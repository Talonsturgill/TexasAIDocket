# Slide brief, frame 7 of 9, 2026-11-27 (BESPOKE, LOOK V2, tone WATCH)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-27/storyboard.md` (your dossier is its slide 7 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-27/claims.json`.

## The story in one line
On November 18th Texas Comptroller Don Huffines announced proposed amendments to Rule 3.308. They ran in the Texas Register on November 20th. Data processing, taxed since 1987, would mean a provider processing data the customer supplied and handing it back organized. Cloud computing, artificial intelligence and quantum computing would be hosted technology services, not taxable data processing. The comptroller's own fiscal note estimates General Revenue losses of $1,947,310,000 in fiscal year 2027 rising every year to $4,286,040,000 in 2032, local losses of $507,450,000 rising to $1,116,890,000, and calls the effect on the economy insignificant. Comments go to Robin Robinson by December 20th, the earliest adoption date. The deck's argument is ONE SHEET, ONE MILLION: the fiscal note drawn in the document's own material, one sheet of paper per $1,000,000 of the estimate, 500 sheets a ream, 0.1 mm a sheet. RULES: proposed, never adopted, never 'Texas stopped taxing AI'. Every dollar is the comptroller's estimate, never a measured loss. No company, product, logo, real data center, real building or likeness. No partisan framing. No legible text in any art.

## The beat
THE SAME NOTE. Know: the note finds an insignificant effect on the economy and one effect it can't estimate. c38 c39.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): a macro on the fiscal note page lying at the foot of the fiscal 2032 stack, one line highlighted in dusk gold, the stack towering out of focus above and its long violet shadow falling across the highlighted line.
Camera and largest object: MACRO. chassis register_page at macro with fibre bump and dusk gold wax, the fiscal 2032 paper_ream stack out of focus, a coral key about 8 degrees high, the stack's cast shadow across the page, a dog eared corner
Data in art: the out of focus stack's height is FIG.state_fy2032_stack_mm at true scale, and its shadow length follows from it under the low key
Planned type seat: see the dossier's composition bands. Put the type where YOUR picture leaves quiet.

## The copy (fixed)
- kicker: `The same note`
- counter: `07 / 09`
- headline (verbatim): `"Insignificant effect on this state's economy"`
- dek (verbatim, except the one exception below): `That is the chief revenue estimator's finding. It sits in the same note that estimates the losses. The note also says a likely negative effect on sales tax remittances can't be estimated.`
- labels: []
- claim ids (the `src` furniture): `c38 c39`

**The one exception.** A dek sentence that only describes the picture must describe YOUR picture truthfully. Rewrite only that sentence, add no number, date, name or claim. "Drawn to illustrate" is printed on frame 3 ONLY. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"state_fy2032_sheets": 4286, "state_fy2032_stack_mm": 428.6}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch.

## The spine
- chassis: `assets/js/deck/2026-11-27-onesheet-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `watch`, accent dusk gold `#e0956a` meaning THE WORDS OF THE PROPOSAL and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-27/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture; its render `out/2026-11-27/tmp/probe/render/slide-01.png` is a model proof of the paper models). Use `CH.develop(await TXT.snapshot(R, {}), gl)`, then seat type with `CH.seat`, footer with `TXLOOK.footWash`, and `TXDECK.finish(cx)` last.
- accent on this frame: YES, #e0956a, on the words of the proposal only (a highlighted line or paragraph, the last day tab, the line of the letter quoting the rule)
- MATERIAL CODE: kraft wrapped reams with a rose band and cream sheet edges are the ESTIMATE (`K.make('ream_stack', { sheets })`, one sheet per $1,000,000). Cream Register paper with violet grey ink is the RULE (`K.make('register_page', { hl, curl, clip })`). The accent is `CH.goldMat(K)` or a highlighted line on a page texture.
- WATCH tone: violet over rose, a coral key, a violet fill, violet and navy in every shadow, never black. No dark room, no black type band. Grey mid tones fail value_register, so surfaces take saturated colour.
- chassis models (read their doc comments in the chassis): `paper_ream` (sheets, torn), `ream_stack` (sheets, jitter, seed, tornTop; userData.top, reams, loose, sheets; origin at its base), `register_page` (hl line index or -1, curl 0 to 1, clip, seed; lies flat on y = 0), `envelope` (flap degrees, letter 0 to 1, seed; lies flat). Helpers `CH.goldMat`, `CH.rackMat`, `CH.pageTex`, `CH.ortho`, `CH.pin`, `CH.project`, `CH.studioOpts`, `CH.roomOpts`, `CH.rigSpec`, `CH.rigOpts`, `CH.aim`, `CH.canvasTex`. Plus every kit model in ARSENAL (server_rack, server_row, access_floor, desk, document_stack, laptop, hearing_dais, public_seating, index_card_drawer and more). The chassis models are BASIC geometry; REFINE their look inside your own frame (wrapper creases, a torn top, wear) but never edit the chassis file. Anything else you need you build in your own frame, at true size in metres, never as a bare primitive.
- a TXBENCH relief file shape to copy (never its picture): `runs/carousel/2026-11-25/slides/slide-03.html` (CH.bootFlat, TXBENCH.relief under the chassis key).
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- NO logo, maker's mark, real building, legible screen or legible text in the art, no likeness of any person. Keep people out of this deck.
- file: `out/2026-11-27/slides/slide-07.html`
- your render dir: `out/2026-11-27/work/render-07` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-27/slides --out-dir out/2026-11-27/work/render-07 --only 7 --timeout 300000`
- your concepts: `out/2026-11-27/briefs/slide-07.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-27/`; never write under any .claude directory.

## The neighbours
- frame before: CITIES, COUNTIES, TRANSIT. Know: local governments lose too, by the same note. c32 c37.
- frame after: THIRTY DAYS. Know: comments within 30 days of November 20th, adoption no earlier than December 20th. c41 c43 c45.

## What already ran, so do not repeat it
November 26th drew a turboshaft engine on a stand, a flight recorder tape, a socket tray of gold cubes, an hour rule, a blisk, a hangar bench and an open hangar door (explainer). November 25th drew glass lungs, manila chart folders, a card drawer and a family under a live oak (people). November 24th drew drone aerials over roofs and plate racks (wonder). November 22nd drew cutaway exam rooms and studio benches (explainer). Judges lately charged: a 3D bar chart of blocks with ghosts on a flat field, primitive extrusions, a tag reading as a luggage tag, a close split into a pale doorway with small objects, grey pill labels, capsule people, flat face on elevations, top down trays reading as charts, uncountable units at feed size, missing contact shadows, a hero under a tenth of the frame, 'drawn to illustrate' on every dek (now ONE per deck, on frame 3 only). Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
