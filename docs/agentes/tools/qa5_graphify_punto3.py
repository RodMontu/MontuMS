import json, collections
d = json.load(open("/Users/montu/graphify-workspace/optifierro/graphify-out/graph.json"))
nodes = {n["id"]: n for n in d["nodes"]}
def fo(i): return (nodes.get(i) or {}).get("source_file")

files = sorted({n.get("source_file") for n in d["nodes"] if n.get("source_file")})
print("Archivos del grafo que mencionan averia/etapa/historial:")
for f in files:
    if any(k in f.lower() for k in ("averia", "etapa", "historial", "estado_maq")):
        print("  ", f)

objetivo = {
    "backend/estado_maquinas.py",
    "backend/routers/programacion.py",
    "frontend/src/components/domain/GestorProgramacion.tsx",
}
# agregar cualquier archivo de averias (backend o frontend)
objetivo |= {f for f in files if "averia" in f.lower() and not f.endswith(("test.py",)) and "test_" not in f}
print("\nAnalizando impacto sobre:", sorted(objetivo))

ext = collections.defaultdict(set)
for l in d["links"]:
    fs, ft = fo(l["source"]), fo(l["target"])
    if fs in objetivo and ft not in objetivo and ft:
        ext[fs].add(ft)
    elif ft in objetivo and fs not in objetivo and fs:
        ext[ft].add(fs)
for f in sorted(objetivo):
    print(f"\n=== {f} ===  (depende de / es usado por, fuera del conjunto)")
    for x in sorted(ext.get(f, [])):
        print("   ", x)
