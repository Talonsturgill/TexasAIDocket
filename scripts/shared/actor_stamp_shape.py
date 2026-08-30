#!/usr/bin/env python3
"""actor_stamp_shape.py — no instruction file may tell a session to WRITE the actor stamp.

WHY THIS EXISTS, and it is six interruptions of the owner's day across eleven days.

The lane stamp used to be a file. `.githooks/pre-commit` read `.git/ACTOR` to refuse an
out-of-lane write and `.githooks/commit-msg` copied it into the commit as the `Actor:` trailer CI
judges, so every routine wrote it at least twice a run, once at Phase 0 and again around the
retro. That write stopped an unattended run on 2026-08-20, 08-26, 08-27, 08-28, 08-29 and 08-30.

FIVE FIXES, EACH AIMED AT HOW THE FILE WAS WRITTEN.

  1. `.claude/settings.json` grew an allow list of exact command strings.
  2. Then more strings, when a variant appeared.
  3. Then the compound forms, because an allow entry matches ONE command and a session writes
     `echo upgrade > .git/ACTOR && cat .git/ACTOR`.
  4. Then a prose rule: never join the stamp to another command. A session read it the next day,
     understood it, and wrote the stamp inside a six line script anyway.
  5. Then the Write tool, on the reasoning that it takes no shell and produces no command string,
     so the Bash sandbox never sees it and there is nothing to match or chain.

The fifth was a different KIND of fix from the four before it and it still failed, on 2026-08-30,
because the diagnosis under all five was wrong.

WHAT WAS ACTUALLY HAPPENING, measured rather than reasoned about.

In the scheduled cloud runner the repo's own `.claude/settings.json` IS loaded, and its
permission grant is INERT. A cloned repository is not permitted to grant itself
`bypassPermissions`; if it were, cloning any repo would be arbitrary privilege escalation. The
only grant actually in force came from the host's launcher settings, which allowed one tool.

So it was never the sandbox, never the command shape, and never the choice of tool. Four writes
were tested side by side and all four prompted: a shell redirect into `.git/ACTOR`, a `Write` call
to the same path, a `Write` call to an ordinary new file in the working tree, and a shell redirect
to that same ordinary file.

What is NOT established is whether every write prompts, or only the first of its kind in a
session. Runs have shipped here with hundreds of writes, so it is not the former. CLAUDE.md
carries that as a labelled hypothesis and this gate does not depend on which answer is right:
removing a required write is correct either way.

AND A SESSION CANNOT SEE THAT IT PROMPTED. The tool result reads `File created successfully`
whether it was auto-approved or a human tapped approve on a phone an hour later. That is the
second half of why this recurred: each run verified its own fix, honestly, and was wrong.

THE CURE IS THAT NOTHING IS WRITTEN.

The branch already says which lane is acting. `ownership.yaml` maps prefixes to actors, CI has
judged commits that way since 2026-08-16, and `check_per_commit` already falls back to the branch
actor for an unstamped commit. `resolve_actor()` in `scripts/shared/ownership_check.py` reads
`TXDOCKET_ACTOR`, then a stamp file if some other process left one, then the branch prefix, then
`human`. A phase that needs a NARROWER lane than its branch rides the commit it is already
making: `TXDOCKET_ACTOR=upgrade git commit -m ...`, which git exports to both hooks and which
costs no extra tool call at all.

WHY A CHECKER AND NOT A SIXTH PARAGRAPH.

This repo's own doctrine, stated in CLAUDE.md three times over: a rule stated in config with
nothing checking it is a rule that ships broken. Four of the five failed fixes were prose, and
prose is what the session read and then contradicted. This reads the instruction files and fails
the build if any of them tells a session to write the stamp BY ANY MEANS, so the instruction a
future run receives cannot be the one that breaks it.

Note what changed here on 2026-08-30. This gate used to bless `Write tool` as the sanctioned
phrasing and fail only on a shell redirect. That exemption was the fifth fix, and it is now
exactly the thing being caught: an instruction to write the stamp with the Write tool prompts
just the same, so blessing it would keep the defect alive under a checker reporting green.

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
# that decide whether a run prompts. Anything else naming the stamp is describing the mechanism
# rather than instructing a write, and this checker deliberately does not police prose.
INSTRUCTION_GLOBS = (
    "CLAUDE.md",
    "prompts/*.md",
    ".claude/skills/*/SKILL.md",
    ".claude/agents/*.md",
)

# A SHELL redirect, a tee, or a heredoc landing on the stamp. Written against the REDIRECT rather
# than against echo, so a session reaching for `tee` or `cat >` is caught too.
SHELL_WRITE = re.compile(
    r"""(?:>>?\s*|\|\s*tee\s+(?:-a\s+)?)['"`]?(?:\./)?\.git/ACTOR""",
    re.IGNORECASE,
)

