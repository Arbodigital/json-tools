"""Funções básicas: ler, escrever, formatar e validar JSON (somente stdlib)."""

import json
from typing import Any, List

_TYPES = {
    "object": dict, "array": list, "string": str, "boolean": bool,
    "null": type(None),
}


def read_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Any, indent: int = 2) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def format_json(text: str, indent: int = 2, sort_keys: bool = False) -> str:
    return json.dumps(json.loads(text), indent=indent, sort_keys=sort_keys,
                      ensure_ascii=False)


def _type_ok(value: Any, t: str) -> bool:
    if t == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if t == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if t == "boolean":
        return isinstance(value, bool)
    return isinstance(value, _TYPES[t]) and not (
        t != "boolean" and isinstance(value, bool))


def validate(data: Any, schema: dict, path: str = "$") -> List[str]:
    """Valida `data` contra um subconjunto de JSON Schema.

    Suporta: type, enum, required, properties, items, minimum, maximum,
    minLength, maxLength. Retorna lista de erros (vazia se válido).
    """
    errors: List[str] = []
    t = schema.get("type")
    if t is not None:
        types = t if isinstance(t, list) else [t]
        if not any(_type_ok(data, x) for x in types):
            return [f"{path}: esperado tipo {t}, recebido {type(data).__name__}"]
    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: valor deve ser um de {schema['enum']}")
    if isinstance(data, dict):
        for key in schema.get("required", []):
            if key not in data:
                errors.append(f"{path}: campo obrigatório ausente '{key}'")
        for key, sub in schema.get("properties", {}).items():
            if key in data:
                errors += validate(data[key], sub, f"{path}.{key}")
    if isinstance(data, list) and "items" in schema:
        for i, item in enumerate(data):
            errors += validate(item, schema["items"], f"{path}[{i}]")
    if isinstance(data, (int, float)) and not isinstance(data, bool):
        if "minimum" in schema and data < schema["minimum"]:
            errors.append(f"{path}: menor que {schema['minimum']}")
        if "maximum" in schema and data > schema["maximum"]:
            errors.append(f"{path}: maior que {schema['maximum']}")
    if isinstance(data, str):
        if "minLength" in schema and len(data) < schema["minLength"]:
            errors.append(f"{path}: tamanho menor que {schema['minLength']}")
        if "maxLength" in schema and len(data) > schema["maxLength"]:
            errors.append(f"{path}: tamanho maior que {schema['maxLength']}")
    return errors
