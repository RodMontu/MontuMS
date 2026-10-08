# Manual Técnico — Sistema Planificador de la Producción (SPP)

**Versión:** 1.0 (Entrega 24 de septiembre de 2026)  
**Ambiente de Producción:** Servidor local Torres Ocaranza (TO)  
**Identificador Técnico de Repositorio:** `optifierro`  
**Contenedores de Aplicación:** `optifierro-backend`, `optifierro-frontend`

---

## 1. Arquitectura General del Sistema

El **Sistema Planificador de la Producción (SPP)** está implementado como una arquitectura de microservicios contenerizada mediante Docker Compose sobre un servidor anfitrión local en las dependencias de Torres Ocaranza (TO).

### 1.1 Componentes y Contenedores
- **Servidor Host:** Windows 11 Pro en red local de Torres Ocaranza, ejecutando Docker Desktop.
- **Ruta de Despliegue en Servidor:** `C:\Users\OptiFierro\Desktop\optifierro`
- **Contenedor Frontend (`optifierro-frontend`):**
  - **Servidor Web:** Nginx Alpine escuchando en puerto interno `80`.
  - **Build de Aplicación:** Single Page Application (SPA) construida con React 19, TypeScript 5.9, TailwindCSS y Vite.
  - **Proxy Inverso:** Redirige las peticiones dirigidas a `/api/` hacia el contenedor backend (`http://backend:8000`), con `proxy_read_timeout` configurado en 620 segundos para soportar cálculos pesados del optimizador.
- **Contenedor Backend (`optifierro-backend`):**
  - **Runtime:** Python 3.11-slim sobre Debian Bookworm.
  - **Framework Web:** FastAPI con servidor ASGI Uvicorn escuchando en puerto interno `8000`.
  - **Driver de Base de Datos:** `msodbcsql18` (ODBC Driver 18 for SQL Server) junto a `unixodbc` y soporte OpenSSL Legacy (`openssl_legacy.cnf`).
  - **Planificador de Tareas:** `APScheduler` (`AsyncIOScheduler`) en zona horaria `America/Santiago`.
- **Red Docker:** `optifierro-network` (modo bridge), con alias `host.docker.internal` mapeado a `host-gateway` para intercomunicación con servicios del anfitrión.

### 1.2 Diagrama Mermaid de Arquitectura y Flujos de Datos

```mermaid
flowchart TB
    subgraph Host_TO ["Servidor Host Windows 11 Pro (TO)"]
        subgraph Docker_Compose ["Docker Compose (optifierro-network)"]
            FE["optifierro-frontend\n(Nginx:80 + React 19 SPA)"]
            BE["optifierro-backend\n(FastAPI:8000 + Python 3.11)"]
            SQLITE[("SQLite Local\noptifierro_v2.db\n(Volumen montado)")]
        end

        NAV["Navegador Usuario\n(Jefes de Planta / Gerencias)"]
        NAV -->|HTTP :80| FE
        FE -->|Proxy /api/ :8000| BE
        BE <-->|Lectura / Escritura| SQLITE
    end

    subgraph Red_LAN ["Red LAN Torres Ocaranza"]
        CUB_SQL[("Cubigest SQL Server\n192.168.1.195:1433\n(SOLO LECTURA)")]
        CUB_WEB["Cubigest Web (IIS)\nhttp://192.168.1.195\n(OptiSteel / MP / Detalle)"]
        GEO["GeoVictoria API / Scraper\nhttp://192.168.1.111:8002\n(Asistencia Biometrica)"]
    end

    BE -->|pyodbc / ODBC 18 (Solo Lectura)| CUB_SQL
    BE -->|Scrapers HTTP / BeautifulSoup4| CUB_WEB
    BE -->|HTTP POST /scraper/ejecutar| GEO
```

---

## 2. Integraciones y Fuentes de Datos

### 2.1 Conexión a Cubigest (SQL Server) — Regla Cardinal de Solo Lectura
- **Acceso:** Clase singleton `CubigestDB` (`backend/database_cubigest.py`), utilizando `pyodbc` con cadena de conexión ODBC Driver 18.
- **Configuración de Seguridad:** `Encrypt=no;TrustServerCertificate=yes;timeout=10;`.
- **Regla Estricta:** **SOLO LECTURA**. El SPP jamás ejecuta operaciones `INSERT`, `UPDATE`, `DELETE` o `DROP` sobre la base de datos de Cubigest.
- **Tablas Consultadas:** `IT`, `Viaje`, `DetallePaquetesPieza`, `Piezas`, `Pieza_Produccion`, `DoblezPiezas`, `Maquina`, `EstExi1` (saldos bodega), `ADQORD` (tránsito INET).

