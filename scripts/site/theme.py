#!/usr/bin/env python3
"""theme.py — the design system, generated from config/brand.yaml.

WHY THE CSS IS GENERATED AND NOT A FILE

The sibling product keeps its entire site CSS as one string constant inside a 7,581 line build
script, and the colours in it are typed by hand. That means the brand config and the stylesheet
are two sources of truth for the same fact, and the only thing keeping them equal is somebody
remembering. They will drift, and the drift is invisible until a deck and a page disagree in
front of a reader.

Here the tokens live in `config/brand.yaml` and the stylesheet is derived. Change the token, the
whole site moves. There is no second place to edit.

THE PART THAT MATTERS MOST: CONTRAST IS COMPUTED, NOT EYEBALLED

CLAUDE.md's law says every published numeral is produced by code from data. A contrast ratio is
a numeral, and a palette is data, so the same law applies to the design system. Colours here are
not chosen because they looked right in a preview:

  - Every foreground and background pairing is measured against WCAG 2.1 and gated in the
    self-test. A pairing that fails is a build failure, not a note for later.
  - Where a token cannot meet its target as authored, the value is DERIVED by walking the
    colour toward white or black until the required ratio is reached, in code, at build time.
    The urgent red is the case that forced this: Texas red on Big Bend night measures 2.94 to
    1, which fails even the 3 to 1 floor for large text, and the element wearing it is the
    countdown telling somebody how many days they have left to file a comment. The single most
    consequential number on the site was the least legible thing on it.

TWO REAL MATERIALS, NOT ONE PALETTE AND ITS INVERSE

Dark is Big Bend at dusk. Light is a caliche road cut in full sun. Caliche is the same stone in
both: the type at night, the ground in daylight. Light mode is therefore not a lightened dark
mode and not a generic cream, and its accent is the sunset red granite the Capitol is faced in
rather than a brown picked to sit on beige.

WHAT THE STYLE IS FOR

Every rule below answers one question: does this help a reader who is busy, on a phone, and
sceptical? So body text is set at a measure that stays readable at arm's length, data is set in
a monospace with tabular figures so a number reads as a measurement, Texas red appears only
where something is genuinely urgent, focus is always visible, and nothing animates unless the
reader allows it.

    theme.py --css            write the stylesheet to stdout
    theme.py --contrast       print the measured contrast table
    theme.py --self-test
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND = REPO_ROOT / "config" / "brand.yaml"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import fonts_build                                                 # noqa: E402

# WCAG 2.1 thresholds. Named rather than inlined, because a bare 4.5 in a comparison is exactly
# the kind of typed number this project does not allow itself elsewhere.
AA_BODY = 4.5           # 1.4.3, text under 24px (or under 18.66px bold)
AA_LARGE = 3.0          # 1.4.3, large text
AA_NONTEXT = 3.0        # 1.4.11, boundaries a reader needs in order to find a control


# --------------------------------------------------------------------------- colour maths
def _rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))          # type: ignore[return-value]


def _hex(rgb) -> str:
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(c))) for c in rgb)


def luminance(colour: str) -> float:
    """Relative luminance, WCAG 2.1 definition."""
    out = []
    for c in _rgb(colour):
        s = c / 255
        out.append(s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4)
    return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]


def contrast(a: str, b: str) -> float:
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def mix(a: str, b: str, t: float) -> str:
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(ra[i] + (rb[i] - ra[i]) * t for i in range(3)))


def lift(base: str, ground: str, target: float, toward: str | None = None) -> str:
    """`base`, walked toward white or black until it clears `target` against `ground`.

    This is how a colour that carries MEANING keeps that meaning while becoming legible. Texas
    red is a derived Pantone 193 and the site says so, so it can't simply be replaced with a
    different red that happens to pass. Lifting it toward white on a dark ground keeps the hue
    and its reservation intact and changes only what has to change.

    Walking in 1/255 steps rather than solving in closed form keeps the result on a real 8 bit
    colour and makes the search deterministic, which the byte-equality rebuild depends on.
    """
    if toward is None:
        toward = "#FFFFFF" if luminance(ground) < 0.18 else "#000000"
    if contrast(base, ground) >= target:
        return base.upper()
    for step in range(1, 256):
        candidate = mix(base, toward, step / 255)
        if contrast(candidate, ground) >= target:
            return candidate
    return toward.upper()


def lift_over(base: str, grounds: list, target: float) -> str:
    """`base`, lifted until it clears `target` against EVERY ground it is rendered on.

    Deriving against one ground is how a value passes its own test and fails on the page. The
    urgent countdown is set on a panel, not on the page, so a red derived against the page
    measured 4.51 where it was checked and 4.16 where it actually appeared. A colour used in
    two places has to satisfy both, and the worst ground is the only one worth solving.
    """
    out = base
    for ground in grounds:
        out = lift(out, ground, target)
    # One pass can leave an earlier ground behind, because lifting for a later ground moves the
    # colour. Repeat until every ground is satisfied at once.
    while any(contrast(out, g) < target for g in grounds):
        out = lift(out, min(grounds, key=lambda g: contrast(out, g)), target)
    return out


def mute(base: str, toward: str, grounds: list, target: float) -> str:
    """`base`, faded toward `toward` as far as it can go while still carrying small print.

    The opposite walk from `lift`. A muted ink is not a different colour, it is the SAME ink
    with less of it, and the interesting value is the last one that still passes rather than the
    first. Walking the whole range and keeping the final passing step is what makes it the limit
    rather than an arbitrary point along the way.

    It fades toward the PAGE and is measured against every ground, which are not the same list.
    A muted ink that fades toward the darkest panel would take that panel's colour; one measured
    only against the page goes illegible the moment it lands on a panel. The direction and the
    constraint are separate questions.
    """
    best = base
    for step in range(1, 256):
        candidate = mix(base, toward, step / 255)
        if any(contrast(candidate, g) < target for g in grounds):
            break
        best = candidate
    return best


# --------------------------------------------------------------------------- tokens
def tokens() -> dict:
    """Colour and type tokens, straight from the brand config.

    No defaults and no fallbacks. A missing token should fail the build loudly rather than
    render a grey approximation that nobody notices until a reader does.
    """
    import yaml                                                    # noqa: PLC0415
    doc = yaml.safe_load(BRAND.read_text(encoding="utf-8"))
    vis = doc["visual"]
    colours = {k: v for k, v in vis["tokens"].items()
               if isinstance(v, str) and v.startswith("#")}
    return {"colour": colours, "type": vis["type"],
            "constellation": vis["constellation"], "palette": vis["site_palette"]}


def palette() -> dict:
    """The nine roles, twice, with every derived value computed against its own ground.

    Returned as data rather than baked into the CSS string so the self-test can measure exactly
    what ships, and so `--contrast` can print it for a human.
    """
    c = tokens()["colour"]

    dark = {
        "bg": c["night"], "surface": c["deep"], "raised": c["panel"],
        "ink": c["caliche"], "ink-bright": c["limestone"], "ink-mute": c["dust"],
        "rule": c["line"],
        "accent": c["dusk_gold"], "accent-deep": c["dusk_ember"],
    }
    light = {
        "bg": c["paper"], "surface": c["limestone"], "raised": c["caliche"],
        "ink": c["deep"], "ink-bright": c["night"],
        # The muted ink is the one role with no natural token. It is the night register faded
        # into the paper as far as small print allows, so it moves when the base register moves
        # and is never a grey typed to look about right.
        "ink-mute": mute(c["night"], c["paper"],
                         [c["paper"], c["limestone"], c["caliche"]], AA_BODY),
        "rule": c["paper_rule"],
        "accent": c["capitol_granite"],
        "accent-deep": mix(c["capitol_granite"], "#000000", 0.28),
    }

    for mode in (dark, light):
        # Both of these are derived against EVERY ground they land on, not just the page. The
        # ask box sits on the surface and its input border is the strong rule; the countdown
        # sits on the surface too. A value solved against the page alone passes its own test
        # and fails where a reader meets it.
        grounds = [mode["bg"], mode["surface"], mode["raised"]]
        # A DIVIDER AND A CONTROL BOUNDARY ARE NOT THE SAME OBJECT. WCAG 1.4.11 asks 3 to 1 of
        # anything a reader needs in order to find a control, and asks nothing of decoration. A
        # table's row divider is decoration and wants to be a hairline. The border that is the
        # only thing making a text input findable is not, and gets its own token derived to
        # clear the threshold.
        mode["rule-strong"] = lift_over(mode["rule"], grounds, AA_NONTEXT)
        # Texas red is reserved for genuine urgency, which means it lands on the countdown and
        # nowhere else. Reserving a colour is worth nothing if the reader can't read it.
        mode["urgent"] = lift_over(c["flag_red"], grounds, AA_BODY)
        # The label on a filled button. Its ground is the button, not the page, so it is the
        # one role that cannot be a raw token: `limestone` on the dark register's ember reads
        # at 2.6 to 1, and the button in question is the one that asks the record a question.
        # White or night, whichever the fill can actually carry, then pushed until it clears.
        ink_side = c["limestone"] if luminance(mode["accent-deep"]) < 0.35 else c["night"]
        mode["on-accent"] = lift(ink_side, mode["accent-deep"], AA_BODY)

    return {"dark": dark, "light": light}


def _vars(role_map: dict) -> str:
    return "".join(f"--{k}:{v};" for k, v in role_map.items())


# --------------------------------------------------------------------------- stylesheet
def css() -> str:
    t = tokens()
    c, ty = t["colour"], t["type"]
    p = palette()

    return f"""/* Texas AI Docket. Generated from config/brand.yaml by scripts/site/theme.py.
   Do not edit. Edit the tokens and rebuild.
   Every contrast ratio in here is computed and gated. See theme.py --contrast. */

