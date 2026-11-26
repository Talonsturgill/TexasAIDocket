# Slide brief, frame 5 of 9, 2026-11-25 (BESPOKE, LOOK V2, tone PEOPLE)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-25/storyboard.md` (your dossier is its slide 6 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-25/claims.json`.

## The story in one line
UTMB Health announced on November 19th that AI now supports its lung cancer screening work. A system developed with Bunkerhill reviews radiology reports, and any nodule on a scan that includes part of the lungs is flagged for patient navigator Amanda Rodriguez, whose dashboard computes a validated risk score so she can decide which follow up comes first. Dr. Shawn Nishi calls the AI an assistant, not a decision maker. The turn: roughly two thirds of the nodules the program found came from patients who were not having lung cancer screening. The scan was for something else. Dr. Nishi's patient in her 20s had a scan after a car accident, a nodule was found incidentally, a biopsy showed lung cancer and she had surgery for cure, and she named seven or eight relatives with cancer, a hereditary disease. The deck's argument is THE SECOND FINDING: a scan drawn as a field covering part of a body that can hold a gold bead nobody ordered it to find, and that bead's path from report to a person's hand. RULES: no accuracy figure, no count of patients, scans or nodules, no after adoption timing exists and none may be implied. The AI flags, a person reviews, doctors decide; no frame shows the AI deciding, diagnosing or treating. No real CT image, no real patient, no likeness of Dr. Nishi, Rodriguez or the patient, no legible screen, no interface, no logo, no UTMB or Bunkerhill mark. People are three quarters away, at distance or cropped, no face square to camera, no face over 2 percent of the frame. No crash, injury, blood, bed or surgery is ever drawn. Not a scare deck.

## The beat
WHO DECIDES. Know: AI is an assistant, people stay at the center. c15 c16.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): one continuous oak counter seen high three quarter axonometric in a bright workroom, at its far left a small brushed steel reading bridge glowing cyan over a drawer of white cards with gold flags rising behind it, in the middle two plum sleeved hands setting nine flagged cards into an oak rack, at the right a white coat cuff and a pen resting over the front card, three plum pills reading flags, checks and ranks, decides.
Camera and largest object: chassis oak counter with reading bridge, card rack and three cropped kit hands, OrthographicCamera, TXT.interior workroom
Data in art: card count in the rack equals FIG.units and periwinkle tab count equals FIG.of_nine, read in the slide's own code
Planned type seat: see the dossier's composition bands. Put the type where YOUR picture leaves quiet.

**As built after repairs:** one light oak counter across the frame on a bright apricot sweep, reader head with a cyan beam at the left, plate rail and sleeves in the middle, doctor's cuff and pen at the right, type on the plum cabinet front.

## The copy (fixed)
- kicker: `Who decides`
- counter: `06 / 09`
- headline (verbatim): `It flags. People decide.`
- dek (verbatim, except the one exception below): `Dr. Nishi calls the AI an assistant, not a decision maker. The release says people stay at the center while it works in the background.`
- labels: ["flags", "checks and ranks", "decides"]
- claim ids (the `src` furniture): `c15 c16 c31 c11 c14`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "cards drawn to illustrate") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate" where it is, add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"units": 9, "of_nine": 6}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-25-secondfind-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `people`, accent gold `#ffc83d` meaning A NODULE FLAGGED FOR A PERSON and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-25/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture; its render is `out/2026-11-25/tmp/probe/render/slide-01.png`). Use `CH.develop(await TXT.snapshot(R, {}), gl)`, then seat type with `CH.seat`, footer with `TXLOOK.footWash`, and `TXDECK.finish(cx)` last.
- accent on this frame: YES, #ffc83d, on the bead, flag or flagged line only.
- MATERIAL CODE, held on every frame that draws it: periwinkle `CH.OTHER` means a scan ordered for something else, frosted white `CH.SCREEN` means a screening exam (`CH.acrylicMat(K,'other'|'screen')`).
- PEOPLE tone: periwinkle sky over an apricot horizon, an apricot key, plum and violet in every shadow, never black. No dark room, no black type band. Grey mid tones fail value_register, so surfaces take saturated colour.
- chassis models (read their doc comments in the chassis): `glass_lung` (option scale; userData.anchor(side,u,v) gives a point inside a lung), `scan_slab` (w,h,d, kind 'other'|'screen'), `nodule_bead` (r), `manila_folder` (thick, tab, tabAt, dog), `chart_cart`, `age_rule` (length, span, step, from, to; userData.at(u)), `ct_gantry` (trim, extend, pillow), `card_rack` (slots; userData.slot(i)), `oak_counter`, `reading_bridge`. Helpers `CH.glassMat`, `CH.acrylicMat`, `CH.goldMat`, `CH.paperTex(THREE, seed, lines, flagLine)`, `CH.ortho`, `CH.leader`, `CH.pin`, `CH.project`, `CH.studioOpts`, `CH.rigSpec`, `CH.rigOpts`. Plus every kit model in ARSENAL (person with poses, crowd, desk, office_chair, monitor, index_card_drawer, document_stack, workstation_cart, live_oak, yard, filing_cabinet and more). The chassis models are BASIC geometry: the glass lung in particular is two smooth pods; REFINE their look inside your own frame (lobe fissures, more parts, materials, wear) but never edit the chassis file. Anything else you need you build in your own frame, at true size in metres, never as a bare primitive.
- a TXBENCH relief file shape to copy (never its picture): `runs/carousel/2026-11-22/slides/slide-04.html` (CH.bootFlat, TXBENCH.relief under the chassis key).
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `out/2026-11-25/slides/slide-06.html`
- your render dir: `out/2026-11-25/work/render-06` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-25/slides --out-dir out/2026-11-25/work/render-06 --only 6 --timeout 300000`
- your concepts: `out/2026-11-25/briefs/slide-06.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-25/`; never write under any .claude directory.

## The neighbours
- frame before: A PERSON CHECKS. Know: every flag goes to navigator Amanda Rodriguez and a risk score orders her queue. c11 c12 c13 c14.
- frame after: HER 20s. Know: Dr. Nishi's patient was in her 20s, decades before screening age. c18 c19 c20 c28.

## What already ran, so do not repeat it
November 24th drew a stitched aerial Gulf Coast subdivision, damaged roofs, a downed oak, a responder at a tailgate (wonder). November 22nd drew cutaway exam rooms, a stethoscope wall, studio benches, exam paper and an open binder (explainer). November 21st drew a tracked rover on rubble in a staged disaster town (win). November 20th drew a survey quadcopter on a ridge and a clay tablet (people). Judges lately charged: an orange boulder with spikes, rims read as gutters, a smooth mannequin operator, a close that repeats the cover, a distant isometric dollhouse, toy cubes on a flat sweep with labels doing the explaining, a part floating above its body, the top 40 percent flat and empty, flat face on elevations, top down trays reading as charts, capsule people and soft kit hands, missing contact shadows, sky banding behind headlines, uncountable units at feed size, a hero under a tenth of the frame. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
