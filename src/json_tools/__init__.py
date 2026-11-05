"""json-tools: ler, escrever e validar JSON."""

from .core import read_json, write_json, validate, format_json
from .tools import Tool, REGISTRY, register, call_tool

__version__ = "0.1.0"
__all__ = ["read_json", "write_json", "validate", "format_json",
           "Tool", "REGISTRY", "register", "call_tool"]
