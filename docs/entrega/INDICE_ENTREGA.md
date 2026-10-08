# Índice del Paquete de Entrega — Sistema Planificador de la Producción (SPP)

**Fecha:** 24 de septiembre de 2026  
**Destinatarios:** Gerencia de Operaciones, Gerencia de Logística y Jefes de Planta (Cerrillos, Calama, Coronel) — Torres Ocaranza  
**Ubicación de Documentación:** `/Users/montu/MontuMS/docs/entrega/`

---

## 1. Documentos del Paquete de Entrega

1. **[`MANUAL_USUARIO_SPP.md`](file:///Users/montu/MontuMS/docs/entrega/MANUAL_USUARIO_SPP.md):** Manual operativo para jefes de planta y gerencias que explica qué decide y qué no decide el SPP, el funcionamiento pantalla por pantalla (Gantt, Bolsa, Vista Semanal, Producción por Máquina, Gestores y Averías), la lectura de turnos y colaciones, el significado de los avisos estadísticos, las preguntas frecuentes y el glosario.
2. **[`MANUAL_TECNICO_SPP.md`](file:///Users/montu/MontuMS/docs/entrega/MANUAL_TECNICO_SPP.md):** Manual de ingeniería que detalla la arquitectura de contenedores Docker en el servidor TO, el diagrama Mermaid de flujos de integración, las reglas del motor de asignación, el scheduler automático (08:10/20:10), los procedimientos de despliegue y reversión (rollback), monitoreo y el mapa de archivos clave.
3. **[`FICHA_TECNICA_SPP.md`](file:///Users/montu/MontuMS/docs/entrega/FICHA_TECNICA_SPP.md):** Formulario técnico estructurado (ítem A12 del backlog) con criticidad media, stack de desarrollo, lenguajes, dependencias, bases de datos (SQLite local y SQL Server Cubigest en solo lectura), infraestructura física on-premise, dependencias sistémicas y análisis de riesgos normativos.
4. **[`INDICE_ENTREGA.md`](file:///Users/montu/MontuMS/docs/entrega/INDICE_ENTREGA.md):** Documento guía que consolida el inventario del paquete de entrega y el registro exhaustivo de ítems no verificados o pendientes de formalización.

---

## 2. Vacíos y POR CONFIRMAR

A continuación se lista exhaustivamente todo dato, parámetro o definición que no pudo ser comprobado en el código fuente ni en los documentos del repositorio, y que requiere confirmación formal:

### Infraestructura y Hardware
- `POR CONFIRMAR`: Especificaciones de hardware (CPU, memoria RAM y almacenamiento disponible) asignadas a la máquina anfitriona Windows 11 Pro en Torres Ocaranza.
- `POR CONFIRMAR`: Infraestructura cloud en producción directa (no se evidenció consumo directo de nubes públicas en runtime en TO; el sistema opera on-premise).
- `POR CONFIRMAR`: Proveedor exacto del repositorio Git remoto corporativo (`origin/master`).
- `POR CONFIRMAR`: Configuración formal de túneles externos o VPN para soporte técnico remoto hacia el servidor de TO.

### Parámetros Operativos y de Continuidad
- `POR CONFIRMAR`: Métricas formales de continuidad operativa (RTO / RPO) comprometidas para el servicio en caso de caída del servidor anfitrión.
- `POR CONFIRMAR`: Política, procedimiento y destino de respaldos automáticos periódicos para el archivo de base de datos local `optifierro_v2.db`.
- `POR CONFIRMAR`: Procedimiento institucional de integración con directorio corporativo (LDAP / Active Directory) para autenticación unificada de usuarios.

### Aspectos Normativos y Legales (Revisión con Montu)
- `POR CONFIRMAR CON MONTU`: Validación jurídica y laboral ante la Dirección del Trabajo (DT) sobre la aplicación de la ventana de tolerancia operativa de \(\pm\)15 minutos respecto a la jornada contractual y el descuento rígido de colación (13:00–14:00 día, 01:00–02:00 noche).
- `POR CONFIRMAR CON MONTU`: Tratamiento reglamentario de la Ley de 40 Horas (régimen de 42 horas observado a contar del 01-03-2026) en la configuración de turnos y capacidades de jornada.
- `POR CONFIRMAR CON MONTU`: Políticas de seguridad de la información y cumplimiento de la ley de protección de datos personales respecto al almacenamiento local de RUT, nombres y registros de asistencia de colaboradores.
- `POR CONFIRMAR CON MONTU`: Deslinde de responsabilidad técnica y operacional entre las sugerencias de asignación del motor de tiempos y las facultades autónomas de prevención de riesgos y seguridad industrial en planta.
- `POR CONFIRMAR CON MONTU`: Nivel y exigencia de certificación formal del software respecto a normas técnicas de construcción y calidad del acero (NCh204).
