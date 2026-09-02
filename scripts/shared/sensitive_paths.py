#!/usr/bin/env python3
"""sensitive_paths.py — no instruction file may tell a session to WRITE under `.claude/`.

WHY THIS EXISTS.

The host classifies everything under `.claude/` as a SENSITIVE FILE and prompts on any edit to
one, whatever the permission mode says and whatever any allow list contains. The dialog names it:

    Claude requested permissions to edit
    /home/user/TexasAIDocket/.claude/WORKLOG.md which is a sensitive file.

That guard is deliberate and it is the same shape as a cloned repository not being allowed to
grant itself `bypassPermissions`: those paths decide what runs and what is permitted, so a
session cannot be allowed to edit them on its own say so. **There is therefore no configuration
answer to it.** `.claude/settings.json` cannot switch it off, `defaultMode` cannot, and the
SessionStart hook that writes `~/.claude/settings.json` cannot.

WHAT IT COST. `CLAUDE.md` told every run to keep its durable plan in `.claude/WORKLOG.md`, so
every long task hit the prompt, and an unattended run has nobody to answer it. Worse, the same
file was `human` lane under `ownership.yaml`'s catch-all, so even an approved write could not be
committed by the `daily` routine. Two files in this repo had already noticed the ownership half
and worked around it in prose rather than fixing it: `knowledge/carousel/UPGRADE_BACKLOG.md`
("would be the natural home and cannot be") and `runs/carousel/2026-08-25/RECUT_PLAN.md`.

AND AN APPROVAL DOES NOT SURVIVE. Answering the prompt writes the grant to
`.claude/settings.local.json`, which `.gitignore` excludes, so it dies with the container. The
owner tapping approve fixes one run and no future one, which is how the count kept climbing.

WHY A CHECKER AND NOT A PARAGRAPH. This repo's own doctrine, stated in CLAUDE.md several times
over: a rule stated in config with nothing checking it is a rule that ships broken. The actor
stamp took five prose fixes across six wedged runs before somebody wrote
`scripts/shared/actor_stamp_shape.py`. This is that gate's sibling and it exists for the same
reason: the instruction a future run receives must not be the one that breaks it.

READING AND EXECUTING ARE FINE. `bash .claude/skills/carousel-engine/bootstrap.sh` and reading
`.claude/skills/carousel-engine/SKILL.md` do not prompt, because neither is an edit. This gate is
about writes only, and a checker that flagged every mention would be turned off within a week.

    python3 scripts/shared/sensitive_paths.py
    python3 scripts/shared/sensitive_paths.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The instruction surfaces. A session reads these and does what they say, so these are the files
# that decide whether a run prompts. Anything else naming the path is describing the mechanism.
INSTRUCTION_GLOBS = (
    "CLAUDE.md",
    "AGENTS.md",
    "prompts/*.md",
    ".claude/skills/*/SKILL.md",
    ".claude/agents/*.md",
)

DOT_CLAUDE = r"['\"`]?(?:\./)?\.claude/[^\s'\"`)]*"

# A shell redirect, a tee, or a heredoc landing under .claude/.
SHELL_WRITE = re.compile(rf"(?:>>?\s*|\|\s*tee\s+(?:-a\s+)?){DOT_CLAUDE}", re.IGNORECASE)

# A tool write named in either order on one line.
TOOL_WRITE = re.compile(
    rf"(?:(?:write|edit)\s+tool[^\n]*\.claude/|{DOT_CLAUDE}[^\n]*\b(?:write|edit)\s+tool)",
    re.IGNORECASE,
)

# Any imperative to put something under .claude/, which is the general case.
VERB_WRITE = re.compile(
    rf"(?:write|append|stamp|put|set|save|create|update|maintain|record)\s+"
    rf"(?:[^\n]{{0,60}}?\s+)?(?:in|into|to|at)\s+{DOT_CLAUDE}",
    re.IGNORECASE,
)

# A file-moving or file-removing command aimed under .claude/.
MOVE_WRITE = re.compile(
    rf"\b(?:cp|mv|rm|touch|git\s+(?:mv|rm|add|checkout))\b[^\n]*{DOT_CLAUDE}",
    re.IGNORECASE,
)

PATTERNS = (SHELL_WRITE, TOOL_WRITE, VERB_WRITE, MOVE_WRITE)

HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")

# The heading marking a section as the RULE's own explanation, where the mistake has to be quoted
# in order to be warned against. Deliberately narrow, taking these literal words, so a file cannot
# wave the gate away with a synonym. Same device as actor_stamp_shape.py, and same reason: the
# earlier version of THAT gate went red on the very file documenting it.
SANCTIONED = "sensitive file"


def offending_lines(text: str) -> list[tuple[int, str]]:
    """Every line telling somebody to write under `.claude/`, by any mechanism.

    Lines inside a section whose heading contains `sensitive file` are teaching rather than
    telling: CLAUDE.md has to quote the dialog and name the old path in order to explain why the
    rule exists. The section is the right unit rather than the line, because the paragraph
    explaining a mistake runs several lines and the quote lands on one. The exemption ends at the
    next heading of any level so it cannot leak down the document, and the self-test asserts it.
    """
    out: list[tuple[int, str]] = []
    exempt = False
    for i, line in enumerate(text.splitlines(), 1):
        head = HEADING.match(line)
        if head:
            exempt = SANCTIONED in head.group(1).lower()
            continue
        if exempt:
            continue
        if any(p.search(line) for p in PATTERNS):
            out.append((i, line.strip()))
    return out


def scan(root: Path) -> list[str]:
    problems: list[str] = []
    for pattern in INSTRUCTION_GLOBS:
        for path in sorted(root.glob(pattern)):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for lineno, line in offending_lines(text):
                problems.append(f"{path.relative_to(root)}:{lineno}: {line}")
    return problems


def self_test() -> int:
    checks: list[tuple[str, bool]] = []

    real = "- `.claude/WORKLOG.md` if it exists — the durable plan across contexts."
    checks.append(("a bare mention is NOT flagged, because reading is fine",
                   not offending_lines(real)))

    write = "Write the durable plan to `.claude/WORKLOG.md` before touching code."
    checks.append(("the instruction that actually wedged runs is CAUGHT",
                   bool(offending_lines(write))))

    maintain = "Resume from that table and update it in .claude/WORKLOG.md after every commit."
    checks.append(("'update it in' is caught, not just 'write'", bool(offending_lines(maintain))))

    redirect = "run `echo done >> .claude/state`"
    checks.append(("a shell redirect under .claude/ is CAUGHT", bool(offending_lines(redirect))))

    tool = "Use the Write tool to create `.claude/NOTES.md`."
    checks.append(("a Write tool instruction is CAUGHT", bool(offending_lines(tool))))

    move = "archive it: `git mv .claude/WORKLOG.md runs/`"
    checks.append(("a git mv out of .claude/ is CAUGHT, because it edits the tree there",
                   bool(offending_lines(move))))

    execute = "6. `bash .claude/skills/carousel-engine/bootstrap.sh`."
    checks.append(("EXECUTING a committed script there is NOT flagged",
                   not offending_lines(execute)))

    render = ("python3 .claude/skills/carousel-engine/render.py --slides-dir out/<date>/slides "
              "--out-dir out/<date>/render")
    checks.append(("running the render engine is NOT flagged, and its --out-dir does not fool it",
                   not offending_lines(render)))

    read = "Read `.claude/skills/carousel-engine/SKILL.md` before writing a slide, every run."
    checks.append(("reading a skill file is NOT flagged, though the line says 'writing'",
                   not offending_lines(read)))

    exempted = (
        "### Why .claude/ is a sensitive file\n"
        "The dialog says: requested permissions to edit `.claude/WORKLOG.md`.\n"
        "It used to say write the plan to `.claude/WORKLOG.md`, which is the bug.\n"
        "## Another heading\n"
        "Write the plan to `.claude/WORKLOG.md`.\n"
    )
    hits = offending_lines(exempted)
    checks.append(("the explaining section may quote the mistake", len(hits) == 1))
    checks.append(("...and the exemption ENDS at the next heading", hits and hits[0][0] == 5))

    ok = True
    for label, passed in checks:
        print(f"  {'ok  ' if passed else 'FAIL'}  {label}")
        ok = ok and bool(passed)
    print()
    print("sensitive_paths self-test: " + ("all passed" if ok else "FAILED"))
    return 0 if ok else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

    problems = scan(REPO_ROOT)
    if problems:
        print("An instruction file tells a session to WRITE under `.claude/`.")
        print("The host prompts on every edit there and an unattended run has nobody to answer.")
        print()
        for line in problems:
            print(f"  {line}")
        print()
        print("Move the file. `runs/carousel/` is `daily` lane and is not sensitive.")
        return 1

    print("sensitive paths: no instruction file writes under `.claude/`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
