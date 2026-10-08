# Spec — Lógica de asignación óptima del motor (post-OptiSteel)
**Contexto cerrado con Montu, 12-09-2026 (dictado). NO empezar a implementar
hasta que la captura de datos (B1, fuente OptiSteel/Cubigest) esté afinada
primero — orden explícito de Montu.**

## Premisa (reconfirma el mensaje anterior)
OF no decide QUÉ se produce — eso lo dicta OptiSteel/Cubigest, hasta Etapa 2.
El valor de OF es encontrar la combinación trabajo→máquina que maximiza la
producción total del día.

## Modelo de dos corridas por día
La programación de OptiSteel llega **por día completo** (00:00-23:59:59),
pero ese total se reparte en DOS corridas separadas del motor, una por
turno:

1. **Corrida turno día** (~unos minutos después del inicio de jornada día,
   ej. 08:06-08:12, tras el chequeo de asistencia): usa SOLO los operadores
   presentes en ese momento (ej. 3 de 6 — los otros 3 están en turno noche).
   Asigna lo que puede a las máquinas que esos operadores saben operar.
   Lo que no alcanza a completar queda como saldo pendiente.

2. **Corrida turno noche** (~unos minutos después del inicio de jornada
   noche, ej. 20:00+): PRIMERO lee la base de datos para saber cómo quedó
   el turno día real (qué se cerró total o parcialmente), calcula el saldo
   restante del día completo, y reparte ESE saldo entre los operadores de
   turno noche y sus máquinas habilitadas. Aplica las mismas reglas, pero
   sobre el trabajo remanente, no sobre el total original.

## Reglas del optimizador (por corrida)
- Operadores presentes en ESA jornada específica (día o noche).
- Competencia operador-máquina (qué máquinas sabe operar cada uno).
- Un operador en una sola máquina a la vez — pero puede terminar y
  cambiarse de máquina, **incluso para continuar el mismo trabajo** en otra
  máquina (secuencial en el tiempo — distinto del reparto en paralelo de
  B2, que es simultáneo entre 2+ máquinas).
- IdForma de la pieza → qué máquinas están habilitadas para esa forma.
- **Explícitamente fuera de esta etapa**: disponibilidad de materias primas
  (mencionado por Montu, decidido dejar para Fase 2 de OptiFierro).
- Posible condición faltante, palabras de Montu: "puede que se me escape
  una condición" — no cerrado al 100%, revisar de nuevo antes de
  implementar.

## Complejidad reconocida
No es asignación greedy/secuencial — es una combinatoria real (todas las
rutas posibles trabajo↔máquina, elegir la de mayor producción). Montu lo
reconoce explícitamente como no trivial.

## Pendiente secundario, no prioritario ahora
Cuánto tiempo (minutos) toma correr el algoritmo — determina a qué hora
exacta después del chequeo de asistencia se puede lanzar la corrida. No
bloquea el diseño, se resuelve después.

## Orden de trabajo confirmado
1. Captura de datos de OptiSteel/Cubigest (B1) — EN CURSO (ver
   pendientes_sistema_planificador.md B1, y diagnóstico SSL en curso).
2. Recién después: diseño e implementación de esta lógica de asignación.
