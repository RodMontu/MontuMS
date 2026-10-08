# B45 — Implementación FP-LC fuera del SPP (WORKTREE, sin tocar B16)

**Agente:** CCa-7 · **Repo:** OptiFierro-V2 · **Base:** commit `8604d50` (worktree `optifierro_b45`, TO)
**Fecha:** 2026-09-23 · **Entrega:** jueves 24-09

## Aislamiento (verificado)
- Worktree creado: `git -C .../optifierro_b45 worktree add ../optifierro_b45 8604d50` (no existía).
- `git -C optifierro_b45 diff --stat 8604d50` → 4 archivos, 64 líneas (+53/-11).
- `git -C optifierro (checkout principal) diff --stat` → **idéntico** antes y después de mi trabajo (5 archivos, 309 líneas, working tree de B16 sin tocar).

## Diseño implementado
1. **`motor_v2.py`**: constante `MAQUINAS_FICTICIAS = {"FP-LC"}` + helper `es_despacho_directo(id_forma, largo_mm, diametro)` (misma condición exacta que tenía el caso especial de `resolver_ruta:458-468`, sin cambiar valores). `resolver_ruta` ahora llama al helper — mismo resultado, una sola definición. Se quitó `"FP-LC"` de `MAQUINAS_ACTIVAS["Cerrillos"]` (queda con las 10 máquinas reales).
2. **Exclusión en la entrada** (`programacion.py`): `_obtener_pids_pendientes` y `_piezas_optisteel_por_viajes` (compartida por `_obtener_pids_pendientes_optisteel` y `_obtener_pendientes_bolsa_optisteel`) filtran las filas de Cubigest con `es_despacho_directo(...)` antes de devolverlas, y loguean INFO con conteo y kg excluidos. Un solo punto de filtrado por query, cubre además otros consumidores no listados en el mandato (confirmado con Graphify): `compromisos_semanales.get_compromisos_semanales`, `programacion.obtener_proyeccion_semanal`, job programado en `main.py` — todos llaman a `_obtener_pids_pendientes` y heredan el filtro gratis.
3. **Máquina fuera de todo**: al quitar `"FP-LC"` de `MAQUINAS_ACTIVAS`, `programacion.py:794-806` (reasignación manual) la rechaza por "máquina no activa" sin tocar esas líneas.
4. **Presentación**: `main.py` (lifespan) ya no agrega la fila `maquina_id=17` a `global_recursos` → desaparece de `/api/maquinas` (pestaña maestro) y de `recursos` en `/api/programacion` (columnas del Gantt). `routers/maquinas.py` filtra FP-LC en `/diametros` y `/hebras` (las 2 pestañas que leen SQLite directo, no `global_recursos`); `/restricciones` no tiene filas FP-LC (0 en SQLite, confirmado). `obtener_programacion` filtra `eventos` por `recurso_id` antes del `return`, así los planes ya guardados con tareas FP-LC no las muestran.
5. No se tocó `estimar_duracion_min`, cursor/asignación, `tiempos_maquina.py`, ni el resto de `programar_turno`/B16.

## Verificación (arnés, sin tocar el servicio desplegado)

**a) `py_compile`** — `python -m py_compile motor_v2.py routers/programacion.py main.py routers/maquinas.py` → **PASA**.

**b) Casos del helper `es_despacho_directo`** — todos correctos:
| id_forma | largo | diám | esperado | resultado |
|---|---|---|---|---|
| 1 | 5999 | 16 | False | False |
| 1 | 6000 | 16 | True | True |
| 1 | 12000 | 16 | True | True |
| 1 | 12001 | 16 | False | False |
| 1 | 8000 | 18 | False | False |
| 1 | 8000 | 12 | True | True |
| 2 | 8000 | 16 | False | False |
| 1 | None | 16 | False | False |
**PASA** (8/8).

**c) Universo real de Cerrillos (Cubigest, solo lectura, hoy 2026-09-23)** — `_obtener_pids_pendientes(10, hoy)`: 2000 etiquetas (tope `TOP 2000` de la query), 0 clasifican FP-LC hoy. `_obtener_pids_pendientes_optisteel(10, hoy)`: 36 etiquetas, 0 FP-LC. Consistente con el informe CCa-6 (volumen 0,3-0,9%, no garantizado que haya FP-LC pendiente todo los días — las 5 piezas FP-LC del historial ya fueron *asignadas*, no están en el pool de pendientes hoy). **PASA** (0 fugas al Motor/Bolsa en el universo real de hoy).

