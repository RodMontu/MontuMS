# Pendientes — Sistema Planificador de la Producción (Torres Ocaranza)
**Documento vivo — sin versionado formal, se actualiza frecuentemente**
**Última actualización:** 2026-09-06

## Grupo A — TI / Seguridad / Coordinación con Roberto
| # | Punto | Estado |
|---|---|---|
| A1 | GRANT solo lectura Cubigest | Aprobado |
| A2 | Llave SSH Mac-TO | Aprobado y en uso |
| A3 | Auto-login servidor TO | Listo para ejecutar - falta que Montu corra el paso con la contraseña real |
| A4 | Sincronizacion horaria a Cubigest (fusionado con A9 - levantar queries reales) | Pendiente levantar las queries actuales antes de enviarlas a Roberto |
| A5 | Cuenta dedicada sistema de averias | Resuelto - acceso alternativo encontrado via DevTools, misma cuenta sirve para Cuadre INET y Averias |
| A6 | Correo a Roberto - cuenta de servicio sin expiracion | Borrador listo, sin enviar |
| A7 | Reunion 1:1 con Roberto sobre averias | Cerrado - se resuelve junto con A5 |
| A8 | Monitoreo de carga propio durante consultas | Cerrado - es practica manual (Miaude/CCa vigilan la carga de Cubigest durante estudios puntuales), no requiere infraestructura nueva |
| A9 | Entregar queries actuales a Roberto | Fusionado con A4 |
| A11 | Cadencia de extraccion de turnos_programados (semanal vs diaria, para CENSURA_JORNADA del Motor de Tiempos) | Documentado, decision pendiente - posible conversacion con Roberto |

## Grupo B — Funcional / Producto (jefes de planta)
| # | Punto | Estado |
|---|---|---|
| B1 | PRIORIDAD 1 - Posible sistema OptiSteel con programacion real de fabricacion por planta/jornada, hallado por Montu via Cubigest | Investigar - podria resolver de fondo el problema de fecha despacho/fabricacion |
| B2 | Repartir etiquetas entre 2+ maquinas (cajita) - opcion manual por trabajo, habilitar en las 3 plantas | Pendiente, prioridad justo detras de B1 |
| B6 | Bloqueo de dias para Remiz/Francisco/Jose | Sin confirmar |
| B7 | Confirmar con Roberto lectura de columna prioridad Cubigest | Sin confirmar |
| B8 | Mejorar presentacion de tiempos con ayudantes | Sin confirmar |
| B11 | Actualizar GeoVictoria - Dylan (Coronel) | Sin estrategia aun |
| B12 | Generar programacion de turno noche | Probablemente simple (turnos semanales ya existen) - sin confirmar si se ejecuto |

(B3, B4, B5 retirados - viven en el Motor de Tiempos. B9 cerrado junto con B1.
B10 retirado - no aplica, era mala transcripcion de "EURA"/"pasadas", tema
operativo sin relacion con OptiFierro.)

## Grupo C — Compromisos con Mauricio Torres (dueno, reunion 30-jul)
| # | Punto | Estado |
|---|---|---|
| C2 | Conciliacion de volumenes semanales (583/196/135 ton) | Pendiente - hay pista de un informe dentro de Cubigest |
| C3 | Metrica ton/hora | En paralelo - ventana Motor de Tiempos |
| C6 | Ronda de validacion con jefes de planta | Primera ronda cumplida (Cerrillos, Coronel); segunda ronda pendiente, despues de que los cambios actuales esten en produccion |
| C7 | Reunion de seguimiento Mauricio-Rodrigo | No aplica todavia - se hace una vez consolidado todo lo demas |

## Fuentes
- Transcripcion reunion TI Torres Ocaranza, 28-08-2026 (Roberto, Rene, Gustavo)
- Acta consolidada de inducciones - Jose Auger (Cerrillos) y Remiz Rivano/Nelson Bustos (Coronel), 28-07-2026
- Minuta de reunion con Mauricio Torres, 30-07-2026
- TAREA_REINTERPRETACION_ESTADO_TURNOS_2.md + trabajo de CCa, 06-09-2026
- Presentacion "Sistema Planificador - Seguridad y Plan de Trabajo"
- Procedimiento de Trabajo Seguro v1.0