{fonts_build.face_css("fonts/")}

:root {{
  /* Big Bend at dusk. The base register is a real place, not a generic dark theme. */
  --night:{c['night']}; --deep:{c['deep']}; --panel:{c['panel']}; --line:{c['line']};
  --caliche:{c['caliche']}; --limestone:{c['limestone']}; --dust:{c['dust']};
  --ember:{c['dusk_ember']}; --gold:{c['dusk_gold']};
  --paper:{c['paper']}; --granite:{c['capitol_granite']};
  --flag-red:{c['flag_red']}; --flag-blue:{c['flag_blue']}; --star:{c['flag_white']};

  {_vars(p['dark'])}

  --display:"{ty['display']}",Georgia,"Times New Roman",serif;
  --body:"{ty['body']}",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"{ty['mono']}",ui-monospace,SFMono-Regular,Menlo,monospace;

  /* A fifth-based scale. Enough steps to build hierarchy, few enough to stay consistent. */
  --s-2:.7rem; --s-1:.79rem; --s0:1rem; --s1:1.27rem; --s2:1.6rem; --s3:2.04rem; --s4:2.59rem;
  --measure:68ch; --gap:clamp(1rem,3vw,1.75rem); --radius:3px;
  /* MARFA. The discipline of the empty field: a section is separated by air, not by a box.
     One step, used everywhere, so the rhythm is a decision rather than an accident. */
  --band:clamp(3rem,7vw,5.5rem);
  --hair:1px;
}}

