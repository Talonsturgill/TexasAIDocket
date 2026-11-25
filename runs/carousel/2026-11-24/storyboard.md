# Carousel, November 24th, 2026: every roof, read

## The story, and what the fact check did to it

Texas A&M built CLARKE, an AI tool that reads drone imagery after hurricanes, tornados, wildfires and other disasters and produces detailed damage assessments within minutes (c1). Tom Manzini of the development team says it does in minutes what takes 18 to 24 hours otherwise (c2). The drone images are stitched into one georectified orthomosaic and aligned to building and road footprints (c23). The Building Damage Assessment rates the damage to each individual building (c5) and gives a color coded view, structure by structure (c6). A road model identifies road damage and obstructions (c21) so crews can route around them (c7). Given a finished orthomosaic it assesses roughly 2,000 buildings in about 7 minutes (c16, c22). A trained operator reviews every assessment before it reaches decision makers (c19), it runs in the field with no wireless transmission of imagery (c20), and its outputs are GeoJSON and KML (c18). The models learned from drone imagery of more than 21,000 damaged homes in 10 major disasters (c3), Harvey and Ian among them (c4), a dataset of 265 orthomosaics (c17). 125 responders from 63 agencies in 14 states and Puerto Rico have trained on it (c8). It was deployed in Florida and Pennsylvania in the 2024 season (c10), and Florida's state drone remote sensing team has made it standard operating procedure (c9). The fact check carried 23 claims and rejected the damage classes (not public), any time per flight, the AAAI paper (bot wall), the unconfirmed "game changer" line, and records a scoped absence: the November 24th release and clarke.crasar.org name no Texas agency or county among the tool's users.

Docket item tx-2026-0258, Brazos County, research-and-science.

## Why this treatment, and what was grafted

Base: EVERY ROOF, READ (the map it makes). The release is about a picture, one stitched aerial mosaic in which every roof and every road is judged, so the deck draws that artifact and teaches a reader to read it. Grafted from THE ROAD OUT (built here, used there): the close restages frame 1's camera over an undamaged Texas street with the gold road arriving, and the close asks a Texan to watch for a Texas name, scoped to the two documents. Grafted from ONE CENTIMETRE A MINUTE (the clock): time drawn as physical measured marks on frame 2, and the rule that no ratio of the two timings is ever printed. Declined: the watch tone, because this is a Texas tool doing real work and a watch deck would turn it into a disaster deck beside Nov 21, and the survey tape hero, because it asks a reader to learn a metaphor before the story.

## The spine

`assets/js/deck/2026-11-24-roofread-bespoke.js`. LOOK V2, tone WONDER (`TXT.V2_WORLD.wonder`, v2wonder), bespoke. Each frame owns its world, light, camera and type position. Shadows lean navy and violet, never black. Tones of the last six decks were explainer, win, people, wonder, explainer and watch. Wonder last ran Nov 19, and a reader learning to see a whole neighbourhood at once is the wonder register.

THE ACCENT is the wonder tone's own gold #ffcc00 and means ONE thing: THE WAY THROUGH, the route around damaged roads (c7, c21). It is never on a roof, a person or type. Frames 1, 4, 7 and 9.

THE COLOR CODE is not the accent. Judged roofs carry a three step cool ramp from the wonder tone's own family (ice, cerulean, cobalt violet), with no red, no legend and no class name, drawn to illustrate. Rims are HOLLOW before the review frame (6) and FILLED after it, which draws c19 as geometry, so no frame shows the AI deciding alone.

CONTINUITY: MOTIF_EVOLUTION, CAMERA_MOVE, EDGE_TEASE
1. MOTIF_EVOLUTION of the mosaic's state. Loose drone frames, then stitched with footprints aligned (3), one roof judged and hollow (4), the person checks (6), plates filled and the route driven (7), and bare roofs on undamaged Texas ground (9).
2. CAMERA_MOVE over one drawn neighbourhood, seeded once in the chassis. 38 m over it (1), down on a rural road (2), plan (3), 6 m over one roof (4), and frame 1's exact camera again at the close over Texas ground (9).
3. EDGE_TEASE. The gold route leaves frame 1's right edge, and the footprint rim cut by frame 3's right edge completes around the roof on frame 4.

### Palette

