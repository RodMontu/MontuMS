# Análisis — Export OptiSteel (piezas NO variables)
**Fecha de análisis:** 2026-09-06
**Fuente:** `docs/evidencia/Diametros_Totales_06-09-2026.csv` (copiado desde
`~/Downloads/Diametros_Totales_06-09-2026.csv`, export original de Cubigest
vía `DescargarOptistel.aspx`, filtrado por sucursal/semana al momento de
la descarga: dispatch 07-sep al 11-sep-2026)

## 1. Estructura de columnas

CSV delimitado por `;`, con BOM/CRLF (Windows, típico de exports ASP.NET).
743 filas de datos + 1 header. 27 columnas (la última queda vacía por el
`;` final de cada línea).

| # | Columna | Tipo inferido | Significado |
|---|---|---|---|
| 1 | `codigo` | string | Código de obra/pedido (ej. `ASR-244/1`, `CHSA-3/2`). Prefijo parece identificar cliente/proyecto. |
| 2 | `marca` | string | Marca o descripción de la pieza dentro de la obra (ej. `TRABA 1`, `TRABAS e=25`). 331 valores distintos sobre 743 filas — no es categoría cerrada, es texto libre de ingeniería. |
| 3 | `nropiezas` | int | Cantidad de piezas iguales que representa esta fila/tag (no es 1 pieza = 1 fila; es un lote). |
| 4 | `diametro` | int (mm) | Diámetro de la barra. Valores observados: 8,10,12,16,18,22,25,28,32,36. Es el eje de agrupación del reporte ("Diametros_Totales"). |
| 5 | `largo` | int (mm) | Largo teórico de la pieza. |
| 6 | `LargoReal` | int (mm) | Largo real/efectivo. En la muestra coincide siempre con `largo` — posible ajuste de corte que en este export no se activó. |
| 7 | `IdForma` | int | Código de forma de doblado (catálogo interno Cubigest, 31 valores distintos en la muestra). No hay diccionario en este CSV — habría que pedir a Roberto la tabla de formas si se necesita interpretar visualmente. |
| 8 | `Kgs` | decimal | Peso teórico del lote de la fila. |
| 9 | `KgsReales` | decimal | Peso real. Igual a `Kgs` en la muestra (mismo patrón que LargoReal). |
| 10 | `etiqueta` | string | Texto de la etiqueta física impresa, formato `" Tag #:  N  of  M"` — indica que cada fila es UN tag/etiqueta individual dentro de un lote de M tags para ese código+marca. Esta es la evidencia de que el export es a **nivel de tag**, no de obra. |
| 11 | `id` | int (PK) | ID interno Cubigest de la fila/tag (`3589683`, etc.). Único por fila. |
| 12 | `FechaDespacho` | date (dd/mm/aaaa) | Fecha planificada de despacho a obra. Es el campo que la heurística vieja usaba para inferir cuándo debía fabricarse (despacho − 1/2 días). |
| 13 | `diaSemana` | string | Día de la semana en español, redundante con `FechaDespacho` (se puede derivar). Útil para vistas de Gantt sin recalcular. |
| 14 | `Producido` | bool (0/1) | **Campo clave.** 1 = la pieza YA fue fabricada; no debe planificarse ni mostrarse pendiente en el Gantt. 0 = pendiente de fabricar. |
| 15 | `FechaProduccion` | date (dd/mm/aaaa), nullable | Fecha real en que se fabricó. Vacío si `Producido=0`. |
| 16 | `HoraProduccion` | time (HH:MM:SS), nullable | Hora exacta de fabricación. |
| 17 | `ProducidoEn` | string, nullable | Máquina/línea donde se fabricó. Valores observados: `COIL 14`, `COIL 14 M`, `Carro de Corte`, `Dobladoras`, `Eura 16`, `Robomaster 60`. Es el dato que permitiría cruzar con el Motor de Tiempos por máquina. |
| 18 | `ProducidoPor` | string, nullable | Usuario/operario que registró la producción (ej. `rcolumba`, `dlopez`). |
| 19 | `FechaDespacho1` | date, nullable | **Vacío en el 100% de las 743 filas de esta muestra.** Presumiblemente se llena cuando existe guía de despacho INET real (columna hermana de `NroGuiaInet`/`HoraDespacho`), distinta de `FechaDespacho` (planificada). No hay evidencia en esta muestra de que se use — confirmar con Roberto si aplica solo post-despacho real. |
| 20 | `HoraDespacho` | time, nullable | Vacío en toda la muestra. Mismo comentario que `FechaDespacho1`. |
| 21 | `NroGuiaInet` | string/int, nullable | Vacío en toda la muestra. Número de guía de despacho INET una vez emitida. |
| 22 | `EsFactorCorreccion` | string (N/S?) | Constante `N` en las 743 filas. Bandera de si el peso/largo fue corregido por factor — no se activó en esta muestra. |
| 23 | `TipoGuiaINET` | string | Constante `Facturable` en las 743 filas. Sugiere que este export solo trae piezas facturables (consistente con "piezas NO variables" del enunciado del punto B1). |
| 24 | `tipoAcero` | string | Constante `A630-420H` en las 743 filas — esta descarga es de un solo tipo de acero; no asumir que el campo sea siempre constante en otros exports. |
| 25 | `prioridad` | int | Constante `0` en las 743 filas. **Relevante para B7** (pendiente "confirmar con Roberto lectura de columna prioridad Cubigest"): en este export la columna está presente pero sin uso real (todo 0) — no sirve como evidencia de que el campo esté poblado en producción real; hay que revisar con Roberto si se llena en otras vistas/exports. |
| 26 | `Teorico_Menos1%` | decimal | Kgs teórico con descuento de 1% (probable ajuste de merma de proceso). Igual o muy cercano a `Kgs` en la muestra. |
| 27 | *(vacía)* | — | Artefacto del `;` final de cada línea, ignorar. |

