# CCa — Actualización de manuales v2 tras "cajita = viaje" (GAN2)

**Fecha:** 29-09-2026 · **Ejecutado por:** CCa (Claude Code, local, Mac Studio) · **Alcance:** solo documentación
en `docs/entrega/v2/` (MontuMS). No se tocó ningún repositorio de código.

## Aviso previo — archivo de fuente citado en la tarea que no existe

La tarea indicaba como "informe técnico completo, ya escrito" el archivo
`/Users/montu/MontuMS/docs/agentes/CCa_cajita_viaje_20260929.md`. **Ese archivo no existe** en el repo (se
verificó con `find` sobre todo `MontuMS`, no aparece con ningún nombre similar). Seguí la instrucción de no
preguntar y de decidir con criterio: `MAPA_DECISIONES_SPP.md` sección 3b-2 (`GAN2-01..GAN2-08`) ya contenía todas
las reglas necesarias y es la fuente de verdad explícitamente indicada como prioritaria ("léela primero"), así
que trabajé solo con ese documento más la verificación directa en código (SSH a TO, solo lectura) para el punto
que el propio mapa dejaba abierto. No se perdió ninguna regla por la ausencia del informe faltante, pero lo dejo
anotado porque alguien debería crear ese archivo o corregir la referencia en el mapa.

## Qué cambié en cada archivo

### 1. `MANUAL_USUARIO_SPP.md`
- Header: v2.0 (28-09) → **v2.1 (29-09)**, con línea nueva bajo "Reemplaza a:" explicando el motivo (mismo
  estilo que la nota v1→v2 existente).
- Sección 2 (Conceptos clave): redefiní "Cajita" como grupo de etiquetas consecutivas del mismo viaje/máquina,
  con la jerarquía de criterios (calidad > diámetro > forma > largo) y la degradación a "Forma n°: varios".
  Cita a `GAN2-01/02/03`.
