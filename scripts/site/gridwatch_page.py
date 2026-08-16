#!/usr/bin/env python3
"""gridwatch_page.py — the Texas Grid Watch, rendered from the record and nothing else.

THE SPLIT THAT MATTERS. The collector in `scripts/gridwatch/` writes the record. This file
reads it. They are owned by different actors on purpose, so the unattended thing that fetches
from ERCOT has no way to change what the page says except by changing the data, and the data
is append only. A collector that could also write the page could tell any story it liked.

WHAT THIS PAGE IS FOR

Every number here is about one question: how is Texas absorbing large constant load. The
answer is not the peak. Peak megawatts is a summer weather story that Texas has been telling
since air conditioning, and a data center barely moves it. The answer is the SHAPE.

    A data center is flat. It draws at four in the morning what it draws at five in the
    afternoon. Air conditioning is a spike against a low night.

So a grid taking on large constant load has its TROUGH rise faster than its peak, and the load
factor, the mean over the peak, climbs. That is a fingerprint no announcement can spin, no
single day can show, and no other Texas page is keeping. It is the reason this series starts
now rather than when somebody gets around to it.

WHAT IT REFUSES TO SAY

No reliability verdict. Not a shortfall, not an all clear. The gauge is a BAR and never a dial,
at one hue and one intensity at every value, because a dial implies a red zone and a red zone
is a verdict this page does not get to publish. The length is the whole message.

WHAT IT SAYS INSTEAD

The size of what is not public. Per site large load metering is confidential in Texas, so
nobody outside ERCOT can say what any one data center drew. That gap is published as a fact
rather than filled with an estimate.

DEGRADING HONESTLY. A series that starts today has one record in it, and a page that needs
thirty to say anything is a page that lies for a month. Everything here is written to be true
at n=1 and to get richer, never to pretend. The trend blocks appear when there is a trend.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numeral_lint                                                # noqa: E402

READINGS = REPO_ROOT / "ledger" / "gridwatch" / "readings.jsonl"

# Rounding is a computation with a stated rule. Gigawatts to one decimal is a tenth of a
# gigawatt on a system whose peak is in the eighties, which is finer than any decision a reader
# makes from this page and coarser than the noise in a five minute telemetry feed.
GW_DP = 1
PCT_DP = 1


def load(path: Path = READINGS) -> list[dict]:
    """Every day the record holds, one per date, latest line wins.

    Append only is not write once: an incomplete day may be superseded by a complete one, and
    both lines stay on disk. The page shows what currently stands.
    """
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
# THE RENDERER AND THE LINT DRAW FROM THESE SAME FUNCTIONS. That is what makes the numeral
# gate meaningful: there is no path by which a displayed figure and an authorised figure can
# disagree, because they are the same call.
def gw(mw) -> str | None:
    return None if mw is None else f"{round(float(mw) / 1000.0, GW_DP):,.1f}"


def pct(x) -> str | None:
    return None if x is None else f"{round(float(x), PCT_DP):,.1f}"


def share(x) -> str | None:
    """Shares carry two decimals, and the reason is Hydro.

    ERCOT's hydro fleet ran 745 MWh against a system total near 1.7 million on the first day
    collected. At one decimal that prints as 0.0, which reads as "none" and is wrong: the
    plants ran.

    THE RULE: two decimals, extended until a quantity that is not zero is not published as
    zero. Stated that way it is a computation with a reason rather than a taste, and it holds
    for a fuel a hundred times smaller than hydro without anybody revisiting it.
    """
    if x is None:
        return None
    v = float(x)
    dp = 2
    while dp < 6 and v != 0 and round(v, dp) == 0:
        dp += 1
    return f"{round(v, dp):,.{dp}f}"


def plural(n, one: str, many: str) -> str:
    """The word after the number, never the number. Keeps 'day(s)' off a published page."""
    try:
        return one if abs(float(str(n).replace(",", ""))) == 1 else many
    except (TypeError, ValueError):
        return many


def _residual_ceiling(load: list, fc: list) -> float | None:
    """The residual strip's symmetric ceiling, or None when there is no strip to draw.

    Factored out of the chart because the GUTTER has to know how wide "-2,500" is before the
    strip is drawn, and the alternative is this arithmetic written twice, which is one place
    for it to drift and produce a gutter sized for a label the chart does not print.
    """
    if not fc or len(fc) != len(load):
        return None
    errs = [fc[i] - load[i] for i in range(len(load))
            if isinstance(fc[i], (int, float)) and isinstance(load[i], (int, float))]
    if not errs:
        return None
    span = max(abs(v) for v in errs) or 1.0
    # A round ceiling so the label is a number a reader can hold, and never zero.
    return max(500.0, (int(span / 500) + 1) * 500.0)


def n0(x) -> str | None:
    return None if x is None else f"{round(float(x)):,}"


def ordinal_date(iso: str) -> str:
    """House style: month first, with the ordinal. August 10th, never 2026-08-10."""
    import datetime as _dt
    d = _dt.date.fromisoformat(iso)
    suf = "th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th")
    return f"{d:%B} {d.day}{suf}, {d.year}"


def hour(he) -> str | None:
    """Hour ending 17 is the hour that ends at 5 pm, so it is the 4 to 5 pm hour."""
    if he is None:
        return None
    end = int(he) % 24
    start = (end - 1) % 24

    def clock(h):
        ap = "am" if h < 12 else "pm"
        return f"{(h % 12) or 12}{ap}"
    return f"{clock(start)} to {clock(end)}"


# --------------------------------------------------------------------------- computation
def figures(records: list[dict]) -> dict:
    """Every number this page publishes, computed here, from the record.

    Nothing downstream computes. The renderer formats what this returns and the lint authorises
    what this returns, so a figure that is not in here cannot reach a reader.
    """
    live = [r for r in records if r.get("verified") and r.get("peak_load_mw") is not None]
    f: dict = {
        "days_held": len(records),
        "days_verified": len(live),
        "days_unverified": len(records) - len(live),
        "latest": None,
        "series": [],
        "trend": None,
        "accuracy": None,
    }
    if not live:
        return f

    last = live[-1]
    f["latest"] = {
        "date": last["date"],
        "peak_mw": last["peak_load_mw"],
        "peak_hour_ending": last.get("peak_hour_ending"),
        "min_mw": last["min_load_mw"],
        "min_hour_ending": last.get("min_hour_ending"),
        "mean_mw": last["mean_load_mw"],
        "energy_mwh": last.get("energy_mwh"),
        "load_factor": last.get("load_factor"),
        "capacity_at_peak_mw": last.get("capacity_at_peak_mw"),
        "reserve_at_peak_mw": last.get("reserve_at_peak_mw"),
        "forecast_peak_mw": last.get("forecast_peak_mw"),
        "peak_forecast_error_mw": last.get("peak_forecast_error_mw"),
        "reconciliation_pct": last.get("generation_load_gap_pct"),
        "load_mw": last.get("load_mw") or [],
        "day_ahead_forecast_mw": last.get("day_ahead_forecast_mw") or [],
        "hour_ending": last.get("hour_ending") or [],
        "fuel_energy_mwh": last.get("fuel_energy_mwh") or {},
    }

    # The reserve bar. Load as a share of the capacity ERCOT had committed at that hour. It is
    # a length and nothing else: no threshold, no band, no colour that changes.
    cap = last.get("capacity_at_peak_mw")
    if cap:
        f["latest"]["load_share_of_capacity_pct"] = round(
            last["peak_load_mw"] / cap * 100.0, PCT_DP)

    f["series"] = [{"date": r["date"], "peak_mw": r["peak_load_mw"],
                    "min_mw": r["min_load_mw"], "load_factor": r.get("load_factor")}
                   for r in live]

    # THE TREND BLOCK ONLY EXISTS WHEN THERE IS A TREND. Two points is a line through noise,
    # not a finding. Fourteen days is the shortest window in which a weekday and weekend
    # pattern has repeated twice, which is the least that can be called a shape.
    if len(live) >= 14:
        half = len(live) // 2
        early, late = live[:half], live[len(live) - half:]

        def mean(rows, key):
            vals = [r[key] for r in rows if isinstance(r.get(key), (int, float))]
            return sum(vals) / len(vals) if vals else None
        lf0, lf1 = mean(early, "load_factor"), mean(late, "load_factor")
        tr0, tr1 = mean(early, "min_load_mw"), mean(late, "min_load_mw")
        pk0, pk1 = mean(early, "peak_load_mw"), mean(late, "peak_load_mw")
        f["trend"] = {
            "window_days": len(live),
            "half_days": half,
            "load_factor_early": round(lf0, 4) if lf0 else None,
            "load_factor_late": round(lf1, 4) if lf1 else None,
            "trough_change_mw": round(tr1 - tr0, 1) if tr0 and tr1 else None,
            "peak_change_mw": round(pk1 - pk0, 1) if pk0 and pk1 else None,
        }

    # ERCOT's model against ERCOT's telemetry, across every day held. Ours to compute, never
    # ours to grade: the number is what it is and it is published whichever way it falls.
    errs = [abs(r["peak_forecast_error_mw"]) for r in live
            if isinstance(r.get("peak_forecast_error_mw"), (int, float))]
    if errs:
        pk = [r["peak_load_mw"] for r in live
              if isinstance(r.get("peak_forecast_error_mw"), (int, float))]
        f["accuracy"] = {
            "days": len(errs),
            "mean_abs_peak_error_mw": round(sum(errs) / len(errs), 1),
            "mean_abs_peak_error_pct": round(
                sum(e / p for e, p in zip(errs, pk)) / len(errs) * 100.0, 2),
            "worst_mw": round(max(errs), 1),
        }
    return f


# --------------------------------------------------------------------------- the chart
def load_shape_svg(latest: dict) -> str:
    """The day, drawn, with the two things a reader came for marked on it.

    THE Y AXIS STARTS AT ZERO AND STAYS THERE. A truncated axis makes an ordinary Tuesday
    look like a crisis, and the true finding here is the opposite one: ERCOT's load never
    falls much below three quarters of its peak. Exaggerating that with a drawing would be
    arguing against our own measurement.

    WHAT WAS WRONG WITH IT ANYWAY, measured rather than felt. On a real day the load runs
    60,462 to 88,143 MW against a 100,000 ceiling, so **the entire story occupied 27.7% of
    the canvas and 60.5% of it was a featureless block below the trough.** Worse, the day
    ahead forecast missed the peak by 432 MW, which is half a percent, which at true scale
    is about one pixel. The dashed forecast line was drawn exactly on top of the measured
    one and carried no information at all while looking like it did. Honest and unreadable
    is still unreadable.

    Three changes, none of which touch the scale.

    THE PEAK AND THE TROUGH ARE MARKED AND LABELLED where they happen. A reader gets the two
    magnitudes and the two hours without decoding an axis, and they sit in the empty upper
    field rather than in a table somewhere else on the page.

    THE MISS GETS ITS OWN PANEL, at its own scale, said so in words. A residual strip under
    the main chart is the standard way to show a small difference without distorting the
    thing it is a difference from. The main chart keeps the truthful shape; the strip
    answers "by how much, and when". Its scale is stated on it, so nobody reads the two as
    the same axis.

    THE FILL FADES DOWNWARD. That is not a severity ramp and carries no value meaning. The
    grid watch's no-ramp rule is about the capacity gauge, where colour would imply a red
    zone this page does not get to publish. Here the fade separates a filled area from the
    ground under it, and the line on top carries the reading.
    """
    load = [v for v in latest["load_mw"]]
    if not any(isinstance(v, (int, float)) for v in load):
        return ""
    fc = latest["day_ahead_forecast_mw"] or []
    # THE LEFT GUTTER HOLDS THE WIDEST LABEL AT THE LARGEST PHONE TYPE SIZE, and that is the
    # whole reason it is 108 rather than the 52 it used to be.
    #
    # WHAT 52 SHIPPED. The axis labels are right anchored eight units inside this gutter, and
    # the type steps up to 27 user units on a phone so the glyphs clear ten CSS pixels once the
    # drawing is scaled down. Six characters of mono at 27 units is about 97, which did not fit
    # in 44, so the residual axis was cut on every phone. It did not read as a cut. It read as
    # "500", because the part that fell off the left edge was "2,". A published figure showing a
    # different number from the one computed is the one failure this project cannot have, so
    # this is a correctness fix wearing a layout fix's clothes.
    #
    # The geometry is Python and the type size is a CSS breakpoint, so neither can see the
    # other. The gutter is therefore sized for the worst case the stylesheet can produce, and
    # `tests/responsive.mjs` measures the rendered glyph boxes against the drawing rather than
    # trusting this arithmetic.
    # `pad_t` holds the unit caption ABOVE the top gridline label rather than on top of it.
    # At 16 the caption's baseline sat five units above the plot and the topmost axis number
    # sat four below it, which is fine at eleven point type and prints "GW" through "100" at
    # twenty seven.
    w, pad_t = 720.0, 44.0
    # The largest `.loadshape .ax` step in theme.py, in user units. If that step changes, this
    # changes with it, and the test catches the pair going out of step.
    ax_max_px = 27.0
    # A MONO ADVANCE, ROUNDED UP RATHER THAN AVERAGED. This was 0.62, which is about right for
    # the face this site serves and is not a bound: a fallback mono, or a face that has not
    # swapped in yet, sets wider. 0.66 covers the common Linux fallbacks with room, and the
    # cost of being generous is a few units of gutter nobody will notice.
    est = lambda s: 0.66 * ax_max_px * len(s)
    # `gap` and `res_h` are sized on the same principle as the gutter. The residual strip
    # stacks three captions down the gutter, one at each end and the unit in the middle, so
    # the strip's HALF HEIGHT is the space between them. At 62 that was 31 units for a caption
    # 27 units tall, which stopped being enough the moment the type stepped up for phones.
    main_h, gap, res_h, pad_b = 210.0, 48.0, 86.0, 24.0
    h = pad_t + main_h + gap + res_h + pad_b
    vals = [v for v in load if isinstance(v, (int, float))]
    top = max(vals + [v for v in fc if isinstance(v, (int, float))])
    ceil = (int(top / 20000) + 1) * 20000.0
    n = len(load)

    # THE GUTTER IS SIZED FROM THE LABELS IT HAS TO HOLD.
    #
    # It was 108, a constant, and 108 was right for the labels that existed when it was
    # measured. The residual strip's ceiling moves with the data, and the day it reached 2,500
    # the negative label became six characters, which needs 100.4 units of the 100 the gutter
    # leaves. It rendered correctly here and was CUT ON THE CI RUNNER, because the margin was
    # under half a unit and the two machines do not have the same fonts. The runner was right.
    # A reader whose web font has not swapped in yet is looking at the runner's render.
    #
    # This is the same fault as the one in GATE_LESSONS 24, one level up. That one was type
    # size in CSS and geometry in Python with nothing able to see the pair. This is the pair
    # being visible and the gutter still being a number typed once, against labels that change
    # daily. So it is computed from every string that gets drawn into it.
    rceil = _residual_ceiling(load, fc)
    gutter = [str(int(ceil * k / 4 / 1000)) for k in range(5)] + ["GW", "MW"]
    if rceil is not None:
        gutter += [n0(rceil), "-" + n0(rceil)]
    # 8 is the gap the labels are anchored back from the plot; 6 more so a face wider than the
    # estimate still lands inside the drawing rather than one unit outside it.
    pad_l = round(max(est(s) for s in gutter) + 8 + 6, 1)

    plot_w = w - pad_l - 12

    def x(i):
        return round(pad_l + (i / max(n - 1, 1)) * plot_w, 2)

    def y(v):
        return round(pad_t + main_h - (v / ceil) * main_h, 2)

    pts = [(x(i), y(v)) for i, v in enumerate(load) if isinstance(v, (int, float))]
    area = (f'M{pts[0][0]},{y(0)} ' + " ".join(f"L{a},{b}" for a, b in pts) +
            f' L{pts[-1][0]},{y(0)} Z')
    line = "M" + " L".join(f"{a},{b}" for a, b in pts)
    fpts = [(x(i), y(v)) for i, v in enumerate(fc) if isinstance(v, (int, float))]
    fline = ("M" + " L".join(f"{a},{b}" for a, b in fpts)) if fpts else ""

    grid = "".join(
        f'<line class="g" x1="{pad_l}" x2="{w - 12}" y1="{y(v)}" y2="{y(v)}"/>'
        f'<text class="ax" x="{pad_l - 8}" y="{y(v) + 4}" text-anchor="end">'
        f'{int(v / 1000)}</text>'
        for v in [ceil * k / 4 for k in range(5)])
    # ANCHORED TO THE ENDS, NOT CENTRED ON THEM. A centered label at x=0 puts half its width
    # outside the drawing, and at the right edge the same thing clipped "midnight" to "midni".
    ticks = "".join(
        f'<text class="ax" x="{x(i)}" y="{pad_t + main_h + 15}" text-anchor="{anchor}">{lab}</text>'
        for i, lab, anchor in [(0, "midnight", "start"), (n // 2, "noon", "middle"),
                               (n - 1, "midnight", "end")]
        if n > 2)

    # THE PEAK AND THE TROUGH, found in the same series the line is drawn from rather than
    # read off a field somewhere else, so the dot cannot land away from the bend it names.
    marks = ""
    idx = [i for i, v in enumerate(load) if isinstance(v, (int, float))]
    if idx:
        hi = max(idx, key=lambda i: load[i])
        lo = min(idx, key=lambda i: load[i])
        for i, tag, dy, anchor in ((hi, "peak", -14.0, "middle"), (lo, "trough", 22.0, "middle")):
            px, py = x(i), y(load[i])
            # CLAMPED BY THE LABEL'S OWN WIDTH, not by a fixed inset. These callouts are long
            # sentences, about 340 units at the phone type size, and a middle anchored label
            # that wide needs half of itself either side of the point it names. The old clamp
            # allowed the center anywhere from 86 to 674, so on a phone the trough callout ran
            # off the left edge and sat across the axis numbers.
            label = f"{gw(load[i])} GW at {hour(i + 1)}"
            # The left bound is the GUTTER, not the canvas edge. Clamping to zero kept the
            # callout on the drawing and laid it straight across the axis numbers, which is
            # legible in neither direction.
            half = est(label) / 2.0
            lo_x, hi_x = pad_l + half, w - half
            lx = (pad_l + (w - pad_l) / 2.0 if lo_x > hi_x else min(max(px, lo_x), hi_x))
            marks += (f'<circle class="mk" cx="{px}" cy="{py}" r="3.5"/>'
                      f'<text class="ax mklab" x="{lx}" y="{round(py + dy, 2)}" '
                      f'text-anchor="{anchor}">{label}</text>')

    # THE RESIDUAL STRIP. Forecast minus measured, hour by hour, on a scale of its own.
    res = ""
    if rceil is not None:
        errs = [(i, fc[i] - load[i]) for i in range(n)
                if isinstance(fc[i], (int, float)) and isinstance(load[i], (int, float))]
        if errs:
            mid = pad_t + main_h + gap + res_h / 2

            def ry(v):
                return round(mid - (v / rceil) * (res_h / 2), 2)

            bars = "".join(
                f'<line class="res" x1="{x(i)}" x2="{x(i)}" y1="{mid}" y2="{ry(v)}"/>'
                for i, v in errs)
            res = (f'<line class="zero" x1="{pad_l}" x2="{w - 12}" y1="{mid}" y2="{mid}"/>'
                   f'{bars}'
                   f'<text class="ax" x="{pad_l - 8}" y="{ry(rceil) + 4}" '
                   f'text-anchor="end">{n0(rceil)}</text>'
                   f'<text class="ax" x="{pad_l - 8}" y="{ry(-rceil) + 4}" '
                   f'text-anchor="end">-{n0(rceil)}</text>'
                   f'<text class="ax unit" x="{pad_l - 8}" y="{round(mid + 4, 2)}" '
                   f'text-anchor="end">MW</text>')

    fseg = (f'<path class="fc" d="{fline}"/>' if fline else "")
    return f"""<figure class="shape">
<svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" class="loadshape"
     aria-label="Measured ERCOT demand hour by hour against ERCOT's day ahead forecast, with
     the forecast error shown separately below.">
  <defs><linearGradient id="lsfill" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="var(--accent-deep)" stop-opacity=".42"/>
    <stop offset="1" stop-color="var(--accent-deep)" stop-opacity=".06"/>
  </linearGradient></defs>
  {grid}
  <path class="area" fill="url(#lsfill)" d="{area}"/>
  {fseg}
  <path class="line" d="{line}"/>
  {marks}
  {ticks}
  <text class="ax unit" x="4" y="{pad_t - 8}" text-anchor="start">GW</text>
  {res}
</svg>
<figcaption>Measured demand, peak and trough marked. The dashed line is ERCOT's forecast,
close enough to overlap. The scale starts at zero, so the flatness is real. The strip below is
forecast minus measured, scaled separately because a miss is one pixel up here.
</figcaption></figure>"""


def reserve_bar(latest: dict) -> str:
    """A BAR AND NEVER A DIAL. One hue, one intensity, at every value.

    A dial has a red zone. A red zone is a verdict, and a verdict is the one thing this page has
    promised never to publish, because a unit trip can produce an emergency on a day the numbers
    looked comfortable. So the fill is the same color at ninety percent as at forty, and the
    length carries the entire message.
    """
    share = latest.get("load_share_of_capacity_pct")
    if share is None:
        return ""
    return f"""<div class="bar" role="img"
     aria-label="Demand at the daily peak reached {pct(share)} percent of the capacity ERCOT
     had committed for that hour.">
  <div class="fill" style="width:{min(float(share), 100.0):.1f}%"></div>
