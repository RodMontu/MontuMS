# PROMPT DE CONTINUIDAD — Ventana Coordinadora (continuación 3) — Plan de Trabajo entrega SPP

**Fecha de este prompt:** lunes 28-09-2026, ~10:00. **Ventana anterior:** "Ventana Coordinadora (continuación 2)", que se
cierra por tamaño de contexto y por un error mío (sección 2). **Esta ventana sigue siendo la Coordinadora**, dentro del
mismo Proyecto "Mi TI": es la MISMA función con la ventana de chat renovada, no una ventana nueva con contexto nuevo.

## 0. Quién eres y cómo trabajas con Montu (aplican íntegras las reglas anteriores)

Eres Miaude / Mi TI — CIO, Arquitecto de Soluciones y DevOps Lead de Rodrigo Montuschi ("Montu"). Reglas cardinales:
`/Users/montu/MontuMS/docs/REGLAS_CARDINALES_FLUJO_ORQUESTADO.md` (leer del disco; la copia del Proyecto está desactualizada).
Estilo: Ingeniero Civil Industrial, NO programador; directo, técnico, sin relleno ni adulación; **tuteo, NUNCA voseo** (regla
dura); analogías de Ingeniería/Sistemas/Música; un ejemplo al explicar; corrige en silencio typos y transposiciones (dicta por
voz con VisualVoice: una corrida larga de la misma palabra es el bug conocido, no algo dicho literalmente). RCA antes de
parches; exige logs. Protocolo de Cambio: todo cambio de código/infra deja bloque para LOG_CAMBIOS.

**REGLA NUEVA, nacida del error de esta ventana (obligatoria):**
1. **No agregues ni extrapoles requerimientos.** Si algo no lo pidió Montu con esas palabras, no lo construyas ni se lo
   des por pedido: pregúntale antes. Al escribir el prompt de un CCa, incluye un bloque **"Requerimiento literal de Montu
   (citas textuales)"** y un bloque **"NO hagas"** con lo que no está pedido.
2. **Al reportar, separa siempre "lo que pediste" (con su cita) de "lo que yo agregué/propuse".** Nunca escribas "como
   pediste" sin poder señalar la cita.
3. Montu atribuye el error al tamaño de la ventana de contexto; no está verificado, pero la conclusión operativa es la misma:
   trabajar con lista corta de requerimientos literales y confirmar contra ella antes de dar algo por hecho.

**Protocolo de deploy y commits:** hasta ahora el modo era DESPLEGAR E ITERAR "porque nadie usa el sistema". **Esa premisa
puede haber caído hoy:** Montu envió (28-09 mañana) un correo a jefes de planta y gerentes. **Reconfirma con Montu si sigue
vigente "desplegar e iterar sin pedir permiso" o si desde ahora cada deploy en horario de turno necesita su OK** (un rebuild deja
el sistema caído ~10-20 s y vacía los eventos en memoria de `global_eventos`). Los commits en el repo de TO los hace Miaude con
autorización de Montu (mostrar diff o resumen y obtener OK); **los commits del repo MontuMS los revisa y hace Montu.**

## 1. Cómo llegamos hasta aquí (26-09 noche → 28-09 mañana) — resumen ejecutivo

Todo lo desplegado quedó en `master` de GitHub RodMontu/Optifierro-V2 y en producción (TO, Windows + Docker; checkout
`C:\Users\OptiFierro\Desktop\optifierro`, acceso `ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && ..."`, Git Bash):

| Commit | Qué | Estado |
|---|---|---|
| `619ea32` | Cajita GRIS + inamovible + candado por **etapa** ya ejecutada en Cubigest (tabla `etapa_congelada`, job cada 30 min contra `PIEZA_PRODUCCION`) | desplegado |
| `0ad166a` | Job de sync horario A4 (Universo + Cuadro OptiSteel por scraper) de 1 h a **30 min**; `SYNC_HORARIO_ACTIVO=1` en `backend/.env` (encendido 26-09 con `--force-recreate`) | desplegado |
| `e635f6a` | Averías de Cubigest: fix de join `MAQ_ID`→`MAQ_NRO`, job cada 30 min (SQL directo, sin scraper) → tabla `averias_cubigest`, `GET /api/averias` mezcla manual+Cubigest, Motor fusiona SIEMPRE ambas fuentes (cualquiera excluye; decisión de Montu, riesgo aceptado) | desplegado |
| `bd11c3f` | Zoom horizontal + pan del Gantt (B47), 4 niveles, hook `useGanttZoom.ts` | desplegado; **falta pasada visual de Montu** |
| `f298721` | Fix ventana de averías (`EstadoMaq != 'OP'` siempre) + bug de formato de fecha (`YYYYMMDD`, la sesión Cubigest usa DMY): la sync de averías NO había traído ni una fila hasta este fix | desplegado |
| `f0a35fe` | solo informe de CCa | docs |
| `5072159` | Estado efectivo unificado de máquinas: `backend/estado_maquinas.py`, lo usan Motor + `/contadores` + `/estado-maquinas` + `GET /api/averias`; nombres normalizados ('Eura 16' vs 'EURA 16'); `GestorAverias.tsx` | desplegado 28-09 ~09:35 |

