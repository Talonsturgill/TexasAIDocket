# Machine queue: what the weekly machine pass works on

Since 2026-10-03 a run fixes only what broke in its own run and queues every other machine change
here, in Phase 17, under the `upgrade` stamp. Once a week the machine pass (Phase 17, brief in
`prompts/machine_weekly.md`) reads the week's own artifacts through
`scripts/carousel/week_digest.py`, works the themes that recurred and this list, and marks what it
shipped. `scripts/carousel/machine_due.py` reads this file to decide whether a pass is due early.

The owner's words, 2026-10-02: the daily automation should "only fix like the things that were
broken during the run", and once a week spend time "addressing the things that really need to be
fixed based on the recurring themes that it saw during the week ... based on actual output".

One line per item, in this exact shape, so the due check can read it:

    - [ ] <date found> | repeat: <runs it has bitten beyond the first> | <signature> | evidence: <what showed it, with frames and rounds> | fix: <the proposed change>

**A defect already open is never added twice.** The run that meets it again raises its `repeat`
count in place and appends its date to the evidence. An item at `repeat: 2` makes the pass due the
next day rather than waiting out the week.

A pass that ships an item changes `[ ]` to `[x]` and appends ` | shipped <date> <commit>`. An item
it can't fix safely stays open with ` | escalated <date>: <why>`. An item that needs a `human`
file, the engine (`assets/js/txthree.js`) or the kit registry (`assets/js/txkit.js`), is written
up in `UPGRADE_BACKLOG.md` and named at the top of the email.

## Open

- [ ] 2026-10-03 | repeat: 0 | dry-van-built-in-chassis | evidence: no. 41 built a 53 ft dry van (doors, 100 load places, beams, tapes, near-wall cut) in assets/js/deck/2026-10-03-norther.js because the kit has none; it carried all nine frames | fix: lift dry_van, its load places and the load bar into assets/js/kit at the judges' named fixes (seams, grime, lit floor) | escalated 2026-10-03: the deck was mid-panel and its installKit returns early once the kit defines dry_van, so a lift would swap its models under it; lift from the shipped chassis next (UPGRADE_BACKLOG 2026-10-03 item 7)
- [ ] 2026-10-03 | repeat: 0 | roadside-furniture-built-in-chassis | evidence: no. 41 frame 4 built delineator and raised_pavement_marker in the chassis; round 1 pixel critic could not count the posts at 432px | fix: lift both into assets/js/kit with a reflector that reads at thumb size | escalated 2026-10-03: same chassis and same reason as dry_van, the three are one lift (UPGRADE_BACKLOG 2026-10-03 item 7)
- [ ] 2026-10-03 | repeat: 0 | hub-world-void | evidence: no. 41 flow critic round 1 named five frames (1, 5, 6, 8, 9) standing on one bare court to a blank horizon; pixel critics named 'object on an empty plane' on frames 1, 6, 8, 9 in rounds 1 and 2 | fix: a kit truck-hub scene (warehouse with dock doors, trailer rows, light poles, oil-stained joints, clay edge) a frame places once and aims at | escalated 2026-10-03: a new kit scene from one run, deferred until a second deck needs it or the dry_van lift brings it (UPGRADE_BACKLOG 2026-10-03 item 7)
- [ ] 2026-10-03 | repeat: 0 | flat-sky-gradient | evidence: no. 41 stormFront sky read as a flat gradient with no cloud edge on frames 1, 2, 5, 7, 8, 9 in pixel rounds 1 and 2 | fix: engine (human), a stormFront shelf edge visible at long and normal lenses; backlog proposal | escalated 2026-10-03: engine, assets/js/txthree.js is human (UPGRADE_BACKLOG 2026-10-03 item 4)
- [ ] 2026-10-03 | repeat: 0 | shadow-serration-hard-casts | evidence: no. 41 frames 8 and 9 sawtooth shadow edges on carton faces (pixel rounds 1 and 2, flow round 1), frames 4 and 6 hard rectangular casts | fix: engine (human), VSM resolution and blur on small casters; backlog proposal | escalated 2026-10-03: engine, assets/js/txthree.js is human (UPGRADE_BACKLOG 2026-10-03 item 4)
- [ ] 2026-10-03 | repeat: 0 | acceptance-lists-trivially-satisfiable | evidence: no. 41 pixel critics in rounds 1 and 2 said on every frame that the dossier's acceptance list would pass on a near blank frame (no item on the data subject's visible size, contact, world or the paint's value) | fix: dossier_check requires one measurable acceptance item per frame on its data_in_art subject (minimum px at 432) and one on its world | escalated 2026-10-03: one run, and a stricter dossier_check would have gone red on the live run's dossiers mid-panel; ship it dated if a second deck shows it (UPGRADE_BACKLOG 2026-10-03 item 8)
- [ ] 2026-10-03 | repeat: 1 | qa-glyph-run-as-rule | evidence: no. 41 slide 9 round 2, qa canvas_rules read a tight display hook's own touching serifs as a canvas rule through the glyph band; letter-spacing 0.012em cleared it ; also 2026-10-02 (UPGRADE_BACKLOG 2026-10-02 item 5, serif feet of a short heavy last line) | fix: qa.py (under .claude, maintainer) compare the strip against the canvas with the type hidden | escalated 2026-10-03: qa.py is under .claude/skills, a maintainer's edit (UPGRADE_BACKLOG 2026-10-03 item 5)
- [ ] 2026-10-03 | repeat: 0 | pixel-critic-thumb-path | evidence: no. 41 pixel round 1, three of five critics looked for final/thumbs/slide-0N.png and found nothing; the files are slide-0N-thumb.png | fix: name the thumb path pattern in the carousel-pixel-critic definition (under .claude, maintainer) or in the routine's Phase 12 spawn text | escalated 2026-10-03: the agent definition is under .claude and the Phase 12 spawn text is prompts/daily_routine.md, both a maintainer's (UPGRADE_BACKLOG 2026-10-03 item 6)