</div>
<p class="barnote">At the peak hour, demand reached <strong class="num">{pct(share)}%</strong>
of the generation capacity ERCOT had committed for that hour. This bar has one color at every
value on purpose. It is a measurement rather than a judgement about whether the grid was
comfortable. No number on this page can tell you that.</p>"""


# --------------------------------------------------------------------------- the page body
def body(records: list[dict], today: str) -> str:
    f = figures(records)
    if not f["latest"]:
        return """
<h1>Texas Grid Watch</h1>
<div class="prose">
  <p>A daily numeric record of how the ERCOT grid is absorbing large constant load. The
  collector runs on its own schedule and appends one settled day at a time.</p>
  <div class="gap"><strong>The record is empty.</strong> No day has been collected yet.
  Nothing is estimated to fill the space.</div>
</div>
"""
    L = f["latest"]
    d = ordinal_date(L["date"])
    lf = L.get("load_factor")
    lfpct = pct(lf * 100.0) if lf else None
    fuel = L.get("fuel_energy_mwh") or {}
    served = sum(v for v in fuel.values() if isinstance(v, (int, float)) and v > 0)
    fuel_rows = "".join(
        f'<tr><td>{k}</td><td class="n num">{n0(v)}</td>'
        f'<td class="n num">{share(v / served * 100.0) if served and v > 0 else "charging"}'
        f'</td></tr>'
        for k, v in sorted(fuel.items(), key=lambda kv: -kv[1]) if isinstance(v, (int, float)))
    # THE ARITHMETIC A READER WOULD DO, SHOWN. Gross generation and the net after storage are
    # different numbers, and the reconciliation below compares the net one. Printing only the
    # gross would leave a reader subtracting our figures and landing somewhere we did not.
    net = sum(v for v in fuel.values() if isinstance(v, (int, float)))
    fuel_rows += (f'<tr><td><strong>Gross generation</strong></td>'
                  f'<td class="n num"><strong>{n0(served)}</strong></td>'
                  f'<td class="n num">{share(100.0)}</td></tr>'
                  f'<tr><td>Net after storage</td>'
                  f'<td class="n num">{n0(net)}</td><td></td></tr>'
                  f'<tr><td>Measured load</td>'
                  f'<td class="n num">{n0(L["energy_mwh"])}</td><td></td></tr>' if served
                  else "")

    err = L.get("peak_forecast_error_mw")
    err_dir = ("ERCOT forecast high" if isinstance(err, (int, float)) and err > 0 else
               "ERCOT forecast low" if isinstance(err, (int, float)) and err < 0 else
               "forecast minus measured")

    acc = f["accuracy"]
    acc_block = ""
    if acc:
        acc_block = f"""
