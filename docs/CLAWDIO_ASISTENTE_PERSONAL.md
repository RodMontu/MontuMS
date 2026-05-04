# CLAWDIO — Asistente Personal IA
## Documentación Técnica Completa

**Archivo:** `/mnt/extra/DOCUMENTOS_TECNICOS/CLAWDIO_ASISTENTE_PERSONAL.md`
**Última actualización:** 2026-05-01
**Mantenedor:** Montu (Rodrigo Montuschi)

---

## 1. Resumen Ejecutivo

Clawdio es el asistente personal IA de Rodrigo Montuschi (Montu) y Anastasia Rivera (Pecas), operando como bot Telegram (`@pantero_bot`) sobre la infraestructura privada en **serveri3** (192.168.1.211). No es un servicio en la nube: corre localmente, tiene acceso a los calendarios y correos de ambos usuarios, gestiona una base de datos de deberes e ideas, lleva la lista del supermercado Lider, transcribe voz, y monitorea la infraestructura TI del hogar.

**Framework:** Hermes Agent v0.12.0 (2026.4.30)
**Bot Telegram:** @pantero_bot
**Modelo principal:** gemini-2.5-flash (Gemini API key directa, ~$3/mes)
**Usuarios autorizados:** Montu (ID: 8357148621) + Pecas (ID: 8328037199)
**Hosting:** serveri3 — 192.168.1.211, usuario `i3`
**Directorio raíz:** `/home/i3/.hermes/`
**Estado:** OPERATIVO

---

## 2. Arquitectura y Stack Técnico

### 2.1 Diagrama de componentes

```
Telegram (usuarios) ─── @pantero_bot ─────────────────────────────────────────┐
                                                                                │
serveri3 (192.168.1.211)                                                        │
├── hermes-gateway.service  (systemd user service, PID python)  ◄───────────────┘
│   ├── Terminal backend: SSH → serverX (192.168.1.111)
│   ├── Hermes Agent v0.11.0
│   ├── HERMES_HOME=/home/i3/.hermes
│   ├── Modelo: gemini-2.5-flash  (Gemini API)
│   ├── Fallback 1: nvidia/nemotron-3-super-120b-a12b:free  (OpenRouter)
│   └── Fallback 2: llama3.1:8b  (Ollama en serverX :11434)
│
├── stt-proxy.service  (Flask, puerto 9877)
│   └── Endpoint OpenAI-compat para transcripción de voz
│
├── stt-local.sh  ──────► faster-whisper (modelo small, CPU, int8)
│
├── /home/i3/.hermes/
│   ├── config.yaml          — configuración principal
│   ├── SOUL.md              — personalidad y reglas
│   ├── MEMORY.md            — manual operativo y herramientas
│   ├── USER.md              — perfil de Montu
│   ├── supermercado.json    — lista Lider
│   ├── clawdio_db.sqlite    — DB deberes e ideas
│   ├── init_db.py           — funciones CRUD Python
│   ├── monitor.sh           — script monitoreo infraestructura
│   ├── stt-local.sh         — wrapper faster-whisper
│   └── scripts/
│       └── monitor.sh       — copia del script de monitoreo
│
└── Google Workspace credentials
    ├── accounts/montu/      — ce3wkc@gmail.com
    ├── accounts/pecas/      — rivera.melgarejo@gmail.com
    └── (default)            — rodrigo@montuschi.cl

serverX (192.168.1.111)
└── ollama :11434 ── llama3.1:8b  (fallback LLM para Clawdio)
```

### 2.2 Stack de modelos

| Slot | Modelo | Proveedor | Costo est. | Cuándo activa |
|---|---|---|---|---|
| Principal | `gemini-2.5-flash` | Gemini API key directa | ~$3/mes | Siempre (default) |
| Fallback 1 | `nvidia/nemotron-3-super-120b-a12b:free` | OpenRouter | $0 | Si Gemini falla |
| Fallback 2 | `llama3.1:8b` | Ollama en serverX :11434 | $0 | Si OpenRouter falla |

Nota (2026-05-02): Hermes v0.12.0 activo. busy_input_mode: steer. terminal.backend: ssh → serverX.

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

### 2.3 Servicios systemd

