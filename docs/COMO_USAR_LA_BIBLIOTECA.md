# La Biblioteca — Referencia canónica de uso

**Audiencia:** Miaude (en cualquier chat futuro), Aurora, Rabín, Carlitos, CCa, agy, y cualquier agente nuevo que se sume al ecosistema de Montu. También Montu, si necesita repasar el diseño.

**Última actualización:** 2026-07-21, tras completar la Fase 1 de indexación (403 filas, 12 archivos de MontuMS) y corregir el bug de resúmenes-copiados-de-tablas (55 filas).

---

## 1. Qué es La Biblioteca

Un sistema de catálogo/índice sobre la documentación técnica de MontuMS. No reemplaza los documentos fuente — vive **junto a ellos**, como capa de búsqueda rápida, para que ningún agente (ni Miaude) necesite cargar un archivo completo en contexto solo para encontrar un dato puntual.

Ubicación técnica: `/home/x/MontuMS/biblioteca/` en serverX (192.168.1.111, usuario `x`).

## 2. Principio arquitectónico central: escritura lenta, lectura rápida

Esta separación es la decisión de diseño más importante del sistema, y nunca debe romperse:

- **Escritura (lenta, con criterio):** cuando hay información nueva para archivar, la clasifica y la guarda **la bibliotecaria** — Aurora, para todo lo referente a MontuMS. Ella decide en qué documento y sección va, genera resumen y tags, y confirma la operación.
- **Lectura (rápida, directa, sin LLM de por medio):** cualquier consulta —¿dónde está X?, ¿cuál es la última versión de Y?— se hace **directo contra el catálogo SQLite**, sin invocar a Aurora ni a ningún modelo. Es una búsqueda de milisegundos, no una conversación con un agente.

**Regla dura:** ningún agente debe preguntarle a Aurora "¿dónde está tal cosa?" para una lectura simple. Eso reintroduce exactamente la lentitud que este sistema existe para eliminar.

## 3. Componentes técnicos

| Componente | Ubicación | Función |
|---|---|---|
| `catalogo.db` | `biblioteca/catalogo.db` | SQLite con FTS5. Tablas: `documentos`, `documentos_fts`, `credenciales`, `relaciones`. WAL mode activado (permite lectura/escritura concurrente sin bloqueos). |
| `indexador.py` | `biblioteca/indexador.py` | Escaneo mecánico de archivos `.md` en `MontuMS/` y `MontuMS/docs/`, divide por headers markdown, hace upsert idempotente, limpia filas huérfanas (archivos borrados). |
| `clasificador.py` | `biblioteca/clasificador.py` | Heurística simple de clasificación por palabras clave (tags conocidos del ecosistema). |
| `clasificar_directo.py` | `biblioteca/clasificar_directo.py` | **El método validado para generar resumen+tags.** Llama directo a la API nativa de Ollama (`http://192.168.1.102:11434/api/chat`, modelo `qwen3.6:35b-a3b`) con timeout HTTP obligatorio. Nunca pasa por el bucle agéntico de Claude Code. |
| `mcp_tools/` | `biblioteca/mcp_tools/` | Cuatro funciones: `buscar_tema`, `obtener_ultima_version`, `registrar_cambio`, `buscar_credencial`. |
| `biblioteca-mcp` | contenedor Docker, puerto 8813, path `/mcp` | Servidor MCP dedicado que expone las 4 herramientas para que cualquier agente las consulte sin SSH ni acceso directo al filesystem. |

## 4. Cómo consultar (lectura — el 95% del uso normal)

- **`buscar_tema(query)`** — búsqueda de texto completo (FTS5) sobre archivo, sección, resumen y tags. Uso principal para "¿qué sabemos sobre X?".
  - *Cuidado de sintaxis:* FTS5 interpreta el guion como operador NOT. Buscar `biblioteca-mcp` sin comillas falla; usar `"biblioteca-mcp"` entre comillas.
- **`obtener_ultima_version(archivo, seccion)`** — devuelve la fecha de actualización y el resumen de un documento/sección puntual.
- **`buscar_credencial(query)`** — devuelve **solo metadata** (servicio, variable, archivo `.env`, fecha de rotación). Nunca el valor real de una credencial.