**d) Corrida del Motor antes/después (arnés sintético, mismos insumos)** — 3 etiquetas: 2 normales (Ø12, Ø20) + 1 FP-LC (IdForma=1, largo=8000, Ø12). "Antes" = FP-LC en `MAQUINAS_ACTIVAS` + etiqueta sin filtrar (comportamiento previo). "Después" = etiqueta excluida en el filtro de entrada + `MAQUINAS_ACTIVAS` actual. Resultado: tareas no-FP-LC **idénticas** (`before == after` → True), tarea FP-LC presente en "antes" y **ausente** en "después", `bolsa_sin_asignar` de las otras 2 piezas sin cambios (2 y 2). **PASA**. No se pudo probar con una etiqueta FP-LC real de hoy porque no hay ninguna pendiente en este momento (ver c) — la prueba sintética ejercita el mismo código real.

**e) GET de planes guardados de Cerrillos con FP-LC real** — encontrados en `programacion_guardada` (SQLite, solo lectura): `(10, dia, 2026-09-23)` con 4 tareas FP-LC de 39 totales, y `(10, dia, 2026-09-21)` con 1 de 37. Llamando `obtener_programacion(10,'dia',fecha)` directo (aislado, sin contaminación de estado entre llamadas): 2026-09-23 → 35 eventos, 0 FP-LC (39-4=35 ✓). 2026-09-21 → 36 eventos, 0 FP-LC (37-1=36 ✓). `recursos` sin fila FP-LC en ambos casos. **PASA**.

**f) Reasignación manual a FP-LC** — confirmado por código: `MAQUINAS_ACTIVAS["Cerrillos"]` ya no contiene `"FP-LC"` → en `programacion.py:794-806`, `activas and m.nombre_maquina not in activas` es `True` → se agrega a `rechazadas` con motivo "máquina no activa". No se ejecutó contra la DB de producción (solo lectura de código). **PASA (verificado por código, no por request real)**.

**g) Graphify** — dependientes de `resolver_ruta`, `_obtener_pids_pendientes`, `_piezas_optisteel_por_viajes`, `_obtener_pids_pendientes_optisteel` revisados contra `graphify-out/graph.json` (snapshot 2026-09-23). Todos los llamadores pasan por las funciones que se filtraron (ver punto 2) — no se encontró ningún otro punto de entrada al universo de pendientes fuera de los ya cubiertos. **PASA**.

## Limitaciones / NO VERIFICADO
- No se ejecutó ninguna request HTTP real contra un servidor vivo (uvicorn) — las funciones se invocaron directamente en Python, que es equivalente para su lógica pero no prueba el stack ASGI/CORS/etc.
- Cubigest `MAQUINA` para "FP-LC" en `tiempos_maquina.py` (Producción por Máquina, B26) — **NO VERIFICADO**, fuera de alcance de este cambio (no se tocó ese archivo, por mandato explícito).
- El día de prueba (2026-09-23) no tenía etiquetas FP-LC *pendientes* en Cubigest en el momento de la corrida — la exclusión de entrada (punto c) se probó contra el universo real pero sin una fuga real que evitar hoy; la prueba sintética (punto d) cubre el caso con datos fabricados que sí activan la regla.
- `.env` y `optifierro_v2.db` se copiaron temporalmente al worktree para poder ejecutar el arnés con Cubigest real (solo SELECT) y SQLite real; se borraron ambos del worktree al terminar (`rm`, confirmado).
- No se coordinó con el otro CCa (B16) más allá de no tocar sus archivos — el diff no toca `programar_turno` ni el bloque de capacidad que B16 está construyendo.

## Nota de concurrencia
Durante esta sesión, el checkout principal de TO avanzó su `HEAD` de `8604d50` a `bb0c194` (el otro CCa de B16 commiteó su trabajo). Mi worktree quedó fijo (detached) en `8604d50` durante todo el proceso y no se vio afectado — verificado con `git -C optifierro_b45 log -1` antes de cerrar. El parche de este informe se generó como `git diff 8604d50`, por lo que deberá aplicarse con `git apply --3way` sobre el estado actual de B16 (`bb0c194` o posterior), tal como estaba previsto en el mandato.

## Entrega
- Parche: `/Users/montu/MontuMS/docs/agentes/diffs/B45_diff_20260923.patch` (`git diff 8604d50`, 4 archivos, rutas relativas, listo para `git apply --3way` sobre el resultado de B16).
