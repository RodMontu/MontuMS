═══════════════════════════════════════════════
2026-10-09 — DEPLOY CCa-43: credenciales web de Cubigest fuera del código (variables de entorno); HEAD f61b08c
═══════════════════════════════════════════════
**Quién:** CCa-43 (código, informe en el repo: `docs/agentes/CCa43_credenciales_scrapers_20261009.md`), Miaude (revisión, `.env`, deploy, push, Graphify). Motivo: preparar la entrega del código fuente del SPP al cliente sin credenciales en texto plano.

1. **Cambio.** `scraper_optisteel.py`, `scraper_cuadroprogramacion.py` y `scraper_cuadre_inet.py` dejan de llevar usuario y clave de Cubigest escritos en el código; los leen con `obtener_credenciales_web()` (nuevo `backend/cubigest_credenciales.py`) desde `CUBIGEST_WEB_USER` y `CUBIGEST_WEB_PASS`, **al llamar y no al importar** (la app arranca aunque falten; el error nombra solo las variables). `backend/.env.example` documenta ambas. Commit `f61b08c` (merge fast-forward a `cajita-viaje-deploy`, rama y worktrees temporales eliminados).
2. **Revisión de Miaude (no se aceptó el autoreporte):** diff correcto; 8 tests relevantes OK (5 nuevos + regresión Coronel); módulos importan sin variables; 0 apariciones de la clave previa en el worktree (el usuario previo solo en un snapshot de `.playwright-mcp`, en el backup de BD de marzo y en el informe de CCa: nada entregable). **Corrección al reporte de CCa:** dijo que solo `test_sync_unificado` fallaba (5 errores); la suite completa da **1 falla + 41 errores en 9 módulos, idénticos y con los mismos nombres en la base `116b3fb`** (154 tests antes, 159 ahora). Causas por tipo: 19 `no such table: maquinas_info` (worktree limpio sin BD), 14 `FileNotFoundError`, 8 `PermissionError` (bloqueo de archivos temporales en Windows). Coherente con un problema del entorno de pruebas, **NO confirmado** corriéndolas con una copia de la BD. Pendiente antes de entregar: clasificar y dejar la suite en verde o documentar cómo correrla.
3. **Deploy (OK explícito de Montu, 14:09–14:10 CL):** imágenes `-rollback:pre_cred_20261009` (backend y frontend); `backend/.env` respaldado **fuera del repo** en `C:/Users/OptiFierro/optifierro_env_backups/.env.bak_pre_cred_20261009`; las dos variables se escribieron desde el servidor leyendo el commit anterior (las 3 copias eran idénticas), sin mostrar valores, entre comillas simples; `docker compose build --no-cache backend` + `up -d --force-recreate backend` (frontend sin cambios). Build `2026-10-09T17:09:36Z`, integridad SQLite ok antes y después, sin errores en logs.
4. **Verificación:** usuario y clave dentro del contenedor **idénticos por hash** a los anteriores; login real de solo lectura contra el portal de Cubigest con las variables nuevas, sin excepción. **Primer ciclo automático (14:30 CL, verificado 14:33):** el sync del Cuadro de Programación y del resumen semanal cargó las 3 plantas (Calama 17:30:06/:25, Cerrillos 17:30:13/:32, Coronel 17:30:19/:38 UTC) usando `scraper_cuadroprogramacion` con las variables nuevas; 0 apariciones de 'Faltan credenciales' o Traceback desde el deploy. **Importación OptiSteel de las 14:45 CL (verificada 14:48): OK** con `scraper_optisteel` y las variables nuevas: Calama 1.849 filas y Cerrillos 4.231 cargadas (17:45:07 y 17:45:16 UTC), 0 'Faltan credenciales' ni Traceback. Único error: Coronel, el bug conocido de Cubigest (`DescargarOptistel.aspx` sin adjunto), sin relación con este deploy. **Deploy CCa-43 verificado de punta a punta (los 3 scrapers).**
5. **Rollback:** `docker tag optifierro-backend-rollback:pre_cred_20261009 optifierro-backend`, restaurar el `.env` desde el respaldo y `docker compose up -d --force-recreate --no-build backend`.
6. **GitHub:** `f61b08c` empujado a `origin/cajita-viaje-deploy` (verificado remoto = local).
7. **Graphify** regenerado a `f61b08c` (reset del espejo a esa rama + `graphify update .`): **1.340 nodos, 2.335 aristas, 96 comunidades**. Respaldo del grafo previo en `~/graphify-backups/graphify-out.bak_pre_cca43_20261009`. Comprobado: 0 nodos de `venv`/`.playwright-mcp`, sin respaldos dentro del workspace. Variación vs. el grafo anterior (1.212): backend +15 (helper y tests); frontend +111 **sin cambio de código frontend entre ambos commits: NO explicado** (el grafo actual sale de un checkout limpio del commit exacto).
8. **Riesgos abiertos:** (a) la clave de Cubigest sigue en el historial git del repo privado `Optifierro-V2` y CCa la mostró una vez en pantalla (puede estar en su transcripción local del Mac) → **rotar**, idealmente con una cuenta de servicio dedicada (trámite del cliente con Cubigest); (b) el usuario sigue siendo la cuenta personal de un colaborador; (c) `backend/venv/` versionado en git y basura de herramientas (ver auditoría de entrega).
9. **Entrega:** repo `RodMontu/SPP` creado (privado, vacío). Versión propuesta **v3.1.0** (último publicado por el cliente: v3.0.2 del 28-09), tag `v3.1.0` (no `v2.0.0`). Publicar en la plataforma del cliente después de este deploy.

═══════════════════════════════════════════════
2026-10-08 — DEPLOY: barrido final de etapas en el rollover (historial gris) + antigüedad de averías manuales; push a GitHub (HEAD 116b3fb)
═══════════════════════════════════════════════
**Quién:** CCa-41 (historial gris, informe `docs/agentes/CCa41_historial_gris_20261008.md`), CCa-42 (averías, informe `docs/agentes/CCa42_averias_antiguedad_20261008.md`), Miaude (revisión, integración, deploy, push).

1. **Historial gris — brecha cerrada (CCa-41).** `_ejecutar_generacion` (rollover automático 08:10/20:10, `backend/main.py`) borraba de `global_eventos` todos los eventos de la sucursal sin una pasada final. Una etapa que Cubigest confirmaba entre el último ciclo de 30 min y el rollover nunca se marcaba en `etapa_congelada`, y esa cajita quedaba sin gris para siempre en el día pasado. Fix: una llamada extra a `_job_verificar_etapas_completadas()` justo antes del borrado (dentro de try/except). Verificación en vivo previa: 0 faltantes contra Cubigest en 3 plantas × hoy y 2-3 días pasados. 4 tests nuevos (`test_historial_gris_rollover.py`). **Limitación conocida:** no cubre confirmaciones que Cubigest registre DESPUÉS del borrado (el evento ya no está en memoria); el muestreo no encontró casos. La verificación de punta a punta ocurrirá en el primer rollover tras este deploy (buscar `[etapa_congelada]` en los logs a las 08:10/20:10).
2. **Antigüedad de averías manuales (CCa-42).** `GestorAverias.tsx`: muestra "hace N días/horas" en las averías manuales activas y marca con ámbar + ícono las que superan `AVERIA_MANUAL_ANTIGUA_DIAS = 7` (valor por defecto a confirmar con Montu). La fecha de inicio ya venía en `GET /api/averias` (`timestamp`), sin cambios de backend. No cierra ni caduca nada. Propuesta no implementada: mismo indicador en la pantalla de Programación.
3. **Diagnóstico scraper Coronel (CCa-40, 07-10):** bug del propio Cubigest, ver entrada 2026-10-08 anterior.

**Deploy:** primer intento (anoche, ~00:00) no llegó a ejecutarse (las herramientas locales de Claude Desktop se colgaron; sin efecto en producción). Ejecutado hoy 06:34–06:36, antes del turno: backup de integridad (`integrity_check` = ok antes y después), `docker compose build --no-cache backend frontend` (29 s), `up -d` (≈20 s de indisponibilidad). `/api/version` nuevo build `2026-10-08T09:34:41Z`; sin errores en logs; planes de las 3 plantas restaurados desde la BD.

