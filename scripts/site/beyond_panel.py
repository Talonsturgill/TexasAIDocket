"""Who is here, and what is being built for them. The two sources beyond ERCOT.

THE RENDERER AND ITS NUMERAL AUTHORISATION LIVE IN ONE MODULE, for the reason this project
has now written down twice: they shipped apart once and the daily page check went red on
figures the collector had measured correctly. Anything that formats a number here authorises
it here.

WHAT THESE TWO PANELS ARE FOR. The rest of the grid page measures ERCOT and stops, because
per site metering is confidential and the page refuses to model what it cannot see. These say
the parts that ARE public: the state names 149 data centers and says when each registered, and
EIA says what generation is operating, planned, retired and cancelled in every Texas county.

WHAT THEY REFUSE TO SAY. What any data center draws. Nothing tested publishes it. Putting a
modelled figure here would trade this page's best property, which is that its gaps are labelled
gaps, for a number nobody can check.
"""
from __future__ import annotations

import json
from pathlib import Path

import numeral_lint

REPO_ROOT = Path(__file__).resolve().parents[2]
ROSTER = REPO_ROOT / "ledger" / "gridwatch" / "datacenters.json"
DC_SERIES = REPO_ROOT / "ledger" / "gridwatch" / "datacenters.jsonl"
GEN_SERIES = REPO_ROOT / "ledger" / "gridwatch" / "generators.jsonl"

MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")
DC_URL = "https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php"


# HOW OLD A READING MAY BE BEFORE THE PAGE SAYS SO. Matched to each source's own cadence
# plus slack for a weekend and a missed run, because a feed that stopped and a feed that is
# merely between publications must not look the same to a reader.
STALE_AFTER_DAYS = {"registry": 4, "generators": 70}


def _last(path: Path, verified_only: bool = True) -> dict | None:
    if not path.exists():
        return None
    best = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if verified_only and not r.get("verified"):
            continue
        best = r
    return best


def load() -> dict:
    roster = json.loads(ROSTER.read_text(encoding="utf-8")) if ROSTER.exists() else {}
    return {"roster": roster, "dc": _last(DC_SERIES), "gen": _last(GEN_SERIES)}


def freshness(data: dict, today: str) -> list[dict]:
    """How old each reading is, and whether that is older than its own source allows.

    THE POINT OF THIS FUNCTION IS THAT A STOPPED COLLECTOR LOOKS LIKE A WORKING ONE. Both
    publish the same last figure forever. The only difference is the read date, so the read
    date is computed here, shown on the page, and checked by the page check rather than
    trusted. A feed that goes quiet has to become visible without anybody remembering to look.
    """
    import datetime as _dt
    now = _dt.date.fromisoformat(today)
    out = []
    for key, label, rec, datefield in (
            ("registry", "Data center registry", data.get("dc"), "date"),
            ("generators", "Generator inventory", data.get("gen"), None)):
        if not rec:
            out.append({"key": key, "label": label, "read": None, "age_days": None,
                        "stale": True, "note": "no verified reading held"})
            continue
        shown = None
        if datefield:
            read = rec.get(datefield)
            shown = f"read {ordinal_date(read)}"
        else:
            # A monthly workbook is dated by its report month, so age is measured from the
            # first of the month after it, which is the earliest the next one could exist.
            y, m = (int(x) for x in rec["month"].split("-"))
            nxt = _dt.date(y + (m == 12), (m % 12) + 1, 1)
            read = nxt.isoformat()
            # SAY WHICH EDITION, NOT WHEN WE FETCHED IT. `read` above is the earliest date a
            # newer workbook could exist and is the right anchor for staleness, but printing
            # it as a read date would tell a reader we fetched the file that day, which is
            # not what happened and not what they need to know about a monthly publication.
            shown = f"{month_label(rec['month'])} edition"
        age = (now - _dt.date.fromisoformat(read)).days
        limit = STALE_AFTER_DAYS[key]
        out.append({"key": key, "label": label, "read": read, "age_days": age,
                    "shown": shown, "stale": age > limit, "limit": limit,
                    "note": "" if age <= limit else
                            f"{age} days since the last verified reading, over the "
                            f"{limit} day limit for this source"})
    return out


