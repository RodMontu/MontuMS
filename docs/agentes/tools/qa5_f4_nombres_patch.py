p = "motor_v2.py"
s = open(p, encoding="utf-8").read()
def una(a, b):
    global s
    assert s.count(a) == 1, ("ancla no unica/ausente", a[:70], s.count(a))
    s = s.replace(a, b)

# 1) __init__: indice por (sucursal, username)
una("        self.nombre_por_username: dict[str, str] = {}\n",
    "        self.nombre_por_username: dict[str, str] = {}\n"
    "        # F4 (QA 05-10): el mismo username existe en mas de una planta (p. ej. 'curra' en Cerrillos y en Coronel, personas\n"
    "        # distintas). Resolver SIEMPRE con resolver_nombre_operador(sucursal, username); nombre_por_username queda como respaldo.\n"
    "        self.nombre_por_sucursal_username: dict[tuple, str] = {}\n")

# 2) carga de la matriz
una("            nuevos_nombres: dict = {}\n", "            nuevos_nombres: dict = {}\n            nuevos_nombres_suc: dict = {}\n")
una("                nuevos_nombres[operador] = row[\"Nombre\"] or operador\n",
    "                nuevos_nombres[operador] = row[\"Nombre\"] or operador\n"
    "                nuevos_nombres_suc[(suc, operador)] = row[\"Nombre\"] or operador\n")
una("            self.nombre_por_username.update(nuevos_nombres)\n",
    "            self.nombre_por_username.update(nuevos_nombres)\n"
    "            self.nombre_por_sucursal_username.update(nuevos_nombres_suc)\n")

# 3) metodo
una("    def cargar(self):\n        self._cargar_matriz_rutas()\n",
    "    def resolver_nombre_operador(self, sucursal: str, username: str) -> str:\n"
    "        \"\"\"username -> nombre completo DE ESA SUCURSAL (no mezcla personas homonimas de otras plantas).\"\"\"\n"
    "        if not username:\n            return username or ''\n"
    "        return (self.nombre_por_sucursal_username.get((sucursal, username))\n"
    "                or self.nombre_por_username.get(username, username))\n\n"
    "    def cargar(self):\n        self._cargar_matriz_rutas()\n")

# 4) asignacion normal
una("                        \"operador\":       conocimiento.nombre_por_username.get(\n"
    "                                              operador_asignado or '', operador_asignado or ''),\n",
    "                        \"operador\":       conocimiento.resolver_nombre_operador(\n"
    "                                              sucursal_nombre, operador_asignado or ''),\n")

# 5) adelanto: tambien nombre completo, no username crudo
una("                \"operador\":       operador_asignado,\n                \"estado\": (\n                    \"programado-semi-operativa\" if maquina_destino in maquinas_semi\n",
    "                \"operador\":       conocimiento.resolver_nombre_operador(sucursal_nombre, operador_asignado or ''),\n                \"estado\": (\n                    \"programado-semi-operativa\" if maquina_destino in maquinas_semi\n")
open(p, "w", encoding="utf-8").write(s)
print("OK motor_v2 parcheado")
