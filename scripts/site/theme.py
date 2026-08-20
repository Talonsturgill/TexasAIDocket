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
  /* The paper side of the palette. `rust` is deliberately NOT here: brand.yaml scopes it
     deck_only and theme's own self-test refuses it in site CSS, which is the right call and
     caught this. The card uses --granite, which brand.yaml scopes with --paper. */
  --paper-rule:{c['paper_rule']};
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
  /* The phone's own bottom furniture, the home indicator strip. The ask box reads this
     when it parks the composer above the fold, so the field never sits under it. Zero
     everywhere that has no such strip. */
  --safe-bottom:env(safe-area-inset-bottom, 0px);
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
   and off-center by design, so something has to contain it. Putting `overflow-x:clip` on
   `body` does contain it and also silently breaks `position:sticky` on everything inside,
   because a clipping ancestor becomes the scroll container the sticky element resolves
   against: the bar detached and rode down the page over the copy. */
html {{ -webkit-text-size-adjust:100%; scroll-behavior:smooth; overflow-x:clip; }}
@media (prefers-reduced-motion:reduce) {{
  html {{ scroll-behavior:auto; }}
  /* ITERATION COUNT IS THE ONE THAT MATTERS. Shortening the duration of an `infinite`
     animation does not stop it, it runs it faster forever, so the sky's eight loops kept
     cycling. `shimmer` animates `background-position` on a full width blurred layer, which is
     not compositable, so every frame repainted and re-blurred it on every page of the site.
     A reader who set reduce-motion asked not to pay that. */
  *,*::before,*::after {{ animation-duration:.01ms!important; animation-iteration-count:1!important;
    transition-duration:.01ms!important; }}
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
/* THE ATMOSPHERE GOES UNDER THE RECORD, and until now it did not.
   `.sky` is a POSITIONED element at z-index 0 and `main` is a static one, and in the painting
   order a positioned box at auto or zero paints after every non-positioned block in the same
   stacking context. So the sky was on top of the copy the whole time. `pointer-events:none`
   hid the consequence from anything that hit tests, which is most of this suite.
   The tumbleweed is what made it visible. It rolls along `top:74vh` measured from the top of
   the DOCUMENT, and on a phone 74vh is 621 pixels down a stacked column, so it crossed the
   front page's own statistics, the record's map and the grid chart's residual strip, on top,
   in the accent colour. Three pages, one cause, and no gate saw any of it: page_ground samples
   points where content is NOT, and text_contrast composites background COLOURS and cannot see
   a drawing laid over a numeral.
   One declaration fixes the class rather than the weed. Content sits above the weather, the
   masthead at 80 and the grain at 90 still sit above content, and nothing needed a new number. */
main, .masthead, footer.site {{ position:relative; z-index:1; }}
.masthead {{ z-index:80; }}

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
  animation:shimmer 27s ease-in-out infinite alternate; }}
.sky .shimmer.s2 {{ filter:blur(30px); opacity:.6; background-size:290% 100%;
  animation-duration:38s; animation-direction:alternate-reverse; }}
@keyframes shimmer {{ from {{ background-position:0% 0; }} to {{ background-position:100% 0; }} }}

/* Dusk cloud, drifting.
   THE PERIODS WERE 38 TO 97 SECONDS AND THE TRAVEL WAS ABOUT 6vw, which is a still image with
   extra steps: the owner looked at the page and could not see any moving layer at all, which is
   the correct verdict on motion nobody can perceive. Motion has to be seen inside the time
   somebody actually spends looking, so the periods are roughly halved and the travel doubled,
   and the clouds scale as they drift, because a cloud that slides at a fixed size reads as a
   sticker being dragged.
   THE COOL PAIR GOT THE BRIGHTNESS AND THE WARM PAIR DID NOT. Warm over this violet ground is
   what made the page pink, and that is a fact about blending rather than about opacity, so the
   warm layers are only faster. The cool ones deepen rather than shift hue, so they can carry the
   visible weight. The rendered check samples the ground and would say so either way. */
/* THE WARM ONES SIT LOW AND THE HIGH ONE IS COOL, which is both the physics and the fix. At
   dusk the lit band is at the HORIZON and the sky overhead has already gone. The first version
   had the warm veils at the top of the page, so ember and gold were screening over the whole
   ground at once, and warm light screened over a violet ground is the definition of mauve. The
   page read pink. Warmth belongs where the sun went. */
.sky .veil {{ position:absolute; border-radius:50%; filter:blur(52px);
  mix-blend-mode:screen; opacity:.34; }}
/* The warm pair sit so their CENTRES clear the fade zone. A blurred ellipse whose middle is
   inside the fade loses most of itself and reads as a smudge rather than as cloud. */
.sky .v1 {{ width:64vw; height:34vh; left:30vw; bottom:calc(var(--sky-fade) + 2vh);
  background:radial-gradient(closest-side,color-mix(in srgb,var(--accent) 34%,transparent),
    transparent 70%); animation:drift1 15s ease-in-out infinite alternate; }}
.sky .v2 {{ width:52vw; height:30vh; left:2vw; bottom:calc(var(--sky-fade) + 6vh);
  background:radial-gradient(closest-side,color-mix(in srgb,var(--accent-deep) 30%,transparent),
    transparent 70%); animation:drift2 19s ease-in-out infinite alternate; }}
/* The one high cloud, and it is cool. A dusk sky is warm at the bottom and cold at the top. */
.sky .v3 {{ width:46vw; height:32vh; left:22vw; top:-12vh; opacity:.26;
  background:radial-gradient(closest-side,color-mix(in srgb,var(--flag-blue) 46%,transparent),
    transparent 70%); animation:drift3 24s ease-in-out infinite alternate; }}

/* THE UPPER SKY HAS TO MOVE TOO, and for a while it did not. Fixing the pink meant pulling every
   warm layer down to the horizon, which was right, and it left the top two thirds of the page as
   near black with a fixed star field on it. Motion only at the very bottom is motion nobody sees,
   so the page read as a still image.
   These are the same slow drift as the warm ones and they are COOL, deliberately. Warm light
   screened over this violet ground is the thing that made mauve, and that is a fact about
   blending rather than about opacity, so turning a warm veil down would only make a slower
   mistake. Violet over violet deepens instead of shifting hue, which is what a real sky does
   overhead at this hour anyway. Long, uneven periods so the two never visibly cycle together. */
.sky .v4, .sky .v5 {{ position:absolute; border-radius:50%; filter:blur(58px);
  mix-blend-mode:screen; }}
/* THE OPACITIES ARE .78 AND .68 BECAUSE THAT IS THE MOST THE NIGHT GROUND WILL CARRY.
   The owner reported the background did not appear to move, and measuring the rendered
   frames rather than the DOM proved it: over fifteen seconds the page changed by a mean of
   2.6 parts in 255, which is about one percent of luminance delivered slowly enough for the
   eye to adapt to it. Transforms were changing the whole time. Nothing was arriving.
   Three levers exist and only two are free. Speed and travel distance cost no brightness, so
   the periods came down by about a third and the translate ranges roughly doubled. Opacity
   costs brightness directly, and brightness is capped by the swept ground ceiling that earns
   the star field. At .9 and .8 the sweep put five points over it, peaking at 8.2 against a
   7.5 limit. At .78 and .68 it holds. These are measured limits, not chosen values, and
   tests/page_ground.mjs is what measures them.
   SMALLER AND BRIGHTER RATHER THAN BIGGER AND BRIGHTER, and the rendered check is what forced
   the distinction. At 78vw these spanned the whole page, so raising their opacity to make the
   motion visible lifted the ground itself: the left gutter measured 10 percent lightness against
   a 7.5 ceiling, and the ceiling is the argument that the star field is earned. A wash that
   covers everything is not a cloud, it is a tint, and tinting the page is not the same as moving
   it. Narrower and brighter reads as something PASSING, which is the thing that was missing. */
.sky .v4 {{ width:44vw; height:38vh; left:14vw; top:4vh; opacity:.78;
  background:radial-gradient(closest-side,color-mix(in srgb,var(--flag-blue) 62%,transparent),
    transparent 72%); animation:drift4 17s ease-in-out infinite alternate; }}
.sky .v5 {{ width:38vw; height:30vh; right:12vw; top:26vh; opacity:.68;
  background:radial-gradient(closest-side,color-mix(in srgb,var(--panel) 88%,transparent),
    transparent 70%); animation:drift5 21s ease-in-out infinite alternate; }}
@keyframes drift4 {{ from {{ transform:translate(-20vw,-6vh) scale(1); }}
  to {{ transform:translate(24vw,10vh) scale(1.34); }} }}
@keyframes drift5 {{ from {{ transform:translate(20vw,8vh) scale(1.26); }}
  to {{ transform:translate(-22vw,-7vh) scale(1); }} }}

/* THE TUMBLEWEED, which is this page's answer to the sibling's meteor. Not another thing in the
   sky. The one piece of West Texas motion everybody already has in their head, and a real plant
   doing the thing it evolved to do: Salsola tragus snaps off at the root when it dries and rolls
   to scatter seed, so the rolling is the organism working. See sky.py for how the skeleton is
   generated.
   IT IS RARE ON PURPOSE. A loop that fires every few seconds is a screensaver. This crosses once
   in fifty seconds, so it is a thing you catch rather than a thing you watch, which is the entire
   trick the meteor is playing. The roll and the travel are one transform, because a tumbleweed
   that slides without turning is a ball and reads as a bug.

   SIZE AND SPEED (owner, 2026-08-12). Bigger, and across a little faster. The speed lives in the
   KEYFRAME PERCENTAGES rather than in the duration, because the fifty second cycle is what makes
   the thing rare and shortening it would trade rarity for speed. Compressing the visible window
   from 30 percent to 22 percent takes the crossing from about fifteen seconds to about eleven and
   leaves the loop alone. The rotation went up with it, since a weed that crosses faster at the
   same spin rate is sliding, and sliding without turning is the bug this whole element avoids.

   THE FIRST CROSSING IS ALMOST IMMEDIATE (owner, 2026-08-12). It used to wait six seconds, and
   rarity and a long cold open are not the same decision. Six seconds is most of the time a reader
   spends on the page before scrolling, so the effect that gives the site its character was one a
   lot of visitors never saw at all. The LOOP stays fifty seconds, which is what makes it rare;
   only the opening wait is cut, so the first one lands while somebody is still looking. */
.sky .tumble {{ position:absolute; top:74vh; left:0; width:clamp(52px,6.2vw,88px);
  aspect-ratio:1; opacity:0; animation:tumble 50s linear infinite; animation-delay:1.2s; }}
.sky .tumble .weed {{ width:100%; height:100%; display:block; }}
.sky .tumble .weed path {{ fill:none; stroke:var(--accent); stroke-width:1.6;
  stroke-linecap:round; opacity:.5; }}
@keyframes tumble {{
  0%   {{ opacity:0; transform:translate(-14vw,0) rotate(0deg); }}
  2%   {{ opacity:.85; }}
  /* The hops. A tumbleweed does not roll along a line, it catches and lifts. */
  6%   {{ transform:translate(6vw,-2.4vh) rotate(230deg); }}
  9%   {{ transform:translate(22vw,0) rotate(470deg); }}
  12%  {{ transform:translate(40vw,-3.2vh) rotate(700deg); }}
  15%  {{ transform:translate(60vw,-.5vh) rotate(960deg); }}
  18%  {{ transform:translate(82vw,-2.8vh) rotate(1200deg); }}
  20%  {{ opacity:.7; }}
  22%  {{ opacity:0; transform:translate(114vw,0) rotate(1450deg); }}
  100% {{ opacity:0; transform:translate(114vw,0) rotate(1450deg); }}
}}
@keyframes drift1 {{ from {{ transform:translate(-24vw,-3vh) scale(1); }}
  to {{ transform:translate(15vw,4vh) scale(1.12); }} }}
@keyframes drift2 {{ from {{ transform:translate(22vw,6vh) scale(1.18); }}
  to {{ transform:translate(-14vw,-3vh) scale(1); }} }}
@keyframes drift3 {{ from {{ transform:translate(-10vw,-2vh) scale(1); }}
  to {{ transform:translate(11vw,5vh) scale(1.16); }} }}

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
/* THE MARK IS THE FLAG, DRAWN TO THE STATUTE. Its proportions are not set here: the viewBox
   carries them, computed in scripts/site/mark.py from Government Code sec. 3100.001, so the only
   decision left to CSS is how large to render it. `height` and `auto` rather than both, because
   fixing both would be overruling the law with a round number. */
.wordmark .lonestar-mark {{ height:1.75em; width:auto; display:block; flex:none;
  border-radius:1.5px; }}
.wordmark .m-blue {{ fill:var(--flag-blue); }}
.wordmark .m-white {{ fill:var(--star); }}
.wordmark .m-red {{ fill:var(--flag-red); }}
.m-star {{ fill:var(--star); }}
/* THE ROTUNDA CUT. The star inlaid in the Capitol floor is set in stone wedges that take the
   light differently either side of each point, and that is the whole difference between a mark
   that reads as an object and one that reads as a sticker. Lit from the upper left, which is
   where every other shadow on this page is lit from. The wedges sit ON the solid star, so a
   renderer that drops them loses the facets and keeps the mark. */
