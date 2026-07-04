# IMPROVE.md — Self-Improving Harness Ledger

Append-only ledger for the `/improve` harness. This is the **memory half** of the loop: improvement
accrues here, not in raw transcript carryover. Prior records are never rewritten so regressions stay
auditable. See `self-improve-harness-prompt.md` for the full harness design and
`orchestration-workflow/improve-harness.md` for the flow diagram.

## best_so_far

```yaml
best_so_far: { iter: 0, total_score: null, worktree_ref: null }
```

## Iterations

<!-- The improve-report skill appends one record per iteration below this line. Schema:

- iter: <N>
  phase_state: "[ ][ ][ ][ ][ ][ ][ ]"
  verdict: APPROVED | APPROVED WITH CONDITIONS | NEEDS REVISION | REJECTED
  scores: { correctness: 0, security: 0, simplicity: 0, edge_cases: 0 }
  total_score: 0
  findings:
    - { severity: High, loc: "file.md:LINE", fix: "..." }
  changed_files: []
  validator: "markdown ok / 0 broken links"
  model: { generator: "<snapshot-id>", judge: "<snapshot-id>" }
  cost_usd: 0.00
  cum_cost_usd: 0.00
-->
