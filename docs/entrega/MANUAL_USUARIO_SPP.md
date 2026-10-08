# Manual de Usuario — Sistema Planificador de la Producción (SPP)

**Versión:** 1.0 (Entrega 24 de septiembre de 2026)  
**Destinatarios:** Gerencia de Operaciones, Gerencia de Logística y Jefes de Planta (Cerrillos, Calama, Coronel) — Torres Ocaranza  
**Sistema:** Sistema Planificador de la Producción (SPP / el Planificador)

---

## 1. ¿Qué es el SPP y qué decide?

El **Sistema Planificador de la Producción (SPP)** es una herramienta operativa diseñada para apoyar la toma de decisiones diarias en las plantas de Torres Ocaranza (Cerrillos, Calama y Coronel). Su objetivo es organizar el trabajo diario de las máquinas y de los operadores presentes para maximizar la producción efectiva de cada jornada laboral.

### Lo que el SPP SÍ decide
1. **Asignación eficiente de trabajos a máquinas:** Determina qué máquina específica debe procesar cada etiqueta de producción, respetando las capacidades técnicas de los equipos, los diámetros permitidos y las restricciones físicas de cada máquina.
2. **Asignación de operadores:** Asigna operadores disponibles y calificados a cada máquina según su competencia técnica y su asistencia real en la jornada.
3. **Secuencia de fabricación:** Ordena las tareas en el tiempo para minimizar detenciones improductivas, penalizando cambios innecesarios de diámetro en una misma máquina (regla de setup de 15 minutos).
4. **Respeto a las etapas de fabricación:** Si una pieza ya fue cortada en una etapa previa (avance mayor al 0%), el Planificador reconoce que esa etapa ya se cumplió y programa directamente la etapa siguiente (por ejemplo, el doblado).

### Lo que el SPP NO decide (Regla fundamental ASG-01)
> **Principio de Operación (Regla ASG-01):**  
> El SPP **no decide QUÉ se produce ni cuándo se despacha al cliente**. El programa de producción y las prioridades de entrega las dictan exclusivamente los sistemas centrales de la empresa (**Cubigest y OptiSteel**).  
> El valor del SPP radica en encontrar la mejor combinación operativa entre los trabajos ya liberados y las máquinas/operadores de la planta para cumplir el programa en el menor tiempo posible y con la mayor productividad de la jornada.

---

## 2. Pantalla por Pantalla

### 2.1 Programación (Carta Gantt y Cajitas)

Esta es la pantalla principal de trabajo del jefe de planta. Muestra el cronograma del turno en un formato visual tipo Carta Gantt interactiva.

- **Filas del Gantt:** Cada fila representa una máquina activa de la planta (por ejemplo: *Dobladora Tecmor S40 1*, *EURA 20_3*, *Línea de Corte*). Las máquinas sin trabajo asignado se muestran disponibles.
- **Eje horizontal:** Representa la línea de tiempo de la jornada de trabajo, demarcando la hora de inicio, el horario de colación y la hora de término de la jornada.
- **Cajitas de trabajo:** Cada bloque o "cajita" sobre la línea de una máquina representa un lote de fabricación asociado a un viaje y obra.
  - **Color por obra:** Las cajitas se pintan automáticamente con un color persistente según la obra de destino, lo que permite al jefe de planta identificar a simple vista la continuidad de un pedido.
  - **Información visible en la cajita:** Muestra el código de viaje, nombre de la obra, kilos totales del paquete, diámetro del acero, cantidad de piezas y duración estimada.
  - **Identificador de fabricación en la cajita:**
    > **[PENDIENTE DE CIERRE OLA 3 — Requerimiento B42]:**  
    > En la versión desplegada actual, la cajita muestra el código genérico de TAG. Conforme a lo acordado con la jefatura de planta (Minuta Cerrillos 22-09), se encuentra en construcción el cambio para que la cajita exhiba directamente el **número de etiqueta de fabricación**, que constituye la unidad mínima de control en piso.

