# Skill de Proyecto: OptiFierro V2
## Versión: 1.0 — Mayo 2026
## Cliente: Torres Ocaranza (TO)
## Contactos: Gustavo Godoy (Gerente Logística, SuperAdmin), Nelson Bustos (Gerente Operaciones, Admin)
## Jefes de planta: Francisco Ramos (Calama), José Auger (Cerrillos), Remiz Rivano (Coronel)

---

## Descripción del sistema
Sistema de planificación de la producción de acero para Torres Ocaranza.
Tres sucursales operativas: Calama, Cerrillos, Coronel.
Integra datos de Cubigest (ERP del cliente) vía SQL Server READ-ONLY.

## Stack tecnológico
- Backend: FastAPI (Python) — uvicorn en puerto 3001
- Frontend: React + TypeScript + Tailwind CSS v4 — build estático servido por nginx
- DB propia: SQLite (optifierro_v2.db) — lectura/escritura
- DB cliente: SQL Server Cubigest en 192.168.1.195 — READ-ONLY ABSOLUTO
- Entorno producción: PROMETHEUS-AI-CORE (192.168.1.65, Windows 11, user OptiFierro)
- Git: GitHub privado RodMontu/optifierro (fuente de verdad)

## Mapeos críticos — NUNCA cambiar sin validación explícita
```python
# sucursal_id en SQLite ↔ BodSucCod en Cubigest
_BODSUC_MAP = {1: 2, 10: 1, 14: 3}
# Calama: sucursal_id=1, BodSucCod=2, prefijo material='2'
# Cerrillos: sucursal_id=10, BodSucCod=1, prefijo material='1'
# Coronel: sucursal_id=14, BodSucCod=3, prefijo material='3'

# Joins cross-tabla: normalizar con codigo[1:] (quitar primer caracter)
```

## Usuarios del sistema y permisos
- Gustavo Godoy: SuperAdmin — acceso total + configuración
- Nelson Bustos: Admin — acceso operativo sin configuración de sistema
- Jefes de planta: Visualizador — solo su sucursal

## Tablas Cubigest involucradas (READ-ONLY)
- TOLTDA, TOREN, TORREON1 — Calama
- TOSOL, TOGENUA, TMAESTRANZA — Coronel
- Vista de OC pendientes: INFORMAT_Vista_OrdenesCompra (permisos SELECT pendientes de Roberto)

## BACKLOG CRÍTICO ACTIVO
- BACKLOG-MP01-ROBERTO: Roberto debe otorgar SELECT en tablas Cubigest para OC pendientes (P18 bloqueado)

## Reglas de negocio críticas
- El primer caracter del código de material indica su sucursal ('1', '2', '3')
- Joins entre tablas deben normalizar el código quitando el prefijo
- La asistencia de operadores se obtiene de Geovictoria (API en puerto 8002)
- El motor de optimización prioriza: 1) Días Atrasados, 2) Días Restantes, 3) Fecha IT
- Penalización de Setup: 15 min por cambio de diámetro

## Proceso de deploy en TO
1. Backup de optifierro_v2.db en TO
2. git pull en TO (Git Bash)
3. Si hay cambios de backend: reiniciar uvicorn
4. Si hay cambios de frontend: npm run build → copiar dist/ al directorio nginx
5. Avisar a Gustavo que el sistema fue actualizado
6. Registrar en LOG_CAMBIOS_2026.md

## Archivos y rutas en TO
- Repo: C:\Users\OptiFierro\Desktop\optifierro (Git Bash path: ~/Desktop/optifierro)
- DB: ~/Desktop/optifferro/optifierro_v2.db (NUNCA en .gitignore)
- Backend: ~/Desktop/optifierro/backend/
- Frontend: ~/Desktop/optifierro/frontend/

## Lo que NO se toca en Cubigest
Todo. Sin excepción. Solo SELECT.
