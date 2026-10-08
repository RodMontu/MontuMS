# QA-A-01 + mitad "Vista Semanal" de QA-A-02 — Informe (Miaude, 2026-09-24)

**Worktree:** `TO:/c/Users/OptiFierro/Desktop/optifierro-vista-semanal-qa` (rama `vista-semanal-qa`, base `f430b75`).
**Diff:** `docs/agentes/diffs/vista_semanal_qa_diff_20260924.patch` (sin commitear, per instrucciones).
**Spec:** `UNIVERSO_FECHAS_spec.md` V6, secciones 3, 4 y 5.

## 1. VistaSemanal.tsx — línea "Atrasado ≤30d" + "Sin fecha confirmada / muy futura"

- `frontend/src/components/domain/VistaSemanal.tsx:202-237` (nuevo bloque en `SucursalCard`, sidebar,
  justo después de "Resumen {semana}").
- No toqué el filtro `getFiltered`/`inicioActual` de las 3 pestañas existentes (quedan igual, tal como pide
  el punto 1 de la tarea: "deja las 3 pestañas actuales"). En vez de eso, agregué un bloque que lee
  `data.resumen_categorias[sucId]` directo del backend, **sin pasar por `getFiltered`** — ese es el "arreglo
  del descarte": antes ese dato ni se pedía/mostraba porque ninguna de las 3 pestañas incluye fechas
  `<hoy`; ahora se muestra aparte, siempre visible, independiente de qué pestaña esté activa.
