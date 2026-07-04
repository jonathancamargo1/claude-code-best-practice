---
name: improve-rubric
description: Preloaded scoring rubric and typed-verdict schema for the self-improving harness. Preloaded into the adversarial-judge agent; not directly invocable.
user-invocable: false
disable-model-invocation: true
---

# Improve Rubric & Verdict Schema

This skill is **preloaded** (via the agent `skills:` field) into `adversarial-judge` so the current
rubric is always in context at startup. It defines HOW to score a candidate and the EXACT shape of the
verdict the judge must return.

## Default Rubric Dimensions

Override these only when the caller supplies a `RUBRIC SOURCE`. Every dimension needs file:line evidence.

| Dimension | Rating | Evidence required |
|---|---|---|
| Correctness / spec-conformance | Aligned · Partial · Misaligned + 0–10 | file:line + real validator output |
| Security / safety | Aligned · Partial · Misaligned + 0–10 | file:line |
| Simplicity / maintainability | Aligned · Partial · Misaligned + 0–10 | file:line |
| Edge-case & completeness | Aligned · Partial · Misaligned + 0–10 | file:line |

`total_score` = sum of the four 0–10 dimension scores (0–40).

## Typed Verdict (return EXACTLY this shape)

```yaml
verdict: APPROVED | APPROVED WITH CONDITIONS | NEEDS REVISION | REJECTED
scores: { correctness: <0-10>, security: <0-10>, simplicity: <0-10>, edge_cases: <0-10> }
total_score: <0-40>
findings:
  - severity: Blocker | High | Medium
    location: "path/to/file.md:LINE"
    finding: "<what is wrong, grounded in the actual text>"
    fix: "<specific, actionable change — not 'improve this'>"
summary: "<one-sentence overall judgment>"
```

## Verdict → Gate mapping

- `APPROVED` + zero Blocker/High + validator passes → **DRY exit**, merge.
- `APPROVED WITH CONDITIONS` + no Blocker/High + iter ≥ 2 → **merge best-so-far**, report open Mediums.
- `NEEDS REVISION` → route findings to `fix-applier`, loop.
- `REJECTED` (any Blocker) → discard candidate worktree; if a Blocker survives 2 alternative fixes → escalate.

## Discipline

- **Additive, not destructive:** ADD a Critique; never rewrite the generator's work — preserve provenance.
- **Grounded in executed reality:** cite real validator output; ungrounded critique → confident-but-wrong fixes.
- **Noise-aware:** run-to-run variance is ±8–14%; a `total_score` delta < 1.0 point across 2 iters is noise → recommend stop, do NOT invent findings to justify another loop.
