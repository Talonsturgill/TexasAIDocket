#!/usr/bin/env python3
"""Every label a frame prints beside a claim id has to be words that claim says.

THE DEFECT THIS EXISTS FOR (2026-08-25, round 12, a scoring hard fail).

`compute.py` guards its own shape map hard. Every entry in ACTED is a place, a shape and the
claim whose own words prove the shape, and an assertion refuses any shape word that appears in
neither that claim's quote nor its text. It caught "moratorium declined" on Laredo and
"disclosure asked" on Lubbock. It is one of the strongest guards in this pipeline.

And frame 3 printed BRAZORIA / CONDITIONS SET / C40.

The guard runs over the MAP. The reader reads the FRAME. Nothing stood between them, so a frame
that reworded `resolution adopted` into its own vocabulary slipped a guard that had already done
its job correctly. Three more were live in the same deck on frame 6: ZONING for
`conditional use only`, SEWER for `discharge regulated`, INELIGIBLE for `made ineligible`.

This closes that gap by running the SAME test on the shipped HTML. For every claim id printed on
a frame, it takes the capitalised words immediately before it, drops the ones that are place
names or connective furniture, and requires each of the rest to appear in that claim's own quote
or text, stemmed exactly the way compute.py stems them.

Run it by EXIT CODE. 0 clean, 1 a label the record does not support, 2 could not run.
"""
from __future__ import annotations
import ast, html as _html, json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Words a label may carry that are not claims about what a body did: connectives, the deck's own
# furniture, and the generic half of a body's name. Kept short on purpose. Anything that is not
# here and not a place name has to be in the claim.
FURNITURE = {
    "AND", "OR", "THE", "A", "AN", "OF", "IN", "ON", "AT", "TO", "FOR", "BY", "WITH", "FROM",
    "COUNTY", "CITY", "COMMISSION", "COURT", "COUNCIL", "TX", "SAYS", "SAY", "NEITHER",
}
WORD = re.compile(r"[A-Z][A-Z0-9'-]{1,}")
# CASE INSENSITIVE SINCE 2026-09-02, AND THAT IS NOT A TIDY UP.
#
# This matched an uppercase C only. Deck 13 sets every citation in lowercase, `c8 c9 c12 c14`,
# which is how the copywriter writes them and how nine of nine frames rendered them. So the loop
# below examined NO labels on that deck, the receipt recorded `checked: 0` with no problems, and
# gate_status rendered a zero-count receipt as a PASS. An unsupported institution name beside a
# lowercase id could have shipped through a gate that says in its own docstring it exists to stop
# exactly that.
#
# GATE_LESSONS' oldest shape, again: a checker wired to nothing, passing. Found by a review bot on
# the pull request, not by the gate's own self-test, because the self-test used uppercase.
CLAIM_TOKEN = re.compile(r"\bC(\d{1,3})\b", re.I)
WINDOW = 6          # capitalised words before an id that count as its label
STRIP = ".,\"'()"   # ONE strip set. Two of them disagreeing crashed this gate twice

# WHERE PLACE NAMES COME FROM, and it is the record rather than the deck.
#
# `places` is the set of label words that are NOT claims about what a body did, because a county
# name beside a claim id names where, not what. It used to be derived from the deck's own `ACTED`
# map, which meant a deck without one had an EMPTY place set, and every county it printed would
# have been read as an unsupported label. That is the false-positive failure this file already
# refuses to have, and it is the other half of why the gate bailed instead of running.
#
# Whether a word is a Texas place is a fact about Texas, so it is read from the gazetteer the
# rest of this project already computes places from, 336 counties and places with their aliases.
# The deck's own map is still unioned in, because a map may name a body the gazetteer does not.
PLACES_FILE = REPO_ROOT / "assets" / "geo" / "tx-places.json"

