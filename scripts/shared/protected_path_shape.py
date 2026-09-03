#!/usr/bin/env python3
"""No instruction file may tell a session to WRITE inside `.claude/` or `.git/`.

THE DEFECT THIS EXISTS FOR, and it is the same defect twice under two different filenames.

    2026-08-20 to 2026-08-30   six scheduled runs stopped writing `.git/ACTOR`
    2026-08-30 to 2026-09-03   five scheduled runs stopped writing the worklog

Eleven interrupted runs, two files, one cause. Both live in a directory the HARNESS gates
regardless of the permission mode, because both directories carry things that define what the
agent may do: `.git/hooks/` executes on every commit, and `.claude/` holds `settings.json` and
the hook definitions that set the session's own permissions. A tool that could write there
unattended could grant itself anything, so the approval is a security property rather than a
bug, and it is the same property that stops a cloned repository granting itself
`bypassPermissions`.

WHAT WAS MEASURED ON 2026-09-03, because the earlier diagnosis was wrong for eleven days.

`~/.claude/settings.json` was read in a live scheduled run and it carried
`permissions.defaultMode: bypassPermissions`, written by the SessionStart hook exactly as
designed. The run then wrote `.claude/WORKLOG.md` and the owner was interrupted anyway. That
single observation falsifies the standing hypothesis, which held that the FIRST gated write of
a session is what stops it and that the cure was a permission grant. The mode was granted. The
write still asked.

It also explains why every earlier fix failed. Four of them changed HOW the stamp was written
and the fifth changed WHICH TOOL wrote it, and the gating is on neither: it is on WHERE. The
one variable nobody moved was the directory.

WHY THE 2026-08-30 PROBE POINTED THE WRONG WAY. That run wrote four files side by side, two of
them ordinary paths in the working tree, and recorded that all four prompted. It could not have
known. A tool result reads `File created successfully` whether it was auto-approved or approved
by a human an hour later, which that same run wrote down two paragraphs above its own
conclusion. The only reliable observer of a prompt is the person it interrupts, and the owner
has only ever reported two, the lane stamp and the worklog. Both under a gated
directory. Meanwhile runs here have shipped hundreds of writes to `out/`, `ledger/`, `docs/`
and `runs/` without stopping once, which is the control the probe never had.

WHAT IS ESTABLISHED, and it is narrower than the paragraph above may read.

  established   `bypassPermissions` was in force at the user level and a `.claude/` write still
                prompted, so the mode is not the lever
  established   ordinary tracked paths do not stop these runs, over hundreds of writes
  established   moving the stamp out of `.git/` ended six runs' worth of interruptions
  NOT           the precise rule the harness applies. Whether it is these two directories by
                name, a wider protected set, or a per-file rule, is not visible from inside a
                session and this gate does not guess. It polices the two paths that have
                actually cost runs.

WHY A CHECKER AND NOT ANOTHER PARAGRAPH. This repo's oldest lesson, stated in CLAUDE.md and in
GATE_LESSONS: a rule written in prose with nothing checking it is a rule that ships broken.
Five of the six fixes to the stamp were prose, and prose is what the next session read and then
contradicted. This reads the instruction files and fails the build if any of them sends a run
back into a gated directory with a write, so the instruction a future run receives cannot be
the one that stops it.

    python3 scripts/shared/protected_path_shape.py
    python3 scripts/shared/protected_path_shape.py --self-test
"""
from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The instruction surfaces. A session reads these and does what they say, so these are the files
# that decide whether a run prompts. Anything else naming a path under a gated directory is
# describing the mechanism rather than instructing a write.
INSTRUCTION_GLOBS = (
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "prompts/*.md",
    ".claude/skills/*/SKILL.md",
    ".claude/agents/*.md",
)

# The directories the harness gates. Named one by one rather than by a pattern, because this is
# a list of what has actually cost this project runs and not a theory about what might.
GATED = r"(?:\.claude|\.git)"

# A path under a gated directory, with an optional leading `./`. `.github/` and `.githooks/` are
# ordinary tracked directories and must NOT match, so the boundary after the directory name is
# required to be a slash.
GATED_PATH = rf"['\"`]?(?:\./)?{GATED}/[A-Za-z0-9_.*/-]+"

# A SHELL redirect, a tee, or a heredoc landing inside a gated directory. Written against the
# REDIRECT rather than against echo, so `tee` and `cat >` are caught too.
SHELL_WRITE = re.compile(
    rf"(?:>>?\s*|\|\s*tee\s+(?:-a\s+)?){GATED_PATH}",
    re.IGNORECASE,
)

