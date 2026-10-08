# ENTORNO Y MODO DE TRABAJO (leer primero)
Eres Miaude/Mi TI en una ventana secundaria de ejecucion (SPP, repo tecnico "OptiFierro-V2", Torres Ocaranza).
Sesion NO INTERACTIVA (claude -p en background): nadie contesta preguntas. No pidas permiso ni confirmaciones:
decide con la evidencia y registra la decision en el informe. Nombre de usuario: "SPP"/"el Planificador".

Corres en el Mac Studio. Codigo real en TO (Windows) por SSH: alias `ssh TO` ya funciona (VPN activa).
TU WORKTREE: `/c/Users/OptiFierro/Desktop/optifierro-qa-a03-mp` (rama `qa-a03-mp`), creado hoy desde `master`
en `f430b75`. PRIMER PASO: `ssh TO "cd /c/Users/OptiFierro/Desktop/optifierro-qa-a03-mp && git log --oneline -1"` (debe mostrar f430b75).

NO subagentes ni tareas en segundo plano. NO git commit/add/stash/checkout/reset/rebase/push. Edita SOLO
dentro de tu worktree, deja SIN commitear. Al terminar: `ssh TO 'git -C /c/Users/OptiFierro/Desktop/optifierro-qa-a03-mp diff HEAD' > /Users/montu/MontuMS/docs/agentes/diffs/qa_a03_mp_diff_20260924.patch`

Prohibido en produccion: docker build/up/restart, escrituras en SQLite/Cubigest. Cubigest/SQLite: SOLO SELECT
acotado. Evidencia con archivo:linea o salida real; lo no verificado: "NO VERIFICADO". Espanol, tuteo.

Lee (ya en este Mac via NFS): `/Users/montu/MontuMS/docs/agentes/UNIVERSO_FECHAS_spec.md` (spec V6 — tu tarea
es QA-A-03, seccion 4 "Materia Prima").

## TU TAREA: corregir QA-A-03 (Materia Prima sobreestima demanda)
Archivos: `materias_primas.py` (linea ~239) y posiblemente `database_cubigest.py` funcion
`obtener_comprometido_por_codigo` (linea ~341-375) SI el filtro de avance corresponde ahi — confirma con
`grep -n` antes de asumir cual de los dos edita.

DEPENDENCIA CRUZADA (importante): tu codigo depende de `universo_fechas.py`, que otra ventana hermana esta
creando en paralelo AHORA MISMO — no existe todavia en tu worktree. Trata la firma
`clasificar_fecha(fecha_despacho, horizonte_reprog=None) -> str` (retorna "atrasada_valida"/"atrasada_suciedad"/
"proxima"/"lejana_normal"/"muy_futura", regla completa en seccion 3 del spec) como un CONTRATO ya acordado:
escribe el `import` como si el modulo ya existiera en el mismo nivel que `motor_v2.py`. Si al verificar no
puedes ejecutar el codigo end-to-end porque falta el modulo, documentalo como "NO VERIFICADO end-to-end
(depende de universo_fechas.py de otra ventana)" — no es un bloqueo para ti, sigue escribiendo el codigo.

Logica: demanda de materia prima = suma de kg de ITs con avance<100 clasificadas como atrasada_valida +
proxima + lejana_normal (excluye atrasada_suciedad y muy_futura). Las "muy_futura" van en linea aparte "sin
fecha confirmada" (no suman a la necesidad de compra), con la leyenda: "No considera ITs con fecha de
despacho mayor a 60 dias (N ITs / X.XXX kg fuera; ver aparte)".

Verificacion SIN el modulo: aunque no puedas correr `clasificar_fecha` importado, SI puedes replicar la
regla en SQL/Python suelto contra Cubigest (SELECT acotado, solo lectura) para confirmar que tu filtro
produce numeros cercanos a los del spec (Cerrillos: 939k actual -> ~673k esperado tras filtro, -39%;
Coronel: 115k -> ~34k, ~3.4x). Documenta el numero real que obtuviste.

Territorio: NO toques `programacion.py`, `motor_v2.py`, `GestorProgramacion.tsx`, `compromisos_semanales.py`,
`VistaSemanal.tsx`, `calendario_futuro.py`, `CalendarioFuturo.tsx` — son de otras ventanas hermanas.

## Protocolo de reporte (obligatorio al terminar)
1. Guarda el diff (comando arriba).
2. Informe en `/Users/montu/MontuMS/docs/agentes/CCa_qa_a03_mp_20260924.md`: archivo:linea editado, logica
   aplicada, numero real verificado por SELECT vs esperado del spec, riesgos, que necesitas de la Coordinadora
   (especialmente: confirmar el path/import real de universo_fechas.py cuando exista).
3. Salida final por stdout: SOLO un RESUMEN de maximo 15 lineas.
