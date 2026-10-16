"""Cut and verify native-size review tiles without changing the full-frame pixels.

Adapted from alaskaaicarousels render.py at
03da46445a18974351cc6e74835679b3de2c89c8.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

TILE = (1080, 900)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def regions(width, height):
    for row, y in enumerate(range(0, height, TILE[1]), 1):
        for col, x in enumerate(range(0, width, TILE[0]), 1):
            yield row, col, [x, y, min(width, x + TILE[0]), min(height, y + TILE[1])]


def write(png: Path, scale: float) -> dict:
    """Cut every native pixel once; publish the manifest only after every tile exists."""
    try:
        from PIL import Image
        if not math.isfinite(scale) or scale <= 0:
            raise ValueError("scale must be positive and finite")
        crops = png.parent / "crops"
        crops.mkdir(exist_ok=True)
        manifest = crops / (png.stem + ".json")
        manifest.unlink(missing_ok=True)
        for old in crops.glob(png.stem + "-r*c*.png"):
            old.unlink()
        tiles = []
        with Image.open(png) as image:
            size = list(image.size)
            for row, col, rect in regions(*size):
                path = crops / f"{png.stem}-r{row}c{col}.png"
                image.crop(rect).save(path, compress_level=1)
                tiles.append({"file": path.name, "px": rect,
                              "design": [round(v / scale) for v in rect], "sha256": sha(path)})
        record = {"frame": png.name, "frame_sha256": sha(png), "frame_px": size,
                  "scale": scale, "tile_px": list(TILE), "tiles": tiles}
        pending = manifest.with_suffix(".tmp")
        pending.write_text(json.dumps(record, indent=1))
        pending.replace(manifest)
        return {"ok": True, "dir": "crops", "tiles": len(tiles)}
    except Exception as exc:
        return {"ok": False, "reason": f"{type(exc).__name__}: {exc}"[:160]}


def read(render_dir: Path, slide: int) -> dict:
    """Return a complete, current set, or one diagnostic with no partial tile list."""
    from PIL import Image
    frame = Path(render_dir) / f"slide-{slide:02}.png"
    crops = Path(render_dir) / "crops"
    manifest = crops / (frame.stem + ".json")
    if not frame.exists() or not manifest.exists():
        return {"missing": f"slide {slide:02}: render.py must generate the native crops"}
    try:
        record = json.loads(manifest.read_text())
        if record["frame"] != frame.name or record["frame_sha256"] != sha(frame):
            raise ValueError("source image changed after the tiles were cut")
        with Image.open(frame) as image:
            size = list(image.size)
        scale = record["scale"]
        if record["frame_px"] != size or not math.isfinite(scale) or scale <= 0:
            raise ValueError("invalid image size or scale")
        expected = list(regions(*size))
        if len(record["tiles"]) != len(expected):
            raise ValueError("incomplete tile coverage")
        tiles = []
        for tile, (row, col, rect) in zip(record["tiles"], expected):
            name = f"{frame.stem}-r{row}c{col}.png"
            design = [round(v / scale) for v in rect]
            if tile["file"] != name or tile["px"] != rect or tile["design"] != design:
                raise ValueError("tile order or region does not cover the current frame")
            path = crops / name
            if not path.exists() or tile["sha256"] != sha(path):
                raise ValueError(f"missing or changed tile {name}")
            tiles.append({"path": str(path.resolve()), "px": rect, "design": design})
        return {"tiles": tiles}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {"stale": f"slide {slide:02}: {exc}; re-render it to refresh every crop"}
