# TAREA — Lote Fase 1 + MT-03, Motor de Tiempos — 2026-09-06 (actualizado)
**Ejecutor de las consultas reales: Carlitos3.8** (puerto 11505, Qwen3.8-27B —
reemplaza a CarlitosCoderFlash para esta tarea, por confiabilidad multi-paso).
**CCa supervisa y espera por Carlitos — Miaude no debe hacer polling directo,
ahorro de tokens.**

## PASO 0 — Gate G0 rapido sobre Carlitos3.8 (bloqueante, hacer primero)
Antes de darle datos reales de TO a Carlitos3.8: correr el Gate G0 completo
(2 pruebas de inyeccion de prompt, datos sinteticos, ver
`handoff_carlitos_harness_2026-09-03.md` seccion 2 para el diseño exacto),
con verificacion independiente (no confiar en el autoreporte). Si Carlitos3.8
falla alguna, DETENTE y reporta - no sigas a las tareas de abajo con datos
reales. Documentar veredicto en `handoff_lote_cca_20260906.md`.

**Aprobado por:** Montu (via Miaude, ventana coordinadora)
**Contexto completo en:** ~/MontuMS/docs/handoff_actual.md,
~/MontuMS/docs/actualizaciones_plan_motor_tiempos.md,
~/MontuMS/docs/bitacora_accesos_torres_ocaranza.md (revisa las entradas de HOY
2026-09-06 antes de tocar nada),
~/MontuMS/docs/TAREA_REINTERPRETACION_ESTADO_TURNOS.md

## Reglas duras (PTS v1.0) - sin excepcion
1. Cubigest SOLO LECTURA. Nunca INSERT/UPDATE/DELETE/DROP/ALTER/EXEC.
2. Columnas explicitas, WHERE con indice, rango de fechas acotado, TOP de
   seguridad. Nunca SELECT * sobre tablas grandes.
3. Acceso real a Cubigest: **Carlitos3.8** via SSH alias `TO`, con
   `docker exec optifierro-backend python -c "from database_cubigest import cubigest_db; print(cubigest_db.execute_query('QUERY_AQUI'))"`.
   No inventar cadenas de conexion distintas. **Usar siempre con timeout duro**
   (variable `CARLITOS_TIMEOUT`, default 600s ya viene en el wrapper nuevo) -
   nunca lanzar sin ese resguardo, es el fix real del cuelgue de hoy.
4. Log obligatorio despues de cada tarea: entrada en bitacora_accesos_torres_ocaranza.md
   (mismo formato de hoy) y log en Escritorio de TO. Verificar con `ls` que
   quedo escrito - no confiar en autoreporte de Carlitos.
5. Instrucciones a Carlitos: comando literal completo siempre, nunca prosa.
6. Limpiar scripts temporales (contenedor y Escritorio de TO) al cerrar cada
   tarea, verificado.
7. NO ejecutar Fase 2 (barrido masivo). NO sobreescribir extractor_rutas.py
   original.
8. Si te bloqueas en algo que requiere decision de Montu, registralo pendiente
   en el handoff de cierre y avanza a la siguiente tarea.

## Que hay que hacer, en orden (avanza a la siguiente apenas termine la anterior)

### TAREA 1 - join PLC_IdEtiquetaTO <-> etiqueta fisica
Prueba ambas hipotesis contra Cubigest, TOP 1000, ultimos 2 meses, Cerrillos
(IdSucursal=4):
a) PLC_IdEtiquetaTO = detallePaquetesPieza.id
b) PLC_IdEtiquetaTO = piezas.id
Cuenta matches reales de cada hipotesis, gana la de mas matches.

### TAREA 2 - cruce de calibracion PLC vs proxy (Fase 1, MT-04)
**AUTORIZADO por Montu, confirmado con Roberto (DBA TO): luz verde con criterio
explicito de Roberto - "consulta lo mas pequeña posible, no todo junto". El tope
de tempdb (40GB) que Roberto ya puso es la red de seguridad estructural para
esto - no es una alarma nueva, es la salvaguarda funcionando como fue diseñada.**

**Correccion sobre el intento anterior:** el join de 4 tablas de una sola vez
(via MAQUINA.MAQ_NRO + detallePaquetesPieza.IdViaje, sin acotar fecha) violo el
criterio de Roberto. NO se necesita ese join. El universo ya esta acotado desde
la Tarea 1: son ~11.940 filas conocidas de ProduccionesPLC (Cerrillos, todo el
piloto Feb-2025 a Mar-2026) con su detallePaquetesPieza.id ya confirmado como
la clave.

**Pasos atomicos obligatorios, uno a la vez, verificando cada uno antes de seguir:**

a) UNA query, acotada por fecha (Feb-2025 a Mar-2026) y sucursal Cerrillos:
   trae de ProduccionesPLC los campos PLC_IdEtiquetaTO, PLC_FechaInicio,
   PLC_FechaFin (solo donde ambas no nulas). Guarda el resultado en un archivo
   local en TO (CSV o sqlite), NO lo dejes solo en memoria.

b) Con esa lista ya guardada (maximo ~12k IDs), consulta PIEZA_PRODUCCION
   filtrando por dp.id IN (...) EN LOTES DE 500 IDs por query (no los 12k
   juntos), y SIEMPRE con el mismo acote de fecha del piloto. Trae solo
   PIE_FECHA_PRODUCCION y el identificador de maquina. Guarda cada lote
   localmente antes de pasar al siguiente.

c) El calculo de "delta con el registro anterior de la misma maquina" (proxy)
   y la comparacion contra la duracion real de PLC: TODO en Python local sobre
   los archivos ya guardados, CERO consultas nuevas a Cubigest para esta parte.

d) Agrega: mediana, media, percentil 80 de la diferencia (proxy - real).

**Regla dura para el resto del lote:** ninguna query nueva contra
PIEZA_PRODUCCION o detallePaquetesPieza puede unir mas de 2 tablas a la vez, y
toda query contra esas dos tablas debe llevar acote de fecha explicito. Si en
algun punto crees que necesitas mas de eso, DETENTE y dejalo documentado en vez
de intentarlo.

### TAREA 3 - borrador de informe de calibracion (MT-04)
Con el resultado de Tarea 2: casos coincidentes, si el sesgo es sistematico o
ruido, recomendacion preliminar entre las 4 opciones de la seccion 3.1 del
plan maestro. El circuito PLC de Cerrillos fue un piloto corto con errores
conocidos - priorizar mediana/moda sobre promedio, tratar extremos como
probable ruido de instrumentacion.

### TAREA 4 (alta prioridad, bloqueante Fase 2) - MT-03
Reescribir extractor_rutas.py en copia nueva (extractor_rutas_v2.py, no
sobreescribir original): agrupar por dp.Etiqueta en vez de dp.id, usar el
patron de conexion de database_cubigest.py.

### TAREA 5 (opcional, baja prioridad) - MT-05
Campo IdMov de detallePaquetesPieza: revisar sys.foreign_keys o inferir por
valores.

## Log y cierre
Al terminar cada tarea: append en ~/MontuMS/docs/handoff_lote_cca_20260906.md
(que, que se hizo, resultado verificado, que falta) y entrada en la bitacora.
Al terminar la ultima tarea alcanzada, cierre final con estado global.
