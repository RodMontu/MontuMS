# TAREA CCa-30 — QA SPP 05-10: OLA 0 (diagnostico, SOLO LECTURA)

Eres CCa (Claude Code) operando para Rodrigo Montuschi ("Montu") desde su Mac Studio. El repo del SPP vive en el
host Windows "TO". Accedes SIEMPRE asi: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>" (Git Bash,
nunca PowerShell). Comandos docker en TO llevan el prefijo MSYS_NO_PATHCONV=1. Scripts auxiliares se suben al
`/tmp` del contenedor `optifierro-backend` (NUNCA a `/app`) y se borran al terminar.

Origen de esta tarea: Montu pidio un Plan de Trabajo a partir de su QA general del SPP del 05-10-2026 y lo aprobo
en esta fecha. Esta tarea es la Ola 0 (diagnostico). Miaude (la Coordinadora) lee tu informe y decide la Ola 1.

## CITAS LITERALES DE MONTU (fuente de cada requisito; no agregues nada que no este aqui)
- Adelanto: "no se cumplio la regla de ADELANTAR TRABAJOS HASTA COMPLETAR LA CAPACIDAD DE MINUTOS/HOMBRE (en maquinas) disponible en la jornada, esto DEBE CUMPLIRSE SIEMPRE todos los dias en todas las jornadas."
- Ribete: "Debemos chequear que los trabajos adelantados esten si o si con el ribete con linea negra segmentada, ya que solamente veo uno con ello, y al cruzar las ITs con el Cuadro de Programacion, veo que hay otros trabajos adelantados pero que no estan debidamente identificados."
- Ribete naranja: "ribete naranjo con linea segmentada enmarcando toda la cajita ... para acero de otra calidad que no sea el A630"; si ademas esta adelantada "debe llevar ambos ribetes juntos", uno por fuera del otro.
- Operadores: "nos basamos solamente en lo que Geovictoria dice que es operador (operador senior, operador junior, operador sin otra palabra); la unica excepcion es ayudante de operador". "Una maquina solamente puede ser operada por un Operador, no por un Ayudante". "Si una maquina esta detenida, entonces no puede tener operador asignado."
- Vista Semanal: "debe quedar igual ... debemos replicarlo tal cual" (informe Cuadro de Programacion de Cubigest, cuadro "Fierro Preparado", <=16 y >16; el cuadro "Fierro Punta Largo Comercial" queda aparte).
- Login/cache: sesion de 8 h se mantiene; el front debe consultar la version del backend y recargarse solo.

## REGLAS CARDINALES (obligatorias)
- SOLO LECTURA: sin edicion de codigo, sin commit, sin push, sin docker build/up/restart, sin POST /generar ni
  /reprogramar, sin escrituras a SQLite ni a Cubigest. Cubigest solo SELECT (via el contenedor).
- Graphify (`~/graphify-workspace/optifierro` en el Mac) se CONSULTA antes de afirmar quien depende de que.
- No extrapoles: si un dato no esta, escribe "NO VERIFICADO" y di que falta. Cita archivo:linea o salida real.
- Estado esperado: rama `cajita-viaje-deploy`, HEAD `c818ff6`, contenedores arriba desde 2026-10-04 18:07 UTC.
  Si no coincide, reportalo primero.

## TAREAS (en este orden; cada una con evidencia)
D0. Estado del repo y del adelanto por scraper: `git log -12`, diferencia entre `cajita-viaje-deploy` y `master`,
    y si todo lo de `cajita-viaje-deploy` esta en el contenedor desplegado. Confirma si la migracion del adelanto a
    `trabajos_optisteel` (commits 04e6bbf, 69690ab, 8cc136a, 93e4a3b, c818ff6) esta COMPLETA o parcial: que lee hoy
    `completar_con_adelanto`, si `_job_importar_optisteel` esta programado y cada cuanto, filas de `trabajos_optisteel`
    por sucursal y fecha del ultimo import, y si las columnas `largo` y `tipoAcero` existen y tienen datos.
D1. Corrida de las 08:10 del 05-10 en las 3 plantas: logs del contenedor (busca `adelanto`, `[ADEL`, errores SSL,
    scraper) y GET read-only de `/api/programacion` por sucursal (Calama=1, Cerrillos=10, Coronel=14). Para cada planta:
    (a) `metadata.capacidad` (capacidad_mh, saldo_mh, operadores_contados) y minutos libres por maquina tras la
    corrida; (b) para CADA cajita cuyo viaje/IT tenga fecha > hoy en `cuadro_programacion_optisteel`, si lleva
    `viene_de_futuro` o no; lista las que NO lo llevan y por que ruta entraron (asignacion normal de /generar,
    Bolsa, arrastre manual, adelanto); (c) si el adelanto corrio y que decidio por cada maquina ociosa
    (sin trabajo compatible / sin operador / fallo de fuente / otro). Hipotesis previa (NO confirmada): la herencia
    del grupo toma el estado de la primera etiqueta (`_construir_evento_grupo`, `dict(primero)`).
