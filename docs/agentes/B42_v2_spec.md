# B42 v2 — Spec: "una cajita = una etiqueta" (Gantt del SPP)

**Fecha:** 24-09-2026 · **Ventana:** V5 (Miaude / Mi TI) con Montu · **Estado:** SPEC CERRADA (Paso A). Sin codigo escrito.
**Revision con Gerencias y jefes de planta:** movida al viernes 25-09-2026 (Montu, 24-09).

## 1. Origen y hallazgo de QA
- Minuta Cerrillos 22-09 (Jose Auger, Jefe de Planta): pedido B42. B42 v1 (`1dda6e0`) rotulo la cajita con el N° de una etiqueta *representante* del grupo. No calza con lo pedido.
- Interpretacion correcta (Montu, 24-09), con foto de la etiqueta fisica de Calama (Francisco Ramos, Jefe de Planta; viaje ASR-266/1, etiquetas 1 y 2 de 13) y captura del detalle actual de Cerrillos (viaje R68-379/1, "Etiquetas incluidas (44)" = el viaje completo).
- Causa del desajuste (espejo `4325640`, NO VERIFICADO contra `master 1cd8f88`): el Motor agrupa por (codigo_viaje, diametro, etapa_avance) en `motor_v2.py` y cada grupo es una cajita; el detalle se arma por viaje+maquina (`detalle-maquina`, `tags-viaje`) sin filtrar por `lista_etiqueta_ids`.

## 2. Definicion
**Una cajita = una etiqueta (TAG) = un trabajo.** Etiqueta y TAG son el mismo concepto. Campos de la etiqueta fisica (nombre nuestro):
1 Obra (proyecto) · 2 Viaje · 3 Etiqueta (identifica la cajita) · 4 Diametro · 5 Largo (total de la pieza) · 6 Cantidad (piezas a fabricar) · 7 Paquete (mismo N° que la etiqueta) · 8 Peso de la etiqueta (casi nunca > 1000 kg) · 9 Marca (NO se agrega) · 10 Calidad del acero.
"Pieza" en la etiqueta fisica es una figura; en el SPP se sigue usando el ID_forma (numero).

## 3. Regla de series (Motor)
Etiquetas con igual (viaje, diametro, id_forma, largo, calidad, etapa_avance) forman una **serie**. La serie se asigna a UNA maquina, sus etiquetas quedan **una tras otra** (cajitas consecutivas). Repartir la serie en 2 maquinas en paralelo: solo manual (doble clic) mas la alerta por umbral existente. La optimizacion automatica sin repartir vs repartida es **Fase 2** (seccion 9).

## 4. Caratula de la cajita (imagen 4 de Montu; mismo aspecto que hoy)
Viaje · `Etiqueta N de M` (N = etiqueta que se ejecuta, ej. "1 of 13") · Diametro (muy importante) · Peso de la etiqueta (kg) · aviso ATRASO igual que hoy (no se modifica).

## 5. Detalle (1 clic)
- Formato visual identico al actual. Arriba se mantiene "Ajustar duracion del trabajo (en minutos)" en la misma posicion.
- **Header** (mismos colores): viaje, obra, etiqueta, calidad (solo se agrega "etiqueta").
- **Cuerpo**: campos 4 a 8 del punto 2, en ese orden, mas ID_forma en el lugar de "Pieza" (entre largo y cantidad). Sin repetir lo que esta en el header. Sin "marca". Sin lista "Etiquetas incluidas".

## 6. Lo que NO cambia
Doble clic = repartir en maquinas (B2) · "Ajustar duracion" (B44a) · aviso ATRASO · formato visual del detalle · drag&drop (B33/B34) · B16 (capacidad), B35 (ventana +-15), B45 (FP-LC fuera).

## 7. Criterios de aceptacion (medibles)
- AC1: en el plan real de Cerrillos (turno dia), N° de cajitas = N° de etiquetas asignadas; toda cajita tiene exactamente 1 `etiqueta_id`.
- AC2: caratula con viaje, `Etiqueta N de M`, diametro, peso de la etiqueta y ATRASO cuando `dias_atraso` lo indica (criterio actual).
- AC3: detalle con los campos de la seccion 5; peso = `KgsPaquete` y cantidad = `NroPiezas` de esa etiqueta, cotejados con SELECT acotado a Cubigest.
- AC4: para toda serie, todas sus cajitas estan en la misma maquina y consecutivas (sin otra serie intercalada), salvo reparto manual.
- AC5: conservacion: mismas etiquetas y mismos kg totales antes y despues (sin perdidas ni duplicados).
- AC6: la maquina asignada a cada serie es elegible para su forma y diametro (hoy se decide con una etiqueta representante).
- AC7: sin regresion en B2, B44a, B16, B35, B45 (API + lectura de codigo); el drag real lo confirma Montu con el mouse.
- AC8: rendimiento: tiempo del GET del plan y render con N real de cajitas de Cerrillos, sin degradacion perceptible (se mide N y tiempo).
- AC9: `py_compile` y build TypeScript limpios; arnes antes/despues sobre copia de datos, nunca `POST /generar` contra produccion.

## 8. Archivos probables (a confirmar en Paso B)
`motor_v2.py` (clave de agrupacion y emision por etiqueta; territorio compartido: avisar a la Coordinadora antes de editar) · `routers/programacion.py` (`_tarea_a_evento`, detalle, `id_tarea`) · `GestorProgramacion.tsx` (caratula, tooltip, modal). Verificar estado de CCa-8b (worktree `optifierro_g`) antes de tocar el frontend.