**Respaldo en GitHub:** rama `cajita-viaje-deploy` empujada a `origin` (RodMontu/Optifierro-V2), HEAD `116b3fb`, 43 commits sobre `origin/master` (`5072159`), sin force. `origin/master` NO se modificó (el avance rápido es posible; pendiente de decisión de Montu). Revisión previa al push: ningún archivo sensible (db/env/csv/bak) en el diff y ninguna credencial nueva; las líneas `Tx_Pass` de `scraper_optisteel.py`, `scraper_cuadroprogramacion.py` y `scraper_cuadre_inet.py` ya estaban en `origin/master` (idénticas). **Riesgo conocido, sin resolver:** esas credenciales de Cubigest están en texto plano en el repositorio y ya están en GitHub; debe pasarse a una cuenta de servicio con variables de entorno (ver `principles-and-rules`). Además `backend/venv/` está versionado en git (≈ site-packages completo), lo que infla el repo; conviene sacarlo con `git rm -r --cached` y añadirlo al `.gitignore`.

**Corrección sobre Graphify (error mío del 08-10):** el crecimiento del grafo (3.745 → 14.238 nodos) NO era real ni "estable". Cada `cp -R graphify-out graphify-out.bak_*` dejado dentro de `~/graphify-workspace/optifierro` sumaba ~4.000 nodos basura (los `manifest.json` de los respaldos entraban como nodos; 91% del grafo). Mi verificación con `--force` fue inválida: el log decía "outputs left untouched". Corregido: respaldos movidos a `~/graphify-backups/` y reconstruido: **1.212 nodos, 2.147 aristas, 86 comunidades** (grafo real, commit `116b3fb`). Los análisis de impacto previos siguen siendo válidos (los nodos basura no tenían aristas con código). **Regla:** nunca guardar respaldos dentro del workspace de Graphify.

═══════════════════════════════════════════════
2026-10-08 — Clave SQL de Cubigest expirada (renovada) + diagnostico scraper Coronel (bug de Cubigest, no nuestro)
═══════════════════════════════════════════════
**Quién:** Montu (renovación de la clave en Cubigest), Miaude (reinicio/verificación), CCa-40 (diagnóstico del scraper, informe `docs/agentes/CCa40_coronel_scraper_20261008.md`).

**Contexto:** tras una caída de la VPN de Torres Ocaranza (06 al 08-10), al reconectar se detectó que la conexión SQL directa a Cubigest fallaba con error 18487 ("la contraseña de la cuenta expiró"). Montu renovó la clave del lado de Cubigest y la dejó en el `.env`; Miaude reinició el backend y verificó con una consulta real (`SELECT 1`) y con una corrida completa de `ejecutar_importacion()` (Calama y Cerrillos cargaron bien de inmediato). Esto resuelve la sincronización de "universo"/compromisos futuros, que llevaba horas fallando en casi cada ciclo.

**Hallazgo separado, sin relación con la clave:** el scraper de detalle por etiqueta de Coronel (`scraper_optisteel.py` / `importar_optisteel.py`) seguía fallando igual después de renovar la clave. CCa-40 investigó con bisección sistemática de rangos de fecha (sin workarounds a ciegas) y confirmó: es un **bug del propio Cubigest**, específico de Coronel — el servidor no ejecuta la descarga cuando la fecha inicial del rango es desde ayer en adelante, sin importar la fecha final, y el mismo rango funciona sin problema en Calama y Cerrillos. No hay ningún desplazamiento de fecha que evite el bug sin perder el propósito (traer trabajo futuro). Se descartó con evidencia que fuera un problema de nuestro scraper (formulario, VIEWSTATE, valor de sucursal — todo idéntico a las plantas que sí funcionan). Se corrigió un docstring desactualizado y se agregó un test de regresión con un fixture HTML redactado (sin datos reales de clientes/obras). El Cuadro de Programación de Coronel (la pantalla principal) no se ve afectado — solo el detalle usado por Producción por Máquina y el camino de adelanto vía SQL directo.

**Pendiente:** escalar la evidencia (tabla de fechas en el informe de CCa-40) a quien administra Cubigest en Torres Ocaranza, para que revisen el handler de descarga de Coronel.

═══════════════════════════════════════════════
2026-10-06 — FIX URGENTES: colisión jcastillo, avería manual sin cerrar (COIL 14), gris/candado en fallback histórico, VersionWatcher frontend, 7 bajas (commit 47c72c7)
═══════════════════════════════════════════════
**Quién:** CCa-37 (jcastillo + averías, informe `docs/agentes/CCa37_urgentes_20261006.md`), CCa-38/39 (iniciaron, Miaude terminó y commiteó), Miaude (migraciones, merge, deploy).

**Contexto:** QA en vivo de Montu el 06-10 ~08:00, con jornada a carga completa en las 3 plantas (incluido adelanto). Ola previa: Ola 1 (05-10).

1. **Colisión de usuario "jcastillo" (Calama).** Causa raíz: `sincronizar_operadores_desde_gv` (`routers/admin.py`) deriva el username sin chequear colisión entre candidatos nuevos del mismo lote; dos personas con el mismo apellido paterno (Joan Ignacio Castillo Valderrama, Ayte; Joan Manuel Castillo Cisternas, Supervisor) quedaron con `Operador='jcastillo'` ambas, afectando también `PUT /api/operadores/{id}` (editaba las dos filas a la vez). Fix: desambiguación en el sync (`_desambiguar_username`). Decisión de Montu: el Supervisor conserva `jcastillo`; el Ayudante pasa a `jcastillov`. Migración `migrate_fix_jcastillo_20261006.py` ejecutada contra producción.
2. **Avería manual sin cerrar — COIL 14 (Calama).** Las 3 hipótesis del ticket (tests de ayer contaminando la BD, scheduler caído, bug de fusión) quedaron descartadas con evidencia: el sync corre cada 30 min y está al día. La causa real: una avería MANUAL de COIL 14 del 2026-03-23 nunca se cerró, y `estado_maquinas.py` no caduca la fuente manual por diseño (para que el jefe de planta la vea). Migración `migrate_levantar_coil14_20261006.py` ejecutada. Recomendación pendiente (no implementada): alertar en el frontend cuando una avería manual supere cierta antigüedad.
3. **Gris/candado no sobrevivía al fallback histórico.** Al leer un día sin eventos en memoria (p. ej. un día pasado, cayendo a `programacion_guardada`), `obtener_programacion` no reaplicaba `_marcar_etapas_congeladas` sobre el snapshot guardado — una cajita ya confirmada en Cubigest podía perder el gris al verla como historial. Fix: una llamada adicional a la función existente (`routers/programacion.py`). Gap documentado, no implementado: no existe una "vista de día completo en gris" como modo explícito — el mecanismo sigue siendo cajita por cajita.
4. **VersionWatcher no detectaba despliegues de solo-frontend** (como el fix del 05-10 de noche). Ahora compara también el bundle de Vite servido en `/` (por hash) contra el cargado en el documento, sin endpoint nuevo.
5. **7 bajas aplicadas** (regla: desaparecer del roster completo de Geovictoria, re-verificado contra el roster de HOY, no solo 30 días de asistencia): Aníbal García (Coronel), Héctor Acuña y Giovanni Acuña (Coronel, habituales de Dobladora 3/Línea Corte Coronel y Dobladora 4 respectivamente — limpiados también esos campos, que guardan NOMBRE completo, no username), Fabián Quezada, Jofran Medina, Miguel Gutiérrez, Gabriel Sepúlveda (Cerrillos). Migración `migrate_baja_desvinculados_20261006.py`. `operadores_matriz`: 70 → 63 filas.

**Proceso — Graphify no se consultó antes de estas 3 tareas** (miss de Miaude en los prompts de hoy, a diferencia del preludio de la Ola 1). Se consultó retroactivamente antes de integrar: sin colisiones de riesgo detectadas entre los archivos tocados. Regenerado tras el deploy (commit `47c72c7`): 6.801 nodos / 7.747 enlaces — **casi duplicó el conteo de ayer (3.745/4.680) sin una razón clara**; posible acumulación del workspace de Graphify entre regeneraciones sucesivas (modo "watch", no limpieza previa). Pendiente investigar antes de confiar en el conteo absoluto; las consultas de impacto por archivo (no afectadas por esto) siguen siendo confiables.

