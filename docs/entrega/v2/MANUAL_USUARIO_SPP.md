# Manual de Usuario — Sistema Planificador de la Producción (SPP)

**Versión:** 2.1 · **Fecha:** 29-09-2026
**Reemplaza a:** v1.0 (24-09-2026). Este documento fue escrito de nuevo desde el código real; v1 contenía avisos
de funciones "pendientes" que ya están en producción y al menos una afirmación incorrecta sobre el
comportamiento del sistema (ver `VERIFICACION_MANUAL_USUARIO.md`).
v2.1 corrige la definición de "cajita" en todo el documento tras el cambio de Gustavo (TO) del 29-09-2026: la
cajita vuelve a representar un grupo de etiquetas de un mismo viaje, no una etiqueta suelta (ver
`MAPA_DECISIONES_SPP.md`, sección 3b-2, `GAN2-01..GAN2-08`).
**Destinatarios:** Jefes de planta y gerencias de Torres Ocaranza (Cerrillos, Calama, Coronel). No requiere
conocimientos de informática.
**Nombre del sistema:** SPP o "el Planificador". El componente que calcula la asignación de trabajos se llama
**el Motor**.

**Cómo leer este manual:** las afirmaciones de hechos (nombres de pantallas y botones, horarios, comportamientos)
llevan un comentario oculto con su fuente, por ejemplo `<!-- fuente: backend/main.py:141 -->`. No es visible al
imprimir ni leer el documento normalmente; sirve para que alguien de TI pueda auditar cada frase contra el
código. Donde no se pudo verificar algo, se dice explícitamente "por confirmar" en vez de inventarlo.

---

## 0. Guía rápida

Existe un documento aparte de 1-2 páginas para imprimir y tener a mano en el puesto de trabajo:
`GUIA_RAPIDA_JEFE_PLANTA.md`. Este manual es la referencia completa.

---

## 1. ¿Qué es el SPP y qué decide?

El SPP es la herramienta que organiza, dentro de cada turno, qué máquina y qué operador de la planta ejecuta
cada trabajo pendiente, buscando la combinación que logra la mayor producción posible en la jornada.

### Lo que el SPP SÍ decide
1. **A qué máquina va cada etiqueta de fabricación**, respetando diámetro, forma y restricciones físicas del
   equipo. <!-- fuente: MAPA_DECISIONES_SPP.md ASG-03, ASG-12; backend/motor_v2.py -->
2. **Qué operador presente atiende cada máquina**, según su competencia registrada y su asistencia real del
   turno (leída de GeoVictoria). <!-- fuente: MAPA_DECISIONES_SPP.md ASG-03 -->
3. **En qué orden se hacen los trabajos** dentro de una misma máquina, penalizando 15 minutos cada vez que la
   máquina cambia de diámetro. <!-- fuente: MAPA_DECISIONES_SPP.md ASG-05; SETUP_CAMBIO_DIAMETRO_MIN -->
4. **Si una etapa anterior ya se hizo** (por ejemplo, el corte), el Motor no vuelve a programar esa etapa y
   pasa directo a la siguiente (por ejemplo, el doblado). <!-- fuente: MAPA_DECISIONES_SPP.md ASG-09 -->

### Lo que el SPP NO decide (Regla ASG-01)
> El SPP **no decide qué se produce ni cuándo se despacha al cliente**. Esas decisiones las toman Cubigest y
> OptiSteel, los sistemas centrales de la empresa. El SPP recibe los trabajos ya liberados por esos sistemas y
> busca la mejor forma de repartirlos entre las máquinas y operadores disponibles de la planta.
> <!-- fuente: MAPA_DECISIONES_SPP.md ASG-01 -->

Materias primas (si hay stock de fierro suficiente) **no** son consideradas por el Motor en esta etapa: queda
fuera del cálculo de asignación. <!-- fuente: MAPA_DECISIONES_SPP.md sección 4, ASG-03 -->

---

## 2. Conceptos clave

- **IT (Instrucción de Trabajo):** la orden de fabricación que emite Cubigest para un cliente/obra.
- **Viaje:** una parte de esa IT, pensada para ir en un camión a la obra.
- **Etiqueta:** la unidad física mínima que se fabrica y se rotula en planta, con sus kilos exactos
  (`KgsPaquete`). Es lo que el operario ve en el atado de fierro.
- **Cajita:** en el Gantt de la pantalla Programación (y, desde este cambio, también en la Bolsa de Trabajo),
  cada bloque representa **un grupo de etiquetas consecutivas del mismo viaje/IT y la misma máquina**, no una
  etiqueta suelta. El grupo se arma según qué tan parecidas son las etiquetas, en este orden de prioridad:
  1) calidad de acero, 2) diámetro, 3) forma de pieza (ID de forma), 4) largo. Si no comparten los 4, el grupo se
  "degrada" al criterio más alto que sí comparten (por ejemplo, misma calidad+diámetro+forma pero distinto largo);
  si ni siquiera comparten calidad y diámetro, quedan como cajitas separadas. Cuando el grupo mezcla más de una
  forma de pieza, el detalle muestra "Forma n°: varios" en vez de un ID de forma único.
  <!-- fuente: MAPA_DECISIONES_SPP.md GAN2-01, GAN2-02, GAN2-03 -->
- **Etapa:** un paso del proceso de fabricación de una etiqueta (por ejemplo corte → doblado). Una misma
  etiqueta puede pasar por más de una máquina, una etapa a la vez.