### 2.2 Scrapers Web de Cubigest
El backend cuenta con módulos de scraping HTTP para extraer información consolidada desde el aplicativo web de Cubigest (`http://192.168.1.195`):
- `scraper_cuadroprogramacion.py` y `scraper_optisteel.py`: Descarga el Cuadro de Programación OptiSteel (`CuadroProgramacionPr.aspx` y `DescargarOptistel.aspx`) para obtener el programa maestro de fabricación y piezas pendientes.
- `scraper_cuadre_inet.py`: Consulta `MP_Inet.aspx` para comparar el stock contable INET con el stock físico de materia prima.

### 2.3 Integración con GeoVictoria (Asistencia)
- **Servicio:** API local en `http://192.168.1.111:8002` (configurable vía variable `GEOVICTORIA_API_URL`).
- **Disparo Automático:** El scheduler del backend ejecuta `POST /scraper/ejecutar` a las **08:08** y a las **20:08** (Lunes a Viernes) para forzar la recolección de las marcas de asistencia antes de que corra el optimizador del SPP.
- **Consumo:** Lee los registros de colaboradores presentes por sucursal para determinar qué operadores están disponibles en el turno.

### 2.4 Base de Datos Local SQLite (`optifierro_v2.db`)
Montada como volumen persistente en `/app/optifierro_v2.db`. Almacena la configuración propia y el estado del SPP:
- `maquinas_info`: Catálogo de máquinas por sucursal.
- `hebras`: Multiplicidad de hebras por máquina y diámetro (origen de la mejora HEBRAS-01).
- `diametros`: Matriz de compatibilidad máquina-diámetro.
- `restricciones_maquina`: Restricciones físicas y dimensionales de los equipos.
- `operadores_matriz`: Competencias de cada operador y asignación habitual a máquinas.
- `turnos_programados`: Turnos planificados de colaboradores sincronizados desde GeoVictoria.
- `jornada_json`: Configuración de horarios de turnos por sucursal.
- `programacion_guardada`: Planes generados por el motor en formato JSON (`tareas_json` y `metadata_json`).
- `programacion_manual`: Registro de movimientos manuales (drag & drop) realizados en el Gantt.
- `averias`: Registro de contingencias mecánicas de equipos.
- `alertas_operador`: Log de operadores que no registraron marca de entrada tras 45 minutos.
- `log_planificacion_auto`: Auditoría de ejecuciones del scheduler automático.

### 2.5 Mapeo de Identificadores de Sucursales
Existe una discrepancia histórica entre los identificadores de sucursal en el SPP y en Cubigest que el sistema resuelve mediante traducción interna (regla técnica FP-006):

| Sucursal | ID en SPP (SQLite) | ID en Cubigest (SQL Server) |
|---|---|---|
| **Calama** | `1` | `1` |
| **Cerrillos** *(Vista Clara)* | `10` | `4` |
| **Coronel** | `14` | `14` |

> *Nota:* TOSOL queda fuera de alcance de esta entrega. El sistema ya admite una eventual incorporación sin migración de esquema.

---

## 3. Reglas Operativas del Motor de Asignación (`motor_v2.py`)

Las reglas del motor implementan las decisiones consolidadas en la Sección 3 del `MAPA_DECISIONES_SPP.md`:

1. **Premisa de Negocio (ASG-01):** El SPP no define qué piezas se fabrican. Recibe las etiquetas liberadas por OptiSteel/Cubigest y busca la combinación óptima trabajo \(\to\) máquina para maximizar el avance de la jornada.
2. **Modelo de Dos Corridas por Día (ASG-02):**
   - **Turno Día:** Se ejecuta en la mañana tras la verificación de asistencia real.
   - **Turno Noche:** Se ejecuta al inicio de la noche, calculando el saldo real de trabajo no terminado durante el día y repartiéndolo entre la dotación nocturna.
3. **Condiciones de Asignación (ASG-03 y AR-009):**
   - Solo se asigna trabajo a operadores con estado `PRESENTE`.
   - Se valida la matriz de competencia operador–máquina.
   - **Regla AR-009:** Un operador puede estar habilitado para varias máquinas, pero solo puede estar asignado a **una máquina a la vez**. Sus tareas se serializan; no se admite simultaneidad.
