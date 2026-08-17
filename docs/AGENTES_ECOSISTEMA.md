# AGENTES_ECOSISTEMA.md — Directorio Vigente de Agentes de la MS

**Última actualización:** 2026-08-16, por Miaude (Claude Sonnet 5).
**Motivo de creación:** incidente de citación de rol obsoleto (Miaude afirmó
que Rabín documenta, cuando ese rol ya había sido reemplazado por
Aurora+CCa). Este documento existe para que ningún agente — Miaude incluido
— cite un rol que ya cambió.

## Propósito y alcance

Este NO es un documento de especificaciones técnicas profundas (para eso
está INVENTARIO_MAESTRO.md). Es la capa de ROUTING: quién hace qué, HOY,
con qué comando exacto. Si un rol cambia, este archivo se actualiza en el
mismo commit que introduce el cambio — no después.

## Protocolo de actualización de este documento

- Se actualiza CADA VEZ que un rol de agente cambia, no solo cuando se
  agrega infraestructura nueva.
- Responsable operativo: CCa (bajo supervisión, mismo protocolo que
  LOG_CAMBIOS_2026.md).
- Todo cambio de rol debe dejar rastro en la tabla "Roles retirados" de
  abajo — nunca se borra una fila, se marca como reemplazada.

## Tabla de agentes vigente (verificado 2026-08-16)

| Agente | Rol | Invocación real | Modelo | Ejecuta en | ¿Documenta? |
|---|---|---|---|---|---|
| **Miaude** (yo) | Arquitecto principal, RCA, decisiones binarias, orquestador de más alto nivel | Chat directo (claude.ai) | Claude Sonnet 5 (modelo activo; verificar cada sesión — puede cambiar) | — | Redacta contenido; delega escritura/catálogo a CCa+Aurora |
| **CCa** (Claude Code) | Implementación compleja, ejecución en servidores, ORQUESTADOR de Aurora | `~/.local/bin/claude --dangerously-skip-permissions -p "prompt"` | Sonnet (Anthropic, vía cuenta CCa) | Mac Studio (con SSH a serverX/TO) | Sí — supervisa a Aurora, escribe LOG_CAMBIOS, git commit+push |
| **agy** (Antigravity) | Ejecución de primer nivel, frontend, gratis (reemplazó a Gemini CLI) | `/Users/montu/.local/bin/agy` · agy-headless-bridge como MCP | Gemini 3.5 Flash | Mac Studio | No |
| **Carlitos** | Coding mecánico, completion-only | `~/bin/Carlitos` → `pi --provider llama-local --model qwen3-coder-next --append-system-prompt carlitos-sp.md` (verificado en vivo 2026-08-16; alias viejo de Claude Code CLI sobre Ollama queda comentado en .zshrc, NO USAR) | qwen3-coder-next vía Pi/llama-server | Mac Studio | No |
| **Aurora** | Clasificación + resumen/tags para La Biblioteca. SIEMPRE bajo supervisión de CCa | `~/bin/Aurora` → `pi --provider llama-local --model qwen3-coder-next --append-system-prompt aurora-sp.md` (mismo hallazgo que Carlitos) | qwen3-coder-next vía Pi/llama-server | Mac Studio | Genera borrador — CCa valida antes de aceptar |
| **Rabín** (Clawdio) | Mensajería/notificaciones Telegram únicamente | MCP `clawdio`, target `telegram:8357148621` | qwen3.6:35b-a3b, hermes-gateway.service | serverX | ❌ NO desde 2026-08-16 — ver "Roles retirados" |
| **Risko** | Asistente OP Risk, Telegram, mención en grupo | hermes-risko.service | qwen3.6:35b-a3b | serverX | No |
| **QRO** (Qwen Desktop) | Segundo/tercer cerebro — red-team arquitectónico, deep research, contexto masivo (1M tokens) | App GUI, handoff MANUAL vía Montu (no invocable por Miaude) | Qwen3.8-Max (Alibaba, cloud) | Mac Studio (cliente MCP puro) | No — analiza, no escribe en el ecosistema |

## Roles retirados / cambios de rol (histórico — no repetir la cita vieja)

| Fecha | Cambio | Motivo |
|---|---|---|
| 2026-08-16 | Rabín deja de documentar (doc-updater, commit+push a MontuMS) | Reemplazado por Aurora+CCa con supervisión, para elevar confianza en calidad de Aurora |
| 2026-08-06 | Carlitos/Aurora migran de Ollama directo a Pi + llama-server (qwen3-coder-next) | Ver INVENTARIO_MAESTRO.md, sección "Stack de inferencia local nuevo" |
| 2026-06-18 | Gemini CLI reemplazado por Antigravity (agy) | Google eliminó OAuth de Code Assist individuales |
| 2026-07-12 | serveri3 apagado físicamente, servicios migrados a serverX | Consolidación de infraestructura |

## Reglas transversales (aplican a todos los agentes, sin excepción)

- Ningún agente que no sea Miaude/CCa toma decisiones de arquitectura —
  el resto solo ejecuta lo indicado explícitamente.
- Todo modelo local se invoca con timeout explícito, nunca vía bucle
  agéntico sin límite (incidente de referencia: cuelgue de 9+ horas sin
  error ni resultado).
- El routing entre agentes es SIEMPRE configuración determinista, nunca
  delegado a un LLM pequeño (incidente de referencia: modelo 9B fabricó
  su propia identidad al decidir routing).
- Datos de cliente (Torres Ocaranza/OptiFierro) y datos nominados de OP
  Risk NUNCA salen del perímetro Anthropic/local — cero excepciones,
  incluyendo QRO o cualquier otro agente cloud de terceros.

## Fuentes relacionadas (no duplicar contenido — referenciar)

- Especificaciones técnicas profundas de infraestructura → `INVENTARIO_MAESTRO.md`
- Uso de La Biblioteca (catálogo FTS5) → `COMO_USAR_LA_BIBLIOTECA.md`
- Patrón técnico de invocación CCa/Gemini vía osascript → skill `miaude-sin-montu`
- Flujo orquestado y reglas de escalamiento → `REGLAS_CARDINALES_FLUJO_ORQUESTADO.md`
  ⚠️ **Parcialmente desactualizado:** menciona Gemini CLI como agente primario
  y serveri3 como gateway activo — ambos superados por este documento y por
  INVENTARIO_MAESTRO. Pendiente de refresco formal (ver backlog).