- **Bolsa de Trabajo:** la lista de etiquetas que aún no tienen máquina asignada en el turno.
- **el Motor:** el cálculo que decide la asignación óptima de trabajos a máquinas y operadores.
- **Turnos:** Día y Noche (ver sección 6A de horarios).
- **Colación:** el bloque de 60 minutos en que ninguna máquina recibe trabajo nuevo.
- **Hebras (multiplicidad):** cuántas barras del mismo diámetro puede procesar una máquina al mismo tiempo, en
  una sola pasada. Ejemplo real verificado en vivo el 28-09-2026: en Coronel, la *Dobladora 2* está configurada
  con 8 hebras en Ø10 mm, 6 hebras en Ø12 mm y 3 hebras en Ø16 mm.
  <!-- fuente: consulta SQLite en vivo, tabla `hebras`, sucursal_id=14, 28-09-2026 -->
- **Acero delgado (AD):** diámetro ≤ 16 mm. **Acero grueso (AG):** diámetro > 16 mm.
  <!-- fuente: MAPA_DECISIONES_SPP.md ASG-08 -->

Cada planta es distinta: Cerrillos tiene las máquinas más nuevas; Calama tiene las más antiguas.
**Corrección de auditoría 28-09-2026 — el dato de "Calama a 1 sola hebra" es incorrecto:** se verificó en vivo
la tabla `hebras` completa de Calama (sucursal_id=1) y **no** todas las máquinas están limitadas a 1 hebra —
por ejemplo Carro de Corte tiene 2 hebras en Ø8/10/12/16mm, y EURA 20_2 tiene 2 hebras en Ø10mm; otras máquinas
sí están en 1 hebra o en 0 (diámetro no habilitado) según el caso. La generalización "todas a 1 hebra" no debe
usarse en capacitación. <!-- fuente: en vivo, tabla `hebras` sucursal_id=1, 28-09-2026 -->
Coronel y Cerrillos usan de 2 a 10 hebras en acero delgado.

---

## 3. Pantalla por pantalla

Menú lateral, en el orden exacto en que aparece: **Programación · Vista Semanal · Próximas Semanas · Producción
por Máquina** — y bajo "Gestores": **Máquinas · Operadores · Piezas · Mat. Prima · Averías** — y, según el rol
del usuario, **Administración**. <!-- fuente: frontend/src/App.tsx:329-344 -->

### 3.1 Programación

Es la pantalla de trabajo diario del jefe de planta. El encabezado muestra: sucursal, el turno activo (Día o
Noche) y la fecha, con un campo para cambiarla. <!-- fuente: GestorProgramacion.tsx, header "Planificador de
Producción" -->

**Botones y controles del encabezado:**
- **Sincronizar:** actualiza dos fuentes de datos a pedido (no espera a la próxima corrida automática). Junto
  al botón aparecen dos indicadores, **"Universo hace X min"** y **"Cuadro hace X min"**, en verde si están al
  día o en ámbar con un ícono de advertencia si están desactualizados.
  <!-- fuente: frontend/src/components/domain/SyncEstado.tsx -->
- **Deshacer:** aparece solo después de un movimiento manual reciente en el Gantt; revierte esa última
  reasignación. <!-- fuente: GestorProgramacion.tsx, botón "Deshacer" -->
- **Compromisos Futuros:** cambia la vista para mostrar los compromisos de fechas futuras en lugar del Gantt del
  turno actual; el botón cambia su texto a "Ver Planificador" para volver.
  <!-- fuente: GestorProgramacion.tsx, `showCompromisos` -->
- **Argumento:** disponible cuando hay eventos en el Gantt; genera una explicación en lenguaje natural de la
  programación actual. <!-- fuente: GestorProgramacion.tsx, botón "Argumento" -->
- **Reprogramar:** vuelve a ejecutar el Motor para el turno y fecha visibles, con los datos más recientes.
  <!-- fuente: GestorProgramacion.tsx, botón "Reprogramar" → `handleGenerar` → `POST /api/programacion/generar` -->
  **Importante — a diferencia de v1:** este botón es manual, distinto de la corrida automática de las 08:10/20:10;
  su comportamiento respecto a los movimientos manuales se explica en el punto siguiente y en la sección 7 (FAQ).

**El Gantt:**
- Cada fila es una máquina activa de la sucursal. Cada cajita es un grupo de etiquetas consecutivas del mismo
  viaje en esa máquina, en un horario (ver definición completa en la sección 2). La carátula muestra el rango de
  etiquetas del grupo en vez de "Etiqueta N de M": por ejemplo "45-67 de 139" si las etiquetas son correlativas,
  o "45-47,51,67 de 139" si no lo son. <!-- fuente: MAPA_DECISIONES_SPP.md GAN2-01, GAN2-04 -->
- **Zoom y desplazamiento:** la línea de tiempo permite acercar/alejar y desplazarse horizontalmente (íconos de
  lupa y de expandir). <!-- fuente: agentes/CCa_gantt_zoom_20260926.md; imports `ZoomIn, ZoomOut, Maximize2` en
  GestorProgramacion.tsx -->
