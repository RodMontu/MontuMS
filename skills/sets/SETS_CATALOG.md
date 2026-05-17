# Catálogo de Sets de Skills — Montuschi Consultores SpA
## Versión: 1.0 — Mayo 2026
## Uso: al iniciar CCa o un subagente, indicar qué set aplica para que cargue las skills correctas

---

## SET-01: Explorar cualquier repo (read-only, máxima seguridad)
**Cuándo:** primera vez que se analiza un codebase desconocido o después de inactividad
**Modelo recomendado:** qwen2.5-coder:7b (ccl)
**Skills a cargar:**
- universal/seguridad-universal.md
- roles/rol_explorador.md (= agente explorer existente)
**Instrucción de inicio:** "Modo read-only absoluto. Tu único output es un mapa del sistema."

---

## SET-02: Desarrollo backend OptiFierro
**Cuándo:** cualquier tarea de backend en OptiFierro (FastAPI, SQLite, Cubigest)
**Modelo recomendado:** claude-sonnet-4-* (cca) para lógica compleja / qwen2.5-coder:7b (ccl) para tareas atómicas
**Skills a cargar:**
- universal/seguridad-universal.md
- universal/infra_serverx.md (si trabaja desde serverX)
- roles/rol_backend_dev.md
- roles/rol_data_engineer.md
- proyectos/skill_proyecto_optifierro.md
**Instrucción de inicio:** "Stack: FastAPI + SQLite. Cubigest es READ-ONLY. Lee CLAUDE.md local antes de empezar."

---

## SET-03: QA OptiFierro pre-deploy
**Cuándo:** antes de cualquier deploy a TO (PROMETHEUS-AI-CORE)
**Modelo recomendado:** claude-sonnet-4-* (cca)
**Skills a cargar:**
- universal/seguridad-universal.md
- roles/rol_qa.md
- roles/rol_security_auditor.md
- proyectos/skill_proyecto_optifierro.md
**Instrucción de inicio:** "No modificas nada. Solo reportas. Ejecuta checklist de seguridad completo."

---

## SET-04: DevOps / infra serverX
**Cuándo:** cambios de Docker, nginx, Cloudflare, servicios en serverX o serveri3
**Modelo recomendado:** claude-sonnet-4-* (cca)
**Skills a cargar:**
- universal/seguridad-universal.md
- universal/infra_serverx.md
- roles/rol_sysadmin.md
- roles/rol_devops.md
**Instrucción de inicio:** "Valida con devops-guardian antes de ejecutar cualquier cambio de infra."

---

## SET-05: Documentación pura
**Cuándo:** actualizar INVENTARIO_MAESTRO.md, LOG_CAMBIOS, CLAUDE.md, READMEs
**Modelo recomendado:** qwen2.5-coder:7b (ccl) / ccqwen
**Skills a cargar:**
- universal/seguridad-universal.md
- roles/rol_documentador.md (= agente doc-updater existente)
**Instrucción de inicio:** "Solo escribes en archivos .md. No tocas código fuente."

---

## SET-06: Nuevo proyecto (fase de análisis)
**Cuándo:** al arrancar cualquier proyecto nuevo (OF etapa 2, nuevo cliente)
**Modelo recomendado:** claude-sonnet-4-* (cca) — Miaude dirige
**Skills a cargar:**
- universal/seguridad-universal.md
- roles/rol_analista_negocio.md
- roles/rol_arquitecto.md
**Instrucción de inicio:** "Fase 0: mapear proceso de negocio ANTES de proponer tecnología. Output: Ficha de Requerimientos."

---

## SET-07: Auditoría de seguridad (pre-entrega cliente)
**Cuándo:** antes de entregar cualquier sistema a un cliente (TO u otro)
**Modelo recomendado:** claude-sonnet-4-* (cca) — este set NO se delega a modelos locales
**Skills a cargar:**
- universal/seguridad-universal.md
- roles/rol_security_auditor.md
- roles/rol_change_manager.md
- proyectos/[skill del proyecto correspondiente]
**Instrucción de inicio:** "Auditoría formal pre-entrega. Output: informe de seguridad firmable para el cliente."

---

## SET-08: Soporte Clawdio / Hermes
**Cuándo:** modificaciones al sistema Clawdio en serveri3
**Modelo recomendado:** claude-sonnet-4-* (cca)
**Skills a cargar:**
- universal/seguridad-universal.md
- roles/rol_sysadmin.md
- proyectos/skill_proyecto_clawdio.md
**Instrucción de inicio:** "Extrema precaución. Clawdio es 24/7. Cambios en SOUL.md y config.yaml requieren confirmación de Montu."

---

## SET-09: Documentar infra personal + commit MontuMS
Cuando: despues de cualquier cambio de infra en el ecosistema Montuschi
Modelo recomendado: ccnemo3 o ccgpt120 (NO usar Rabin/Clawdio para commits)
Skills a cargar:
- universal/seguridad-universal.md
- roles/rol_documentador.md
- proyectos/skill_doc_montuMS.md
Instruccion de inicio: Working dir ~/MontuMS/ en serverX. Pull primero. Solo archivos .md.

---

## SET-10: Documentar cambio OptiFierro + commit repo
Cuando: despues de cambio funcional en OptiFierro V2 que amerite registro
Modelo recomendado: el agente activo en la sesion. Miaude decide cual ejecuta.
Opciones: cca / ccnemo3 / ccgpt120 / ccqwen3
Skills a cargar:
- universal/seguridad-universal.md
- roles/rol_documentador.md
- proyectos/skill_doc_optifierro.md
- proyectos/skill_proyecto_optifierro.md
Instruccion de inicio: Solo .md de documentacion. Verificacion seguridad pre-commit obligatoria.

---

## NOTA GENERAL SOBRE DOCUMENTACION Y GITHUB
Rabin (Clawdio) queda excluido de tareas de commit a GitHub.
Su rol se limita a notificar resultados por Telegram.
La escritura en repos GitHub es responsabilidad exclusiva de agentes CC.
