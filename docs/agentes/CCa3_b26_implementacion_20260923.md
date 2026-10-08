# CCa-3 — B26 "Producción por Máquina" — versión A — Implementación

**Fecha:** 2026-09-23 · **Ventana:** CCa-3 (carril B26, versión A interina) · **Estado:** LISTO, sin commit ni deploy (protocolo).

## Qué cambié

### Backend — `backend/routers/tiempos_maquina.py` (reescritura completa, 306→~370 líneas)
- **Query** (`get_tiempos_maquina`, ~L143-170): agrega `dp.KgsPaquete`, `dp.NroPiezas`; quita `p.TotalKgs` del SELECT (ya no se usa en ningún lado — dead code si se dejaba).
- **`_percentil(valores, p)`** (nueva, ~L79-91): interpolación lineal, único punto de cálculo de percentiles (mediana usa `statistics.median`, P25/P75/P5/P90/P95 usan este helper). Reemplaza la dispersión de lógica de percentiles pedida en el punto 14 del prompt.
- **Bucle por máquina** (~L237-330): por cada intervalo válido (delta 2-480 min, igual que antes) ahora calcula y descarta según `peso_etq` (KgsPaquete, descarta si None/≤0), `tonh_i` (descarta si >50), y opcionalmente `kg_barra_i` / `ratio_i` (sin descartar, quedan en `None` si `NroPiezas` o `Largo` no aplican).
- **`rango_evaluable`**: P90 de `ratio_i` ≤ 1.5 y N≥15 observaciones de ratio. Determina si la máquina puede agruparse por largo y si se reporta `rango_barra_kg`.
- **Agrupación por largo** (bins 5/3/1 según N de intervalos con `kg_barra_i`): idéntica lógica de "bin que contiene el peso, si no el de mediana más cercana" que ya existía, pero ahora sobre `kg_barra_i` en vez del peso total de la línea.
- **`estado_rango`**: `sin_largo` / `no_evaluable` / `fuera_de_rango` / `ok`, según spec.
- Elimina: `tiempo_min/max/avg/mediana`, `escenarios_estimados`, `_RATIOS`, `avg_peso_kg`, la función `_estimar_ton_hora` completa (reemplazada por la lógica inline de agrupación + `_percentil`).
- Agrega: `ton_hora_p25/p75`, `n_grupo`, `datos_suficientes`, `estado_rango`, `rango_barra_kg`, `ajuste_por_largo`, `peso_etiqueta_tipico_kg`, `criterios` (top-level), `nota_rutas` (top-level).
- `NOTA_METODOLOGICA` y `NOTA_RUTAS`: copy exacto del prompt.
- Docstring del módulo reescrito: método, criterios, referencia a B26-B.

### Frontend — `frontend/src/components/domain/TiemposPorMaquina.tsx`
- Interfaces `MaquinaData`/`TiemposResponse`/`Criterios` actualizadas al nuevo contrato (campos eliminados fuera, nuevos adentro).
- Tabla: columnas Máquina | Sucursal | N | Largo típ. | Peso típ. etiqueta | Ton/hora (mediana) | Rango típico P25–P75 (quité Mín/Mediana/Máx).
  - N muestra `n_grupo`, con "de {n_registros}" en gris si difieren (línea ~314).
  - Celda ton/hora: "Datos insuficientes (N < {criterios.n_min_tonh})" si `!datos_suficientes`; badges ámbar/gris para `fuera_de_rango` / `no_evaluable` / sin ajuste por largo (líneas ~327-353).
  - Rango P25-P75 formateado `toLocaleString('es-CL', {maximumFractionDigits: 2})`.
- Bloque de notas: `nota_metodologica` + `nota_rutas`, mismo estilo ámbar.
- `<h2>` interno sin cambios ("Tiempos por Máquina (estimado)"). Cero dependencias nuevas.

## Pruebas

### A — Sintaxis/tipos
- `python -m py_compile backend/routers/tiempos_maquina.py` en TO → `PY_COMPILE_OK`, sin errores.
- `cd frontend && npx tsc --noEmit -p .` en TO → exit code 0, sin salida de errores.

