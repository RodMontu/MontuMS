# B16 — Capacidad de la planta por jornada (minutos-hombre → toneladas) — SPEC CERRADA

**Fecha:** 2026-09-23 · **Sesión de diseño:** Miaude + Montu (ventana V4, sin código) · **Implementa:** CCa en Ola 2, tras commit de V1 y V2 (ver tablero)
**Estado:** cerrada. CCa no debe preguntar nada; si algo contradice el código real, detenerse y avisar a Montu.
**Verificado contra:** espejo `~/graphify-workspace/optifierro`, HEAD `ff00b595` (sin commits posteriores en TO según CCa-1/CCa-2).

---

## 1. Qué es B16 (y qué NO es)

B16 es un **cálculo interno**, no un número que se muestre en pantalla. Determina la **capacidad de la planta (sucursal) por turno y día**, ligada a los operadores presentes, y es el insumo para saber la **producción máxima en TONELADAS** de esa jornada frente al trabajo asignado (Montu: "buscando el máximo de producción posible en la jornada").

- B16 mide **personas-tiempo**. NO mide throughput de máquina (eso son las hebras, HEBRAS-01 / V1). No mezclar.
- Alimenta a **B43** (adelantar trabajo hasta completar la capacidad de la jornada).
- **No se muestra en el Gantt ni en la Vista Semanal.** Se expone solo como `metadata` del API (para B43, QA y validación de Montu) y en log.

## 2. Definiciones cerradas

| Tema | Decisión (Montu 23-09) |
|---|---|
| Qué se cuenta | **Solo operadores.** Ayudantes NO suman. Ausentes aportan 0. |
| Ventana | **Ventana de planta** (la que ya resuelve el sistema, con +15 min inicio / −15 min fin) para todos. |
| Ausencia parcial | Solo si las marcas reales difieren **≥ 30 min** de la ventana de planta (entrada tarde o salida temprana). Ahí la ventana de esa persona = intersección `ventana_planta ∩ [entrada_real, salida_real]`. Diferencia < 30 min → ventana de planta completa. |
| Colación | 60 min fijos: 13:00–14:00 turno día, 01:00–02:00 turno noche. Se descuenta **solo si cae dentro de la ventana de la persona**. |
| Consumo | **1 operador por tarea durante toda su duración** (`duracion_min`). |
| AR-009 | Un operador que califica para 2+ máquinas cuenta **una sola vez** en la capacidad; sus tareas van en serie, nunca en paralelo. |
| Días futuros | Dotación y horario planificado desde `turnos_programados` (turnos cargados mensual/semanal desde GeoVictoria). Sin marcas reales. |
| Hoy / pasado | Mandan las marcas reales de GeoVictoria (`asistencia_colaboradores`); lo planificado es respaldo. |
| Toneladas | Se cuentan solo **piezas terminadas** (todas las etapas de su ruta completas dentro de la jornada). Pieza a medio camino no suma. |
| Rutas | Jueves: **rutas actuales** (`resolver_ruta`, frecuencia histórica). Optimización de ruta por ton/h queda para después (sección 9). |
| Última tarea | Si no cabe entera en el saldo, **se parte** (avance parcial, continúa al día siguiente). |

## 3. Fórmulas

```
min_utiles(persona) = max(0, dur(ventana_persona) − solape(colacion, ventana_persona))
ventana_persona     = ventana_planta                       si |desvío| < 30 min
                    = ventana_planta ∩ [entrada, salida]   si desvío ≥ 30 min (entrada tarde O salida temprana)
capacidad_mh        = Σ min_utiles(persona)  sobre operadores presentes (cargo = operador)
saldo_mh            = capacidad_mh − Σ duracion_min de las tareas asignadas ese (sucursal, turno, fecha)
toneladas_jornada   = Σ kgs de piezas terminadas en la jornada / 1000
```

- `saldo_mh` puede ser **negativo** (sobreasignación): se informa tal cual, sin recortar a 0.
- Turno noche: ventana anclada al **día de inicio**, cruza medianoche (ya lo hace `_ventana_turno`); las toneladas se imputan al día de inicio.
- Ruta de varias etapas ("Corte → Dobladora"): la pieza consume minutos-hombre en **cada etapa**. Tareas con `reparto[]` en paralelo: cada segmento consume su propia `duracion_min` (usar `reparto[]`, ver FP-012).
- Restricción adicional que NO reemplaza B16: una máquina no puede tener 2 operadores a la vez; el tiempo-máquina (ventana − colación por máquina disponible, excluyendo detenidas/no liberadas) sigue siendo cota real cuando hay más operadores que máquinas útiles. El cursor de asignación (`_saltar_break`) ya lo respeta; B16 no lo toca.

## 4. Fuentes de datos

| Dato | Fuente | Nota |
|---|---|---|
| Ventana de planta | `_get_config_turno` (`motor_v2.py:63-126`) vía `inicio_override/fin_override` (`programacion.py:1000`) | B16 consume lo que devuelva; NO unificar aquí (ver riesgo R1). |
| Operadores presentes hoy/pasado | `asistencia_colaboradores` (GeoVictoria) + `operadores_matriz` | `programar_turno` ya recibe `operadores_disponibles: list[str]`. |
| Dotación día futuro | `turnos_programados` (`init_db.py:48`): `sucursal_id, fecha, rut, nombre, turno, hora_inicio_turno, hora_fin_turno, estado, permiso`; UNIQUE(sucursal_id, fecha, rut) | Carga: `routers/admin.py:77`. **No trae `cargo`**: cruzar con `operadores_matriz`. |
| Duración de tarea | `estimar_duracion_min` (`motor_v2.py:585-649`), ya incluye hebras | No modificar. |

## 5. Contrato de salida (interno)

