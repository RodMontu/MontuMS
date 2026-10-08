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

## FLUJO DE 7 PASOS (MS v3.0 — Harness Engineering)

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
8. **Antes de tocar código de OptiFierro o de cualquier repo relacionado con TO, y después de cualquier modificación real, se debe consultar/regenerar el grafo de dependencias (Graphify) — ver sección 11.**

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


---

## 10. Protocolo de eficiencia en orquestación por lotes (agregado 2026-09-06, a pedido de Montu)

**Contexto:** con la cadena Miaude → CCa (supervisor) → Carlitos (ejecutor) ya
operativa, Montu identificó un problema de eficiencia: si Miaude lanza una tarea
y luego chequea cada pocos minutos si terminó, se pierde tiempo de ambos lados
sin necesidad.

**Regla:** cuando una tarea se pueda descomponer en varios pasos secuenciales para
CCa/Carlitos, Miaude debe:

1. Encargar **todos los pasos de una vez**, en un solo prompt/lote, de forma que
   al completar un paso el agente avance automáticamente al siguiente — no
   encargar de a un paso por vez esperando confirmación intermedia.
2. Lanzar la tarea, verificar que arrancó bien (no que terminó), y **detenerse**.
3. Al detenerse, decirle a Montu una **estimación de tiempo** razonable antes de
   que valga la pena volver a preguntar/chequear el estado — no dejar que Montu
   tenga que adivinar cuándo volver a consultar, y no generar polling innecesario
   de Miaude hacia CCa/Carlitos tampoco.

**Relación con la jerarquía de supervisión:** Miaude supervisa a CCa, que
supervisa a Carlitos. Por transitividad, Miaude también supervisa a Carlitos,
pero no debería hacerlo de forma directa y continua si CCa ya está en el rol de
supervisor para esa tarea — el chequeo de Miaude es sobre el resultado
consolidado que CCa entrega, no sobre cada paso individual de Carlitos.

Esto no reemplaza la verificación cruzada obligatoria (nunca confiar en el
autoreporte) — solo cambia la *cadencia* de cuándo se verifica, de "cada pocos
minutos" a "cuando la estimación de tiempo indica que ya debería estar listo".


---

## 11. Grafo de dependencias de código (Graphify) — obligatorio antes/después
    de tocar código OF/TO (agregado 2026-09-09, a pedido de Montu)

**Contexto:** la noche del 08-09-2026 se construyó un mapa completo de
dependencias del código de OptiFierro (backend+frontend) y scrap-geovictoria
usando Graphify (tree-sitter, 100% local, sin LLM externo — ninguna línea de
código salió de la máquina). Resultado: 890 nodos combinados, 99% de las
conexiones extraídas de forma determinista (no adivinadas), construido sobre
el commit 7581b9a de optifierro (confirmado como HEAD real de TO al momento
de construirlo). Artefactos en
~/graphify-workspace/{optifierro,scrap-geovictoria}/graphify-out/ y
~/graphify-workspace/merged/ en el Mac Studio. Documentado en La Biblioteca
vía Aurora.

**Regla (obligatoria, no una recomendación):**

1. **Antes** de proponer o ejecutar cualquier cambio de código en OptiFierro
   o en cualquier repositorio relacionado con TO, Miaude y CCa DEBEN
   consultar el grafo vigente para identificar qué otras partes del sistema
   se ven afectadas por el cambio propuesto.
2. **Después** de aplicar cualquier modificación real al código de OF/TO, es
   obligatorio regenerar el grafo antes de cerrar la tarea.
3. El grafo solo se considera vigente si corresponde al commit actual del
   repo. Si el commit cambió desde la última regeneración, tratarlo como
   potencialmente desactualizado hasta confirmarlo (comparar el HEAD real
   contra el commit registrado en la sección "Graph Freshness" de
   GRAPH_REPORT.md).
4. Esta regla se SUMA a la verificación cruzada obligatoria de todo
   autoreporte de agentes — no la reemplaza. Generador≠Evaluador sigue
   aplicando igual al resultado de regenerar el grafo.

