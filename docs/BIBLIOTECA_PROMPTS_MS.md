# BIBLIOTECA DE PROMPTS MS v3.0
**Última actualización:** 2026-05-24
**Mantenida por:** Miaude (Claude) + CCa
**Códigos fuente:** 01 XML Maestro · 04 Primero Piensa · 08 Paso a Paso · 15 Motor de Disparo · 44 SOP

---

## ÍNDICE
1. [INICIO DE SESIÓN — Motor de Disparo (código 15)](#1-inicio-de-sesión--motor-de-disparo)
2. [DELEGACIÓN A CCa — Paso a Paso (código 08)](#2-delegación-a-cca--paso-a-paso)
3. [DELEGACIÓN A GEMINI — XML Maestro (código 01)](#3-delegación-a-gemini--xml-maestro)
4. [ACTUALIZACIÓN DE DOCS VÍA RABÍN (código 44)](#4-actualización-de-docs-vía-rabín)
5. [NOTAS DE USO](#5-notas-de-uso)

---

## 1. INICIO DE SESIÓN — Motor de Disparo

> **Código 15:** Una frase de activación (trigger phrase) que dispara el contexto completo
> al inicio de cada chat. Va SIEMPRE en las primeras líneas del prompt.

### 1.1 Activación rápida (uso diario)

    ACTIVAR_MS_V3 — Soy Montu. Contexto:
    - Proyecto activo: [NOMBRE_PROYECTO]
    - Último estado: [RESUMEN_1_ORACIÓN]
    - Objetivo de esta sesión: [OBJETIVO]
    - Agentes disponibles: CCa, Gemini CLI, Rabín, ccor1-5

### 1.2 Activación con HANDOFF (continuación de sesión anterior)

    <handoff_inicio>
      <identidad>Soy Montu. MS v3.0 activa. Tú eres Mi TI + Miaude.</identidad>
      <proyecto>[NOMBRE_PROYECTO]</proyecto>
      <estado_anterior>[RESUMEN_DE_LO_COMPLETADO]</estado_anterior>
      <decisiones_tomadas>
        - [DECISIÓN 1]
        - [DECISIÓN 2]
      </decisiones_tomadas>
      <objetivo_sesion>[QUÉ TERMINAR HOY]</objetivo_sesion>
      <restricciones>[IPs fijas / archivos protegidos / reglas inamovibles]</restricciones>
      <proximo_paso>[PRIMERA_ACCIÓN_CONCRETA]</proximo_paso>
    </handoff_inicio>

### 1.3 Activación para Gemini Lead (relay cuando Claude agota cuota)

    <handoff_gemini>
      <rol>Eres el Gemini Lead de la MS v3.0. Continúas donde Claude quedó.</rol>
      <proyecto>[NOMBRE_PROYECTO]</proyecto>
      <infra>
        - serverX: ssh x@192.168.1.111 (cómputo, Docker, GPU P104-100)
        - serveri3: ssh i3@192.168.1.211 (gateway, Cloudflare, Clawdio)
        - TO: ssh OptiFierro@192.168.1.65 (cliente, OptiFierro V2)
      </infra>
      <reglas_cardinales>
        - No tomas decisiones de arquitectura sin consultar a Montu
        - No modificas .env ni credenciales
        - No haces push a GitHub sin revisión de Montu
        - Mapeo sucursales CRÍTICO: _BODSUC_MAP = {1:2, 10:1, 14:3} — NUNCA cambiar
        - Pascal GPU: usar compute_type=int8, nunca float16
      </reglas_cardinales>
      <estado_actual>[PEGAR CONTENIDO DE handoff_actual.md]</estado_actual>
    </handoff_gemini>

### 1.4 Activación para Rabín (Clawdio) vía Telegram

    Rabín, activar modo trabajo. Sesión: [NOMBRE_TAREA].
    Repo: ~/MontuMS en serverX.
    Tarea: [DESCRIPCIÓN].
    Al terminar: reporta resultado y hash de commit.

---

## 2. DELEGACIÓN A CCa — Paso a Paso

> **Código 08:** Estructura que obliga a CCa a planificar y mostrar el plan ANTES de ejecutar.
> Previene ejecución impulsiva. Usar siempre para tareas con más de 2 pasos.

### 2.1 Template base — delegación general

    MISIÓN CCa — [NOMBRE_TAREA]
    Fecha: [FECHA]
    Working dir: [PATH_LOCAL o "SSH: ssh x@192.168.1.111"]

    ANTES DE EJECUTAR:
    1. Lee el estado actual con: [comando de diagnóstico]
    2. Escribe tu plan completo (pasos numerados) ANTES de tocar nada
    3. Confirma que entendiste las restricciones
    [Código 04: piensa el plan antes de ejecutar]

    TAREA:
    [DESCRIPCIÓN DETALLADA]

    PASOS ESPERADOS:
    1. [PASO 1]
    2. [PASO 2]
    N. [PASO N]

    RESTRICCIONES (no negociables):
    - [RESTRICCIÓN 1]
    - [RESTRICCIÓN 2]

    CRITERIO DE ÉXITO:
    [CÓMO SE VE EL RESULTADO CORRECTO — observable y verificable]

    AL TERMINAR:
    - Reporta qué hiciste y el resultado exacto
    - Si algo falló: muestra el error exacto, no supongas
    - No hagas push a GitHub (Montu revisa primero)

### 2.2 Template RCA — diagnóstico de falla

    MISIÓN CCa — RCA: [SÍNTOMA EXACTO]

    SÍNTOMA: [DESCRIPCIÓN DEL ERROR — copiar textual si hay mensaje]

    PASO 1 — Recolecta evidencia (NO modifiques nada aún):
    - Log: [comando exacto para ver el log relevante]
    - Estado servicio: [comando]
    - Últimos cambios: git log --oneline -5

    PASO 2 — Lista 3 hipótesis de causa raíz basadas en la evidencia.

    PASO 3 — Verifica CADA hipótesis antes de proponer fix.

    PASO 4 — Propón el fix MÍNIMO. No refactorices. No mejores nada extra.

    RESTRICCIÓN CARDINAL: Si el fix toca producción, detente y reporta a Montu primero.

### 2.3 Template deploy / infra (XML Maestro aplicado a CCa)

    <mision_cca tipo="deploy">
      <objetivo>[QUÉ DEPLOYAR]</objetivo>
      <servidor>[serverX | serveri3 | TO]</servidor>
      <path_proyecto>[RUTA ABSOLUTA]</path_proyecto>
      <pre_deploy>
        <verificar>docker ps</verificar>
        <verificar>git status</verificar>
        <verificar>df -h /</verificar>
      </pre_deploy>
      <pasos>
        <paso n="1">[ACCIÓN 1]</paso>
        <paso n="2">[ACCIÓN 2]</paso>
      </pasos>
      <rollback>[COMANDO EXACTO DE ROLLBACK SI FALLA]</rollback>
      <criterio_exito>[CÓMO VERIFICAR QUE FUNCIONÓ]</criterio_exito>
    </mision_cca>

---

## 3. DELEGACIÓN A GEMINI — XML Maestro

> **Código 01:** Estructura XML que elimina ambigüedad en tareas complejas para Gemini.
> Preferido sobre texto libre para análisis, frontend y documentación extensa.

### 3.1 Template análisis técnico / segunda opinión arquitectónica

    <mision_gemini tipo="analisis">
      <rol>Eres el Gemini Lead de la MS v3.0. Analista técnico senior sin ego.</rol>
      <tarea>[DESCRIPCIÓN DE LA TAREA]</tarea>
      <contexto>
        <proyecto>[NOMBRE]</proyecto>
        <archivos_relevantes>[PATHS O CONTENIDO PEGADO]</archivos_relevantes>
      </contexto>
      <output_esperado>
        <formato>Markdown estructurado</formato>
        <secciones>
          <seccion>Hallazgos principales</seccion>
          <seccion>Riesgos identificados</seccion>
          <seccion>Recomendaciones priorizadas (máximo 5)</seccion>
        </secciones>
      </output_esperado>
      <restriccion>Solo analiza y propón. No ejecutes comandos.</restriccion>
    </mision_gemini>

### 3.2 Template frontend React/TSX

    <mision_gemini tipo="frontend">
      <rol>Eres el Gemini Lead especialista en React/TypeScript/Tailwind v4.</rol>
      <tarea>[COMPONENTE O PÁGINA A CONSTRUIR]</tarea>
      <stack>React + Vite + TypeScript + Tailwind v4</stack>
      <ui_perfil>
        Usuarios: TEA+TDAH+AACC. Diseño obligatorio:
        - Jerarquía visual fuerte (tamaño y peso tipográfico)
        - Colores con significado semántico (no decorativo)
        - Densidad de información controlada
        - Patrones reconocibles, sin sorpresas de navegación
      </ui_perfil>
      <paleta>Naranja: #f97316 | Sidebar: #111827 | Fondo: blanco/gris claro</paleta>
      <referencia_visual>[DESCRIPCIÓN O PATH DE SCREENSHOT]</referencia_visual>
      <restricciones>
        - No romper rutas ni componentes existentes
        - Código completo y funcional, no fragmentos
        - Sin dependencias nuevas sin avisar
      </restricciones>
    </mision_gemini>

### 3.3 Template documentación técnica extensa

    <mision_gemini tipo="documentacion">
      <tarea>Generar / Actualizar: [NOMBRE_DOCUMENTO]</tarea>
      <cambios_a_documentar>
        [LISTA DETALLADA DE CAMBIOS]
      </cambios_a_documentar>
      <formato>Markdown compatible con GitHub (headers ##, tablas, code blocks)</formato>
      <instruccion>
        Entrega el bloque exacto listo para insertar o reemplazar.
        No parafrasees ni resumas — escribe el texto definitivo y completo.
      </instruccion>
    </mision_gemini>

### 3.4 Template Gemini como "Abogado del Diablo" (código 12)

    <mision_gemini tipo="revision_critica">
      <rol>Eres el revisor crítico. Tu trabajo es encontrar los problemas del plan, no validarlo.</rol>
      <plan_a_revisar>[PEGAR EL PLAN O ARQUITECTURA]</plan_a_revisar>
      <instruccion>
        1. Identifica los 3 riesgos más probables de falla
        2. Señala asunciones incorrectas o no verificadas
        3. Propón las preguntas que Montu debería hacerse antes de ejecutar
        NO suavices las críticas. Prefiere false positives a false negatives.
      </instruccion>
    </mision_gemini>

---

## 4. ACTUALIZACIÓN DE DOCS VÍA RABÍN

> **Código 44 (SOP):** Proceso estándar para mantener INVENTARIO_MAESTRO y LOG_CAMBIOS
> actualizados sin intervención de Montu. Rabín tiene acceso SSH a serverX y skill doc-updater.

### 4.1 Template delegación estándar a Rabín (vía MCP Clawdio)

    RABÍN — Tarea: actualización de documentación técnica.

    ARCHIVOS EN ~/MontuMS/docs/ (serverX 192.168.1.111):

    LOG_CAMBIOS_2026.md — Insertar al inicio del archivo:
    ---
    ## [FECHA YYYY-MM-DD] — [TÍTULO DEL CAMBIO]
    **Contexto:** [UNA ORACIÓN]
    **Cambios:**
    - [CAMBIO 1]
    - [CAMBIO 2]
    ---

    INVENTARIO_MAESTRO.md — Sección [N]: [DESCRIPCIÓN DE LA MODIFICACIÓN]
    [BLOQUE EXACTO A INSERTAR O REEMPLAZAR]

    Al terminar:
    git add -A && git commit -m "docs: [FECHA] [TÍTULO]" && git push
    Reporta el hash del commit por Telegram a Montu.

### 4.2 Template cambio de infraestructura (Rabín)

    RABÍN — Documentar nuevo servicio/cambio de infra.

    Datos del cambio:
    - Nombre del servicio: [NOMBRE]
    - Host: [serverX | serveri3 | TO]
    - Puerto: [PUERTO]
    - Compose path: [PATH]
    - Función en una oración: [FUNCIÓN]
    - Estado: [OPERATIVO | EN PRUEBA | DEPRECADO]

    Actualiza INVENTARIO_MAESTRO.md en la sección correspondiente.
    Agrega entrada en LOG_CAMBIOS_2026.md.
    Commit y push. Reporta hash.

---

## 5. NOTAS DE USO

**Placeholders:** Todo texto en `[MAYÚSCULAS]` es reemplazable. Nunca enviar con placeholders sin completar.

**Jerarquía de templates:**
- Tarea simple (1-2 pasos) → texto libre con trigger phrase (1.1)
- Tarea compleja CCa (3+ pasos) → template 2.1 siempre
- Análisis o frontend Gemini → XML obligatorio (sección 3)
- Docs → siempre vía Rabín (sección 4), nunca manual

**Motor de Disparo (código 15):** La trigger phrase va en la PRIMERA LÍNEA del prompt, no al final. Define el "modo" del agente antes de que procese el resto.

**XML vs texto libre:** XML elimina ambigüedad en prompts largos. Gemini parsea XML mejor que markdown anidado. CCa puede usar cualquiera de los dos.

**Código 04 (Primero Piensa):** Siempre incluir la instrucción "escribe tu plan antes de ejecutar" en delegaciones a CCa. Previene el patrón de ejecución impulsiva que genera errores difíciles de revertir.

**Actualización de esta biblioteca:** Cuando se agregue un nuevo template o se mejore uno existente, Rabín actualiza este archivo + agrega entrada en LOG_CAMBIOS_2026.md.

---
*Documento vivo — MS v3.0 — Montuschi Consultores SpA*
