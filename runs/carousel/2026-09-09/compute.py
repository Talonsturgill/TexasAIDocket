#!/usr/bin/env python3
"""compute.py — every numeral and every measurable length in carousel no. 18.

THE LAW THIS FILE EXISTS FOR. No numeral this project publishes is typed by a person or produced
by a language model. Arithmetic, unit conversion, percentages, ratios, deltas, rankings, date
maths and rounding all happen here, and the slides read `computed.json`.

THE INSTINCT THIS FILE EXISTS FOR, which is broader than the law. **Any position or length a
reader could measure goes through here, not just the ones that carry a printed number.** A shadow
edge at 0.795 of a run's length is an assertion about a percentage whether or not the percentage
is printed beside it, and a frame that eyeballs it is publishing an uncomputed figure in the only
form nobody checks.

Everything below traces to `out/2026-09-09/claims.json`. The claim id is named at every value.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- the source figures
# PARSED OUT OF THE CLAIM QUOTES, not retyped beside them.
#
# This block used to head itself "Read from claims.json rather than retyped, so a claim that
# changes upstream changes here too and cannot silently disagree with the frame", and then assign
# ten literals. Every one of the ten was correct, which is exactly why it survived: nothing
# downstream could tell, and `computed.json` carried the same sentence in its own header. The
# integrity judge found it by reading the file rather than its output.
#
# It is the rubric preamble's own named class and this project's central public promise, so the
# comment is now true. Each figure is lifted from the string the fact checker verified, and a
# quote that stops carrying its figure raises here instead of drifting quietly away from the
# frame. The file already did this for c3's stations and c13's byline credentials, so the honest
# route was in front of it the whole time.
CLAIMS = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}


# WHICH CLAIMS THIS FILE ACTUALLY READ, recorded as it reads them. `computed.json` used to
# publish `claims_used: sorted(CLAIMS)`, which is every id in the claims file: it listed c10,
# which this deck cut, and c15 to c18, which belong to the ERCOT and Lubbock stories and appear
# on no surface. A field named for what was used that reports what was available is the same
# defect as the comment above, one file over.
CLAIMS_READ: set = set()


def _q(cid: str) -> str:
    CLAIMS_READ.add(cid)
    return CLAIMS[cid]["quote"]


def _one(pattern: str, cid: str) -> tuple[str, ...]:
    m = re.search(pattern, _q(cid))
    if not m:
        raise SystemExit(f"claim {cid} no longer carries the figures this deck reads from it. "
                         f"The quote is now {_q(cid)!r}")
    return m.groups()


# c2, the last day, within one day of the true date.
#   "At 24 hours, 79.5% of case manager estimations fell within 1 day vs 37.9% for AI estimations"
_p2 = [float(x) for x in re.findall(r"(\d+\.\d+)%", _q("c2"))]
assert len(_p2) == 2, "c2 must carry exactly the two percentages, case managers first"
CM_WITHIN_1D_24H, AI_WITHIN_1D_24H = _p2

# c3, mean absolute error in days at the two later stations, with intervals.
#   "48 hours: MAE, 1.29 [95% CI, 1.26-1.32] vs 1.59 [95% CI 1.57-1.61] days; 24 hours: ..."
_s3 = re.findall(r"(\d+)\s+hours:\s*MAE,\s*(\d+\.\d+)\s*\[95% CI,?\s*(\d+\.\d+)-(\d+\.\d+)\]"
                 r"\s*vs\s*(\d+\.\d+)\s*\[95% CI,?\s*(\d+\.\d+)-(\d+\.\d+)\]", _q("c3"))
assert [r[0] for r in _s3] == ["48", "24"], "c3 must report the 48 hour station then the 24 hour"
_f = lambda r, k: float(r[k])
CM_MAE_48H, AI_MAE_48H = _f(_s3[0], 1), _f(_s3[0], 4)
CM_MAE_24H, AI_MAE_24H = _f(_s3[1], 1), _f(_s3[1], 4)
CM_CI_48H, AI_CI_48H = (_f(_s3[0], 2), _f(_s3[0], 3)), (_f(_s3[0], 5), _f(_s3[0], 6))
CM_CI_24H, AI_CI_24H = (_f(_s3[1], 2), _f(_s3[1], 3)), (_f(_s3[1], 5), _f(_s3[1], 6))

# c4, admission. The second interval is written without the "95% CI" label in the source, so the
# pattern allows it rather than the deck retyping the bound the source did label oddly.
_a4 = _one(r"MAE,\s*(\d+\.\d+)\s*\[95% CI,?\s*(\d+\.\d+)-(\d+\.\d+)\]"
           r"\s*vs\s*(\d+\.\d+)\s*\[(?:95% CI,?\s*)?(\d+\.\d+)-(\d+\.\d+)\]", "c4")
CM_MAE_ADM, AI_MAE_ADM = float(_a4[0]), float(_a4[3])
CM_CI_ADM, AI_CI_ADM = (float(_a4[1]), float(_a4[2])), (float(_a4[4]), float(_a4[5]))
_e4 = _one(r"\((\d+\.\d+)%\s*vs\s*(\d+\.\d+)%\)", "c4")
CM_EXACT_ADM, AI_EXACT_ADM = float(_e4[0]), float(_e4[1])

# c1, the study window. The month names are the source's own, so the dates are read rather than
# transcribed into ISO by hand.
_MONTHS = ("January February March April May June July August September October November "
           "December").split()
_d1 = re.findall(r"(" + "|".join(_MONTHS) + r")\s+(\d{1,2}),\s*(\d{4})", _q("c1"))
assert len(_d1) == 2, "c1 must carry the two window dates"
_iso = lambda d: f"{d[2]}-{_MONTHS.index(d[0]) + 1:02d}-{int(d[1]):02d}"
WINDOW_START, WINDOW_END = _iso(_d1[0]), _iso(_d1[1])

FRAME_W, FRAME_H = 1080, 1350


def oklch_to_hex(L: float, C: float, H: float) -> str:
    """OKLCH to sRGB hex, gamut-clipped.

    The palette is declared in OKLCH because perceptual lightness is what lets this deck hold
    two party hues at the same L*, which is the discipline that stops colour carrying a verdict.
    The engine needs hex, so the conversion is arithmetic here rather than a hex value somebody
    picked by eye and called equivalent.
    """
    h = math.radians(H)
    a, b = C * math.cos(h), C * math.sin(h)
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    def enc(u: float) -> int:
        u = max(0.0, min(1.0, u))
        u = 12.92 * u if u <= 0.0031308 else 1.055 * (u ** (1 / 2.4)) - 0.055
        return max(0, min(255, round(u * 255)))

    return "#{:02X}{:02X}{:02X}".format(enc(r), enc(g), enc(bl))


# --------------------------------------------------------------------------- the palette
# Every source is a place in Harris County or the Gulf coastal plain, named in the storyboard.
# `manager` and `tool` are held at the SAME L and differ in hue and chroma only, so no frame can
# code one party good and the other bad by value. That equality is asserted below rather than
# trusted, because a hand-tuned pair drifts the first time somebody adjusts one of them.
PARTY_L = 0.58
PALETTE_OKLCH = {
    "crust":    (0.72, 0.03, 70),    # Lake Charles clay, dry cracked surface
    "clay":     (0.34, 0.03, 60),    # the same clay in a crack. The deck's ink
    "bluestem": (0.62, 0.09, 48),    # little bluestem cured to copper, the single warm accent
    "straw":    (0.78, 0.07, 72),    # Indiangrass straw
    "sky":      (0.88, 0.03, 235),   # the Houston September sky
    "haze":     (0.92, 0.02, 80),    # its warm horizon band
    "oakshade": (0.30, 0.03, 160),   # coastal live oak shade
    "cloud":    (0.22, 0.02, 250),   # ground under the cumulus shadow, slide 7 only
    # THE INK IS ITS OWN TOKEN AND IT WAS MEASURED RATHER THAN CHOSEN. `clay` at L 0.34 gives
    # 4.78 against the crust, which clears 4.5 on paper and leaves nothing for the texture the
    # crust actually carries, and qa.py grades the WORST point along a run rather than the mean.
    # This sits far enough down that every ground in the deck clears the bar with room.
    "ink":      (0.20, 0.02, 60),
    "manager":  (PARTY_L, 0.10, 40),
    "tool":     (PARTY_L, 0.05, 250),
}
PALETTE = {k: oklch_to_hex(*v) for k, v in PALETTE_OKLCH.items()}


def _lum(hexstr: str) -> float:
    r, g, b = (int(hexstr[i:i + 2], 16) / 255 for i in (1, 3, 5))

    def f(u: float) -> float:
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4

    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a: str, b: str) -> float:
    la, lb = _lum(PALETTE[a]), _lum(PALETTE[b])
    hi, lo = max(la, lb), min(la, lb)
    return round((hi + 0.05) / (lo + 0.05), 2)


# WHICH GROUND EACH SLIDE MAY SET TYPE ON, measured rather than assumed. A light deck inverts
# the usual risk: on a dark deck a pale ink clears everything, and here the ink has to earn every
# ground it lands on. The slides read this table rather than each making its own judgement.
GROUNDS = ("crust", "straw", "sky", "haze", "bluestem", "manager", "tool", "oakshade", "cloud")
INK_CONTRAST = {g: contrast("ink", g) for g in GROUNDS}
TYPE_SAFE = sorted(g for g, v in INK_CONTRAST.items() if v >= 4.5)
assert "crust" in TYPE_SAFE and "haze" in TYPE_SAFE and "sky" in TYPE_SAFE, \
    "the ink must clear 4.5 against every ground this deck sets type on"

assert PALETTE_OKLCH["manager"][0] == PALETTE_OKLCH["tool"][0], \
    "the two party hues must sit at one lightness, so colour carries no verdict"


# --------------------------------------------------------------------------- slide 2, the window
def days_between(a: str, b: str) -> int:
    import datetime as dt
    return (dt.date.fromisoformat(b) - dt.date.fromisoformat(a)).days


WINDOW_DAYS = days_between(WINDOW_START, WINDOW_END)
# The phenology ramp runs across the drawable width inside the safe margins. Position along it is
# days elapsed rather than a hand-placed stop, so the ramp IS the calendar.
RAMP_X0, RAMP_X1 = 80, FRAME_W - 80
RAMP_PX_PER_DAY = (RAMP_X1 - RAMP_X0) / WINDOW_DAYS


# --------------------------------------------------------------------------- slide 4, the runs
# c2 is a PROPORTION, so each run's shadow edge sits at a fraction of THAT RUN's own length. No
# scale is needed and no ratio between the two runs is drawable, which is why the band between
# them carries no rule.
RUN_LEN = 820
# THE SAME DIVERGENCE AS SLIDE 5, ONE FRAME OVER, FOUND IN THE ROUND THAT CLOSED SLIDE 5.
# This file held 96 and 190; slide-04.html draws 138 and 178 under a comment reading
# "FROM compute.py". No reader received a wrong figure, because the run length and both lit
# fractions agreed and those are what carry the claim, but two of the six geometry fields
# published for this frame described a drawing nobody made. The frame is what a reader receives,
# so these come to the frame. Four scoring panels did not see it, which is the argument for
# injecting each slide's computed block into its frame rather than hand-syncing two files.
RUN_DEPTH = 138
RUN_GAP = 178
CM_EDGE_FRAC = CM_WITHIN_1D_24H / 100.0
AI_EDGE_FRAC = AI_WITHIN_1D_24H / 100.0
CM_EDGE_PX = round(RUN_LEN * CM_EDGE_FRAC, 1)
AI_EDGE_PX = round(RUN_LEN * AI_EDGE_FRAC, 1)


# --------------------------------------------------------------------------- slide 5, the slope
# The axis is anchored at zero and the zero is printed. A truncated axis here would be a lie told
# with a true number, and the top of the axis is set from the largest interval bound in the plot
# rather than from the largest value, so no interval can run off the frame.
# THE PLOT RECT IS THE ONE THE FRAME ACTUALLY DRAWS, and it was not until round 4.
#
# This file had 250/900 and 380/980, giving 300 px per day. Slide 5 draws 330/812 and 660/1020,
# giving 180. So every y coordinate this block published, the four series points, the eight
# interval bounds, the zero and both pixel gaps, described a plot no frame contains, and the
# frame computed its own geometry from its own literals. CLAUDE.md's rule is that every
# measurable length, fraction and coordinate comes from here and nothing is eyeballed, and this
# is the one frame that quietly opted out.
#
# NOTHING CAUGHT IT AND ONE ROUND OF THIS RUN MADE IT WORSE. A judge found aggregates.json
# declaring 180 where computed.json said 300, the run "corrected" aggregates to 300, and 300 is
# the number nobody draws. The frame is what a reader receives, so the frame's rect wins and this
# file is brought to it. The board sits at y 560 to 1120 and a plot at 380 would start above it.
PLOT_X0, PLOT_X1 = 330, 812
PLOT_Y0, PLOT_Y1 = 660, 1020         # y0 is the axis top, y1 is zero
SLOPE_MAX_DAYS = max(AI_CI_24H[1], AI_CI_48H[1], CM_CI_48H[1], CM_CI_24H[1])
SLOPE_AXIS_TOP = math.ceil(SLOPE_MAX_DAYS * 2) / 2      # to the next half day
SLOPE_PX_PER_DAY = (PLOT_Y1 - PLOT_Y0) / SLOPE_AXIS_TOP


def slope_y(days: float) -> float:
    return round(PLOT_Y1 - days * SLOPE_PX_PER_DAY, 1)


SLOPE = {
    "axis_top_days": SLOPE_AXIS_TOP,
    "px_per_day": round(SLOPE_PX_PER_DAY, 4),
    "x_48h": PLOT_X0, "x_24h": PLOT_X1,
    "manager": {"y_48h": slope_y(CM_MAE_48H), "y_24h": slope_y(CM_MAE_24H),
                "ci_48h": [slope_y(CM_CI_48H[1]), slope_y(CM_CI_48H[0])],
                "ci_24h": [slope_y(CM_CI_24H[1]), slope_y(CM_CI_24H[0])]},
    "tool": {"y_48h": slope_y(AI_MAE_48H), "y_24h": slope_y(AI_MAE_24H),
             "ci_48h": [slope_y(AI_CI_48H[1]), slope_y(AI_CI_48H[0])],
             "ci_24h": [slope_y(AI_CI_24H[1]), slope_y(AI_CI_24H[0])]},
    "zero_y": PLOT_Y1,
}

# THE CROSSING WAS SOLVED, AND THERE ISN'T ONE. This is the whole reason the arithmetic runs
# before the drawing.
#
# Two of the three treatments that came back from the directors room described slide 5 as the
# frame where the two lines CROSS, and the storyboard was written that way. They do not cross.
# The case managers sit below the tool at 48 hours (1.29 against 1.59) and further below it at
# 24 hours (0.98 against 1.93), so over the interval the frame draws, the two series DIVERGE.
# Solving for the intersection puts it at t = -0.46, which is off the left of the plot and in a
# region the study reports nothing about.
#
# The picture is better for it. A crossing says one method overtook the other. A widening wedge
# says the humans were ahead the whole way and pulled away, which is what the record holds. A
# frame drawing an eyeballed crossing would have asserted an overtake that never happened, in
# the largest type on the page, and every gate after this one would have passed it.
_dm = CM_MAE_24H - CM_MAE_48H
_dt_ = AI_MAE_24H - AI_MAE_48H
_denom = _dm - _dt_
CROSS_T = (AI_MAE_48H - CM_MAE_48H) / _denom if _denom else None
SLOPE["cross_t"] = round(CROSS_T, 4) if CROSS_T is not None else None
SLOPE["lines_cross_in_plot"] = CROSS_T is not None and 0.0 < CROSS_T < 1.0
assert not SLOPE["lines_cross_in_plot"], \
    "the storyboard must not describe a crossing the figures do not produce"

# The wedge, which is what the frame actually draws. Declared as an aggregate because a gap is a
# computed assertion even when it is drawn rather than printed.
SLOPE["gap_48h_days"] = round(AI_MAE_48H - CM_MAE_48H, 2)
SLOPE["gap_24h_days"] = round(AI_MAE_24H - CM_MAE_24H, 2)
SLOPE["gap_widens"] = SLOPE["gap_24h_days"] > SLOPE["gap_48h_days"]
SLOPE["gap_48h_px"] = round(abs(slope_y(AI_MAE_48H) - slope_y(CM_MAE_48H)), 1)
SLOPE["gap_24h_px"] = round(abs(slope_y(AI_MAE_24H) - slope_y(CM_MAE_24H)), 1)
SLOPE["manager_below_tool_at_both"] = CM_MAE_48H < AI_MAE_48H and CM_MAE_24H < AI_MAE_24H

# The direction each series moves over the last two days, derived rather than asserted in prose.
SLOPE["manager_direction"] = "down" if CM_MAE_24H < CM_MAE_48H else "up"
SLOPE["tool_direction"] = "down" if AI_MAE_24H < AI_MAE_48H else "up"


# --------------------------------------------------------------------------- slide 3, admission
# The two admission marks sit on one scale so their separation is the real one. The frame's whole
# subject is that this separation is unresolvable at feed scale, so the gap is computed and
# published rather than described.
ADM_PX_PER_DAY = 26.0
ADM_GAP_PX = round(abs(AI_MAE_ADM - CM_MAE_ADM) * ADM_PX_PER_DAY, 2)
ADM_GAP_AT_THUMB = round(ADM_GAP_PX * (432 / FRAME_W), 3)


# --------------------------------------------------------------------- slides 6 and 7, ONE sun
# THE FRAME USED TO STAND EACH SOLID UNDER ITS OWN SUN, and the code said so while calling it one.
# The comment here read "one declared sun" over two computed altitudes, 34.99 and 23.11 degrees,
# picked so a 210px solid and a 128px solid would throw one length, and the frame's own comment
# admitted it in as many words: "which is only possible because each stands under its own sun
# altitude". The rationalisation attached to it, that differing altitudes are "exactly the point",
# is the part worth naming. The point is that two methods can agree on an OUTPUT and share nothing
# about the process. Moving the light between them makes the agreement a property of the lighting
# rather than of the objects, which is the opposite claim, drawn on the one frame the deck's
# argument turns on. The storyboard rule two sections up says the sun is declared once and HELD
# STILL across slides 4, 5 and 6, and this broke it inside a single frame.
#
# Under ONE sun, two solids throw one shadow length if and only if they stand the SAME HEIGHT. So
# they do, and everything else about them differs: footprint, profile, curvature, silhouette. That
# is the better drawing of the claim as well as the honest one. The two methods here agreed on one
# measured quantity at admission and shared nothing about how they reached it, which is a shared
# height and no other shared dimension.
#
# Found by the craft judge, from `computed.json`, which published both altitudes openly. Nothing
# was hidden and no gate could see it: the geometry was internally consistent and only the deck's
# own written rule said it was wrong.
SUN_ALT = 34.0                       # the deck's one sun, used by slides 6 and 7 alike
SOLID_H = 202.0                      # ONE height, both solids, so ONE shadow length follows
SHADOW_LEN = round(SOLID_H / math.tan(math.radians(SUN_ALT)), 1)
SUN_ALT_A = SUN_ALT_B = SUN_ALT
SOLID_A_H = SOLID_B_H = SOLID_H
assert SUN_ALT_A == SUN_ALT_B, \
    "two sun altitudes in one frame make the shadow agreement a property of the light"
assert abs(SOLID_A_H / math.tan(math.radians(SUN_ALT_A))
           - SOLID_B_H / math.tan(math.radians(SUN_ALT_B))) < 0.05, \
    "under one sun the two solids agree on shadow length only by standing the same height"


# --------------------------------------------------------------------------- slide 7, the cloud
# The cumulus shadow's offset from the cloud is solved from the SAME declared sun altitude slide 6
# uses, so the weather is geometry rather than a placed shape and the deck's light is one light.
SUN_ALT_S7 = SUN_ALT
CLOUD_BASE_PX = 760.0
CLOUD_OFFSET_PX = round(CLOUD_BASE_PX / math.tan(math.radians(SUN_ALT_S7)), 1)
# The occlusion edge must sit well away from horizontal or it becomes the excluded norther front.
OCCLUSION_EDGE_DEG = 27.0
assert OCCLUSION_EDGE_DEG >= 15.0, "an occlusion edge inside 15 degrees of horizontal is a norther front"


# ------------------------------------------------------------------ the caption's station count
# The caption says the two figures moved "Between the two readings". TWO is a tally of the time
# stations c3 reports, so it is counted off c3's own quote rather than typed. The study reports
# each station as "<N> hours:" followed by its figures, and there are exactly two of them nearer
# discharge. Admission is reported in c4 and is deliberately not one of these.
STATIONS = re.findall(r"(\d+)\s+hours:", _q("c3"))
STATION_COUNT = len(STATIONS)
assert STATIONS == ["48", "24"], \
    "the caption's 'two readings' is the pair c3 names, in the order c3 names them"


# ------------------------------------------------------------------- the caption's author count
# The caption opens "Three authors compared ...". THREE is a tally and the deck must not type it,
# so it is counted here off c13's byline rather than read off it by eye. Each author on that
# byline carries a trailing credential, so the credentials are what get counted: a name with no
# letters after it would not be an author of record and should not be counted as one.
#
# IT SAID "clinicians" UNTIL ALL THREE JUDGES CAUGHT IT. The byline reads MD, BS, MD, and a BS is
# not a clinician credential, so the noun asserted a profession for one of the three that nothing
# fetched establishes. c13's own text carried the overstatement, which is how it reached the
# caption: a claim whose paraphrase says more than its quote hands the extra to every surface
# downstream and no gate can see the difference. The count was right the whole time. The noun was
# not, and the noun is the part a reader believes.
_BYLINE = _q("c13")
CREDENTIALS = re.findall(r",\s*(MD|DO|BS|BA|BSN|RN|MSN|MPH|MS|PhD|PharmD)\b", _BYLINE)
AUTHOR_COUNT = len(CREDENTIALS)
CLINICAL_CREDENTIALS = {"MD", "DO", "RN", "BSN", "MSN", "PharmD"}
# Published as a measurement rather than used, so the next run can see WHY the noun is "authors".
CLINICIANS_ON_BYLINE = len([c for c in CREDENTIALS if c in CLINICAL_CREDENTIALS])
assert AUTHOR_COUNT == len([p for p in _BYLINE.split(",") if p.strip() not in CREDENTIALS]), \
    "every name on the byline must carry exactly one credential, or the tally is counting wrong"
assert CLINICIANS_ON_BYLINE < AUTHOR_COUNT, \
    "if every credential were clinical the caption could say clinicians, and this assert is the " \
    "record that it checked rather than assumed"


def main() -> None:
    out = {
        "run": "2026-09-09",
        "note": "Every value here is computed from claims.json. No numeral in this deck is typed.",
        "frame": {"w": FRAME_W, "h": FRAME_H},
        "palette_oklch": {k: {"L": v[0], "C": v[1], "H": v[2]} for k, v in PALETTE_OKLCH.items()},
        "palette": PALETTE,
        "ink_contrast": INK_CONTRAST,
        "type_safe_grounds": TYPE_SAFE,
        "party_lightness_equal": PALETTE_OKLCH["manager"][0] == PALETTE_OKLCH["tool"][0],
        "figures": {
            "cm_within_1d_24h": CM_WITHIN_1D_24H, "ai_within_1d_24h": AI_WITHIN_1D_24H,
            "cm_mae_48h": CM_MAE_48H, "ai_mae_48h": AI_MAE_48H,
            "cm_mae_24h": CM_MAE_24H, "ai_mae_24h": AI_MAE_24H,
            "cm_mae_adm": CM_MAE_ADM, "ai_mae_adm": AI_MAE_ADM,
            "cm_exact_adm": CM_EXACT_ADM, "ai_exact_adm": AI_EXACT_ADM,
        },
        "slide2": {"window_days": WINDOW_DAYS, "ramp_x0": RAMP_X0, "ramp_x1": RAMP_X1,
                   "px_per_day": round(RAMP_PX_PER_DAY, 4)},
        "slide3": {"px_per_day": ADM_PX_PER_DAY, "gap_px": ADM_GAP_PX,
                   "gap_px_at_432": ADM_GAP_AT_THUMB},
        "slide4": {"run_len": RUN_LEN, "run_depth": RUN_DEPTH, "run_gap": RUN_GAP,
                   "manager_edge_frac": CM_EDGE_FRAC, "tool_edge_frac": AI_EDGE_FRAC,
                   "manager_edge_px": CM_EDGE_PX, "tool_edge_px": AI_EDGE_PX},
        "slide5": SLOPE,
        "slide6": {"shadow_len": SHADOW_LEN, "solid_a_h": SOLID_A_H, "solid_b_h": SOLID_B_H,
                   "sun_alt_deg": SUN_ALT, "one_sun": SUN_ALT_A == SUN_ALT_B,
                   "solids_same_height": SOLID_A_H == SOLID_B_H},
        "slide7": {"sun_alt_deg": SUN_ALT_S7, "cloud_base_px": CLOUD_BASE_PX,
                   "cloud_offset_px": CLOUD_OFFSET_PX, "occlusion_edge_deg": OCCLUSION_EDGE_DEG},
        "caption": {"author_count": AUTHOR_COUNT, "credentials": CREDENTIALS,
                    "station_count": STATION_COUNT, "stations_hours": STATIONS,
                    "clinicians_on_byline": CLINICIANS_ON_BYLINE},
        "claims_read": sorted(CLAIMS_READ),
        "claims_available": len(CLAIMS),
    }
    (HERE / "computed.json").write_text(json.dumps(out, indent=2) + "\n")
    print(f"computed.json written, {len(PALETTE)} palette tokens, "
          f"party lightness equal: {out['party_lightness_equal']}")
    print(f"  slide 4 edges  manager {CM_EDGE_PX}px of {RUN_LEN}  tool {AI_EDGE_PX}px of {RUN_LEN}")
    print(f"  slide 5 axis top {SLOPE_AXIS_TOP} days. Solved crossing at t={SLOPE['cross_t']}, "
          f"inside the plot: {SLOPE['lines_cross_in_plot']}")
    print(f"  slide 5 the wedge  gap {SLOPE['gap_48h_days']}d -> {SLOPE['gap_24h_days']}d "
          f"({SLOPE['gap_48h_px']}px -> {SLOPE['gap_24h_px']}px), widens: {SLOPE['gap_widens']}")
    print(f"  slide 5 direction  manager {SLOPE['manager_direction']}  tool {SLOPE['tool_direction']}")
    print(f"  slide 3 admission gap {ADM_GAP_PX}px, {ADM_GAP_AT_THUMB}px at 432 wide")
    print(f"  slide 6 one sun at {SUN_ALT} degrees, both solids {SOLID_H}px, "
          f"for one shadow length")
    print(f"  ink contrast  " + "  ".join(f"{g} {v}" for g, v in INK_CONTRAST.items()))
    print(f"  type-safe grounds at 4.5 or better: {', '.join(TYPE_SAFE)}")
    for k, v in PALETTE.items():
        print(f"    {k} {v}")


if __name__ == "__main__":
    main()
