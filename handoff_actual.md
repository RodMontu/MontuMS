# Handoff — Infraestructura Clawdio + MS-Flow inauguración
**Última actualización:** 2026-05-03
**Sesión anterior:** Miaude — fixes Clawdio + implementación MS-Flow base
**Próxima sesión:** OptiFierro entrega final martes 2026-05-05

---

## Proyecto activo
MS-Flow — Sistema de trabajo orquestado (inauguración)

## Objetivo de la sesión anterior
Reparar Clawdio (monitor.sh + SOUL.md) e implementar la infraestructura base de MS-Flow (handoff + repo MontuMS).

## Estado actual
- ✅ Completados: fix monitor.sh, fix SOUL.md, repo MontuMS creado, README MS-Flow, handoff_actual.md operativo
- 🔄 En curso: symlink handoff → MontuMS (esta sesión)
- ⏳ Pendientes: conectar Clawdio como lector/escritor del repo, definir hooks CC, OptiFierro entrega final

## Decisiones tomadas
- MS-Flow es el nombre del protocolo de coordinación de la MS (sistema nervioso)
- Repo MontuMS en GitHub (privado, RodMontu) es el sistema de archivos compartido Claude↔Gemini
- Handoff vive en /home/x/MontuMS/handoff_actual.md con symlink desde /home/x/handoff/
- CCa solo para tareas críticas — priorizar ccor1-5 para coding rutinario

## Próximo paso concreto
Arrancar revisión OptiFierro V2 en TO para entrega final martes 2026-05-05.
Ejecutar en TO: revisar estado actual de pendientes PEND-01, PEND-03, PEND-04 y nginx bind-mount.

## Convenciones activas
- serverX = 192.168.1.111 / serveri3 = 192.168.1.211
- AG = Antigravity / G3F = Gemini 3 Flash / G3.1PH = Gemini 3.1 Pro High
- CCa = tokens caros / ccor1-5 = gratuitos (priorizar)
- Miaude = arquitectura / Clawdio = orquestación / CC+AG = ejecución
- Docker: rebuild siempre / Correos: solo borrador

## Contexto adicional
MS-Flow inaugurado hoy. El repo MontuMS es el hub central. AG puede leer este archivo directamente para tomar contexto sin reexplicación. Próxima sesión arranca con OptiFierro — conectarse a TO (192.168.1.65) y revisar estado del sistema con Gustavo Godoy para cerrar entrega del martes.
