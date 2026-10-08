# CCa-33 — F9: version del backend + recarga automática del front + cabeceras de cache

Fecha: 2026-10-05
Worktree: `C:/Users/OptiFierro/Desktop/optifierro_f9` (rama `ola1-f9`, base `c818ff6` de `cajita-viaje-deploy`)
Checkout principal: NO tocado.

## Qué se hizo

### 1. Backend — `GET /api/version` (commit `879f13e`)
Archivo: `backend/main.py`. Agregado antes de `/api/health`, sin tocar nada más del archivo salvo el import de
`timezone` (ya estaba `date, datetime`) y dos líneas junto a `BASE_DIR` para capturar `_STARTED_AT` y
`_BUILD_INFO_PATH`.

Respuesta: `{"build_id": str, "commit": str, "started_at": ISO}`. Sin autenticación (no hay `Depends` de sesión en
ningún router de este backend — ver hallazgo de seguridad abajo, ya reportado en CCa-30).

**Cómo se obtiene `build_id`** (decisión tomada, explicada por la tarea): el backend YA genera
`backend/BUILD_INFO.json` en cada build de imagen (`backend/Dockerfile`, línea con `RUN echo ... BUILD_INFO.json`),
con `commit` (via `--build-arg GIT_COMMIT`, hoy en `"unknown"` porque `docker-compose.yml` no pasa ese build-arg —
no lo cambié, no estaba en el alcance) y `built_at` (timestamp real del build, siempre cambia, no depende de que
se pase el build-arg). Reutilicé ese mismo archivo (mismo patrón que `backend/routers/admin.py:_leer_build_info`,
ya usado por `/api/admin/sistema/estado`) y uso `built_at` como `build_id`: cambia en cada `docker compose build`
sin que haga falta tocar `docker-compose.yml`. Si el archivo no existe o no se puede leer (caso de este worktree,
sin build de imagen), cae a `started_at` (hora de arranque del proceso) — sigue sirviendo para detectar un
reinicio del contenedor, aunque no distingue dos reinicios de la misma imagen sin rebuild.

No toqué `/api/health` ni `backend/routers/auth.py`.

**Hallazgo de seguridad (solo reporto, no lo arreglé — fuera de alcance de esta tarea):** ningún endpoint de este
backend usa `Depends` para exigir sesión/token — confirmado al revisar `routers/jornada.py`,
`routers/compromisos_semanales.py` y el router nuevo. Ya estaba documentado en CCa-30 (D5); `/api/version` hereda
el mismo estado, consistente con pedir que sea público.

### 2. Frontend — `VersionWatcher` (commit `dc14f8f`)
Archivo nuevo: `frontend/src/components/VersionWatcher.tsx`. Montado UNA sola vez en `frontend/src/main.tsx`
(root real, antes de `<App/>`), así cubre tanto `LoginScreen` como el layout autenticado sin duplicar el mount
point ni tocar la lógica de `App.tsx`.

- Consulta `/api/version` al montar, cada 60 s (`setInterval`) y al volver el foco (`window focus` +
  `visibilitychange`).
- Guarda el primer `{build_id, started_at}` visto; si alguno de los dos cambia en una consulta posterior, entra en
  modo "esperando ventana ocupada".
- Detección de "no interrumpir" genérica (no toqué `GestorProgramacion.tsx` ni `CompromisosSemanales.tsx`, que son
  los únicos con drag&drop real vía HTML5 `draggable`/`onDragStart`/`onDragEnd`):
  - Arrastre: listeners globales a nivel `document` de `dragstart`/`dragend`/`drop` (eventos nativos que burbujean
    desde cualquier elemento `draggable`), marcan `document.body.dataset.dragging`.
  - Modal abierto: `document.querySelector('.fixed.inset-0')` — convención ya usada en todo el repo para overlays
    de modal (los dos modales del propio `App.tsx`, `CalendarioFuturo`, `CompromisosSemanales`, `GestorAverias`,
    `GestorMatPrima`, `GestorProgramacion` usan literalmente las clases Tailwind `fixed inset-0`). El banner propio
    del watcher usa `fixed bottom-4 right-4` (no `inset-0`), así que no se auto-detecta como modal.
- Una vez que no hay arrastre ni modal: muestra "Nueva versión del SPP disponible; recargando en 10 s" y hace
  `location.reload()` a los 10 s.
- Falla silenciosa: cualquier error de `fetch` (red caída, CORS, etc.) se traga y no dispara nada.
- No toqué la sesión de 8 h (`routers/auth.py` intacto, nada relacionado con el logueo).

### 3. nginx — cabeceras de cache (commit `f1a4f81`)
Archivo: `frontend/nginx.conf` (único archivo de config nginx del frontend en el repo).
- `location /` (incluye `index.html`): `Cache-Control: no-cache` (revalida siempre — así el `VersionWatcher` y
  cualquier recarga manual reciben HTML fresco sin "refresco profundo").