| token | hex | role |
|---|---|---|
| sky | TXLOOK.TONES.wonder | cobalt zenith over peach horizon |
| gumbo | #8a5a3c | Gulf Coast gumbo clay, cut faces, bare ground |
| lawn | #3f7d3a | St. Augustine lawn |
| shell | #efe6d2 | oyster shell road base |
| decking | #c79a62 | OSB roof decking where shingles are gone |
| tarp | #2f6fd6 | a blue poly tarp, vernacular |
| ice, cerulean, cobalt violet | from TXLOOK.palette("wonder") | the judged roof ramp |
| accent | #ffcc00 | the way through |

## THE NINE BEATS

1. AFTER THE STORM. Know: a tool reads drone imagery and returns a damage assessment within minutes. c1 c16.
2. THE OLD CLOCK. Know: the developers say it took 18 to 24 hours, and gathering damage information can take days. c2 c15.
3. STITCHED. Know: the images become one map aligned to building and road footprints, and roughly 2,000 buildings take about 7 minutes. c23 c16 c22.
4. ONE ROOF. Know: each individual building is rated. c5 c6.
5. WHAT IT LEARNED. Know: more than 21,000 damaged homes in 10 disasters, Harvey among them, 265 orthomosaics. c3 c4 c17.
6. A PERSON CHECKS. Know: a trained operator reviews every assessment, in the field, no wireless needed. c19 c20 c18.
7. THE ROAD OUT. Know: a road model finds damage and obstructions so crews route around them. c7 c21.
8. WHO HAS TRAINED. Know: 125 responders from 63 agencies in 14 states and Puerto Rico. c8.
9. BUILT IN TEXAS. Know: Florida's state drone team made it procedure, and the two documents name no Texas user yet. c9 c10, scoped absence.

Showstopper frame: 01
VALUE CUT: frame 6. The deck drops from the honey evening to cobalt dusk and a screen lit face, the one moment a person holds the map, and the value drop is that turn.
Tonal arc: honey evening over the judged neighbourhood (1), a cool working morning on a rural road (2), the even key of the relief bench (3), raking honey on one roof (4), warm window light inside a lab (5), cobalt dusk at a tailgate (6), honey from the other side as crews move (7), warm training room (8), and a peach Texas evening over an undamaged street (9).

## CRAFT PLAN

| slide | shot | largest object, and how it is modelled |
|---|---|---|
| 01 | AERIAL | a Gulf Coast subdivision of exactly FIG.buildings footprints, kit ranch_house and two_story_house in the near rows with roof damage and a tarp, instanced chassis roof_lod beyond, a chassis downed_oak with its gumbo root plate across one street, the gold route tube, TXT.sky v2wonder, TXT.contact under every near house |
| 02 | WIDE | a rural chip seal road receding on a long lens with 24 raised kit or chassis pavement markers, a tarped kit ranch_house, a leaning kit utility_pole with its line down, a kit person in a vest, TXT.sky, prairie ground |
| 03 | CLOSE | a TXBENCH plan relief of anodised drone frame plates settling into one gumbo clay plane, FIG.buildings footprint rims raised 1.5 mm, cast shadows plate on plate |
| 04 | CLOSE | one kit ranch_house roof with chassis roof_damage, OSB decking, nail rows, a tarp corner and sandbag lumps, a hollow chassis footprint_rim, kit live_oak limb, TXT.sky, contact everywhere |
| 05 | CLOSE | a chassis plate_rack of FIG.orthomosaics anodised plates on a steel cradle in a TXT.interior lab, one plate lifted by a gloved kit hand, window light |
| 06 | MEDIUM | a kit pickup tailgate and a kit person operator, a kit laptop seen from behind its lid, a hard case with the folded chassis survey_quad, TXT.sky cobalt dusk |
| 07 | MEDIUM | a kit utility_bucket_truck stopped at a junction behind a chassis downed_oak and standing water, the gold route turning right, filled roof plates beyond, kit person pointing |
| 08 | WIDE | a pegboard wall of FIG.responders chassis rescue_helmet models in five rows, a kit person hanging the last one, TXT.interior training room |
| 09 | AERIAL | frame 1's camera over an undamaged Texas street, kit ranch_house in limestone, kit live_oak, kit water_tower with its star, the gold route arriving from the left edge, TXT.sky v2wonder |

