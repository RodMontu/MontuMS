# Handoff — MS-Flow inauguración completa
**Última actualización:** 2026-05-03 — 21:30 hrs
**Sesión anterior:** Miaude — sesión completa de infraestructura MS-Flow
**Próxima sesión:** DOS frentes paralelos (ver abajo)

---

## Lo que se completó hoy

- ✅ Fix monitor.sh (heredoc — bug unterminated string literal)
- ✅ Fix SOUL.md (registro lingüístico, criterio de oro, prohibidos)
- ✅ Hermes reiniciado — crons 08:00 y 20:00 operativos
- ✅ Repo MontuMS creado (github.com/RodMontu/MontuMS, privado)
- ✅ SSH key serverX → GitHub configurada (id_ed25519_github)
- ✅ Infraestructura handoff: /home/x/MontuMS/ + symlink + aliases
- ✅ Gemini Lead (Gem) configurado con system prompt MS-Flow completo
- ✅ agentes.md — catálogo completo 11 agentes Claude + equipo Gemini
- ✅ proyectos.md — 5 proyectos activos + pipeline TO
- ✅ convenciones.md — IPs, aliases, reglas, URLs raw
- ✅ docs/ — INVENTARIO_MAESTRO, LOG_CAMBIOS, CLAWDIO migrados desde Samba
- ✅ GitHub reemplaza Samba como fuente de verdad activa
- ✅ MS-Flow bautizado oficialmente como protocolo de coordinación de la MS
- ✅ LOG_CAMBIOS_2026.md actualizado y pusheado desde AG

## Problema pendiente — Rabín (CRÍTICO)
Monitor.sh sigue fallando en los crons 08:00 y 20:00 — el fix de hoy no fue suficiente. El cron de las 20:00 indica que el script está siendo **interpretado como Python en vez de bash**. Esto sugiere que el problema no es solo sintaxis del script sino cómo Hermes lo invoca.

## Dos frentes abiertos para próximas sesiones

### Frente 1 — Clawdio (ventana separada)
- RCA real del monitor.sh (interpretado como Python, no bash)
- Verificar fix SOUL.md aplicado correctamente
- Diseñar rol Clawdio Dev como coordinador MS-Flow
- Restricción: usar ccor1-3 y ccl prioritariamente

### Frente 2 — OptiFierro (ventana separada) — URGENTE martes 2026-05-05
- Configurar SSH Mac → TO
- Instalar Gemini CLI en TO
- Revisar 17-18 puntos pendientes de reunión cliente martes pasado
- Estrategia: Mac con VPN para QA + Gemini CLI en TO para ejecución

## Convenciones activas
- serverX = 192.168.1.111, user x
- serveri3 = 192.168.1.211, user i3
- TO = 192.168.1.65, user OptiFierro (Windows 11)
- AG = Antigravity / G3F = Gemini 3 Flash / G3.1PH = Gemini 3.1 Pro High
- CCa = tokens caros / ccor1-3 = gratuitos (priorizar) / ccor4-5 = pago OpenRouter
- MontuMS = github.com/RodMontu/MontuMS — fuente de verdad
- DOCUMENTOS_TECNICOS en Samba = archivo histórico, no tocar
- Docker: rebuild siempre / Correos: solo borrador

## Próximo paso concreto
Abrir dos ventanas de chat nuevas con los mensajes de arranque provistos por Miaude al cierre de esta sesión. Cada ventana trabaja un frente independiente.