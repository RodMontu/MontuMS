# CCa-13 — B42 v2 FASE 1: implementación "una cajita = una etiqueta" (worktree)

**Fecha:** 24-09-2026 · **Rama:** `b42v2-etiqueta` en `/c/Users/OptiFierro/Desktop/optifierro_b42` (TO), base `master 1cd8f88`.
**Estado:** T0-T9 completadas. Sin push, sin tocar `master`, sin `docker build/up/restart`, sin escrituras en Cubigest ni en la DB real.
**Especificación:** `/Users/montu/MontuMS/docs/agentes/B42_v2_spec.md` · **Mapa previo:** `CCa12_b42v2_mapa_20260924.md`.

---

## 1. Commits (hash + archivos)

| Commit | Archivos | Qué hace |
|---|---|---|
| `834425b` | `backend/database_cubigest.py`, `backend/routers/programacion.py` | D4: agrega `dp.Etiqueta AS etiqueta_raw` al SELECT de `_obtener_pids_pendientes` (antes solo lo traía `_piezas_optisteel_por_viajes`). Nueva función `parse_numero_y_total_etiqueta` (N y M). Anota `numero_etiqueta`/`total_etiquetas` en el dict de cada etiqueta en AMBOS caminos de entrada al Motor. |
| `48d946c` | `backend/motor_v2.py` | D1+D2+D3: clave de serie `(codigo_viaje, diametro, id_forma, largo_mm=round(largo_a*1000), calidad_acero_real, etapa_avance)`. Ruta/máquina/operador se resuelven una vez por serie con el representante. Duración de la serie = `estimar_duracion_min` con los kg de la serie (igual que hoy), repartida proporcional a kg entre sus etiquetas. Se emite 1 tarea del Motor por etiqueta (antes: 1 tarea fusionada por grupo). Reestructura el loop interno (`pendientes`/`siguientes_pendientes`) para procesar etiqueta por etiqueta dentro de cada paso de ruta, con cursor de máquina compartido (logra "consecutivas" de forma natural, sin reordenar). |
| `04d61a1` | `backend/routers/programacion.py` | D3/D4/D6: `_tarea_a_evento` y la anotación cruda en `/generar` priorizan `numero_etiqueta`/`total_etiquetas` de la tarea (ya poblados por el Motor) sobre el mapa volátil, que queda solo como respaldo. |
| `c6eb349` | `frontend/.../GestorProgramacion.tsx` | D7: carátula con `Ø{diametro} · N de M` (línea 1) + `peso · viaje` (línea 2), prioridad por truncate/ellipsis CSS. Elimina línea "TAGs". Tooltip: agrega Largo/Forma, renombra Cantidad/Peso, elimina "TAGs: N etiquetas". |
| `5147564` | `frontend/.../GestorProgramacion.tsx` | D7 §5: modal — header con chip `ETIQUETA: N de M`, cuerpo reordenado (Diámetro, Largo, IdForma, Cantidad, Paquete=N, Peso), sin Operador/Secuencia/marca. Elimina el bloque "Etiquetas incluidas" completo y su fetch (`selectedTareaTags`, `useEffect` a `/detalle-maquina`+`/tags-viaje`, `selectedTagsParaModal` y derivados), y el tipo `TagViaje` (sin uso). |
| `fe5f7b1` | `backend/test_b42v2_etiquetas.py` (nuevo) | Arnés sintético AC1/AC4/AC5/AC6 contra `ConocimientoMotor` real (matriz_rutas.json, deltat CSV, Excel maestro, mapa MAQ_NRO desde `optifierro_v2.db`). 5/5 tests OK. |

Patches: `/Users/montu/MontuMS/docs/agentes/diffs/B42v2/0001..0006*.patch`.

---

## 2. Decisión D5 (reparto en paralelo) — CON evidencia, sin rediseño

**Pregunta:** ¿el bloque de auto-reparto 80%/100% (umbral de jornada, `motor_v2.py` ~1212-1412 en master) se puede preservar tal cual al pasar de "1 tarea=grupo" a "1 tarea=etiqueta"?

**Mapeo hecho antes de tocar código:** el bloque calcula `pct_jornada = duracion / minutos_restantes` sobre la duración de LA TAREA que se está emitiendo. Con el cambio de granularidad, "la tarea" pasa a ser 1 etiqueta en vez del grupo completo — el bloque no necesita lógica nueva, solo evaluarse con la duración de 1 etiqueta.

