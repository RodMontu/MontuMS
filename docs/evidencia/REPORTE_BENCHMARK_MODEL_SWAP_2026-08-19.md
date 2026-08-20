# Reporte Benchmark Model-Swap — Qwen3-Coder-30B-A3B vs Devstral-Small-2-24B

Cierra BACKLOG-MODEL-SWAP-BENCH. Sesión iniciada 2026-08-19 (noche), continuada y
cerrada 2026-08-20 tras un fallo de ejecución en el intento anterior (ver sección
"Hallazgo: fallo de la sesión anterior" más abajo).

## Objetivo

Evaluar dos modelos candidatos para reemplazar (o no) al modelo actual de
Carlitos en producción (`qwen3-coder-next-80b-a3b-Q4_K_M`, llama-server
`:11500`), usando el mismo benchmark metodológico del 2026-08-18 (15 tareas
reales de solo lectura sobre OptiFierro-V2), con la política fovea-selectivo
por tarea ya vigente (ver `EVALUACION_HARNESS_AGENTICOS_CARLITOS_2026-08.md`).

Candidatos:
1. **Qwen3-Coder-30B-A3B-Instruct** (MoE, 30B total / ~3.3B activos), GGUF
   Q4_K_M, repo `unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF`.
2. **Devstral-Small-2-24B-Instruct-2512** (denso, 24B activos en cada token),
   GGUF Q4_K_M, repo `unsloth/Devstral-Small-2-24B-Instruct-2512-GGUF`.

Servidores de prueba en puertos nuevos (11501 / 11502), nunca simultáneos,
producción (`:11500`) nunca tocada. Providers `llama-test-1` / `llama-test-2`
agregados como entradas nuevas en `~/.pi/agent/models.json` (backup previo en
`/tmp/models.json.pre-benchmark-2026-08-19.bak`; entrada `llama-local` de
producción verificada intacta antes, durante y después de todo el proceso).

## Hallazgo: fallo de la sesión anterior (2026-08-19 noche)

La primera ejecución de esta tarea murió sin completar nada más allá de la
descarga del candidato 1. Causa raíz: el agente ejecutor (CCa) backgroundeó
la descarga con `&` y terminó su turno escribiendo que "esperaría a que una
tarea de monitoreo en background le avisara cuando terminara" — ese mecanismo
no existe en una invocación `pi -p` de un solo turno síncrono (modo headless,
sin sesión persistente). Al no bloquear activamente sobre el proceso backgroundeado,
el turno simplemente terminó y ninguna acción posterior (registro de provider,
levantar servidor, smoke test, benchmark) se ejecutó. No fue un fallo del
comando de descarga en sí — el archivo del candidato 1 quedó completo e íntegro
(confirmado en esta sesión con `hf download` idempotente, sin re-descarga).

Corrección aplicada en esta sesión: todo comando de larga duración (descargas,
carga de modelo en llama-server, benchmark de 15 tareas) se ejecutó en
background pero con un loop de espera síncrono y real (`while kill -0 $PID; do
sleep N; done`) dentro de la misma invocación de herramienta, repitiendo el
bloqueo en llamadas sucesivas cuando la duración excedía el límite de una sola
invocación. Ninguna acción posterior se disparó sin confirmación real de que
la anterior había terminado.

Nota adicional: el comando de descarga documentado en el prompt original usaba
`huggingface-cli download`, binario que ya no existe en la instalación actual
de `huggingface_hub` (fue renombrado a `hf`). Se usó `hf download` con la
misma semántica (idempotente, no re-descarga si el archivo local ya está
completo y verificado contra el hash remoto).

## Verificación de integridad de descargas

- Candidato 1: `Qwen3-Coder-30B-A3B-Instruct-Q4_K_M.gguf` — 18,556,689,568
  bytes (~18.56 GB). Verificado con `hf download` repetido sobre el mismo
  destino (idempotente): confirmó archivo completo sin re-descargar.