- [ ] 2026-10-03 | repeat: 0 | highway-kit-verge-polygon | evidence: no. 41 frame 4, a flat yellow-olive quad on the right verge named by the pixel critics and all three judges in every panel round (1 to 4); scratch renders proved it survives removing the rig, its contact shadow, the pastures, the yard and the grass scatter and goes with the kit highway | fix: find the verge or shoulder mesh in the kit highway that draws it and give it the shoulder material or remove it
- [ ] 2026-10-03 | repeat: 0 | carton-side-serration-not-shadow-resolution | evidence: no. 41 frames 8 and 9, the sawtooth band down the left carton column survived a 4096 map over a 7 m frustum and normalBias 0.08 in rounds 3 and 4, so it is not shadow-map aliasing; a judge suggests z-fighting between the stack side faces and the van liner | fix: inset the chassis stacks 2 cm from the liner, or cull the side faces against the wall, and prove it on frame 8 at full size
- [ ] 2026-10-03 | repeat: 0 | ship-images-og-from-first-png | evidence: no. 41, rerunning ship_images.py after slide 1 was already WebP built og.jpg from slide-02.png, the first PNG left in the folder | fix: write_og reads slide-01.png or slide-01.webp by name, never the first PNG in sort order

## Done

- [x] 2026-10-03 | repeat: 0 | dedupe-misses-same-company-same-lane | evidence: no. 41 passed dedupe at 0.50 against no. 34 (seven days earlier, same company, same I-45 lane, same September 25th release), and two of three round 1 judges hard-failed the 30 day window on frames 8 and 9 and the caption | fix: dedupe_check also compares the cited source URLs and the named company and place against the window and fails a deck whose close or two or more frames rest on a docket item a deck in the window already carried | shipped 2026-10-03 4c8c9819 (a maintainer session: dedupe_check exit 3 is binding on the same item, the same documents or the same company at the same place, and panel_ready runs it on the built deck)
- [x] 2026-10-03 | repeat: 0 | emissive-accent-reads-salmon | evidence: no. 41 ember beams with emissive 1.05 measured (220,131,93) against #B4664F (180,102,79) in sun and read pink to three critics; emissive 0.72 fixed it | fix: TECHNIQUE_LIBRARY note, an accent object takes its colour from albedo and a small emissive, measured off the render | shipped 2026-10-03 pending-commit
