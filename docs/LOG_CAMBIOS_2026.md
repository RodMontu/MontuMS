---
## 2026-07-13: Incidente Visual-Voice — ExitCode 128 + STT ffmpeg missing

### Parte 1 — Contenedor caído (NVML Driver Not Loaded)
- **Síntoma:** HTTP 502 en https://visual-voice.montuschi.cl. Contenedor caído desde 2026-07-12 07:11 UTC (38h downtime).
- **Root Cause:** docker-compose.yml tenía runtime: nvidia + deploy.resources.reservations.devices: [gpu]. GPU P104-100 está bajo vfio-pci (VFIO passthrough a VM Windows) → NVML no disponible en host → ExitCode=128 al crear la task.
- **Fix:** Eliminados runtime: nvidia y bloque deploy.resources.reservations del compose /home/x/visual-voice/docker-compose.yml. Backup: docker-compose.yml.bak.20260713_*.
- **Justificación:** Pipeline post-2026-07-10 no requiere GPU en serverX. Todo el cómputo IA reside en Mac Studio (STT mlx-whisper :8765, Ollama :11434 gpt-oss:20b, Metal M2 Max).

### Parte 2 — STT 500 Error (ffmpeg no instalado en Mac Studio)
- **Síntoma:** Transcripción OK en chunks S1-S6 (0-60min), S7-S11 retornaban vacío silencioso.
- **Root Cause:** ffmpeg no estaba instalado en Mac Studio. stt-mac lo requiere internamente para preprocesar audio antes de mlx-whisper. Chunks 1-6 eran legibles nativamente; S7+ requirieron conversión → FileNotFoundError: ffmpeg → HTTP 500.
- **Fix:** brew install ffmpeg (v8.1.2_1) en Mac Studio + launchctl kickstart -k gui/501/cl.montuschi.stt-mac.
- **Aclaración arquitectural:** El .env de Visual-Voice tiene OLLAMA_BASE_URL=http://192.168.1.111:11434 (serverX, obsoleto — ignorado por el código). El main.py hardcodea http://192.168.1.102:11434 (Mac Studio). Ollama nunca corrió en serverX.
- **Estado post-fix:** Contenedor Up, puerto 8502 LISTEN, stt-mac PID 35364 operativo, test HTTP 200 confirmado.

## 2026-06-01 — Setup escritorio virtual serverX + fix bridge Clawdio Mac

**serverX — Nuevas instalaciones:**
- Google Chrome stable (repo oficial Google, apt)
- Claude Desktop v1.9255.2 (aaddrick/claude-desktop-debian, apt)
- Antigravity CLI → /home/x/.local/bin/agy
- Antigravity IDE → /home/x/.local/share/antigravity-ide/ (Electron, launcher en .local/bin)
- Extensión cafetechne.antigravity-link-extension-1.0.16-universal

**MCPs configurados en serverX (~/.config/Claude/claude_desktop_config.json):**
- clawdio: /home/x/bin/hermes-mcp-bridge → SSH a i3@192.168.1.211 (hermes mcp serve)
- desktop-commander: npx @wonderwhy-er/desktop-commander
- antigravity-link: node ~/.antigravity-ide/extensions/cafetechne.antigravity-link-extension-1.0.16-universal/mcp-server.mjs

**SSH key nueva:** x@serverX → i3@serveri3
- Archivo: ~/.ssh/id_ed25519_serveri3
- Agregada a authorized_keys de serveri3 ✅

**Mac — Fix bridge Clawdio:**
- Archivo: /Users/montu/hermes-mcp-bridge-v2
- Problema: apuntaba a docker exec clawdio-v2 (contenedor ya no existe)
- Fix: reemplazado por SSH directo a /home/i3/.hermes/hermes-agent/venv/bin/hermes mcp serve --accept-hooks
- Estado: running ✅

**Pendiente:** Rotar API key OpenRouter expuesta en sesión de hoy

## 2026-05-30 — Rabín: migración definitiva a DeepSeek V4 Flash + fixes estructurales

**Contexto:** openrouter/owl-alpha presentaba identidad propia alterada (respondía como "OWL de ZOO company"
en vez de Clawdio Rabín — no respetaba SOUL.md). gemini-2.5-flash con créditos agotados (HTTP 429).
Migración completa a OpenRouter como provider único.

**Stack de modelos (nuevo):**
| Slot | Modelo | Provider | Costo |
|---|---|---|---|
| Principal | deepseek/deepseek-v4-flash | OpenRouter | ~$0,10/M tokens |
| Fallback 1 | nousresearch/hermes-3-llama-3.1-405b:free | OpenRouter | Free |
| Fallback 2 | nvidia/nemotron-3-super-120b-a12b:free | OpenRouter | Free |

**Cambios en /home/i3/.hermes/config.yaml (serveri3):**
- model.provider: gemini → openrouter
- model.default: openrouter/owl-alpha → deepseek/deepseek-v4-flash
- browser.engine: disabled (fix HTTP 404 "No endpoints found that support tool use")
- compression.enabled: false
- Todos los auxiliary providers: auto → openrouter (elimina intentos a Gemini → 429)
- cron: [] — 10 crons eliminados
- Backup: config.yaml.bak.20260530 creado

**Crons eliminados (los 10):**
- Documentados: monitor-manana, monitor-noche, briefing-manana, ideas-pendientes, resumen-semanal
- No documentados (descubiertos en log): Monitor Mañana, Monitor Noche, Recordatorio Terminal Miau-Nube,
  inbox-miaude-check, Hermes Agent al día

**Docker clawdio-v2:** DETENIDO (docker stop). Corría con config antiguo (gemini-2.5-flash) y competía
por polling de Telegram con el gateway nativo. PENDIENTE: docker rm clawdio-v2.

**Bugs documentados (Hermes v0.14.0):**
1. NameError: _pool_may_recover_from_rate_limit — crons fallan al usar Gemini. Regresión del framework.
2. auxiliary_client.py línea 427: _OPENROUTER_MODEL = "google/gemini-2.5-flash" hardcodeado como
   fallback — causa que provider:auto intente Gemini si hay GOOGLE_API_KEY en .env.

**Modelos descartados:**
- openrouter/owl-alpha: identidad propia alterada ("Soy OWL de ZOO company")
- gemini-2.5-flash: doble falla (NameError + créditos agotados)

**Archivos modificados en este repo:**
- docs/INVENTARIO_MAESTRO.md — sección 8 actualizada
- docs/LOG_CAMBIOS_2026.md — este registro (nuevo)
- docs/CLAWDIO_ASISTENTE_PERSONAL.md — Stack modelos + Pendientes actualizados

---

---
## 2026-05-29 — Fix Rabín: modelo principal + eliminación de crons

**Contexto:** Créditos Gemini agotados. Fallo del switch /model session-only con
sufijo :free (RuntimeError: No LLM provider configured). Se migra OpenRouter como
provider primario. Se eliminan 10 crons (5 no documentados descubiertos en log).

**Cambios en /home/i3/.hermes/config.yaml (serveri3):**
- model.provider: gemini → openrouter
- model.default: gemini-2.5-flash → openrouter/owl-alpha
- fallback_providers reordenados:
  1. openrouter/nousresearch/hermes-3-llama-3.1-405b:free (nuevo, del equipo Hermes)
  2. gemini/gemini-2.5-flash (degradado a fallback 2)
  3. openrouter/nvidia/nemotron-3-super-120b-a12b:free (degradado a fallback 3)
- cron: [] — eliminados 10 crons (5 documentados + 5 no documentados)

**RCA del fallo /model:free:**
El comando /model en Hermes es session-only. El sufijo :free en OpenRouter
falla cuando el provider primario en config.yaml es gemini, porque el switch
de sesión no hereda el contexto del proveedor fallback.
Solución definitiva: OpenRouter como provider primario en config.yaml.

**Bug Hermes v0.14.0 detectado:**
NameError: _pool_may_recover_from_rate_limit en contexto de ejecución de crons.
Afecta: Monitor Mañana, Monitor Noche, Recordatorio Terminal Miau-Nube,
Hermes Agent al día. Regresión del framework, no de config.

**Crons no documentados encontrados:**
Monitor Mañana, Monitor Noche, Recordatorio Terminal Miau-Nube,
inbox-miaude-check, Hermes Agent al día.

**Archivos modificados:**
- /home/i3/.hermes/config.yaml — MODIFICADO
- /home/i3/.hermes/config.yaml.bak.20260529 — BACKUP creado
- INVENTARIO_MAESTRO.md — secciones Clawdio actualizadas
- LOG_CAMBIOS_2026.md — este registro
---

## 2026-05-24 -- BIBLIOTECA_PROMPTS_MS v1.1 - Bloque B completado

**Contexto:** Meta-prompt iterativo (codigo 61) aplicado a la v1.0. Abogado del Diablo identifico 3 problemas sistemicos y mejoras en 11 de 14 templates.

**Cambios:**
- Indice rapido de 14 filas por situacion (nuevo)
- Tiempo de completar en cada template (nuevo, criterio <60s)
- Placeholders de accion eliminados de campos de dato
- Campo Servidor agregado en templates 2.1 y 2.2
- Campo componentes_existentes agregado en template 3.2
- Campo longitud agregado en output de template 3.1
- Template 1.3 simplificado: infra como bloque opcional separado
- Template 1.4 agrega campo Prioridad y Confirmar antes de ejecutar
- Template 2.3 agrega git log --oneline -3 en pre_deploy
- Template 3.4 agrega probabilidad estimada y limite de 2 paginas
- Templates 3.3 y 4.2 validados como APTOS sin cambios
- Nota operacional agregada en seccion 5: Gemini CLI fuera de directorio raiz
## 2026-05-24 — Rabín 2.0 Docker + fixes NVML + diagnóstico SSH

### Rabín 2.0 — instalación completa
- Migrado de systemd nativo a Docker (clawdio-v2 en /home/i3/clawdio-v2/)
- Path interno: /opt/data/ — Crons en /opt/data/cron/jobs.json
- Modelo: gemini-3-flash-preview vía Gemini API directa
- 9 skills: cotidianas (3) + infra (2) + MS (5 incluyendo canal Miaude↔Rabín)
- DB migrada: 23 deberes + 1 idea + tabla miaude_inbox nueva
- SSH contenedor→serverX: /opt/data/.ssh/id_ed25519 con fix -F /dev/null
- briefing-manana: retry automático ante HTTP 503
- MCP bridge v2 activo en Claude Desktop
- SOUL.md: limitación SSH a serveri3 documentada (comportamiento esperado)
- /sethome: canal home = Rodrigo Montuschi (8357148621)

### Fix NVML serverX
- Causa: apt upgrade nvidia 580.126→580.159 sin reboot
- Fix: sudo systemctl stop ollama && sudo reboot
- Post-reboot: GPU P104-100 operativa, todos los contenedores up en 54s

### Pendientes registrados
- BACKLOG-RABIN-01: webhook HTTP canal Miaude→Rabín autónomo

### Equipos afectados
- serveri3 (clawdio-v2), serverX (GPU fix), MacBook (bridge MCP v2)

---

## 2026-05-24 — Rabín 2.0 instalado en Docker + fixes de confiabilidad

### Contexto
Rabín 1.x (Hermes systemd nativo) reemplazado por Rabín 2.0 en Docker
por problemas de confiabilidad: crons incompletos, drift de skills,
tool use frágil con Gemini 2.5 Flash.

### Cambios aplicados
- Hermes Agent migrado de systemd nativo → Docker (contenedor: clawdio-v2)
- Directorio base host: /home/i3/clawdio-v2/ en serveri3
- Path interno contenedor: /opt/data/ (no /root/.hermes/)
- Crons en: /opt/data/cron/jobs.json (no en config.yaml)
- Modelo: gemini-3-flash-preview vía Gemini API directa
  (reemplaza gemini-2.5-flash-preview vía OpenRouter)
- 9 skills creadas:
  - Cotidianas: deberes-ideas, google-workspace, supermercado
  - Infra: infra-monitor, infra-docker-check
  - MS: ms-canal-miaude-a-rabin, ms-canal-rabin-a-miaude,
        ms-protocolo-comunicacion, ms-doc-updater, ms-handoff-reader
- DB migrada desde Rabín 1.x: 23 deberes + 1 idea
- Tabla miaude_inbox agregada a clawdio_db.sqlite (canal asíncrono Miaude↔Rabín)
- SSH key contenedor→serverX: /opt/data/.ssh/id_ed25519
  Fix: symlink /root/.ssh → /opt/data/.ssh (permisos hermes/root)
  Fix monitor.sh: ssh con -F /dev/null -i /root/.ssh/id_ed25519
- briefing-manana: retry automático ante HTTP 503 Gemini
- MCP bridge v2: ~/hermes-mcp-bridge-v2 activo en Claude Desktop
- /sethome configurado: canal home = Rodrigo Montuschi (8357148621)

### Pendientes registrados
- BACKLOG-RABIN-01: webhook HTTP para canal Miaude→Rabín autónomo
  (hoy MCP solo permite Miaude→Montu, no instrucciones directas a Rabín)
- BACKLOG-SERVERX-01: CERRADO (ver entrada siguiente)

### Equipos afectados
- serveri3 (192.168.1.211) — contenedor clawdio-v2 nuevo
- MacBook Pro — bridge MCP v2 activo en Claude Desktop

---

## 2026-05-24 — Fix NVML serverX: driver/library version mismatch

### Contexto
nvidia-smi reportaba "Failed to initialize NVML: Driver/library version mismatch"
Detectado en reporte monitor.sh de Rabín 2.0.

### RCA
Actualización de paquetes nvidia-driver-580-server 580.126.09 → 580.159.03
ejecutada sin reboot. Módulo viejo (580.126.09) quedó cargado en RAM
mientras librerías en disco pasaron a 580.159.03. NVML detecta mismatch
y se niega a inicializar. Sin daño de hardware.

### Fix aplicado
Reboot controlado con cierre previo de Ollama:
sudo systemctl stop ollama && sudo reboot

### Estado post-reboot
- nvidia-smi: 580.159.03 ✅ (módulo y librería sincronizados)
- GPU P104-100: 34°C, 0MiB usados, operativa
- CUDA display 13.0 en nvidia-smi = versión máxima del driver,
  no versión runtime. Ollama usa CUDA 12.x internamente. Sin impacto.
- Todos los contenedores up en ~54s post-reboot:
  ollama, pegas_v2, visual-voice, cutx-app, retroassembly, portainer ✅

### Equipos afectados
- serverX (192.168.1.111)

---

## 2026-05-24 — Biblioteca de Prompts MS v3.0 — Bloque A

**Contexto:** Primera versión de la biblioteca de prompts reutilizables de la MS v3.0, construida aplicando códigos de prompt engineering de la infografía "100 Códigos" (01 XML Maestro, 04 Primero Piensa, 08 Paso a Paso, 15 Motor de Disparo, 44 SOP).

**Cambios:**
- Archivo nuevo: `docs/BIBLIOTECA_PROMPTS_MS.md` (292 líneas)
- Sección 1: Inicio de sesión — 4 templates con Motor de Disparo (trigger phrase ACTIVAR_MS_V3)
- Sección 2: Delegación CCa — templates base, RCA y deploy con estructura Paso a Paso
- Sección 3: Delegación Gemini — templates análisis, frontend, documentación y Abogado del Diablo
- Sección 4: Actualización docs vía Rabín — SOP estándar y template cambio infra
- Código 12 (Contrarian) integrado como template de revisión arquitectónica