Showstopper frame: 01. Its depth is the descent from three big roofs at the bottom edge through the instanced carpet to a hazed horizon.
Tonal arc: it opens bright in honey evening (1), lifts to a cool morning (2) and the even relief (3), holds warm on the roof and lab (4, 5), is darkest at cobalt dusk on the operator (6), lifts again with honey on the road (7) and the warm room (8), and peaks brightest in the peach Texas evening (9).

---
```yaml
slide: 1
layout: FULL_BLEED
primary_image:
  subject: a Gulf Coast subdivision seen from 38 m at evening after a storm, three big brick roofs cut by the bottom edge, one stripped to tan decking with a blue tarp corner, an instanced carpet of roofs to a hazed horizon, every roof outlined with a thin hollow cool rim, a fallen live oak across one street and one gold route ribbon bending around it and leaving the right edge
  rect: [0, 360, 1080, 990]
  bleeds: [left, right, bottom]
accent: '#ffcc00'
data_in_art: {figure: buildings, drives: "roof count, the number of roofs drawn (near kit houses plus instanced roofs) equals FIG.buildings, asserted in the slide's own code"}
job: "Stop the thumb on a whole neighbourhood judged at once."
claims: [c24, c1, c16]
numerals: []
depth:
  eye: 38
  horizon: 0.2
  cues: [AERIAL, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. The slide artist composes the picture and places the type where this picture leaves quiet (knowledge/carousel/BESPOKE.md). An aerial oblique, because the claim is a whole area seen and judged at once.", bands: "Top fifth, the cobalt sky with the headline. Middle, the instanced carpet of roofs hazing to the horizon. Bottom third, the foreground, three big near brick roofs in raking light and long shadow, modelled at kit detail with shingle courses catching the honey key, the one stripped to tan decking with a blue tarp corner, the fallen live oak with its gumbo root plate casting across the street, and the gold route bending around it.", focal: "the stripped roof beside the fallen oak where the gold route bends"}
art: {technique: "physically based outdoor render, kit houses, chassis roof_lod, downed_oak and footprint_rim, TXT.sky v2wonder, TXT.ground, TXT.contact, TXT.weather", why_this_technique: "a whole neighbourhood only reads from the height a drone flies", palette: "brick and charcoal shingle, tan decking, blue tarp, lawn green, cool ramp rims, gold route", value_structure: "Frame median L* planned at 50. Lightest is the peach horizon and the lit roof planes. Darkest is the navy shade on the north faces."}
verbatim: []
acceptance: ["the subdivision of roofs owns at least 60 percent of the frame area at 432 px", "the near damaged roof covers at least 15 percent of the frame at 432 px and shows tan decking", "a horizon and sky are visible in the top quarter", "every visible roof carries a cool rim and no rim is filled", "the gold route is present, bends around the fallen oak and touches the right edge", "the footprint total in the slide's code equals FIG.buildings", "every near house has a contact shadow", "no rim colour is red and there is no legend", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["a distant dollhouse, so the three near roofs are big and cut by the bottom edge", "2,000 units as mush, so only the near rows are modelled in full and the rest is a texture gradient"]
type:
  kicker: "After the storm"
  hook: "Every roof, read in minutes"
  dek: "Texas A&M's CLARKE reads drone imagery after a disaster and returns a detailed damage assessment within minutes. Neighborhood and colors drawn to illustrate."
```

