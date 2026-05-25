# BIBLIOTECA DE PROMPTS MS v3.0
Version: 1.1 — 2026-05-24
Mantenida por: Miaude + CCa
Codigos: 01 XML, 04 Piensa, 08 Paso a Paso, 12 Abogado Diablo, 15 Disparo, 44 SOP

Como usar: (1) Identifica la situacion en el indice (2) Copia el template (3) Reemplaza TODO lo que esta en [MAYUSCULAS] (4) Dispara. Si dudas en algun campo: template mal elegido o mal completado.

---

## INDICE RAPIDO

| # | Situacion | Template |
|---|-----------|----------|
| 1.1 | Iniciar sesion rapido | Activacion rapida |
| 1.2 | Pasar contexto entre sesiones | HANDOFF |
| 1.3 | Relevar a Gemini | Relay a Gemini Lead |
| 1.4 | Delegar tarea a Rabin | Activacion Rabin |
| 2.1 | Delegar tarea general a CCa | Delegacion general |
| 2.2 | Algo esta roto | RCA |
| 2.3 | Subir a produccion | Deploy |
| 3.1 | Pedir analisis tecnico a Gemini | Analisis tecnico |
| 3.2 | Construir frontend React/TSX | Frontend React/TSX |
| 3.3 | Generar documentacion tecnica | Documentacion tecnica |
| 3.4 | Revisar plan criticamente | Abogado del Diablo |
| 4.1 | Actualizar LOG_CAMBIOS | Actualizar LOG |
| 4.2 | Registrar nuevo servicio | Documentar servicio |

---

## SECCIÓN 1 — INICIO DE SESION (Motor de Disparo)

### 1.1 Activacion rapida

```
ACTIVAR_MS_V3
Proyecto: [NOMBRE_PROYECTO]
Estado: [ESTADO_ACTUAL_EN_UNA_LINEA]
Sesion de hoy: [QUE_QUIERES_LOGRAR_HOY]
```

---

### 1.2 HANDOFF entre sesiones

```xml
<handoff>
  <proyecto>[NOMBRE_PROYECTO]</proyecto>
  <completado>[LO_QUE_SE_TERMINO_EN_LA_SESION_ANTERIOR]</completado>
  <decisiones>[DECISIONES_TOMADAS_QUE_NO_SE_PUEDEN_REVERTIR]</decisiones>
  <pendiente>[PROXIMA_TAREA_CONCRETA]</pendiente>
  <no_tocar>[ARCHIVOS_O_SISTEMAS_QUE_NO_SE_DEBEN_MODIFICAR]</no_tocar>
</handoff>
```

---

### 1.3 Relay a Gemini Lead

```xml
<relay_gemini>
  <rol>[ROL_QUE_DEBE_ASUMIR_GEMINI]</rol>
  <proyecto>[NOMBRE_PROYECTO]</proyecto>
  <estado>[ESTADO_ACTUAL]</estado>
  <pendiente>[TAREA_A_CONTINUAR]</pendiente>
  <restriccion_critica>[LO_QUE_NO_PUEDE_TOCAR_BAJO_NINGUN_CONCEPTO]</restriccion_critica>
</relay_gemini>

<!-- OPCIONAL: incluir si la tarea requiere acceso a infra -->
<infra>
  <serverX>192.168.1.111 — SSH: ssh x@192.168.1.111</serverX>
  <serveri3>192.168.1.211 — SSH: ssh i3@192.168.1.211</serveri3>
  <TO>192.168.1.65 — SSH: ssh OptiFierro@192.168.1.65 (requiere VPN)</TO>
</infra>
```

---

### 1.4 Activacion Rabin

```
Titulo: [TITULO_BREVE_DE_LA_TAREA]
Prioridad: [URGENTE | cuando puedas]
Tarea: [DESCRIPCION_EXACTA_DE_LO_QUE_HAY_QUE_HACER]
Path: [RUTA_COMPLETA_DEL_ARCHIVO_O_DIRECTORIO]
Confirmar antes: [SI | NO]
Al terminar: [QUE_DEBE_REPORTAR_RABIN]
```

