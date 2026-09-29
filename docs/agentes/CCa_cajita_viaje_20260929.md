# Cajita = Viaje (agrupación de etiquetas) — CCa, 2026-09-29

Rama: `unificar-generacion-auto-manual` (base `332f98c`, YA activa en el checkout de
TO). Sin push, sin merge, sin deploy. Solo commits locales.

## 1. Objetivo

Requerimiento literal de Montu: que quede sin efecto el pedido anterior de José
Auger, y que cada "cajita" del Gantt (y de la Bolsa de Trabajo) vuelva a
representar un viaje/IT con las etiquetas que se deban fabricar juntas, en vez
de una cajita = una etiqueta (comportamiento actual, de B42 v2). Agrupación
NO retroactiva: solo desde una fecha de corte que Montu fijará en el deploy.

## 2. Diseño de la solución

### 2.1 Motor de agrupación compartido (`backend/routers/programacion.py`)

Toda la lógica nueva es de presentación/lectura pura sobre datos ya calculados
por el Motor o ya traídos de Cubigest — **no toca `motor_v2.py` ni
`ejecutar_pipeline_generacion`/`generar_programacion`/`_ejecutar_generacion`**
(la unificación auto/manual de CCa-28, ver `CCa_unificar_generacion_20260928.md`).

- `_nivel_criterio_comun(base, candidato) -> int`: jerarquía literal de Montu
  (1 calidad_acero, 2 diametro, 3 id_forma, 4 largo_a) → devuelve 4/3/2/0.
- `_agrupar_consecutivos_por_criterio(items, clave_grupo_fn) -> list[(grupo, nivel)]`:
  motor genérico de escaneo secuencial, usado tanto por el Gantt como por la
  Bolsa (no duplica la lógica). Recorre `items` **en su orden actual, sin
  reordenar**, agrupando elementos consecutivos que comparten `clave_grupo_fn`
  (viaje [+máquina]), maximizando el nivel más alto posible; si extender el
  grupo bajaría el nivel ya alcanzado, cierra el grupo ahí.
- `_agrupar_cajitas_por_viaje(eventos) -> list[dict]`: la función pedida
  explícitamente por el brief. `clave_grupo_fn = (codigo_viaje, recurso_id)`.
- `_construir_evento_grupo` / `_detalle_etiqueta` / `_formatear_rango_etiquetas`:
  arman el evento-cajita resultante (ver §2.2 campos).
- `CAJITA_VIAJE_VIGENTE_DESDE = os.getenv(..., "2099-01-01")` — placeholder
  evidente con TODO, **no fijado por mí** (instrucción explícita del brief).

`obtener_programacion` llama a `_agrupar_cajitas_por_viaje(eventos)` **antes**
de `_aplicar_ajustes_duracion`, y solo si `fecha >= CAJITA_VIAJE_VIGENTE_DESDE`;
antes de esa fecha sirve el formato legado sin pasar por la función nueva. El
ajuste de duración queda automáticamente "sobre el grupo" (confirmación de
Montu, "(a)") porque `id_tarea` del grupo = `id_tarea` de la primera etiqueta,
sin cambio de esquema en `ajustes_duracion`.

### 2.2 Campos nuevos del evento-cajita agrupado

- `id_tarea`/`id` = de la primera etiqueta del grupo.
- `lista_etiqueta_ids` = **reutilizado** (no colisiona: hoy ya es "lista de
  ids de la tarea", con 1 solo elemento por diseño de B42 v2 — extenderlo a
  N elementos para el grupo es la misma semántica, no una redefinición).
- `rango_etiquetas` (nuevo, string ya formateado "45-47,51,67 de 139") — **no
  reutilicé `numero_etiqueta`** para esto: ese campo es `int|None` en todo el
  resto del código (tooltips, `_mapa_numero_etiqueta`, etc.), convertirlo a
  string habría sido una redefinición de tipo con riesgo de romper otros usos
  silenciosamente. `numero_etiqueta`/`total_etiquetas` del grupo quedan igual
  que en la primera etiqueta (compatibilidad con el fallback legado del
  frontend); el header y la cajita del Gantt usan `rango_etiquetas` cuando
  está presente.
- `id_forma`: valor común, o `"varios"` (string) si el grupo solo llegó a
  nivel 2 (1+2, sin forma ni largo comunes) — cambia de tipo `number` a
  `number | "varios"`, documentado en el tipo `Tarea` del frontend.
