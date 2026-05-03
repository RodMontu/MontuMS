# MontuMS — Sistema de Trabajo Orquestado de Rodrigo Montuschi

Repositorio central de la **Metodología Sinérgica (MS)** y su protocolo de coordinación **MS-Flow**.
Este repo es el sistema nervioso compartido entre todos los agentes, modelos y herramientas del ecosistema.

---

## Metodología Sinérgica (MS)

Framework de tres capas para trabajo técnico con IA:

| Capa | Rol | Herramienta |
|---|---|---|
| Cerebro Cognitivo | Arquitectura, decisiones, diseño | Miaude (Claude) |
| Cerebro Lógico | Orquestación, coordinación, memoria | Clawdio (Hermes/Telegram) |
| Fábrica de Código | Ejecución, implementación | CC (CCa / ccor1-5) + AG (Antigravity/Gemini) |

**Principio cardinal:** Montu supervisa y valida. Los agentes ejecutan. Miaude decide la arquitectura. Clawdio coordina. Nadie improvisa roles.

---

## MS-Flow — Protocolo de coordinación

MS-Flow es el sistema nervioso de la MS: define cómo se pasan el trabajo los agentes, cómo se mantiene el contexto entre sesiones, y cómo Montu queda liberado para supervisar en lugar de intermediar.

### Flujo estándar

```
Montu define objetivo
    ↓
Miaude diseña el plan + genera handoff_actual.md
    ↓
Clawdio distribuye tareas a CC/AG según tipo
    ↓
CC ejecuta código / AG analiza y redacta
    ↓
Clawdio recoge resultados → agent_results/
    ↓
Miaude valida + actualiza handoff
    ↓
Montu supervisa y toma decisiones
```

### Reglas de rol

- **Miaude:** única fuente de decisiones de arquitectura y diseño. Nunca delegable.
- **AG (Gemini):** segundo cerebro. Arquitecto de reemplazo para implementación y análisis extenso. Lee handoff_actual.md y continúa desde donde Miaude dejó.
- **CCa:** ejecución crítica. Usar solo cuando sea imprescindible (costo de tokens).
- **ccor1-5:** ejecución rutinaria con modelos gratuitos OpenRouter. Priorizar siempre.
- **Clawdio:** capataz y mensajero. Ejecuta, distribuye, reporta. Nunca diseña ni decide arquitectura.

### Archivo handoff_actual.md

- **Ruta canónica:** `/home/x/handoff/handoff_actual.md` (symlink → `/home/x/MontuMS/handoff_actual.md`)
- El handoff es el "parte de turno" entre sesiones y entre agentes. Contiene:
  - Proyecto activo y objetivo
  - Estado (completados / en curso / pendientes)
  - Decisiones tomadas y sus razones
  - Próximo paso concreto con instrucción exacta
  - Convenciones activas del proyecto

**Workflow:**
- Al cerrar sesión con Miaude → Miaude genera el bloque handoff → Montu lo pega en AG y guarda
- Al abrir sesión nueva → ejecutar `sesion` en serverX o pegar handoff en primer mensaje
- AG lee: `"Lee /home/x/MontuMS/handoff_actual.md y continúa desde el próximo paso"`

---

## Convenciones globales del ecosistema

| Variable | Valor |
|---|---|
| serverX | 192.168.1.111, user x |
| serveri3 | 192.168.1.211, user i3 |
| AG | Antigravity (VS Code fork con Gemini) |
| G3F | Gemini 3 Flash |
| G3.1PH | Gemini 3.1 Pro High |
| G3.1PL | Gemini 3.1 Pro Low |
| CCa | Claude Code Anthropic (tokens caros) |
| ccor1-5 | Claude Code + OpenRouter (gratuitos) |
| Miaude | Claude claude.ai — Mi TI, CIO, Arquitecto |
| Clawdio / Rabín | Hermes Agent en serveri3, @pantero_bot |
| Clawdio Dev | @clawdio_dev_local_bot — alertas TI |
| Docker | Siempre rebuild (build + up), nunca solo restart |
| Correos | Siempre borrador, nunca enviar directo |
| Handoff | /home/x/MontuMS/handoff_actual.md |

---

## Proyectos activos

| Proyecto | Prioridad | Estado |
|---|---|---|
| OptiFierro V2 (Torres Ocaranza) | 🔴 URGENTE | Entrega final martes 2026-05-05 |
| OP Risk | 🟠 Alta | Arquitectura pendiente |
| PeluCare | 🟡 Media | Desarrollo pendiente |
| FabianSteel | 🟡 Media | Desarrollo pendiente |

---

*Repositorio privado — Rodrigo Montuschi D. — Montuschi Consultores SpA*
*MS-Flow inaugurado: 2026-05-03*
