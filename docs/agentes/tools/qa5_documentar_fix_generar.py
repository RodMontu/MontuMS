import shutil
base = "/Users/montu/MontuMS/docs/"
linea = "═══════════════════════════════════════════════\n"
lp = base + "LOG_CAMBIOS_2026.md"
shutil.copy(lp, lp + ".bak_pre_fix_generar_20261005")
s = open(lp, encoding="utf-8").read()
e = (linea + "2026-10-05 — FIX GAN2: tras pulsar \"Generar\" el Gantt volvía a dibujar 1 cajita por etiqueta (commit 46f91fa)\n" + linea +
"""**Quién:** Miaude (directo).

**Síntoma (reportado por Montu, ≈17:44):** en Coronel el Gantt mostraba 1 cajita por etiqueta (47 cajitas, tooltip "Etiqueta 19 de 29") en vez de 1 por viaje.

**Causa raíz (con evidencia):** el backend respondía bien: `GET /api/programacion` devolvía 4 eventos agrupados (`cantidad_etiquetas` 15/2/10/20, `rango_etiquetas`). La agrupación GAN2 (`_agrupar_cajitas_por_viaje`, commit `19c2148`) se aplica solo al LEER (`GET`). Pero `handleGenerar` (`GestorProgramacion.tsx`, botón "Generar") reemplaza el estado del Gantt con las tareas crudas, por etiqueta, de la respuesta de `POST /api/programacion/generar`, y no vuelve a leer. El log del backend registra un `POST /generar` de Coronel a las ≈17:43. Es un defecto latente de GAN2 desde el 29-09 (no lo causó el deploy de la Ola 1, aunque el reinicio del backend y el nuevo pool de operadores llevaron a regenerar Coronel). Los demás flujos (reprogramar, deshacer, aplicar reparto) sí releen el GET.

**Fix:** `await fetchData(true)` al final de la rama de éxito de `handleGenerar` (4 líneas, frontend). Solo se reconstruyó y reinició el frontend (el backend no se tocó, no se perdieron planes en memoria). `tsc` limpio. Verificado en el navegador de Montu tras recargar: cajitas agrupadas ("Etiquetas 8-15 de 19 — Viaje ASR-277/1"), bundle `index--lYF-0dZ.js`.

**Pendiente derivado:** el vigilante de versión (F9) solo compara la versión del BACKEND: un despliegue solo de frontend no dispara la recarga automática (las pestañas abiertas necesitan F5 esta vez). Hay que agregar un identificador de build del frontend a la comparación.

""")
open(lp, "w", encoding="utf-8").write(e + s)

bp = base + "bitacora_accesos_torres_ocaranza.md"
shutil.copy(bp, bp + ".bak_pre_fix_generar_20261005")
b = open(bp, encoding="utf-8").read()
b = b.rstrip("\n") + """

---

## 2026-10-05 (noche, 2) — Diagnóstico y fix de la regresión visual de cajitas (Miaude)

**Campos comunes:** Sistema = TO (192.168.1.65), checkout `optifierro` (`cajita-viaje-deploy`, HEAD `46f91fa`). Sensibilidad: MEDIA (escrituras: rebuild y reinicio solo del contenedor `optifierro-frontend`, commit y merge `--ff-only`). Autorización: petición explícita de Montu ("solucionar esto, que es grave").

1. **≈17:45–17:49 (solo lectura):** `GET /api/programacion` (Coronel, turnos `dia` y `Día`) vía `curl` y `docker exec`; lectura de logs del backend (`POST /generar` registrado a las ≈17:43); lectura del código del frontend.
2. **≈17:46–17:52 — acceso al navegador de Montu mediante la extensión de Control de Chrome** (pestaña `192.168.1.65:3001`): lectura de DOM y de la respuesta de `/api/programacion`; para devolver resultados se cambió temporalmente `document.title` (restaurado a "Planificador TO"); a las ≈17:50 se ejecutó `location.reload()` en esa pestaña para cargar el nuevo frontend. No se pulsó ningún botón ni se modificaron datos.
3. **≈17:50 — Escritura:** commit `46f91fa` en `ola1-int`, `git merge --ff-only` en el checkout principal, `docker compose build --no-cache frontend` y `up -d frontend` (backend sin tocar). Junction temporal de `node_modules` en `optifierro_int/frontend` creado para `tsc` y retirado con `rmdir` (verificado; `node_modules` del principal intacto, 198 entradas).
"""
open(bp, "w", encoding="utf-8").write(b + "\n")
print("OK")
