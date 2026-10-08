
---
# TAREA CCa-37 — URGENTE: colision de usuario "jcastillo" (Calama) + averias desactualizadas en Calama
TAG: `urg1` (rama `fix-urgente-1`, directorio `optifierro_urg1`). Informe: `CCa37_urgentes_20261006.md`.
Repo: ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro && <comando>". Crea tu worktree desde el HEAD actual (verifica
cual es con `git log -1 --format=%h`; hoy deberia ser `46f91fa` o posterior) con `git worktree add C:/Users/OptiFierro/Desktop/optifierro_urg1 -b fix-urgente-1 <HEAD>`.
NUNCA ejecutes pruebas (`python -m unittest`, pytest, scripts sueltos) con working directory sobre `optifierro/backend`
del checkout principal: la BD real (`optifierro_v2.db`) vive ahi. Copia la BD a tu worktree o usa `docker run --rm -v
<tu_worktree>/backend:/work <imagen> python -` para cualquier lectura/escritura de prueba. Commits locales, sin push.

## PARTE A — Colision "jcastillo" (URGENTE, decision de Montu)
Hoy el usuario `jcastillo` en sucursal 1 (Cerrillos) esta duplicado en `operadores_matriz`: una fila es Joan Ignacio
Castillo Valderrama (cargo Geovictoria: Ayte del Operador) y otra es Joan Manuel Castillo Cisternas (cargo: Supervisor).
Montu interpreta: "el Supervisor es el padre y el Ayudante es el hijo... el padre, por antiguedad, es quien debe
tener el usuario 'jcastillo'". DECISION: el Supervisor (Joan Manuel Castillo Cisternas) CONSERVA `jcastillo`; al
Ayudante (Joan Ignacio Castillo Valderrama) se le asigna un usuario nuevo y distinto.
1. Encuentra el origen de la fila duplicada: `operadores_matriz` (SQLite) se carga desde algun Excel maestro o
   proceso de alta (buscar en `main.py`/`routers/operadores.py`/scripts de import). Confirma si el duplicado esta
   tambien en el Excel maestro (ruta probable segun bitacora: `Maestro_operadores_maquinas.xlsx`) o solo en la BD.
2. Resuelve el duplicado en la fuente correcta (Excel y/o BD, segun donde viva): nuevo usuario para el Ayudante
   (propone uno por convencion: inicial+apellido, evitando colisiones existentes — revisa toda la tabla antes de
   fijarlo), MISMAS maquinas/turno que tenia antes esa fila (no se pierden datos), nombre y cargo intactos.
3. Verifica que NINGUN otro usuario este duplicado dentro de la MISMA sucursal en ninguna de las 3 plantas (un
   mismo usuario en sucursales distintas SI esta permitido, ya lo resolvimos ayer con `resolver_nombre_operador`).
4. Si el cambio de usuario requiere tocar algo en Geovictoria (improbable: Geovictoria identifica por RUT/nombre,
   no por este username interno) verificalo y dilo en el informe; NO toques la base de Geovictoria bajo ninguna
   circunstancia (es de otro sistema, fuera de nuestro alcance).
5. Test que reproduzca el escenario (2 personas, mismo cargo-no-operador vs operador, verificando que tras el fix
   cada una tiene un usuario unico dentro de su sucursal) y verificacion con los datos reales corregidos.