# A TOOL write. `Write ... .claude/x` in either order, on one line, is an instruction to make
# the call. This is the shape the stamp's fifth and last failed fix took.
TOOL_WRITE = re.compile(
    rf"(?:write\s+tool[^\n]*{GATED_PATH}|{GATED_PATH}[^\n]*write\s+tool)",
    re.IGNORECASE,
)

# Any imperative to put something into a gated path, however the file is reached. This is the
# general case the two patterns above are the known instances of.
VERB_WRITE = re.compile(
    rf"(?:write|stamp|put|save|create|append)\s+(?:[^\n]{{0,60}}?\s+)?(?:in|into|to|at)\s+"
    rf"{GATED_PATH}",
    re.IGNORECASE,
)

# A shell command whose whole job is making a file there.
MAKE_WRITE = re.compile(
    rf"(?:touch|mkdir(?:\s+-p)?|cp|mv)\s+(?:[^\n]{{0,60}}?\s+)?{GATED_PATH}",
    re.IGNORECASE,
)

# RETIRED PATHS, and this is the pattern that actually catches the regression.
#
# The four above are line scoped, and the instruction that cost five runs was not on one line.
# CLAUDE.md named `.claude/WORKLOG.md` in one sentence and said "Write one at the START of any
# task too large for a single context" in the next, which is an unmistakable instruction to
# write there and matches no single-line pattern. Rather than guess at paragraph scope, this
# takes the narrower and harder fact: neither file exists any more, so an instruction file
# naming one at all, outside a section teaching why it went, means somebody put it back.
#
# A retired path earns its place on this list by having interrupted a run. Do not add a path
# here on suspicion, and do not remove one because the mention looks harmless: the mention IS
# the regression, since there is nothing left at either address to legitimately reference.
#
# The worklog is retired OUTRIGHT rather than relocated, on the owner's instruction of
# 2026-09-03, so the bare filename is matched at any path. `run_state.json` already carried the
# resume state the worklog existed for, which is why the answer here was deletion and not a
# safer address. `DATACENTER_DOSSIER_WORKLOG.md` and the shipped `runs/**/WORKLOG.md` archives
# are deliberately not matched: the word boundary requires the name to stand alone, and the
# instruction globs never reach `runs/` or `knowledge/`.
RETIRED_PATHS = (
    re.compile(r"(?<![A-Za-z0-9_])WORKLOG\.md", re.IGNORECASE),
    re.compile(r"(?:\./)?\.git/ACTOR", re.IGNORECASE),
)

PATTERNS = (SHELL_WRITE, TOOL_WRITE, VERB_WRITE, MAKE_WRITE) + RETIRED_PATHS

# A markdown heading, for the section scope below.
HEADING = re.compile(r"^\s{0,3}#{1,6}\s+(.*)$")

# The headings that mark a section as a RULE's own explanation, where the mistakes have to be
# quoted in order to be warned against. Deliberately narrow: they take these literal words, so a
# file cannot wave the gate away with a synonym. Two of them, because the stamp and the worklog
# are the same defect under two filenames and each already has its own account written up.
SANCTIONED_HEADINGS = ("protected director", "never written", "no worklog")


def offending_lines(text: str) -> list[tuple[int, str]]:
    """Every line that TELLS somebody to write inside a gated directory.

    One exemption, and it is the same one `actor_stamp_shape.py` needs for the same reason. Any
    line inside a SECTION whose own heading names protected directories is teaching rather than
    telling: CLAUDE.md's rule has to quote the two writes that cost eleven runs in order to
    explain why neither of them held.

    The section is the right unit rather than the line, because the paragraph explaining a
    mistake is several lines long and the quote lands on only one of them. Scoping it to a
    heading keeps the gate strict everywhere else, the exemption ends at the next heading of any
    level so it cannot leak down the document, and the self-test asserts exactly that.
    """
    out: list[tuple[int, str]] = []
    in_rule_section = False
    for i, line in enumerate(text.splitlines(), 1):
        head = HEADING.match(line)
        if head:
            low = head.group(1).lower()
            in_rule_section = any(s in low for s in SANCTIONED_HEADINGS)
            continue
        if in_rule_section:
            continue
        if any(p.search(line) for p in PATTERNS):
            out.append((i, line.strip()))
    return out


def scan(root: Path) -> list[tuple[Path, int, str]]:
    found: list[tuple[Path, int, str]] = []
    for glob in INSTRUCTION_GLOBS:
        for path in sorted(root.glob(glob)):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for line_no, line in offending_lines(text):
                found.append((path.relative_to(root), line_no, line))
    return found


CASES = 18


