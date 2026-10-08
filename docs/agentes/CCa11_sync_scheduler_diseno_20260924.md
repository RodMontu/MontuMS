# CCa-11 — Mapa de "Sincronizar" + actualización horaria + universo del scheduler

**Modo:** SOLO LECTURA (diseño, sin implementación). **Fecha:** 24-09-2026.
**Código verificado en TO:** `ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && git log -1"` → HEAD `1cd8f88 fix(utils): decodificar_material lee largo decimal...` (coincide con el HEAD indicado en el prompt).
**Nota de alcance:** el repo local en el Mac (`~/graphify-workspace/optifierro`) tiene commits más nuevos que no vi en TO (SPP/B16/B45/B35/HEBRAS-01); todo lo citado abajo es del código real en TO, no del repo local.

---

## 1. Botón "Sincronizar" (sección Programación)

- Frontend: `frontend/src/components/domain/GestorProgramacion.tsx:2015` — `onClick={() => { setUndoState(null); setBannerAveria(false); onAveriaTimestampConsumed?.(); fetchData(); }}`.
- `fetchData` (`GestorProgramacion.tsx:1408`) hace **únicamente** `fetch('/api/programacion?sucursal=...&turno=...&fecha=...')` (GET) y renormaliza la respuesta en el estado local. No dispara scraping, no llama `/generar`, no llama al scraper del Cuadro.
- `GET /api/programacion` (`backend/routers/programacion.py:275`) lee `global_recursos`/`global_eventos` — **memoria viva** poblada por el `lifespan` al arrancar el proceso y actualizada solo por `_ejecutar_generacion` (scheduler) o por `POST /generar` (botón "Generar", distinto botón). El botón "Sincronizar" **no re-consulta Cubigest ni el Cuadro**; solo refresca lo que ya está en RAM/SQLite desde la última generación.
- **Conclusión:** hoy "Sincronizar" en Programación es un *refresh de pantalla*, no un *refresh de datos*. No actualiza ninguna de las dos fuentes (ni universo de compromisos ni Cuadro).
- Aparte, hay otros 3 botones "Sincronizar" homónimos en otras secciones (`GestorMaquinas.tsx:350`, `GestorOperadores.tsx:114`, `GestorMatPrima.tsx:169` como "Sincronizar Stock") — cada uno hace su propio `fetchData` local a su propio endpoint; no tocan el universo de compromisos ni el Cuadro tampoco.

## 2. Actualización automática hoy (jobs de `main.py`)

Único scheduler real: `AsyncIOScheduler` en `main.py:427-462` (America/Santiago). Jobs, L-V salvo feriado CL (`holidays_lib.Chile`):

| Job | id / hora | Qué hace | Fuente que toca |
|---|---|---|---|
| `_ejecutar_scraper_geovictoria` | 08:08 y 20:08 (`main.py:428,433`) | `POST http://192.168.1.111:8002/scraper/ejecutar` — dispara un **servicio externo** (serverX, fuera de este repo) que hace scraping de Geovictoria y, según el docstring de `routers/admin.py:413` ("Llamado por el scheduler de scrap-geovictoria vía HTTP, misma red docker"), es quien a su vez llama `POST /api/admin/cuadro-programacion/ejecutar`. **NO VERIFICADO**: el código de ese servicio no está en este repo, no pude confirmar horario exacto ni que siempre incluya el Cuadro. |
| `_job_dia` / `_job_noche` | 08:10 y 20:10 (`main.py:437,442`) | `_ejecutar_generacion(suc, turno)` para suc 1/10/14 → llama `_programar_turno` del motor y persiste en `programacion_guardada` + `global_eventos`. Usa **`_obtener_pids_pendientes`** (universo Cubigest crudo, ver §5), NO el Cuadro. |
| `_job_verificar_its_cerradas` | cada hora, minuto :30 (`main.py:447`) | Único job "cada 1 hora" que existe hoy. Solo marca `estado='completado'` en `global_eventos` para ITs que salieron de estado activo en Cubigest. **No refresca ni el universo ni el Cuadro** — no trae etiquetas nuevas, solo cierra las que ya estaban cargadas. |
| `_job_tardios_dia` / `_job_tardios_noche` | 08:51 / 21:21 (`main.py:452,457`) | Alertas de operadores tardíos (SQLite local), no toca Cubigest/Cuadro. |

