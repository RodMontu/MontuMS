# CCa-9 — Ola 3 / Carril Averías — B39: estado real de máquinas (Cubigest)

**Fecha:** 2026-09-23 | **Rama:** `ola3-averias` (worktree `optifierro_av` en TO, base `4325640`) | **Commit:** `4e7011b`

## 1. Mapa del flujo actual (antes de tocar código)

`motor_v2.py::programar_turno` (bloque ~l.844-899) ya combinaba 3 fuentes en este orden:

1. **SQLite `averias` (primario)** — último registro por `maquina_nombre` y `sucursal_id`. Si la conexión SQLite funciona (`_sqlite_ok=True`), esta es la única fuente que decide `detenida` / `no-liberada` / `semi`.
2. **Cubigest `MAQUINA.MAQ_ACTIVA='N'`** — se fusiona SIEMPRE (independiente de si SQLite funcionó), vía `_maquinas_inactivas_cubigest()`. Esto es un flag de maestro (máquina dada de baja), no una avería puntual.
3. **Cubigest `NotificacionAveria` (fallback)** — solo se consulta si `_sqlite_ok=False` (SQLite no disponible). Nunca se usa como fuente concurrente cuando SQLite responde.

Es decir: la arquitectura para leer avería en tiempo real desde Cubigest **ya existía** (`database_cubigest.py::obtener_estado_maquinas`, cacheada 15 min); B39 no partía de cero, a diferencia de lo que sugería el pendiente original.

**¿Por qué la Línea de Corte de Coronel figuraba disponible desde el 24-08?**
No es un bug de lectura de fuente equivocada. Es un vacío de registro manual: el SQLite `averias` (única fuente real para Coronel, ver punto 2) no tuvo ningún registro de "Linea Corte Coronel" en estado `detenida` hasta el **2026-09-22** (confirmado con `SELECT ... FROM averias ORDER BY id DESC`). Cubigest nunca pudo haber corregido esto porque, como muestra el punto 2, Cubigest no tiene ningún dato de avería para Coronel.

## 2. Datos reales (solo lectura, hoy 23-09) — conteos por planta

Consulta directa vía `docker exec` en `optifierro-backend` (contenedor desplegado), usando `cubigest_db` con las credenciales ya configuradas (sin credenciales nuevas):

| Sucursal (SQLite → Cubigest) | Notificaciones históricas en Cubigest | Última notificación | DET/SEMI reales (no test) |
|---|---|---|---|
| Calama (1 → 1) | 2.482 | 2026-09-16 | 0 |
| Cerrillos (10 → 4) | 3.489 | **2026-08-24** (se detuvo) | 0 (solo "PRUEBAS DE TI", máquina de pruebas, no de producción) |
| Coronel (14 → 14) | **0** | nunca | 0 |

Hallazgo crítico: **la fuente de datos de Cubigest para Cerrillos dejó de recibir notificaciones el 24-08-2026** (mismo mes del compromiso con Remiz/José Auger) y **Coronel jamás tuvo un solo registro** en `NotificacionAveria`. La única señal de "problema" que aparece en Cubigest en ese rango es la máquina **"PRUEBAS DE TI"** (Cerrillos, `MAQ_ID`=10, no forma parte del catálogo de máquinas activas ni de SQLite `maquinas_info`), con `EstadoMaq='DET'` desde 2026-08-24 21:27, **`FechaSolucion` = NULL (nunca se cerró)**.

