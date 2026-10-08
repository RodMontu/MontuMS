
---
# TAREA CCa-41 — Historial en gris: verificar de punta a punta y cerrar brechas contra la especificacion de Montu
TAG: `hist2` (rama `fix-historial-gris`, directorio `optifierro_hist2`). Informe DENTRO de tu worktree:
`docs/agentes/CCa41_historial_gris_20261008.md` (Miaude lo lee por SSH; no lo escribas en rutas del Mac).
Repo: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>". Crea el worktree desde el HEAD actual:
`git worktree add C:/Users/OptiFierro/Desktop/optifierro_hist2 -b fix-historial-gris 8a4f903`.

## Impacto (Graphify, consultado por Miaude, 08-10-2026; orientativo)
Los archivos que probablemente toques y sus vecinos: `backend/routers/programacion.py` (lo usan `main.py`,
`motor_v2.py`, `routers/operadores.py`, `routers/compromisos_semanales.py`, `universo_fechas.py`, `event_log.py`,
`database_cubigest.py`, `cargos.py` y varios tests) y `frontend/.../GestorProgramacion.tsx` (lo usan `App.tsx`,
`CompromisosSemanales.tsx`, `SyncEstado.tsx`, `useGanttZoom.ts`, `constants.ts`). Son modulos centrales: haz cambios
LOCALIZADOS (una funcion o un bloque), no refactores. `seccion_7_averias.py`/`app.py` son un prototipo Streamlit
abandonado: ignoralos. Tras tocar codigo, avisa a Miaude para que regenere el grafo; no lo regeneres tu.

## Especificacion de Montu (cita literal, 06-10-2026) — es la unica fuente de requisitos
"Los trabajos (cajitas) que se programaron para hoy en este turno (día) y que ya están finalizados en Cubigest, debe
ponerse de un color gris y no se podrán mover, ya que es 'historia'; además se había considerado que esto iba a
repercutir que las Gantt de los días pasados (a partir de este cambio) iban a quedar como historial, quedando con
todas las cajitas de color gris (si es que se terminaron todos los trabajos). ... Como haya sido, es importante que
esto quede OK hoy para poder entregar el SPP."
Documentado en: `/Users/montu/MontuMS/docs/agentes/CCa_gantt_etapa_gris_20260926.md`,
`/Users/montu/MontuMS/docs/entrega/v2/MANUAL_USUARIO_SPP.md` (secciones sobre etapa congelada) y la entrada
"2026-09-26 cajita gris e inamovible" de `/Users/montu/MontuMS/docs/LOG_CAMBIOS_2026.md`. Mecanismo existente: tabla
`etapa_congelada`, job `_job_verificar_etapas_completadas` (cada 30 min), `_marcar_etapas_congeladas`,
`isEtapaCongelada` en el frontend. El 06-10 se corrigio UN hueco (commit `98d38d2`): al leer un dia que cae al
respaldo `programacion_guardada` ahora se reaplica el marcado. Eso se probo con datos sinteticos, NO de punta a punta.

## Que hacer
1. VERIFICACION EN VIVO (solo lectura; GET a la API del backend desde el contenedor, p. ej. `docker exec
   optifierro-backend python -c ...` con urllib contra `http://localhost:8000/api/programacion?sucursal=<id>&turno=...&fecha=...`;
   Calama=1, Cerrillos=10, Coronel=14). Para HOY y para al menos 2 dias pasados que tengan plan guardado, en las 3
   plantas, cuantifica: cajitas totales, cuantas estan marcadas congeladas, y cuantas deberian estarlo segun Cubigest
   (lectura SQL de solo lectura via el codigo existente de `database_cubigest.py`; la conexion ya funciona desde hoy).
   Reporta la tabla.
2. Responde con evidencia estas preguntas concretas (pueden ser fuente de brechas reales):
   a. El job que marca etapas solo mira el plan "de hoy" en memoria? Cuando termina el dia (o el turno), existe una
      pasada final que marque lo que se completo despues del ultimo ciclo de 30 min? Si no, las cajitas terminadas
      al final de la jornada quedarian sin marcar para siempre en el dia pasado (el historial quedaria incompleto).
   b. Turno noche: cruza medianoche. Que fecha usa el plan guardado y el marcado? Hay riesgo de que una cajita del
      turno noche quede en el dia equivocado o sin marcar?
   c. Al seleccionar una fecha pasada en la pantalla, una cajita gris sigue siendo no arrastrable y rechaza soltar
      encima (igual que hoy)? Y las NO terminadas de un dia pasado: se comportan como siempre (no inventes un modo nuevo).
   d. La cajita-viaje (GAN2 agrupa etiquetas): una cajita con algunas etiquetas terminadas y otras no, como se pinta?
      Esta documentado "al menos la primera etiqueta del grupo"; confirma que el comportamiento coincide con lo
      documentado y describe el resultado real.
3. Corrige SOLO las brechas que contradigan la especificacion de Montu de arriba (ej. si 2.a es real: una pasada
   final de cierre de dia/turno reutilizando las funciones existentes). NO agregues funcionalidades que Montu no
   pidio (p. ej. un "modo historial" con banner, bloqueo de todo el dia, nuevos botones). Si encuentras algo que
   parece valioso pero esta fuera de la especificacion, describelo en el informe como "propuesta" sin implementarlo.
4. Tests nuevos para cada correccion (con fixtures realistas, sobre una COPIA de la BD).
5. Si tras verificar todo NO hay brechas, dilo explicitamente con la evidencia; en ese caso solo agrega, si falta, un
   test de regresion que cubra el escenario "dia pasado + cajita-viaje + congelada".

## Reglas
- Cubigest y la BD de produccion: SOLO LECTURA. Para cualquier prueba que escriba, usa una copia de la BD dentro de tu
  worktree (`cp /c/Users/OptiFierro/Desktop/optifierro/backend/optifierro_v2.db <tu_worktree>/backend/`). Nunca corras
  `unittest`/scripts con cwd en el `backend` del checkout principal (ahi vive la BD real).
- No pongas credenciales en ningun archivo. Si necesitas llamar a Cubigest, usa el codigo existente. Borra todo
  script de depuracion antes de terminar; `git status` debe quedar limpio salvo lo que quieres commitear.
- Commits locales, sin push, sin build/deploy ni restart de contenedores (lo hace Miaude).

## NO HAGAS
No toques `motor_v2.py`, `cargos.py`, ni los ribetes (F8). No modifiques la logica de adelanto. No cambies colores ni
estilos existentes. No refactorices `programacion.py`. No toques averias (otra tarea en paralelo).
