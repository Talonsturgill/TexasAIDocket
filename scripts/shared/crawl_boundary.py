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
import unicodedata
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


def _browser_form(url: str) -> str:
    """The url as a browser-style client parses it, when that differs from `urlsplit`.

    For http and https a browser drops tabs and newlines, reads every backslash before the query as
    a slash, and accepts any number of slashes after the scheme, so `https:capitol.texas.gov/x` and
    `https://capitol.texas.gov\\tlodocs\\x.pdf` both reach capitol.texas.gov and its `/tlodocs/`.
    `urlsplit` reads a different host out of both. A tool that fetches the way a browser does,
    WebFetch among them, would therefore reach a forbidden path this checker had waved through,
    and `shipped_check` judges claims that tool fetched. Found by review on PR 361.

    A url with no scheme at all is read the way an address bar reads it, as https.
    """
    u = re.sub(r"[\t\n\r]", "", url).strip("".join(map(chr, range(0x21))))
    m = re.match(r"(?i)(https?|wss?|ftp):", u)
    scheme, rest = (m.group(1).lower(), u[m.end():]) if m else ("https", u)
    cut = min([i for i in (rest.find("?"), rest.find("#")) if i >= 0] or [len(rest)])
    head = rest[:cut].replace("\\", "/").lstrip("/")
    return f"{scheme}://{head}{rest[cut:]}"


def _hosts_of(url: str) -> set[str]:
    """Every host a client might connect to for this url, in the form a rule names."""
    name = urlsplit(url if "//" in url else "//" + url).hostname or ""
    out = set()
    # A CLIENT UNQUOTES THE HOST BEFORE IT CONNECTS. urllib does it in `Request` and a browser
    # does it in its host parser, so `%6crl.texas.gov` reaches lrl.texas.gov and
    # `capitol.texas.gov%3a443` reaches capitol.texas.gov on port 443, and neither matched a rule
    # while only the escaped spelling was judged. The decoded name is split again so a port the
    # decode exposed is dropped. Found in this PR's own review, 2026-09-25.
    for host in dict.fromkeys((name, urlsplit("//" + unquote(name)).hostname or "")):
        # A TRAILING DOT IS THE SAME HOST. `capitol.texas.gov.` is the fully qualified spelling
        # of `capitol.texas.gov` and DNS answers both with the same server, so a rule matched
        # against the raw spelling was walked around by one character. Codex found it on PR 361.
        host = host.lower().rstrip(".")
        # AND A UNICODE SPELLING IS THE SAME HOST. `capitol\u3002texas.gov`, with an ideographic
        # full stop, reaches the real server because urllib IDNA-encodes the name before it
        # connects, and the encoding turns U+3002, U+FF0E and U+FF61 into dots and folds full
        # width letters. So the rule is judged on the encoded name too. Found by review on PR 361.
        try:
            host = host.encode("idna").decode("ascii").lower().rstrip(".")
        except UnicodeError:
            pass  # a name IDNA can't encode is a name urllib can't connect to either
        if host:
            out.add(host[4:] if host.startswith("www.") else host)
    return out


def _trim(path: str) -> str:
    """WINDOWS DROPS A TRAILING DOT OR SPACE FROM EVERY PATH SEGMENT, so an IIS host serves
    `/tlodocs./`, `/tlodocs%20/` and `/tlodocs%2e/` from `/tlodocs/`. `.` and `..` are left for
    the resolve. Found by review on PR 361."""
    return "/".join(g if g in (".", "..") else g.rstrip(". ") for g in path.split("/"))


