# Plan de Arquitectura de IA Local — Montuschi Consultores SpA
**Versión:** 1.0 — 5 de agosto de 2026
**Destinatario:** Miaude (instancia de implementación) + Montu
**Naturaleza:** Documento de plan. No es ejecución. Todo comando incluido es propuesto, no ejecutado.
**Verificación:** el estado del arte citado en §12 fue verificado por búsqueda web el 2026-08-05.

---

## 0. Resumen ejecutivo — la decisión en una página

El diagnóstico actual apunta al modelo de coding como culpable. **No lo es.** La causa raíz es el *harness*: Claude Code CLI redirigido por `ANTHROPIC_BASE_URL` a Ollama inyecta 21.500–23.000 tokens de system prompt + tool schema en cada turno, con un prefijo que **cambia entre invocaciones**, lo que anula cualquier reutilización de caché KV del servidor local. 102,68 s para responder "OK" no es lentitud del modelo: es reprocesamiento completo de prefill en cada llamada.

Tres cambios estructurales:

| # | Cambio | De | A |
|---|---|---|---|
| 1 | **Harness** | Claude Code CLI vía `ANTHROPIC_BASE_URL` | **Pi** (`pi-coding-agent`, MIT, system prompt < 1.000 tokens, lazy skills) |
| 2 | **Runtime + control de caché** | Ollama (caja negra sobre KV) | **`llama-server`** con `--cache-reuse` + `--slot-save-path` + `/slots` (o LM Studio/MLX como alternativa medida) |
| 3 | **Modelo y política de memoria** | 3 modelos residentes `keep_alive: Forever` (~64 GB de pesos) | **Un solo slot grande** con `Qwen3-Coder-Next 80B-A3B` 4-bit (~46 GB) + un slot chico para el agente conversacional |

**Tesis arquitectónica central:** *el rol pertenece al harness, no al modelo.* Hoy hay un modelo distinto por agente (Carlitos, Aurora, Risko...). Eso es tener tres orquestas afinando en la misma sala para tocar tres partituras. Un solo modelo capaz + tres conjuntos de skills/prompts/herramientas cubre lo mismo con un tercio de la RAM y sin swap.

---

## 1. Supuestos declarados (resueltos por criterio, no consultados)

1. **El Mac Studio sigue siendo también estación de trabajo diaria.** Por eso el techo duro de working set de inferencia se fija en **~62 GB**, no en 90 GB. macOS + navegador + editor + Docker Desktop ocupan 20–30 GB reales.
2. **La "Necesidad B" hoy es laboratorio, mañana es producto.** Se diseña para correr en el hardware del cliente, no en el Mac de Montu. En el Mac convive con A solo en modo demo.
3. **Telegram primero, WhatsApp después.** Telegram Bot API tiene costo cero y cero fricción de aprobación; WhatsApp Cloud API exige WABA propia, plantillas aprobadas y ahora restricciones de contenido para bots de IA. El MVP no debe bloquearse en trámites de Meta.
4. **La P104-100 queda fuera del alcance de inferencia LLM.** Se mantiene el passthrough VFIO. Justificación en §6.
5. **"Absorber trabajo de Claude Code en la nube" ≠ reemplazarlo.** El objetivo medible es desplazar la *ejecución mecánica* (boilerplate, refactor, tests, migraciones repetitivas, documentación), no la arquitectura ni el RCA.
6. Se asume que hay ~120 GB libres en disco para pesos de modelos nuevos. Si no los hay, la Fase 1 se bloquea hasta liberarlos.

---

## 2. RCA — reencuadre del diagnóstico

### 2.1 Los tres fallos son uno solo

| Síntoma observado | Causa aparente | Causa raíz real |
|---|---|---|
| `num_ctx` bajo truncaba el prompt → salida vacía | configuración del modelo | El harness exige ~22K tokens solo para existir |
| 102,68 s en una tarea trivial | modelo lento | Prefijo inestable + invocación aislada ⇒ 0% de cache hit, prefill completo cada turno |
| Terminación silenciosa sin error | bug de Ollama | Claude Code CLI no está diseñado para hablar con un backend que no es la API de Anthropic; los modos de fallo no tienen ruta de reporte |
| El agente de documentación **sí** funciona (74 s en frío) | "ese modelo es mejor" | Tarea de un solo turno, tolerante a 74 s. El mismo defecto está presente; simplemente no duele |

**Conclusión:** el agente de documentación no es contraejemplo, es el mismo sistema roto operando en un régimen donde la latencia no importa. Si se conserva el harness actual, cualquier modelo nuevo heredará el problema.

### 2.2 El fallo de memoria es de política, no de capacidad

91 GB/96 GB en uso con 27 GB en compresor y cientos de swapouts, con tres modelos en `keep_alive: Forever`, uno de ellos huérfano. En un Mac, la RAM unificada es también la VRAM: **el compresor de memoria y el swap compiten con los pesos del modelo por el mismo bus**. Un modelo que swapea no baja un 20% de rendimiento; cae de decenas de tokens/s a unidades.

`keep_alive: -1` en dos o más modelos bloquea la política de evicción LRU de Ollama y garantiza la sobre-suscripción. Es el patrón exacto que hay que erradicar.

### 2.3 El router 9B que mintió sobre su identidad

Un modelo pequeño que fabrica su propia identidad y falla decisiones de delegación no es un modelo mal elegido: es una **decisión de arquitectura equivocada**. El enrutamiento de tareas es una función determinística (reglas, tipo de tarea, presupuesto, disponibilidad). No se delega a un LLM. Ver §3.5.

---

## 3. Necesidad A — Agente técnico de desarrollo

### 3.1 Modelo: Qwen3-Coder-Next 80B-A3B (4-bit)