Nota aparte (landmine para futuros agentes): Cubigest tiene también un `IdSucursal=10` propio (30 notificaciones, distinto de "Cerrillos"), que **no** corresponde al Cerrillos del SPP (Cerrillos en Cubigest es `IdSucursal=4`, per `_maquinas_inactivas_cubigest`'s mapping `{1:1,10:4,14:14}`). Si algún agente futuro consulta Cubigest con `IdSucursal=10` sin pasar por ese mapeo, mezcla datos de una planta ajena.

También existe `IdSucursal=7` (planta "Pilotera...", ajena al SPP) con 4.095 notificaciones activas — confirma que el módulo de averías de Cubigest sí se usa operativamente, pero no para Calama/Cerrillos/Coronel salvo Calama de forma parcial.

Confirma y generaliza el hallazgo de B22 (EURA 20_2, gestor 100% manual sobre SQLite) a las 3 plantas: **Cubigest `NotificacionAveria` no es una fuente viva confiable para el SPP** — Coronel no la usa nunca, Cerrillos dejó de alimentarla hace un mes, solo Calama tiene actividad reciente y aun así limitada.

## 3. Regla de fusión: NO se cambia (decisión justificada con datos)

El pendiente B39 pedía evaluar "detenida si CUALQUIERA de las fuentes lo dice". Los datos muestran que esto **es inseguro**: el registro de "PRUEBAS DE TI" lleva un mes con `EstadoMaq='DET'` sin `FechaSolucion`. Si una máquina de producción real cayera en ese mismo patrón (notificación abierta que Cubigest/el operario nunca cierra, cosa que ya pasa en la práctica con esta tabla), una regla "cualquiera excluye" la dejaría fuera del turno **para siempre**, aunque ya esté reparada — exactamente el falso positivo que el encargo pedía evitar.

Además, para 2 de las 3 plantas (Coronel: 0 registros; Cerrillos: feed muerto desde 24-08) no hay ninguna señal viva que fusionar: el fallback actual (Cubigest solo si SQLite cae) ya es la postura correcta, porque no hay nada mejor que ofrecer desde Cubigest para esas dos plantas hoy.

**Conclusión:** la arquitectura de fusión existente (SQLite primario + Cubigest `MAQ_ACTIVA` siempre + Cubigest `NotificacionAveria` solo como fallback de disponibilidad de SQLite) es la regla correcta y **no se modifica**. El problema de fondo no es de lectura de fuente sino de **proceso**: el gestor manual (`GestorAverias.tsx`) no fue actualizado por casi un mes para Coronel. Eso es un tema operativo/de capacitación en planta, no un bug de código — señalado explícitamente para que Montu/Miaude decidan si amerita una alerta de "avería no actualizada hace N días" (mejora futura, fuera de este alcance por regla de "sin cambiar nada más de la asignación").

## 4. Implementación mínima realizada

Dado que no correspondía cambiar la regla de fusión, se implementó solo la trazabilidad pedida en el punto 3 del encargo:

- `maquinas_fuente_exclusion: dict[str,str]` — mapea cada máquina excluida a la fuente que la excluyó: `sqlite_gestor_manual`, `cubigest_maq_inactiva`, `cubigest_notificacion_fallback`.
- Log `INFO` adicional: `MOTOR {sucursal}: Fuente de exclusión: {maquina}={fuente}, ...`
- Nuevo campo `metadata.maquinas_excluidas_fuente` en la respuesta del Motor (mismo dict `programar_turno` que ya expone `maquinas_detenidas`/`maquinas_no_liberadas`/`capacidad` — no requiere tocar `programacion.py`, que solo reenvía el dict).

No se tocó la lógica de asignación, `estimar_duracion_min`, cursor, ni `routers/programacion.py` / `GestorProgramacion.tsx`.

## 5. Verificación (arnés, sin tocar el servicio desplegado)

- `py_compile` del `motor_v2.py` parcheado dentro de `optifierro-backend`: **OK**.
- Comparación antes (`4325640`)/después (patch) ejecutando `programar_turno(etiquetas=[], ...)` para las 3 sucursales (1, 10, 14) dentro del contenedor: **`maquinas_detenidas` y `maquinas_no_liberadas` idénticos en las 3 plantas** — el cambio es puramente aditivo (metadata/log), no altera asignación.
- Caso Coronel: `Linea Corte Coronel` queda excluida con `fuente = sqlite_gestor_manual` (confirma que hoy, 23-09, el gestor manual ya la tiene correctamente marcada `detenida` desde el 22-09 — la corrección de datos ya se hizo en paralelo por otra vía; el código la respeta bien).
- Robustez ante Cubigest caído: durante la prueba, la conexión a Cubigest falló por SSL (`SSL routines::unsupported protocol`) en las 3 corridas — `programar_turno` **no rompió la generación**, degradó silenciosamente (excepción capturada, listas vacías donde correspondía). Esto valida el requisito "sin errores si Cubigest no responde".
- El contenedor de producción `optifierro-backend` fue restaurado a su `motor_v2.py` original (MD5 idéntico a `git show 4325640`) inmediatamente después de la prueba — no quedó modificado en runtime.
- `uvicorn` corre sin `--reload`, así que ninguna escritura temporal en el contenedor durante la prueba pudo haber afectado tráfico real.

## 6. Supuestos y limitaciones

- No se investigó por qué el feed de Cubigest para Cerrillos se detuvo el 24-08 (podría ser una integración/agente externo caído) — es un tema de infraestructura de Cubigest, fuera del alcance de este carril (solo lectura, sin tocar Cubigest).
- No se encontró una máquina llamada "Dobladora 16" en Cubigest ni SQLite para Cerrillos (existen "Dobladora Manual 3", "Dobladora Tecmor S40 1/2"); es probable que sea un nombre coloquial usado por José Auger que no coincide con el nombre canónico del sistema — no se puede confirmar/descartar sin preguntarle directamente.
- No se implementó ninguna alerta de "avería sin actualizar hace N días" en el gestor manual — es la mejora real que evitaría que se repita el caso Coronel, pero excede "sin cambiar nada más de la asignación" de este encargo.
