# ESTADO ACTUAL — Sistema Planificador de la Producción (SPP)
**Última actualización:** 2026-09-23

**Este archivo YA NO es la fuente de verdad del backlog.** Quedó
desactualizado desde el 15-09; el 22 y 23 de septiembre se generó un
backlog mucho más rico (B32-B44 y correcciones a B1-B31) y un Plan de
Trabajo activo para la entrega. **Para todo lo pendiente, prioridades y
el Plan de Trabajo vigente: leer `pendientes_sistema_planificador.md`
— ese es ahora el documento principal de coordinación.**

Este archivo conserva solo referencia ESTABLE que no cambia con el
backlog: mapeo de sucursales, trampas conocidas de código, protocolo de
territorio compartido, y reglas duras.

## Mapeo de sucursales (referencia rápida, ya confirmado, no reabrir)
| Sucursal  | SQLite OptiFierro | Cubigest SQL Server |
|-----------|-------------------|----------------------|
| Calama    | 1                 | 1                    |
| Cerrillos | 10                | 4                    |
| Coronel   | 14                | 14                   |

TOSOL queda SIEMPRE fuera de alcance (posible futura 4ta sucursal — el
campo `sucursales_permitidas` de usuarios ya está diseñado para incluirla
automáticamente sin migración, si el valor es `null`=Todas). "Vista Clara"
= nombre alternativo de Cerrillos — mismo lugar.

## Territorio de archivos entre ventanas — REFORZADO 23-09

`backend/routers/programacion.py` y `backend/motor_v2.py` son territorio
COMPARTIDO: `git pull` + revisar diff real + confirmar con Montu antes de
tocar. Esto ya era regla desde antes — **ahora es crítico**, porque a
partir del 23-09 el Plan de Trabajo se ejecuta con MÚLTIPLES ventanas y
agentes en paralelo (CCa, Carlitos, Gemini Desktop + Antigravity, y
potencialmente otros), coordinados desde la ventana "Coordinación entrega
final SPP". Riesgo real detectado el 22-09: dos sesiones distintas
trabajando la misma mañana sobre Programación sin saberlo entre sí
(resultó ser secuencial, no conflicto — pero pudo no serlo).

**Regla dura nueva:** ninguna ventana secundaria edita `programacion.py`
ni `motor_v2.py` sin que la ventana Coordinadora lo sepa y lo autorice
explícitamente para ESE momento — aunque el archivo esté "libre" según
git. Si dos fases del Plan de Trabajo tocan estos archivos, se
SERIALIZAN (una termina, comitea con diff+confirmación, recién ahí
empieza la siguiente) — nunca en paralelo real sobre el mismo archivo.
Detalle completo: `REGLAS_CARDINALES_FLUJO_ORQUESTADO.md`, sección 12.

## Trampas conocidas (ver HARNESS.md FORBIDDEN_PATTERNS para el detalle)
- FP: sumar "multi-máquina" por lote subestima la cifra real.
- FP: código Cubigest de sucursal ≠ código SQLite — verificar siempre.
- FP: un commit en `~/graphify-workspace/` no llega a producción solo por
  existir en git — falta `git pull` + rebuild en TO.
- FP-010: `ServerX-Home/stack/optifierro_v2_frontend` es un worktree roto
  y abandonado — NO es el flujo de desarrollo real.
- FP-011: `git status` de `~/graphify-workspace/` puede verse "sucio" solo
  por desactualización — sincronizar antes de diagnosticar algo raro.
- FP-012: `fecha_fin` top-level de una tarea con `reparto[]` puede
  pertenecer a OTRA máquina — usar siempre `reparto[]` para detalle real.
- AR-009: un operador puede calificar para 2+ máquinas, pero solo trabajo
  asignado en UNA a la vez — nunca simultáneo, ningún camino del motor.

## Reglas duras que nunca cambian
- Cubigest: SOLO LECTURA, siempre, sin excepción.
- Nunca `git commit`/`push` sin mostrar diff y confirmación de Montu.
- Consultar/regenerar grafo Graphify antes y después de tocar código de
  OF/TO (regla AR-008 / sección 11 de REGLAS_CARDINALES).
- Login/autenticación: si un sub-agente (CCa) se detiene por precaución
  legítima, no insistir reformulando — ejecutar directo cuando Montu
  autoriza en la propia conversación.
- Agentes nuevos en el equipo (Gemini/Antigravity, Qwen, DeepSeek,
  ChatGPT/Codex) NO conocen estas reglas por repetición como CCa/Carlitos
  — deben recibirlas explícitas en cada prompt que se les entregue.
