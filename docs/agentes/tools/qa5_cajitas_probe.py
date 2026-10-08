import json, urllib.request, collections
HOY = "2026-10-05"
d = json.load(urllib.request.urlopen(f"http://localhost:8000/api/programacion?sucursal=14&turno=dia&fecha={HOY}", timeout=90))
ev = d.get("eventos", [])
print("n eventos:", len(ev), "| metadata keys:", sorted((d.get("metadata") or {}).keys())[:14])
print("keys del primer evento:", sorted(ev[0].keys()) if ev else None)
por_maq = collections.Counter(e.get("nombre_maquina") or e.get("recurso_id") for e in ev)
print("por maquina:", dict(por_maq))
print("--- ejemplos (maquina, codigo_viaje, tipo/es_grupo, n etiquetas, kg, inicio) ---")
for e in ev[:60]:
    ks = {k: e.get(k) for k in ("nombre_maquina", "codigo_viaje", "es_grupo", "tipo", "n_etiquetas", "etiquetas_count", "kilos", "fecha_inicio") if k in e}
    print(ks)
    if len([1 for _ in ev]) > 12 and ev.index(e) > 14: break
