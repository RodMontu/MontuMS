# Procedimiento de Trabajo Seguro

**Versión:** 1.0
**Fecha:** 2026-08-26
**Autores:** Rodrigo Montuschi + Miaude (Claude)
**Alcance:** Todo trabajo de Montuschi Consultores SpA que involucre infraestructura o datos de un cliente. Primera aplicación: Torres Ocaranza / OptiFierro.
**Origen:** Incidentes de disponibilidad y exposición de seguridad en Torres Ocaranza, agosto 2026 (ver `incidente_seguridad.md`) + reflexión estructurada de Rodrigo Montuschi, registrada y consolidada en esta conversación.
**Estado:** Vigente desde esta fecha. Se aplica de inmediato a todos los pendientes abiertos con Torres Ocaranza.

## 1. Propósito

Este documento fija cómo trabajamos cuando el trabajo toca infraestructura o datos de un cliente, para que la seguridad de la información deje de depender de la memoria o el criterio puntual de quien está trabajando esa noche, y pase a ser un procedimiento explícito, verificable y exigible — tanto por nosotros como por el cliente.

No busca la perfección ni cubrir cada escenario posible. Busca ser un procedimiento bueno, claro y que efectivamente se cumpla, y que evolucione con el tiempo (ver sección 11).

## 2. Principio rector

**El dato del cliente se queda donde corre nuestro hardware propio. Todo lo que toca un tercero — nube, SaaS, cualquier proveedor externo — se trata como si pudiera salir de nuestro control, sin importar cuán confiable sea ese proveedor.**

De este principio se derivan todas las reglas siguientes.

## 3. Roles — quién puede tocar qué

| Rol | Qué es | Qué puede tocar |
|---|---|---|
| **Miaude** (Claude, en la nube) | Arquitecto y supervisor metodológico | Nunca datos operativos puntuales del cliente. Revisa metodología, coherencia de resultados agregados, redacta documentación y planes. |
| **CCa** (Claude Code, en la nube) | Ejecutor de tareas de código e infraestructura | Tareas de servidor que no exponen datos sensibles del cliente (configuración, despliegues, logs filtrados). Nunca consultas directas a bases de datos del cliente. |
| **Agente de desarrollo local** (nombre interno "Carlitos" — ver sección 9 sobre cómo referirnos a él frente al cliente) | Modelo de lenguaje corriendo 100% en hardware propio (Mac Studio), sin credenciales de ningún servicio en la nube | Único canal autorizado para cualquier consulta a bases de datos del cliente. Actúa bajo planificación y supervisión de Miaude o CCa según el tipo de tarea. |
| **Rodrigo** | Responsable final | Valida resultados, autoriza excepciones, decide qué se comparte con el cliente. |

## 4. Clasificación de datos y canal obligatorio

| Tipo de dato | Ejemplo | Canal obligatorio |
|---|---|---|
| Datos personales u operativos puntuales del cliente | Filas de una consulta a Cubigest, registros de asistencia GeoVictoria, nombres de usuario en logs | **Agente local, sin excepción** |
| Resultados agregados o derivados que reflejan capacidad operativa del cliente | Tabla final de toneladas/hora por máquina | Confidencial de negocio: validación directa por Rodrigo; Miaude puede revisar metodología y rangos generales, nunca la tabla completa con cifras exactas |
| Metodología y código propio | Lógica del motor de tiempos, prompts, arquitectura de la aplicación | Sin restricción especial — es propiedad intelectual nuestra, tratada igualmente con cuidado mientras no exista NDA/DPA firmado con el cliente |
| Infraestructura del servidor | `docker ps`, reinicios, configuración, logs de sistema sin datos personales | CCa o Miaude por defecto; agente local si el log expone datos personales |

## 5. Excepción — incidentes de disponibilidad urgentes

Existe una única excepción a la regla de "agente local para todo lo que toca al cliente": una caída de producción en curso, donde la velocidad de respuesta importa más que la pureza del canal.

Condiciones para que aplique la excepción:
- Debe ser un incidente real de disponibilidad, no conveniencia.
- El output debe filtrarse antes de llegar a Miaude o CCa (ej. `grep` por código de error, nunca logs completos sin filtrar).
- Debe quedar registrado en la bitácora explícitamente como excepción, con el motivo.
- Se revisa después del hecho — no se convierte en práctica habitual.