**Decisión tomada:** se preservó el bloque de reparto **sin cambios de lógica**, movido dentro del sub-loop por etiqueta, sustituyendo `kgs`→`kg_e`, `duracion`→`dur_e`, `etiqueta_id`→`eid_e`. No fue necesario un rediseño — es una adaptación mecánica del mismo código a una unidad más fina, confirmando la hipótesis de CCa-12 §2d ("en teoría con el mismo resultado, pero consumiendo más ciclos").

**Evidencia real (T7, universo de hoy):** el efecto NO es neutro en la práctica — al evaluarse por etiqueta individual (duraciones mucho más chicas que antes), el umbral 80%/100% se activa con mucha menos frecuencia por etiqueta suelta, PERO el chequeo de solapamiento de operador SÍ se activa más seguido (una etiqueta de pocos minutos deja "huecos" que antes quedaban ocultos dentro de la duración agregada del grupo). Resultado medido: kg totales efectivamente programados bajan (Cerrillos 117.790→81.753 kg, Calama 126.521→96.973 kg, Coronel 8.311→7.047 kg, en el escenario sintético "todos los operadores disponibles"). Esto es un **cambio de comportamiento real, no un bug** — el scheduler nuevo es más conservador porque valida disponibilidad de operador a grano fino. **Riesgo abierto para Montu**: decidir si este comportamiento (menos kg agendado por turno, más precisión por etiqueta) es aceptable o si se requiere un ajuste de tolerancia antes de producción.

---

## 3. Resultados reales T6 (arnés sintético, `backend/test_b42v2_etiquetas.py`)

Ejecutado dentro de `optifierro-backend` vía `MOTOR_BASE_DIR=/app` (config estática real, sin Cubigest). 5/5 OK:

- **AC1+AC5** (serie de 5 etiquetas homogéneas): conservación exacta etiquetas/kg entre entrada y tareas+bolsa.
- **AC4** (dos series reales, IdForma 2 y 4, Ø10mm Cerrillos, ambas → PRIMA 3D): verificado con `fecha_inicio`/`fecha_fin` reales — serie A completa 08:15-08:20, serie B arranca 08:20, **sin intercalar**.
- **AC5 (float)**: largo `8.699999809265137` vs `8.7` → misma serie, misma máquina (Robomaster 60), consecutivas.
- **AC6**: réplica exacta del sesgo real CCa-12 §2c/§6b — mismo viaje/diámetro, distinto IdForma → ruta histórica real distinta (IdForma=2 Ø10mm→PRIMA 3D, IdForma=3 Ø10mm→EURA 16 en Cerrillos, verificado contra `matriz_rutas.json`); cada serie resolvió su propia máquina correctamente.
- **AC5 (duración)**: suma de `duracion_min` de la serie == `estimar_duracion_min` del grupo completo (pasó, con 4/4 etiquetas asignadas).

---

## 4. Resultados reales T7 (arnés con universo real, solo lectura)

Metodología: mismo universo de etiquetas (`_obtener_pids_pendientes` real, Cubigest solo SELECT) y mismos operadores (todos los reales de la sucursal, para aislar el efecto del cambio de Motor) alimentados a `programar_turno` VIEJO (master `1cd8f88`) y NUEVO (`b42v2-etiqueta`), sin llamar `/generar` ni escribir nada.

| Sucursal | Universo etiquetas | Cajitas viejo | Cajitas nuevo | kg viejo | kg nuevo | Series (`total_grupos`) | Tiempo viejo | Tiempo nuevo | JSON nuevo |
|---|---|---|---|---|---|---|---|---|---|
| Cerrillos | 2000 (tope query) | 51 | 469 (~9.2x) | 117.790 | 81.753 | — | 0.17s | 1.21s | — |
| Calama | 2000 (tope query) | 61 | 413 (~6.8x) | 126.521 | 96.973 | 1025 | 0.22s | 1.54s | 321.217 bytes |
| Coronel | 261 | 10 | 70 (~7.0x) | 8.311 | 7.047 | 103 | 0.03s | 0.09s | 52.255 bytes |