# A TOOL write, which is the shape the fifth fix introduced and which prompts exactly as hard.
# `Write ... .git/ACTOR` in either order, on one line, is an instruction to make the call.
TOOL_WRITE = re.compile(
    r"(?:write\s+tool[^\n]*\.git/ACTOR|\.git/ACTOR[^\n]*write\s+tool)",
    re.IGNORECASE,
)

# Any imperative to put a value into the stamp, however the file is reached. This is the general
# case the two patterns above are the known instances of.
VERB_WRITE = re.compile(
    r"(?:write|stamp|put|set|save|create)\s+(?:[^\n]{0,60}?\s+)?(?:in|into|to|at)\s+"
    r"['\"`]?(?:\./)?\.git/ACTOR",
    re.IGNORECASE,
)

PATTERNS = (SHELL_WRITE, TOOL_WRITE, VERB_WRITE)

# A markdown heading, for the section scope below.
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")

# The heading that marks a section as the RULE's own explanation, where the mistakes have to be
# quoted in order to be warned against. Deliberately narrow: it takes these literal words, so a
# file cannot wave the gate away with a synonym.
SANCTIONED_HEADING = "never written"


def offending_lines(text: str) -> list[tuple[int, str]]:
    """Every line that TELLS somebody to write the stamp, by any mechanism.

    One exemption, and it exists because the previous version of this gate went red on its first
    CI run against the very file that documents it. Any line inside a SECTION whose own heading
    says the stamp is `never written` is teaching rather than telling: CLAUDE.md's rule has to
    quote `echo upgrade > .git/ACTOR` and "write `daily` to `.git/ACTOR` with the Write tool" in
    order to explain why neither of them held.

    The section is the right unit for that distinction rather than the line, because the
    paragraph explaining a mistake is necessarily several lines long and the quote lands on only
    one of them. Scoping it to a heading keeps the gate strict everywhere else: a write
    instruction under any other heading, in any of these files, is still caught. The exemption
    ends at the next heading of any level, so it cannot leak down the document, and the self-test
    asserts exactly that.
    """
    out: list[tuple[int, str]] = []
    in_rule_section = False
    for i, line in enumerate(text.splitlines(), 1):
        head = HEADING.match(line)
        if head:
            in_rule_section = SANCTIONED_HEADING in head.group(1).lower()
            continue
        if in_rule_section:
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
                rel = path.relative_to(root)
                problems.append(f"{rel}:{lineno}: {line}")
    return problems


