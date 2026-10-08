# HARNESS — OptiFierro V2
**Versión:** 1.0
**Proyecto:** OptiFierro V2 — Sistema de Planificación Torres Ocaranza
**Fecha creación:** 2026-05-29
**Última actualización:** 2026-09-14 (agregado AR-009 — operador nunca en 2
máquinas simultáneas, ni en flujo normal ni en auto-reparto; agregado
FAILURE_LOG del hallazgo real de hoy)
**Stack:** FastAPI / React / Vite / TypeScript / Tailwind v4 / SQLite / SQL Server Cubigest
**Servidores:** PROMETHEUS-AI-CORE 192.168.1.65 (producción Windows 11)

---

## 1. FORBIDDEN_PATTERNS

| ID | Patrón prohibido | Motivo | Origen |
|---|---|---|---|
| FP-001 | Usar `localhost` o `host.docker.internal` para comunicación inter-contenedor | Los contenedores en la misma compose network deben usar el hostname del servicio (ej: `geovictoria-api:8002`). localhost apunta al contenedor mismo, no al vecino. | QA sesión #7 — bug crítico Docker networking |
| FP-002 | Modificar `_BODSUC_MAP = {1:2, 10:1, 14:3}` en motor_v2.py | Mapping crítico sucursal_id interno → Cubigest SucCod. Calama=1→2, Cerrillos=10→1, Santiago, Coronel=14→3. Cambiar rompe todas las consultas a Cubigest. | Regla arquitectónica inamovible |
| FP-003 | Agregar filtro por peso >= N kg en consultas de bolsa de trabajo | Filtro >=1500kg ocultaba ~55% del trabajo real de Coronel. El motor no filtra por peso — eso es decisión del planificador humano. | QA sesión #8 — bug crítico datos Coronel |
| FP-004 | Hacer `docker restart` cuando cambian variables de entorno | Variables de entorno solo se aplican con `--force-recreate`. Restart no las recarga. Usar: `docker compose up -d --force-recreate [servicio]` | Bug de configuración recurrente |
| FP-005 | Asumir que sucursal_id en código = SucCod en Cubigest | Son distintos. El carácter inicial del código de material indica sucursal Cubigest: 1=Cerrillos, 2=Calama, 3=Coronel. Siempre usar `_BODSUC_MAP` para traducir. | Regla de mapeo de datos |
| FP-006 | Asumir que Cerrillos tiene sucursal_id=10 en TODOS los archivos | motor_v2.py usa Cerrillos=4 (inconsistencia conocida). El resto del código usa 10. No cambiar un lado sin verificar el otro. Documentado en CLAUDE.md. | Inconsistencia arquitectónica conocida CLAUDE.md (sincronizado desde copia TO, 09-09) |
| FP-007 | Modificar motor_v2.py sin correr primero los tests de integración | El motor es la pieza más crítica del sistema. Cambios sin tests pueden romper planificación silenciosamente. | Regla de proceso (sincronizado desde copia TO, 09-09) |
| FP-008 | Mapear IdSucursal 2, 7 u 11 de Cubigest | Cubigest es multi-empresa (mismo holding TO). IdSucursal 1=Calama, 4=Cerrillos, 14=Coronel son las únicas plantas de Torres Ocaranza en Etapa 1. IdSucursal 2, 7, 11 pertenecen a otras razones sociales del mismo grupo. Excluidas por instrucción explícita de Gustavo. No mapear sin nueva autorización escrita. | QA sesión 2026-05-29 (sincronizado desde copia TO, 09-09) |
| FP-009 | Clasificación acero AD/AG con `else` o `> 16` para grueso | AD = diámetro ≤ 16mm exacto. AG = diámetro ≥ 18mm exacto. NUNCA usar `else` ni `> 16` para asignar grueso — el gap de 17mm no existe en barras estándar pero la condición debe ser explícita. Usar siempre `elif diam >= 18` en Python y condición explícita en SQL/TS. Afecta: `compromisos_semanales.py`, `obtener_proyeccion_semanal`, y cualquier lógica futura de clasificación de acero. | Fix 2026-06-03 (sincronizado desde copia TO, 09-09) |
| FP-010 | Tratar `/Users/montu/ServerX-Home/stack/optifierro_v2_frontend` (o cualquier ruta equivalente en serverX) como flujo de desarrollo real/canónico | Es un git worktree ROTO y ABANDONADO de un prototipo temprano en Streamlit (archivos de marzo 2026, antes de que existiera el FastAPI+React actual). No tiene relación con el desarrollo real de hoy. El único flujo real es directo en TO (`C:\Users\OptiFierro\Desktop\optifierro`) + push a `github.com/RodMontu/Optifierro-V2`. Una ventana de chat lo confundió el 14-09-2026 y lo presentó como "flujo canónico" — descartar cualquier instrucción que lo mencione. | Incidente 14-09-2026, ventana "fix CUBIGESTPRUEBAS" |
| FP-011 | Confiar en `git status` de `~/graphify-workspace/{optifierro,scrap-geovictoria}` sin sincronizar primero | Es una COPIA DE ANÁLISIS para Graphify en el Mac Studio, no el repo de desarrollo. Puede divergir del real (commits locales que nunca llegaron a TO/GitHub, o quedar desactualizada). Antes de diagnosticar algo como "sucio" o "corrupto" ahí, correr `git fetch + git reset --hard origin/master` (o comparar hash HEAD contra TO real) — lo que parece "sucio" suele ser solo desactualización, no corrupción. Una ventana lo diagnosticó mal el 14-09-2026 ("miles de archivos falsos modificados" — en los hechos eran ~30 diffs preexistentes conocidos). | Incidente 14-09-2026, ventana "fix CUBIGESTPRUEBAS" |
| FP-012 | Asumir que un `nombre_maquina` + `fecha_fin` de una fila top-level de `programacion_guardada` describe una sola máquina | Cuando la tarea pasó por el bloque de auto-reparto, `fecha_fin` top-level toma `max(fines_reparto)` — puede pertenecer a la OTRA máquina del reparto, no a la de `nombre_maquina`. Para el detalle real por-máquina, usar siempre el campo `reparto[]` de cada tarea, nunca los campos top-level solos. | Incidente 14-09-2026 — generó falsos positivos de "solape de máquina" al analizar datos reales |
| FP-013 | Agregar o cambiar el horario de un job en el scheduler de `backend/main.py` (APScheduler) sin listar los horarios de TODOS los jobs existentes y verificar margen suficiente (≥10-15 min) contra el nuevo | `optifierro_v2.db` corre en SQLite modo "delete" por defecto hasta el fix del 01-10 (ver FP-014): cualquier escritura concurrente de dos jobs en la misma ventana de minutos bloquea el archivo completo (`database is locked`). `_job_importar_optisteel` (agregado 30-09 con `IntervalTrigger`/`CronTrigger(minute="*/20")` sin anclar a hora de pared) coincidió con el cluster de jobs de las 08:08-08:30 y causó caída total del login y de la generación automática del 01-10-2026. | Incidente 01-10-2026 — ver `docs/agentes/CCa_investigacion_lock_horario_scraper_20261001.md` en TO |
| FP-014 | Abrir conexiones nuevas a `optifierro_v2.db` con `sqlite3.connect()` directo en vez del helper `backend/db_conn.py` (`conectar()`) | El helper fuerza `PRAGMA journal_mode=WAL` + `PRAGMA busy_timeout=5000` en cada conexión. Si el archivo de BD se recrea alguna vez desde cero, SQLite vuelve a nacer en modo "delete" (bloqueo de archivo completo) salvo que algo lo fuerce explícitamente — eso fue la causa raíz de FP-013. Ya migrado `main.py` e `init_db.py`; `motor_v2.py` y el resto de `routers/*.py` (~120 call sites) quedan pendientes de migración incremental — no se tocaron en el incidente 01-10 por estar fuera de alcance de esa tarea. | Incidente 01-10-2026 |