- Candidato 2: `Devstral-Small-2-24B-Instruct-2512-Q4_K_M.gguf` —
  14,334,446,752 bytes (~14.33 GB), dentro del ±5% del tamaño esperado
  (~14.3 GB).

## Smoke test de tool-calling

Ambos candidatos pasaron al primer intento (sin necesidad del segundo
reintento permitido), respondiendo la lista exacta de 8 tools disponibles
(`read`, `bash`, `edit`, `write`, `fovea_sketch`, `fovea_focus`,
`fovea_dwell`, `fovea_impact`) sin texto adicional.

## Resultados — Candidato 1: Qwen3-Coder-30B-A3B-Instruct (puerto 11501, sin `--jinja`)

| Tarea | Condición | Resultado | Tiempo(seg) | Tokens |
|---|---|---|---|---|
| 1 | FOVEA_EXCLUIDA | OK | 86 | in=19080,out=2069,cacheRead=35245,total=56394 |
| 2 | FOVEA_EXCLUIDA | OK | 30 | in=7448,out=988,cacheRead=20553,total=28989 |
| 3 | FOVEA_EXCLUIDA | OK | 24 | in=4830,out=984,cacheRead=4658,total=10472 |
| 4 | FOVEA_EXCLUIDA | OK | 115 | in=27839,out=1152,cacheRead=135608,total=164599 |
| 5 | FOVEA_DISPONIBLE | OK | 33 | in=11559,out=670,cacheRead=10175,total=22404 |
| 6 | FOVEA_EXCLUIDA | OK | 73 | in=14868,out=1868,cacheRead=20038,total=36774 |
| 7 | FOVEA_EXCLUIDA | OK | 51 | in=14878,out=831,cacheRead=20075,total=35784 |
| 8 | FOVEA_DISPONIBLE | OK | 319 | in=52198,out=1566,cacheRead=506476,total=560240 |
| 9 | FOVEA_EXCLUIDA | OK | 24 | in=6981,out=820,cacheRead=2369,total=10170 |
| 10 | FOVEA_EXCLUIDA | OK | 55 | in=14878,out=1069,cacheRead=20055,total=36002 |
| 11 | FOVEA_EXCLUIDA | OK | 16 | in=2952,out=747,cacheRead=4692,total=8391 |
| 12 | FOVEA_EXCLUIDA | OK | 21 | in=1791,out=1222,cacheRead=4698,total=7711 |
| 13 | FOVEA_DISPONIBLE | OK | 112 | in=27783,out=1404,cacheRead=164714,total=193901 |
| 14 | FOVEA_DISPONIBLE | OK | 27 | in=6286,out=834,cacheRead=30594,total=37714 |
| 15 | FOVEA_EXCLUIDA | OK | 34 | in=5944,out=1285,cacheRead=24983,total=32212 |

**Resumen candidato 1:** 15/15 OK, 0 timeouts, 0 errores. Tiempo total: 1020s.
Promedio por tarea: 68.0s. Tokens de salida totales: 17,509 (throughput de
salida ≈ 17.2 tok/s agregado sobre el tiempo total de pared).

## Resultados — Candidato 2: Devstral-Small-2-24B-Instruct-2512 (puerto 11502, con `--jinja`)

