"""Servidor MCP mínimo via stdio (JSON-RPC 2.0, uma mensagem por linha)."""

import json
import sys

from . import tools

PROTOCOL_VERSION = "2024-11-05"


def handle(msg: dict):
    """Processa uma mensagem; retorna resposta ou None (notificações)."""
    method, mid = msg.get("method"), msg.get("id")
    if mid is None:
        return None
    if method == "initialize":
        result = {"protocolVersion": PROTOCOL_VERSION,
                  "capabilities": {"tools": {}},
                  "serverInfo": {"name": "json-tools", "version": "0.1.0"}}
    elif method == "tools/list":
        result = {"tools": [t.describe() for t in tools.REGISTRY.values()]}
    elif method == "tools/call":
        params = msg.get("params") or {}
        out = tools.call_tool(params.get("name", ""),
                              params.get("arguments") or {})
        result = {"content": [{"type": "text",
                               "text": json.dumps(out, ensure_ascii=False)}],
                  "isError": not out["ok"]}
    elif method == "ping":
        result = {}
    else:
        return {"jsonrpc": "2.0", "id": mid,
                "error": {"code": -32601, "message": f"método desconhecido: {method}"}}
    return {"jsonrpc": "2.0", "id": mid, "result": result}


def serve_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            resp = handle(json.loads(line))
        except json.JSONDecodeError:
            resp = {"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32700, "message": "JSON inválido"}}
        if resp is not None:
            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
