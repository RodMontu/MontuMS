# PROMPT DE CONTINUIDAD — Motor de Tiempos + coordinación con chat paralelo OF
**Fecha:** 2026-09-07, ~06:45 hrs
**Origen:** ventana coordinadora del Motor de Tiempos (Prompt 4 original + trabajo
de la noche del 6 al 7 de septiembre)
**Rol a asumir:** Mi TI. Tuteo chileno, RCA antes de parche, par intelectual.
**Motivo de este prompt:** Montu tiene dos ventanas de chat trabajando en
OptiFierro sin coordinación — esta (Motor de Tiempos) y otra en paralelo (trabajo
general de OF, incluye al menos un importador OptiSteel corrido hoy 09:09 hrs,
ver `LOGs accesos/sesion_20260907_090859_optisteel_importador.log` en el
Escritorio de TO). Se van a fusionar ambos prompts en una sola ventana para
coordinar, y luego posiblemente volver a separar en ventanas nuevas.

**Ventana de trabajo:** sin acceso a Cubigest entre ~07:45 y 18:00 hrs (lunes,
jornada laboral de TO) — cualquier tarea que toque la DB debe esperar a esa
hora, salvo trabajo de infraestructura propia (modelos locales, scripts,
documentación) que no requiere Cubigest.

---

## 1. Estado real del Motor de Tiempos a esta hora

**Fase 0 y Fase 1: CERRADAS.** Ver `~/MontuMS/docs/handoff_actual.md` (documento
vivo, fuente de verdad) sección 12 para el cierre formal. Resumen:
- Bug de agrupación (`dp.id` vs `dp.Etiqueta`) confirmado y corregido en
  `extractor_rutas_v2.py` (MT-03) — original intacto, luz verde de Montu para
  usarlo, evaluación pendiente cuando corra a escala.
- Join `PLC_IdEtiquetaTO = detallePaquetesPieza.id` confirmado (99,95% match).
- Informe de calibración PLC vs proxy: mediana 6,66min, media 735min, p80
  77,4min — domina ruido de instrumentación, no sesgo sistemático. Recomienda
  Opción 3 (proxy para priorizar, no cronometrar) en las 2 máquinas de mayor
  volumen del piloto (84%), Opción 4 (documentar límite) para el resto. Ver
  `docs/informe_calibracion_plc_proxy_20260906.md`.
- `IdMov = Movimientos.Id` confirmado 100%.
- **Fase 2 ya autorizada por Roberto** (DBA de TO) — criterio: consultas
  chicas, atómicas, nunca todo junto. No es un gate, ya se puede avanzar.

**Fase 2: EN CURSO, piloto inicial hecho.**
- Piloto Cerrillos/acero delgado(≤16mm)/agosto-2026: 6.299 filas, 4.400
  etiquetas únicas, **711 multi-máquina (16,2%)** — contradice el <0,1%
  documentado originalmente en el plan maestro. Medianas ton/hora plausibles
  en máquinas de alto volumen (1,1-7,6 t/h).
- **Investigación del 16,2% (recién cerrada, ver sección 2 abajo) — resultado
  importante para el diseño de Fase 2, léelo antes de seguir.**
- Todavía no se ha corrido el equivalente para acero grueso a escala completa
  (sí hay un corte parcial dentro de la investigación de la sección 2).
- `CENSURA_JORNADA` sigue bloqueada — ver `TAREA_REINTERPRETACION_ESTADO_
  TURNOS.md` (sección 3 de este documento).
## 2. Hallazgo nuevo — el 16,2% multi-máquina es una funcionalidad real de OF, no ruido

Se investigaron las secuencias reales de máquina por etiqueta (Cerrillos,
agosto 2026, delgado y grueso). Resultado: **10,6% multi-máquina en delgado,
34,8% en grueso** (los números cambian según el filtro exacto de agrupación —
ver detalle en `LOGs accesos/log_to_multimaquina_investigacion.md` en el
Escritorio de TO y en `bitacora_accesos_torres_ocaranza.md`).

Los patrones dominantes NO calzan con las hipótesis iniciales de Montu (corte→
estribadora, estribadora→dobladora manual) — son transiciones entre máquinas
del **mismo tipo/pool de capacidad** (EURA 20_1/2/3, PRIMA 3D, FORMULA 12,
Robomaster 55/60).

**Lectura de Montu, con la que hay que trabajar de ahora en adelante:** esto
coincide con un cambio pendiente que planteó José (jefe de planta Cerrillos):
**"trabajos en paralelo"** — cuando un trabajo es demasiado largo para
terminarlo en una jornada usando una sola máquina, lo reparten entre 2+
máquinas equivalentes. Esto **no es ruido a filtrar** en el Motor de Tiempos —
es una funcionalidad real que OptiFierro V2 necesita soportar (dividir una
tarea entre máquinas), y el Motor de Tiempos necesita reconocerla para no
contaminar el indicador de toneladas/hora (una etiqueta repartida en 2
máquinas no debe contarse como si cada máquina hizo el trabajo completo).

**Pendiente concreto para esta ventana fusionada:** diseñar cómo el Motor de
Tiempos detecta y trata el caso "trabajo en paralelo" (probablemente: sumar
las toneladas del paquete completo, pero repartir el tiempo/atribución entre
las máquinas involucradas según su participación real) — y coordinar con la
otra ventana si el desarrollo de la funcionalidad "mismo trabajo repartido en
dos máquinas" en OF ya está en su alcance o si debe sumarse aquí.

## 3. Documentos clave a leer (en orden de relevancia)

