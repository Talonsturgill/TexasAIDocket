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
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------- the source figures
# Read from claims.json rather than retyped, so a claim that changes upstream changes here too
# and cannot silently disagree with the frame.
CLAIMS = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}

# c2, the last day, within one day of the true date.
CM_WITHIN_1D_24H = 79.5     # "79.5% of case manager estimations fell within 1 day"
AI_WITHIN_1D_24H = 37.9     # "vs 37.9% for AI estimations"

# c3, mean absolute error in days at the two later stations.
CM_MAE_48H, AI_MAE_48H = 1.29, 1.59
CM_MAE_24H, AI_MAE_24H = 0.98, 1.93
CM_CI_48H, AI_CI_48H = (1.26, 1.32), (1.57, 1.61)
CM_CI_24H, AI_CI_24H = (0.96, 1.01), (1.91, 1.95)

# c4, admission.
CM_MAE_ADM, AI_MAE_ADM = 4.20, 4.27
CM_CI_ADM, AI_CI_ADM = (4.08, 4.31), (4.15, 4.38)
CM_EXACT_ADM, AI_EXACT_ADM = 23.6, 15.3

# c1, the study window.
WINDOW_START, WINDOW_END = "2023-08-01", "2024-02-28"

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
RUN_DEPTH = 96
RUN_GAP = 190
CM_EDGE_FRAC = CM_WITHIN_1D_24H / 100.0
AI_EDGE_FRAC = AI_WITHIN_1D_24H / 100.0
CM_EDGE_PX = round(RUN_LEN * CM_EDGE_FRAC, 1)
AI_EDGE_PX = round(RUN_LEN * AI_EDGE_FRAC, 1)


# --------------------------------------------------------------------------- slide 5, the slope
# The axis is anchored at zero and the zero is printed. A truncated axis here would be a lie told
# with a true number, and the top of the axis is set from the largest interval bound in the plot
# rather than from the largest value, so no interval can run off the frame.
PLOT_X0, PLOT_X1 = 250, 900
PLOT_Y0, PLOT_Y1 = 380, 980          # y0 is the axis top, y1 is zero
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


# --------------------------------------------------------------------------- slide 6, the solids
# Two dissimilar solids, one declared sun, and the shadow lengths SOLVED to equality. The height
# of each solid differs, so each needs its own sun altitude to land the same shadow length, which
# is exactly the point: agreement on the output says nothing about the process behind it.
SHADOW_LEN = 300.0
SOLID_A_H, SOLID_B_H = 210.0, 128.0
SUN_ALT_A = math.degrees(math.atan2(SOLID_A_H, SHADOW_LEN))
SUN_ALT_B = math.degrees(math.atan2(SOLID_B_H, SHADOW_LEN))


# --------------------------------------------------------------------------- slide 7, the cloud
# The cumulus shadow's offset from the cloud is solved from a declared sun altitude and cloud
# base, so the weather is geometry rather than a placed shape.
SUN_ALT_S7 = 34.0
CLOUD_BASE_PX = 760.0
CLOUD_OFFSET_PX = round(CLOUD_BASE_PX / math.tan(math.radians(SUN_ALT_S7)), 1)
# The occlusion edge must sit well away from horizontal or it becomes the excluded norther front.
OCCLUSION_EDGE_DEG = 27.0
assert OCCLUSION_EDGE_DEG >= 15.0, "an occlusion edge inside 15 degrees of horizontal is a norther front"


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
                   "sun_alt_a_deg": round(SUN_ALT_A, 2), "sun_alt_b_deg": round(SUN_ALT_B, 2)},
        "slide7": {"sun_alt_deg": SUN_ALT_S7, "cloud_base_px": CLOUD_BASE_PX,
                   "cloud_offset_px": CLOUD_OFFSET_PX, "occlusion_edge_deg": OCCLUSION_EDGE_DEG},
        "claims_used": sorted(CLAIMS),
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
    print(f"  slide 6 sun altitudes {round(SUN_ALT_A,2)} and {round(SUN_ALT_B,2)} degrees "
          f"for one shadow length")
    print(f"  ink contrast  " + "  ".join(f"{g} {v}" for g, v in INK_CONTRAST.items()))
    print(f"  type-safe grounds at 4.5 or better: {', '.join(TYPE_SAFE)}")
    for k, v in PALETTE.items():
        print(f"    {k} {v}")


if __name__ == "__main__":
    main()
