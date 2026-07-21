#!/usr/bin/env python3
"""Indexador de La Biblioteca: aplica schema.sql y sincroniza catalogo.db
a partir de los .md de MontuMS (raiz y docs/), seccion por seccion."""

import argparse
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
MONTUMS_ROOT = BASE_DIR.parent
DB_PATH = BASE_DIR / "catalogo.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

# Nota: al 2026-07-19 las versiones vigentes de INVENTARIO_MAESTRO.md y
# LOG_CAMBIOS_2026.md viven en MontuMS/docs/ (mas recientes que las copias
# de nivel superior con el mismo nombre). Se indexan ambas ubicaciones;
# el campo 'archivo' guarda la ruta relativa a MONTUMS_ROOT para no pisarse.
SCAN_DIRS = [MONTUMS_ROOT, MONTUMS_ROOT / "docs"]

# Carpetas que NUNCA deben indexarse, aunque queden dentro de SCAN_DIRS
# (defensa en profundidad: hoy el glob no es recursivo asi que no las toca,
# pero si SCAN_DIRS o el glob cambian a futuro, esto evita que se cuelen).
# miau_nube_copia/ es una copia local del NAS, no documentacion propia de
# MontuMS. biblioteca/ es el propio sistema de indexado y no debe auto-indexarse.
EXCLUDE_DIRS = {"miau_nube_copia", "biblioteca"}


def _excluido(path: Path) -> bool:
    return bool(EXCLUDE_DIRS & set(path.relative_to(MONTUMS_ROOT).parts[:-1]))

HEADER_RE = re.compile(r"^(#{2,3})\s+(.*)$")


def migrar_seccion_not_null(conn: sqlite3.Connection) -> bool:
    """Normaliza seccion NULL -> '' y, si la tabla 'documentos' vigente
    todavia permite NULL en esa columna (schema anterior a este fix),
    la reconstruye con 'seccion TEXT NOT NULL DEFAULT ''' + UNIQUE(archivo,
    seccion). SQLite no trata NULLs como iguales en restricciones UNIQUE,
    asi que con el schema viejo podian colarse duplicados silenciosos."""
    existe = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documentos'"
    ).fetchone()
    if existe is None:
        return False

    conn.execute("UPDATE documentos SET seccion = '' WHERE seccion IS NULL")
    conn.commit()

    info = conn.execute("PRAGMA table_info(documentos)").fetchall()
    seccion_col = next((c for c in info if c[1] == "seccion"), None)
    if seccion_col is not None and seccion_col[3] == 1:
        return False  # ya es NOT NULL, nada que migrar

    antes = conn.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]

    conn.executescript(
        """
        DROP TRIGGER IF EXISTS documentos_ai;
        DROP TRIGGER IF EXISTS documentos_ad;
        DROP TRIGGER IF EXISTS documentos_au;
        DROP TABLE IF EXISTS documentos_fts;

        CREATE TABLE documentos_new (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          archivo TEXT NOT NULL,
          seccion TEXT NOT NULL DEFAULT '',
          resumen TEXT,
          tags TEXT,
          fecha_actualizacion TEXT,
          tipo TEXT DEFAULT 'documento',
          UNIQUE(archivo, seccion)
        );

        INSERT INTO documentos_new
            (id, archivo, seccion, resumen, tags, fecha_actualizacion, tipo)
        SELECT d.id, d.archivo, COALESCE(d.seccion, ''), d.resumen, d.tags,
               d.fecha_actualizacion, d.tipo
        FROM documentos d
        JOIN (
            SELECT archivo, COALESCE(seccion, '') AS seccion_norm, MAX(id) AS keep_id
            FROM documentos
            GROUP BY archivo, seccion_norm
        ) k ON k.keep_id = d.id;

        DROP TABLE documentos;
        ALTER TABLE documentos_new RENAME TO documentos;
        """
    )
    conn.commit()

    despues = conn.execute("SELECT COUNT(*) FROM documentos").fetchone()[0]
    if despues < antes:
        print(
            f"  [migracion] {antes - despues} fila(s) duplicada(s) por "
            f"seccion NULL colapsadas (se conservo la de mayor id por "
            f"archivo+seccion)."
        )

    return True


def aplicar_schema(conn: sqlite3.Connection) -> None:
    reconstruido = migrar_seccion_not_null(conn)
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()
    if reconstruido:
        # la tabla documentos_fts se recreo vacia: repoblarla desde documentos
        conn.execute("INSERT INTO documentos_fts(documentos_fts) VALUES('rebuild')")
        conn.commit()