# THE STEM FLOOR, and why this gate owns it rather than borrowing it from a deck.
#
# `stems` maps a label word to the stem that must appear in the claim, so ESTABLISHED passes
# against a claim that says "establishes". It was read ONLY from the deck's own `_STEM` table,
# which two separate things wrong with it:
#
#   1. A deck with no shape map has no `_STEM` either, so the gate stopped rather than run. That
#      is eight of fifteen published decks.
#   2. Six decks DO define one and three of those wrote the keys in UPPER CASE, while the lookup
#      is `stems.get(w.lower())`. Those three tables matched nothing and the decks were checked
#      with no stemming at all, silently, which is the false-positive mode this file refuses to
#      have. `_guarded` lower cases both halves now, so an existing table starts working.
#
# This floor is the union of every stem the six decks proved, lower cased. A deck's own table is
# still read and still WINS, so nothing here overrides a run that knows better. It is a floor
# under a gate that was otherwise refusing to run, not a replacement for the deck's judgement.
DEFAULT_STEMS = {
    "abatement": "abatement", "action": "action", "added": "add", "adopted": "adopt",
    "agreement": "agreement", "approval": "approv", "approved": "approv", "asked": "ask",
    "booked": "book", "borders": "border", "cameras": "camera", "canceled": "cancel",
    "cancellation": "cancel", "cancelled": "cancel", "capped": "cap", "cleared": "clear",
    "conditional": "conditional", "consider": "consider", "cooling": "cooling",
    "cooperative": "cooperativ", "covered": "cover", "denied": "den", "deny": "deny",
    "devoted": "devote", "directed": "direct", "discharge": "discharg", "disclosure": "disclos",
    "established": "establish", "fill": "fill", "framework": "framework", "gathered": "gather",
    "grants": "grant", "hearings": "hearing", "improvements": "improvement",
    "ineligible": "ineligible", "initiated": "initiat", "installs": "install", "listed": "list",
    "lists": "list", "made": "mak", "meetings": "meeting", "moratorium": "moratorium",
    "motion": "motion", "no": "no", "not": "not", "only": "only", "orders": "order",
    "ordinance": "ordinance", "passed": "pass", "paused": "pause", "permit": "permit",
    "petition": "petition", "placed": "place", "placing": "place", "process": "process",
    "pursued": "pursu", "reads": "read", "regulated": "regulat", "request": "request",
    "resolution": "resolution", "review": "review", "says": "say", "searched": "search",
    "searches": "search", "staff": "staff", "taken": "taken", "turns": "turn", "use": "use",
    "voted": "vote", "water": "water", "zone": "zone",
}


class Absent(Exception):
    """No published surface to check. Exit 2, which this file's contract calls could not run."""


