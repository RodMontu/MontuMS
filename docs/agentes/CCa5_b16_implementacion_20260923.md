# CCa-5 — B16 "Capacidad de la planta por jornada (minutos-hombre)" — Implementación Ola 2

**Fecha:** 2026-09-23 · **Agente:** CCa-5 · **Checkout editado:** TO por SSH (`/c/Users/OptiFierro/Desktop/optifierro`), HEAD `8604d50`.
**Diff:** `docs/agentes/diffs/B16_diff_20260923.patch`

## 1. Resumen de cambios

| Archivo | Cambio | Líneas (aprox., TO) |
|---|---|---|
| `backend/motor_v2.py` | `programar_turno`: nuevo parámetro `presencia_capacidad=None`; se elimina el uso muerto de `minutos_turno` y se calcula `capacidad_b16` (try/except, AC8); tras construir `tareas`/`bolsa_sin_asignar` se calcula `saldo_mh` y `toneladas_asignadas` (try/except separado); se agrega `metadata.capacidad`. Helper nuevo `_calcular_capacidad_mh` + `_solape_minutos` junto a `_ventana_turno` (motor_v2.py:1687 en adelante). | ~813, ~1630-1650, ~1712-1795 |
| `backend/routers/programacion.py` | Import `date` agregado (`datetime, timedelta, date`). Helper nuevo **compartido** `_obtener_presencia_capacidad(sucursal_id, fecha, turno_norm, conocimiento)` (después de `_obtener_operadores_disponibles`): hoy/pasado → Geovictoria (mismo endpoint que ya usa `_obtener_operadores_disponibles`); día futuro → `turnos_programados` filtrando `estado='PRESENTE'` y cruzando con `operadores_matriz`. `generar_programacion`: llama al helper y pasa `presencia_capacidad` a `programar_turno`. `obtener_programacion` (GET): lee `metadata.capacidad` ya persistido en `programacion_guardada.metadata_json` de la última generación y lo mezcla en `metadata_turno` (mismo portador que B35), sin recalcular. | helper ~1774-1878, `/generar` ~1047-1061, GET ~365-383 |
| `backend/main.py` | Importa y usa el mismo `_obtener_presencia_capacidad` en `_ejecutar_generacion` (scheduler 08:10/20:10), mismos argumentos que `/generar`. | ~126-133, ~157-165 |
| `backend/test_b16_capacidad.py` | Nuevo. 9 pruebas `unittest` sobre `_calcular_capacidad_mh` (AC1-AC7, AC9). AC8 se verifica en el arnes (sección 3), no acá. | nuevo |

Nada tocado en `estimar_duracion_min`, el cursor de asignación, ni frontend.

## 2. Diseño de `_calcular_capacidad_mh`

Recibe `presencia_capacidad = {"fuente": ..., "operadores": [{"username","entrada","salida"}]}`.
- `presencia_capacidad is None` → devuelve `None` (capacidad ausente en metadata; nunca rompe).
- `operadores == []` → `capacidad_mh = 0` (AC7).
- Por persona: si hay `entrada`/`salida` reales y el desvío (llegada tarde o salida temprana) es `>= 30 min`, ventana_persona = intersección con la ventana de planta; si no, ventana completa. Colación se descuenta solo si intersecta la ventana efectiva de esa persona.
- Dedupe por `username` (AR-009): un operador que aparece 2+ veces en la lista de presencia (ej. califica para varias máquinas) cuenta una sola vez.
- `saldo_mh` y `toneladas_asignadas` se calculan en `programar_turno` después de tener `tareas`: `Σ duracion_min` suma cada segmento de `reparto[]` por separado cuando existe (spec sección 3); toneladas = `Σ kilos` de tareas donde `paso_secuencia == total_pasos` (pieza terminada), / 1000.

## 3. Verificación

### 3.1 py_compile (TO)
`python -m py_compile motor_v2.py routers/programacion.py main.py` → **OK**, sin warnings.

### 3.2 Pruebas AC1-AC9 (arnes en contenedor)
Corridas con `python -m unittest test_b16_capacidad -v` directo en el checkout de TO (mismo Python 3.11 que usa el contenedor) — **9/9 OK**:

