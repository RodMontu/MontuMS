# REGLAS CARDINALES — FLUJO DE TRABAJO ORQUESTADO
**Versión:** 2.0
**Fecha:** 2026-05-29
**Anterior:** v1.0 (2026-05-02) en /mnt/extra/DOCUMENTOS_TECNICOS/
**Metodología:** Sinérgica v3.0 — Harness Engineering
**Propósito:** Brújula sistémica para el trabajo coordinado entre Montu, Claude (CCa/Miaude), Clawdio y agentes del ecosistema.

---

## ARQUITECTURA DE CAPAS (MS v3.0)

1. **ARQUITECTO:** Claude (Miaude/CCa) — Planificación, diseño y visión estratégica.
2. **LÍDERES / SUBGERENTES:** Gemini (chat) + ChatGPT — Análisis de apoyo y supervisión.
3. **COORDINADOR / ORQUESTADOR:** Clawdio Rabín — Puente de ejecución y gestión de contexto.
4. **EJECUTORES:** CCa + CC's + Gemini CLI + Antigravity + Codex CLI — Implementación atómica.

**Principio cardinal:** Montu deja de ser el canal de comunicación entre Claude y los agentes. Clawdio actúa como puente de ejecución. Montu supervisa y valida. Las instrucciones correctivas siempre van de Montu directamente a Claude, nunca mediadas por Clawdio.

---

## FLUJO DE 7 PASOS (v2.0)

### PASO 0 — Carga del Harness [NUEVO en v3.0]
- **Quién:** SessionStart hook de CCa
- **Qué:** Inyectar en contexto el HARNESS.md del proyecto activo + permissions.yml + sección FAILURE_LOG
- **Regla:** Si no existe HARNESS.md para el proyecto → crearlo desde `harness/HARNESS_TEMPLATE.md` antes de continuar
- **Archivo fuente:** `~/MontuMS/harness/[proyecto]/HARNESS.md`

---

### PASO A — Recepción y Clarificación
- **Quién:** Montu (input) + Claude Miaude (recepción)
- **Qué:** Recibir la tarea. Clarificar ambigüedades antes de descomponer.
- **Regla:** Si el objetivo no es claro → preguntar antes de actuar. No asumir.

---

### PASO B — Evaluación de Contexto
- **Quién:** Claude Miaude
- **Qué:** Revisar INVENTARIO_MAESTRO, HARNESS.md activo, historial relevante.
- **Regla:** Nunca ejecutar sin leer el HARNESS.md del proyecto. El contexto correcto evita el 80% de los fallos.

---

### PASO C — Descomposición y Asignación
- **Quién:** Claude Miaude (arquitecto)
- **Qué:** Dividir la tarea en subtareas atómicas. Asignar cada una al ejecutor óptimo.
- **Nota v3.0:** Las subtareas de desarrollo se dividen en D1 (Generator) y D2 (Evaluator). No asignar ambos roles al mismo agente.

**Tabla de asignación de ejecutores:**

| Tipo de tarea | Ejecutor preferente | Alternativa |
|---|---|---|
| Código Python / FastAPI | CCa (serverX) | Gemini CLI |
| Código React / TypeScript | CCa (TO via SSH) | Codex CLI |
| Análisis extenso / logs > 10K | Gemini CLI | Nemotron 3 Super |
| Infra / Docker / SSH | CCa | Clawdio (si automatizado) |
| Evaluación adversarial (D2) | Gemini CLI | CCa en rol evaluador |
| Tareas privadas / sin API | qwen2.5-coder:7b local | Devstral (VPN TO) |

---

### PASO D1 — Ejecución (Generator)
- **Quién:** Ejecutor asignado en PASO C (CCa, Gemini CLI, Codex CLI, etc.)
- **Qué:** Construir la solución bajo las reglas del HARNESS.md activo.
- **Regla:** El Generator NO evalúa su propio output. Eso es rol de D2.
- **Constraint:** Respetar todos los FORBIDDEN_PATTERNS y ARCHITECTURAL_RULES del HARNESS.md activo.

---

### GATE — Verificación de Restricciones [NUEVO en v3.0]
- **Quién:** Claude Miaude (verificación automática)
- **Qué:** ¿El output de D1 viola algún FORBIDDEN_PATTERN o ARCHITECTURAL_RULE del HARNESS.md activo?
  - **Si viola** → retorno a D1 con contexto específico del fallo
  - **Si pasa** → continuar a D2
- **Regla:** El GATE es no-negociable. Ningún output pasa a evaluación sin verificar constraints.

---