.f-lit {{ fill:#FFFFFF; opacity:.55; }}
.f-shade {{ fill:var(--flag-blue); opacity:.14; }}
nav.main {{ display:flex; gap:1.1rem; flex-wrap:wrap; margin-left:auto;
  font-size:var(--s-1); letter-spacing:.03em; text-transform:uppercase; }}
/* The underline WIPES IN from the left rather than switching on. It is two properties and a
   transition, and it is most of the difference between a nav that responds and a nav that
   toggles. */
/* WCAG 2.5.8 asks 24 by 24 CSS pixels of any control that is not inline in a sentence, and
   a navigation link is not inline in a sentence. The vertical padding already cleared it and the
   WIDTH did not: "Ask" measured 21 by 26 on a phone. `min-width` needs a block box to apply to,
   which is why the display changes with it. */
nav.main a {{ color:var(--ink-mute); text-decoration:none; padding-block:.35em;
  display:inline-block; min-width:24px; text-align:center; position:relative; }}
nav.main a::after {{ content:""; position:absolute; left:0; right:100%; bottom:0; height:1.5px;
  background:var(--accent); transition:right .25s ease; }}
nav.main a:hover {{ color:var(--ink-bright); }}
nav.main a:hover::after {{ right:0; }}
nav.main a[aria-current] {{ color:var(--accent); }}
nav.main a[aria-current]::after {{ right:0; }}
/* ON A NARROW SCREEN THE MASTHEAD LETS GO. Nine sections wrap to two rows, and stuck to the top
   that is a third of the viewport permanently spent on navigation. It scrolls away instead, and
   the skip link above it is what a keyboard reader uses to get past it either way.
   THE BREAKPOINT IS MEASURED, AND IT USED TO BE GUESSED. At 46rem the bar was 692 pixels wide and
   the nav alone measures 553, so from about 740 to 800 pixels the nav had already wrapped to a
   second row while the desktop rules still applied: it stayed right-aligned, leaving a hole under
   the wordmark, and the Lone Star came back on and sat directly behind the word SERVICES. That
   band is exactly half of a laptop screen, which is where the owner found it.
   The number now comes from the content rather than from a round figure. The nav needs 553, the
   wordmark 205, and a gap that reads as a gap is about 48, so 806 of content. The shell's gutter
   is 28 a side, so 862 of viewport. 56rem is 896, which leaves headroom for the moment a web font
   swaps in and every label gets fractionally wider. */
@media (max-width:56rem) {{
  .masthead {{ position:static; }}
  .masthead::before {{ display:none; }}
  .masthead .wrap {{ gap:.6rem; }}
  nav.main {{ margin-left:0; gap:.5rem .9rem; font-size:var(--s-2); }}
}}

/* ---- ON A PHONE THE NAV IS ONE ROW THAT SCROLLS ------------------------- */
/* WHAT THE OWNER SAW: a phone screenshot of the about page whose whole first screen was a
   wordmark, a nav, and then a field of stars, with the headline pushed off the bottom. Three
   measured things were adding up, and none of them looked wrong on its own.
   The nav wrapped. Eight labels need 327 pixels of text and the seven gaps between them add
   123 more, so at 412 the row broke and left ABOUT alone on a second line under seven
   siblings. A one-item second row does not read as a navigation, it reads as a rendering
   fault, which is very close to what was reported: tabs missing.
   That second row also cost 34 pixels of masthead, and the hero was already spending
   `9vh` above its headline, which is 82 on a tall phone. Add the shell's own top padding and
   the reader met 309 pixels of nothing before the first word. On a 915 pixel screen that is a
   quarter of the phone gone before the page says anything.
   THE BREAKPOINT IS MEASURED, not chosen, and the first measurement was wrong in a way worth
   keeping. Stepping the viewport FOUR pixels at a time said the bar holds one row down to 460,
   so the rule ended at 28.75rem. Stepping ONE pixel at a time finds the bar taking a second row
   at 461 and 462, holding only "About", which is the exact one-item second row described below.
   A four pixel step cannot find a two pixel band. The rule now ends at 29rem and 29rem is that number, and it is the
   same one the Lone Star's own rules turn on, because it is the same event.
   A SCROLLING ROW RATHER THAN A MENU BUTTON. Every section stays visible and reachable with a
   thumb, and nothing is hidden behind a control a reader has to discover. The row bleeds to
   both screen edges, because a strip that stops inside the gutter looks like it ends there. */
@media (max-width:28.9999rem) {{
  nav.main {{ flex-wrap:nowrap; overflow-x:auto; overscroll-behavior-x:contain;
    -webkit-overflow-scrolling:touch; scrollbar-width:none; -ms-overflow-style:none;
    margin-inline:calc(var(--gap) * -1); padding-inline:var(--gap); }}
/* NO EDGE FADE, AND THAT IS THE SECOND ANSWER TO THE QUESTION. The first was a mask that
   dissolved the last 2.4rem of the row, which reads well while the row overflows and is a
   defect the moment it does not: near the top of this range the eight labels fit, and the mask
   went on dimming a link that was entirely visible. A mask cannot ask whether there is
   anything to scroll to. What can answer that is the row itself: it bleeds to both screen
   edges, so when there is more, the next label is visibly cut by the edge of the phone, and
   when there is not, nothing is cut and nothing is dimmed. The affordance is the overflow. */
  nav.main::-webkit-scrollbar {{ display:none; }}
  /* Without this the links shrink to fit instead of overflowing, and the row silently becomes
     eight squeezed columns rather than a strip that scrolls. */
  nav.main a {{ flex:none; }}
}}
/* The spacing half of the same fix is NOT here, it is below `.hero` and `main`, and that is
   deliberate rather than untidy. It lived in this block first and did nothing: `.hero` and
   this rule both weigh 0-0-1-0, `.hero` is declared 90 lines further down, and at equal
   specificity the later declaration wins no matter which one sits inside a media query. The
   computed padding stayed at 82.35 pixels while the stylesheet read as fixed. */

/* THE MARK COMES OFF WHERE THE NAV ACTUALLY WRAPS, AND NOT 376 PIXELS EARLIER.
   This rule lived at `max-width:56rem` and justified itself in a comment: "the nav wraps to
   two rows at this width and the hero starts right under it, so there is no clear field left
   to put a star in". Every word of that is true at the width it was written for and false
   across most of the range it was applied to. Measured by stepping the viewport ten pixels at
   a time and counting the distinct top offsets of the nav links, the bar holds ONE row down to
   520px. So the mark was being deleted through 600, 700, 800 and 896 pixels of perfectly clear
   sky, which is the width most laptops open a window at.
   The breakpoint is the measurement now, rounded down to the nearest whole rem, and it is
   re-measured by tests/responsive.mjs rather than reasoned about again.
   WRITTEN AS `.home .sky` TO MATCH THE RULE IT OVERRIDES. The first version said
   `.sky .lonestar`, one class less specific than the `.home .sky .lonestar` that turns the mark
   on, and specificity beats both source order and being inside a media query, so the mark
   stayed on every phone with its glow sitting in the wrapped navigation. */
/* AND ON A PHONE IT MOVES DOWN INSTEAD OF BEING DELETED.
   This rule used to be `display:none`, and the justification above is the tell: the mark was
   removed because its glow sat in the wrapped navigation. That is a POSITION problem, and the
   answer to a position problem is a position. Deleting the one piece of brand furniture on the
   page, on the majority of the traffic, to avoid moving it eighty pixels is not a trade.
   MEASURED RATHER THAN GUESSED. With the mark forced on and every box compared, it never
   touches the headline or the telemetry strip at any width from 280 to 480px. The nav is the
   only thing it ever met, and the nav is two rows deep below about 450px, ending at 117px.
   So the mark clears it and sits in the band between the navigation and the strip.
   TWO RANGES, BECAUSE THE NAV HAS TWO STATES AND THE BAND MOVES WITH IT. Stepping the
   viewport a pixel at a time, the bar is two rows up to 459px and one row from 460px, which
   is 28.75rem. Below it the band runs 117 to 236; above it, 82 to 199. One rule spanning both
   put the mark through the telemetry strip at 480px, which is how this fix failed its own
   measurement the first time it was written.
   IN REM RATHER THAN PX, and that is load bearing. The wrap point is a property of how wide
   the nav text is, so it moves with the reader's font size. A px breakpoint would hold the
   mark in the two-row position on a phone whose nav had already collapsed to one. */
/* ONE BAND NOW, WHERE THERE WERE TWO, because the thing that split them is gone. The pair
   above existed to track a masthead that was two rows on a phone and one row just above it,
   and the nav is a single scrolling row at every width now. Keeping two rules meant keeping
   two numbers for one event, and they promptly disagreed at their own boundary: at 460 the
   hero rule read narrow and the mark rule read wide, and the mark landed on the telemetry
   strip in the eleven pixel band between them. That band was the scrollbar.
   THE PLACE IS THE ONE THE NAV VACATED. Tightening the bar to a single row opened 65 pixels
   between the masthead at 97 and the telemetry strip at 162, and it is the same 65 pixels at
   every width down to 300 because both edges are set by content rather than by proportion. A
   54 pixel mark sits in it with eight to spare, which is why it is small here and not because
   small looks better: it is the size the clear field is. */
@media (max-width:37.5rem) {{
  .home .sky .lonestar {{ top:6.3rem; right:5vw; width:min(16vw,54px); }}
}}
/* AND THE TELEMETRY PILL STOPS RUNNING UNDER IT. Measured with the mark forced on and its box
   compared against the hero's, the mark never touches the headline at any width down to 360px.
   The only thing it ever met was this strip, between about 640 and 800 pixels, where the pill
   is long enough to reach the right gutter. Capping the strip is a smaller change than deleting
   a mark, and it is the change that matches what was actually wrong. */
@media (min-width:30.01rem) and (max-width:56rem) {{
  .home .hero .tele {{ max-width:74%; }}
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
   page feel alive rather than published. Texas has no daylight story, so this one counts
   hundred degree days against what a normal year holds by the same date, and freezing nights
   through the winter. Computed, dated, and never a forecast. */
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
/* THE PILL LOSES A LINE ON A PHONE BY GIVING UP TRACKING IT DOES NOT NEED. Three segments of
   mono caps at .13em wrapped onto a third line carrying one word. Measured at 390px: .13em is
   78px tall, .10em and below is 58px. Tracking is what makes small caps readable, so this
   gives up the least that buys the line back rather than shrinking the type. Below about
   370px it wraps to three again, which is correct. The text is simply longer than that screen.

   THIS RULE LIVES HERE AND NOT WITH THE OTHER NARROW-SCREEN RULES ABOVE, and the reason is
   the whole lesson. Written into the `max-width:30rem` block further up the sheet it was
   perfectly correct CSS, matched the right element at the right width, and did nothing at
   all, because a media query carries no extra specificity and that block sits ABOVE the
   `.tele` rule it was meant to override. Same specificity, earlier in the source, silently
   loses. It read as fixed and measured as unchanged. */
@media (max-width:30rem) {{
  .tele {{ letter-spacing:.095em; }}
}}

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
/* AN ITEM PAGE'S SECTIONS WERE SPACED BY ACCIDENT, and the accident held for as long as every
   section happened to end in a paragraph. They sit inside `<article>`, so the rule above has
   never matched one of them, and their computed top margin is zero on all 61 pages. What
   separated them was the trailing paragraph's own bottom margin, borrowed. The moment a
   section ended in a table the next heading landed against it, which is what "The evidence"
   has been doing under the Dates table all along and what the movement log made impossible to
   keep missing. Spacing that depends on the shape of the last child is not spacing.
   NOT `var(--band)`. That token is the full page band and would re-space every item page well
   past what the paragraph was giving, which is a redesign rather than a repair. This matches
   `.asksection`, already in this sheet, and collapses with the paragraph margin it replaces. */
article > section {{ margin-top:2.25rem; }}
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
/* THE OTHER HALF OF THE PHONE FIX, and it has to live below both `.hero` and `main` to have any
   effect at all. Three separate openings were stacking on a phone: 54.9 pixels from `main`,
   26.4 of margin on the hero, and 82.35 of `9vh` padding inside it, so 164 pixels of nothing
   sat between a 97 pixel masthead and the first word. `6vh` and `9vh` are proportions of the
   window, which is the right instinct on a laptop and the wrong one on a phone, where the
   window is tall, narrow, and already carrying a masthead that a desktop hides. */
@media (max-width:28.9999rem) {{
  main {{ padding-top:1.5rem; }}
  .hero {{ padding-top:1.2rem; }}
}}
/* THE SECTION MARK. A hairline across the top of every section heading with a short accent
   tick sitting on it, which is the rhythm the whole page is built on.
   `.startsay > h2` is named because that heading is one level deeper than the rest. The
   selector was `main > section > h2` alone, and the moment the services form went to two
   columns its heading stopped being a direct child, silently lost its rule and its tick, and
   that section stopped matching every other section on the page. Nothing failed. It just
   looked wrong, which is the kind of regression only a screenshot catches. */
main > section > h2 {{ position:relative;
  padding-top:1.1rem; border-top:var(--hair) solid var(--rule); }}
main > section > h2::after {{ content:""; position:absolute;
  top:-1px; left:0; width:3.5rem; border-top:2px solid var(--accent); }}
/* THE TWO COLUMN SECTION WEARS THE MARK ITSELF. Its heading sits inside the left column, so
   hanging the rule on the heading drew it a fifth of the way across and stopped, which is the
   one section on the site whose rule did not reach. The grid carries it instead and the rule
   spans both columns like every other one. */
.startgrid {{ position:relative; padding-top:1.1rem;
  border-top:var(--hair) solid var(--rule); }}
.startgrid::before {{ content:""; position:absolute; top:-1px; left:0; width:3.5rem;
  border-top:2px solid var(--accent); }}

/* ---- the map ------------------------------------------------------------ */
/* A SURVEY, NOT AN INFOGRAPHIC. Hairline mesh at one weight, a lit county at one intensity,
   and a scale bar computed from the projection rather than drawn to look about right. No
   severity ramp, because a ramp implies a judgement this page does not get to publish. */
/* THE SHEET IS CAPPED. The map is 1000 by 900, so at full container width it stood taller than
   a laptop viewport and the record it illustrates started below the fold. Capping the WIDTH by
   the height budget keeps the aspect exact and lets the sheet be a figure on the page rather
   than the page. 1000/900 of 72vh is 80vh. */
/* TOUCH-ACTION IS THE DECLARATIVE HALF, and it was missing entirely. The pinch handler
   suppresses the browser's own page zoom with `preventDefault` inside a non-passive touchmove,
   which Chromium honours and which is why the gesture suite is green. iOS Safari drives pinch
   through `gesturestart`/`gesturechange` and does not reliably let a touchmove cancel a zoom
   already under way, so an iPhone reader pinching the map could zoom the whole page instead.
   `touch-action:none` tells both engines the element handles its own gestures. */
.txmap {{ touch-action:none; width:100%; max-width:min(100%,80vh); height:auto; display:block;
  margin-inline:auto; }}
/* THE INSET, for a page whose subject is one place rather than the state. On a metro page the
   map's job is to answer "where in Texas is this", which is orientation and takes a glance. At
   the full size it answered that question with 900 pixels of unlit Texas, and the one item the
   page exists to show sat below the fold underneath it. Same drawing, one third the height. */
.txmap.inset {{ max-width:min(100%,42vh); }}
/* AND THE SURVEY FURNITURE COMES OFF WITH THE SIZE. The graticule labels and the scale bar are
   sized in the SVG's own units, so shrinking the sheet shrinks them to about seven pixels,
   which is furniture a reader can see is there and cannot read. The rule already exists for
   phones one media query below and it is the same judgement: this drawing is being glanced at
   rather than measured. */
.txmap.inset .survey {{ display:none; }}
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
/* WCAG 2.5.8 ON A SHAPE THAT CANNOT BE GIVEN A MINIMUM SIZE, AND WHAT IS HONESTLY DONE
   ABOUT IT. The record page invites a reader to click a lit county. Borden measures 12.7 by
   12.9 on a phone and 9 by 9 at 320px, and a county is a fixed shape on a map, so `min-width`
   has nothing to act on and no amount of CSS makes Borden 24 pixels wide without lying about
   where Borden is.
   TWO THINGS ARE DONE INSTEAD. A touch pointer gets a heavier outline, which is hit tested
   along with the fill and so genuinely enlarges the target, and reads as a deliberate emphasis
   rather than a hack. And the same page carries the county TABLE, every county as a full width
   text link, which is the equivalent control the success criterion asks for and the route that
   actually works on a phone. The map is the overview; the table is the control. Claiming the
   map alone is compliant would be the kind of green check this project keeps a file about. */
@media (pointer:coarse) {{
  .txmap a .c.on {{ stroke-width:3; }}
  /* A drag across the map must not start selecting the labels under it. */
  .txmap {{ -webkit-user-select:none; user-select:none; }}
}}
/* ---- the map under a thumb ---------------------------------------------- */
/* On a laptop the map answers "what is this county" on hover. A phone has no hover, so the
   only way to ask was to commit to a county, load its page, come back, and commit to the next
   one. That is not looking around, it is a survey taken one page load at a time.
   Both of these exist only where there is a thumb. A readout that never fills is a line of
   empty furniture under the drawing, so it is hidden wherever hover already answers. */
.mapread {{ min-height:1.5em; margin:.55rem 0 0; font-family:var(--mono);
  font-size:var(--s-1); color:var(--ink-mute); }}
.mapread:empty {{ min-height:0; margin:0; }}
/* THE WAY BACK OUT. A map that zooms and cannot be reset is a map a reader can get lost in,
   and the gesture that would undo it is the one they just used to get here. Hidden until the
   view has actually moved, because a control that does nothing is furniture. */
.mapreset {{ margin:.5rem 0 0; padding:.5em 1em; border-radius:999px; cursor:pointer;
  font-family:var(--mono); font-size:var(--s-2); letter-spacing:.08em;
  text-transform:uppercase; background:var(--accent-deep); color:var(--on-accent);
  border:var(--hair) solid transparent; }}
.mapreset[hidden] {{ display:none; }}
/* KEYED OFF WHETHER A TOUCH EXISTS, not off the primary pointer. `(hover:hover) and
   (pointer:fine)` describes the mouse a device leads with, while the gesture layer turns on
   for any device with `ontouchstart`. A touchscreen laptop, a Surface or an iPad with a
   trackpad matched both: pinch to the 8x cap worked and the way back was `display:none`,
   leaving a page reload. `any-pointer:coarse` asks the question the gesture actually asks. */
@media (hover:hover) and (pointer:fine) and (any-pointer:coarse) {{
  .mapread, .mapreset {{ display:revert; }}
}}
@media (hover:hover) and (pointer:fine) {{ .mapread, .mapreset {{ display:none; }} }}
@media (any-pointer:coarse) {{ .mapread {{ display:block; }} }}
/* THE HIGHLIGHT IS A STROKE AND NOT A FILL, so a lit county goes on saying it is lit while the
   thumb is on it. Swapping the fill would answer "where is my finger" by deleting the answer to
   "what does the record hold here", and the second question is the one the map is for. */
.txmap .c.under {{ stroke:var(--accent); stroke-width:2.5; paint-order:stroke; }}
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
/* DISPLAY, NOT FONT SIZE, and this rule did nothing for as long as it existed. It set
   `font-size` on the `<g class="survey">` wrapper while every `<text>` inside carries
   `class="lab"` and takes 11px from `.txmap .lab` directly. An own declaration beats an
   inherited one, so the label kept its 11 units and rendered at 3.94 CSS pixels on a 390 wide
   phone: exactly the smudge the comment above claims to have cured. `texas_map.py` also tells
   a screen reader the scale bar is not announced because "the stylesheet hides the whole
   survey layer below 34rem", which was describing behaviour that never happened.
   Hiding it is what the comment, the aria text and the design all already said. */
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

/* ---- the open data list -------------------------------------------------- */
/* Filename first in mono, then what is in it. A bare bulleted list of four links reads as an
   afterthought; the point of this page is that the files ARE the record, so the names carry
   the weight and the description follows in body type. */
.filelist {{ list-style:none; padding:0; margin:1.4rem 0 0; display:grid; gap:.75rem; }}
.filelist li {{ display:flex; flex-wrap:wrap; gap:.2rem .8rem; align-items:baseline;
  padding-bottom:.75rem; border-bottom:var(--hair) solid var(--rule); color:var(--ink-dim); }}
.filelist li:last-child {{ border-bottom:0; padding-bottom:0; }}
.filelist a {{ font-family:var(--mono); font-size:var(--s-1); letter-spacing:.02em;
  color:var(--accent); text-decoration:none;
  border-bottom:var(--hair) solid color-mix(in srgb,var(--accent) 40%,transparent); }}
.filelist a:hover {{ color:var(--ink-bright); border-bottom-color:currentColor; }}

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
  /* A COLUMN RESERVED FOR SOMETHING 54 OF 58 CARDS DO NOT HAVE.
     The countdown only renders for an item with a dated comment window, and `clock()` returns
     an empty string otherwise, so the element is genuinely absent rather than empty. The grid
     went on holding 13.5rem for it anyway, which put a fifth of every card on the record and
     every topic page into white space, and it read as the same dead space the phone had.
     `:has()` asks the card whether it actually has a clock. Where it is unsupported the rule
     does not match and the layout is exactly what it was, so this cannot make anything worse. */
  .items > li:not(:has(.clock)) {{ grid-template-columns:minmax(0,1fr);
    grid-template-areas:"title" "meta"; }}
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

/* ---- the topic row: the record's own filter ----------------------------- */
/* This was five `.tag` boxes carrying the raw slug, which is what a database export looks
   like rather than a record. `.tag` is right where it is used, on a date or a kind marker
   beside a headline, and wrong as the primary way into the record, so this is its own class
   instead of a widening of that one. Three things changed and each does work.
   THE LABEL IS ENGLISH. `DEFENSE-AND-FEDERAL` is the filing name and the reader never asked
   for it. The slug stays the identifier in the URL, the ledger and the ask vocabulary.
   THE COUNT IS ON THE CHIP. Five identical boxes assert five equal beats, and this record is
   not shaped like that: one topic can hold half the decisions and another can hold one. The
   reader deciding where to look is asking exactly that, so the row answers before the click.
   THE GEOMETRY IS A PILL, the same 999px the ask box's suggestion chips use, so the two
   control rows on this site read as one family. */
/* THE COVERS GRID, on /topic/ and on the front page.

   DENSER THAN THE CARD WALL IT REPLACES AND CARRYING MORE. The reference version of this is a
   wall of full width cards, which spends most of a screen on eight facts. `auto-fit` with a
   floor lets it run three across on a desktop, two on a tablet and one on a phone without a
   breakpoint, and the card is a text block rather than a box, so the beats read as a list a
   reader scans rather than eight things competing for a click.

   THE RULE IS ON THE LEFT, NOT AROUND. A border on four sides makes eight boxes; a hairline on
   the leading edge groups them as one structure and costs no vertical space, which is the
   whole point of this being denser than what it is modelled on. */
.covers {{ list-style:none; margin:1.3rem 0 2rem; padding:0; display:grid; gap:1.15rem 1.6rem;
  grid-template-columns:repeat(auto-fit,minmax(17rem,1fr)); }}
.covers .cv-card {{ padding:0 0 0 .95rem; border-left:var(--hair) solid var(--rule-strong); }}
.covers .cv-card a {{ text-decoration:none; color:inherit; }}
.covers .cv-card h2, .covers .cv-card h3 {{ margin:0; font-size:var(--s0); line-height:1.2; }}
@media (hover:hover) {{
  .covers .cv-card a:hover h2, .covers .cv-card a:hover h3 {{ color:var(--ink-bright); }}
}}
.covers .cv-blurb {{ margin:.3rem 0 .45rem; font-size:var(--s-1); line-height:1.45;
  color:var(--ink-quiet); }}
/* The count and the open flag on one baseline, in mono, because every other figure on this
   site is set in mono and a count that changes typeface between surfaces reads as a different
   kind of number. */
.covers .cv-foot {{ margin:0; font-family:var(--mono); font-size:var(--s-2);
  letter-spacing:.04em; color:var(--ink-quiet); display:flex; flex-wrap:wrap; gap:.55rem; }}
/* OPEN IS THE ONE THING ON THIS CARD A READER CAN ACT ON, so it is the one thing that carries
   the accent. It is absent rather than zero when nothing is open, because "0 open" is a true
   sentence that reads as a dead beat. */
.covers .cv-open {{ color:var(--accent); }}
.covers .cv-open::before {{ content:"·"; margin-right:.55rem; color:var(--ink-quiet); }}
/* On the front page the grid sits among full width sections, so it gets a little more air
   above it and a smaller floor, which lets it run four across on a wide screen. */
.covers.front {{ grid-template-columns:repeat(auto-fit,minmax(15rem,1fr)); }}

.topicrow {{ display:flex; flex-wrap:wrap; gap:.5rem; margin:1.3rem 0 2rem; }}
.topicchip {{ display:inline-flex; align-items:center; gap:.55rem;
  padding:.42rem .5rem .42rem .95rem; border-radius:999px; text-decoration:none;
  color:var(--ink); font:400 var(--s-1)/1.15 var(--body);
  border:var(--hair) solid var(--rule-strong);
  background:color-mix(in srgb,var(--surface) 72%,transparent);
  transition:border-color .18s ease, background-color .18s ease, color .18s ease,
    transform .18s ease; }}
/* The count sits in its own well so it reads as a quantity and not as part of the name.
   Mono, because it is a figure, and every other figure on this site is set in mono. */
.topicchip .tc-n {{ font-family:var(--mono); font-size:var(--s-2); line-height:1;
  color:var(--ink-mute); min-width:1.55em; padding:.34em .48em; border-radius:999px;
  text-align:center; background:color-mix(in srgb,var(--ink) 9%,transparent);
  transition:background-color .18s ease, color .18s ease; }}
/* HOVER GUARDED, because on a phone `:hover` latches on after a tap and leaves the chip a
   reader just left looking like the one they are on. */
@media (hover:hover) {{
  .topicchip:hover {{ color:var(--ink-bright); transform:translateY(-1px);
    border-color:color-mix(in srgb,var(--accent) 62%,transparent);
    background:color-mix(in srgb,var(--surface) 96%,transparent); }}
  .topicchip:hover .tc-n {{ color:var(--ink-bright);
    background:color-mix(in srgb,var(--accent) 24%,transparent); }}
}}
/* THE CURRENT TOPIC IS A FILLED CHIP, not an underline. This row repeats on every topic page
   so a reader can cross from one beat to the next without going back through the record, and
   the one they are standing on has to be readable at a glance. */
.topicchip[aria-current] {{ color:var(--on-accent); border-color:transparent;
  background:var(--accent-deep); }}
/* THE WELL LIGHTENS HERE AND DARKENS ON EVERY OTHER CHIP, and that inversion is the whole
   point rather than an inconsistency. An ordinary chip is light text on a dark ground, so a
   lighter well would eat its contrast. This one is `--on-accent`, which is DARK ink on the
   ember, so the well has to go the other way. The first version mixed black in on both, which
   read fine on the four dark chips and dropped this numeral to 2.93 against its own well. */
.topicchip[aria-current] .tc-n {{ color:var(--on-accent);
  background:color-mix(in srgb,#fff 34%,transparent); }}

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

/* ---- the answered questions --------------------------------------------- */
/* THE QUESTION IS THE HEADING AND THE ANSWER IS THE PARAGRAPH, which is the whole layout. A
   reader scanning for one of these is scanning the questions, so they get the type size and
   the answer does not compete with them. The mono kicker above each answer is what the
   question-hub pages call this kind of question, so a reader who follows one of those links
   lands on a page using the same words. */
.qa {{ margin:1.4rem 0; }}
.qa h3 {{ font-size:var(--s0); line-height:1.3; margin:0; }}
.qa h3 a {{ text-decoration:none; border-bottom:var(--hair) solid var(--rule); }}
.qa h3 a:hover {{ color:var(--ink-bright); border-bottom-color:var(--accent); }}
.qa p {{ margin:.35rem 0 0; max-width:38rem; }}

/* ---- the source archive's stat line -------------------------------------- */
/* FOUR FIGURES IN A ROW, each with its own label, reading as a meter rather than a sentence.
   The figure leads and the word follows it, because the eye is scanning the numbers down the
   page and the words only matter once it stops. */
/* THE GAP BETWEEN PAIRS HAS TO BEAT THE GAP INSIDE ONE, or "25 CLAIMS 3 PRIMARY" reads as four
   loose tokens and the eye has to pair them by meaning. Mono type at a wide letter-spacing
   already carries air inside every word, so the column gap is set well clear of it. */
p.srcstat {{ display:flex; flex-wrap:wrap; gap:.35rem 1.9rem; margin:.35rem 0 1.6rem;
  font-family:var(--mono); font-size:var(--s-2); letter-spacing:.05em;
  text-transform:uppercase; color:var(--ink-mute); }}
p.srcstat .st {{ white-space:nowrap; }}
p.srcstat .num {{ color:var(--ink); margin-right:.3rem; }}

/* The ranked hub. A numbered list would print a rank beside each publisher, which is a figure
   nothing computed and a claim the page is not making. The order carries the ranking. */
ol.srclist {{ list-style:none; margin:1.4rem 0 0; padding:0; }}
ol.srclist > li {{ padding:.9rem 0; border-top:var(--hair) solid var(--rule); }}
ol.srclist > li:last-child {{ border-bottom:var(--hair) solid var(--rule); }}
ol.srclist h2 {{ font-size:var(--s0); margin:0; }}
ol.srclist h2 a {{ text-decoration:none; border-bottom:var(--hair) solid var(--rule); }}
ol.srclist h2 a:hover {{ color:var(--ink-bright); border-bottom-color:var(--accent); }}
/* The stat line's clearance is for the heading that follows it on a publisher's own page. In
   a hub row the row's own padding is the separation, so the extra would just be a gap. */
ol.srclist p.srcstat {{ margin-bottom:0; }}

/* ---- cite this ----------------------------------------------------------- */
/* ONE LINE A READER CAN SELECT WHOLE. It is set in the mono face because it is a record to be
   copied rather than prose to be read, and the box exists so a triple click takes the whole
   citation and nothing either side of it. */
p.cite {{ font-family:var(--mono); font-size:var(--s-1); line-height:1.65;
  padding:.9rem 1rem; border:var(--hair) solid var(--rule); border-radius:2px;
  color:var(--ink); overflow-wrap:anywhere; }}

/* ---- the timeline: where this decision sits relative to now -------------- */
/* A SPINE WITH STATIONS, and today is one of them. The point of the strip is that a reader
   can see whether the thing has happened without reading a word, so the marker for now has
   to sit IN the sequence rather than beside it. Everything above it is done and everything
   below it is not.
   The past is dimmed and the future is not. That is the only severity this strip carries,
   and it encodes a fact about the calendar rather than a judgement about the decision. */
ol.tl {{ list-style:none; margin:1rem 0 0; padding:0; position:relative; }}
ol.tl::before {{ content:""; position:absolute; left:.3rem; top:.55rem; bottom:.55rem;
  border-left:var(--hair) solid var(--rule); }}
ol.tl > li {{ position:relative; padding:0 0 1.1rem 1.6rem; }}
ol.tl > li:last-child {{ padding-bottom:0; }}
ol.tl > li > .dot {{ position:absolute; left:0; top:.42rem; width:.65rem; height:.65rem;
  border-radius:50%; border:2px solid var(--rule-strong); background:var(--bg); }}
ol.tl > li time {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.06em;
  color:var(--ink-mute); margin-right:.6rem; }}
ol.tl > li > .lbl {{ font-size:var(--s-1); color:var(--ink); }}
ol.tl > li > p {{ margin:.2rem 0 0; font-size:var(--s-1); line-height:1.55;
  color:var(--ink-mute); max-width:34rem; }}
/* THE PAST IS QUIETER, NOT GREYED OUT. A date that has passed is still evidence and a reader
   still reads it, so this is a step down in emphasis rather than a disabled state. */
ol.tl > li.past {{ opacity:.72; }}
/* TODAY. The one filled marker on the strip, in the accent, with no date beside it because
   the reader supplies that. */
ol.tl > li.now {{ padding-bottom:1.1rem; }}
ol.tl > li.now > .dot {{ background:var(--accent); border-color:var(--accent); }}
ol.tl > li.now > .lbl {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.1em;
  text-transform:uppercase; color:var(--accent); }}
/* THE NEXT DATE IS THE ONE THEY CAME FOR. A count, on its own line, in the mono face the rest
   of the site uses for a figure. It is not red and it is not a badge, because a date being
   near is not an alarm. */
ol.tl > li > .out {{ display:block; margin-top:.2rem; font-family:var(--mono);
  font-size:var(--s-2); letter-spacing:.04em; color:var(--ink-mute); }}
ol.tl > li.ahead > .dot {{ border-color:var(--ink-mute); }}

/* ---- the movement log: a decision being watched -------------------------- */
/* THE LIST MARKER IS SUPPRESSED ON PURPOSE. This is an `ol` because the order is the
   meaning, oldest first, so the markup has to say ordered. What it must not do is PRINT
   a counter beside each line, because a reader arriving at "3." next to a date reads a
   figure about the decision rather than a position in a list. The date is the marker.
   It also keeps the one rule this project will not bend on: every numeral a reader sees
   was computed from data, and a CSS counter is a number the build never computed.
   The rule down the left is the same device the claims block uses, for the same reason.
   These are observations of the record, and they hang off one spine. */
ol.moved {{ list-style:none; margin:1rem 0 0; padding:0 0 0 1rem;
  border-left:2px solid var(--rule-strong); }}
ol.moved > li {{ margin:0 0 1rem; }}
ol.moved > li:last-child {{ margin-bottom:0; }}
ol.moved > li > .num {{ display:block; font-size:var(--s-2); letter-spacing:.04em;
  color:var(--ink-mute); }}
ol.moved > li > p {{ margin:.15rem 0 0; font-size:var(--s-1); line-height:1.6;
  color:var(--ink); max-width:34rem; }}

/* Mid-century oil charts: heavy rules top and bottom, hairlines between. The weight tells a
   reader where the table starts and stops without a box around it. */
table {{ border-collapse:collapse; width:100%; font-size:var(--s-1);
  border-top:2px solid var(--rule-strong); border-bottom:2px solid var(--rule-strong); }}
/* A TABLE THAT CANNOT FIT SCROLLS ITSELF, rather than pushing the page sideways. The water
   page's figures table wants 364 pixels of columns and a 375 pixel phone offers about 325 of
   content, so it hung over the edge and took the whole document with it. `display:block` makes
   the table its own scroll box while its rows keep laying out as a table, which is the one
   change here that needs no markup. The caption stays put because it is not a column. */
@media (max-width:34rem) {{
  table {{ display:block; overflow-x:auto; }}
  table caption {{ position:sticky; left:0; }}
}}
th,td {{ text-align:left; padding:.5em .75em; border-bottom:var(--hair) solid var(--rule);
  vertical-align:top; }}
tr:last-child td {{ border-bottom:0; }}
th {{ font-weight:600; color:var(--ink-mute); font-size:var(--s-2); letter-spacing:.04em;
  text-transform:uppercase; border-bottom:var(--hair) solid var(--rule-strong); }}
td.n,th.n {{ text-align:right; }}
/* A NUMBER COLUMN IS AS WIDE AS THE NUMBER, and no wider. A two column table at full page
   width strands its figure a thousand pixels from the label it belongs to, and a reader has
   to track across empty space to pair them, which is the exact job a table is supposed to do
   for you. The first column takes the slack instead. `min-content` on a right aligned numeric
   cell is the width of its longest number plus the padding, so the columns stay aligned with
   each other and stop being a gulf. */
table.tally td.n,table.tally th.n {{ width:1%; white-space:nowrap; }}
table.tally td:first-child,table.tally th:first-child {{ width:99%; }}
/* A TWO COLUMN TALLY NARROWS THE TABLE INSTEAD OF THE COLUMN. With only a label and a count
   there is no third column to absorb the slack, so giving the label 99% just moves the gulf
   rather than closing it. Capping the table at a readable measure is the only thing that puts
   the number back beside the thing it counts. */
table.tally.pair {{ max-width:32rem; }}

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
/* A VERTICAL FADE, NOT A SEVERITY RAMP. The grid watch's no-ramp rule governs the capacity
   gauge, where a colour change would imply a red zone this page does not get to publish.
   Nothing here encodes value in colour: the fade separates the filled day from the ground
   under it, and the stroke on top carries the reading. Sixty percent of that fill sits below
   the trough on a normal day, and as a flat slab it read as a placeholder. */
/* NO `fill` HERE. The gradient is defined inside the chart's own SVG, so a `url(#lsfill)`
   in the stylesheet is a reference every page loads and only one page can resolve. The port
   audit calls that an unwired asset and it is right to: a paint server and the thing that
   paints with it belong in the same file. The element carries the fill. */
/* The peak and the trough, marked where they happen. */
.loadshape .mk {{ fill:var(--accent); stroke:var(--bg); stroke-width:1.5; }}
.loadshape .mklab {{ fill:var(--ink-bright); font-size:11px; }}
/* The residual strip. One hue, one width, and the length is the whole message, which is the
   same rule the capacity bar follows. A miss above the line and a miss below it are the same
   colour, because "forecast high" is not better or worse than "forecast low". */
.loadshape .res {{ stroke:var(--accent); stroke-width:6; stroke-linecap:butt;
  opacity:.75; vector-effect:non-scaling-stroke; }}
/* The residual's zero, drawn stronger than a gridline. Whether a bar hangs above or below it
   is the whole reading, and against the faint divider token it was a guess. */
.loadshape .zero {{ stroke:var(--rule-strong); stroke-width:1.5;
  vector-effect:non-scaling-stroke; }}
.loadshape .line {{ fill:none; stroke:var(--accent); stroke-width:2;
  stroke-linejoin:round; vector-effect:non-scaling-stroke; }}
.loadshape .fc {{ fill:none; stroke:var(--ink-mute); stroke-width:1.4;
  stroke-dasharray:5 4; vector-effect:non-scaling-stroke; }}
.loadshape .g {{ stroke:var(--rule); stroke-width:1; vector-effect:non-scaling-stroke; }}
.loadshape .ax {{ fill:var(--ink-mute); font-family:var(--mono); font-size:11px; }}
.loadshape .ax.unit {{ font-size:9px; letter-spacing:.08em; }}
/* SVG TEXT SCALES WITH THE DRAWING, AND THE DRAWING SHRINKS TO FIT.
   The chart is a 720 unit wide viewBox rendered to whatever the column gives it, so an 11
   unit label is 11 screen pixels at exactly one width and nothing like it anywhere else.
   Measured: at a 390px viewport the sheet renders 358px wide, a scale of 0.497, which puts
   every axis number and both peak labels at 5.5 PIXELS. Legible on a laptop, unreadable on
   the phone this site is mostly read on, and no build-time check can see it because the
   markup is identical at every width.
   So the user-unit size steps up as the sheet steps down, chosen to land every label between
   about 10 and 13 screen pixels across the whole range. `tests/responsive.mjs` measures the
   effective size and fails under 10, so these numbers cannot drift away from the drawing. */
@media (max-width:22rem) {{
  .loadshape .ax, .loadshape .mklab {{ font-size:27px; }}
  .loadshape .ax.unit {{ font-size:22px; }}
}}
@media (min-width:22.01rem) and (max-width:26rem) {{
  .loadshape .ax, .loadshape .mklab {{ font-size:22px; }}
  .loadshape .ax.unit {{ font-size:18px; }}
}}
@media (min-width:26.01rem) and (max-width:34rem) {{
  .loadshape .ax, .loadshape .mklab {{ font-size:19px; }}
  .loadshape .ax.unit {{ font-size:16px; }}
}}
@media (min-width:34.01rem) and (max-width:46rem) {{
  .loadshape .ax, .loadshape .mklab {{ font-size:15px; }}
  .loadshape .ax.unit {{ font-size:12px; }}
}}
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

/* THE QUEUE GAP. Two bars on one scale, which is the whole instrument: the distance is seen
   rather than computed. Same law as .bar above, one hue at one intensity at every value, so
   the LENGTH is the entire message and nothing implies a verdict about whether the queue is
   real. A reader draws that conclusion or does not; the page does not draw it for them. */
/* THE INSTRUMENT SITS ON THE PAGE RATHER THAN IN IT. A light card on the night ground, which
   is the one idea worth taking from Meng To's Sylva: the reading is a different KIND of thing
   from the prose around it, and giving it its own surface says so before a word is read.
   Executed in this site's own tokens and not his, so it belongs to this palette.

   EVERY PAIRING WAS CHECKED WITH theme.contrast() AGAINST THE CARD, not against the page. A
   card inverts the ground, so a colour that passed on night can fail on paper and the check
   has to be redone rather than assumed:
     night on paper           17.85   the figures
     capitol_granite on paper  6.14   the labels AND the bar fill
     paper_rule on paper       1.56   the bar track, which carries no meaning and no text

   ONE ACCENT, NOT TWO. Label and bar share a hue and are told apart by size and weight, which
   is the discipline the rest of this sheet keeps. brand.yaml scopes `paper` and
   `capitol_granite` together, so the card is built from a pair the palette already pairs. */
.queuegap {{ margin:0 0 var(--band); scroll-margin-top:5rem;
  background:var(--paper); color:var(--night);
  border-radius:var(--radius-lg); padding:clamp(1.25rem,4vw,2.5rem);
  box-shadow:0 1px 0 rgba(255,255,255,.06), 0 24px 60px -28px rgba(0,0,0,.85); }}
.queuegap h2, .queuegap h3 {{ color:var(--night); }}
.queuegap .qlede {{ color:var(--night); }}
.queuegap .qk {{ color:var(--granite); }}
.queuegap .qv {{ color:var(--night); }}
.queuegap .qnote {{ color:var(--granite); }}
.queuegap .qnote a {{ color:var(--granite); text-decoration-color:var(--paper-rule); }}
.queuegap .qbar {{ background:var(--paper-rule); border-color:var(--paper-rule); }}
.queuegap .qfill {{ background:var(--granite); }}
.queuegap .qstages li {{ border-bottom-color:var(--paper-rule); }}
.queuegap .qstages .qs {{ color:var(--granite); }}
/* The page's first section sits under a sticky masthead, so its heading needs the same
   clearance an anchored jump would get. */
.queuegap > h2:first-child {{ padding-top:.35rem; }}
.queuegap .qlede {{ font-family:var(--display); font-size:var(--s2); line-height:1.25;
  max-width:22ch; margin:0 0 var(--gap); }}
.qgap {{ display:flex; flex-direction:column; gap:.55rem; margin:0 0 .7rem; }}
.qrow {{ display:grid; grid-template-columns:minmax(9rem,auto) 1fr; gap:.5rem 1rem;
  align-items:center; }}
.qlab {{ display:flex; flex-direction:column; line-height:1.15; }}
.qk {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-mute); }}
.qv {{ font-family:var(--display); font-size:var(--s1); color:var(--ink-bright);
  font-variant-numeric:tabular-nums; }}
.qbar {{ height:1.1rem; background:var(--surface); border:var(--hair) solid var(--rule-strong);
  border-radius:2px; overflow:hidden; }}
.qfill {{ height:100%; background:var(--accent-deep); min-width:2px; }}
.qnote {{ font-size:var(--s-1); color:var(--ink-mute); max-width:var(--measure);
  margin:0 0 var(--gap); }}

/* The funnel. AN ORDERED LIST because the stages are genuinely sequential: a project cannot
   draw power before it is cleared to. The number is not decoration, so it is not drawn. */
/* max-width:none because the base rule caps every `ol` at the reading measure, and this is a
   figure rather than prose: capped, its rows stopped two thirds across while the bars above
   ran the full card and the two read as misaligned. */
.qstages {{ list-style:none; padding:0; margin:0 0 .7rem; max-width:none;
  display:flex; flex-direction:column; gap:.4rem; }}
.qstages li {{ display:grid; grid-template-columns:minmax(0,1fr) auto auto; gap:.75rem;
  align-items:baseline; padding:.5rem 0; border-bottom:var(--hair) solid var(--line); }}
/* THE STAGE LABEL WRAPS, THE FIGURE NEVER DOES. At 380px the three columns were overflowing
   and taking the share off the right edge. The label is the only part that can afford to
   take two lines. */
.qstages .qk {{ overflow-wrap:anywhere; }}
.qstages .qs {{ font-family:var(--mono); font-size:var(--s-2); color:var(--ink-mute);
  font-variant-numeric:tabular-nums; min-width:3.4rem; text-align:right; }}

/* The monthly series. Paired bars per month, cleared then drawing, so a reader sees that
   neither has moved. Shape carries it, not colour: the pair is always left-then-right and the
   two are separated by a gap rather than by hue alone. */
/* ---- BEYOND ERCOT: WHO IS HERE, AND WHAT IS BEING BUILT ----
   Two feeds that are not ERCOT and do not share its cadence, so they say when they were read
   and say it LOUDLY when they stop. A stopped collector publishes the same last figure
   forever and is indistinguishable from a working one; the read date is the only difference,
   so it ships beside the figure rather than in a commit log. */
.beyond {{ margin:0 0 var(--band); }}
.beyond .blede {{ font-family:var(--display); font-size:var(--s2); line-height:1.25;
  max-width:28ch; margin:1.1rem 0 var(--gap); color:var(--ink-bright); }}
.srcline {{ display:flex; align-items:center; gap:.45rem; font-family:var(--mono);
  font-size:var(--s-2); letter-spacing:.05em; text-transform:uppercase;
  color:var(--ink-mute); margin:0 0 .4rem; }}
.srcdot {{ width:.4rem; height:.4rem; border-radius:50%; background:var(--gold); flex:none; }}
/* THE STALE STATE IS A SENTENCE, NOT A COLOUR. A reader who cannot see the tint still reads
   that the feed stopped, because the copy says so and the copy is what carries it. */
.srcline.stale {{ text-transform:none; letter-spacing:0; font-family:var(--body);
  font-size:var(--s-1); color:var(--ink-bright); border-left:2px solid var(--gold);
  padding-left:.7rem; max-width:var(--measure); display:block; }}

/* A year, a bar and a count. The same row shape serves the registry and the county list, so
   the two read as one instrument rather than two chart styles on one page. */
.ryears {{ list-style:none; padding:0; margin:0 0 .6rem; max-width:none;
  display:flex; flex-direction:column; gap:.28rem; }}
.ryr {{ display:grid; grid-template-columns:4.6rem minmax(0,1fr) 3.4rem; gap:.7rem;
  align-items:center; }}
.rk {{ font-family:var(--mono); font-size:var(--s-2); color:var(--ink-mute);
  letter-spacing:.05em; overflow-wrap:anywhere; }}
.rb {{ height:.8rem; background:var(--ember); border-radius:1px; min-width:2px; }}
.rv {{ font-family:var(--mono); font-size:var(--s-2); color:var(--ink-bright);
  text-align:right; font-variant-numeric:tabular-nums; }}

/* THREE ROLES SIDE BY SIDE, because the registry records three and they answer different
   questions. They stack on a narrow screen rather than shrinking to unreadable columns. */
/* min() on the track floor and min-width:0 on the cell. Without both, a long filer name sets
   a min-content width the 1fr track cannot go below, the grid grows past its container, and
   the third column's counts are cut off at the edge of the page. */
.rroles {{ display:grid; gap:1.4rem 2rem; margin:.6rem 0 0;
  grid-template-columns:repeat(auto-fit, minmax(min(15rem, 100%), 1fr)); }}
.rrole {{ min-width:0; }}
.rrole h4 {{ font-size:var(--s-1); margin:0 0 .4rem; }}
.rrole .ops li {{ gap:.6rem; }}
.rrole .on {{ min-width:0; overflow-wrap:anywhere; }}
.newest {{ list-style:none; margin:.4rem 0 0; padding:0; max-width:none;
  display:grid; gap:.1rem; }}
.newest li {{ display:grid; grid-template-columns:9.5rem 1fr 1fr; gap:.6rem;
  padding:.4rem 0; border-bottom:var(--hair) solid var(--rule); align-items:baseline; }}
.nwd {{ font-family:var(--mono); font-size:var(--s-2); color:var(--dust); }}
.nwn {{ font-weight:500; }}
.nwo {{ color:var(--dust); font-size:var(--s-1); }}
@media (max-width:34rem) {{
  .newest li {{ grid-template-columns:1fr; gap:.1rem; }}
}}
/* THE WHOLE ROSTER. 149 rows is the actual record and it is the thing nobody else publishes
   as a table, so it ships in full rather than as a top ten. It scrolls inside its own box so a
   wide table never makes the PAGE scroll sideways. */
/* THE SCANNER'S FRONT DOOR. The question is set at display size in the reader's own voice,
   and under it the crew that answers it is listed as a numbered run order rather than a feature
   grid, because that is what it is: four agents, in sequence, each with one job. A feature grid
   says "here are some benefits". A run order says "here is the machine, and here is what it
   does first". */
/* THE SCANNER'S FRONT DOOR, AS AN INSTRUMENT AND NOT AN EXPLAINER.
   The first attempt answered a design brief with prose: four agents, four paragraphs, most of
   a screen of text before the control. Owner's note, and it is right, was that a reader should
   FEEL this rather than read it. So the words are cut to a fraction and the crew is drawn as
   the signal chain it actually is, four stages on one line, each with a name and three or four
   words. The control sits directly under the question where a front door belongs, and the chain
   reads as the machine behind it rather than as a list of features. */
/* An <h2>, so it takes the same top rule and accent stub every other section heading gets
   from `main > section > h2`. It IS this section's heading; it was a <p> only because it is
   phrased as the reader's question, and that is what data-voice is for. */
/* FULL WIDTH FOR THE RULE, SHORT MEASURE FOR THE WORDS. The separator every section wears is
   the h2's own border-top, so the heading has to span the section or the line comes up short:
   at 1400px the others are 1152px wide and this one was 391px, which is why its rule looked
   like a stub instead of a seam. The max-width belongs to the TEXT, so it moves inside. */
.scanq {{ font-family:var(--display); font-size:var(--s3); line-height:1.1;
  letter-spacing:-.015em; margin:0 0 .5rem; }}
.scanq span {{ display:block; max-width:18ch; }}
.scanlede {{ color:var(--dust); margin:0 0 1.2rem; max-width:34ch; }}
.scanfoot {{ color:var(--dust); font-size:var(--s-1); margin:1.1rem 0 0; }}
/* A LINE WITH FOUR STATIONS ON IT. The rule runs behind the dots, so the eye reads a chain
   rather than four cards, which is the difference between a machine and a feature grid. */
.chainlab {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.1em;
  text-transform:uppercase; color:var(--accent); margin:1.7rem 0 0; }}
.chain {{ list-style:none; margin:.9rem 0 0; padding:0; max-width:none; position:relative;
  display:grid; grid-template-columns:repeat(4, minmax(0, 1fr)); gap:0 1rem; }}
.chain::before {{ content:""; position:absolute; left:.3rem; right:.3rem; top:.34rem;
  height:1px; background:var(--rule); }}
.chain li {{ position:relative; padding-top:1.3rem; }}
.chain li::before {{ content:""; position:absolute; left:0; top:0; width:.7rem; height:.7rem;
  border-radius:50%; background:var(--bg); border:1px solid var(--accent); }}
.chain b {{ display:block; font-weight:500; font-size:var(--s-1); }}
.chain span {{ display:block; color:var(--dust); font-family:var(--mono);
  font-size:var(--s-2); line-height:1.45; margin-top:.15rem; }}
@media (max-width:42rem) {{
  .chain {{ grid-template-columns:repeat(2, minmax(0, 1fr)); gap:1.1rem 1rem; }}
  .chain::before {{ display:none; }}
}}
/* WATCHING A RUN. The chain is the same four stations the front door shows, so the thing a
   reader was promised is the thing they watch, and the state moves along it. Done is filled,
   live pulses, ahead is an empty ring. The pulse stops under prefers-reduced-motion, same as
   the daily reading's dot. */
.watch .watchchain li[data-state="done"]::before {{ background:var(--accent);
  border-color:var(--accent); }}
/* Live carries a halo AS WELL AS the pulse, because the pulse is the only thing separating
   live from done and prefers-reduced-motion turns it off. A distinction that exists only in
   motion does not exist for the reader who asked for no motion. */
.watch .watchchain li[data-state="live"]::before {{ background:var(--accent);
  border-color:var(--accent); animation:livepulse 1.8s ease-in-out infinite;
  box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 26%,transparent); }}
.watchstate {{ font-family:var(--mono); font-size:var(--s-1); color:var(--accent);
  letter-spacing:.06em; text-transform:uppercase; margin:1.2rem 0 0; }}
.wfeed {{ list-style:none; margin:1.4rem 0 0; padding:0; max-width:none;
  display:grid; gap:.1rem; }}
/* THE FEED IS NOT PROSE AND DOES NOT TAKE THE PROSE MEASURE. `p,li` caps every list item at
   --measure, which is right for a paragraph and wrong here: these are short monospace lines,
   and capping them left the feed as a narrow ragged column in the left half of a wide page
   with the rules stopping in mid air. The lane runs the width of the column it is in. */
.wfeed li {{ max-width:none; padding:.5rem 0; border-top:var(--hair) solid var(--rule);
  display:grid; grid-template-columns:minmax(0,7.5rem) 1fr; gap:0 1.2rem;
  align-items:baseline; }}
/* AND THE STATION IS PRINTED WHERE IT CHANGES, not on every line. Repeating the same word
   twelve times says nothing. Printing it once, at the turn, is what makes the depth legible:
   a reader sees how many things happened under footprint before industry started. */
.wfeed li.wturn {{ border-top-color:color-mix(in srgb,var(--accent) 34%,var(--rule)); }}
.wphase {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.14em;
  text-transform:uppercase; color:var(--accent); line-height:1.5; }}