- Sección 3.1:
  - "El Gantt": cajita = etiqueta → cajita = grupo, con el formato de rango de etiquetas en la carátula.
  - "Modal de la cajita": reescrito completo — header "Etiquetas: {rango}", Diámetro, "Forma n°" (o "varios"),
    Cantidad de Etiquetas, Peso total, y la tabla de etiquetas del grupo (TAG/Forma/Largo/Cantidad/Peso). Dejé
    explícito que esto es lo contrario de lo que decía la versión anterior (GAN-04 decía "sin lista de otras
    etiquetas"; GAN2-05 lo revierte).
  - Bolsa de Trabajo: agregada nota de que ahora también agrupa por los mismos criterios, y que el badge pasó de
    "N ITs" a "N cajitas".
- Sección 5 (Colores y estados): agregué un párrafo explicando, con cita de código (`_construir_evento_grupo`,
  `dict(primero)`), que el candado gris / verde se leen ahora sobre la primera etiqueta del grupo — que en la
  práctica equivale a "color del grupo" cuando todas las etiquetas del grupo comparten estado, pero es un caso
  sin verificar si alguna vez no lo hacen (ver "por confirmar" abajo). Ajusté las dos filas de la tabla
  correspondientes.
- Sección 7 (FAQ), pregunta 2: agregué una aclaración explícita de que el mecanismo de "posiciones manuales
  pegadas" (sticky) **no cambió** — sigue siendo capa del Motor no tocada por GAN2 — solo cambió la clave que usa
  (id_tarea de la primera etiqueta del grupo en vez de una etiqueta suelta), según GAN2-07.
- Sección 8 (Glosario): "Cajita" reescrita con la nueva definición.
- Sección 10 (Por confirmar): agregué el punto nuevo sobre grupos con estados mezclados (ver hallazgo técnico
  abajo).

### 2. `GUIA_RAPIDA_JEFE_PLANTA.md`
- Agregada una frase al inicio de "## Cajitas: qué significa cada cosa" explicando el cambio en una línea, sin
  citas de código (se mantuvo la convención de brevedad del documento). No toqué el resto del documento.

### 3. `MANUAL_TECNICO_SPP.md`
- Agregada la sección **4.9 "Agrupación de cajitas por viaje (GAN2) — capa de presentación, no toca el Motor"**
  (la vieja 4.9 pasó a ser 4.10, sin cambios de contenido), con cita de función y línea para:
  `_nivel_criterio_comun` (programacion.py:325-341), `_agrupar_consecutivos_por_criterio` (programacion.py:344-373),
  `_clave_grupo_evento` (programacion.py:454-455), `_agrupar_cajitas_por_viaje` (programacion.py:456-467),
  `_construir_evento_grupo` (programacion.py:397-443), `_formatear_rango_etiquetas` (programacion.py:304-322),
  `_detalle_etiqueta` (programacion.py:378-395), y el uso en Bolsa (~programacion.py:2139+).
- Documenté el hallazgo del punto abierto de `MAPA_DECISIONES_SPP.md` (ver más abajo) con cita de código.
- Documenté el riesgo de presentación no verificado (grupos con estados mezclados heredando el estado de la
  primera etiqueta) — mismo hallazgo que en el manual de usuario, con más detalle técnico aquí.
- No toqué la versión del header del documento (la tarea no lo pidió para este archivo).

### 4. `CAPTURAS_PENDIENTES.md`
- Título y fecha de la lista actualizados a v2.1 / martes 29-09 (día en que ya rige el gate).
- Capturas 1, 4, 5, 7, 8, 9 ajustadas para pedir explícitamente lo que corresponde ver con el nuevo modal/carátula
  (rango de etiquetas, tabla de etiquetas del grupo, "N cajitas" en la Bolsa, candado gris sobre un grupo con
  más de una etiqueta).
- Agregada una nota dentro de la captura 7 pidiendo específicamente un caso de "Forma n°: varios" si aparece en
  producción — **no identifiqué un caso real** (no consulté Cubigest en vivo para buscar uno; hubiera requerido
  una consulta SQL adicional fuera del alcance de esta tarea de documentación), así que quedó anotado como
  pendiente de conseguir, no inventado.

## Investigación de código — alerta de "serie ≥80% del turno" (punto abierto en `MAPA_DECISIONES_SPP.md`)

Verificado vía SSH a TO (solo lectura, sin editar nada):

- La alerta (K2, `motor_v2.py:1169-1204`) se calcula sobre el concepto de **"serie" del Motor**
  (`motor_v2.py:958-1005`), agrupación propia y **anterior** a GAN2, por `(codigo_viaje, diametro, id_forma,
  largo_mm, calidad_acero_real, etapa_avance)` — un superconjunto de los 4 criterios de GAN2 (agrega
  `etapa_avance`). El Motor resuelve ruta/máquina/operador una vez por serie y luego emite **1 tarea por
  etiqueta** (comentario explícito en el código, `motor_v2.py:960-961`).
- GAN2 (`_agrupar_cajitas_por_viaje`) corre **después**, en `programacion.py`, sobre las tareas ya guardadas por
  el Motor — es una capa de presentación posterior e independiente.
- **Conclusión:** la alerta en sí (si dispara, con qué frecuencia, a qué porcentaje) **no cambia** con GAN2 — es
  un cálculo interno del Motor, ajeno a cómo se agrupen las etiquetas después para mostrarlas.
- **Lo que sí queda desactualizado es la redacción del comentario del código** (`motor_v2.py:1194-1204`, del
  24-09), que asume "con unidad=etiqueta cada cajita ya es arrastrable por separado". Verifiqué que las
  etiquetas de una misma serie que terminan en la misma máquina comparten viaje+diámetro+forma+largo+calidad, por
  lo que GAN2 las va a fusionar en **una sola cajita-grupo** — ya no en varias cajitas-etiqueta sueltas. Confirmé
  además que el mecanismo de reparto manual (`onOpenReparto` en `GestorProgramacion.tsx:521-524,554-560`, que
  llama a `POST /api/programacion/aplicar-reparto`) opera sobre el evento `ev` tal como llega, es decir, sobre la
  cajita ya agrupada. **En la práctica:** cuando la alerta dispara hoy, lo que el jefe de planta reparte/arrastra
  suele ser una sola cajita-grupo con todas las etiquetas sobrantes, no varias sueltas — el mecanismo de reparto
  no está roto (sigue funcionando igual a nivel de código), pero su granularidad visual cambió. Documenté esto en
  el Manual Técnico, sección 4.9, con recomendación de que Montu decida si vale la pena actualizar el comentario
  del código para que no induzca a error a quien lo lea después.
- Esto es puramente un hallazgo de documentación/lectura de código — no toqué `motor_v2.py` ni ningún archivo del
  repo de TO.

## "Por confirmar" nuevos que dejé explícitos (no inventé comportamiento)

1. **Grupos con estados mezclados (candado gris/verde):** `_construir_evento_grupo` copia el campo `estado` (y
   el resto de campos top-level) de la primera etiqueta del grupo, sin agregación sobre todas las etiquetas del
   grupo. Si alguna vez un grupo queda con etiquetas en estados distintos (una ya confirmada como ejecutada en
   Cubigest, otra no), el color/candado que se ve seguiría el de la primera etiqueta, no un resumen real del
   grupo. Verificado en código (`programacion.py`, `_construir_evento_grupo`; `GestorProgramacion.tsx`,
   `isEtapaCongelada`/`isCompletado`), **no verificado con datos reales** si esta mezcla llega a ocurrir en la
   práctica. Anotado en ambos manuales (usuario sección 10, técnico sección 4.9).
2. **"Forma n°: varios" — caso real:** no identifiqué un caso concreto identificable en esta revisión (hubiera
   requerido una consulta adicional a Cubigest/SQLite en vivo, fuera del alcance dado). Anotado en
   `CAPTURAS_PENDIENTES.md` como pendiente de conseguir cuando aparezca.
3. **Ribetes de fecha (rojo/naranja/verde) dentro de un grupo:** `esVencido`/`esInminente` en el frontend leen
   `fechaDespacho` del evento — un campo que, a diferencia de calidad/diámetro, **no es uno de los 4 criterios de
   agrupación de GAN2**. No verifiqué si dos etiquetas del mismo grupo podrían tener `fecha_despacho` distinta en
   la práctica (lo esperable es que compartan la misma IT/viaje y por lo tanto la misma fecha, pero no lo
   confirmé contra datos reales). No lo agregué como punto separado en "Por confirmar" porque es de menor riesgo
   práctico que el punto 1, pero lo dejo anotado aquí por si alguien quiere revisarlo con más profundidad.

## Verificación de consistencia final

Los 4 archivos quedaron alineados en terminología: "grupo" (no "conjunto" ni otro sinónimo), "Forma n°" (no
"ID de forma" salvo cuando se explica qué dato es), "Cantidad de Etiquetas", "Peso total", formato de rango
("45-67 de 139" / "45-47,51,67 de 139"), y "N cajitas" (badge de la Bolsa). Verificado con grep cruzado sobre
los 4 archivos.

## Commit

Commit local creado en el repo `MontuMS` con el mensaje `docs(spp): actualizar manuales v2 tras cajita=viaje
(GAN2)`. **Sin push**, según instrucción de la tarea y regla cardinal del CLAUDE.md del usuario.