Agregar a `metadata` de la respuesta (POST `/generar` y GET `obtener_programacion`, mismo portador que B35):

```json
"capacidad": {
  "capacidad_mh": 4080,
  "operadores_contados": 8,
  "min_utiles_planta": 510,
  "operadores_parciales": [{"username": "...", "min_utiles": 375}],
  "saldo_mh": 930,
  "toneladas_asignadas": 41.7,
  "fuente_presencia": "geovictoria|turnos_programados"
}
```

Sin cambios de UI. Se registra además una línea de log por generación.

## 6. Cómo lo consume B43 (fuera del mínimo del jueves)

Adelantar tareas mientras `saldo_mh > 0`; solo lo que ya está en el Cuadro de Programación (nunca crudo de Cubigest); aplica a las 3 plantas; puede cruzar a la semana siguiente; la última tarea se parte con avance parcial.

## 7. Casos borde

| Caso | Regla |
|---|---|
| Turno noche | Ancla al día de inicio; colación 01–02 dentro de ventana. |
| Sábado/domingo/feriado | Sin calendario de feriados propio. Sin turno programado ni marcas → capacidad 0, sin error. |
| Ausente | 0. Presente con cargo ≠ operador: no entra. |
| Ausencia parcial | Umbral 30 min (≥ 30 = parcial). Colación se descuenta solo si intersecta. |
| Operador en 2+ máquinas | Cuenta 1 vez; tareas en serie. |
| Viernes corto | Lo que devuelva `_get_config_turno` (día 16:45, noche 04:45 en fallback). |
| Día futuro | `turnos_programados`; el mismo umbral de 30 min compara horario planificado individual vs ventana de planta. |

## 8. Criterios de aceptación (medibles)

- **AC1 (propiedad, criterio de Montu):** misma sucursal y turno, misma duración de ventana y mismo número de operadores contados → `capacidad_mh` idéntica entre días distintos.
- **AC2:** Cerrillos, turno día, ventana 08:15–17:45 (no viernes), 8 operadores completos → 8 × 510 = **4.080**. (Ilustrativo; Montu valida contra su cálculo manual con un día real que cumpla AC1.)
- **AC3 parcial:** entrada 10:30 → ventana 10:30–17:45 = 435 − 60 = **375**. Entrada 08:40 (25 min) → **510**. Entrada 08:45 (30 min) → **480**.
- **AC4 colación:** salida 12:30 en turno día → 255 min, **sin** descontar colación.
- **AC5 noche:** 20:15–05:45 = 570 − 60 = **510** por operador.
- **AC6 AR-009:** operador con 3 máquinas cuenta **1**.
- **AC7 día sin turno ni marcas:** capacidad **0**, sin excepción.
- **AC8 no invasivo:** el jueves B16 NO cambia la asignación. Diff de `eventos` de `/generar` antes vs después de B16 = **idéntico** (solo se agrega `metadata.capacidad`).
- **AC9 saldo:** `saldo_mh = capacidad_mh − Σ duracion_min`; admite negativo.

## 9. Mínimo viable jueves vs después

**Entra el jueves (Ola 2):** cálculo de `capacidad_mh` (con ausencia parcial y colación), `saldo_mh`, `toneladas_asignadas` con las rutas actuales, `metadata.capacidad`, pruebas AC1–AC9.

**Queda para después:**
1. Optimización de ruta por ton/h (id_forma × diámetro × largo × máquina): hoy `resolver_ruta` (`motor_v2.py:405-470`) elige por **frecuencia histórica**, no por productividad. Requiere criterio nuevo, ton/h confiable de B26 (bugs "fuera de rango" y mezcla método validado/deltas crudos pendientes) y decidir el manejo de rutas multi-etapa.
2. Techo estimado en toneladas antes de asignar.
3. B43 (adelanto de trabajo y su indicador visual).
4. B44 y cualquier UI de capacidad.

## 10. Archivos a tocar en Ola 2

| Archivo | Cambio |
|---|---|
| `backend/motor_v2.py` | `programar_turno` (~l.772): reemplazar `minutos_turno` muerto por llamada a nuevo helper `_calcular_capacidad_mh(...)` (junto a `_ventana_turno`, ~l.1612); calcular `saldo_mh` y toneladas de piezas terminadas; devolver `capacidad` en el dict de salida. **No tocar `estimar_duracion_min` ni el cursor.** |
| `backend/routers/programacion.py` | `generar_programacion` (~l.944-1002): armar presencia (marcas GV o `turnos_programados`) y ventanas parciales y pasarlas al motor; `obtener_programacion` (~l.365-369): devolver `metadata.capacidad` (mismo portador que B35). |
| `frontend/.../GestorProgramacion.tsx` | **Ninguno el jueves** (no se muestra). |
| Prueba nueva | Casos AC1–AC9 (ruta según convención del repo). |

**Serialización:** B16 después de V1 (HEBRAS-01, `motor_v2.py`) y V2; B35 expone el turno resuelto después de B16 (mismo `metadata`); B44 después de B16. Graphify: consultar antes, regenerar tras commit.

## 11. Riesgos y verificaciones pendientes para CCa

- **R1:** la ventana tiene 3 fuentes inconsistentes: la rama SQLite usa default `fin=16:45` (`motor_v2.py:~96-99`) y el fallback hardcodeado `17:45` (no viernes). B16 usa lo que devuelva `_get_config_turno`; unificar es territorio B35.
- **R2:** inspeccionar valores reales de `estado` y `permiso` en `turnos_programados` para definir qué excluye a una persona (licencia, vacaciones).
- **R3:** confirmar que `operadores_disponibles` ya excluye ayudantes; si no, filtrar por cargo antes de contar.
- **R4:** confirmar en producción que el umbral de 30 min funciona con marcas GV reales (formato de hora).