#### Detalle y ajuste manual de la tarea (Modal al hacer clic)
Al hacer doble clic sobre cualquier cajita del Gantt, se despliega una ventana modal con los datos exhaustivos del trabajo:
- Obra, cliente y código de viaje.
- Diámetro del fierro (\(\varnothing\) en mm) y calidad del acero.
- Kilos y número de piezas del paquete.
- Máquina asignada y operador responsable.
- Hora programada de inicio y término.
- **Ajuste manual de duración:**
  > **[PENDIENTE DE CIERRE OLA 3 — Requerimiento B44(a)]:**  
  > En proceso de habilitación el campo **"Ajustar duración del trabajo (en minutos)"** dentro del modal. Permitirá al jefe de planta sobrescribir puntualmente el tiempo calculado por el sistema (por ejemplo, corregir de "todo el día" a 90 minutos si conoce una condición especial de fabricación).

#### Reorganización manual (Drag & Drop en vivo)
El jefe de planta mantiene siempre el control de la operación. Puede arrastrar una cajita para:
1. **Moverla entre máquinas compatibles:** Si una dobladora se satura o se prefiere derivar carga, se puede arrastrar el trabajo a otra máquina que acepte el diámetro y la forma. El sistema valida la compatibilidad y no permite soltar trabajos en máquinas no autorizadas.
2. **Reordenar la secuencia:** Es posible cambiar el orden de fabricación dentro de la misma máquina.
3. **Piso de hora real:** Si se reasigna o mueve un trabajo durante el transcurso del turno, el sistema fija automáticamente como hora de inicio el momento actual (*Math.max(ahora, calculado)*), evitando programaciones en el pasado.

---

### 2.2 Bolsa de Trabajo (Pendientes)

La Bolsa de Trabajo agrupa todas las piezas y paquetes que requieren fabricación pero que aún no han sido asignados a una máquina en el turno en curso.

- **¿De dónde viene el trabajo de la Bolsa?**
  1. **Órdenes de días futuros:** Trabajos programados en el Cuadro OptiSteel para fechas posteriores cuyo avance de fabricación es menor al 100%.
  2. **Remanentes del turno actual:** Piezas de la jornada que no alcanzaron a entrar en el turno de hoy por capacidad de tiempo de las máquinas o de los operadores.
- **Actualización dinámica:** La Bolsa consulta el estado de avance en Cubigest, reflejando altas y cierres conforme avanza la producción real en planta.
- **Asignación directa desde la Bolsa al Gantt:** El jefe de planta puede tomar cualquier trabajo de la Bolsa de Pendientes y arrastrarlo hacia la línea de una máquina en el Gantt. Al soltarlo, el trabajo se agenda inmediatamente en la máquina elegida y desaparece de la Bolsa, sin duplicaciones.
- **Adelanto de trabajo futuro:**
  > **[PENDIENTE DE CIERRE OLA 3 — Requerimiento B43]:**  
  > Se encuentra en diseño e implementación un **indicador visual (ribete o distintivo de color)** en las cajitas para identificar claramente aquellas órdenes de producción que provienen de días futuros y que se han adelantado para aprovechar la capacidad ociosa de minutos-hombre de la jornada (articulación con el cálculo de capacidad de la planta). Aplica a las 3 plantas de Torres Ocaranza.

---

### 2.3 Vista Semanal y Próximas Semanas

- **Vista Semanal:** Presenta una matriz consolidada de los compromisos de producción de los 7 días de la semana (Lunes a Domingo), permitiendo a la jefatura de operaciones y planta contrastar el volumen global comprometido frente a lo que se ha ido ejecutando.
- **Próximas Semanas (Calendario Futuro):** Agrupa las ITs (Instrucciones de Trabajo) pendientes de fabricar en un horizonte de 3 semanas hacia adelante, clasificadas por su fecha estimada de despacho. Permite a los supervisores anticipar requerimientos de dotación o identificar cuellos de botella de capacidad con días de antelación.

---

### 2.4 Producción por Máquina (Estimación Histórica)

Ubicada en el menú lateral bajo el nombre **"Producción por Máquina"** (título interno: *Tiempos por Máquina (estimado)*).

#### ¿Para qué sirve?
Permite a los jefes de planta y gerentes consultar cuál ha sido el rendimiento histórico real en **toneladas por hora (ton/h)** de cada máquina para una combinación específica de:
- **Forma** (código de forma geométrica del acero).
- **Diámetro** (\(\varnothing\) en mm).
- **Largo aproximado de la pieza** (opcional, en mm o metros).
- **Sucursal y período de análisis** (meses de historial).

