# Ficha Formulario Técnico (A12) — Sistema Planificador de la Producción (SPP)

**Identificador de Requerimiento:** A12  
**Nombre Oficial del Sistema:** Sistema Planificador de la Producción (SPP / "el Planificador")  
**Cliente / Destinatario:** Torres Ocaranza (TO)  
**Fecha de Emisión:** 24 de septiembre de 2026  
**Criticidad del Sistema:** **MEDIA** (definida en el Plan de Trabajo)  
**Estado:** Documento de Entrega — Hechos verificados en repositorio e infraestructura

---

## 1. Identificación General

| Campo | Detalle Técnico | Estado de Verificación |
|---|---|---|
| **Nombre Oficial** | Sistema Planificador de la Producción (SPP) | Verificado en código y documentación |
| **Nombre Técnico Interno de Repositorio** | `optifierro` | Verificado en git |
| **Cliente / Entidad Receptora** | Torres Ocaranza (TO) | Verificado |
| **Plantas de Aplicación** | Cerrillos (Santiago), Calama y Coronel | Verificado en configuración de sucursales |
| **Nivel de Criticidad Operativa** | **MEDIA** | Verificado (compromiso A12 del backlog) |
| **Propietario / Responsable Técnico** | Rodrigo Montuschi ("Montu") | Verificado |
| **Usuarios Finales** | Jefes de Planta, Supervisores, Gerencia de Operaciones y Gerencia de Logística | Verificado |

---

## 2. Stack Técnico y Lenguajes

| Componente | Tecnología / Versión | Propósito en el Sistema |
|---|---|---|
| **Backend Runtime** | Python 3.11-slim (Debian 12 Bookworm) | Ejecución del servidor de API, optimizador y tareas programadas |
| **Framework Web Backend** | FastAPI (ASGI con Uvicorn) | Exposición de endpoints REST para la interfaz de usuario y automatización |
| **Frontend Framework** | React 19.2.0 | Construcción de la interfaz de usuario interactiva (SPA) |
| **Lenguaje Frontend** | TypeScript ~5.9.3 | Tipado estático y lógica de componentes del cliente |
| **Estilos y Maquetación** | TailwindCSS 3.4.19 + PostCSS + Autoprefixer | Diseño responsivo de pantallas, Gantt y gestores |
| **Herramienta de Compilación Frontend** | Vite 7.3.1 | Empaquetado y construcción de assets estáticos |
| **Servidor Web Frontend** | Nginx Alpine (en contenedor Docker) | Servidor de archivos estáticos y proxy inverso hacia el backend |
| **Gestor de Tareas Asíncronas** | APScheduler 3.10.4 (`AsyncIOScheduler`) | Automatización de corridas del motor (08:10/20:10), scrapers y monitoreo |
| **Manipulación de Datos** | Pandas 2.x, openpyxl | Procesamiento de matrices de tiempos y lectura de planillas de configuración |
| **Interacción con Interfaz Gráfica** | `@dnd-kit/core` 6.3.1, `@dnd-kit/sortable` 10.0.0 | Manejo del drag & drop de cajitas en la Carta Gantt interactiva |

---

## 3. Dependencias del Software

### 3.1 Dependencias Backend (`requirements.txt`)
- `fastapi`: Framework web moderno y de alto rendimiento.
- `uvicorn`: Servidor ASGI para ejecución de FastAPI.
- `pyodbc`: Conexión ODBC a base de datos Microsoft SQL Server (Cubigest).
- `python-dotenv`: Carga de variables de entorno desde archivo `.env`.
- `pandas`: Procesamiento analítico y estructuración tabular de datos.
- `openpyxl`: Lectura y procesamiento de archivos Excel de ingeniería y restricciones.
- `httpx`: Cliente HTTP asíncrono para comunicación con servicios locales (GeoVictoria).
- `apscheduler==3.10.4`: Programador de tareas cron en segundo plano.
- `holidays==0.46`: Detección de feriados nacionales oficiales de Chile.
- `pytz`: Manejo de zonas horarias (`America/Santiago`).
- `bcrypt`: Encriptación unidireccional y verificación segura de contraseñas de usuarios.
- `requests`: Cliente HTTP síncrono para scrapers web.
- `beautifulsoup4`: Análisis y extracción sintáctica de páginas HTML de Cubigest.

