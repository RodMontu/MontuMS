# INVENTARIO_MAESTRO — Estado actual post-migración 2026-07-10

Última actualización: 2026-07-16 (reorganización LLMs Mac Studio + despliegue Risko hermes-risko.service)

---


## MAC STUDIO — Nodo Primario IA + Workstation (act 2026-07-15)

**IP LAN:** 192.168.1.102 | **Usuario:** montu | **Serial:** DFW97WXJR6
**macOS:** Tahoe 26.5 | **RAM:** 96GB unified | **CPU:** M2 Max | **GPU:** 38 cores | **SSD:** 1TB NVMe

**Rol:** Nodo de inferencia IA local (Ollama), workstation diaria de Montu, terminal de orquestacion.

### Ollama v0.31.1 - Modelos activos (act. 2026-07-16)
| Modelo | Agente | Uso |
|---|---|---|
| gemma3:27b (17GB) | Rabín, Risko (primario), dev-reviewer, of-reviewer | Asistente personal / OP Risk / revisión de código |
| carlitos:latest (18GB, via alias carlitos) | Carlitos CLI | Coding assistant |
| qwen3.6:35b-a3b (23GB) | Aurora, dev-tech-lead, of-tech-lead, delegación Rabín y Risko, dev-refactorizador, of-refactorizador | Razonamiento complejo / documentación / refactoring |
| qwen3-coder:30b (18GB) | dev-implementer, dev-debugger, of-implementer, of-debugger | Coding subagents |
| qwen3.5:9b (6.6GB) | fallback Hermes Rabín | Fallback |

**Eliminados 2026-07-16** (69GB liberados, sin uso tras reorganización): gpt-oss:20b, qwen3.6:27b,
qwen3.6:35b-a3b-mtp-q4_K_M, qwen3.6:27b-mtp-q4_K_M

**LaunchAgent** homebrew.mxcl.ollama (Homebrew):
OLLAMA_KEEP_ALIVE=-1, OLLAMA_NUM_PARALLEL=1, OLLAMA_FLASH_ATTENTION=1,
OLLAMA_KV_CACHE_TYPE=q8_0, OLLAMA_HOST=0.0.0.0:11434, OLLAMA_MAX_LOADED_MODELS=2

**LaunchAgent** cl.montuschi.ollama-warmup.plist (nuevo 2026-07-16):
Precarga carlitos + gemma3:27b a 25s del inicio de sesión macOS (fix cold start Carlitos).

### Carlitos - Agente coding CLI
- Binario: /Users/montu/.local/bin/claude --dangerously-skip-permissions
- Modelo: carlitos (qwen3-coder:30b, num_ctx=16384, temp=0.1, top_p=0.9, keep_alive=-1)
- CLAUDE.md: /Users/montu/.claude/CLAUDE.md
- Agents dir: /Users/montu/.claude/agents/
- Dev agents: dev-tech-lead (qwen3.6:35b-a3b), dev-implementer/dev-debugger (qwen3-coder:30b),
  dev-refactorizador (qwen3.6:27b), dev-reviewer (gpt-oss:20b)

### agy - Antigravity CLI (reemplaza Gemini CLI desde 2026-06-18)
- Ruta: /Users/montu/.local/bin/agy | Version: v1.1.1
- Modelo: Gemini 3.5 Flash Medium | Auth: Google One AI Pro (ce3wkc@gmail.com)
- MCP: agy-headless-bridge v1.2.1 en claude_desktop_config.json
- Herramientas: agy_ask, agy_research

### NFS Mounts (reemplaza SMB - bug macOS 26 Tahoe bloquea getdents via SMB)
| Mount Mac Studio | Origen serverX |
|---|---|
| ~/MiauNube | /mnt/extra |
| ~/MontuMS | /home/x/MontuMS |
| ~/ServerX-Home | /home/x |
LaunchAgent: cl.montuschi.nfs.serverx.plist (RunAtLoad: true)
SMB permanece activo en serverX para clientes Windows/iOS.

## SERVIDORES / EQUIPOS

| Ítem | IP | Hostname | User | Rol actual | Estado |
|------|-----|----------|------|------------|--------|
| Mac Studio M2 Max | 192.168.1.102 | (por confirmar) | montu | **Nodo IA principal** — Ollama + modelos locales para todos los agentes | Activo |
| serverX | 192.168.1.111 | serverx | x | Gateway de infraestructura, Docker, VM Windows 11 (KVM) | Activo |
| serveri3 | — | serveri3 | i3 | Gateway Cloudflare Tunnel + Pi-hole DNS | **En retiro** — desconectar físicamente cuando se complete Fase 2 |

