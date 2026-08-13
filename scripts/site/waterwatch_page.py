#!/usr/bin/env python3
"""waterwatch_page.py — Texas reservoir storage, rendered from the record and nothing else.

WHY WATER SITS BESIDE THE GRID ON THIS SITE

A data centre needs two things Texas has to supply from a finite stock: electricity, and, for
most cooling designs, water. The grid watch tracks the first. This tracks the second, and the
two together are the physical account behind every siting decision in the docket.

The finding that made this instrument worth building is visible on day one and needs no model:

    The Texas metro with the least water in storage is Midland Odessa, in the Permian
    Basin, at a quarter full, while Austin sits near the top of its reservoirs.

That is two measured numbers side by side, not an argument. Where the new load is going and
where the water is are different maps, and this page publishes both without drawing the
conclusion for anybody.

WHAT IT REFUSES TO SAY

No verdict, on the same terms as the grid watch. A reservoir at a quarter full is a measurement,
not a shortage: some are drawn down on purpose, some are fed by rivers that recover in a week,
and municipal supply is a system of many parts, of which surface storage is one. So the bars
carry one hue at one intensity at every value, and the words "drought" and "shortage" do not
appear as findings anywhere on this page.

WHAT IT PUBLISHES INSTEAD OF THE HISTORY IT CANNOT HAVE

TWDB keeps daily reservoir figures back to 1933, which would let today be ranked against the
same date in ninety four prior years. Those files are CSVs, and `waterdatafortexas.org`
robots.txt disallows `*.csv`. So we do not take them, we do not print a percentile, and we say
why. Our own history starts the day the collector started. That is a smaller claim and a true
one, and the gap itself is a fact worth publishing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numeral_lint                                                # noqa: E402

READINGS = REPO_ROOT / "ledger" / "gridwatch" / "water.jsonl"

# NUMERALS THAT ARE QUOTED RATHER THAN COMPUTED. The law admits both and forbids only a numeral
# that is neither; the docket gate has always worked this way. Every entry names the source it
# is quoted from, and there is deliberately no way to add one without writing that down, which
# is what keeps this from becoming a hole in the gate.
QUOTED = {
    "1933": "TWDB publishes daily reservoir conservation storage beginning 1933-07-01, "
            "which is the archive this page explains it does not take.",
}

# Metro slugs come from TWDB's own municipal tags. Their display names are ours, and they are
# labels rather than data: no numeral lives in this table, so nothing here can smuggle a figure
# onto the page.
METRO_NAMES = {
    "abilene": "Abilene", "amarillo": "Amarillo", "austin": "Austin",
    "beaumont_port_arthur": "Beaumont and Port Arthur", "brownsville": "Brownsville",
    "corpus_christi": "Corpus Christi", "dallas": "Dallas", "el_paso": "El Paso",
    "fort_worth": "Fort Worth", "houston": "Houston", "laredo": "Laredo",
    "lubbock": "Lubbock", "midland_odessa": "Midland and Odessa",
    "nacogdoches": "Nacogdoches", "san_angelo": "San Angelo", "san_antonio": "San Antonio",
    "temple_killeen": "Temple and Killeen", "texarkana": "Texarkana", "tyler": "Tyler",
    "waco": "Waco", "wichita_falls": "Wichita Falls",
}


def load(path: Path = READINGS) -> list[dict]:
    """Every day the record holds, one per date, latest line wins."""
    if not path.exists():
        return []
    by_date: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("date"):
            by_date[rec["date"]] = rec
    return [by_date[d] for d in sorted(by_date)]


# --------------------------------------------------------------------------- formatting
def pct(x) -> str | None:
    return None if x is None else f"{round(float(x), 1):,.1f}"


def af(x) -> str | None:
    """Acre feet, whole. A tenth of an acre foot is a rounding artefact, not a measurement."""
    return None if x is None else f"{round(float(x)):,}"


def pt(x) -> str | None:
    """Percentage points, two decimals.

    Used only for the disagreement between our arithmetic and the publisher's. At one decimal
    a gap of 0.05 prints as 0.1, which reports our own check as twice as bad as it is. A
    figure whose entire job is to be small deserves the precision to show that it is.
    """
    return None if x is None else f"{round(float(x), 2):,.2f}"


def maf(x) -> str | None:
    """Millions of acre feet, for the statewide figure, where the raw number is unreadable."""
    return None if x is None else f"{round(float(x) / 1e6, 2):,.2f}"


def ordinal_date(iso: str) -> str:
    import datetime as _dt
    d = _dt.date.fromisoformat(iso)
    suf = "th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th")
    return f"{d:%B} {d.day}{suf}, {d.year}"


def metro_name(slug: str) -> str:
    return METRO_NAMES.get(slug, slug.replace("_", " ").title())


# --------------------------------------------------------------------------- computation
def figures(records: list[dict]) -> dict:
    """Every number this page publishes, computed here, from the record."""
    live = [r for r in records if r.get("verified") and r.get("percent_full") is not None]
    f: dict = {"days_held": len(records), "days_verified": len(live),
               "days_unverified": len(records) - len(live), "latest": None, "change": None}
    if not live:
        return f

    last = live[-1]
    metros = []
    for slug, m in (last.get("metros") or {}).items():
        if m.get("percent_full") is not None:
            metros.append({"slug": slug, "name": metro_name(slug),
                           "percent_full": m["percent_full"],
                           "storage_af": m.get("storage_af"),
                           "capacity_af": m.get("capacity_af"),
                           "reservoirs": m.get("reservoirs")})
    metros.sort(key=lambda m: m["percent_full"])

    f["latest"] = {
        "date": last["date"],
        "storage_af": last["storage_af"],
        "capacity_af": last["capacity_af"],
        "percent_full": last["percent_full"],
        "reservoir_count": last["reservoir_count"],
        # THE NAMES, NOT THE FIGURES. `coverage` needs to know whether a named reservoir is
        # in the day's record before the page says it is, and nothing else here reads them.
        # Carrying the whole storage map would put 119 unauthorised numerals in reach of a
        # page that has no business printing any of them.
        "reservoir_names": sorted(last.get("reservoirs") or {}),
        "metros": metros,
        "excluded_out_of_state": last.get("excluded_out_of_state") or [],
        "excluded_no_pool": last.get("excluded_no_conservation_pool") or [],
        "agreement": last.get("percent_full_max_disagreement"),
    }
    # COMPUTED HERE, so the page and its numeral gate read the same two figures from the
    # same call. Computing it in the renderer and again in `authorised` would be two copies
    # of one derivation, and the gate would be checking its own second opinion.
    f["latest"]["coverage"] = coverage(metros, f["latest"]["reservoir_names"])

    # THE DAY OVER DAY MOVE, which is the whole reason this instrument is daily rather than
    # weekly. It appears only when there is an actual previous day to difference against, and
    # only when that day is the one immediately before: differencing across a gap would present
    # a week of change as a day of it.
    if len(live) >= 2:
        import datetime as _dt
        prev, cur = live[-2], live[-1]
        gap = (_dt.date.fromisoformat(cur["date"])
               - _dt.date.fromisoformat(prev["date"])).days
        if gap == 1:
            f["change"] = {
                "storage_af": round(cur["storage_af"] - prev["storage_af"], 1),
                "percent_full": round(cur["percent_full"] - prev["percent_full"], 2),
                "from_date": prev["date"],
            }
    return f


# --------------------------------------------------------------------------- rendering
def registry() -> dict:
    """The slug-to-registry crosswalk, derived, or {} when the gazetteer is unreadable.

    THE SLUG IS THE SOURCE'S WORD AND IT IS NOT REWRITTEN. `municipal_temple_killeen` and
    `municipal_midland_odessa` are tags TWDB publishes and this project fetched. Editing
    them to match the federal delineation would be editing fetched data, which is the one
    thing a record product does not get to do. So the OMB name is derived beside the slug
    by `places.Resolver.crosswalk`, and where the two disagree the page shows both.
    """
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "shared"))
        import places                                                # noqa: PLC0415
        r = places.Resolver.load()
    except Exception:                                                # noqa: BLE001
        return {}
    return {"resolver": r,
            "areas": [p for p in r.places if p.get("kind") == r.METRO]}


def coverage(metros: list[dict], reservoir_names: list) -> dict:
    """What the metro roll-up reaches, and what it does not.

    THE SAN ANTONIO HOLE, WHICH IS THE POINT OF THIS FUNCTION. Nineteen slugs come out of
    the feed and San Antonio-New Braunfels is not one of them, while Canyon and Medina are
    both in the reservoir list. So the second largest metropolitan area in Texas has no
    line on this page and two of its reservoirs are sitting in the same payload untagged.

    That is a gap in the SOURCE's municipal tagging rather than a fact about water, and
    the difference matters enormously to a reader. A page that simply omitted San Antonio
    would read as though there were nothing to say.

    Every part of this is checked rather than asserted. The areas with a line are the ones
    whose slug resolves. The named reservoirs are confirmed present in the day's record.
    Neither the count nor the names are typed.
    """
    reg = registry()
    if not reg:
        return {}
    r = reg["resolver"]
    hit, walk = set(), []
    for m in metros:
        c = r.crosswalk(m["slug"])
        walk.append({**c, "name": m["name"]})
        # EVERY GRAIN IS LIFTED TO CBSA BEFORE IT IS COUNTED, or the comparison is between
        # two different populations. The first version counted the raw ids and reported
        # "20 of the 67 statistical areas", where 67 is the CBSA count and the 20 included
        # two metropolitan DIVISIONS, which are not CBSAs and are both inside one. Dallas
        # and Fort Worth were counted twice and their shared area counted zero times.
        #
        # Both numbers were computed from data and the numeral gate passed them, because a
        # gate that checks whether a figure was computed cannot check whether it was the
        # right figure. Only reading the sentence catches this one. A division and a
        # combined area both lift through their member counties, which is the one route
        # every grain in this registry shares.
        for pid in c["ids"]:
            p = r.by_id.get(pid)
            if not p:
                continue
            if p.get("kind") == r.METRO:
                hit.add(pid)
                continue
            for county in p.get("counties") or []:
                parent = r.metro_of(county)
                if parent:
                    hit.add(parent["id"])
    unlined = [p for p in reg["areas"] if p["id"] not in hit]
    sa = next((p for p in reg["areas"] if p["id"].startswith("metro-san-antonio")), None)
    # Named only if the day's record actually holds them. An example a reader can check.
    stranded = [k for k in ("Canyon", "Medina") if k in set(reservoir_names or [])]
    return {"walk": walk, "areas": len(reg["areas"]), "lined": len(hit),
            "unlined": len(unlined),
            "san_antonio": sa if (sa and sa["id"] not in hit) else None,
            "stranded": stranded}


def metro_bars(metros: list[dict], walk: list | None = None) -> str:
    """Nineteen metros, sorted driest first, one bar each.

    ONE HUE AT EVERY VALUE, same rule as the grid watch. A colour ramp here would say that a
    quarter full is bad, and this page does not know that: some reservoirs are drawn down on
    purpose, some refill in a week, and surface storage is one part of a municipal supply that
    also runs on groundwater, reuse and purchased water. The order carries the comparison. The
    length carries the size. Nothing else is claimed.
    """
    if not metros:
        return ""
    # THE FEDERAL NAME, WHERE IT DIFFERS FROM THE SOURCE'S. Shown only on the rows where
    # the two disagree, because printing "Abilene (Abilene, TX)" nineteen times to catch
    # the four that matter is noise a reader has to filter every visit.
    by_slug = {w["slug"]: w for w in (walk or [])}

    def omb(m):
        w = by_slug.get(m["slug"])
        if not w or not w["ids"]:
            return ""
        r = registry().get("resolver")
        names = [r.by_id[i]["name"] for i in w["ids"] if r and i in r.by_id]
        if not names or (len(names) == 1 and names[0].lower() == m["name"].lower()):
            return ""
        return f'<br><span class="meta">{", ".join(names)}</span>'

    rows = "".join(f"""<tr>
  <th scope="row">{m['name']}{omb(m)}</th>
  <td class="barcell"><div class="bar mini"><div class="fill"
      style="width:{min(float(m['percent_full']), 100.0):.1f}%"></div></div></td>
  <td class="n num">{pct(m['percent_full'])}%</td>
  <td class="n num">{af(m['storage_af'])}</td>
