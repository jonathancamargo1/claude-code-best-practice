---
name: research-gate
description: Research and vet a feature to a GO/NO-GO verdict before planning. Use when the user wants to scope, assess feasibility of, or decide whether to build a feature, or when another skill needs a grounded GO/NO-GO gate before /plan.
argument-hint: "<feature description or path to a REQUEST.md>"
allowed-tools:
  - AskUserQuestion
  - Agent
  - Read
  - Grep
  - Glob
  - WebFetch
  - Write
---

# research-gate

Decide whether a feature is worth planning — and leave behind a grounded, auditable `RESEARCH.md` — before
any implementation. This is the **Research** stage of `Research → Plan → Execute → Review → Ship`.

The virtue this skill protects is **predictability**: every run walks the same arc —
**FRAME → DIVERGE → GROUND → CONSULT → CONVERGE** — and ends in a typed verdict. Each stage inherits the
strongest research move from one source framework (see Provenance); the value is the complete arc, which no
single framework walks end to end.

Run the stages in order. Each stage lists a **Done when** criterion — advance only once it holds. Delegate
discovery through `Agent(subagent_type="...", description="...", prompt="...")`; run independent agents
concurrently by issuing their calls in one message. Prefer built-in `Explore`, `Plan`, and `general-purpose`
agents; a subagent cannot spawn another, so every Agent call originates here.

## FRAME

1. Restate the problem, not the solution: one paragraph on *who* hurts and *why now*, with implementation language stripped out.
2. Decompose into 2–5 independent sub-goals.
3. Load the constitution: read `constitution.md`, `PRINCIPLES.md`, `CLAUDE.md`, or `.project/constitution.md` and extract the constraints this feature must honor.

**Done when:** the problem is stated without solution language, sub-goals are listed, and constitution constraints are extracted (or "none found" is recorded).

## CLARIFY

Fire the gate only when the request is ambiguous, contradictory, or under-specified: ask ≤3 questions with
`AskUserQuestion`, then stop and wait. A stable intent is what protects the discovery spend that follows.

**Done when:** the intent is unambiguous — either on arrival, or after the questions are answered.

## DIVERGE

Brainstorm at least two genuinely distinct approaches (e.g. build-from-scratch, reuse-existing,
buy/integrate, defer), naming the trade-off axis for each. Convergence waits for CONVERGE.

**Done when:** ≥2 named approaches exist, each with its trade-off axis.

## GROUND

Judgment rests on citable reality. Run two grounding agents concurrently:

- **CODE** — `Agent(subagent_type="Explore")`: current implementation, integration points, data models, dependencies, reusable components, real constraints. Findings carry `file:line` anchors.
- **DOCS** — `Agent(subagent_type="general-purpose")` with WebFetch: for every external library/API/SDK the feature touches, check the claim against current documentation. An unverified assumption is a finding, recorded as a risk.

**Done when:** CODE findings cite `file:line` for current state, integration points, and reuse; and every external claim is marked verified (with URL) or flagged as a risk.

## CONSULT

Seed three specialist lenses with the FRAME, DIVERGE, and GROUND outputs and run them concurrently. Each
returns a High/Medium/Low score plus concerns:

| Lens | Judges | Anchored in |
|---|---|---|
| Product | user value, market fit, constitution alignment | FRAME + constitution |
| Engineering | feasibility, complexity, tech-debt, risks | GROUND/CODE |
| Strategy | risk vs. reward, build/buy/partner/defer | all of the above |

**Done when:** all three lenses have returned a score and their concerns.

## CONVERGE

Synthesize into one typed verdict, then write the artifact.

Verdict — emit exactly this shape:

```yaml
decision: GO | CONDITIONAL GO | DEFER | NO-GO
confidence: High | Medium | Low
scores: { product: High|Medium|Low, engineering: High|Medium|Low, strategy: High|Medium|Low }
chosen_approach: "<one named DIVERGE candidate>"
conditions: [ "<prereq>", ... ]     # populated only for CONDITIONAL GO
top_risks:
  - { risk: "<risk>", evidence: "file:line or doc URL", mitigation: "<action>" }
rationale: "<2–3 sentences>"
```

Then write `RESEARCH.md` beside the target (`research/RESEARCH.md` for an RPI feature folder, else
`<target-dir>/RESEARCH.md`) with these sections: Executive Summary · Problem Frame · Candidate Approaches ·
Code Grounding · Docs Grounding · Specialist Consultation · Verdict (the YAML above) · Next Steps.

**Done when:** the verdict is emitted and `RESEARCH.md` exists with all eight sections. A GO hands off to the
Plan stage — planning is out of scope here.

## Provenance

Each stage inherits one framework's strongest research move. The complete arc is the point.

| Stage | Fused move | Source |
|---|---|---|
| FRAME | problem-not-solution + goal decomposition + constitution | BMAD · oh-my-claudecode · Spec Kit |
| CLARIFY | explicit clarifying questions, stop-and-ask | Spec Kit `/clarify` · RPI |
| DIVERGE | ≥2 approaches before converging | Superpowers · Compound Engineering |
| GROUND / CODE | grounding in the actual codebase | HumanLayer · OpenSpec · RPI |
| GROUND / DOCS | verify claims against real docs | Matt Pocock `/grill-with-docs` |
| CONSULT | multi-lens specialist panel | gstack `/office-hours` · RPI |
| CONVERGE | GO/NO-GO verdict + RESEARCH.md | RPI · Get Shit Done |

## Notes

- Where a repo defines richer specialists (product-manager, senior-software-engineer, technical-cto-advisor), prefer them for CONSULT.
- This pipeline consumes real context; suggest `/compact` before the Plan stage.
