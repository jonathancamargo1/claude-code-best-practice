# SELF-IMPROVING HARNESS BUILDER

You are building a **self-improving harness**: a reusable Claude Code workflow that takes a
target artifact (code, doc, config, prompt, feature) and iteratively improves it through a closed
loop — GENERATE → CRITIQUE → APPLY-FIX → VERIFY — looping until quality converges (DRY) or a
budget is exhausted. Build it now, in this repo, as durable, re-runnable artifacts.

**Orchestration primitives (use ONLY these — they exist; do not invent a "Workflow tool"):**
a **command** (`/improve`) as the orchestrator, the **Agent tool** for all fan-out, **Task tools**
(`TaskCreate`/`TaskUpdate`/`TaskGet`/`TaskList`) for live phase state, command-scoped **hooks** for
enforcement, and an append-only **`IMPROVE.md` ledger** for cross-session durability. Optionally
`/loop` for cadence — but note `/loop` tasks are in-memory, session-scoped, and expire after 3 days,
so durable resumption MUST come from the ledger + a `SessionStart` hook, never the schedule.

This prompt encodes hard-won practices. Follow them exactly; they are not suggestions.

---

## TARGET (fill in, or ask me ≤3 questions then proceed)
- **Artifact under improvement:** `<<TARGET>>` (path or description)
- **Definition of "good" (rubric source):** `<<RUBRIC SOURCE>>` (tests to pass / spec / acceptance criteria)
- **Budget knobs (all default-able):**
  - `MAX_ITERS = <<N, default 5>>`
  - `MAX_USD = <<default 5.00>>`  · `PANEL_USD_CAP = <<default 1.50 per critique round>>`
  - `EFFORT = <<low|medium|high|xhigh|max, default high>>`
  - `PANEL_SIZE = <<1|3, default 1>>`
  - `COMPACT_PCT = <<default 50>>`  (sets `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` so compaction fires early)

> **Budget enforcement reality:** `--max-budget-usd` and `--max-turns` are **print-mode only**.
> They bind hard ONLY when this harness is launched headless (`claude -p ... --max-budget-usd $MAX_USD
> --max-turns ...`). In an interactive `/improve` run there is no native enforcer — so the orchestrator
> tracks cumulative cost in the ledger from status-line telemetry and a `Stop`/`PreToolUse` hook halts
> the loop when a soft cap is crossed. Wire BOTH paths.

If the rubric source is missing, ask up to 3 clarifying questions, then proceed. Cheap upstream
clarification beats burning the iteration budget on the wrong target.

---

## HUMAN GATE (before any mutation)
Run PHASE 0–1, then **present the plan + GO/NO-GO verdict and STOP for my approval** before PHASE 2
mutates anything (plan-mode-first + human-gated discipline). After approval, run unattended via
**auto mode** (model-based permission classifier: safe ops auto-approve, risky ones pause) — never
`--dangerously-skip-permissions`. Always stop-and-ask before irreversible ops (force-push, history
rewrite, deleting non-worktree files).

---

## PILLAR 1 — ORCHESTRATION LOOP (the outer loop)

`/improve` owns control flow ONLY; it never does the work — it delegates (Command → Agent → Skill).
**Topology rule (non-negotiable):** subagents cannot spawn subagents via bash. ALL fan-out happens
from the orchestrator via the Agent tool: `Agent(subagent_type="...", description="...",
prompt="...", model="...")`. Flat, orchestrator-driven topology — never nested self-spawning.

```
PHASE 0  GO/NO-GO        cheap (haiku) feasibility gate — worth attempting? → GO | NO-GO + rationale
PHASE 1  GROUND          read-only Explore agent: current state, adjacent files, patterns, risks
         ── HUMAN GATE: present plan + verdict, wait for approval ──
PHASE 2  GENERATE        producer agent emits a candidate change INTO a worktree
PHASE 3  SELF-VALIDATE   producer runs linter/tests/build FOR REAL (not reasoning about them)
PHASE 4  CRITIQUE        SEPARATE adversarial judge panel scores a fixed rubric, emits typed verdict
PHASE 5  GATE            branch on verdict: APPROVED | APPROVED WITH CONDITIONS | NEEDS REVISION | REJECTED
PHASE 6  APPLY-FIX       feed prioritized findings into a targeted fix pass (in worktree)
PHASE 7  MERGE + LOG     on success, merge worktree → working tree; append iteration record to IMPROVE.md
        ──── LOOP to PHASE 2, or EXIT (see TERMINATION) ────
```

Track phase state with **Task tools** and markers: `[ ]` not started · `[~]` in progress ·
`[x]` validated · `[!]` conditional · `[-]` failed. **Never advance past a failing gate.**

**PHASE 0 — GO/NO-GO:** haiku, emits `GO` / `NO-GO` + one-line rationale. NO-GO halts and reports.

**PHASE 4 — CRITIQUE (the heart):** Critique by the producing context is weak. Route to a
**fresh, separate critic** (`opus`), preferring a **heterogeneous model** (different from the
generator) to break correlated blind spots. Default rubric dimensions (override via `<<RUBRIC SOURCE>>`):

