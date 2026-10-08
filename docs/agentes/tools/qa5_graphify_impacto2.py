import json, collections
d = json.load(open("/Users/montu/graphify-workspace/optifierro/graphify-out/graph.json"))
nodes = {n["id"]: n for n in d["nodes"]}
print("built_at_commit:", d.get("built_at_commit"))

def file_of(nid):
    n = nodes.get(nid)
    return n.get("source_file") if n else None

objetivo = {
    "backend/routers/admin.py",
    "backend/routers/operadores.py",
    "backend/routers/programacion.py",
    "backend/estado_maquinas.py",
    "backend/motor_v2.py",
    "backend/cargos.py",
    "frontend/src/components/VersionWatcher.tsx",
}
externos = collections.defaultdict(set)
internos = 0
for l in d["links"]:
    fs, ft = file_of(l["source"]), file_of(l["target"])
    if fs in objetivo or ft in objetivo:
        if fs in objetivo and ft in objetivo:
            internos += 1
        elif fs in objetivo:
            externos[fs].add((ft, l["target"]))
        else:
            externos[ft].add((fs, l["source"]))

print(f"\nenlaces 100% internos a los archivos de hoy: {internos}")
for f in sorted(objetivo):
    ext = externos.get(f, set())
    otros_archivos = sorted({of for of, _ in ext if of and of not in objetivo})
    print(f"\n=== {f} === depende-de/es-dependido-por archivos FUERA del cambio de hoy: {otros_archivos}")
