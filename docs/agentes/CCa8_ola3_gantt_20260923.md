# CCa-8 — Ola 3 / Carril Gantt: B42 -> B44(a) -> B43

**Fecha:** 23-09-2026 | **Worktree:** `/c/Users/OptiFierro/Desktop/optifierro_g` (TO), rama `ola3-gantt`, base `4325640`.
**Commits:** `0fdd28d` (B42) -> `2508cb2` (B43) -> `88964ac` (B44a). Working tree limpio, sin push, `master` no tocado, sin `docker build/up/restart`.

## B42 — Numero de etiqueta de fabricacion en la cajita

**RCA (con evidencia real, Cerrillos):** la tabla Cubigest `detallePaquetesPieza` tiene una columna de texto libre `Etiqueta` con formato `"Tag #: N of M"` (verificado con `SELECT TOP 3 ... ORDER BY id DESC`: `'Etiqueta': ' Tag #:  27  of  27'`). Esto **resuelve la contradiccion marcada en el pendiente**: no hay jerarquia Paquete/Etiqueta de 5 niveles — `dp.id` (usado hasta ahora como `etiqueta_id`) es la PK interna, y `N` (parseado de `dp.Etiqueta`) es el numero fisico de etiqueta que ve el operario. Confirmado contra el viaje real `ASR2-215/1` (sucursal 10): `dp.id=3595134 -> numero_etiqueta=1`, `3595135 -> 2`, ... secuencial y consistente con `dp.id ASC`.

**Cambios:**
- `backend/database_cubigest.py`: nueva funcion `parse_numero_etiqueta()` (regex `Tag #:\s*(\d+)\s*of\s*(\d+)`); `get_etiquetas_por_viaje` ahora selecciona `dp.Etiqueta` y devuelve `numero_etiqueta`.
- `backend/routers/programacion.py`: `_piezas_optisteel_por_viajes` (fuente real de `/generar`) selecciona `dp.Etiqueta`; mapa en memoria `_mapa_numero_etiqueta` (etiqueta_id -> numero fisico); `_tarea_a_evento` y `/tags-viaje` lo exponen. `/generar` anota `numero_etiqueta` tambien en la tarea cruda (el frontend pinta `result.tareas` directo, sin pasar por GET).
- `frontend/GestorProgramacion.tsx`: cajita, tooltip, modal ("N° Etiqueta") y lista de etiquetas del modal muestran `numero_etiqueta` con fallback a `codigo_viaje`/`etiqueta_id` si aun no esta resuelto.

**Verificacion:** `py_compile` OK; `tsc --noEmit` limpio; query real ejecutada dentro de `optifierro-backend` (modulo cargado desde `/tmp`, sin tocar el checkout de produccion) contra `ASR2-215/1` sucursal 10 — 40 filas, `numero_etiqueta` correcto y secuencial.

**SUPUESTO (documentar y confirmar con Jose Auger/imagenes, como Montu propuso):** cuando una cajita agrupa varias etiquetas (`nr_tags>1`, es el caso mas comun: 27 de 35 cajitas reales de Cerrillos hoy), se muestra el numero de la etiqueta **representante del grupo** (la de menor `dp.id`), no un rango. `nr_tags` sigue visible en la linea 2 para dejar claro que son varias.
**Limitacion conocida:** el mapa `_mapa_numero_etiqueta` es en memoria (igual que `global_eventos`); tras un reinicio del backend, las cajitas cargadas desde el cache SQLite muestran TAG hasta el siguiente "Generar".

## B43 — Ribete visual para cajitas adelantadas desde dias futuros

**Definicion usada:** `dias_atraso < 0` (ya calculado por el backend contra la fecha real de Cubigest/FechaDespacho-FechaEntrega vs hoy) — es el mismo dato que usa el Motor para `_etiqueta_prioridad`, ya llega a la cajita sin cambios de backend. Aplica a las 3 plantas (logica en el componente compartido, sin condicion de sucursal).

**Cambio:** `GestorProgramacion.tsx`, `DraggableTimelineEvent`: `outline: 2px dashed #0ea5e9` cuando `dias_atraso<0` y no completado (no compite con el borde de completado/no-A630 ni con el `borderTop` de estado de maquina). Leyenda agregada: "Adelantada (viene de dias futuros)".

**Verificacion:** `tsc --noEmit` limpio; distribucion real Cerrillos hoy: 29/35 cajitas con `dias_atraso<0` (rango -1 a -15).

