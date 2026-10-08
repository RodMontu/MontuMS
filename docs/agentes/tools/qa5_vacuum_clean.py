import sqlite3, os, sys, time
SRC = "/work/optifierro_v2.db"
DST = "/work/optifierro_v2_CLEAN.db"
if os.path.exists(DST):
    os.remove(DST)
s = sqlite3.connect(SRC, timeout=60)
print("journal_mode origen:", s.execute("pragma journal_mode").fetchone()[0])
try:
    print("integrity origen:", [r[0] for r in s.execute("pragma integrity_check")][:3])
except Exception as e:
    print("integrity origen: error al recorrer ->", e)
t0 = time.time()
s.execute(f"VACUUM INTO '{DST}'")
print(f"VACUUM INTO OK ({time.time()-t0:.1f}s), tamano limpio: {os.path.getsize(DST)}")
c = sqlite3.connect(DST)
print("integrity LIMPIA:", [r[0] for r in c.execute("pragma integrity_check")])
# comparar filas tabla por tabla (sin perdida de datos)
malas = 0
for (t,) in s.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'").fetchall():
    a = s.execute(f'select count(*) from "{t}"').fetchone()[0]
    b = c.execute(f'select count(*) from "{t}"').fetchone()[0]
    if a != b:
        malas += 1
        print(f"  DIFERENCIA {t}: origen={a} limpia={b}")
print("tablas con diferencia de filas:", malas)
# residuos de pruebas: sucursal_id=4 no existe en produccion (plantas 1, 10, 14)
for (t,) in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'").fetchall():
    cols = [r[1] for r in c.execute(f'pragma table_info("{t}")')]
    if "sucursal_id" in cols:
        n = c.execute(f'select count(*) from "{t}" where sucursal_id=4').fetchone()[0]
        if n:
            print(f"  residuo sucursal_id=4 en {t}: {n} filas ->", c.execute(f'select * from "{t}" where sucursal_id=4 limit 1').fetchall().__repr__()[:240])
c.close(); s.close()
