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

WHAT IT MATCHES, and what it leaves alone (Codex, PR 378). A person trailer is any key ending in
`-by` (Co-Authored-By, Signed-off-by, Reviewed-by and the rest), Author, Committer or Cc. It counts
when its value is an identity, meaning a name, an address in brackets or bare, or both, and that
identity is Anthropic's or the assistant's. That is an address on a domain Anthropic owns
(anthropic.com, claude.ai, claude.com), the company as a name, or Claude alone or followed only by
version numbers and product words, `Claude 3.5 Sonnet`, `Claude 4`, `claude-3-opus`, `Claude.ai`.
A comment in parentheses is judged on its own, so `Claude (AI assistant)` is the assistant. A human
whose name merely contains the letters, Claudette, Claude Monet or an anthropology department,
stays. So does a sentence that merely opens with a trailer key, because a sentence is not an
identity. A session trailer, the generated footer, a robot line and a lone session link count
wherever they stand. Every rule is anchored to a whole line, so prose that mentions one stays. A
trailer folded onto an indented second line is read as git joins it, and a message with CRLF line
endings is read the same as one without.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# A person trailer: any key ending in -by, Author, Committer or Cc, with or without a Co- prefix,
# and with the space before the colon git allows.
PERSON = re.compile(r"^[ \t]*(?:[A-Za-z][A-Za-z-]*-by|(?:Co-)?Authors?|(?:Co-)?Committers?|Cc)"
                    r"[ \t]*:[ \t]*(?P<value>.*?)[ \t\r]*$", re.I)
# A value that is an identity and nothing else: a name, an address in angle brackets or bare, or
# both, then an optional comment in parentheses and a closing stop. A sentence that merely opens
# with a trailer key is not one. The body of 6ee1100 on PR 378 held such a sentence, and a rule
# reading the whole line would have had the hook delete it.
IDENTITY = re.compile(r"(?P<name>[^<>@:\n]*?)[ \t]*"
                      r"(?:<(?P<addr>[^<>\n]*)>|(?P<bare>[^\s<>@:]+@[^\s<>@:]+))?[ \t]*"
                      r"(?:\((?P<comment>[^()\n]*)\))?[ \t]*[.,;]?")
# An address on a domain Anthropic owns, a subdomain included, read to the address's end, so
# anthropic.community.example and anthropic.com.example.org are someone else's.
DOMAIN = re.compile(r"@(?:[\w-]+\.)*(?:anthropic\.com|claude\.ai|claude\.com)\.?$", re.I)
# The company as a name: Anthropic, possessive or not, followed only by a company suffix or a
# product or role word. A sentence that opens with the company's name is not an identity, and
# neither is one that opens with the assistant's, which is the next rule down (Codex, PR 378).
ANTHROPIC = re.compile(r"(?:the[ \t]+)?Anthropic(?:'s)?(?:[ \t]+(?:PBC|Inc\.?|LLC|Ltd\.?|AI|Claude|"
                       r"Code|assistant|bot|model|team|staff|agent|app|research|labs?))*", re.I)
# The assistant as a name: Claude alone, or followed only by version numbers and product words,
# `Claude 3.5 Sonnet`, `claude-3-opus`, `Claude.ai`. "Claude Code found the regression" is not.
ASSISTANT = re.compile(r"Claude(?:[- \t.]+(?:\d+(?:\.\d+)*|Code|Opus|Sonnet|Haiku|Fable|Mythos|"
                       r"Instant|AI|Assistant|Agent|Bot|App)\b)*", re.I)
