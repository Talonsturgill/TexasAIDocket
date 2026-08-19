#!/usr/bin/env python3
"""lastmod.py — the date a page actually changed, for the footer and for the sitemap.

WHY THIS EXISTS

Two surfaces published the same untruth, and both were doing it 222 times a day.

`sitemap.xml` stamped every url with the build date, so the record told Google that all 222
pages changed this morning. They did not. `/about/` had not changed in days. Google's stated
position on this is not subtle: a `lastmod` it finds unreliable is a `lastmod` it stops
reading, and a site that claims everything changed today has told it exactly once that the
field is worthless. The signal that is supposed to say "this page is worth recrawling" was
being spent on 222 pages that were not.

The page footer said it out loud too. "Revised August 19th, 2026" ran under every page on
the site, including the ones whose last real edit was a week earlier. A reader has no way to
check that, which is what made it the wrong thing to print.

The cause was the same in both places and it was not laziness. There was no per page revision
date to print, because nothing computed one. So both surfaces reached for the build date,
which is always available and is never the answer.

WHAT IT COMPUTES, AND WHY GIT IS THE SOURCE

A page's revision date is the date its PUBLISHED BYTES last changed. `docs/` is generated and
committed, so git already holds that record exactly, with no new state to keep and nothing to
get out of step. This is the repo's own argument for `last_verified` reused: the provenance of
a value is the file's own history, which is a stronger trace than a field somebody maintains.

So, for each page:

  built bytes == the bytes at HEAD  ->  the date of the last commit that touched that file
  built bytes != the bytes at HEAD  ->  today, because today is when it changed

THE STAMP IS NORMALISED OUT OF BOTH SIDES BEFORE THEY ARE COMPARED. The footer prints the
revision date, so a page carrying its own date cannot be compared against a page carrying a
different one without every page differing from itself every day. That is a loop, and it is
the reason the naive version of this fix does nothing at all: with the date rendered in, every
page differs from HEAD every morning and every `lastmod` comes back as today, which is what it
already said. `page()` renders the placeholder `%%REVISED%%` instead, the committed side has
its rendered stamp replaced by the same placeholder, and the comparison is then about the
page's content and nothing else. The real date is substituted in afterwards.

DETERMINISM, WHICH `site_fresh_check` DEPENDS ON. Same HEAD plus same built bytes gives the
same date on every rebuild, so a rebuild into a temp dir is byte identical to `docs/` and the
freshness gate still means what it says.

    lastmod.py --self-test
"""
from __future__ import annotations

import datetime as _dt
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The token `page()` renders where the date goes. Substituted at the end of the build, once
# the date is known, which cannot happen before the page exists to be compared.
TOKEN = "%%REVISED%%"

# The rendered stamp, as it appears in a committed page. Matched so the committed side can be
# normalised back to the token. Deliberately narrow: it matches the colophon's own format and
# would not match a date written in running prose, which must never be normalised away because
# a change to one is a real change to the page.
STAMP = re.compile(r"Revised [A-Z][a-z]+ \d{1,2}(?:st|nd|rd|th), \d{4}")


def normalise(text: str) -> str:
    """A page with its revision stamp taken back out, so two of them can be compared."""
    return STAMP.sub(TOKEN, text)


def _run(args: list[str]) -> str:
    return subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True,
                          check=False).stdout


def head_pages(prefix: str = "docs/") -> dict[str, str]:
    """Every committed page under `prefix`, keyed by path relative to it.

    TWO PROCESSES, NOT ONE PER FILE. `git show HEAD:docs/<path>` is the obvious way to write
    this and it is 223 subprocesses on a build that already takes forty seconds, twice over
    because the freshness check rebuilds. `ls-tree` names the blobs and `cat-file --batch`
    hands them all over down one pipe.
    """
    tree = _run(["git", "ls-tree", "-r", "-z", "HEAD", prefix])
    if not tree:
        return {}
    shas, paths = [], []
    for row in tree.split("\0"):
        if not row:
            continue
        meta, _, path = row.partition("\t")
        parts = meta.split()
        if len(parts) < 3 or not path.endswith(".html"):
            continue
        shas.append(parts[2])
        paths.append(path[len(prefix):])
    if not shas:
        return {}
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=REPO_ROOT, check=False,
                          input=("\n".join(shas) + "\n").encode(), capture_output=True)
    out, pos, blobs = proc.stdout, 0, {}
    for path in paths:
        nl = out.find(b"\n", pos)
        if nl < 0:
            break
        header = out[pos:nl].split()
        if len(header) < 3:
            break
        size = int(header[2])
        blobs[path] = out[nl + 1:nl + 1 + size].decode("utf-8", "replace")
        pos = nl + 1 + size + 1
    return blobs