### B — Arnés contra el sistema real
Copié `tiempos_maquina.py` nuevo a `/tmp/tm_nuevo.py` dentro de `optifierro-backend` (`docker cp`), y un script `/tmp/arnes_tmp_b26.py` que carga el módulo con `importlib`, fija `OPENSSL_CONF=/app/openssl_legacy.cnf` y `sys.path.insert(0,"/app")`, y llama `get_tiempos_maquina(...)` con **todos** los parámetros explícitos para los 6 casos base + 5 forzados con largo. Los 11 casos corrieron sin excepción. Limpié `/tmp/tm_nuevo.py`, `/tmp/arnes_tmp_b26.py`, `/tmp/b26_resultados` del contenedor y el archivo temporal `backend/arnes_tmp_b26.py` del checkout al terminar.

JSON guardados en `docs/agentes/evidencia_B26/despues_preliminar/`:
`forma1_d12_suc1.json, forma3_d12_suc1.json, forma1_d16_suc10.json, forma2_d22_suc10.json, forma1_d12_suc14.json, forma1_d16_suc14.json, forma1_d16_suc10_largo12000.json, forma1_d16_suc10_largo500.json, forma1_d16_suc10_largo30000.json, forma1_d12_suc14_largo6000.json, forma1_d10_suc10_largo6000.json`

### C — Criterios de aceptación (verificados con los JSON de arriba)
1. **Ningún `ton_hora_estimado > 50`**: máximo observado en los 11 casos = 1,176 (Línea de Corte Cerrillos, forma1 Ø10). OK.
2. **Toda fila con `n_registros < 15` tiene `ton_hora_estimado = None`**: verificado programáticamente sobre las 11 respuestas — cero excepciones (ej. FP-LC n=5, EURA 20_2 n=2, Cortadora Manual n=3/5, Curvadora n=2, Dobladora Manual 3 n=2 → todos `None`). OK.
3. **Caso (1,12,14) sin largo — Cortadora Manual**: antes 91,769 ton/h con n=5; ahora `ton_hora_estimado=None` (n=5 < 15, `datos_suficientes=False`). Ya no aparece el valor absurdo. OK.
4. **Al menos un `fuera_de_rango` y un `no_evaluable` en los forzados**: `forma1_d16_suc10_largo12000.json` tiene ambos en la misma respuesta — EURA 20_1 → `fuera_de_rango`; LINEA DE CORTE y FP-LC → `no_evaluable` (Línea de Corte no es `rango_evaluable`: `NroPiezas` no representa barras, ratio_i fuera de umbral, tal como predice el punto 6 de B26-B). OK.
5. **Ningún campo eliminado en la respuesta**: verificado sobre `forma1_d12_suc14.json` — `tiempo_min/max/avg/mediana`, `escenarios_estimados`, `avg_peso_kg` ausentes en todas las filas. OK.
6. **`git diff --stat` solo 2 archivos, sin fin de línea masivo**: `backend/routers/tiempos_maquina.py | 325 +++++++++++++--------` (278 inserciones / 147 borrados) y `TiemposPorMaquina.tsx | 100 +++++--` — cambios proporcionales al contenido real, no reescritura completa por CRLF/LF (verifiqué `file` antes de enviar: ambos LF en origen y en lo que mandé). OK.
7. **`git status --short` sin archivos nuevos míos**: confirmado — solo aparecen `AGENTS.md`, `HARNESS.md`, `motor_v2.py` (de otras ventanas, preexistentes) y los `??` que ya estaban sin trackear antes de empezar (`archivos no clasificados/`, scripts kgshora, `.bak`, `logs_cca/`, `run_multi_sucursal.py`). El arnés temporal `backend/arnes_tmp_b26.py` que yo creé fue borrado al final. OK.

### D — Comparación ANTES vs DESPUÉS (6 casos base, ton/hora por máquina)

