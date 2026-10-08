# Actualizaciones — PROMPT_MOTOR_TIEMPOS_SONNET5.md

Correcciones sobre el plan original (planificación Opus 5, 2026-09-02). Se
registran aquí en vez de editar el original, para mantener trazabilidad.

## 2026-09-02 — Sesión de ejecución (tarde)

**Sección 5.3 — Calendario de turnos: RESUELTO**
- Ubicación: OptiFierro V2 → Administración → pestaña Geovictoria.
- Almacenamiento: persistido en el SQLite LOCAL de OptiFierro (no Cubigest,
  no API en vivo). Fuera del perímetro de riesgo de la Sección 2.
- Pendiente: nombre exacto de tabla/columnas, cobertura de las 3 plantas.

**Fase 0, tarea 1 (ingeniería inversa UI Cubigest) — DIFERIDA**
Postergada por decisión de Montu. Sigue pendiente.

**Sección 2.3, Regla 5 (aviso previo a Roberto) — DEROGADA**
Acuerdo nuevo, reunión de hoy: NO se avisa a Roberto antes de ejecutar
consultas contra Cubigest. Queda conforme con que el acceso quede
registrado en la bitácora (`bitacora_accesos_torres_ocaranza.md`). El resto
de las reglas duras de la Sección 2.3 (solo lectura, forma canónica,
ventana horaria, monitoreo de carga) siguen vigentes sin cambios.

**Fase 0, tarea 7 (permisos 6 bases) — DESCARTADA, ya validada**
Montu confirma que esto ya se validó hace ~6 meses con Roberto. No se
reabre. Retirar de cualquier lista de pendientes de Fase 0.

**División de trabajo Carlitos / CCa — ACLARADA**
Carlitos: exclusivamente tareas que tocan datos/estructura de una base de
datos (Cubigest o el SQLite local de OptiFierro).
CCa: tareas de backend/código (grep de queries existentes, ubicación de
archivos, lectura de configuración). Fase 0 tarea 1 / Paso A (descubrir la
tabla de piezas/etiquetas) se reasigna de Carlitos a CCa.

## ACTUALIZACIÓN — 2026-09-0X (post-hallazgo matriz_rutas.json)

**Fase 0, Tarea 1 (registro de paso por máquina) — TABLA IDENTIFICADA, CON UNA GRIETA
METODOLÓGICA QUE HAY QUE CERRAR ANTES DE DAR ESTO POR RESUELTO.**

### Lo confirmado

Script `extractor_rutas.py` (en TO: `/c/Users/OptiFierro/Desktop/optifierro/`, y su output
`matriz_rutas.json` en la misma ruta y en `backend/`) contiene una query ya escrita y ya
ejecutada contra Cubigest (marzo 2026) que identifica:

- **`PIEZA_PRODUCCION`** — tabla de registro de producción por máquina.
  - `PIE_ETIQUETA_PIEZA` → FK a `detallePaquetesPieza.id`
  - `PIE_MAQUINA` → FK a `MAQUINA.MAQ_NRO`
  - `PIE_FECHA_PRODUCCION` → timestamp de registro (mismo campo ya conocido del plan)
  - `PIE_OPERARIO` → operador
- **`MAQUINA`** — `MAQ_NRO`, `MAQ_NOMBRE`.

### La grieta encontrada — verificar antes de confiar en esto

Se inspeccionó el `matriz_rutas.json` real (2.133 combinaciones, 191 `IdForma` distintos,
diámetros 8–36mm): **`NroPasos` = 1 en el 100% de los casos, sin una sola excepción.**
Contradice la observación de Montu en la UI de Cubigest (acero grueso pasa por varias
máquinas).

**Hipótesis (no verificada, requiere consulta real vía Carlitos):** la query original agrupa
por `dp.id AS EtiquetaId` — `dp.id` es la llave primaria de fila de `detallePaquetesPieza`,
NO la etiqueta física. Esa tabla tiene un campo separado `Etiqueta` (varchar, código físico
del TAG) y un campo `IdMov` (no confirmado, sospechoso de ser FK a movimiento/máquina). Si
cada paso por máquina genera una fila nueva con `Id` distinto pero mismo `Etiqueta`, agrupar
por `dp.id` garantiza `NroPasos=1` por construcción, sin importar la realidad física.

**Tarea concreta para la próxima vez que Carlitos toque Cubigest (antes de Fase 2):**
re-ejecutar la misma query de `extractor_rutas.py` pero agrupando por `dp.Etiqueta` en vez
de `dp.id`, y comparar. Si `NroPasos > 1` aparece para acero grueso, la grieta queda cerrada
y Escenario A se confirma también a nivel de datos, no solo de UI. Si sigue en 1, hay que
investigar `IdMov` directamente.

### Nota técnica aparte, no bloqueante

