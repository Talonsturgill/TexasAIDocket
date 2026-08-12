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
import gzip
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND = REPO_ROOT / "config" / "brand.yaml"
sys.path.insert(0, str(Path(__file__).resolve().parent))

import fonts_build                                                 # noqa: E402
import grain                                                       # noqa: E402
import sky                                                         # noqa: E402

# WCAG 2.1 thresholds. Named rather than inlined, because a bare 4.5 in a comparison is exactly
# the kind of typed number this project does not allow itself elsewhere.
AA_BODY = 4.5           # 1.4.3, text under 24px (or under 18.66px bold)
AA_LARGE = 3.0          # 1.4.3, large text
AA_NONTEXT = 3.0        # 1.4.11, boundaries a reader needs in order to find a control

# The film grain tile, as a sibling of the stylesheet rather than a data URI inside it.
GRAIN_FILE = "grain.png"

# THE STYLESHEET BUDGET, MEASURED ON WHAT CROSSES THE WIRE.
#
# The first version of this gate counted uncompressed source bytes and called the limit "one round
# trip", which was the right intent measured on the wrong quantity twice over. GitHub Pages serves
# this compressed, so uncompressed bytes are not what a reader waits for; and a third of those
# bytes were maintainer comments, which are worth a great deal in theme.py and nothing at all in a
# browser. Stripped and compressed, the same sheet is 6 KB rather than 56 KB.
#
# The number itself is not a taste value. TCP opens at an initial congestion window of 10 segments,
# so roughly 14 KB arrives before the client has to acknowledge anything. A render blocking
# stylesheet inside that window costs one round trip; a byte over it costs two, which is the
# difference a reader actually perceives. So the budget is the window, and it is applied to the
# compressed bytes of the sheet as shipped.
INITIAL_CWND = 10 * 1460      # bytes delivered before the first ACK is needed

