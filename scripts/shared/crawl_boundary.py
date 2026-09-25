#!/usr/bin/env python3
"""crawl_boundary.py — ask the registry whether a url is inside the boundary, once, in one place.

WHY THIS EXISTS, 2026-09-19.

`knowledge/shared/SOURCES_REGISTRY.md` states this project's crawl boundary and is `human` owned,
correctly: an unattended run that can edit its own boundary does not have one, because it could
delete a disallow and the next fetch would be compliant with a file it had just rewritten. What
the repo did NOT have was anything that READS that boundary, so every script that fetches carried
its own copy of the rule, and a copy of a rule is a rule that is wrong somewhere.

THE DEFECT. On 2026-09-19 a run's own research helper carried the boundary as a tuple of HOSTS:

    BLOCKED = ("lrl.texas.gov", "data.capitol.texas.gov", "gisweb.tceq.texas.gov")

and fetched one `capitol.texas.gov/TLODOCS/` url. `capitol.texas.gov` is an ALLOWED HOST carrying
a DISALLOWED PATH, and a tuple of hosts cannot express that. Nothing from the fetch reached a
claim and the guard in that script was repaired the same hour. The script is scratch under
`out/`, so the repair died with the container and the next run writes the tuple again from
memory. **A fix that cannot outlive the container is not a fix, it is a run that got lucky.**

WHAT THIS DOES NOT PROMISE, AND THE SENTENCE IS THE WHOLE CONTRACT.

**`forbidden(url)` returning None is NOT permission.** It means no rule this parser could read
matches that url. The registry is prose written for people, its boundary is stated in four
different table shapes and twice in running text, and a parser over prose is complete only until
somebody writes the next row a different way. A checker that answered "allowed" would be making a
promise it cannot keep, and a fetcher that read it as one would be worse off than a fetcher that
read the file.

So it answers in three states and the caller can tell them apart:

    FORBIDDEN   a parsed rule matches. Do not fetch. The reason names the registry's own words.
    NO_RULE     nothing this parser read matches. Go and read the registry.
    UNREADABLE  the registry could not be parsed to a usable boundary at all. HARD FAIL.

THE THIRD STATE IS THE ONE THAT MATTERS AND IT IS WHY THE FLOOR EXISTS. A parse that silently
finds zero entries produces a checker that permits everything and exits 0, which is the exact
shape `noun_trace` shipped for a month and the shape GATE_LESSONS 37 is about: a check that
CANNOT RUN is red, never green. `rules()` raises rather than returning an empty list, and
`--self-test` pins the five host rules and the one path rule the registry states today, measured
2026-09-19, so a reformat that drops one goes red in the suite instead of quietly widening the
boundary.

TWO READINGS THE REGISTRY HAS ALREADY SETTLED AND THIS FILE INHERITS.

  CASE. `Disallow: /TLODOCS/` is upper case and the live urls are lower case. The registry says in
  as many words that taking a case sensitive reading is routing around a disallow on a
  technicality and this project does not do that. Matching here is case folded.

  SUBDOMAINS. A whole host rule covers the names under it, so `www.lrl.texas.gov` is refused by
  the `lrl.texas.gov` rule. That direction over-refuses rather than under-refuses, which is the
  only direction a boundary may be wrong in.

    crawl_boundary.py https://capitol.texas.gov/tlodocs/x.pdf     exit 1, with the reason
    crawl_boundary.py --list                                      the boundary it parsed
    crawl_boundary.py --self-test
"""
from __future__ import annotations

import argparse
import posixpath
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "knowledge" / "shared" / "SOURCES_REGISTRY.md"

# THE WORDS THE REGISTRY ACTUALLY USES TO REFUSE A SOURCE, taken off the file rather than invented
# here. Every one of these was read out of a real row on 2026-09-19, which is GATE_LESSONS 35's
# rule applied to a prose artifact: get the form from the thing, not from your idea of it.
#
#   "OFF LIMITS"            capitol.texas.gov, lrl.texas.gov, data.capitol.texas.gov, TCEQ GIS
#   "Do not fetch"          gisweb.tceq.texas.gov, and the path clause on capitol.texas.gov
#   "Do not collect"        data.capitol.texas.gov
#   "must not be polled"    the TCEQ regulated facilities row in section 3
#   "EXCLUDED ON PURPOSE"   tacc.utexas.edu, whose refusal is stated in a feed table and argued
#                           in running text below it
#   "robots Disallow"       the capitol.texas.gov BillLookup/Search/Reports row in section 4
REFUSAL = re.compile(
    r"off[ -]limits|do not fetch|do not collect|do not poll|must not be polled|"
    r"excluded on purpose|robots disallow", re.I)

