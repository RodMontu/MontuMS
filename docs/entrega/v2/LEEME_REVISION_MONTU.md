# LÉEME — revisión de Montu al despertar (28-09-2026)

**Lee esto primero, 5 minutos.** El resto de la carpeta `v2/` es el detalle si necesitas profundizar.

## Qué hay en la carpeta

Dos procesos escribieron el paquete v2 en paralelo anoche (Manual de Usuario + Guía Rápida + sus verificaciones,
y Manual Técnico + Ficha Técnica + Índice + su verificación). Yo (CCa) hice una **tercera pasada de auditoría
independiente** sobre los 8 documentos: releí el código real en TO, hice consultas en vivo de solo lectura, y
corregí en sitio lo que encontré mal. Detalle completo en `AUDITORIA_v2.md`.

## Veredicto por documento

| Documento | Veredicto |
|---|---|
| Manual de Usuario | **Listo para entrega** |
| Guía Rápida | **Listo para entrega** |
| Manual Técnico | **Listo con reservas** (ver hallazgo 1 abajo) |
| Ficha Técnica | **Listo para entrega** |
| Índice de Entrega | **Listo para entrega** |
| Verificaciones (Usuario/Técnico) | **Listo con reservas**, misma razón que Manual Técnico |
| Capturas Pendientes | **Listo para entrega** (es una lista de tareas, no cambia) |

## Los 8 hallazgos sobre el SISTEMA que deberías conocer

1. **`HARNESS.md` tiene información desactualizada que hizo que el Manual Técnico se equivocara dos veces.**
   Decía que `_BODSUC_MAP` vive en `motor_v2.py` (no es cierto, vive en `database_cubigest.py`) y que el fix de
   reparto en paralelo seguía pendiente (no es cierto, está resuelto desde el 24-09). Si `HARNESS.md` es lo que
   un técnico nuevo o un agente de IA lee antes de tocar código, estos dos errores pueden hacer perder tiempo o
   hacer que alguien "arregle" algo que ya funciona. **Vale la pena actualizar `HARNESS.md` cuanto antes** — no
   lo toqué porque mi tarea era solo la carpeta de documentación, no el repo de TO.

2. **El reparto en paralelo de una serie entre 2+ máquinas ya no existe como auto-split.** Desde el 24-09
   (decisión tuya, commit `313d089`) el Motor solo muestra una alerta con la máquina sugerida; el jefe de planta
   reparte a mano arrastrando. El bug de "mismo operador en 2 máquinas a la vez" que viste el 14-09 está resuelto
   desde antes de eso (commit `0a959e8`). Si en algún reporte o conversación con TO todavía se habla de esto como
   un problema abierto, ya no lo es.

3. **Las corridas automáticas (08:10 Día / 20:10 Noche) no aplican los movimientos manuales ni la asignación
   manual de operadores por jornada** — solo el botón "Reprogramar" lo hace (dos caminos de código distintos).
   *Corrección de Miaude, 28-09 (la versión original de este punto decía que la corrida de las 20:10 borraba lo
   movido durante el día — es falso):* cada corrida solo reescribe el plan de SU turno, así que lo movido en el
   turno Día se conserva a las 20:10. Lo que se pierde es lo hecho ANTES de la corrida del mismo turno (p. ej.
   un ajuste de las 07:45 se pisa a las 08:10). Riesgo real, pero acotado.

4. **Discrepancia de hebras en Calama, a resolver por Montu:** la tabla `hebras` de la base tiene 2 hebras
   configuradas para Carro de Corte (Ø8 a 16) y para EURA 20_2 (Ø10), mientras que lo que Montu ha dicho es que
   Calama trabaja todas sus máquinas a 1 hebra. Una de las dos está mal (la configuración o el dato de contexto), y
   el Motor usa la tabla para estimar duraciones. Ver si se corrige la tabla en el Gestor de Máquinas.

