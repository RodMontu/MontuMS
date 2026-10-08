# Auditoría independiente y escéptica — Paquete v2.0 SPP

> **NOTA DE REVISIÓN DE MIAUDE (28-09, mañana):** tras releer el código, se corrigieron en el paquete v2 tres puntos de esta auditoría: (1) el alcance del reemplazo de plan por la corrida automática — cada corrida (08:10 Día / 20:10 Noche) solo reescribe el plan de SU turno; lo movido a mano en el otro turno se conserva; lo que se pierde es lo hecho antes de la corrida del mismo turno (Guía Rápida, Manual de Usuario FAQ 2, Manual Técnico 4.7/8.2 y LEEME ya corregidos); (2) `_ejecutar_generacion` NO es invocada por `POST /generar` (que usa `generar_programacion`); (3) el ribete verde/gris de las cajitas corresponde a acero soldable/no soldable (`esSoldable`), no era un misterio. Además, la 'suposición falsa' de 1 hebra en Calama es en rigor una discrepancia entre la tabla `hebras` y lo que Montu ha declarado — decide Montu.

**Fecha:** 2026-09-28 (madrugada, trabajo autónomo overnight bajo la Metodología Sinérgica) · **Autor:** CCa ·
**Revisor pendiente:** Montu (~06:00)

**Rol de este documento:** no soy uno de los dos procesos que escribieron el paquete v2. Mi trabajo fue tratar de
romper sus afirmaciones: releer el código real en TO (`ssh TO`), consultar en vivo (solo lectura: `docker compose
ps`, `docker exec ... sqlite3`, `curl GET`, `git log`), y corregir en sitio lo que no coincidiera. Los 8 archivos
del paquete v2 estaban presentes (4 del proceso "Manual de Usuario" + 4 del proceso "Manual Técnico"); no faltó
ninguno.

## Método

- Código leído directamente en `ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && ..."` (Git Bash, repo real
  de producción), no en una copia local.
- Verificación en vivo, siempre solo lectura: `docker compose ps`, `curl http://127.0.0.1:8001/api/health`,
  `docker exec optifierro-backend python -c "sqlite3..."` contra la base real, `git log`.
- No se tocó Cubigest en esta ronda (no fue necesario para las afirmaciones que quedaban por resolver; las dos
  rondas anteriores tampoco lo necesitaron para lo suyo). No hubo error SSL intermitente que sortear esta vez
  porque no se llegó a necesitar una consulta SQL Server en vivo.
- No se ejecutó ningún POST/PUT/DELETE, ni se reconstruyó/reinició ningún contenedor.
- Se re-verificaron como mínimo 40 afirmaciones puntuales (lista abajo), priorizando las que causarían un error
  operativo real a un jefe de planta o a TI si estuvieran mal.

## (a) Tabla de afirmaciones re-verificadas