def path_commits(prefix: str = "docs/") -> dict[str, list[tuple[str, str]]]:
    """Path relative to `prefix` -> [(commit, ISO date)], newest first."""
    log = _run(["git", "log", "--no-renames", "--format=%x00%H %cs", "--name-only", "--",
                prefix])
    out: dict[str, list[tuple[str, str]]] = {}
    sha = date = ""
    for line in log.splitlines():
        if line.startswith("\0"):
            sha, _, date = line[1:].strip().partition(" ")
        elif line.startswith(prefix) and line.endswith(".html"):
            out.setdefault(line[len(prefix):], []).append((sha, date))
    return out


def _blobs(specs: list[str]) -> dict[str, str]:
    """`<commit>:<path>` -> its text, in one `cat-file` process.

    A missing spec makes git print a "missing" line with no payload, which is why the reply is
    keyed by walking the input rather than by counting bytes blindly.
    """
    if not specs:
        return {}
    proc = subprocess.run(["git", "cat-file", "--batch"], cwd=REPO_ROOT, check=False,
                          input=("\n".join(specs) + "\n").encode(), capture_output=True)
    out, pos, got = proc.stdout, 0, {}
    for spec in specs:
        nl = out.find(b"\n", pos)
        if nl < 0:
            break
        header = out[pos:nl].split()
        if len(header) < 3:               # "<spec> missing"
            pos = nl + 1
            continue
        size = int(header[2])
        got[spec] = out[nl + 1:nl + 1 + size].decode("utf-8", "replace")
        pos = nl + 1 + size + 1
    return got


# How far back to look for the commit that introduced a page's current content. A page that has
# not changed in more than this many commits is dated at the oldest commit examined, which
# understates its age and never overstates it.
DEPTH = 60


def dates_for(built: dict[str, str], today: str) -> dict[str, str]:
    """Every built page's true revision date.

    `built` maps a path relative to `docs/` to the page's text WITH the token still in it.

    THE ANSWER IS WHEN THIS CONTENT FIRST APPEARED, NOT WHEN THE FILE WAS LAST TOUCHED, and
    the difference is the whole correctness of this module.

    The date is rendered INTO the page. So "the date of the last commit that touched this file"
    is a value that changes the file it is computed from: stamp a page with August 18th, commit
    it, and that commit is now the last one touching the file, so tomorrow the same page
    computes August 19th, changes again, and commits again. Every page on the site churns every
    day forever and the sitemap is back to saying everything changed today, which is the exact
    defect this module exists to remove.

    So history is walked backwards with the stamp normalised out at every step, and the answer
    is the OLDEST commit whose content still matches what was just built. That value is stable
    under rewriting, because rewriting only changes the stamp and the stamp is not compared.
    """
    head, hist = head_pages(), path_commits()
    out: dict[str, str] = {}
    live: list[str] = []                      # pages still reaching back through history

    for path, text in built.items():
        was = head.get(path)
        if was is None or normalise(was) != text:
            out[path] = today                 # new, or the content genuinely moved
        else:
            out[path] = today
            live.append(path)

    # FETCHED IN ROUNDS, NOT ALL AT ONCE. Asking for every page's whole history up front is
    # 4,000 blobs today and grows with every commit, and almost all of it is thrown away: most
    # pages stop at the first or second step back. Each round asks only for the next step, and
    # only for the pages that are still matching.
    for step in range(DEPTH):
        specs = {}
        for path in live:
            commits = hist.get(path, [])
            if len(commits) > step:
                specs[f"{commits[step][0]}:docs/{path}"] = path
        if not specs:
            break
        blobs = _blobs(sorted(specs))
        still = []
        for spec, path in specs.items():
            blob = blobs.get(spec)
            if blob is not None and normalise(blob) == built[path]:
                out[path] = hist[path][step][1]     # still matching, so keep reaching back
                still.append(path)
        live = still
    return out


