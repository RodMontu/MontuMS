# Incidente de Seguridad y Continuidad — Torres Ocaranza (OptiFierro / PROMETHEUS-AI-CORE)

**Equipo involucrado:** PROMETHEUS-AI-CORE (192.168.1.65), servidor cliente para el proyecto OptiFierro
**Fecha de los hechos:** disponibilidad 31-07/01-08-2026 · exposición detectada en auditoría 01–02-07-2026
**Fecha de compilación de este documento:** 2026-08-26
**Clasificación:** Interno / Confidencial
**Fuentes:** Informe Interno — Incidentes de Producción y Seguridad (TI Torres Ocaranza, 06-08-2026) + transcripción de la reunión de aclaración entre Rodrigo Montuschi, Roberto (DBA TO) y René (seguridad TO)

## 1. Por qué existe este documento

Este es el documento ancla de seguridad de la información de Montuschi Consultores SpA. No es un registro más de La Biblioteca: es el antecedente principal y la brújula para rediseñar cómo trabajamos con datos de clientes, a partir de dos incidentes reales ocurridos en el mismo equipo y en la misma ventana de tiempo. Toda decisión futura sobre metodología de trabajo seguro debe poder remitirse a este documento.

## 2. Incidente 1 — Disponibilidad en producción (tempdb)

**Qué pasó:** Un batch de OptiFierro, ejecutado directamente por Rodrigo (no un proceso desatendido) en la madrugada del 31-07 (03:53–05:18), corrió consultas sin acotar por rango de fechas contra la réplica productiva de SQL Server. El archivo `tempdev` de `tempdb` creció de ~100 MB a ~95 GB en 85 minutos (más de 50 crecimientos consecutivos, sin tope de tamaño configurado). El disco del servidor de base de datos (192.168.1.195) llegó a 96,4% de ocupación (9,9 GB libres de 278,8 GB), con riesgo inminente de detener el motor SQL Server. Coincidió con la ventana de pago de sueldos del fin de semana — la aplicación externa SIRC dejó de operar con normalidad durante el incidente.

**Causa raíz confirmada:** login SQL `OptiFierro`, cliente `python3.11`, ejecutado desde un contenedor en 192.168.1.65 — confirmado por el default trace del motor (evidencia preservada con hash SHA-256).

**Mitigación aplicada por TI (Torres Ocaranza), sábado 01-08, 09:00–11:00:**
1. Deshabilitó el login `OptiFierro` (contención, `is_disabled=1`).
2. Reinicio controlado del servidor — al recrearse `tempdb` con su tamaño de arranque (8 MB), el disco liberó espacio a 114,4 GB libres (62% ocupado) en vez de intentar recuperar los 95 GB.
3. Tope estructural aplicado a `tempdb` (`tempdev`: 4096 MB inicial / crecimiento fijo 512 MB / tope 40960 MB; `templog`: 1024 MB / 256 MB / 8192 MB). Antes tenía crecimiento del 10% sin tope — esto es lo que amplificaba cada evento. Con el tope puesto, una consulta desmedida falla de forma aislada (error 1105, tempdb lleno) sin comprometer el servidor.

**Lo que la reunión aclaró y el informe escrito no registra:**
- Rodrigo reconoce el error sin atenuantes: trabaja de noche por diseño (menor carga de sistema, mejor concentración), pero esa noche no cruzó el dato de que era ventana de pago de sueldos, y no acotó el rango de fechas de la consulta.
- Confirma explícitamente que fue él directamente frente al computador esa madrugada — no un proceso automatizado ni desatendido. Esto importa para la trazabilidad: no fue una falla de diseño del sistema, fue una decisión operacional puntual sin las salvaguardas adecuadas.
- Compromiso concreto hacia adelante: antes de correr un análisis pesado de este tipo a futuro, coordinarlo primero con Roberto — evaluando incluso trabajar sobre una copia de la base en vez de la réplica productiva en vivo.
- Tono de la conversación: aprendizaje conjunto, no sanción. Ambas partes (Rodrigo y TI) plantean trabajar más integrados y compartir lo que van aprendiendo.