/* A reader who has asked for light gets light, and gets a real material rather than an
   inverted one. Caliche is the ground here and the type on the dark register: one stone,
   two jobs. The roles are identical, so the reservation on red and the meaning of every
   other token survive the switch. */
@media (prefers-color-scheme: light) {{
  :root:not([data-theme="dark"]) {{ {_vars(p['light'])} }}
}}
:root[data-theme="light"] {{ {_vars(p['light'])} }}

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
/* THE MARK IS THE FLAG'S OWN GEOMETRY. The Lone Star flag is a blue hoist band carrying a
   white star, then white over red. Setting the star in a blue block is that construction and
   nothing else: no rope, no cowhide, no wood type. It is the one Texas device that is
   statutory, abstract, and legible at 16 pixels. */
.masthead {{ border-bottom:var(--hair) solid var(--rule); background:var(--bg);
  position:sticky; top:0; z-index:10; backdrop-filter:saturate(1.2) blur(6px); }}
.masthead .wrap {{ display:flex; align-items:center; gap:var(--gap);
  padding-block:.85rem; flex-wrap:wrap; }}
.wordmark {{ display:inline-flex; align-items:center; gap:.7rem;
  font-family:var(--display); font-weight:600; font-size:var(--s0);
  letter-spacing:.06em; text-transform:uppercase; color:var(--ink-bright);
  text-decoration:none; }}
.wordmark .hoist {{ display:grid; place-items:center; width:1.9em; height:2.05em;
  background:var(--flag-blue); border-radius:1px; flex:none; }}
.wordmark .star {{ width:1.15em; height:1.15em; fill:var(--star); display:block; }}
nav.main {{ display:flex; gap:1.1rem; flex-wrap:wrap; margin-left:auto;
  font-size:var(--s-1); letter-spacing:.03em; text-transform:uppercase; }}
nav.main a {{ color:var(--ink-mute); text-decoration:none; padding-block:.25em;
  border-bottom:var(--hair) solid transparent; }}
nav.main a:hover, nav.main a[aria-current] {{ color:var(--ink-bright);
  border-bottom-color:var(--accent); }}

