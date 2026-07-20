"""Lectura rapida de METADATA de credenciales unicamente.
La tabla 'credenciales' nunca almacena valores reales, solo referencias
a donde vive cada secreto (servicio, variable, archivo .env)."""

import sqlite3

from ._conexion import conectar


def buscar_credencial(query: str) -> list[dict]:
    try:
        conn = conectar()
    except sqlite3.Error as e:
        return [{"error": f"no se pudo conectar a catalogo.db: {e}"}]
    try:
        like = f"%{query}%"
        rows = conn.execute(
            """
            SELECT servicio, variable, archivo_env, fecha_creacion, fecha_rotacion, notas
            FROM credenciales
            WHERE servicio LIKE ? OR variable LIKE ?
            ORDER BY servicio
            """,
            (like, like),
        ).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        return [{"error": f"error de busqueda en credenciales: {e}"}]
    finally:
        conn.close()