### PASO D2 — Evaluación Adversarial (Evaluator) [NUEVO en v3.0]
- **Quién:** Gemini CLI (evaluador preferente)
- **Invocación:** `node ~/.nvm/versions/node/v24.13.0/bin/gemini --skip-trust -p "[prompt evaluador]"`
- **Qué:** Revisar el output de D1 con perspectiva adversarial:
  - **Para código:** verificar tests, imports correctos, linting, ausencia de patrones prohibidos
  - **Para infra:** verificar que comandos no violen permission matrix del HARNESS.md
  - **Para docs:** verificar coherencia con INVENTARIO_MAESTRO y harness activo
- **Resultado posible:**
  - `APRUEBA` → avanzar a PASO E
  - `RECHAZA [motivo específico]` → retorno a D1 con contexto del rechazo
- **Threshold:** Si D2 encuentra fallos → volver a D1. Si aprueba → PASO E.

---

### PASO E — Consolidación y Documentación
- **Quién:** Claude Miaude + Montu (validación)
- **Qué:** Integrar outputs aprobados. Actualizar documentación relevante. Commit si aplica.
- **Regla:** Nunca hacer git push sin revisión explícita de Montu.
- **Entregables mínimos:** código funcional + tests + actualización de INVENTARIO si hay cambio arquitectónico.

---

### PASO F — Harness Update [NUEVO en v3.0]
- **Quién:** Miaude + Montu (validación humana obligatoria)
- **Cuándo:** Tras cualquier sesión donde:
  - D2 encontró fallos
  - Surgió un comportamiento inesperado de agente
  - Se descubrió un patrón de error nuevo
- **Qué:**
  1. Anotar el fallo en FAILURE_LOG del HARNESS.md del proyecto afectado
  2. Proponer nueva entrada en FORBIDDEN_PATTERNS o ARCHITECTURAL_RULES
  3. Montu valida y aprueba la nueva regla
- **Regla Hashimoto:** cada error anotado en FAILURE_LOG DEBE generar una regla que lo haga imposible de repetir. Un error sin regla nueva es una deuda técnica de seguridad.

---

## STACK DE MODELOS (MS v3.0 — Mayo 2026)

| Recurso | Proveedor | Costo | Rol |
|---|---|---|---|
| Claude Sonnet (Desktop/chat) | Anthropic Pro | $20/mes | Arquitecto, RCA, decisiones críticas |
| Claude Code (CCa) | Anthropic Pro | incluido | Ejecutor principal, Generator (D1) |
| Gemini 2.5 Pro (Antigravity/CLI) | Google Pro | $20/mes | Evaluator (D2) + análisis extenso |
| Gemini 2.5 Flash (Clawdio) | Google API | ~$3/mes | Orquestador, SSH, distribución de prompts |
| ChatGPT Pro / Codex CLI | OpenAI Pro | $20/mes | Subgerente secundario, ejecutor Windows/TO |
| Qwen3 Coder 480B:free | OpenRouter | $0 | Coding rutinario, 262K ctx |
| Nemotron 3 Super:free | OpenRouter | $0 | Análisis mixto, 1M ctx |
| qwen2.5-coder:7b (Ollama local) | Local GPU | $0 | Privacidad total, offline |

**Total estimado:** ~$63 USD/mes

---

## REGLAS CARDINALES INAMOVIBLES

1. **Montu no es canal entre agentes.** Clawdio es el puente de ejecución.
2. **Ningún agente hace push a main sin PR y revisión de Montu.**
3. **El HARNESS.md del proyecto activo se carga SIEMPRE al inicio de sesión.**
4. **Cada error en FAILURE_LOG genera una regla nueva. Sin excepción.**
5. **D2 (Evaluator) nunca es el mismo agente que D1 (Generator).**
6. **Correos siempre como borrador. Nunca envío directo desde agentes.**
7. **Clawdio solo vive en serveri3. Jamás levantar en serverX.**

---

## PENDIENTES DE IMPLEMENTACIÓN

- [ ] Implementar handoff_actual.md automático al inicio de sesiones de desarrollo
- [ ] Criterios de asignación ccor4/ccor5 en esta tabla (costo/complejidad)
- [ ] Cron Clawdio Dev: monitoreo cuota semanal Anthropic
- [ ] Automatizar Entropy Scheduler (cuando Clawdio esté estabilizado)
- [ ] PreToolUse hooks en CCa para verificar FORBIDDEN_PATTERNS en tiempo real
- [ ] Evaluar Maestro-Orchestrate para Fase 4

---

**Actualización:** 2026-05-29 — Migración de v1.0 a v2.0 (MS v3.0 Harness Engineering)