.wnote {{ color:var(--dust); font-family:var(--mono); font-size:var(--s-2);
  line-height:1.5; }}
@media (max-width:46rem) {{
  /* On a phone the gutter would eat a third of the line, so the station sits on its own row
     above the run it opens, and the lines that do not open one give the row back. */
  .wfeed li {{ grid-template-columns:1fr; gap:.2rem; }}
  .wphase:empty {{ display:none; }}
}}
.watchdone {{ font-family:var(--display); font-size:var(--s1); line-height:1.2;
  margin:1.3rem 0 0; max-width:34ch; }}
@media (prefers-reduced-motion:reduce) {{
  .watch .watchchain li[data-state="live"]::before {{ animation:none; }}
}}
/* THE HIDDEN HALF ANNOUNCES ITSELF. At 390px the table is 704px wide inside a 356px box, so
   exactly half of it, the operator and the date, was off screen with nothing at the right edge
   saying so: the last column simply stopped mid word and read as the end of the table.

   THE FADE IS A SIBLING, NOT AN ANCESTOR, and that is the whole engineering of it. The first
   version put the gradient on the scroll box itself, which works and looks right and cost
   1,482 runs of text: tests/text_contrast composites the ANCESTOR stack and declines to
   measure a run whose ground is a gradient rather than guess at it, so a gradient on the
   scroller made the roster, the largest block of text on the page, invisible to the gate that
   checks whether text is legible. Declines went 126 to 1,608 and guards still went green,
   which is the point. A pseudo element on the wrapper paints over the same pixels without
   entering any cell's ancestor chain, so every cell stays measured.

   A scrollbar was tried first and does not work here: overlay scrollbars reserve no space and
   appear only while scrolling, which is exactly when the reader no longer needs telling.
   Measured, the gutter is 2px with or without `scrollbar-gutter: stable`, and that 2px is the
   border. */
