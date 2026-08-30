#!/usr/bin/env python3
"""Every numeral this deck prints, asserted out of claims.json and nowhere else.

The law is in CLAUDE.md. No numeral on a frame is typed by a person or produced by a model. A
figure reaches a slide as a string this file proved was already in a source's own words, or it
does not reach a slide.

WHAT IS DANGEROUS ON THIS DECK IS NOT ARITHMETIC. IT IS SUBTRACTION THE READER DOES.

Three pairs on this story look like they want to be related, and not one of them may be:

  $81 million raised  against  $50.8 million granted   -> a remainder
  459 organizations   against  28 cameras              -> a part and a whole
  62,000 searches     against  about 1,660 cases       -> a hit rate

Every one of those would be a fresh factual assertion in the largest type on the page, about a
relationship no source states. So this file emits NO derived figure at all. It only proves that
each string it hands the slides is already present, character for character, inside the verbatim
quote of the claim that carries it.

`$81 million` is deliberately absent from the output. It is quotable from c16 and it is the one
figure whose presence beside $50.8 million would invite the subtraction. The omission is a
decision, recorded here so a later pass does not add it back as a helpful detail.

    python3 out/2026-08-30/compute.py
"""
import json
import pathlib
import sys

RUN = pathlib.Path(__file__).resolve().parent
CLAIMS = json.loads((RUN / "claims.json").read_text(encoding="utf-8"))["claims"]
BY = {c["id"]: c for c in CLAIMS}


def quoted(cid: str, needle: str) -> str:
    """Return the string only if it is really inside that claim's verbatim quote."""
    q = BY[cid]["quote"]
    if needle not in q:
        sys.exit(f"compute: {needle!r} is not in claim {cid}'s quote. Refusing to invent it.")
    return needle


# Each entry is (slide, claim, the exact substring the frame prints, what set it counts).
# The set line is not decoration. Instinct `count-names-its-set` says a bare count over a partly
# quoted index asserts a number nothing checked, so every count here carries the words the frame
# must print beside it.
FIGURES = [
    (1, "c20", "28", "cameras in the city contract"),
    (3, "c21", "459", "outside organizations that ran searches including this network"),
    (3, "c21", "nearly 1.6 million", "searches that included Pflugerville's camera network"),
    (3, "c21", "the last six months", "the window the city pulled records for"),
    (4, "c13", "2023", "the year the Legislature passed it"),
    (4, "c13", "$1", "added to auto insurance costs for Texans"),
    (4, "c16", "$50.8 million", "of the fee funnelled into grants"),
    (4, "c16", "234", "grants made by the authority"),
    (5, "c14", "at least $30 million", "of the fee devoted to the network"),
    (5, "c15", "at least 3,200", "Flock cameras the fee has been turned into"),
    (6, "c18", "62,000", "searches of license plate reader data in 2025"),
    (6, "c18", "about 1,660", "cleared catalytic converter theft cases"),
    (6, "c18", "2025", "the year the authority reported on"),
    (7, "c17", "$15.9 million", "the contract with the Department of Public Safety"),
    (7, "c17", "1,183", "cameras the contract installs"),
    (7, "c17", "three-year", "the contract term, set as words on the frame"),
    (7, "c17", "2025", "the year the contract was signed"),
    (9, "c40", "October 13, 2026", "the next board meeting the department's page lists"),
]

# The three relationships this deck refuses to publish, named so the refusal is auditable.
REFUSED = [
    {"pair": ["$81 million (c16)", "$50.8 million (c16)"],
     "why": "a remainder no source states. $81 million is on no frame in this deck."},
    {"pair": ["459 (c21)", "28 (c20)"],
     "why": "a part and a whole. They count different things and they are on different frames, "
            "with nothing drawn between them anywhere in the deck."},
    {"pair": ["62,000 (c18)", "about 1,660 (c18)"],
     "why": "a hit rate. Both are printed on slide 6 and a drawn control joint separates them, "
            "with no shared axis, baseline or unit."},
]

# ---------------------------------------------------------------------------------------------
# THE SHAPE MAP. `label_guard` reads this, and it exists because a label beside a drawn mark is a
# CLAIM ABOUT WHAT THAT MARK IS. Two marks are placed on this deck, both on slide 5's Albers
# outline, and both are named ends of the span c14 states verbatim. Nothing else in this deck is
# placed anywhere, which is the whole point of that frame's printed refusal.
#
# The key is the mark's own id, then the place, then the SHAPE WORDS a label beside it may use,
# then the claim that proves it.
ACTED = {
    "tx-48-141": ("EL PASO",             "EL PASO",             "c14"),
    "tx-48-361": ("THE LOUISIANA BORDER", "LOUISIANA BORDER",   "c14"),
}

# The stem table, so a label may inflect a word the claim uses without the gate firing on the
# inflection. It is read by brace matching rather than by a line regex, so it closes here.
_STEM = {"BORDERS": "BORDER", "CAMERAS": "CAMERA", "PLACED": "PLACE", "PLACING": "PLACE",
         "DEVOTED": "DEVOTE", "SEARCHES": "SEARCH", "SEARCHED": "SEARCH", "GRANTS": "GRANT",
         "CLEARED": "CLEAR", "COVERED": "COVER", "VOTED": "VOTE", "PAUSED": "PAUSE",
         "INSTALLS": "INSTALL", "LISTS": "LIST", "LISTED": "LIST", "READS": "READ"}

for _mid, (_place, _shape, _cid) in ACTED.items():
    _q = (BY[_cid].get("quote", "") + " " + BY[_cid].get("text", "")).upper()
    for _w in _shape.split():
        assert _w in _q or _STEM.get(_w, _w) in _q, (
            f"{_mid}: the shape word {_w!r} is in no part of {_cid}'s own words")

out = {"run": "2026-08-30", "figures": [], "refused": REFUSED}
for slide, cid, s, names in FIGURES:
    out["figures"].append({
        "slide": slide, "claim": cid, "string": quoted(cid, s), "names_the_set": names,
        "source_url": BY[cid]["url"],
    })

# Nothing here is computed, so there is nothing to round and no unit to convert. Assert that,
# rather than leaving it to be assumed by whoever reads the output next.
# THE RUN'S OWN COUNTS. The article page prints how many claims were verified, and that numeral
# is COMPUTED by this run rather than quoted from any source, so it has to be computed HERE and
# not by the page that prints it. numeral_lint refused the build until it was, which is the law
# working: a figure a reader sees traces to a computation or it does not publish.
out["counts"] = {
    "claims_verified": len(CLAIMS),
    "figures_proved": len(out["figures"]),
    "relationships_refused": len(REFUSED),
}

out["derived_figures"] = []
out["note"] = ("No figure in this deck is derived. Every string above was proved present in its "
               "claim's own verbatim quote before it reached a frame.")

(RUN / "computed.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
print(f"compute: {len(out['figures'])} figure(s) proved against their claims, "
      f"0 derived, {len(REFUSED)} relationship(s) refused by name")
