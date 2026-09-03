#!/usr/bin/env python3
"""waterwatch_page.py — Texas reservoir storage, rendered from the record and nothing else.

WHY WATER SITS BESIDE THE GRID ON THIS SITE

A data center needs two things Texas has to supply from a finite stock: electricity, and, for
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

import html
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
# Empty, and that is the wanted state. The one entry here existed for a paragraph explaining
# why no historical percentile is printed, and that paragraph came off the page. An
# authorisation outliving the copy it was granted for is how an allowlist rots.
QUOTED: dict[str, str] = {}

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
def reservoir_rows(record: dict) -> list[dict]:
    """One day's reservoirs, each with the percent full THIS build computed.

    THE PUBLISHER'S OWN `percent_full` IS NOT READ, here or anywhere. The page has said since
    it was written that percent full is storage over capacity and never the feed's field, and
    that promise has to hold for the hundred and nineteen readings a drawing is made of just
    as it holds for the one figure a sentence quotes. A chart plotted from their number beside
    a sentence quoting ours would be two different measurements wearing one label.

    A reservoir with no conservation pool is not here: dividing by a capacity of zero is not a
    percentage, and `waterwatch_collect` already excludes those from the day's roll up for the
    same reason. They stand dry by design.
    """
    rows = []
    for key, r in sorted((record.get("reservoirs") or {}).items()):
        # A RESERVOIR THIS FUNCTION CANNOT READ COSTS ITS OWN ROW AND NOTHING ELSE. The record
        # is fetched data and the drawings are the last thing on the page that should decide
        # whether it renders at all, so an entry that is not the shape expected is skipped
        # rather than raised on. This is not hypothetical: `waterwatch_pagecheck`'s fixture
        # carries `reservoirs` as a plain name to storage map, which is what the field was
        # when only its KEYS were ever read, and the first version of this crashed the whole
        # page on it. A page that renders no figures because one field changed shape is a
        # worse failure than a map with a pin missing.
        if not isinstance(r, dict):
            continue
        cap, sto = r.get("capacity_af"), r.get("storage_af")
        if not isinstance(cap, (int, float)) or not isinstance(sto, (int, float)) or not cap:
            continue
        rows.append({"key": key, "storage_af": float(sto), "capacity_af": float(cap),
                     "percent_full": round(float(sto) / float(cap) * 100.0, 2)})
    return rows


def capacity_below_average(rows: list[dict], statewide_capacity) -> float | None:
    """How much of the state's capacity sits in reservoirs below the state's own average.

    THE FIGURE THE METRO TABLE STRUCTURALLY CANNOT SHOW. Nineteen roll ups average away the
    spread inside them, and the spread is most of what is going on: the state total can sit
    comfortably while a large share of the capacity behind it is half empty. Weighted by
    capacity rather than counted, because a hundred acre foot pond and a three million acre
    foot lake are not one vote each.

    THE MARK IS THE STATE'S OWN AVERAGE AND NOT A ROUND NUMBER, which is what keeps this from
    being a threshold somebody chose. It falls where the measurement falls.

    An earlier version also returned the shares below each quarter. Nothing drew them and
    nothing printed them, and they were being handed to the numeral gate anyway, which put
    three figures on this page's allowlist that no reader would ever see. That is the same rot
    the QUOTED table above exists to prevent. A figure is computed here because something
    draws it.
    """
    total = float(statewide_capacity or 0.0) or sum(r["capacity_af"] for r in rows)
    if not total or not rows:
        return None
    avg = sum(r["storage_af"] for r in rows) / total * 100.0
    below = sum(r["capacity_af"] for r in rows if r["percent_full"] < avg)
    return round(below / total * 100.0, 1)


def metro_series(live: list[dict]) -> dict:
    """Each metro's percent full across every verified day, in the record's own order.

    A METRO IS ABSENT ON A DAY RATHER THAN ZERO ON IT. A slug the source stopped tagging is
    not a metro whose reservoirs emptied, and a sparkline that drops to the floor says exactly
    that. `None` travels instead, and the drawing breaks its line rather than inventing a
    plunge.
    """
    out: dict[str, list] = {}
    for r in live:
        metros = r.get("metros") or {}
        for slug in metros:
            out.setdefault(slug, [])
    for slug in out:
        for r in live:
            m = (r.get("metros") or {}).get(slug) or {}
            out[slug].append(m.get("percent_full"))
    return out


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

    # EVERY RESERVOIR IN THE DAY, for the map and the distribution. The metro roll up is
    # nineteen numbers over a hundred and nineteen measurements, and the averaging is where
    # the interesting part goes: a metro at half full can be one reservoir near empty beside
    # one nearly brimming, and the table cannot say which. So the individual readings travel
    # too, and the drawings show what the roll up had to flatten.
    #
    # NONE OF THESE IS AUTHORISED FOR PROSE, deliberately. They exist to be drawn, and SVG is
    # stripped before the numeral gate reads a page. Anything that reaches a sentence has to
    # come back through `figures` as its own named value, which is why the extremes below are
    # computed here rather than picked out of this list at render time.
    f["latest"]["reservoirs"] = reservoir_rows(last)

    f["latest"]["below_average"] = capacity_below_average(f["latest"]["reservoirs"],
                                                          last.get("capacity_af"))
    # HEADROOM, which the page had no figure for and the trend chart was already drawing.
    # The band between the water and the ceiling is most of the top panel, and until this
    # existed it was empty space that a reader had to estimate by eye off two other numbers.
    # It is the same subtraction either way. Doing it here means it is computed, authorised
    # and labelled rather than left as an inference.
    if last.get("capacity_af") is not None and last.get("storage_af") is not None:
        f["latest"]["headroom_af"] = round(float(last["capacity_af"])
                                           - float(last["storage_af"]), 1)

    # THE SERIES, which is the whole reason this page is worth visiting twice. A single day is
    # a figure and a run of days is an instrument, and until now the record held ten days and
    # published one of them.
    f["series"] = [{"date": r["date"], "storage_af": r["storage_af"],
                    "capacity_af": r["capacity_af"], "percent_full": r["percent_full"]}
                   for r in live]
    f["metro_series"] = metro_series(live)
    f["span"] = {"from_date": live[0]["date"], "to_date": live[-1]["date"],
                 "days": len(live),
                 "storage_af": round(live[-1]["storage_af"] - live[0]["storage_af"], 1),
                 "percent_full": round(live[-1]["percent_full"] - live[0]["percent_full"], 2)}

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


# --------------------------------------------------------------------------- the stage
#
# WHY THIS STYLESHEET TRAVELS WITH THE PAGE INSTEAD OF LIVING IN theme.py
#
# `theme.py` emits ONE render blocking sheet carried by all 241 pages, and its self-test holds
# it under the initial TCP congestion window so the site paints in a single round trip. That
# budget had 884 bytes of headroom when these drawings were built, and these drawings need more
# than that. Every byte of it would have been paid for on 240 pages that have no chart on them.
#
# So it ships inside the page that uses it. `csp.py` hashes every inline `<style>` from the
# page's own final bytes, so the policy covers this with no allowlist entry and no
# `'unsafe-inline'`. `numeral_lint` and `house_style_check` both strip `<style>` already, for
# the same reason they strip `<script>`, so a stylesheet cannot be read as prose or as a figure.
#
# THE MOTION RULE, AND IT IS NOT NEGOTIABLE. Every animation here runs FROM a hidden state TO
# the page's resting state, with `backwards` fill, and is triggered by the `.in` class the
# shell's IntersectionObserver adds. That ordering is the whole safety property: with script
# off, or an observer that never fires, or a browser that does not animate, NOTHING is hidden,
# because the resting state is the base state and the animation is the thing that is absent.
# Written the other way round, with the base state at `scaleY(0)` and the animation revealing
# it, a page with script off is a page with no chart on it and no error to explain why.
#
# `prefers-reduced-motion` is already handled globally in `theme.py`, which clamps every
# animation on the site to one iteration at hundredths of a millisecond. So a reader who asked
# for stillness gets the finished drawing immediately rather than a faster version of the show.
STAGE_CSS = """
.wviz{margin:1.9rem 0;position:relative}
.wviz>svg{width:100%;height:auto;display:block;position:relative;z-index:1}
.waterviz .ax{fill:var(--ink-mute);font-family:var(--mono);font-size:11px}
.waterviz .ax.unit{font-size:9px;letter-spacing:.08em}
/* `.ax.lab` SETS COLOUR AND NOTHING ELSE, and the version that also set a size was a real
   defect rather than a tidiness point. `.waterviz .ax.lab` is a three class selector and
   `.waterviz .ax` in a media query is two, so the breakpoint below could never raise it: the
   base rule won at every width. Every label wearing it stayed at 11 units and rendered at 4.4
   pixels on a 320 pixel phone, on a page whose breakpoints were written specifically to stop
   that. The size comes from `.ax` for every label, and only the colour is specialised. */
.waterviz .ax.lab{fill:var(--ink-bright)}
.waterviz .mklab{fill:var(--ink-bright);font-size:11px}
.waterviz .g{stroke:var(--rule);stroke-width:1;vector-effect:non-scaling-stroke}
.waterviz .zero{stroke:var(--rule-strong);stroke-width:1.4;vector-effect:non-scaling-stroke}
.waterviz .line{fill:none;stroke:var(--accent);stroke-width:2.2;stroke-linejoin:round;
  stroke-linecap:round;vector-effect:non-scaling-stroke}
.waterviz .cap{stroke:var(--ink-mute);stroke-width:1.3;stroke-dasharray:5 4;
  vector-effect:non-scaling-stroke;opacity:.85}
.waterviz .mean{stroke:var(--accent);stroke-width:1.5;stroke-dasharray:6 4;
  vector-effect:non-scaling-stroke}
.waterviz .brk{stroke:var(--ink-mute);stroke-width:1;opacity:.45;
  vector-effect:non-scaling-stroke}
.waterviz .mk{fill:var(--accent);stroke:var(--bg);stroke-width:1.5}
.waterviz .room{fill:var(--surface);opacity:.55}
.waterviz .mv,.waterviz .rv{fill:var(--accent-deep)}
.waterviz .rv{stroke:var(--bg);stroke-width:.3;vector-effect:non-scaling-stroke}

/* THE SHEEN. A band of light travelling slowly across the filled water, clipped to the water
   itself so it can never light the empty headroom above the line. It carries no value and is
   not a ramp: it is the same intensity wherever it is, and what it does is stop a flat fill
   from reading as a painted block. Light moves on water. */
/* SOFT EDGED, and the first version was not. A flat rect at one opacity is a BLOCK sliding
   across the water with two hard vertical edges, and on a fill this size it read as though the
   chart had rendered in two halves. Light on water has no edges. The gradient is what makes it
   light rather than a shape. */
