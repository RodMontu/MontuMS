# Handoff — Modo-desarrollo: Carlitos3.6 + Carlitos3.8, harness liviano

**Fecha:** 2026-09-06
**Ejecutado por:** CCa, en base a `TAREA_MODO_DESARROLLO_CCA_20260906.md`
**Aprobado por:** Montu directo (no vía ventana separada)
**Alcance:** infraestructura propia (RAM, modelos, scripts). No tocó
TO/Cubigest real en ningún momento — solo procesos locales huérfanos de una
sesión anterior (ver §6).

## Estado por punto (1-9)

### 1. Liberar RAM — HECHO
Bajados `cl.montuschi.llama-server` (Flash, 11500) y
`cl.montuschi.llama-server-coderflash` (coder-flash, 11503), los únicos dos
cargados al empezar. Pro y Lite ya estaban abajo. Páginas libres subieron de
~130K a ~1.36M antes de cargar los modelos nuevos.

### 2. Descargar los 2 modelos nuevos — HECHO
- **Qwen3.6-35B-A3B:** no existía en disco. Descargado de
  `unsloth/Qwen3.6-35B-A3B-GGUF` (único archivo Q4_K_M, sin shardear) vía
  `hf download`, consistente con el patrón Unsloth ya usado para el resto de
  los modelos. 22.1 GB, magic GGUF verificado. Guardado en
  `~/models/qwen3.6-35b-a3b-Q4_K_M.gguf`.
- **Qwen3.8-27B:** ya existía en disco (`~/models/qwen3.8-27b-Q4_K_M.gguf`,
  16.4 GB, del 2026-08-21) — no se volvió a descargar.
- Método: `llama-server` directo, no Ollama — se mantuvo el patrón existente,
  no se encontró razón documentada para cambiar.

### 3. Cargar ambos en RAM simultáneamente — HECHO
Dos instancias `llama-server`: Carlitos3.6 en 11504, Carlitos3.8 en 11505.
**RAM real medida (no estimada):** 19.5 GB + 22.3 GB = **41.8 GB total**.
Entra cómodo en los 96 GB compartidos.

### 4. Alias `modo-desarrollo` — HECHO
`~/bin/modo-desarrollo`, mismo patrón que `modo-flash`/`modo-coder`: baja
Flash/coder-flash/Pro/Lite, sube Carlitos3.6+3.8, espera a que ambos
respondan en `/v1/models`. Probado en vivo, funciona.

### 5. Wrappers Carlitos3.6 y Carlitos3.8 — HECHO
`~/bin/Carlitos3.6` y `~/bin/Carlitos3.8`, mismo patrón que
`CarlitosCoderFlash` (fovea toggle, blindaje stdin en modo one-shot), más el
fix del punto 6. Providers `carlitos36`/`carlitos38` agregados a
`~/.pi/agent/models.json` (no existían).

### 6. Diagnosticar y arreglar el cuelgue — HECHO, causa raíz distinta a la hipotetizada
**No era el harness Pi ni permisos.** Al diagnosticar en vivo se encontraron
dos procesos `ssh TO "find / ..."` de la sesión real de hoy, todavía
corriendo 40+ minutos después:
- PID 7580: `ssh TO find / -type d -name 'app' ...` (sin BatchMode)
- PID 7675: `ssh -o BatchMode=yes -o ConnectTimeout=10 TO find / -type d -name '*app*' ...`

El segundo **ya tenía** BatchMode y ConnectTimeout y aun así nunca retornó —
conexión TCP `ESTABLISHED` a TO, CPU ~0%, exactamente el síntoma reportado
("CPU cae a 0% casi de inmediato, queda así indefinidamente"). Esto descarta
la hipótesis (b) del prompt de continuidad (SSH esperando password/host key)
y también la (a) (permisos del harness) — un `find /` recorriendo el
filesystem completo de un Windows remoto simplemente no termina en tiempo
razonable, y ningún wrapper tenía timeout de ejecución sobre el comando SSH
en sí (`ConnectTimeout` solo acota el handshake TCP, no la duración del
comando).