def _paths_of(url: str) -> set[str]:
    """Every path a server might serve for this url. A rule refuses the url if ANY of them is
    under it.

    One normalised reading was the first fix and it was wrong both ways. Compared raw, the
    boundary was walked around by `/%74lodocs/`, `/Committees/../tlodocs/` and `//tlodocs/`.
    Decoded three times and then resolved, it was walked around the other way by
    `/tlodocs/%252e%252e/../x`, which a server decodes ONCE, keeping `%2e%2e` as a directory
    name that the `..` then removes, so it serves `/tlodocs/x`, while three decodes turned it into
    `/x`. And `/tlodocs/.` resolved to `/tlodocs`, which no longer started with `/tlodocs/`.

    A checker cannot know which reading a given server takes, so it takes all of them: the raw
    path, and the path decoded zero to three times, each with backslashes and repeated slashes
    folded and dot segments resolved, with and without the Windows trim, with and without path
    parameters, as written and case folded. Refusing when any one matches can only refuse MORE
    than any single reading, which is the one direction a boundary may err in.
    """
    raw = (urlsplit(url if "//" in url else "//" + url).path or "/").lower()
    out = {raw}
    p = raw
    for _ in range(4):
        # A SERVER THAT COMPARES UNICODE FOLDS IT FIRST. NFKC turns a full width `ｔ` into `t`, and
        # a Windows volume compares in upper case, where the dotless `ı` is `I`.
        for f in dict.fromkeys((p, unicodedata.normalize("NFKC", p).upper().lower())):
            q = re.sub(r"/+", "/", f.replace("\\", "/"))
            # A JAVA SERVER DROPS A `;parameter` FROM EVERY SEGMENT, so `/tlodocs;a=b/` is
            # `/tlodocs/` to it and `/x/..;/tlodocs/` climbs out of `/x/`.
            s = re.sub(r";[^/]*", "", q)
            for form in dict.fromkeys((q, _trim(q), s, _trim(s))):
                resolved = posixpath.normpath("/" + form.lstrip("/"))
                out.add(form)
                out.add(resolved)
                out.add(resolved + "/")  # `/tlodocs/.` and `/tlodocs` both name the directory
        # IIS ALSO DECODES ITS OWN `%uXXXX` ESCAPE, so `%u0074lodocs` is `tlodocs` to it. AND A
        # DECODE CAN SURFACE A CAPITAL, `%54` being `T`, so each decoded reading is folded again.
        # `/%54LODOCS/` was permitted until this PR's own review, 2026-09-25.
        nxt = unquote(re.sub(r"%u([0-9a-f]{4})", lambda m: chr(int(m.group(1), 16)), p)).lower()
        if nxt == p:
            break
        p = nxt
    return out


_SHORT = re.compile(r"([a-z0-9_$-]{1,6})~\d{1,6}")


def _under(candidate: str, rule: str) -> bool:
    """True when one reading of a path falls under a rule's path.

    A WINDOWS SHORT NAME IS THE SAME FOLDER. Where a volume keeps 8.3 names, `/BILLLO~1/` serves
    `/BillLookup/`. The alias a volume gives a folder can't be predicted from outside (a collision
    swaps the tail for a hash), so a `~<digits>` segment is taken as the folder whenever its first
    two letters agree. That refuses a little more than it must, which is the only direction this
    checker may be wrong in. Found by review on PR 361.
    """
    if candidate.startswith(rule):
        return True
    rs = [g for g in rule.split("/") if g]
    cs = [g for g in candidate.split("/") if g]
    if not rs or len(cs) < len(rs):
        return False
    for r_seg, c_seg in zip(rs, cs):
        if c_seg == r_seg:
            continue
        m = _SHORT.fullmatch(c_seg)
        if not (m and r_seg.startswith(m.group(1)[:2])):
            return False
    return True