- **Conservación (AC5) confirmada en las 3 sucursales**: `entrada == tareas_nuevo ∪ bolsa_nuevo` (True en los 3 casos). En el código VIEJO esta igualdad da **False** — no es un bug de mi implementación: el `bolsa_sin_asignar` de v1 registra 1 entrada por GRUPO fallido (no por etiqueta), así que subestima drásticamente cuántas etiquetas quedan realmente sin asignar. Esto es una mejora real de trazabilidad que trae v2, no solo un cambio de conteo.
- **Duración de cajitas nuevas** (Calama, 413 tareas): min 0.2 min, mediana 5.0 min, max 111.0 min, **180/413 (44%) por debajo de 5 min** — confirma con datos reales el riesgo de cajitas muy angostas descrito en CCa-12 §5, relevante para la decisión de UI tomada en T4/T5 (truncate por prioridad, sin min-width).
- **Máquinas que cambiaron de asignación** viejo→nuevo: 137/413 en Calama, 7/50 en Coronel — esperado, consistente con el fix de sesgo AC6 (la ruta ahora se resuelve por serie homogénea, no por el primer elemento de un grupo heterogéneo).
- **Rendimiento (AC8)**: 6-8x más lento que el viejo (1.2-1.5s en universos de 2000 etiquetas/~400-470 tareas), pero sigue en el orden de 1-2 segundos — no hay degradación catastrófica, pero tampoco es "imperceptible". **Sin medir aún el render en navegador** (fuera de alcance de este arnés backend).

---

## 5. Regresión T8 (lectura de código + verificación puntual)

- **B45 (FP-LC fuera):** sin cambios — el filtro corre en `_obtener_pids_pendientes`/`_piezas_optisteel_por_viajes` ANTES de que las etiquetas lleguen al Motor; no tocado.
- **B35 (ventana ±15):** `_ventana_turno`/`_resolver_ventana_override` no tocados.
- **B16 (`metadata.capacidad`):** `duracion_asignada_min`/`kgs_terminados` se calculan iterando `tareas` genéricamente (sin asumir granularidad) — confirmado por lectura de código que la suma es matemáticamente invariante (la duración de la serie se reparte proporcional a kg entre sus etiquetas, así que la suma por serie coincide con la duración de grupo de antes). No se corrió T7 con B16 activo end-to-end (requiere presencia real vía Geovictoria, fuera del arnés sintético) — **NO VERIFICADO con ejecución real**, solo por lectura+invariante matemática.
- **B2 (`/aplicar-reparto`):** sin cambios de código (no tocado en ningún commit); sigue operando por `id_tarea`, que ahora identifica 1 etiqueta en vez de un grupo — coherente con el pedido de negocio original.
- **B44a (`ajustes_duracion`):** riesgo YA documentado en CCa-12 §4 y confirmado sin cambios de código: los `id_tarea` viejos (etiqueta representante del grupo) quedan huérfanos tras el deploy porque el representante de cada serie nueva casi siempre difiere del representante del grupo viejo. **No se implementó migración/backfill** (no estaba en el alcance de las tareas T1-T6; queda como pendiente explícito, ver Riesgos).
- **`backfill_programacion_detalle.py`:** usa `t.get("lista_etiqueta_ids") or [t.get("etiqueta_id")]` — mismo patrón defensivo que `/generar`, funciona sin cambios con listas de 1 elemento.

---

## 6. Riesgos abiertos (para Montu, antes de deploy)

1. **D5 con evidencia real**: el auto-reparto operando a grano de etiqueta agenda MENOS kg totales por turno que el grupo viejo (sección 2) — validar si es aceptable.
2. **Cajitas < 5 min (44% en Calama)**: sin piso de duración por etiqueta (decisión Montu, sección 12 de la spec) — confirmar que el diseño de carátula (T4, truncate por prioridad) es suficiente en el navegador real; **el render visual no fue probado** (solo backend).
3. **`ajustes_duracion`/`programacion_manual` huérfanos tras el deploy** — decisión de negocio pendiente (avisar a jefes de planta vs. limpieza silenciosa), ya señalada por CCa-12, no resuelta en esta implementación.
4. **Rendimiento 6-8x más lento** en la generación (aún en el orden de 1-2s) — validar con Montu si es aceptable o si amerita optimización antes de producción.
5. **Calidad del acero (`mp.CalidadAcero` vs `IT.TipoAcero`)** — fuera de alcance de Fase 1 (documentado, no tocado), sigue mostrando el default `A630` cuando falta colada asignada.

## 7. No verificado (requiere a Montu)

- Drag & drop real con el mouse (B33/B34) sobre las cajitas nuevas.
- Render visual real en navegador de la carátula angosta y el modal (solo se corrió `tsc --noEmit` + `npm run build`, sin abrir la UI).
- B16 end-to-end con presencia real de Geovictoria.
- Comportamiento real de `/aplicar-reparto` (B2) sobre una tarea de 1 etiqueta con doble clic real.

