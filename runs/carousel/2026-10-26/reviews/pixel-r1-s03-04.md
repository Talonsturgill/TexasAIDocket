Both slides get REVISE. Coordinates are design space (1080x1350) unless marked "display" (the 1600x2000 view, design = display x 0.675). I did not run value_register.py, so I can't quote its line. I judged the tone from pixels.

```json
{
 "reviews": [
 {
  "slide": "slide-03",
  "frame_looked_at": "432px thumb first, then the 2160x2700 render, then all six native crops at 100 percent",
  "world": "LASTLIGHT, but only as a near-black field. There is no seam, no ground and no verge. The posts' lit edge is on the left, which agrees with the deck's key at azimuth -55.",
  "transcription": "THE CITY LIMIT | 03 / 09 | The city can't regulate the flight path | Round Rock says the FAA regulates airspace and flight paths. Its page says drones may fly over residential areas on approved routes. Inside city limits it may regulate where drone infrastructure sits. The aircraft is drawn to illustrate. | CITY LIMIT (on the sign) | c4 c6 c7 c8 | texasaidocket.com",
  "illegible": [],
  "copy_check": "Matches copy.json. The straight apostrophe in can't is correct. No colons, semicolons or dashes. None of gap, matters or pattern. c4, c6, c7 and c8 trace to claims.json. No numeral other than 03 / 09. No 3-versus-5 misread at feed size.",
  "checklist": [
   {"item": "the sign's green face reads CITY LIMIT, names no town and carries no population figure", "pass": true, "note": "Legend reads CITY LIMIT at 432px. No town name, no figure."},
   {"item": "the sign's face owns at least a sixth of the frame area at 432px", "pass": false, "note": "The face runs about x 0 to 533, y 797 to 1121, roughly 11 percent of the frame. A sixth is 16.7 percent. With posts it is still short of what the dossier planned."},
   {"item": "the aircraft's path is visible as a long exposure trail of its wingtip lights crossing above the sign from the left edge, ending at the aircraft's lit nav lights to the right", "pass": true, "note": "Present, but marginal at 432px. See the trail verdict below. It passes the item as written and fails the intent of reading at feed size."},
   {"item": "the sign's posts run out of the bottom edge, the sign cropped by the left and bottom edges", "pass": true, "note": "The sign is cropped at the left and the posts run out of the bottom. The sign face itself ends at y 1121, so only the posts do the bottom crop."},
   {"item": "the frame's median L* at 432px is 22 or lower", "pass": true, "note": "Nearly all near black. The only mid tone is the sign."}
  ],
  "trail_verdict": "It reads as a flight path, and mostly because the headline says 'flight path'. At 432px the three lines (green, white, red) merge into one hairline about 1px wide and dim. What carries the read is the soft glow dot at the right end. At 100 percent the tiny aircraft silhouette is there, and the red, white and green hairlines match wingtip and tail lights. Three things work against it. (1) The trail bows up in an arc (it rises about 35 design px, then falls) while the aircraft is meant to hold a constant 91.4 m. A level path seen from a camera looking up is a straight line in a fov-40 perspective, so the arc reads as a comet or projectile. (2) The aircraft ends at x 878, well past the sign's right edge at x 534, and above empty black. Nothing under it says it is over the city, so 'the whole of c7 in one picture' is not delivered. (3) The glow halo is larger than the aircraft and looks like bokeh.",
  "verdict": "revise",
  "must_fix": [
   {"what": "THE SHOWSTOPPER TEST fails. The sign is an object in a void, flat black behind it with no ground, verge, seam or distant glow. The face is lit evenly. The dossier's 'falling off from the lamp side' is not visible, and there is no pool of light, no wear and no grime. The sign is about 11 percent of the frame where the test wants a third or more. This is the owner's 'object in a void' rejection.", "where": "whole frame. Sign face x 0 to 533, y 797 to 1121. Posts x 24 to 71 and x 395 to 429, y 1121 to 1350.", "fix": "Pull the camera in on the sign. Keep the 0.9 m eye and fov 40. Move the camera from 4.6 m to about 3.2 m off the sign so the face is 17 to 22 percent of the frame, and move the sign's right edge to about x 640. Stage the world behind it with TXT.stage(R, sign): a worn verge of dry grass and gravel at the posts' feet with TXT.contact where the U channel meets it, and the lastLight seam low behind the sign in the south west. Then lay a falloff across the face with a pool on the lamp side, so the left third is about 2 stops brighter than the right edge. Keep the grade untouched."},
   {"what": "The sign face is under the planned size (acceptance item failed).", "where": "x 0 to 533, y 797 to 1121", "fix": "Same camera move as above. Target face area at or above 16.7 percent of the frame. That is about 243,000 square design px, for example 640 wide by 380 tall visible."},
   {"what": "The trail is too thin at 432px and bows when it should run straight. The glow is bigger than the object.", "where": "trail from (0, 682) through its peak at y 648 to the aircraft at (878, 687). Glow dot about 40 design px across.", "fix": "Draw the trail 3 to 4 px wide at 1080 with a white-hot core and the red and green as 1.5 px offsets, so it survives the 0.4 downscale. Make the path a straight run with the camera's perspective slope, entering the left edge at y about 700 and ending at the aircraft at about (878, 640), with no mid-span bow. Cut the halo radius in half. Run the trail so it passes above the sign's top edge (y 797) and ends beyond it, so the aircraft is over the limit and past it."},
   {"what": "The posts carry hard black strips beside them that fall on nothing (no ground, no wall). They read as a hard-edged shadow with no contact.", "where": "left post about x 70 to 90, right post about x 429 to 445, y 1121 to 1350", "fix": "Delete the hard offset shadow, or give the posts a ground to cast on (the verge above) with a soft contact-hardened shadow under TXT.contact. A shadow on a surface that isn't there is the cheapening the library warns about."}
  ],
  "frame_causes": [
   {"cause": "b", "problem": "The largest object, the sign, is an unfinished render. It is face-on, evenly lit, with no sheeting falloff, no edge wear, no dirt, and posts that float with no ground. The bolts have faint green smudges beside them. The face shows a fine diamond weave at 100 percent, in crop r2c1 (x 0 to 540, y 450 to 900), which can read as a screen over the surface.", "fix": "Add the lamp-side falloff and a grimed lower third (road dirt and dust on the lower 25 percent of the face and the posts' feet). Cut the sheeting texture contrast to about a third so no visible weave survives at 2x. Stage the verge under the posts."},
   {"cause": "c", "problem": "Dead region, lower right: roughly design x 540 to 1080, y 709 to 1350, about 25 percent of the frame. It is empty black with a faint navy gradient at the bottom, while everything else sits at the left.", "fix": "Put the lastLight seam and a few distant lamps or a faint roofline of the town in that quadrant at its horizon height (design y about 1000 to 1100). Light the verge's gravel there with the sign's pool. That also makes the aircraft 'over' something."},
   {"cause": "d", "problem": "A regular dither or grain grid is visible in the near-black sky at 100 percent, in crops r1c1, r1c2 and r3c2 (x 0 to 1080, y 0 to 450 and y 900 to 1350). It will shimmer on a phone.", "fix": "Drop grain amplitude under 3 percent and re-seed the noise per frame with no fixed tile, or blue-noise it, so the 2x tile doesn't repeat."}
  ],
  "would_improve": [
   "The headline states the legal conclusion in the site's voice. The dek attributes it with 'Round Rock says', which saves it. Putting 'Round Rock says' in the hook ('Round Rock says it can't regulate the flight path') would match slides 1 and 4.",
   "The red and green wingtip colours are the only chroma on the frame besides the sign. They are nav lights and not the flag red. Keep them small, since the flag red is reserved for open deadlines.",
   "The claim-id line c4 c6 c7 c8 sits about 30 design px from the left post (x 162 against the post at x 130). It doesn't cross it. Don't move the post nearer."
  ]
 },
 {
  "slide": "slide-04",
  "frame_looked_at": "432px thumb first, then the 2160x2700 render, then all six native crops at 100 percent",
  "world": "A staged night aerial: dark navy sky, a horizon glow, lamps and a lit ring on dark clay. The light is the lamps and the ring, and it agrees with the dusk world. It is the strongest frame of the two, with true blacks, one bright edge and little grey middle.",
  "transcription": "THE COMPANY'S REACH | 04 / 09 | Three miles in every direction | As the city relays the company, that reach covers about 28.3 square miles around a hub its zoning doesn't specifically address. The ring is computed from the three miles and drawn to illustrate. | THE HUB | 3 MILES | c1 c2 c3 | texasaidocket.com",
  "illegible": [],
  "copy_check": "28.3 = pi x 3 squared = 28.27, rounded to one decimal. compute.py produces it as reach_sq_mi, so it is computed rather than typed. 3 MILES agrees with c3. At feed size the 3 in 28.3 reads as a 3, not a 5. No colons, semicolons or dashes. None of gap, matters or pattern. The apostrophe in doesn't prints curly in the render, and the straight-quotes house rule is broken. copy.json records it as straight, so the record and the pixels disagree (see must_fix).",
  "checklist": [
   {"item": "the ring is visible as one continuous closed ellipse and spans at least 80 percent of the frame width at 432px", "pass": false, "note": "It spans 100 percent and more. The far arc leaves the frame at the left at about (0, 837) and the right at (1080, 820), and the near arc leaves at (0, 1124) and (1080, 1148). It is never closed in frame, so it reads as two arcs. The dossier asked for one closed ellipse."},
   {"item": "the hub's lit pad sits inside the ring at its centre", "pass": true, "note": "The pad glow is at about (560, 883), inside the ring and near its perspective centre. It is weak at 432px, a tiny dull oval much dimmer than the streets, so the named subject doesn't pop."},
   {"item": "street lamps are visible inside the ring and thin toward the horizon", "pass": true, "note": "They are dense near the camera and thin to scattered points at the horizon."},
   {"item": "the horizon and a band of sky are visible above the far arc", "pass": true, "note": "A navy sky band runs about y 540 to 740, with the horizon glow at about y 740."},
   {"item": "the label 3 MILES lands on the ring within 24 px and THE HUB on the pad within 24 px", "pass": false, "note": "3 MILES sits at (255 to 373, 980). The nearest ring point is on the near arc about 167 design px below it, and the radius line passes about 60 px to its right. THE HUB at (601 to 719, 839) is about 57 px from the pad, tied by a short leader, which is acceptable. The 3 MILES failure stands."},
   {"item": "the frame's median L* at 432px is 16 or lower", "pass": true, "note": "Mostly near black with lamp points. It is a dark frame."}
  ],
  "verdict": "revise",
  "must_fix": [
   {"what": "A curly apostrophe prints in the dek ('doesn’t'). The house rule is straight quotes only, and copy.json says straight. Slide 3's can't and the kicker's COMPANY'S are straight, so this is a renderer or typography transform on this frame only.", "where": "dek line 2 at about (726 to 803, 437)", "fix": "Remove whatever smart-quote step is touching this dek, then re-render. Confirm the glyph is U+0027 in the DOM text node and in the PNG."},
   {"what": "The ring isn't a closed ellipse. It is clipped by both side edges, so a reader sees two arcs and the 'ring computed from three miles' is not whole.", "where": "far arc exits (0, 837) and (1080, 820), near arc exits (0, 1124) and (1080, 1148)", "fix": "Pull the camera back, or widen fov 50 to 58. Keep the eye at 1,200 m, or raise it to 1,600 m. This must keep the ring's full width at 88 to 92 percent of the frame, about 950 design px, with 60 px clear on each side. Re-run the labels against the new ring."},
   {"what": "3 MILES floats over the lamp field, 167 px from the ring. It is unattached to the thing it names. It also sits on dense lamp dots and bright street streaks.", "where": "(255 to 373, 980)", "fix": "Move 3 MILES to the midpoint of the radius line, offset 14 px perpendicular and rotated to the line's angle, or put a leader from it onto the ring's near arc at the radius foot (236, 1141). Back the label with a soft dark plate at about 55 percent so the dots don't run through the glyphs."},
   {"what": "Moire and a regular dot lattice in the lamp field. In crop r3c2 (x 540 to 1080, y 900 to 1350) the dots form scalloped arcs from aliasing. In r3c1 the block interiors are a rigid grid of identical points. At thumb this is the shimmer the library warns about, and a regular dot lattice also reads as the deleted halftone.", "where": "lamp field display x 0 to 1600, y 1150 to 1700, worst at design x 540 to 1080, y 900 to 1150", "fix": "Jitter each lamp's position by plus or minus 35 percent of the pitch, vary radius and intensity per lamp (0.6x to 1.4x), and drop about 12 percent of lots as dark. Fade point size into an area glow once projected pitch is under 3 px at 2x. Do this in the instanced lamp pass, not by blurring the frame."},
   {"what": "An unexplained amber dotted line crosses the whole frame, through the hub. It isn't in the dossier and has no label, and it competes with the radius line. A reader will ask what it is.", "where": "(0, 813) to (1080, 996)", "fix": "If it is a road (the I-35 corridor), label it, or remove it. The dossier's accent is none, and the amber doesn't help the ring. If kept, dim it to a third of its brightness so the radius line is the only linear mark through the hub."}
  ],
  "frame_causes": [
   {"cause": "d", "problem": "Moire and aliasing in the lamp lattice (see must_fix 4), plus visible block-fringing in the lamp streets at 100 percent in crop r2c1.", "fix": "Jitter, distance-fade and per-lamp variation as above, with MSAA or a lamp-point size floor of 1.5 px at 2x."},
   {"what_note": "none for b", "cause": "b", "problem": "The hub's pad is the dossier's named subject and the focal point, and it is the least visible part of the frame. It is a small dim oval with a 2 px dot, much dimmer than the streets, and it doesn't pop at 432px.", "fix": "Raise the pad's emissive to about 3x so it is the second-brightest mark after the near arc, widen its glow to about 40 design px, and put a clearly lit rectangle for the pad (a bright core about 24 by 14 px with a soft halo). Keep its hue to the lamps' own so it adds no accent."},
   {"cause": "c", "problem": "A dark crescent just inside the far arc (design x about 600 to 830, y 810 to 870, around the THE HUB label) has no lamps. It reads as a hole in the town and as an unlit plug around the hub. The label sits in this void. It is not a dead third of the frame.", "fix": "Either state it as the hub's cleared site with a clear boundary, or fill the crescent with the same lamp lattice so the ring encloses a continuous town."}
  ],
  "would_improve": [
   "Make the lit radius line 2 px thicker at 1080 so it survives the 432px downscale. At thumb it is a hairline.",
   "Add a slightly brighter first row of lamps just inside the near arc, so the ring reads as the edge of something and not only a drawn stroke.",
   "Check that slide 3 to slide 4 doesn't run two night skies of the same navy ramp back to back. Slide 4's seam can go warmer by a few degrees to stay in the lastLight world."
  ]
 }
 ],
 "checklist_audit": "Slide 3's checklist is partly trivial. Items 1 and 4 pass on any frame with a sign cropped at the left, and item 5 passes on any near-black frame. Nothing in the list asks the sign to stand in a lit world, to take a falloff, or to meet a ground, and none asks the aircraft's trail to survive 432px. The frame could execute the whole list and still be an object in a void, which it is. The list needs a pool-of-light item and a minimum trail width at the thumb. Slide 4's list is stronger, but its closed-ellipse item and its 24 px label item are the ones the frame failed, so they did their job."
}
```

Files reviewed (absolute paths):
- /home/user/TexasAIDocket/out/2026-10-26/render/slide-03.png
- /home/user/TexasAIDocket/out/2026-10-26/render/slide-04.png
- /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-03-thumb.png
- /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-04-thumb.png
- /home/user/TexasAIDocket/out/2026-10-26/render/crops/ (all twelve slide-03 and slide-04 tiles)
- /home/user/TexasAIDocket/out/2026-10-26/storyboard.md
- /home/user/TexasAIDocket/out/2026-10-26/copy.json
- /home/user/TexasAIDocket/out/2026-10-26/claims.json
- /home/user/TexasAIDocket/out/2026-10-26/compute.py