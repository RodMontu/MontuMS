# CCa-2 — Blast radius Graphify + estado real B16 / B26 / B44

**Fecha:** 2026-09-23 · **Agente:** CCa-2 (solo lectura) · **Entrega objetivo:** jueves 2026-09-24
**Fuente:** espejo local `~/graphify-workspace/optifierro`, HEAD `ff00b595` (= graph.json / GRAPH_REPORT.md, `Built from commit: ff00b595`, sin cambios de código desde entonces → grafo vigente, no se regeneró).
**Modo:** SOLO LECTURA. No se editó código, no se corrió `Generar Programación`, no se tocó DB.

---

## 1. B26 — "Producción por Máquina" — spec vs implementado

Endpoint: `GET /api/tiempos-maquina` en `backend/routers/tiempos_maquina.py` (306 líneas).
Frontend: `frontend/src/components/domain/TiemposPorMaquina.tsx`, montado en `App.tsx:150` (`case 'tiempos_maquina'`).

| Ítem del spec | Estado | Evidencia |
|---|---|---|
| Rename en menú lateral a "Producción por Máquina" | **HECHO** | `frontend/src/App.tsx:332` — `<NavItem id="tiempos_maquina" ... label="Producción por Máquina" />` |
| Título interno "Tiempos por Máquina (estimado)" | **HECHO, pero inconsistente con el rename** | `TiemposPorMaquina.tsx:102` — el `<h2>` interno del componente NO se renombró; el menú dice "Producción" y el header del panel dice "Tiempos". Confirmado por `git show --stat 77bc809`: solo tocó `App.tsx` (label), `tiempos_maquina.py`, `TiemposPorMaquina.tsx` (lógica), no el `<h2>`. |
| Frase "estimaciones ... con intervalo de confianza del XX%" | **FALTA — contradice lo implementado** | `tiempos_maquina.py:37-43` (`NOTA_METODOLOGICA`) dice literalmente "sin intervalo estadistico riguroso (limitacion de origen de datos)". El código evita a propósito reclamar un intervalo de confianza numérico; no hay ningún `%` calculado. Si Montu quiere la frase con XX%, hay que decidir si se inventa un número (riesgoso) o se cambia el copy pedido. |
| Rutas de máquina posibles (Fase 1 del motor) | **FALTA / PARCIAL implícito** | El endpoint no llama a `resolver_ruta()` (`backend/motor_v2.py:405`, la función real de resolución de ruta Fase 1). En vez de eso, agrupa por `(MaquinaId, IdSucursal)` las máquinas que **históricamente** procesaron ese `(IdForma, diametro)` en Cubigest (`tiempos_maquina.py:158-181, 218-229`). Es una aproximación por antecedentes, no una consulta a la lógica de ruteo del motor — puede diverger si `motor_v2.py` tiene reglas de ruta que el histórico no refleja. |
| Ton/hora por máquina | **HECHO** | `_estimar_ton_hora()` (`tiempos_maquina.py:52-113`) + campo `ton_hora_estimado` expuesto (línea 292) y renderizado (`TiemposPorMaquina.tsx:306-312`). |
| Filtros: ID Forma, diámetro, sucursal, período | **HECHO** | Query params `id_forma`, `diametro`, `sucursal_id`, `meses` (`tiempos_maquina.py:127-139`); inputs correspondientes en `TiemposPorMaquina.tsx:113-173`. |
| Filtro peso/largo por pieza | **HECHO** (cambiado de peso a largo, commit `818bc18`) | Input "Largo aprox. pieza (mm)" (`TiemposPorMaquina.tsx:175-189`) → `_peso_estimado_kg()` (`tiempos_maquina.py:46-49`, fórmula barra corrugada d²/162) → usado por `_estimar_ton_hora`. |
| Bug 1 — falta indicador "fuera de rango" cuando el bin más cercano está lejos del peso pedido | **FALTA, no arreglado** | `_estimar_ton_hora()` (`tiempos_maquina.py:96-105`): cuando `peso_input` no cae dentro de ningún bin, elige el bin de mediana más cercana (`mejor_dist`) y lo retorna igual, sin exponer `mejor_dist` ni ningún flag. La respuesta (`por_maquina[].ton_hora_estimado`) no tiene campo de "distancia" ni "fuera_de_rango". Frontend tampoco lo muestra (no hay ningún condicional de advertencia en `TiemposPorMaquina.tsx`). |
| Bug 2 — tabla mezcla método validado (ton/hora por pedido+operario+máquina) con deltas crudos sin validar (filtro laxo 2-480min) para min/mediana/max | **FALTA, no arreglado** | Las columnas "Mín/Mediana/Máx (min)" (`TiemposPorMaquina.tsx:268-270`, datos de `tiempo_min/tiempo_mediana/tiempo_max`) vienen de `deltas_validos`, que solo descarta `< 2min` o `> 480min` (`_DELTA_MIN_MIN`/`_DELTA_MAX_MIN`, `tiempos_maquina.py:32-33`, aplicado en línea 248) — es el delta crudo entre registros consecutivos de Cubigest por máquina, **sin** el método validado de Fase 3 (operario+máquina+pedido, con censura de jornada, tests de bondad de ajuste, etc. — ver `fase3_operario_maquina.py`, `fase3_operario_pedido.py`). Se muestran en la misma fila que `ton_hora_estimado`, que sí usa el método de bins validado en `FASE3_PESO_POR_PIEZA_20260921.md`. Mezcla confirmada, sin fix aplicado. |

