# CCa-34 — F5: Vista Semanal replicando el Cuadro de Programación de Cubigest ("Fierro Preparado")

Rama `ola1-f5`, worktree `C:/Users/OptiFierro/Desktop/optifierro_f5`, base `c818ff6` (HEAD de
`cajita-viaje-deploy` verificado idéntico al desplegado). 4 commits locales, sin push, sin tocar el
checkout principal ni los contenedores desplegados.

```
86aed96 fix(frontend): reemplaza panel Fuera de ventana por una nota discreta en Vista Semanal (CCa-34 F5)
6c6402d fix(vista-semanal): obtener_proyeccion_semanal lee delgado/grueso/total de cuadro_resumen_semanal (Fierro Preparado) en vez de SQL directo a Cubigest (CCa-34 F5)
fa26c87 feat(sync): llama a sincronizar_resumen_semanal desde el job de sync del Cuadro (CCa-34 F5)
7635967 feat(cuadro): nuevo modulo cuadro_resumen.py - parser del resumen Fierro Preparado/Largo Comercial de CuadroProgramacionPr.aspx (CCa-34 F5)
```

`git diff --stat` (c818ff6..HEAD):
```
backend/cuadro_resumen.py                       | 205 ++++++++++++++++++++++++
backend/main.py                                 |   5 +
backend/routers/programacion.py                 |  71 ++++----
backend/test_cuadro_resumen.py                  | 158 ++++++++++++++++++
frontend/src/components/domain/VistaSemanal.tsx |  52 ++----
5 files changed, 426 insertions(+), 65 deletions(-)
```

## 1. Investigación (solo lectura) — ¿viene el bloque resumen en el HTML?

Con sesión real contra Cubigest (login reutilizado de `scraper_cuadroprogramacion._login`, misma query
que ya hace el sync cada 30 min — autorizada), pedí `CuadroProgramacionPr.aspx` para CORONEL, semana
05-10..11-10-2026. **El bloque SÍ viene en el HTML de la respuesta del POST final** (no se arma por
postback/JS aparte): dos tablas internas `Gr_ResumenSem` ("Fierro Preparado", columnas Diam≤16/Diam>16)
y `Gr_ResumenSemFE` ("Fierro Punta largo Comercial", columnas Diam≤18/Diam>18), cada una con 6 filas
(Lunes..Sábado) + fila Totales.

**Tabla referencia (Montu) vs HTML real extraído — coincide exacto, kg a kg:**

| Día | Preparado ≤16 / >16 / Total (referencia) | Preparado ≤16/>16/Total (HTML Cubigest) | Largo Com. ≤18/>18/Total (ref.) | Largo Com. (HTML) |
|---|---|---|---|---|
| Lun 05-10 | 6.221 / 4.247 / 10.468 | 6.221 / 4.247 / 10.468 | 0 / 32.320 / 32.320 | 0 / 32.320 / 32.320 |
| Mar 06-10 | 622 / 4.110 / 4.732 | 622 / 4.110 / 4.732 | 10.100 / 30.300 / 40.400 | 10.100 / 30.300 / 40.400 |
| Mié 07-10 | 96 / 0 / 96 | 96 / 0 / 96 | 0 / 0 / 0 | 0 / 0 / 0 |
| Jue 08-10 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| Vie 09-10 | 8.239 / 41.356 / 49.595 | 8.239 / 41.356 / 49.595 | 0 / 0 / 0 | 0 / 0 / 0 |
| Sáb 10-10 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 |
| **Totales** | 15.178 / 49.713 / **64.891** | 15.178 / 49.713 / **64.891** | 10.100 / 62.620 / **72.720** | 10.100 / 62.620 / **72.720** |

Coincidencia exacta (0 kg de diferencia) en los 7 días/totales de ambos bloques. Implementé la ruta (a)
del encargo: parsear y persistir, no reconstruir desde `cuadro_programacion_optisteel`.

**Hallazgo importante no anticipado en la tarea**: `Gr_ResumenSem`/`Gr_ResumenSemFE` agregan por
**nombre** de día de semana sobre **todo** el rango de fechas consultado, no por fecha real. Verificado
pidiendo un rango de 3 semanas (05-10..25-10) para Coronel: la fila "Jueves" cambió de `0/0/0` a
`21.080/6.941/28.021` y "Viernes" de `8.239/41.356/49.595` a `19.278/45.933/65.211` — mezclando los
jueves/viernes de varias semanas en una sola fila. Por eso `cuadro_resumen.py` pide **una semana exacta
por llamada** (lunes-sábado, igual criterio que `scraper_cuadroprogramacion._rango_semana_actual`) y
traduce cada nombre de día a la fecha calendario de *esa* semana específica — nunca pide un rango
multi-semana al bloque resumen.

