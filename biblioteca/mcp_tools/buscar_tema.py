"""Lectura rapida: busqueda de texto completo sobre documentos_fts.
No pasa por ningun LLM ni por Aurora."""

import sqlite3

from ._conexion import conectar


def buscar_tema(query: str) -> list[dict]:
    try:
        conn = conectar()
    except sqlite3.Error as e:
        return [{"error": f"no se pudo conectar a catalogo.db: {e}"}]
    try:
        rows = conn.execute(
            """
            SELECT d.archivo, d.seccion, d.resumen, d.tags, d.fecha_actualizacion,
                   bm25(documentos_fts) AS relevancia
            FROM documentos_fts
            JOIN documentos d ON d.id = documentos_fts.rowid
            WHERE documentos_fts MATCH ?
            ORDER BY relevancia
            """,
            (query,),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        return [{"error": f"error de busqueda en documentos_fts: {e}"}]
    finally:
        conn.close()