| Atributo | Valor |
|---|---|
| Arquitectura | MoE híbrida Qwen3Next (Gated DeltaNet + Gated Attention), 512 expertos, ~10 activos |
| Parámetros | 80B totales / ~3B activos por token |
| Contexto nativo | 262.144 tokens (extensible con YaRN) |
| Licencia | Apache 2.0 |
| SWE-bench Verified | ~70,6–71,3% según scaffold (reportado por Qwen / réplicas OpenHands) |
| Huella 4-bit | ~46 GB de pesos (8-bit: ~85 GB → **descartado**, no cabe) |
| Rendimiento esperado M2 Max | 20–30 tok/s de decode a 4-bit (referencia: M3 Max 64 GB, 22–28 tok/s) |

**Por qué este y no el 30B actual:** 3B activos significa que el costo de decode es de un modelo de 3B, mientras la calidad es de gama alta. En un Mac con ancho de banda de memoria limitado (M2 Max ≈ 400 GB/s), MoE de alta dispersión es exactamente la arquitectura correcta: paga en RAM (barata aquí, 96 GB) y ahorra en ancho de banda (caro aquí). Además fue entrenado explícitamente para agentes: tool-calling, horizonte largo y **recuperación tras fallo de ejecución** — la capacidad que decide si un run nocturno termina o se cuelga.

**Riesgo conocido y mitigación:** la arquitectura Qwen3Next es reciente y su soporte en `llama.cpp` recibió correcciones de parsing de tool-calling durante 2026. **Validar tool-calling antes de comprometerse** (Fase 1, criterio de salida). Ruta de respaldo: MLX 4-bit vía `mlx-lm` o LM Studio, donde el soporte de Qwen3-Next es de primera clase en Mac.

**Segundo modelo de respaldo (no simultáneo):** `Qwen3.6 27B` como generalista/refactor si Coder-Next resulta inestable. ~16–18 GB a 4-bit.

### 3.2 Runtime: `llama-server` como primario, MLX como challenger medido

La decisión no es "quién es más rápido" sino **quién me deja controlar la caché**, porque la caché es el problema.

| Runtime | A favor | En contra |
|---|---|---|
| **`llama-server` (llama.cpp)** | `cache_prompt` por defecto; `--cache-reuse` (KV shifting sobre prefijos compartidos); `--cache-ram` y `--cache-idle-slots`; `--slot-save-path` + endpoint `/slots` para **persistir y restaurar sesiones entre procesos**; restauración por similitud LCP visible en logs | 15–50% más lento que MLX en decode; requiere tuning explícito |
| **MLX (mlx-lm / LM Studio)** | 1,4–1,8× más rápido en modelos densos y hasta ~3× en MoE; ~10% menos memoria que GGUF a igual cuantización; soporte nativo de Qwen3-Next | `mlx_lm.server` tiene bug documentado de **contaminación cruzada de KV entre requests concurrentes**; no expone save/restore de slots equivalente |
| **Ollama ≥0.30** | Ergonomía; backend MLX auto-ruteado por formato | Abstrae precisamente los controles que necesitamos; caja negra ante el fallo actual |
| **vLLM en Metal** | PagedAttention, batching real | Soporte Metal inmaduro; reportes de agotamiento de memoria FP16 en contextos largos sobre Apple Silicon. **Descartado para este hardware.** |

**Decisión:** `llama-server` para el agente de coding (sesión larga, un usuario, caché es el cuello de botella). MLX/LM Studio para el agente conversacional (muchos turnos cortos, sin estado largo, throughput manda). Si la medición de Fase 1 muestra que LM Studio 0.4.x ya sostiene prefix caching estable entre turnos, se consolida todo en MLX y se simplifica el stack — **decidir con números, no con preferencia**.

Configuración de arranque propuesta (Mac Studio, zsh, usuario `montu`):

```bash
llama-server \
  --model ~/models/qwen3-coder-next-80b-a3b-Q4_K_M.gguf \
  --host 127.0.0.1 --port 11500 \
  --ctx-size 131072 \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --cache-reuse 256 \
  --slot-save-path ~/llama-slots \
  --parallel 1 \
  --flash-attn \
  --log-file ~/logs/llama-server.log --verbose
```

Notas: `--parallel 1` es deliberado — un solo slot, un solo consumidor, máxima probabilidad de cache hit. `--ctx-size 131072` (no 262K) para acotar la huella de KV; subir solo si una tarea real lo exige. Los flags deben verificarse contra `llama-server --help` de la build instalada; cambian entre releases.

### 3.3 Harness: Pi

`@mariozechner/pi-coding-agent` (org Earendil, MIT, Node ≥22.19).

- **System prompt < 1.000 tokens** contra los 7.000–10.000 de los harness mainstream y los ~22.000 medidos en la configuración actual. Reducción de ~95% del prefill fijo.
- **Lazy skills:** solo la descripción de una línea de cada skill queda residente; las instrucciones completas y los schemas se cargan cuando la skill se invoca. Es lo opuesto a MCP, que precarga todos los schemas al inicio de sesión.
- **4 herramientas core** (read, write, edit, bash) + extensiones en TypeScript.
- **Sesiones en árbol** y compactación de contexto explícita.
- Provider local vía bloque en `~/.pi/agent/models.json` apuntando a un endpoint OpenAI-compatible.

Efecto combinado con `llama-server`: prefijo pequeño **y estable** ⇒ el `cache_prompt` acierta ⇒ el turno N solo procesa el delta. Es la diferencia entre reafinar la orquesta entera en cada compás y solo entrar con el instrumento que cambia.

**Alternativas evaluadas:** OpenCode (el harness genérico dominante, ~165–172k estrellas, más pesado en prompt); Goose (Apache-2.0, ahora bajo Linux Foundation, fuerte en MCP, local-first — **segunda opción real**); OpenHands (sandbox Docker, ideal para runs nocturnos autónomos — candidato de Fase 6 para ejecución desatendida); Aider (git-native, bueno para tareas acotadas); Cline/Kilo (IDE-first).

⚠️ Pi opera en modo "YOLO" por defecto (sin gates de aprobación). Para runs nocturnos sobre repos reales: trabajar siempre en **branch dedicado**, nunca sobre `main`, y con commit automático por paso para poder revertir.

