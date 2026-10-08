# VENTANA V4 — B16: DISENO con Montu (SIN CODIGO) (Ola 1, prepara la Ola 2)
Antes de todo: lee `/Users/montu/MontuMS/docs/agentes/prompts/00_CONTEXTO_BASE_OLA1.md` (ignora lo de deploy/commit: aqui no hay codigo).

## Tu carril
**Punto:** B16 — calculo de minutos-hombre REALES disponibles por jornada. Montu: "practicamente lo mas importante que debemos trabajar". Nunca desarrollado; requiere DISENO desde cero con Montu presente.
**Entregable unico:** `/Users/montu/MontuMS/docs/agentes/B16_diseno_spec.md` — spec cerrada, lista para que CCa implemente en Ola 2 sin preguntar nada. Maximo ~1 hora de sesion con Montu. No escribas codigo del SPP.

## Insumos (lee solo lo necesario)
- `agentes/CCa2_motor_blast_20260923.md` seccion B16: hoy existe la ventana horaria +-15 min (3 niveles) y `_saltar_break` en el cursor de asignacion,
  pero `minutos_turno` (`motor_v2.py:772`) se calcula y no se usa; no hay agregado de capacidad. Colacion real: 13-14h turno dia, 01-02h turno noche.
- `pendientes_sistema_planificador.md`: filas B16, B35, B43 (B43 adelanta trabajo "hasta completar la capacidad de minutos-hombre de la jornada" -> B16 es su insumo).
- Fuente de presencia: GeoVictoria (`asistencia_colaboradores`, campo `cargo`; ausencia diaria ya excluye maquinas). Regla AR-009: un operador califica para 2+ maquinas pero trabaja en UNA a la vez.
- Hebras (V1) cambian la capacidad por maquina: B16 mide personas-tiempo, no throughput; no los mezcles.

## Como conducir la sesion
Propon un BORRADOR concreto primero (Montu corrige mas rapido de lo que construye desde cero) y luego preguntas atomicas, de a una o dos (`ask_user_input_v0` cuando sean opciones). Puntos a cerrar:
1. Definicion exacta: minutos-hombre = para cada planta/turno/dia, suma sobre personas presentes (operadores y ayudantes, segun GeoVictoria) de (ventana -15/+15 menos colacion). Confirmar formula y que se cuenta y que no (ayudantes? ausentes? medio turno?).
2. Granularidad: por planta+turno+dia; y desglose por maquina o por persona?
3. Formato de salida y DONDE se muestra (Programacion? cabecera del Gantt? Vista Semanal?). Bosqueja el texto/numero exacto.
4. Como se consume: capacidad total vs minutos-hombre ya asignados (Gantt) = saldo; como lo usara B43 para adelantar trabajo.
5. Casos borde: turno noche (cruza medianoche), sabado/domingo, feriados, ausencia parcial, operador asignado a 2 maquinas en el dia.
6. Criterios de aceptacion medibles (ej. Cerrillos, un dia real: X operadores presentes -> Y minutos; Montu valida contra su calculo manual) y a que archivos apunta la implementacion (`motor_v2.py`, `programacion.py`, frontend) para serializar bien en Ola 2 (despues de V1 y V2).
7. Que entra al jueves (minimo viable) y que queda para despues.

## Cierre
Al terminar: spec en el archivo, fila del tablero actualizada, RESUMEN de maximo 15 lineas (decisiones tomadas, criterios de aceptacion, archivos a tocar, minimo viable jueves).
