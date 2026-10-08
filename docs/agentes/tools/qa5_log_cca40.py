import shutil
p = "/Users/montu/MontuMS/docs/LOG_CAMBIOS_2026.md"
shutil.copy(p, p + ".bak_pre_cca40_20261008")
s = open(p, encoding="utf-8").read()
linea = "═══════════════════════════════════════════════\n"
e = (linea + "2026-10-08 — Clave SQL de Cubigest expirada (renovada) + diagnostico scraper Coronel (bug de Cubigest, no nuestro)\n" + linea +
"""**Quién:** Montu (renovación de la clave en Cubigest), Miaude (reinicio/verificación), CCa-40 (diagnóstico del scraper, informe `docs/agentes/CCa40_coronel_scraper_20261008.md`).

**Contexto:** tras una caída de la VPN de Torres Ocaranza (06 al 08-10), al reconectar se detectó que la conexión SQL directa a Cubigest fallaba con error 18487 ("la contraseña de la cuenta expiró"). Montu renovó la clave del lado de Cubigest y la dejó en el `.env`; Miaude reinició el backend y verificó con una consulta real (`SELECT 1`) y con una corrida completa de `ejecutar_importacion()` (Calama y Cerrillos cargaron bien de inmediato). Esto resuelve la sincronización de "universo"/compromisos futuros, que llevaba horas fallando en casi cada ciclo.

**Hallazgo separado, sin relación con la clave:** el scraper de detalle por etiqueta de Coronel (`scraper_optisteel.py` / `importar_optisteel.py`) seguía fallando igual después de renovar la clave. CCa-40 investigó con bisección sistemática de rangos de fecha (sin workarounds a ciegas) y confirmó: es un **bug del propio Cubigest**, específico de Coronel — el servidor no ejecuta la descarga cuando la fecha inicial del rango es desde ayer en adelante, sin importar la fecha final, y el mismo rango funciona sin problema en Calama y Cerrillos. No hay ningún desplazamiento de fecha que evite el bug sin perder el propósito (traer trabajo futuro). Se descartó con evidencia que fuera un problema de nuestro scraper (formulario, VIEWSTATE, valor de sucursal — todo idéntico a las plantas que sí funcionan). Se corrigió un docstring desactualizado y se agregó un test de regresión con un fixture HTML redactado (sin datos reales de clientes/obras). El Cuadro de Programación de Coronel (la pantalla principal) no se ve afectado — solo el detalle usado por Producción por Máquina y el camino de adelanto vía SQL directo.

**Pendiente:** escalar la evidencia (tabla de fechas en el informe de CCa-40) a quien administra Cubigest en Torres Ocaranza, para que revisen el handler de descarga de Coronel.

""")
open(p, "w", encoding="utf-8").write(e + s)
print("OK")
