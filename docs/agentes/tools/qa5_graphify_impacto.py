import json
d = json.load(open("/Users/montu/graphify-workspace/optifierro/graphify-out/graph.json"))
nodes = {n["id"]: n for n in d["nodes"]}
links = d["links"]
print("built_at_commit:", d.get("built_at_commit"), "| nodes:", len(nodes), "| links:", len(links))

def vecinos(sub):
    ids = [i for i in nodes if sub in i]
    out = set()
    for l in links:
        if any(sub in str(l.get(k, "")) for k in ("source", "target")):
            out.add((l.get("source"), l.get("target"), l.get("type") or l.get("kind") or ""))
    return ids, out

for sub in ("routers/admin.py", "routers/operadores.py", "routers/programacion.py",
            "VersionWatcher", "estado_maquinas.py", "motor_v2.py"):
    ids, rel = vecinos(sub)
    print(f"\n=== {sub} === nodos que calzan: {ids[:3]}  | aristas tocando ese archivo: {len(rel)}")
    for s, t, k in list(rel)[:8]:
        print("   ", s, "->", t, f"[{k}]")
