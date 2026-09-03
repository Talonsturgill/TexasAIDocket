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
carries however many seconds that human took. The two populations do not overlap.

WHAT THAT COST. Five fixes were written against a guess about which write was prompting, each
verified honestly by the run that shipped it, each wrong. The runs could not tell. They could
have: the number was in the log the whole time.

MEASURED ON 2026-09-02, across both processes of one run, 432 dispatches:

    21585 ms   Bash   one call, and the only one
       43 ms   Bash   the slowest of the other 431
        4 ms   Bash   the fastest

So the threshold is not a tuning problem. Anything past a second is a human.

THREE THINGS THIS DELIBERATELY DOES NOT DO, each of which it got wrong first.

**It does not print the command.** A granted permission rule carries the command text, and a
command can carry a credential, a private url or an address. The routine sends this finding into
a COMMITTED run record and an email, so printing it verbatim would turn a local debug log into
durable repository content. Only the tool and the first word of the command survive.

**It does not guess which call a rule belongs to.** Rules are matched to the dispatch that
follows them, because the grant is written microseconds before the call it releases. A rule with
no waited dispatch after it is reported as unassociated rather than attached to whichever slow
call happened to be in the same log.

**It does not call an unreadable log clean.** Zero parsed dispatches means the format moved or
the file is empty, which is UNMEASURED. Reporting that as "nothing prompted" is this repo's
oldest failure shape, a green banner measuring something narrower than it appears to certify.

    python3 scripts/shared/prompt_audit.py
    python3 scripts/shared/prompt_audit.py --json
    python3 scripts/shared/prompt_audit.py --self-test

