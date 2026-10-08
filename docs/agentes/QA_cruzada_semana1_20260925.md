# QA cruzada — Próximas Semanas vs Compromisos Futuros, Cerrillos semana 1

**Fecha:** 2026-09-25 · **Agente:** Miaude (ventana de diagnóstico, solo lectura) · **Sucursal:** Cerrillos
(OptiFierro id=10, Cubigest sucursal=4)

**Nota de fecha:** el criterio de aceptación del spec (§5) dice literal "24–30 sep" (escrito 24-09). Hoy es
25-09, así que "semana 1" se tomó como **hoy .. hoy+6d = 2026-09-25 .. 2026-10-01** (rolling), que es
exactamente como la define `calendario_futuro.py` para su semana 1. No se usó el rango literal 24-30 sep.

## Método

Sin Docker, sin tocar archivos de los worktrees. Se instanció Python directo (3.11.8) en cada worktree vía
`ssh TO`, exportando las credenciales de Cubigest ya usadas por `optifierro-backend` (leídas de
`backend/.env` del checkout principal `optifierro`, solo lectura — no se copiaron a los worktrees ni se
escribió ningún archivo en ellos). Los dos worktrees están en el mismo commit `f430b75`, rama respectiva
(`proximas-semanas` / `vista-semanal-qa`), sin cambios pendientes.

- **Próximas Semanas**: invocación directa de `obtener_calendario_futuro(sucursal_id=10)` desde
  `optifierro-proximas-semanas/backend/routers/calendario_futuro.py` (función completa, sin mocks).
- **Compromisos Futuros / Vista Semanal**: invocación directa de `_obtener_pids_pendientes(10, hoy)` desde
  `optifierro-vista-semanal-qa/backend/routers/programacion.py:1448` (misma función que usa
  `compromisos_semanales.py:53` y `/semanal`), filtrando el resultado al mismo rango de fechas
  `[hoy, hoy+6]` para comparar manzanas con manzanas.

## Limitación encontrada

El endpoint HTTP completo `GET /api/compromisos-semanales` **no pudo invocarse end-to-end**: el
`optifierro_v2.db` (SQLite) de ambos worktrees no tiene las tablas `sesion_planificacion` ni `it_detenida`
(seed de datos incompleto en estos checkouts de prueba). Se evitó ese camino y se llamó directo a
`_obtener_pids_pendientes`, que es la única función que aporta el universo de kg (las tablas faltantes solo
afectan sesión de reubicación manual y flag "detenida", no el total de kg). Limitación documentada, no
resuelta (no se debía tocar nada en los worktrees).

## Resultado 1 — mismo rango exacto (hoy .. hoy+6, 25-09 .. 01-10)

| Fuente | kg total | n° ITs/viajes |
|---|---|---|
| Próximas Semanas — `semanas[0].kg_total` (`calendario_futuro.py`) | **189.345,0 kg** | 26 |
| Compromisos Futuros — universo `_obtener_pids_pendientes` filtrado al mismo rango | **189.345,7 kg** | 26 |

**Diferencia: 0,7 kg (0,0004%) — coincide.** El desfase de redondeo es despreciable (`round(x,1)` por
etiqueta vs por IT agregada).

**Veredicto parcial: OK — el criterio de aceptación del spec §5 (QA-A-02) se cumple hoy** para el mismo
rango de fechas: ambos caminos comparten el mismo universo subyacente (`IT`/`Viaje`/`detallePaquetesPieza`/
`piezas`, avance<100, estados PEN/IET/APR/ING, exclusión FP-LC vía `es_despacho_directo`). La discrepancia
">2x" que reportaba el spec el 24-09 ya no se reproduce con el código actual (`f430b75`) para ventanas
idénticas.

## Hallazgo — la discrepancia visible en la UI no es de datos, es de definición de "semana"

Al comparar semana 1 de Próximas Semanas contra el **valor por defecto** de Compromisos Futuros
(`semana_offset=0`, que usa semana calendario lunes-domingo — `compromisos_semanales.py:21-24`,
`_lunes_de_semana`), los rangos de fechas NO son el mismo:

| Fuente | Rango | kg total | n ITs |
|---|---|---|---|
| Próximas Semanas, semana 1 | 25-09 .. 01-10 (hoy..+6d, rolling) | 189.345,0 kg | 26 |
| Compromisos Futuros, offset=0 | 21-09 .. 27-09 (lun-dom semana calendario) | 713,0 kg | 1 |

Esta es la comparación que un usuario haría mirando ambas pantallas "hoy" sin ajustar el selector de semana
de Compromisos Futuros — y ahí SÍ hay una diferencia enorme (266x), pero la causa raíz **no es un filtro de
datos distinto**: es que casi toda la carga de la semana 1 de Próximas Semanas (28-09 al 01-10) cae fuera de
la semana calendario lun-dom vigente (21-27 sep) que usa por defecto Compromisos Futuros.

- `calendario_futuro.py:187` define semana 1 = `hoy .. hoy+6` (rolling, se recalcula cada día).
- `compromisos_semanales.py:39,47` con `semana_offset=0` usa `_lunes_de_semana(0)` = lunes de la semana
  calendario vigente (fijo hasta el próximo lunes), **no** `hoy..hoy+6`.

**RCA:** no es QA-A-02 (ya resuelto para el mismo rango). Es una inconsistencia de UX/contrato entre
componentes: "semana 1" significa cosas distintas en las dos pantallas. Si Montu quiere que ambas pantallas
sean comparables por defecto sin tocar el selector, una de las dos tendría que alinear su definición de
"semana 1" a la otra (no se toca código en esta tarea — solo diagnóstico).

## Hallazgo secundario (no pedido, encontrado al ejecutar) — `clasificar_fecha` falla silenciosamente en `_obtener_pids_pendientes`

`programacion.py:1611` llama `clasificar_fecha(fecha_str, horizonte)` pasando `fecha_str` como **string**
(viene de `f.get("fecha_despacho")`, `CONVERT(varchar(10), ...)` en el SQL), pero
`universo_fechas.clasificar_fecha` espera `fecha_despacho: date` y hace `fecha_despacho - hoy` — con un
string revienta `TypeError`, capturado por el `except Exception` de la línea 1612-1613, y
`f["categoria_fecha"] = None` para **todas** las etiquetas (792/792 en esta corrida). Esto no afecta el kg
total (el filtro por rango de fechas es independiente), pero sí rompe silenciosamente la línea "Atrasado
≤30d" / "Sin fecha confirmada" de Vista Semanal (`resumen_categorias`, `programacion.py:690-694`), que
siempre queda en 0 porque nunca hay `cat in resumen` (siempre `None`). Falta un `date.fromisoformat(fecha_str)`
antes de pasarlo a `clasificar_fecha`. No corregido (fuera de alcance, solo lectura).

## Resumen de limitaciones

- No se pudo invocar el endpoint HTTP completo de Compromisos Futuros (faltan tablas SQLite en el seed de
  los worktrees de prueba) — se usó la función núcleo `_obtener_pids_pendientes` directamente, que es la
  única relevante para el kg total.
- Credenciales de Cubigest reutilizadas de `optifierro/backend/.env` (checkout principal, solo lectura, no
  copiadas a ningún worktree).
- No se ejecutó ninguna escritura: sin git add/commit/stash/checkout/reset/push, sin docker build/up/restart,
  sin editar un solo archivo en los worktrees.
