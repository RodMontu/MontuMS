"""Helper de conexion compartido para mcp_tools/.
WAL evita que registrar_cambio (escritura) bloquee las lecturas
concurrentes (buscar_tema, obtener_ultima_version, buscar_credencial)
con 'database is locked'; timeout da margen si igual hay contencion breve."""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "catalogo.db"


def conectar() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.row_factory = sqlite3.Row
    return conn
