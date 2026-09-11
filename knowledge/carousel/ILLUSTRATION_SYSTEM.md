# The illustration system — how a frame gets an IMAGE

Written 2026-09-11, the upgrade session after carousel no. 21, on the owner's instruction that
the artwork was "very mediocre" and had to be a different order of thing by the next run. This
file is the whole of that answer in one place: the diagnosis, the law, the ten layouts, the print
register, the five libraries, the order of work, and the gate that reads the pixels afterwards.
**Read it before the directors room. Read it again before the art build.** The example that
shows all of it working is `examples/editorial-deck/`, nine frames with their storyboard, and
its contact sheet is what a director should look at before pitching.

## The diagnosis, so the cure is not mistaken for taste

Twenty one decks shipped and three judges found the same thing under all of them in different
words. "Assembled, not drawn." "An object in a void." "A diagram of a place." "Two planes and two
books." "Clip art." "The same page nine times." Every one of those decks passed every gate,
because every gate asks whether what is on the frame is RIGHT and none asked whether there was an
image on it at all.

The cause was structural, four ways at once, and none of them was a lapse of taste:

1. **Nothing had a size.** Every frame was drawn in screen pixels with no camera. A bus was a
   slab because a slab is what you draw when you do not know how tall a bus is, and nothing
   stood on anything or cast a shadow onto anything.
2. **One skeleton.** Kicker top, headline under it, a small drawing under that, source line at
   the bottom. Where the image went and how much of the page it took was never decided per
   frame, so it was the same on all nine.
3. **Surfaces instead of subjects.** The technique library is atmospheres, fields, plates and
   grades. Those are what a frame is made OF. None of them is what a frame is a picture OF, and
   a run reaching for a technique reached for a surface.
4. **Nobody in the picture.** A deck about a school, a hearing room, a grid crew or a ward drew
   the room and nobody in it. A figure gives every object beside it a size, gives the reader
   somewhere to stand, and turns a statistic into a count of people.

So the cure is not a nicer gradient. It is a camera, a subject drawn at true scale, a decision
per frame about where the image goes, a print register that says a hand made it, and a gate.

## THE PRIMARY IMAGE LAW

**Every frame carries one drawn subject that owns at least thirty percent of the frame, reads
as one silhouette at feed size, and on most frames runs off at least one edge.** The type is
placed around the image, never the other way round. The dossier names the subject, the rect it
owns in frame px and the edges it bleeds, and `scripts/carousel/layout_check.py` reads the
pixels afterwards and refuses a frame whose rect turns out to hold a flat plate with words on it.

What follows from it:

- **The image is planned first and drawn first.** A frame's dossier opens with `layout` and
  `primary_image`. Its code draws the image before a line of type exists, and the type is fitted
  into the reserve the image leaves.
- **A subject is a THING.** A bus, a courthouse, a pump jack, a person at a desk, a sheet of
  paper, a page of a rule, a county. A field, a haze, a gradient, a wash and a grain are not
  subjects. They are what the subject stands in.
- **True scale or no scale.** If the subject is a physical thing it is drawn in metres on the
  scene bench beside something whose size a reader knows, which is usually a person.
- **Most frames bleed.** A subject cropped by the frame is inside the reader's space. A subject
  floating in the middle with margin all round is a postage stamp, and a deck of postage stamps
  is what the judges called "objects in a void". At least four frames of nine bleed an edge.
- **One accent per deck, used with restraint.** One colour from `config/brand.yaml`, never the
  flag red, present on three to six frames and never over eight percent of any frame. The rest
  of the deck is paper and ink.
- **One light per scene.** Declared once, in the camera, and every shadow in the scene falls
  from it.

## THE TEN LAYOUTS, and the rotation

The table lives in `assets/js/txlayout.js`, in the browser and in Node, and `layout_check.py`
carries a copy its self-test asserts against that file. The names:

| archetype | the image | the type |
|---|---|---|
| **FULL_BLEED** | fills the frame edge to edge | one reserve, a band top or bottom, kept quiet by the scene itself (a black ceiling, a dark sky, `TXINK.reserve`) |
| **SPLIT_HORIZON** | one side of one straight horizontal cut, at least 55 percent of the height | the other side, on flat ground |
| **TYPE_AS_OBJECT** | the headline IS the image, carved, cast, stacked, extruded, poured | the rest is small. At most one per deck |
| **OBJECT_AND_CAPTION** | one object drawn large on a ground plane with a horizon, the poster | a short caption beside or under it |
| **DIAGRAM** | a drawing annotated with leaders and mono labels, the thing explained | the labels ARE the type |
| **GRID** | repeated units at true scale, the isotype, a count a reader can count | a headline and a number under each unit |
| **DOCUMENT** | a drawn page, form, screen, ledger or letter with its own typography inside it | the type on the page is image, not caption |
| **MAP** | cartography from `assets/geo/`, places named | a caption, and the labels on the map |
| **CLOSE_CROP** | the subject cropped by at least two edges, at detail scale, the reader inside it | one reserve |
| **FIGURE_SCALE** | a person at true scale beside the thing, so the thing has a size | in the sky or ground the composition leaves empty |