.rtfield {{ position:relative; }}
.rtfield::after {{ content:""; position:absolute; top:1px; right:1px; bottom:1px; width:2.2rem;
  pointer-events:none; border-radius:0 3px 3px 0;
  background:linear-gradient(to left, var(--night), transparent); }}
@media (min-width:46.01rem) {{
  .rtfield::after {{ display:none; }}
}}
.rtwrap {{ overflow-x:auto; overflow-y:auto; max-height:32rem; margin:.5rem 0 0;
  border:var(--hair) solid var(--rule); border-radius:3px;
  scrollbar-width:thin; scrollbar-color:var(--dust) transparent; }}
.rtwrap::-webkit-scrollbar {{ height:9px; width:9px; }}
.rtwrap::-webkit-scrollbar-thumb {{ background:var(--dust); border-radius:5px; }}
/* And the words, on the widths where the table actually overflows. */
.rthint {{ display:none; }}
@media (max-width:46rem) {{
  .rthint {{ display:block; }}
}}
.rtable {{ border-collapse:collapse; width:100%; min-width:44rem;
  table-layout:fixed; font-size:var(--s-1); }}
.rtable col.cf {{ width:19%; }}
.rtable col.co {{ width:24%; }}
.rtable col.cu {{ width:22%; }}
.rtable col.cp {{ width:22%; }}
.rtable col.cd {{ width:13%; }}
.rtable td {{ overflow-wrap:anywhere; }}
.rtable th, .rtable td {{ text-align:left; padding:.45rem .7rem; vertical-align:top;
  border-bottom:var(--hair) solid var(--rule); }}
