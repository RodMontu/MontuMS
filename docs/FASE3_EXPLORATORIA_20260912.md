# Fase 3 — Análisis exploratorio preliminar de tiempos por máquina

**Fecha:** 2026-09-12
**Estado: EXPLORATORIO / PRELIMINAR — NO es la corrida oficial de Fase 3.**
Falta la corrección de censura de jornada (depende de `turnos_programados`,
pendiente de otra ventana de trabajo). Los resultados de forma de distribución
aquí presentados **no deben usarse todavía** para calibrar el motor de
planificación — ver conclusión al final.

## Origen de los datos

- Fuente: `optifierro-backend:/app/fase2_rutas_completo.db`, tabla `datos_rutas`.
- 373.934 filas, 49.450 etiquetas únicas, 3 plantas, 24 meses
  (2024-09-01 a 2026-08-31).
- Ejecutado directamente en el contenedor `optifierro-backend` vía
  `docker exec` en el servidor TO (solo lectura, no toca Cubigest).
- Se instaló `scipy==1.17.1` en el contenedor (no estaba presente; pandas y
  numpy sí).

### Nota — inconsistencia de ID de sucursal confirmada en los datos

`datos_rutas.idsucursal` usa la convención de `motor_v2.py`
(**Cerrillos = 4**), NO la de `maquinas_info` / API / frontend
(**Cerrillos = 10**). Para mapear nombres de máquina se usó el alias
`idsucursal 4 → sucursal_id 10` contra la tabla `maquinas_info` de
`optifierro_v2.db`. Esto es exactamente la inconsistencia ya documentada en
`CLAUDE.md` — queda confirmada también en el dataset de Fase 2, no solo en
el motor.

Algunos `maquina_id` presentes en `datos_rutas` no tienen entrada en
`maquinas_info` (catálogo desactualizado/incompleto): `25, 26, 27, 28`
(Cerrillos) y `108, 111` (Calama), `413, 414, 415, 416, 417` (Coronel).
Se reportan igual, marcados como `SIN_CATALOGO_<id>`.

## Metodología

1. **Delta entre visitas consecutivas**: por cada etiqueta, se ordenan sus
   filas por `fecha_produccion` y se calcula el tiempo transcurrido hasta la
   visita siguiente. Ese delta se atribuye a la máquina del paso N (proxy de
   tiempo real de trabajo/tránsito en esa máquina — metodología ya validada
   en Fase 1 / MT-04).
2. **Multi-máquina / pool (APROXIMACIÓN, ver limitación abajo)**: se agrupó el
   catálogo de máquinas por "familia" quitando el sufijo `_<n>` final del
   nombre (ej. `EURA 20_1`, `EURA 20_2`, `EURA 20_3` → familia `EURA 20`).
   Toda familia con 2+ `maquina_id` distintos en la misma sucursal se
   consideró un pool candidato. Una etiqueta se marcó como
   **multi-máquina/pool** si visitó 2 o más `maquina_id` distintos de la
   misma familia-pool en algún momento de su recorrido, y se **excluyó** del
   set principal de calibración, contándose aparte.
   - **Esto NO es el criterio oficial.** El documento
     `docs/TAREA_MULTIMAQUINA_20260906.md` (MontuMS) existe pero responde a
     una pregunta distinta: si el 16,2% "multi-máquina" de
     Cerrillos/delgado/agosto-2026 es en realidad una secuencia normal de
     ruta (corte→estribadora, +dobladora manual) y no duplicación de pool.
     No define un criterio mecánico de pool aplicable a las 3 plantas /
     24 meses completos. Para esta pasada exploratoria se usó la
     aproximación por sufijo de nombre descrita arriba, sabiendo que:
     - Solo detectó explícitamente **una familia-pool real**: `EURA 20`
       en Cerrillos (ids 14 `EURA 20_1` y 16 `EURA 20_3`; no hay `EURA 20_2`
       registrado en Cerrillos).
     - Otras posibles familias con nombres tipo "Dobladora Tecmor S40 1/2",
       "Curvadora 1/2", "Dobladora 2/3/4", "ESTRIBADORA TJK 1/2" **no se
       agruparon** porque el sufijo va con espacio, no con guion bajo, y
       fusionarlas automáticamente habría sido arriesgado sin confirmar si
       son unidades físicas intercambiables (pool real) o máquinas
       funcionalmente distintas. Quedan sin marcar — **subestimación
       probable** del universo multi-máquina real.
     - Las máquinas `SIN_CATALOGO_*` no pudieron evaluarse para pool por
       falta de nombre.
