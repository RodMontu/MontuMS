# BIBLIOTECA DE PROMPTS MS v3.0
**Version:** 1.1 - 2026-05-24
**Mantenida por:** Miaude + CCa
**Codigos:** 01 XML Maestro, 04 Piensa Primero, 08 Paso a Paso, 12 Abogado Diablo, 15 Motor de Disparo, 44 SOP

> Como usar: (1) Identifica la situacion en el indice (2) Copia el template completo (3) Reemplaza TODO lo que esta en [MAYUSCULAS] (4) Dispara el prompt. Si dudas en algun campo al completar: template mal elegido o mal completado, reporta a Miaude.

---

## INDICE RAPIDO

| Situacion | Template |
|---|---|
| Inicio de chat nuevo (proyecto conocido) | 1.1 |
| Retomar sesion anterior con decisiones tomadas | 1.2 |
| Claude agoto cuota, pasar a Gemini | 1.3 |
| Pedir tarea a Rabin | 1.4 |
| Tarea backend/infra/scripts a CCa (3+ pasos) | 2.1 |
| Algo esta roto, necesito diagnostico | 2.2 |
| Deployar o cambiar configuracion de servicio | 2.3 |
| Analisis tecnico extenso a Gemini | 3.1 |
| Componente o pagina frontend a Gemini | 3.2 |
| Documentacion tecnica extensa a Gemini | 3.3 |
| Revisar plan critico antes de ejecutar | 3.4 |
| Actualizar LOG_CAMBIOS_2026.md | 4.1 |
| Documentar nuevo servicio en infra | 4.2 |

---

## 1. INICIO DE SESION -- Motor de Disparo

### 1.1 -- Activacion rapida
> Cuando: inicio de chat nuevo sobre proyecto que Miaude conoce. Completar en menos de 30 segundos.

    ACTIVAR_MS_V3
    Proyecto: [NOMBRE -- ej: OptiFierro, OP Risk, Pegas V2, Clawdio]
    Estado: [Una oracion -- que quedo hecho la ultima vez]
    Sesion de hoy: [Que quiero terminar]

---

### 1.2 -- HANDOFF entre sesiones
> Cuando: retomar trabajo de sesion anterior con decisiones tomadas que no quiero perder. Completar en menos de 60 segundos.

    <handoff_inicio>
      <proyecto>[NOMBRE]</proyecto>
      <completado>[Que quedo listo -- lista o parrafo]</completado>
      <decisiones>[Decisiones tomadas y por que -- una por linea, las que apliquen]</decisiones>
      <pendiente>[Proxima accion concreta -- verbo + objeto]</pendiente>
      <no_tocar>[Archivos, IPs o reglas que no cambian en esta sesion]</no_tocar>
    </handoff_inicio>

---

### 1.3 -- Relay a Gemini Lead (Claude agoto cuota)
> Cuando: Claude se queda sin cuota en medio de una tarea. Pegar en Antigravity o Gemini CLI. Completar en menos de 60 segundos.

    <handoff_gemini>
      <rol>Eres el Gemini Lead de la MS v3.0. No tomas decisiones de arquitectura sin Montu. No tocas .env ni credenciales. No haces push a GitHub sin revision de Montu.</rol>
      <proyecto>[NOMBRE]</proyecto>
      <estado>[Pegar contenido de handoff_actual.md -- o describir estado actual en detalle]</estado>
      <pendiente>[Proxima accion concreta -- verbo + objeto]</pendiente>
      <restriccion_critica>[La regla mas importante de este proyecto -- ej: mapeo _BODSUC_MAP nunca cambia]</restriccion_critica>
    </handoff_gemini>

    Infra de referencia (copiar solo si la tarea involucra servidores):
    - serverX: ssh x@192.168.1.111 -- computo, Docker, GPU P104-100
    - serveri3: ssh i3@192.168.1.211 -- gateway, Cloudflare, Clawdio
    - TO: ssh OptiFierro@192.168.1.65 -- cliente, OptiFierro V2

---

### 1.4 -- Activacion Rabin (Telegram)
> Cuando: delegar tarea a Clawdio Rabin -- docs, SSH, notificaciones. Completar en menos de 30 segundos.

    Rabin -- [TITULO DE LA TAREA]
    Prioridad: [URGENTE / cuando puedas]
    Tarea: [Que hacer -- concreto y accionable]
    Path: [~/MontuMS o ruta especifica en serverX]
    Confirmar antes de ejecutar: [SI / NO]
    Al terminar: reporta resultado [y hash de commit si aplica]

---

## 2. DELEGACION A CCa -- Paso a Paso