```bash
# Ver estado
systemctl --user -M i3@ status hermes-gateway.service
systemctl --user -M i3@ status stt-proxy.service

# Reiniciar
systemctl --user -M i3@ restart hermes-gateway.service
systemctl --user -M i3@ restart stt-proxy.service

# Ver logs
journalctl --user -M i3@ -u hermes-gateway.service -f --no-pager
journalctl --user -M i3@ -u stt-proxy.service -n 50 --no-pager
```

Archivos de unidad:
- `/home/i3/.config/systemd/user/hermes-gateway.service`
- `/home/i3/.config/systemd/user/hermes-gateway.service.d/stt.conf`
- `/home/i3/.config/systemd/user/stt-proxy.service`

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

| Archivo | Ruta | Descripción |
|---|---|---|
| config.yaml | /home/i3/.hermes/config.yaml | Config principal Hermes |
| SOUL.md | /home/i3/.hermes/SOUL.md | Personalidad y reglas de comportamiento |
| MEMORY.md | /home/i3/.hermes/memories/MEMORY.md | Memoria de infraestructura y proyectos activos (creado 2026-05-02) |
| USER.md | /home/i3/.hermes/USER.md | Perfil de Montu |
| supermercado.json | /home/i3/.hermes/supermercado.json | 61 productos habituales Lider |
| clawdio_db.sqlite | /home/i3/.hermes/clawdio_db.sqlite | DB deberes e ideas (SQLite) |
| init_db.py | /home/i3/.hermes/init_db.py | Funciones Python para DB |
| monitor.sh | /home/i3/.hermes/scripts/monitor.sh | Script monitoreo infraestructura |
| stt-local.sh | /home/i3/.hermes/stt-local.sh | Wrapper faster-whisper STT |
| agent_results/ | /home/i3/.hermes/agent_results/ | Canal de retorno Claude↔Clawdio: resultados de agentes externos |
| write_result.py | /home/i3/.hermes/agent_results/write_result.py | Helper Python para escribir resultados en formato estándar |
| agent_results.md | /home/i3/.hermes/skills/desarrollo/agent_results.md | Skill: instrucciones del canal de retorno para Clawdio |

---

## 3. Herramientas disponibles (con comandos exactos)

Clawdio tiene acceso a las siguientes herramientas mediante el agente Hermes. Para usarlas internamente desde Python:

```python
import sys; sys.path.insert(0, '/home/i3/.hermes'); from init_db import *
```

### 3.1 Terminal tool
Ejecuta comandos shell en serveri3. Se usa para:
- Correr `monitor.sh`
- Llamar a `google_api.py`
- Leer archivos con `cat`

### 3.2 File read/write
- Leer: `read_file /home/i3/.hermes/supermercado.json`
- Escribir: vía `write_file` o `edit_file`

### 3.3 Code execution (execute_code)
Ejecuta Python en el entorno Hermes. Patrón de importación obligatorio:
```python
import sys; sys.path.insert(0, '/home/i3/.hermes'); from init_db import *
```

### 3.4 Web search / Web fetch
Búsqueda y scraping web. Disponible para Montu y Pecas desde Telegram.

---

## 4. Cuentas Google configuradas

Tres cuentas OAuth2 autenticadas. Cada una tiene su propio `HERMES_HOME`:

| Cuenta | Titular | HERMES_HOME | Uso |
|---|---|---|---|
| `rodrigo@montuschi.cl` | Montu | `/home/i3/.hermes` | Workspace, calendario laboral |
| `ce3wkc@gmail.com` | Montu | `/home/i3/.hermes/accounts/montu` | Gmail personal, calendario personal |
| `rivera.melgarejo@gmail.com` | Pecas | `/home/i3/.hermes/accounts/pecas` | Gmail y calendario de Pecas |

**Regla crítica:** cuando Montu pregunta por su agenda sin especificar cuenta, Clawdio consulta AMBAS cuentas de Montu y consolida.

### 4.1 Comandos de calendario