.rtable th {{ position:sticky; top:0; background:var(--panel); font-family:var(--mono);
  font-size:var(--s-2); letter-spacing:.06em; text-transform:uppercase;
  color:var(--dust); z-index:1; }}
.rtable td.num {{ font-family:var(--mono); font-size:var(--s-2); white-space:nowrap;
  color:var(--dust); }}
.rtable tbody tr:hover {{ background:color-mix(in srgb, var(--dust) 8%, transparent); }}
.ops {{ list-style:none; padding:0; margin:0 0 .6rem; max-width:none;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(16rem,1fr)); gap:0 1.6rem; }}
.ops li {{ display:grid; grid-template-columns:1fr auto; gap:.6rem; align-items:baseline;
  padding:.36rem 0; border-bottom:var(--hair) solid var(--line); font-size:var(--s-1); }}
.ops .on {{ color:var(--ink-bright); overflow-wrap:anywhere; }}
.ops .os {{ font-family:var(--mono); font-size:var(--s-2); color:var(--ink-mute);
  font-variant-numeric:tabular-nums; }}

@media (max-width:30rem) {{
  .ryr {{ grid-template-columns:4.2rem minmax(0,1fr) 3rem; gap:.5rem; }}
}}

/* ---- THE DAILY READING, AS AN INSTRUMENT PANEL ----
   The section held a settled reading every day and read like an essay about one: seven equal
   weight headings, two tables, and prose explaining the page to itself. What follows gives the
   day one hierarchy, one chart, one bar and one row of tiles, so a reader meets four KINDS of
   thing rather than seven paragraphs. */

/* The state of the machine, in the machine's voice. The dot carries no value and no verdict,
   it only says the collector ran, and it holds still for anyone who asked it to. */
.livebar {{ display:flex; flex-wrap:wrap; align-items:center; gap:.4rem .9rem;
  font-family:var(--mono); font-size:var(--s-1); color:var(--ink-mute);
  padding:.55rem 0 1.1rem; border-bottom:var(--hair) solid var(--line); margin-bottom:1.4rem; }}
.livebar strong {{ color:var(--ink-bright); font-weight:500; }}
.livedot {{ width:.5rem; height:.5rem; border-radius:50%; background:var(--gold);
  box-shadow:0 0 0 0 color-mix(in srgb, var(--gold) 70%, transparent);
  animation:livepulse 2.6s ease-out infinite; flex:none; }}
@keyframes livepulse {{
  0% {{ box-shadow:0 0 0 0 color-mix(in srgb, var(--gold) 60%, transparent); }}
  70% {{ box-shadow:0 0 0 .5rem color-mix(in srgb, var(--gold) 0%, transparent); }}
  100% {{ box-shadow:0 0 0 0 color-mix(in srgb, var(--gold) 0%, transparent); }}
}}
@media (prefers-reduced-motion:reduce) {{ .livedot {{ animation:none; }} }}
.livesep {{ width:var(--hair); height:.9rem; background:var(--line); flex:none; }}

/* The day's vital signs. A table gave six numbers the same weight and spent a column
   explaining each one; these align on one optical line so magnitudes compare by eye. */
.stiles {{ display:grid; gap:1px; background:var(--line); border:var(--hair) solid var(--line);
  grid-template-columns:repeat(auto-fit,minmax(8.5rem,1fr)); margin:1.6rem 0 0;
  border-radius:var(--radius); overflow:hidden; }}
.stile {{ background:var(--deep); padding:.85rem .9rem 1rem; display:flex;
  flex-direction:column; gap:.15rem; }}
.sk {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.09em;
  text-transform:uppercase; color:var(--ink-mute); }}
.sv {{ font-family:var(--display); font-size:clamp(1.35rem,3.2vw,1.9rem); line-height:1.05;
  color:var(--ink-bright); font-variant-numeric:tabular-nums; }}
.su {{ font-family:var(--mono); font-size:.42em; color:var(--ink-mute); margin-left:.28em;
  letter-spacing:.04em; }}
.sn {{ font-size:var(--s-2); color:var(--ink-mute); }}

/* What served the load. One bar says gas served about half the day before a word is read;
   the figures stay underneath rather than being replaced by the picture. */
.fuelbar {{ display:flex; height:1.5rem; border-radius:2px; overflow:hidden; margin:.2rem 0 1rem;
  border:var(--hair) solid var(--line); }}
.fseg {{ display:block; height:100%; }}
.fseg.f0 {{ background:var(--ember); }}
.fseg.f1 {{ background:var(--gold); }}
.fseg.f2 {{ background:color-mix(in srgb, var(--gold) 62%, var(--panel)); }}
.fseg.f3 {{ background:color-mix(in srgb, var(--ember) 58%, var(--panel)); }}
.fseg.f4 {{ background:color-mix(in srgb, var(--caliche) 46%, var(--panel)); }}
.fseg.f5 {{ background:color-mix(in srgb, var(--caliche) 30%, var(--panel)); }}
.fseg.f6 {{ background:color-mix(in srgb, var(--dust) 26%, var(--panel)); }}
.fseg.f7 {{ background:color-mix(in srgb, var(--dust) 16%, var(--panel)); }}
.fuelkey {{ list-style:none; padding:0; margin:0 0 .5rem; max-width:none;
  display:grid; grid-template-columns:repeat(auto-fit,minmax(15rem,1fr)); gap:.1rem 1.6rem; }}
