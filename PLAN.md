## 1. Executive Summary

This document proposes the development of **SpecOps**, a new capability packaged as an Agent Skill. SpecOps addresses the "Ambiguity Bottleneck" in the Agentic Software Development Lifecycle (SDLC), where vague human requirements lead AI agents to build incorrect features.

SpecOps acts as an **adversarial requirement engineer**. It is a portable skill that any compatible agent can invoke to guide a user through a structured specification process, automatically detecting ambiguity, forcing clarification, and finally generating a suite of machine-enforceable artifacts (failing tests, API schemas). This shifts quality assurance left—from debugging code to refining requirements—and provides a verifiable contract for subsequent coding agents.

## 2. Motivation & Problem Statement

As AI agents become the primary executors of coding tasks, the input to these agents—human language specifications—has become the critical path to quality. Current workflows suffer from:
*   **The Ambiguity Tax:** Engineers and PMs write specifications with implicit assumptions. AI agents confidently implement their own interpretation, leading to incorrect code and costly rework.
*   **Lack of a Verifiable Contract:** There is no intermediate artifact between a natural language spec and the final code that can be used to objectively validate an agent's work.
*   **Context Fragmentation:** Best practices for writing effective agent prompts are not codified or reusable. They exist as tribal knowledge or in disparate documents.
*   **Toolchain Gap:** Existing tools (Jira, Notion, Copilot) handle either human collaboration or code generation, but none actively help *engineer the specification itself* for machine consumption.

An Agent Skill is the ideal delivery mechanism because it places this capability directly within the agent's workflow, is reusable across different agent platforms, and can be versioned and improved independently.

## 3. Proposed Solution: The SpecOps Skill

The SpecOps Skill is a package of instructions, prompt templates, and executable scripts that, when invoked by a host agent, transforms a vague feature request into a "compiled" specification and its corresponding test harness.

### 3.1. Core Principles
*   **Agent-First Workflow:** The entire interaction is managed by the agent, guided by the Skill. The user never leaves their chat interface.
*   **Shift-Left on Validation:** Ambiguity is detected and resolved *before* a single line of implementation code is considered.
*   **"Spec as Code":** The final output is a set of executable artifacts (tests) and structured data (schemas, compiled spec) that live alongside the codebase.
*   **Portability:** The Skill can be used by any agent platform that supports the Agent Skills format.

### 3.2. User Experience (as an Agent-Sided Flow)
1.  **Invocation:** The user asks their agent: *"Let's use the SpecOps skill to define the new user profile editing feature."*
2.  **Guided Requirements Capture:** The agent, following the Skill's instructions, prompts the user for an initial description, encouraging bullet points or user stories.
3.  **Adversarial Clarification Loop:**
    *   The agent analyzes the description against a checklist of ambiguity types (undefined actors, missing error paths, contradictory statements, unspecified edge cases).
    *   It asks targeted, clarifying questions: *"You mentioned 'admins can edit any profile.' What should happen if an admin tries to edit the profile of another admin? Is that allowed?"*
    *   This loop continues until the agent determines the specification is "compiled"—i.e., it has a definitive answer for every scenario in its internal checklist.
