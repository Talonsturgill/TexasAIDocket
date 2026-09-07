#!/usr/bin/env python3
"""lesson_refs.py — the lesson a citation points at is the lesson it names.

WHY THIS EXISTS

`knowledge/shared/GATE_LESSONS.md` is the file this repository tells every session to read
before adding a gate, trusting one, or believing a green suite. Other files cite it by entry
number, and those citations are how a rule in a script reaches the story that justifies it.

The numbering had drifted badly and nobody could have noticed by reading. Two runs of entries
had been appended over time, each restarting its count, so twelve numbers were used twice and
fifty four entries carried forty two distinct numbers. One live citation already resolved to the
wrong lesson: `daily_routine.md` sent a reader to "entry 26" for the difference between a claim
about today and a claim about the record, and the FIRST entry 26 is about a contrast gate
mis-parsing a colour.

The other three citations were correct, and that is the more useful half of the story. Fixing the
collisions meant renumbering, and renumbering turned all three into references to a different
lesson without touching a character of them. A correct citation becoming wrong because a file it
does not import was reordered is the whole hazard here, and nothing in a diff of that file shows
it.

A citation that resolves to the wrong thing reads exactly like a citation that resolves. That
is `GATE_LESSONS` entry 19 ("A reference is a dependency even when it is not a link") happening
to the file that records it.

WHAT IT ASSERTS

  1. Entries are numbered 1 to N in document order, no gaps and no repeats.
  2. Every citation elsewhere in the repository carries the entry's TITLE beside the number.
     A bare `entry 26` is refused, because a bare number is what let the drift go unseen. The
     title is the redundancy that makes a stale citation detectable.
  3. A cited title matches that entry's real title exactly.
  4. Prose that states how many entries the file holds states the true count.

Rule 2 is the one doing the work. Rules 1, 3 and 4 catch drift after it happens. Rule 2 makes
the next renumber fail loudly instead of silently retargeting every reference in the repository.

    lesson_refs.py               # check the repository
    lesson_refs.py --self-test   # hermetic, replays the four original defects
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

LESSONS = "knowledge/shared/GATE_LESSONS.md"
HEADING = re.compile(r"^## (\d+)\. (.+?)\s*$")
# A citation is the lessons file, then within a short window the word "entry" and a number,
# then optionally the title in quotes. The window and the DOTALL title both exist because a
# citation WRAPS: prose is hard wrapped at 100 columns here, so requiring the whole citation on
# one line would fail on correctly written docs and teach people to write worse ones. The first
# run of this gate did exactly that to a docstring reflowed minutes earlier.
CITE = re.compile(
    r"GATE_LESSONS[^\n]{0,120}?\bentry\s+(\d+)"
    r"(?:\s*\(\"((?:[^\"\\]|\\.){0,200}?)\"\))?",
    re.DOTALL,
)
SCAN_SUFFIXES = (".py", ".md", ".mjs", ".js", ".yaml", ".yml", ".txt", ".json", ".sh")
SKIP_DIRS = {".git", "out", "node_modules", "__pycache__", "docs", "runs", "assets", "vendor"}
COUNT_CLAIM = re.compile(r"`GATE_LESSONS\.md`,\s*(\d+)\s+entries")


def entries(text: str) -> list[tuple[int, str]]:
    """Every numbered entry, in document order."""
    out = []
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            out.append((int(m.group(1)), m.group(2)))
    return out


def check_sequence(ents: list[tuple[int, str]]) -> list[str]:
    """Rule 1. Numbered 1 to N in document order, no gaps and no repeats."""
    bad = []
    for position, (num, title) in enumerate(ents, start=1):
        if num != position:
            bad.append(f"entry at position {position} is numbered {num}: {title}")
    return bad


def sources(root: pathlib.Path) -> list[pathlib.Path]:
    """Every file worth scanning for citations. Generated trees are excluded.

    This file is excluded too, and it is the only named exclusion. Its self-test fixtures are
    deliberately malformed citations, so scanning itself would report a working gate as seven
    violations, and a gate that calls a correct product broken is a gate somebody switches off.
    The carve out cannot widen: it is this one path, resolved, not a pattern.
    """
    mine = pathlib.Path(__file__).resolve()
    frozen = append_only_paths(root)
    out = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix not in SCAN_SUFFIXES:
            continue
        if SKIP_DIRS & set(p.relative_to(root).parts):
            continue
        if p.resolve() == mine:
            continue
        if p.relative_to(root).as_posix() in frozen:
            continue
        out.append(p)
    return out


def append_only_paths(root: pathlib.Path) -> set[str]:
    """The files `ownership.yaml` declares append_only, which this gate may not judge.

    2026-09-07. CI went red on `ledger/carousel/upgrades.json`, which cites a lesson by number
    inside prose describing this gate's own citation format. The obvious fix was to add the
    title, and it does not work: `CITE` wants a literal `("` after the number, a double quote
    inside a JSON string is written `\"`, so the raw bytes read `(\"` and no titled citation is
    spellable in a `.json` file at all. The second fix was to reword the line, and the
    pre-commit hook refused it, correctly: that file is `append_only` because an upgrade trail
    whose author can edit its own history can hide an upgrade.

    **A rule that can only be satisfied by editing a file nobody is permitted to edit is not a
    rule, it is a deadlock.** The trail is a historical record. When a lesson is renumbered, an
    old entry's citation becomes wrong and no actor in this repository may correct it, so
    holding the frozen files to a live consistency rule guarantees a permanent red build for a
    defect that cannot be fixed. They are skipped, and the reason is read out of the map rather
    than hardcoded here, so a path that stops being append_only comes back under the gate
    automatically.

    This is deliberately NOT a suffix or directory rule. Every file the map leaves writable is
    still checked, `.json` included.
    """
    import re as _re
    frozen, path, y = set(), None, (root / "ownership.yaml")
    if not y.exists():
        return frozen
    for line in y.read_text(encoding="utf-8").splitlines():
        m = _re.match(r'\s*-\s*path:\s*"([^"]+)"', line)
        if m:
            path = m.group(1)
            continue
        if path and _re.match(r"\s*append_only:\s*true\b", line):
            frozen.add(path)
            path = None
    return frozen



def frozen_notes(root: pathlib.Path) -> list[str]:
    """Citation drift inside the append_only files, reported and never fatal.

    Same parser, same rules, different disposition. See `append_only_paths` for why these
    files cannot be failed and why that is a property of the ownership map rather than a
    weakness in this gate.
    """
    lessons = root / LESSONS
    if not lessons.is_file():
        return []
    by_num = dict(entries(lessons.read_text(encoding="utf-8")))
    out = []
    for rel in sorted(append_only_paths(root)):
        f = root / rel
        if not f.is_file() or f.suffix not in SCAN_SUFFIXES:
            continue
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for m in CITE.finditer(text):
            num, title = int(m.group(1)), m.group(2)
            line = text.count("\n", 0, m.start()) + 1
            real = by_num.get(num)
            if real is None:
                out.append(f"{rel}:{line} cites entry {num}, which no longer exists. "
                           f"append_only, so this is a note rather than a failure")
            elif title is None:
                out.append(f"{rel}:{line} cites entry {num} with no title. append_only, so "
                           f"this is a note rather than a failure. It is entry {num} "
                           f'("{real}")')
            elif title.replace(chr(92) + chr(34), chr(34)).strip() != real.strip():
                out.append(f"{rel}:{line} cites entry {num} as {title!r} and that entry is "
                           f"{real!r}. append_only, so this is a note rather than a failure")
    return out

def citations(root: pathlib.Path) -> list[tuple[str, int, int, str | None]]:
    """Every `entry N` on a line that names the lessons file. Title captured when present."""
    found = []
    for p in sources(root):
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        if "GATE_LESSONS" not in text:
            continue
        for m in CITE.finditer(text):
            lineno = text.count("\n", 0, m.start()) + 1
            title = m.group(2)
            if title is not None:
                # A wrapped title carries the newline and its indent. Compare on the words.
                title = " ".join(title.split())
            found.append((str(p.relative_to(root)), lineno, int(m.group(1)), title))
    return found


def check_citations(cites, ents) -> list[str]:
    """Rules 2 and 3. A citation carries the title, and the title is the right one."""
    by_num = {num: title for num, title in ents}
    bad = []
    for path, lineno, num, title in cites:
        where = f"{path}:{lineno}"
        if num not in by_num:
            bad.append(f"{where} cites entry {num}, which does not exist")
            continue
        if title is None:
            bad.append(
                f'{where} cites entry {num} with no title. Write it as '
                f'entry {num} ("{by_num[num]}") so a renumber cannot retarget it silently'
            )
            continue
        if title != by_num[num]:
            bad.append(
                f"{where} cites entry {num} as {title!r}, but entry {num} is "
                f"{by_num[num]!r}"
            )
    return bad


def check_counts(root: pathlib.Path, ents) -> list[str]:
    """Rule 4. A stated entry count is the true one."""
    bad = []
    for p in sources(root):
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            m = COUNT_CLAIM.search(line)
            if m and int(m.group(1)) != len(ents):
                bad.append(
                    f"{p.relative_to(root)}:{lineno} says {m.group(1)} entries, "
                    f"the file holds {len(ents)}"
                )
    return bad


def run(root: pathlib.Path) -> list[str]:
    lessons = root / LESSONS
    if not lessons.exists():
        return [f"{LESSONS} does not exist"]
    ents = entries(lessons.read_text(encoding="utf-8"))
    if not ents:
        return [f"{LESSONS} holds no numbered entries, which cannot be right"]
    return (
        check_sequence(ents)
        + check_citations(citations(root), ents)
        + check_counts(root, ents)
    )


CLEAN_LESSONS = """# Lessons

