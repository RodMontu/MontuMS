# HARNESS — Pegas V2
**Versión:** 0.1 (stub)
**Proyecto:** Pegas V2 — LinkedIn Job Scraper Multi-usuario
**Fecha creación:** 2026-05-29
**Stack:** FastAPI + Playwright + SQLite / serverX puerto 8000 / pegas.montuschi.cl
**Estado:** ✅ Deployado — harness a completar cuando retome desarrollo activo

---

## 1. FORBIDDEN_PATTERNS

| ID | Patrón prohibido | Motivo | Origen |
|---|---|---|---|
| FP-001 | Ejecutar Playwright en modo headless=False en producción | Crashea el contenedor Docker sin display. Usar headless=True siempre en Docker. | Comportamiento conocido |
| FP-002 | Almacenar credenciales de LinkedIn en código o variables de entorno sin cifrar | Riesgo de ban de cuenta + exposición de datos. Usar Cloudflare Zero Trust para auth. | Regla de seguridad |

---

## 2. ARCHITECTURAL_RULES

| ID | Regla | Enforcement | Herramienta |
|---|---|---|---|
| AR-001 | Auth vía Cloudflare Zero Trust — nunca exponer /api/* directamente a internet | Revisión de nginx config | Manual |
| AR-002 | SQLite = única DB. No introducir PostgreSQL sin aprobación de Montu. | Dockerfile review | Manual |

---

## 3. PERMISSION_MATRIX

### Tier 1 — Autónomo
- Leer SQLite, ejecutar scraping en modo dry-run, correr tests

### Tier 2 — Requiere confirmación
- Modificar Playwright selectors, cambiar lógica de scraping, actualizar dependencias

### Tier 3 — NUNCA autónomo
- Modificar credenciales LinkedIn almacenadas, cambiar Cloudflare Zero Trust config

---

## 4. FAILURE_LOG

| Fecha | Módulo | Error detectado | Causa raíz | Corrección aplicada | Regla generada |
|---|---|---|---|---|---|
