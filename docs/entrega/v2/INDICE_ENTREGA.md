# Índice del Paquete de Entrega v2.0 — Sistema Planificador de la Producción (SPP)

**Fecha:** 2026-09-28 (redactado de forma autónoma, de madrugada, bajo la Metodología Sinérgica — Montu revisa
al despertar)
**Destinatarios:** Gerencia de Operaciones, Gerencia de Logística, Jefes de Planta (Cerrillos, Calama, Coronel)
y personal de TI de Torres Ocaranza
**Ubicación:** `/Users/montu/MontuMS/docs/entrega/v2/` (Mac Studio; equivalente a `/home/x/MontuMS/docs/entrega/v2/`
en serverX)
**Reemplaza a:** el paquete v1 (24-09-2026, en `/Users/montu/MontuMS/docs/entrega/`, sin subcarpeta `v2/`) — v1
queda como referencia histórica, no se modificó ni se debe usar como fuente vigente.

---

## 1. Documentos del paquete v2

1. **[`MANUAL_TECNICO_SPP.md`](./MANUAL_TECNICO_SPP.md)** — Manual de ingeniería para TI de TO: arquitectura de
   contenedores, puertos reales, fuentes de datos y mapeos de sucursal, inventario completo de las 33 tablas
   SQLite, reglas del Motor, scheduler y jobs (incluido el condicional `SYNC_HORARIO_ACTIVO`), endpoints,
   despliegue y rollback (no ensayado), monitoreo/diagnóstico, respaldos y mapa de archivos.
2. **[`FICHA_TECNICA_SPP.md`](./FICHA_TECNICA_SPP.md)** — Ficha formulario (ítem A12): stack técnico con
   versiones reales verificadas en el contenedor corriendo, dependencias, bases de datos, infraestructura física
   y cloud (on-premise, sin nube en runtime), dependencias con Cubigest/OptiSteel/GeoVictoria, riesgos
   normativos y normativas aplicables (todo como preguntas abiertas, sin afirmación legal).
3. **[`VERIFICACION_MANUAL_TECNICO.md`](./VERIFICACION_MANUAL_TECNICO.md)** — Tabla de trazabilidad
   afirmación → fuente → estado; lista de todo lo de v1 que era falso, incompleto o sin respaldo, con su
   corrección; hallazgos operativos para Montu.
4. **[`MANUAL_USUARIO_SPP.md`](./MANUAL_USUARIO_SPP.md)** — Manual operativo para jefes de planta y gerencias
   (redactado por otro proceso en paralelo sobre esta misma carpeta).
5. **[`GUIA_RAPIDA_JEFE_PLANTA.md`](./GUIA_RAPIDA_JEFE_PLANTA.md)** — Guía rápida de referencia (redactada por
   otro proceso en paralelo).
6. **[`VERIFICACION_MANUAL_USUARIO.md`](./VERIFICACION_MANUAL_USUARIO.md)** — Verificación del manual de usuario
   (redactada por otro proceso en paralelo).
7. **[`CAPTURAS_PENDIENTES.md`](./CAPTURAS_PENDIENTES.md)** — Capturas de pantalla pendientes de incorporar
   (redactado por otro proceso en paralelo).

> Los documentos 4–7 fueron escritos por otro proceso corriendo en paralelo sobre la misma carpeta `v2/`; este
> proceso (Manual Técnico, Ficha Técnica, Verificación e Índice) no los modificó, solo los enlaza.

---

## 2. "Por confirmar" — consolidado

### Infraestructura y hardware
- Especificaciones de CPU/RAM/disco del host Windows 11 Pro de TO.
- Origen exacto del mapeo de puertos de host `8001`/`3001`/`11434` (no está en `docker-compose.yml`; probable
  override local de Docker Desktop o configuración manual no versionada).
- Gestión del ciclo de vida del contenedor `optifierro-ollama` (no está declarado en `docker-compose.yml`).
- Configuración formal de túneles/VPN de soporte remoto hacia el servidor de TO.
- Existencia real y vigencia de imágenes Docker de rollback etiquetadas (mencionadas en v1, no confirmadas en
  esta redacción — correr `docker images` en TO antes de asumir que existen).

