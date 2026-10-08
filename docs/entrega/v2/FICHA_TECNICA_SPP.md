# Ficha Técnica (ítem A12) v2.0 — Sistema Planificador de la Producción (SPP)

**Nombre oficial:** Sistema Planificador de la Producción (SPP / "el Planificador")
**Nombre técnico interno de repositorio:** `optifierro` (GitHub: `RodMontu/Optifierro-V2`)
**Cliente:** Torres Ocaranza (TO)
**Plantas:** Cerrillos, Calama, Coronel (TOSOL fuera de alcance)
**Criticidad:** **MEDIA** (definida por Montu)
**Fecha de esta versión:** 2026-09-28 — reemplaza v1 (24-09-2026)

> "OptiFierro" se usa **solo como identificador técnico interno**: nombre del repositorio (`Optifierro-V2`),
> de los contenedores (`optifierro-backend`, `optifierro-frontend`, `optifierro-ollama`) y del archivo de base
> de datos (`optifierro_v2.db`). El producto que usan los usuarios de TO se llama **SPP** / "el Planificador".

---

## 1. Stack técnico

| Capa | Tecnología | Versión real verificada en producción |
|---|---|---|
| Runtime backend | Python | 3.11.15 (imagen `python:3.11-slim`, Debian 12 Bookworm) |
| Framework backend | FastAPI + Uvicorn (ASGI) | FastAPI 0.141.1, Uvicorn 0.54.0 |
| Driver de base de datos | pyodbc + ODBC Driver 18 for SQL Server (Microsoft) | pyodbc 5.3.0 |
| Planificador de tareas | APScheduler (`AsyncIOScheduler`) | 3.10.4 (pinneada en requirements.txt) |
| Feriados Chile | `holidays` | 0.46 (pinneada) |
| Zona horaria | `pytz` | 2026.4 |
| Hash de contraseñas | `bcrypt` | 5.0.0 |
| Scraping HTTP | `requests` + `beautifulsoup4` | 2.34.2 / 4.15.0 |
| Cliente HTTP asíncrono | `httpx` | 0.28.1 |
| Análisis de datos | `pandas`, `openpyxl` | 3.0.6 / 3.1.5 |
| Frontend framework | React | 19.2.0 |
| Lenguaje frontend | TypeScript | ~5.9.3 |
| Estilos | TailwindCSS + PostCSS + Autoprefixer | ^3.4.19 |
| Bundler frontend | Vite | ^7.3.1 |
| Drag & drop (Gantt) | `@dnd-kit/core` / `sortable` / `utilities` | 6.3.1 / 10.0.0 / 3.2.2 |
| Servidor web frontend | Nginx (imagen `nginx:stable-alpine`) | 1.28.3 |
| Orquestación | Docker Compose | formato `3.8` (advertencia: Compose moderno marca esta clave como obsoleta, sigue funcionando) |
| IA local | Ollama (contenedor `optifierro-ollama`) | usado para normalizar texto libre de averías (`routers/averias.py::POST /normalizar`); on-premise, sin llamadas a APIs de IA en la nube |

<!-- fuente: en vivo, docker exec optifierro-backend pip freeze / python --version / nginx -v, 2026-09-28 -->
<!-- fuente: backend/requirements.txt; frontend/package.json; docker-compose.yml -->

**Advertencia de mantenimiento:** de las dependencias de `requirements.txt`, solo `apscheduler` y `holidays`
están pinneadas a una versión exacta. El resto (`fastapi`, `uvicorn`, `pyodbc`, `pandas`, `httpx`, `bcrypt`,
`requests`, `beautifulsoup4`, `python-dotenv`, `openpyxl`, `pytz`) se instalan sin versión fija — un
`docker compose build --no-cache` en otra fecha puede traer versiones distintas a las verificadas arriba.

---

## 2. Lenguajes

- **Backend:** Python (snake_case, sin type hints exhaustivos en el código existente — no es una convención
  aplicada de forma consistente en `motor_v2.py`/`routers/*`).
- **Frontend:** TypeScript en modo estricto (`noUnusedLocals`, `noUnusedParameters` activos en `tsconfig`), React
  con componentes en PascalCase.
