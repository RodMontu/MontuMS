# CARLITOS 3.6 — Fase 0: Verificaciones B38, B13 y B6 del SPP

**Fecha:** 2026-09-23
**Agente:** Carlitos
**Proyecto:** OptiFierro-V2 (SPP — Sistema Planificador de la Producción)
**HEAD:** commit 4325640

---

## B38 — Minuta Coronel 21-09: suprimir de la vista de Programación los trabajos con 100 % de fabricación

### Evidencia

**Commit `912ffb2`** (`2026-09-22`): "feat(programacion): avance parcial por pieza con reasignacion de ruta a etapa siguiente". Este commit trata sobre **reasignar ruta de máquina** para piezas con avance intermedio (0%<avance<100%), NO sobre filtrar trabajos al 100% del Gantt. [backend/motor_v2.py:595,616]

**El filtro `AND ISNULL(av.avance_pct, 0) < 100` se aplica en 2 lugares:**

1. **`_obtener_pids_pendientes_optisteel`** (`backend/routers/programacion.py:1317`): filtra piezas pendientes de Cubigest que tienen avance=100%. Comentario: "Pieza ya terminada (avance=100%) no es 'pendiente de fabricar'".

2. **`_piezas_optisteel_por_viajes`** (`backend/routers/programacion.py:1441`): filtra piezas OptiSteel con el mismo criterio. Comentario: "Regla avance B: piezas 100% avanzadas ya no estan pendientes".

**El filtro NO se aplica a los eventos del Gantt (ya agendados):**

- `obtener_programacion()` carga eventos desde `global_eventos` (memoria) o desde `programacion_guardada` (SQLite: `backend/routers/programacion.py:255-285`) sin ningún filtro de avance.
- Los eventos ya guardados en el Gantt se muestran tal cual, sin verificar `avance_pct`.
- El motor_v2.py maneja `avance_pct >= 100` solo para la lógica de reasignación de ruta: "No se llama para avance>=100%" (`backend/motor_v2.py:616`). Las piezas al 100% se tratan como si tuvieran 0% avance (ruta normal desde el primer paso).

**Datos reales de Coronel (sucursales: Calama=1, Cerrillos=10, Coronel=14):**
- Base de datos: `backend/optifierro_v2.db`, 2320 tareas totales en `programacion_guardada` para Coronel.
- **0 tareas con `avance_pct >= 100`** en todo el histórico de Coronel.
- El campo `avance_pct` se setea solo cuando el Motor ejecuta la generación; tareas sin motor run no tienen este campo (valor N/A).
- Cuadro OptiSteel Coronel: 3 viajes (2026-09-23), 2 (2026-09-24), 3 (2026-09-25).

### Umbral exacto
`< 100` (estrictamente menor que 100). El dato de avance sale de `PIE_AVANCE` en Cubigest (tabla `PIEZA_PRODUCCION`), vía `CROSS APPLY`:
```sql
SELECT MAX(pz.PIE_AVANCE) AS avance_pct
FROM PIEZA_PRODUCCION pz
WHERE pz.PIE_ETIQUETA_PIEZA = dp.id
```
[backend/routers/programacion.py:1298-1300]

### Veredicto: **PARCIAL**

- ✅ **Sí se filtra en la Bolsa** (pendientes de fabricar) — `programacion.py:1317` y `:1441`
- ❌ **NO se filtra en los EVENTOS ya agendados del Gantt** — se cargan directamente desde `programacion_guardada` sin filtro
- Si un plan tiene un trabajo guardado con 100% de avance en el Gantt, seguiría visible (aunque en la práctica actual no hay ninguna tarea con `avance_pct >= 100` en Coronel)
- El commit `912ffb2` no implementa este filtro; solo maneja reasignación de ruta para 0%<avance<100%

---

## B13 — Coronel: "hueco real de programacion en OptiSteel, 0 filas 26-08 al 26-09"

### Evidencia

**`trabajos_optisteel` en el código:**

```
backend/importar_optisteel.py:5:  local trabajos_optisteel de optifierro_v2.db.
backend/importar_optisteel.py:35: CREATE TABLE IF NOT EXISTS trabajos_optisteel (
backend/importar_optisteel.py:108:        cur.execute("DELETE FROM trabajos_optisteel WHERE sucursal_id = ?", (sucursal_id,))
backend/importar_optisteel.py:110:            """INSERT INTO trabajos_optisteel
```

