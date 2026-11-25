# Director brief, November 24th, 2026, carousel no. 86 (BESPOKE + LOOK V2)

## The story (docket tx-2026-0258, claims in out/2026-11-24/claims.json, c1 to c23, the ONLY facts you may use)
Texas A&M built CLARKE, an AI tool that reads drone imagery after hurricanes, tornados, wildfires and other
disasters and produces detailed damage assessments within minutes (c1). Tom Manzini of the development team says
it does in minutes what takes 18 to 24 hours otherwise (c2). The drone images are stitched into one georectified
orthomosaic and aligned to building and road footprints (c23). Its Building Damage Assessment rates the damage to
each individual building (c5) and gives responders a color coded view, structure by structure, across an affected
area (c6). A road model identifies road network damage and obstructions (c21) so crews can route around damaged
roads (c7). Given a finished orthomosaic it assesses roughly 2,000 buildings in about 7 minutes (c16, c22), the
clock starting after stitching. Outputs are GeoJSON and KML that drop into TAK, ArcGIS Online and other common
operating pictures (c18). It runs in the field and needs no wireless transmission of imagery (c20). A trained
operator reviews every assessment before it reaches decision makers (c19). The models were trained on drone imagery
of more than 21,000 damaged homes in 10 major disasters (c3), Hurricane Harvey and Hurricane Ian among them (c4),
the CRASAR-U-DROIDs dataset of 265 orthomosaics and 21,716 building polygons (c17). 125 responders from 63 agencies
in 14 states and Puerto Rico have trained on it (c8). It was deployed in Florida and Pennsylvania in the 2024
season after hurricanes Debby and Helene (c10). Florida's state drone remote sensing team, FL-UAS1, has made it
part of its standard operating procedures (c9). Gathering damage information can take days, especially in rural
areas or where communications are down (c15), and Florida's drone task force lead says responders can fly and see
the damage at once rather than wait days (c11). Semafor picked it for its Innovation Atlas 2026, one of five
inventions (c13, c14). NSF funded it through the AI Institute for Societal Decision Making (c12).

THE TURN. A tool built in College Station and trained partly on Harvey's damage is standard procedure in Florida.
The November 24th release and the project site name no Texas agency or county among its users (rejected list,
scoped to those two documents). Say that only as a scoped absence, never as "Texas doesn't use it".

## Figures (out/2026-11-24/figures.json, every numeral drawn must be read from it in code)
hours_low 18, hours_high 24, hours_low_minutes 1080 (drawn only as a length), homes 21000 (a floor, "more than"),
disasters 10, orthomosaics 265, building_views 122502, polygons 21716, buildings 2000 (roughly), minutes 7 (about),
responders 125, agencies 63, states 14 (plus Puerto Rico), season_year 2024.
No ratio of the two timings is ever printed. They come from two pages and the site's clock starts after stitching.

## Integrity, binding on every pitch
- NO accuracy figure exists. Never imply one, never show a damage class name (the classes are not public), never a
  legend with named categories. The color code may be drawn as colour alone, labelled "drawn to illustrate".
- No real town, real street, real disaster scene, logo, product screen or legible interface. Everything is drawn to
  illustrate. Harvey is named in copy only as training imagery.
- Florida's adoption, the training count and the Semafor pick are Texas A&M's statements. Attribute them.
- A human operator reviews every assessment (c19). No frame may show the AI deciding alone.
- Banned words on every surface: gap, gaps, matters, pattern, patterns. No colons, semicolons, em or en dashes.

## Doctrine to read first
- knowledge/carousel/BESPOKE.md (you pitch nine BEATS, not layouts). CLAUDE.md, LOOK V2. Pick a TONE (wonder,
  explainer, win, watch, people). Recent tones Nov 22 explainer, Nov 21 win, Nov 20 people, Nov 19 wonder, Nov 18
  explainer, Nov 17 watch. Argue for yours and name TXT.V2_WORLD[tone].
- knowledge/carousel/ARSENAL.md KIT and ENGINE. The kit has ranch_house, two_story_house, garden_apartment, yard,
  palm, live_oak, road, utility_pole, pickup, suv, utility_bucket_truck, person, laptop, vtol_drone, drone_dock,
  water_tower, privacy_fence, chain_link_fence. Earlier chassis built survey_quad and rubble_pile (Nov 20 and 21,
  assets/js/deck/2026-11-21-handoff-bespoke.js). Name in metres anything else.
- knowledge/carousel/ILLUSTRATION_SYSTEM.md "What still fails" and THE SHOWSTOPPER TEST.
- The rotation rule changed on 2026-09-16 (ILLUSTRATION_SYSTEM.md, THE DECK IS THE UNIT). On this bespoke run
  BESPOKE.md supersedes its one world and one light half. No screen at all. Name at least two continuity devices.

## What the judges charged the last three decks (fix upstream)
- Nov 22 frame 1, a distant isometric dollhouse with mannequin figures. Frame 5, a dark wedge read as a pennant.
  Frame 9, a closed laptop pair floating on a flat blue field. Frame 6, the subject in a thin band under a hazy top.
- Nov 21 frame 3, toy cubes on a flat yellow sweep with labels doing the explaining. Frame 8, a primitive medic.
- Nov 20 frame 4, a floating puck stem and malformed laptops. Frame 7, top 40 percent flat empty magenta.
- Recurring, capsule people, flat elevations, top down trays reading as charts, uncountable units at feed size,
  sky banding, missing contact shadows, a hero under a tenth of the frame, "drawn to illustrate" closing eight deks.
- DO NOT REPEAT. Nov 20 a survey quad on a ridge, Nov 21 a tracked rover on rubble and a staged disaster town
  (DARPA triage at Disaster City). This deck must not look like Nov 21. Find this story's own picture, most likely
  the thing CLARKE actually makes, a stitched aerial mosaic with every roof and road judged, and the road out.

## What to return
One complete treatment: title, tone (and its TXT.V2_WORLD), the visual argument in two sentences, the accent
colour and its ONE meaning, two or more continuity devices, then NINE BEATS. Each beat: number, kicker (two or three
words), what the reader must FEEL and KNOW, claim ids, the figure it carries and how the drawing carries it, a
starting picture (subject by kit model or chassis build in metres, world, camera AERIAL/WIDE/MEDIUM/CLOSE/MACRO,
light), and where the type wants to sit. Frame 1 is the hook. Frame 9 is the close that names what a reader can
do or watch for. Then a CRAFT PLAN row per frame, `Showstopper frame: NN` and `Tonal arc:`. Plain text.