**The rotation over nine frames:** no archetype twice in a row, at least five distinct,
TYPE_AS_OBJECT at most once, FULL_BLEED and CLOSE_CROP at least two between them, at least four
frames bleeding an edge. Check the sequence before any dossier is written:

    node -e 'require("./assets/js/txlayout.js"); console.log(TXLAYOUT.check(["FULL_BLEED","DOCUMENT","FIGURE_SCALE","OBJECT_AND_CAPTION","GRID","DIAGRAM","CLOSE_CROP","SPLIT_HORIZON","FULL_BLEED"]))'

An empty list is a plan. Anything else is a rewrite before a single dossier.

**Which layout wants which claim.** A claim about a thing wants OBJECT_AND_CAPTION or
CLOSE_CROP. A claim about a place wants FULL_BLEED or SPLIT_HORIZON. A claim that is a document's
own words wants DOCUMENT. A count wants GRID. A mechanism wants DIAGRAM. A where wants MAP. A
"how big" wants FIGURE_SCALE. A single phrase that is the whole story wants TYPE_AS_OBJECT, once.

## THE PRINT REGISTER

A gradient is what a screen does when nobody decided anything. A print is a set of decisions: a
paper, an ink, a screen that turns tone into marks a reader can see, a contour that says a hand
drew the edge, and plates that do not quite register. That is why an illustration in a magazine
looks made and a stock vector looks placed, and it is the whole surface of this system.

`TXINK.print` does it in one call. The scene is drawn in GREYS into an offscreen twin, then:

1. **Paper.** The ground colour with fibre and a faint mottle. Night paper (`#0F0C1C`) is the
   house default because the brand caps light decks at one in eight. A light deck is the same
   pipeline with a pale paper and dark ink.
2. **Screen.** The twin's tone becomes marks in the ink. Four screens, and the choice is named
   in the dossier and held by the critic:
   - `halftone`, round dots on a rotated grid, the newspaper photograph. Cell 6 to 9.
   - `line`, parallel lines whose weight carries the tone, the banknote. Cell 4 to 6.
   - `hatch`, three threshold passes at three angles, the engraver's cross hatch. Cell 6 to 8.
   - `stipple`, jittered dots whose count carries the tone, the field guide, stars, stone.
     Cell 5.
   Under cell 4 a screen becomes texture and stops being a mark. Over 12 the tone breaks up.
3. **Contour.** A Sobel on the twin, laid as ink a pixel or so out of register. This is what
   makes a flat shape read as drawn.
4. **The accent plate.** Anything that must stay flat colour is painted last in `over`: the one
   accent, and any type reserve (`TXINK.reserve`).

Vary the screen across the deck the way the layouts vary. A deck that is nine halftones is
one drawing nine times in a new way.

## THE FIVE LIBRARIES

All under `assets/js/`, all deterministic per seed, all loaded with `@@ASSETS@@/js/<name>.js`,
in this order because each needs the one before: `txscene.js`, `txfig.js`, `txobjects.js`,
`txink.js`, `txlayout.js`. `noise.js` and `txtype.js` as before.

### txscene.js — the camera and the ground

A pinhole camera at `eye` metres above a flat ground, looking level, horizon at `horizon` px,
focal length `f` px. World X is lateral, Y is up, Z is depth. Everything in metres.

```js
const S = TXSCENE.create(cx, { w:1080, h:1350, eye:1.4, horizon:640, f:820, sky:"#000",
                               fogZ:1e9, light:{ az:-40, el:38 } });
S.ground({ near:0.8, far:400, fill:"#4A4A4A" });          // the plane, far to near
S.gridZ({ dz:4, from:2, to:120, ink:"rgba(0,0,0,.3)" });   // joints of constant depth
S.strip({ X:-6, w:7, near:1, far:500, fill:"#333" });      // a road
S.shadow(sprite, { X:6, Z:30, ink:"#000", alpha:.5 });    // the ground shadow, from the light
S.sprite(sprite, { X:6, Z:30, inks:{ ink:"#DCDCDC", paper:"#141414", accent:"#DCDCDC" } });
S.box({ X:20, Z:60, w:30, h:9, d:40, fill:"#B9B4A5" });    // a shaded block with a hull shadow
S.rectBox({ X, Z }, { x, y, w, h })                        // a local rect's screen box, to mount type on a sign
S.project(X, Y, Z); S.groundY(Z); S.ppm(Z);                // the arithmetic, when you need it
```

