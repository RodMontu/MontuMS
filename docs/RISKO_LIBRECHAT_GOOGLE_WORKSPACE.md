# RISKO — Chat IA Local (LibreChat) + RAG OP Risk + Google Workspace

**Fecha:** 2026-08-24 / 2026-08-25
**Estado:** Fase A+B completadas y verificadas. Fase C (workspaces Familia/OP Risk, cuentas de Yerko/Chepu/Pecas) pendiente.

## 1. Propósito

Reemplazar el concepto de Risko (Hermes Agent, Telegram) por un chat web con LLMs locales del Mac Studio, con rol de asistente personal: acceso a Gmail/Calendar/Drive/Docs/Sheets/Slides/Tasks por persona, y al RAG de OP Risk. Uso previsto: tareas lineales diarias (agendar, revisar correo, redactar borradores, consultar RAG) — no análisis pesado de documentos (para eso siguen las IA de pago).

## 2. Decisión de arquitectura: LibreChat vs AnythingLLM vs Jan

| App | Rol final | Motivo |
|---|---|---|
| **LibreChat** | Elegida como base para "Familia" y "OP Risk" | Única con OAuth 2.1 nativo **por usuario** para Google Workspace. Login con Google de fábrica (primera cuenta registrada = admin). RBAC granular vía Admin Panel (roles custom, ACL por recurso). |
| **AnythingLLM** | Se mantiene en producción para Pecas (ver INVENTARIO_MAESTRO, entrada 2026-08-23) | Bloqueada estructuralmente para Google-por-persona: su MCP es global a la instancia (issue #3855 del repo, abierto desde mayo 2025, sin resolver). Más simple operativamente, sigue siendo la opción correcta para casos de un solo usuario/cuenta compartida. |
| **Jan** | Uso personal de Montu, fuera del alcance compartido | No se ajusta a multiusuario/Google Workspace, preferencia personal de Montu. |

Ambas plataformas (LibreChat, AnythingLLM) tuvieron CVEs críticos reales en 2026. Los de LibreChat se concentraron en MCP (RCE root, robo de credenciales, bypass de permisos) — parchados antes de 0.8.4. Instancia desplegada: **0.8.7**, ya parchada. Requiere vigilancia continua dado que MCP es la pieza más usada acá.
## 3. Infraestructura desplegada — LibreChat en serverX

**Ubicación:** `/srv/librechat/` en serverX (192.168.1.111, usuario `x`).
**Acceso actual:** `http://192.168.1.111:3080` (LAN only, sin Cloudflare para el chat en sí). Admin panel: `http://192.168.1.111:3000`.
**Cuenta admin:** rodrigo@montuschi.cl (primera cuenta registrada = admin automático en LibreChat).

### Contenedores (docker compose, proyecto `librechat`)

| Contenedor | Imagen | Función |
|---|---|---|
| `LibreChat` (servicio `api`) | `registry.librechat.ai/danny-avila/librechat:latest` | Backend + frontend |
| `admin-panel` | `registry.librechat.ai/clickhouse/librechat-admin-panel:latest` | Usuarios, roles, config |
| `chat-mongodb` | `mongo:8.0.20` | Usuarios, conversaciones |
| `chat-meilisearch` | `getmeili/meilisearch:v1.35.1` | Búsqueda (no activada, `SEARCH=false`) |
| `vectordb` | `pgvector/pgvector:0.8.0-pg15-trixie` | Vector DB para RAG nativo de LibreChat |
| `rag_api` | `registry.librechat.ai/danny-avila/librechat-rag-api-dev-lite:latest` | File Search / Upload as Text |
| `google-workspace-mcp` | `google-workspace-mcp:local` (build propio de `taylorwilsdon/google_workspace_mcp`) | Conector MCP Google, puerto 8815 |

### Modelos conectados (endpoints custom → Mac Studio)

- **Mac-Flash**: `http://192.168.1.102:11500/v1` — `qwen3-30b-a3b-flash`. Verificado funcionando end-to-end.
- **Mac-Pro**: `http://192.168.1.102:11501/v1` — `qwen3-coder-next-80b-a3b`. Proceso manual, no siempre activo, no bloqueante.

### Archivos clave (con backups con timestamp antes de cada edición)

- `/srv/librechat/librechat.yaml` — endpoints, mcpServers, mcpSettings
- `/srv/librechat/docker-compose.override.yml` — servicio google-workspace-mcp
- `/srv/librechat/.env` — secretos (JWT, CREDS_KEY/IV, MEILI_MASTER_KEY, credenciales Google OAuth)
- `/srv/google-workspace-mcp/` — repo clonado, imagen construida localmente
- `/srv/google-workspace-mcp/credentials/` — tokens OAuth persistidos (bind mount, UID 1000)
## 4. Conexiones MCP activas

### 4.1 RAG de OP Risk (`risko-rag-mcp`)

Ya existía en serverX antes de esta sesión (puerto 8814), en uso por Jan desde el Mac Studio. No se creó nada nuevo — solo se conectó a LibreChat. Endpoint: `http://192.168.1.111:8814/mcp` (streamable-http). **Estado: conectado y verificado.** Herramienta expuesta: `consultar_rag_op_risk`.

### 4.2 Google Workspace (cuenta rodrigo@montuschi.cl)

Servidor MCP propio (`taylorwilsdon/google_workspace_mcp`), desplegado esta sesión. Cubre Gmail, Calendar, Drive, Docs, Sheets, Slides, Tasks (120+ herramientas en el proyecto original). Servidor arriba y registrado correctamente como "requiere OAuth" — falta que Montu complete la autorización desde la interfaz de LibreChat.

**Decisión sobre múltiples cuentas Google:** conectar simultáneamente 3 cuentas (personal, montuschi.cl, oprisk.cl) en una sola instancia de este MCP no es confiable — hay reportes documentados de que el parámetro de cuenta se ignora y ambas llamadas devuelven datos de la misma cuenta. Se empieza solo con rodrigo@montuschi.cl. oprisk.cl, Pecas y la cuenta personal se agregan más adelante como conexiones separadas y nombradas.

### 4.3 Credenciales OAuth generadas (Google Cloud Console)

- **Proyecto GCP:** `Clawdio-Mail-Service` (existente, reutilizado — el cliente OAuth creado es nuevo y separado del que ya usa Clawdio para su propio Gmail).
- **Tipo de cliente:** Aplicación web.
- **Client ID:** `650446401695-f3vsnjrj73m2565c7b057qk07t4p36gi.apps.googleusercontent.com`
- **Client Secret:** en `/srv/librechat/.env` (serverX) — no se documenta el valor aquí. Copias en el Mac: `/Users/montu/Documents/client_secret_650446401695-f3vsnjrj73m2565c7b057qk07t4p36gi.apps.googleusercontent.com.json` y `/Users/montu/Documents/OAuth_montuschi_LibreChat.md`.
- **Pantalla de consentimiento:** Interno (montuschi.cl es Google Workspace) — evita verificación externa de Google.
- **APIs habilitadas:** Gmail, Calendar, Drive, Docs, Sheets, Slides, Tasks API.
- **Redirect URI:** `https://gauth.montuschi.cl/oauth2callback` (Google rechaza IPs privadas para clientes "Aplicación web").

## 5. Cloudflare Tunnel — cambio de infraestructura

Nuevo ingress en `/srv/cloudflared/config.yml` (backup con timestamp antes de editar):

```yaml
# LibreChat -- Google Workspace MCP OAuth callback (serverX docker, puerto 8815)
- hostname: gauth.montuschi.cl
  service: http://192.168.1.111:8815
```

Validado (`tunnel ingress validate` → OK) y reiniciado. Túnel reconectó con 3 conexiones activas.

**Pendiente (Montu):** registro DNS CNAME para `gauth.montuschi.cl` en Cloudflare. Y política de Access (Zero Trust): dos aplicaciones — `gauth.montuschi.cl/oauth2callback*` con Bypass (Everyone), y `gauth.montuschi.cl` (resto) con Allow restringido a `@montuschi.cl`. Necesario para no dejar el servidor MCP completamente expuesto a internet.
## 6. Problemas reales encontrados y su causa raíz (RCA)

Ninguno se resolvió a ciegas — cada uno con causa raíz confirmada antes del fix:

1. **`mkdir /srv/librechat`: permiso denegado.** `/srv/` es de root; requiere `sudo mkdir` + `chown` (mismo patrón que `/srv/web` y `/srv/cloudflared`).
2. **Mongo y Meilisearch en crash-loop.** Docker crea los directorios de datos bind-mounted como root en el primer arranque; los contenedores corren como usuario no-root. Fix: `chown` de esos directorios.
3. **Contenedor `LibreChat` con red vacía (`Networks: {}`) reproducible.** Causa: `docker-compose.override.yml` declaraba `ports:` para `api`, y Compose concatena (no reemplaza) listas `ports:` entre base y override — dos bindings del mismo puerto compitiendo. Fix: se sacó el `ports:` del override.
4. **`librechat.yaml` fallaba su propio schema** (`models.default` no puede ser array vacío aunque `fetch: true` esté activo). Fix: ID real del modelo Flash confirmado contra el propio llama-server.
5. **Error `400 unsupported content[].type`** al adjuntar un PDF. Causa: llama-server no entiende archivos nativos (solo texto), LibreChat intentó mandar el PDF como adjunto multimodal. Fix de uso: elegir "Upload as Text" al adjuntar. Pendiente forzar esto por config en fase posterior.
6. **Bloqueo SSRF de LibreChat** contra IPs/hosts privados (`192.168.1.111:8814` y `google-workspace-mcp:8815`) — bloqueo por defecto de destinos de red privada para MCP. Fix: agregados a `mcpSettings.allowedAddresses` en `librechat.yaml`.
7. **Permisos del directorio de credenciales de Google** — mismo patrón que el punto 2, en el volumen de `google-workspace-mcp`. Fix: volumen nombrado → bind mount en `/srv/google-workspace-mcp/credentials`, `chown` a UID 1000 (usuario `app` del contenedor).
8. **Detección automática de OAuth fallida** — LibreChat concluyó erróneamente que el servidor "no usa OAuth" y trató el 401 como falla dura. Fix: `requiresOAuth: true` explícito (práctica recomendada por LibreChat en vez de confiar en auto-detección).
9. **Redirect URI rechazada por Google** (`192.168.1.111` no es TLD público válido). Fix: subdominio real `gauth.montuschi.cl` — Google solo valida sintaxis del dominio, no que esté resuelto al momento del registro.
10. **Fallo transitorio de cloudflared al reiniciar** (precheck de red falló una vez). Se recuperó solo en el reintento automático — no relacionado a los cambios de esta sesión.

**Aprendizaje transversal:** cada invocación de CCa vía `claude -p` es una sesión nueva, sin memoria de invocaciones anteriores. Un prompt que asume continuidad ("ya hiciste X") es tratado por CCa igual que una instrucción narrada por un tercero — y CCa se negó a actuar sobre esa base, correctamente. Toda delegación futura a CCa debe ser una tarea completa y autocontenida, nunca asumiendo sesión previa.

## 7. Pendientes

- Montu: DNS CNAME para `gauth.montuschi.cl` + las dos aplicaciones de Cloudflare Access (sección 5).
- Montu: completar autorización OAuth de Google Workspace desde la interfaz de LibreChat.
- Crear workspaces/Agents "Familia" (Pecas + Montu) y "OP Risk" (Yerko + Chepu + Montu) — una vez validada la conexión de Google.
- Conectar cuentas de Yerko, Chepu y Pecas (conexiones separadas y nombradas — límite de una cuenta por instancia del MCP).
- Evaluar conexión de Gmail personal de Montu y de rmontuschi@oprisk.cl (separadas, no unificadas).
- Forzar por config que Mac-Flash/Mac-Pro solo ofrezcan "Upload as Text"/"Search", nunca archivo nativo (no son modelos con visión).
- Personalización visual (logo, colores) y evaluación de extender LibreChat con módulos propios (Kanban, calendario, recordatorios) — viable técnicamente, pendiente decisión de negocio.
- Verificar si el bug de RAG-compartido-en-Agent (#8322, repo LibreChat) sigue vigente en 0.8.7 antes de confiar en RAG compartido para OP Risk.

## 8. Sesión 2026-08-25 (noche) — Jan conectado, swap de ia.montuschi.cl, cuenta de Pecas

**Jan → Google Workspace:** agregado como servidor MCP en `mcp_config.json` de Jan (Mac Studio), mismo patrón `mcp-remote` que ya usa risko-rag: `npx -y mcp-remote http://192.168.1.111:8815/mcp --allow-http`. Comparte el mismo servidor y las mismas credenciales que LibreChat — no es una instancia nueva.

**`ia.montuschi.cl`: de AnythingLLM a LibreChat.** Se decidió migrar también a Pecas a LibreChat (deja de ser AnythingLLM-only). Cambio de ingress en `/srv/cloudflared/config.yml`: el hostname ahora apunta a `http://localhost:3080` (LibreChat) en vez de `http://localhost:3001` (AnythingLLM). AnythingLLM **no se eliminó** — sigue corriendo puertas adentro (solo LAN) como red de contención hasta confirmar que Pecas está cómoda en LibreChat.

**Cuenta de Pecas creada en LibreChat:** email `rivera.melgarejo@gmail.com`, usuario `pecas`, vía el script `config/create-user.js` del propio contenedor (no por autoregistro). Contraseña temporal generada y entregada a Montu por canal separado (no queda documentada acá).

**`ALLOW_REGISTRATION` pasado a `false`:** con el dominio ya público apuntando a LibreChat, se cerró el autoregistro abierto — de ahora en más los usuarios se crean explícitamente.

**Hallazgo importante (RCA, no ejecutado todavía):** el directorio `/srv/google-workspace-mcp/credentials/` está vacío — nadie completó nunca el consentimiento real de OAuth con Google, ni desde LibreChat ni desde Jan. Los logs del contenedor muestran intentos de conexión reales desde el Mac Studio (192.168.1.102) recibiendo `401` y hacienda correctamente el descubrimiento de endpoints OAuth — el cableado funciona, falta el paso humano de autorización. Como LibreChat y Jan comparten el mismo servidor y las mismas credenciales, autorizar una sola vez (desde cualquiera de las dos apps) destraba a ambas. Pendiente: DNS CNAME de `gauth.montuschi.cl` + verificar las 2 Aplicaciones de Access + completar el consentimiento desde la UI de LibreChat.

**Pecas — Google Workspace personal:** no tiene cuenta en el Workspace de montuschi.cl (no amerita el costo por asiento todavía). Usa su Gmail personal; Montu tiene acceso a esa cuenta y podría replicar el mismo trabajo de conexión MCP para ella — explícitamente diferido, no para esta sesión.

## 9. Sesión 2026-08-26 — Mac-GPTOSS conectado como modelo de respaldo en LibreChat, Jan y Rabín

**Contexto:** gpt-oss-20b ya venía corriendo persistente en el Mac Studio (puerto
11502, LaunchAgent con `RunAtLoad`/`KeepAlive`, activado en una sesión anterior
nunca documentada — ver `MODELOS_CONVERSACIONALES_CANDIDATOS.md` para el detalle
completo de esa activación). Esta sesión lo conectó como modelo de respaldo/alternativa
liviana en las tres aplicaciones que ya usan Flash/Pro, siempre disponible
independientemente del toggle `modo-carlitos`/`modo-normal` — útil sobre todo cuando
Pro está cargado en RAM y deja poco margen.

**LibreChat:** nuevo endpoint custom **Mac-GPTOSS** agregado en `/srv/librechat/librechat.yaml`
(serverX), mismo patrón que Mac-Flash/Mac-Pro (ver sección 3), `baseURL:
http://192.168.1.102:11502/v1`. Contenedor `api` recreado para tomar el config nuevo.
Verificado con `curl` contra el endpoint: `HTTP 200`, sin errores.

**Jan (Mac Studio):** nuevo provider `llama_server_gptoss` agregado en `settings.json`,
mismo patrón que el provider `llama_server_local` ya existente para Flash/Pro,
`base_url: http://127.0.0.1:11502/v1`. **Pendiente, no crítico:** requiere reiniciar
Jan para que el provider aparezca en el selector de modelos — no se reinició en esta
sesión.

**Rabín (Hermes, perfil `default` en serverX, `/home/x/.hermes/config.yaml`):**
agregado como **primer** ítem de `fallback_providers` — antes de los dos existentes
(`deepseek/deepseek-v4-flash` y `nvidia/nemotron-3-super-120b-a12b:free`, ambos vía
OpenRouter). Entrada nueva con `provider: custom`, `base_url:
http://192.168.1.102:11502/v1`. Gateway reiniciado con el comando propio `hermes
gateway restart` (no se mataron procesos a mano) — verificado activo, sin errores en
logs. Los perfiles `nacho` y `risko` **no se tocaron**.

**AnythingLLM:** excluido explícitamente de este trabajo, decisión de Montu — ya no
es la app elegida para el dominio público (`ia.montuschi.cl` apunta a LibreChat desde
la sesión de 2026-08-25, ver sección 8), no vale la pena complicarlo con un endpoint
adicional.

---
*Ver también: sección 7 (Pendientes) para el estado previo a esta sesión.*

