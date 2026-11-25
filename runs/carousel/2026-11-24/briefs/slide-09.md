# Slide brief, frame 9 of 9, 2026-11-24 (BESPOKE, LOOK V2, tone WONDER)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-24/storyboard.md` (your dossier is its slide 9 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-24/claims.json`.

## The story in one line
Texas A&M developed CLARKE, an AI tool that reads drone imagery after hurricanes, tornados and wildfires. The images are stitched into one georectified orthomosaic aligned to building and road footprints, the Building Damage Assessment rates each individual building in a color coded view, and a road model finds road damage and obstructions so crews can route around them. A trained operator reviews every assessment before it reaches decision makers. Its developers say it takes minutes instead of 18 to 24 hours. It learned from drone imagery of more than 21,000 damaged homes in 10 disasters, Harvey among them. 125 responders from 63 agencies have trained on it, and Texas A&M says Florida's state drone team made it standard operating procedure. The two documents name no Texas user. The deck's argument is EVERY ROOF, READ: one drawn Gulf Coast neighbourhood goes through every state the tool puts it through, loose frames, one stitched map, every roof judged, a person's check that turns hollow rims filled, a gold route out, and at the close frame 1's camera over undamaged Texas ground. RULES: the damage classes are not public, so the colour code is CH.RAMP (three cool steps) as colour alone, no legend, no class names, never red. No accuracy is implied. No real town, street or disaster scene, no logo, no product interface, no legible screen. People are never likenesses: no face turned square to camera, no face over 2 percent of the frame; keep them three quarters away, lit from the camera side, at distance or cropped. No frame shows the AI deciding alone.

## The beat
BUILT IN TEXAS. Know: Florida's state drone team made it procedure, and the two documents name no Texas user yet. c9 c10, scoped absence.
Planned picture (a strong starting concept, not a cage; pitch three and you may beat it): frame 1's exact camera over an undamaged Texas street at peach evening, limestone ranch houses with bare roofs, live oaks, caliche verges, a water tower with its star on the horizon, and the gold route arriving from the left edge onto the street.
Camera and largest object: AERIAL, frame 1's camera over an undamaged Texas street, kit ranch_house in limestone, kit live_oak, kit water_tower with its star, the gold route arriving from the left edge, TXT.sky v2wonder.
Rims and colour code on this frame: NO rims, no damage, bare roofs on undamaged Texas ground.
Planned type seat: see the dossier's composition bands. Put the type where YOUR picture leaves quiet.

## The copy (fixed)
- kicker: `Built in Texas`
- counter: `09 / 09`
- headline (verbatim): `Texas A&M says Florida's team uses it`
- dek (verbatim, except the one exception below): `Texas A&M says Florida's state drone team now uses CLARKE as standard operating procedure. It was deployed in Florida and Pennsylvania in the 2024 hurricane season. The November 24th release and the project site name no Texas agency or county among its users. Street drawn to illustrate. Watch for the first.`
- labels: [] (none)
- claim ids (the `src` furniture): `c24 c9 c10`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one helmet stands for one responder", "one marker stands for one hour") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate" where it is, add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{"buildings": 2000}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch. Data in art for this frame: roof count of the Texas tile equals FIG.buildings, the same tile size as frame 1.

## The spine
- chassis: `assets/js/deck/2026-11-24-roofread-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `wonder`, accent gold `#ffcc00` meaning THE WAY THROUGH, the route around damaged roads, and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-24/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture; its render is `out/2026-11-24/tmp/probe/render/slide-01.png`). Use `CH.develop(await TXT.snapshot(R, {}), gl)`, then seat type with `CH.seat`, and `TXDECK.finish(cx)` last.
- accent on this frame: YES. CH.route arrives from the LEFT edge onto the Texas street.
- WONDER tone: cobalt zenith over a peach horizon, a honey key, navy and violet in every shadow, never black. No dark room, no black type band. Seat type with `CH.seat`, footer with `TXLOOK.footWash`. Grey mid tones fail value_register, so surfaces take saturated colour.
- chassis helpers and models (read their doc comments in the chassis): `CH.lots(n, seed)` (seeded Gulf Coast lots with .streets centrelines), `CH.carpet(THREE, K, lots, { rims:'hollow'|'filled', damage:true, skip })` (instanced walls, hip and gable roofs, rims; userData.count is the roofs drawn), `CH.rims`, `CH.rim(THREE, K, w, d, step, filled, y)`, `CH.RAMP` (the three cool colour code steps), `CH.route(THREE, K, pts, { r, lift, glow })` (the gold accent tube), `CH.roofDamage(THREE, K, { w, d, tarp })` (OSB decking with nail rows, torn shingle tabs, a tarp with sandbags, in its own XZ plane to tilt onto a roof pitch), `CH.aerialTex(THREE, seed)`, and kit models `downed_oak` (a live oak on its side with a gumbo root plate), `rescue_helmet`, `ortho_plate` (anodised plate with an aerial patch), `plate_rack` (n plates on edge at a pitch, option lift removes one), `survey_quad`. Plus every kit model in ARSENAL (ranch_house, two_story_house, yard, live_oak, palm, crape_myrtle, road, caliche_road, pavement_marker, utility_pole, pickup, suv, utility_bucket_truck, person with poses, laptop, mailbox, water_tower, privacy_fence and more). The chassis models are basic geometry: REFINE their look inside your own frame (materials, wear, more parts) but never edit the chassis file. Anything else your picture needs you build in your own frame, at true size in metres, never as a bare primitive.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours.
- file: `out/2026-11-24/slides/slide-09.html`
- your render dir: `out/2026-11-24/work/render-09` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-24/slides --out-dir out/2026-11-24/work/render-09 --only 9 --timeout 300000`
- your concepts: `out/2026-11-24/briefs/slide-09.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-24/`; never write under any .claude directory.

## The neighbours
- frame before: WHO HAS TRAINED. Know: 125 responders from 63 agencies in 14 states and Puerto Rico. c8.
- frame after: none, this is the close
- copy frame 1's camera constants exactly from `out/2026-11-24/slides/slide-01.html` (the block commented `CAMERA (frame 9 copies this)`); if that file is not written yet when you start, use position [0, 38, 52], target [0, 0, -18], fov 34, and say so in your hand-back.

## What already ran, so do not repeat it
November 22nd drew cutaway exam rooms, a stethoscope wall, studio benches, exam paper and an open binder (explainer). November 21st drew a tracked rover on rubble in a staged disaster town aerial and a medic with a tablet (win). November 20th drew a survey quadcopter on a ridge and a clay tablet (people). November 19th drew sort glass and flies (wonder). Judges lately charged: a distant isometric dollhouse with mannequin figures, toy cubes on a flat sweep with labels doing the explaining, a part floating above its body, the top 40 percent flat and empty, flat face on elevations, top down trays reading as charts, capsule people and soft kit hands, missing contact shadows, sky banding behind headlines, uncountable units at feed size, a hero under a tenth of the frame. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
