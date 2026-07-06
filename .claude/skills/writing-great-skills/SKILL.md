---
name: writing-great-skills
description: Reference for writing and editing skills well — the vocabulary and principles that make a skill predictable.
disable-model-invocation: true
---

# Writing Great Skills

Installed from [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-great-skills)
as the house standard for authoring skills in this repo.

## Core principle

A skill exists to wrangle determinism out of a stochastic system. **Predictability** — the agent taking
the same *process* every run, not producing the same output — is the root virtue. Every rule below serves it.

## Invocation

A skill is either model-invoked or user-invoked. The choice trades context load against cognitive load.

**Model-invoked** — the agent can discover it autonomously, other skills can reach it, users can type it.
Its description sits in context every turn (context load). Mechanics: omit `disable-model-invocation`;
write a model-facing description rich in trigger language ("Use when the user wants…, mentions…").

**User-invoked** — the description is stripped from the agent's reach; only manual invocation fires it,
and no other skill can reach it. Zero context load, but the user must remember it exists (cognitive load).
Mechanics: set `disable-model-invocation: true`; the description becomes a one-line human summary with no
trigger list.

**Rule:** choose model-invocation only when the agent must reach the skill autonomously or another skill
needs access. Otherwise make it user-invoked to avoid paying context load. When user-invoked skills grow
past what a person can remember, add one **router** skill that names the others with their triggers.

## Writing the description

A model-invoked description does two jobs: state what the skill does, and list the branches that trigger it.

- Front-load the skill's leading word — the first word carries invocation power.
- One trigger per branch; collapse synonyms that describe the same branch.
- Cut identity already stated in the body; keep the description to triggers and "when another skill needs…" reach clauses.

## Information hierarchy — the ladder

Skills mix two content types freely: **steps** (ordered actions) and **reference** (facts consulted on demand).
Rank material by how immediately the agent needs it:

1. **In-skill step** — ordered actions in SKILL.md. Each step ends with a **completion criterion**: a
   checkable, exhaustive condition that signals the step is genuinely done. Vague criteria invite premature
   completion.
2. **In-skill reference** — definitions, rules, and facts in SKILL.md, consulted on demand. Flat peer-sets
   are fine; an all-reference skill (like this one) is a valid shape.
3. **External reference** — reference in sibling files reached via context pointers, loaded on demand.

**Legwork:** demanding completion criteria drive thorough investigation whether or not steps exist.

**Progressive disclosure:** move detail *down* the ladder (SKILL.md → linked files) to keep the top legible.
Inline what every branch needs; push behind a pointer what only some branches reach. The *pointer's wording*
— not the target file — determines whether the agent reliably reaches the material.

**Co-location:** keep a concept's definition, rules, and caveats under one heading.

## When to split

Granularity spends load. Split only for one of two reasons:

1. **By invocation** — break off a model-invoked skill when a distinct leading word should trigger
   independently, or another skill must reach it. You pay the always-loaded description's context cost.
2. **By sequence** — hide post-completion steps when their visibility tempts the agent to rush the current
   step. Concealing future work encourages thorough legwork now.

## Pruning

- Keep a single source of truth per meaning — one authoritative place to change it.
- Check every line: does it change behavior versus the model's default? Delete whole sentences that fail
  the test, not partial trims. Be aggressive.

## Leading words

A leading word is a compact concept from pretraining that the agent thinks *with* during execution
(e.g. *lesson*, *fog of war*, *tracer bullets*). Repeated through the text, it accumulates a distributed
definition and anchors behavior cheaply. It serves predictability twice: in the body it anchors execution
(consistent behavior per word); in the description it anchors invocation (shared language fires the skill).

- Collapse restated qualities into one word ("fast, deterministic, low-overhead" → "tight").
- Convert fuzzy gates into observable states ("a loop you believe in" → "red").

## Failure modes

- **Premature completion** — ending a step before it is truly done. Defend first by sharpening the
  completion criterion (cheap); only if the criterion stays irreducibly fuzzy and you observe rushing, hide
  post-completion steps via a sequence split.
- **Duplication** — the same meaning in several places. Costs maintenance and tokens, and inflates the
  idea's apparent prominence.
- **Sediment** — stale layers left by the bias toward adding over deleting. Cured by pruning discipline.
- **Sprawl** — the skill is too long despite unique content. Cured by disclosure behind pointers and
  branch/sequence splitting.
- **No-op** — a line the model would obey by default. Fix a weak leading word ("be thorough" → "relentless")
  rather than the technique.
- **Negation** — prohibitions can backfire, because naming the undesired behavior raises its availability.
  Prompt the positive target; use prohibitions only as hard guardrails, always paired with the positive
  alternative.
