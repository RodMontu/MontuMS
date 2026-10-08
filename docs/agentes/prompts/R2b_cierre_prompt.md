# ENTORNO Y MODO DE TRABAJO (leer primero)
Eres Miaude/Mi TI en una ventana secundaria de ejecucion (SPP, repo tecnico "OptiFierro-V2", Torres Ocaranza).
Sesion NO INTERACTIVA (claude -p en background): nadie contesta preguntas. No pidas permiso ni confirmaciones.
Nombre de usuario: "SPP"/"el Planificador". Corres en el Mac Studio, codigo real en TO por SSH (`ssh TO`, VPN
activa). TU WORKTREE: `/c/Users/OptiFierro/Desktop/optifierro-qa-a03-mp` (rama `qa-a03-mp`).

NO subagentes ni background. NO git commit/add/stash/checkout/reset/rebase/push. Deja SIN commitear. Al
terminar: `ssh TO 'git -C /c/Users/OptiFierro/Desktop/optifierro-qa-a03-mp diff HEAD' > /Users/montu/MontuMS/docs/agentes/diffs/qa_a03_mp_diff_20260925_v2.patch`

Prohibido en produccion: docker build/up/restart, escrituras en SQLite/Cubigest. Cubigest/SQLite: SOLO SELECT
acotado. Espanol, tuteo.

## CONTEXTO — ya hiciste esta tarea antes, esto es un cierre
En tu sesion anterior (hoy) implementaste el filtro avance<100 + `universo_fechas.clasificar_fecha` en
`database_cubigest.py` (`obtener_comprometido_por_codigo`) y `materias_primas.py` (`comprometido_detalle`).
Verificado con SELECT real: Cerrillos 938.753->683.626 kg, Coronel 115.536->31.602 kg. Tu propio diff dejo
documentado: "muy_futura debería mostrarse aparte como 'sin fecha confirmada' en la UI — pendiente de
implementar". La Coordinadora acaba de copiar `universo_fechas.py` a tu worktree (`backend/universo_fechas.py`,
ya confirmado que importa bien: `python -c "import universo_fechas"` funciona).

## TU TAREA (cierre, dos partes)
1. **Verificacion real end-to-end** (antes solo pudiste hacer SELECT manual sin el modulo): ahora que
   `universo_fechas.py` existe en tu worktree, ejecuta de verdad `obtener_comprometido_por_codigo` (o el
   codigo equivalente, invocalo directo con Python si no puedes levantar el server completo sin Docker) para
   una sucursal real (ej. Cerrillos) y confirma que el resultado coincide con lo que verificaste por SELECT
   manual la vez anterior (683k kg). Si no puedes instanciar la clase completa sin Docker, dilo y documenta
   hasta donde llegaste.
2. **Cerrar el gap**: agrega la linea aparte "sin fecha confirmada" (categoria `muy_futura`, excluida de la
   demanda) en la respuesta de la API de Materia Prima — tanto en el endpoint que usa
   `obtener_comprometido_por_codigo` como en `comprometido_detalle`. Sigue el patron que ya uso la ventana
   hermana `vista-semanal-qa` para "resumen_categorias" (puedes leer su diff, SOLO LECTURA, en
   `/Users/montu/MontuMS/docs/agentes/diffs/vista_semanal_qa_diff_20260924.patch` en este Mac vía NFS — no es
   tu worktree, no lo toques, es solo referencia de patron) — no lo copies literal, adapta a la forma de
   respuesta que ya tiene Materia Prima. Incluye la leyenda de la seccion 3 del spec
   (`/Users/montu/MontuMS/docs/agentes/UNIVERSO_FECHAS_spec.md`): "No considera ITs con fecha de despacho
   mayor a 60 dias (N ITs / X.XXX kg fuera; ver aparte)".
3. Verifica con SELECT real que el numero de "muy_futura" que ahora expones aparte es coherente (kg y N de
   ITs) con la diferencia entre el total sin filtrar y el total filtrado que ya mediste antes.

## Protocolo de reporte
1. Guarda el diff (comando arriba, nombre `_v2` para no pisar el anterior).
2. Actualiza `/Users/montu/MontuMS/docs/agentes/CCa_qa_a03_mp_20260924.md` con una seccion nueva al final:
   "Cierre 25-09" — que verificaste real end-to-end, que agregaste, numeros reales.
3. Salida final por stdout: SOLO un RESUMEN de maximo 12 lineas.