### 2.1 -- Delegacion general
> Cuando: cualquier tarea de backend, scripts, configuracion o infra con 3 o mas pasos. Completar en menos de 60 segundos.

    MISION CCa -- [NOMBRE DE LA TAREA]
    Servidor: [serverX | serveri3 | TO | Mac local]
    Path: [ruta absoluta del proyecto]

    ANTES DE EJECUTAR:
    Lee el estado actual con: [comando -- ej: docker ps, git status, cat archivo.log]
    Escribe tu plan completo (pasos numerados) ANTES de tocar nada.

    TAREA:
    [Descripcion detallada de que hacer]

    RESTRICCIONES:
    - [Regla inamovible 1]
    - [Regla inamovible 2]

    CRITERIO DE EXITO:
    [Como se ve el resultado correcto -- observable y verificable]

    AL TERMINAR:
    Reporta que hiciste y el resultado exacto. Si algo fallo: muestra el error exacto, no supongas. No hagas push a GitHub.

---

### 2.2 -- RCA (algo esta roto)
> Cuando: un servicio falla o hay error inesperado. Usar SIEMPRE antes de tocar nada. Completar en menos de 45 segundos.

    MISION CCa -- RCA
    Servidor: [serverX | serveri3 | TO]
    Sintoma: [Error exacto -- pegar el mensaje textual si existe]

    PASO 1 -- Solo recolecta evidencia, no toques nada:
    - Log: [journalctl -u SERVICIO -n 50 / docker logs CONTENEDOR -n 50 / cat archivo.log]
    - Estado: [systemctl status SERVICIO / docker ps]
    - Ultimos cambios: git log --oneline -3

    PASO 2 -- Lista 3 hipotesis de causa raiz con la evidencia que las soporta.
    PASO 3 -- Verifica cada hipotesis antes de proponer fix.
    PASO 4 -- Propone el fix minimo. No refactorices nada adicional.

    Si el fix toca produccion: detente y reporta a Montu primero.

---

### 2.3 -- Deploy / modificacion de servicio
> Cuando: deployar codigo nuevo o cambiar configuracion de un contenedor o servicio. Completar en menos de 60 segundos.

    <mision_cca tipo="deploy">
      <objetivo>[Que deployar o cambiar -- concreto]</objetivo>
      <servidor>[serverX | serveri3 | TO]</servidor>
      <path>[ruta absoluta del proyecto o compose]</path>
      <pre_deploy>
        git log --oneline -3
        git status
        docker ps
        df -h /
      </pre_deploy>
      <pasos>[Lista numerada de pasos -- o pedir a CCa que los proponga antes de ejecutar]</pasos>
      <rollback>[Comando exacto de rollback si falla -- ej: git revert HEAD y docker compose up -d]</rollback>
      <criterio_exito>[Como verificar que funciono -- curl, docker ps, log limpio]</criterio_exito>
    </mision_cca>

---

## 3. DELEGACION A GEMINI -- XML Maestro

### 3.1 -- Analisis tecnico / segunda opinion
> Cuando: analisis extenso de codigo, arquitectura o logs. Output esperado mayor a 500 tokens. Completar en menos de 60 segundos.

    <mision_gemini tipo="analisis">
      <rol>Eres el Gemini Lead de la MS v3.0. Analista tecnico senior.</rol>
      <tarea>[Que analizar -- una oracion clara]</tarea>
      <proyecto>[Nombre del proyecto]</proyecto>
      <material>[Pegar el contenido relevante -- codigo, logs, config. Si son paths de archivos, aclararlo explicitamente.]</material>
      <output>
        Formato: Markdown.
        Longitud: [CORTO=1 pagina | MEDIO=3 paginas | EXTENSO=sin limite]
        Secciones: hallazgos principales, riesgos identificados, recomendaciones (maximo 5).
      </output>
      <restriccion>Solo analiza y propone. No ejecutes comandos.</restriccion>
    </mision_gemini>

---

### 3.2 -- Frontend React/TSX
> Cuando: construir o modificar componentes o paginas React con Tailwind v4. Completar en menos de 60 segundos.

    <mision_gemini tipo="frontend">
      <rol>Eres el Gemini Lead especialista en React/TypeScript/Tailwind v4.</rol>
      <tarea>[Componente o pagina a construir -- nombre y funcion]</tarea>
      <stack>React + Vite + TypeScript + Tailwind v4</stack>
      <ui_perfil>Usuarios TEA+TDAH+AACC: jerarquia visual fuerte, colores con significado semantico, densidad de informacion controlada, patrones predecibles sin sorpresas de navegacion.</ui_perfil>
      <paleta>Naranja: #f97316 | Sidebar: #111827 | Fondo: blanco o gris claro</paleta>
      <componentes_existentes>[Listar lo que no debe romper -- ej: Sidebar.tsx, useAuth.ts, rutas en App.tsx]</componentes_existentes>
      <referencia_visual>[Descripcion o path de screenshot -- OPCIONAL, dejar vacio si no hay]</referencia_visual>
      <restricciones>
        Codigo completo y funcional, no fragmentos.
        Sin dependencias nuevas sin avisar primero.
        No romper rutas ni componentes existentes.
      </restricciones>
    </mision_gemini>

