import json, sqlite3, urllib.request, glob, os, datetime
HOY = "2026-10-05"
def get(sid):
    u = f"http://localhost:8000/api/programacion?sucursal={sid}&turno=dia&fecha={HOY}"
    return json.load(urllib.request.urlopen(u, timeout=60))
p = None
for c in ("/app/optifierro_v2.db", "/app/data/optifierro_v2.db"):
    if os.path.exists(c):
        p = c; break
if p is None:
    p = (glob.glob("/app/**/optifierro_v2.db", recursive=True) or [None])[0]
print("db:", p)
con = sqlite3.connect(f"file:{p}?mode=ro", uri=True)
print("cuadro cols:", [r[1] for r in con.execute("PRAGMA table_info(cuadro_programacion_optisteel)")])
d = get(14)
ev = d.get("eventos", [])
print("n eventos Coronel:", len(ev))
if ev:
    print("keys evento:", sorted(ev[0].keys()))
    print("ejemplo:", {k: ev[0][k] for k in list(ev[0].keys())[:25]})
