# B26-B — Portar el método validado (FASE3) a "Producción por Máquina"

**Fecha:** 2026-09-23 · **Estado:** PENDIENTE (posterior a la entrega del 24-09) · **Prioridad:** alta, Motor de Tiempos
**Origen:** decisión de Montu 23-09 — para el jueves se entrega la versión A (interina, honesta); B es la versión definitiva y debe hacerse pronto.

## Por qué B es necesario (evidencia RCA 23-09)
El endpoint `GET /api/tiempos-maquina` (`backend/routers/tiempos_maquina.py`) **no usa el método validado**:

| Aspecto | Endpoint (A, interino) | Método validado FASE3 |
|---|---|---|
| Unidad de tiempo | Delta entre registros consecutivos de `PIEZA_PRODUCCION` por máquina+sucursal, filtro laxo 2-480 min (líneas 243-253) | Agrupar operario+máquina, colapsar rachas por `pedido_it`, delta entre inicios de racha consecutiva |
| Break | No se descuenta | Se descuenta (13-14h Día / 01-02h Noche) |
| Exclusiones | Ninguna | Máquinas 111 y 415; saltos > 15 h; `ton_hora > 50` |
| Peso | Peso por etiqueta de la línea de pieza (A lo corrige a `KgsPaquete`) | `peso_prom_pieza` = suma(KgsPaquete del pedido) / etiquetas distintas del pedido |
| Bimodalidad | No tratada | Ninguna distribución pasó ajuste en 32 equipos: se reporta P25-P75, no media ± desvío |

Fuentes del método validado (espejo `~/graphify-workspace/optifierro/`): `FASE3_OPERARIO_MAQUINA_20260914.md`, `FASE3_OPERARIO_PEDIDO_FINAL_20260914.md`, `FASE3_TONELADAS_HORA_20260914.md`, `FASE3_PESO_POR_PIEZA_20260921.md`, scripts `fase3_operario_maquina.py`, `fase3_operario_pedido.py`. **Ninguno está en el checkout de TO ni trackeado en git.** Los scripts `build_kgshora_referencia.py` / `diagnostico_kgshora.py` en TO están sin trackear.

Hallazgo adicional: `p.TotalKgs` (usado hasta hoy) es el peso TOTAL de la línea de pieza (1 a 23.000 kg), no el de cada etiqueta. Con `dp.KgsPaquete` el ton/h de las líneas de corte baja 3-8x (p. ej. Línea de Corte Cerrillos, forma1 Ø16: 7,75 -> 1,04). En máquinas sin corte la diferencia es pequeña.

## Qué hace A (interino, jueves)
Solo el método de delta crudo, pero honesto: peso por etiqueta corregido (`KgsPaquete`), ton/h por intervalo con tope 50, rango empírico P25-P75, N por fila, N mínimo para mostrar ton/h, indicador "fuera de rango" y copy "estimado sobre historial, no validado a nivel operario". Se eliminan Mín/Mediana/Máx y `escenarios_estimados`.

## Qué exige B (definición de terminado)
1. **Definir la fuente de datos.** Hoy el método corre sobre `datos_rutas_v5` / `deltas_operario_maquina` (backup local, análisis offline). Opciones: (a) tabla precomputada en SQLite refrescada por job (recomendada: rápida y sin cargar Cubigest), (b) cálculo en vivo desde Cubigest (requiere confirmar que `PIEZA_PRODUCCION` expone operario: NO verificado).
2. **Llevar el método a código versionado** en el repo (hoy solo existe como scripts de análisis en el espejo).
3. **Aplicar** operario+máquina+pedido, colapso de rachas, descuento de break, exclusiones y tope, más segmentación por forma+diámetro+máquina+planta.
4. **Verificar** contra `FASE3_TONELADAS_HORA_20260914.md` (mismas cifras dentro de tolerancia) en 3 combinaciones por planta, sin valores absurdos.
5. **Cambiar el copy** de "estimado, no validado" a la frase definitiva, manteniendo P25-P75 (sin porcentaje de confianza inventado).
6. **Aclarar el caso de las líneas de corte:** `NroPiezas` allí no representa barras (kg/barra con P95 de 1000 a 2000 kg). Verificar su semántica antes de usar kg/barra en esas máquinas.

## Archivos y territorio
`backend/routers/tiempos_maquina.py`, `frontend/src/components/domain/TiemposPorMaquina.tsx` (exclusivos del Motor de Tiempos), más el job/tabla nueva. No toca `motor_v2.py`, `programacion.py` ni `GestorProgramacion.tsx`, salvo que se decida alimentar al Motor con estos ton/h (decisión aparte).

## Relación con otros puntos
- B44 (ajuste manual de tiempos, feedback loop del Motor) y auto-aprendizaje: Ola 3, después de B.
- B16 (minutos-hombre por jornada) y B44 (ajuste manual de tiempos que calibra el Motor): consumirán ton/h; conviene tener B26-B antes de calibrar.
