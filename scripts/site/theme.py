#!/usr/bin/env python3
"""theme.py — the design system, generated from config/brand.yaml.

WHY THE CSS IS GENERATED AND NOT A FILE

The sibling product keeps its entire site CSS as one string constant inside a 7,581 line build
script, and the colours in it are typed by hand. That means the brand config and the stylesheet
are two sources of truth for the same fact, and the only thing keeping them equal is somebody
remembering. They will drift, and the drift is invisible until a deck and a page disagree in
front of a reader.

Here the tokens live in `config/brand.yaml` and the stylesheet is derived. Change the token,
the whole site moves. There is no second place to edit.

WHAT THE STYLE IS FOR

Every rule below is answering one question: does this help a reader who is busy, on a phone,
and sceptical? So:

  - Body text is caliche on Big Bend dusk, at a measure that stays readable at arm's length.
  - Data is set in a monospace with TABULAR figures, so columns line up and a number reads as
    a measurement rather than as prose.
  - Texas red appears only where something is genuinely urgent. Reserving it is what makes it
    mean anything, and the reservation is enforced here by simply not giving it a general
    purpose class.
  - Focus is always visible. A keyboard reader is not a second-class reader.
  - Nothing animates unless the reader allows it.

    theme.py --css            write the stylesheet to stdout
    theme.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND = REPO_ROOT / "config" / "brand.yaml"


def tokens() -> dict:
    """Colour and type tokens, straight from the brand config. No defaults, no fallbacks: if a
    token is missing the build should fail loudly rather than render a grey approximation."""
    import yaml
    doc = yaml.safe_load(BRAND.read_text(encoding="utf-8"))
    vis = doc["visual"]
    t = {k: v for k, v in vis["tokens"].items() if isinstance(v, str) and v.startswith("#")}
    return {"colour": t, "type": vis["type"], "constellation": vis["constellation"]}


def css() -> str:
    t = tokens()
    c, ty = t["colour"], t["type"]

    return f"""/* Texas AI Docket. Generated from config/brand.yaml by scripts/site/theme.py.
   Do not edit. Edit the tokens and rebuild. */

:root {{
  /* Big Bend at dusk. The base register is a real place, not a generic dark theme. */
  --night:{c['night']}; --deep:{c['deep']}; --panel:{c['panel']}; --line:{c['line']};
  --caliche:{c['caliche']}; --limestone:{c['limestone']}; --dust:{c['dust']};
  --rust:{c['rust']}; --ember:{c['dusk_ember']}; --gold:{c['dusk_gold']};
  --bluebonnet:{c['bluebonnet']}; --mesquite:{c['mesquite']};
  --flag-red:{c['flag_red']}; --flag-blue:{c['flag_blue']}; --star:{c['flag_white']};

  --bg:var(--night); --surface:var(--deep); --raised:var(--panel);
  --ink:var(--caliche); --ink-bright:var(--limestone); --ink-mute:var(--dust);
  --rule:var(--line); --accent:var(--gold); --accent-deep:var(--ember);

  --display:"{ty['display']}",Georgia,"Times New Roman",serif;
  --body:"{ty['body']}",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"{ty['mono']}",ui-monospace,SFMono-Regular,Menlo,monospace;

  /* A fifth-based scale. Enough steps to build hierarchy, few enough to stay consistent. */
  --s-1:.79rem; --s0:1rem; --s1:1.27rem; --s2:1.6rem; --s3:2.04rem; --s4:2.59rem;
  --measure:68ch; --gap:clamp(1rem,3vw,1.75rem); --radius:3px;
}}

/* A reader who has asked for light gets light. The palette inverts by role, so the
   reservation on red and the meaning of every other token survive the switch. */
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{
    --bg:#FBF8F1; --surface:#F3EEE2; --raised:#EDE6D6;
    --ink:#241E2E; --ink-bright:#0F0B18; --ink-mute:#5A5064;
    --rule:#D9CFBC; --accent:#8C4A22; --accent-deep:#6B3517;
  }}
}}
:root[data-theme="light"] {{
  --bg:#FBF8F1; --surface:#F3EEE2; --raised:#EDE6D6;
  --ink:#241E2E; --ink-bright:#0F0B18; --ink-mute:#5A5064;
  --rule:#D9CFBC; --accent:#8C4A22; --accent-deep:#6B3517;
}}

