"""CLI: json-tools {validate,format,tools,call,serve-http,serve-mcp,ask}."""

import argparse
import json
import sys

from . import tools
from .core import read_json, validate


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="json-tools")
    p.add_argument("--agents", metavar="ARQUIVO",
                   help="JSON com agentes externos a registrar como ferramentas")
    sub = p.add_subparsers(dest="cmd", required=True)

    v = sub.add_parser("validate", help="valida arquivo JSON (opcional --schema)")
    v.add_argument("file")
    v.add_argument("--schema")

    f = sub.add_parser("format", help="formata arquivo JSON")
    f.add_argument("file")
    f.add_argument("--indent", type=int, default=2)
    f.add_argument("--sort-keys", action="store_true")

    sub.add_parser("tools", help="lista ferramentas em JSON")

    c = sub.add_parser("call", help="chama ferramenta: call NOME '{json}'")
    c.add_argument("name")
    c.add_argument("arguments", nargs="?", default="{}")

    h = sub.add_parser("serve-http", help="API HTTP")
    h.add_argument("--host", default="127.0.0.1")
    h.add_argument("--port", type=int, default=8000)

    sub.add_parser("serve-mcp", help="servidor MCP via stdio")

    a = sub.add_parser("ask", help="pergunta a um modelo local (Ollama/llama.cpp)")
    a.add_argument("prompt")
    a.add_argument("--backend", choices=["ollama", "llamacpp"], default="ollama")
    a.add_argument("--model", default="llama3.2:1b")
    a.add_argument("--url")

    args = p.parse_args(argv)

    if args.agents:
        from .adapters import load_agents_file
        try:
            load_agents_file(args.agents)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            print(f"erro ao carregar agentes: {exc}", file=sys.stderr)
            return 1

    if args.cmd == "validate":
        try:
            data = read_json(args.file)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"JSON inválido: {exc}", file=sys.stderr)
            return 1
        errors = validate(data, read_json(args.schema)) if args.schema else []
        for e in errors:
            print(e, file=sys.stderr)
        if not errors:
            print("OK")
        return 1 if errors else 0
    if args.cmd == "format":
        try:
            with open(args.file, encoding="utf-8") as fh:
                print(tools.REGISTRY["json_format"].func(
                    {"text": fh.read(), "indent": args.indent,
                     "sort_keys": args.sort_keys}))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"erro: {exc}", file=sys.stderr)
            return 1
        return 0
    if args.cmd == "tools":
        print(json.dumps([t.describe() for t in tools.REGISTRY.values()],
                         indent=2, ensure_ascii=False))
        return 0
    if args.cmd == "call":
        try:
            arguments = json.loads(args.arguments)
        except json.JSONDecodeError as exc:
            print(f"argumentos inválidos: {exc}", file=sys.stderr)
            return 1
        out = tools.call_tool(args.name, arguments)
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 0 if out["ok"] else 1
    if args.cmd == "serve-http":
        from .http_api import serve
        serve(args.host, args.port)
        return 0
    if args.cmd == "serve-mcp":
        from .mcp_server import serve_stdio
        serve_stdio()
        return 0
    if args.cmd == "ask":
        from .backends import ask
        print(ask(args.prompt, args.backend, args.model, args.url))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