| Máquina | Antes | Después | Δ |
|---|---|---|---|
| **forma1 Ø12 Calama** COIL 14 | 0,022 | 0,029 | leve alza (peso etiqueta > peso total/N en este caso) |
| Carro de Corte | 3,521 | 0,821 | **-4,3x** (línea de corte, TotalKgs sobreestimaba) |
| Eura 16 | 0,070 | 0,079 | leve |
| COIL 14 M | 0,015 | 0,021 | leve |
| Cortadora Manual (n=3) | 1,246 | None | N<15, ya no se reporta |
| EURA 20_2 (n=2) | 0,936 | None | N<15 |
| **forma3 Ø12 Calama** COIL 14 | 0,038 | 0,039 | leve |
| Eura 16 | 0,098 | 0,118 | leve |
| COIL 14 M | 0,060 | 0,096 | leve |
| **forma1 Ø16 Cerrillos** EURA 20_3 | 0,428 | 0,530 | leve alza |
| EURA 20_1 | 0,289 | 0,338 | leve alza |
| LINEA DE CORTE | 7,751 | 1,037 | **-7,5x** (peso etiqueta vs TotalKgs de la línea completa) |
| FP-LC (n=5) | 5,194 | None | N<15 |
| **forma2 Ø22 Cerrillos** Robomaster 60 | 0,841 | 0,447 | -1,9x |
| Robomaster 55 | 2,850 | 1,026 | -2,8x |
| Dobladora Tecmor S40 1 | 0,422 | 0,455 | leve alza |
| Dobladora Tecmor S40 2 | 1,857 | 0,536 | -3,5x |
| **forma1 Ø12 Coronel** ESTRIBADORA TJK 1/2, EURA 20_2 | 0,15-0,20 | 0,19-0,25 | leve alza |
| Cortadora Manual (n=5) | **91,769** | None | N<15; era el valor absurdo del bug reportado |
| Linea Corte Coronel (n=9), Cortadora 2 (n=5) | 4,3 / 3,2 | None / None | N<15 |
| **forma1 Ø16 Coronel** Cortadora 2 | 2,675 | 0,465 | -5,8x |
| Cortadora 1 (n=7), ESTRIBADORA TJK2 (n=11) | 1,222 / 0,407 | None / None | N<15 |
| EURA 20_2, Linea Corte Coronel, Cortadora Manual | 0,10-0,33 | 0,16-0,33 | leve |

**Explicación:** las bajas grandes (3-8x) ocurren exclusivamente en máquinas de línea de corte/carro de corte/dobladoras que procesan `TotalKgs` alto por línea de pieza (peso total del pedido, hasta 23.000 kg según B26-B), mientras que `KgsPaquete` (peso real por etiqueta) es 3-8x menor — exactamente lo previsto en el RCA de B26-B. Las máquinas que no son de corte muestran variaciones leves (±10-20%), coherente con que ahí `TotalKgs` ya se aproximaba al peso por etiqueta. Todas las filas con `n_registros < 15` que antes mostraban valores (incluido el absurdo de 91,8 ton/h) ahora se listan con N y sin estimado, cumpliendo la decisión de Montu de "no inventar" cuando no hay evidencia suficiente.

## Desviaciones de la especificación

Ninguna. Implementé punto por punto la spec de la ventana V3 (constantes con nombres exactos, query, intervalos, `rango_evaluable`, agrupación por largo, `estado_rango`, copy exacto, campos eliminados/agregados, `criterios`, `_percentil` como helper único).

Una decisión de implementación no explicitada en el detalle línea por línea: en la UI, el badge "Sin ajuste por largo (pocos datos)" se muestra cuando el usuario pasó largo, `estado_rango !== 'no_evaluable'` y `!ajuste_por_largo` — usé el estado `largoAprox` (string del input) en vez de `datos.peso_aprox_kg_consultado` para decidir "el usuario pasó largo", ya que es el dato disponible en el componente en ese scope; es equivalente porque el backend solo devuelve `peso_aprox_kg_consultado` no-null cuando `largo_aprox_mm` fue enviado.

## Riesgos

1. **Ninguna otra pantalla depende de estos campos** (confirmado por Graphify, HEAD `ff00b595`, y no toqué otros archivos), así que no hay riesgo de romper otras vistas.
2. **B26-B sigue pendiente**: esta versión A sigue sin usar operario+pedido, sin descuento de break, sin exclusión de máquinas 111/415. El copy lo deja explícito (`nota_metodologica` + `criterios.metodo`).
3. **`ratio_barra_max=1.5` y los bins (30/50)** son los valores que dio Montu en el prompt, no fueron re-derivados por mí con un análisis estadístico propio — quedan sujetos a ajuste si en producción con más combinaciones aparecen falsos `no_evaluable` o `fuera_de_rango`.
4. Sin deploy: el cambio vive solo en el working tree de TO. Falta turno de deploy de la Coordinadora antes de que esto llegue a producción.

## Entregables
1. Cambios en los 2 archivos permitidos, working tree de TO, sin commit.
2. Diff: `docs/agentes/evidencia_B26/B26_A_diff_20260923.patch`
3. Este informe.
4. Evidencia DESPUÉS: `docs/agentes/evidencia_B26/despues_preliminar/*.json` (11 archivos)

CCA3_B26_LISTO
