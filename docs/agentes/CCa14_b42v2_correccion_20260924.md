# CCa-14 — B42 v2 FASE 1: CORRECCIÓN del Motor (K0-K7)

**Fecha:** 24-09-2026 · **Rama:** `b42v2-etiqueta` en `/c/Users/OptiFierro/Desktop/optifierro_b42` (TO), base `master 1cd8f88`, continuando sobre 6 commits de CCa-13. **Sin commits** (modo de trabajo de esta sesión): todo el working tree queda sin commitear, listo para que Miaude revise y commitee.
**Especificación:** `B42_v2_spec.md` · **Prompt:** `agentes/prompts/CCa14_b42v2_correccion.md` · **Estado de partida:** K1(a) ya resuelto por un intento previo (working tree con 7 líneas de fix sin commitear) — verificado, no rehecho, extendido.

---

## Resumen ejecutivo (para chat, ≤15 líneas)

- **K0-K1 (determinismo): RESUELTO Y VERIFICADO.** La fuente era `motor_v2.py` ~1084: `candidatas_alt` iteraba un `set` de nombres de máquina sin orden estable → el desempate por carga dependía de `PYTHONHASHSEED`. Fix: `sorted(activas)` + desempate `(carga, nombre)`. Verificado con universo real (3 sucursales, 5 semillas) y con test sintético nuevo (`test_k1_determinismo...`, 315 etiquetas/45 series) que FALLA sin el fix y PASA con él. No se hallaron otras fuentes de no-determinismo (K1b).
- **K2 (reparto por serie): IMPLEMENTADO, TESTEADO, pero NO alcanza AC11.** Umbral 80/100% ahora se evalúa a nivel de serie y el reparto divide en 2 bloques contiguos reales (verificado con test sintético controlado: split limpio, sin pérdidas, 1 sola alerta por serie). Con universo real: Cerrillos 41.9% del viejo (objetivo ≥95%), Calama 74.3%, Coronel 110% (sí cumple). **Causa raíz identificada con evidencia** (sección 3): a escala real (~300-500+ series/turno, muchas de 1 sola etiqueta) el gatillo de reparto near-end-of-shift dispara con altísima frecuencia (524/525 disparos eran series de 1 etiqueta, sin nada que repartir — corregido como ruido); los ~30 splits reales que sí ocurren redirigen carga a una "máquina sugerida" sin que el algoritmo sepa cuánta carga ya le redirigieron OTRAS series en el mismo turno, saturándola y empeorando `operador_solapado`/`turno_lleno` en cadena.
- **K3/K4: NO INTENTADOS.** Regla de parada aplicada: arreglar la causa raíz de K2 exige que `_sugerir_maquina_reparto` tenga conciencia de la carga ya redirigida en el turno — eso es un rediseño más allá "del bloque de reparto". K3 (continuidad ante turno_lleno) heredaría el mismo problema de fondo. Se documenta la opción más simple (sección 5) para que Montu decida.
- **K5 regresión:** `py_compile` limpio (motor_v2.py, test file, programacion.py, database_cubigest.py). 7/7 tests (5 de CCa-13 + 2 nuevos K1/K2) pasan. Conservación universo=tareas+bolsa confirmada en las 3 sucursales. B16/B35/B45: código no tocado (confirmado por diff --stat: solo 2 archivos, motor_v2.py y test file).
- **Cero escrituras en producción** (detalle en sección "Accesos").

---

## 1. Reproducción K0 (E1-E5, universo real de hoy)

Arnés `arnes_v5_repro.py` (Miaude), corrido tal cual contra el working tree (con el fix K1 ya presente). Universo real vía `_obtener_pids_pendientes` (Cubigest SELECT), mismos operadores para ambos motores.

| Sucursal | Universo | kg viejo | kg nuevo (solo K1) | Etiq. viejo | Etiq. nuevo |
|---|---|---|---|---|---|
| Cerrillos | 2000 et. / 562.764 kg | 64.859 | 40.691 | 516 | 324 |
| Calama | 1773 et. / 585.552 kg | 122.964 | 98.709 | 498 | 498 |
| Coronel | 273 et. / 34.360 kg | 3.664 | 4.165 | 126 | 95 |