**El scraper del Cuadro (`cuadro_programacion_ejecutar`, `routers/admin.py:404-427` → `scrape_cuadro_programacion`, `backend/scraper_cuadroprogramacion.py:153`) NO tiene ningún `CronTrigger` propio en `main.py`.** Solo existe como endpoint HTTP, invocado (según el comentario del propio código) por el servicio externo de Geovictoria en 192.168.1.111:8002 — no por el `AsyncIOScheduler` de este proceso. Esto es justo lo que confirma **A13** del plan de trabajo (`pendientes_sistema_planificador.md:76`): el 500 de SANTIAGO es reproducible desde el propio Cubigest, ya detectado el 22-09, no bug de OptiFierro.

**Qué pasa si el scraper del Cuadro falla (HTTP 500):** en `scrape_cuadro_programacion` (`scraper_cuadroprogramacion.py:222-227`) el `soup3.find('table', ...)` que falla lanza `RuntimeError` **antes** de llegar al bloque `DELETE FROM cuadro_programacion_optisteel ... INSERT ...` (líneas 244-256, ejecutado después). Es decir: **los datos previos del Cuadro se conservan intactos** (no se borran ni se vacían) cuando el scrape falla — se queda desactualizado en silencio. No hay ningún aviso visible al usuario en frontend (ni banner ni timestamp de "última sincronización exitosa" encontrado en `GestorProgramacion.tsx` ni en `CompromisosSemanales.tsx`); el único rastro es el log del backend (`logger.error` en `routers/admin.py:429`). Esto coincide con lo documentado en A13: "Cerrillos quedó 1 día desactualizado mientras esto no se resuelva", sin mecanismo de alerta.

**"Sincronización horaria a Cubigest" (concepto general del prompt) NO existe hoy como funcionalidad.** Es el ítem **A4** del plan de trabajo (`pendientes_sistema_planificador.md:68`), estado "PRIORIZADO 07-09... pendiente levantar las queries actuales", Fase 4 (Infraestructura TI), **no ejecutado aún**. El único job horario real (`_job_verificar_its_cerradas`) no cumple ese rol — solo cierra ITs, no trae datos nuevos.

## 3. Secciones y su fuente real

| Sección | Endpoint | Función / archivo:línea | Fuente | Ventana de fechas |
|---|---|---|---|---|
| Programación (Gantt) | `GET /api/programacion` | `routers/programacion.py:275` | `global_eventos`/`global_recursos` en RAM, poblados por `_ejecutar_generacion` (usa `_obtener_pids_pendientes`, universo) o por `POST /generar` (usa `_obtener_pids_pendientes_optisteel`, Cuadro) — **depende de cuál corrió último** | La de la función que generó el plan vigente |
| Compromisos Futuros (toggle dentro de Programación) | `GET /api/compromisos-semanales` | `routers/compromisos_semanales.py:39` (`get_compromisos_semanales`) → llama `_obtener_pids_pendientes` (`programacion.py:1404`) | **Universo** (Cubigest crudo, NO el Cuadro) | `-30d` a `+21d` desde hoy (`programacion.py:1471`) |
| Vista Semanal (Global) | `GET /api/semanal` | `routers/programacion.py:596` (`obtener_proyeccion_semanal`) → `_obtener_pids_pendientes` | Universo | `-30d` a `+21d` |
| Próximas Semanas (Calendario Futuro) | `GET /api/calendario-futuro` | `routers/calendario_futuro.py:26-70` | Query directa a Cubigest (`FROM IT`), independiente de `_obtener_pids_pendientes` | `hoy` a `+20d` (línea 69-70), **sin cola de atrasadas** |
| Materia Prima (comprometido) | `GET /api/materias-primas` | `routers/materias_primas.py:36` → `database_cubigest.py:341` (`obtener_comprometido_por_codigo`) | Query propia a Cubigest (duplicada, no reusa `_obtener_pids_pendientes`) | `-30d` a `+21d` (`database_cubigest.py:373`) |