**SUPUESTO / riesgo a validar con Montu:** con el umbral `<0` casi todo el tablero de Cerrillos queda marcado (la planta trabaja con bastante colchon como norma operativa, no como excepcion) — puede ser exactamente lo que se quiere visibilizar, o puede ser demasiado ruidoso. Monto mismo califico el ribete como "forma final por definir"; dejo el umbral simple (`<0`) sin inventar un corte arbitrario (ej. `<=-2`) porque no hay definicion de negocio para eso. Facil de ajustar (una comparacion) una vez Montu vea el resultado real.

## B44(a) — Ajustar duracion del trabajo (en minutos)

**Cambios:**
- `backend/routers/programacion.py`: tabla nueva `ajustes_duracion` (PK `sucursal_id,fecha,turno,id_tarea`; `minutos`, `usuario`, `creado_en`) via `CREATE TABLE IF NOT EXISTS` en `_init_programacion_guardada()`. Endpoint `POST /api/programacion/ajuste-duracion` (upsert `ON CONFLICT`, valida `minutos>0`) que persiste y ademas actualiza `global_eventos` en memoria para efecto inmediato. Helper `_aplicar_ajustes_duracion()` reaplicado en el GET (`obtener_programacion`) y en `/generar` (antes de persistir a `global_eventos`) — el ajuste sobrevive a un reload y a un "Generar" siempre que la tarea conserve el mismo `id_tarea` (`etiqueta_id + paso_secuencia`).
- `frontend/GestorProgramacion.tsx`: campo "Ajustar duración del trabajo (en minutos)" arriba del todo en el modal de detalle, con boton "Aplicar"; actualiza `selectedTarea` y `data.eventos` de inmediato (sin esperar refetch) y badge "Ajustada manualmente".

**Fuera de alcance (respetado):** sin auto-aprendizaje, sin tocar `estimar_duracion_min`/asignacion, sin campo en "Produccion por Maquina" (B44b).

**Comportamiento documentado (pedido explicito del ticket):**
- Solo la cajita ajustada cambia su `fecha_fin`; `fecha_inicio` no se toca y las cajitas siguientes de la misma maquina **no se recorren** (el hueco liberado, si `minutos` reduce la duracion, queda vacio hasta el proximo "Generar"; si `minutos` la alarga, puede solaparse visualmente con la siguiente cajita — no se resuelve colision).
- "Generar" no borra el ajuste de una tarea que se mantiene: la clave es `id_tarea`, se reaplica automaticamente tras cada regeneracion mientras la etiqueta siga en el mismo paso de ruta.

**Verificacion:** `py_compile` OK; `tsc --noEmit` limpio; tabla + `INSERT ... ON CONFLICT ... DO UPDATE` + logica de recalculo de `fecha_fin` probadas con `sqlite3` real (3.46.1, soporta upsert) sobre una **copia** de `optifierro_v2.db` dentro del contenedor (`/tmp`, nunca el archivo real) — insert, update por conflicto y recalculo de `fecha_fin`/`duracion_min` correctos.

## Verificacion general
- `py_compile` limpio en los 3 archivos backend tocados.
- `tsc --noEmit -p tsconfig.json` limpio tras cada commit (node_modules del checkout principal montado por Junction NTFS en `optifierro_g/frontend/node_modules` — no se toco `optifierro`/`master`).
- No se modifico `motor_v2.py`, `tiempos_maquina.py`, `TiemposPorMaquina.tsx` ni `main.py`.
- Drag & drop (B33/B34) no tocado — sin cambios en `useDraggable`/`useDroppable`/`handleDragEnd`. Pendiente confirmacion manual con mouse por Montu.
- Cubigest: solo `SELECT` (ademas del `SELECT TOP 3`/`TOP 2000` ya existentes en el codigo). Ninguna escritura a Cubigest ni a `optifierro_v2.db` real (solo a la copia de prueba en `/tmp` del contenedor, borrada al terminar).

## Riesgos / pendientes para la Coordinadora
1. B42: confirmar con Jose Auger (con imagenes, como Montu propuso) que el numero mostrado en cajitas agrupadas (representante del grupo) es aceptable, o si se requiere mostrar un rango.
2. B43: validar si el umbral `dias_atraso<0` es el deseado o genera demasiado ruido visual (29/35 cajitas hoy en Cerrillos).
3. B44(a): falta B44(b) (campo en "Produccion por Maquina") — se especifica junto a B26 en el pendiente, no incluido en este carril.
4. Deploy: falta turno de la Coordinadora para `docker compose build --no-cache && up -d` en el checkout principal (no en el worktree).

---
Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
