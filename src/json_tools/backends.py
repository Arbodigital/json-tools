"""Backends opcionais de modelo local (Ollama e llama.cpp server), via stdlib."""

import json
import urllib.request

DEFAULT_URLS = {"ollama": "http://127.0.0.1:11434",
                "llamacpp": "http://127.0.0.1:8080"}


def _post(url: str, payload: dict, timeout: float) -> dict:
    if not url.startswith(("http://", "https://")):
        raise ValueError("URL deve começar com http:// ou https://")
    req = urllib.request.Request(
        url, json.dumps(payload).encode("utf-8"),
        {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
        return json.loads(resp.read())


def ask(prompt: str, backend: str = "ollama", model: str = "llama3.2:1b",
        url: str = None, timeout: float = 120) -> str:
    base = (url or DEFAULT_URLS[backend]).rstrip("/")
    if backend == "ollama":
        out = _post(base + "/api/generate",
                    {"model": model, "prompt": prompt, "stream": False}, timeout)
        return out["response"]
    if backend == "llamacpp":
        out = _post(base + "/v1/chat/completions",
                    {"model": model,
                     "messages": [{"role": "user", "content": prompt}]}, timeout)
        return out["choices"][0]["message"]["content"]
    raise ValueError(f"backend desconhecido: {backend}")