Nota: los kg del universo real cambian levemente entre corridas (Cubigest es data viva, no una foto congelada) — comparar contra los números de Miaude (15:20-15:40) es solo orientativo; las proporciones y motivos de bolsa son consistentes con E1-E5.

- **E1 (kg agendados caen):** reproducido — el nuevo agenda 63-80% de lo que agenda el viejo, según sucursal.
- **E2 (reparto automático perdido):** reproducido — `tareas_con_reparto_efectivo` cae a 0-3 en el nuevo contra 3-4 en el viejo (motor viejo real, no el escenario sintético de CCa-13 T7). Es la causa que ataca K2.
- **E3 (no determinismo):** reproducido en la corrida inicial (ver K1). Resuelto.
- **E4 (bolsa `turno_lleno` con capacidad ociosa):** reproducido — `bolsa_turno_lleno_de_series_parciales` no-cero en Cerrillos/Calama/Coronel incluso tras K1.
- **E5 (modelo de tiempos Calama):** NO profundizado (K4 no intentado, ver sección 5). El patrón (`kg_por_min` más bajo en el nuevo: Calama 55.1→40.3-32.2) es consistente con lo reportado por Miaude pero no se aisló la causa exacta (cambios de diámetro, piso 5 min, orden de series).

---

## 2. K1 — Determinismo: causa raíz, fix, verificación

**Causa raíz (archivo:línea):** `backend/motor_v2.py:1082-1088` (numeración post-fix; pre-fix era la misma zona, ~1081-1087 en la versión sin el `sorted()` agregado por el intento previo). Dentro de `programar_turno`, cuando la máquina resuelta por `resolver_ruta` no está en `MAQUINAS_ACTIVAS` (fallback):

```python
activas = MAQUINAS_ACTIVAS.get(sucursal_nombre, set())
if activas and nombre_maquina not in activas:
    candidatas_alt = [m for m in activas if ...]          # <- set, sin orden estable
    candidatas_alt.sort(key=lambda m: carga)               # <- sin desempate por nombre
```

`activas` es un `set[str]`; iterar un set de strings en Python tiene orden dependiente del hash de cada string, que Python aleatoriza por proceso salvo `PYTHONHASHSEED` fijo. Cuando dos o más máquinas candidatas tenían la MISMA carga (`sum(1 for t in tareas if t["nombre_maquina"]==m)` — frecuente al principio del turno, con carga 0 para varias), el `.sort()` (estable) preservaba el orden de iteración del set, que cambiaba de proceso a proceso → la máquina elegida (`candidatas_alt[0]`) cambiaba con la semilla, alterando la asignación real (no solo el orden de logueo).

**Fix (ya estaba en el working tree al iniciar esta sesión, verificado y extendido):**
```python
candidatas_alt = [m for m in sorted(activas) if ...]
candidatas_alt.sort(key=lambda m: (carga, m))
```

**K1(a) — verificación con universo real, 3 sucursales, 5 semillas (0,1,2,3,42):** firma SHA1 de `(id_tarea, nombre_maquina, fecha_inicio)` ordenada, sobre el universo congelado del día. Resultado: **firma idéntica en las 5 semillas, en las 3 sucursales**:
```
Cerrillos: sig=c8c1723bd9 (x5)   kg=40691  cajitas=324
Calama:    sig=382165cd92 (x5)  kg=98709  cajitas=498
Coronel:   sig=3ae3536b16 (x5)  kg=4165   cajitas=95
```

**K1(b) — búsqueda de otras fuentes:** `grep -n 'for .* in .*(activas|maquinas_|set(\)' motor_v2.py` + inspección manual de `resolver_ruta`, `_fallback_ad`, `_fallback_ag`, `ajustar_ruta_por_avance`, `_maquinas_elegibles_reparto`, `_sugerir_maquina_reparto`. Todas las demás apariciones de `activas` (líneas 536, 550, 635) son **pruebas de membresía** (`in`), no iteración — orden-independientes. `_maquinas_elegibles_reparto` (línea 752, antes del fix de esta sesión) ya usaba `sorted(activas)`. `_sugerir_maquina_reparto` ordena `con_tasa` por tasa histórica sobre una lista ya determinista (viene de `_maquinas_elegibles_reparto`). El único punto de iteración de un set sin orden que afectaba una decisión era el de línea 1082-1088. **Conclusión: no se hallaron otras fuentes.**