3. **Limpieza de deltas**: se excluyeron deltas `<= 0` horas (desorden de
   timestamps) y deltas `> 30 días` (720 h, considerados error de dato /
   no representativos de tiempo de máquina), reportados aparte, no
   descartados en silencio.
4. **Estadística y ajuste de distribución** (`scipy.stats`, sobre el set
   principal limpio, por `maquina_id`): n, mediana, percentil 80 (p80 —
   métrica que usará el motor), asimetría (skew), curtosis, y comparación de
   3 candidatas (log-normal, gamma, Weibull) por AIC/BIC (ajuste con
   `floc=0`).

## Resultados — universo y exclusiones

| Concepto | Valor | % |
|---|---|---|
| Filas totales | 373.934 | — |
| Etiquetas totales | 49.450 | 100% |
| Etiquetas multi-máquina/pool excluidas (aproximación) | 5.914 | 11,96% |
| Deltas calculados (set principal, sin pool) | 146.570 | 100% de deltas del set principal |
| Deltas negativos o cero (error de timestamps) | 5.423 | 3,7% |
| Deltas absurdos (> 30 días) | 67.812 | 46,3% |
| Deltas limpios usados para estadística | 73.335 | 50,0% |

**Hallazgo más importante de esta pasada:** el 46,3% de los deltas caen fuera
del umbral de 30 días. Esto es exactamente el efecto de censura de jornada
que la tarea advierte como pendiente: sin filtrar por `turnos_programados`,
un delta "entre visitas consecutivas" mezcla tiempo real de máquina con
tiempo de espera en cola, fines de semana, y períodos sin producción
programada. El 30 días es un corte arbitrario de "esto es claramente error",
no un filtro de censura real — probablemente una fracción sustancial de los
deltas *dentro* de los 30 días también incluye tiempo de espera no
productivo, no solo tiempo de máquina.

## Resultados por máquina (set principal limpio, `n`, mediana y p80 en horas)

