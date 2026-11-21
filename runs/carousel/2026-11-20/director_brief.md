# Director brief, November 20th, 2026, carousel no. 83 (BESPOKE + LOOK V2)

## The story (docket tx-2026-0253, claims in out/2026-11-20/claims.json, c1 to c26, the ONLY facts you may use)
GPS spoofing sends false signals that trick a receiver into reporting the wrong location (c1). It could send a
civilian drone into restricted airspace or set it down somewhere unsafe (c2), steer an opposing drone away in a
conflict (c19), or make a drone miss a threat, endanger other aircraft or crash near people (c20). The release's
own example is a search drone meant to sweep a ridge that a false signal sends into the next valley (c18).
Researchers at East Texas A&M University in Commerce (c14), led by professor Jinoh Kim (c16), tested whether AI can
spot false location information in a drone's flight records (c3). The method ignores GPS and reads the drone's own
motion sensors, how fast, which way, over how much time, for inconsistencies (c4, c15). They used a public dataset
of 96 real drone flights (c5): 42 normal and 54 flown under controlled spoofing attacks (c6), some fed one false
location and some fed false coordinates that changed over time (c7). They held back 22 whole flights for testing,
flights the models had never seen (c8). They compared eight AI models (c9), and a part of the system sorts short
stretches of flight data as normal or abnormal (c24). The best had already learned to read numerical data over time
(c10), which Kim called a surprise (c21). Given 10 consecutive readings, a model called Chronos scored 97.5% on a
measure balancing caught abnormal stretches against how often its alerts are right (c11). Chronos's own paper calls
it a framework for pretrained time series models (c26). The study used recorded flights. Running the check in flight
is the next step (c12). The project has a two year NSF grant of about $200,000 (c13, award no. 2502117, c17). The
first author is an undergraduate, Iyanuoluwa Alegbeleye (c22), and the team has two undergraduate and two graduate
research assistants (c23). The study was accepted at WATCH 2026, a peer reviewed workshop beside the ACM computer and
communications security conference in The Hague (c3), which met November 15th (c25).

## Integrity, binding on every pitch
- Nothing was flown live. Every drone drawn is "drawn to illustrate", to no maker's design. Never draw the check
  running in flight as a result, never draw an in flight alarm as if it happened.
- 97.5% is a score on one balanced measure for one model given 10 readings. It is NOT "accuracy", NOT a catch rate,
  and never "97.5 of 100 attacks caught". Never draw it as a pie of attacks caught. A drawn scale must say what it is.
- No scores are published for the other seven models. Never rank them with drawn bars.
- The release does not say who made Chronos. Never say or imply Amazon or any company.
- The ridge and valley search is the release's own hypothetical (c18). It is not a Texas incident. Never pin it on
  a real Texas place or name a missing person.
- No spoofing incident in Texas is in the claims. No county is named beyond Commerce (c14).
- Every count drawn (96, 42, 54, 22, 8, 10) is computed in code from figures.json. No numeral typed by a model.
- No ETAMU logo, seal, mascot or NSF logo.

## The doctrine you must read first
- knowledge/carousel/BESPOKE.md (this run is BESPOKE: one artist per slide; you pitch nine BEATS, not layouts).
- CLAUDE.md, the LOOK V2 section. Pick a TONE from wonder, explainer, win, watch, people. Recent tones: Nov 19
  wonder, Nov 18 explainer, Nov 17 watch, Nov 15 people; explainer ran on three of the last six. Argue for your tone.
  At most two `watch` decks in seven, and one has run.
- knowledge/carousel/ARSENAL.md, its KIT and ENGINE sections. Name every object by its kit model (K.make name and
  options) or say in metres what the chassis must build. The kit has NO quadcopter. A survey quadcopter was built
  once in assets/js/deck/2026-10-18-brush.js (survey_drone, 1.1 m across); the chassis will rebuild a finer one.
  The kit does have vtol_drone, drone_dock, person, pickup, live_oak, mesquite, hill_country_terrain, mesa,
  transmission_tower, windmill and more.
- knowledge/carousel/ILLUSTRATION_SYSTEM.md "What still fails" and THE SHOWSTOPPER TEST (LOOK V2 version).
- The rotation rule changed on 2026-09-16. Read ILLUSTRATION_SYSTEM.md, "THE DECK IS THE UNIT", and judge against
  that; if anything in your own definition disagrees, this paragraph wins. On this bespoke run BESPOKE.md supersedes
  its one world and one light half: the deck shares only its spine (tone, palette, grade, type faces, counter, site
  line, accent meaning, story order) and each slide owns its world, light, camera and composition. No screen at all,
  the print register is deleted. Name at least two continuity devices that do real work.

## What the judges charged the last three decks (fix these upstream)
- Nov 19 frame 5: crawling flies read as ants, a bucket read as a paint pail. Frame 9: a still life whose phone screen
  read as two blobs, repeated grass tiles. Frame 7: a grid of boxes under half the frame in a void.
- Nov 18 frame 4: eight unlabelled swatch bands in a tray read as UI. Frame 9: no subject owns the frame. Frame 1:
  a primitive box satellite.
- Nov 17 frame 4: the subject small in the lower half seen from high and far, the top 45 percent type on a wash.
  Frame 9: desk and chair floating small in a wide empty sweep.
- Recurring: capsule people, soft kit hands, walls filling the top half, flat face on elevations, top down trays
  reading as charts, uncountable units at feed size, sky banding behind headlines, objects with no contact shadow.
- What already ran (do not repeat): Nov 19 sort glass, flies, a tube rack, bales. Nov 18 a survey satellite, stake
  grids, an air column. Nov 17 a scoring machine and card drawer. October 26th (no. 62) drew Zipline delivery drones
  and a dock in Round Rock. October 18th (no. 54) drew a survey quadcopter over brush.
- Instincts to honour: write acceptance items so rendering nothing fails them; read every repair at 432 px; a
  claim's paraphrase can assert more than its quote.

## What to return
One complete treatment: title, tone (and its TXT.V2_WORLD), the visual argument in two sentences, the accent
colour and its ONE meaning, two or more continuity devices, then NINE BEATS. Each beat: number, kicker (two or
three words), what the reader must FEEL and KNOW, claim ids, the figure it carries (if any) and how the drawing
carries it, a starting picture (subject by kit model or chassis build in metres, world, camera shot
AERIAL/WIDE/MEDIUM/CLOSE/MACRO, light), and where the type wants to sit. Frame 1 is the hook, frame 9 the close that
names a next step a Texan can watch (the in flight test, c12). Then a CRAFT PLAN row per frame and
`Showstopper frame: NN` and `Tonal arc:`. Plain text, no colons in copy you propose.
