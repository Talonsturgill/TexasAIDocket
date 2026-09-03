"""The Queue Gap. How much large load asked ERCOT for power, and how much is drawing it.

THE RENDERER AND ITS NUMERAL AUTHORISATION LIVE IN ONE MODULE, deliberately. The sibling
project shipped those in two files once and the daily page check went red on figures its own
collector had measured correctly, because the two drifted. Anything that formats a number here
also authorises it here, three lines away.

WHAT THIS PANEL IS FOR. The rest of the grid page measures yesterday. This measures the
distance between what has been asked for and what exists, which is the question every other
one on this beat resolves to: whether a county's water matters, whether a comment window
matters, whether a bill matters, all depend on how much of the queue is real.

WHAT IT REFUSES TO SAY. Whether the queue is real. The page shows the stages and the reader
concludes. A queue is a pipeline with multi-year lead times, so a low share drawing power today
is partly just what a queue IS, and a design that made the reader feel otherwise would be
publishing a verdict this page has promised not to publish. Same reason the gauge is a bar and
never a dial.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

import numeral_lint

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER = REPO_ROOT / "ledger" / "gridwatch" / "queue.jsonl"
REQUESTED = REPO_ROOT / "config" / "gridwatch" / "queue_requested.json"

MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")


def load(ledger: Path = LEDGER, requested: Path = REQUESTED) -> dict:
    recs = []
    if ledger.exists():
        for line in ledger.read_text(encoding="utf-8").splitlines():
            if line.strip():
                recs.append(json.loads(line))
    recs.sort(key=lambda r: r.get("month", ""))
    ask = json.loads(requested.read_text(encoding="utf-8")) if requested.exists() else {}
    return {"records": recs, "requested": ask}


# --------------------------------------------------------------------------- formatting
def gw(mw) -> str | None:
    """Megawatts as gigawatts. The unit a reader can hold.

    A TRAILING .0 IS DROPPED. "410 GW" is the figure; "410.0 GW" is the same figure wearing a
    precision it does not have, and the queue is stated by ERCOT as approximately 410. The
    decimal stays wherever it carries information, so 4.4 keeps it.
    """
    if mw is None:
        return None
    v = float(mw) / 1000.0
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


def n0(x) -> str | None:
    return None if x is None else f"{float(x):,.0f}"


def pct(x) -> str | None:
    """Same rule as gw(): no decimal where there is no decimal to report."""
    if x is None:
        return None
    v = float(x)
    return f"{v:.0f}" if abs(v - round(v)) < 0.05 else f"{v:.1f}"


def times(x) -> str | None:
    return None if x is None else f"{float(x):.1f}"


def ordinal_date(iso: str) -> str:
    """August 17th, 2026. The house form, month first, ordinal day."""
    y, m, d = (int(p) for p in iso.split("-"))
    suf = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return f"{MONTHS[m - 1]} {d}{suf}, {y}"


def month_label(key: str) -> str:
    y, m = (int(p) for p in key.split("-"))
    return f"{MONTHS[m - 1]} {y}"


# --------------------------------------------------------------------------- the numbers
def figures(data: dict) -> dict:
    """Every number this panel publishes, computed here, from the record.

    Nothing downstream computes. The renderer formats what this returns and authorised() permits
    what this returns, so a figure not in here cannot reach a reader.
    """
    live = [r for r in data["records"] if r.get("verified")]
    ask = data.get("requested") or {}
    f: dict = {
        "latest": None,
        "series": [],
        "requested": None,
        "months_held": len(data["records"]),
        "months_verified": len(live),
    }
    if ask.get("requested_gw"):
        f["requested"] = {
            "gw": float(ask["requested_gw"]),
            "mw": float(ask["requested_gw"]) * 1000.0,
            "dc_share_pct": ask.get("data_center_share_pct"),
            "as_of": ask.get("as_of"),
            "source_url": ask.get("source_url"),
            "source_title": ask.get("source_title"),
        }
    if not live:
        return f

    last = live[-1]
    approved = float(last["approved_to_energize_mw"])
    drawing = float(last["observed_operational_mw"])
    f["latest"] = {
        "month": last["month"],
        "reported_for": last.get("reported_for"),
        "published": last.get("published"),
        "source_url": last.get("source_url"),
        "approved_mw": approved,
        "drawing_mw": drawing,
        "drawing_share_of_approved_pct": drawing / approved * 100.0 if approved else None,
        "peak_record_mw": last.get("month_peak_record_mw"),
    }
    if f["requested"]:
        req = f["requested"]["mw"]
        f["latest"]["approved_share_of_requested_pct"] = approved / req * 100.0
        f["latest"]["drawing_share_of_requested_pct"] = drawing / req * 100.0
        if last.get("month_peak_record_mw"):
            f["latest"]["requested_vs_peak_times"] = req / float(last["month_peak_record_mw"])

    f["series"] = [{"month": r["month"],
                    "approved_mw": float(r["approved_to_energize_mw"]),
                    "drawing_mw": float(r["observed_operational_mw"])}
                   for r in live]
    # THE TIMELINE KEEPS THE MONTHS THE SERIES DROPS. `series` is verified-only because it is
    # what `change` measures and what authorised() permits, and an unverified month has no
    # number to contribute to either. But the CHART drew off `series` and so closed the gap
    # silently: May 2026 has no Monthly Operational Overview yet, the collector wrote the
    # explicit unverified record the rules require, and the picture then set April beside June
    # as though they were adjacent. The collector paid for that honesty and the renderer spent
    # it. The timeline carries every month the record holds, verified or not, and a month with
    # no reading publishes no number: it gets its name and a mark saying nothing was published.
    #
    # ONE SLOT PER MONTH, NOT ONE PER RECORD, and this drew one per record until 2026-09-03.
    #
    # The ledger is APPEND ONLY and that is correct. A month with no Monthly Operational
    # Overview gets an explicit unverified record every time the collector looks, because a
    # failed read writes what it found and never carries yesterday's number forward. Three days
    # of looking at August wrote three honest lines saying nothing was published.
    #
    # The chart then drew three Augusts. The published page carried two, a fresh build made
    # three, and the count went up by one every day the overview stayed unpublished, so
    # `site_fresh_check` went red on `main` and would have gone red again the next morning
    # however many times it was rebuilt. Rebuilding was the loudest wrong answer available: it
    # clears the gate for a day and puts a fourth August on the live page.
    #
    # A month axis is one slot per month. The record that speaks for a month is the VERIFIED
    # one if there is one, whatever order the lines are in, because a month can be unverified
    # for days and then publish, and last-wins would then throw the reading away. Where none is
    # verified the latest look is the one that stands, and it says the same thing every other
    # look said.
    by_month = {}
    for r in sorted(data["records"], key=lambda r: (r["month"], str(r.get("read_at") or ""))):
        held = by_month.get(r["month"])
        if held is None or not held.get("verified"):
            by_month[r["month"]] = r
    f["timeline"] = [{"month": r["month"],
                      "verified": bool(r.get("verified")),
                      "approved_mw": (float(r["approved_to_energize_mw"])
                                      if r.get("verified") else None),
                      "drawing_mw": (float(r["observed_operational_mw"])
                                     if r.get("verified") else None)}
                     for _, r in sorted(by_month.items())]
    if len(f["series"]) >= 2:
        first, latest = f["series"][0], f["series"][-1]
        f["change"] = {
            "months": len(f["series"]),
            "from_month": first["month"],
            "drawing_change_mw": latest["drawing_mw"] - first["drawing_mw"],
            "approved_change_mw": latest["approved_mw"] - first["approved_mw"],
        }
    return f


# --------------------------------------------------------------------------- the visuals
def gap_bar(f: dict) -> str:
    """THE ONE PICTURE. Asked for, against drawing, on a single scale.

    Both bars share one axis, which is the entire point: a reader sees the distance without
    reading a number or doing arithmetic. One hue at one intensity, per the page's standing
    rule, because the length is the message and a color ramp would be a verdict.

    The drawing bar is given a floor of 0.35% so it stays visible. At true scale it is four
    thousandths of the other and would render as nothing, and a bar that shows nothing reads as
    a broken widget rather than as a small number. The figure beside it is exact.
    """
    L, R = f.get("latest"), f.get("requested")
    if not (L and R):
        return ""
    share = L["drawing_mw"] / R["mw"] * 100.0
    return f"""<div class="qgap">
  <div class="qrow">
    <div class="qlab"><span class="qk">Asked for</span>
      <span class="qv num">{gw(R['mw'])} GW</span></div>
    <div class="qbar"><div class="qfill" style="width:100%"></div></div>
  </div>
  <div class="qrow">
    <div class="qlab"><span class="qk">Drawing power</span>
      <span class="qv num">{gw(L['drawing_mw'])} GW</span></div>
    <div class="qbar"><div class="qfill" style="width:{max(share, 0.35):.2f}%"></div></div>
  </div>