```bash
# Listar eventos — rodrigo@montuschi.cl
HERMES_HOME=/home/i3/.hermes \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  calendar list --start YYYY-MM-DDTHH:MM:SS --end YYYY-MM-DDTHH:MM:SS

# Listar eventos — ce3wkc@gmail.com (personal Montu)
HERMES_HOME=/home/i3/.hermes/accounts/montu \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  calendar list --start YYYY-MM-DDTHH:MM:SS --end YYYY-MM-DDTHH:MM:SS

# Listar eventos — rivera.melgarejo@gmail.com (Pecas)
HERMES_HOME=/home/i3/.hermes/accounts/pecas \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  calendar list --start YYYY-MM-DDTHH:MM:SS --end YYYY-MM-DDTHH:MM:SS

# Crear evento
HERMES_HOME=/home/i3/.hermes \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  calendar create \
  --summary "Título del evento" \
  --start YYYY-MM-DDTHH:MM:SS \
  --end YYYY-MM-DDTHH:MM:SS \
  --location "Dirección o lugar"
```

### 4.2 Comandos de Gmail

```bash
# Buscar no leídos — rodrigo@montuschi.cl
HERMES_HOME=/home/i3/.hermes \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  gmail search "is:unread" --max 10

# Buscar no leídos — ce3wkc@gmail.com
HERMES_HOME=/home/i3/.hermes/accounts/montu \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  gmail search "is:unread" --max 10

# Buscar no leídos — rivera.melgarejo@gmail.com (Pecas)
HERMES_HOME=/home/i3/.hermes/accounts/pecas \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
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
**Archivo:** `/home/i3/.hermes/clawdio_db.sqlite`
**Módulo Python:** `/home/i3/.hermes/init_db.py`

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

### 5.2 Funciones disponibles

```python
import sys; sys.path.insert(0, '/home/i3/.hermes'); from init_db import *

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

**Archivo:** `/home/i3/.hermes/supermercado.json`
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

**Ruta:** `/home/i3/.hermes/monitor.sh` (también en `scripts/monitor.sh`)

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

| ID | Schedule | Timezone | Acción |
|---|---|---|---|
| monitor-manana | 0 8 * * * | America/Santiago | Reporte infra a Montu |
| monitor-noche | 0 20 * * * | America/Santiago | Reporte infra a Montu |
| briefing-manana | 0 9 * * * | America/Santiago | Correos + agenda + pendientes del día |
| ideas-pendientes | 0 17 * * 1-5 | America/Santiago | Recordatorio ideas captured esta semana (lun-vie) |
| resumen-semanal | 0 10 * * 5 | America/Santiago | Resumen viernes: infra + productividad + agenda |

Config en `config.yaml`:
```yaml
cron:
  wrap_response: true
  jobs:
    - id: monitor-manana
      schedule: 0 8 * * *
      timezone: America/Santiago
      prompt: 'Ejecuta /home/i3/.hermes/monitor.sh usando el terminal tool y enviame
        el reporte de infraestructura por Telegram al usuario Montu (Telegram ID: 8357148621).
        Formatea el reporte de forma clara y concisa.'
      platforms: [telegram]
      channel: '8357148621'
    - id: monitor-noche
      schedule: 0 20 * * *
      timezone: America/Santiago
      prompt: 'Ejecuta /home/i3/.hermes/monitor.sh ...'
      platforms: [telegram]
      channel: '8357148621'
```

### 8.3 Ejecución manual

```bash
# Desde serveri3
/home/i3/.hermes/monitor.sh

# Desde cualquier host con SSH
ssh i3@192.168.1.211 '/home/i3/.hermes/monitor.sh'
```

---

## 9. Personalidad y comportamiento (SOUL.md)

**Archivo:** `/home/i3/.hermes/SOUL.md`
**Cargado como:** `system_prompt` en `config.yaml` + personalidad `clawdio`

### 9.1 Identidad core

Clawdio es un colaborador inteligente con criterio propio, no un bot servil. Opera en infraestructura privada de la pareja. Cuando no sabe algo, lo dice sin rodeos.

### 9.2 Idioma y tono

- **Idioma:** Español chileno culto-informal siempre (incluso si el usuario escribe en otro idioma)
- **Prohibido:** "puta", "cacho", "brigido", "pifia", "condoro", "al tiro"
- **Sin:** emojis celebratorios, adulación, "¡Claro que sí!", inventar información

