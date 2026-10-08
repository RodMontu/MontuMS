# Mapa de decisiones del SPP — estadísticas, análisis y asignación de trabajos

**Creado:** 2026-09-23 · **Encargado por:** Montu · **Mantiene:** cada ventana que cambie un criterio (ver sección 6)
**Propósito:** tener "mapeado" en un solo lugar qué decisiones toma el SPP (Sistema Planificador de la Producción), con qué valor o regla, por qué (dato o quién lo definió), dónde vive en el código y si va al manual de entrega. Es la fuente para los manuales, para la capacitación y para no re-discutir lo ya decidido.

**Cómo leerlo:** cada fila es una decisión con ID estable (`PRO-`, `EST-`, `ASG-`). Columnas: **Regla** (qué se hace), **Por qué** (evidencia o responsable), **Fuente / código** (dónde verificarla), **Fecha · quién** (cuándo y quién la aprobó) y **Manual** (sí = debe explicarse a los usuarios).
**Regla de honestidad de este documento:** solo entra lo verificado en código o en un documento de análisis. Donde el motivo no está documentado se escribe "motivo no documentado" en vez de reconstruirlo. Lo que falta por mapear está en la sección 5.

Estados: `VIGENTE` (en código) · `VIGENTE` (implementado y verificado en arnés, falta desplegar) · `POR CONFIRMAR` · `PENDIENTE` (decidido, no implementado).

---

## 1. Pantalla "Producción por Máquina" (B26, versión A) — `PRO-`
Código: `backend/routers/tiempos_maquina.py`, `frontend/src/components/domain/TiemposPorMaquina.tsx`. Detalle narrativo para manuales: `B26_A_criterios_produccion_maquina.md`. Todas las decisiones de esta sección: **Montu, 23-09-2026** (con Mi TI), estado `VIGENTE`.

