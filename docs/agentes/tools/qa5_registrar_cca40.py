import sys
sys.path.insert(0, "/app/biblioteca")
import mcp_tools as m
r = m.registrar_cambio(
    "LOG_CAMBIOS_2026.md",
    "2026-10-08 — Diagnostico scraper Coronel (bug de Cubigest, no nuestro) + expiracion de clave SQL",
    ("Contraseña de la cuenta SQL de Cubigest expiro (error 18487), bloqueando la sincronizacion de "
     "compromisos futuros ('universo') en todas las sucursales; Montu la renovo del lado de Cubigest, "
     "se actualizo el .env y se reinicio el backend, verificado con una consulta real. Aparte, el scraper "
     "de detalle (trabajos por etiqueta) de Coronel seguia fallando; CCa-40 investigo con biseccion de "
     "rangos de fecha y confirmo que es un bug del propio Cubigest especifico de Coronel (el servidor no "
     "ejecuta la descarga para fechas desde ayer en adelante, independiente del rango), no reproducible en "
     "Calama ni Cerrillos con los mismos rangos; no se aplico ningun workaround a ciegas, se corrigio un "
     "docstring desactualizado y se agrego un test de regresion. Pendiente: escalar a soporte de Cubigest."),
    "SPP, OptiFierro, Cubigest, Coronel, scraper, contraseña-expirada, CCa-40, universo",
    "log_cambio",
)
print(r)
