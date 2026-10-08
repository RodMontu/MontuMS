# Paquete para la Coordinadora — B26 versión A (V3)

**Fecha:** 2026-09-23 · **Estado:** listo para commit; deploy pendiente de turno.

## Archivos a commitear (repo optifierro, en TO) — `git add` de archivos concretos, nunca `-A`
```
git add backend/routers/tiempos_maquina.py frontend/src/components/domain/TiemposPorMaquina.tsx
```
En el working tree hay otros archivos modificados de otras ventanas (`AGENTS.md`, `HARNESS.md`, `backend/motor_v2.py`): NO son de B26.
Verificado: los 2 archivos de B26 no se superponen con los del commit B35 (`0522109`: `programacion.py`, `GestorProgramacion.tsx`).

## Mensaje de commit sugerido
```
feat(tiempos-maquina): Produccion por Maquina v-A — peso por etiqueta, rango P25-P75, N minimo e indicador fuera de rango — B26

- Causa raiz: el endpoint usaba piezas.TotalKgs (peso TOTAL de la linea) como peso de cada registro;
  ton/hora inflado 3-8x en lineas de corte y filtro por largo comparaba barra vs linea. Ahora
  detallePaquetesPieza.KgsPaquete (peso de etiqueta) y kg/barra = KgsPaquete/NroPiezas.
- ton/hora = mediana por intervalo (2-480 min, tope 50), rango P25-P75, N por fila, N minimo 15.
- estado_rango: ok / fuera_de_rango (bajo P5*0,9 o sobre P95*1,1 del historial de la maquina; margen 10 %) /
  no_evaluable (lineas de corte) / sin_largo.
- Subtitulo de la tabla unificado con el menu: "Produccion por maquina — Forma X · Ø Y mm".
- Se eliminan Min/Mediana/Max y escenarios_estimados (ratios sin respaldo); nueva nota metodologica y nota de rutas.
- Metodo validado FASE3 pendiente: B26-B (docs/B26_B_pendiente_metodo_validado.md).
```

## Bloque de Changelog (Protocolo de Cambio)
```
## 2026-09-23 — B26 (v-A) Produccion por Maquina
- CAMBIO: backend/routers/tiempos_maquina.py, frontend/src/components/domain/TiemposPorMaquina.tsx
- CAUSA RAIZ: peso por linea (TotalKgs) usado como peso por etiqueta; metodo de delta crudo con columnas Min/Med/Max sin sentido.
- CRITERIOS: intervalo 2-480 min; tope 50 ton/h; N min 15; fuera de rango < P5*0,9 o > P95*1,1 kg/barra (margen 10 %, aprobado 23-09); no evaluable si P90(ratio)>1,5; grupos 5/3/1 por N (>=50/>=30); rango P25-P75.
- VERIFICACION: arnes pre-deploy (11 casos + 7 con margen, Cubigest solo lectura); 0 filas con ton/h>50; N<15 sin ton/h; con margen 12 m = ok, 14 m y 30 m = fuera de rango.
- PENDIENTE: B26-B (metodo validado FASE3), deploy y verificacion real.
```

## Documentos actualizados (repo MontuMS/docs)
`LOG_CAMBIOS_2026.md` (entrada nueva arriba, con backup), `pendientes_sistema_planificador.md` (fila B26 y fila nueva B26-B), `tablero_coordinacion_spp.md` (fila V3), `B26_A_criterios_produccion_maquina.md` (para manuales), `B26_B_pendiente_metodo_validado.md`, y **`MAPA_DECISIONES_SPP.md` (nuevo)**.
Evidencia: `agentes/evidencia_B26/{antes,despues_preliminar}/`, `B26_A_diff_20260923.patch`, informe `agentes/CCa3_b26_implementacion_20260923.md`, encargo `agentes/prompts/CCa3_B26_ejecucion.md`.

## Después del commit
1. Regenerar Graphify (HEAD actual `0522109`; el grafo vigente está construido desde `ff00b595`).
2. Turno de deploy: solo backend + frontend. Un rebuild empaqueta también los cambios de las demás ventanas.
3. Verificación DESPUÉS contra el sistema desplegado (mismos 6 casos base + forzados con largo) y reemplazar el ejemplo del manual.

## Propuesta a la Coordinadora — mantenimiento del mapa de decisiones (pedido de Montu 23-09)
`docs/MAPA_DECISIONES_SPP.md` registra cada decisión del SPP (estadística, análisis, asignación) con valor, motivo, fuente en código, fecha y quién aprobó. Sección 1 (B26) completa; secciones 2 (FASE3) y 3 (Motor) sembradas desde código y documentos; lista de faltantes en la sección 5.
Propuesta de regla para todas las ventanas: al registrar el LOG, agregar o actualizar la fila del mapa en el mismo turno; si el código y el mapa difieren, gana el código y se corrige el mapa. Pendiente de aprobación de la Coordinadora.