<h2>Checking the forecast against what happened</h2>
<div class="prose">
  <p>ERCOT publishes a forecast then what happened. The gap is arithmetic rather than
  opinion. Across <strong class="num">{n0(acc['days'])}</strong>
  {plural(acc['days'], 'day', 'days')} its day ahead peak forecast missed by
  <strong class="num">{n0(acc['mean_abs_peak_error_mw'])} MW</strong> on average, or
  <strong class="num">{pct(acc['mean_abs_peak_error_pct'])}%</strong> of peak. Worst so far
  <strong class="num">{n0(acc['worst_mw'])} MW</strong>.</p>
  <p>Published whichever way it falls. A page that checks its inputs in public beats one that
  asserts they are good.</p>
</div>"""

    trend_block = ""
    t = f["trend"]
    if t and t.get("trough_change_mw") is not None:
        trend_block = f"""
<h2>The fingerprint</h2>
<div class="prose">
  <p>Over the <strong class="num">{n0(t['window_days'])}</strong> days held, the overnight
  trough moved by <strong class="num">{n0(t['trough_change_mw'])} MW</strong> and the daily
  peak moved by <strong class="num">{n0(t['peak_change_mw'])} MW</strong>, comparing the most
  recent <strong class="num">{n0(t['half_days'])}</strong> days against the first
  <strong class="num">{n0(t['half_days'])}</strong>.</p>
  <p>A trough rising faster than a peak is what large constant load looks like from outside.
  Weather moves both together. A data center lifts the floor.</p>
