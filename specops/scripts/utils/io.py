from __future__ import annotations

import json
from pathlib import Path


def resolve_path(input_path: str) -> Path:
    return Path(input_path).expanduser().resolve()


def read_json(file_path: str):
    path = resolve_path(file_path)
    return json.loads(path.read_text(encoding="utf-8"))


def read_text(file_path: str) -> str:
    path = resolve_path(file_path)
    return path.read_text(encoding="utf-8")


def write_text(file_path: str, content: str) -> Path:
    path = resolve_path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def apply_template(template: str, replacements: dict[str, str]) -> str:
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
    return rendered