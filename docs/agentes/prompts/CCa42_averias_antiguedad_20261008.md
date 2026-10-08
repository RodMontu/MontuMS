
---
# TAREA CCa-42 — Averias manuales: mostrar antiguedad y marcar las que llevan mucho tiempo abiertas
TAG: `averias` (rama `fix-averias-antiguedad`, directorio `optifierro_averias`). Informe DENTRO de tu worktree:
`docs/agentes/CCa42_averias_antiguedad_20261008.md` (Miaude lo lee por SSH; no lo escribas en rutas del Mac).
Repo: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>". Crea el worktree desde el HEAD actual:
`git worktree add C:/Users/OptiFierro/Desktop/optifierro_averias -b fix-averias-antiguedad 8a4f903`.

## Impacto (Graphify, consultado por Miaude, 08-10-2026; orientativo)
- `backend/estado_maquinas.py`: lo usan `main.py`, `motor_v2.py` y `test_estado_maquinas.py` (el Motor lee el estado
  efectivo para decidir si una maquina esta detenida: NO alteres esa semantica).
- `backend/routers/averias.py`: lo usan `main.py`, `models.py` y `test_averias_cubigest.py`.
- `frontend/.../GestorAverias.tsx`: lo usan `App.tsx` y `constants.ts`.
Cambios LOCALIZADOS y aditivos. `seccion_7_averias.py` (raiz) es un prototipo Streamlit abandonado: ignoralo. Tras tocar
codigo, avisa a Miaude para regenerar el grafo; no lo regeneres tu.

## Contexto (documentado por CCa-37 el 06-10; ver su informe `docs/agentes/CCa37_urgentes_20261006.md` en el repo)
Una averia MANUAL de COIL 14 (Calama) del 23-03-2026 nunca se cerro y siguio mostrando la maquina como detenida/
semioperativa durante meses. Por diseno la fuente manual NO caduca (para que el jefe de planta la vea y la cierre),
y eso es correcto. Montu autorizo cerrar esa averia puntual (ya hecho). CCa-37 recomendo que el sistema AVISE cuando
una averia manual lleva mucho tiempo abierta, para que no vuelva a pasar desapercibida. Esa recomendacion es esta tarea.

## Que hacer (minimo y aditivo)
1. Investiga como se guardan y se devuelven las averias manuales: tabla, campos de fecha de inicio, y que entrega
   `routers/averias.py` al frontend. Confirma si ya existe la fecha de inicio en la respuesta; si no, agrega el campo
   (solo lectura, sin cambiar semantica ni esquema si no es necesario).
2. En `GestorAverias.tsx`, para cada averia MANUAL abierta muestra su antiguedad ("hace N dias"/"hace N horas") junto a
   la fecha de inicio. Las averias que vienen de Cubigest NO se tocan (su ciclo lo maneja Cubigest).
3. Marca visualmente (icono/etiqueta discreta, sin cambiar la paleta existente) las averias manuales con antiguedad
   mayor a un umbral definido como UNA constante nombrada al inicio del archivo (`AVERIA_MANUAL_ANTIGUA_DIAS = 7`),
   con un tooltip tipo "Averia manual abierta hace N dias: confirme si sigue vigente". El umbral de 7 dias es un valor
   inicial razonable que Montu debera confirmar: dejalo facil de cambiar y menciona en el informe que es un valor por
   defecto a validar.
4. NO cierres, caduques ni modifiques ninguna averia automaticamente, NO cambies `estado_maquinas.py` ni el calculo del
   estado efectivo que usa el Motor, y NO agregues notificaciones, correos ni jobs nuevos.
5. Si te parece valioso mostrar tambien un indicador en la pantalla de Programacion, NO lo implementes (esa pantalla la
   toca otra tarea en paralelo): descríbelo como "propuesta" en el informe.
6. Tests: backend si agregas un campo a la respuesta (sobre una COPIA de la BD); frontend `npx tsc --noEmit` limpio
   (si tu worktree no tiene `node_modules`, usa un junction temporal al del checkout principal con `mklink /J` y
   retiralo con `rmdir` al terminar, sin borrar el contenido del destino).

## Reglas
- BD de produccion y Cubigest: solo lectura. Nunca corras `unittest`/scripts con cwd en el `backend` del checkout
  principal (ahi vive la BD real): copia la BD a tu worktree para cualquier prueba.
- No pongas credenciales en ningun archivo; borra scripts de depuracion; `git status` limpio al terminar salvo lo
  commiteado. Commits locales, sin push, sin build/deploy ni restart (lo hace Miaude).

## NO HAGAS
No toques `programacion.py`, `GestorProgramacion.tsx`, `motor_v2.py` ni `cargos.py`. No cambies el comportamiento de
averias de Cubigest. No agregues dependencias nuevas.
