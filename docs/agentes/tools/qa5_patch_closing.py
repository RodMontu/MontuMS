import re, sys
p = "routers/programacion.py"
s = open(p, encoding="utf-8").read()
changes = 0
# 1) import closing (una sola vez)
if "from contextlib import closing" not in s:
    s = s.replace("import sqlite3\n", "import sqlite3\nfrom contextlib import closing\n", 1)
    changes += 1
# 2) funciones nuevas de esta ola: cerrar la conexion de verdad (el 'with' de sqlite3 solo hace commit)
for fn in ("_marcar_adelanto_desde_cuadro", "_obtener_resumen_cuadro_por_fecha"):
    i = s.index("def " + fn)
    j = s.find("\ndef ", i + 10)
    bloque = s[i:j if j != -1 else len(s)]
    nuevo = re.sub(r"with sqlite3\.connect\(([^)]*(?:\([^)]*\))?[^)]*)\) as conn:", r"with closing(sqlite3.connect(\1)) as conn:", bloque)
    if nuevo != bloque:
        s = s[:i] + nuevo + s[(j if j != -1 else len(s)):]
        changes += 1
    print(fn, "parcheada" if nuevo != bloque else "SIN CAMBIO (revisar a mano)")
open(p, "w", encoding="utf-8").write(s)
print("cambios:", changes)
