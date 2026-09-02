#!/usr/bin/env python3
"""prompt_audit.py — did this run stop and wait for a human, and on exactly which call.

WHY THIS EXISTS, and it is the sentence that blocked six fixes.

CLAUDE.md has said since 2026-08-30 that "a session cannot see that it prompted", because the
tool result reads `File created successfully` whether it was auto-approved or a human tapped
approve on a phone an hour later. That was true of the TOOL RESULT and it was never true of the
process. Claude Code writes a per-call line to its debug log:

    [Stall] tool_dispatch_start tool=Bash toolUseId=toolu_01... permissionDecisionMs=21585

`permissionDecisionMs` is how long the call waited for a permission decision. An auto-approved
call settles in single or double digit milliseconds. A call that put a dialog in front of a human
carries however many seconds that human took. The two populations do not overlap and there is
nothing to interpret.

WHAT THAT COST. Five fixes were written against a guess about which write was prompting, each
verified honestly by the run that shipped it, each wrong. The runs could not tell. They could
have: the number was in the log the whole time.

MEASURED ON 2026-09-02, across both processes of one run, 432 dispatches:

    21585 ms   Bash   one call, and the only one
       43 ms   Bash   the slowest of the other 431
        4 ms   Bash   the fastest

So the threshold is not a tuning problem. Anything past a second is a human and anything under
a tenth of one is not.

WHAT THIS DOES NOT DO. It does not say why a call prompted. On the day it was written the same
`git checkout` verb ran unprompted in the first process of the run and prompted in the second,
and that is NOT explained. This tool reports the fact and the exact command, so the next fix can
be aimed at a measured target instead of a hypothesis. Naming the call is the whole job.

    python3 scripts/shared/prompt_audit.py
    python3 scripts/shared/prompt_audit.py --json
    python3 scripts/shared/prompt_audit.py --self-test

Exit 0 when nothing waited on a human. Exit 1 when something did, with the calls named. Exit 0
with a note when no debug log exists, because a run without `--debug` is unmeasured rather than
clean, and reporting "clean" for it would be the same lie this tool exists to end.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

# Claude Code writes here when --debug is on. The launcher passes it in the scheduled runner.
LOG_GLOBS = ("/tmp/claude-code.log", "/tmp/claude-code-*.log")

# A call that waited longer than this had a human in the loop. See the docstring: the measured
# populations are 4-43 ms against 21585 ms, so this sits an order of magnitude clear of both.
HUMAN_MS = 1000

DISPATCH = re.compile(
    r"tool_dispatch_start\s+tool=(?P<tool>\S+)\s+toolUseId=(?P<id>\S+)\s+"
    r"permissionDecisionMs=(?P<ms>\d+)"
)

# The rules the permission system persisted when somebody answered. This is the closest thing the
# log carries to "what was actually asked", and it names the command rather than the tool.
APPLIED = re.compile(r"Applying permission update: Adding \d+ allow rule\(s\).*?(\[.*\])")


def logs() -> list[Path]:
    seen: dict[str, Path] = {}
    for pattern in LOG_GLOBS:
        for hit in glob.glob(pattern):
            path = Path(hit)
            if path.is_file():
                seen[str(path)] = path
    return sorted(seen.values())


def scan_text(text: str) -> tuple[list[dict], list[str], int]:
    """Return the calls that waited on a human, the rules that got persisted, and the total."""
    waited: list[dict] = []
    total = 0
    for match in DISPATCH.finditer(text):
        total += 1
        ms = int(match.group("ms"))
        if ms >= HUMAN_MS:
            waited.append({"tool": match.group("tool"), "id": match.group("id"), "ms": ms})

    rules: list[str] = []
    for match in APPLIED.finditer(text):
        try:
            rules.extend(json.loads(match.group(1)))
        except json.JSONDecodeError:
            rules.append(match.group(1))
    return waited, rules, total


def scan() -> dict:
    waited: list[dict] = []
    rules: list[str] = []
    total = 0
    read: list[str] = []
    for path in logs():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        read.append(str(path))
        got_waited, got_rules, got_total = scan_text(text)
        waited.extend(got_waited)
        rules.extend(got_rules)
        total += got_total
    waited.sort(key=lambda row: row["ms"], reverse=True)
    return {"logs": read, "dispatches": total, "waited": waited, "rules_added": rules}


def report(result: dict) -> int:
    if not result["logs"]:
        print("prompt audit: no debug log found, so this run is UNMEASURED rather than clean.")
        print("             the scheduled runner passes --debug and writes /tmp/claude-code.log")
        return 0

    total = result["dispatches"]
    waited = result["waited"]
    if not waited:
        print(f"prompt audit: {total} tool call(s), none waited on a human")
        return 0

    print(f"prompt audit: {total} tool call(s), {len(waited)} WAITED ON A HUMAN")
    print()
    for row in waited:
        print(f"  {row['ms'] / 1000:8.1f}s  {row['tool']:10s}  {row['id']}")
    if result["rules_added"]:
        print()
        print("  the permission rules that were granted, which name the command that asked:")
        for rule in result["rules_added"]:
            print(f"    {rule}")
        print()
        print("  these persist to .claude/settings.local.json, which .gitignore excludes, so")
        print("  they die with the container. A grant that has to survive belongs in the")
        print("  SessionStart hook that writes ~/.claude/settings.json.")
    return 1


def self_test() -> int:
    """Prove the checker can go red, on the exact line shape that was measured."""
    checks: list[tuple[str, bool]] = []

    real = (
        "2026-09-02T11:54:36.255Z [INFO] [Stall] tool_dispatch_start tool=Bash "
        "toolUseId=toolu_012WpR5JjQmNLdVagwFRPr7E permissionDecisionMs=21585"
    )
    waited, _, total = scan_text(real)
    checks.append(("the 21585 ms call that actually stopped this run is CAUGHT",
                   len(waited) == 1 and waited[0]["ms"] == 21585 and total == 1))

    fast = (
        "2026-09-02T11:54:45.065Z [INFO] [Stall] tool_dispatch_start tool=Bash "
        "toolUseId=toolu_015AfwtY5pmXmaXstBrFeRx8 permissionDecisionMs=16"
    )
    waited, _, total = scan_text(fast)
    checks.append(("a 16 ms auto-approval is NOT reported, and is still counted",
                   waited == [] and total == 1))

    slowest_clean = fast.replace("permissionDecisionMs=16", "permissionDecisionMs=43")
    waited, _, _ = scan_text(slowest_clean)
    checks.append(("43 ms, the slowest measured auto-approval, is still clean", waited == []))

    rules_line = (
        "2026-09-02T11:54:36.249Z [DEBUG] Applying permission update: Adding 3 allow rule(s) "
        "to destination 'localSettings': [\"Bash(cp a b)\",\"Bash(git checkout *)\","
        "\"Bash(git add *)\"]"
    )
    _, rules, _ = scan_text(rules_line)
    checks.append(("the granted rules are read back, so the report names the COMMAND",
                   rules == ["Bash(cp a b)", "Bash(git checkout *)", "Bash(git add *)"]))

    _, _, total = scan_text("nothing here resembles a dispatch line")
    checks.append(("a log with no dispatches reports none rather than throwing", total == 0))

    combined = "\n".join([real, fast, rules_line])
    waited, rules, total = scan_text(combined)
    checks.append(("a real mixed log separates the one from the many",
                   total == 2 and len(waited) == 1 and len(rules) == 3))

    ok = True
    for label, passed in checks:
        print(f"  {'ok  ' if passed else 'FAIL'}  {label}")
        ok = ok and passed
    print()
    print("prompt_audit self-test: " + ("all passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--json", action="store_true", help="machine readable")
    parser.add_argument("--self-test", action="store_true", help="prove the gate can go red")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    result = scan()
    if args.json:
        print(json.dumps(result, indent=2))
        return 1 if result["waited"] else 0
    return report(result)


if __name__ == "__main__":
    sys.exit(main())