def _copy_strings(blk) -> list:
    """Every published string in a slide's copy block, whatever the deck named its fields.

    THE FIELD NAMES ARE BESPOKE PER DECK and this gate used to read only `strings`. Measured
    across fourteen shipped decks on 2026-09-03, `strings` appears in exactly ONE, the deck this
    gate was written against. The rest use `hook`, `dek`, `labels`, `kicker`, `lines`, `s1` and
    others, so the gate read nothing on thirteen of fourteen and reported them checked.

    So nothing is named. Every string under the block is published copy, except `claims`, which
    is the id list rather than something a reader sees.
    """
    out = []

    def walk(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            for x in v:
                walk(x)
        elif isinstance(v, dict):
            for k, x in v.items():
                if str(k).lower() != "claims":
                    walk(x)

    walk(blk)
    return out


def _gazetteer_places() -> set:
    """Every Texas place name, upper cased, word by word, from the canonical record."""
    out = set()
    try:
        rows = json.loads(PLACES_FILE.read_text(encoding="utf-8")).get("places") or []
    except (OSError, ValueError):
        return out
    for r in rows:
        for field in (r.get("name"), r.get("full_name")):
            for w in WORD.findall((field or "").upper()):
                out.add(w)
        for a in (r.get("aliases") or []):
            for w in WORD.findall(str(a).upper()):
                out.add(w)
    return out


def _guarded(compute_src: str):
    """The place names, the proof claim to shape map, and the stem table, out of compute.py."""
    places, stems, shapes = set(), {}, {}
    for m in re.finditer(r'"(tx-[\d-]+)":\s*\("([^"]+)",\s*"([^"]+)",\s*"(c\d+)"', compute_src):
        for w in WORD.findall(m.group(2).upper()):
            places.add(w)
        # the claim that PROVES this shape. A label beside it may say the shape and nothing else.
        shapes.setdefault(m.group(4).lower(), set(m.group(3).upper().split()))
    # BRACE MATCHED, NOT REGEXED. The first version looked for `_STEM = {...\n}` and the real
    # dict closes on the same line as its last entry, so it matched nothing, every stem fell back
    # to the literal word, and the gate fired on ESTABLISHED against a claim that says
    # "establishes". A gate that fails correct work is worse than no gate, so this parse is
    # asserted below rather than allowed to fall back quietly.
    i = compute_src.find("_STEM = {")
    if i >= 0:
        j, depth = compute_src.index("{", i), 0
        for k in range(j, len(compute_src)):
            depth += (compute_src[k] == "{") - (compute_src[k] == "}")
            if depth == 0:
                body = re.sub(r"#[^\n]*", "", compute_src[j:k + 1])
                try:
                    raw = ast.literal_eval(body)
                    # LOWER CASED BOTH HALVES. The lookup is stems.get(w.lower()), so an
                    # UPPER CASE table matched nothing and its deck was checked unstemmed.
                    stems = {str(k).lower(): str(v).lower() for k, v in raw.items()}
                except (ValueError, SyntaxError, AttributeError):
                    stems = {}
                break
    return places, stems, shapes


def _flat_for_count(html: str) -> str:
    """Visible text only, for counting how many claim ids the gate actually looked at."""
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))


def _elements(html: str):
    """Each element's own visible text, in document order.

    The window walks ELEMENTS, not a flattened string. Flattening ran frame 6's three route
    slips together, so the label for C43 picked up ONLY from the slip before it and the gate
    fired on a word that belonged to a different claim. An element boundary is the real one.
    """
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S | re.I)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    # ENTITIES ARE DECODED BEFORE SPLITTING. `CONTRACT &nbsp;c20` split into one token
    # `&nbsp;c20`, which the id matcher rejected, and the gate died with a traceback on two
    # published decks. A non breaking space is a space to a reader, so it is one here.
    html = _html.unescape(html).replace("\u00a0", " ")
    out = []
    for chunk in re.split(r"<[^>]+>", html):
        t = re.sub(r"[ \t]+", " ", chunk).strip()
        for line in t.split("\n"):
            if line.strip():
                out.append(line.strip())
    return out


