#!/usr/bin/env python3
"""Measure the shipped renders. Every number the ledger and the run record print comes from here.

Round 4's craft judge found the storyboard saying frame 7's falloff is 22.1 L* and artwork.json
saying 17.2 L* for the same feature, and the run brief saying bespoke median 0.1816 where the
ledger recorded 0.2465. Two committed numbers for one measurement, on a product whose first law
is that numbers are computed. So they are computed, once, here, and both files are written from
this output.
"""
import json, pathlib, statistics as st
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[3]
R = ROOT / "out/2026-08-25/render"

def lstar(rgb):
    def f(c):
        c = c / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(x) for x in rgb[:3])
    y = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return 116 * (y ** (1 / 3)) - 16 if y > 0.008856 else 903.3 * y

def frame_median(p):
    im = Image.open(p).convert("RGB").resize((216, 270))
    px = list(im.getdata())
    return st.median([lstar(q) for q in px])

def band_median(p, x0, y0, x1, y1):
    """Median L* of a box given in 1080x1350 CSS px, read off the 2160x2700 render."""
    im = Image.open(p).convert("RGB")
    sx = im.width / 1080.0
    box = im.crop((int(x0*sx), int(y0*sx), int(x1*sx), int(y1*sx)))
    return st.median([lstar(q) for q in box.getdata()])

files = sorted(R.glob("slide-0*.png"))
med = [round(frame_median(p), 1) for p in files]
deck_med, deck_sd = round(st.median(med), 1), round(st.pstdev(med), 1)
junctions = [round(med[i+1] - med[i], 1) for i in range(len(med) - 1)]

# FRAME 7's FALLOFF, measured on the page between the four repeat lines rather than on the type.
# The rows sit at CSS y 624, 762, 900 and 1038; the page is sampled in the gutter under each.
s7 = R / "slide-07.png"
rows = [624, 762, 900, 1038]
gut = [round(band_median(s7, 300, y + 46, 780, y + 90), 1) for y in rows]
falloff = round(gut[-1] - gut[0], 1)

# FRAME 6's two cards against their cork, and the pin's contrast with the paper it sits on.
s6 = R / "slide-06.png"
f6 = {"card_a": round(band_median(s6, 130, 420, 490, 520), 1),
      "card_b": round(band_median(s6, 590, 420, 940, 660), 1),
      # BARE cork, and the sample had to move. Frame 6 grew four route slips over y 720-904, so
      # the old window at 830-880 was measuring slip paper and reporting it as cork: 90.4 where
      # the cork is 60s. Sampled below the foot and above the rail, which is cork and nothing else.
      "cork_under": round(band_median(s6, 120, 1032, 950, 1104), 1)}

out = {"per_frame_median_lstar": med, "deck_median": deck_med, "deck_sd": deck_sd,
       "junctions": junctions,
       "biggest_junction": {"between": junctions.index(min(junctions)) + 1,
                            "delta": min(junctions)},
       "frame7_repeat_gutters": gut, "frame7_falloff_lstar": falloff,
       "frame6": f6,
       "band_declared": [62, 68],
       "frames_inside_declared_band": [i + 1 for i, v in enumerate(med) if 62 <= v <= 68]}
(ROOT / "out/2026-08-25/measurements.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
