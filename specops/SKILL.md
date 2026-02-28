---
name: specops
description: Adversarial requirements engineering skill that compiles ambiguous feature requests into a validated JSON spec, then instructs the LLM to generate failing tests in the target repository's native language/framework. Use when users ask to define, clarify, or formalize software requirements before implementation.
compatibility: Requires file read/write access to the target repository where tests will be generated.
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
2. Start with a Markdown specification using `prompts/spec_markdown_template.md`.
3. Convert the Markdown into a compiled-spec JSON draft using `prompts/markdown_to_json_compilation.txt`.
4. Resolve ambiguity and produce a final compiled spec that validates against [compiled-spec-schema.json](./schemas/compiled-spec-schema.json).
5. Only after explicit user approval, detect the target repository language/framework and generate failing tests directly in that native test stack.

## Safety and trust requirements

- Do not write or modify target-repository files without explicit user confirmation.
- Do not treat unresolved ambiguity as acceptable; keep clarifying until completion criteria are met.
- If schema validation fails, return to clarification and repair the spec.

## Outputs

- `compiled-spec.json` (schema-valid)
- Failing test suite generated in the target repository's existing language/framework
- Agent-optimized Markdown handoff summary

See [instructions.md](./instructions.md) for strict execution details.