"""Adaptadores: expõem agentes/serviços externos como ferramentas json-tools.

Um agente externo é descrito por um endpoint HTTP que aceita POST com JSON
{"arguments": {...}} e devolve JSON. Registre com `register_http_agent`, ou
carregue de um arquivo com `load_agents_file` (veja agents.example.json).
"""

import json
import urllib.request

from .core import read_json
from .tools import Tool, register


def register_http_agent(name: str, url: str, description: str = "",
                        input_schema: dict = None, timeout: float = 60) -> Tool:
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL deve começar com http:// ou https://")

    def call(args: dict):
        req = urllib.request.Request(
            url, json.dumps({"arguments": args}).encode("utf-8"),
            {"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            return json.loads(resp.read())

    return register(Tool(name, description or f"Agente externo {name}",
                         input_schema or {"type": "object"}, call))


def load_agents_file(path: str) -> list:
    """Carrega lista [{name,url,description,input_schema}, ...]."""
    return [register_http_agent(a["name"], a["url"], a.get("description", ""),
                                a.get("input_schema"))
            for a in read_json(path)]
