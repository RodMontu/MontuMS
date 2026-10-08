p = "routers/operadores.py"
s = open(p, encoding="utf-8").read()
assert "_excluir_ayudantes_presentes" not in s

# imports + helper (despues del import de Counter)
a = "from collections import Counter\n"
assert s.count(a) == 1
s = s.replace(a, a + "import time\nimport logging\nimport httpx\nfrom cargos import es_ayudante\n\nlogger = logging.getLogger(__name__)\n")

helper = '''

# F4 (QA SPP 05-10, Montu): "Los que se detecten como operador [por el cargo de Geovictoria] deberan aparecer en la seccion
# Gestor de Operadores ... y en el Gestor de Maquinas > Maestros". Los ayudantes (cargo "Ayte del Operador"/"Ayudante de Operador")
# NO aparecen ahi. Este filtro usa a los presentes de hoy (unica fuente con cargo expuesta por la API de Geovictoria): un ayudante
# AUSENTE hoy no se puede identificar y sigue visible. Sin respuesta de Geovictoria: no se filtra (nunca oculta por error).
_GEOVICTORIA_URL = os.getenv("GEOVICTORIA_API_URL", "http://192.168.1.111:8002")
_CACHE_AYUDANTES: dict = {}
_CACHE_TTL_S = 60


def _norm_nombre(s: str) -> str:
    return " ".join(_sin_acento((s or "").strip()).lower().split())


def _nombres_ayudantes_presentes(sucursal_id: int) -> set:
    ahora = time.time()
    hit = _CACHE_AYUDANTES.get(sucursal_id)
    if hit and ahora - hit[0] < _CACHE_TTL_S:
        return hit[1]
    nombres: set = set()
    try:
        r = httpx.get(f"{_GEOVICTORIA_URL}/asistencia/operadores_presentes/{sucursal_id}", timeout=3.0)
        if r.status_code == 200:
            for p in r.json() or []:
                if es_ayudante(p.get("cargo")) and p.get("nombre"):
                    nombres.add(_norm_nombre(p["nombre"]))
        _CACHE_AYUDANTES[sucursal_id] = (ahora, nombres)
    except Exception as e:
        logger.warning(f"[F4] Gestor de Operadores: sin datos de cargo de Geovictoria (suc={sucursal_id}): {e}")
    return nombres


def _excluir_ayudantes_presentes(filas: list, sucursal_id: int) -> list:
    ayudantes = _nombres_ayudantes_presentes(sucursal_id)
    if not ayudantes:
        return filas
    return [f for f in filas if _norm_nombre(f.get("Nombre")) not in ayudantes]

'''
b = '@router.get("")\ndef obtener_operadores('
assert s.count(b) == 1
s = s.replace(b, helper.lstrip("\n") + "\n\n" + b)

c = "            return result\n    except Exception as e:\n        raise HTTPException(status_code=500, detail=str(e))\n"
i = s.index("def obtener_operadores(")
j = s.index(c, i)
s = s[:j] + "            if sucursal:\n                result = _excluir_ayudantes_presentes(result, int(sucursal))\n" + s[j:]
open(p, "w", encoding="utf-8").write(s)
print("OK operadores.py")