| ID | Regla | Por qué | Fuente / código | Manual |
|---|---|---|---|---|
| PRO-01 | El peso de cada registro es `detallePaquetesPieza.KgsPaquete` (peso de la etiqueta), no `piezas.TotalKgs` | `TotalKgs` es el peso TOTAL de la línea de pieza (de 1 a 23.000 kg); inflaba el ton/hora 3 a 8 veces en líneas de corte (Línea de Corte Cerrillos, forma 1 Ø16: 7,75 → 1,04) | query en `get_tiempos_maquina`; evidencia `agentes/evidencia_B26/antes` vs `despues_preliminar` | Sí |
| PRO-02 | El peso por barra es `KgsPaquete / NroPiezas`; el largo que ingresa el usuario se convierte con `diámetro² / 162 × largo (m)` | En 8 combinaciones de las 3 plantas, el kg/barra de Cubigest coincide con la fórmula (razón mediana 1,00; P10–P90 entre 0,98 y 1,05 en máquinas sin corte) | `_peso_estimado_kg`, cálculo de `kg_barra_i` | Sí |
| PRO-03 | Un intervalo válido es el tiempo entre dos registros consecutivos de una misma máquina y sucursal, de 2 a 480 minutos | Menos de 2 min es ruido dentro del mismo lote; más de 480 es pausa entre turnos o días. Criterio histórico del endpoint, mantenido | `_DELTA_MIN_MIN`, `_DELTA_MAX_MIN` | Sí |
| PRO-04 | La producción de un intervalo es `KgsPaquete / duración`; se descarta el intervalo si supera 50 ton/hora | Mismo criterio de FASE3 (`ton_hora>50` = outliers de duración cercana a 0). La foto ANTES mostraba 91,8 ton/h en Cortadora Manual Coronel con N=5 | `_TONH_MAX`; `FASE3_PESO_POR_PIEZA_20260921.md` línea 21 | Sí |
| PRO-05 | Se muestra la mediana y el rango típico P25–P75; nunca un "% de confianza" ni media ± desviación | Ninguna familia de distribución pasó el ajuste en las 32 máquinas evaluables (datos bimodales); un % de confianza sería falso (ver EST-06) | `_percentil`, `ton_hora_p25/p75`; `FASE3_ESTADISTICA_APLICADA_20260913.md` | Sí |
| PRO-06 | Con menos de 15 intervalos válidos, la máquina se lista con su N pero sin ton/hora ("Datos insuficientes") | Con N pequeño el P25–P75 no representa la máquina; el N mínimo de FASE3 fue 30 (EST-01) y aquí se acepta 15 por ser una pantalla referencial | `_N_MIN_TONH` | Sí |
| PRO-07 | Con largo pedido, el historial de la máquina se agrupa por kg/barra: 5 grupos si hay 50 o más datos, 3 si hay 30 o más, y sin agrupar si hay menos ("Sin ajuste por largo") | Deja al menos ~10 observaciones por grupo para calcular P25–P75. Se elige el grupo que contiene el peso pedido, o el de mediana más cercana | `_BINS_5_MIN_N`, `_BINS_3_MIN_N` | Sí |
| PRO-08 | "Fuera de rango" cuando el kg/barra pedido queda bajo P5 × 0,9 o sobre P95 × 1,1 del historial de esa máquina (P5/P95 sobre todos sus intervalos) | P5–P95 = rango observado real de la máquina (ej. EURA 20_3 Ø16: 2,5–19,1 kg/barra). El margen de 10 % se agregó porque 12 m en Ø16 (19,0 kg), el largo comercial más común, caía en el borde (EURA 20_1: marcado fuera de rango por 0,06 kg). Con margen: 12 m queda "ok", 14 m y 30 m "fuera de rango" | `_RANGO_PCT_INF/SUP`, `_RANGO_MARGEN`; harness del 23-09 | Sí |
| PRO-09 | La máquina es "no evaluable" para largo si el P90 de (kg/barra medido ÷ kg/barra teórico) supera 1,5 o tiene menos de 15 datos con ratio; en ese caso se usa el historial completo | En líneas de corte `NroPiezas` no representa barras. En máquinas normales el ratio está entre 0,98 y 1,05; en combinaciones que incluyen líneas de corte, el P90 de toda la combinación sube a 79–325. Resultado real: Línea de Corte, FP-LC, Cortadora 2, Línea Corte Coronel y Cortadora Manual salen "no evaluable" en los casos probados | `_RATIO_BARRA_MAX` | Sí |
| PRO-10 | Los "escenarios con ayudantes" (solo / +1 / +2) y las columnas Mín/Mediana/Máx se eliminan | Los ratios (1,0 / 0,75 / 0,55) eran fijos y sin respaldo; la dotación no es detectable en el historial (ratio 1:1). Mín/Máx daban valores sin sentido (mín ≈ 2, máx ≈ 440–478 min) por el filtro laxo | diff `B26_A_diff_20260923.patch` | Sí |
| PRO-11 | Las máquinas listadas son las que históricamente procesaron esa forma y diámetro; no son el ruteo del Planificador | Evitar que el usuario tome la lista como decisión de asignación | `NOTA_RUTAS` | Sí |
| PRO-12 | Textos: título interno "Tiempos por Máquina (estimado)"; menú "Producción por Máquina"; subtítulo de la tabla "Producción por máquina — Forma X · Ø Y mm" (unificado con el menú) | Consistencia con el nombre del menú (decisión de Montu 23-09) | `TiemposPorMaquina.tsx` | Sí |
| PRO-13 | El método de tiempo de esta pantalla es el delta crudo entre registros consecutivos; NO es el método validado FASE3 | Se entrega A el jueves con copy honesto; el método validado requiere definir fuente de datos y llevar los scripts al repo | `B26_B_pendiente_metodo_validado.md`; estado `PENDIENTE` (B26-B) | Sí |

---

## 2. Estadística y análisis de tiempos (FASE3) — `EST-`
Origen: análisis exploratorios del Motor de Tiempos (13–21 sep 2026), documentados en `FASE3_*.md`. Son la base del "método validado" que B26-B debe llevar a producción. Fechas: las de cada documento. Aprobación: reglas de negocio dictadas por Montu donde el documento lo indica.