*Ejemplo real verificado:*  
Para **Forma 1 (recto / corte), \(\varnothing\) 16 mm en Cerrillos**: la máquina *EURA 20_3* presenta un rendimiento histórico mediano de **0,53 ton/hora**, con un rango típico observado entre **0,12 y 1,64 ton/hora** (sobre una muestra de 1.727 intervalos históricos).

#### ¿Cómo se interpreta el rango P25 – P75?
El sistema informa siempre la **mediana** acompañada del rango **P25 – P75** (percentil 25 al percentil 75).
- La **mediana** es el valor intermedio típico alcanzado en la historia de la planta.
- El **rango P25–P75** representa la franja donde se concentró el 50% central de las jornadas reales.
- *¿Por qué no se muestra un "porcentaje de confianza" o un promedio clásico?*  
  Porque el análisis estadístico de los datos reales de las 32 máquinas de Torres Ocaranza demostró que la producción no sigue una campana de Gauss; existen días con pedidos cortos y días de grandes tiradas (comportamiento bimodal). Prometer un porcentaje teórico de confianza sería estadísticamente falso. El rango empírico P25–P75 es transparente y describe fielmente lo que ha ocurrido en la planta.

#### Avisos e indicadores en pantalla
| Aviso en pantalla | ¿Cuándo aparece? | ¿Qué debe entender el usuario? |
|---|---|---|
| **Datos insuficientes (N < 15)** | La máquina tiene menos de 15 registros históricos válidos para esa forma y diámetro. | La máquina se muestra en la tabla para constancia de que puede procesar la pieza, pero no se publica un número de ton/h porque una muestra tan pequeña induciría a error. |
| **Fuera del rango histórico de esta máquina** *(tolerancia \(\pm\)10%)* | El peso por barra calculado para el largo pedido queda bajo el percentil 5 o sobre el percentil 95 de lo procesado por esa máquina en su historia. | La máquina habitualmente no fabrica piezas de esa longitud o peso. El valor de ton/h mostrado corresponde al grupo más cercano y debe usarse con precaución. *(Ejemplo: en Cerrillos \(\varnothing\)16, una barra estándar de 12 m pesa 19,0 kg y entra en rango normal; en cambio, 14 m o 30 m se alertan como fuera de rango).* |
| **Rango no evaluable en esta máquina** | Ocurre en líneas de corte (Línea de Corte Cerrillos, Carro de Corte Calama, Línea Corte Coronel). | En estas máquinas el registro de "piezas por paquete" en los partes no representa barras individuales homogéneas. Por tanto, no se calcula el filtro por barra unitaria y se entrega el rendimiento histórico global de la máquina. |
| **Sin ajuste por largo (pocos datos)** | Se especificó un largo de pieza, pero hay menos de 30 registros históricos en la combinación. | La muestra no alcanza para segmentar por grupos de peso; se entrega el promedio mediano del historial completo. |

#### Lo que esta pantalla NO es
- **No es el ruteo automático del Planificador:** La pantalla lista todas las máquinas que en el pasado han procesado esa forma; no significa que el Planificador vaya a enviar el trabajo obligatoriamente a esa máquina hoy.
- **No alimenta directamente al optimizador del Motor:** Es una herramienta de consulta y referencia para la toma de decisiones del personal de planta.

---

### 2.5 Gestor de Máquinas y Hebras

En esta pantalla los jefes de planta administran los parámetros operativos de sus equipos:
- **Catálogo de máquinas activas:** Cada planta gestiona únicamente su dotación autorizada:
  - *Cerrillos (10 máquinas activas):* Curvadora CER40 1 Schnell, Dobladora Tecmor S40 1, Dobladora Tecmor S40 2, EURA 16, EURA 20_1, EURA 20_3, LINEA DE CORTE, PRIMA 3D, Robomaster 55, Robomaster 60.
  - *Calama (8 máquinas activas):* Carro de Corte, COIL 14, COIL 14 M, Cortadora Manual, Dobladoras, EURA 16, EURA 20_2, Robomaster 60.
  - *Coronel (9 máquinas activas):* Cortadora Manual, Curvadora 1, Curvadora 2, Dobladora 2, Dobladora 3, Dobladora 4, ESTRIBADORA TJK 1, ESTRIBADORA TJK 2, Linea Corte Coronel.