</div>"""


def anchor_bar(f: dict) -> str:
    """What 410 GW is, next to the biggest thing the grid has ever done.

    A gigawatt figure means nothing on its own. Against the state's own record peak it means
    something immediately, and both numbers are measured rather than framed.
    """
    L, R = f.get("latest"), f.get("requested")
    if not (L and R and L.get("peak_record_mw")):
        return ""
    peak = float(L["peak_record_mw"])
    return f"""<div class="qgap">
  <div class="qrow">
    <div class="qlab"><span class="qk">The queue</span>
      <span class="qv num">{gw(R['mw'])} GW</span></div>
    <div class="qbar"><div class="qfill" style="width:100%"></div></div>
  </div>
  <div class="qrow">
    <div class="qlab"><span class="qk">Record peak, all of Texas</span>
      <span class="qv num">{gw(peak)} GW</span></div>
    <div class="qbar"><div class="qfill" style="width:{peak / R['mw'] * 100.0:.1f}%"></div></div>
  </div>
</div>"""


def stages(f: dict) -> str:
    """Three stages, each measured, none inferred.

    ERCOT's own deck shows five. The middle two are drawn in a chart image with no text layer,
    so they are not collected and not shown. Three stages that can be checked beat five that
    can't.
    """
    L, R = f.get("latest"), f.get("requested")
    if not (L and R):
        return ""
    rows = [("Asked for", R["mw"], None),
            ("Cleared to switch on", L["approved_mw"], L.get("approved_share_of_requested_pct")),
            ("Actually drawing", L["drawing_mw"], L.get("drawing_share_of_requested_pct"))]
    out = []
    for label, mw, share in rows:
        pctlab = f'<span class="qs">{pct(share)}%</span>' if share is not None else \
                 '<span class="qs">100%</span>'
        out.append(
            f'<li><span class="qk">{label}</span>'
            f'<span class="qv num">{gw(mw)} GW</span>{pctlab}</li>')
    return f'<ol class="qstages" data-prose="data">{"".join(out)}</ol>'


PLOT_MAX = 76.0  # per cent of the plot the tallest bar may use; the rest is label room


def flatline(f: dict) -> str:
    """The series, as a readable instrument rather than a picture of bars.

    WHAT WAS WRONG WITH THE FIRST VERSION. It was six pairs of rectangles with month names
    under them and no values anywhere, which asks a reader to take the shape on trust. The
    point of the panel is that these are MEASURED figures, so the figures have to be on the
    page. Owner's call, and right.

    HTML BARS RATHER THAN SVG, for three reasons that all matter here. Type never distorts,
    because nothing is inside a stretched viewBox. Hover and keyboard focus are native. And
    every number is real DOM text, which means the numeral gate can see it, a screen reader can
    read it, and a reader can select and copy it.

    NOT COLOUR ALONE. Each group is labelled, each bar carries its own value, and the pair is
    always cleared-then-drawing in that order. A reader who cannot separate the two hues still
    gets the whole reading from the text.

    NO HIDDEN DATA TABLE, deliberately. The usual advice is to ship a visually hidden table
    beside a chart, and the first version did. Two things were wrong with it here. It is a
    SECOND COPY of the same numbers in the DOM, which is a second thing to keep true. And
    tests/text_contrast measures each run of text against its own ground, which for a `th`
    inside a clipped table is the page rather than nothing, so ten runs reported 1.8 against a
    floor of 4.5: a real reading of markup that should not have been there. Every group is
    focusable and its `aria-label` carries the month and both figures, which is the same
    reading and is navigable, from one source.
    """
    s = f.get("series") or []
    ch = f.get("change")
    if len(s) < 2 or not ch:
        return ""
    # Drawn from the TIMELINE, which holds every month on the record, and scaled by the
    # verified ones, which are the only months carrying a number.
    tl = f.get("timeline") or [dict(r, verified=True) for r in s]
    top = max(r["approved_mw"] for r in s)

    groups = []
    for r in tl:
        label = MONTHS[int(r["month"][5:]) - 1][:3]
        if not r["verified"]:
            # A MONTH WITH NO READING IS DRAWN AS A MONTH WITH NO READING. Not skipped, which
            # would set the months either side of it side by side and quietly claim the series
            # is continuous. Not filled from the month before, which is the carry-forward the
            # collector is forbidden to do and would be no better done in CSS. The slot keeps
            # its width and its name, and where the bars would be there is a rule and a mark.
            groups.append(
                f'<li class="qgrp qnone" tabindex="0" aria-label="{month_label(r["month"])}, '
                f'no monthly operational overview published, so nothing is plotted">'
                f'<span class="qbars"><span class="qmiss" aria-hidden="true">'
                f'<span class="qmissr"></span><span class="qmisst">none</span></span></span>'
                f'<time class="qm" datetime="{r["month"]}">{label}</time></li>')
            continue
        # THE LABEL GETS ITS OWN BAND, and the bar is drawn in what is left. It was a sibling
        # of the fill in a column both shared, with the fill at a percentage of the WHOLE
        # column, so a tall bar and its label were asked to fit in more space than the column
        # had and the value came down on top of the bar. tests/text_contrast did not catch it,
        # and could not: it composites a run of text against its ANCESTOR stack, the label's
        # ancestor is the transparent column, and the bar it visually lands on is a sibling the
        # check has no reason to look at. An earlier version of this nesting DID fail that gate
        # at 3.12 and I made the failure invisible rather than fixing it, which is a gate
        # passing by collision. The band below makes the overlap impossible to construct: the
        # label is laid out first, the plot is the remainder, and the fill is a percentage of
        # the PLOT rather than of the column.
        # ONE BOX, ONE BASELINE, ONE SCALE. Both bars are positioned inside the SAME box, the
        # group's .qbars, pinned to its bottom. That is not a style choice, it is the only way
        # the picture can be true: when each bar resolved its percentage against its own nested
        # box, the two columns of a pair ended up with different heights AND different bottoms,
        # so the chart drew 4,049 at 1.66 times the height its value earns and sat it on a
        # baseline 22.4px below the bar it is meant to be compared with. A bar chart with two
        # baselines is not a bar chart. Sharing the box makes both properties structural.
        #
        # THE LABEL RIDES ITS OWN BAR, at the bar's top edge, rather than sitting in a band at
        # the top of the column. The band was what put the short bars' labels 64px away from the
        # thing they label, floating with nothing under them.
        #
        # PLOT_MAX leaves the top of the box for the labels, so the tallest bar's label has
        # somewhere to go and no label can leave the figure.
        bars = "".join(
            f'<span class="qb {cls}" style="--h:{r[key] / top * PLOT_MAX:.2f}%">'
            f'<span class="qbv num">{n0(r[key])}</span>'
            f'<span class="qbf"></span></span>'
            for key, cls in (("approved_mw", "qa"), ("drawing_mw", "qd")))
        groups.append(
            f'<li class="qgrp" tabindex="0" aria-label="{month_label(r["month"])}, '
            f'cleared to switch on {n0(r["approved_mw"])} megawatts, '
            f'actually drawing {n0(r["drawing_mw"])} megawatts">'
            f'<span class="qbars">{bars}</span>'
            f'<time class="qm" datetime="{r["month"]}">{label}</time></li>')

    return f"""<figure class="qchart">
  <ol class="qgroups" data-prose="data">{''.join(groups)}</ol>
  <p class="qlegend" data-prose="data">
    <span class="qkey qa"></span>Cleared to switch on
    <span class="qkey qd"></span>Actually drawing
    <span class="qunit">megawatts</span></p>
