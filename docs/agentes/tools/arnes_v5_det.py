"""V5 / Miaude - prueba de determinismo (SOLO LECTURA). modo dump: congela universo+operadores de Cerrillos; modo run: corre viejo/nuevo sobre lo congelado."""
import importlib.util, os, sys, json, sqlite3, hashlib, datetime
sys.path.insert(0, "/app"); os.chdir("/app")
MODE = sys.argv[1]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m

old = load("motor_old", "/tmp/mv/old/motor_v2.py"); new = load("motor_new", "/tmp/mv/new/motor_v2.py")
_CUB_MAQ_MAP = {(1, 101): 17, (1, 102): 16, (1, 104): 105, (1, 105): 101, (1, 106): 104, (1, 107): 107, (1, 108): 102, (1, 111): 106,
    (4, 10): 13, (4, 11): 16, (4, 13): 14, (4, 16): 18, (4, 17): 23, (4, 18): 17, (4, 21): 7, (4, 22): 21, (4, 23): 22, (4, 25): 10, (4, 26): 11,
    (14, 405): 404, (14, 406): 401, (14, 407): 402, (14, 411): 405, (14, 412): 407, (14, 413): 406, (14, 414): 411, (14, 416): 412, (14, 417): 16}
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
    c.cargar_mapa_maquinas(mapa); return c

if MODE == "dump":
    from routers.programacion import _obtener_pids_pendientes, _obtener_operadores_disponibles
    et = _obtener_pids_pendientes(10, "2026-09-24")
    ops = _obtener_operadores_disponibles(10, cargar(old), "dia")
    json.dump({"et": et, "ops": ops}, open("/tmp/mv/u.json", "w"), default=str)
    print("dump ok", len(et), ops)
else:
    u = json.load(open("/tmp/mv/u.json")); et, ops = u["et"], u["ops"]
    out = []
    for nombre, mod in (("VIEJO", old), ("NUEVO", new)):
        c = cargar(mod)
        sid = 10 if 10 in mod.SUCURSALES else 4
        res = mod.programar_turno(etiquetas=[dict(e) for e in et], sucursal_id=sid, fecha="2026-09-24", turno="dia", operadores_disponibles=list(ops), conocimiento=c)
        t = res["tareas"]
        sig = hashlib.sha1(json.dumps(sorted([(x.get("id_tarea"), x.get("nombre_maquina"), str(x.get("fecha_inicio"))) for x in t])).encode()).hexdigest()[:10]
        out.append(f"{nombre}: cajitas={len(t)} kg={round(sum((x.get('kilos') or 0) for x in t))} bolsa={len(res.get('bolsa_sin_asignar', []))} sig={sig}")
    print(f"seed={os.environ.get('PYTHONHASHSEED')} | " + " | ".join(out))
