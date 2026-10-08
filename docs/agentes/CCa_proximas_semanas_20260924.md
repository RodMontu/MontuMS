# QA-A-02 — "Próximas Semanas" — 2026-09-24

**Ventana:** SPP (Miaude), worktree `/c/Users/OptiFierro/Desktop/optifierro-proximas-semanas`
(rama `proximas-semanas`, base `master`=`f430b75`, verificado al inicio). Sin commit — diff en
`/Users/montu/MontuMS/docs/agentes/diffs/proximas_semanas_diff_20260924.patch`.

## Archivos editados
- `backend/routers/calendario_futuro.py:1-218` — reescrito completo.
- `frontend/src/components/domain/CalendarioFuturo.tsx:1-400` — agregadas interfaces
  `BloqueFecha`, componente `BloqueResumen` (líneas ~149-207) y dos bloques colapsables
  "Atrasado" / "Sin fecha confirmada / muy futura" antes y después de las 3 semanas.

## Filtro exacto copiado de `programacion.py` (`_obtener_pids_pendientes`, `programacion.py:1404-1498` en `master`)
- `it.Estado IN ('PEN','IET','APR','ING')`
- `v.estado <> '00'`
- `p.estado NOT IN ('00','O40','O60')`
- `ISNULL(av.avance_pct, 0) < 100` (avance vía `CROSS APPLY MAX(PIEZA_PRODUCCION.PIE_AVANCE)` por `dp.id`)
- FP-LC: `es_despacho_directo(id_forma, largo_mm, diametro)` importado de `motor_v2.py` (no editado,
  solo import) — excluye por etiqueta, no por IT completa (una IT puede mezclar etiquetas FP-LC y no-FP-LC;
  el query original de calendario_futuro agrupaba a nivel IT, lo cual habría sumado igual el kg de
  etiquetas FP-LC dentro de una IT mixta — por eso cambié la granularidad de la consulta a nivel etiqueta
  y agrupo en Python después de filtrar).
- **No copiado:** la rama `it.Estado = 'IVI' AND DATEDIFF(...)<=5 AND CalidadAcero LIKE '%S'` de
  `_obtener_pids_pendientes` — caso borde (acero "S", IT recién invalidada) no incluido; diferencia esperada
  mínima frente a Compromisos Futuros. Documentado como gap conocido, no bloqueante.

## Número real verificado vs Compromisos Futuros
SELECT acotado desde TO contra Cubigest (solo lectura, réplica del filtro en Python suelto, sin poder
importar `_obtener_pids_pendientes` por territorio ajeno):

- Cerrillos (Cubigest id=4), rango 2026-09-24..2026-09-30 (semana 1):
  - **Lógica vieja (actual en main, sin avance/estado/FP-LC):** 373.477,4 kg
  - **Lógica nueva (avance<100 + estado IT/pieza/viaje + FP-LC excluido):** 154.126,1 kg
  - Ratio viejo/nuevo = **2,42×** — coincide con el ">2x" reportado en el spec §2/§5 para QA-A-02.
- No pude correr el endpoint real de Compromisos Futuros (`compromisos_semanales.py`, territorio de otra
  ventana) para comparar 1:1; el número de 154.126,1 kg usa el mismo filtro central que
  `_obtener_pids_pendientes` (salvo la excepción IVI/acero-S arriba), así que debería acercarse bastante.
  **NO VERIFICADO end-to-end contra el endpoint real de Compromisos Futuros.**

## Riesgos / pendientes
1. **NO VERIFICADO end-to-end**: `calendario_futuro.py` importa `from universo_fechas import
   clasificar_fecha` — ese módulo no existe todavía en este worktree (lo crea otra ventana hermana en
   paralelo). El archivo no puede ejecutarse hasta que exista con la firma acordada
   `clasificar_fecha(fecha_despacho, horizonte_reprog=None) -> str` retornando
   `"atrasada_valida"/"atrasada_suciedad"/"proxima"/"lejana_normal"/"muy_futura"`.
2. Ventana SQL ampliada a -800d/+900d (antes: sin filtro de fecha en absoluto salvo el post-proceso en
   Python que solo miraba hoy..+20). Fechas basura tipo 2090/2099 (mencionadas en el spec para Cerrillos)
   quedan fuera de ambos extremos — no entran a "atrasada suciedad" ni a "muy futura", simplemente no se
   traen. Si se necesita contarlas explícitamente, hay que ensanchar la ventana o hacer una query de
   conteo aparte.
3. Sin `TOP` en la query (a diferencia de `_obtener_pids_pendientes` que trunca en 2000) — no debería haber
   problema de truncamiento silencioso en esta vista, pero la ventana ampliada trae más filas que antes;
   no medí volumen total, solo el rango de la semana 1 de Cerrillos.
4. El backend ahora devuelve `{"error": ...}` en vez de `[]` silencioso cuando Cubigest falla (spec §4,
   punto 5) — el frontend ya lo muestra (`data?.error`), pero **no probé el caso de falla real de Cubigest**
   (solo el camino feliz).
5. `npm install` + `npx tsc --noEmit -p tsconfig.app.json` corrido en el worktree: sin errores de tipos.
   No corrí el backend real (no puedo, falta `universo_fechas.py`) ni levanté el frontend en navegador.

## Qué necesito de la Coordinadora
- Path/import real de `universo_fechas.py` cuando exista (confirmar que quedó en `backend/` al mismo nivel
  que `motor_v2.py`, y que la firma coincide con la acordada arriba) para poder correr el endpoint completo
  y comparar 1:1 contra Compromisos Futuros.


---

## Addendum 25-09 — Unificación de criterio de semana (fix de Coordinadora, pedido directo de Montu)

**Pedido:** unificar el criterio de "semana 1/2/3" entre Próximas Semanas y Compromisos Futuros, adoptando
el de Compromisos Futuros (semana calendario lunes-domingo vía `_lunes_de_semana(offset)`, no el rolling
`hoy..+6d` que tenía Próximas Semanas).

**Cambio aplicado:** `lunes_semana1 = hoy - timedelta(days=hoy.weekday())`, `domingo_semana3 = lunes_semana1
+ 3 semanas - 1 día`. La clasificación se reordenó: primero se chequea si `fecha` cae en la ventana
`[lunes_semana1, domingo_semana3]` (entra a "semana" sin importar el veredicto de `clasificar_fecha`,
igual que `compromisos_semanales.py` que no separa "atrasado" dentro de la semana solicitada); solo si cae
fuera de esa ventana se aplica el criterio atrasada/muy_futura de siempre. Sin este reordenamiento, un día ya
pasado de la semana 1 (ej. lunes/martes si hoy es jueves) se perdía en el bucket "atrasadas" en vez de
mostrarse en semana 1 — exactamente el mismo tipo de desfase que QA-A-02 ya había encontrado, pero en el
límite de fecha en vez de en el filtro de datos.

**Verificado:** `ast.parse` OK. Cálculo real para hoy (25-09, viernes): `lunes_semana1=2026-09-21`,
`domingo_semana3=2026-10-11` — coincide exacto con lo que devolvería `_lunes_de_semana(0)` en
`compromisos_semanales.py` para la misma fecha. No verificado contra Cubigest en vivo desde esta sesión
(mismo problema de entorno documentado en `CCa_vista_semanal_qa_20260924.md`, addendum 25-09 — no es
network real, es la invocación puntual de esta sesión).

Diff: `diffs/proximas_semanas_diff_20260925_v2.patch`.
