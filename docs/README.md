# Documentation

This folder is the project's memory. When code answers *what*, docs answer *why*.

## Three-type model

| Type | Folder | Lifecycle | When to write |
|------|--------|-----------|---------------|
| **PRD** | `prd/` | Living | Before building a feature — captures user intent and acceptance criteria |
| **Design** | `design/` | Living | Before/during implementation — captures architecture and Mermaid diagrams |
| **ADR** | `decisions/` | **Append-only** | Whenever a choice is non-obvious — library, schema, deprecation |
| **Research** | `research/` | Frozen snapshot | Investigations, competitive analysis, "as of date X" findings |

> **Living docs** must stay in sync with code. Update the `Last verified` line at the top after touching related code.
> **Append-only docs** (ADRs) are never modified once Accepted. To reverse a decision, write a new ADR that "Supersedes" the old one.
> **Snapshots** carry their date in the filename and are never updated — write a new dated snapshot if needed.

## Index

> Update this index whenever a doc is added, renamed, or superseded.

### PRD

_(none yet — design doc captures product intent; formalize as separate PRD if scope expands)_

### Design

_(none yet — see `design/TEMPLATE.md`)_

### ADRs

_(none yet — see `decisions/TEMPLATE.md`)_

### Research

_(none yet)_

## Conventions

- **Filenames:** kebab-case. PRD/Design use feature names (`prd-checkout.md`); ADRs use sequential numbering (`adr-0001-use-postgres.md`); Research uses topic + date (`research-payment-providers-2026-05-03.md`).
- **First line of every doc:** `# {Type}: {Title}`
- **Living docs** start with: `> Last verified: YYYY-MM-DD (commit <hash>)`
- **ADRs** start with: `Status:`, `Date:`, optional `Supersedes:` / `Superseded-by:`

## When NOT to write a doc

- Trivial bug fixes
- One-line typo / rename PRs
- Throwaway exploratory spikes (mark them as such in commit message instead)

For everything else above the trivial line, write the doc. With AI doing most reading and writing, the cost is low — the cost of *not* having the record is high.
