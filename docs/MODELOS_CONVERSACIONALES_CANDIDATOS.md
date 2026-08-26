# Modelos conversacionales candidatos — evaluación en curso

**Propósito de este documento:** registro vivo de candidatos a modelo conversacional
liviano para uso junto a Pro/Carlitos y para Jan.app/LibreChat. Escrito directo por
Miaude (Aurora descartada como agente el 2026-08-25, invocación colgada sin salida —
desde esa fecha Miaude escribe directo al catálogo de La Biblioteca).

## Candidato descartado: Qwen3.8-27B (2026-08-22/23)

Probado en Jan.app contra Flash (Qwen3-30B-A3B) y Nemotron-3-Nano-Omni. Resultado real
medido (no benchmark de terceros): dense, 27B parámetros activos completos (sin atajo
de eficiencia de MoE). 14-15 tok/s, 65-103 segundos de "pensar" antes de responder,
se quedó sin contexto por pensamiento excesivo (38.150 tokens contra 32.768
disponibles), generó íconos/emojis no solicitados. Descartado — el diseño de atención
híbrida que promete la documentación pública (Gated DeltaNet, KV cache chico) no se
tradujo en velocidad real en este hardware. Flash (Qwen3-30B-A3B, MoE, 3B activos)
sigue siendo el mejor conversacional probado: 47-59 tok/s, 10-22s de "pensar".

## gpt-oss-20b (OpenAI, Apache 2.0) — activado y persistente en Mac Studio

**Historial real en este ecosistema:** NO es un modelo nuevo para Montu. Fue el
modelo primario real de Rabín durante semanas (julio 2026) — ganó un A/B test contra
qwen3.5:9b por consistencia en tool-calling/resolución de fechas. Se retiró del disco
más adelante, no por mal desempeño, sino porque la migración lo fue reemplazando
(qwen3.6:35b-a3b, después Flash). Advertencia de otro contexto (OP Risk, mayo 2026):
como agente ejecutor de bash/tools mostró loops de formato poco confiables — ese rol
es distinto al conversacional donde rindió bien.

**Especificaciones:** MoE, 21B total / 3.6B activos (mismo perfil de eficiencia que
Flash). Esfuerzo de razonamiento ajustable (clave: esto es lo que le faltó a
Qwen3.8-27B para no quedarse pensando). GGUF oficial (ggml-org), cuantización nativa
MXFP4, ~11.3GB en disco.

**Estado actual: activado y persistente (sesión anterior a 2026-08-26, nunca se
documentó hasta ahora).** Cargado, validado con completion real, y confirmado que
sobrevive el toggle completo Flash↔Pro (`modo-carlitos`/`modo-normal`) sin caerse
(~50 chequeos sin fallos durante la transición). Los scripts del toggle NO tocan
gpt-oss ni el puerto 11502 — es un tercer proceso independiente, permanente.

- Archivo: `/Users/montu/models/gpt-oss-20b-MXFP4.gguf` (~11.3GB, cuantización MXFP4
  nativa).
- LaunchAgent: `~/Library/LaunchAgents/cl.montuschi.llama-server-gptoss.plist`,
  `RunAtLoad=true`, `KeepAlive=true` — mismo criterio de persistencia que Flash.
- Puerto 11502 (Flash=11500, Pro=11501, gpt-oss=11502). `--host 192.168.1.102` (LAN,
  no loopback). `--alias gpt-oss-20b`. `--jinja` obligatorio (formato de chat
  Harmony, no funciona sin este flag — quedaba pendiente de confirmar y ya se
  confirmó que sí funciona). `-c 65536`.

**Por qué se eligió:** MoE real (mismo perfil de eficiencia que Flash), esfuerzo de
razonamiento ajustable, e historial ya probado en este ecosistema (ver arriba). Se
descartaron antes Qwen3.8-27B (14-15 tok/s, se quedaba sin contexto por pensar
demasiado, emojis no solicitados — ver sección de arriba) y Nemotron-3-Nano-Omni
(respuestas incompletas).

**RAM medida (no proyectada):** Flash+gpt-oss = ~16GB libres (sano). Pro+gpt-oss =
solo 551MB libres (ajustado pero funcional). Anomalía investigada: tras volver a
`modo-normal` la RAM libre cruda cayó a ~70MB, pero `memory_pressure` mostró 66%
libre real — macOS estaba reteniendo ~33GB en páginas "inactive" (cache de disco del
archivo de 48GB de Pro, reclamable al instante). Confirmado que NO es memory leak,
es comportamiento normal de macOS.

**Uso como modelo de respaldo (sesión 2026-08-26):** conectado como alternativa
liviana siempre disponible en LibreChat, Jan y Rabín (Hermes) — independiente del
toggle Flash/Pro. Detalle completo de esa integración en
`RISKO_LIBRECHAT_GOOGLE_WORKSPACE.md`, sección 9.

**Apodo "Lite" (sesión 2026-08-26, prueba):** en Jan, el modelo se identifica como
"Lite gpt-oss-20b" — parte de una limpieza del selector de Jan donde los tres
modelos locales quedaron con nombres consistentes: "Flash qwen3:30b-a3b", "Lite
gpt-oss-20b", "Pro qwen3-coder-next-80b-a3b", en ese orden, primero en la lista.
De paso se corrigió que el provider de Flash tenía el nombre/archivo de Pro por
error (nunca se había notado), se eliminó el provider `candidatos_conversacionales`
(modelos ya descartados: qwen3.8-27b, nemotron-3-nano-omni-30b-a3b), y se creó por
primera vez un provider dedicado para Pro en Jan (no existía). Es una convención de
nombres a modo de prueba, no necesariamente definitiva.

## Pendiente

- Jan.app: agregado el provider `llama_server_gptoss` en `settings.json`, pero
  requiere reinicio de Jan para aparecer en el selector (no crítico, no hecho aún).
- Confirmar si conviene documentar formalmente gpt-oss-20b como modelo de producción
  (fuera de la categoría "candidato en evaluación" de este documento) dado que ya
  está activo y en uso real hace más de una sesión.