---
```yaml
slide: 2
layout: FIGURE_SCALE
primary_image:
  subject: a rural chip seal road receding across the frame on a long lens with 24 raised pavement markers at one even spacing, the last six standing on a peach band, a tarped ranch house at the near end with a responder in a vest, and a utility pole leaning with its line down to the verge
  rect: [0, 480, 1080, 870]
  bleeds: [left, right]
accent: none
data_in_art: {figure: hours_high, drives: "the marker count equals FIG.hours_high and the band starts at marker FIG.hours_low, one marker per hour, read in the slide's own code"}
job: "Make a long wait physical without a chart."
claims: [c2, c15]
numerals:
- {value_from: c2}
depth:
  eye: 2
  horizon: 0.38
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 70}
composition: {structure: "BESPOKE. A long lens side view so the markers read evenly spaced like a ruler.", bands: "Top, a pale morning sky. Middle, the road and its markers across the frame. Bottom third, the ditch and verge in violet shade, prairie grass blades lit at their tips by the morning key, gravel shoulder texture and the pole's downed line lying in the grass, with the type seated in the shade.", focal: "the six markers on the peach band"}
art: {technique: "physically based outdoor render, kit ranch_house, utility_pole, person, chassis pavement markers, TXT.sky, TXT.ground", why_this_technique: "an hour is a countable mark on a road a responder drives", palette: "chip seal grey brown, prairie gold, peach band, tarp blue", value_structure: "Frame median L* planned at 55. Lightest is the morning sky. Darkest is the ditch shade."}
verbatim: []
acceptance: ["the rural chip seal road with its 24 raised markers spans the full frame width and is modelled with a shoulder and texture, and the frame fails without it", "the road and markers band is at least 90 px tall at 432 px", "24 markers are drawn, counted in the slide's code from FIG.hours_high", "each marker reads as a separate highlight at 432 px", "the peach band begins at the marker index FIG.hours_low", "the leaning pole and its downed line are visible", "the person is under a fifth of the frame height with a lit face", "nothing drawn stands for minutes and no ratio is printed", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["the band reading as a red zone, so it is low chroma peach and never the accent"]
type:
  kicker: "The old clock"
  hook: "18 to 24 hours, the old way"
  dek: "Tom Manzini of the development team says CLARKE turns drone imagery into damage assessments in minutes instead of 18 to 24 hours. Gathering damage information can take days, particularly in rural areas. Roadside marker posts count off the hours."
```

---
```yaml
slide: 3
layout: DIAGRAM
primary_image:
  subject: a plan relief in which loose anodised drone frame plates, each carrying a patch of neighbourhood in shallow relief, overlap and cast shadows on the left and settle flush into one stitched clay plane on the right, where the building footprint rims and a road footprint ribbon rise out of it, one rim cut by the right edge
  rect: [0, 300, 1080, 1050]
  bleeds: [right, bottom]
accent: none
data_in_art: {figure: buildings, drives: "rim count, the number of raised footprint rims on the stitched plane equals FIG.buildings, asserted in the slide's own code"}
job: "Show many pictures becoming one map aligned to footprints."
claims: [c23, c16, c22]
numerals:
- {value_from: c16}
depth:
  eye: 0
  horizon: 0
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. A plan material relief, because an orthomosaic is flat in life.", bands: "Top third, a quiet gumbo clay margin with the type. Middle third, loose anodised plates overlapping at left, each with roofs in 3 mm relief and casting onto the plate below, meeting the stitched plane at right. Bottom third, the stitched clay plane with raised footprint rims, a road footprint ribbon and live oak domes in relief, shaded by the loose plates' casts.", focal: "the seam where loose plates become one plane"}
art: {technique: "TXBENCH material relief, anodised plates, gumbo clay ground, satin rims", why_this_technique: "stitching is a flat operation and reads best in plan with real casts", palette: "anodised blue and silver plates, gumbo clay, cool rims", value_structure: "Frame median L* planned at 52. Lightest is the plate bevels. Darkest is the casts under loose plates."}
verbatim: []
acceptance: ["the relief of plates and stitched plane owns at least 70 percent of the frame area", "the relief report shows at least three materials and cast shadows", "loose plates cast onto plates on the left half", "the rim count in the slide's code equals FIG.buildings", "one rim is cut by the right edge", "at 432 px it reads as a stitched aerial and not a chart", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["a top down tray reading as a chart, so the loose half carries tall plates and long casts"]
type:
  kicker: "Stitched first"
  hook: "Many pictures, one map"
  dek: "The drone images are stitched into one georectified orthomosaic and aligned to building and road footprints. Given a finished orthomosaic, the project site says CLARKE assesses roughly 2,000 buildings in about 7 minutes."
```