## 2. `Producido=1` vs. la heurística vieja de "despacho −1/2 días"

La heurística anterior asumía que una pieza se fabrica genéricamente 1 o 2
días antes de su `FechaDespacho`, sin verificar si realmente ya se
fabricó. Esto genera dos tipos de error:

- **Falso pendiente**: una pieza ya producida (a veces con semanas de
  anticipación, ver fila `ASR-243/1` con `FechaProduccion=02/09/2026` para
  un despacho `10/09/2026`, 8 días antes) seguía apareciendo en el Gantt
  como si faltara fabricar.
- **Falso urgente/false negative de replanificación**: si la producción
  real se atrasa respecto al offset de 1-2 días asumido, el sistema no lo
  detecta porque nunca compara contra la realidad, solo contra la fecha
  de despacho.

El campo `Producido` (con `FechaProduccion`, `HoraProduccion`,
`ProducidoEn`, `ProducidoPor`) es un hecho registrado en Cubigest al
momento real de fabricación, no una proyección. Reemplaza la heurística
con una fuente de verdad binaria y auditable: si `Producido=1`, la fila
se excluye del Gantt de pendientes sin importar cuán lejos esté la
`FechaDespacho`; si `Producido=0`, se planifica usando `FechaDespacho`
(y opcionalmente `prioridad`, aunque ver limitación arriba) como antes.

## 3. Nivel de detalle: este export (tag) vs. `CuadroProgramacionPr.aspx` (resumen semanal por obra)

- **Este export (`DescargarOptistel.aspx`)**: una fila = **un tag físico
  individual** dentro de un lote (`etiqueta = "Tag #: N of M"`), con su
  propio `id`, su propio estado `Producido` y su propia máquina
  `ProducidoEn`. Es el nivel de granularidad que necesita el piso de
  planta (qué tag específico falta, en qué máquina se hizo cada uno).
