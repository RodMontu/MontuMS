import sqlite3, os, time
DB = "/work/optifierro_v2.db"
con = sqlite3.connect(DB, timeout=60, isolation_level=None)
sql_idx = con.execute("select sql from sqlite_master where type='index' and name='idx_hist_fecha_suc'").fetchone()
print("DDL del indice danado:", sql_idx)
assert sql_idx and sql_idx[0], "no se encontro el DDL del indice"
con.execute("PRAGMA writable_schema=ON")
con.execute("DELETE FROM sqlite_master WHERE type='index' AND name='idx_hist_fecha_suc'")
con.execute("PRAGMA writable_schema=OFF")
con.close()

con = sqlite3.connect(DB, timeout=60, isolation_level=None)
print("reabre OK; filas historial (scan de tabla):", con.execute("select count(*) from historial_asignaciones not indexed").fetchone()[0])
t0 = time.time()
con.execute(sql_idx[0])
print(f"indice recreado desde los datos de la tabla ({time.time()-t0:.1f}s)")
res = [r[0] for r in con.execute("pragma integrity_check")]
print("integrity_check tras recrear indice:", res[:4])
con.close()