def self_test() -> int:
    """Prove the checker can go red, which is the only thing a self-test is for.

    GATE_LESSONS' standing complaint is a checker that has never failed and is therefore not
    known to be connected to anything. Every shape that actually stopped a run is walked here,
    including the one this gate used to bless.
    """
    checks: list[tuple[str, bool]] = []

    bad = "2. Stamp the actor so both checkers enforce your lane: `echo daily > .git/ACTOR`."
    checks.append(("the shell redirect that wedged five runs is CAUGHT", bool(offending_lines(bad))))

    compound = "`echo upgrade > .git/ACTOR && cat .git/ACTOR`, then spawn the engineer."
    checks.append(("the compound form the allow list could not match is CAUGHT",
                   bool(offending_lines(compound))))

    printf = "run `printf daily >> .git/ACTOR` before committing"
    checks.append(("append and printf are caught, because the pattern reads the redirect",
                   bool(offending_lines(printf))))

    tee = "pipe it: `echo ask | tee .git/ACTOR`"
    checks.append(("a tee onto the stamp is CAUGHT", bool(offending_lines(tee))))

    # THE CASE THIS GATE USED TO BLESS, which is the whole point of the 2026-08-30 rewrite.
    tool = "2. Stamp the actor with the Write tool: write `daily` to `.git/ACTOR`."
    checks.append(("the Write tool instruction, the FIFTH failed fix, is now CAUGHT",
                   bool(offending_lines(tool))))

    tool_rev = "Use the Write tool to put `upgrade` in `.git/ACTOR`. Never a shell command."
    checks.append(("...in either word order, and the 'never a shell command' half does not "
                   "excuse it", bool(offending_lines(tool_rev))))

    verb = "Write `upgrade` into `.git/ACTOR` before you spawn the engineer."
    checks.append(("a bare imperative naming no tool at all is CAUGHT", bool(offending_lines(verb))))

    describes = "The commit-msg hook honours an `ACTOR` file if some other process left one."
    checks.append(("prose describing the mechanism is NOT policed", not offending_lines(describes)))

    cure = "Declare a narrower lane on the commit itself: `TXDOCKET_ACTOR=upgrade git commit`."
    checks.append(("the cure passes", not offending_lines(cure)))

    # THE SECTION SCOPE, which is the half the previous checker did not have when CI first ran it
    # and it failed the build against CLAUDE.md's own explanation of the rule.
    teaching = ("## The actor stamp is never written\n"
                "An allow entry matches ONE command, so `echo upgrade > .git/ACTOR && cat "
                ".git/ACTOR`\nmatched nothing. Writing `daily` to `.git/ACTOR` with the Write "
                "tool prompted too.\n")
    checks.append(("both mistakes QUOTED inside the rule's own section are exempt",
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

    # The real files, which are the cases that actually go red in CI.
    for name in ("CLAUDE.md", "prompts/daily_routine.md"):
        real = REPO_ROOT / name
        if real.exists():
            checks.append((f"{name} scans clean",
                           not offending_lines(real.read_text(encoding="utf-8"))))

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "prompts").mkdir()
        (root / "prompts" / "x_routine.md").write_text(bad, encoding="utf-8")
        checks.append(("a real instruction file under prompts/ is FOUND by the scan",
                       bool(scan(root))))
        (root / "prompts" / "x_routine.md").write_text(cure, encoding="utf-8")
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
        print("actor stamp: no instruction file tells a session to write the stamp")
        return 0

    print(f"actor_stamp_shape: {len(problems)} instruction(s) tell a session to write the stamp\n")
    for p in problems:
        print(f"  - {p}")
    print(
        "\n  Nothing has to be written to declare a lane, and requiring it stopped six\n"
        "  unattended runs. In the scheduled cloud runner this repo's own permission grant is\n"
        "  inert, because a cloned repository may not grant itself bypassPermissions, so EVERY\n"
        "  write prompts a human who is not there. The tool does not matter and the path does\n"
        "  not matter: a shell redirect, a Write call and an ordinary file in the tree all\n"
        "  prompt the same. A session cannot even see that it prompted.\n\n"
        "  The branch already names the lane. If a phase needs a NARROWER one, declare it on\n"
        "  the commit it is already making:  TXDOCKET_ACTOR=upgrade git commit -m ...\n"
        "  See resolve_actor() in scripts/shared/ownership_check.py."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