---
```yaml
slide: 4
layout: CLOSE_CROP
primary_image:
  subject: one brick ranch house roof from 6 m above the eave, a patch stripped to tan OSB decking with nail rows and torn shingle courses, a blue tarp corner with sandbags, a live oak limb across the ridge, a hollow cool rim hugging the walls, and a short length of the gold route on the street beyond
  rect: [0, 280, 1080, 1070]
  bleeds: [right, bottom]
accent: '#ffcc00'
data_in_art: null
job: "Make the judgement specific to one building."
claims: [c5, c6]
numerals: []
depth:
  eye: 6
  horizon: 0.05
  cues: [FORM_SHADING, CAST_SHADOW, OCCLUSION, TEXTURE_GRADIENT]
  subject_at: {X: 0, Z: 9}
composition: {structure: "BESPOKE. A close oblique so damage reads in relief under a raking key.", bands: "Top third, the shadowed street asphalt and lawn at top left with the type, the gold route on the street beyond. Middle third, the roof ridge with the live oak limb across it and the tarp corner with sandbag lumps. Bottom third, the stripped decking patch with nail rows and torn shingle courses lit by the raking key and casting fine shadow lines, the decking texture in the foreground, the hollow rim along the eave, cut by the right and bottom edges.", focal: "the stripped decking patch"}
art: {technique: "physically based outdoor render, kit ranch_house with chassis roof_damage and footprint_rim, kit live_oak, TXT.sky", why_this_technique: "a raking key makes each missing shingle course cast a shadow", palette: "charcoal shingle, tan decking, tarp blue, brick, cool rim, gold", value_structure: "Frame median L* planned at 48. Lightest is the decking in the key. Darkest is the eave shadow."}
verbatim: []
acceptance: ["the roof covers at least 55 percent of the frame", "decking and nail rows are visible at full size", "the rim is hollow and continuous around the footprint", "a short gold route is visible on the street", "contact shadows under the house and fence", "the dek says the colors are drawn to illustrate", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["a primitive house, so the kit ranch_house is used at full detail"]
type:
  kicker: "Structure by structure"
  hook: "Then every roof is judged"
  dek: "The Building Damage Assessment rates the damage to each individual building and gives responders a color coded view, structure by structure. Colors drawn to illustrate."
```

---
```yaml
slide: 5
layout: OBJECT_AND_CAPTION
primary_image:
  subject: a long steel cradle of anodised plates on a lab bench, each plate's top edge showing a sliver of neighbourhood relief, one plate lifted by a gloved hand to show a stitched neighbourhood, window light across the plate edges
  rect: [0, 330, 1080, 960]
  bleeds: [left]
accent: none
data_in_art: {figure: orthomosaics, drives: "the plate count equals FIG.orthomosaics in the slide's own code"}
job: "Give the training data weight and a Texas thread."
claims: [c3, c4, c17, c25]
numerals:
- {value_from: c3}
- {value_from: c17}
depth:
  eye: 1.6
  horizon: 0
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, FORM_SHADING]
  subject_at: {X: 0, Z: 2}
composition: {structure: "BESPOKE. A raking three quarter along the rack so plates read as strata.", bands: "Top third, the lab wall in violet shade with a window throwing warm light. Middle third, the rack of plates running out of the left edge with the lifted plate held above it. Bottom third, the lower plate edges catching the window as fine strata, the powder coated cradle and its contact shadow on the bench, with the type on the bench apron.", focal: "the lifted plate"}
art: {technique: "physically based interior render, chassis plate_rack, kit person hand, TXT.interior", why_this_technique: "a dataset becomes a countable physical archive", palette: "anodised aluminium, powder coated steel, warm window, violet wall", value_structure: "Frame median L* planned at 50. Lightest is the window and plate edges. Darkest is the violet back wall."}
verbatim: []
acceptance: ["the plate rack spans at least 70 percent of the frame width and the lifted plate is at least 120 px wide at 432 px", "the plate count in the slide's code equals FIG.orthomosaics", "the lifted plate reads as a neighbourhood at 432 px", "the hand is lit from the camera side", "the room is visible and not black", "the dek says one plate stands for one orthomosaic", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["265 plates merging into one block, so the rack rakes and edges catch the window"]
type:
  kicker: "What it learned"
  hook: "Taught partly on Harvey"
  dek: "The models learned from drone imagery of more than 21,000 damaged homes in 10 major disasters, Hurricane Harvey and Hurricane Ian among them. One plate stands for one of the dataset's 265 orthomosaics, drawn to illustrate."
```