> **Nota:** IP de serveri3 pendiente de confirmar. No existe en inventario activo post-retiro.

### GPU

| Equipo | GPU | VRAM | Rol actual |
|--------|-----|------|------------|
| Mac Studio | M2 Max (GPU integrada) | ~96GB shared RAM | Modelos LLM locales vía Ollama/Metal |
| serverX | NVIDIA P104-100 | 8GB VRAM + 7660 MiB free | Redestinada a passthrough → VM Windows 11 KVM + NoMachine |

> **Hallazgo crítico M2 Max:** macOS no entrega los 96GB completos a Metal/GPU. Modelo de 85GB se derramó 95% a CPU. Modelo >~60-70GB requiere cuidado de sizing para este equipo.

---

## AGENTES (estados FINAL confirmados, act. 2026-07-16)

| Agente | Bot Telegram | Default Model | Ubicación | Estado |
|--------|-------------|---------------|-----------|--------|
| **Rabín** | `@pantero_bot` | `gemma3:27b` primario, `qwen3.6:35b-a3b` delegación (Ollama local, Mac Studio) | `hermes-gateway.service` (serverX, HERMES_HOME=/home/x/.hermes) | Activo |
| **Carlitos** | `@Carlitos` | `qwen3-coder:30b` (Ollama local, Mac Studio) | CLI (Mac Studio) | Activo |
| **Aurora** | — | `qwen3.6:35b-a3b` (Ollama local, Mac Studio) | CLI (Mac Studio) | Activa (documentación) |
| **Risko** | `@Risko_OP_bot` | `gemma3:27b` primario, `qwen3.6:35b-a3b` delegación (Ollama local, Mac Studio) | `hermes-risko.service` (serverX, HERMES_HOME=/home/x/.hermes-risko) | Activo — token Telegram pendiente |
| **Spinita** | — | `qwen3.5:9b` descargado, agente no levantado | — | Pendiente de levantar |

> **Nomenclatura:** "Clawdio" ya no es un agente real — apodo genérico del período OpenClaw→Hermes. Agentes reales con personalidad definida (nombre propio mayúscula): Rabín, Risko, Spinita, Carlitos, Aurora. Protocolo `cc+modelo` para futuros modelos cloud genéricos sin personalidad.

---

## DOCKER CONTAINERS (serverX)

| Contenedor | Puerto(s) | Compose Path | Estado | Rol |
|------------|-----------|--------------|--------|-----|
| visual-voice | 8502→8000 | /home/x/visual-voice/ | Up | Audio → mapa conceptual (STT + LLM) |
| hermes-hub-backend | — | — | Up | Backend Hermes Hub |
| hermes-hub-frontend | 8750→80 | — | Up | Frontend Hermes Hub |
| pegas_v2 | 8000 | /home/x/dev/pegas_v2/ | Up (healthy) | Pegas V2 app |
| visual-voice | 8502 | /home/x/visual-voice/ | Up | Visual-Voice |
| retroassembly | 8088→8000 | — | Up | RetroAssembly |
| cutx-app | 8600→8600 | — | Up | CUTX App |
| ollama | 11434→11434 | /srv/ollama/ | Up | Ollama server (Mac Studio) |
| portainer | 9000 | portainer-ce | Up | Portainer |

### Contenedores fuera de servicio / eliminados (no eliminar del inventario)