- `nr_piezas`, `kilos`: suma del grupo.
- `largo_a`: **`None`** a nivel de grupo (requerimiento literal: "ya no va a
  nivel de grupo/resumen") — solo vive en `detalle_etiquetas[].largo_a`.
- `cantidad_etiquetas` (nuevo): cuenta de etiquetas del grupo, distinta de
  `nr_piezas` (piezas).
- `detalle_etiquetas` (nuevo): `[{tag, id_forma, largo_a, nr_piezas, kilos}]`
  ordenado ascendente por `numero_etiqueta` (fallback `etiqueta_id`).
- `fecha_inicio`/`fecha_fin`/`duracion_min`: primero/último/suma — como son
  contiguas por construcción (agrupación solo de consecutivas), `duracion_min`
  recalculado como `fecha_fin - fecha_inicio` coincide con la suma pedida por
  Montu en el dictado.

### 2.3 Bolsa de Trabajo (Pendientes)

`_obtener_pendientes_bolsa_optisteel` ya agrupaba a nivel de datos por IT
(`nro_it`), pero **el frontend dibuja 1 tarjeta por elemento de la lista que
devuelve esta función** (`data.pendientes.map(p => <DraggableTarea tarea={p}/>)`),
no 1 tarjeta por elemento de `tags[]`. Para lograr "una cajita visual por
grupo" también ahí (pedido explícito del brief en el punto 6), la función
ahora devuelve **1 item por GRUPO** (no 1 por IT) cuando el gate de fecha
aplica — reutilizando el mismo `_agrupar_consecutivos_por_criterio` con
`clave_grupo_fn = (codigo_viaje,)` (sin `recurso_id`: la Bolsa todavía no
tiene máquina asignada). El particionado por IT ocurre **antes** de agrupar
(`piezas_por_it`), así que "la agrupación nunca cruza IT" se cumple por
construcción. Antes de `CAJITA_VIAJE_VIGENTE_DESDE` se mantiene exactamente
el formato legado (1 tarjeta por IT completo, con `tags[]` plano) — cero
cambio de comportamiento para fechas ya pasadas/hoy.

**Decisión técnica mía** (no estaba en el brief con estas palabras): el gate
de fecha para la Bolsa se evalúa contra `fecha_despacho` del IT (único dato
de fecha disponible a ese nivel — las piezas de un mismo IT comparten fecha
de despacho en la práctica). Si Montu detecta un caso real donde un mismo IT
tiene piezas con `fecha_despacho` distinta a ambos lados del corte, avisar:
hoy el gate se aplica de forma "todo o nada" por IT, no por pieza.

## 3. Frontend (`GestorProgramacion.tsx`)

- Interfaz `Tarea`: agregados `rango_etiquetas`, `cantidad_etiquetas`,
  `detalle_etiquetas`.
- Cajita del Gantt (`DraggableTimelineEvent`): usa `rango_etiquetas` en vez de
  `numero_etiqueta` cuando está presente (label y tooltip), con fallback al
  formato legado.
- Modal de detalle (1 click, `selectedTarea`):
  - Header: "Etiqueta: N de M" → "Etiquetas: {rango_etiquetas}" cuando el
    evento es un grupo; sin cambios si es legado.
  - Se mantiene el input "Ajustar duración del trabajo (en minutos)" tal cual
    (ya opera sobre `id_tarea`, que para un grupo es el de la primera
    etiqueta — sin cambios de código ahí).
  - Grid de resumen: cuando hay grupo, "Largo" y "Paquete" (que mostraban un
    único valor por etiqueta) se ocultan del resumen — el "IdForma" pasa a
    llamarse "Forma n°" y "Cantidad" pasa a "Cantidad de Etiquetas"
    (=`cantidad_etiquetas`, no `nr_piezas`); "Peso" pasa a "Peso total". Sin
    grupo (formato legado), el grid queda exactamente como estaba.
  - Tabla nueva "Listado de Etiquetas (TAGs)" (columnas TAG/Forma/Largo/
    Cantidad/Peso), ordenada de menor a mayor TAG, visible solo cuando hay
    `detalle_etiquetas`.
- Bolsa de Trabajo: **sin cambios de código** más allá de los ya mencionados
  — al devolver el backend 1 item por grupo, el `.map()` existente
  (`DroppableBacklog` → `DraggableTarea`) ya dibuja 1 cajita por grupo
  automáticamente, y el click abre el mismo modal de detalle (comparte
  `selectedTarea`/`DraggableTarea` con el Gantt). No toqué el layout de texto
  de 3 líneas de `DraggableTarea` (viaje/obra/kg) porque el brief no pidió
  cambiarlo explícitamente y ya muestra `codigo_viaje` correctamente por
  grupo.
- **No toqué** `useGanttZoom.ts` ni Averías/Estado de Máquinas.

## 4. Alcance temporal (NO retroactivo)

`CAJITA_VIAJE_VIGENTE_DESDE` (env var, default `"2099-01-01"` con comentario
`# TODO: Montu debe fijar aqui la fecha real de corte antes del deploy`) en
`backend/routers/programacion.py`. Gatea tanto `obtener_programacion` (contra
`fecha` del turno consultado) como `_obtener_pendientes_bolsa_optisteel`
(contra `fecha_despacho` del IT, ver §2.3). **No fijé una fecha real** —
placeholder evidente, tal como pidió el brief.

## 5. Archivos tocados

- `backend/routers/programacion.py`: constante `CAJITA_VIAJE_VIGENTE_DESDE`;
  funciones nuevas `_formatear_rango_etiquetas`, `_nivel_criterio_comun`,
  `_agrupar_consecutivos_por_criterio`, `_detalle_etiqueta`,
  `_construir_evento_grupo`, `_clave_grupo_evento`, `_agrupar_cajitas_por_viaje`,
  `_construir_grupo_bolsa`, `_construir_item_bolsa`; `obtener_programacion`
  llama a la agrupación antes de `_aplicar_ajustes_duracion`;
  `_obtener_pendientes_bolsa_optisteel` reescrita para devolver 1 item por
  grupo (gated) en vez de 1 por IT. `_tarea_a_evento`, `_aplicar_ajustes_duracion`,
  `_piezas_optisteel_por_viajes`, `ejecutar_pipeline_generacion`,
  `generar_programacion` — **sin tocar**, tal como pedía el brief.
- `frontend/src/components/domain/GestorProgramacion.tsx`: interfaz `Tarea`
  ampliada; cajita del Gantt y modal de detalle actualizados (ver §3).
- `backend/test_cajita_viaje.py` (nuevo) — 16 tests.
- `docs/agentes/CCa_cajita_viaje_20260929.md` (este archivo).

## 6. Tests y verificación

`backend/test_cajita_viaje.py`, mismo patrón que `test_b42v2_etiquetas.py`
(datos sintéticos, sin tocar Cubigest ni la DB real), corrido con el Python
del host TO (`python -m unittest test_cajita_viaje -v`, mismas dependencias
que el contenedor — no rebuild, no toqué el contenedor en ejecución):

```
Ran 16 tests in 0.001s
OK
```

Cobertura pedida explícitamente por el brief:
- `test_grupo_4_de_4_completo` — grupo 4/4 completo.
- `test_degradacion_a_3_de_4_forma_no_varios` — degradación a 3/4 (Forma n°
  sigue siendo el valor común, no "varios" — solo a nivel 2 es "varios").
- `test_degradacion_a_2_de_4_forma_varios` — degradación a 2/4 → "varios".
- `test_sin_ningun_criterio_comun_cajitas_separadas` — sin criterio común →
  cajitas separadas.
- `test_racha_con_sueltos` (+ 5 variantes) — formato de rango con racha y
  sueltos no correlativos.

Más cobertura adicional (no pedida explícitamente, pero necesaria para
confiar en el motor de agrupación): viaje/máquina distintos no agrupan,
cierre de grupo cuando extenderlo bajaría el nivel ya alcanzado, conservación
de `nr_piezas`/`kilos` totales, `fecha_inicio`/`fecha_fin`/`duracion_min` del
grupo, orden ascendente de `detalle_etiquetas`.

Además:
- `python -m py_compile backend/routers/programacion.py` — sin errores.
- `python -c "from routers.programacion import obtener_programacion, ..."` en
  el host TO (mismas deps que el contenedor) — import completo sin
  excepciones.
- `python -m unittest test_b42v2_etiquetas.TestB42v2Series -v` — las 5 pruebas
  de B42 v2 (agrupación del Motor, NO tocada por esta tarea) siguen en verde,
  confirmando que no hay regresión en `_tarea_a_evento`/`motor_v2`.
- `frontend`: `npx tsc -b` (build real de TypeScript, `tsc -b && vite build`
  es el script `build` del proyecto) — exit code 0, sin errores de tipos.
- No pude levantar el frontend en un browser real (fuera del alcance de una
  sesión sin acceso visual a la VM/TO) — Montu debe verificar visualmente el
  Gantt y la Bolsa antes de considerar esto "probado en UI".

## 7. Graphify

Sincronicé desde el HEAD real de la rama en TO (`332f98c`, confirmado con
`git branch --show-current` + `git rev-parse HEAD` antes y después de mis
cambios — no se movió, solo hice commits locales pendientes, ver §8) los
archivos que toqué (`backend/routers/programacion.py`,
`frontend/src/components/domain/GestorProgramacion.tsx`,
`backend/test_cajita_viaje.py`) más `backend/main.py` (sin cambios, sincronizado
por completitud) hacia `~/graphify-workspace/optifierro`, y corrí
`graphify update ~/graphify-workspace/optifierro --force`:

```
Rebuilt: 1077 nodes, 1824 edges, 73 communities
```

`built_at_commit` del grafo quedó en `5072159` — **ese es el HEAD propio del
repo `graphify-workspace` (su propia historia git, no la de TO)**, sin mover
porque no hice ningún commit ahí (instrucción del brief: solo sincronizar
archivos de trabajo, no commitear). El contenido de los 3 archivos sincronizados
sí corresponde 1:1 al working tree real de la rama `unificar-generacion-auto-manual`
en TO en el momento de correr `graphify update` (verificado por tamaño/diff
antes de correr el comando) — la vigencia del grafo se valida por contenido de
archivos, no por igualdad de SHA entre los dos repos (imposible mientras la
rama de TO no esté pusheada a `origin`, tal como advertía el brief).

## 8. Estado de commits — pendiente de confirmación

Los cambios están escritos en el working tree de TO
(`/c/Users/OptiFierro/Desktop/optifierro`, rama
`unificar-generacion-auto-manual`) pero **todavía NO commiteados**. El brief
de esta tarea dice explícitamente "decide con el criterio dado arriba, no
hagas preguntas" para el diseño/alcance, pero mis reglas cardinales (CLAUDE.md,
regla 2: "Muestra el diff antes de commitear") piden confirmación explícita
antes de cualquier `git commit`. Interpreté que ambas instrucciones son
compatibles: implementé todo sin pedir aclaraciones de diseño, pero dejo el
commit real pendiente de tu confirmación explícita (no es una pregunta sobre
qué hacer, es el gate de commit que ya tenías configurado como regla
permanente). Corré `git status`/`git diff` en TO para revisar antes de pedirme
que commitee.

