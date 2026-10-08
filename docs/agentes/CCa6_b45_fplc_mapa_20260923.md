# B45 — Mapa de FP-LC en el SPP y propuesta de exclusión mínima (SOLO LECTURA)

**Agente:** CCa-6 (apoyo a Miaude) · **Repo:** OptiFierro-V2, HEAD `8604d50` (verificado en TO vía SSH, `git show HEAD:<archivo>`)
**Fecha:** 2026-09-23 · **Para:** entrega jueves 24-09 (Gerentes Operaciones/Logística + 3 jefes de planta)

> Nota de entorno: hay otro CCa editando `motor_v2.py` y `programacion.py` en la copia de trabajo de TO (working tree con cambios sin commitear en esos dos archivos, para B16). Todo lo citado abajo es contra `HEAD` estable (commit `8604d50`), no contra el working tree a medio editar.

---

## 1. Mapa completo de FP-LC

### Definición de negocio
FP-LC = Fierro en Punta - Largo Comercial (6–12 m). No pasa por ninguna máquina: va de Bodega directo al camión. Debe tratarse como "no es una máquina real" del SPP.

### Backend — `backend/motor_v2.py` (HEAD)
| Línea | Qué hace |
|---|---|
| `motor_v2.py:131` | `MAQUINAS_SIN_OPERADOR = {"FP-LC"}` — FP-LC no requiere operador. |
| `motor_v2.py:130-142` | `MAQUINAS_ACTIVAS["Cerrillos"]` incluye `"FP-LC"` junto con las 10 máquinas reales de Cerrillos. Solo aparece en Cerrillos (sucursal 10); Calama y Coronel no la tienen. |
| `motor_v2.py:172-174` | `FPLC_LARGO_MIN = 6000`, `FPLC_LARGO_MAX = 12000` (mm) — comentario dice "confirmar con cliente"; el valor de negocio (Montu 23-09) es 6–12 m, coincide. |
| `motor_v2.py:458-468` (`resolver_ruta`) | Caso especial con **prioridad más alta** (antes que matriz histórica y fallback AD/AG): `if id_forma==1 and largo_a is not None and FPLC_LARGO_MIN<=largo_a<=FPLC_LARGO_MAX and diametro<=DIAMETRO_AD_MAX: return ["FP-LC"], False`. Este es el único punto donde el Motor decide que una pieza "es" FP-LC. |
| `motor_v2.py:578-611` (`ajustar_ruta_por_avance`) | Para piezas con avance parcial (0%<avance<100%), descarta explícitamente `"FP-LC"` (junto con la máquina de solo-corte) como primer paso ya cursado, dejando la etapa siguiente. Ya existe lógica defensiva anti-reasignación a FP-LC en piezas con avance. |
| `rutas_por_forma` (SQLite, vía `_buscar_ruta_historica`) | 0 filas con FP-LC — la ruta histórica nunca produce FP-LC; solo sale del caso especial de línea 458-468. |

FP-LC **no aparece** por nombre en `backend/main.py`, `backend/routers/maquinas.py` ni `backend/routers/tiempos_maquina.py` (grep sin resultados) — estos archivos no tienen lógica propia de FP-LC, heredan lo que ya está en la máquina "operativa" de SQLite (ver §SQLite).

### Backend — `backend/routers/programacion.py` (HEAD)
| Línea | Qué hace |
|---|---|
| `programacion.py:789` | `from motor_v2 import SUCURSALES, MAQUINAS_ACTIVAS, MAQUINAS_SIN_OPERADOR, _operadores_candidatos` — dentro del endpoint de **reprogramación manual** (reasignar un PID a otra máquina). |
| `programacion.py:794-806` | Valida cada máquina propuesta por el usuario: si está en `MAQUINAS_ACTIVAS` (FP-LC lo está, para Cerrillos) pasa el check de "máquina activa"; si está en `MAQUINAS_SIN_OPERADOR` (FP-LC lo está) se salta el check de operador disponible. **Consecuencia: un usuario puede reasignar manualmente cualquier PID de Cerrillos a FP-LC vía este endpoint sin que el backend lo rechace.** |
| `_obtener_pids_pendientes` (`programacion.py:1223`) | Universo de etiquetas pendientes que alimenta tanto al Motor (`programar_turno`) como a la Bolsa (`programacion.py:500,519`). No filtra por máquina resultante — la etiqueta entra aquí *antes* de que `resolver_ruta` decida si es FP-LC. |
| `_obtener_pids_pendientes_optisteel` (`programacion.py:1420`) y `_obtener_pendientes_bolsa_optisteel` (`programacion.py:1463`) | Universos paralelos (Cuadro OptiSteel) — también sin filtro por resultado de ruta. |