`extractor_rutas.py` tiene `BASE_DIR = "/home/x/stack/optifierro_v2_frontend"` — ruta estilo
Linux, no Windows. El archivo generado sí aparece en rutas Windows reales
(`/c/Users/OptiFierro/Desktop/optifierro/`), así que probablemente corrió dentro del
contenedor Docker del backend (Linux por dentro, aunque el host sea Windows). No bloquea
nada, pero vale la pena confirmarlo antes de reusar el script tal cual.

---

## ACTUALIZACIÓN — 2026-09-03 (cierre Fase 0)

### Fase 0, Tarea 1 — CERRADA. Escenario A confirmado a nivel de dato.

**Ejecutado por:** CCa (Claude Code, Anthropic API) orquestando script Python en TO.
Bitácora: `bitacora_accesos_torres_ocaranza.md` — entrada 2026-09-03 #5.

**Hipótesis verificada (CONFIRMADA):**
Query corregida agrupando por `dp.Etiqueta` (código físico del TAG) en vez de `dp.id` (PK
de fila) — Cerrillos, acero grueso (diámetro ≥18mm), último mes:
- 2406 etiquetas únicas en la muestra (TOP 5000 no llegó al límite → dataset cabe completo)
- **372 etiquetas con NroPasos > 1 (15.5%)** — segmento de ruta multi-máquina, consistente
  con el modelo de negocio (cortadora → dobladora/curvadora → estribadora)
- 2034 etiquetas con NroPasos = 1 (84.5%) — acero delgado o paso único

**Causa raíz de NroPasos=100% en matriz_rutas.json (CERRADA):**
La query original de `extractor_rutas.py` agrupaba por `dp.id` (PK de fila de
`detallePaquetesPieza`). Cada paso por máquina genera una fila nueva con `id` distinto pero
mismo `Etiqueta`, por lo que agrupar por `dp.id` garantizaba NroPasos=1 por construcción
matemática, independiente de la realidad física. Confirmado.

**Estado del entorno de conexión (registrar para futuras queries):**
- La conexión a Cubigest desde el contenedor backend (Linux) requiere:
  `Encrypt=no` + `OPENSSL_CONF` en modo legacy — el SQL Server de TO usa TLS antiguo.
- DB_NAME=Cubigest (réplica productiva). No existe réplica de pruebas activa a esta fecha
  (pendiente sin resolver, ítem 3 de `incidente_seguridad.md` tabla de pendientes).
- extractor_rutas.py sí corrió dentro del contenedor Docker del backend (Linux), confirmado.

**Índices verificados (Fase 0 Tarea 4):**
- Con índice en clave crítica: `dp.IdPieza`, `IT.IdSucursal`, `PIE_ETIQUETA_PIEZA` (PK).
- Sin índice líder (gaps, no bloqueantes): `detallePaquetesPieza.IdViaje`, `MAQUINA.MAQ_NRO`.
  Son oportunidades de optimización para Fase 2 (barrido máquina × mes). Registrar para Roberto.

**Respaldo auditoria_tiempos_2026/ (Fase 0 Tarea 0):**
- Rama `respaldo/auditoria-tiempos-2026` creada localmente en repo Optifierro-V2 (TO).
- 22 archivos, ~27MB commiteados. SIN PUSH — pendiente revisión de Montu del diff.
- .gitignore la tenía como artefacto generado/backup, sin razón de datos sensibles documentada.
- NOTA: el dataset incluye CSV de 128K registros (~26.8MB) de producción del cliente.
  Repo es privado (github.com/RodMontu/Optifierro-V2). Montu decide si hace push.

### Fase 0 completa — gate para Fase 1

Todas las tareas de Fase 0 están cerradas o explícitamente descartadas:
- Tarea 0 (respaldo): ✅ rama local lista, push pendiente de Montu
- Tarea 1 (tabla de piezas + Escenario A): ✅ CERRADA
- Tarea 2 (inventario columnas): ✅ cubierto por extractor_rutas.py + esta sesión
- Tarea 3 (tipo dato geometría): ✅ resuelto en sesión anterior (tabla relacional, no geometry)
- Tarea 4 (índices): ✅ verificado
- Tarea 5 (cardinalidad): pendiente — no bloqueante para Fase 1, aplazar a Fase 2
- Tarea 6 (calendario turnos): ubicación conocida (SQLite local OptiFierro, pestaña Geovictoria),
  nombre exacto de tabla/columnas pendiente para la implementación de CENSURA_JORNADA
- Tarea 7 (permisos 6 bases): ✅ descartada

**Próximo paso: Fase 1** — definición formal del indicador toneladas/hora y calibración
contra PLC (Línea de Corte Cerrillos). Ver PROMPT_MOTOR_TIEMPOS_SONNET5.md sección 7.
Gate de Fase 2: el .md de entregable de Fase 0 está en `actualizaciones_plan_motor_tiempos.md`
(este archivo). Entregable formal pendiente: archivar este resultado en MontuMS con Aurora.
