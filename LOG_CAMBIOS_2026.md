
---

## 2026-07-12 — MiauNube: Migración NFS + accesos completos serverX (Mac Studio)

### Bug confirmado: SMB + macOS 26 Tahoe (build 25F71)
- Síntoma:  en TODOS los directorios del share SMB
- RCA: macOS 26 bloquea getdents() (FILE_LIST_DIRECTORY) pero permite open() (FILE_TRAVERSE). DACL sintético Samba 4.19 incompatible con nuevo SMB client de Tahoe. NFS confirma que servidor y permisos son correctos.
- Workaround: NFS para clientes macOS. SMB queda activo para Windows/iOS.

### Cambios serverX
- smb.conf: eliminado parámetro obsoleto 
- smb.conf: agregado share [MontuMS] → /home/x/MontuMS (read-only)
- smb.conf: fix  (crash loop rpcd_classic en standalone)
- /etc/exports: agregado /home/x/MontuMS como export explícito dedicado

### Mac Studio — Mounts NFS activos
- ~/MiauNube → 192.168.1.111:/mnt/extra
- ~/MontuMS  → 192.168.1.111:/home/x/MontuMS  (acceso dedicado docs diarios)
- ~/ServerX-Home → 192.168.1.111:/home/x
- LaunchAgent: cl.montuschi.nfs.serverx.plist (RunAtLoad, 3 mounts)

### Pendientes
- MacBook Pro + Mac Pecas (NFS): sesión futura
- sda WDC 931GB: LV sin montar — investigar separado
- winuser Pecas: pendiente en smb.conf


---

## 2026-07-02 — Reconstrucción completa VM windows11 (serverX) tras falla SSD abril

### Contexto
La instalación de abril 2026 (VM windows11, usuario "consultor", sudoers.d,
rdp-forward.service) se perdió íntegramente con la falla del SSD del sistema
en serverX. La reinstalación de mayo 2026 quedó a medio camino, atascada en
validación de cuenta Microsoft (OOBE). Esta sesión cierra esa reinstalación
y reconstruye la cadena de acceso remoto completa.

### OOBE / Instalación
- Bypass de cuenta Microsoft: `start ms-cxh:localonly` (CMD vía Shift+F10) —
  método alternativo a `oobe\bypassnro`, funcionó donde el otro no.
- Usuario local creado: montu (reemplaza "consultor" de abril).
- Nombre de PC dentro de Windows: WindowsVM.

### RCA — Teclado
- Causa raíz: layout seleccionado en Windows era "Latinoamericano" pero el
  teclado físico (Logitech K380) es Español (España) ISO — confirmado por
  tecla º/ª/\ y doble tecla de tilde (junto a P y junto a Ñ).
- Fix: seleccionar "Español (España)" en el instalador.

### RCA — Cliente VNC
- macOS Screen Sharing.app (nativo) queda pegado en prompt de password
  contra servidor VNC de QEMU sin auth configurada (security type "None").
  Incompatibilidad de handshake, no es tema de credenciales.
- Fix: usar RealVNC Viewer.app vía túnel SSH local
  (ssh -L 5900:127.0.0.1:5900 x@192.168.1.111 → 127.0.0.1:5900).

### Automatización toggle VM (MacBook)
- /Users/montu/vm-windows11.sh (invocado por /Applications/Windows 11.app)
- RCA: dependía de sudo virsh + sudoers.d perdido en falla de SSD.
- Fix: reemplazado por `virsh -c qemu:///system` — usuario x pertenece de
  forma permanente al grupo libvirt, no requiere sudo.

### Acceso remoto — RDP
- RDP habilitado dentro de Windows.
- IP interna VM: 192.168.122.210.
- Forward reconstruido: socat TCP-LISTEN:3389,fork,reuseaddr
  TCP:192.168.122.210:3389 en serverX, sin sudo.
- Persistencia: crontab @reboot de usuario x, sin systemd.
- Validado end-to-end: nc -zv exitoso (interno y forward), conexión real
  confirmada por usuario vía Windows App.

### Backlog nuevo abierto
- BACKLOG-VM-WIN-GPU: passthrough P104-100 → VM windows11, bloqueado por
  llegada Mac Studio + migración de cargas IA locales. Ver INVENTARIO_MAESTRO.