- **Cajita con candado gris (etapa ya ejecutada):** cuando Cubigest confirma que una etapa (una etiqueta, en una
  máquina específica) ya se ejecutó realmente en planta, la cajita queda de color gris permanente, con un ícono
  de candado, y **no se puede volver a arrastrar**. Esto ocurre incluso si se vuelve a generar la programación:
  el sistema revisa una tabla separada (`etapa_congelada`) en cada corrida y repinta el gris, sin importar si
  la cajita "sobrevivió" en memoria o no. Un clic simple sigue mostrando el detalle (es un registro histórico);
  el doble clic para repartir queda bloqueado.
  <!-- fuente: agentes/CCa_gantt_etapa_gris_20260926.md; GestorProgramacion.tsx `isEtapaCongelada` -->
  Esta verificación contra Cubigest corre automáticamente cada 30 minutos.
  <!-- fuente: agentes/CCa_gantt_etapa_gris_20260926.md, addendum Montu 26-09 (bajado de 15 a 30 min) -->
- **Aviso ATRASO:** una cajita puede mostrar la advertencia "⚠ ATRASO" en su carátula.
  <!-- fuente: GestorProgramacion.tsx:474 --> El criterio exacto que determina cuándo se marca así es
  **por confirmar** en este manual (no se alcanzó a leer la función completa que la calcula).

**Averías y la máquina:** si la máquina de destino está fuera de servicio por avería, el sistema rechaza el
movimiento con el mensaje *"⚠️ ERROR: Máquina fuera de servicio por avería."* Si el diámetro de la pieza no es
compatible con la máquina, el mensaje es *"⚠️ ERROR: La máquina [nombre] no soporta Ø[diámetro]mm."* Si se
intenta soltar una cajita sobre una etapa ya confirmada (candado gris), el mensaje es *"⚠️ No se puede soltar
sobre una cajita ya ejecutada (confirmada en Cubigest) — es registro histórico permanente."*
<!-- fuente: GestorProgramacion.tsx líneas 1306, 1311, 1386 -->

**Modal de la cajita (detalle, un clic):** el encabezado ya no dice "Etiqueta: N de M" — ahora dice
**"Etiquetas: {rango}"**, con el mismo formato de rango de la carátula (ej. "45-67 de 139"). El cuerpo muestra
Diámetro, **"Forma n°"** (el ID de forma, o "varios" si el grupo mezcla más de una forma — ver sección 2),
**Cantidad de Etiquetas** (el número de etiquetas del grupo — distinto de la cantidad de piezas) y **Peso
total** del grupo. Ya no aparece la marca comercial del fierro. A diferencia de versiones anteriores de este
manual: **sí aparece** una tabla con el detalle de cada etiqueta del grupo, columnas TAG / Forma / Largo /
Cantidad / Peso, en orden ascendente por número de etiqueta — el Largo y el Paquete, que antes aparecían como
un dato único del cuerpo del modal, ahora son columnas de esa tabla porque cada etiqueta del grupo puede tener
su propio largo.
<!-- fuente: MAPA_DECISIONES_SPP.md GAN2-05; backend/routers/programacion.py `_construir_evento_grupo`,
`_detalle_etiqueta`, `_formatear_rango_etiquetas` -->

**Arrastrar y soltar:** permite mover una cajita a otra máquina compatible o reordenarla dentro de la misma
máquina. El sistema valida diámetro, forma y estado de la máquina antes de aceptar el movimiento (ver mensajes
de rechazo arriba).

**Bolsa de Trabajo:** lista, en la misma pantalla, las etiquetas sin máquina asignada en el turno. Se puede
arrastrar una etiqueta de la Bolsa directamente a una máquina del Gantt. Desde este cambio, la Bolsa también
agrupa etiquetas por el mismo criterio del Gantt (calidad, diámetro, forma, largo), aunque todavía sin máquina
asignada — antes de este cambio, la Bolsa siempre mostraba 1 tarjeta por etiqueta/IT; ahora un mismo IT puede
aparecer con varias tarjetas si sus etiquetas no comparten todos los criterios entre sí. El badge que antes decía
"N ITs" ahora dice **"N cajitas"**. <!-- fuente: MAPA_DECISIONES_SPP.md GAN2-06, GAN2-08 -->

### 3.2 Vista Semanal

Matriz de los compromisos de la semana. Distingue, por ejemplo, "Atrasado ≤30 días" (en rojo) de "Sin fecha
confirmada / muy futura", con la leyenda: *"No considera ITs con fecha de despacho mayor a 60 días (N ITs / X kg
fuera; ver aparte)."* <!-- fuente: frontend/src/components/domain/VistaSemanal.tsx líneas 224-232 -->

### 3.3 Próximas Semanas

Agrupa las ITs pendientes por fecha en un horizonte de varias semanas, con el mismo criterio de fecha "muy
futura" que Vista Semanal (leyenda: *"No considera ITs con fecha de despacho mayor a 60 días, o reprogramadas
por el cliente/TO con fecha poco confiable"*). <!-- fuente: CalendarioFuturo.tsx líneas 385-386 -->

**Reglas de fecha aplicadas en todo el sistema (vigentes desde el 26-09-2026):**
| Categoría | Regla |
|---|---|
| Atrasada válida | 1 a 30 días atrasada. Más de 30 días se considera "suciedad" de datos y queda fuera de las vistas de demanda. |
| Próxima | Hoy hasta +21 días. |
| Lejana normal | +22 a +60 días. |
| Muy futura | Más de +60 días (no cuenta como demanda para Materia Prima). |
<!-- fuente: MAPA_DECISIONES_SPP.md sección 3c, UNI-01..UNI-05, VIGENTE desde 26-09-2026 -->

### 3.4 Producción por Máquina

