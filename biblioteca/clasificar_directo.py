"""Clasificacion directa via API nativa de Ollama (sin bucle agentico de Claude Code).

Causa raiz del colgado de 9+ horas: invocar el modelo local a traves del bucle
agentico de Claude Code (--model aurora sobre ANTHROPIC_BASE_URL->Ollama) no tiene
timeout. Este modulo evita ese camino: llama directo a POST /api/chat de Ollama
con requests.post(..., timeout=timeout), sin tool-calling y sin bucle agentico.
La lectura de archivos y la escritura al catalogo las hace siempre el orquestador
(Bash/Read + mcp_tools.registrar_cambio), nunca el modelo.
"""

import json
import re
import time

import requests

OLLAMA_URL = "http://192.168.1.102:11434/api/chat"
MODELO = "qwen3.6:35b-a3b"

SYSTEM_PROMPT = """Eres un clasificador de documentacion tecnica para MontuMS.
Reglas:
- Nunca inventes datos que no esten en el texto recibido.
- Responde EXCLUSIVAMENTE con un JSON valido, sin texto extra, sin markdown:
  {"resumen": "resumen breve en espanol de 1-2 lineas", "tags": ["tag1", "tag2"]}
- Los tags deben ser palabras o frases cortas relevantes al contenido
  (nombres de servicios, IPs, proyectos, tecnologias mencionadas).
- No agregues explicaciones ni comentarios fuera del JSON."""


def _extraer_json(texto: str) -> dict:
    """Extrae el primer objeto JSON valido de un texto que puede traer
    ```json ... ``` o texto alrededor."""
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if not match:
        raise ValueError("no se encontro un objeto JSON en la respuesta")
    return json.loads(match.group(0))


def clasificar_seccion(texto: str, timeout: int = 60) -> dict:
    """Pide a Ollama (API nativa, sin shim de tool-calling) un resumen + tags
    en JSON estricto para una seccion de texto.

    Devuelve {"resumen": str, "tags": [str, ...]} o {"error": str} -- nunca
    lanza una excepcion sin capturar.
    """
    payload = {
        "model": MODELO,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": texto},
        ],
        "stream": False,
        "format": "json",
    }

    inicio = time.monotonic()
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        duracion = time.monotonic() - inicio
        print(f"[clasificar_seccion] llamada real: {duracion:.2f}s (timeout={timeout}s)")
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        duracion = time.monotonic() - inicio
        print(f"[clasificar_seccion] TIMEOUT tras {duracion:.2f}s")
        return {"error": f"timeout tras {timeout}s esperando a Ollama"}
    except requests.exceptions.ConnectionError as e:
        return {"error": f"error de conexion con Ollama: {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"error HTTP llamando a Ollama: {e}"}

    try:
        cuerpo = resp.json()
        contenido = cuerpo["message"]["content"]
    except (ValueError, KeyError) as e:
        return {"error": f"respuesta de Ollama con formato inesperado: {e}"}

    try:
        resultado = _extraer_json(contenido)
    except (ValueError, json.JSONDecodeError) as e:
        return {"error": f"JSON invalido en la respuesta del modelo: {e}"}

    if "resumen" not in resultado or "tags" not in resultado:
        return {"error": f"JSON valido pero le faltan claves resumen/tags: {resultado}"}

    return resultado


if __name__ == "__main__":
    texto_prueba = (
        "OptiFierro es el cliente Torres Ocaranza, corre en un servidor Windows 11 "
        "en 192.168.1.65 con Docker en C:/Users/OptiFierro/Desktop/optifierro/. "
        "El acceso SSH usa la key ~/.ssh/id_optifierro."
    )
    print(clasificar_seccion(texto_prueba))