# --------------------------------------------------------------------------- formatting
def n0(x) -> str | None:
    return None if x is None else f"{float(x):,.0f}"


def gw(mw) -> str | None:
    if mw is None:
        return None
    v = float(mw) / 1000.0
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


def ordinal_date(iso: str) -> str:
    y, m, d = (int(p) for p in iso.split("-"))
    suf = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return f"{MONTHS[m - 1]} {d}{suf}, {y}"


def month_label(key: str) -> str:
    y, m = (int(p) for p in key.split("-"))
    return f"{MONTHS[m - 1]} {y}"


def e(t) -> str:
    import html
    return html.escape(str(t), quote=True)


# --------------------------------------------------------------------------- the numbers
def figures(data: dict) -> dict:
    """Every number these panels publish, computed here. Nothing downstream computes."""
    f: dict = {"dc": None, "gen": None}
    dc, roster = data.get("dc"), data.get("roster") or {}
    if dc and dc.get("total"):
        years = dc.get("by_year") or {}
        # The current year is deliberately kept separate from the completed ones. It is a
        # part year and a reader comparing it to a full one without being told is being
        # invited to a conclusion the data does not support.
        latest = max(years) if years else None
        f["dc"] = {
            "total": dc["total"],
            "by_year": [{"year": y, "count": c} for y, c in sorted(years.items())],
            "max_year_count": max(years.values()) if years else 0,
            "latest_year": latest,
            "latest_year_count": years.get(latest, 0),
            "distinct_operators": dc.get("distinct_operators", 0),
            "operators": (dc.get("operators") or [])[:8],
            "read": roster.get("read") or dc.get("date"),
            "first_effective": (roster.get("facilities") or [{}])[0].get("effective"),
        }
    gen = data.get("gen")
    if gen and gen.get("operating"):
        op, pl = gen["operating"], gen["planned"]
        ca, re_ = gen["canceled"], gen["retired"]
        tops = sorted(pl["counties"].items(), key=lambda kv: -kv[1]["mw"])[:6]
        f["gen"] = {
            "month": gen["month"],
            "operating_mw": op["total_mw"],
            "planned_mw": pl["total_mw"],
            "canceled_mw": ca["total_mw"],
            "retired_mw": re_["total_mw"],
            "counties": len(op["counties"]),
            "planned_counties": len(pl["counties"]),
            "top_planned": [{"county": c, "mw": v["mw"], "units": v["units"]} for c, v in tops],
            "max_planned_mw": tops[0][1]["mw"] if tops else 0,
            "source_url": gen.get("source_url"),
        }
    return f


# --------------------------------------------------------------------------- the panels
def registry_panel(f: dict) -> str:
    """The count of registered facilities, by the year each one took effect."""
    d = f.get("dc")
    if not d:
        return ""
    top = max(d["max_year_count"], 1)
    bars = "".join(
        f'<li class="ryr"><span class="rk">{e(y["year"])}</span>'
        f'<span class="rb" style="width:{y["count"] / top * 100.0:.1f}%"></span>'
        f'<span class="rv num">{n0(y["count"])}</span></li>'
        for y in d["by_year"])
    ops = "".join(
        # A <cite>, because these are the Comptroller's spellings and not this project's
        # prose. "Whinstone US, Inc." tripped the first person check on the word "US", which
        # is the same class of false positive the sibling hit on "the US Army Corps": house
        # style governs what we write and stops at the quotation mark.
        f'<li><span class="on"><cite>{e(o["name"])}</cite></span>'
        f'<span class="os num">{n0(o["sites"])}</span></li>' for o in d["operators"])
    return f"""<section class="beyond" data-reveal>
  <h2>Who is here</h2>
  <p class="qnote">The state names them. <a href="{DC_URL}">The Comptroller's registry</a>
  lists every facility holding the data center exemption.</p>

  <p class="blede"><strong class="num">{n0(d['total'])}</strong> data centers are registered
  in Texas. <strong class="num">{n0(d['latest_year_count'])}</strong> of them took effect
  this year.</p>

  <h3>By the year each took effect</h3>
  <ul class="ryears" data-prose="data">{bars}</ul>
  <p class="qnote">{e(d['latest_year'])} is a part year and is not finished.</p>

  <h3>Who runs them</h3>
  <ul class="ops" data-prose="data">{ops}</ul>
  <p class="qnote"><strong class="num">{n0(d['distinct_operators'])}</strong> operators in
  all. A site with more than one operator counts for each.</p>
</section>"""


