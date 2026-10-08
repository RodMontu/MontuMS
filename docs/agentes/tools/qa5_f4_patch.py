import re, io
# ---------- 1) backend/cargos.py ----------
cargos = '''"""
F4 (QA SPP 05-10-2026, decision de Montu): operador vs ayudante se determina SOLO por el
cargo que entrega Geovictoria.
  - Operador: el cargo contiene "operador" (Operador Senior, Operador Junior, Operador Junior
    Practica, "Operador" a secas) y NO es "Ayte del Operador" / "Ayudante de Operador".
  - Ayudante: el cargo contiene "ayte" o "ayudante" -> NO es operador y no recibe maquinas.
  - Cualquier otro cargo (Mecanico, Supervisor, ...) no es operador (lista blanca).
La matriz de competencias (operadores_matriz) NO manda sobre el cargo.
"""
import logging
import unicodedata

logger = logging.getLogger(__name__)


def _sin_acento(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _cargo_usable(cargo) -> bool:
    """Valores defensivos: vacio o con ':' (p. ej. '0:00:00') no son un cargo real."""
    return bool(cargo) and ":" not in str(cargo)


def es_ayudante(cargo) -> bool:
    if not _cargo_usable(cargo):
        return False
    c = _sin_acento(str(cargo)).lower()
    return "ayte" in c or "ayudante" in c


def es_operador(cargo) -> bool:
    if not _cargo_usable(cargo):
        return False
    c = _sin_acento(str(cargo)).lower()
    return "operador" in c and "ayte" not in c and "ayudante" not in c


def filtrar_presentes_por_cargo(presentes: list, etiqueta: str = "") -> list:
    """
    Deja solo a los presentes (lista de dicts de Geovictoria con clave 'cargo') que son operadores.
    Salvaguarda: si NINGUN presente trae un cargo utilizable (scraper sin ese dato), no filtra
    (comportamiento anterior) y lo deja en el log: es mejor eso que dejar la planta sin operadores.
    """
    if not presentes:
        return presentes
    if not any(_cargo_usable(p.get("cargo")) for p in presentes):
        logger.warning(f"[F4] {etiqueta}: ningun presente trae cargo utilizable; no se filtra por cargo")
        return presentes
    operadores = [p for p in presentes if es_operador(p.get("cargo"))]
    excluidos = [f"{p.get('nombre')} ({p.get('cargo')})" for p in presentes if not es_operador(p.get("cargo"))]
    logger.warning(f"[F4] {etiqueta}: {len(operadores)}/{len(presentes)} presentes son operadores por cargo; excluidos: {excluidos}")
    return operadores
'''
open("cargos.py", "w", encoding="utf-8").write(cargos)

# ---------- 2) jornada.py delega en cargos ----------
j = open("routers/jornada.py", encoding="utf-8").read()
i = j.index("def _es_ayudante(cargo: str) -> bool:")
k = j.index("def _init_jornada_table")
j = j[:i] + "from cargos import es_ayudante as _es_ayudante, es_operador as _es_operador  # F4: fuente unica del criterio por cargo\n\n\n" + j[k:]
open("routers/jornada.py", "w", encoding="utf-8").write(j)

# ---------- 3) programacion.py ----------
p = open("routers/programacion.py", encoding="utf-8").read()
def una_vez(s, a, b):
    assert s.count(a) == 1, ("ancla no unica/ausente", a[:60], s.count(a))
    return s.replace(a, b)

p = una_vez(p, "from contextlib import closing\n", "from contextlib import closing\nfrom cargos import filtrar_presentes_por_cargo\n")

# 3a) _obtener_operadores_disponibles
p = una_vez(p,
"        # PASO 2: Construir username desde nombre completo de Geovictoria\n",
"        # F4 (QA 05-10): el endpoint de Geovictoria devuelve TODOS los presentes con su cargo (Mecanico, Ayte del\n"
"        # Operador, ...). Solo los cargos de operador pueden recibir maquinas; la matriz no manda sobre el cargo.\n"
"        presentes = filtrar_presentes_por_cargo(presentes, f\"suc{sucursal_id} turno={turno}\")\n"
"        if not presentes:\n"
"            return []\n\n"
"        # PASO 2: Construir username desde nombre completo de Geovictoria\n")

# 3b) _obtener_presencia_capacidad (capacidad B16)
p = una_vez(p,
"        presentes = [p for p in presentes if p.get(\"turno_inferido\") in (turno_norm, None, \"\")]\n\n        import unicodedata\n",
"        # F4: la capacidad cuenta solo operadores por cargo (el endpoint devuelve todos los presentes).\n"
"        presentes = filtrar_presentes_por_cargo(presentes, f\"capacidad suc{sucursal_id}\")\n"
"        presentes = [p for p in presentes if p.get(\"turno_inferido\") in (turno_norm, None, \"\")]\n\n        import unicodedata\n")
p = p.replace("(mismo endpoint que\n        # _obtener_operadores_disponibles; ya filtrado por cargo Operador — R3).",
              "(mismo endpoint que\n        # _obtener_operadores_disponibles; devuelve todos los presentes: se filtra por cargo abajo — F4).")

# 3c) helper + llamada: maquina detenida no puede tener operador
helper = '''
def _quitar_operador_de_maquinas_detenidas(recursos: list, sucursal_id: int) -> list:
    """
    F4 (QA 05-10, Montu): "si una maquina esta detenida, entonces no puede tener operador asignado".
    `recursos` sale de la tabla estatica maquinas_info (habitual), que no se entera de las averias;
    el estado efectivo (manual + Cubigest) vive en estado_maquinas. Nunca lanza.
    """
    try:
        from estado_maquinas import (
            obtener_estado_efectivo_maquinas, normalizar_nombre_maquina, AVERIA_CUBIGEST_CADUCIDAD_DIAS,
        )
        estados = obtener_estado_efectivo_maquinas(sucursal_id, db_path=DB_PATH)
        detenidas = {n for n, info in estados.items() if info.get("estado_motor") == "detenida"}
        if not detenidas:
            return recursos
        salida = []
        for r in recursos:
            if normalizar_nombre_maquina(r.get("nombre")) in detenidas:
                r = dict(r)
                r["operador"] = "Sin Operador Asignado"
                r["operador_noche"] = "Sin Operador Asignado"
            salida.append(r)
        return salida
    except Exception as e:
        logger.warning(f"[F4] no se pudo ajustar operador de maquinas detenidas (suc={sucursal_id}): {e}")
        return recursos

'''
p = una_vez(p, "\ndef _marcar_adelanto_desde_cuadro(", helper + "\ndef _marcar_adelanto_desde_cuadro(")
p = una_vez(p,
"            recursos = recursos_resueltos\n        except Exception:\n            pass\n\n    # 2. Eventos (Programación actual en memoria)",
"            recursos = recursos_resueltos\n        except Exception:\n            pass\n\n    # F4: maquina detenida no puede mostrar operador\n    recursos = _quitar_operador_de_maquinas_detenidas(recursos, sucursal)\n\n    # 2. Eventos (Programación actual en memoria)")
open("routers/programacion.py", "w", encoding="utf-8").write(p)
print("OK parches aplicados")
