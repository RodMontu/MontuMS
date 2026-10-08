# CCa — Gantt: etapa gris e inamovible (etapa_completada)

**Fecha:** 2026-09-26
**Rama:** `gantt-etapa-gris` (NO mergeada, NO pusheada — commits pendientes de que Miaude/Montu vean el diff)
**Objetivo:** cuando Cubigest confirme que una etapa (etiqueta + máquina especifica) ya se ejecutó, la
cajita del Gantt queda GRIS e INAMOVIBLE para siempre.

## Qué se hizo

### 1. Backend — nuevo estado `etapa_completada`, distinto de `completado`

- **`backend/routers/programacion.py`**
  - Tabla nueva `etapa_congelada` (creada en `_init_programacion_guardada()`), clave
    `(sucursal_id, etiqueta_id, nombre_maquina)` — **sin fecha/turno a propósito** (ver hallazgo crítico
    abajo).
  - `_obtener_etapas_congeladas(sucursal_id)`: lee el set de pares `(etiqueta_id, nombre_maquina)` ya
    confirmados.
  - `_marcar_etapas_congeladas(items, sucursal_id)`: aplica `estado='etapa_completada'` a las tareas que
    matchean, sin pisar `'completado'` (IT/viaje cerrado — señal más fuerte, mecanismo existente que NO se
    tocó).
  - Llamada a `_marcar_etapas_congeladas` agregada en `generar_programacion` (POST `/generar`), justo
    después de `_aplicar_ajustes_duracion` (mismo punto, mismo patrón que B44a).
  - Guardas nuevas en `POST /reprogramar` (`reprogramar_pid`): rechaza (409) mover un pid cuyo evento actual
    ya está `etapa_completada`, y rechaza soltar cualquier otro pid sobre un rango horario que se superponga
    con una cajita `etapa_completada` en la máquina destino. Es defensa en profundidad — el frontend ya
    bloquea ambos casos, pero un caller directo del API o una carrera podría saltárselo.

- **`backend/main.py`**
  - Job nuevo `_job_verificar_etapas_completadas`, cron `*/30` (ajustado 26-09 por Montu, ver addendum al final) (más fino y más frecuente que
    `_job_verificar_its_cerradas`, que corre cada 30 min a nivel IT/viaje completo — ese mecanismo NO se
    tocó). Junta candidatos `(etiqueta_id, nombre_maquina)` de `global_eventos` no marcados aún, traduce
    `nombre_maquina` → `MAQ_NRO` de Cubigest vía `conocimiento.mapa_maq_nro_nombre` (mapa ya existente,
    poblado en el lifespan desde `_CUB_MAQ_MAP`), consulta `PIEZA_PRODUCCION JOIN MAQUINA` (mismo patrón de
    join que `tiempos_maquina.py`/`build_kgshora_referencia.py`) filtrando por `IdSucursal` de Cubigest
    (`cubigest_db.get_cubigest_sucursal_ids`), y para los que confirma: inserta en `etapa_congelada`
    (`INSERT OR IGNORE`, persistente) y muta el evento en memoria a `estado='etapa_completada'` (para que se
    pinte gris sin esperar el próximo "Generar").
  - `_ejecutar_generacion` (scheduler automático 08:10/20:10) también llama `_marcar_etapas_congeladas`
    antes de persistir/publicar — ver hallazgo crítico.

### 2. Frontend — `frontend/src/components/domain/GestorProgramacion.tsx`

- `DraggableTimelineEvent`: nueva bandera `isEtapaCongelada = ev.estado === 'etapa_completada'`.
  - `useDraggable({ disabled: isEtapaCongelada })` — no se puede agarrar, punto.
  - Color propio (gris `#57534e`/borde `#78716c`, distinto del verde de `completado`), ícono `Lock` en vez
    de `CheckCircle2`, cursor `not-allowed`, tooltip explicativo. Nunca vuelve a color de obra: se comporta
    como `completado` para todos los badges secundarios (atraso/urgente/adelantada/no-A630/reparto) — se
    silencian igual que para `completado`.
  - Doble-click (abrir modal de reparto) bloqueado para etapas congeladas; click simple (ver detalle) se deja
    abierto a propósito — es "registro histórico visible", tiene sentido poder verlo.
- `handleDragEnd`: dos guardas nuevas —
  1. si la tarea arrastrada ya es `etapa_completada`, no hace nada (defensa extra; el `disabled` de arriba ya
     debería impedir que el drag arranque).
  2. antes de armar el payload, calcula solapamiento de horario contra las cajitas `etapa_completada` de la
     máquina destino (`eventosMaquina`) — si choca, `alert()` y `return` sin llamar al backend.

### 3. Test — `backend/test_gantt_etapa_gris.py`

7 casos con `unittest`, mismo patrón que `test_b44b_capacidad_real.py` (copia de la SQLite real en `/tmp`,
sin tocar Cubigest ni la DB del contenedor). Cubre: marcado correcto, no-match, no-match por máquina distinta
en la misma etiqueta, no pisar `completado`, no confundir sucursales, y el caso crítico —
**AC4: sobrevive a una regeneración completa** (dos "corridas" con listas de tareas nuevas e independientes,
simulando lo que hace `motor_v2` en cada `programar_turno`).