**Verificado en vivo (06-10, ~15:10):** `/api/version` responde; Calama (`sucursal_id=1`) Carro de Corte y COIL 14 operativas; operadores de Coronel = kgallegos, elara, rneira, dneira (los 7 de baja ya no aparecen); `integrity_check` = ok antes y después de las 3 migraciones.

**Pendiente:** prompt de prueba de SSH para Antigravity (agy) pendiente de que Montu confirme si pudo correrlo interactivamente (headless vía MCP quedó bloqueado); registro de hoy en La Biblioteca.
═══════════════════════════════════════════════
2026-10-05 — FIX GAN2: tras pulsar "Generar" el Gantt volvía a dibujar 1 cajita por etiqueta (commit 46f91fa)
═══════════════════════════════════════════════
**Quién:** Miaude (directo).

**Síntoma (reportado por Montu, ≈17:44):** en Coronel el Gantt mostraba 1 cajita por etiqueta (47 cajitas, tooltip "Etiqueta 19 de 29") en vez de 1 por viaje.

**Causa raíz (con evidencia):** el backend respondía bien: `GET /api/programacion` devolvía 4 eventos agrupados (`cantidad_etiquetas` 15/2/10/20, `rango_etiquetas`). La agrupación GAN2 (`_agrupar_cajitas_por_viaje`, commit `19c2148`) se aplica solo al LEER (`GET`). Pero `handleGenerar` (`GestorProgramacion.tsx`, botón "Generar") reemplaza el estado del Gantt con las tareas crudas, por etiqueta, de la respuesta de `POST /api/programacion/generar`, y no vuelve a leer. El log del backend registra un `POST /generar` de Coronel a las ≈17:43. Es un defecto latente de GAN2 desde el 29-09 (no lo causó el deploy de la Ola 1, aunque el reinicio del backend y el nuevo pool de operadores llevaron a regenerar Coronel). Los demás flujos (reprogramar, deshacer, aplicar reparto) sí releen el GET.

**Fix:** `await fetchData(true)` al final de la rama de éxito de `handleGenerar` (4 líneas, frontend). Solo se reconstruyó y reinició el frontend (el backend no se tocó, no se perdieron planes en memoria). `tsc` limpio. Verificado en el navegador de Montu tras recargar: cajitas agrupadas ("Etiquetas 8-15 de 19 — Viaje ASR-277/1"), bundle `index--lYF-0dZ.js`.

**Pendiente derivado:** el vigilante de versión (F9) solo compara la versión del BACKEND: un despliegue solo de frontend no dispara la recarga automática (las pestañas abiertas necesitan F5 esta vez). Hay que agregar un identificador de build del frontend a la comparación.

═══════════════════════════════════════════════
2026-10-05 — DEPLOY Ola 1 del QA SPP: operadores por cargo, ribetes desde el Cuadro, Vista Semanal = Cuadro, recarga por versión + reparación de índices SQLite
═══════════════════════════════════════════════
**Quién:** Miaude (coordinación, F4 y despliegue directo), CCa-33/34/35 (F9/F5/F8, informes en `docs/agentes/CCa33…CCa35_*_20261005.md`). CCa-36 no corrió (límite de sesión de CCa).

**Contexto:** QA general de Montu del 05-10-2026 (decisiones aprobadas en el chat de coordinación). Rama `ola1-int`, desplegada con avance rápido sobre `cajita-viaje-deploy`: HEAD `2550d3a` (base `c818ff6`). Respaldo previo de la BD: `backend/optifierro_v2_BACKUP_20261005_pre_ola1.db` y `backend/optifierro_v2.db.PRE_REPARACION_INDICE_20261005`.

**Qué se hizo (commits en `c818ff6..2550d3a`):**
1. **F9 — versión y caché** (`879f13e`, `dc14f8f`, `f1a4f81`): `GET /api/version` sin autenticación; `VersionWatcher.tsx` consulta al cargar, cada 60 s y al recuperar el foco, y recarga solo (aviso de 10 s) cuando cambia la versión; nginx: `index.html` sin caché, `/assets/` inmutable, `/api/` sin almacenar. La sesión de 8 h no se tocó.
2. **F5 — Vista Semanal = Cuadro de Cubigest** (`7635967`, `fa26c87`, `6c6402d`, `86aed96`, `1fde992`): módulo nuevo `cuadro_resumen.py` + tabla `cuadro_resumen_semanal` (bloques "Fierro Preparado" y "Largo Comercial" del Cuadro; una semana por consulta porque Cubigest agrega por nombre de día); Largo Comercial fuera de los totales; "Fuera de ventana" pasó a nota; sync de 3 semanas en la corrida de :00 y de la semana actual en :30.
3. **F8 — ribetes** (`9befb40`, `fbfd969`, `55b821c`): `viene_de_futuro` se calcula desde la fecha del IT en el Cuadro en todas las rutas; ribete negro segmentado (adelantado), naranja segmentado (acero ≠ A630), ambos apilados; se eliminó "inminente" y el naranja de avería; ribetes también en eventos que cruzan la colación; leyenda y manuales v2 actualizados.
4. **F4 — operador vs ayudante por cargo de Geovictoria** (`db67895`, `08f6513`, `fbf2632`, `2550d3a`): nuevo `cargos.py` (fuente única); el pool de asignación y la capacidad B16 cuentan solo operadores por cargo; máquina detenida no muestra operador; Gestor de Operadores/Maestros sin ayudantes presentes y con operadores presentes aunque no tengan máquinas autorizadas; nombre de operador resuelto por (sucursal, usuario) (colisión `curra` Cerrillos/Coronel) y el adelanto usa nombre completo.

**Verificación (05-10, ~17:40):** `/api/version` y cabeceras de caché correctas; Vista Semanal de Coronel coincide con el Cuadro de Cubigest (lun 10.468, mar 4.732, mié 96; el viernes cambió durante el día en el propio Cubigest); cajitas con IT de fecha futura en el Cuadro con flag: Calama 31/31, Cerrillos 83/83, Coronel 7/7 (antes 0/0/1); Gestor de Operadores de Coronel: Kurt, Enzo, Rafael, Damian. Tests: 17 de F4, F8 (9), resumen del Cuadro (7), versión (3), cajita (16), B16 (9) y demás suites relevantes OK; suites que ya fallaban en el checkout principal (`sync_unificado`, `averias_cubigest`, `b44b`, `gantt_etapa_gris`) siguen igual por rutas del contenedor.

**Incidente descubierto durante el deploy — BD con índices corruptos:** `PRAGMA integrity_check` desde el contenedor reportó corrupción en `idx_hist_fecha_suc` (página inválida 12075 fuera de rango, páginas "never used") y, tras reconstruirlo, `idx_hist_pit` incompleto. Los datos de `historial_asignaciones` (97.100 filas) estaban íntegros. Reparación con el backend detenido (17:35–17:37): respaldo, `DROP` del índice desde `sqlite_master` con `writable_schema`, `CREATE INDEX` desde los datos, `VACUUM` y reconstrucción de `idx_hist_pit`; `integrity_check` final = `ok`, sin pérdida de filas (historial 97.100, matriz 70, `trabajos_optisteel` 6.450, `programacion_guardada` 669). **Causa NO determinada**; hipótesis: escrituras desde un proceso del host Windows sobre una BD en modo WAL que usa el contenedor Linux (archivos `-shm`/`-wal` compartidos por bind mount). Se encontraron filas de prueba (`sucursal_id=4`, obra "Obra Test", fecha 2026-09-24, `created_at` 2026-10-01) en `historial_asignaciones` creadas por pruebas ejecutadas contra la BD real; no se borraron. Ojo: `sucursal_id=4` también tiene 35 filas legítimas antiguas en `programacion_guardada` (SANTIAGO, marzo-abril 2026).

**Pendiente:** ejecutar las pruebas SIEMPRE contra una copia de la BD (no contra `backend/optifierro_v2.db` del checkout principal); F2 (completar saldo_mh con el adelanto) sigue abierto; el plan guardado de hoy conserva las tareas asignadas antes del deploy hasta la próxima generación (20:10) o un "Reprogramar"; candidatos a baja en `docs/agentes/QA5_bajas_candidatas_20261005.csv` (sin aplicar); colisión de usuario dentro de Calama (`jcastillo`, dos personas).