*,*::before,*::after {{ box-sizing:border-box; }}
html {{ -webkit-text-size-adjust:100%; scroll-behavior:smooth; }}
@media (prefers-reduced-motion:reduce) {{
  html {{ scroll-behavior:auto; }}
  *,*::before,*::after {{ animation-duration:.01ms!important; transition-duration:.01ms!important; }}
}}

body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:400 var(--s0)/1.65 var(--body);
  font-synthesis-weight:none; text-rendering:optimizeLegibility;
  /* Fonts load late. Reserving the metric stops the page reflowing under a reader's eye. */
  font-size-adjust:0.52;
}}

h1,h2,h3 {{ font-family:var(--display); font-weight:600; line-height:1.15;
  letter-spacing:-.012em; color:var(--ink-bright); margin:0 0 .5em; text-wrap:balance; }}
h1 {{ font-size:var(--s4); }} h2 {{ font-size:var(--s2); }} h3 {{ font-size:var(--s1); }}
p,li {{ max-width:var(--measure); text-wrap:pretty; }}
a {{ color:var(--accent); text-decoration-thickness:1px; text-underline-offset:.18em; }}
a:hover {{ color:var(--ink-bright); }}
:focus-visible {{ outline:2px solid var(--accent); outline-offset:3px; border-radius:2px; }}

/* Every figure on this site is a measurement. Tabular means columns align and a reader can
   compare two numbers by eye without counting digits. */
.num,time,td.n,.data {{ font-family:var(--mono); font-variant-numeric:tabular-nums;
  letter-spacing:-.01em; }}

.wrap {{ width:min(72rem,100% - 2*var(--gap)); margin-inline:auto; }}
.prose {{ width:min(var(--measure),100%); }}
.skip {{ position:absolute; left:-9999px; }}
.skip:focus {{ left:var(--gap); top:var(--gap); z-index:99; background:var(--raised);
  color:var(--ink-bright); padding:.6em 1em; border:1px solid var(--accent); }}

/* ---- masthead ---------------------------------------------------------- */
.masthead {{ border-bottom:1px solid var(--rule); background:var(--bg);
  position:sticky; top:0; z-index:10; backdrop-filter:saturate(1.2) blur(6px); }}
.masthead .wrap {{ display:flex; align-items:center; gap:var(--gap);
  padding-block:.85rem; flex-wrap:wrap; }}
.wordmark {{ display:inline-flex; align-items:center; gap:.55rem;
  font-family:var(--display); font-weight:600; font-size:var(--s0);
  letter-spacing:.06em; text-transform:uppercase; color:var(--ink-bright);
  text-decoration:none; }}
.wordmark .star {{ width:1.05em; height:1.05em; fill:var(--star); flex:none; }}
nav.main {{ display:flex; gap:1.1rem; flex-wrap:wrap; margin-left:auto;
  font-size:var(--s-1); letter-spacing:.03em; text-transform:uppercase; }}
nav.main a {{ color:var(--ink-mute); text-decoration:none; padding-block:.25em;
  border-bottom:1px solid transparent; }}
nav.main a:hover, nav.main a[aria-current] {{ color:var(--ink-bright);
  border-bottom-color:var(--accent); }}

/* ---- the map ------------------------------------------------------------ */
/* The record, rendered. A county is lit or it is not, at one intensity. No severity ramp,
   because a ramp implies a judgement this page does not get to publish. */
.txmap {{ width:100%; height:auto; display:block; }}
.txmap .c {{ fill:var(--surface); stroke:var(--rule); stroke-width:.8;
  vector-effect:non-scaling-stroke; transition:fill .18s ease; }}
.txmap .c.on {{ fill:var(--accent-deep); stroke:var(--accent); stroke-width:1.2; }}
.txmap .c:hover {{ fill:var(--raised); }}
.txmap .c.on:hover {{ fill:var(--accent); }}

/* ---- the clock ---------------------------------------------------------- */
/* The question nobody else answers: can a Texan still act on this, and by when. */
.clock {{ display:grid; gap:.35rem; padding:1rem 1.15rem; background:var(--surface);
  border:1px solid var(--rule); border-left:3px solid var(--accent); border-radius:var(--radius); }}
.clock .days {{ font-family:var(--mono); font-variant-numeric:tabular-nums;
  font-size:var(--s3); line-height:1; color:var(--ink-bright); }}
.clock .lab {{ font-size:var(--s-1); letter-spacing:.05em; text-transform:uppercase;
  color:var(--ink-mute); }}