.fuelkey li {{ display:grid; grid-template-columns:auto 1fr auto auto; align-items:baseline;
  gap:.55rem; padding:.32rem 0; border-bottom:var(--hair) solid var(--line);
  font-size:var(--s-1); }}
.fkey {{ width:.65rem; height:.65rem; border-radius:1px; align-self:center; }}
.fkey.f0 {{ background:var(--ember); }}
.fkey.f1 {{ background:var(--gold); }}
.fkey.f2 {{ background:color-mix(in srgb, var(--gold) 62%, var(--panel)); }}
.fkey.f3 {{ background:color-mix(in srgb, var(--ember) 58%, var(--panel)); }}
.fkey.f4 {{ background:color-mix(in srgb, var(--caliche) 46%, var(--panel)); }}
.fkey.f5 {{ background:color-mix(in srgb, var(--caliche) 30%, var(--panel)); }}
.fkey.f6 {{ background:color-mix(in srgb, var(--dust) 26%, var(--panel)); }}
.fkey.f7 {{ background:color-mix(in srgb, var(--dust) 16%, var(--panel)); }}
.fkey.fnone {{ border:var(--hair) dashed var(--rule-strong); }}
.fuelkey .fn {{ color:var(--ink-bright); }}
.fuelkey .fp, .fuelkey .fm {{ font-family:var(--mono); font-size:var(--s-2);
  color:var(--ink-mute); font-variant-numeric:tabular-nums; }}
.fuelkey .fp {{ min-width:3.6rem; text-align:right; }}
.fuelkey .fm {{ min-width:5rem; text-align:right; }}
.fuelkey .fneg .fn {{ color:var(--ink-mute); }}
.funit {{ font-family:var(--mono); font-size:var(--s-2); letter-spacing:.06em;
  text-transform:uppercase; color:var(--ink-mute); margin:0 0 var(--gap); }}

.daily h3 {{ margin-top:var(--band); }}
.daily h4 {{ font-family:var(--mono); font-size:var(--s-1); letter-spacing:.08em;
  text-transform:uppercase; color:var(--ink-mute); margin:1.8rem 0 .5rem; font-weight:500; }}
.gridnote {{ margin-top:var(--band); }}

/* THE SERIES, AS AN INSTRUMENT RATHER THAN A PICTURE. Built from HTML boxes and not SVG so the
   values are real text: selectable, readable by a screen reader, visible to the numeral gate,
   and never distorted by a stretched viewBox. Hover and keyboard focus both raise a group,
   because a chart nobody can interrogate is a screenshot with extra steps. */
.qchart {{ margin:0; padding:0; }}
.qgroups {{ list-style:none; margin:0; padding:0; max-width:none;
  display:grid; grid-auto-flow:column; grid-auto-columns:1fr; gap:clamp(.2rem,1.4vw,1rem);
  align-items:end; height:clamp(7rem,20vw,10rem); }}
.qgrp {{ display:flex; flex-direction:column; align-items:center; justify-content:flex-end;
  height:100%; gap:.35rem; border-radius:2px; padding:.2rem .1rem;
  transition:background .18s ease; }}
.qgrp:hover, .qgrp:focus-visible {{
  background:color-mix(in srgb, var(--granite) 9%, transparent); outline:none; }}
.qgrp:focus-visible {{ box-shadow:0 0 0 2px var(--granite); }}
/* The pair is CAPPED and centred so the two bars read as one month's reading. Letting the
   columns take the whole group set the two bars of a pair as far apart as two neighbouring
   months, and the pairing stopped being visible. The cap is wide enough for both value labels
   at every width tested; tightening it further is what puts them back into each other. */
/* THE PAIR SHARES ONE BOX, AND THERE IS NO OTHER BOX. .qbars is the plot: it holds the
   height, it is the positioning context, and both bars are absolutely positioned in it. The
   .qb wrapper is display:contents, so it contributes NO box at all and only carries --h down
   to the two children that need it.
   That last part is the fix. Every previous version kept .qb as a real box and tried to make it
   fill its row, and every version got it wrong in a different direction: too tall and the
   labels left the figure, too short and the bars stood on two baselines 22.4px apart, drawing
   4,049 at 1.66 times the height its value earns. A bar chart with two baselines is not a bar
   chart, and the reliable way to have one baseline is to have one box. Both fills now resolve
   `bottom:0` and `height:var(--h)` against the SAME element, so a shared baseline and a shared
   scale are not properties to be maintained, they are the only thing the markup can express. */
.qbars {{ position:relative; width:100%; max-width:clamp(4.6rem,13vw,7.5rem);
  margin-inline:auto; flex:1; }}
.qb {{ display:contents; }}
.qbf {{ position:absolute; bottom:0; transform:translateX(-50%);
  width:clamp(9px,3.2vw,26px); height:var(--h); min-height:2px;
  border-radius:1px 1px 0 0; }}
/* THE LABEL RIDES ITS OWN BAR: same --h, so it sits at the bar's top edge whatever the value.
   The band at the top of the column was what left a short bar's number floating 64px above the
   thing it names. */
.qbv {{ position:absolute; bottom:var(--h); transform:translateX(-50%);
  margin-bottom:.2rem; white-space:nowrap; }}
.qb.qa .qbf, .qb.qa .qbv {{ left:27%; }}
.qb.qd .qbf, .qb.qd .qbv {{ left:73%; }}
.qb.qa .qbf {{ background:var(--granite); }}
.qb.qd .qbf {{ background:color-mix(in srgb, var(--granite) 42%, var(--paper)); }}
.qmiss {{ height:100%; display:flex; flex-direction:column; justify-content:flex-end;
  align-items:center; gap:.3rem; width:100%; }}
.qmissr {{ width:70%; border-top:1px dashed color-mix(in srgb, var(--granite) 45%, transparent);
  height:0; }}
/* NOT DIMMED. The first version faded both the word and the month to signal absence, which
   put "May" at 3.49 against a floor of 4.5 and was caught by tests/text_contrast. Fading is
   also the wrong instrument: it says "absent" in colour alone, which is the signal this file
   refuses everywhere else. The dashed rule and the word carry it, at full legibility. */
.qmisst {{ font-family:var(--mono); font-size:clamp(7.5px,1.9vw,11px); line-height:1.6;
  color:var(--granite); letter-spacing:.06em; order:-1; }}
.qb.qa .qbf {{ background:var(--granite); }}
.qb.qd .qbf {{ background:color-mix(in srgb, var(--granite) 42%, var(--paper)); }}
/* THE VALUE SITS ABOVE ITS OWN BAR and is always present, never revealed on hover. A number a
   reader has to hunt for is a number the page did not really publish. It turns upright rather
   than disappearing on a narrow screen, so six months still fit at 380px. */
.qbv {{ font-family:var(--mono); font-size:clamp(7.5px,1.9vw,11px); line-height:1.6;
  color:var(--granite); font-variant-numeric:tabular-nums; white-space:nowrap; }}
.qgrp:hover .qbv, .qgrp:focus-visible .qbv {{ color:var(--night); font-weight:500; }}
.qm {{ font-family:var(--mono); font-size:var(--s-2); color:var(--granite);
  letter-spacing:.06em; }}
.qlegend {{ display:flex; flex-wrap:wrap; align-items:center; gap:.35rem 1rem;
  font-family:var(--mono); font-size:var(--s-2); color:var(--granite);
  letter-spacing:.06em; text-transform:uppercase; margin:.9rem 0 .5rem; }}
.qkey {{ width:.7rem; height:.7rem; border-radius:1px; display:inline-block;
  margin-right:.3rem; vertical-align:-1px; }}
.qkey.qa {{ background:var(--granite); }}
.qkey.qd {{ background:color-mix(in srgb, var(--granite) 42%, var(--paper)); }}
.qlegend .qunit {{ margin-left:auto; opacity:.75; }}
/* NARROW SCREENS TURN THE VALUE UPRIGHT, and the container has to make room for it or the
   tallest bars push their own labels off the top. The first phone render clipped five of six
   to "8,78" and "9,04", which is worse than no label. The padding is inside the fixed height,
   so the bars simply get shorter and every value stays whole. */
@media (max-width:30rem) {{
  .qgroups {{ height:13rem; padding-top:3.4rem; }}
  .qbv {{ writing-mode:vertical-rl; transform:rotate(180deg);
    font-size:9.5px; letter-spacing:.02em; }}
  .qlegend {{ font-size:9.5px; gap:.3rem .6rem; }}
  .qlegend .qunit {{ margin-left:0; }}
}}

/* Meng To's Sylva easing. A long tail that settles rather than stops, which suits a bar whose
   length IS the measurement: it arrives at its value and stays there instead of bouncing. */
.queuegap .qfill {{ transition:width 1.1s cubic-bezier(.16,1,.3,1); }}
@media (prefers-reduced-motion:reduce) {{ .queuegap .qfill {{ transition:none; }} }}

@media (max-width:26rem) {{
  .qrow {{ grid-template-columns:1fr; gap:.15rem; }}
  .qlab {{ flex-direction:row; align-items:baseline; gap:.5rem; }}
}}
/* The metro bars on the water watch. Same rule, smaller: sorted driest first, and identical in
   colour at every value, so the ordering carries the comparison and nothing implies that a
   short bar is a verdict about a city's water supply. */
.bar.mini {{ height:.7rem; margin:0; min-width:6rem; }}
td.barcell {{ width:40%; vertical-align:middle; }}
/* FOUR COLUMNS IN 380 PIXELS, AND THE BAR WAS TAKING THE NAME'S SHARE.
   Measured on a phone: the table gets 380, the bar cell took 131 of it from `width:40%` and a
   6rem floor, and the metro name was left with 100. "Midland and Odessa" then wrapped to two
   lines, the federal delineation under it wrapped to two more, and that row stood 118 pixels
   tall against a 34 pixel median. Nineteen rows of that is a column of ragged whitespace.
   Four options were measured rather than argued about. Dropping the bar column is the shortest
   table by a little and it is the wrong answer: the caption tells a reader that the length
   carries the comparison, so a width where the bar is absent makes the caption lie. Narrowing
   it and tightening the cell padding keeps every column, every figure and the bar, gives the
   name 176 pixels instead of 100, and takes the worst row from 118 to 75 and the whole table
   down by 27 percent. */
@media (max-width:34rem) {{
  td.barcell {{ width:20%; }}
  .bar.mini {{ min-width:2.6rem; }}
  table.metros th, table.metros td {{ padding:.45em .3em; }}
}}
table.metros th[scope="row"] {{ font-weight:400; color:var(--ink-bright);
  text-transform:none; letter-spacing:0; font-size:var(--s-1); border-bottom-width:var(--hair);
  border-bottom-color:var(--rule); }}
caption {{ caption-side:bottom; text-align:left; padding-top:.75rem; font-size:var(--s-1);
  color:var(--ink-mute); max-width:var(--measure); }}

/* ---- the ask box -------------------------------------------------------- */
/* Answered in the reader's browser. The styling says "a tool", not "a chatbot": no avatar, no
   typing dots, no conversation. A question and what the record says. */
/* A FOLD, for the complete answer a reader did not ask for yet. `details` needs no script,
   is keyboard and screen reader native, and prints open. */
.fold {{ margin:1.25rem 0 0; border-top:var(--hair) solid var(--rule);
  border-bottom:var(--hair) solid var(--rule); }}
.fold > summary {{ cursor:pointer; padding:.8rem 0; font-family:var(--mono);
  font-size:var(--s-2); letter-spacing:.08em; text-transform:uppercase;
  color:var(--ink-mute); }}
.fold > summary:hover {{ color:var(--ink-bright); }}
.fold[open] > summary {{ color:var(--ink-bright); }}
.fold h3 {{ margin:1.4rem 0 0; font-size:var(--s0); }}
.fold table {{ margin-bottom:1rem; }}
@media print {{ .fold > summary {{ list-style:none; }}
  .fold > summary::-webkit-details-marker {{ display:none; }}
  .fold > *:not(summary) {{ display:revert !important; }} }}

/* ---- services: the capability grid, the offers and the form ----------------- */
.capgrid {{ display:grid; gap:var(--gap); margin:1.5rem 0 0;
  grid-template-columns:repeat(auto-fit,minmax(min(100%,15rem),1fr)); }}
/* SIX CARDS WANT THREE AND THREE. Left to auto-fit at reading width they land four and two,
   which reads as a grid that ran out rather than one that was planned. */
@media (min-width:58rem) {{ .capgrid {{ grid-template-columns:repeat(3,1fr); }} }}
.cap {{ border-top:2px solid var(--rule-strong); padding-top:.9rem; }}
.cap .k {{ display:block; font-family:var(--mono); font-size:var(--s-2);
  letter-spacing:.1em; text-transform:uppercase; color:var(--accent); }}
.cap h3 {{ margin:.35rem 0 .35rem; font-size:var(--s0); line-height:1.25; }}
.cap p {{ margin:0; color:var(--ink-mute); font-size:var(--s-1); }}

/* THE OFFERS CARRY THE WEIGHT OF THE PAGE, so they are the only cards on the site with a
   filled ground. The first one leads because a reader choosing between three options mostly
   wants to be told where to start. */
.offers {{ display:grid; gap:var(--gap); margin:1.5rem 0 0;
  grid-template-columns:repeat(auto-fit,minmax(min(100%,17rem),1fr)); }}
.offer {{ border:var(--hair) solid var(--rule-strong); border-radius:var(--radius);
  background:var(--surface); padding:1.15rem var(--gap) 1.25rem; }}
.offer.lead {{ border-color:var(--accent); background:var(--panel); }}
.offer h3 {{ margin:.5rem 0 .4rem; font-size:var(--s1); line-height:1.2; }}
.offer p {{ margin:0 0 .6rem; color:var(--ink-mute); }}
.offer .terms {{ margin:0; font-size:var(--s-1); color:var(--ink-bright); }}
.offer.lead .terms {{ color:var(--accent); }}

/* THE FORM. Typography on rules, not boxes.
   A form on a services page is the only place on this site a reader types anything that leaves
   the machine, so it is the one place worth getting right. It was four identical bordered boxes
   stacked in a narrow column with the field names living in placeholders, which is the shape a
   contact form has had since about 2009 and reads exactly that old.
   What it is instead: a mono uppercase label that never leaves, over a field with no box at all,
   sitting on the same hairline rule this site draws under every heading and between every
   footer link. The page already speaks that language everywhere else. */
.startgrid {{ display:grid; gap:clamp(1.75rem,4vw,3.5rem); align-items:start;
  grid-template-columns:minmax(0,1fr); }}
/* The pitch and the alternatives on the left, the form on the right, which is read then act.
   One column until there is genuinely room for two, so the form never gets squeezed thin. */
@media (min-width:56rem) {{
  .startgrid {{ grid-template-columns:minmax(0,20rem) minmax(0,1fr); }}
}}
.startsay h2 {{ margin-top:0; }}

/* The two ways in that are not this form. They were three stacked paragraphs competing with
   the thing they sit next to. A kicker, a link and one line each says the same in a third of
   the space and stops reading as an apology for the form. */
.altways {{ list-style:none; margin:1.75rem 0 0; padding:0; display:grid; gap:1.15rem; }}
.altways li {{ max-width:none; border-top:var(--hair) solid var(--rule); padding-top:.85rem; }}
.altways .k {{ display:block; font-family:var(--mono); font-size:var(--s-2);
  letter-spacing:.14em; text-transform:uppercase; color:var(--accent); margin-bottom:.3rem; }}
