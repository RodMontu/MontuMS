# Mapeo de Arquitectura de Código de OptiFierro (Graphify)

## 1. Qué es esto

Registro del mapeo de dependencias de código construido con Graphify sobre los
repos `optifierro` (TO) y `scrap-geovictoria`, y de la regla institucional que
nace de este trabajo.

## 2. El mapeo puntual (evento, no la regla)

**Cuándo:** construido y verificado la noche del 08-09-2026, entre las 23:39 y
las 23:45 hrs (hora Chile).

**Sobre qué código exacto:** commit `7581b9a` del repo `optifierro` (TO) —
verificado en vivo que ese era el HEAD real del servidor al momento de
construirlo, no una copia vieja. Incluye también el repo `scrap-geovictoria`.

**Qué se obtuvo:** 890 nodos combinados (810 de `optifierro` + 80 de
`scrap-geovictoria`), 99% de las conexiones extraídas de forma determinista
(tree-sitter, sin adivinar con IA), 0 tokens de API usados (100% local, sin
enviar código a ningún proveedor externo). El componente más conectado del
sistema es `ConocimientoMotor` (`motor_v2.py`), el motor de asignación de
trabajos.

**Dónde viven los archivos:** `~/graphify-workspace/optifierro/graphify-out/`
y `~/graphify-workspace/scrap-geovictoria/graphify-out/` (`graph.json`,
`graph.html`, `GRAPH_REPORT.md`), más el grafo combinado en
`~/graphify-workspace/merged/` — todo en el Mac Studio de Montu.

**Pendiente, no hecho todavía:** ponerle nombres legibles a los grupos de
código (hoy dicen "Community 1", "Community 2", etc.) — requiere un modelo
de IA local, nunca uno externo.

## 3. La regla institucional (vigente desde el 09-09-2026)

**Dato crítico:** este mapeo queda atado al commit `7581b9a`. Cualquier cambio
posterior al código de OptiFierro o de lo relacionado a TO puede volverlo
desactualizado.

A partir del 09-09-2026 rige como regla institucional (agregada al system
prompt del proyecto "Mi TI"):

> Antes de proponer o ejecutar cualquier cambio de código en OptiFierro o en
> cualquier repositorio relacionado con TO, Mi TI y CCa DEBEN consultar el
> grafo de dependencias vigente (Graphify, en `~/graphify-workspace/` del Mac
> Studio) para identificar qué otras partes del sistema se ven afectadas.
> Después de aplicar cualquier modificación real al código de OF/TO, es
> OBLIGATORIO regenerar el grafo antes de cerrar la tarea. El grafo solo se
> considera vigente si corresponde al commit actual del repo — si el commit
> cambió desde la última regeneración, tratarlo como potencialmente
> desactualizado hasta confirmarlo.

**Primer uso real de esta regla:** la noche del 08/09→09-09-2026, antes de
delegar a CCa un fix sobre `_configurar_fechas()` (scraper GeoVictoria,
compartida con el scraper diario en producción), se consultó este grafo para
confirmar los 3 únicos llamadores de la función compartida
(`scrape_y_descarga()`) antes de tocar nada. Ver `bitacora_accesos_torres_ocaranza.md`
y `handoff_actual.md` del Motor de Tiempos para el detalle de esa sesión.

## 4. Nota sobre Aurora

Este registro lo escribió Miaude directo en el catálogo, no Aurora — Aurora
lleva descartada como agente desde el 2026-08-25 (dejó de responder,
invocación colgada sin salida), según el propio código de
`registrar_cambio.py`. Desde esa fecha la escritura al catálogo la hace
Miaude directamente.

## 5. Actualización — 12-09-2026

El mapeo de `scrap-geovictoria` dejó de corresponder al commit `7581b9a`: se
aplicó un fix real a `_configurar_fechas()` (filtro de fecha del scraper
GeoVictoria — ver commit `9985793`) y el grafo se regeneró de inmediato por la
regla institucional de la sección 3.

**Estado nuevo:** `scrap-geovictoria` — 82 nodos, 136 aristas, 16 comunidades,
atado a commit `9985793`. Grafo combinado (`merged/graph.json`) — 892 nodos,
1455 aristas. El mapeo de `optifierro` (commit `7581b9a`) no cambió, sigue
vigente sin modificaciones.

## 6. Actualización — 14-09-2026 (tarea B28/B27, CCa)

**Hallazgo previo:** al consultar el grafo antes de tocar `tiempos_maquina.py`
(regla de la sección 3), se detectó que el mapeo de `optifierro` ya no
correspondía a `7581b9a` sino a `c3d42b00` (regenerado en algún punto entre el
09-09 y el 14-09, sin dejar registro en este archivo — pendiente reconstruir
cuándo/por quién en una próxima sesión). El grafo confirmó, antes de tocar
nada, que `get_tiempos_maquina()` es una función aislada (solo llama a
`_cubigest_conn()`, sin otros llamadores internos) — blast radius mínimo.

**Consulta:** único caso de uso real de la sección 3 hasta ahora aparte del
09-09 (ver sección 3).

**Regeneración post-cambio:** aplicado el fix de unidades de `avg_largo_mm`
(B28) sobre el working tree real de TO (aún no comiteado — Miaude revisa el
diff y comitea después). Para regenerar con contenido real sin inventar un
commit, se sincronizó el archivo corregido al mirror local
(`~/graphify-workspace/optifierro/`, clon de `RodMontu/Optifierro-V2`) sobre
su propio working tree (que ya tenía sincronizado el cambio B27 de
`TiemposPorMaquina.tsx` de una sesión anterior) y se corrió
`graphify update .`.

**Estado nuevo:** `optifierro` — 904 nodos, 1432 aristas, 66 comunidades.
**Importante:** `graph.json.built_at_commit` sigue marcando `c3d42b00`
porque el fix vive en working tree, no en un commit nuevo — la etiqueta de
commit del grafo quedará desactualizada hasta que Miaude comitee y pushee
B28+B27, momento en el que corresponde una nueva regeneración para atar el
grafo al hash real. Tratar el grafo como vigente en contenido pero con
commit-tag pendiente de actualizar.