**Hallazgo relevante para §4 y B42:** "Compromisos Futuros" hoy **NO** está alimentado por el Cuadro OptiSteel como plantea el concepto de negocio del prompt — usa el mismo universo crudo que Vista Semanal (mismo componente frontend `CompromisosSemanales.tsx` reutilizado en ambos contextos, mismo endpoint `/api/compromisos-semanales`). Solo `POST /generar` (Programación "Generar") y su Cuadro alimentan de verdad el pipeline OptiSteel.

**Hallazgo sobre "muy futura":** las 3 consultas que implementan el "universo de compromisos" (`programacion.py:1471`, `materias_primas.py:239`, `database_cubigest.py:373`) usan la **misma ventana fija `-30d`/`+21d`**, duplicada en 3 lugares con SQL independiente. Ninguna incluye explícitamente fechas "muy futuras" (ej. dic-2026) salvo por el `OR ISNULL(...) IS NULL OR = '19000101'` de `programacion.py:1472-1474` (solo cubre IT sin fecha, no fecha futura real puesta a propósito). Si un usuario pone una fecha de despacho "muy futura" (dic-2026) en Cubigest, **hoy esa IT queda fuera de las 3 vistas del universo** (Vista Semanal, Compromisos Futuros, Materia Prima) hasta que la fecha entre en la ventana de +21 días. Esto contradice directamente el requerimiento de Montu de incluir "muy futura" en el universo.

## 4. Diferencias con el requerimiento

Requerimiento: "Sincronizar" y la actualización horaria deben refrescar **ambas fuentes juntas** (universo + Cuadro), en el orden correcto, con aviso seguro si una falla.

Brechas encontradas:
1. **"Sincronizar" no refresca nada** — es un simple re-GET de memoria (§1). No dispara ni el universo (que de todos modos se consulta en vivo a Cubigest en cada llamada a `_obtener_pids_pendientes`, sin caché) ni el Cuadro (que sí tiene caché en `cuadro_programacion_optisteel` y solo se refresca vía el scraper externo).
2. **No existe ningún job "cada 1 hora" que traiga datos nuevos** — el único job horario (`_job_verificar_its_cerradas`) solo cierra ITs ya cargadas. La sincronización horaria real (A4) está pendiente de implementar, no es un bug sino trabajo no iniciado.
3. **Las dos fuentes no están acopladas hoy**: el universo (`_obtener_pids_pendientes`) se consulta en vivo a Cubigest cada vez que se llama (sin persistencia intermedia); el Cuadro se persiste en SQLite (`cuadro_programacion_optisteel`) y solo se actualiza cuando el servicio externo de Geovictoria lo dispara. No hay ningún punto del código que actualice ambas en la misma transacción/llamada.
4. **Fallo silencioso**: si el scraper del Cuadro falla (caso SANTIAGO 500), los datos viejos se conservan pero sin ningún indicador visible en UI de "desactualizado desde X". El universo, al consultarse en vivo, no tiene este problema de raíz (siempre trae el estado actual de Cubigest), pero tampoco valida si Cubigest mismo está degradado.
5. **Ventana `-30d/+21d` fija en 3 lugares duplicados** excluye "muy futura" — brecha directa con el concepto de negocio, y riesgo de que alguien cambie un límite y no el otro.

