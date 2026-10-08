# VENTANA V2 — PANTALLA: B35 (regla +15 min inicio / -15 min fin de jornada) (Ola 1)
Antes de todo: lee `/Users/montu/MontuMS/docs/agentes/prompts/00_CONTEXTO_BASE_OLA1.md` y aplica sus reglas.

## Tu carril
**Punto:** B35 — la regla +-15 min "sigue fallando" (Montu, ~7 fixes previos, frustracion legitima). Debe quedar resuelta de raiz, no como un fix mas.
**Archivos que puedes tocar:** `backend/routers/programacion.py` (solo `obtener_programacion()` y lo minimo necesario) y
`frontend/.../GestorProgramacion.tsx` (`getEventStyle`, `getHoraFromPercent` y el estado de jornada). **Prohibido:** `motor_v2.py` (V1 lo edita; tu solo IMPORTAS/llamas sus funciones), y el componente/endpoint de "Produccion por Maquina" (V3).

## Diagnostico ya hecho (RCA 22-09 + CCa-1 23-09; verificalo tu con codigo real)
- La regla vive bien en el backend (`motor_v2.py` `_get_config_turno`, 3 niveles de prioridad, default 08:15/16:45; y `_ventana_desde_geovictoria` / `_ventana_desde_turnos_programados` en programacion.py).
- `POST /generar` la aplica bien. Pero `obtener_programacion()` (GET, carga de pantalla) NO devuelve `metadata` con el turno resuelto (`programacion.py:365-369`).
- El frontend calcula su PROPIO `inicioTurno/finTurno` con fallback a `jornadaInicio/jornadaFin` (sin buffer) y luego `'08:00'` crudo. Tras cualquier recarga, el Gantt y el drag&drop usan ese fallback.
- Tres fuentes de verdad para una regla de negocio = por eso "se arregla y vuelve". El fix debe dejar UNA.
- Git confirma: ningun commit de B35 despues de `ff00b59`. Ignora la afirmacion "B35 corregido y desplegado" de documentos previos.

## Pasos
1. Graphify: blast radius de `obtener_programacion()` y de los consumidores de `metadata`/`jornadaInicio` en el frontend.
2. Reproduce el sintoma ANTES (produccion real): "Generar Programacion" -> recargar pantalla -> comparar inicio/fin del Gantt con el turno resuelto. 3 sucursales, turno dia y turno noche (cruza medianoche).
3. Fix: el backend expone en la respuesta GET el turno YA resuelto (`metadata.hora_inicio_turno/hora_fin_turno`, llamando a la MISMA funcion que usa el Motor; no reimplementes la regla).
   El frontend usa SIEMPRE ese dato y se eliminan los fallbacks locales (`?? '08:00'`, jornadaInicio/Fin como origen de la regla). Si el backend no lo manda: mostrar aviso visible, no inventar hora.
4. Verificacion en el sistema real, mismo escenario del paso 2, 3 sucursales x dia/noche. Sin regresion de B33/B34: reordenar en la misma maquina, piso a "ahora", asignar desde la Bolsa sin rebote ni duplicado.
   (dnd-kit bloquea eventos sinteticos: el drag real lo confirma Montu con el mouse; tu verifica por API y build limpio.)
5. Build TS limpio, diff a Montu, OK, commit (`fix(programacion): turno resuelto viaja del backend al Gantt, una sola fuente de verdad — B35`), turno de deploy a la Coordinadora, regenera Graphify.
6. Reporta segun protocolo (RESUMEN <=15 lineas). B44 (Ola 3) tocara estos mismos archivos: tu commit debe quedar limpio y documentado antes.
