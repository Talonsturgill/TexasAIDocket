# Look v2 proof

The shipped 2026-11-14 deck (Texas Tech's AI computing cluster award, tx-2026-0247) rebuilt on look v2,
explainer tone. Same story, same headlines and dek, same figures read from the same `window.FIG` lines.
Only light, colour, materials and the type's seat changed.

- `2026-11-14/slides/` the nine frames. Spatial frames call `TXT.studio(R, CH.studioOpts(...))` where the
  shipped deck called `TXT.interior(R, CH.roomOpts(...))`, and drop `TXT.stage` and `TXT.weather`.
  Relief frames start from `TXLOOK.sky2d`, take `TXLOOK.reliefLight()` and give their materials tone albedos.
- `assets/js/deck/2026-11-14-waferbench-v2.js` the chassis: the shipped chassis with `look: "v2"`,
  `tone: "explainer"`, `grade: TXLOOK.grade("explainer")`, the `v2explainer` world, a coloured mirror
  environment and the type seated on the tone's own deep hue.
- `2026-11-14/before_after.webp` the shipped frames above, the proof below.

Measured at 432 x 540 (value_register.py):

| | deck median L* | median chroma | vivid share (C* 30+) | near black share |
|---|---|---|---|---|
| shipped Nov 14 | 5.6 | 2.2 | 0.02 | 0.62 |
| look v2 proof | 49.7 | 26.9 | 0.54 | 0.04 |

Re-render: `python3 .claude/skills/carousel-engine/render.py --slides-dir examples/look-v2-proof/2026-11-14/slides --out-dir /tmp/v2`
then `python3 scripts/carousel/value_register.py --render-dir /tmp/v2 --look v2`.
