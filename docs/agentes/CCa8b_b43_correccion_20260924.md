# CCa-8b — Corrección B43 "adelantada" (2026-09-24)

## Problema
Commit `2508cb2` marcaba "adelantada" con `dias_atraso < 0` (fecha real de
despacho posterior a hoy). Resultado real medido: 29/35 cajitas de Cerrillos
marcadas — no distingue "despacho futuro" de "origen futuro", volviendo el
indicador inútil.

## Señal real usada
`_obtener_pendientes_bolsa_optisteel` (routers/programacion.py) arma la Bolsa
de Trabajo con:
```sql
SELECT viaje, fecha FROM cuadro_programacion_optisteel
WHERE sucursal_id = ? AND fecha > ?
```
Por construcción, **todo** item que esa función devuelve viene de un día
futuro del Cuadro OptiSteel (B18/B34) — es exactamente la definición de
negocio de "adelantada". Se agregó el campo `viene_de_futuro: true` a cada
item de esa función.

Para que la señal sobreviva al arrastre manual desde la Bolsa hacia una
máquina (`/api/programacion/reprogramar`, rama "el pid nunca existió en
global_eventos" — FIX 22-09), se sumó `viene_de_futuro` a
`ReprogramarRequest` (models.py) y al dict `_tarea_nueva`, siguiendo el
mismo patrón ya usado para `obra`/`codigo_viaje`/`kilos`. `_tarea_a_evento`
lo propaga al evento del Gantt.

Frontend (`GestorProgramacion.tsx`): `vieneDeFuturo` ahora lee
`ev.viene_de_futuro === true` en vez de `dias_atraso < 0`; el drag-handler
que llama a `/reprogramar` desde la Bolsa incluye
`viene_de_futuro: tarea.viene_de_futuro ?? false` en el payload. Estilo
visual sin cambios (ribete punteado celeste + leyenda de `2508cb2`).

## Archivos tocados
- `backend/models.py`
- `backend/routers/programacion.py`
- `frontend/src/components/domain/GestorProgramacion.tsx`

Commit nuevo `9fd96ed` encima de `88964ac` (B42/B43/B44a intactos, sin
reescribir historia).

## Verificación
- `py_compile backend/models.py backend/routers/programacion.py` → OK.
- `npx tsc --noEmit` (frontend) → OK, sin errores.
- **No hubo prueba end-to-end contra el servidor vivo**: el backend en
  `localhost:8001` corre dentro del contenedor Docker `optifierro-backend`,
  montado sobre el checkout principal (`.../optifierro/backend`), NO sobre
  este worktree (`optifierro_g`). Docker build/up/restart está prohibido en
  este encargo, así que no fue posible levantar el código corregido en el
  puerto vivo dentro del plazo.
- Verificación alternativa con SQL de solo lectura contra la DB real
  (`optifierro_v2.db`, mismo query que usa la función corregida), hoy
  2026-09-24:

  | Sucursal | Filas futuras (Cuadro) | Viajes distintos | Total filas Cuadro |
  |---|---|---|---|
  | Calama (1)    | 62 | 61 | 141 |
  | Cerrillos (10)| 5  | 5  | 149 |
  | Coronel (14)  | 2  | 2  | 27  |

  Es el pool de la Bolsa en vivo (lo que *podría* arrastrarse); el número de
  cajitas que terminan marcadas en el Gantt de hoy es un subconjunto aún
  menor (solo lo que se arrastra manualmente). `programacion_manual` para
  hoy está vacío en las 3 plantas (nadie arrastró nada aún), por lo que hoy
  el conteo en pantalla sería 0/N — consistente con "minoría", pero no
  permite un test positivo del mecanismo end-to-end sin producir una
  asignación real.
- Trazado manual del código (sin ejecutar servidor) confirma el flujo
  completo: bolsa (`viene_de_futuro: True`) → payload de drag → `_tarea_nueva`
  → `_tarea_a_evento` → evento con `viene_de_futuro`. No se pudo ejecutar
  este trazado como test dinámico porque el entorno Python del worktree
  (`backend/venv`) no resolvió correctamente sobre la conexión SSH
  disponible (binario venv no ejecutable desde ahí); se optó por no forzar
  más intentos dado el plazo.

## Conclusión
Indicador corregido y commiteado con la señal real de negocio. Recomendado:
que alguien con acceso directo al Docker de TO reconstruya el contenedor
cuando corresponda mergear esta rama, y arrastre una cajita real desde la
Bolsa para confirmar visualmente el ribete antes de dar por cerrado B43.