═══════════════════════════════════════════════
2026-10-02 — Pecas: autonomía 100%, bloqueo técnico de SPP/OptiFierro, log de auditoría y LLM local
═══════════════════════════════════════════════
**Quién:** Miaude (directo vía Desktop Commander, sin CCa — cambio mecánico de permisos, sin
decisiones de diseño que requirieran un agente aparte).

**Contexto:** Montu decidió que Pecas (y su Claude, proyecto "Desarrollos (serverX)") pasan a ser
100% autónomos — ya no necesita avisar ni pedir autorización antes de cada desarrollo nuevo. A
cambio, se excluye explícitamente todo lo relacionado al SPP (ex OptiFierro) y se agrega una capa
de auditoría objetiva, dado que ya no hay supervisión previa por desarrollo.

**Qué se hizo:**
1. **Bloqueo técnico de SPP/OptiFierro** (`chmod o-rwx`, usuario `pecas` no pertenece a grupo `x`):
   `/home/x/stack/{Optifierro-V2,optifierro_v2,optifierro_v2_frontend,optifierro_UI_estable_backup.tar.gz}`,
   `/home/x/stack/scrap_geovictoria/optifierro_v2.db`, `/home/x/optifierro/` (completa),
   `/home/x/MontuMS/harness/optifierro/` + `aurora_task_optifferro_20260713.md`,
   `/home/x/Documents/Montu_Office_Agent/Reporte_Auditoria_OptiFierro.docx`,
   y en `/home/x/MontuMS/docs/`: `MAPA_DECISIONES_SPP.md`, `analisis_optisteel_export.md`,
   `pendientes_sistema_planificador.md`, `spec_motor_asignacion_optisteel.md`,
   `tablero_coordinacion_spp.md` (+ sus sombras `.` de macOS).
   Verificado como `pecas`: Permission denied en las 4 rutas probadas; `/srv/eta-tracking`,
   `/srv/pecas` y `/srv/op-risk` sin cambios (siguen accesibles, como ya estaba decidido).
   **Hallazgo pendiente, no resuelto hoy:** `INVENTARIO_MAESTRO.md`, `LOG_CAMBIOS_2026.md` y
   `handoff_actual.md` son docs compartidos entre proyectos y pueden mencionar SPP de pasada —
   redactarlos por completo rompería su función para el resto de los proyectos. Queda como
   exposición residual conocida, no como omisión.
2. **Documentación — `/home/x/MontuMS/docs/pecas/`** (dentro del árbol que indexa La Biblioteca),
   ACL `u:pecas:rwx` + default ACL (dueño sigue siendo `x:x`). Ahí vive `CAMBIOS_PECAS.md` y
   `bitacora_pecas.md` de Pecas, mas `ver_actividad_pecas.sh` (ver punto 3).
3. **Auditoría objetiva (auditd):** instalado (`auditd`, `audispd-plugins`), regla persistente
   `/etc/audit/rules.d/pecas.rules` (`-a always,exit -F arch=b64 -S execve -F auid=1001 -k pecas_cmds`,
   UID real de `pecas`). Captura todo execve de la sesión de `pecas` — shell interactiva y Claude
   Code por igual, al ser el mismo usuario Linux. Script de consulta:
   `/home/x/MontuMS/docs/pecas/ver_actividad_pecas.sh [YYYY-MM-DD]`.
4. **LLM local del Mac Studio expuesto a la LAN:** Ollama pasó de `localhost:11434` a `*:11434`
   (`launchctl setenv OLLAMA_HOST 0.0.0.0:11434`, persistido en LaunchAgent nuevo
   `cl.montuschi.ollama-env.plist` porque Homebrew regenera su propio plist en cada restart y
   pisa ediciones directas). Verificado `curl http://192.168.1.102:11434/api/tags` desde serverX:
   200 OK. **Riesgo abierto:** expone el puerto a toda la LAN 192.168.1.0/24, no solo a serverX;
   y comparte el cupo de un solo modelo cargado a la vez con `ccl`/`ccgemma` (contención si
   coinciden en uso).
5. **`LEEME_PECAS.md`** reescrito (v2) en `/srv/eta-tracking/` y `/srv/pecas/`: quita el paso de
   "avisar antes de un desarrollo nuevo", documenta el bloqueo de SPP, la carpeta de
   documentación, el acceso a Ollama y la existencia del log de auditoría (declarado
   explícitamente a su Claude, no oculto).
6. Grupo `docker` y shell real de `pecas` ya estaban concedidos desde el 2026-09-17 — sin cambios.

**Sin cambios de código ni de infraestructura de producción de ningún otro cliente.**

═══════════════════════════════════════════════
2026-10-01 — fix: reintento 3x en CubigestDB.connect() (SSL intermitente a Cubigest)
═══════════════════════════════════════════════
**Commit:** `c818ff6` (rama `cajita-viaje-deploy`, HEAD de esa rama a la fecha de este log).

**Contexto:** la SSL intermitente a Cubigest (documentada desde el 27-09, investigada a fondo el 30-09 — ver
entrada siguiente de este log) bloqueaba ese mismo día también la asignación real de operador para Coronel,
no solo el adelanto de trabajos.

**Qué se hizo:** `fix: reintento (3x, 1.5s) en CubigestDB.connect() - la SSL intermitente a Cubigest bloqueaba
hoy la asignación real de Coronel, no solo el adelanto` — `backend/database_cubigest.py`, 18 líneas agregadas /
6 eliminadas.

**Verificación:** NO VERIFICADO — no se encontró informe, fila de tablero ni confirmación de deploy
(build/up en TO) para este commit puntual, más allá del mensaje del propio commit.

**Informe:** no encontrado en `docs/agentes/` ni en `pendientes_sistema_planificador.md` para este commit
específico.

═══════════════════════════════════════════════
2026-10-01 — INCIDENTE: login caído por "database is locked" + fix WAL/busy_timeout y reanclaje del scheduler
═══════════════════════════════════════════════
**Commit:** `8cc136a`, `93e4a3b` (rama `cajita-viaje-deploy`).

