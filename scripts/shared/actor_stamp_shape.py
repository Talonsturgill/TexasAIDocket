#!/usr/bin/env python3
"""actor_stamp_shape.py — no instruction file may tell a session to SHELL the actor stamp.

WHY THIS EXISTS, and it is five interruptions of the owner's day.

`.git/ACTOR` is the lane stamp. `.githooks/pre-commit` reads it to refuse an out-of-lane write
and `.githooks/commit-msg` copies it into the commit as the `Actor:` trailer CI judges. Every run
writes it at least twice, once at Phase 0 and twice more around the retro.

The routine told every session to write it with `echo daily > .git/ACTOR`, and that one shell
redirect wedged an unattended run on 2026-08-20, 08-26, 08-27, 08-28 and 08-29.

WHAT ACTUALLY ASKS, because four earlier diagnoses each got a piece of it.

The Bash SANDBOX is a different mechanism from the permission mode. `.git/` is inside the working
tree and outside what the sandbox will write to, so a sandboxed redirect into it cannot complete
and the tool asks to re-run unsandboxed. `bypassPermissions` does not cover that prompt. Neither
does the scratch rule in CLAUDE.md, because the stamp has nowhere else to live: the commit-msg
hook reads exactly that path.

`.claude/settings.json` then grew an allow list of the exact command strings. It did not hold,
because an allow entry matches a COMMAND and a session writes compounds. `echo upgrade >
.git/ACTOR && cat .git/ACTOR` is not `echo upgrade > .git/ACTOR`, and neither is the same write
buried in a six line heredoc script with a `git add` and a checker after it. Chaining is
unbounded and no list can enumerate it.

So on 2026-08-28 the settings file wrote the rule in prose instead: never join the stamp to
another command. On 2026-08-29 a session read that file, understood it, and then wrote the stamp
inside a compound anyway, twice, and stopped the run both times.

THE CURE IS NOT A SHELL COMMAND AT ALL.

The `Write` tool writes `.git/ACTOR` directly. No shell, so no sandbox. No command string, so
nothing to match and nothing to chain. It cannot prompt, whatever else the session puts in the
same turn. That is a different KIND of fix from the four before it, which all tried to make a
shell command safe, and it is why this one is enforced rather than written down again.

WHY A CHECKER AND NOT A FIFTH PARAGRAPH.

This repo's own doctrine, stated in CLAUDE.md three times over: a rule stated in config with
nothing checking it is a rule that ships broken. The last four attempts at this were all prose.
Prose is what the session read and then contradicted. This reads the instruction files and fails
the build if any of them still tells a session to shell the stamp, so the instruction a future
run receives cannot be the one that breaks it.

    python3 scripts/shared/actor_stamp_shape.py
    python3 scripts/shared/actor_stamp_shape.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The instruction surfaces. A session reads these and does what they say, so these are the files
# that decide whether a run prompts. Anything else naming .git/ACTOR is describing the mechanism
# rather than instructing a write, and this checker deliberately does not police prose.
INSTRUCTION_GLOBS = (
    "CLAUDE.md",
    "prompts/*.md",
    ".claude/skills/*/SKILL.md",
    ".claude/agents/*.md",
)

# A shell redirect, a tee, or a heredoc landing on the stamp. The forms seen in this repo were
# `echo daily > .git/ACTOR` and `printf upgrade > .git/ACTOR`; the pattern is written against the
# REDIRECT rather than against echo, so a session reaching for `tee` or `cat >` is caught too.
SHELL_WRITE = re.compile(
    r"""(?:>>?\s*|\|\s*tee\s+(?:-a\s+)?)['"`]?(?:\./)?\.git/ACTOR""",
    re.IGNORECASE,
)

# The one phrasing that is correct, so a file can say what to do instead without tripping itself.
SANCTIONED = "Write tool"

# A markdown heading, for the section scope below.
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")


def offending_lines(text: str) -> list[tuple[int, str]]:
    """Every line that TELLS somebody to redirect a shell stream into the stamp.

    Two exemptions, and the second one exists because this gate went red on its first CI run
    against the very file that documents it.

    ONE, a line naming the `Write tool`, which is how the cure is written down beside the mistake
    it replaces. Narrow on purpose: it takes the literal words, so a file cannot wave it away with
    a synonym.

    TWO, any line inside the SECTION whose own heading names the `Write tool`. CLAUDE.md's rule
    for this stamp has to quote `echo upgrade > .git/ACTOR && cat .git/ACTOR` in order to explain
    why an allow list could never match it, and the first version of this checker read that
    sentence as an instruction and failed the build. It was not wrong that a redirect was present.
    It could not tell TEACHING from TELLING.

    The section is the right unit for that distinction rather than the line, because the paragraph
    explaining a mistake is necessarily several lines long and the quote lands on only one of them.
    Scoping it to a heading keeps the gate strict everywhere else: a redirect under any other
    heading, in any of these files, is still caught. The exemption ends at the next heading of any
    level, so it cannot leak down the document, and the self-test asserts exactly that.
    """
    out: list[tuple[int, str]] = []
    in_rule_section = False
    for i, line in enumerate(text.splitlines(), 1):
        head = HEADING.match(line)
        if head:
            in_rule_section = SANCTIONED in head.group(1)
            continue
        if not SHELL_WRITE.search(line):
            continue
        if SANCTIONED in line or in_rule_section:
            continue
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
                rel = path.relative_to(root)
                problems.append(f"{rel}:{lineno}: {line}")
    return problems