## 1. First lesson
Body.

## 2. Second lesson
Body.
"""


def self_test() -> int:
    """Replay each defect this gate exists for and watch it go red."""
    import tempfile

    checks = []

    def case(name: str, lessons: str, extra: dict[str, str], expect_red: bool):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "knowledge" / "shared").mkdir(parents=True)
            (root / LESSONS).write_text(lessons)
            for rel, body in extra.items():
                p = root / rel
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(body)
            problems = run(root)
            ok = bool(problems) == expect_red
            checks.append(ok)
            print(f"  {'ok  ' if ok else 'FAIL'}  {name}")
            if not ok:
                print(f"        expected {'problems' if expect_red else 'none'}, got {problems}")

    case("a clean corpus passes", CLEAN_LESSONS,
         {"a.md": 'GATE_LESSONS entry 2 ("Second lesson") explains it.'}, False)

    # 2026-09-07. The deadlock: an append_only file cannot be corrected by any actor here, so a
    # live consistency rule over it is a permanent red build for a defect nobody may fix. The
    # pair below is the whole argument. Same citation, same fault, two dispositions, decided by
    # the ownership map rather than by the file's suffix or its directory.
    OWNS = ('- path: "frozen/log.json"\n    append_only: true\n'
            '  - path: "writable/note.md"\n    owner: daily\n')
    case("a bare citation in an append_only file is a note, not a failure", CLEAN_LESSONS,
         {"ownership.yaml": OWNS,
          "frozen/log.json": '{"why": "GATE_LESSONS entry 2 says so"}'}, False)
    case("...and the identical citation in a writable file still fails", CLEAN_LESSONS,
         {"ownership.yaml": OWNS,
          "writable/note.md": "GATE_LESSONS entry 2 says so"}, True)

    # The note has to actually be PRODUCED. A skip that reports nothing is a gate quietly
    # narrowing its own subject, which is the failure mode this file's own header is about.
    with tempfile.TemporaryDirectory() as d:
        root = pathlib.Path(d)
        (root / "knowledge" / "shared").mkdir(parents=True)
        (root / LESSONS).write_text(CLEAN_LESSONS)
        (root / "ownership.yaml").write_text(OWNS)
        (root / "frozen").mkdir()
        (root / "frozen" / "log.json").write_text('{"why": "GATE_LESSONS entry 2 says so"}')
        notes = frozen_notes(root)
        ok = len(notes) == 1 and "entry 2" in notes[0] and "note rather than a failure" in notes[0]
        checks.append(ok)
        print(f"  {'ok  ' if ok else 'FAIL'}  the skipped file's drift is still reported")
        if not ok:
            print(f"        got {notes}")

    # The original defect: two runs of entries, each restarting its count.
    case("duplicate numbering fails",
         "## 1. First lesson\n\n## 1. Restarted count\n", {}, True)

    case("a gap in the numbering fails",
         "## 1. First lesson\n\n## 3. Skipped one\n", {}, True)

    # The form that let the drift go unseen.
    case("a bare citation fails", CLEAN_LESSONS,
         {"a.md": "GATE_LESSONS entry 2 explains it."}, True)

    # The drift itself: number resolves, lesson is the wrong one.
    case("a citation whose title no longer matches fails", CLEAN_LESSONS,
         {"a.md": 'GATE_LESSONS entry 2 ("First lesson") explains it.'}, True)

    case("a citation of an entry that does not exist fails", CLEAN_LESSONS,
         {"a.md": 'GATE_LESSONS entry 9 ("Nothing") explains it.'}, True)

    case("a stale entry count fails", CLEAN_LESSONS,
         {"a.md": "| Postmortems | `GATE_LESSONS.md`, 30 entries, each naming what |"}, True)

    case("a true entry count passes", CLEAN_LESSONS,
         {"a.md": "| Postmortems | `GATE_LESSONS.md`, 2 entries, each naming what |"}, False)

    # A citation on a line that does not name the file is somebody else's word "entry".
    case("an unrelated use of the word entry is not a citation", CLEAN_LESSONS,
         {"a.md": "The ledger entry 5 was written by the collector."}, False)

    # The defect the FIRST run of this gate produced. Prose here is hard wrapped, so a citation
    # spans two lines, and a one-line scanner read the title as absent and failed a correct file.
    case("a citation wrapped across lines is read whole", CLEAN_LESSONS,
         {"a.md": '`GATE_LESSONS` entry 2 ("Second\n         lesson"): the rest of it.'}, False)

    case("a wrapped citation with the wrong title still fails", CLEAN_LESSONS,
         {"a.md": '`GATE_LESSONS` entry 2 ("First\n         lesson"): the rest of it.'}, True)

    passed = sum(checks)
    print(f"\nlesson_refs self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="repository root to check")
    ap.add_argument("--self-test", action="store_true", help="hermetic, no repository read")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    root = pathlib.Path(args.root).resolve()
    problems = run(root)

    # THE FROZEN FILES ARE REPORTED, NEVER FAILED. Skipping them silently would lose 52 live
    # citations from `ledger/carousel/upgrades.json` with nothing said, and a gate that quietly
    # narrows its own subject is the exact shape GATE_LESSONS is a list of. They are read with
    # the same parser and printed as notes, so drift stays visible to a reader while the build
    # does not deadlock on a file nobody is permitted to correct.
    for note in frozen_notes(root):
        print(f"  note  {note}")

    if problems:
        print(f"lesson_refs: {len(problems)} problem(s)")
        for p in problems:
            print(f"  {p}")
        return 1
    print("lesson_refs: every citation names the lesson it points at")
    return 0


if __name__ == "__main__":
    sys.exit(main())
