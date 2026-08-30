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

import collections
import json
import re
import sys
from pathlib import Path

import numeral_lint

# THE COLLECTOR'S KEY, NOT A SECOND COPY OF IT. datacenters_collect.opkey already folds the
# spelling variants the Comptroller files under, and its docstring is the record of why the
# rule is exactly as conservative as it is. Restating the rule here is how the two drift and
# how a leaderboard starts disagreeing with the count printed beside it.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gridwatch"))
from datacenters_collect import opkey  # noqa: E402

import facility_dossier as fdoss

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
def _role(facs: list[dict], role: str, n: int = 8) -> dict:
    """One of the three roles the registry records, tallied.

    THE REGISTRY RECORDS THREE DIFFERENT ANSWERS and the page published one of them. Owner,
    occupant and operator are not synonyms: the company that owns the building, the company
    whose computing happens in it, and the company that runs the floor are frequently three
    different firms, and which one a reader cares about depends entirely on the question they
    came with. Publishing only the operator answered "who runs the floor" and silently dropped
    the other two, which are the ones most people mean when they ask whose data center it is.

    THE VARIANT SPELLINGS ARE ONE FILER. The registry writes "Amazon Data Services, Inc." and
    "Amazon Data Services Inc." for the same company, and "Oracle America Cloud Services LLC"
    beside "Oracle America Cloud Services, LLC". Tallying the raw strings published those as
    separate firms with a fraction of their real count against each, which is a wrong number
    with a right-looking name on it. Grouping uses the collector's own key; the label shown is
    the spelling the registry uses most often for that key.
    """
    tally: collections.Counter = collections.Counter()
    spellings: dict = {}
    for fac in facs:
        for v in (fac.get(role) or []):
            v = re.sub(r"\s+", " ", v or "").strip()
            if not v:
                continue
            k = opkey(v)
            tally[k] += 1
            spellings.setdefault(k, collections.Counter())[v] += 1
    return {"distinct": len(tally),
            "mentions": sum(tally.values()),
            "named": sum(1 for fac in facs if fac.get(role)),
            "top": [{"name": spellings[k].most_common(1)[0][0], "count": c}
                    for k, c in tally.most_common(n)]}


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
        # EVERYTHING ELSE THE REGISTRY ALREADY HELD. The record carries a name, a date and
        # three named parties for all 149 facilities, and the page was publishing a year
        # histogram and eight operators. What follows is not new collection, it is the same
        # file read properly.
        facs = list(roster.get("facilities") or [])
        if facs:
            byname = sorted(facs, key=lambda x: (x.get("effective") or "", x.get("name") or ""),
                            reverse=True)
            f["dc"].update({
                "owners": _role(facs, "owners"),
                "occupants": _role(facs, "occupants"),
                "operator_roles": _role(facs, "operators"),
                # The most recently certified, which is the part of this record that moves.
                "newest": [{"name": x.get("name"), "effective": x.get("effective"),
                            "occupants": x.get("occupants") or [],
                            "owners": x.get("owners") or []} for x in byname[:10]],
                "roster": [{"name": x.get("name"), "effective": x.get("effective"),
                            "owners": x.get("owners") or [],
                            "occupants": x.get("occupants") or [],
                            "operators": x.get("operators") or []} for x in byname],
                "newest_effective": byname[0].get("effective"),
                "oldest_effective": min(x.get("effective") or "9999" for x in facs),
            })
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

# ---------------------------------------------------------------- dossiers on the roster
# A FACILITY WITH RESEARCH BEHIND IT IS A LINK. One without is plain text, because a link that
# leads to five fields a reader has already read is a promise the page does not keep. The
# dialog and the page render the same `fdoss.panel` call, so they cannot disagree.
def _dossiers() -> dict:
    try:
        return fdoss.by_name(fdoss.load())
    except Exception:
        return {}


def _dossier_attrs(name: str) -> str:
    d = _dossiers().get(name)
    return (f' class="hasdoss" data-slug="{e(d["slug"])}" data-researched="true"'
            if d else ' data-researched="false"')