def forbidden(url: str, boundary: list[dict] | None = None) -> str | None:
    """The registry's reason for refusing this url, or None if NO RULE READ HERE MATCHES.

    None IS NOT PERMISSION. See the module docstring. The caller that wants permission has to go
    and read `SOURCES_REGISTRY.md`, which is the only thing that carries it.
    """
    b = rules() if boundary is None else boundary
    try:
        for reading in dict.fromkeys((url, _browser_form(url))):
            hosts = _hosts_of(reading)
            paths = None
            for row in b:
                r = row["host"]
                if not any(h == r or h.endswith("." + r) for h in hosts):
                    continue
                if not row["paths"]:
                    return (f"{r} is off limits to this project, whole host. "
                            f"SOURCES_REGISTRY.md: {row['why']}")
                paths = _paths_of(reading) if paths is None else paths
                for p in row["paths"]:
                    if any(_under(c, p) for c in paths):
                        return (f"{r}{p} is a disallowed path on an allowed host. "
                                f"SOURCES_REGISTRY.md: {row['why']}")
    except ValueError as exc:
        # A URL THE PARSER CAN'T READ IS REFUSED, never waved through. `urlsplit` raises on a
        # host that NFKC turns into a separator and on a broken IPv6 bracket, and a checker that
        # crashed there left its caller to guess. A url that can't be judged is not fetched.
        return (f"{url[:120]!r} can't be parsed ({exc}), so no rule in SOURCES_REGISTRY.md can be "
                f"judged against it, and a url that can't be judged is not fetched")
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
              "https://capitol.texas.gov/./tlodocs/x.pdf", "http://lrl.texas.gov./x",
              # and the three a review found in the first normalisation, 2026-09-25
              "https://capitol.texas.gov/tlodocs/%252e%252e/../89R/x.pdf",
              "https://capitol.texas.gov/tlodocs/.", "https://capitol.texas.gov/TLODOCS",
              "https://capitol\u3002texas.gov/tlodocs/x.pdf", "https://lrl\uff0etexas.gov/x",
              "https://\uff43apitol.texas.gov/tlodocs/x.pdf",
              # and the IIS and browser spellings a second review found, 2026-09-25
              "https://capitol.texas.gov/tlodocs./x.pdf", "https://capitol.texas.gov/tlodocs%20/x.pdf",
              "https://capitol.texas.gov/tlodocs.%20/x.pdf", "https://capitol.texas.gov/tlodocs%2e/x.pdf",
              "https://capitol.texas.gov/%u0074lodocs/x.pdf", "https://capitol.texas.gov/TLODOC~1/x.pdf",
              "https://capitol.texas.gov/BILLLO~1/x", "https://capitol.texas.gov\\tlodocs\\x.pdf",
              "https:capitol.texas.gov/tlodocs/x", "https:\\\\lrl.texas.gov\\x",
              "https://capitol.texas.gov/tl\todocs/x.pdf",
              # and the ones this PR's own review found after that, 2026-09-25
              "https://capitol.texas.gov/%54LODOCS/x.pdf", "https://%6crl.texas.gov/x",
              "https://capitol.texas.gov%3a443/tlodocs/x", "https://capitol.texas.gov/ｔlodocs/x",
              "https://capitol.texas.gov/bılllookup/x", "capitol.texas.gov\\tlodocs\\x.pdf",
              "https://capitol.texas.gov/tlodocs;a=b/x.pdf",
              "https://capitol.texas.gov/committees/..;/tlodocs/x.pdf"):
        ok(f"...and spelled {u!r} it is still refused", bool(forbidden(u, b)))
    for u in ("https://capitol.texas.gov／tlodocs/x", "https://[::1/x"):
        try:
            why = forbidden(u, b)
            ok(f"a url the parser can't read, {u!r}, is refused rather than waved through",
               bool(why) and "can't be parsed" in why, str(why))
        except Exception as exc:  # noqa: BLE001  a crash is the defect this replays
            ok(f"a url the parser can't read, {u!r}, is refused rather than raising", False,
               f"{type(exc).__name__}: {exc}")
    ok("...while a path that merely passes through `..` to an allowed page stays allowed",
       forbidden("https://capitol.texas.gov/Committees/x/../MeetingsUpcoming.aspx", b) is None)
    ok("...and a path that only shares the rule's first letters is not refused",
       forbidden("https://capitol.texas.gov/tlodocsarchive/x", b) is None)
    for u in ("https://capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S&q=%2Ftlodocs%2F",
              "https://capitol.texas.gov/Committees/x.%20/MeetingsUpcoming.aspx",
              "https://www.ercot.com/content/wcm/lists/x.pdf"):
        ok(f"...while {u} stays allowed", forbidden(u, b) is None, str(forbidden(u, b)))
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