| ID | Regla | Por qué | Fuente | Manual |
|---|---|---|---|---|
| EST-01 | Una máquina o combinación solo se evalúa si tiene al menos 30 datos (n ≥ 30) | Umbral de volumen mantenido en todas las fases FASE3 | `FASE3_ESTADISTICA_APLICADA` (línea 19), `FASE3_SEGMENTACION_FORMA` (línea 43), `FASE3_OPERARIO_TURNO` (línea 70) | No |
| EST-02 | Se excluyen los registros de trabajos multi-máquina / pool | Mantenido igual entre fases (motivo detallado en el documento) | `FASE3_ESTADISTICA_APLICADA` línea 19 | No |
| EST-03 | Limpieza de deltas: se excluyen los ≤ 0 y los muy largos (> 720 h) | Ver detalle y motivo en el documento | `FASE3_CENSURADA_20260913.md` línea 29 | No |
| EST-04 | Se excluyen saltos de turno o día (> 15 h) y se descuenta el break real: 13–14 h en turno Día y 01–02 h en turno Noche. Delta neto = bruto − break, con piso en 0 | Regla de Montu, aplicada tal cual; 13.756 pares (7,82 %) tocaron una ventana de break | `FASE3_OPERARIO_TURNO_20260914.md` líneas 56–62 y 81–82; `FASE3_TONELADAS_HORA_20260914.md` línea 6 | Sí |
| EST-05 | El tiempo se mide por Trabajo + Operario + Máquina (operario + máquina + pedido, con colapso de rachas por `pedido_it`) | Con el delta por operario, 24 de 33 máquinas dejan de rechazar unimodalidad (antes 26 de 32 la rechazaban) | `FASE3_OPERARIO_TURNO` líneas 159–160; `FASE3_OPERARIO_PEDIDO_FINAL_20260914.md` | Sí (resumen) |
| EST-06 | No se reportan medias ± desviación ni intervalos de confianza paramétricos; se usan mediana y rango empírico (P25–P75) | En las 32 máquinas evaluables ninguna familia simple de distribución pasó el ajuste (p > 0,05) y hay bimodalidad real | `FASE3_ESTADISTICA_APLICADA_20260913.md` líneas 59–112 y 171 | Sí |
| EST-07 | La unidad de negocio es toneladas por hora, no minutos por pedido | "El negocio se mide en toneladas" | `FASE3_TONELADAS_HORA_20260914.md` línea 10 | Sí |
| EST-08 | Se descartan intervalos con `ton_hora > 50` | Outliers de duración cercana a 0 | `FASE3_PESO_POR_PIEZA_20260921.md` línea 21 | No |
| EST-09 | La relación entre peso por pieza y ton/hora es monotónica, no lineal; por eso se agrupa por rangos de peso y no se usa una fórmula fija | Spearman significativo con Pearson bajo | `FASE3_PESO_POR_PIEZA_20260921.md` líneas 26–48 | Sí (resumen) |

---

## 3. Asignación de trabajos (Motor) — `ASG-`
Código: `backend/motor_v2.py` (constantes y `ConocimientoMotor`) y `backend/routers/programacion.py`. Diseño de origen: `spec_motor_asignacion_optisteel.md` (dictado de Montu, 12-09-2026). Estado: `VIGENTE` salvo donde se indique.

