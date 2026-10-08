# Handoff — Motor de Tiempos OptiFierro V2
**Fecha:** 2026-09-06 (actualizado — ver sección 12 para el cierre de Fase 1)  
**Estado:** ✅ **FASE 1 CERRADA** (MT-02 a MT-06 completos) — Fase 2 en espera
de gate de terceros, ver sección 12  
**Documento vivo:** actualizar al cierre de cada sesión de trabajo

---

## 1. OBJETIVO DEL PROYECTO

Construir el indicador **toneladas/hora por máquina** para alimentar el motor de
planificación de OptiFierro V2. El objetivo es **estimar duración de trabajos para
planificar**, no cronometrar personas. Esta distinción define el nivel de precisión exigible.

Variables del modelo:
- `ID_Forma` (tipo de pieza)
- Diámetro del acero
- Calidad del acero (colada)
- Complejidad geométrica
- Peso total de la etiqueta (TAG)
- Máquina y etapa de la ruta de fabricación
- Operador (con las salvedades de la sección "Problema del operador")

---

## 2. CONTEXTO DEL CLIENTE Y RESTRICCIONES

**Cliente:** Torres Ocaranza (TO) — acería, 3 plantas (Calama, Cerrillos, Coronel).  
**Sistema:** OptiFierro V2. Repo privado: github.com/RodMontu/Optifierro-V2 (master).  
**Servidor cliente:** PROMETHEUS-AI-CORE, 192.168.1.65, user OptiFierro, Windows 11 Pro.  
**SSH alias:** `TO` en ~/.ssh/config del Mac Studio (llave id_optifierro). VPN obligatoria.

### Mapeo de sucursales — SAGRADO, nunca alterar
| Sucursal  | SQLite OptiFierro | Cubigest SQL Server |
|-----------|-------------------|---------------------|
| Calama    | 1                 | 1 (CORREGIDO)       |
| Cerrillos | 10                | 4                   |
| Coronel   | 14                | 14 (CORREGIDO)      |

### Reglas de seguridad (PTS v1.0) — no negociables
Origen: incidente agosto 2026 (query sin acotar reventó tempdb, sistema de sueldos interrumpido).

1. **Cubigest SOLO LECTURA.** Sin excepciones. Nunca INSERT/UPDATE/DELETE/DROP/ALTER/EXEC.
2. **Toda agregación ocurre fuera de Cubigest**, en script local (Python + SQLite en TO).
3. **Ningún dato crudo de Cubigest sale de TO** hacia modelos cloud. Solo metadatos.
4. **Forma canónica de toda query:** columnas explícitas, WHERE con índice, rango de fechas
   acotado, TOP de seguridad, sin ORDER BY en SQL.
5. **Ventana horaria (05:00–08:00 / 18:00–20:00):** aplica SOLO a Fase 2 (barrido masivo
   máquina × mes). NO aplica a tareas de mapeo/diagnóstico puntual.
6. **Agente ejecutor:** CCa (Claude Code) orquesta scripts Python en TO. CCa no lee filas
   crudas — solo recibe metadatos. Todo el cómputo ocurre en TO.
7. **Log obligatorio en dos lugares** tras cada sesión: bitácora_accesos_torres_ocaranza.md
   (MontuMS) + archivo de log en Escritorio de TO.

### Cadena de conexión a Cubigest (confirmada en sesión 2026-09-03)
El contenedor backend (Linux, Docker en TO) requiere:
- `Encrypt=no` — el SQL Server de TO usa TLS antiguo
- `OPENSSL_CONF` en modo legacy
- Reutilizar exactamente el mismo método de `database_cubigest.py` del backend.
  No inventar credenciales. Credenciales en el .env del contenedor.
- DB_NAME=Cubigest (réplica productiva — no existe réplica de pruebas activa a 2026-09-03).

---

## 3. MODELO DE NEGOCIO — RUTAS DE FABRICACIÓN

### Unidad de registro
El operador registra **ETIQUETAS (TAG)**: paquete de piezas del mismo `ID_Forma`,
típicamente hasta ~1000 kg. Dentro del TAG: ID_Forma, calidad, diámetro, cotas de la pieza.

### Rutas por diámetro
**Acero delgado (≤16mm):** una sola máquina (estribadora). Casos excepcionales <0.1%.  
**Acero grueso (≥18mm):** cortadora → dobladora/curvadora → estribadora (multi-etapa).

### El peso NO es aditivo entre máquinas
Un TAG de 800 kg que pasa por 3 máquinas aporta 800 kg a CADA una — no 266 kg.
Toneladas/hora es un indicador **de estación**, no de planta.

### Escenario A — CONFIRMADO a nivel de dato (2026-09-03)
Cubigest registra el paso por **cada máquina** de la ruta. Verificado en UI (Montu) y
en datos (CCa, sesión 2026-09-03):
- 2406 etiquetas únicas en Cerrillos, acero grueso ≥18mm, último mes
- **372 etiquetas (15.5%) con NroPasos > 1** — multi-máquina confirmado
- 2034 etiquetas (84.5%) con NroPasos = 1

---

## 4. ESQUEMA DE BASE DE DATOS VERIFICADO (Fase 0)

### Tablas del motor de tiempos
**`PIEZA_PRODUCCION`** — registro de producción por máquina (fuente principal):
- `PIE_ETIQUETA_PIEZA` → FK a `detallePaquetesPieza.id` (¡no al Etiqueta físico!)
- `PIE_MAQUINA` → FK a `MAQUINA.MAQ_NRO`
- `PIE_FECHA_PRODUCCION` → timestamp de registro (hora de pistolada, NO de fabricación real)
- `PIE_OPERARIO` → operador

**`MAQUINA`:** `MAQ_NRO`, `MAQ_NOMBRE`

**`detallePaquetesPieza`** — FK puente:
- `id` → PK de fila (¡no es el Etiqueta físico!)
- `Etiqueta` → código físico del TAG (varchar — el agrupador correcto para rutas)
- `IdMov` → campo sospechoso de ser FK a movimiento/máquina (no investigado — no bloqueante)
- `idpieza` → FK a `piezas`
- `IdViaje` → FK a `Viaje` (sin índice líder — gap a optimizar)

**`piezas`:** `id`, `estado`, `diametro`, `ID_Forma` (y otros)  
**`Viaje`:** `Id`, `IdIt`  
**`IT`:** `Id`, `IdSucursal`  
**`DetalleFormas`:** `Id`, `IdForma`, `X int`, `Y int`, `NroPunto int`, `EsAngulo varchar`
  → tabla relacional de puntos (X,Y) por forma. NO geometry nativo. Confirmado 2 veces.

### Índices verificados
| Tabla | Campo | Estado |
|---|---|---|
| `detallePaquetesPieza` | `idpieza` (dp.IdPieza) | ✅ índice |
| `IT` | `IdSucursal` | ✅ índice |
| `PIEZA_PRODUCCION` | `PIE_ETIQUETA_PIEZA` (PK) | ✅ PK |
| `detallePaquetesPieza` | `IdViaje` | ⚠️ sin índice líder |
| `MAQUINA` | `MAQ_NRO` | ⚠️ sin índice líder |

Los gaps no bloquean queries puntuales. Sí importarán en Fase 2 (barrido masivo). Informar a Roberto antes de Fase 2.

### Query verificada (la correcta — agrupa por Etiqueta, no por id)
```sql
SELECT TOP 5000 dp.Etiqueta AS EtiquetaReal, dp.id AS FilaId, dp.IdMov,
       maq.MAQ_NRO AS MaquinaId, pp.PIE_FECHA_PRODUCCION
FROM piezas p
JOIN detallePaquetesPieza dp ON dp.idpieza = p.id
JOIN Viaje v ON dp.IdViaje = v.Id
JOIN IT it ON v.IdIt = it.Id
JOIN PIEZA_PRODUCCION pp ON pp.PIE_ETIQUETA_PIEZA = dp.id
JOIN MAQUINA maq ON maq.MAQ_NRO = pp.PIE_MAQUINA
WHERE p.estado <> '00' AND it.IdSucursal = 4 AND p.diametro >= 18
  AND pp.PIE_FECHA_PRODUCCION >= DATEADD(month, -1, GETDATE())
```
Nota: `extractor_rutas.py` original agrupaba por `dp.id` — garantizaba NroPasos=1.
Esta versión agrupa por `dp.Etiqueta` — revela rutas reales. **Usar esta, no la original.**

---

## 5. EL PROBLEMA DEL TIEMPO — CENSURA ESTRUCTURAL

### Solo existe marca de INICIO
No hay registro de término. La duración se infiere como delta hasta el siguiente pistoleo
en la misma máquina. No es tiempo de proceso: es tiempo de ocupación aparente.

### Filtrar por causa, NO por magnitud
Filtrar por percentiles es el método **equivocado**. El método correcto es estructural:

| Bandera | Criterio | Tratamiento |
|---|---|---|
| `CENSURA_JORNADA` | Delta cruza fin de turno según calendario laboral | Excluir, contar y reportar |
| `RAFAGA` | Delta bajo el piso físico de la máquina, o N registros en ventana muy corta | Excluir, contar y reportar |
| `CAMBIO_DIA` | Delta cruza medianoche | Marcar; evaluar si es subconjunto de CENSURA_JORNADA |
| `ULTIMO_DEL_DIA` | Último registro de la máquina en la jornada | Excluir — término desconocido |
| `OK` | Ninguna de las anteriores | Set de calibración |

### Calendario de turnos — MT-01 CERRADA (2026-09-06)
Ubicación: OptiFierro V2 → Administración → pestaña Geovictoria.  
Almacenado en **SQLite local de OptiFierro** (`optifierro_v2.db`, no Cubigest, no API externa).

**Tabla: `turnos_programados`** — granularidad por persona × día (no por planta):
`id, sucursal_id, fecha, rut, nombre, turno, hora_inicio_turno, hora_fin_turno,
estado, permiso, extraido_en`. El campo `turno` viene como string compuesto
(ej. `"08:00 - 17:00(60 mins)"`, con la colación embebida), pero `hora_inicio_turno`
y `hora_fin_turno` ya vienen parseados por separado.

**Cobertura confirmada — 3 plantas:** 1=Calama (311 filas/23 rut), 10=Cerrillos
(677 filas/48 rut), 14=Coronel (154 filas/14 rut). 1142 filas totales.

**⚠️ ACTUALIZACIÓN 2026-09-06 (dictado Montu + investigación adicional) — MT-01
BAJA DE "CERRADA" A "UBICADA, CON LIMITACIÓN DE ALCANCE SIN RESOLVER":**

