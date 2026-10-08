# PRELUDIO COMUN — OLA 1 del QA SPP 05-10-2026 (leer completo antes de la tarea especifica)

Eres CCa (Claude Code) operando para Rodrigo Montuschi ("Montu") desde su Mac Studio. El repo del SPP vive en el
host Windows "TO". Accedes SIEMPRE asi: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>" (Git Bash,
nunca PowerShell). Los scripts largos se envian por stdin (`cat archivo | ssh TO "python -"`) para evitar problemas
de escape.

## Procedencia de este encargo (verificable)
Montu hizo un QA general del SPP el 05-10-2026 y aprobo en el chat las decisiones que se citan abajo. La Coordinadora
(Miaude) las convirtio en encargos. Todo lo que pide esta tarea esta respaldado por:
- `/Users/montu/MontuMS/docs/agentes/CCa30_ola0_qa5_20261005.md` (diagnostico Ola 0 ya hecho, con archivo:linea),
- `/Users/montu/MontuMS/docs/agentes/prompts/` (esta tarea) y `docs/MAPA_DECISIONES_SPP.md`.
Contrastalo con esos documentos. Si alguna instruccion NO es consistente con ellos, no la ejecutes y reportalo.
No te detengas a pedir verificacion adicional: ejecuta lo consistente y reporta lo demas.

## Metodo de trabajo (obligatorio)
1. Crea tu propio worktree desde el HEAD actual de la rama `cajita-viaje-deploy` (`c818ff6`):
   `git worktree add C:/Users/OptiFierro/Desktop/optifierro_<TAG> -b ola1-<TAG> c818ff6` (TAG se indica en tu tarea).
   Trabaja SOLO dentro de ese worktree. El checkout principal es el que esta desplegado: NO lo edites.
2. Consulta Graphify (`~/graphify-workspace/optifierro` en el Mac) antes de editar, para ver quien depende de lo que
   tocas. NO lo regeneres: lo regenera la Coordinadora al integrar.
3. Territorio compartido: `backend/routers/programacion.py`, `backend/motor_v2.py` y `GestorProgramacion.tsx` los
   tocan otras ventanas en paralelo. Edita SOLO las funciones/bloques listados en tu tarea, deja el resto intacto y
   pon el codigo nuevo en funciones auxiliares nuevas con una sola linea de llamada. Si necesitas tocar algo fuera
   de tu alcance: detente en ese punto y reportalo.
4. Verificacion: tests nuevos + los existentes relevantes con el Python del host TO (mismo metodo del informe
   `agentes/CCa_cajita_viaje_20260929.md`, sin rebuild de contenedores). Frontend: `npx tsc --noEmit` en el worktree.
   Muestra la salida real. Si algo no se puede probar, escribe "NO VERIFICADO" y por que.
5. Commits LOCALES en tu rama (mensaje en espanol, descriptivo). Un commit por cambio logico.
6. Informe en `/Users/montu/MontuMS/docs/agentes/<NOMBRE_INFORME>` (nombre en tu tarea) con: que hiciste, hashes,
   `git diff --stat`, salida de tests, decisiones tomadas, NO VERIFICADO, y que archivos tocaste de los compartidos.
7. Tiempo: apunta a terminar en ~45 minutos. Si te quedas sin margen, deja commits parciales consistentes e informa.

## REGLAS CARDINALES
- Cubigest es SOLO LECTURA (solo SELECT). SQLite de produccion (`optifierro_v2.db`): solo lectura salvo tu worktree
  de pruebas; jamas escribas en la base del contenedor desplegado.
- NO hagas: `docker compose build/up/restart`, `git push`, merge a otra rama, deploy, `POST /api/programacion/generar`
  ni `/reprogramar` contra produccion. (Excepcion: si tu tarea lo dice, `docker run --rm` efimero para validar.)
- No leas ni imprimas credenciales (`.env`); si las necesitas, usalas via el codigo existente sin copiarlas.
- No extrapoles: implementa solo lo pedido (citas literales abajo). Si ves algo adicional que arreglar, reportalo.
- Nombre en pantalla: "SPP / el Planificador", nunca "OptiFierro".
- Estado base verificado hoy: HEAD `c818ff6`, contenedores desplegados con codigo identico (MD5).

## NO HAGAS (comun)
No agregues funcionalidades, no refactorices por gusto, no cambies estilos fuera de lo pedido, no toques manuales
salvo que tu tarea lo indique, no borres datos, no modifiques `docker-compose.yml` ni `.env`.