| ID | Regla | Por qué / quién | Fuente / código | Manual |
|---|---|---|---|---|
| ASG-01 | El SPP no decide QUÉ se produce (lo dicta OptiSteel/Cubigest); su valor es encontrar la combinación trabajo → máquina que maximiza la producción total del día | Premisa reconfirmada por Montu, 12-09 | `spec_motor_asignacion_optisteel.md` | Sí |
| ASG-02 | Hay dos corridas por día: turno Día (minutos después del inicio, tras el chequeo de asistencia, con los operadores presentes) y turno Noche (primero lee cómo quedó el día real, calcula el saldo y lo reparte entre los operadores de noche) | Diseño acordado con Montu, 12-09 | spec, "Modelo de dos corridas por día" | Sí |
| ASG-03 | Reglas por corrida: solo operadores presentes en esa jornada; competencia operador–máquina; un operador en una máquina a la vez (puede cambiarse de máquina después, incluso para continuar el mismo trabajo); la forma (`IdForma`) define qué máquinas están habilitadas; materias primas quedan fuera de esta etapa | Montu, 12-09 ("puede que se me escape una condición": no cerrado al 100 %) | spec, "Reglas del optimizador" | Sí |
| ASG-04 | Horario de turno: prioridad 1 = hora real de Geovictoria (con ±15 min ya aplicados); prioridad 2 = jornada configurada en SQLite por sucursal; prioridad 3 = valores por defecto (Día 08:15–17:45, viernes hasta 16:45; Noche 20:15–05:45, viernes hasta 04:45; break 13:00–14:00 Día y 01:00–02:00 Noche) | Regla "+15 min inicio / −15 min fin de jornada" (B35); el turno resuelto viaja del backend al Gantt como única fuente de verdad (commit `0522109`, 23-09) | `_get_config_turno` en `motor_v2.py` | Sí |
| ASG-05 | Cambiar de diámetro en una misma máquina penaliza 15 minutos | Motivo no documentado en el código | `SETUP_CAMBIO_DIAMETRO_MIN` | Sí |
| ASG-06 | (Reemplazada por ASG-11) FP-LC ya no es una maquina del SPP; antes se trataba como "sin operador" | Motivo original no documentado; superada por la decision B45 de 23-09 | `MAQUINAS_SIN_OPERADOR` sigue en el codigo, sin efecto | No |
| ASG-07 | Solo se asigna a las máquinas activas por sucursal (Cerrillos, Calama, Coronel según lista del código) | Confirmadas por el Jefe de Planta el 2026-03-16 | `MAQUINAS_ACTIVAS` | Sí |
| ASG-08 | Acero delgado (AD) es diámetro ≤ 16 mm | Definición de negocio; motivo no documentado | `DIAMETRO_AD_MAX` | Sí |
| ASG-09 | Existe una máquina de solo corte por sucursal (Línea de Corte / Carro de Corte / Línea Corte Coronel): una pieza con avance Cubigest > 0 % no vuelve a asignarse a ella | Evitar reasignar cortes ya hechos | `MAQUINAS_SOLO_CORTE` | Sí |
| ASG-10 | Dobladora por defecto por sucursal (Cerrillos: Tecmor S40 1; Calama: Dobladoras; Coronel: Dobladora 2) como punto de partida cuando la ruta no se resuelve por avance | Confirmado contra Cubigest (`MAQ_ACTIVA='S'`) el 2026-09-22 | `DOBLADORA_DEFAULT` | No |
| ASG-11 | FP-LC (Fierro en Punta - Largo Comercial, 6.000 a 12.000 mm) es una maquina FICTICIA: va de Bodega al camion y NO se considera en el SPP: sus etiquetas no entran al Motor ni a la Bolsa, no figura como maquina, ni en el Gantt/Gestor de Maquinas, y no se puede reasignar manualmente | Gustavo (TO) via Montu, 23-09. Volumen ~0,4-0,9 % | `motor_v2.py` (`es_despacho_directo`, `MAQUINAS_FICTICIAS`), `programacion.py` (`_obtener_pids_pendientes`, JOIN OptiSteel), commit `4325640` — `VIGENTE` | Si |
| ASG-12 | Restricciones por máquina (Cerrillos): PRIMA 3D cota A máx. 2.000 mm; Robomaster 55 y 60 pata máx. 2.500 mm; Curvadora CER40 solo anillos y espirales; EURA 20_1 sin anillos; Robomaster 55 solo dobleces a 90° | Excel "Restricciones de máquinas" (según comentario del código) | `RESTRICCIONES_LARGO`, `RESTRICCIONES_FUNCIONALES` | Sí |
| ASG-13 | Cerrillos tiene id 10 en el SPP (SQLite) y 4 en Cubigest; el SPP traduce entre ambos | Regla técnica FP-006 | `SUCURSALES` en `motor_v2.py`, `_ALL_CUBIGEST` | No |
| ASG-14 | La Bolsa de Trabajo usa solo el cuadro OptiSteel para días futuros | B18, cerrado y desplegado 15-09, refinado 22-09 (commit `fd9e256`) | `pendientes_sistema_planificador.md` fila B18 | Sí |