</div>"""
    elif f["days_verified"] < 14:
        trend_block = f"""
<h2>The fingerprint</h2>
<div class="prose">
  <div class="gap"><strong>Not yet.</strong> Comparing the trough against the peak needs at
  least <strong class="num">14</strong> settled days, so that a weekday and weekend pattern has
  repeated twice. The record holds <strong class="num">{n0(f['days_verified'])}</strong>.
  Nothing is drawn from fewer, because a line through two points is noise with a slope.</div>
</div>"""

    recon = L.get("reconciliation_pct")
    recon_block = ""
    if recon is not None:
        recon_block = f"""
  <p>Separate feeds, and everything generated inside the grid is consumed inside it, so they
  must agree. They differ by <strong class="num">{pct(abs(recon))}%</strong>, about what ties
  and losses account for. Both print because this catches either reader breaking.</p>"""

    return f"""
<h1>Texas Grid Watch</h1>
<div class="prose">
  <p class="lede">A daily numeric record of how the ERCOT grid is absorbing large constant
  load. This page does not predict, grade or reassure. It publishes measurements, the
  arithmetic done on them and the size of what nobody outside ERCOT can see.</p>
</div>

<h2>{d}</h2>
{load_shape_svg(L)}

<table class="figures">
<thead><tr><th>Figure</th><th class="n">Value</th><th>What it is</th></tr></thead>
<tbody>
<tr><td>Peak demand</td><td class="n num">{gw(L['peak_mw'])} GW</td>
    <td>measured, {hour(L['peak_hour_ending'])}</td></tr>
