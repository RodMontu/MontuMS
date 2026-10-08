# CCa-3 — B26 "Produccion por Maquina" — version A (ejecucion en lote unico)

Eres CCa (Claude Code). Trabajas para Montu (Ingeniero Civil Industrial, no programador; trato de "tu", nunca voseo). Este lote implementa la version A de B26.
Contexto completo en `/Users/montu/MontuMS/docs/agentes/prompts/V3_b26_produccion_maquina.md` y `/Users/montu/MontuMS/docs/agentes/prompts/00_CONTEXTO_BASE_OLA1.md` (leelos primero, en ese orden). Criterios y evidencia: `/Users/montu/MontuMS/docs/B26_B_pendiente_metodo_validado.md`.
Nombre en textos de usuario: "SPP" o "el Planificador". NUNCA "OptiFierro" en copy visible (si en nombres tecnicos).

## REGLAS DURAS (no negociables)
1. **Solo puedes modificar 2 archivos** en el checkout REAL de TO (`ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && ..."`, Git Bash; prefijo `MSYS_NO_PATHCONV=1` para docker):
   - `backend/routers/tiempos_maquina.py`
   - `frontend/src/components/domain/TiemposPorMaquina.tsx`
   PROHIBIDO tocar cualquier otro archivo del repo, en especial `motor_v2.py`, `routers/programacion.py`, `GestorProgramacion.tsx`, `App.tsx`, `main.py`. Si crees que necesitas otro archivo: DETENTE y reportalo.
2. **NO commit, NO push, NO `git add`, NO stash/checkout/reset.** Deja los cambios en el working tree. El commit lo hace otra ventana.
3. **NO `docker build`, NO `docker compose up/restart`, NO tocar contenedores en marcha** (deploy solo con turno de la Coordinadora). Permitido: `docker exec` de solo lectura y `docker cp` de un archivo hacia `/tmp` del contenedor para pruebas.
4. **Cubigest: SOLO LECTURA** (solo SELECT). Sucursales: Calama=1 | Cerrillos=10 (SQLite) / 4 (Cubigest) | Coronel=14.
5. `~/graphify-workspace/optifierro` es espejo de LECTURA: nunca edites ahi. Edita en TO. Para escribir un archivo en TO: prepara el contenido final en `/tmp/b26/` (Mac) y envialo con `ssh TO "cat > /c/Users/OptiFierro/Desktop/optifierro/<ruta>" < /tmp/b26/<archivo>`. Preserva codificacion UTF-8 y los fines de linea originales del archivo (verifica con `git diff --stat`: si aparece TODO el archivo cambiado, es problema de fin de linea: corrigelo).
6. No modifiques ni borres archivos sin trackear existentes (`*.bak`, `logs_cca/`, `kgshora*`, etc.).
7. RCA con evidencia antes de cambiar comportamiento; si algo se atasca: para, reporta y propone la alternativa mas simple. Sin loops.
8. Antes de modificar, consulta Graphify (`~/graphify-workspace/optifierro/graphify-out/GRAPH_REPORT.md`, HEAD `ff00b595`): B26 solo depende de estos 2 archivos (verificado: ninguna otra pantalla consume tiempo_min/tiempo_mediana/tiempo_max/escenarios_estimados).
9. Verifica tu propio trabajo (el autoreporte no basta): revisaras el `git diff` real y correras las pruebas de abajo.

## DECISIONES DE MONTU (23-09) — implementar EXACTAMENTE esto
Contexto: el ton/hora del endpoint sale de deltas crudos entre registros consecutivos (filtro laxo 2-480 min), NO del metodo validado de FASE3 (eso es B26-B, pendiente). A = version interina honesta.

