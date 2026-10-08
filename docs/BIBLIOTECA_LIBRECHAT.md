# La Biblioteca — RAG + Skill en LibreChat (ia.montuschi.cl)

**Fecha:** 2026-08-28 / 2026-08-29
**Estado:** Conectado y verificado end-to-end.

## 1. Propósito

Habilitar consulta y archivado de La Biblioteca (catalogo SQLite+FTS5 de
MontuMS) desde LibreChat, para que Montu pueda: (a) preguntar por
documentacion tecnica/historial de proyectos directo en el chat, y (b)
entregar bloques de actualizacion de documentacion (LOG_CAMBIOS,
INVENTARIO_MAESTRO) y que el modelo local los archive el mismo, siguiendo el
mismo protocolo de clasificacion que ya regia para Aurora/Miaude.

Guia usada: la conexion ya existente de `risko-rag-mcp` a LibreChat (ver
`RISKO_LIBRECHAT_GOOGLE_WORKSPACE.md`), que resulto tener dos diferencias de
implementacion no evidentes hasta que se probo end-to-end (ver seccion 3).

## 2. Cambios aplicados

- `/srv/librechat/librechat.yaml` (backup `.bak.20260828233915`): nueva
  entrada `mcpServers.biblioteca` (`streamable-http`,
  `http://192.168.1.111:8813/mcp`, timeout 60000) + `192.168.1.111:8813`
  agregado a `mcpSettings.allowedAddresses`.
- `/srv/librechat/skill/biblioteca/SKILL.md` (deployment skill, se carga
  solo via `DEPLOYMENT_SKILLS_DIR` default `./skill` -> `/app/skill`, ya
  bind-mounteado en el compose base). Cubre: protocolo de lectura sin
  friccion (`buscar_tema`, `obtener_ultima_version`, `buscar_credencial`) y
  protocolo estricto de escritura (`registrar_cambio`): clasificar antes de
  escribir, granularidad, resumen siempre en prosa original, confirmacion
  explicita de Montu antes de escribir, verificacion posterior con
  `buscar_tema`.
- `/home/x/ws/biblioteca-mcp/app.py` (backup `.bak.20260828234400`): agregado
  `TransportSecuritySettings(enable_dns_rebinding_protection=False)` al
  constructor de `FastMCP` (ver RCA 3.1).
- `/home/x/ws/biblioteca-mcp/requirements.txt`: pin `mcp[cli]==1.28.1` (antes
  sin pin) (ver RCA 3.2).
- `/home/x/MontuMS/docs/COMO_USAR_LA_BIBLIOTECA.md` (backup
  `.bak.20260828235700`): seccion 5 actualizada para reflejar que Aurora fue
  descontinuada el 2026-08-25 (ver hallazgo en seccion 4) y que el skill de
  LibreChat es ahora un escritor autorizado explicitamente por Montu.

## 3. RCA — dos problemas reales, ninguno parcheado a ciegas

### 3.1 `421 Invalid Host header` al conectar LibreChat a biblioteca-mcp

Sintoma: LibreChat reportaba `fetch failed` al conectar
`http://192.168.1.111:8813/mcp`; `curl` directo devolvia
`421 Misdirected Request` / `Invalid Host header`. Causa raiz: el SDK de MCP
(`mcp.server.transport_security`) trae proteccion DNS-rebinding activa por
defecto, que rechaza el header `Host: 192.168.1.111:8813` al no reconocerlo
como local. `risko-rag-mcp/app.py` ya tenia el fix aplicado
(`enable_dns_rebinding_protection=False`) — `biblioteca-mcp/app.py` no lo
tenia, porque nunca antes se habia conectado un cliente externo (solo Jan
via `mcp-remote`, que no impone ese header). Fix: mismo patron que
risko-rag-mcp.

### 3.2 `ModuleNotFoundError: mcp.server.fastmcp` tras el rebuild

Al reconstruir `biblioteca-mcp` con `--no-cache` para aplicar el fix 3.1, el
build fallo: `requirements.txt` no fijaba version de `mcp[cli]`, y el
`pip install` sin cache resolvio `mcp` 2.x (renombro `FastMCP` a
`MCPServer`). La imagen vieja (built hace ~4 semanas) tenia cacheado
`mcp==1.28.1` sin que nadie lo hubiera fijado explicitamente — quedo
expuesto recien al forzar `--no-cache`. `risko-rag-mcp/requirements.txt` si
fija `mcp[cli]==1.28.1`. Fix: mismo pin aplicado a biblioteca-mcp.

## 4. Hallazgo colateral — Aurora descontinuada (2026-08-25)

El docstring de `registrar_cambio.py` (fecha 2026-08-25) declara que Aurora
dejo de usarse como agente por quedar colgada sin salida, y que desde
entonces Miaude escribe directo al catalogo; ningun otro agente puede
llamar `registrar_cambio` sin autorizacion explicita de Montu.
`COMO_USAR_LA_BIBLIOTECA.md` (ultima actualizacion 2026-07-21) segia
describiendo a Aurora como bibliotecaria activa — desactualizado desde
antes de esta sesion. Corregido en el mismo commit de esta sesion (ver
seccion 2).

## 5. Verificacion end-to-end

