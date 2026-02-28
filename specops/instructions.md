# SpecOps Execution Instructions

This file defines how a host agent must run SpecOps.

## Goal

Start from a Markdown specification, convert it into a compiled JSON draft, resolve ambiguity from that JSON state, and generate schema-grounded failing tests in the target repository's native test stack.

## Required behavior

1. Stay in requirements mode until the spec is complete.
2. Require or construct a Markdown spec before JSON compilation.
3. Ask targeted clarifying questions for every unresolved ambiguity.
4. Maintain a working JSON draft state that is progressively refined.
5. Validate the final JSON against `schemas/compiled-spec-schema.json`.
6. Detect repository language/framework before test generation.
7. Ask for explicit confirmation before writing tests into the target repository.

## Workflow

### Phase 1: Initialization

- Briefly explain SpecOps to the user.
- State that you will ask clarifying questions and compile a contract before coding.

### Phase 2: Markdown Spec Ingestion

- Use guidance in `prompts/initial_requirements_gather.txt`.
- Ask the user for a Markdown spec using `prompts/spec_markdown_template.md`.
- If the user provides prose/bullets/docs, transform it into the required Markdown template and ask for confirmation.
- Save the confirmed Markdown as the active source of truth for this run.

### Phase 3: Markdown → JSON Draft Compilation

- Use `prompts/markdown_to_json_compilation.txt` to convert the Markdown spec into a compiled-spec JSON draft.
- The result may still be incomplete or ambiguous; treat it as a working draft.
- Do not generate artifacts yet.

### Phase 4: Adversarial Clarification Loop

Repeat until complete:

1. Evaluate current draft using `prompts/ambiguity_checklist.txt`.
2. Pick highest-risk unresolved ambiguity.
3. Ask one concise, concrete question using patterns from `prompts/clarification_question_templates.txt`.
4. Integrate the user answer into the draft state.
5. Re-check for contradictions introduced by the new answer.

### Phase 5: Completion Gate

Only continue when all of these are true:

- Every scenario has `given`, `when`, and one or more concrete `then` outcomes.
- Actor permissions and boundaries are explicit.
- Error and unauthorized paths are specified.
- Data field constraints are explicit where needed.
- No unresolved contradictions remain.

If any gate fails, continue clarification.

### Phase 6: Final Spec Compilation and Validation

- Use `prompts/final_spec_formatter.txt`.
- Generate a JSON object and validate against `schemas/compiled-spec-schema.json`.
- If invalid, explain validation errors and re-engage the user to repair missing/invalid parts.

### Phase 7: Repo-Aware Test Generation (LLM-driven)

After user approval, generate failing tests directly via the LLM in the target repository.

Use `prompts/repo_aware_test_generation.txt` and follow these rules:

1. Inspect repository signals to detect language/framework:
	- manifests (`package.json`, `pyproject.toml`, `pom.xml`, `go.mod`, etc.)
	- existing test directories/files
	- CI workflows and test commands
2. Prefer existing test framework conventions already present in the repo.
3. If multiple frameworks are possible, ask the user which one to use.
4. Generate failing tests that map `scenarios[]` from the compiled spec.
5. Place tests in idiomatic paths for the detected stack.
6. Do not generate implementation code in this phase.

### Phase 8: Final Handoff

Provide:

- location of compiled spec
- generated test file paths
- concise summary of behavior covered by the generated tests
- suggested next step: assign coding agent to make tests pass

## Invalid-spec fallback

If validation fails and user cannot answer immediately:

1. Save draft marked as incomplete.
2. Save the latest Markdown and JSON draft snapshots.
3. List unresolved items.
4. Ask whether to continue now or pause.

## Large specification handling

When user provides a long external spec:

1. Chunk by functional area.
2. Run checklist per chunk.
3. Merge chunk outputs into one compiled spec.
4. Run final cross-chunk contradiction check.