---

## SECCIÓN 2 — DELEGACION A CCa (Paso a Paso)

### 2.1 Delegacion general

```
MISION CCa

Servidor: [serverX | serveri3 | TO | local]
Path: [RUTA_ABSOLUTA_DEL_PROYECTO]

ANTES DE EJECUTAR:
- [VERIFICACION_1]
- [VERIFICACION_2]

TAREA:
1. [PASO_1]
2. [PASO_2]
3. [PASO_N]

RESTRICCIONES:
- [RESTRICCION_1]
- [RESTRICCION_2]

CRITERIO DE EXITO:
[COMO_SE_VE_CUANDO_ESTA_BIEN_HECHO]

AL TERMINAR:
[QUE_DEBE_REPORTAR_CCa]
```

---

### 2.2 RCA (algo esta roto)

```
Servidor: [serverX | serveri3 | TO]
Sintoma: [DESCRIPCION_EXACTA_DEL_ERROR_O_COMPORTAMIENTO_INESPERADO]

1. Solo evidencia: muéstrame logs, status, errores — sin tocar nada.
2. Hipotesis: lista las 3 causas mas probables ordenadas por probabilidad.
3. Verificar: dime que comandos ejecutar para confirmar la causa raiz.
4. Fix minimo: propone el cambio mas pequeño posible que resuelva el problema.

RESTRICCION CARDINAL: no tocar produccion hasta que Montu apruebe el fix.
```

---

### 2.3 Deploy

```xml
<mision_cca>
  <objetivo>[QUE_SE_VA_A_DEPLOYAR_Y_POR_QUE]</objetivo>
  <servidor>[serverX | serveri3 | TO]</servidor>
  <path>[RUTA_ABSOLUTA_DEL_PROYECTO]</path>
  <pre_deploy>
    git log -3
    git status
    docker ps
    df -h
  </pre_deploy>
  <pasos>
    <paso>1. [PASO_1]</paso>
    <paso>2. [PASO_2]</paso>
    <paso>3. [PASO_N]</paso>
  </pasos>
  <rollback>[COMANDO_O_PROCEDIMIENTO_PARA_REVERTIR]</rollback>
  <criterio_exito>[COMO_SE_VERIFICA_QUE_EL_DEPLOY_FUNCIONO]</criterio_exito>
</mision_cca>
```

---

## SECCIÓN 3 — DELEGACION A GEMINI (XML Maestro)

### 3.1 Analisis tecnico

```xml
<mision_gemini tipo="analisis">
  <rol>[ROL_EXPERTO_QUE_DEBE_ASUMIR]</rol>
  <tarea>[PREGUNTA_O_TAREA_CONCRETA]</tarea>
  <proyecto>[NOMBRE_Y_CONTEXTO_DEL_PROYECTO]</proyecto>
  <material>[CODIGO_LOGS_DOCS_O_REFERENCIA_AL_MATERIAL]</material>
  <output>
    <formato>Markdown</formato>
    <longitud>[CORTO | MEDIO | EXTENSO]</longitud>
    <secciones>[SECCION_1, SECCION_2, SECCION_N]</secciones>
  </output>
  <restriccion>[LO_QUE_NO_DEBE_HACER_O_ASUMIR]</restriccion>
</mision_gemini>
```

---

### 3.2 Frontend React/TSX

```xml
<mision_gemini tipo="frontend">
  <rol>Arquitecto frontend senior especializado en React accesible</rol>
  <tarea>[DESCRIPCION_DEL_COMPONENTE_O_PANTALLA_A_CONSTRUIR]</tarea>
  <stack>React + Vite + TypeScript + Tailwind v4</stack>
  <ui_perfil>TEA + TDAH + AACC — alta densidad informativa, sin decoracion innecesaria, jerarquia clara</ui_perfil>
  <paleta>
    <primario>naranja #f97316</primario>
    <sidebar>#111827</sidebar>
  </paleta>
  <componentes_existentes>[LISTA_DE_COMPONENTES_YA_CREADOS_O_NINGUNO]</componentes_existentes>
  <referencia_visual>[URL_O_DESCRIPCION — OPCIONAL]</referencia_visual>
  <restricciones>
    - [RESTRICCION_1]
    - [RESTRICCION_2]
  </restricciones>
</mision_gemini>
```

