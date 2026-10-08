# UNIVERSO_FECHAS_spec.md — Reglas de fecha del universo de compromisos (V6)

**Fecha:** 2026-09-24 · **Agente:** Miaude (V6, ventana de diseño, sin código) · **Acordado con:** Montu, 24-09
**Código verificado en:** `master` = `f430b75` (B42 v2 y Sync ya desplegados; `database_cubigest.py`,
`programacion.py`, `motor_v2.py`, `GestorProgramacion.tsx` liberados de bloqueo).
**Fuentes:** `agentes/CCa11_sync_scheduler_diseno_20260924.md`, `agentes/QA_A_universo_20260924.md`,
datos reales por SELECT acotado (Cubigest, 3 plantas, avance<100, ITs PEN/IET/APR/ING).

## 1. Mapa de reglas actuales
| Sección | Función / archivo:línea | Ventana | Filtros |
|---|---|---|---|
| Programación | `_obtener_pids_pendientes_optisteel` `programacion.py:1634` | día del Cuadro | avance<100, sin FP-LC |
| Compromisos Futuros | `compromisos_semanales.py:39` → `_obtener_pids_pendientes` | −30/+21 d, offset sem [-2,+3] | igual al universo, sin Cuadro |
| Vista Semanal | `programacion.py:597` → `_obtener_pids_pendientes` | −30/+21 d (backend); frontend descarta `<hoy` (`VistaSemanal.tsx:66-73`) | igual al universo |
| Próximas Semanas | `calendario_futuro.py:26-70` | hoy..+20 d | SQL propio, **sin** avance<100 ni exclusión FP-LC (QA-A-02) |
| Materia Prima | `database_cubigest.py:341-375` (`obtener_comprometido_por_codigo`) + `materias_primas.py:239` | −30/+21 d | `Piezas.TotalKgs`, **sin** filtro de avance (QA-A-03) |

`_obtener_pids_pendientes` (`programacion.py:1404-1498`) es `[]` silencioso si Cubigest falla (línea 1498).
No existe campo en Cubigest que marque "en espera de confirmación del cliente"; el catálogo `IT.Estado` no
lo distingue y la tabla `Reprogramar_IT` no tiene un flag para esto (solo texto libre en `MotivoRep`).

## 2. Datos reales (24-09, SELECT acotado, avance<100, ITs PEN/IET/APR/ING, sin ventana de fechas)

| Tramo | Calama (ITs/kg) | Cerrillos (ITs/kg) | Coronel (ITs/kg) |
|---|---|---|---|
| >60 d atrasada ("suciedad") | 127 / 645.k | 1.326 / 6,47M | 122 / 606k |
| 31–60 d atrasada | 0 | 3 / 9k | 0 |
| 8–30 d atrasada | 0 | 0 | 0 |
| 1–7 d atrasada + hoy | 8 / 59k | 1 / 18k | 4 / 5,6k |
| +1..21 d (próxima) | 65 / 527k | 65 / 655k | 8 / 29k |
| +22..60 d (lejana normal) | 13 / 103k | 1 / 18k | 0 |
| +61..120 d | 68 / 308k | 99 / 3,62M | 1 / 11k |
| >+120 d | 14 / 40k | 116 / 353k | 2 / 8k |

- Vacío total entre 8 y 30 días atrasados en las 3 plantas: atrasada válida = 1–30 d, todo lo posterior es
  suciedad (Cerrillos llega a fechas de 2013).
- "Muy futura" no se distingue solo por umbral de días: en Cerrillos, 30 ITs con último motivo de
  reprogramación "Reprogramación del cliente" están fechadas 31-dic-2026; solo la IT 1384 pesa 3,02M kg
  (27% de todo lo pendiente de la planta). En Calama, 46 ITs el 31-dic-2026 con motivo "IT Fuera de
  Programación"; en Cerrillos, 111 ITs el 25-dic-2027 con motivo "Reprogramación del administrador de TO"
  modificadas el 19-nov-2025 (horizonte 761 días). Hay fechas basura (2090, 2099).
- Proxy de "espera de confirmación del cliente" (no hay campo dedicado): horizonte = fecha de despacho −
  fecha de última reprogramación. >120 días de horizonte es el patrón que aparece en los casos anteriores.
- Materia Prima sobreestima frente al universo en la misma ventana −30/+21: Cerrillos 939k vs 673k kg
  (+39%), Calama +13%, Coronel 115k vs 34k kg (3,4×) — falta el filtro de avance (QA-A-03).
- El Cuadro OptiSteel llega solo hasta: Calama 09-oct, Cerrillos 26-sep, Coronel 25-sep (2026).
- **`TOP 2000` de `_obtener_pids_pendientes` ya trunca hoy en Cerrillos** (2.231 filas de 2.000 posibles,
  contadas sin el límite, misma query y ventana −30/+21). Ensanchar la ventana a "lejana" (+60d) sin subir
  el límite empeora el truncamiento silencioso.

