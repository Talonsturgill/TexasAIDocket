# Slide brief, frame 2 of 9, 2026-11-17 (BESPOKE, LOOK V2, tone WATCH)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-17/storyboard.md` (your dossier is its slide 2 yaml block, which carries your acceptance list). Claims are `out/2026-11-17/claims.json`.

## The story in one line
The Texas Education Agency's automated scoring engine reads the written answers on English STAAR tests first, and districts asked 64,489 times this spring for a person to read one again. STAAR is answered ONLINE: any answer shown is greeked TYPED text, never handwriting, never legible. No real student, essay, school, booklet, STAAR logo or TEA seal.

## The beat
Why a machine. Make TEA's reason physical, a workload that grew six to seven fold.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): a relief cliff of paper strata, one thin band at the base for the old load and a mass six to seven times as thick above it, the top band lighter for the range. Camera: MEDIUM, orthographic elevation relief raked from the upper left.

## The copy (fixed)
- kicker: `Why a machine`
- counter: `02 / 09`
- headline (verbatim): `Six to seven times the written answers`
- dek (verbatim, except the one exception below): `TEA says STAAR now brings 6 to 7 times more written answers a year. Scoring them all by hand would cost $15 million to $20 million more a year and take four to five times as many scorers.`
- labels (optional, keep any you use verbatim): []
- claim ids (the `src` furniture): `c19 c10 c11`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one sheet stands for one request") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"training_responses": 3000}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-17-scorebench-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `watch`, accent dusk gold `#e0956a` meaning A PERSON'S SCORE and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `runs/carousel/2026-11-16/slides/slide-01.html` loads its chassis (copy that file's head and boot shape, never its picture; swap the chassis path).
- this frame MAY carry the accent on the guide tabs of the human scored cards only.
- WATCH tone rule: keep studio and room floors violet rose, never the coral floor, so dusk gold never fights an orange room. Shadows lean violet, never black.
- chassis models for this frame: card_cabinet (with a kit index_card_drawer in userData.drawerAt). All four (scoring_engine, response_sheet, card_cabinet, paper_column) are installed by CH.boot; read their notes at the top of the chassis. Plus every kit model in ARSENAL.
- a chassis probe render (`out/2026-11-17/tmp/probe/render/slide-01.png`) shows the models build, and that under the watch coral key cream paper drifts to salmon; tune your key and the paper albedo so paper reads as paper.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-17/slides/slide-02.html`
- your render dir: `out/2026-11-17/work/render-02` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-17/slides --out-dir out/2026-11-17/work/render-02 --only 2 --timeout 300000`
- your concepts: `out/2026-11-17/briefs/slide-02.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time.

## The neighbours
- frame before: Read by a machine first. Put the whole story in one object, a machine reading a child's written answer before any person does.
- frame after: What it learned from. Show what the machine is made of, thousands of judgments people already made, kept shut away.

## What already ran, so do not repeat it
November 15th (people tone) drew a student desk from above and a gym of 100 desks from bleachers, so NO school desks, gyms, rows of desks or bleachers. November 16th drew a gold ribbon under an open caliper on a studio sweep and dark instruments. November 14th drew wafers in a quartz boat and a county relief. Judges lately charged: walls filling the top half, subjects cropped, sky banding behind headlines, wavy kit wood, an orange room fighting the accent, flat face-on squares with typed labels, type plates reading as UI, top-down trays reading as charts, capsule people and mannequins, soft kit hands, uncountable blocks at feed size. The fourteen decks before November 14th put the headline top left at y 150 on every frame; place your type where THIS picture leaves quiet. Integrity: TEA's design (25 percent to people) is dated December 2023 and March 2024; never imply the engine got any answer wrong; 13,300 and 5,100 are floors.