---
```yaml
slide: 6
layout: OBJECT_AND_CAPTION
primary_image:
  subject: an operator in a vest at a pickup tailgate at cobalt dusk, a laptop seen from behind its lid lighting the face, a hard case holding a folded drone, and a leaning utility pole with its line down behind
  rect: [380, 420, 700, 930]
  bleeds: [right, bottom]
accent: none
data_in_art: null
job: "Put a person's hand on the map before anyone acts on it."
claims: [c19, c20, c26, c18]
numerals: []
depth:
  eye: 1.4
  horizon: 0.55
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 2, Z: 6}
composition: {structure: "BESPOKE. A medium portrait lit by the screen and a low key.", bands: "Top third, cobalt dusk sky over the prairie with the leaning pole silhouetted. Middle third, the operator at right, face lit by the laptop, the open tailgate and the hard case with the folded drone, the type in a left column over the sky. Bottom third, the caliche shoulder with tire ruts, the truck's navy contact shadow and the operator's boots seated on the gravel.", focal: "the operator's lit face over the laptop"}
art: {technique: "physically based outdoor render, kit pickup, person, laptop, chassis field case with survey_quad, TXT.sky", why_this_technique: "trust is one person at one screen", palette: "cobalt dusk, warm screen glow, vest orange, caliche", value_structure: "Frame median L* planned at 38. Lightest is the screen glow on the face. Darkest is the navy truck shadow, never black."}
verbatim: []
acceptance: ["the operator and the pickup tailgate together own at least 30 percent of the frame area, and the operator stands at least 150 px tall at 432 px", "no laptop screen face is visible to the camera", "the operator's face is lit and is not a silhouette", "contact shadows under the truck and boots", "no antenna or dish is drawn", "near black at most 0.25 of the frame", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["a mannequin face, so the operator turns three quarters and the face is lit from the camera side"]
type:
  kicker: "Reviewed"
  hook: "A person checks every map"
  dek: "A trained operator reviews every assessment before it reaches decision makers. CLARKE's models are designed to run entirely in the field. No wireless transmission of imagery is needed to generate an assessment. Its results come out as GeoJSON and KML map files."
```

---
```yaml
slide: 7
layout: FULL_BLEED
primary_image:
  subject: a lineman bucket truck stopped at a residential junction behind a fallen live oak and its torn root plate, standing water on the street ahead reflecting the sky, the gold route turning right in front of the bumper and leaving the right edge, filled roof plates on the houses along the block, a crew member pointing
  rect: [0, 330, 1080, 1020]
  bleeds: [left, right, bottom]
accent: '#ffcc00'
data_in_art: null
job: "Show what a crew does with the map."
claims: [c21, c7, c19]
numerals: []
depth:
  eye: 3.5
  horizon: 0.3
  cues: [RELATIVE_SIZE, CAST_SHADOW, OCCLUSION, AERIAL]
  subject_at: {X: 0, Z: 12}
composition: {structure: "BESPOKE. Foreground occlusion with a diegetic route.", bands: "Top third, sky with the type at top right over the roofs with filled plates. Middle third, the bucket truck and the fallen oak with its root plate. Bottom third, the foreground of wet asphalt with texture and the oak's long shadow, the standing water reflecting the lit sky, curb and gutter, and the gold route turning right past the bumper.", focal: "the gold route turning past the bumper"}
art: {technique: "physically based outdoor render, kit utility_bucket_truck, person, road, chassis downed_oak and footprint plates, TXT.sky", why_this_technique: "a route is a choice made at a junction", palette: "truck white, oak green, gumbo root plate, water reflecting cobalt, gold route", value_structure: "Frame median L* planned at 48. Lightest is the water's sky reflection. Darkest is shade under the oak."}
verbatim: []
acceptance: ["the gold route touches the right edge", "every roof plate in view is filled", "the root plate and trunk cast onto the asphalt", "the water reflects the sky", "the truck and oak fill at least 40 percent of the frame", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["a boxy toy truck, so the kit truck is used and placed large"]
type:
  kicker: "Road by road"
  hook: "The road out"
  dek: "A road model identifies road damage and obstructions. Crews can then find routes around damaged roads and other obstacles. Filled roofs show assessments after review, drawn to illustrate."
```