---

## 3b. Gantt: qué es una cajita y cómo se ve (B42 v2) — `GAN-`
Spec: `agentes/B42_v2_spec.md`. Decisiones de **Montu, 24-09-2026** (con foto de etiqueta física de Calama, Francisco Ramos, y captura del detalle de Cerrillos). Estado de toda la sección: `PENDIENTE` (decidido, no implementado). Reemplaza el criterio de B42 v1 (`1dda6e0`, etiqueta representante del grupo), que no calzaba con lo pedido.

**Nota 29-09-2026:** GAN-01, GAN-03, GAN-04 y GAN-09 quedaron reemplazadas por decisión de Gustavo — ver sección 3b-2. GAN-02, GAN-05, GAN-06, GAN-07 y GAN-08 siguen vigentes tal cual (son de otra capa, o no se vieron afectadas).

| ID | Regla | Por qué | Fuente / código | Fecha · quién | Manual |
|---|---|---|---|---|---|
| GAN-01 | Una cajita = una etiqueta (TAG) = un trabajo | Es la unidad que el operario ve y ejecuta; lo que importa es lo que se va a fabricar en ese trabajo, no el resto del viaje | Hoy: agrupación por (viaje, diámetro, etapa_avance) en `motor_v2.py` (espejo `4325640`, NO VERIFICADO en `master`) | 24-09 · Montu | Sí |
| GAN-02 | Etiquetas con igual (viaje, diámetro, forma, largo, calidad, etapa) forman una serie: van a una misma máquina, una tras otra | Regla operativa de planta. Reparto de la serie en 2 máquinas: manual (doble clic) mientras no exista la Fase 2 | Por implementar en `motor_v2.py` (clave de agrupación) | 24-09 · Montu | Sí |
| GAN-03 | Carátula: viaje, `Etiqueta N de M`, diámetro y peso de la etiqueta; el aviso ATRASO no cambia | El diámetro es lo que más pesa al mirar el Gantt; N de M dice qué etiqueta se ejecuta | `GestorProgramacion.tsx` (`DraggableTimelineEvent`) | 24-09 · Montu | Sí |
| GAN-04 | Detalle: header viaje, obra, etiqueta y calidad; cuerpo con diámetro, largo, ID_forma, cantidad, paquete y peso de la etiqueta; sin "marca" ni lista de otras etiquetas | Refleja la etiqueta física de planta; "Pieza" (figura) se reemplaza por ID_forma, el dato que usa el SPP | `GestorProgramacion.tsx` (modal de detalle) | 24-09 · Montu | Sí |
| GAN-05 | No cambian: doble clic (reparto), "Ajustar duración", aviso ATRASO, formato visual, drag&drop | Funciones ya validadas con los jefes de planta | B2, B44a, B33/B34 | 24-09 · Montu | No |
| GAN-06 | Fase 2: el Motor evalúa "sin repartir" vs "repartido" y elige el que da la máxima producción en el menor tiempo de la jornada | Definido por Montu; el criterio exacto de "mejor" está por definir | Post-entrega, spec propia | 24-09 · Montu | Por definir |
| GAN-07 | Duracion: la de la serie (misma formula de hoy) se reparte entre sus etiquetas proporcional a kg | Conserva los tiempos que calcula el Motor; `KgsPromedio_por_trabajo` ya esta en escala de etiqueta (42-636 kg) | `estimar_duracion_min` (`motor_v2.py:645-712`) | 24-09 · Montu | Si |
| GAN-08 | Calidad del acero en caratula/detalle: `mp.CalidadAcero` con default `A630` (NO `IT.TipoAcero`) | Decision de Montu; diferencia conocida con la etiqueta fisica (`A630-420H NORMAL (A)`). Mejora posterior: `IT.TipoAcero` | `programacion.py:1423,1541` | 24-09 · Montu | Si |
| GAN-09 | Cajita angosta: se prioriza Diametro, luego `N de M`, luego peso; el resto va al tooltip | ~570 cajitas por turno en Cerrillos (hoy 42) | `GestorProgramacion.tsx` (`DraggableTimelineEvent`) | 24-09 · Montu | Si |