### SQLite (`backend/optifierro_v2.db`, vía SELECT)
FP-LC está dado de alta como máquina real en 3 tablas maestras (todas `sucursal_id=10`, `maquina_id=17`):

| Tabla | Fila FP-LC |
|---|---|
| `maquinas_info` | `(10, 17, 'FP-LC', 'Sin Operador Asignado', 'operativa', '')` — **estado `operativa`**, visible en Gestor de Máquinas. |
| `hebras` | `(10, 17, 'FP-LC', 0,0,0,0,0,0,0,0,0,0)` — todos los diámetros en 0 (fila "vacía" pero presente). |
| `diametros` | ídem, todos 0. |
| `rutas_por_forma` | 0 filas — confirma que FP-LC nunca sale de la matriz histórica. |
| `compatibilidad_formas`, `restricciones` | 0 filas. |

No hay tabla llamada `maquinas` (el CLAUDE.md la referencia genéricamente); la tabla real es `maquinas_info`.

### Frontend (`frontend/src`)
`GET /api/maquinas` (`routers/maquinas.py:35`) sirve `global_recursos`, cargado en memoria desde `maquinas_info` en el `lifespan` de `main.py`. Como FP-LC está `operativa` en esa tabla, **se propaga sin filtro** a:
- **Gestor de Máquinas** (`GestorMaquinas.tsx:32-35`) — pestañas maestro/diámetros/hebras/restricciones, todas por `/api/maquinas*`. FP-LC aparece como fila editable en las 4 pestañas.
- **Reasignación manual en el Gantt** (`GestorProgramacion.tsx`, `RepartoModal`, líneas 739-821) — `recursos` viene del mismo `/api/programacion` (que a su vez expone `global_recursos`); el selector de máquinas (línea 821 `recursos.map`) no excluye FP-LC, consistente con que el backend tampoco la rechaza (ver `programacion.py:794-806` arriba).
- **Gantt principal** — las columnas de máquina se arman desde `data.recursos` (mismo origen); si FP-LC tiene una tarea asignada (caso real, ver §2) aparece como columna/fila igual que cualquier máquina.
- **Producción por Máquina** (`TiemposPorMaquina.tsx`) — consume `/api/tiempos-maquina`, que consulta **Cubigest directamente** (`tiempos_maquina.py:154-176`, join contra tabla `MAQUINA` de Cubigest por `IdForma`+`diametro`) — **NO VERIFICADO** si Cubigest tiene un `MAQ_NRO` para "FP-LC" con historial suficiente para pasar el N-mínimo de B26; dado que en SQLite local FP-LC solo tiene 7 registros históricos totales (ver §2), es improbable que supere el umbral, pero no se verificó contra Cubigest (fuera de alcance de esta pasada, requeriría SELECT adicional en Cubigest).

No se encontraron menciones textuales `"FP-LC"` hardcodeadas en `frontend/src` (grep sin resultados) — todo lo que aparece en pantalla es porque el dato viene "operativo" desde `maquinas_info` o porque el Motor generó una tarea con `nombre_maquina="FP-LC"`.

---

## 2. Datos reales (últimas 2 semanas, 2026-09-09 a 2026-09-23)

Fuente: SQLite local en TO (`optifierro_v2.db`), tablas `historial_asignaciones` (registro de asignaciones reales del Motor) y `programacion_guardada` (lo que efectivamente se guardó y se le muestra al usuario).

| Métrica | Valor |
|---|---|
| Asignaciones totales (todas las sucursales, `asignado=1`) | 1239 piezas / 2 273 520,6 kg |
| Asignaciones totales solo Cerrillos (única sucursal con FP-LC) | 557 piezas / 1 214 432,7 kg |
| **Asignaciones a FP-LC** | **5 piezas / 7 593,9 kg** (PITs 3580824, 3596181, 3596187, 3578973, 3606148 — fechas 2026-09-21 y 2026-09-23) |
| FP-LC / total todas sucursales | **0,40% de etiquetas · 0,33% de toneladas** |
| FP-LC / total Cerrillos | **0,90% de etiquetas · 0,63% de toneladas** |
| Histórico completo (`programacion_detalle`, desde abril 2026) | Solo 7 filas / 8 225 kg en total — confirma volumen bajo y consistente. |
| `programacion_guardada` (Cerrillos, últimas 2 semanas, 20 turnos guardados) | **9 de 20 turnos guardados contienen "FP-LC" en `tareas_json`** (0 en `bolsa_json`) → hoy el usuario SÍ ve FP-LC como fila/tarea en el Gantt en ~45% de los turnos de Cerrillos de las últimas 2 semanas, aunque el volumen de piezas sea bajo. |