.altways a {{ display:inline-block; min-width:24px; padding-block:.15rem;
  font-size:var(--s1); color:var(--ink-bright); text-decoration:none;
  border-bottom:var(--hair) solid color-mix(in srgb,var(--accent) 50%,transparent);
  transition:border-color .2s; }}
.altways a:hover {{ border-bottom-color:var(--accent); }}
.altways p {{ margin:.4rem 0 0; font-size:var(--s-1); color:var(--ink-mute); max-width:34rem; }}

/* Capped, because a rule running the full width of a wide column stops reading as a field
   and starts reading as a divider. */
.leadform {{ display:grid; gap:1.4rem; margin:1.9rem 0 0; max-width:36rem; }}
/* Inside the two column block the grid's own gap does this job, so the margin would double it. */
.startgrid .leadform {{ margin-top:0; }}
/* Two short fields share a row rather than each taking a full one, which is most of why the
   old form looked like a queue. */
.row2 {{ display:grid; gap:1.4rem; grid-template-columns:minmax(0,1fr); }}
@media (min-width:34rem) {{ .row2 {{ grid-template-columns:1fr 1fr; }} }}
.field label {{ display:block; font-family:var(--mono); font-size:var(--s-2);
  letter-spacing:.14em; text-transform:uppercase; color:var(--ink-mute); margin:0 0 .45rem; }}
/* "optional" is an aside, so it is set as one. Lowercase against the uppercase label carries
   the distinction at the SAME colour, because a dimmer grey is how a legible label becomes an
   illegible one and this site measures every run of text against its ground. */
.field .opt {{ text-transform:none; letter-spacing:.01em; font-style:italic; }}
.field input, .field textarea {{ display:block; width:100%; font:400 var(--s1)/1.5 var(--body);
  color:var(--ink-bright); background:transparent; border:0; border-radius:0;
  border-bottom:var(--hair) solid var(--rule-strong); padding:.4em 0 .5em;
  transition:border-color .2s,box-shadow .2s; }}
.field textarea {{ resize:vertical; min-height:6.5rem; }}
.field input:hover, .field textarea:hover {{ border-bottom-color:var(--ink-mute); }}
/* Focus thickens the rule AND changes its hue, so the state is not carried by colour alone.
   The site's global focus ring still lands on top of this, which is the convention everywhere
   else here and is not worth breaking for one component. */
.field input:focus, .field textarea:focus {{ border-bottom-color:var(--accent);
  box-shadow:0 2px 0 0 var(--accent); }}
/* AUTOFILL, WHICH IS WHERE A TRANSPARENT FIELD GOES WRONG. Chrome paints its own near-white
   background behind an autofilled input and ignores `background`, so a dark form fills itself
   in with white boxes of nearly invisible text. The inset shadow is the only thing that
   overrides it. */
.field input:-webkit-autofill, .field input:-webkit-autofill:hover,
.field input:-webkit-autofill:focus {{
  -webkit-text-fill-color:var(--ink-bright); caret-color:var(--ink-bright);
  -webkit-box-shadow:0 0 0 100px var(--bg) inset;
  transition:background-color 9999s ease-in-out 0s; }}
.field .hint {{ display:block; margin:.5rem 0 0; font-size:var(--s-1); color:var(--ink-mute); }}
/* Full width on a phone, where a button that does not fill the column reads as an afterthought.
   Sized to its own text once there is room beside it. */
.leadform button {{ cursor:pointer; border:0; width:100%; margin-top:.2rem; }}
@media (min-width:34rem) {{
  .leadform button {{ width:auto; justify-self:start; min-width:13rem; }}
}}

/* ---- published work: the article feed -------------------------------------- */
/* TWO COLUMNS AT READING WIDTH, ONE ON A PHONE, and the image leads.
   IT USED TO CARRY `.vcard` TOO, back when the videos page was a grid of posters beside this
   one. That page is a full-bleed vertical feed now with its own document and its own styles,
   so every `.vcard` selector here matched nothing. Dead CSS in a shared selector list is the
   worst kind: it reads as a live rule, so the next person to change the grid keeps it working
   for a page that stopped existing. */
.deckgrid {{ display:grid; gap:var(--gap); margin:1.75rem 0 0;
  grid-template-columns:repeat(auto-fill,minmax(min(100%,17rem),1fr)); }}
.deckgrid .deck {{ display:block; margin:0; text-decoration:none; color:inherit;
  border:var(--hair) solid var(--rule); border-radius:var(--radius); overflow:hidden;
  background:var(--surface); }}
.deckgrid .deck img {{ display:block; width:100%; height:auto;
  aspect-ratio:4/5; object-fit:cover; background:var(--panel); }}
.deckgrid .deck h3 {{ margin:.35rem 0 0; font-size:var(--s0); line-height:1.25; }}
.deckgrid .deck .meta {{ margin:0; }}
/* The one line under a card title that says what the article is about. A title names
   the piece and a name is not a summary, so the card carried only half its job. */
.deckgrid .deck .tease {{ margin:.3rem 0 0; font-size:var(--s-1); line-height:1.45;
  color:var(--ink-mute); }}
.deckgrid .deck > :not(img) {{ padding:0 .9rem; }}
.deckgrid .deck {{ padding-bottom:1rem; transition:border-color .2s,transform .2s; }}
.deckgrid .deck:hover {{ border-color:var(--accent); transform:translateY(-2px); }}

/* THE LATEST ONE, on the front page. Cover beside copy above the fold width, stacked below
   it, because a 4:5 image next to a paragraph at 30rem leaves neither enough room. */
.latest {{ display:grid; gap:var(--gap); margin:1.25rem 0 0; align-items:start;
  grid-template-columns:minmax(0,15rem) minmax(0,1fr); }}
.latest .cover img, .latest .vidwrap video {{ display:block; width:100%; height:auto;
  aspect-ratio:4/5; object-fit:cover; border-radius:var(--radius);
  border:var(--hair) solid var(--rule); background:var(--panel); }}
.latest h3 {{ margin:.4rem 0 .3rem; font-size:var(--s1); line-height:1.2; }}
.latest p {{ margin:0 0 .9rem; color:var(--ink-mute); }}
@media (max-width:40rem) {{
  .latest {{ grid-template-columns:1fr; }}
  .latest .cover, .latest .vidwrap {{ max-width:15rem; }}
}}
.sub {{ margin:.2rem 0 0; color:var(--ink-mute); font-size:var(--s-1); }}
/* Every slide of one shipped article, read top to bottom. */
.slides {{ display:grid; gap:.75rem; margin:1.5rem 0 0;
  grid-template-columns:repeat(auto-fill,minmax(min(100%,20rem),1fr)); }}
.slides img {{ display:block; width:100%; height:auto; border-radius:var(--radius);
  border:var(--hair) solid var(--rule); }}

.askbox {{ border:var(--hair) solid var(--rule-strong); border-radius:var(--radius);
  padding:1.25rem var(--gap); background:var(--surface); margin:1.5rem 0; }}
/* THE LEAN VARIANT, which is the box on the front page. It sits directly under the hero and
   competes with it for the first screen, so it carries no chrome of its own: the field IS the
   object, and the border, the panel and the padding that made sense on a dedicated page all
   read as a box drawn around a box here. The answer region still gets its rule, because that
   one separates two different things rather than decorating one. */
.askbox.lean {{ border:0; background:transparent; padding:0; margin:0; }}
.askbox.lean .composer {{ gap:.5rem; }}
.askbox.lean .chips {{ margin-top:.7rem; }}
.asksection {{ margin:2.25rem 0 0; }}
.askfoot {{ margin:.7rem 0 0; font-size:var(--s-1); color:var(--ink-mute); }}
/* A label that a screen reader reads and a sighted reader does not need, because the
   placeholder already says it. Never `display:none`, which takes it off the accessibility
   tree along with everything else. */
.vh {{ position:absolute; width:1px; height:1px; margin:-1px; padding:0; overflow:hidden;
  clip:rect(0 0 0 0); white-space:nowrap; border:0; }}
/* THE COMPOSER, NOT A SEARCH FORM. This was a square cornered field with a square cornered
   button sitting beside it, which is the shape a site search has had since about 2006 and
   reads that way. What this box actually does is take a question in a sentence and answer it,
   so it is shaped like the thing people now type questions into: ONE rounded container with
   the field and the send control inside it, rather than two rectangles in a row.
   THE SHELL IS ON THE FORM AND NOT ON `.askbox`, which matters because the front page uses
   the `.lean` variant that strips the outer panel. Putting the shape on the wrapper would
   have deleted it exactly where it is most used. */
.composer {{ display:flex; gap:.5rem; align-items:center; flex-wrap:nowrap;
  padding:.4rem .4rem .4rem 1.15rem; border-radius:1.6rem;
  border:var(--hair) solid var(--rule-strong);
  background:color-mix(in srgb,var(--surface) 82%,transparent);
  transition:border-color .18s ease, box-shadow .18s ease, background-color .18s ease; }}
/* FOCUS IS A SOFT RING, NOT A HARD BORDER SWAP. A one pixel colour change on a dark ground is
   almost invisible, and this control is the one thing on the front page a reader is invited to
   act on. `:focus-within` so the ring belongs to the composer while the caret is in the field. */
.composer:focus-within {{ border-color:color-mix(in srgb,var(--accent) 70%,transparent);
  background:color-mix(in srgb,var(--surface) 96%,transparent);
  box-shadow:0 0 0 4px color-mix(in srgb,var(--accent) 14%,transparent); }}
.askbox label {{ position:absolute; left:-9999px; }}
.composer input {{ flex:1 1 auto; min-width:0; font:400 var(--s1)/1.5 var(--body);
  padding:.5em 0; background:transparent; color:var(--ink-bright);
  border:0; border-radius:0; }}
/* The field carries no ring of its own. The composer around it already has one, and two
   nested focus rings is how a control starts looking like a bug. */
.composer input:focus, .composer input:focus-visible {{ outline:none; }}
.composer input::placeholder {{ color:var(--ink-mute); }}
/* Safari paints its own clear affordance inside a `type=search`, which lands on top of the
   send control at small widths. */
.composer input::-webkit-search-decoration,
.composer input::-webkit-search-cancel-button {{ -webkit-appearance:none; appearance:none; }}
/* THE SEND CONTROL IS A CIRCLE INSIDE THE SHELL. Square is 2.4rem so it clears the 24 pixel
   target floor on a phone with room to spare, and it keeps its accessible name in a visually
   hidden span rather than relying on the glyph. */
.composer button[type="submit"] {{ flex:none; height:2.4rem; display:grid;
  place-items:center; padding:0; border:0; cursor:pointer;
  background:var(--accent-deep); color:var(--on-accent);
  transition:transform .16s ease, background-color .16s ease, opacity .16s ease; }}
.composer button[type="submit"] svg {{ width:1.05rem; height:1.05rem; display:block; }}
.composer button[type="submit"]:hover {{ transform:translateY(-1px); }}
.composer button[type="submit"]:active {{ transform:translateY(0); }}
/* TWO CONTROL SHAPES IN ONE SHELL, chosen by whether the control carries a word.
   THE CIRCLE is the ask composer's. Its placeholder already says what the box does, so an
   arrow is the whole instruction, and 2.4rem square clears the 24 pixel target floor on a
   phone with room to spare.
   THE PILL is for a control that has to name its own action. The scan bar starts a scan on
   somebody's own website, which is a different promise from sending a question and is worth a
   word rather than a glyph. Same shell, same height, same focus ring, so the two read as one
   family at a glance.
   `:not(.cta)` rather than source order: two rules of equal specificity fighting over one
   button is a shape that breaks the next time somebody reorders this file. */
.composer button[type="submit"]:not(.cta) {{ width:2.4rem; border-radius:50%; }}
.composer button.cta {{ width:auto; border-radius:999px; padding:0 1.2rem;
  font-size:var(--s-2); box-shadow:none; }}
.composer button.cta:hover {{ transform:translateY(-1px); box-shadow:none; }}
/* The scan bar's own spacing. The shell is shared, the distance from the prose above it is
   this section's business. */
.scanform {{ margin:1.5rem 0 0; }}
.askbox .chips {{ display:flex; gap:.5rem; flex-wrap:wrap; margin-top:.9rem; }}
.askbox .chips button {{ font:400 var(--s-1)/1 var(--body); padding:.5em .85em;
  background:transparent; color:var(--ink-mute);
  border:var(--hair) solid var(--rule-strong); border-radius:999px; cursor:pointer; }}
.askbox .chips button:hover {{ color:var(--ink-bright); border-color:var(--accent); }}

/* ---- the written lane --------------------------------------------------- */
/* Typing is answered here in the browser and sends nothing. Pressing enter sends the question
   to a model that writes it up from the same record. Those are two different things and the
   box has to make a reader feel the difference before they press, not explain it after.
   THE NOTE IS ABOVE THE CONTROL IT DESCRIBES, and it says what each half does in the reader's
   own terms. It is not fine print: it is the honest half of an offer. */
.asknote {{ margin:.75rem 0 0; font-size:var(--s-1); line-height:1.55; color:var(--ink-mute);
  max-width:52ch; }}
.asknote b {{ color:var(--ink-bright); font-weight:500; }}

/* A LINK THAT IS A BUTTON, AND A BUTTON THAT IS A LINK. "Send feedback" opens a dialog so it
   has to be a button for a keyboard and a screen reader, and "Book a call" leaves the site so
   it has to be an anchor. They sit in the same sentence and must not look like two different
   kinds of thing, so the styling is on the class rather than on the element. */
.asklink {{ font:inherit; color:var(--accent); background:none; border:0; padding:0;
  cursor:pointer; text-decoration:none;
  border-bottom:1px solid color-mix(in srgb,var(--accent) 35%,transparent); }}
.asklink:hover {{ border-bottom-color:var(--accent); }}
.askdot {{ display:inline-block; width:3px; height:3px; border-radius:50%; margin:0 .55em .2em;
  background:var(--ink-mute); vertical-align:middle; }}

/* THE FEEDBACK DIALOG. A native <dialog>, so focus trapping, escape to close and the top
   layer come from the browser rather than from three hundred lines that are wrong on one
   phone. ::backdrop is the browser's too. */
.askfb {{ border:var(--hair) solid var(--rule-strong); border-radius:var(--radius);
  background:var(--surface); color:var(--ink); padding:0; max-width:min(94vw, 34rem);
  width:100%; }}