**K1(c) — test de regresión (`backend/test_b42v2_etiquetas.py`, clase `TestB42v2Determinismo`):** universo sintético de 315 etiquetas / 45 series (combinaciones reales IdForma/Diámetro de Cerrillos, muestreadas de `matriz_rutas.json`, con rutas hacia máquinas distintas) x 7 operadores reales x 7 máquinas activas reales. Lanza 5 subprocesos (`PYTHONHASHSEED` 0,1,2,3,42) y compara firmas.
- **Corrido SIN el fix** (HEAD del working tree antes de esta sesión, vía `git show HEAD:...`): **FALLA** — 5 firmas distintas entre semillas (`5 != 1`), kg constante (7904) pero máquina/orden cambia.
- **Corrido CON el fix:** **PASA** (6/6 con el resto de la suite).

**K1_acumulado.patch:** `agentes/diffs/B42v2_r2/K1_acumulado.patch` (151 líneas: 7 en motor_v2.py + el test nuevo... nota: en este punto el patch acumulado solo llevaba el fix de motor_v2.py; el test K1 se agregó en el mismo commit lógico, ver diff --stat de K2_acumulado que ya lo incluye completo).

---

## 3. K2 — Reparto por serie: implementación, test, y por qué NO alcanza AC11

### 3.1 Cambio de diseño
`motor_v2.py`: se agregó `_partir_serie_por_kg()` (función pura, parte una lista de etiquetas en 2 bloques contiguos ~50/50 por kg) y se reestructuró el bloque de asignación dentro de `programar_turno` (dentro del loop `for paso_idx, maquina_str in enumerate(ruta)`):

1. El umbral 80%/100% ahora se evalúa **una vez por paso** con `duracion_total_paso` (la duración de la SERIE completa, ya calculada con `estimar_duracion_min` — D2, sin cambios) contra el tiempo libre en la máquina **al inicio del paso** (antes de programar ninguna etiqueta de la serie ahí) — antes se evaluaba por CADA etiqueta suelta con su fracción de duración (el defecto D5 de CCa-13).
2. Si el nivel es "dura" y desbordaría el turno, y hay ≥2 etiquetas pendientes: `_partir_serie_por_kg` corta la serie en bloque A (prefijo) / bloque B (resto), ~50/50 por kg. Bloque A sigue en la máquina original, bloque B va a la máquina sugerida por `_sugerir_maquina_reparto` (sin cambios en esa función).
3. Se extrajo `_asignar_bloque()` (closure dentro de `programar_turno`) con la lógica de asignación secuencial (cursor, setup por cambio de diámetro, break, solape de operador, tope de jornada) — antes duplicada inline, ahora compartida por el camino sin-reparto (1 bloque = toda la serie) y por cada uno de los 2 bloques del reparto.
4. `alerta_reparto` va SOLO en la primera etiqueta de la serie (éxito o bolsa). `serie_repartida: true` se agrega en las tareas de AMBOS bloques cuando el split ocurre.
5. Ajuste posterior (mismo punto K2, ver 3.3): la alerta/decisión de reparto solo se calcula si hay ≥2 etiquetas pendientes — evita marcar "dura" en series de 1 etiqueta que no tienen nada que repartir.

### 3.2 Test sintético controlado (`TestB42v2K2Reparto`) — PASA
Escenario: serie "filler" (8×1000kg, IdForma=2 Ø10mm→PRIMA 3D) consume ~275 min de PRIMA 3D desde el inicio del turno; serie "target" (12×1000kg, mismo IdForma/diámetro, viaje distinto) queda con <300 min libres, duración de serie completa (~413 min) excede ese remanente. Resultado verificado:
- 12/12 etiquetas conservadas (0 a bolsa) — sin el split, varias caerían a `turno_lleno`.
- Exactamente 2 máquinas usadas (PRIMA 3D + EURA 16, sugerida).
- `serie_repartida: true` en las 12 tareas.
- Exactamente 1 tarea con `alerta_reparto` (la primera, id 9100), nivel "dura".
- Orden preservado dentro de cada bloque (sin intercalar).