### 3.4 Manejo de contexto y caché entre turnos — la regla dura

**Una sesión = un proceso vivo.** Prohibido el patrón actual de N invocaciones CLI aisladas por turno. Concretamente:

- `llama-server` queda como servicio permanente (launchd), no como proceso por tarea.
- Pi mantiene la sesión abierta; los turnos se agregan al mismo hilo.
- Para tareas desatendidas: usar `pi -p` en modo script contra el mismo servidor, no relanzar el runtime.
- Persistencia entre reinicios: `/slots` save/restore contra `--slot-save-path`.
- **Nada de heredocs largos ni prompts armados inline** — escribir a `/tmp/prompt.txt` y referenciar (patrón ya estándar en esta infraestructura).

**Métrica de aceptación:** TTFT del turno N (N≥2) ≤ 5 s en una sesión con ~30K tokens de historia. Si no se cumple, la caché no está funcionando y no se avanza de fase.

### 3.5 Orquestación y enrutamiento: LiteLLM proxy, determinístico

Una única fachada OpenAI-compatible delante de **todos** los backends: `llama-server` local, LM Studio, OpenRouter, Anthropic.

Beneficios directos sobre los problemas diagnosticados:
- **Observabilidad:** log estructurado de cada request/response, latencia, tokens y errores. Se acaba el fallo silencioso.
- **Timeouts obligatorios por ruta.** Recordatorio del incidente de 9 h colgadas: ninguna llamada a un modelo local puede existir sin timeout explícito.
- **Fallback declarativo:** si el local no responde en X s, escala a OpenRouter. Configuración, no un LLM decidiendo.
- **Presupuesto y contabilidad:** cuánto trabajo se desplazó efectivamente de la nube al local. Ese número es el KPI del proyecto.

**El enrutamiento es una tabla, no un modelo.** El 9B que fabricó identidad queda eliminado del diseño; ningún modelo pequeño decide a quién delegar.

### 3.6 División de roles resultante

| Rol actual | Qué pasa |
|---|---|
| Carlitos (coding) | Se convierte en un perfil de Pi (skills + AGENTS.md) sobre Coder-Next. Nombre se conserva si Montu quiere; es un alias, no un modelo. |
| Aurora (documentación) | Mismo modelo, otras skills. Deja de tener 23 GB residentes propios. Se conserva `clasificar_directo.py` (HTTP directo + timeout) como patrón validado para bulk. |
| dev-tech-lead / implementer / debugger / refactorizador | Colapsan en perfiles de Pi. **Excepción:** `dev-reviewer` conserva un modelo distinto — la segunda opinión pierde valor si viene del mismo modelo. Candidato: Gemma 4 12B o el modelo del slot chico (§4). |
| Rabín (Telegram personal) | Sin cambios en Fase 1–4. Migra al slot chico en Fase 5. |
| Risko / Espinita | Se rediseñan sobre la arquitectura de §4. |

---

## 4. Necesidad B — Agente conversacional de atención

### 4.1 Principio de diseño: el LLM redacta, el sistema decide

Un agente de atención que "entiende y responde" con un LLM suelto es exactamente lo que Meta ya no permite en WhatsApp (política 2026: los bots de IA deben ejecutar tareas de negocio concretas, no ser chatbots abiertos) y lo que la Ley 21.719 vuelve auditable. El diseño correcto es un **pipeline determinístico con el LLM en dos puntos acotados**: comprensión (extracción a JSON) y redacción (con citas a la fuente).

```
Canal (Telegram / WhatsApp Cloud / Web)
        │  webhook
        ▼
[Ingesta]  ── log crudo del payload ANTES de procesar (auditoría + 21.719)
        ▼
[Cola]     ── desacopla el timeout del webhook del tiempo de inferencia
        ▼
[Router determinístico]  ── reglas/intents. Saludo, FAQ exacta, fuera de alcance → sin LLM
        ▼
[RAG]      ── embeddings + reranker sobre el reglamento/base de referencia
        ▼
[LLM]      ── responde SOLO con lo recuperado. Salida estructurada + cita obligatoria.
        ▼
[Validador] ── ¿hay cita? ¿confianza mínima? si no → "no lo sé" + handoff humano
        ▼
[Respuesta + registro de decisión]
```

El **validador** es la pieza que hace vendible esto: un agente que dice "no lo sé" cuando no encontró respaldo vale más comercialmente que uno que improvisa. Y el registro de decisión es evidencia operativa, que es justo lo que la APDP fiscaliza.

### 4.2 Modelo y presupuesto

El slot grande ya reservó ~60 GB. B debe caber en **≤ 12 GB residentes**.

- **Generación:** modelo instruct de 9–12B a 4-bit (~6–8 GB) + KV (~2 GB). Candidatos: **Gemma 4 12B** (destacado por fiabilidad del formato de salida y tool-calling nativo — crítico para salida estructurada) o **Qwen3.5-9B** (razonamiento fuerte para su clase; con contexto amplio rinde por encima de su tamaño).
- **Runtime:** MLX vía LM Studio en modo servidor. Turnos cortos, throughput manda, sin necesidad de slots persistentes.
- **Crítico:** el trabajo pesado lo hace el retriever, no el modelo. Un 9B con el párrafo correcto en contexto supera a un 80B adivinando.

### 4.3 Capa de recuperación (RAG)

| Componente | Elección | Dónde corre |
|---|---|---|
| Embeddings | **BGE-M3** (MIT, 100+ idiomas, denso+sparse híbrido, 8K ctx) — el caballo de batalla self-hosted 2026. Alternativa liviana: `Qwen3-Embedding-0.6B` (~1,5 GB). | serverX, CPU |
| Reranker | `BGE-reranker-v2` — segunda etapa sobre top-100 → top-5 | serverX, CPU |
| Índice | SQLite + FTS5 (ya validado en La Biblioteca) para híbrido léxico, + pgvector si el corpus crece | serverX |

