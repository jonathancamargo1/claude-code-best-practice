# Self-Improving Harness — Flow

The `/improve` harness is a **Command → Agent → Skill** orchestration that iteratively improves a
target artifact through a closed loop, bounded by budget and a human approval gate. It is the
runnable implementation of [`self-improve-harness-prompt.md`](../self-improve-harness-prompt.md).

## Components

| Component | File | Role |
|---|---|---|
| `/improve` command | `.claude/commands/improve.md` | Orchestrator — owns control flow, the human gate, and termination |
| `grounding-explorer` | `.claude/agents/grounding-explorer.md` | PHASE 0/1 — read-only GO/NO-GO + grounding brief (`haiku`) |
| `candidate-generator` | `.claude/agents/candidate-generator.md` | PHASE 2/3 — produce + self-validate a candidate in a worktree (`sonnet`) |
| `adversarial-judge` | `.claude/agents/adversarial-judge.md` | PHASE 4 — fresh read-only critic, typed verdict (`opus`) |
| `fix-applier` | `.claude/agents/fix-applier.md` | PHASE 6 — apply prioritized findings in the worktree (`sonnet`) |
| `improve-rubric` skill | `.claude/skills/improve-rubric/SKILL.md` | Preloaded into the judge — rubric + verdict schema |
| `improve-report` skill | `.claude/skills/improve-report/SKILL.md` | PHASE 7 — append iteration record to the ledger |
| `improve-gate.py` | `.claude/hooks/scripts/improve-gate.py` | Command-scoped hook — markdown validator + soft budget gate |
| `IMPROVE.md` | `IMPROVE.md` | Append-only ledger — the memory half of the loop |

## Flow

```
/improve <target> <rubric?>
   │
   ▼
PHASE 0  grounding-explorer ──► GO / NO-GO ──(NO-GO)──► halt + report
   │ GO
   ▼
PHASE 1  grounding-explorer ──► current state · patterns · risks · ranked focus
   │
   ▼
════════ HUMAN GATE: present plan + verdict, WAIT for approval ════════
   │ approved
   ▼
PHASE 2  candidate-generator (worktree) ──► candidate change
   │
   ▼
PHASE 3  candidate-generator ──► improve-gate.py --event=validate  (real validator)
   │ pass
   ▼
PHASE 4  adversarial-judge (opus, read-only) ──► typed verdict + findings
   │
   ▼
PHASE 5  gate on verdict ─ REJECTED ─► discard worktree ─► (escalate if Blocker survives 2 fixes)
   │ NEEDS REVISION
   ▼
PHASE 6  fix-applier (worktree) ──► targeted fixes ──► re-validate
   │
   ▼
PHASE 7  merge worktree ──► working tree ; improve-report ──► append to IMPROVE.md
   │
   └────► LOOP to PHASE 2  ──or──►  EXIT (DRY | conditional | budget | no-progress | regression | escalation)
```

## Design invariants

- **Flat topology** — subagents never spawn subagents; every Agent call originates in the command.
- **Separation of duties** — the orchestrator routes, generators mutate (in worktrees), the judge scores
  (read-only), the report skill persists. No component does another's job.
- **Grounded, additive critique** — the judge cites `path:line` + real validator output and adds a
  Critique; it never rewrites the candidate, preserving provenance.
- **Bounded & observable** — every exit path names its termination reason; the ledger keeps `best_so_far`
  so a regression reverts instead of compounding.
- **Non-bypassable enforcement** — `improve-gate.py` blocks (exit 2) on invalid markdown or an exceeded
  soft budget, regardless of what the model wants to do.