---

## 8. Accesos y confirmación de cero escrituras

**Ventana:** 24-09-2026, ejecución en una sola sesión continua (T0 a T9).

**Comandos ejecutados en TO** (`ssh TO "..."`):
- `git worktree add -b b42v2-etiqueta ../optifierro_b42 1cd8f88` + junction NTFS de `frontend/node_modules` (`cmd /c mklink /J ...`).
- Múltiples `python -m py_compile` (backend) y `npx tsc --noEmit` / `npm run build` (frontend) sobre el worktree — todo local, sin red.
- `docker cp` (7 veces) — copias de solo lectura de `motor_v2.py`/`programacion.py`/`database_cubigest.py`/scripts de test hacia `/tmp` del contenedor `optifierro-backend`, para poder ejecutar la lógica nueva SIN reemplazar el código que sirve producción (`/app` no se tocó en ningún momento).
- `docker exec ... python3 -m unittest test_b42v2_etiquetas` (T6) y `docker exec ... python3 arnes_b42v2_real.py` (T7) — ambos con `-e MOTOR_BASE_DIR=/app` (solo para leer config estática: `matriz_rutas.json`, `deltat_por_forma_maquina.csv`, `Maestro_operadores_maquinas.xlsx`, `optifierro_v2.db` — este último es master local, no Cubigest) y `-e OPENSSL_CONF=/app/openssl_legacy.cnf` (requerido por el driver ODBC para el SELECT a Cubigest).
- `docker exec ... rm -f ...` — limpieza de todos los archivos temporales copiados al contenedor, ejecutada al finalizar.
- `git format-patch 1cd8f88..HEAD` + `scp`/`ssh cat` de los 6 patches hacia `/Users/montu/MontuMS/docs/agentes/diffs/B42v2/` (Mac).

**Accesos a Cubigest (SQL Server 192.168.1.195), SIEMPRE vía `cubigest_db.execute_query` dentro del contenedor `optifierro-backend`, nunca directo desde el Mac:**
- `_obtener_pids_pendientes(sucursal, fecha)` ×3 (Cerrillos, Calama, Coronel) — mismo SELECT que usa el scheduler automático en producción hoy, sin `TOP` explícito pero acotado por rango de fechas/sucursal (comportamiento existente, no modificado en su lógica de filtrado, solo se agregó 1 columna `dp.Etiqueta`).

**Confirmación explícita: CERO ESCRITURAS.**
- Ninguna sentencia SQL contra Cubigest distinta de `SELECT` (la función usada es exactamente la que ya usa producción para leer, sin cambios en su WHERE/lógica).
- Ningún `POST /api/programacion/generar` ni ningún otro POST/PUT/DELETE contra la API — todas las llamadas fueron funciones Python invocadas directamente dentro del contenedor, no HTTP.
- Ningún `docker compose build/up/restart` — solo `docker cp` (copia de archivos hacia `/tmp` del contenedor, nunca hacia `/app`) y `docker exec` de scripts Python de solo lectura.
- `optifierro_v2.db` real: solo se leyó (`SELECT sucursal_id, maquina_id, maquina FROM maquinas_info`) para reconstruir el mapa MAQ_NRO→nombre — nunca se escribió.
- Ningún `git commit/push` contra `master` ni contra el checkout principal — los 6 commits están únicamente en la rama `b42v2-etiqueta` del worktree `optifierro_b42`.
- El checkout principal de TO (`/c/Users/OptiFierro/Desktop/optifierro`) y el espejo local (`~/graphify-workspace/optifierro`) no fueron modificados — la única razón por la que aparecen archivos editados bajo `/Users/montu/graphify-workspace/optifierro/backend/` en la sesión es un intento inicial fallido de edición local (revertido de inmediato al confirmar que las reglas exigen trabajar solo en el worktree de TO vía SSH); ese directorio local **no tiene cambios reales aplicados** por esta sesión.

## 9. Turno de deploy sugerido

Dado el riesgo #1 (D5, menos kg agendado) y #3 (`ajustes_duracion` huérfanos), se sugiere **NO deployar antes de la revisión con Gerencias/jefes de planta del viernes 25-09** (ya movida, según la spec). Deploy recomendado en una ventana de bajo tráfico (ej. antes del scheduler automático de las 08:10 o 20:10), con aviso previo a los 3 jefes de planta sobre la pérdida de ajustes manuales guardados.