**Contexto:** incidente del 01-10, 08:28-08:31 (hora de TO): login caído para todos los usuarios ("Unexpected
token... is not valid JSON" en el front = el backend devolvía 500 en vez de JSON). Causa: `sqlite3.OperationalError:
database is locked` — la base nunca había estado en modo WAL (modo por defecto "delete": una escritura bloquea
todo el archivo, no solo la fila). El job `_job_importar_optisteel` (cada 20 min, agregado el 30-09 — ver
entrada de ese día) escribe bastante más que los jobs previos y coincidió con el sync de universo/horario/averías
de las 08:08-08:10-08:30, saturando la base. Fuente: `pendientes_sistema_planificador.md`, fila "INCIDENTE 01-10".

**Qué se hizo:**
1. Mitigación en caliente, sin deploy, ~08:31: `PRAGMA journal_mode=WAL` aplicado directamente sobre
   `optifierro_v2.db` (persiste en el archivo, sobrevive reinicios).
2. `8cc136a` (2026-10-01 08:44:59) — `fix: reanclar job_importar_optisteel + endurecer WAL/busy_timeout tras
   lock storm 01-10`: `job_importar_optisteel` reanclado de `CronTrigger(minute=*/20)` a
   `CronTrigger(hour=0-7,9-23, minute=45)` (excluye la hora 8: el único margen real <10 min era 08:45 vs
   `tardios_dia` 08:51). Nuevo helper `backend/db_conn.py` fuerza `PRAGMA journal_mode=WAL` + `busy_timeout=5000`
   en cada conexión nueva, migrado en `main.py` e `init_db.py`; `motor_v2.py` y el resto de `routers/*.py`
   quedan fuera de alcance de este fix, documentados como deuda técnica. Nota agregada a `HARNESS.md` (TO y
   copia MontuMS) sobre verificar margen contra todos los jobs del scheduler antes de mergear cambios futuros.
3. `93e4a3b` (2026-10-01 09:30:24) — `fix: migración defensiva de columnas en trabajos_optisteel - CREATE
   TABLE IF NOT EXISTS no altera tabla ya existente, causaba fallo silencioso de todo insert desde el deploy
   de ayer` (es decir, desde el commit `04e6bbf` del 30-09, ver entrada siguiente).

**Verificación:** la mitigación en caliente quedó "sin más bloqueos en los minutos siguientes" según
`pendientes_sistema_planificador.md`. Esa misma fuente señala como pendiente real, al momento del incidente,
agregar `PRAGMA`+`busy_timeout` explícitos en el código (no solo aplicados manualmente una vez) — cubierto por
`8cc136a`. NO VERIFICADO si `8cc136a` y `93e4a3b` llegaron a desplegarse en producción (build/up) tras
commitearse, ni el resultado de la verificación de la corrida de las 08:10 del día siguiente.

**Informe:** `docs/agentes/CCa_investigacion_lock_horario_scraper_20261001.md` — **vive en el repo de TO
(agregado en el commit `8cc136a`); no está copiado en `MontuMS/docs/agentes/`**, no se encontró localmente.
`docs/pendientes_sistema_planificador.md`, fila "INCIDENTE 01-10".

═══════════════════════════════════════════════
2026-09-30 — Investigación SSL intermitente a Cubigest + migración de adelanto y Bolsa OptiSteel a scraper HTTP
═══════════════════════════════════════════════
**Commit:** `04e6bbf`, `69690ab` (rama `cajita-viaje-deploy`); decisión documentada en
`entrega/v2/MANUAL_TECNICO_SPP.md` v2.2 (30-09-2026).

**Contexto:** la conexión SQL directa a Cubigest usada por el adelanto de trabajos resultó intermitente de
verdad (confirmado: 15/15 éxitos en una prueba, 4/5 fallos silenciados en otra, misma ventana de tiempo) — no
una falla dura como se creyó por un rato durante la investigación. Se encontró además un bug real y separado:
`CubigestDB.execute_query` traga la excepción SSL y devuelve `[]`, indistinguible de "sin datos" — afecta a
los 9 consumidores de SQL directo a Cubigest, no solo al adelanto. Torres Ocaranza no interviene la
configuración TLS de su servidor (descartado por Montu). Fuente: `pendientes_sistema_planificador.md`, fila
"CUBIGEST-SQL"; `MANUAL_TECNICO_SPP.md` secciones 2.2-bis y 2.5.

**Qué se hizo:**
1. Decisión de Montu (30-09-2026): para el adelanto de trabajos específicamente, migrar la fuente de datos de
   SQL directo a `scraper_optisteel.py` + `importar_optisteel.py` (HTTP plano sobre `DescargarOptistel.aspx`,
   puerto 80, sin TLS — ya construidos pero no conectados antes de este cambio).
2. `04e6bbf` (2026-09-30 18:59:59) — `feat: migrar adelanto de trabajos y Bolsa OptiSteel de SQL directo a
   scraper HTTP`: reemplaza la fuente de `_obtener_pids_pendientes_optisteel` y
   `_obtener_pendientes_bolsa_optisteel` (`routers/programacion.py`) por la tabla local `trabajos_optisteel`,
   cargada por `importar_optisteel.py`. Extiende `trabajos_optisteel` con
   `largo`/`calidad_acero`/`nr_piezas`/`numero_etiqueta`/`total_etiquetas` (antes no se persistían). Programa
   la importación cada 20 min en el scheduler de `main.py`. No toca `motor_v2.py` ni los otros 9 consumidores
   de SQL directo a Cubigest.
3. `69690ab` (2026-09-30 19:57:38) — `fix: cerrar explícitamente la conexión sqlite en
   _piezas_optisteel_desde_trabajos (with de sqlite3.Connection no cierra, solo commitea) - causaba
   PermissionError de Windows al limpiar tests`.

**Verificación:** NO VERIFICADO en producción — no se encontró confirmación de deploy/build de estos dos
commits (a diferencia de otras entradas de este log, no hay mensaje de "push a origin/master confirmado" ni
resultado de tests citado más allá del archivo `backend/test_migracion_scraper_optisteel.py` mencionado en el
propio commit `04e6bbf`).

**Informe:** `docs/agentes/CCa_migracion_scraper_optisteel_20260930.md`, según el propio commit `04e6bbf` —
**vive en el repo de TO y no está copiado en `MontuMS/docs/agentes/`**, no se encontró localmente.
`entrega/v2/MANUAL_TECNICO_SPP.md` sección 2.2-bis.

═══════════════════════════════════════════════
2026-09-29 — fix: sesión 8h, filtro estado_maq de averías y zoom/columna sticky del Gantt
═══════════════════════════════════════════════
**Commit:** `deba479`, `12a439a`, `ee4a667` (rama `cajita-viaje-deploy`).

**Contexto:** tres fixes operativos independientes el 29-09, en paralelo al trabajo de GAN2 y del adelanto
automático (ver entradas de este log).

**Qué se hizo:**
1. `deba479` (2026-09-29 07:57:25) — `fix(gantt-zoom): callback ref en vez de useRef+efecto de deps vacías -
   el zoom nunca ensanchaba porque el div se mide antes de existir (detrás del spinner de carga)`.
2. `12a439a` (2026-09-29 10:01:46) — `fix: sesión 24h->8h (VPN cliente); averías activas filtraba por columna
   equivocada (estado, no estado_maq) dejando resueltas como activas para siempre; hipótesis de fix para zoom
   sticky en scroll largo` — toca `backend/routers/auth.py`, `backend/routers/averias.py`,
   `frontend/src/components/domain/GestorProgramacion.tsx`.
3. `ee4a667` (2026-09-29 11:23:35) — `fix(gantt-zoom): reemplazar position:sticky nativo (se rompe pasado
   cierto scroll en áreas muy anchas, confirmado en vivo) por position:relative + translateX(scrollLeft) manual
   vía scroll listener`.

**Verificación:** NO VERIFICADO — no se encontró informe ni entrada de tablero/pendientes para estos tres
commits puntuales, más allá del mensaje de cada commit.

**Informe:** no encontrado en `docs/agentes/` con fecha 29-09 para estos tres cambios puntuales.

═══════════════════════════════════════════════
2026-09-29 — DESPLEGADO: adelanto automático de trabajos (ADEL) + operador real mostrado en el Gantt
═══════════════════════════════════════════════
**Commit:** `33175ac`, `9564fca`, `d6fc4a9`, `5f1c354` (rama `cajita-viaje-deploy`).

**Contexto:** máquinas activas con tiempo ocioso antes de fin de turno quedaban sin llenar; se construye un
adelanto automático que completa esa capacidad con trabajo de días futuros del Cuadro OptiSteel. Fuente: fila
"ADEL" de `pendientes_sistema_planificador.md`.

**Qué se hizo:**
1. `33175ac` (2026-09-29 05:48:49) — `feat(motor): adelanto automático de trabajos - llena capacidad ociosa con
   días futuros del Cuadro OptiSteel (v1, sin reparto entre 2 máquinas)`: nueva `completar_con_adelanto()` en
   `motor_v2.py`, conectada solo en `_ejecutar_generacion` (corrida automática, no el botón manual). Según
   `pendientes_sistema_planificador.md`: máquinas activas con ≥30 min libres antes de fin de turno se completan
   con trabajo de día+1 a día+5; desplegado 07:39 el mismo 29-09; v1 sin chequeo de conflicto de operador entre
   máquinas; escrito directamente por Miaude (dos corridas independientes de CCa se negaron a implementarlo por
   no poder verificar el origen de la tarea); 5 tests nuevos + 21 de regresión, todo verde.
2. `9564fca` (2026-09-29 09:03:36) — `fix(motor): retry con backoff en consulta a Cubigest dentro de
   completar_con_adelanto - fallas SSL intermitentes al llamar varias veces seguidas`.
3. `d6fc4a9` (2026-09-29 10:49:25) — `feat(motor): adelanto reutiliza operador real
   (habitual+autorizado+anti-solape vía _operadores_candidatos/intervalos_operador) en vez de lógica propia;
   conectado también a Reprogramar (generar_programacion), no solo a la corrida automática`.
4. `5f1c354` (2026-09-29 10:59:30) — `feat(gantt): mostrar operador real asignado por el Motor (derivado de las
   tareas), no el habitual estático de Maestros -- ese solo de respaldo si la máquina no tiene tareas hoy`.

**Verificación:** para `33175ac`, "5 tests nuevos + 21 de regresión, todo verde" según
`pendientes_sistema_planificador.md` (fila ADEL), que marca como pendiente real "confirmar en la corrida de las
08:10 que efectivamente adelantó trabajo donde correspondía" — NO VERIFICADO si se confirmó. Para
`9564fca`/`d6fc4a9`/`5f1c354`: NO VERIFICADO — no se encontró informe ni fila de tablero con resultado de tests
más allá del mensaje de cada commit.

**Informe:** no se encontró informe dedicado en `docs/agentes/` para esta funcionalidad (nota explícita en
`pendientes_sistema_planificador.md`, fila ADEL: "informe formal de CCa no existe para esta feature, quedó
documentado solo en el commit y en el chat"). Fuente: `docs/pendientes_sistema_planificador.md`, fila ADEL.

═══════════════════════════════════════════════
2026-09-29 — DESPLEGADO: GAN2, cajita = viaje (agrupación de etiquetas en Gantt y Bolsa de Trabajo)
═══════════════════════════════════════════════
**Commit:** `19c2148` (rama aislada `cajita-viaje-deploy`, cherry-pick de `31d63a9` sobre `master` limpio,
deliberadamente sin CCa-24), más `349e27f` y `de6e582` la misma noche. NO VERIFICADO si esta rama llegó a
mergearse a `master`.

**Contexto:** decisión de Gustavo (TO) vía Montu, 29-09-2026, que revierte lo pedido antes por José Auger: la
cajita del Gantt y de la Bolsa vuelve a representar el viaje/IT completo (agrupación de etiquetas), no una
etiqueta suelta. Reemplaza las reglas GAN-01, GAN-03, GAN-04 y GAN-09 (`MAPA_DECISIONES_SPP.md` sección 3b-2,
GAN2-01..08).

**Qué se hizo:**
1. `19c2148` (fecha de commit en el log de la rama: 2026-09-28 23:02:03) — `feat(programacion): cajita=viaje,
   agrupación de etiquetas por IT+máquina (Gantt y Bolsa) - CCa-29`: nueva función `_agrupar_cajitas_por_viaje`
   en `backend/routers/programacion.py`, criterio jerárquico calidad de acero → diámetro → forma (`id_forma`) →
   largo, con degradación a "Forma n°: varios" si no comparte los 4 criterios (GAN2-01/02). La agrupación nunca
   cruza viaje/IT (GAN2-03). La carátula usa el rango de etiquetas en vez de "Etiqueta N de M" (GAN2-04); el
   detalle agrega Diámetro, Forma, Cantidad, Peso total y la lista de etiquetas del grupo (GAN2-05, revierte
   explícitamente GAN-04). El ajuste manual de duración pasa a aplicar sobre el total del grupo (GAN2-07). El
   badge de la Bolsa pasa de "N ITs" a "N cajitas" (GAN2-08). Gate `CAJITA_VIAJE_VIGENTE_DESDE=2026-09-29` en
   `backend/.env`: no retroactivo, rige desde la corrida de las 08:10 del 29-09 en adelante (GAN2-06).
2. `349e27f` (2026-09-28 23:49:14) — `fix(programacion): viene_de_futuro por grupo = any(), no solo la primera
   etiqueta (B43 tras cajita-viaje)`.
3. `de6e582` (2026-09-29 00:11:06) — `fix(gantt): ribete de adelantada a negro 4px (celeste 2px no se
   apreciaba)`.
4. Manuales (MontuMS): `a2a3a4c` (2026-09-28 23:36:20) y `05388f8` (2026-09-28 23:41:49) —
   `MANUAL_USUARIO_SPP.md` → v2.1, `GUIA_RAPIDA_JEFE_PLANTA.md`, `MANUAL_TECNICO_SPP.md` (sección 4.9 nueva),
   `CAPTURAS_PENDIENTES.md`, y copia de `agentes/CCa_cajita_viaje_20260929.md` desde el repo de TO.

**Verificación:** según `pendientes_sistema_planificador.md` (fila CCa-29 del tablero): build+recreate
backend/frontend, logs limpios, HTTP 200; 16/16 tests nuevos (`test_cajita_viaje.py`) + 5/5 regresión B42v2,
verificados independientemente por Miaude además de por CCa. La investigación en código confirmó que la alerta
de "serie ≥80% del turno" del Motor es independiente de esta agrupación y no cambia. Pendiente real, no cerrado
a esa fecha: verificación visual de Montu de la corrida del martes 08:10. NO VERIFICADO si esa verificación
visual llegó a hacerse.

**Informe:** `docs/agentes/CCa_cajita_viaje_20260929.md`, `docs/agentes/CCa_manuales_cajita_viaje_20260929.md`,
`docs/MAPA_DECISIONES_SPP.md` sección 3b-2 (GAN2-01..08).

═══════════════════════════════════════════════
2026-09-28 (mañana) — DESPLEGADO: estado efectivo unificado de máquinas (Motor + Gestor de Averías + Gantt)
═══════════════════════════════════════════════
**Commit:** `5072159` (fast-forward `f0a35fe..5072159`), push a `origin/master` confirmado.

**Contexto:** con la sincronización de Cubigest ya funcionando (13 filas el lunes 28-09), la pantalla Gestor de
Averías seguía mostrando todo operativo (Coronel: 9/0/0) mientras el Motor excluía Línea Corte Coronel y
Curvadora 2 y marcaba Dobladora 3 como semi: los contadores y la tabla "Estado de Maquinaria" leían solo el
gestor manual. Además había un desajuste de nombres ('Eura 16' vs 'EURA 16') y nombres de máquinas inactivas de
Cubigest ajenas al SPP ('Prima 12 ', etc.) contaminaban `maquinas_detenidas`.

**Qué se hizo (CCa):** módulo nuevo `backend/estado_maquinas.py` con `obtener_estado_efectivo_maquinas`
(fusión gestor manual + `averias_cubigest` + `MAQ_ACTIVA='N'`, gana la más restrictiva, nombres normalizados,
solo máquinas activas del SPP). Lo usan el Motor, `GET /api/averias/contadores`, `/estado-maquinas` y
`GET /api/averias` (una fila vigente por máquina). `GestorAverias.tsx` muestra el estado real, badge "Cubigest"
y antigüedad ("registrada hace N días"). Constante `AVERIA_CUBIGEST_CADUCIDAD_DIAS = None` (sin caducidad, decisión
de Montu: la notificación de Curvadora 2 Coronel abierta desde el 01-04 está efectivamente detenida).

**Verificación:** 73 tests OK (contenedor efímero), `tsc`/build limpios, la función real contra copia de la BD
coincide con el Motor en las 3 sucursales. En producción tras el deploy: contadores Calama 4/2/2, Cerrillos
9/0/1, Coronel 6/1/2; Coronel muestra Curvadora 2 y Línea Corte Coronel detenidas y Dobladora 3 semi. Se
observaron averías reales registradas en Cubigest a las 09:03–09:23 del 28-09 (COIL 14 M y Dobladoras en Calama,
EURA 16 en Cerrillos): ya aparecen en Averías, pero el plan de las 08:10 ya tenía cajitas asignadas a esas máquinas
(el Motor solo excluye al generar; ver pendiente de decisión en el tablero).

**Informe:** `docs/agentes/CCa_averias_estado_unificado_20260928.md`.

═══════════════════════════════════════════════
2026-09-27 (madrugada) — DESPLEGADO: fix ventana de averías (excluía notificaciones abiertas viejas) + bug de formato de fecha vs Cubigest
═══════════════════════════════════════════════
**Commit:** `f298721`, push a `origin/master` confirmado.

**Contexto:** Montu detectó con capturas reales de Cubigest que "Dobladora 3" (Coronel) figura `SEMI` desde
el 23-09 y no aparecía ni en la sección Averías ni afectaba al Gantt.

**2 bugs encontrados y corregidos (CCa, investigando el reporte de Montu):**
1. `sync_averias_cubigest()` filtraba por `FechaRegistro >= hoy-3d` — excluía notificaciones que siguen sin
   resolver pero son más viejas que la ventana. Corregido: `EstadoMaq != 'OP'` se trae SIEMPRE sin importar
   antigüedad (mismo criterio que "PRUEBAS DE TI" de CCa-9); la ventana de 3 días solo limita el histórico ya
   resuelto. Nota: `FechaSolucion` no sirve para detectar si sigue abierta — Cubigest la puebla igual a
   `FechaRegistro` incluso sin resolver (confirmado con el caso real, Id 74214).
2. **Más grave, no reportado, encontrado al verificar el fix anterior contra Cubigest en vivo**: el parámetro
   de fecha se mandaba como `YYYY-MM-DD`; la sesión SQL Server de Cubigest usa `@@LANGUAGE='Español'` (DMY),
   interpretaba el string como día=2026 → error `22007`, la query fallaba en silencio → **`averias_cubigest`
   nunca tuvo una sola fila desde el deploy de anoche**. Corregido: formato `YYYYMMDD` (sin separadores, no
   ambiguo). Esto significa que todo lo desplegado anoche (sección Averías + fusión del Motor) estuvo
   funcionalmente inactivo (sin datos que fusionar) hasta este fix.

**Verificación — PARCIAL, bloqueada por un problema externo:** el deploy (`build --no-cache && up -d
--force-recreate backend`) salió limpio, sin errores de arranque. Pero la verificación en vivo contra
Cubigest real (confirmar que el Id 74214 real se sincroniza) **no se pudo completar**: la conexión a Cubigest
falla intermitentemente con error SSL (`SSL routines::unsupported protocol`) — mismo síntoma que ya había
documentado `CCa9_ola3_averias_20260923.md` hace días, no algo introducido por este fix. Confirmado con
múltiples intentos (uno de ellos con una conexión simple exitosa, luego varios fallidos) — parece
intermitente/dependiente del momento, no permanente. El job automático (cada 30 min) va a reintentar solo;
no hace falta acción manual salvo que Montu quiera forzar una verificación cuando la conexión esté estable.

**Hallazgo operativo aparte, no resuelto ahora:** `sync_averias_cubigest` no tiene ningún registro de
error/staleness visible (a diferencia de `sync_estado` del otro job, que sí trackea `ultimo_error_ts`) — si
Cubigest falla seguido, hoy no hay forma de notarlo salvo mirando logs. Candidato a mejora futura, no
bloqueante.

**Informe completo:** `docs/agentes/CCa_fix_ventana_averias_20260927.md`.

═══════════════════════════════════════════════
2026-09-27 (madrugada) — DESPLEGADO: zoom horizontal + pan en la línea de tiempo del Gantt (B47)
═══════════════════════════════════════════════
**Commit:** `bd11c3f` (merge fast-forward `e635f6a..bd11c3f`), push a `origin/master` confirmado.

**Qué se construyó:** 4 niveles de zoom (jornada completa/media jornada/2h/1h, según duración real del turno
— no un número fijo), botones +/-, centrado automático en la hora actual al cambiar de nivel, y pan por
arrastre con el mouse cuando el zoom está activo. `getEventStyle` (posicionamiento de las cajitas en % de la
jornada) **no se tocó** — el ensanche sale gratis de ampliar en píxeles el contenedor de timeline compartido
entre el header (regla de horas) y todas las filas de máquina. La columna "Máquina/Operador" queda fija con
`position: sticky` en vez de un árbol DOM separado (evita desincronización de alturas entre filas).

**Riesgo verificado:** interacción con el drag-and-drop de cajitas (`@dnd-kit`) — resuelto excluyendo la
cajita y la columna fija del handler de pan vía atributos `data-gantt-draggable`/`data-gantt-label`.

**Limitación honesta, no oculta:** no hay Playwright ni navegador real disponible en el entorno de ejecución
de CCa — la verificación fue `tsc`/`vite build` limpios + inspección de código, no una prueba visual en vivo.
**Pendiente: que Montu haga una pasada visual real** (sensación del arrastre, suavidad del centrado al
cambiar de zoom) antes de dar el ajuste por completamente cerrado — no bloqueante para el deploy, pero sí
para el cierre fino de la UX.

Un punto menor dejado documentado por CCa: el centrado en "hora actual" se dispara en cualquier cambio de
nivel (subir o bajar), no solo al subir como decía el pedido original — ajustable si Montu prefiere que bajar
zoom no recentre.

**Verificación de deploy:** `docker compose build --no-cache frontend && up -d --force-recreate frontend` sin
errores, `GET /` responde 200. Graphify regenerado a `bd11c3f` (1143 nodos, 1888 edges).

**Informe completo:** `docs/agentes/CCa_gantt_zoom_20260926.md`.

═══════════════════════════════════════════════
2026-09-26 (noche) — DESPLEGADO: averías de Cubigest visibles en la sección Averías + el Motor las considera para excluir máquinas
═══════════════════════════════════════════════
**Commit:** `e635f6a` (merge fast-forward `0ad166a..e635f6a`), push a `origin/master` confirmado.

**Contexto:** resuelve B39 (leer averías desde Cubigest, no solo gestor manual). Montu tomó capturas reales
de `VerAverias.aspx` (Coronel/Calama/Santiago) que contradecían la conclusión de `CCa9_ola3_averias_20260923.md`
("feed de Cubigest muerto para Cerrillos/Coronel") — Miaude cruzó los IDs reales de las capturas contra la
base y encontró la causa real: **bug de join**, `NotificacionAveria.IdMaquina` se unía contra `MAQUINA.MAQ_ID`
en vez de `MAQUINA.MAQ_NRO`. El feed nunca estuvo muerto — el join nunca matcheaba nada, para ninguna planta.

**Qué se construyó (CCa, 2 vueltas, mismo día):**
- Fix del join (`database_cubigest.py`, 2 ocurrencias) — verificado en vivo cruzando los 7 IDs reales de las
  capturas de Montu contra `MAQUINA`, coincidencia exacta.
- Job nuevo cada 30 min (`main.py`) — consulta **directa** a Cubigest (sin scraper, a diferencia del Cuadro de
  Programación), persiste en tabla local `averias_cubigest`.
- `GET /api/averias` mezcla manual + Cubigest, marcado por `fuente`. Solo expone el nivel de detalle que ya
  tiene la fuente manual (Montu: "solo completando los datos que tenemos, sin más detalle salvo que el
  Cliente lo pida") — `estado_supervisor`/`fecha_supervisor`/`operador_id` quedan guardados pero no expuestos.
- **`motor_v2.py`: la fusión pasa de "Cubigest solo como fallback en vivo" a "SIEMPRE fusionado"** — decisión
  explícita de Montu que reemplaza a propósito la de CCa-9 (que había rechazado "cualquiera excluye" por el
  riesgo de notificaciones Cubigest abiertas indefinidamente — caso real "PRUEBAS DE TI"). Argumento de Montu:
  "hoy nadie usa el sistema, podemos hacer lo que necesitemos" — riesgo aceptado a propósito, documentado, no
  pasado por alto. El fallback en vivo se mantiene como red de seguridad residual (por decisión de Montu),
  disparándose solo si tanto el SQLite manual como el caché local fallan a la vez.

**Verificación:** 64/64 tests (suite completa + 5 nuevos: recorte de campos, fusión por Cubigest solo,
conflicto entre fuentes en ambos sentidos, trazabilidad de 3 fuentes), en contenedor efímero sin tocar
producción. `docker compose build --no-cache backend frontend && up -d` sin errores, `GET /api/averias` y
`GET /api/programacion` responden 200 en producción. Graphify regenerado a `e635f6a` (1134 nodos, 1871 edges).

**Informe completo:** `docs/agentes/CCa_averias_cubigest_20260926.md` (2 secciones, con la segunda vuelta).

═══════════════════════════════════════════════
2026-09-26 (noche) — DESPLEGADO: job sync horario A4 sube de 1h a 30 min; CCa-17 cerrado (sin retirar el scraper)
═══════════════════════════════════════════════
**Commit:** `0ad166a`.

**Contexto:** sesión de diseño corta sobre los 3 puntos pendientes de CCa-17. Punto #3 (blindar fallo
silencioso de `_obtener_pids_pendientes`) resultó ya resuelto, efecto colateral del fix QA-A-01 de hoy mismo
(propaga `RuntimeError` en vez de `[]`). Para los puntos #4/#6, Miaude propuso retirar
`scraper_cuadroprogramacion.py` y usar SQL directo (misma fuente que ya usa el Motor) como único origen de
verdad para ITs/Etiquetas del Cuadro de Programación. **Montu evaluó y decidió NO hacerlo**: el scraper trae
prioridad/status/observación que la consulta directa no tiene — se queda con el scraper, solo sube la
cadencia del job de sync horario de una vez por hora a **cada 30 minutos** (`CronTrigger(minute="*/30")`,
mismo intervalo que el job de `etapa_completada`).