Draw far things first. The bench does not sort. **Every scene declares one light** (`az`
degrees from the camera axis, `el` above the horizon, 8 to 75) and every shadow falls from it.
The sun 16 degrees up throws the long shadows of a poster at dusk. 50 degrees is noon.

Two cameras worth knowing. **Standing eye** (1.6 to 1.7 m, horizon around 0.55 to 0.67 of the
height) for places. **Seated eye** (1.05 to 1.15 m) for rooms. A **long lens** (f 2400 at Z 16)
flattens a row of units to equal size for a GRID. A **low horizon** (horizon 0.65 and up) with a
tall subject bleeds the top for FIGURE_SCALE.

### txfig.js — people

```js
TXFIG.figure({ pose:"walk", height:1.7, hat:"hard", hold:"clipboard" })
TXFIG.figure({ view:"front" })                    // the isotype front view, for counts
TXFIG.figure({ pose:"sit", seat:0.45 })           // seated, at a desk or a dais
TXFIG.crowd(12, { seed:7, hats:["hard"], holds:["bag"], children:true })
```

Poses: `stand walk stride point wave raise phone carry sit crossed lean`. Hats: `hard brim
cap`. Held things: `briefcase box placard clipboard phone bag`. Eight head canon, 1.70 m unless
told otherwise, `child:true` for a child's proportions. Mirror through TXSCENE to face left.

A person is not decoration. Use one where the claim has a person in it: the student the rule
is for, the lineman on the pole, the commissioner behind the dais, the queue at the counter.

### txobjects.js — the catalogue

Forty four objects at true scale. `examples/objects/catalogue-1.jpg` and `catalogue-2.jpg`
show every one beside a 1.7 m figure, and that is the page to look at before choosing a
subject.

    vehicles     school_bus sedan (sensor:true for a robotaxi) pickup truck_semi ambulance
    the grid     utility_pole (transformer:true) transmission_tower wind_turbine pump_jack
                 substation data_center power_plant cooling_tower solar_panel
                 battery_container server_rack
    water, land  water_tower windmill stock_tank live_oak pine mesquite cattle fence_post
    buildings    house (style:"two_story") school civic_facade (dome:true) capitol hospital
                 warehouse strip_mall
    the street   road_sign (kind:"stop") billboard camera_pole streetlight traffic_signal
    interiors    desk office_chair student_desk dais podium hospital_bed filing_box
                 pallet_boxes voting_booth
    the air      drone helicopter

`TXOBJ.sprite(name, opts)`. Bodies are ink, details are paper, and `{ body:"accent" }` paints
one object in the accent. `TXOBJ.wire(S, [X,Z,Y], [X,Z,Y])` strings a catenary between two
points, so a row of poles reads as a line. `TXOBJ.fence(S, [x0,z0], [x1,z1])` runs a fence.
Objects that come in populations (`live_oak`, `house`) take `seed` and vary.

A subject that is not in the catalogue is drawn as parts in metres with `TXSCENE.sprite(parts)`,
four part kinds: `poly`, `rect`, `ellipse`, `line` (thick, round capped). The tablet in frame 6
of the example deck is nine lines. When a run draws one worth keeping, it goes in the backlog as
a proposal for the catalogue.

### txink.js — the print

```js
TXINK.print(cx, {
  ground:"#0F0C1C", ink:"#EDE6D6", fibre:0.05, seed:21,
  screen:{ mode:"halftone", cell:6, angle:22, gamma:1.15, floor:0.05 },
  edges:{ threshold:20, width:1.4, alpha:0.8, dx:1.0, dy:-0.8 },
  draw:  function (a) { /* the scene, in greys, on a */ },
  over:  function (c) { TXINK.reserve(c, { ground:"#0F0C1C", bottom:200, bottomSolid:130 });
                        /* the accent plate */ }
});
```

The pieces are separate when you need them: `TXINK.canvas`, `screen`, `edges`, `duotone`,
`posterise`, `tint`, `paper`, `press`, `wobble` (an SVG path redrawn by hand), `hatchFill`.