# A comment in parentheses is read on its own, wherever it sits, so `Claude (AI assistant)` is
# judged as the name Claude with a comment beside it.
PAREN = re.compile(r"\(([^()]*)\)")
# The rest are attribution whatever surrounds them on the line: an assistant session trailer, the
# generated footer, a line that opens with the robot emoji and a session link standing alone. A
# carriage return counts as trailing space, so a CRLF message reads the same as an LF one.
OTHER = re.compile(
    r"[ \t]*(?:(?:Claude|Assistant)-Session[ \t]*:.*"
    r"|[*_]*Generated (?:with|by) \[?Claude Code\b.*"
    r"|[*_]*\U0001F916.*"
    r"|[*_]*(?:<?https?://claude\.ai/code/session_[^\s>)]*>?"
    r"|\[[^\]\n]*\]\(https?://claude\.ai/code/session_[^)\s]*\))[*_]*[.,]?"
    r")[ \t\r]*", re.I)
RULE = re.compile(r"^[ \t]*(?:-{3,}|\*{3,}|_{3,})[ \t\r]*$")


# A line git reads as a trailer's first line. Git joins the lines under it that open with
# whitespace onto it with a space, so `Co-Authored-By: Jane` over ` <jane@anthropic.com>` is one
# trailer naming an Anthropic address, and is judged as one.
TRAILER = re.compile(r"^[A-Za-z0-9-]+[ \t]*:")


def attributes(line: str) -> bool:
    """Whether one line, or one trailer as git joins it, is Claude or Anthropic attribution."""
    if OTHER.fullmatch(line):
        return True
    trailer = PERSON.fullmatch(line)
    ident = trailer and IDENTITY.fullmatch(trailer["value"])
    if not ident:
        return False
    comments = PAREN.findall(ident["name"]) + ([ident["comment"]] if ident["comment"] else [])
    name = re.sub(r"\s+", " ", PAREN.sub(" ", ident["name"])).strip().strip('"').strip()
    address = (ident["addr"] or ident["bare"] or "").strip()
    return bool(DOMAIN.search(address) or ANTHROPIC.fullmatch(name) or ASSISTANT.fullmatch(name)
                or any(ANTHROPIC.fullmatch(c.strip()) or ASSISTANT.fullmatch(c.strip())
                       for c in comments))


def scan(lines: list) -> tuple:
    """The indices of the attribution lines, and each as it reads. A trailer counts as git joins it,
    continuation lines and all, and every line is also judged on its own, so an indented line git
    folds into some other trailer still counts."""
    drop, removed, i = set(), [], 0
    while i < len(lines):
        j = i + 1
        if TRAILER.match(lines[i]):
            while j < len(lines) and lines[j][:1] in (" ", "\t") and lines[j].strip():
                j += 1
        joined = " ".join([lines[i].rstrip("\r")] + [ln.strip() for ln in lines[i + 1:j]])
        if attributes(joined):
            drop.update(range(i, j))
            removed.append(joined.strip())
        else:
            for k in range(i, j):
                if attributes(lines[k]):
                    drop.add(k)
                    removed.append(lines[k].strip())
        i = j
    return drop, removed


def offending(text: str) -> list:
    return scan(text.split("\n"))[1]