### Pendiente (no bloqueante)
- Activación de licencia Windows.
- Verificar drivers VirtIO completos vía Device Manager.
- Limpiar devices obsoletos en Windows App del usuario ("consultor",
  "serverX / No credentials").

---

## 2026-06-01 — Visual-Voice: Cambio de modelos LLM para generación de minutas

**Archivo modificado:** `/home/x/visual-voice/main.py` (volumen montado, sin rebuild)

**Cambios aplicados:**
- MODEL_CONFIGS reemplazado: de 5 modelos a exactamente 2:
  - `openrouter:deepseek/deepseek-v4-flash` | Label: "DeepSeek V4 Flash (rápido)" | Badge: CREDITS | DEFAULT
  - `openrouter:openai/gpt-oss-120b:free`   | Label: "GPT-OSS 120B (gratuito)"   | Badge: FREE
- Default `model_key` en `MinutesReq` actualizado a `openrouter:deepseek/deepseek-v4-flash`
- Contenedor reiniciado con `docker restart` (sin rebuild — main.py es volumen directo)
- Endpoint `/models` verificado: retorna exactamente los 2 modelos nuevos ✓

**Estado post-cambio:** visual-voice Up, puerto 8502→8000 activo

---

## [SESIÓN DE TRABAJO] - 2026-06-29
**Área:** Estrategia LinkedIn + Conocimiento OP Risk
**Ejecutado por:** Miaude (Mi TI) + Montu

### Entregables generados

**1. Brújula Estratégica LinkedIn 2026** (`Brujula_LinkedIn_2026_Montuschi.docx`)
- Documento Word descargable, 9 secciones
- Cubre: algoritmo LinkedIn 2026 (fuentes primarias: papers arXiv LiGR/Feed SR,
  datasets Buffer 52M + van der Blom 1.8M + AuthoredUp 3M+), reglas de oro,
  formatos y rendimiento, cadencia por perfil, funnel de contenido 60/30/10,
  guía individual para Rodrigo / Pecas / Montuschi Consultores / OP Risk,
  métricas reales vs vanity, newsletter, checklist de implementación
- Scope: LinkedIn personal Rodrigo + Pecas + ambas páginas de empresa

**2. Skill `linkedin-strategy`** instalada en MacBook
- Ruta: `~/.claude/skills/linkedin-strategy/SKILL.md`
- También subida al Knowledge Base del Proyecto "Mi TI"

### Diagnóstico LinkedIn personal Rodrigo (estado actual)
- Badge "En busca de empleo" ACTIVO → **desactivar urgente** (no hecho aún)
- Headline desactualizado → propuesta acordada
- About orientado a empleador → pendiente reescritura orientada a cliente

### Pendientes LinkedIn (backlog activo)
- BACKLOG-LI-01: Sección Servicios perfil Rodrigo
- Textos finales perfil Rodrigo (Headline + About + Experiencia actual)
- Estrategia LinkedIn OP Risk, perfil Pecas, carrusel PDF, calendario editorial

---

═══════════════════════════════════════════════════
FECHA: 2026-06-05
PROYECTO: OptiFierro V2 — Sistema de Planificación
═══════════════════════════════════════════════════

[FEATURE] Tiempos por Máquina — nueva sección en sidebar

BACKEND
- Nuevo router: backend/routers/tiempos_maquina.py
- GET /api/tiempos-maquina?id_forma&diametro&sucursal_id&meses
- Query live a Cubigest: PIEZA_PRODUCCION + piezas +
  detallePaquetesPieza + Viaje + IT + MAQUINA
- DeltaT calculado en vivo con pandas shift(-1) por máquina
- Filtros outliers: < 2 min (ruido intra-lote) y > 480 min
  (gaps entre turnos) descartados
- Estadística por máquina: N, mín, máx, mediana
- dotacion_detectable = false confirmado: ratio 1:1 en
  PIEZA_PRODUCCION (34.462 registros, todos únicos)
- Escenarios estimados (hipótesis, no validados):
  solo=mediana · con_1_ayud=×0.75 · con_2_ayud=×0.55

FRONTEND
- Nuevo componente: src/components/domain/TiemposPorMaquina.tsx
- NavItem "Tiempos por Máquina" (ícono Timer) en sidebar
- Tabla: Máquina · Sucursal · N · Mín · Mediana · Máx
- Fila con mayor N resaltada en naranja tenue + ★
- Sección escenarios estimados separada con disclaimer
- Avg descartado de UI (4× mayor que mediana por outliers)
- Moda descartada (ruido intra-lote contamina con filtro ≥2min)
- Mediana elegida: robusta, consistente con motor_v2.py