Esto confirma que el MECANISMO de split (K2) funciona correctamente tal como está especificado.

### 3.3 AC11 — medición con universo real (3 semillas de universo real del día, `_obtener_pids_pendientes`)

| Sucursal | kg VIEJO | kg NUEVO (K1+K2) | % del viejo | AC11 (≥95%) |
|---|---|---|---|---|
| Cerrillos | 66.504 | 27.859 | 41,9% | **NO** |
| Calama | 122.964 | 91.312 | 74,3% | **NO** |
| Coronel | 3.664 | 4.044 | 110,4% | SÍ |

`tareas_con_reparto_efectivo` (campo del arnés, cuenta tareas con `reparto` no-nulo — heredado del formato viejo de reparto por-etiqueta) da 0 en las 3 sucursales para el NUEVO porque K2 ya no usa el campo `reparto` legado (usa `serie_repartida`); no es indicativo de que no hubo splits.

**Diagnóstico con evidencia (instrumentación temporal, removida antes de guardar el patch final):** se corrió el arnés con un `print` de diagnóstico en el punto de decisión del umbral, contando cada evaluación "dura"/"suave" con `pct_jornada`, máquina, máquina sugerida y `len(pendientes)` en ese momento. Sobre las 3 sucursales combinadas: **525 evaluaciones "dura", de las cuales 524 tenían `len(pendientes) == 1`** (una sola etiqueta pendiente — nada que partir en 2 bloques). Ejemplos reales: `pct=617.38 maq=Carro de Corte sug=Cortadora Manual npend=1`, `pct=165.96 maq=Robomaster 60 sug=Curvadora CER40 1 Schnell npend=1`.

**Causa raíz:** con la granularidad "una serie = (viaje,diámetro,forma,largo,calidad,etapa)" de B42 v2 (D1, CCa-13), el universo real de ~2000 etiquetas se parte en **~300-500+ series por turno**, muchas de 1-2 etiquetas. El umbral `pct_jornada = duracion_serie / minutos_restantes` evaluado cerca del cierre del turno en una máquina ya cargada por series previas produce `pct_jornada` muy por encima de 1.0 casi SIEMPRE (minutos_restantes chico), incluso para series triviales — esto es esperable y correcto como señal de "la máquina está llena", pero al ser series de 1 etiqueta no hay nada que repartir. Se corrigió el ruido cosmético (sección 3.1 punto 5: exigir `len(pendientes)>=2`), lo cual NO cambió los kg (confirmado: misma medición antes/después del ajuste) porque esas series de 1 etiqueta de todas formas no se dividían (ya estaban protegidas por el mismo guard en la rama de split) — solo dejaron de mostrar una alerta "dura" espuria.

De las ~30-35 evaluaciones restantes con `len(pendientes)>=2` (splits reales), la caída de kg proviene de que **`_sugerir_maquina_reparto` no tiene memoria de cuánta carga ya le fue redirigida por OTRAS series en el mismo turno**: distintas series compitiendo por capacidad cercana al fin de turno sugieren repetidamente la MISMA "mejor máquina alternativa" (ej. `EURA 20_2`, `Dobladoras`, `Cortadora Manual` aparecen decenas de veces como `sug=` en la instrumentación), saturándola progresivamente y empujando a `operador_solapado`/`turno_lleno` tanto a esa máquina como, en cadena, a series posteriores. Esto es un efecto emergente de escala (~300+ series compitiendo), no reproducible en el test sintético controlado (que usa una sola serie objetivo).

**No se aplicaron trucos para forzar la métrica** (no se infló duración, no se relajó solape de operador/turno) — instrucción explícita del prompt.

### 3.4 K2_acumulado.patch
`agentes/diffs/B42v2_r2/K2_acumulado.patch` (669 líneas: motor_v2.py 426 líneas de diff / +385 -217 netas contando el test; test_b42v2_etiquetas.py +176 líneas).