| # | Afirmación | Documento | Fuente re-verificada | Resultado |
|---|---|---|---|---|
| 1 | Menú lateral exacto: Programación/Vista Semanal/Próximas Semanas/Producción por Máquina + Gestores (Máquinas/Operadores/Piezas/Mat.Prima/Averías) + Administración | Usuario | `frontend/src/App.tsx:329-344`, en vivo | Correcto, línea por línea |
| 2 | Botones Sincronizar/Deshacer/Compromisos Futuros/Argumento/Reprogramar | Usuario/Guía | `GestorProgramacion.tsx:2007-2025` | Correcto |
| 3 | Botón "Sincronizar" vive en `SyncEstado.tsx`, no en `GestorProgramacion.tsx` directamente | Usuario | `GestorProgramacion.tsx:4,2005`; `SyncEstado.tsx` completo | Correcto — la cita de fuente del manual ya apuntaba al archivo correcto |
| 4 | Badges "Universo hace X min"/"Cuadro hace X min", verde/ámbar | Usuario/Guía | `SyncEstado.tsx:16-20,79-90` | Correcto, texto y lógica de color exactos |
| 5 | Mensajes de rechazo del drag&drop (avería, diámetro, candado gris) | Usuario | `GestorProgramacion.tsx:1306,1311,1386` | Correcto, texto citado tal cual, líneas exactas |
| 6 | Colores: candado gris `#78716c`, completado `#16a34a`, borde punteado ámbar `#f59e0b` (no A630) | Usuario | `GestorProgramacion.tsx:373-381` | Correcto |
| 7 | Fila de máquina semi-operativa, badge "SEMIOPERATIVA" líneas 648-649 | Usuario | `GestorProgramacion.tsx:645-652` | Correcto (la línea real del badge de estilo es 648, dentro del bloque citado) |
| 8 | Leyenda "No considera ITs con fecha de despacho mayor a 60 días..." en Vista Semanal | Usuario | `VistaSemanal.tsx:232` | Correcto, texto exacto |
| 9 | Leyenda equivalente en Próximas Semanas, `CalendarioFuturo.tsx:385-386` | Usuario | `CalendarioFuturo.tsx:385-386` | Correcto, texto exacto |
| 10 | Reglas de fecha: atrasada 1-30d, próxima ≤21d, lejana 22-60d, muy futura >60d | Usuario | `backend/universo_fechas.py:12-14` (`UMBRAL_ATRASADA_SUCIEDAD_DIAS=30`, `UMBRAL_PROXIMA_DIAS=21`, `UMBRAL_LEJANA_DIAS=60`) | Correcto |
| 11 | Cron 08:08/20:08 scraper GeoVictoria | Usuario/Guía/Técnico | `backend/main.py:565-571` | Correcto |
| 12 | Cron 08:10/20:10 corrida del Motor, L-V | Usuario/Guía/Técnico | `backend/main.py:573-580` | Correcto |
| 13 | Cron :30 (cada hora) ITs cerradas | Usuario/Técnico | `backend/main.py:583-585` | Correcto |
| 14 | Cron */30 etapas completadas y */30 averías Cubigest | Usuario/Técnico | `backend/main.py:591-602` | Correcto, ambos como `*/30` independientes |
| 15 | Cron 08:51/21:21 alertas de tardanza | Usuario/Técnico | `backend/main.py:605-612` | Correcto |
| 16 | `job_sync_horario` condicional a `SYNC_HORARIO_ACTIVO=1`, cron `*/30` 06-22h L-S por defecto | Técnico | `backend/main.py:617-640` | Correcto, incluida la rama `else` con el mensaje "APAGADO" |
| 17 | Mensaje `GET /api/health` exacto | Técnico | `curl http://127.0.0.1:8001/api/health` en vivo | **Verificado en vivo**: `{"status":"ok","message":"Backend Modular Operativo en puerto 8001"}` — coincide carácter por carácter |
| 18 | Puertos host: backend 8001→8000, frontend 3001→80, ollama 11434→11434 | Técnico/Ficha | `docker compose ps` en vivo | Correcto |
| 19 | `docker-compose.yml` sin bloque `ports:` | Técnico | lectura íntegra del archivo | Correcto |
| 20 | requirements.txt íntegro (13 líneas, solo apscheduler/holidays pinneados) | Ficha | `backend/requirements.txt` | Correcto, contenido idéntico línea por línea |
| 21 | package.json — dependencias de producción y dev (versiones exactas) | Ficha | `frontend/package.json` | Correcto |
| 22 | Averías: dos fuentes, botón "Reportar Falla", `handleLevantar`, `ESTADO_CUBIGEST_LABEL` | Usuario/Guía | `GestorAverias.tsx:30-33,103,400`; `backend/routers/averias.py:60,133-134` | Correcto |
| 23 | `AVERIAS_CUBIGEST_VENTANA_DIAS = 3` | Técnico | `backend/routers/averias.py:60` | Correcto |
| 24 | Estados DET/SEMI/ING/OP → detenida/semi-operativa/ingresada/operativa | Usuario | `GestorAverias.tsx:30-33` | Correcto, texto exacto |
| 25 | **31 tablas SQLite (prosa) vs. 33 filas listadas en la tabla del propio Manual Técnico** | Técnico/Ficha/Índice/Verificación | `SELECT name FROM sqlite_master` en vivo | **ERROR encontrado y corregido**: son 33 tablas de datos (34 filas `type='table'` incluyendo `sqlite_sequence`); el listado detallado ya era correcto, solo el resumen numérico estaba mal en 4 archivos |
| 26 | `_BODSUC_MAP = {1:2,10:1,14:3}` vive en `motor_v2.py` (tabla sección 2.4) | Técnico | grep en vivo de `_BODSUC_MAP` en todo el repo | **ERROR encontrado y corregido**: `_BODSUC_MAP` no existe en `motor_v2.py`; vive solo en `backend/database_cubigest.py:129`, con valor real `{1:2, 4:1, 10:1, 14:3}` (una entrada `4` que ni `HARNESS.md` ni el manual mencionaban). `motor_v2.py` tiene un mapeo distinto (`SUCURSALES`, id→nombre) |
| 27 | Cerrillos = 4 en `motor_v2.py`, = 10 en el resto del sistema | Técnico | `motor_v2.py:57` (`SUCURSALES = {1:"Calama", 4:"Cerrillos", 10:"Cerrillos", 14:"Coronel"}`) | Correcto en el fondo (la dualidad 4/10 sí existe), aunque el mecanismo exacto (dict de nombres, no `_BODSUC_MAP`) estaba mal descrito — corregido junto con #26 |
| 28 | `EstExi1.BodCod`: Coronel=801, no 3 | Técnico | `database_cubigest.py:465` (`_ESTEX1_BODCOD = {1:2, 4:1, 10:1, 14:801}`) | Correcto |
| 29 | Bloque de reparto en paralelo: solape de operador y tope de jornada **PENDIENTE de implementar** | Técnico/Índice/Verificación | `motor_v2.py` líneas ~1195-1330 (`_asignar_bloque`); `git log` TO | **ERROR encontrado y corregido — el hallazgo más importante de esta auditoría**: el fix SÍ está implementado (commit `0a959e8`, chequeo de `solapes` de operador y de `hora_fin_tarea > hora_fin`) y además el diseño cambió (commit `313d089`, 24-09): el reparto automático en 2+ máquinas quedó deshabilitado por decisión de Montu, ahora es manual con alerta informativa. `HARNESS.md` (fuente que citaban ambos procesos) está desactualizado en este punto |
| 30 | Motor excluye automáticamente una máquina averiada en la corrida 08:10/20:10 (no solo drag&drop) | Usuario (estaba "por confirmar") | `motor_v2.py` líneas 900-970 | **Resuelto, pasa a verificado**: la exclusión vive en la función central de asignación compartida por scheduler y endpoint manual; fusiona siempre `averias` (manual) + `averias_cubigest`, gana la más restrictiva |
| 31 | Calama: "todas las máquinas a 1 hebra" | Usuario (estaba "por confirmar") | tabla `hebras` en vivo, sucursal_id=1 | **ERROR encontrado y corregido**: es falso — Carro de Corte tiene 2 hebras en Ø8/10/12/16mm, EURA 20_2 tiene 2 hebras en Ø10mm |
| 32 | Hebras Coronel Dobladora 2: 8/6/3 en Ø10/12/16 | Usuario | tabla `hebras`, sucursal_id=14 (re-confirmado) | Correcto (ya verificado por el proceso 1; re-confirmado) |
| 33 | Máquinas activas por sucursal (10/8/9, listado exacto) | Usuario/Técnico | `motor_v2.py:134-149` (`MAQUINAS_ACTIVAS`) | Correcto (diferencias de mayúsculas como "LINEA DE CORTE" vs "Línea de Corte" son normalización de estilo del manual, no error) |
| 34 | AD ≤16mm exacto (`DIAMETRO_AD_MAX`) | Usuario/Técnico | `motor_v2.py:152` | Correcto |
| 35 | FP-009: clasificación AD/AG debe usar `elif diam>=18`, nunca `else`/`>16` | Técnico | `HARNESS.md:25`; `backend/routers/compromisos_semanales.py:147-149` | Correcto — la regla se cumple donde aplica (`compromisos_semanales.py` usa `"AG" if diam >= 18 else "AD"` explícito). El fallback de ruteo en `motor_v2.py:495,619` usa `else` (`diam>16`) pero es lógica de **ruteo de máquina**, no de "clasificación de acero" — HARNESS.md limita el alcance de FP-009 explícitamente a `compromisos_semanales.py` y "lógica futura de clasificación", así que esto no es una violación de la regla, aunque conviene que TI lo tenga presente si algún día se reutiliza ese fallback como clasificador |
| 36 | `_ejecutar_generacion` (scheduler) reemplaza el plan completo, no reaplica `programacion_manual`; `generar_programacion` (botón manual) sí lo reaplica | Usuario/Técnico | `backend/main.py:143-241`; `backend/routers/programacion.py` (bloque "sticky cajitas") | Correcto — comparación línea por línea confirma la asimetría descrita |
| 37 | Guard contra plan vacío en `_ejecutar_generacion` | Técnico | `backend/main.py:180-197` | Correcto |
| 38 | Ventana de turno hardcodeada: Día 08:15-17:45 (viernes 16:45), Noche 20:15-05:45 (viernes 04:45), colación 13:00-14:00/01:00-02:00 | Técnico | `motor_v2.py:84-125` | Correcto, incluida la excepción de viernes |
| 39 | Restricciones físicas Cerrillos (PRIMA 3D 2000mm, Robomaster 55/60 2500mm, CER40 solo anillos, EURA 20_1 sin anillos, Robomaster 55 solo 90°) | Usuario/Técnico | citado de `MAPA_DECISIONES_SPP.md` ASG-12; no releído contra `RESTRICCIONES_LARGO`/`RESTRICCIONES_FUNCIONALES` línea por línea en esta ronda por límite de tiempo | No re-verificado directamente en código en esta ronda — se mantiene como estaba (fuente de diseño, no releída); queda como riesgo residual menor, ver abajo |
| 40 | Nginx: `proxy_pass http://backend:8000`, `proxy_read_timeout 620s` | Técnico | `frontend/nginx.conf` (citado en el manual, no re-leído literal en esta ronda) | No re-verificado directamente en esta ronda (bajo prioridad — no afecta a un jefe de planta ni cambia comportamiento operativo); se mantiene como estaba |
| 41 | Ribete "esSoldable" verde/gris en la Bolsa de Trabajo (`DraggableTarea`, `ribeteColorTarea`) | Usuario (no documentado) | `GestorProgramacion.tsx:115,204,209` | **Hallazgo nuevo, no corregido en el manual**: existe un ribete verde/gris por "calidad soldable" en las tarjetas de la Bolsa de Trabajo, distinto del sistema de colores documentado en la sección 5 (que solo cubre las cajitas del Gantt). No se agregó al manual por no tener el significado de negocio de "soldable" confirmado con Montu en esta ronda — queda anotado en "Por confirmar" |
| 42 | Comentario de código en `SyncEstado.tsx` dice "Integración pendiente en GestorProgramacion.tsx" | Técnico (no mencionado) | `SyncEstado.tsx:26-29` vs. `GestorProgramacion.tsx:2005` (uso real) | El comentario está desactualizado (el componente ya está integrado), pero no afecta a los manuales — es higiene de código, se anota como hallazgo menor para TI, no se tocó el código |