Ojo con las licencias: `jina-embeddings-v3` y `NV-Embed-v2` puntúan alto pero son **CC-BY-NC** — inutilizables en un producto comercial. BGE-M3 (MIT) evita ese problema de raíz.

**Reutilización directa:** el patrón de La Biblioteca (catálogo SQLite + FTS5 + servidor MCP con funciones de búsqueda) es exactamente esta arquitectura aplicada a documentación técnica. El agente de atención es La Biblioteca apuntando al reglamento del cliente en vez de a MontuMS. Eso reduce el trabajo nuevo de forma significativa y ya está probado en producción interna.

### 4.4 Integración de canales

**Telegram (Fase 5, MVP):** Bot API, long polling o webhook detrás del túnel Cloudflare existente. Costo cero, sin aprobaciones. Sirve para validar el pipeline completo con usuarios reales.

**WhatsApp (Fase 6):** **Cloud API oficial de Meta, no bibliotecas no oficiales.** Baileys/WAHA/OpenWA funcionan y son tentadoramente rápidas, pero se basan en el protocolo de WhatsApp Web: riesgo de suspensión del número y — decisivo — **imposible de ofrecer a una empresa que necesita demostrar cumplimiento**. Vender a un cliente de Ley 21.719 un canal que viola los ToS de su proveedor es un contrasentido comercial.

Restricciones verificadas a agosto 2026 que condicionan el diseño:
- Modelo de cobro **por mensaje** (desde julio 2025), no por conversación.
- WABA propia obligatoria; el modelo "On-Behalf-Of" desapareció.
- **Desde el 1 de octubre de 2026**, las respuestas de servicio enviadas por un agente humano o IA de terceros dentro de la ventana de 24 h pasan a ser facturables. **Implicancia de diseño directa: respuestas consolidadas, no ráfagas de burbujas cortas.** Cada burbuja extra será un cargo.
- Webhooks obligatorios; procesamiento asíncrono obligatorio (el timeout del webhook de Meta es más corto que una inferencia local).
- Los bots de IA abiertos ya no son aceptables; el agente debe ejecutar tareas de negocio definidas.

**Handoff humano:** Chatwoot (open source, canal WhatsApp dedicado, bandeja de agentes, asignación por equipo, historial). Es también la base natural para el "asignar el reclamo a quién corresponde" de la visión futura: el LLM extrae y clasifica a JSON, Chatwoot enruta y registra. La decisión sigue siendo del sistema.

### 4.5 Dónde corre cada cosa

| Plano | Nodo | Por qué |
|---|---|---|
| Control (gateway, cola, RAG, Chatwoot, LiteLLM, logs) | **serverX** (Docker) | 24/7, ya expuesto vía Cloudflare Tunnel, sin puertos abiertos (restricción GTD) |
| Inferencia | **Mac Studio** | Único nodo con cómputo real |
| Fuente de verdad documental | Git privado + catálogo SQLite | Ya existente |

El Mac nunca es servidor expuesto: es un backend de inferencia en LAN detrás de LiteLLM.

---

## 5. Presupuesto de memoria — declaración explícita

| Proceso | Reserva | Justificación |
|---|---|---|
| macOS + estación de trabajo | **~28 GB** | Tahoe + navegador + editor + Docker Desktop. No negociable si el Mac sigue siendo el equipo diario. |
| Slot grande — Coder-Next 4-bit | **~46 GB** pesos | Único modelo grande residente |
| KV cache del slot grande (128K, q8_0) | **~10–14 GB** | Estimar empíricamente en Fase 1; la arquitectura híbrida de Qwen3Next reduce la huella respecto de atención plena. Si excede, bajar a 64K. |
| Slot chico — agente conversacional | **~10 GB** | Solo levantado cuando B está en uso o en demo |
| Margen anti-swap | **≥ 8 GB** | El compresor de memoria es la señal de alarma, no el límite |
| **Total pico** | **~92 GB** | ⚠️ Solo si A y B corren simultáneamente. **En operación normal, A o B, no ambos.** |
| **Total operación normal (solo A)** | **~86 GB** | Deja margen real |

**Reglas duras de memoria:**
1. `OLLAMA_MAX_LOADED_MODELS=1` mientras Ollama siga existiendo en la máquina.
2. **Ningún** `keep_alive: -1` / "Forever" en más de un modelo. Preferir `30m` finito.
3. Ningún modelo a 8-bit en este hardware (Coder-Next 8-bit = ~85 GB: no cabe con nada más).
4. Instrumentación permanente: `memory_pressure` y contador de swapouts como healthcheck. Si el compresor pasa de ~10 GB sostenidos, algo se cargó de más.

---

## 6. serverX y la GPU P104-100 — dejarla fuera

**Recomendación: no liberar la P104-100 del passthrough VFIO para este proyecto.**

RCA de la decisión:
- Pascal, compute capability 6.1: **sin soporte real de float16**. Ya obligó a `compute_type=int8` en CTranslate2. Cualquier stack moderno de inferencia asume cc ≥ 7.0.
- 8 GB de VRAM: no aloja ningún modelo relevante de este plan. El más chico útil (12B a 4-bit) ya roza el límite sin contexto.
- El costo de romper el passthrough (reconfigurar VFIO, perder la VM Windows) es real y el beneficio es marginal.

**Lo que sí puede aportar serverX:** todo el plano de control. Docker, cola, Chatwoot, LiteLLM, índice RAG, embeddings en CPU (BGE-M3 corre bien en CPU: 0,3–2 GB), observabilidad, cron nocturno. Ese es su rol correcto en esta topología: no es un nodo de cómputo, es el sistema nervioso.

Reevaluar solo si aparece presupuesto para una GPU NVIDIA moderna (≥24 GB, cc ≥ 8.9) — ese sería un cambio de arquitectura, no un ajuste.

---

## 7. Plan de migración por fases

Cada fase tiene **criterio de salida medible**. No se avanza sin cumplirlo. No se ejecutan dos fases en paralelo.

