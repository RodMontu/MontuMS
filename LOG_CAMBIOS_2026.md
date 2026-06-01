
---

## 2026-06-01 — Visual-Voice: Cambio de modelos LLM para generación de minutas

**Archivo modificado:** `/home/x/visual-voice/main.py` (volumen montado, sin rebuild)

**Cambios aplicados:**
- MODEL_CONFIGS reemplazado: de 5 modelos a exactamente 2:
  - `openrouter:deepseek/deepseek-v4-flash` | Label: "DeepSeek V4 Flash (rápido)" | Badge: CREDITS | DEFAULT
  - `openrouter:openai/gpt-oss-120b:free`   | Label: "GPT-OSS 120B (gratuito)"   | Badge: FREE
- Default `model_key` en `MinutesReq` actualizado a `openrouter:deepseek/deepseek-v4-flash`
- Contenedor reiniciado con `docker restart` (sin rebuild — main.py es volumen directo)
- Endpoint `/models` verificado: retorna exactamente los 2 modelos nuevos ✓

**Estado post-cambio:** visual-voice Up, puerto 8502→8000 activo
