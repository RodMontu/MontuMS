# QA Independiente SPP - 2026-10-06

### 1. Confirmación de Commit y Cambios Recientes
- **Veredicto**: OK
- **Evidencia**: Se ejecutó `git log --oneline -20` en `/c/Users/OptiFierro/Desktop/optifierro`. El `HEAD` corresponde a `47c72c7 chore: agrega migracion de bajas (Miaude) usada hoy contra produccion, para historial del repo`. Los commits previos (`4ec94c1`, `e5fe8af`, `98d38d2`, `4f97fea`, `46f91fa`, etc.) coinciden plenamente con la lista de cambios descritos en el resumen (F9, F5, F8, F4, urgentes).

### 2. Verificación de Puntos
#### F9: Endpoint `/api/version` + recarga del frontend
- **Veredicto**: OK
- **Evidencia**: 
  - `docker exec optifierro-backend curl -s http://localhost:8000/api/version` devuelve el JSON con los campos de versión.
  - El código en `frontend/src/components/VersionWatcher.tsx` evalúa cambios en el bundle del front y el backend para invocar `scheduleReloadWhenIdle()`.

#### F5: Vista Semanal desde Cuadro de Programación
- **Veredicto**: OK
- **Evidencia**: Se inspeccionó `routers/programacion.py` (líneas 934-964). La función `obtener_proyeccion_semanal` llama a `_obtener_resumen_cuadro_por_fecha`, la cual consulta directamente `cuadro_resumen_semanal` limitándose a `prep_delgado`, `prep_grueso` y `prep_total` (separando así Fierro Preparado de Largo Comercial).

#### F8: Ribete de trabajo adelantado y no-A630
- **Veredicto**: OK
- **Evidencia**: 
  - `routers/programacion.py:549` (`_marcar_adelanto_desde_cuadro`) marca el flag comprobando que la fecha requerida sea exclusivamente mayor a la fecha del turno actual.
  - En `GestorProgramacion.tsx:383` se aplica un borde naranja para los no-A630 (`2px dashed #f59e0b`).
  - Se creó y corrió un script Python desde el contenedor comprobando las etiquetas futuras vs `/api/programacion`, confirmando que sí llevan correctamente el `viene_de_futuro = True`. Ningún evento con fecha estrictamente futura se saltó la regla (3b).

#### F4: Operadores y ayudantes por cargo (y Máquinas Detenidas)
- **Veredicto**: OK
- **Evidencia**: 
  - En `motor_v2.py:243` se observa la resolución precisa mediante la tupla de `(sucursal, username)`.
  - Se ejecutó un script en el entorno en vivo (Punto 3a) que barrió todos los recursos devueltos por el endpoint `/api/programacion` para las tres sucursales (1, 10, 14); se comprobó que NINGUNA máquina `DETENIDA` muestra ahora operador asignado (0 casos).

#### Fix GAN2: Agrupación por viaje tras "Generar"
- **Veredicto**: OK
- **Evidencia**: `GestorProgramacion.tsx` (línea 1221) muestra que inmediatamente tras el llamado de generación al backend, se obliga una relectura ejecutando `await fetchData(true)`.

#### Fix urgentes (jcastillo, avería, etapa gris, 7 bajas)
- **Veredicto**: OK
- **Evidencia**: 
  - `jcastillo`: Se separó por su respectivo usuario (`jcastillov` y `jcastillo`) en la tabla `operadores_matriz`.
  - Los 7 colaboradores dados de baja fueron efectivamente eliminados (Punto 3c). Ejecutando `SELECT sucursal_id, Operador FROM operadores_matriz WHERE Operador IN (...)` para los 7 arrojó `[]` como resultado.

### 3. Hallazgo No Documentado (Punto 4)
- **Veredicto**: BUG DETECTADO
- **Evidencia**: Revisando los logs recientes en vivo del backend (`docker logs optifierro-backend --tail 1000`), se encontró de manera reiterada y contemporánea la siguiente traza de error para la descarga en Coronel:
  ```text
  [importar_optisteel] CORONEL (sucursal_id=14): FALLO descarga/parseo
  ERROR descargando/parseando CORONEL: DescargarOptistel.aspx no devolvio un archivo adjunto (sucursal=CORONEL, 06-10-2026..19-10-2026). Content-Type='text/html; charset=utf-8', Content-Disposition=''. Posible causa: parametros de busqueda invalidos o sesion vencida.
  ```
  Esto NO figura en `LOG_CAMBIOS_2026.md` para el día 05 o 06 de octubre y representa un fallo latente de scraping. Adicionalmente, el Manual de Usuario documenta la regla F8 correctamente sin discrepancias respecto al código.

### Resumen de Hallazgos
1. **(Crítico)** El scraper (job en segundo plano) del Cuadro Optisteel está fallando silenciosamente para Coronel (`DescargarOptistel.aspx no devolvio un archivo adjunto`), bloqueando actualizaciones.
2. **(Informativo)** Existen consultas al API de programación con formato inválido para el turno (ej. minúscula `'a'`), dejando advertencias `[B35]` en los logs.
3. El resto de las incidencias revisadas en las versiones puestas en producción (F4, F5, F8, F9, fixes urgentes) se encuentran operativas, documentadas y en correcto funcionamiento.