- `location /assets/` (JS/CSS con hash de Vite, servidos desde el mismo `root`): `Cache-Control: public,
  max-age=31536000, immutable`.
- `location /api/`: `Cache-Control: no-store` (agregado, ya existía el proxy_pass).
- Usé `add_header ... always;` en cada `location` porque `add_header` NO se hereda entre bloques `location`
  hermanos — si lo hubiera puesto solo en el `server` o en un solo `location`, los otros se habrían quedado sin
  cabecera.

Validación de sintaxis (único uso permitido de `docker run` en esta tarea):
```
docker run --rm --network optifierro-network --entrypoint nginx \
  -v C:/Users/OptiFierro/Desktop/optifierro_f9/frontend/nginx.conf:/etc/nginx/conf.d/default.conf \
  optifierro-frontend -t
```
Primera corrida sin `--network` dio `host not found in upstream "backend"` (esperable, upstream solo resuelve
dentro de la red de compose) — con `--network optifierro-network` attacheado a los contenedores ya corriendo:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

## Tests (salida real)

### Backend — `python -m unittest test_version_endpoint -v` (Python 3.11.8 del host TO, sin Docker)
```
test_build_id_cae_a_started_at_si_no_hay_build_info ... ok
test_responde_con_las_claves_esperadas ... ok
test_ruta_registrada_sin_dependencias_de_auth ... ok

Ran 3 tests in 0.000-0.001s
OK
```
No usé `TestClient(app)` con `with` porque eso dispara el `lifespan` de `main.py`, que abre `optifierro_v2.db`
(no existe en este worktree de pruebas, solo en el contenedor desplegado vía volumen). En su lugar llamo
directo a la función `main.version_check()` e inspecciono `main.app.routes` — válido porque el endpoint no
depende de `Request` ni de sesión.

### Backend — regresión en tests existentes relevantes
- `test_cajita_viaje.py` (16/16, corrido solo): **OK**, sin relación con mis cambios.
- `test_b42v2_etiquetas.py` y `test_b44b_capacidad_real.py`: fallan por `sqlite3.OperationalError: no such table`
  / `FileNotFoundError: /app/optifierro_v2.db` — **preexistente, no relacionado con esta tarea** (ambos requieren
  la base real del contenedor o una copia en `/app/`, que no existe en este worktree de prueba; no toqué
  `motor_v2.py`, `programacion.py` ni esas tablas).

### Frontend — `npx tsc --noEmit`
Sin salida (exit 0) — **OK**. Nota sobre entorno: el worktree nuevo no trae `node_modules` propio (git worktree
no lo comparte); creé una **junction temporal** (`cmd /c mklink /J node_modules ...\optifierro\frontend\node_modules`,
apuntando al checkout principal, solo lectura) para poder correr `tsc`, y la borré (`cmd /c rmdir node_modules`)
al terminar — no quedó rastro en el worktree ni se tocó el checkout principal (confirmado con `git status`
después del commit: no aparece `node_modules`, ya está en `.gitignore`).

## NO VERIFICADO
- No se probó el flujo end-to-end en navegador real (login, dejar la pestaña abierta, forzar un cambio de
  `build_id` reiniciando el backend, confirmar que el banner aparece y recarga). Las instrucciones de la tarea
  no permiten `docker compose build/up` ni reiniciar el backend desplegado; probar esto hubiera requerido tocar
  producción, fuera de alcance.
- No se probó el caso real de arrastre/modal abierto bloqueando el reload (requiere el navegador + interacción
  manual con `GestorProgramacion.tsx`, que no debía tocar).
- `commit` en `/api/version` seguirá devolviendo `"unknown"` en producción mientras `docker-compose.yml` no pase
  `--build-arg GIT_COMMIT=$(git rev-parse HEAD)` al build del backend — no es un bug de esta tarea (la tarea pide
  explícitamente no depender de cambios en `docker-compose.yml`), pero lo dejo anotado por si se quiere resolver
  en otra ventana.

## git diff --stat (c818ff6..HEAD)
```
 backend/main.py                            |  37 +++++++++-
 backend/test_version_endpoint.py           |  42 +++++++++++
 frontend/nginx.conf                        |   7 ++
 frontend/src/components/VersionWatcher.tsx | 110 +++++++++++++++++++++++++++++
 frontend/src/main.tsx                      |   2 +
 5 files changed, 197 insertions(+), 1 deletion(-)
```

Commits:
- `879f13e` feat(backend): agrega GET /api/version sin auth
- `dc14f8f` feat(frontend): agrega VersionWatcher
- `f1a4f81` fix(nginx): cabeceras de cache correctas

## Archivos compartidos — ¿se tocaron?
`backend/routers/programacion.py`, `backend/motor_v2.py`, `GestorProgramacion.tsx`: **NO tocados**, confirmado
por `git diff --stat` arriba (ni aparecen).

## Tiempo
Dentro del margen de ~45 min.