def extraer_secciones(texto: str) -> list[dict]:
    """Divide el markdown en secciones por headers ## o ###."""
    lineas = texto.splitlines()
    secciones = []
    actual_titulo = "introduccion"
    actual_cuerpo: list[str] = []

    def cerrar_seccion():
        if actual_cuerpo or actual_titulo != "introduccion":
            cuerpo = "\n".join(actual_cuerpo).strip()
            if cuerpo:
                secciones.append({"titulo": actual_titulo, "cuerpo": cuerpo})

    for linea in lineas:
        m = HEADER_RE.match(linea)
        if m:
            cerrar_seccion()
            actual_titulo = m.group(2).strip()
            actual_cuerpo = []
        else:
            actual_cuerpo.append(linea)
    cerrar_seccion()
    return secciones


def resumir(cuerpo: str, max_len: int = 240) -> str:
    texto = " ".join(cuerpo.split())
    if len(texto) <= max_len:
        return texto
    return texto[:max_len].rsplit(" ", 1)[0] + "..."


def indexar_archivo(conn: sqlite3.Connection, path: Path) -> int:
    from clasificador import clasificar

    texto = path.read_text(encoding="utf-8", errors="replace")
    archivo_rel = str(path.relative_to(MONTUMS_ROOT))
    fecha = datetime.now(timezone.utc).isoformat()
    secciones = extraer_secciones(texto)

    filas = 0
    for sec in secciones:
        resumen = resumir(sec["cuerpo"])
        clasificacion = clasificar(sec["titulo"] + " " + sec["cuerpo"])
        tags = clasificacion["tags"]
        seccion = sec["titulo"] or ""
        conn.execute(
            """
            INSERT INTO documentos (archivo, seccion, resumen, tags, fecha_actualizacion, tipo)
            VALUES (?, ?, ?, ?, ?, 'documento')
            ON CONFLICT(archivo, seccion) DO NOTHING
            """,
            (archivo_rel, seccion, resumen, ",".join(tags), fecha),
        )
        filas += 1
    conn.commit()
    return filas


def encontrar_markdowns(solo_archivo: str | None) -> list[Path]:
    if solo_archivo:
        candidatos = []
        for d in SCAN_DIRS:
            p = d / solo_archivo
            if p.exists():
                candidatos.append(p)
        if not candidatos:
            p = Path(solo_archivo)
            if p.exists():
                candidatos.append(p)
        return candidatos

    encontrados = []
    for d in SCAN_DIRS:
        if not d.exists():
            continue
        encontrados.extend(sorted(d.glob("*.md")))
    return [p for p in encontrados if not _excluido(p)]


def limpiar_huerfanos(conn: sqlite3.Connection) -> int:
    """Borra de documentos (con su sincronizacion via triggers en documentos_fts)
    cualquier fila cuyo 'archivo' ya no exista como archivo real en disco."""
    cur = conn.execute("SELECT DISTINCT archivo FROM documentos")
    archivos_en_db = [row[0] for row in cur.fetchall()]

    borrados = 0
    for archivo_rel in archivos_en_db:
        if not (MONTUMS_ROOT / archivo_rel).exists():
            cur = conn.execute("DELETE FROM documentos WHERE archivo = ?", (archivo_rel,))
            borrados += cur.rowcount

    conn.commit()
    return borrados


def main():
    parser = argparse.ArgumentParser(description="Indexa documentos de MontuMS en catalogo.db")
    parser.add_argument("--solo-archivo", help="Indexa un unico archivo .md (nombre o ruta)")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    aplicar_schema(conn)

    archivos = encontrar_markdowns(args.solo_archivo)
    if not archivos:
        print("No se encontraron archivos .md para indexar.")
    else:
        total = 0
        for path in archivos:
            filas = indexar_archivo(conn, path)
            total += filas
            try:
                etiqueta = path.relative_to(MONTUMS_ROOT)
            except ValueError:
                etiqueta = path
            print(f"  {etiqueta}: {filas} secciones")

        print(f"\nTotal secciones procesadas: {total}")

    borrados = limpiar_huerfanos(conn)
    print(f"Filas huerfanas eliminadas (archivo ya no existe en disco): {borrados}")

    conn.close()


if __name__ == "__main__":
    main()
