# Verificación del Manual Técnico v2.0 — SPP

**Fecha:** 2026-09-28. Redactado de forma autónoma bajo la Metodología Sinérgica (ventana overnight); Montu
revisa al despertar. Método: cada afirmación clave del Manual Técnico y la Ficha Técnica se contrasta contra
código real leído en `ssh TO`, consultas de solo lectura en vivo (`docker compose ps`, `docker exec ... pip
freeze`, `SELECT sqlite_master`), o documentos de análisis de Montu en `MontuMS/docs/`. Nada se afirmó sin una
de estas tres fuentes; donde no se pudo verificar, se marcó `POR CONFIRMAR` en los documentos correspondientes.

---

## 1. Tabla de trazabilidad — afirmaciones clave

| # | Afirmación | Fuente | Estado |
|---|---|---|---|
| 1 | Puerto host backend = 8001, frontend = 3001, ollama = 11434 | `docker compose ps` en vivo, TO, 2026-09-28 | Verificado en vivo |
| 2 | `docker-compose.yml` no declara bloque `ports:` explícito | Lectura íntegra de `docker-compose.yml` | Verificado en código |
| 3 | Python 3.11.15, FastAPI 0.141.1, Uvicorn 0.54.0, pyodbc 5.3.0, pandas 3.0.6, etc. | `docker exec optifierro-backend pip freeze` / `python --version` en vivo | Verificado en vivo |
| 4 | Nginx 1.28.3 | `docker exec optifierro-frontend nginx -v` en vivo | Verificado en vivo |
| 5 | Solo `apscheduler==3.10.4` y `holidays==0.46` están pinneados en requirements.txt | Lectura íntegra de `backend/requirements.txt` | Verificado en código |
| 6 | 33 tablas de datos en `optifierro_v2.db` (listado completo, sección 3 del Manual) | `SELECT name FROM sqlite_master` ejecutado en vivo dentro de `optifierro-backend`, TO, 2026-09-28 (re-verificado en auditoría 28-09: el conteo real es 34 filas `type='table'` incluyendo `sqlite_sequence`, es decir 33 tablas de datos; el "31" original era un error aritmético del proceso 2, no del listado) | Verificado en vivo, base real de producción |
| 7 | `_BODSUC_MAP` de `motor_v2.py` = `{1:2, 10:1, 14:3}`, prohibido modificar | `HARNESS.md` FP-002; confirmado indirectamente en `database_cubigest.py:_ADQORD_SUCCOD_MAP` idéntico | Verificado en código (`HARNESS.md`); `motor_v2.py` no se leyó completo, ver Limitación 1 abajo |
| 8 | `motor_v2.py` usa Cerrillos=4, resto del sistema usa Cerrillos=10 | `HARNESS.md` FP-006; `CLAUDE.md` de Graphify workspace; `database_cubigest.py:112` (`_CUB_TO_SQL_SUC = {1:1, 4:10, 14:14}`) | Verificado en código (2 fuentes independientes que coinciden) |
| 9 | `EstExi1.BodCod` usa mapa de "bodega" distinto (Coronel=801, no 3) | `database_cubigest.py:494-495`, comentario explícito en el código | Verificado en código |
| 10 | Join de averías por `MAQ_NRO`, bug histórico usaba `MAQ_ID` | `database_cubigest.py::obtener_estado_maquinas` (usa `MAQ_NRO`); `tablero_coordinacion_spp.md` fila CCa-20 (relato del bug y fix) | Verificado en código + verificado en documento de cierre |
| 11 | Fechas hacia Cubigest deben ir en `YYYYMMDD`, no `YYYY-MM-DD` (sesión `@@LANGUAGE='Español'`) | `tablero_coordinacion_spp.md` fila CCa-22 (commit `f298721`) | Verificado en documento de cierre, respaldado por commit real citado en `git log` |
| 12 | `execute_query` de Cubigest devuelve `[]` ante cualquier excepción (conexión, sintaxis, tipo de dato) | `database_cubigest.py:88-105`, bloque `try/except Exception` que retorna `[]` | Verificado en código |
| 13 | `openssl_legacy.cnf` se fuerza en `main.py` y en `database_cubigest.py` de forma independiente, antes de importar `pyodbc` | `backend/main.py:1-6`; `backend/database_cubigest.py:1-14` | Verificado en código |
| 14 | Scheduler: 8 jobs fijos + 1 condicional (`job_sync_horario`, depende de `SYNC_HORARIO_ACTIVO`) | Lectura íntegra de `backend/main.py` (líneas 564-645) | Verificado en código |
| 15 | `SYNC_HORARIO_ACTIVO=1` en producción hoy (job activo) | `grep` de nombres de variable en `.env` no revela valores; **el valor `1` se infiere del comentario de `tablero_coordinacion_spp.md`** ("Job horario ENCENDIDO 26-09"), no de una lectura directa del valor de la variable (por regla de seguridad, no se leyó el valor de `.env`) | Verificado por documento de cierre, no por lectura directa del valor (correcto por regla de no exponer secretos, pero calidad de evidencia distinta) |
| 16 | `_ejecutar_generacion` reemplaza completamente el plan guardado de sucursal+turno+fecha; v1 afirmaba que respetaba movimientos manuales | Lectura íntegra de `backend/main.py:143-241` | **Verificado en código — v1 era FALSO en este punto** |
| 17 | Único guardrail existente es el guard contra plan vacío (0 tareas no pisa plan con tareas) | `backend/main.py:180-197` | Verificado en código |
| 18 | Bloque de reparto en paralelo: estado del fix de solape de operador y tope de jornada | `backend/motor_v2.py` (`_asignar_bloque`, líneas ~1195-1330), en vivo, 28-09-2026; `git log` TO (commits `0a959e8`, `313d089`) | **Corregido en auditoría 28-09**: el fix SÍ está implementado desde el 14/24-09-2026 — `HARNESS.md` FAILURE_LOG estaba desactualizado; ver Manual Técnico sección 4.8 |
| 19 | Endpoints por router (listado completo, sección 6 del Manual) | `grep` en vivo de decoradores `@router.*` y `APIRouter(prefix=...)` sobre los 14 archivos de `backend/routers/`, TO, 2026-09-28 | Verificado en vivo/código |
| 20 | Procedimiento real de deploy usa `--no-cache` + `--force-recreate`, distinto del `DEPLOY_TO.md` corto | `tablero_coordinacion_spp.md`, sección "DEPLOY 25-09"; `HARNESS.md` FP-004; `DEPLOY_TO.md` (contraste) | Verificado por documento de cierre + regla explícita de HARNESS.md |
| 21 | No se evidencia respaldo automatizado de `optifierro_v2.db`; solo copias manuales puntuales | Búsqueda de "backup"/"respaldo" en repo TO (`find`) y en `MontuMS/docs/`; intento de listar tareas programadas de Windows vía `ssh TO powershell Get-ScheduledTask` | **No concluyente al 100%** — ver Limitación 2 abajo |
| 22 | Ollama corre local (contenedor `optifierro-ollama`), no hay llamadas a IA en la nube en el backend | `docker compose ps` en vivo (contenedor visible); no se hizo un `grep` exhaustivo de todo el código backend buscando URLs de proveedores cloud de IA | Verificado en vivo (existencia del contenedor); ausencia de llamadas cloud no verificada exhaustivamente — ver Limitación 3 |
| 23 | Graphify construido sobre commit `f2987219` (= `f298721` corto), un commit de código detrás del `HEAD` real `f0a35fe` (que es solo un commit de documentación) | `GRAPH_REPORT.md` sección "Graph Freshness"; `git log` en vivo de TO | Verificado (comparación directa de hashes) |
| 24 | Git status de TO: `AGENTS.md`/`HARNESS.md` modificados sin commitear; lista de untracked; ramas locales | `git status` / `git branch -a` en vivo, TO, 2026-09-28 | Verificado en vivo |

