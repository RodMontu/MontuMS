
---
# TAREA CCa-36 — F4: operadores vs ayudantes por cargo de Geovictoria; maquina detenida sin operador; candidatos a baja (solo reporte)
TAG: `f4` (rama `ola1-f4`, directorio `optifierro_f4`). Informe: `CCa36_f4_operadores_20261005.md`.
AVISO: toca el Motor. Montu autorizo explicitamente esta tarea en el chat ("aplica tal cual. Delega a CCa las ejecuciones que requieras").
Si por tu politica no puedes ejecutarla, escribe en el informe EXACTAMENTE que parte rechazas y por que, y entrega igual la parte de
diagnostico y el CSV de bajas (solo lectura): la Coordinadora implementara el resto directamente.

## Citas literales de Montu
- "Confirmo que lo que manda es lo que esta en Geovictoria, es decir, si el cargo de la persona dice Operador Senior, Operador Junior o simplemente Operador, entonces es Operador; en cambio, si dice Ayudante de Operador, el cargo es Ayudante."
- "Los que se detecten como operador, deberan aparecer en la seccion Gestor de Operadores para asignarles maquinas (las que estan autorizados a operar) y en el Gestor de Maquinas para asignar el operador frecuente en la pestana 'Maestros'."
- "una maquina solamente puede ser operada por un Operador, no por un Ayudante de Operador."
- "si tengo 5 operadores presentes en esta jornada, puedo operar solamente 5 maquinas de manera simultanea ... por cada operador se pierde 30 minutos (15 al inicio y 15 al fin) y ademas la hora del break, 60 minutos, que se resta a los minutos hombre disponibles."
- "Hay que asegurar que no exista conflicto de operador entre maquinas."
- "Si una maquina esta 'detenida', entonces no puede tener operador asignado."
- Regla de bajas (B11/B37 + QA 05-10): "si un colaborador no aparece en el listado de Geovictoria, entonces el ha sido desvinculado de la empresa, por lo cual hay que eliminarlo del SPP." Montu: "aplica tal cual" la regla por cargo (en Coronel, Cristian Urra, Dilan Diaz y Matias Urra son 'Ayte del Operador' => ayudantes; Remiz corregira el cargo en Geovictoria si alguno realmente opera).

## Hechos del diagnostico (CCa-30 D3 + verificacion de Miaude con datos vivos 05-10)
- Geovictoria Coronel hoy (contenedor `geovictoria_api`, `/app/asistencia.db`, tabla `asistencia_colaboradores`): Operador Junior Practica (Damian Neira),
  Operador Junior (Enzo Lara, Kurt Gallegos), Operador Senior (Rafael Neira), "Ayte del Operador" (Cristian Urra, Dilan Diaz, Matias Urra),
  Mecanico Junior (Cristian Escalona, Hector Guerrero).
- `_es_ayudante` / `_es_operador` (lista blanca, ya cubre "Ayte"/"ayudante") existen solo en `backend/routers/jornada.py:37,48`.
  El motor de asignacion nunca los consulta (`_operadores_candidatos`, `motor_v2.py:1950`; pool: `_obtener_operadores_disponibles`, `programacion.py:2385`;
  hay un comentario "ya filtrado por cargo Operador" en `_obtener_presencia_capacidad` ~2554: verifica con codigo que filtra y que NO).
- Eventos de Coronel hoy (GET /api/programacion): Dilan Diaz (ayudante) 4 eventos en Dobladoras 2/3; Matias Urra (ayudante) 5 eventos en Dobladoras 3/4 y TJK 1;
  "Cristofer Andres Urra Salgado" 4 eventos en Cortadora Manual — NO figura en Geovictoria de hoy; y un evento con operador crudo `dneira`
  (el codigo exige nombre completo: `motor_v2.py:235,1299`).
- `recursos[].operador/estado_maquina` (`obtener_programacion`, `programacion.py:520-724`) sale de `maquinas_info` estatica: "Linea Corte Coronel" aparece
  "Operativa" con operador "Hector Manuel Acuña Sanhueza" aunque el Motor la excluye como detenida (`cubigest_averias_30min`) y ese operador ni esta
  en Geovictoria ni tiene autorizaciones. Existe `backend/estado_maquinas.py` (`obtener_estado_efectivo_maquinas`) con el estado efectivo correcto.
- `operadores_contados = 6` identico en las 3 plantas hoy (sospechoso; Coronel tiene 4 operadores por cargo).