- **Consultas a la base de terceros (Cubigest):** T-SQL (Transact-SQL), siempre `SELECT`/CTE de solo lectura.

---

## 3. Dependencias del software

### 3.1 Backend (`requirements.txt`, íntegro)
```
fastapi
uvicorn
pyodbc
python-dotenv
pandas
openpyxl
httpx
apscheduler==3.10.4
holidays==0.46
pytz
bcrypt
requests
beautifulsoup4
```
<!-- fuente: backend/requirements.txt -->

### 3.2 Dependencias de sistema operativo (contenedor backend)
`unixodbc`, `unixodbc-dev`, `msodbcsql18` (driver ODBC 18 de Microsoft para SQL Server, instalado desde el
repositorio oficial de paquetes de Microsoft para Debian 12), y `openssl_legacy.cnf` propio para compatibilidad
TLS con el SQL Server legado de Cubigest.
<!-- fuente: backend/Dockerfile -->

### 3.3 Frontend (`package.json`, íntegro)
Producción: `@dnd-kit/core` ^6.3.1, `@dnd-kit/sortable` ^10.0.0, `@dnd-kit/utilities` ^3.2.2, `clsx` ^2.1.1,
`lucide-react` ^0.577.0, `react`/`react-dom` ^19.2.0, `tailwind-merge` ^3.5.0, `xlsx` ^0.18.5.
Desarrollo: `vite` ^7.3.1, `typescript` ~5.9.3, `tailwindcss` ^3.4.19, `eslint` ^9.39.1, `@vitejs/plugin-react`
^5.1.1, entre otros.
<!-- fuente: frontend/package.json -->

---

## 4. Bases de datos

| Base de datos | Motor | Ubicación | Acceso | Contenido |
|---|---|---|---|---|
| **Base local del SPP** | SQLite 3 | Bind mount `./backend/optifierro_v2.db` en el host TO (`C:\Users\OptiFierro\Desktop\optifierro\backend\optifierro_v2.db`) | Lectura y escritura | 33 tablas (ver Manual Técnico sección 3): usuarios/sesiones, máquinas, hebras, diámetros, restricciones, operadores, planes generados y manuales, averías, sincronización, auditoría |
| **Cubigest (ERP del cliente)** | Microsoft SQL Server | `192.168.1.195:1433`, red LAN de TO | **ESTRICTO SOLO LECTURA** — sin credenciales de escritura configuradas; código exclusivamente `SELECT`/CTE | ITs, viajes, piezas, paquetes/etiquetas, avances de producción, stock de bodega, órdenes de compra, averías de máquina |

**Regla AR-002 (sagrada):** el SPP nunca ejecuta `INSERT`/`UPDATE`/`DELETE`/`DROP`/`ALTER`/`EXEC`/`TRUNCATE`
contra Cubigest. Verificado por revisión íntegra de `backend/database_cubigest.py` (573 líneas): toda consulta
usa `execute_query`, que ejecuta únicamente el texto SQL recibido — y en el código real, todo ese texto SQL es
`SELECT`/`WITH ... SELECT`.

---

## 5. Infraestructura física

- **Servidor anfitrión:** equipo físico en las dependencias de Torres Ocaranza, Windows 11 Pro, con Docker
  Desktop.
- **Ruta de despliegue:** `C:\Users\OptiFierro\Desktop\optifierro`.
- **Red:** LAN corporativa de TO (segmento `192.168.1.x`), con visibilidad directa a Cubigest
  (`192.168.1.195`) y al servicio GeoVictoria (`192.168.1.111:8002`).
- **Puertos publicados en el host** (verificado en vivo, `docker compose ps`): frontend `3001`→80, backend
  `8001`→8000, Ollama `11434`→11434. Estos mapeos **no están en `docker-compose.yml`** (que no declara bloque
  `ports:`) — su origen exacto (override local, configuración manual de Docker Desktop) es `POR CONFIRMAR`.
- **Recursos de hardware (CPU/RAM/disco) del host:** `POR CONFIRMAR` — no se tuvo acceso de solo lectura al
  panel de recursos de Docker Desktop ni a `systeminfo` de Windows durante esta redacción.

