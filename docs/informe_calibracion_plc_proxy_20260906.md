# Informe de calibración PLC vs. proxy — Fase 1, MT-04 (borrador)

**Fecha:** 2026-09-06
**Autor:** CCa (con datos ejecutados directamente por CCa — ver nota de desviación en
`bitacora_accesos_torres_ocaranza.md`, entrada 2026-09-06 "Fase 1 Tarea 2, pasos a-d")
**Universo:** `ProduccionesPLC`, piloto Cerrillos, Feb-2025 a Mar-2026, filas con
`PLC_FechaInicio` y `PLC_FechaFin` ambas no nulas (4.180 de 11.946 filas totales — 65%
del piloto tiene tiempos incompletos, ver entrada de bitácora previa).

## 1. Qué se comparó

- **Duración real:** `PLC_FechaFin - PLC_FechaInicio` (tiempo real de máquina, medido por PLC).
- **Proxy:** delta de tiempo entre el registro de `PIEZA_PRODUCCION` de una pieza y el
  registro inmediatamente anterior de la **misma máquina** (el proxy que usa hoy el motor
  de tiempos para el resto de las máquinas sin PLC).
- **Diferencia analizada:** `proxy_delta_min - duracion_real_min`, por máquina.

4.179 registros cruzados (99,98% del universo con tiempos completos), 4.172 con diferencia
calculable (requiere un registro anterior de la misma máquina).

## 2. Resultado agregado

| Métrica | Valor (min) |
|---|---|
| Mediana | 6.66 |
| Media | 735.08 |
| Percentil 80 | 77.40 |

**La media es ~110x la mediana — señal clara de outliers pesados, no de sesgo sistemático
moderado.** Esto es consistente con lo anticipado en la Tarea 3 del lote: el circuito PLC
de Cerrillos fue un piloto corto con errores conocidos, y el proxy de "delta con registro
anterior" no distingue entre una pieza que sigue inmediatamente a la anterior en el mismo
turno y una que sigue después de un corte de turno, fin de semana, o parada de máquina —
en esos casos el proxy captura horas o días de inactividad, no tiempo de proceso.

## 3. Resultado por máquina

| Máquina (código) | n | Mediana (min) | P80 (min) |
|---|---|---|---|
| 17 | 2.543 | 6.82 | 53.36 |
| 16 | 964 | 6.26 | 92.43 |
| 25 | 290 | 6.13 | 444.65 |
| 26 | 220 | 14.35 | 413.62 |
| 21 | 95 | 0.11 | 253.66 |
| 23 | 33 | 56.83 | 3073.42 |
| 24 | 27 | -0.43 | 1061.86 |

Lectura:
- Las dos máquinas con más volumen (17 y 16, ~84% de los casos) tienen medianas bajas y
  consistentes (6-7 min) y P80 razonables (53-92 min) — el proxy parece razonablemente
  utilizable ahí como orden de magnitud, con cola de outliers esperable.
- Máquinas 25, 26, 23, 24 tienen muestra chica (27-290 casos) y P80 muy inflados
  (400-3000+ min) — no hay evidencia suficiente para calibrar esas máquinas de forma
  confiable con este piloto; el ruido de instrumentación/turnos domina la muestra.
- Máquina 21 tiene mediana casi cero (0.11 min) y máquina 24 mediana negativa (-0.43 min) —
  compatibles con registros de piezas casi simultáneas en la misma máquina (probablemente
  piezas del mismo paquete/lote registradas juntas), no con tiempo de ciclo real.

## 4. ¿Sesgo sistemático o ruido?

**Conclusión preliminar: predominantemente ruido de instrumentación del piloto, no un sesgo
sistemático corregible con un factor único.** La brecha extrema entre mediana y media/P80,
y la variabilidad enorme entre máquinas con muestra chica, apuntan a que la fuente principal
de error es estructural al proxy (no distingue turnos/paradas), no un desfase constante que
se pueda corregir con una constante de calibración global o por máquina.

Esto no descarta que exista *algo* de sesgo sistemático dentro de la porción "limpia" de la
distribución (mediana ~6-7 min en las dos máquinas de mayor volumen) — pero separar esa señal
del ruido de turno requeriría filtrar por proximidad temporal razonable (ej. excluir deltas
> N horas como "no es el mismo ciclo productivo"), lo cual es un análisis adicional, no
incluido en este borrador para no exceder el alcance de Tarea 2/3.

## 5. Recomendación preliminar (de las 4 opciones abiertas, `handoff_actual.md` Fase 1)

1. Instrumentar más máquinas con PLC.
2. Cambiar el flujo para pistolada de inicio Y término.
3. Aceptar el proxy si el objetivo es solo priorizar, no cronometrar.
4. Documentar el límite y no tocar nada.

**Recomendación: Opción 3, con matiz.** Para las dos máquinas de mayor volumen (17 y 16,
84% del piloto), el proxy da un orden de magnitud razonable (mediana de minutos, no horas)
y es utilizable para **priorización** (ordenar/comparar máquinas), tal como está planteado
el uso actual del motor de tiempos. **No es confiable para cronometrar** ni para
comprometer SLAs, dado el P80 alto y la cola de outliers.

Para el resto de las máquinas (25, 26, 23, 24 en este piloto, y por extensión cualquier
máquina fuera de Cerrillos sin PLC), la muestra es insuficiente para calibrar — aplica
**Opción 4** (documentar el límite) hasta que exista más volumen o, si el objetivo lo
justifica, **Opción 1** (instrumentar selectivamente las máquinas de mayor carga).

No se recomienda Opción 2 (cambiar el flujo operativo de captura) como primer paso — es la
opción de mayor costo/fricción operacional y el problema principal detectado (contaminación
por huecos de turno en el proxy, no falta de una segunda pistolada) se puede mitigar con un
filtro de proximidad temporal en el cálculo, más barato que cambiar el flujo en planta.

## 6. Limitaciones de este borrador

- No se filtraron outliers por proximidad temporal (ej. excluir deltas > X horas) — el plan
  maestro (Fase 3) ya prevé caracterizar la forma de la distribución y usar mediana/P80 como
  métricas centrales; este informe usa esas mismas métricas pero sobre el delta crudo.
- Las 4 opciones citadas se tomaron de `handoff_actual.md` sección "FASE 1"; no se localizó
  un documento con el título exacto "plan maestro sección 3.1" mencionado en
  `TAREA_LOTE_CCA_20260906.md` — si existe en otra ubicación, revisar antes de cerrar MT-04
  formalmente.
- Es un borrador para decisión de Montu, no una recomendación final — falta su criterio de
  negocio sobre qué tan crítico es cronometrar (vs. solo priorizar) para el motor de tiempos.