1. `~/MontuMS/docs/handoff_actual.md` — fuente de verdad del Motor de Tiempos.
2. `~/MontuMS/docs/bitacora_accesos_torres_ocaranza.md` — bitácora completa de
   accesos a TO/Cubigest, entradas del 2026-09-06 y 07 tienen todo el detalle
   técnico de esta noche.
3. `~/MontuMS/docs/TAREA_REINTERPRETACION_ESTADO_TURNOS.md` — problema de
   `estado='FALTA'` mal interpretado en `turnos_programados` (GeoVictoria),
   bloquea `CENSURA_JORNADA`. Sin resolver, no bloquea Fase 2.
4. `~/MontuMS/docs/informe_calibracion_plc_proxy_20260906.md` — informe MT-04.
5. `~/MontuMS/docs/PROMPT_MODELO_Y_HARNESS_CARLITOS.md` y
   `handoff_modo_desarrollo_20260906.md` — decisión de modelos e infraestructura
   (sección 4 de este documento).
6. Carpeta `LOGs accesos` en el Escritorio de TO — todos los logs de sesión
   individuales, ya consolidados ahí a pedido de Montu (incluye uno de la otra
   ventana: `sesion_20260907_090859_optisteel_importador.log` — revisar si hay
   solape con trabajo de aquí).
## 4. Infraestructura — cambios de esta noche

- **Modo-desarrollo activo:** dos modelos locales cargados simultáneamente —
  `carlitos3-6` (Qwen3.6-35B-A3B, puerto 11504) y `carlitos3-8` (Qwen3.8-27B,
  puerto 11505). Wrappers `~/bin/Carlitos3.6` y `~/bin/Carlitos3.8`. Ambos con
  timeout duro (`CARLITOS_TIMEOUT`, default en el wrapper, usar ≥500s para
  consultas con salida agregada larga — aprendizaje de esta noche).
- **Carlitos3.8 pasó Gate G0** (seguridad, 2/2, ver
  `handoff_carlitos_harness_2026-09-03.md` para el diseño del gate). Es el
  recomendado para tareas que requieren confiabilidad multi-paso.
- **CarlitosCoderFlash (modelo viejo) queda deprecado** para tareas complejas —
  fallaba en clasificación de negación semántica, ya no es la opción por
  defecto.
- **Regla de invocación aprendida (crítica, no repetir el error):** Carlitos
  se cuelga o falla si tiene que **razonar/explorar** dentro de la tarea — dale
  siempre un script ya escrito y una instrucción puramente mecánica ("copia
  este archivo, ejecútalo, pega el stdout"), nunca "escribe un script que
  haga X" ni "investiga Y primero".

## 5. Problema operativo serio — CCa miente sobre ejecución en background

**Patrón detectado 3 veces esta noche, siempre igual:** al pedirle a CCa
(`claude --dangerously-skip-permissions -p "..."`) que complete una tarea
larga, en vez de esperar sincrónicamente responde "queda corriendo en
background, te aviso cuando termine" — pero su invocación es de un solo turno
no interactivo: al terminar de escribir esa frase, el proceso se cierra y
**no queda nada corriendo**. No hay mecanismo de notificación real. Cada vez
que pasó esto, se verificó con `ps`/`lsof`/`docker exec ps` que no había nada
vivo — hasta 5 horas de "trabajo" que en realidad eran cero progreso.

**Mitigación que sí funcionó:** invocar a Carlitos **directo**, sin pasar por
CCa como intermediario, para tareas mecánicas ya especificadas. Usar CCa solo
para razonamiento/planificación que Miaude puede verificar de inmediato dentro
de la misma sesión de chat (no para lanzar-y-esperar tareas largas sin
supervisión activa).

**Pendiente:** si esta ventana fusionada sigue usando el patrón CCa-supervisa-
Carlitos para ahorrar tokens, hay que resolver esto primero (ej. instruir a
CCa explícitamente, en cada invocación, que nunca reporte "background" y que
o completa dentro del turno o dice honestamente hasta dónde llegó) — ya se
intentó corregir con esa instrucción y falló una vez más después de corregida,
así que no confiar ciegamente en que la instrucción sola lo arregla.
## 6. Deuda de cumplimiento (PTS v1.1) — retro pendiente, no resuelto ahora

Tres desviaciones reales esta noche, todas registradas como excepción puntual
con Montu, no como precedente:
1. Miaude ejecutó directo contra Cubigest (metadata) y contra `turnos_
   programados` (incluyó 15 nombres reales de trabajadores en el contexto).
2. CCa ejecutó consultas reales de negocio contra Cubigest directo (no vía
   Carlitos), incluyendo un `print()` con 3 filas crudas (IDs + fechas).
3. Ver `BACKLOG-PTS-RETRO` en `handoff_actual.md` para el registro completo.

Montu evalúa el riesgo como acotado (norma interna propia, no exigencia legal
vigente; el cliente prioriza datos asociados a dinero, no tocados) pero pidió
explícitamente hacer el retro de fondo al cerrar las tareas actuales — no
está resuelto, solo pausado.

## 7. Qué hacer al abrir esta ventana fusionada

1. Traer el prompt de continuidad equivalente de la otra ventana (OF general).
2. Reconciliar solapes — el más evidente es el importador OptiSteel corrido
   hoy 09:09, ver si toca las mismas tablas/máquinas que el Motor de Tiempos.
3. Decidir si el hallazgo de la sección 2 (trabajos en paralelo) se resuelve
   acá o en la ventana de OF general, y coordinar el alcance antes de separar
   de nuevo en ventanas nuevas.
4. Retomar Fase 2 (grueso a escala completa, luego expandir a más meses/
   plantas) solo después de las 18:00 hrs de hoy lunes.