## 3b-2. Gantt y Bolsa: cajita = viaje, agrupación de etiquetas — `GAN2-`
Reemplaza GAN-01, GAN-03, GAN-04 y GAN-09 de la sección 3b. Decisión de **Gustavo (TO), 29-09-2026** (vía Montu,
revierte lo pedido antes por José Auger). Estado: `VIGENTE`, desplegado en rama aislada `cajita-viaje-deploy`
(commit `19c2148`), gateado por fecha (GAN2-06). No toca el Motor (`motor_v2.py`) ni
`ejecutar_pipeline_generacion`/`generar_programacion` (la unificación auto/manual de CCa-24, que sigue en su
propia rama `unificar-generacion-auto-manual` sin desplegar). Informe técnico completo:
`agentes/CCa_cajita_viaje_20260929.md`.

| ID | Regla | Por qué | Fuente / código | Fecha · quién | Manual |
|---|---|---|---|---|---|
| GAN2-01 | Una cajita ya NO es una etiqueta: es una agrupación de etiquetas consecutivas del mismo viaje/IT y misma máquina, que comparten (en orden de prioridad) calidad de acero, diámetro, forma de pieza (`id_forma`) y largo | Gustavo pidió que la cajita vuelva a representar el viaje completo con sus etiquetas, no una etiqueta suelta | `backend/routers/programacion.py`, `_agrupar_cajitas_por_viaje` | 29-09 · Gustavo (vía Montu) | Sí |
| GAN2-02 | Si el grupo no alcanza los 4 criterios, se degrada: primero a 1+2+3 (calidad+diámetro+forma, largo distinto); si tampoco, a 1+2 (calidad+diámetro) y el detalle muestra "Forma n°: varios"; si no comparte ni calidad+diámetro, quedan cajitas separadas | Privilegiar la agrupación máxima posible sin mezclar piezas realmente distintas | ídem, `_nivel_criterio_comun` | 29-09 · Montu | Sí |
| GAN2-03 | La agrupación nunca cruza viaje/IT, aunque dos etiquetas de viajes distintos compartan todos los criterios | Se trabaja por IT (instrucción explícita) | ídem, clave de agrupación `(codigo_viaje, recurso_id)` | 29-09 · Montu | Sí |
| GAN2-04 | Carátula: usa el rango de etiquetas ("45-67 de 139", o "45-47,51,67 de 139" si no es correlativo) en vez de "Etiqueta N de M" cuando la cajita es un grupo | Reemplaza GAN-03 | `GestorProgramacion.tsx`, `rango_etiquetas` | 29-09 · Montu | Sí |
| GAN2-05 | Detalle (1 click): header "Etiquetas: {rango}"; se agrega Diámetro, "Forma n°" (o "varios"), Cantidad de Etiquetas, Peso total, y **sí** aparece ahora la lista de etiquetas del grupo (tabla TAG/Forma/Largo/Cantidad/Peso, orden ascendente) — GAN-04 decía explícitamente lo contrario ("sin lista de otras etiquetas"); queda revertido | Reemplaza GAN-04 | `GestorProgramacion.tsx`, modal de detalle | 29-09 · Montu | Sí |
| GAN2-06 | No retroactivo: el gate `CAJITA_VIAJE_VIGENTE_DESDE` (env, hoy `2026-09-29`) decide si una fecha usa el formato agrupado o el legado (una cajita = una etiqueta). Aplica igual al Gantt y a la Bolsa de Trabajo (en la Bolsa, sin `recurso_id` en la clave — todavía no hay máquina asignada — y el corte se evalúa por `fecha_despacho` del IT completo, no por pieza) | Montu no quiso perder trazabilidad de lo ya generado con el formato viejo | ídem, constante + `_obtener_pendientes_bolsa_optisteel` | 29-09 · Montu | Sí |
| GAN2-07 | Ajuste manual de duración ("Ajustar duración del trabajo") pasa a aplicarse sobre el total del grupo, no sobre una etiqueta suelta; usa el `id_tarea` de la primera etiqueta del grupo como clave, sin cambiar el esquema de la tabla `ajustes_duracion` | Confirmado por Montu ("(a)") | ídem, `_aplicar_ajustes_duracion` corre después de agrupar | 29-09 · Montu | Sí |
| GAN2-08 | El badge de la Bolsa de Trabajo pasó de "N ITs" a "N cajitas", porque desde este cambio un IT puede producir más de una cajita si sus etiquetas no comparten todos los criterios | Precisión del label tras GAN2-01 | `GestorProgramacion.tsx`, `DroppableBacklog` | 29-09 · Miaude (menor, autorizada por Montu) | Sí |

