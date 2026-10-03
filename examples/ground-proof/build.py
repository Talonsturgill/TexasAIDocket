"""Builds the ground-proof compares from three renders of the same archived slides.

MEASUREMENT, NOT A TEMPLATE. Every panel is a shipped deck's own slide HTML from runs/carousel/,
rendered unchanged through three engines: `main` before 2026-10-03, item 1 (the worn ground and
the receiving surface) and items 1 and 2 (plus PCSS shadows, the shadow box fade and the kit
highway at grade). The frames differ in the engine alone, which is the only honest way to show
what the engine changed. Render each set with the engine checked out at that state:

    python3 .claude/skills/carousel-engine/render.py --slides-dir runs/carousel/2026-10-03/slides --out-dir <set>/1003

for 2026-10-03, 2026-10-02, 2026-09-30 and 2026-09-29, then

    python3 examples/ground-proof/build.py --main <set> --item1 <set> --item12 <set>

Writes `deck-<date>.webp` (every frame at the 432 px thumb, main | item 1 | items 1 and 2),
`zoom-ground.webp`, `zoom-shadows.webp` and `zoom-worse.webp` (regions at full size, 1:1 with the 2160 px
render, the last the regions on the frames the blind graders marked down) and
`full-<deck>-<frame>.webp` (two whole frames at full size, main | items 1 and 2).
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
DECKS = [("1003", "2026-10-03", "carousel no. 41, stormFront, concrete court and Blackland soil"),
         ("1002", "2026-10-02", "carousel no. 40, golden hour roof and interiors"),
         ("0930", "2026-09-30", "carousel no. 38, overcast, a school lawn"),
         ("0929", "2026-09-29", "carousel no. 37, desert, caliche")]
# (label, deck, slide, box in 2160 x 2700 render pixels), the regions each item changed most
ZOOM_GROUND = [("no. 41 frame 1, the court at the van's tandems", "1003", 1, (300, 1700, 1300, 2500)),
               ("no. 41 frame 6, the court round the rig", "1003", 6, (1100, 1500, 2100, 2300)),
               ("no. 41 frame 9, the court at the person", "1003", 9, (300, 1700, 1300, 2500)),
               ("09-29 frame 1, the worker on the deck's own pad", "0929", 1, (1150, 1650, 1650, 1950)),
               ("09-30 frame 4, the lawn at the desks", "0930", 4, (60, 1700, 1460, 2350))]
ZOOM_SHADOWS = [("no. 41 frame 8, light inside the wall's shadow", "1003", 8, (560, 1100, 1260, 1900)),
                ("no. 41 frame 1, the straps' shadows on the load", "1003", 1, (1300, 1440, 1880, 2140)),
                ("no. 41 frame 5, the door post's shadow down the bay", "1003", 5, (1760, 1180, 2140, 1640)),
                ("no. 41 frame 3, the lamp's shadow on the fascia, against a low sun", "1003", 3, (330, 1500, 940, 1900)),
                ("no. 41 frame 4, the verge polygon and the barrier's cut shadow", "1003", 4, (0, 1650, 2160, 2450)),
                ("no. 41 frame 6, the van's cast, sharp at the foot, soft at the tip", "1003", 6, (300, 1150, 1300, 1950)),
                ("09-29 frame 2, long golden hour casts", "0929", 2, (0, 1500, 1400, 2300)),
                ("no. 40 frame 9, blocks of light in the paper stacks' shadow", "1002", 9, (880, 1820, 2160, 2280)),
                ("no. 40 frame 7, streaks down the glass", "1002", 7, (120, 1260, 1000, 2000))]
# the regions the blind graders named on the frames items 1 and 2 made WORSE, shown as honestly as the
# gains. The fifth field is the pair of sets: (0, 1) is main | item 1, (1, 2) is item 1 | items 1 and 2
ZOOM_WORSE = [("no. 40 frame 6, item 1, the adopted sill a few levels darker in the lower left", "1002", 6, (0, 1800, 1080, 2700), (0, 1)),
              ("no. 41 frame 1, grain in the wide penumbrae under the roof and the load bar", "1003", 1, (1300, 1440, 1880, 2140)),
              ("no. 41 frame 6, the load bar's shadow sharp on the cartons, teeth where the wall's shadow crosses their tops", "1003", 6, (1180, 1560, 1840, 2160)),
              ("no. 41 frame 5, shadows the old filter bled away, crescents in the hubs and the door post down the bay", "1003", 5, (1500, 1180, 2060, 1740)),
              ("no. 40 frame 4, the vial's shadow starts off its base (the deck's own spot bias, see the README)", "1002", 4, (1380, 1880, 2160, 2460))]


def font(size):
    for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(f, size)
        except OSError:
            pass
    return ImageFont.load_default()


def deck_sheet(sets, key, date, note):
    W, H, gap = 432, 540, 12
    trip = 3 * W + 2 * 4
    cols = 2
    frames = sorted(p.name for p in (sets[0] / key).glob("slide-*.png"))
    rows = (len(frames) + cols - 1) // cols
    head = 70
    sheet = Image.new("RGB", (cols * trip + (cols - 1) * gap + 2 * gap, head + rows * (H + 34) + gap), (246, 245, 242))
    d = ImageDraw.Draw(sheet)
    d.text((gap, 14), f"{date}  {note}", fill=(20, 20, 20), font=font(26))
    d.text((gap, 44), "each frame: main | item 1, the worn ground | items 1 and 2, PCSS and the highway at grade", fill=(70, 70, 70), font=font(20))
    for i, f in enumerate(frames):
        x = gap + (i % cols) * (trip + gap)
        y = head + (i // cols) * (H + 34)
        d.text((x, y + 4), f[6:8], fill=(20, 20, 20), font=font(20))
        for j, s in enumerate(sets):
            p = s / key / f
            if p.exists():
                sheet.paste(Image.open(p).convert("RGB").resize((W, H), Image.LANCZOS), (x + j * (W + 4), y + 30))
    return sheet


def zoom_sheet(sets, regions, title, pair):
    gap, lab = 12, 40
    tiles = []
    for r in regions:
        label, key, n, box = r[:4]
        crops = [Image.open(sets[i] / key / f"slide-{n:02d}.png").convert("RGB").crop(box) for i in (r[4] if len(r) > 4 else pair)]
        w, h = crops[0].size
        t = Image.new("RGB", (len(crops) * w + (len(crops) - 1) * 6, h + lab), (246, 245, 242))
        ImageDraw.Draw(t).text((4, 8), label, fill=(20, 20, 20), font=font(24))
        for j, c in enumerate(crops):
            t.paste(c, (j * (w + 6), lab))
        tiles.append(t)
    W = max(t.width for t in tiles) + 2 * gap
    Hh = sum(t.height for t in tiles) + gap * (len(tiles) + 1) + 50
    sheet = Image.new("RGB", (W, Hh), (246, 245, 242))
    ImageDraw.Draw(sheet).text((gap, 12), title, fill=(20, 20, 20), font=font(26))
    y = 50
    for t in tiles:
        sheet.paste(t, (gap, y)); y += t.height + gap
    return sheet


# whole frames at full size, main | items 1 and 2
FULL = [("1003", 8), ("0929", 1)]


def full_sheet(sets, key, n):
    a = Image.open(sets[0] / key / f"slide-{n:02d}.png").convert("RGB")
    b = Image.open(sets[2] / key / f"slide-{n:02d}.png").convert("RGB")
    s = Image.new("RGB", (a.width * 2 + 12, a.height), (246, 245, 242))
    s.paste(a, (0, 0)); s.paste(b, (a.width + 12, 0))
    return s


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--main", required=True); ap.add_argument("--item1", required=True); ap.add_argument("--item12", required=True)
    a = ap.parse_args()
    sets = [Path(a.main), Path(a.item1), Path(a.item12)]
    for key, date, note in DECKS:
        deck_sheet(sets, key, date, note).save(HERE / f"deck-{date}.webp", quality=74, method=6)
    zoom_sheet(sets, ZOOM_GROUND, "Item 1, the worn ground and the receiving surface: main | item 1, 1:1", (0, 1)).save(
        HERE / "zoom-ground.webp", quality=80, method=6)
    zoom_sheet(sets, ZOOM_SHADOWS, "Item 2, PCSS and the highway at grade: item 1 | items 1 and 2, 1:1", (1, 2)).save(
        HERE / "zoom-shadows.webp", quality=80, method=6)
    zoom_sheet(sets, ZOOM_WORSE, "What the blind graders marked down, before | after, 1:1", (1, 2)).save(
        HERE / "zoom-worse.webp", quality=80, method=6)
    for key, n in FULL:
        full_sheet(sets, key, n).save(HERE / f"full-{key}-{n:02d}.webp", quality=82, method=6)
    for p in sorted(HERE.glob("*.webp")):
        print(p.name, p.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