**Desplegado y verificado:** `docker compose build --no-cache backend && up -d --force-recreate backend`, sin
errores de arranque, `GET /api/sync/estado` responde 200. Graphify resincronizado a `0ad166a` (sin cambios de
topología, era solo un valor de cron).

═══════════════════════════════════════════════
2026-09-26 (noche) — DESPLEGADO: cajita gris e inamovible por etapa confirmada en Cubigest (etapa_completada)
═══════════════════════════════════════════════
**Contexto:** requisito nuevo salido de A4 (job horario de sincronizacion) — Montu pidio que una cajita del
Gantt quede gris y NUNCA reasignable en cuanto Cubigest confirme que esa etapa especifica (etiqueta + maquina
asignada) ya se ejecuto fisicamente, como registro historico permanente de lo hecho en la jornada. Diseñado
con Miaude (granularidad a nivel etiqueta, confirmado con capturas reales de Cubigest — Cuadro de
Programacion + detalle de avance por Tag), implementado y verificado por CCa (rama `gantt-etapa-gris`),
revisado por Montu via dictado, y desplegado por Miaude.

**Commit:** `619ea32` (merge fast-forward `52568d1..619ea32`), push a `origin/master` confirmado.

**Que se construyo:**
- Tabla nueva `etapa_congelada` (`sucursal_id, etiqueta_id, nombre_maquina`), **sin fecha/turno a proposito**
  — asi sobrevive cualquier regeneracion del dia. Se confirmo con evidencia real que HAY DOS lugares que
  reemplazan `global_eventos`/`programacion_guardada` por completo (`generar_programacion` manual y
  `_ejecutar_generacion` automatico 08:10/20:10), no uno — el diseño de tabla separada esquiva el problema
  en vez de parchar cada uno.
