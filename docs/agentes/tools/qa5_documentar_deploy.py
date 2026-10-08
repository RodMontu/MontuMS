import shutil
base = "/Users/montu/MontuMS/docs/"
# ---------------- LOG_CAMBIOS_2026.md (mas nuevo arriba) ----------------
lp = base + "LOG_CAMBIOS_2026.md"
shutil.copy(lp, lp + ".bak_pre_deploy_ola1_20261005")
s = open(lp, encoding="utf-8").read()
linea = "═══════════════════════════════════════════════\n"
entrada = linea + "2026-10-05 — DEPLOY Ola 1 del QA SPP: operadores por cargo, ribetes desde el Cuadro, Vista Semanal = Cuadro, recarga por versión + reparación de índices SQLite\n" + linea + """**Quién:** Miaude (coordinación, F4 y despliegue directo), CCa-33/34/35 (F9/F5/F8, informes en `docs/agentes/CCa33…CCa35_*_20261005.md`). CCa-36 no corrió (límite de sesión de CCa).

**Contexto:** QA general de Montu del 05-10-2026 (decisiones aprobadas en el chat de coordinación). Rama `ola1-int`, desplegada con avance rápido sobre `cajita-viaje-deploy`: HEAD `2550d3a` (base `c818ff6`). Respaldo previo de la BD: `backend/optifierro_v2_BACKUP_20261005_pre_ola1.db` y `backend/optifierro_v2.db.PRE_REPARACION_INDICE_20261005`.

**Qué se hizo (commits en `c818ff6..2550d3a`):**
1. **F9 — versión y caché** (`879f13e`, `dc14f8f`, `f1a4f81`): `GET /api/version` sin autenticación; `VersionWatcher.tsx` consulta al cargar, cada 60 s y al recuperar el foco, y recarga solo (aviso de 10 s) cuando cambia la versión; nginx: `index.html` sin caché, `/assets/` inmutable, `/api/` sin almacenar. La sesión de 8 h no se tocó.
2. **F5 — Vista Semanal = Cuadro de Cubigest** (`7635967`, `fa26c87`, `6c6402d`, `86aed96`, `1fde992`): módulo nuevo `cuadro_resumen.py` + tabla `cuadro_resumen_semanal` (bloques "Fierro Preparado" y "Largo Comercial" del Cuadro; una semana por consulta porque Cubigest agrega por nombre de día); Largo Comercial fuera de los totales; "Fuera de ventana" pasó a nota; sync de 3 semanas en la corrida de :00 y de la semana actual en :30.
3. **F8 — ribetes** (`9befb40`, `fbfd969`, `55b821c`): `viene_de_futuro` se calcula desde la fecha del IT en el Cuadro en todas las rutas; ribete negro segmentado (adelantado), naranja segmentado (acero ≠ A630), ambos apilados; se eliminó "inminente" y el naranja de avería; ribetes también en eventos que cruzan la colación; leyenda y manuales v2 actualizados.
4. **F4 — operador vs ayudante por cargo de Geovictoria** (`db67895`, `08f6513`, `fbf2632`, `2550d3a`): nuevo `cargos.py` (fuente única); el pool de asignación y la capacidad B16 cuentan solo operadores por cargo; máquina detenida no muestra operador; Gestor de Operadores/Maestros sin ayudantes presentes y con operadores presentes aunque no tengan máquinas autorizadas; nombre de operador resuelto por (sucursal, usuario) (colisión `curra` Cerrillos/Coronel) y el adelanto usa nombre completo.

**Verificación (05-10, ~17:40):** `/api/version` y cabeceras de caché correctas; Vista Semanal de Coronel coincide con el Cuadro de Cubigest (lun 10.468, mar 4.732, mié 96; el viernes cambió durante el día en el propio Cubigest); cajitas con IT de fecha futura en el Cuadro con flag: Calama 31/31, Cerrillos 83/83, Coronel 7/7 (antes 0/0/1); Gestor de Operadores de Coronel: Kurt, Enzo, Rafael, Damian. Tests: 17 de F4, F8 (9), resumen del Cuadro (7), versión (3), cajita (16), B16 (9) y demás suites relevantes OK; suites que ya fallaban en el checkout principal (`sync_unificado`, `averias_cubigest`, `b44b`, `gantt_etapa_gris`) siguen igual por rutas del contenedor.

**Incidente descubierto durante el deploy — BD con índices corruptos:** `PRAGMA integrity_check` desde el contenedor reportó corrupción en `idx_hist_fecha_suc` (página inválida 12075 fuera de rango, páginas "never used") y, tras reconstruirlo, `idx_hist_pit` incompleto. Los datos de `historial_asignaciones` (97.100 filas) estaban íntegros. Reparación con el backend detenido (17:35–17:37): respaldo, `DROP` del índice desde `sqlite_master` con `writable_schema`, `CREATE INDEX` desde los datos, `VACUUM` y reconstrucción de `idx_hist_pit`; `integrity_check` final = `ok`, sin pérdida de filas (historial 97.100, matriz 70, `trabajos_optisteel` 6.450, `programacion_guardada` 669). **Causa NO determinada**; hipótesis: escrituras desde un proceso del host Windows sobre una BD en modo WAL que usa el contenedor Linux (archivos `-shm`/`-wal` compartidos por bind mount). Se encontraron filas de prueba (`sucursal_id=4`, obra "Obra Test", fecha 2026-09-24, `created_at` 2026-10-01) en `historial_asignaciones` creadas por pruebas ejecutadas contra la BD real; no se borraron. Ojo: `sucursal_id=4` también tiene 35 filas legítimas antiguas en `programacion_guardada` (SANTIAGO, marzo-abril 2026).

**Pendiente:** ejecutar las pruebas SIEMPRE contra una copia de la BD (no contra `backend/optifierro_v2.db` del checkout principal); F2 (completar saldo_mh con el adelanto) sigue abierto; el plan guardado de hoy conserva las tareas asignadas antes del deploy hasta la próxima generación (20:10) o un "Reprogramar"; candidatos a baja en `docs/agentes/QA5_bajas_candidatas_20261005.csv` (sin aplicar); colisión de usuario dentro de Calama (`jcastillo`, dos personas).

"""
assert s.startswith(linea)
open(lp, "w", encoding="utf-8").write(entrada + s)