| maquina_id | Sucursal | Nombre | n | Mediana (h) | p80 (h) | Skew | Kurtosis | Mejor ajuste (AIC) |
|---|---|---|---|---|---|---|---|---|
| 10 | Cerrillos | Dobladora Tecmor S40 1 | 7.232 | 252,7 | 517,6 | 0,35 | -1,14 | gamma |
| 11 | Cerrillos | Dobladora Tecmor S40 2 | 7.660 | 247,8 | 519,1 | 0,36 | -1,15 | gamma |
| 13 | Cerrillos | EURA 16 | 7.116 | 222,2 | 508,5 | 0,43 | -1,16 | gamma |
| 14 | Cerrillos | EURA 20_1 | 8.218 | 246,8 | 500,4 | 0,38 | -1,13 | gamma |
| 16 | Cerrillos | EURA 20_3 | 1.443 | 238,8 | 492,0 | 0,46 | -0,99 | weibull_min |
| 17 | Cerrillos | FP-LC | 6.097 | 206,2 | 469,8 | 0,60 | -0,79 | gamma |
| 21 | Cerrillos | PRIMA 3D | 1.246 | 298,5 | 454,2 | -0,10 | -0,95 | weibull_min |
| 22 | Cerrillos | Robomaster 55 | 7.176 | 258,4 | 549,7 | 0,42 | -1,09 | weibull_min |
| 23 | Cerrillos | Robomaster 60 | 336 | 202,8 | 461,2 | 0,53 | -0,91 | weibull_min |
| 24 | Cerrillos | FORMULA 12 | 1.967 | 223,8 | 408,3 | 0,36 | -0,86 | weibull_min |
| 25 | Cerrillos | SIN_CATALOGO_25 | 1.193 | 171,2 | 320,8 | 1,05 | 0,39 | gamma |
| 26 | Cerrillos | SIN_CATALOGO_26 | 588 | 165,7 | 424,4 | 0,99 | -0,21 | gamma |
| 27 | Cerrillos | SIN_CATALOGO_27 | 97 | 467,9 | 490,4 | -1,81 | 1,89 | weibull_min |
| 28 | Cerrillos | SIN_CATALOGO_28 | 3 | 26,6 | 26,6 | — | — | n<30, insuficiente |
| 101 | Calama | COIL 14 M | 1.760 | 263,7 | 532,4 | 0,36 | -1,09 | weibull_min |
| 102 | Calama | Cortadora Manual | 485 | 160,9 | 381,2 | 1,07 | 0,01 | weibull_min |
| 104 | Calama | Dobladoras | 2.854 | 211,2 | 415,3 | 0,68 | -0,52 | weibull_min |
| 105 | Calama | EURA 16 | 2.007 | 311,5 | 566,1 | 0,19 | -1,23 | weibull_min |
| 106 | Calama | EURA 20_2 | 848 | 188,7 | 388,8 | 0,68 | -0,54 | gamma |
| 107 | Calama | Robomaster 60 | 1.209 | 193,0 | 351,1 | 0,76 | -0,08 | weibull_min |
| 108 | Calama | SIN_CATALOGO_108 | 16 | 30,8 | 53,6 | — | — | n<30, insuficiente |
| 111 | Calama | SIN_CATALOGO_111 | 232 | 269,6 | 400,6 | 0,17 | -0,91 | gamma |
| 401 | Coronel | Curvadora 1 | 11 | 200,6 | 464,7 | — | — | n<30, insuficiente |
| 402 | Coronel | Curvadora 2 | 39 | 93,5 | 357,3 | 1,13 | -0,03 | gamma |
| 404 | Coronel | Dobladora 2 | 237 | 152,1 | 311,2 | 1,11 | 0,30 | gamma |
| 405 | Coronel | Dobladora 3 | 286 | 239,1 | 358,2 | 0,62 | -0,20 | weibull_min |
| 406 | Coronel | Dobladora 4 | 2.053 | 186,0 | 335,6 | 0,85 | 0,43 | weibull_min |
| 407 | Coronel | ESTRIBADORA TJK 1 | 1.192 | 161,1 | 340,3 | 1,00 | 0,30 | weibull_min |
| 411 | Coronel | ESTRIBADORA TJK 2 | 141 | 174,5 | 330,7 | 1,04 | 0,51 | weibull_min |
| 412 | Coronel | Linea Corte Coronel | 3.794 | 278,7 | 473,8 | 0,27 | -0,87 | weibull_min |
| 413 | Coronel | SIN_CATALOGO_413 | 340 | 273,2 | 456,4 | 0,40 | -0,82 | weibull_min |
| 414 | Coronel | SIN_CATALOGO_414 | 4.919 | 297,4 | 484,4 | 0,19 | -0,75 | weibull_min |
| 415 | Coronel | SIN_CATALOGO_415 | 359 | 241,4 | 449,5 | 0,38 | -0,78 | gamma |
| 416 | Coronel | SIN_CATALOGO_416 | 131 | 312,5 | 459,0 | 0,06 | -0,84 | gamma |
| 417 | Coronel | SIN_CATALOGO_417 | 50 | 213,6 | 304,6 | 1,11 | 0,52 | weibull_min |

35 máquinas con datos; 3 quedaron con n<30 (28, 108, 401) y no se ajustó
distribución.

**Patrón por AIC:** gamma y Weibull se reparten casi todo el liderazgo
(ninguna máquina favorece log-normal por AIC). No hay una distribución única
claramente dominante — ambas candidatas quedan muy cerca en la mayoría de
los casos, típico cuando la muestra todavía mezcla tiempo de proceso real con
tiempo de espera no filtrado.

## Outliers y errores encontrados (no descartados en silencio)

- **5.423 deltas ≤ 0 horas** (3,7% del total de deltas del set principal):
  timestamps desordenados o duplicados dentro de la misma etiqueta.