---

### 3.3 Documentacion tecnica

```xml
<mision_gemini tipo="documentacion">
  <tarea>[QUE_DOCUMENTAR — nuevo modulo, cambio de arquitectura, SOP, etc.]</tarea>
  <cambios>[DESCRIPCION_DE_LOS_CAMBIOS_O_CONTENIDO_A_DOCUMENTAR]</cambios>
  <formato>Markdown GitHub</formato>
  <instruccion>[INSTRUCCION_ADICIONAL — ej: insertar al inicio del archivo, reemplazar seccion X]</instruccion>
</mision_gemini>
```

---

### 3.4 Abogado del Diablo

```xml
<mision_gemini tipo="revision_critica">
  <rol>Abogado del Diablo tecnico — eres escéptico, no destructivo</rol>
  <plan>[DESCRIPCION_COMPLETA_DEL_PLAN_A_REVISAR]</plan>
  <instruccion>
    1. Identifica los 3 riesgos principales con probabilidad estimada (alta/media/baja).
    2. Lista las asunciones criticas que si fallan hunden el plan.
    3. Formula 3 preguntas que Montu deberia responder antes de ejecutar.
    Formato: max 2 paginas. Prefiere false positives sobre false negatives.
  </instruccion>
</mision_gemini>
```

---

## SECCIÓN 4 — DOCS VIA RABIN

### 4.1 Actualizar LOG_CAMBIOS

```
Path: [RUTA_ABSOLUTA_DEL_LOG — ej: /home/x/MontuMS/docs/LOG_CAMBIOS.md]
Instruccion: insertar al INICIO del archivo (despues del header) el siguiente bloque:

## [YYYY-MM-DD] [TITULO_DEL_CAMBIO]
Contexto: [POR_QUE_SE_HIZO_ESTE_CAMBIO]
Cambios:
- [CAMBIO_1]
- [CAMBIO_2]

Luego ejecuta:
cd [RUTA_REPO] && git add [ARCHIVO] && git commit -m "docs: [YYYY-MM-DD] [TITULO]" && git push

Reporta el hash del commit.
```

---

### 4.2 Documentar nuevo servicio

```
Servicio: [NOMBRE_DEL_SERVICIO]
Host: [serverX | serveri3 | TO | otro]
Puerto: [PUERTO]
Compose path: [RUTA_AL_DOCKER_COMPOSE_O_NINGUNO]
Funcion: [QUE_HACE_ESTE_SERVICIO_EN_UNA_LINEA]
Estado: [OPERATIVO | EN PRUEBA | DEPRECADO]

Acciones:
1. INVENTARIO — agrega entrada al inventario de servicios del host correspondiente.
2. LOG — inserta entrada en LOG_CAMBIOS.md con fecha de hoy.
3. git add + git commit -m "docs: [YYYY-MM-DD] add [NOMBRE_SERVICIO]" + git push

Reporta el hash del commit.
```

---

## SECCIÓN 5 — NOTAS DE USO

**Regla de oro:** si el template tiene campos que no sabes como rellenar, el template esta mal elegido o la tarea no esta suficientemente definida. Define primero, dispara despues.

**Campos opcionales:** solo `referencia_visual` en el template 3.2 es estrictamente opcional. Todos los demas campos son obligatorios.

**Formato de fecha:** siempre `YYYY-MM-DD`. Sin excepciones.

**RCA primero:** si algo falla en produccion, usa siempre 2.2 antes de cualquier otra accion. No improvisar fixes directamente en produccion.

**Proceso de actualizacion:** esta biblioteca se actualiza via Rabin (template 4.1). No editar manualmente. Toda actualizacion debe quedar registrada en el LOG_CAMBIOS.md del repo MontuMS.
