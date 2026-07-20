"""Lectura rapida: ultima version conocida de un archivo/seccion."""

import sqlite3

from ._conexion import conectar


def obtener_ultima_version(archivo: str, seccion: str | None = None) -> dict:
    try:
        conn = conectar()
    except sqlite3.Error as e:
        return {"error": f"no se pudo conectar a catalogo.db: {e}"}
    try:
        if seccion is not None:
            row = conn.execute(
                """
                SELECT archivo, seccion, resumen, tags, fecha_actualizacion
                FROM documentos
                WHERE archivo = ? AND seccion = ?
                """,
                (archivo, seccion),
            ).fetchone()
        else:
            row = conn.execute(
                """
                SELECT archivo, seccion, resumen, tags, fecha_actualizacion
                FROM documentos
                WHERE archivo = ?
                ORDER BY fecha_actualizacion DESC
                LIMIT 1
                """,
                (archivo,),
            ).fetchone()
        return dict(row) if row else {}
    except sqlite3.Error as e:
        return {"error": f"error consultando documentos: {e}"}
    finally:
        conn.close()