Estas se consultan vía el servidor `biblioteca-mcp` (puerto 8813) cuando hay acceso MCP disponible, o importando `mcp_tools` directo en Python cuando se opera por SSH/Bash.

## 5. Cómo archivar información nueva (escritura — solo vía Aurora)

1. Se le entrega el contenido a Aurora (la bibliotecaria).
2. Aurora clasifica: decide archivo y sección destino en `docs/` (la fuente de verdad — ver sección 7).
3. Para generar el resumen y tags, se usa **`clasificar_directo.py`**, nunca el bucle agéntico completo de Claude Code apuntando a Ollama (ver advertencia crítica abajo).
4. Aurora (o el orquestador que la representa) llama a `registrar_cambio(archivo, seccion, resumen, tags, tipo)` para sincronizar el catálogo.
5. Se verifica con `buscar_tema` que la entrada quedó encontrable.

### Criterio de granularidad (obligatorio)

- Tabla o lista con ítems independientes entre sí → se desglosa en una fila de catálogo por ítem.
- Prosa corrida sobre un solo tema → una sola sección.
- El campo `resumen` **siempre** es una síntesis en prosa. Nunca debe contener una copia literal del contenido original (tablas markdown crudas, etc.) — esto ya causó un bug real (55 filas debieron corregirse) y el prompt de `clasificar_directo.py` ya tiene el guardrail explícito contra esto.

## 6. Advertencia crítica — incidente ya ocurrido, no repetir

Invocar un modelo local (Aurora, Risko, o cualquier otro) **a través del bucle agéntico de Claude Code** (`--model <nombre> --dangerously-skip-permissions`, con `ANTHROPIC_BASE_URL` apuntando a Ollama) para tareas largas y desatendidas **no es confiable**: una sesión así quedó colgada **9+ horas sin producir ningún resultado ni error**, porque esa vía no tiene timeout.

**La arquitectura correcta, ya validada con pruebas reales:** el modelo local se invoca con una llamada HTTP directa a la API nativa de Ollama, con timeout explícito y obligatorio (`clasificar_directo.py` es la referencia). La lectura de archivos y las llamadas a herramientas (`registrar_cambio`, git, etc.) las hace siempre un orquestador confiable (Claude Code con un modelo real de Anthropic — Sonnet, Haiku), nunca el modelo local.

Invocación simple de Aurora para casos puntuales (no bulk): `/Users/montu/bin/aurora "prompt"` — funciona bien para una consulta o archivado puntual, no para cientos de secciones seguidas.

## 7. Fuente de verdad y exclusiones

- **Fuente de verdad de documentos:** `/home/x/MontuMS/docs/`. Los duplicados que existían en la raíz de `MontuMS/` (`INVENTARIO_MAESTRO.md`, `LOG_CAMBIOS_2026.md`) se eliminaron — no deben recrearse ahí.
- **Exclusiones permanentes del índice, nunca tocar ni indexar:**
  - `miau_nube_copia/` (copia histórica, ~12GB)
  - `/mnt/extra/DOCUMENTOS_TECNICOS/` (archivo histórico intocable)
  - `/home/x/.vault/` (bóveda de credenciales)
  - `biblioteca/` no se autoindexa a sí misma.

## 8. Bóveda de credenciales

`/home/x/.vault/` — fuera del árbol de git, permisos 700/600. Un `.env` por servicio. El catálogo (tabla `credenciales`) solo indexa metadata — nunca valores reales. `vault_run.sh` inyecta variables al shell de ejecución sin exponerlas a ningún LLM, incluido Miaude.

## 9. Estado actual (a la fecha de este documento)

403 filas indexadas, cobertura completa de los 12 archivos de documentación de MontuMS. Servidor `biblioteca-mcp` operativo en puerto 8813.

## 10. Proyectos relacionados (no confundir)

- **Contrato de futuro frontend:** ya especificado en `biblioteca/docs/CONTRATO_FUTURO_FRONTEND.md`, para cuando se construya una UI sobre este catálogo.
- **"Risko + OP Risk"**: proyecto hermano en construcción, mismo patrón conceptual (catálogo + bibliotecario) pero para la documentación de OP Risk en Google Drive. Es un sistema **separado**, con su propia infraestructura — no comparte catálogo ni base de datos con La Biblioteca de MontuMS.
