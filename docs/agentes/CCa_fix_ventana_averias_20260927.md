# Fix — ventana de averías excluía notificaciones sin resolver + bug de formato de fecha (2026-09-27)

**Commit:** `f298721`, mergeado a `master` y desplegado por Miaude.
**Reportado por:** Montu, con capturas reales de `VerAverias.aspx` (Coronel) mostrando "Dobladora 3" en SEMI
desde el 23-09, ausente en la sección Averías del SPP y sin efecto en el Gantt.

## 1. Bug reportado — confirmado y corregido

`sync_averias_cubigest()` filtraba `WHERE na.FechaRegistro >= (hoy - 3d)`. La notificación Id=74214
("Dobladora 3", Coronel, `EstadoMaq='SEMI'`, registrada 23-09) sigue sin resolver hoy (4+ días) — cae fuera
de la ventana y nunca se sincroniza.

Distinción verificada contra datos reales: `Estado` (clasificación del incidente) y `EstadoMaq` (estado real
vigente de la máquina) no son lo mismo. `FechaSolucion` no sirve para detectar si sigue abierta — Cubigest la
puebla igual a `FechaRegistro` incluso sin resolver (confirmado con el caso 74214: mismo timestamp en ambos
campos, y la columna "Solución Avería" vacía en la captura real de Montu).

**Fix:** `WHERE ... AND (na.FechaRegistro >= ? OR na.EstadoMaq != 'OP')` — cualquier notificación sin
resolver se trae siempre, sin importar antigüedad; la ventana de 3 días solo limita el histórico ya resuelto.

## 2. Bug más grave, no reportado, encontrado al verificar el fix anterior contra Cubigest en vivo

El parámetro de fecha se mandaba como `strftime("%Y-%m-%d")` (ej. `"2026-09-24"`). La sesión SQL Server de
Cubigest usa `@@LANGUAGE='Español'` (formato DMY) — interpretaba ese string como día=2026, error `22007`
(fuera de rango), la query completa fallaba y `execute_query()` la traga en silencio devolviendo `[]`.

**Consecuencia real:** `averias_cubigest` nunca tuvo una sola fila desde el deploy de anoche (`e635f6a`) — la
sección Averías con datos de Cubigest y la fusión del Motor estuvieron funcionalmente inactivas (sin datos
que fusionar), sin ningún error visible para el usuario.

**Fix:** formato `%Y%m%d` (sin separadores) — único formato que SQL Server interpreta sin ambigüedad sin
importar el `DATEFORMAT`/`LANGUAGE` de la sesión.

## 3. Verificación — parcial, bloqueada por un problema externo

Deploy (`build --no-cache && up -d --force-recreate backend`) limpio, sin errores de arranque. La
verificación end-to-end contra Cubigest real (confirmar que el Id 74214 real se sincroniza tras el fix) **no
se pudo completar**: la conexión a Cubigest falló repetidamente con error SSL
(`SSL routines::unsupported protocol`) — mismo síntoma ya documentado en `CCa9_ola3_averias_20260923.md` hace
días, no introducido por este fix. Un intento aislado de conexión simple sí funcionó; los siguientes
(incluyendo dentro de `sync_averias_cubigest`) fallaron — parece intermitente, no permanente.

El job automático (cada 30 min) va a reintentar solo; no hace falta acción manual salvo que Montu quiera
forzar una verificación más tarde cuando la conexión esté estable.

## 4. Hallazgo operativo aparte, no resuelto ahora

`sync_averias_cubigest` no tiene ningún registro de error/staleness visible (a diferencia de `sync_estado`
del otro job de sync, que sí trackea `ultimo_error_ts`/`desactualizado`). Si Cubigest falla seguido, hoy no
hay forma de notarlo salvo revisando logs del contenedor. Candidato a mejora futura (agregar tracking similar
a `sync_estado`), no bloqueante para este fix.

## 5. Estado

Fix desplegado y en producción. Verificación funcional pendiente de que la conexión a Cubigest esté estable —
el job de 30 min la completará solo, o se puede forzar manualmente (`docker exec optifierro-backend python -c
"from routers.averias import sync_averias_cubigest; sync_averias_cubigest()"`) cuando se quiera confirmar.