### 3.2 Dependencias de Sistema Operativo en Contenedor Backend
- `msodbcsql18` (ODBC Driver 18 for SQL Server de Microsoft).
- `unixodbc` y `unixodbc-dev`.
- Archivo de configuración OpenSSL Legacy (`openssl_legacy.cnf`) para compatibilidad con el servidor SQL Server legado.

### 3.3 Dependencias Frontend (`package.json`)
- Producción: `react`, `react-dom`, `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`, `lucide-react`, `clsx`, `tailwind-merge`, `xlsx`.
- Desarrollo: `vite`, `typescript`, `@types/react`, `@types/node`, `tailwindcss`, `eslint`.

---

## 4. Bases de Datos

| Base de Datos | Motor / Tecnología | Ubicación / Host | Modo de Acceso | Información Almacenada |
|---|---|---|---|---|
| **Base Local SPP** | SQLite 3 (`optifierro_v2.db`) | Servidor TO (volumen local `/app/optifierro_v2.db`) | Lectura y Escritura | Usuarios, contraseñas encriptadas, roles, máquinas activas, hebras por diámetro, restricciones físicas, horarios de jornada, planes guardados (`programacion_guardada`), reasignaciones manuales y logs de auditoría. |
| **Base ERP Cubigest** | Microsoft SQL Server | Servidor de producción TO (`192.168.1.195:1433`) | **ESTRICTO SOLO LECTURA** | Catálogo de ITs, viajes, detalles de paquetes/etiquetas (`DetallePaquetesPieza`), piezas, avances de producción en planta, stock en bodega y materias primas. |

---

## 5. Infraestructura Física y Cloud

### 5.1 Infraestructura Física (On-Premise)
- **Servidor Anfitrión:** Estación/Servidor de producción ubicado físicamente en las instalaciones de Torres Ocaranza.
- **Sistema Operativo del Host:** Windows 11 Pro.
- **Capa de Virtualización / Contenedores:** Docker Desktop con Docker Compose versión 3.8.
- **Topología de Red:** Conexión a la red LAN corporativa de Torres Ocaranza (segmento `192.168.1.x`), con visibilidad directa hacia el servidor de base de datos de Cubigest y servidores de servicios internos.
- **Recursos de Hardware Asignados:** `POR CONFIRMAR` (especificaciones exactas de CPU/RAM del host de TO).

### 5.2 Infraestructura Cloud
- **Servicios Cloud en Producción Directa:** `POR CONFIRMAR` (no se evidencia uso de infraestructura cloud para la ejecución directa del SPP en Torres Ocaranza; opera íntegramente de manera local on-premise).
- **Repositorio de Código Fuente:** Repositorio Git centralizado (`origin/master`). Servicio exacto de hosting remoto: `POR CONFIRMAR`.
- **Túneles de Soporte / Acceso Remoto Seguro:** Servicio SSH para mantenimiento y soporte técnico. Configuración de túneles externos: `POR CONFIRMAR`.

---

## 6. Dependencias con Otros Sistemas e Integraciones

1. **Cubigest ERP (Sistema Central de Producción de Acero de TO):**
   - *Dependencia de Base de Datos:* Consulta directa vía ODBC a tablas transaccionales de fabricación en modo solo lectura.
   - *Dependencia Web:* Conexión HTTP al portal IIS (`http://192.168.1.195`) para extracción del Cuadro de Programación OptiSteel (`CuadroProgramacionPr.aspx`), exportación de piezas (`DescargarOptistel.aspx`) y cuadre de stock contable (`MP_Inet.aspx`).
