#!/usr/bin/env python3
"""Every kit model's DECLARED size against the size it MEASURES at its defaults.

    python3 examples/kit/sizes.py --out out/kit/sizes
    python3 examples/kit/sizes.py --out out/kit/sizes --fix      # rewrite the declared sizes

`size` in a K.define is what ARSENAL.md prints and what a treatment director plans a frame
around, so a declared size that is not the built model is a planning error waiting to happen: a
grain elevator declared 46 m wide built 71 m, and a ranch gate declared 5.4 m built 13.9 m with
its default fencing. Codex caught those one at a time on #359. This measures all of them at once,
in the real engine, and says whether each model's footprint is centred on its origin.

It renders one page per family through the carousel engine's render.py, so it needs the browser
and is a tool, not a CI gate. Exit 0 when every model is within tolerance, 1 otherwise.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
KIT = REPO / "assets" / "js" / "kit"
RENDER = REPO / ".claude" / "skills" / "carousel-engine" / "render.py"

# within 10 percent or 0.5 m on each axis, whichever is looser, and centred within 5 percent
TOL_FRAC, TOL_M, CENTRE_FRAC = 0.10, 0.5, 0.05

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;width:1080px;height:1350px;background:#000}</style></head><body>
<script type="module">
import * as THREE from '@@ASSETS@@/js/three.module.min.js';
import { init } from '@@ASSETS@@/js/txthree.js';
import { initKit } from '@@ASSETS@@/js/txkit.js';
window.renderReady = (async () => {
  const TXT = init(THREE), K = initKit(THREE, TXT), out = [];
  for (const name of __NAMES__) {
    const spec = K.registry[name];
    try {
      const g = K.make(name, { seed: 1 });
      const bb = new THREE.Box3().setFromObject(g), sz = new THREE.Vector3(); bb.getSize(sz);
      out.push({ name, declared: spec.size || null, measured: [sz.x, sz.y, sz.z].map(v => +v.toFixed(2)),
        centre: [(bb.min.x + bb.max.x) / 2, (bb.min.z + bb.max.z) / 2].map(v => +v.toFixed(2)),
        anchored: spec.anchor === 'base' || !!g.userData.heightAt || !!g.userData.attach });
    } catch (e) { out.push({ name, error: String(e) }); }
  }
  console.error('KIT_SIZES ' + JSON.stringify(out));
  return true;
})();
</script></body></html>
"""


def families() -> dict:
    return {p.stem: re.findall(r"K\.define\(\s*['\"]([a-z0-9_]+)['\"]", p.read_text(encoding="utf-8"))
            for p in sorted(KIT.glob("*.js"))}


def measure(out: Path) -> list:
    slides = out / "slides"
    slides.mkdir(parents=True, exist_ok=True)
    for old in slides.glob("slide-*.html"):
        old.unlink()
    for i, (fam, names) in enumerate(families().items(), 1):
        if names:
            (slides / f"slide-{i:02d}.html").write_text(PAGE.replace("__NAMES__", json.dumps(names)), encoding="utf-8")
    subprocess.run([sys.executable, str(RENDER), "--slides-dir", str(slides), "--out-dir", str(out / "render")],
                   check=True, stdout=subprocess.DEVNULL)
    report = json.loads((out / "render" / "render_report.json").read_text(encoding="utf-8"))
    rows = []
    for s in report["slides"]:
        for line in s.get("console_errors", []):
            if line.startswith("KIT_SIZES "):
                rows.extend(json.loads(line[len("KIT_SIZES "):]))
    return rows


def judge(row: dict) -> list:
    if "error" in row:
        return [f"did not build: {row['error']}"]
    d, m, c = row["declared"], row["measured"], row["centre"]
    bad = []
    if not d:
        bad.append("declares no size")
    else:
        for axis, dv, mv in zip("xyz", d, m):
            if abs(dv - mv) > max(TOL_M, TOL_FRAC * mv):
                bad.append(f"{axis} declared {dv} measures {mv}")
    # a pole anchored at its foot, or a model publishing coordinates, keeps its own origin (txkit.js)
    for axis, cv, mv in ([] if row.get("anchored") else zip("xz", c, (m[0], m[2]))):
        if abs(cv) > max(TOL_M, CENTRE_FRAC * mv):
            bad.append(f"footprint centre is {cv} m off the origin on {axis}")
    return bad


def fix(rows: list) -> int:
    """Rewrite each declared size to the measured one, rounded to 0.1 m. Centring is not touched."""
    by_name = {r["name"]: r for r in rows if "measured" in r}
    n = 0
    for p in sorted(KIT.glob("*.js")):
        src = p.read_text(encoding="utf-8")

        def sub(m):
            nonlocal n
            name = m.group(1)
            r = by_name.get(name)
            if not r or not any(x.startswith(("x ", "y ", "z ")) for x in judge(r)):
                return m.group(0)
            n += 1
            return m.group(0).replace(m.group(2), "[" + ", ".join(f"{v:.1f}".rstrip("0").rstrip(".") for v in r["measured"]) + "]")
        src2 = re.sub(r"K\.define\(\s*'([a-z0-9_]+)',\s*\{\s*(?:anchor:[^\n]*\n\s*)?size:\s*(\[[^\]]*\])", sub, src)
        if src2 != src:
            p.write_text(src2, encoding="utf-8")
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--fix", action="store_true", help="rewrite declared sizes to the measured ones")
    a = ap.parse_args()
    rows = measure(Path(a.out))
    (Path(a.out) / "sizes.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
    failing = [(r["name"], judge(r)) for r in rows if judge(r)]
    for name, bad in failing:
        print(f"  {name}: " + "; ".join(bad))
    if a.fix:
        print(f"sizes: rewrote {fix(rows)} declared size(s). Re-run without --fix to confirm")
        return 0
    print(f"sizes: {len(rows) - len(failing)} of {len(rows)} model(s) declare the size they build, centred")
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