### Fase 0 — Estabilizar memoria y medir (día 1, ~1 h)
**Qué:** descargar el modelo huérfano; fijar `keep_alive` finito; `OLLAMA_MAX_LOADED_MODELS=1`; instalar instrumentación de memoria y latencia; capturar la **línea base** (los 102,68 s y los 74 s son el punto de comparación).
**Se conserva:** todo lo actual, funcionando.
**Criterio de salida:** memoria en uso < 60 GB en reposo, compresor < 5 GB, swapouts estables durante 30 min de trabajo normal.
**Rollback:** trivial (recargar modelos).

### Fase 1 — Runtime nuevo, sin tocar nada más (día 2–3)
**Qué:** instalar `llama.cpp` (build reciente) y descargar Qwen3-Coder-Next 4-bit. Levantar `llama-server` en el puerto 11500 con la config de §3.2. Ollama sigue vivo en 11434 sin conflicto.
**Criterio de salida — protocolo de benchmark obligatorio:**
1. `curl` directo al endpoint: respuesta válida.
2. **Tool-calling:** 10 llamadas con un schema de herramienta real → ≥9 JSON válidos. *Si falla, cambiar a MLX/LM Studio antes de seguir.*
3. TTFT en frío < 20 s con ~5K tokens de prompt.
4. **TTFT en caliente (segunda llamada, mismo prefijo) < 3 s.** Este es el número que decide el proyecto.
5. Decode ≥ 15 tok/s.
**Rollback:** apagar `llama-server`. Cero impacto.

### Fase 2 — Pi contra el runtime nuevo (día 4–5)
**Qué:** instalar Pi, configurar provider local hacia 11500, escribir el `AGENTS.md` del primer repo de prueba (candidato: un repo interno, **no** OptiFierro).
**Criterio de salida:** una tarea real acotada completada de punta a punta (ej. agregar un endpoint + su test) con TTFT del turno N ≤ 5 s y sin intervención manual.
**Rollback:** volver al flujo actual, que sigue intacto.

### Fase 3 — LiteLLM como fachada única (día 6)
**Qué:** LiteLLM proxy en serverX; todas las rutas (local, OpenRouter, Anthropic) detrás de un endpoint; timeouts explícitos por ruta; log estructurado.
**Criterio de salida:** un backend caído produce un **error visible y logueado**, no una terminación silenciosa. Se prueba apagando `llama-server` a propósito.

### Fase 4 — Corte (semana 2)
**Qué:** migrar Carlitos y Aurora a perfiles de Pi. Apagar Claude Code CLI apuntando a Ollama. Retirar los modelos ahora redundantes (liberar ~40 GB de disco y RAM).
**Criterio de salida:** una semana de trabajo real sin volver al flujo antiguo. **Métrica del proyecto:** % de tareas de ejecución que ya no consumieron cuota de Anthropic.
**Rollback:** los modelos antiguos se conservan en disco hasta cerrar la fase.

### Fase 5 — Necesidad B, MVP en Telegram (semana 3–4)
**Qué:** pipeline completo de §4 sobre un reglamento real (candidato natural: reglamento de copropiedad — reactiva el caso Espinita, que tiene usuario real y baja criticidad). RAG + validador + handoff.
**Criterio de salida:** 20 preguntas reales; ≥16 respondidas correctamente **con cita**; **0 respuestas inventadas** (el validador debe preferir "no lo sé"). Latencia < 8 s.

### Fase 6 — WhatsApp Cloud API (semana 5–6)
**Qué:** WABA, verificación de negocio, plantillas, Chatwoot para handoff. El pipeline ya está probado; esto es solo el canal.
**Criterio de salida:** conversación end-to-end con un usuario externo real.
⚠️ La verificación de negocio de Meta puede tomar días o semanas y **no depende de nosotros**. Iniciar el trámite en la Fase 5, en paralelo, para que no bloquee.

---

## 8. Riesgos y trade-offs — sin maquillaje

| # | Riesgo | Prob. | Impacto | Mitigación |
|---|---|---|---|---|
| R1 | Soporte de Qwen3Next en `llama.cpp` con tool-calling defectuoso | Media | Alto — bloquea la Fase 1 | Criterio de salida explícito en Fase 1; ruta de respaldo MLX/LM Studio ya definida |
| R2 | 20–30 tok/s sigue siendo demasiado lento para trabajo interactivo | **Alta** | Medio | **Aceptarlo honestamente.** El local es para trabajo por lotes y nocturno; lo interactivo sigue en la nube. Prometer paridad de velocidad es mentira. |
| R3 | Pi en modo YOLO daña un repo | Media | Alto | Branch dedicado + commit por paso + jamás sobre `main` ni sobre OptiFierro |
| R4 | Coder-Next queda 6–8 puntos de SWE-bench bajo la frontera → más iteraciones | Alta | Medio | Ese gap es el argumento para reservar la nube a lo difícil, no para abandonar el local |
| R5 | El Mac Studio como estación de trabajo + servidor de inferencia crea contención | Alta | Medio | Presupuesto de §5 con margen anti-swap; a mediano plazo, evaluar un nodo de inferencia dedicado |
| R6 | Meta rechaza o demora la verificación de la WABA | Media | Medio | Telegram es el MVP; WhatsApp es incremental, no bloqueante |
| R7 | Cambio del 1-oct-2026 en WhatsApp encarece conversaciones largas | Alta (es un hecho) | Medio | Diseñar respuestas consolidadas desde el día 1; no burbujas |
| R8 | Sobre-ingeniería: 5 componentes nuevos a la vez | **Alta** — es el riesgo real de este plan | Alto | Fases secuenciales con criterio de salida. Si la Fase 1 falla, no existe Fase 2. |
| R9 | Deuda documental: se implementa y no se registra | Media | Alto | Cada fase cierra con entrada en LOG_CAMBIOS + indexación en La Biblioteca. Sin registro, la fase no está cerrada. |