---

## 2. Limitaciones de esta verificación (léase antes de asumir cobertura total)

1. **`motor_v2.py` no se leyó íntegro.** Es el archivo más crítico del sistema (advertencia explícita de
   `HARNESS.md` FP-007: "no modificar sin correr tests de integración primero"), pero por volumen y por el
   alcance de esta tarea (documentación, no auditoría de código completa) solo se verificaron los fragmentos
   citados por `MAPA_DECISIONES_SPP.md` y por `HARNESS.md`. **No se pudo confirmar directamente en el código si
   el fix de auto-reparto (solape de operador + tope de jornada, hallazgo #18) ya fue implementado** — el Manual
   Técnico lo documenta como pendiente basándose en `HARNESS.md`, pero esto podría estar desactualizado si se
   corrigió después del 14-09 sin actualizar ese documento. **Recomendación para Montu:** confirmar el estado
   real de este punto antes de considerarlo cerrado o abierto en la próxima capacitación.
2. **La ausencia de respaldo automatizado no se pudo confirmar al 100%.** El intento de listar tareas
   programadas de Windows vía `powershell Get-ScheduledTask` a través de SSH falló por un error de parseo del
   bloque de script en el shell remoto (no un error de permisos) — no se pudo enumerar exhaustivamente todas las
   tareas programadas del host. La conclusión "no se evidencia respaldo automatizado" se basa en: (a) ausencia de
   cualquier script de backup en el repositorio de TO, (b) ausencia de mención en `HARNESS.md`/`AGENTS.md`/docs
   de `MontuMS`, y (c) presencia de solo copias manuales puntuales (nombres de archivo con fecha y motivo del
   `_pre_algo`, consistente con "alguien copió el archivo a mano antes de un cambio riesgoso"). Es una inferencia
   fuerte, no una confirmación directa de que no existe ninguna tarea de Windows fuera del repo.
3. **No se hizo una búsqueda exhaustiva de URLs de proveedores de IA en la nube en todo el backend** — la
   afirmación de "sin uso de IA cloud en runtime" se apoya en que el único cliente de IA visible en
   `requirements.txt`/imports revisados es hacia Ollama local; no se garantiza que no exista una llamada aislada
   en algún archivo no revisado.
4. **No se probó en un navegador ninguna pantalla del frontend.** Esta tarea es de documentación técnica de
   backend/infraestructura; la validación de UI corresponde al Manual de Usuario (proceso paralelo) y a QA
   funcional, no a este documento.
5. **El valor real de `SYNC_HORARIO_ACTIVO` no se leyó directamente** (correcto por la regla de nunca volcar
   valores de `.env`), se infirió de un documento de cierre de tarea. Si alguien cambió esa variable después del
   26-09 sin dejar constancia en `tablero_coordinacion_spp.md`, el Manual Técnico podría estar desactualizado en
   ese punto puntual — es fácilmente re-verificable en vivo con `GET /api/admin/scheduler/estado` sin exponer el
   `.env`.

---

## 3. Todo lo de v1 que era falso, incompleto o sin respaldo — y su corrección

| # | Problema en v1 | Corrección en v2 |
|---|---|---|
| 1 | **Falso.** Afirmaba (implícitamente, al no aclarar lo contrario) que la corrida automática de las 20:10 respeta movimientos manuales del Gantt | **Corregido:** sección 4.7 del Manual Técnico documenta, con cita de código, que `_ejecutar_generacion` reemplaza el plan completo de sucursal+turno+fecha, con la única salvaguarda del guard contra plan vacío |
| 2 | **Incompleto.** Listaba 11 tablas SQLite | **Corregido:** inventario completo de 33 tablas, extraído en vivo de la base real de producción (sección 3 del Manual Técnico) |
| 3 | **Incompleto.** Listaba 7 jobs del scheduler, omitiendo `job_etapas_completadas`, `job_averias_cubigest` y el condicional `job_sync_horario` | **Corregido:** tabla completa de 9 jobs (8 fijos + 1 condicional) con su condición de activación explícita (sección 5 del Manual Técnico) |
| 4 | **Desactualizado.** Hablaba de "Motor de Tiempos" como si fuera el motor de asignación | **Corregido:** "el Motor" es el nombre correcto del motor de asignación (`motor_v2.py`); "Motor de Tiempos" se aclara como el proyecto de análisis estadístico previo (FASE3), hoy parcialmente incorporado como reglas `EST-`/`PRO-`, no fusionado con el motor de asignación |
| 5 | **Sin respaldo verificable.** Sección de riesgos normativos mezclaba Ley de 40 horas, Dirección del Trabajo, NCh204 y protección de datos como si fueran análisis cerrados | **Corregido:** Ficha Técnica sección 8-9 presenta cada punto como hecho operativo verificado en código + pregunta abierta explícita "POR CONFIRMAR con TO / asesoría legal", sin afirmar cumplimiento ni incumplimiento de ninguna norma |
| 6 | **Impreciso.** Puertos documentados como 8000 (backend) y 80 (frontend), que son los puertos *internos* del contenedor | **Corregido:** puertos reales del host (8001/3001) verificados en vivo con `docker compose ps`, con nota explícita de que no están declarados en `docker-compose.yml` |
| 7 | **Sin respaldo.** No mencionaba que la mayoría de dependencias de Python no están pinneadas por versión | **Corregido:** Ficha Técnica sección 1 lista versión real vs. pinneada, con advertencia de riesgo de reproducibilidad de build |
| 8 | **Incompleto.** Rollback descrito con nombres de imágenes Docker de respaldo específicas, presentadas como vigentes | **Corregido:** procedimiento de rollback redactado como plan **no ensayado**, con advertencia explícita de que la existencia de esas imágenes no se pudo reverificar en esta redacción |
| 9 | **No mencionaba** la práctica real de copias manuales de `.db` como único mecanismo de respaldo existente | **Corregido:** sección 9 del Manual Técnico documenta los archivos de backup manual encontrados en el repo como evidencia de la ausencia de un mecanismo automatizado |
| 10 | **No mencionaba** los tres mapeos distintos de sucursal (SPP↔`motor_v2.py`↔Cubigest general↔`EstExi1`) | **Corregido:** sección 2.4 del Manual Técnico documenta los tres mapeos por separado, con la inconsistencia Cerrillos=4/10 explícita |
| 11 | **No mencionaba** el bug de fecha `YYYYMMDD` vs `YYYY-MM-DD` ni el bug de join `MAQ_ID`/`MAQ_NRO` | **Corregido:** ambos documentados como lecciones técnicas en la sección 2.5 del Manual Técnico |
| 12 | **No mencionaba** el hallazgo abierto del bloque de auto-reparto (solape de operador, tope de jornada) | **Corregido:** sección 4.8 del Manual Técnico, citando `HARNESS.md` FAILURE_LOG, con advertencia de que no se confirmó si ya está resuelto (ver Limitación 1) |
| 13 | **Índice de entrega** no incluía inventario del estado del repositorio de TO (archivos sin commitear, ramas obsoletas, remoto) | **Corregido:** `INDICE_ENTREGA.md` v2 sección 3 |

---

## 4. Hallazgos operativos que Montu debería conocer (riesgos reales, no solo documentación)

1. **Riesgo de reproducibilidad de build:** la mayoría de dependencias de Python no están pinneadas
   (`fastapi`, `uvicorn`, `pyodbc`, `pandas`, `httpx`, `bcrypt`, `requests`, `beautifulsoup4`, `python-dotenv`,
   `openpyxl`, `pytz`). Un `docker compose build --no-cache` en una fecha distinta puede traer una versión
   incompatible sin que nadie lo decida — recomendación: pinnear con la salida de `pip freeze` capturada en este
   manual.
2. **Corregido en auditoría 28-09-2026:** el fix de auto-reparto (operador en 2 máquinas simultáneas, tope de
   jornada) **sí está implementado** en `motor_v2.py` desde los commits `0a959e8` (14/15-09) y `313d089`
   (24-09, que además cambió el reparto en paralelo a manual-only con alerta informativa). `HARNESS.md`
   (`FAILURE_LOG`) sigue listando el hallazgo como PENDIENTE — está desactualizado y debería corregirse para no
   inducir a error a la próxima persona que lo use como fuente sin releer el código (como ocurrió en el primer
   borrador de este mismo documento).
3. **No hay respaldo automatizado de `optifierro_v2.db`.** Es la única fuente de verdad de configuración de
   máquinas, operadores, planes guardados y usuarios. Hoy depende enteramente de que alguien recuerde copiar el
   archivo a mano antes de una intervención de riesgo.
4. **El origin remoto por defecto (`origin/HEAD`) apunta a `main`, una rama vacía**, mientras el trabajo real
   vive en `master`. Cualquier `git clone` simple de alguien nuevo en el proyecto (sin que le indiquen
   explícitamente "usa master") terminará en una rama vacía y puede concluir erróneamente que el repositorio está
   roto o incompleto.
5. **El working tree de TO tiene archivos de trabajo sin clasificar** (`archivos no clasificados/`, `logs_cca/`,
   varios scripts sueltos de diagnóstico y dos copias `.bak` de código de producción dentro del árbol). No es
   bloqueante, pero dificulta que un técnico nuevo distinga qué es código vigente de qué son restos de sesiones
   de trabajo anteriores — ver acciones de higiene recomendadas en `INDICE_ENTREGA.md` sección 3.
