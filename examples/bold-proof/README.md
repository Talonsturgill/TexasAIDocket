# Bold proof, 2026-10-04

The owner, on carousel no. 42 beside the sibling's no. 78 of the same morning: *"the Alaska one,
when I look at it, it just kind of like wows me. It amazes me. It's more like bold. The Texas one,
it's okay, but it's just more like faded colors and stuff."*

This folder is the engine half of the answer, measured. Three shipped decks, nos. 40, 41 and 42,
re-rendered through main's engine (before) and through the staged engine (after), from the same
archived slides, beside the sibling's deck as the standard. `ILLUSTRATION_SYSTEM.md`, THE STAGE,
is the doctrine and `scripts/carousel/value_register.py` the gate.

## The sheets

- `deck-40.webp`, `deck-41.webp`, `deck-42.webp`, before on top and after below.
- `beside-the-sibling.webp`, the sibling's no. 78 as shipped over no. 42 staged.

## What changed between the rows

- **Nos. 40 and 41**: the chassis's `sky` became `"lastLight"` and nothing else. Every frame,
  camera, model, light direction and grade is the deck's own. The engine stages each snapshot by
  itself (`TXT.stage`, on the largest thing near where the camera is aimed).
- **No. 42**, which was built for noon with dark type, needed what a run under the new doctrine
  writes into its own chassis: `"lastLight"`, the key moved from az 10 el 58 to az -70 el 12 (a
  room's back wall was lit face on), the light type the chassis already had for dark frames, its
  pale washes turned dark, the exposure cut that held the light deck cap removed, and its rooms'
  limestone at 0.38 of its tone with the studio fill at 0.12. The frames' own code is unchanged.

## Measured, with value_register's own measure (432 by 540, CIE L*)

| deck | mid tone share, L* 30 to 70 | near black, L* under 15 | deck median L* |
|---|---|---|---|
| no. 40, 2026-10-02 | 0.407 to 0.205 | 0.138 to 0.373 | 32.2 to 20.1 |
| no. 41, 2026-10-03 | 0.477 to 0.134 | 0.191 to 0.631 | 29.7 to 6.1 |
| no. 42, 2026-10-04 | 0.698 to 0.173 | 0.090 to 0.539 | 58.4 to 4.2 |
| the sibling's no. 78, as shipped | 0.139 | 0.509 | 11.2 |
| the sibling's no. 77, as shipped | 0.129 | 0.593 | 10.6 |

The gate holds a deck to 0.35 on the mean and a probe frame to 0.50. Over the ten Texas decks from
September 24th the mean was 0.418, and over the sibling's twelve 0.131.

## Blind grades

Three graders who were not told which side was which, each shown the sibling's two latest decks
as the reference and all 27 frames as A/B pairs with the sides drawn at random, scored each frame
1 to 10 and named the bolder, the better and the closer to the reference. Counted over 81 verdicts:

| decks | verdicts | after bolder | better, after to before | after closer to the sibling | mean score, before to after |
|---|---|---|---|---|---|
| no. 40 | 27 | 15 | 14 to 5 (8 the same) | 15 | 6.45 to 6.70 |
| no. 41 | 27 | 27 | 24 to 3 (0 the same) | 27 | 6.16 to 6.91 |
| no. 42 | 27 | 27 | 26 to 1 (0 the same) | 27 | 6.04 to 6.88 |
| all three decks | 81 | 69 | 64 to 9 (8 the same) | 69 | 6.21 to 6.83 |

Frames scored lower after, on the mean of the three graders:

- no. 40 frame 2, 6.70 to 6.63. "Effectively identical; A's light on the left wall is a touch warmer, and both are warm mid-brown rooms rather than a dark stage." "Indistinguishable warm office with sun on the wall; the scale board reads in both and the vial is very small for a hero." "The two are nearly identical. A carries slightly warmer amber light on the left wall and B is a touch greyer."
- no. 40 frame 9, 6.67 to 6.50. "Nearly identical; A has a faint blue-violet wash across the left of the desk and binders that B does not, so B is marginally cleaner." "Nearly identical; A carries a cool blue light spill washing over the left stack of papers that B does not, and both remain warm mid tone rooms." "The two are nearly identical. A has a stray blue-violet light spill on the desk under the binders that B does not, so B reads slightly cleaner."
- no. 41 frame 4, 6.23 to 5.50. "B is darker but carries a clear render artifact, a jagged triangular lit patch on the road surface, and the road beyond dissolves into black; A is a coherent if muddy, faded dusk highway." "B is darker but its road light lands as a jagged brown wedge that reads as a render artifact, the guardrail glows an odd blue and most of the day posts are lost, killing the one-post-per-day idea; A is muddy haze but keeps the road and posts legible." "B is darker, but a jagged lighter wedge in the road reads as a render artifact, and the trees and lane detail are lost in a muddy purple distance. A is hazy but coherent."

## How the engine got here, three rounds of fresh graders

- **Round 1**, the first cut of the stage: after better 61 to 9, mean score 6.39 to 6.94. No. 41 frame 4, a road seen from a truck's
  cab, went 6.77 to 4.87: the stage took the cab the camera sits in for the subject and fogged the
  road from a few metres out, and warm glow over the cool fog printed plum bands. Fixed: a thing
  the camera stands in is never the subject, a frame with nothing large on screen is staged where
  the camera is aimed, the fog never starts nearer than 0.6 of that distance, and the seam's glow
  is softer.
- **Round 2**: after better 60 to 12, mean score 6.26 to 6.80. The graders named dead black thirds, faceless figures and the truck's
  own shadow cut across the road as a jagged wedge (6.30 to 5.07). Changed: the staged worlds' fill and
  ambient now hold every shadow at a deep navy, about 3 percent of the key, as the sibling's
  hemisphere fill does. That lifted the dead blacks. It did not remove the wedge, which is below.
- **Round 3**, the frames in the sheets above and the table above.

## What still fails, as the round 3 graders named it

- **No. 41 frame 4**, still the one frame clearly worse. The camera sits in a truck's cab with the
  key low behind it, so the truck throws its own long shadow up the road, and with no sky light to
  fill it the lit road between reads as a jagged wedge. A frame composed under THE STAGE puts the
  key to the side of a camera on a vehicle, or stages a subject on the road.
- **No. 42 frame 5**, judged better and still costly. The magenta bays that mark the pilot buses
  dim outside the pool. THE STAGE's rule 6 says stage a count as one subject, the whole row.
- **No. 40's rooms** stay warm mid brown, because that chassis lights its rooms itself (a 70 unit
  sun spot and `light: 1.0`), which the engine leaves alone. Two graders saw a faint blue violet
  spill on one desk. `value_register` measures a room like any frame.
- **Black voids.** The clock frame's sky and a lot's lower third read as empty black to some
  graders. The sibling keeps a fog gradient in its skies, and so does `lastLight` at the horizon,
  but a frame looking up has none of it.

## What this does not prove

The decks were composed for daylight places, so they show what the light does to the same
frames, not what a deck composed under THE STAGE looks like: one subject close and large in every
frame. That is the routine's half, and the first deck after the merge is its proof. No. 42's after
row includes chassis edits a run would make, listed above, and is not the engine alone.