.askfb::backdrop {{ background:color-mix(in srgb,#000 62%,transparent); }}
.askfb form {{ display:grid; gap:.55rem; padding:1.35rem var(--gap) 1.15rem; }}
.askfb h2 {{ margin:0; font-size:var(--s2); }}
.askfbnote {{ margin:0 0 .35rem; font-size:var(--s-1); line-height:1.55; color:var(--ink-mute); }}
.askfbl {{ font-size:var(--s-1); color:var(--ink-mute); }}
.askfb textarea, .askfb input[type="email"] {{ font:400 var(--s0)/1.5 var(--body);
  width:100%; padding:.6em .75em; border-radius:.6rem; color:var(--ink-bright);
  background:color-mix(in srgb,var(--surface) 60%,#000);
  border:var(--hair) solid var(--rule-strong); }}
.askfb textarea:focus, .askfb input[type="email"]:focus {{ outline:none;
  border-color:color-mix(in srgb,var(--accent) 70%,transparent);
  box-shadow:0 0 0 3px color-mix(in srgb,var(--accent) 14%,transparent); }}
.askfbcheck {{ display:flex; gap:.5rem; align-items:flex-start; margin-top:.2rem;
  font-size:var(--s-1); color:var(--ink-mute); cursor:pointer; }}
.askfbcheck input {{ margin-top:.15rem; accent-color:var(--accent); }}
/* What is about to be sent, shown before it is. Scrolls rather than growing the dialog past
   the viewport on a phone. */
.askfbctx {{ margin:0; max-height:8.5rem; overflow:auto; white-space:pre-wrap;
  font:400 var(--s-1)/1.5 var(--body); color:var(--ink-mute);
  padding:.6rem .75rem; border-radius:.5rem;
  background:color-mix(in srgb,var(--surface) 60%,#000);
  border:var(--hair) solid var(--rule); }}
.askfbmsg {{ margin:0; min-height:1.2em; font-size:var(--s-1); color:var(--accent); }}
.askfbrow {{ display:flex; gap:1rem; align-items:center; margin-top:.3rem; }}
.askfbsend {{ font:400 var(--s-1)/1 var(--body); padding:.7em 1.4em; border:0;
  border-radius:999px; cursor:pointer; background:var(--accent-deep); color:var(--on-accent);
  transition:transform .16s ease, opacity .16s ease; }}
.askfbsend:hover {{ transform:translateY(-1px); }}
.askfbsend[disabled] {{ opacity:.6; cursor:default; transform:none; }}

/* THE THREAD SITS ABOVE THE FIELD. A conversation reads upward: what was said is behind you
   and the thing you type into stays under your thumb. Putting answers below the composer
   pushes the field down the page as the exchange grows, so the control a reader wants is the
   one that keeps moving away from them. */
.askthread {{ margin:0 0 1.1rem; display:grid; gap:0; }}
.askturn {{ margin:0 0 .7rem; padding-left:.85rem; font-size:var(--s0);
  line-height:1.5; color:var(--ink-mute);
  border-left:2px solid var(--rule-strong); }}
.askreply + .askturn {{ margin-top:1.6rem; }}
.askreply {{ font-size:var(--s1); line-height:1.7; color:var(--ink-bright); }}
.askreply p {{ margin:0; }}
.askreply a.cite {{ color:var(--accent); text-decoration:none;
  border-bottom:1px solid color-mix(in srgb,var(--accent) 35%,transparent); }}
.askreply a.cite:hover {{ border-bottom-color:var(--accent); }}

/* WHAT IS HAPPENING, WHILE IT HAPPENS. Both halves of this line are true rather than
   decorative. The record really is being read, and every figure really is checked against it
   before it is allowed onto the page. */
.askstage {{ display:flex; align-items:center; gap:.6rem;
  font-size:var(--s-1); color:var(--ink-mute); }}
.askstage::before {{ content:""; width:.4rem; height:.4rem; border-radius:50%; flex:none;
  background:var(--accent); animation:askpulse 1.1s ease-in-out infinite; }}
@keyframes askpulse {{ 0%,100% {{ opacity:.25; transform:scale(.8); }}
                       50% {{ opacity:1; transform:scale(1); }} }}
/* Each verified sentence arrives on its own and fades rather than snapping in. The fade is
   not ornament: it marks the sentence as a unit, which is the unit the guard checks. */
.askseg {{ animation:askfade .3s ease both; }}
@keyframes askfade {{ from {{ opacity:0; }} to {{ opacity:1; }} }}

/* WHERE AN ANSWER STOPPED, AND WHY. A sentence that fails a check ends the answer there. The
   reader is told which check, in words, because "something went wrong" from a record product
   is worse than the stop itself. */
.askstop {{ margin-top:.8rem; padding-left:.85rem; border-left:2px solid var(--accent);
  font-size:var(--s-1); line-height:1.55; color:var(--ink-mute); }}

/* TAKING THE ANSWER UP ON ITS CLOSING OFFER. Every answer ends by offering the obvious next
   question. This turns that offer into one press, and it FILLS THE FIELD RATHER THAN SENDING,
   because sending is the half that costs and a reader should see what they are about to ask. */
.asknext {{ justify-self:start; margin-top:1rem; font:400 var(--s-1)/1 var(--body);
  padding:.6em 1.1em; cursor:pointer; border-radius:999px;
  color:var(--accent); background:color-mix(in srgb,var(--accent) 8%,transparent);
  border:var(--hair) solid color-mix(in srgb,var(--accent) 40%,transparent);
  transition:background-color .18s ease, border-color .18s ease; }}
.asknext:hover {{ background:color-mix(in srgb,var(--accent) 16%,transparent);
  border-color:var(--accent); }}

/* Provenance, after the answer and quiet about it. This is the line that makes the box worth
   trusting, so it stays. It just does not announce itself first. */
.askfrom {{ margin-top:1.1rem; padding-top:.8rem;
  border-top:var(--hair) solid var(--rule);
  display:flex; flex-wrap:wrap; gap:.9rem; align-items:baseline;
  font-size:var(--s-1); line-height:1.5; color:var(--ink-mute); }}
.askagain {{ font:inherit; color:var(--accent); background:none; border:0; padding:0;
  cursor:pointer; border-bottom:1px solid color-mix(in srgb,var(--accent) 35%,transparent); }}
.askagain:hover {{ border-bottom-color:var(--accent); }}

/* ANSWERING TAKES THE SCREEN. The starters, the note and the engine's live list all step
   aside, so the answer is the only thing being read. They come back with Start over. */
.askbox.answering .chips,
.askbox.answering .asknote {{ display:none; }}

/* ---- THE BOX TAKES THE SCREEN ON A PHONE -----------------------------------------------
   Owner, after asking a question on a phone: "there's so much stuff on screen, your eyes
   don't even go to the right spot", and of the field, "when a user clicks onto the search
   bar, we really want everything else on the screen to just disappear".
   A hero, a stat row, a nav and a sky sit behind this box, and on a 390px screen they are all
   still there while somebody is trying to read an answer. On a laptop there is room for
   context, so this is scoped to the width where there is not.
   NOT `position: fixed` ON THE BOX. Fixing the box inside a scrolled document leaves the rest
   of the page scrolling underneath it on iOS and fights the parking arithmetic that keeps the
   field seated. The PAGE is held still and everything that is not the box is taken out of the
   flow, so the box is simply the only thing there is. */
@media (max-width:37.5rem) {{
  body.asking {{ overflow:hidden; }}
  body.asking .sky, body.asking .masthead, body.asking main > *:not(.asksection),
  body.asking .sitefoot {{ display:none; }}
  body.asking .asksection {{ margin:0; }}
  body.asking main {{ padding:0; }}
  /* The safe-area token keeps the field off the home indicator on a notched phone. */
  body.asking #ask {{ position:fixed; inset:0; z-index:60; overflow-y:auto;
    padding:.9rem var(--gap) calc(.9rem + var(--safe-bottom));
    background:var(--bg); display:flex; flex-direction:column; justify-content:flex-end; }}
  body.asking #ask .askthread {{ flex:1 1 auto; overflow-y:auto; }}
  /* THE WAY OUT IS VISIBLE. A full screen mode with no exit is a trap, and Escape is not
     discoverable on a phone at all. */
  body.asking .askclose {{ display:flex; }}
}}
.askclose {{ display:none; position:absolute; top:.5rem; right:.5rem; z-index:61;
  width:2.75rem; height:2.75rem; align-items:center; justify-content:center;
  border:0; border-radius:999px; background:transparent; color:var(--ink-mute);
  font-size:1.5rem; line-height:1; cursor:pointer; }}
.askclose:hover, .askclose:focus-visible {{ color:var(--ink-bright); }}


/* The send control while it is working. The spinner replaces the arrow rather than sitting
   beside it, so the control keeps its size and the layout does not shift under a thumb. */
.askbox button[type="submit"][aria-busy="true"] svg {{ display:none; }}
.askbox button[type="submit"][aria-busy="true"]::after {{ content:""; width:.95rem;
  height:.95rem; border-radius:50%; border:2px solid color-mix(in srgb,var(--on-accent) 35%,transparent);
  border-top-color:var(--on-accent); animation:askspin .7s linear infinite; }}
@keyframes askspin {{ to {{ transform:rotate(360deg); }} }}
.askbox button[type="submit"][disabled] {{ cursor:default; opacity:.75; }}

/* The human check. Managed mode is invisible unless a person is genuinely needed, so this
   holds no space until Turnstile puts something in it. */
#askts:not(:empty) {{ margin-top:.9rem; }}

@media (prefers-reduced-motion:reduce) {{
  .askstage::before {{ animation:none; opacity:1; }}
  .askseg {{ animation:none; }}
  .askbox button[type="submit"][aria-busy="true"]::after {{ animation:none; }}
}}

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
/* Every one of these measured 14 pixels tall, which is a target a thumb misses. The gap
   shrinks by the padding added, so the row reads the same and the target is twice the size. */
.footnav {{ display:flex; flex-wrap:wrap; gap:.1rem 1.4rem; margin:0; padding:0;
  list-style:none; font-family:var(--mono); font-size:var(--s-2); letter-spacing:.14em;
  text-transform:uppercase; }}
.footnav a {{ display:inline-block; min-width:24px; padding-block:.45rem; }}
/* THE SAME 24 PIXEL FLOOR, FOR THE LINKS THAT ARE NOT IN A SENTENCE. WCAG 2.5.8 exempts a target
   inline in a block of text, and that exemption is doing real work here: inline-blocking a link
   inside running prose stops it wrapping mid-phrase, which is a worse outcome than a small target
   a reader hits by aiming at a word. So this reaches only the standalone ones. A source citation
   and a call to action are objects on the page, not words in a sentence. */
.meta a, cite a, a.go, .filelist a, .prose > p > a.plain {{ display:inline-block;
  min-width:24px; padding-block:.28rem; }}
.footnav li {{ max-width:none; }}
/* WHERE THIS RECORD IS ELSEWHERE. A row of marks, sized as targets first.
   44 pixels, not the 24 the footnav links settled for. WCAG 2.5.8 sets 24 as the floor and
   2.5.5 sets 44 as the comfortable size, and a text link has its own label to aim at while an
   icon is only ever the box. The box IS the target here, so it takes the larger number.
   The mark sits at 18 so the padding does the growing, which keeps the row visually quiet at a
   size a thumb still lands on. */
.socials {{ display:flex; flex-wrap:wrap; gap:.5rem; margin:1.25rem 0 0; padding:0;
  list-style:none; }}
.socials li {{ max-width:none; }}
.socials a {{ display:flex; width:44px; height:44px; align-items:center; justify-content:center;
  border:var(--hair) solid var(--rule); border-radius:12px; color:var(--ink-mute);
  transition:color .2s, border-color .2s, transform .2s; }}
/* `fill:currentColor` so the glyph follows the link's own colour through hover and focus, which
   is one declaration instead of three and cannot get out of step with them. */
.socials svg {{ width:18px; height:18px; fill:currentColor; }}
.socials a:hover {{ color:var(--accent); border-color:var(--accent);
  transform:translateY(-2px); }}
/* THE SAME TREATMENT ON FOCUS, because a keyboard reaches this row too and the hover state is
   the only thing that says which mark is live. */
.socials a:focus-visible {{ color:var(--accent); border-color:var(--accent); }}
@media (prefers-reduced-motion:reduce) {{
  .socials a {{ transition:none; }}
  .socials a:hover {{ transform:none; }}
}}
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
.colophon-line span {{ white-space:normal; }}
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
    ("on-accent", "accent-deep", AA_BODY,
     "the ask box's submit control, and the topic chip a reader is standing on"),
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

    # THE CHART'S TWO GEOMETRIC PROMISES, ASSERTED IN THE STYLESHEET THAT MAKES THEM.
    # Both bars are pinned to the bottom of the SHARED box, which is what gives the pair one
    # baseline and one scale; and each label is pinned to its own bar's height, which is what
    # keeps a short bar's number with the short bar. Both shipped broken while the markup looked
    # right, so they are asserted here, where they are actually decided.
    check("both bars are pinned to the bottom of the shared plot",
          ".qbf { position:absolute; bottom:0;" in sheet)
    check("...and the plot box is the thing that is positioned",
          ".qbars { position:relative;" in sheet)
    check("...and the column contributes no box of its own to get mis-sized",
          ".qb { display:contents; }" in sheet)

    # THE HIDDEN HALF OF THE ROSTER HAS TO ANNOUNCE ITSELF. Half the table is off screen at
    # phone width, and the shadows are what say so. `local` on two of the four layers is the
    # whole mechanism: without it they are a static fade that lies at the end of the travel.
    # The affordance must not be a gradient under the text. A gradient ground is one
    # tests/text_contrast declines to measure, and putting one on the roster hid 1,482 runs
    # from the gate that checks legibility without turning anything red.
    # The fade must be a SIBLING of the table, never a background on one of its ancestors.
    # A gradient ancestor is a ground tests/text_contrast declines to measure, and putting one
    # on the scroll box hid 1,482 runs from the gate that checks legibility while guards stayed
    # green. This asserts the shape that keeps them measured.
    check("the roster's edge fade is painted by a sibling, not by the scroll box",
          ".rtfield::after { content:\"\";" in sheet
          and "background" not in sheet.split(".rtwrap {")[1].split("}")[0])
    check("...and the words appear at the widths where it actually overflows",
          ".rthint { display:none; }" in sheet and ".rthint { display:block; }" in sheet)
    check("...and each label is pinned to the height of its own bar",
          ".qbv { position:absolute; bottom:var(--h);" in sheet)

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
    #
    # ONE CARVE-OUT, AND IT IS NARROW ON PURPOSE. The mark is the Texas flag, and the flag has a
    # red stripe in it; refusing the flag its own colour would be the rule eating the thing it
    # was written to protect. So `--flag-red` may be worn by exactly one selector, the mark's red
    # field, and the check names that selector rather than counting uses. A carve-out that says
    # "once" would let the next use be anywhere.
    # `re`, not `_re`: the alias is bound below and is therefore local to the
    # whole function. Same trap as the print-block check further up.
    reds = re.findall(r"([^{}]*)\{[^{}]*var\(--flag-red\)", sheet)
    check("red is not a general utility",
          ".red{" not in sheet and ".text-red" not in sheet)
    check("...and the only thing wearing the flag's red is the flag",
          [r.strip() for r in reds] == [".wordmark .m-red"], str([r.strip() for r in reds]))
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
    # THE MARK IS THE WHOLE FLAG NOW, drawn to Government Code sec. 3100.001 in mark.py rather
    # than typed as an approximate path into a blue box that was very nearly square when the
    # statute makes that stripe twice as tall as it is wide.
    check("the mark carries the flag's three fields",
          all(f".wordmark .m-{f}" in sheet for f in ("blue", "white", "red")))
    check("...and the star is cut the way the rotunda's is",
          ".f-lit" in sheet and ".f-shade" in sheet)
    check("...with its proportions coming from the statute, not from CSS",
          ".wordmark .lonestar-mark" in sheet and "width:auto" in sheet)
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
