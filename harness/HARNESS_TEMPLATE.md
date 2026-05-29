# HARNESS — [NOMBRE_PROYECTO]
**Versión:** 1.0
**Proyecto:** [NOMBRE]
**Fecha creación:** [FECHA]
**Última actualización:** [FECHA]

---

## 1. FORBIDDEN_PATTERNS
> Acciones que ningún agente puede ejecutar en este proyecto bajo ninguna circunstancia.
> Cada entrada aquí tiene origen en un fallo real (ver FAILURE_LOG).

| ID | Patrón prohibido | Motivo | Origen |
|---|---|---|---|
| FP-001 | [DESCRIBIR ACCIÓN] | [POR QUÉ ES PELIGROSO] | [FALLO QUE LO ORIGINÓ] |

---

## 2. ARCHITECTURAL_RULES
> Reglas estructurales del proyecto. No son sugerencias — se verifican por scripts/linters/hooks.

| ID | Regla | Enforcement | Herramienta |
|---|---|---|---|
| AR-001 | [REGLA] | [CÓMO SE VERIFICA] | [SCRIPT O LINTER] |

---

## 3. PERMISSION_MATRIX

### Tier 1 — Autónomo (sin confirmación de Montu)
- Leer archivos del proyecto
- Ejecutar tests y linters
- Consultar DB en modo read-only
- Correr builds locales

### Tier 2 — Requiere confirmación explícita
- Modificar archivos de configuración (.env, docker-compose.yml)
- Escribir o modificar datos en DB
- Push a ramas non-main

### Tier 3 — NUNCA autónomo
- Eliminar datos, archivos o tablas
- Modificar credenciales o secrets
- Push a main/production
- Cambios en schema de DB de producción

---

## 4. FAILURE_LOG
> Registro de fallos de agentes en este proyecto.
> Principio Hashimoto: cada entrada aquí DEBE generar una regla en FORBIDDEN_PATTERNS o ARCHITECTURAL_RULES.

| Fecha | Módulo | Error detectado | Causa raíz | Corrección aplicada | Regla generada |
|---|---|---|---|---|---|