<tr><td>Overnight trough</td><td class="n num">{gw(L['min_mw'])} GW</td>
    <td>measured, {hour(L['min_hour_ending'])}</td></tr>
<tr><td>Mean across the day</td><td class="n num">{gw(L['mean_mw'])} GW</td>
    <td>computed from the hourly series</td></tr>
<tr><td>Load factor</td><td class="n num">{lfpct}%</td>
    <td>computed, mean over peak</td></tr>
<tr><td>Energy served</td><td class="n num">{n0(L['energy_mwh'])} MWh</td>
    <td>computed from the hourly series</td></tr>
<tr><td>ERCOT day ahead peak forecast</td><td class="n num">{gw(L['forecast_peak_mw'])} GW</td>
    <td>modeled by ERCOT, published the day before</td></tr>
<tr><td>Forecast miss at the peak</td>
    <td class="n num">{n0(L['peak_forecast_error_mw'])} MW</td>
    <td>computed, {err_dir}</td></tr>
</tbody>
</table>

<h2>Demand against committed capacity</h2>
{reserve_bar(L)}

<h2>The load factor, and why it is the number to watch</h2>
<div class="prose">
  <p>A day's mean demand divided by its peak. On {d} it was
  <strong class="num">{lfpct}%</strong>.</p>
  <p>Peak is a weather story. Shape is the story. A data center draws about as much at four in
  the morning as at five in the afternoon, so constant load lifts the overnight floor faster
  than the afternoon ceiling. Weather lifts both.</p>
  <p>One day can't show that. A year can.</p>
</div>
{trend_block}
{acc_block}

<h2>What served the load</h2>
<table class="figures">
<thead><tr><th>Fuel</th><th class="n">MWh</th><th class="n">Share</th></tr></thead>
<tbody>{fuel_rows}</tbody>
</table>
<div class="prose">
  <p>Integrated from ERCOT's five minute telemetry. Storage is signed. It reads negative when
  batteries absorb more than they return. Shares count positive generation only.</p>{recon_block}
</div>

<h2>The size of what is not public</h2>
<div class="prose">
  <div class="gap">
    <p><strong>Nobody outside ERCOT can say what any single data center drew.</strong> Per site
    large load metering is confidential. What is public is the system total, which is what this
    page publishes.</p>
    <p>So this page can show the shape of Texas demand changing. It can't attribute that change
    to a named facility, and it does not try. Where an attribution is wanted and can't be
    computed, the gap is printed instead of an estimate.</p>
  </div>
  <p>The record holds <strong class="num">{n0(f['days_held'])}</strong>
  {plural(f['days_held'], 'day', 'days')}, of which
  <strong class="num">{n0(f['days_verified'])}</strong>
  {plural(f['days_verified'], 'is a complete settled day', 'are complete settled days')} and
  <strong class="num">{n0(f['days_unverified'])}</strong>
  {plural(f['days_unverified'], 'is', 'are')} marked unverified. An unverified
  day carries no numbers at all rather than yesterday's. A gap that says it is a gap is honest.
  A gap filled with the last known figure is a fabrication nothing downstream can detect.</p>
</div>

<h2>How this is collected</h2>
<div class="prose">
  <p>Once a day the settled previous day is read whole from ERCOT's dashboard feeds. Demand
  hour by hour, the day ahead forecast, committed capacity and generation by fuel. Raw responses
  are archived first.</p>
  <p>The full hourly series is stored, so every figure here can be recomputed from
  <a href="../gridwatch.json">the open data</a>.</p>
  <p>ERCOT keeps no archive. A missed day is gone for good, so the collector runs on its own
  schedule.</p>