- Job `_job_verificar_etapas_completadas` (`main.py`), **cada 30 min** (ajustado por Montu desde 15 min por
  precaucion de saturacion de Cubigest — confirmado que consulta DIRECTO a SQL Server via `cubigest_db`
  contra `PIEZA_PRODUCCION JOIN MAQUINA`, sin scraper de por medio).
- `_marcar_etapas_congeladas` reaplica el estado en cada regeneracion. Guardas 409 en `/reprogramar`: no se
  puede mover una cajita congelada ni soltar otra encima.
- Frontend (`GestorProgramacion.tsx`): estilo gris + icono candado, `useDraggable` deshabilitado, drop
  bloqueado en `handleDragEnd`. Distinto y coexiste con el `completado` verde existente (ese es a nivel de
  IT/viaje completo cerrado, cada 30 min via `_job_verificar_its_cerradas` — no se toco).

**Decisiones de Montu al revisar (confirmadas, sin cambios de diseno salvo la frecuencia):**
1. Reprogramar una etiqueta ya confirmada a otro turno/dia en la MISMA maquina: sigue gris igual — correcto.
2. Gap angosto post-reinicio del backend (compartido con B44a, preexistente): no se corrige — premisa de
   Montu es que el sistema corre 24/7 sin reinicios, no complicar el diseño por esto.