**Conclusión de datos:** volumen absoluto bajo (0,3–0,9% según corte), pero visibilidad frecuente en el Gantt de Cerrillos (9/20 turnos). Confirma que es "ruido" recurrente más que un problema de capacidad.

---

## 3. Qué pasa con esas etiquetas al excluir FP-LC

Opciones evaluadas:

**(A) No se programan, se omiten de pendientes/Bolsa/conteos.**
- `_obtener_pids_pendientes` (`programacion.py:1223`) seguiría trayendo la etiqueta (nada la distingue *antes* de `resolver_ruta`); haría falta filtrarla *después* de que `resolver_ruta` devuelva `["FP-LC"]`, o la etiqueta desaparecería silenciosamente sin dejar rastro — el jefe de planta no vería que existe ni que fue excluida a propósito. Riesgo de confusión ("¿por qué esta IT no aparece en ningún lado?").
- Efecto en conteos: "asignadas/total" bajaría el denominador en Cerrillos (~0,9%), impacto marginal pero medible. `pendientes` bajaría en la misma proporción. Toneladas: -0,63% en Cerrillos.
- Efecto en B16 (`agentes/B16_diseno_spec.md:39-44`): `saldo_mh = capacidad_mh − Σ duracion_min`. Como FP-LC está en `MAQUINAS_SIN_OPERADOR`, **NO VERIFICADO** si `estimar_duracion_min` hoy le asigna una duración distinta de cero a las tareas de FP-LC — si la suma, excluirla aumentaría `saldo_mh` (más capacidad "libre" reportada); si no la suma (por no tener operador), no hay efecto. Este punto es importante coordinarlo con el CCa de B16 antes de tocar nada, porque B16 entra recién el jueves y toca las mismas líneas (`motor_v2.py` `programar_turno` ~l.772, `programacion.py` `generar_programacion` ~l.944-1002).

**(B) Se listan aparte como "despacho directo" sin máquina ni tiempo.**
- Preserva trazabilidad (el jefe de planta ve que la IT existe y fue clasificada como despacho directo, no que "desapareció").
- Requiere una categoría nueva en la UI (aunque sea una etiqueta/badge simple) — más superficie de cambio que (A), pero menos riesgo de percepción de "datos perdidos" el día de la demo a Gerencia.
- Efecto en conteos/toneladas: igual que (A) si se excluyen de "asignadas/pendientes de máquina", pero se puede mantener un conteo aparte ("despacho directo: N etiquetas / X ton") para que el cuadro OptiSteel siga cuadrando en toneladas totales.

**Recomendación:** (A) para el filtrado interno del Motor (no ensuciar rutas/capacidad de máquina), combinado con una etiqueta visual mínima en frontend para no dar la sensación de pérdida de datos — ver punto único de filtrado abajo. No es necesario un endpoint ni tabla nueva para mañana; alcanza con no generar la tarea de máquina y, opcionalmente, taggear la IT en la respuesta de pendientes con `es_despacho_directo: true` para que el frontend la muestre en una fila informativa aparte del Gantt (sin ocupar columna de máquina).

---

## 4. Propuesta de cambio mínimo y seguro

**Punto único de filtrado recomendado:** en `resolver_ruta` (`motor_v2.py:458-468`), justo donde hoy se decide `return ["FP-LC"], False`. Es el único lugar del código donde el sistema "sabe" que una pieza es FP-LC — todo lo demás (Bolsa, pendientes, conteos, Gantt) consume el resultado de esta función indirectamente vía el flujo de `programar_turno`.