### Parámetros operativos y continuidad
- RTO/RPO comprometidos ante caída del servidor.
- Política formal de respaldo de `optifierro_v2.db` — **hoy no existe evidencia de respaldo automatizado**; solo
  copias manuales puntuales previas a intervenciones de riesgo (ver Manual Técnico sección 9).
- Integración con directorio corporativo (LDAP/Active Directory) para autenticación unificada.

### Aspectos normativos y legales (revisión con Montu / asesoría legal de TO)
- Tolerancia de ±15 min sobre marca GeoVictoria y descuento fijo de colación, frente a la doctrina de la
  Dirección del Trabajo.
- Régimen de 42 horas / turnos dinámicos (vigente desde el 01-03-2026 según los datos de planta) y su
  tratamiento en la parametrización de turnos y capacidad.
- Almacenamiento local de RUT, nombre y horarios de colaboradores (protección de datos personales).
- Deslinde de responsabilidad entre las sugerencias del Motor y la autoridad de prevención de riesgos en planta.
- Alineación de la fórmula de peso lineal (`diámetro²/162`) con NCh204 para fines de calidad/certificación.

### Del propio Motor / código (técnico, no legal)
- ~~Si el fix de solape de operador + tope de jornada dentro del bloque de auto-reparto ya se implementó~~ —
  **resuelto en auditoría 28-09-2026**: sí está implementado (commits `0a959e8` y `313d089`); `HARNESS.md`
  quedó desactualizado en este punto y debería corregirse (ver Manual Técnico, sección 4.8).

---

## 3. Estado del repositorio de TO para el traspaso (observado en solo lectura, 2026-09-28)

Verificado con `git status`, `git log`, `git branch -a` desde `ssh TO` sobre
`C:\Users\OptiFierro\Desktop\optifierro`. **Nada de lo siguiente fue modificado ni corregido por este proceso**
— es un inventario de observación para que quien reciba el sistema sepa en qué estado quedó el checkout.

### Últimos commits en `master` (rama activa, al día con `origin/master`)
```
f0a35fe docs: informe del fix de ventana de averias + bug de formato de fecha
f298721 fix(averias): ventana no debe excluir averias sin resolver + bug de formato de fecha vs Cubigest
bd11c3f feat(gantt): zoom horizontal + pan en la linea de tiempo
e635f6a docs(averias-cubigest): agrega seccion de la segunda vuelta (2 ajustes Montu 26-09)
4b93ac6 feat(motor): fusiona SIEMPRE averias_cubigest (no solo como fallback en vivo)
```

### Cambios sin confirmar (working tree sucio)
- **Modificados, no commiteados:** `AGENTS.md`, `HARNESS.md`.
- **Sin seguimiento (untracked):**
  - `archivos no clasificados/` (carpeta completa, contenido no inventariado en esta pasada)
  - `backend/build_kgshora_referencia.py`
  - `backend/diagnostico_kgshora.py`
  - `backend/diagnostico_metodologia.py`
  - `backend/kgshora_referencia.csvkgshora_referencia.csv` (nombre de archivo con extensión duplicada, probable
    error al generarlo)
  - `backend/motor_v2.py.bak_pre_fix_reparto_final_20260915` (copia de respaldo manual dentro del árbol)
  - `backend/routers/programacion.py.bak_pre_b18_bolsa_20260915_084116` (ídem)
  - `logs_cca/` (carpeta de logs de sesiones de agente)
  - `run_multi_sucursal.py`
  - `spp_query.py`

### Archivos `.bak`/backup de base de datos dentro del árbol (no en `.gitignore` aparente)
`backend/optifierro_v2.db.backup_20260330_2328`, `backend/optifierro_v2.db.TO_backup`,
`backend/optifierro_v2_BACKUP_20260728_133052.db`, `backend/optifierro_v2_BACKUP_20260730_082540_pre_t3.db`,
`backend/optifierro_v2_BACKUP_20260730_092945_pre_[nombre_colaborador]_fix.db` (nombre de archivo real redactado
en auditoría 28-09: incluía el apellido de un colaborador), `motor_v2_backup_MAQUINAS_ACTIVAS.txt`.
También `backend/routers/programacion.py.bak_pre_b18_bolsa_20260915_084116` (listado arriba).

