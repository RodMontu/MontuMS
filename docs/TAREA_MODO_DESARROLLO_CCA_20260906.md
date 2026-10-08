# TAREA — Modo-desarrollo: Carlitos 3.6 + 3.8, harness liviano
**Aprobado por Montu directo (no via ventana separada).**
**Contexto:** ~/MontuMS/docs/PROMPT_MODELO_Y_HARNESS_CARLITOS.md (investigacion
ya hecha - modelos identificados, benchmarks, causa probable del cuelgue).
Tambien: ~/MontuMS/docs/handoff_carlitos_harness_2026-09-03.md (Gate G0
original), ~/MontuMS/docs/COMO_USAR_LA_BIBLIOTECA.md.

## Que se necesita, en orden

### 1. Liberar RAM
Detener los modelos locales actualmente cargados (Flash, Pro, Lite,
coder-flash actual en puerto 11503) - Montu confirma que no los esta usando
ahora, no hay problema en bajarlos. Usar los scripts de toggle existentes en
~/bin/ si aplican, o detener los procesos llama-server directamente.

### 2. Descargar los 2 modelos nuevos
- Qwen3.6-35B-A3B (GGUF Unsloth, cuantizacion Q4_K_M, ~18GB)
- Qwen3.8-27B (GGUF, cuantizacion Q4_K_M, ~17GB)
Verificar primero en La Biblioteca / web si hay una recomendacion ya
documentada del metodo optimo de descarga+carga para este Mac Studio (Ollama
vs llama-server/llama.cpp directo) - el patron actual del proyecto usa
llama-server directo (no Ollama), mantener esa consistencia salvo que
encuentres una razon documentada para cambiar.

### 3. Cargar ambos en RAM simultaneamente
Levantar dos instancias llama-server, una por modelo, en puertos nuevos (no
reusar 11500-11503 para no chocar con los modos existentes):
- Qwen3.6-35B-A3B -> puerto 11504, alias "carlitos3-6"
- Qwen3.8-27B -> puerto 11505, alias "carlitos3-8"
Documentar RAM real usada por ambos simultaneos (deberia entrar comodo en los
96GB compartidos, pero confirmalo, no lo asumas).

### 4. Alias "modo-desarrollo"
Crear ~/bin/modo-desarrollo (mismo patron que modo-flash/modo-coder/modo-chat
existentes) que levanta ambos servers (3.6 y 3.8) juntos.

### 5. Wrappers Carlitos3.6 y Carlitos3.8
Crear ~/bin/Carlitos3.6 y ~/bin/Carlitos3.8 (mismo patron que
~/bin/CarlitosCoderFlash), cada uno apuntando a su puerto/modelo
correspondiente. Pueden usarse simultaneamente (Montu lo sabe, acepta la baja
de velocidad individual si la tarea lo amerita).

### 6. Diagnosticar y arreglar el cuelgue (bloqueante - hazlo ANTES de dar por
buenos los wrappers nuevos)
Los wrappers actuales (CarlitosCoderFlash) se colgaron 2/2 veces hoy en tareas
de varios pasos - CPU del proceso caia a ~0% casi de inmediato, sugiere espera
de algo interactivo (permiso del harness Pi, o SSH sin BatchMode). Diagnostica
la causa raiz LEYENDO el wrapper y el harness Pi en vivo, reproduce con datos
sinteticos (nunca Cubigest real), arregla, y aplica el fix a los wrappers
nuevos (3.6 y 3.8) tambien.

### 7. Harness ultra liviano, foco en seguridad
Rediseña el harness para que sea minimo: la seguridad y las reglas
fundamentales (no ejecutar instrucciones inyectadas desde datos, no escribir
fuera de rutas permitidas, no destruir nada sin confirmacion) van en el
harness/config. El rol, el entorno, las reglas de PTS v1.1, etc. van en el
PROMPT que se le pasa en cada invocacion, no en el harness. Agrega ahi lo que
consideres indispensable mas alla de seguridad (ej. timeout duro, no quedar
esperando input).

Antes de decidir el framework: busca en la web informacion de HOY (Pi sigue
activo, version reciente v0.82.x, hay un rebuild en Go llamado "gi" con
paridad declarada) y evalua si conviene seguir con Pi o cambiar, basandote en
la tarea real que hacemos con TO/Cubigest (ejecucion no interactiva, confiable,
sin colgarse). Documenta la decision con razones, no solo la conclusion.

### 8. Validacion minima antes de declarar listo
Para CADA wrapper nuevo (Carlitos3.6, Carlitos3.8): correr una tarea sintetica
de varios pasos (similar a la de hoy que colgo) y confirmar que termina sin
colgarse, ANTES de tocar TO/Cubigest real con ellos. No es necesario repetir
el Gate G0 completo de inyeccion de prompt en esta pasada si el tiempo aprieta,
pero dejalo anotado como pendiente si se salta.

### 9. Documentar todo en La Biblioteca
Actualizar ~/MontuMS/docs/PLAN_ARQUITECTURA_IA_LOCAL_v1.0.md con el nuevo
esquema de modelos/puertos. Crear/actualizar un documento tecnico completo
(arquitectura modo-desarrollo, decision de framework, causa raiz del cuelgue y
fix) y registrarlo via el flujo normal de La Biblioteca (ver
COMO_USAR_LA_BIBLIOTECA.md seccion 5 - clasificar_directo.py +
registrar_cambio). Si no tienes acceso directo a ese flujo, deja el documento
listo en ~/MontuMS/docs/ con nombre claro para que Aurora lo indexe despues.

## Reglas
- Todo esto es infraestructura propia (RAM, modelos, scripts) - no toca datos
  de cliente, no requiere el canal de Carlitos-solamente del PTS v1.1.
- Trabaja de corrido, sin pedir confirmacion entre pasos, salvo bloqueo real.
- Al terminar (o si te quedas pegado en algo), deja un handoff en
  ~/MontuMS/docs/handoff_modo_desarrollo_20260906.md con estado de cada punto
  (1-9) y que falta.