def generation_panel(f: dict) -> str:
    """What is operating, planned, retired and cancelled, and where the planning is."""
    g = f.get("gen")
    if not g:
        return ""
    top = max(g["operating_mw"], 1)
    rows = [("Operating", g["operating_mw"]), ("Planned", g["planned_mw"]),
            ("Canceled or postponed", g["canceled_mw"]), ("Retired", g["retired_mw"])]
    bars = "".join(
        f'<div class="qrow"><div class="qlab"><span class="qk">{lab}</span>'
        f'<span class="qv num">{gw(mw)} GW</span></div>'
        f'<div class="qbar"><div class="qfill" style="width:{mw / top * 100.0:.1f}%"></div>'
        f'</div></div>' for lab, mw in rows)
    cmax = max(g["max_planned_mw"], 1)
    counties = "".join(
        f'<li class="ryr"><span class="rk"><cite>{e(c["county"])}</cite></span>'
        f'<span class="rb" style="width:{c["mw"] / cmax * 100.0:.1f}%"></span>'
        f'<span class="rv num">{n0(c["mw"])}</span></li>' for c in g["top_planned"])
    return f"""<section class="beyond" data-reveal>
  <h2>What is being built for them</h2>
  <p class="qnote">Generation in Texas, by county, from
  <a href="{e(g['source_url'])}">EIA's generator inventory</a>.</p>

  <div class="qgap">{bars}</div>
  <p class="qnote"><strong class="num">{n0(g['counties'])}</strong> counties hold operating
  generation. <strong class="num">{n0(g['planned_counties'])}</strong> have some planned.</p>

  <h3>Where the planning is, in megawatts</h3>
  <ul class="ryears" data-prose="data">{counties}</ul>
  <p class="qnote">Nameplate capacity, which is what a plant is rated to produce and not what
  it produced. This is supply. It is not a claim about who will use it.</p>
</section>"""


def source_line(fresh: dict) -> str:
    """One line per feed saying when it was read, and saying so LOUDLY when it went quiet.

    A reader cannot tell a live figure from a frozen one, and neither can anyone maintaining
    this, so the read date ships beside the figure rather than in a commit log.
    """
    if fresh.get("stale"):
        return (f'<p class="srcline stale" data-prose="data"><strong>{e(fresh["label"])} '
                f'has not been read recently.</strong> {e(fresh["note"])}. The figures below '
                f'are the last verified reading and are not current.</p>')
    return (f'<p class="srcline" data-prose="data"><span class="srcdot" aria-hidden="true">'
            f'</span>{e(fresh["label"])}, {e(fresh["shown"])}.</p>')


def panels(data: dict, today: str) -> str:
    f = figures(data)
    fr = {x["key"]: x for x in freshness(data, today)}
    out = registry_panel(f)
    if out:
        out = out.replace("<h2>Who is here</h2>",
                          "<h2>Who is here</h2>\n  " + source_line(fr["registry"]), 1)
    gen = generation_panel(f)
    if gen:
        gen = gen.replace("<h2>What is being built for them</h2>",
                          "<h2>What is being built for them</h2>\n  "
                          + source_line(fr["generators"]), 1)
    return out + gen


