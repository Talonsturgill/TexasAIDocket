#!/usr/bin/env python3
"""verbatim_check.py — a fragment set in a verbatim slot is the source's own words.

THE DEFECT THIS EXISTS FOR (2026-09-04, carousel no. 15). Three judges, working independently,
found FIVE strings on the shipped frames that look sourced and are not. Every gate was green.

  frame 8  IT DID JUST THAT      on a plate under the heading STATED, where the dossier says each
                                 plate carries one verbatim fragment of what the account DOES say.
                                 The phrase was in no claim quote at all.
  frame 8  HIGH QUALITY IMAGES   c9 says "high-quality facial images". The frame silently dropped
                                 the word that narrows it, in a verbatim slot, beside a real quote.
  frame 4  MARYLAND, ROOFED      a physical assertion about a real place, in no claim.
  frame 4  PROGRESO, OPEN SKY    the same, and it contradicted the deck's own frame 1.
  frame 6  CARRIL DE CAPTURA     Spanish sign text on a frame whose whole subject is what the signs
           CARRIL DE EXCLUSION   said. The source says only that the signs were in English and
                                 Spanish. It never says what they said.

WHY THE TWO GATES THAT EXIST BOTH PASSED, and neither was wrong on its own question.

`label_guard.py` tests a LABEL BESIDE A CLAIM ID. Its window is the capitalised run in the few
elements before an id, so a plate seated in the art region, with the citation chip a third of a
frame away in the footer, is outside it and always was.

`noun_trace.py` warns on named THINGS that appear in no claim. `IT DID JUST THAT` names no thing.
It is a SENTENCE, and its whole defect is that it wears the costume of a quotation.

WHAT THIS DOES, IN TWO DIRECTIONS, AND ONLY ONE OF THEM CAN FAIL

  DECLARED   the hard half. A dossier that seats a fragment of the source's own words on a frame
             lists it, with the claim it came from, under a `verbatim:` key. Every listed string
             must be a literal substring of THAT claim's own quote, after the normalisation stated
             below, and must actually be on the frame. Exit 1 on either.

  DISCOVERED the soft half, and it never fails. Where a frame prints one all-caps label that IS a
             literal fragment of a claim's quote, every other all-caps label set in the SAME
             RENDERED STYLE on that frame is standing in the same slot and claiming the same
             provenance. Any that trace to no claim are listed for a human to read.

WHY THE SECOND HALF ONLY WARNS, measured rather than argued. Replayed across all fifteen shipped
decks it names three groups: 2026-08-16's FIRST PHASE CAPITAL, 2026-08-25's four abatement matter
titles and 2026-09-03's 8 STATE AGENCIES. At least two of those are legitimate authored labels
sitting beside a quoted one. A machine cannot tell an authored label from a paraphrase, and
`knowledge/carousel/TECHNIQUE_LIBRARY.md` records what happens to a gate that fires on correct
behaviour: it gets switched off, and then it protects nothing. So the discovery half prints a list
somebody reads in seconds and decides nothing.

WHAT THE TWO HALVES ACTUALLY CATCH, REPLAYED AGAINST THIS RUN'S OWN RENDER REPORT rather than
against a fixture, because a fixture written beside a detector agrees with it.

  Restore the deck the panel saw, which is c31 removed from `claims.json` and the word `FACIAL`
  taken back out of frame 8's second plate, and the DISCOVERY half names both fabrications with
  no declaration anywhere in the storyboard. On the repaired deck it is silent. So the two
  strings that reached three judges are caught by this gate as it stands today, on a deck written
  the way this project already writes them.

  Frame 4's two place assertions and frame 6's two Spanish sign strings are caught only where the
  dossier DECLARES them, because their slots hold no quoted anchor to discover. That is the
  honest limit and it is stated rather than papered over. The answer to it is the spec, not a
  cleverer detector: `SLIDE_DOSSIER_SPEC.md` now requires a `verbatim:` key on any frame that
  seats source wording.

An earlier draft of this file made the discovery half a hard fail. Measured, it went red on the
REPAIRED deck of 2026-09-04, on frame 3, where `AND AIFI` is a line-wrapped fragment of
`PARAVISION AND AIFI` and `SOLUTION 1` beside it is a legitimate authored label. That measurement
is the whole argument for the split, and it is why an anchor may not begin with a conjunction.

THE NORMALISATION, STATED ONCE, because a comparison whose rules are not written down is a
comparison nobody can argue with.

  curly quotes become straight, dashes become spaces, every run of characters that is not a
  letter or a digit becomes one space, and the whole is case folded and trimmed.

It is deliberately loose in ONE direction. It can only make a match MORE likely, never less, so a
failure here is never about punctuation and is always about a word. `HIGH-QUALITY FACIAL` matches
`high-quality facial images` under it, which is the hyphen case that bit c9. `HIGH QUALITY IMAGES`
does not, because `images` is not the word that follows `quality` in the source.

RUN IT BY EXIT CODE. 0 clean, 1 a declared fragment the record does not carry, 2 could not run.

    verbatim_check.py --date 2026-09-04
    verbatim_check.py --run 2026-09-04
    verbatim_check.py --self-test
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# THE DECLARATION. One spelling, and the spec says so, because two spellings of one idea is how
# `sources_block` ended up accepting a neighbour gate's flag as a prefix and reading nothing.
#
#   verbatim:
#     - c7: "EXCEEDED EXPECTATIONS"
#     - c9: "HIGH-QUALITY FACIAL"
#
# `verbatim: []` is the explicit none, and it means something different from the key being absent:
# the run looked and says this frame seats no fragment of anybody's words.
VERBATIM_BLOCK = re.compile(r"^verbatim:[ \t]*(\[\s*\])?[ \t]*\n((?:[ \t]+-[ \t]+.*\n)*)", re.M)
VERBATIM_ITEM = re.compile(r"^[ \t]*-[ \t]*(c\d+)[ \t]*:[ \t]*\"([^\"]+)\"[ \t]*$")

# The deck's own standing furniture, recognised by SHAPE rather than by a word list, because a
# word list is an allowlist and GATE_LESSONS 39 is the entry about what an allowlist does not see.
COUNTER = re.compile(r"^\s*\d{1,2}\s*/\s*\d{1,2}\s*$")           # 08 / 09
CHIP = re.compile(r"^\s*c\d+(\s+c\d+)*\s*$", re.I)               # c18 c19 c20
URLISH = re.compile(r"^[A-Za-z0-9.·\- ]+\.(com|edu|gov|org|net)\b", re.I)

# A phrase opening on a connective is a CONTINUATION, not a fragment somebody seated. Frame 3 of
# the repaired 2026-09-04 deck wraps `PARAVISION AND AIFI` across two nodes, and the tail `AND
# AIFI` is a literal substring of a quote purely because the quote contains those two words in
# that order. Reading it as an anchor turned two correct authored labels into a finding.
CONTINUATION = {"and", "or", "of", "the", "to", "for", "a", "an", "in", "on", "at", "by",
                "with", "from", "that", "which"}


class CouldNotRun(Exception):
    """Exit 2. Never exit 1 for a thing the gate was unable to look at."""


def norm(s: str) -> str:
    """The stated normalisation. See the docstring: loose in one direction only."""
    s = (s or "")
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", " "), ("—", " ")):
        s = s.replace(a, b)
    return " ".join(re.sub(r"[^0-9a-z]+", " ", s.lower()).split())


def parse_dossiers(storyboard: str) -> dict:
    """Slide number to its YAML-ish block. The same fenced form dossier_check reads."""
    return {int(n): body for n, body in
            re.findall(r"```yaml\s*\nslide:\s*(\d+)\s*\n(.*?)```", storyboard, re.S)}


def declared_verbatim(body: str) -> tuple:
    """`(entries, declared_at_all)`. Entries are `(claim_id, string)` in written order.

    THE EMPTY CASE AND THE ABSENT CASE ARE DIFFERENT EVENTS and this returns both, because a
    checker whose "nothing to do" and "nothing found" print the same line is the shape
    `sources_block` shipped behind an exit code of 0 for a whole run.
    """
    m = VERBATIM_BLOCK.search(body)
    if not m:
        return [], False
    entries = []
    for line in (m.group(2) or "").splitlines():
        im = VERBATIM_ITEM.match(line)
        if im:
            entries.append((im.group(1).lower(), im.group(2).strip()))
    return entries, True


def slide_nodes(report: dict, n: int) -> list:
    """Every text node dict for one slide, in document order."""
    for s in report.get("slides") or []:
        if f"{n:02d}" in str(s.get("file", "")):
            return [t for t in (s.get("text_nodes") or []) if (t.get("text") or "").strip()]
    return []


def style_of(node: dict) -> tuple:
    """The rendered style signature a slot is defined by.

    A VERBATIM SLOT IS A THING A READER SEES, not a thing a class name asserts. On the deck this
    gate was written for the three seated plates are canvas-drawn text nodes carrying no class at
    all, and what separates them from the five empty-cavity labels beside them is that they are
    weight 700 in near-black ink and the others are weight 500 in grey. That difference is in
    `render_report.json` already, measured by the renderer, so the slot is read rather than
    guessed. A class-based rule would have found nothing on this deck.
    """
    return (node.get("font_px"), str(node.get("weight")), node.get("family"), node.get("color"))


def is_caps_label(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and all(c.isupper() for c in letters)


def furniture(text: str, everywhere: set) -> bool:
    return bool(text in everywhere or COUNTER.match(text) or CHIP.match(text)
                or URLISH.match(text))


def repeated_on_every_frame(report: dict) -> set:
    """Strings on every frame of the deck. The masthead and the site line, derived not listed."""
    per = []
    for s in report.get("slides") or []:
        per.append({(t.get("text") or "").strip()
                    for t in (s.get("text_nodes") or []) if (t.get("text") or "").strip()})
    return set.intersection(*per) if len(per) > 1 else set()


# ------------------------------------------------------------------ the two directions

def check_declared(dossiers: dict, claims: list, report: dict) -> tuple:
    """The hard half. Returns `(fails, declared_count, slides_declaring)`."""
    by_id = {str(c.get("id", "")).lower(): c for c in claims}
    quotes = {cid: norm(c.get("quote") or "") for cid, c in by_id.items()}
    fails, declared, slides = [], 0, []

    for n, body in sorted(dossiers.items()):
        entries, present = declared_verbatim(body)
        if present:
            slides.append(n)
        nodes = slide_nodes(report, n)
        frame = norm(" ".join(str(t.get("text") or "") for t in nodes))
        for cid, want in entries:
            declared += 1
            claim = by_id.get(cid)
            if claim is None:
                fails.append(f"slide {n}: the dossier declares {want!r} as verbatim from {cid} "
                             f"and claims.json has no such claim")
                continue
            q = quotes.get(cid, "")
            w = norm(want)
            if not q:
                fails.append(
                    f"slide {n}: the dossier declares {want!r} as verbatim from {cid} and {cid} "
                    f"carries no quote. A verbatim fragment is a piece of what a source SAID, so "
                    f"it needs a quoted source and not a summary")
            elif w not in q:
                elsewhere = sorted(o for o, oq in quotes.items() if oq and w in oq)
                if elsewhere:
                    fails.append(
                        f"slide {n}: the dossier declares {want!r} as verbatim from {cid}, and "
                        f"{cid}'s quote does not contain it. {', '.join(elsewhere)} does. A "
                        f"fragment filed under the wrong claim cites a source that did not say it")
                else:
                    fails.append(
                        f"slide {n}: the frame seats {want!r} as a verbatim fragment of {cid} and "
                        f"NO claim in claims.json quotes those words in that order. {cid} says "
                        f"{(by_id[cid].get('quote') or '')[:90]!r}. This is IT DID JUST THAT and "
                        f"HIGH QUALITY IMAGES, which three judges found on 2026-09-04 and no gate "
                        f"could")
            if frame and w and w not in frame:
                fails.append(
                    f"slide {n}: the dossier declares {want!r} as a verbatim fragment on this "
                    f"frame and the render does not print it. A declaration for a string nobody "
                    f"drew describes a frame the run did not make")
    return fails, declared, slides


def check_discovered(dossiers: dict, claims: list, report: dict) -> list:
    """The soft half. A list for a human, and it decides nothing. See the docstring."""
    quotes = [norm(c.get("quote") or "") for c in claims if (c.get("quote") or "").strip()]
    texts = [norm(c.get("text") or "") for c in claims if (c.get("text") or "").strip()]
    hay_quote, hay_any = quotes, quotes + texts
    everywhere = repeated_on_every_frame(report)
    notes = []

    frames = sorted(dossiers)
    if not frames:
        # A DECK WITH NO DOSSIERS STILL HAS FRAMES, and this half needs no plan at all, so it
        # reads the slide numbers off the render report rather than returning nothing. A loader
        # that silently yields nothing reports clean forever, which is what `craft_floor` shipped.
        frames = sorted({int(m.group(1)) for s in (report.get("slides") or [])
                         for m in [re.search(r"(\d+)", str(s.get("file", "")))] if m})
    for n in frames:
        nodes = slide_nodes(report, n)
        declared = {norm(w) for _cid, w in declared_verbatim(
            dossiers.get(n, ""))[0]}
        groups = {}
        for t in nodes:
            groups.setdefault(style_of(t), []).append(str(t.get("text") or "").strip())
        for _style, texts_in_slot in groups.items():
            cand = [t for t in dict.fromkeys(texts_in_slot)
                    if is_caps_label(t) and not furniture(t, everywhere)]
            anchors = [t for t in cand
                       if len(norm(t).split()) >= 2
                       and norm(t).split()[0] not in CONTINUATION
                       and any(norm(t) in q for q in hay_quote)]
            if not anchors:
                continue
            loose = [t for t in cand
                     if t not in anchors and norm(t) not in declared
                     and len(norm(t).split()) >= 2
                     and not any(norm(t) in q for q in hay_any)]
            if loose:
                notes.append(
                    f"slide {n}: {anchors[0]!r} is a literal fragment of a claim's quote, and "
                    f"{', '.join(repr(x) for x in loose)} sit(s) in the same rendered style on "
                    f"the same frame while tracing to no claim. Either they are the source's "
                    f"words and belong in this dossier's `verbatim:` block, or they are the "
                    f"deck's own labels and should not be dressed as the source's")
    return notes


# ------------------------------------------------------------------ driver

def audit(base: Path) -> dict:
    sb = base / "storyboard.md"
    cj = base / "claims.json"
    if not sb.exists() or not cj.exists():
        raise CouldNotRun(f"verbatim_check needs storyboard.md and claims.json under {base}")
    rp = base / "render" / "render_report.json"
    if not rp.exists():
        rp = base / "render_report.json"
    if not rp.exists():
        raise CouldNotRun(f"verbatim_check found no render_report.json under {base}, so there is "
                          f"no rendered frame to hold a declaration against")
    dossiers = parse_dossiers(sb.read_text(encoding="utf-8"))
    if not dossiers:
        raise CouldNotRun("verbatim_check parsed no fenced slide dossier out of storyboard.md")
    claims = json.loads(cj.read_text(encoding="utf-8")).get("claims") or []
    report = json.loads(rp.read_text(encoding="utf-8"))
    fails, declared, slides = check_declared(dossiers, claims, report)
    notes = check_discovered(dossiers, claims, report)
    return {"slides": len(dossiers), "declaring": slides, "declared": declared,
            "problems": fails, "notes": notes}


def report_lines(res: dict) -> int:
    for note in res["notes"]:
        print(f"  note  {note}")
    if res["problems"]:
        print(f"\nverbatim_check: {len(res['problems'])} declared fragment(s) the record does "
              f"not carry\n", file=sys.stderr)
        for p in res["problems"]:
            print(f"  - {p}\n", file=sys.stderr)
        print("  A verbatim slot is a promise that these are somebody else's words. Quote what "
              "the\n  source says, or move the string out of the slot and say it in the deck's "
              "own voice.", file=sys.stderr)
        return 1
    if res["declared"]:
        print(f"verbatim_check: {res['declared']} declared fragment(s) across "
              f"{len(res['declaring'])} of {res['slides']} dossier(s), every one a literal "
              f"substring of its own claim's quote and every one on its own frame. "
              f"{len(res['notes'])} slot note(s)")
    else:
        # NOT A CLEAN RUN. A deck that declares nothing was not checked, and saying "clean" here
        # would be the `checked: 0` receipt label_guard already went red over once. gate_status
        # renders this as WARN rather than PASS for the same reason.
        print(f"verbatim_check: NOT ONE of this deck's {res['slides']} dossiers declares a "
              f"`verbatim:` block, so no on-frame string was held to a quote. "
              f"knowledge/carousel/SLIDE_DOSSIER_SPEC.md says how to write one. "
              f"{len(res['notes'])} slot note(s) below are all this could look at")
    return 0


def run(base: Path) -> int:
    try:
        res = audit(base)
    except CouldNotRun as exc:
        print(f"verbatim_check: {exc}", file=sys.stderr)
        return 2
    code = report_lines(res)
    (base / "verbatim_report.json").write_text(
        json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return code


# --------------------------------------------------------------------------- self-test

def _report(nodes_by_slide: dict) -> dict:
    """A render report from `{slide_number: [(text, style_dict), ...]}`."""
    return {"slides": [
        {"file": f"slide-{n:02d}.html",
         "text_nodes": [dict(st, text=tx) for tx, st in rows]}
        for n, rows in sorted(nodes_by_slide.items())]}


PLATE = {"font_px": 25, "weight": "700", "family": "JetBrains Mono", "color": "rgb(15, 21, 19)"}
CAVITY = {"font_px": 25, "weight": "500", "family": "JetBrains Mono",
          "color": "rgb(167, 181, 174)"}
FOOT = {"font_px": 24, "weight": "500", "family": "JetBrains Mono", "color": "rgb(185, 194, 188)"}

# THE 2026-09-04 CLAIMS, the four that matter, quoted off the shipped claims.json.
CLAIMS = [
    {"id": "c7", "quote": "The image capture capabilities of pedestrians walking through the "
                          "border exit area exceeded expectations in both day and night "
                          "conditions.", "text": "Attributed to CBP's Biometrics Program Office."},
    {"id": "c9", "quote": "We were able to demonstrate NEC's SmartID Express and Neoface Express "
                          "in real-world outdoor conditions and weather, successfully capturing "
                          "high-quality facial images of thousands of pedestrians a day",
     "text": "A vendor statement in the account."},
    {"id": "c13", "quote": "As pedestrians approached the border exits, signs in English and "
                           "Spanish informed them that U.S. citizens could opt out of biometric "
                           "exit collection if they did not wish to have their picture taken",
     "text": "The account does not say what the signs said."},
    {"id": "c3", "quote": "In early 2026, S&T invited six companies to the Maryland Test "
                          "Facility (MdTF) for basic capability demonstrations to determine which "
                          "solutions should be operationally tested.", "text": "Six were shown."},
    {"id": "c30", "quote": "Before deployment, S&T built a replica of the pedestrian exit "
                           "environment at MdTF so vendors could install and assess their "
                           "prototypes before taking them to the Progreso border crossing.",
     "text": "The Maryland Test Facility built the lane first."},
]
C31 = {"id": "c31", "quote": "And it did just that.", "text": "The account's own closing line."}


def _board(slide: int, verbatim_lines: str) -> str:
    return ("```yaml\nslide: %d\njob: >\n  the hero\n%s```\n" % (slide, verbatim_lines))


def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            bad += 1

    # ---- THE NORMALISATION, in both directions, on the string that actually bit ---------
    ok("HIGH-QUALITY FACIAL matches high-quality facial images across the hyphen",
       norm("HIGH-QUALITY FACIAL") in norm(CLAIMS[1]["quote"]))
    ok("...and HIGH QUALITY IMAGES does not, because `images` is not the next word",
       norm("HIGH QUALITY IMAGES") not in norm(CLAIMS[1]["quote"]))

    # ---- 1 and 2. THE HERO FRAME'S THREE PLATES, as they shipped and as they were repaired ----
    shipped = _report({8: [("EXCEEDED EXPECTATIONS", PLATE),
                           ("HIGH QUALITY IMAGES", PLATE),
                           ("IT DID JUST THAT", PLATE),
                           ("ACCURACY RATE", CAVITY), ("IMAGES CAPTURED", CAVITY),
                           ("c18 c19 c20", FOOT), ("08 / 09", FOOT)]})
    board = _board(8, 'verbatim:\n  - c7: "EXCEEDED EXPECTATIONS"\n'
                      '  - c9: "HIGH QUALITY IMAGES"\n  - c7: "IT DID JUST THAT"\n')
    f, n, _s = check_declared(parse_dossiers(board), CLAIMS, shipped)
    ok("HIGH QUALITY IMAGES, a paraphrase in a verbatim slot, is CAUGHT",
       any("HIGH QUALITY IMAGES" in x and "NO claim" in x for x in f), str(f))
    ok("IT DID JUST THAT, in no claim quote at all, is CAUGHT",
       any("IT DID JUST THAT" in x and "NO claim" in x for x in f), str(f))
    ok("...and the one plate that IS the source's words is not reported",
       not any("EXCEEDED EXPECTATIONS" in x for x in f), str(f))
    ok("three declarations were counted rather than skipped", n == 3, str(n))

    repaired = _report({8: [("EXCEEDED EXPECTATIONS", PLATE),
                            ("HIGH-QUALITY FACIAL", PLATE),
                            ("IT DID JUST THAT", PLATE),
                            ("ACCURACY RATE", CAVITY), ("c18 c19 c20", FOOT), ("08 / 09", FOOT)]})
    rboard = _board(8, 'verbatim:\n  - c7: "EXCEEDED EXPECTATIONS"\n'
                       '  - c9: "HIGH-QUALITY FACIAL"\n  - c31: "IT DID JUST THAT"\n')
    f, _n, _s = check_declared(parse_dossiers(rboard), CLAIMS + [C31], repaired)
    ok("...and the REPAIRED plates, with the narrowing word back and c31 admitted, pass",
       not f, str(f))

    # ---- 3. FRAME 4's TWO PLACE ASSERTIONS -----------------------------------------------
    f4 = _report({4: [("MARYLAND, ROOFED", PLATE), ("PROGRESO, OPEN SKY", PLATE),
                      ("c30", FOOT), ("04 / 09", FOOT)]})
    b4 = _board(4, 'verbatim:\n  - c30: "MARYLAND, ROOFED"\n  - c30: "PROGRESO, OPEN SKY"\n')
    f, _n, _s = check_declared(parse_dossiers(b4), CLAIMS, f4)
    ok("MARYLAND, ROOFED is CAUGHT", any("MARYLAND, ROOFED" in x for x in f), str(f))
    ok("PROGRESO, OPEN SKY is CAUGHT", any("PROGRESO, OPEN SKY" in x for x in f), str(f))
    r4 = _report({4: [("MARYLAND TEST FACILITY", PLATE), ("PROGRESO BORDER CROSSING", PLATE),
                      ("c30", FOOT), ("04 / 09", FOOT)]})
    # THE FIRST DRAFT OF THIS CASE FILED BOTH REPAIRED STRINGS UNDER c30 AND THE GATE REFUSED IT,
    # correctly: c30's quote says "a replica of the pedestrian exit environment at MdTF" and never
    # spells the facility out. `Maryland Test Facility` is c3's words. That is the misattribution
    # branch firing on a fixture its own author wrote, which is the one thing GATE_LESSONS 16 says
    # a fixture usually cannot do, so it stays in the file as written rather than being smoothed.
    rb4 = _board(4, 'verbatim:\n  - c3: "MARYLAND TEST FACILITY"\n'
                    '  - c30: "PROGRESO BORDER CROSSING"\n')
    f, _n, _s = check_declared(parse_dossiers(rb4), CLAIMS, r4)
    ok("...and the repaired pair, each filed under the claim that actually quotes it, pass",
       not f, str(f))
    wrongfile = _board(4, 'verbatim:\n  - c30: "MARYLAND TEST FACILITY"\n')
    f, _n, _s = check_declared(parse_dossiers(wrongfile), CLAIMS, r4)
    ok("...while filing MARYLAND TEST FACILITY under c30, which never spells it out, is CAUGHT",
       any("c3 does" in x for x in f), str(f))

    # ---- 4. FRAME 6's SPANISH SIGN TEXT ---------------------------------------------------
    f6 = _report({6: [("CARRIL DE CAPTURA", PLATE), ("CARRIL DE EXCLUSION", PLATE),
                      ("c13 c14", FOOT), ("06 / 09", FOOT)]})
    b6 = _board(6, 'verbatim:\n  - c13: "CARRIL DE CAPTURA"\n  - c13: "CARRIL DE EXCLUSION"\n')
    f, _n, _s = check_declared(parse_dossiers(b6), CLAIMS, f6)
    ok("CARRIL DE CAPTURA is CAUGHT against a claim that never says what the signs said",
       any("CARRIL DE CAPTURA" in x for x in f), str(f))
    ok("CARRIL DE EXCLUSION is CAUGHT", any("CARRIL DE EXCLUSION" in x for x in f), str(f))

    # ---- A MISATTRIBUTION reads differently from a fabrication ---------------------------
    mis = _board(8, 'verbatim:\n  - c30: "EXCEEDED EXPECTATIONS"\n')
    f, _n, _s = check_declared(parse_dossiers(mis), CLAIMS, shipped)
    ok("a fragment filed under the wrong claim names the claim that DOES carry it",
       any("c7 does" in x for x in f), str(f))

    # ---- A DECLARATION THE FRAME NEVER PRINTED -------------------------------------------
    ghost = _board(8, 'verbatim:\n  - c7: "EXCEEDED EXPECTATIONS"\n')
    f, _n, _s = check_declared(parse_dossiers(ghost), CLAIMS,
                               _report({8: [("SOMETHING ELSE", PLATE)]}))
    ok("a declared fragment nobody drew is CAUGHT",
       any("does not print it" in x for x in f), str(f))

    # ---- AN UNKNOWN CLAIM ID -------------------------------------------------------------
    unk = _board(8, 'verbatim:\n  - c99: "EXCEEDED EXPECTATIONS"\n')
    f, _n, _s = check_declared(parse_dossiers(unk), CLAIMS, shipped)
    ok("a declaration citing a claim that does not exist is CAUGHT",
       any("no such claim" in x for x in f), str(f))

    # ---- A CLAIM WITH NO QUOTE -----------------------------------------------------------
    noq = _board(8, 'verbatim:\n  - c50: "EXCEEDED EXPECTATIONS"\n')
    f, _n, _s = check_declared(parse_dossiers(noq),
                               CLAIMS + [{"id": "c50", "text": "a summary, no quote"}], shipped)
    ok("a verbatim fragment attributed to a claim carrying no quote is CAUGHT",
       any("carries no quote" in x for x in f), str(f))

    # ---- THE ABSENT CASE AND THE EMPTY CASE ARE DIFFERENT EVENTS -------------------------
    e, present = declared_verbatim("job: >\n  nothing declared here\n")
    ok("a dossier with no verbatim key declares nothing and says so", e == [] and not present)
    e, present = declared_verbatim("job: >\n  x\nverbatim: []\n")
    ok("...and an explicit `verbatim: []` is a DECLARATION of none", e == [] and present)

    # ---- THE DISCOVERY HALF, on the frame it was written for -----------------------------
    notes = check_discovered({8: 'job: >\n  the hero\n'}, CLAIMS, shipped)
    ok("with no declaration at all, the shipped hero frame still gets a slot NOTE naming both",
       len(notes) == 1 and "HIGH QUALITY IMAGES" in notes[0] and "IT DID JUST THAT" in notes[0],
       str(notes))
    notes = check_discovered({8: 'job: >\n  the hero\n'}, CLAIMS + [C31], repaired)
    ok("...and the repaired frame gets none", not notes, str(notes))

    # A CONTINUATION IS NOT AN ANCHOR. The repaired 2026-09-04 frame 3 wraps `PARAVISION AND
    # AIFI`, and reading the tail as an anchor made two correct authored labels a finding.
    wrap = _report({3: [("AND AIFI", FOOT), ("SOLUTION 1", FOOT), ("SOLUTION 2", FOOT)]})
    conj = [{"id": "c4", "quote": "Paravision and AiFi were carried forward.", "text": ""}]
    ok("a line-wrapped tail opening on a conjunction anchors nothing",
       not check_discovered({3: "job: >\n  x\n"}, conj, wrap),
       str(check_discovered({3: "job: >\n  x\n"}, conj, wrap)))

    # THE FURNITURE IS DERIVED, NOT LISTED. The counter and the citation chip share one style.
    ok("the slide counter is furniture", furniture("08 / 09", set()))
    ok("the citation chip is furniture", furniture("c18 c19 c20 c21", set()))
    ok("the site line is furniture", furniture("texasaidocket.com", set()))
    ok("...and a real label is not", not furniture("ACCURACY RATE", set()))

    # ---- AGAINST EVERY SHIPPED DECK, because a fixture written beside a detector agrees with
    # it. This is the calibration that decided the discovery half warns rather than fails: three
    # groups across fifteen decks, and ZERO on the repaired deck this gate was written for.
    shipped_runs = sorted((REPO_ROOT / "runs" / "carousel").glob("2*"))
    checked, noisy = 0, []
    for p in shipped_runs:
        rr, cj, sb = p / "render_report.json", p / "claims.json", p / "storyboard.md"
        if not (rr.exists() and cj.exists() and sb.exists()):
            continue
        checked += 1
        rep = json.loads(rr.read_text(encoding="utf-8"))
        cl = json.loads(cj.read_text(encoding="utf-8")).get("claims") or []
        ds = parse_dossiers(sb.read_text(encoding="utf-8"))
        ns = check_discovered(ds, cl, rep)
        if ns:
            noisy.append((p.name, len(ns)))
        fs, _d, _sl = check_declared(ds, cl, rep)
        ok(f"{p.name}: no shipped deck fails the declared half", not fs, str(fs))
    ok("the calibration read a real corpus rather than nothing", checked >= 10, str(checked))
    print(f"       discovery notes across {checked} shipped deck(s): "
          f"{noisy if noisy else 'none'}")
    newest = next((p.name for p in reversed(shipped_runs)
                   if (p / "render_report.json").exists()), None)
    ok(f"the newest shipped deck ({newest}) draws NO discovery note, so this gate does not fire "
       f"on a repaired deck", newest not in dict(noisy), str(noisy))

    # THIS GATE HAS NO SOFTENING FLAG. Built from parts so the needle does not match itself.
    src = Path(__file__).read_text(encoding="utf-8")
    dash = "-" * 2
    ok("no flag on this gate can soften it",
       not any(dash + f in src for f in ("allow-", "skip", "force", "warn-only")))
    ok("argparse prefix matching is off, so a neighbour gate's flag is an error",
       "allow_abbrev=False" in src)

    print("\nverbatim_check self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    # allow_abbrev=False, because `sources_block` silently accepted `--run` as a prefix of
    # `--run-dir`, read an empty directory and printed `clean` every time it was asked.
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0], allow_abbrev=False)
    ap.add_argument("--date", help="a working run under out/<date>/")
    ap.add_argument("--run", help="a shipped run under runs/carousel/<date>/")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.date:
        base = REPO_ROOT / "out" / a.date
    elif a.run:
        base = REPO_ROOT / "runs" / "carousel" / a.run
    else:
        ap.error("--date, --run or --self-test")
    if not base.is_dir():
        print(f"verbatim_check: no such run directory: {base}", file=sys.stderr)
        return 2
    return run(base)


if __name__ == "__main__":
    raise SystemExit(main())