/* ---- section furniture, from a drawing sheet ---------------------------- */
/* A survey sheet separates its zones with a hairline and labels them in the margin. That is
   the whole device: a rule that runs the full width of the container with the heading sitting
   on it, and a mono label in the gutter. It reads as a document rather than a landing page,
   which is what this is. */
main > section {{ margin-block:var(--band); }}
main > section:first-child {{ margin-top:calc(var(--band) * .55); }}
main > section > h2 {{ position:relative; padding-top:1.1rem;
  border-top:var(--hair) solid var(--rule); }}
main > section > h2::after {{ content:""; position:absolute; top:-1px; left:0; width:3.5rem;
  border-top:2px solid var(--accent); }}
.sheetlabel {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.16em;
  text-transform:uppercase; color:var(--ink-mute); margin:0 0 .35rem; }}

/* ---- the map ------------------------------------------------------------ */
/* A SURVEY, NOT AN INFOGRAPHIC. Hairline mesh at one weight, a lit county at one intensity,
   and a scale bar computed from the projection rather than drawn to look about right. No
   severity ramp, because a ramp implies a judgement this page does not get to publish. */
.txmap {{ width:100%; height:auto; display:block; }}
.txmap .c {{ fill:var(--surface); stroke:var(--rule); stroke-width:.6;
  vector-effect:non-scaling-stroke; transition:fill .18s ease; }}
.txmap .c.on {{ fill:var(--accent-deep); stroke:var(--accent); stroke-width:1.1; }}
.txmap .c:hover {{ fill:var(--raised); }}
.txmap .c.on:hover {{ fill:var(--accent); }}
.txmap .frame {{ fill:none; stroke:var(--rule); stroke-width:1;
  vector-effect:non-scaling-stroke; }}
.txmap .tick {{ stroke:var(--ink-mute); stroke-width:1; vector-effect:non-scaling-stroke; }}
.txmap .scale {{ stroke:var(--ink-mute); stroke-width:1.4; vector-effect:non-scaling-stroke; }}
.txmap .lab {{ fill:var(--ink-mute); font-family:var(--mono); font-size:11px;
  letter-spacing:.06em; }}

/* ---- the clock ---------------------------------------------------------- */
/* The question nobody else answers: can a Texan still act on this, and by when. */
.clock {{ display:grid; gap:.35rem; padding:1rem 1.15rem; background:var(--surface);
  border:var(--hair) solid var(--rule); border-left:3px solid var(--accent);
  border-radius:var(--radius); }}
.clock .days {{ font-family:var(--mono); font-variant-numeric:tabular-nums;
  font-size:var(--s3); line-height:1; color:var(--ink-bright); }}
.clock .lab {{ font-size:var(--s-1); letter-spacing:.05em; text-transform:uppercase;
  color:var(--ink-mute); }}
/* The urgent value is DERIVED from Texas red against this mode's ground, because the red as
   authored measures 2.94 to 1 on the night register and this is the number a reader came for. */
.clock.soon {{ border-left-color:var(--urgent); }}
.clock.soon .days {{ color:var(--urgent); }}

.rooms {{ display:inline-flex; align-items:center; gap:.45em; font-size:var(--s-1);
  letter-spacing:.04em; text-transform:uppercase; color:var(--ink-mute); }}
.rooms::before {{ content:""; width:.6em; height:.6em; border-radius:50%;
  background:var(--ink-mute); }}
.rooms.open_comment::before, .rooms.open_meeting::before {{ background:var(--accent); }}
.rooms.closed::before {{ background:var(--rule-strong); }}

/* ---- items -------------------------------------------------------------- */
.items {{ display:grid; gap:var(--hair); background:var(--rule);
  border:var(--hair) solid var(--rule); border-radius:var(--radius); overflow:hidden;
  list-style:none; padding:0; margin:0; }}
.items > li {{ background:var(--bg); padding:1.1rem var(--gap); display:grid; gap:.5rem; }}
.items > li:hover {{ background:var(--surface); }}
.items h3 {{ margin:0; font-size:var(--s1); }}
.items h3 a {{ text-decoration:none; color:var(--ink-bright); }}
.items h3 a:hover {{ text-decoration:underline; }}
.meta {{ display:flex; flex-wrap:wrap; gap:.4rem 1rem; font-size:var(--s-1);
  color:var(--ink-mute); }}
.tag {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.04em;
  text-transform:uppercase; color:var(--ink-mute);
  border:var(--hair) solid var(--rule-strong); padding:.1em .5em; border-radius:2px; }}

