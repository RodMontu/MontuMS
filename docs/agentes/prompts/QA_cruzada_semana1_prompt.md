# ENTORNO Y MODO DE TRABAJO (leer primero)
Eres Miaude/Mi TI en una ventana de DIAGNOSTICO puro (SPP, repo "OptiFierro-V2", Torres Ocaranza). Sesion NO
INTERACTIVA: nadie contesta preguntas. No pidas permiso: decide con evidencia y registra en el informe.
Nombre de usuario: "SPP"/"el Planificador". Corres en el Mac Studio, codigo real en TO por SSH (`ssh TO`, VPN
activa). Espanol, tuteo.

**Esta tarea es SOLO LECTURA, sin worktree propio.** Trabajas sobre DOS worktrees existentes, sin editar
NADA en ninguno de los dos — solo los invocas/lees para comparar numeros:
- `/c/Users/OptiFierro/Desktop/optifierro-vista-semanal-qa` (rama `vista-semanal-qa`)
- `/c/Users/OptiFierro/Desktop/optifierro-proximas-semanas` (rama `proximas-semanas`)
Ambos ya tienen `backend/universo_fechas.py` copiado (confirmado que importa bien en los dos). NO ejecutes
git commit/add/stash/checkout/reset/push en ninguno. NO toques ni un archivo. Cubigest/SQLite: SOLO SELECT
acotado, una consulta a la vez. Prohibido docker build/up/restart.

Lee (ya en este Mac via NFS): `/Users/montu/MontuMS/docs/agentes/UNIVERSO_FECHAS_spec.md` seccion 5, criterio
de aceptacion: "Próximas Semanas Cerrillos, semana 1 (24–30 sep): kg debe coincidir con Compromisos Futuros
para el mismo rango (hoy difieren >2×, QA-A-02)". La fecha de hoy YA NO es 24-09 (avanzo un dia) — usa
"semana 1" relativa a hoy (hoy..+6d), no el rango literal 24-30 sep, y anotalo en el informe.

## TU TAREA
Para Cerrillos (sucursal_id=10, Cubigest sucursal=4), calcula y compara:
1. **Próximas Semanas**: invoca `obtener_calendario_futuro(sucursal_id=10)` (worktree `proximas-semanas`,
   `backend/routers/calendario_futuro.py`) — directo por Python si puedes instanciar sin Docker, si no,
   replica su query+logica en un script suelto de solo lectura. Extrae `semanas[0].kg_total` (semana 1).
2. **Compromisos Futuros / Vista Semanal**: invoca la logica equivalente en el worktree `vista-semanal-qa`
   (`backend/routers/compromisos_semanales.py` o `programacion.py` `/semanal`, el `resumen_categorias` o el
   filtro por semana que corresponda) para el mismo rango de fechas y la misma sucursal.
3. Compara los dos kg totales para el mismo rango exacto de fechas. Si coinciden (o estan razonablemente
   cerca, indica el % de diferencia y por que), es un OK. Si no coinciden, haz RCA con evidencia
   (archivo:linea de cada lado) de por que difieren — granularidad etiqueta vs IT, filtro de estado distinto,
   ventana de fechas distinta, lo que sea — sin arreglarlo, solo diagnosticarlo.
4. Documenta ambos numeros reales, el metodo exacto que usaste para obtenerlos (invocacion directa o replica
   de query), y cualquier limitacion (ej. si no pudiste instanciar algo sin Docker).

## Protocolo de reporte
1. Informe en `/Users/montu/MontuMS/docs/agentes/QA_cruzada_semana1_20260925.md`: los dos numeros, el
   metodo, coincide o no coincide (con RCA si no), limitaciones.
2. Salida final por stdout: SOLO un RESUMEN de maximo 12 lineas con el veredicto (coincide / no coincide /
   no se pudo verificar) primero.
