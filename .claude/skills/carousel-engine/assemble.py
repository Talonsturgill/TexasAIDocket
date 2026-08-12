#!/usr/bin/env python3
"""assemble.py — build the deliverables from rendered slides.

Produces:
  1. carousel.pdf   — VECTOR-TEXT pdf (Chromium print engine, fonts embedded).
                      LinkedIn recompresses uploads; raster text blurs, vector
                      text survives, and the text layer feeds LinkedIn's
                      semantic ranker + accessibility mode. Falls back to
                      img2pdf (raster) only if the print path fails.
  2. contact_sheet.png — every slide side by side in order, for flow review.
  3. thumbs/slide-XX-thumb.png — 432px-wide feed-size previews for the
                      pixel critic's small-size legibility pass.

Usage:
  python .claude/skills/carousel-engine/assemble.py \
      --slides-dir out/run/slides --render-dir out/run/render \
      --out-dir out/run/final [--title "Document title"]

Exit 0 on success. Writes assemble_report.json with sizes + mode used.
"""

import argparse
import glob
import io
import json
import re
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[3]
MONO_FONT = REPO_ROOT / "assets" / "fonts" / "JetBrainsMono-Medium.ttf"


def vector_pdf(slides_dir: Path, out_pdf: Path, width: int, height: int, title: str) -> bool:
    """Print each slide HTML to a single-page vector PDF via Chromium, merge with pypdf."""
    try:
        from playwright.sync_api import sync_playwright
        from pypdf import PdfReader, PdfWriter
    except ImportError as e:
        print(f"vector pdf unavailable ({e}); falling back to raster", file=sys.stderr)
        return False

    sys.path.insert(0, str(Path(__file__).parent))
    from render import launch_chromium, resolve_html  # reuse fallback + token logic

    slides = sorted(slides_dir.glob("slide-*.html"))
    if not slides:
        return False
    tmp = out_pdf.parent / ".pdf_pages"
    tmp.mkdir(parents=True, exist_ok=True)
    resolved_dir = out_pdf.parent / ".resolved_pdf"
    resolved_dir.mkdir(parents=True, exist_ok=True)
    try:
        with sync_playwright() as p:
            browser = launch_chromium(p)
            for s in slides:
                resolved = resolve_html(s, resolved_dir)
                page = browser.new_page(viewport={"width": width, "height": height},
                                        device_scale_factor=2)
                page.goto(resolved.as_uri(), wait_until="load", timeout=45000)
                page.evaluate("() => document.fonts.ready.then(() => true)")
                if page.evaluate("() => typeof window.renderReady !== 'undefined'"):
                    page.evaluate("() => Promise.race([window.renderReady, "
                                  "new Promise((_, rej) => setTimeout(() => rej('timeout'), 30000))])")
                else:
                    page.wait_for_timeout(400)
                page.pdf(path=str(tmp / (s.stem + ".pdf")),
                         width=f"{width}px", height=f"{height}px",
                         print_background=True, page_ranges="1",
                         margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
                page.close()
            browser.close()

        writer = PdfWriter()
        for s in slides:
            reader = PdfReader(str(tmp / (s.stem + ".pdf")))
            writer.add_page(reader.pages[0])
        # recompress large opaque bitmaps to JPEG; alpha (SMask) images are
        # left alone so overlays keep their transparency
        for pg in writer.pages:
            try:
                for img in pg.images:
                    try:
                        xobj = img.indirect_reference.get_object()
                        if "/SMask" in xobj or len(img.data) < 400_000:
                            continue
                        if img.image.mode not in ("RGB", "L"):
                            continue
                        img.replace(img.image, quality=88)
                    except Exception:
                        continue
            except Exception:
                continue
        meta = {"/Title": title, "/Author": "Texas AI Docket",
                "/Creator": "Texas AI Docket carousel engine"}
        writer.add_metadata(meta)
        with open(out_pdf, "wb") as f:
            writer.write(f)
        return out_pdf.exists() and out_pdf.stat().st_size > 20_000
    except Exception as e:
        print(f"vector pdf failed ({e}); falling back to raster", file=sys.stderr)
        return False
    finally:
        # Cleanup must never decide the outcome. An exception raised in here
        # REPLACES the `return False` the except block just computed, so main()
        # never reaches raster_pdf() and the run ends with a traceback and no
        # PDF at all. resolve_html writing anything nested, or a leftover
        # directory from an interrupted run, is enough: unlink raises
        # IsADirectoryError, or rmdir raises OSError on a non-empty dir.
        # CLAUDE.md says images beat a broken PDF, and this path was yielding
        # neither.
        for d in (tmp, resolved_dir):
            shutil.rmtree(d, ignore_errors=True)


def raster_pdf(pngs, out_pdf: Path) -> bool:
    import img2pdf
    jpegs = []
    for p in pngs:
        im = Image.open(p).convert("RGB")
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=92)
        jpegs.append(buf.getvalue())
    out_pdf.write_bytes(img2pdf.convert(jpegs))
    return out_pdf.exists()


