# VENTANA V3 — B26: "Produccion por Maquina" (Ola 1)
Antes de todo: lee `/Users/montu/MontuMS/docs/agentes/prompts/00_CONTEXTO_BASE_OLA1.md` y aplica sus reglas.

## Tu carril
**Punto:** B26 — terminar la seccion "Produccion por Maquina" (ton/hora por maquina segun forma + diametro + largo). NO parte de cero.
**Archivos:** solo el router/endpoint y el componente frontend de esta seccion (ubicalos con el informe `agentes/CCa2_motor_blast_20260923.md`, tabla B26).
**Prohibido:** `motor_v2.py` (V1), `routers/programacion.py` y `GestorProgramacion.tsx` (V2). Puedes IMPORTAR funciones del Motor, no editarlas.
**Fuera de alcance hoy:** B44(b) (campo "capacidad real" al final de esta pantalla) y auto-aprendizaje: van en Ola 3 junto con B44. No dejes codigo a medias para eso.

## Ya hecho (commits 77bc809, 818bc18, 21-09)
Rename de menu a "Produccion por Maquina", filtros (ID Forma, diametro, sucursal, periodo), ton/hora por quintil, filtro por largo (conversion d^2/162).

## Faltante y decisiones de Montu (23-09)
1. Titulo interno sobre el selector: **"Tiempos por Maquina (estimado)"** (hoy el componente dice otra cosa; unificar).
2. **Sin porcentaje de confianza inventado.** Ninguna distribucion paso las pruebas de ajuste en los 32 equipos (bimodalidad real), asi que "confianza XX%" seria falso.
   Decision de Montu: rango empirico P25-P75 + frase honesta, p.ej. "Producciones estimadas en base a antecedentes historicos; rango tipico segun el historial (P25-P75)".
   Reemplaza el copy actual ("sin intervalo estadistico riguroso") de forma coherente. Muestra tambien N de observaciones por fila.
3. **Bug 1 — "bin de peso" mas cercano sin aviso:** agrega indicador "fuera de rango" cuando el bin usado esta lejos del pedido. Define el umbral con datos reales y PROPONELO a Montu antes de fijarlo.
4. **Bug 2 — mezcla de metodos:** la tabla combina el metodo validado (ton/hora, operario+maquina+pedido) con deltas crudos sin validar (min/mediana/max en minutos, filtro laxo 2-480 min) -> numeros sin sentido (min 2,2; max 442).
   Deja SOLO el metodo validado; elimina o reemplaza esas columnas. Verifica que ninguna otra pantalla dependa de ellas.
5. "Rutas posibles" es una aproximacion historica (`resolver_ruta()` no se usa): no la vendas como ruteo real; que el copy diga "segun historial".

## Pasos
1. Graphify + informe CCa-2: confirma archivos y dependientes. 2. Foto ANTES en produccion (capturas de la tabla para 2-3 formas/diametros por planta).
3. Implementa (CCa para backend; los textos/UI triviales puede hacerlos Gemini CLI con reglas copiadas y SIN commit propio; el commit lo haces tu tras diff aprobado por Montu).
4. Verifica DESPUES contra el sistema real, 3 plantas: sin numeros absurdos, indicador visible en un caso forzado, sin regresion en filtros. Build TS limpio.
5. Diff a Montu, OK, commit (`feat/fix(produccion-maquina): rango empirico P25-P75, indicador fuera de rango, solo metodo validado — B26`), turno de deploy, regenera Graphify.
6. Reporta segun protocolo (RESUMEN <=15 lineas).