def apply(text: str, iso: str, ordinal) -> str:
    """Put the real date where the token is."""
    d = _dt.date.fromisoformat(iso)
    return text.replace(TOKEN, f"Revised {ordinal(d)}, {iso[:4]}")


def self_test() -> int:
    failures = 0

    def check(label, cond, got=""):
        nonlocal failures
        print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  ({got})"))
        if not cond:
            failures += 1

    print("the stamp is normalised out, and only the stamp")
    page = "<span>Revised August 12th, 2026</span><p>Filed August 11th, 2026.</p>"
    n = normalise(page)
    check("the colophon stamp becomes the token", TOKEN in n, n)
    check("a date in prose is left alone", "Filed August 11th, 2026." in n, n)
    check("two pages differing only by stamp normalise equal",
          normalise("<span>Revised August 12th, 2026</span>x")
          == normalise("<span>Revised August 19th, 2026</span>x"))

    print("\nthe date follows the content, not the build")
    # THE FIXTURE IS THE DEFECT, TWICE OVER. Before this module every date was the build date.
    # Before the rewrite below it, the date was the file's last commit, which is a value that
    # changes the file it is read from, so every page churned daily.
    same = "<span>" + TOKEN + "</span><p>unchanged</p>"
    moved = "<span>" + TOKEN + "</span><p>moved</p>"
    def stamped(body, day):
        return f"<span>Revised August {day}th, 2026</span><p>{body}</p>"
    committed = {"a/index.html": stamped("unchanged", 18),
                 "b/index.html": stamped("was", 12)}
    # `a` was RESTAMPED on the 18th and the 19th without its content moving, which is exactly
    # what a daily rebuild does. Its content first appeared on the 12th and that is its date.
    hist = {"a/index.html": [("s3", "2026-08-18"), ("s2", "2026-08-15"), ("s1", "2026-08-12")],
            "b/index.html": [("s1", "2026-08-12")]}
    blobs = {"s3:docs/a/index.html": stamped("unchanged", 18),
             "s2:docs/a/index.html": stamped("unchanged", 15),
             "s1:docs/a/index.html": stamped("unchanged", 12),
             "s1:docs/b/index.html": stamped("was", 12)}
    real = (head_pages, path_commits, _blobs)
    try:
        globals()["head_pages"] = lambda prefix="docs/": committed
        globals()["path_commits"] = lambda prefix="docs/": hist
        globals()["_blobs"] = lambda specs: {k: v for k, v in blobs.items() if k in specs}
        got = dates_for({"a/index.html": same, "b/index.html": moved,
                         "c/index.html": same}, "2026-08-19")
    finally:
        globals()["head_pages"], globals()["path_commits"], globals()["_blobs"] = real
    check("an unchanged page is dated when its content first appeared",
          got["a/index.html"] == "2026-08-12", got["a/index.html"])
    check("a restamp does not count as a change, which is what made it churn",
          got["a/index.html"] != "2026-08-18", got["a/index.html"])
    check("a page whose content moved is dated today",
          got["b/index.html"] == "2026-08-19", got["b/index.html"])
    check("a page that is not committed yet is dated today",
          got["c/index.html"] == "2026-08-19", got["c/index.html"])
    check("they are not all the same, which is the whole point",
          len(set(got.values())) > 1, str(got))

    print("\nthe token is substituted, and nothing else is")
    def ordinal(d):
        return f"{d.strftime('%B')} {d.day}th"
    out = apply("<span>" + TOKEN + "</span>", "2026-08-12", ordinal)
    check("the real date lands", out == "<span>Revised August 12th, 2026</span>", out)
    check("no token survives a build", TOKEN not in out, out)

    print("\nthe repository answers, which proves the plumbing is connected")
    real = head_pages()
    check("HEAD carries committed pages", len(real) > 50, str(len(real)))
    check("and they parse as pages",
          all(v.lstrip().startswith("<!doctype") for v in list(real.values())[:5]))
    hist = path_commits()
    check("history dates them", len(hist) > 50, str(len(hist)))

    print("\nlastmod self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(self_test() if "--self-test" in sys.argv else
                     (print(__doc__.strip()) or 0))
