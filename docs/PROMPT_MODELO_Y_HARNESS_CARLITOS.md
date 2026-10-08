# PROMPT DE CONTINUIDAD — Modelo + Harness de Carlitos
**Fecha:** 2026-09-06
**Origen:** ventana coordinadora del Motor de Tiempos (Prompt 4), desviada para no
perder foco de esa tarea.
**Rol a asumir:** Mi TI. Tuteo chileno, RCA antes de parche, par intelectual.
**Objetivo de esta ventana:** decidir si conviene cambiar el modelo detrás de
Carlitos (coder-flash), y diagnosticar/arreglar por qué el harness se cuelga en
tareas de varios pasos.

---

## 1. Contexto — por qué se abre esta ventana

Durante el trabajo del Motor de Tiempos (ver `~/MontuMS/docs/handoff_actual.md` y
`bitacora_accesos_torres_ocaranza.md`, entradas 2026-09-06), Carlitos
(`~/bin/CarlitosCoderFlash`, modelo actual **Qwen3-Coder-30B-A3B-Instruct**,
puerto 11503) se colgó **dos veces consecutivas** al recibir una tarea de varios
pasos (escribir script, copiarlo a TO, ejecutarlo, guardar resultado, reportar
agregados). Ambos cuelgues con firma idéntica: CPU del proceso `pi` cae a ~0%
casi de inmediato y se queda así indefinidamente — no es lentitud de inferencia
(eso mostraría CPU alto), es un bloqueo real, probablemente esperando algo
interactivo que nunca llega (ej. un prompt de SSH, host key, o confirmación de
permisos del harness Pi).

Verificado en ambos cuelgues: **cero riesgo para Cubigest** — se confirmó por
SSH que no había ningún proceso Python corriendo dentro del contenedor
`optifierro-backend`, es decir, el cuelgue ocurre ANTES de tocar la base de
datos del cliente, en el harness local mismo.
## 2. Lo que ya se investigó (no repetir desde cero)

**Identidad confirmada de coder-flash (en vivo, vía `/v1/models` y `/props` del
servidor llama.cpp en 192.168.1.102:11503):**
- Modelo: `Qwen3-Coder-30B-A3B-Instruct`
- 30.532.122.624 parámetros totales (~30.5B, ~3.3B activos, MoE)
- Contexto nativo 262K, entrenado con vocab Qwen (151.936 tokens)
- Archivo: `/Users/montu/models/coder-flash-Q4_K_M.gguf`, quant Unsloth Q4_K_M

**Investigación web ya hecha (2026-09-06) sobre alternativas — resumen, no
repetir la búsqueda desde cero, sí profundizar donde falte:**

| Modelo | Arquitectura | Terminal-Bench | SWE-bench Pro | IFBench | Nota |
|---|---|---|---|---|---|
| Qwen3-Coder-30B-A3B (actual) | MoE, 3.3B activos | no encontrado | no encontrado | no encontrado | Foco: coding/agéntico general, sin dato de confiabilidad de instrucción |
| **Qwen3.6-35B-A3B** (16-abr-2026) | MoE, 3B activos, 256 expertos | 51.5 (v2.0) | 49.5 | no encontrado | Candidato a reemplazo directo de coder-flash — misma familia MoE, generación más nueva |
| **Qwen3.8-27B** (dense, ~ago-2026) | Denso, 27B activos siempre | **73.0** (v2.1) | **61.7** | **79.5** | Descripción textual: "designed to carry complex, multi-step tasks through to completion with greater reliability" — apunta directo al síntoma del cuelgue |

**No se encontró** un benchmark cabeza a cabeza entre Qwen3-Coder-30B-A3B y
estos dos candidatos en las mismas pruebas — la comparación de arriba es
direccional (generación más nueva + foco explícito en confiabilidad), no una
cifra de mejora exacta. **Esto es lo primero que esta ventana debería intentar
cerrar**, si hay forma de encontrar un benchmark más directo.

**Requisitos de hardware ya verificados por búsqueda (no verificado en el Mac
Studio real todavía):** Qwen3.8-27B en Q4 necesita ~24GB (ajustado) en Apple
Silicon; Qwen3.6-35B-A3B en Q4 corre en ~18-23GB. El Mac Studio tiene 96GB
compartida — debería entrar cualquiera de los dos sin problema, pero falta
confirmar que no choque con los otros modelos ya cargados (Flash, Pro,
coder-flash actual) según el modo activo (`modo-flash`/`modo-coder`/`modo-chat`
en `~/bin/`).
## 3. Qué debe resolver esta ventana