Título interno: *"Tiempos por Máquina (estimado)"*. Consulta el rendimiento histórico en toneladas por hora de
una máquina para una forma, diámetro y (opcional) largo de pieza. <!-- fuente: MAPA_DECISIONES_SPP.md sección 1,
PRO-01..PRO-13 -->

- Se informa **mediana** y **rango típico P25–P75**, nunca un promedio con desviación ni un "% de confianza":
  el comportamiento real de las máquinas no sigue una distribución de campana. <!-- fuente: PRO-05, EST-06 -->
- Avisos que puede mostrar: "Datos insuficientes" (menos de 15 registros), "Fuera de rango histórico" (con
  tolerancia de ±10%), "Rango no evaluable" (líneas de corte, donde "piezas por paquete" no representa barras
  individuales) y "Sin ajuste por largo" (menos de 30 registros para segmentar). <!-- fuente: PRO-06, PRO-08,
  PRO-09, PRO-07 -->
- **Esta pantalla NO alimenta al Motor**: es solo referencial para la toma de decisiones del jefe de planta.
  <!-- fuente: PRO-11, sección 4 de MAPA_DECISIONES_SPP.md -->
- Método pendiente de mejora: hoy usa el delta crudo entre registros consecutivos (versión A); el método
  estadístico más fino (FASE3) todavía no está en producción. <!-- fuente: PRO-13, B26-B PENDIENTE -->

### 3.5 Gestores

**Máquinas:** catálogo de máquinas activas por sucursal, con su matriz de diámetros y de hebras, y las
restricciones físicas configuradas. <!-- fuente: ASG-07, ASG-12 -->

Máquinas activas por planta (código, no exhaustivo de todo el parque físico — solo lo que el Motor considera):
<!-- fuente: backend/motor_v2.py:134-149, `MAQUINAS_ACTIVAS` -->
- **Cerrillos (10):** Curvadora CER40 1 Schnell, Dobladora Tecmor S40 1, Dobladora Tecmor S40 2, EURA 16,
  EURA 20_1, EURA 20_3, Línea de Corte, PRIMA 3D, Robomaster 55, Robomaster 60.
- **Calama (8):** Carro de Corte, COIL 14, COIL 14 M, Cortadora Manual, Dobladoras, EURA 16, EURA 20_2,
  Robomaster 60.
- **Coronel (9):** Cortadora Manual, Curvadora 1, Curvadora 2, Dobladora 2, Dobladora 3, Dobladora 4,
  Estribadora TJK 1, Estribadora TJK 2, Línea Corte Coronel.

Restricciones físicas conocidas (Cerrillos): PRIMA 3D con cota A máxima de 2.000 mm; Robomaster 55 y 60 con pata
máxima de 2.500 mm; Robomaster 55 solo dobleces a 90°; Curvadora CER40 solo anillos y espirales; EURA 20_1 no
procesa anillos. <!-- fuente: ASG-12, RESTRICCIONES_LARGO / RESTRICCIONES_FUNCIONALES -->

**FP-LC (Fierro en Punta - Largo Comercial) no es una máquina del SPP:** son piezas rectas de 6 a 12 metros en
diámetros delgados que van directo de bodega al camión, sin pasar por ninguna máquina de planta. No entran al
Motor ni a la Bolsa, no aparecen en el Gantt ni en el Gestor de Máquinas, y no se pueden reasignar manualmente.
<!-- fuente: ASG-11, `MAQUINAS_FICTICIAS`, `es_despacho_directo` -->

**Operadores, Piezas, Mat. Prima:** pantallas de gestión de competencias de operadores, catálogo de piezas y
materia prima. <!-- por confirmar: no se relevó el detalle pantalla por pantalla de estos tres Gestores para
esta versión; queda para una próxima revisión. -->

### 3.6 Averías

Combina **dos fuentes reales y distintas** de información sobre el estado de las máquinas:
1. **Manual:** el jefe de planta registra la avería a mano con el botón **"Reportar Falla"**, eligiendo la
   máquina y describiendo el síntoma; el sistema clasifica el síntoma y guarda el estado (operativa /
   semi-operativa / detenida). <!-- fuente: GestorAverias.tsx, botón "Reportar Falla"; POST /api/averias/normalizar -->
2. **Cubigest:** una consulta directa (sin simulación de navegador) a la tabla `NotificacionAveria` de Cubigest,
   que se ejecuta cada 30 minutos y trae los estados DET (detenida), SEMI (semi-operativa), ING (ingresada) u OP
   (operativa) según los registra el propio ERP. <!-- fuente: backend/routers/averias.py, `sync_averias_cubigest`,
   `ESTADO_CUBIGEST_LABEL` en GestorAverias.tsx -->

La pantalla muestra **contadores** de máquinas operativas / semi-operativas / detenidas y la **falla más
recurrente** de la sucursal. <!-- fuente: GestorAverias.tsx, `contadores`, `fallaTop`; endpoints
`/api/averias/contadores` y `/api/averias/falla_recurrente` -->

**Actualización 28-09 (`5072159`): el estado que ve en Averías, en las filas del Gantt y el que usa el Motor es el
mismo.** Los contadores y la tabla "Estado de Maquinaria" muestran el estado **efectivo** de cada máquina activa,
que resulta de combinar el gestor manual, las notificaciones de Cubigest y las máquinas dadas de baja en Cubigest;
si dos fuentes discrepan, **prevalece la más restrictiva** (por ejemplo, detenida sobre operativa). Para las
averías que vienen de Cubigest, la columna "Falla vigente / restricción" muestra el texto de la falla, la marca
"Cubigest" y cuánto tiempo lleva registrada ("registrada hace N días"), para que se note una notificación que
Cubigest nunca cerró. <!-- fuente: backend/estado_maquinas.py, routers/averias.py, GestorAverias.tsx -->

