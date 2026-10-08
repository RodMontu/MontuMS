# B26-A — Criterios adoptados en "Producción por Máquina" (SPP)

**Fecha:** 2026-09-23 · **Decidido por:** Montu (con Mi TI) · **Estado:** implementada y verificada en arnés pre-deploy (versión A, entrega 24-09); falta commit (Coordinadora) y deploy
**Uso previsto:** registro de criterios para los manuales de entrega del SPP. Las secciones 1 a 5 están redactadas para poder pasar al manual casi tal cual. Las secciones 6 a 8 son técnicas (trazabilidad).
**Mapa general de decisiones del SPP:** `MAPA_DECISIONES_SPP.md` (este documento detalla la sección 1 del mapa).
**Relacionado:** `B26_B_pendiente_metodo_validado.md` (versión definitiva, pendiente), `agentes/prompts/V3_b26_produccion_maquina.md` (encargo), `agentes/CCa3_b26_implementacion_20260923.md` (implementación).

## 1. Qué muestra la pantalla
Para una forma y un diámetro (y opcionalmente un largo de pieza), la pantalla lista las máquinas que históricamente procesaron esa combinación y estima cuántas **toneladas por hora** produce cada una. Filtros: ID de forma, diámetro, sucursal, período (meses de historial) y largo aproximado de la pieza.

## 2. Cómo se calcula (en lenguaje simple)
- Se toma el historial de producción de Cubigest (solo lectura) y se ordena por máquina y sucursal.
- Cada par de registros consecutivos de una misma máquina forma un **intervalo**. Solo cuentan los intervalos de **2 a 480 minutos** (menos de 2 es ruido dentro del mismo lote; más de 480 es una pausa entre turnos o días).
- La producción de un intervalo es el **peso de la etiqueta** (kg del paquete) dividido por la duración del intervalo.
- Se descartan intervalos con más de **50 ton/hora** (físicamente imposibles para estas máquinas; casi siempre son errores de registro).
- El valor que se muestra es la **mediana** de esos intervalos, junto con el **rango típico P25–P75**: la mitad central de lo que históricamente ocurrió en esa máquina. Ejemplo de lectura: "0,53 ton/hora, rango típico 0,12 – 1,64" significa que la producción típica es 0,53, pero es normal ver desde 0,12 hasta 1,64.

**Por qué rango P25–P75 y no "confianza XX %":** al revisar las 32 máquinas ninguna distribución de tiempos pasó las pruebas estadísticas de ajuste (los datos son bimodales de verdad: trabajos cortos y largos mezclados). Un porcentaje de confianza sería falso. El rango empírico es honesto y se calcula solo con lo observado.

## 3. Filtro por largo de pieza
- El largo se convierte a **kg por barra** con la fórmula de barra corrugada `diámetro² / 162 × largo (m)`.
- El historial de cada máquina se agrupa por kg por barra (en 5 grupos si hay 50 datos o más, en 3 si hay 30 o más, y sin agrupar si hay menos: en ese caso se avisa "Sin ajuste por largo (pocos datos)"). Se muestra el grupo que corresponde al largo pedido.
- Comprobado con datos reales: el kg por barra calculado desde Cubigest coincide con la fórmula (razón mediana 1,00 en 8 combinaciones de las 3 plantas).

## 4. Avisos que puede mostrar cada fila
| Aviso | Cuándo aparece | Qué significa |
|---|---|---|
| **Datos insuficientes (N < 15)** | La máquina tiene menos de 15 intervalos válidos | Se lista la máquina con su N, pero no se entrega ton/hora (con tan pocos datos el número engaña) |
| **Fuera del rango histórico de esta máquina (x–y kg/barra, tolerancia ±10 %)** | El kg por barra pedido queda bajo el percentil 5 o sobre el percentil 95 de lo que esa máquina ha procesado, con una tolerancia de ±10 % | Nunca ha trabajado piezas de ese peso; el ton/hora mostrado es el del grupo más cercano y debe tomarse con cautela |
| **Rango no evaluable en esta máquina** | Líneas de corte y similares | En estas máquinas el campo "piezas por paquete" no representa barras, así que no se puede comparar el peso por barra; se muestra el ton/hora del historial completo |
| **Sin ajuste por largo (pocos datos)** | Se pidió largo pero hay menos de 30 datos | No alcanzan datos para agrupar por largo; se muestra el historial completo |

## 5. Lo que la pantalla NO es (aclaraciones para el manual)
- **No es un intervalo de confianza ni una predicción garantizada:** es una referencia basada en el historial.
- **No es el ruteo del Planificador:** las máquinas listadas son las que históricamente procesaron esa forma y diámetro; el Planificador calcula sus rutas por su cuenta.
- **No está validada a nivel de operario y pedido:** el método definitivo (operario + máquina + pedido, con descuento de colación) está pendiente (B26-B). Los valores actuales son coherentes con el historial, pero pueden diferir de los del método validado.

