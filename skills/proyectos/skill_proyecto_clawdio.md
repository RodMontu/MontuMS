# Skill de Proyecto: Clawdio / Hermes
## Versión: 1.0 — Mayo 2026
## Host: serveri3 (192.168.1.211, user i3)

---

## Descripción
Clawdio es el asistente personal IA de Montu y Pecas.
Bot Telegram: @pantero_bot
Framework: Hermes Agent v0.12.0
Modelo: gemini-2.5-flash (principal) + Nemotron free + llama3.1:8b (fallbacks)

## Rutas críticas — NO mover ni renombrar sin actualizar config.yaml
- Config: /home/i3/.hermes/config.yaml
- Personalidad: /home/i3/.hermes/SOUL.md
- Memoria: /home/i3/.hermes/memories/MEMORY.md
- Perfil usuario: /home/i3/.hermes/USER.md
- Supermercado: /home/i3/.hermes/supermercado.json
- DB deberes/ideas: /home/i3/.hermes/clawdio_db.sqlite
- Resultados agentes: /home/i3/.hermes/agent_results/
- Skills: /home/i3/.hermes/skills/

## Servicios systemd (usuario i3)
- hermes-gateway.service — gateway principal
- stt-proxy.service — STT Flask en puerto 9877

## Cuentas Google autenticadas
- rodrigo@montuschi.cl — perfil default (/home/i3/.hermes/)
- ce3wkc@gmail.com — perfil montu (/home/i3/.hermes/accounts/montu/)
- rivera.melgarejo@gmail.com — perfil pecas (/home/i3/.hermes/accounts/pecas/)

## Reglas de operación
- session_reset.mode = session (preserva perfil entre sesiones)
- tool_progress: none para Telegram (no mostrar pasos intermedios)
- Clawdio NO puede enviar correos directamente — solo crear borradores
- Clawdio NO puede hacer push a GitHub sin instrucción explícita de Claude

## Usuarios autorizados del bot
- Montu: Telegram ID 8357148621
- Pecas: Telegram ID 8328037199
- Cualquier otro ID no está autorizado

## Crons activos
- 08:00 diario: monitor infra
- 09:00 diario: briefing mañana
- 17:00 L-V: recordatorio ideas
- 20:00 diario: monitor noche
- 10:00 viernes: resumen semanal

## Lo que NO se toca sin orden explícita
- SOUL.md (personalidad core — cambiar esto afecta toda la experiencia)
- config.yaml (cambios aquí pueden romper el servicio)
- Credenciales Google OAuth (tokens en accounts/)
- supermercado.json (lista de 61 productos — no vaciar)