### Ramas locales (además de `master`)
`b44b-capacidad-real`, `fix-decodificar`, `main`, `ola3-averias`, `ola3-gantt`, `qa-fixes-24`,
`respaldo/auditoria-tiempos-2026`, `sync-unificado`. Ninguna mostró commits pendientes de mergear a `master` en
las menciones de `tablero_coordinacion_spp.md` revisadas (varias corresponden a trabajo ya integrado por
merge/cherry-pick y no fueron eliminadas tras el merge) — **`POR CONFIRMAR` si alguna sigue teniendo trabajo
vivo** antes de borrarlas; no se borró ninguna en esta pasada (solo lectura).

### Remoto
`origin` → `github.com/RodMontu/Optifierro-V2`. `origin/HEAD` apunta a `origin/main`, pero la rama de trabajo
real y productiva es `master` (confirmado también en `CLAUDE.md` del workspace de Graphify: "rama `master`, no
`main` — `main` es una rama vacía que no se usa"). Esto es una fuente potencial de confusión para quien clone el
repo por primera vez con `git clone` simple (puede terminar en `main` vacío en vez de `master`).

### Grafo de dependencias Graphify
Último grafo regenerado en `/Users/montu/graphify-workspace/optifierro/graphify-out/`, construido sobre commit
`f298721x` (prefijo largo `f2987219`, mismo commit corto `f298721` del `git log` de arriba). El `HEAD` real de
`master` es `f0a35fe`, un commit más adelante — pero ese commit es puramente de documentación (informe del fix
de averías), sin cambios de código. **El grafo está, en la práctica, vigente para efectos de código**; falta
regenerarlo formalmente para reflejar el commit de docs más reciente, siguiendo la regla AR-008 de `HARNESS.md`.

### Acciones de higiene recomendadas antes del traspaso (no ejecutadas — decisión de Montu)
1. Decidir el destino de `AGENTS.md`/`HARNESS.md` modificados sin commitear: revisar el diff y commitear o
   descartar conscientemente (nunca descartar sin revisar — pueden contener reglas nuevas no guardadas).
2. Mover los archivos `.bak*`/`*BACKUP*`/`*_backup*` fuera del árbol de trabajo (o a una carpeta explícita
   `respaldos_manuales/` con `.gitignore`), para que dejen de aparecer como ruido en cada `git status`.
3. Revisar y clasificar `archivos no clasificados/` y `logs_cca/` — decidir si van al repo, a `.gitignore`, o se
   archivan aparte.
4. Confirmar si `backend/kgshora_referencia.csvkgshora_referencia.csv`,
   `backend/build_kgshora_referencia.py`, `backend/diagnostico_kgshora.py`, `backend/diagnostico_metodologia.py`,
   `run_multi_sucursal.py` y `spp_query.py` son herramientas de análisis vigentes o restos de una investigación
   puntual — si son restos, eliminarlos; si son vigentes, agregarlos al repo con un `.gitignore` que excluya sus
   salidas.
5. Depurar ramas locales ya integradas (`ola3-averias`, `ola3-gantt`, `qa-fixes-24`, `sync-unificado`,
   `b44b-capacidad-real`, `fix-decodificar`) tras confirmar con Montu que no tienen trabajo vivo pendiente.
6. Aclarar en `README`/`AGENTS.md` que la rama productiva es `master`, no `main` (que hoy queda vacía y es el
   `HEAD` por defecto del remoto) — riesgo de confusión para cualquier `git clone` nuevo.
7. Regenerar formalmente el grafo Graphify sobre el commit `f0a35fe` (o el que sea `HEAD` al momento del
   traspaso), por más que el delta sea solo documentación, para mantener la regla AR-008 sin excepciones.
8. Pinnear en `requirements.txt` las versiones exactas de los paquetes que hoy no la tienen (ver Ficha Técnica
   sección 1), usando como base la salida real de `pip freeze` capturada en este manual.

Ninguna de estas 8 acciones fue ejecutada por este proceso (solo lectura, sin tocar el repo de TO, según regla
de alcance de la tarea).