| Contenedor | Estado | Notas |
|-----------|--------|-------|
| hermes-risko (fantasma #3) | **Detenido (no eliminado)** 2026-07-10 | Competía por token Telegram con risko-gateway.service, causaba getUpdates conflictivos |

---

## AGENTES — INFRA EIS (serverX)

| Servicio | Ubicación | Modelo(s) | Estado | Notas |
|----------|-----------|-----------|--------|-------|
| **Rabín** | `hermes-gateway.service` (systemd --user), `HERMES_HOME=/home/x/.hermes` | gemma3:27b primario, qwen3.6:35b-a3b delegación (Mac Studio Ollama) | Activo | Migración post-retiro serveri3 completada. Modelo actualizado 2026-07-16 (era gpt-oss:20b) |
| **Carlitos** | — | qwen3-coder:30b (Mac Studio Ollama) | Activo | Setup completado en sesión 2026-07-10 |
| **Aurora** | `~/MontuMS/harness/aurora/` | qwen3.6:35b-a3b (Mac Studio Ollama) | Activa | HARNESS.md definido, primera tarea: consolidar esta documentación |
| **Risko** | `hermes-risko.service` (systemd --user, nuevo 2026-07-16), `HERMES_HOME=/home/x/.hermes-risko` | gemma3:27b primario, qwen3.6:35b-a3b delegación (Mac Studio Ollama) | Activo — token @Risko_OP_bot pendiente | Reemplaza el despliegue anterior en `/home/i3/.risko/` (serveri3, apagado). Contenedor fantasma hermes-risko sigue detenido/no eliminado (serveri3, referencia histórica) |

---

## REDES / ACCESOS SSH

| Origen → Destino | Puente/Protocolo | Notas |
|------------------|------------------|-------|
| Mac Studio (192.168.1.102) ↔ serverX (192.168.1.111) | SSH directo | IP fija Mac Studio confirmada |
| serverX → serveri3 | **Nueva llave SSH creada** esta sesión 2026-07-10 (no existía, solo había i3→x) | Agregar a config SSH de x en serverX |
| serverX → VM Windows 11 (KVM) | GPU P104-100 passthrough + NoMachine / KDE | DEC-03 resuelto |
| Acceso externo | Cloudflare Tunnel (serveri3) | **No exponer puertos directo a internet desde serverX** |

> **Nueva llave SSH x→i3:** creada durante esta sesión, agregado al inventario de accesos. Antes solo existía i3→x.

---

## ALMACENAMIENTO

| Disco | Device | Label/Size | Montaje | Uso actual |
|-------|--------|------------|---------|------------|
| sdc | KC600 512GB | OS | / (42% usado, 182G/468G) | Ubuntu Server + Docker + apps |
| sdb | SA400S3 112GB | — | /srv/vms | VM Windows 11 KVM |
| sdd | HGST 465GB | miau_nube | /mnt/extra | NAS principal — Samba (4 shares) + NFS exportado |
| sda | WDC 931GB | — | NO ASIGNADO | Pendiente asignación |
| RESPALDO_ARCA | — | — | **DESCONECTADO** | No perdido, desconectado físicamente — pendiente reconexión |


### Samba (serverX) — estado 2026-07-12

| Share | Path | Permisos | Estado |
|-------|------|----------|--------|
| [miau_nube] | /mnt/extra | RW para x | Activo |
| [home_x] | /home/x | RW para x | Activo |
| [sistema] | / | RO para x | Activo |
| [MontuMS] | /home/x/MontuMS | RO para x | Nuevo 2026-07-12 |

Fixes aplicados 2026-07-12:
- `directory name cache size` eliminado (parámetro obsoleto)
- `rpc_server:svcctl = disabled` — resuelve crash loop de rpcd_classic en Samba 4.19 standalone
- Bug documentado: SMB + macOS 26 Tahoe — `getdents()` bloqueado por DACL sintético. Workaround: NFS.

### NFS (serverX) — exports activos

| Export | Red | Opciones |
|--------|-----|----------|
| /mnt/extra | 192.168.1.0/24 | rw, no_root_squash, no_subtree_check |
| /home/x | 192.168.1.0/24 | rw, no_root_squash, no_subtree_check |
| /home/x/MontuMS | 192.168.1.0/24 | rw, no_root_squash, no_subtree_check — nuevo 2026-07-12 |

### Acceso NAS desde clientes — Mac Studio (192.168.1.102, user montu)

| Mount local | Path serverX | Protocolo | Auto-mount |
|-------------|-------------|-----------|------------|
| ~/MiauNube | /mnt/extra | NFS | LaunchAgent cl.montuschi.nfs.serverx.plist |
| ~/MontuMS | /home/x/MontuMS | NFS | LaunchAgent cl.montuschi.nfs.serverx.plist |
| ~/ServerX-Home | /home/x | NFS | LaunchAgent cl.montuschi.nfs.serverx.plist |

> MacBook Pro + Mac Pecas (MacBook Neo): pendiente — misma arquitectura NFS, sesión futura.

> **DISCO RESPALDO_ARCA:** estado actual = desconectado (no perdido). Ubicación física fue ambigua en inventario anterior. Corregir a "pendiente reconexión" cuando se localize físicamente.

---

## PROYECTOS / URLS PÚBLICAS

| Proyecto | URL | Puerto/Path | Estado |
|----------|-----|-------------|--------|
| Pegas V2 | pegas.montuschi.cl (TBD dominio) | :8000 | Activo |
| Visual-Voice | audio → mapa conceptual | :8502 | Activo |
| Nextcloud OP Risk | docs.risk.montuschi.cl | :8090 | 16 documentos indexados desde /mnt/extra/OP Risk/ |
| RetroAssembly | — | :8088 | Activo |
| CUTX App | — | :8600 | Activo |
| Hermes Hub | — | hermes-hub-backend + :8750 frontend | Activo |

---

## HALLAZGOS PENDIENTES (no cerrados)

### BACKLOG-TECHNICAL

| Ítem | Descripción | Pendiente |
|------|------------|-----------|
| **BACKLOG-AURORA-FASE2** | Capacidad de localización ("¿dónde está X?") — evaluar RAG vectorial vs ripgrep sobre repo | Diseñar en sesión dedicada |
| **Spinita no levantada** | Modelo `qwen3.5:9b` descargado, agente pendiente de configurar | Pendiente |
| **Compression Hermes** | Evaluar activar compresión de contexto o reset automático periódico (afecta todos los agentes) | Evaluar priorización |
| **sda sin asignar** | Disco WDC 931GB — LV ubuntu-lv (928GB) activo pero SIN mountpoint. Investigar si tiene datos antes de asignar. | Sesión dedicada |
| **NFS MacBook Pro + Mac Pecas** | Misma arquitectura NFS que Mac Studio. Limpiar config SMB vieja primero. | Sesión futura |
| **SMB Tahoe bug** | Rastrear fix en Samba >=4.20 o macOS 26.x para reactivar SMB en clientes Mac | Monitorear updates |
| **/sethome detalle** | Montu resolvió algo con `/sethome` en chat con Risko — pendiente explicación para registro | Montu explicar detalle |
| **Rabín solo-lectura técnico** | Definir si "solo lectura" sobre docs técnicos es restricción Unix o regla de config | Pregunta abierta a Montu |
| **DISCO RESPALDO_ARCA** | Desconectado, ubicación ambigua en inventario | Localizar físicamente y reconectar |

### HALLAZGOS DESEADOS POR SECCIÓN

#### serveri3 (desafiliación)

> **ESTADO 2026-07:** APAGADO FISICAMENTE. Todos los servicios migrados a serverX (192.168.1.111).
- [ ] Confirmar IP exacta de serveri3 antes de eliminar del inventario
- [ ] Migrar servicios Cloudflare Tunnel a otro nodo cuando se desconecte
- [ ] Actualizar PLAN_MIGRACION sobre GPU P104-100 status (tenía "host por ahora" como default)

---

## HISTORIAL DE CAMBIOS DE ESTADO

| Fecha | Cambio | Sección afectada |
|-------|--------|-----------------|
| 2026-07-16 | Reorganización stack LLMs Mac Studio (Rabín/reviewer agents → gemma3:27b, Aurora/tech-lead/refactorizador → qwen3.6:35b-a3b, 69GB liberados). Warmup LaunchAgent nuevo. Risko desplegado como hermes-risko.service independiente (HERMES_HOME=/home/x/.hermes-risko), token Telegram pendiente. | MAC STUDIO, AGENTES, AGENTES EIS |
| 2026-07-12 | Samba: share [MontuMS] nuevo, fix svcctl crash, smb.conf limpiado. NFS: export /home/x/MontuMS agregado. Mac Studio: 3 mounts NFS + LaunchAgent. Bug SMB+macOS26 Tahoe documentado. | ALMACENAMIENTO, NFS, Clientes |
| 2026-07-10 | Migración serveri3→Mac Studio, Ollama + modelos, A/B Rabín, repunte local, Carlitos setup, Risko ciclo completo, contenedor hermes-risko detenido | Todo el inventario |
| 2026-05-05 | Deploy original de Risko (risko-gateway.service) | AGENTES EIS (sin registrarse entonces en INVENTARIO) |

> **Nota:** Este inventario se debe actualizar cada vez que haya cambio de infraestructura nuevo (seguir protocolo del CLAUDE.md sección 7).
