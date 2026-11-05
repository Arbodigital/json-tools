import json
import threading
import urllib.request

from json_tools import core, tools, mcp_server, http_api, adapters
from json_tools.cli import main


def test_roundtrip(tmp_path):
    p = tmp_path / "a.json"
    core.write_json(str(p), {"a": "é"})
    assert core.read_json(str(p)) == {"a": "é"}


def test_validate():
    schema = {"type": "object", "required": ["n"],
              "properties": {"n": {"type": "integer", "minimum": 1}}}
    assert core.validate({"n": 2}, schema) == []
    assert core.validate({}, schema)
    assert core.validate({"n": True}, schema)
    assert core.validate({"n": 0}, schema)


def test_call_tool():
    assert tools.call_tool("json_parse", {"text": "{}"})["result"]["valid"]
    assert not tools.call_tool("json_parse", {"text": "{"})["result"]["valid"]
    assert not tools.call_tool("json_parse", {})["ok"]
    assert not tools.call_tool("nope", {})["ok"]


def test_cli(tmp_path, capsys):
    p = tmp_path / "a.json"
    p.write_text('{"a":1}')
    assert main(["validate", str(p)]) == 0
    p.write_text("{")
    assert main(["validate", str(p)]) == 1


def test_mcp():
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert len(r["result"]["tools"]) >= 3
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                           "params": {"name": "json_parse",
                                      "arguments": {"text": "[]"}}})
    assert r["result"]["isError"] is False
    assert mcp_server.handle({"jsonrpc": "2.0", "method": "x"}) is None


def test_http():
    srv = http_api.make_server("127.0.0.1", 0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    try:
        req = urllib.request.Request(
            base + "/call/json_parse", json.dumps({"text": "{}"}).encode(),
            {"Content-Type": "application/json"})
        assert json.loads(urllib.request.urlopen(req).read())["ok"]
        assert json.loads(urllib.request.urlopen(base + "/tools").read())
    finally:
        srv.shutdown()


def test_adapter_rejects_bad_url():
    try:
        adapters.register_http_agent("x", "file:///etc/passwd")
    except ValueError:
        return
    raise AssertionError


def test_json_get():
    d = {"a": {"b": [{"c": 5}]}}
    assert tools.call_tool("json_get", {"data": d, "path": "a.b.0.c"})["result"] == 5
    assert not tools.call_tool("json_get", {"data": d, "path": "a.x"})["ok"]


def test_cli_agents_flag(tmp_path, capsys):
    f = tmp_path / "ag.json"
    f.write_text(json.dumps([{"name": "ag1", "url": "http://127.0.0.1:1/x"}]))
    assert main(["--agents", str(f), "tools"]) == 0
    assert "ag1" in capsys.readouterr().out
    tools.REGISTRY.pop("ag1", None)
    assert main(["--agents", str(tmp_path / "nope.json"), "tools"]) == 1