---

## 6. Infraestructura cloud

**No se evidencia uso de infraestructura cloud pública para la ejecución en tiempo real (runtime) del SPP.**
El sistema corre íntegramente **on-premise** en el servidor de TO:
- Backend, frontend y base de datos SQLite: en el mismo host físico de TO.
- Ollama (normalización de texto libre de averías con IA): también corre **local**, en el contenedor
  `optifierro-ollama` del mismo servidor — no se detectó ninguna llamada a una API de IA en la nube
  (OpenAI, Anthropic, Google, etc.) en el código del backend.
- Cubigest y GeoVictoria: sistemas de terceros en la misma LAN de TO, no en la nube.

Lo único potencialmente relacionado con "nube" es el repositorio de código fuente, alojado en GitHub
(`RodMontu/Optifierro-V2`) — esto es control de versiones, no parte del runtime de producción.

- **Repositorio remoto:** GitHub, `origin` apunta a `RodMontu/Optifierro-V2` (rama `master` es la productiva;
  `main` existe mapeada como `origin/HEAD` pero no se usa como rama de trabajo real — ver Índice de Entrega).
- **Acceso remoto de soporte:** se opera vía SSH hacia el servidor de TO (alias `TO` en la configuración SSH del
  equipo de Montu) — esto es acceso de mantenimiento, no un componente cloud del propio SPP. Detalles de
  túnel/VPN exactos: `POR CONFIRMAR`.

---

## 7. Dependencias con otros sistemas

| Sistema | Tipo de dependencia | Detalle |
|---|---|---|
| **Cubigest (ERP)** | SQL directo (solo lectura) + scraper web | `pyodbc` contra `192.168.1.195:1433` para ITs/piezas/stock/averías; scraper HTTP+BeautifulSoup4 contra el portal IIS (`http://192.168.1.195`) para el Cuadro de Programación OptiSteel |
| **OptiSteel** | Módulo de Cubigest, no sistema separado | Provee el programa maestro de fabricación (Cuadro de Programación) que alimenta la Bolsa de Trabajo |
| **GeoVictoria** | API/scraper HTTP | `http://192.168.1.111:8002`, invocado automáticamente 08:08/20:08 (scraper) y consultado para presencia y tardíos |
| **Red LAN de Torres Ocaranza** | Infraestructura | La disponibilidad del SPP para leer Cubigest/GeoVictoria depende de la estabilidad de esta red interna |

---

## 8. Riesgos normativos

> **Declaración de alcance:** no se emite ninguna afirmación de cumplimiento legal ni certificación
> reglamentaria en este documento. Se listan únicamente los hechos operativos verificables en el código; la
> evaluación jurídica queda explícitamente abierta.

| Materia | Hecho operativo verificado en código | Estado |
|---|---|---|
| Control de jornada y descansos | El SPP aplica una tolerancia de ±15 minutos sobre la marca real de GeoVictoria para resolver el horario efectivo de turno, y descuenta colación fija (13:00–14:00 día, 01:00–02:00 noche) al calcular capacidad en minutos-hombre (`_calcular_capacidad_mh`, `motor_v2.py`) | `POR CONFIRMAR con TO / asesoría legal` |
| Régimen de 42 horas / turnos dinámicos (2026) | Los datos históricos de planta muestran una alteración de la duración de turnos desde el 01-03-2026 (documentado en `FASE3_CENSURADA_20260913.md`, referenciado en `MAPA_DECISIONES_SPP.md`); Montu decidió el 23-09-2026 tratar ese régimen como población estadística separada al calibrar el Motor, pendiente de codificación (B26-B) | `POR CONFIRMAR con TO / asesoría legal` |
| Almacenamiento de datos de asistencia de colaboradores | La tabla local `turnos_programados` almacena RUT, nombre, turno y horario de colaboradores importados desde GeoVictoria, en la base SQLite del servidor de TO (sin cifrado a nivel de columna verificado en el código) | `POR CONFIRMAR con TO / asesoría legal` |
| Autoridad sobre seguridad de planta | El Motor calcula asignaciones según capacidades teóricas y restricciones dimensionales cargadas en `restricciones`/`RESTRICCIONES_*`; no hay en el código ningún mecanismo de override de seguridad — cualquier detención de emergencia o inhabilitación por prevención de riesgos es una decisión operativa de planta, fuera del sistema | `POR CONFIRMAR con TO / asesoría legal` |