**Pendiente (al momento de este documento):**
- Optimizar el batch de OptiFierro: acotar rangos de fecha, evitar extracciones completas de vistas de reporte pesadas, revisar planes de ejecución con derrame a tempdb.
- Evaluar aislar el entorno de pruebas de la instancia productiva de SQL Server.
- Condiciones para rehabilitar el login `OptiFierro`: mínimo privilegio (solo réplica `CubigestPruebas`, sin roles de servidor), primera ejecución en ventana controlada con monitoreo, idealmente trasladar el proceso a una instancia aislada.

## 3. Incidente 2 — Exposición de seguridad (Ollama sin autenticación, puerto 11434)

**Qué pasó:** La auditoría de seguridad de julio (escaneo 01–02-07-2026) detectó en 192.168.1.65 un servicio de IA local (Ollama) respondiendo sin autenticación en la red interna. Verificado en vivo durante la reunión: `GET /api/version`, `GET /api/tags` (enumeró los modelos cargados: qwen3:14b, devstral, qwen2.5:14b-instruct) y `POST /api/generate` respondieron sin exigir ninguna credencial. Superficie adicional identificada en el mismo equipo: servicios web (nginx, Uvicorn/FastAPI en varios puertos), múltiples canales de acceso remoto concentrados en un solo host (RDP, SSH, herramienta de terceros), y SMB con firma habilitada pero no requerida.

**Lo que la reunión aclaró:**
- El puerto 11434 es el estándar de Ollama para comunicación **entre contenedores** de un mismo stack (no exclusivo de IA) — no está expuesto a Internet, solo a la LAN interna del cliente. Los servicios propios de Rodrigo expuestos a Internet pasan siempre por Cloudflare Tunnel, sin puertos abiertos en su infraestructura personal.
- El riesgo real que plantea René (TI) no es acceso directo desde Internet, sino un vector lateral: un equipo interno comprometido (ej. navegación insegura desde el puesto de un usuario) actuando de puente para escanear la LAN y llegar al servicio sin autenticación.
- Rodrigo toma como tarea propia verificar que el puerto nunca ha estado expuesto hacia Internet (estimación propia: ~98% de certeza de que no).
- René toma como tarea propia (no urgente) profundizar la seguridad de la red Docker en general — explícitamente extiende la lección a su propia infraestructura personal también.

**Verificación propia, 26-08-2026:** el contenedor `optifierro-ollama` sigue publicado en `0.0.0.0:11434` en producción. Además, quedó identificado como **contenedor huérfano** (ya no referenciado por el `docker-compose.yml` vigente) durante una intervención de otro incidente ese mismo día. Este punto sigue sin resolver.

**Pendiente:**
- Exigir autenticación al servicio de IA (proxy inverso con credenciales) o restringir el acceso de red al puerto 11434 solo a las aplicaciones que lo consumen; idealmente volver al comportamiento por defecto (solo localhost).
- Consolidar el acceso remoto al equipo en un único método oficial (hoy: RDP + SSH + herramienta de terceros conviviendo).
- Decidir qué hacer con el contenedor huérfano `optifierro-ollama`.

## 4. Compromisos nuevos surgidos en la reunión (no están en el informe escrito)

| Compromiso | Solicitado por | Dirigido a | Nota |
|---|---|---|---|
| Separar la cuenta `OptiFierro` del uso personal de Rodrigo | Rodrigo | Roberto/René | Para poder distinguir si un error futuro es humano o del sistema |
| Que la cuenta de servicio `OptiFierro` **no expire cada 3 meses** | Rodrigo | Roberto | Ver hallazgo crítico, sección 5 |
| Auto-login de Windows en PROMETHEUS-AI-CORE, para que la red Docker se levante sola tras un corte de energía | Rodrigo | René/Roberto | Marcado como "comercial, no urgente" en la reunión |
| Documento de seguimiento de 3 columnas (tarea / responsable René o Roberto) | Compromiso de Roberto | — | Puntapié inicial de organización de pendientes de TI |
| Sincronización a Cubigest ~cada 1 hora (bajado de "tiempo real" por costo) | Acordado con Gustavo y Nelson | Falta el visto bueno técnico final de Roberto antes de implementar | |

## 5. Hallazgo crítico — la recurrencia ya se materializó