## Cómo se verificó

- `python -m py_compile` sobre los 3 archivos backend modificados/nuevos: OK.
- `docker cp` de los archivos backend al contenedor `optifierro-backend` (corriendo, SIN rebuild — no se
  tocó el protocolo de deploy) y corrida de:
  - `test_gantt_etapa_gris.py` (7 tests nuevos): **OK**.
  - `test_b42v2_etiquetas.py`, `test_b44b_capacidad_real.py`, `test_b16_capacidad.py` (23 tests existentes):
    **OK, sin regresiones**.
- Frontend: `npx tsc -b` y `npm run build` completos sobre el checkout real (Windows, con `node_modules` ya
  instalado) — compilan sin errores, bundle generado normalmente. No se pudo probar en navegador real (no
  hay UI de browser en este entorno de ejecución) — recomendado que alguien lo pruebe a mano: arrastrar una
  cajita gris (debe no moverse), soltar otra cajita sobre una gris (debe rechazar con alert), y confirmar que
  el estilo se ve distinto del verde `completado`.
- NO se hizo `docker compose build --no-cache && up -d` — la rama no está para deploy todavía, solo para
  revisión.

## Hallazgo crítico (el que pedían verificar antes de cerrar): persistencia entre regeneraciones

**Confirmado con evidencia, es un problema real — y ya resuelto por el diseño elegido, no por un parche
posterior:**

Hay **dos** lugares que reemplazan `global_eventos`/`programacion_guardada` por completo, no uno:

1. `generar_programacion` (POST `/generar`, click manual "Generar Programación") — filtra y borra todos los
   eventos de `(sucursal_id, turno, fecha)` (líneas ~1417-1424 antes de mis cambios) y hace `INSERT ... ON
   CONFLICT DO UPDATE` sobre `programacion_guardada` (upsert, no append) — un segundo "Generar" el mismo día
   pisa completamente el primero.
2. `_ejecutar_generacion` (scheduler automático, `_job_dia`/`_job_noche` 08:10/20:10) — es **todavía más
   agresivo**: borra **todos** los eventos de esa `sucursal_id` sin filtrar por turno/fecha
   (`global_eventos[:] = [e for e in global_eventos if str(e.get("sucursal_id")) != sucursal_str_g]`, ver
   `main.py` línea ~201 antes de mis cambios).

O sea: sí, una regeneración a mediodía (manual o automática) borra por completo lo que había antes en
memoria — confirmado leyendo el código, no es una suposición.

**Por qué la cajita gris sobrevive igual:** en vez de intentar preservar/fusionar el evento viejo (que es lo
que sugería la instrucción original como plan A), la clave de diseño fue **no depender del evento en
absoluto**. `etapa_congelada` es una tabla aparte, con clave `(sucursal_id, etiqueta_id, nombre_maquina)` —
**sin fecha ni turno**. El hecho físico ("esta etapa, en esta máquina, para esta etiqueta, ya se ejecutó") no
depende de en qué turno/fecha cayó la cajita hoy en el Gantt. Entonces, en cada corrida —sea `/generar` manual
o el scheduler automático—, después de que `motor_v2` devuelve tareas nuevas "desde cero", se llama
`_marcar_etapas_congeladas(tareas, sucursal_id)` que **re-consulta la tabla y re-aplica el gris**, sin
importar si el evento anterior sobrevivió o no. El test `test_ac4_sobrevive_a_una_regeneracion_completa`
prueba exactamente esto: dos listas de tareas completamente independientes (simulando dos corridas
separadas), ambas terminan grises porque ambas se chequean contra la misma tabla persistente.

Esto también resuelve gratis el caso de reprogramación: si Cubigest ya confirmó etiqueta X en máquina Y, y
por algún motivo esa etiqueta se reprograma a otro turno/día futuro pero **a la misma máquina**, la cajita
seguiría marcándose gris (es la misma etapa física, ya ejecutada) — comportamiento que parece correcto según
el objetivo ("registro histórico de lo que ya se ejecutó"), pero **no estaba explícitamente pedido para ese
caso límite** y vale la pena que Montu lo confirme si llega a pasar en la práctica.

**Límite conocido, heredado y no nuevo (documentado, no corregido — mismo patrón que `ajustes_duracion`
B44a):** el `estado='etapa_completada'` que pone `_marcar_etapas_congeladas` sobre las tareas de
`resultado["tareas"]` se aplica **después** de que `generar_programacion` ya escribió `tareas_json` en
`programacion_guardada` (la persistencia a SQLite ocurre antes en el código, línea ~1362-1377, y
`_aplicar_ajustes_duracion`/`_marcar_etapas_congeladas` corren después, línea ~1430). Esto es *exactamente* el
mismo orden pre-existente que ya tiene el ajuste manual de duración (B44a) — ninguno de los dos queda en el
snapshot `tareas_json`, solo en `global_eventos` (memoria viva). Consecuencia: si el backend se reinicia
(pierde `global_eventos`, es volátil por diseño — ver comentario ya existente sobre `_mapa_numero_etiqueta`)
**y** alguien pide `GET /api/programacion` **antes** del próximo "Generar", esa ventana angosta mostraría la
cajita sin el gris (cae al fallback de SQLite crudo). No lo corregí porque es un gap preexistente y compartido
con B44a, no algo que este feature introduzca — pero si Montu quiere cerrarlo también, se puede escribir
`estado` directamente en `tareas_json` antes del insert, o simplemente reordenar las líneas (mover el insert
de `programacion_guardada` después de aplicar ajustes/congeladas). Lo dejo marcado, no lo toqué para no
mezclar un fix no pedido con este feature.