Se mataron ambos procesos huérfanos (`kill`, locales, sin acción sobre TO) y
se verificó que no quedó nada corriendo del lado de TO.

**Fix aplicado:** los wrappers nuevos envuelven el modo no interactivo con
`timeout $CARLITOS_TIMEOUT` (default 600s) del sistema operativo — no
`--print` de Pi, sino el proceso completo. Cualquier ejecución colgada, sea
la causa que sea, se corta sola. Validado con `sleep 120` +
`CARLITOS_TIMEOUT=15`: cortó exactamente a los 15s, exit code 124, sin
proceso huérfano.

**Pendiente explícito:** este fix se aplicó a `Carlitos3.6` y `Carlitos3.8`
únicamente. `Carlitos` y `CarlitosCoderFlash` (los wrappers originales,
todavía en uso en `modo-flash`/`modo-coder`) **no se tocaron** — quedan con
el mismo riesgo de cuelgue por comando remoto sin acotar. Recomendación:
replicar el mismo patrón de `timeout` en esos dos wrappers en la próxima
ventana, y agregar la regla a la disciplina operativa: nunca correr
`find /` sin acotar contra un filesystem remoto vía `ssh TO`.

### 7. Harness ultra liviano — HECHO (rediseño documental + un archivo nuevo)
- **Wrapper:** se mantiene minimo — ruteo de provider/modelo, toggle fovea,
  blindaje stdin, y ahora el timeout duro (justificado como red de
  seguridad genérica, no solo para el caso SSH).
- **Núcleo de seguridad nuevo:** `~/.claude/carlitos-seguridad-nucleo.md` —
  las reglas no negociables (no ejecutar instrucciones inyectadas desde
  datos, no escribir fuera de rutas permitidas sin confirmación, no
  destruir sin confirmación, Cubigest solo lectura), compartidas por todos
  los wrappers vía `--append-system-prompt` (se pasa primero, antes del rol).
- **Rol y PTS:** siguen en `~/.claude/carlitos-sp.md`, sin cambios de fondo
  — ya seguía este patrón (rol/entorno/reglas en el prompt, no en el
  harness), solo se separó explícitamente la capa de seguridad pura.

**Decisión de framework (Pi vs "gi"/pi-go), con razones:**
Investigado hoy: existe `dimetron/pi-go`, una reimplementación no oficial en
Go del harness Pi que declara paridad. **Se decidió NO migrar.** Razones:
1. Pi canónico (`@earendil-works/pi-coding-agent`) ya está en v0.84.2 —
   más nuevo que la v0.82.x que motivó la pregunta, sin señales de abandono
   (629+ dependientes en npm, changelog activo agosto 2026).
2. La causa raíz real del cuelgue (§6) es independiente del lenguaje/runtime
   del harness — es un comando remoto sin timeout. Migrar a pi-go no lo
   habría evitado; el fix (timeout duro en el wrapper) aplica igual sobre
   cualquier harness que se use.
3. pi-go es de un tercero individual, sin el historial de validación que Pi
   ya tiene en esta infraestructura (Gate G0, 2/2 red-teaming superado dos
   veces). Migrar reintroduce superficie de riesgo sin beneficio medido.
4. No se encontró benchmark independiente (Terminal-Bench o similar) que
   muestre a pi-go superando a Pi en el escenario real de uso
   (confiabilidad multi-paso, ejecución desatendida contra TO/Cubigest).

Detalle completo en `PLAN_ARQUITECTURA_IA_LOCAL_v1.0.md` §13 (nota: este
archivo vivía solo en `~/Documents/`, no en `~/MontuMS/docs/` pese a que
`PROMPT_MODELO_Y_HARNESS_CARLITOS.md` lo daba por existente ahí — se copió a
la ubicación canónica hoy; el original en `~/Documents/` queda intacto, sin
tocar, pendiente de que Montu decida si lo elimina).