---

### 3.3 -- Documentacion tecnica
> Cuando: generar o actualizar documentos tecnicos de mas de 50 lineas. Completar en menos de 30 segundos.

    <mision_gemini tipo="documentacion">
      <tarea>[Generar | Actualizar]: [nombre del documento]</tarea>
      <cambios>[Lista de cambios a documentar -- uno por linea]</cambios>
      <formato>Markdown compatible con GitHub. Headers ##, tablas, code blocks.</formato>
      <instruccion>Entrega el bloque exacto listo para insertar o reemplazar. Texto definitivo y completo, no resumen.</instruccion>
    </mision_gemini>

---

### 3.4 -- Abogado del Diablo
> Cuando: antes de ejecutar un plan importante o decision arquitectonica. Completar en menos de 30 segundos (solo pegar el plan).

    <mision_gemini tipo="revision_critica">
      <rol>Eres el revisor critico. Tu trabajo es encontrar problemas del plan, no validarlo.</rol>
      <plan>[Pegar el plan, arquitectura o decision a revisar]</plan>
      <instruccion>
        Output en lista numerada. Maximo 2 paginas.
        1. Los 3 riesgos mas probables de falla (con probabilidad estimada)
        2. Asunciones no verificadas que podrian invalidar el plan
        3. Las 3 preguntas que Montu debe responder antes de ejecutar
        No suavices las criticas. False positives son preferibles a false negatives.
      </instruccion>
    </mision_gemini>

---

## 4. ACTUALIZACION DE DOCS VIA RABIN

### 4.1 -- Actualizar LOG_CAMBIOS
> Cuando: despues de cualquier cambio relevante en codigo, infra o configuracion. Completar en menos de 45 segundos.

    RABIN -- Actualizar LOG_CAMBIOS_2026.md
    Path: ~/MontuMS/docs/LOG_CAMBIOS_2026.md en serverX
    Accion: insertar al INICIO del archivo este bloque exacto:

    ---
    ## [YYYY-MM-DD] -- [TITULO DEL CAMBIO]
    **Contexto:** [Una oracion]
    **Cambios:**
    - [Cambio 1]
    - [Cambio 2]
    ---

    Commit: git add docs/LOG_CAMBIOS_2026.md && git commit -m "docs: [YYYY-MM-DD] [TITULO]" && git push
    Reporta el hash del commit.

---

### 4.2 -- Documentar nuevo servicio en infra
> Cuando: se agrega, modifica o depreca un servicio en serverX, serveri3 o TO. Completar en menos de 45 segundos.

    RABIN -- Documentar cambio de infra
    Servicio: [NOMBRE]
    Host: [serverX | serveri3 | TO]
    Puerto: [PUERTO]
    Compose path: [PATH]
    Funcion: [Una oracion]
    Estado: [OPERATIVO | EN PRUEBA | DEPRECADO]

    Acciones:
    1. Actualizar seccion correspondiente en ~/MontuMS/docs/INVENTARIO_MAESTRO.md
    2. Insertar entrada en ~/MontuMS/docs/LOG_CAMBIOS_2026.md (usar formato de template 4.1)
    3. git add -A && git commit -m "docs: [YYYY-MM-DD] infra [NOMBRE]" && git push
    Reporta el hash del commit.

---

## 5. NOTAS DE USO

**Regla de oro:** Si dudas en algun campo al completar el template, para. O el template esta mal elegido o necesita mejora. Reporta a Miaude para iterarlo.

**Unico campo opcional:** referencia_visual en template 3.2. Todos los demas campos son obligatorios.

**Formato de fecha:** siempre YYYY-MM-DD. Es la fecha del dia en que usas el template.

**RCA es siempre el primer paso** cuando algo falla en produccion -- antes de cualquier otra accion.

**Gemini CLI:** ejecutar siempre desde un directorio de proyecto acotado, no desde la raiz del sistema. Evita que use el filesystem completo como contexto.

**Actualizacion de esta biblioteca:** cuando un template genere friccion o el tiempo de completar supere 60 segundos, reportar a Miaude. Rabin hace el commit de la mejora.

---
*BIBLIOTECA_PROMPTS_MS.md -- v1.1 -- MS v3.0 -- Montuschi Consultores SpA -- 2026-05-24*
