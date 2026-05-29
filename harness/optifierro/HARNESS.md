# HARNESS — OptiFierro V2
**Versión:** 1.0
**Proyecto:** OptiFierro V2 — Sistema de Planificación Torres Ocaranza
**Fecha creación:** 2026-05-29
**Última actualización:** 2026-05-29
**Stack:** FastAPI / React / Vite / TypeScript / Tailwind v4 / SQLite / SQL Server Cubigest
**Servidores:** PROMETHEUS-AI-CORE 192.168.1.65 (producción Windows 11)

---

## 1. FORBIDDEN_PATTERNS

| ID | Patrón prohibido | Motivo | Origen |
|---|---|---|---|
| FP-001 | Usar `localhost` o `host.docker.internal` para comunicación inter-contenedor | Los contenedores en la misma compose network deben usar el hostname del servicio (ej: `geovictoria-api:8002`). localhost apunta al contenedor mismo, no al vecino. | QA sesión #7 — bug crítico Docker networking |
| FP-002 | Modificar `_BODSUC_MAP = {1:2, 10:1, 14:3}` en motor_v2.py | Mapping crítico sucursal_id interno → Cubigest SucCod. Calama=1→2, Cerrillos=10→1, Santiago, Coronel=14→3. Cambiar rompe todas las consultas a Cubigest. | Regla arquitectónica inamovible |
| FP-003 | Agregar filtro por peso >= N kg en consultas de bolsa de trabajo | Filtro >=1500kg ocultaba ~55% del trabajo real de Coronel. El motor no filtra por peso — eso es decisión del planificador humano. | QA sesión #8 — bug crítico datos Coronel |
| FP-004 | Hacer `docker restart` cuando cambian variables de entorno | Variables de entorno solo se aplican con `--force-recreate`. Restart no las recarga. Usar: `docker compose up -d --force-recreate [servicio]` | Bug de configuración recurrente |
| FP-005 | Asumir que sucursal_id en código = SucCod en Cubigest | Son distintos. El carácter inicial del código de material indica sucursal Cubigest: 1=Cerrillos, 2=Calama, 3=Coronel. Siempre usar `_BODSUC_MAP` para traducir. | Regla de mapeo de datos |

---

## 2. ARCHITECTURAL_RULES

| ID | Regla | Enforcement | Herramienta |
|---|---|---|---|
| AR-001 | Layering de dependencias: Types → Config → Repo → Service → Runtime → UI | Revisión manual en PR + CCa evalúa imports | Code review |
| AR-002 | Cubigest DB (SQL Server 192.168.1.195) = solo lectura. Nunca INSERT/UPDATE/DELETE. | No hay credenciales de escritura disponibles. Si se intenta, falla con permisos. | SQL Server permissions |
| AR-003 | SQLite local = escritura permitida. Separar claramente queries SQLite vs Cubigest en código. | Usar prefijo de función: `get_local_*` vs `get_cubigest_*` | Naming convention |
| AR-004 | Ventana temporal de trabajo: retroactivo -30 días desde hoy. No modificar sin confirmar con Gustavo (BACKLOG-OF-01). | Test en motor_v2.py que valida ventana | Unit test |
| AR-005 | IDs de sucursal en SQLite: Calama=1, Cerrillos=10, Coronel=14. Nunca mezclar con SucCod de Cubigest. | Comentario obligatorio en todo código que maneje IDs de sucursal | Code convention |

---

## 3. PERMISSION_MATRIX

### Tier 1 — Autónomo
- Leer SQLite local (optifierro.db)
- Leer SQL Server Cubigest (solo SELECT)
- Ejecutar motor_v2.py en modo dry-run
- Correr tests unitarios y de integración
- Leer logs de FastAPI

### Tier 2 — Requiere confirmación de Montu
- Modificar motor_v2.py o cualquier archivo de lógica de negocio
- Cambiar docker-compose.yml en producción (TO)
- Modificar queries a Cubigest
- Actualizar dependencias (requirements.txt)
- Deployment a PROMETHEUS-AI-CORE

### Tier 3 — NUNCA autónomo
- INSERT/UPDATE/DELETE en Cubigest (no hay credenciales de escritura)
- Modificar _BODSUC_MAP
- Eliminar tablas o datos de SQLite de producción
- Cambiar credenciales de conexión Cubigest
- Push directo a rama main sin PR

---

## 4. FAILURE_LOG

| Fecha | Módulo | Error detectado | Causa raíz | Corrección aplicada | Regla generada |
|---|---|---|---|---|---|
| 2026-05 | Docker / networking | API containers llamando localhost entre sí → timeout | Containers en misma compose network deben usar hostname de servicio, no localhost | Cambiar URLs de localhost a nombre de servicio inter-contenedor | FP-001 |
| 2026-05 | motor_v2.py | bolsa_de_trabajo mostraba 0 kg para todas las OCs | append() de sites no estaba siendo llamado correctamente | Fix en lógica de append en motor_v2.py | FP-003 (relacionado) |
| 2026-05 | Frontend / badge | Turno A/B badge mostraba valor incorrecto por race condition | Cálculo del badge en frontend dependía de estado no sincronizado | Mover lógica de badge al backend para cálculo determinístico | AR-001 (layering) |
| 2026-05 | motor_v2.py / Coronel | ~55% de OCs de Coronel no aparecían en planificación | Filtro >=1500kg incorrecto aplicado a bolsa de trabajo | Eliminar filtro de peso del motor — no corresponde al motor decidir esto | FP-003 |