Solo referenced en `backend/importar_optisteel.py` (script de importación). **Ningún router ni endpoint usa esta tabla directamente.** No hay SELECTs a `trabajos_optisteel` en ningún endpoint activo. [backend/importar_optisteel.py:5,35,108,110]

**La Bolsa hoy usa:**
- `cuadro_programacion_optisteel` (SQLite) + Cubigest directamente (CROSS APPLY a `PIEZA_PRODUCCION`)
- Función `_obtener_pendientes_bolsa_optisteel()` en `backend/routers/programacion.py:1516`
- Decision de negocio B18 (definitiva): OptiSteel optimiza el corte; sin cuadro cargado, día queda vacío en la Bolsa.

**Datos reales de `trabajos_optisteel` para Coronel (sucursales=14):**
- **0 filas** para Coronel en la tabla `trabajos_optisteel`.
- Cuadro OptiSteel activo para Coronel: 3+2+3+6+3+1+6+4 viajes en las fechas recientes (2026-09-14 a 2026-09-25).

### Veredicto: **OBSOLETO (cerrar)**

- La tabla `trabajos_optisteel` está **vacía para Coronel** (0 filas).
- Ningún router la usa actualmente. La Bolsa usa `cuadro_programacion_optisteel` + Cubigest directamente (función `_obtener_pendientes_bolsa_optisteel` en `programacion.py:1516`).
- El archivo `importar_optisteel.py` que creó esta tabla parece ser legacy. Se puede cerrar B13 como obsoleto.

---

## B6 — "Bloqueo de dias para Remiz/Francisco/Jose"

### Evidencia

**Búsqueda exhaustiva en el código:**

```bash
grep -rn -i "bloque" backend/ frontend/src/
grep -rn -i "bloque.*dia\|dia.*bloque\|bloquear.*dia\|excluir.*dia\|feriado\|no.programar\|calendar.block\|dias.*habilit" backend/ frontend/src/
```

**Resultados encontrados para "bloque":**
- `motor_v2.py:266-281`: `bloque_maquinas`, `bloque_actual_sucursal` → son **bloques de la hoja Excel** (uno por sucursal), no tienen nada que ver con bloqueo de personas.
- `compromisos_semanales.py:207-212`: `bloqueadas` → son **ITs detenidas** (con info de obra), no bloqueo de días.
- `GestorProgramacion.tsx:131-146`: "bloque visual del Gantt" → son **bloques visuales** en la UI del Gantt.
- `main.py:238-272`: `feriado` → solo controla si es feriado CL para skip del scraper/scheduler.

**Búsqueda de nombres específicos:**
```bash
grep -rn -i "remiz\|francisco\|jose" backend/ frontend/src/
```
Solo aparece en `backend/migrate_p26.py` (script de migración de usuarios: Francisco, Jose Auger, Remiz Rivano). **Ningún código funcional los menciona.**

**`calendario_futuro.py`:** Existe en `backend/routers/calendario_futuro.py`, pero su función es mostrar ITs pendientes agrupadas en 3 semanas futuras desde Cubigest. **No tiene ninguna lógica de bloqueo de días.**

### Veredicto: **NO EXISTE**

- No existe ninguna función, tabla, configuración o código que realice "bloqueo de días" para Remiz, Francisco o José.
- Los únicos "bloques" referenciados son bloques de Excel en el motor, ITs bloqueadas/detenidas, y bloques visuales del Gantt.
- No corresponde ninguna acción adicional. Montu probablemente no recuerda el detalle porque esta funcionalidad nunca se implementó (o se descartó).

---

## Resumen ejecutivo

| Hito | Veredicto | Notas |
|------|-----------|-------|
| **B38** (100% fabricación en Gantt) | **PARCIAL** | Filtro aplica a Bolsa (pendientes), NO a eventos ya agendados del Gantt. Se necesita añadir filtro en `obtener_programacion()` para eventos cargados desde `programacion_guardada`. |
| **B13** (hueco OptiSteel Coronel) | **OBSOLETO (cerrar)** | Tabla `trabajos_optisteel` vacía para Coronel, ningún router la usa. Bolsa usa `cuadro_programacion_optisteel` + Cubigest directo. |
| **B6** (bloqueo días Remiz/Francisco/Jose) | **NO EXISTE** | No hay código de bloqueo de días para ninguna persona. Nunca se implementó. |
