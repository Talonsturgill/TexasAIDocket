# Carousel art atelier

Six executable construction studies for the `carousel-art-studio` skill. They prove larger
visual ideas — camera, depth, light, material, evidence and typography — with the same offline
browser stack used in production.

They are **not slide templates** and do not contain reusable story claims. Copy a mechanism,
never a composition, palette, object or lockup.

## Render

```bash
python3 .claude/skills/carousel-engine/render.py \
  --slides-dir examples/art-atelier/slides \
  --out-dir out/art-atelier/tmp/render

python3 .claude/skills/carousel-engine/qa.py \
  --render-dir out/art-atelier/tmp/render

python3 .claude/skills/carousel-engine/assemble.py \
  --slides-dir examples/art-atelier/slides \
  --render-dir out/art-atelier/tmp/render \
  --out-dir out/art-atelier/tmp/final \
  --title "Texas AI Docket — code atelier"
```

Inspect the 1080×1350 renders, the 432-pixel thumbnails and the contact sheet. See
`.claude/skills/carousel-art-studio/references/atelier.md` for the construction index and the
rules for learning from these studies.