### Backend (`tiempos_maquina.py`)
Constantes nuevas (nombres exactos, con comentario que cite este criterio): `_N_MIN_TONH = 15`, `_TONH_MAX = 50.0`, `_RANGO_PCT_INF = 0.05`, `_RANGO_PCT_SUP = 0.95`, `_BINS_5_MIN_N = 50`, `_BINS_3_MIN_N = 30`, `_RATIO_BARRA_MAX = 1.5`.
1. **Query:** agrega `dp.KgsPaquete AS KgsPaquete` y `dp.NroPiezas AS NroPiezas`. `p.TotalKgs` deja de usarse para ton/hora ni para peso tipico (es el peso TOTAL de la linea de pieza, no el de la etiqueta: error de origen). Todo SELECT, sin tocar filtros existentes.
2. **Intervalos por (MaquinaId, IdSucursal):** igual que hoy (delta entre registros consecutivos, `2 <= delta_min <= 480`), y ademas por cada intervalo: `peso_etq = KgsPaquete` del registro que abre el intervalo; descarta el intervalo si `peso_etq` es None o <= 0. `tonh_i = (peso_etq/1000)/(delta_min/60)`; descarta si `tonh_i > _TONH_MAX`. `kg_barra_i = KgsPaquete/NroPiezas` si NroPiezas > 0, si no None. `ratio_i = kg_barra_i / ((diametro**2/162) * Largo_m)` si Largo > 0 (p.Largo esta en METROS).
3. **`n_registros`** = intervalos validos (tras todos los descartes). Si `n_registros == 0`, la maquina se omite (como hoy).
4. **Maquina evaluable para largo** (`rango_evaluable`): true si hay >= `_N_MIN_TONH` valores de `ratio_i` y el percentil 90 de `ratio_i` <= `_RATIO_BARRA_MAX`. (Lineas de corte: NroPiezas no representa barras -> no evaluable.)
5. **Agrupacion por largo** (solo si el usuario paso `largo_aprox_mm`, la maquina es `rango_evaluable` y hay `kg_barra_i`): ordena intervalos por `kg_barra_i`; `n_bins = 5` si N >= `_BINS_5_MIN_N`, `3` si N >= `_BINS_3_MIN_N`, si no `1` (sin ajuste por largo; `ajuste_por_largo=False`). Bin elegido = el que contiene `peso_aprox_kg`; si ninguno lo contiene, el de mediana de `kg_barra` mas cercana (comportamiento actual). Sin largo o no evaluable: grupo = todos los intervalos.
6. **Estadisticos del grupo elegido:** `ton_hora_estimado` = mediana de `tonh_i` (redondeo 3); `ton_hora_p25` y `ton_hora_p75` = percentiles 25 y 75 de `tonh_i` (usa `statistics.quantiles(..., n=4, method="inclusive")` o equivalente; con < 2 datos, None); `n_grupo` = tamaño del grupo; `peso_referencia_kg` = mediana de `kg_barra_i` del grupo (solo cuando hubo ajuste por largo, si no None).
7. **Suficiencia:** `datos_suficientes = (n_registros >= _N_MIN_TONH)`. Si False: `ton_hora_estimado`, `ton_hora_p25`, `ton_hora_p75` = None (la fila se lista igual, con su N).
8. **Indicador fuera de rango** (`estado_rango`, string): `"sin_largo"` si el usuario no paso largo; `"no_evaluable"` si paso largo y la maquina no es evaluable o no hay datos suficientes; `"fuera_de_rango"` si `peso_aprox_kg < P5` o `> P95` de `kg_barra_i` (percentiles `_RANGO_PCT_INF/_SUP` sobre TODOS los intervalos de la maquina); `"ok"` en otro caso. Devuelve tambien `rango_barra_kg = [P5, P95]` (redondeo 1) cuando la maquina es evaluable, si no None. En `fuera_de_rango` el ton/hora se sigue entregando (bin extremo mas cercano) pero la UI lo advierte.
9. **Peso/largo tipicos:** `avg_largo_mm` igual que hoy. Reemplaza `avg_peso_kg` por `peso_etiqueta_tipico_kg` = mediana de `KgsPaquete` de los intervalos validos (redondeo 1).
10. **Elimina de la respuesta y del codigo:** `tiempo_min`, `tiempo_max`, `tiempo_avg`, `tiempo_mediana`, `escenarios_estimados`, `_RATIOS`, `avg_peso_kg`.
11. **Copy exacto** (constante `NOTA_METODOLOGICA`, reemplaza el actual): `"Producciones estimadas en base a antecedentes historicos de produccion; rango tipico segun el historial (P25-P75). Es una estimacion referencial: no es un intervalo de confianza ni esta validada a nivel de operario y pedido."` Nueva constante `NOTA_RUTAS` = `"Las maquinas listadas son las que procesaron esta forma y diametro segun el historial; no corresponden al ruteo que calcula el Planificador."` Ambas en la respuesta (`nota_metodologica`, `nota_rutas`).
12. **Respuesta top-level:** conserva `id_forma, diametro, meses_consultados, total_registros (suma de n_registros), dotacion_detectable, peso_aprox_kg_consultado, por_maquina`; agrega `criterios` = dict con las constantes (`n_min_tonh`, `tonh_max`, `rango_pct`, `bins_5_min_n`, `bins_3_min_n`, `ratio_barra_max`, `metodo`: "delta crudo entre registros consecutivos (2-480 min); no validado a nivel operario+pedido (ver B26-B)"). El caso sin filas devuelve la misma estructura con `por_maquina: []`.
13. Actualiza el docstring del modulo: metodo, criterios, y `Pendiente B26-B: portar metodo validado FASE3 (ver docs/B26_B_pendiente_metodo_validado.md)`. Cubigest READ-ONLY y FP-006 se mantienen.
14. `stats.quantiles`/percentiles: implementa un helper pequeño y testeable (`_percentil(valores, p)` interpolacion lineal) en vez de dispersar logica.

