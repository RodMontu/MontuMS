# Capturas pendientes — Manual de Usuario SPP v2.1

Lista para tomar el martes 29-09-2026 durante turno real (fecha en que ya rige `CAJITA_VIAJE_VIGENTE_DESDE` y
por lo tanto la cajita se ve como grupo de etiquetas, no como etiqueta suelta), con datos reales (no se inventó
ningún ejemplo numérico en el manual; estas capturas deben reemplazar los marcadores `[CAPTURA n]`).

1. **Pantalla Programación, vista general del Gantt** — turno Día, con al menos una cajita de cada tipo visible
   (normal, gris con candado, con ribete rojo de atraso si existe). Buscar, si es posible, al menos una cajita
   cuya carátula muestre un rango de etiquetas no correlativo (formato "45-47,51,67 de 139") además de una
   correlativa ("45-67 de 139"), para que se vea la diferencia de formato. Resaltar: encabezado completo
   (sucursal, turno, fecha, botones e indicadores Universo/Cuadro).
2. **Botón Sincronizar recién presionado** — capturar el estado "sincronizando" (ícono girando) y luego el
   resultado con los badges "Universo hace X min" / "Cuadro hace X min" en verde.
3. **Mismo indicador en estado ámbar (desactualizado)** — requiere esperar a que pase el tiempo suficiente sin
   sincronizar, o capturarlo si ocurre naturalmente durante el turno.
4. **Cajita-grupo gris con candado** — zoom sobre una cajita-grupo en ese estado, mostrando el ícono de candado
   y el color distinto al verde de "completado". Si se puede identificar un caso donde el candado gris aplique
   a un grupo con más de una etiqueta (rango, no un número suelto), preferirlo — sirve para documentar en qué
   caso real se ve el candado sobre el grupo completo. Idealmente junto a una cajita verde para contraste.
5. **Intento de mover una cajita-grupo sobre una cajita gris (candado)** — capturar el mensaje de rechazo
   ("No se puede soltar sobre una cajita ya ejecutada...").
6. **Intento de mover una cajita a una máquina con avería** — capturar el mensaje "⚠️ ERROR: Máquina fuera de
   servicio por avería."
7. **Modal de detalle de una cajita-grupo** (clic simple) — a diferencia de la versión anterior de esta lista,
   ahora debe mostrar explícitamente: el encabezado "Etiquetas: {rango}" (no "Etiqueta: N de M"), y en el cuerpo
   Diámetro, "Forma n°" (o "varios" si aplica), Cantidad de Etiquetas, Peso total, y la **tabla de etiquetas del
   grupo** (columnas TAG/Forma/Largo/Cantidad/Peso, orden ascendente por TAG). Preferir un grupo con 3+ etiquetas
   para que la tabla se note bien en la captura.
   **Nueva — degradación "Forma n°: varios":** si se identifica en planta un grupo real que haya degradado por
   no compartir forma de pieza (mismo viaje+máquina+calidad+diámetro, pero con más de un ID de forma — nivel de
   criterio 2 en `_nivel_criterio_comun`), agregar una captura específica de su modal de detalle mostrando
   "Forma n°: varios". No se identificó un caso así durante esta revisión (no se consultó Cubigest en vivo para
   buscarlo); anotar como pendiente de conseguir cuando aparezca uno en producción.
8. **Zoom y desplazamiento del Gantt** — dos capturas: una con zoom normal, otra con zoom acercado mostrando el
   detalle de una cajita-grupo angosta (con varias etiquetas agrupadas).
9. **Bolsa de Trabajo** — con al menos 2-3 tarjetas (cajitas) pendientes visibles, y el momento de arrastrar una
   hacia el Gantt. Si es posible, incluir un caso donde un mismo IT aparezca con más de una tarjeta (porque sus
   etiquetas no comparten todos los criterios de agrupación entre sí), para ilustrar el cambio de "N ITs" a
   "N cajitas" en el badge.
10. **Botón Compromisos Futuros activado** — pantalla cambiada a la vista de compromisos, con el botón mostrando
    "Ver Planificador".
11. **Pantalla Averías — vista general** — contadores de operativas/semi-operativas/detenidas, y la falla más
    recurrente.
12. **Formulario "Reportar Falla"** — modal abierto, con una máquina seleccionada y el síntoma en el campo de
    texto (usar un síntoma de ejemplo genérico, no un caso real confidencial si no corresponde).
13. **Avería con fuente "Cubigest"** — si existe una avería activa proveniente de Cubigest (no manual) en el
    momento de la captura, mostrar su distinción visual respecto de una avería manual.
14. **Confirmación "Levantar avería"** — el modal de confirmación con el texto "¿Levantar avería de [máquina]?".
15. **Vista Semanal** — matriz completa de la semana, con la fila de "Atrasado ≤30 días" y "Sin fecha confirmada
    / muy futura" visibles, incluyendo la leyenda de ITs excluidas.
16. **Próximas Semanas (Calendario Futuro)** — vista con al menos 2-3 semanas de ITs agrupadas, mostrando la
    leyenda "No considera ITs con fecha de despacho mayor a 60 días...".
17. **Producción por Máquina** — una consulta real con forma/diámetro que produzca un resultado con mediana y
    rango P25-P75, y otra que muestre alguno de los avisos ("Datos insuficientes", "Fuera de rango histórico",
    "Rango no evaluable" o "Sin ajuste por largo").
18. **Gestor de Máquinas** — matriz de hebras de una máquina real (para reemplazar/confirmar el ejemplo de
    Coronel Dobladora 2 ya verificado en este manual), y la lista de restricciones físicas de Cerrillos.
19. **Botón Reprogramar en curso** — estado "Generando..." del botón.
20. **Botón Deshacer visible** — justo después de un movimiento manual, antes de que se pierda esa opción.
21. **(Opcional, si ocurre naturalmente el lunes) corrida automática de las 08:10** — captura de los logs del
    contenedor (`docker logs optifierro-backend --tail 25`) mostrando el mensaje
    "Scheduler: [sucursal] dia [fecha] → X/Y etiquetas", para ilustrar la sección 6 del manual sin necesidad de
    exponer datos sensibles en la interfaz.

**Nota para quien tome las capturas:** evitar que aparezcan nombres reales de operadores o RUT en cualquier
captura, según la regla de privacidad de este proyecto. Si una captura los muestra, recortar o difuminar esa
zona antes de insertarla en el manual.
