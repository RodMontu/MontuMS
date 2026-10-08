# CCa-10 — Fix `decodificar_material` (largo decimal mal leido)

Fecha: 2026-09-24
Rama: `fix-decodificar` (worktree TO: `/c/Users/OptiFierro/Desktop/optifierro_dm`)
Commit: `64b7de7`
Base: `4325640`

## Problema
`backend/utils.py::decodificar_material` leia el largo con `int(codigo[8:10])`,
asumiendo siempre 2 digitos enteros tras la `X`. Codigos con largo decimal
de 1 digito (`1B63T32X6.9`, `1B63T25X9,9`) fallaban con `ValueError` y
quedaban silenciosamente en `largo=0` → descripcion "32mm x 0m" (visible en
balance de MP Cerrillos, 916 kg / 2 materiales).

## Fix
- Se lee `codigo[8:]` (resto del string tras la `X`) en vez de un slice fijo
  de 2 caracteres.
- Se normaliza `,` → `.` y se parsea: si hay separador decimal, `float`
  redondeado a 2 decimales; si no, `int` (mismo comportamiento que hoy para
  `X12`, `X06`, etc. — mismo tipo, mismo valor).
- Si el parseo falla, ya no se devuelve `0` silencioso: `largo_m = None` y
  la descripcion queda explicita ("... x largo invalido") en vez de "x 0m".
- Firma y claves del diccionario de salida sin cambios.

## Consumidores revisados
- Unico consumidor en el repo: `backend/routers/materias_primas.py:134`
  (`info_mat = decodificar_material(full_cod)`). Solo usa
  `info_mat["descripcion"]` e `info_mat["tipo_acero"]` — no toca
  `largo_m` ni `diametro_mm` en ningun calculo/agrupacion/filtro.
  Cambiar `largo_m` de `int` a `float`/`None` en casos decimales/invalidos
  es seguro, no rompe nada downstream.
- Grep confirmado (`grep -rn "decodificar_material"`) y verificado tambien
  contra el mirror de solo lectura Graphify — mismo resultado, un unico
  llamador.

## Pruebas
`backend/test_decodificar_material.py` (nuevo, estilo `unittest` como
`test_b16_capacidad.py`), 7 casos, todos OK:
- `1B63T32X6.9` → 6.9
- `1B63T25X9,9` → 9.9
- `1B63N36X6,5` → 6.5
- `1B63N32X12` → 12 (int, igual que antes)
- `1B63N32X10,8` → 10.8
- `1B63N32X11,9` → 11.9
- codigo invalido → `largo_m=None`, descripcion "largo invalido"

`py_compile` OK sobre `utils.py` y el test.

### Verificacion con datos reales (solo lectura)
`GET http://localhost:8001/api/materias_primas?sucursal=10` desde TO → 91
codigos unicos. Se copio `utils.py` corregido y la respuesta JSON a
`/tmp` del contenedor `optifierro-backend` (via `docker cp`,
`MSYS_NO_PATHCONV=1`, sin tocar `/app`) y se corrio un script comparando
`decodificar_material` viejo vs nuevo sobre los 91 codigos:
- 2 descripciones cambiaron: `1B63T25X9,9` y `1B63T32X6.9` (los mismos 2
  materiales del reporte de Carlitos 3.8) → ahora muestran el largo
  correcto en vez de "x 0m".
- 0 codigos quedan con "x 0m" tras el fix.
- 0 regresiones (ningun codigo que hoy decodifica bien cambio de valor).
- Archivos temporales del contenedor eliminados al terminar.

## Riesgo
Bajo. Cambio acotado a una funcion pura sin efectos secundarios, un solo
consumidor verificado, sin cambio de firma ni de claves del dict. No se
toco Docker, `master`, ni el checkout principal/espejo Mac. No hubo push.

## Entrega
- Patch: `docs/agentes/diffs/fix_decodificar/0001-fix-decodificar-material-largo-decimal.patch`
- Commit solo en rama `fix-decodificar` del worktree `optifierro_dm` en TO
  (no mergeado, no pusheado).
