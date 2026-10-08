import sys
sys.path.insert(0, "/app/biblioteca")
import mcp_tools as m

entradas = [
    dict(
        archivo="LOG_CAMBIOS_2026.md", seccion="2026-10-05 (noche) — DEPLOY Ola 1",
        resumen=("Deploy de la Ola 1 del QA del SPP tras QA en vivo de Montu (05-10): F9 endpoint de version "
                 "y VersionWatcher con recarga automatica, cache-control correcto en nginx; F5 Vista Semanal "
                 "reconstruida desde el Cuadro de Programacion real de Cubigest (no desde SQL directo), "
                 "separando Fierro Preparado de Largo Comercial; F8 ribete de adelantado calculado desde el "
                 "Cuadro en todas las rutas, ribete de acero distinto de A630, elimina el concepto 'inminente'; "
                 "F4 el Motor y los gestores distinguen operador de ayudante solo por el cargo real de "
                 "Geovictoria, maquina detenida no muestra operador, nombre de operador resuelto por sucursal "
                 "para evitar mezclar personas homonimas entre plantas. Durante el deploy se detecto y reparo "
                 "una corrupcion de indices SQLite en la base de produccion (historial_asignaciones), sin "
                 "perdida de datos."),
        tags="SPP, OptiFierro, deploy, Ola-1, vista-semanal, ribetes, operadores, Geovictoria, VersionWatcher, cuadro-programacion, sqlite-corrupcion",
        tipo="log_cambio",
    ),
    dict(
        archivo="LOG_CAMBIOS_2026.md", seccion="2026-10-05 — FIX GAN2 tras Generar",
        resumen=("Bug encontrado por Montu horas despues del deploy de la Ola 1: al presionar el boton "
                 "'Generar' en el Planificador, el Gantt volvia a mostrar una cajita por etiqueta en vez de "
                 "una por viaje (regresion de la agrupacion GAN2 del 29-09). Causa: la respuesta de "
                 "POST /generar trae las tareas sin agrupar, y la pantalla no volvia a leer GET /programacion "
                 "(que si agrupa) despues de generar. Fix de una linea: releer tras generar. Corregido solo "
                 "con rebuild de frontend, sin tocar el backend."),
        tags="SPP, OptiFierro, GAN2, cajita-viaje, bug, gantt, frontend, regresion",
        tipo="log_cambio",
    ),
    dict(
        archivo="LOG_CAMBIOS_2026.md", seccion="2026-10-06 — FIX URGENTES y 7 bajas",
        resumen=("Segunda ronda de QA en vivo de Montu (06-10), con las 3 plantas a carga completa tras la "
                 "Ola 1. Se corrigieron 4 problemas: (1) colision de nombre de usuario entre dos colaboradores "
                 "de la misma sucursal, causada por el sincronizador de operadores desde Geovictoria (no "
                 "chequeaba colisiones dentro del mismo lote); (2) una averia manual de una maquina de Calama "
                 "que nunca se habia cerrado, con antiguedad de meses, y que el sistema no caduca por diseño; "
                 "(3) el marcador de etapa confirmada en Cubigest (cajita gris e inamovible) no se reaplicaba "
                 "al leer un dia pasado desde el respaldo en SQLite, solo en la generacion en vivo; "
                 "(4) VersionWatcher no detectaba un despliegue de solo-frontend (como el fix anterior), ahora "
                 "tambien compara el bundle servido. Ademas se dieron de baja 7 colaboradores que ya no "
                 "aparecen en el listado completo de Geovictoria (regla: desaparecer del roster = eliminar del "
                 "SPP), limpiando tambien las maquinas que los tenian como operador habitual. Incidente de "
                 "proceso: el grafo de dependencias (Graphify) no se consulto antes de estas tareas; se "
                 "consulto retroactivamente antes de integrar, sin hallar riesgos, y se corrigio el "
                 "procedimiento para prompts futuros."),
        tags="SPP, OptiFierro, fix-urgente, Geovictoria, operadores, averias, Cubigest, gantt-etapa-gris, VersionWatcher, Graphify, bajas",
        tipo="log_cambio",
    ),
    dict(
        archivo="bitacora_accesos_torres_ocaranza.md", seccion="2026-10-06 (mañana) — fixes urgentes y deploy",
        resumen=("Registro de accesos de la sesion del 06-10: ejecucion de 3 migraciones de datos contra la "
                 "base de produccion del SPP (colision de usuario, averia manual sin cerrar, bajas de "
                 "colaboradores), cada una probada antes contra copia, con respaldo e integrity_check "
                 "verificados antes y despues; merge de 3 ramas de trabajo, rebuild y deploy unico con "
                 "indisponibilidad breve; limpieza de worktrees de git (incluidos residuos de la Ola 1 del dia "
                 "anterior); regeneracion de Graphify; intento, sin exito por restriccion de permisos en modo "
                 "headless, de usar Antigravity (agy) via MCP para una prueba de conectividad SSH."),
        tags="bitacora, accesos, SPP, OptiFierro, migraciones, deploy, worktrees, Graphify, Antigravity",
        tipo="log_cambio",
    ),
]

for e in entradas:
    r = m.registrar_cambio(e["archivo"], e["seccion"], e["resumen"], e["tags"], e["tipo"])
    print(e["archivo"], "|", e["seccion"][:50], "->", r)
