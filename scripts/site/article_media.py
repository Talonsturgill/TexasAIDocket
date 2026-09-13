"""Responsive article images derived from shipped artwork without rewriting that artwork.

The source files are often twice the displayed dimensions. Each build publishes smaller
derivatives and keeps a content-addressed scratch cache so reproducibility checks do not
repeat every encode. A cache miss always has the same committed source and encoder settings.
"""
from __future__ import annotations

import hashlib
import html
import io
import math
from pathlib import Path

from PIL import Image, ImageChops, ImageStat, __version__ as PILLOW_VERSION, features

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "out" / "article-media" / "tmp"
WIDTHS = (540, 1080)
COVER_WIDTHS = (320, 640, 1080)
QUALITY_LADDER = (82, 88, 92, 96)
QUALITY_FLOOR_DB = 40
ENCODER = f"v1-pillow{PILLOW_VERSION}-webp{features.version('webp')}"


def psnr(source: Image.Image, result: Image.Image) -> float:
    rms = ImageStat.Stat(ImageChops.difference(source, result)).rms
    mse = sum(x * x for x in rms) / len(rms)
    return math.inf if mse == 0 else 20 * math.log10(255) - 10 * math.log10(mse)


def encode(source: Path, width: int) -> bytes:
    """Keep the existing shipping quality floor against the resized source.

    Lossless is the fallback when texture or fine type cannot clear that floor. Resizing is
    the intended change; comparing the decode against the resized source measures only the
    additional loss introduced by encoding.
    """
    with Image.open(source) as opened:
        image = opened.convert("RGB")
        width = min(width, image.width)
        height = round(image.height * width / image.width)
        image = image.resize((width, height), Image.Resampling.LANCZOS)
        for quality in QUALITY_LADDER:
            stream = io.BytesIO()
            image.save(stream, "WEBP", quality=quality, method=6)
            data = stream.getvalue()
            with Image.open(io.BytesIO(data)) as decoded:
                if psnr(image, decoded.convert("RGB")) >= QUALITY_FLOOR_DB:
                    return data
        stream = io.BytesIO()
        image.save(stream, "WEBP", lossless=True, method=6)
        return stream.getvalue()


def derivative(source: Path, width: int) -> tuple[bytes, int, int]:
    raw = source.read_bytes()
    key = hashlib.sha256(raw + f"{ENCODER}:{width}".encode()).hexdigest()
    cached = CACHE / f"{key}.webp"
    if cached.exists():
        data = cached.read_bytes()
    else:
        data = encode(source, width)
        CACHE.mkdir(parents=True, exist_ok=True)
        # Separate build processes may share this cache. An atomic rename prevents readers
        # from treating a partially written image as a completed encode.
        import tempfile
        with tempfile.NamedTemporaryFile(dir=CACHE, suffix=".webp", delete=False) as temp:
            temp.write(data)
            temp_path = Path(temp.name)
        temp_path.replace(cached)
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        return data, image.width, image.height


def prepare(runs: list, out: Path) -> None:
    """Write the public derivatives before any page refers to them."""
    for run in runs:
        run["media"] = {}
        for name in run["files"]:
            source = ROOT / "runs" / "carousel" / run["date"] / name
            widths = sorted(set(WIDTHS + (COVER_WIDTHS if name == run["cover"] else ())))
            variants = []
            for width in widths:
                data, actual_width, height = derivative(source, width)
                digest = hashlib.sha256(data).hexdigest()[:12]
                rel = (Path("media/articles") / run["date"] /
                       f"{source.stem}-{actual_width}-{digest}.webp")
                dest = out / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                variants.append({"src": rel.as_posix(), "width": actual_width,
                                 "height": height, "bytes": len(data)})
            run["media"][name] = variants


def image_attrs(run: dict, name: str, depth: int, *, cover: bool = False) -> str:
    """The same responsive selection for article cards and full slides."""
    variants = run.get("media", {}).get(name, [])
    if not variants:
        # Standalone renderer fixtures do not run the asset build. The original is still a
        # real image, and a full build always prepares the derivatives first.
        url = ("https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/main/"
               f"runs/carousel/{run['date']}/{name}")
        return f'src="{html.escape(url, quote=True)}" width="1080" height="1350"'
    wanted = COVER_WIDTHS if cover else WIDTHS
    variants = [v for v in variants if v["width"] in wanted]
    chosen = variants[-1]
    prefix = "../" * depth
    srcset = ", ".join(f"{prefix}{v['src']} {v['width']}w" for v in variants)
    sizes = ("(max-width: 640px) calc(100vw - 48px), (max-width: 980px) 45vw, 360px"
             if cover else "(max-width: 1128px) calc(100vw - 48px), 1080px")
    # All callers lazy-load these images. Let supporting browsers use the actual grid cell
    # width; retain explicit fallback sizes for older engines. The dimensions reserve space.
    return (f'src="{prefix}{chosen["src"]}" srcset="{srcset}" sizes="auto, {sizes}" '
            f'width="{chosen["width"]}" height="{chosen["height"]}" decoding="async"')
