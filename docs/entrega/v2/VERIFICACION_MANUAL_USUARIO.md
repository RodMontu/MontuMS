# Verificación del Manual de Usuario SPP v2.0

**Fecha:** 28-09-2026 (domingo noche / madrugada lunes) · **Autor:** CCa, trabajo autónomo overnight ·
**Revisor pendiente:** Montu (~06:00)

Metodología: lectura directa del código en el repo canónico de TO (`ssh TO`, rama en uso en el servidor de
producción), contraste con `MAPA_DECISIONES_SPP.md` y `LOG_CAMBIOS_2026.md`, y una consulta SQLite en vivo
(solo lectura) contra el contenedor `optifierro-backend`. No se ejecutó ningún POST/PUT/DELETE ni se
reconstruyó/reinició ningún contenedor. No se logró verificar contra Cubigest en vivo (SELECT) por estar fuera
de horario de trabajo real un domingo — no era necesario para las afirmaciones de este manual, que se basan en
código y en datos SQLite locales.

## (a) Tabla de afirmaciones clave → fuente → estado

| # | Afirmación | Fuente | Estado |
|---|---|---|---|
| 1 | El SPP no decide qué se produce ni cuándo se despacha (ASG-01) | `MAPA_DECISIONES_SPP.md` ASG-01, `spec_motor_asignacion_optisteel.md` | Verificado en documento de diseño |
| 2 | Menú lateral: Programación, Vista Semanal, Próximas Semanas, Producción por Máquina, Gestores (Máquinas, Operadores, Piezas, Mat. Prima, Averías), Administración | `frontend/src/App.tsx:329-344` | Verificado en código |
| 3 | Botones "Sincronizar", "Deshacer", "Compromisos Futuros"/"Ver Planificador", "Argumento", "Reprogramar" | `GestorProgramacion.tsx` líneas 2003-2027 | Verificado en código |
| 4 | Indicadores "Universo hace X min" / "Cuadro hace X min", verde/ámbar | `SyncEstado.tsx` completo | Verificado en código |
| 5 | Cajita gris con candado = etapa confirmada en Cubigest, permanente, sobrevive a regeneración | `agentes/CCa_gantt_etapa_gris_20260926.md`; `GestorProgramacion.tsx` `isEtapaCongelada` | Verificado en código + informe de implementación (rama sin mergear a la fecha del informe — **por confirmar si ya se mergeó/desplegó a producción**, ver hallazgo 3 abajo) |
| 6 | Job de verificación de etapas ejecutadas corre cada 30 min (bajado de 15 por decisión de Montu) | `agentes/CCa_gantt_etapa_gris_20260926.md`, addendum 26-09 | Verificado en informe, no releído el cron literal en `main.py` de esta corrida — **por confirmar el valor exacto en el código actualmente desplegado** |
| 7 | Cron: 08:08/20:08 scraper GeoVictoria; 08:10/20:10 corrida del Motor (suc. 1,10,14), L-V sin feriados CL; 08:51/21:21 alertas de tardanza; :30 verificación ITs cerradas | `backend/main.py` líneas 141-300 (leído completo) | Verificado en código |
| 8 | Manual override (drag&drop) SÍ se reaplica en `generar_programacion` (botón "Reprogramar") vía bloque "sticky cajitas" | `backend/routers/programacion.py` líneas ~1415-1450 | Verificado en código |
| 9 | Manual override NO se reaplica en `_ejecutar_generacion` (corrida automática 08:10/20:10) | `backend/main.py` líneas 141-228, comparado línea por línea contra el punto 8 | Verificado en código — ver hallazgo 1 |
| 10 | FP-LC excluido completamente del SPP (Motor, Bolsa, Gantt, Gestor de Máquinas) | `MAPA_DECISIONES_SPP.md` ASG-11 | Verificado en documento de diseño; no releído `es_despacho_directo` línea por línea en esta ronda |
| 11 | Máquinas activas por sucursal (10 Cerrillos, 8 Calama, 9 Coronel, listado exacto) | `backend/motor_v2.py:134-149`, `MAQUINAS_ACTIVAS` | Verificado en código, coincide exactamente con v1 |
| 12 | Restricciones físicas (PRIMA 3D 2000mm, Robomaster 55/60 2500mm, etc.) | `MAPA_DECISIONES_SPP.md` ASG-12 | Verificado en documento de diseño; no releído `RESTRICCIONES_LARGO` línea por línea |
| 13 | Ejemplo de hebras: Coronel, Dobladora 2 → 8 hebras Ø10, 6 hebras Ø12, 3 hebras Ø16 | Consulta SQLite en vivo, 28-09-2026, tabla `hebras` sucursal_id=14 | **Verificado en vivo** (dato real: Ø8=10, Ø10=8, Ø12=6, Ø16=3, Ø18=3 hebras) |
| 14 | Mensajes de rechazo del drag&drop (avería, diámetro incompatible, cajita ya ejecutada) | `GestorProgramacion.tsx` líneas 1306, 1311, 1386 | Verificado en código, texto citado tal cual |
| 15 | Averías: dos fuentes (manual y Cubigest), contadores, "Reportar Falla", "Levantar avería" | `GestorAverias.tsx` completo (primeras 140 líneas), `backend/routers/averias.py` | Verificado en código |
| 16 | Sync de averías Cubigest cada 30 min, ventana de 3 días solo para resueltas | `backend/routers/averias.py`, `AVERIAS_CUBIGEST_VENTANA_DIAS` y comentarios del bug del 27-09 | Verificado en código |
| 17 | Reglas de fecha UNI-01..05 (atrasada 1-30d, próxima +21d, muy futura +60d) VIGENTE desde 26-09 | `MAPA_DECISIONES_SPP.md` sección 3c | Verificado en documento, con estado explícito VIGENTE y desplegado |
| 18 | Leyenda "No considera ITs con fecha de despacho mayor a 60 días..." en Vista Semanal y Próximas Semanas | `VistaSemanal.tsx:232`, `CalendarioFuturo.tsx:386` | Verificado en código, texto citado tal cual |
| 19 | Setup de 15 min al cambiar diámetro en la misma máquina | `MAPA_DECISIONES_SPP.md` ASG-05 | Verificado en documento (motivo de negocio no documentado en el código, se dice así en el manual) |
| 20 | Criterio exacto del aviso "⚠ ATRASO" en la cajita | No se leyó la función completa que lo calcula | **Por confirmar** — se documentó en el manual como pendiente |
| 21 | Estilo visual de "no liberada" / "adelanto de trabajo futuro" | Solo se vieron comentarios/variables en código (`viene_de_futuro`), no el render final | **Por confirmar** |
| 22 | Comportamiento de Gestores de Operadores/Piezas/Mat. Prima pantalla por pantalla | No se relevó en esta ronda por límite de tiempo | **Por confirmar**, omitido del manual salvo mención de que existen |
| 23 | Si el Motor excluye automáticamente una máquina averiada en la corrida 08:10/20:10 (no solo el drag&drop) | No se leyó esa parte de `motor_v2.py` | **Por confirmar** |
| 24 | Calama: todas las máquinas a 1 hebra | Tabla `hebras` en vivo, sucursal_id=1, 28-09-2026 (auditoría) | **FALSO — corregido en auditoría 28-09**: Carro de Corte tiene 2 hebras en Ø8/10/12/16mm, EURA 20_2 tiene 2 hebras en Ø10mm; no todas las máquinas están en 1 hebra |

