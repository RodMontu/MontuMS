
---
# TAREA CCa-40 — Scraper de detalle OptiSteel falla SOLO para CORONEL (DescargarOptistel.aspx)
TAG: `coronel-scraper` (rama `fix-coronel-scraper`, directorio `optifierro_coronel`). Informe:
`docs/agentes/CCa40_coronel_scraper_20261008.md`. Repo: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>".

## OBLIGATORIO antes de tocar nada (no se salto esta vez)
Miaude ya consulto Graphify (grafo puede estar algo desactualizado respecto al HEAD actual; tratarlo como
orientativo) para `scraper_optisteel.py` e `importar_optisteel.py`:
- `scraper_optisteel.py`: SIN dependientes fuera del par -- archivo aislado, bajo riesgo de romper otra cosa.
- `importar_optisteel.py`: lo usan `main.py` (confirma que SI esta programado, pese a lo que dice su propio
  docstring -- ver punto 5 abajo), `database_cubigest.py` (probablemente solo por `parse_numero_y_total_etiqueta`,
  verifica que no sea mas que eso) y su propio test `test_migracion_scraper_optisteel.py`. Nadie mas se ve afectado.
Tras CUALQUIER modificacion real de codigo, es OBLIGATORIO avisarle a Miaude para que regenere el grafo antes de
cerrar la tarea -- no lo regeneres tu mismo.

## Sintoma (confirmado en vivo por Miaude, 08-10-2026, con la contraseña de Cubigest ya renovada)
```
io.ejecutar_importacion() ->
  CALAMA (1): OK, 1763 filas
  SANTIAGO/Cerrillos (10): OK, 3672 filas
  CORONEL (14): ERROR descargando/parseando CORONEL: DescargarOptistel.aspx no devolvio un
  archivo adjunto (sucursal=CORONEL, 07-10-2026..20-10-2026). Content-Type='text/html;
  charset=utf-8', Content-Disposition=''. Posible causa: parametros de busqueda invalidos o
  sesion vencida.
```
Confirmado que NO es el password de Cubigest (ya se renovo y Calama/Santiago cargan bien con la
misma cuenta). El Cuadro de Programacion de Coronel (`scraper_cuadroprogramacion.py`, tabla
`cuadro_programacion_optisteel`) SI esta sano y actualizado -- este bug es especifico de
`scraper_optisteel.py` (el detalle por etiqueta), no de todo Cubigest ni de toda la conexion.
Lleva fallando en CADA ciclo desde antes del corte de VPN del 06/07-10 (no es nuevo de hoy).

## Que investigar
1. `scraper_optisteel.py` hace login + 3 pasos de postback ASP.NET (`__EVENTTARGET=Cmb_sucursal`,
   luego 2 POST mas) reutilizando "tal cual" el patron de `scraper_cuadroprogramacion.py` (que SI
   funciona para Coronel). Compara ambos scripts linea por linea: que es literalmente IDENTICO y
   que es DISTINTO entre ambos (headers, nombres de campos del postback, manejo de VIEWSTATE,
   valor exacto de `Cmb_sucursal` para Coronel en cada uno).
2. Instrumenta (en tu worktree, solo lectura hacia Cubigest, sin escribir en la BD real) para
   volcar a un archivo la respuesta HTML cruda de cada paso (`r3`, `r4`, `r5`, `r6`) cuando
   `suc='CORONEL'`, y compara contra la respuesta de un `suc` que si funciona. Busca
   especificamente: un mensaje de error visible en el HTML, un campo oculto adicional que solo
   aparece para Coronel (por ejemplo un sub-selector de linea/maquina, dado que Coronel es la
   planta con mas maquinas de las 3), o un VIEWSTATE que no se esta reenviando correctamente entre
   pasos.
3. Verifica si el valor literal de `Cmb_sucursal` para Coronel (revisa el diccionario de valores
   cerca de la linea 21 de `scraper_optisteel.py`) es efectivamente el que la pagina usa HOY (pudo
   cambiar del lado de Cubigest, aunque no hay otra evidencia de que Cubigest cambiara algo).
4. Corrige la causa raiz que encuentres con evidencia (no agregues reintentos ciegos ni ajustes de
   timeout sin haber visto el porque real en el HTML). Si tras una investigacion genuina no logras
   identificar la causa exacta, documenta en detalle lo que viste (los 4 HTML volcados, diffeados)
   y NO inventes un fix a ciegas -- entrega el diagnostico para que Miaude decida el siguiente paso.
5. Nota aparte, no relacionada al bug: el docstring de `importar_optisteel.py` dice "NO esta wireado
   a main.py ni a ningun router" pero esta corriendo cada hora en produccion (se ve en los logs del
   contenedor). Encuentra donde esta efectivamente programado (probablemente un job en `main.py`
   agregado despues de escrito ese docstring) y corrige el docstring para que no engañe a nadie mas.
6. Test de regresion que cubra el caso Coronel especificamente (con el HTML real capturado como
   fixture, sin pegarlo igual si es muy largo -- guarda el fixture en un archivo aparte).

## Reglas
- Lectura hacia Cubigest esta autorizada (es el mismo scraper de siempre, de solo lectura de su
  lado). CERO escrituras a `trabajos_optisteel` de la BD real durante tus pruebas -- usa una copia
  (`cp /c/Users/OptiFierro/Desktop/optifierro/backend/optifierro_v2.db ./` en tu worktree) o un
  archivo de BD nuevo para probar `ejecutar_importacion`.
- Commits locales en tu rama, sin push, sin build/deploy ni restart de contenedores -- eso lo hace
  Miaude tras revisar.
- `npx tsc` no aplica (es solo backend). Corre los tests existentes relevantes
  (`test_migracion_scraper_optisteel.py` si sigue vigente) contra una copia de la BD.

## NO HAGAS
No toques `scraper_cuadroprogramacion.py` (funciona bien, no es parte de este bug). No toques
`database_cubigest.py` ni nada relacionado a la conexion SQL directa (ya resuelto hoy, aparte). No
agregues reintentos/sleeps como solucion sin haber visto la causa real en el HTML. No hagas commit
de ningun archivo HTML/CSV con datos reales de produccion si contiene informacion sensible mas alla
de lo tecnico necesario para el diagnostico (si el HTML trae datos de clientes/obras, recortalo al
fragmento relevante del formulario, no el documento completo).
