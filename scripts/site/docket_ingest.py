#!/usr/bin/env python3
"""docket_ingest.py — turn a research batch into docket items the gates will accept.

WHY THIS IS A SCRIPT AND NOT A HANDFUL OF EDITS.

A researcher returns JSON in the shape it was asked for, and the record's shape is not quite
that shape. Four differences recur, every batch, and every one of them is a place where doing
it by hand forty times gets it wrong once:

  * `source_type` comes back as `secondary_reported`, which is not in the vocabulary. The
    record's word is `journalism`.
  * Claims arrive without ids. Ids are positional and have to be unique inside an item.
  * `last_verified` is required and a researcher has no reason to think about it.
  * `open_comment` is the one room that MUST carry a close date, because a window a reader
    cannot date is not actionable. A batch that reports an open comment period with a null
    `closes` is reporting a room it could not confirm, and the honest demotion is
    `open_meeting` when a hearing is named and `contact_only` when one is not.

None of that is judgment. It is mechanical, so it belongs in code, where it is applied
identically to every item and can be read.

WHAT THIS DELIBERATELY DOES NOT DO. It does not fact check, it does not write prose, and it
does not decide what is an item. A claim that arrives without a verbatim quote is dropped and
REPORTED, never repaired. The gates in docket_build.py are what say yes.

Usage:
    python3 scripts/site/docket_ingest.py --batch out/research/*.json --today 2026-08-14
    python3 scripts/site/docket_ingest.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCKET = REPO_ROOT / "ledger" / "docket.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docket_build import _resolver          # noqa: E402  the same gazetteer the gate reads

# The researcher's word on the left, the record's on the right. Anything not listed passes
# through and fails the gate loudly, which is correct: a source type nobody has thought about
# should stop the batch rather than be guessed into the nearest bucket.
SOURCE_TYPE_MAP = {
    "secondary_reported": "journalism",
    "secondary": "journalism",
    "reported": "journalism",
    "primary_official": "primary_official",
    "primary_corporate": "primary_corporate",
    "journalism": "journalism",
}

# A decider type the researchers were offered that the record does not carry, mapped to the
# one it actually is. `utility` and `university` were in the research prompt and are not in
# DECIDER_TYPES, which is a prompt bug rather than a record bug: a public university system
# board is a state agency, and an investor owned utility is not a decider at all here, its
# regulator is.
DECIDER_TYPE_MAP = {
    "utility": "special-district",
    "university": "state-agency",
}

ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _slug_id(n: int, year: int) -> str:
    return f"tx-{year}-{n:04d}"


def next_number(items: list) -> int:
    """One past the highest id in the record, so a re-run never reuses a number."""
    top = 0
    for it in items:
        m = re.match(r"^tx-\d{4}-(\d{4})$", str(it.get("id", "")))
        if m:
            top = max(top, int(m.group(1)))
    return top + 1


def normalise(raw: dict, item_id: str, today: str) -> tuple[dict, list[str]]:
    """One research item as a docket item, plus every repair and drop it required."""
    notes: list[str] = []
    it = json.loads(json.dumps(raw))          # never mutate the caller's batch
    it["id"] = item_id
    it["last_verified"] = today

    d = it.get("decider") or {}
    if d.get("type") in DECIDER_TYPE_MAP:
        notes.append(f"decider.type {d['type']} -> {DECIDER_TYPE_MAP[d['type']]}")
        d["type"] = DECIDER_TYPE_MAP[d["type"]]

    # THE METRO IS DERIVED FROM THE COUNTIES, NEVER TYPED, and a researcher naturally types it
    # because "Austin" is what a person calls the place. The record stores the statistical
    # area's own full name so a county page and a metro page can never disagree about which
    # metro a county is in. Whatever arrived is replaced by what the gazetteer computes.
    g = it.get("geography") or {}
    res = _resolver()
    if res is not None:
        metros = []
        for c in g.get("counties") or []:
            m = res.metro_of(c)
            if m and m.get("full_name") not in metros:
                metros.append(m["full_name"])
        computed = metros[0] if len(metros) == 1 else None
        if g.get("metro") != computed:
            notes.append(f"geography.metro {g.get('metro')!r} -> {computed!r} (derived)")
            g["metro"] = computed

    pa = it.get("public_access") or {}
    # THE ONE RULE WITH TEETH. An open comment window that carries no close date is a room the
    # batch could not confirm, and publishing it as open would put a door on the page that a
    # reader cannot date. Demoted to the strongest room the item can actually support.
    if pa.get("room") == "open_comment" and not pa.get("closes"):
        has_hearing = any(k.get("kind") == "hearing" for k in it.get("key_dates") or [])
        pa["room"] = "open_meeting" if has_hearing else "contact_only"
        notes.append(f"open_comment without a close date -> {pa['room']}")

    good, cn = [], 0
    for c in it.get("claims") or []:
        st = SOURCE_TYPE_MAP.get(c.get("source_type"), c.get("source_type"))
        if not str(c.get("verbatim_quote", "")).strip():
            notes.append(f"dropped a claim with no verbatim quote: {str(c.get('text'))[:60]}")
            continue
        if not str(c.get("source_url", "")).startswith(("http://", "https://")):
            notes.append(f"dropped a claim with no source url: {str(c.get('text'))[:60]}")
            continue
        cn += 1
        c["id"] = f"{item_id}-c{cn}"
        c["source_type"] = st
        c.setdefault("fetched", today)
        good.append(c)
    it["claims"] = good
    if not good:
        notes.append("NO CLAIMS SURVIVED. The item cannot be published")

    for kd in it.get("key_dates") or []:
        if not ISO.match(str(kd.get("date", ""))):
            notes.append(f"key date {kd.get('date')!r} is not ISO and will fail the gate")
    return it, notes


def load_batch(path: Path) -> list[dict]:
    """A batch file, whether it is bare JSON or JSON inside a fenced block in prose."""
    text = path.read_text()
    try:
        d = json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.S)
        if not m:
            raise SystemExit(f"{path}: no JSON and no fenced JSON block")
        d = json.loads(m.group(1))
    if isinstance(d, dict):
        d = d.get("items", [])
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch", nargs="*", default=[], help="research batch JSON file(s)")
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    ap.add_argument("--out", default=None, help="write here instead of the record")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return _self_test()
    # A GATE INVOKED WITH NOTHING TO DO EXITS 2 AND NEVER 0. A batchless run that reported
    # success would be indistinguishable from a run that ingested everything.
    if not a.batch:
        print("docket_ingest: no --batch given and nothing to do", file=sys.stderr)
        return 2

    doc = json.loads(DOCKET.read_text())
    items = doc["items"]
    n = next_number(items)
    added, report = [], []
    for f in a.batch:
        for raw in load_batch(Path(f)):
            item, notes = normalise(raw, _slug_id(n, int(a.today[:4])), a.today)
            if not item["claims"]:
                report.append(f"SKIPPED {raw.get('title', '?')[:70]}: no claims survived")
                continue
            added.append(item)
            for note in notes:
                report.append(f"{item['id']}: {note}")
            n += 1

    items.extend(added)
    out = Path(a.out) if a.out else DOCKET
    out.write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")
    for line in report:
        print(f"  .. {line}")
    print(f"docket_ingest: {len(added)} item(s) added, "
          f"{sum(len(i['claims']) for i in added)} claim(s), {len(report)} repair(s)")
    return 0


def _self_test() -> int:
    fails = []

    def check(label, cond, extra=""):
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}" + ("" if cond or not extra
                                                            else f"  {extra}"))
        if not cond:
            fails.append(label)

    base = {"title": "T", "summary": "S", "topic": "data-centers",
            "decider": {"name": "N", "type": "city"},
            "geography": {"statewide": False, "counties": [], "metro": None, "on_ercot": True},
            "status": "decided", "key_dates": [{"date": "2026-08-11", "kind": "ordered"}],
            "public_access": {"room": "open_meeting", "how": "H", "url": "https://x.tld",
                              "closes": None},
            "claims": [{"text": "t", "verbatim_quote": "q", "source_url": "https://x.tld",
                        "source_type": "secondary_reported"}]}

    it, notes = normalise(base, "tx-2026-0099", "2026-08-14")
    check("the researcher's source type becomes the record's",
          it["claims"][0]["source_type"] == "journalism", it["claims"][0]["source_type"])
    check("claims are numbered inside the item", it["claims"][0]["id"] == "tx-2026-0099-c1")
    check("last_verified is stamped", it["last_verified"] == "2026-08-14")
    check("the caller's batch is not mutated",
          base["claims"][0].get("id") is None and "last_verified" not in base)

    # THE ROOM DEMOTION, both ways.
    oc = json.loads(json.dumps(base))
    oc["public_access"] = {"room": "open_comment", "how": "H", "url": "https://x.tld",
                           "closes": None}
    oc["key_dates"] = [{"date": "2026-09-01", "kind": "hearing"}]
    it2, n2 = normalise(oc, "tx-2026-0100", "2026-08-14")
    check("an undated comment window with a hearing becomes an open meeting",
          it2["public_access"]["room"] == "open_meeting", it2["public_access"]["room"])
    check("...and the demotion is reported rather than silent", any("open_comment" in x
                                                                    for x in n2))
    oc2 = json.loads(json.dumps(oc))
    oc2["key_dates"] = [{"date": "2026-09-01", "kind": "filed"}]
    it3, _ = normalise(oc2, "tx-2026-0101", "2026-08-14")
    check("an undated comment window with no hearing becomes contact only",
          it3["public_access"]["room"] == "contact_only", it3["public_access"]["room"])
    dated = json.loads(json.dumps(base))
    dated["public_access"] = {"room": "open_comment", "how": "H", "url": "https://x.tld",
                              "closes": "2026-09-04"}
    it4, _ = normalise(dated, "tx-2026-0102", "2026-08-14")
    check("a comment window that carries its close date is left alone",
          it4["public_access"]["room"] == "open_comment")

    # A CLAIM WITHOUT PROOF IS DROPPED, NEVER REPAIRED.
    bad = json.loads(json.dumps(base))
    bad["claims"] = [{"text": "t", "verbatim_quote": "  ", "source_url": "https://x.tld",
                      "source_type": "journalism"},
                     {"text": "u", "verbatim_quote": "q", "source_url": "not-a-url",
                      "source_type": "journalism"},
                     {"text": "v", "verbatim_quote": "q", "source_url": "https://y.tld",
                      "source_type": "primary_official"}]
    it5, n5 = normalise(bad, "tx-2026-0103", "2026-08-14")
    check("a claim with no quote is dropped", len(it5["claims"]) == 1, len(it5["claims"]))
    check("...and so is a claim with no source url", it5["claims"][0]["text"] == "v")
    check("...and both drops are reported", sum("dropped" in x for x in n5) == 2)
    check("surviving claims renumber from one without a gap",
          it5["claims"][0]["id"] == "tx-2026-0103-c1")

    empty = json.loads(json.dumps(base))
    empty["claims"] = []
    it6, n6 = normalise(empty, "tx-2026-0104", "2026-08-14")
    check("an item with nothing provable says so", any("NO CLAIMS" in x for x in n6))

    check("the next id is one past the highest, not the count",
          next_number([{"id": "tx-2026-0001"}, {"id": "tx-2026-0025"}]) == 26)
    check("an empty record starts at one", next_number([]) == 1)

    # A DECIDER TYPE THE RESEARCH PROMPT OFFERED AND THE RECORD DOES NOT CARRY.
    uni = json.loads(json.dumps(base))
    uni["decider"] = {"name": "UT System Board of Regents", "type": "university"}
    it7, n7 = normalise(uni, "tx-2026-0105", "2026-08-14")
    check("a decider type outside the vocabulary is mapped and reported",
          it7["decider"]["type"] == "state-agency" and any("decider.type" in x for x in n7))

    print("\ndocket_ingest self-test: " +
          ("all passed" if not fails else f"{len(fails)} FAILED"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