- **`CuadroProgramacionPr.aspx`** (visto previamente, resumen semanal por
  obra): agrega por obra/semana — probablemente suma `nropiezas`/`Kgs` de
  todos los tags de un `codigo` para una semana, sin exponer el detalle
  de qué tags puntuales ya se hicieron. Es la vista gerencial ("¿cuánto
  falta de esta obra esta semana?"), no la operativa ("¿qué tag imprimo
  ahora?").
- Implicación de diseño: **no se puede reconstruir el nivel de tag a
  partir del resumen semanal**, pero sí se puede derivar el resumen
  semanal agregando este export por `codigo` + semana de `FechaDespacho`.
  Si OF V2 necesita ambas vistas, este export a nivel de tag es la fuente
  primaria; el resumen semanal debería calcularse localmente a partir de
  él, no consumirse como export separado (evita que las dos vistas
  queden inconsistentes entre sí).

## 4. Propuesta de diseño — ingesta a OptiFierro V2 (a discutir con Montu)

**Nota:** esto es una propuesta, no una decisión ni una ejecución. No se
corrió ninguna query contra Cubigest para este análisis — todo lo anterior
sale de leer el CSV ya descargado manualmente por Montu.

Opciones evaluadas:

1. **Import manual de CSV diario/por turno** (más simple, cero riesgo de
   tocar Cubigest en caliente): alguien descarga desde
   `DescargarOptistel.aspx` con el filtro de sucursal/semana vigente y lo
   sube a OF V2, que lo parsea y actualiza el estado `Producido` por
   `id`. Costo: depende de que un humano recuerde descargar y subir el
   archivo con la frecuencia correcta (¿cada turno? ¿cada mañana?
   relacionado directamente con el pendiente A11 de cadencia de
   `turnos_programados`, que tiene el mismo problema de frecuencia).
2. **Vista SQL equivalente en Cubigest, consultada por Carlitos**: si
   `DescargarOptistel.aspx` internamente corre una query/vista fija, en
   teoría existe una vista o stored procedure en el SQL Server de
   Cubigest (`192.168.1.195`) que se podría consultar directo — pero
   **no se ha identificado cuál es** (no se inspeccionó el backend de
   `DescargarOptistel.aspx`, ni se debe hacerlo sin autorización). Si se
   opta por este camino, aplican las reglas ya vigentes: **solo Carlitos
   toca Cubigest, solo lectura, solo `SELECT`, ejecutado desde TO vía SSH
   (nunca directo desde el Mac), reutilizando las credenciales que ya usa
   `optifierro-backend`** — ninguna conexión nueva sin pasar primero por
   Montu.
3. **Híbrido**: import manual como puente de corto plazo mientras se
   identifica (con Roberto, no unilateralmente) si existe una vista
   segura y estable que Carlitos pueda leer con la cadencia que se
   decida para A11/A4.

Recomendación tentativa (a validar con Montu): empezar con la opción 1
(import manual) para no tocar Cubigest mientras B1 sigue en estado
"Investigar", y evaluar la opción 2 solo si el volumen/frecuencia de
descargas manuales se vuelve un cuello de botella operativo.

## 5. Observaciones (patrones en el CSV analizado)

- **Distribución global `Producido`**: 373 filas con `Producido=1` (50.2%)
  vs. 370 con `Producido=0` (49.8%) sobre 743 filas totales — export
  tomado a mitad de semana, con la producción de esa semana aprox. a la
  mitad.
- **`Producido` correlaciona fuerte con cercanía de `FechaDespacho`** (el
  export es del 06-sep-2026):
  - `07/09` (mañana): 171/206 producidas (83%)
  - `08/09`: 143/213 producidas (67%)
  - `09/09`: 0/59 producidas (0%) — **anomalía a confirmar con Roberto**:
    ninguna de las 59 piezas con despacho 09-sep está producida aún,
    corte abrupto respecto al patrón decreciente de los otros días (podría
    ser feriado/parada de planta ese día, o simplemente que se saltó de
    producir por prioridad de otras obras — no se puede determinar solo
    con este CSV).
  - `10/09`: 28/159 producidas (18%)
  - `11/09`: 31/106 producidas (29%) — leve repunte respecto a 10/09, sin
    explicación evidente en los datos disponibles.
  - Patrón general (fuera de la anomalía del 09/09): a mayor cercanía del
    despacho, mayor proporción ya producida, consistente con producción
    "justo a tiempo" y validando que `Producido` es más confiable que un
    offset fijo de días.
- **Piezas vencidas con `Producido=0`**: no aplica en esta muestra — el
  rango de `FechaDespacho` va del 07-sep al 11-sep-2026, todas fechas
  futuras respecto al 06-sep-2026 (fecha del export). No hay piezas con
  despacho ya pasado y sin producir en este corte puntual. Repetir esta
  verificación en exports futuros, especialmente si `FechaDespacho` queda
  en el pasado y `Producido` sigue en 0 — esa combinación sí sería una
  señal de atraso real de producción.
- **Campos siempre constantes en esta muestra** (posibles falsos
  positivos de "campo fijo" si solo se mira este export): `EsFactorCorreccion=N`,
  `TipoGuiaINET=Facturable`, `tipoAcero=A630-420H`, `prioridad=0`,
  `FechaDespacho1`/`HoraDespacho`/`NroGuiaInet` siempre vacíos. No asumir
  que estos campos son inútiles en general — esta descarga filtra por un
  solo tipo de acero y por piezas aún no despachadas físicamente (de ahí
  que la guía INET esté vacía); podrían variar en otros filtros/exports.
- **`largo` = `LargoReal` y `Kgs` = `KgsReales`** en el 100% de la
  muestra — sin casos de corrección real vs. teórico en este corte.
- **331 marcas distintas / 743 filas**: alta variedad de piezas por
  obra, consistente con que este es el nivel de detalle de fabricación
  (tags), no un agregado.