**Comportamiento seguro propuesto (diseño, no implementado):**
- Un único endpoint `POST /api/sync/ejecutar` que orqueste, en orden: (a) invalidar/recalcular universo (no requiere red externa, es query directa a Cubigest — solo requiere confirmar que Cubigest esté arriba con una query liviana antes); (b) disparar el scraper del Cuadro (única fuente que requiere red externa/scraping HTML y puede fallar con 500).
- Si (b) falla: mantener el Cuadro anterior (ya es el comportamiento actual por diseño de `scrape_cuadro_programacion`), pero **agregar un timestamp `ultima_sincronizacion_ok` por sucursal** (nueva columna o tabla chica) y exponerlo en el frontend (badge "Cuadro actualizado hace Xh" / rojo si > umbral) para que el fallo deje de ser silencioso.
- Si (a) falla (Cubigest caído): no pisar el universo en memoria de sesiones ya cargadas (hoy es consulta en vivo sin caché, así que un fallo simplemente devuelve `[]` — ver `except Exception: return []` en `programacion.py:1494` — **hoy un fallo de Cubigest vacía silenciosamente el universo**, riesgo real a corregir también).

## 5. Alineación del scheduler con `POST /generar`

Confirmado el diagnóstico del prompt: `main.py:145` usa `_obtener_pids_pendientes` (universo crudo, TOP 2000, sin filtro de Cuadro/[N2]) mientras `POST /generar` (`routers/programacion.py:1167`) usa `_obtener_pids_pendientes_optisteel` (`programacion.py:1634`), que reutiliza `_piezas_optisteel_por_viajes` (`programacion.py:1518`, JOIN compartido con la Bolsa de Trabajo) y aplica lógica adicional de exclusión de viajes con ITs detenidas y fechas desde `turnos_programados` que **no está en el pipeline del scheduler automático**.

**Diseño mínimo propuesto:** extraer una función compartida `preparar_etiquetas_generacion(sucursal_id, fecha, turno)` en `routers/programacion.py` que encapsule exactamente lo que hoy hace `_obtener_pids_pendientes_optisteel` + la exclusión [N2] + resolución de fecha vía `turnos_programados`, y hacer que:
- `POST /generar` (`programacion.py:1167`) la llame (mismo resultado que hoy, refactor puro).
- `_ejecutar_generacion` en `main.py:140-145` importe y llame la misma función en vez de `_obtener_pids_pendientes`.

**Impacto:**
- **B42** (mapa de N° de etiqueta): hoy solo se puebla al pasar por el pipeline del Cuadro (`_obtener_pids_pendientes_optisteel`/`_piezas_optisteel_por_viajes`). Si el scheduler automático empieza a usar la misma función, el scheduler automático también poblaría ese mapa — efecto colateral positivo, pero a validar que no rompa nada que hoy asuma que ese mapa solo se llena vía `/generar` manual.
- **B16** (capacidad de planta en `metadata.capacidad`) y **B45** (exclusión FP-LC): ambos ya están implementados dentro de `_obtener_pids_pendientes` (B45, `programacion.py:1494-1502`) y en `_programar_turno`/`_resolver_ventana_override` (B16, ya compartido — ver `main.py:143,152` que ya llaman `_resolver_ventana_override` y `_obtener_presencia_capacidad` igual que `/generar`, según comentarios "B35"/"B16" en el propio código). Este refactor no debería tocar B16 (ya alineado); si toca B45 hay que verificar que `_piezas_optisteel_por_viajes` también excluya FP-LC (**NO VERIFICADO** — no confirmé si `_obtener_pids_pendientes_optisteel` aplica el mismo filtro `es_despacho_directo`).
- Riesgo principal: el scheduler automático pasaría a depender del Cuadro (SQLite `cuadro_programacion_optisteel`) en vez de Cubigest en vivo — si el Cuadro está desactualizado (caso SANTIAGO §2), la generación automática de las 08:10/20:10 heredaría ese atraso. Esto es justamente la brecha #3 de §4: hay que resolver primero que ambas fuentes se mantengan sincronizadas, o el refactor del scheduler simplemente traslada el problema de "universo vs Cuadro" a "Cuadro desactualizado sin aviso".

## 6. Plan de trabajo (atómico)

