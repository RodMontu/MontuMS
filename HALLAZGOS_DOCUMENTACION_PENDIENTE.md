# Hallazgos y Documentación Pendiente — Migración Mac Studio / Retiro serveri3
## Insumo para Aurora (a ejecutar una vez que tenga modelo local + harness definidos)

Este documento se va actualizando en vivo durante la migración. Cuando Aurora esté lista, este es su punto de partida — no partir de cero revisando chats.

---

## A. Cosas que existían y NO estaban en INVENTARIO_MAESTRO ni LOG_CAMBIOS del repo principal

| Ítem | Detalle | Fuente del hallazgo |
|---|---|---|
| **Risko (risko-gateway.service)** | Instancia completa de Hermes Agent para OP Risk, `HERMES_HOME=/home/i3/.risko/`, bot `@Risko_OP_bot`, modelo `gemini-2.5-flash`. Desplegada 2026-05-05, nunca llegó al INVENTARIO_MAESTRO ni LOG_CAMBIOS_2026.md principal. | Chat aislado "Herramientas de control para OP Risk" (05-may), no propagado a docs centrales |
| **Nextcloud OP Risk** | Contenedor `op-risk-nextcloud`, puerto 8090, `docker-compose.nextcloud.yml` en `/srv/op-risk/`, datos en `/srv/op-risk/nextcloud-data/`, expuesto en `docs.risk.montuschi.cl`. 16 documentos indexados desde `/mnt/extra/OP Risk/` en serverX. | Mismo chat aislado del 05-may |
| **voice-proxy.service** | Proxy de transcripción de la era OpenClaw (puerto 9877). Detenido y deshabilitado 2026-04-18, reemplazado por `stt-proxy`. El archivo `.service` sigue en disco pero inactivo — candidato a limpieza física, no solo documental. | Chat "Reinstalación ServerX con KC600" (19-abr) |
| **Cadena de fallback de Clawdio desactualizada** | La doc dice `model.default: gemini-2.5-flash` + fallback único `llama3.1:8b` en serverX. La realidad (verificada 2026-07-10 antes de Fase 3): `model.default: deepseek-v4-flash` (OpenRouter) + 3 fallbacks (`hermes-3-llama-3.1-405b`, `nemotron-3-super-120b`, `glm-5` vía ollama-cloud). El fallback a serverX/llama3.1:8b documentado **nunca existía** en la config real al momento de revisar. | Verificación directa de config.yaml en serveri3, previo a Fase 3 |
| **Nomenclatura de agentes aclarada** | "Clawdio" ya no es un agente real — quedó como apodo genérico del período OpenClaw→Hermes para referirse en conjunto a los agentes de IA. Los agentes reales hoy: Rabín, Risko, Spinita (pendiente), Carlitos, Aurora. Protocolo de alias: nombre propio con mayúscula para agentes con personalidad definida (Carlitos, Aurora); protocolo `cc+modelo` se mantiene para futuros modelos cloud genéricos sin personalidad propia. | Aclarado por Montu 2026-07-10 |
| **Rol Aurora vs. Rabín resuelto (definitivo)** | Dos corpus documentales separados, sin superposición: **Aurora** escribe documentación técnica (LOG_CAMBIOS, INVENTARIO_MAESTRO, commits a MontuMS) — cero acceso a documentación personal de Montu. **Rabín** solo LEE documentación técnica (consulta/referencia, no escribe ahí) y es dueño completo (lectura+escritura) de la documentación personal de Montu (tareas, ideas, notas). Pendiente de definir: ¿el "solo lectura" de Rabín sobre lo técnico es una restricción de permisos Unix real, o una regla de comportamiento en su config? — pregunta abierta a Montu. | Aclarado por Montu 2026-07-10 |
| **Aurora — capacidad de localización ("¿dónde está X?")** | Requisito nuevo de Montu: Aurora debe poder responder dónde vive cierta información, no solo documentarla. Sin resolver aún si necesita RAG vectorial o basta con búsqueda de texto completo (ripgrep) sobre el repo. Backlog: **BACKLOG-AURORA-FASE2** — diseñar en su propia sesión, no bloqueante para que Aurora exista y documente hoy. | Misma sesión 2026-07-10 |
| **Contenedor Docker `hermes-risko` (fantasma, #3)** | Contenedor Docker corriendo desde el 3 de junio, compitiendo por el mismo token de Telegram que `risko-gateway.service` (systemd, el deployment documentado desde 05-may), causando conflictos de getUpdates. Confirmado que compartía el mismo directorio de datos (/home/i3/.risko, sin estado propio). Detenido (no eliminado) 2026-07-10. | Descubierto por CCa durante Fase de repunte de Risko |
| **Límite real de memoria GPU en M2 Max (96GB)** | macOS no entrega los 96GB completos a Metal/GPU — un modelo de 85GB (`qwen3.5:122b-a10b`) se derramó 95% a CPU, cayendo de 27.1 a 15.4 tok/s con contexto real. Afecta el sizing de cualquier modelo >~60-70GB para este equipo. Alternativa técnica no aplicada: `sysctl iogpu.wired_limit_mb` para subir el límite manualmente. | Fase Risko, 2026-07-10 |
| **Risko cambia de modelo por latencia** | `qwen3.5:122b-a10b` → `qwen3.6:35b-a3b` (24GB, MoE, entra completo en GPU) por derrame a CPU. Confirmado: 26.4s primera respuesta (vs 2m2s), 100% GPU, sin derrame. | 2026-07-10 |
| **Contaminación de contexto por sesiones sin límite (transversal)** | Confirmado en 2 agentes distintos: Rabín acumuló 89k tokens desde el 30-may (Fase 3, causó latencia); Risko se "identificó como Gemini" por contaminación de una sesión de Telegram también del 30-may. Mismo mecanismo de fondo: `compression.enabled: false` en Hermes, sesiones que nunca se resetean solas. No es bug aislado de un agente — es de diseño, compartido por todos los agentes Hermes (Rabín, Risko, y futuros Aurora/Spinita si usan el mismo framework). Backlog: evaluar activar compresión de contexto o política de reset automático periódico, no solo mitigar con /new manual. | Fase Risko (diagnóstico de tono), cruzado con Fase 3 (Rabín) |
| **Comando /sethome** | Montu resolvió algo relacionado a `/sethome` en su chat individual con Risko justo antes del informe de CCa — detalle aún no documentado, pendiente que Montu explique qué era para registrarlo correctamente. | 2026-07-10, mencionado sin detalle |

## B. Cambios de esta sesión de migración, aún no formalizados

| Ítem | Estado actual | Pendiente documentar |
|---|---|---|
| Mac Studio M2 Max 96GB | IP fija `192.168.1.102`, usuario `montu`, nodo IA principal | Ficha completa en INVENTARIO_MAESTRO (specs, rol, reemplaza qué) |
| GPU P104-100 (serverX) | Redestinada a passthrough → VM Windows + NoMachine (DEC-03 resuelto) | Actualizar PLAN_MIGRACION (tenía "host por ahora" como default) + INVENTARIO_MAESTRO |
| serveri3 | En proceso de retiro completo — servicios migran a serverX | Documentar migración cuando se complete Fase 2 |
| Llave SSH x→i3 | Creada esta sesión (no existía, solo había i3→x) | Agregar a sección de accesos SSH del inventario |
| Stack de modelos Ollama por agente (estado FINAL, confirmado) | Rabín: `gpt-oss:20b` (ganador del A/B en Fase 2). Carlitos: `qwen3-coder:30b`. Aurora: `qwen3.6:35b-a3b`. Risko: `qwen3.6:35b-a3b` (cambiado desde `qwen3.5:122b-a10b` por derrame a CPU). Spinita: modelo `qwen3.5:9b` descargado, agente aún no levantado. | Confirmar todo esto quedó reflejado en INVENTARIO_MAESTRO |
| Visual-Voice STT | Benchmark mlx-whisper (large-v3 / large-v3-turbo / medium) — aún no ejecutado | Documentar resultado + decisión final cuando se corra Fase 4 |
| Disco RESPALDO_ARCA | Desconectado (no perdido), ubicación fue ambigua en el inventario | Corregir estado a "desconectado, pendiente reconexión" |

## C. Sobre el harness de Aurora (pendiente de diseño, previo a delegarle este documento)

Antes de pasarle esta lista a Aurora, hay que auditar/construir su HARNESS.md siguiendo el patrón MS v3.0 (igual que otros proyectos). Como mínimo debería incluir:
- Reglas de formato exactas para LOG_CAMBIOS_2026.md e INVENTARIO_MAESTRO.md (estructura, nivel de detalle, qué va en cada uno)
- Regla explícita: Samba `/mnt/extra/DOCUMENTOS_TECNICOS/` es archivo histórico, NO modificar
- Fuente de verdad: repo MontuMS en GitHub, copia local en `~/MontuMS` en serverX
- Protocolo de commit vía Clawdio (doc-updater skill) — clarificar si Aurora reemplaza esa función de Clawdio o la complementa (pregunta abierta de sesiones anteriores, aún sin responder)
- Ejemplos de entradas "buenas" de LOG_CAMBIOS ya existentes, para que imite el tono/nivel de detalle real

**Esto se hace DESPUÉS de tener Ollama + modelo de Aurora corriendo en Mac Studio, antes de asignarle este backlog documental.**
