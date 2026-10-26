Round 2 recheck, carousel no. 61, slides 3 and 4. Both slides get REVISE. Slide 4 has four unresolved round 1 must-fixes, including the curly apostrophe. Slide 3 has one, the object in a void. Coordinates are design space (1080x1350) unless marked "display" (the 1600x2000 view, design = display x 0.675). I read the thumbs first, then the full-size PNGs, then crops r1c2, r2c1, r2c2, r3c1 and r3c2 for slide 4 and r1c1, r2c1, r2c2, r3c1 and r3c2 for slide 3 at 100 percent. I did not run value_register.py, so I can't quote its line. I did not read storyboard.md or claims.json. Slide 3's checklist items are the ones from my round 1 notes, and I did not re-check the dossier wording or the claim ids against claims.json.

```json
{
 "reviews": [
  {
   "slide": "slide-03",
   "frame_looked_at": "432px thumb first, then the 2160x2700 render, then the 100 percent crops",
   "world": "lastLight as a near-black field only. There is still no ground, verge, seam or horizon. The sign's lit edge is on the left, which agrees with the deck's key.",
   "transcription": "THE CITY LIMIT | 03 / 09 | The city can't regulate the flight path | Round Rock says the FAA regulates airspace and flight paths. Its page says drones may fly over residential areas on approved routes. Inside city limits it may regulate where drone infrastructure sits. The aircraft is drawn to illustrate. | CITY LIMIT (sign legend, leading C cropped by the left edge) | c4 c6 c7 c8 | texasaidocket.com",
   "illegible": [],
   "copy_check": "Transcribed from the thumb and matched at full size. Matches copy.json. can't in the headline is a straight apostrophe in the serif at full size. No 3-versus-5 misread (03 / 09 reads correctly at thumb). No colons, semicolons, dashes or banned words.",
   "checklist": [
    {"item": "the sign's green face reads CITY LIMIT, names no town and carries no population figure", "pass": true, "note": "Reads at 432px. The C is clipped by the left edge, which is the planned crop."},
    {"item": "the sign's face owns at least a sixth of the frame area at 432px", "pass": true, "note": "Face runs display x 0 to 940, y 1110 to 1730, which is about 17 percent of the frame. That clears a sixth by a hair. Round 1 had it at 11 percent, so this is resolved but marginal."},
    {"item": "the aircraft's path is a long exposure trail of wingtip lights crossing above the sign from the left edge to the aircraft's lit nav lights", "pass": true, "note": "Now a straight run from the left edge (display y 1015) to the aircraft at display (1300, 945), clear above the sign's top edge. At 432px it is a visible green, white and red band that survives the downscale. The halo is small. At 100 percent the aircraft is a tiny silhouette in a small glow (crop r2c2)."},
    {"item": "the sign's posts run out of the bottom edge, the sign cropped by the left and bottom edges", "pass": true, "note": "The right post runs out of the bottom. The left post is a sliver at the left edge. The earlier hard black offset strips are essentially gone."},
    {"item": "the frame's median L* at 432px is 22 or lower", "pass": true, "note": "Near black except the sign."}
   ],
   "round1_status": {
    "sign_too_small_and_object_in_a_void": "Size is resolved. The void is NOT resolved: the sign still stands in flat black with no ground, no pool of light, no lamp-side falloff, no wear and no grime.",
    "trail_thin_bowed_glow_big": "Resolved. The trail is straight and thicker and the glow is small.",
    "hard_offset_post_shadows": "Resolved. No strips beside the posts are visible in crops r3c1 and r3c2.",
    "dead_region_lower_right": "Not resolved. See frame_causes c.",
    "grain_grid": "Faintly visible still, minor. See frame_causes d."
   },
   "verdict": "revise",
   "must_fix": [
    {"what": "THE SHOWSTOPPER TEST still fails on the world. The larger sign is now bold, but it is an object in a void. The face is lit flat with no falloff, the posts have no ground to land on, and the whole right half of the frame below the trail is empty black. There is no contact, no dirt, and nothing under the aircraft to say it is over a place.", "where": "whole frame. Sign face display x 0 to 940, y 1110 to 1730. Posts display y 1730 to 2000.", "fix": "Light the face and ground it. (1) Add a ground plane at the posts' feet with TXT.ground (dry grass and gravel verge) and TXT.contact where each post meets it. Put the lastLight seam low behind the sign at the horizon, at about design y 1000 to 1100 in the right half. (2) Lay a falloff across the face so the left third is about 2 stops brighter than the right edge, as the dossier already says. (3) Grime the lower 25 percent of the face and the post feet. Leave the grade untouched."}
   ],
   "frame_causes": [
    {"cause": "b", "problem": "The sign is still an unfinished largest object. The face is evenly lit, with vertical lighter and darker bands (crop r3c1, columns across the face), a fine diamond weave at 100 percent (crops r2c1 and r3c1) and no edge wear or dirt. The weave can read as a screen at 2x.", "fix": "Cut the sheeting texture contrast to about a third and smooth the banding on the face. Add the lamp-side falloff and bottom dirt described in must_fix."},
    {"cause": "c", "problem": "Dead region, right of the sign. Display x 950 to 1600, y 1100 to 2000, about 25 percent of the frame, is empty black with a faint navy gradient at the bottom. Everything else is on the left.", "fix": "Put the seam glow and a few distant lamps or a faint roofline at display y 1500 to 1650 in that quadrant, and let the gravel verge catch the sign's pool there."},
    {"cause": "d", "problem": "A faint regular grain grid is visible in the black field at 100 percent (crops r1c1 and r2c2). It is minor but will shimmer on a phone.", "fix": "Keep grain under 3 percent and re-seed per frame, or use blue noise, so no fixed 2x tile shows."}
   ],
   "would_improve": [
    "The aircraft ends over empty black at display (1300, 945). Distant lamps under it would make the 'over the city' line of c7 visible.",
    "The red and green nav colours are the only chroma beside the sign. Keep them small so they never read as the flag red."
   ]
  },
  {
   "slide": "slide-04",
   "frame_looked_at": "432px thumb first, then the 2160x2700 render, then the 100 percent crops",
   "world": "A staged night aerial: dark navy sky, a horizon glow, a lamp field and a lit ring on dark ground. True blacks, one bright edge, little grey middle. The light agrees with the deck's.",
   "transcription": "THE COMPANY'S REACH | 04 / 09 | Three miles in every direction | As the city relays the company, that reach covers about 28.3 square miles around a hub its zoning doesn't specifically address. The ring is computed from the three miles and drawn to illustrate. | THE HUB | 3 MILES | c1 c2 c3 | texasaidocket.com",
   "illegible": [],
   "copy_check": "28.3 reads as a 3, not a 5, in both the thumb and the full-size body face (crop r1c2 of slide 3's sibling confirmed 04 / 09 and the dek digits are round-topped). 3 MILES agrees with c3. No colons, semicolons, dashes or banned words. THE APOSTROPHE IN 'doesn't' IS STILL CURLY AT FULL SIZE: the glyph at design x 726 to 803, y about 437 (display 1075 to 1190, y 647) is a slanted, comma-shaped right single quote form, visible in crop slide-04-r1c2 bottom edge ('its zoning doesn’t'). Slide 3's headline can't is a straight tick. copy_sync_check reads the DOM and sees U+0027, so the pixels disagree with the DOM. The mark a reader receives is a smart quote, against the straight-quotes house rule. I can't see from pixels whether the cause is a transform or the body font's own U+0027 design.",
   "checklist": [
    {"item": "the ring is visible as one continuous closed ellipse and spans at least 80 percent of the frame width at 432px", "pass": false, "note": "The ring is still not closed in frame. Its left end touches the left edge at display (0, 1340) and the far and near arcs leave the frame at the right (design x 1080, about y 820 and y 1148, crop r2c2 and r3c2). At thumb it reads as an ellipse cut off at both sides, with the right side clearly cropped. The dossier asked for a closed ellipse with the ring closing in frame."},
    {"item": "the hub's lit pad sits inside the ring at its centre", "pass": true, "note": "The pad is at display (830, 1308), inside the ring, with a leader to THE HUB. It is a tiny dot at 100 percent (crop r2c2, bottom left) and is invisible at 432px. It is not brighter or larger in any way a reader receives."},
    {"item": "street lamps are visible inside the ring and thin toward the horizon", "pass": true, "note": "Dense near the camera, thinning to scattered points at the horizon. They are still hard points, not soft glows."},
    {"item": "the horizon and a band of sky are visible above the far arc", "pass": true, "note": "Navy sky from about display y 800 to 1100 with a horizon glow."},
    {"item": "the label 3 MILES lands on the ring within 24 px and THE HUB on the pad within 24 px", "pass": true, "note": "3 MILES now sits centered under the radius foot at display (605, 1490), about 27 design px below the near arc. It has a faint dark knockout (crop r3c1). THE HUB has a short leader to the pad. THE HUB's knockout is faint and lamp dots run next to and through its glyphs at 100 percent (crop r3c2), but it reads at thumb."},
    {"item": "the frame's median L* at 432px is 16 or lower", "pass": true, "note": "Dark frame."}
   ],
   "round1_status": {
    "curly_apostrophe": "NOT resolved. Still curly at full size.",
    "ring_not_closed": "NOT resolved. Still clipped at the right edge and touching the left at full frame.",
    "3_MILES_floats_167px_from_ring": "Resolved. It sits under the radius foot on a dark knockout.",
    "moire_and_dot_lattice": "NOT resolved. See frame_causes d.",
    "unexplained_amber_I35_dotted_line": "Resolved. It is gone from the frame.",
    "hub_pad_not_visible": "NOT resolved. The pad is still a 2 to 3 px dot at 100 percent and does not show at 432px.",
    "dark_crescent_inside_far_arc": "NOT resolved and larger. A black void now sits inside the far arc above the hub, display x 700 to 1250, y 1235 to 1300."
   },
   "verdict": "revise",
   "must_fix": [
    {"what": "A curly apostrophe still prints in the dek 'doesn’t'. The glyph a reader receives is not the straight U+0027 the DOM holds, which is a house-rule break that the DOM-reading check can't see.", "where": "dek line 2, design x 726 to 803, y about 437", "fix": "Find why the body-face U+0027 draws curly. Check for a smart-quote or text-transform step on slide 4's dek, and check whether the body font's quotesingle is designed that way. If the font draws it curly, set the apostrophe in a face whose U+0027 is straight, or rewrite the dek as 'does not specifically address'. Then re-render and read the glyph in the PNG at 100 percent."},
    {"what": "The ring is still not a closed ellipse in frame. It is clipped at the right edge and touches the left edge, so it reads as two arcs cut off by the frame, and the ring computed from the three miles is not whole.", "where": "left end display (0, 1340). Right arcs leave the frame at design (1080, about 820) and (1080, about 1148).", "fix": "Pull the camera back further, or widen fov from 50 to 58, until the ring's full width is 88 to 92 percent of the frame, about 950 design px, with about 60 px clear each side. Keep the eye at 1,200 m, or raise it to 1,600 m. Re-seat 3 MILES and THE HUB against the new ring."},
    {"what": "The hub pad, the named subject, is not visible at thumb. It is a tiny dot at display (830, 1308) and is not brighter than the streets around it. The dark crescent above it (display x 700 to 1250, y 1235 to 1300) makes the hub read as a hole in the town.", "where": "display (830, 1308) and the crescent above it", "fix": "Make the pad a clearly lit rectangle, a bright core about 24 by 14 design px with a soft halo about 40 px across, and raise its emissive to about 3x so it is the second-brightest mark after the near arc. Fill the crescent with the same lamp field, or give it a drawn boundary as the cleared site."},
    {"what": "Moire and a rigid dot lattice are still in the lamp field. Inside the ring the lamps are a grid of identical points in tight pairs, and the street streaks radiate as parallel stripes at the left of the ring that read as a hatch at 432px. This is the shimmer the library warns about, and a regular dot lattice reads as the deleted halftone.", "where": "inside the ring, design x 0 to 1080, y 800 to 1150, worst at the left, in crops r2c1, r3c1 and r3c2", "fix": "In the instanced lamp pass, jitter each lamp's position by plus or minus 35 percent of the pitch, vary radius and intensity per lamp (0.6x to 1.4x), and drop about 12 percent of lots as dark. Once projected pitch falls under 3 px at 2x, fade the point into an area glow. Don't blur the frame."}
   ],
   "frame_causes": [
    {"cause": "d", "problem": "Moire and aliasing in the lamp lattice, plus hard rectangular block-fringing where the lamp blocks meet the ring and the dark land. The blocks are visible as stair-stepped dark rectangles along the near arc at design x 0 to 300, y 900 to 960 (crop r3c1) and along the far arc (crop r2c2, display y 750).", "fix": "Same instanced-lamp change as the fourth must-fix. Also set a point-size floor of 1.5 px at 2x and anti-alias the block edges so no rectangular blocks show against the dark land."},
    {"cause": "b", "problem": "The largest object, the lit ring and its town, is still unfinished in one place: the hub pad, the named subject, doesn't register at 432px (see the third must-fix).", "fix": "Make the pad a bright core with a soft halo as in the third must-fix."},
    {"cause": "c", "problem": "A black void inside the far arc, display x 700 to 1250, y 1235 to 1300, with no lamps. It reads as a hole in the town, and it is bigger than in round 1. It is not a dead third of the frame.", "fix": "Fill it with the lamp field, or draw its edge as the hub's cleared site."}
   ],
   "would_improve": [
    "Make the lit radius line 2 px thicker at 1080 so it survives the 432px downscale. It is a hairline at thumb.",
    "Back THE HUB with the same dark plate as 3 MILES so lamp dots stop running into its letters.",
    "Add a brighter first row of lamps just inside the near arc so the ring reads as the edge of something."
   ]
  }
 ],
 "checklist_audit": "Slide 3's list can still be satisfied by an object in a void. No item asks for a pool of light, a ground or a lamp-side falloff, so the frame passes four of five items while its world stays empty. It needs a pool-of-light item and a minimum trail width at the thumb. Slide 4's list is stronger. The closed-ellipse item is the one the frame still fails, and the label item passed this round only because the label moved. The pad item would pass on any dot inside the ring, so it should require a visible pad at 432px."
}
```

Files reviewed (absolute paths):
- /home/user/TexasAIDocket/out/2026-10-26/render/slide-03.png
- /home/user/TexasAIDocket/out/2026-10-26/render/slide-04.png
- /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-03-thumb.png
- /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-04-thumb.png
- /home/user/TexasAIDocket/out/2026-10-26/render/crops/ (slide-03 r1c1, r2c1, r2c2, r3c1, r3c2 and slide-04 r1c2, r2c1, r2c2, r3c1, r3c2)
- /home/user/TexasAIDocket/out/2026-10-26/tmp/brief_all.txt
- /home/user/TexasAIDocket/out/2026-10-26/copy.json
- /home/user/TexasAIDocket/out/2026-10-26/reviews/pixel-r1-s03-04.md