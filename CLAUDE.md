# CLAUDE.md

This file orients Claude (and any AI agent) working in this repo.

## Project context

> Update this section as the project takes shape. Keep it under 10 lines.

- **What it does:** TBD
- **Who uses it:** TBD
- **Stack:** Python 3.12+, uv, pytest, ruff
- **Status:** WIP

## Documentation strategy

This project follows the **three-type documentation model**:

| Type | Location | Lifecycle |
|------|----------|-----------|
| PRD (product requirements) | `docs/prd/` | Living — keep current |
| Design (technical design) | `docs/design/` | Living — keep current |
| ADR (decisions) | `docs/decisions/` | Append-only — never modify |
| Research (snapshots) | `docs/research/` | Frozen — date in filename |

**Always start by reading `docs/README.md`** — it indexes everything in `docs/`.

## Operating rules in this repo

- **Read before editing**: when changing code in `src/`, scan related docs first. The "why" lives there, not in the code.
- **Update living docs**: after non-trivial changes to `src/`, update the matching `docs/prd/*.md` or `docs/design/*.md` and bump the `Last verified` line.
- **New decisions get an ADR**: any choice that someone might second-guess later (library choice, schema design, deprecation) → write `docs/decisions/adr-NNN-{topic}.md`. Never edit an Accepted ADR; supersede it instead.
- **Read superseded ADRs too**: when researching past decisions, include superseded ones — they often hold the constraints that shaped the current state.
- **No real secrets in `.env.example`** — only placeholders. Real values go in `.env` (gitignored).

## Workflow expectations

1. Understand before changing — read `docs/`, then `src/`, then write code.
2. For non-trivial features: write/update PRD + Design first, get user confirmation, then implement.
3. TDD where it fits: failing test → implementation → green → refactor.
4. Verify locally before reporting done — run `uv run pytest` and start any servers the change affects.

## Project-specific notes

> Add anything Claude needs to know that isn't obvious from the code:
> - Long-running services, deployment targets
> - Domain-specific terminology
> - External integrations and where their docs live
> - Known quirks or gotchas