D2. Render real de los ribetes en `frontend/src/components/domain/GestorProgramacion.tsx`: lineas exactas de
    `vieneDeFuturo` (outline/color real, hoy celeste `#0ea5e9` segun CCa-8 o negro?), `esNoA630`, `esInminente`,
    `isDetenida`, `borderTop` de estado de maquina, `esVencido`, `esSoldable`. Responde: de donde sale el borde
    superior naranja punteado de la cajita "ROP-27/1 9,19 DE 20" de Coronel; si el contenedor de la fila tiene
    `overflow` que recortaria un `outline` externo; y si hay CSS/tooltip/leyenda que mencione "inminente".
D3. Operadores (Geovictoria vs SPP), 3 plantas, SIN TOSOL: por sucursal, ultimo dia con datos de
    `asistencia_colaboradores` (nombre, cargo) vs `operadores_matriz` y vs lo que muestra el Gantt/Gestor de
    Operadores. Clasifica: operador (cargo con "operador" salvo "ayudante de operador"), ayudante, otro cargo,
    en SPP pero ausente de Geovictoria 30 dias (candidato a desvinculado), en Geovictoria pero ausente del SPP.
    Casos obligatorios Coronel: Dilan Diaz, Matias Urra, Cristian Urra, Rafael Neira, Cristian Escalona
    (B23 lo registro como Mecanico Junior), hacuna/gacuna (B23: probable desvinculados), Hector Acuña vs Hector
    Guerrero. Rastrea de donde sale el nombre que el Gantt muestra por maquina (commit 5f1c354 "operador real asignado
    por el Motor") y por que no coincide con Geovictoria; y como decide hoy `_obtener_operadores_disponibles` /
    `/operadores_presentes` quien es ayudante (hay una `_es_ayudante`?). Verifica si una maquina DETENIDA puede
    quedar con operador asignado en el Gantt (caso Linea Corte Coronel).
D5. Cache y login: configuracion nginx real del contenedor `optifierro-frontend` y `curl -sI` de `/`, `/index.html` y
    un asset con hash (por localhost:3001 en TO); logica de expiracion de sesion/token (8 h) y por que Administracion
    pide re-login y la pantalla inicial no; si existe un endpoint de version/build del backend (`/api/health`,
    `/api/version` o similar) y si el frontend ya tiene un identificador de build inyectado por Vite.
D6. Vista Semanal vs Cuadro de Programacion: como se arma hoy `/api/programacion/semanal` (archivo:linea) y de que
    tabla/fuente sale. Verifica si `cuadro_programacion_optisteel` guarda diametro o la separacion <=16 / >16 y los
    kilos propuestos por viaje. Calcula, solo lectura, el equivalente para Coronel 05-11 oct y compara con el
    informe real de Cubigest (cuadro "Fierro Preparado", columnas Diam<=16 / Diam>16 / Total): lun 6.221/4.247/10.468,
    mar 622/4.110/4.732, mie 96/0/96, jue 0/0/0, vie 8.239/41.356/49.595, sab 0/0/0, totales 15.178/49.713/64.891.
    Calcula tambien Calama y Cerrillos (sin referencia: solo reporta). Indica si el scraper existente puede extraer
    ese bloque resumen directamente de la pagina del Cuadro.

## FORMATO DE SALIDA
Un unico informe en `/Users/montu/MontuMS/docs/agentes/CCa30_ola0_qa5_20261005.md` con una seccion por tarea
(D0, D1, D2, D3, D5, D6), cada una con: hallazgo, evidencia (comando/salida/archivo:linea), "NO VERIFICADO" donde
corresponda y, al final, un resumen de 15 lineas maximo con causa raiz probable por item. No toques otros archivos.
No registres nada en La Biblioteca.

## NO HAGAS
- No modifiques codigo, configuracion, base de datos ni contenedores. No hagas commit, push, merge ni deploy.
- No corrijas lo que encuentres: reportalo. No propongas cambios de alcance que Montu no pidio.
- No leas ni imprimas credenciales; si aparecen en un archivo, no las copies al informe.
- No supongas la causa raiz sin evidencia: si dos hipotesis calzan, listalas ambas con lo que falta para decidir.