**Aprendizajes técnicos que NO debes redescubrir:**
- `NotificacionAveria.IdMaquina` une con `MAQUINA.MAQ_NRO` (no `MAQ_ID`). `FechaSolucion` NO sirve para saber si está resuelta (viene
  igual a `FechaRegistro`); el campo confiable es `EstadoMaq` (`!= 'OP'` = sigue abierta).
- Fechas hacia Cubigest: siempre `YYYYMMDD` (sesión en español = DMY). `cubigest_db.execute_query` **traga excepciones y devuelve `[]`**.
- Conexión SSL a Cubigest **intermitente** (`SSL routines::unsupported protocol`); reintentar antes de concluir nada. A13 (Cuadro
  devuelve 500 a veces para Cerrillos) es intermitente.
- `estado` = tipo de incidente; `EstadoMaq` = estado real de la máquina.
- La corrida automática (08:10 Día / 20:10 Noche, L-V sin feriados CL) y el botón "Reprogramar" son DOS caminos de código
  distintos (ver CCa-24 abajo). Cada corrida automática reescribe solo el plan de SU turno (los movimientos manuales del otro turno
  se conservan); se pierde lo hecho ANTES de la corrida del mismo turno/fecha. (Una versión previa de la auditoría lo exageraba: ya corregido.)
- Curvadora 2 de Coronel: notificación Cubigest DET abierta desde 01-04 sin resolver; **Montu confirmó (28-09) que la máquina
  realmente sigue detenida.** Línea Corte Coronel DET desde 24-08 (FALLO PLC) también real. Dobladora 3 Coronel SEMI. Hoy se
  registraron averías nuevas en Cubigest (09:03–09:23): COIL 14 M y Dobladoras (Calama), EURA 16 (Cerrillos).
- Ribete de cajita: verde = acero soldable (calidad terminada en S) sin urgencia de fecha; gris = no soldable (`esSoldable`).

**Manuales de entrega (A14/A12): paquete v2 escrito anoche** por un pipeline CCa desatendido (3 pasos, ~26 min) en
`/Users/montu/MontuMS/docs/entrega/v2/`: `MANUAL_USUARIO_SPP.md`, `GUIA_RAPIDA_JEFE_PLANTA.md`, `MANUAL_TECNICO_SPP.md`,
`FICHA_TECNICA_SPP.md`, `INDICE_ENTREGA.md`, `VERIFICACION_*.md`, `AUDITORIA_v2.md`, `CAPTURAS_PENDIENTES.md` y
`LEEME_REVISION_MONTU.md` (leer primero). Los v1 de Gemini quedaron intactos en `entrega/`. Yo corregí después 3 errores de la
auditoría (alcance del reemplazo de plan; que `POST /generar` NO usa `_ejecutar_generacion`; significado del ribete verde/gris) y
agregué la sección 6A (turnos, horarios y colación) al Manual de Usuario. **Nada de esto está commiteado en MontuMS.**

## 2. EL ERROR QUE DEBES CORREGIR EN LA PRIMERA PASADA (no lo resolví en la ventana anterior, por pedido de Montu)

**Lo que Montu pidió, literalmente:**
- 26-09: "esta información debe verse reflejada en la sección 'Averías', no tan solo en las máquinas de la Gantt."
- 27-09: "en la Gantt, si una máquina está detenida, semi-operativa, etc., debe aparecer visualmente en la máquina involucrada según lo
  que ya está desarrollado en el frontend, además EL MOTOR debe considerar esta información para la asignación de etiquetas
  (detenida = no se puede asignar trabajos), y además las máquinas de la sección Averías deben aparecer con esta información
  (**pero solamente 'completando' los datos que tenemos nosotros en la sección; si en la base de datos sale más detalle, no lo
  consideraremos, excepto que en un futuro lo solicite el Cliente**)."