## 2. Implementación

- **`backend/cuadro_resumen.py` (nuevo)**: `_obtener_resumen_semana(sucursal_nombre, lunes)` repite el
  patrón login/VIEWSTATE/postback de `scraper_cuadroprogramacion.scrape_cuadro_programacion` (reusa sus
  helpers privados `_login`/`_gv`/`BASE` por import, sin modificar ese archivo) y parsea ambos grids con
  `_parsear_grid`. `sincronizar_resumen_semanal(sucursales=None, semanas=3)` recorre 3 semanas
  (Actual/Próxima/Subsiguiente, UNI-02) × 3 sucursales y hace upsert en la tabla nueva
  `cuadro_resumen_semanal` (`sucursal_id, fecha, prep_delgado/grueso/total, lc_delgado/grueso/total,
  fecha_carga`, `UNIQUE(sucursal_id, fecha)`, `CREATE TABLE IF NOT EXISTS` igual patrón que
  `importar_optisteel.py:123-126`). Nunca lanza: cada combinación sucursal×semana que falle queda
  registrada con su propio error en el `detalle` devuelto, sin tumbar las demás ni el job que la llama.
- **`backend/main.py`**: una sola línea nueva (`await run_in_threadpool(_sincronizar_resumen_cuadro)`,
  más los 2 imports del bloque) dentro de `_job_sync_horario`, después de `_ejecutar_sync_horario()` y
  dentro del mismo `try` — si falla, el `except Exception` ya existente lo absorbe y lo deja en el log,
  sin afectar el resto del sync horario (universo + Cuadro de detalle, que siguen intactos).
- **`backend/routers/programacion.py`**: nueva función auxiliar `_obtener_resumen_cuadro_por_fecha(sid)`
  (con su propio `CREATE TABLE IF NOT EXISTS` defensivo, por si corre antes de cualquier sync). Dentro de
  `obtener_proyeccion_semanal`, `data[str(sid)]` ahora se llena **siempre** desde esa función (no depende
  de que la consulta en vivo a Cubigest funcione); el resto de la función (`top_viajes`,
  `resumen_categorias`, manejo de `errores`) sigue exactamente igual, derivando de
  `_obtener_pids_pendientes` tal cual estaba — **no se tocó ni se usó esa función para los totales**, tal
  como pedía la tarea. `_obtener_pendientes_bolsa_optisteel`/el adelanto/Materia Prima/Próximas
  Semanas/Compromisos Futuros no se tocaron.
- **`frontend/VistaSemanal.tsx`**: el panel "Fuera de ventana" (título + card con las 2 líneas +
  leyenda) se reemplazó por un único párrafo de 2 líneas con ícono `AlertTriangle` chico, mismo texto que
  antes (Atrasado ≤30 días + Sin fecha confirmada/muy futura + leyenda UNI-04), debajo de "Resumen
  {semana}". Mismo comportamiento ante error/falta de dato: si `data.errores[sucId]` existe o no hay
  `resumen_categorias[sucId]`, la nota simplemente no se renderiza (antes mostraba una card de error o un
  "Sin datos..."; ahora se omite sin avisar, consistente con "nota discreta" y con que esto no bloquee el
  resto de la tarjeta). No se tocó nada del resto del diseño/colores/distribución.

## 3. Decisiones tomadas (no explícitas en la tarea, marcadas para que Miaude/Montu las revisen)

1. **3 semanas, no solo la actual**: el Cuadro de detalle (`cuadro_programacion_optisteel`) y su sync
   horario solo cubren "semana actual". Pero `VistaSemanal.tsx` tiene pestañas Actual/Próxima/Subsiguiente
   (UNI-02, +21 días) que antes sí traían datos (de Cubigest en vivo, aunque descuadrados). Para no dejar
   esas 2 pestañas en blanco, `sincronizar_resumen_semanal` pide 3 semanas propias (parámetro `semanas=3`),
   independiente del rango que usa el Cuadro de detalle — no modifiqué `_rango_semana_actual` de
   `routers/sync.py` (no estaba en mi alcance). **Costo**: cada corrida del job de sync horario (cada 30
   min, 6-22h) ahora hace 9 logins+scrapes adicionales a Cubigest (3 sucursales × 3 semanas) solo para el
   resumen, además de los 3 que ya hacía el Cuadro de detalle. No medí el tiempo real contra el Cubigest
   productivo (solo contra el espejo de pruebas); si 9 scrapes adicionales cada 30 min resultan pesados
   para el ERP, la mitigación más simple es bajar `semanas` a 1 (solo Actual) o espaciar el job — **no
   verificado, queda para que Montu/Miaude decidan con visibilidad del ERP real**.