**El trade-off central, dicho claro:** se cambia velocidad de respuesta por soberanía del dato y costo marginal cero. Para el trabajo de Montu, esto solo se paga si el trabajo desplazado es *tolerante a la latencia*. Si al mes 2 el 80% del trabajo sigue yendo a la nube porque es interactivo, el proyecto falló como herramienta interna — pero **sigue siendo válido como I+D del producto comercial**. Son dos justificaciones distintas y conviene no confundirlas.

---

## 9. Lista negra — qué evitar explícitamente

1. **Claude Code CLI con `ANTHROPIC_BASE_URL` apuntando a un backend local.** Herramienta usada fuera de su diseño, prompt de ~22K tokens por turno, fallo silencioso. Causa raíz de todo lo diagnosticado.
2. **`keep_alive: -1` / "Forever" en más de un modelo simultáneo.** Bloquea la evicción LRU y garantiza swap.
3. **Invocación aislada por turno.** Un proceso nuevo por turno = 0% de cache hit por construcción. Sesión larga o nada.
4. **Un LLM pequeño como router de decisiones.** Ya fabricó identidad y falló delegaciones. El enrutamiento es una tabla de configuración.
5. **Cualquier llamada a un modelo local sin timeout explícito.** El incidente de 9+ horas colgadas sin error ni resultado es el precedente. Timeout obligatorio en toda ruta HTTP.
6. **Bucle agéntico completo para tareas masivas y desatendidas contra modelos locales.** El patrón validado es `clasificar_directo.py`: HTTP directo a la API nativa + timeout, con un orquestador confiable manejando archivos y herramientas.
7. **Ajustar `num_ctx` sin conocer el tamaño real del prompt del harness.** Se corrigió una vez subiendo el contexto; la solución correcta era bajar el prompt.
8. **Cuantización de 8 bits en este hardware.** No cabe.
9. **Bibliotecas no oficiales de WhatsApp (Baileys/WAHA/OpenWA) en cualquier cosa que se muestre o venda a un cliente.** Riesgo de baneo + contradicción con el discurso de cumplimiento.
10. **Modelos de embeddings CC-BY-NC** (`jina-v3`, `NV-Embed-v2`) en el producto comercial.
11. **Un modelo distinto por agente.** El rol es del harness. Tres modelos residentes es como tener tres orquestas para tres partituras.
12. **Cambiar más de una variable por fase.** Sin eso, no hay atribución causal cuando algo mejore o empeore.

---

## 10. Conexión con la ventana comercial (Ley 21.719)

### 10.1 Estado verificado del marco regulatorio (agosto 2026)

- **Ley 21.719** publicada el 13-dic-2024, **entrada en plena vigencia el 1 de diciembre de 2026**. Quedan **~4 meses**.
- Crea la **Agencia de Protección de Datos Personales (APDP)**, ya operativa, con facultades para investigar de oficio, multar, ordenar suspensión de tratamiento y publicar un Registro Nacional de Sanciones.
- Multas hasta **20.000 UTM** o **4% de ingresos anuales** en reincidencia.
- Notificación de brechas a la Agencia en **72 horas**.
- **Ley 21.663** (Ciberseguridad) ya vigente: ANCI, reporte de incidentes en 3 horas para servicios esenciales, multas hasta 40.000 UTM.

**Matiz comercial que hay que decir en voz alta:** durante los primeros 12 meses (1-dic-2026 → 1-dic-2027), las empresas de menor tamaño según Ley 20.416 reciben **amonestación escrita en lugar de multa** por sus primeras infracciones. Esto **debilita el argumento del miedo frente a la PyME**. Consecuencias para la oferta:

- El pitch de "multa inminente" funciona con **empresa mediana/grande**, no con la PyME chica.
- Con la PyME, el argumento debe ser **operativo y competitivo**: "puedes usar IA sobre tus datos de clientes sin que salgan de tu edificio, y sin pagar por token".
- La ventana real de venta con urgencia máxima es **agosto–noviembre 2026**. Después, el mercado se segmenta entre quien ya cumplió y quien está bajo régimen de gracia.

### 10.2 Qué de este plan es demostrable ante un cliente

| Activo demostrable | Fase que lo produce | Fecha realista |
|---|---|---|
| **Demo viva:** "responde sobre tu reglamento interno sin que un solo dato salga del edificio" — Telegram o web, con citas al documento fuente | Fase 5 | **~mediados de septiembre 2026** |
| **Trazabilidad como evidencia:** log de cada consulta, qué documento se citó, qué decidió el sistema. Es literalmente lo que la APDP fiscaliza: evidencia operativa, no políticas | Fases 3 y 5 | septiembre 2026 |
| **Arquitectura de referencia replicable** (documento de diseño + presupuesto de hardware por tamaño de empresa) | Derivado de Fases 1–5 | octubre 2026 |
| **Argumento de costo:** costo marginal por consulta ≈ 0 vs. API por token, con números medidos propios | Fase 4 (métrica del proyecto) | octubre 2026 |
| Canal WhatsApp oficial con handoff humano | Fase 6 | noviembre 2026 |

### 10.3 El argumento que realmente vende

No es "IA local". Es: **"la inferencia ocurre dentro de tu perímetro, por lo tanto no hay transferencia de datos personales a un tercero, por lo tanto ese conjunto de obligaciones simplemente no se te aplica"**. Eso convierte un problema de cumplimiento en un problema de arquitectura — que es exactamente la secuencia metodológica de Montuschi Consultores: visión sistémica → procesos → causa raíz → simplificación → automatización.

Y la credibilidad viene de haberlo hecho primero en casa. Los 102,68 segundos, el swap y el harness equivocado no son vergüenza: **son el material del caso de estudio.** "Así se ve cuando se hace mal, así se corrigió, esto midió antes y después." Ese carrusel se escribe solo.

### 10.4 Riesgo comercial honesto

El cuello de botella de este producto **no es técnico, es de hardware del cliente**. Un Mac Studio de 96 GB o equivalente NVIDIA no es una compra trivial para una PyME chilena. La oferta realista se segmenta:

- **Empresa mediana con datos sensibles** (salud, legal, RRHH, prevención de riesgos → sinergia directa con OP Risk): despliegue on-premise completo. Ticket alto.
- **PyME:** modelo híbrido — clasificación y anonimización local, generación en nube sobre datos ya despersonalizados. Menos puro, mucho más vendible.

Ambos caminos se sostienen sobre la misma arquitectura de este plan. Es una decisión comercial, no técnica.

---

## 11. Bloque para LOG_CAMBIOS (usar al cerrar cada fase)

```markdown
## 2026-XX-XX — [FASE N] Arquitectura IA Local — [título de la fase]

**Nodo:** Mac Studio M2 Max (192.168.1.102) / serverX (192.168.1.111)
**Referencia:** PLAN_ARQUITECTURA_IA_LOCAL_v1.0.md §[sección]

**Cambio realizado:**
- [componente instalado/retirado/configurado, con versión exacta]

**Estado de memoria post-cambio:**
- Modelos residentes: [lista con huella en GB]
- RAM en uso / compresor / swapouts: [valores medidos]

**Criterio de salida de la fase:** [CUMPLIDO / NO CUMPLIDO]
- [métrica]: [valor medido] vs [umbral definido]

**Rollback disponible:** [sí/no — cómo]

**Pendiente que abre:** [BACKLOG-XX si aplica]
```

Bloque para INVENTARIO_MAESTRO (Fase 4, cuando el stack quede en régimen):

```markdown
### Stack de inferencia local — Mac Studio M2 Max
| Componente | Versión | Puerto | Servicio | Huella RAM |
|---|---|---|---|---|
| llama-server (llama.cpp) | [build] | 11500 | launchd `cl.montuschi.llama.server` | ~60 GB |
| Pi coding agent | [versión] | — | CLI, `~/.pi/agent/models.json` | — |
| LiteLLM proxy | [versión] | 4000 | Docker en serverX | — |
| LM Studio (slot chico) | [versión] | 1234 | on-demand | ~10 GB |

**Reglas duras:** un solo modelo grande residente · sin keep_alive infinito · timeout obligatorio en toda ruta.
**Retirado en esta fecha:** Claude Code CLI vía ANTHROPIC_BASE_URL · qwen3-coder:30b · [otros]
```

---

## 12. Fuentes verificadas (consulta web 2026-08-05)

**Runtimes Apple Silicon**
- modelfit.io — MLX vs Ollama Mac 2026 (backend MLX en Ollama ≥0.19, ganancia condicional por arquitectura)
- willitrunai.com — benchmarks MLX vs Ollama, ~10% menos memoria en MLX
- compute-market.com — MLX 30–50% sobre llama.cpp; arXiv:2511.05502
- contracollective.com — MLX vs vLLM en Metal, límites de vLLM sobre Apple Silicon
- github.com/ml-explore/mlx-lm issue #965 — contaminación cruzada de KV en `mlx_lm.server` con concurrencia
- insiderllm.com — Ollama 0.30/0.31, techo de 96 GB del Mac Studio actual
- 7minai.com — flags de reutilización de KV en `llama-server` (`--cache-reuse`, `--slot-save-path`, `/slots`)
- mykolaaleksandrov.dev — caso documentado: prefijo inestable de coding agents ⇒ reprocesamiento completo

**Modelos**
- unsloth.ai/docs — Qwen3-Coder-Next: 46 GB a 4-bit, 85 GB a 8-bit, 256K ctx, fixes de tool-calling
- digitalapplied.com — SWE-bench Verified open-weights 2026; Coder-Next ~71,3% con OpenHands
- atomic.chat, kilo.ai, kdnuggets, openaitoolshub — Qwen3.6 27B, Gemma 4, throughput en Mac
- lmstudio.ai/models/qwen/qwen3-next-80b — soporte Qwen3-Next en Mac vía MLX

**Harness / orquestación**
- tensorlake.ai, byteiota.com, ailearningguides.com, luismori.dev — Pi: system prompt <1K tokens, lazy skills, provider local, modo YOLO
- pinggy.io, openhands.dev, frontman.sh — panorama de agentes CLI open source 2026

**RAG / embeddings**
- premai.io, innovativeais.com, d-central.tech — BGE-M3 (MIT) como workhorse self-hosted; Qwen3-Embedding; licencias CC-BY-NC de jina-v3 y NV-Embed-v2

**Canales**
- chatarmin.com — restricciones 2026 de WhatsApp: WABA propia, webhooks obligatorios, prohibición de chatbots abiertos
- sleekflow.io, setsmart.io, blueticks.co — cobro por mensaje; cambio del 1-oct-2026 sobre respuestas de servicio
- freecodecamp.org, dev.to, serverspace.io — patrones self-hosted (Chatwoot, n8n, WAHA) y sus riesgos

**Marco regulatorio Chile**
- preyproject.com, anami.cl, xmslatam.com, yourdevs.net, asentic.cl — Ley 21.719: vigencia 1-dic-2026, APDP operativa, 20.000 UTM / 4%, 72 h de notificación, régimen de amonestación para PyMEs dic-2026→dic-2027

---

## 13. Modo-desarrollo — Carlitos3.6 + Carlitos3.8 (2026-09-06)

**Contexto:** Carlitos (`CarlitosCoderFlash`, coder-flash 30B-A3B) se colgó 2/2 veces
en tareas de varios pasos el 2026-09-06. Ver
`PROMPT_MODELO_Y_HARNESS_CARLITOS.md`, `handoff_modo_desarrollo_20260906.md`
(handoff de esta tarea) y `LOG_CAMBIOS_2026.md` para el detalle completo.

### 13.1 Esquema de modelos/puertos — nuevo modo `modo-desarrollo`