def strip(text: str) -> tuple:
    """The message without attribution lines, and the lines it took out."""
    lines = text.split("\n")
    drop, removed = scan(lines)
    if not removed:
        return text, []
    lines = [ln for k, ln in enumerate(lines) if k not in drop]
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
            "Signed-off-by: Anthropic <bot@example.com>",
            "Reviewed-by: Helper <bot@anthropic.com>",
            "Assisted-by: Claude Code",
            "Author: Claude <noreply@anthropic.com>",
            "Reviewed-by: bot@anthropic.com",
            "Author: noreply@claude.ai",
            "Signed-off-by: helper@eu.claude.com",
            "Cc: Claude <noreply@anthropic.com>",
            "Committer: Claude <noreply@anthropic.com>",
            "Co-Authored-By: Claude (Anthropic) <x@example.com>",
            "Co-Authored-By: Claude.ai <noreply@example.com>",
            "Co-Authored-By: Claude (AI assistant) <bot@example.com>",
            "Co-Authored-By: Anthropic's Claude <x@example.com>",
            "Co-Authored-By: Jane <jane@example.com> (Anthropic)",
            "Co-Authored-By: Jane Doe <jane@anthropic.com>.",
            "Co-Authored-By : Claude <noreply@anthropic.com>",
            'Reviewed-by: "Claude" <x@example.com>',
            "**\U0001F916 Generated with [Claude Code](https://claude.com/claude-code)**",
            "**Generated with [Claude Code](https://claude.com/claude-code)**",
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
            "Signed-off-by: Talon Sturgill <Talon.sturgill@gmail.com>",
            "Reviewed-by: Claude Monet <monet@example.com>",
            "Reviewed-by: jane@anthropic.community.example",
            "Reviewed-by: jane@notanthropic.com",
            "Reviewed-by: Jane <jane@anthropic.com.example.org>",
            "Cc: Jane Doe <jane@example.com>",
            "Co-Authored-By: Claude.Monet <monet@example.com>",
            'Co-Authored-By: "Claude Monet" <monet@example.com>',
            "Context: Claude 4 is named in a body line that is not a person trailer.",
            "Signed-off-by: Anthropic or Reviewed-by: Helper <bot@anthropic.com> passed both the "
            "hook and CI.",
            "Reviewed-by: Claude, whose tests found the bug, see issue 12: it was real.",
            "Reviewed-by: Claude Code found the regression.",
            "Reviewed-by: Anthropic's tools found the regression.",
            "Co-Authored-By: Jane Doe (formerly of Anthropic) <jane@example.com>",
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
    # A FOLDED TRAILER IS READ AS GIT JOINS IT (git interpret-trailers --parse joins a line that
    # opens with whitespace onto the trailer above it).
    out, removed = strip("Subject\n\nBody.\n\nCo-Authored-By: Jane\n <jane@anthropic.com>\n")
    ok("a trailer folded onto a second line goes whole",
       removed == ["Co-Authored-By: Jane <jane@anthropic.com>"] and out == "Subject\n\nBody.\n",
       repr(out))
    folded = "Subject\n\nCo-Authored-By: Jane Doe\n <jane@example.com>\n"
    ok("a folded human trailer stays whole", strip(folded) == (folded, []), repr(strip(folded)))
    out, removed = strip("Subject\n\nActor: daily\n  Co-Authored-By: Claude\n")
    ok("an indented attribution line git folds into another trailer still goes",
       removed == ["Co-Authored-By: Claude"] and out == "Subject\n\nActor: daily\n", repr(out))

    crlf = "Subject\r\n\r\nBody.\r\n\r\nCo-Authored-By: Claude\r\n---\r\n"
    out, removed = strip(crlf)
    ok("a message with CRLF line endings loses the line and the rule and keeps its endings",
       removed == ["Co-Authored-By: Claude"] and out == "Subject\r\n\r\nBody.\r\n", repr(out))
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
        f.write_bytes(b"Subject\r\n\r\nCo-Authored-By: Jane\r\n <jane@anthropic.com>\r\n"
                      b"Signed-off-by: Jane Doe <jane@example.com>\r\n")
        rc = subprocess.run([sys.executable, __file__, str(f)], capture_output=True).returncode
        want = b"Subject\r\n\r\nSigned-off-by: Jane Doe <jane@example.com>\r\n"
        ok("the hook keeps a CRLF message's other lines byte for byte",
           rc == 0 and f.read_bytes() == want, repr(f.read_bytes()))

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
        # Bytes rather than text mode, because text mode would turn every CRLF into LF and so
        # change lines the hook did not remove.
        out, removed = strip(p.read_bytes().decode("utf-8", errors="surrogateescape"))
        if removed:
            p.write_bytes(out.encode("utf-8", errors="surrogateescape"))
            print("commit-msg: removed Claude attribution lines, which CLAUDE.md forbids on every "
                  "commit", file=sys.stderr)
        return 0
    print("usage: attribution_strip.py <msg-file> | --check-range <range> | --self-test",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