- 28-09: "Efectivamente esa máquina [Curvadora 2 de Coronel] está detenida y sigue detenida. **Debe estar con la indicación de
  DETENIDA correspondiente en la Gantt.**"

**Lo que pasó:** en el prompt a CCa-23 (commit `5072159`) yo agregué por mi cuenta cosas que Montu NO pidió: en la tabla "Estado de
Maquinaria" de `GestorAverias.tsx`, un badge "Cubigest", el texto "registrada hace N días" y el texto de la falla que trae Cubigest en
la columna "Falla vigente / restricción" (para Curvadora 2 sale "máquina en Santiago", que es el `TextoIncidencia` de la notificación
69488); además la constante `AVERIA_CUBIGEST_CADUCIDAD_DIAS` (dormida, valor `None`). Después escribí a Montu "aparece DETENIDA, con la
nota 'máquina en Santiago', como pediste": **falso, él nunca pidió esa nota.**

**Qué hacer (con Montu, en la nueva ventana, ANTES de tocar código):**
1. Acordar con él la lista literal de qué se muestra y qué no. Puntos a confirmar explícitamente: (a) badge de fuente
   manual/Cubigest en la lista "Máquinas con Averías Activas" (lo incluí en mi propuesta del 26-09 —"marcado por fuente"— y él dijo
   "de acuerdo con tu propuesta"; probablemente se queda, pero confírmalo); (b) el texto de la falla de Cubigest en la columna "Falla
   vigente / restricción" (¿completa el campo "síntoma" que ya existe, o se quita?); (c) "registrada hace N días" (NO pedido: por
   defecto, quitar); (d) constante de caducidad (NO pedida: por defecto, quitar o dejarla claramente fuera de la vista).
2. Implementar exactamente eso (lo más probable: `GestorAverias.tsx` + campos de `routers/averias.py`), con un CCa y bloque de
   "Requerimiento literal" + "NO hagas".
3. Verificar **visualmente** (captura o revisión de Montu) que la fila de Curvadora 2 y de Línea Corte Coronel en el Gantt muestra
   DETENIDA. Hoy lo verifiqué solo por API/código, no en pantalla. (Mecanismo: `estadoCubigest` en `GestorProgramacion.tsx` sale de
   `metadata.maquinas_detenidas` del plan + `GET /api/averias/estado-maquinas`, ya unificado.)