| Modo | Puertos activos | Modelos | Wrapper Carlitos |
|---|---|---|---|
| `modo-flash` (default) | 11500 (Flash) + 11503 (coder-flash) | Qwen3-30B-A3B / Qwen3-Coder-30B-A3B | `CarlitosCoderFlash` |
| `modo-coder` | 11501 (Pro) + 11502 (Lite) | Qwen3-Coder-Next-80B-A3B / gpt-oss-20B | `Carlitos` |
| **`modo-desarrollo` (nuevo)** | **11504 (Carlitos3.6) + 11505 (Carlitos3.8)** | **Qwen3.6-35B-A3B (MoE, reemplazo directo de coder-flash) / Qwen3.8-27B (denso, "Pro" de confiabilidad multi-paso)** | **`Carlitos3.6` / `Carlitos3.8`** |

Archivos: `~/models/qwen3.6-35b-a3b-Q4_K_M.gguf` (Unsloth GGUF, 22.1 GB en
disco), `~/models/qwen3.8-27b-Q4_K_M.gguf` (16.4 GB, ya existía en disco desde
el 2026-08-21). Plists: `cl.montuschi.llama-server-carlitos36.plist`,
`cl.montuschi.llama-server-carlitos38.plist`. Providers Pi:
`carlitos36`/`carlitos38` en `~/.pi/agent/models.json`.

**RAM real medida con ambos simultáneos (no estimada):** 19.5 GB
(Carlitos3.6) + 22.3 GB (Carlitos3.8) = **41.8 GB total**, dentro del
presupuesto de §5, con margen amplio sobre los 96 GB compartidos.

### 13.2 Causa raíz real del cuelgue — no era el harness

La hipótesis inicial (permisos de Pi / SSH sin BatchMode) **se descartó por
evidencia directa**: al diagnosticar en vivo se encontraron dos procesos
`ssh TO "find / ..."` de la sesión real del incidente, todavía corriendo
40+ minutos después — uno de ellos **ya tenía** `-o BatchMode=yes -o
ConnectTimeout=10` y de todas formas nunca retornó (conexión TCP
`ESTABLISHED`, CPU ~0%). Causa raíz real: **un `find /` sin acotar contra el
filesystem remoto de TO (Windows) que nunca termina** — no hay timeout que
limite la duración del comando remoto en sí, solo el handshake de conexión.
Coincide exactamente con el síntoma reportado ("CPU cae a 0% casi de
inmediato, queda así indefinidamente").

**Fix aplicado (`Carlitos3.6`, `Carlitos3.8`, pendiente replicar en
`Carlitos`/`CarlitosCoderFlash`):** el wrapper envuelve el modo no
interactivo (`--print`) con `timeout` duro del sistema operativo
(`CARLITOS_TIMEOUT`, default 600 s). Cualquier ejecución colgada —sea por
SSH, por un comando local, o por cualquier causa no anticipada— se corta
sola. Validado en vivo: `sleep 120` con `CARLITOS_TIMEOUT=15` cortó a los
15 s exactos, exit code 124, sin proceso huérfano. El modo interactivo (sin
argumentos, humano presente) no lleva timeout.

Regla de diseño que se agrega a la lista negra (§9): **ningún comando SSH
remoto sobre TO debe recorrer el filesystem completo sin acotar
(`find /`)** — acotar siempre a un subdirectorio conocido, y preferir que el
timeout duro del wrapper sea la última red de seguridad, no la primera línea
de defensa.

### 13.3 Harness: se mantiene Pi, no se migra a "gi"/pi-go

Investigado 2026-09-06: existe un reimplementación no oficial en Go del
harness Pi (`dimetron/pi-go` en GitHub, terceros, no el proyecto canónico de
Earendil Works) que declara paridad de funcionalidad. **Decisión: no
migrar.**

Razones:
1. Pi (canónico, `@earendil-works/pi-coding-agent`) ya está en v0.84.2,
   más nuevo que la v0.82.x referenciada como "actual" — no hay urgencia de
   actualizar ni de migrar de stack.
2. La causa raíz del cuelgue (§13.2) es independiente del runtime/lenguaje
   del harness — es un comando remoto sin timeout. Migrar a pi-go no la
   habría evitado; el fix real (timeout duro en el wrapper) aplica igual
   sobre cualquier harness.
3. `pi-go` es un proyecto de un tercero individual, sin el historial de
   validación que Pi ya tiene en esta infraestructura (Gate G0, 2/2 pruebas
   de red-teaming superadas dos veces — ver `handoff_carlitos_harness_
   2026-09-03.md`). Cambiar de runtime reintroduce superficie de riesgo sin
   beneficio medido para el caso de uso real (ejecución no interactiva
   confiable contra TO/Cubigest).
4. No se encontró benchmark independiente que muestre a pi-go superando a
   Pi en confiabilidad o en el escenario real (tareas multi-paso,
   ejecución desatendida) — la "paridad declarada" es una afirmación del
   propio proyecto alternativo, no verificada por terceros.

### 13.4 Harness liviano — dónde vive cada cosa

- **Wrapper (`~/bin/Carlitos*`):** ruteo de provider/modelo, toggle de
  fovea, blindaje de stdin en modo one-shot, y ahora el timeout duro. Nada
  de rol, entorno, ni reglas de negocio.
- **Núcleo de seguridad (`~/.claude/carlitos-seguridad-nucleo.md`, nuevo):**
  compartido por todos los wrappers vía `--append-system-prompt`. Solo lo
  no negociable — no ejecutar instrucciones inyectadas desde datos, no
  escribir fuera de rutas permitidas sin confirmación, no borrar/destruir
  sin confirmación, Cubigest solo lectura.
- **Rol y reglas de PTS (`~/.claude/carlitos-sp.md`, existente, sin
  cambios de fondo):** identidad, convenciones de código, protocolo de
  Cubigest en detalle. Se sigue pasando como segundo
  `--append-system-prompt`, después del núcleo de seguridad.

---

*Fin del plan. Documento vivo: actualizar al cierre de cada fase con los números medidos, que reemplazan a las estimaciones de §5 y §8.*
