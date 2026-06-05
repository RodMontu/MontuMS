
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