## 3. Categorías y umbrales acordados con Montu (24-09)

Días respecto de hoy, sobre la fecha efectiva de despacho (`FechaDespacho` con fallback `FechaEntrega`).

| Categoría | Regla |
|---|---|
| Atrasada válida | 1–30 d atrasada |
| Atrasada "suciedad" | > 30 d atrasada — fuera de toda vista de demanda, con contador visible por planta |
| Próxima | hoy .. +21 d |
| Lejana normal | +22 .. +60 d |
| **Muy futura** | > +60 d **o** (horizonte de reprogramación > 120 d **y** fecha > +21 d) |

La segunda condición evita que una IT como la 1384 de Cerrillos (fecha +98 d, horizonte 381 d) se cuente
como demanda real de materia prima solo porque todavía no cruzó la marca de +60 d.

**Leyenda en UI (todas las secciones de demanda):** *"No considera ITs con fecha de despacho mayor a 60
días (N ITs / X.XXX kg fuera; ver aparte)"*, con N/kg actualizados según la planta y sección. Los casos que
además entran a "muy futura" por la regla de horizonte (≤60 d pero reprogramados con horizonte >120 d) se
listan en la misma línea aparte, con nota en el detalle/tooltip: *"reprogramada por el cliente/TO, fecha
poco confiable"* — no se agregan a la leyenda base para no confundir al jefe de planta con dos criterios
distintos en una sola frase.

## 4. Tratamiento por sección

- **Vista Semanal:** mismas 3 pestañas hoy vigentes, más una línea "Atrasado ≤30 d" (dato ya disponible en
  el backend, hoy descartado por el frontend) y otra "Sin fecha confirmada / muy futura" aparte, con la
  leyenda del punto 3.
- **Próximas Semanas:** mismas 3 semanas; bloque de atrasadas arriba y de muy futuras abajo, con los mismos
  filtros de avance/estado/FP-LC que el universo (corrige QA-A-02, hoy sobreestima frente a Compromisos
  Futuros).
- **Materia Prima:** demanda = atrasada válida + próxima + lejana normal (con filtro de avance, corrige
  QA-A-03). Las muy futuras van en línea aparte "sin fecha confirmada", sin sumar a la necesidad de compra.
- **Compromisos Futuros / Programación:** sobre el Cuadro OptiSteel, sin cambio de ventana (ya filtra por
  lo que el Cuadro trae).
- **Fallo de Cubigest:** error visible en las 4 secciones en vez del `[]` silencioso actual.

## 5. Plan de implementación

**Configuración única propuesta:** módulo nuevo (p.ej. `universo_fechas.py`) con las constantes de umbral
(30, 21, 60, 120) y una función `clasificar_fecha(fecha_despacho, horizonte_reprog) -> categoria` que
reemplace las 3 ventanas `-30d/+21d` hoy duplicadas en `database_cubigest.py:374`, `materias_primas.py:239`
y `programacion.py:1476`.

**Criterios de aceptación medibles:**
- Cerrillos, Materia Prima: demanda con avance<100 y ventana ampliada a +60d = N ITs / X kg (calcular tras
  implementar), con las muy futuras separadas y sumando 0 a la necesidad.
- Próximas Semanas Cerrillos, semana 1 (24–30 sep): kg debe coincidir con Compromisos Futuros para el mismo
  rango (hoy difieren >2×, QA-A-02).
- `TOP 2000` de `_obtener_pids_pendientes`: subir el límite o paginar antes de ampliar la ventana, y agregar
  un log/alerta si la cuenta real supera el límite (hoy sucede en silencio).
- Cubigest caído: las 4 secciones muestran error, no `[]`/0 silencioso.

**Archivos y orden (ya no hay bloqueo por B42 v2 — se integró en `master` como `cc5cf7e`/`f430b75`):**
- Libres para hoy: módulo nuevo de umbrales, `calendario_futuro.py`, `materias_primas.py`,
  `compromisos_semanales.py`, `VistaSemanal.tsx`, `CalendarioFuturo.tsx`.
- `database_cubigest.py` (`obtener_comprometido_por_codigo`) y `programacion.py`
  (`_obtener_pids_pendientes`, `/semanal`): también libres ahora, sin dependencia de otra ventana.
- **Riesgo:** cruza con CCa-17 (Sync unificado, `SYNC_HORARIO_ACTIVO=0`) — el job horario que refresca el
  universo debe usar la misma función de clasificación una vez activado, para no duplicar la ventana una
  cuarta vez.

## 6. Cierre
Umbrales y tratamiento por sección acordados con Montu 24-09 (sección 3 y 4). Sin bloqueo de rama pendiente:
implementación puede partir hoy en los 6 archivos frontend/backend listados, incluyendo los antes
bloqueados por B42 v2 (ya desplegado). Riesgo abierto: `TOP 2000` y el job horario de CCa-17.