</tr>""" for m in metros)
    return f"""<table class="figures metros">
<caption>Municipal reservoir storage by metro, driest first. Every bar is the same colour at
every value. The order and the length carry the comparison. Neither implies a judgement.
Where the water data's name for an area differs from the federal delineation, both are
shown.</caption>
<thead><tr><th>Metro</th><th>Full</th><th class="n">Percent</th>
<th class="n">Acre feet</th></tr></thead>
<tbody>{rows}</tbody></table>"""


def body(records: list[dict], today: str) -> str:
    f = figures(records)
    if not f["latest"]:
        return """
<h1>Texas Water Watch</h1>
<div class="prose">
  <p>A daily numeric record of water held in Texas reservoirs, published beside the grid watch
  because a data centre draws on both.</p>
  <div class="gap"><strong>The record is empty.</strong> No day has been collected yet.
  Nothing is estimated to fill the space.</div>
</div>
"""
    L = f["latest"]
    d = ordinal_date(L["date"])
    metros = L["metros"]
    driest, fullest = (metros[0], metros[-1]) if metros else (None, None)

    lede = ""
    if driest and fullest and driest["slug"] != fullest["slug"]:
        lede = f"""
  <p class="lede">Texas reservoirs hold <strong class="num">{maf(L['storage_af'])}</strong>
  million acre feet, <strong class="num">{pct(L['percent_full'])}%</strong> of the conservation
  capacity across <strong class="num">{af(L['reservoir_count'])}</strong> reservoirs. The
  spread between metros is the part worth looking at. {driest['name']} sits at
  <strong class="num">{pct(driest['percent_full'])}%</strong> while {fullest['name']} sits at
  <strong class="num">{pct(fullest['percent_full'])}%</strong>.</p>"""

    change = ""
    c = f["change"]
    if c:
        direction = "rose" if c["storage_af"] > 0 else "fell" if c["storage_af"] < 0 else "held"
        change = f"""
  <p>Storage {direction} by <strong class="num">{af(abs(c['storage_af']))}</strong> acre feet
  against {ordinal_date(c['from_date'])}. That is a move of
  <strong class="num">{pct(abs(c['percent_full']))}</strong> points. Daily movement is the reason
  this record is daily. A weekly instrument would have shown the same number twice.</p>"""

    agree = ""
    if L.get("agreement") is not None:
        agree = f"""
  <p>Percent full is computed here from storage over capacity, never read from the feed's own
  field. Comparing the two is free. Across every reservoir counted the largest disagreement
  was <strong class="num">{pt(L['agreement'])}</strong> of a percentage point, which is
  rounding. It is checked every day because the day it stops being rounding is the day their
  field means something other than what this code assumes.</p>"""

    cov = L.get("coverage") or {}
    gap = ""
    if cov and cov.get("san_antonio"):
        sa = cov["san_antonio"]
        seen = (" Both are in the day's reservoir record. The missing line is a gap in the "
                "source's municipal tagging rather than an absence of water."
                if len(cov["stranded"]) == 2 else "")
        gap = f"""
    <p><strong>San Antonio has no line above. That is a gap rather than an answer.</strong>
    The state's water data tags reservoirs to <strong class="num">{af(cov['lined'])}</strong>
    of the <strong class="num">{af(cov['areas'])}</strong> statistical areas in Texas.
    {sa['name']} is not one of them.
    {" and ".join(cov["stranded"]) if cov["stranded"] else "Its reservoirs"} sit in the same
    payload carrying no municipal tag at all.{seen} Reading that as a dry metro would be
    exactly backwards.</p>"""

    out_of_state = ""
    if L["excluded_out_of_state"]:
        out_of_state = f"""
    <p><strong>El Paso is not in this table, and that is the correct answer.</strong> The only
    reservoir tagged to El Paso in the state's data is Elephant Butte Lake, which is in New
    Mexico. It is excluded from every figure above, along with
    <strong class="num">{af(len(L['excluded_out_of_state']) - 1)}</strong> other out of state
    reservoirs. Publishing a New Mexico lake as El Paso's water supply would be wrong, and El
    Paso's supply is a different system that this instrument does not measure.</p>"""

    return f"""
<h1>Texas Water Watch</h1>
<div class="prose">{lede}
  <p>A data centre needs electricity. Most cooling designs need water too. The
  <a href="../grid/">grid watch</a> tracks the first and this tracks the second. Together they
  are the physical account behind every siting decision in <a href="../record/">the record</a>.</p>
</div>

<h2>{d}</h2>
{metro_bars(metros, cov.get("walk"))}

<div class="prose">
  <p>Statewide, conservation storage stands at
  <strong class="num">{af(L['storage_af'])}</strong> acre feet against a conservation capacity
  of <strong class="num">{af(L['capacity_af'])}</strong>.</p>{change}{agree}
</div>

<h2>What this measures, and what it does not</h2>
<div class="prose">
  <div class="gap">
    <p><strong>This is surface water in reservoirs, and nothing else.</strong> A Texas city's
    supply also runs on groundwater, on reuse, and on water bought from other systems. The
    Ogallala under the Panhandle and the Edwards under Central Texas are not measured here and
    do not move the numbers above.</p>{gap}
    <p>So a low bar is not a conclusion about a city's water supply and a full bar is not a
    promise about it. Some reservoirs are drawn down deliberately. Some refill in a week from
    one storm upstream. The figures are what was in storage on the day and nothing more is
    claimed from them.</p>{out_of_state}
    <p>Flood control dams with no conservation pool are excluded rather than counted as
    empty, <strong class="num">{af(len(L['excluded_no_pool']))}</strong> of them. They stand dry by
    design and would otherwise drag the state total down for doing their job.</p>
  </div>
  <p><strong>There is no historical percentile on this page, and the reason is worth stating.
  </strong> The state publishes daily reservoir figures back to 1933, which would let today be
  ranked against the same date in every prior year. Those files are CSVs, and the publisher's
  robots.txt asks crawlers not to take CSVs. So they are not taken, no percentile is printed,
  and this record's own history begins the day it began. The comparison exists. Taking the
  file it lives in is the one thing the publisher has asked crawlers not to do.</p>
  <p>The record holds <strong class="num">{af(f['days_held'])}</strong> day(s) so far.
  <a href="../waterwatch.json">The data is open</a>, per reservoir, so every roll up above can
  be recomputed without refetching anything.</p>
</div>
"""