# A hostname inside backticks or bold. Two labels minimum and a real TLD, so `Allow: /` and
# `TexasAIDocket/1.0` cannot become hosts.
HOST = re.compile(r"\b([a-z0-9][a-z0-9\-]*(?:\.[a-z0-9][a-z0-9\-]*)+\.[a-z]{2,})\b", re.I)

# A PATH IS ONLY NARROWED WHEN THE REGISTRY PAIRS IT WITH THE REFUSAL. Anything else is read as a
# WHOLE HOST rule, which is the failing-safe direction: over-refusing a permitted path is loud and
# costs a substitute, under-refusing is the thing this file exists to stop. The capitol.texas.gov
# verdict cell names a VERIFIED SUBSTITUTE in the same breath as the refusal
# (`Committees/MeetingsUpcoming.aspx`), so reading every path in the cell would refuse the source
# the registry just told a run to use.
PATH_AFTER = re.compile(r"(?:do not fetch|do not collect|do not poll|disallow[: ]*)\s*`?(/[^`,\s]+)",
                        re.I)
PATH_QUOTED = re.compile(r"`(/[^`]+)`")

# A verdict that says the whole site is refused overrides any path reading in the same cell.
WHOLE_HOST = re.compile(r"whole host|domain[- ]wide|for all agents|do not collect", re.I)

# THE FLOOR. Measured 2026-09-19: the registry states six rules over five hosts. A parse that
# comes back under this is a parse that has lost its grip on the file, and it is refused rather
# than returned, because an empty boundary is a boundary that permits everything.
MIN_RULES = 5


class BoundaryUnreadable(RuntimeError):
    """The registry could not be parsed to a usable boundary. Never an empty allow list."""


