# json-tools

Ferramenta para ler, escrever e validar JSON em Python, sem dependências
externas. Também expõe suas funções como "ferramentas" de agentes de IA por
CLI, API HTTP e servidor MCP, no mesmo formato em qualquer plataforma.

## Instalação

### Termux (Android)
```
pkg update && pkg upgrade
pkg install python git
git clone https://github.com/Arbodigital/json-tools.git
cd json-tools
pip install -e .
```

### Linux / macOS / Windows
```
git clone https://github.com/Arbodigital/json-tools.git
cd json-tools
python -m pip install -e .
```

## Uso

```
json-tools validate arquivo.json
json-tools validate arquivo.json --schema esquema.json
json-tools format arquivo.json --indent 4
json-tools tools                                  # lista ferramentas (JSON)
json-tools call json_parse '{"text": "{\"a\": 1}"}'
```

Como biblioteca:
```python
from json_tools import read_json, write_json, validate
validate({"n": 1}, {"type": "object", "required": ["n"]})  # []
```

O `validate` suporta um subconjunto de JSON Schema: `type`, `enum`,
`required`, `properties`, `items`, `minimum`, `maximum`, `minLength`,
`maxLength`.

## Interface única de ferramentas

Toda ferramenta (`json_parse`, `json_format`, `json_validate`, `json_get`) tem nome,
descrição, `inputSchema` e responde `{"ok": true, "result": ...}` ou
`{"ok": false, "error": ...}`. Os argumentos são validados pelo esquema antes
da execução. Veja `src/json_tools/tools.py`.

### API HTTP
```
json-tools serve-http --port 8000
curl http://127.0.0.1:8000/tools
curl -X POST http://127.0.0.1:8000/call/json_parse -d '{"text":"{}"}'
```
Por padrão escuta só em `127.0.0.1`. Não há autenticação; não exponha à rede
sem proteção.

### Servidor MCP (Copilot, Claude, Cursor...)
Configure o cliente para executar `json-tools serve-mcp` (stdio):
```json
{"mcpServers": {"json-tools": {"command": "json-tools", "args": ["serve-mcp"]}}}
```

## Integrar outros agentes

Qualquer agente com endpoint HTTP (POST `{"arguments": {...}}` → JSON) vira
uma ferramenta:
```python
from json_tools.adapters import register_http_agent, load_agents_file
register_http_agent("meu_agente", "http://127.0.0.1:9000/run")
load_agents_file("agents.example.json")
```
Depois ele aparece em `/tools` e no MCP, e pode ser chamado pela mesma
interface. Na CLI, use a opção global `--agents`:
```
json-tools --agents agents.example.json tools
json-tools --agents agents.json serve-mcp
```

## Modelos locais (opcional)

Ollama ou o servidor do llama.cpp (`llama-server`), inclusive no Termux com
modelos pequenos:
```
json-tools ask "Resuma: ..." --backend ollama --model llama3.2:1b
json-tools ask "Resuma: ..." --backend llamacpp --url http://127.0.0.1:8080
```

## Desenvolvimento
```
pip install -e ".[dev]"
pytest
```
O CI roda em Linux, Windows e macOS (`.github/workflows/ci.yml`).