```
test_ac1_propiedad_misma_ventana_mismos_operadores ... ok
test_ac2_cerrillos_dia_8_operadores_completos ... ok
test_ac3_ausencia_parcial_umbral_30min ... ok
test_ac4_colacion_no_se_descuenta_si_no_intersecta ... ok
test_ac5_turno_noche_cruza_medianoche ... ok
test_ac6_ar009_operador_en_2_o_mas_maquinas_cuenta_una_vez ... ok
test_ac7_dia_sin_turno_ni_marcas ... ok
test_ac7b_presencia_none_no_hay_excepcion ... ok
test_ac9_saldo_admite_negativo ... ok
```

### 3.3 Caso real por sucursal (Cerrillos, Calama, Coronel — turno día, 2026-09-23)
Arnes corrido con `docker cp` a `/tmp/b16_before` y `/tmp/b16_after` dentro de `optifierro-backend` (no se tocó `/app` ni el servicio), cada árbol con su **propia copia** de `optifierro_v2.db` (nunca se escribió en la DB montada). Presencia real de Geovictoria (llamada en vivo, `GEOVICTORIA_URL=192.168.1.111:8002`, funcionando):

| Sucursal | Ventana (día, hoy) | Operadores contados | `min_utiles_planta` | `capacidad_mh` |
|---|---|---|---|---|
| Cerrillos (10) | 08:15–16:45 | 8 | 450 | 4.080 → **espera** AC2 (510×8=4080), pero la jornada real hoy resolvió fin=16:45 (no 17:45) vía `jornada_json` de SQLite (prioridad 2), no el fallback. `capacidad_mh` real = 8×450 = **3.600**, correcto para esa ventana. |
| Calama (1) | 08:15–16:45 | 6 | 450 | 2.700 |
| Coronel (14) | 08:15–16:45 | 6 | 450 | 2.700 |

Sin operadores parciales hoy (0 desvíos ≥ 30 min en las 3 sucursales) → `operadores_parciales: []` en las 3.

**⚠️ Cubigest no disponible durante el arnes**: `_obtener_pids_pendientes` devolvió `[]` en las 3 sucursales por
`SSL Provider: [error:0A000102:SSL routines::unsupported protocol]` al conectar a `192.168.1.195` desde un proceso `docker exec` en el contenedor `optifierro-backend` (mismo contenedor, mismo `openssl_legacy.cnf`, mismo `.env`). Por lo tanto `tareas=[]`, `bolsa_sin_asignar=[]`, `saldo_mh == capacidad_mh` y `toneladas_asignadas=0` en los 3 casos — **no se pudo validar `saldo_mh`/`toneladas_asignadas` contra un turno con trabajo real**. No se investigó más a fondo (fuera de alcance: Cubigest es de terceros, solo lectura, y el error es de conectividad/TLS, no de B16). Recomiendo a Montu/Miaude confirmar si el servicio en vivo (proceso principal, no `docker exec`) está actualmente logrando conectar a Cubigest — si el error es el mismo ahí, es una falla de infraestructura activa, independiente de B16.

Prueba complementaria con una etiqueta sintética (bypass de Cubigest, sin tocar datos reales): la etiqueta cayó a `bolsa_sin_asignar` (ruta no resuelta para la combinación forma/diámetro fabricada) — confirma que con 0 tareas asignadas `saldo_mh == capacidad_mh` y `toneladas_asignadas == 0`, consistente con la fórmula. No se logró un caso con tarea efectivamente asignada dentro del tiempo disponible; las fórmulas de `saldo_mh`/`toneladas_asignadas` quedan validadas al nivel de aritmética por los AC1-AC9 (unitarios), no con un turno real de punta a punta.

### 3.4 AC8 — no invasividad (diff de `eventos`/`tareas` antes vs después)
Mismo arnes (`/tmp/b16_before` = HEAD `8604d50` sin B16, `/tmp/b16_after` = working tree con B16), mismos insumos reales (Geovictoria, ventana, Cubigest — este último vacío por el error de 3.3, pero **idéntico en ambos árboles**):