---
```yaml
slide: 8
layout: FIGURE_SCALE
primary_image:
  subject: a pegboard wall of rescue helmets in five rows, seeded shell colours of white, yellow, orange and navy, each with a lit crown and a cast on the board, one responder turned away hanging the last helmet, window light from the right
  rect: [0, 250, 1080, 900]
  bleeds: [left]
accent: none
data_in_art: {figure: responders, drives: "the helmet count equals FIG.responders in five rows, read in the slide's own code"}
job: "Make the trained responders a countable field."
claims: [c8]
numerals:
- {value_from: c8}
depth:
  eye: 1.6
  horizon: 0
  cues: [RELATIVE_SIZE, CAST_SHADOW, FORM_SHADING]
  subject_at: {X: 0, Z: 3}
composition: {structure: "BESPOKE. A raking view along the wall so each helmet shows crown, front and cast.", bands: "Top third, the upper helmet rows running off the top and left edges. Middle third, the middle rows with lit crowns and casts on the pegboard, and the type in a right column on plain painted block. Bottom third, the lowest helmet rows, the responder's arm and the last helmet, the pegboard's holes in raking light and a bench below.", focal: "the last helmet in the responder's hand"}
art: {technique: "physically based interior render, chassis rescue_helmet, kit person, TXT.interior", why_this_technique: "a count reads best as objects on a wall", palette: "helmet white, yellow, orange, navy, painted block, warm window", value_structure: "Frame median L* planned at 55. Lightest is the white shells. Darkest is the violet shade at left."}
verbatim: []
acceptance: ["the helmet wall owns at least half of the frame area and each helmet is at least 14 px wide at 432 px", "the helmet count in the slide's code equals FIG.responders", "each helmet shows a lit crown and a cast at 432 px", "no red shell", "the person is turned away and under a fifth of the frame", "the dek says one helmet stands for one responder", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["125 units as dots, so the helmets are large and rows few"]
type:
  kicker: "Who has trained"
  hook: "125 responders, 63 agencies"
  dek: "Texas A&M says 125 emergency responders from 63 agencies in 14 states and Puerto Rico have trained on CLARKE. One helmet stands for one responder."
```

---
```yaml
slide: 9
layout: FULL_BLEED
primary_image:
  subject: frame 1's exact camera over an undamaged Texas street at peach evening, limestone ranch houses with bare roofs, live oaks, caliche verges, a water tower with its star on the horizon, and the gold route arriving from the left edge onto the street
  rect: [0, 400, 1080, 950]
  bleeds: [left, right, bottom]
accent: '#ffcc00'
data_in_art: {figure: buildings, drives: "roof count, the Texas street tile carries FIG.buildings roofs, the same tile size as frame 1, asserted in the slide's own code"}
job: "Turn the story home and name what to watch for."
claims: [c24, c9, c10]
numerals:
- {value_from: c10}
depth:
  eye: 38
  horizon: 0.2
  cues: [AERIAL, RELATIVE_SIZE, CAST_SHADOW, OCCLUSION]
  subject_at: {X: 0, Z: 0}
composition: {structure: "BESPOKE. Frame 1's camera on Texas ground, the mirror is the argument.", bands: "Top third, peach sky with the water tower on the horizon and the type. Middle third, the undamaged street of limestone ranch houses and live oaks receding. Bottom third, three big near limestone roofs with standing seam and shingle catching the low key, live oak crowns casting on the caliche verge, and the gold route arriving from the left edge onto the street.", focal: "where the gold route reaches the street"}
art: {technique: "physically based outdoor render, kit ranch_house, live_oak, water_tower, road, TXT.sky v2wonder", why_this_technique: "the same camera on a different ground makes the turn without a word", palette: "limestone, live oak green, caliche, water tower white, peach sky, gold route", value_structure: "Frame median L* planned at 58. Lightest is the peach horizon. Darkest is live oak shade."}
verbatim: []
acceptance: ["the Texas street of roofs owns at least 55 percent of the frame area at 432 px", "the roof count in the slide's code equals FIG.buildings", "the camera values in source match frame 1", "no roof shows damage and no rim is drawn", "the gold route touches the left edge and reaches the street", "the water tower carries no name", "the absence in the dek names both documents", "no numeral on this slide is absent from claims.json or figures.json"]
risks: ["implying Texas refuses it, so the picture is neutral and the words carry the scoped absence"]
type:
  kicker: "Built in Texas"
  hook: "Texas A&M says Florida's team uses it"
  dek: "Texas A&M says Florida's state drone team now uses CLARKE as standard operating procedure. It was deployed in Florida and Pennsylvania in the 2024 hurricane season. The November 24th release and the project site name no Texas agency or county among its users. Street drawn to illustrate. Watch for the first."
```