| # | Archivo:línea | Cambio | Riesgo de regresión | Cómo probarlo en arnés |
|---|---|---|---|---|
| 1 | `motor_v2.py:466-468` | En vez de `return ["FP-LC"], False`, devolver una ruta vacía o un marcador (`["__DESPACHO_DIRECTO__"]`) que el llamador (`programar_turno`) interprete como "no asignar a máquina, no consumir capacidad, no operador". | Medio — es el corazón del caso especial; si el marcador no se maneja en todos los consumidores de `resolver_ruta` (hay al menos 2: flujo normal y `ajustar_ruta_por_avance`), puede romper reprogramación de piezas con avance parcial que hoy dependen de ver `"FP-LC"` en la ruta para saltarla (`motor_v2.py:607`). |
| 2 | `motor_v2.py:130-142` (`MAQUINAS_ACTIVAS["Cerrillos"]`) | Quitar `"FP-LC"` del set. | Bajo si el punto 1 ya impide que se genere la tarea; pero si se quita esto *sin* tocar el punto 1, `programacion.py:794` (reprogramación manual) empezaría a rechazar FP-LC como "máquina no activa" — que es justo el efecto deseado para bloquear la reasignación manual. Este cambio por sí solo (sin tocar `resolver_ruta`) ya cierra el hueco de §1 (reprogramación manual a FP-LC). |
| 3 | `motor_v2.py:131` (`MAQUINAS_SIN_OPERADOR`) | Sin cambio necesario si se hace el punto 2 (FP-LC ya no pasaría el check de "activa" antes de llegar al de operador). |
| 4 | SQLite `maquinas_info` fila `(10,17,'FP-LC',...,'operativa',...)` | Cambiar `estado_maquina` a algo distinto de `'operativa'` (ej. `'inactiva'` o `'no_maquina'`), **si** el Gestor de Máquinas / Gantt ya filtran por `estado_maquina` en otro lado — **NO VERIFICADO**, no se confirmó que `GestorMaquinas.tsx` o el armado de columnas del Gantt filtren por este campo; si no filtran, este cambio de dato no alcanza solo y haría falta un filtro explícito en frontend o en `/api/maquinas`. Es un cambio de **dato**, no de código — más seguro para mañana si se confirma que alcanza, pero requiere verificarlo primero (no tocar la fila sin confirmar el efecto, es DB de producción). |
| 5 | Frontend — filtro adicional en `GestorMaquinas.tsx`, `GestorProgramacion.tsx` (armado de columnas/selector `RepartoModal:821`) | Solo si el punto 4 no alcanza: excluir explícitamente `nombre_maquina === "FP-LC"` (o `estado_maquina !== "operativa"`) al listar máquinas seleccionables. | Bajo-medio, cambio acotado a UI, pero son 2-3 archivos distintos (más superficie que un solo punto backend). |

**Serialización con B16:** los puntos 1 y 2 tocan `motor_v2.py` (líneas 130-142 y 458-468) y potencialmente `programar_turno`, que es exactamente donde B16 va a insertar `_calcular_capacidad_mh` (spec dice `motor_v2.py` `programar_turno` ~l.772, `programacion.py` `generar_programacion` ~l.944-1002). **Hay conflicto directo de archivos con el otro CCa que ya está editando esto.** Recomendación: no tocar nada hoy/mañana sin coordinar con ese CCa — aplicar el cambio después de que B16 mergee, o coordinar un solo commit conjunto.

---

## 5. Riesgos para mañana y qué NO conviene tocar

- **No tocar `motor_v2.py` ni `programacion.py` antes de la demo del jueves** — ambos archivos tienen ediciones en curso de otro CCa para B16 (working tree sucio, no commiteado). Cualquier cambio de FP-LC ahí debe esperar a que ese trabajo cierre, o coordinarse explícitamente.
- **No cambiar el `estado_maquina` de FP-LC en SQLite** sin antes confirmar (con una prueba de lectura en arnés, no en producción) que el frontend efectivamente filtra por ese campo — si no filtra, el cambio de dato no tiene efecto visible y solo genera falsa sensación de haber resuelto el problema.
- **El volumen real es bajo (0,3–0,9%)** — no es un problema de capacidad/negocio urgente hoy; el riesgo real es de **percepción** en la demo (que Gerencia vea "FP-LC" como fila de máquina en el Gantt y pregunte por qué una "máquina ficticia" está en el sistema). Para mañana, alcanza con **explicarlo verbalmente** como comportamiento conocido y ya acotado (9/20 turnos de Cerrillos, <1% del volumen), sin necesidad de deployar un fix antes de la reunión.
- **El check de reprogramación manual (`programacion.py:794-806`) no bloquea reasignar a FP-LC hoy** — es el hallazgo más "afilado" de este mapeo: un jefe de planta podría, sin querer, arrastrar una pieza real a FP-LC vía el Gantt y el backend lo aceptaría. Vale la pena mencionarlo aunque no se implemente antes del jueves.
- Todo lo marcado **NO VERIFICADO** arriba (Cubigest `MAQUINA` para FP-LC en `tiempos_maquina.py`, si `GestorMaquinas.tsx` filtra por `estado_maquina`, si `estimar_duracion_min` suma tiempo a tareas FP-LC) requiere una pasada adicional antes de implementar — no asumir.
