# SpecOps

SpecOps is an Agent Skill for converting ambiguous product requirements into a machine-enforceable contract before implementation starts.

The workflow is markdown-first:
1. Start with a feature spec in Markdown.
2. Have the LLM convert Markdown into Compiled Spec JSON.
3. Run adversarial clarification until ambiguity is removed.
4. Instruct the LLM to generate failing tests directly in the target repository using its native language/framework.

![](assets/info.png)

## What This Skill Produces

- A validated `compiled-spec.json` contract
- Failing tests generated in the target repository's existing test stack
- A cleaner handoff to coding agents (implement to satisfy tests)

## Repository Layout

- Skill manifest: [specops/SKILL.md](specops/SKILL.md)
- Runtime workflow: [specops/instructions.md](specops/instructions.md)
- Prompt assets: [specops/prompts/](specops/prompts/)
- JSON schema: [specops/schemas/compiled-spec-schema.json](specops/schemas/compiled-spec-schema.json)
- Examples:
	- Markdown input: [specops/examples/spec-markdown.example.md](specops/examples/spec-markdown.example.md)
	- JSON output target shape: [specops/examples/compiled-spec.example.json](specops/examples/compiled-spec.example.json)

## Prerequisites

- Agent environment that supports Agent Skills (loads `SKILL.md`)
- Permission to read and write files in the target repository

## Detailed Step-by-Step Usage

### Step 1: Activate SpecOps in your agent session

Tell your agent to use SpecOps for requirements compilation, for example:

```text
Use the SpecOps skill for this feature. Start from Markdown spec, compile JSON, clarify ambiguities, then generate failing tests in this repo's native test framework.
```

The agent should follow [specops/instructions.md](specops/instructions.md).

### Step 2: Create the input Markdown spec

Use [specops/prompts/spec_markdown_template.md](specops/prompts/spec_markdown_template.md) as the required format.

Minimum required sections:
- `Feature`
- `Objective`
- `Actors`
- `Scenarios` (with `Given`, `When`, `Then`)
- `Error and Edge Behavior`
- `Data Models`

If you already have notes/bullets/prose, provide them and instruct the agent to normalize into the template before continuing.

### Step 3: Confirm the Markdown source of truth

Before compiling JSON, ensure the agent confirms:
- the Markdown version to use
- unresolved unknowns it detected
- any assumptions added during normalization

Recommended prompt:

```text
Confirm the normalized Markdown spec first. Then compile it into SpecOps JSON draft.
```

### Step 4: Convert Markdown to Compiled Spec JSON draft

The agent should use [specops/prompts/markdown_to_json_compilation.txt](specops/prompts/markdown_to_json_compilation.txt).

Expected behavior:
- output JSON only
- map scenarios into `scenarios[]`
- map actors into `actors[]`
- map data model fields into `dataModels`
- keep conservative placeholders only when required for structure

### Step 5: Run adversarial clarification loop

The agent should iterate with:
- ambiguity checklist: [specops/prompts/ambiguity_checklist.txt](specops/prompts/ambiguity_checklist.txt)
- question templates: [specops/prompts/clarification_question_templates.txt](specops/prompts/clarification_question_templates.txt)

The loop continues until all completion gates are satisfied:
- no missing `Given/When/Then`
- explicit actor boundaries
- explicit unauthorized/error behaviors
- explicit field constraints where needed
- no contradictions

### Step 6: Compile final JSON and validate shape

The agent should use [specops/prompts/final_spec_formatter.txt](specops/prompts/final_spec_formatter.txt) to produce final JSON that conforms to:

- [specops/schemas/compiled-spec-schema.json](specops/schemas/compiled-spec-schema.json)

Save this as your working contract (for example `compiled-spec.json` in your target repository).

### Step 7: Generate failing tests from compiled spec

Use repo-aware test generation instructions in [specops/prompts/repo_aware_test_generation.txt](specops/prompts/repo_aware_test_generation.txt).

The LLM must:
- detect the repository's language and test framework from repo evidence
- reuse existing test conventions (paths, naming, assertion style, fixtures)
- create failing tests for each scenario in the compiled spec
- avoid implementation code changes in this phase

Recommended prompt:

```text
Generate failing tests from the compiled spec in this repository's existing test framework. Detect the stack from the repo and follow local test conventions.
```

### Step 8: Review generated artifacts

Confirm all artifacts match the final contract:
- scenario coverage in tests
- status/error behavior representation

If mismatched, fix the Markdown/JSON spec first, then regenerate.

### Step 9: Handoff to coding agent

When spec and generated artifacts are accepted:
- commit/publish the compiled spec and failing tests
- assign coding agent to make tests pass
- require implementation PR to preserve contract semantics

## Recommended Operator Prompts (Copy/Paste)

```text
Use SpecOps. Start with Markdown spec only. If my input is rough notes, normalize it to the SpecOps markdown template and ask me to confirm.
```

```text
Now convert the confirmed Markdown spec into compiled-spec JSON draft using the SpecOps markdown-to-json compilation prompt.
```

```text
Run the adversarial clarification loop until no ambiguity remains, then produce final schema-valid compiled-spec JSON.
```

```text
After I approve file writes, detect this repository's stack and generate failing tests from the compiled spec using the existing test framework.
```

## Common Pitfalls

- Skipping Markdown confirmation before JSON conversion
- Generating artifacts from an unvalidated or incomplete JSON draft
- Letting ambiguous actor permissions remain unresolved
- Forcing Jest/PyTest when the target repository uses a different language/framework
- Treating generated tests as implementation (they are intentionally failing)

## Skill Manifest

See [specops/SKILL.md](specops/SKILL.md) for activation guidance and [specops/instructions.md](specops/instructions.md) for execution details.