def contact_sheet(pngs, out_png: Path, col_w=300, per_row=5, gutter=14, label_h=34):
    font = ImageFont.truetype(str(MONO_FONT), 20) if MONO_FONT.exists() else ImageFont.load_default()
    cells = []
    for p in pngs:
        im = Image.open(p)
        h = int(im.height * col_w / im.width)
        cells.append(im.resize((col_w, h), Image.LANCZOS))
    if not cells:
        return
    cell_h = max(c.height for c in cells) + label_h
    rows = (len(cells) + per_row - 1) // per_row
    cols = min(per_row, len(cells))
    W = cols * col_w + (cols + 1) * gutter
    H = rows * cell_h + (rows + 1) * gutter
    sheet = Image.new("RGB", (W, H), (14, 16, 22))
    d = ImageDraw.Draw(sheet)
    for i, c in enumerate(cells):
        r, k = divmod(i, per_row)
        x = gutter + k * (col_w + gutter)
        y = gutter + r * (cell_h + gutter)
        sheet.paste(c, (x, y))
        d.text((x + 4, y + c.height + 6), f"{i + 1:02d}", fill=(255, 199, 44), font=font)
    sheet.save(out_png)


def thumbnails(pngs, thumbs_dir: Path, width=432):
    thumbs_dir.mkdir(parents=True, exist_ok=True)
    outs = []
    for p in pngs:
        im = Image.open(p)
        h = int(im.height * width / im.width)
        t = im.resize((width, h), Image.LANCZOS)
        out = thumbs_dir / (Path(p).stem + "-thumb.png")
        t.save(out)
        outs.append(str(out))
    return outs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slides-dir", required=True, help="dir of slide-*.html (for vector pdf)")
    ap.add_argument("--render-dir", required=True, help="dir of rendered slide-*.png")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--title", default="Texas AI Docket — Carousel")
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1350)
    args = ap.parse_args()

    render_dir = Path(args.render_dir).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    pngs = sorted(glob.glob(str(render_dir / "slide-*.png")))
    if not pngs:
        print("FAIL: no rendered slide-*.png found", file=sys.stderr)
        sys.exit(1)

    pdf_path = out_dir / "carousel.pdf"
    mode = "vector"
    if not vector_pdf(Path(args.slides_dir).resolve(), pdf_path, args.width, args.height, args.title):
        mode = "raster-fallback"
        raster_pdf(pngs, pdf_path)

    sheet_path = out_dir / "contact_sheet.png"
    contact_sheet(pngs, sheet_path)
    thumbs = thumbnails(pngs, out_dir / "thumbs")

    report = {
        "pdf": str(pdf_path), "pdf_mode": mode,
        "pdf_bytes": pdf_path.stat().st_size,
        "pdf_mb": round(pdf_path.stat().st_size / 1e6, 2),
        "slides": len(pngs),
        "contact_sheet": str(sheet_path),
        "thumbs": thumbs,
        "title": args.title,
    }
    (out_dir / "assemble_report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    if report["pdf_mb"] > 90:
        print("WARN: pdf near LinkedIn's 100MB cap", file=sys.stderr)
    if mode != "vector":
        print("WARN: raster fallback used — text will not survive LinkedIn "
              "compression as well; investigate", file=sys.stderr)


if __name__ == "__main__":
    main()