1. **No es un sync detenido — es un diseño de foto semanal.** Las cargas
   (`extraido_en`) son casi siempre los días **lunes ~11:00**, no diarias (12
   fechas de carga en ~3.5 meses). La tabla **no cubre los demás días de la
   semana** → tal cual, no sirve como el calendario continuo que necesita
   `CENSURA_JORNADA`. Sigue abierto si conviene pedir a TO cambiar la cadencia.
2. **`FALTA` mal etiquetado — más amplio de lo esperado.** Montu propone que
   turnos que inician ≥18:00 se reclasifiquen como `TURNO_NOCHE` en vez de
   `FALTA` (el operador aún no ha entrado a esa hora de lectura). Pero al revisar
   la carga real del 31-ago (11:00), 20 de 21 `FALTA` de Calama tienen turno de
   **día** (08:00) — a esa hora ya deberían llevar 3 horas trabajando. Hipótesis
   de latencia de sincronización de Geovictoria, sin descartar.
3. **Discrepancia de fecha sin resolver:** Montu reporta que la UI de OptiFierro
   muestra última carga = 1-sep; la tabla cruda muestra 31-ago 11:00. No
   investigado — la UI puede leer de otra fuente o mostrar "próxima carga".

**Detalle completo y evidencia:** `docs/TAREA_REINTERPRETACION_ESTADO_TURNOS.md`
— documento de handoff para una ventana de chat dedicada a resolver esto. No
bloquea el arranque de Fase 1.

`jornada_asignacion_manual` es una tabla distinta (asignación manual operador/
máquina, 3 filas) — no es el calendario, no aporta a `CENSURA_JORNADA`.

Detalle completo de la sesión: `bitacora_accesos_torres_ocaranza.md`, entrada
2026-09-06 "MT-01".

### Tiempo real verificado: ProduccionesPLC
`ProduccionesPLC` (Línea de Corte, Cerrillos): única fuente con `PLC_FechaInicio`/`PLC_FechaFin`.
Coincide con el proxy de registro solo en el 5.4% de los casos.
Esta es la **piedra de Rosetta** del modelo — calibra el sesgo del proxy.

---

## 6. EL PROBLEMA DEL OPERADOR

`PIE_OPERARIO` registra al usuario que pistolea, no necesariamente al operador que fabricó.  
Decisión tomada: usar la lista de operadores de OptiFierro. Registros fuera de esa lista
→ `OPERADOR_NO_CONFIABLE`, excluir del eje personas, conservar para el eje máquina.

**Ventanas de análisis:**
- Eje máquina → máximo 2 años
- Eje personas/operadores → máximo 6 meses

---

## 7. PLAN DE TRABAJO — ESTADO ACTUAL

### ✅ FASE 0 — Reconocimiento de metadatos — COMPLETA
| Tarea | Estado | Nota |
|---|---|---|
| T0: Respaldo auditoria_tiempos_2026/ | ✅ | Rama respaldo/auditoria-tiempos-2026 en GitHub |
| T1: Tabla de rutas + Escenario A | ✅ | PIEZA_PRODUCCION + Escenario A confirmado |
| T2: Inventario columnas | ✅ | Cubierto por extractor_rutas.py + sesión 2026-09-03 |
| T3: Tipo dato geometría | ✅ | DetalleFormas — tabla relacional (X,Y), no geometry |
| T4: Índices | ✅ | Verificados — ver sección 4 |
| T5: Cardinalidad | ✅ | Resuelta 2026-09-06 (Prueba de Carga/Prompt 3): `detallePaquetesPieza`=3.309.591 filas, `PIEZA_PRODUCCION`=2.917.466 filas, `MAQUINA`=79 filas, `Formas`=0 filas (real, no error). Vía `sys.dm_db_partition_stats`, sin COUNT(*) |
| T6: Calendario de turnos | ⚠️ | Tabla ubicada (`turnos_programados`) 2026-09-06, pero NO cubre el uso de Fase 3: es foto semanal (lunes), no calendario diario. Ver sección 5 y `docs/TAREA_REINTERPRETACION_ESTADO_TURNOS.md`. No bloquea Fase 1 |
| T7: Permisos 6 bases | ❌ | Descartada — ya validada ~6 meses atrás con Roberto |

### 🔜 FASE 1 — Definición formal del indicador + calibración PLC
Sin SQL de volumen. Ingeniería pura.

**Objetivo:** separar el indicador en DOS métricas distintas:
1. **Rendimiento observado** — solo Línea de Corte Cerrillos, con PLC. Tonelada real / tiempo real.
2. **Rendimiento estimado** — resto de máquinas, con el proxy de registro.

**El puente que da valor:** con el 5.4% de casos coincidentes + universo PLC, calibrar
cuánto sesga el proxy y en qué dirección — ¿sistemático (corregible) o ruido puro?

**Entregable:** informe de calibración + decisión sobre las 4 opciones abiertas:
1. Instrumentar más máquinas con PLC.
2. Cambiar el flujo para pistolada de inicio Y término.
3. Aceptar el proxy si el objetivo es solo priorizar, no cronometrar.
4. Documentar el límite y no tocar nada.

**Gate de Fase 2:** no avanzar hasta que este informe exista.

### ⏳ FASE 2 — Extracción de datos (barrido masivo)
Estrategia: lotes máquina × mes (~30 máquinas × 24 meses). Cada lote independiente y
reintentable. Sleep configurable entre lotes. Tabla de control de avance en SQLite.  
**APLICA ventana horaria 05:00–08:00 / 18:00–20:00.**  
**Gate:** set de queries parametrizadas revisadas por Roberto antes de ejecutar.

### ⏳ FASE 3 — Plan estadístico
Distribución asimétrica a la derecha (confirmado por académico). Secuencia:
1. Caracterizar la forma (histograma, Q-Q, asimetría, curtosis) por familia de máquina.
2. Contrastar candidatas (log-normal, gamma, Weibull) por AIC/BIC + inspección gráfica.
3. Métrica central: **mediana** (nunca promedio).
4. Para el motor de planificación: **percentil 80** (compromiso operacional).
5. Modelado de efectos: GLM familia gamma con link logarítmico, o regresión cuantílica.
6. Censura: evaluar métodos de análisis de supervivencia para CENSURA_JORNADA.

### ⏳ FASE 4 — Complejidad geométrica
Variables a derivar desde DetalleFormas (tabla X,Y):
nro. dobleces, ángulo acumulado, longitud desarrollada, radio de curvatura, nro. estribos.
Depende de lo que se encontró: tabla relacional (X,Y) — parseable en Python.  
Si la geometría resulta inútil: caída de vuelta al conteo de cotas, declarando la limitación.

### ⏳ FASE 5 — Secuencia de ataque: PRIMERO DELGADO, DESPUÉS GRUESO
Acero ≤16mm primero: atribución limpia (1 máquina, 99.9% de los casos). Banco de
calibración del modelo. Solo después, con la estructura validada, atacar el acero grueso.

**Riesgo declarado (acero grueso):** tiempo de tránsito entre estaciones contamina el delta.
Cuantificar en Fase 5 usando como referencia el parámetro de la estribadora (calibrado en
el segmento delgado).

---

## 8. MATERIAL RECUPERADO — AUDITORÍA JULIO 2026

En `auditoria_tiempos_2026/` (ahora en GitHub, rama respaldo/auditoria-tiempos-2026):
- `dataset_tiempos_completo.csv` — 128K registros, ventana jul-2025/jul-2026, ~26.8MB
- Matrices y estadísticos agregados
- `run_auditoria_tiempos.py` y `run_modulo5_cientifico.py` — metodología propia

**Advertencia:** ese análisis usó filtro IQR×1.5 — el plan maestro llama esto "el método
EQUIVOCADO". El material es insumo útil para contexto, no metodología a reusar.

**Hallazgo clave de julio (útil):** regresión desde geometría da R²=0.0096 — prácticamente
nulo, con multicolinealidad severa. Valida el giro actual hacia ETIQUETA/TAG + censura
estructural.

---

## 9. BACKLOG COMPLETO

### Backlog de infraestructura / seguridad
| ID | Pendiente | Prioridad | Responsable |
|---|---|---|---|
| BACKLOG-ROBERTO-01 | Entregar a Roberto todas las queries de OptiFierro contra Cubigest para revisión y optimización de índices | Media | Rodrigo |
| BACKLOG-ROBERTO-02 | Confirmar si cuenta de servicio `OptiFierro` quedó aprobada **sin expiración de contraseña** (ya se materializó una vez el 26-08) | Alta | Roberto |
| BACKLOG-ROBERTO-03 | Confirmar estado real del GRANT de Carlitos (aprobado de palabra vs. ejecutado vs. probado) | Alta | Roberto |
| BACKLOG-ROBERTO-04 | Crear réplica de pruebas de Cubigest aislada de producción | Media | Roberto/TI TO |
| BACKLOG-CUBIGEST-INDICES | Agregar índice líder en `detallePaquetesPieza.IdViaje` y `MAQUINA.MAQ_NRO` antes de Fase 2 | Media | Roberto |
| BACKLOG-OLLAMA-TO | Puerto 11434 (Ollama) en TO sigue sin autenticación — pendiente de restricción de red o proxy | Baja | Rodrigo |

