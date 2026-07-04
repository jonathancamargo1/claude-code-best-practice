---
name: improve-report
description: Render one iteration record and append it to the IMPROVE.md ledger, updating best_so_far. Invoked by the /improve orchestrator at PHASE 7 (MERGE + LOG).
user-invocable: false
allowed-tools:
  - "Read"
  - "Edit"
---

# Improve Report Renderer

Invoked on-demand at **PHASE 7** to record an iteration in the append-only `IMPROVE.md` ledger.
This is the memory half of the loop — improvement accrues here, not in raw transcript carryover.

## Task

1. **Read** `IMPROVE.md` to get the current `best_so_far`.
2. **Append** a new iteration record (schema below) under the `## Iterations` section.
3. **Update `best_so_far`** IFF this iteration's `total_score` strictly exceeds the recorded best AND
   its verdict is not `REJECTED`. Record `iter`, `total_score`, and the `worktree_ref`.
4. **Never rewrite** prior iteration records — the ledger is append-only so regressions stay auditable.

## Iteration Record Schema

```yaml
- iter: <N>
  phase_state: "[x][x][x][x][!][x][x]"      # the 7 phase markers
  verdict: NEEDS REVISION
  scores: { correctness: 7, security: 9, simplicity: 5, edge_cases: 6 }
  total_score: 27                            # note vs best_so_far — flag REGRESSION if lower
  findings:
    - { severity: High, loc: "target.md:42", fix: "make the noise threshold numeric" }
  changed_files: ["target.md"]
  validator: "markdown ok / 0 broken links"
  model: { generator: "<snapshot-id>", judge: "<snapshot-id>" }   # pin snapshots, not floating aliases
  cost_usd: 0.83
  cum_cost_usd: 2.41
```

## Rules

- **Pin model snapshots**, not floating aliases — so regressions attribute to the change, not serving variance.
- **cum_cost_usd** is the running total; the `improve-gate.py` PreToolUse hook reads it to enforce the soft budget.
- Only promote a finding to durable "recurring" status after it appears in **≥2 iterations** (±8–14% noise floor).