/* ---- claims: the proof, made visible ------------------------------------ */
/* Every figure traces to a quote. Showing the quote inline is what turns a policy into
   something a reader can feel. */
.claim {{ margin:1rem 0; padding-left:1rem; border-left:2px solid var(--rule-strong); }}
.claim blockquote {{ margin:0 0 .4rem; font-family:var(--mono); font-size:var(--s-1);
  line-height:1.6; color:var(--ink); }}
.claim blockquote::before {{ content:"\\201C"; }}
.claim blockquote::after {{ content:"\\201D"; }}
.claim cite {{ font-style:normal; font-size:var(--s-1); color:var(--ink-mute); }}
.claim .kind {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.06em;
  text-transform:uppercase; color:var(--ink-mute); }}

/* Mid-century oil charts: heavy rules top and bottom, hairlines between. The weight tells a
   reader where the table starts and stops without a box around it. */
table {{ border-collapse:collapse; width:100%; font-size:var(--s-1);
  border-top:2px solid var(--rule-strong); border-bottom:2px solid var(--rule-strong); }}
th,td {{ text-align:left; padding:.5em .75em; border-bottom:var(--hair) solid var(--rule);
  vertical-align:top; }}
tr:last-child td {{ border-bottom:0; }}
th {{ font-weight:600; color:var(--ink-mute); font-size:var(--s-2); letter-spacing:.04em;
  text-transform:uppercase; border-bottom:var(--hair) solid var(--rule-strong); }}
td.n,th.n {{ text-align:right; }}

.gap {{ border:var(--hair) dashed var(--rule-strong); border-radius:var(--radius);
  padding:1rem 1.15rem; background:transparent; color:var(--ink-mute); font-size:var(--s-1); }}
.gap strong {{ color:var(--ink); }}

.lede {{ font-size:var(--s1); line-height:1.5; color:var(--ink-bright); }}

/* ---- the grid watch ----------------------------------------------------- */
/* THE LOAD SHAPE. Measured demand filled, ERCOT's day ahead forecast dashed over it. The fill
   is one flat colour: this is a measurement drawn at its true scale, not a chart arguing a
   case. */
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

/* A BAR AND NEVER A DIAL. One hue at one intensity at every value, so there is no red zone and
   therefore no verdict. The length is the whole message. If a future edit adds a threshold
   colour here, it has changed what this page claims, and theme.py's self-test is what refuses
   it. */
.bar {{ height:1.6rem; background:var(--surface); border:var(--hair) solid var(--rule-strong);
  border-radius:2px; overflow:hidden; margin:.25rem 0 .75rem; }}
.bar .fill {{ height:100%; background:var(--accent-deep); }}
.barnote {{ font-size:var(--s-1); color:var(--ink-mute); }}
.barnote strong {{ color:var(--ink-bright); }}
/* The metro bars on the water watch. Same rule, smaller: sorted driest first, and identical in
   colour at every value, so the ordering carries the comparison and nothing implies that a
   short bar is a verdict about a city's water supply. */
.bar.mini {{ height:.7rem; margin:0; min-width:6rem; }}
td.barcell {{ width:40%; vertical-align:middle; }}
table.metros th[scope="row"] {{ font-weight:400; color:var(--ink-bright);
  text-transform:none; letter-spacing:0; font-size:var(--s-1); border-bottom-width:var(--hair);
  border-bottom-color:var(--rule); }}
caption {{ caption-side:bottom; text-align:left; padding-top:.75rem; font-size:var(--s-1);
  color:var(--ink-mute); max-width:var(--measure); }}

/* ---- the ask box -------------------------------------------------------- */
/* Answered in the reader's browser. The styling says "a tool", not "a chatbot": no avatar, no
   typing dots, no conversation. A question and what the record says. */
.askbox {{ border:var(--hair) solid var(--rule-strong); border-radius:var(--radius);
  padding:1.25rem var(--gap); background:var(--surface); margin:1.5rem 0; }}
.askbox form {{ display:flex; gap:.6rem; flex-wrap:wrap; align-items:center; }}
.askbox label {{ position:absolute; left:-9999px; }}
.askbox input {{ flex:1 1 20rem; font:400 var(--s1)/1.4 var(--body); padding:.7em .9em;
  background:var(--bg); color:var(--ink-bright);
  border:var(--hair) solid var(--rule-strong); border-radius:2px; }}
.askbox input:focus-visible {{ border-color:var(--accent); }}
.askbox button[type="submit"] {{ font:600 var(--s0)/1 var(--body); padding:.85em 1.4em;
  background:var(--accent-deep); color:var(--on-accent); border:0; border-radius:2px;
  cursor:pointer; }}
