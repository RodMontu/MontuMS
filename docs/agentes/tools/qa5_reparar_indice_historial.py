import sqlite3, time
DB = "/app/optifierro_v2.db"
con = sqlite3.connect(DB, timeout=60)
con.execute("PRAGMA busy_timeout=60000")
print("journal_mode:", con.execute("pragma journal_mode").fetchone()[0])

# 1) reconstruir el indice danado (los datos de la tabla estan intactos: scan completo OK)
t0 = time.time()
con.execute("REINDEX idx_hist_fecha_suc")
con.commit()
print(f"REINDEX idx_hist_fecha_suc OK ({time.time()-t0:.1f}s)")

# 2) donde hay residuos de las pruebas (sucursal_id=4 no existe en produccion: plantas 1, 10 y 14)
tablas = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
for t in tablas:
    cols = [r[1] for r in con.execute(f'pragma table_info("{t}")')]
    if "sucursal_id" in cols:
        n = con.execute(f'select count(*) from "{t}" where sucursal_id=4').fetchone()[0]
        if n:
            print(f"  sucursal_id=4 en {t}: {n} filas")
print("programacion_guardada sucursal_id=4 (muestra):", con.execute("select * from programacion_guardada where sucursal_id=4 limit 2").fetchall().__repr__()[:300])
n_test = con.execute("select count(*) from historial_asignaciones where sucursal_id=4 and obra='Obra Test' and fecha='2026-09-24'").fetchone()[0]
print("filas de prueba a borrar en historial_asignaciones:", n_test)
con.execute("delete from historial_asignaciones where sucursal_id=4 and obra='Obra Test' and fecha='2026-09-24'")
con.commit()

# 3) verificar
res = con.execute("pragma integrity_check").fetchall()
print("integrity_check tras reparar:", [r[0] for r in res][:5])
print("filas historial_asignaciones:", con.execute("select count(*), max(id) from historial_asignaciones").fetchone())
con.close()
