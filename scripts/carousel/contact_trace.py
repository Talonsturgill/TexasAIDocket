#!/usr/bin/env python3
"""contact_trace.py — an address a reader could write to, that no source in the run carries.

THE DEFECT THIS EXISTS FOR (2026-09-14, carousel no. 24, frame 2)

The frame's whole argument is what a public notice does and does not say. It is a drawn
facsimile of a real ERCOT market notice, and its first cut set two lines inside that facsimile,
in the same serif as two verbatim quotations from the notice itself:

    Questions to BatchZero@ercot.com
    Attachment, the dispute form the notice names

**No claim in that run carries an email address, and no claim mentions an attachment.** The
address was invented, on a real organisation's domain, on a frame dressed as that
organisation's own document, and the deck was one pixel critic away from publishing it.

It was found by a human reading the render. Every gate was green and each was right on its own
terms. `claims_check` asks whether claims were fetched and quoted. `noun_trace` warns on named
THINGS and an address is not a name. `numeral_trace` reads digits. `verbatim_check` holds
DECLARED fragments to their claims and nothing declared this one. `aggregate_check` reads
numeric phrases. There was no gate whose subject was this.

WHY THIS ONE FAILS RATHER THAN WARNS, WHICH IS THE WHOLE ARGUMENT

The proper-noun half of `noun_trace` warns, and correctly: a machine cannot tell a fabricated
body from a legitimate label, and `UPGRADE_BACKLOG.md` records a first pass raising 33, 10 and 8
candidates per deck. **A contact token is not that kind of string.** An email address, a
telephone number or a host is unambiguous to a regular expression, it is the one class of thing
on a slide a reader can ACT on, and acting on a fabricated one means writing to a real
organisation about a mailbox that does not exist.

And it is quiet. Measured 2026-09-14 across all 23 shipped decks that carry a claims file, a
copy file and a render report: **the only contact tokens anywhere on any published surface are
this site's own host and its own item pages.** Zero emails, zero telephone numbers, zero
third-party hosts, over the whole corpus. So the exemption is one host read from
`config/brand.yaml`, and a gate that has fired zero times on correct work is a gate that can be
believed when it fires.

WHAT IT READS AND WHAT IT CANNOT SEE

It reads the rendered text nodes, `copy.json`, the caption and the first comment, and it holds
each token to the run's own claims: any claim's text, quote, evidence, publisher, title or url.
It cannot see a contact token drawn as ART rather than set as type, because a drawn address is
pixels and this reads the render report. It cannot see a fabricated attachment, a fabricated
docket number or a fabricated room number, which are the same family and are not mechanically
separable from legitimate design furniture. Frame 2's second fabricated line is in that half and
this gate would not have caught it.

    contact_trace.py --date 2026-09-14        the run in out/
    contact_trace.py --run 2026-09-14         a shipped run under runs/carousel/
    contact_trace.py --all                    every shipped run
    contact_trace.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"
OUT = REPO_ROOT / "out"

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
# A host, with or without a scheme and a path. The suffix list is the set this corpus and its
# sources actually use, kept explicit so a word like "etc.us" in prose cannot become a finding.
HOST = re.compile(r"\b(?:https?://)?(?:[A-Za-z0-9-]+\.)+"
                  r"(?:com|org|gov|net|edu|io|us|coop|info|mil)\b(?:/[^\s\"'<>]*)?")
PHONE = re.compile(r"\(?\b\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b")
KINDS = (("email address", EMAIL), ("host", HOST), ("telephone number", PHONE))


def brand_host() -> str | None:
    """The site's own host, read from `config/brand.yaml` through the gate that already reads it.

    NOT A CONSTANT IN THIS FILE, and `CLAUDE.md` carries the whole account of why: the public URL
    is stated in config and every surface that kept its own copy of it printed the wrong one.
    `coherence_check.brand_site()` is the one reader and this calls it.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        from coherence_check import brand_site  # noqa: PLC0415
        v = brand_site()
    except Exception:
        return None
    if not v:
        return None
    return re.sub(r"^https?://", "", v.strip()).rstrip("/").lower()


def strings(o) -> list[str]:
    if isinstance(o, str):
        return [o]
    if isinstance(o, dict):
        return [s for v in o.values() for s in strings(v)]
    if isinstance(o, list):
        return [s for v in o for s in strings(v)]
    return []


def tokens(text: str) -> list[tuple[str, str]]:
    """Every contact token in one string, email first so a host inside one is not double-read."""
    found = []
    rest = text
    for m in EMAIL.finditer(text):
        found.append(("email address", m.group(0)))
        rest = rest.replace(m.group(0), " " * len(m.group(0)))
    for kind, rx in (("host", HOST), ("telephone number", PHONE)):
        for m in rx.finditer(rest):
            found.append((kind, m.group(0)))
    return found


