# CLAWDIO — Asistente Personal IA
## Documentación Técnica Completa

**Archivo:** `/mnt/extra/DOCUMENTOS_TECNICOS/CLAWDIO_ASISTENTE_PERSONAL.md`
**Última actualización:** 2026-05-24
**Mantenedor:** Montu (Rodrigo Montuschi)

---

## 1. Resumen Ejecutivo

Clawdio es el asistente personal IA de Rodrigo Montuschi (Montu) y Anastasia Rivera (Pecas), operando como bot Telegram (`@pantero_bot`) sobre la infraestructura privada en **serveri3** (192.168.1.211). No es un servicio en la nube: corre localmente, tiene acceso a los calendarios y correos de ambos usuarios, gestiona una base de datos de deberes e ideas, lleva la lista del supermercado Lider, transcribe voz, y monitorea la infraestructura TI del hogar.

**Framework:** Hermes Agent v0.14.0 — Docker (contenedor: clawdio-v2)
**Bot Telegram:** @pantero_bot
**Modelo principal:** gemini-3-flash-preview (Gemini API key directa, ~$3/mes)
**Usuarios autorizados:** Montu (ID: 8357148621) + Pecas (ID: 8328037199)
**Hosting:** serveri3 — 192.168.1.211, Docker (imagen: nousresearch/hermes-agent:latest)
**Directorio host:** `/home/i3/clawdio-v2/` | Path interno contenedor: `/opt/data/`
**Estado:** OPERATIVO

---

## 2. Arquitectura y Stack Técnico

### 2.1 Diagrama de componentes

```
Telegram (usuarios) ─── @pantero_bot ──────────────────────────────────────┐
                                                                             │
serveri3 (192.168.1.211)                                                     │
├── Docker: contenedor clawdio-v2  ◄────────────────────────────────────────┘
│   ├── Imagen: nousresearch/hermes-agent:latest
│   ├── Hermes Agent v0.14.0
│   ├── Path interno: /opt/data/
│   ├── Modelo: gemini-3-flash-preview (Gemini API directa)
│   ├── Terminal backend: local (dentro del contenedor)
│   ├── SSH → serverX: /opt/data/.ssh/id_ed25519 (fix: -F /dev/null)
│   ├── Fallback 1: nvidia/nemotron-3-super-120b-a12b:free (OpenRouter)
│   └── Fallback 2: llama3.1:8b (Ollama en serverX :11434)
│
├── stt-proxy.service (Flask, puerto 9877) — servicio nativo en serveri3
│   └── Endpoint OpenAI-compat para transcripción de voz
│
├── /home/i3/clawdio-v2/           ← directorio host
│   ├── docker-compose.yml
│   └── .env                       ← GEMINI_API_KEY + secrets
│
├── Volúmenes Docker nombrados:
│   ├── clawdio_home → /opt/data/
│   ├── clawdio_skills → /opt/data/skills/
│   └── clawdio_memory → /opt/data/memory/
│
└── Google Workspace credentials
    ├── /opt/data/accounts/montu/   — ce3wkc@gmail.com
    ├── /opt/data/accounts/pecas/   — rivera.melgarejo@gmail.com
    └── /opt/data/ (default)        — rodrigo@montuschi.cl

serverX (192.168.1.111)
└── ollama :11434 ── llama3.1:8b  (fallback LLM para Clawdio)

MacBook Pro (Montu)
└── ~/hermes-mcp-bridge-v2  → SSH → docker exec -i -u hermes clawdio-v2 hermes mcp serve
    └── Claude Desktop MCP server "clawdio" — estado: RUNNING
```

### 2.2 Stack de modelos

| Slot | Modelo | Proveedor | Costo est. | Cuándo activa |
|---|---|---|---|---|
| Principal | `gemini-3-flash-preview` | Gemini API key directa | ~$3/mes | Siempre (default) |
| Fallback 1 | `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | $0 | Si Gemini falla |
| Fallback 2 | `llama3.1:8b` | Ollama en serverX :11434 | $0 | Si OpenRouter falla |

Nota (2026-05-24): Migrado de gemini-2.5-flash-preview a gemini-3-flash-preview.
Provider: Gemini API directa (no OpenRouter). Model ID sin prefijo google/.

Config en `config.yaml`:
```yaml
model:
  default: gemini-2.5-flash
  provider: gemini
fallback_providers:
  - provider: openrouter
    model: nvidia/nemotron-3-super-120b-a12b:free
  - provider: ollama
    model: llama3.1:8b
    base_url: http://192.168.1.111:11434/v1
```

### 2.3 Servicios

Rabín 2.0 corre como contenedor Docker, no como servicio systemd.

```bash
# Ver estado del contenedor
ssh i3@192.168.1.211 "docker ps --filter name=clawdio-v2 --format '{{.Names}} {{.Status}}'"