def check(run_dir: Path):
    problems = []
    compute = run_dir / "compute.py"
    claims_f = run_dir / "claims.json"
    if not compute.exists() or not claims_f.exists():
        return ["label_guard needs compute.py and claims.json in the run directory"]
    src = compute.read_text(encoding="utf-8")
    places, stems, shapes = _guarded(src)

    # A DECK WITH NO SHAPE MAP IS THE ORDINARY CASE, NOT A MISREAD FILE, and treating it as one
    # meant this gate had never run against most of what this project has published. Measured on
    # 2026-09-03 across fifteen shipped decks: eight carry no `ACTED` map at all, because a deck
    # about one supercomputer or one docket has no bodies to label with a shape. The gate read
    # `places` empty, concluded it was pointed at the wrong file, and returned that as its only
    # finding. Nobody saw it, because nothing ran it.
    #
    # THE DISCRIMINATOR IS THE `ACTED` TOKEN rather than the parse result. A deck that declares
    # the map and yields no entries IS a misread and still stops here, which is the case the
    # original bail was written for. A deck that never declares one has nothing to parse, so
    # `shapes` is empty, the shape test below simply does not bite, and the LABEL WORD test still
    # runs, which is the half that applies to every deck.
    if "ACTED" in src and not shapes:
        return ["label_guard found an ACTED map in compute.py and parsed no entries out of it, "
                "so it is reading the file wrongly rather than reading the wrong file"]

    places |= _gazetteer_places()
    # The deck's own table WINS. This is a floor under a gate that was otherwise refusing to run.
    stems = {**DEFAULT_STEMS, **(stems or {})}
    if "_STEM = {" in src and not _guarded(src)[1]:
        return ["label_guard found a _STEM table in compute.py and parsed nothing out of it, so "
                "the deck's own stemming is not in force. That is the one failure mode a checker "
                "does not get to have, so it stops instead"]
    claims = {c["id"].lower(): c for c in json.loads(claims_f.read_text())["claims"]}

    surfaces = sorted((run_dir / "slides").glob("slide-*.html"))
    cp = run_dir / "copy.json"
    if cp.exists():
        blocks = json.loads(cp.read_text()).get("slides") or {}
        for key, blk in blocks.items():
            for st in _copy_strings(blk):
                surfaces.append(("copy.json " + key, st))
    if not surfaces:
        # EXIT 2, NOT 1. This file's own contract is 0 clean, 1 a label the record does not
        # support, 2 could not run. A deck that archived no slide HTML and no copy strings is
        # the third, and calling it the second reports a violation nobody committed. Three of
        # fifteen shipped decks keep no `slides/`, today's included.
        raise Absent("label_guard found no slide HTML and no copy strings in the run directory, "
                     "so there was no published surface to check")

    for surf in surfaces:
        if isinstance(surf, tuple):
            name, els = surf[0], [surf[1]]
        else:
            name, els = surf.name, _elements(surf.read_text(encoding="utf-8"))
        for ei, el in enumerate(els):
            ids = CLAIM_TOKEN.findall(el)
            if len(ids) != 1:
                # A LABEL BESIDE A LIST IS A CLAIM ABOUT THE SET, not about one item, and the
                # figures file is what backs those. The cover's "SOURCES SILENT" sits above a
                # cite naming five ids and is force_unstated, a computation, not any one claim.
                continue
            tok = "c" + ids[0]
            cid = "c" + ids[0]
            claim = claims.get(cid)
            if not claim:
                problems.append(f"{name} prints {tok!r} and no such claim is in claims.json")
                continue
            hay = ((claim.get("quote") or "") + " " + (claim.get("text") or "")).lower()
            # the label is the capitalised run before the id, in this element and the ones just
            # before it, stopping at any other claim id
            label, budget = [], WINDOW
            pool = el.split()
            # THE TWO STRIP SETS HAVE TO MATCH, and they did not. This line stripped `.,"'` while
            # the loop below strips `.,"'()`, so an id written `(c8)` was FOUND by the findall
            # above and then matched nothing here. `next()` raised StopIteration and the gate died
            # with a traceback rather than a finding, on 2026-08-29 and 2026-08-30. One strip set,
            # named once, and a default so a miss can never crash the gate again.
            cut = next((i for i, t in enumerate(pool)
                        if CLAIM_TOKEN.fullmatch(t.strip(STRIP))), None)
            if cut is None:
                # The id is inside a longer token this split cannot separate, so where the label
                # ends is not knowable here. Say so rather than guess a boundary or die.
                problems.append(
                    f"{name} prints {tok!r} in a run of text this gate cannot split on, so the "
                    f"label boundary is not knowable. Set the id off with a space")
                continue
            pool = pool[:cut]
            back = ei - 1
            while budget > 0:
                for w in pool[::-1]:
                    w = w.strip(STRIP)
                    if CLAIM_TOKEN.fullmatch(w) or not WORD.fullmatch(w):
                        budget = 0
                        break
                    label.append(w)
                    budget -= 1
                    if budget == 0:
                        break
                if budget <= 0 or back < 0:
                    break
                pool = els[back].split()
                back -= 1
            # THE STRICT RULE, AND THE ONE THE HARD FAIL NEEDED. If this id is the claim that
            # PROVES an item's shape, then a label beside it is a claim about what that body did,
            # and compute.py has already proved exactly one string against this claim's own
            # words. The frame prints that string or it prints no shape at all. Word membership
            # alone was not enough: ZONING and SEWER both appear in their claims and neither is
            # the shape the map guards, so a frame could still narrate around the guard.
            said = [w for w in label
                    if w not in FURNITURE and w not in places and not re.fullmatch(r"[0-9-]+", w)]
            if said and cid in shapes and set(said) != shapes[cid]:
                problems.append(
                    f"{name} prints {' '.join(said[::-1])!r} beside {tok}, and compute.py guards "
                    f"{' '.join(sorted(shapes[cid]))!r} as the shape {cid} proves. A label beside "
                    f"a proof claim is a claim about what a body did, so it says the guarded "
                    f"string or it says no shape at all. This is how BRAZORIA / CONDITIONS SET / "
                    f"C40 shipped over a claim whose own word is 'adopted'")
            for w in label:
                if w in FURNITURE or w in places or re.fullmatch(r"[0-9-]+", w):
                    continue
                stem = stems.get(w.lower(), w.lower())
                if stem not in hay:
                    problems.append(
                        f"{name} prints the label word {w!r} beside {tok}, and {cid} says neither "
                        f"{w.lower()!r} nor {stem!r} in its quote or its text. compute.py guards "
                        f"its own shape map against exactly this and the frame reworded it, which "
                        f"is how BRAZORIA / CONDITIONS SET / C40 shipped over a claim whose own "
                        f"word is 'adopted'")
    return problems