DECISIONES TÉCNICAS
- Script generador de deltat_por_forma_maquina.csv no existe
  en el repo (fue generado offline). DeltaT se recalcula live.
- Cubigest no registra dotación (ayudantes): ratios son 
  hipótesis calibradas, requieren validación futura.

---

[BUG FIX] Popover asignación operador/ayudante cortado

- Componente: GestorProgramacion.tsx (popover L1/L2)
- Causa: position relativa al contenedor padre con overflow
  oculto tapaba el popover detrás de tarjetas de máquinas
- Fix: position fixed con getBoundingClientRect(), z-[9999],
  lógica anti-desborde (flip izquierda/arriba si se sale)

---

[BUG FIX + FEATURE] Compromisos Futuros — coherencia
con Próximas Semanas + Bolsa de trabajos disponibles

CAUSA DEL BUG
- Compromisos Futuros filtraba ITs solo por FechaDespacho
  exacta en la columna del día → aparecía casi vacío
- Próximas Semanas mostraba 68 ITs / 522 ton para la misma
  semana → incoherencia real (no de diseño)
- Principio corregido: Cubigest es fuente de verdad absoluta.
  SQLite = staging temporal de sesión únicamente.

FIX BACKEND
- /api/compromisos-semanales modificado para retornar:
  1. "compromisos": ITs asignados a días específicos
     (sesión SQLite activa + FechaDespacho exacta en columna)
  2. "bolsa": TODOS los ITs pendientes próximos 21 días
     no incluidos en compromisos, misma fuente que Próximas
     Semanas para garantizar coherencia
  3. Nuevo campo "fecha_comprometida": MIN(FechaEntrega,
     FechaDespacho, FechaDespacho1, ...) por IT

FIX FRONTEND — Bolsa de trabajos disponibles
- Panel colapsable bajo las columnas de días
- Tarjetas compactas draggables hacia columnas de día
- Filtros: texto por obra (client-side) · sort fecha
  comprometida ↑↓ · sort peso ↑↓
- Default: sort fecha_comprometida ↑ (más urgente primero)
- Header dinámico: "Bolsa de trabajos disponibles (N de M)"

---

[FEATURE] Modal detalle IT en Próximas Semanas

BACKEND
- Nuevo endpoint: GET /api/its/detalle/{it_id}
- Cubigest READ-ONLY
- Retorna: it_numero, obra, fecha_despacho, estado,
  dias_atraso, total_toneladas, total_tags,
  desglose por (diametro, tipo AD/AG, calidad, n_tags, ton)

FRONTEND
- Clic en tarjeta IT → modal overlay con detalle completo
- Tabla desglose con separador visual AD / AG
- Badge estado coloreado, spinner cargando

---

[FEATURE] Botón "Planificar semana →" en Próximas Semanas

- Botón outline naranja en header de cada columna de semana
- Navega a vista Programación activando Compromisos Futuros
  posicionado en la semana seleccionada
- Implementado via callback onNavigate(view, params) en 
  App.tsx pasado como prop

---

[BACKLOG ABIERTO]

BACKLOG-OF-02: Validación estadística ratios dotación
- Hipótesis actual hardcodeada: +1=75%, +2=55%
- Validación propuesta: análisis de clusters en distribución
  DeltaT de formas complejas y frecuentes (>300 registros)
- Si distribución muestra 3 tendencias → ratios reales
- Condición: sesión dedicada de análisis exploratorio offline

BACKLOG ESTRATÉGICO: Motor de aprendizaje plan vs real
- Estado actual: DeltaT estático (CSV generado una vez)
- Objetivo: cruzar plan motor vs PIEZA_PRODUCCION real →
  actualizar medianas rodantes en SQLite
- Motor lee SQLite en vez de CSV congelado
- Estado: diseño conceptual definido, impl pendiente

═══════════════════════════════════════════════════
FECHA: 2026-07-10
PROYECTO: Migración serveri3 → Mac Studio + Consolidación agentes
═══════════════════════════════════════════════════

## Fase 0 — Backup pre-retiro de serveri3

**Contexto:** serveri3 (gateway Cloudflare Tunnel + Pi-hole DNS) entra en retiro. Servicios migran a serverX y Mac Studio. Antes de desconectar nada, se hace backup completo del estado actual como punto de recuperación.

