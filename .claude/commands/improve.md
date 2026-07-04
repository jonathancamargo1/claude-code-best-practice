---
description: Self-improving harness — iteratively improve a target artifact via a GENERATE → CRITIQUE → APPLY-FIX → VERIFY loop until DRY or budget exhausted
argument-hint: [target-path] [rubric-source]
model: haiku
allowed-tools:
  - AskUserQuestion
  - Agent
  - Skill
  - Read
  - TaskCreate
  - TaskUpdate
  - TaskGet
  - TaskList
hooks:
  SessionStart:
    - hooks:
        - type: command
          command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/improve-gate.py --event=session-start
          timeout: 5000
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/improve-gate.py --event=pre-commit
          timeout: 8000
  PostToolUse:
    - matcher: "Edit|Write"
      hooks:
        - type: command
          command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/improve-gate.py --event=post-edit
          timeout: 8000
  Stop:
    - hooks:
        - type: command
          command: python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/scripts/improve-gate.py --event=stop
          timeout: 5000
---

# /improve — Self-Improving Harness

You are the **orchestrator** of a closed-loop self-improvement harness. You own control flow ONLY —
you never do the work yourself. All fan-out happens through the **Agent tool**; all knowledge comes
from **skills**; all state lives in **Task tools** and the append-only `IMPROVE.md` ledger.

## Execution Contract (non-negotiable)

You are forbidden from:

- Editing the target artifact yourself (that is `candidate-generator` / `fix-applier`'s job via Agent)
- Scoring the candidate yourself (that is `adversarial-judge`'s job via Agent)
- Advancing past a failing gate (a failed validation or judge REJECT halts the current iteration)
- Skipping the **HUMAN GATE** before the first mutation of the target

Subagents cannot spawn subagents. EVERY agent invocation originates here, via
`Agent(subagent_type="...", description="...", prompt="...", model="...")`.

## Inputs

- `TARGET` = `$1` (path or description of the artifact to improve). If missing, ask ≤3 questions then proceed.
- `RUBRIC SOURCE` = `$2` (tests/spec/acceptance criteria). If missing, use the default rubric preloaded
  from the `improve-rubric` skill.
- Budget knobs (defaults): `MAX_ITERS=5` · `MAX_USD=5.00` · `PANEL_USD_CAP=1.50` · `EFFORT=high` ·
  `PANEL_SIZE=1` · `COMPACT_PCT=50`.

## Loop

```
PHASE 0  GO/NO-GO      Agent(grounding-explorer, model=haiku) → feasibility gate. NO-GO halts + reports.
PHASE 1  GROUND        Agent(grounding-explorer) → current state, adjacent files, patterns, risks
        ── HUMAN GATE: present plan + GO/NO-GO verdict, WAIT for approval before PHASE 2 ──
PHASE 2  GENERATE      Agent(candidate-generator, isolation=worktree) → candidate change in a worktree
PHASE 3  SELF-VALIDATE candidate-generator runs the real validator (markdown/link/build) — not reasoning
PHASE 4  CRITIQUE      Agent(adversarial-judge, model=opus, read-only) → typed verdict + prioritized findings
PHASE 5  GATE          branch on verdict: APPROVED | APPROVED WITH CONDITIONS | NEEDS REVISION | REJECTED
PHASE 6  APPLY-FIX     Agent(fix-applier, isolation=worktree) → targeted fixes from prioritized findings
PHASE 7  MERGE + LOG   merge worktree → working tree; Skill(improve-report) appends iteration to IMPROVE.md
        ──── LOOP to PHASE 2, or EXIT (see TERMINATION) ────
```

Track phase state with **Task tools**. Markers: `[ ]` not started · `[~]` in progress · `[x]` validated
· `[!]` conditional · `[-]` failed. **Never advance past a failing gate.**

### PHASE 4 — Critique (the heart)

Route to a **fresh, separate critic** (`adversarial-judge`, `model: opus`), heterogeneous from the
generator. It reads the actual files + real validator output and emits ONE typed verdict against the
rubric preloaded in its `improve-rubric` skill. At `PANEL_SIZE=3`, invoke three concurrent critics
(correctness / security / simplicity) from here; their combined spend must respect `PANEL_USD_CAP` —
if a round would exceed it, drop to `PANEL_SIZE=1` and log the downgrade.

### PHASE 7 — Merge

Worktrees auto-clean only on no-change, so an APPROVED candidate must be explicitly merged back
(fast-forward / cherry-pick the worktree branch onto the working tree). A REJECTED candidate's
worktree is discarded.

## Termination (loop-until-dry, bounded — must always terminate)

Exit when ANY holds — always report the exit reason:

1. **DRY (success):** verdict `APPROVED`, zero Blocker/High findings, validator passes → merge, report.
2. **CONDITIONAL ceiling:** `APPROVED WITH CONDITIONS`, no Blocker/High, `iter >= 2` → merge best-so-far,
   report open Medium conditions.
3. **Budget exhausted:** `iter >= MAX_ITERS` OR `cum_cost_usd >= MAX_USD` → stop, report best-so-far.
4. **No-progress (noise floor):** median `total_score` gain across 2 iters < 1.0 point (0–10 scale),
   over ≥2 critic samples → stop.
5. **Regression guard:** `total_score` below `best_so_far` for 2 consecutive iters → revert to
   `best_so_far` and stop.
6. **Hard-unfixable:** a Blocker survives 2 fix attempts with alternative approaches → escalate.

Bounded retry: alternative fix ≤2× per defect; flaky agent retry ×1 then proceed-and-document.

## Budget enforcement reality

`--max-budget-usd` / `--max-turns` are **print-mode only** — they bind hard ONLY under headless launch:
`claude -p "/improve <TARGET>" --max-budget-usd 5.00 --max-turns 40`. In an interactive run there is no
native enforcer, so the `improve-gate.py` PreToolUse hook blocks commits once `cum_cost_usd >= MAX_USD`
in the ledger. Wire both paths.

## Deliverable

Run one full iteration end-to-end (through the HUMAN GATE); show the typed verdict, the `IMPROVE.md`
ledger entry, and the exit reason.