</figure>"""


# --------------------------------------------------------------------------- the panel
def panel(data: dict) -> str:
    """The whole thing, in as few words as it can be said in.

    THE WORDS ARE THE BUDGET. The page this joins ran 741 words against one chart, which is an
    essay with a picture in it. Everything here that a bar already says has been cut.
    """
    f = figures(data)
    L, R = f.get("latest"), f.get("requested")
    if not (L and R):
        return ""
    ch = f.get("change")
    trend = ""
    if ch:
        trend = f"""<h3>It has not moved all year</h3>
{flatline(f)}
<p class="qnote">Every figure ERCOT has published this year. The queue grew to
{gw(R['mw'])} GW over the same months.</p>"""

    return f"""<section class="queuegap" data-reveal>
  <h2>The Queue Gap</h2>
  <p class="qlede">Large load has asked ERCOT for <strong class="num">{gw(R['mw'])} GW</strong>.
  <strong class="num">{gw(L['drawing_mw'])} GW</strong> of it is drawing power.</p>

  {gap_bar(f)}

  <p class="qnote"><span class="num">{pct(R['dc_share_pct'])}%</span> of the queue is data
  centers. Queue read <a href="{R['source_url']}">{ordinal_date(R['as_of'])}</a>. The rest read
  <a href="{L['source_url']}">{month_label(L['month'])}</a>. Both from ERCOT.</p>

  <h3>For scale</h3>
  {anchor_bar(f)}
  <p class="qnote">The queue is <span class="num">{times(L['requested_vs_peak_times'])}</span>
  times the most power Texas has ever used at once.</p>

  <h3>Where it stands</h3>
  {stages(f)}
  {trend}
