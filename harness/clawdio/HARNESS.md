# HARNESS — Clawdio / Hermes Agent
**Versión:** 1.0
**Proyecto:** Clawdio (Hermes Agent v0.14.0) — Asistente Personal IA
**Fecha creación:** 2026-05-29
**Última actualización:** 2026-05-29
**Stack:** Hermes Agent / Python / systemd / serveri3 (192.168.1.211)
**Bot Telegram:** @pantero_bot

---

## 1. FORBIDDEN_PATTERNS

| ID | Patrón prohibido | Motivo | Origen |
|---|---|---|---|
| FP-001 | Usar `localhost` o `127.0.0.1` para llamadas entre servicios en serveri3 | Los servicios deben referenciarse por nombre de red interno o IP LAN. | Regla arquitectónica Docker/systemd |
| FP-002 | Modificar SOUL.md con comandos en línea sin validación YAML previa | SOUL.md es YAML. Un error de sintaxis mata el gateway. Siempre: backup → editar → `python3 -c "import yaml; yaml.safe_load(open('SOUL.md'))"` → aplicar. | Protocolo CCa SOUL.md |
| FP-003 | Iniciar hermes-gateway.service en serverX | Clawdio reside EXCLUSIVAMENTE en serveri3. Jamás levantar en serverX. | Nota crítica INVENTARIO_MAESTRO |
| FP-004 | Responder mensajes de Telegram sin validar user_id | Solo IDs autorizados: Montu=8357148621, Pecas=8328037199. Cualquier otro ID debe ser rechazado. | Regla de seguridad |

---

## 2. ARCHITECTURAL_RULES

| ID | Regla | Enforcement | Herramienta |
|---|---|---|---|
| AR-001 | Backup obligatorio antes de editar SOUL.md: `cp SOUL.md SOUL.md.bak.$(date +%Y%m%d)` | Pre-edit hook manual | Protocolo CCa |
| AR-002 | Validar YAML de SOUL.md antes de aplicar: `python3 -c "import yaml; yaml.safe_load(open('SOUL.md'))"` | Post-edit check | Python3 |
| AR-003 | Skills en ~/.hermes/skills/ — nunca modificar directamente en producción, siempre staging primero | Code review | Manual |
| AR-004 | LLM stack: Gemini 2.5 Flash (primary) → Nemotron 3 Super free (fallback 1) → llama3.1:8b local (fallback 2). No alterar el orden sin confirmar con Montu. | config.yaml validation | Manual |

---

## 3. PERMISSION_MATRIX

### Tier 1 — Autónomo
- Leer ~/.hermes/config.yaml y archivos de skills
- Leer SOUL.md, MEMORY.md, USER.md
- Ejecutar comandos de diagnóstico del sistema (systemctl status, journalctl)
- Leer agent_results/

### Tier 2 — Requiere confirmación
- Modificar SOUL.md o MEMORY.md
- Agregar o modificar skills en ~/.hermes/skills/
- Reiniciar hermes-gateway.service
- Modificar config.yaml (cambio de modelo, timeouts)

### Tier 3 — NUNCA autónomo
- Levantar hermes-gateway en serverX
- Modificar Telegram webhook o bot token
- Enviar mensajes masivos o broadcast
- Eliminar agent_results/ o historial

---

## 4. FAILURE_LOG

| Fecha | Módulo | Error detectado | Causa raíz | Corrección aplicada | Regla generada |
|---|---|---|---|---|---|
| 2026-04 | SOUL.md | Gateway crasheó tras edición | Error de sintaxis YAML introducido sin validación previa | Restaurar desde backup, agregar validación pre-aplicación | FP-002, AR-001, AR-002 |