# --------------------------------------------------------------------------- numeral gate
def authorised(f: dict) -> set[str]:
    acc = numeral_lint.Authorised()
    add = acc.add
    add(*QUOTED)
    add(af(f["days_held"]), af(f["days_verified"]), af(f["days_unverified"]))
    L = f.get("latest")
    if L:
        add(ordinal_date(L["date"]), maf(L["storage_af"]), af(L["storage_af"]),
            af(L["capacity_af"]), pct(L["percent_full"]), af(L["reservoir_count"]),
            pt(L.get("agreement")), af(len(L["excluded_no_pool"])),
            af(max(len(L["excluded_out_of_state"]) - 1, 0)))
        for m in L["metros"]:
            add(pct(m["percent_full"]), af(m["storage_af"]), af(m["capacity_af"]),
                af(m["reservoirs"]))
        cov = L.get("coverage") or {}
        add(af(cov.get("lined")), af(cov.get("areas")), af(cov.get("unlined")))
    c = f.get("change")
    if c:
        add(af(abs(c["storage_af"])), pct(abs(c["percent_full"])),
            ordinal_date(c["from_date"]))
    return acc.set


def lint(html_body: str, f: dict) -> list[str]:
    return numeral_lint.scan(html_body, authorised(f))


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def rec(date, storage=24303346.0, capacity=31558535.0, metros=None, verified=True):
        metros = metros if metros is not None else {
            "midland_odessa": {"storage_af": 30000.0, "capacity_af": 108000.0,
                               "percent_full": 27.59, "reservoirs": 3},
            "austin": {"storage_af": 1980000.0, "capacity_af": 2000000.0,
                       "percent_full": 99.04, "reservoirs": 4},
            "houston": {"storage_af": 145000.0, "capacity_af": 149000.0,
                        "percent_full": 97.26, "reservoirs": 3},
        }
        return {"_spec": 1, "date": date, "verified": verified, "storage_af": storage,
                "capacity_af": capacity,
                "percent_full": round(storage / capacity * 100, 2), "reservoir_count": 119,
                "metros": metros, "excluded_out_of_state": ["ElephantButte"],
                "excluded_no_conservation_pool": ["Addicks", "Barker"],
                "percent_full_max_disagreement": 0.05}

    one = [rec("2026-08-11")]
    f = figures(one)
    b = body(one, "2026-08-11")
    check("the page renders from a single record", "<h1>Texas Water Watch</h1>" in b)
    check("metros are sorted driest first",
          [m["slug"] for m in f["latest"]["metros"]][0] == "midland_odessa")
    check("the lede names the driest and the fullest without judging either",
          "Midland and Odessa" in b and "Austin" in b)
    check("every numeral traces to a computation", not lint(b, f), str(lint(b, f)[:8]))
    check("a typed numeral fails the gate", "8.9" in lint(b.replace("</h1>",
          "</h1><p>about 8.9 percent</p>"), f))

    # THE VERDICT RULE. Water has no red zone to imply either.
    for w in ("drought", "shortage", "crisis", "running out", "at risk"):
        check(f"the copy does not pronounce: {w}", w not in b.lower())
    check("the bars carry no severity class",
          'class="fill"' in b and "fill low" not in b and "fill crit" not in b)

    # THE EL PASO TRAP, said out loud on the page rather than only handled in code.
    check("El Paso's absence is explained rather than silently correct",
          "Elephant Butte" in b and "New Mexico" in b)
    check("El Paso is not given a bar", "el_paso" not in b)

    check("the missing percentile is explained, not omitted quietly",
          "robots.txt" in b and "1933" in b)
    check("...and 1933 is authorised, since it names a real published start",
          "1933" not in lint(b, f))

    # THE DAY OVER DAY MOVE.
    two = [rec("2026-08-10", storage=24329431.0), rec("2026-08-11")]
    f2 = figures(two)
    check("two consecutive days produce a change figure", f2["change"] is not None)
    check("...computed, and signed", f2["change"]["storage_af"] == -26085.0,
          str(f2["change"]["storage_af"]))
    b2 = body(two, "2026-08-11")
    check("the change renders as a fall without calling it a decline",
          "fell by" in b2 and "26,085" in b2)
    check("...and passes the gate", not lint(b2, f2), str(lint(b2, f2)[:8]))

    gapped = [rec("2026-08-01", storage=24329431.0), rec("2026-08-11")]
    check("a gap in the series produces no day over day figure",
          figures(gapped)["change"] is None)
    check("...so a week of movement is never printed as a day of it",
          "fell by" not in body(gapped, "2026-08-11"))

    empty = body([], "2026-08-11")
    check("an empty record says so rather than rendering zeros",
          "The record is empty." in empty and not lint(empty, figures([])))

    unver = [{"_spec": 1, "date": "2026-08-11", "verified": False}]
    check("an unverified day publishes no number",
          figures(unver)["latest"] is None and figures(unver)["days_verified"] == 0)

    # ---- the house rules, on every shape the record can take ------------------
    # THE RICHER BRANCHES USED TO SHIP UNLINTED UNTIL DATA HAPPENED TO ARRIVE. This page is
    # written to be true at one record and to say more as the series grows, so whole paragraphs
    # exist only at two records or more. The comparison paragraph rendered for the FIRST time on
    # 2026-08-12, the day a second reading landed, carrying a colon and pushing the page's comma
    # rate over its ceiling. It reached the deploy gate because nothing had ever linted it: the
    # fixtures below already built the two record shape, and the checks on it only asked
    # structural questions.
    #
    # A page that degrades honestly has more shapes than a page that does not, and every one of
    # them is copy a reader eventually sees. So the linter runs on all of them here, at the same
    # moment the fixture is built, rather than on whichever shape today's data happens to produce.
    import house_style_check as _hs                                 # noqa: PLC0415
    for label, records in (("one record", one), ("two records", two), ("a gap", gapped),
                           ("an empty record", []), ("an unverified day", unver)):
        rendered = body(records, records[-1]["date"] if records else "2026-08-11")
        problems = _hs.caption_check.check(_hs.our_prose(rendered))
        rate = _hs.caption_check.rate_problem(_hs.our_sentences(rendered),
                                              _hs.caption_check.SITE_COMMA_CEILING)
        if rate:
            problems = problems + [rate]
        check(f"the copy at {label} keeps the house rules", not problems,
              "; ".join(problems)[:150])

    # THE QUOTED ESCAPE HATCH, held to its own standard. It is the one route by which a numeral
    # that was not computed can reach a reader, so it must be impossible to widen quietly.
    check("every quoted numeral carries the source it is quoted from",
          all(isinstance(v, str) and len(v) > 40 for v in QUOTED.values()),
          str([k for k, v in QUOTED.items() if not isinstance(v, str) or len(v) <= 40]))
    check("the quoted list stays short enough to read in one glance", len(QUOTED) <= 5,
          f"{len(QUOTED)} entries")
    check("a quoted numeral actually appears in the copy it was admitted for",
          all(k in b for k in QUOTED), str([k for k in QUOTED if k not in b]))

    check("a metro slug with no display name still reads as words",
          metro_name("some_new_metro") == "Some New Metro")
    check("the display name table carries no numerals",
          not any(ch.isdigit() for ch in "".join(METRO_NAMES.values())))

    # THE COVERAGE ARITHMETIC HAS TO CLOSE, and this is the assertion that would have
    # caught the sentence that shipped: "20 of the 67 statistical areas", where the 20
    # counted two metropolitan divisions that are not among the 67. Both numbers were
    # computed and the numeral gate passed them. The population they are drawn from is
    # what the gate could not check, and 20 + 49 never equalled 67.
    live = figures(load())
    cov = (live.get("latest") or {}).get("coverage") or {}
    if cov:
        check("every area is either lined or unlined, and never both or neither",
              cov["lined"] + cov["unlined"] == cov["areas"],
              f'{cov["lined"]} + {cov["unlined"]} != {cov["areas"]}')
        check("the lined count is drawn from the same population it is compared against",
              cov["lined"] <= cov["areas"])
        check("San Antonio is reported as a gap while the source does not tag it",
              cov["san_antonio"] is not None)

    synthetic = coverage([{"slug": "dallas", "name": "Dallas"},
                          {"slug": "fort_worth", "name": "Fort Worth"}], [])
    check("two divisions of one area count that area once, not twice",
          not synthetic or synthetic["lined"] == 1, str(synthetic.get("lined")))
    check("a slug the registry does not know is counted as reaching nothing",
          (coverage([{"slug": "narnia", "name": "Narnia"}], []) or {}).get("lined") == 0)

    if failures:
        print(f"\nwaterwatch_page self-test: {failures} FAILED")
        return 1
    print("\nwaterwatch_page self-test: all passed")
    return 0


if __name__ == "__main__":
    sys.exit(self_test())