</div>
"""


# --------------------------------------------------------------------------- numeral gate
def authorised(f: dict) -> set[str]:
    """Every numeral string this page is allowed to show, built from the same calls that render.

    A figure reaches a reader only by passing through here first. That is the whole mechanism:
    not a promise that nobody types a number, a check that fails the build if anybody does.
    """
    acc = numeral_lint.Authorised()
    add = acc.add

    add(n0(f["days_held"]), n0(f["days_verified"]), n0(f["days_unverified"]), "14")
    L = f.get("latest")
    if L:
        add(ordinal_date(L["date"]), gw(L["peak_mw"]), gw(L["min_mw"]), gw(L["mean_mw"]),
            gw(L["forecast_peak_mw"]), n0(L["energy_mwh"]), n0(L["peak_forecast_error_mw"]),
            hour(L["peak_hour_ending"]), hour(L["min_hour_ending"]),
            pct(L.get("load_share_of_capacity_pct")))
        if L.get("load_factor"):
            add(pct(L["load_factor"] * 100.0))
        if L.get("reconciliation_pct") is not None:
            add(pct(abs(L["reconciliation_pct"])))
        served = sum(v for v in (L.get("fuel_energy_mwh") or {}).values()
                     if isinstance(v, (int, float)) and v > 0)
        if served:
            add(n0(served), share(100.0),
                n0(sum(v for v in (L.get("fuel_energy_mwh") or {}).values()
                       if isinstance(v, (int, float)))))
        for v in (L.get("fuel_energy_mwh") or {}).values():
            if isinstance(v, (int, float)):
                add(n0(v))
                if served and v > 0:
                    add(share(v / served * 100.0))
    for blk, keys in ((f.get("trend"), ("window_days", "half_days", "trough_change_mw",
                                        "peak_change_mw")),
                      (f.get("accuracy"), ("days", "mean_abs_peak_error_mw", "worst_mw"))):
        if blk:
            add(*(n0(blk[k]) for k in keys if blk.get(k) is not None))
    if f.get("accuracy"):
        add(pct(f["accuracy"]["mean_abs_peak_error_pct"]))
    return acc.set


def lint(html_body: str, f: dict) -> list[str]:
    """Every numeral in this page's copy, traced to a computed value or named as a violation."""
    return numeral_lint.scan(html_body, authorised(f))


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def rec(date, peak, trough, *, verified=True, cap=100000.0, fcerr=500.0):
        n = 24
        load = [trough + (peak - trough) * (1 - abs(i - 16) / 16.0) for i in range(n)]
        load[16] = peak
        load[4] = trough
        return {"_spec": 1, "date": date, "verified": verified,
                "hour_ending": list(range(1, n + 1)),
                "load_mw": load, "day_ahead_forecast_mw": [v + fcerr for v in load],
                "capacity_mw": [cap] * n,
                "hours_measured": n, "hours_in_day": n,
                "peak_load_mw": peak, "peak_hour_ending": 17,
                "min_load_mw": trough, "min_hour_ending": 5,
                "mean_load_mw": round(sum(load) / n, 1), "energy_mwh": round(sum(load), 1),
                "load_factor": round((sum(load) / n) / peak, 4),
                "capacity_at_peak_mw": cap, "reserve_at_peak_mw": cap - peak,
                "forecast_peak_mw": peak + fcerr, "peak_forecast_error_mw": fcerr,
                "generation_load_gap_pct": 0.1,
                "fuel_energy_mwh": {"Natural Gas": 700000.0, "Wind": 380000.0,
                                    "Solar": 290000.0, "Power Storage": -15000.0}}

    one = [rec("2026-08-10", 83118.16, 58093.11)]
    f = figures(one)
    check("one day is enough to publish a day", f["latest"] is not None)
    check("...and not enough to publish a trend", f["trend"] is None)
    b = body(one, "2026-08-11")
    check("the page renders from a single record", "<h1>Texas Grid Watch</h1>" in b)
    check("...and says plainly that the trend is not available yet",
          "Not yet." in b and "14" in b)

    # THE NUMERAL GATE. This is the hard rule for this page, so it is tested hardest.
    viol = lint(b, f)
    check("every numeral on the page traces to a computed value", not viol, str(viol[:8]))
    tampered = b.replace("<h1>Texas Grid Watch</h1>",
                         "<h1>Texas Grid Watch</h1><p>about 8.9 gigawatts</p>")
    check("a numeral typed into the copy fails the gate", "8.9" in lint(tampered, f))
    check("...and the gate names the offending numeral, not just a count",
          lint(tampered, f) == ["8.9"], str(lint(tampered, f)))
    check("a numeral inside SVG geometry is not treated as reader copy",
          not lint('<svg><path d="M12.5,300 L44,9"/></svg>', f))

    # A BAR AND NEVER A DIAL.
    check("the gauge is a bar", 'class="bar"' in b and "dial" not in b.lower())
    check("the bar carries no severity class that a stylesheet could ramp",
          not re.search(r'class="fill [a-z]', b))
    verdicts = ("shortfall", "blackout", "all clear", "emergency", "at risk", "safe",
                "conservation appeal", "warning")
    hit = [w for w in verdicts if w in b.lower()]
    check("no reliability verdict in the reader copy", not hit, str(hit))

    empty = body([], "2026-08-11")
    check("an empty record says it is empty rather than rendering zeros",
          "The record is empty." in empty and "0.0 GW" not in empty)
    check("...and the empty page has no numerals to authorise",
          not lint(empty, figures([])), str(lint(empty, figures([]))))

    unver = [{"_spec": 1, "date": "2026-08-09", "verified": False, "note": "fetch failed"}]
    fu = figures(unver)
    check("an unverified day counts, and publishes no number",
          fu["days_held"] == 1 and fu["days_verified"] == 0 and fu["latest"] is None)

    many = [rec(f"2026-07-{i:02d}", 80000.0 + i * 10, 55000.0 + i * 60) for i in range(1, 29)]
    fm = figures(many)
    check("fourteen settled days or more earns a trend block", fm["trend"] is not None)
    check("...comparing halves, not endpoints", fm["trend"]["half_days"] == 14)
    check("a trough rising faster than the peak is visible in the trend",
          fm["trend"]["trough_change_mw"] > fm["trend"]["peak_change_mw"],
          f"{fm['trend']['trough_change_mw']} vs {fm['trend']['peak_change_mw']}")
    bm = body(many, "2026-08-11")
    check("the trend block renders", "The fingerprint" in bm and "Not yet." not in bm)
    check("the trend page also passes the numeral gate", not lint(bm, fm),
          str(lint(bm, fm)[:8]))

    check("the accuracy check is computed across every day held",
          fm["accuracy"]["days"] == 28 and fm["accuracy"]["mean_abs_peak_error_mw"] == 500.0)

    # ---- the house rules, on every shape the record can take ------------------
    # THE RICHER BRANCHES USED TO SHIP UNLINTED UNTIL DATA HAPPENED TO ARRIVE. This page is
    # written to be true at one record and to say more as the series grows, which is the right
    # design and it means whole paragraphs exist only at two days, or at fourteen. The sibling
    # water page proved the cost on 2026-08-12: its comparison paragraph rendered for the FIRST
    # time the day a second reading landed, carrying a colon and pushing the page over its comma
    # ceiling, and it reached the deploy gate because nothing had ever linted that branch. The
    # fixtures above already build every shape. Now the copy in each is read as copy.
    import house_style_check as _hs                                 # noqa: PLC0415
    for label, records in (("one settled day", one), ("an empty record", []),
                           ("an unverified day", unver), ("a full trend", many)):
        rendered = body(records, records[-1]["date"] if records else "2026-08-11")
        problems = _hs.caption_check.check(_hs.our_prose(rendered))
        rate = _hs.caption_check.rate_problem(_hs.our_sentences(rendered),
                                              _hs.caption_check.SITE_COMMA_CEILING)
        if rate:
            problems = problems + [rate]
        check(f"the copy at {label} keeps the house rules", not problems,
              "; ".join(problems)[:150])

    dup = [rec("2026-08-10", 1.0, 1.0, verified=False), rec("2026-08-10", 83118.16, 58093.11)]
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "r.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in dup) + "\n")
        got = load(p)
        check("a superseded day appears once, as the later record",
              len(got) == 1 and got[0]["verified"] is True)
        p.write_text('{"date":"2026-08-10"}\nnot json\n\n{"date":"2026-08-11"}\n')
        check("a corrupt line is skipped rather than taking the page down",
              [r["date"] for r in load(p)] == ["2026-08-10", "2026-08-11"])

    # HOUSE STYLE AND HONEST ROUNDING, both checked on the real rendered page.
    check("no page prints day(s), which is a machine talking", "day(s)" not in b + bm)
    check("the date reads in house style, not ISO",
          "August 10th, 2026" in b and "2026-08-10" not in b)
    check("a share that is not zero is never published as zero",
          share(0.0437) == "0.04" and share(0.0004) == "0.0004" and share(0.0) == "0.00",
          f"{share(0.0437)} {share(0.0004)} {share(0.0)}")
    tiny = [rec("2026-08-10", 83118.16, 58093.11)]
    tiny[0]["fuel_energy_mwh"] = dict(tiny[0]["fuel_energy_mwh"], Hydro=745.0)
    bt = body(tiny, "2026-08-11")
    check("a tiny real contribution shows a real number on the page",
          ">0.05<" in bt or "0.05" in bt, "hydro share missing")
    check("...and it still passes the numeral gate", not lint(bt, figures(tiny)),
          str(lint(bt, figures(tiny))[:6]))
    check("a charging battery is labelled, not left as an empty cell",
          "charging" in b and "<td class=\"n num\"></td>" not in b)
    check("the forecast miss says which way it missed",
          "ERCOT forecast high" in b, "direction missing")

    check("hour ending 17 reads as the hour it actually covers", hour(17) == "4pm to 5pm",
          str(hour(17)))
    check("hour ending 24 wraps to midnight", hour(24) == "11pm to 12am", str(hour(24)))
    check("hour ending 1 reads from midnight", hour(1) == "12am to 1am", str(hour(1)))

    if failures:
        print(f"\ngridwatch_page self-test: {failures} FAILED")
        return 1
    print("\ngridwatch_page self-test: all passed")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
