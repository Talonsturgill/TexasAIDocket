#!/usr/bin/env python3
"""numeral_trace.py — a numeral a frame prints has to be reachable from a claim that frame cites.

THE DEFECT THIS EXISTS FOR. 2026-08-29, deck no. 11, round 4, a scoring hard fail.

Six frames printed the eyebrow `NSF AWARD 2535195`. The cite line beside it named c34. c34 is the
agency's news release about three new centres, and its quote is:

    "Researchers will combine robotics, AI, and human factors to develop new methods ..."

The string 2535195 is not in it. It is not in c34's text, its document title or its url either,
because c34 came off a different document. A reader who did what the frame invites, follow the id
and check the number, arrives at a page that does not contain the number.

**Every gate was green.** `copy_sync_check` proved the id RESOLVES, which it did, and its quotation
half only reads text set between quotation marks, and this eyebrow is not a quotation. Its own
docstring says so under NOT COVERED. `claims_check` proved c34 is fetched and quoted.
`aggregate_check` reads four aggregate SHAPES, a count, a duration, a span and a ratio, and an
award number is none of them, so nothing asked where 2535195 came from. `label_guard` reads the
capitalised WORDS before an id and skips numerals outright, by an explicit `[0-9-]+` test, and it
skips any element carrying more than one id, which the cite line is.

The repair the run made is the shape of the right answer. It fetched the award record's own id
field, wrote it down as c35, and cited c35 on the frames that print the number. This gate is what
would have said so in round 1 instead of round 4.

WHAT IT CHECKS

Every numeral token the browser laid out on a frame is authorised if its digits occur in the
EVIDENCE of a claim that frame declares, being that claim's quote, its text, the document title
and the source url. Anything else is a numeral on a published frame that traces to nothing a
reader can reach.

THE FOUR FIELDS, AND WHY IT IS NOT ONLY THE QUOTE.

`copy_sync_check` compares a QUOTATION against the quote alone, and it is right to: a frame that
sets words in quotation marks is telling a reader a document said them, and the claim's text is
this project's own sentence. A numeral is a different question. Measured over the ten shipped
decks, restricting to the quote alone adds seven findings and every one of them is correct work:
c5 of 2026-08-18 quotes one line of a daily schedule and its text carries the 110 and 90 minute
blocks the run read off the same page, and a gate that fires there teaches a run to pad quotes.
Document title and url carry the docket and award numbers that identify the fetched thing, which
is entry 47's shape exactly: the exemption is earned per claim from that claim's own evidence,
never granted by a list of numbers somebody typed.

    quote      the source's own words
    text       the run's record of what that document says
    document   the title of the fetched artifact
    url        its address, which is where a docket or award number usually lives

WHAT ELSE AUTHORISES A NUMERAL

    a declaration in aggregates.json. `aggregate_check` re-derives every one of those from the
    claim ids it names and fails when the arithmetic disagrees, so a value it has already judged
    is not judged twice here. Deferring to the gate that owns the question is deliberate: two
    gates with two opinions about one number is how a run learns to argue with whichever one it
    likes less.

THE TWO EXEMPTIONS, EACH A SPECIFIC THING

    the slide counter   `03 / 09` is furniture the engine writes, not a figure the deck claims.
    a decorative node   the design already marks its own furniture and every other carousel gate
                        reads that marker. It is also what stops the render report's concatenated
                        parent nodes being read as figures: `SB 2807254 COUNTIES` is two adjacent
                        spans and no number at all, and it is marked decorative on the frame.

WHAT THIS CANNOT SEE, stated rather than implied.

A numeral that is authorised by COINCIDENCE. If a frame prints 2026 and a declared claim's url
carries 2026, the digits match and nothing here can tell a year from a docket number. Entry 47
names this and it is the price of an evidence-scoped allowlist: it is right far more often than a
site-wide one, and it is not proof. The gate is about a numeral that traces to NOTHING, which is
the defect that shipped.

MEASURED, on every deck this repo has rendered before today: 86 frames, 205 numeral tokens, 15
untraced. Each of the fifteen was read by hand and each is a real one of the same kind. Three
frames of 2026-08-22 print PROJECT 58482 while fourteen claims carry that number and none of the
three frames declares one of them. 2026-08-28 frame 2 prints 265.5 MW citing five claims, and the
figure is in a sixth. 2026-08-28 frame 6 prints 100 MW, which no claim in that run carries at all.
The 2026-08-29 deck as it shipped comes back clean, which is the discrimination this gate needs:
it separates the round 4 frame from the round 5 repair of the same frame.

    numeral_trace.py <run-dir>
    numeral_trace.py --self-test

Run it by EXIT CODE. 0 clean, 1 a numeral the record does not reach, 2 the checker could not run.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# WHOLE TOKENS, NEVER A SHAPE MATCH IN THE MIDDLE OF A STRING. GATE_LESSONS 16 and 18.
#
# `aggregate_check` matches SHAPES, a number followed by a plural noun and so on, and its own
# header records what that cost: `\d{1,4}` read "2,600 streamlines" as 600 and named a figure the
# slide does not contain. Its NUM pattern still caps at four digits because an aggregate here has
# never been larger, and on `2535195` it would match `2535` and report a number nobody printed.
#
# This gate asks a different question and so tokenises rather than pattern-matches: split on
# whitespace, strip the punctuation a writer puts around a token, and keep what is entirely
# digits, commas and points. `2535195` is one token. `$30` is one token once the currency mark is
# stripped. There is no shape to get wrong because no shape is being looked for.
#
# It is deliberately NOT a second copy of aggregate_check's regex. Two tokenisers for one
# alphabet is entry 34's fault and this is not that: one is a detector of aggregate PHRASES, the
# other splits a string into words. They answer different questions and share no pattern.
NUMERAL_TOKEN = re.compile(r"[0-9][0-9,.]*")
STRIP = "“”‘’.,\"'()[]{}:;!?$%·–—-•/"

# The engine's own progress counter. `coherence_check` owns whether the deck is numbered and
# whether the numbering is honest; this is only saying the counter is not a claim about the world.
SLIDE_COUNTER = re.compile(r"^\s*\d{1,3}\s*/\s*\d{1,3}\s*$")

EVIDENCE_FIELDS = ("quote", "text", "document", "url")


def digits(s) -> str:
    return re.sub(r"[^0-9]", "", str(s))


def evidence(claims) -> dict[str, str]:
    """Each claim id mapped to the digits of everything a reader could reach through it."""
    items = (claims.get("claims") or claims.get("verified_claims") or []) if claims else []
    out: dict[str, str] = {}
    for c in items:
        if not isinstance(c, dict):
            continue
        cid = next((str(c[k]) for k in ("id", "claim_id", "cid") if c.get(k)), None)
        if cid:
            out[cid] = digits(" ".join(str(c.get(k) or "") for k in EVIDENCE_FIELDS))
    return out


def declared_values(aggregates) -> set[str]:
    """Digits of every figure the run DECLARED and `aggregate_check` re-derives."""
    out = set()
    for a in ((aggregates or {}).get("aggregates") or []):
        if not isinstance(a, dict):
            continue
        out.add(digits(a.get("value")))
        for t in NUMERAL_TOKEN.findall(str(a.get("phrase") or "")):
            out.add(digits(t))
    out.discard("")
    return out


def slide_no(rec) -> int | None:
    n = rec.get("n") or rec.get("slide")
    if n is None:
        m = re.search(r"(\d+)", str(rec.get("file", "")))
        n = m.group(1) if m else None
    try:
        return int(n)
    except (TypeError, ValueError):
        return None


def tokens_in(text: str) -> list[str]:
    out = []
    for w in str(text).split():
        w = w.strip(STRIP)
        if w and NUMERAL_TOKEN.fullmatch(w):
            out.append(w)
    return out


def check(copy: dict, report: dict, claims: dict, aggregates: dict | None = None):
    """Returns (problems, stats). Empty problems means every numeral is reachable."""
    ev = evidence(claims)
    allowed = declared_values(aggregates)
    slides = copy.get("slides") or {}
    problems, examined = [], 0

    for rec in report.get("slides") or []:
        n = slide_no(rec)
        if n is None:
            continue
        blk = slides.get(f"S{n}")
        cited = [str(c) for c in ((blk or {}).get("claims") or [])]
        hay = " ".join(ev.get(c, "") for c in cited)
        for node in rec.get("text_nodes") or []:
            if node.get("decorative"):
                continue
            text = str(node.get("text", ""))
            if SLIDE_COUNTER.match(text.strip()):
                continue
            for tok in tokens_in(text):
                d = digits(tok)
                if not d:
                    continue
                examined += 1
                if d in hay or d in allowed:
                    continue
                elsewhere = sorted(c for c, e in ev.items() if e and d in e)
                shown = text if len(text) <= 56 else text[:53] + "..."
                if elsewhere:
                    problems.append(
                        f"s{n} prints {tok!r} in \"{shown}\" and the claims that frame cites "
                        f"({', '.join(cited) or 'none'}) carry no such figure. "
                        f"{', '.join(elsewhere)} do. Cite the claim the number came from")
                else:
                    problems.append(
                        f"s{n} prints {tok!r} in \"{shown}\" and NO claim in this run carries "
                        f"that figure in its quote, its text, its document title or its url. "
                        f"The frame cites {', '.join(cited) or 'nothing'}. Fetch the span that "
                        f"states it and make it a claim, or declare it in aggregates.json where "
                        f"aggregate_check can re-derive it")
    return problems, {"examined": examined, "frames": len(report.get("slides") or [])}


# --------------------------------------------------------------------------- run
def run(run_dir: Path) -> int:
    copy_p = run_dir / "copy.json"
    claims_p = run_dir / "claims.json"
    rep_p = run_dir / "render" / "render_report.json"
    if not rep_p.exists():
        rep_p = run_dir / "render_report.json"
    for p in (copy_p, claims_p, rep_p):
        if not p.exists():
            print(f"numeral_trace: {p} is missing. Run the render before this gate.",
                  file=sys.stderr)
            return 2
    try:
        copy = json.loads(copy_p.read_text(encoding="utf-8"))
        claims = json.loads(claims_p.read_text(encoding="utf-8"))
        report = json.loads(rep_p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"numeral_trace: unreadable artifact: {exc}", file=sys.stderr)
        return 2
    agg_p = run_dir / "aggregates.json"
    aggregates = json.loads(agg_p.read_text(encoding="utf-8")) if agg_p.exists() else None

    problems, stats = check(copy, report, claims, aggregates)
    # THE RECEIPT, the same wiring label_guard and quantifier_check use. `gate_status` reads it,
    # so the run record's table carries the row and a run cannot quietly skip the gate. CI cannot
    # take it, because .github/workflows belongs to the human actor by ownership.yaml.
    (run_dir / "numeral_report.json").write_text(
        json.dumps({"examined": stats["examined"], "frames": stats["frames"],
                    "problems": problems}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    if problems:
        print(f"numeral_trace: {len(problems)} numeral(s) the cited claims do not reach, "
              f"of {stats['examined']} examined across {stats['frames']} frame(s)\n")
        for p in problems:
            print("  - " + p + "\n")
        print("  A numeral beside a claim id tells a reader the id is where the number came\n"
              "  from. On 2026-08-29 an award number sat on six frames over a claim whose\n"
              "  document does not contain it, and every other gate was green, because each of\n"
              "  them proved something true about a different question. FIX THE CITATION, or\n"
              "  fetch the span that states the figure. Never write a claim around a number the\n"
              "  deck has already drawn.")
        return 1
    print(f"numeral_trace: {stats['examined']} numeral(s) across {stats['frames']} frame(s), "
          f"every one reachable from a claim its frame cites")
    return 0


# --------------------------------------------------------------------------- self-test
def _report_of(*per_slide):
    return {"slides": [{"file": f"slide-{i:02d}.html", "n": i,
                        "text_nodes": [t if isinstance(t, dict) else {"text": t} for t in texts]}
                       for i, texts in enumerate(per_slide, start=1)]}


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    # ---------------------------------------------------------------- THE REAL DEFECT
    #
    # Replayed against the run's OWN COMMITTED CLAIMS FILE. The claims half is not reconstructed.
    # The frame half is the eyebrow and the cite line as they stood in round 4, which the run's
    # panel record names: the award number cited to c34.
    #
    # A MISSING FILE IS A FAILURE HERE, NEVER A SKIP. GATE_LESSONS 37: a skip and a check that
    # cannot run print the same colour, and this is the one case in the file that proves the gate
    # goes red on something that really happened.
    shipped = REPO_ROOT / "runs" / "carousel" / "2026-08-29"
    if not (shipped / "claims.json").exists():
        ok("the 2026-08-29 claims file is present to replay round 4 against", False, str(shipped))
    else:
        real = json.loads((shipped / "claims.json").read_text(encoding="utf-8"))
        round4 = {"slides": {"S1": {"claims": ["c21", "c22", "c34"]}}}
        rep = _report_of(["NSF AWARD 2535195", "c21 c22 c34"])
        probs, st = check(round4, rep, real)
        ok("the round 4 award number cited to c34 is CAUGHT", len(probs) == 1, str(probs))
        ok("...and the message names the number", bool(probs) and "2535195" in probs[0], str(probs))
        ok("...and it names the claim that DOES carry it, so the fix is one line",
           bool(probs) and "c35" in probs[0], str(probs))
        ok("...and it names the claims the frame actually cited",
           bool(probs) and "c21, c22, c34" in probs[0], str(probs))
        ok("...and the token was examined rather than skipped", st["examined"] >= 1, str(st))

        # THE ROUND 5 REPAIR, which is the discrimination test. A gate that cannot tell the fix
        # from the defect has measured nothing. Same words, same frame, one id changed.
        round5 = {"slides": {"S1": {"claims": ["c21", "c22", "c35"]}}}
        probs, _ = check(round5, _report_of(["NSF AWARD 2535195", "c21 c22 c35"]), real)
        ok("the round 5 repair, citing c35, is clean", probs == [], str(probs))

        # THE WHOLE SHIPPED DECK, against its own committed copy.json. The nine frames as they
        # went out must come back clean or the carve-outs are wrong in the other direction.
        if (shipped / "copy.json").exists():
            shipped_copy = json.loads((shipped / "copy.json").read_text(encoding="utf-8"))
            agg = shipped / "aggregates.json"
            shipped_agg = json.loads(agg.read_text(encoding="utf-8")) if agg.exists() else None
            # the frames as copy.json records them, which copy_sync_check proves is what rendered
            synth = {"slides": []}
            for key, blk in shipped_copy["slides"].items():
                n = int(re.search(r"(\d+)", key).group(1))
                strings = [blk.get("hook") or "", blk.get("dek") or ""]
                strings += [str(x) for x in (blk.get("labels") or [])]
                synth["slides"].append({"file": f"slide-{n:02d}.html", "n": n,
                                        "text_nodes": [{"text": s} for s in strings if s]})
            probs, st = check(shipped_copy, synth, real, shipped_agg)
            ok("the shipped 2026-08-29 deck is clean on all nine frames", probs == [], str(probs))
            ok("...and it examined numerals rather than passing by examining none",
               st["examined"] > 0, str(st))

    # ---------------------------------------------------------------- THE CARVE-OUTS
    cl = {"claims": [
        {"id": "c1", "quote": "the queue holds 6,180 megawatts", "text": "", "document": "",
         "url": "https://interchange.puc.texas.gov/Documents/59220_1_1.pdf"},
        {"id": "c2", "quote": "nothing numeric at all", "text": "", "document": "", "url": ""},
    ]}
    d = {"slides": {"S1": {"claims": ["c1"]}}}
    ok("a figure the cited claim quotes passes",
       check(d, _report_of(["6,180 MEGAWATTS"]), cl)[0] == [])
    ok("...and a thousands separator is not split into two tokens",
       check(d, _report_of(["6,180 MEGAWATTS"]), cl)[1]["examined"] == 1,
       str(check(d, _report_of(["6,180 MEGAWATTS"]), cl)[1]))
    ok("a docket number that only the cited claim's URL carries passes",
       check(d, _report_of(["PUCT DOCKET 59220"]), cl)[0] == [])
    ok("a figure NO claim carries is CAUGHT",
       len(check(d, _report_of(["100 MW"]), cl)[0]) == 1)
    ok("...and the message says no claim in the run carries it",
       "NO claim in this run" in check(d, _report_of(["100 MW"]), cl)[0][0])
    ok("a figure another claim carries but this frame does not cite is CAUGHT",
       len(check({"slides": {"S1": {"claims": ["c2"]}}},
                 _report_of(["6,180 MEGAWATTS"]), cl)[0]) == 1)
    ok("...and it names the claim that has it",
       "c1" in check({"slides": {"S1": {"claims": ["c2"]}}},
                     _report_of(["6,180 MEGAWATTS"]), cl)[0][0])
    ok("a frame that cites nothing at all cannot support a figure",
       len(check({"slides": {"S1": {}}}, _report_of(["6,180 MEGAWATTS"]), cl)[0]) == 1)

    # The slide counter is the engine's furniture, and a gate that reported it would report nine
    # findings a deck forever. GATE_LESSONS 16: a gate that cries wolf nine times teaches the run
    # to scroll past the tenth.
    ok("the slide counter is not a claim about the world",
       check(d, _report_of(["03 / 09"]), cl)[0] == [])
    ok("...and it is not counted as examined either",
       check(d, _report_of(["03 / 09"]), cl)[1]["examined"] == 0)
    ok("a decorative node is the design's own furniture and is skipped",
       check(d, _report_of([{"text": "SB 2807254 COUNTIES", "decorative": True}]), cl)[0] == [])
    ok("...but the same string NOT marked decorative is judged",
       len(check(d, _report_of([{"text": "SB 2807254 COUNTIES"}]), cl)[0]) == 1)

    # A DECLARED AGGREGATE IS aggregate_check's QUESTION, and answering it twice with two
    # opinions is how a run learns to argue with whichever gate it likes less.
    agg = {"aggregates": [{"phrase": "481 DAYS", "kind": "duration", "value": 481,
                           "claim_ids": ["c1"]}]}
    ok("a figure declared in aggregates.json passes here",
       check(d, _report_of(["481 DAYS"]), cl, agg)[0] == [])
    ok("...and the same figure with no declaration is CAUGHT",
       len(check(d, _report_of(["481 DAYS"]), cl, None)[0]) == 1)

    # THE TOKENISER. Punctuation a writer puts around a number is not part of the number, and a
    # token that is not a numeral is not a numeral.
    ok("a currency mark is stripped rather than making the token unreadable",
       check({"slides": {"S1": {"claims": ["c1"]}}},
             _report_of(["$6,180"]), cl)[1]["examined"] == 1)
    ok("a word containing digits is not read as a figure",
       check(d, _report_of(["CQD-2026A"]), cl)[1]["examined"] == 0,
       str(check(d, _report_of(["CQD-2026A"]), cl)))
    ok("prose with no numeral in it examines nothing",
       check(d, _report_of(["The rooms are named."]), cl)[1]["examined"] == 0)

    # ---------------------------------------------------------------- CALIBRATION
    #
    # Every deck this repo has rendered, with the count of findings ASSERTED rather than the
    # silence. GATE_LESSONS 26: a run that covered almost nothing must not read as a run that
    # found nothing. These fifteen were each read by hand and each is a real one; they are pinned
    # so a later change to the matching rule that quietly dissolves them shows up here.
    expected = {"2026-08-16": 2, "2026-08-18": 0, "2026-08-19": 1, "2026-08-20": 0,
                "2026-08-21": 1, "2026-08-22": 4, "2026-08-25": 5, "2026-08-26": 0,
                "2026-08-27": 0, "2026-08-28": 2}
    seen, tokens = 0, 0
    for name, want in sorted(expected.items()):
        base = REPO_ROOT / "runs" / "carousel" / name
        rp = base / "render_report.json"
        if not (rp.exists() and (base / "copy.json").exists() and (base / "claims.json").exists()):
            continue
        seen += 1
        ap = base / "aggregates.json"
        probs, st = check(json.loads((base / "copy.json").read_text(encoding="utf-8")),
                          json.loads(rp.read_text(encoding="utf-8")),
                          json.loads((base / "claims.json").read_text(encoding="utf-8")),
                          json.loads(ap.read_text(encoding="utf-8")) if ap.exists() else None)
        tokens += st["examined"]
        ok(f"{name}: {want} untraced numeral(s), as measured", len(probs) == want,
           f"got {len(probs)}: " + str(probs)[:220])
    ok("the calibration read the shipped decks rather than finding none", seen >= 8, str(seen))
    ok("...and it examined a real corpus of numerals", tokens > 200, str(tokens))
    ok("the module header states the blind spot rather than implying coverage",
       "WHAT THIS CANNOT SEE" in (__doc__ or "") and "COINCIDENCE" in (__doc__ or ""))

    if failures:
        print(f"\nnumeral_trace self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nnumeral_trace self-test: all passed ({tokens} numeral tokens over {seen} decks)")
    return 0


def main(argv) -> int:
    if "--self-test" in argv:
        return self_test()
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: numeral_trace.py <run-dir> | --self-test", file=sys.stderr)
        return 2
    d = Path(args[0])
    if not d.is_dir():
        print(f"not a directory: {d}", file=sys.stderr)
        return 2
    return run(d)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:                                            # noqa: BLE001
        print(f"numeral_trace: broke: {exc}", file=sys.stderr)
        sys.exit(2)