</section>"""


# --------------------------------------------------------------------------- the gate
def authorised(f: dict) -> set[str]:
    """Every numeral string this panel may show, built from the same calls that render it."""
    acc = numeral_lint.Authorised()
    add = acc.add
    R, L, ch = f.get("requested"), f.get("latest"), f.get("change")
    if R:
        add(gw(R["mw"]), pct(R["dc_share_pct"]), ordinal_date(R["as_of"]))
    if L:
        add(gw(L["approved_mw"]), gw(L["drawing_mw"]), month_label(L["month"]),
            pct(L.get("drawing_share_of_approved_pct")),
            pct(L.get("approved_share_of_requested_pct")),
            pct(L.get("drawing_share_of_requested_pct")),
            times(L.get("requested_vs_peak_times")), "100")
        if L.get("peak_record_mw"):
            add(gw(L["peak_record_mw"]))
    if ch:
        add(n0(ch["months"]), month_label(ch["from_month"]))
    for r in f.get("series") or []:
        # n0 as well as gw: the chart prints exact megawatts now, which is the whole point of
        # it being data rather than a shape, so those strings have to be authorised too.
        add(month_label(r["month"]), MONTHS[int(r["month"][5:]) - 1][:3],
            gw(r["approved_mw"]), gw(r["drawing_mw"]),
            n0(r["approved_mw"]), n0(r["drawing_mw"]))
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

    data = load()
    f = figures(data)
    check("the ledger has a verified reading", bool(f.get("latest")))
    check("the requested figure is configured", bool(f.get("requested")))

    html = panel(data)
    check("the panel renders", bool(html.strip()))
    check("the gap bar is present", 'class="qgap"' in html)
    check("the funnel is present", 'class="qstages"' in html)

    stray = lint(html, f)
    check("every numeral traces to a computation", not stray, ", ".join(stray[:8]))

    # THE GATE MUST BE ABLE TO GO RED. A checker that cannot fail proves nothing.
    planted = html.replace("</section>", "<p>An untraceable 8675309 figure.</p></section>")
    check("and an invented numeral is caught", bool(lint(planted, f)))

    # THE FLOOR MUST NEVER OVERSTATE THE BAR. A minimum width exists so a very small value
    # still renders as something rather than as a broken widget, and the moment it makes the
    # bar look bigger than the measurement it has become a lie told in pixels. On today's
    # figures the floor does not engage at all; this asserts the property, not today's luck.
    if f.get("latest") and f.get("requested"):
        share = f["latest"]["drawing_mw"] / f["requested"]["mw"] * 100.0
        rendered = max(share, 0.35)
        check("the drawing bar never renders wider than the measurement",
              rendered <= share or share < 0.35,
              f"share {share:.3f}% rendered {rendered:.3f}%")
        check("and the floor is not engaged at today's figures", share >= 0.35,
              f"share {share:.3f}%")

    # A MONTH WITH NO READING KEEPS ITS SLOT. The chart drew off the verified-only series and
    # so closed the gap silently, setting April next to June as though the record ran straight
    # through. Both fixtures below are hermetic: an unverified month must produce a slot, and a
    # record with no gap must produce none, so the check fails in both directions.
    holed = {"records": [
        {"month": "2026-01", "verified": True, "approved_to_energize_mw": 8787,
         "observed_operational_mw": 4049},
        {"month": "2026-02", "verified": False, "note": "nothing published"},
        {"month": "2026-03", "verified": True, "approved_to_energize_mw": 9042,
         "observed_operational_mw": 4008}],
        "requested": data.get("requested")}
    hf = figures(holed)
    hh = flatline(hf)
    check("a month with no reading is drawn as a gap, not skipped",
          hh.count('class="qgrp') == 3 and "qmiss" in hh)
    check("...and that gap publishes no number of its own", not lint(hh, hf))
    solid = {"records": [r for r in holed["records"] if r.get("verified")],
             "requested": data.get("requested")}
    check("...and a record with no hole draws no gap",
          "qmiss" not in flatline(figures(solid)))

    # ONE SLOT PER MONTH, AND THE LEDGER IS APPEND ONLY. A month with nothing published gets an
    # honest unverified record every time the collector looks, so August carried three lines by
    # 2026-09-03 and the chart drew three Augusts. The published page had two, a fresh build had
    # three, and the number went up every morning: site_fresh_check red on main with rebuilding
    # as the loudest wrong answer, since it clears the gate for a day and puts a fourth August
    # on the live page. Both directions, because the second is what makes the first safe.
    repeated = {"records": [
        {"month": "2026-01", "verified": True, "approved_to_energize_mw": 8787,
         "observed_operational_mw": 4049},
        {"month": "2026-02", "verified": False, "note": "nothing published",
         "read_at": "2026-09-01T00:00:00Z"},
        {"month": "2026-02", "verified": False, "note": "nothing published",
         "read_at": "2026-09-02T00:00:00Z"},
        {"month": "2026-02", "verified": False, "note": "nothing published",
         "read_at": "2026-09-03T00:00:00Z"},
        {"month": "2026-03", "verified": True, "approved_to_energize_mw": 9042,
         "observed_operational_mw": 4008}],
        "requested": data.get("requested")}
    rh = flatline(figures(repeated))
    check("a month looked at three times is drawn once, not three times",
          rh.count('class="qgrp') == 3 and rh.count('datetime="2026-02"') == 1,
          f"{rh.count('class=' + chr(34) + 'qgrp')} slot(s), "
          f"{rh.count('datetime=' + chr(34) + '2026-02' + chr(34))} February")
    # AND A LATE READING WINS OVER AN EARLIER MISS WHATEVER ORDER THE LINES ARE IN. A month can
    # go unpublished for days and then publish, so last-wins alone would throw the reading away.
    published_late = {"records": [
        {"month": "2026-01", "verified": True, "approved_to_energize_mw": 8787,
         "observed_operational_mw": 4049},
        {"month": "2026-02", "verified": True, "approved_to_energize_mw": 9043,
         "observed_operational_mw": 4037, "read_at": "2026-09-01T00:00:00Z"},
        {"month": "2026-02", "verified": False, "note": "nothing published",
         "read_at": "2026-09-02T00:00:00Z"}],
        "requested": data.get("requested")}
    ph = flatline(figures(published_late))
    check("...and a verified reading wins over a later miss on the same month",
          "9,043" in ph and ph.count('datetime="2026-02"') == 1, ph[:200])

    # THE VALUE CANNOT LAND ON THE BAR. Not "does not today" but cannot: the label is laid out
    # above a plot wrapper and the fill's percentage resolves against that wrapper, so full
    # scale reaches the top of the plot and stops. This asserts the STRUCTURE, because the
    # thing that went wrong was a structure whose overlap tests/text_contrast could not see
    # (it composites a run of text against its ancestors, and the bar was a sibling).
    # THE TWO BARS OF A PAIR MUST BE ON ONE SCALE. This is the check that was missing when the
    # chart shipped drawing 4,049 at 1.66 times the height its value earns, because each bar
    # resolved its height against its own box. Both --h now come from the same `top`, so the
    # ratio of the drawn heights has to equal the ratio of the measured values, and this asserts
    # exactly that rather than asserting the markup that happens to produce it.
    hs = [float(x) for x in re.findall(r'--h:([\d.]+)%', html)]
    check("every bar carries a drawn height", len(hs) == 2 * len(f["series"]))
    scale_ok, worst = True, ""
    for r, (ha, hd) in zip(f["series"], zip(hs[0::2], hs[1::2])):
        want = r["drawing_mw"] / r["approved_mw"]
        got = hd / ha if ha else 0.0
        if abs(want - got) > 0.005:
            scale_ok, worst = False, f'{r["month"]} drawn {got:.3f} vs measured {want:.3f}'
    check("...and the two bars of a month are drawn on one scale", scale_ok, worst)
    check("...and no bar is drawn past the room left for the labels",
          all(h <= PLOT_MAX + 1e-9 for h in hs), f"max {max(hs) if hs else 0:.2f}%")

    check("no dial, no severity ramp", "dial" not in html and "severity" not in html)
    print("\nqueue_panel self-test " + ("clean" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
