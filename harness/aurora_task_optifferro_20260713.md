# TAREA AURORA — Documentar sesión OptiFierro V2 | 2026-07-13

## Instrucción
Actualizar LOG_CAMBIOS_2026.md en /home/x/MontuMS/ con todos los
cambios de la sesión de trabajo del 13 de julio de 2026 en OptiFierro V2.
Usar el formato estándar del log. NO modificar entradas anteriores.

---

## CAMBIOS A DOCUMENTAR

### Fecha: 2026-07-13
### Proyecto: OptiFierro V2 (Torres Ocaranza)
### Servidor: TO (192.168.1.65, Windows 11, contenedor optifierro-backend)

---

### [FIX] Gestor Materia Prima — SALDO INET (fuente definitiva)

Reemplaza scraper frágil de MP_Inet.aspx por SQL directo a TOCARANZA.dbo.EstExi1.Ebostoact.
Fuente idéntica a SP_ConsultasGenerales @Opcion=157 de Cubigest.
Archivo: backend/database_cubigest.py — método nuevo: obtener_saldo_inet_estex1()

BodCod mapping (campo bodega de tabla Sucursal, NO idsucursalINET):
- Calama (suc_id=1) → BodCod=2
- Cerrillos (suc_id=10) → BodCod=1
- Coronel (suc_id=14) → BodCod=801 (era 3 con idsucursalINET — incorrecto)

Validado: SALDO INET identico a Cubigest MP_Inet.aspx para las tres sucursales.

---

### [FIX] Gestor Materia Prima — SALDO CUB (filtros correctos)

Archivo: backend/database_cubigest.py — método: obtener_stock_bodega()

Filtros agregados (igual a Cubigest SP_ConsultasGenerales @Opcion=148):
- e.TipoEtiqueta = 'P' (solo etiquetas de Produccion)
- e.Grabada = 'S' (solo etiquetas confirmadas en sistema)
Formula: per-etiqueta PesoPaquete - KgsVinculados via LEFT JOIN a EtiquetasVinculadas.

Validado: SALDO CUB identico a columna Saldo Cubigest en MP_Inet.aspx.

---

### [FIX] Gestor Materia Prima — COMPROMETIDO y NECESIDAD

Archivo: backend/routers/materias_primas.py

Root cause: map_comp agrupaba comprometido por diametro base (stripping X suffix),
asignando mismo valor a TODOS los largos del mismo diametro — falsas alertas en X08..X12.

Correccion:
1. map_comp mantiene claves sin largo (B63N25, R63N12...) — dato real de Cubigest
2. _primary_of_group: primer largo (orden alfabetico) de cada grupo recibe comprometido
3. Secundarios reciben comprometido=None (muestra como guion en frontend)
4. NECESIDAD = COMPROMETIDO - (SALDO_CUB + OC_PENDIENTE) con valores individuales
5. alerta = necesidad > 0
6. Sort descendente: -x["necesidad"] — alertas rojas aparecen arriba de la lista

Semantica confirmada con Montu:
- SALDO_CUB y SALDO_INET son dos vistas del mismo stock; NUNCA sumarlos
- OC_PENDIENTE = material en transito (viene en camino)
- COMPROMETIDO = kg con OC de clientes pendientes de fabricar
- NECESIDAD positiva = deficit (ROJO); negativa = surplus (sin alerta)

---

### [FIX] Detalle Comprometido — fecha mas reciente

Archivo: backend/routers/materias_primas.py
Endpoint: GET /api/materias_primas/comprometido_detalle

Columna DESPACHO cambiada de MIN a MAX de (FechaDespacho, FechaEntrega).
FechaDespacho es la que Cubigest actualiza en cada reprogramacion.
MIN mostraba FechaEntrega (fecha original cliente, mas antigua).
MAX muestra la fecha operativa mas reciente.

---

### [FIX] Frontend GestorMatPrima.tsx — bugs visuales

Archivo: frontend/src/components/domain/GestorMatPrima.tsx

1. Scroll ghost: thead sticky sin fondo — agregado bg-white dark:bg-slate-900
2. Key groupFirstSet: colision entre barras (B) y rollos (R) del mismo diametro.
   La barra tomaba el slot y el rollo perdia su comprometido.
   Fix: key usa cod.slice(1,4) (incluye tipo B/R) — grupos separados.
3. Comprometido display: condicion isFirstInGroup && comprometido > 0

---

### [FEAT] Permiso Ver Geovictoria en Panel de Roles

Archivos: backend/auth.py, SQLite (roles_permisos), frontend/Administracion.tsx

Nuevo permiso ver_geovictoria agregado a la matriz de roles:
- SuperAdmin: habilitado
- Admin: habilitado
- JefePlanta: habilitado
- Visualizador: deshabilitado

Tab Geovictoria en Panel de Administracion ahora es condicional al permiso.

---

### [FIX] Bug JefePlanta — sucursal bloqueada en Calama tras login

Archivo: frontend/src/App.tsx

Root cause: globalSucursal se inicializaba con useState() UNA VEZ al montar App,
antes del login. En ventana incognito, auth_user no existe en localStorage — default
'1' (Calama). Al hacer login, setAuthUser() re-renderizaba pero globalSucursal ya
estaba clavado en '1'.

Fix: en callback onLogin, se agrega setGlobalSucursal(String(user.sucursal_asignada))
para JefePlanta. Detectado con Jose Auger (JefePlanta Cerrillos, sucursal_asignada=10).

---

### [FEAT] Forzar cambio de contrasena tras reset admin

Archivos: backend/auth.py, SQLite (tabla usuarios), frontend LoginScreen + App.tsx

Nueva columna: ALTER TABLE usuarios ADD COLUMN debe_cambiar_password INTEGER NOT NULL DEFAULT 0

Flujo:
1. Admin resetea contrasena — debe_cambiar_password=1 en BD
2. Usuario hace login — backend retorna flag en user_data
3. Frontend activa modal bloqueante (z-[300], sin escape posible)
4. Usuario ingresa nueva contrasena + confirmacion
5. POST /api/auth/cambiar_password_forzado — BD limpia flag — modal cierra
6. Usuario navega normalmente

Nuevo endpoint: POST /api/auth/cambiar_password_forzado
Estado inicial post-deploy: todos los usuarios en 0 (ningun reset pendiente).

---

## NOTA
No hay cambios de infraestructura en esta sesion. No actualizar INVENTARIO_MAESTRO.