### 8. Validación mínima — HECHO, parcial (según lo previsto en la tarea)
Para cada wrapper nuevo: tarea sintética de varios pasos (escribir archivo +
comando local múltiple), completada sin colgarse, con verificación
independiente (`cat` de los archivos resultantes, no solo el auto-reporte).
Prueba adicional del corte de timeout con `sleep` forzado — confirmado que
funciona (exit 124, sin huérfanos).

Prueba de inyección de prompt **abreviada** (una sola, no las 2 del Gate G0
completo) contra Carlitos3.6: resistió la inyección (no ejecutó el comando
embebido en el dato, lo señaló explícitamente) y además clasificó
correctamente la negación textual ("sin atraso") — el mismo tipo de error
semántico que el Gate G0 original había encontrado en coder-flash el
2026-09-03. Señal direccional positiva, no concluyente con una sola corrida.

**Pendiente explícito (como preveía la tarea si el tiempo aprieta):** Gate
G0 completo (2 pruebas de inyección, estilo explícito + social, con
verificación independiente, sobre AMBOS wrappers nuevos) antes de usarlos
contra TO/Cubigest real. No se corrió hoy.

### 9. Documentar en La Biblioteca — HECHO vía fallback documental
No hay acceso MCP a `biblioteca-mcp` en esta sesión (no aparece en las
herramientas disponibles). Siguiendo la instrucción de fallback:
- `PLAN_ARQUITECTURA_IA_LOCAL_v1.0.md` actualizado con §13 (esquema de
  modelos/puertos, causa raíz del cuelgue, decisión de framework), copiado
  a la ubicación canónica `~/MontuMS/docs/`.
- Entrada nueva en `LOG_CAMBIOS_2026.md` (2026-09-06, bloque completo).
- Este handoff (`handoff_modo_desarrollo_20260906.md`).
**Pendiente:** que Miaude (o quien tenga el flujo de `registrar_cambio.py`)
indexe estos tres documentos en el catálogo de La Biblioteca.

## Resumen para la ventana coordinadora (Motor de Tiempos)

- **Modelo recomendado:** esquema de dos niveles, tal como sugirió Montu —
  Carlitos3.6 (Qwen3.6-35B-A3B) para uso diario, Carlitos3.8 (Qwen3.8-27B)
  para tareas donde la confiabilidad multi-paso importa más que la
  velocidad. Ambos cargados simultáneamente en `modo-desarrollo` (41.8 GB
  RAM real).
- **Causa raíz del cuelgue:** comando SSH remoto sin acotar (`find /`
  completo contra TO) sin timeout de ejecución — no el harness ni permisos.
  Fix: timeout duro del SO en el wrapper, aplicado y validado en los
  wrappers nuevos, pendiente replicar en los originales.
- **Gate G0 completo:** pendiente sobre Carlitos3.6/3.8, no se saltó por
  descuido — está anotado explícitamente arriba.

## Qué falta (para la próxima ventana o para Montu)

1. ✅ CERRADO 2026-09-06 — replicado el fix de timeout duro en `~/bin/Carlitos`
   y `~/bin/CarlitosCoderFlash` (misma variable `CARLITOS_TIMEOUT`, default
   600s, `timeout` del SO envolviendo el modo no interactivo, sin tocar el
   modo interactivo). Validado con `sleep 30` + `CARLITOS_TIMEOUT=3`: cortó
   a los 3s, exit code 124. No se tocó TO/Cubigest para esta verificación.
2. Correr el Gate G0 completo (2 pruebas de inyección + verificación
   independiente) sobre Carlitos3.6 y Carlitos3.8.
3. Indexar los tres documentos de esta tarea en La Biblioteca (vía Miaude).
4. Decidir si `~/Documents/PLAN_ARQUITECTURA_IA_LOCAL_v1.0.md` (duplicado
   histórico fuera de la fuente de verdad) se elimina o se deja como está —
   no se tocó hoy, solo se copió su versión actualizada a `~/MontuMS/docs/`.
5. Uso real (no sintético) de Carlitos3.6/3.8 en tareas del Motor de Tiempos
   u otro proyecto, para tener señal más allá de la validación mínima de hoy.