**Mecanismo de aplicación (triple capa, redundante a propósito — un solo
lugar se puede olvidar):**
- Project instructions de "Mi TI" en claude.ai (regla #5 de "TUS REGLAS DE
  ORO").
- Este documento (regla #8 de REGLAS CARDINALES INAMOVIBLES, arriba).
- CLAUDE.md del repo optifierro en TO — para que CCa la reciba
  automáticamente al iniciar sesión ahí, sin depender de que el prompt de
  turno la repita.


---

## 12. Territorio de archivos entre ventanas paralelas (agregado 2026-09-14,
    corrige la regla original del 07-09)

**Regla original (07-09-2026):** `backend/routers/programacion.py`,
`backend/routers/tiempos_maquina.py`, `backend/motor_v2.py` y algunos otros
archivos quedaron declarados como territorio exclusivo de la ventana Motor
de Tiempos, para evitar colisiones con la ventana Pendientes-OF.

**Por qué ya no es sostenible tal cual:** desde el 13-09-2026, B1
(Pendientes-OF) necesitó legítimamente modificar `programacion.py` para
wirear `_obtener_pids_pendientes_optisteel` al motor de asignación
(`/api/programacion/generar`). El mismo día, Motor de Tiempos también
necesitó tocar `motor_v2.py` (diámetro en `estimar_duracion_min`). Ambos
cambios eran legítimos y ambos fueron autorizados por Montu paso a paso —
pero la regla de "territorio exclusivo" nunca se actualizó para reflejar
que ahora es territorio compartido. Una ventana (la de esta mañana,
14-09) detectó la colisión potencial y frenó apropiadamente antes de
tocar el archivo sin coordinar — comportamiento correcto, pero evidencia
de que la regla vieja generaba ambigüedad real.

**Regla nueva (reemplaza la exclusividad por coordinación explícita):**

1. `backend/routers/programacion.py` y `backend/motor_v2.py` son
   **territorio compartido** entre Motor de Tiempos y Pendientes-OF —
   ninguna de las dos ventanas es dueña exclusiva.
2. Antes de modificar cualquiera de estos 2 archivos, la ventana que va a
   tocar debe: (a) hacer `git pull` primero para tener el estado real más
   reciente (evita pisar el trabajo de la otra ventana sin saberlo), (b)
   revisar `handoff_actual.md` por si la otra ventana dejó una nota de
   trabajo en curso sobre el mismo archivo, (c) preguntarle a Montu
   explícitamente si la otra ventana está activa en paralelo en este
   momento, antes de proceder si hay cualquier duda.
3. `backend/routers/tiempos_maquina.py`,
   `frontend/.../TiemposPorMaquina.tsx`, `extractor_rutas_v2.py` y los
   scripts de análisis propios (`build_kgshora_referencia.py`,
   `diagnostico_kgshora.py`, `diagnostico_metodologia.py`,
   `run_multi_sucursal.py`) **siguen siendo exclusivos de Motor de
   Tiempos** — no cambia nada ahí.
4. `backend/scraper_cuadroprogramacion.py`, `backend/scraper_optisteel.py`,
   `backend/routers/admin.py` (el endpoint de cuadro-programación) y
   `scrap-geovictoria/scheduler.py` **siguen siendo exclusivos de
   Pendientes-OF**.
5. Cualquier archivo nuevo que ambas ventanas necesiten tocar en el futuro
   sigue este mismo patrón por defecto (compartido + coordinación
   explícita), no se asume exclusividad de entrada.

**Nota sobre el ejemplo real del 13/14-09:** el cruce de esos días no causó
daño — ambos cambios (B1 en `programacion.py`, diámetro en `motor_v2.py`)
tocaron partes distintas del archivo y el merge de git fue limpio sin
conflictos. Pero fue suerte de que no se solaparan las líneas exactas, no
un mecanismo de coordinación real. Esta regla existe para no depender de
esa suerte la próxima vez.
