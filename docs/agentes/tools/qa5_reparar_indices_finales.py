import sqlite3, time
DB = "/work/optifierro_v2.db"
con = sqlite3.connect(DB, timeout=60, isolation_level=None)
res = [r[0] for r in con.execute("pragma integrity_check")]
print("integrity antes (n mensajes):", len(res))
malos = sorted({r.split(" from index ")[1] for r in res if " from index " in r})
otros = [r for r in res if " from index " not in r and r != "ok"]
print("indices con filas faltantes:", malos, "| otros mensajes:", otros[:3])
for nombre in malos:
    ddl = con.execute("select sql from sqlite_master where type='index' and name=?", (nombre,)).fetchone()[0]
    t0 = time.time()
    con.execute(f'DROP INDEX "{nombre}"')
    con.execute(ddl)
    print(f"  reconstruido {nombre} ({time.time()-t0:.1f}s)")
res2 = [r[0] for r in con.execute("pragma integrity_check")]
print("integrity_check FINAL:", res2[:3])
print("filas: historial_asignaciones =", con.execute("select count(*) from historial_asignaciones").fetchone()[0],
      "| operadores_matriz =", con.execute("select count(*) from operadores_matriz").fetchone()[0],
      "| trabajos_optisteel =", con.execute("select count(*) from trabajos_optisteel").fetchone()[0],
      "| programacion_guardada =", con.execute("select count(*) from programacion_guardada").fetchone()[0])
con.close()