| Dimension | Rated | Evidence required |
|---|---|---|
| Correctness / spec-conformance | Aligned·Partial·Misaligned + 0–10 | file:line + real test output |
| Security | Aligned·Partial·Misaligned + 0–10 | file:line |
| Simplicity / maintainability | Aligned·Partial·Misaligned + 0–10 | file:line |
| Edge-case handling | Aligned·Partial·Misaligned + 0–10 | file:line |

Then ONE typed verdict + prioritized findings:
`{ severity: Blocker|High|Medium, location: file:line, finding: ..., fix: <specific action> }`.

- **Additive, not destructive:** the critic ADDS a "Critique" section; never rewrites the
  generator's work — preserves provenance so you can diff critique vs. generation.
- **Grounded in executed reality:** reads actual files + real lint/test/build output. Ungrounded
  critique → confident-but-wrong fixes.

**PHASE 7 — MERGE:** worktrees auto-clean only when no changes are made, so an *approved* candidate
must be explicitly merged back (fast-forward or cherry-pick the worktree branch onto the working
tree). A REJECTED/abandoned candidate's worktree is discarded.

**Scaling knob — fan-out:** isolated subagent contexts give ≈ N× effective context. At `PANEL_SIZE=3`
run three concurrent critics from the orchestrator: a **correctness critic** (`opus`, read-only),
a **security critic** (`opus`, read-only, `disallowedTools: Write,Edit`), a **simplicity critic**
(`sonnet`, read-only). **Route models per role:** haiku for orchestration/GO-NO-GO, opus for the
judge. The panel's combined spend must respect `PANEL_USD_CAP` — if a round would exceed it, drop to
`PANEL_SIZE=1` and log the downgrade.

---

## PILLAR 2 — SUBAGENTS / SKILLS / PROGRESSIVE DISCLOSURE

Components (single responsibility, minimal context, bounded blast radius via
`tools` allowlist + `disallowedTools` + `maxTurns` + `effort`):

- **`grounding-explorer`** — `model: haiku`, READ-ONLY (no Write/Edit), `maxTurns: 8`.
- **`candidate-generator`** — `isolation: "worktree"`, `maxTurns: 12`. All mutations land in a temp
  worktree (auto-cleaned on no-change) → reversible, low-risk.
- **`adversarial-judge`** — `model: opus`, READ-ONLY, `disallowedTools: Write, Edit`. Emits the typed
  verdict above.
- **`fix-applier`** — `isolation: "worktree"`, `maxTurns: 10`, takes prioritized findings, applies
  targeted fixes only.

**Progressive disclosure:** preload the rubric + verdict-schema into the judge via the agent
`skills:` field (full content at startup — guarantees current knowledge). Keep machine-only skills
out of the `/` menu with `user-invocable: false`. Use `context: fork` on token-heavy analysis skills.
Scope skill/rule auto-activation with `paths:` globs. Two patterns, used deliberately: **preload**
for always-on knowledge (rubric, schema); **`Skill(skill:"…")`** for discrete mid-flow actions
(iteration-report rendering).

**Containment (this harness writes its own skills/config):** set `disableSkillShellExecution: true`
so self-authored skills can't run arbitrary shell; treat managed-tier rules
(`allowManagedPermissionRulesOnly`, `strictPluginOnlyCustomization`) and any `deny` rules as hard
floors the harness must NOT attempt to loosen.

---

## PILLAR 3 — MEMORY / FEEDBACK (so improvement accrues, not noise)

**1. Durable ledger** — append every iteration to `IMPROVE.md`, and track `best_so_far`:

```yaml
# IMPROVE.md (append-only)
best_so_far: { iter: 2, total_score: 28, worktree_ref: "improve/iter-2" }
- iter: 3
  phase_state: "[x][x][x][x][!][x][x]"
  verdict: NEEDS REVISION
  scores: { correctness: 7, security: 9, simplicity: 5, edge_cases: 6 }   # total 27 — REGRESSION vs best (28)
  findings: [{ severity: High, loc: "src/auth.ts:42", fix: "validate token before decode" }]
  changed_files: ["src/auth.ts"]
  tests: "12 pass / 1 fail"
  model: { generator: "<snapshot-id>", judge: "<snapshot-id>" }   # pin snapshots, not floating aliases
  cost_usd: 0.83
  cum_cost_usd: 2.41
```

**2. Per-agent memory** — `memory: project` on judge and fix-applier. **Explicitly prompt the
read-before / write-after cycle** in every agent body: *"Before starting, review your memory for
patterns seen before. After completing, update memory with what you learned."* The loop only closes
if both halves run every invocation.

**Memory hygiene:** only ~first 200 lines of `MEMORY.md` load at startup — **curate, don't append**;
overflow into topic files (`recurring-defects.md`, `accepted-fixes.md`). Pair static `skills:`
(conventions) with dynamic `memory:` ("what we learned" vs "what we were told").

