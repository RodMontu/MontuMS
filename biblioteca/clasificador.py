"""Clasificador heuristico por palabras clave para La Biblioteca.
Usado por Aurora en el camino de escritura (registrar_cambio)."""

TEMAS_KEYWORDS = {
    "OptiFierro": ["optifierro", "torres ocaranza", " to ", "to/"],
    "OP Risk": ["op risk", "op-risk", "oprisk", "accidentes laborales"],
    "Aurora": ["aurora", "bibliotecaria"],
    "Rabin": ["rabin", "hermes rabin", "hermes rabín"],
    "Ollama": ["ollama", "qwen", "gemma", "modelo local"],
    "serverX": ["serverx", "server x", "192.168.1.111"],
    "Mac Studio": ["mac studio", "192.168.1.102"],
    "NFS": ["nfs", "montaje", "samba", "mnt/extra"],
    "MCP Core": ["mcp-core", "mcp core", "mcp_core", "fastmcp", "8812"],
    "Cloudflare": ["cloudflare", "tunnel", "túnel", "serveri3"],
    "credenciales": ["credencial", "api key", "token", "contraseña", "password", ".env"],
    "backup/ARCA": ["backup", "arca", "respaldo"],
    "TO/Torres Ocaranza": ["torres ocaranza", "optifierro"],
}


def clasificar(texto: str) -> dict:
    texto_low = texto.lower()
    tags = []
    seccion = "sin_clasificar"

    for tema, keywords in TEMAS_KEYWORDS.items():
        for kw in keywords:
            if kw in texto_low:
                tags.append(tema)
                break

    if tags:
        seccion = tags[0]

    return {"seccion": seccion, "tags": tags}
