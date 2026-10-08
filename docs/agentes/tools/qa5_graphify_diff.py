import json, collections
base = "/Users/montu/graphify-workspace/optifierro/"
old = json.load(open(base + "graphify-out.bak_pre_cca41_20261008/graph.json"))
new = json.load(open(base + "graphify-out/graph.json"))
o = {n["id"]: n for n in old["nodes"]}
n = {x["id"]: x for x in new["nodes"]}
print("nodos viejo/nuevo:", len(o), len(n))
add = set(n) - set(o); rem = set(o) - set(n)
print("ids agregados:", len(add), "| ids removidos:", len(rem))

# duplicados "logicos": misma (source_file, label) con ids distintos
def clave(x): return (x.get("source_file"), x.get("label"), x.get("source_location"))
c_old = collections.Counter(clave(x) for x in old["nodes"])
c_new = collections.Counter(clave(x) for x in new["nodes"])
dup_old = sum(1 for k, v in c_old.items() if v > 1)
dup_new = sum(1 for k, v in c_new.items() if v > 1)
print("claves logicas duplicadas viejo/nuevo:", dup_old, dup_new)

# donde se concentran los agregados
por_archivo = collections.Counter(n[i].get("source_file") for i in add)
print("\nTop archivos con nodos agregados:")
for f, k in por_archivo.most_common(10): print("  ", k, f)
print("\nMuestra de ids agregados:")
for i in list(add)[:8]: print("  ", i, "|", n[i].get("label"), "|", n[i].get("source_file"), "|", n[i].get("file_type"))

# nodos por tipo de archivo
tipo = collections.Counter((x.get("source_file") or "").rsplit(".", 1)[-1] for x in new["nodes"])
print("\nNodos por extension (nuevo):", dict(tipo.most_common(8)))
# archivos distintos
print("archivos distintos viejo/nuevo:", len({x.get('source_file') for x in old['nodes']}), len({x.get('source_file') for x in new['nodes']}))