Exit 0 when calls were measured and none waited. Exit 1 when something waited. Exit 1 when
nothing could be measured, because unmeasured is not clean.
"""
from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from pathlib import Path

LOG_GLOBS = ("/tmp/claude-code.log", "/tmp/claude-code-*.log")

# A call that waited longer than this had a human in the loop. The measured populations are
# 4 to 43 ms against 21585 ms, so this sits an order of magnitude clear of both.
HUMAN_MS = 1000

STAMP = re.compile(r"^(\d{4}-\d\d-\d\dT[\d:.]+Z)")
DISPATCH = re.compile(
    r"tool_dispatch_start\s+tool=(?P<tool>\S+)\s+toolUseId=(?P<id>\S+)\s+"
    r"permissionDecisionMs=(?P<ms>\d+)"
)
APPLIED = re.compile(r"Applying permission update: Adding \d+ allow rule\(s\).*?(\[.*\])")

# `Bash(cp .claude/WORKLOG.md out/x)` -> tool `Bash`, command `cp`, and the arguments dropped.
RULE = re.compile(r"^(?P<tool>[A-Za-z_][\w]*)\((?P<body>.*)\)$", re.S)


def redact(rule: str) -> str:
    """Keep what identifies the call and drop what could carry a secret.

    A rule is `Tool(command and its arguments)`. The tool and the command name are the whole
    diagnostic value, and every argument after them is arbitrary text a run does not control. The
    routine puts this output in a committed file, so the arguments never leave this process.
    """
    rule = rule.strip()
    m = RULE.match(rule)
    if not m:
        return rule.split()[0] if rule else rule       # a bare tool name is already safe
    body = m.group("body").strip()
    if not body or body == "*":
        return f"{m.group('tool')}({body})" if body else m.group("tool")

    # Keep the command, and its SUBCOMMAND when there is one, because `git` alone does not say
    # what was refused and `git checkout` does. A subcommand is a bare alphabetic word: that
    # admits `checkout` and `add` while rejecting a flag, a path and anything with a dot in it,
    # which is where an argument's secret would live.
    words = body.split()
    kept = words[:1]
    if len(words) > 1 and re.fullmatch(r"[a-z][a-z-]*", words[1]):
        kept.append(words[1])
    rest = " ..." if words[len(kept):] else ""
    return f"{m.group('tool')}({' '.join(kept)}{rest})"


def scan_text(text: str) -> tuple[list[dict], list[str], int]:
    """Return the waited calls with the rules that released them, the orphan rules, and the total.

    A permission grant is written just before the dispatch it releases, so each pending rule set
    attaches to the next waited dispatch. Anything still pending at the end never released a
    waited call and is reported separately rather than guessed at.
    """
    waited: list[dict] = []
    total = 0
    pending: list[str] = []
    orphans: list[str] = []

    for line in text.splitlines():
        stamp = STAMP.match(line)

        applied = APPLIED.search(line)
        if applied:
            try:
                pending.extend(json.loads(applied.group(1)))
            except json.JSONDecodeError:
                pending.append(applied.group(1))
            continue

        hit = DISPATCH.search(line)
        if not hit:
            continue
        total += 1
        ms = int(hit.group("ms"))
        if ms < HUMAN_MS:
            continue
        waited.append({
            "tool": hit.group("tool"),
            "id": hit.group("id"),
            "ms": ms,
            "at": stamp.group(1) if stamp else None,
            "rules": [redact(r) for r in pending],
        })
        pending = []

    orphans = [redact(r) for r in pending]
    return waited, orphans, total


def logs() -> list[Path]:
    seen: dict[str, Path] = {}
    for pattern in LOG_GLOBS:
        for hit in glob.glob(pattern):
            path = Path(hit)
            if path.is_file():
                seen[str(path)] = path
    return sorted(seen.values())


def scan() -> dict:
    waited: list[dict] = []
    orphans: list[str] = []
    total = 0
    read: list[str] = []
    for path in logs():
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        read.append(str(path))
        got_waited, got_orphans, got_total = scan_text(text)
        waited.extend(got_waited)
        orphans.extend(got_orphans)
        total += got_total
    waited.sort(key=lambda row: row["ms"], reverse=True)
    return {"logs": read, "dispatches": total, "waited": waited,
            "unassociated_rules": orphans, "measured": total > 0}


def report(result: dict) -> int:
    # UNMEASURED IS NOT CLEAN. No log, or a log this parser got nothing out of, both mean the
    # question was not answered. Saying "none waited" for either is the exact failure this file
    # exists to end, one layer up.
    if not result["measured"]:
        why = "no debug log found" if not result["logs"] else \
              "a log was read and no tool dispatch line parsed, so the format may have moved"
        print(f"prompt audit: UNMEASURED, {why}")
        print("             this is not a clean result. The scheduled runner passes --debug and")
        print("             writes /tmp/claude-code.log")
        return 1

    total = result["dispatches"]
    waited = result["waited"]
    if not waited:
        print(f"prompt audit: {total} tool call(s) measured, none waited on a human")
        return 0

    print(f"prompt audit: {total} tool call(s) measured, {len(waited)} WAITED ON A HUMAN")
    print()
    for row in waited:
        print(f"  {row['ms'] / 1000:8.1f}s  {row['tool']:10s}  {row['id']}")
        for rule in row["rules"]:
            print(f"            released by  {rule}")
    if result["unassociated_rules"]:
        print()
        print("  rules granted with no waited call after them, so NOT attributed to any above:")
        for rule in result["unassociated_rules"]:
            print(f"    {rule}")
    print()
    print("  Arguments are withheld on purpose. A command can carry a credential and this")
    print("  finding goes into a committed run record.")
    print("  Grants persist to .claude/settings.local.json, which .gitignore excludes, so they")
    print("  die with the container. A grant that must survive belongs in the SessionStart hook.")
    return 1


def self_test() -> int:
    checks: list[tuple[str, bool]] = []

    real = ("2026-09-02T11:54:36.255Z [INFO] [Stall] tool_dispatch_start tool=Bash "
            "toolUseId=toolu_012WpR permissionDecisionMs=21585")
    waited, _, total = scan_text(real)
    checks.append(("the 21585 ms call that actually stopped this run is CAUGHT",
                   len(waited) == 1 and waited[0]["ms"] == 21585 and total == 1))

    fast = ("2026-09-02T11:54:45.065Z [INFO] [Stall] tool_dispatch_start tool=Bash "
            "toolUseId=toolu_015Afw permissionDecisionMs=16")
    waited, _, total = scan_text(fast)
    checks.append(("a 16 ms auto-approval is NOT reported, and is still counted",
                   waited == [] and total == 1))

    waited, _, _ = scan_text(fast.replace("Ms=16", "Ms=43"))
    checks.append(("43 ms, the slowest measured auto-approval, is still clean", waited == []))

    # REDACTION. The real rule carried a path; a real one could carry a credential.
    checks.append(("a command's arguments are stripped from a rule",
                   redact("Bash(cp .claude/WORKLOG.md out/tmp/x.md)") == "Bash(cp ...)"))
    checks.append(("...including anything that looks like a secret",
                   "hunter2" not in redact("Bash(curl -H 'Authorization: hunter2' https://x/y)")))
    checks.append(("a wildcard rule survives readably", redact("Bash(git checkout *)")
                   == "Bash(git checkout ...)"))
    checks.append(("a bare tool rule is untouched", redact("Write") == "Write"))

    # ASSOCIATION. The grant precedes the call it releases.
    rules_line = ("2026-09-02T11:54:36.249Z [DEBUG] Applying permission update: Adding 2 allow "
                  "rule(s) to destination 'localSettings': [\"Bash(git checkout *)\","
                  "\"Bash(git add *)\"]")
    waited, orphans, total = scan_text("\n".join([rules_line, real, fast]))
    checks.append(("a rule granted before a waited call is attached to it",
                   len(waited) == 1 and waited[0]["rules"] == ["Bash(git checkout ...)",
                                                               "Bash(git add ...)"]))
    checks.append(("...and nothing is left unattributed when it matched", orphans == []))

    waited, orphans, _ = scan_text("\n".join([fast, rules_line]))
    checks.append(("a rule with no waited call after it is UNASSOCIATED, never guessed onto one",
                   waited == [] and orphans == ["Bash(git checkout ...)", "Bash(git add ...)"]))

    second = real.replace("toolu_012WpR", "toolu_09ZZZZ").replace("Ms=21585", "Ms=9000")
    waited, _, _ = scan_text("\n".join([rules_line, real, second]))
    checks.append(("a second waited call does not inherit the first call's rules",
                   len(waited) == 2 and waited[1]["rules"] == []))

    # UNMEASURED IS NOT CLEAN.
    _, _, total = scan_text("nothing here resembles a dispatch line")
    checks.append(("a log with no dispatch lines parses to zero rather than throwing", total == 0))
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()):
        unmeasured = report({"logs": ["/tmp/x.log"], "dispatches": 0, "waited": [],
                             "unassociated_rules": [], "measured": False})
    checks.append(("...and zero dispatches reports UNMEASURED, exit 1, never clean",
                   unmeasured == 1))

    ok = True
    for label, passed in checks:
        print(f"  {'ok  ' if passed else 'FAIL'}  {label}")
        ok = ok and bool(passed)
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
        return 0 if result["measured"] and not result["waited"] else 1
    return report(result)


if __name__ == "__main__":
    sys.exit(main())