**Conclusión B26:** el rename de menú, los filtros, el ton/hora por quintil y el cambio peso→largo están HECHOS. La frase de intervalo de confianza está FALTA y en tensión directa con el copy actual (que dice lo contrario). "Rutas posibles" es una aproximación histórica, no ruteo real. Los dos bugs diagnosticados siguen sin arreglo.

---

## 2. B16 — minutos-hombre reales por jornada — qué existe hoy

**No existe cálculo de minutos-hombre disponibles.** Lo que existe es resolución de la **ventana horaria** del turno, en tres niveles de prioridad, y un salto de colación en el *cursor* de asignación — pero nunca se agrega a un total de minutos-hombre de capacidad.

- `_get_config_turno()` — `backend/motor_v2.py:63-126`. Prioridad 1: `inicio_override/fin_override` (ya con ±15min aplicado, ver abajo). Prioridad 2: `jornada_json` en SQLite vía `routers.sucursales.get_jornada()`. Prioridad 3: fallback hardcodeado (`08:15-17:45` día, `20:15-05:45` noche, viernes corto). Colación fija hardcodeada en el fallback: `13:00-14:00` día, `01:00-02:00` noche (líneas 84-85, 106-107, 117-118, 124-125) — coincide con el spec.
- `_ventana_desde_geovictoria()` — `backend/routers/programacion.py:866-897`. Consulta GV, aplica **+15min inicio / −15min fin** (líneas 889-890) — el ajuste que pide el spec ya existe, pero solo en esta función de fallback.
- `_ventana_desde_turnos_programados()` — `backend/routers/programacion.py:900-930`. Mismo ±15min (líneas 924-925), usando la moda de horarios de `turnos_programados` en SQLite. Es la prioridad 1 real en `generar_programacion()` (línea 1000), con GV como fallback (línea 1002).
- `_ventana_turno()` — `backend/motor_v2.py:1612-1636`. Ancla horas a la fecha, maneja cruce de medianoche (turno noche) y calcula `brk_ini`/`brk_fin`. **Aquí se calcula `minutos_turno = int((hora_fin - hora_inicio).total_seconds() / 60)` (línea 772 de `motor_v2.py`) — pero es una variable muerta: no se descuenta la colación (`brk_fin - brk_ini`) y no se usa en ningún otro punto del archivo** (verificado: única ocurrencia de `minutos_turno` en todo `motor_v2.py`).
- `_saltar_break()` — `backend/motor_v2.py:1639-1643`. Esto sí se usa (líneas 1118, 1170): si el cursor de asignación secuencial cae dentro del break, lo salta al fin del break. Es un mecanismo de **secuenciación**, no de **capacidad agregada** — no hay ningún lugar donde el motor sepa "hoy la jornada tiene X minutos-hombre disponibles" para decidir cuánto trabajo adelantar (B43).