**Cambios:**
- Backup de configuración de serveri3 realizado antes del inicio de la migración
- Se captura el estado de Cloudflare Tunnel, Pi-hole DNS, y config de agentes (Clawdio/hermes) en serveri3
- **Dato pendiente:** IP exacta de serveri3 por confirmar (sección red del inventario a actualizar cuando se complete retiro total)

**Hallazgos:**
- Cadena de fallback de Clawdio documentada estaba desactualizada: la doc decía `model.default: gemini-2.5-flash` + fallback `llama3.1:8b` en serverX, pero la config real tenía `model.default: deepseek-v4-flash` (OpenRouter) + 3 fallbacks (`hermes-3-llama-3.1-405b`, `nemotron-3-super-120b-a12b`, `glm-5` vía ollama-cloud)
- El fallback a serverX/llama3.1:8b documentado **nunca existió** en la config real al momento de revisar

---

## Fase 1 — Ollama + 5 modelos en Mac Studio M2 Max

**Contexto:** Mac Studio M2 Max 96GB se convierte en nodo IA principal (IP `192.168.1.102`, user `montu`). Se instala Ollama y se descargan los modelos necesarios para todos los agentes.

**Cambios:**
- Ollama instalado en Mac Studio M2 Max (IP `192.168.1.102`)
- Modelos descargados:
  - `gpt-oss:20b` — Rabín (ganador del A/B, Fase 2)
  - `qwen3.6:27b` — evaluado en el A/B de Rabín, no seleccionado
  - `qwen3-coder:30b` — Carlitos
  - `qwen3.6:35b-a3b` — Aurora + Risko
  - `qwen3.5:9b` — Spinita (descargado, agente pendiente de levantar)
- Mac Studio reemplaza a serveri3 como nodo IA principal

**Hallazgos:**
- Límite real de memoria GPU en M2 Max no es los 96GB completos — macOS no entrega toda la RAM a Metal/GPU. Modelo de 85GB (`qwen3.5:122b-a10b`) se derramó 95% a CPU, cayendo de 27.1 a 15.4 tok/s con contexto real
- Alternativa técnica no aplicada: `sysctl iogpu.wired_limit_mb` para subir el límite manualmente

---

## Fase 2 — A/B Rabín (gpt-oss:20b ganador)

**Contexto:** Se realizan pruebas comparativas entre modelos locales de Ollama y cloud (OpenRouter) para determinar el modelo óptimo para Rabín, buscando equilibrio entre calidad de respuesta y latencia.

**Cambios:**
- Prueba A/B entre múltiples modelos para Rabín
- **Resultado:** `gpt-oss:20b` declarado ganador para Rabín
- Modelo se queda como default en config de Rabín

---

## Fase 3 — Repunte de Rabín a modelo local

**Contexto:** Después del A/B, se vuelve a Rabín al modelo local (`qwen3.5:122b-a10b` o equivalente). Se detecta contaminación de contexto por sesiones sin límite en el framework Hermes.

**Cambios:**
- Rabín repunta a modelo local
- Se identifica mecanismo de contaminación transversal: `compression.enabled: false` en Hermes, sesiones que nunca se resetean solas
- Rabín acumuló 89k tokens desde el 30-may (causó latencia)

**Hallazgos:**
- Contaminación de contexto afecta a **todos los agentes Hermes** (Rabín, Risko, futuros Aurora/Spinita). No es bug aislado, es de diseño del framework
- Backlog: evaluar activar compresión de contexto o política de reset automático periódico

---

## Setup del alias Carlitos

**Contexto:** Se configura y activa el agente Carlitos con personalidad propia, modelo local `qwen3-coder:30b`, y su bot correspondiente en Telegram.

**Cambios:**
- Bot Telegram `@Carlitos` creado/activado
- Modelo default: `qwen3-coder:30b` (Ollama local, Mac Studio)
- Protocolo de alias: nombre propio con mayúscula (personalidad definida)
- Carlitos se suma a la lista de agentes reales: Rabín, Risko, Spinita (pendiente), Carlitos, Aurora

**Aclaración nomenclatura:** "Clawdio" ya no es un agente real — quedó como apodo genérico del período OpenClaw→Hermes para referirse en conjunto a los agentes de IA. Los agentes reales hoy: **Rabín, Risko, Spinita (pendiente), Carlitos, Aurora.**

