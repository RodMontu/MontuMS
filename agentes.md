# agentes.md — Catálogo de Agentes del MS Team
**Repositorio:** github.com/RodMontu/MontuMS
**Última actualización:** 2026-05-03
**Nota:** Este archivo es la fuente de verdad del stack de agentes. Actualizar cada vez que se agregue, elimine o modifique un agente.

---

## Equipo Claude (Claude Lead / Miaude)

| Alias | Modelo | Tipo | Costo | Rol |
|---|---|---|---|---|
| CCa | Claude Sonnet (Anthropic) | Cloud pago | Plan Pro | Ejecución crítica — usar solo cuando imprescindible |
| ccor4 | deepseek/deepseek-v4-flash | OpenRouter pago | $0.14/$0.28 M tok | Desarrollo real, bajo costo |
| ccor5 | deepseek/deepseek-v4-pro | OpenRouter pago | $0.44/$0.87 M tok | Tareas críticas, máximo razonamiento |
| ccor1 | openai/gpt-oss-20b:free | OpenRouter gratis | $0 | Tareas mecánicas rápidas, boilerplate |
| ccor2 | openai/gpt-oss-120b:free | OpenRouter gratis | $0 | Razonamiento complejo free |
| ccor3 | nvidia/nemotron-3-super-120b-a12b:free | OpenRouter gratis | $0 | Multiagente, 1M contexto |
| ccl | qwen2.5-coder:7b (Ollama local) | Local GPU | $0 | Coding privado, offline, sin rate limit |
| ccgemma | gemma3n (Ollama local) | Local GPU | $0 | Multimodal, resumen, visión básica |
| ccglm | glm-5:cloud (Ollama cloud) | Cloud gratis | $0 | Propósito general |
| cckimi | kimi-k2.5:cloud (Ollama cloud) | Cloud gratis | $0 | Razonamiento complejo, contexto extenso |
| ccqwen | qwen3.5:cloud (Ollama cloud) | Cloud gratis | $0 | Tareas generales, lógica avanzada |

**Regla de uso:** priorizar agentes gratuitos y locales. CCa, ccor4 y ccor5 solo cuando la tarea lo justifica.
**Presupuesto OpenRouter:** $15 USD cargados (saldo ~$14.76 al 2026-05-03).
**Hardware GPU:** NVIDIA P104-100 8GB VRAM. OLLAMA_MAX_LOADED_MODELS=1.

---

## Equipo Gemini (Gemini Lead)

| Herramienta | Modelo | Tipo | Rol |
|---|---|---|---|
| Gemini Lead (Gem) | Gemini Pro | Cloud pago | Arquitecto de reemplazo, análisis extenso, relay |
| AG (Antigravity) | Gemini Pro/Flash | Cloud pago | IDE principal, implementación frontend/docs |
| Gemini CLI | Gemini Pro/Flash | Cloud pago | Ejecución desde terminal, subagentes paralelos |

---

## Coordinador del MS Team

| Herramienta | Bot | Host | Rol |
|---|---|---|---|
| Clawdio Dev | @clawdio_dev_local_bot | serveri3 | Coordinador y orquestador entre equipos |
| Clawdio / Rabín | @pantero_bot | serveri3 | Asistente personal Montu + Pecas (NO es el coordinador) |

---

## Criterio de asignación por tipo de tarea

| Tipo de tarea | Agente preferido |
|---|---|
| Coding mecánico, boilerplate, scripts simples | ccor1, ccor2, ccl |
| Razonamiento complejo, lógica de negocio | ccor5, CCa |
| Análisis extenso, documentación masiva | Gemini Lead / AG |
| Privacidad total / offline | ccl, ccgemma |
| Ejecución crítica en producción | CCa |
| Relay cuando Claude agota cuota | Gemini Lead |

---

*Stack en evolución — actualizar este archivo cuando cambie el ecosistema.*