**Puntos de integración probables para B16/B43:**
1. `motor_v2.py:772` — reemplazar el cálculo muerto de `minutos_turno` por uno real: `(hora_fin - hora_inicio) - (brk_fin - brk_ini)`, multiplicado por operadores disponibles si se quiere el total "minutos-hombre" (no solo minutos de ventana).
2. La lógica de B43 (adelantar trabajo hasta completar la capacidad) tendría que vivir cerca de `programar_turno()` (`motor_v2.py:743` en adelante), después de que se conoce `operadores_disponibles` (pasado como parámetro) y antes/durante el loop de asignación que usa `_saltar_break`.
3. `routers/programacion.py:944` (`generar_programacion`) es donde hoy se decide la ventana horaria antes de invocar `programar_turno` — cualquier "minutos-hombre reales" que dependa de asistencia real de GV se resolvería aquí, no en el motor.

---

## 3. B44 — ajuste manual de duración

### (a) Modal de detalle de la cajita
Vive en `frontend/src/components/domain/GestorProgramacion.tsx`, bloque `{selectedTarea && (...)}` líneas **1705-1851** (no es un `<Modal>` componentizado, es un panel condicional sobre `selectedTarea`, estado en línea 875).

- La duración por tarea (`duracion_min`, tipo declarado en línea 22) llega desde el backend ya calculada — no se muestra ni edita en este panel hoy (no hay ningún `duracion_min` renderizado dentro del bloque 1705-1851; solo aparece en el tipo `Tarea` (línea 22), en el tipo de `reparto[]` (línea 51) y al mapear datos de máquina (línea 163)).
- Origen del cálculo: `estimar_duracion_min()` — `backend/motor_v2.py:585-649`. Fórmula: `DeltaT_Mediana × (kilos_grupo / KgsPromedio_historico) / hebras`, con caps 5-480 min. Se invoca en el loop principal de asignación (`motor_v2.py:1121`) y en el camino de reparto en paralelo (`motor_v2.py:1172`).
- **No existe hoy ningún campo "Ajustar duración del trabajo (minutos)"** en el frontend, ni endpoint backend para setearlo (`grep` de `ajustar_duracion|duracion_manual|duracion_ajustada` en todo el repo: 0 resultados). B44(a) es FALTA completa.

### (b) Campo de capacidad real al final de "Producción por Máquina"
`grep` de `capacidad_real|capacidad_manual|CapacidadInput` en todo el repo: 0 resultados. FALTA completa — ni el componente `TiemposPorMaquina.tsx` ni el router `tiempos_maquina.py` tienen ningún campo de captura ni persistencia para que el jefe de planta ingrese capacidad.

### Persistencia que habría que agregar (solo descripción, sin diseñar)
- Tabla nueva en SQLite (patrón ya usado por `jornada_asignacion_manual`, ver `backend/routers/jornada.py:62-78`, que hace `CREATE TABLE IF NOT EXISTS ... UNIQUE(...)` con upsert vía `ON CONFLICT ... DO UPDATE`). Un ajuste de duración por tarea necesitaría una clave estable (¿`etiqueta_id` + fecha + turno? ¿`codigo_viaje` + `nombre_maquina`?) — la `Tarea` del frontend no tiene un ID único obvio más allá de `etiqueta_id`/`codigo_viaje` (revisar tipos en `GestorProgramacion.tsx:1-60` antes de decidir).
- Endpoint nuevo estilo `POST /api/jornada-asignacion` (`jornada.py:174-205`) pero para duración: recibiría la tarea + minutos ajustados, upsert.
- Para B44(b): columna o tabla de "capacidad declarada" por (máquina, sucursal, fecha o vigencia), separada de la tabla `hebras` (SQLite, consumida por `routers/maquinas.py:180-192`) — no reusar `hebras` porque es multiplicidad por diámetro, no capacidad de jornada.
- Auto-aprendizaje / retroalimentación al motor: explícitamente fuera de alcance (no se investigó ni se diseñó).

---

## 4. Blast radius (Graphify) — matriz de archivos tocados

Basado en `graphify-out/graph.json` (comunidades 4 `motor_v2.py`, 13 `programacion.py`, hub `ConocimientoMotor` con 27 edges) + lectura directa de código.

