#!/usr/bin/env python3
"""texan_check.py — can a Texan tell where this happened and what to do next.

WHY THIS EXISTS. It is the only finding that appeared in EVERY scoring round of EVERY panel
and was never once attacked.

`story_and_stakes` (0.18) and `voice` (0.12) are 0.30 of the rubric between them. Across the
five panel rounds of 2026-08-19, from all three judges, NEITHER EVER REACHED 8.0, and every
judge gave the same reason in nearly the same words. The 2026-08-18 scorer put it best:

    "Change three nouns and this is Ohio."

and

    "What it never does is tell a Texan what to do next."

Twelve scoring rounds went into artwork. Zero went into this. Every round attacked the frame a
judge had named last, and the standing finding survived all of them, because a run reads a
craft note as a task and a voice note as an opinion.

WHAT IT MEASURES, AND WHY THESE FOUR THINGS

Not a taste judgement. This mechanises the rubric's OWN definition of a 9, quoted from
`config/carousel/scoring_rubric.yaml`:

    "Names the county, the body and the deadline. A reader knows what to do next."

So: the place, the body, the deadline, the next step. Four facts, each checkable, and the
place is checked against `assets/geo/tx-places.json` rather than against a word list, so a
county this project has never mentioned still counts and a person named Anderson does not.

IT DOES NOT FAIL A PLACELESS STORY, and that restraint is the whole design.

A statewide procedural item genuinely names no county, and the rubric is explicit that such a
story still scores 7 for "Clear and accurate, stakes stated generally". The 2026-08-19 run
spent six rounds insisting the placeless story capped its score, and the rubric contradicted
that in its own words the entire time. A gate that hard-failed here would encode the exact
error that run made.

What it does instead is make the profile VISIBLE, and visible EARLY. A run that knows at
selection that it has no county knows it must carry the score on art and on the closing frame,
instead of finding out from a judge in round four. That is UPGRADE_BACKLOG item 5, and the
`--text` mode is there so the selector can ask before the deck exists.

MEASURED ON THE THREE SHIPPED DECKS

    2026-08-16   Grimes County, Iola ISD        story 7.3
    2026-08-18   Bonham, Houston ISD            story 7.0
    2026-08-19   nothing                        story 8.0

The last row is the useful one. That deck named no place and still scored highest of the
three, because it built a closing frame of dated, actionable rows. That is the proof the
placeless story is not a ceiling, and it is why the "next step" half of this check matters at
least as much as the place half.

    texan_check.py --date 2026-08-19
    texan_check.py --text "ERCOT delays Batch Zero classification"   # at selection
    texan_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PLACES = REPO_ROOT / "assets" / "geo" / "tx-places.json"

# A body that decides something. The rubric asks for "the body", and a reader who cannot name
# who decided cannot tell whether it is theirs to argue with.
BODY = re.compile(
    r"\b(?:ERCOT|PUCT|Public Utility Commission|commission|commissioners court|council|"
    r"board of trustees|board|school district|legislature|senate|house committee|"
    r"Office of the Governor|Governor|attorney general|agency|department|authority|"
    r"district court|county judge|mayor)\b", re.I)   # case-insensitive: these are common
                                                     # nouns and a deck sets them as labels in
                                                     # all caps and in prose in lower case. The
                                                     # first draft missed "Board" on a deck
                                                     # about a school board.

# A date, month first, which is the house form.
DATE = re.compile(
    r"\b(?:January|February|March|April|May|June|July|August|September|October|November|"
    r"December)\s+\d{1,2}", re.I)
# CASE INSENSITIVE, and it was not until 2026-08-25. ACTION beside it always was, so one half of
# the same test read display type and the other half could not. That day's closing frame carried
# NOVEMBER 10TH at 58px, the largest numeral in the deck and the one thing a reader could still
# act on, and this gate reported the deck gave them nothing dated. Display type is set in caps as
# a matter of course, so a case sensitive month name here reads the caption and never the slide.

# Something a reader could actually do, or turn up to.
ACTION = re.compile(
    r"\b(?:public comments?|comment period|comment deadline|open meetings?|hearings?|testimony|"
    r"dockets?|project \d+|filings?|agendas?|votes?|deadlines?|comments? (?:are )?due)\b", re.I)
# PLURALS, since 2026-08-25. `hearing` could not see "the first of two required public hearings",
# which is how a closing frame actually says it. That deck passed on the word DEADLINE sitting
# elsewhere on the same frame, so the gate was right by accident about a deck it had misread.


# A NAME THAT IS ANOTHER PLACE'S FIRST WORD IS THAT OTHER PLACE. See `places_named`.
OTHER_PLACE_TAIL = r"(?!\s+(?:Count(?:y|ies)|ISD|Independent\s+School\s+District)\b)"


def gazetteer() -> tuple:
    """`(counties, cities)`, and the second set is where a Houston story went missing.

    THE DEFECT THIS EXISTS FOR. 2026-09-05, carousel no. 16, a story about a University of
    Houston led team, printing "The Houston led team" on frame 4. This gate reported
    `places NONE`, so the run record had to say in prose that the deck names a Texas city while
    its own gate said it named none.

    `assets/geo/tx-places.json` holds 254 counties, 67 CBSAs, 13 CSAs and 2 divisions, and NO
    CITIES. So the only string in the file that carries the word Houston as a CITY is the
    metropolitan area's full name, `Houston-Pasadena-The Woodlands`, which no deck has ever
    written and none ever will. The one bare Houston in the file is Houston COUNTY, a rural
    county in East Texas that has nothing to do with the story.

    Measured across sixteen shipped decks on 2026-09-05, this gate reported no place on six
    decks that name Austin, Dallas, Fort Worth or Houston in plain prose. That is the four
    largest cities in Texas, invisible to the one gate whose subject is whether a Texan can tell
    where this happened.

    THE FIX IS THE FILE'S OWN STRUCTURE RATHER THAN A TYPED LIST. OMB names a statistical area
    after its PRINCIPAL CITIES, joined with hyphens, so `Houston-Pasadena-The Woodlands` is
    already a machine readable statement that Houston, Pasadena and The Woodlands are cities.
    Splitting the delineated name on its hyphens reads that statement instead of restating it,
    and it needs no gazetteer change, which matters because `assets/` is not this lane's.

    Two guards on the split, both measured rather than assumed.

      A ROW THAT LEAVES TEXAS IS DROPPED WHOLE. `El Paso-Las Cruces, TX-NM` would otherwise
      teach this gate that Las Cruces, New Mexico is a Texas place, which is the misreport this
      file already refuses to make about a surname. Only rows whose `full_name` ends `, TX`
      contribute components. It costs Texarkana, which appears only in the `TX-AR` row, and a
      miss is the safe half of that trade.

      THE LENGTH FLOOR STAYS. A component is a city only if its name is longer than four
      characters, which is the rule this set already ran on and the reason Alice and Paris carry
      the same risk they always did.

    Replayed across all sixteen shipped decks with a `copy.json`, the split adds seven place
    findings, every one of them a real Texas city in real geographic use, and removes none.
    """
    if not PLACES.exists():
        return set(), set()
    d = json.loads(PLACES.read_text(encoding="utf-8"))
    ps = d.get("places") or []
    cities = set()
    for p in ps:
        if p.get("kind") == "county":
            continue
        name = str(p.get("name") or "")
        if len(name) > 4:
            cities.add(name)
        if not str(p.get("full_name") or "").endswith(", TX"):
            continue
        for part in name.split("-"):
            part = part.strip()
            if len(part) > 4:
                cities.add(part)
    return ({p["name"] for p in ps if p.get("kind") == "county"}, cities)


def places_named(text: str) -> list:
    """Texas places this copy actually names.

    Matched on the SHAPE a place is written in, never on the bare token. `assets/geo` carries a
    county called Anderson, and a bare-token match found it inside a person's surname on the
    2026-08-16 deck. A county counts when it is written as a county, a school district when it
    is written as one, and a city only if its name is long enough not to be an ordinary word.

    AND A CITY NAME STANDING AT THE HEAD OF ANOTHER PLACE'S NAME IS THAT OTHER PLACE. Houston is
    a principal city and it is also a rural county in East Texas and a school district, so a bare
    token match reads `Houston County` and `Houston ISD` as the city and reports a place the copy
    does not name. This is `label_guard._place_mask`'s argument one gate over: a component word is
    exempt only where its whole name stands, and here a component is a CITY only where the longer
    name does not stand. Without it the 2026-08-18 calibration gains a Houston off `Houston ISD`.
    """
    counties, cities = gazetteer()
    hits = set()
    for c in counties:
        if re.search(rf"\b{re.escape(c)}\s+Count(?:y|ies)\b", text):
            hits.add(f"{c} County")
    for c in cities:
        if re.search(rf"\b{re.escape(c)}\b" + OTHER_PLACE_TAIL, text):
            hits.add(c)
    for m in re.finditer(r"\b([A-Z][a-zA-Z]+)\s+(?:ISD|Independent School District)\b", text):
        hits.add(m.group(0))
    # One place, once. A deck sets the same district as a display line and as an all-caps label,
    # so "Iola ISD" and "IOLA ISD" are the same school district counted twice. Title case wins
    # because that is how the place is written rather than how a label is styled.
    best = {}
    for h in hits:
        k = h.lower()
        if k not in best or (h != h.upper() and best[k] == best[k].upper()):
            best[k] = h
    return sorted(best.values())


def slide_texts(copy: dict) -> list:
    out = []
    for sid, s in (copy.get("slides") or {}).items():
        if not isinstance(s, dict):
            continue
        parts = []
        for k, v in s.items():
            if k == "claims":
                continue
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, list):
                parts += [x for x in v if isinstance(x, str)]
        out.append((sid, " ".join(parts)))
    return out


def profile(text: str, closing: str = "") -> dict:
    return {
        "places": places_named(text),
        "body": bool(BODY.search(text)),
        "date": bool(DATE.search(text)),
        # The next step is judged on the CLOSING frame when there is one. A docket id buried on
        # slide 3 is not a reader knowing what to do; the last frame is where they are left.
        "next_step": bool(ACTION.search(closing or text) and DATE.search(closing or text)),
    }


def check(copy: dict) -> tuple:
    slides = slide_texts(copy)
    whole = " ".join(t for _, t in slides)
    closing = slides[-1][1] if slides else ""
    p = profile(whole, closing)
    warns = []
    if not p["places"]:
        warns.append(
            "this deck names no Texas county, city or district anywhere. That is allowed and it "
            "is not a ceiling: the rubric scores a placeless story 7 for 'stakes stated "
            "generally', and the deck that did this scored highest of the three on story. It IS "
            "a thing to know before the art is planned rather than in round four, because the "
            "score has to be carried somewhere else")
    if not p["next_step"]:
        warns.append(
            "the closing frame gives a reader nothing dated to act on. The rubric's 9 for "
            "story_and_stakes is 'a reader knows what to do next', and 2026-08-18's scorer "
            "wrote 'what it never does is tell a Texan what to do next' about a deck that had "
            "every other ingredient")
    if not p["body"]:
        warns.append("no deciding body is named, so a reader cannot tell whose decision this is")
    return [], warns, p


def render(p: dict) -> str:
    """One line, and NO pipe characters in it.

    gate_status drops this straight into a markdown table cell, and a pipe there splits the row
    into columns that do not exist. The run record is read as rendered markdown, so a separator
    that is also table syntax corrupts the artifact this line exists to inform.
    """
    return (f"places {', '.join(p['places']) if p['places'] else 'NONE'}"
            f" / body {'yes' if p['body'] else 'NO'}"
            f" / deadline {'yes' if p['date'] else 'NO'}"
            f" / next step {'yes' if p['next_step'] else 'NO'}")


def run(date: str | None, text: str | None, quiet: bool = False) -> int:
    if text:
        p = profile(text)
        print(f"texan_check (selection): {render(p)}")
        if not p["places"]:
            print("  note  this candidate names no Texas place. Brief the directors room that "
                  "the score has to be carried on art and on the closing frame", file=sys.stderr)
        return 0
    for base in (REPO_ROOT / "out" / date, REPO_ROOT / "runs" / "carousel" / date):
        if (base / "copy.json").exists():
            copy = json.loads((base / "copy.json").read_text(encoding="utf-8"))
            break
    else:
        print(f"texan_check: no copy.json for {date}", file=sys.stderr)
        return 1
    fails, warns, p = check(copy)
    for w in warns:
        print(f"  warn  {w}", file=sys.stderr)
    if not quiet:
        print(f"texan_check: {render(p)}")
    return 1 if fails else 0


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    ok("the gazetteer is present and carries places", all(gazetteer()))

    # THE REAL FALSE POSITIVE. 2026-08-16's copy carries a surname that is also a county name.
    ok("a bare county token inside a surname is NOT a place",
       places_named("Anderson said the plant is announced.") == [],
       str(places_named("Anderson said the plant is announced.")))
    ok("...and the same county written as a county IS",
       places_named("Grimes County approved it.") == ["Grimes County"],
       str(places_named("Grimes County approved it.")))
    ok("a school district counts", "Houston ISD" in places_named("Houston ISD voted."))

    # THE 2026-09-05 DEFECT, REPLAYED. The gazetteer holds no cities, so before the principal
    # city split this line measured NONE on a deck whose whole story is a Houston led team. The
    # first two assertions go red on the unsplit set and the third goes red without the tail
    # guard, because a bare token match reads the East Texas county as the city.
    _c, _cities = gazetteer()
    ok("the gazetteer yields Houston as a principal city, not only inside its metro's full name",
       "Houston" in _cities)
    ok("a deck naming the city of Houston reports it",
       places_named("The Houston led team aims to surpass neodymium.") == ["Houston"],
       str(places_named("The Houston led team aims to surpass neodymium.")))
    ok("...and Houston County is the county, never the city",
       places_named("Houston County approved it.") == ["Houston County"],
       str(places_named("Houston County approved it.")))
    ok("...and Houston ISD is the district, never the city",
       places_named("Houston ISD voted.") == ["Houston ISD"],
       str(places_named("Houston ISD voted.")))
    # A ROW THAT LEAVES TEXAS CONTRIBUTES NOTHING. `El Paso-Las Cruces, TX-NM` would otherwise
    # make a New Mexico city a Texas place, which is the misreport this file refuses to make.
    ok("a New Mexico principal city is not a Texas place",
       places_named("Las Cruces filed a brief.") == [],
       str(places_named("Las Cruces filed a brief.")))

    # The closing frame decides the next step, not a docket buried mid deck.
    p = profile("Project 58482 took a comment on August 18th. Nothing else.",
                closing="Nothing here but a hook.")
    ok("a docket buried off the closing frame is NOT a next step", not p["next_step"], str(p))
    p = profile("x", closing="September 4th, 2026. Public comment deadline on the calendar.")
    ok("a dated action ON the closing frame IS a next step", p["next_step"], str(p))

    # A DATE SET IN DISPLAY CAPS IS STILL A DATE (2026-08-25). ACTION was case insensitive and
    # this was not, so the same test could read a caption and not a slide.
    p = profile("x", closing="NOT LATER THAN NOVEMBER 10TH. THE FIRST OF TWO PUBLIC HEARINGS.")
    ok("a dated action set in display caps IS a next step", p["next_step"], str(p))
    p = profile("x", closing="ONE DOOR IS STILL OPEN. NOTHING SCHEDULED.")
    ok("...and caps alone do not conjure one", not p["next_step"], str(p))

    # CALIBRATION against shipped decks, so drift shows up as a number.
    #
    # 2026-09-05 is here because it is the deck the principal city split was written for, and
    # 2026-08-25 is here because it is the one row the split CHANGED. It used to report both
    # `Lubbock` and `Lubbock County` for a copy whose only Lubbock is `Lubbock County`, so the
    # tail guard removed a duplicate rather than a finding. Every Lubbock in that copy was
    # measured before this line was written rather than argued about.
    expect = {"2026-08-16": ["Grimes County", "Iola ISD"],
              "2026-08-18": ["Bonham", "Houston ISD"],
              "2026-08-19": [],
              "2026-08-25": ["Brazoria County", "El Paso", "Fort Worth", "Hays County",
                             "Hill County", "Lubbock County", "San Angelo", "Tom Green County",
                             "Wichita Falls", "Williamson County"],
              "2026-09-05": ["Houston"]}
    for date, want in expect.items():
        cp = REPO_ROOT / "runs" / "carousel" / date / "copy.json"
        if not cp.exists():
            continue
        copy = json.loads(cp.read_text(encoding="utf-8"))
        _f, _w, p = check(copy)
        ok(f"{date}: places measured as {want or 'none'}", p["places"] == want, str(p["places"]))
        ok(f"{date}: no hard fail, because a placeless story is not a failure", not _f, str(_f))

    print("\ntexan_check self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date")
    ap.add_argument("--text", help="a candidate story, at selection, before any deck exists")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not (a.date or a.text):
        ap.error("--date, --text or --self-test")
    return run(a.date, a.text)


if __name__ == "__main__":
    raise SystemExit(main())