# The three page grounds anything can land on. ONE list, used both to derive the colours that
# must clear every ground and to generate the contrast table that proves they did.
GROUNDS = ("bg", "surface", "raised")


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
    #
    # THE CAP IS NOT DEFENSIVE PADDING, IT IS THE ONLY EXIT FROM AN IMPOSSIBLE ASK. `lift` picks
    # its direction per ground, toward white on a dark one and toward black on a light one, so a
    # set of grounds straddling that threshold makes the value ping-pong and the loop never
    # converges. `lift_over("#BF0A30", ["#141020", "#F6F1E4"], 4.5)` spins forever. That set is
    # not a bug in this function, it is a palette asking one colour to be legible on both a near
    # black and a near white ground, which no single colour does at 4.5 to 1. Uncapped, the
    # symptom is the site build and its self-test hanging in CI with no output, which reads as
    # an infrastructure fault rather than a palette that cannot be satisfied.
    for _ in range(512):
        failing = [g for g in grounds if contrast(out, g) < target]
        if not failing:
            return out
        out = lift(out, min(failing, key=lambda g: contrast(out, g)), target)
    worst = min(grounds, key=lambda g: contrast(out, g))
    raise ValueError(
        f"no single colour derived from {base} clears {target}:1 against every ground in "
        f"{grounds}. The closest attempt was {out}, still {contrast(out, worst):.2f} against "
        f"{worst}. Grounds this far apart in luminance need two tokens, not one derivation.")


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
    """The nine roles, with every derived value computed against its own ground.

    ONE REGISTER. There used to be two, and the second one was never asked for. It existed
    because a second palette looks like diligence, and what it actually bought was a whole
    parallel rendering of the product that nobody wanted, nobody chose and nobody ever opened,
    including the person who wrote it: every check and every review screenshot forced dark. The
    first person to see the light register was the owner, on the live site, and what they saw was
    the dusk atmosphere multiplied into cream paper.

    A second theme is not free. It doubles the palette, doubles the contrast table, and doubles
    the number of renderings any visual check has to cover, and it will be the un-looked-at half
    that breaks. Deleted rather than fixed.

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

    for mode in (dark,):
        # Both of these are derived against EVERY ground they land on, not just the page. The
        # ask box sits on the surface and its input border is the strong rule; the countdown
        # sits on the surface too. A value solved against the page alone passes its own test
        # and fails where a reader meets it.
        grounds = [mode[g] for g in GROUNDS]
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
        # THE SIGNAL COLOURS ARE DERIVED PER MODE, and this is not a formality. A spring green
        # that reads beautifully on Big Bend night measures under 2 to 1 on caliche paper, and
        # the thing wearing it is the word telling a reader a comment window is open to them.
        # Authored once, solved twice, against every ground it lands on.
        for role in ("sig-open", "sig-soon", "sig-shut", "sig-link"):
            mode[role] = lift_over(c[role.replace("-", "_").replace("sig_", "signal_")],
                                   grounds, AA_BODY)

    return {"dark": dark}


def _vars(role_map: dict) -> str:
    return "".join(f"--{k}:{v};" for k, v in role_map.items())


# --------------------------------------------------------------------------- stylesheet
def strip_comments(sheet: str) -> str:
    """The shipped sheet, without the reasoning a browser has no use for.

    The comments in `annotated()` are the record of why each value is what it is, and they belong
    in version control where a maintainer reads them, not in a render blocking download every
    reader pays for. `theme.py --css --annotated` prints them for a human.

    Safe as a plain regex here, and checked rather than assumed: the self-test asserts brace
    balance survives and that no `/*` appears inside a quoted value, which is the one way this
    could eat a declaration.
    """
    out = re.sub(r"/\*.*?\*/", "", sheet, flags=re.S)
    out = re.sub(r"[ \t]+\n", "\n", out)
    return re.sub(r"\n{2,}", "\n", out).strip() + "\n"


def css() -> str:
    """What ships."""
    return strip_comments(annotated())


def annotated() -> str:
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

  --display:"{ty['display']}","Fraunces fallback",Georgia,"Times New Roman",serif;
  --body:"{ty['body']}","Manrope fallback",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:"{ty['mono']}",ui-monospace,SFMono-Regular,Menlo,monospace;

  /* SIGNAL COLOURS. Not decoration and not a second accent. Each one means exactly one thing
     about a public process, and nothing else on the site may wear it. `open` is the one a
     reader is looking for, which is why it is the only cool hue in a warm palette and reads
     instantly against everything around it. */
  /* Derived per mode, because a spring green that sings on Big Bend night is invisible on
     caliche paper. See theme.py --contrast. */

  /* A fifth-based scale. Enough steps to build hierarchy, few enough to stay consistent. */
  --s-2:.7rem; --s-1:.79rem; --s0:1rem; --s1:1.27rem; --s2:1.6rem; --s3:2.04rem; --s4:2.59rem;
  /* THE DISPLAY SIZE IS ITS OWN SCALE, and this is most of the difference between a page that
     reads as designed and one that reads as a document with a slightly bigger first line. The
     type scale above tops out around 41 pixels, which is a fine size for a heading and far too
     small for a masthead. A front page gets to be loud once. */
  --d1:clamp(2.6rem,7.4vw,5.6rem); --d2:clamp(1.75rem,3.6vw,2.5rem);
  --measure:68ch; --gap:clamp(1rem,3vw,1.75rem); --radius:3px; --radius-lg:12px;
  /* MARFA. The discipline of the empty field: a section is separated by air, not by a box.
     One step, used everywhere, so the rhythm is a decision rather than an accident. */
  --band:clamp(3rem,7vw,5.5rem);
  --hair:1px;
  --shell:72rem;
}}

/* ONE REGISTER, AND THIS IS IT. There was a second palette here that nobody asked for. It
   followed the operating system, so a reader on a light machine got a whole parallel rendering of
   the site, and the first person ever to look at that rendering was the owner, on the live site.
   Everything that checks this page forced dark, and so did every screenshot taken while building
   it, so the half that broke was the half nobody opened.
   A second theme is not free. It doubles the palette, doubles the contrast table, and doubles the
   renderings any visual check has to cover. It was deleted rather than fixed, because the fix
   preserves the cost and the cost is what produced the fault. */

*,*::before,*::after {{ box-sizing:border-box; }}
/* THE CLIP GOES ON html, NOT body. The masthead's full-bleed glass panel is 100vw wide
   and off-centre by design, so something has to contain it. Putting `overflow-x:clip` on
   `body` does contain it and also silently breaks `position:sticky` on everything inside,
   because a clipping ancestor becomes the scroll container the sticky element resolves
   against: the bar detached and rode down the page over the copy. */
html {{ -webkit-text-size-adjust:100%; scroll-behavior:smooth; overflow-x:clip; }}
@media (prefers-reduced-motion:reduce) {{
  html {{ scroll-behavior:auto; }}
  *,*::before,*::after {{ animation-duration:.01ms!important; transition-duration:.01ms!important; }}
}}

/* THE SWAP REFLOW, which only became real when the fonts did. `font-display:swap` paints in the
   fallback and then re-lays-out when the real face arrives. Before this site served any font
   there was nothing to swap, so nothing shifted. Now three faces load on a cold cache, and
   without a metric override the reader watches the page jump under their eyes.
   `size-adjust` on a fallback-only family scales the fallback's glyphs to the real face's
   measured x-height ratio, so the two occupy nearly the same space and the swap is a change of
   shape rather than a change of layout. Ratios are the faces' own metrics. */
@font-face {{ font-family:"Manrope fallback"; src:local("Arial"),local("Helvetica"),
  local("Liberation Sans"); size-adjust:104%; ascent-override:100%; descent-override:26%; }}
@font-face {{ font-family:"Fraunces fallback"; src:local("Georgia"),local("Times New Roman"),
  local("Liberation Serif"); size-adjust:107%; ascent-override:96%; descent-override:24%; }}

body {{
  margin:0; background:var(--bg); color:var(--ink);
  font:400 var(--s0)/1.65 var(--body);
  font-synthesis-weight:none; text-rendering:optimizeLegibility;
  /* A LONG UNBREAKABLE TOKEN MUST NOT RUN OFF THE PAGE, and on this site the tokens are addresses
     somebody needs. A bare URL in one item's "how to take part" copy could not break, so at 390
     pixels it ran past the column and `overflow-x:clip` cut it dead: the phone reader was shown
     the first half of the address for filing their comment and no way to reach the rest.
     Set on `body` rather than on the paragraph that happened to break, because the record is
     written by a routine and the next long token is not going to be in the same element. */
  overflow-wrap:break-word;
}}

/* ---- the surface ------------------------------------------------------- */
/* FILM GRAIN OVER EVERYTHING. A perfectly smooth dark field is the loudest tell of a page
   nobody designed: ink, paper, film and photographs all have noise, and an eye that has looked
   at any of them reads a flat rectangle as a screen rather than a surface. One tiled 110 pixel
   square at low opacity, generated with no dependencies so it can never silently go missing.
   Fixed, so it does not scroll with the content and give away that it is a tile.
   IT IS ITS OWN FILE, NOT A DATA URI, and that is a first-paint decision rather than tidiness.
   Inlined it was 12 KB of base64 in the middle of a RENDER BLOCKING stylesheet, and base64 of an
   already-compressed PNG is close to incompressible, so it alone pushed the sheet past the
   initial congestion window and delayed first paint on every page for a texture nobody would
   notice arriving a beat late. As a file it loads in parallel and blocks nothing, and it stops
   costing the 33 percent that base64 adds. Relative with no leading slash, so it resolves
   against the stylesheet and works from any page depth and under a project path. */
body::after {{ content:""; position:fixed; inset:0; pointer-events:none; z-index:90;
  background-image:url({GRAIN_FILE}); mix-blend-mode:overlay; opacity:.5; }}

/* The reading position, as a hairline. Scroll-driven, so it runs on the compositor and costs
   no script at all. Nothing depends on it, which is why it is inside @supports rather than
   polyfilled. */
@supports (animation-timeline:scroll()) {{
  body::before {{ content:""; position:fixed; top:0; left:0; right:0; height:2px; z-index:95;
    background:linear-gradient(90deg,var(--accent-deep),var(--accent));
    transform-origin:0 50%; transform:scaleX(0);
    animation:progress linear both; animation-timeline:scroll(root); }}
  @keyframes progress {{ to {{ transform:scaleX(1); }} }}
}}
::selection {{ background:color-mix(in srgb,var(--accent) 28%,transparent); }}
::-webkit-scrollbar {{ width:11px; }}
::-webkit-scrollbar-thumb {{ background:var(--raised); border-radius:6px;
  border:3px solid var(--bg); }}
::-webkit-scrollbar-thumb:hover {{ background:var(--rule-strong); }}

/* ---- big bend at dusk --------------------------------------------------- */
/* The atmosphere. None of it is information and all of it is why the page reads as a place.
   Everything here is behind the content, ignores the pointer, and is hidden from assistive
   tech at the markup. */
/* YOU MUST NOT BE ABLE TO SEE WHERE WEATHER STOPS, and you could. Every warm layer in here is
   anchored to the BOTTOM of this box and reaches its maximum exactly where `overflow:hidden`
   cuts it off, so the page showed a hard horizontal seam right across it: sampled at a scroll of
   800 the brightest row of the horizon measured rgb(58,40,37) with rgb(8,6,15) directly beneath
   it, a 106 step drop over one pixel, looking like a rendering fault rather than a sky.
   THE FADE IS ON THE CONTAINER, NOT ON EACH LAYER. Fading the horizon alone would fix the
   horizon and leave the next layer somebody adds to reintroduce the same edge. Masking the box
   makes the guarantee structural: nothing inside it can reach the cut at full strength.
   `--sky-fade` is the depth of that fade, and the rule for every layer inside is: REACH THE
   BOTTOM AND LET THE MASK DO IT. A layer that stops at the top of the fade zone instead just
   moves its own hard edge there, which is exactly what the first attempt at this did. Peaks go
   above the fade, geometry goes through it. */
.sky {{ --sky-fade:18vh;
  position:absolute; inset:0 0 auto 0; height:132vh; overflow:hidden;
  -webkit-mask-image:linear-gradient(180deg,#000 0 calc(100% - var(--sky-fade)),transparent 100%);
  mask-image:linear-gradient(180deg,#000 0 calc(100% - var(--sky-fade)),transparent 100%);
  pointer-events:none; z-index:0; }}

/* THE STAR FIELD IS EARNED. Big Bend is a certified International Dark Sky Park with among the
   least light pollution left in the lower 48, so a Texas night sky is genuinely one of the
   darkest and busiest in the country. That is the fact this is drawing. */
.sky .stars {{ position:absolute; inset:0; background-image:{sky.star_field_css()}; }}

/* HEAT SHIMMER, which is the Texas phenomenon where the sibling product has an aurora. The
   aurora is vertical, cold and northern. This is horizontal, warm and low: air off hot ground,
   banding and sliding sideways just above the skyline. Masked so it fades out before it can
   touch the type. */
.sky .shimmer {{ position:absolute; inset:auto 0 0; height:calc(70vh + var(--sky-fade));
  mix-blend-mode:screen;
  background:repeating-linear-gradient(2deg,transparent 0 6%,
    color-mix(in srgb,var(--accent) 9%,transparent) 8% 10.5%,
    color-mix(in srgb,var(--accent) 3%,transparent) 12% 15%,transparent 17% 24%,
    color-mix(in srgb,var(--accent-deep) 7%,transparent) 26% 28.5%,transparent 30% 40%);
  background-size:240% 100%; filter:blur(18px);
  -webkit-mask-image:linear-gradient(0deg,#000 6%,rgba(0,0,0,.45) 42%,transparent 74%);
  mask-image:linear-gradient(0deg,#000 6%,rgba(0,0,0,.45) 42%,transparent 74%);
  animation:shimmer 52s ease-in-out infinite alternate; }}
.sky .shimmer.s2 {{ filter:blur(30px); opacity:.6; background-size:290% 100%;
  animation-duration:71s; animation-direction:alternate-reverse; }}
@keyframes shimmer {{ from {{ background-position:0% 0; }} to {{ background-position:100% 0; }} }}

/* Dusk cloud, drifting.
   THE WARM ONES SIT LOW AND THE HIGH ONE IS COOL, which is both the physics and the fix. At
   dusk the lit band is at the HORIZON and the sky overhead has already gone. The first version
   had the warm veils at the top of the page, so ember and gold were screening over the whole
   ground at once, and warm light screened over a violet ground is the definition of mauve. The
   page read pink. Warmth belongs where the sun went. */
.sky .veil {{ position:absolute; border-radius:50%; filter:blur(84px);
  mix-blend-mode:screen; opacity:.34; }}
/* The warm pair sit so their CENTRES clear the fade zone. A blurred ellipse whose middle is
   inside the fade loses most of itself and reads as a smudge rather than as cloud. */
.sky .v1 {{ width:64vw; height:34vh; left:30vw; bottom:calc(var(--sky-fade) + 2vh);
  background:radial-gradient(closest-side,color-mix(in srgb,var(--accent) 34%,transparent),
    transparent 70%); animation:drift1 38s ease-in-out infinite alternate; }}
.sky .v2 {{ width:52vw; height:30vh; left:2vw; bottom:calc(var(--sky-fade) + 6vh);
  background:radial-gradient(closest-side,color-mix(in srgb,var(--accent-deep) 30%,transparent),
    transparent 70%); animation:drift2 47s ease-in-out infinite alternate; }}
/* The one high cloud, and it is cool. A dusk sky is warm at the bottom and cold at the top. */
.sky .v3 {{ width:46vw; height:32vh; left:22vw; top:-12vh; opacity:.26;
  background:radial-gradient(closest-side,color-mix(in srgb,var(--flag-blue) 46%,transparent),
    transparent 70%); animation:drift3 61s ease-in-out infinite alternate; }}
@keyframes drift1 {{ from {{ transform:translate(-5vw,0); }} to {{ transform:translate(6vw,3vh); }} }}
@keyframes drift2 {{ from {{ transform:translate(4vw,2vh); }} to {{ transform:translate(-6vw,-2vh); }} }}
@keyframes drift3 {{ from {{ transform:translate(0,0) scale(1); }}
  to {{ transform:translate(-4vw,2vh) scale(1.12); }} }}

/* THE HORIZON. The thing you actually see out there is the sun gone behind the Chisos and the
   bottom of the sky staying lit long after the top has gone dark.
   IT REACHES THE BOTTOM AND HOLDS ITS PEAK ON A PLATEAU. The band runs the full height of the box
   so the container's fade is what ends it, and the gradient holds full strength across the fade
   zone before climbing away, so the brightest row a reader sees sits just above the fade at the
   authored intensity rather than at some fraction of it. Without the plateau the mask multiplies
   the peak down to about three fifths and the dusk goes out of the dusk. */
.sky .horizon {{ position:absolute; inset:auto 0 0; height:calc(44vh + var(--sky-fade));
  mix-blend-mode:screen;
  background:linear-gradient(0deg,color-mix(in srgb,var(--accent) 20%,transparent) 0
      var(--sky-fade),
    color-mix(in srgb,var(--accent-deep) 9%,transparent) calc(var(--sky-fade) + 13vh),
    transparent 100%); }}

/* The mark in the sky, where the sibling puts its constellation. One star, not a pattern,
   which is the entire point of the thing. */
/* THE MARK IS ON THE FRONT PAGE ONLY. Everywhere else the top right of the page is content,
   not sky, and a 210 pixel star sat over the grid watch's chart and the record's first cards.
   The atmosphere still runs on every page; the mark does not. */
.sky .lonestar {{ display:none; }}
.home .sky .lonestar {{ display:block; position:absolute; right:4vw; top:7vh;
  width:min(21vw,210px); height:auto; opacity:.85; }}
.sky .lonestar .twinkle {{ animation:twinkle 5.5s ease-in-out infinite; }}
/* Scintillation rides on OPACITY and only on the halo subgroup. Animating a blur or a drop
   shadow repaints a huge area every frame, and a mark that flickers stops being a mark. */
@keyframes twinkle {{ 0%,100% {{ opacity:.8; }} 31% {{ opacity:.96; }} 52% {{ opacity:.86; }}
  74% {{ opacity:1; }} 88% {{ opacity:.9; }} }}
/* ON PAPER THERE IS NO SKY AT ALL, and the version that tried to keep one is what made the
   background pink. The old rule thinned the warm layers to 20 percent and switched them to
   multiply, on the theory that a night could become a daylight haze by turning it down. It
   cannot. Multiply takes the darker of the two, so the only thing a red veil can do to cream
   paper is stain it, and a stain spread across a soft field the width of the page is read as a
   colour rather than as weather. Measured at #F0E4D7, twelve points of red over green.
   The paper register is gone now, so the only place this still matters is print. A night sky
   does not print. */
@media print {{ .sky {{ display:none; }} }}

h1,h2,h3 {{ font-family:var(--display); font-weight:600; line-height:1.15;
  letter-spacing:-.012em; color:var(--ink-bright); margin:0 0 .5em; text-wrap:balance; }}
/* The display size is FLUID, because a fixed one is a size chosen for a desktop and endured
   everywhere else. At the top step on a 390 pixel phone the home headline ran to eight lines
   and pushed the record itself off the first two screens. */
h1 {{ font-size:clamp(var(--s2),6.2vw,var(--s4)); }}
h2 {{ font-size:clamp(var(--s1),4vw,var(--s2)); }} h3 {{ font-size:var(--s1); }}
/* The measure is for READING. A list item that is a card is a layout box, not a line of prose,
   and capping it at 68 characters left the container's own rule colour showing through the
   right half of every card on a wide screen. */
p,li {{ max-width:var(--measure); text-wrap:pretty; }}
.items > li, footer.site dd, footer.site dt {{ max-width:none; }}
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
/* GLASS ONLY ONCE THERE IS SOMETHING BEHIND IT. A solid bar pinned over the sky cuts the
   atmosphere off at the top of the page and is the first thing that makes a designed page look
   assembled. The panel fades in on scroll instead, full bleed, so at rest the mark simply sits
   in the sky. */
.masthead {{ position:sticky; top:0; z-index:80; }}
.masthead::before {{ content:""; position:absolute; inset:0; left:50%; width:100vw;
  margin-left:-50vw; z-index:-1; opacity:0;
  background:color-mix(in srgb,var(--bg) 82%,transparent);
  backdrop-filter:saturate(1.3) blur(14px); -webkit-backdrop-filter:saturate(1.3) blur(14px);
  border-bottom:var(--hair) solid var(--rule); transition:opacity .35s; }}
.masthead.scrolled::before {{ opacity:1; }}
.masthead .wrap {{ display:flex; align-items:center; gap:var(--gap);
  padding-block:1.15rem .9rem; flex-wrap:wrap; }}
.wordmark {{ display:inline-flex; align-items:center; gap:.7rem;
  font-family:var(--display); font-weight:600; font-size:var(--s0);
  letter-spacing:.06em; text-transform:uppercase; color:var(--ink-bright);
  text-decoration:none; }}
.wordmark .hoist {{ display:grid; place-items:center; width:1.9em; height:2.05em;
  background:var(--flag-blue); border-radius:1px; flex:none; }}
.wordmark .star {{ width:1.15em; height:1.15em; fill:var(--star); display:block; }}
nav.main {{ display:flex; gap:1.1rem; flex-wrap:wrap; margin-left:auto;
  font-size:var(--s-1); letter-spacing:.03em; text-transform:uppercase; }}
/* The underline WIPES IN from the left rather than switching on. It is two properties and a
   transition, and it is most of the difference between a nav that responds and a nav that
   toggles. */
nav.main a {{ color:var(--ink-mute); text-decoration:none; padding-block:.35em;
  position:relative; }}
nav.main a::after {{ content:""; position:absolute; left:0; right:100%; bottom:0; height:1.5px;
  background:var(--accent); transition:right .25s ease; }}
nav.main a:hover {{ color:var(--ink-bright); }}
nav.main a:hover::after {{ right:0; }}
nav.main a[aria-current] {{ color:var(--accent); }}
nav.main a[aria-current]::after {{ right:0; }}
/* ON A PHONE THE MASTHEAD LETS GO. Nine sections wrap to two rows at 390 pixels, and stuck to
   the top that is a third of the viewport permanently spent on navigation, on the one device
   the stated reader is most likely to be holding. It scrolls away instead, and the skip link
   above it is what a keyboard reader uses to get past it either way. */
@media (max-width:46rem) {{
  /* The mark comes off entirely. The nav wraps to two rows at this width and the hero starts
     right under it, so there is no clear field left to put a star in, and a mark tangled in
     the copy is worse than no mark. The sky keeps its stars, shimmer and horizon.
     WRITTEN AS `.home .sky` TO MATCH THE RULE IT IS OVERRIDING. The first version said
     `.sky .lonestar`, one class less specific than the `.home .sky .lonestar` that turns the mark
     on, and specificity beats both source order and being inside a media query, so the mark stayed
     on every phone with its glow sitting in the wrapped navigation. A media query is not a
     trump card. */
  .home .sky .lonestar {{ display:none; }}
  .masthead {{ position:static; }}
  .masthead::before {{ display:none; }}
  .masthead .wrap {{ gap:.6rem; }}
  nav.main {{ margin-left:0; gap:.5rem .9rem; font-size:var(--s-2); }}
}}

/* ---- the hero ----------------------------------------------------------- */
/* A front page gets to be loud once, and this is the once. The record itself is set at reading
   size everywhere else on the site. */
.hero {{ padding:clamp(2.5rem,9vh,7rem) 0 0; }}
/* A SHORT HEADLINE IS ALLOWED TO BE BIGGER, and that is the whole return on making it short. The
   opening line was fourteen words and had to be set at the shared display size to fit four rows
   inside the measure. At four words it fills one line with room to spare, so it takes its own step
   above `--d1` and a wider measure. `--d1` is left where it is, because the inner page titles use
   it and a docket title is a long sentence that would become a wall at this size. */
.hero h1 {{ font-size:clamp(3rem,9.2vw,7.6rem); line-height:1; letter-spacing:-.03em;
  max-width:22ch; margin:0; text-wrap:balance; }}
/* The one word that carries the argument, in the accent. `em` because the emphasis is real
   rather than decorative, so it survives with styles off and reads correctly aloud. */
.hero h1 em {{ font-style:normal; color:var(--accent); }}
.hero .herolede {{ font-size:clamp(1.05rem,2.1vw,1.32rem); line-height:1.5; color:var(--ink);
  max-width:46ch; margin:1.6rem 0 0; }}

/* THE TELEMETRY PILL. The sibling product opens with how much daylight its state capital has
   left today and how fast it is losing it, which is the single detail that makes its front
   page feel alive rather than published. The Texas equivalent is not daylight, it is the grid,
   which is what Texans actually argue about. Computed, dated, and never a verdict. */
/* INLINE-BLOCK, NOT FLEX. As a flex row the three parts became three columns the moment the
   line had to wrap, so on a phone the date sat in its own column beside a two-line middle. As
   inline-block with a text separator it wraps like the sentence it is. */
.tele {{ display:inline-block; font-family:var(--mono);
  font-size:var(--s-1); letter-spacing:.13em; text-transform:uppercase; color:var(--accent);
  border:var(--hair) solid color-mix(in srgb,var(--accent) 38%,transparent);
  border-radius:5px; padding:.55em .95em; background:color-mix(in srgb,var(--surface) 62%,transparent);
  margin-bottom:1.8rem; position:relative; overflow:hidden; text-decoration:none;
  max-width:100%; }}
.tele span + span::before {{ content:"\\00b7"; margin:0 .55em;
  color:color-mix(in srgb,var(--accent) 55%,transparent); }}
.tele > span:first-of-type::before {{ content:"\\00b7"; margin:0 .55em;
  color:color-mix(in srgb,var(--accent) 55%,transparent); }}
.tele::after {{ content:""; position:absolute; inset:0; transform:translateX(-130%) skewX(-18deg);
  background:linear-gradient(105deg,transparent 30%,
    color-mix(in srgb,var(--accent) 20%,transparent) 50%,transparent 70%);
  animation:sweep 9s ease-in-out infinite; }}
@keyframes sweep {{ 0%,74% {{ transform:translateX(-130%) skewX(-18deg); }}
  90%,100% {{ transform:translateX(130%) skewX(-18deg); }} }}

.ctarow {{ display:flex; gap:.9rem; flex-wrap:wrap; margin:2.4rem 0 0; }}
.cta {{ font-family:var(--mono); font-size:var(--s-1); letter-spacing:.12em;
  text-transform:uppercase; text-decoration:none; padding:.95em 1.5em; border-radius:6px;
  display:inline-block; position:relative; overflow:hidden;
  transition:transform .2s,box-shadow .2s,border-color .2s,color .2s; }}
.cta.solid {{ background:var(--accent-deep); color:var(--on-accent); font-weight:500;
  border:var(--hair) solid transparent; }}
.cta.solid:hover {{ transform:translateY(-2px);
  box-shadow:0 10px 30px color-mix(in srgb,var(--accent) 28%,transparent); }}
.cta.ghost {{ border:var(--hair) solid var(--rule-strong); color:var(--ink); }}
.cta.ghost:hover {{ border-color:var(--accent); color:var(--ink-bright); transform:translateY(-2px); }}
.cta:active {{ transform:translateY(0) scale(.985); }}

/* The counters. Mono, tabular, and every one of them computed from the record on this build. */
.statrow {{ display:flex; gap:clamp(1.5rem,4vw,2.6rem); flex-wrap:wrap; margin:2.8rem 0 0;
  font-family:var(--mono); }}
.stat .n {{ display:block; font-size:clamp(1.6rem,3.4vw,2.4rem); line-height:1;
  color:var(--ink-bright); font-variant-numeric:tabular-nums; letter-spacing:-.01em; }}
.stat .n.hot {{ color:var(--accent); }}
.stat .l {{ display:block; font-size:var(--s-2); letter-spacing:.17em; text-transform:uppercase;
  color:var(--ink-mute); margin-top:.45rem; }}

/* The hero arrives rather than appearing. Staggered, short, and only with script on, so a
   no-script reader sees everything immediately rather than nothing at all. */
html.js .rise > * {{ opacity:0; transform:translateY(20px);
  animation:rise .8s cubic-bezier(.2,.7,.2,1) forwards; }}
html.js .rise > *:nth-child(2) {{ animation-delay:.09s; }}
html.js .rise > *:nth-child(3) {{ animation-delay:.2s; }}
html.js .rise > *:nth-child(4) {{ animation-delay:.31s; }}
html.js .rise > *:nth-child(5) {{ animation-delay:.42s; }}
@keyframes rise {{ to {{ opacity:1; transform:none; }} }}
/* Same idea further down the page, driven by an observer.
   IT FAILS VISIBLE, WHICH IS THE WHOLE DESIGN. Hiding `[data-reveal]` in the stylesheet and
   relying on script to bring it back means any failure between those two points, a dead
   observer, a script error above this one, a browser that never fires the callback, leaves a
   reader looking at a blank column with the content present and invisible. So nothing is
   hidden by the stylesheet alone: JS marks each element `pending` at the moment it observes
   it, and only `pending` is hidden. No script, no marking, no hiding. */
[data-reveal].pending {{ opacity:0; transform:translateY(16px);
  transition:opacity .7s ease,transform .7s ease; }}
[data-reveal].pending.in {{ opacity:1; transform:none; }}

/* ---- section furniture, from a drawing sheet ---------------------------- */
/* A survey sheet separates its zones with a hairline and labels them in the margin. That is
   the whole device: a rule that runs the full width of the container with the heading sitting
   on it, and a mono label in the gutter. It reads as a document rather than a landing page,
   which is what this is. */
main > section {{ margin-block:var(--band); }}
main > section:first-child {{ margin-top:calc(var(--band) * .55); }}
/* AN INNER PAGE OPENS WITH AN H1 RATHER THAN A HERO, and the hero is what was carrying the
   clearance under the sticky bar. Without it the page title sits against the navigation.
   THIS IS ON `main`, NOT ON THE HEADING, because the heading version was written as
   `main > h1:first-child` and every item page wraps its title in an `<article>`. The selector
   matched the pages that were looked at and missed all thirteen of the ones that were not, which
   is the failure mode of styling by document shape: a wrapper somebody adds later silently drops
   the rule. Padding on the container cannot be defeated that way.
   The home page is exempt because its hero brings its own opening measure. */
main {{ padding-top:clamp(2rem,6vh,4rem); }}
.home main {{ padding-top:0; }}
main > section > h2 {{ position:relative; padding-top:1.1rem;
  border-top:var(--hair) solid var(--rule); }}
main > section > h2::after {{ content:""; position:absolute; top:-1px; left:0; width:3.5rem;
  border-top:2px solid var(--accent); }}

/* ---- the map ------------------------------------------------------------ */
/* A SURVEY, NOT AN INFOGRAPHIC. Hairline mesh at one weight, a lit county at one intensity,
   and a scale bar computed from the projection rather than drawn to look about right. No
   severity ramp, because a ramp implies a judgement this page does not get to publish. */
/* THE SHEET IS CAPPED. The map is 1000 by 900, so at full container width it stood taller than
   a laptop viewport and the record it illustrates started below the fold. Capping the WIDTH by
   the height budget keeps the aspect exact and lets the sheet be a figure on the page rather
   than the page. 1000/900 of 72vh is 80vh. */
.txmap {{ width:100%; max-width:min(100%,80vh); height:auto; display:block;
  margin-inline:auto; }}
/* THE MESH IS THE FIGURE, NOT FURNITURE, AND IT WAS DRAWN IN THE DIVIDER TOKEN. `rule` is the
   hairline that separates two rows of a table, and at 1.39 to 1 on the night register and 1.56
   on paper that is exactly right, because a divider is decoration and WCAG 1.4.11 asks nothing
   of decoration. The same value was carrying "every county in Texas, drawn from the state's own
   geometry", which made that sentence a caption for something a reader could not see. The state
   is drawn by its lines here rather than by a fill, deliberately, so the lines are the content
   and they get the token derived to clear the non-text floor.
   THE MESH STAYS QUIET BY WEIGHT, NOT BY CONTRAST. 254 counties at a readable ratio would shout
   if the stroke were heavy, and the temptation is to solve that by dimming the colour, which
   just puts the geometry back under the floor. Weight is the design lever. The threshold is the
   standard, and it does not move. */
.txmap .c {{ fill:var(--surface); stroke:var(--rule-strong); stroke-width:.5;
  vector-effect:non-scaling-stroke; transition:fill .18s ease; }}
/* The silhouette reads before the subdivision, so the outer boundary is the same colour at a
   heavier weight. Same reason: hierarchy by weight. */
.txmap .edge {{ fill:none; stroke:var(--rule-strong); stroke-width:1.4; stroke-linejoin:round;
  vector-effect:non-scaling-stroke; }}
.txmap .c.on {{ fill:var(--accent-deep); stroke:var(--accent); stroke-width:1.1; }}
.txmap .c:hover {{ fill:var(--raised); }}
.txmap .c.on:hover {{ fill:var(--accent); }}
.txmap .frame {{ fill:none; stroke:var(--rule); stroke-width:1;
  vector-effect:non-scaling-stroke; }}
.txmap .tick {{ stroke:var(--ink-mute); stroke-width:1; vector-effect:non-scaling-stroke; }}
.txmap .scale {{ stroke:var(--ink-mute); stroke-width:1.4; vector-effect:non-scaling-stroke; }}
.txmap .lab {{ fill:var(--ink-mute); font-family:var(--mono); font-size:11px;
  letter-spacing:.06em; }}
/* ON A NARROW SCREEN THE SURVEY LAYER COMES OFF. At 350 pixels the sheet's 11 unit type
   renders around 4 pixels, which is not small type, it is a smudge that reads as dirt on the
   map. A phone gets the locator: 254 counties and the ones the record touches. That is why the
   furniture is drawn as one group. */
@media (max-width:34rem) {{ .txmap .survey {{ display:none; }} }}

/* ---- the clock ---------------------------------------------------------- */
/* The question nobody else answers: can a Texan still act on this, and by when. */
/* THE COUNTDOWN WEARS THE SIGNAL, not the accent. The clock is only ever rendered when a window
   is OPEN, which is exactly the state the front page promises in green, and it was reading in the
   generic ink and the generic accent. Green while there is time, Texas red once there is not. */
.clock {{ display:grid; gap:.35rem; padding:1rem 1.15rem; background:var(--surface);
  border:var(--hair) solid var(--rule); border-left:3px solid var(--sig-open);
  border-radius:var(--radius); }}
.clock .days {{ font-family:var(--mono); font-variant-numeric:tabular-nums;
  font-size:var(--s3); line-height:1; color:var(--sig-open); }}
.clock .lab {{ font-size:var(--s-1); letter-spacing:.05em; text-transform:uppercase;
  color:var(--ink-mute); }}
/* The urgent value is DERIVED from Texas red against this mode's ground, because the red as
   authored measures 2.94 to 1 on the night register and this is the number a reader came for. */
.clock.soon {{ border-left-color:var(--urgent); }}
.clock.soon .days {{ color:var(--urgent); }}

/* THE ROOM INDICATOR, AND THE PROMISE IT HAS TO KEEP. The front page tells a reader in as many
   words that green means a door is open to them. This was painting both open states in `accent`,
   the generic link colour, so the home page's cards said green and the record page and all
   thirteen item pages said orange for the same items. The site contradicted its own instruction on
   fourteen of twenty seven pages, and no gate could see it: every token was correct, every ratio
   passed, and the only thing wrong was WHICH token reached the element. That is what the rendered
   check in tests/page_ground.mjs now measures.
   The word carries the colour as well as the dot, because "green" in that sentence is a promise
   about what a reader is looking for, and a coloured dot beside grey text is not what anybody
   scanning a list of thirteen decisions actually sees. */
.rooms {{ display:inline-flex; align-items:center; gap:.45em; font-size:var(--s-1);
  letter-spacing:.04em; text-transform:uppercase; color:var(--ink-mute); }}
.rooms::before {{ content:""; width:.6em; height:.6em; border-radius:50%;
  background:var(--ink-mute); }}
.rooms.open_comment, .rooms.open_meeting {{ color:var(--sig-open); }}
.rooms.open_comment::before, .rooms.open_meeting::before {{ background:var(--sig-open); }}
/* `contact_only` keeps the neutral ink on purpose. It is neither a door nor a decision, and
   giving it a signal colour would mean inventing a fifth meaning for a four state taxonomy. */
/* `comment_closed` is DERIVED rather than stored: a window the ledger recorded as open whose date
   has since passed. It wears the shut signal, because from where a reader stands it is shut. */
.rooms.closed, .rooms.comment_closed {{ color:var(--sig-shut); }}
.rooms.closed::before, .rooms.comment_closed::before {{ background:var(--sig-shut); }}

/* ---- items -------------------------------------------------------------- */
.items {{ display:grid; gap:var(--hair); background:var(--rule);
  border:var(--hair) solid var(--rule); border-radius:var(--radius); overflow:hidden;
  list-style:none; padding:0; margin:0; }}
/* THE COUNTDOWN SITS BESIDE THE DECISION, NOT ON TOP OF IT. As one more row in a single column
   grid the clock stretched to the full width of the list, so a panel holding three short lines
   ran better than a thousand pixels wide with most of it empty. That is what an unstyled default
   looks like, not a designed list. A narrow fixed column also lines every countdown up down the
   left edge, which is the entire point of a list ordered by how soon a reader can still act. */
.items > li {{ background:var(--bg); padding:1.1rem var(--gap); display:grid; gap:.5rem 1.4rem;
  align-items:start; }}
.items > li .clock {{ justify-self:start; min-width:9.5rem; }}
@media (min-width:46rem) {{
  /* `auto 1fr` RATHER THAN TWO AUTO ROWS, and the reason is a real grid rule rather than a
     preference. When an item spans rows that are all `auto`, the excess of its own height is
     distributed BETWEEN those rows, so the clock being taller than the title plus the meta pushed
     the two apart: the title row measured 50 pixels around a 23 pixel heading and the meta drifted
     down the card. `align-content` cannot fix that, because the rows are being SIZED larger rather
     than positioned. A single `1fr` row takes the slack instead, and the meta is pinned to its top,
     so the pair stay together and any leftover height falls below them where the clock is. */
  /* Wide enough that "CLOSES SEPTEMBER 4TH" stays on one line. A date broken across two lines is
     the one wrap worth spending column width to avoid, because the reader is here for the date. */
  .items > li {{ grid-template-columns:13.5rem minmax(0,1fr);
    grid-template-rows:auto 1fr; grid-template-areas:"clock title" "clock meta"; }}
  .items > li .clock {{ grid-area:clock; min-width:0; }}
  .items > li h3 {{ grid-area:title; }}
  .items > li .meta {{ grid-area:meta; align-self:start; margin:0; }}
}}
.items > li:hover {{ background:var(--surface); }}
.items h3 {{ margin:0; font-size:var(--s1); }}
.items h3 a {{ text-decoration:none; color:var(--ink-bright); }}
.items h3 a:hover {{ text-decoration:underline; }}

/* ---- the deadline cards ------------------------------------------------- */
/* The one question this site exists to answer, made scannable. A reader should be able to find
   what is open to them without reading a word of prose, which is what the status colour and
   the date at display size are for. */
.deck {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));
  gap:var(--gap); list-style:none; padding:0; margin:0; }}
.dcard {{ display:block; text-decoration:none; padding:1.4rem 1.5rem;
  border:var(--hair) solid var(--rule-strong); border-radius:var(--radius-lg);
  background:linear-gradient(165deg,var(--surface) 0%,var(--bg) 100%);
  transition:transform .25s,border-color .25s,box-shadow .25s; }}
.dcard:hover {{ transform:translateY(-3px); border-color:var(--accent);
  box-shadow:0 14px 38px color-mix(in srgb,var(--night) 45%,transparent); }}
.dcard.open {{ border-color:color-mix(in srgb,var(--sig-open) 45%,transparent); }}
/* THE DATE AT DISPLAY SIZE. A deadline is the payload, so it is set like a headline rather
   than like metadata. Serif, because a date read as a date wants to look like type and not
   like a readout. */
.dcard .big {{ display:block; font-family:var(--display); font-weight:600; font-size:2.5rem;
  line-height:1; color:var(--ink-bright); letter-spacing:-.02em; margin:.9rem 0 0; }}
.dcard.open .big {{ color:var(--sig-open); }}
.dcard .left {{ display:block; font-family:var(--mono); font-size:var(--s-1);
  color:var(--ink-mute); margin:.5rem 0 .9rem; font-variant-numeric:tabular-nums; }}
.dcard h3 {{ font-family:var(--body); font-weight:600; font-size:var(--s0); line-height:1.35;
  color:var(--ink-bright); margin:0; }}
.dcard .note {{ display:block; font-family:var(--mono); font-size:var(--s-2);
  letter-spacing:.08em; text-transform:uppercase; color:var(--ink-mute); margin-top:.7rem; }}

/* Status, as a word AND a colour. Never colour alone: about one man in twelve cannot separate
   these hues, and the state is the whole point of the card. */
.badge {{ display:inline-block; font-family:var(--mono); font-size:var(--s-2);
  letter-spacing:.13em; text-transform:uppercase; padding:.28em .7em; border-radius:4px;
  border:var(--hair) solid; }}
.badge.open {{ color:var(--sig-open); border-color:color-mix(in srgb,var(--sig-open) 55%,transparent);
  background:color-mix(in srgb,var(--sig-open) 8%,transparent); }}
.badge.soon {{ color:var(--sig-soon); border-color:color-mix(in srgb,var(--sig-soon) 55%,transparent);
  background:color-mix(in srgb,var(--sig-soon) 8%,transparent); }}
.badge.shut {{ color:var(--sig-shut); border-color:color-mix(in srgb,var(--sig-shut) 45%,transparent); }}
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
/* THE BOTTOM OF THE PAGE IS A PLACE, NOT A MARGIN. A record that ends in a build stamp and
   nothing else tells a reader they have reached the end of a document. The sibling product
   ends in a way out: what else there is, where to find it, and a colophon that says where the
   thing was made and what it promises. That last strip is the one people quote back. */
/* SIZED TO WHAT IS IN IT. The footer used to open with two paragraphs restating the site's
   promises, and the padding, the star and the margins were all set around that. With the prose
   gone it held 121 pixels of content inside 245 pixels of box: 91 of padding and a 32 pixel
   margin that existed only to separate the links from paragraphs that are no longer there.
   What is left is two rows of links and a colophon line, so it is sized like two rows of links
   and a colophon line. */
footer.site {{ border-top:2px solid var(--rule-strong); margin-top:var(--band);
  padding-block:1.8rem 2rem; color:var(--ink-mute); font-size:var(--s-1); }}
footer.site a {{ color:var(--ink-mute); text-decoration:none; transition:color .2s; }}
footer.site a:hover {{ color:var(--accent); }}
footer.site .block {{ display:grid; gap:var(--gap) calc(var(--gap) * 1.5);
  grid-template-columns:auto minmax(0,var(--measure)); align-items:start; }}
/* THE CLOSING MARK IS THE SAME STAR AS EVERY OTHER STAR, JUST QUIET. It was filled with
   `rule-strong`, the boundary token, which put a mid grey violet shape at full strength in the
   corner and read as a placeholder rather than as the mark. The ink at low opacity is the same
   star in the same colour the page is set in, and it flips with the mode, which a hardcoded white
   would not: on the paper register a white star is an empty corner. */
footer.site .colophon {{ width:4rem; height:4rem; fill:var(--ink); opacity:.28; flex:none; }}
@media (max-width:34rem) {{
  footer.site .block {{ grid-template-columns:1fr; }}
  footer.site .colophon {{ width:2.75rem; height:2.75rem; }}
}}
/* The way out. One row, mono, letterspaced, every section the site has. */
.footnav {{ display:flex; flex-wrap:wrap; gap:.6rem 1.4rem; margin:0; padding:0;
  list-style:none; font-family:var(--mono); font-size:var(--s-2); letter-spacing:.14em;
  text-transform:uppercase; }}
.footnav li {{ max-width:none; }}
/* The colophon. Where it was made, when it was last revised, the coordinates of that place,
   and the promise the whole product rests on, in one mono strip. */
/* A FLEX ROW, not a sentence with non-breaking separators in it. The first version joined the
   parts with a non-breaking space either side of the middot, which is correct typography and
   leaves the line no legal place to break, so the strip ran off the right edge of the page and
   took the promise at the end of it with it. Each part stays unbroken, the row wraps between
   them. */
.colophon-line {{ display:flex; flex-wrap:wrap; gap:0 .9rem; margin:1.1rem 0 0;
  font-family:var(--mono); font-size:var(--s-2); letter-spacing:.13em; text-transform:uppercase;
  color:var(--ink-mute); line-height:2; max-width:none; }}
.colophon-line span {{ white-space:nowrap; }}
.colophon-line span + span::before {{ content:"\\00b7"; color:var(--rule-strong);
  margin-right:.9rem; }}

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
# EVERY ROLE THAT LANDS ON A GROUND IS CHECKED AGAINST EVERY GROUND, generated rather than
# listed. The hand-written version was a second copy of the same fact as `GROUNDS` in `palette`,
# and the two had already drifted: light `ink-mute` on `raised` measures 4.51, one hundredth
# above the floor, and had no row, while `.txmap .lab` is ink-mute and `.txmap .c:hover` fills
# with raised, so map labels genuinely render there. It passed only because `mute()` happened to
# constrain against caliche. Editing one list without the other would have dropped a real
# pairing below 4.5 with the gate still reporting every pairing clean.
ON_EVERY_GROUND = [
    ("ink", AA_BODY, "body text"),
    ("sig-open", AA_BODY, "the word saying a comment window is open"),
    ("sig-soon", AA_BODY, "a window closing within the week"),
    ("sig-shut", AA_BODY, "a decided item"),
    ("sig-link", AA_BODY, "a link out to a source"),
    ("ink-bright", AA_BODY, "headings, the lede, the skip link"),
    ("ink-mute", AA_BODY, "meta, captions, chips, nav, map labels"),
    ("accent", AA_BODY, "links"),
    ("urgent", AA_BODY, "the closing countdown"),
    ("rule-strong", AA_NONTEXT, "an input or chip boundary, and the county mesh"),
]

# Pairings whose background is not one of the three page grounds, so they cannot be generated.
PAIRS_EXTRA = [
    ("on-accent", "accent-deep", AA_BODY, "the ask box's submit button label"),
]


def pairs() -> list:
    return [(fg, ground, need, f"{what}, on the {ground}")
            for fg, need, what in ON_EVERY_GROUND for ground in GROUNDS] + PAIRS_EXTRA


def contrast_report() -> list:
    p = palette()
    rows = []
    for fg, bg, need, what in pairs():
        for mode in ("dark",):
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

    # THE REGRESSION THAT STARTED THIS. Texas red as authored measured 2.94 to 1 on the night
    # ground, failing even the large-text floor, while worn by the comment countdown.
    #
    # The number MOVED when the ground was darkened from 9 percent lightness to 4 to fix the
    # page reading mauve, and it now clears the large-text floor. That is a real improvement
    # and it does not retire the derivation: the countdown is body-weight text and is held to
    # 4.5, which the authored red still misses. So the assertion is against the threshold that
    # actually governs the element rather than against the number it happened to measure on the
    # day it was written, which is what broke this test.
    p = palette()
    authored = contrast(t["colour"]["flag_red"], p["dark"]["bg"])
    check("the authored red still misses the floor its element is held to",
          authored < AA_BODY, f"{authored:.2f}")
    check("...and the derived urgent fixes it",
          contrast(p["dark"]["urgent"], p["dark"]["bg"]) >= AA_BODY,
          f'{contrast(p["dark"]["urgent"], p["dark"]["bg"]):.2f}')
    check("...while staying recognisably the same red",
          _rgb(p["dark"]["urgent"])[0] > _rgb(p["dark"]["urgent"])[2],
          "the red channel must still dominate the blue")

    # ---- the tokens reach the CSS, or the config is decoration ---------------
    used = (set(t["palette"]["dark"]) | set(t["palette"]["both"])
            | set(t["palette"].get("quoted_only", [])))
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
        (".skip", "there is a skip link"),
        ("@media print", "the record prints"),
        ("font-display:swap", "type never blocks the first paint"),
    ]:
        check(why, want in sheet)

    # ---- one register, and the paper one kept for the job it is right for ------
    # THIS USED TO ASSERT THAT A LIGHT READER GETS LIGHT, and the site deliberately stopped
    # promising that. The two registers were never equals. The dark one is a place drawn at an
    # hour, with a star field and a horizon; the light one was a fallback, and the atmosphere
    # rendered over cream paper multiplied into a rose stain across the whole page. The owner's
    # first look at the live site was on a light machine and the question was why the background
    # was pink.
    #
    # The assertions below are the decision, so that reinstating the automatic switch means
    # arguing with a gate rather than deleting a comment.
    check("there is one register and the machine does not get a vote",
          "prefers-color-scheme" not in sheet)
    check("...and no second palette to go unlooked at", "data-theme" not in sheet)
    check("...so the site has exactly one ground", sheet.count("--bg:") == 1,
          f"{sheet.count('--bg:')} grounds declared")
    # `re`, not the `_re` the rest of this function uses. That alias is bound further down, which
    # makes it local to the whole function and unusable above its own import line.
    check("a night sky does not print",
          bool(re.search(r'@media print\s*\{\s*\.sky\s*\{\s*display:none', sheet)))

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

    # WHAT ACTUALLY RENDERS, shared by the checks below. Comments are stripped first: a comment
    # draws nothing, and scanning them failed this build once for the comment that lists the
    # kitsch being avoided. Substring matching failed it twice more, for "rope" inside Manrope
    # and "dial" inside radial-gradient, which is why everything below uses word boundaries.
    import re as _re                                                # noqa: PLC0415
    rendered = _re.sub(r"/\*.*?\*/", " ", sheet, flags=_re.DOTALL)

    # A BAR AND NEVER A DIAL, enforced in the one place a ramp would have to be written.
    bar = sheet[sheet.find(".bar {"):sheet.find(".barnote")] if ".bar {" in sheet else ""
    check("the grid watch gauge exists", bool(bar))
    check("the gauge fill has exactly one colour",
          bar.count("background:") == 2, f"{bar.count('background:')} backgrounds in the bar")
    check("no severity variant can be styled on the gauge",
          not any(s in sheet for s in (".fill.warn", ".fill.high", ".fill.crit",
                                       ".bar.warn", ".bar.high", ".bar.crit")))
    # Word boundary, for the third time in this file. `radial-gradient` contains the letters of
    # "dial", so a substring test failed the build the moment the sky introduced a radial. The
    # rule being guarded is about a GAUGE shape, so it looks for the shapes a dial is made of.
    check("the gauge is never a dial",
          not _re.search(r"\bdial\b", rendered, _re.IGNORECASE)
          and "conic-gradient" not in sheet)

    # THE FLAG'S GEOMETRY, and the kitsch it exists instead of. If a future edit reaches for a
    # longhorn or a rope border, this is where the argument was already had.
    check("the mark is the flag's hoist", ".wordmark .hoist" in sheet
          and "var(--flag-blue)" in sheet)
    kitsch = _re.findall(r"\b(longhorn|cowhide|rope|lasso|lariat|boots?|spur|sheriff|saloon|"
                         r"wagon|cactus|armadillo)\b", rendered, _re.IGNORECASE)
    check("no kitsch", not kitsch, str(sorted(set(kitsch))))

    # ---- what a reader waits for ------------------------------------------------
    # THE BUDGET IS THE CONGESTION WINDOW, AND IT IS MEASURED COMPRESSED. Two earlier versions of
    # this gate counted uncompressed source bytes against a hand-raised ceiling, which drifted
    # upward every time the surface grew and so constrained nothing by the end. The quantity that
    # decides whether the page paints in one round trip or two is the COMPRESSED size of the
    # render blocking sheet, and the threshold is a property of TCP rather than of taste.
    #
    # Stripping the comments and moving the grain out took the same stylesheet from 24 KB
    # compressed, comfortably over the window, to about 6 KB. Neither change removed a rule.
    wire = len(gzip.compress(sheet.encode(), 9))
    check("the stylesheet paints in one round trip", wire < INITIAL_CWND,
          f"{wire:,} bytes compressed, window is {INITIAL_CWND:,}")
    # Kept as its own check because the sheet and the texture fail for different reasons and a
    # combined number hides which. The tile is a fixed-size asset, so this is a regression guard
    # rather than a budget: it should not move unless the noise parameters do.
    tile = grain.png()
    check("the texture stays cheap", len(tile) < 14_000, f"{len(tile):,} bytes of tile")
    check("...and it is not inlined into the render blocking sheet",
          "data:image/png" not in sheet and GRAIN_FILE in sheet)

    # The stripping is the one transformation between the annotated source and what ships, so it
    # is checked rather than trusted. A `/*` inside a quoted value is the only way the regex could
    # swallow a declaration, and unbalanced braces are how that would show up.
    full = annotated()
    check("the reasoning survives in the source", len(full) > len(sheet) * 1.3)
    check("stripping comments leaves the rules intact",
          sheet.count("{") == sheet.count("}") == full.count("{") == full.count("}"),
          f"{sheet.count('{')}/{sheet.count('}')} vs {full.count('{')}/{full.count('}')}")
    check("...and no comment marker hides inside a value",
          not _re.search(r'"[^"\n]*/\*', full))
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
