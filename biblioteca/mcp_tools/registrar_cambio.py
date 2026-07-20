"""Camino de escritura: usado exclusivamente por Aurora (la bibliotecaria).
Ningun otro agente ni la futura UI debe llamar a esta funcion."""

import sqlite3
from datetime import datetime, timezone

from ._conexion import conectar


def registrar_cambio(
    archivo: str,
    seccion: str,
    resumen: str,
    tags: str,
    tipo: str = "documento",
) -> dict:
    if seccion is None:
        seccion = ""
    try:
        conn = conectar()
    except sqlite3.Error as e:
        return {"error": f"no se pudo conectar a catalogo.db: {e}"}
    try:
        conn.execute(
            """
            INSERT INTO documentos (archivo, seccion, resumen, tags, fecha_actualizacion, tipo)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(archivo, seccion) DO UPDATE SET
                resumen = excluded.resumen,
                tags = excluded.tags,
                fecha_actualizacion = excluded.fecha_actualizacion,
                tipo = excluded.tipo
            """,
            (archivo, seccion, resumen, tags, datetime.now(timezone.utc).isoformat(), tipo),
        )
        conn.commit()
        return {"status": "ok"}
    except sqlite3.Error as e:
        return {"error": f"error registrando cambio: {e}"}
    finally:
        conn.close()