| # | Cambio | Archivo/función | Riesgo | Cómo probar sin escribir en prod | Tamaño est. | ¿Hoy? |
|---|---|---|---|---|---|---|
| 1 | Agregar timestamp `ultima_sincronizacion_ok` por sucursal tras `scrape_cuadro_programacion` exitoso | `scraper_cuadroprogramacion.py` (nueva col/tabla), `routers/admin.py:427` | Bajo — solo lectura adicional, no cambia lógica de negocio | Ejecutar scraper contra CALAMA/CORONEL (funcionan hoy) en ambiente de prueba, verificar timestamp se escribe; simular fallo (mockear `soup3.find`→None) y verificar que NO se pisa | ~20 líneas | Sí |
| 2 | Badge en frontend "Cuadro actualizado hace Xh" con umbral de alerta | `GestorProgramacion.tsx`, nuevo campo en `GET /api/programacion` o endpoint propio | Bajo — solo UI | Con datos mockeados de timestamp viejo, verificar que el badge cambia de color | ~30-40 líneas | Sí |
| 3 | Blindar `_obtener_pids_pendientes` para no devolver `[]` silencioso si Cubigest falla (hoy `programacion.py:1494` retorna `[]` en except) — devolver señal de error explícita, no confundir "sin pendientes" con "Cubigest caído" | `programacion.py:1493-1495` | Medio — cambia contrato de la función, hay que revisar todos los callers (`_ejecutar_generacion`, `/api/semanal`, `/api/compromisos-semanales`) | Simular excepción de `cubigest_db.execute_query` en ambiente de prueba, verificar que cada caller maneja el nuevo valor sin romper | ~40-60 líneas (toca 3-4 callers) | No — requiere revisar todos los consumidores primero |
| 4 | Extraer `preparar_etiquetas_generacion()` compartida y usarla en `_ejecutar_generacion` | `main.py:140-145`, `programacion.py` (nueva función cerca de `_obtener_pids_pendientes_optisteel`) | Alto — cambia la fuente de datos del scheduler automático de producción (universo→Cuadro); si el Cuadro está desactualizado, la generación automática se degrada | Ejecutar `_ejecutar_generacion` manualmente en ambiente de prueba/staging con datos de una sucursal, comparar `tareas` resultantes contra `POST /generar` mismo día — deben coincidir | ~30 líneas (refactor, sin lógica nueva) | No — depender de #1/#3 primero para no degradar el scheduler en silencio |
| 5 | Endpoint único `POST /api/sync/ejecutar` que orqueste universo + Cuadro en orden y togee el botón "Sincronizar" de Programación a llamarlo | Nuevo en `routers/admin.py` o `programacion.py`; `GestorProgramacion.tsx:2015` | Medio-Alto — cambia el comportamiento del botón que usan los jefes de planta a diario | Probar en staging con Cubigest de solo lectura; medir tiempo de respuesta (el scraper del Cuadro puede tardar por sucursal) antes de exponerlo como botón síncrono | ~80-120 líneas | No |
| 6 | Unificar ventana de fechas `-30d/+21d` + tier "muy futura" en una sola función/constante reusada por las 3 consultas | `programacion.py:1471`, `materias_primas.py:239`, `database_cubigest.py:373` | Medio — cambia qué ITs aparecen en Vista Semanal/Compromisos Futuros/Materia Prima, visible para usuarios de negocio | Comparar conteo de ITs devueltas antes/después para una sucursal en un día conocido, validar con Montu/jefe de planta qué debe aparecer como "muy futura" | ~50-70 líneas (toca 3 archivos) | No — requiere que Montu defina el criterio exacto de "muy futura" (¿fecha límite? ¿flag explícito en Cubigest?) |

**Compatibles con desplegar HOY:** #1 y #2 (solo agregan visibilidad, no cambian ninguna fuente de datos ni lógica de negocio).
**No compatibles con hoy:** #3-#6 (cambian contratos de funciones compartidas por múltiples secciones, o requieren definición de negocio pendiente).