## 9. Fase 2 (post-entrega, spec propia)
Motor define dos escenarios (sin repartir / repartido) y elige el que da "la maxima produccion en el menor tiempo posible" de toda la jornada. Pendiente definir el criterio: (a) menor tiempo total de la jornada, (b) mas toneladas terminadas dentro del turno, (c) menor atraso ponderado. Requiere modelar el reparto dentro de `programar_turno` (hoy es post-hoc en `/aplicar-reparto`).

## 10. Supuestos vigentes (se validan con el resultado visual)
Operador y Secuencia salen del detalle (el operador ya esta en la fila de la maquina) · chip del header `CALIDAD | VIAJE | ETIQUETA: N de M` · aplica igual a las 3 plantas · formato `Etiqueta N de M`.

## 11. Riesgos a verificar en Paso B
- B44(a): `ajustes_duracion` se indexa por `id_tarea` (etiqueta_id + paso_secuencia); cambia la unidad, cambia la clave.
- B2/drag&drop operan por `pid`; pasan a actuar sobre una etiqueta.
- B42 v1: `_mapa_numero_etiqueta` es memoria volatil y el scheduler (08:10/20:10) no la puebla; en v2 N, M, diametro y peso deben viajar con la tarea desde la entrada del Motor.
- Legibilidad: cajitas angostas; rendimiento con cientos de draggables (dnd-kit).
- Hipotesis a verificar: "Id Paq" de la etiqueta fisica (3601069, 3601070) = `dp.id` (secuencial).

## 12. Decisiones de Montu tras el Paso B (24-09, ≈12:30) — vigentes para la Fase 1
- **Duracion:** la duracion de la serie se calcula como hoy (`estimar_duracion_min` con los kg de la serie) y se **reparte entre sus etiquetas proporcional a kg**. Conserva los tiempos que calcula el Motor. No se recalibra `KgsPromedio_por_trabajo` (su escala ya es de etiqueta: 42 a 636 kg, verificado en `deltat_por_forma_maquina.csv`).
- **Calidad del acero:** se mantiene `mp.CalidadAcero` con default `A630`. Diferencia CONOCIDA con la etiqueta fisica ("A630-420H NORMAL (A)"): `IT.TipoAcero` tiene el grado real ('A630-420H', verificado en Id 207900); queda como mejora posterior, no entra en la Fase 1.
- **Cajita angosta (~570 cajitas por turno en Cerrillos):** prioridad de lectura = Diametro, luego `N de M`, luego peso; lo que no quepa va al tooltip.
- **`ajustes_duracion` / `programacion_manual`:** las claves `id_tarea` cambian de "etiqueta representante del grupo" a "etiqueta propia"; los ajustes guardados con clave vieja quedan huerfanos e inertes tras el deploy (B44a existe solo desde hoy 08:13; contar filas antes del deploy).
- **Riesgo a vigilar:** hoy el tope de 480 min oculta grupos sobrecargados (ej. 200 etiquetas); al desagrupar, la carga real de la serie puede verse. Con el reparto proporcional de la duracion de la serie el tope se mantiene por serie.

## 13. Decisión de Montu — reparto en paralelo queda MANUAL (24-09, ~20:15)
Se desiste del auto-reparto de una serie larga entre 2 máquinas para esta entrega. Razón operativa (Montu): prefiere que cada Jefe de Planta lo haga manual. Razón técnica adicional (Miaude): con unidad=etiqueta, el doble clic histórico (pensado para partir un GRUPO/serie completa en una sola cajita) pierde sentido a nivel de una sola etiqueta — no hay nada que partir dentro de una pieza. La forma natural de "reparto manual" en la unidad nueva es **arrastrar** las cajitas-etiqueta sobrantes de una serie a otra máquina (drag&drop existente, no tocado, más fino que un 50/50 automático).
**Implementado (commit `313d089`, sobre `5a94add`):** se mantiene el umbral corregido por SERIE completa (K2 de CCa-14: evita alertas espurias en series de 1 etiqueta) y la `alerta_reparto` informativa con máquina sugerida, pero **se retira la acción de auto-división**. Lo que no cabe en el turno cae a bolsa (`turno_lleno`), como antes de cualquier reparto automático. `_partir_serie_por_kg` queda definida, testeada y sin usar, reservada para una eventual Fase 2.
**Resultado (universo real, VIEJO=master vs NUEVO):** Cerrillos 88% de los kg del viejo (146 etiquetas a bolsa), Calama 76% (21 a bolsa), Coronel 98% (1 a bolsa). Mejor que el intento de auto-split (Cerrillos 42%, Calama 74%) y sin el riesgo de saturación en cadena entre series competidoras por la misma máquina sugerida.
**Doble clic (RepartoModal): CONFIRMADO SIN CAMBIOS (Montu, 24-09 ~20:45).** No se oculta ni se deshabilita para una tarea de 1 etiqueta. Corrección de la hipótesis anterior: no toda etiqueta es un trabajo corto — con acero grueso y formas complejas, una sola etiqueta puede tomar mucho tiempo, y ahí repartir el trabajo de ESA etiqueta entre 2 máquinas en paralelo (doble clic) sigue siendo una operación legítima y útil, independiente de si su serie es larga o corta.