def self_test() -> int:
    """Replay the 2026-08-25 defect on a synthetic run, both ways."""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "slides").mkdir()
        (d / "compute.py").write_text(
            'ACTED = {\n    "tx-2026-0052": ("Brazoria County",  "resolution adopted",    "c40"),\n}\n'
            '_STEM = {"adopted": "adopt", "resolution": "resolution"}\n')
        (d / "claims.json").write_text(json.dumps({"claims": [
            {"id": "c40", "quote": "Resolution Regarding the Development of Data Centers",
             "text": "Its own agenda system records the matter as Adopted."}]}))
        bad = '<div class="pl">BRAZORIA COUNTY</div><div class="in">CONDITIONS SET</div><div class="ci">C40</div>'
        (d / "slides" / "slide-03.html").write_text(bad)
        if not check(d):
            print("SELF-TEST FAILED: the gate passed BRAZORIA / CONDITIONS SET / C40, which is "
                  "the exact string round 12 hard failed the deck for")
            return 1
        # the round 12 variant the word membership rule alone let through: a word the claim
        # does say, that is still not the shape the map guards
        near = bad.replace("CONDITIONS SET", "MATTER ADOPTED")
        (d / "slides" / "slide-03.html").write_text(near)
        if not check(d):
            print("SELF-TEST FAILED: the gate passed a label whose words are in the claim but "
                  "which is not the shape compute.py guards, which is the narrate-around-the-"
                  "guard case")
            return 1
        good = bad.replace("CONDITIONS SET", "RESOLUTION ADOPTED")
        (d / "slides" / "slide-03.html").write_text(good)
        left = check(d)
        if left:
            print("SELF-TEST FAILED: the gate refused the guarded label itself, which would teach "
                  "a run to ignore it. " + "; ".join(left))
            return 1
    print("label_guard self-test: refuses a reworded label, passes the guarded one")
    return 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    args = [a for a in argv[1:] if not a.startswith("-")]
    if not args:
        print("usage: label_guard.py <run-dir> | --self-test", file=sys.stderr)
        return 2
    d = Path(args[0])
    if not d.is_dir():
        print(f"not a directory: {d}", file=sys.stderr)
        return 2
    # ONE HANDLER FOR BOTH RAISES. `check` raises Absent when there is no surface at all, and the
    # receipt block below raises it when the surfaces carry no label beside an id. Wrapping only
    # the first left the second escaping as a traceback.
    try:
        return _run(d)
    except Absent as a:
        # 2 is "could not run", which is what a deck with no checkable surface is. Reporting it
        # as 1 would name a violation nobody committed.
        print(f"label_guard: {a}")
        (d / "label_report.json").write_text(json.dumps(
            {"run": d.name, "status": "absent", "reason": str(a),
             "checked": 0, "problems": []}, indent=1) + "\n", encoding="utf-8")
        return 2


