"""
migrate_baja_desvinculados_20261006.py — QA SPP 05/06-10-2026, Montu confirmo los 7.
Regla: si un colaborador desaparece del listado (roster) de Geovictoria, se elimina del SPP.
Re-verificado 06-10 contra el roster COMPLETO de HOY por sucursal (no solo 30 dias de
asistencia): ninguno de los 7 aparece hoy, y su ultima aparicion fue hace 2 a 5 meses.

Elimina de operadores_matriz las 7 filas, y en maquinas_info limpia Operador_Habitual /
Operador_Habitual_Noche cuando referencian a alguno de estos 7 -- esos campos guardan el
NOMBRE COMPLETO, no el username (verificado en vivo), asi que el match es por nombre
normalizado (sin acentos, minuscula). Evita que una maquina quede mostrando como habitual a
alguien que ya no existe en el SPP (el mismo problema que vimos ayer con Hector Acuña en
Linea Corte Coronel). No toca Geovictoria (no es nuestro).

Uso:  python migrate_baja_desvinculados_20261006.py <ruta_db>
Idempotente: si ya se aplico, no encuentra filas y no hace nada.
"""
import sqlite3
import sys
import unicodedata


def _norm(s):
    s = s or ""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").strip().lower()


BAJAS = [
    (14, "agarcia", "Anibal Luis Alberto Garcia Aguayo"),
    (14, "hacuna", "Hector Manuel Acuña Sanhueza"),
    (14, "gacuna", "Giovanni Mauricio Acuña Sanhueza"),
    (10, "fquezada", "Fabian Eduardo Quezada Gonzalez"),
    (10, "jmedina", "Jofran Orlando Medina Meza"),
    (10, "mgutierrez", "Miguel Alonso Gutierrez Consuegra"),
    (10, "gsepulveda", "Gabriel Antonio Sepulveda Alarcon"),
]


def main(db_path: str) -> None:
    con = sqlite3.connect(db_path)
    con.execute("PRAGMA busy_timeout=60000")
    cols_hab = [r[1] for r in con.execute("PRAGMA table_info(maquinas_info)")]
    assert {"Operador_Habitual", "Operador_Habitual_Noche"} <= set(cols_hab)

    borradas = 0
    maquinas_limpiadas = []
    for suc, user, nombre in BAJAS:
        row = con.execute(
            "SELECT id FROM operadores_matriz WHERE sucursal_id=? AND Operador=?",
            (suc, user),
        ).fetchone()
        if not row:
            print(f"  (sin fila en operadores_matriz para {user} en sucursal {suc}; ya aplicado o no existe)")
        else:
            con.execute(
                "DELETE FROM operadores_matriz WHERE sucursal_id=? AND Operador=?", (suc, user)
            )
            borradas += 1
            print(f"  BAJA operadores_matriz: sucursal={suc} {user} ({nombre})")

        # Operador_Habitual / _Noche guardan el NOMBRE COMPLETO, no el username.
        for col in ("Operador_Habitual", "Operador_Habitual_Noche"):
            candidatas = con.execute(
                f'SELECT maquina, "{col}" FROM maquinas_info WHERE sucursal_id=?', (suc,)
            ).fetchall()
            for maquina, valor in candidatas:
                if _norm(valor) == _norm(nombre):
                    con.execute(
                        f'UPDATE maquinas_info SET "{col}"=NULL WHERE sucursal_id=? AND maquina=?',
                        (suc, maquina),
                    )
                    maquinas_limpiadas.append((suc, maquina, col, valor))
    con.commit()

    print(f"\nTotal filas eliminadas de operadores_matriz: {borradas}/{len(BAJAS)}")
    print("Referencias de habitual limpiadas:")
    for m in maquinas_limpiadas:
        print("  ", m)
    if not maquinas_limpiadas:
        print("   ninguna")

    quedan = con.execute(
        "SELECT sucursal_id, Operador FROM operadores_matriz WHERE Operador IN (%s)"
        % ",".join("?" * len(BAJAS)),
        [u for _, u, _ in BAJAS],
    ).fetchall()
    assert not quedan, f"quedaron filas sin borrar: {quedan}"
    print("Verificado: 0 filas restantes de los 7 usuarios dados de baja en operadores_matriz.")
    con.close()


if __name__ == "__main__":
    main(sys.argv[1])