5. **El SPP sí excluye automáticamente una máquina averiada en la corrida automática** (08:10/20:10), no solo
   cuando alguien la mueve a mano. Esto estaba marcado "por confirmar" y ahora está verificado en el código: la
   exclusión vive en la función central de asignación, compartida por el scheduler y el botón manual.

6. **No hay respaldo automatizado de la base SQLite** (`optifierro_v2.db`). Solo copias manuales sueltas hechas
   antes de cambios riesgosos. Es la única fuente de verdad de máquinas, operadores, planes guardados y
   usuarios. Esto ya estaba documentado por el proceso técnico de anoche; lo repito acá porque es de las cosas
   con más impacto si el servidor de TO falla.

7. **La mayoría de las dependencias de Python no están fijadas por versión** en `requirements.txt`. Un rebuild
   futuro (`docker compose build --no-cache`) puede traer versiones distintas sin que nadie lo decida. Bajo
   riesgo hoy, pero crece con el tiempo.

8. **Encontré (y ya redacté) un apellido real de un colaborador** dentro de un nombre de archivo de backup
   citado textualmente en dos documentos técnicos (`optifierro_v2_BACKUP_..._pre_[nombre]_fix.db`). No era
   information sensible del negocio, pero viola la regla de privacidad del proyecto — ya está corregido, no
   requiere que hagas nada, solo que lo sepas por si aparece en otro lugar (el archivo real sigue existiendo con
   ese nombre en el servidor de TO, solo se redactó en la documentación).

## Decisiones que solo tú puedes tomar

1. **¿Actualizamos `HARNESS.md`** para reflejar que `_BODSUC_MAP` vive en `database_cubigest.py` y que el fix de
   reparto en paralelo ya está resuelto? (Recomiendo sí, cuanto antes — es la fuente que usan los agentes de IA.)
2. **¿Unificamos la corrida automática (08:10/20:10) con el botón "Reprogramar"** para que ambas apliquen los
   mismos movimientos manuales y la misma asignación manual de operadores? Hoy son dos caminos de código con
   distinto comportamiento. Es un refactor chico y hoy nadie usa el sistema, así que es buen momento para
   hacerlo (ver la corrección del hallazgo 3: el riesgo real es acotado a ajustes hechos antes de la corrida).
3. **¿Vale la pena pinnear `requirements.txt`** con las versiones reales verificadas (ya están documentadas en
   la Ficha Técnica, listas para copiar)?
4. **¿Se implementa alguna forma de respaldo automatizado** de `optifierro_v2.db`? Hay una recomendación
   concreta y no implementada en el Manual Técnico (tarea programada + `sqlite3 .backup`), solo falta que la
   apruebes.
5. ~~El ribete verde/gris "esSoldable"~~ — **resuelto por Miaude el 28-09**: el código lo define (función
   `esSoldable`, comentario "calidad de acero soldable, sufijo S, ej. A440S, A630S"): ribete verde = acero soldable
   sin urgencia de fecha; gris = no soldable. Ya está en la tabla de colores del Manual de Usuario. Solo confirma si
   te parece correcto que la soldabilidad sea la señal del ribete cuando no hay urgencia de fecha.

## Orden recomendado de lectura

1. Este archivo (ya lo hiciste).
2. `MANUAL_USUARIO_SPP.md` + `GUIA_RAPIDA_JEFE_PLANTA.md` — son los que van a leer los jefes de planta, y son
   los más cortos.
3. `AUDITORIA_v2.md` — el detalle completo de qué se verificó y qué se corrigió, si quieres el rigor completo
   antes de aprobar la entrega.
4. `MANUAL_TECNICO_SPP.md` + `FICHA_TECNICA_SPP.md` — para cuando tengas que hablarle a TI de TO.
5. `INDICE_ENTREGA.md` — al final, tiene la lista de higiene del repositorio (ramas, archivos sueltos) que no es
   urgente pero conviene resolver antes del traspaso formal.