---

## 4. K3/K4 — NO intentados (regla de parada)

**K3 (continuidad de serie ante turno_lleno):** explícitamente condicionado en el prompt a "solo si tras K2 E4 persiste" — persiste y empeoró (`bolsa_turno_lleno_de_series_parciales` en Cerrillos: 82 con solo-K1 → 164 con K1+K2). Sin embargo, K3 usa "la misma lógica de K2" para continuar una serie parcial en otra máquina elegible con tiempo libre — heredaría el MISMO problema de fondo de la sección 3.3 (elegir una máquina "elegible con tiempo libre" sin conciencia de cuánta otra carga del turno ya converge ahí). Implementarlo sin resolver eso primero arriesga profundizar el mismo efecto en cadena, con el agravante de que K3 se dispara en MUCHOS más puntos que K2 (cualquier `turno_lleno` parcial, no solo los umbrales 80/100%).

**K4 (modelo de tiempos / orden de series, E5):** no se llegó a esta prioridad. Requeriría aislar, con datos, si la diferencia Calama (`kg_por_min` 55.1→40.3-32.2, cambios de diámetro 19→24-29) viene de: (i) representante-vs-serie-homogénea (ya parcialmente explicado por CCa-13 §T7: 137/413 tareas cambiaron de máquina en Calama por el fix AC6), (ii) el piso de 5 min por serie, o (iii) intercalado de series del mismo (viaje,diámetro) generando más setups. NO se tocó el modelo de tiempos (decisión de Montu, spec §12, sigue vigente sin reabrir).

**Regla de parada aplicada literalmente:** *"Si K2 exige rediseñar más allá del bloque de reparto: PARA y reporta la opción más simple."* — K2 SÍ se implementó dentro del bloque de reparto (sin rediseño), pero su resultado (AC11 no alcanzado) expone que la opción más simple para cerrar la brecha es un rediseño que excede ese bloque.

**Opción más simple para Montu/Miaude (no implementada):** darle a `_sugerir_maquina_reparto` un acumulador de minutos ya comprometidos por reparto en esta corrida (dict `{maquina: minutos_reservados}` poblado por cada split exitoso, consultado antes de sugerir), para que dos series distintas no compitan a ciegas por la misma máquina "mejor". Esto es un cambio acotado (una estructura de estado + un filtro adicional en `_maquinas_elegibles_reparto`), pero toca la firma/contrato de `_sugerir_maquina_reparto` (usada también, sin cambios de comportamiento esperado, sería igual para el reparto manual B2) — de ahí que se considere "más allá del bloque" tal como está delimitado hoy.

---

## 5. K5 — Regresión completa

- **`py_compile` limpio:** `motor_v2.py`, `test_b42v2_etiquetas.py`, `routers/programacion.py`, `database_cubigest.py` — sin errores.
- **Tests:** 7/7 OK (`TestB42v2Series` x5 de CCa-13 sin cambios + `TestB42v2Determinismo` K1 + `TestB42v2K2Reparto` K2).
- **Conservación (universo == tareas + bolsa):** confirmada en las 3 corridas del arnés de esta sesión (K0, AC11 pre-ajuste, AC11 post-ajuste) — `kg_tareas + kg_bolsa ≈ kg_universo` en los 3 casos, 3 sucursales (diferencias de redondeo <0,2%).
- **Tabla VIEJO vs NUEVO final (universo real, con K1+K2+ajuste 3.1.5):** ver tabla de la sección 3.3 (misma corrida es la final).
- **Tiempos de generación (AC8):** NUEVO: Cerrillos 0,69s, Calama 0,87s, Coronel 0,13s — sin degradación catastrófica, consistente con lo medido por CCa-13 (orden de 1-2s en universos más grandes).
- **B16 (`metadata.capacidad`):** código no tocado — confirmado por `git diff --stat` (solo 2 archivos: `motor_v2.py`, `test_b42v2_etiquetas.py`) y por inspección de los rangos de líneas del diff (los hunks tocan 796-820, 1081-1122, 1143-1315 aprox.; el bloque `capacidad_b16`/`saldo_mh` está en 834-843 y 1479-1500, fuera de todos los hunks).
- **B35 (ventana ±15):** `_ventana_turno`/`_resolver_ventana_override` no tocados (fuera del archivo modificado en la zona relevante; función completa a partir de línea 1536+, sin hunks ahí).
- **B45 (FP-LC fuera):** `MAQUINAS_SIN_OPERADOR`, `es_despacho_directo`, filtro en `_obtener_pids_pendientes` — no tocados (mismo archivo `motor_v2.py` pero fuera de los hunks del diff; `routers/programacion.py` sin cambios en esta sesión).

