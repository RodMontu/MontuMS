# Guía Rápida — SPP (el Planificador)
**Para jefes de planta · 28-09-2026 · imprimir y tener a mano**

## ¿Qué hace el Planificador?
Reparte los trabajos ya liberados por Cubigest/OptiSteel entre las máquinas y operadores presentes, buscando la
mayor producción posible del turno. **No decide qué se fabrica ni cuándo se despacha** — eso lo define Cubigest.

## El día en 4 momentos
| Hora | Qué pasa solo, sin que usted haga nada |
|---|---|
| 08:08 | Se lee la asistencia real desde GeoVictoria |
| **08:10** | El Motor genera la programación del turno Día (Calama, Cerrillos, Coronel) |
| 20:08 | Se lee la asistencia del turno Noche |
| **20:10** | El Motor genera la programación del turno Noche, con el saldo pendiente del día |

Estas dos corridas automáticas **no corren** sábado, domingo ni feriado de Chile. Si el Gantt aparece vacío en
esos días, es normal.

## ⚠️ Lo más importante que debe saber
**Haga sus ajustes DESPUÉS de que corra la generación automática de su turno** (08:10 el turno Día, 20:10 el
turno Noche). Cada corrida automática arma de nuevo el plan de su turno y **reemplaza** lo que se haya movido
a mano antes en ese mismo turno (por ejemplo, un movimiento hecho a las 07:45 se pierde a las 08:10). Lo que usted
mueve **después** de la corrida queda guardado y se conserva, incluso cuando más tarde corre la del otro turno.
El botón **"Reprogramar"** sí vuelve a aplicar sus movimientos y asignaciones manuales guardados.

## Botones de la pantalla Programación
- **Sincronizar:** trae los datos más recientes de Universo y Cuadro OptiSteel. Los badges "hace X min" al
  lado le dicen qué tan viejo está cada dato (verde = al día, ámbar = atrasado).
- **Reprogramar:** vuelve a correr el Motor ahora mismo, con los datos actuales, y sí respeta sus movimientos
  manuales guardados.
- **Deshacer:** revierte su último movimiento manual.
- **Compromisos Futuros:** muestra los compromisos de fechas futuras en vez del Gantt de hoy.

## Cajitas: qué significa cada cosa
Desde el 29-09, la cajita ya no es una etiqueta suelta: agrupa las etiquetas de un mismo viaje que se fabrican
juntas, una tras otra, en la misma máquina.
- **Gris con candado:** esa etapa YA se ejecutó de verdad (confirmado en Cubigest). No se puede mover, nunca.
- **Verde:** trabajo completado (viaje/IT cerrado).
- **Ribete rojo:** fecha atrasada. **Ribete naranja:** fecha por vencer, o máquina con avería.
  Sin urgencia de fecha: **ribete verde** = acero soldable (calidad terminada en S, ej. A630S); **gris** = no soldable.
- **Borde punteado ámbar:** acero que no es la calidad estándar A630.

## Ante una avería
1. Vaya a **Averías** → **"Reportar Falla"** → elija la máquina → describa el síntoma.
2. Vuelva a **Programación** y arrastre las cajitas afectadas a otra máquina compatible.
3. Cuando se resuelva, en Averías use **"Levantar avería"** para volver la máquina a operativa.
El sistema también revisa Cubigest cada 30 minutos por si la avería fue reportada directamente ahí.

## Si algo no calza
- **¿Un trabajo no se asignó?** Revise: operador presente, diámetro/forma compatible con la máquina, máquina no
  averiada.
- **¿Una IT no aparece en Vista Semanal / Próximas Semanas?** Puede estar a más de 60 días de despacho, o
  "atrasada" hace más de 30 días — el sistema la excluye de la demanda a propósito.
- **¿Cubigest no responde?** El sistema reintenta solo; los datos de averías/sincronización pueden quedar
  desactualizados un rato, no es una falla del Planificador.

Para el detalle completo de cada pantalla, ver `MANUAL_USUARIO_SPP.md`.
