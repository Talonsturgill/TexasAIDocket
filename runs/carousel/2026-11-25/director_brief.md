# Director brief, November 25th, 2026, carousel no. 87 (BESPOKE + LOOK V2)

## The story (docket tx-2026-0260, claims in out/2026-11-25/claims.json, c2 to c28, the ONLY facts you may use)
UTMB Health announced on November 19th that AI now supports its lung cancer screening work (c2). The program was
established in 2016 to screen patients at high risk for lung cancer (c3). Dr. Shawn Nishi directs the Comprehensive
Lung Cancer Screening & Incidental Lung Nodule Program (c4). The old process sometimes took weeks or even months (c5),
and by the time staff navigated the care pathway the time-critical follow-up window had often closed (c6). They
needed a faster process (c7). The current system, developed with Bunkerhill, reviews radiology reports (c8) for
patients having lung cancer screening exams (c9). Any nodule, whether found on a screening exam or on another imaging
study involving any portion of the lungs (c10), is now flagged for review by the patient navigator (c11), Amanda
Rodriguez (c12). Her dashboard calculates a validated lung cancer risk score for patients with scan abnormalities
(c13) so she can prioritize follow-up care (c14). Much of the chart review, once the most time-consuming part, is
automated (c30). Nishi calls AI an assistant, not a decision maker (c15). People remain at the center while AI works
in the background (c16).

THE TURN. Roughly two-thirds of the nodules identified through the program were found in patients who were NOT
having lung cancer screening (c17). The scan was for something else. Nishi's example: a patient in her 20s had a car
accident (c18), a scan found a nodule incidentally (c19), a biopsy showed lung cancer and she underwent resection for
cure (c20). She named seven or eight relatives diagnosed with cancer (c21), and the hereditary disease made it
important for her family to be tested (c22).

Context you may use: robotic bronchoscopy, which Nishi calls AI-enabled, reaches any area of the lung (c23) and
biopsies with a high degree of accuracy (c24, no figure, and NEVER attached to the flagging AI). Bunkerhill's own case
study claims 80% faster lung nodule triage at UTMB (c25), names a Brock risk score (c26) and says UTMB keeps a human
in the loop for now (c27). Those three are the VENDOR's claims, attribute them or leave them out. Federal guidance
recommends screening for adults aged 50 to 80 with a 20 pack-year history who smoke or quit within 15 years (c28).

## Figures (out/2026-11-25/figures.json, every numeral drawn must be read from it in code)
share_num 2, share_den 3 (roughly two-thirds, draw as 2 of every 3, never a percent), of_nine 6 of units 9 (drawing
units only), program_start 2016, patient_decade 20, relatives_low 7, relatives_high 8, vendor_pct 80 (Bunkerhill's,
never UTMB's), age_low 50, age_high 80, pack_years 20, quit_years 15.

## Integrity, binding on every pitch
- NO accuracy figure, NO count of patients, scans or nodules, NO after-adoption timing exists. Never imply one.
- The AI flags, the navigator reviews, doctors decide. No frame shows the AI deciding, diagnosing or treating alone.
- No real CT image, no real patient, no likeness of Nishi, Rodriguez or the patient. No legible screen, no UI, no logo,
  no Bunkerhill or UTMB mark. Everything is drawn to illustrate. Any person is three quarters away, at distance or cropped.
- The patient story is Dr. Nishi's account. Attribute it. Never draw a crash scene, blood, an injury or surgery.
- Not a scare deck. Not "AI finds cancer". The story is a safety net under scans taken for other reasons.
- Banned words on every surface: gap, gaps, matters, pattern, patterns. No colons, semicolons, em or en dashes.
  The release's own line "time matters" may not be quoted on a slide.

## Doctrine to read first
- knowledge/carousel/BESPOKE.md (you pitch nine BEATS, not layouts). CLAUDE.md, LOOK V2. Pick a TONE (wonder,
  explainer, win, watch, people). Recent tones Nov 24 wonder, Nov 22 explainer, Nov 21 win, Nov 20 people, Nov 19 wonder,
  Nov 18 explainer, Nov 17 watch. Argue for yours and name TXT.V2_WORLD[tone].
- knowledge/carousel/ARSENAL.md KIT and ENGINE. The kit has person (poses incl. sit_read, read, point), monitor
  (screen chart|dash|doc|sheet|off, never legible), workstation_cart, patient_wristband, desk, office_chair,
  document_stack, hospital, conference_table. The Nov 22 chassis (assets/js/deck/2026-11-22-fairtest-bespoke.js) built
  exam_table, stethoscope, output_slip (greeked printed slip), paper_roll. Anything else, name in metres (a CT gantry
  and couch, a translucent lung, a nodule bead, a tray of report slips, a sieve).
- knowledge/carousel/ILLUSTRATION_SYSTEM.md "What still fails" and THE SHOWSTOPPER TEST.
- The rotation rule changed on 2026-09-16. Read knowledge/carousel/ILLUSTRATION_SYSTEM.md, "THE DECK IS THE UNIT", and
  judge against that. If anything in your own definition disagrees with it, this paragraph wins. At most TWO of the same
  archetype in a row and at least THREE distinct, not five. On this bespoke run BESPOKE.md supersedes the one world and
  one light half, and no screen at all, because the print register is deleted. Name at least two continuity devices.

## What the judges charged the last decks (fix upstream)
- Nov 24: frame 7 root plate read as an orange boulder with spikes, frame 4 rims read as gutters not a code, frame 6
  operator a smooth mannequin, frame 9 the softest picture repeating the cover. Lead with the news the caption carries.
  Give the close a concrete action that names a body and that a claim supports. Never let a context beat break a run.
- Nov 22: a distant isometric dollhouse with mannequin figures, a dark wedge read as a pennant, a closed laptop pair
  floating on a flat blue field, the subject in a thin band under a hazy top.
- Recurring: capsule people, flat elevations, top down trays reading as charts, uncountable units at feed size, sky
  banding, missing contact shadows, a hero under a tenth of the frame, "drawn to illustrate" closing eight deks.
- DO NOT REPEAT. Nov 22 drew cutaway exam rooms, a stethoscope wall, studio benches, exam paper and an open binder.
  Nov 24 drew a stitched aerial neighbourhood. This deck must not look like Nov 22's clinic. Find this story's own
  picture: a scan taken for one reason that holds a second thing, a report read for a word, a small bead flagged, a
  queue sorted by risk, a person who checks.

## What to return
One complete treatment: title, tone (and its TXT.V2_WORLD), the visual argument in two sentences, the accent colour and
its ONE meaning, two or more continuity devices, then NINE BEATS. Each beat: number, kicker (two or three words), what
the reader must FEEL and KNOW, claim ids, the figure it carries and how the drawing carries it, a starting picture
(subject by kit model or chassis build in metres, world, camera AERIAL/WIDE/MEDIUM/CLOSE/MACRO, light), and where the
type wants to sit. Frame 1 is the hook, and it carries the news the caption will lead with. Frame 9 is the close that
names what a reader can do or watch for, supported by a claim (for example c28's screening criteria, or asking about a
nodule on any chest scan, c10). Then a CRAFT PLAN row per frame, `Showstopper frame: NN` and `Tonal arc:`. Plain text.