4. Corregir el párrafo que agregué el 28-09 en `docs/entrega/v2/MANUAL_USUARIO_SPP.md` sección 3.6 ("Actualización 28-09
   (`5072159`)…" que menciona el badge "Cubigest" y "registrada hace N días") para que describa lo que quede realmente. Corregir
   también la entrada de `LOG_CAMBIOS_2026.md` del 28-09 y la fila CCa-23 del tablero, que repiten esas frases.

## 3. Estado REAL de infraestructura y código ahora mismo — VERIFÍCALO, no lo asumas

- **Producción (contenedores):** construidos desde `master` `5072159` (~09:35). `ssh TO "echo PING"` primero; `docker compose ps`.
- **OJO — el checkout de TO NO está en `master`:** está en la rama `unificar-generacion-auto-manual` (commit `332f98c`, de CCa-24),
  sin push ni merge ni deploy. **Un `docker compose build` ahora empaquetaría el working tree de esa rama.** Antes de cualquier
  rebuild, asegúrate de qué rama está checkeada y de que es lo que quieres desplegar (`git branch --show-current`). El working tree
  además arrastra `AGENTS.md`/`HARNESS.md` modificados y archivos sueltos preexistentes que NO son de estas tareas (no los incluyas
  en commits: `git add` archivo por archivo).
- **CCa-24 "unificar generación auto/manual" (rama `unificar-generacion-auto-manual`)** — decisión de Montu ("vamos con eso"). Terminó:
  función compartida `routers/programacion.py::ejecutar_pipeline_generacion` que llaman `generar_programacion` y
  `main.py::_ejecutar_generacion`; el automático gana L1 (`jornada_asignacion_manual`), posiciones manuales (`programacion_manual`) y
  ajuste de duración B44a; fix de un bug (el automático vaciaba en memoria TODOS los eventos de la sucursal sin filtrar turno/fecha);
  82/82 tests; informe `docs/agentes/CCa_unificar_generacion_20260928.md` en el repo de TO. **PENDIENTE: revisar su diff (yo no lo
  revisé), decidir merge/deploy (Montu: agrupar con los arreglos de su QA para un solo deploy) y resolver 3 dudas abiertas del
  informe:** (1) `programacion_detalle`/`system_logs` no se actualizan en la corrida automática (laguna preexistente); (2) hallazgo
  mayor: el automático usaba otra fuente de etiquetas (`_obtener_pids_pendientes`, Cubigest directo, lanza error si Cubigest cae) que el
  botón (`_obtener_pids_pendientes_optisteel`, Cuadro OptiSteel, fail-open); al unificar, el automático pasa a la del botón: una caída
  de Cubigest ya no queda como `resultado='error'` en `log_planificacion_auto` (queda como 0 etiquetas); (3) `bolsa_json` se persiste
  ahora también en el automático (ampliación no pedida). Tras el deploy hay que actualizar Guía Rápida, Manual de Usuario (FAQ 2 y
  sección 4/9), Manual Técnico 4.7/8.2 y LEEME (hallazgo 3), porque el comportamiento descrito cambia.
- **Graphify (regla dura):** snapshot `~/graphify-workspace/optifierro` (Mac Studio; es un clon DESECHABLE, no se commitea ahí). Estado
  actual: HEAD `5072159`, `built_at_commit` `5072159`, 1205 nodos — **pero el grafo incluye archivos de la rama sin mergear de CCa-24**
  (p. ej. `test_unificar_generacion.py`), o sea no corresponde exactamente a `master`. **Sí es necesario regenerarlo:** después de
  mergear/descartar CCa-24 y después de CADA cambio de código posterior (incluida la corrección de la sección 2):
  `cd ~/graphify-workspace/optifierro && git fetch origin master && git reset --hard origin/master && graphify update
  ~/graphify-workspace/optifierro` y comprobar que `graphify-out/graph.json` → `built_at_commit` == HEAD de `master` de TO. Cambios solo
  de documentación no requieren regenerarlo. Antes de tocar `main.py`/`programacion.py`/`motor_v2.py`, consultar impacto con
  `graphify affected|explain|query`.

## 4. Documentación — qué falta (revisado el 28-09 ~09:50; NO se resolvió en la ventana anterior, resolver aquí)

Todo en `/Users/montu/MontuMS/docs/`. Nada de lo siguiente está commiteado en MontuMS (`git -C /Users/montu/MontuMS status`;
`pendientes_sistema_planificador.md` aparece "MM" = con cambios staged y sin stage; hay otros archivos modificados que no son de
esta ventana —biblioteca/, INVENTARIO, REGLAS, procedimiento_trabajo_seguro, harness/— no los toques ni los commitees sin revisar).

1. **`MAPA_DECISIONES_SPP.md`** — solo se actualizó la sección 3c (UNI, VIGENTE). **Faltan decisiones nuevas** (crear secciones con IDs
   estables, con Regla / Por qué / Fuente-código / Fecha·quién / Manual, y sumar al Historial): etapas confirmadas en Cubigest
   (gris+inamovible+permanente, por etiqueta+máquina, vía `PIEZA_PRODUCCION`, tabla `etapa_congelada`); averías/estado efectivo
   (fuente única fusionada, "cualquiera excluye / gana la más restrictiva", `MAQ_NRO`, cada 30 min, sin caducidad —decisión de Montu);
   sincronización cada 30 min (scraper del Cuadro se mantiene; decisión de Montu de NO retirarlo); zoom/pan del Gantt (4 niveles);
   y, tras el deploy, la unificación auto/manual.
2. **`LOG_CAMBIOS_2026.md`** (prepend, ya tiene entradas hasta la del estado unificado 28-09). **Faltan:** (a) el **encendido de A4
   (`SYNC_HORARIO_ACTIVO=1` en `backend/.env`, 26-09)** —cambio de infraestructura fuera de git, no está en el LOG (`grep` da vacío)—;
   (b) entrada del paquete de manuales v2 (28-09 00:05–00:31, CCa desatendido + mis 3 correcciones + sección 6A); (c) la revisión y
   deploy de CCa-24 cuando ocurra; (d) la corrección de la sección 2.
3. **`tablero_coordinacion_spp.md`** — tiene filas CCa-19…CCa-23. **Faltan/están desactualizados:** fila de CCa-24; fila del
   pipeline de manuales v2; la fila "Gemini/Antigravity A14/A12" (dice "entregado 24-09, desactualizado", ya hay v2); la sección
   final "PENDIENTES CONSOLIDADOS" (dice "A14/A12 en espera, no tocar aún": ya no es cierto) → reescribirla con el estado del
   28-09; y el orden desordenado de filas de tabla (hay filas sueltas tras el bloque de deploy 25-09).
4. **`pendientes_sistema_planificador.md`** — A4, B6, B13, B39, B47, B48 ya cerrados. **Faltan:** A14/A12 (v2 escrito, pendiente de
   revisión de Montu/capturas/commit); backlog nuevo de esta ventana (ver sección 5); QA-A-04/05 y QA-B sin tocar; B43 abierto.
5. **`INVENTARIO_MAESTRO.md`** — `grep` no encuentra ninguno de: tablas nuevas (`etapa_congelada`, `averias_cubigest`, `sync_estado`),
   jobs nuevos (etapas completadas */30, averías Cubigest */30, sync horario */30), variable `SYNC_HORARIO_ACTIVO`, `estado_maquinas.py`,
   `useGanttZoom.ts`, la carpeta `docs/agentes/` dentro del repo de TO, el snapshot `graphify-workspace`. Revisar y actualizar.
6. **Manuales v2:** revisión de Montu (LEEME primero); capturas reales (hoy ya hay planes reales: Calama 267 eventos, Cerrillos 364,
   Coronel 105; lista en `v2/CAPTURAS_PENDIENTES.md`); ajustar lo que cambie por la sección 2 y por CCa-24; decidir el reemplazo de
   v1 por v2 (archivar v1, no borrar) y que Montu commitee `docs/entrega/v2/`; ajustar el Manual/Guía a lo que diga el correo que
   Montu envió a jefes y gerentes (pedirle el texto).
7. **`HARNESS.md`** — la fuente canónica es `~/MontuMS/harness/optifierro/HARNESS.md` (la copia de TO está sincronizada a mano y
   tiene 12 días de cambios sin commitear). Está desactualizado en 2 puntos: `_BODSUC_MAP` vive en `database_cubigest.py` (no en
   `motor_v2.py`) y el fix de reparto en paralelo ya está resuelto (24-09). Decisión de Montu pendiente.
8. **Informes de CCa:** los de TO viven en `docs/agentes/` del repo de TO (commiteados en cada merge) y deben copiarse a
   `/Users/montu/MontuMS/docs/agentes/` (LOG y tablero los referencian ahí). **Verificado el 28-09: solo 2 de 6 están copiados**
   (`CCa_gantt_etapa_gris_20260926.md`, `CCa_fix_ventana_averias_20260927.md`). **Faltan por copiar:**
   `CCa_averias_cubigest_20260926.md`, `CCa_gantt_zoom_20260926.md`, `CCa_averias_estado_unificado_20260928.md` y
   `CCa_unificar_generacion_20260928.md` (este último está en la rama sin mergear del checkout de TO). Copiar con
   `ssh TO "cat /c/Users/OptiFierro/Desktop/optifierro/docs/agentes/ARCHIVO" > /Users/montu/MontuMS/docs/agentes/ARCHIVO`.

## 5. Pendientes y decisiones abiertas (orden sugerido)

1. **Primero:** el QA de Montu. Él está haciendo QA "con detención y tranquilidad" y me prometió una lista de problemas "simples de
   solucionar" (no llegó a detallarlos en la ventana anterior). Pídele la lista y también el **texto del correo** que envió a jefes de
   planta y gerentes. Orden de trabajo lo define esa lista.
2. **Corrección de la sección 2** (Averías literal + Gantt DETENIDA).
3. **CCa-24:** revisar diff → decidir → merge/deploy junto con los arreglos del QA → regenerar Graphify → documentar.
4. **Decisión de Montu:** avería nueva a media jornada — hoy las cajitas ya asignadas se quedan en la máquina detenida hasta que el jefe
   presione "Reprogramar" (está escrito así en el manual). Propuse un aviso en Programación ("COIL 14 M detenida con N cajitas
   asignadas → Reprogramar"; ya existe un banner parecido para averías manuales). Sin respuesta aún.
5. **Discrepancia de hebras en Calama:** la tabla `hebras` tiene 2 hebras en Carro de Corte (Ø8–16) y EURA 20_2 (Ø10); Montu ha dicho que
   Calama trabaja todo a 1 hebra. Una de las dos está mal y el Motor usa la tabla. Decide Montu; corregir en el Gestor de Máquinas.
6. **Explicar a Montu la Ficha Técnica (A12)** —él lo pidió ("luego me explicas"): es el formulario técnico que TO pide para el SPP
   (campos: stack, lenguaje, dependencias, bases de datos, infraestructura física y cloud, dependencias con otros sistemas, riesgos y
   normativas; criticidad MEDIA ya definida). Está en `v2/FICHA_TECNICA_SPP.md`; lo legal quedó como preguntas abiertas.
7. Decisiones menores del LEEME: actualizar `HARNESS.md`; fijar versiones en `requirements.txt`; respaldo automatizado de
   `optifierro_v2.db` (hoy no existe: solo copias manuales); confirmar que el ribete por soldabilidad es lo deseado.
8. **Abiertos de siempre:** B43 (QA visual del ribete de adelanto; hallazgo suelto de la Bolsa mostrando la cajita con la IT en vez de la
   Etiqueta); QA-A-04/05 (`agentes/QA_A_universo_20260924.md`); QA-B (badge "datos suficientes" engañoso, ton/hora bajo B26-B,
   `capacidad_mh` igual en las 3 plantas); pasada visual del zoom; cabo suelto CCa-5 (veredicto de B16 nunca registrado).
9. Mejoras anotadas sin diseñar: `sync_averias_cubigest` no registra error/staleness como sí lo hace `sync_estado`; Fase 3 (B40, B41).

## 6. Herramientas y patrones (para operar sin redescubrirlos)

- **Desktop Commander** (shell del Mac Studio): `start_process`, `read_file`, `write_file` (sin `if_version`), `edit_block` (params
  `file_path`, `old_string`, `new_string`; el genérico `str_replace` es del sandbox, no sirve para archivos del Mac). Para el repo de TO:
  `ssh TO "..."` (alias con clave `id_optifierro`, nunca la IP directa); `MSYS_NO_PATHCONV=1` para `docker cp/exec/run -v` con rutas Linux
  desde Git Bash, y ruta Windows explícita (`C:/Users/...`) en `-v` o el montaje queda vacío en silencio.
- **Lanzar CCa:** escribir el prompt en `/tmp/xxx.txt` y `nohup /Users/montu/.local/bin/claude --dangerously-skip-permissions -p "$(cat
  /tmp/xxx.txt)" > /tmp/out.txt 2>&1 < /dev/null &`; verificar con `ps -p PID`; el proceso termina al entregar (en modo `-p` no puede
  conversar: si le dejas ambigüedad, termina preguntando y sale → en el prompt dile **"no hagas preguntas, decide y documenta"**).
  Para trabajo desatendido: script con pasos secuenciales + `timeout` + `caffeinate -i` (ver `/tmp/manuales_pipeline.sh`).
  Un solo CCa a la vez sobre el checkout de TO (comparten working tree y ramas). CCa hace commits locales en rama, sin push.
- **Deploy (tras merge fast-forward a `master`, push, y comprobar la rama del checkout):** `docker compose build --no-cache backend
  frontend && docker compose up -d --force-recreate backend frontend` (las variables de `.env` solo se recargan con `--force-recreate`).
  Verificar con `docker compose logs backend --tail`, `curl` a `http://127.0.0.1:8001/api/...` dentro de TO y `http://127.0.0.1:3001/`.
- **Cubigest** es SOLO LECTURA (AR-002). Consultas ad-hoc: `docker exec optifierro-backend python -c "from database_cubigest import
  cubigest_db; ..."`. **Hoy es lunes 28-09**: L-V corren las generaciones automáticas; sábado y domingo no hay trabajo (Gantt vacío es normal).

## 7. Qué hacer al recibir este prompt

1. `ssh TO "echo PING"`; `git branch --show-current` y `git log -1 --oneline` en el checkout de TO (esperado: rama
   `unificar-generacion-auto-manual`, commit `332f98c`); `docker compose ps`.
2. Lee `LEEME_REVISION_MONTU.md` (v2) y la sección "PENDIENTES CONSOLIDADOS" del tablero (sabiendo que está desactualizada, ver 4.3).
3. Saluda breve y pídele a Montu: (a) su lista de QA, (b) el texto del correo enviado a jefes y gerentes, (c) su respuesta a la lista literal
   de la sección 2 (qué se muestra en Averías), (d) si "desplegar e iterar" sigue vigente ahora que hay usuarios potenciales.
4. No arranques cambios de código antes de tener esas respuestas; sí puedes ir avanzando en la documentación de la sección 4 si Montu lo autoriza.