4.  **Compilation & Artifact Generation:**
    *   The agent structures the final, unambiguous spec into a predefined JSON format (the **Compiled Spec**).
    *   The agent (or the Skill's scripts) uses this JSON to:
        *   Generate a **failing test suite** (e.g., Jest, PyTest) and commit it to the appropriate repo location.
        *   Generate an **OpenAPI schema** (if applicable).
        *   Produce an **Agent-Optimized Markdown file** summarizing the spec for the next agent.
5.  **Handoff:** The agent informs the user: *"The spec is compiled. I've created a pull request with the failing tests. A coding agent can now be assigned to make these tests pass."*

### 3.3. Skill Architecture

The SpecOps Skill repository would have the following structure:

```
specops-skill/
├── skill.md                 # Skill manifest: name, description, version, author, compatible agent platforms
├── instructions.md          # PRIMARY LOGIC: Detailed guide for the host agent on how to execute the SpecOps workflow.
├── prompts/                 # Reusable prompt fragments for the agent to use
│   ├── initial_requirements_gather.txt
│   ├── ambiguity_checklist.txt      # Instructions on what types of ambiguity to look for
│   ├── clarification_question_templates.txt
│   └── final_spec_formatter.txt      # Prompt to structure the final JSON spec
├── schemas/
│   └── compiled-spec-schema.json     # JSON Schema defining the structure of a "compiled" spec
├── scripts/                  # Executable code for artifact generation
│   ├── generators/           # Language/framework specific generators
│   │   ├── generate_jest.js
│   │   ├── generate_pytest.py
│   │   └── generate_openapi.py
│   └── utils/                # Shared helper functions (e.g., for API calls to GitHub)
└── templates/                # Templates for generated files (e.g., using Jinja or EJS)
    ├── jest.test.template
    ├── pytest.test.template
    └── openapi.yaml.template
```

### 3.4. Key Internal Data Structures

The **Compiled Spec JSON** is the core internal artifact. Its schema (`compiled-spec-schema.json`) is critical. A simplified example:

```json
{
  "specVersion": "1.0",
  "featureName": "User Profile Editing",
  "actors": [
    { "name": "User", "properties": { "isAuthenticated": true, "isProfileOwner": true } },
    { "name": "Admin", "properties": { "isAuthenticated": true, "isAdmin": true } }
  ],
  "scenarios": [
    {
      "id": "SC-001",
      "description": "User edits own profile",
      "given": "Actor is a User and is viewing their own profile",
      "when": "User updates 'name' field to a new valid string",
      "then": [
        "System accepts the update",
        "Database record for that user is updated with new name",
        "System returns success response (200 OK)"
      ]
    },
    {
      "id": "SC-002",
      "description": "Admin edits another user's profile",
      "given": "Actor is an Admin and is viewing the profile of another user",
      "when": "Admin updates the 'bio' field",
      "then": [
        "System accepts the update",
        "Database record for the target user is updated",
        "System returns success response (200 OK)"
      ]
    },
    {
      "id": "SC-003",
      "description": "User edits another user's profile (Unauthorized)",
      "given": "Actor is a User and is viewing the profile of a *different* user",
      "when": "User attempts to update any field",
      "then": [
        "System rejects the update",
        "Database record is unchanged",
        "System returns unauthorized error (403 Forbidden)"
      ]
    }
  ],
  "dataModels": {
    "UserProfile": {
      "fields": {
        "name": { "type": "string", "required": true, "maxLength": 100 },
        "bio": { "type": "string", "required": false, "maxLength": 500 }
      }
    }
  }
}
```

## 4. Detailed Design & Workflow

The host agent's execution of the `instructions.md` file is the heart of the system.

1.  **Initialization:** Agent loads the Skill and presents its purpose to the user.
2.  **Requirement Ingestion:** Agent uses `prompts/initial_requirements_gather.txt` to ask the user for an initial description. It can accept plain text, bullet points, or even a link to a document.
3.  **Iterative Clarification:**
    *   Agent enters a loop. It uses `prompts/ambiguity_checklist.txt` to analyze the current requirement set.
    *   For each potential ambiguity found (e.g., missing "given" state for a scenario), it selects a question from `prompts/clarification_question_templates.txt`, personalizes it, and asks the user.
    *   The user's answers are incorporated. The agent maintains a working state of the specification.
    *   The loop ends when the agent determines the spec fully satisfies the checklist.
4.  **Spec Compilation:** The agent uses `prompts/final_spec_formatter.txt` to convert its internal state into a JSON object that strictly validates against `schemas/compiled-spec-schema.json`.
5.  **Artifact Generation:**
    *   The agent (or a user-approved script execution) runs the relevant generator scripts from `scripts/generators/`, passing the `compiled-spec.json` as input.
    *   These scripts use the `templates/` to output the final test files and schemas.
    *   The scripts can be designed to write files directly to the user's filesystem (via agent capabilities) or to interact with Git (e.g., create a new branch and commit).
6.  **Final Output:** The agent presents the user with a summary of what was generated and where. The final Agent-Optimized Markdown summary is also produced for the next step in the pipeline.

## 5. Alternatives Considered

*   **Standalone Web Application:** Rejected. This would create context-switch friction and wouldn't leverage the agent's existing conversational interface and access to the user's environment.
*   **IDE Plugin:** Rejected. This ties the capability to a specific editor, reducing portability and reach. It also doesn't integrate with the agentic workflow itself.
*   **A simple, static Prompt Template:** Rejected. Without the structured output schema and scriptable generation components, a static prompt cannot reliably produce complex, multi-file artifacts like test suites.

## 6. Adoption & Integration Plan

*   **Initial Target:** We will initially develop and test the Skill against a single, well-documented agent platform that supports the Agent Skills format (e.g., the reference implementation mentioned on agentskills.io).
*   **Skill Distribution:** The Skill will be published in a public registry or repository, making it discoverable by users of compatible agents.
*   **Iterative Refinement:** We will release the Skill as "beta" and gather feedback on the `instructions.md` clarity and the robustness of the generator scripts. The ambiguity checklist will be continuously expanded based on real-world user scenarios.
*   **Community Building:** We will encourage contributions to the Skill's prompts and generators to support more programming languages, testing frameworks, and domain-specific ambiguity patterns.

## 7. Open Questions

*   **How is user trust and security managed when the Skill's scripts write to the filesystem?** The Skill's instructions should mandate that the agent asks for explicit user confirmation before executing any script that modifies the local environment or pushes to a repository.
*   **What is the fallback if the compiled spec JSON is invalid?** The Skill should include validation steps and instruct the agent on how to correct issues by re-engaging the user.
*   **How are large, pre-existing specs handled?** The initial workflow assumes a conversational start. We need a mechanism for the user to paste a large document and have the agent parse and apply the ambiguity checklist to it in chunks.
*   **How can the Skill be tested itself?** We need a strategy for unit-testing the generator scripts and for simulating the agent interaction to validate the `instructions.md` logic.
