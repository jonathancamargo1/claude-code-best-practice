# PRD Template

Outline for `<feature-dir>/PRD.md`. Fill every section from the locked phases — no placeholders left behind.
Stay on the **what, not how** side of the line throughout: user-facing functionality, never implementation.

```markdown
# PRD — <Feature Name>

## Core Purpose
<1–3 sentences: what we're building and for whom. Lifted from the RESEARCH.md Problem Frame.>

## In Scope
<The locked headline feature list — 4–8 bullets, each one user-facing capability.>

## Out of Scope (v1)
<The explicit exclusions. What we are deliberately NOT building yet, and why.>

## Tech Stack
<Stack name only (e.g. Rails + React). What the starter template already provides.>

## Integrations
| Feature | Provider | Credential required |
|---|---|---|
| <feature> | <e.g. OpenAI> | <e.g. API key> |

## Data Model
<Entities, their fields, and relationships — in plain language. The inventory of what the product remembers.>

- **<Entity>** — <fields> · relates to <entity> (<relationship>)

## Features in Detail
<Per in-scope feature: user-facing in-scope behavior and out-of-scope details. Flows, not code.>

### <Feature>
- **In scope:** <user-facing behavior, flows, states>
- **Out of scope:** <what this feature will NOT do in v1>

## Milestones
<Ordered vertical slices. Each independently shippable; the first proves the riskiest assumption.>

1. **<N-slug>** — <scope: which features / partial features this slice delivers>

## Source
<Link to the RESEARCH.md this PRD was planned from, or "brain dump — Research gate skipped".>
```

Notes:
- If the reader is non-technical, additionally render a single-file HTML version with the same scope and voice — presentation only; the what-not-how boundary is identical across formats.
- The Milestones section here is the summary; each slice's build-ready detail lives in its own `milestones/N-{slug}/prompt.md` (see `milestone-prompt.md`).