| Tarea | Condición | Resultado | Tiempo(seg) | Tokens |
|---|---|---|---|---|
| 1 | FOVEA_EXCLUIDA | OK | 197 | in=15667,out=1972,cacheRead=2117,total=19756 |
| 2 | FOVEA_EXCLUIDA | OK | 64 | in=7520,out=424,cacheRead=11801,total=19745 |
| 3 | FOVEA_EXCLUIDA | OK | 66 | in=5047,out=761,cacheRead=4093,total=9901 |
| 4 | FOVEA_EXCLUIDA | OK | 61 | in=3388,out=840,cacheRead=13818,total=18046 |
| 5 | FOVEA_DISPONIBLE | OK | 85 | in=11465,out=425,cacheRead=3370,total=15260 |
| 6 | FOVEA_EXCLUIDA | OK | 184 | in=13597,out=1913,cacheRead=4091,total=19601 |
| 7 | FOVEA_EXCLUIDA | OK | 166 | in=13607,out=1591,cacheRead=4101,total=19299 |
| 8 | FOVEA_DISPONIBLE | OK | 53 | in=5590,out=393,cacheRead=15437,total=21420 |
| 9 | FOVEA_EXCLUIDA | OK | 70 | in=4926,out=849,cacheRead=4104,total=9879 |
| 10 | FOVEA_EXCLUIDA | OK | 106 | in=13604,out=491,cacheRead=4098,total=18193 |
| 11 | FOVEA_EXCLUIDA | OK | 52 | in=3132,out=693,cacheRead=4098,total=7923 |
| 12 | FOVEA_EXCLUIDA | OK | 54 | in=1855,out=884,cacheRead=4110,total=6849 |
| 13 | FOVEA_DISPONIBLE | OK | 304 | in=20789,out=2880,cacheRead=406655,total=430324 |
| 14 | FOVEA_DISPONIBLE | OK | 78 | in=6555,out=773,cacheRead=38023,total=45351 |
| 15 | FOVEA_EXCLUIDA | OK | 64 | in=5115,out=691,cacheRead=8470,total=14276 |

**Resumen candidato 2:** 15/15 OK, 0 timeouts, 0 errores. Tiempo total: 1604s.
Promedio por tarea: 106.9s. Tokens de salida totales: 15,580 (throughput de
salida ≈ 9.7 tok/s agregado sobre el tiempo total de pared).

## Comparación directa

| Métrica | Candidato 1 (Qwen3-Coder-30B-A3B, MoE) | Candidato 2 (Devstral-Small-2-24B, denso) |
|---|---|---|
| Tareas OK | 15/15 | 15/15 |
| Tiempo total (15 tareas) | 1020s (17.0 min) | 1604s (26.7 min) |
| Promedio por tarea | 68.0s | 106.9s |
| Tokens salida totales | 17,509 | 15,580 |
| Throughput salida agregado | ~17.2 tok/s | ~9.7 tok/s |
| Tool-calling smoke test | OK, 1er intento | OK, 1er intento |
| Flags especiales requeridos | ninguno | `--jinja` (obligatorio) |

**Confirmación de la hipótesis planteada en el prompt de la tarea:** Devstral
(denso, 24B activos por token) es efectivamente más lento por tarea que el
MoE Qwen3-Coder-30B-A3B (~3.3B activos por token) — 57% más lento en tiempo
total de pared y ~1.8x más lento en throughput de tokens de salida, pese a
tener menos parámetros totales (24B vs 30B). Confirma con datos la expectativa
de que "más chico en total" no implica "más rápido" cuando el modelo es denso
vs MoE.

Ambos candidatos son funcionalmente correctos en el smoke test y en las 15
tareas del benchmark (sin timeouts ni errores), por lo que la elección entre
ellos (o mantener el modelo actual de producción) es una decisión de
velocidad/calidad, no de viabilidad — no se evaluó calidad de las respuestas
en detalle en esta pasada (queda fuera de alcance de este benchmark, que mide
completitud y performance, no corrección semántica de las explicaciones
generadas).

## Supuestos documentados

- Se reutilizó el script de benchmark y el archivo de tareas ya preparados en
  el intento anterior (`/tmp/run_model_benchmark.sh`, `/tmp/benchmark_tasks.tsv`),
  ambos ya alineados a la política fovea-selectivo por tarea (columna
  `single`/`multi` por tarea, no las dos condiciones corridas para cada una
  como en el benchmark original del 18-08). No se reconstruyó desde cero
  porque ya existía y coincidía con la metodología pedida.
- No se comparó contra el modelo de producción en esta misma pasada (ya existe
  la referencia de línea base del reporte 2026-08-18); este benchmark es
  candidato-vs-candidato, no candidato-vs-producción directo con las mismas
  tareas en la misma sesión.
