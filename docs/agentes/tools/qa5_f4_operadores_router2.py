p = "routers/operadores.py"
s = open(p, encoding="utf-8").read()
def una(a, b):
    global s
    assert s.count(a) == 1, ("ancla no unica/ausente", a[:70], s.count(a))
    s = s.replace(a, b)

# 1) el cache guarda (ayudantes, operadores) presentes
una("from cargos import es_ayudante\n", "from cargos import es_ayudante, es_operador\n")
una("def _nombres_ayudantes_presentes(sucursal_id: int) -> set:\n"
    "    ahora = time.time()\n"
    "    hit = _CACHE_AYUDANTES.get(sucursal_id)\n"
    "    if hit and ahora - hit[0] < _CACHE_TTL_S:\n"
    "        return hit[1]\n"
    "    nombres: set = set()\n",
    "def _nombres_presentes_por_cargo(sucursal_id: int) -> tuple:\n"
    "    \"\"\"(ayudantes, operadores) presentes hoy, por nombre normalizado, segun el cargo de Geovictoria.\"\"\"\n"
    "    ahora = time.time()\n"
    "    hit = _CACHE_AYUDANTES.get(sucursal_id)\n"
    "    if hit and ahora - hit[0] < _CACHE_TTL_S:\n"
    "        return hit[1]\n"
    "    nombres: set = set()\n"
    "    operadores: set = set()\n")
una("                if es_ayudante(p.get(\"cargo\")) and p.get(\"nombre\"):\n                    nombres.add(_norm_nombre(p[\"nombre\"]))\n        _CACHE_AYUDANTES[sucursal_id] = (ahora, nombres)\n",
    "                if es_ayudante(p.get(\"cargo\")) and p.get(\"nombre\"):\n                    nombres.add(_norm_nombre(p[\"nombre\"]))\n"
    "                elif es_operador(p.get(\"cargo\")) and p.get(\"nombre\"):\n                    operadores.add(_norm_nombre(p[\"nombre\"]))\n"
    "        _CACHE_AYUDANTES[sucursal_id] = (ahora, (nombres, operadores))\n")
una("    return nombres\n\n\ndef _excluir_ayudantes_presentes(filas: list, sucursal_id: int) -> list:\n    ayudantes = _nombres_ayudantes_presentes(sucursal_id)\n",
    "    return nombres, operadores\n\n\ndef _nombres_ayudantes_presentes(sucursal_id: int) -> set:\n    return _nombres_presentes_por_cargo(sucursal_id)[0]\n\n\n"
    "def _excluir_ayudantes_presentes(filas: list, sucursal_id: int) -> list:\n    ayudantes = _nombres_ayudantes_presentes(sucursal_id)\n")
# la rama de error devolvia 'nombres' (set): ahora debe devolver la tupla
una("        logger.warning(f\"[F4] Gestor de Operadores: sin datos de cargo de Geovictoria (suc={sucursal_id}): {e}\")\n    return nombres, operadores\n",
    "        logger.warning(f\"[F4] Gestor de Operadores: sin datos de cargo de Geovictoria (suc={sucursal_id}): {e}\")\n    return nombres, operadores\n")

# 2) incluir operadores presentes por cargo aunque aun no tengan maquinas autorizadas (para poder asignarselas)
una("                if selected_machine_cols:\n                    machine_filter = \" OR \".join(f'\"{c}\" > 0' for c in selected_machine_cols)\n                    where_sql = f'WHERE sucursal_id = ? AND ({machine_filter})'\n                else:\n                    where_sql = 'WHERE sucursal_id = ?'\n",
    "                # F4: antes se omitian los operadores sin maquinas autorizadas; un operador presente por cargo (p. ej. un Operador\n"
    "                # Senior nuevo) debe aparecer para poder asignarle sus maquinas. El filtro se aplica abajo, en Python.\n"
    "                where_sql = 'WHERE sucursal_id = ?'\n")
una("            if sucursal:\n                result = _excluir_ayudantes_presentes(result, int(sucursal))\n",
    "            if sucursal:\n"
    "                _op_presentes = _nombres_presentes_por_cargo(int(sucursal))[1]\n"
    "                result = [\n"
    "                    r for r in result\n"
    "                    if (not selected_machine_cols) or any((r.get(c) or 0) > 0 for c in selected_machine_cols)\n"
    "                    or _norm_nombre(r.get(\"Nombre\")) in _op_presentes\n"
    "                ]\n"
    "                result = _excluir_ayudantes_presentes(result, int(sucursal))\n")
open(p, "w", encoding="utf-8").write(s)
print("OK operadores.py (2)")