## PARTE B — Averias desactualizadas en Calama (URGENTE)
Montu, QA en vivo hoy 06-10 ~08:00: en Programacion y en Averias, sucursal Calama muestra "Carro de Corte" y
"EURA 16" DETENIDAS y "COIL 14" SEMIOPERATIVA, pero el estado real es: Carro de Corte OPERATIVA, COIL 14 OPERATIVA,
y EURA 16 recien quedo detenida hace ~15 min (en Cubigest la averia de EURA 16 quedo registrada a las 10:40 de HOY
— es decir, el SPP la mostraba detenida ANTES de que el hecho ocurriera realmente). El job de sync de averias
(`_job_sync_averias_cubigest`, cada 30 min, tabla `averias_cubigest`) deberia estar trayendo el estado real.
1. Hipotesis A (prioridad alta, investigar primero): las pruebas ejecutadas AYER durante el deploy de la Ola 1
   (`test_averias_cubigest`, `test_estado_maquinas`, o cualquier script de prueba) se corrieron en algun momento
   con working directory sobre el backend del checkout PRINCIPAL (`optifierro_v2.db` real, no una copia) —
   esto ya genero una corrupcion de indices SQLite que tuvimos que reparar anoche (ver `LOG_CAMBIOS_2026.md`,
   entrada "DEPLOY Ola 1"). Es MUY posible que esas mismas pruebas hayan escrito filas de FIXTURE (nombres de
   maquina de prueba, posiblemente coincidiendo justo con "Carro de Corte"/"EURA 16"/"COIL 14" si son los nombres
   que usan los tests) en `averias_cubigest` o en el estado efectivo que lee `estado_maquinas.py`, con timestamps
   que ahora se leen como si fueran reales. Revisa los tests mencionados: que nombres de maquina/estado usan como
   fixture, y si hay alguna fila en la BD de produccion cuyo `created_at`/`fecha_registro` sea de AYER (05-10) o
   de una corrida de test, para sucursal Calama, con esos 3 nombres de maquina exactos.
2. Hipotesis B: el job programado (`SYNC_HORARIO_ACTIVO=1`, cada 30 min) dejo de correr tras el/los reinicios de
   anoche (2 rebuilds del backend); revisa si el scheduler (APScheduler u otro) se reinicia correctamente al
   levantar el contenedor, y la hora del ULTIMO sync real registrado para `averias_cubigest` en Calama (deberia
   ser de hace minutos, no de ayer).
3. Hipotesis C: el join/fusion de averias (commit del 26-09, "averias de Cubigest join+fusion siempre") tiene un
   bug que no limpia una averia resuelta o no refresca el estado "semioperativa"/"detenida" al volver a operativa.
4. Diagnostica con evidencia cual(es) aplica(n) (puede ser mas de una). Corrige la causa raiz (no borres a mano las
   3 filas sin entender el origen: si es Hipotesis A, hazlo con una migracion explicita que documente que eran
   datos de prueba; si es B, corrige el scheduler; si es C, corrige la logica de fusion). Agrega un test de
   regresion para la causa que encuentres.
5. Verifica en vivo (lectura, vs `http://localhost:8001/api/averias?sucursal=10` o el endpoint que corresponda a
   Calama=10... CONFIRMA el id correcto de Calama antes: en este sistema Calama=1, Cerrillos=10, Coronel=14 segun
   uso previo de `sucursal` en la API, pero DOBLE-CHEQUEALO porque en `operadores_matriz` del CSV de ayer Calama
   aparecio como sucursal_id=1) que Carro de Corte y COIL 14 figuran OPERATIVAS y EURA 16 DETENIDA con timestamp de
   hoy cercano a las 10:40.

## Archivos permitidos
Parte A: el Excel/script de alta de `operadores_matriz` (o un endpoint de administracion si existe), SOLO la fila
afectada. Parte B: `estado_maquinas.py`, el job de sync de averias en `main.py`, `database_cubigest.py` si aplica,
tests nuevos. Nada de `motor_v2.py`, `cargos.py`, `GestorProgramacion.tsx` (otras tareas en curso podrian tocarlos).

## NO HAGAS
No toques Geovictoria. No borres filas de `averias_cubigest`/`estado efectivo` sin antes identificar su origen y
documentarlo en el informe. No ejecutes NADA de prueba contra la BD real del checkout principal. No hagas
`docker build`/`up` tu mismo: deja el worktree listo, verificado, con commits — el deploy lo hace Miaude tras revisar.