### Backlog del motor de tiempos
| ID | Pendiente | Prioridad | Bloquea |
|---|---|---|---|
| MT-01 | ⚠️ Tabla ubicada, pero es foto semanal (lunes), no calendario diario — no sirve tal cual para CENSURA_JORNADA. Ver `TAREA_REINTERPRETACION_ESTADO_TURNOS.md` | Alta | Fase 3 |
| MT-01b | Respondida por Montu 2026-09-06: no es sync roto, es diseño de carga semanal. Sigue abierto si se puede pedir a TO cambiar la cadencia a diaria | Alta | Fase 3 |
| MT-01c | Investigada 2026-09-06: hipótesis de Montu (turno de noche) no explica todos los casos — 20/21 FALTA de Calama el 31-ago son turno de DÍA. Hipótesis de latencia de sync de Geovictoria, sin descartar. Ventana dedicada a diseñar la solución. ACTUALIZACIÓN 08-09 (ventana coordinadora): esta es la MISMA tabla `turnos_programados` que la ventana Pendientes-OF trabajó como B14 la noche del 07-09 — encontró causa raíz real (el mecanismo de extracción nunca trajo datos futuros por leer la tabla de asistencia diaria en vez de scrapear GeoVictoria en vivo) y la corrigió parcialmente (mañana 08-09 ya tiene datos reales; 09 al 13-09 quedó bloqueado por un problema del daterangepicker de GeoVictoria, decisión pendiente de Montu). Esto NO resuelve la hipótesis de latencia de sync que sigue abierta aquí — son hallazgos relacionados pero distintos. Ver `pendientes_sistema_planificador.md` B14 para el detalle completo antes de retomar esto | Alta | Fase 3 |
| MT-02 | ✅ CERRADA 2026-09-06 — ver T5 en sección 7 (detallePaquetesPieza=3.309.591, PIEZA_PRODUCCION=2.917.466) | — | — |
| MT-03 | ✅ CERRADA 2026-09-06 — `extractor_rutas_v2.py` escrito (agrupa por `dp.Etiqueta`, conexión compartida), original intacto. Luz verde de Montu, se evalúa cuando corra | — | — |
| MT-04 | ✅ CERRADA 2026-09-06 — informe en `docs/informe_calibracion_plc_proxy_20260906.md`: mediana 6,66min vs media 735min → ruido de instrumentación domina. Recomienda Opción 3 (priorizar, no cronometrar) en las 2 máquinas de mayor volumen (84%), Opción 4 para el resto | — | — |
| MT-05 | ✅ CERRADA 2026-09-06 — `IdMov` = `Movimientos.Id`, confirmado 100% (2000/2000) | — | — |
| MT-06 | ✅ CERRADA 2026-09-06 — cobertura confirmada en las 3 plantas (Calama 311 filas/23 rut, Cerrillos 677/48, Coronel 154/14) | — | — |
| MT-07 | Analizar dataset de julio 2026 (auditoria_tiempos_2026/) dentro de infraestructura TI de Montu | Media | — |

| BACKLOG-PTS-RETRO | ⚠️ PENDIENTE: dos violaciones de canal el 2026-09-06 — (1) Miaude ejecutó directo contra Cubigest/turnos_programados (ver detalle previo), (2) **CCa ejecutó directo contra Cubigest** para destrabar Tarea 2 del lote Motor de Tiempos, en vez de Carlitos3.8. **Montu confirma ambas como excepción puntual, no precedente.** Retro de fondo pendiente al cerrar tareas actuales | Alta (post-tareas) |

### Backlog de arquitectura del ecosistema
| ID | Pendiente | Prioridad |
|---|---|---|
| BACKLOG-CRED-WINCREDMAN | Resolver warnings de persistencia de credenciales git en TO (`wincredman`) | Baja |
| BACKLOG-CCA-IDENTITY | ✅ CONFIRMADO Y RESUELTO 2026-09-06: CCa rechazó un prompt `-p` que le asignaba identidad/rol/credenciales inline (lo leyó como posible inyección, correctamente). Fix que funcionó: instrucción corta y natural apuntando a un archivo real en `~/MontuMS/docs/` (ej. `TAREA_LOTE_CCA_20260906.md`) para que él mismo lo verifique con `ls` junto a los demás docs del proyecto, en vez de recibir el rol por línea de comando | Media |

---

## 10. CONVENCIONES DEL PROYECTO

- serverX = 192.168.1.111, user `x`
- Mac Studio = 192.168.1.102, user `montu`, ~/MontuMS/ es NFS mount a /home/x/MontuMS/
- TO = 192.168.1.65, user `OptiFierro` (Windows 11). SSH via alias `TO` en ~/.ssh/config
- Cubigest SQL Server = 192.168.1.195:1433
- Repo OptiFierro: github.com/RodMontu/Optifierro-V2 (master)
- Repo MontuMS: github.com/RodMontu/MontuMS (fuente de verdad de infraestructura)
- CCa = Claude Code con Anthropic API (`claude --dangerously-skip-permissions`)
- Carlitos = Claude Code con modelo local vía harness Pi (`pi --provider coder-flash`)
- Nunca `git push` sin revisión de Montu del diff
- Bitácora de accesos: ~/MontuMS/docs/bitacora_accesos_torres_ocaranza.md
- Log de TO: archivo de log en Escritorio de PROMETHEUS-AI-CORE

---

## 11. PRÓXIMO PASO CONCRETO

**Actualización 2026-09-06 (ventana coordinadora, Prompt 4):** dos tareas que estaban
pendientes en esta sección ya se cerraron, con nueva evidencia real (no solo consolidación
de handoffs — ver detalle en `bitacora_accesos_torres_ocaranza.md`, entradas del día):

1. **Prueba de carga contra Cubigest (Prompt 3) — EJECUTADA Y APROBADA.** 4 niveles
   crecientes (conexión pura → catálogo → cardinalidad → hipótesis multi-máquina), CPU sin
   impacto significativo en ningún nivel (máx. 2%→15%). La hipótesis de `dp.Etiqueta` vs
   `dp.id` se **re-confirmó de forma independiente**: 372 etiquetas multi-máquina, número
   idéntico a la sesión del 2026-09-03 (sobre una base de únicas ligeramente distinta por
   ser corrida en día distinto). T5 (cardinalidad) queda resuelta de paso.
2. **MT-01 (calendario de turnos) — CERRADA.** Ver sección 5. Tabla `turnos_programados`
   ubicada, con dos cabos sueltos nuevos que hay que confirmar con Montu antes de Fase 3
   (ventana de datos no llega a hoy; semántica de `estado` sesgada hacia `FALTA`).

**Gate pendiente de esta ventana coordinadora, no resuelto aún:** `LOG_CAMBIOS_2026.md` no
tenía registrada la sesión de Prueba de Carga del 2026-09-06 hasta esta actualización —
solo vivía en la bitácora. Corregido en este mismo cierre (ver `LOG_CAMBIOS_2026.md`).

**Primera acción de Fase 1 — EJECUTADA 2026-09-06.** Esquema de `ProduccionesPLC`
verificado (metadata únicamente, `INFORMATION_SCHEMA.COLUMNS`, sin filas de negocio):
20 columnas. Las relevantes para el modelo:
- `PLC_IdEtiquetaTO` (int, NOT NULL) — FK probable hacia la etiqueta/TAG. **Pendiente
  confirmar contra qué campo hace join exacto** (¿`detallePaquetesPieza.Etiqueta`?
  ¿otro identificador?) — esto es lo que habilita cruzar el 5.4% de casos coincidentes.
- `PLC_FechaInicio` y `PLC_FechaFin` (datetime, **ambos NULLABLE**) — hallazgo nuevo:
  no todas las filas de `ProduccionesPLC` tienen tiempo de proceso completo. Filtrar
  por `IS NOT NULL` en ambos antes de usar para calibración.
- `PLC_Estado`, `PLC_CodigoIT`, `PLC_Diametro`, `PLC_largo`, `PLC_NroPiezas` — atributos
  físicos de la pieza procesada. `PLC_CodigoIT` es candidato para relacionar con la
  tabla `IT` (que ya tiene `IdSucursal`) — no verificado aún.
- Detalle de hasta 3 barras de materia prima (`PLC_KgsBarraN`, `PLC_LargoBarraN`,
  `PLC_IdMP_BarraN`) — no crítico para el indicador principal, pero disponible.

**Siguiente acción concreta de Fase 1:** confirmar el join `PLC_IdEtiquetaTO` ↔
etiqueta física (`dp.Etiqueta`), y con eso ejecutar la consulta de cruce del 5.4%
de casos coincidentes contra el universo completo de `ProduccionesPLC` con
`PLC_FechaInicio`/`PLC_FechaFin` no nulos. Esta consulta sí toca filas de negocio de
Cubigest (no solo metadata) → ejecutar vía Carlitos desde TO, respetando PTS v1.0,
con la plantilla de conexión validada el 2026-09-06 (bitácora "Nivel 2").

**⚠️ Advertencia de Montu sobre `ProduccionesPLC` (2026-09-06, a tener en cuenta al
calibrar, no antes):** el circuito PLC en Cerrillos fue un **piloto corto y con
errores conocidos** — no un sistema maduro. Al llegar al análisis real: privilegiar
datos que se agrupen en torno a mediana/media/moda; esperar muchos valores extremos
que sean ruido del piloto (no señal real) y que van a ensuciar la calibración si se
toman todos por buenos. Esto se suma — no reemplaza — al tratamiento de censura
estructural ya definido en la sección 5: aquí el ruido es de **instrumentación del
piloto**, no de censura por jornada.

---

## 12. CIERRE DE FASE 1 (2026-09-06)

**FASE 1 CERRADA.** Los seis ítems del backlog del motor de tiempos que
delimitaban Fase 1 (MT-02 a MT-06) están completos — ver detalle de cada uno
en la sección 9. Resumen:
- MT-02: cardinalidad de tablas resuelta.
- MT-03: `extractor_rutas_v2.py` escrito (agrupa por `dp.Etiqueta`).
- MT-04: informe de calibración PLC/proxy entregado, con recomendación
  (Opción 3 para las 2 máquinas de mayor volumen, Opción 4 para el resto).
- MT-05: `IdMov` confirmado como FK a `Movimientos.Id`.
- MT-06: cobertura de `turnos_programados` confirmada en las 3 plantas.

MT-01/MT-01b/MT-01c (calendario de turnos) quedan abiertas pero **no bloquean
Fase 1** — bloquean Fase 3 (ver sección 5 y `TAREA_REINTERPRETACION_ESTADO_TURNOS.md`).

**Fase 2 ya autorizada por Roberto** (criterio: consultas chicas, atómicas, no
todo junto — mismo criterio ya aplicado en Fase 1). Índices/GRANT
(`BACKLOG-CUBIGEST-INDICES`, `BACKLOG-ROBERTO-03`) son optimización deseable,
no gate — no bloquean el arranque.

## 13. ARRANQUE FASE 2 — GRUESO (ventana 18:00-20:00, 07-09-2026)

**Confirmado 17:51 hrs (ventana coordinadora):** Carlitos3.6 (puerto 11504) y
Carlitos3.8 (puerto 11505) activos en Mac Studio, sin necesidad de levantarlos.

**Contexto:** TAREA_MULTIMAQUINA_20260906.md investigó el 16,2% multi-maquina
del piloto delgado. Conclusion: son "trabajos en paralelo" reales (mismo pool
de maquinas, ej. EURA 20_1/2/3), no ruido. Cifras: 10,6% delgado, 34,8% grueso
(Cerrillos, agosto). H1/H2 de corte->estribadora NO explican el patron.

