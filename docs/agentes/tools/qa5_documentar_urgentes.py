import shutil
base = "/Users/montu/MontuMS/docs/"
linea = "═══════════════════════════════════════════════\n"
lp = base + "LOG_CAMBIOS_2026.md"
shutil.copy(lp, lp + ".bak_pre_urgentes_20261006")
s = open(lp, encoding="utf-8").read()
e = (linea + "2026-10-06 — FIX URGENTES: colisión jcastillo, avería manual sin cerrar (COIL 14), gris/candado en fallback histórico, VersionWatcher frontend, 7 bajas (commit 47c72c7)\n" + linea +
"""**Quién:** CCa-37 (jcastillo + averías, informe `docs/agentes/CCa37_urgentes_20261006.md`), CCa-38/39 (iniciaron, Miaude terminó y commiteó), Miaude (migraciones, merge, deploy).

**Contexto:** QA en vivo de Montu el 06-10 ~08:00, con jornada a carga completa en las 3 plantas (incluido adelanto). Ola previa: Ola 1 (05-10).

1. **Colisión de usuario "jcastillo" (Calama).** Causa raíz: `sincronizar_operadores_desde_gv` (`routers/admin.py`) deriva el username sin chequear colisión entre candidatos nuevos del mismo lote; dos personas con el mismo apellido paterno (Joan Ignacio Castillo Valderrama, Ayte; Joan Manuel Castillo Cisternas, Supervisor) quedaron con `Operador='jcastillo'` ambas, afectando también `PUT /api/operadores/{id}` (editaba las dos filas a la vez). Fix: desambiguación en el sync (`_desambiguar_username`). Decisión de Montu: el Supervisor conserva `jcastillo`; el Ayudante pasa a `jcastillov`. Migración `migrate_fix_jcastillo_20261006.py` ejecutada contra producción.
2. **Avería manual sin cerrar — COIL 14 (Calama).** Las 3 hipótesis del ticket (tests de ayer contaminando la BD, scheduler caído, bug de fusión) quedaron descartadas con evidencia: el sync corre cada 30 min y está al día. La causa real: una avería MANUAL de COIL 14 del 2026-03-23 nunca se cerró, y `estado_maquinas.py` no caduca la fuente manual por diseño (para que el jefe de planta la vea). Migración `migrate_levantar_coil14_20261006.py` ejecutada. Recomendación pendiente (no implementada): alertar en el frontend cuando una avería manual supere cierta antigüedad.
3. **Gris/candado no sobrevivía al fallback histórico.** Al leer un día sin eventos en memoria (p. ej. un día pasado, cayendo a `programacion_guardada`), `obtener_programacion` no reaplicaba `_marcar_etapas_congeladas` sobre el snapshot guardado — una cajita ya confirmada en Cubigest podía perder el gris al verla como historial. Fix: una llamada adicional a la función existente (`routers/programacion.py`). Gap documentado, no implementado: no existe una "vista de día completo en gris" como modo explícito — el mecanismo sigue siendo cajita por cajita.
4. **VersionWatcher no detectaba despliegues de solo-frontend** (como el fix del 05-10 de noche). Ahora compara también el bundle de Vite servido en `/` (por hash) contra el cargado en el documento, sin endpoint nuevo.
5. **7 bajas aplicadas** (regla: desaparecer del roster completo de Geovictoria, re-verificado contra el roster de HOY, no solo 30 días de asistencia): Aníbal García (Coronel), Héctor Acuña y Giovanni Acuña (Coronel, habituales de Dobladora 3/Línea Corte Coronel y Dobladora 4 respectivamente — limpiados también esos campos, que guardan NOMBRE completo, no username), Fabián Quezada, Jofran Medina, Miguel Gutiérrez, Gabriel Sepúlveda (Cerrillos). Migración `migrate_baja_desvinculados_20261006.py`. `operadores_matriz`: 70 → 63 filas.

**Proceso — Graphify no se consultó antes de estas 3 tareas** (miss de Miaude en los prompts de hoy, a diferencia del preludio de la Ola 1). Se consultó retroactivamente antes de integrar: sin colisiones de riesgo detectadas entre los archivos tocados. Regenerado tras el deploy (commit `47c72c7`): 6.801 nodos / 7.747 enlaces — **casi duplicó el conteo de ayer (3.745/4.680) sin una razón clara**; posible acumulación del workspace de Graphify entre regeneraciones sucesivas (modo "watch", no limpieza previa). Pendiente investigar antes de confiar en el conteo absoluto; las consultas de impacto por archivo (no afectadas por esto) siguen siendo confiables.

**Verificado en vivo (06-10, ~15:10):** `/api/version` responde; Calama (`sucursal_id=1`) Carro de Corte y COIL 14 operativas; operadores de Coronel = kgallegos, elara, rneira, dneira (los 7 de baja ya no aparecen); `integrity_check` = ok antes y después de las 3 migraciones.

**Pendiente:** prompt de prueba de SSH para Antigravity (agy) pendiente de que Montu confirme si pudo correrlo interactivamente (headless vía MCP quedó bloqueado); registro de hoy en La Biblioteca.
""")
open(lp, "w", encoding="utf-8").write(e + s)
print("OK LOG")
