
---
# TAREA CCa-38 — Verificar/corregir: cajita gris-y-candado (etapa confirmada en Cubigest) en produccion HOY, compatibilidad con GAN2
TAG: `hist` (rama `fix-hist-gris`, directorio `optifierro_hist`). Informe: `CCa38_hist_gris_20261006.md`.
Repo: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>". Worktree desde el HEAD actual (`git log -1
--format=%h`; hoy `46f91fa` o posterior). NUNCA pruebas contra la BD real del checkout principal (copia o
`docker run --rm -v .../backend:/work <imagen> python -`). Commits locales, sin push, sin build/deploy (lo hace Miaude).

## Contexto documentado (leelo primero, no reimplementes lo que ya existe)
`docs/agentes/CCa_gantt_etapa_gris_20260926.md`, `docs/entrega/v2/MANUAL_USUARIO_SPP.md` (lineas ~129-145, ~315,
~337, ~474), `docs/entrega/v2/VERIFICACION_MANUAL_USUARIO.md` (item 5), `docs/bitacora_accesos_torres_ocaranza.md`
(entrada "2026-09-26 (noche)"), `docs/LOG_CAMBIOS_2026.md` (entrada "2026-09-26 ... cajita gris e inamovible").
Diseno: tabla `etapa_congelada`, job `_job_verificar_etapas_completadas` (cada 30 min) marca como congelada la
PRIMERA etiqueta de un grupo cuando Cubigest confirma que esa etapa (etiqueta+maquina) ya se ejecuto; el frontend
(`isEtapaCongelada`, `GestorProgramacion.tsx`) pinta la cajita gris con candado y bloquea el drag; soltar otra
cajita encima debe rechazar con alert. Hay test `test_gantt_etapa_gris` (paso ayer, pero corrio contra datos
sinteticos: NO prueba contra el estado real de hoy).

## Pregunta de Montu (textual): "no tengo claro si solamente se diseño esto o si se implementó... es importante que
esto quede OK hoy para poder entregar el SPP." Y: estaba previsto que, por este mecanismo, el Gantt de un DIA YA
PASADO quede completo (o casi) en gris, funcionando como vista de historial de ese dia.

## Que hacer
1. Verificacion end-to-end EN VIVO (solo lectura primero): para las 3 plantas, hoy (06-10), encuentra al menos una
   cajita cuya primera etiqueta Cubigest ya marca ejecutada y confirma que (a) hay una fila en `etapa_congelada`
   para ella, (b) `GET /api/programacion` la devuelve marcada de forma que el frontend la pinte gris+candado, (c)
   intentar reasignarla via `/api/programacion/reprogramar` (en tu worktree, NO contra el deploy real: usa una
   copia de la BD para esta prueba especifica) es rechazado.
2. CRITICO: la agrupacion GAN2 (cajita = viaje, 29-09, posterior a esta funcionalidad del 26-09) cambia que es
   "la cajita": ahora una cajita puede agrupar VARIAS etiquetas de maquinas/horarios consecutivos. Verifica que
   `_construir_evento_grupo` SIGUE propagando el flag de congelada correctamente cuando se agrupan etiquetas (el
   manual dice "para, al menos, la primera etiqueta del grupo" — confirma si esto sigue siendo cierto tras los
   cambios de F4/F8 de ayer, que tambien tocaron `_construir_evento_grupo`/el bloque de `recursos` en
   `programacion.py`). Si el flag se perdio en algun punto de la cadena (agrupacion, o el nuevo calculo de
   `viene_de_futuro` de F8 pisando el estilo), corrigelo ahi — es el lugar logico del bug si lo hay.
3. Vista de "dia pasado" como historial: revisa si HOY, al seleccionar una fecha anterior en el selector de fecha
   del Gantt, las cajitas de ese dia que ya se completaron en Cubigest se ven grises (si todas las etapas de ese
   dia estan confirmadas, el dia entero deberia quedar historico). Si esto nunca se implemento (solo el bloqueo
   cajita-por-cajita, no una "vista de historial" por dia), dilo claramente en el informe: NO inventes esa pieza
   si no hay spec mas detallada que la frase de Montu; limitate a reportar el gap con precision (que existe HOY
   si seleccionas una fecha pasada, cajita por cajita) y que falta para que sea "historial completo" (si acaso
   algo), dejando una recomendacion breve, SIN IMPLEMENTARLA sin que Miaude/Montu decidan alcance.
4. Corrige cualquier bug real que encuentres en el punto 2 (eso si es claramente bug, no gap de alcance). Agrega
   un test con datos de HOY (fixture realista: viaje con 3 etiquetas consecutivas en la misma maquina, 2 ya
   confirmadas en Cubigest, 1 no) que cubra la interaccion agrupacion+congelada+F8.
5. Si todo funciona bien (sin bug), dilo explicitamente con la evidencia del punto 1, y cierra la tarea sin tocar
   codigo mas alla del test de regresion que agregues para dejarlo cubierto hacia adelante.

## Archivos permitidos
`backend/routers/programacion.py` (solo lo relacionado a `etapa_congelada`/`_construir_evento_grupo`/el job),
`frontend/.../GestorProgramacion.tsx` (solo `isEtapaCongelada` y el candado, si hace falta), tests nuevos.

## NO HAGAS
No implementes la "vista de historial por dia completo" sin autorizacion explicita — solo diagnostica y reporta
el gap. No toques `cargos.py`, `motor_v2.py` (operadores), ni los ribetes de adelanto/no-A630 (F8, ya cerrado).
No hagas build/deploy.