### 3.1 Decisión de modelo
1. Buscar si existe un benchmark más directo Qwen3-Coder-30B-A3B vs
   Qwen3.6-35B-A3B vs Qwen3.8-27B en instruction-following/agentic-reliability
   (IFBench, Terminal-Bench, o similar) — la tabla de arriba tiene huecos.
2. Confirmar disponibilidad de los GGUF (Unsloth u otro) y tamaño exacto de
   descarga para ambos candidatos.
3. Evaluar la estrategia de dos niveles que sugirió Montu: Qwen3.6-35B-A3B como
   reemplazo de coder-flash (uso diario, rápido), Qwen3.8-27B como modelo
   "Pro" — más lento, reservado para tareas donde la confiabilidad de completar
   instrucciones de varios pasos importa más que la velocidad (exactamente el
   tipo de tarea que se colgó hoy).
4. Decidir y documentar en `~/MontuMS/docs/PLAN_ARQUITECTURA_IA_LOCAL_v1.0.md`
   (ya existe, ver Fase 4 pendiente) qué modelo(s) se descargan y en qué puerto.

### 3.2 Diagnóstico y fix del harness
1. Leer en vivo `~/bin/CarlitosCoderFlash` completo (no asumir el contenido —
   ya se hizo esto el 2026-09-03 para el Gate G0, pero antes del cuelgue de hoy,
   así que puede haber cambiado o el gate no cubrió este escenario).
2. Reproducir el cuelgue con **datos sintéticos**, nunca con Cubigest real — el
   Gate G0 (`handoff_carlitos_harness_2026-09-03.md`) ya estableció el patrón de
   testing aislado, reutilizarlo. Tarea de prueba sugerida: pedirle a Carlitos
   una tarea de 3-4 pasos que incluya escribir un archivo local + un SSH
   `ConnectTimeout`/`BatchMode` a un host cualquiera (puede ser localhost o un
   host de prueba), para aislar si el cuelgue es del SSH específicamente o de
   cualquier tarea multi-paso.
3. Hipótesis a probar, en orden de probabilidad: (a) el wrapper no pasa un flag
   equivalente a `--dangerously-skip-permissions` de Claude Code, y el harness
   Pi se queda esperando una confirmación de permisos que nunca llega en modo
   no interactivo; (b) el SSH sin `-o BatchMode=yes` se cuelga esperando una
   contraseña o confirmación de host key; (c) algo del tamaño/complejidad del
   prompt de tarea causa un problema de generación en el modelo mismo
   (verificar si el cuelgue ocurre incluso con un prompt mínimo).
4. Una vez resuelto: correr de nuevo el Gate G0 completo (sección 4 de
   `handoff_carlitos_harness_2026-09-03.md`) antes de declarar apto para
   producción — no asumir que el fix del cuelgue no rompió nada de la
   resistencia a inyección ya validada.
## 4. Regla de eficiencia de tokens (nueva, aplicar en esta ventana también)

Montu está repartiendo cuota de tokens entre esta ventana y otra en paralelo.
**Todo lanzamiento y espera de Carlitos en esta ventana debe hacerse a través de
CCa** (que corre con credenciales de Pecas, cuenta secundaria — tokens
separados), no directo por esta ventana. Esta ventana planifica, CCa ejecuta y
supervisa, y reporta solo el veredicto final — mismo patrón recién adoptado en
la ventana del Motor de Tiempos.

## 5. Qué NO hacer en esta ventana

- No tocar Cubigest ni TO real — todo el testing de harness es con datos
  sintéticos, aislado, como el Gate G0 original.
- No cambiar el modelo en producción (puerto 11503, usado por el Motor de
  Tiempos ahora mismo en la otra ventana) sin que esta ventana entregue un
  veredicto claro y Montu lo confirme.
- No declarar "listo" sin volver a correr el Gate G0 completo.

## 6. Cierre de esta ventana

Al terminar, entregar a Montu un resumen para traer de vuelta a la ventana del
Motor de Tiempos: modelo recomendado (o los dos, en el esquema de dos niveles),
causa raíz del cuelgue y su fix, y resultado del Gate G0 re-ejecutado.