---

## 9. Normativas aplicables

Se listan como preguntas abiertas, no como afirmaciones de cumplimiento — ninguna fue verificada en código ni
en documento de Montu con carácter legal:

- Código del Trabajo de Chile (jornada, descansos, colación): `POR CONFIRMAR con TO / asesoría legal`.
- Reglamentación de la Dirección del Trabajo sobre control de asistencia digital: `POR CONFIRMAR con TO /
  asesoría legal`.
- Ley de reducción de jornada laboral (régimen de 42 horas, vigente en Chile desde 2024 con implementación
  gradual): impacto en la parametrización de turnos y capacidad — `POR CONFIRMAR con TO / asesoría legal`.
- Normativa de protección de datos personales aplicable al almacenamiento de RUT y registros de asistencia:
  `POR CONFIRMAR con TO / asesoría legal`.
- NCh204 u otra norma técnica de acero para hormigón armado: el sistema usa la fórmula de peso lineal nominal
  `kg/m = diámetro² / 162` para estimar peso por barra (`PRO-02`, `MAPA_DECISIONES_SPP.md`); el grado de
  alineación de esta fórmula con NCh204 y su suficiencia para fines de calidad/certificación no fue evaluado:
  `POR CONFIRMAR con TO / asesoría legal`.

---

## 10. Variables de entorno (`.env` del backend) — solo nombres y propósito, nunca valores

| Variable | Propósito |
|---|---|
| `DB_SERVER` | Host/IP del SQL Server de Cubigest |
| `DB_NAME` | Nombre de la base de datos Cubigest a conectar |
| `DB_USER` | Usuario de conexión ODBC a Cubigest (solo lectura por diseño de credenciales) |
| `DB_PASSWORD` | Contraseña del usuario anterior — **nunca documentar su valor** |
| `OLLAMA_URL` | URL del servicio Ollama para normalización de texto de averías (sobrescrita en runtime por `docker-compose.yml` a `http://host.docker.internal:11434`, tiene prioridad sobre el valor en `.env`) |
| `GEOVICTORIA_API_URL` | URL base del servicio GeoVictoria (default en código: `http://192.168.1.111:8002`) |
| `SYNC_HORARIO_ACTIVO` | `1`/`0` — enciende o apaga el job de sincronización horaria (Sección 5 del Manual Técnico). Verificado en vivo el 2026-09-28: está en `1` |
| `SYNC_HORARIO_CRON` (opcional, no siempre presente) | Permite sobrescribir el cron por defecto del sync horario (`*/30` entre 06–22h, L-S) con una expresión crontab propia |
| `SYNC_DESACTUALIZADO_MIN` (opcional, código de `routers/sync.py`) | Minutos tras los cuales una fuente se considera desactualizada en `GET /api/sync/estado` (default 90 en código si no está seteada) |

<!-- fuente: en vivo, grep -oE nombres de variable de backend/.env (sin valores), TO, 2026-09-28; backend/routers/sync.py -->

---

## 11. Parámetros operativos pendientes de formalización

- RTO/RPO ante caída del servidor anfitrión: `POR CONFIRMAR`.
- Política formal de respaldo de `optifierro_v2.db`: **no se evidencia respaldo automatizado** (ver Manual
  Técnico sección 9); existe una recomendación no implementada, pendiente de decisión de Montu/TO.
- Especificaciones de hardware del host (CPU/RAM/disco): `POR CONFIRMAR`.
- Integración con directorio corporativo (LDAP/Active Directory) para autenticación: hoy el SPP usa
  autenticación local propia (`usuarios`, `bcrypt`, roles `SuperAdmin`/`JefePlanta`/`Visualizador`); integración
  a un directorio central no existe en el código — `POR CONFIRMAR` si es un requisito de TO.
