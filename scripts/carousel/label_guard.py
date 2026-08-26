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
import ast, json, re, sys
from pathlib import Path

# Words a label may carry that are not claims about what a body did: connectives, the deck's own
# furniture, and the generic half of a body's name. Kept short on purpose. Anything that is not
# here and not a place name has to be in the claim.
FURNITURE = {
    "AND", "OR", "THE", "A", "AN", "OF", "IN", "ON", "AT", "TO", "FOR", "BY", "WITH", "FROM",
    "COUNTY", "CITY", "COMMISSION", "COURT", "COUNCIL", "TX", "SAYS", "SAY", "NEITHER",
}
WORD = re.compile(r"[A-Z][A-Z0-9'-]{1,}")
CLAIM_TOKEN = re.compile(r"\bC(\d{1,3})\b")
WINDOW = 6          # capitalised words before an id that count as its label


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
                    stems = ast.literal_eval(body)
                except (ValueError, SyntaxError):
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
    places, stems, shapes = _guarded(compute.read_text(encoding="utf-8"))
    if not places:
        return ["label_guard found no shape map in compute.py, so it is reading the wrong file"]
    if not stems:
        return ["label_guard could not read compute.py's _STEM table, so every word would be "
                "matched literally and the gate would fire on correct labels. That is the one "
                "failure mode a checker does not get to have, so it stops instead"]
    claims = {c["id"].lower(): c for c in json.loads(claims_f.read_text())["claims"]}

    surfaces = sorted((run_dir / "slides").glob("slide-*.html"))
    cp = run_dir / "copy.json"
    if cp.exists():
        blocks = json.loads(cp.read_text()).get("slides") or {}
        for key, blk in blocks.items():
            for st in (blk.get("strings") or []):
                surfaces.append(("copy.json " + key, str(st)))
    if not surfaces:
        return ["label_guard found no slides and no copy.json, so it checked nothing"]

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
            tok = "C" + ids[0]
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
            pool = pool[:next(i for i, t in enumerate(pool)
                              if CLAIM_TOKEN.fullmatch(t.strip(".,\"'")))]
            back = ei - 1
            while budget > 0:
                for w in pool[::-1]:
                    w = w.strip(".,\"'()")
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
    problems = check(d)
    # THE RECEIPT. gate_status reads this rather than re-deriving the answer, so the run record's
    # gate table carries the row and a run cannot quietly skip the gate. CI cannot take it,
    # because .github/workflows belongs to the human actor by ownership.yaml.
    import re as _re
    checked = 0
    for f in sorted((d / "slides").glob("slide-*.html")):
        checked += len(CLAIM_TOKEN.findall(_flat_for_count(f.read_text(encoding="utf-8"))))
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