# Ver logs en tiempo real
ssh i3@192.168.1.211 "docker logs clawdio-v2 --tail 50 --follow --no-color"

# Reiniciar (aplica cambios de config)
ssh i3@192.168.1.211 "docker restart clawdio-v2 && sleep 15 && docker ps --filter name=clawdio-v2"

# Detener / iniciar
ssh i3@192.168.1.211 "cd /home/i3/clawdio-v2 && docker compose down"
ssh i3@192.168.1.211 "cd /home/i3/clawdio-v2 && docker compose up -d"

# Health check
ssh i3@192.168.1.211 "docker inspect clawdio-v2 --format '{{.State.Health.Status}}'"
```

NOTA: stt-proxy.service sigue corriendo como servicio systemd nativo en serveri3
(no dockerizado). Comandos de gestión sin cambios.

### 2.4 Versiones de dependencias clave

| Paquete | Versión | Rol |
|---|---|---|
| Hermes Agent | v0.12.0 (2026.4.30) | Framework core |
| Python | 3.11.15 | Runtime |
| OpenAI SDK | 2.32.0 | Capa API |
| faster-whisper | 1.2.1 | STT local |
| google-api-python-client | 2.194.0 | Google Workspace |
| google-auth | 2.49.2 | OAuth2 Google |
| requests | 2.33.1 | HTTP |
| Node.js | 20.x | Camofox browser automation |

### 2.5 Archivos clave

| Archivo | Ruta (contenedor) | Ruta (host via docker cp) | Descripción |
|---|---|---|---|
| config.yaml | /opt/data/config.yaml | — | Config principal Hermes |
| SOUL.md | /opt/data/SOUL.md | — | Personalidad y reglas |
| USER.md | /opt/data/USER.md | — | Perfil de Montu |
| MEMORY.md | /opt/data/memories/MEMORY.md | — | Manual operativo |
| supermercado.json | /opt/data/supermercado.json | — | Lista Lider |
| clawdio_db.sqlite | /opt/data/clawdio_db.sqlite | — | DB deberes+ideas+miaude_inbox |
| init_db.py | /opt/data/init_db.py | — | Funciones CRUD Python |
| monitor.sh | /opt/data/scripts/monitor.sh | — | Script monitoreo infra |
| jobs.json | /opt/data/cron/jobs.json | — | Crons (NO en config.yaml) |
| agent_results/ | /opt/data/agent_results/ | — | Canal retorno Miaude↔Rabín |
| write_result.py | /opt/data/agent_results/write_result.py | — | Helper resultados |
| id_ed25519 | /opt/data/.ssh/id_ed25519 | — | SSH key contenedor→serverX |
| skills/ | /opt/data/skills/ | — | 9 skills (cotidianas/infra/ms) |

CRÍTICO — Crons en jobs.json, NO en config.yaml:
```bash
ssh i3@192.168.1.211 "docker exec clawdio-v2 cat /opt/data/cron/jobs.json"
```

---

## 3. Herramientas disponibles (con comandos exactos)

Clawdio tiene acceso a las siguientes herramientas mediante el agente Hermes. Para usarlas internamente desde Python:

```python
import sys; sys.path.insert(0, '/opt/data'); from init_db import *
```

### 3.1 Terminal tool
Ejecuta comandos shell en serveri3. Se usa para:
- Correr `bash /opt/data/scripts/monitor.sh`
- Llamar a `python3 /opt/data/skills/cotidianas/google_api.py`
- Leer archivos con `cat`

### 3.2 File read/write
- Leer: `read_file /opt/data/supermercado.json`
- Escribir: vía `write_file` o `edit_file`

### 3.3 Code execution (execute_code)
Ejecuta Python en el entorno Hermes. Patrón de importación obligatorio:
```python
import sys; sys.path.insert(0, '/opt/data'); from init_db import *
```

### 3.4 Web search / Web fetch
Búsqueda y scraping web. Disponible para Montu y Pecas desde Telegram.

---

## 4. Cuentas Google configuradas

⚠️ NUNCA usar el argumento --account — NO EXISTE en google_api.py.
SIEMPRE usar HERMES_HOME switching para cambiar de cuenta.

Tres cuentas OAuth2 autenticadas. Cada una tiene su propio `HERMES_HOME`:

| Cuenta | Titular | HERMES_HOME | Uso |
|---|---|---|---|
| `rodrigo@montuschi.cl` | Montu | `/opt/data` | Workspace, calendario laboral |
| `ce3wkc@gmail.com` | Montu | `/opt/data/accounts/montu` | Gmail personal, calendario |
| `rivera.melgarejo@gmail.com` | Pecas | `/opt/data/accounts/pecas` | Gmail y calendario Pecas |

**Regla crítica:** cuando Montu pregunta por su agenda sin especificar cuenta, Clawdio consulta AMBAS cuentas de Montu y consolida.

### 4.1 Comandos de calendario

```bash
# Listar eventos — rodrigo@montuschi.cl
HERMES_HOME=/opt/data \
  python3 \
  /opt/data/skills/cotidianas/google_api.py \
  calendar list --start YYYY-MM-DDTHH:MM:SS --end YYYY-MM-DDTHH:MM:SS