def self_test() -> int:
    """Prove the checker can go red, which is the only thing a self-test is for.

    GATE_LESSONS' standing complaint is a checker that has never failed and is therefore not known
    to be connected to anything. Both halves are walked: the shape that wedged five runs, and the
    shape that replaces it.
    """
    checks: list[tuple[str, bool]] = []

    bad = "2. Stamp the actor so both checkers enforce your lane: `echo daily > .git/ACTOR`."
    checks.append(("the exact instruction that wedged five runs is CAUGHT", bool(offending_lines(bad))))

    compound = "`echo upgrade > .git/ACTOR && cat .git/ACTOR`, then spawn the engineer."
    checks.append(("the compound form the allow list could not match is CAUGHT",
                   bool(offending_lines(compound))))

    printf = "run `printf daily >> .git/ACTOR` before committing"
    checks.append(("append and printf are caught too, because the pattern reads the redirect",
                   bool(offending_lines(printf))))

    tee = "pipe it: `echo ask | tee .git/ACTOR`"
    checks.append(("a tee onto the stamp is CAUGHT", bool(offending_lines(tee))))

    good = "2. Stamp the actor with the Write tool: write `daily` to `.git/ACTOR`."
    checks.append(("the cure passes", not offending_lines(good)))

    describes = "The commit-msg hook copies whatever is in `.git/ACTOR` into the message."
    checks.append(("prose describing the mechanism is NOT policed", not offending_lines(describes)))

    excuse = "`echo daily > .git/ACTOR` is fine here because it is a special case"
    checks.append(("a line cannot excuse itself without naming the Write tool",
                   bool(offending_lines(excuse))))

    # THE SECTION SCOPE, which is the half this checker did not have when CI first ran it and it
    # failed the build against CLAUDE.md's own explanation of the rule.
    teaching = ("## Write the actor stamp with the Write tool, never a shell command\n"
                "An allow entry matches ONE command, so `echo upgrade > .git/ACTOR && cat .git/ACTOR`\n"
                "matched nothing and went to approval.\n")
    checks.append(("a redirect QUOTED inside the rule's own section is exempt",
                   not offending_lines(teaching)))

    telling = ("## Phase 0, wake\n"
               "2. Stamp the actor: `echo daily > .git/ACTOR`.\n")
    checks.append(("...but the same line under any other heading is still CAUGHT",
                   bool(offending_lines(telling))))

    leaks = (teaching + "\n## Scratch never leaves the working tree\n"
             "Then run `echo daily > .git/ACTOR` before you commit.\n")
    found = offending_lines(leaks)
    checks.append(("...and the exemption does NOT leak past the next heading",
                   len(found) == 1 and "Scratch" not in found[0][1]))

    # The real file, which is the case that actually went red in CI.
    claude_md = REPO_ROOT / "CLAUDE.md"
    if claude_md.exists():
        checks.append(("CLAUDE.md's own rule section scans clean",
                       not offending_lines(claude_md.read_text(encoding="utf-8"))))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "prompts").mkdir()
        (root / "prompts" / "x_routine.md").write_text(bad, encoding="utf-8")
        checks.append(("a real instruction file under prompts/ is FOUND by the scan",
                       bool(scan(root))))
        (root / "prompts" / "x_routine.md").write_text(good, encoding="utf-8")
        checks.append(("...and a clean tree scans green", not scan(root)))

    failed = 0
    for name, ok in checks:
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
        failed += 0 if ok else 1
    if failed:
        print(f"\nactor_stamp_shape self-test: {failed} FAILED")
        return 1
    print("\nactor_stamp_shape self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(REPO_ROOT))
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    problems = scan(Path(args.root))
    if not problems:
        print("actor stamp: no instruction file shells the stamp")
        return 0

    print(f"actor_stamp_shape: {len(problems)} instruction(s) tell a session to shell the stamp\n")
    for p in problems:
        print(f"  - {p}")
    print(
        "\n  `.git/ACTOR` is inside the working tree and outside what the Bash sandbox will\n"
        "  write to, so a shell redirect into it asks to re-run unsandboxed. That prompt is not\n"
        "  covered by bypassPermissions and it has no one to answer it in an unattended run.\n"
        "  An allow list cannot fix it either, because an entry matches one command string and a\n"
        "  session writes compounds.\n\n"
        "  Write the stamp with the Write tool instead. No shell, nothing to match, nothing to\n"
        "  chain, and it cannot prompt whatever else shares the turn."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
