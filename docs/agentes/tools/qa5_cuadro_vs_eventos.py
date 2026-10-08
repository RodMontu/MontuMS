import json, sqlite3, urllib.request, collections
HOY = "2026-10-05"
def get(sid):
    u = f"http://localhost:8000/api/programacion?sucursal={sid}&turno=dia&fecha={HOY}"
    return json.load(urllib.request.urlopen(u, timeout=90))
con = sqlite3.connect("file:/app/optifierro_v2.db?mode=ro", uri=True)
for sid in (1, 10, 14):
    d = get(sid)
    ev = d.get("eventos", [])
    cua = collections.defaultdict(set)
    for v, f in con.execute("SELECT viaje, fecha FROM cuadro_programacion_optisteel WHERE sucursal_id=?", (sid,)):
        cua[(v or "").strip()].add((f or "")[:10])
    fechas_ej = sorted({x for s in cua.values() for x in s})[:3]
    cls = collections.Counter(); sin_flag = []; con_flag = 0
    for e in ev:
        v = (e.get("codigo_viaje") or "").strip()
        fs = cua.get(v)
        if not fs:
            c = "no_en_cuadro"
        elif min(fs) > HOY:
            c = "cuadro_futuro"
        elif HOY in fs:
            c = "cuadro_hoy"
        else:
            c = "cuadro_pasado"
        cls[c] += 1
        if c == "cuadro_futuro":
            if e.get("viene_de_futuro"):
                con_flag += 1
            else:
                sin_flag.append((v, min(fs), e.get("recurso_id"), e.get("tipo"), round(e.get("kilos") or 0)))
    print(f"\n== sucursal {sid}: eventos={len(ev)} formato fecha cuadro ej={fechas_ej}")
    print("clasificacion (por IT en Cuadro):", dict(cls))
    print(f"cuadro_futuro con flag={con_flag} SIN flag={len(sin_flag)}")
    for r in sin_flag[:12]:
        print("   sin flag:", r)
    if sid == 14:
        ops = collections.Counter((e.get("recurso_id"), e.get("operador")) for e in ev)
        print("maquina/operador en eventos Coronel:", sorted(ops.items(), key=lambda x: str(x[0])))