## 6. Parámetros vigentes (trazabilidad; todos aprobados por Montu el 23-09-2026)
| Parámetro | Valor | Justificación con datos |
|---|---|---|
| Intervalo válido | 2 a 480 min | Criterio histórico del endpoint (ruido intra-lote / pausas entre turnos) |
| Tope de ton/hora por intervalo | 50 | Criterio FASE3 (`ton_hora > 50` = outlier de duración cercana a 0). Foto ANTES: Cortadora Manual Coronel mostraba 91,8 ton/h con N=5 |
| N mínimo para mostrar ton/hora | 15 | Con N pequeño el P25–P75 no es representativo; el umbral de FASE3 fue n ≥ 30 (aquí se acepta 15 por ser una pantalla referencial) |
| Umbral "fuera de rango" | Bajo P5 × 0,9 o sobre P95 × 1,1 del kg/barra histórico de la máquina (margen de tolerancia 10 %, agregado el 23-09) | Rango observado real, p. ej. EURA 20_3 Cerrillos Ø16: 2,5 a 19,1 kg/barra; un largo de 12 m (19,0 kg) queda en el borde; sin margen, EURA 20_1 lo marcaba fuera de rango por 0,06 kg, por eso se agregó la tolerancia (con margen: 12 m "ok", 14 m y 30 m "fuera de rango") |
| Máquina "no evaluable" | Percentil 90 de (kg/barra medido ÷ kg/barra teórico) > 1,5 | En máquinas normales la razón está entre 0,98 y 1,05; en las combinaciones que incluyen líneas de corte, el P90 de toda la combinación sube a 79–325 |
| Grupos por largo | 5 si N ≥ 50; 3 si N ≥ 30; 1 si no | Garantiza al menos ~10 observaciones por grupo para calcular P25–P75 |

## 7. Correcciones de origen incorporadas (RCA 23-09)
1. **Peso por etiqueta:** el endpoint usaba `piezas.TotalKgs` (peso TOTAL de la línea de pieza, de 1 a 23.000 kg) como peso de cada registro. Se reemplaza por `detallePaquetesPieza.KgsPaquete` (peso de la etiqueta). Efecto: el ton/hora de líneas de corte baja 3 a 8 veces (Línea de Corte Cerrillos, forma 1 Ø16: 7,75 → 1,04; Carro de Corte Calama: 3,52 → 0,82); en el resto casi no cambia.
2. **Mezcla de métodos (Bug 2):** se eliminan las columnas Mín/Mediana/Máx (deltas crudos con filtro laxo, valores sin sentido como mín 2,2 o máx 442 min) y los escenarios con ayudantes (ratios fijos sin respaldo).
3. **Indicador fuera de rango (Bug 1):** antes el filtro por largo comparaba el peso de una barra (5 a 36 kg) contra el peso total de la línea (hasta 23.000 kg) y elegía casi siempre el grupo más liviano sin avisar.
4. **Copy:** se reemplaza "sin intervalo estadístico riguroso" por la frase acordada (ver sección 8).

## 8. Textos vigentes en pantalla
- Título interno: **"Tiempos por Máquina (estimado)"**. Menú lateral: **"Producción por Máquina"**. Subtítulo de la tabla: **"Producción por máquina — Forma X · Ø Y mm"** (unificado con el menú el 23-09).
- Nota metodológica: "Producciones estimadas en base a antecedentes históricos de producción; rango típico según el historial (P25-P75). Es una estimación referencial: no es un intervalo de confianza ni está validada a nivel de operario y pedido."
- Nota de rutas: "Las máquinas listadas son las que procesaron esta forma y diámetro según el historial; no corresponden al ruteo que calcula el Planificador."

## 9. Pendiente y decisiones abiertas
- **B26-B** (método validado FASE3): ver `B26_B_pendiente_metodo_validado.md`.
- Subtítulo de la tabla unificado con el menú (resuelto 23-09, aprobado por Montu).
- Confirmar la semántica de `NroPiezas` en líneas de corte antes de usar kg/barra allí.
- **Ejemplo verificado en arnés (pre-deploy):** EURA 20_3 Cerrillos, forma 1 Ø16, sin largo: mediana 0,53 ton/hora, rango típico 0,12 – 1,64, N = 1.727. Repetir con el sistema desplegado antes de fijarlo en el manual.
- **Margen de tolerancia (resuelto 23-09, aprobado por Montu):** ±10 % sobre P5/P95. Antes, 12 m en Ø16 (19,0 kg/barra) quedaba en el borde del P95 (EURA 20_1: 18,9) y se marcaba fuera de rango por 0,06 kg. Verificado con el sistema real: 12 m = "ok"; 14 m y 30 m = "fuera de rango".
