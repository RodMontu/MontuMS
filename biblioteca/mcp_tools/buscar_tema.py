"""Lectura rapida: busqueda de texto completo sobre documentos_fts.
No pasa por ningun LLM ni por Aurora."""

import re
import pysqlite3 as sqlite3

from ._conexion import conectar

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _sanitizar_query_fts(query: str) -> str | None:
    """Extrae solo tokens de palabra del texto de entrada, descartando
    cualquier caracter que FTS5 interprete como operador de sintaxis
    (guion = NOT, parentesis = agrupacion, dos puntos = filtro de columna,
    asterisco = prefijo, comillas = frase). El resultado es una lista de
    palabras sueltas unidas por espacio, que FTS5 combina con AND implicito
    por defecto -- sin ningun caracter que pueda romper el parser, sin
    importar que tan puntuado venga el texto original (fechas, titulos con
    parentesis, terminos con guion, etc.). Devuelve None si no queda ningun
    token util (query vacio o solo puntuacion)."""
    tokens = _TOKEN_RE.findall(query or "")
    if not tokens:
        return None
    return " ".join(tokens)


def buscar_tema(query: str) -> list[dict]:
    query_segura = _sanitizar_query_fts(query)
    if query_segura is None:
        return []
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
            (query_segura,),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        return [{"error": f"error de busqueda en documentos_fts: {e}"}]
    finally:
        conn.close()