.clock.soon {{ border-left-color:var(--flag-red); }}
.clock.soon .days {{ color:var(--flag-red); }}

.rooms {{ display:inline-flex; align-items:center; gap:.45em; font-size:var(--s-1);
  letter-spacing:.04em; text-transform:uppercase; color:var(--ink-mute); }}
.rooms::before {{ content:""; width:.6em; height:.6em; border-radius:50%;
  background:var(--ink-mute); }}
.rooms.open_comment::before, .rooms.open_meeting::before {{ background:var(--accent); }}
.rooms.closed::before {{ background:var(--rule); }}

/* ---- items -------------------------------------------------------------- */
.items {{ display:grid; gap:1px; background:var(--rule); border:1px solid var(--rule);
  border-radius:var(--radius); overflow:hidden; list-style:none; padding:0; margin:0; }}
.items > li {{ background:var(--bg); padding:1.1rem var(--gap); display:grid; gap:.5rem; }}
.items > li:hover {{ background:var(--surface); }}
.items h3 {{ margin:0; font-size:var(--s1); }}
.items h3 a {{ text-decoration:none; color:var(--ink-bright); }}
.items h3 a:hover {{ text-decoration:underline; }}
.meta {{ display:flex; flex-wrap:wrap; gap:.4rem 1rem; font-size:var(--s-1);
  color:var(--ink-mute); }}
.tag {{ font-family:var(--mono); font-size:.75rem; letter-spacing:.04em;
  text-transform:uppercase; color:var(--ink-mute); border:1px solid var(--rule);
  padding:.1em .5em; border-radius:2px; }}

/* ---- claims: the proof, made visible ------------------------------------ */
/* Every figure traces to a quote. Showing the quote inline is what turns a policy into
   something a reader can feel. */
.claim {{ margin:1rem 0; padding-left:1rem; border-left:2px solid var(--rule); }}
.claim blockquote {{ margin:0 0 .4rem; font-family:var(--mono); font-size:var(--s-1);
  line-height:1.6; color:var(--ink); }}
.claim blockquote::before {{ content:"\\201C"; }}
.claim blockquote::after {{ content:"\\201D"; }}
.claim cite {{ font-style:normal; font-size:var(--s-1); color:var(--ink-mute); }}
.claim .kind {{ font-family:var(--mono); font-size:.7rem; letter-spacing:.06em;
  text-transform:uppercase; color:var(--ink-mute); }}

table {{ border-collapse:collapse; width:100%; font-size:var(--s-1); }}
th,td {{ text-align:left; padding:.5em .75em; border-bottom:1px solid var(--rule);
  vertical-align:top; }}
th {{ font-weight:600; color:var(--ink-mute); font-size:.8rem; letter-spacing:.04em;
  text-transform:uppercase; }}
td.n,th.n {{ text-align:right; }}

.gap {{ border:1px dashed var(--rule); border-radius:var(--radius); padding:1rem 1.15rem;
  background:transparent; color:var(--ink-mute); font-size:var(--s-1); }}
.gap strong {{ color:var(--ink); }}

.lede {{ font-size:var(--s1); line-height:1.5; color:var(--ink-bright); }}

/* ---- the grid watch ----------------------------------------------------- */
/* THE LOAD SHAPE. Measured demand filled, ERCOT's day ahead forecast dashed over it. The
   fill is one flat colour: this is a measurement drawn at its true scale, not a chart
   arguing a case. */
.shape {{ margin:1.5rem 0; }}
.loadshape {{ width:100%; height:auto; display:block; }}
.loadshape .area {{ fill:var(--accent-deep); fill-opacity:.28; }}
.loadshape .line {{ fill:none; stroke:var(--accent); stroke-width:2;
  stroke-linejoin:round; vector-effect:non-scaling-stroke; }}
.loadshape .fc {{ fill:none; stroke:var(--ink-mute); stroke-width:1.4;
  stroke-dasharray:5 4; vector-effect:non-scaling-stroke; }}
.loadshape .g {{ stroke:var(--rule); stroke-width:1; vector-effect:non-scaling-stroke; }}
.loadshape .ax {{ fill:var(--ink-mute); font-family:var(--mono); font-size:11px; }}
.loadshape .ax.unit {{ font-size:9px; letter-spacing:.08em; }}
figcaption {{ font-size:var(--s-1); color:var(--ink-mute); margin-top:.5rem;
  max-width:var(--measure); }}