4. **Resolución de Horarios de Turno (ASG-04):**
   - Prioridad 1: Hora real de GeoVictoria con ventana de \(\pm\)15 minutos aplicada.
   - Prioridad 2: Horario configurado en SQLite (`jornada_json`).
   - Prioridad 3: Fallback hardcodeado:
     - Turno Día: 08:15 a 17:45 (Viernes 16:45). Colación: 13:00 a 14:00.
     - Turno Noche: 20:15 a 05:45 (Viernes 04:45). Colación: 01:00 a 02:00.
5. **Penalización por Cambio de Diámetro (ASG-05):**  
   Constante `SETUP_CAMBIO_DIAMETRO_MIN = 15`. Si una máquina pasa de procesar un diámetro a otro distinto, el motor agrega 15 minutos por concepto de cambio de herramientas y calibración.
6. **Dotación de Máquinas Activas (ASG-07):**  
   El motor solo asigna trabajo a las máquinas declaradas en `MAQUINAS_ACTIVAS` para Cerrillos (10), Calama (8) y Coronel (9).
7. **Clasificación de Acero (ASG-08):**  
   Acero Delgado (AD) definido como \(\varnothing \le 16\text{ mm}\) (`DIAMETRO_AD_MAX = 16`). Acero Grueso (AG) como \(\varnothing > 16\text{ mm}\).
8. **Máquinas de Solo Corte y Avance Parcial (ASG-09):**  
   Máquinas definidas en `MAQUINAS_SOLO_CORTE` (*Línea de Corte* en Cerrillos, *Carro de Corte* en Calama, *Línea Corte Coronel* en Coronel). Si una pieza tiene avance en Cubigest mayor a 0% (`PIE_AVANCE > 0`), el motor prohíbe reasignarla a la máquina de corte y la envía a la siguiente etapa.
9. **Dobladora por Defecto (ASG-10):**  
   Si una pieza de acero grueso tiene dobleces pendientes (`DoblezPiezas.NroDoblez > 0`) pero no posee ruta histórica resuelta, el motor utiliza como fallback la dobladora activa por defecto (`DOBLADORA_DEFAULT`): *Dobladora Tecmor S40 1* (Cerrillos), *Dobladoras* (Calama) o *Dobladora 2* (Coronel).
10. **Exclusión Absoluta de FP-LC (ASG-11, B45):**  
    `MAQUINAS_FICTICIAS = {"FP-LC"}`. La función `es_despacho_directo(id_forma, largo_mm, diametro)` identifica piezas rectas (\(\text{IdForma}=1\)) de 6 a 12 metros en diámetros AD. Estas etiquetas son filtradas en la entrada (`_obtener_pids_pendientes` y JOIN OptiSteel) y quedan completamente excluidas del Motor, la Bolsa y el Gantt.
11. **Restricciones Geométricas y Físicas (ASG-12):**  
    `RESTRICCIONES_LARGO` y `RESTRICCIONES_FUNCIONALES`: Cota A máxima de 2.000 mm en PRIMA 3D, pata máxima de 2.500 mm en Robomaster 55/60, solo 90° en Robomaster 55, solo anillos/espirales en CER40, no anillos en EURA 20_1.
12. **Bolsa de Trabajo para Días Futuros (ASG-14):**  
    La Bolsa de Trabajo extrae los pendientes futuros directamente del Cuadro OptiSteel filtrando por avance menor a 100%, combinándolos con los remanentes del día actual.
13. **Capacidad de Planta en Minutos-Hombre (B16, Ola 2):**  
    Implementado en `_calcular_capacidad_mh()`:
    $$\text{capacidad\_mh} = \sum_{\text{operadores}} \max(0, \text{duración}(\text{ventana}) - \text{solape}(\text{colación}, \text{ventana}))$$
    Se descuenta colación solo si intersecta la jornada. Si el desvío de marcación real respecto a la planta es \(\ge 30\text{ min}\), se recorta la ventana al horario real. La salida se adjunta en `metadata.capacidad` con `saldo_mh` y toneladas de piezas terminadas sin alterar la asignación de tareas (no invasivo, criterio AC8).

---

## 4. Scheduler y Tareas en Segundo Plano (`APScheduler`)

Configurado en el ciclo de vida (*lifespan*) de `backend/main.py` mediante `AsyncIOScheduler`:

| Job ID | Horario / Frecuencia | Días | Función Ejecutada | Descripción Operativa |
|---|---|---|---|---|
| `scraper_geo_dia` | **08:08** | Lun–Vie | `_ejecutar_scraper_geovictoria()` | Dispara scraper de asistencia GeoVictoria previo al turno día. |
| `scraper_geo_noche` | **20:08** | Lun–Vie | `_ejecutar_scraper_geovictoria()` | Dispara scraper de asistencia GeoVictoria previo al turno noche. |
| `job_dia` | **08:10** | Lun–Vie | `_job_dia()` | Corre optimizador para Sucursales 1, 10 y 14. Aplica lockfile `/tmp/motor_dia.lock`. Omite feriados de Chile. |
| `job_noche` | **20:10** | Lun–Vie | `_job_noche()` | Corre optimizador para Sucursales 1, 10 y 14. Aplica lockfile `/tmp/motor_noche.lock`. Omite feriados de Chile. |
| `job_its_cerradas` | Minuto **:30** | Todos | `_job_verificar_its_cerradas()` | Consulta Cubigest cada 1 hora y marca como `completado` los eventos cuyos viajes ya finalizaron. |
| `job_tardios_dia` | **08:51** | Lun–Vie | `_job_tardios_dia()` | Identifica operadores con turno que no han marcado tras 45 min del inicio del turno día y crea alerta. |
| `job_tardios_noche` | **21:21** | Lun–Vie | `_job_tardios_noche()` | Identifica operadores con turno que no han marcado tras 45 min del inicio del turno noche y crea alerta. |

### Mecanismo de Protección contra Planes Vacíos (Guard)
En `_ejecutar_generacion()` existe una salvaguarda explícita: si la corrida del motor produce 0 tareas y la base de datos ya contenía un plan válido previo con tareas para esa misma sucursal, fecha y turno, el sistema **aborta el guardado** y registra un error crítico en el log, evitando borrar accidentalmente la programación activa ante una falla transitoria de red con Cubigest.

---

## 5. Procedimiento de Despliegue y Reversión (Rollback)

### 5.1 Procedimiento de Despliegue Estándar
Ejecutado desde consola PowerShell en el servidor anfitrión de Torres Ocaranza:

```powershell
# 1. Posicionarse en el repositorio de trabajo
cd C:\Users\OptiFierro\Desktop\optifierro

# 2. Descargar últimos cambios aprobados de master
git pull origin master

# 3. Compilar imágenes limpias sin caché y levantar en background
docker compose build --no-cache
docker compose up -d

# 4. Verificar estado de contenedores
docker ps --filter "name=optifierro"
docker logs optifierro-backend --tail 25
```

### 5.2 Verificación Rápida Post-Deploy
```powershell
# Probar generación de programación en backend
Invoke-RestMethod -Uri "http://localhost:8000/api/programacion/generar" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"sucursal_id":4,"fecha_produccion":"2026-09-24","turno":"dia"}'
```

### 5.3 Procedimiento de Reversión (Rollback de Emergencia)
En caso de detectarse anomalías críticas o regresiones tras un despliegue, se utilizan las imágenes etiquetadas de respaldo generadas antes de cada intervención mayor:
- **Imágenes de Reversión Validadas:**
  - `optifierro-backend-rollback:pre_b45_20260923` (backend con B16 y B35)
  - `optifierro-backend-rollback:pre_b16_20260923` (backend con B35/HEBRAS/B26)
  - `optifierro-frontend-rollback:20260923`
- **Comando de Reversión:**
  Modificar temporalmente `docker-compose.override.yml` o reetiquetar la imagen previa:
  ```powershell
  docker tag optifierro-backend-rollback:pre_b45_20260923 optifierro_backend:latest
  docker compose up -d --no-build backend
  ```

---

## 6. Comprobaciones de Salud y Monitoreo (Health Checks)

1. **Endpoint de Salud HTTP:**
   - `GET http://localhost:8000/api/health`
   - Respuesta esperada: `{"status": "ok", "timestamp": "...", "database": "connected"}`
2. **Inspección de Logs en Vivo:**
   ```bash
   docker logs -f --tail 50 optifierro-backend
   ```
   Verificar ausencia de tracebacks y confirmación del scheduler al boot:
   `INFO: Scheduler — 08:08/20:08 scraper GV + 08:10/20:10 planif. (suc 1,10,14) + 08:51/21:21 tardíos + :30 ITs cerradas, L-V sin feriados CL.`
3. **Persistencia de Logs de Auditoría:**  
   La tabla SQLite `log_planificacion_auto` registra cada ejecución del scheduler (`resultado='ok'` o `'error'`, cantidad de etiquetas asignadas y pendientes).

---

## 7. Límites Conocidos y Trabajo Pendiente

