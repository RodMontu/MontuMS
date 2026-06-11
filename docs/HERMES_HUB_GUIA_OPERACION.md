# Hermes Hub — Guía de Operación de Agentes
**Creado:** 2026-06-10
**Propósito:** Referencia operativa para Carlitos y Aurora. Válida en cualquier ventana de chat con Miaude para retomar contexto operativo.

---

## Estado del ecosistema (2026-06-10)

5 agentes operativos en Hermes Hub (serverX :8750 → :8751):

| Agente | Host | Modelo | Rol |
|---|---|---|---|
| Rabín | serveri3 | Gemini 2.5 Flash | Asistente personal Montu+Pecas, @pantero_bot |
| Espinita | serveri3 | Gemini 2.5 Flash | Conserje IA Edificio Los Espinos |
| Risko | serveri3 | Gemini 2.5 Flash | Asistente OP Risk |
| Carlitos | serverX | qwen2.5-coder:7b (Ollama) | Coordinador MS, análisis técnico |
| Aurora | serverX | qwen2.5-coder:7b (Ollama) | Documentación técnica, escritura MontuMS |

---

## Aurora — Protocolo de uso

### Regla de oro
Aurora es un escribano, no un analista.
Darle siempre el texto ya formateado. Ella escribe y commitea.
Nunca pedirle que decida que documentar — siempre darle el contenido exacto.

### Keywords que activan detección de archivo destino
| Keyword en el prompt | Archivo destino |
|---|---|
| log / log_cambios | docs/LOG_CAMBIOS_2026.md |
| inventario / inventario_maestro | docs/INVENTARIO_MAESTRO.md |
| clawdio | docs/CLAWDIO_ASISTENTE_PERSONAL.md |
| reglas | docs/REGLAS_CARDINALES_FLUJO_ORQUESTADO.md |
| biblioteca | docs/BIBLIOTECA_PROMPTS_MS.md |
| guia / guia_operacion | docs/HERMES_HUB_GUIA_OPERACION.md |

### Formato de prompt correcto para Aurora
Aurora, actualiza el [keyword] con este bloque exacto:
[CONTENIDO COMPLETO Y FORMATEADO — sin que Aurora tenga que inferir nada]

### Capacidades de Aurora
- Leer archivos MontuMS (ultimas 3000 chars como contexto)
- Escribir/append en archivos MontuMS conocidos
- git commit + push a GitHub (key: id_ed25519_github)
- NO ejecuta comandos del sistema
- NO escribe fuera de /home/x/MontuMS

---

## Carlitos — Protocolo de uso

### Regla de oro
Carlitos es un tecnico de guardia: analiza y genera codigo, no ejecuta.
Siempre darle TODO el contexto pegado en el mensaje (logs, codigo, output).
Nunca pedirle que revise que esta corriendo — no tiene acceso al sistema.

### Cuando usarlo
| Situacion | Que pedirle |
|---|---|
| Error en serverX con logs disponibles | Causa raiz + comandos de diagnostico |
| Antes de ejecutar un script complejo | Revision logica y sintaxis |
| Necesito script bash/Python para serverX | Generacion del borrador |
| Segunda opinion arquitectonica rapida | Validacion del approach |

### Formato de prompt correcto para Carlitos
Carlitos, [tarea concreta].
Contexto:
[logs / codigo / output de comandos pegado aqui]
Dame: [script / comando / analisis / pasos]

### Capacidades de Carlitos
- Analizar logs y codigo dados en el prompt
- Generar scripts bash/Python para serverX
- Proponer comandos Docker con contexto dado
- Razonar sobre arquitectura
- NO ejecuta nada
- NO lee archivos del sistema

---

## Control directo por Miaude (Protocolo Miaude-sin-Montu)

### Endpoint REST
POST http://192.168.1.111:8751/api/chat/{agent_id}
Body: {content: mensaje, agent_id: aurora}

### Canal operativo
Miaude → Clawdio MCP → SSH serverX → curl REST → Hermes Hub → Aurora/Carlitos

### Regla Miaude para documentacion
Cuando hay cambios que documentar, Miaude NO entrega bloques para copiar/pegar.
Miaude genera el prompt exacto para Aurora con el contenido ya formateado.
Formato estandar: [Para Aurora en Hermes Hub] Aurora, actualiza el [keyword] con este bloque exacto: [contenido]

---

*Generado por CCa — act. 2026-06-10*