El 26-08-2026, OptiFierro dejó de traer datos de Cubigest. Diagnóstico: la contraseña de la cuenta SQL `OptiFierro` había expirado (error 18487). **Este es exactamente el escenario que Rodrigo pidió evitar en esta misma reunión** (sección 4: que la cuenta de servicio no expire cada 3 meses). El pedido no se había ejecutado, y el problema se materializó tal cual se anticipó. Se corrigió puntualmente el 26-08 (reset de contraseña + recreación del contenedor backend para que tomara el `.env` actualizado), pero **la causa de fondo (política de expiración sobre una cuenta de servicio) sigue sin resolverse** y se repetirá en el próximo ciclo si no se corrige con Roberto.

## 6. Punto de cultura de trabajo a corregir

En la misma reunión, Rodrigo menciona haber accedido en algún momento a la cuenta de Gustavo para resolver algo puntual, con aviso verbal previo pero sin autorización formal por escrito — él mismo lo califica como "no perverso, pero no correcto". Independiente de la intención, esta es exactamente el tipo de práctica que la metodología de trabajo seguro que estamos construyendo debe impedir hacia adelante: ninguna credencial ajena se usa sin autorización explícita y registrada, sin excepción y sin importar la urgencia del momento.

## 7. Principios ya validados (mantener, no rediseñar)

- **Manejo de credenciales:** entregar credenciales vía archivo `.env` que la aplicación consume para autenticar, nunca como texto legible por un modelo o agente de IA. Validado explícitamente por Roberto como el método correcto.
- **Arquitectura Cloud-piensa / agente-local-ejecuta:** el modelo en la nube (Claude) diseña el plan y no toca datos sensibles; un agente local ejecuta la consulta real contra la base de datos y solo devuelve resultados procesados a la nube. Esto es lo que protege los datos del cliente de salir hacia un modelo externo.
- **Ventanas de análisis estadístico:** máquinas → máximo 2 años atrás; personas/operadores → máximo 6 meses atrás (criterio ya en uso, reafirmado en esta reunión).

## 8. Tabla consolidada de pendientes

| # | Pendiente | Origen | Responsable | Estado a la fecha de este documento |
|---|---|---|---|---|
| 1 | Optimizar batch de OptiFierro (acotar fechas, evitar vistas pesadas completas) | Informe + reunión | Rodrigo | Pendiente |
| 2 | Evaluar aislar entorno de pruebas de producción SQL | Informe | TI / Rodrigo | Por evaluar |
| 3 | Condiciones de rehabilitación del login `OptiFierro` (mínimo privilegio, ventana controlada) | Informe | TI + Rodrigo | Pendiente |
| 4 | Autenticación o restricción de red para Ollama (puerto 11434) | Informe + reunión | Rodrigo | Pendiente — verificado 26-08 que sigue abierto |
| 5 | Consolidar accesos remotos al equipo en un único método oficial | Informe | Por definir | Pendiente |
| 6 | Decidir destino del contenedor huérfano `optifierro-ollama` | Verificación propia 26-08 | Rodrigo | Pendiente |
| 7 | Separar cuenta `OptiFierro` del uso personal de Rodrigo | Reunión | Roberto/René | Pendiente |
| 8 | Cuenta de servicio `OptiFierro` sin expiración de contraseña | Reunión | Roberto | Urgente — ya se materializó una vez (sección 5) |
| 9 | Auto-login Windows en PROMETHEUS-AI-CORE | Reunión | René/Roberto | Pendiente, no urgente |
| 10 | Documento de seguimiento de TI (3 columnas) | Reunión | Roberto | Verificar si ya se entregó |
| 11 | Sincronización horaria a Cubigest — visto bueno técnico final | Reunión | Roberto | Pendiente confirmación |
| 12 | Nunca usar credenciales ajenas sin autorización formal registrada | Reunión (autocrítica) | Rodrigo | Principio a incorporar en metodología de trabajo seguro |
| 13 | Rotación de credenciales del equipo/proyecto | Informe | TI + Rodrigo | Recomendada |

## 9. Fuentes

- Informe Interno — Incidentes de Producción y Seguridad, Torres Ocaranza / PROMETHEUS-AI-CORE, 06-08-2026.
- Transcripción de la reunión de aclaración (Rodrigo Montuschi, Roberto, René) — fecha de reunión no registrada en la transcripción; se realizó entre la detección del incidente (01-08) y la fecha del informe escrito (06-08).
