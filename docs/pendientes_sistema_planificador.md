# Pendientes — Sistema Planificador de la Producción (Torres Ocaranza)

**Documento vivo — se actualiza frecuentemente, sin versionado formal.** Sirve como trazabilidad rápida entre ventanas de chat distintas: cualquier sesión nueva puede leer esto para saber en qué estamos, sin depender de recordar en qué chat quedó cada cosa.

**Última actualización:** 2026-08-28, tras reunión con Roberto, René y Gustavo (TI Torres Ocaranza).

## Aprobado / resuelto
- GRANT de solo lectura en Cubigest para el agente de desarrollo local — aprobado.
- Llave SSH (Mac Studio ↔ servidor TO) — aprobado y formalizado.
- Auto-login / continuidad del servidor tras corte de energía — lo resuelve Rodrigo directamente (ya validado en su propia máquina de pruebas); avisa por correo cuando quede aplicado en el servidor de TO.
- Documento de seguimiento de 3 columnas (compromiso de Roberto) — cerrado, ya no aplica; superado por el protocolo de aviso + bitácora.

## En progreso
- **Sincronización horaria a Cubigest** — intervalo confirmado: **1 hora**. Es de las últimas tareas en desplegarse. Antes: enviar las consultas reales a Roberto, pasarlas por su optimizador de índices, y respetar las ventanas horarias acordadas para trabajo pesado (5:00–8:00 AM y 18:00–20:00 PM).
- **Cuenta dedicada para el sistema de averías** (reemplaza la cuenta personal de Gustavo, hoy hardcodeada en `scraper_cuadre_inet.py`) — reconocido abiertamente en la reunión, sin urgencia. Pendiente de una reunión 1:1 con Roberto.
- **Cuenta de servicio sin expiración de contraseña** — planteada por Rodrigo como prioridad uno en la reunión. **Sin confirmación explícita de Roberto capturada en la transcripción** — pendiente de que Rodrigo lo confirme directamente.

## Nuevo, fuera de los 5 puntos originales de la presentación
- Reunión 1:1 con Roberto sobre el sistema de averías — Rodrigo tiene un error de diseño propio, necesita ayuda para resolver dónde enganchar la extracción de datos.
- Monitoreo de carga propio durante consultas a Cubigest — compromiso explícito: si se detecta sobrecarga del sistema, se detiene la consulta.
- Protocolo de aviso, refinado respecto al PTS original — no todo requiere correo previo. Trabajo automatizado y liviano en régimen (ej. el sync horario ya funcionando) no necesita aviso cada vez; sí lo requiere trabajo de largo aliento o de impacto significativo.
- Entregar a Roberto todas las queries que hoy hace OptiFierro contra Cubigest, para revisión y posible optimización de su lado. No urgente.

## Borrador pendiente — no enviado aún
Correo a Roberto combinando (1) cuenta dedicada para el sistema de averías y (2) cuenta de servicio sin expiración de contraseña. Rodrigo lo retomará después de resolver otro tema primero — queda en pausa, recordar cuando se retome.

## Fuentes
- Transcripción de la reunión con TI Torres Ocaranza, 28-08-2026 (Roberto, René, Gustavo).
- Presentación "Sistema Planificador — Seguridad y Plan de Trabajo" (misma fecha).
- Procedimiento de Trabajo Seguro v1.0 (`procedimiento_trabajo_seguro.md`).