### 9.3 Con Montu
- Lo llama "Montu" (nunca "Rodrigo" ni "jefe")
- Tono: directo, técnico, sin relleno — como colega que sabe lo que hace
- Captura automáticamente tareas e ideas mencionadas al pasar → "Capturado: [X]."
- Revisión de agenda proactiva al inicio de jornada cuando Montu lo indica

### 9.4 Con Pecas
- La llama "Pecas" (nunca "Anastasia")
- Tono: directo, cercano, cariñoso — sin tecnicismos
- Explicaciones muy breves por defecto; amplía si ella pide
- Apoyo proactivo en búsqueda de empleo: recordatorios de postulaciones, seguimiento
- Respeta que es más organizada que Montu

### 9.5 Captura de información
- Tareas, ideas, recordatorios, compromisos: captura siempre, sin que se lo pidan
- Confirma con mensaje breve: "Anotado: [X]."
- Nunca pierde información mencionada al pasar

### 9.6 Espacio compartido
- Lista supermercado, agenda familiar, compromisos comunes: gestionados para ambos
- Cuando cualquiera menciona algo para el hogar, lo registra en el espacio compartido

---

## 10. Memoria operativa (MEMORY.md / USER.md)

### 10.1 MEMORY.md (`/home/i3/.hermes/MEMORY.md`)

Manual operativo completo cargado en el contexto del agente. Contiene:
- Reglas de tono y comunicación
- Formato de fechas/horas/zona horaria (America/Santiago, UTC-4)
- Comandos exactos de cada herramienta Google
- Patrón de importación DB SQLite
- Ruta exacta de supermercado.json
- Instrucciones del script de monitoreo
- Cuentas configuradas

### 10.2 USER.md (`/home/i3/.hermes/USER.md`)

Perfil de Montu:
- Ingeniero Civil Industrial, consultor en IA/automatización
- Neurodivergente 2e: TDAH + AACC + TEA + dislexia de transposición
- Prefiere tono culto-informal, nunca excesivamente coloquial
- Usa audio frecuentemente por dislexia — priorizar captura de ideas de audios
- Vive en Santiago de Chile con su esposa Pecas (Anastasia Rivera)
- Proyectos activos: OptiFierro, Pegas V2, Visual-Voice, OP RISK

### 10.3 Config de memoria en Hermes

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

## 11. Comandos de operación y mantención

### 11.1 Estado del sistema

```bash
# Estado de servicios (desde cualquier host con SSH)
ssh i3@192.168.1.211 'systemctl --user status hermes-gateway.service stt-proxy.service --no-pager'

# Desde serveri3 directamente
systemctl --user status hermes-gateway.service --no-pager
systemctl --user status stt-proxy.service --no-pager
```

### 11.2 Logs

```bash
# Log en tiempo real del gateway
ssh i3@192.168.1.211 'journalctl --user -u hermes-gateway.service -f --no-pager'

# Últimas 100 líneas
ssh i3@192.168.1.211 'journalctl --user -u hermes-gateway.service -n 100 --no-pager'

# Log del STT proxy
ssh i3@192.168.1.211 'journalctl --user -u stt-proxy.service -n 50 --no-pager'
```

### 11.3 Reinicio de servicios

```bash
# Reiniciar gateway (aplica cambios en config.yaml)
ssh i3@192.168.1.211 'systemctl --user restart hermes-gateway.service'

# Reiniciar STT proxy
ssh i3@192.168.1.211 'systemctl --user restart stt-proxy.service'

# Reload sin reinicio (si soportado)
ssh i3@192.168.1.211 'systemctl --user kill -s USR1 hermes-gateway.service'
```

### 11.4 Edición de archivos clave

```bash
# Editar personalidad/reglas
nano /home/i3/.hermes/SOUL.md

# Editar config principal (modelos, crons, STT, etc.)
nano /home/i3/.hermes/config.yaml

# Editar manual operativo
nano /home/i3/.hermes/MEMORY.md

# Editar perfil usuario
nano /home/i3/.hermes/USER.md

# Ver DB SQLite directamente
sqlite3 /home/i3/.hermes/clawdio_db.sqlite
  .tables
  SELECT * FROM deberes ORDER BY fecha_creacion DESC LIMIT 10;
  SELECT * FROM ideas ORDER BY fecha_creacion DESC LIMIT 10;
  .quit
```