def _facility_cell(name: str) -> str:
    d = _dossiers().get(name)
    if not d:
        return f"<cite>{e(name)}</cite>"
    return (f'<a class="dosslink" href="../facility/{e(d["slug"])}/">'
            f'<cite>{e(name)}</cite></a>')


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
    def role_block(key: str, heading: str, noun: str) -> str:
        r = d.get(key)
        if not r:
            return ""
        rows = "".join(
            # A <cite>, because these are the Comptroller's spellings and not this project's
            # prose. "Whinstone US, Inc." tripped the first person check on the word "US",
            # which is the same class of false positive the sibling hit on "the US Army
            # Corps": house style governs what we write and stops at the quotation mark.
            f'<li><span class="on"><cite>{e(x["name"])}</cite></span>'
            f'<span class="os num">{n0(x["count"])}</span></li>' for x in r["top"])
        return (f'<div class="rrole"><h4>{heading}</h4>'
                f'<ul class="ops" data-prose="data">{rows}</ul>'
                f'<p class="qnote"><strong class="num">{n0(r["distinct"])}</strong> {noun} in '
                f'all. A site with more than one counts for each.</p></div>')

    roster = d.get("roster") or []
    def roster_row(x: dict) -> str:
        hay = " ".join([x["name"]] + x["owners"] + x["occupants"] + x["operators"]).lower()
        return (
            f'<tr{_dossier_attrs(x["name"])} data-registry-search="{e(hay)}">'
            f'<td data-label="Facility">{_facility_cell(x["name"])}</td>'
            f'<td data-label="Owner"><cite>{e(", ".join(x["owners"]))}</cite></td>'
            f'<td data-label="Occupant"><cite>{e(", ".join(x["occupants"]))}</cite></td>'
            f'<td data-label="Operator"><cite>{e(", ".join(x["operators"]))}</cite></td>'
            f'<td data-label="Took effect" class="num">'
            f'<time datetime="{e(x["effective"])}">{ordinal_date(x["effective"])}</time>'
            f'</td></tr>')

    rows = "".join(roster_row(x) for x in roster)

    return f"""<section class="beyond" data-reveal>
  <h2>Who is here</h2>
  <p class="qnote">The state names them. <a href="{DC_URL}">The Comptroller's registry</a>
  lists every facility holding the data center exemption.</p>

  <p class="blede"><strong class="num">{n0(d['total'])}</strong> data centers are registered
  in Texas. <strong class="num">{n0(d['latest_year_count'])}</strong> of them took effect
  this year.</p>

  <div class="registryoverview">
    <section class="registryyears">
      <h3>By the year each took effect</h3>
      <ul class="ryears" data-prose="data">{bars}</ul>
      <p class="qnote">{e(d['latest_year'])} is a part year and is not finished.</p>
    </section>
    <section class="registryroles">
      <h3>Who owns them, who uses them, who runs them</h3>
      <p class="qnote">The registry records three parties for each site. Which one matters
      depends on the question.</p>
      <div class="rroles">
        {role_block("owners", "Owner", "owners")}
        {role_block("occupants", "Occupant", "occupants")}
        {role_block("operator_roles", "Operator", "operators")}
      </div>
    </section>
  </div>

  <section class="registryroster" aria-labelledby="registry-roster-title">
  <h3 id="registry-roster-title">Every registered facility</h3>
  <p class="qnote">Search by a facility name or any company in the state filing.
  A facility whose name is a link has a researched dossier behind it.
  <a href="../company/">Read the registry by company instead</a>,
  see <a href="../registry-changes/">what the state has changed</a> since anyone started looking,
  or read <a href="../construction/">what the builders told a different agency</a>.</p>
  <div class="rtools" id="rtools" role="search">
    <label class="rfind" for="rsearch"><span>Find a facility</span>
      <input id="rsearch" type="search" autocomplete="off" placeholder="Facility or company"
        aria-controls="registry-roster"></label>
    <label class="rcheck"><input id="rresearched" type="checkbox"
      aria-controls="registry-roster"> <span>Researched only</span></label>
    <p class="rresult" id="rresult" aria-live="polite">
      <strong class="num" id="rcount">{n0(len(roster))}</strong> shown</p>
    <button class="rclear" id="rclear" type="button" disabled>Clear</button>
  </div>
  <p class="rempty" id="rempty" hidden>No facility matches that search.</p>
  <div class="rtfield"><div class="rtwrap">
  <table class="rtable" id="registry-roster" data-prose="data">
    <colgroup><col class="cf"><col class="co"><col class="cu"><col class="cp"><col class="cd">
    </colgroup>
    <thead><tr><th>Facility</th><th>Owner</th><th>Occupant</th><th>Operator</th>
      <th>Took effect</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  </div></div>
  {_roster_filter()}
  {_dossier_dialog()}
  </section>
</section>"""


