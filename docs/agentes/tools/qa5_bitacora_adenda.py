from datetime import datetime
import shutil, re
base = "/Users/montu/MontuMS/docs/"
b = base + "bitacora_accesos_torres_ocaranza.md"
shutil.copy(b, b + ".bak_pre_adenda_tarde_20261005")
s = open(b, encoding="utf-8").read()
assert "## 2026-10-05 (tarde)" not in s
entrada = """

---

## 2026-10-05 (tarde) — Ola 1 del QA SPP: CCa-33/34/35/36 + trabajo directo de Miaude en TO (INCLUYE escrituras en worktrees y copia de archivos sensibles)

**Campos comunes:** Sistema = TO / PROMETHEUS-AI-CORE (192.168.1.65). El checkout principal `optifierro` NO se modificó (HEAD `c818ff6`, verificado sin cambios en archivos trackeados a las ≈12:08 y ≈13:07). Se crearon worktrees en `C:/Users/OptiFierro/Desktop/`: `optifierro_f9`, `_f5`, `_f8`, `_f4` (este último sin commits: CCa-36 no corrió) y `_int`. Excepción PTS §5: no se declara. Sensibilidad: MEDIA (hay escrituras en worktrees y copias de credenciales y de datos personales). Sin push, sin merge a `master`/`cajita-viaje-deploy`, sin `docker build/up/restart`, sin escrituras a Cubigest ni a la base de datos de producción. **Corrección de la entrada anterior de este mismo día:** su frase "sin escrituras a TO" corresponde solo a los accesos de las 11:31–11:39, no al resto del día.

1. **Miaude, 12:12 — lanzamiento de CCa-33, CCa-34, CCa-35 y CCa-36** (prompts en `docs/agentes/prompts/`; cada uno crea su propio worktree y rama `ola1-<tag>` desde `c818ff6`). Informes: `docs/agentes/CCa33_f9_version_cache_20261005.md`, `CCa34_f5_vista_semanal_cuadro_20261005.md`, `CCa35_f8_ribetes_20261005.md`. **CCa-36: no ejecutó** (la cuenta de CCa alcanzó su límite de sesión, log `sesion_20261005_121157_cca36_f4.log`); sin accesos.
2. **CCa-34 (según su informe):** consulta de solo lectura al portal Cubigest (`CuadroProgramacionPr.aspx`, mismo mecanismo que el sync existente) para Coronel; no ejecutó `sincronizar_resumen_semanal` de punta a punta contra producción. **CCa-35:** además de su worktree, modificó `MANUAL_USUARIO_SPP.md` y `GUIA_RAPIDA_JEFE_PLANTA.md` en `MontuMS/docs/entrega/v2/` (según su informe). Detalle de comandos de cada CCa: ver sus informes (autoreporte, sin evidencia objetiva adicional).
3. **Miaude ≈12:50–14:00 (lectura + escritura en worktree `_int`):** `git worktree add optifierro_int -b ola1-int c818ff6`; merges de `ola1-f9`, `ola1-f5`, `ola1-f8`; commits locales en `ola1-int` (`db67895`, `08f6513`, `1fde992`; ver `git log`); archivos nuevos/modificados en ese worktree (`cargos.py`, `routers/operadores.py`, `routers/programacion.py`, `routers/jornada.py`, `main.py`, `test_f4_operadores.py`); ejecución de tests con `python -m unittest` en el host TO y `npx tsc --noEmit`.
4. **Miaude, lecturas contra el sistema en producción (solo lectura):** `GET /api/programacion/semanal` y `GET /api/programacion` (sucursales 1, 10, 14) vía `docker exec optifierro-backend python` contra `localhost`; lectura SQLite en modo `mode=ro` de `optifierro_v2.db`; `GET http://geovictoria_api:8002/asistencia/operadores_presentes/14` desde el contenedor backend (**datos personales**: nombre, RUT, cargo y hora de ingreso; impresos en la sesión de chat).
5. **Miaude ≈13:20 — COPIA DE CREDENCIALES Y DATOS DE PRODUCCIÓN a un worktree:** `.env` del checkout principal → `optifierro_int/backend/.env` (contiene credenciales; ignorado por git) y `optifierro_v2.db` (≈49 MB) → `optifierro_int/backend/`, para ejecutar tests. **PENDIENTE de eliminación** al momento de escribir esta entrada.
6. **Miaude ≈13:30 — COPIA de asistencia Geovictoria:** `docker cp geovictoria_api:/app/asistencia.db` → `C:/Users/OptiFierro/AppData/Local/Temp/gv_qa5.db` (nombres y RUT). Se usó en modo lectura para generar el listado de candidatos a baja. **PENDIENTE de eliminación.**
7. **Miaude — junction `node_modules`** en `optifierro_int/frontend` (`mklink /J` hacia el `node_modules` del checkout principal, solo para `tsc`). **PENDIENTE de eliminación** (con `rmdir`, sin borrar el contenido destino).
8. **Resultado de la lectura 6:** listado de 70 filas (cruce matriz de operadores vs Geovictoria 30 días) guardado en `docs/agentes/QA5_bajas_candidatas_20261005.csv` (contiene nombres de colaboradores; los acentos salieron corruptos por codificación cp1252; se regenerará en UTF-8). **No se aplicó ninguna baja.**
9. **≈16:50 — TO deja de responder** (ping 100% de pérdida, entrada ARP incompleta; el gateway 192.168.1.1 y serverX 192.168.1.111 sí responden). No fue posible completar la limpieza de los puntos 5–7 ni verificar el estado de los contenedores. Causa: NO VERIFICADA.
"""
open(b, "w", encoding="utf-8").write(s.rstrip("\n") + entrada)
# CSV de bajas candidatas
t = open("/tmp/qa5_bajas_out.txt", encoding="utf-8", errors="replace").read()
body = t.split("=====CSV", 1)[1].split("=====FIN", 1)[0].strip() + "\n"
open(base + "agentes/QA5_bajas_candidatas_20261005.csv", "w", encoding="utf-8").write(body)
print("OK", len(body.splitlines()), "lineas csv")