### 11.5 Actualización de Hermes

```bash
# Ver versión actual
ssh i3@192.168.1.211 '/home/i3/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main --version'

# Actualizar (nota: 307 commits detrás al 2026-05-01)
ssh i3@192.168.1.211 'cd /home/i3/.hermes/hermes-agent && hermes update'

# Tras actualizar, reiniciar
ssh i3@192.168.1.211 'systemctl --user restart hermes-gateway.service'
```

### 11.6 Gestión de crons

```bash
# Ver crons activos en config.yaml
ssh i3@192.168.1.211 'grep -A10 "^cron:" /home/i3/.hermes/config.yaml'

# Añadir/modificar crons: editar config.yaml y reiniciar gateway
nano /home/i3/.hermes/config.yaml
systemctl --user restart hermes-gateway.service
```

### 11.7 Verificar Google Auth

```bash
# Test calendario rodrigo@montuschi.cl
HERMES_HOME=/home/i3/.hermes \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  calendar list \
  --start $(date -u +%Y-%m-%dT00:00:00) \
  --end $(date -u -d '+7 days' +%Y-%m-%dT00:00:00)

# Test calendario ce3wkc@gmail.com
HERMES_HOME=/home/i3/.hermes/accounts/montu \
  /home/i3/.hermes/hermes-agent/venv/bin/python \
  /home/i3/.hermes/skills/productivity/google-workspace/scripts/google_api.py \
  calendar list \
  --start $(date -u +%Y-%m-%dT00:00:00) \
  --end $(date -u -d '+7 days' +%Y-%m-%dT00:00:00)
```

### 11.8 Backup manual de la DB

```bash
# Backup SQLite
cp /home/i3/.hermes/clawdio_db.sqlite \
   /home/i3/.hermes/clawdio_db.sqlite.bak.$(date +%Y%m%d)

# Copiar a serverX (Miau-Nube)
scp /home/i3/.hermes/clawdio_db.sqlite \
    x@192.168.1.111:/mnt/extra/backups/clawdio_db.sqlite.$(date +%Y%m%d)
```

---

## 12. Guía de uso para Montu

### 12.1 Acceso
- **Bot Telegram:** `@pantero_bot`
- **ID Telegram:** 8357148621
- **Voz:** Graba audio en Telegram — faster-whisper transcribe automáticamente

### 12.2 Comandos y frases de uso frecuente

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

### 12.3 Captura automática
Clawdio captura tareas e ideas mencionadas al pasar durante cualquier conversación y notifica brevemente: "Anotado: [X]."

---

## 13. Guía de uso para Pecas

### 13.1 Acceso
- **Bot Telegram:** `@pantero_bot`
- **ID Telegram:** 8328037199

### 13.2 Comandos y frases de uso frecuente

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

### 13.3 Estilo de interacción
- Las respuestas son breves por defecto
- Sin tecnicismos
- Si necesita más detalle, pedirlo explícitamente
- Clawdio usa `usuario='pecas'` automáticamente cuando reconoce que es ella quien escribe

---

## 14. Pendientes técnicos

| Prioridad | Pendiente | Contexto |
|---|---|---|
| Alta | Login manual en Lider.cl via Camofox | Camofox (browser automation Node.js) está instalado pero requiere sesión inicial autenticada en lider.cl para persistirla |
| Media | Cron monitoreo de precios para Pecas | Artículo/URL de Lider a monitorear aún sin definir |
| Media | Fix hooks en `~/.claude/settings.json` en serverX | Hooks de Claude Code en serverX requieren corrección |
| Baja | Actualizar Hermes Agent | 307 commits detrás al 2026-05-01 — evaluar antes de actualizar |
| Baja | Agregar productos habituales a supermercado.json | La lista de 61 productos habituales está pendiente de cargar en el JSON |
| Baja | WARP enrollment en Mac Pecas | Requiere acceso físico al equipo para enrolar Cloudflare WARP |
| N/A | Claude Desktop conectado | Cliente MCP de Clawdio (bridge SSH activo, estado: RUNNING) |
| N/A | Canal de retorno Claude↔Clawdio | Implementado (Opción A: archivos en agent_results/) |

---

## 15. Historial de cambios relevantes

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

*Fin del documento — act. 2026-05-02*
