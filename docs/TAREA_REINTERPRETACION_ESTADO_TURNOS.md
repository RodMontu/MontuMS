# TAREA — Reinterpretación del campo `estado` en `turnos_programados`
**Fecha:** 2026-09-06 (Domingo)
**Origen:** dictado de Montu vía Visual-Voice, respondiendo a MT-01b/MT-01c
**Para:** una ventana de chat dedicada, futura — este documento es el punto de partida
**Estado:** problema identificado y con evidencia real, sin resolver — no bloquea Fase 1

---

## 1. El problema, en una frase

`turnos_programados.estado = 'FALTA'` no significa necesariamente "el operador no
fue a trabajar". Puede significar simplemente que, al momento de la lectura, el
operador **todavía no había iniciado su turno** — y el sistema no distingue entre
ambos casos.

## 2. El caso que motivó esto (ejemplo de Montu)

Lectura de Geovictoria un lunes a las 08:06. De 12 operadores, 6 figuran "presentes"
y 6 "faltan". Al revisar el horario de ingreso de esos 6 que "faltan", su turno
empieza a las 20:00. **El operador no ha faltado — todavía no le toca entrar.**

**Regla propuesta por Montu (no implementada, a diseñar en la ventana dedicada):**
cualquier turno que comience desde ~18:00 en adelante debería reclasificarse como
`TURNO_NOCHE`, no arrastrar el valor crudo `FALTA` de Geovictoria sin reinterpretar.

## 3. Evidencia real encontrada hoy (2026-09-06) — más amplia de lo esperado

Se revisó `turnos_programados` para la última carga disponible (`fecha = 2026-08-31`,
un lunes real — corresponde con el ejemplo de Montu). Datos:

- Distribución `estado` en esa carga: Calama 21 `FALTA`, Cerrillos 40 `FALTA`,
  Coronel 10 `FALTA` (sobre el total de filas de sucursal ese día).
- **De los 21 `FALTA` de Calama, 20 tienen `hora_inicio_turno = '08:00'`** — turno
  de **día**, no de noche.
- El campo `extraido_en` para esa carga es `2026-08-31 11:00:00` — es decir, la
  lectura se hizo **3 horas después** de que el turno de 08:00 ya debería estar en
  curso.

**Esto no calza con la hipótesis de "turno de noche todavía no iniciado".** A las
11:00, alguien con turno 08:00–17:00 ya lleva 3 horas trabajando si asistió. Dos
lecturas posibles, ninguna descartada:

1. Son ausencias reales (mal indicador de eficiencia de asistencia, no de dato).
2. Hay un problema de **latencia de sincronización** de Geovictoria — el check-in
   real ocurre pero tarda en reflejarse, y el corte de extracción a las 11:00 lo
   toma "en tránsito" como si no hubiese llegado.

**Conclusión:** el problema de `FALTA` mal etiquetado es más amplio que solo el
caso de turno de noche. Hay que investigar ambas causas (mala interpretación por
horario Y posible latencia de sincronización) antes de construir la regla de
reclasificación.

## 4. Hallazgo adicional — limitación de alcance de la tabla (no es un sync roto)

`turnos_programados` **no es un calendario continuo**. Las fechas de carga
(`extraido_en`) son, con pocas excepciones, **semanales, siempre los lunes,
siempre ~11:00**:

```
2026-08-31, 2026-08-24, 2026-08-10, 2026-08-03, 2026-07-27, 2026-07-20,
2026-07-13, 2026-07-06, 2026-06-22, 2026-06-15, 2026-06-08, 2026-06-01, ...
```
(con un par de saltos de 14 días en vez de 7 — cargas semanales que también
fallaron, no solo la de esta semana).

**Implicancia para el plan del Motor de Tiempos:** esta tabla, tal como está, **no
puede servir como el calendario continuo que necesita `CENSURA_JORNADA`** (que
requiere saber el horario de turno para *cada* día en que las máquinas produjeron,
no solo los lunes de cada semana). Es más bien una foto semanal, probablemente
pensada para un dashboard de dotación de los lunes, no para trazabilidad diaria.

**MT-01 se reclasifica:** la tabla y sus columnas quedan ubicadas (eso sigue
cerrado), pero **el uso que el plan necesita de ella NO está resuelto** —
downgrade de "CERRADA" a "ubicada, con limitación de alcance sin resolver".

## 5. Cabo suelto sin cerrar — discrepancia de fecha

Montu reporta que la UI de OptiFierro dice que la última carga de turnos fue el
**1 de septiembre**. La tabla cruda muestra la última carga el **31 de agosto,
11:00**. No se investigó la UI directamente en esta sesión (solo la base). Posibles
explicaciones sin verificar: la UI muestra fecha de "próxima carga programada" en
vez de "última carga real"; diferencia de huso horario en el render; la UI lee de
otra fuente distinta a `turnos_programados`. **Queda para la ventana dedicada.**

## 6. Qué necesita resolver la ventana dedicada

1. Confirmar si el corte de extracción (siempre lunes ~11:00) es un diseño
   deliberado o un cron mal configurado que debería correr a diario.
2. Diseñar la regla de reclasificación real: no basta con "turno ≥18:00 →
   TURNO_NOCHE" — hay que primero descartar o confirmar la hipótesis de latencia
   de sincronización con evidencia (ej. cruzar con otro sistema de asistencia si
   existe, o pedir a Roberto/TI de TO el detalle del pipeline Geovictoria→SQLite).
3. Decidir si vale la pena pedir a TO que cambien la cadencia/hora de extracción
   a algo que sirva para `CENSURA_JORNADA` (ej. carga diaria nocturna, después de
   cerrado el día), en vez de rediseñar todo en base a un dato que nunca fue
   pensado para este uso.
4. Confirmar directamente con Montu/TO qué significa `FALTA` en el sistema
   Geovictoria de origen (no asumir).

## 7. Puntero técnico para la ventana dedicada

- Acceso: SSH alias `TO` (Mac Studio) → `docker exec optifierro-backend python ...`
  contra `optifierro_v2.db` (SQLite local, NO Cubigest — sin restricciones de PTS
  v1.0, sin ventana horaria).
- Tabla: `turnos_programados` — columnas en `handoff_actual.md` sección 5.
- Ver también `bitacora_accesos_torres_ocaranza.md`, entradas "MT-01" del
  2026-09-06, para el detalle completo de las consultas ya ejecutadas.
