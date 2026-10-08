
---
# TAREA CCa-33 — F9: version del backend + recarga automatica del front + cabeceras de cache
TAG de worktree/rama: `f9` (rama `ola1-f9`, directorio `optifierro_f9`). Informe: `CCa33_f9_version_cache_20261005.md`.

## Citas literales de Montu
- "me quedo con 'que el front consulte la version del backend y se recargue solo'".
- "Me gustaria que esto sea practicamente automatico, o sea, que cuando se refresque, se refresque sin cache ... para que refleje 100% la informacion" (los usuarios normales no saben hacer "refresco profundo").
- "yo pedi que el logueo para este sistema sea cada 8 horas. Me gustaria mantenerlo."

## Hechos del diagnostico (CCa-30, D5)
- nginx de `optifierro-frontend` (`/etc/nginx/conf.d/default.conf`) NO emite `Cache-Control`/`expires`: ni `index.html`
  ni `/assets/*` (con hash de Vite). `GET /api/health` (`main.py:806-808`) no trae version. No hay `VITE_*`/`__BUILD*`.

## Que hacer
1. Backend: `GET /api/version` SIN autenticacion, respuesta pequena `{"build_id": str, "commit": str, "started_at": ISO}`.
   `build_id`: ve como obtener un identificador que cambie en cada despliegue SIN requerir cambios en docker-compose:
   por ejemplo un archivo `BUILD_ID` generado en el build de imagen, y como respaldo la hora de arranque del proceso.
   Elige lo mas simple y robusto, explicalo en el informe. No cambies `/api/health`.
2. Frontend: un hook/componente pequeno (nuevo archivo) que consulta `/api/version` al cargar, cada 60 s y al volver
   el foco a la pestana. Si `build_id` o `started_at` difiere del primero que vio: mostrar un aviso breve
   ("Nueva version del SPP disponible; recargando en 10 s") y recargar con `location.reload()` — sin interrumpir si hay
   un arrastre (drag&drop) o un modal de edicion abierto: en ese caso esperar a que se cierre. Falla silenciosa si la
   consulta falla (no recargar por errores de red). Montalo una sola vez en el layout raiz.
3. nginx (archivo de config del frontend en el repo; ubicalo): `index.html` y `/` con `Cache-Control: no-cache`
   (revalida siempre); `/assets/` con `Cache-Control: public, max-age=31536000, immutable`; `/api/` con
   `Cache-Control: no-store`. Cuida el comportamiento de `add_header` dentro de `location` (no heredado).
   Valida la sintaxis con un contenedor efimero: `docker run --rm --entrypoint nginx -v <conf>:/etc/nginx/conf.d/default.conf optifierro-frontend -t`
   (permitido solo para esto).
4. Tests: backend (`/api/version` responde y no exige sesion). Frontend: `npx tsc --noEmit`.

## Archivos permitidos
`backend/main.py` (solo agregar el endpoint, sin tocar el resto), un router/archivo nuevo si prefieres, config nginx
del frontend, `frontend/src/` (hook nuevo + una linea de montaje en el layout), tests nuevos.

## NO HAGAS (especifico)
No toques `backend/routers/auth.py` ni la logica de sesion de 8 h. No agregues validacion de sesion a endpoints
existentes (hallazgo de seguridad: solo reportalo en el informe, sin cambiarlo). No toques `programacion.py`,
`motor_v2.py` ni `GestorProgramacion.tsx`. No hagas `docker build`.
