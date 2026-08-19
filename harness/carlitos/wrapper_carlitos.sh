#!/bin/bash
# Carlitos — wrapper Pi (coding agent) contra llama-server local
# (qwen3-coder-next-80b-a3b Q4_K_M, 127.0.0.1:11500).
#
# Politica "fovea selectivo" (formalizada 2026-08-19, ver EVALUACION_HARNESS_
# AGENTICOS_CARLITOS_2026-08.md y BACKLOG-FOVEA-BENCHMARK en INVENTARIO_MAESTRO.md):
# el benchmark formal de 15 tareas reales sobre OptiFierro-V2 mostro que las 4
# tools fovea_* (fovea_sketch/focus/dwell/impact) dan ventaja real y grande SOLO
# en tareas multi-archivo (busqueda de patrones cruzando archivos, trazado de
# referencias, estructura de directorio completo), y son neutras (a veces con
# overhead sin beneficio claro) en tareas acotadas a un solo archivo.
#
# Por eso el default es fovea OFF (las 4 tools quedan excluidas del set del
# modelo via --exclude-tools, mecanismo nativo de Pi, verificado). Se activa
# explicitamente con --fovea como primer argumento cuando la tarea es
# multi-archivo.
#
# Nota tecnica: el hook de "grep augment mode" de fovea (que agrega una
# seccion de grafo a resultados de grep nativo en queries tipo-simbolo) NO se
# puede togglear por invocacion sin reescribir el archivo de config de fovea
# (~/.pi/agent/fovea.json o <repo>/.pi/fovea.json) — Pi/fovea no exponen un
# override por CLI ni por variable de entorno para tools.grepMode. Ese hook
# queda activo en ambos modos. El benchmark mostro que es inocuo en tareas de
# archivo unico, asi que no se considero necesario resolverlo para esta fase.
# Detalle en BACKLOG-FOVEA-GREPMODE (INVENTARIO_MAESTRO.md).
#
# Uso:
#   Carlitos "tarea de un solo archivo"              -> fovea OFF (default)
#   Carlitos --fovea "tarea multi-archivo, trazado de referencias, etc."

set -eo pipefail
# Nota: NO se usa "set -u". macOS trae bash 3.2 de sistema (shebang /bin/bash),
# y en bash 3.2 expandir un array vacio como "${FOVEA_FLAG[@]}" bajo "set -u"
# lanza "unbound variable" (bug real encontrado probando este wrapper el
# 2026-08-19, no es teorico). bash 4+ no tiene este problema, pero no hay
# garantia de que /bin/bash sea Homebrew bash en este entorno.

FOVEA_TOOLS="fovea_sketch,fovea_focus,fovea_dwell,fovea_impact"

if [[ "${1:-}" == "--fovea" ]]; then
  shift
  FOVEA_FLAG=()
else
  FOVEA_FLAG=(--exclude-tools "$FOVEA_TOOLS")
fi

# Blindaje stdin SOLO en modo one-shot (hay prompt como argumento): sin esto,
# `pi -p` en modo headless puede colgarse esperando EOF de un stdin heredado
# que nunca cierra (bug real, ver LOG_CAMBIOS_2026.md 2026-08-18, mismo patron
# encontrado de nuevo en vivo el 2026-08-19 durante las pruebas de este
# wrapper). Si Carlitos se invoca alguna vez sin argumentos (modo interactivo/
# TUI), NO se toca stdin, porque redirigirlo a /dev/null rompería el REPL.
if [[ $# -gt 0 ]]; then
  exec pi --provider llama-local --model "qwen3-coder-next" \
    --append-system-prompt /Users/montu/.claude/carlitos-sp.md \
    "${FOVEA_FLAG[@]}" \
    "$@" < /dev/null
else
  exec pi --provider llama-local --model "qwen3-coder-next" \
    --append-system-prompt /Users/montu/.claude/carlitos-sp.md \
    "${FOVEA_FLAG[@]}"
fi
