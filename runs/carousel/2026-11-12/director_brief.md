# Director brief, carousel no. 75, November 12th, 2026

## The story (docket item tx-2026-0188)

The Texas Department of Motor Vehicles now publishes who is allowed to run automated vehicles
commercially on Texas roads. Its Company and Vehicle Summary Report, data as of October 29th,
2026, lists 17 companies and 3,164 automated motor vehicles authorized under Senate Bill 2807,
enforceable since May 28th, 2026. Two companies hold most of them: Waymo 1,259 and Tesla Robotaxi
1,080. Then Avride 344, Aurora 91, Gatik 64, Zoox 63, Nuro 47, Atlas Energy Solutions (an
oilfield sand hauler) 38, Kodiak 36, Torc 32, Stack 31, May Mobility 22, Bot Auto 13, Waabi 13,
MOIA 12, PlusAI 12, International Transport Eng 7.

The honest counter-image. An authorization has no fee and no expiry, valid until revoked. The
department says statute does not let it require crash history (Dallas asked it to). It treats an
operation as endangering the public at serious bodily injury, and says enforcement below that
standard is unlikely. And a vehicle on the list is not a vehicle with nobody in it: Volvo and
Waabi's trucks between Dallas and Houston run with an observer in the driver's seat, and Kodiak
and Charger's between Dallas and Laredo with a safety driver behind the wheel.

The question for a Texan: who is now allowed to drive without a driver on my roads, how many, and
what does the state actually ask of them. Next step for the close: anyone can read the list, and a
concern involving serious bodily injury goes to the department's Enforcement Division (claims will
confirm the exact route).

Verified claims: `out/2026-11-12/claims.json` (read it; every slide string traces to a claim id).
Every share, ratio or total a frame draws is computed by `out/2026-11-12/compute.py`, never typed.

## Variety exclusions (last 30 days)

- Waymo San Antonio robotaxis, no. 59 (October 16th). Do not redraw a robotaxi at an airport curb.
- Aurora Q3 letter, no. 66 (November 3rd): semi trucks at weigh stations, Dallas to Laredo in primer.
- No. 74 (yesterday): survey lath, tidal flats, dark hearing room, city limit sign. No. 73: machine
  hall trays. No. 72: lab plate reliefs. No. 71: residential street at night with a camera pod.
- Recently overused: city limit signs (no. 61), survey stakes (62, 69), hearing room interiors.

## What the last three decks' judges named (the weakest frames, and which repairs failed)

- No. 72: a cell slab read as a flat printed grid with no wall casting a shadow; hovering plates
  with no contact; a small rack in the lower middle band with flat grey tubes; dead left 40 percent.
- No. 73: a uniform dark grey field bleeding off both edges with an eight-pixel label; a straight-on
  plan that read as a keyboard or a chart; bare wireframe racks on a mid grey pool; a small tower
  in empty floor, near twin of another frame.
- No. 74: a flat plank with low-poly clods, no texture at close range; a pale primitive plant a
  fifth of the frame on the horizon; a flat ribbon outline with nothing of known size; dead wall
  and box chairs in a room; a frame reusing another frame's kit for different copy.
- Common thread: subjects too small, primitives with no surface detail, straight-on plans that
  read as charts, uniform grey fields. Pitch subjects CLOSE and LARGE, modelled best where largest.

## Craft refresh (today)

Break uniform roughness with faint low-contrast noise; a small bevel gives a highlight somewhere to
sit (`TXT.roundedBox`); edge wear only on convex edges and multiplied by noise; dark regions beside
bright reflections make a shiny object read solid; flat even light is what reads as CG.

## Instincts (instincts.py --top 5)

- Read every repair at 432px against the defect it was meant to cure.
- Write every acceptance item so that rendering NOTHING fails it.
- A claim's own paraphrase can assert more than its quote; every surface inherits the excess.
- Rebuild every derived artifact in the same commit as the change it derives from.
- Run house_style_check straight after admitting anything to the record.

## The rotation rule (it travels with the brief)

> The rotation rule changed on 2026-09-16. Read `knowledge/carousel/ILLUSTRATION_SYSTEM.md`,
> "THE DECK IS THE UNIT", and judge against that. If anything in your own definition disagrees
> with it, this paragraph wins. At most TWO of the same archetype in a row and at least THREE distinct,
> not five. ONE visual argument, ONE light, ONE grade for the whole deck, and no screen at all,
> because the print register is deleted. Judge
> whether the nine frames read as one deck and whether at least two continuity devices are
> doing real work, and treat a deck that turns the page nine different ways as a FAULT.

## Must read before pitching

`prompts/carousel_studio.md`; `knowledge/carousel/ILLUSTRATION_SYSTEM.md` (THE STAGE, THE WORLD,
THE ARTWORK CARRIES THE DATA, THE TEN LAYOUTS, What still fails); `knowledge/carousel/ARSENAL.md`
(ENGINE and KIT: vehicles include `sedan`, `suv`, `delivery_van`, `semi_truck` with `sensors`
pods/roof/full, `semi_cab_interior`; civic includes `road`, `traffic_signal`, `streetlight`,
`crosswalk`, `stop_sign`, `bus_stop`, `gas_station`; `person`); `knowledge/carousel/TECHNIQUE_LIBRARY.md`;
`examples/bold-proof/README.md`; `examples/art-direction-proof/README.md`;
`examples/figure-bearing/storyboard.md`. A robotaxi roof sensor the kit lacks is built once in the
chassis as a kit model, never as geometry in one frame. No maker's likeness, logo or livery: every
vehicle is drawn to illustrate.

Hard constraints: at least six of nine frames declare `data_in_art` from computed figures; at
least six use a physical renderer; five stand in a world (`TXT.sky`), a built room, or a measured
relief; start in `lastLight` or `floodlit`; one subject a third to two thirds of the frame; light
type on a dark field, never a pale wash; nine layouts that pass `TXLAYOUT.check`; at least two
continuity devices; a CRAFT PLAN with shots (AERIAL/WIDE/MEDIUM/CLOSE/MACRO, no shot on more than
three frames).