**Guard against noise (the loop feeds its own outcomes forward):**
- **Aggregate, don't anecdote** — only promote a finding to durable memory after it recurs across
  **≥2 iterations** (run-to-run serving variance is **±8–14%**; you cannot detect a real ~5% change
  from one sample).
- **Pin model snapshots** + record per-run metadata so regressions attribute to your change, not
  serving variance.
- **No context contamination** — do NOT feed the raw failing transcript forward. On a FAILED attempt,
  **rewind-and-reprompt** (distill the lesson into one informed prompt). Improvement = curated memory,
  not raw carryover. Compact at `COMPACT_PCT` with a forward-looking hint.

---

## PILLAR 4 — CONFIG / HOOKS (deterministic, non-bypassable enforcement)

Hooks run shell at lifecycle events and **block tool calls even when the model wants to proceed** —
they enforce what advisory prompts can't. Scope them to the `/improve` **command** (frontmatter
`hooks`), not global settings, so enforcement travels with the workflow:

- **`PostToolUse`** (Edit/Write) → run formatter + linter automatically.
- **`PreToolUse`** (commit/merge) → **block if tests fail** ("tests must pass before commit"; "no
  skipping the gate"). Also block if `cum_cost_usd >= MAX_USD` (soft-budget enforcement).
- **`Stop`** → if the loop halted before a terminal verdict AND budget remains, re-poke to continue;
  if budget is spent, allow stop.
- **`SessionStart`** → load `IMPROVE.md` + agent memory so each run resumes grounded.

**Permissions** — append precise rules; remember **deny > ask > allow**, first match wins, deny can't
be overridden, Bash matching splits on `&&`/`|`/`;` so each subcommand matches independently:
```jsonc
"allow": ["Bash(npm test *)", "Bash(npm run lint *)", "Edit(src/**)"],
"deny":  ["Bash(git push --force*)", "Edit(.claude/settings.json)"]   // self-restrict the blast radius
```
Write durable/shareable rules to committed `settings.json`; keep experiments in `settings.local.json`;
never assume you can override managed settings. A **status-line `command`** (harness-run, not
model-run) emits live JSON (context %, cost, rate-limit resets) — feed it into the ledger to drive the
soft budget and proactive compaction.

---

## TERMINATION (loop-until-dry, bounded — must always terminate & be observable)

Exit when ANY holds:

1. **DRY (success):** verdict `APPROVED`, zero Blocker/High findings, AND all tests/lint/build pass
   for real. → merge, report success.
2. **CONDITIONAL ceiling:** verdict `APPROVED WITH CONDITIONS` AND no Blocker/High AND `iter >= 2`
   → merge best-so-far, report the open Medium conditions. (Do NOT loop forever chasing Mediums.)
3. **Budget exhausted:** `iter >= MAX_ITERS` OR `cum_cost_usd >= MAX_USD` → stop, report best-so-far.
4. **No-progress (noise floor):** median `total_score` gain across 2 consecutive iters **< 1.0 point
   on the 0–10×dimensions scale**, measured over ≥2 critic samples → stop (you're chasing variance).
5. **Regression guard:** if `total_score` drops below `best_so_far` for **2 consecutive iters** →
   **revert to `best_so_far` candidate and stop.**
6. **Hard-unfixable:** a Blocker survives **2 fix attempts with alternative approaches** → escalate.

**Bounded retry + escalation — never spin:** alternative fix approach **max 2×** per defect; retry a
flaky agent **once** then proceed-and-document the gap; on exhaustion emit
*"Attempted N approaches on `<finding>`. User guidance needed."* and stop. Graceful degradation
(proceed-and-document OR halt-and-escalate) is the safety valve.

**Context budget:** treat ~300–400k tokens as the rot zone (not the 1M limit). Proactive `/compact`
with a forward-looking hint before autocompact fires; delegate noisy exploration to subagents whose
intermediate output is GC'd on exit; fresh session per genuinely new target.

---

## DELIVERABLES (build them; don't just describe)
1. `/improve` command — thin orchestrator owning the loop, the human gate, and TERMINATION.
2. The four agents (`grounding-explorer`, `candidate-generator`, `adversarial-judge`, `fix-applier`)
   with correct `model`/`effort`/`tools`/`disallowedTools`/`maxTurns`/`isolation`/`memory` frontmatter.
3. Skills: rubric + verdict-schema (preloaded, `user-invocable: false`) and an iteration-report
   renderer (on-demand). Set `disableSkillShellExecution: true`.
4. Command-scoped hooks: format/lint (PostToolUse), test-gate + budget-gate (PreToolUse),
   resume-if-budget (Stop), load-ledger (SessionStart).
5. `IMPROVE.md` seeded with the schema above (including `best_so_far`).
6. A headless launch line documented in the command (`claude -p ... --max-budget-usd $MAX_USD
   --max-turns ...`) so hard budget caps apply in unattended mode.

Then **run one full iteration on `<<TARGET>>`** end-to-end (through the human gate) to prove the loop
closes; show the typed verdict, the ledger entry, and the exit reason
(DRY / CONDITIONAL / budget / no-progress / regression / escalation).

**Build it. Don't just describe it.**
