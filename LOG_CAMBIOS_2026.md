
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