- **Matriz de diámetros:** Define qué diámetros de barra (\(\varnothing\) 8 a 36 mm) puede doblar o cortar cada máquina.
- **Matriz de Hebras (Multiplicidad):**  
  Indica cuántas barras en paralelo puede procesar la máquina al mismo tiempo para cada diámetro.  
  *Importancia operativa (mejora HEBRAS-01):* El Planificador ahora lee directamente los valores reales configurados por los jefes de planta en el sistema. Por ejemplo, en Coronel la *Dobladora 2* está configurada para trabajar con **8 hebras en \(\varnothing\) 10 mm, 6 hebras en \(\varnothing\) 12 mm y 3 hebras en \(\varnothing\) 16 mm**. El Planificador considera esta capacidad múltiple al estimar la duración del lote.
- **Restricciones técnicas por máquina:**  
  El sistema valida automáticamente restricciones físicas para no programar piezas inviables:
  - *PRIMA 3D (Cerrillos):* Cota A máxima de 2.000 mm.
  - *Robomaster 55 y 60 (Cerrillos):* Pata máxima de 2.500 mm.
  - *Robomaster 55 (Cerrillos):* Exclusivo para dobleces a 90°.
  - *Curvadora CER40 (Cerrillos):* Exclusiva para anillos y espirales.
  - *EURA 20_1 (Cerrillos):* No procesa anillos.

#### Decisión Operativa Clave: FP-LC NO es una máquina del SPP
> **Decisión de Negocio (23-09-2026, Gustavo / TO):**  
> El concepto **FP-LC (Fierro en Punta - Largo Comercial, piezas rectas de 6.000 a 12.000 mm en diámetros delgados)** es un *despacho directo* que va desde la bodega de materias primas directo al camión.  
> **No pasa por ningún proceso de corte ni doblado en máquina de planta.**  
> En consecuencia, **FP-LC ha sido completamente excluida del SPP**:
> 1. Sus etiquetas no entran al Motor de programación ni a la Bolsa de Trabajo.
> 2. No figura como máquina en el Gantt ni consume capacidad ni operarios.
> 3. No aparece en el Gestor de Máquinas.
> 4. No es posible reasignar manualmente piezas a FP-LC.

---

### 2.6 Averías y Detenciones

Permite declarar contingencias mecánicas o eléctricas en los equipos de planta:
- **Registro de avería:** El jefe de planta marca una máquina como averiada indicando el motivo y la hora estimada de detención.
- **Efecto en la programación:** La máquina queda bloqueada para nuevas asignaciones. El sistema permite normalizar la avería cuando el equipo retorna a servicio y reprogramar los trabajos pendientes hacia otras máquinas operativas.
- **Integración con Cubigest:**
  > **[PENDIENTE DE CIERRE OLA 3 — Requerimiento B39]:**  
  > Se encuentra en desarrollo la captura automática del estado de máquinas con averías registradas en Cubigest (por ejemplo, la situación de la *Línea de Corte Coronel* o la *Dobladora 16 en Cerrillos*), de modo que el SPP refleje de manera desatendida las indisponibilidades cargadas en el sistema central.

---

## 3. Horarios y Turnos de Producción

El SPP opera bajo un modelo de dos turnos productivos: **Turno Día** y **Turno Noche**.

### Reglas de Horario y Ventana Operativa
1. **Turno Día:**  
   - Horario base estándar: **08:15 a 17:45** (Lunes a Jueves).  
   - **Viernes:** Salida temprana a las **16:45**.  
   - **Colación:** 60 minutos obligatorios entre **13:00 y 14:00**.
2. **Turno Noche:**  
   - Horario base estándar: **20:15 a 05:45** (entra en la noche de la fecha indicada y concluye en la madrugada del día siguiente).  
   - **Viernes noche:** Salida a las **04:45**.  
   - **Colación:** 60 minutos obligatorios entre **01:00 y 02:00**.