---
## 2026-05-17 — Actualización Hermes/Clawdio Rabín a v0.14.0 + fixes de confiabilidad

### Cambios aplicados
- Hermes Agent: v0.12.0 → v0.14.0 "The Foundation Release" (1693 commits, 545 issues cerrados, 12 P0)
- Fix nativo bug cron output (código Python crudo en Telegram) — resuelto en v0.13+
- Secret redaction: ON por defecto (corrige bug de patch corruption de v0.12)
- SOUL.md: 3 reglas técnicas canónicas agregadas (comunicación proactiva, protocolo SSH write_file→scp→ssh, formato cron)
- Memory provider: holographic activado (SQLite FTS5 + HRR local, sin cloud)
- Cron "Hermes Agent al día": prompt reescrito + deliver explícito telegram:8357148621

### Estado post-cambios
✅ Hermes v0.14.0 activo | ✅ Gateway corriendo | ✅ Holographic memory | ✅ SOUL.md 113 líneas limpio
## 2026-05-17 — Hermes v0.14.0 + fixes confiabilidad Rabín

- Hermes Agent: v0.12.0 → v0.14.0 "The Foundation Release" (1693 commits, 545 issues, 12 P0)
- Fix cron output: toolset web → search (web requería API keys no configuradas)
- SOUL.md: 3 reglas técnicas canónicas (comunicación proactiva, protocolo SSH, formato cron)
- Memory provider: holographic activado (SQLite FTS5 + HRR local)
- Config: provider gemini corregido (corrupción por replace múltiple), config v19 funcional
- Cron "Hermes Agent al día": prompt reescrito + deliver telegram:8357148621 + toolset search

Estado: ✅ v0.14.0 | ✅ Gateway activo | ✅ Holographic memory | ✅ SOUL.md 113 líneas | ✅ doctor sin errores críticos
## 2026-05-18 — QA OptiFierro V2: 9/9 PASS + fixes post-entrega Gustavo

### Contexto
QA completo ejecutado sobre los fixes solicitados por Gustavo Godoy (Torres Ocaranza) post-entrega del 13 de mayo. 9 checks verificados, todos PASS. BACKLOG-MP01-ROBERTO cerrado: Roberto confirmó que el acceso a Cubigest para Calama y Coronel ya existe. Docker Desktop en TO configurado para autoarranque y resiliencia de contenedores.