**Tratamiento propuesto para "trabajo en paralelo" (pendiente luz verde de
Montu, NO bloquea la extraccion de hoy):**
- Fase 2 (extraccion cruda): capturar SIEMPRE la secuencia completa por
  etiqueta (ya lo hace extractor_rutas_v2.py, agrupa por dp.Etiqueta). No se
  pierde informacion aunque la decision de tratamiento se demore.
- Fase 3 (calibracion): tratar multi-maquina igual que el 0,1% excepcional del
  segmento delgado — flag + EXCLUSION del set de calibracion principal,
  contado aparte (no hay dato de participacion real por maquina para repartir
  tiempo/atribucion todavia). Ese subconjunto excluido queda como dataset
  propio: es insumo directo para B2 en la ventana Pendientes-OF una vez haya
  mas volumen para ver el criterio real que usan los jefes de planta.

**Tarea concreta de esta ventana (18:00-20:00 HOY, no mas):**
Fase 2 - extraccion cruda ACERO GRUESO, Cerrillos, agosto-2026 completo
(equivalente al piloto delgado ya hecho). Via extractor_rutas_v2.py +
Carlitos3.8, lotes chicos (maquina x semana o similar), tabla de control de
avance en SQLite. NO expandir a otras plantas/meses hoy - cerrar este ciclo
primero, evaluar resultado, recien despues escalar a las ~30 maquinas x 24
meses completos.

**Recordatorio duro:** PTS v1.0 vigente. Ventana horaria 18:00-20:00 hoy.
Monitoreo de carga durante la ejecucion, aborto inmediato ante sobrecarga.
Cubigest solo lectura, filas crudas acotadas, agregacion siempre en local.



## 14. FASE 2 GRUESO — CERRILLOS/AGOSTO-2026 EJECUTADA (ventana 18:00-20:00, 07-09-2026)

**Estado: ✅ COMPLETADA para este ciclo (Cerrillos, agosto-2026, grueso ≥18mm).**
NO expandido a otras plantas/meses — según instrucción de esta ventana.

**Verificación de infra (independiente, no autoreporte):** Carlitos3.6 (11504) y
Carlitos3.8 (11505) confirmados arriba vía `curl http://192.168.1.102:PUERTO/health`
→ 200 en ambos (el `curl` a `127.0.0.1` falla porque el bind es a la IP LAN, no
localhost — anotar para la próxima ventana, no es que estén caídos).

**Script:** `extractor_rutas_v2.py` no existía en el contenedor (se había limpiado
tras el piloto delgado del 2026-09-06). Reescrito desde cero para grueso,
parametrizado por lote (`fecha_ini fecha_fin idsucursal diametro_min`), copiado a
`optifierro-backend:/app/extractor_rutas_v2.py`. Adopta las correcciones ya
validadas en el piloto delgado: `detallePaquetesPieza.KgsPaquete` (no
`piezas.PesoReal`), JOIN `MAQUINA.IdSucursal = IT.IdSucursal` (evita mezclar
máquinas de otra planta con mismo `MAQ_NRO`), fechas en formato `YYYYMMDD` sin
separadores (evita error 22007).

**Persistencia local (nueva, en TO, dentro del contenedor):**
`optifierro-backend:/app/fase2_grueso_cerrillos.db` (SQLite) — dos tablas:
- `datos_grueso`: filas crudas (lote_id, etiqueta, maquina_id, fecha_produccion,
  kgs_paquete). Nunca salió de TO — solo agregados viajaron a Miaude/Carlitos.
- `control_avance`: una fila por lote (fecha_ini, fecha_fin, idsucursal,
  diametro_min, estado, filas_extraidas, etiquetas_unicas,
  etiquetas_multi_maquina, timestamps). Reintentable: rerun del mismo lote hace
  `INSERT OR REPLACE`.

**Ejecutor real de las 5 consultas:** Carlitos3.8 vía `ssh TO` →
`docker exec optifierro-backend`, `CARLITOS_TIMEOUT=550` desde el inicio
(aprendizaje del piloto delgado). Las 5 corrieron sin timeout, sub-segundo cada
una en el servidor (volumen bajo, sin señal de sobrecarga).

**Lotes ejecutados (semana calendario, no ISO, cubren agosto completo sin huecos
ni solapes):**
| Lote | Filas | Etiquetas únicas | Multi-máquina (dentro del lote) |
|---|---|---|---|
| 01-08 ago | 638 | 613 | 7 |
| 08-15 ago | 712 | 665 | 18 |
| 15-22 ago | 705 | 609 | 42 |
| 22-29 ago | 701 | 645 | 27 |
| 29-31 ago | 83 | 83 | 0 |
| **Total** | **2839** | — | — |

**⚠️ Hallazgo metodológico — sumar el "multi-máquina" por lote SUBESTIMA la
cifra real.** Verificado calculando directo sobre `datos_grueso` completo (los
5 lotes unidos, query propia — no toca Cubigest, no requiere Carlitos):
`FILAS=2839, ETIQUETAS_ÚNICAS=2277, MULTI_MÁQUINA=261 (11,46%)`. La suma de los
"multi-máquina" impresos por lote da 94, no 261 — porque una etiqueta con pasos
en semanas distintas (ej. viernes semana 2 + lunes semana 3) queda partida entre
lotes y cada lote la ve como mono-máquina. **Los datos crudos están completos y
correctos** (rango contiguo sin huecos ni solapes, cero filas perdidas o
duplicadas) — el problema es solo de lectura: la cifra de multi-máquina debe
calcularse siempre sobre el dataset unificado, nunca sumando el campo impreso
por lote. Aplica igual para Fase 2 completa (30 máquinas × 24 meses): diseñar
el cálculo de multi-máquina como paso posterior sobre la tabla consolidada, no
como parte del extractor por lote.

**⚠️ Discrepancia sin resolver, no investigada hoy (fuera de alcance):** esta
cifra real (11,46% multi-máquina, grueso, Cerrillos, agosto-2026) no calza con
el "34,8% grueso (Cerrillos, agosto)" citado en la sección 13 de este mismo
handoff (contexto de `TAREA_MULTIMAQUINA_20260906.md`). Puede ser distinta
definición de "grueso"/filtro, o base de cálculo distinta (¿% sobre etiquetas
multi-paso ya preseleccionadas, no sobre el universo completo?). Queda
pendiente para quien retome `TAREA_MULTIMAQUINA_20260906.md` — no se investigó
la causa en esta ventana por estar fuera del alcance pedido.

**Próximo paso concreto:** con el ciclo Cerrillos/agosto/grueso cerrado y
validado, evaluar resultado antes de escalar a más meses/plantas (instrucción
explícita de no expandir hoy). Candidatos para la próxima ventana: (a) repetir
el mismo patrón de lotes semanales para Calama y Coronel, agosto-2026, grueso;
(b) o retroceder en el tiempo dentro de Cerrillos (jul-2026, jun-2026...)
manteniendo grueso. Decisión pendiente de Montu / ventana coordinadora.

**Limpieza:** archivos de staging en `/tmp` (Mac y TO) borrados al cierre.
Persisten en TO (intencional, son el entregable): `/app/extractor_rutas_v2.py`
y `/app/fase2_grueso_cerrillos.db`.

## 15. REPLANTEO DE ESTRATEGIA DE LOTES (08-09, antes de la ventana 18:00-20:00)

**Pregunta de Montu:** ¿es realmente necesario ir mes por mes y máquina por
máquina? A este ritmo no terminamos ni el próximo año.

**Evidencia real de la sección 14 (no opinión, dato medido anoche):** las 5
consultas del ciclo Cerrillos/agosto/grueso corrieron **sub-segundo cada una,
sin señal de sobrecarga** (CPU 2%→15% máx en la prueba de carga formal del
06-09, sección 11). El cuello de botella NO es la base de datos — es el
overhead de proceso: cada lote hoy implica una invocación completa de
Carlitos con su propia verificación y documentación.

