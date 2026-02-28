#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.utils.io import apply_template, read_json, read_text, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate OpenAPI YAML from a SpecOps compiled spec"
    )
    parser.add_argument("--spec", required=True, help="Path to compiled-spec.json")
    parser.add_argument("--out", required=True, help="Output YAML path")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parents[2] / "templates" / "openapi.yaml.template"),
        help="Template file path",
    )
    return parser.parse_args()


def slugify(name: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return value or "feature"


def extract_response_codes(scenarios: list[dict]) -> dict[str, str]:
    responses: dict[str, str] = {}
    for scenario in scenarios:
        then_lines = scenario.get("then", [])
        for line in then_lines:
            match = re.search(r"\b([1-5][0-9]{2})\b", line)
            if not match:
                continue
            code = match.group(1)
            responses.setdefault(code, line)
    if not responses:
        responses["200"] = "Successful operation"
    return dict(sorted(responses.items(), key=lambda item: int(item[0])))


def build_responses_block(response_map: dict[str, str], indent: int = 8) -> str:
    space = " " * indent
    lines = []
    for code, description in response_map.items():
        safe_description = description.replace('"', "'")
        lines.append(f'{space}"{code}":')
        lines.append(f'{space}  description: "{safe_description}"')
    return "\n".join(lines)


def build_schemas_block(data_models: dict, indent: int = 4) -> str:
    base_space = " " * indent
    lines: list[str] = []

    for model_name, model_data in data_models.items():
        fields = model_data.get("fields", {})
        required_fields = [name for name, field in fields.items() if field.get("required")]

        lines.append(f"{base_space}{model_name}:")
        lines.append(f"{base_space}  type: object")

        if required_fields:
            lines.append(f"{base_space}  required:")
            for field_name in required_fields:
                lines.append(f"{base_space}    - {field_name}")

        lines.append(f"{base_space}  properties:")
        for field_name, field_def in fields.items():
            lines.append(f"{base_space}    {field_name}:")
            lines.append(f"{base_space}      type: {field_def.get('type', 'string')}")

            if "format" in field_def:
                lines.append(f"{base_space}      format: {field_def['format']}")
            if "minLength" in field_def:
                lines.append(f"{base_space}      minLength: {field_def['minLength']}")
            if "maxLength" in field_def:
                lines.append(f"{base_space}      maxLength: {field_def['maxLength']}")
            if "minimum" in field_def:
                lines.append(f"{base_space}      minimum: {field_def['minimum']}")
            if "maximum" in field_def:
                lines.append(f"{base_space}      maximum: {field_def['maximum']}")

    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    spec = read_json(args.spec)
    data_models = spec.get("dataModels", {})

    if not data_models:
        raise ValueError("Compiled spec must include a non-empty dataModels object.")

    first_schema_name = next(iter(data_models.keys()))
    response_map = extract_response_codes(spec.get("scenarios", []))
    template = read_text(args.template)

    rendered = apply_template(
        template,
        {
            "FEATURE_NAME": spec["featureName"],
            "FEATURE_SLUG": slugify(spec["featureName"]),
            "REQUEST_SCHEMA_NAME": first_schema_name,
            "RESPONSES_BLOCK": build_responses_block(response_map),
            "SCHEMAS_BLOCK": build_schemas_block(data_models),
            "SPEC_VERSION": spec.get("specVersion", "1.0"),
            "GENERATED_AT": datetime.now(timezone.utc).isoformat(),
        },
    )

    output_file = write_text(args.out, rendered)
    print(f"Generated OpenAPI: {output_file}")


if __name__ == "__main__":
    main()