**The reserve rule.** Type never sits on a screen. The scene keeps the type's zone dark by
construction (a black ceiling, the sky above the horizon glow, the floor falling to black away
from the pool of light) or `TXINK.reserve` fades the print to paper under the furniture band.
The furniture band is 130 px top and bottom. A frame whose only quiet zone is the reserve is
still a frame with an image on it, which is the point.

### txlayout.js — the table and the furniture

`TXLAYOUT.check(sequence)` at plan time. `TXLAYOUT.mount(document.body, { kicker, kicker2,
counter, src, ink })` writes the kicker, the counter and the source line in their fixed
positions, so bespoke code is only ever the image and the headline. **The site line is static
HTML in every slide**, `<div class="tx-site" id="site">texasaidocket.com</div>` with the
`.tx-site` rule the example slides carry, because `coherence_check` reads it from the FILE with
a regex and a line a script mounts is not in the file. `mount` throws if asked for it.
`TXLAYOUT.reserve(arch)` is where the type goes for each archetype, as a starting rect.

## THE ORDER OF WORK, which is half of the craft

1. **Rotation before dossiers.** Write the nine layouts as a list, run `TXLAYOUT.check`, then
   assign a subject to each, then write the dossiers. A dossier written before its layout is a
   dossier for the one skeleton.
2. **Frames 7, 8 and 9 first.** Every judged deck was thinnest at the end, because the budget
   ran out where the argument lands. Build the close first, then the turn, then the open.
3. **Image before type, on every frame.** Draw the scene, render it, look at it at 432 px with
   no type on it. If it is not an image yet, no headline will make it one.
4. **One frame, one screen, one light.** Declared in the dossier, held by the critic.
5. **Then the type,** into the reserve the image left. `TX.fitText` for the hook. The furniture
   through `TXLAYOUT.mount`.
6. **Then the gates,** `qa.py` and `layout_check.py --require`, before any critic sees a
   frame. A critic's round costs more than a gate's, and the gate is what finds the plate.

## THE GATE, so this is a law and not a mood

`scripts/carousel/layout_check.py` reads `storyboard.md` and the renders and measures:

    1  the rotation over the nine `layout` values
    2  each `primary_image.rect` at least 0.30 of the frame
    3  at least four rects touching a frame edge, and every declared bleed real
    4  detail inside the rect, on the pixels: a quarter of the 8 px cells that are not under
       type carry a luminance std over 6 (a DOCUMENT's type counts as its image)
    5  a silhouette at thumb scale: the subject covers 8 percent of the rect and one piece
       holds half of it (a GRID must come apart into four or more pieces instead)
    6  the accent: present on three to six frames, never over 8 percent of one, never flag red

The routine runs it with `--require`, so a deck with no `layout` keys is a run that did not
plan its layouts, and that is a fail. The example deck measures clean on all six. Carousel no.
21, given full frame rects and measured the same way, fails 4 or 5 on seven of nine frames,
which is the finding the judges made in words and the number that says the gate is aimed at it.

## What still fails, named so nobody rediscovers it

- **A subject at the wrong distance.** A 60 m school at Z 58 is 30 px tall on a phone. Bring
  the subject in until it owns its rect, and let something else carry the distance.
- **A crowd as a mass.** Figures at the same tone as the furniture beside them merge into one
  pale shape. Give the figures and the objects different greys in the twin.
- **A screen under type.** The contrast gate will catch it and the critic will fail it. The
  scene keeps the reserve dark, or `TXINK.reserve` does.
- **A ring or a leader through a letter.** Draw marks beside type in the DOM (an SVG path), and
  end every leader short of the glyph band. `qa.py` reads a canvas stroke through a line as a
  strikethrough, and it is right.
- **Rotated DOM text.** The QA's line boxes are axis aligned and rotated lines overlap. Rotate
  the drawn sheet a degree if you must, never the type by more than that.
- **The accent everywhere.** One object, one stroke, one window. Three to six frames.
- **Nine halftones.** Vary the screen with the layout.
- **A slab where a thing should be.** If it is not in the catalogue, draw it in metres from
  parts, and put it in the backlog.
- **Nine frames that are one call.** `bespoke_check` compares slide CODE and fails a deck at a
  median similarity of 0.55. The print pipeline is shared by design, so the scene inside each
  frame's `draw` has to carry its own drawing. The example deck measures 0.46 with every frame
  a different scene, and a deck that copies a frame and swaps the object will not.
- **A site line a script wrote.** `coherence_check` reads `class="tx-site"` from the HTML
  file. The line is static in every slide, never mounted.
