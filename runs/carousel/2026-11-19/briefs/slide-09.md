# Slide brief, frame 9 of 9, 2026-11-19 (BESPOKE, LOOK V2, tone WONDER)

**You are the artist for this frame only.** Read `knowledge/carousel/BESPOKE.md`, `.claude/agents/carousel-slide-artist.md`, the LOOK V2 section of `CLAUDE.md` and `knowledge/carousel/ARSENAL.md` first. The deck plan is `out/2026-11-19/storyboard.md` (your dossier is its slide 9 yaml block, which carries your acceptance list; the CRAFT PLAN row is your starting concept). Claims are `out/2026-11-19/claims.json`.

## The story in one line
UT Arlington coordinates a $3.1 million USDA funded project to build an AI smart trap meant to tell wild New World screwworm flies from sterile ones and females from males, keeping wild females and letting sterile flies and other insects go. The trap is NOT built; a prototype is expected next spring. The deck's argument is ONE DOOR OR TWO: today's traps have one exit and keep everything, the planned trap would have two. Never draw the trap as a deployed field device, never draw an accuracy, catch count or field result, never draw a camera, flap or circuit on it. No fly size is claimed, so never put a fly beside an object that measures it. No gore, no wound. No USDA, APHIS or UTA logo or seal.

## The beat
NEXT SPRING. Feel: a part a Texan can play, and a date to watch. Know: A prototype is expected next spring, and producers would report cases from a phone. c6 c14 c10.
Planned picture (a strong starting concept, not a cage; you pitch three and may beat it): a kit person cropped at the shoulder three quarters from behind holding the chassis smartphone at chest height, its screen a framed pasture photo and a dusk gold report pill, kit stock_tank and kit live_oak beyond, TXT.sky v2wonder golden, face edge and hand lit from the camera side
Camera: MEDIUM, 50 mm equivalent at 1.1 m behind the shoulder.

## The copy (fixed)
- kicker: `Next spring`
- counter: `09 / 09`
- headline (verbatim): `Watch for the prototype next spring`
- dek (verbatim, except the one exception below): `UTA's Shouyi Wang expects a smart trap prototype by then. Producers and veterinarians would report cases with phone photos. Each trap detection could feed alerts and risk maps to APHIS. Drawn to illustrate.`
- labels: [] (tone pills from TXLOOK.css; only a label marking the wild female or the report may be dusk gold)
- claim ids (the `src` furniture): `c6 c14 c10`

**The one exception.** A dek sentence that only describes the picture ("drawn to illustrate", "one tube stands for one trap") must describe YOUR picture truthfully. Rewrite only that sentence, keep "drawn to illustrate", add no number, date, name or claim. Every other sentence stays word for word. House rules on any word you set: no em or en dashes, no colons or semicolons, no first person, can't never cannot, no sentence opening with And or But, straight quotes, banned words gap, gaps, matters, pattern, patterns.

## The figures (window.FIG, exactly)
`{}`
Every count or length you draw is computed from window.FIG in your code with a check that throws on a mismatch. No figure is drawn on this frame; set window.FIG = {} .

## The spine
- chassis: `assets/js/deck/2026-11-19-sortglass-bespoke.js` (declares `bespoke: true`, LOOK V2 tone `wonder`, accent dusk gold `#e0956a` meaning THE FLY THE SORT KEEPS, the wild female and the report she becomes, and nothing else). Load it after `txdeck.js` and `txlook.js`, exactly as `out/2026-11-19/tmp/probe/slides/slide-01.html` loads it (copy that file's head and boot shape, never its picture).
- accent on this frame: this frame CARRIES dusk gold.
- WONDER tone: cobalt zenith, peach horizon, honey key. Shadows lean violet and navy, never black. No dark room, no black type band. Keep the golden key from swallowing the gold accent: seat any gold against cobalt.
- chassis models (installed by CH.boot; read their notes in the chassis): blowfly (options flying 0..1, spread), beetle, sort_glass (userData.keep, .release, .fork, .mouth; origin at the stem foot; band:true for the gold band), cell_block (cells, shut, open; userData.cells), stone_plinth, dead_end_jar, bucket_trap (origin at the bail top), smartphone (screen painter). Plus every kit model in ARSENAL. K.make merges a model's `options` as defaults, so pass real values. You may refine a chassis model's look inside your own frame (materials, extra detail parented to it) but never edit the chassis file.
- a chassis probe render (`out/2026-11-19/tmp/probe/render/slide-01.png`) shows every chassis model builds. The fly is tiny in model units (about 10 mm); scale it up for macro work only where no other object measures it.
- type faces, counter, kicker, site line and `TXDECK.finish` are fixed. Everything else is yours. Seat type with `CH.seat`, footer with `TXLOOK.footWash`.
- file: `out/2026-11-19/slides/slide-09.html`
- your render dir: `out/2026-11-19/work/render-09` (yours alone): `python3 .claude/skills/carousel-engine/render.py --slides-dir out/2026-11-19/slides --out-dir out/2026-11-19/work/render-09 --only 9 --timeout 300000`
- your concepts: `out/2026-11-19/briefs/slide-09.concepts.md`
- `@@ASSETS@@` resolves to `assets/` at render time. All scratch stays inside `out/2026-11-19/`; never write under any .claude directory.

## The neighbours
- frame before: THE ROAD TO 2028. Feel: a long road, and patience. Know: The project runs through June 2028 with fieldwork in Texas, other states and Mexico. c12 c15. FIG months_to_end.
- frame after: none, this is the close

## What already ran, so do not repeat it
November 18th drew a survey satellite in foil, an air monitor shelter on caliche, a stake grid, an air column relief, a flagstone floor and a terrain relief. November 17th drew a violet steel scoring machine, a card cabinet drawer, paper strata and paper columns, a desk under a lamp. November 16th drew a gold ribbon under a caliper and hands round a mug. November 15th drew student desks and a gym. October 18th (no. 54) told this same parasite from USDA's side in bluebonnet with a stock tank, a fly trap on a post, release boxes and a drone, and its backlit macro fly read as a black spider. Judges lately charged: subjects small in the lower half seen from high and far, walls filling the top half, flat face on elevations and swatch stacks reading as UI, top down trays reading as charts, capsule people and mannequins, soft kit hands, defocus blur with no finished subject, objects floating with no contact shadow, sky banding behind headlines, uncountable units at feed size. Place your type where THIS picture leaves quiet; neighbours put theirs elsewhere.