## Alcance de archivos tocados

- `backend/main.py` — job nuevo + llamada en `_ejecutar_generacion`.
- `backend/routers/programacion.py` — tabla, helpers, llamada en `generar_programacion`, guardas en
  `reprogramar_pid`.
- `backend/motor_v2.py` — **NO tocado**. Toda la info necesaria (`etiqueta_id`, `nombre_maquina` vía
  `recurso_id` del evento) ya estaba expuesta.
- `frontend/src/components/domain/GestorProgramacion.tsx` — estilo gris, `disabled` en `useDraggable`,
  guardas en `handleDragEnd`.
- `backend/test_gantt_etapa_gris.py` — nuevo, 7 tests.
- `test_b16_capacidad.py` / `test_b42v2_etiquetas.py` — no necesitaron casos nuevos (no tocan el código que
  cambié; corridos igual como regresión, OK).

## Dudas / abiertos para Montu o Miaude

1. **Caso límite de reprogramación a otro turno/día, misma máquina** (arriba) — confirmar que "siempre gris
   una vez confirmado, sin importar a qué turno se reprograme" es el comportamiento deseado.
2. **Gap de ventana angosta post-reinicio** (arriba) — decidir si se cierra ahora (cambio chico, no lo hice
   para no mezclar con este feature) o se deja documentado igual que B44a.
3. **Reparto en paralelo**: si una etiqueta tiene `reparto[]` (varias máquinas en paralelo para el mismo
   `id_tarea`), el congelado es por `(etiqueta_id, nombre_maquina)` de la tarea principal — cada fila de
   `reparto` no tiene su propio evento/`id_tarea` independiente en `global_eventos`, así que si Cubigest
   confirma una sola de las máquinas del reparto, hoy no hay granularidad para pintar gris solo esa porción.
   No es un caso que las instrucciones pidieran resolver, lo documento como límite conocido.
4. `git status` en la rama mostraba `AGENTS.md`/`HARNESS.md` modificados y varios archivos sin clasificar de
   antes de que yo empezara (no los tokué, no son míos) — quedan igual que estaban, no se incluyeron en mis
   cambios.

## Graphify

Corrí `git pull` en `~/graphify-workspace/optifierro` (Mac Studio) — sigue en `52568d1`, sin cambios,
porque **todavía no commiteé nada** en `gantt-etapa-gris` (el diff está solo en el checkout Windows,
sin commit, a la espera de revisión). Regenerar el snapshot ahora habría sido un no-op idéntico al que
ya existe. Queda pendiente como paso obligatorio en cuanto Miaude/Montu aprueben el diff y yo pueda
commitear en la rama: `cd ~/graphify-workspace/optifierro && git pull && graphify update
~/graphify-workspace/optifierro` — no cierro el ciclo completo de la tarea hasta hacerlo después de ese
commit.

## Addendum — revisión de Montu (26-09)

- **Mecanismo de consulta a Cubigest, aclarado:** el job `_job_verificar_etapas_completadas` consulta
  **directo contra SQL Server** (`cubigest_db.execute_query`, mismo patrón que `_job_verificar_its_cerradas`
  y las queries de `tiempos_maquina.py`) — **no** usa ningún scraper/simulación de navegador. Verificado
  leyendo el diff real (sin ninguna referencia a scraper/Selenium/Playwright en los 2 archivos backend
  tocados).
- **Decisión de Montu:** por precaución ante el riesgo de saturar Cubigest, baja la frecuencia de cada 15 a
  **cada 30 minutos** (`CronTrigger(minute="*/30")`). Aplicado directamente por Miaude (cambio de un
  parámetro, sin tocar el diseño), verificado con `py_compile`.
- **Punto 1 (gris permanente):** confirmado sin cambios.
- **Punto 2 (gap post-reinicio):** Montu no quiere complicar el diseño por esto — el sistema debe operar
  24/7 sin reinicios como premisa de base. Se deja documentado, sin corregir, tal como proponía CCa.
- **Punto 3 (reparto en paralelo, todo o nada):** confirmado explícitamente por Montu — Cubigest no
  discrimina entre las 2 máquinas de un reparto, así que el comportamiento todo-o-nada (las dos etapas se
  confirman juntas o ninguna) es el correcto, no un límite a resolver.
- **Luz verde de Montu:** commit + regeneración de Graphify + build/deploy, con el ajuste de 30 min ya
  incluido.
