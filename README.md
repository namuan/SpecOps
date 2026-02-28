# SpecOps

SpecOps is an Agent Skill designed to enhance the software development process by systematically identifying and resolving ambiguities in human requirements. By leveraging a structured checklist and interactive dialogue, SpecOps ensures that AI agents have clear, unambiguous specifications to work from, ultimately improving the quality and accuracy of the software being developed.

![](assets/info.png)

## Key Features

- Adversarial clarification workflow to force requirement precision
- Compiled spec contract in strict JSON Schema format
- Generators for failing Jest and PyTest suites
- OpenAPI schema generation from compiled specs
- Agent-optimized handoff outputs for downstream coding agents

## Repository Layout

The implemented skill package is in [specops/](specops/).

## Quick Start

1. Create a compiled spec JSON (or start from [specops/examples/compiled-spec.example.json](specops/examples/compiled-spec.example.json)).
2. Generate failing tests:
	- `node specops/scripts/generators/generate_jest.js --spec specops/examples/compiled-spec.example.json --out /tmp/specops.generated.test.js`
	- `python3 specops/scripts/generators/generate_pytest.py --spec specops/examples/compiled-spec.example.json --out /tmp/test_specops_generated.py`
3. Generate OpenAPI:
	- `python3 specops/scripts/generators/generate_openapi.py --spec specops/examples/compiled-spec.example.json --out /tmp/specops.openapi.yaml`

## Skill Manifest

See [specops/SKILL.md](specops/SKILL.md) for activation guidance and workflow orchestration.