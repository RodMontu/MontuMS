
---
# TAREA CCa-34 — F5: Vista Semanal replicando el Cuadro de Programacion de Cubigest ("Fierro Preparado")
TAG: `f5` (rama `ola1-f5`, directorio `optifierro_f5`). Informe: `CCa34_f5_vista_semanal_cuadro_20261005.md`.

## Citas literales de Montu
- "debemos replicarlo tal cual" (la Vista Semanal debe replicar el informe del Cuadro de Programacion de Cubigest).
- "nos quedamos con el cuadro que dice Fierro Preparado donde muestra acero delgado y acero grueso ... menor o igual que 16 y mayor estricto que 16".
- "el Fierro Punta Largo Comercial lo dejaria aparte porque eso no es parte de la produccion".
- "en la seccion vista semanal donde dice resumen actual, abajo dice fuera de ventana y eso si lo dejaria, pero ... como una nota; el resumen actual debe incluir todo lo que diga ahi (todo lo que haya en el cuadro de programacion)".
- Esta seccion "debe quedar igual" que el informe aprobado por Gustavo: NO rediseñes la pantalla; solo corrige los datos y reemplaza el panel "Fuera de ventana" por una nota.

## Hechos del diagnostico
- `/api/programacion/semanal` (`programacion.py:850`, `obtener_proyeccion_semanal`) usa `_obtener_pids_pendientes` (SQL directo a
  Cubigest, solo pendientes). Verificado hoy por Miaude contra el informe real de Coronel: el API (a) INCLUYE el Largo Comercial
  (05-10 = 32.320 kg = exactamente IQ87-20/1; 06-10 = 45.132 = 4.732 Preparado + 40.400 Largo Comercial) y (b) EXCLUYE lo ya
  producido, que el Cuadro si suma (05-10: 10.468 kg del Preparado ausentes). El viernes 09-10 tampoco coincide (API 6.916 vs 49.595).
- Referencia real (Coronel, Cuadro 05-11 oct, pantalla de Cubigest de hoy 11:09), kg `Diam<=16 / Diam>16 / Total`:
  Fierro Preparado: lun 6.221/4.247/10.468 · mar 622/4.110/4.732 · mie 96/0/96 · jue 0/0/0 · vie 8.239/41.356/49.595 · sab 0/0/0 ·
  totales 15.178/49.713/64.891.  Fierro Punta Largo Comercial (`Diam<=18 / >18`): lun 0/32.320/32.320 · mar 10.100/30.300/40.400 ·
  resto 0 · totales 10.100/62.620/72.720. (Pueden variar levemente si Cubigest cambio desde entonces.)
- Ya existe un scraper del Cuadro (`scraper_cuadroprogramacion.py`, pagina `CuadroProgramacionPr.aspx`) y la tabla
  `cuadro_programacion_optisteel` (columnas: sucursal_id, fecha, viaje, kilos_propuestos, kgs_desp, avance_it_pct, status...),
  sincronizada cada 30 min por el job de sync. El scraper de detalle `importar_optisteel.py` baja un CSV por etiqueta (tabla `trabajos_optisteel`).

## Que hacer
1. INVESTIGAR (solo lectura): con el codigo del scraper existente (login/sesion ya implementados; sin imprimir credenciales),
   descarga la pagina del Cuadro para Coronel, semana 05-10-2026..11-10-2026, y determina si el HTML trae los bloques
   "Fierro Preparado" y "Fierro Punta largo Comercial" (tablas Dia / Diam<=16 / Diam>16 / Total). Esta consulta es identica a la
   que ya hace el sync cada 30 min: esta autorizada. Si el bloque resumen NO viene en el HTML (se arma por postback/JS), dilo.
2. IMPLEMENTAR segun el resultado:
   (a) Si el bloque viene: parsealo y guardalo en tabla nueva `cuadro_resumen_semanal` (sucursal_id, fecha, prep_delgado, prep_grueso,
       prep_total, lc_delgado, lc_grueso, lc_total, fecha_carga), cargada desde el mismo job de sync del Cuadro (una sola linea de
       llamada nueva en `main.py`; la logica en un modulo nuevo `cuadro_resumen.py`).
   (b) Si no viene: reconstruyelo con `cuadro_programacion_optisteel` (+ `trabajos_optisteel` para separar <=16/>16 por diametro) y demuestra
       con la tabla de referencia que reproduce los numeros. Si no es posible igualarlos, NO inventes: reporta el mejor ajuste y la diferencia.
   Criterio de aceptacion: para Coronel, los totales por dia deben coincidir con la referencia (tolerancia 1 kg por redondeo si
   Cubigest no cambio). Presenta la tabla "referencia vs SPP" en el informe.
3. `obtener_proyeccion_semanal` debe leer esa fuente local (sin SQL directo a Cubigest para los kg del Cuadro), manteniendo la FORMA de
   respuesta que consume `VistaSemanal.tsx` (lista por fecha con delgado/grueso/total por sucursal, `top_viajes` y demas claves);
   Largo Comercial FUERA de esos totales. Calama y Cerrillos: misma logica (regla de alcance: todo cambio vale para las 3 plantas).
4. Frontend `VistaSemanal.tsx` (cambio minimo): el panel "FUERA DE VENTANA" pasa a ser una NOTA discreta dentro/debajo de "Resumen
   actual", con la misma informacion de la leyenda UNI-04 y los contadores de atrasados/muy futura que hoy muestra (si esos
   contadores dependen de Cubigest y falla, la nota se omite sin error). Cuida que el Resumen actual sume lo que muestra el Cuadro.
5. Tests nuevos (parser o reconstruccion + endpoint) y `npx tsc --noEmit`.

## Archivos permitidos
`backend/routers/programacion.py` SOLO la funcion `obtener_proyeccion_semanal` y sus auxiliares; modulo nuevo `backend/cuadro_resumen.py`;
`backend/main.py` SOLO una llamada nueva en el job de sync del Cuadro; `frontend/.../VistaSemanal.tsx`; tests nuevos; esquema de la
tabla nueva (init/migracion defensiva con `CREATE TABLE IF NOT EXISTS`, como en `importar_optisteel.py:123-126`).

## NO HAGAS (especifico)
No cambies el diseño/colores/distribucion de la Vista Semanal. No toques Materia Prima, Proximas Semanas ni Compromisos Futuros
(siguen sobre el universo V6). No retires el scraper del Cuadro. No uses ni modifiques `_obtener_pids_pendientes`.
No escribas en Cubigest. No hagas `docker build`.
