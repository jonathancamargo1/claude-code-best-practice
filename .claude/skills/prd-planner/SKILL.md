---
name: prd-planner
description: Turn a GO'd feature into a PRD, break it into shippable milestones, and write a build-ready prompt per milestone. Use when the user has a RESEARCH.md or an approved feature and wants to plan it, scope it, spec it, or produce milestones — the Plan stage after research-gate, before implementation.
argument-hint: "<path to a RESEARCH.md, or a feature description>"
allowed-tools:
  - AskUserQuestion
  - Read
  - Write
  - Glob
  - Grep
---

# prd-planner

Turn an approved feature into a **PRD**, a set of shippable **milestones**, and one **build-ready prompt**
per milestone. This is the **Plan** stage of `Research → Plan → Execute → Review → Ship` — it consumes a
`research-gate` GO and hands each milestone prompt to the Execute stage.

Two words govern every run. **Lock**: advance one decision at a time and confirm it before the next — a
locked phase is an input the later phases build on, so never re-open it silently. **What, not how**: the PRD
states user-facing functionality, flows, scope, and required data; it names the stack and integration
providers but never prescribes code, libraries beyond the stack name, algorithms, or internal patterns.

Run the phases in order. Each ends with a **Done when** criterion — advance only once it holds. Drive
discrete choices with `AskUserQuestion` (tappable options) and defaults-first proposals; use free-form chat
only for brain dumps, names, and descriptions. Propose a sensible default with one line of reasoning, then
ask to confirm or edit — never open-ended generation.

## INGEST

Read the source of truth. If `$1` is a `RESEARCH.md` (or one exists beside the target), read it and carry
forward its Problem Frame, chosen approach, sub-goals, code grounding, and constitution constraints — these
are already locked; do not re-litigate them. If there is no RESEARCH.md, capture a brain dump instead, and
note that the feature skipped the Research gate.

**Done when:** the problem frame, the chosen approach, and the known constraints are in hand — sourced from a
RESEARCH.md, or captured as a brain dump with the skipped-gate noted.

## SCOPE

Propose 4–8 headline in-scope features, then propose the likely v1 out-of-scope cuts. Lock each list with a
confirmation. The out-of-scope list is a feature of the PRD, not an afterthought — explicit exclusions are
what keep v1 finite.

**Done when:** the in-scope headline list and the explicit out-of-scope list are both confirmed.

## STACK

Detect and confirm the tech stack and any starter template (what the starter already provides is out of the
build). Then, per feature that needs an external service, name the **provider** and the **credential** it
requires — provider names only, no integration code.

**Done when:** the stack is named, and every feature needing an external service has a named provider and its
required credential.

## MODEL

Propose the data model in plain language: entities, their fields, and the relationships between them. No
schemas, no types, no migrations — the *inventory* of things the product remembers and how they connect.

**Done when:** entities, fields, and relationships are listed and confirmed.

## DETAIL

For each in-scope feature, lock its user-facing in-scope and out-of-scope details — sequentially, one feature
at a time. Stay on the what-not-how side of the line: flows and behavior, not implementation.

**Done when:** every in-scope feature has its user-facing scope locked.

## SLICE

Break the work into ordered milestones. Propose a default sequence plus one or two alternatives, then lock
names and scope. A milestone is a **vertical slice**: independently shippable, demoable on its own, and
ordered so the first proves the riskiest assumption early.

**Done when:** milestones are named and ordered, each maps to a subset of the locked features, and the first
is independently shippable.

## WRITE

Emit the artifacts. Default to Markdown; offer a single-file HTML PRD as well if the reader is non-technical.
Follow the two templates exactly:

- **PRD** → `<feature-dir>/PRD.md` — outline in `steps/prd-template.md`.
- **Per milestone** → `<feature-dir>/milestones/N-{slug}/prompt.md` — outline in `steps/milestone-prompt.md`.

Each milestone prompt is **build-ready**: it restates only the slice's scope, the relevant data model and
integrations, and its acceptance criteria — enough that the Execute stage can build the slice without
re-reading the whole PRD.

**Done when:** `PRD.md` exists with every template section, and one `prompt.md` exists per milestone, each
carrying its own scope and acceptance criteria. Hand the first milestone prompt to the Execute stage.

## Provenance

The phased-interview shape — sequential locked decisions, defaults-first, the what-not-how boundary, and the
PRD + milestones + per-milestone prompt output — is adapted from
[buildermethods/bm-prd-creator](https://github.com/buildermethods/bm-skills/tree/main/plugins/bm-prd-creator)
by Brian Casel, retargeted from non-technical builders to an engineering audience and chained onto
`research-gate`'s GO/NO-GO gate.

## Notes

- Where a RESEARCH.md exists, its locked decisions are inputs — surface a contradiction rather than silently re-deciding it.
- This interview consumes real context; suggest `/compact` before the Execute stage.
