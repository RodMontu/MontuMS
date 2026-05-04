# convenciones.md — Convenciones Globales del MS Team
**Última actualización:** 2026-05-03

---

## Infraestructura

| Nodo | IP | Usuario | Rol |
|---|---|---|---|
| serverX | 192.168.1.111 | x | Docker host principal, GPU P104-100 8GB, Ollama |
| serveri3 | 192.168.1.211 | i3 | 24/7, Clawdio, Cloudflare tunnel, nginx, Pi-hole |
| TO / PROMETHEUS-AI-CORE | 192.168.1.65 | OptiFierro | Servidor cliente Torres Ocaranza, OptiFierro V2 |
| MacBook Pro 13" 2018 | — | Montu | Estación de trabajo principal |
| Cubigest (SQL Server) | 192.168.1.195 | — | Base de datos ERP Torres Ocaranza |

## Aliases SSH

| Alias | Destino |
|---|---|
| sshi3 | ssh i3@192.168.1.211 |
| sshx | ssh x@192.168.1.111 |
| sshto | ssh OptiFierro@192.168.1.65 (pendiente configurar) |

## Abreviaciones del equipo

| Abreviación | Significado |
|---|---|
| MS | Metodología Sinérgica |
| MS-Flow | Protocolo de coordinación de la MS |
| AG | Antigravity (VS Code fork con Gemini) |
| G3F | Gemini 3 Flash |
| G3.1PH | Gemini 3.1 Pro High |
| G3.1PL | Gemini 3.1 Pro Low |
| CCa | Claude Code Anthropic |
| MontuMS | github.com/RodMontu/MontuMS |
| Miaude | Claude Lead en claude.ai (Mi TI, CIO, Arquitecto) |
| Clawdio / Rabín | Asistente personal @pantero_bot |
| Clawdio Dev | Coordinador MS Team @clawdio_dev_local_bot |
| TO | Torres Ocaranza (cliente) |

## Reglas operativas globales

- **Docker:** siempre `docker compose build && docker compose up -d` — nunca solo `restart`
- **Correos:** siempre como borrador, nunca enviar directamente
- **GitHub MontuMS:** fuente de verdad — leer antes de actuar, commitear al terminar
- **Instrucciones correctivas:** siempre de Montu directo a Claude — nunca mediadas por agentes
- **Tokens:** priorizar gratuitos y locales — CCa y ccor4/5 solo cuando la tarea lo justifica
- **Agentes disponibles:** consultar `agentes.md` — el stack evoluciona

## Rutas clave

| Ruta | Contenido |
|---|---|
| /home/x/MontuMS/ | Repo MontuMS local en serverX |
| /home/x/handoff/handoff_actual.md | Symlink → handoff en repo |
| /home/i3/.hermes/ | Hermes Agent (Clawdio) |
| /home/i3/.hermes/scripts/monitor.sh | Script monitoreo infraestructura |
| /home/i3/.hermes/SOUL.md | Personalidad Clawdio |
| /mnt/extra/DOCUMENTOS_TECNICOS/ | Archivo histórico (Samba miau_nube) |

## GitHub — URLs directas para el MS Team

| Archivo | URL raw |
|---|---|
| handoff_actual.md | https://raw.githubusercontent.com/RodMontu/MontuMS/main/handoff_actual.md |
| agentes.md | https://raw.githubusercontent.com/RodMontu/MontuMS/main/agentes.md |
| proyectos.md | https://raw.githubusercontent.com/RodMontu/MontuMS/main/proyectos.md |
| convenciones.md | https://raw.githubusercontent.com/RodMontu/MontuMS/main/convenciones.md |
| INVENTARIO_MAESTRO.md | https://raw.githubusercontent.com/RodMontu/MontuMS/main/docs/INVENTARIO_MAESTRO.md |
| LOG_CAMBIOS_2026.md | https://raw.githubusercontent.com/RodMontu/MontuMS/main/docs/LOG_CAMBIOS_2026.md |
