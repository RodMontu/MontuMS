# Spec — Reparto de trabajo en 2+ máquinas en paralelo (B2)
**Diseño cerrado con Montu, 12-09-2026. Reemplaza el diseño anterior de B2
Fase 0 (toggle proactivo separado) — ver sección "Camino manual" abajo.**

## Problema
El Motor de OF asigna cada trabajo a una sola máquina. Hay trabajos tan
largos/complejos que ocupan toda la jornada o se pasan de ella — en la
práctica (datos reales del Motor de Tiempos, piloto Cerrillos) ya se reparten
en 2+ máquinas un 11-35% de las veces, sin que el sistema lo proponga ni lo
sepa.

## Comportamiento default
El Motor asigna igual a **una sola máquina** — nunca auto-reparte sin que el
Jefe de Planta lo apruebe.

## Camino automático — alerta por umbral
Umbral doble, sobre el tiempo estimado del trabajo vs. tiempo restante de
la jornada:
- **≥80% de la jornada restante**: alerta suave.
- **100%+ (se pasa de la jornada)**: alerta dura.

Ambas usan la misma mecánica. La alerta aparece en la sección Programación,
dirigida al Jefe de Planta (o quien ejerza su rol), con una propuesta
**concreta**, no genérica: nombra la máquina específica propuesta para
repartir (2da máquina), y deja en el mismo mensaje la opción de extender a
una 3ra máquina.

**Explícitamente descartado**: el sistema NO intenta decidir "si con 2
alcanza" — depende de contexto (operadores disponibles, carga total del
turno) que no es capturable de forma confiable a nivel sistémico. Se
propone, el Jefe decide con su propio criterio.

**Botón**: "Aplicar reparto en paralelo" — explícitamente NO "Reprogramar".
Acotado solo a este cambio puntual (pasar de 1 a 2-3 máquinas) y sus
consecuencias directas, no un recálculo completo del día.

## Camino manual — doble-clic
Independiente del umbral: doble-clic en la "cajita" de cualquier trabajo en
Programación da acceso a la misma opción de repartir en máquinas en
paralelo. Existe porque el Jefe de Planta puede tener criterio de terreno
(decisiones del momento) que el Motor no puede capturar — incluso para
trabajos que no son extremadamente largos según el cálculo del sistema.

**Esto reemplaza el diseño anterior de B2 Fase 0** (un toggle previo,
separado, para marcar proactivamente un trabajo como repartido) — la vía
manual ahora vive directamente en el doble-clic de la cajita, no como un
paso aparte.

## Reglas compartidas por AMBOS caminos (automático y manual)
- **Elegibilidad de máquinas**: mismas reglas que ya rigen la asignación
  normal — diámetro, forma (IdForma), operador disponible y competente
  (B15). El Jefe no puede repartir a una máquina que no calificaría de
  todas formas.
- **Reparto de carga**: partes iguales. 50/50 con 2 máquinas, 33/33/33 con
  3. Nota abierta, no bloqueante: si datos reales del Motor de Tiempos
  muestran que el reparto real no es igualitario (ej. según rendimiento
  relativo de cada máquina), revisar esta regla más adelante — no bloquea
  la implementación inicial.

## Patrón reutilizable
La mecánica de "alerta accionable con propuesta concreta + botón acotado,
distinto de un reprocesamiento completo" se construye como componente
genérico, pensando en futuras alertas del Motor (no exclusivo de este caso).

## Pendiente (Tier 2 — requiere autorización explícita de Montu antes de tocar código)
Implementación concreta en motor_v2.py/programacion.py/frontend, una vez
que la investigación de CCa (solo lectura) traiga las opciones reales de
dónde enganchar cada pieza. Ver handoff/backlog para el resultado de esa
investigación.


---

## Hallazgos técnicos de CCa (solo lectura, 12-09-2026)

**Frontend**: `GestorProgramacion.tsx`, componente `DraggableTimelineEvent`
(línea 268) es la cajita real en el Gantt. Sin `onDoubleClick` en todo el
archivo hoy — libre, sin conflicto. Interfaz `Tarea` (líneas 8-46) no tiene
ningún campo de reparto (`maquinas[]`, `porcentaje_carga`, etc.) — hay que
agregarlos.

**Backend**: `estimar_duracion_min()` (motor_v2.py:486-538) ya calcula
duración por trabajo. El flujo de asignación HOY es binario — cabe entero o
va a `bolsa_sin_asignar` con `"turno_lleno"` (línea 899). No existe ningún
cálculo de "% de jornada restante" — hay que construirlo, engancha justo en
esa línea 899.

**Persistencia**: 4 tablas tocadas. `programacion_manual` tiene PK
`(sucursal_id, turno, fecha, pid)` que asume 1 fila = 1 máquina por trabajo
— **requiere cambio de esquema** (agregar `recurso_id` a la PK o columna de
secuencia) para soportar 2-3 filas por trabajo. Las otras 3
(`programacion_guardada` JSON, `programacion_detalle`,
`historial_asignaciones`) no tienen esa fricción. Ninguna tabla tiene campo
de porcentaje de carga — se agrega en todas.