## 6. Bitácora de accesos

Cada sesión que toque el servidor o la base de datos de un cliente genera una entrada, escrita en el momento por el propio agente que ejecuta la tarea (no reconstruida después desde el historial de una conversación).

**Campos de la entrada:**
- Fecha, hora de entrada, hora de salida, tiempo neto trabajado
- Canal / agente usado (agente local, CCa, o excepción de Miaude/CCa directo)
- Sistema tocado (servidor, base de datos, o ambos)
- Qué se hizo (resumen de la tarea)
- Resultado o referencia (commit, documento, conversación)
- Nivel de sensibilidad de los datos tocados
- Si fue excepción: sí/no, y motivo

**Mecanismo de escritura:** CCa y el agente local escriben su sesión completa a un archivo en el momento de ejecutar (ej. redirección de la sesión de terminal a un archivo), no por copiar y pegar después. Miaude redacta su propia entrada estructurada al cerrar cada tarea. La bitácora completa vive en La Biblioteca, como cualquier otro documento técnico.

## 7. Qué es interno y qué se comparte con el cliente

- **Bitácora interna (completa):** incluye el *cómo* — comandos, prompts, metodología, decisiones técnicas. Es propiedad intelectual del trabajo. Se mantiene interna.
- **Extracto para el cliente (derivado):** incluye únicamente el *qué* y el *cuándo* — fecha, hora, sistema tocado en términos generales, propósito de alto nivel. Nunca la metodología ni los comandos exactos. Se genera a partir de la bitácora interna, no se redacta por separado a mano.

## 8. Cómo demostramos al cliente que el agente local es realmente local

- **Prueba estructural:** el agente de desarrollo local no tiene ninguna credencial de ningún servicio en la nube almacenada en su configuración — verificable inspeccionando el archivo de configuración del agente.
- **Prueba empírica:** monitoreo de conexiones salientes durante una sesión (ej. Little Snitch en Mac Studio) muestra únicamente la conexión hacia el propio servidor del cliente, nada más.
- **Invitación abierta:** el equipo de seguridad del cliente puede observar directamente una sesión de trabajo del agente local si lo desea, sin necesidad de confiar en nuestra palabra.

## 9. Nomenclatura hacia el cliente

Al comunicarnos con el cliente (Torres Ocaranza u otros), nunca usamos el nombre interno "Carlitos". Se describe como: *"nuestro agente de desarrollo, que corre sobre un modelo de lenguaje local en nuestra propia infraestructura, sin conexión a servicios en la nube."*

## 10. Higiene periódica de nuestros propios equipos

- **Mac Studio:** monitoreo de conexiones salientes (Little Snitch o similar); revisión periódica de `~/.ssh/authorized_keys` y de LaunchAgents/LaunchDaemons no reconocidos.
- **ServerX:** ejecución periódica de herramientas de detección de rootkits (`rkhunter`, `chkrootkit`); revisión de puertos abiertos (`ss -tlnp`) contra lo esperado.
- **Cadencia:** mensual o trimestral, automatizado y notificado por Telegram, siguiendo el mismo patrón ya usado para otros reportes periódicos.

## 11. Control de versiones de este documento

Usamos versionado semántico (`MAYOR.MENOR`, análogo al de software):
- **MAYOR:** cambia un principio o una regla estructural (ej. quién puede tocar qué, sección 3 o 4).
- **MENOR:** se agrega una sección o regla nueva sin contradecir lo anterior.
- Correcciones menores de redacción no incrementan la versión — se registran igual en el historial de cambios.

Esta es la versión **1.0**: entra en vigencia de inmediato como procedimiento vinculante, no como borrador — por eso no parte en `0.x`.

## 12. Historial de cambios

| Versión | Fecha | Cambio |
|---|---|---|
| 1.0 | 2026-08-26 | Primera versión. Generada a partir de la reflexión conjunta post-incidente Torres Ocaranza (ver `incidente_seguridad.md`) y consolidada en conversación dedicada. |

## 13. Fuentes

- `incidente_seguridad.md` — informe de incidentes de Torres Ocaranza + reunión de aclaración con TI (origen de este procedimiento).
- Conversación de definición de este procedimiento, 2026-08-26.
