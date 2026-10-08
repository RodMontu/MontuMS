"""V5 / Miaude - arnes de reproduccion B42 v2 (SOLO LECTURA). Compara programar_turno de master (old) vs rama b42v2 (new)
con el MISMO universo real (Cubigest solo SELECT via _obtener_pids_pendientes) y MISMOS operadores. No escribe nada."""
import importlib.util, os, sys, time, collections, sqlite3, json
sys.path.insert(0, "/app")
os.chdir("/app")

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m

old = load("motor_old", "/tmp/mv/old/motor_v2.py")
new = load("motor_new", "/tmp/mv/new/motor_v2.py")

_CUB_MAQ_MAP = {
    (1, 101): 17, (1, 102): 16, (1, 104): 105, (1, 105): 101, (1, 106): 104, (1, 107): 107, (1, 108): 102, (1, 111): 106,
    (4, 10): 13, (4, 11): 16, (4, 13): 14, (4, 16): 18, (4, 17): 23, (4, 18): 17, (4, 21): 7, (4, 22): 21, (4, 23): 22, (4, 25): 10, (4, 26): 11,
    (14, 405): 404, (14, 406): 401, (14, 407): 402, (14, 411): 405, (14, 412): 407, (14, 413): 406, (14, 414): 411, (14, 416): 412, (14, 417): 16,
}
_CUB_TO_SQL_SUC = {1: 1, 4: 10, 14: 14}

def cargar(mod):
    c = mod.ConocimientoMotor("/app"); c.cargar()
    with sqlite3.connect("/app/optifierro_v2.db") as conn:
        conn.row_factory = sqlite3.Row
        nombre = {(r["sucursal_id"], r["maquina_id"]): r["maquina"] for r in conn.execute("SELECT sucursal_id, maquina_id, maquina FROM maquinas_info")}
    mapa = {}
    for (cs, mn), sm in _CUB_MAQ_MAP.items():
        n = nombre.get((_CUB_TO_SQL_SUC[cs], sm))
        if n: mapa[(_CUB_TO_SQL_SUC[cs], mn)] = n
    c.cargar_mapa_maquinas(mapa)
    return c

from routers.programacion import _obtener_pids_pendientes, _obtener_operadores_disponibles

import datetime
def _dt(x):
    try: return datetime.datetime.fromisoformat(str(x).replace("Z",""))
    except Exception: return None

def extra(res, et):
    key = {e["etiqueta_id"]: (e.get("codigo_viaje"), e.get("diametro"), e.get("id_forma"), round((e.get("largo_a") or 0)*1000), e.get("calidad_acero_real", e.get("calidad_acero"))) for e in et}
    t = res.get("tareas", []); b = res.get("bolsa_sin_asignar", [])
    asig = set()
    for x in t:
        for eid in (x.get("lista_etiqueta_ids") or [x.get("etiqueta_id")]): asig.add(key.get(eid))
    parcial = [x for x in b if x.get("motivo_key") == "turno_lleno" and key.get(x.get("etiqueta_id")) in asig]
    # cambios de diametro y huecos por maquina
    cambios = 0; hueco = 0.0; lastfin = {}
    por_maq = collections.defaultdict(list)
    for x in t:
        a, f = _dt(x.get("fecha_inicio")), _dt(x.get("fecha_fin"))
        if a and f: por_maq[x.get("nombre_maquina")].append((a, f, x.get("diametro")))
    for m, L in por_maq.items():
        L.sort()
        lastfin[m] = max(f for _, f, _ in L).strftime("%H:%M")
        for i in range(1, len(L)):
            if L[i][2] != L[i-1][2]: cambios += 1
            hueco += max(0.0, (L[i][0] - L[i-1][1]).total_seconds()/60)
    return {"bolsa_turno_lleno_de_series_parciales": {"n": len(parcial), "kg": round(sum((x.get("kgs") or 0) for x in parcial))},
            "cambios_diametro": cambios, "huecos_min": round(hueco), "ultimo_fin_por_maquina": lastfin}

def resumen(res):
    t = res.get("tareas", []); b = res.get("bolsa_sin_asignar", [])
    kg = sum((x.get("kilos") or 0) for x in t)
    kgb = sum((x.get("kgs") or 0) for x in b)
    eti_t = sum(len(x.get("lista_etiqueta_ids") or [x.get("etiqueta_id")]) for x in t)
    rep = [x for x in t if x.get("reparto")]
    niv = collections.Counter(((x.get("alerta_reparto") or {}).get("nivel") or "sin") for x in t)
    mot = collections.Counter(x.get("motivo_key") for x in b)
    motkg = collections.defaultdict(float)
    for x in b: motkg[x.get("motivo_key")] += (x.get("kgs") or 0)
    maqs = collections.Counter(x.get("nombre_maquina") for x in t)
    return {
        "cajitas": len(t), "kg_tareas": round(kg), "etiquetas_en_tareas": eti_t,
        "bolsa_n": len(b), "kg_bolsa": round(kgb),
        "tareas_con_reparto_efectivo": len(rep), "kg_en_tareas_con_reparto": round(sum((x.get("kilos") or 0) for x in rep)),
        "alerta_niveles": dict(niv),
        "bolsa_por_motivo": {str(k): {"n": mot[k], "kg": round(motkg[k])} for k in mot},
        "maquinas_usadas": len(maqs),
        "min_totales_tareas": round(sum((x.get("duracion_min") or 0) for x in t)),
        "kg_por_min": round(kg / max(sum((x.get("duracion_min") or 0) for x in t), 1), 1),
        "tareas_dur_ge_479": sum(1 for x in t if (x.get("duracion_min") or 0) >= 479),
        "kg_en_tareas_dur_ge_479": round(sum((x.get("kilos") or 0) for x in t if (x.get("duracion_min") or 0) >= 479)),
        "min_por_maquina": {k: round(v) for k, v in sorted(collections.Counter({m: 0 for m in maqs}).items())} and {m: round(sum((x.get("duracion_min") or 0) for x in t if x.get("nombre_maquina") == m)) for m in maqs},
    }

fecha = "2026-09-24"
for sql_id, etiqueta in ((10, "Cerrillos"), (1, "Calama"), (14, "Coronel")):
    et = _obtener_pids_pendientes(sql_id, fecha)
    kg_univ = round(sum((e.get("kgs") or 0) for e in et))
    print(f"### {etiqueta} (sql {sql_id}): universo {len(et)} etiquetas, {kg_univ} kg", flush=True)
    for nombre, mod in (("VIEJO(master)", old), ("NUEVO(b42v2)", new)):
        c = cargar(mod)
        ops = _obtener_operadores_disponibles(sql_id, c, "dia")
        sid = sql_id if sql_id in mod.SUCURSALES else {1: 1, 10: 4, 14: 14}[sql_id]
        t0 = time.time()
        res = mod.programar_turno(etiquetas=[dict(e) for e in et], sucursal_id=sid, fecha=fecha, turno="dia",
                                  operadores_disponibles=ops, conocimiento=c)
        dt = time.time() - t0
        r = resumen(res); r.update(extra(res, et)); r["segundos"] = round(dt, 2); r["operadores"] = len(ops)
        print(f"{nombre}: " + json.dumps(r, ensure_ascii=False), flush=True)
print("FIN")