def self_test() -> int:
    """Replay the two writes that stopped eleven runs, and the shapes around them."""
    failures: list[str] = []

    def check(name: str, text: str, want_hit: bool) -> None:
        hits = offending_lines(text)
        if bool(hits) != want_hit:
            verb = "missed" if want_hit else "wrongly flagged"
            failures.append(f"{name}: {verb}\n    {text.strip()[:110]}")

    # The two that actually cost runs.
    check("worklog write tool",
          "Write one at the START of any task too large for a single context. Use the Write "
          "tool to create `.claude/WORKLOG.md` before touching code.", True)
    check("worklog verb",
          "Write your durable plan into `.claude/WORKLOG.md` before you begin.", True)
    check("actor stamp redirect",
          "2. Stamp the actor so both checkers enforce your lane: `echo daily > .git/ACTOR`.",
          True)
    check("actor stamp tee",
          "Run `printf upgrade | tee .git/ACTOR` before you spawn the engineer.", True)
    check("touch",
          "First `touch .claude/WORKLOG.md` so the next context finds it.", True)
    check("settings write",
          "Save the mode into `.claude/settings.json` and carry on.", True)

    # The regression that four line-scoped patterns all miss, and the reason RETIRED_PATHS
    # exists. This is CLAUDE.md's own wording, and it is what five runs actually read.
    check("retired path, split across lines",
          "If `.claude/WORKLOG.md` exists, READ IT FIRST. It is the durable plan.\n"
          "Write one at the START of any task too large for a single context.", True)
    check("retired worklog at ANY address, since it was deleted not moved",
          "- `WORKLOG.md` at the repository root if it exists, the durable plan.", True)
    check("worklog named bare in an instruction",
          "Resume from the WORKLOG.md table and update it after every commit.", True)
    check("retired stamp merely named",
          "The lane used to be declared in `.git/ACTOR` and a run should keep it current.", True)

    # Running and describing are fine, and a gate that failed on these would push the next
    # writer to stop documenting the mechanism at all.
    check("run a script is fine",
          "python3 .claude/skills/carousel-engine/render.py --slides-dir out/x/slides", False)
    check("hooks path is fine",
          "Point git at the hooks with `git config core.hooksPath .githooks`.", False)
    check("githooks is not gated",
          "Write the new check into `.githooks/pre-commit` and make it executable.", False)
    check("github workflows not gated",
          "Add the step to `.github/workflows/guards.yml` in the same commit.", False)
    check("the replacement is fine",
          "Write `out/<date>/run_state.json` at wake and stamp each phase done.", False)
    check("a longer name is not the retired one",
          "`knowledge/shared/DATACENTER_DOSSIER_WORKLOG.md` is the facility handoff.", False)

    # The section exemption, and the assertion that it ends at the next heading.
    teaching = (
        "## The write that never happens, and protected directories\n"
        "Never `echo daily > .git/ACTOR`, and never write `.claude/WORKLOG.md`.\n"
        "## Some other heading\n"
        "Write the plan into `.claude/WORKLOG.md` before you start.\n"
    )
    hits = offending_lines(teaching)
    if [h[0] for h in hits] != [4]:
        failures.append(
            "section exemption: expected the line under the LATER heading only, got "
            f"{[h[0] for h in hits]}"
        )

    # And the gate must go red on a real file, not just on strings.
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "prompts").mkdir()
        (root / "prompts" / "x.md").write_text(
            "# Phase 0\n\nWrite `daily` into `.git/ACTOR` before you commit.\n"
        )
        if not scan(root):
            failures.append("scan: a planted instruction file did not go red")
        (root / "prompts" / "x.md").write_text(
            "# Phase 0\n\nRead `out/<date>/run_state.json` first.\n"
        )
        if scan(root):
            failures.append("scan: a clean instruction file went red")

    if failures:
        print("protected_path_shape self-test: FAIL")
        for f in failures:
            print("  " + f)
        return 1
    print(f"protected_path_shape self-test: ok, {CASES} case(s)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true",
                    help="prove the gate can go red, then exit")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    found = scan(REPO_ROOT)
    if not found:
        print("protected_path_shape: clean, no instruction file writes into .claude/ or .git/")
        return 0

    print("protected_path_shape: FAIL")
    print()
    print("  An instruction file tells a session to write inside a directory the harness gates.")
    print("  That write asks a human for approval whatever the permission mode says, and an")
    print("  unattended run has nobody to ask. Eleven scheduled runs stopped this way.")
    print()
    for path, line_no, line in found:
        print(f"  {path}:{line_no}")
        print(f"      {line}")
    print()
    print("  The cure is never a reword and never a broader permission. Move the file to an")
    print("  ordinary tracked path and name its owner in ownership.yaml. See CLAUDE.md under")
    print("  the heading about protected directories.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