2. **OptiSteel (Módulo de Despiece y Programación de TO):**
   - Provee la ordenación de trabajos liberados para fabricación en el horizonte semanal y diario.
3. **GeoVictoria (Control de Asistencia Biométrico):**
   - Servicio API/Scraper local en `http://192.168.1.111:8002` invocado automáticamente a las 08:08 y 20:08 para obtener las marcas de entrada de los operadores en cada sucursal.
4. **Infraestructura de Red LAN de Torres Ocaranza:**
   - La operación ininterrumpida del SPP depende de la estabilidad de la red local para alcanzar el motor SQL Server y el servicio GeoVictoria.

---

## 7. Riesgos Normativos y Cumplimiento

> **DECLARACIÓN DE ALCANCE:**  
> En cumplimiento de las directrices de entrega, en esta sección **no se emite afirmación de cumplimiento legal ni certificación reglamentaria**. Se detallan los aspectos operativos que inciden en materias normativas para su debida validación formal:

| Materia Normativa | Aspecto Operativo en el SPP | Estado de Revisión |
|---|---|---|
| **Control de Jornada Laboral y Descansos** | El SPP lee marcaciones biométricas de GeoVictoria y aplica una regla de tolerancia operativa de \(\pm\)15 minutos respecto a la jornada contractual, además de descontar una hora rígida de colación (13:00–14:00 día, 01:00–02:00 noche). La conformidad de estos filtros respecto a la doctrina de la Dirección del Trabajo (DT) requiere revisión. | `POR CONFIRMAR CON MONTU` |
| **Ley de 40 Horas (Reducción de Jornada en Chile)** | El historial de datos de planta evidenció una alteración en la duración de turnos a contar del 01-03-2026 (régimen de 42 horas y turnos dinámicos). El impacto normativo en la parametrización de turnos futuros debe coordinarse con RRHH de TO. | `POR CONFIRMAR CON MONTU` |
| **Protección de Datos Personales de Operarios** | La base de datos local SQLite almacena RUT, nombre y registros horarios de los trabajadores de planta extraídos de GeoVictoria para efectos de asignación de turnos. Las medidas de resguardo conforme a la legislación de protección de datos personales requieren validación. | `POR CONFIRMAR CON MONTU` |
| **Seguridad de la Máquina y Prevención de Riesgos** | El optimizador calcula tiempos y asigna piezas según capacidades teóricas y restricciones dimensionales ingresadas. La detención de emergencia o inhabilitación por seguridad laboral prima sobre cualquier plan y es potestad de planta. | `POR CONFIRMAR CON MONTU` |

---

## 8. Normativas Técnicas y Aplicables

- **Legislación Laboral Chilena (Código del Trabajo):** Normas sobre jornada de trabajo ordinaria, descansos entre turnos, descanso dominical y colación. `POR CONFIRMAR CON MONTU`.
- **Reglamentación de Control de Asistencia (Dirección del Trabajo):** Estándares de interoperabilidad y consulta de registros de asistencia digital. `POR CONFIRMAR CON MONTU`.
- **Normas Técnicas del Acero para Hormigón Armado (p. ej. NCh204):** El software utiliza la formulación técnica de peso lineal nominal para barra con resaltes (\(\text{kg/m} = \text{diámetro}^2 / 162\)). El alcance de certificación técnica del software ante auditores de calidad de TO queda: `POR CONFIRMAR CON MONTU`.

---

## 9. Parámetros Operativos Pendientes de Formalización

- **RTO / RPO (Tiempos de Recuperación ante Desastres):** `POR CONFIRMAR`.
- **Política de Respaldo Automatizado del Archivo `optifierro_v2.db`:** `POR CONFIRMAR`.
- **Procedimiento de Alta / Baja de Usuarios Centralizado (LDAP/Active Directory):** Actualmente opera con autenticación local mediante roles gestionados en pantalla de Administración; integración a directorio corporativo: `POR CONFIRMAR`.