# --------------------------------------------------------------------------- the gate
def authorised(f: dict) -> set[str]:
    """Every numeral string these panels may show, from the same calls that render them."""
    acc = numeral_lint.Authorised()
    add = acc.add
    d = f.get("dc")
    if d:
        add(n0(d["total"]), n0(d["latest_year_count"]), n0(d["distinct_operators"]),
            d["latest_year"], ordinal_date(d["read"]))
        for y in d["by_year"]:
            add(y["year"], n0(y["count"]))
        for o in d["operators"]:
            add(n0(o["sites"]))
    g = f.get("gen")
    if g:
        add(gw(g["operating_mw"]), gw(g["planned_mw"]), gw(g["canceled_mw"]),
            gw(g["retired_mw"]), n0(g["counties"]), n0(g["planned_counties"]),
            month_label(g["month"]))
        for c in g["top_planned"]:
            add(n0(c["mw"]), n0(c["units"]))
    return acc.set


def lint(html_body: str, f: dict, fresh: list[dict] | None = None) -> list[str]:
    allowed = authorised(f)
    for x in fresh or []:
        if x.get("read"):
            allowed.add(ordinal_date(x["read"]))
        if x.get("age_days") is not None:
            allowed |= {n0(x["age_days"]), n0(x.get("limit"))}
    return numeral_lint.scan(html_body, allowed)


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    data = load()
    f = figures(data)
    check("the registry reading is held", bool(f.get("dc")))
    check("the generator reading is held", bool(f.get("gen")))

    today = "2026-08-18"
    html = panels(data, today)
    fr = freshness(data, today)
    check("both panels render", html.count('class="beyond"') == 2)
    check("the registry year bars are present", 'class="ryears"' in html)
    check("the operator list is present", 'class="ops"' in html)

    stray = lint(html, f, fr)
    check("every numeral traces to a computation", not stray, ", ".join(stray[:8]))
    planted = html.replace("</section>", "<p>An untraceable 8675309.</p></section>", 1)
    check("...and an invented one is caught", bool(lint(planted, f, fr)))

    check("every panel says when it was read", html.count('class="srcline') == 2, html.count('srcline'))
    # A STOPPED FEED MUST NOT LOOK LIKE A WORKING ONE. Both publish the same last figure
    # forever; only the read date differs, so the stale path is exercised rather than trusted.
    old = {"key": "registry", "label": "Data center registry", "read": "2026-01-01",
           "age_days": 230, "stale": True, "limit": 4, "shown": "read January 1st, 2026",
           "note": "230 days since the last verified reading, over the 4 day limit"}
    check("a stale feed says so in the copy", "not current" in source_line(old))
    # A MONTHLY SOURCE MUST NOT CLAIM A READ DATE IT DOES NOT HAVE. The staleness anchor for
    # a monthly workbook is the first of the following month, which is not when anyone
    # fetched it, and printing it as "read" would misstate provenance on every render.
    gfresh = next(x for x in fr if x["key"] == "generators")
    check("the monthly source names its edition, not a read date",
          "edition" in (gfresh.get("shown") or ""), str(gfresh.get("shown")))
    check("...and the page does not claim it was read that day",
          "read July" not in html and "read August 1st" not in html)
    check("...and is marked for a stylesheet", 'class="srcline stale"' in source_line(old))

    # THE LAW THIS PAIR EXISTS UNDER. Neither panel may imply a per site draw.
    low = html.lower()
    for phrase in ("draws", "consumes", "uses about", "per site", "each data center uses"):
        check(f"no per site load claim: {phrase!r}", phrase not in low)
    check("no reliability verdict", not any(
        w in low for w in ("shortfall", "blackout", "all clear", "at risk")))
    check("the part year is labelled", "part year" in low)
    check("nameplate is named as nameplate", "nameplate" in low)
    # THE STATE'S SPELLINGS ARE QUOTED, NOT ADOPTED. An operator called "Whinstone US, Inc."
    # is not this project writing "us", and a county is not this project's word either.
    check("operator names are marked as quoted", "<cite>" in html)
    check("...and every operator is inside one",
          all(f"<cite>{o['name']}</cite>" in html.replace("&amp;", "&")
              or "&" in o["name"] for o in (f["dc"]["operators"] if f.get("dc") else [])),
          "an operator name is not cited")

    print("\nbeyond_panel self-test " + ("clean" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
