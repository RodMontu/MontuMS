# TAREA — Fase 0, Motor de Tiempos — 2026-09-03
**Aprobado por:** Montu  
**Contexto completo en:** ~/MontuMS/docs/actualizaciones_plan_motor_tiempos.md

## Qué hay que hacer (en orden)

### PASO 0 — verificar credencial (hacerlo primero, antes de cualquier otra cosa)
`ssh TO` y lee el .env del backend de OptiFierro para ver contra qué base apunta la conexión
SQL Server: ¿réplica productiva de Cubigest o CubigestPruebas? Solo repórtalo, no toques nada.

### PASO 1 — entorno de extractor_rutas.py
El script original tiene `BASE_DIR = /home/x/stack/optifierro_v2_frontend` (ruta Linux).
Eso sugiere que corrió dentro del contenedor backend Docker, no en el host Windows.
Confirma con `docker exec` al backend: ¿hay pyodbc y ODBC driver de SQL Server disponibles ahí?

### PASO 2 — índices (Fase 0 Tarea 4 del plan)
Consulta sys.indexes sobre las 6 tablas del JOIN: piezas, detallePaquetesPieza, Viaje, IT,
PIEZA_PRODUCCION, MAQUINA. Solo dime si los campos de JOIN/WHERE tienen índice. No asumas.

### PASO 3 — script de verificación de hipótesis (el núcleo)
Escribe un script Python que corra EN TO (no en el Mac):
- Se conecta a Cubigest usando el mismo método del backend (no inventes credenciales)
- Ejecuta esta query exacta (sin modificar):

```sql
SELECT TOP 5000 dp.Etiqueta AS EtiquetaReal, dp.id AS FilaId, dp.IdMov,
       maq.MAQ_NRO AS MaquinaId, pp.PIE_FECHA_PRODUCCION
FROM piezas p
JOIN detallePaquetesPieza dp ON dp.idpieza = p.id
JOIN Viaje v ON dp.IdViaje = v.Id
JOIN IT it ON v.IdIt = it.Id
JOIN PIEZA_PRODUCCION pp ON pp.PIE_ETIQUETA_PIEZA = dp.id
JOIN MAQUINA maq ON maq.MAQ_NRO = pp.PIE_MAQUINA
WHERE p.estado <> '00' AND it.IdSucursal = 4 AND p.diametro >= 18
  AND pp.PIE_FECHA_PRODUCCION >= DATEADD(month, -1, GETDATE())
```

- Escribe filas a SQLite local en TO (C:\Temp\verificacion_etiqueta.db)
- Agrega EN PYTHON: cuenta MaquinaId distintos por EtiquetaReal
- Devuelve SOLO: total etiquetas únicas, cuántas con NroPasos>1, cuántas con NroPasos=1,
  y máximo 5 ejemplos de EtiquetaReal con NroPasos>1 (solo esos dos campos)

Copia el script a TO vía SCP y ejecútalo desde allá.
A ti solo debe volver ese resumen — sin filas crudas.

### PASO 4 — veredicto
NroPasos>1 aparece → hipótesis CONFIRMADA, Escenario A cerrado a nivel de dato.
Todo en NroPasos=1 → PARA y reporta para investigar IdMov.

### PASO 5 — respaldo (no bloqueante, después del PASO 4)
Carpeta TO: C:\Users\OptiFierro\Desktop\optifierro\auditoria_tiempos_2026\ (22 archivos, ~27MB)
Está excluida del repo por .gitignore. Lee el .gitignore y dime por qué.
Si no hay razón de datos sensibles: crea rama `respaldo/auditoria-tiempos-2026`,
git add + git commit local. NO hagas push — Montu revisa el diff antes.

### LOG — al terminar, en ambos lugares
Texto de transparencia (incluirlo literal):
"CCa orquesta un script Python que corre íntegramente en TO. CCa no lee filas crudas de
Cubigest; solo recibe metadatos (conteos, OK/ERROR). El script hace toda la consulta y
agregación en local."

1. Nueva entrada en ~/MontuMS/docs/bitacora_accesos_torres_ocaranza.md (mismo formato existente)
2. Resumen en el log del Escritorio de TO

### ENTREGABLE
Texto plano: resultado Paso 0, resultado Paso 2, veredicto Paso 3/4, estado Paso 5.
Si algo falla: error completo, no solo la última línea. RCA antes de reintentar.