**Sin confirmar (CCa lo marcó explícito, no asumido)**: otros consumidores
de `programacion_manual`/`programacion_guardada` que asuman 1 fila = 1
máquina (no se revisó el archivo completo de 1572 líneas); si el modal de
detalle del trabajo tiene límite de layout para mostrar 2-3 líneas de
máquina+%.


---

## Cierre de las 2 preguntas abiertas (CCa, 12-09-2026)

**`programacion_manual` — confirmado que SÍ requiere cambio real, no cosmético.**
Sus 3 únicos consumidores (todos en `routers/programacion.py`) asumen 1
fila = 1 pid: el upsert (línea 653, `ON CONFLICT` sobre la PK completa) y
la lectura (línea 903, dict keyed por `pid` — con múltiples filas por pid
se pierden silenciosamente todas menos la última). Cambiar la PK sin tocar
esa lógica de aplicación rompe en silencio, no con error visible.

**`programacion_guardada` — independiente, no bloquea nada.** El `pid` vive
dentro del JSON (`tareas_json`), no como columna — no tiene la misma
invariante de cardinalidad. Tocar `programacion_manual` no la afecta.

**Modal de detalle — no requiere rediseño.** Ya existe un patrón de lista
flexible (`.map()` + scroll, sección "Etiquetas incluidas",
GestorProgramacion.tsx:1492-1533) que se puede replicar para mostrar
máquina+% de carga por cada máquina del reparto. El grid fijo de stats
(líneas 1466-1493) no serviría para esto, pero no hace falta tocarlo — el
bloque nuevo va aparte, entre el grid y la sección ATRASADO.

**Investigación de reparto en paralelo: CERRADA.** Lista para decisión de
implementación (Tier 2) entre Montu y Miaude.


---

## DECISIÓN FINAL — enfoque de implementación cerrado con Montu (12-09-2026)

**Criterio de sugerencia de máquina para la alerta automática: OPCIÓN 1**
(mejor tasa histórica kg/hora del Motor de Tiempos, entre las máquinas
elegibles por diámetro+forma+operador). Fallback si no hay histórico
suficiente para esa combinación: primera máquina elegible libre.

**Esquema:**
- `programacion_manual`: PK extendida a `(sucursal_id, turno, fecha, pid,
  recurso_id)` + columna `pct_carga` (default 100.0). Compatible hacia
  atrás — trabajos sin reparto quedan igual (1 fila, 100%).
- `programacion_guardada` (JSON): sin cambio de esquema. Trabajo repartido
  = 2-3 entradas en `tareas_json`, mismo `etiqueta_id`, distinta
  `nombre_maquina`, campo nuevo `pct_carga`.

**Backend:**
- Umbral 80%/100% calculado justo antes de motor_v2.py:899:
  `pct_jornada = duracion / (hora_fin - cursor)`. Asignación normal sigue
  igual; respuesta lleva `alerta_reparto` (nivel + máquina sugerida por
  criterio kg/hora) si aplica.
- Endpoint nuevo `POST /programacion/aplicar-reparto` — usado por alerta
  automática Y doble-clic manual (mismo flujo, sin duplicar). Valida
  elegibilidad (B15) por máquina, reparte % igual entre las elegidas,
  escribe en ambas tablas.

**Frontend:**
- `Tarea` gana `reparto?: {recurso_id, nombre_maquina, pct_carga}[]`.
- Doble-clic en la cajita (`DraggableTimelineEvent`) abre el mismo flujo.
- Modal: sección nueva con el patrón de "Etiquetas incluidas" (lista+scroll)
  para mostrar máquina+% cuando hay reparto.
- Banner de alerta en Programación + botón "Aplicar reparto en paralelo".

Implementación delegada a CCa en 2 fases (backend primero, verificado, luego
frontend). Ver handoff/log de ejecución para el resultado real.


---

## CORRECCIÓN al comportamiento 100%+ (Montu, 12-09-2026, tras revisar Fase 1)

Cambio real respecto a lo escrito en la primera pasada de Fase 1:

**80-99% (alerta suave)**: sin cambio. Asignación normal a 1 máquina, alerta
informativa, el Jefe decide si aplica el reparto.

**100%+ (se pasa de la jornada)**: YA NO es solo alerta. El trabajo no fitear
completo es argumento suficiente por sí mismo para dividir — el Motor debe
**auto-asignar a 2 máquinas** (no a 3, solo 2) usando el mismo criterio de
sugerencia (kg/hora histórico, fallback primera elegible), en vez de mandarlo
a `bolsa_sin_asignar`. La alerta se muestra igual, en la misma ventana/banner
que las alertas de 80-99%, mostrando al Jefe que ya se auto-repartió y por
qué — pero el trabajo queda asignado, no pendiente.

Este es un cambio de la Fase 1 backend ya escrita — antes de commitear se
corrige y se re-verifica.