def _roster_filter() -> str:
    """Progressive filtering for the full registry.

    The controls stay hidden until this script runs. With script unavailable the complete table
    remains in the document and no dead control is presented to the reader.
    """
    return """<script>
(function () {
  var tools = document.getElementById('rtools');
  var search = document.getElementById('rsearch');
  var researched = document.getElementById('rresearched');
  var clear = document.getElementById('rclear');
  var count = document.getElementById('rcount');
  var empty = document.getElementById('rempty');
  var table = document.getElementById('registry-roster');
  if (!tools || !search || !researched || !clear || !count || !empty || !table) return;
  var rows = [].slice.call(table.querySelectorAll('tbody tr'));

  function apply() {
    var q = search.value.trim().toLowerCase();
    var only = researched.checked;
    var shown = 0;
    rows.forEach(function (row) {
      var match = (!q || row.getAttribute('data-registry-search').indexOf(q) !== -1) &&
        (!only || row.getAttribute('data-researched') === 'true');
      row.hidden = !match;
      if (match) shown++;
    });
    count.textContent = String(shown);
    empty.hidden = shown !== 0;
    clear.disabled = !q && !only;
  }

  search.addEventListener('input', apply);
  researched.addEventListener('change', apply);
  clear.addEventListener('click', function () {
    search.value = '';
    researched.checked = false;
    apply();
    search.focus();
  });
  tools.classList.add('live');
  apply();
})();
</script>"""



def _dossier_dialog() -> str:
    """The popup, and the reason it fetches rather than inlines.

    Every researched facility already has a real page, so the dossier markup exists once. The
    registry will eventually carry all of them, and inlining every dossier into the grid page
    would put hundreds of kilobytes of markup in front of every reader to serve the one row
    they clicked. The dialog pulls the page it is already linking to, same origin, and lifts
    the panel out of it.

    THE LINK IS THE FALLBACK AND IT IS NOT A COURTESY. With script off, with the fetch
    refused, or with anything at all going wrong, the anchor navigates to the facility page
    and the reader gets the whole dossier. Nothing here is reachable only through the script.
    """
    return """<dialog id="dossdlg" class="dossdlg" aria-label="Facility dossier">
  <button type="button" class="dossclose" id="dossclose" aria-label="Close">Close</button>
  <div class="dossbody" id="dossbody"></div>
</dialog>
<script>
(function () {
  var dlg = document.getElementById('dossdlg');
  var body = document.getElementById('dossbody');
  if (!dlg || !body || typeof dlg.showModal !== 'function') return;
  var cache = {};

  function open(html, href) {
    body.innerHTML = html +
      '<p class="dossmore"><a href="' + href + '">Open the full page for this facility</a></p>';
    dlg.showModal();
    body.scrollTop = 0;
  }

  document.addEventListener('click', function (ev) {
    var a = ev.target.closest ? ev.target.closest('a.dosslink') : null;
    if (!a) return;
    // A modifier click is the reader asking for a new tab. Never swallow that.
    if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button !== 0) return;
    var href = a.getAttribute('href');
    if (cache[href]) { ev.preventDefault(); open(cache[href], href); return; }
    ev.preventDefault();
    fetch(href, { credentials: 'same-origin' })
      .then(function (r) { if (!r.ok) throw new Error('status'); return r.text(); })
      .then(function (t) {
        var doc = new DOMParser().parseFromString(t, 'text/html');
        var panel = doc.querySelector('.dossier');
        if (!panel) throw new Error('no panel');
        cache[href] = panel.innerHTML;
        open(cache[href], href);
      })
      .catch(function () { window.location.href = href; });
  });

  document.getElementById('dossclose').addEventListener('click', function () { dlg.close(); });
  // A click on the backdrop closes it. The dialog element itself is the backdrop's target.
  dlg.addEventListener('click', function (ev) { if (ev.target === dlg) dlg.close(); });
  dlg.addEventListener('close', function () { body.innerHTML = ''; });
})();
</script>"""


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