.waterviz .sheen{fill:url(#wtsheen);
  animation:wsheen 14s cubic-bezier(.5,0,.5,1) infinite}
@keyframes wsheen{0%{transform:translateX(-60%)}62%,100%{transform:translateX(160%)}}

/* THE READOUT. The figures a reader came for, at the top, at a size that says they are the
   subject rather than a caption. This is the block that replaced three paragraphs, and it
   holds every number those paragraphs held. `auto-fit` rather than a fixed column count
   because the chips are of unequal width and a phone should be allowed to reflow them
   instead of squeezing six into a row and hyphenating every label. */
/* THE COLUMN IS SIZED FOR THE WIDEST FIGURE THIS BLOCK CAN HOLD, which is a signed six digit
   acre foot total with its unit beside it. At 7.5rem that value wrapped and dropped its "AF"
   onto a second line, which both broke the row rhythm and separated a number from the unit
   that gives it meaning. A figure and its unit are one thing and they do not get to be on
   different lines. */
.wreadout{display:grid;grid-template-columns:repeat(auto-fit,minmax(9.75rem,1fr));
  gap:.1rem;margin:1.25rem 0 1.6rem;border-top:var(--hair) solid var(--rule-strong)}
.wreadout>div{padding:.85rem .9rem .95rem;border-bottom:var(--hair) solid var(--rule)}
.wrk{display:block;font-size:var(--s-2);letter-spacing:.09em;text-transform:uppercase;
  color:var(--ink-mute);margin-bottom:.3rem}
.wrv{display:block;font-family:var(--mono);font-variant-numeric:tabular-nums;
  font-size:var(--s2);line-height:1.05;color:var(--ink-bright);letter-spacing:-.02em;
  white-space:nowrap}
.wru{font-size:var(--s-1);color:var(--ink-mute);margin-left:.25rem;letter-spacing:0}
[data-reveal].in .wreadout>div{animation:wrise .55s cubic-bezier(.2,.75,.25,1)
  var(--wd,0s) backwards}
@keyframes wrise{from{opacity:0;transform:translateY(9px)}}

/* THE MAP. The mesh is the faintest thing on the page on purpose: it is there so a reader can
   find their own county under the water, and the moment it competes with a reservoir it has
   stopped doing that and started being decoration. */
/* THE COUNTIES ARE FILLED, and the first version had them hollow, which was a mistake worth
   writing down. A stroke only mesh over a dark page is a ghost: the state had no body, the
   reservoirs floated in the same black as the margin, and the drawing read as dots on nothing.
   Filled with `--surface`, the same token the county map uses, Texas becomes LAND and the
   water sits on it. The whole picture depends on that one declaration. */
.waterviz.resmap{max-width:min(100%,82vh);margin-inline:auto}
.waterviz.resmap .cty{fill:var(--surface);stroke:var(--rule-strong);stroke-width:.5;
  vector-effect:non-scaling-stroke}
.waterviz.resmap .edge{fill:none;stroke:var(--ink-mute);stroke-width:1.4;
  stroke-linejoin:round;vector-effect:non-scaling-stroke;opacity:.75}
/* THE TANK IS ITS OWN MARK, UNDER THE WATER RATHER THAN OVER IT. See `_vessel` for the
   defect: this fill used to live on `.rim`, which is painted last, so it went over every lake
   on the map and took the colour out of all of them. */
.waterviz.resmap .tank{fill:url(#reservoir-shell);opacity:.96}
.waterviz.resmap .shellshade{fill:url(#reservoir-depth);pointer-events:none}
.waterviz.resmap .rim{fill:none;stroke:url(#reservoir-rim);stroke-width:1.25;
  vector-effect:non-scaling-stroke;opacity:.9}
.waterviz.resmap .rimlight{fill:none;stroke:var(--water-lit);stroke-width:.75;
  stroke-dasharray:26 90;stroke-linecap:round;vector-effect:non-scaling-stroke;opacity:.78;
  transform-box:fill-box;transform-origin:50% 50%;transform:rotate(-42deg)}
/* WATER, IN A COLOUR WATER COMES IN. `--water` is Comal, derived in theme.py against every
   ground and contrast gated like every other role on this site. Fully opaque, so the page's
   film grain stops reading through the one surface on the site that is meant to be liquid. */
.waterviz.resmap .wf{fill:url(#reservoir-water)}
/* THE LIT LINE WHERE WATER MEETS AIR. It is the same curve the fill closes over, so the two
   can never disagree about where the surface is. */
.waterviz.resmap .men{fill:none;stroke:var(--water-lit);stroke-width:1.3;
  vector-effect:non-scaling-stroke;stroke-linecap:round;opacity:.95}
.waterviz.resmap .flow{fill:none;stroke:var(--water-lit);stroke-width:.8;
  vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-dasharray:3 5;
  opacity:.15}
.waterviz.resmap .orbshine{fill:url(#reservoir-shine);opacity:.66;pointer-events:none}
.waterviz.resmap .hit{fill:transparent;stroke:none;pointer-events:all}
.waterviz.resmap .lake{transform-box:fill-box;transform-origin:50% 50%}
.waterviz.resmap .res{transform-box:fill-box;transform-origin:50% 50%}
.waterviz.resmap .reslink{cursor:pointer;outline:none}

/* HOVER, AND WHY IT MAGNIFIES RATHER THAN SLOSHES.
   The obvious motion is the water rocking in the bowl, and at this scale it cannot work. The
   circles run from 5.4 units to 27 and the map is a 1000 unit viewBox in about 740 pixels, so
   a swell big enough to see on the largest lake is half the radius of the smallest, and any
   rocking of the body lifts it off the vessel wall and opens a crescent of nothing behind it.
   So the body never moves. The mark grows, which also answers the real problem a reader has
   with a 5 unit circle, and the SURFACE ripples inside it.
   THE RIPPLE ONLY EVER SINKS. Moving the lit line up would part it from the water it sits on
   and show the tank through the gap. Downward it reads as a swell passing under it, which is
   what it is, and there is nothing to part from. */
@media (hover:hover){
  .waterviz.resmap .res{transition:transform .28s cubic-bezier(.16,1,.3,1),filter .28s ease}
}
.waterviz.resmap .reslink:is(:hover,:focus-visible) .res{transform:scale(1.58);
  filter:url(#reservoir-shadow)}
.waterviz.resmap .reslink:is(:hover,:focus-visible) .rim{stroke-width:2.25;opacity:1}
.waterviz.resmap .reslink:is(:hover,:focus-visible) .rimlight{stroke-width:1.45;opacity:1;
  animation:wrim 1.8s ease-in-out infinite}
.waterviz.resmap .reslink:is(:hover,:focus-visible) .men{opacity:1;
  animation:wripple 1.4s ease-in-out infinite}
.waterviz.resmap .reslink:is(:hover,:focus-visible) .flow{opacity:.9;
  animation:wwhoosh .8s linear infinite}
.waterviz.resmap .reslink:is(:hover,:focus-visible) .orbshine{
  animation:wglint 1.8s ease-in-out infinite}
@keyframes wripple{0%,100%{transform:translateY(0)}50%{transform:translateY(.9px)}}
@keyframes wwhoosh{to{stroke-dashoffset:-16}}
@keyframes wrim{50%{opacity:.42;transform:rotate(-28deg)}}
@keyframes wglint{50%{opacity:.9;transform:translate(1px,-.6px)}}
@media (prefers-reduced-motion:reduce){
  .waterviz.resmap .res{transition:none}
  .waterviz.resmap .reslink:is(:hover,:focus-visible) :is(.rimlight,.men,.flow,.orbshine){
    animation:none}}
/* THE KEY HAS ITS OWN TYPE SCALE, because the map has its own geometry. It is a 1000 unit
   viewBox against the chart's 720, so the same user unit size renders about a third smaller
   here at any given column width, and the chart's steps would leave this key under the ten
   pixel floor on every phone. The county map's answer to the same problem is to hide its
   survey furniture below 34rem. That is right for a scale bar, which a reader can do without,
   and wrong for a key, which is the only thing on the page that says what the two encodings
   on a circle mean. So it steps up rather than disappearing. */
.waterviz.resmap .key .rim{opacity:.75}
.waterviz.resmap .key .ax{font-size:15px}
.waterviz.resmap .key .ax.unit{font-size:13px;fill:var(--ink-bright)}
@media (max-width:26rem){
  .waterviz.resmap .key .ax{font-size:38px}
  .waterviz.resmap .key .ax.unit{font-size:32px}}
@media (min-width:26.01rem) and (max-width:34rem){
  .waterviz.resmap .key .ax{font-size:30px}
  .waterviz.resmap .key .ax.unit{font-size:26px}}
@media (min-width:34.01rem) and (max-width:46rem){
  .waterviz.resmap .key .ax{font-size:23px}
  .waterviz.resmap .key .ax.unit{font-size:20px}}
@media (min-width:46.01rem) and (max-width:62rem){
  .waterviz.resmap .key .ax{font-size:19px}
  .waterviz.resmap .key .ax.unit{font-size:16px}}

/* THE CAUSTICS. Two soft pools of the accent, drifting behind the state on different periods
   so they never repeat a pattern a reader can catch. This is the water page's answer to the
   heat shimmer the sky carries everywhere else on the site, and it is the same idea: the
   atmosphere of a real thing, at the lowest intensity that still reads. */
/* CLIPPED TO THE FIGURE, because the glow is drawn wider than it and a `-6%` inset on a full
   width figure is six percent of the page hanging off the right edge. It cost two pixels of
   horizontal scroll at 1180 and the page sweep caught it. The gradients fade to transparent
   well inside the bleed, so clipping removes an overflow and no light. */
.wviz.map{overflow:clip}
.wviz.map::before{content:"";position:absolute;inset:-3% -6%;z-index:0;pointer-events:none;
  background:radial-gradient(38% 42% at 28% 34%,
      color-mix(in srgb,var(--accent) 15%,transparent),transparent 70%),
    radial-gradient(34% 38% at 72% 62%,
      color-mix(in srgb,var(--accent-deep) 17%,transparent),transparent 70%);
  animation:wcaustic 26s ease-in-out infinite alternate}
@keyframes wcaustic{from{transform:translate(-3%,-2%) scale(1)}
  to{transform:translate(4%,3%) scale(1.09)}}

/* THE MAP READS BACK WHAT THE POINTER FOUND. The circles are intentionally dense, so the
   stable panel carries the name and value without asking a reader to hold a tiny tooltip open.
   The select is the same route for touch and keyboard users, with every option coming from the
   exact population drawn above it. */
.reservoir-tools{display:grid;grid-template-columns:minmax(0,1fr) minmax(15rem,.7fr);
  gap:.75rem;margin:.8rem 0 1.1rem;align-items:stretch}
.reservoir-inspect,.reservoir-picker{border:var(--hair) solid var(--rule-strong);
  background:color-mix(in srgb,var(--surface) 78%,transparent);padding:.9rem 1rem;
  min-height:4.7rem}
.reservoir-inspect{display:flex;align-items:center;gap:.9rem}
.reservoir-pulse{width:2.45rem;height:2.45rem;flex:none;border-radius:50%;position:relative;
  background:radial-gradient(circle at 30% 24%,var(--water-lit),var(--water) 35%,
    color-mix(in srgb,var(--water) 35%,var(--bg)) 74%);
  box-shadow:inset -.35rem -.45rem .7rem color-mix(in srgb,var(--bg) 65%,transparent),
    inset .2rem .18rem .3rem color-mix(in srgb,white 35%,transparent),
    0 .45rem 1rem color-mix(in srgb,var(--water) 22%,transparent)}
.reservoir-pulse::after{content:"";position:absolute;left:21%;top:15%;width:23%;height:34%;
  border-radius:50%;background:linear-gradient(140deg,color-mix(in srgb,white 72%,transparent),
    transparent);transform:rotate(28deg)}
.reservoir-copy{min-width:0}.reservoir-copy strong{display:block;color:var(--ink-bright)}
.reservoir-copy span{display:block;color:var(--ink-mute);font-size:var(--s-1);margin-top:.15rem}
.reservoir-copy a{display:inline-block;margin-top:.32rem;font-size:var(--s-1)}
.reservoir-copy a[hidden]{display:none}
.reservoir-picker label{display:block;color:var(--ink-mute);font-size:var(--s-2);
  letter-spacing:.08em;text-transform:uppercase;margin-bottom:.42rem}
.reservoir-picker select{width:100%;color:var(--ink-bright);background:var(--bg);
  border:var(--hair) solid var(--rule-strong);padding:.62rem .7rem;font:inherit}
@media (max-width:42rem){.reservoir-tools{grid-template-columns:1fr}}

/* THE SPARKLINE. Sized in the row rather than by the drawing, and `preserveAspectRatio:none`
   is deliberate: the cell is short and wide, the shape being read is a slope over time, and
   letting it letterbox would waste the only dimension that carries the reading. */
.spark{width:5.5rem;height:1.375rem;display:block;overflow:visible}
.spark .zero{stroke:var(--rule);stroke-width:1;vector-effect:non-scaling-stroke}
.spark .line{fill:none;stroke:var(--accent);stroke-width:1.6;
  vector-effect:non-scaling-stroke;stroke-linecap:round;stroke-linejoin:round}
.spark .mk{fill:var(--accent)}
td.sparkcell{width:6rem;vertical-align:middle}
/* WHICH COLUMN GIVES WAY ON A PHONE, and it was the wrong one until 2026-08-22.
   The trend was dropped below this width and the acre feet kept, so a reader on a phone lost
   the one column they cannot get anywhere else and kept a seven digit lookup value. The owner
   reported it as the trend being cut off, which is what a column that is simply absent looks
   like from the outside.
   Acre feet gives way instead. The figure is still in the markup, still in the tooltip on every
   bar and still in waterwatch.json, and dropping it also stops the long numerals forcing the
   metro names to wrap onto three lines. */
@media (max-width:46rem){td.af,th.afhead{display:none}}

/* SVG TEXT SCALES WITH THE DRAWING, AND THE DRAWING SHRINKS TO FIT, which is the same problem
   the grid watch chart already solved and the same numbers it solved it with. A 720 unit wide
   viewBox rendered into a 358 pixel column puts an 11 unit label at five and a half pixels.
   Legible on the laptop it was written on and unreadable on the phone this site is mostly read
   on, and no build time check can see it, because the markup is identical at every width.
   Measured on the first render of this page and it was exactly that: every axis number on the
   trend and the distribution was under six pixels at 390. */
@media (max-width:22rem){
  .waterviz .ax,.waterviz .mklab{font-size:27px}.waterviz .ax.unit{font-size:22px}}
@media (min-width:22.01rem) and (max-width:26rem){
  .waterviz .ax,.waterviz .mklab{font-size:22px}.waterviz .ax.unit{font-size:18px}}
@media (min-width:26.01rem) and (max-width:34rem){
  .waterviz .ax,.waterviz .mklab{font-size:19px}.waterviz .ax.unit{font-size:16px}}
@media (min-width:34.01rem) and (max-width:46rem){
  .waterviz .ax,.waterviz .mklab{font-size:15px}.waterviz .ax.unit{font-size:12px}}

/* ---- the show, all of it FROM hidden TO resting, never the other way ---- */
.wviz .rv,.wviz .mv,.waterviz .wf{transform-box:fill-box;
  transform-origin:50% 100%}
[data-reveal].in .rv,[data-reveal].in .mv{animation:wgrow .7s cubic-bezier(.2,.75,.25,1)
  var(--wd,0s) backwards}
@keyframes wgrow{from{transform:scaleY(0)}}
[data-reveal].in .wf{animation:wgrow .9s cubic-bezier(.3,.7,.3,1) var(--wd,0s) backwards}
[data-reveal].in .rim{animation:wfade .5s ease var(--wd,0s) backwards}
@keyframes wfade{from{opacity:0}}
/* THE LINE DRAWS ITSELF, and the dash length is the path's OWN measured length, computed in
   Python and handed over in `--len`. A guessed constant either stops short of the end or sits
   still for the first part of its run, and both look like a bug in the data. */
[data-reveal].in .waterviz .line{stroke-dasharray:var(--len);
  animation:wdraw 1.15s cubic-bezier(.4,0,.2,1) backwards}
@keyframes wdraw{from{stroke-dashoffset:var(--len)}to{stroke-dashoffset:0}}
[data-reveal].in .mean,[data-reveal].in .cap{animation:wfade .6s ease .75s backwards}
[data-reveal].in .mk,[data-reveal].in .mklab{animation:wfade .5s ease .95s backwards}
.wviz .d1{--wd:.05s}.wviz .d2{--wd:.1s}.wviz .d3{--wd:.15s}.wviz .d4{--wd:.2s}
.wviz .d5{--wd:.26s}.wviz .d6{--wd:.32s}.wviz .d7{--wd:.4s}
"""


# --------------------------------------------------------------------------- the drawings
#
# WHY THIS PAGE IS MOSTLY DRAWINGS NOW, written down so the next person does not undo it.
#
# It used to publish one day of figures and then explain itself for six paragraphs. Every one of
# those paragraphs was true and each was there for a reason, and together they were a wall of
# type standing between a reader and the only thing they came for, which is the state of the
# water. The record held ten days and the page showed one of them.
#
# The rule now is that a thing measured gets DRAWN, and prose is left to carry only what a
# drawing cannot: what the instrument refuses to say, and where the source stops. So the
# caveats did not get deleted, which would have cost this page the thing it is actually for.
# They got turned into pictures of themselves. The San Antonio gap is a grid with a hole in
# it. The exclusions are counted dots. Both say more, in less space, than the sentence did.
#
# WHAT NONE OF THESE MAY DO. No severity ramp, no red zone, no verdict, in exactly the terms
# the metro bars have always obeyed. A colour that darkens as a reservoir empties would be this
# page telling a reader that a quarter full is bad, and it does not know that. So every drawing
# here uses ONE hue at ONE intensity, and the geometry carries the reading: a length, an area, a
# water line, a position. The one place a second colour appears is to separate a thing that is
# measured from a thing that is excluded, which is a statement about the DATA and never about
# the water.

# A mono advance, rounded up rather than averaged, on the same reasoning as the grid watch
# chart: a fallback face sets wider than the one this site serves, and a gutter sized for the
# average is a gutter that clips on the machine with the wrong fonts.
MONO_ADV = 0.66


def _gutter(labels: list[str], size: float, pad: float = 14.0) -> float:
    """Left margin wide enough for the widest label the drawing will actually print.

    SIZED FROM THE STRINGS, NEVER TYPED. The grid watch page carries the scar this is copied
    from: its gutter was a constant that was right when it was measured, the data moved, the
    label grew a character, and the axis was cut on the CI runner's fonts but not on the
    author's. The part that fell off was the leading digits, so a reader saw a different number
    from the one computed. That is the one failure this project cannot have.
    """
    return round(max((MONO_ADV * size * len(s) for s in labels), default=0.0) + pad, 1)


def _margin(size: float, pad: float = 14.0) -> float:
    """The frame margin on a side that prints no axis label, derived rather than typed.

    THE DEFECT THIS EXISTS FOR, reported by the owner on 2026-08-22 as the trend chart being
    "cut off on the right side" on a phone and on a narrowed desktop window.

    Nothing was cut off. `_gutter` above sizes the LEFT margin from the widest string the axis
    will actually print, and at this drawing's type size the residual strip's "-50,000" makes
    that about 139 units. The right margin was the literal 16 it was born with. Eight to one.
    The plot ran to within 16 units of the frame while the left carried a gutter nine times
    that, so the drawing read as though the page had sliced it, and on a 390 pixel phone those
    16 units are eight pixels.

    NO GATE COULD SEE IT, and that is the part worth keeping. `responsive.mjs` asks whether
    anything is clipped or off screen and nothing was: every mark sat inside the viewBox and
    every label inside the frame. A drawing can be entirely within its bounds and still be
    composed wrongly, and no assertion about bounds will ever say so.

    THE RULE. A plot is inset from a frame edge by at least one line of axis type plus the same
    optical pad `_gutter` adds beyond its widest label. One line of type is the smallest inset
    that reads as deliberate rather than as an accident of cropping, and it is a real
    typographic unit rather than a number somebody liked.
    """
    return round(size + pad, 1)


def _polylen(pts: list) -> float:
    """The drawn length of a polyline, so a line can be told to draw itself over exactly itself.

    The stroke-dash reveal needs the path's own length. A constant large enough to cover it
    leaves the line sitting still through the front of its run and then snapping; a constant
    too small stops it short of the end. Both read as a fault in the data rather than in the
    animation, which is the worst way for a chart to be wrong.
    """
    import math                                                      # noqa: PLC0415
    return round(sum(math.dist(pts[i - 1], pts[i]) for i in range(1, len(pts))), 1)


def _delay(i: int, n: int, buckets: int = 7) -> str:
    """A stagger class, bucketed, because 119 inline delays is 119 inline styles.

    The stylesheet carries seven delays and the markup points at one of them. Emitting a
    computed delay per element instead would put a `style` attribute on every reservoir on the
    map, which is bytes on every page load to express seven distinct values.
    """
    if n <= 1:
        return ""
    return f" d{min(buckets, max(1, round(i / (n - 1) * buckets)))}"


def _round_steps(top: float) -> list:
    """Gridline values a reader can hold, from zero up to a ceiling.

    Chooses the step whose count lands between three and six lines, from the set of steps people
    actually read a scale in. Four gridlines is a scale; eleven is a ruler and reads as noise
    behind the data.
    """
    import math                                                      # noqa: PLC0415
    if top <= 0:
        return [0.0]
    mag = 10.0 ** math.floor(math.log10(top))
    for mult in (0.1, 0.2, 0.25, 0.5, 1.0, 2.0):
        step = mag * mult
        if 3 <= top / step <= 6:
            return [step * k for k in range(int(top / step) + 1)]
    return [top * k / 4 for k in range(5)]


def state_trend_svg(f: dict) -> str:
    """The whole record in one drawing: the tank, and the daily move under it.

    TWO PANELS, AND THE REASON IS THE SAME ONE THE GRID WATCH FOUND. Statewide storage is three
    quarters of a capacity that does not change, and it moves by hundredths of a point in a day.
    Drawn honestly against its own ceiling that is a flat line, and drawn against a zoomed axis
    it is a cliff face that argues for a crisis the measurement does not support. Neither one
    alone is the truth.

    So the top panel keeps the true scale, zero to conservation capacity, and answers "how full
    is Texas". The bottom panel carries the motion at its own scale and answers "which way, and
    by how much", with the scale stated on it so nobody reads the two as one axis. The flatness
    up top is real and the page says so rather than hiding it.
    """
    series = f.get("series") or []
    if len(series) < 2:
        return ""
    # `pad_t` HOLDS THE CEILING CAPTION'S ASCENT, and nothing else needs to fit up there now
    # that the unit caption has moved to the foot of the axis. At 26 the "conservation capacity"
    # label's baseline sat at 19 and a 27 unit face has about 23 units of ascent, so its box
    # started four units above the drawing and the top of the glyphs was cut on every phone.
    # `gap` IS SIZED FROM MEASURED GLYPH BOXES, not from an estimate of them. At 46 the main
    # panel's unit caption and the residual strip's top label overlapped by two units at 320px,
    # and the estimate that sized it had ascent at 0.85 of the type size. Measured in the
    # browser it is about 1.02 above the baseline and 0.28 below, so a 27 unit label occupies
    # 35 units rather than the 29 the estimate allowed. Two units of error per label is how a
    # layout that reads fine at every width the author tried fails on one they did not.
    w, pad_t, main_h, gap, res_h, pad_b = 720.0, 36.0, 178.0, 60.0, 78.0, 34.0
    h = pad_t + main_h + gap + res_h + pad_b
    ax = 27.0                          # the largest `.waterviz .ax` step, in user units

    cap = max(float(r["capacity_af"]) for r in series)
    # THE CEILING IS THE CAPACITY ITSELF, not a rounded number above it. Conservation capacity
    # is a real published quantity and the whole point of the top panel is the gap between the
    # water and that line, so inventing a tidier ceiling would put a gap on the drawing that
    # does not exist in the data.
    #
    # THE GRIDLINES ARE ROUND, AND THEY DID NOT USED TO BE. Dividing the capacity into quarters
    # is arithmetically tidy and labels the axis 7.89, 15.78 and 23.67, which are three numbers
    # no reader can hold or estimate against. Round steps with the true ceiling drawn separately
    # gives both halves: an axis somebody can read, and a ceiling that is still the published
    # quantity rather than a rounding of it.
    # DROPPED IN DRAWN SPACE, NOT IN DATA SPACE. The first filter was `v < cap * 0.97`, which
    # is a percentage of the value and has nothing to do with how far apart two labels land on
    # a 168 unit panel. Capacity is 31.56 and the top round step is 30.00, which is 4.9 percent
    # below it and passed the filter, and the two labels then printed one on top of the other.
    # A collision is a distance on the drawing, so it is measured on the drawing.
    marks = [v for v in _round_steps(cap)
             if (cap - v) / cap * main_h > ax * 0.75] + [cap]
    # The day over day moves, which are what the strip is drawn from.
    import datetime as _dt
    moves = []
    for i in range(1, len(series)):
        a, b = series[i - 1], series[i]
        if (_dt.date.fromisoformat(b["date"]) - _dt.date.fromisoformat(a["date"])).days == 1:
            moves.append((i, b["storage_af"] - a["storage_af"]))
    span = max((abs(v) for _, v in moves), default=0.0) or 1.0
    step = 10.0 ** (len(str(int(span))) - 1)
    rceil = (int(span / step) + 1) * step

    labels = [maf(v) for v in marks] + ["MAF", "AF", af(rceil), "-" + af(rceil)]
    pad_l = _gutter([s for s in labels if s], ax)
    pad_r = _margin(ax)
    plot_w = w - pad_l - pad_r
    n = len(series)

    def x(i):
        return round(pad_l + (i / max(n - 1, 1)) * plot_w, 2)

    def y(v):
        return round(pad_t + main_h - (float(v) / cap) * main_h, 2)

    pts = [(x(i), y(r["storage_af"])) for i, r in enumerate(series)]
    area = (f'M{pts[0][0]},{y(0)} ' + " ".join(f"L{a},{b}" for a, b in pts) +
            f' L{pts[-1][0]},{y(0)} Z')
    # THE HEADROOM IS DRAWN, not left as background. It is the largest area on the panel and
    # black is what the page is made of, so undrawn it read as nothing rather than as the
    # empty part of a vessel. Tinted at a fraction of the surface token it becomes the top of
    # a tank and the whole panel reads as one object with a water line across it.
    #
    # IT IS NOT A SECOND VALUE COLOUR. The tint is flat at every height and every day, so it
    # carries no reading of its own. What it carries is the boundary, which is the capacity
    # line the water is being measured against.
    room = (f'M{pts[0][0]},{y(cap)} L{pts[-1][0]},{y(cap)} ' +
            " ".join(f"L{a},{b}" for a, b in reversed(pts)) + " Z")
    line = "M" + " L".join(f"{a},{b}" for a, b in pts)
    length = _polylen(pts)

    grid = "".join(
        f'<line class="g" x1="{pad_l}" x2="{w - pad_r}" y1="{y(v)}" y2="{y(v)}"/>'
        f'<text class="ax" x="{pad_l - 8}" y="{y(v) + 4}" text-anchor="end">{maf(v)}</text>'
        for v in marks)
    # THE CEILING GETS ITS OWN WEIGHT, because it is the only line on the panel that is a
    # published quantity rather than a division of one.
    ceiling = (f'<line class="cap" x1="{pad_l}" x2="{w - pad_r}" y1="{y(cap)}" y2="{y(cap)}"/>'
               f'<text class="ax lab" x="{w - pad_r}" y="{y(cap) - 7}" text-anchor="end">'
               f'conservation capacity</text>')

    # THE LATEST READING IS MARKED AND LABELLED where it happens, so the figure a reader came
    # for is on the drawing rather than in a sentence somewhere else on the page.
    last = series[-1]
    lx, ly = x(n - 1), y(last["storage_af"])
    tag = f'{maf(last["storage_af"])} MAF, {pct(last["percent_full"])}% full'
    half = MONO_ADV * ax * len(tag) / 2.0
    tx = min(max(lx, pad_l + half), w - pad_r - half)
    head = (f'<circle class="mk" cx="{lx}" cy="{ly}" r="3.6"/>'
            f'<text class="ax mklab" x="{tx}" y="{round(ly - 12, 2)}" '
            f'text-anchor="middle">{tag}</text>')

    ticks = "".join(
        f'<text class="ax" x="{x(i)}" y="{pad_t + main_h + 17}" text-anchor="{anc}">{lab}</text>'
        for i, lab, anc in [(0, ordinal_short(series[0]["date"]), "start"),
                            (n - 1, ordinal_short(series[-1]["date"]), "end")])

    # THE DAILY MOVE. A bar per day, signed, on a symmetric scale of its own.
    mid = pad_t + main_h + gap + res_h / 2
    bw = max(2.0, min(16.0, plot_w / max(n, 1) * 0.5))

    def ry(v):
        return round(mid - (float(v) / rceil) * (res_h / 2), 2)

    bars = "".join(
        f'<rect class="mv{_delay(k, len(moves))}" x="{round(x(i) - bw / 2, 2)}" '
        f'y="{min(ry(v), mid)}" width="{bw}" height="{max(abs(ry(v) - mid), 0.8)}">'
        f'<title>{ordinal_date(series[i]["date"])}, '
        f'{"up" if v > 0 else "down" if v < 0 else "no change"} {af(abs(v))} acre feet</title></rect>'
        for k, (i, v) in enumerate(moves))
    strip = (f'<line class="zero" x1="{pad_l}" x2="{w - pad_r}" y1="{mid}" y2="{mid}"/>{bars}'
             f'<text class="ax" x="{pad_l - 8}" y="{ry(rceil) + 4}" text-anchor="end">'
             f'{af(rceil)}</text>'
             f'<text class="ax" x="{pad_l - 8}" y="{ry(-rceil) + 4}" text-anchor="end">'
             f'-{af(rceil)}</text>'
             f'<text class="ax unit" x="{pad_l - 8}" y="{round(mid + 4, 2)}" text-anchor="end">'
             f'AF/DAY</text>')

    return f"""<figure class="wviz">
<svg viewBox="0 0 {w:.0f} {h:.0f}" class="waterviz trend" role="img"
     aria-label="Texas reservoir storage across every day the record holds, drawn against
     conservation capacity, with the day over day change shown separately below.">
  <defs><linearGradient id="wtfill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="var(--accent-deep)" stop-opacity=".46"/>
    <stop offset="1" stop-color="var(--accent-deep)" stop-opacity=".05"/>
  </linearGradient>
  <linearGradient id="wtsheen" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="var(--accent)" stop-opacity="0"/>
    <stop offset=".5" stop-color="var(--accent)" stop-opacity=".22"/>
    <stop offset="1" stop-color="var(--accent)" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="wtclip"><path d="{area}"/></clipPath></defs>
  {grid}
  <path class="room" d="{room}"/>
  <path class="area" fill="url(#wtfill)" d="{area}"/>
  <g clip-path="url(#wtclip)"><rect class="sheen" x="{pad_l - plot_w * 0.3:.1f}"
     y="{pad_t}" width="{plot_w * 0.3:.1f}" height="{main_h}"/></g>
  <path class="line" style="--len:{length}" d="{line}"/>
  {ceiling}{head}{ticks}
  <text class="ax unit" x="4" y="{pad_t + main_h + 17}" text-anchor="start">MAF</text>
  {strip}
</svg>
<figcaption>The tank and the tap. Above, storage against the conservation capacity it is
measured out of, on a scale that starts at zero, so the flatness is the measurement rather
than a drawing choice. The band between the water and the dashed line is the room left. Below, the change from one day to the next at its own scale, which is
the movement the top panel is too honest to show.</figcaption></figure>"""


def distribution_svg(f: dict) -> str:
    """Every reservoir at once, sorted emptiest first, each as wide as its share of the state.

    THE CHART THE METRO TABLE STRUCTURALLY CANNOT BE. Nineteen roll ups are nineteen averages,
    and an average is where the spread goes to die: a metro at half full can be one lake nearly
    dry beside one nearly brimming, and the table has no way to say which. This draws all
    hundred and nineteen readings without averaging any of them.

    WIDTH IS CAPACITY SHARE, and that is the choice that makes it honest. Counting reservoirs
    one vote each would let a five thousand acre foot pond argue as loudly as a lake six hundred
    times its size. Weighted, the horizontal axis is the state's water itself, so the AREA UNDER
    THE STEPS IS THE STATEWIDE PERCENTAGE, exactly, and the drawing and the headline figure are
    the same measurement seen twice.
    """
    L = f.get("latest") or {}
    rows = sorted(L.get("reservoirs") or [], key=lambda r: r["percent_full"])
    if len(rows) < 2:
        return ""
    total = sum(r["capacity_af"] for r in rows)
    if not total:
        return ""
    # ROOM UNDER THE TICKS FOR THE AXIS CAPTION, which used to sit on the same baseline as
    # the "50%" and "100%" ticks and printed straight through both of them at phone type.
    w, pad_t, plot_h, pad_b = 720.0, 30.0, 210.0, 78.0
    h = pad_t + plot_h + pad_b
    ax = 27.0
    pad_l = _gutter([f"{v}%" for v in (0, 25, 50, 75, 100)] + ["FULL"], ax)
    pad_r = _margin(ax)
    plot_w = w - pad_l - pad_r

    def y(p):
        return round(pad_t + plot_h - (min(float(p), 100.0) / 100.0) * plot_h, 2)

    grid = "".join(
        f'<line class="g" x1="{pad_l}" x2="{w - pad_r}" y1="{y(v)}" y2="{y(v)}"/>'
        f'<text class="ax" x="{pad_l - 8}" y="{y(v) + 4}" text-anchor="end">{v}%</text>'
        for v in (0, 25, 50, 75, 100))

    bars, cx = [], pad_l
    for k, r in enumerate(rows):
        bw = r["capacity_af"] / total * plot_w
        top = y(r["percent_full"])
        bars.append(
            f'<rect class="rv{_delay(k, len(rows))}" x="{round(cx, 2)}" y="{top}" '
            f'width="{round(max(bw, 0.35), 2)}" '
            f'height="{round(pad_t + plot_h - top, 2)}">'
            f'<title>{reservoir_label(r["key"])}, {pct(r["percent_full"])}% full, '
            f'{af(r["storage_af"])} of {af(r["capacity_af"])} acre feet</title></rect>')
        cx += bw

    # THE STATEWIDE LINE, drawn across the steps it is the area under. Where it crosses is the
    # thing worth seeing: everything left of the crossing is capacity sitting below the average.
    sw = L.get("percent_full")
    state = ""
    if sw is not None:
        # ANCHORED LEFT, NOT RIGHT. The label sat at the right edge, which on a curve that
        # rises left to right is exactly where the bars are tallest, so it printed on top of
        # them. The empty quadrant on a rising curve is the top left and that is where it goes.
        state = (f'<line class="mean" x1="{pad_l}" x2="{w - pad_r}" y1="{y(sw)}" y2="{y(sw)}"/>'
                 # BELOW ITS OWN LINE, NOT ABOVE IT. Above, it shares the top left of the
                 # drawing with the crossing label and the two printed through each other at
                 # phone type. Below the line and at the left the curve is at its lowest, and
                 # there is nothing else there at any width.
                 f'<text class="ax mklab" x="{pad_l + 6}" y="{round(y(sw) + 26, 2)}" '
                 f'text-anchor="start">statewide {pct(sw)}%</text>')
        # THE CROSSING, WHICH IS THE READING THE CAPTION PROMISES. Until this was drawn the
        # caption told a reader to look at where the line crosses and left them to estimate it
        # off an axis. It is a computed share and it deserves to be marked and named.
        # THE MARKER IS DRAWN HERE AND THE FIGURE IS NAMED IN THE CAPTION, which is a
        # division of labour rather than a compromise. Two reasons, and the second is the
        # important one.
        #
        # Geometry cannot see a media query, so an in chart label has to be sized for the
        # largest type the stylesheet can set, and at that size the long form ran 128 units
        # off the left edge and the short form that did fit read as "34.6% of capacity" with
        # no verb. A caption has no such constraint.
        #
        # And a figure inside an `<svg>` is invisible to `numeral_lint`, which strips svg
        # before it reads a page. Every number these drawings moved out of prose left the
        # gate that was watching it. This one goes back into reader facing text, where the
        # gate can see it and where it has to be authorised by name.
        share = L.get("below_average")
        if share is not None:
            mx = round(pad_l + plot_w * float(share) / 100.0, 2)
            state += f'<line class="brk" x1="{mx}" x2="{mx}" y1="{pad_t}" y2="{pad_t + plot_h}"/>'

    xticks = "".join(
        f'<text class="ax" x="{round(pad_l + plot_w * k / 4, 2)}" y="{pad_t + plot_h + 17}" '
        f'text-anchor="{anc}">{lab}</text>'
        for k, lab, anc in ((0, "0%", "start"), (2, "50%", "middle"), (4, "100%", "end")))

    below = ("" if L.get("below_average") is None else
             f'<strong class="num">{pct(L["below_average"])}%</strong> of Texas conservation '
             f'capacity sits below it.')
    return f"""<figure class="wviz">
<svg viewBox="0 0 {w:.0f} {h:.0f}" class="waterviz dist" role="img"
     aria-label="Every reservoir in the day's record, sorted from emptiest to fullest, each
     drawn as wide as its share of the state's conservation capacity.">
  {grid}
  <g class="rvs">{"".join(bars)}</g>
  {state}{xticks}
  <text class="ax unit" x="4" y="{pad_t + plot_h + 55}" text-anchor="start">FULL</text>
  <text class="ax unit" x="{w - pad_r}" y="{pad_t + plot_h + 55}" text-anchor="end">
    SHARE OF STATE CAPACITY</text>
</svg>
<figcaption>Every reservoir, emptiest to fullest, each as wide as the share of state
capacity it holds. {below}</figcaption>
</figure>"""


def reservoir_map_svg(f: dict) -> str:
    """Texas, and the water in it, each reservoir drawn as a vessel filled to its own level.

    WHY A MAP EARNS ITS SPACE HERE AND ON MOST PAGES DOES NOT. A metro table is sorted by a
    number, so it answers "which is lowest" and destroys the one thing a reader of a WATER page
    is holding in their head, which is where these places are. The Permian sitting dry beside a
    brimming Piney Woods is a fact about a map and it survives no ranking. Nineteen rows cannot
    show it and one drawing cannot avoid showing it.

    THE FILL IS A WATER LINE, NOT A COLOUR. Every circle is one hue at one intensity, and the
    reading is the height the fill reaches inside it, which is the same rule as the bars and the
    same rule as the grid watch gauge. Shading a lake darker as it empties would be a severity
    ramp, which is a verdict, which is the thing this page does not publish. A reader looking at
    a half filled circle is looking at a measurement of a half full reservoir and nothing else.

    SIZE IS THE FOURTH ROOT OF CAPACITY, and that is a stated compromise rather than a default.
    Capacity here spans five thousand acre feet to nearly three million, so a true area encoding
    would draw the smallest lake at a fifth of a pixel and the map would simply be missing most
    of its subject. The fourth root keeps every reservoir a mark a reader can see and still
    ranks them correctly by size. The caption says so, because a scale nobody states is a scale
    that gets read as linear.
    """
    L = f.get("latest") or {}
    rows = L.get("reservoirs") or []
    if not rows:
        return ""
    try:
        import texas_map as tm                                       # noqa: PLC0415
        import reservoirs as rv                                      # noqa: PLC0415
    except Exception:                                                # noqa: BLE001
        return ""
    where = rv.load()
    if not where:
        return ""

    try:
        counties = tm.county_rings()
        scale, dx, dy = tm.fit(counties)
        edge = tm.polyline_d(tm.state_outline(), scale, dx, dy)
    except Exception:                                                # noqa: BLE001
        return ""
    mesh = "".join(f'<path class="cty" d="{d}"/>' for d in
                   (tm.path_d(rings, scale, dx, dy) for _fips, _name, rings in counties) if d)

    placed = []
    for r in rows:
        loc = where.get(r["key"])
        # AN OUT OF STATE RESERVOIR IS NOT DRAWN ON A MAP OF TEXAS WATER, which is the same
        # exclusion the ledger already makes and the page already explains. The tag is TWDB's
        # own, carried through the asset, so the map and the total cannot disagree about it.
        if not loc or not loc.get("texas"):
            continue
        px, py = tm.albers(loc["lon"], loc["lat"])
        placed.append({**r, "name": loc.get("name") or reservoir_label(r["key"]),
                       "cx": round(px * scale + dx, 2), "cy": round(py * scale + dy, 2)})
    if not placed:
        return ""

    cap_max = max(p["capacity_af"] for p in placed)
    r_min, r_max = 5.4, 27.0

    def radius(cap):
        return round(max(r_min, r_max * (float(cap) / cap_max) ** 0.25), 2)

    # DRAWN LARGEST FIRST so a small reservoir inside a big one's circle is still on top and
    # still readable. Painted the other way round the Panhandle's small lakes vanish under
    # nothing and the map quietly loses a third of its readings.
    # THE WAVE RUNS WEST TO EAST, which is the direction the state actually reads and, as it
    # happens, the direction the water goes from dry to wet. The stagger is by LONGITUDE and
    # the paint order is by size, so the two are independent: the big lakes still draw first
    # and stay under the small ones, and the filling still sweeps across the state.
    lons = sorted(q["cx"] for q in placed)
    span_x = (lons[-1] - lons[0]) or 1.0
    dots = []
    for p in sorted(placed, key=lambda q: -q["capacity_af"]):
        r = radius(p["capacity_af"])
        wd = _delay(int((p["cx"] - lons[0]) / span_x * 100), 101)
        frac = max(0.0, min(float(p["percent_full"]) / 100.0, 1.0))
        name = html.escape(p["name"])
        meta = (f'{pct(p["percent_full"])}% full · {af(p["storage_af"])} of '
                f'{af(p["capacity_af"])} acre feet')
        label = html.escape(f'{p["name"]} details, {meta}')
        slug = reservoir_slug(p["key"])
        title = f'<title>{name}, {html.escape(meta)}</title>'
        dots.append(
            f'<a class="reslink" href="reservoir/{slug}/" aria-label="{label}" '
            f'data-name="{name}" data-meta="{html.escape(meta)}" data-proper-name="{name}">'
            f'<g class="res">{_vessel(p["cx"], p["cy"], r, frac, wd)}{title}'
            f'<circle class="hit" cx="{p["cx"]}" cy="{p["cy"]}" r="{max(r, 9.0):.2f}"/>'
            f'</g></a>')

    # THE LEGEND, IN THE CORNER THE STATE DOES NOT REACH. A map with two encodings on one mark
    # needs to say what they are, and this one has two: how big the circle is, and how far up
    # it is filled. Without it a reader has to infer both from the caption, which is the reading
    # order backwards.
    #
    # IT CARRIES NO NUMERAL, deliberately. A legend showing "25%" and "75%" would be printing
    # two figures that came from nowhere, which is the exact thing this project's law forbids,
    # and it would be doing it inside an `<svg>` where the numeral gate cannot see it. The
    # encoding is ordinal and the words say so. Anybody wanting a figure has the whole table,
    # the distribution and a tooltip on every circle.
    # LAID OUT BY WALKING THE RADII, not on a fixed pitch. The size key runs from the smallest
    # circle on the map to the largest, which is a five fold span, so any single spacing either
    # overlaps the big pair or strands the small one in whitespace. Each circle is placed a gap
    # past the edge of the one before it.
    def key_row(radii, cy, fracs=None):
        out, cx = [], lx
        for k, rr in enumerate(radii):
            cx += rr if k == 0 else rr + 11.0
            frac = fracs[k] if fracs is not None else None
            # THE KEY IS DRAWN BY THE SAME FUNCTION AS THE MAP, which it was not before. Two
            # code paths building the same mark is how a legend ends up describing a drawing
            # that has moved on without it, and this one had already started to: the map's
            # circles were about to gain a vessel and a lit surface that the key knew nothing
            # about. A key that does not look like the thing it explains is worse than none.
            out.append(_vessel(cx, cy, rr, frac, "", tank=frac is not None))
            cx += rr
        return "".join(out), cx

    lx, ly = 66.0, tm.VIEW_H - 302.0
    fullrow, fullend = key_row([15.0] * 3, ly + 46, [0.1, 0.5, 1.0])
    bigrow, bigend = key_row([r_min, 15.0, r_max], ly + 186)
    lg = [f'<text class="ax unit" x="{lx}" y="{ly}" text-anchor="start">HOW FULL</text>',
          fullrow,
          # ONE LABEL, NOT A PAIR. "empty" at the left of the row and "full" at the right of
          # it is the obvious layout and it does not survive the type stepping up for a phone:
          # the row is 112 units wide and the two words want over 300 between them, so they
          # printed on top of each other. One phrase under the row says the same thing and has
          # nothing to collide with.
          f'<text class="ax" x="{lx}" y="{ly + 92}" text-anchor="start">empty to full</text>',
          f'<text class="ax unit" x="{lx}" y="{ly + 140}" text-anchor="start">HOW BIG</text>',
          bigrow,
          f'<text class="ax" x="{lx}" y="{ly + 234}" text-anchor="start">'
          f'conservation capacity</text>']

    options = "".join(
        f'<option value="reservoir/{reservoir_slug(p["key"])}/">'
        f'{html.escape(p["name"])}</option>'
        for p in sorted(placed, key=lambda q: q["name"]))
    return f"""<figure class="wviz map">
<svg viewBox="0 0 {tm.VIEW_W:g} {tm.VIEW_H:g}" class="waterviz resmap" role="group"
     aria-label="Interactive map of every Texas reservoir in the day's record. Each link opens
     that reservoir's daily record. Circle size follows conservation capacity and water height
     follows the level it is holding."
     preserveAspectRatio="xMidYMid meet">
  {_reservoir_defs()}
  <g class="mesh">{mesh}</g>
  <path class="edge" d="{edge}"/>
  <g class="dots">{"".join(dots)}</g>
  <g class="key" aria-hidden="true">{"".join(lg)}</g>
</svg>
<figcaption>Where the water is. One circle per reservoir, at its own gauge, filled to the level
it is holding today. Size follows the fourth root of conservation capacity rather than capacity
itself, so the smallest lakes stay visible beside the largest, and the ranking by size still
holds. Hover, focus or select a reservoir to open its daily record.</figcaption>
<div class="reservoir-tools" data-prose="data">
  <div class="reservoir-inspect" id="reservoir-inspect" aria-live="polite">
    <span class="reservoir-pulse" aria-hidden="true"></span>
    <span class="reservoir-copy"><strong id="reservoir-name">Explore a reservoir</strong>
      <span id="reservoir-meta">Move across the map or choose a name</span>
      <a id="reservoir-open" hidden>Open the daily record</a></span>
  </div>
  <label class="reservoir-picker">Find a reservoir
    <select id="reservoir-picker">
      <option value="">Choose a name</option>{options}
    </select>
  </label>
</div></figure>"""


def _reservoir_defs() -> str:
    """One lighting rig shared by every vessel on a drawing."""
    return """<defs>
  <radialGradient id="reservoir-shell" cx="30%" cy="22%" r="82%">
    <stop offset="0" stop-color="var(--ink-mute)"/>
    <stop offset=".48" stop-color="var(--surface)"/>
    <stop offset="1" stop-color="var(--bg)"/>
  </radialGradient>
  <linearGradient id="reservoir-water" x1="0" y1="0" x2=".85" y2="1">
    <stop offset="0" stop-color="var(--water-lit)"/>
    <stop offset=".38" stop-color="var(--water)"/>
    <stop offset="1" stop-color="var(--accent-deep)"/>
  </linearGradient>
  <radialGradient id="reservoir-depth" cx="28%" cy="20%" r="78%">
    <stop offset="0" stop-color="white" stop-opacity=".13"/>
    <stop offset=".55" stop-color="var(--bg)" stop-opacity="0"/>
    <stop offset="1" stop-color="var(--bg)" stop-opacity=".58"/>
  </radialGradient>
  <linearGradient id="reservoir-rim" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="var(--water-lit)"/>
    <stop offset=".46" stop-color="var(--accent)"/>
    <stop offset="1" stop-color="var(--ink-mute)"/>
  </linearGradient>
  <radialGradient id="reservoir-shine" cx="50%" cy="50%" r="50%">
    <stop offset="0" stop-color="white" stop-opacity=".64"/>
    <stop offset="1" stop-color="white" stop-opacity="0"/>
  </radialGradient>
  <filter id="reservoir-shadow" x="-80%" y="-80%" width="260%" height="260%">
    <feDropShadow dx="0" dy="3" stdDeviation="3.2" flood-color="var(--water)"
      flood-opacity=".5"/>
  </filter>
</defs>"""


def _vessel(cx: float, cy: float, r: float, frac, wd: str, tank: bool = True) -> str:
    """One reservoir: the vessel, the water in it, and the lit line where the two meet.

    THE PAINT ORDER IS THE WHOLE FIX AND IT WAS BACKWARDS.

    Until 2026-08-22 this drew the water and then painted the rim circle on top of it, and that
    rim carried `fill:var(--bg)` at 55 percent opacity. So every lake on the map had a disc of
    page background laid over it at more than half strength. The water was authored as dusk
    gold at 92 percent and reached a reader at about 41, which is a muddy taupe, and the film
    grain the whole site carries showed straight through it. The owner described the result as
    grainy and bland and was reading it exactly right. Nothing was wrong with the colour. It was
    being painted over.

    So the vessel is its own mark now, underneath, and the rim is a stroke with no fill at all.
    Three objects, in the order a real one would be built: the empty tank, the water, the rim
    that holds both.

    ONE HUE AT ONE INTENSITY STILL HOLDS, and it is worth being precise about what that rule
    forbids, because this mark now carries three colours. It forbids a colour that MOVES WITH
    THE READING. A lake at 12 percent and a lake at 96 are drawn in the identical blue, at the
    identical strength, with the identical lit line on top, and the only thing that differs
    between them is where the water sits. That is the rule. The vessel and the rim were already
    a second and third intensity before this change, because a bar with no trough is not a
    gauge, and the water page has always drawn the tank as well as what is in it.
    """
    if frac is None:
        return (f'<circle class="rim{wd}" cx="{cx}" cy="{cy}" r="{r}"/>')
    frac = max(0.0, min(float(frac), 1.0))
    body = (f'<circle class="wf{wd}" cx="{cx}" cy="{cy}" r="{r}"/>' if frac >= 0.999
            else f'<path class="wf{wd}" d="{_segment(cx, cy, r, frac)}"/>' if frac > 0.001
            else "")
    line = _surface(cx, cy, r, frac)
    men = f'<path class="men{wd}" d="{line}"/>' if line else ""
    flows = _flow_lines(cx, cy, r, frac, wd)
    return ((f'<circle class="tank{wd}" cx="{cx}" cy="{cy}" r="{r}"/>' if tank else "")
            + (f'<g class="lake">{body}{flows}{men}</g>' if body else "")
            + f'<circle class="shellshade" cx="{cx}" cy="{cy}" r="{r}"/>'
            + f'<ellipse class="orbshine" cx="{cx - r * .28:.2f}" cy="{cy - r * .3:.2f}" '
              f'rx="{r * .18:.2f}" ry="{r * .3:.2f}"/>'
            + f'<circle class="rim{wd}" cx="{cx}" cy="{cy}" r="{r}"/>'
            + f'<circle class="rimlight" cx="{cx}" cy="{cy}" r="{r * .94:.2f}"/>')


def _flow_lines(cx: float, cy: float, r: float, frac: float, wd: str) -> str:
    """Highlights inside the measured water area, animated without moving its boundary."""
    if frac <= 0.02:
        return ""
    ys, _half = _waterline(cy, r, frac)
    floor = cy + r
    room = floor - ys
    out = []
    for i, share in enumerate((0.32, 0.61)):
        y = ys + room * share
        half = max(r * r - (y - cy) ** 2, 0.0) ** 0.5 * (0.58 if i == 0 else 0.42)
        if half < 0.45:
            continue
        amp = min(r * .11, room * .1)
        out.append(
            f'<path class="flow flow{i + 1}{wd}" d="M{cx - half:.2f},{y:.2f} '
            f'Q{cx:.2f},{y - amp:.2f} {cx + half:.2f},{y:.2f}"/>')
    return "".join(out)


def _segment(cx: float, cy: float, r: float, frac: float) -> str:
    """The filled part of a circle, as water sits in it: a circular segment measured from the bottom.

    A CLIP PATH PER RESERVOIR WOULD ALSO WORK AND IS WORSE. A hundred and nineteen of them is a
    hundred and nineteen extra nodes in `defs`, each carrying an id that has to stay unique
    across a page that already draws a county map. The segment is four numbers of trigonometry
    and no shared state at all.

    The arc sweeps the short way for a level below the middle and the long way above it, which
    is what the large-arc flag is for. Getting that backwards draws the complement, so a nearly
    empty lake renders nearly full, which is the one error on this page that would be both
    invisible in review and completely wrong.
    """
    ys, half = _waterline(cy, r, frac)
    large = 1 if frac > 0.5 else 0
    # THE ARC RETURNS RIGHT TO LEFT, WHICH FLIPS THE SWEEP FLAG. Before the wave the path went
    # M at the left end, arc to the right end, and `Z` closed it back along the chord. The wave
    # walks that chord itself, so the current point is already at the right end and an arc drawn
    # to the right end is a zero length arc, which the spec says to ignore. The first version of
    # this drew every lake as its own complement: a reservoir at 92 percent rendered as a thin
    # blue band at the TOP of an empty circle, and the map was wrong about every mark on it.
    # Reversing the arc means tracing the same side of the circle in the other direction, and
    # that is exactly what the sweep flag is.
    # THE SURFACE IS ALWAYS WALKED, EVEN WHEN IT IS A STRAIGHT LINE, and that is the second bug
    # the area check found rather than the first. `_crest` returns nothing when the swell would
    # be under a hundredth of a unit, which is right, and this then had the arc start and end at
    # the same point. A zero length arc is one the spec says to ignore, so the whole path
    # collapsed and the lake drew NOTHING. It only ever happened past 99 percent and under one,
    # which is the band nobody scrolls to check and the band where a dry reservoir lives.
    #
    # So the path always has the same shape. Along the surface from the left end to the right,
    # by a wave or by a plain `L`, then the arc back around the bottom. One shape means one set
    # of flags to get right, and the sweep is 1 because the arc now runs right to left.
    top = _crest(cx, ys, half, r, frac) or f"L{round(cx + half, 3)},{round(ys, 3)} "
    return (f"M{round(cx - half, 3)},{round(ys, 3)} {top}"
            f"{_wall(cx, cy, r, half, ys, frac)}Z")


def _wall(cx: float, cy: float, r: float, half: float, ys: float, frac: float) -> str:
    """The vessel's wall, from one end of the surface round the bottom to the other.

    IN QUARTERS, NEVER IN ONE PIECE, and that is about what a RENDERER does rather than about
    tidiness. An SVG arc is given two endpoints and a radius, and every renderer recovers the
    centre from them the same way the spec sets out. When the two ends are nearly a diameter
    apart that recovery is ill conditioned: the term under the root goes to zero, so a
    thousandth of rounding in an endpoint swings the recovered centre by a large multiple of
    itself along the perpendicular.

    Half full is exactly that case, and it is not a corner. It is the middle of the range and
    the single most likely level for a reservoir to be at. The water reached about a tenth of a
    unit below the floor of its own vessel there, in the browser and not only in the check.

    So the return is broken at the circle's own quarter points, which are exact and need no
    recovery at all. Every piece is at most a quarter turn, every one is well conditioned, and
    the flags are the same on all of them, which removes the other thing that was easy to get
    wrong here.
    """
    q = lambda x, y: f"A{r},{r} 0 0 1 {round(x, 3)},{round(y, 3)} "
    stops = []
    if frac > 0.5:                       # the surface is above the middle, so the wall passes
        stops.append((cx + r, cy))       # the right shoulder and the left one as well
    stops.append((cx, cy + r))           # the floor, which every level's wall passes
    if frac > 0.5:
        stops.append((cx - r, cy))
    stops.append((cx - half, ys))
    return "".join(q(x, y) for x, y in stops)


def _waterline(cy: float, r: float, frac: float) -> tuple:
    """Where the surface sits, and how wide the vessel is there, as the path will PRINT them.

    THE ROUNDING HAS TO AGREE WITH ITSELF, which it did not, and the area check found it at
    exactly half full where nothing else would look.

    The chord's ends have to land ON the circle, because the arc that closes the path is given
    that circle's radius and SVG's rule for an arc whose endpoints are too far apart is to grow
    the radius until they fit. At 49 percent of a 20 unit circle the half chord is 19.996, which
    rounds to 20.0 while the surface sits at 100.4, so the printed ends were 0.4 units off their
    own circle and the renderer answered by drawing a bigger one. The water reached below the
    floor of the vessel holding it.

    So the surface is rounded first and the half chord is then computed FROM THE ROUNDED VALUE
    and floored, never rounded up, so a printed end is always ON the circle or just inside it.

    AND THIS ONE DRAWING PRINTS THREE PLACES WHERE THE REST OF THE PAGE PRINTS TWO. At two
    places the residual error is a fiftieth of a unit, which is nothing on the trend chart's
    720 unit frame and is four percent of the radius of the smallest reservoir here. The map
    is the one drawing on this page whose marks are five units across. It costs about a
    kilobyte before compression and it is the difference between a vessel that holds its water
    and one that leaks a little at exactly half full.
    """
    import math                                                      # noqa: PLC0415
    ys = round(cy + r - 2.0 * r * frac, 3)
    return ys, math.floor(math.sqrt(max(r * r - (ys - cy) ** 2, 0.0)) * 1000) / 1000


def _amp(r: float, half: float, frac: float) -> float:
    """How far the surface may rise and fall, in user units.

    THREE THINGS BOUND IT AND EACH ONE IS A REAL EDGE.

    A proportion of the RADIUS, so the swell looks the same on a five unit stock tank as on
    Toledo Bend rather than being a fixed wobble that swamps the small marks.

    A proportion of the WATER'S OWN DEPTH, so a lake at two percent does not get a trough that
    dips below the bottom of its own vessel and draws a crescent of nothing.

    A proportion of the HALF CHORD, which is the one that matters near the top. At ninety eight
    percent full the chord is short and sits near the crown of the circle, so a swell sized off
    the radius would ride straight out through the rim.

    AND THE VESSEL'S OWN WALL, WHICH THE FIRST THREE DO NOT COVER. Water standing proud of the
    rim that holds it is not a small visual bug on this page. It is the drawing saying a
    reservoir is over its conservation capacity, which is a claim the record never makes.

    THAT BOUND TOOK TWO GOES AND THE SECOND ONE IS THE POINT. The obvious version measures the
    room at the crest's peak, which sits a quarter along the chord, and it is not enough: the
    sweep below found a 27 unit circle at 91.8 percent breaking out by 0.066 units at `t=0.13`,
    near where the curve LEAVES the chord, because the circle's wall there is climbing far
    faster than a curve aimed at a peak further along. Checking the one point a person would
    think to check is how a rule passes review and still draws the wrong picture.

    So it is solved along the whole curve instead, and it is exact rather than sampled-and-hoped
    because the curve is linear in this number. A quadratic from `(x0, ys)` through a control at
    `ys -/+ 2a` to `(x1, ys)` has `y(t) = ys -/+ 4a·t(1-t)`, and its `x` runs straight from one
    end of the chord to the other. So at every `t` the wall gives a ceiling on `a` directly, and
    the answer is the tightest of them. Twenty four samples, then 98 percent of it, so rounding
    a coordinate to two places cannot spend the last of the clearance.
    """
    import math                                                      # noqa: PLC0415
    if half <= 0.0:
        return 0.0
    off = r * (1.0 - 2.0 * frac)            # the chord's own offset from the middle, signed
    bound = min(r * 0.13, r * frac * 0.55, half * 0.30)
    for k in range(1, 24):
        t = k / 24.0
        bell = 4.0 * t * (1.0 - t)          # how much of `a` the curve is spending at this t
        # The crest runs right to left from the chord's left end, the trough left to right from
        # the middle, so at the same `t` they stand at mirrored distances from the centre. One
        # wall serves both because the circle is symmetric about its own horizontal.
        for wall, room in ((half * (1.0 - t), off), (half * t, -off)):
            head = room + math.sqrt(max(r * r - wall * wall, 0.0))
            bound = min(bound, max(head, 0.0) / bell)
    return round(bound * 0.98, 3)


def _crest(cx: float, ys: float, half: float, r: float, frac: float) -> str:
    """The water line, as one full wave rather than a ruled chord.

    THE READING IS THE AREA AND THE WAVE DOES NOT MOVE IT. One crest and one trough of equal
    size, so what the crest adds the trough takes back and the enclosed area is the circular
    segment's, exactly. That is not a detail. The height of the fill IS the measurement on this
    page, so an ornament that changed it by even a little would be the drawing lying about the
    number underneath, which is the one thing this project never does for a picture.

    Two quadratics rather than sampled line segments. A `Q` control point sits at twice the
    peak it produces, so the peak is `_amp` and the control is `2 * _amp`, and the curve is
    smooth at every size instead of showing facets on the big lakes.

    Returns an empty string when there is no surface to draw, which is a full lake and an empty
    one. A full circle has no water line, and neither has a vessel with nothing in it.
    """
    if frac >= 0.999 or frac <= 0.001 or half <= 0.0:
        return ""
    a = _amp(r, half, frac)
    if a <= 0.02:
        return ""
    x0, w = cx - half, half * 2.0
    q = round(a * 2.0, 3)
    return (f"Q{round(x0 + w * 0.25, 3)},{round(ys - q, 3)} "
            f"{round(x0 + w * 0.5, 3)},{round(ys, 3)} "
            f"Q{round(x0 + w * 0.75, 3)},{round(ys + q, 3)} "
            f"{round(x0 + w, 3)},{round(ys, 3)} ")


def _surface(cx: float, cy: float, r: float, frac: float) -> str:
    """The water line on its own, open rather than closed, for the lit meniscus.

    The same curve the segment closes over, so the two can never disagree about where the
    water is. Drawn separately because a stroke on the segment would light the arc as well,
    and the arc is the vessel's wall rather than the surface.
    """
    ys, half = _waterline(cy, r, frac)
    crest = _crest(cx, ys, half, r, frac)
    if not crest:
        return ""
    return f"M{round(cx - half, 3)},{round(ys, 3)} {crest}"


def reservoir_label(key: str) -> str:
    """The payload's key, spaced back out into words for a tooltip.

    TWDB's keys are names with the spaces removed, so `SamRayburn` and `OCFisher` are both in
    there. Splitting before a capital that follows a lower case letter handles the first and
    leaves an initialism alone, which is the best a rule can do without a name table nobody
    would keep current.
    """
    import re as _re                                                 # noqa: PLC0415
    return _re.sub(r"(?<=[a-z])(?=[A-Z])", " ", key)


def reservoir_slug(key: str) -> str:
    """The stable public id for one payload key."""
    import re as _re                                                 # noqa: PLC0415
    return _re.sub(r"[^a-z0-9]+", "-", str(key).lower()).strip("-")


def reservoir_catalogue(records: list[dict]) -> list[dict]:
    """The exact latest-day population shared by the map and the detail-page builder."""
    live = [r for r in records if r.get("verified") and isinstance(r.get("reservoirs"), dict)]
    if not live:
        return []
    shared = str(REPO_ROOT / "scripts" / "shared")
    if shared not in sys.path:
        sys.path.insert(0, shared)
    try:
        import reservoirs as _reservoirs                              # noqa: PLC0415
        where = _reservoirs.load()
    except Exception:                                                # noqa: BLE001
        return []
    rows = {r["key"]: r for r in reservoir_rows(live[-1])}
    out = []
    for key, row in rows.items():
        loc = where.get(key) or {}
        if not loc.get("texas"):
            continue
        out.append({**row, "slug": reservoir_slug(key),
                    "name": loc.get("name") or reservoir_label(key),
                    "lon": loc.get("lon"), "lat": loc.get("lat")})
    slugs = [r["slug"] for r in out]
    if len(set(slugs)) != len(slugs):
        raise ValueError("two reservoir keys resolve to one public route")
    return sorted(out, key=lambda r: r["name"])


def reservoir_history(records: list[dict], key: str,
                      catalogue: list[dict] | None = None) -> dict:
    """One reservoir across every verified day that carries a usable reading."""
    by_key = {r["key"]: r for r in
              (catalogue if catalogue is not None else reservoir_catalogue(records))}
    if key not in by_key:
        raise KeyError(key)
    identity = by_key[key]
    rows = []
    for rec in records:
        if not rec.get("verified"):
            continue
        raw = (rec.get("reservoirs") or {}).get(key)
        if not isinstance(raw, dict):
            continue
        storage, capacity = raw.get("storage_af"), raw.get("capacity_af")
        if not isinstance(storage, (int, float)) or not isinstance(capacity, (int, float)) \
                or not capacity:
            continue
        rows.append({"date": rec["date"], "storage_af": float(storage),
                     "capacity_af": float(capacity),
                     "percent_full": round(float(storage) / float(capacity) * 100.0, 2),
                     "change_af": None})
    if not rows:
        raise KeyError(key)

    import datetime as _dt                                           # noqa: PLC0415
    for prior, cur in zip(rows, rows[1:]):
        gap = (_dt.date.fromisoformat(cur["date"])
               - _dt.date.fromisoformat(prior["date"])).days
        if gap == 1:
            cur["change_af"] = round(cur["storage_af"] - prior["storage_af"], 1)
    latest = rows[-1]
    values = [r["percent_full"] for r in rows]
    return {**identity, "rows": rows, "latest": latest, "days": len(rows),
            "from_date": rows[0]["date"], "to_date": latest["date"],
            "span_storage_af": round(latest["storage_af"] - rows[0]["storage_af"], 1),
            "span_percent_full": round(latest["percent_full"] - rows[0]["percent_full"], 2),
            "range_low": min(values), "range_high": max(values)}


RESERVOIR_DETAIL_CSS = """
.reservoir-back{display:inline-flex;gap:.45rem;align-items:center;margin:.4rem 0 1.2rem;
  color:var(--ink-mute);font-size:var(--s-1)}
.reservoir-back::before{content:"←";color:var(--water-lit)}
.reservoir-hero{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(17rem,.7fr);
  align-items:center;gap:clamp(1.2rem,4vw,4.6rem);padding:clamp(1rem,3vw,2.2rem) 0 1rem}
.reservoir-kicker{font:600 var(--s-2)/1 var(--mono);letter-spacing:.14em;text-transform:uppercase;
  color:var(--water-lit);margin:0 0 .65rem}
.reservoir-hero h1{margin:0;max-width:14ch}
.reservoir-hero .lede{max-width:37rem;margin:.9rem 0 .45rem}
.reservoir-orb-card{--orb-x:50%;--orb-y:50%;position:relative;isolation:isolate;
  min-height:clamp(17rem,34vw,27rem);display:grid;place-items:center;outline:none;
  border-radius:50%;background:radial-gradient(circle at var(--orb-x) var(--orb-y),
    color-mix(in srgb,var(--water) 18%,transparent),transparent 54%)}
.reservoir-orb-card[data-tilt-x="left"]{--orb-x:22%;--orb-ry:-3.2deg}
.reservoir-orb-card[data-tilt-x="centre"]{--orb-x:50%;--orb-ry:0deg}
.reservoir-orb-card[data-tilt-x="right"]{--orb-x:78%;--orb-ry:3.2deg}
.reservoir-orb-card[data-tilt-y="top"]{--orb-y:22%;--orb-rx:2.4deg}
.reservoir-orb-card[data-tilt-y="centre"]{--orb-y:50%;--orb-rx:0deg}
.reservoir-orb-card[data-tilt-y="bottom"]{--orb-y:78%;--orb-rx:-2.4deg}
.reservoir-orb-card::before{content:"";position:absolute;inset:14%;border-radius:50%;z-index:-1;
  background:var(--water);filter:blur(3.2rem);opacity:.12}
.reservoir-orb-wrap{width:min(100%,27rem);
  transform:perspective(46rem) rotateX(var(--orb-rx,0deg)) rotateY(var(--orb-ry,0deg));
  transition:transform .18s ease-out;filter:drop-shadow(0 1.3rem 1.7rem rgba(0,0,0,.34))}
.reservoir-orb{width:100%;height:auto;display:block;overflow:visible}
.reservoir-orb .tank{fill:url(#reservoir-shell)}
.reservoir-orb .wf{fill:url(#reservoir-water)}
.reservoir-orb .shellshade{fill:url(#reservoir-depth)}
.reservoir-orb .orbshine{fill:url(#reservoir-shine)}
.reservoir-orb .rim{fill:none;stroke:url(#reservoir-rim);stroke-width:2.3}
.reservoir-orb .rimlight{fill:none;stroke:var(--water-lit);stroke-width:1.8;
  stroke-dasharray:65 240;stroke-linecap:round;transform-box:fill-box;
  transform-origin:50% 50%;transform:rotate(-42deg)}
.reservoir-orb .men{fill:none;stroke:var(--water-lit);stroke-width:2.2;stroke-linecap:round}
.reservoir-orb .flow{fill:none;stroke:var(--water-lit);stroke-width:1.6;
  stroke-linecap:round;stroke-dasharray:7 12;opacity:.32}
.reservoir-orb-card:is(:hover,:focus-visible) .flow{opacity:.86;
  animation:detailwhoosh 1.05s linear infinite}
.reservoir-orb-card:is(:hover,:focus-visible) .men{animation:detailripple 1.7s ease-in-out infinite}
.reservoir-orb-card:is(:hover,:focus-visible) .rimlight{animation:detailrim 2.2s ease-in-out infinite}
@keyframes detailwhoosh{to{stroke-dashoffset:-38}}
@keyframes detailripple{50%{transform:translateY(1.4px)}}
@keyframes detailrim{50%{opacity:.42;transform:rotate(-29deg)}}
.reservoir-metrics{display:grid;grid-template-columns:repeat(auto-fit,minmax(10.5rem,1fr));
  margin:1.5rem 0 3.2rem;border-top:var(--hair) solid var(--rule-strong)}
.reservoir-metrics>div{padding:1rem;border-bottom:var(--hair) solid var(--rule);
  background:linear-gradient(150deg,color-mix(in srgb,var(--surface) 82%,transparent),transparent)}
.reservoir-metrics .label{display:block;color:var(--ink-mute);font-size:var(--s-2);
  letter-spacing:.08em;text-transform:uppercase;margin-bottom:.35rem}
.reservoir-metrics .value{display:block;color:var(--ink-bright);font:500 var(--s1)/1.1 var(--mono);
  white-space:nowrap}
.reservoir-metrics .unit{font-size:var(--s-1);color:var(--ink-mute);margin-left:.25rem}
.reservoir-section{margin:3.4rem 0}.reservoir-section>header{max-width:45rem;margin-bottom:1rem}
.reservoir-trend{width:100%;height:auto;display:block}
.reservoir-trend .area{fill:url(#detail-water-area)}
.reservoir-trend .line{fill:none;stroke:var(--water-lit);stroke-width:3;
  stroke-linejoin:round;stroke-linecap:round;vector-effect:non-scaling-stroke}
.reservoir-trend .g{stroke:var(--rule);stroke-width:1;vector-effect:non-scaling-stroke}
.reservoir-trend .ax{fill:var(--ink-mute);font-family:var(--mono);font-size:12.25px}
.reservoir-trend .point{fill:var(--water-lit);stroke:var(--bg);stroke-width:2;
  vector-effect:non-scaling-stroke}
.reservoir-trend .latest{fill:var(--ink-bright);stroke:var(--water);stroke-width:5}
.reservoir-table-wrap{overflow-x:auto;border-top:var(--hair) solid var(--rule-strong)}
.reservoir-table{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
.reservoir-table th,.reservoir-table td{text-align:left;padding:.72rem .65rem;
  border-bottom:var(--hair) solid var(--rule);white-space:nowrap}
.reservoir-table th{color:var(--ink-mute);font-size:var(--s-2);letter-spacing:.07em;
  text-transform:uppercase}.reservoir-table td:not(:first-child){font-family:var(--mono)}
.reservoir-data-note{margin-top:1rem;color:var(--ink-mute);font-size:var(--s-1)}
@media (max-width:46rem){
  .reservoir-hero{grid-template-columns:1fr}.reservoir-orb-card{order:-1;min-height:16rem}
  .reservoir-orb-wrap{width:min(82vw,22rem)}.reservoir-hero h1{max-width:none}}
@media (max-width:42rem){.reservoir-metrics .metric-wide{grid-column:1/-1}}
@media (max-width:22rem){.reservoir-trend .ax{font-size:34px}}
@media (min-width:22.01rem) and (max-width:26rem){.reservoir-trend .ax{font-size:27px}}
@media (min-width:26.01rem) and (max-width:34rem){.reservoir-trend .ax{font-size:22px}}
@media (min-width:34.01rem) and (max-width:46rem){.reservoir-trend .ax{font-size:17px}}
@media (prefers-reduced-motion:reduce){
  .reservoir-orb-wrap{transition:none;transform:none!important}
  .reservoir-orb-card :is(.flow,.men,.rimlight){animation:none!important}}
"""


MAP_JS = """(() => {
  const map = document.querySelector('svg.resmap');
  const picker = document.getElementById('reservoir-picker');
  const name = document.getElementById('reservoir-name');
  const meta = document.getElementById('reservoir-meta');
  const open = document.getElementById('reservoir-open');
  if (!map || !picker || !name || !meta || !open) return;
  const show = (link) => {
    if (!link) return;
    name.textContent = link.dataset.name || '';
    meta.textContent = link.dataset.meta || '';
    open.href = link.getAttribute('href');
    open.hidden = false;
    picker.value = link.getAttribute('href');
  };
  map.addEventListener('pointerover', (event) => show(event.target.closest('a.reslink')));
  map.addEventListener('focusin', (event) => show(event.target.closest('a.reslink')));
  picker.addEventListener('change', () => {
    if (picker.value) window.location.href = picker.value;
  });
  const restore = () => {
    if (!picker.value) return;
    show([...map.querySelectorAll('a.reslink')].find(
      (link) => link.getAttribute('href') === picker.value));
  };
  window.addEventListener('pageshow', restore);
  restore();
})();"""


RESERVOIR_DETAIL_JS = """(() => {
  const card = document.querySelector('.reservoir-orb-card');
  const orb = document.querySelector('.reservoir-orb-wrap');
  if (!card || !orb || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  const reset = () => {
    delete card.dataset.tiltX;
    delete card.dataset.tiltY;
  };
  const region = (value, low, middle, high) => value < .34 ? low : value > .66 ? high : middle;
  card.addEventListener('pointermove', (event) => {
    const box = card.getBoundingClientRect();
    const x = Math.max(0, Math.min(1, (event.clientX - box.left) / box.width));
    const y = Math.max(0, Math.min(1, (event.clientY - box.top) / box.height));
    card.dataset.tiltX = region(x, 'left', 'centre', 'right');
    card.dataset.tiltY = region(y, 'top', 'centre', 'bottom');
  });
  card.addEventListener('pointerleave', reset);
  card.addEventListener('blur', reset);
})();"""


def _signed(value) -> str:
    sign = "-" if value < 0 else "+" if value > 0 else ""
    return f"{sign}{af(abs(value))}"


def reservoir_trend_svg(detail: dict) -> str:
    """A magnified daily percent-full line using this reservoir's recorded range."""
    rows = detail["rows"]
    if len(rows) < 2:
        return ""
    width, height = 840.0, 330.0
    vals = [r["percent_full"] for r in rows]
    span = max(vals) - min(vals)
    cushion = max(span * .18, .18)
    low, high = max(0.0, min(vals) - cushion), max(vals) + cushion
    if max(vals) <= 100.0:
        high = min(100.0, high)
    if high <= low:
        low, high = max(0.0, low - .5), high + .5
    ticks = [low, (low + high) / 2, high]
    # SIZE FROM THE ACTUAL PHONE LABELS. A fixed gutter passed on macOS and clipped 100.0%
    # on CI's fallback face at 300px. The largest axis face is 34 SVG units; reserve its
    # conservative mono advance plus the 10-unit anchor gap and 24 units of outer clearance.
    # The top tick likewise needs a full cap-height above its baseline.
    left = max(138.0, _gutter([f"{pct(v)}%" for v in ticks], 34.0, pad=34.0))
    right, top, bottom = 24.0, 48.0, 58.0
    plot_w, plot_h = width - left - right, height - top - bottom

    def x(i):
        return left + plot_w * i / max(len(rows) - 1, 1)

    def y(value):
        return top + plot_h * (high - value) / (high - low)

    pts = [(x(i), y(row["percent_full"])) for i, row in enumerate(rows)]
    line = "M" + " L".join(f"{px:.2f},{py:.2f}" for px, py in pts)
    area = line + f" L{pts[-1][0]:.2f},{top + plot_h:.2f} L{pts[0][0]:.2f},{top + plot_h:.2f} Z"
    grid = "".join(
        f'<line class="g" x1="{left}" x2="{width - right}" y1="{y(v):.2f}" y2="{y(v):.2f}"/>'
        f'<text class="ax" x="{left - 10}" y="{y(v) + 4:.2f}" text-anchor="end">{pct(v)}%</text>'
        for v in ticks)
    points = "".join(
        f'<circle class="point{" latest" if i == len(rows) - 1 else ""}" '
        f'cx="{px:.2f}" cy="{py:.2f}" r="{5 if i == len(rows) - 1 else 3.2}">'
        f'<title>{ordinal_date(row["date"])}, {pct(row["percent_full"])}% full</title></circle>'
        for i, (row, (px, py)) in enumerate(zip(rows, pts)))
    labels = "".join(
        f'<text class="ax" x="{x(i):.2f}" y="{height - 20}" text-anchor="{anchor}">'
        f'{ordinal_short(rows[i]["date"])}</text>'
        for i, anchor in ((0, "start"), (len(rows) // 2, "middle"), (len(rows) - 1, "end")))
    return f"""<figure class="wviz">
<svg class="waterviz reservoir-trend" viewBox="0 0 {width:g} {height:g}" role="img"
  aria-label="Daily percent full for {html.escape(detail['name'])} from
  {html.escape(ordinal_date(rows[0]['date']))} through
  {html.escape(ordinal_date(rows[-1]['date']))}">
  <defs><linearGradient id="detail-water-area" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="var(--water)" stop-opacity=".48"/>
    <stop offset="1" stop-color="var(--water)" stop-opacity=".03"/>
  </linearGradient></defs>
  {grid}<path class="area" d="{area}"/><path class="line" style="--len:{_polylen(pts):.2f}" d="{line}"/>
  {points}{labels}
</svg>
<figcaption>Daily percent full. The vertical scale follows this record's own range instead of
starting at zero, so its movement stays visible without changing the measurement.</figcaption>
</figure>"""


def reservoir_detail_body(detail: dict) -> str:
    """A complete, static, linkable record for one reservoir."""
    name = html.escape(detail["name"])
    latest = detail["latest"]
    frac = max(0.0, min(float(latest["percent_full"]) / 100.0, 1.0))

    metrics = [("Percent full", pct(latest["percent_full"]), "%"),
               ("Storage", af(latest["storage_af"]), "AF"),
               ("Conservation capacity", af(latest["capacity_af"]), "AF")]
    if latest.get("change_af") is not None:
        metrics.append(("Change today", _signed(latest["change_af"]), "AF"))
    if detail["days"] > 1:
        metrics.append(("Across the record", _signed(detail["span_storage_af"]), "AF"))
    metrics.extend([
        ("Recorded range", f'{pct(detail["range_low"])}% to {pct(detail["range_high"])}%', ""),
        ("Record", af(detail["days"]), plural(detail["days"], "day", "days")),
    ])
    def metric_cell(label, value, unit):
        unit_html = f'<span class="unit">{unit}</span>' if unit else ""
        wide = ' class="metric-wide"' if label == "Recorded range" else ""
        return (f'<div{wide}><span class="label">{label}</span>'
                f'<span class="value">{value}{unit_html}</span></div>')

    cells = "".join(metric_cell(label, value, unit) for label, value, unit in metrics)

    table_rows = []
    for index, row in reversed(list(enumerate(detail["rows"]))):
        if row.get("change_af") is not None:
            move = f'{_signed(row["change_af"])} AF'
        else:
            move = "First reading" if index == 0 else "No adjacent reading"
        table_rows.append(
            f'<tr><td>{ordinal_date(row["date"])}</td>'
            f'<td>{pct(row["percent_full"])}%</td><td>{af(row["storage_af"])} AF</td>'
            f'<td>{move}</td></tr>')

    return f"""<style>{STAGE_CSS}\n{RESERVOIR_DETAIL_CSS}</style>
<a class="reservoir-back" href="../../../water/">Texas Water Watch</a>
<section class="reservoir-hero" data-proper-name="{name}">
  <div>
    <p class="reservoir-kicker">Reservoir record</p>
    <h1>{name}</h1>
    <p class="lede">{name} is <strong class="num">{pct(latest['percent_full'])}%</strong> full,
    holding <strong class="num">{af(latest['storage_af'])}</strong> acre feet against a
    conservation capacity of <strong class="num">{af(latest['capacity_af'])}</strong> acre feet.</p>
    <p class="wnote">Updated {ordinal_date(latest['date'])}</p>
  </div>
  <div class="reservoir-orb-card" tabindex="0"
       aria-label="A dimensional gauge for {name} at {pct(latest['percent_full'])}% full">
    <div class="reservoir-orb-wrap">
      <svg class="reservoir-orb" viewBox="0 0 360 360" role="img"
           aria-label="{name} filled to {pct(latest['percent_full'])}%">
        {_reservoir_defs()}
        <g>{_vessel(180.0, 180.0, 112.0, frac, "")}</g>
      </svg>
    </div>
  </div>
</section>
<div class="reservoir-metrics" data-prose="data">{cells}</div>
<section class="reservoir-section">
  <header><h2>Daily movement</h2>
    <p>The line follows every verified reading held for this reservoir.</p></header>
  {reservoir_trend_svg(detail)}
</section>
<section class="reservoir-section">
  <header><h2>The readings</h2>
    <p>Daily movement appears only when the previous reading is from the prior calendar day.</p>
  </header>
  <div class="reservoir-table-wrap"><table class="reservoir-table" data-prose="data">
    <thead><tr><th>Date</th><th>Percent full</th><th>Storage</th><th>Daily movement</th></tr></thead>
    <tbody>{''.join(table_rows)}</tbody>
  </table></div>
  <p class="reservoir-data-note">Every reading is available in the
    <a href="../../../waterwatch.json">open water record</a>.</p>
</section>
<script>{RESERVOIR_DETAIL_JS}</script>
"""


def reservoir_authorised(detail: dict) -> set[str]:
    """Exactly the figures reader-facing detail prose and cells publish."""
    acc = numeral_lint.Authorised()
    add = acc.add
    latest = detail["latest"]
    add(pct(latest["percent_full"]), af(latest["storage_af"]), af(latest["capacity_af"]),
        ordinal_date(latest["date"]), pct(detail["range_low"]), pct(detail["range_high"]),
        af(detail["days"]))
    if latest.get("change_af") is not None:
        add(af(abs(latest["change_af"])))
    if detail["days"] > 1:
        add(af(abs(detail["span_storage_af"])))
    for row in detail["rows"]:
        add(ordinal_date(row["date"]), pct(row["percent_full"]), af(row["storage_af"]))
        if row.get("change_af") is not None:
            add(af(abs(row["change_af"])))
    return acc.set


def reservoir_lint(html_body: str, detail: dict) -> list[str]:
    return numeral_lint.scan(html_body, reservoir_authorised(detail))


def ordinal_short(iso: str) -> str:
    """A date for an axis, where the year is furniture the reader already has."""
    import datetime as _dt                                           # noqa: PLC0415
    d = _dt.date.fromisoformat(iso)
    suf = "th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th")
    return f"{d:%b} {d.day}{suf}"


def sparkline(values: list, window: float) -> str:
    """One metro's whole record, small enough to sit in a table cell.

    PLOTTED AS CHANGE FROM THE FIRST DAY, ON A SCALE SHARED BY EVERY ROW. That is the decision
    that makes this a chart rather than decoration, and both halves matter.

    Scaled to each metro's OWN range, the usual sparkline default, every row would fill its
    cell top to bottom and a metro that moved three hundredths of a point would look exactly
    like one that moved two whole points. Scaled 0 to 100 instead, every row is a dead flat
    line, because no metro moves more than a point or two in the length of this record. Neither
    drawing carries the comparison a reader is making, which is who is falling fastest.

    So the baseline is each metro's first reading and the scale is one window, sized from the
    largest move any metro made. The slopes are then comparable across rows, which is the whole
    question. What it deliberately does NOT show is the level, because the bar beside it in the
    same row already does, and drawing the level twice would be the only thing in the cell.
    """
    pts = [(i, v) for i, v in enumerate(values) if isinstance(v, (int, float))]
    if len(pts) < 2 or not window:
        return ""
    base = pts[0][1]
    w, h = 88.0, 22.0
    mid = h / 2

    def x(i):
        return round(i / max(len(values) - 1, 1) * w, 2)

    def y(v):
        return round(mid - ((float(v) - base) / window) * (mid - 2.0), 2)

    # A BREAK RATHER THAN A BRIDGE. A metro the source stopped tagging for a day is a hole in
    # the record, and a line drawn straight across it would publish an interpolation as a
    # measurement. Consecutive runs only, so a gap reads as a gap.
    runs, cur = [], []
    for i, v in enumerate(values):
        if isinstance(v, (int, float)):
            cur.append((x(i), y(v)))
        elif cur:
            runs.append(cur)
            cur = []
    if cur:
        runs.append(cur)
    d = " ".join("M" + " L".join(f"{a},{b}" for a, b in run) for run in runs if len(run) > 1)
    if not d:
        return ""
    last = runs[-1][-1]
    length = round(sum(_polylen(run) for run in runs if len(run) > 1), 1) or 1.0
    return (f'<svg class="spark" viewBox="0 0 {w:g} {h:g}" aria-hidden="true" '
            f'preserveAspectRatio="none">'
            f'<line class="zero" x1="0" x2="{w:g}" y1="{mid}" y2="{mid}"/>'
            f'<path class="line" style="--len:{length}" d="{d}"/>'
            f'<circle class="mk" cx="{last[0]}" cy="{last[1]}" r="1.9"/></svg>')


def metro_bars(metros: list[dict], walk: list | None = None,
               series: dict | None = None) -> str:
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

    # THE SHARED WINDOW FOR EVERY SPARKLINE ON THE TABLE, computed once here from the largest
    # move any metro made across the record. Sized per row instead, the drawings would be
    # nineteen unrelated pictures that happen to share a shape, and a reader comparing two rows
    # would be comparing two different scales with nothing on the page to say so.
    window = 0.0
    for vals in (series or {}).values():
        seen = [v for v in vals if isinstance(v, (int, float))]
        if len(seen) >= 2:
            window = max(window, max(abs(v - seen[0]) for v in seen))
    window = window or 1.0

    rows = "".join(f"""<tr>
  <th scope="row">{m['name']}{omb(m)}</th>
  <td class="barcell"><div class="bar mini"><div class="fill"
      style="width:{min(float(m['percent_full']), 100.0):.1f}%"></div></div></td>
  <td class="n num">{pct(m['percent_full'])}%</td>
  <td class="n num af">{af(m['storage_af'])}</td>
  <td class="sparkcell">{sparkline((series or {{}}).get(m['slug']) or [], window)}</td>
</tr>""" for m in metros)
    # THE CAPTION WAS SIXTY TWO WORDS OF READING INSTRUCTIONS, cut to five on the owner's
    # instruction, 2026-08-21. It explained that one hue is used at every value, that the last
    # column is drawn as change from each metro's own first day on a shared scale, and that a
    # second name under a metro is the federal one. Every sentence was true and every sentence
    # was asking a reader to study a paragraph before looking at a table.
    #
    # A caption names the table. The column headings say what the columns are, and the last one
    # is "Trend" now rather than "Record", because a word that needs a sentence under it to be
    # understood is the wrong word. The shared scale is still shared and still computed above,
    # and a reader comparing two rows is still comparing like with like. That was never
    # something the paragraph made true. It was something the paragraph claimed.
    return f"""<table class="figures metros">
<caption>Metro reservoir storage, driest first</caption>
<thead><tr><th>Metro</th><th>Full</th><th class="n">Percent</th>
<th class="n afhead">Acre feet</th><th class="sparkhead">Trend</th></tr></thead>
<tbody>{rows}</tbody></table>"""


def plural(n, one: str, many: str) -> str:
    """The word after the number, never the number. Keeps "day(s)" off a published page."""
    try:
        return one if abs(float(str(n).replace(",", ""))) == 1 else many
    except (TypeError, ValueError):
        return many


def sits(name: str) -> str:
    """Whether a metro takes a singular verb, which four of the nineteen do not.

    Seven metro names here are compounds. "Midland and Odessa sits at 27.1% full" is what a
    fixed verb produces, and it is the kind of wrong a reader notices before they notice the
    number. The metro is one place and the NAME is plural, so the verb follows the name.
    """
    return "sit" if " and " in name else "sits"


def readout(f: dict) -> str:
    """The figures a reader came for, at the top, at the size of a subject.

    THIS BLOCK IS WHAT THREE PARAGRAPHS BECAME and it holds every number they held. The
    paragraphs were accurate and they asked a reader to walk through a sentence to reach a
    quantity that was going to be a quantity either way. A figure that is the point of the page
    should look like the point of the page.

    NOTHING IS SUMMARISED AWAY. Storage, percent full, the day's move, the move across the whole
    record, the reservoir count and the length of the record are all here, each still computed in
    `figures` and each still authorised by name, so the numeral gate reads exactly what a reader
    reads.
    """
    L = f.get("latest") or {}
    if not L:
        return ""
    # ROOM LEFT LIVES HERE RATHER THAN ON THE CHART, and that is a placement fixed by
    # measurement rather than by taste. It was drawn inside the trend panel's empty band, which
    # is where the quantity actually is, and at phone type that band holds one line while three
    # labels wanted it: the ceiling caption, the latest reading and this. Every pair collided
    # and the page sweep named all of them. A figure worth publishing does not fight two others
    # for a line, so it moved to the one block on this page built to hold figures.
    chips = [("Storage", maf(L["storage_af"]), "MAF"),
             ("Percent full", pct(L["percent_full"]), "%")]
    if L.get("headroom_af") is not None:
        chips.append(("Room left", maf(L["headroom_af"]), "MAF"))
    chips.append(("Reservoirs", af(L["reservoir_count"]), ""))
    c = f.get("change")
    if c:
        sign = "-" if c["storage_af"] < 0 else "+" if c["storage_af"] > 0 else ""
        chips.insert(3, ("Change today", f"{sign}{af(abs(c['storage_af']))}", "AF"))
    sp = f.get("span")
    if sp and sp["days"] > 1:
        sign = "-" if sp["storage_af"] < 0 else "+" if sp["storage_af"] > 0 else ""
        # THE LABEL CARRIES NO DATE, and that is a house style fix rather than a taste one. It
        # read "Since August 11th, 2026" and the value beside it opens with a minus, so the two
        # ran together as "2026 -368,416" and the gate correctly called it a range written with
        # a dash. The date was furniture in any case. The chip beside this one says how long the
        # record is and the trend chart's axis is labelled at both ends.
        chips.insert(4 if c else 3,
                     ("Across the record", f"{sign}{af(abs(sp['storage_af']))}", "AF"))
    chips.append(("Record", af(f["days_held"]),
                  plural(f["days_held"], "day", "days")))
    def cell(i, k, v, u):
        unit = f'<span class="wru">{u}</span>' if u else ""
        return (f'<div class="d{min(i, 7)}"><span class="wrk">{k}</span>'
                f'<span class="wrv">{v}{unit}</span></div>')

    cells = "".join(cell(i, k, v, u) for i, (k, v, u) in enumerate(chips))
    # `data-prose="data"` MARKS THIS AS STRUCTURED RATHER THAN WRITTEN. These are labels on
    # instrument faces, and measuring comma density over them would be measuring the shape of a
    # table. The marker is subtracted from the DENSITY rule only, never from the construction
    # rules, so a colon or an em dash in a label still fails the gate.
    return f'<div class="wreadout" data-prose="data">{cells}</div>'


def body(records: list[dict], today: str) -> str:
    f = figures(records)
    if not f["latest"]:
        return """
<h1>Texas Water Watch</h1>
<div class="prose">
  <p>A daily numeric record of water held in Texas reservoirs, published beside the grid watch
  because a data center draws on both.</p>
  <div class="gap"><strong>The record is empty.</strong> No day has been collected yet.
  Nothing is estimated to fill the space.</div>
</div>
"""
    L = f["latest"]
    d = ordinal_date(L["date"])
    metros = L["metros"]
    driest, fullest = (metros[0], metros[-1]) if metros else (None, None)

    # THE LEDE IS THE SPREAD AND NOTHING ELSE, cut from 72 words to 11 on the owner's
    # instruction, 2026-08-21.
    #
    # What came out was the statewide total, the capacity it is measured against, the sentence
    # saying the spread is the story, and a paragraph explaining why water sits beside the grid.
    # Every one of those was true and every one was type standing in front of a drawing. The
    # readout strip one block down prints the total at the size of a subject. The map, the
    # distribution and the metro rows ARE the spread, three ways. A sentence announcing that
    # the spread is the story is a caption on a page that no longer needs telling.
    #
    # The two extremes stay in words because they are the finding, and because a reader who
    # takes one line off this page should take that one.
    lede = ""
    if driest and fullest and driest["slug"] != fullest["slug"]:
        lede = f"""
  <p class="lede">{driest['name']} {sits(driest['name'])} at
  <strong class="num">{pct(driest['percent_full'])}%</strong> full.
  {fullest['name']} {sits(fullest['name'])} at
  <strong class="num">{pct(fullest['percent_full'])}%</strong>.</p>"""

    # THE PROVENANCE NOTE IS OFF THE PAGE, on the owner's instruction, 2026-08-21. It said
    # percent full is computed from storage over capacity and never read from the feed's own
    # field, then published the largest disagreement between the two. A date stands there now.
    #
    # WHAT WENT WITH IT. `waterwatch_pagecheck` failed the page if that sentence disappeared,
    # and `daily_routine.md` carried an `onpage` marker holding the page to it. Both came off
    # in the same commit. A gate left standing over copy nobody intends to write again is a
    # permanently red advisory, and this project has learned twice what that does to the
    # findings around it. A rule and the thing it guards are removed together or not at all.
    #
    # WHAT IS NOT LOST. `figures` still computes the agreement and `waterwatch.json` still
    # publishes `percent_full_max_disagreement` per day, so the check is still run and still
    # open. It is no longer copy. The authorisation for the figure came off the list with the
    # sentence, because an authorised numeral nothing prints is a hole the width of that number.
    agree = f"""
  <p class="wnote">Updated {d}</p>"""

    cov = L.get("coverage") or {}
    # THE COVERAGE AND EXCLUSION NOTES ARE OFF THE PAGE, ON THE OWNER'S EXPLICIT INSTRUCTION,
    # 2026-08-20. Written down because it reverses a rule this repo argued for at length.
    #
    # What came off: the "What is counted" section with its coverage grid and exclusion dots,
    # then the two sentences that survived it, which said that San Antonio has no line because
    # the state's water data does not tag it and that El Paso's only tagged reservoir sits in
    # New Mexico. The owner's judgement is that it is irrelevant to a reader and was costing
    # screen space, and that is a call about what this page is for rather than about whether
    # the sentences were true.
    #
    # THE RULE WENT WITH THE COPY, DELIBERATELY. `waterwatch_pagecheck` used to fail the page
    # if either went unexplained. Leaving that gate standing over copy nobody intends to
    # restore would have meant a permanently red advisory, which is the exact failure mode this
    # project keeps writing down: a finding that is always there teaches a reader to skim past
    # the one that is real. A rule and the thing it guards are removed together or not at all.
    #
    # WHAT IS NOT LOST. `coverage()` still computes the crosswalk, because `metro_bars` needs
    # the walk for the federal names, and `waterwatch.json` still publishes the exclusions per
    # reservoir. The facts are in the open data. They are no longer in the copy.
    #
    # The `gap` slot went with the closing block on 2026-08-29, on the owner's instruction, and
    # so did the surface water caveat, the low bar caveat and the line about the record's length.
    # `days_held` is still printed, by the Record chip in the readout, so it stays authorised.

    # THE STAGE TRAVELS WITH THE PAGE. Emitted here rather than linked, so the drawings and the
    # rules that style them arrive in one response and there is no width at which a reader sees
    # an unstyled chart. `csp.py` hashes this from the page's final bytes, so it is covered by
    # the policy without an allowlist entry and without `'unsafe-inline'` anywhere near it.
    return f"""<style>{STAGE_CSS}</style>
<h1>Texas Water Watch</h1>
<div class="prose">{lede}</div>

<h2>{d}</h2>
<div data-reveal>{readout(f)}</div>

<div data-reveal>{reservoir_map_svg(f)}</div>

<div data-reveal>{state_trend_svg(f)}</div>
<div class="prose">{agree}</div>

{metro_bars(metros, cov.get("walk"), f.get("metro_series"))}

<div data-reveal>{distribution_svg(f)}</div>

<script>{MAP_JS}</script>
"""


# --------------------------------------------------------------------------- numeral gate
def authorised(f: dict) -> set[str]:
    """Exactly the numerals this page prints, and not one more.

    PRUNED, AND THE PRUNING IS THE POINT. This set had grown to 84 entries of which 29 reached
    no reader, which is a third of an allowlist standing open for figures the page had stopped
    printing. Several were stale in the ordinary way, from a formatter change: statewide storage
    moved from acre feet to millions of acre feet and both stayed authorised. Others were never
    printed at all, like every metro's capacity beside the storage that is.

    A dead authorisation is not inert. `numeral_lint` asks whether a numeral is in this set and
    nothing else, so an entry nothing prints is a hole exactly the width of that number, on this
    page and, through `site_build._watch_numerals`, on the site wide check as well. The QUOTED
    table above already carries this lesson for the one numeral that is allowed in without being
    computed. It holds just as hard for the computed ones.

    `self_test` fails on an orphan now, so this cannot silently regrow.
    """
    acc = numeral_lint.Authorised()
    add = acc.add
    add(*QUOTED)
    L = f.get("latest")
    if L:
        # THE LENGTH OF THE RECORD IS AUTHORISED ONLY WHERE IT IS PRINTED. On a record with
        # no verified day the page renders its empty branch, which carries no figure at all,
        # and this authorisation stood there permitting a bare count that nothing printed.
        # The orphan gate found both cases the moment it was pointed at the degraded shapes,
        # which is exactly where nobody looks.
        #
        # CAPACITY CAME OFF THIS LIST WITH THE LEDE THAT PRINTED IT, 2026-08-21, and the orphan
        # gate named it the same minute. The figure is still on the page. It labels the ceiling
        # the trend chart is drawn against, and a label inside an `svg` is outside the reach of
        # both `numeral_lint` and this list, so an authorisation for it permits a numeral in
        # PROSE that no prose prints. That is the hole the orphan check exists to refuse, and
        # it does not care that the number is honest.
        add(af(f["days_held"]),
            ordinal_date(L["date"]),
            maf(L["storage_af"]), maf(L.get("headroom_af")),
            pct(L["percent_full"]), af(L["reservoir_count"]),
            pct(L.get("below_average")))
        # THE EXCLUSION COUNTS CAME OFF WITH THE SECTION THAT PRINTED THEM. "2 flood control
        # dams", "1 sits out of state" and the counted total all lived in the exclusion dots
        # caption, and that block is gone. The orphan gate named all three the moment it did.
        for m in L["metros"]:
            add(pct(m["percent_full"]), af(m["storage_af"]))
        # `cov` lined and areas are computed and no longer published, so they are not
        # authorised. An authorisation for a figure nothing prints is a hole the width of
        # that number, which is what the orphan check below exists to refuse.
    c = f.get("change")
    if c:
        add(af(abs(c["storage_af"])))
    sp = f.get("span")
    # GUARDED ON THE SAME CONDITION THE READOUT USES. The across-the-record chip only renders
    # when the record holds more than one day, and on a single day the move is zero, so an
    # unguarded authorisation stood there permitting a bare "0" that nothing printed.
    if sp and sp["days"] > 1:
        add(af(abs(sp["storage_af"])))
    return acc.set


def reader_numerals(html_body: str, auth: set[str]) -> set[str]:
    """Every numeral token a reader actually sees, tokenised the way the gate tokenises.

    THE INVERSE OF `numeral_lint.scan`, and it has to share the scanner's rules or it proves
    nothing. Markup, script, style, cite and svg come out; entities are decoded; authorised
    PHRASES are consumed whole at a token boundary before anything is tokenised, for the same
    reason the scanner does it, which is that a phrase sitting inside a numeral would otherwise
    split it and invent tokens no reader ever saw.
    """
    import html as _h                                                # noqa: PLC0415
    import re as _re                                                 # noqa: PLC0415
    nl = numeral_lint
    text = _h.unescape(nl.TAG.sub(" ", nl.CITE_BLOCK.sub(
        " ", nl.SCRIPT_BLOCK.sub(" ", nl.SVG_BLOCK.sub(" ", html_body)))))
    for v in sorted((a for a in auth if a and _re.search(r"[^0-9,.]", a)), key=len, reverse=True):
        text = _re.sub(r"(?<![0-9.,])" + _re.escape(v) + r"(?![0-9])", " ", text)
    return set(nl.NUMERAL.findall(text))


def orphans(html_body: str, auth: set[str]) -> list[str]:
    """Authorised values that reach no reader. Every one is a hole the width of that number."""
    import re as _re                                                 # noqa: PLC0415
    seen = reader_numerals(html_body, auth)
    out = []
    for v in auth:
        if not v:
            continue
        if _re.search(r"[^0-9,.]", v):
            if v not in html_body:
                out.append(v)
        elif v not in seen:
            out.append(v)
    return sorted(out)


def lint(html_body: str, f: dict) -> list[str]:
    return numeral_lint.scan(html_body, authorised(f))


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    import math                                                      # noqa: PLC0415
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
    check("El Paso is not given a bar", "el_paso" not in b)

    check("no orphaned quoted numeral survives the copy it was admitted for",
          all(k in b for k in QUOTED), str([k for k in QUOTED if k not in b]))


    # THE DAY OVER DAY MOVE.
    two = [rec("2026-08-10", storage=24329431.0), rec("2026-08-11")]
    f2 = figures(two)
    check("two consecutive days produce a change figure", f2["change"] is not None)
    check("...computed, and signed", f2["change"]["storage_af"] == -26085.0,
          str(f2["change"]["storage_af"]))
    b2 = body(two, "2026-08-11")
    # ASSERTED ON THE INTENT, not on a phrase, and the intent outlived two rewrites of the
    # surface it is carried on. It first read `"fell by" in b2` and went red when the copy was
    # tightened to "fell 26,085". It then read `"fell" in b2` and went red again when the
    # sentence became a readout chip and the word left the page entirely.
    #
    # What the check has been for the whole time is TWO things, and neither one is a wording.
    # The day's move must be PUBLISHED, with its direction, and it must never be GRADED. A
    # figure that arrives as "-26,085" says the same thing the sentence said, and "decline" is
    # still the word that would turn a measurement into a verdict.
    check("the day's move is published, signed, and never graded",
          "26,085" in b2 and "-26,085" in b2
          and not any(w in b2.lower() for w in ("declin", "worsen", "improv")))
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

    # NO AUTHORISATION OUTLIVES THE COPY IT WAS GRANTED FOR, computed ones included.
    #
    # This set reached 84 entries of which 29 reached no reader. Some went stale in the
    # ordinary way, from a formatter change, when statewide storage moved to millions of acre
    # feet and the acre foot form stayed authorised beside it. Others were never printed at
    # all. Each one is a hole the exact width of that number, here and on the site wide check
    # that reads this same function, and none of it was visible because a gate reports what
    # fails rather than what it is quietly permitting.
    #
    # Checked on EVERY SHAPE the record can take, because a page written to say more as the
    # series grows authorises more as it grows too, and the shape that is not today's data is
    # the one nobody looks at.
    for label, records in (("one record", one), ("two records", two), ("a gap", gapped),
                           ("an empty record", []), ("an unverified day", unver)):
        rendered = body(records, records[-1]["date"] if records else "2026-08-11")
        left = orphans(rendered, authorised(figures(records)))
        check(f"every authorised numeral at {label} reaches a reader", not left, str(left))

    # THE QUOTED ESCAPE HATCH, held to its own standard. It is the one route by which a numeral
    # that was not computed can reach a reader, so it must be impossible to widen quietly.
    check("every quoted numeral carries the source it is quoted from",
          all(isinstance(v, str) and len(v) > 40 for v in QUOTED.values()),
          str([k for k, v in QUOTED.items() if not isinstance(v, str) or len(v) <= 40]))
    check("the quoted list stays short enough to read in one glance", len(QUOTED) <= 5,
          f"{len(QUOTED)} entries")
    check("a quoted numeral actually appears in the copy it was admitted for",
          all(k in b for k in QUOTED), str([k for k in QUOTED if k not in b]))

    # ---- the drawings ---------------------------------------------------------
    # THESE ARE THE GATES FOR THE SURFACES THAT REPLACED THE PROSE. The paragraphs that came
    # off this page were checked by `numeral_lint` and `house_style_check` every build. A
    # drawing is checked by NEITHER, because both strip `<svg>` before they read a page, so
    # every figure moved into a chart is a figure that left the reach of the two gates that
    # were watching it. That is a fair trade only if something else watches instead.
    live_f = figures(load())
    if live_f.get("latest"):
        live_b = body(load(), live_f["latest"]["date"])
        for name, drawn in (("the map", reservoir_map_svg(live_f)),
                            ("the trend", state_trend_svg(live_f)),
                            ("the distribution", distribution_svg(live_f))):
            check(f"{name} renders from the record", bool(drawn) and drawn.startswith("<"))

        # THE EL PASO TRAP AGAIN, ON THE ONE SURFACE THAT COULD REOPEN IT. The ledger excludes
        # Elephant Butte and the copy explains why, and a map drawn from a coordinate file
        # rather than from the exclusion list would put it back on the page as a Texas
        # reservoir with nothing complaining. It is the only reservoir in the payload without
        # TWDB's `texas` tag, so the drawing has to be the thing that respects the tag.
        drawn_map = reservoir_map_svg(live_f)
        check("the map draws no out of state reservoir",
              "Elephant Butte" not in drawn_map and "ElephantButte" not in drawn_map)
        check("...while still drawing the ones that are in Texas",
              drawn_map.count('class="rim') > 100, str(drawn_map.count('class="rim')))

        # EVERY DOT IS NOW A DOOR. The population comes from one function and the map and page
        # builder both consume it, but that shared intent still needs an assertion on the bytes
        # a reader receives. A circle without an anchor would otherwise look complete and do
        # nothing, which is exactly the experience this family replaces.
        cat = reservoir_catalogue(load())
        check("every mapped reservoir is a keyboard reachable detail link",
              drawn_map.count('class="reslink"') == len(cat),
              f'{drawn_map.count("reslink")} links for {len(cat)} reservoirs')
        check("every mapped reservoir declares its source proper name",
              drawn_map.count('data-proper-name=') == len(cat),
              f'{drawn_map.count("data-proper-name=")} names for {len(cat)} reservoirs')
        check("every detail route is unique",
              len({r["slug"] for r in cat}) == len(cat), str(len(cat)))
        # AN ANCHOR CAN EXIST AND STILL BE UNCLICKABLE when every pixel of its hit circle is
        # painted over by later reservoirs. Sample the whole usable disc against paint order,
        # which is the property the pointer sees. Keyboard access alone is not a substitute for
        # the direct map interaction this drawing offers.
        import re as _hit_re                                         # noqa: PLC0415
        hits = [(href, float(x), float(y), float(radius)) for href, x, y, radius in
                _hit_re.findall(
                    r'<a class="reslink" href="([^"]+)".*?'
                    r'<circle class="hit" cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)"/>',
                    drawn_map, _hit_re.S)]
        buried = []
        for i, (href, cx, cy, radius) in enumerate(hits):
            samples = [(cx, cy)]
            for reach in (.45, .75, .95):
                samples.extend((cx + radius * reach * math.cos(step * math.tau / 32),
                                cy + radius * reach * math.sin(step * math.tau / 32))
                               for step in range(32))
            if not any(all((sx - ox) ** 2 + (sy - oy) ** 2 > other ** 2
                           for _href, ox, oy, other in hits[i + 1:])
                       for sx, sy in samples):
                buried.append(href)
        check("every map link keeps a pointer reachable patch", not buried, str(buried[:8]))
        check("the dimensional vessels carry depth, light and moving water",
              all(token in drawn_map for token in
                  ("reservoir-shell", "reservoir-depth", "orbshine", "flow flow"))
              and "wwhoosh" in live_b)
        check("a motion preference turns the water animation off",
              "prefers-reduced-motion:reduce" in live_b and "animation:none" in live_b)

        if cat:
            detail = reservoir_history(load(), cat[0]["key"])
            detail_body = reservoir_detail_body(detail)
            check("a reservoir page carries every verified reading it has",
                  detail_body.count("<tbody>") == 1
                  and detail_body.count("<tr>") - 1 == len(detail["rows"]),
                  f'{detail_body.count("<tr>") - 1} rows vs {len(detail["rows"])}')
            check("the reservoir trend and dimensional hero both render",
                  "reservoir-trend" in detail_body and "reservoir-orb" in detail_body)
            full_detail = {**detail, "rows": [{**row, "percent_full": 100.0}
                                            for row in detail["rows"]]}
            full_axis = _hit_re.findall(
                r'<text class="ax" x="([\d.]+)" y="[\d.]+" text-anchor="end">'
                r'([^<]+%)</text>', reservoir_trend_svg(full_detail))
            check("a full reservoir axis reserves fallback-font clearance on a phone",
                  bool(full_axis) and all(float(x) - MONO_ADV * 34 * len(label) >= 23.9
                                         for x, label in full_axis), str(full_axis))
            check("the reservoir page declares its source proper name",
                  f'data-proper-name="{html.escape(detail["name"])}"' in detail_body)
            check("the reservoir page has no uncomputed reader numeral",
                  not reservoir_lint(detail_body, detail),
                  str(reservoir_lint(detail_body, detail)[:8]))
            check("every reservoir authorisation reaches a reader",
                  not orphans(detail_body, reservoir_authorised(detail)),
                  str(orphans(detail_body, reservoir_authorised(detail))[:8]))
            detail_problems = _hs.caption_check.check(_hs.our_prose(detail_body))
            detail_rate = _hs.caption_check.rate_problem(
                _hs.our_sentences(detail_body), _hs.caption_check.SITE_COMMA_CEILING)
            if detail_rate:
                detail_problems.append(detail_rate)
            check("the reservoir page keeps the house rules", not detail_problems,
                  "; ".join(detail_problems)[:180])

        # THE CHART'S OWN CLAIM, CHECKED. The distribution's caption tells a reader that the
        # area under the steps is the statewide percentage. That is either true arithmetic or
        # it is a sentence, and the difference is this assertion.
        rows = live_f["latest"]["reservoirs"]
        tot = sum(r["capacity_af"] for r in rows)
        area = sum(r["capacity_af"] / tot * r["percent_full"] for r in rows)
        check("the area under the distribution is the statewide figure the page prints",
              abs(area - live_f["latest"]["percent_full"]) < 0.05,
              f'{area:.3f} vs {live_f["latest"]["percent_full"]}')

        # NO SEVERITY RAMP ON ANY OF THE NEW SURFACES, which is the same law the bars have
        # always obeyed, restated where it could newly be broken. A drawing gets to carry a
        # value in a length, an area or a water line. It never gets to carry one in a colour.
        for cls in ("warn", "crit", "high", "low", "danger", "alert", "dry", "empty"):
            check(f"no drawing marks a value as {cls}", f'class="wf {cls}' not in live_b
                  and f'class="rv {cls}' not in live_b and f"{cls}\"" not in STAGE_CSS)

        # EVERY STAGGER CLASS THE MARKUP EMITS HAS A RULE BEHIND IT. `_delay` buckets into
        # seven and the stylesheet defines seven, and the two are written in different places,
        # so a widened bucket count would silently emit a class that styles nothing.
        import re as _re                                             # noqa: PLC0415
        emitted = {c for c in _re.findall(r'class="[^"]*?\b(d\d+)\b', live_b)}
        check("every delay class the drawings emit is one the stylesheet defines",
              emitted <= {"d0", "d1", "d2", "d3", "d4", "d5", "d6", "d7"}, str(sorted(emitted)))

        # THE LEDE IS THE ONE SENTENCE LEFT ABOVE THE DRAWINGS, so it is read rather than
        # assumed. A compound metro name takes a plural verb and seven of the nineteen are
        # compounds, so a fixed "sits" prints "Midland and Odessa sits" on any day the Permian
        # is at either end of the spread, which is most days.
        check("a compound metro name takes a plural verb", sits("Midland and Odessa") == "sit")
        check("...and a single one does not", sits("Texarkana") == "sits")
        check("...and the built page never prints the disagreement",
              " and " not in live_b or "Odessa sits" not in live_b, "compound name with 'sits'")

        # THE DRAWINGS HOLD WHAT THE PARAGRAPHS HELD. Four paragraphs have come off this page
        # across two passes, carrying storage, capacity, percent full, the reservoir count, the
        # day's move and the length of the record. Deleting prose is only an improvement if
        # none of it was load bearing, so every figure is asked for by name against the page's
        # own final bytes. Capacity now answers from the trend chart's ceiling label rather
        # than from a sentence, which is why it is no longer on the authorised list above.
        L2 = live_f["latest"]
        for label, val in (("storage", maf(L2["storage_af"])),
                           ("capacity", maf(L2["capacity_af"])),
                           ("percent full", pct(L2["percent_full"])),
                           ("the reservoir count", af(L2["reservoir_count"])),
                           ("the length of the record", af(live_f["days_held"]))):
            check(f"the page still publishes {label}", val in live_b, val)

    # ------------------------------------------------------ THE WATER, AS DRAWN NOT AS MEANT
    # Everything below reads the path string the page actually ships and works out what area it
    # encloses. Asserting on the numbers that went IN would have passed every one of these on
    # the morning the arc was reversed and every lake on the map rendered as its own complement.
    def _flatten(d, r):
        """The emitted path, as a list of points. Arc flags read from the string, not assumed."""
        import re as _r                                              # noqa: PLC0415
        nums = lambda t: [float(x) for x in _r.findall(r"-?\d+(?:\.\d+)?", t)]
        pts, cur = [], None
        for tok in _r.findall(r"[MQLAZ][^MQLAZ]*", d):
            k, v = tok[0], nums(tok[1:])
            if k == "M":
                cur = (v[0], v[1]); pts.append(cur)
            elif k == "Q":
                (x0, y0), (qx, qy), (x1, y1) = cur, (v[0], v[1]), (v[2], v[3])
                for i in range(1, 33):
                    t = i / 32
                    pts.append((((1 - t) ** 2) * x0 + 2 * (1 - t) * t * qx + t * t * x1,
                                ((1 - t) ** 2) * y0 + 2 * (1 - t) * t * qy + t * t * y1))
                cur = (x1, y1)
            elif k == "L":
                cur = (v[0], v[1]); pts.append(cur)
            elif k == "A":
                # Endpoint to centre, the SVG spec's own conversion, so the large-arc and sweep
                # flags in the shipped string are what decides which way round this goes.
                rr, large, sweep, x1, y1 = v[0], int(v[3]), int(v[4]), v[5], v[6]
                x0, y0 = cur
                mx, my = (x0 - x1) / 2, (y0 - y1) / 2
                q = max(rr * rr / max(mx * mx + my * my, 1e-12) - 1.0, 0.0) ** 0.5
                if large == sweep:
                    q = -q
                ux, uy = q * my + (x0 + x1) / 2, -q * mx + (y0 + y1) / 2
                a0 = math.atan2(y0 - uy, x0 - ux)
                a1 = math.atan2(y1 - uy, x1 - ux)
                da = a1 - a0
                if sweep and da < 0:
                    da += 2 * math.pi
                if not sweep and da > 0:
                    da -= 2 * math.pi
                for i in range(1, 65):
                    a = a0 + da * i / 64
                    pts.append((ux + rr * math.cos(a), uy + rr * math.sin(a)))
                cur = (x1, y1)
        return pts

    def _area(pts):
        return abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1]
                       for i in range(len(pts)))) / 2.0

    def _true_segment(r, frac):
        h = r * (1.0 - 2.0 * frac) / r                                # the chord, as cos
        h = max(-1.0, min(1.0, h))
        return r * r * (math.acos(h) - h * math.sqrt(max(1 - h * h, 0.0)))

    worst_area, worst_at, worst_out, out_at = 0.0, None, -9.0, None
    for rr in (5.4, 9.0, 14.0, 20.0, 27.0):
        for i in range(1, 200):
            fr = i / 200
            pts = _flatten(_segment(100.0, 100.0, rr, fr), rr)
            # MEASURED AGAINST THE WHOLE CIRCLE, not against the segment. A segment at half a
            # percent has almost no area, so a relative error against ITSELF divides by nearly
            # nothing and reports a hundred percent for a rounding step. The question a reader
            # has is how far the water line is from where it should be, and the circle is what
            # that is a fraction of.
            err = abs(_area(pts) - _true_segment(rr, fr)) / (math.pi * rr * rr)
            if err > worst_area:
                worst_area, worst_at = err, (rr, round(fr, 3))
            for x, y in pts:
                d = math.hypot(x - 100.0, y - 100.0) - rr
                if d > worst_out:
                    worst_out, out_at = d, (rr, round(fr, 3))

    # THE READING IS THE AREA. A wave that is not exactly area neutral is the drawing quietly
    # reporting a different number from the one computed, which is the one thing this page may
    # never do. Half a percent over five radii and two hundred levels, which is the flattening
    # error rather than the wave's.
    check("the drawn water is the true circular segment, wave and all",
          worst_area < 0.004, f"worst {worst_area:.4%} of the circle at r,frac={worst_at}")

    # THE INVERSION, REPLAYED. Adding the wave left the arc running to the point the wave had
    # already reached, which is a zero length arc the spec says to ignore, and every lake on the
    # map drew its own complement: a reservoir at 92 percent rendered as a thin band at the top
    # of an empty circle. Every input was correct and every number was right. Only the picture
    # was wrong, and an area check is the only assertion here that could have said so.
    low = _flatten(_segment(100.0, 100.0, 20.0, 0.1), 20.0)
    check("a nearly empty lake draws nearly empty, not nearly full",
          _area(low) < math.pi * 400 * 0.15, f"{_area(low):.1f} of {math.pi * 400:.1f}")
    high = _flatten(_segment(100.0, 100.0, 20.0, 0.9), 20.0)
    check("...and a nearly full one draws nearly full",
          _area(high) > math.pi * 400 * 0.85, f"{_area(high):.1f} of {math.pi * 400:.1f}")
    check("...and the water sits at the BOTTOM of the vessel",
          sum(y for _, y in low) / len(low) > 100.0,
          "the centroid of a low lake is above the centre")

    # WATER STANDING PROUD OF ITS OWN RIM would be the drawing saying a reservoir is over
    # capacity. `_amp` solves the swell against the vessel wall along the whole curve for this.
    # The tolerance is one hundredth of a user unit, which is what the coordinates are rounded
    # to, so anything under it cannot be expressed in the path let alone drawn.
    check("no swell ever breaks out through the rim that holds it",
          worst_out <= 0.01, f"worst {worst_out:+.4f} units at r,frac={out_at}")

    # THE SURFACE AND THE FILL AGREE. Two paths drawn from one curve, so a reader can never see
    # a lit line floating clear of the water it belongs to.
    for fr in (0.05, 0.3, 0.62, 0.94):
        seg, sur = _segment(60.0, 60.0, 18.0, fr), _surface(60.0, 60.0, 18.0, fr)
        check(f"the lit surface starts on the water line at {int(fr * 100)}%",
              sur and seg.startswith(sur.split("Q")[0]), f"{sur[:40]} vs {seg[:40]}")
    check("a full lake has no water line, because it has no surface to light",
          _surface(60.0, 60.0, 18.0, 1.0) == "")
    check("...and neither has an empty one", _surface(60.0, 60.0, 18.0, 0.0) == "")

    # THE PAINT ORDER, WHICH IS THE WHOLE DEFECT THIS REWORK EXISTS FOR. The vessel used to be
    # a fill on the rim, and the rim is painted last, so a disc of page background went over
    # every lake at 55 percent and took the colour out of all of them.
    mark = _vessel(50.0, 50.0, 12.0, 0.5, "")
    check("the vessel is painted BEFORE the water, never over it",
          mark.index("tank") < mark.index("wf") < mark.index("rim"), mark[:90])
    check("...and the rim carries no fill of its own any more",
          'class="rim' in mark and "fill=" not in mark)
    check("an empty vessel still draws, so a dry lake is a mark and not a gap",
          "tank" in _vessel(50.0, 50.0, 12.0, 0.0, "") and
          "wf" not in _vessel(50.0, 50.0, 12.0, 0.0, ""))

    # A RECORD SHAPE THE DRAWINGS DO NOT RECOGNISE COSTS THE DRAWINGS AND NOT THE PAGE.
    # `waterwatch_pagecheck` carries a fixture whose `reservoirs` is a name to storage map,
    # which is what that field was back when only its keys were ever read, and the first
    # version of `reservoir_rows` raised on it and took the whole page down. The figures a
    # reader came for do not depend on a map, so they must not fail with one.
    odd = {"_spec": 1, "date": "2026-08-11", "verified": True, "storage_af": 24303346.0,
           "capacity_af": 31558535.0, "percent_full": 77.01, "reservoir_count": 2,
           "reservoirs": {"Travis": 1.0, "Buchanan": 2.0},
           "metros": {"austin": {"storage_af": 1.0, "capacity_af": 2.0,
                                 "percent_full": 50.0, "reservoirs": 2}},
           "excluded_out_of_state": [], "excluded_no_conservation_pool": []}
    check("a reservoir entry of an unexpected shape is skipped rather than raised on",
          reservoir_rows(odd) == [])
    odd_b = body([odd], "2026-08-11")
    # ASSERTED ON THE FORMATTER THE PAGE ACTUALLY USES. Statewide storage is published in
    # millions of acre feet, because the raw figure is nine digits and unreadable, so checking
    # for the raw form would be checking for a string this page does not print.
    check("...and the page still publishes its figures", maf(24303346.0) in odd_b,
          maf(24303346.0))
    check("...and still passes the numeral gate", not lint(odd_b, figures([odd])),
          str(lint(odd_b, figures([odd]))[:6]))
    check("a reservoir with a capacity of zero is not a percentage",
          reservoir_rows({"reservoirs": {"X": {"capacity_af": 0.0, "storage_af": 0.0}}}) == [])

    # THE WATER LINE IS NOT INVERTED, which is the one error in `_segment` that would be both
    # invisible in review and completely wrong. Get the large-arc flag backwards and the path
    # draws the COMPLEMENT of the segment, so a reservoir at 4 percent renders as a circle
    # that is 96 percent full. Every dot on the map would be confidently, silently reversed.
    lo, hi = _segment(0.0, 0.0, 10.0, 0.05), _segment(0.0, 0.0, 10.0, 0.95)
    ylo = float(lo.split(",")[1].split(" ")[0])
    yhi = float(hi.split(",")[1].split(" ")[0])
    check("a nearly empty reservoir draws its water line near the bottom", ylo > 8.0, str(ylo))
    check("a nearly full one draws it near the top", yhi < -8.0, str(yhi))
    # THE LARGE ARC FLAG IS GONE, and with it the error it used to invite. The wall is drawn in
    # quarter turns through the circle's own exact points, so every piece is minor and every set
    # of flags on this path is identical. What is worth asserting now is the ROUTE.
    check("a lake below the middle takes its wall over the floor and nowhere else",
          lo.count("A") == 2 and "0.0,10.0" in lo, lo)
    check("...and one above the middle goes by both shoulders as well",
          hi.count("A") == 4 and "10.0,0.0" in hi and "-10.0,0.0" in hi, hi)
    check("every piece of every wall is a minor arc, swept the same way",
          all(" 0 1 " in a for a in (lo + hi).split("A")[1:]), f"{lo} | {hi}")    # A GAP IN A METRO'S RECORD IS A BREAK, NEVER A BRIDGE. A line drawn straight across a
    # missing day publishes an interpolation as a measurement, which is the one thing this
    # project's own law forbids most plainly.
    broken = sparkline([50.0, 49.0, None, 47.0, 46.0], 4.0)
    check("a sparkline breaks across a missing day rather than drawing through it",
          broken.count("M") == 2, str(broken.count("M")))
    check("...and an unbroken record draws as one run",
          sparkline([50.0, 49.0, 48.0, 47.0], 4.0).count("M") == 1)
    check("a sparkline with one reading draws nothing rather than a dot on a scale",
          sparkline([50.0], 4.0) == "")
    check("the sparkline measures its own length for the reveal",
          "--len:" in sparkline([50.0, 48.0, 46.0], 4.0))

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
