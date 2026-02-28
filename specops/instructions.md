# SpecOps Execution Instructions

This file defines how a host agent must run SpecOps.

## Goal

Convert an initial, possibly vague feature request into a compiled, schema-valid contract and optional generated artifacts.

## Required behavior

1. Stay in requirements mode until the spec is complete.
2. Ask targeted clarifying questions for every unresolved ambiguity.
3. Maintain a working draft state that is progressively refined.
4. Validate the final JSON against `schemas/compiled-spec-schema.json`.
5. Ask for explicit confirmation before running any write-capable script.

## Workflow

### Phase 1: Initialization

- Briefly explain SpecOps to the user.
- State that you will ask clarifying questions and compile a contract before coding.

### Phase 2: Requirement Ingestion

- Use guidance in `prompts/initial_requirements_gather.txt`.
- Accept bullets, user stories, raw prose, or pasted docs.
- Normalize user input into a temporary structure:
  - feature name
  - actors
  - scenarios
  - data model constraints
  - error/edge behavior

### Phase 3: Adversarial Clarification Loop

Repeat until complete:

1. Evaluate current draft using `prompts/ambiguity_checklist.txt`.
2. Pick highest-risk unresolved ambiguity.
3. Ask one concise, concrete question using patterns from `prompts/clarification_question_templates.txt`.
4. Integrate the user answer into the draft state.
5. Re-check for contradictions introduced by the new answer.

### Phase 4: Completion Gate

Only continue when all of these are true:

- Every scenario has `given`, `when`, and one or more concrete `then` outcomes.
- Actor permissions and boundaries are explicit.
- Error and unauthorized paths are specified.
- Data field constraints are explicit where needed.
- No unresolved contradictions remain.

If any gate fails, continue clarification.

### Phase 5: Spec Compilation

- Use `prompts/final_spec_formatter.txt`.
- Generate a JSON object and validate against `schemas/compiled-spec-schema.json`.
- If invalid, explain validation errors and re-engage the user to repair missing/invalid parts.

### Phase 6: Artifact Generation

After user approval, run one or more scripts in `scripts/generators/` with `--spec <compiled-spec.json>`:

- `generate_jest.js`
- `generate_pytest.py`
- `generate_openapi.py`

Each script writes files and should be treated as filesystem-modifying.

### Phase 7: Final Handoff

Provide:

- location of compiled spec
- generated artifact file paths
- concise summary of behavior covered by the generated tests
- suggested next step: assign coding agent to make tests pass

## Invalid-spec fallback

If validation fails and user cannot answer immediately:

1. Save draft marked as incomplete.
2. List unresolved items.
3. Ask whether to continue now or pause.

## Large specification handling

When user provides a long external spec:

1. Chunk by functional area.
2. Run checklist per chunk.
3. Merge chunk outputs into one compiled spec.
4. Run final cross-chunk contradiction check.