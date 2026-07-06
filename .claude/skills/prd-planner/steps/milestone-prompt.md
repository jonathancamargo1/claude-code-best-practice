# Milestone Prompt Template

Outline for `<feature-dir>/milestones/N-{slug}/prompt.md`. One per milestone. It must be **build-ready**: the
Execute stage should be able to build this slice from this file alone, without re-reading the whole PRD.
Restate only what this slice needs — copy the relevant scope, data model, and integrations down into it.

```markdown
# Milestone N — <Slug>

## Slice Goal
<1–2 sentences: what shipping this slice proves or delivers. Why it is ordered here.>

## In Scope (this slice only)
<The subset of features / partial features this milestone delivers. Nothing beyond it.>

## Out of Scope (deferred to later slices)
<What a builder might assume belongs here but is explicitly a later milestone.>

## Data Model (relevant subset)
<Only the entities/fields/relationships this slice touches. Copied from the PRD, not referenced.>

## Integrations (relevant subset)
<Only the providers + credentials this slice needs.>

## Acceptance Criteria
<Checkable, user-observable conditions that mean this slice is done. One per line.>

- [ ] <observable behavior a user or reviewer can verify>

## Handoff
<What the next milestone can now assume exists. The seam this slice leaves for the next.>
```

Notes:
- Acceptance criteria are user-observable outcomes, not implementation tasks — they are how Execute and Review know the slice is truly done.
- Keep each prompt self-contained: duplication across slices is acceptable here because it removes a dependency on reading the full PRD mid-build.