### Fixes aplicados (commits en Optifierro-V2)
- `2fa552f` fix(#1): asistencia muestra VACACIONES/LICENCIA/PERMISO desde GV
- `f5fce4d` fix(#6): cache 15min en obtener_estado_maquinas (Cubigest)
- `a3a9f51` fix: bolsa de trabajo vacía al montar (id_tarea undefined)
- `1021b73` fix: turno noche clasificado como FALTA en presencia
- `7589f0a` fix: operadores repetidos entre turnos (guard sucursal_id==10 removido)
- `5be1c05` fix: prompt Argumento mejorado con diámetros, carga, ITs rechazadas
- `af38ced` chore: OLLAMA_URL fallback en docker-compose.yml
- fix UI: input hora jornada como text HH:MM (fix AM/PM locale) — sin commit aún

### Backlog cerrado
- **BACKLOG-MP01-ROBERTO:** CERRADO. Roberto confirmó que el acceso a Cubigest para Calama y Coronel ya existe. No requería gestión adicional.

### Infra TO (PROMETHEUS-AI-CORE 192.168.1.65)
- Docker Desktop: Start on login ✅ configurado
- Todos los contenedores: restart policy `always` o `unless-stopped` ✅
- `OLLAMA_URL=http://host.docker.internal:11434` configurado en docker-compose.yml como fallback

### Equipos afectados
- TO (PROMETHEUS-AI-CORE 192.168.1.65) — OptiFierro V2

### Estado post-cambios
✅ 9/9 QA PASS — sistema estable post-entrega a Gustavo

---

## 2026-05-17 — Actualización Hermes/Clawdio Rabín a v0.14.0 + fixes de confiabilidad

### Cambios aplicados
- Hermes Agent: v0.12.0 → v0.14.0 "The Foundation Release" (1693 commits, 545 issues cerrados, 12 P0)
- Fix nativo bug cron output (código Python crudo en Telegram) — resuelto en v0.13+
- Secret redaction: ON por defecto (corrige bug de patch corruption de v0.12)
- SOUL.md: 3 reglas técnicas canónicas agregadas (comunicación proactiva, protocolo SSH write_file→scp→ssh, formato cron)
- Memory provider: holographic activado (SQLite FTS5 + HRR local, sin cloud)
- Cron "Hermes Agent al día": prompt reescrito + deliver explícito telegram:8357148621

### Estado post-cambios
✅ Hermes v0.14.0 activo | ✅ Gateway corriendo | ✅ Holographic memory | ✅ SOUL.md 113 líneas limpio## 2026-05-16 — Fix NoMachine serverX: escritorio remoto KDE operativo

### Problema
NoMachine conectaba pero mostraba pantalla negra con solo cursor del mouse.

### RCA (Root Cause Analysis)
Tres capas de problema identificadas y resueltas en secuencia:
1. `/etc/X11/Xwrapper.config` tenía `allowed_users=console` → Xorg no podía arrancar como usuario nx
2. Paquete `dbus-x11` no instalado post-reinstalación → `dbus-launch` ausente → exit code 127 en startplasma-x11
3. Servicio `xvfb.service` corriendo en `:0` → NoMachine detectaba Xorg "activo" y no creaba display virtual propio

### Solución aplicada
- `/etc/X11/Xwrapper.config` → `allowed_users=anybody` + `needs_root_rights=yes`
- `sudo apt-get install -y dbus-x11`
- `sudo systemctl stop xvfb && sudo systemctl disable xvfb`
- `sudo /etc/NX/nxserver --restart`
- En cliente Mac: aceptar creación de nueva pantalla virtual → KDE Plasma levanta correctamente

### Estado final
✅ NoMachine operativo desde MacBook Pro → serverX vía LAN
✅ KDE Plasma 5.27 corriendo en display virtual NoMachine
✅ xvfb.service deshabilitado permanentemente
✅ dbus-x11 instalado
✅ Xwrapper.config corregido

### Notas
- serverX tiene TV 42" 4K conectado vía HDMI como pantalla de emergencia, pero no se usa como display manager
- NoMachine crea display virtual bajo demanda (sin display manager activo)
- Checkbox "Crear siempre nueva pantalla en este servidor" activado en cliente
---
═══════════════════════════════════════════════════
FECHA: 2026-05-15
PROYECTO: Infraestructura NAS — Migración SMB → NFS
═══════════════════════════════════════════════════

[MIGRACIÓN NAS SERVERX]
RCA final: cliente SMB de macOS Sequoia tiene bug con Samba/Linux
que produce fts_read: Permission denied en readdir, irresolvible
por configuración (afecta Finder, Terminal y todos los procesos).
SOLUCIÓN: Migrado a NFS nativo.
- serverX: nfs-kernel-server activo, exports en /etc/exports:
  /mnt/extra y /home/x exportados a 192.168.1.41 (rw,no_root_squash)
- Mac: mounts en ~/Miau-Nube y ~/Home-X via mount -t nfs
- LaunchAgent: com.user.nfs-serverx (automontaje cada 5 min)
- Samba: smb.conf actualizado con config 2026 para macOS (por si acaso)
Estado: ✅ NFS funcionando. SMB deprecado para acceso desde Mac.
---
---
===================================================
FECHA: 2026-05-15
SESION: Fix Clawdio - ModuleNotFoundError init_db
===================================================

#### Fix Clawdio: ModuleNotFoundError init_db

- **Sintoma:** Clawdio fallaba con execute_code para deberes/ideas. Error: ModuleNotFoundError: No module named init_db. Ruta incorrecta generada en runtime: /home/i3/.hermes/skills/productivity/personal-productivity-db/scripts

- **RCA:** init_db.py esta en /home/i3/.hermes/init_db.py (raiz directa). MEMORY.md no documentaba el patron de importacion correcto, Gemini Flash inferia la ruta y la alucinaba. Bug de contexto ausente, no de codigo.

- **Fix aplicado por Miaude via Control Your Mac:**
  - Bloque PATRON DE IMPORTACION DB - OBLIGATORIO agregado en /home/i3/.hermes/memories/MEMORY.md
  - Patron correcto: sys.path.insert(0, /home/i3/.hermes) — nunca subdirectorios
  - Hermes reiniciado. Smoke test: import exitoso

- **Aprendizaje:** LLM sin ground truth en contexto inventa rutas plausibles pero falsas. Solucion: anclar la verdad en MEMORY.md.


---
═══════════════════════════════════════════════════
FECHA: 2026-05-08
SESIÓN: Fix MCP y VPN Respaldo
═══════════════════════════════════════════════════

#### Fix MCP bridge Clawdio en Claude Desktop
- Síntoma: "Could not attach to MCP server clawdio" en Claude Desktop
- Causa raíz: /usr/local/bin/hermes-mcp-bridge sin bit de ejecución (-rw-r--r-- en vez de -rwxr-xr-x)
- Fix: chmod +x /usr/local/bin/hermes-mcp-bridge
- Verificación: hermes v0.12.0 responde en /home/i3/.local/bin/hermes — path correcto
- Estado: RUNNING ✅
- Pendiente: hermes 850 commits behind — evaluar hermes update en serveri3

#### VPN TO: script de respaldo actualizado
- Script ~/conectar_to_vpn.sh actualizado en MacBook
- IP anterior (GTD): 152.230.125.218
- IP nueva (TLINK, respaldo): 45.4.1.234
- Causa: caída del proveedor principal GTD, conexión de respaldo TLINK activada

---

═══════════════════════════════════════════════════
FECHA: 2026-05-07
PROYECTO: OptiFierro V2 — QA Pre-Entrega + Fixes
SESIÓN: QA completo 7 secciones + 10 fixes aplicados + verificación Fase 2
═══════════════════════════════════════════════════

### Fixes aplicados (todos verificados PASS por Codex CLI)

**Backend — Torres Ocaranza (PROMETHEUS-AI-CORE 192.168.1.65)**
- AV-02 backend: POST /api/averias ahora retorna `requires_reprogram: True` en el JSON de respuesta. Archivo: routers/averias.py línea 108.
- OP-01 DB: maquinas_info.Operador_Habitual corregido de 'OmRamirez' a 'oramirez' (1 fila). SQLite: optifierro_v2.db.
- OP-01 código: routers/maquinas.py — query de nombre_map cambiada a LEFT JOIN con LOWER() case-insensitive entre maquinas_info y operadores_matriz.
- OP-02 DB: operadores_matriz id=18, username=ctrujillo — nombre actualizado de '(Nombre Pendiente - confirmar con RRHH)' a 'Carlos Alexis Rogers Trujillo'. Fuente: asistencia.db de scrap-geovictoria.

**Frontend — Torres Ocaranza**
- AV-01: window.confirm() reemplazado por modal React en GestorAverias.tsx. Texto: "Confirma lo siguiente: [resumen falla]".
- AV-02 frontend: Banner auto-dismiss 8s en GestorAverias.tsx cuando response.requires_reprogram === true. Texto: "Averia registrada. Para reflejar el cambio en la planificacion ejecuta Reprogramar".
- PROG-03: Math.min eliminado en GestorProgramacion.tsx línea 488. porcentajeCarga ahora muestra valor real sin cap. Si >100% muestra barra roja.
- PROG-05: Fallback hora inicio turno corregido de '08:15'/'20:15' a '08:00'/'20:10' en GestorProgramacion.tsx líneas 792, 816, 1170.
- PROG-06: Función getTextColorForBackground() implementada en GestorProgramacion.tsx con WCAG_AA_CONTRAST_RATIO = 4.5. Las cajitas del Gantt calculan automáticamente texto blanco o negro según contraste del fondo.
- PROG-07: Condición lista_etiqueta_ids.length > 1 cambiada a >= 1 en GestorProgramacion.tsx línea 945. Modal ahora muestra etiquetas aunque haya solo 1.
- VS-01: Indicador de sucursal activa en VistaSemanal.tsx corregido. Dot ahora usa flex items-center gap-1.5 (inline izquierda del nombre).

**Build y deploy**
- npm run build: PASS exit 0. Solo warning pre-existente de chunk size Vite (no bloqueante).
- docker compose restart backend: ejecutado post-fixes backend.
- docker compose restart frontend: ejecutado 3 veces durante la sesión (post-cada batch de fixes).

### Metodología usada en esta sesión
- Miaude_sin_Montu Skill activa: CCa + Gemini CLI + Codex CLI en paralelo sin intervención manual de Montu.
- CCa (Mac): diagnóstico, análisis de código fuente.
- Codex CLI (TO, GPT-5.5): fixes backend + fixes frontend + QA verificación. Acceso directo al filesystem de TO sin SSH desde Mac.
- Gemini CLI (Mac): intentado para frontend pero bloqueado por falta de SSH configurado hacia TO. Reemplazado por Codex en TO.
- Fase 2 verificación: 10/10 checks PASS.

### Pendientes críticos post-sesión
- BACKLOG-MP01-ROBERTO (PRIORIDAD MÁXIMA): Usuario OptiFierro necesita GRANT SELECT en SQL Server Cubigest para bases de Calama (TOLTDA/TOREN/TORREON1) y Coronel (TOSOL/TOGENUA/TMAESTRANZA) sobre tabla INFORMAT_Vista_OrdenesCompra. Contactar a Roberto en TO. Sin esto, obtener_oc_pendientes_inet retorna {} para Calama y Coronel.
- PROG-02 pendiente: Operador en tooltip/modal Gantt no coincide con operador asignado. Requiere investigación más profunda del flujo de datos. Fase siguiente.
- Fase 2 (post-entrega): ADMIN-01 (turno noche marcado FALTA), RCA#4 (semántica Turno A/B), MAQ-MEJORA-01 (restricciones al motor), PROG-OBS-01 (argumento LLM).


## 2026-05-06 — cctol habilitado en MacBook (Devstral remoto vía VPN)
- Alias cctol agregado en /Users/montu/.zshrc
- Patrón: ANTHROPIC_BASE_URL=http://192.168.1.65:11434 ANTHROPIC_API_KEY=ollama /Users/montu/.local/bin/claude --model devstral --dangerously-skip-permissions
- Ollama en TO (192.168.1.65) ya escuchaba en 0.0.0.0:11434 sin cambios necesarios
- Test funcional end-to-end: CCTOL_MAC_OK ✅
- Restricción operacional: VPN TO activa en un solo equipo a la vez (nunca simultáneos)
- GPU TO: RTX 5060 Ti 16GB, modelo devstral

## 2026-05-06 — MS v3.0 aprobada: incorporación Equipo OpenAI
- Metodología Sinérgica actualizada a v3.0
- Nueva capa de equipo incorporada: Equipo OpenAI (ChatGPT como Subgerente/cerebro secundario, Codex CLI como ejecutor)
- Estructura de 4 capas:
  1. ARQUITECTO: Claude (Miaude)
  2. LÍDERES/SUBGERENTES: Gemini (chat) + ChatGPT
  3. COORDINADOR/ORQUESTADOR: Clawdio Rabín
  4. EJECUTORES: CCa + CC's + Gemini CLI + Antigravity + Codex CLI
- Codex CLI instalado: Mac (v0.120.0, /usr/local/bin/codex), TO (v0.128.0, user OptiFierro)
- Codex asignado como ejecutor preferente en Windows/PowerShell (TO) y fallback de CCa por cuota
- Deuda técnica: verificar versión en serverX y serveri3; autenticación OpenAI pendiente en todos los equipos

## 2026-05-05/06 — Clawdio: desacoplamiento de serverX
- terminal.backend cambiado de ssh → local en /home/i3/.hermes/config.yaml
- terminal.backend cambiado de ssh → local en /home/i3/.hermes/config.yaml
- terminal.cwd cambiado de /home/x → /home/i3
- Fix supermercado.json: eliminado prefijo ```json corrupto, lista_mes_actual reactivada con 3 productos (vinagre blanco, leche almendras Orasi, galletas Gran Cereal cacao)
- Ejecutado con Codex CLI desde MacBook
- Backup: /home/i3/.hermes/config.yaml.bak.20260506_1034
- Deuda: productos_habituales vacío, reconstruir lista completa con Pecas

---


## 2026-05-03 — MontuMS completado + MS-Flow operativo

**Repo:** github.com/RodMontu/MontuMS (privado)
**Commit:** 036e6c5

**Archivos creados:**
- agentes.md — catálogo completo MS Team (11 agentes Claude + equipo Gemini + coordinadores)
- proyectos.md — estado de 5 proyectos activos + pipeline TO
- convenciones.md — IPs, aliases, reglas operativas, rutas clave, URLs raw GitHub
- docs/INVENTARIO_MAESTRO.md — migrado desde Samba (fuente de verdad → GitHub)
- docs/LOG_CAMBIOS_2026.md — migrado desde Samba
- docs/CLAWDIO_ASISTENTE_PERSONAL.md — migrado desde Samba

**Decisiones:**
- GitHub MontuMS reemplaza carpeta DOCUMENTOS_TECNICOS como fuente de verdad activa
- Samba /mnt/extra/DOCUMENTOS_TECNICOS/ queda como archivo histórico
- Gemini Lead (Gem) configurado con system prompt MS-Flow + conocimientos cargados
- MS-Flow bautizado oficialmente como protocolo de coordinación de la MS

## 2026-05-03 — MS-Flow inaugurado + repo MontuMS

**MS-Flow:** protocolo de coordinación de la Metodología Sinérgica (MS).
Sistema nervioso compartido entre Miaude, AG, CC y Clawdio.

**Infraestructura creada:**
- Repo GitHub privado: github.com/RodMontu/MontuMS
- SSH key serverX → GitHub: id_ed25519_github (registrada en GitHub/settings/keys)
- Git identity serverX: ce3wkc@gmail.com / RodMontu
- /home/x/MontuMS/ — clone local del repo en serverX
- /home/x/handoff/handoff_actual.md → symlink a /home/x/MontuMS/handoff_actual.md
- Aliases serverX: handoff, handoff-edit, sesion, montu-ms
- README.md con estructura MS + MS-Flow + convenciones globales
- handoff_actual.md con estado al 2026-05-03

**Primer commit:** 145813e — pusheado a main

## 2026-05-03 — Fix monitor.sh + SOUL.md registro lingüístico

**monitor.sh (`/home/i3/.hermes/scripts/monitor.sh`):**
- Root cause: comillas triples `'''` para escapar awk dentro de bloque SSH — sintaxis frágil que generaba `unterminated string literal` en línea 15.
- Fix: reescritura del bloque SSH usando heredoc (`<<'EOF'`) — elimina todo el escaping anidado.
- Verificado: serveri3 + serverX + GPU + montuschi.cl reportan correctamente.

**SOUL.md (`/home/i3/.hermes/SOUL.md`):**
- Root cause: sección `## Idioma` no incluía "puta" en la lista de términos prohibidos, lo que le daba permiso implícito al modelo.
- Fix: sección reescrita con registro permitido explícito, lista de prohibidos ampliada, y criterio de oro como regla autónoma de decisión para el modelo.
- Hermes reiniciado para aplicar cambios.

## 2026-05-02 al 2026-05-03 — Expansión de Infraestructura y OpenRouter

**Contexto:** Fortalecimiento del stack de modelos vía OpenRouter y habilitación de entorno gráfico avanzado en serveri3 para automatización de browser.

**Cambios en serveri3 (192.168.1.211):**
- **Gemini CLI v0.40.1:** Instalado globalmente en `/home/i3/.hermes/node/bin/gemini`. Autenticado con Google One AI Pro. PATH actualizado en `~/.bashrc`.
- **Entorno Gráfico:** Instalación de NoMachine Server v9.4.14, XFCE4 + goodies, x11vnc y noVNC para gestión remota liviana.
- **Google Chrome:** Instalado (deb nativo, v147) en `/usr/bin/google-chrome`.
- **Camoufox operativo:** better-sqlite3 recompilado para Node v22. Puerto 9377. Sesión persistente de Lider.cl (Anastasia Rivera) funcional.

**Cambios en serverX (192.168.1.111):**
- **Aliases OpenRouter:** Configurados 5 nuevos aliases (`ccor1` a `ccor5`) integrando modelos de OpenRouter (GPT-OSS, Nemotron, DeepSeek v4 Flash/Pro).
- **Hook Post-Tool-Use:** Actualizado script `post-tool-use.sh` con contador de llamadas. Alertas automáticas a Telegram (@clawdio_dev_local_bot) al llegar a 80 (aviso) y 100 (crítico) calls.
- **Presupuesto:** Carga inicial de $15 USD en OpenRouter (Saldo: ~$14.76).

**Nomenclatura y Alertas:**
- **Clawdio Rabín (@pantero_bot):** Alias coloquial "Rabín" para el asistente personal.
- **Clawdio Dev (@clawdio_dev_local_bot):** Bot dedicado exclusivamente a alertas TI e infraestructura.
- **Miaude:** Alias fonético para Claude en el contexto de Mi TI.

**Gastos IA mensuales consolidados:**
- Claude Pro ($20) + Gemini Pro ($20) + Google API Gemini ($10) + OpenRouter ($15). Total est: ~$65 USD/mes.

---
## 2026-05-02 — Superpoderes Clawdio: Fase 1, 2 y 3 + Nuevo Sistema de Trabajo

**Contexto:** Sesión completa de mejoras a Clawdio (Hermes Agent) basada en investigación previa de arena.ai sobre maximizar el potencial de Hermes. Paralelamente, definición del nuevo sistema de trabajo orquestado Claude + Clawdio + Gemini.

**Cambios en Hermes / Clawdio (serveri3):**
- Hermes actualizado v0.11.0 → v0.12.0 (307 commits, pip install -e .)
- terminal.backend: local → ssh (apuntando a serverX 192.168.1.111, user x)
- Llave pública i3→serverX establecida (authorized_keys)
- display.busy_input_mode: interrupt → steer
- display.background_process_notifications: all → result
- security.website_blocklist activado (localhost, 192.168.1.195, portainer.internal)
- Permisos 600 en .env y config.yaml
- MEMORY.md creado en ~/.hermes/memories/ (60 líneas, infra + proyectos activos)
- 3 crons nuevos: briefing-manana (09:00), ideas-pendientes (17:00 lun-vie), resumen-semanal (10:00 viernes)
- Total crons activos: 5

**Integración Claude Desktop ↔ Clawdio (MCP):**
- Bridge SSH creado en Mac: /usr/local/bin/hermes-mcp-bridge
- claude_desktop_config.json actualizado: mcpServers.clawdio → bridge SSH
- Estado: RUNNING (verificado en Claude Desktop → Configuración → Desarrollador)
- Claude Desktop puede ahora delegar tareas a Clawdio y recibir resultados vía MCP

**Canal de retorno Clawdio → Claude (Opción A):**
- Directorio: /home/i3/.hermes/agent_results/
- Helper: write_result.py (escribe resultados en formato MD estandarizado)
- Skill: ~/.hermes/skills/desarrollo/agent_results.md
- Flujo: Claude delega → Clawdio ejecuta en agente → escribe .md → Claude lee vía MCP

**Nuevo sistema de trabajo — Reglas Cardinales:**
- Documento creado: REGLAS_CARDINALES_FLUJO_ORQUESTADO.md
- Stack de modelos definido: Claude Sonnet (arquitectura), Gemini Pro (análisis/relay), Gemini Flash (Clawdio/orquestación), Qwen3 Coder 480B:free (coding rutinario), Nemotron 3 Super:free (análisis mixto), qwen2.5-coder:7b local (privacidad/offline)
- Flujo orquestado 6 pasos: Montu define → Clawdio recolecta contexto → Claude planifica → Clawdio distribuye → Claude evalúa → Clawdio notifica
- Variante Gemini relay: handoff_actual.md en repo para continuidad cuando se agota cuota Claude
- Regla de seguridad cardinal: instrucciones correctivas siempre van de Montu directo a Claude, nunca mediadas por Clawdio

**Archivos nuevos en /mnt/extra/DOCUMENTOS_TECNICOS/:**
- REGLAS_CARDINALES_FLUJO_ORQUESTADO.md (nuevo — brújula del sistema de trabajo)

**Deuda técnica registrada:**
- Gemini CLI: verificar instalación en serverX y serveri3 (necesario para Fase siguiente)
- OpenRouter: configurar CC con Qwen3 Coder 480B:free como alias en serverX
- Handoff automático: implementar escritura de handoff_actual.md al inicio de sesiones de desarrollo

---
## 2026-04-25 al 2026-05-01 — Implementación completa de Clawdio

**Contexto:** Migración de OpenClaw a Hermes Agent. Implementación de Clawdio como asistente personal para Montu y Pecas.

**Cambios realizados:**
- Hermes Agent instalado en serveri3, gateway como user service systemd con linger
- Bot Telegram @pantero_bot activo con 2 usuarios autorizados
- Stack de modelos: Gemini 2.5 Flash (principal) + Nemotron free + llama3.1:8b local
- SOUL.md creado con personalidad Clawdio (tono culto-informal, español chileno)
- Google Workspace autenticado: 3 cuentas Gmail + Calendar (OAuth2)
- Lista supermercado Lider: 61 productos habituales en supermercado.json
- DB SQLite deberes e ideas: init_db.py con funciones CRUD completas
- STT voz: faster-whisper instalado en venv, stt-local.sh wrapper activo
- Monitoreo automático: monitor.sh + 2 crons Hermes (08:00 y 20:00)
- MEMORY.md y USER.md con manual operativo completo de herramientas
- session_reset cambiado de "both" a "session" para preservar perfil usuario
- Pasos intermedios suprimidos en Telegram (tool_progress: none)
- Node.js 20.x instalado para soporte Camofox (browser automation)
- ByteRover CLI instalado pero desactivado como provider (incompatibilidad Gemini 2.5 Flash)

**Deuda técnica registrada:**
- Lider.cl requiere login manual una vez via Camofox
- Hooks en serverX settings.json pendientes de fix

---
## 2026-04-19 — Instalación de Gemini CLI en Nodo Cliente (MacBook Pro)

**Contexto:** Se requiere un motor de IA nativo en terminal para telemetría remota hacia la infraestructura local, dado que la App visual nativa de Gemini no soporta la arquitectura x64 (Intel). Para asegurar la sincronización de contexto entre los distintos LLMs del ecosistema (Gemini / Claude), se documenta explícitamente el stack cognitivo de esta nueva herramienta.

**Ejecución y Topología:**
- Instalación global de `@google/gemini-cli` vía NPM en entorno Node.js v24.13.0.
- Autenticación OAuth exitosa heredando cuota compartida de Google One AI Pro.
- **Stack Cognitivo Integrado:** El CLI opera con **Gemini 3.1 Pro** para tareas de análisis sistémico y razonamiento profundo, y utiliza el motor de **Gemini Code Assist** para la generación y validación de comandos shell.
- **Nuevo vector de control:** La terminal de macOS funciona ahora como un "HUD Ejecutivo". El CLI genera e inyecta comandos SSH autónomos hacia `x@192.168.1.111` y `i3@192.168.1.211` para analizar logs y gestionar contenedores Docker sin salir del prompt local.
- **Smoke Test:** Lectura remota exitosa del runtime de `ollama` en serverX vía SSH.

---
## 2026-04-10 — SSO Cloudflare Access + Exposición de Apps

**Contexto:** Se implementó autenticación centralizada vía Cloudflare Access para las aplicaciones personales, eliminando la necesidad de validación individual por app. Se expusieron nuevas apps vía Cloudflare Tunnel y se actualizó El Tablero con URLs HTTPS públicas.

**Cambios en Cloudflare Tunnel (`/srv/cloudflared/config.yml` en serveri3):**
- AGREGADO: `tablero.montuschi.cl` → `http://localhost:8080`
- AGREGADO: `visual-voice.montuschi.cl` → `http://192.168.1.111:8502`
- AGREGADO: `cutx.montuschi.cl` → `http://192.168.1.111:8600` *(pendiente DNS/Access)*
- ELIMINADO: `sim.montuschi.cl`
- ELIMINADO: `sim-ws.montuschi.cl`
- CORREGIDO: catch-all `http_status:418` → `http_status:404`

**Cloudflare Access — nuevas políticas creadas:**
- `tablero.montuschi.cl` → política "Acceso Autorizado" (Allow por correo)
- `visual-voice.montuschi.cl` → política "Acceso Autorizado" (Allow por correo)
- `superagente.montuschi.cl` → política "Acceso Autorizado" (Allow por correo)

**El Tablero (`/srv/web/var/www/html/tablero/index.html`):**
- SuperAgente: URL actualizada de `192.168.1.111:18080` → `https://superagente.montuschi.cl`
- Visual Voice: URL actualizada de `192.168.1.111:8502` → `https://visual-voice.montuschi.cl`
- CutX: URL actualizada de `192.168.1.111:8600` → `https://cutx.montuschi.cl`
- Backup guardado: `index.html.bak`

**Decisiones de arquitectura tomadas en esta sesión:**
- Cloudflare Access es el portero único (no se construyó backend de autorización propio)
- OptiFierro mantiene login nativo (sin Access, por diseño)
- Pegas y n8n se mantienen en tunnel pero sin política Access aún (desarrollo activo)
- ia.montuschi.cl se mantiene en tunnel pendiente decisión de reciclaje
- WARP identity (Beta) no activada — pendiente enrollment completo en ambos equipos

---
## [2026-04-04] Sesión: Fix Ollama GPU + Compose Formal

### Problema resuelto
- Ollama consumía RAM del sistema (~60%) y CPU al arrancar, en vez de mantenerse en VRAM.
- GPU caía a CPU intermitentemente, requiriendo watchdog como parche.

### Causa raíz identificada
1. `OLLAMA_MAX_LOADED_MODELS=0` (ilimitado): múltiples modelos se cargaban simultáneamente agotando VRAM y desbordando a RAM.
2. `runtime: runc` en vez de `nvidia`: acceso a GPU frágil ante reinicios y eventos del sistema.
3. Ollama levantado con `docker run` manual sin compose formal.

### Acciones ejecutadas
- Creado compose formal: `/srv/stack/ollama/docker-compose.yml`
- Runtime cambiado a `nvidia`
- Variables aplicadas: `OLLAMA_MAX_LOADED_MODELS=1`, `OLLAMA_KEEP_ALIVE=0`, `OLLAMA_GPU_OVERHEAD=536870912`
- Watchdog `ollama-gpu-watchdog.timer` detenido y deshabilitado permanentemente
- Open WebUI eliminado permanentemente (red `ia-net` eliminada)
- Modelo `deepseek-r1:7b` (4.9GB) descargado como modelo principal para Clawdio

### Verificación
- `ollama ps` confirma: `deepseek-r1:7b → 100% GPU`
- RAM del sistema: 12% (normal, sin desborde)

### Archivos modificados
- `/srv/stack/ollama/docker-compose.yml` — CREADO
- `INVENTARIO_MAESTRO.md` — actualizado
- `INVENTARIO_LLMS_LOCALES.md` — actualizado
- `gpu_intermitente_en_ollama_docker_server_x_p_104_100.md` — ELIMINADO (obsoleto)
---

═══════════════════════════════════════════════════
FECHA: 2026-03-30
PROYECTO: Almacenamiento "ARCA" & Backup Remoto
═══════════════════════════════════════════════════

[ESTRATEGIA ARCA]
- Creación del disco "ARCA" en serverX (/dev/sda1) como repositorio central de datos históricos (745 GB).
- Reciclaje de disco Toshiba USB como "RESPALDO_ARCA" (formato ext4).
- Implementación de sistema de respaldo automatizado desde serveri3 a serverX vía rsync + cron (05:11 AM).
- Configuración de SSH Keys para sincronización sin contraseña i3 → X.
- Auditoría y limpieza de serverX: Liberación de 537 GB de backups obsoletos.

[IA & DESARROLLO - CLAUDE CODE HÍBRIDO]
- Upgrade de Ollama: v0.12.10 → v0.19.0 (Docker).
- Ingesta de nuevo modelo: `qwen3.5:9b` para razonamiento avanzado.
- Implementación de aliases (~/.bashrc) para Claude Code local:
  - `ccoder` (qwen2.5-coder:7b)
  - `creason` (qwen3.5:9b)
- Optimización de tráfico: `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1` habilitado en ejecución local.

═══════════════════════════════════════════════════
FECHA: 2026-03-28
PROYECTO: Infraestructura (NAS & Samba)
═══════════════════════════════════════════════════

[NAS MIAU-NUBE]
- Implementación de almacenamiento centralizado (NAS) en serverX usando disco /dev/sdc1 (/mnt/extra).
- Configuración de Samba para acceso LAN/Externo (Cloudflare WARP).
- Despliegue de scripts de automontaje (~/Miau-Nube) en Mac Rodrigo y Mac Pecas vía Launch Agents.
- Documentación completa integrada en INVENTARIO_MAESTRO.md (Sección 8).

═══════════════════════════════════════════════════
FECHA: 2026-03-23 (jornada completa + madrugada 24)
PROYECTO: OptiFierro V2 + Scraper Geovictoria
═══════════════════════════════════════════════════

[SCRAPER GEOVICTORIA]
- Reescritura completa del scraper: nuevo reporte "Gestión de Asistencia" con horas reales.
- Nuevos campos: hora_ingreso, hora_salida, cargo, turno, permiso, HEA/HEC/HNT/HT, empresa, planta.
- Mapeo sucursal_id corregido: Vista Clara → 10.
- Creado repo independiente: github.com/RodMontu/scrap-geovictoria
- Deploy en TO: contenedores geovictoria-api (:8002) y geovictoria-scheduler.
- Backfill marzo 2026: 1.610 registros, 70 personas.

[INTEGRACIÓN GEOVICTORIA ↔ OPTIFIERRO]
- Motor consulta Geovictoria antes de programar: GET /asistencia/operadores_presentes/{id}
- Cruce RUT→Cubigest Trabajador→username implementado (regla nombre chileno).
- Variable GEOVICTORIA_API_URL=http://host.docker.internal:8002. Fallback configurado.
- Nombres reales poblados en operadores_matriz.Nombre.

[OPTIFIERRO — FIXES CRÍTICOS]
- BUG mapa_maq_nro_nombre resuelto: reconstruido desde SQLite. Cerrillos pasó de 0 a 18 asignadas.
- BUG sucursal_id Cerrillos resuelto: homologado a 10 en constants.ts.
- BUG tabla averias: ALTER TABLE aplicado para columnas faltantes.
- BUG DB optifierro_v2.db corrupta en TO: Reconstruida, migrada y agregada a .gitignore.

[OPTIFIERRO — DATOS REALES DESDE CUBIGEST]
- Sprint 3 re-ejecutado: 19 máquinas con operador habitual real, diámetros reales 2 años, 5.600 registros compatibilidad_formas.
- Matriz operador×máquina repoblada (6 meses).

[OPTIFIERRO — UI]
- Facelift visual: accent=#f97316, sidebar=#111827.
- Branding: Cambio a "Sistema de Planificación de la Producción". Eliminadas referencias a OptiFierro y Torres Ocaranza.

[RESULTADOS MOTOR AL CIERRE]
- Calama: 31/63 asignadas ✅
- Cerrillos: 18/41 asignadas ✅
- Coronel: 1/54 asignadas ⚠️

[PENDIENTES ACTIVOS]
- [ ] Diagnóstico Motor Coronel (1/54).
- [ ] BUG-05/06/07: Gestor Materia Prima.
- [ ] Repoblar compatibilidad_formas con datos reales 2 años.
- [ ] Verificar join diámetros Coronel.
- [ ] UI Geovictoria: dashboard KPIs asistencia (en desarrollo).

**ACTUALIZACIÓN OPTIFIERRO (2026-02-20):**
- **Servicio:** OptiFierro UI (Prototipo HTML/JS Dashboard)
- **Host:** serverX (192.168.1.111)
- **Puerto Activo:** 8080 (tablero_proyecto.html)
- **Ruta de Datos:** Simulador generar_datos_demo.py activo.

## [2026-02-26] Despliegue OptiFierro v2 - Fase 4 (Exposición UI)
- **Acción:** Dockerización final de Streamlit y exposición a internet.
- **Configuración Docker:** `serverX`. Mapeo de volumen local (`/home/x/optifierro:/app`). Dependencias inyectadas vía `requirements.txt`. Redirección de red a `0.0.0.0:8501`.
- **Configuración Red:** Ingress en `serveri3` (`/srv/cloudflared/config.yml`) apuntando a `http://192.168.1.111:8501`.
- **Estado:** App visible en optifierro.montuschi.cl (HTTP 200 OK).
- **Pendiente inmediato:** Asegurar endpoint con Cloudflare Zero Trust.

### LOG DE CAMBIOS (Update)
- **Fecha:** 2026-03-02
- **Versión:** 0.5.0
- **Hito:** Implementación de UI Completa y Lógica Core.
- **Cambios:** Capa de Login (Admin/Visualizador), Sidebar con 8 secciones, Banner de Alerta Global (Discovery Engine), y Hub de Administración con 4 tarjetas (Usuarios, Sucursales, Logs, Geovictoria).
- **Fixes:** Solución definitiva a la pérdida de estado en DataFrames de Streamlit usando mutación de índices y copia de objetos.

- **Fecha:** 2026-03-01
- **Servicio:** OptiFierro V2 (Motor de Orquestación)
- **Host:** `serverX` (192.168.1.111)
- **Path:** `/home/x/stack/optifierro_v2/`
- **Puertos Asignados:** `8000` (API/Backend) / `8503` (UI Frontend Streamlit - Auto-asignado por colisión con V1).
- **Base de Datos:** `optifierro_db` en Postgres (Puerto `5433`)
- **Estado:** Fase Antigravity Atómica - Sección 1 (Estable)
---

> **FECHA:** 2026-03-04
> **PROYECTO:** OptiFierro V2
> **EVENTO:** Estabilización de Infraestructura de Red y Resolución de Conflictos Proxy.
> **CAMBIOS A NIVEL INFRAESTRUCTURA (CLOUDFLARE):** > - Se eliminó por completo la aplicación de Cloudflare Access (Zero Trust / Google Auth) para el subdominio `optifierro.montuschi.cl`. 
> - **Causa:** Colisión de políticas entre la interceptación de cookies asincrónicas de Cloudflare y los motores de "Tracking Prevention" de navegadores (Edge/Safari), lo cual bloqueaba la descarga de assets estáticos (JS/CSS) y WebSockets de Streamlit.
> - **Resolución:** La seguridad perimetral se delega al 100% a la capa de aplicación (Login nativo de Python en Streamlit). El túnel Cloudflare ahora actúa como un conducto de transporte puro (Clean Pipe) sin inspección de sesión.
> **DESCUBRIMIENTO DE RED (FALLBACK):**
> - Se mapeó la IP virtual asignada a `serverX` por la VPN FortiClient del cliente: `10.212.134.171`. 
> - Se validó el acceso "Client-to-Client" exitoso en el puerto `8503`, permitiendo un bypass total de internet público en caso de caídas de DNS o cachés envenenadas en el borde.
---

## 2026-03-06: Pivot Arquitectónico OptiFierro V2 (Integración IA Local)
- **Decisión:** Eliminación de n8n como middleware. Comunicación Frontend (Streamlit) <-> Backend (Python) 100% nativa.
- **Nuevas Capacidades UI:** 1. Recálculo en caliente (Reprogramar Turno vía `sucursal_id`).
  2. Componentes de ingesta NLP (texto libre a JSON).
  3. Renderizado XAI (Explainable AI) para justificación de ruteos.
  4. Sistema inmunológico visual (Toast alerts) para anomalías del motor.

  ## [ACTUALIZACIÓN ARQUITECTÓNICA] Backend y Motor V2 — Fecha: 2026-03-07
- **Eliminación de n8n:** Se descartó el uso de n8n como orquestador debido a riesgos de inestabilidad y loops. Todo el backend será un demonio monolítico en Python puro.
- **Topología Híbrida Definida:** 1. Frontend: Streamlit (`app.py`).
  2. Base de Datos Local: SQLite (`optifierro_v2.db`) para reglas duras y capacidades, reemplazando el archivo Excel manual.
  3. Motor Matemático: Heurística en Python (`motor_optimizacion.py`) determinista.
  4. Capa Cognitiva: Ollama local en serverX para NLP y Explainable AI (XAI).
- **Nuevo Criterio de Programación:** El ruteo ahora se calcula priorizando: 1) Días Atrasados, 2) Días Restantes, 3) Fecha IT. Se inyectó una penalización de Setup (15 min) por cambio de diámetro.
- **Contrato de Datos UI:** Se modificó el JSON de salida del motor para incluir la variable `calidad_acero` (ej. A630 vs A440) para alertas visuales en el Gantt.
- **Creación de Archivos Core:** Se crearon y probaron con éxito `database.py` y `motor_optimizacion.py`.

## 2026-03-08: Aclaración de Topología de Red (Air-Gap Lógico)
- **Corrección:** El Servidor TO *sí* tiene conexión a internet, pero la aplicación **OptiFierro V2** operará bajo un estricto **Air-Gap Lógico** por políticas de seguridad industrial.
- **Impacto Arquitectónico:** La arquitectura FastAPI + React (Vite) se mantiene. Se establece como regla estricta que el proceso de "build" del frontend debe empaquetar todos los assets (fuentes, iconos, CSS) localmente. Prohibido el uso de CDNs externas o telemetría en el código cliente.

## 2026-03-08: Asignación de Puerto FastAPI (OptiFierro V2)
- **Componente:** Capa de Traducción RESTful (Backend FastAPI).
- **Estado:** Operativo en `serverX` (PID registrado por Antigravity).
- **Cambio Topológico:** El servidor se ancló al puerto **8001** (colisión en el 8000 por stack de contenedores previo).
- **Impacto Frontend:** El servidor de desarrollo Vite y las llamadas de red en producción deben apuntar sus proxies a `http://localhost:8001`.

## 2026-03-08: Inyección de Layout Base (React + Tailwind v4)
- **Componente:** `src/index.css` y `src/App.tsx` (Frontend React).
- **Cambio Sistémico:** Se estableció el esquema visual "Dark Mode + Glassmorphism" definido en la directiva `ui-ux-pro-max.md`. 
- **Tailwind v4:** Se migró la configuración de variables a CSS nativo (`@theme`) para minimizar la carga de dependencias en el entorno Air-Gapped.
- **Conectividad:** Se implementó un hook `useEffect` en el layout principal para monitorear en tiempo real la salud del backend (`/api/health`) vía el proxy de Vite.

## 2026-03-08: Validación de Sinapsis Frontend-Backend
- **Estado:** Éxito. El proxy de Vite superó el bloqueo de red y conectó con FastAPI (Puerto 8001).
- **UI:** Componente `DatabaseStatus` renderizando correctamente en React, leyendo las tablas de `optifierro_v2.db` (sucursal, operador, maquina, etc.).
- **Siguiente Fase:** Iniciar migración 1:1 de las vistas de Streamlit (`seccion_1` a `seccion_8`) hacia la nueva arquitectura de enrutamiento en React (SPA).

## 2026-03-09: Arquitectura Bimodal y Topología de Cliente
- **Componentes:** `index.css`, `App.tsx`.
- **Cambio Sistémico 1:** Se mapearon las 8 secciones de navegación originales solicitadas por el cliente.
- **Cambio Sistémico 2:** Se implementó una arquitectura de Theme Toggle (Claro/Oscuro). Se modificó el `glass-panel` en CSS nativo para reaccionar al DOM, evitando hardcodear colores en las vistas futuras y reduciendo la deuda técnica.

## 2026-03-09: Personalización UI/UX (Requerimientos Cliente Final)
- **Componente:** `App.tsx`
- **Cambio Sistémico 1:** Rebranding a "Sistema de Planificación de la Producción" e integración de logo corporativo (`/public/logo.png`).
- **Cambio Sistémico 2:** Telemetría Silenciosa. Indicador de API oculto por defecto; renderiza alerta roja solo en desconexión.
- **Cambio Sistémico 3:** Se mapearon las 3 sucursales (Calama, Cerrillos, Coronel) y los horarios reales de turno (Día L-V, Noche L-S madrugada).

## 2026-03-09: Corrección de Motor UI y Simplificación
- **Componentes:** `index.css`, `App.tsx`
- **Cambio Sistémico 1:** Se estableció el Tema Claro como default por requerimiento de legibilidad del cliente.
- **Cambio Sistémico 2:** Se parcheó el motor de Tailwind v4 (`@variant dark`) para forzar el modo oscuro por clase en lugar de media query del SO. Esto corrige el fallo de contraste en tipografías.
- **Cambio Sistémico 3:** Se redujo la carga cognitiva en el selector de Turnos, limitándolo a "Día" y "Noche".

## 2026-03-09: Inyección de Componentes de Dominio (Gestor de Máquinas)
- **Nuevos Archivos:** `src/components/domain/GestorMaquinas.tsx`
- **Cambio Sistémico 1:** Se creó el componente de Data Table para la gestión de máquinas, aplicando diseño bimodal (Claro/Oscuro) y manejo de estados (Loading, Error, Empty).
- **Cambio Sistémico 2:** Se enlazó el componente al enrutador principal en `App.tsx` para la vista `gestor_maquinas`.

## 2026-03-09: Reestructuración de Dominio (Gestor de Máquinas)
- **Componentes Modificados:** `src/components/domain/GestorMaquinas.tsx`
- **Cambio Sistémico 1:** Se alineó la estructura de datos a la lógica de negocio (eliminación de columna "Capacidad").
- **Cambio Sistémico 2:** Se implementó un sistema de navegación interna por Pestañas (Tabs) para replicar la UX original de Streamlit.
- **Cambio Sistémico 3:** Se preparó el andamiaje para consumir los 4 nuevos endpoints RESTful (`/api/maquinas`, `/diametros`, `/hebras`, `/restricciones`).

## 2026-03-09: Normalización de Contrato y Edición Matricial
- **Componentes:** `src/components/domain/GestorMaquinas.tsx`
- **Cambio Sistémico 1:** Adaptación al nuevo contrato del Backend. Las columnas dinámicas ahora leen directamente el formato `Xmm` y procesan enteros (`1`/`0`) como booleanos.
- **Cambio Sistémico 2:** Habilitación de ciclo Update (Edición) para la matriz de Diámetros (mediante Checkboxes) y la matriz de Hebras (mediante Number Inputs).
- **Cambio Sistémico 3:** El controlador de guardado ahora enruta dinámicamente el `PUT` hacia `/api/maquinas/...`, `/api/maquinas/diametros/...` o `/api/maquinas/hebras/...` según la pestaña activa.

## 2026-03-09: Hotfix UI (Pestaña Restricciones)
- **Componentes:** `src/components/domain/GestorMaquinas.tsx`
- **Cambio Sistémico:** Se restauró el renderizador genérico de columnas y filas para la pestaña "Restricciones", el cual había sido omitido durante la refactorización de matrices dinámicas.

## 2026-03-09: Implementación de Súper Matriz de Operadores
- **Nuevos Componentes:** `src/components/domain/GestorOperadores.tsx`
- **Cambio Sistémico 1:** Se fusionaron las vistas de Nómina y Competencias en una "Súper Matriz" unificada, reduciendo la carga cognitiva.
- **Cambio Sistémico 2:** Se implementó lógica de detección de "Nuevo Recurso" (Onboarding). Si un operador tiene 0 máquinas asignadas, el sistema despliega una alerta visual para requerir la atención del administrador.
- **Cambio Sistémico 3:** Se habilitó el ciclo Update (Checkboxes) conectado a `/api/operadores/{operador}`.

## 2026-03-09: Parche de Usabilidad y Contexto Global (Requerimientos PO)
- **Componentes:** `App.tsx`, `GestorOperadores.tsx`, `GestorMaquinas.tsx`
- **Cambio Sistémico 1 (Contexto Global):** Se cableó el selector del Sidebar (`globalSucursal`). Ahora toda la UI reacciona y filtra los datos según la planta seleccionada (Calama, Cerrillos, Coronel).
- **Cambio Sistémico 2 (Scroll & Responsive):** Se reparó el bug de `overflow` en el Layout principal (CSS Flexbox), permitiendo el scroll vertical infinito en las Data Tables y añadiendo adaptabilidad básica para pantallas menores.
- **Cambio Sistémico 3 (Aislamiento de Planta):** La Súper Matriz ahora oculta dinámicamente las columnas de las máquinas que no pertenecen a la sucursal seleccionada, evitando asignaciones erróneas.
- **Cambio Sistémico 4 (Bloqueo de Llave Primaria):** Se habilitó la edición de "Sucursal", pero se mantuvo el "Usuario" como `readonly` para proteger la integridad de sincronización con el ERP Cubigest.

## 2026-03-09: Hotfix Estructural y Contextual (PO QA)
- **Componentes:** `App.tsx`, `GestorOperadores.tsx`
- **Cambio Sistémico 1 (Filtro Estricto de Máquinas):** El `GestorOperadores` ahora realiza un cross-fetch con `/api/maquinas` para renderizar únicamente las columnas de máquinas físicamente existentes en la sucursal seleccionada.
- **Cambio Sistémico 2 (UX Renderizado Condicional):** Se reincorporó el filtro global de "Turno", configurado para renderizarse exclusivamente en el módulo de "Programación".
- **Cambio Sistémico 3 (Scroll Bidireccional):** Se ajustó el motor CSS de la Data Table (`min-w-max`) para soportar scroll horizontal infinito, vital para visualizar matrices densas como las de Cerrillos.

## 2026-03-09: Integración de Catálogo Maestro de Formas (Cubigest)
- **Nuevos Componentes:** `src/components/domain/GestorPiezas.tsx`
- **Cambio Sistémico 1:** Se conectó el Frontend con el CDN interno de Cubigest (puerto 86) para renderizar en vivo los diagramas geométricos de las piezas sin sobrecargar el Frontend.
- **Cambio Sistémico 2:** Implementación de Paginación Server-Side (bloques de 20 registros) y Motor de Búsqueda por `id_forma` para manejar el catálogo masivo.
- **Cambio Sistémico 3:** Súper Matriz de Asignación. Los administradores ahora pueden encender/apagar qué máquinas (filtradas por sucursal) están homologadas para fabricar cada geometría.

## 2026-03-09: Hotfix API Gestor de Piezas
- **Componentes:** `src/components/domain/GestorPiezas.tsx`
- **Cambio Sistémico:** Se inyectó el parámetro obligatorio `&sucursal=` en la query string de `/api/piezas/formas` para resolver el error HTTP 422 de validación en FastAPI. Se añadió reactividad para refetching al cambiar de filial.

## 2026-03-09: Implementación de Gestor de Materia Prima (Fase 1 - Mock INET)
- **Nuevos Componentes:** `src/components/domain/GestorMatPrima.tsx`
- **Cambio Sistémico 1:** Se construyó la tabla de inventario cruzado para detectar quiebres de stock tempranos.
- **Cambio Sistémico 2:** Implementación de cálculo en tiempo real: `Necesidad = Stock Cubigest + Tránsito - Comprometido`.
- **Cambio Sistémico 3:** Poka-Yoke visual. Las necesidades negativas (quiebre de stock) se iluminan automáticamente en rojo alerta.
- **Cambio Sistémico 4:** Se enlazó el módulo al filtro de estado global de la sucursal.

## 2026-03-09: Refactor API Gestor de Materia Prima
- **Componentes:** `src/components/domain/GestorMatPrima.tsx`
- **Cambio Sistémico 1:** Se actualizó el endpoint a `/api/materias_primas` según el nuevo contrato del dominio.
- **Cambio Sistémico 2:** Adopción del patrón "Fat Server". Se eliminó el cálculo de necesidad en el Frontend, pasando a consumir el valor `necesidad` pre-calculado por el motor Backend.

## 2026-03-09: Mejora de UX Analítica en Gestor de Materia Prima
- **Componentes:** `src/components/domain/GestorMatPrima.tsx`
- **Cambio Sistémico 1:** Se incorporó un motor de búsqueda en tiempo real (Client-Side) que filtra simultáneamente por Código de Insumo o Descripción.
- **Cambio Sistémico 2:** Se habilitó el ordenamiento bidireccional (Ascendente/Descendente) en todas las columnas de la tabla para facilitar el análisis de quiebres de stock.

## 2026-03-09: Despliegue de Motor de Programación (Carta Gantt)
- **Nuevos Componentes:** `src/components/domain/GestorProgramacion.tsx`
- **Cambio Sistémico 1:** Se construyó el lienzo interactivo del Gantt usando arquitectura de Estado Plano (Flat State) para maximizar el rendimiento.
- **Cambio Sistémico 2:** Motor visual de tiempo. Las barras calculan su posición (X) y ancho en base a la diferencia de minutos dentro del turno seleccionado.
- **Cambio Sistémico 3:** Poka-Yoke de Calidad. Barras de acero estándar (A630) usan paleta neutra; calidades especiales se renderizan en ámbar/rojo de alerta.
- **Cambio Sistémico 4:** Tooltip analítico. Al hacer hover sobre una IT, se despliega una tarjeta con los campos críticos (Obra, Elemento, Formato, Kilos).
- **Cambio Sistémico 5:** Bandeja de "Backlog" inferior para ITs pendientes de asignación.

## [PROYECTO: OptiFierro] - Módulo Geovictoria Scraper
- **Estado:** En Diseño / Fase 0.
- **Tecnología:** Python + Playwright (Dockerizado en serverX).
- **Dependencia Externa:** Portal Web Geovictoria.
- **Destino de Datos:** optifierro_v2.db (Tabla: asistencia_diaria).

## [ACTUALIZACIÓN INVENTARIO] - 2026-03-10
**Proyecto:** OptiFierro V2
**Componente:** Geovictoria Scraper
- **Ruta:** `/home/x/stack/optifierro_v2/geovictoria_scraper/`
- **Stack:** Python 3.11, Docker, Playwright (Stealth Mode).
- **Rol:** Extracción diaria de asistencia. Operación 100% automatizada (evasión de Captcha vía persistencia de sesión).

## [ACTUALIZACIÓN INVENTARIO] - 2026-03-10
**Proyecto:** OptiFierro V2 (Geovictoria Scraper)
**Incidencia:** Contenedor Docker en serverX no resolvía dominios externos (ERR_NAME_NOT_RESOLVED).
**Causa:** Conflicto de resolución DNS con Pi-hole (serveri3).
**Solución (Hardcode):** Se inyectaron DNS públicos (1.1.1.1, 8.8.8.8) a nivel de `docker-compose.yml` aislando al scraper del filtrado de la red local.
**Ajuste Dependencias:** `playwright-stealth` fijado a v1.0.6 para compatibilidad con `sync_playwright`.

## [ACTUALIZACIÓN INVENTARIO] - 2026-03-10
**Proyecto:** OptiFierro V2 (Geovictoria Scraper)
**Corrección Arquitectónica:** URL de login corregida de `secure.geovictoria.com` a `clients.geovictoria.com/account/login`.
**Avance:** Fase 2 (Login payload). Implementación de tipeo asíncrono aleatorio (50-250ms) para evadir heurísticas de detección de bots en el formulario.

## [ACTUALIZACIÓN INVENTARIO] - 2026-03-11
**Módulo:** Geovictoria Scraper (Fase 3 - ETL)
**Estrategia:** Interceptación de evento de descarga nativa (.xlsx) vía Playwright, descartando scraping de DOM debido a estructura tabular compleja.
**Dependencias agregadas:** `openpyxl`, `sqlalchemy`.
**Reglas de Negocio:** Incorporado mapeo estático de sucursales (Vista Clara=1, Calama=2, Coronel=3, Quilicura=4) validado con Jefatura de Planta.

## [ACTUALIZACIÓN INVENTARIO] - 2026-03-11
**Módulo:** Geovictoria Scraper (Fase ETL)
**Cambio Arquitectónico (DDD):** Refactorización semántica de la entidad de negocio. "Operador" cambia a "Colaborador".
**Ajuste DB:** Se elimina tabla `asistencia_operadores`. Se crea tabla `asistencia_colaboradores`.
**Ajuste Columnas:** `rut_operador` -> `rut_colaborador`, `nombre_operador` -> `nombre_colaborador`.
**Restricciones aplicadas:** Normalización estricta de `sucursal_id` (1-4) y `estado` (PRESENTE, AUSENTE, LICENCIA, FALTA) vía reglas de Regex en Pandas.

## [ACTUALIZACIÓN OPERATIVA] - 2026-03-11
**Proyecto:** OptiFierro V2 (React + FastAPI)
**Documento:** SOP de Arranque en Frío (Standard Operating Procedure)
**Contexto:** Tras la migración de la interfaz nativa (Streamlit) a la arquitectura desacoplada (React + FastAPI), el ecosistema se aisló en un nuevo `workdir` (`optifierro_v2_frontend`) para evitar colisiones de dependencias de Python.

**Secuencia Oficial de Arranque en `serverX`:**
Para levantar la plataforma tras un apagado total del servidor, se deben levantar 3 componentes en orden:

1. **Motor Cognitivo (Ollama):**
   - Asegurar que el contenedor Docker esté activo para las parametrizaciones NLP.
   - Comando: `sudo docker start ollama`

2. **Backend (FastAPI):**
   - El motor debe iniciar en su carpeta dedicada para ejecutar el `lifespan` que inyecta la DB a la RAM.
   - Ruta: `cd /home/x/stack/optifierro_v2_frontend/backend`
   - Comando: `source venv/bin/activate` (si aplica) && `uvicorn main:app --host 0.0.0.0 --port 8001 --reload`

3. **Frontend (Vite / React):**
   - El servidor de desarrollo UI.
   - Ruta: `cd /home/x/stack/optifierro_v2_frontend/frontend`
   - Comando: `npm run dev`

   ## [ACTUALIZACIÓN INVENTARIO] - 2026-03-11 (Standby)
**Módulo:** Geovictoria Scraper (Fase ETL)
**Hallazgo 1 (Estructura de Datos):** El archivo exportado por Geovictoria es un "Falso Excel" (probablemente HTML o TSV con extensión alterada). Se requerirá ajuste en el parser de Pandas una vez verificado su raw text.
**Hallazgo 2 (Diccionario de Entidades):** Se recuperó el maestro de sucursales original. El mapeo del Backend deberá actualizarse para reflejar los IDs reales (10=Vista Clara, 1=Calama, 14=Coronel) y evitar colisiones de Foreign Keys.
**Estado de Operación:** Pausado por el Product Owner. A la espera de reanudación para aplicar inspección de archivo (`head / cat`) y parche final de DB.

## [REPARACIÓN TÉCNICA] - Sincronización de Contratos y Estabilidad UI
**Fecha:** 2026-03-11
**Módulos Afectados:** Gestor de Averías (Frontend) + Motor de Programación (Backend/Gantt)

### 1. Resolución de "Amnesia de Inicio" (Backend)
- **Incidencia:** Tras el reinicio del `serverX`, el endpoint `/api/programacion` devolvía un Error 500 (Validation Error).
- **Causa:** Desajuste entre el modelo Pydantic (exigía `sucursal_id`) y la inyección en el `lifespan` de FastAPI (enviaba `sucursal`).
- **Solución:** Estandarización del esquema de datos en el ciclo de vida del servidor. Se implementó un *lifespan context manager* para asegurar la persistencia de las 11 máquinas de Cerrillos en la RAM al arrancar.

### 2. Sincronización de Mapeo PascalCase (Frontend)
- **Incidencia:** La tabla de Averías mostraba "Sin datos" o `#undefined`.
- **Causa:** El Backend entrega llaves en PascalCase (`Maquina`, `Sucursal`, `Id`) mientras que el Frontend buscaba camelCase.
- **Solución:** Se actualizó el mapper de `GestorAverias.tsx` para soportar ambas nomenclaturas y se inyectó un filtro por `sucursal` en el cliente para asegurar la consistencia visual.

### 3. Preservación Rígida de Duración (Gantt)
- **Incidencia:** Los PIDs (cajitas azules) colapsaban a una línea (duración 0) tras ser reasignados.
- **Solución:** Implementación de cálculo de delta en milisegundos (`msDuration`). Al soltar un PID, el sistema captura la duración original y la suma a la nueva `hora_inicio`, garantizando que el ancho de la caja sea inmutable independientemente del movimiento.

### 4. Refinamiento UX / UI
- **Simplificación de Glosas:** Se eliminó el término "Poka-Yoke" de los títulos para mejorar la legibilidad del operario.
- **Títulos Dinámicos:** El subtítulo superior ahora responde al estado global: `"Monitoreo en ${sucursal}"`.
- **Limpieza de Tooltips:** Se añadió un reset de estado en `onDragStart` para eliminar tarjetas de detalles pegadas durante el movimiento.

## 2026-03-11 BÚFER DE ACTUALIZACIÓN: LOG DE CAMBIOS (v2.x.x)
🚀 NUEVAS CARACTERÍSTICAS (FEATURES)

Módulo Vista Semanal (Fase 1): Creación del componente base VistaSemanal.tsx con selectores dinámicos de proyección (Semana Actual, Próxima, Subsiguiente) e integración de KPIs de Kgs y calibres de acero. (Nota: En proceso de re-densificación visual).

Módulo Administración (Fase 1): Despliegue del hub de control Administracion.tsx con 4 pestañas operativas (Usuarios, Sucursales, Logs, Geovictoria) y la alerta global de detección de nuevos parámetros en la base de datos Cubigest.

🛠️ ARQUITECTURA Y BACKEND (API & CONTRATOS)

Flexibilización de Pydantic (Gantt): Se modificó el esquema del backend para aceptar Union[int, str] en la reasignación de PIDs, permitiendo el flujo bidireccional entre máquinas reales (int) y la Bolsa de Trabajo ("PENDIENTE").

Traductor de Sucursales: Se eliminó el "sobre-filtrado" destructivo en el Frontend. El cliente ahora envía estricta y únicamente el SucursalId (ej. ?sucursal=1 para Cerrillos) y renderiza el array puro entregado por el Backend.

Tipado Estricto de Llaves Primarias: Refactorización transversal en Gestor de Máquinas, Piezas, Operadores y Averías para abandonar el genérico id y consumir estrictamente MaquinaId desde el JSON anidado del backend.

🐛 BUGFIXES CRÍTICOS Y POKA-YOKES (UI/UX)

Resolución Error 422 (Registro de Averías): Se corrigió la discrepancia del payload en el POST /api/averias/registrar, pasando de maquina_id a MaquinaId, restaurando la comunicación con el LLM (Qwen) y la base de datos.

Poka-Yoke Visual en Gantt (Bloqueo por Falla): Confirmada la reactividad en tiempo real: al registrar una avería, la Carta Gantt tiñe la fila de la máquina de rojo y rechaza físicamente el drop de nuevas tareas.

Anti-Colapso de Fechas (Gantt): Se corrigió el bug de huso horario (Timezone) que colapsaba las tareas a "0px" (líneas invisibles) al cruzar la medianoche. Se implementó matemática de marcas absolutas (getTime()) y un seguro de renderizado visual mínimo de 2 horas.

Resiliencia de CDN (Gestor de Piezas): Se inyectó un deflector de red (onError) en los diagramas de formas. Si el servidor de imágenes de Cubigest (192.168.1.195:86) no responde, la UI oculta el error silenciosamente en lugar de romper la matriz.

Desbloqueo de UI (Gestor de Averías): Se eliminó el estrangulamiento CSS (overflow-hidden) y se inyectaron eventos onClick en las filas de la tabla para permitir la visibilidad y activación del botón de "Analizar Falla".

## [2026-03-15] Motor V2 — Primera Ejecución Real con Datos de Cubigest

### Hitos de la sesión
- **Motor operativo:** `POST /api/programacion/generar` retorna 200 con datos reales.
  Resultado Cerrillos turno día: 174/500 etiquetas asignadas, 18.085 Kgs totales.
- **Terminología corregida:** "PID" → "Etiqueta" en backend y frontend.
  Unidad visual del Gantt: `OBRA-(totalViajes)/(viajeActual)`.

### Archivos nuevos generados en serverX
| Archivo | Ruta | Descripción |
|---|---|---|
| `motor_v2.py` | `backend/` | Motor de optimización completo (Fase 1 + Fase 2) |
| `extractor_rutas.py` | raíz proyecto | Extractor historial Cubigest → matriz_rutas.json |
| `matriz_rutas.json` | raíz proyecto | 2.135 combinaciones únicas (3 sucursales, 12 meses) |
| `deltat_por_forma_maquina.csv` | raíz proyecto | 352 medianas de DeltaT por (IdForma, Máquina, Sucursal) |
| `openssl_legacy.cnf` | raíz proyecto | Fix SSL para conexión pyodbc → SQL Server legacy |

### Decisiones arquitectónicas
- **Mapa definitivo de sucursales Cubigest:**
  `1=Calama · 4=Cerrillos (alias Santiago) · 14=Coronel`
  IDs excluidos: 7/18 (TOSOL, instrucción cliente) · 10/15 (inactivos)
- **Duración de trabajos:** mediana de DeltaT histórico por (IdForma, Máquina, Sucursal).
  Sin hora de término en Cubigest → se calcula como delta entre inicio de trabajos consecutivos en misma máquina.
- **Complejidad de forma:** índice desde `DetalleFormas` (coordenadas XY, NroPuntos + NroAngulos).
  477 formas únicas, rango 1-14 puntos, promedio 6.5.
- **FP-LC:** máquina virtual sin operador requerido. Criterio: IdForma=1, largo 6000-12000mm, diámetro AD.
- **Ventana de etiquetas pendientes:** -30 días (quiebres stock acero) / +21 días (cubre Vista Semanal).
- **Acero delgado (AD):** diámetro ≤ 16mm · **Acero grueso (AG):** diámetro ≥ 18mm.
- **OPENSSL_CONF:** debe setearse antes de cualquier import de pyodbc.
  Para Docker/TO: agregar variable de entorno en `docker-compose.yml`.

### Protocolo de trabajo establecido
- **Claude:** motor lógico, backend Python/FastAPI, algoritmos, SQL.
- **Gemini:** frontend React, componentes UI, consumo de contratos JSON.
- **Montu:** arquitecto, orquestador, QA, deploy.
- Contrato JSON del Gantt entregado a Gemini para construcción del componente.

### Pendientes inmediatos
- [ ] Gemini construye componente Gantt sobre contrato JSON entregado.
- [ ] Deploy en TO: Git push/pull + ajuste `docker-compose.yml` con `OPENSSL_CONF`.
- [ ] Geovictoria: integrar scraper cuando cliente entregue credenciales.
- [ ] Confirmar con cliente unidad de largo en Cubigest (metros vs milímetros) para FP-LC.
- [ ] Confirmar máquinas inactivas de Cerrillos: EURA 20_2, FORMULA 12, CURVADORA 2, VRP 2 Schnell, series 101-111.

═══════════════════════════════════════════════════
FECHA: 2026-03-30
PROYECTO: Infraestructura de Agentes (Antigravity)
═══════════════════════════════════════════════════

[CAPABILITY: MANIPULACIÓN DE ARCHIVOS MS OFFICE & POWER BI]
- Integración de Antigravity (AG) con entorno Python en serverX para manipulación de binarios.
- Dependencias inyectadas: `pandas`, `openpyxl`, `python-docx`, `python-pptx`.
- Instalación de motor `.NET 8.0` y utilidad `pbi-tools` (v1.2.0 Core) para desacoplamiento y compilación de archivos `.pbix` / `.pbip`.
- Implementación de topología híbrida: AG actúa como Orquestador (ECU) y rutea tareas cognitivas de datos hacia Ollama local (`qwen2.5-coder` / `qwen3.5:9b`) vía `http://localhost:11434/api/generate`.
- Smoke Test validado: Flujo completo Excel → Pandas → Ollama → DOCX automatizado sin errores (Exit Code 0).

---

# LOG DE CAMBIOS — 01 Abril 2026

## Incidente: Apagón Abrupto ServerX + Recuperación Completa

### Causa Raíz
Apagón eléctrico abrupto en serverX. Consecuencias en cadena:
- Disco PUSKILL (sistema original) con sectores dañados
- Corrupción de /var/lib/docker/network/files/local-kv.db
- Corrupción de /var/lib/containerd/io.containerd.metadata.v1.bolt/meta.db
- Contenedor openwebui_knowledge-ragapi-1 en estado zombie permanente

### Acciones de Recuperación (en orden)
1. Backup ARCA: 695GB clonados al disco Toshiba externo ✅
2. Clonación PUSKILL → WDC con ddrescue (100% completado) ✅
3. GRUB instalado en WDC ✅
4. fsck reparó filesystem ✅
5. fstab corregido: línea /mnt/storage comentada (disco ARCA desconectado) ✅
6. ServerX arrancando desde WDC ✅
7. Docker network DB corrupta eliminada: /var/lib/docker/network/files/local-kv.db ✅
8. Containerd metadata DB corrupta eliminada: /var/lib/containerd/io.containerd.metadata.v1.bolt/meta.db ✅
9. Containerd y Docker reiniciados limpiamente ✅
10. Zombie openwebui_knowledge-ragapi-1 eliminado al reconstruir meta.db ✅
11. Redes Docker recreadas manualmente post-reconstrucción ✅
12. Stack completo relanzado contenedor por contenedor ✅

### Limpieza de Contenedores (decisión arquitectural)
Contenedores eliminados permanentemente (docker rm -f):
- open-webui (no se usa)
- openwebui_knowledge-ragapi-1 (roto + no se usa)
- n8n (no se usa)
- sim-with-ollama-simstudio-1, realtime-1, db-1
- superagenda_frontend, backend, scraper
- optifierro_app, optifierro_db, optifierro-adminer-1 (producción en TO)
- geovictoria_api (producción en TO)

Contenedores detenidos (stop sin rm, volúmenes preservados):
- pegas-pegas-web-1
- pegas-pegas-api-1

### Estado Final Stack ServerX
| Contenedor | Estado |
|---|---|
| ollama | ✅ Up |
| portainer | ✅ Up |
| superagente-web | ✅ Up |
| superagente-orchestrator | ✅ Up |
| superagente-api | ✅ Up |
| superagente-qdrant | ✅ Up |
| web | ✅ Up |
| retroassembly | ✅ Up |
| visual-voice-visualvoice-1 | ✅ Up |
| mcp-core-mcp-core-1 | ✅ Up |
| pegas-pegas-web-1 | ⏸️ Stopped (modificar antes de relanzar) |
| pegas-pegas-api-1 | ⏸️ Stopped (modificar antes de relanzar) |

### Notas Técnicas Importantes
- /mnt/storage: SIN DISCO. El disco ARCA (UUID 704473f4-b005-4bf8-91bf-0c9bf0e8d150) fue usado para recuperación y está desconectado. Línea comentada en fstab.
- /mnt/extra (miau_nube, sdb1): montado correctamente ✅
- Disco de sistema: WDC (clonado desde PUSKILL). PUSKILL con sectores dañados — NO reconectar sin diagnóstico.
- GPU P104-100: operativa, Persistence Mode ON ✅
- Openclaw/Clawdio: NO está en serverX. Está en serveri3 (/srv/openclaw). No levantar en serverX.

### Pendientes Post-Incidente
- [ ] Configurar teclado KDE (tildes y símbolos perdidos post-reboot)
- [ ] Desactivar Powerlevel10k en zsh (prompt con símbolos molestos)
- [ ] Aplicar 127 actualizaciones pendientes: sudo apt upgrade
- [ ] Comprar pila CR2032 para CMOS (reloj derivará sin ella)
- [ ] Ubicar compose de searxng y qdrant standalone y levantar
- [ ] Evaluar disco PUSKILL: diagnóstico con smartctl antes de cualquier uso
- [ ] Documentar nuevo disco de sistema (WDC) en INVENTARIO_MAESTRO
---
## 2026-05-24 — Optimización de Tokens — Stack Claude (toda la infra)

**Contexto:** Consumo elevado de tokens detectado por Montu. Mi TI (Miaude) ejecutó implementación autónoma vía protocolo Miaude-sin-Montu en los 4 nodos de la infraestructura.

### Cambios aplicados

**MacBook (user: montu)**
- : agregado  y 
- : creado — excluye , , , , , , , , binarios

**serverX (192.168.1.111, user: x)**
- : agregado  y  (preservando hooks SessionStart/PostToolUse/Notification)
- : creado (patrón global)
-  creado en proyectos: , , , 

**serveri3 (192.168.1.211, user: i3)**
- : CREADO desde cero (no existía) — , 
- : creado

**TO — PROMETHEUS-AI-CORE (192.168.1.65, user: OptiFierro)**
- : , 
- Plugins CC reducidos de **11 → 2** (solo  y  — críticos OptiFierro; eliminados 9 plugins de overhead puro)
- : creado

### Protocolos operacionales establecidos (no requieren archivo)
-  al llegar al 40% de contexto
-  en cambio de proyecto, no al final del día
- Referencias a archivos específicos, no a directorios (ahorro 10k-25k tokens/sesión)
- /Gemini para coding rutinario;  solo para arquitectura y RCA

### Impacto estimado
- : reducción 30-50% tokens por respuesta compleja
- : elimina indexación de cachés, SQLite, logs, modelos pesados
- Plugins TO 11→2: ~30.000-50.000 tokens menos por sesión en PROMETHEUS
- : elimina telemetría y tráfico de fondo no esencial

### Agente ejecutor
Miaude (Claude.ai Desktop) vía Desktop Commander — verificación cruzada en todos los nodos post-implementación ✅


---
## 2026-05-24 — Optimización de Tokens — Stack Claude (toda la infra)

**Contexto:** Consumo elevado de tokens detectado por Montu. Mi TI (Miaude) ejecutó implementación autónoma vía protocolo Miaude-sin-Montu en los 4 nodos de la infraestructura.

### Cambios aplicados

**MacBook (user: montu)**
- settings.json: agregado MAX_THINKING_TOKENS=10000 y CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
- .claudeignore global: creado — excluye __pycache__, node_modules, *.db, *.sqlite, .git, *.log, *.gguf, .env, binarios

**serverX (192.168.1.111, user: x)**
- settings.json: agregado MAX_THINKING_TOKENS=10000 y CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 (preservando hooks SessionStart/PostToolUse/Notification existentes)
- .claudeignore global: creado en ~/.claudeignore
- .claudeignore por proyecto creado en: optifierro_v2_frontend, scrap_geovictoria, visual-voice, pegas2

**serveri3 (192.168.1.211, user: i3)**
- settings.json: CREADO desde cero (no existia) — MAX_THINKING_TOKENS=10000, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
- .claudeignore global: creado en ~/.claudeignore

**TO — PROMETHEUS-AI-CORE (192.168.1.65, user: OptiFierro)**
- settings.json: MAX_THINKING_TOKENS=10000, CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1
- Plugins CC reducidos de 11 a 2 (solo chrome-devtools-mcp y github — criticos para OptiFierro; 9 plugins de overhead eliminados)
- .claudeignore en proyecto optifierro: creado

### Protocolos operacionales establecidos
- /compact con instrucciones al 40% de contexto (Focus on architecture decisions, file paths modified, error messages)
- /clear en cambio de proyecto, no al final del dia
- Referenciar archivos especificos en vez de directorios (ahorro 10k-25k tokens/sesion)
- ccor1/Gemini para coding rutinario; cca solo para arquitectura y RCA

### Impacto estimado
- MAX_THINKING_TOKENS: reduccion 30-50% tokens por respuesta compleja
- .claudeignore: elimina indexacion de caches, SQLite, logs, modelos pesados
- Plugins TO 11 a 2: ~30.000-50.000 tokens menos por sesion en PROMETHEUS
- NONESSENTIAL_TRAFFIC: elimina telemetria y trafico de fondo no esencial

### Agente ejecutor
Miaude (Claude.ai Desktop) via Desktop Commander — verificacion cruzada en todos los nodos post-implementacion OK


---
## 2026-06-03 — Arquitectura Multi-Agente Hermes: Espinita + Risko

**Autor:** Miaude (autónomo, Protocolo Miaude-sin-Montu)
**Sesión:** ~6 horas nocturnas (Montu durmiendo)

### Contexto
Montu propuso separar responsabilidades de Clawdio en agentes especializados independientes, cada uno con su propio HERMES_HOME, personalidad, modelo y canal de comunicación. Espinita y Risko fueron los primeros en desplegarse.

### Espinita — hermes-espinita (NUEVO)
- **Imagen:** nousresearch/hermes-agent:latest
- **Compose:** /home/i3/espinita/docker-compose.yml
- **HERMES_HOME:** /home/i3/espinita/data/ (bind mount)
- **Docs edificio:** /home/i3/espinita/docs/
- **Bot Telegram:** @Espinita1010_bot (token creado por Montu en @BotFather al retorno)
- **WhatsApp:** número prepago pareado (Baileys nativo Hermes, bridge en port 3000)
- **Modelo:** deepseek/deepseek-v4-flash vía OpenRouter
- **Personalidad:** Conserje virtual Edificio Los Espinos, culto-formal, **masculino** (referencia al personaje televisivo chileno de los 80s + coincidencia con nombre del edificio)
- **Comportamiento grupos WA:** group_mentions_only=true (invocar con @espinita)

#### Fixes aplicados durante despliegue
1. `user: "1000:1000"` en compose → removido: el init script de hermes-agent requiere root para instalar bridge npm en `/opt/hermes/`
2. Chown recursivo a UID 10000 vía alpine: `docker run --rm -v ./data:/data alpine chown -R 10000:10000 /data`
3. Lock files obsoletos en `.local/state/hermes/gateway-locks/` → eliminados en caliente para desbloquear reconexión Telegram

### Risko — hermes-risko (REACTIVADO como Docker)
- **Imagen:** nousresearch/hermes-agent:latest
- **Compose:** /srv/risko/docker-compose.yml (reemplaza setup OpenClaw obsoleto)
- **HERMES_HOME:** /home/i3/.risko/ (bind mount, directorio preexistente)
- **Bot Telegram:** @Risko_OP_bot (token preexistente en .env)
- **Modelo:** actualizado gemini-2.5-flash → **deepseek/deepseek-v4-flash vía OpenRouter**
- **Auxiliares:** todos migrados a OpenRouter (eliminado Gemini trap — provider auto detectaba GOOGLE_API_KEY)
- **Fix aplicado:** `user: "1000:1000"` en compose (HERMES_HOME preexistente compatible con UID 1000)
- Telegram only, sin WhatsApp

### Backlog generado en sesión
- **BACKLOG-ESPINITA-01:** Agrupar docs edificio desde MacBook → /home/i3/espinita/docs/ + fix Samba
- **AGENTE-CARLITOS:** Coordinador MS, vive en serverX, config TBD
- **AGENTE-AURORA:** Documentadora técnica, modelo local, femenino, honra *La Aurora de Chile*

---
## 2026-05-24 — Fix SSH Clawdio-v2 (container) → serverX

**Contexto:** Rabín (Hermes en container clawdio-v2) no podia hacer SSH a serverX. Detectado al intentar documentar el LOG de optimizacion de tokens.

### Root Cause Analysis
- El container clawdio-v2 tiene un volumen Docker en /opt/data (home del user hermes, uid 10000)
- Las llaves SSH existian en /opt/data/.ssh/ pero con ownership root:root
- SSH rechaza llaves con ownership incorrecto — autenticacion fallaba silenciosamente
- Ademas, faltaba ssh config y known_hosts para serverX

### Acciones ejecutadas (en container clawdio-v2 via docker exec)
- chown hermes:hermes /opt/data/.ssh/ y los archivos id_ed25519, id_ed25519.pub
- chmod 600 /opt/data/.ssh/id_ed25519
- Creado /opt/data/.ssh/config con entradas para Host serverx y 192.168.1.111 (User x, IdentityFile correcto)
- ssh-keyscan 192.168.1.111 >> /opt/data/.ssh/known_hosts
- La llave publica clawdio-v2@serveri3 ya estaba en authorized_keys de serverX (no requirio cambio en serverX)

### Verificacion
- docker exec -u hermes clawdio-v2 ssh x@192.168.1.111 echo OK -> CONEXION_OK
- docker restart clawdio-v2 + test post-restart -> POST_RESTART_OK
- Persistencia confirmada: /opt/data esta en volumen Docker clawdio-v2_clawdio_data

### Persistencia
Los cambios persisten en reinicios y recreaciones del container porque /opt/data es un volumen Docker nombrado (no un layer efimero del container).

### Agente ejecutor
Miaude (Claude.ai Desktop) via Desktop Commander — fix completo sin intervencion de Montu


---
## 2026-06-01 — Claude Desktop + Antigravity IDE en serverX

**Contexto:** Setup de entorno de trabajo gráfico en serverX (KDE/NoMachine) con Claude Desktop, Antigravity IDE y MCPs locales.

### Instalaciones
- **Google Chrome** — repo oficial Google (apt)
- **Claude Desktop linux v1.9255.2** — via aaddrick/claude-desktop-debian (apt)
- **Antigravity CLI** → `/home/x/.local/bin/agy`
- **Antigravity IDE** → `/home/x/.local/share/antigravity-ide/` + symlink en `.local/bin`
- **Extensión MCP bridge:** `cafetechne.antigravity-link-extension-1.0.16-universal`

### MCPs configurados en Claude Desktop
Config: `~/.config/Claude/claude_desktop_config.json`

| MCP | Comando | Notas |
|-----|---------|-------|
| clawdio | `/home/x/bin/hermes-mcp-bridge` | SSH → i3@192.168.1.211 → `hermes mcp serve` |
| desktop-commander | `npx @wonderwhy-er/desktop-commander` | Control escritorio |
| antigravity-link | `node mcp-server.mjs` | Bridge extensión Antigravity IDE |

### SSH key nueva
- **Key:** `~/.ssh/id_ed25519_serveri3`
- **Ruta:** x@serverx → i3@192.168.1.211
- **Estado:** agregada a authorized_keys de serveri3 ✅

### Pendiente
- Rotar API key OpenRouter expuesta en sesión (prefijo `sk-or-v1-856c...`) — invalidar y generar nueva en OpenRouter dashboard.


---
## 2026-06-10 — Activation of Agents and Backend Improvements

**Proyecto:** Hermes Hub
**Estado:** ✅ Agentes activados y mejoras en backend

### Cambios
- Carlitos y Aurora activados como agentes `ollama_local` en Hermes Hub (serverX)
  - Carlitos: qwen2.5-coder:7b, rol Coordinador MS
  - Aurora: qwen2.5-coder:7b, rol Documentación técnica
- Aurora v3: pipeline de documentación controlado por backend (sin marcadores XML)
- Volúmenes montados en container backend: `/home/x/MontuMS` y `/home/x/.ssh`
- 5/5 agentes Hermes Hub operativos: Rabín, Espinita, Risko, Carlitos, Aurora

**Infraestructura de referencia**
- serverX: 192.168.1.111, Ubuntu 24.04, Docker, Ollama, GPU P104-100
- serveri3: 192.168.1.211, Ubuntu 24.04, Cloudflare tunnels, Hermes agents
- Proyectos: OptiFierro V2, OP Risk, Hermes Hub, Visual-Voice, CutX, Pegas V2
- Agentes Hub: Rabín, Espinita, Risko, Carlitos, Aurora

---


---
## 2026-06-15 — Endpoint REST Hermes Hub mejorado

**Proyecto:** Hermes Hub
**Estado:** 🔄 Mejora en endpoint

### Cambios
- Actualización de la documentación del endpoint POST /api/chat/{agent_id}
- Mejoras en el manejo de errores y validaciones
- Nuevos tests unitarios: CARLITOS_REST_ERR + AURORA_REST_ERR

**Infraestructura de referencia**
- serverX: 192.168.1.111, Ubuntu 24.04, Docker, Ollama, GPU P104-100
- serveri3: 192.168.1.211, Ubuntu 24.04, Cloudflare tunnels, Hermes agents
- Proyectos: OptiFierro V2, OP Risk, Hermes Hub, Visual-Voice, CutX, Pegas V2
- Agentes Hub: Rabín, Espinita, Risko, Carlitos, Aurora

## TEST-TRANSCRIPCION
Este texto debe aparecer identico en el archivo, sin reinterpretacion.

## TEST-TRANSCRIPCION
Este texto debe aparecer identico en el archivo, sin reinterpretacion.

## TEST-TRANSCRIPCION
Este texto debe aparecer identico en el archivo, sin reinterpretacion.

## TEST-BYPASS-LLM 2026-06-10
Este texto debe aparecer identico. Sin reinterpretacion.

---
## 2026-06-10 — Hermes Hub: Carlitos, Aurora, REST endpoint y autonomía Miaude

**Proyecto:** Hermes Hub (serverX :8750)
**Estado:** Operativo

### Cambios implementados

**Nuevos agentes activos:**
- Carlitos: ollama_local, qwen2.5-coder:7b, rol Coordinador MS
- Aurora: ollama_local, qwen2.5-coder:7b, rol Documentación técnica

**Aurora — escritura autónoma en MontuMS:**
- Funciones aurora_read_file, aurora_write_file, aurora_git_commit en routers/agents.py
- Volumen /home/x/MontuMS montado en container /app/montums:rw
- SSH key id_ed25519_github en /app/ssh_host:ro
- Git identity: Aurora (Hermes Hub) / aurora@montuschi.cl
- Aurora v3: bypass LLM con aurora_extract_exact_block()
  Patrón con este bloque exacto: escribe sin pasar por el modelo

**Endpoint REST síncrono:**
- POST /api/chat/{agent_id} en main.py
- Body: {content, agent_id} — Response: {agent_id, agent, response}
- Puerto: 8750 nginx, accesible desde LAN y SSH

**Miaude-sin-Montu — control directo:**
- Miaude invoca Carlitos y Aurora via osascript SSH serverX curl REST
- Sin intervención de Montu para documentar o consultar agentes

**Documentación generada:**
- HERMES_HUB_GUIA_OPERACION.md creado en MontuMS (98 líneas)
- Keywords Aurora ampliados: guia/guia_operacion activos
- Protocolo Carlitos y Aurora documentado para retomar en cualquier chat

## 2026-07-10 — Visual-Voice P0: Pass 2 Gemini → Ollama gpt-oss:20b

**Contexto:** Pipeline de minuta two-pass de Visual-Voice estaba completamente roto — Gemini API con créditos prepago agotados (error 429). 4 notas de voz sin minuta (la mayor de 135 min).

**Ejecutor:** CCa (Claude Code autónomo, MacBook Pro 13")
**Trigger:** 4 notas de voz pendientes de minuta. Pecas es usuaria activa.

### Cambios en serverX (/home/x/visual-voice/main.py)
- **Funciones modificadas:** `_do_analyze()`, `consolidate()`, `analyze()`
- **Cambio:** Las tres funciones de análisis/redacción de minuta ahora llaman a `gpt-oss:20b` vía Ollama en Mac Studio usando `requests` nativo (sin librería `openai`)
- **Constantes nuevas:** `_OLLAMA_BASE_URL = "http://192.168.1.102:11434"` y `_OLLAMA_MODEL_PASS2 = "gpt-oss:20b"`
- **Deploy:** `docker compose build --no-cache && docker compose up -d` ✅

### Estado post-fix
- Contenedor visual-voice: Up (http://localhost:8502 → HTTP 200) ✅
- Conectividad serverX → Mac Studio desde contenedor: 200 OK ✅
- Pass 2 operativo: test E2E con JSON válido recibido desde gpt-oss:20b ✅
- STT: faster-whisper small (sin cambios, sigue en serverX GPU P104-100)

### Fase 2 STT — diferida
- mlx-whisper en Mac Studio: instalación diferida (Fase 1 operativa, STT actual funciona)
- Motivo: sin urgencia inmediata, mlx-whisper requiere sesión dedicada

### Deuda técnica nueva
- [ ] Evaluar `qwen3.6:27b` vs `gpt-oss:20b` para Pass 2 (calidad de minutas)
- [ ] Hacer stt-mac.service persistente como servicio launchd en Mac Studio cuando se retome Fase 2
- [ ] Recargar créditos Gemini API y evaluar rollback si calidad local < Gemini

---

## 2026-07-10/11 — Mac Studio: Limpieza + Mejoras Rabín + Setup Carlitos

**Contexto:** Sesión de migración y optimización del ecosistema de agentes IA. Ejecutado vía protocolo Miaude-sin-Montu (Claude Desktop + Desktop Commander, sin intervención manual de Montu salvo el sudo de timezone).

### Mac Studio — Modelos Ollama
- **Eliminado:** `qwen3.5:122b-a10b` (81 GB, MoE sin agente asignado desde migración de Risko)
- **Espacio recuperado:** 81 GB (SSD: 302 GB libres post-limpieza)
- **Inventario final:** gpt-oss:20b (13GB) + qwen3-coder:30b (18GB) + qwen3.5:9b (6.6GB) + qwen3.6:27b (17GB) + qwen3.6:35b-a3b (23GB) = ~77.6 GB total

### serverX — Timezone
- **Cambio:** Timezone UTC → America/Santiago
- **Comandos:** `sudo timedatectl set-timezone America/Santiago && sudo timedatectl set-ntp true`
- **Estado:** `System clock synchronized: yes`, `NTP service: active` ✅
- **Motivo:** Rabín obtenía hora UTC y la presentaba como hora de Santiago

### serveri3 — Rabín (Hermes Agent)
- **Fix 1 — Terminal backend:** `terminal.backend: local → ssh`
  - Parámetros SSH ya estaban en .env: `TERMINAL_SSH_HOST=192.168.1.111`, `TERMINAL_SSH_USER=x`, `TERMINAL_SSH_PORT=22`
  - Resultado: Rabín ejecuta comandos en serverX correctamente
- **Fix 2 — Fallback local:** Agregado `qwen3.5:9b` vía Mac Studio como PRIMERA opción de fallback (antes de los 3 fallbacks OpenRouter que causaron el outage del 2026-07-04)
  - Configuración: `provider: custom`, `base_url: http://192.168.1.102:11434/v1`, `model: qwen3.5:9b`
- **Fix 3 — Compresión de contexto:** Habilitada (`enabled: true`, `threshold: 0.6`, `target_ratio: 0.3`, `protect_last_n: 10`)
- **SOUL.md:** Agregada sección "Información en tiempo real" (instrucción para usar terminal en fecha/hora). Efectividad parcial — modelo ignora instrucción texto; requiere function calling en Semana 3.

### Mac Studio — Carlitos (Claude Code local)
- **CLAUDE.md creado:** `/Users/montu/.claude/CLAUDE.md` (72 líneas)
  - Incluye: infraestructura completa (Mac Studio, serverX, serveri3, TO), proyectos activos (OptiFierro V2, Visual-Voice, MontuMS), convenciones de código, reglas cardinales de deploy y seguridad
- **settings.json:** `effortLevel: low → medium`
- **Alias verificado:** `Carlitos` en .zshrc funciona correctamente (test: respuesta CARLITOS_OK en 103s cold start)

### Hallazgos sin resolver (backlog)
- **BACKLOG-RABIN-DATETIME:** gpt-oss:20b responde fecha/hora desde memoria del modelo, ignorando instrucciones SOUL. Fix real: implementar tool `get_datetime(timezone)` con function calling. Semana 3 del plan de optimización.
- **BACKLOG-WHATSAPP-BRIDGE:** Bridge WhatsApp en Hermes muere con exit code 1 en cada arranque. No afecta Telegram. Relacionado con Espinita (infraestructura parcialmente lista: WHATSAPP_ENABLED=true, 5 números autorizados).
- **BACKLOG-SEARXNG-UNDOC:** SearXNG local corriendo en serveri3 localhost:8888. No documentado en INVENTARIO_MAESTRO. Agregar en próxima actualización de inventario.
## 2026-07-12 — Configuración inicial de Aurora como agente CLI

**Contexto:** Aurora fue configurada como agente de documentación técnica accesible
desde CLI (Terminal del Mac Studio) y desde Miaude via Claude Desktop. Anteriormente
existía el HARNESS.md pero Aurora no tenía configuración operativa como agente.

**Cambios:**
- Creado: /Users/montu/.claude/agents/aurora.md (78 líneas, modelo qwen3.6:27b)
  Define a Aurora como sub-agente de Claude Code con tools: Read, Write, Edit, Bash, Glob, Grep
- Agregado en /Users/montu/.zshrc:
  alias Aurora (y alias aurora en minúscula) apuntando a qwen3.6:27b via Ollama localhost:11434
- Modelo corregido: HARNESS.md decía qwen3.6:35b-a3b (MoE, tuvo alucinaciones en síntesis
  larga). Nuevo modelo asignado: qwen3.6:27b (denso, 17GB, sin presión de latencia)

**Hallazgos:**
- HARNESS.md en ~/MontuMS/harness/aurora/HARNESS.md tenía el modelo incorrecto documentado
  (qwen3.6:35b-a3b). Corregido en el archivo durante esta misma sesión.

**Siguiente paso:** Validar Aurora con tarea real de documentación y evaluar calidad de output.


## 2026-07-12 — Optimizacion de performance de Aurora y Ollama

**Contexto:** Tras primera tarea real de Aurora (21m 44s), se identificaron y corrigieron causas de lentitud.

**Cambios:**
- aurora.md: agregado /no_think en system prompt (desactiva extended thinking de qwen3.6:27b)
- aurora.md: protocolo de inicio actualizado — leer tail/grep en vez de archivos completos
- aurora.md: regla de transferencia de contenido via /tmp explicitada
- Ollama plist: OLLAMA_MAX_LOADED_MODELS 2 a 3, agregado OLLAMA_NUM_PARALLEL=2
- Ollama reiniciado para aplicar nueva configuracion

**Siguiente paso:** Medir tiempo de esta tarea como benchmark post-optimizacion.


## 2026-07-13 — Benchmark Aurora v3: system prompt cargado via --system-prompt-file

**Cambios:**
- Alias Aurora actualizado: agrega --system-prompt-file apuntando a /Users/montu/.claude/aurora-sp.md
- Con esto el HARNESS de Aurora (incluyendo /no_think) se carga en cada invocacion CLI
- Archivo aurora-sp.md creado: version del agente sin front matter YAML

**Resultado:** ver tiempo de esta ejecucion vs 394s (v2) y 1304s (v1).

## 2026-07-13 — Benchmark Aurora v4: modelo gpt-oss:20b (sin thinking)

**Contexto:** Prueba de modelo alternativo para Aurora. qwen3.6:27b tiene extended thinking que no puede desactivarse via system prompt, causando ~4-5 min de overhead. Se prueba gpt-oss:20b (sin thinking, 67.3 tok/s vs 16.4 tok/s).

**Cambios:**
- Alias Aurora en .zshrc: qwen3.6:27b cambiado a gpt-oss:20b
- aurora.md: modelo actualizado a gpt-oss:20b

**Resultado esperado:** reduccion de 6.5 min a menos de 2 min si el cuello de botella era el thinking.

---

## 2026-07-18 — Optimización stack de inferencia local Mac Studio (PLAN-INFER-MS-01)

**Contexto:** Ejecución de plan de optimización multi-fase para agentes Hermes/CLI sobre
Ollama en Mac Studio M2 Max 96GB. Plan sintetizado desde deep research multi-IA (Qwen Studio,
Gemini, ChatGPT, GLM) + análisis arquitectónico Opus 4.8. Ejecutado autónomamente por Miaude
bajo protocolo Miaude-sin-Montu.

**Cambios:**
- /opt/homebrew/opt/ollama/homebrew.mxcl.ollama.plist (Cellar, fuente de verdad brew):
  - OLLAMA_MAX_LOADED_MODELS: 2 a 3 (elimina swaps entre agentes con 4 modelos productivos)
  - Agregado OLLAMA_KEEP_ALIVE=-1 (faltaba del Cellar, solo estaba en LaunchAgents)
  - Agregado OLLAMA_NUM_PARALLEL=1 (idem)
- Modelfile carlitos: num_ctx 16384 a 20480 (mayor contexto para archivos de codigo reales)
  Recreado via ollama create carlitos -f /tmp/Modelfile.carlitos
- ~/Library/LaunchAgents/ollama.carlitos.plist a .DISABLED
  (causaba proceso zombie de ollama serve sin env vars correctas al boot)
- ~/Library/LaunchAgents/cl.montuschi.ollama-warmup.plist: actualizado de 2 a 3 modelos
  (carlitos + gemma3:27b + qwen3.6:35b-a3b)

**Hallazgos:**
- gpt-oss:20b y qwen3.6:27b NO estan presentes en Ollama Mac Studio (ver Ollama list).
  Discrepancia con INVENTARIO_MAESTRO. Requiere verificacion de que modelos usan Rabin/Aurora.
- brew services restart/start regenera el plist desde el Cellar, borrando cambios manuales
  en ~/Library/LaunchAgents/. Regla documentada: editar SIEMPRE el plist del Cellar.
- Prefix cache ya operativo antes de cambios (ratio 14.37x TTFT T1/T2). Fase 2 del plan
  (orden de prompts) no requeria intervencion.
- iogpu.wired_limit_mb=0 en macOS 26 Tahoe = administrado por SO. Fase 4 del plan cancelada.
- Backend Ollama 0.31.1 en Apple Silicon = Metal nativo. No existe flag OLLAMA_MLX separado.
  Fase 3 (MLX vs GGUF) = N/A para esta version.

**Benchmark PRE vs POST (modelo: carlitos / qwen3-coder:30b Q4_K_M):**
- TTFT cold: 2.041s a 1.669s (-18.2%)
- TTFT warm (cache hit): 0.142s a 0.141s (sin cambio)
- Decode tok/s: 82.3 a 67.1 (-18.5%, atribuible al aumento de num_ctx; sigue sobre meta >=40)
- Calidad de respuesta: Excelente en ambos casos (sin degradacion)
- Archivos benchmark: ~/bench/results/bench_PRE_20260718_155208.json y bench_POST_20260718_200422.json

**Siguiente paso:** ver entrada 2026-07-19 — la discrepancia de modelos se investigo y resolvio.

---

## 2026-07-19 — Fix modelo primario Rabin/Risko + migracion Risko a perfil nativo

**Contexto:** Rabin y Risko respondian siempre con qwen3.5:9b (fallback) en vez
de su modelo primario configurado (gemma3:27b en ese momento).

**Causa raiz 1 (confirmada con logs):** gemma3:27b no soporta tool-calling.
Cada llamada de Hermes incluye herramientas por defecto (ej. ejecutar date),
generando HTTP 400 "gemma3:27b does not support tools" y forzando fallback
a qwen3.5:9b en cada turno.

**Fix 1:** modelo primario de Rabin y Risko cambiado de gemma3:27b a
qwen3.6:35b-a3b (MoE, 3B parametros activos, soporta tools+thinking, ya
usado como subagente de analisis de ambos). Cambio en el campo
model.default de /home/x/.hermes/config.yaml (Rabin) y config.yaml de Risko.

**Causa raiz 2 (confirmada con evidencia de codigo y verificacion con hash):**
Hermes Agent reescribe su propio unit file de systemd en cada arranque segun
HERMES_HOME. Risko vivia en /home/x/.hermes-risko (directorio hermano, no
reconocido como "perfil nativo" bajo /home/x/.hermes/profiles/), causando que
Hermes calculara mal el nombre de servicio y sobreescribiera el unit file de
hermes-gateway.service (Rabin) cada vez que Risko arrancaba. Esto producia
conflictos de PID, gateway.lock compartido, y caidas en cascada.

**Fix 2 (migracion de datos en produccion):**
- Backup en frio: servicios detenidos, tar czf, exit code 0, 57 archivos,
  ~9MB. Ubicacion: /home/x/hermes-risko-backup-pre-migracion.tar.gz
  (se mantiene, no eliminar sin autorizacion explicita de Montu)
- Movido /home/x/.hermes-risko a /home/x/.hermes/profiles/risko
- Actualizado hermes-risko.service con las nuevas rutas
- Verificacion critica: md5sum de hermes-gateway.service identico antes y
  despues de reiniciar hermes-risko.service. Confirma fix de raiz, no parche.
- Verificado con "hermes profile list" y "hermes profile show risko":
  ambos perfiles con modelo qwen3.6:35b-a3b, gateway running, rutas correctas.

**Fix 3 — experimento de reasoning_effort (aprendizaje documentado):**
Se probo reasoning_effort=low en el bloque agent de ambos configs, con la
hipotesis de mejorar adherencia a instrucciones del SOUL (anti-voseo,
anti-alucinacion). Resultado: calidad mejoro pero el tiempo de segunda
respuesta empeoro severamente (Risko: ~6s a ~28s; Rabin: ~11s a ~14s) porque
cada respuesta, incluso un saludo, pagaba el costo de un ciclo de
razonamiento oculto. Se revirtio a reasoning_effort vacio manteniendo el
guardrail textual del SOUL (ver Fix 4). Con esa combinacion se confirmo en
pruebas reales: calidad se mantiene, velocidad vuelve a ser rapida
(Risko ~11s, Rabin ~18s en segunda respuesta).
Conclusion: el guardrail textual explicito es suficiente por si solo para
este caso de uso. No activar reasoning_effort en agentes conversacionales
de baja latencia salvo necesidad especifica de una tarea.

**Fix 4 — guardrails agregados al SOUL de Rabin y Risko:**
- Regla anti-voseo explicita: prohibido vos/tenes/queres/sabes/podes/haces
  (formas rioplatenses). Tutear siempre tu/tienes/quieres. Espanol chileno
  sin excepcion.
- Guardrail de auto-descripcion: al preguntar que modelo/infraestructura
  usan, responder SOLO con datos verificados (qwen3.6:35b-a3b, proveedor
  custom, infraestructura privada). Prohibido inventar detalles tecnicos
  adicionales.

**Discrepancia de modelos, resuelta:** el INVENTARIO_MAESTRO previo
documentaba gpt-oss:20b (Rabin) y qwen3.6:27b (Aurora) como modelos activos.
Verificacion confirma que NINGUNO de los dos existe. Stack real verificado:
gemma3:27b, carlitos (Modelfile custom sobre qwen3-coder:30b, num_ctx 20480),
qwen3-coder:30b (base, contexto completo), qwen3.6:35b-a3b (23GB, ahora
primario de Rabin/Risko y subagente de analisis), qwen3.5:9b (fallback).

**Version de Hermes Agent:** documentada como v0.14.0, verificacion previa
sugirio v0.18.2 instalada. PENDIENTE DE VERIFICACION FORMAL.

---

## 2026-07-19 — Aurora: alias roto (modelo eliminado) + Modelfile de contexto

**Contexto:** Al intentar delegar una tarea de documentacion a Aurora, se
descubrio que el alias Aurora en .zshrc apuntaba a qwen3.6:27b-mtp-q4_K_M,
variante eliminada en la reorganizacion de modelos del 2026-07-16/17. El
alias fallaba silenciosamente (modelo no encontrado en Ollama).

**Hallazgo adicional:** el archivo /Users/montu/.claude/agents/aurora.md
(formato de subagente de Claude Code) NO es el que Aurora usa realmente.
La invocacion real vive en el alias de .zshrc, que carga el SOUL via
--system-prompt-file apuntando a /Users/montu/.claude/aurora-sp.md — un
archivo distinto, sin relacion operativa con agents/aurora.md. Cualquier
edicion futura al harness de Aurora debe hacerse en aurora-sp.md.

**Fix del alias — primer intento:** corregido a apuntar a qwen3.6:35b-a3b
directo (mismo modelo ahora usado por Rabin/Risko). Al probar con una tarea
real de documentacion, el proceso hizo timeout a los ~20 minutos sin
completar nada (git status limpio, sin commit). Diagnostico: qwen3.6:35b-a3b
estaba cargado en Ollama con CONTEXT=262144 (maximo, sin recortar) — el
mismo patron de sobrecosto ya documentado en las sesiones 2026-07-12/13
(Aurora con qwen3.6:27b sin thinking desactivable, 21m44s en su primera
tarea real).

**Prueba de aislamiento de causa:** se ejecuto una tarea de complejidad
comparable (3 llamadas SSH + lectura + escritura de archivo) via Carlitos
(qwen3-coder:30b, contexto recortado a 20480, sin capacidad de thinking).
Resultado: 332 segundos (5m32s), completado sin errores. Descarta que el
hardware o "los modelos locales en general" sean la causa — el problema es
especifico a la combinacion modelo-con-thinking + contexto sin recortar.

**Fix definitivo:** creado Modelfile custom "aurora" sobre qwen3.6:35b-a3b
(mismos pesos, sin costo adicional de disco) con num_ctx recortado a 32768.
Alias actualizado para usar el modelo "aurora" en vez de qwen3.6:35b-a3b
directo. Validado con la misma tarea de prueba usada para Carlitos:
225 segundos (3m45s), completado sin errores — incluso mas rapido que
Carlitos en la misma tarea.

**Nota para consideracion futura:** el historial de este mismo documento
(sesiones 2026-07-12/13) ya habia identificado que qwen3.6 (27b en ese
entonces) tiene extended thinking dificil de desactivar via prompt, y que
gpt-oss:20b resolvia el problema por no tener thinking en absoluto. Ese
modelo ya no existe en el stack. El fix de contexto recortado resolvio el
problema en esta prueba puntual; si en tareas reales mas largas/complejas
el thinking vuelve a ser un cuello de botella, la alternativa historica
probada es usar un modelo sin capacidad de thinking en absoluto para el
rol de Aurora, en vez de intentar suprimir el thinking de un modelo que
si lo tiene.

**BACKLOG-MS-OLLAMA-01 — cerrado:** discrepancia de modelos investigada y
resuelta (ver arriba). Warmup e inventario actualizados con el stack real.