- `curl http://192.168.1.111:8813/healthz` -> `{"ok":true}`.
- `POST /mcp` `initialize` (protocolo 2025-06-18) -> `200 OK`,
  `serverInfo.name: "biblioteca"`.
- Logs de `LibreChat` tras restart:
  `[MCP][biblioteca] Tools: buscar_tema, obtener_ultima_version,
  registrar_cambio, buscar_credencial` — conexion limpia, sin reintentos.
- `[deploymentSkills] Loaded 1 deployment skill(s) from /app/skill` — sin
  errores de frontmatter (se corrigieron dos: un `:` sin comillas en
  `description` rompia el parser YAML).

## 6. Pendiente (Montu)

- En la UI de LibreChat: activar el MCP server `biblioteca` y el skill
  `biblioteca` en el Agent que se vaya a usar para esto (Agent Builder ->
  Tools / Skills).
- Decidir si el gateo de escritura actual (skill exige confirmacion
  explicita de Montu en el chat antes de llamar `registrar_cambio`) es
  suficiente, o si se prefiere un paso adicional fuera de LibreChat.

## 7. Aurora — Agente de LibreChat (redefinición 2026-08-29)

Aurora fue redefinida como Agente de LibreChat (ia.montuschi.cl), de uso
exclusivo de Montu. Su rol pasó a ser doble: consulta directa a La
Biblioteca y procesamiento de bloques técnicos para archivado bajo
protocolo estricto, dejando atrás su rol previo como agente CLI
descontinuado el 2026-08-25. Configuración actual: modelo
qwen3-30b-a3b-flash (proveedor Mac-Flash), temperatura 0.3, tokens de
salida máximos en 4096. El skill 'biblioteca' quedó con always-apply
activo, sin depender de que el modelo decida invocarlo cada turno.

Prueba end-to-end de esta misma sesión: Aurora preguntó correctamente
archivo/sección antes de escribir (regla 1 del protocolo), no copió el
bloque literal (regla 3), y usó `buscar_tema` para verificar tras escribir
(regla 6) — pero su primer intento de verificación reveló un bug real en
`buscar_tema.py` (ver sección 8).

## 8. RCA — `buscar_tema` rompía con títulos de sección puntuados

Síntoma: Aurora, al verificar con `buscar_tema` usando el título literal de
la sección 7 (con paréntesis, guion largo y fecha con guiones), recibió
errores de sintaxis repetidos en `documentos_fts`, y solo obtuvo resultado
al caer a palabras sueltas sin puntuación. Causa raíz: `buscar_tema.py`
pasaba el `query` crudo, sin sanitizar, directo a `MATCH ?` — cualquier
guion, paréntesis o número-con-guion en la entrada se interpreta como
sintaxis de FTS5 (NOT, agrupación), no como texto literal. No era un
problema de "fechas" ni de un caso puntual: cualquier título de sección con
puntuación iba a fallar, para cualquier agente, indefinidamente.

Fix: `_sanitizar_query_fts()` en `buscar_tema.py` extrae solo tokens de
palabra (`\w+`) del query de entrada antes de pasarlo a FTS5, descartando
todo carácter especial. Verificado con 5 casos: el título literal de la
sección 7 completo (con paréntesis/guiones/fecha), `biblioteca-mcp` sin
comillas (el caso ya documentado), palabras sueltas, query vacío, y query
de puro ruido de puntuación — los 5 responden correctamente, sin error.
La recomendación de "usar comillas para términos con guion" en
`COMO_USAR_LA_BIBLIOTECA.md` y en el skill `biblioteca` queda obsoleta:
`buscar_tema` ahora acepta cualquier texto natural sin que el llamador deba
recordar reglas de escapado.

## 9. Brecha arquitectónica encontrada — `registrar_cambio` no escribe al archivo real

Al registrar la sección 7, Aurora escribió correctamente al catálogo — pero
`registrar_cambio` **solo hace INSERT/UPDATE en `documentos` (SQLite)**;
nunca toca el `.md` real en `docs/`. El archivo quedó terminando en la
sección 6 hasta que Miaude agregó manualmente la sección 7 más abajo en
esta misma edición. Esto significa que, tal como está hoy, cualquier
"archivado" que haga Aurora (o cualquier agente) vía `registrar_cambio` crea
metadata de catálogo — resumen y tags buscables — pero **no el contenido
real en el archivo fuente de verdad**. Hasta ahora esto no era visible
porque quien llamaba `registrar_cambio` (Miaude) siempre escribía el
archivo real por separado, en el mismo turno, antes de sincronizar el
catálogo. Aurora no tiene esa capacidad — sus únicas herramientas son las
4 del MCP `biblioteca`, ninguna de las cuales escribe al filesystem.

Pendiente de decisión (Montu): si el objetivo es que Aurora archive de
punta a punta sin que Miaude tenga que cerrar la brecha después, hace falta
una quinta herramienta en `biblioteca-mcp` (p. ej. `escribir_seccion`) que
además de sincronizar el catálogo, escriba o actualice la sección
correspondiente en el `.md` real. Alternativa más simple: Aurora
archiva solo metadata de catálogo (uso actual), y el contenido completo del
bloque técnico queda en el historial de chat de LibreChat, no en el
archivo — pero esto contradice el principio de "`docs/` es la fuente de
verdad" ya establecido.