def _run(d: Path):
    problems = check(d)
    # THE RECEIPT. gate_status reads this rather than re-deriving the answer, so the run record's
    # gate table carries the row and a run cannot quietly skip the gate. CI cannot take it,
    # because .github/workflows belongs to the human actor by ownership.yaml.
    # COUNTED OVER EVERY SURFACE THE GATE ACTUALLY READ, not over slide HTML alone. Three of
    # fifteen shipped decks archive no `slides/`, today's included, so a slides-only count wrote
    # `checked: 0` on a run where the gate had read nine copy.json blocks and traced every label
    # in them. The receipt then said the gate looked at nothing while it had done its whole job,
    # which is the narrow-measurement defect this file exists to catch, in this file.
    checked = 0
    for f in sorted((d / "slides").glob("slide-*.html")):
        checked += len(CLAIM_TOKEN.findall(_flat_for_count(f.read_text(encoding="utf-8"))))
    cpf = d / "copy.json"
    if cpf.exists():
        for blk in (json.loads(cpf.read_text(encoding="utf-8")).get("slides") or {}).values():
            for st in _copy_strings(blk):
                checked += len(CLAIM_TOKEN.findall(st))
    # A ZERO COUNT IS NOT A PASS. Deck 13's receipt read `checked: 0` with an empty problems
    # list, and gate_status rendered that as PASS, because nothing here asked whether the gate
    # had actually looked at anything. A deck that prints claim ids on its frames and gives this
    # gate none of them is a gate that is not wired up, which is the failure this file exists to
    # prevent in the copy and had in itself.
    slide_files = sorted((d / "slides").glob("slide-*.html"))
    if checked == 0:
        # THREE STATES, AND ONLY ONE OF THEM IS A DEFECT.
        #
        # This gate tests a LABEL BESIDE AN ID, so it needs a surface where the two are adjacent.
        # That is the rendered frame. A `copy.json` that keeps `labels` and `claims` in separate
        # fields, which is what every deck here does, carries no adjacency to test.
        #
        # So a deck that archived no `slides/` cannot be checked at all, and saying so is the
        # honest answer. Calling it a pass would be the `checked: 0` receipt this gate already
        # went red over once. Calling it a violation would name a defect nobody committed.
        if not slide_files:
            raise Absent(
                "this deck archived no slides/*.html, and its copy.json keeps labels and claim "
                "ids in separate fields, so no surface carries a label beside an id to check. "
                "Archive the rendered frames to make this deck checkable")
        problems.append(
            "label_guard matched no claim id on any frame. Either this deck cites nothing, which "
            "no deck here does, or the token pattern and the rendered ids disagree. A receipt "
            "reading `checked: 0` is not a pass and this refuses to write one")
    (d / "label_report.json").write_text(
        json.dumps({"checked": checked, "problems": problems}, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8")
    if problems:
        print(f"label_guard: {len(problems)} label(s) the record does not support\n")
        for p in problems:
            print("  - " + p + "\n")
        print("  A label is a CLAIM ABOUT WHAT A BODY DID. compute.py already proves each shape\n"
              "  against its claim's own words. Print that string, or change the shape in the map\n"
              "  and let the map's own assert judge it.")
        return 1
    print("label_guard: every printed label traces to its claim's own words")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
