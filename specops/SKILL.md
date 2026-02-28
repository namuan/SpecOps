---
name: specops
description: Adversarial requirements engineering skill that compiles ambiguous feature requests into a validated JSON spec, then generates failing tests and OpenAPI artifacts. Use when users ask to define, clarify, or formalize software requirements before implementation.
compatibility: Requires file read/write access. Artifact generators require Python 3 and/or Node.js.
metadata:
  author: namuan
  version: "0.1.0"
---

# SpecOps

SpecOps is a shift-left specification skill. It helps an agent turn vague requirements into a machine-checkable contract before any implementation coding starts.

## When to use this skill

- The user asks to define a new feature but requirements are still ambiguous.
- The user wants failing tests generated from agreed behavior.
- The team wants an intermediate contract between natural language and code.

## Operating workflow

1. Run the interaction loop in [instructions.md](./instructions.md).
2. Use prompts such as [initial_requirements_gather.txt](./prompts/initial_requirements_gather.txt) during requirement ingestion and clarification.
3. Produce a compiled spec that validates against [compiled-spec-schema.json](./schemas/compiled-spec-schema.json).
4. Only after explicit user approval, run generators such as [generate_jest.js](./scripts/generators/generate_jest.js) to write artifacts.

## Safety and trust requirements

- Do not execute filesystem-modifying scripts without explicit user confirmation.
- Do not treat unresolved ambiguity as acceptable; keep clarifying until completion criteria are met.
- If schema validation fails, return to clarification and repair the spec.

## Outputs

- `compiled-spec.json` (schema-valid)
- Failing Jest or PyTest test suite
- OpenAPI YAML (when API behavior is represented)
- Agent-optimized Markdown handoff summary

See [instructions.md](./instructions.md) for strict execution details.