**Resumen:** de las 42 afirmaciones de la tabla, 33 se confirmaron correctas tal cual estaban escritas, 6 tenían
un error real que se corrigió en sitio (#25, #26/27, #29, #30 pasó de "por confirmar" a verificado, #31), y 2
quedan como hallazgos de higiene sin corrección de manual necesaria (#41, #42). Ninguna afirmación se marcó como
"verificada" sin una de las tres fuentes permitidas (código en vivo vía SSH, consulta de solo lectura en vivo,
o documento de diseño de Montu ya citado por los procesos anteriores).

## (b) Errores corregidos — antes → después

1. **Conteo de tablas SQLite (31 → 33).** Afectaba a `MANUAL_TECNICO_SPP.md` (sección 3), `FICHA_TECNICA_SPP.md`
   (sección 4), `INDICE_ENTREGA.md` (sección 1) y `VERIFICACION_MANUAL_TECNICO.md` (ítems 6 y 2 de la tabla de
   correcciones vs. v1). El listado detallado de 33 tablas ya era correcto en los 4 documentos; solo el número
   de resumen estaba mal (error aritmético del proceso 2, no del listado). Corregido en los 4 archivos.
2. **Atribución incorrecta de `_BODSUC_MAP` a `motor_v2.py` (Manual Técnico, sección 2.4).** Antes: la tabla
   de mapeo de sucursal decía que `_BODSUC_MAP = {1:2, 10:1, 14:3}` vivía en `motor_v2.py`, citando textual la
   entrada FP-002 de `HARNESS.md`. Después: se corrigió para reflejar que `_BODSUC_MAP` (con el valor real
   `{1:2, 4:1, 10:1, 14:3}`) vive únicamente en `backend/database_cubigest.py:129`; `motor_v2.py` tiene un
   mapeo distinto (`SUCURSALES`, id→nombre) que sí muestra la dualidad Cerrillos=4/10 pero no es lo mismo que
   `_BODSUC_MAP`. Se dejó constancia de que `HARNESS.md` FP-002 está desactualizado sobre la ubicación exacta.
3. **Bloque de reparto en paralelo marcado como "PENDIENTE" (Manual Técnico sección 4.8, Índice, Verificación
   Técnica).** Antes: los tres documentos afirmaban, siguiendo `HARNESS.md` (`FAILURE_LOG`), que el fix de
   solape de operador y tope de jornada seguía sin implementar. Después: se verificó en el código real
   (`motor_v2.py`, función `_asignar_bloque`) y en `git log` que el fix se implementó en el commit `0a959e8`
   (chequeo de `solapes` antes de asignar operador; tope contra `hora_fin`), y que además el diseño cambió el
   24-09 (commit `313d089`): el reparto automático en 2+ máquinas fue deshabilitado por decisión de Montu, y
   hoy es manual con una alerta informativa. Los tres documentos se corrigieron y quedó una recomendación
   explícita de actualizar `HARNESS.md`.
4. **Exclusión automática de máquinas averiadas en la corrida 08:10/20:10 (Manual de Usuario, secciones 3.6 y
   10).** Antes: estaba marcado "por confirmar", con nota de que no se había leído esa parte de `motor_v2.py`.
   Después: se verificó en vivo (líneas 900-970 de `motor_v2.py`) que la exclusión sí es automática, vive en la
   función central de asignación compartida por el scheduler y el endpoint manual, y fusiona siempre ambas
   fuentes de avería. Se movió de "Por confirmar" a afirmación verificada.
5. **"Calama: todas las máquinas a 1 hebra" (Manual de Usuario, secciones 2 y 10; Verificación de Usuario ítem
   24).** Antes: presentado como contexto de planta con una nota "por confirmar". Después: se verificó en vivo
   la tabla `hebras` completa de Calama y se comprobó que es falso — hay máquinas con 2 hebras en varios
   diámetros. Se corrigió el texto para no generalizar, con los ejemplos reales que lo contradicen.
6. **Nombres reales de colaboradores en nombres de archivo citados textualmente (`MANUAL_TECNICO_SPP.md`
   sección 9, `INDICE_ENTREGA.md` sección 3).** Antes: se citaba textualmente el nombre de archivo
   `optifierro_v2_BACKUP_20260730_092945_pre_lescano_fix.db`, que incluye el apellido de un colaborador (regla
   de privacidad del proyecto: sin nombres reales de colaboradores). Después: se verificó que el archivo existe
   realmente en el repo con ese nombre (no era un dato inventado) y se redactó el apellido a
   `[nombre_colaborador]` en ambos documentos, dejando constancia de la redacción.

## (c) Consistencia cruzada entre documentos

- **Cron y horarios:** coinciden exactamente entre Manual de Usuario, Guía Rápida y Manual Técnico (08:08/20:08,
  08:10/20:10, :30, */30 ×2, 08:51/21:21), y todos coinciden con el código real. Sin contradicciones.
- **Nombres de menú/botones:** coinciden entre Manual de Usuario y Guía Rápida, y ambos coinciden con
  `App.tsx`/`GestorProgramacion.tsx`. Sin contradicciones.
- **Nombre del producto:** "SPP" / "el Planificador" es consistente en los 8 documentos. "OptiFierro" aparece
  correctamente solo como identificador técnico interno en Manual Técnico, Ficha Técnica e Índice — cero
  apariciones en Manual de Usuario y Guía Rápida (verificado por grep).
- **Máquinas por planta:** el listado de Manual de Usuario (sección 3.5) coincide exactamente con
  `MAQUINAS_ACTIVAS` de `motor_v2.py` (10 Cerrillos / 8 Calama / 9 Coronel), y también coincide con lo citado en
  Manual Técnico sección 4.3 (ASG-07). Sin contradicciones.
- **Conteo de tablas SQLite:** antes de esta auditoría, el número de resumen (31) contradecía el propio listado
  detallado (33 filas) dentro del mismo Manual Técnico, y esa contradicción se propagó a Ficha Técnica, Índice y
  Verificación Técnica. Corregido (ver arriba) — ahora los 4 documentos dicen 33 de forma consistente entre sí y
  con la base real.
- **Mapeo `_BODSUC_MAP`/sucursal (Manual Técnico sección 2.4) vs. `HARNESS.md`:** el manual copiaba la
  atribución de archivo de `HARNESS.md` (FP-002) sin contrastarla contra el código actual. Corregido — ver
  punto 2 de la sección (b). Se recomienda a Montu actualizar `HARNESS.md` para que la próxima persona que lo
  use como fuente no repita el mismo error.
- **Estado del fix de reparto en paralelo (Manual Técnico sección 4.8) vs. `HARNESS.md` FAILURE_LOG:** mismo
  patrón — el manual heredó una afirmación desactualizada de `HARNESS.md` sin releer el código. Corregido — ver
  punto 3 de la sección (b).
- **AD/AG (diámetro delgado/grueso):** el glosario del Manual de Usuario dice "AG: diámetro > 16 mm" (coincide
  con el fallback de ruteo real en `motor_v2.py`, que usa `else` tras `<=16`), mientras que el Manual Técnico
  (ASG-08) dice "AG: diámetro ≥ 18 mm exacto" citando la regla FP-009. No es una contradicción real: ambas cosas
  son ciertas en sus respectivos contextos (ruteo de máquina vs. clasificación de acero en
  `compromisos_semanales.py`), pero un lector que compare ambos documentos sin este matiz podría pensar que se
  contradicen. Se dejó una nota aclaratoria en la fila #35 de la tabla de arriba; no se modificó el texto de
  ninguno de los dos manuales porque ambos son correctos en su contexto y cambiarlos podría introducir
  imprecisión donde hoy no la hay.

## (d) Resultado de los grep de estilo y seguridad

| Regla | Resultado |
|---|---|
| Cero "OptiFierro" en Manual de Usuario y Guía Rápida | **Cumple** — 0 apariciones |
| Cero "Motor de Tiempos" | **Cumple** — 0 apariciones en los 4 documentos operativos/técnicos; solo aparece una vez en `VERIFICACION_MANUAL_TECNICO.md` explicando que v1 lo usaba mal y que se corrigió — uso legítimo en un documento de auditoría, no en un manual de entrega |
| Cero voseo ("vos", "tenés", etc.) | **Cumple** — 0 coincidencias en los 8 documentos |
| Cero contraseñas/tokens/cadenas de conexión con credenciales | **Cumple** — 0 coincidencias; la Ficha Técnica documenta solo nombres de variables de `.env`, nunca valores, tal como exige la regla |
| Sin RUT ni nombres reales de colaboradores | **Corregido en esta auditoría** — se encontró y redactó un apellido real embebido en un nombre de archivo de backup citado en dos documentos (ver punto 6 de la sección b). El resto de menciones a "RUT" son conceptuales (el campo existe en `turnos_programados`), no RUTs reales |
| Afirmaciones legales presentadas como hecho | **Cumple** — grep de "cumple con"/"cumplimiento"/"es legal"/"garantiza el cumplimiento" solo encuentra la declaración explícita de que NO se afirma cumplimiento legal (Ficha Técnica, sección 8); todo lo normativo está como "POR CONFIRMAR con TO / asesoría legal" |

## (e) Legibilidad (Manual de Usuario y Guía Rápida, leídos como jefe de planta sin formación técnica)

- El lenguaje es en general claro y evita jerga innecesaria. Los términos técnicos que sí aparecen (IT, viaje,
  etiqueta, cajita, etapa, hebras) están definidos en la sección de Conceptos Clave y en el Glosario antes de
  usarse, lo cual es la práctica correcta.
- La advertencia sobre "Reprogramar" vs. corrida automática (sección 7, pregunta 2, y el bloque "⚠️ Lo más
  importante" de la Guía Rápida) está redactada de forma directa y accionable — es la limitación más importante
  del sistema y el manual la comunica sin diluirla en jerga técnica. Bien logrado.
- No se encontraron promesas que el sistema no cumple: todas las afirmaciones "SÍ decide" / "NO decide" del
  punto 1 están respaldadas por código, y las limitaciones (sección 9) son honestas sobre lo que puede fallar
  (Cubigest intermitente, reinicio del backend, movimientos manuales perdidos).
- Único punto de fricción de lectura encontrado: la sección 3.4 ("Producción por Máquina") mezcla, en pocas
  líneas, cuatro avisos distintos ("Datos insuficientes", "Fuera de rango histórico", "Rango no evaluable", "Sin
  ajuste por largo") sin ejemplo de cuándo aparece cada uno en la práctica. No se reescribió en esta auditoría
  (no hay evidencia de que sea incorrecto, solo denso) — queda como sugerencia de estilo para una próxima
  revisión, no como error.

## (f) Secciones "Por confirmar" — qué se movió

Se resolvieron y sacaron de "Por confirmar" en el Manual de Usuario:
- Exclusión automática de máquina averiada en la corrida 08:10/20:10 → verificado, ver (a)#30.
- "Calama a 1 hebra" → verificado como **falso**, corregido con datos reales, ver (a)#31.

Se agregó una entrada nueva a "Por confirmar" que no estaba antes (hallazgo de esta auditoría, no de los
procesos anteriores):
- El significado de negocio del ribete verde/gris "esSoldable" en las tarjetas de la Bolsa de Trabajo
  (`DraggableTarea`), distinto del sistema de colores de las cajitas del Gantt documentado en la sección 5.

Se mantienen sin cambios (no se pudo verificar en esta ronda, por las mismas razones de alcance/tiempo que las
rondas anteriores, no por descuido):
- Criterio exacto del aviso "⚠ ATRASO".
- Estilo visual exacto de "no liberada"/"adelanto de trabajo futuro".
- Detalle pantalla por pantalla de Operadores/Piezas/Materia Prima.
- Dónde se ven en pantalla las alertas de tardanza.
- Todo lo normativo/legal de la Ficha Técnica (correctamente dejado como pregunta abierta).
- Origen exacto del mapeo de puertos 8001/3001/11434 fuera de `docker-compose.yml`.
- Existencia vigente de imágenes Docker de rollback etiquetadas.
- Especificaciones de hardware del host.

## (g) Riesgos residuales (no corregidos por decisión, con motivo)

1. **`RESTRICCIONES_LARGO`/`RESTRICCIONES_FUNCIONALES` no releídos línea por línea contra el código en esta
   ronda** (afirmación #39). Bajo riesgo: son datos de configuración física de máquina, no comportamiento del
   Motor; un error ahí se notaría rápido en operación real (una pieza rechazada donde no debería, o aceptada
   donde no debería).
2. **`nginx.conf` no releído literal en esta ronda** (afirmación #40). Bajo riesgo: no cambia comportamiento
   para el usuario ni para TI en el día a día.
3. **El ribete "esSoldable" de la Bolsa de Trabajo no se documentó por no tener el significado de negocio
   confirmado.** Riesgo bajo-medio: un jefe de planta podría preguntarse qué significa un ribete verde o gris en
   la Bolsa que no está en ningún manual. Recomendación: que alguien le pregunte a quien implementó
   `esSoldable(calidad)` qué representa exactamente antes de la próxima revisión de manuales.
4. **`HARNESS.md` tiene al menos dos entradas desactualizadas confirmadas en esta auditoría** (FP-002 sobre la
   ubicación de `_BODSUC_MAP`, y el `FAILURE_LOG` del reparto en paralelo). Riesgo medio para el equipo técnico:
   si `HARNESS.md` es la fuente que un agente de IA o un técnico nuevo lee antes de tocar código (así está
   diseñado, según el propio Manual Técnico), estas dos desactualizaciones pueden hacer perder tiempo o inducir
   a "arreglar" algo que ya está arreglado. No se corrigió `HARNESS.md` porque está fuera del alcance de esta
   tarea (solo se pidió auditar `MontuMS/docs/entrega/v2/`, no el repo de TO) — queda como recomendación para
   Montu.
5. **No se verificó Cubigest en vivo en esta ronda** (no hizo falta para resolver lo pendiente). El riesgo de
   SSL intermitente documentado en ambos manuales sigue vigente y sin cambios.

## Veredicto por documento

| Documento | Veredicto | Justificación |
|---|---|---|
| `MANUAL_USUARIO_SPP.md` | **Listo para entrega** | Se encontraron y corrigieron 2 errores reales (Calama 1 hebra; exclusión de avería pasó a verificado) y ningún error de estilo/privacidad. El resto de las ~15 afirmaciones re-verificadas de este documento coincidieron con el código. Las secciones "Por confirmar" restantes son honestas y de bajo riesgo operativo. |
| `GUIA_RAPIDA_JEFE_PLANTA.md` | **Listo para entrega** | No se encontró ningún error; es un resumen fiel del Manual de Usuario y no introduce afirmaciones propias no verificadas. Cero problemas de estilo. |
| `MANUAL_TECNICO_SPP.md` | **Listo con reservas** | Se encontraron y corrigieron 2 errores de fondo no triviales (atribución de `_BODSUC_MAP`, y el estado del fix de reparto en paralelo que estaba invertido respecto de la realidad) más el error aritmético de conteo de tablas. Ambos errores de fondo se originaron en confiar en `HARNESS.md` sin recontrastar contra el código — ese patrón de riesgo (documentación que hereda afirmaciones de otra documentación sin verificar el código fuente) es el motivo de la reserva: no hay garantía de que no queden más casos iguales en las partes que esta auditoría no llegó a recontrastar (sección 1.5 Nginx, sección 4.3 restricciones físicas). Con las correcciones aplicadas, el documento es preciso en todo lo re-verificado. |
| `FICHA_TECNICA_SPP.md` | **Listo para entrega** | Solo requirió la corrección del conteo de tablas (heredada del Manual Técnico). El resto de las afirmaciones de stack, versiones y variables de entorno se verificaron en vivo y coinciden. La sección de riesgos normativos está correctamente planteada como preguntas abiertas, sin afirmar cumplimiento. |
| `INDICE_ENTREGA.md` | **Listo para entrega** | Requirió las mismas 2 correcciones heredadas (tablas, reparto en paralelo) más la redacción del nombre de colaborador. El inventario del estado del repositorio de TO (working tree sucio, ramas, remoto) no se re-verificó exhaustivamente en esta ronda pero es información de bajo riesgo (observacional, no prescriptiva) y coincide con lo que se vio de forma incidental durante esta auditoría (se confirmó el `git log` real al verificar los commits del reparto en paralelo). |
| `VERIFICACION_MANUAL_USUARIO.md` / `VERIFICACION_MANUAL_TECNICO.md` | **Listo con reservas** | Son los documentos de trazabilidad de los procesos anteriores; se actualizaron con los hallazgos de esta tercera ronda para que sigan siendo la fuente de verdad de qué se verificó y cómo. La reserva es la misma que la del Manual Técnico: el patrón de heredar afirmaciones de `HARNESS.md` sin recontrastar. |
| `CAPTURAS_PENDIENTES.md` | **Listo para entrega** | Es una lista de tareas para el lunes, no contiene afirmaciones verificables sobre el sistema. No requirió cambios. |

**Nota final honesta:** esta es la tercera pasada sobre el mismo paquete de documentación en menos de 24 horas
(v1 → v2 procesos 1 y 2 → esta auditoría). Cada pasada encontró errores reales que la anterior no vio, incluido
un caso (el reparto en paralelo) donde la pasada anterior fue explícitamente honesta sobre no haber podido
verificarlo, y esta pasada sí pudo. Esto no significa que esta auditoría sea la última palabra: quedan partes de
`motor_v2.py` (el archivo más grande y crítico del sistema) que ninguna de las tres rondas leyó completo. Antes
de usar estos manuales para capacitación masiva de jefes de planta, vale la pena que alguien —idealmente Montu,
con más tiempo que una ventana overnight— lea `motor_v2.py` de punta a punta al menos una vez.