**Importante ante una avería nueva a media jornada:** una avería registrada en Cubigest (o a mano) aparece en
Averías y en la fila de la máquina dentro de un máximo de 30 minutos, pero las cajitas que el Motor ya había
asignado a esa máquina **no se mueven solas**: el jefe de planta debe presionar **"Reprogramar"** (el Motor no
asigna trabajo a máquinas detenidas) o arrastrarlas a otra máquina compatible.
<!-- fuente: motor_v2.py solo excluye al generar; estado observado el 28-09 con averías de las 09:03–09:23 -->
Una avería que viene de Cubigest se cierra en Cubigest (el botón "Levantar avería" es solo para las manuales).

**Levantar avería:** el jefe de planta puede marcar una avería (manual) como resuelta con un botón de
confirmación ("¿Levantar avería de [máquina]? La máquina pasará a estado OPERATIVA."). <!-- fuente:
GestorAverias.tsx, `handleLevantar` -->

**Efecto en el Motor:** mientras una máquina está averiada (fuente manual o Cubigest), la pantalla de
Programación rechaza cualquier intento de asignarle trabajo con el mensaje ya citado en 3.1 ("Máquina fuera de
servicio por avería"). <!-- fuente: GestorProgramacion.tsx:1306 --> **Confirmado en auditoría 28-09-2026:** el
Motor también excluye automáticamente esa máquina en la corrida automática de las 08:10/20:10, no solo en el
drag & drop manual — la exclusión vive dentro de la función central de asignación (`motor_v2.py`, resolución de
`maquinas_detenidas`/`maquinas_semi`, líneas ~900-970), que es compartida por el endpoint manual y por el
scheduler; fusiona siempre ambas fuentes (avería manual y Cubigest, la más restrictiva gana).
<!-- fuente: en vivo, backend/motor_v2.py líneas 900-970, 28-09-2026 -->

### 3.7 Administración

Panel visible según el rol del usuario (SuperAdmin, Admin, Jefe de Planta, Visualizador), con pestañas: Usuarios,
Sucursales, Logs, Geovictoria, Roles y Sistema (estas dos últimas solo para SuperAdmin).
<!-- fuente: frontend/src/components/domain/Administracion.tsx -->
El detalle de cada pestaña **no se documenta aquí** porque no es de uso diario del jefe de planta; queda como
referencia de que existen, para que Gerencia sepa a quién pedir cambios de usuarios o roles.

---

## 4. Un día tipico del jefe de planta

<!-- por confirmar en general: esta sección describe el flujo esperado según el código del scheduler
(horarios exactos verificados); la parte de "qué debe revisar/hacer" el jefe de planta en cada paso es
una recomendación razonable, no una instrucción documentada en el código o en un manual previo — trátese
como guía, no como procedimiento oficial de TO. -->

1. **08:08 (lunes a viernes):** el sistema dispara automáticamente la lectura de asistencia desde GeoVictoria.
   <!-- fuente: backend/main.py, job `scraper_geo_dia` -->
2. **08:10 (lunes a viernes, sin feriados de Chile):** corre automáticamente el Motor para las 3 sucursales
   (Calama, Cerrillos, Coronel) con los operadores que ya marcaron asistencia. <!-- fuente: backend/main.py,
   `_job_dia` -->
   **Importante:** esta corrida automática **reemplaza completamente** la programación guardada de esa
   sucursal/turno/fecha con el resultado nuevo del Motor — ver advertencia en la sección 7, pregunta 2.
3. **Durante el turno:** el jefe de planta revisa el Gantt, ajusta con arrastrar y soltar si es necesario, y usa
   "Sincronizar" si sospecha que los indicadores "Universo"/"Cuadro" están desactualizados.
4. **Ante una avería:** ingresa a Averías, usa "Reportar Falla", y luego reasigna manualmente en Programación
   las cajitas afectadas hacia una máquina operativa compatible.
5. **08:51:** el sistema marca alerta para operadores con turno que no han marcado entrada 45 minutos después de
   iniciado el turno día. <!-- fuente: backend/main.py, `_job_tardios_dia` -->
6. **20:08 / 20:10 (lunes a viernes):** se repite el ciclo de asistencia y corrida automática para el turno
   noche, calculando el saldo de trabajo no terminado durante el día. <!-- fuente: backend/main.py,
   `scraper_geo_noche`, `_job_noche`; MAPA_DECISIONES_SPP.md ASG-02 -->
7. **21:21:** alerta de tardanza para el turno noche. <!-- fuente: backend/main.py, `_job_tardios_noche` -->
8. **Cada 30 minutos, todos los días:** el sistema revisa en Cubigest qué etapas ya se ejecutaron realmente
   (para pintar cajitas grises con candado) y qué averías siguen abiertas. <!-- fuente:
   `_job_verificar_etapas_completadas`, `sync_averias_cubigest` -->
9. **Cada hora, al minuto :30:** se revisa si algún viaje ya se cerró en Cubigest, para marcar sus eventos como
   completados. <!-- fuente: backend/main.py, `_job_verificar_its_cerradas` -->

---

## 5. Colores y estados de las cajitas y máquinas

**Desde el cambio de agrupación (29-09-2026), estos colores y candados se ven sobre el GRUPO completo (la
cajita), no sobre una etiqueta suelta** — verificado en código: el grupo hereda el estado, color de ribete y
color de calidad de la **primera etiqueta del grupo** (`_construir_evento_grupo`, `dict(primero)` en
`programacion.py`), y el Gantt lee ese único valor (`ev.estado`, `ev.calidad_acero`, etc. en
`GestorProgramacion.tsx`). Cuando todas las etiquetas del grupo están en el mismo estado (lo esperable en la
inmensa mayoría de los casos: si una etapa se ejecutó, normalmente se ejecutó para todo el grupo a la vez), esto
equivale en la práctica a "el color es del grupo". **Por confirmar (caso límite, no verificado en datos reales):**
si alguna vez un grupo queda con etiquetas en estados distintos entre sí (por ejemplo, solo una etiqueta del
grupo ya fue confirmada como ejecutada en Cubigest y el resto no), el color que se ve seguiría el de la primera
etiqueta del grupo, no un resumen de todas — ver punto nuevo en la sección 10.

| Elemento | Significado | Fuente |
|---|---|---|
| Cajita gris con ícono de candado | Etapa ya confirmada como ejecutada en Cubigest, para (al menos) la primera etiqueta del grupo; no se puede mover; permanente. | `GestorProgramacion.tsx`, `isEtapaCongelada`; `programacion.py`, `_construir_evento_grupo` |
| Cajita verde (borde `#16a34a`) | Trabajo completado (IT/viaje cerrado), según el estado de la primera etiqueta del grupo. | `GestorProgramacion.tsx`, `isCompletado` |
| Ribete rojo | Fecha vencida (atrasada). | `GestorProgramacion.tsx`, `esVencido` |
| Ribete naranja | Fecha próxima a vencer (inminente), o máquina detenida por avería. | `GestorProgramacion.tsx`, `esInminente` / `isDetenida` |
| Ribete verde | Sin urgencia de fecha y acero **soldable** (calidad con sufijo S, por ejemplo A630S o A440S). | `GestorProgramacion.tsx`, función `esSoldable` (corregido por Miaude 28-09; la auditoría lo había dejado sin explicar) |
| Ribete gris | Sin urgencia de fecha y acero no soldable. | `GestorProgramacion.tsx`, valor por defecto |
| Borde punteado ámbar (2px) | Acero que no es calidad A630 (calidad no estándar). | `GestorProgramacion.tsx`, `esNoA630` |
| Fila de máquina en fondo ámbar, badge "SEMIOPERATIVA" | Máquina con avería parcial (semi-operativa). | `GestorProgramacion.tsx` líneas 648-649 |
| Estado de máquina en Averías: DET / SEMI / ING / OP | Detenida / Semi-operativa / Ingresada / Operativa — etiqueta que usa Cubigest. | `GestorAverias.tsx`, `ESTADO_CUBIGEST_LABEL` |
| Badge "Universo hace X min" / "Cuadro hace X min" en verde | Esa fuente de datos está actualizada. | `SyncEstado.tsx` |
| Mismo badge en ámbar con ícono de alerta | Esa fuente está desactualizada (`desactualizado: true`). | `SyncEstado.tsx` |

Los estados "no liberada" y "adelanto de trabajo futuro" mencionados en versiones anteriores del manual existen
en el código como señales internas (`viene_de_futuro`, indicador de orden adelantada), pero su representación
visual exacta en pantalla **queda por confirmar** con una captura real, porque no se alcanzó a verificar el
estilo exacto (color/ribete) en esta revisión. <!-- fuente parcial: GestorProgramacion.tsx comentarios líneas 59-65, 363-365 -->

---

## 6A. Turnos, horarios y colación

*(Sección agregada por Miaude el 28-09 tras detectar que la versión anterior remitía a "horarios" sin explicarlos.)*

El SPP trabaja con dos turnos, **Día** y **Noche**. El turno Noche empieza en la fecha indicada y termina de
madrugada del día siguiente.

**¿Qué horario usa el Motor para programar?** Toma el primero disponible de esta lista:
1. **Horario real de los colaboradores del turno**, registrado en el SPP a partir de GeoVictoria (se toma el horario
   más frecuente de esa fecha). Al inicio se le suman 15 minutos y al término se le restan 15 (regla B35: evita
   programar trabajo en el cambio de turno). <!-- fuente: backend/routers/programacion.py `_ventana_desde_turnos_programados` -->
2. Si no hay datos del punto 1: el horario que informa directamente GeoVictoria, con la misma ventana de ±15 minutos.
   <!-- fuente: `_resolver_ventana_override` (docstring B35); la lectura exacta de `_ventana_desde_geovictoria` no se revisó línea a línea -->
3. Si tampoco hay datos: la **jornada configurada para la sucursal** en el sistema (horario por día de la semana).
   <!-- fuente: backend/motor_v2.py `_get_config_turno`, prioridad 2 (`get_jornada`) -->
4. Si no existe configuración: los **valores de respaldo**: turno Día 08:15 a 17:45 (viernes hasta 16:45); turno Noche
   20:15 a 05:45 (viernes hasta 04:45). <!-- fuente: backend/motor_v2.py `_get_config_turno`, prioridad 3 -->

**Colación:** por defecto 13:00 a 14:00 en el turno Día y 01:00 a 02:00 en el turno Noche (se puede configurar por
sucursal). Durante ese bloque ninguna máquina recibe trabajo; en el Gantt aparece marcado como "BREAK".
<!-- fuente: backend/motor_v2.py `_get_config_turno` (break_inicio/break_fin); captura de pantalla de Coronel 27-09 -->

**Cómo verificar el horario que se está usando:** la pantalla Programación muestra el eje horario del turno con la
franja de colación; si el horario real de un día especial (por ejemplo, un turno acortado) no aparece bien, revise
primero que la asistencia del día ya esté cargada desde GeoVictoria.

---

## 6. Cuándo se actualiza cada dato

| Dato | Frecuencia / disparador | Dónde se ve |
|---|---|---|
| Asistencia (GeoVictoria) | Automático 08:08 y 20:08 (L-V); también al presionar "Sincronizar" | Presencia de operadores en Programación |
| Corrida del Motor (turno Día) | Automático 08:10 (L-V, sin feriados CL); manual con "Reprogramar" | Gantt de Programación |
| Corrida del Motor (turno Noche) | Automático 20:10 (L-V, sin feriados CL); manual con "Reprogramar" | Gantt de Programación |
| Etapas ejecutadas confirmadas en Cubigest (candado gris) | Automático cada 30 minutos | Gantt de Programación |
| Averías Cubigest | Automático cada 30 minutos (ventana de 3 días para las ya resueltas; las abiertas se traen siempre) | Pantalla Averías |
| ITs/viajes cerrados en Cubigest | Automático cada hora, minuto :30 | Gantt (marca eventos como completados) |
| Alertas de tardanza | Automático 08:51 (turno día) y 21:21 (turno noche), L-V | (no relevado en esta revisión dónde se listan en pantalla — por confirmar) |
| Indicadores "Universo" / "Cuadro" | Botón "Sincronizar" (a pedido); la pantalla también refresca su estado cada 60 segundos | Encabezado de Programación |

<!-- fuente: backend/main.py (cron jobs), backend/routers/averias.py, SyncEstado.tsx -->

Todas las corridas automáticas del Motor (día y noche) **omiten los feriados de Chile** y no corren fines de
semana. <!-- fuente: backend/main.py, `_job_dia`/`_job_noche`, `holidays_lib.Chile` -->

---

## 7. Preguntas frecuentes

**1. ¿Por qué el Planificador no asignó trabajo a una máquina si había piezas pendientes en la Bolsa?**
Revise: (a) si el operador calificado para esa máquina marcó asistencia; (b) si el diámetro o la forma de la
pieza son incompatibles con las restricciones configuradas de esa máquina; (c) si la máquina está con avería
activa (manual o Cubigest). <!-- fuente: ASG-03, ASG-12, GestorProgramacion.tsx mensajes de rechazo -->

**2. Si reasigno una cajita a mano, ¿la corrida automática de la noche (o del día) la respeta?**
**No siempre — corrección importante respecto de v1.** Esto no cambió con el cambio de agrupación del 29-09: el
mecanismo de "posiciones manuales pegadas" (sticky) es una capa del Motor que no fue tocada por ese cambio; lo
único distinto es que ahora la posición pegada se guarda con el identificador de la primera etiqueta del grupo,
en vez de con el de una etiqueta suelta, para que siga funcionando igual con la nueva cajita-grupo.
<!-- fuente: MAPA_DECISIONES_SPP.md GAN2-07 --> Depende de cómo se vuelva a generar la programación:
- Si usted mismo presiona **"Reprogramar"** en pantalla, el sistema sí vuelve a aplicar sus movimientos
  manuales guardados (posiciones "pegadas") sobre el resultado nuevo del Motor.
  <!-- fuente: backend/routers/programacion.py, bloque "Aplicar posiciones manuales (sticky cajitas)",
  función `generar_programacion`, líneas ~1415-1450 -->
- **Pero la corrida automática de las 08:10/20:10 no ejecuta ese mismo camino de código**: llama directamente
  al Motor (`programar_turno`) y reemplaza toda la programación guardada de esa sucursal/turno/fecha con el
  resultado nuevo, **sin volver a aplicar los movimientos manuales guardados**. Solo se preserva el candado
  gris de las etapas ya confirmadas por Cubigest (que usa un mecanismo distinto e independiente).
  <!-- fuente: backend/main.py, función `_ejecutar_generacion`, líneas 141-228; confirmado por comparación
  directa con `generar_programacion` en backend/routers/programacion.py — el bloque de posiciones manuales no
  aparece en `_ejecutar_generacion` -->
- **En la práctica (alcance real, verificado por Miaude el 28-09):** cada corrida automática genera y guarda
  solamente el plan **de su propio turno** (la de las 08:10 el turno Día; la de las 20:10 el turno Noche) y no
  modifica el plan guardado del otro turno. Por eso un movimiento manual hecho durante el turno Día **se
  conserva** aunque después corra la corrida de las 20:10: queda guardado y se recupera al volver a abrir la
  pantalla. Lo que sí se sobrescribe es un ajuste manual hecho **antes** de la corrida automática de ese mismo
  turno y fecha (por ejemplo, un movimiento hecho a las 07:45 con "Reprogramar" queda reemplazado a las 08:10),
  y lo mismo ocurre con la asignación manual de operadores por jornada, que solo aplica el botón "Reprogramar".
  Regla práctica: haga sus ajustes después de que corra la generación automática de su turno.
  <!-- fuente: backend/main.py `_job_dia` (turno "dia") / `_job_noche` (turno "noche") → `_ejecutar_generacion`;
  backend/routers/programacion.py: reprogramar actualiza programacion_guardada (turno del movimiento) -->
  Ver detalle en `VERIFICACION_MANUAL_USUARIO.md`.

**3. ¿Qué hago si una máquina se detiene a mitad de turno por falla mecánica?**
Vaya a **Averías**, presione **"Reportar Falla"**, seleccione la máquina y describa el síntoma. Luego, en
Programación, arrastre las cajitas afectadas hacia otra máquina compatible y operativa.

**4. ¿Por qué una IT no aparece en Vista Semanal ni en Próximas Semanas?**
Puede tener una fecha de despacho a más de 60 días, o estar en la categoría "atrasada más de 30 días", que el
sistema trata como suciedad de datos y excluye de las vistas de demanda. Revise el contador de ITs excluidas que
se muestra junto a la leyenda de cada pantalla. <!-- fuente: UNI-01, UNI-03, UNI-04 -->

**5. ¿La pantalla de Producción por Máquina decide a qué máquina se manda un trabajo?**
No. Es solo consulta histórica de referencia; el Motor decide de forma independiente, con sus propias reglas
(sección 3.4). <!-- fuente: PRO-11 -->

---

## 8. Glosario

- **IT (Instrucción de Trabajo):** orden de fabricación emitida por Cubigest.
- **Viaje:** subdivisión de una IT orientada al despacho en camión.
- **Etiqueta:** unidad física mínima de fabricación, con sus kilos exactos (`KgsPaquete`).
- **Cajita:** representación en el Gantt (y en la Bolsa de Trabajo) de un **grupo de etiquetas** del mismo
  viaje/IT y la misma máquina que comparten calidad de acero, diámetro, forma de pieza y largo (o el subconjunto
  más alto posible de esos criterios); ya no es una etiqueta suelta. Ver definición completa en la sección 2.
- **Etapa:** un paso del proceso de una etiqueta (p. ej. corte, doblado).
- **Bolsa de Trabajo:** etiquetas sin máquina asignada en el turno actual.
- **el Motor:** el cálculo de asignación de trabajos a máquinas/operadores.
- **Hebras (multiplicidad):** cantidad de barras que una máquina procesa a la vez en un mismo diámetro.
- **Acero delgado (AD):** diámetro ≤ 16 mm. **Acero grueso (AG):** diámetro > 16 mm.
- **FP-LC:** Fierro en Punta - Largo Comercial; despacho directo, fuera del SPP.
- **Candado gris:** marca visual de una etapa ya confirmada como ejecutada en Cubigest; la cajita queda
  bloqueada permanentemente.
- **Universo / Cuadro:** las dos fuentes de datos que el botón "Sincronizar" actualiza (Cuadro = Cuadro de
  Programación OptiSteel).

---

## 9. Limitaciones conocidas

1. **Domingos y feriados de Chile:** no hay corrida automática del Motor; el Gantt puede aparecer vacío o sin
   cambios respecto del día anterior. Esto es esperado, no una falla. <!-- fuente: `_job_dia`/`_job_noche`,
   `holidays_lib.Chile` -->
2. **Cubigest puede fallar de forma intermitente** (error SSL documentado); cuando eso ocurre, las averías desde
   Cubigest, el candado gris y el Cuadro OptiSteel pueden mostrar datos desactualizados hasta que la conexión se
   recupere. El sistema reintenta solo en su próximo ciclo automático. <!-- fuente: LOG_CAMBIOS_2026.md
   27-09-2026 -->
3. **Movimientos manuales y corrida automática nocturna:** ver pregunta 2 de la sección 7 — es la limitación más
   importante detectada en esta revisión y debería comunicarse explícitamente a los jefes de planta.
4. **Reinicio del sistema:** las asignaciones que viven solo en memoria (no en la tabla de programación guardada
   ni en `programacion_manual`) podrían no reflejarse hasta la próxima corrida si el backend se reinicia entre
   medio. La premisa de diseño es que el sistema opera de forma continua, sin reinicios frecuentes.
   <!-- fuente: agentes/CCa_gantt_etapa_gris_20260926.md, addendum Montu 26-09 -->
5. **Producción por Máquina (versión A):** usa un método estadístico simplificado (delta crudo); el método más
   riguroso (FASE3) todavía no está en producción. <!-- fuente: PRO-13 -->

---

## 10. Por confirmar

- Estilo visual exacto (color/ribete) de las cajitas "no liberada" y "adelanto de trabajo futuro" en el Gantt
  — se sabe que la señal existe en el código, no se verificó su representación visual con una captura real.
- Criterio exacto que determina cuándo una cajita muestra el aviso "⚠ ATRASO".
- Detalle pantalla por pantalla de los Gestores de Operadores, Piezas y Materia Prima.
- Dónde exactamente en pantalla se ven las alertas de tardanza (08:51 / 21:21).
- **(Agregado 29-09-2026, tras cajita=viaje):** si un grupo de etiquetas queda con estados mezclados (por
  ejemplo, una sola etiqueta del grupo ya confirmada como ejecutada en Cubigest y el resto no), el código
  muestra el color/candado de la **primera etiqueta del grupo**, no un resumen de todas — se verificó esto en el
  código (`_construir_evento_grupo` en `programacion.py`, sección 5), pero no se verificó con un caso real en
  planta si esta mezcla de estados realmente llega a ocurrir ni con qué frecuencia.
