# La Biblioteca

La Biblioteca es el catalogo central de toda la documentacion tecnica del
ecosistema de Montu (OptiFierro, OP Risk, Aurora, Rabin, serverX, Mac Studio,
MCP Core, credenciales, etc). Es como un indice de biblioteca: no guarda los
documentos completos, guarda "fichas" con resumen, tags y fecha de cada
seccion, para poder encontrar informacion al instante.

## La idea central: escritura lenta, lectura rapida

Hay dos caminos totalmente separados:

- **Escritura (lenta, con criterio):** Aurora, la bibliotecaria, es la unica
  que agrega o actualiza fichas en el catalogo. Aurora lee los documentos
  fuente (INVENTARIO_MAESTRO.md, LOG_CAMBIOS_2026.md, etc), decide como
  clasificarlos y los guarda. Este camino puede tardar porque involucra
  criterio (un modelo de lenguaje).

- **Lectura (rapida, sin IA):** cualquier consulta — mia, de otros agentes,
  o de una futura interfaz web — va directo a una base de datos (SQLite),
  sin pasar por Aurora ni por ningun modelo de lenguaje. Es una simple
  busqueda de texto, tan rapida como buscar una palabra en un indice.

Esta separacion evita que cada consulta simple ("¿que sabemos de
OptiFierro?") tenga que esperar a un modelo de IA para responder.

## Piezas

- `schema.sql`: la estructura de la base de datos (las "tablas" donde se
  guarda todo).
- `catalogo.db`: la base de datos en si. Se genera automaticamente, **nunca
  se edita a mano** y **nunca se sube a git** (ver `.gitignore`).
- `indexador.py`: el script que Aurora (o cualquiera, manualmente) corre
  para leer los documentos .md y volcar su contenido al catalogo.
- `clasificador.py`: las reglas que deciden a que tema pertenece cada
  seccion de texto (OptiFierro, Ollama, credenciales, etc).
- `mcp_tools/`: las funciones que se usaran como herramientas de consulta
  y escritura (buscar un tema, ver la ultima version de un documento,
  registrar un cambio, buscar metadata de una credencial).
- `docs/CONTRATO_FUTURO_FRONTEND.md`: especificacion para cuando se
  construya una interfaz web sobre este catalogo.

## Como se alimenta (Aurora)

Aurora corre `indexador.py` (todo o `--solo-archivo nombre.md` para uno
especifico) cada vez que hay documentacion nueva o actualizada. El proceso
es repetible: correrlo varias veces no duplica informacion, solo actualiza
lo que cambio.

## Como se consulta

Cualquier agente o interfaz que necesite informacion llama directamente a
las funciones de `mcp_tools/` (por ejemplo `buscar_tema("OptiFierro")`).
Estas funciones solo leen la base de datos, no piensan ni interpretan nada.

## Que NO hacer

- **No editar `catalogo.db` a mano.** Si algo esta mal, se corrige en el
  documento fuente (.md) y se vuelve a correr el indexador.
- **No commitear credenciales.** La tabla `credenciales` solo guarda datos
  de referencia (que servicio, que variable, en que archivo .env vive),
  **jamas el valor real de una clave o contraseña**. Los valores reales
  viven aparte, en la boveda de credenciales (fuera de este repositorio).
- **No mezclar el camino de lectura con el de escritura.** Ninguna consulta
  de lectura debe invocar a Aurora ni a ningun modelo de lenguaje.
