# Handoff — Material recuperado de la investigación "tiempos por máquina" pre-incidente

**Fecha de este hallazgo:** 2026-09-03
**Encontrado por:** Miaude, durante la resolución de un incidente no relacionado (máquina "FORMULA 12" ausente en Cerrillos, mismo repo OptiFierro)
**Por qué existe este documento:** Montu preguntó si la investigación de "tiempos por máquina" que quedó interrumpida por el incidente de seguridad del 1 de agosto dejó algo recuperable. La respuesta es sí. Este documento resume todo lo encontrado, más el prompt de handoff completo entregado en el chat del motor de tiempos.

**Nota:** el contenido íntegro (inventario, JSON de metodología, schemas, recomendaciones) está en
`/mnt/user-data/outputs/HANDOFF_hallazgo_auditoria_tiempos_2026-09-03.md`, entregado directamente a
Montu como artefacto para copiar/pegar en la sesión del motor de tiempos. Este archivo en MontuMS es
la copia de referencia para que quede indexado y no se pierda.

## Resumen ejecutivo

- Carpeta encontrada: `auditoria_tiempos_2026/` en el repo OptiFierro de TO
  (`/c/Users/OptiFierro/Desktop/optifierro/auditoria_tiempos_2026/`).
- 22 archivos, ~27 MB, todos fechados 2026-07-15 (~02:45-02:56), dos semanas
  antes del incidente de disponibilidad del 31-jul/1-ago.
- **NO está en git** — excluida por `.gitignore`, vive solo en disco de TO,
  sin respaldo. Recomendación: copiarla a un lugar con respaldo cuanto antes.
- Contiene: dataset crudo (`dataset_tiempos_completo.csv`, 26.8 MB, ~128K
  registros, ventana jul-2025/jul-2026), matrices/estadísticos agregados, y
  metodología completa ya validada (mediana como estimador central, filtro
  IQR×1.5, ventana 12 meses).
- Hallazgo clave del análisis previo: modelo de regresión desde geometría de
  pieza (largo, nro. puntos, diámetro) da **R²=0.0096** — prácticamente nulo,
  con multicolinealidad severa. Confirma que la geometría sola no explica el
  tiempo de proceso; el giro actual hacia ETIQUETA/TAG + censura por causa
  va en la dirección correcta.
- No existe tabla de dotación en Cubigest (confirmado por búsqueda en
  INFORMATION_SCHEMA en esa corrida de julio) — dato ya conocido, reafirmado.
- Pendiente de revisión (requiere Carlitos para el dataset crudo, o lectura
  directa para los 2 scripts .py que son metodología propia): el dataset
  completo, los CSV agregados individuales, y `run_auditoria_tiempos.py` /
  `run_modulo5_cientifico.py`.

## Fuentes
- `incidente_seguridad.md` — informe de los incidentes de agosto.
- `actualizaciones_plan_motor_tiempos.md` — plan vigente del motor de tiempos
  (sesión 2026-09-02).
- `bitacora_accesos_torres_ocaranza.md` — incidente Formula 12 durante el
  cual se encontró esto.
