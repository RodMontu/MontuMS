CREATE TABLE IF NOT EXISTS documentos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  archivo TEXT NOT NULL,
  seccion TEXT NOT NULL DEFAULT '',
  resumen TEXT,
  tags TEXT,
  fecha_actualizacion TEXT,
  tipo TEXT DEFAULT 'documento',
  UNIQUE(archivo, seccion)
);

CREATE VIRTUAL TABLE IF NOT EXISTS documentos_fts USING fts5(
  archivo, seccion, resumen, tags,
  content='documentos', content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS documentos_ai AFTER INSERT ON documentos BEGIN
  INSERT INTO documentos_fts(rowid, archivo, seccion, resumen, tags)
  VALUES (new.id, new.archivo, new.seccion, new.resumen, new.tags);
END;

CREATE TRIGGER IF NOT EXISTS documentos_ad AFTER DELETE ON documentos BEGIN
  INSERT INTO documentos_fts(documentos_fts, rowid, archivo, seccion, resumen, tags)
  VALUES('delete', old.id, old.archivo, old.seccion, old.resumen, old.tags);
END;

CREATE TRIGGER IF NOT EXISTS documentos_au AFTER UPDATE ON documentos BEGIN
  INSERT INTO documentos_fts(documentos_fts, rowid, archivo, seccion, resumen, tags)
  VALUES('delete', old.id, old.archivo, old.seccion, old.resumen, old.tags);
  INSERT INTO documentos_fts(rowid, archivo, seccion, resumen, tags)
  VALUES (new.id, new.archivo, new.seccion, new.resumen, new.tags);
END;

CREATE TABLE IF NOT EXISTS credenciales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  servicio TEXT NOT NULL,
  variable TEXT NOT NULL,
  archivo_env TEXT NOT NULL,
  fecha_creacion TEXT,
  fecha_rotacion TEXT,
  notas TEXT,
  UNIQUE(servicio, variable)
);

CREATE TABLE IF NOT EXISTS relaciones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tema TEXT NOT NULL,
  impacta_a TEXT NOT NULL
);