---

## 6. K6 — Higiene del diff

**Archivos tocados (2, ambos backend):**
- `backend/motor_v2.py`: +385/-217 líneas netas.
  - Helper nuevo: `_partir_serie_por_kg()` (K2).
  - `programar_turno()`: fix de determinismo en el bloque de fallback de máquina (K1, ~7 líneas), y reestructuración del bloque de asignación/reparto dentro del loop de paso (K2: nuevo cálculo de umbral a nivel de serie + `_asignar_bloque()` closure + orquestación de split en 2 bloques).
  - Ninguna otra función tocada.
- `backend/test_b42v2_etiquetas.py`: +176 líneas (archivo ya versionado por CCa-13, sin archivos nuevos creados).
  - `TestB42v2K2Reparto` (1 test).
  - `TestB42v2Determinismo` (1 test, con helper `_universo_sintetico`).
  - Las 5 clases/tests de CCa-13 sin modificar.

**Sin refactors no pedidos:** no se tocó nada fuera de `programar_turno`/`_sugerir_maquina_reparto` (zona ya señalada como territorio del commit `48d946c` de CCa-13); no se reordenó ni renombró código existente salvo lo estrictamente necesario para extraer `_asignar_bloque`.

**`K_final.patch`** (= `git diff HEAD` al terminar) = idéntico a `K2_acumulado.patch` (669 líneas) — no hubo cambios de K3/K4/otros después de K2.

---

## 7. Riesgos abiertos y lo NO verificado

1. **AC11 no alcanzado en Cerrillos (41,9%) y Calama (74,3%).** Causa raíz documentada (sección 3.3). Requiere decisión de Montu: (a) aceptar el reparto por serie tal como está (mejor UX de "una cajita = una etiqueta" y splits correctos cuando ocurren, pero con menos kg total agendado que el viejo), o (b) invertir en el rediseño de `_sugerir_maquina_reparto` con conciencia de carga acumulada (sección 4) antes de ir a producción.
2. **E2/D5 (CCa-13) parcialmente mitigado, no resuelto:** K2 corrige el mecanismo de reparto (ahora es real, a nivel de serie, con 2 bloques), pero el volumen total de kg agendado sigue por debajo del viejo. El riesgo #1 de CCa-13 ("D5: el auto-reparto agenda MENOS kg totales") sigue vigente, con una causa más precisa ahora.
3. **E4 (turno_lleno con capacidad ociosa) empeoró numéricamente** tras K2 (bolsa_turno_lleno_de_series_parciales Cerrillos: 82→164) — ver sección 4, K3 no intentado.
4. **E5 (modelo de tiempos Calama) no verificado** — K4 no intentado.
5. **Instrumentación de diagnóstico:** se usó un archivo temporal con `print` de depuración (`motor_v2_k2_debug.py`) SOLO en `/tmp` del contenedor, nunca escrito al worktree ni al patch final — confirmado por `git diff --stat` (2 archivos, sin líneas de debug).
6. **No verificado en esta sesión** (fuera de alcance, ya señalado por CCa-13): drag&drop real, render visual del frontend (esta sesión no tocó frontend), B16 end-to-end con Geovictoria real, comportamiento de `/aplicar-reparto` (B2) con las tareas nuevas de K2 (el campo `reparto` legado ya no se usa desde K2; `serie_repartida` es nuevo y B2/`/aplicar-reparto` no fue revisado para ver si necesita leerlo).

---

## 8. Accesos y confirmación de cero escrituras