---

## Ciclo completo de Risko

**Contexto:** Risko (instancia Hermes Agent para OP Risk) pasa por su propio ciclo de migración y optimización durante esta sesión.

**Hallazgos previos al ciclo:**
- Risko: `risko-gateway.service` completa, `HERMES_HOME=/home/i3/.risko/`, bot `@Risko_OP_bot`, modelo original `gemini-2.5-flash`. Desplegada 2026-05-05, **nunca llegó al INVENTARIO_MAESTRO ni LOG_CAMBIOS_2026.md principal** (despliegue en chat aislado)
- Contenedor Docker fantasma `hermes-risko` (#3) corriendo desde 2026-06-03, compitiendo por el mismo token de Telegram que `risko-gateway.service`, causando conflictos de getUpdates. Compartía directorio `/home/i3/.risko` sin estado propio. **Detenido (no eliminado) esta sesión**
- Nextcloud OP Risk: contenedor `op-risk-nextcloud`, puerto 8090, `docker-compose.nextcloud.yml` en `/srv/op-risk/`, datos en `/srv/op-risk/nextcloud-data/`, expuesto en `docs.risk.montuschi.cl`. 16 documentos indexados desde `/mnt/extra/OP Risk/`
- voice-proxy.service: proxy de transcripción de la era OpenClaw (puerto 9877), detenido/deshabilitado 2026-04-18, reemplazado por `stt-proxy`. Archivo `.service` inactivo en disco — candidato a limpieza física

**Cambios del ciclo Risko:**
- Modelos: `qwen3.5:122b-a10b` → `qwen3.6:35b-a3b` (24GB, MoE, entra completo en GPU) por derrame a CPU con el 122b
- Confirmado: 26.4s primera respuesta vs 2m2s anterior — **mejoría dramática**
- Riesgo identificado como Gemini por contaminación de sesión del 30-may (resuelto durante ciclo)
- Montu resolvió algo relacionado a `/sethome` en chat individual con Risko (pendiente que Montu explique detalle para registro correcto)

**Diagnóstico de confiabilidad de Risko (4 puntos):**

1. **Contaminación de contexto por sesiones sin límite** —mecanismo transversal: `compression.enabled: false` en Hermes, sesiones nunca se resetean solas
2. **Identidad como Gemini** — sesión de Telegram del 30-may contaminó la configuración actual; Risko "se identificó como Gemini" hasta limpieza de contexto
3. **Contenedor fantasma hermes-risko** — competía por token de Telegram con `risko-gateway.service`, causando getUpdates conflictivos. Detenido (no eliminado) 2026-07-10
4. **Derrame a CPU del modelo 122b** — qwen3.5:122b-a10b derramó 95% a CPU, cayendo de ~27 tok/s a ~15 tok/s con contexto real; se resolvió cambiando a qwen3.6:35b-a3b (24GB MoE, entra completo en GPU)

---

## Aclaraciones de rol (sessión 2026-07-10)

**Rol Aurora vs. Rabín resuelto (definitivo):**
- **Aurora:** escribe documentación técnica (LOG_CAMBIOS, INVENTARIO_MAESTRO, commits a MontuMS) — **cero acceso** a documentación personal de Montu
- **Rabín:** solo LEE documentación técnica (consulta/referencia, no escribe ahí); es dueño completo (lectura+escritura) de la documentación personal de Montu (tareas, ideas, notas)
- Pendiente de definir: ¿el "solo lectura" de Rabín sobre lo técnico es una restricción de permisos Unix real, o una regla de comportamiento en su config?

**Capacidad de localización Aurora:**
- Requisito nuevo: Aurora debe poder responder dónde vive cierta información (¿dónde está X?)
- Pendiente evaluar: RAG vectorial vs búsqueda de texto completo (ripgrep) sobre repo
- **BACKLOG-AURORA-FASE2:** diseñar en su propia sesión, no bloqueante para que Aurora exista y documente hoy

**Próximos items pendientes:**
- Visual-Voice STT: benchmark mlx-whisper (large-v3 / large-v3-turbo / medium) — aún no ejecutado → documentar resultado + decisión final cuando se corra Fase 4
- Disco RESPALDO_ARCA: desconectado (no perdido), ubicación fue ambigua en inventario → corregir estado a "desconectado, pendiente reconexión"