# ---------------- bitacora_accesos ----------------
bp = base + "bitacora_accesos_torres_ocaranza.md"
shutil.copy(bp, bp + ".bak_pre_deploy_ola1_20261005")
b = open(bp, encoding="utf-8").read()
bit = """

---

## 2026-10-05 (noche) — DEPLOY de la Ola 1 y reparación de la base de datos SQLite (Miaude, con autorización explícita de Montu para el deploy)

**Campos comunes:** Sistema = TO / PROMETHEUS-AI-CORE (192.168.1.65), checkout `optifierro` (`cajita-viaje-deploy`). Excepción PTS §5: no se declara. Sensibilidad: **ALTA — escrituras en producción** (código, contenedores y base de datos). Autorización: Montu, en el chat de coordinación ("vamos con el deploy!"); la reparación de la base de datos fue una acción correctiva no prevista que se informa a Montu en el mismo chat.

1. **≈17:30 — Respaldos.** `backup()` de SQLite desde el host de TO: copia inconsistente (`database disk image is malformed` al verificarla; el host Windows no comparte el `-shm` del contenedor Linux). Se reemplazó por una copia hecha **desde el contenedor** (`/tmp` → `docker cp`) = `backend/optifierro_v2_BACKUP_20261005_pre_ola1.db`; ≈17:35, con el backend detenido, copia cruda `backend/optifierro_v2.db.PRE_REPARACION_INDICE_20261005` (y `-shm.pre_rep`).
2. **≈17:31 — `git merge --ff-only ola1-int` en el checkout principal** (HEAD `c818ff6` → `fbf2632`); a las ≈17:39, segundo avance a `2550d3a`. Sin push.
3. **≈17:34 y ≈17:39 — Imágenes:** `docker compose build --no-cache backend frontend` y luego `build --no-cache backend`.
4. **17:35:27 — `docker compose stop backend`** (inicio de la ventana de indisponibilidad del SPP).
5. **17:35–17:37 — Reparación SQLite con `docker run --rm` de la imagen `optifierro-backend`** montando `backend/` como `/work` (escrituras directas a `optifierro_v2.db`): `VACUUM INTO` falló; `PRAGMA writable_schema=ON` + eliminación de la fila de `idx_hist_fecha_suc` en `sqlite_master` + `CREATE INDEX` desde los datos; `VACUUM`; `DROP INDEX`/`CREATE INDEX` de `idx_hist_pit`. Resultado: `integrity_check` = `ok`; filas verificadas: `historial_asignaciones` 97.100, `operadores_matriz` 70, `trabajos_optisteel` 6.450, `programacion_guardada` 669. No se borró ningún dato.
6. **17:36:55 — `docker compose up -d backend frontend`** (frontend recreado; fin de la indisponibilidad: ≈1,5 min). A las ≈17:39:41 `up -d backend` otra vez (≈15 s de indisponibilidad del backend).
7. **≈17:37 — Sync manual:** `sincronizar_resumen_semanal()` ejecutado una vez dentro del contenedor: consultas de solo lectura al portal Cubigest (9 combinaciones sucursal×semana, 52 s) y escritura de 54 filas en `cuadro_resumen_semanal`.
8. **Lecturas (solo lectura):** `GET /api/version`, cabeceras HTTP de `/`, `/api/health` y un asset; `GET /api/programacion/semanal`, `/api/programacion` (3 sucursales) y `/api/operadores?sucursal=14`; `PRAGMA integrity_check` de la BD desde el contenedor en vivo; revisión de logs del backend (sin errores).
9. **Graphify (Mac, ≈17:40):** `git archive 2550d3a backend frontend/src` desde TO extraído en `~/graphify-workspace/optifierro` (sobrescribe archivos de ese espacio de trabajo derivado; respaldo en `graphify-out.bak_pre_ola1_20261005`) y `graphify update .`; registro del commit sincronizado en `graphify-out/SYNC_COMMIT_TO.txt`. El alcance del grafo ahora incluye `frontend/src` (3.745 nodos; antes 1.127).
10. **Hallazgo de seguridad de proceso (autocrítica de Miaude):** durante la tarde se ejecutaron pruebas unitarias con `python -m unittest` **desde el checkout principal** (cwd `backend/` con `optifierro_v2.db` relativa = la BD real, abierta desde el host Windows mientras el contenedor la usa en modo WAL). Esto es un riesgo de corrupción y puede haber escrito en producción; la causa del daño de índices **no está determinada** (hay filas de prueba de otro día en la tabla, 2026-10-01). Regla desde ahora: las pruebas se ejecutan solo sobre una copia de la BD.
"""
open(bp, "w", encoding="utf-8").write(b.rstrip("\n") + bit)
print("OK LOG y bitacora")
