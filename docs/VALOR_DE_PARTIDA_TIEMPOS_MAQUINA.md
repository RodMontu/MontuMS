# Valor de Partida — Tiempos por Máquina (Motor de Tiempos OptiFierro)

**Generado:** 14-09-2026, 06:08 hrs — bajo presión de tiempo (lunes 08:00).
**Método:** mediana de tiempo real por (operario + máquina + pedido), turno
real (`pie_Turno`) con descuento de break (Día 13-14h / Noche 01-02h), saltos
entre turnos/días excluidos (>15h). Excluye máquinas 111 y 415 (EURA 20_2,
sospecha de "pistoleo" no confiable — ver handoff sección 34).

**Qué es esto:** un punto de partida razonable, NO un intervalo estadístico
riguroso. Cada corrida de esta semana (censura de jornada, bondad de ajuste,
segmentación por forma, por tamaño de pedido) confirmó que el dato de origen
no permite un intervalo de confianza angosto y confiable — ver
`handoff_actual.md` secciones 18-33 y los informes `FASE3_*.md` para el
detalle completo de por qué. Este documento es el resultado práctico de esa
semana de trabajo: la mejor mediana defendible que tenemos hoy, para arrancar
el motor, con la intención declarada (Montu) de que el sistema aprenda y se
recalibre con el tiempo.

## Tabla principal — mediana por máquina (minutos)

| Máquina | Planta | Mediana (min) | n | Confianza |
|---|---|---|---|---|
| Cortadora Manual | Calama | 95,2 | 68 | Media (n bajo) |
| Robomaster 60 | Cerrillos | 80,6 | 94 | Media |
| SIN_CATALOGO_25 | Cerrillos | 70,4 | 151 | Media (falta nombre en catálogo) |
| EURA 16 | Calama | 53,3 | 348 | Alta |
| PRIMA 3D | Cerrillos | 54,0 | 70 | Media (n bajo) |
| Dobladoras | Calama | 49,5 | 631 | Alta |
| Dobladora 4 | Coronel | 53,2 | 320 | Alta |
| Dobladora Tecmor S40 2 | Cerrillos | 43,2 | 2.006 | Alta |
| EURA 16 | Cerrillos | 43,3 | 1.733 | Alta |
| Dobladora Tecmor S40 1 | Cerrillos | 38,2 | 1.912 | Alta |
| FP-LC | Cerrillos | 38,3 | 2.448 | Alta |
| ESTRIBADORA TJK 1 | Coronel | 37,8 | 206 | Media |
| ESTRIBADORA TJK 2 | Coronel | 35,9 | 56 | Media (n bajo) |
| SIN_CATALOGO_26 | Cerrillos | 35,1 | 121 | Media (falta nombre) |
| EURA 20_3 | Cerrillos | 41,6 | 518 | Alta |
| Robomaster 55 | Cerrillos | 29,9 | 2.039 | Alta |
| FORMULA 12 | Cerrillos | 28,4 | 91 | Media |
| EURA 20_1 | Cerrillos | 27,5 | 2.060 | Alta |
| SIN_CATALOGO_414 | Coronel | 26,4 | 802 | Media (falta nombre) |
| Dobladora 3 | Coronel | 24,7 | 46 | Baja (n bajo) |
| SIN_CATALOGO_413 | Coronel | 18,3 | 58 | Baja (n bajo, falta nombre) |
| Línea Corte | Coronel | 16,4 | 753 | Alta |

## Máquinas sin valor confiable — NO usar la mediana tal cual

| Máquina | Planta | Mediana observada | Motivo |
|---|---|---|---|
| EURA 20_2 | Calama (111) | — | **Excluida.** Sospecha de "pistoleo" no confiable. |
| EURA 20_2 | Coronel (415) | — | **Excluida.** Mismo motivo. |
| COIL 14 M | Calama (101) | 1,5 min | Mediana implausible (segundos/pocos min), no investigado. |
| Robomaster 60 | Calama (107) | 3,0 min | Mediana implausible, no investigado. |
| EURA 20_2 | Calama (106, nombre de catálogo — no confundir con 111) | 3,7 min | Mediana implausible, no investigado. |
| Dobladora 2 | Coronel (404) | 0,2 min | Mediana implausible, no investigado. |
| SIN_CATALOGO_111 | Calama | 0,4 min | Mediana implausible, no investigado. |
| Curvadora 1/2, SIN_CATALOGO_416/417/27 | Coronel/Cerrillos | — | n<30, sin dato suficiente. |

**Para estas máquinas, usar como respaldo temporal la mediana censurada por
calendario (sección 27 del handoff) o el juicio de los jefes de planta,
hasta poder investigar la causa.**

## Segmentación por tamaño de pedido (más preciso, donde exista)

Para las máquinas de mayor volumen, la mediana varía bastante según el
tamaño del pedido (kg) — usar esto en vez de la mediana única cuando se
pueda. Tabla completa en
`~/graphify-workspace/optifierro/FASE3_OPERARIO_PEDIDO_FINAL_20260914.md`
(sección "Resultado 3"). Ejemplo (Dobladoras, Calama):
pedidos 2-64kg → 0,7 min · 64-188kg → 14,4 min · 188-478kg → 49,3 min ·
478-4.030kg → 150,6 min.

## Cómo se llegó a esto — resumen para retomar el estudio

1. Delta crudo (etiqueta a etiqueta): mediana en cientos de horas — inservible.
2. Censura por calendario estático: solo cambió Cerrillos, no resolvió nada.
3. Estadística aplicada rigurosa: bimodalidad confirmada en 81% de máquinas,
   ninguna distribución candidata pasa bondad de ajuste formal.
4. Segmentación por ID_Forma (complejidad de pieza): redujo la señal de
   mezcla 80-95% pero no la eliminó.
5. **Idea de Montu — seguir al operario, no solo la pieza — fue el quiebre
   real.** Tras 3 iteraciones (operario solo → operario+máquina con etiqueta
   → operario+máquina con pedido real `IT.Id`), la mediana por máquina
   finalmente cae en minutos plausibles para 26 de 33 máquinas.
6. El intervalo de confianza al 95% sigue sin ser angosto — la causa
   identificada es tiempo de espera hasta el siguiente pedido, no tamaño
   del pedido ni forma de la pieza. Este es el punto exacto donde retomar.

## Próximo paso sugerido para cuando se retome

Buscar si existe en Cubigest una señal de **cierre/entrega de pedido**
distinta de "inicio del siguiente" (algo que marque cuándo un pedido
realmente terminó, no solo cuándo empezó el próximo) — eso separaría
tiempo de proceso de tiempo de espera, que es la única pieza que falta.

## Dónde está todo

- Dataset: `optifierro-backend:/app/fase2_rutas_completo.db` (TO) — tablas
  `datos_rutas_v5` (con operario/turno/pedido_it) y
  `deltas_operario_pedido_segmentado`. Copia de seguridad en
  `~/MontuMS/datos_fase2/fase2_rutas_completo.db` (Mac Studio).
- Reportes completos: `~/graphify-workspace/optifierro/FASE3_*.md`.
- Handoff con la cronología completa: `~/MontuMS/docs/handoff_actual.md`,
  secciones 18 a 34.