**Resumen:** 19 afirmaciones clave verificadas en código, documento de diseño o consulta en vivo; 5 quedaron
explícitamente en "por confirmar" (ninguna se inventó).

## (b) Lo que en v1 estaba falso, desactualizado o sin respaldo — y la corrección aplicada

1. **FALSO — la más grave (FAQ v1 #2):** v1 afirmaba que si el jefe de planta reasigna una cajita a mano, la
   corrida automática de las 20:10 "respeta los eventos ya asignados y ejecutados". **Verificado en código que
   esto es falso para la corrida automática**: `_ejecutar_generacion` (el scheduler de las 08:10/20:10) llama
   directo a `motor_v2.programar_turno` y reemplaza toda la programación de esa sucursal/turno/fecha, sin pasar
   por el bloque de "posiciones manuales (sticky cajitas)" que sí existe — pero solo en el endpoint
   `generar_programacion` usado por el botón manual "Reprogramar". **Corrección aplicada:** sección 7 (FAQ 2) y
   sección 9 (Limitaciones) del manual v2, más advertencia destacada en la Guía Rápida.

2. **DESACTUALIZADO — 5 avisos "PENDIENTE DE CIERRE OLA 3" (B42, B44a, B43, B39, y el genérico de la sección de
   averías):** todos describían funciones que hoy ya están desplegadas y en uso:
   - B42 (número de etiqueta en la cajita en vez de código genérico de TAG) → hoy la cajita muestra viaje,
     "Etiqueta N de M", diámetro y peso (GAN-03), y el modal de detalle usa la etiqueta real (GAN-04).
   - B44a (ajustar duración manualmente) → existe función de doble clic para repartir/ajustar (GAN-05,
     confirmado como "ya validado con los jefes de planta").
   - B43 (indicador de adelanto de trabajo futuro) → existe la señal `viene_de_futuro` en el código; su
     representación visual exacta quedó "por confirmar" en v2 en vez de describirla como pendiente o inventarla.
   - B39 (averías desde Cubigest) → hoy es una fuente real y activa (`sync_averias_cubigest`, cada 30 min),
     documentada en la sección 3.6 de v2.
   **Corrección aplicada:** se eliminaron los 5 avisos "PENDIENTE" y se describieron como funciones vigentes,
   con su fuente en código.

3. **SIN RESPALDO VERIFICADO EN ESTA RONDA — estado de despliegue del "candado gris" (B42 v2 / etapa
   congelada):** el informe `CCa_gantt_etapa_gris_20260926.md` describe la implementación como hecha en una
   rama (`gantt-etapa-gris`) que a esa fecha **no estaba mergeada ni pusheada**, pendiente de revisión de
   Montu/Miaude. El addendum del mismo informe registra "luz verde de Montu" para commit + build/deploy. **No
   se verificó en esta ronda, contra el código que corre hoy en el contenedor de producción, si ese deploy ya
   se completó** (no se hizo `docker logs`/inspección del build activo, para no consumir tiempo de una
   verificación no esencial en domingo de madrugada). El manual v2 describe el candado gris como función
   vigente porque el informe indica luz verde y el flujo de trabajo de este equipo asume deploy tras
   aprobación — **Montu debería confirmar en la mañana que el candado gris ya está en producción**, o
   marcarlo como pendiente si el deploy final no se hizo.

4. **POSIBLE INEXACTITUD MENOR EN v1, no confirmada como error:** v1 citaba el ejemplo de hebras de Coronel
   Dobladora 2 (8/6/3 hebras en Ø10/12/16) sin marcar fuente. Se verificó en vivo contra la tabla SQLite real
   el 28-09-2026 y **el dato coincide exactamente** — no era un error, pero tampoco tenía respaldo explícito en
   v1. En v2 se agregó la fuente (consulta en vivo, con fecha).

## (c) Hallazgos de comportamiento del sistema que Montu debería conocer

1. **Hallazgo principal (CORREGIDO por Miaude el 28-09 tras revisión independiente — la versión original de este
   punto sobrestimaba el alcance):** la corrida automática de cada turno (08:10 → Día; 20:10 → Noche) reemplaza el
   plan guardado **de su propio turno**, sin reaplicar movimientos manuales ni la asignación manual de operadores por
   jornada (tabla `jornada_asignacion_manual`) hechos ANTES de esa corrida. NO afecta al otro turno: los
   movimientos manuales del turno Día se conservan después de la corrida de las 20:10 (el turno Noche se guarda en
   otra fila; al reabrir el turno Día se recarga desde `programacion_guardada`, que `/reprogramar` mantiene
   actualizada). Riesgo real y acotado: ajustes hechos antes de la corrida automática de su turno (p. ej. 07:45 →
   se pierden a las 08:10). Esto es una diferencia de comportamiento entre dos caminos de código que
   deberían (¿?) comportarse igual pero no lo hacen: `generar_programacion` (endpoint manual) sí reaplica
   `programacion_manual`; `_ejecutar_generacion` (scheduler) no. **Recomendación:** decidir si esto es el
   comportamiento deseado (el sistema recalcula "desde cero" cada 12 horas, ignorando ajustes puntuales del
   jefe de planta) o si es un bug que debería corregirse agregando el mismo bloque de "sticky cajitas" al
   scheduler. Mientras no se decida, el manual ya advierte a los jefes de planta.

2. **La misma asimetría existe también para el candado gris, pero ahí SÍ está resuelto por diseño:** el
   mecanismo de `etapa_congelada` se re-aplica en ambos caminos (`generar_programacion` y
   `_ejecutar_generacion`), porque no depende de "sobrevivir" en memoria sino de una tabla separada que se
   re-consulta en cada corrida. Esto muestra que el patrón para resolver la asimetría de la nota 1 ya existe en
   el código (podría reusarse el mismo enfoque para `programacion_manual` si se decide corregirlo).

3. **Guard contra planes vacíos:** existe una salvaguarda explícita en `_ejecutar_generacion` — si el Motor
   devuelve 0 tareas y ya había un plan guardado con tareas para esa sucursal/turno/fecha, el sistema aborta el
   guardado y registra un error en vez de borrar la programación activa. Esto es una buena práctica ya
   implementada, vale la pena que Montu la conozca como mitigante parcial de fallas transitorias de Cubigest.

4. **Persistencia de `programacion_manual` vs. memoria viva:** `global_eventos` vive solo en RAM del proceso;
   las reasignaciones manuales se respaldan en la tabla `programacion_manual`, pero un reinicio del contenedor
   antes de la próxima corrida del Motor podría no reflejar en pantalla los últimos movimientos hasta que se
   ejecute la planificación de nuevo. No es nuevo (documentado ya en el Manual Técnico v1), pero se reafirma
   porque es relevante para el mismo hallazgo 1.

5. **La conexión SSL a Cubigest sigue siendo intermitente** (mismo síntoma documentado el 23-09 y otra vez el
   27-09). No se intentó verificar en vivo en esta ronda porque no era necesario para las afirmaciones del
   manual, pero sigue siendo un riesgo operativo activo para todo lo que depende de Cubigest en tiempo real
   (averías, candado gris, Cuadro OptiSteel).

## Bloqueos encontrados

- No se ejecutó ninguna consulta SELECT en vivo contra Cubigest (no era necesaria para verificar las
  afirmaciones de este manual; todo lo relevante para el manual se pudo verificar contra código y SQLite
  local). Si Montu quiere una verificación en vivo adicional de algún dato específico de Cubigest, queda
  pendiente para una próxima ronda.
- No se relevaron en detalle los Gestores de Operadores, Piezas y Materia Prima, ni el criterio exacto del
  aviso "⚠ ATRASO", por límite de tiempo/alcance de esta sesión — quedan listados en la sección 10 del manual
  ("Por confirmar") y no se inventó contenido para ellos.