### Frontend (`TiemposPorMaquina.tsx`)
- Actualiza interfaces al nuevo contrato (borra los campos eliminados, agrega los nuevos: `n_grupo, ton_hora_p25, ton_hora_p75, datos_suficientes, estado_rango, rango_barra_kg, ajuste_por_largo, peso_etiqueta_tipico_kg, peso_referencia_kg`; respuesta: `nota_rutas, criterios`).
- El `<h2>` interno se mantiene: "Tiempos por Máquina (estimado)". No cambies el menu ni `App.tsx`.
- Tabla, columnas en este orden: Máquina | Sucursal | N | Largo típ. (mm) | Peso típ. etiqueta (kg) | Ton/hora (mediana) | Rango típico P25–P75. Quita Mín/Mediana/Máx.
  - N: `n_grupo`; si `n_grupo !== n_registros`, agrega debajo en gris pequeño "de {n_registros}".
  - Ton/hora: si `!datos_suficientes`, muestra "Datos insuficientes (N < {criterios.n_min_tonh})" en gris y deja el rango en "—". Si hay `peso_referencia_kg`, "@ x kg/barra" debajo (como hoy con kg/pieza).
  - Rango: "{p25} – {p75}" con formato es-CL (`toLocaleString('es-CL', {maximumFractionDigits: 2})`).
  - Insignias bajo el ton/hora segun `estado_rango`: `fuera_de_rango` -> ambar "Fuera del rango histórico de esta máquina ({rango_barra_kg[0]}–{rango_barra_kg[1]} kg/barra)"; `no_evaluable` -> gris "Rango no evaluable en esta máquina"; y si el usuario paso largo y `ajuste_por_largo === false` con `estado_rango !== 'no_evaluable'` -> gris "Sin ajuste por largo (pocos datos)".
- Bloque de notas (sustituye el actual): `data.nota_metodologica` y debajo `data.nota_rutas`, mismo estilo ambar del actual, sin porcentaje de confianza.
- Conserva filtros, estados (idle/loading/ok/empty/error), resaltado de la fila con mayor N y el footer. Mantén el estilo visual existente. Cero dependencias nuevas.

## PRUEBAS OBLIGATORIAS (sin deploy)
A. **Sintaxis/tipos:** compila el backend (`python -m py_compile` dentro de un `docker exec` sobre la copia en /tmp, o con el python disponible) y verifica el frontend con `cd frontend && npx tsc --noEmit -p .` (o el comando de tipos del proyecto). Sin errores. No generes `dist`.
B. **Arnes contra el sistema real (solo lectura):** copia el router nuevo a `/tmp/tm_nuevo.py` del contenedor `optifierro-backend` (`docker cp`), y ejecutalo con un script que use `-w /app`, `os.environ["OPENSSL_CONF"]="/app/openssl_legacy.cnf"`, `sys.path.insert(0,"/app")` y cargue `/tmp/tm_nuevo.py` con `importlib`. Llama `get_tiempos_maquina(id_forma=..., diametro=..., sucursal_id=..., meses=24, largo_aprox_mm=...)` (pasa TODOS los parametros; no dependas de defaults). Casos: (forma,diam,sucursal) = (1,12,1), (3,12,1), (1,16,10), (2,22,10), (1,12,14), (1,16,14), cada uno SIN largo; y forzados con largo: (1,16,10) con 12000 mm y con 500 mm y con 30000 mm; (1,12,14) con 6000 mm; (1,10,10) con 6000 mm.
   Guarda las salidas JSON en `/Users/montu/MontuMS/docs/agentes/evidencia_B26/despues_preliminar/` (nombres `formaX_dY_sucZ[_largoN].json`).
C. **Criterios de aceptacion (verificalos y reportalos con numeros):** (i) ninguna fila con `ton_hora_estimado > 50`; (ii) toda fila con `n_registros < 15` tiene `ton_hora_estimado = None`; (iii) el caso (1,12,14) sin largo ya no muestra 91,8 ton/h en Cortadora Manual; (iv) hay al menos un caso `fuera_de_rango` y uno `no_evaluable` (lineas de corte) en los forzados; (v) ningun campo eliminado sigue en la respuesta; (vi) `git diff --stat` en TO muestra SOLO los 2 archivos permitidos, sin cambios de fin de linea masivos; (vii) `git status --short` no muestra otros archivos nuevos tuyos.
D. Compara contra la foto ANTES (`/Users/montu/MontuMS/docs/agentes/evidencia_B26/antes/*.json`) y resume en tabla las diferencias de ton/hora por maquina (antes vs despues) para los 6 casos base; explica las diferencias grandes (esperado: lineas de corte bajan 3-5x por usar KgsPaquete).

## ENTREGABLES
1. Cambios en los 2 archivos (working tree TO, sin commit).
2. `git diff` completo guardado en `/Users/montu/MontuMS/docs/agentes/evidencia_B26/B26_A_diff_20260923.patch` (generado con `ssh TO "cd ... && git diff -- backend/routers/tiempos_maquina.py frontend/src/components/domain/TiemposPorMaquina.tsx"`).
3. Informe `/Users/montu/MontuMS/docs/agentes/CCa3_b26_implementacion_20260923.md`: que cambiaste (por archivo y funcion, con `archivo:linea`), resultados de las pruebas A-D con salida real, cualquier desviacion de esta especificacion y por que, riesgos.
4. Ultima linea de tu salida: `CCA3_B26_LISTO` si todo paso, o `CCA3_B26_BLOQUEADO: <motivo>` si algo te detuvo.
