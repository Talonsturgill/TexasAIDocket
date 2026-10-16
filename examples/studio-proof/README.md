# Material relief renderer study

Three native HTML studies use the frozen figures from Texas no. 52 to exercise `TXBENCH.relief`.
They show a computed mark count, a cut scale and a multi-material inset. This is an engineering
proof. It is not a daily release, an approved treatment or an independent artwork score.

The renderer is adapted from Alaska's `akbench.js`. Geometry, copy and materials here are Texas
inputs. Each slide authors its own height and material functions; the shared chassis supplies
only the light, palette and finish. All visible type remains DOM text.

```bash
python3 examples/studio-proof/build.py
python3 .claude/skills/carousel-engine/render.py \
  --slides-dir examples/studio-proof/slides --out-dir out/studio-proof/render
python3 .claude/skills/carousel-engine/qa.py --render-dir out/studio-proof/render
node tests/txbench.mjs
python3 tests/carousel_studio.py
```

The native renderer tests verify deterministic pixels, actual cast shadows, inherited light,
invalid geometry and a flat carrier that casts no shadow. The Python regression tests cover
hardest-frame selection, changed-image review binding, phase-clock resumption and the real
calendar encode that lost a component after passing PSNR.
