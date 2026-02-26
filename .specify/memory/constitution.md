<!--
Sync Impact Report
- Version: 1.0.0 → 1.1.0
- Modified Principles:
  - Specification First → Specification First (clarified scope and enforcement)
  - AI-Native Code Generation → Agentic Implementation Only
  - Independent Phase Execution → Phase Isolation & Sequencing
  - Atomic Tasks → Traceable Tasks & Records (expanded to include PHR + task linking)
  - Testable Acceptance Criteria (added explicit measurable language)
  - Immutable Specifications (retained, clarified change control)
- Added Sections:
  - Mandatory Development Workflow
  - Tooling & Automation Standards
- Removed Sections: None
- Templates:
  - .specify/templates/plan-template.md — ✅ Aligned (no change required)
  - .specify/templates/spec-template.md — ✅ Aligned (no change required)
  - .specify/templates/tasks-template.md — ✅ Aligned (no change required)
- Runtime Guidance:
  - README.md — ✅ Updated to reference constitution v1.1.0 and current principles
- Deferred TODOs: None
-->

# Evolution of Todo Constitution

## Core Principles

### Specification First
Every deliverable MUST originate from a ratified Markdown spec stored under `/specs`. No engineering work, research spike, or architectural change may start until the spec is approved and linked to an execution plan.

### Agentic Implementation Only
All code, configuration, and documentation changes MUST be produced through Claude Code following Spec-Kit Plus workflows. Manual editing is prohibited except for approved governance files explicitly listed in a spec.

### Phase Isolation & Sequencing
Implementation happens inside the active phase directory only (`phase-1-console`, `phase-2-webapp`, etc.). Cross-phase dependencies require explicit sign-off and mirrored specs in each affected phase.

### Traceable Tasks & Records
Every action MUST map to a spec section, tracked task, and Prompt History Record (PHR). "No Task = No Code"—if a task does not exist in `tasks.md`, the work cannot begin.

### Testable Acceptance Criteria
Specifications and tasks MUST define measurable outcomes and verification steps (tests, demos, metrics). Plans and implementations have to prove those criteria before marking work complete.

### Immutable Specifications & Controlled Change
Once a spec is ratified, alterations require a new spec revision, re-approval, and updates to plan/tasks artifacts. The "Specify → Plan → Tasks → Implement" loop is mandatory for every change.

## Mandatory Development Workflow
1. Draft spec in `/specs/<feature>/spec.md` with priorities, requirements, and acceptance criteria.
2. Run `/sp.plan` to create research, data model, quickstart, and plan artifacts; ensure the Constitution Check passes.
3. Run `/sp.tasks` to produce dependency-ordered tasks scoped to the feature's user stories.
4. Execute implementation strictly according to tasks, capturing PHRs for each prompt and keeping branches within their phase directories.
5. After completion, update documentation, rerun acceptance tests, and link outcomes back to the original spec sections.

## Tooling & Automation Standards
- Spec-Kit Plus templates are the only source for specs, plans, and tasks; edit templates before generating new artifacts when governance changes.
- Use `uv` for Python environments and dependency management across all phases.
- Any scaffolding (e.g., monorepo layout, governance docs) must be generated via approved skills or scripts under `.claude/skills/`.
- Continuous compliance checks (lint, tests, validations) must be scripted and documented in plan/tasks artifacts.

## Governance
- This constitution supersedes all other project guidance. Conflicts are resolved in favor of the latest version herein.
- Amendments require: (1) written proposal, (2) explicit version bump, (3) propagation to affected templates/docs, and (4) PHR capture.
- Semantic versioning rules apply: MAJOR for breaking governance changes, MINOR for new principles/sections, PATCH for clarifications.
- Compliance reviews occur at spec approval, plan review, task generation, and implementation completion. Any violation halts the workflow until resolved.

**Version**: 1.1.0 | **Ratified**: 2026-01-03 | **Last Amended**: 2026-01-05