**Ventana:** 24-09-2026, 18:24 (K0, verificación SSH+git log) a 19:05 aprox (cierre de informe), sesión continua en primer plano, sin subagentes ni tareas en segundo plano.

**Comandos ejecutados en TO** (`ssh TO "..."`, alias ya configurado, VPN activa según lo indicado en el prompt):
- `git -C .../optifierro_b42 log --oneline -3 && git branch --show-current` (verificación inicial, K0).
- `git -C .../optifierro_b42 status --short` / `diff HEAD --stat` / `diff HEAD` (múltiples veces, lectura del estado del working tree).
- `cat` de `motor_v2.py`/`test_b42v2_etiquetas.py` hacia el Mac (para editar localmente y recalcular diffs) y de vuelta hacia TO (`cat > archivo`) para aplicar los cambios — siempre sobre el worktree `optifierro_b42`, nunca sobre `/c/Users/OptiFierro/Desktop/optifierro` (checkout principal/master) ni sobre `~/graphify-workspace/optifierro` (espejo local, que el prompt marca explícitamente como IRRELEVANTE para este trabajo y no se tocó).
- `docker exec optifierro-backend ...` (7+ veces) — copias vía `cat >` de archivos hacia `/tmp` del contenedor (nunca `/app`), ejecución de `python3 -m unittest`/scripts de arnés con `MOTOR_BASE_DIR=/app` (config estática real, solo lectura) y `OPENSSL_CONF=/app/openssl_legacy.cnf` (driver ODBC).
- `docker exec optifierro-backend rm -rf /tmp/mv /tmp/run_fix ...` — limpieza de temporales, ejecutada al finalizar cada bloque de pruebas.
- `python3 -m py_compile` (local, sobre copias en `/tmp` del Mac, y remoto dentro del contenedor).

**Accesos a Cubigest (SQL Server 192.168.1.195), siempre vía `_obtener_pids_pendientes`/`_obtener_operadores_disponibles` dentro del contenedor `optifierro-backend` (nunca directo desde el Mac):**
- `_obtener_pids_pendientes(sucursal, "2026-09-24")` — ejecutado ~6 veces (K0, AC11 antes y después del ajuste 3.1.5, dump de determinismo) x 3 sucursales — mismo SELECT que usa producción hoy, sin `TOP` explícito, sin cambios de lógica.
- Ningún `INSERT`/`UPDATE`/`DELETE`/`DDL` contra Cubigest.

**Confirmación explícita: CERO ESCRITURAS EN PRODUCCIÓN.**
- Ningún `POST /api/programacion/generar` ni otro POST/PUT/DELETE contra la API — todas las corridas fueron funciones Python invocadas directamente dentro del contenedor (arnés), no HTTP.
- Ningún `docker compose build/up/restart` ni `docker restart` — solo `docker exec` (lectura/ejecución de scripts) y escritura de archivos en `/tmp` del contenedor, jamás en `/app`.
- `optifierro_v2.db` real: solo lectura (`SELECT sucursal_id, maquina_id, maquina FROM maquinas_info`, patrón ya usado por CCa-13) para reconstruir el mapa de máquinas dentro del arnés — nunca escrita.
- Ningún `git commit`/`add`/`stash`/`checkout`/`reset`/`rebase` — todo el trabajo quedó en el working tree de `b42v2-etiqueta`, sin commitear, tal como exige el modo de trabajo de esta sesión.
- Ningún `git push`.
- El checkout principal de TO y el espejo `~/graphify-workspace/optifierro` no fueron modificados.

**Log de sesión:** este informe reemplaza el log detallado; no se generó un archivo `.log` aparte (la sesión fue interactiva por herramientas, no por shell transcript) — si Miaude requiere el log crudo, los comandos de esta sección son el resumen completo y fiel de lo ejecutado.

**Patches (en orden, todos en `agentes/diffs/B42v2_r2/`):**
- `K1_acumulado.patch` (fix determinismo, 151 líneas).
- `K2_acumulado.patch` = `K_final.patch` (K1 + K2 + ajuste de ruido de alerta, 669 líneas, 2 archivos).
