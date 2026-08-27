#!/usr/bin/env python3
"""compute.py — every figure the 2026-08-27 deck prints that is not quoted from a source.

THE LAW THIS FILE EXISTS FOR. No numeral on a slide is typed by a person or a model. A figure is
either quoted verbatim from a claim in claims.json, or it is computed here from ledger/docket.json
and declared in aggregates.json. Nothing else reaches a frame.

Run it, read it, and put its output on the slides. Never the other way round.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REC  = json.loads((ROOT / "ledger" / "docket.json").read_text())["items"]

# ---------------------------------------------------------------- THE SET, named on the frame
# "An item on the record where a Texas city or county is the decider and the record names a tax
# break or a land rule over a data centre or a large load." The membership test is stated here
# rather than eyeballed, so the count is reproducible and the frame can name what it counted.
#
# THE GLOSS SAID SOMETHING THE TEST DOES NOT MEASURE, and that is what `_gloss_holds` is for.
# Round two's integrity judge refuted the first gloss, "Texas cities and counties asked for a tax
# break or a land rule", against this run's own record. The test below reads WORDS in the item, so
# it admits an item whichever direction the request ran, and half the set runs the other way:
# tx-2026-0033 eliminates El Paso's own incentives, tx-2026-0050 has Corpus Christi directing
# staff to prohibit them, tx-2026-0062 is Fort Worth opening its own moratorium, and
# tx-2026-0037's record says neither the city nor Webb County had received an application at all.
# A computed set may only be narrated by its own membership test. A gloss that adds an actor, a
# direction or a motive the test never looked at is a fabrication wearing a count's authority,
# and the count being right is exactly what makes it convincing.
LOCAL   = {"county", "city"}
ASK     = re.compile(r"tax abatement|reinvestment zone|abatement agreement|chapter 312"
                     r"|moratorium|incentive|economic development agreement", re.I)
SUBJECT = re.compile(r"data cent(?:er|re)|server farm|large load|hyperscale", re.I)

def reader_text(it):
    """Only what a reader is shown. Claims quotes are the source's words, not the record's."""
    parts = [it.get("title", ""), it.get("summary", "")]
    parts.append((it.get("public_access") or {}).get("how", ""))
    parts += [h.get("note", "") for h in it.get("history", [])]
    return " ".join(parts)



# ---------------------------------------------------------------- the shape map
# WHAT A BODY DID, per item, and the claim whose own words prove it. `label_guard.py`
# reads this map and refuses any label beside a claim id that says a shape the claim
# does not carry. It guards itself below.
#
# Five entries, not thirteen, and the shortfall is stated rather than hidden. Only five
# of the thirteen items a1 counts have a claim in THIS run's claims.json, because the
# other eight were verified into the record on earlier runs and this deck did not
# re-fetch them. A shape with no claim behind it is not a shape this map may hold, so
# it is left out and the frame prints no shape word for it either. Frame 4 prints item
# ids and county names only, which is the reason it can carry all thirteen honestly.
ACTED = {
    "tx-2026-0043": ("Archer", "VOTED", "c11"),
    "tx-2026-0051": ("Brazoria", "MOTION DENY", "c13"),
    "tx-2026-0088": ("Brazos", "IMPROVEMENTS", "c15"),
    "tx-2026-0087": ("Denton", "APPROVAL MORATORIUM", "c17"),
    "tx-2026-0027": ("Taylor", "CONSIDER", "c18"),
}

_STEM = {"voted": "vote", "motion": "motion", "deny": "deny",
         "improvements": "improvement", "approval": "approv",
         "moratorium": "moratorium", "consider": "consider"}


def _shapes_hold() -> None:
    """Every shape word in ACTED occurs, by stem, in the claim named as proving it.

    The map guarding itself. A shape word its own claim does not carry is a shape the
    deck may not print.
    """
    claims = json.loads((Path(__file__).parent / "claims.json").read_text())["claims"]
    by_id = {c["id"]: c for c in claims}
    for item, (place, shape, cid) in ACTED.items():
        hay = (by_id[cid]["quote"] + " " + by_id[cid].get("text", "")).lower()
        missing = [w for w in shape.lower().split() if _STEM.get(w, w) not in hay]
        assert not missing, (
            f"{item}: shape {shape!r} names {missing} and {cid} carries neither. "
            f"{cid} says {by_id[cid]['quote'][:90]!r}")


_shapes_hold()


# The words the membership test never looks at. Each names a DIRECTION of a request, and the
# test reads only whether the record's own copy names a tax break or a land rule over a data
# centre, plus who the decider is. A gloss carrying any of these narrates a property no code
# here computed, which is the round-two hard fail this guard exists to make unrepeatable.
DIRECTION = ("ask", "asks", "asked", "asking", "sought", "seeks", "seeking", "request",
             "requests", "requested", "applied", "applies", "applying", "wanted", "wants",
             "lobbied", "petitioned")

# The phrasings that smuggle a direction in without using a direction verb. "Run the other way"
# is the one that shipped, and it is here because a word list of verbs did not catch it.
#
# RELATION is the third thing the set may not assert and the one that cost round five.
# The test finds an ask word and a subject word ANYWHERE in an item's record. It does not
# test that one is ABOUT the other, so "a tax break or a land rule OVER a data center" and
# "each CARRIES a tax break" are both relations no code here computed. tx-2026-0052 is the
# proof: it is a county resolution that is explicitly not a rule and seeks no tax break, and
# it is in the set because its summary's last sentence mentions a reinvestment zone the same
# court refused on a DIFFERENT matter. The count is right. The relation was invented.
IDIOM = ("the other way", "in reverse", "conversely", "the opposite direction")
RELATION = ("over a data", "over a large", "carries a tax", "carries a land",
            "attached to", "behind a data", "for a data cent")


def _gloss_holds(gloss: str) -> str:
    """The frame's name for the set may not add a direction the membership test never tested.

    IDIOM IS TESTED HERE TOO, and it was not until round four pointed out that the idiom list
    had been added to `_surfaces_hold` and not to this one. The phrase that shipped in round
    three would still have passed the older of the two guards. That is this run's whole
    recurring shape happening inside the very pair of functions written to stop it: a repair
    applied to one surface and not its twin, twice, in the same file.
    """
    bad = [w for w in DIRECTION if re.search(rf"\b{w}\b", gloss, re.I)]
    bad += [w for w in IDIOM if w in gloss.lower()]
    bad += [w for w in RELATION if w in gloss.lower()]
    assert not bad, (
        f"set_named_on_frame says {bad} and the membership test never tests who asked whom. "
        f"Name what the test reads, or change the test. Gloss was {gloss!r}")
    return gloss


# ------------------------------------------------------- THE GUARD, POINTED AT WHAT SHIPS
#
# ROUND THREE FAILED ON THE SURFACE ROUND TWO'S FIX DID NOT REACH, and that is the lesson,
# not the sentence. Round two rewrote frame 4's dek and added `_gloss_holds` above, and the
# guard inspected a STRING LITERAL INSIDE THIS FILE. The identical refuted claim went on
# standing in caption.txt paragraph 3, "Thirteen items on this record run the other way",
# where a reader actually meets it, and the integrity judge refused the deck for it.
#
# The judge's own words for the shape: each repair "was applied to one surface and not its
# twin". A guard that reads a literal no reader sees will pass forever while the claim ships.
# So this one reads the PUBLISHED surfaces, caption.txt and copy.json, and it fails the build.
#
# WHAT IT CANNOT DO, said plainly rather than left to be discovered. It matches words, so it
# catches "asked" and it catches "the other way" because that one is written down now. It
# cannot catch the next phrasing that implies a direction without naming one. That is what the
# panel is for, and it is why a green suite is never the same as a correct product.
def _surfaces_hold() -> None:
    here = Path(__file__).parent
    surfaces = {"caption.txt": (here / "caption.txt").read_text()}
    copy = json.loads((here / "copy.json").read_text())["slides"]
    for n, sl in copy.items():
        surfaces[f"copy.json slide {n}"] = " ".join(
            v for k, v in sl.items() if isinstance(v, str))

    # Only sentences that are ABOUT the counted set. The deck says "Amazon asked for no
    # economic incentives" on frame 5 and that is c6's verbatim quote about one company,
    # not a claim about these thirteen.
    # WHAT COUNTS AS A SENTENCE ABOUT THE SET. This read only "thirteen" and "twelve count",
    # so "Each carries a tax break or a land rule over a data center or a large load." and
    # "A Texas city or county is the decider on all of them." were both invisible to it, and
    # both are assertions about these thirteen items. Round four found the gap: the guard had
    # reached the right SURFACE and still not the whole sentence set on it. A sentence that
    # names the set's defining property is about the set whether or not it says the number.
    # ROUND SIX FOUND THE REPAIR PHRASED INTO THIS REGEX'S BLIND SPOT, which is the sharpest
    # single finding of the run. The list read "each names" and "each carries". The sentence the
    # round-five repair produced is "Each RECORD names", on frame 4 and again in caption.txt, and
    # it matched neither. A guard written specifically to read the published surfaces had gone
    # blind to the exact sentence the repair wrote, and it went blind by accident, which is worse
    # than going blind by design. An enumerated word list is a guess about phrasing.
    ABOUT = re.compile(
        r"thirteen|twelve count|all of them|every one of them|these items|the counted set"
        r"|each\b[^.]{0,24}\b(?:names|carries|holds|has|carry)", re.I)
    bad = []
    for where, text in surfaces.items():
        for sent in re.split(r"(?<=[.?!])\s+", text):
            if not ABOUT.search(sent):
                continue
            hits = [w for w in DIRECTION if re.search(rf"\b{w}\b", sent, re.I)]
            hits += [w for w in IDIOM if w in sent.lower()]
            hits += [w for w in RELATION if w in sent.lower()]
            if hits:
                bad.append(f"{where}: {hits} in {sent.strip()!r}")
    assert not bad, (
        "a published surface tells a story about the counted set that the membership test "
        "never tested:\n  " + "\n  ".join(bad) +
        "\nThe set is admitted by WORDS IN THE RECORD, whichever direction the request ran. "
        "Say what the test reads, on every surface that says anything about it.")


members = []
for it in REC:
    if (it.get("decider") or {}).get("type") not in LOCAL:
        continue
    t = reader_text(it)
    if ASK.search(t) and SUBJECT.search(t):
        members.append(it)

members.sort(key=lambda i: i["id"])

# WHY EACH MEMBER IS IN, recorded per item so the set can be audited rather than trusted.
#
# Round five asked for exactly this and it is the cheapest useful thing in the file. For every
# member it keeps the ask word, the subject word, and WHICH FIELD each was found in. Read the
# output and the crudeness of the test is visible without reading the test: tx-2026-0052's ask
# word is in its summary and its subject word is in its title, and the summary sentence carrying
# it is about a matter the same court refused on a DIFFERENT item. tx-2026-0028's ask word sits
# in a sentence comparing it to other counties' votes.
#
# The count is not changed here and the frame does not narrate a relation, so nothing published
# rests on the difference. WHAT IT MEANS is written down in the run record: this test finds two
# words anywhere in a record and calls that a set, which lets an item in on a backward reference
# and would drop tx-2026-0046, a real tax abatement for a data centre campus, under any stricter
# reading that demanded the two words share a sentence. Both directions are wrong and fixing it
# is a design change, not a repair.
def _where(it, rx):
    for field in ("title", "summary"):
        m = rx.search(it.get(field, "") or "")
        if m:
            return {"field": field, "matched": m.group(0)}
    for i, h in enumerate(it.get("history") or []):
        m = rx.search(h.get("note", "") or "")
        if m:
            return {"field": f"history[{i}].note", "matched": m.group(0)}
    m = rx.search((it.get("public_access") or {}).get("how", "") or "")
    return {"field": "public_access.how", "matched": m.group(0)} if m else None


evidence = [{"id": it["id"], "ask": _where(it, ASK), "subject": _where(it, SUBJECT),
             "same_sentence": any(ASK.search(sent) and SUBJECT.search(sent)
                                  for f in ("title", "summary")
                                  for sent in re.split(r"(?<=[.?!])\s+", it.get(f, "") or ""))}
            for it in members]

# The counties those items sit in, deduplicated. A county with two items counts once.
counties = sorted({c for it in members for c in (it.get("geography") or {}).get("counties", [])})

# THE JOIN, one row per item, read off that item's own geography.
#
# THIS EXISTS BECAUSE THE FIRST BUILD OF FRAME 4 DID NOT HAVE IT. The frame printed the
# thirteen ids beside the twelve deduplicated county names, each list sorted on its own
# key, and a reader met a ruled two column table asserting twelve id-to-county pairings
# that no code had produced. Four were false against this run's own claims and the
# thirteenth row orphaned, because thirteen items do not sit beside twelve counties.
# A table is a claim about a JOIN, and a join is computed or it is not printed.
pairs = []
for it in members:
    cs = (it.get("geography") or {}).get("counties") or []
    if cs:
        where = ", ".join(cs) if len(cs) <= 2 else cs[0] + " and " + str(len(cs) - 1) + " more"
    elif (it.get("geography") or {}).get("statewide"):
        where = "statewide"
    else:
        where = "no county on the record"
    pairs.append({"id": it["id"], "where": where, "n_counties": len(cs)})

# The Amazon item, which is the deck's subject and is NOT in the set above.
AMZ = next(i for i in REC if i["id"] == "tx-2026-0084")
amz_in_set = AMZ["id"] in {i["id"] for i in members}

out = {
    "set_definition": ("items on the record whose decider is a Texas city or county, whose reader "
                       "copy names a tax abatement, a reinvestment zone, a moratorium or an "
                       "incentive, and whose subject is a data centre or a large load"),
    "set_named_on_frame": _gloss_holds(
        "items where a Texas city or county is the decider and the record names a data center "
        "or a large load beside a tax break, a moratorium or an incentive"),
    "record_items_total": len(REC),
    "ask_items": len(members),
    "ask_item_ids": [i["id"] for i in members],
    "ask_counties": counties,
    "ask_pairs": pairs,
    "ask_evidence": evidence,
    "ask_members_with_both_words_in_one_sentence": sum(1 for e in evidence if e["same_sentence"]),
    "ask_counties_count": len(counties),
    "amazon_item_in_set": amz_in_set,
    # Frame 6 turns on this pair and neither half is eyeballed. The thirteen have a city or a
    # county deciding, because that is clause one of the membership test. This one does not,
    # because the record names the decider, and the record also states the room it opens.
    "amazon_decider_type": (AMZ.get("decider") or {}).get("type"),
    "amazon_decider_is_local": (AMZ.get("decider") or {}).get("type") in LOCAL,
    "amazon_public_access_room": AMZ["public_access"]["room"],
    "amazon_key_date_count": len(AMZ["key_dates"]),
    "read_from": "ledger/docket.json",
    "read_on": "2026-08-27",
}

def _declarations_hold() -> None:
    """Every declaration in quantifiers.json names a phrase its own surface actually prints.

    THE CHECK RUNS THE OTHER WAY ROUND, and that is the whole point of adding it. `quantifier_check`
    already proves every universal a surface PRINTS is declared. Nothing proved the reverse, so
    when the round-five repair rewrote frame 4's dek, quantifiers.json went on declaring the
    refuted sentence as the membership test and gained no entry for the sentence that replaced it.
    Round six found the deck's own verification ledger describing a deck that did not ship, which
    is the fault artwork.json's 2026-08-19 entry calls corrosive, in the file whose entire job is
    saying what every universal ranges over.

    A stale declaration is not a harmless leftover. It is a sentence this project has written down
    as checked, about copy no reader will ever see, sitting beside the copy they will.
    """
    here = Path(__file__).parent
    surfaces = {"caption.txt": (here / "caption.txt").read_text()}
    copy = json.loads((here / "copy.json").read_text())["slides"]
    for key, sl in copy.items():
        n = int(key[1:]) if key.startswith("S") else int(key)
        surfaces[f"slide-{n:02d}.html"] = " ".join(
            v for v in sl.values() if isinstance(v, str))
    decls = json.loads((here / "quantifiers.json").read_text())["quantifiers"]
    stale = []
    for d in decls:
        where = d.get("where", "")
        if where not in surfaces:          # first_comment.txt and any surface not in copy.json
            continue
        if d["phrase"].strip().rstrip(".").lower() not in surfaces[where].lower():
            stale.append(f"{where} does not print {d['phrase'][:64]!r}")
    assert not stale, (
        "quantifiers.json declares a universal its own surface no longer prints:\n  "
        + "\n  ".join(stale) +
        "\nA declaration left behind by a repair is a checked sentence about copy nobody reads.")


# Last, because they read copy.json, caption.txt and quantifiers.json, which are written after
# the figures are.
_surfaces_hold()
_declarations_hold()
print(json.dumps(out, indent=2))
