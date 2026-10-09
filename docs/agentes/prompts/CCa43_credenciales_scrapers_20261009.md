---
# TAREA CCa-43 — Sacar las credenciales de Cubigest del codigo de los scrapers (preparacion de entrega del SPP)
TAG: `cred` (rama `fix-credenciales-scrapers`, directorio `optifierro_cred`). Informe DENTRO de tu worktree:
`docs/agentes/CCa43_credenciales_scrapers_20261009.md` (Miaude lo lee por SSH; no lo escribas en rutas del Mac).
Repo: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>". Crea el worktree desde el HEAD desplegado:
`git worktree add C:/Users/OptiFierro/Desktop/optifierro_cred -b fix-credenciales-scrapers 116b3fb`.

## Contexto y objetivo
El SPP se entregara con su codigo fuente completo al cliente (Torres Ocaranza). Hoy tres scrapers tienen el login web de
Cubigest escrito en texto plano (claves `Tx_Usuario` / `Tx_Pass` en un diccionario de formulario):
`backend/scraper_optisteel.py`, `backend/scraper_cuadroprogramacion.py`, `backend/scraper_cuadre_inet.py`.
Criterio de exito: cero credenciales literales en el codigo; los scrapers leen usuario y clave desde variables de entorno
y el comportamiento funcional queda IDENTICO cuando las variables estan definidas.

## Excepcion a la regla general de git (explicita)
Esta tarea SI autoriza `git add <archivos concretos>` y `git commit` LOCALES en la rama `fix-credenciales-scrapers`, dentro de
tu worktree (nunca `git add -A` ni `.`). Sigue prohibido: push, stash, checkout/reset/rebase sobre el checkout principal.

## Cambios requeridos
1. Variables de entorno nuevas: `CUBIGEST_WEB_USER` y `CUBIGEST_WEB_PASS`.
2. Un helper unico (p. ej. `backend/cubigest_credenciales.py`) con `obtener_credenciales_web()` que lea ambas variables EN EL
   MOMENTO DE LA LLAMADA, NO al importar (la app debe seguir arrancando aunque falten). Si falta alguna, lanza un error claro
   y accionable que nombre las variables faltantes (sin valores).
3. Reemplaza los literales de los tres scrapers por ese helper. Si algun otro archivo del repo (sin contar `backend/venv/`)
   contiene el mismo login, reportalo y corrigelo igual.
4. Agrega ambas variables, con valores vacios y un comentario, a `backend/.env.example`.
5. Credenciales ausentes: el job de importacion registra un error claro y sigue vivo (no tumba el backend ni el scheduler).

## Reglas de seguridad
- NO imprimas ni copies el valor de la clave actual en ningun informe, log, commit ni salida. Documenta solo nombres de variables.
- Cubigest y la BD de produccion: SOLO LECTURA. Cualquier prueba que escriba usa una COPIA de la BD dentro de tu worktree
  (`cp /c/Users/OptiFierro/Desktop/optifierro/backend/optifierro_v2.db <tu_worktree>/backend/`). Nunca corras unittest/scripts
  con cwd en el `backend` del checkout principal (ahi vive la BD real). Usa el mismo metodo de pruebas que CCa-41
  (ver `docs/agentes/CCa41_historial_gris_20261008.md` en el repo de TO).
- No ejecutes importaciones reales contra Cubigest. No build/up/restart de contenedores ni deploy (lo hace Miaude).

## Pruebas
- Tests nuevos: (a) con variables definidas el helper las devuelve; (b) sin ellas lanza el error esperado y el mensaje no
  contiene valores; (c) el modulo de cada scraper se importa sin las variables definidas.
- Los tests existentes de scrapers (incluido el de regresion de CCa-40) siguen pasando.
- `grep` final sobre el worktree (excluyendo `backend/venv/`): cero literales asignados a `Tx_Pass` y cero apariciones del
  valor previo (compara sin imprimirlo: usa `grep -c` y reporta solo el conteo).

## Entregables
- Commits locales en `fix-credenciales-scrapers`; `git status` limpio al terminar; sin scripts de depuracion sueltos.
- Informe: archivos tocados, tests y resultado, resultado del grep final (conteos), y la lista exacta de variables que deben
  existir en `backend/.env` de TO antes del deploy.
- Salida final por stdout: resumen de 10 lineas maximo.

## NO HAGAS
No toques `motor_v2.py`, `routers/programacion.py`, `cargos.py` ni frontend. No refactorices los scrapers mas alla del cambio de
credenciales. No cambies nombres de funciones publicas ni firmas.