def surfaces(run_dir: Path) -> list[tuple[str, str]]:
    """Everything this deck PUBLISHES, as (where, text). The render is read first and last."""
    out: list[tuple[str, str]] = []
    rr = run_dir / "render_report.json"
    if not rr.exists():
        rr = run_dir / "render" / "render_report.json"
    if rr.exists():
        try:
            rep = json.loads(rr.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rep = {}
        for s in rep.get("slides", []):
            for t in s.get("text_nodes", []):
                out.append((f"{s.get('file', 'a slide')} (rendered)", t.get("text", "")))
    cp = run_dir / "copy.json"
    if cp.exists():
        try:
            out += [("copy.json", s) for s in strings(json.loads(cp.read_text(encoding="utf-8")))]
        except json.JSONDecodeError:
            pass
    for name in ("caption.txt", "first_comment.txt"):
        f = run_dir / name
        if f.exists():
            out.append((name, f.read_text(encoding="utf-8")))
    return out


def haystack(run_dir: Path) -> str | None:
    cj = run_dir / "claims.json"
    if not cj.exists():
        return None
    try:
        return " \n ".join(strings(json.loads(cj.read_text(encoding="utf-8")))).lower()
    except json.JSONDecodeError:
        return None


def check(run_dir: Path) -> list[str] | None:
    """Findings, or None when the run does not carry what this gate reads."""
    hay = haystack(run_dir)
    surf = surfaces(run_dir)
    if hay is None or not surf:
        return None
    site = brand_host()
    seen, fails = set(), []
    for where, text in surf:
        for kind, tok in tokens(text):
            low = tok.lower()
            if low in hay:
                continue
            if site and (low == site or low.startswith(site + "/")
                         or low.startswith("https://" + site) or low.startswith("http://" + site)):
                continue
            if (kind, low) in seen:
                continue
            seen.add((kind, low))
            fails.append(
                f"{where}: the {kind} \"{tok}\" is published and appears in no claim this run "
                f"verified. A reader can act on an address. This deck's claims carry none like "
                f"it, and the site's own host is the only one exempt")
    return fails


def problems(run_dir: Path):
    """The adapter shipped_check calls."""
    return check(run_dir)


def run(run_dir: Path, label: str) -> int:
    if not run_dir.is_dir():
        print(f"contact_trace: ABSENT. {run_dir} is not a directory, so nothing was read and "
              f"nothing is certified", file=sys.stderr)
        return 2
    fails = check(run_dir)
    if fails is None:
        print(f"contact_trace: ABSENT. {label} carries no claims.json or publishes no readable "
              f"surface, so no token could be held to anything", file=sys.stderr)
        return 2
    n_surf = len(surfaces(run_dir))
    n_tok = sum(len(tokens(t)) for _w, t in surfaces(run_dir))
    if fails:
        print(f"\ncontact_trace: {len(fails)} published contact token(s) in {label} that no "
              f"claim carries\n", file=sys.stderr)
        for f in fails:
            print(f"  - {f}", file=sys.stderr)
        return 1
    print(f"contact_trace: {label}, {n_surf} published surface(s) read, {n_tok} contact "
          f"token(s) found and every one of them traced to a claim or to this site's own host")
    return 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    import tempfile

    claims = {"claims": [
        {"id": "c25", "text": "ERCOT Market Notice M-A080326-04 states the conditions",
         "quote": "conditionally classified", "url": "https://www.ercot.com/services/comm/mkt_notices",
         "publisher": "ERCOT"},
        {"id": "c23", "text": "The notice names no load and no total", "quote": "",
         "url": "https://www.ercot.com/mktrules", "publisher": "ERCOT"}]}

    def deck(td: Path, frame_text: list[str]) -> Path:
        d = td / "2026-09-14"
        d.mkdir(parents=True, exist_ok=True)
        (d / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
        (d / "render_report.json").write_text(json.dumps(
            {"slides": [{"file": "slide-02.html",
                         "text_nodes": [{"text": t} for t in frame_text]}]}), encoding="utf-8")
        (d / "copy.json").write_text(json.dumps({"slides": []}), encoding="utf-8")
        return d

    # ---------------------------------------------------------------- THE DEFECT, REPLAYED
    with tempfile.TemporaryDirectory() as t:
        d = deck(Path(t), ["Questions to BatchZero@ercot.com", "texasaidocket.com"])
        f = check(d)
        ok("frame 2's fabricated address is CAUGHT", len(f) == 1, str(f))
        ok("...and the finding names it as an email address",
           bool(f) and "email address" in f[0] and "BatchZero@ercot.com" in f[0], str(f))
        ok("...and the site's own footer host is NOT a finding",
           not any("texasaidocket" in x for x in f), str(f))

    # The repair: the line came off, and the frame still prints the host the notice is on.
    with tempfile.TemporaryDirectory() as t:
        d = deck(Path(t), ["www.ercot.com/services/comm/mkt_notices", "texasaidocket.com"])
        ok("a host that a cited claim's own url carries is CLEAN", check(d) == [], str(check(d)))

    # ---------------------------------------------------------------- THE OTHER TWO KINDS
    with tempfile.TemporaryDirectory() as t:
        d = deck(Path(t), ["Call (512) 555-0134", "texasaidocket.com"])
        ok("an invented telephone number is CAUGHT",
           any("telephone" in x for x in check(d)), str(check(d)))
        d = deck(Path(t) / "b", ["See datacentercoalition.org", "texasaidocket.com"])
        ok("a third party host no claim carries is CAUGHT",
           any("host" in x for x in check(d)), str(check(d)))

    # ---------------------------------------------------------------- THE EMPTY CASES
    # GATE_LESSONS 51. A checker handed nothing must not print the line it prints when clean.
    with tempfile.TemporaryDirectory() as t:
        ok("a directory that does not exist is ABSENT and not clean",
           run(Path(t) / "nope", "fixture") == 2)
        bare = Path(t) / "bare"
        bare.mkdir()
        ok("a run with no claims.json is ABSENT and not clean", check(bare) is None)
        (bare / "claims.json").write_text(json.dumps(claims), encoding="utf-8")
        ok("...and a run with claims but nothing published is ABSENT too", check(bare) is None)

    ok("the exempt host is read from config/brand.yaml rather than typed here",
       brand_host() == "texasaidocket.com",
       f"got {brand_host()}, so the exemption is not coming from the brand config")

    # ---------------------------------------------------------------- THE REAL CORPUS
    # A fixture written beside a detector agrees with it, GATE_LESSONS 16, so the number that
    # decides whether this gate may FAIL rather than warn is taken from published work.
    decks = [p for p in sorted(RUNS.glob("2*")) if (p / "claims.json").exists()]
    ok("there are shipped decks to measure", len(decks) >= 20, f"{len(decks)} found")
    fired = {p.name: check(p) for p in decks}
    noisy = {k: v for k, v in fired.items() if v}
    ok("no shipped deck publishes a contact token that no claim carries", not noisy, str(noisy))
    read = sum(1 for p in decks if fired[p.name] is not None)
    ok("...and the sweep actually READ them, rather than finding none by reading none",
       read >= 20, f"{read} of {len(decks)} decks had both a claims file and a published surface")
    total = sum(len(tokens(t)) for p in decks for _w, t in surfaces(p))
    ok("...over a corpus that does carry contact tokens for it to judge", total >= 20,
       f"{total} tokens across {len(decks)} decks")

    print("\ncontact_trace self-test:", "clean" if not bad else f"{bad} FAILURE(S)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], allow_abbrev=False)
    ap.add_argument("--date", help="a run in out/<date>/")
    ap.add_argument("--run", help="a shipped run under runs/carousel/<date>/")
    ap.add_argument("--all", action="store_true", help="every shipped run")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()
    if a.all:
        # A SWEEP OVER HISTORY DOES NOT FAIL ON A DECK THAT ARCHIVED NOTHING. Three shipped runs
        # kept no render report and no copy.json, so there is no published surface to read and
        # no finding to make. Counting that as red would make this row permanently red, and
        # GATE_LESSONS 16 is the entry about a row that is always red being ignored exactly as
        # fast as one that is always green. The absent decks are NAMED instead.
        rc, absent = 0, []
        for p in sorted(RUNS.glob("2*")):
            if not (p / "claims.json").exists():
                continue
            code = run(p, p.name)
            if code == 2:
                absent.append(p.name)
            elif code:
                rc = 1
        if absent:
            print(f"\ncontact_trace: {len(absent)} shipped run(s) published no readable surface "
                  f"and were not checked at all: {', '.join(absent)}")
        return rc
    if a.run:
        return run(RUNS / a.run, a.run)
    if a.date:
        return run(OUT / a.date, a.date)
    ap.error("one of --date, --run, --all or --self-test")
    return 2


if __name__ == "__main__":
    sys.exit(main())