- **67.812 deltas > 30 días** (46,3%): tratados como error de dato /
  no representativos para esta pasada exploratoria, pero es altamente
  probable que una fracción importante de estos sean simplemente trabajos
  con paradas largas legítimas (fin de semana largo, feriado, espera de
  materia prima) — el corte de 30 días es una heurística gruesa, no un
  criterio validado. Requiere revisión con `turnos_programados` en Fase 3
  real.

## Subconjunto multi-máquina/pool excluido

- **5.914 etiquetas (11,96% del total)** excluidas por la aproximación de
  familia-pool (ver metodología). Casi la totalidad detectada corresponde a
  la familia `EURA 20` en Cerrillos.
- Este número **no es comparable directamente** con el 16,2% mencionado en
  `docs/TAREA_MULTIMAQUINA_20260906.md`, porque ese 16,2% era específico de
  Cerrillos/delgado/agosto-2026 con un criterio distinto (cualquier etiqueta
  con más de una máquina en su secuencia, sin distinguir ruta normal de pool
  real). El 11,96% de esta pasada es multi-planta/24-meses y solo cuenta
  colisión dentro de la misma familia-pool por nombre.
- Como se explicó arriba, es probable que este número **subestime** el
  universo real de multi-máquina/pool porque no capturó familias con sufijo
  numérico sin guion bajo (Dobladora Tecmor S40 1/2, Curvadora 1/2,
  Dobladora 2/3/4, ESTRIBADORA TJK 1/2).

## Conclusión honesta — ¿qué tan lista está la forma de la distribución para Fase 3 real?

**No está lista para calibración oficial.** Razones concretas:

1. El 46,3% de deltas fuera del umbral de 30 días, y con alta probabilidad
   una fracción no despreciable de los deltas "limpios" restantes, mezclan
   tiempo de máquina real con tiempo de espera/censura de jornada no
   productiva. Sin `turnos_programados` para corregir esto, las medianas de
   ~150-300 horas (6-12 días) por máquina son casi con certeza tiempo de
   ciclo end-to-end, no tiempo de trabajo real en la máquina — son
   inverosímiles como tiempo de proceso puro para las operaciones
   involucradas.
2. El criterio de exclusión multi-máquina/pool es una aproximación de nombre,
   no el criterio validado — probablemente subestima el problema.
3. Dicho esto, la **mecánica del pipeline es válida y reproducible**: el
   cálculo de deltas, el manejo de la inconsistencia de sucursal, el ajuste
   AIC/BIC y el manejo explícito de outliers funcionan correctamente y están
   listos para reejecutarse tal cual sobre datos corregidos por jornada.
   Gamma y Weibull son las candidatas a seguir comparando una vez corregida
   la censura; log-normal no mostró ventaja en ningún caso.
4. **Próximo paso real de Fase 3**: incorporar `turnos_programados` para
   filtrar/corregir censura de jornada, y resolver el criterio oficial de
   multi-máquina/pool (posiblemente extendiendo o reutilizando la
   investigación de `TAREA_MULTIMAQUINA_20260906.md` a todas las plantas)
   antes de recalibrar el motor con estos parámetros.

## Archivos generados

- Reporte completo: `optifierro-backend:/app/docs/FASE3_EXPLORATORIA_20260912.md`
  (y copia en el Mac Studio, ver abajo)
- Resultados por máquina (CSV): `optifierro-backend:/app/fase3_exploratoria_resultados_por_maquina.csv`
- Catálogo de máquinas usado (con flag de pool): `optifierro-backend:/app/fase3_exploratoria_catalogo_maquinas.csv`
- Resumen numérico (JSON): `optifierro-backend:/app/fase3_exploratoria_summary.json`
- Script de análisis (no commiteado): dejado en `/tmp/f3_analisis.py` dentro
  del contenedor `optifierro-backend`, y en `~/f3_analisis.py` en el host TO.

## Tiempo de ejecución

Todo el análisis (carga de 373.934 filas, cálculo de deltas, limpieza,
ajuste de 3 distribuciones × 35 máquinas) corrió en **~1 segundo** dentro del
contenedor. El tiempo total de la tarea, incluyendo exploración de esquema,
instalación de scipy, resolución de problemas de path SSH/Docker en el host
Windows de TO, y redacción de este reporte, fue de aproximadamente
**20-25 minutos**.
