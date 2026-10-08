TAREA — investigar el 16,2% multi-maquina (delgado) y equivalente en grueso
**Contexto:** ver docs/handoff_actual.md seccion 12, docs/informe_calibracion_plc_proxy_20260906.md,
piloto Fase 2 de hoy (bitacora_accesos_torres_ocaranza.md, entrada mas reciente
antes de esta tarea: 6.299 filas/4.400 etiquetas unicas, Cerrillos/delgado/
agosto-2026, 711 etiquetas = 16,2% con mas de una maquina).

Hipotesis de Montu a probar, NO asumir cual es correcta, dejar que el dato
decida:
H1: corte (o equivalente segun nombre por planta) -> estribadora (secuencia
    normal de 2 maquinas, no es una excepcion real).
H2: dentro de H1, algunos trabajos van ademas a dobladora/curvadora MANUAL
    porque la estribadora no da para el doblez/curvatura pedido (secuencia de
    3 maquinas).

Ejecutor real: Carlitos3.8 (`~/bin/Carlitos3.8`, ya existe, wrapper con
timeout duro incorporado). Usar CARLITOS_TIMEOUT=550 desde el inicio -
aprendizaje del piloto anterior, el modelo tarda en generar, no se cuelga.
Pasos atomicos, uno a la vez, DENTRO de esta misma invocacion tuya (no
prometas "background" - completa todo aca o reporta honestamente hasta donde
llegaste).

PASO 1: catalogo de maquinas de Cerrillos - traer MAQ_NRO + nombre/descripcion
de la tabla MAQUINA. Metadata, bajo riesgo.

PASO 2 (delgado): para los 711 etiquetas multi-maquina de Cerrillos/delgado/
agosto-2026 (recalcular con la misma query acotada del piloto si el archivo
anterior ya no existe en el contenedor), traer secuencia ordenada por fecha
de (maquina, fecha) para cada etiqueta. Lotes chicos.

PASO 3 (delgado): clasificar cada etiqueta segun secuencia de NOMBRES de
maquina: cuantas corte->estribadora (H1), cuantas con tercer paso a dobladora/
curvadora manual (H2), cuantas no calzan. Reportar SOLO agregados.

PASO 4 (grueso): repetir para acero GRUESO, mismo Cerrillos/agosto-2026.
Identificar multi-maquina en grueso primero, luego pasos 2-3 sobre ese
conjunto.

PASO 5: comparar delgado vs grueso, misma hipotesis o cambia el patron.

Reglas: PTS de siempre (solo agregados, log/bitacora, timeout duro, comando
literal a Carlitos3.8). No expandir a otras plantas/meses. Reporta breve al
terminar, comparacion delgado/grueso al cierre.