## Que hacer
Motor / backend:
1. Pool de asignacion: SOLO personas presentes (Geovictoria, hoy y turno) cuyo cargo cumpla `_es_operador`. Ayudantes y otros cargos nunca reciben
   maquinas, aunque tengan autorizaciones en `operadores_matriz` (la matriz NO manda sobre el cargo). Debe valer en TODAS las rutas de asignacion:
   asignacion normal, reparto entre maquinas, `completar_con_adelanto` (reutilizacion de operador `d6fc4a9`) y la corrida automatica 08:10/20:10.
   Reutiliza `_es_operador/_es_ayudante` desde un modulo comun si es necesario (sin duplicar la logica; no cambies sus reglas).
2. Causa raiz y arreglo de: (a) operador asignado que NO esta presente hoy en Geovictoria (caso Cristofer Urra Salgado / Cortadora Manual);
   (b) operador crudo (`dneira`) en vez de nombre completo. Si la causa no queda clara con evidencia, detente en ese punto y reportalo (no parches a ciegas).
3. Sin conflicto de operador: un operador no puede estar en dos maquinas a la vez (reglas B15 existentes); verifica con test que se mantiene tras (1).
4. Capacidad (B16, `motor_v2.py:~1891` y `_obtener_presencia_capacidad`): `operadores_contados` = operadores presentes por cargo (misma funcion de (1)).
   La formula de minutos (ventana de la planta ya con +-15 min, menos 60 min de colacion, por operador) NO se cambia ni se resta dos veces: demuestralo con un ejemplo
   numerico en el informe. Lista en el informe, por planta, los operadores presentes SIN autorizaciones de maquina (informativo; p. ej. Rafael Neira): no los resuelvas.
5. `recursos` de `obtener_programacion` (SOLO ese bloque): maquina con estado efectivo DETENIDA => sin operador y estado reflejado como detenida
   (usa `estado_maquinas.py`); si la maquina no tiene tareas y su habitual (`Operador_Habitual`) no es un operador presente hoy => "Sin Operador".
   No cambies el resto de la respuesta.
Gestores (cambio minimo):
6. Gestor de Operadores: solo personas con cargo operador (por Geovictoria) aparecen para asignarles maquinas; los ayudantes NO aparecen en esa lista
   (sus filas en `operadores_matriz` se CONSERVAN, no se borran). "Personal presente hoy": clasificacion solo por cargo.
   Gestor de Maquinas > Maestros: el selector de operador frecuente ofrece solo operadores. Ubica los routers/componentes reales; si el cambio exige tocar mas de
   los archivos permitidos, detente y reportalo.
Bajas (SOLO REPORTE, no apliques nada):
7. Para las 3 plantas (sin TOSOL): lista de personas de `operadores_matriz` y de `Operador_Habitual/_Noche` de `maquinas_info` que NO aparecen en
   `asistencia_colaboradores` de Geovictoria en los ultimos 30 dias (cualquier dia), con el metodo de match usado (nombre completo, o usuario
   [inicial][apellido] para casos como `dneira`) y su nivel de certeza; marca los AMBIGUOS. Guarda CSV en
   `/Users/montu/MontuMS/docs/agentes/CCa36_bajas_candidatas_20261005.csv`. Incluye gacuna/hacuna y Hector Acuña. Lectura via
   `docker exec geovictoria_api python3 -` con sqlite `mode=ro`.
8. Tests nuevos con datos sinteticos (ayudante con autorizaciones no recibe maquina; ausente no recibe maquina; detenida sin operador; capacidad cuenta por cargo)
   y regresion de los existentes relevantes.

## Archivos permitidos
`backend/motor_v2.py` (solo `_operadores_candidatos`, el conteo de capacidad y llamadas puntuales), `backend/routers/programacion.py` (solo
`_obtener_operadores_disponibles`, `_obtener_presencia_capacidad` y el bloque `recursos`), routers de operadores/maquinas y los componentes frontend del
Gestor de Operadores / Maestros (cambio minimo), tests nuevos.

## NO HAGAS (especifico)
No borres ni desactives filas de `operadores_matriz`/`maquinas_info`. No apliques bajas. No cambies la formula de capacidad ni la logica de ribetes
(otra ventana: no toques estilos de `GestorProgramacion.tsx` ni la funcion de `viene_de_futuro`). No toques `completar_con_adelanto` salvo para que use el
pool filtrado. No corrijas el cargo en Geovictoria ni agregues autorizaciones a nadie (eso lo define Remiz). No toques el filtro de Cubigest ni sync.