1. **B26-B — Portar Método Validado FASE3 a Producción por Máquina:**  
   La pantalla de Producción por Máquina entrega actualmente la versión A (deltas crudos depurados con filtro 2–480 min, tope 50 ton/h y rango P25–P75). Está pendiente migrar al método estadístico formal FASE3 (agrupación a nivel de Operario + Máquina + Pedido, colapso de rachas de la misma IT y descuento de colación).
2. **B44 Completo — Ajuste Manual y Bucle de Autoaprendizaje:**  
   Falta implementar la persistencia y el algoritmo de retroalimentación para que los ajustes manuales de duración ingresados por los jefes de planta calibren progresivamente las estimaciones del Motor.
3. **Tratamiento de Censura de Jornada (Población Post-01/03/2026):**  
   Conforme a `FASE3_CENSURADA_20260913.md`, el régimen posterior a marzo de 2026 (implementación gradual de las 42 horas y turnos dinámicos, que representa un 19,25% de los deltas históricos) debe tratarse como una población estadística separada al calibrar los coeficientes del motor. Decisión aprobada por Montu el 23-09; pendiente de codificación en B26-B.
4. **HEBRAS-02 — Sincronización de Checkouts Adicionales:**  
   Queda pendiente revisar si entornos secundarios de desarrollo (como el checkout VM-OF) conservan scripts antiguos con filtros duros en la lectura de hebras.
5. **Persistencia en Memoria de Asignaciones Manuales:**  
   `global_eventos` y `global_pendientes` residen en la memoria RAM del proceso FastAPI. Aunque las reasignaciones se respaldan en la tabla `programacion_manual`, un reinicio del contenedor antes de la siguiente corrida del motor podría no reflejar temporalmente en pantalla los últimos movimientos de la Bolsa hasta que se ejecute nuevamente la planificación.
6. **Incidencia Cubigest Web Santiago (Scraper Cuadro Programación):**  
   El endpoint web `CuadroProgramacionPr.aspx` para Santiago/Cerrillos devuelve un error interno HTTP 500 originado en el propio servidor IIS de Cubigest (mientras Calama y Coronel operan sin problemas). Se mantiene pendiente de revisión con el administrador del ERP.

---

## 8. Mapa de Archivos Clave del Repositorio

```
optifierro/
├── docker-compose.yml                      # Orquestación de contenedores backend y frontend
├── DEPLOY_TO.md                            # Guía operativa de despliegue en servidor TO
├── backend/
│   ├── Dockerfile                          # Imagen Debian Bookworm + Python 3.11 + ODBC 18
│   ├── requirements.txt                    # Dependencias Python
│   ├── main.py                             # Lifespan FastAPI, APScheduler, routers y health check
│   ├── motor_v2.py                         # Motor de asignación, reglas ASG-01..14, ConocimientoMotor
│   ├── database_cubigest.py                # Conexión singleton pyodbc a SQL Server Cubigest
│   ├── optifierro_v2.db                    # Base de datos SQLite local (volumen montado)
│   ├── scraper_cuadroprogramacion.py       # Scraper HTTP para Cuadro de Programación OptiSteel
│   ├── scraper_optisteel.py                # Scraper HTTP para exportación de piezas
│   ├── scraper_cuadre_inet.py              # Scraper HTTP para cuadre de stock en tránsito
│   └── routers/
│       ├── programacion.py                 # Generación, obtención, Bolsa de Trabajo y reasignación
│       ├── tiempos_maquina.py              # Endpoint Producción por Máquina (B26 versión A)
│       ├── maquinas.py                     # API para gestión de máquinas, matrices y hebras
│       ├── averias.py                      # API para gestión y normalización de averías
│       └── admin.py                        # Importación de turnos futuros y administración
└── frontend/
    ├── Dockerfile                          # Build multi-stage Node/Vite + Nginx Alpine
    ├── nginx.conf                          # Configuración proxy inverso HTTP hacia backend:8000
    ├── package.json                        # Dependencias React 19, @dnd-kit, TailwindCSS
    └── src/
        ├── App.tsx                         # Layout principal, autenticación y barra de navegación
        └── components/domain/
            ├── GestorProgramacion.tsx      # Gantt interactivo, cajitas, drag & drop y Bolsa
            ├── TiemposPorMaquina.tsx       # Pantalla Producción por Máquina (B26-A)
            ├── GestorMaquinas.tsx          # Gestión de máquinas, matrices de hebras y restricciones
            ├── GestorAverias.tsx           # Declaración y resolución de averías
            ├── VistaSemanal.tsx            # Matriz semanal consolidada
            └── CalendarioFuturo.tsx        # Proyección de ITs para próximas semanas
```
