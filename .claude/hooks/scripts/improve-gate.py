#!/usr/bin/env python3
"""improve-gate.py — deterministic, non-bypassable enforcement for the /improve harness.

Command-scoped hook (declared in .claude/commands/improve.md frontmatter). It enforces what an
advisory prompt cannot: markdown validity on every edit, and a soft cost ceiling before commits.

Events
------
  --event=session-start   Load the IMPROVE.md ledger into the session (advisory).
  --event=post-edit       After an Edit/Write: validate any staged/changed markdown (advisory warn).
  --event=validate --file=PATH   Explicit validator invoked by generator/fix-applier. Exit 2 on failure.
  --event=pre-commit      Before a Bash tool call: block commits if cum_cost_usd >= MAX_USD. Exit 2 blocks.
  --event=stop            If the loop halted before a terminal verdict and budget remains, nudge to continue.

Exit codes: 0 = allow, 2 = block (stderr is surfaced to the model). Any unexpected error exits 0
(fail-open) so the harness is never wedged by a bug in its own gate — the judge remains the real check.
"""
import argparse
import json
import os
import re
import sys

REPO = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
LEDGER = os.path.join(REPO, "IMPROVE.md")
MAX_USD = float(os.environ.get("IMPROVE_MAX_USD", "5.00"))


def _read(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read()
    except OSError:
        return ""


def validate_markdown(path):
    """Return (ok, [problems]). The repo's real 'build': fences balanced, non-empty, headings sane."""
    text = _read(path)
    problems = []
    if not text.strip():
        problems.append(f"{path}: empty or unreadable")
        return False, problems
    if text.count("```") % 2 != 0:
        problems.append(f"{path}: unbalanced ``` code fences ({text.count('```')} found)")
    # heading levels must not jump more than one (## -> #### is a skip)
    prev = 0
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^(#{1,6})\s", line)
        if m:
            lvl = len(m.group(1))
            if prev and lvl > prev + 1:
                problems.append(f"{path}:{i}: heading jumps from h{prev} to h{lvl}")
            prev = lvl
    return (len(problems) == 0), problems


def cum_cost():
    m = re.findall(r"cum_cost_usd:\s*([0-9]+\.?[0-9]*)", _read(LEDGER))
    return float(m[-1]) if m else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True)
    ap.add_argument("--file")
    args = ap.parse_args()

    if args.event == "session-start":
        if os.path.exists(LEDGER):
            print("improve-gate: IMPROVE.md ledger present — resume grounded in prior iterations.")
        sys.exit(0)

    if args.event == "validate":
        target = args.file or ""
        if not target.endswith(".md"):
            sys.exit(0)  # non-markdown targets: defer to the target's own toolchain
        ok, problems = validate_markdown(os.path.join(REPO, target) if not os.path.isabs(target) else target)
        if not ok:
            sys.stderr.write("VALIDATOR FAILED:\n  " + "\n  ".join(problems) + "\n")
            sys.exit(2)
        print(f"validator ok: {target} (fences balanced, headings hierarchical)")
        sys.exit(0)

    if args.event == "post-edit":
        # advisory: warn on the edited markdown but never block an in-progress edit
        payload = ""
        try:
            payload = sys.stdin.read()
        except Exception:
            pass
        for path in re.findall(r'"file_path"\s*:\s*"([^"]+\.md)"', payload):
            ok, problems = validate_markdown(path)
            if not ok:
                sys.stderr.write("improve-gate warn: " + "; ".join(problems) + "\n")
        sys.exit(0)

    if args.event == "pre-commit":
        spent = cum_cost()
        if spent >= MAX_USD:
            sys.stderr.write(
                f"BUDGET GATE: cum_cost_usd={spent:.2f} >= MAX_USD={MAX_USD:.2f}. "
                "Stop the loop and report best-so-far instead of committing another iteration.\n"
            )
            sys.exit(2)
        sys.exit(0)

    if args.event == "stop":
        # soft nudge only; the orchestrator's TERMINATION rules are the real authority
        print("improve-gate: verify TERMINATION reason was recorded before stopping.")
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # fail-open: never wedge the harness on a gate bug
        sys.stderr.write(f"improve-gate: non-fatal error ({exc}); allowing.\n")
        sys.exit(0)