3. Reparto en paralelo (2 maquinas para la misma tarea): todo-o-nada confirmado como correcto — Cubigest no
   discrimina entre las dos, asi que ninguna se marca gris hasta que ambas se confirmen.

**Verificacion:** 7 tests nuevos (`test_gantt_etapa_gris.py`) + 23 existentes sin regresion, `tsc`/`vite build`
limpios, `docker compose build --no-cache backend frontend && up -d` sin errores de arranque, `GET
/api/programacion` responde 200 en produccion post-deploy. Graphify regenerado a `619ea32` (1104 nodos, 1818
edges).

**Informe completo:** `docs/agentes/CCa_gantt_etapa_gris_20260926.md` (con addendum de la revision de Montu).

═══════════════════════════════════════════════
2026-09-24 (noche) — Revision visual de Montu (B42 v2): confirmado sin bloqueo. Fix de formato Largo. Nueva idea backlog (zoom timeline)
═══════════════════════════════════════════════
**Contexto:** Montu revisó B42 v2 ya desplegado (capturas + dictado VisualVoice). Reporta: "quedó como lo pedí, no tengo mayores comentarios" en lo estructural. Dos puntos a verificar con evidencia real, uno idea nueva.

**1. Largo con decimales excesivos (1.9600000381469727 m) — investigado y CERRADO, NO bloqueante.**
Trazado con evidencia: `largo_a` viene de `p.largo` (Cubigest, tabla `piezas`) SIN ningún cálculo (`routers/programacion.py:1433,1566`); el Motor solo lo usa para derivar `largo_mm = round(largo_a*1000)` como clave de agrupación (`motor_v2.py:984-985`), ya con manejo explícito de este mismo artefacto de precisión (test `D1`, `test_b42v2_etiquetas.py:178-182`, con el caso literal `8.699999809265137`). **SELECT directo a Cubigest** (viaje RESA-40/1, Ø18, IdForma 102) confirma el caso exacto de Montu: id 3604416, Tag #: 66 of 81, `largo=1.9600000381469727` — idéntico a lo mostrado en pantalla. Es un artefacto de precisión float32 del propio SQL Server (columna `real`), presente en el dato crudo de Cubigest, no introducido por nuestro código. **Único cambio aplicado:** formato de presentación, de metros crudos a milímetros redondeados (`Math.round(largo_a*1000)}mm`), en tooltip y modal — commit `f430b75`.

**2. Peso 71 kg (etiqueta 66 de 81) — investigado y CERRADO, dato correcto.**
Mismo SELECT: `KgsPaquete=71.0` exacto para esa etiqueta (18 piezas, Ø18mm, ~1.96m). La duda de Montu (paquetes de ~1000 kg según Francisco Ramos) no aplica a este caso — son paquetes pequeños de esta IT en particular; el campo se extrae directo (`ROUND(dp.KgsPaquete,1) AS kgs`), sin cálculo adicional.

**3. "Código Etiqueta: FCalc FCalc FCalc..." — NO reproducido, no hay campo así en el modal.**
El modal (`GestorProgramacion.tsx` ~1841-1866) solo tiene 6 campos: Diámetro, Largo, IdForma, Cantidad, Paquete, Peso — ningún "Código Etiqueta". Sin match de "FCalc" en todo el repo (backend + frontend). El SELECT real muestra `dp.Etiqueta = ' Tag #:  66  of  81'`, consistente con lo ya mostrado correctamente en el header ("ETIQUETA: 66 DE 81") y en el tooltip ("Etiqueta 5 de 81", ver imagen 4 de Montu). Hipótesis de la Coordinadora: artefacto del dictado VisualVoice (la misma transcripción tiene corridas repetidas de "es que" ~50 veces y "las" ~150 veces sin que Montu las dijera esa cantidad de veces) — **pendiente de que Montu confirme si lo vio realmente en pantalla o fue un glitch de transcripción.**

**4. Tooltip al pasar el mouse — YA muestra la etiqueta correctamente, sin acción.**
Montu dudaba (imagen muy pequeña para leerla bien); la imagen 4 que adjuntó de hecho muestra "Etiqueta 5 de 81 — Ø18 — Viaje RESA-40/1" con claridad. Confirmado, sin cambios.

**5. Idea nueva (NO bloqueante, no estaba en el plan original): zoom horizontal de la línea de tiempo del Gantt.**
Al acercar el zoom, aumenta la distancia entre horas y por ende el ancho de las cajitas — soluciona el caso de cajitas muy angostas e ilegibles con muchas etiquetas por turno (350-500 cajitas observadas). Registrada en `pendientes_sistema_planificador.md` como B47, post-entrega.

**Deploy:** solo frontend (`docker compose build/up frontend`), commit `f430b75`, push OK. Reversión: `optifierro-frontend-rollback:pre_largomm_20260924`. Sin cambios de backend, DB ni Cubigest en esta entrada.