## 9. Dudas abiertas para Montu / Miaude

1. **Gate de fecha en la Bolsa evaluado por IT, no por pieza** (ver §2.3) —
   decisión técnica mía por falta de una fecha por pieza más granular a ese
   nivel del código. Si en la práctica un IT puede tener piezas con fecha de
   despacho distinta y eso importa para el corte de vigencia, avisar.
2. **Badge "N ITs" en la Bolsa** (`DroppableBacklog`, texto fijo "ITs" al lado
   del contador): no lo toqué porque el brief no lo pidió explícitamente, pero
   después de esta tarea ese contador pasa a contar **cajitas/grupos**, no
   ITs reales (un IT con etiquetas heterogéneas puede producir varias
   cajitas). El número sigue siendo correcto como "cantidad de tarjetas en la
   bandeja", pero el label "ITs" queda impreciso. Lo dejo como sugerencia, no
   lo cambié.
3. **`id_forma: "varios"` cambia de tipo** (`number` → `number | "varios"`)
   en la interfaz `Tarea` del frontend y en el JSON del backend. Revisé los
   usos existentes de `id_forma` en `GestorProgramacion.tsx` y ninguno hace
   aritmética con él (solo se muestra), así que no debería romper nada, pero
   si algún otro componente del frontend consume `/api/programacion` y hace
   comparaciones numéricas con `id_forma`, con una cajita agrupada a nivel 2
   podría recibir el string `"varios"` en vez de un número.
4. **No verifiqué visualmente en un browser** (ver §6) — pido que antes de dar
   por cerrada la tarea alguien abra el Gantt/Bolsa reales (con
   `CAJITA_VIAJE_VIGENTE_DESDE` temporalmente adelantada a una fecha pasada
   en un entorno de pruebas, NO en producción) y confirme que las cajitas se
   ven como se espera.