3. **Criterio de Tolerancia \(\pm\)15 minutos (Regla B35):**  
   Para evitar asignar trabajos en los momentos de cambio de ropa, entrega de turno o charla de seguridad de 5 minutos, la jornada productiva efectiva calculada por el sistema inicia 15 minutos después del toque de entrada oficial y concluye 15 minutos antes de la hora contractual de salida.
4. **Prioridad de Horarios:**  
   - **Prioridad 1:** Marcaciones biométricas reales recibidas desde **GeoVictoria** (con la ventana de \(\pm\)15 minutos aplicada).
   - **Prioridad 2:** Horarios programados en la matriz de turnos de la planta.
   - **Prioridad 3:** Horarios de respaldo estándar indicados arriba.

---

## 4. Preguntas Frecuentes (FAQ) de Jefes de Planta

### 1. ¿Por qué el Planificador no asignó trabajo a una dobladora si tenía piezas pendientes en la Bolsa?
Verifique tres causas habituales:
- **Falta de operador presente:** Si el operador calificado para esa máquina no marcó asistencia en GeoVictoria (o está registrado con licencia/falta), la máquina no se programa para evitar planes fantasmas.
- **Incompatibilidad de forma o diámetro:** Las piezas pendientes tienen cotas, formas o diámetros que superan las restricciones técnicas configuradas en el Gestor de Máquinas.
- **Etapa de corte no finalizada:** Si la pieza es de acero grueso y aún no ha sido cortada en la máquina de corte (avance 0%), no puede entrar a la dobladora.

### 2. Si reasigno una cajita a mano, ¿el sistema la vuelve a cambiar en la noche?
No. Las asignaciones manuales realizadas por la jefatura quedan protegidas en el historial de la jornada. Cuando el sistema corre el proceso automático de las 20:10 (turno noche), calcula el saldo de producción pendiente respetando los eventos ya asignados y ejecutados.

### 3. ¿Qué pasa si una máquina se detiene a mitad de turno por falla mecánica?
El jefe de planta debe ingresar al menú **Averías**, marcar la detención de la máquina y registrar el incidente. Luego, desde la pantalla de Programación, puede arrastrar las cajitas comprometidas hacia otra máquina libre que posea herramientas para esa forma y diámetro.

### 4. ¿Por qué una pieza de 12 metros de largo me aparece "Fuera de rango" en la pantalla de Producción por Máquina?
En la versión actual de la pantalla (versión A), el sistema cuenta con un margen de tolerancia del 10% sobre los registros históricos. Una barra estándar de 12 m en \(\varnothing\) 16 mm (19,0 kg) está dentro del rango normal; sin embargo, barras de 14 m o piezas especiales de gran longitud activarán el aviso indicando que históricamente el taller no ha fabricado esa dimensión en esa máquina específica.

---

## 5. Glosario Operativo

- **IT (Instrucción de Trabajo):** Orden de fabricación maestra emitida por Cubigest que agrupa los elementos requeridos por el cliente para una estructura o faena.
- **Viaje:** Subdivisión logística y operativa de una IT orientada al despacho en camión hacia la obra.
- **TAG:** Identificador técnico del conjunto o paquete dentro de la ingeniería de despiece.
- **Etiqueta:** Unidad física mínima de fabricación y rotulación adherida al atado de fierro en planta. Registra los kilos exactos del paquete (*KgsPaquete*).
- **Hebras (Multiplicidad):** Cantidad de barras de acero del mismo diámetro que una máquina puede cortar o doblar de manera simultánea en una sola pasada.
- **Bolsa de Trabajo:** Repositorio visible en pantalla donde se concentran los paquetes pendientes de asignar a máquina.
- **Colación:** Período formal e intransferible de descanso de 60 minutos (13:00–14:00 en turno día; 01:00–02:00 en turno noche) donde se detiene la asignación de producción.
- **Acero Delgado (AD):** Fierro de diámetro menor o igual a 16 mm (\(\varnothing \le 16\)), comúnmente procesable en estribadoras o máquinas automáticas desde rollo.
- **Acero Grueso (AG):** Fierro de diámetro mayor a 16 mm (\(\varnothing > 16\)), que habitualmente exige corte previo en barra recta y posterior doblado.
- **FP-LC:** Fierro en Punta - Largo Comercial. Material que se despacha en largos comerciales estándar sin procesamiento en máquinas de la planta.