/* A BAR AND NEVER A DIAL. One hue at one intensity at every value, so there is no red zone
   and therefore no verdict. The length is the whole message. If a future edit adds a
   threshold colour here, it has changed what this page claims, and theme.py's self-test is
   what refuses it. */
.bar {{ height:1.6rem; background:var(--surface); border:1px solid var(--rule);
  border-radius:2px; overflow:hidden; margin:.25rem 0 .75rem; }}
.bar .fill {{ height:100%; background:var(--accent-deep); }}
.barnote {{ font-size:var(--s-1); color:var(--ink-mute); }}
.barnote strong {{ color:var(--ink-bright); }}
/* The metro bars on the water watch. Same rule, smaller: sorted driest first, and identical
   in colour at every value, so the ordering carries the comparison and nothing implies that
   a short bar is a verdict about a city's water supply. */
.bar.mini {{ height:.7rem; margin:0; min-width:6rem; }}
td.barcell {{ width:40%; vertical-align:middle; }}
table.metros th[scope="row"] {{ font-weight:400; color:var(--ink-bright);
  text-transform:none; letter-spacing:0; font-size:var(--s-1); }}
caption {{ caption-side:bottom; text-align:left; padding-top:.75rem; font-size:var(--s-1);
  color:var(--ink-mute); max-width:var(--measure); }}

table.figures td:first-child {{ color:var(--ink-bright); }}
table.figures td:last-child {{ color:var(--ink-mute); font-size:.92em; }}

footer.site {{ border-top:1px solid var(--rule); margin-top:4rem; padding-block:2rem 3rem;
  color:var(--ink-mute); font-size:var(--s-1); }}
footer.site a {{ color:var(--ink-mute); }}
footer.site a:hover {{ color:var(--ink-bright); }}

@media print {{
  .masthead,nav.main,.txmap {{ display:none; }}
  body {{ background:#fff; color:#000; }}
}}
"""


def self_test() -> int:
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    t = tokens()
    check("tokens load from brand.yaml", len(t["colour"]) >= 12, str(len(t["colour"])))
    sheet = css()

    # The tokens must actually reach the stylesheet, or the config is decorative.
    check("the night token reaches the CSS", t["colour"]["night"] in sheet)
    check("the caliche token reaches the CSS", t["colour"]["caliche"] in sheet)
    check("the display face reaches the CSS", t["type"]["display"] in sheet)

    # THE RESERVATION. Texas red is for genuine urgency only. It may define a variable and it
    # may be used by the soon-closing clock, and it must not have a general purpose class.
    red = t["colour"]["flag_red"]
    uses = sheet.count("var(--flag-red)")
    check("red is reserved to the closing clock", uses <= 2, f"used {uses} times")
    check("red is not a general utility", ".red{" not in sheet and ".text-red" not in sheet)

    for want, why in [
        ("prefers-reduced-motion", "motion is opt in"),
        ("focus-visible", "keyboard focus is visible"),
        ("tabular-nums", "figures align as measurements"),
        ("prefers-color-scheme", "a light reader gets light"),
        (".skip", "there is a skip link"),
        ("@media print", "the record prints"),
    ]:
        check(why, want in sheet)

    check("no severity ramp on the map",
          ".txmap .c.on" in sheet and ".txmap .c.warn" not in sheet)

    # A BAR AND NEVER A DIAL, enforced in the one place a ramp would have to be written. The
    # grid watch may show a length; it may not show a colour that means "bad", because that
    # is a reliability verdict and the data cannot carry one.
    bar = sheet[sheet.find(".bar {"):sheet.find(".barnote")] if ".bar {" in sheet else ""
    check("the grid watch gauge exists", bool(bar))
    check("the gauge fill has exactly one colour",
          bar.count("background:") == 2, f"{bar.count('background:')} backgrounds in the bar")
    check("no severity variant can be styled on the gauge",
          not any(s in sheet for s in (".fill.warn", ".fill.high", ".fill.crit",
                                       ".bar.warn", ".bar.high", ".bar.crit")))
    check("the gauge is never a dial",
          "dial" not in sheet and "conic-gradient" not in sheet)

    check("the stylesheet stays small", len(sheet.encode()) < 12_000,
          f"{len(sheet.encode())} bytes")
    check("two builds are byte identical", css() == sheet)

    if failures:
        print(f"\ntheme self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ntheme self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--css", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    sys.stdout.write(css())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                      # noqa: BLE001
        print(f"theme: broke: {exc}", file=sys.stderr)
        sys.exit(2)