- Incluye la leyenda de la sección 3 del spec ("No considera ITs con fecha de despacho mayor a 60 días
  (N ITs / X.XXX kg fuera; ver aparte)"), con N/kg reales de `muy_futura_n`/`muy_futura_kg` por sucursal.
- Si `data.errores[sucId]` existe (fallo de Cubigest, ver punto 4), se muestra banda de error roja ahí en
  vez del resumen — no se confunde con "0 kg".
- **NO VERIFICADO visualmente en browser**: no corrí `npm install`/`npm run dev` en este worktree (no
  tiene `node_modules`, no lo instalé porque no fue pedido y no quería alterar el worktree más allá del
  código). Tampoco pude correr `tsc --noEmit` por la misma razón. Revisión fue solo lectura/estructura JSX.

## 2. Compromisos Futuros — filtros avance/estado/FP-LC

- `backend/routers/compromisos_semanales.py:44-58`: el endpoint `/api/compromisos-semanales` ya llama a
  `_obtener_pids_pendientes` (la misma función que usa Vista Semanal), que aplica avance<100, estado
  `PEN/IET/APR/ING` (+ `IVI` con excepción), y exclusión FP-LC (`es_despacho_directo`, B45). **No hice
  cambios de filtro acá** porque la paridad con el universo ya existe por construcción (comparten función) —
  confirmé leyendo el código, no es un supuesto.
- Lo único que cambié en este archivo es el manejo de fallo de Cubigest (punto 4).
- **NO VERIFICADO end-to-end**: no pude comparar kg reales Cerrillos semana 24–30 sep entre Compromisos
  Futuros y Próximas Semanas — `calendario_futuro.py` (que sirve Próximas Semanas) es de otra ventana
  hermana y no sé si ya integró su lado del criterio de aceptación. Pendiente confirmar con la
  Coordinadora antes de cerrar QA-A-02 completo.

## 3. TOP 2000 → 3000 + log de truncamiento

- `backend/routers/programacion.py:1424` — `SELECT TOP 2000` → `SELECT TOP 3000`.
- `backend/routers/programacion.py:1524-1531` (nuevo) — log `logger.warning` si `len(filas) >= 3000`
  (proxy de truncamiento: no hice `COUNT(*)` real sin límite, tal como el spec dice que "el log es el
  mínimo aceptable" sin paginación completa hoy).
- **Cifra real antes/después: NO VERIFICADA esta sesión.** El spec V6 (secc. 2) ya trae el número
  (Cerrillos: 2.231 filas reales vs 2.000 de límite, mismo query/ventana, tomado 24-09 por SELECT acotado
  desde TO). No repetí ese SELECT en vivo — no tengo necesidad adicional de tocar Cubigest solo para
  reconfirmar un número que la spec ya validó hoy mismo. Si la Coordinadora quiere la cifra post-fix con
  el nuevo límite 3000, hay que correr el mismo SELECT sin `TOP` y comparar contra 3000.

## 4. Fallo de Cubigest → error visible (antes `[]` silencioso)

- `backend/routers/programacion.py:1505-1513`: `_obtener_pids_pendientes` ahora hace `raise RuntimeError(...)`
  en vez de `return []` cuando `cubigest_db.execute_query` falla. Verifiqué que los 2 callers que NO son
  míos ya envuelven la función en su propio try/except (no rompen):
  - `backend/main.py:145` (scheduler automático) — try/except ya existente más abajo, degrada con log.
  - `backend/routers/calendario_futuro.py` — usa una query propia, no llama a esta función (comentario en
    el propio archivo: "Query separada... no tocar motor_v2.py").
- `backend/routers/programacion.py:622-628` (`/api/programacion/semanal`): ahora cada sucursal se prueba
  en su propio try/except; si Cubigest falla para una, se guarda en `data["errores"][sid]` y se sigue con
  las otras 2 (antes un fallo total tiraba abajo las 3 sucursales por el try/except global de toda la
  función). El try/except externo (línea ~674) también actualicé su fallback para incluir las claves nuevas
  (`resumen_categorias`, `errores`) y no romper el contrato de respuesta.
- `backend/routers/compromisos_semanales.py:49-58`: ahora hace `raise HTTPException(502, ...)` en vez de
  `todas_etiquetas = []`.
- **Secciones que SIGUEN con `[]`/0 silencioso (fuera de mi alcance, otras ventanas):** Materia Prima
  (`database_cubigest.py:obtener_comprometido_por_codigo` línea ~353, `materias_primas.py:239`) y Próximas
  Semanas (`calendario_futuro.py`). Confirmé que `obtener_comprometido_por_codigo` es de Materia Prima, no
  de Compromisos Futuros — por eso no lo toqué, según la instrucción explícita de solo tocarlo si aplica a
  Compromisos Futuros.

## 5. Clasificación por fecha — contrato con `universo_fechas.py`

- `backend/routers/programacion.py:1536-1560` (nuevo, dentro de `_obtener_pids_pendientes`, antes del
  `return pendientes`): `from universo_fechas import clasificar_fecha` — **import duro, tal como pide la
  instrucción ("trátalo como contrato ya acordado")**. El módulo `universo_fechas.py` NO existe todavía en
  este worktree (lo crea la ventana hermana en paralelo). Esto significa que **ahora mismo, en este
  worktree, `/api/programacion/semanal` y `/api/compromisos-semanales` van a fallar con `ImportError`** al
  llamar a `_obtener_pids_pendientes` — no pude levantar el backend para confirmarlo porque no until
  `universo_fechas.py` exista con la firma `clasificar_fecha(fecha_despacho, horizonte_reprog=None) -> str`
  (retornando `"atrasada_valida"/"atrasada_suciedad"/"proxima"/"lejana_normal"/"muy_futura"`), esto es
  **NO VERIFICADO end-to-end, bloqueado por dependencia cruzada**, exactamente como anticipaba la consigna.
  Necesito que la Coordinadora confirme cuándo ese módulo aterriza en el worktree compartido/rama para
  poder levantar el backend y probar de punta a punta.
- Manejo de `fecha_despacho` NULL o `'1900-01-01'` (fecha basura): lo clasifico directo como `"muy_futura"`
  sin llamar a `clasificar_fecha` (línea ~1540), porque la spec dice que "sin fecha confirmada" va en la
  misma línea que "muy futura" (secc. 3-4) — decisión mía, documentada acá por si la Coordinadora prefiere
  que `universo_fechas.py` mismo decida ese caso en vez de que yo lo intercepte antes.
- `horizonte_reprog` lo calculo como `fecha_despacho − fecha_compromiso_2` (última reprogramación, ya
  disponible en la query como `rep.FechaCompromiso2` / `MAX(FechaMod)` de `Reprogramar_IT`), replicando la
  fórmula de la sección 2 del spec.

## Riesgos / pendientes para la Coordinadora

1. **Bloqueante real:** sin `universo_fechas.py` en el worktree, el backend no levanta para las 2 rutas que
   toqué. No pude arrancar `python main.py` ni probar en browser. Todo lo de arriba es revisión de
   código/sintaxis (`ast.parse` OK en ambos `.py`), no ejecución real.
2. Confirmar si "Próximas Semanas" (otra ventana) ya integró su lado del criterio de aceptación de QA-A-02
   (kg Cerrillos semana 1 24-30 sep) — no pude verificarlo, ese archivo no es mío.
3. TS: no instalé `node_modules` en este worktree; `VistaSemanal.tsx` no fue tipo-chequeado ni renderizado.
4. Cifra TOP 2000→3000 tomada del spec (24-09), no re-verificada con SELECT en vivo esta sesión.


---

## Addendum 25-09 — Fix de Coordinadora tras QA cruzada (`QA_cruzada_semana1_20260925.md`)

**Hallazgo:** en `_obtener_pids_pendientes` (programacion.py, bloque de clasificación agregado en la
sesión 24-09), `fecha_str` (string, ej. `"2026-10-15"`) se pasaba directo a `clasificar_fecha(fecha_str, ...)`,
que espera un `date`. El `try/except` alrededor tragaba el `TypeError` silenciosamente (`categoria_fecha=None`)
para las 792 etiquetas revisadas por la QA cruzada — por eso "Atrasado ≤30d" en Vista Semanal quedaba en 0.
El propio bloque ya parseaba `fecha_str` a `date` (`d_desp`) para calcular `horizonte`, pero solo dentro del
`if fecha_compromiso_2:` y sin reutilizarlo para la llamada a `clasificar_fecha`.

**Fix aplicado (Coordinadora, no CCa):** se parsea `fecha_str` a `d_desp` una sola vez, antes del cálculo de
horizonte, y se reutiliza para ambos usos. `str(fecha_str)[:10]` en vez de `fecha_str` directo, defensivo por
si llega con componente de hora.

**Verificado:** sin acceso a Cubigest disponible desde esta sesión (falla de conexión de entorno, no del
código — ver detalle abajo), se verificó la lógica corregida de forma aislada con 5 casos sintéticos que
replican los formatos reales observados (fecha simple, sentinela `1900-01-01`, horizonte sospechoso vía
`fecha_compromiso_2`, atrasada, y fecha con componente de hora) — los 5 clasifican correctamente, sin
excepciones. `ast.parse` sobre el archivo completo: OK.

**Bug preexistente encontrado de paso (no corregido, fuera de alcance):** `database_cubigest.py` línea ~86,
el manejo de error de `connect()` hace `print(f"❌ Error conectando a Cubigest: {e}")` — el emoji revienta con
`UnicodeEncodeError` bajo la consola por defecto de Windows (cp1252), enmascarando el error real de conexión
con uno de encoding. Encontrado al intentar verificar el fix con una llamada real a Cubigest desde esta
sesión (que sí conectó bien en sesiones anteriores del mismo día — probable diferencia de entorno/consola
entre esa invocación y la mía, no necesariamente un problema de red real). Queda para la próxima ventana que
toque `database_cubigest.py`.

Diff actualizado: `diffs/vista_semanal_qa_diff_20260925_v2.patch`.
