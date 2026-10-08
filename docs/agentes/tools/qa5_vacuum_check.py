import sqlite3, time
DB = "/work/optifierro_v2.db"
con = sqlite3.connect(DB, timeout=60, isolation_level=None)
t0 = time.time()
con.execute("VACUUM")
print(f"VACUUM OK ({time.time()-t0:.1f}s)")
print("integrity_check:", [r[0] for r in con.execute("pragma integrity_check")][:4])
print("journal_mode:", con.execute("pragma journal_mode").fetchone()[0])
print("sucursales registradas:", con.execute("select * from sucursales").fetchall() if con.execute("select count(*) from sqlite_master where name='sucursales'").fetchone()[0] else "sin tabla sucursales")
print("--- residuo sucursal_id=4 (SOLO lectura, no se borra) ---")
for (t,) in con.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'").fetchall():
    cols = [r[1] for r in con.execute(f'pragma table_info("{t}")')]
    if "sucursal_id" in cols:
        n = con.execute(f'select count(*) from "{t}" where sucursal_id=4').fetchone()[0]
        if n:
            print(f"  {t}: {n} filas; ejemplo:", repr(con.execute(f'select * from "{t}" where sucursal_id=4 limit 1').fetchall())[:260])
for r in con.execute("select count(*), min(fecha), max(fecha) from programacion_guardada where sucursal_id=4"): print("  programacion_guardada suc4 (n, min, max):", r) if "fecha" in [c[1] for c in con.execute("pragma table_info(programacion_guardada)")] else None
con.close()