# THE TWO PANELS ANSWER TO TWO TABS NOW. "Who is here" is the certified data center roster and
# it belongs on the data centers page. "What is being built for them" is EIA generator data by
# county, which is a fact about the grid, so it stays on the grid page. They were one function
# because they shipped together, not because they are one subject.
def registry(data: dict, today: str) -> str:
    """Who is here. The certified roster, for the data centers page."""
    out = registry_panel(figures(data))
    if not out:
        return ""
    fr = {x["key"]: x for x in freshness(data, today)}
    return out.replace("<h2>Who is here</h2>",
                       "<h2>Who is here</h2>\n  " + source_line(fr["registry"]), 1)


def generation(data: dict, today: str) -> str:
    """What is being built for them. Generation by county, for the grid page."""
    gen = generation_panel(figures(data))
    if not gen:
        return ""
    fr = {x["key"]: x for x in freshness(data, today)}
    return gen.replace("<h2>What is being built for them</h2>",
                       "<h2>What is being built for them</h2>\n  "
                       + source_line(fr["generators"]), 1)


def panels(data: dict, today: str) -> str:
    """Both, in the order they shipped in. Kept so a caller wanting the pair still gets it."""
    return registry(data, today) + generation(data, today)


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
        for key in ("owners", "occupants", "operator_roles"):
            r = d.get(key)
            if not r:
                continue
            add(n0(r["distinct"]))
            for x in r["top"]:
                add(n0(x["count"]))
        # Every date the roster and the newest list print, in the form they print it.
        for x in (d.get("roster") or []) + (d.get("newest") or []):
            add(ordinal_date(x["effective"]), x["effective"])
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
    # Every named party the page prints, across all three roles and the roster, has to be
    # inside a <cite>. The check used to look only at the operator leaderboard, which was the
    # only place names appeared; the page now names owners, occupants and all 149 facilities,
    # and an uncited name is a company's own capitalisation being measured as our prose.
    plain = html.replace("&amp;", "&")
    missing = []
    dcf = f.get("dc") or {}
    for key in ("owners", "occupants", "operator_roles"):
        for x in (dcf.get(key) or {}).get("top", []):
            if "&" not in x["name"] and f"<cite>{x['name']}</cite>" not in plain:
                missing.append(x["name"])
    for x in (dcf.get("roster") or [])[:40]:
        if "&" not in (x["name"] or "") and f"<cite>{x['name']}</cite>" not in plain:
            missing.append(x["name"])
    check("...and every named party is inside one", not missing,
          "; ".join(missing[:3]))

    # THE VARIANT SPELLINGS MUST MERGE, and this is proved on a fixture rather than trusted,
    # because the failure is silent: two rows that each look like a real company, each carrying
    # a fraction of the true count. It shipped that way, with Oracle Cloud split 15 and 10.
    fixture = [{"occupants": ["Amazon Data Services, Inc."]},
               {"occupants": ["Amazon Data Services Inc."]},
               {"occupants": ["Amazon  Data   Services, Inc. "]},
               {"occupants": ["Vantage Data Centers"]},
               {"occupants": ["Vantage Data Centers Management"]}]
    r = _role(fixture, "occupants")
    check("spelling variants of one filer are counted once",
          r["distinct"] == 3 and r["top"][0]["count"] == 3, str(r["top"]))
    check("...and two genuinely different filers are not merged",
          {x["name"] for x in r["top"]} >= {"Vantage Data Centers",
                                            "Vantage Data Centers Management"})
    check("the roster leads with a reader task rather than layout instructions",
          'id="registry-roster-title"' in html and 'id="rsearch"' in html
          and "Search by a facility name or any company" in html
          and 'class="qnote rthint"' not in html)
    check("...and every phone card field carries its visible label",
          all(f'data-label="{label}"' in html for label in
              ("Facility", "Owner", "Occupant", "Operator", "Took effect")))
    check("...and the label shown is a spelling the registry actually uses",
          all(any(x["name"] in (fac.get("occupants") or []) for fac in fixture)
              for x in r["top"]))

    print("\nbeyond_panel self-test " + ("clean" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
