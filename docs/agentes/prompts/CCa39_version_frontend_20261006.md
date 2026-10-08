
---
# TAREA CCa-39 — VersionWatcher: detectar tambien despliegues de SOLO frontend (no urgente, en paralelo)
TAG: `f9b` (rama `fix-version-frontend`, directorio `optifierro_f9b`). Informe: `CCa39_version_frontend_20261006.md`.
Repo: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>". Worktree desde el HEAD actual. Sin build/deploy
(lo hace Miaude). Commits locales, sin push.

## Contexto
Ayer (05-10) se corrigio un bug con un rebuild SOLO del frontend (commit `46f91fa`); `VersionWatcher.tsx` (F9) solo
compara la version del BACKEND (`/api/version`), asi que ese despliegue no disparo la recarga automatica: los
usuarios con una pestana abierta tuvieron que hacer F5 manualmente. Esto se va a repetir cada vez que haya un fix
de solo-frontend.

## Que hacer
1. Diseno propuesto por Miaude (ajustalo si encuentras algo mejor, pero no agregues un endpoint nuevo si se puede
   evitar): el propio HTML servido en `/` ya cambia su referencia al bundle con hash cuando se rebuildea el
   frontend (ej. `assets/index-CGldLSg4.js` -> `assets/index--lYF-0dZ.js`, Vite). `VersionWatcher` puede, en el
   mismo poll de 60s / foco de pestana que ya hace, hacer un `fetch('/', {cache:'no-store'})`, extraer el/los
   `src` de `<script type="module" src="...">` del HTML (regex simple sobre el texto, sin parsear DOM completo
   para no ejecutar nada), y comparar contra el que esta cargado ahora mismo (se puede leer del propio DOM del
   documento actual: `document.querySelector('script[type="module"]')?.src`). Si difiere -> mismo flujo de aviso
   y recarga que ya existe para el cambio de backend (reusa el estado/temporizador existente, no dupliques logica).
2. Mantener la comparacion de backend tal cual esta (ambas señales, backend O frontend, disparan el mismo aviso).
3. Cuidado: el fetch de `/` pasa por nginx; no debe interferir con el `Cache-Control: no-cache` ya configurado para
   `index.html` (F9 de ayer) — confirma que efectivamente nunca se sirve cacheado.
4. Test: con un mock del fetch de `/` devolviendo HTML con un hash de bundle distinto al actual, el componente debe
   disparar el mismo flujo de aviso/recarga (reusa el arnes de test que ya haya, si CCa-33 dejo uno).
5. `npx tsc --noEmit` limpio.

## Archivos permitidos
`frontend/src/components/VersionWatcher.tsx` unicamente (y su test si existe un archivo de test asociado).

## NO HAGAS
No toques el backend ni `/api/version`. No agregues un endpoint nuevo salvo que concluyas, con una razon concreta
en el informe, que la comparacion de HTML no es viable (en cuyo caso DETENTE y repórtalo en vez de improvisar algo
mas invasivo). No toques otros componentes.
