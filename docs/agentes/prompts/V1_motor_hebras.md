# VENTANA V1 — MOTOR: HEBRAS-01 (Ola 1)
Antes de todo: lee `/Users/montu/MontuMS/docs/agentes/prompts/00_CONTEXTO_BASE_OLA1.md` y aplica sus reglas.

## Tu carril
**Punto:** BACKLOG-HEBRAS-01 — el Motor no toma las hebras reales que cada jefe de planta ingresa en Gestor de Maquinas -> pestana Hebras.
**Archivo unico que puedes tocar:** `backend/motor_v2.py` (solo la carga de hebras). **Prohibido:** `routers/programacion.py`, `GestorProgramacion.tsx` (los tiene V2/V3).

## Diagnostico ya hecho (CCa-1, verificalo tu con codigo real antes de actuar)
- UI escribe en SQLite tabla `hebras` (`routers/maquinas.py`). El Motor usa `Maestro_operadores_maquinas.xlsx`, cargado UNA vez al boot
  (`motor_v2.py:283-289`), Excel con mtime 2026-03-19; `cargar_desde_sqlite()` sobreescribe diametros/operadores/rutas/restricciones pero NUNCA hebras.
- Efecto medido: Coronel, Dobladoras 2/3/4 = 3-10 hebras en SQLite; el Motor usa 1 -> subestima capacidad hasta 10x.
- Bug secundario: filtro `val in (1,2)` en `motor_v2.py:287` descartaria esos valores reales aunque se corrigiera el Excel.
- Fuera de alcance (solo anotar en pendientes): tercera via de escritura `run_multi_sucursal.py` (fix_hebras_*.sql) y el checkout "VM-OF" (HEBRAS-02).

## Pasos
1. Consulta Graphify (blast radius de `cargar_desde_sqlite()` y de quien consume hebras). Confirma con `archivo:linea` como entra "hebras" en el calculo de duracion/capacidad (multiplicador de throughput? divisor de tiempo?).
2. Foto ANTES: tabla `hebras` por sucursal vs valor que el Motor usa hoy por maquina (SELECT en la DB del contenedor `optifierro-backend`). Guardala en el LOG.
3. Fix minimo: `cargar_desde_sqlite()` lee hebras desde SQLite como fuente de verdad (mismo patron que ya usa para diametros/restricciones); elimina el filtro `val in (1,2)`.
   Maquina sin fila en SQLite -> mantener el comportamiento actual (default previo), sin inventar valores. Ejecuta con CCa o directo; el diff lo revisas tu.
4. Verificacion (contra el backend real, no aislada): a) foto DESPUES: Coronel Dobladoras 2/3/4 usan sus 3-10 hebras reales; b) Calama y Cerrillos sin cambios inesperados;
   c) un "Generar Programacion" de prueba en un dia/turno con datos reales compara duraciones antes/despues para 2-3 piezas (explica a Montu el cambio: piezas de Coronel en dobladoras quedaran MUCHO mas cortas — es lo correcto y los jefes de planta lo notaran).
   Limpia registros de prueba.
5. py_compile, diff a Montu, OK, commit (`fix(motor): hebras se leen desde SQLite, quitar filtro (1,2) — HEBRAS-01`), pide turno de deploy a la Coordinadora, regenera Graphify tras el commit.
6. Reporta segun protocolo (RESUMEN <=15 lineas). Este commit debe existir ANTES de que arranque B16 (Ola 2), que tambien toca `motor_v2.py`.
