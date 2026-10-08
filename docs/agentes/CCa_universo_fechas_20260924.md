# CCa — universo_fechas.py (fundacional) — 24-09-2026

## Ubicación
- `backend/universo_fechas.py` (mismo nivel que `motor_v2.py`, confirmado con
  `find . -iname 'motor_v2.py'` → `./backend/motor_v2.py`).
- Test: `backend/test_universo_fechas.py` (mismo directorio y patrón
  `test_*.py` que `test_b44b_capacidad_real.py`, `test_sync_unificado.py`, etc.
  Framework: `unittest`, comando `python -m unittest test_universo_fechas -v`).
- Worktree: `/c/Users/OptiFierro/Desktop/optifierro-universo-fechas` (TO),
  rama `universo-fechas`, base `master`=`f430b75`. Cambios SIN commitear
  (archivos nuevos, `git status --porcelain` → `?? backend/test_universo_fechas.py`,
  `?? backend/universo_fechas.py`).

## Firma exacta

```python
def clasificar_fecha(
    fecha_despacho: date,
    horizonte_reprog: int | None = None,
    hoy: date | None = None,
) -> str:
```

- `fecha_despacho: datetime.date` — fecha efectiva de despacho (FechaDespacho
  con fallback FechaEntrega, resuelto por el llamador; esta función es pura).
- `horizonte_reprog: int | None` — días entre fecha de despacho y fecha de
  última reprogramación. `None` si no se conoce (no reclasifica).
- `hoy: date | None` — fecha de referencia, default `date.today()`. Agregado
  respecto del spec (que no lo listaba) para que el test sea determinístico
  sin monkeypatchear `date.today`; el llamador en producción no necesita
  pasarlo.
- Retorno: `str`, una de `"atrasada_valida"`, `"atrasada_suciedad"`,
  `"proxima"`, `"lejana_normal"`, `"muy_futura"`.

Constantes expuestas: `UMBRAL_ATRASADA_SUCIEDAD_DIAS=30`,
`UMBRAL_PROXIMA_DIAS=21`, `UMBRAL_LEJANA_DIAS=60`,
`UMBRAL_HORIZONTE_SOSPECHOSO_DIAS=120`.

Puro: sin imports de BD, solo `datetime.date`. Límites verificados: dia 0 y
+21 → `proxima`; +30 atrasado → `atrasada_valida`; +60 → `lejana_normal`;
+61 → `muy_futura`. La regla de horizonte (`horizonte_reprog>120`) solo se
evalúa cuando `dias > 21` (nunca reclasifica `proxima`), tal como pide el
spec.

## Cómo verifiqué el test
`ssh TO "cd .../backend && python -m unittest test_universo_fechas -v"` →
**11/11 tests OK** (0.000s). Casos: un caso por categoría (incl. límites
exactos 30/21/60), el caso sintético de "muy futura por horizonte"
(+45d, horizonte_reprog=150 → `muy_futura`, en vez del mal ejemplo del spec
IT 1384 que ya es `muy_futura` por umbral simple sin necesitar la regla de
horizonte), y un caso explícito de no-reclasificación de `proxima` con
horizonte sospechoso (+10d, horizonte_reprog=500 → sigue `proxima`).

## Riesgos / notas
- No toqué `database_cubigest.py`, `materias_primas.py`, `programacion.py` ni
  ningún otro archivo — solo el módulo + test, según alcance.
- El parámetro `hoy` no estaba en la firma propuesta por el spec (sección 5
  solo menciona `fecha_despacho, horizonte_reprog`). Lo agregué como
  keyword-only-por-convención con default `None`→`date.today()` para que el
  módulo sea testeable sin mockear reloj. Si las ventanas hermanas prefieren
  la firma de 2 argumentos exacta, es trivial quitarlo (usarían
  `date.today()` implícito) — lo dejo a criterio de la Coordinadora.
- Riesgo abierto ya señalado en el spec (no atendido por mí, fuera de
  alcance): `TOP 2000` de `_obtener_pids_pendientes` y el job horario de
  CCa-17 deberán usar esta misma función una vez conectada.

## Qué necesito de la Coordinadora
- Confirmar si el parámetro `hoy` se mantiene en la firma pública que usarán
  `qa-a03-mp`, `proximas-semanas` y `vista-semanal-qa`, para que las 3
  ventanas hermanas importen exactamente la misma firma.
- Diff guardado en
  `/Users/montu/MontuMS/docs/agentes/diffs/universo_fechas_diff_20260924.patch`
  (generado con `diff -u /dev/null <archivo>` porque son archivos nuevos sin
  `git add`, respetando la restricción de no usar comandos git de escritura).