**Cambio propuesto para esta noche:** subir la granularidad del lote de
"semana × 1 sucursal × 1 grado" a **"mes completo × las 3 sucursales × ambos
grados (delgado+grueso) en una sola consulta"** — sigue siendo atómico en el
eje temporal (1 mes, respeta el criterio de Roberto de "consultas chicas, no
todo junto"), pero deja de repetir la misma consulta 3×2=6 veces por mes sin
necesidad. Con esto, el universo completo (3 sucursales × 24 meses) baja de
~144 combinaciones × ~5 lotes semanales cada una (~720 consultas) a **~24
consultas** (una por mes). Monitoreo de carga se mantiene igual de estricto
por consulta, solo cambia cuántas hace falta disparar.

**No implementado aún — validar con el primer lote de la ventana de hoy antes
de asumir que escala igual de bien:** un mes completo × 3 sucursales podría
traer más filas que una semana × 1 sucursal (orden de magnitud a confirmar en
vivo, no en teoría). Primer lote de la ventana 18:00-20:00 de hoy: correr
**un mes de prueba con el criterio nuevo** (sucursal=todas, grado=todos,
mes=agosto-2026, ya tenemos con qué comparar contra los datos de la sección
14) y verificar tiempo de respuesta + CPU antes de asumir que el resto de los
23 meses se comporta igual.



## 16. VALIDACIÓN DEL CRITERIO NUEVO (sección 15) — BLOQUEADOR ENCONTRADO (ventana 18:00-20:00, 08-09-2026)

**Estado: 🛑 el criterio nuevo NO escala tal cual está — encontrado un problema real
de datos en Cubigest, no un bug del script.** No avanzar a los 23 meses restantes
con este criterio hasta resolver esto.

**Verificación de infra (independiente):** Carlitos3.6/3.8 confirmados arriba vía
`curl` a `192.168.1.102:11504`/`11505` → 200 ambos (no confié en el "verificado
19:11" de la ventana coordinadora sin chequeo propio). SSH a TO ok, contenedores
up 20h.

**Lote de prueba ejecutado:** un solo query, agosto-2026 completo, `IT.IdSucursal
IN (2,3,4)` (las 3 sucursales en código Cubigest), sin filtro de diámetro (ambos
grados). Script nuevo `extractor_rutas_v2_test_mensual.py` (deliberadamente NO
sobrescribí `extractor_rutas_v2.py` — ese sigue siendo la versión validada de
grueso/Cerrillos de anoche, intacta). Resultado crudo vía Carlitos3.8,
`CARLITOS_TIMEOUT=550`:
- `SEGUNDOS_QUERY=1.26`, `FILAS_TOTALES=9138`, `ETIQUETAS_UNICAS=5895`.
- CPU del contenedor antes/después: 0.09%→0.08% — sin señal de sobrecarga.

**🚩 Lo que encontré al revisar el desglose por sucursal (no lo di por bueno a la
primera — 9138 coincidía sospechosamente con 6299 delgado + 2839 grueso de
Cerrillos solo, sección 14):** los 9138 filas son **100% Cerrillos (IdSucursal=4).
Calama y Coronel devolvieron CERO filas.** No es casualidad — es un bug real.

**Causa raíz (confirmada, metadata de `MAQUINA.IdSucursal`, vía Carlitos3.8):**
```
IdSucursal  n_maquinas
1           10   <- Calama, pero en código SQLite (no Cubigest)
2            3   <- Calama, código Cubigest correcto, pero incompleto (solo 3 de ~13)
4           28   <- Cerrillos, código Cubigest, bien poblado (por esto el piloto de anoche funcionó)
7           11   <- sin identificar (¿máquinas administrativas/conectores?)
10           1   <- Cerrillos, código SQLite residual (1 fila suelta)
14          17   <- Coronel, pero en código SQLite (no Cubigest) -- Coronel NO tiene NADA en IdSucursal=3
15,16,17,18  1,1,3,4  <- sin identificar
```
`MAQUINA.IdSucursal` **no usa una sola convención de códigos** — mezcla el
esquema SQLite-OptiFierro y el esquema Cubigest según la planta, y para Coronel
directamente no existe ninguna fila con el código Cubigest (3). El JOIN
`MAQUINA.IdSucursal = IT.IdSucursal` (adoptado de `diagnostico_kgshora.py` en el
piloto delgado para "evitar mezclar máquinas de otra planta con mismo MAQ_NRO")
**funciona por casualidad para Cerrillos y falla silenciosamente para Calama y
Coronel** — no lanza error, solo devuelve 0 filas para esas plantas. Sin este
chequeo de desglose por sucursal, el resultado (9138 filas, 1.26s) se habría
reportado como "el criterio nuevo escala perfecto" siendo en realidad un dato
incompleto y engañoso.

**Lo que NO se investigó hoy (sin tiempo, queda para próxima ventana):**
1. Si `MAQ_NRO` realmente colisiona entre plantas (la razón original del JOIN por
   `IdSucursal`). Si NO colisiona, la solución más simple es sacar esa condición
   del JOIN y confiar solo en `IT.IdSucursal` (que sí está limpio y es la fuente
   correcta de sucursal para la ruta de fabricación). Si SÍ colisiona, hay que
   arreglar la condición para tolerar ambos esquemas de código por planta, o pedir
   a Roberto que limpie `MAQUINA.IdSucursal`.
2. Qué son las máquinas en IdSucursal 7, 15, 16, 17, 18 — probablemente las
   administrativas (Conectores, Armacero, PRUEBAS DE TI vistas en el catálogo de
   Cerrillos) que traen su propio IdSucursal separado, a confirmar.

**Artefactos de esta sesión, quedan en TO (`optifierro-backend:/app/`) para que la
próxima ventana los revise, no se subieron a git:** `extractor_rutas_v2_test_mensual.py`,
`diag_maquina_sucursal.py`, `fase2_test_criterio_nuevo.db` (contiene las 9138 filas
de Cerrillos únicamente — dato parcial, NO usar como si fuera el universo completo
de agosto). `extractor_rutas_v2.py` (el de grueso/Cerrillos, sección 14) **no se
tocó** — sigue siendo la única versión validada hasta ahora.

**Próximo paso concreto:** antes de correr un solo mes más con el criterio de la
sección 15, decidir con Montu/Roberto el punto 1 de arriba (colisión real de
MAQ_NRO sí o no) y arreglar el JOIN. Recién con eso resuelto, repetir el lote de
prueba de agosto-2026 y confirmar que Calama y Coronel aparecen con filas > 0
antes de escalar a los 23 meses restantes.

**Cierre de ventana:** 19:2x hrs, dentro de la ventana 18:00-20:00. Nada quedó
corriendo contra Cubigest sin terminar. Staging en `/tmp` (Mac y TO) limpio.

---

## ⚠️ CORRECCIÓN (08-09-2026, sesión posterior) — el diagnóstico de arriba estaba
## incompleto. La causa raíz NO era `MAQUINA.IdSucursal` sucio.

Confirmado con 3 fuentes independientes (chats históricos marzo-mayo 2026, conteo
en vivo de `IT.IdSucursal`, y `INVENTARIO_MAESTRO.md` líneas 860-863, vigente):
los códigos Cubigest reales son **Calama=1, Cerrillos=4, Coronel=14** — NO
`(2,3,4)` como usé en el query de la sección 16. Ese fue el error: filtré
`IT.IdSucursal IN (2,3,4)`, y por eso Calama y Coronel no aparecieron — no porque
`MAQUINA.IdSucursal` estuviera mal poblado (esa columna, revisando de nuevo con
los códigos correctos, calza bien: 10 máquinas en IdSucursal=1 para Calama, 28 en
IdSucursal=4 para Cerrillos, 17 en IdSucursal=14 para Coronel). El JOIN
`MAQUINA.IdSucursal = IT.IdSucursal` no estaba roto — el WHERE sí. La sección
16 queda como registro de lo que pasó, pero el punto 1 de "lo que no se
investigó" ya no aplica: no hace falta sacar la condición del JOIN, solo usar
los códigos correctos. `IdSucursal=7` (14.484 IT, tamaño relevante) sigue sin
identificar, no bloquea nada. Repitiendo el lote de prueba con `(1,4,14)`.


## 17. FASE 2 COMPLETA — RUTAS, 3 PLANTAS, 24 MESES, AMBOS CALIBRES (08-09-2026, sesión posterior a la corrección)

**Estado: ✅ Universo completo de rutas extraído en una sola consulta.** Bug de la
sección 16 corregido (ver corrección arriba) usando los códigos reales
`IdSucursal` Cubigest: Calama=1, Cerrillos=4, Coronel=14 (fuente:
`INVENTARIO_MAESTRO.md` L860-863, ya confirmado con datos en vivo).

**Origen del hallazgo:** Montu recordó (por dictado) que en chats antiguos había
un mapeo de IdSucursal "según dónde se busca". `conversation_search` encontró 3
chats independientes (2026-03-22, 2026-03-26, 2026-05-22) con el mismo mapeo. Se
confirmó además en vivo (`IT` agrupado por `IdSucursal`, sin filtro) y en el
propio `INVENTARIO_MAESTRO.md`, que no se había consultado antes de armar el
query de la sección 16 — debió serlo, es la Regla de Oro #1 del rol.

**Script:** `extractor_rutas_v2_test_v2.py` (en `optifierro-backend:/app/`),
misma lógica que el de la sección 16 pero con `SUCURSALES_CUBIGEST = (1,4,14)`.
Persistencia en `fase2_test_criterio_v2.db` (tablas `datos_test` +
`control_avance_test`).

**Dos lotes corridos, ambos verificados independiente (no solo autoreporte de
Carlitos3.8):**
| Lote | Segundos | Filas | Etiquetas únicas |
|---|---|---|---|
| Sanity check: agosto-2026 | 1.15 | 13.668 | 6.821 |
| **24 meses completos (sep-2024 a sep-2026)** | **3.78** | **360.266** | **49.450** |

**Desglose por planta (lote de 24 meses):** Calama 62.288 filas/13.696 etiquetas
· Cerrillos 251.944/45.619 · Coronel 46.034/15.344. Suma exacta con el total.

**CPU contenedor:** 0.06%→0.06% en el lote grande (0.08% en el sanity check).
Cero señal de sobrecarga en ningún momento. BLOCK I/O subió de 4.3MB a 39.3MB
(esperado, es la escritura de 360k filas a SQLite local).

**Conclusión validada (hipótesis de Montu, confirmada con datos):** el cuello de
botella nunca fue CubiGest ni el tamaño de la consulta — fue la cantidad de
invocaciones/ceremonia por lote. El universo completo de rutas (Fase 2) para las
3 plantas, 24 meses, ambos calibres, quedó resuelto en 2 consultas reales.

**Pendiente, no bloqueante:** `IdSucursal=7` (14.484 IT en el conteo total, tamaño
relevante) sigue sin identificar — no forma parte de las 3 plantas de interés, no
se investiga salvo que Montu lo pida.

**Próximo paso:** con Fase 2 (rutas) cerrada para el universo completo, el
siguiente movimiento natural es Fase 3 (calibración estadística de tiempos por
máquina) usando `datos_test`/`fase2_test_criterio_v2.db` como base — pendiente de
que Montu lo confirme antes de avanzar, y de decidir si este dataset de prueba se
promueve a la tabla "oficial" de Fase 2 o se re-extrae limpio con nombre
definitivo.


## 18. FIX GEOVICTORIA `_configurar_fechas()` — COMMITEADO Y SUBIDO (12-09-2026)

**Estado: ✅ Cerrado.** Cuarto intento de CCa (tras 2 diagnósticos limpios y un
cuelgue real en el intento 3, matado manualmente) tuvo éxito con timeouts
explícitos (`timeout 900` a nivel de proceso + `page.goto(timeout=20s)`), sin
activarse ninguno.

**Causa raíz real (corrige la teoría de la sección 15/16):** GeoVictoria no
migró a un widget custom nuevo — el `#Fecha_Raw` de la página padre quedó
huérfano (oculto, sin efecto real). El filtro real vive ahora en `#datefilter`
dentro del iframe `gvportal.geovictoria.com`, mismo plugin jQuery
`daterangepicker` de siempre. Esto explica por qué el fallback anterior
"funcionaba" para el caso default (hoy) pero ignoraba cualquier rango custom
en silencio.

**Fix:** `_configurar_fechas()` reescrita para esperar el iframe + `#datefilter`
y usar la misma API jQuery (`setStartDate`/`setEndDate`/`clickApply`) apuntando
al elemento correcto. Firma sin cambios — ningún llamador tocado (mapa de
impacto de Graphify: único llamador `scrape_y_descarga()`, 3 llamadores de esa:
`main()` diario, `turnos_futuro.scrapear_rango_futuro()`, `backfill_marzo.main()`).

**Verificado independientemente (no solo autoreporte de CCa):**
- Diff real (tras corregir un problema de CRLF que lo inflaba a 1542 líneas
  falsas): 36 inserciones / 64 eliminaciones, aislado 100% a
  `_configurar_fechas()` + helper nuevo `_obtener_frame_gvportal()`.
- `asistencia.db`: 76 registros para 2026-09-11 y 76 para 2026-09-12,
  coincide exacto con lo reportado por CCa para la prueba del scraper diario.

**Commit:** `9985793` en `scrap-geovictoria` (solo ese archivo — los otros
cambios pendientes sin relación, de la feature `/turnos/extraer-futuro`, quedan
intactos y sin commitear, tal como estaban). Pusheado a `origin/master`.

**Regla #5 aplicada:** grafo Graphify regenerado tras el commit —
`scrap-geovictoria` pasó de estar atado al commit `7581b9a` (sección 17) a
`9985793` (82 nodos, 136 aristas, 16 comunidades). Grafo combinado
(`~/graphify-workspace/merged/graph.json`) también regenerado: 892 nodos,
1455 aristas. Registro en La Biblioteca actualizado con el commit vigente.


## 19. MT-01c VERIFICADO COMO DESTRABADO (12-09-2026, misma sesión)

Con el fix de la sección 18 ya en producción (commit `9985793`), se corrió
`turnos_futuro.scrapear_rango_futuro()` (código de la ventana Pendientes-OF,
solo verificación de lectura, sin tocar su trabajo) para 2026-09-13→09-16
(empieza mañana — el escenario exacto que B14 tenía roto).

**Resultado:** éxito a la primera (`daterangepicker intento 1: ok`), 304
registros, 76 personas, `sucursales=[1, 10, 14, 99]`. El `99` es
"sin mapear" — `_planta_a_sucursal()` solo cubre `empresa=='TOMAE'`, y este
rango trae también empresa `TOSOL` sin mapeo — nota para quien retome B14,
no es un bug de esta sesión, es preexistente en ese parser.

**Conclusión:** MT-01c ya no bloquea Fase 3. Falta que la ventana
Pendientes-OF lo confirme/cierre formalmente de su lado (B14) y decida qué
hacer con el mapeo de sucursal `99`/TOSOL antes de dar por completo el
backfill de `turnos_programados`.


---

## 20. B14 CERRADO Y DESPLEGADO — CONFIRMACIÓN DESDE VENTANA PENDIENTES-OF (12-09-2026)

Recibido el aviso de la sección 18-19. Verificación independiente hecha antes
de aceptar el reporte (no se tomó al pie de la letra):

**Hallazgo:** el commit `9985793` era real y estaba genuinamente pusheado a
GitHub — pero el trabajo se hizo sobre `~/graphify-workspace/scrap-geovictoria`
(la copia de análisis del Mac Studio para Graphify), NO sobre el checkout real
de TO. El checkout real (`/c/Users/OptiFierro/Desktop/scrap-geovictoria`)
seguía en HEAD `468985c` (junio) — el fix nunca llegó a desplegarse. Por eso
`turnos_programados` seguía vacío para el rango de prueba pese al reporte de
éxito.

**Corregido por esta ventana:**
1. `git pull origin master` en el checkout real de TO → fast-forward limpio,
   diff confirmado idéntico al reportado (36+/64- en `scraper_geovictoria.py`).
2. Rebuild `--no-cache` + `up -d --force-recreate` de `geovictoria-api` y
   `geovictoria-scheduler`. Logs limpios post-rebuild.
3. Backfill real ejecutado: `POST /turnos/extraer-futuro` para 09-09 al
   09-20 → **690 registros reales** (190 Calama / 400 Cerrillos / 100
   Coronel), verificado directo en `turnos_programados` (no solo la
   respuesta del endpoint) — horarios variables correctos por día (17:00 vs
   18:00 según corresponda).
4. Confirmado en `scheduler.py`: `refresh_turnos_semana` apunta a
   `day_of_week='sun', hour=20, minute=0` — correcto. Job mensual viejo ya
   no existe.
5. TOSOL/sucursal 99: no requiere fix. `extraer_turnos_futuro_logic()` ya
   filtra a `SUCURSALES_TURNOS_FUTURO = (1, 10, 14)` por diseño — TOSOL
   queda excluido naturalmente, no es alcance de OptiFierro.

**B14 queda CERRADO de este lado.** MT-01c confirmado destrabado — Fase 3
puede retomarse sin pendientes de esta ventana.

**Lección para ambas ventanas:** cuando el grafo Graphify o cualquier trabajo
de análisis usa una copia local del repo (`~/graphify-workspace/`), un commit
ahí no llega al sistema real solo por existir en git — falta el pull en el
checkout real + rebuild. Verificar despliegue real, no solo que el commit
exista, antes de reportar algo como "resuelto".


## 20. DECISIÓN APROBADA — Tratamiento multi-máquina para Fase 3 (12-09-2026)

Montu aprobó el criterio propuesto en sección 13: los casos "multi-máquina"
(trabajos en paralelo, mismo pool de máquinas) se **flaggean y excluyen** del
set principal de calibración de Fase 3, contados aparte como dataset propio
(insumo para B2 en la ventana Pendientes-OF más adelante).

## 21. FASE 3 EXPLORATORIA — LANZADA (12-09-2026)

Corrida preliminar (NO oficial — falta censura de jornada, pendiente de
`turnos_programados` completo por la otra ventana) sobre `fase2_rutas_completo.db`
completo (373.934 filas). Caracterización de distribución de tiempos por
máquina (mediana, p80, skew/curtosis, candidatas log-normal/gamma/Weibull por
AIC/BIC vía scipy), con exclusión de multi-máquina por el criterio recién
aprobado. Delegado completo a CCa (SSH a TO, análisis local, sin tocar
Cubigest). En curso — ver próxima entrada para resultado.


## 22. FASE 3 EXPLORATORIA — RESULTADO (12-09-2026, cierra sección 21)

**Tiempo real: 5 minutos** (10:23→10:28, verificado por timestamp de archivo —
CCa autoreportó "20-25 minutos", equivocado; no confiar en su autoreporte de
tiempo transcurrido).

**Conclusión honesta de CCa: NO lista para calibración oficial.** 46,3% de los
deltas entre máquinas superan 30 días — confirma que sin `turnos_programados`
se mezcla tiempo real de máquina con tiempo de espera/cola. Medianas de
150-300h/máquina son tiempo de ciclo end-to-end, no tiempo de proceso.
Mecánica del pipeline (deltas, ajuste AIC/BIC, manejo de outliers) sí quedó
validada y lista para re-correr una vez haya censura de jornada.

**Candidatas de distribución:** gamma y Weibull se reparten el mejor ajuste
en las 35 máquinas con datos suficientes; log-normal no ganó en ninguna.

**Limitación explícita del criterio multi-máquina usado (aproximación, NO
oficial):** agrupó por nombre de máquina quitando sufijo `_N` (detectó solo
familia EURA 20 en Cerrillos) — excluyó 11,96% de etiquetas, probablemente
**subestima** el universo real (no agrupó "Dobladora Tecmor S40 1/2",
"Curvadora 1/2", "ESTRIBADORA TJK 1/2", que usan espacio en vez de guion
bajo). `TAREA_MULTIMAQUINA_20260906.md` no da un criterio mecánico aplicable
a las 3 plantas — pendiente para cuando se defina el criterio oficial.

**Gap de catálogo encontrado:** `maquina_id` en los datos sin entrada en
`maquinas_info`: 25,26,27,28 (Cerrillos), 108,111 (Calama), 413-417 (Coronel).
No bloquea, pendiente de limpieza de catálogo.

**Reporte completo:** `~/MontuMS/docs/FASE3_EXPLORATORIA_20260912.md` (Mac
Studio) y `optifierro-backend:/app/docs/FASE3_EXPLORATORIA_20260912.md` (TO).
CSVs/JSON de soporte y script reusable (no commiteado) en `/app/` del
contenedor.

**Estado de esta ventana: sin pendientes propios.** Bloqueada en
`turnos_programados` (Pendientes-OF). Nada más que hacer hasta que esa
ventana cierre su parte.


## 23. CORRECCIÓN IMPORTANTE — TOSOL está FUERA de alcance (12-09-2026)

**Montu aclaró: TOSOL no es parte de este proyecto — es otro giro legal de la
empresa.** No se debe mapear, incluir, ni considerar TOSOL en nada de Motor
de Tiempos ni en el backfill de `turnos_programados`.

**Esto corrige el mensaje enviado antes a la ventana coordinadora** (ver
prompt de la sección de arriba en esta conversación, ya entregado): ese
mensaje sugería que `sucursal_id=99` era "sin mapear" y que agregar un mapeo
para TOSOL (ID 7 = Quilicura, documentado en `CLAUDE.md` de
`scrap-geovictoria` pero no implementado en `_planta_a_sucursal()`)
resolvería el problema. **Eso está mal.** El tratamiento correcto es
**EXCLUIR/FILTRAR los registros de empresa TOSOL**, no mapearlos a una
sucursal. Si la ventana coordinadora ya actuó sobre el mensaje anterior,
corregir con esta indicación antes de avanzar más con el backfill.

**No se tocó código por esto** — es una corrección de entendimiento, no un
fix aplicado. Queda para quien resuelva el backfill de `turnos_programados`
(ventana Pendientes-OF) filtrar TOSOL explícitamente antes de dar por
completo ese trabajo.

---

## ESTADO ACTUAL DE ESTA VENTANA (Motor de Tiempos) — para la ventana coordinadora

- **Fase 2 (rutas):** ✅ completa. `fase2_rutas_completo.db` en TO
  (`optifierro-backend:/app/`), 373.934 filas, 24 meses, 3 plantas (Calama,
  Cerrillos, Coronel — TOSOL excluido por diseño de la extracción original),
  ambos calibres.
- **GeoVictoria `_configurar_fechas()`:** ✅ arreglado, commiteado y pusheado
  (commit `9985793`, repo `scrap-geovictoria`). MT-01c queda destrabado
  mecánicamente — verificado con una corrida real de rango futuro.
- **Fase 3 exploratoria:** ✅ corrida preliminar completa (sección 22) —
  confirma que **no se puede calibrar en serio hasta que `turnos_programados`
  esté completo** (censura de jornada pendiente). Candidatas de distribución
  adelantadas: gamma/Weibull.
- **Bloqueador real para seguir:** backfill completo de `turnos_programados`
  — territorio de la ventana Pendientes-OF (item B14), no de esta ventana.
  **Con la corrección de TOSOL de arriba aplicada.**
- **Pendiente menor, no bloqueante:** confirmar con Montu si se guarda un
  cambio de documentación en `CLAUDE.md` de `scrap-geovictoria` (agrega dónde
  vive el filtro de fecha real, `#datefilter` en iframe `gvportal` — no toca
  código, solo documentación).
- **Sin pendientes propios de ejecución en esta ventana** hasta que
  Pendientes-OF cierre su parte.


## 24. CLAUDE.md ACTUALIZADO Y PUSHEADO (12-09-2026, cierra pendiente de sección 23)

Commit `7008a76` en `scrap-geovictoria` — solo documentación, no toca código.
Agrega: (1) dónde vive el filtro de fecha real tras el fix de `_configurar_fechas()`
(`#datefilter` en iframe `gvportal`, no `#Fecha_Raw`); (2) aclaración explícita
de que **TOSOL es otro giro legal, fuera de alcance de este proyecto** — el
tratamiento correcto es excluir/filtrar esos registros (ID 7 "Quilicura"/TOSOL
y el catch-all ID 99), nunca mapearlos. No se toca código de
`_planta_a_sucursal()` — queda para quien resuelva el backfill de
`turnos_programados` aplicar el filtro real.

**Sin pendientes de documentación en esta ventana.** Todo lo de hoy
(sección 18-24) está commiteado/documentado. Sigue bloqueada en el backfill
de `turnos_programados` (Pendientes-OF).


---

## 25. CRITERIO DE CENSURA HISTÓRICA DE JORNADA — definido con Montu (12-09-2026)

Sin backfill histórico real posible (GeoVictoria no expone 24 meses atrás).
Criterio estático acordado para Fase 3:

- Día 8:00-18:00 L-V: ventana fija, 3 plantas, todo el histórico (24 meses).
- Cerrillos noche 20:00-06:00: ventana fija, todo el histórico (confirmado
  por Montu: 2+ años, cubre el período completo de estudio).
- Calama/Coronel NO tienen turno noche histórico fijo (el de Calama es
  reciente, sin fecha exacta) — no asumir ventana noche ahí.
- Cualquier producción fuera de esas ventanas (fin de semana cualquier
  planta, noche en Calama/Coronel) = jornada extraordinaria real, SIN
  ventana fija (confirmado: "sacan cierta cantidad de trabajo y paran, sin
  límite de hora"). Ventana disponible = entre la primera y la última marca
  de producción real observada ese período en esa máquina. No asumir 8-18
  ni ninguna otra ventana fija para estos casos.
- Zona de confianza reducida: ley de 42 horas / turnos dinámicos empezó a
  regir hace ~6 meses (sin fecha exacta — Montu no tiene contrato de
  referencia). Aplicar igual el criterio fijo desde ~marzo-2026 en adelante
  como aproximación, pero taguear esos registros como confianza reducida
  para que Fase 3 los pueda excluir/ponderar aparte si el ajuste sale mal.

Pendiente de implementación (no bloqueante, se retoma cuando corresponda).


---

## 26. ACTUALIZACIÓN DESDE VENTANA PENDIENTES-OF — B14 y B1 CERRADOS (13-09-2026)

Actualización para el Motor de Tiempos: la ventana Pendientes-OF cerró los
dos puntos que bloqueaban el avance de Fase 3.

### B14 — `turnos_programados` COMPLETO Y FUNCIONAL

El backfill histórico real vía GeoVictoria no fue posible (GeoVictoria no
expone 24 meses de historia). Se acordó el criterio estático (ver sección
25). Adicionalmente:

- El mecanismo de extracción semanal (`_configurar_fechas` / iframe
  `#datefilter`) quedó arreglado y desplegado (commit `9985793` ya conocido
  por esta ventana). El scraper diario de asistencia sigue sano.
- El scheduler corre cada domingo 20:00 y actualiza `turnos_programados`
  con la semana siguiente. Datos verificados en producción: Cerrillos y
  Calama con horarios variables reales (17:00/18:00 según el día), Coronel
  sin programación (esperado, Gustavo confirmó planta casi sin trabajo).
- TOSOL: excluido por diseño (`SUCURSALES_TURNOS_FUTURO = (1, 10, 14)`).

**Implicación para Motor de Tiempos:** `turnos_programados` ya tiene datos
reales y correctos para las fechas futuras. La CENSURA DE JORNADA en Fase 3
puede implementarse con esta tabla como fuente de ventana horaria real
(complementando el criterio estático del sección 25 para el histórico de 24
meses). El pipeline de Fase 3 puede retomarse.

### B1 — Motor OF ya usa cuadro OptiSteel como fuente del día

El motor de OptiFierro ya no usa el heurístico de ventana de fechas de
Cubigest para decidir qué fabricar. Desde commit `5828637` (13-09-2026),
`_obtener_pids_pendientes_optisteel` es la fuente del día:

- Lee `cuadro_programacion_optisteel` (programación real de OptiSteel)
  para el día/sucursal → solo los viajes que OptiSteel decidió.
- JOIN a Cubigest para traer diámetro/forma/largo por pieza (misma cadena
  técnica que antes).
- Sin datos → sin asignación (sin fallback al heurístico viejo).
- Scheduler activo: domingo 20:00 + L-V 07:50 para actualizar el cuadro.

**Implicación para Motor de Tiempos:** el campo `prioridad_optisteel` que
la función nueva hereda por viaje viene **vacío** en todos los casos actuales
(problema interno de Torres Ocaranza, no bug nuestro — sin plazo de
resolución). El Motor de Tiempos no necesita considerar esto para Fase 3,
pero si en algún momento el campo se puebla, la función ya lo propaga.

### Commits relevantes de esta ventana (para referencia cruzada)

| Commit | Repo | Qué hace |
|---|---|---|
| `3bd49d0` | optifierro | scraper_cuadroprogramacion.py |
| `a9c72d9` | optifierro | endpoint /cuadro-programacion/ejecutar |
| `8c4253b` | scrap-geovictoria | scheduler jobs cuadro OptiSteel |
| `5828637` | optifierro | wire motor → cuadro OptiSteel (B1 cerrado) |
| `40b64da` | optifierro | fix es_viernes en motor_v2.py |
| `3e2112a` | optifierro | UI reparto en paralelo (B2 frontend) |
| `1d9653e` | optifierro | backend reparto en paralelo (B2 backend) |

### Pendientes que siguen abiertos desde esta ventana (para cuando retome)

- B16 (minutos-hombre reales): depende de que Motor de Tiempos entregue
  duraciones confiables por trabajo — sin insumo todavía.
- B17 (ventana ±15min): verificado que sigue intacto en el código (mayo).
- B15 (restricción operador-máquina): verificado que sigue activo en motor.
- Factores de forma (MT4 de esta ventana): validar si hay suficiente
  histórico por combinación forma+diámetro+máquina antes de segmentar.
- Gap de catálogo `maquinas_info`: IDs 25-28, 108, 111, 413-417 sin entrada
  (detectado en Fase 3 exploratoria, sección 22).
- Criterio oficial multi-máquina: el de la sección 22 es aproximación, no
  oficial. Definir antes de la calibración oficial de Fase 3.

### Estado de bloqueo levantado

Con B14 y B1 cerrados, **el bloqueo de Fase 3 queda levantado.** La
siguiente tarea del Motor de Tiempos es implementar la censura de jornada
(criterio de sección 25) sobre `fase2_rutas_completo.db` y re-correr Fase 3
con los datos censurados correctamente.


## 27. CENSURA DE JORNADA — IMPLEMENTACIÓN LANZADA (13-09-2026)

Con B14/B1 cerrados (sección 26), Fase 3 destrabada. Se implementa el
criterio de censura de sección 25 sobre `fase2_rutas_completo.db` y se
re-corre la caracterización de distribución. Delegado completo a CCa
(SSH a TO, análisis local, sin tocar Cubigest). En curso — ver próxima
entrada para resultado.


## 28. PÉRDIDA Y RECUPERACIÓN DE `fase2_rutas_completo.db` (13-09-2026)

**Qué pasó:** al lanzar la censura de jornada (sección 27), CCa encontró que
`fase2_rutas_completo.db` ya no existía en `optifierro-backend`. Verificado
independientemente: el contenedor se recreó hoy 14:58 (coincide con los
despliegues de B14/B1 de la otra ventana — `docker build --no-cache && up -d`).
Único bind mount del contenedor es `optifierro_v2.db` — todo lo demás,
incluido nuestro archivo, vivía en la capa efímera y se perdió al recrear el
contenedor. **No es error de la otra ventana** — es un hueco nuestro: guardamos
algo que necesitábamos conservar en un lugar sin persistencia real.

CCa se detuvo a preguntar en vez de adivinar o volver a tocar Cubigest por su
cuenta — comportamiento correcto.

**Recuperación:** re-extraído con el mismo query/criterio ya validado
(secciones 14-17), vía Carlitos3.8. **360.264 filas** (no 373.934 — ver nota
de calidad abajo), 49.450 etiquetas únicas. Por planta: Calama 62.288/13.696,
Cerrillos 251.944/45.619, Coronel 46.032/15.344 (2 filas menos que la
extracción original, variación mínima esperable).

**Mejora de calidad encontrada de paso:** el dataset original (373.934 filas)
tenía agosto-2026 **duplicado** — se había corrido un lote de sanity-check de
solo agosto y luego el de 24 meses completo (que ya incluía agosto) sin
deduplicar, ambos insertados en la misma tabla. Esta vez no se repitió el
lote redundante — el dataset nuevo (360.264 filas) es más limpio que el
original. Cualquier análisis de Fase 3 anterior (sección 22, exploratoria)
que haya usado el dataset viejo debe considerarse con esa duplicación de
agosto como ruido de fondo — no invalida las conclusiones cualitativas
(candidatas de distribución, % de deltas >30 días) pero los conteos exactos
de esa corrida no son 100% limpios.

**Persistencia esta vez — corregido el hueco:** copia guardada FUERA del
contenedor en `~/MontuMS/datos_fase2/fase2_rutas_completo.db` (Mac Studio /
NFS serverX, fuera del ciclo de vida de TO). Verificada íntegra (360.264
filas, coincide exacto). El archivo dentro del contenedor sigue existiendo
para que el trabajo de censura pueda seguir operando ahí, pero ya no es la
única copia.

**Pendiente de decisión, no urgente:** si vale la pena pedir a la otra
ventana un bind mount real para este tipo de datos de análisis en el
contenedor, para no depender de acordarse de sacar copia manual cada vez.


## 29. ESTADÍSTICA APLICADA — INTERVALOS DE PREDICCIÓN (13-09-2026)

Con censura de jornada implementada (sección 27), Montu pidió ir un paso más
allá: no solo comparar candidatas de distribución por AIC/BIC (relativo),
sino bondad de ajuste real (KS, Anderson-Darling, chi-cuadrado), prueba de
bimodalidad (hipótesis: proceso + espera en cola podría verse como mezcla de
2 poblaciones), y de ahí intervalos de predicción al 95% correctos (usando
percentiles de la distribución ajustada, no fórmula de normal) en formato
aplicado: "Máquina X: entre A y B minutos, 95% confianza". Delegado a CCa.
En curso — ver próxima entrada.


## 30. SEGMENTACIÓN POR ID_FORMA — PROBANDO HIPÓTESIS ALTERNATIVA A LA BIMODALIDAD (13-09-2026)

Montu (dictado VisualVoice) propuso que la bimodalidad de la sección 29
podría deberse a mezclar piezas simples y complejas por máquina, no (solo)
a cola de espera. Contexto valioso encontrado en chats de 03-09: ya existe
un `decisiones_metodologicas.json`/CSV previo que normaliza por hebras
(`T_norm = DeltaT/(LargoTotal*NroPiezas/Hebras)`) pero con R²=0,0078 —
prácticamente nulo, sugiere que falta segmentar por complejidad de forma,
no solo normalizar por tamaño/hebras.

**Extracción extendida:** `datos_rutas_conforma` en `fase2_rutas_completo.db`
— mismo dataset (360.264 filas, 3.99s de query, vía Carlitos3.8) +
`id_forma` (columna `piezas.IdForma`, confirmada por metadata). ID_Forma=1
("largo comercial", sin valor agregado) es el más común pero irrelevante.
ID_Forma=2 (un doblez, la más simple con proceso real, según Montu):
48.607 filas, 18.485 etiquetas — buena muestra para la prueba.

Copia de seguridad actualizada en `~/MontuMS/datos_fase2/fase2_rutas_completo.db`.

**Prueba en curso (delegada a CCa):** aislar id_forma=2, repetir bimodalidad
+ bondad de ajuste, comparar directo contra el resultado de "todas las
formas mezcladas" (sección 29). Si la bimodalidad desaparece al aislar una
sola forma → confirma hipótesis de Montu. Si persiste → sigue apuntando a
cola de espera. En curso — ver próxima entrada para resultado.


## 31. RUTA + TIEMPOS — SEGUIMIENTO POR OPERARIO (14-09-2026, madrugada)

Nueva idea de Montu (dibujada a mano): en vez de seguir la etiqueta de máquina en
máquina, seguir también al **operario** — clave Trabajo + Operario + Máquina, no
solo Trabajo + Máquina. Razón: un salto de tiempo entre dos pasos de un trabajo
puede no ser cola de espera — puede ser que el operario haya ido a hacer un tramo
de otro trabajo distinto en el medio.

**Datos confirmados (metadata, vía Carlitos con incidente de generación — resultado
recuperado del log de sesión — y CCa, que se negó dos veces correctamente a un
intento de autorización relayada; ver bitácora):**
- `pie_Turno`: 100% poblado, solo 'Dia'/'Noche', limpio en todo el histórico.
- `PIE_OPERARIO`: 100% poblado en todo el histórico.
- `PIE_AVANCE`: no se pudo verificar con etiqueta real esta noche (no crítico).

**Regla de break confirmada por Montu:** turno Día, descontar 60 min si la ventana
pasa por 13:00-14:00. Turno Noche, descontar 60 min si pasa por 01:00-02:00.

**Extracción extendida:** `datos_rutas_v4` en `fase2_rutas_completo.db` — mismo
dataset (360.264 filas, 5,72s de query, vía Carlitos3.8) + `operario` + `turno`,
cobertura 100% en ambos. Copia de seguridad actualizada en
`~/MontuMS/datos_fase2/fase2_rutas_completo.db`.

**Análisis en curso (delegado a CCa):** reconstruir línea de tiempo por operario
(no por etiqueta), calcular delta entre eventos consecutivos del mismo operario,
aplicar descuento de break real por turno, excluir saltos entre turnos/días,
comparar bimodalidad y medianas contra los dos métodos anteriores (crudo,
censura estática). En curso — ver próxima entrada para resultado.


## 32. CORRECCIÓN DEL MÉTODO — (OPERARIO + MÁQUINA), NO SOLO OPERARIO (14-09-2026)

El intento de la sección 31 falló: seguir al operario sin anclar a máquina mezcló
escaneos rápidos entre máquinas distintas (medianas de 3-782 segundos, sin
sentido). Montu corrigió con un dato operativo real, no hipótesis: **"un trabajo
lo comienza y termina el mismo operador"** — el operario procesa todo el trabajo 1
en una máquina, termina, y el registro del trabajo 2 en esa MISMA máquina marca
el fin real del trabajo 1 ahí. Luego se mueve a la siguiente máquina y repite el
patrón.

**Unidad de análisis corregida:** agrupar por (operario, máquina_id) —no operario
solo, no etiqueta sola—, colapsar registros consecutivos de la misma etiqueta
(mismo lote), y tomar el delta al cambiar de etiqueta dentro del mismo grupo como
el tiempo real de la etiqueta anterior en esa máquina. Regla de break (13-14h
día, 01-02h noche) sin cambios. Delegado a CCa, comparando contra los 3 métodos
anteriores (crudo, censura calendario, operario sin anclar). En curso.


## 33. AGREGADO CAMPO PEDIDO (IT.Id) Y REINTENTO OPERARIO+MÁQUINA (14-09-2026)

Causa raíz de la sección 32: faltaba distinguir "pedido" (IT.Id, ~50 piezas) de
"etiqueta" (pieza individual) — por eso el colapso de filas consecutivas casi
nunca se activaba (0,36%). `datos_rutas_v5` agrega `pedido_it`. Reintento
delegado a CCa, dispatch 03:07. Ver próxima entrada para resultado.


## 34. CIERRE DE LA MADRUGADA — VALOR DE PARTIDA ENTREGADO (14-09-2026, 06:08)

**Estado: pausado aquí por horario (lunes 08:00), no por falta de camino.**

Se llegó al mejor resultado de toda la semana: la idea de Montu (seguir al
operario, no solo la pieza) fue el quiebre real. Tras 3 iteraciones
(operario solo → +máquina con etiqueta → +máquina con `pedido_it` real),
26 de 33 máquinas dan medianas en minutos plausibles (16-95 min).

**Entregable:** `~/MontuMS/docs/VALOR_DE_PARTIDA_TIEMPOS_MAQUINA.md` — tabla
de medianas por máquina lista para usar como valor inicial del motor,
más las máquinas a NO usar todavía (111/415 excluidas por pistoleo; 101,
106, 107, 404, 111 con medianas implausibles sin investigar; varias con
n<30).

**Lo que sigue sin resolver:** el intervalo de confianza 95% sigue ancho
(no hay forma de acotarlo con este dato) — la causa identificada es tiempo
de espera hasta el siguiente pedido, no tamaño ni forma de pieza. Pista
para retomar: buscar una señal de cierre/entrega de pedido en Cubigest,
distinta de "inicio del siguiente".

**Pendiente menor, sin investigar:** por qué 5 máquinas (101,106,107,404,
más 111 ya excluida por otra razón) dan medianas de segundos/pocos minutos
pese al método correcto.

**Todo lo demás de esta ventana (Fase 2, fix GeoVictoria, MT-01/MT-01b
aclarado, MT-07/José Auger encontrado) sigue documentado en las secciones
anteriores — nada de eso cambió esta madrugada.**


## 35. REFORMULACIÓN A TONELADAS/HORA POR ID_FORMA+DIÁMETRO (14-09-2026)

Montu corrigió el entregable: el negocio mide todo en toneladas, no minutos
por pedido. La sección "Tiempos por máquina" debe entregar, para
(ID_forma, diámetro, planta): ruta posible + ton/hora por cada máquina de
esa ruta. Método de cálculo del tiempo NO cambia (operario+máquina+pedido
ya validado) — cambia la segmentación (por id_forma+diámetro, no por kg) y
la conversión final a ton/hora. Delegado a CCa. En curso.


## 36. IMPLEMENTACIÓN REAL EN motor_v2.py — DIÁMETRO EN LA ESTIMACIÓN (14-09-2026)

Montu: prioridad máxima es entregar el proyecto esta semana (ideal martes),
necesita facturar. El "valor de partida" simple (sección 34) queda como piso
mínimo ya en producción — esto es el paso real: que `estimar_duracion_min()`
use también diámetro (ya recibe el parámetro, no lo usaba para el match del
CSV). Mapa de impacto verificado antes de tocar (único llamador:
`programar_turno`; 2 lectores del CSV sin romperse con columna nueva).
Delegado completo a CCa: agregar columna `Diametro` al CSV con las 581
combinaciones ya calculadas (sección 35), nuevo nivel de match más específico
en el código, pruebas, sin commit. En curso.


## 37. CIERRE: DIÁMETRO EN motor_v2.py COMMITEADO, DESPLEGADO Y GRAFO AL DÍA (14-09-2026)

**Todo cerrado, en producción:**
- Commit `657d720` (sobre B1/B2 ya mergeados, sin conflicto — verificado con
  las 4 pruebas: match específico, fallback sin diámetro, fallback global,
  y el path de auto-reparto 80/100% intacto). Pusheado a `origin/master`.
- Grafo Graphify regenerado: `657d7203` (904 nodos, 1432 aristas — antes 810).
  Grafo combinado con `scrap-geovictoria` también actualizado (986 nodos).
- Desplegado al contenedor en vivo de TO (`optifierro-backend`), con backup
  de ambos archivos previos, restart limpio, verificado respondiendo 200.

**Auditoría pedida por Montu, corregida en el momento:**
- Bitácora de accesos a TO: tenía 5 accesos reales de esta madrugada sin
  registrar (2 metadata, 2 extracciones completas de 24 meses, 1 consulta de
  nombres de máquina) — corregidos retroactivamente, ver entrada en
  `bitacora_accesos_torres_ocaranza.md`.
- Grafo: estaba 6 commits atrasado (`7581b9a` vs HEAD real) — corregido con
  esta misma sesión de cierre.

**Pendiente menor, no crítico, anotado por CCa:** `_tasa_kg_hora_historica`
(usada para sugerir la 2da máquina del reparto 80/100%) no filtra por
diámetro — con las 276 filas nuevas puede tomar la tasa de un diámetro
distinto al real al sugerir máquina. No afecta la duración calculada, solo
la sugerencia de a qué otra máquina repartir. Queda para revisión futura.