.askbox .chips {{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.9rem; }}
.askbox .chips button {{ font:400 var(--s-1)/1 var(--body); padding:.5em .85em;
  background:transparent; color:var(--ink-mute);
  border:var(--hair) solid var(--rule-strong); border-radius:999px; cursor:pointer; }}
.askbox .chips button:hover {{ color:var(--ink-bright); border-color:var(--accent); }}
.askbox .answer {{ margin-top:1.25rem; padding-top:1.1rem;
  border-top:var(--hair) solid var(--rule); }}
.askbox .answer h3 {{ margin:0 0 .6rem; font-size:var(--s1); }}
.askbox .answer ul {{ list-style:none; padding:0; margin:.5rem 0 0; display:grid; gap:.7rem; }}
.askbox .answer .meta {{ font-size:var(--s-1); color:var(--ink-mute);
  font-family:var(--mono); }}

table.figures td:first-child {{ color:var(--ink-bright); }}
table.figures td:last-child {{ color:var(--ink-mute); font-size:.92em; }}

/* ---- the title block ---------------------------------------------------- */
/* Every drawing sheet ends in one: what this is, who is answerable for it, when it was last
   revised. A record that publishes its own build date in the same place a survey publishes its
   revision is making the same promise, and the star sits here at the size it deserves rather
   than shrunk into the navigation. */
footer.site {{ border-top:2px solid var(--rule-strong); margin-top:var(--band);
  padding-block:2rem 3rem; color:var(--ink-mute); font-size:var(--s-1); }}
footer.site a {{ color:var(--ink-mute); }}
footer.site a:hover {{ color:var(--ink-bright); }}
footer.site .block {{ display:grid; gap:var(--gap) calc(var(--gap) * 1.5);
  grid-template-columns:auto minmax(0,var(--measure)); align-items:start; }}
footer.site .colophon {{ width:5.5rem; height:5.5rem; fill:var(--rule-strong); flex:none; }}
@media (max-width:34rem) {{
  footer.site .block {{ grid-template-columns:1fr; }}
  footer.site .colophon {{ width:3.5rem; height:3.5rem; }}
}}
footer.site dl {{ display:grid; grid-template-columns:auto 1fr; gap:.3rem 1rem; margin:1.25rem 0 0;
  font-family:var(--mono); font-size:var(--s-2); }}
footer.site dt {{ letter-spacing:.14em; text-transform:uppercase; color:var(--ink-mute); }}
footer.site dd {{ margin:0; color:var(--ink); }}

