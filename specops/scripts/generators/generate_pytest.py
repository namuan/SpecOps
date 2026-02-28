#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[2]
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from scripts.utils.io import apply_template, read_json, read_text, write_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate failing PyTest tests from a SpecOps compiled spec"
    )
    parser.add_argument("--spec", required=True, help="Path to compiled-spec.json")
    parser.add_argument("--out", required=True, help="Output test file path")
    parser.add_argument(
        "--template",
        default=str(Path(__file__).resolve().parents[2] / "templates" / "pytest.test.template"),
        help="Template file path",
    )
    return parser.parse_args()


def sanitize_name(name: str) -> str:
    lowered = "".join(ch.lower() if ch.isalnum() else "_" for ch in name)
    while "__" in lowered:
        lowered = lowered.replace("__", "_")
    lowered = lowered.strip("_")
    return lowered or "scenario"


def scenario_to_test_block(scenario: dict) -> str:
    fn_name = sanitize_name(f"{scenario['id']}_{scenario['description']}")
    payload = json.dumps(
        {
            "given": scenario.get("given"),
            "when": scenario.get("when"),
            "then": scenario.get("then"),
        },
        indent=2,
        ensure_ascii=False,
    )
    return "\n".join(
        [
            f"def test_{fn_name}():",
            f"    scenario = {payload}",
            f"    pytest.fail(\"SpecOps generated failing test for {scenario['id']}: implement behavior to satisfy compiled spec.\")",
        ]
    )


def main() -> None:
    args = parse_args()
    spec = read_json(args.spec)
    scenarios = spec.get("scenarios", [])

    if not scenarios:
        raise ValueError("Compiled spec must include a non-empty scenarios array.")

    test_cases = "\n\n".join(scenario_to_test_block(scenario) for scenario in scenarios)
    template = read_text(args.template)
    rendered = apply_template(
        template,
        {
            "FEATURE_NAME": spec["featureName"],
            "GENERATED_AT": datetime.now(timezone.utc).isoformat(),
            "TEST_CASES": test_cases,
        },
    )

    output_file = write_text(args.out, rendered)
    print(f"Generated PyTest tests: {output_file}")


if __name__ == "__main__":
    main()