# Listar eventos — ce3wkc@gmail.com (personal Montu)
HERMES_HOME=/opt/data/accounts/montu \
  python3 \
  /opt/data/skills/cotidianas/google_api.py \
  calendar list --start YYYY-MM-DDTHH:MM:SS --end YYYY-MM-DDTHH:MM:SS

# Listar eventos — rivera.melgarejo@gmail.com (Pecas)
HERMES_HOME=/opt/data/accounts/pecas \
  python3 \
  /opt/data/skills/cotidianas/google_api.py \
  calendar list --start YYYY-MM-DDTHH:MM:SS --end YYYY-MM-DDTHH:MM:SS

# Crear evento
HERMES_HOME=/opt/data \
  python3 \
  /opt/data/skills/cotidianas/google_api.py \
  calendar create \
  --summary "Título del evento" \
  --start YYYY-MM-DDTHH:MM:SS \
  --end YYYY-MM-DDTHH:MM:SS \
  --location "Dirección o lugar"
```

### 4.2 Comandos de Gmail

```bash
# Buscar no leídos — rodrigo@montuschi.cl
HERMES_HOME=/opt/data \
  python3 \
  /opt/data/skills/cotidianas/google_api.py \
  gmail search "is:unread" --max 10

# Buscar no leídos — ce3wkc@gmail.com
HERMES_HOME=/opt/data/accounts/montu \
  python3 \
  /opt/data/skills/cotidianas/google_api.py \
  gmail search "is:unread" --max 10

# Buscar no leídos — rivera.melgarejo@gmail.com (Pecas)
HERMES_HOME=/opt/data/accounts/pecas \
  python3 \
  /opt/data/skills/cotidianas/google_api.py \
  gmail search "is:unread" --max 10