| Punto | `motor_v2.py` | `routers/programacion.py` | `GestorProgramacion.tsx` | Otros archivos |
|---|---|---|---|---|
| **B16** | X — `_get_config_turno`, `_ventana_turno`, `minutos_turno`, `programar_turno` | X — `_ventana_desde_geovictoria`, `_ventana_desde_turnos_programados`, `generar_programacion` | — (no consume ventana/minutos directamente) | `routers/sucursales.py` (`get_jornada`, llamada desde `_get_config_turno`) |
| **B26** | — (no lo toca; usa datos propios de Cubigest, no `ConocimientoMotor`) | — | — | `routers/tiempos_maquina.py`, `components/domain/TiemposPorMaquina.tsx` |
| **B44** | X — `estimar_duracion_min` (origen del número a ajustar) | Posible — si el ajuste se persiste vía un router, candidato natural es `programacion.py` (ya maneja `reparto`, `avance parcial`) o un router nuevo tipo `jornada.py` | X — panel `selectedTarea` (líneas 1705-1851), tipo `Tarea.duracion_min` | Tabla SQLite nueva; `routers/tiempos_maquina.py` + `TiemposPorMaquina.tsx` para B44(b) |
| **HEBRAS-01** (asumido) | X — `hebras_x_maquina` (dict cargado desde Excel, `motor_v2.py:208,278-290`), usado en `estimar_duracion_min` (línea 645) | — (no referencia `hebras` en ningún punto — confirmado por grep) | — (no la toca directamente; la UI de hebras vive en `GestorMaquinas.tsx`, fuera de esta matriz) | `routers/maquinas.py` (`GET/PUT /api/hebras`, líneas 180-297) — **fuente SQLite independiente del dict de `motor_v2.py`**, son dos storages distintos hoy |
| **B35** (turno resuelto expuesto) | — | X — sería donde se agregaría el campo (`turno_norm` ya se calcula 4 veces: líneas 449, 752, 958, 1642, pero no se retorna en ninguna respuesta) | X — consumiría el nuevo campo | Ninguno hoy: `grep` de `turno_resuelto` en todo el repo (backend + frontend) = 0 resultados. **FALTA completa**, no solo el consumo. |

### Paralelismo derivado

- **EN PARALELO (no comparten archivo):**
  - B26 (solo `tiempos_maquina.py` + `TiemposPorMaquina.tsx`) puede avanzar en paralelo con cualquier otro punto — no toca `motor_v2.py` ni `programacion.py` ni `GestorProgramacion.tsx`.
  - HEBRAS-01 puede avanzar en paralelo con B16 **si** se limita a `motor_v2.py` (no toca `programacion.py` ni `GestorProgramacion.tsx` hoy) — riesgo bajo de choque, pero ambos escriben en `motor_v2.py`, revisar por-función, no por-archivo.

- **DEBEN SERIALIZARSE (mismo archivo, alto riesgo de choque):**
  - B16 y B44 — ambos tocan `motor_v2.py` (B16 en `_get_config_turno`/`_ventana_turno`/`programar_turno`; B44 en `estimar_duracion_min`) y B44 además depende de que `programar_turno` ya haya corrido para tener un `duracion_min` que ajustar. Serializar: **B16 primero** (cambia el loop de `programar_turno`), B44 después.
  - B16 y B35 — ambos tocan `routers/programacion.py` (`generar_programacion` y las funciones de ventana), y B35 necesita saber qué turno quedó resuelto, que es justo lo que B16 recalcula. Serializar: **B16 primero**, B35 expone el resultado.
  - B44(a) y cualquier cambio de estructura de `Tarea` en `GestorProgramacion.tsx` — si dos agentes tocan el mismo bloque 1705-1851 a la vez, choque directo de diff.

---

## 5. Riesgos para el jueves (máx. 3 líneas c/u)

- **B16:** mínimo entregable = corregir `minutos_turno` (ya existe la variable, solo está mal calculada y sin usar) para que descuente colación; la lógica de "adelantar hasta completar capacidad" (B43) es más grande y se puede diferir sin bloquear B16 aislado.
- **B26:** mínimo entregable = separar visualmente en la tabla las columnas validadas (ton/hora) de las crudas (min/mediana/max), y decidir con Montu si la frase "XX% confianza" se difiere (contradice el copy actual, que es honesto a propósito).
- **B44:** mínimo entregable = el campo (a) en el modal, porque es local y no requiere tocar el motor; el campo (b) y cualquier persistencia real (tabla nueva, endpoint) se puede diferir — hoy no existe nada de ninguno de los dos.

---

**Informe generado en modo solo lectura. No se ejecutó ningún cambio de código, commit, ni operación en Docker/DB.**
