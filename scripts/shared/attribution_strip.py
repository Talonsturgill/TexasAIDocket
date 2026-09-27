#!/usr/bin/env python3
"""attribution_strip.py — no Claude or Anthropic attribution in a commit message, ever.

    attribution_strip.py <commit-msg-file>        strip it in place (run by .githooks/commit-msg)
    attribution_strip.py --check-range <range>    exit 1 if any commit in the range carries it
    attribution_strip.py --self-test

WHY THIS EXISTS

CLAUDE.md: never author or co-author a commit as Claude or Anthropic. No `Co-Authored-By: Claude`
or Anthropic trailer, no `Claude-Session:` or assistant-session trailer or link, no "Generated
with Claude Code" line. The harness asks every session to add them and a session sometimes does.
Two reached `main` on 2026-09-19, and the runs of September 20th, 21st and 27th each rewrote
pushed history to take them out.

The hook strips them before a commit exists, so there is nothing to rewrite. CI reads every
commit in a pull request's range with `--check-range`, so a commit made without the hook, from a
web edit or an API write, still can't land with one.

WHAT IT MATCHES, and what it leaves alone (Codex, PR 378): a co-author line counts only when its
address is on an Anthropic-owned domain (anthropic.com, claude.ai, claude.com), its name is
Anthropic, or its name is Claude alone or Claude followed by a version number or a product word,
`Claude 3.5 Sonnet`, `Claude 4`, `claude-3-opus`. A human co-author whose name merely contains the
letters, Claudette, Claude Monet or an anthropology department, stays. Prose that
mentions a trailer stays too, because every pattern is anchored to a whole line.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LINE = re.compile(
    r"^[ \t]*(?:"
    r"Co-Authored-By:[ \t]*(?:[^\n<]*<[^>\n]*@(?:[\w.-]+\.)?(?:anthropic\.com|claude\.ai|claude\.com)>"
    r"|Anthropic\b[^\n<]*(?:<[^>\n]*>)?"
    r"|Claude(?:[- \t]+(?:\d+(?:\.\d+)*|Code|Opus|Sonnet|Haiku|Fable|Mythos|Instant|AI|Assistant)\b"
    r"[^\n<]*)?[ \t]*(?:<[^>\n]*>)?)"
    r"|(?:Claude|Assistant)-Session:[^\n]*"
    r"|_?Generated (?:with|by) \[?Claude Code\b[^\n]*"
    r"|\U0001F916[^\n]*"
    r"|[*_]*(?:<?https?://claude\.ai/code/session_[^\s>)]*>?"
    r"|\[[^\]\n]*\]\(https?://claude\.ai/code/session_[^)\s]*\))[*_]*[.,]?"
    r")[ \t]*$", re.I | re.M)
RULE = re.compile(r"^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t]*$")


def offending(text: str) -> list:
    return [m.group(0).strip() for m in LINE.finditer(text)]


def strip(text: str) -> tuple:
    """The message without attribution lines, and the lines it took out."""
    removed = offending(text)
    if not removed:
        return text, []
    lines = [ln for ln in text.split("\n") if not LINE.fullmatch(ln)]
    # A footer usually sits under a horizontal rule. With the footer gone, a rule left at the end
    # of the message separates nothing.
    while lines and (not lines[-1].strip() or RULE.match(lines[-1])):
        lines.pop()
    out = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).rstrip("\n") + "\n"
    return out, removed


def check_range(rng: str) -> int:
    log = subprocess.run(["git", "log", "--format=%H%x1f%B%x1e", rng], capture_output=True,
                         text=True, encoding="utf-8", errors="replace", check=True).stdout
    bad = 0
    for rec in filter(None, (r.strip("\n") for r in log.split("\x1e"))):
        sha, _, body = rec.partition("\x1f")
        for line in offending(body):
            print(f"{sha[:10]}: {line}")
            bad += 1
    if bad:
        print(f"attribution_strip: {bad} attribution line(s) in {rng}. CLAUDE.md forbids them on "
              f"every commit. Reword the commit on this branch, or commit with core.hooksPath set "
              f"to .githooks so the hook strips them first.")
        return 1
    print(f"attribution_strip: no attribution lines in {rng}")
    return 0


def self_test() -> int:
    failures = 0

    def ok(name, cond, detail=""):
        nonlocal failures
        print(("ok    " if cond else "FAIL  ") + name + ("" if cond else f"  {detail}"))
        failures += 0 if cond else 1

    gone = ["Co-Authored-By: Claude <noreply@anthropic.com>",
            "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>",
            "Co-authored-by: Claude Code <noreply@anthropic.com>",
            "Co-Authored-By: Claude",
            "Co-Authored-By: Some Model <bot@anthropic.com>",
            "Co-Authored-By: Claude 3.5 Sonnet <noreply@example.com>",
            "Co-Authored-By: Claude 4 <noreply@example.com>",
            "Co-authored-by: claude-3-opus <bot@example.com>",
            "Co-Authored-By: Claude AI <ai@example.com>",
            "Co-Authored-By: Anthropic <bot@example.com>",
            "Co-Authored-By: Anthropic PBC <legal@example.com>",
            "Co-Authored-By: Helper Bot <noreply@claude.com>",
            "Co-Authored-By: Someone <x@mail.anthropic.com>",
            "Claude-Session: https://claude.ai/code/session_01abc",
            "Assistant-Session: 01abc",
            "\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)",
            "\U0001F916 Claude Code",
            "\U0001F916",
            "_Generated by [Claude Code](https://claude.ai/code/session_01abc)_",
            "https://claude.ai/code/session_01HyKgzQTS8qstm4cYTLbZQ9",
            "[Claude session](https://claude.ai/code/session_01abc)",
            "_[session](https://claude.ai/code/session_01abc)_"]
    kept = ["Co-Authored-By: Claudette Colbert <claudette@example.com>",
            "Co-Authored-By: Claude Monet <monet@example.com>",
            "Co-Authored-By: Claude Debussy <claude.debussy@example.com>",
            "Co-Authored-By: Anthropology Dept <dept@example.edu>",
            "Co-Authored-By: Jane Doe <jane@example.com>",
            'The hook strips lines like "Generated with Claude Code" from messages.',
            "A Claude-Session: trailer mentioned mid-sentence stays.",
            "A robot emoji \U0001F916 mid-sentence stays.",
            "See [the record](https://texasaidocket.com/record/) for the item.",
            "Actor: daily"]
    for line in gone:
        msg = f"Subject\n\nBody.\n\n{line}\n"
        out, removed = strip(msg)
        ok(f"removed: {line[:60]}", removed == [line] and out == "Subject\n\nBody.\n", repr(out))
    for line in kept:
        msg = f"Subject\n\n{line}\n"
        out, removed = strip(msg)
        ok(f"kept: {line[:60]}", not removed and out == msg, repr(out))

    footer = ("Subject\n\nBody.\n\n---\n_Generated by [Claude Code]"
              "(https://claude.ai/code/session_01abc)_\n")
    out, _ = strip(footer)
    ok("a footer's rule goes with the footer", out == "Subject\n\nBody.\n", repr(out))
    mixed = ("Subject\n\nBody.\n\nCo-Authored-By: Jane Doe <jane@example.com>\n"
             "Co-Authored-By: Claude <noreply@anthropic.com>\nActor: daily\n")
    out, _ = strip(mixed)
    ok("a human co-author and the Actor trailer survive beside a removed line",
       out == "Subject\n\nBody.\n\nCo-Authored-By: Jane Doe <jane@example.com>\nActor: daily\n",
       repr(out))

    # A MESSAGE THAT IS NOT UTF-8 IS STILL STRIPPED, and its other bytes survive exactly, because
    # the hook fails closed and a decode error must not be what stops a commit.
    with tempfile.TemporaryDirectory() as t:
        f = Path(t) / "MSG"
        f.write_bytes(b"Subject caf\xe9\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n")
        rc = subprocess.run([sys.executable, __file__, str(f)], capture_output=True).returncode
        ok("a message that is not UTF-8 is stripped and keeps its other bytes",
           rc == 0 and f.read_bytes() == b"Subject caf\xe9\n", repr(f.read_bytes()))

    # THE RANGE CHECK CAN GO RED, measured on a real repository rather than asserted.
    with tempfile.TemporaryDirectory() as t:
        def git(*a):
            return subprocess.run(["git", "-C", t, "-c", "user.name=t", "-c", "user.email=t@t",
                                   "-c", "core.hooksPath=/dev/null", *a],
                                  capture_output=True, text=True, check=True)
        git("init", "-q")
        git("commit", "-q", "--allow-empty", "-m", "base")
        base = git("rev-parse", "HEAD").stdout.strip()
        git("commit", "-q", "--allow-empty", "-m", "clean\n\nActor: daily")
        here = Path.cwd()
        try:
            os.chdir(t)
            clean = check_range(f"{base}..HEAD")
            git("commit", "-q", "--allow-empty", "-m",
                "dirty\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
            dirty = check_range(f"{base}..HEAD")
        finally:
            os.chdir(here)
        ok("--check-range passes a clean range", clean == 0)
        ok("--check-range fails a range with an attribution trailer", dirty == 1)

    print(f"\nattribution_strip self-test: {'all passed' if not failures else f'{failures} FAILED'}")
    return 1 if failures else 0


def main() -> int:
    args = sys.argv[1:]
    if args == ["--self-test"]:
        return self_test()
    if len(args) == 2 and args[0] == "--check-range":
        return check_range(args[1])
    if len(args) == 1 and not args[0].startswith("--"):
        p = Path(args[0])
        # surrogateescape carries bytes that are not UTF-8 through untouched, so a message this
        # can't decode is still stripped rather than crashing the hook, which now fails closed.
        out, removed = strip(p.read_text(encoding="utf-8", errors="surrogateescape"))
        if removed:
            p.write_text(out, encoding="utf-8", errors="surrogateescape")
            print("commit-msg: removed Claude attribution lines, which CLAUDE.md forbids on every "
                  "commit", file=sys.stderr)
        return 0
    print("usage: attribution_strip.py <msg-file> | --check-range <range> | --self-test",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
