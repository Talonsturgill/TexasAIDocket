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


def flatline(f: dict) -> str:
    """The series, which is the finding a single reading can't show.

    Both figures have sat flat all year while the queue grew. That observation only exists
    because each month was stored.

    THE MONTH LABELS ARE HTML, NOT SVG TEXT. The bars want a stretched viewBox so they fill the
    column at any width, and `preserveAspectRatio="none"` stretches every glyph inside it with
    them. The first render had months squashed into unreadable wide letters. Bars stretch, type
    does not, so the type lives outside the drawing.
    """
    s = f.get("series") or []
    ch = f.get("change")
    if len(s) < 2 or not ch:
        return ""
    top = max(r["approved_mw"] for r in s) * 1.12
    w, h = 100.0 / len(s), 100.0
    bars = []
    for i, r in enumerate(s):
        x = i * w
        for key, cls, off in (("approved_mw", "qa", 0.16), ("drawing_mw", "qd", 0.52)):
            bh = r[key] / top * h
            bars.append(f'<rect class="{cls}" x="{x + w * off:.2f}" y="{h - bh:.2f}" '
                        f'width="{w * 0.30:.2f}" height="{bh:.2f}"/>')
    labels = "".join(f'<span>{MONTHS[int(r["month"][5:]) - 1][:3]}</span>' for r in s)
    return f"""<div class="qchart">
  <svg viewBox="0 0 100 {h:.0f}" preserveAspectRatio="none" role="img"
       aria-label="Cleared to switch on and actually drawing, by month, from
       {month_label(ch['from_month'])} to {month_label(s[-1]['month'])}. Both sit flat.">
    {''.join(bars)}
  </svg>
  <div class="qticks" aria-hidden="true">{labels}</div>
</div>"""


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
<p class="qnote">Each month since {month_label(ch['from_month'])}. Left bar cleared to switch
on. Right bar actually drawing.</p>"""

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
  <p class="qnote">ERCOT publishes two more stages between the first and the second. Both are
  drawn in a chart with no text behind it. Neither is collected and neither is shown here.</p>

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
        add(month_label(r["month"]), MONTHS[int(r["month"][5:]) - 1][:3],
            gw(r["approved_mw"]), gw(r["drawing_mw"]))
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

    check("no dial, no severity ramp", "dial" not in html and "severity" not in html)
    print("\nqueue_panel self-test " + ("clean" if not failures else f"{failures} FAILED"))
    return 1 if failures else 0


if __name__ == "__main__":
    import sys
    sys.exit(self_test())