---

## 2. ARCHITECTURAL_RULES

| ID | Regla | Enforcement | Herramienta |
|---|---|---|---|
| AR-001 | Layering de dependencias: Types → Config → Repo → Service → Runtime → UI | Revisión manual en PR + CCa evalúa imports | Code review |
| AR-002 | Cubigest DB (SQL Server 192.168.1.195) = solo lectura. Nunca INSERT/UPDATE/DELETE. | No hay credenciales de escritura disponibles. Si se intenta, falla con permisos. | SQL Server permissions |
| AR-003 | SQLite local = escritura permitida. Separar claramente queries SQLite vs Cubigest en código. | Usar prefijo de función: `get_local_*` vs `get_cubigest_*` | Naming convention |
| AR-004 | Ventana temporal de trabajo: retroactivo -30 días desde hoy. No modificar sin confirmar con Gustavo (BACKLOG-OF-01). | Test en motor_v2.py que valida ventana | Unit test |
| AR-005 | IDs de sucursal en SQLite: Calama=1, Cerrillos=10, Coronel=14. Nunca mezclar con SucCod de Cubigest. | Comentario obligatorio en todo código que maneje IDs de sucursal | Code convention |
| AR-006 | TypeScript strict mode activo (`noUnusedLocals`, `noUnusedParameters`). Todo código nuevo debe compilar limpiamente. | `npm run lint` | ESLint + tsc (sincronizado desde copia TO, 09-09) |
| AR-007 | Specs de UI en `docs_ms/` son la fuente de verdad para lógica de negocio. Consultar antes de cambiar cualquier componente de dominio. | Manual review | docs_ms/*.md (sincronizado desde copia TO, 09-09) |
| AR-008 | Antes de proponer o ejecutar cualquier cambio de código en este repo (o en scrap-geovictoria), consultar el grafo de dependencias vigente (Graphify, en ~/graphify-workspace/ del Mac Studio) para identificar impacto en otras partes del sistema. Después de cualquier modificación real, regenerar el grafo antes de cerrar la tarea. El grafo es válido solo si corresponde al commit HEAD actual del repo. | Consultar antes de PR, regenerar después de merge | GRAPH_REPORT.md (sección Graph Freshness) |
| AR-009 | Un operador puede estar calificado/habitual para 2+ máquinas — normal y esperado. Pero solo puede tener TRABAJO ASIGNADO (ventana de tiempo real) en UNA máquina a la vez. Puede trabajar en una, en la otra, o en ambas en momentos distintos — nunca simultáneamente. Aplica a TODOS los caminos de asignación del motor (flujo normal Y bloque de auto-reparto), no solo al principal. | Chequeo de solape contra intervalos del operador antes de confirmar cualquier asignación, en todos los caminos | motor_v2.py — código de asignación (confirmado por Montu 14-09-2026 tras hallazgo real en producción) |

---

## 3. PERMISSION_MATRIX

### Tier 1 — Autónomo
- Leer SQLite local (optifierro.db)
- Leer SQL Server Cubigest (solo SELECT)
- Ejecutar motor_v2.py en modo dry-run
- Correr tests unitarios y de integración
- Leer logs de FastAPI

### Tier 2 — Requiere confirmación de Montu
- Modificar motor_v2.py o cualquier archivo de lógica de negocio
- Cambiar docker-compose.yml en producción (TO)
- Modificar queries a Cubigest
- Actualizar dependencias (requirements.txt)
- Deployment a PROMETHEUS-AI-CORE

### Tier 3 — NUNCA autónomo
- INSERT/UPDATE/DELETE en Cubigest (no hay credenciales de escritura)
- Modificar _BODSUC_MAP
- Eliminar tablas o datos de SQLite de producción
- Cambiar credenciales de conexión Cubigest
- Push directo a rama main sin PR

---

## 4. FAILURE_LOG

| Fecha | Módulo | Error detectado | Causa raíz | Corrección aplicada | Regla generada |
|---|---|---|---|---|---|
| 2026-05 | Docker / networking | API containers llamando localhost entre sí → timeout | Containers en misma compose network deben usar hostname de servicio, no localhost | Cambiar URLs de localhost a nombre de servicio inter-contenedor | FP-001 |
| 2026-05 | motor_v2.py | bolsa_de_trabajo mostraba 0 kg para todas las OCs | append() de sites no estaba siendo llamado correctamente | Fix en lógica de append en motor_v2.py | FP-003 (relacionado) |
| 2026-05 | Frontend / badge | Turno A/B badge mostraba valor incorrecto por race condition | Cálculo del badge en frontend dependía de estado no sincronizado | Mover lógica de badge al backend para cálculo determinístico | AR-001 (layering) |
| 2026-05 | motor_v2.py / Coronel | ~55% de OCs de Coronel no aparecían en planificación | Filtro >=1500kg incorrecto aplicado a bolsa de trabajo | Eliminar filtro de peso del motor — no corresponde al motor decidir esto | FP-003 |
| 2026-09-14 | motor_v2.py — bloque auto-reparto | (a) Mismo operador con trabajo en 2 máquinas simultáneas en Calama; (b) tarea con fin ~1h45min después del fin de jornada; (c) falso positivo de "misma máquina, 2 operadores" | El bloque de auto-reparto (agregado 12-09) llama a `_operadores_candidatos` para cada máquina del reparto SIN cruzar contra intervalos del operador, y calcula `_fin_r` sin ningún tope contra `hora_fin` de jornada. Además, la fila-resumen top-level mezcla `nombre_maquina` de una máquina con `fecha_fin` de la otra (ver FP-012) | Pendiente de implementar (autorizado por Montu 14-09): chequeo de solape de operador + tope de jornada (corta al límite, remanente al turno siguiente) dentro del bloque de auto-reparto; corregir construcción de la fila-resumen | AR-009, FP-012 |
| 2026-10-01 | SQLite (`optifierro_v2.db`) / scheduler `main.py` | 08:10-11:02 (UTC; 08:10-08:11 local): `_ejecutar_generacion` falló con `database is locked` para las 3 sucursales (Calama/Cerrillos/Coronel) turno día — cero filas en `log_planificacion_auto` para hoy (ni 'ok' ni 'error': el propio INSERT de error también chocó con el lock y quedó silenciado por un `except: pass`). 08:28-08:31 local: login SPP completo caído, mismo error, mismo origen. | `optifierro_v2.db` nunca había estado en modo WAL (modo "delete" por defecto: una escritura bloquea el archivo completo). `_job_importar_optisteel` (agregado 30-09, `CronTrigger(minute="*/20")` sin anclar) coincidió con el cluster de las 08:08/08:10/08:30 (scraper GV, job_dia, its_cerradas+etapas+averias) y saturó la BD. | Mitigación en caliente 08:31 (`PRAGMA journal_mode=WAL` directo sobre el archivo). Hardening de código 01-10: `_job_importar_optisteel` reanclado a `CronTrigger(hour="0-7,9-23", minute=45)` (margen ≥10 min contra todos los demás jobs); helper `backend/db_conn.py` fuerza WAL+busy_timeout=5000 en cada conexión nueva (migrado en `main.py`/`init_db.py`, pendiente en el resto). | FP-013, FP-014 |