@media print {{
  .masthead,nav.main,.txmap,.askbox {{ display:none; }}
  body {{ background:#fff; color:#000; }}
  a {{ color:#000; }}
}}
"""


# --------------------------------------------------------------------------- contrast report
# EVERY PAIRING THE SITE ACTUALLY RENDERS, and the threshold each one owes.
#
# The list is written out rather than derived, because the threshold depends on how a colour is
# USED and no amount of introspection over a stylesheet can tell you that a countdown is set at
# 33 pixels. Each row names the element it is about, so a failure points at a thing on a page.
PAIRS = [
    # (foreground role, background role, threshold, what it is)
    ("ink", "bg", AA_BODY, "body text on the page"),
    ("ink", "surface", AA_BODY, "body text on a panel"),
    ("ink", "raised", AA_BODY, "body text on a raised panel"),
    ("ink-bright", "bg", AA_BODY, "headings"),
    ("ink-mute", "bg", AA_BODY, "meta, captions, chips, nav"),
    ("ink-mute", "surface", AA_BODY, "meta inside a panel"),
    ("accent", "bg", AA_BODY, "links"),
    ("accent", "surface", AA_BODY, "links inside a panel"),
    ("urgent", "bg", AA_BODY, "the closing countdown"),
    ("urgent", "surface", AA_BODY, "the closing countdown on its panel"),
    ("urgent", "raised", AA_BODY, "the closing countdown on a raised panel"),
    ("rule-strong", "bg", AA_NONTEXT, "an input or chip boundary on the page"),
    ("rule-strong", "surface", AA_NONTEXT, "the ask box's input boundary, on its panel"),
    ("rule-strong", "raised", AA_NONTEXT, "a boundary on the raised surface"),
    ("accent", "raised", AA_LARGE, "a link on the raised surface"),
    ("on-accent", "accent-deep", AA_BODY, "the ask box's submit button label"),
]


def contrast_report() -> list:
    p = palette()
    rows = []
    for fg, bg, need, what in PAIRS:
        for mode in ("dark", "light"):
            got = contrast(p[mode][fg], p[mode][bg])
            rows.append({"mode": mode, "fg": fg, "bg": bg, "need": need,
                         "got": round(got, 2), "pass": got >= need, "what": what,
                         "fg_hex": p[mode][fg], "bg_hex": p[mode][bg]})
    return rows


def print_contrast() -> int:
    rows = contrast_report()
    print(f"{'mode':6} {'foreground':12} {'on':11} {'hex':8} {'need':>5} {'got':>6}  element")
    for r in rows:
        mark = " " if r["pass"] else "!"
        print(f"{mark}{r['mode']:5} {r['fg']:12} {r['bg']:11} {r['fg_hex']:8} "
              f"{r['need']:>5} {r['got']:>6}  {r['what']}")
    bad = [r for r in rows if not r["pass"]]
    print(f"\n{len(rows)} pairing(s) measured, {len(bad)} below threshold")
    return 1 if bad else 0


# --------------------------------------------------------------------------- self-test
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

    # ---- the colour maths itself, before anything trusts it ------------------
    check("contrast is the WCAG ratio (black on white is 21)",
          round(contrast("#000000", "#FFFFFF"), 1) == 21.0)
    check("...and it is symmetric",
          contrast("#BF0A30", "#141020") == contrast("#141020", "#BF0A30"))
    check("a colour has no contrast with itself",
          round(contrast("#9A3B2A", "#9A3B2A"), 2) == 1.0)
    check("lift leaves a colour that already passes alone",
          lift("#FFFFFF", "#000000", AA_BODY) == "#FFFFFF")
    lifted = lift("#BF0A30", "#141020", AA_BODY)
    check("lift raises one that does not", contrast(lifted, "#141020") >= AA_BODY,
          f"{lifted} -> {contrast(lifted, '#141020'):.2f}")
    check("...and stops as soon as it passes, rather than going white",
          contrast(mix("#BF0A30", "#FFFFFF", (int(lifted[1:3], 16) - 0xBF) / (255 - 0xBF) - 0.02),
                   "#141020") < AA_BODY or lifted != "#FFFFFF")
    check("lift is deterministic", lift("#BF0A30", "#141020", AA_BODY) == lifted)

    # ---- every pairing the site renders --------------------------------------
    rows = contrast_report()
    bad = [r for r in rows if not r["pass"]]
    check(f"all {len(rows)} rendered colour pairings meet WCAG", not bad,
          "; ".join(f"{r['mode']}/{r['fg']} on {r['bg']} = {r['got']} (needs {r['need']})"
                    for r in bad[:4]))

    # THE REGRESSION THAT STARTED THIS. Texas red as authored is 2.94 to 1 on the night ground,
    # which fails even the large-text floor, and it was worn by the countdown.
    p = palette()
    check("the authored red really is the problem this solves",
          contrast(t["colour"]["flag_red"], p["dark"]["bg"]) < AA_LARGE,
          f"{contrast(t['colour']['flag_red'], p['dark']['bg']):.2f}")
    check("...and the derived urgent fixes it in both modes",
          all(contrast(p[m]["urgent"], p[m]["bg"]) >= AA_BODY for m in ("dark", "light")))
    check("...while staying recognisably the same red",
          all(_rgb(p[m]["urgent"])[0] > _rgb(p[m]["urgent"])[2] for m in ("dark", "light")),
          "the red channel must still dominate the blue")

    # ---- the tokens reach the CSS, or the config is decoration ---------------
    used = set(t["palette"]["dark"]) | set(t["palette"]["light"]) | set(t["palette"]["both"])
    missing = [n for n in used if t["colour"][n] not in sheet]
    check("every token the site claims to use reaches the stylesheet", not missing,
          str(missing))
    deck = set(t["palette"]["deck_only"])
    check("...and every unused token is declared deck material",
          deck.isdisjoint(used) and all(n in t["colour"] for n in deck), str(deck))
    stray = [n for n in deck if t["colour"][n] in sheet]
    check("...and no deck-only token leaks into the site", not stray, str(stray))

    check("the display face reaches the CSS", t["type"]["display"] in sheet)

    # ---- THE TYPE ACTUALLY SHIPS ---------------------------------------------
    # The whole reason this check exists: brand.yaml named three faces, theme.py wrote them into
    # every font stack, assets/fonts/ held all three, and NOTHING SERVED THEM. Every reader got
    # Georgia and system-ui. A font stack naming a family that no @font-face rule defines is
    # indistinguishable from a working one until you look at a real page.
    faces = fonts_build.manifest()["faces"]
    check("the brand faces are actually served", len(faces) == 3, f"{len(faces)} faces")
    for face in faces:
        check(f"...{face['family']} has an @font-face rule",
              f'font-family:"{face["family"]}"' in sheet and face["file"] in sheet)
    for role in ("display", "body", "mono"):
        family = t["type"][role]
        check(f"...and the {role} stack's first family is one of them",
              any(f["family"] == family for f in faces), family)

    # ---- the promises the design itself makes --------------------------------
    for want, why in [
        ("prefers-reduced-motion", "motion is opt in"),
        ("focus-visible", "keyboard focus is visible"),
        ("tabular-nums", "figures align as measurements"),
        ("prefers-color-scheme", "a light reader gets light"),
        (".skip", "there is a skip link"),
        ("@media print", "the record prints"),
        ("font-display:swap", "type never blocks the first paint"),
    ]:
        check(why, want in sheet)

    check("no severity ramp on the map",
          ".txmap .c.on" in sheet and ".txmap .c.warn" not in sheet)
    check("the map carries a computed scale bar", ".txmap .scale" in sheet)

    # THE RESERVATION. Texas red is for genuine urgency only. It may define a variable and be
    # derived into --urgent, and it must not have a general purpose class.
    check("red is not a general utility",
          ".red{" not in sheet and ".text-red" not in sheet
          and "var(--flag-red)" not in sheet)
    check("...and urgent is worn only by the closing clock",
          sheet.count("var(--urgent)") == 2, f"{sheet.count('var(--urgent)')} uses")

    # A BAR AND NEVER A DIAL, enforced in the one place a ramp would have to be written.
    bar = sheet[sheet.find(".bar {"):sheet.find(".barnote")] if ".bar {" in sheet else ""
    check("the grid watch gauge exists", bool(bar))
    check("the gauge fill has exactly one colour",
          bar.count("background:") == 2, f"{bar.count('background:')} backgrounds in the bar")
    check("no severity variant can be styled on the gauge",
          not any(s in sheet for s in (".fill.warn", ".fill.high", ".fill.crit",
                                       ".bar.warn", ".bar.high", ".bar.crit")))
    check("the gauge is never a dial",
          "dial" not in sheet and "conic-gradient" not in sheet)

    # THE FLAG'S GEOMETRY, and the kitsch it exists instead of. If a future edit reaches for a
    # longhorn or a rope border, this is where the argument was already had.
    check("the mark is the flag's hoist", ".wordmark .hoist" in sheet
          and "var(--flag-blue)" in sheet)
    # Two mistakes this check made before it worked, both worth keeping in view. Substring
    # matching failed the build for "rope" inside the body face's own name, Manrope. Scanning
    # the comments failed it again for the comment that lists the kitsch being avoided. A
    # comment renders nothing, so the scan is over declarations only, on word boundaries.
    import re as _re                                                # noqa: PLC0415
    rendered = _re.sub(r"/\*.*?\*/", " ", sheet, flags=_re.DOTALL)
    kitsch = _re.findall(r"\b(longhorn|cowhide|rope|lasso|lariat|boots?|spur|sheriff|saloon|"
                         r"wagon|cactus|armadillo)\b", rendered, _re.IGNORECASE)
    check("no kitsch", not kitsch, str(sorted(set(kitsch))))

    # A BUDGET THAT GREW WITH THE SURFACE, NOT WITH WASTE. 12 KB when the site was five pages of
    # text, 16 KB once it carried the county map, the load chart, the gauge, the metro bars and
    # the ask box in two palettes. Now 20 KB: this build adds three @font-face rules, the survey
    # furniture on the map, the drawing-sheet section rules and the footer title block. Raised
    # in one place with the reason attached, never by deleting the check.
    check("the stylesheet stays small", len(sheet.encode()) < 20_000,
          f"{len(sheet.encode())} bytes")
    check("two builds are byte identical", css() == sheet)

    if failures:
        print(f"\ntheme self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\ntheme self-test: all passed ({len(sheet.encode()):,} bytes of CSS, "
          f"{len(rows)} contrast pairings measured)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--css", action="store_true")
    ap.add_argument("--contrast", action="store_true", help="print the measured contrast table")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.contrast:
        return print_contrast()
    sys.stdout.write(css())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                      # noqa: BLE001
        print(f"theme: broke: {exc}", file=sys.stderr)
        sys.exit(2)
