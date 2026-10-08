# CCa-32 — Completar bitacora_accesos_torres_ocaranza.md: 24-09 (tarde) al 05-10

**Fecha de ejecución:** 2026-10-05. **Agente:** CCa (Claude Code), tarea de solo documentación.

## Qué se hizo

Respaldo previo: `bitacora_accesos_torres_ocaranza.md.bak_pre_cca32_20261005`. Agregado al final del
documento (cronológico ascendente, sin tocar entradas previas). Verificado con `diff` contra el respaldo:
**94 líneas agregadas, 0 líneas eliminadas** (`grep -c '^<'` = 0, `grep -c '^>'` = 94).

Se agregaron 9 entradas:

1. **2026-09-25** — QA cruzada "semana 1" (Miaude, solo lectura) + deploy de 5 ramas (universo de fechas,
   QA-A-01/02/03, swap de etiqueta del Gantt). Marcada con la advertencia de desfase de reloj que la propia
   fuente (`tablero_coordinacion_spp.md`) deja explícita: no está claro si el trabajo real fue 25-09 o 26-09.
2. **2026-09-26 (noche)** — 3 deploys: fix del join de averías Cubigest + fusión siempre, sube cadencia del
   job de sync A4 a 30 min, cajita gris por etapa confirmada en Cubigest.
3. **2026-09-27 (madrugada)** — 2 deploys: zoom horizontal del Gantt (B47), fix de ventana de averías (2
   bugs, uno de ellos el formato de fecha vs Cubigest).
4. **2026-09-28** — 2 deploys: estado efectivo unificado de máquinas, pipeline unificado de generación
   auto/manual.
5. **2026-09-29** — GAN2 "cajita = viaje" (implementación noche del 28-09, deploy 29-09) + 7
   fixes/features del día (adelanto automático, operador real, zoom sticky, sesión 8h).
6. **2026-09-30** — Investigación SSL intermitente a Cubigest + migración de adelanto y Bolsa OptiSteel a
   scraper HTTP.
7. **2026-10-01** — INCIDENTE: login caído ("database is locked") + fix WAL/busy_timeout, reanclaje del
   scheduler, retry a Cubigest.
8. **Nota 2026-10-02 al 2026-10-04** — sin commits ni accesos encontrados contra TO en ninguna fuente
   permitida; se aclara que la entrada de Pecas del 02-10 en `LOG_CAMBIOS_2026.md` es sobre serverX, un
   sistema distinto de Torres Ocaranza, y por eso no se incluye.
9. **2026-10-05** — CCa-30 (Ola 0, pendiente de autoreporte), CCa-31 (cerrado), CCa-32 (esta tarea) y la
   verificación directa de Miaude en TO (hechos entregados directamente por la Coordinadora, sin escrituras).

## Fuentes usadas

- `docs/agentes/QA_cruzada_semana1_20260925.md`, `CCa_gantt_etapa_gris_20260926.md`,
  `CCa_fix_ventana_averias_20260927.md`, `CCa_cajita_viaje_20260929.md`, `CCa31_log_29sep_01oct_20261005.md`.
- `docs/LOG_CAMBIOS_2026.md` (entradas 26-09 a 02-10, ya completadas por CCa-31).
- `docs/tablero_coordinacion_spp.md` (sección "DEPLOY 25-09" y "PENDIENTES CONSOLIDADOS", con la advertencia
  de desfase de reloj) y `docs/pendientes_sistema_planificador.md` (fila B48, fila CCa-29).
- `git log --all --format='%h|%ad|%an|%s' --date=iso --since=2026-09-24 --until=2026-10-06` en TO (único
  acceso propio de CCa-32 a TO, solo lectura) — confirmó fecha/hora exacta de cada commit citado arriba y
  que no hay ningún commit entre el 2026-10-02 y el 2026-10-04.
- Hechos del 05-10 entregados directamente por la Coordinadora (Miaude) en el encargo de esta tarea.

## Marcado como NO VERIFICADO / AUTOREPORTE sin evidencia objetiva

- **Fecha real del trabajo del 25-09** (vs. 26-09) — la propia fuente lo deja abierto.
- **Si la rama `cajita-viaje-deploy` (29-09) llegó a mergearse a `master`** — ningún commit del rango
  confirma "push a origin/master" (mismo hallazgo que ya había señalado CCa-31).
- **5 informes citados en commits/LOG que no están copiados en `MontuMS/docs/agentes/`** (corregido de "3" por Miaude, 05-10):
  `CCa_averias_cubigest_20260926.md`, `CCa_gantt_zoom_20260926.md`, `CCa_averias_estado_unificado_20260928.md`,
  `CCa_migracion_scraper_optisteel_20260930.md`, `CCa_investigacion_lock_horario_scraper_20261001.md`.
- **Verificación/deploy explícito de los commits `332f98c` (28-09) y del grupo de 7 commits del 29-09**
  (adelanto automático, zoom sticky, sesión 8h) — el LOG los marca "DESPLEGADO" pero no se encontró un
  informe de agente dedicado que detalle el comando de deploy o la verificación end-to-end.
- **Resultado de la verificación visual de Montu** de las corridas de las 08:10 posteriores al deploy de
  GAN2 (29-09) y al incidente del 01-10 — pendientes reales señalados en `pendientes_sistema_planificador.md`.
- **CCa-30 (05-10):** su informe no existe todavía (log vacío) — entrada marcada "PENDIENTE de autoreporte".
- **Accesos de la Coordinadora vía chat entre el 25-09 y el 04-10** que no quedaron reflejados en un
  commit o informe: se deja la línea estándar "sin registro objetivo local" en cada entrada, según instrucción.

## Lo que NO se hizo (fuera de alcance de esta tarea)

No se editó ninguna entrada existente de la bitácora ni de otro archivo, no se incluyeron credenciales ni
cadenas de conexión, no se ejecutó nada de La Biblioteca, y el único acceso a TO fue el `git log` de solo
lectura citado arriba (sin tocar el working tree, sin `docker`, sin SELECT a Cubigest).


## Correcciones posteriores (Miaude, 05-10)
- Entrada 2026-09-28 de la bitácora: `332f98c` (pipeline unificado auto/manual) NO está en `master` ni fue desplegado; existe solo en la rama `unificar-generacion-auto-manual` (verificado con `git merge-base --is-ancestor` en TO). Título y línea corregidos; respaldo `.bak_pre_correccion332f98c_20261005`.
- Entrada 2026-09-29: "worktree" reemplazado por "rama" (no hay worktree aparte); respaldo `.bak_pre_correccion_worktree_20261005`.
- Fecha real del trabajo del 25-09 (25 vs 26): los 5 commits del deploy tienen timestamp 2026-09-25 09:36 -0300 en git; no hay evidencia adicional, sigue NO VERIFICADO.
