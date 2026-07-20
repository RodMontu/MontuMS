# Contrato futuro: Frontend / API sobre La Biblioteca

Este documento especifica como se debe envolver `mcp_tools/` cuando se
construya la interfaz web (fase futura). El stack sugerido es **FastAPI**,
por consistencia con OP Risk y OptiFierro, que ya lo usan.

**Regla de diseño no negociable:** la capa de datos (`schema.sql` +
`catalogo.db`) no se rediseña para la UI. El frontend es una envoltura
delgada (endpoints HTTP) sobre las funciones que ya existen en
`mcp_tools/`. Si la UI necesita algo que esas funciones no dan, se agrega
una funcion nueva en `mcp_tools/`, no se toca el schema a la fuerza.

## Endpoints propuestos

### `GET /api/biblioteca/buscar`
- Envuelve: `buscar_tema(query: str) -> list[dict]`
- Query params: `q` (obligatorio, el texto a buscar)
- Response:
  ```json
  {
    "resultados": [
      {
        "archivo": "docs/INVENTARIO_MAESTRO.md",
        "seccion": "OptiFierro",
        "resumen": "...",
        "tags": "OptiFierro,credenciales",
        "fecha_actualizacion": "2026-07-19T...",
        "relevancia": -1.23
      }
    ]
  }
  ```

### `GET /api/biblioteca/version`
- Envuelve: `obtener_ultima_version(archivo: str, seccion: str | None) -> dict`
- Query params: `archivo` (obligatorio), `seccion` (opcional)
- Response: la ficha (o `{}` si no existe)

### `POST /api/biblioteca/cambio`
- Envuelve: `registrar_cambio(archivo, seccion, resumen, tags, tipo)`
- Uso restringido: solo Aurora (o un proceso equivalente autenticado) debe
  poder llamar este endpoint. **No exponer sin autenticacion.**
- Request body:
  ```json
  {
    "archivo": "docs/INVENTARIO_MAESTRO.md",
    "seccion": "OptiFierro",
    "resumen": "...",
    "tags": "OptiFierro",
    "tipo": "documento"
  }
  ```
- Response: `204 No Content` en exito

### `GET /api/biblioteca/credencial`
- Envuelve: `buscar_credencial(query: str) -> list[dict]`
- Query params: `q` (obligatorio)
- Response: solo metadata (servicio, variable, archivo_env, fecha_rotacion,
  notas). **Nunca** devuelve valores reales, porque la tabla `credenciales`
  nunca los guarda.

## Notas de implementacion

- Cada endpoint es un wrapper de una linea sobre la funcion correspondiente
  de `mcp_tools/`; no debe reimplementar logica de consulta SQL.
- `catalogo.db` se sigue abriendo en modo lectura para los tres endpoints
  de consulta y en modo escritura solo para `/cambio`.
- Si en el futuro se necesita paginacion o filtros adicionales, se agregan
  parametros opcionales a las funciones existentes, no se crean tablas
  nuevas.

## Servidor MCP dedicado (implementado)

Ya existe un servidor MCP real que expone las 4 funciones de `mcp_tools/`
directamente (sin pasar por HTTP/FastAPI todavia). Cuando se construya el
frontend/API descrito arriba, puede consumir este servidor MCP en lugar de
reimplementar la logica de wrapping.

- **Host:** serverX (192.168.1.111), contenedor `biblioteca-mcp`
- **Puerto:** 8813
- **Path MCP (streamable HTTP):** `/mcp`
- **Health check:** `GET /healthz` -> `{"ok": true}`
- **Codigo fuente:** `/home/x/ws/biblioteca-mcp/` (Dockerfile, app.py, docker-compose.yml)
- **Herramientas registradas:** `buscar_tema`, `obtener_ultima_version`,
  `registrar_cambio`, `buscar_credencial` — cada una wrapea 1:1 la funcion
  homonima de `mcp_tools/`, sin logica adicional.
- **Bind mount:** `/home/x/MontuMS/biblioteca:/app/biblioteca` (rw, porque
  `registrar_cambio` escribe en `catalogo.db`)
- No depende del antiguo `mcp-core-mcp-core-1` (puerto 8812, ya no existe);
  es un servicio nuevo e independiente.