def _cells(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _hosts(text: str) -> list[str]:
    out = []
    for h in HOST.findall(text or ""):
        h = h.lower().lstrip("~*")
        if h.startswith("www."):
            h = h[4:]
        # A version string and a file name are not hosts. `TexasAIDocket/1.0` is stripped by the
        # slash; `robots.txt` and `fuel-mix.json` are caught here.
        if h.rsplit(".", 1)[-1] in ("txt", "json", "csv", "pdf", "xml", "aspx", "html"):
            continue
        if h not in out:
            out.append(h)
    return out


def rules(text: str | None = None) -> list[dict]:
    """The boundary the registry states, as `{host, paths, why, source}` rows.

    Raises `BoundaryUnreadable` rather than returning a short list, because a caller that gets an
    empty boundary back and exits 0 has built a checker that permits everything. That is the
    failure this module's whole design is arranged around.
    """
    if text is None:
        try:
            text = REGISTRY.read_text(encoding="utf-8")
        except OSError as exc:
            raise BoundaryUnreadable(f"{REGISTRY} could not be read: {exc}") from exc
    found: dict[str, dict] = {}
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = _cells(line)
        if len(cells) < 2:
            continue
        marked = [c for c in cells if REFUSAL.search(c)]
        if not marked:
            continue
        verdict = marked[-1]
        # The subject columns name the host. The verdict cell is read for a host ONLY when the
        # subject columns give none, because a verdict cell legitimately names a substitute host
        # the registry is sending a run TO.
        hosts = _hosts(" ".join(cells[:2])) or _hosts(verdict)
        if not hosts:
            continue
        paths = [] if WHOLE_HOST.search(verdict) else PATH_AFTER.findall(verdict)
        if not paths and not WHOLE_HOST.search(verdict) and REFUSAL.search(cells[-1] or ""):
            # A "robots Disallow" row states its paths beside the host in the subject cell, and
            # it writes the FIRST of them glued to the host:
            #     `capitol.texas.gov/BillLookup/`, `/Search/`, `/Reports/` | robots Disallow
            # Reading only the bare ones takes two of the three and leaves `/BillLookup/`
            # permitted, which is the partial parse this file's whole contract is about. The
            # host is stripped off wherever a backticked token carries one.
            for tok in PATH_QUOTED.findall(cells[0]) + re.findall(r"`([^`]+)`", cells[0]):
                if tok.startswith("/"):
                    paths.append(tok)
                elif "/" in tok and tok.lower().startswith(host_prefix := hosts[0]):
                    paths.append(tok[len(host_prefix):])
        host = hosts[0]
        row = found.setdefault(host, {"host": host, "paths": [], "why": [], "whole": False})
        if paths:
            for p in paths:
                p = p.rstrip(".").lower()
                if p not in row["paths"]:
                    row["paths"].append(p)
        else:
            row["whole"] = True
        clean = re.sub(r"\*\*|`|~~", "", verdict).strip()
        row["why"].append(clean[:160])
    # THE PROSE HALF. `tacc.utexas.edu` is refused in a feed table that says only "EXCLUDED ON
    # PURPOSE. See below", and the argument is in the paragraph under it. The table row carries
    # the marker so it is already read; this assertion is here to say that the prose was checked
    # and is not a second parser.
    out = []
    for row in found.values():
        out.append({"host": row["host"],
                    "paths": [] if row["whole"] else row["paths"],
                    "why": " / ".join(dict.fromkeys(row["why"]))})
    out.sort(key=lambda r: r["host"])
    if len(out) < MIN_RULES:
        raise BoundaryUnreadable(
            f"{REGISTRY.name} parsed to {len(out)} boundary rule(s), under the floor of "
            f"{MIN_RULES} measured on 2026-09-19. The registry has been reformatted or this "
            f"parser has lost its grip on it. An empty boundary permits everything, so this is a "
            f"hard failure and never an empty allow list")
    return out


def _host_of(url: str) -> str:
    parts = urlsplit(url if "//" in url else "//" + url)
    # A TRAILING DOT IS THE SAME HOST. `capitol.texas.gov.` is the fully qualified spelling of
    # `capitol.texas.gov` and DNS answers both with the same server, so a rule matched against
    # the raw spelling was walked around by one character. Codex found it on PR 361.
    host = (parts.hostname or "").lower().rstrip(".")
    return host[4:] if host.startswith("www.") else host


def _path_of(url: str) -> str:
    """The path a server would serve, which is the only spelling a path rule may be judged on.

    A rule compared against the raw spelling can be walked around by spelling the same path
    another way, and every one of these reached `/tlodocs/` on 2026-09-25 while the checker said
    no rule matched: `/%74lodocs/`, `/Committees/../tlodocs/`, `//tlodocs/`. So the path is
    percent-decoded until it stops changing, backslashes become slashes (an IIS host treats them
    as one), repeated slashes fold, dot segments resolve, and case folds. Each of those can only
    make the checker refuse MORE, which is the one direction a boundary may err in.
    """
    raw = urlsplit(url if "//" in url else "//" + url).path or "/"
    p = raw
    for _ in range(3):
        nxt = unquote(p)
        if nxt == p:
            break
        p = nxt
    p = re.sub(r"/+", "/", p.replace("\\", "/"))
    trailing = p.endswith("/")
    p = posixpath.normpath("/" + p.lstrip("/"))
    if trailing and not p.endswith("/"):
        p += "/"
    return p.lower()


def forbidden(url: str, boundary: list[dict] | None = None) -> str | None:
    """The registry's reason for refusing this url, or None if NO RULE READ HERE MATCHES.

    None IS NOT PERMISSION. See the module docstring. The caller that wants permission has to go
    and read `SOURCES_REGISTRY.md`, which is the only thing that carries it.
    """
    b = rules() if boundary is None else boundary
    host = _host_of(url)
    if not host:
        return None
    path = _path_of(url)
    for row in b:
        r = row["host"]
        if host != r and not host.endswith("." + r):
            continue
        if not row["paths"]:
            return (f"{r} is off limits to this project, whole host. "
                    f"SOURCES_REGISTRY.md: {row['why']}")
        for p in row["paths"]:
            if path.startswith(p):
                return (f"{r}{p} is a disallowed path on an allowed host. "
                        f"SOURCES_REGISTRY.md: {row['why']}")
    return None


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    b = rules()
    by_host = {r["host"]: r for r in b}

    # THE DEFECT, REPLAYED. A disallowed PATH on an ALLOWED host, in both the case the registry
    # writes it and the case the live urls use. The 2026-09-19 helper's boundary was a tuple of
    # hosts and could not express this, so both of these came back permitted.
    ok("the 2026-09-19 fetch is refused, in the case the live urls use",
       bool(forbidden("https://capitol.texas.gov/tlodocs/BillAnalysis.pdf", b)))
    ok("...and in the upper case the registry writes it in",
       bool(forbidden("https://capitol.texas.gov/TLODOCS/BillAnalysis.pdf", b)))
    # THE SAME PATH SPELLED ANOTHER WAY, and every one of these came back permitted on
    # 2026-09-25 until the host and the path were normalised the way a server reads them.
    for u in ("http://capitol.texas.gov./TLODOCS/x", "https://capitol.texas.gov/%74lodocs/x.pdf",
              "https://capitol.texas.gov/%2574lodocs/x.pdf",
              "https://capitol.texas.gov/Committees/../tlodocs/x.pdf",
              "https://capitol.texas.gov//tlodocs/x.pdf", "https://capitol.texas.gov/\\tlodocs/x.pdf",
              "https://capitol.texas.gov/./tlodocs/x.pdf", "http://lrl.texas.gov./x"):
        ok(f"...and spelled {u} it is still refused", bool(forbidden(u, b)))
    ok("...while a path that merely passes through `..` to an allowed page stays allowed",
       forbidden("https://capitol.texas.gov/Committees/x/../MeetingsUpcoming.aspx", b) is None)
    ok("...and the reason names the registry rather than this file",
       "SOURCES_REGISTRY" in (forbidden("https://capitol.texas.gov/TLODOCS/x", b) or ""))
    # AND THE SUBSTITUTE THE REGISTRY VERIFIED IS NOT REFUSED. A boundary checker that refuses
    # the source the registry just told a run to use costs the run the story, which is the
    # over-refusal this file's path rule is arranged to avoid.
    ok("...while the verified substitute on the same host is not refused by the path rule",
       forbidden("https://capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S", b)
       is None, str(forbidden("https://capitol.texas.gov/Committees/"
                              "MeetingsUpcoming.aspx?Chamber=S", b)))

    # THE SECOND CAPITOL ROW, in section 4, whose three paths are `robots Disallow` and whose
    # first path is written glued to the host. A parser reading only the bare ones takes
    # `/Search/` and `/Reports/` and leaves `/BillLookup/` permitted, which is the partial parse
    # this module's contract is about: a boundary checker that is wrong about ONE path is more
    # dangerous than no boundary checker, because the next fetcher trusts it.
    for p in ("/billlookup/", "/search/", "/reports/"):
        ok(f"capitol.texas.gov{p} is refused too, from the section 4 robots row",
           bool(forbidden(f"https://capitol.texas.gov{p}x", b)),
           str(by_host.get("capitol.texas.gov", {}).get("paths")))

    # THE WHOLE HOST RULES, each named, so a reformat that drops one goes red here rather than
    # silently widening the boundary. Measured 2026-09-19 against the shipped registry.
    for host in ("lrl.texas.gov", "data.capitol.texas.gov", "gisweb.tceq.texas.gov",
                 "tacc.utexas.edu"):
        ok(f"{host} is still read as off limits",
           bool(forbidden(f"https://{host}/anything", b)), str(sorted(by_host)))
    ok("...and a whole host rule reaches a subdomain, which is the direction a boundary may err",
       bool(forbidden("https://www.lrl.texas.gov/x", b)))

    # A HOST THE REGISTRY PERMITS IS NOT REFUSED, because a checker that refuses everything is as
    # useless as one that permits everything and is easier to notice only after it costs a run.
    ok("a host the registry lists as usable comes back with no rule",
       forbidden("https://www.ercot.com/api/x.json", b) is None,
       str(forbidden("https://www.ercot.com/api/x.json", b)))
    ok("...and so does a host the registry never mentions",
       forbidden("https://example.org/x", b) is None)

    # THE FLOOR, AND IT IS THE POINT OF THE WHOLE FILE. A registry that parses to nothing is a
    # hard failure, never an empty allow list that permits everything at exit 0.
    try:
        rules("# a registry with no boundary in it at all\n\nnothing here.\n")
        ok("a registry that parses to no boundary is a HARD FAIL", False,
           "it returned a list instead of raising")
    except BoundaryUnreadable:
        ok("a registry that parses to no boundary is a HARD FAIL", True)
    try:
        rules("| `lrl.texas.gov` | x | **OFF LIMITS, WHOLE HOST** |\n")
        ok("...and so is a parse that finds fewer rules than the registry states", False,
           "one rule was accepted as a boundary")
    except BoundaryUnreadable:
        ok("...and so is a parse that finds fewer rules than the registry states", True)

    ok(f"the shipped registry parses to at least the {MIN_RULES} rules measured on 2026-09-19",
       len(b) >= MIN_RULES, f"{len(b)}: {sorted(by_host)}")
    print(f"\ncrawl_boundary self-test: {'all passed' if not fails else str(fails) + ' FAILED'}")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0], allow_abbrev=False)
    ap.add_argument("url", nargs="?", help="the url to ask about")
    ap.add_argument("--list", action="store_true", help="print the boundary this parser read")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    try:
        b = rules()
    except BoundaryUnreadable as exc:
        print(f"crawl_boundary: {exc}", file=sys.stderr)
        return 2
    if args.list:
        for r in b:
            scope = "WHOLE HOST" if not r["paths"] else " ".join(r["paths"])
            print(f"  {r['host']:<28} {scope}\n      {r['why'][:150]}")
        print(f"\n{len(b)} rule(s) read from {REGISTRY.name}. A url with NO rule here is a url "
              f"this parser found nothing about, which is not the same as a permitted one.")
        return 0
    if not args.url:
        ap.error("give a url, or --list, or --self-test")
    why = forbidden(args.url, b)
    if why:
        print(f"crawl_boundary: DO NOT FETCH. {why}", file=sys.stderr)
        return 1
    print(f"crawl_boundary: no rule in {REGISTRY.name} that this parser reads matches "
          f"{args.url}. THAT IS NOT PERMISSION. Read the registry before fetching.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