2. **Fierro Preparado y Largo Comercial se guardan ambos** en `cuadro_resumen_semanal` (aunque Largo
   Comercial no se usa todavía en la Vista Semanal) para no tener que volver a tocar el parser/la tabla si
   más adelante se pide mostrarlo aparte — el propio encargo dice "lo dejaría aparte", no "lo descartes".
3. El `top_viajes` y `resumen_categorias` (nota) siguen 100% dependientes de Cubigest en vivo
   (`_obtener_pids_pendientes`), como pedía la tarea — por lo tanto pueden seguir descuadrados o fallar
   igual que antes; eso es independiente de este cambio y no estaba en el alcance de F5.

## 4. Verificación

**Tests nuevos** (`backend/test_cuadro_resumen.py`, 7 tests) — HTML fijo con los mismos valores de la
tabla de referencia de arriba:
```
test_parsea_fierro_preparado_excluye_totales ... ok
test_parsea_largo_comercial_distinto_de_preparado ... ok
test_tabla_inexistente_lanza ... ok
test_parse_kg_formato_espanol ... ok
test_lee_solo_fierro_preparado_por_fecha ... ok   (confirma 15.178/49.713/64.891 exacto y que lc_* no se filtra al total)
test_otra_sucursal_sin_datos_devuelve_lista_vacia ... ok
test_upsert_reemplaza_valores_de_corrida_anterior ... ok

Ran 7 tests in 0.057s — OK
```

**Regresión** — suites existentes relevantes, mismo método que `CCa_cajita_viaje_20260929.md` (Python del
host TO dentro de `optifierro-backend`, copia del worktree + copia de solo-lectura de
`optifierro_v2.db` real para que los tests que leen `maquinas_info` tengan datos):
```
python3 -m unittest test_migracion_scraper_optisteel test_adelanto_automatico test_sync_unificado test_universo_fechas test_cajita_viaje
Ran 48 tests in 3.228s — OK (skipped=4)
```

**Frontend**: `npx tsc --noEmit` limpio antes y después del cambio (sin errores, mismo `package-lock.json`
que el checkout principal; `node_modules` se instaló con `npm ci --prefer-offline` en el worktree, no se
tocó el `node_modules` del checkout principal).

**NO VERIFICADO**:
- No ejecuté `sincronizar_resumen_semanal` de punta a punta contra el Cubigest productivo dentro del
  contenedor desplegado (solo contra una copia del backend en `/tmp` dentro del mismo contenedor, con las
  llamadas HTTP reales a Cubigest pero sin escribir en `/app/optifierro_v2.db` real) — por la regla
  cardinal de no tocar el SQLite de producción fuera de mi worktree de pruebas. El HTML real sí se
  descargó end-to-end (sección 1) y el parser se probó contra ese HTML exacto.
- No medí el impacto en tiempo/carga de Cubigest de las 9 llamadas adicionales por corrida (decisión #1
  arriba).
- No probé el render visual de la nota en el navegador (sin acceso a UI en esta sesión) — solo `tsc
  --noEmit` y lectura del JSX resultante.

## 5. Archivos compartidos tocados

`backend/routers/programacion.py`: **solo** `obtener_proyeccion_semanal` y la función auxiliar nueva
`_obtener_resumen_cuadro_por_fecha` (añadida inmediatamente antes). No se tocó ninguna otra función del
archivo. `backend/main.py`: una sola línea de llamada + 2 imports, dentro del bloque ya existente
`if SYNC_HORARIO_ACTIVO`. No se tocó `motor_v2.py`, `GestorProgramacion.tsx`, `_obtener_pids_pendientes`,
`routers/sync.py`, `scraper_cuadroprogramacion.py`, ni Materia Prima/Próximas Semanas/Compromisos Futuros.