**Punto abierto — verificar contra código antes de escribir el Manual Técnico:** `MANUAL_TECNICO_SPP.md`
(líneas ~515-519) describe una alerta de "serie ≥80% del turno" que exige reparto manual de varias cajitas
sueltas hacia dos máquinas (GAN-02/GAN-06, capa del Motor, no tocada por este cambio). Con GAN2-01 vigente,
buena parte de esas series pueden llegar YA agrupadas en una sola cajita — falta confirmar si esa alerta y el
flujo de reparto manual siguen aplicando igual (ahora sería "partir una cajita-grupo en dos", no "juntar varias
sueltas") o si cambia su redacción.

## 3c. Universo de compromisos: reglas de fecha (atrasada, próxima, "muy futura") — `UNI-`
Spec: `agentes/UNIVERSO_FECHAS_spec.md`. Decisiones de **Montu, 24-09-2026** (ventana V6, con Mi TI).
Estado de toda la sección: `VIGENTE` (implementado y desplegado en producción 26-09 — módulo `universo_fechas.py`,
verificado en vivo contra `/api/calendario-futuro` y `/api/compromisos-semanales`; ver LOG_CAMBIOS_2026.md y
`pendientes_sistema_planificador.md` B48). Reemplazó la ventana fija `-30d/+21d` duplicada en
`database_cubigest.py:374`, `materias_primas.py:239` y `programacion.py:1476`.

| ID | Regla | Por qué | Fuente / código | Fecha · quién | Manual |
|---|---|---|---|---|---|
| UNI-01 | Atrasada válida = 1–30 d atrasada; > 30 d atrasada es "suciedad" y queda fuera de toda vista de demanda, con contador visible por planta | Vacío real de datos entre 8 y 30 d atrasados en las 3 plantas; > 30 d llega a fechas de 2013 | Datos reales 24-09, `agentes/UNIVERSO_FECHAS_spec.md` §2 | 24-09 · Montu | Sí |
| UNI-02 | Próxima = hoy..+21 d; Lejana normal = +22..+60 d | Continuidad con la ventana +21 d ya validada por Compromisos Futuros/Vista Semanal | ídem | 24-09 · Montu | Sí |
| UNI-03 | Muy futura = > +60 d, o (horizonte de reprogramación > 120 d y fecha > +21 d); no cuenta como demanda en Materia Prima | Fechas artificiales del cliente/TO no distinguibles por umbral simple (IT 1384 Cerrillos: +98 d, horizonte 381 d, 3,02M kg); Cubigest no tiene campo dedicado | ídem §2-3 | 24-09 · Montu | Sí |
| UNI-04 | Leyenda en UI de toda sección de demanda: "No considera ITs con fecha de despacho mayor a 60 días (N ITs / X kg fuera; ver aparte)" | Para que Gerencia/jefe de planta entienda por qué una IT no aparece | `agentes/UNIVERSO_FECHAS_spec.md` §3 | 24-09 · Montu | Sí |
| UNI-05 | Configuración única: una sola función/constantes de clasificación de fecha, reemplaza las 3 ventanas duplicadas | Evita que alguien cambie un límite y no el otro (riesgo ya detectado por CCa-11) | módulo nuevo propuesto en la spec | 24-09 · Montu | No |

## 4. Lo que hoy NO usa el SPP para decidir (para no confundir en capacitación)
- La pantalla "Producción por Máquina" **no alimenta al Motor**: es referencial (PRO-11).
- El Motor **no usa todavía** ton/hora validado (FASE3): B26-B, y después B44 (ajuste manual de tiempos que calibra el Motor) y B16 (minutos-hombre por jornada).
- Materias primas: fuera de la etapa actual (ASG-03).

## 5. Por mapear (aún sin entradas; se llenan leyendo el código, sin suponer)
1. Cómo el Motor elige entre rutas posibles (función objetivo, empates, penalizaciones distintas al setup de 15 min): `generar_programacion` en `motor_v2.py`.
2. Reglas de reparto de etiquetas entre 2 o más máquinas (B2, B15, B17, B30–B32: cerrado en la práctica).
3. Ajuste de ruta por avance (`ajustar_ruta_por_avance`) y qué pasa con piezas ya iniciadas.
4. Reprogramación manual desde el Gantt (`reprogramar_pid`, `_tarea_a_evento`) y qué campos viajan desde la Bolsa (fix del 22-09).
5. Reglas de asistencia y competencias de operadores (Geovictoria y competencias).
6. Indicador de órdenes adelantadas desde días futuros (B43) y fusión con la Bolsa (B18/B34).
7. Calibración por retroalimentación (B44) y minutos-hombre (B16), cuando existan.
8. Tratamiento de la censura de jornada y de la población posterior a 42 h / turnos dinámicos: recomendación de `FASE3_CENSURADA_20260913.md` (líneas 115–156): tratar el régimen posterior al 01-03-2026 (42 h / turnos dinámicos, `confianza_reducida`, 19,25 % de los deltas) como población separada al calibrar el Motor. **DECIDIDO por Montu, 23-09: se adopta** (aplica a B26-B y B44; estado PENDIENTE de implementación); no tiene relación con extraer horarios de Geovictoria.

## 6. Cómo se mantiene este mapa (propuesta a la Coordinadora)
1. Cada ventana que cambie o cree un criterio del SPP agrega o actualiza su fila (ID estable, valor, por qué, fuente, fecha y quién aprobó) **en el mismo turno** en que registra el LOG.
2. Los valores numéricos deben coincidir con las constantes del código; si difieren, gana el código y se corrige el mapa (o se abre una incidencia).
3. Antes de un manual o capacitación: filtrar la columna "Manual = Sí" y contrastar con el estado (`VIGENTE` no se documenta como vigente hasta el deploy verificado).
4. Regla de trazabilidad: ninguna fila sin fuente verificable. Si el motivo no está documentado, se anota así y se pregunta a Montu.

## 7. Historial de este documento
- 2026-09-26: sección 3c actualizada de `PENDIENTE` a `VIGENTE` — UNI-01..05 implementadas y desplegadas (deploy de las 5 ramas, commit final `52568d1` en `master`), verificado en producción contra el backend real (confirmado por Montu).
- 2026-09-24: sección 3c creada (`UNI-01`..`UNI-05`, ventana V6, PENDIENTE de implementación) tras spec cerrada en `agentes/UNIVERSO_FECHAS_spec.md`.
- 2026-09-23 noche: B26-A desplegado y verificado en produccion (commit `a6c94ea`): las filas PRO-01..PRO-13 pasan de VIGENTE-PRE-DEPLOY a VIGENTE. FP-LC fuera del SPP (ASG-11, `4325640`).
- 2026-09-23: creación. Sección 1 completa (B26 versión A, incluye margen de tolerancia del 10 % y subtítulo unificado, ambos aprobados por Montu). Secciones 2 y 3 sembradas desde `FASE3_*.md`, `motor_v2.py` y `spec_motor_asignacion_optisteel.md`. Faltan las secciones de la lista 5.