```
10_dia  metadata(sin 'capacidad')== True   tareas== True   bolsa== True
1_dia   metadata(sin 'capacidad')== True   tareas== True   bolsa== True
14_dia  metadata(sin 'capacidad')== True   tareas== True   bolsa== True
```

**AC8 cumple**: la única diferencia entre árboles es la presencia de la clave `metadata.capacidad` en "after" (`capacidad_presente: True` vs `False` en "before"); `tareas`, `bolsa_sin_asignar` y el resto de `metadata` son **idénticos byte a byte**.

### 3.5 Graphify
Grafo espejo (`~/graphify-workspace/optifierro/graphify-out/2026-09-23`, `built_at_commit ff00b595` — desactualizado respecto a `8604d50`, no regenerado por mí, ver regla). Dependientes de `programar_turno`: solo `backend/routers/programacion.py::generar_programacion` (llamada directa) y `backend/main.py` (import). No hay otros llamadores en el grafo ni por grep en el código actual. Consistente con los 2 puntos que edité.

## 4. Riesgos R1-R4 — hallazgos

- **R1 (ventana con 3 fuentes):** confirmado en código real. B16 no unifica nada: usa el mismo `hora_inicio`/`hora_fin`/`brk_ini`/`brk_fin` que ya resuelve `_ventana_turno(fecha, _get_config_turno(...))`, exactamente como lo consume el resto de `programar_turno`. Sin cambios aquí (territorio B35).
- **R2 (`estado`/`permiso` en `turnos_programados`):** inspeccionado en la DB real de TO (2.432 filas). Valores de `estado`: `PRESENTE`, `FALTA`, `VACACIONES`, `LICENCIA`. Implementado: solo `estado == 'PRESENTE'` cuenta; los otros 3 aportan 0 (se excluyen de la lista de presencia, equivalente a 0 min_utiles). `permiso` es informativo (texto libre, ej. "Vacaciones", "Licencia Médica Estándar", "Compensación") y no se usa para la regla — el filtro ya lo cubre `estado`.
- **R3 (¿`operadores_disponibles` excluye ayudantes?):** confirmado que sí, y no por un campo `cargo` (no existe tal columna en `operadores_matriz` — se verificó el esquema real con `PRAGMA table_info`). Los ayudantes viven en columnas separadas (`maquinas_info.ayudante1_nombre`/`ayudante2_nombre`), nunca como fila en `operadores_matriz` ni en `conocimiento.operadores_x_maquina`. Por construcción, cualquier persona en ese universo ya es "operador" en el sentido de B16. El propio comentario del código en `_obtener_operadores_disponibles` indica además que el endpoint de Geovictoria ya filtra server-side por "cargo Operador". `_obtener_presencia_capacidad` cruza igual contra ese mismo universo (`todos`) como defensa adicional.
- **R4 (formato de hora GV en producción):** **NO VERIFICADO en vivo** — el endpoint `http://192.168.1.111:8002/asistencia/operadores_presentes/{id}` no respondió (timeout) desde TO al iniciar esta sesión (posible VPN/servicio caído en ese momento), pero **sí respondió correctamente más tarde durante el arnes** (sección 3.3): devolvió `hora_inicio_turno`/`hora_fin_turno` como strings `"HH:MM"`, parseables con el mismo `strptime(..., "%H:%M")` que ya usa `_ventana_desde_geovictoria` en producción. `_obtener_presencia_capacidad` reutiliza ese mismo contrato de campos sin inventar uno nuevo. Formato confirmado en la práctica durante 3.3.

## 5. Limitaciones conocidas / seguir mirando

1. No se logró validar `saldo_mh`/`toneladas_asignadas` con un turno real con tareas asignadas (Cubigest no disponible en el momento del arnes — ver 3.3). Las fórmulas están cubiertas por los 9 tests unitarios pero no de punta a punta.
2. Si un operador tiene `entrada` pero no `salida` (o viceversa) en la fuente de presencia, `_calcular_capacidad_mh` no puede evaluar el desvío y usa la ventana de planta completa (no está en la spec explícitamente; es el fallback más conservador y consistente con "sin marca → no se sabe, no se penaliza"). En la práctica Geovictoria y `turnos_programados` siempre entregan el par completo, así que no debería activarse en el uso normal.
