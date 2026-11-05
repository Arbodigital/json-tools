"""Interface única de "ferramenta": entrada e saída em JSON, com esquema.

Qualquer frontend (CLI, HTTP, MCP, adaptadores de agentes) usa `call_tool`.
"""

import json
from dataclasses import dataclass
from typing import Any, Callable, Dict

from .core import format_json, validate


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    func: Callable[[dict], Any]

    def describe(self) -> dict:
        return {"name": self.name, "description": self.description,
                "inputSchema": self.input_schema}


REGISTRY: Dict[str, Tool] = {}


def register(tool: Tool) -> Tool:
    REGISTRY[tool.name] = tool
    return tool


def call_tool(name: str, arguments: dict) -> dict:
    """Executa uma ferramenta. Sempre retorna {"ok": bool, ...}."""
    tool = REGISTRY.get(name)
    if tool is None:
        return {"ok": False, "error": f"ferramenta desconhecida: {name}"}
    errors = validate(arguments, tool.input_schema)
    if errors:
        return {"ok": False, "error": "argumentos inválidos", "details": errors}
    try:
        return {"ok": True, "result": tool.func(arguments)}
    except Exception as exc:  # noqa: BLE001 - devolve erro ao chamador
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _validate_tool(args: dict) -> dict:
    errors = validate(args["data"], args["schema"])
    return {"valid": not errors, "errors": errors}


def _parse_tool(args: dict) -> dict:
    try:
        json.loads(args["text"])
        return {"valid": True, "errors": []}
    except json.JSONDecodeError as exc:
        return {"valid": False, "errors": [str(exc)]}


register(Tool(
    "json_parse", "Verifica se um texto é JSON válido.",
    {"type": "object", "required": ["text"],
     "properties": {"text": {"type": "string"}}}, _parse_tool))

register(Tool(
    "json_format", "Formata (indenta) um texto JSON.",
    {"type": "object", "required": ["text"],
     "properties": {"text": {"type": "string"},
                    "indent": {"type": "integer", "minimum": 0},
                    "sort_keys": {"type": "boolean"}}},
    lambda a: format_json(a["text"], a.get("indent", 2),
                          a.get("sort_keys", False))))

register(Tool(
    "json_validate", "Valida um valor JSON contra um JSON Schema.",
    {"type": "object", "required": ["data", "schema"],
     "properties": {"schema": {"type": "object"}}}, _validate_tool))