```

### 4.3 Reglas de autorización Google

| Acción | ¿Requiere autorización explícita? |
|---|---|
| Leer calendario | No — ejecuta directamente |
| Buscar correos | No — ejecuta directamente |
| Crear evento | No si se lo piden directamente |
| Eliminar evento | Sí — pedir confirmación siempre |
| Enviar correo | Sí — autorización explícita de Montu o Pecas |
| Eliminar correo | Sí — autorización explícita |

---

## 5. Base de datos deberes e ideas

**Motor:** SQLite
**Archivo:** `/opt/data/clawdio_db.sqlite`
**Módulo Python:** `/opt/data/init_db.py`

### 5.1 Esquema

**Tabla `deberes`:**
```sql
CREATE TABLE deberes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contenido TEXT NOT NULL,
    tipo TEXT,                          -- tarea|reunion|recordatorio|compromiso|cita
    prioridad TEXT DEFAULT 'media',     -- alta|media|baja
    fecha_creacion DATETIME NOT NULL,
    fecha_ejecucion DATETIME,
    estado TEXT DEFAULT 'pendiente',    -- pendiente|en progreso|completado|cancelado
    usuario TEXT NOT NULL               -- montu|pecas
);
```

**Tabla `ideas`:**
```sql
CREATE TABLE ideas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contenido TEXT NOT NULL,
    contexto TEXT,
    fecha_creacion DATETIME NOT NULL,
    fecha_desarrollo_inicio DATETIME,
    estado TEXT DEFAULT 'nueva',        -- nueva|en desarrollo|archivada|descartada
    usuario TEXT NOT NULL               -- montu|pecas
);
```

**Tabla `miaude_inbox` (canal asíncrono Rabín→Miaude):**
```sql
CREATE TABLE miaude_inbox (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarea TEXT NOT NULL,
    resultado TEXT NOT NULL,
    estado TEXT DEFAULT 'completado',
    leido INTEGER DEFAULT 0,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

Funciones nuevas:
- `guardar_para_miaude(tarea, resultado, estado)` — Rabín escribe resultado entre sesiones
- `leer_inbox_miaude()` — Miaude lee pendientes al inicio de sesión (marca como leído)

### 5.2 Funciones disponibles

```python
import sys; sys.path.insert(0, '/opt/data'); from init_db import *

# Agregar deber
agregar_deber(
    contenido="Llamar al dentista",
    tipo="tarea",           # tarea|reunion|recordatorio|compromiso|cita
    prioridad="alta",       # alta|media|baja
    fecha_ejecucion="2026-05-05 10:00:00",
    usuario="montu"         # montu|pecas
)

# Agregar idea
agregar_idea(
    contenido="App para gestión de turnos",
    contexto="conversación con OptiFierro",
    usuario="montu"
)

# Listar deberes (con filtros opcionales)
listar_deberes(usuario="montu", estado="pendiente", prioridad="alta")

# Listar ideas
listar_ideas(usuario="montu", estado="nueva")

# Listar todo (deberes + ideas)
listar_todo(usuario="montu")

# Resumen del día (deberes de hoy + todos los pendientes)
resumen_dia(usuario="montu")

# Actualizar deber
actualizar_deber(
    id=5,
    estado="completado",
    fecha_ejecucion="2026-05-03 15:00:00",
    prioridad="alta",
    tipo="reunion",
    contenido="Nuevo contenido"
)

# Actualizar idea
actualizar_idea(
    id=3,
    estado="en desarrollo",
    fecha_desarrollo_inicio="2026-05-01 09:00:00"
)
```

### 5.3 Valores válidos

| Campo | Valores |
|---|---|
| `tipo` | `tarea`, `reunion`, `recordatorio`, `compromiso`, `cita` |
| `prioridad` | `alta`, `media`, `baja` |
| `estado` (deberes) | `pendiente`, `en progreso`, `completado`, `cancelado` |
| `estado` (ideas) | `nueva`, `en desarrollo`, `archivada`, `descartada` |
| `usuario` | `montu`, `pecas` |

---

## 6. Lista supermercado Lider

**Archivo:** `/opt/data/supermercado.json`
**Lectura:** siempre con `read_file` con esa ruta exacta (nunca `search_files`)

### 6.1 Estructura del JSON

```json
{
  "productos_habituales": [
    {
      "nombre": "Leche entera",
      "cantidad": "6 litros",
      "categoria": "lacteos"
    }
  ],
  "lista_mes_actual": [
    "Producto extra puntual",
    "Vinagre blanco, bidón de 5 litros"
  ]
}
```

### 6.2 Tipos de productos

| Tipo | Descripción | Dónde se guarda |
|---|---|---|
| `productos_habituales` | Se compran todos los meses, cantidad estándar | Array de objetos con nombre/cantidad/categoría |
| `lista_mes_actual` | Extras puntuales del mes en curso | Array de strings |

### 6.3 Lógica mensual
- Al inicio de cada mes: `lista_mes_actual` se precarga con todos los `productos_habituales`
- Tanto Montu como Pecas pueden agregar productos desde Telegram
- Al agregar: confirmar brevemente "Anotado: [X]."
- Al pedir "dame la lista del mes": entregar contenido completo ordenado, listo para usar en lider.cl

---

## 7. STT — Transcripción de voz

### 7.1 Arquitectura STT

```
Usuario → Voz en Telegram
    ↓
hermes-gateway recibe audio
    ↓
HERMES_LOCAL_STT_COMMAND (env var en stt.conf)
    ↓
stt-local.sh {input_path} {output_dir}
    ↓
faster-whisper (modelo: small, idioma: es, CPU, int8)
    ↓
Transcripción devuelta al agente
```

### 7.2 Componentes

**stt-local.sh** (`/home/i3/.hermes/stt-local.sh`):
```bash
#!/bin/bash
INPUT="$1"
OUTPUT_DIR="$2"
/home/i3/.hermes/hermes-agent/venv/bin/python3 -c "
from faster_whisper import WhisperModel
import sys, os, json

model = WhisperModel('small', device='cpu', compute_type='int8')
segments, info = model.transcribe('$INPUT', language='es', beam_size=5)
text = ' '.join([s.text for s in segments]).strip()

out_file = os.path.join('$OUTPUT_DIR', 'transcript.txt')
with open(out_file, 'w') as f:
    f.write(text)
print(text)
"
```

**stt-proxy.service** (Flask en puerto 9877):
- Endpoint compatible con OpenAI Whisper API
- Usado como adaptador para Visual-Voice y otros clientes
- Unidad: `/home/i3/.config/systemd/user/stt-proxy.service`

**Variable de entorno** (en `stt.conf`):
```
HERMES_LOCAL_STT_COMMAND=/home/i3/.hermes/stt-local.sh {input_path} {output_dir}
```

**Config en `config.yaml`:**
```yaml
stt:
  enabled: true
  provider: local
  local:
    model: small
    language: ''
  openai:
    model: whisper-1
    base_url: http://127.0.0.1:9877/v1
    api_key: local
```

### 7.3 Características del modelo STT
- Modelo: `small` (faster-whisper)
- Device: `cpu`
- Compute type: `int8` (cuantizado, bajo consumo RAM)
- Idioma: `es` (español, forzado)
- Beam size: 5

---

## 8. Monitoreo automático de infraestructura

### 8.1 Script de monitoreo

**Ruta:** `/opt/data/scripts/monitor.sh`

```bash
#!/bin/bash
# Monitor de infraestructura — Clawdio
REPORT=""

# serveri3 (local)
REPORT+="=== serveri3 ===\n"
REPORT+="Uptime: $(uptime -p)\n"
REPORT+="Disco /: $(df -h / | awk 'NR==2{print $3"/"$2" ("$5" usado)"}')\n"
REPORT+="RAM: $(free -h | awk 'NR==2{print $3"/"$2}')\n"
REPORT+="Hermes gateway: $(systemctl --user is-active hermes-gateway.service)\n"
REPORT+="STT proxy: $(systemctl --user is-active stt-proxy.service)\n"

# serverX (remoto vía SSH)
REPORT+="\n=== serverX ===\n"
SX=$(ssh -o ConnectTimeout=5 x@192.168.1.111 '...' 2>/dev/null || echo "serverX no responde")
REPORT+="$SX\n"

# Web montuschi.cl
REPORT+="\n=== Web ===\n"
HTTP=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 5 https://montuschi.cl 2>/dev/null)
REPORT+="montuschi.cl: HTTP $HTTP\n"

echo -e "$REPORT"
```

Métricas recopiladas por servidor:
- **serveri3:** uptime, disco /, RAM, estado servicios hermes-gateway y stt-proxy
- **serverX:** uptime, disco /, RAM, contenedores Docker activos, uso GPU (nvidia-smi)
- **Web:** HTTP status code de montuschi.cl

### 8.2 Crons configurados

⚠️ Los crons NO están en config.yaml. Están en `/opt/data/cron/jobs.json`

```bash
ssh i3@192.168.1.211 "docker exec clawdio-v2 cat /opt/data/cron/jobs.json"
```

| ID | Schedule | Timezone | Acción |
|---|---|---|---|
| monitor-manana | 0 8 * * * | America/Santiago | Reporte infra a Montu |
| monitor-noche | 0 20 * * * | America/Santiago | Reporte infra a Montu |
| briefing-manana | 0 9 * * * | America/Santiago | Correos + agenda + pendientes (con retry 503) |
| ideas-pendientes | 0 17 * * 1-5 | America/Santiago | Recordatorio ideas semana (lun-vie) |
| resumen-semanal | 0 10 * * 5 | America/Santiago | Resumen viernes completo |
| inbox-miaude-check | 0 9 * * * | America/Santiago | Verifica resultados pendientes para Miaude |

### 8.3 Ejecución manual

```bash
# Desde dentro del contenedor
bash /opt/data/scripts/monitor.sh

# Desde cualquier host con SSH
ssh i3@192.168.1.211 "docker exec clawdio-v2 bash /opt/data/scripts/monitor.sh"
```

---

## 9. Skills disponibles (Rabín 2.0)

Rabín 2.0 tiene 9 skills organizadas en tres capas:

### Cotidianas (/opt/data/skills/cotidianas/)
| Skill | Archivo | Función |
|---|---|---|
| Deberes e Ideas | deberes-ideas.md | CRUD DB SQLite, captura automática, resumen_dia |
| Google Workspace | google-workspace.md | Gmail + Calendar 3 cuentas con HERMES_HOME switching |
| Supermercado | supermercado.md | Lista Lider, productos habituales, lista_mes_actual |

### Infraestructura (/opt/data/skills/infra/)
| Skill | Archivo | Función |
|---|---|---|
| Monitor Infra | infra-monitor.md | monitor.sh serveri3 + serverX, prompts imperativos |
| Docker Check | infra-docker-check.md | Estado y logs de contenedores vía SSH a serverX |

### Metodología Sinérgica (/opt/data/skills/ms/)
| Skill | Archivo | Función |
|---|---|---|
| Canal Miaude→Rabín | ms-canal-miaude-a-rabin.md | Protocolo recepción instrucciones de Claude |
| Canal Rabín→Miaude | ms-canal-rabin-a-miaude.md | Escritura en agent_results/ y miaude_inbox |
| Protocolo MS | ms-protocolo-comunicacion.md | Jerarquía agentes, reglas cardinales MS v3.0 |
| Doc Updater | ms-doc-updater.md | Actualizar LOG_CAMBIOS + INVENTARIO vía SSH+git |
| Handoff Reader | ms-handoff-reader.md | Leer handoff_actual.md desde GitHub raw |

---

## 10. Personalidad y comportamiento (SOUL.md)

**Archivo:** `/opt/data/SOUL.md`
**Cargado como:** `system_prompt` en `config.yaml` + personalidad `clawdio`

### 10.1 Identidad core

Clawdio es un colaborador inteligente con criterio propio, no un bot servil. Opera en infraestructura privada de la pareja. Cuando no sabe algo, lo dice sin rodeos.

### 10.2 Idioma y tono

- **Idioma:** Español chileno culto-informal siempre (incluso si el usuario escribe en otro idioma)
- **Prohibido:** "puta", "cacho", "brigido", "pifia", "condoro", "al tiro"
- **Sin:** emojis celebratorios, adulación, "¡Claro que sí!", inventar información

### 10.3 Con Montu
- Lo llama "Montu" (nunca "Rodrigo" ni "jefe")
- Tono: directo, técnico, sin relleno — como colega que sabe lo que hace
- Captura automáticamente tareas e ideas mencionadas al pasar → "Capturado: [X]."
- Revisión de agenda proactiva al inicio de jornada cuando Montu lo indica

### 10.4 Con Pecas
- La llama "Pecas" (nunca "Anastasia")
- Tono: directo, cercano, cariñoso — sin tecnicismos
- Explicaciones muy breves por defecto; amplía si ella pide
- Apoyo proactivo en búsqueda de empleo: recordatorios de postulaciones, seguimiento
- Respeta que es más organizada que Montu

### 10.5 Captura de información
- Tareas, ideas, recordatorios, compromisos: captura siempre, sin que se lo pidan
- Confirma con mensaje breve: "Anotado: [X]."
- Nunca pierde información mencionada al pasar

### 10.6 Espacio compartido
- Lista supermercado, agenda familiar, compromisos comunes: gestionados para ambos
- Cuando cualquiera menciona algo para el hogar, lo registra en el espacio compartido

---

## 11. Memoria operativa (MEMORY.md / USER.md)

### 11.1 MEMORY.md (`/opt/data/memories/MEMORY.md`)

Manual operativo completo cargado en el contexto del agente. Contiene:
- Reglas de tono y comunicación
- Formato de fechas/horas/zona horaria (America/Santiago, UTC-4)
- Comandos exactos de cada herramienta Google
- Patrón de importación DB SQLite
- Ruta exacta de supermercado.json
- Instrucciones del script de monitoreo
- Cuentas configuradas

### 11.2 USER.md (`/opt/data/USER.md`)

Perfil de Montu:
- Ingeniero Civil Industrial, consultor en IA/automatización
- Neurodivergente 2e: TDAH + AACC + TEA + dislexia de transposición
- Prefiere tono culto-informal, nunca excesivamente coloquial
- Usa audio frecuentemente por dislexia — priorizar captura de ideas de audios
- Vive en Santiago de Chile con su esposa Pecas (Anastasia Rivera)
- Proyectos activos: OptiFierro, Pegas V2, Visual-Voice, OP RISK

### 11.3 Config de memoria en Hermes

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  memory_char_limit: 2200
  user_char_limit: 1375
  nudge_interval: 10
  flush_min_turns: 6
session_reset:
  mode: session           # preserva perfil usuario entre sesiones
  idle_minutes: 1440      # reset tras 24h de inactividad
  at_hour: 4              # reset diario a las 04:00
```

---

## 12. Comandos de operación y mantención

### 12.1 Estado del sistema

```bash
# Estado del contenedor (desde cualquier host con SSH)
ssh i3@192.168.1.211 "docker ps --filter name=clawdio-v2 --format '{{.Names}} {{.Status}}'"

# Estado del stt-proxy (servicio nativo)
ssh i3@192.168.1.211 "systemctl --user status stt-proxy.service --no-pager"
```

### 12.2 Logs

```bash
# Log en tiempo real del contenedor
ssh i3@192.168.1.211 "docker logs clawdio-v2 --tail 100 --follow --no-color"

# Últimas 50 líneas
ssh i3@192.168.1.211 "docker logs clawdio-v2 --tail 50 --no-color"

# Log del STT proxy
ssh i3@192.168.1.211 "journalctl --user -u stt-proxy.service -n 50 --no-pager"
```

### 12.3 Reinicio de servicios

```bash
# Reiniciar contenedor (aplica cambios en config)
ssh i3@192.168.1.211 "docker restart clawdio-v2 && sleep 15 && docker ps --filter name=clawdio-v2"

# Reiniciar STT proxy
ssh i3@192.168.1.211 "systemctl --user restart stt-proxy.service"

# Detener y levantar desde compose
ssh i3@192.168.1.211 "cd /home/i3/clawdio-v2 && docker compose down && docker compose up -d"
```

### 12.4 Edición de archivos clave

```bash
# Editar personalidad/reglas (dentro del contenedor)
ssh i3@192.168.1.211 "docker exec -it clawdio-v2 nano /opt/data/SOUL.md"

# Editar manual operativo
ssh i3@192.168.1.211 "docker exec -it clawdio-v2 nano /opt/data/memories/MEMORY.md"

# Editar perfil usuario
ssh i3@192.168.1.211 "docker exec -it clawdio-v2 nano /opt/data/USER.md"

# Ver DB SQLite directamente
ssh i3@192.168.1.211 "docker exec -it clawdio-v2 sqlite3 /opt/data/clawdio_db.sqlite"
# .tables
# SELECT * FROM deberes ORDER BY fecha_creacion DESC LIMIT 10;
# SELECT * FROM ideas ORDER BY fecha_creacion DESC LIMIT 10;
# .quit
```

### 12.5 Actualización de Hermes

```bash
# Ver versión actual
ssh i3@192.168.1.211 "docker exec clawdio-v2 hermes --version"

# Actualizar imagen
ssh i3@192.168.1.211 "cd /home/i3/clawdio-v2 && docker compose pull && docker compose up -d"
```

### 12.6 Gestión de crons

```bash
# Ver crons activos en jobs.json
ssh i3@192.168.1.211 "docker exec clawdio-v2 cat /opt/data/cron/jobs.json"

# Editar crons
ssh i3@192.168.1.211 "docker exec -it clawdio-v2 nano /opt/data/cron/jobs.json"
# Reiniciar para aplicar
ssh i3@192.168.1.211 "docker restart clawdio-v2"
```

### 12.7 Verificar Google Auth

```bash
# Test calendario rodrigo@montuschi.cl
ssh i3@192.168.1.211 "docker exec clawdio-v2 bash -c 'HERMES_HOME=/opt/data python3 /opt/data/skills/cotidianas/google_api.py calendar list --start $(date -u +%Y-%m-%dT00:00:00) --end $(date -u -d \"+7 days\" +%Y-%m-%dT00:00:00)'"

# Test calendario ce3wkc@gmail.com
ssh i3@192.168.1.211 "docker exec clawdio-v2 bash -c 'HERMES_HOME=/opt/data/accounts/montu python3 /opt/data/skills/cotidianas/google_api.py calendar list --start $(date -u +%Y-%m-%dT00:00:00) --end $(date -u -d \"+7 days\" +%Y-%m-%dT00:00:00)'"
```

### 12.8 Backup manual de la DB

```bash
# Backup SQLite desde contenedor a host
ssh i3@192.168.1.211 "docker cp clawdio-v2:/opt/data/clawdio_db.sqlite /home/i3/backups/clawdio_db.sqlite.$(date +%Y%m%d)"

# Copiar a serverX
ssh i3@192.168.1.211 "scp /home/i3/backups/clawdio_db.sqlite.$(date +%Y%m%d) x@192.168.1.111:/mnt/extra/backups/"
```

### 12.9 SSH key del contenedor a serverX

La key se genera dentro del contenedor y persiste en el volumen clawdio_home.

```bash
# Ver key pública
ssh i3@192.168.1.211 "docker exec clawdio-v2 cat /opt/data/.ssh/id_ed25519.pub"

# Verificar que está en authorized_keys de serverX
ssh x@192.168.1.111 "grep clawdio ~/.ssh/authorized_keys"

# Test de conexión (debe funcionar sin password)
ssh i3@192.168.1.211 "docker exec clawdio-v2 ssh -F /dev/null -i /opt/data/.ssh/id_ed25519 -o StrictHostKeyChecking=no x@192.168.1.111 'echo OK'"
```

NOTA: SSH desde el contenedor hacia serveri3 (su propio host 192.168.1.211)
NO está disponible y NO es necesario. Comportamiento esperado — no reportar como falla.

---

## 13. Guía de uso para Montu

### 13.1 Acceso
- **Bot Telegram:** `@pantero_bot`
- **ID Telegram:** 8357148621
- **Voz:** Graba audio en Telegram — faster-whisper transcribe automáticamente

### 13.2 Comandos y frases de uso frecuente

**Agenda:**
- "¿Qué tengo mañana?" → consulta ambas cuentas de calendario
- "Crea un evento: reunión OptiFierro el martes a las 10" → crea en rodrigo@montuschi.cl
- "¿Qué correos no leídos tengo?" → busca en ambas cuentas Gmail

**Tareas e ideas:**
- "Tengo que llamar al dentista el viernes" → agrega deber automáticamente
- "Idea: app para X" → agrega idea automáticamente
- "¿Qué tengo pendiente?" → `listar_deberes(estado='pendiente')`
- "Dame el resumen del día" → `resumen_dia(usuario='montu')`
- "Marca el deber 5 como completado" → `actualizar_deber(5, estado='completado')`

**Supermercado:**
- "Agrega aceite de oliva a la lista" → agrega a lista_mes_actual
- "Dame la lista del mes" → muestra lista completa para lider.cl

**Infraestructura:**
- "Cómo está la infra?" → ejecuta monitor.sh y reporta

### 13.3 Captura automática
Clawdio captura tareas e ideas mencionadas al pasar durante cualquier conversación y notifica brevemente: "Anotado: [X]."

---

## 14. Guía de uso para Pecas

### 14.1 Acceso
- **Bot Telegram:** `@pantero_bot`
- **ID Telegram:** 8328037199

### 14.2 Comandos y frases de uso frecuente

**Agenda:**
- "¿Qué tengo esta semana?" → consulta calendario rivera.melgarejo@gmail.com
- "Crea un evento: cita médica el jueves a las 15:30"
- "¿Tengo correos importantes?"

**Tareas:**
- "Tengo que llevar los papeles el lunes" → agrega deber con `usuario='pecas'`
- "¿Qué tengo pendiente?" → lista sus deberes
- "Listo el deber 3" → marca como completado

**Supermercado (compartido con Montu):**
- "Agrega yogur griego a la lista" → agrega a lista_mes_actual (compartida)
- "¿Qué hay en la lista del super?"

**Búsqueda de empleo (soporte proactivo):**
- "Postulé a X empresa hoy" → agrega como deber de seguimiento
- "¿Cuándo debo hacer seguimiento de mis postulaciones?"
- Clawdio puede recordarle hacer seguimiento de postulaciones activas

### 14.3 Estilo de interacción
- Las respuestas son breves por defecto
- Sin tecnicismos
- Si necesita más detalle, pedirlo explícitamente
- Clawdio usa `usuario='pecas'` automáticamente cuando reconoce que es ella quien escribe

---

## 15. Pendientes técnicos

| Prioridad | ID | Pendiente | Contexto |
|---|---|---|---|
| Alta | BACKLOG-RABIN-01 | Webhook HTTP canal Miaude→Rabín autónomo | MCP actual solo permite Miaude→Montu. Para instrucciones directas a Rabín se necesita endpoint HTTP en serveri3 que inyecte mensajes en Hermes |
| Media | — | Re-autenticar Google OAuth en contenedor | Las credenciales se migraron desde Rabín 1.x. Pueden expirar — re-autenticar si falla Calendar/Gmail |
| Baja | — | Login manual Lider.cl via Camofox | Camofox instalado en serveri3 pero requiere sesión autenticada inicial |
| Baja | — | Agregar productos habituales a supermercado.json | Lista de productos pendiente de cargar |
| Baja | — | WARP enrollment Mac Pecas | Requiere acceso físico |

---

## 16. Historial de cambios relevantes

### 2026-05-17 al 2026-05-24 — Rabín 2.0: migración a Docker

- Hermes v0.12.0 (systemd) → v0.14.0 (Docker, contenedor clawdio-v2)
- Directorio host: /home/i3/clawdio-v2/ | Path contenedor: /opt/data/
- Modelo: gemini-2.5-flash → gemini-3-flash-preview (Gemini API directa)
- 9 skills creadas: cotidianas (3) + infra (2) + MS (5)
- Tabla miaude_inbox agregada a SQLite (canal asíncrono Miaude↔Rabín)
- SSH key contenedor→serverX con fix -F /dev/null (permisos hermes/root)
- briefing-manana: retry automático ante HTTP 503
- MCP bridge v2 activo: ~/hermes-mcp-bridge-v2 en Claude Desktop
- /sethome configurado: canal home = Rodrigo Montuschi (8357148621)
- Crons en /opt/data/cron/jobs.json (descubierto en producción — no en config.yaml)
- SOUL.md: limitación SSH a serveri3 documentada

### 2026-04-25 al 2026-05-01 — Implementación completa

- Hermes Agent v0.11.0 instalado en serveri3, gateway como user service systemd con linger habilitado
- Bot Telegram @pantero_bot activo con 2 usuarios autorizados (Montu + Pecas)
- Stack de modelos: Gemini 2.5 Flash (principal) + Nemotron free (fallback 1) + llama3.1:8b local en serverX (fallback 2)
- SOUL.md creado: personalidad Clawdio con tono culto-informal, reglas por usuario, español chileno
- Google Workspace OAuth2: 3 cuentas autenticadas (rodrigo@montuschi.cl, ce3wkc@gmail.com, rivera.melgarejo@gmail.com)
- supermercado.json: estructura base creada (productos_habituales + lista_mes_actual)
- DB SQLite: init_db.py con funciones CRUD completas para deberes e ideas
  - Funciones agregadas: `listar_todo()`, `resumen_dia()` (2026-04-30)
- STT voz: faster-whisper 1.2.1 instalado en venv, stt-local.sh wrapper operativo
- stt-proxy.service: Flask en puerto 9877 como adaptador OpenAI-compat
- Monitoreo automático: monitor.sh + 2 crons Hermes (08:00 y 20:00 America/Santiago)
- MEMORY.md y USER.md creados con manual operativo completo
- `session_reset.mode` cambiado de `both` a `session` → preserva perfil usuario entre sesiones
- Pasos intermedios suprimidos en Telegram: `tool_progress: none` para plataforma telegram
- Node.js 20.x instalado para soporte Camofox browser automation
- ByteRover CLI v3.10.0 instalado pero desactivado como provider (incompatibilidad con Gemini 2.5 Flash)

### Antes de Hermes (pre 2026-04-25)
- Clawdio operaba sobre OpenClaw (fork de OpenWebUI) en serveri3
- Compose: `/srv/openclaw/openclaw` en serveri3
- Migración a Hermes motivada por mayor flexibilidad de herramientas y mejor integración Telegram

---

*Fin del documento — act. 2026-05-24 — Rabín 2.0 Docker*
