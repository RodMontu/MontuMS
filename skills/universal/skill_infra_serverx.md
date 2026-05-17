# Skill de Contexto: Infraestructura serverX
## Versión: 1.0 — Mayo 2026

---

## Identificación del nodo
- Hostname: serverX
- IP LAN: 192.168.1.111
- Usuario: x
- OS: Ubuntu Server 24.04 LTS
- Rol: nodo principal de cómputo, Docker host, Ollama host

## Hardware
- CPU: Intel Xeon E5-2673 v3 (12 cores)
- RAM: 32GB DDR3 ECC
- GPU IA: NVIDIA P104-100 8GB (Pascal, compute 6.1) — Ollama + modelos locales
- GPU display: AMD HD 8570 1GB — KDE/display headless
- Disco sistema: WDC (clonado post-incidente abril 2026)
- Almacenamiento: /mnt/extra (NAS Samba miau_nube)

## Restricción crítica de GPU
- NVIDIA P104-100: driver máximo = 580, CUDA hasta 12.x
- CUDA 13+ ya no soporta Pascal — NO actualizar drivers más allá de 580
- Ollama debe usar runtime: nvidia con OLLAMA_MAX_LOADED_MODELS=1
- ccl y ccgemma NO pueden correr simultáneamente (un modelo local a la vez)

## Servicios activos en serverX
- Ollama: Docker, puerto 11434, modelos: qwen2.5-coder:7b, gemma3n
- Portainer: Docker, puerto 9000
- NoMachine: puerto 4000 (LAN only, NO expuesto a internet)
- Pegas V2: Docker, puerto 8000
- Visual-Voice: Docker, puerto 8502

## Rutas clave
- Proyectos: /home/x/stack/
- Documentación TI: /mnt/extra/DOCUMENTOS_TECNICOS/ (Samba miau_nube)
- INVENTARIO_MAESTRO.md: /mnt/extra/DOCUMENTOS_TECNICOS/INVENTARIO_MAESTRO.md
- LOG_CAMBIOS_2026.md: /mnt/extra/DOCUMENTOS_TECNICOS/LOG_CAMBIOS_2026.md
- Agentes CC: /home/x/.claude/agents/
- Skills CC: /home/x/.claude/skills/
- CLAUDE.md: /home/x/.claude/CLAUDE.md

## Reglas de red
- serverX NO tiene puertos expuestos a internet
- Todo acceso externo pasa por Cloudflare Tunnel en serveri3 (192.168.1.211)
- cloudflared NUNCA debe correr en serverX
- DNS: Pi-hole en serveri3 (192.168.1.211)

## Acceso SSH desde Mac
- ssh x@192.168.1.111
- NoMachine: desde cliente NoMachine en Mac apuntando a 192.168.1.111:4000
