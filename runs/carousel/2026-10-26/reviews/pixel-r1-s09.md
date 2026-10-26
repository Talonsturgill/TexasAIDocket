{
  "slide": "slide-09",
  "frame_looked_at": "Full render (2160x2700, coordinates below are in the 1600x2000 display space, multiply by 1.35 for native), the 432px thumb, and all six native crops r1c1 to r3c2.",
  "transcription": "THUMB: RENAISSANCE SQUARE, PROPOSED | 09 / 09 | Next, the hub comes before the rule | Round Rock is working with Zipline toward a hub behind Renaissance Square on northbound Interstate 35. The city says that site will help it develop regulations for future facilities inside city limits. Drawn to illustrate. | c9 c10 c11 | texasaidocket.com. The full size matches the thumb word for word. The digits read 09 / 09 and 35 correctly, with no 3 and 5 confusion. No house-rule violations in the copy: no colons, semicolons or dashes, no gap/matters/pattern, 'can't' not needed.",
  "illegible": [],
  "checklist": [
    {"item": "four stakes with flagging and a string line enclose an empty rectangle and the rectangle spans at least half the frame width", "pass": true, "note": "Four stakes, closed string quad running from x~85 to x~1510 of 1600. The string is a 2px hairline, so at 432px the rectangle is carried by four small sticks and a faint line. The flag on the far stake (x 900, y 1350) is almost invisible."},
    {"item": "each stake casts a long shadow across the asphalt", "pass": false, "note": "Each stake has only a small dark contact blob at its foot (about 60px wide, e.g. 80,1605, 672,1840, 1510,1560). The long shadows in the frame are wide, meandering, branching ribbons (x 400-1600, y 1380-1900). A thin vertical stake can't throw a ribbon that wavers and forks. They read as a river network, tree roots or cracks, not stake shadows. The picture contradicts its own light and caster."},
    {"item": "nothing stands beyond the pad but the dark", "pass": true, "note": "Only dark and a navy gradient beyond the pad. But the ribbon shadows imply an unseen branching caster (a tree) out of frame, which contradicts 'empty'."},
    {"item": "no aircraft, tower or pod is in frame", "pass": true, "note": "None."},
    {"item": "the frame's median L* at 432px is 22 or lower", "pass": true, "note": "Visibly very dark overall (near-black sky, brown pool). Passes by eye. No value_register line was supplied to quote."}
  ],
  "world_and_showstopper": {
    "world": "lastLight staged world, one warm pool on dark asphalt, near-black navy sky. The key reads from the left on the stakes (lit left edges), and the cast direction is toward the right and away, which is consistent with the deck's key. The ribbon shadows agree with the key direction but have no visible caster.",
    "showstopper_test": "FAIL. With the type covered, the picture is a dark navy field with a small lit patch along the bottom 27 percent of the frame (y 1340 to 2000). The subject does not fill a third of the frame. Four sticks about 100 to 200px tall and a hairline string are the whole of it. The pool is a muddy brown mid-tone and not a bright pool with one hot edge. The rest is empty dark.",
    "one_word_at_432px": "Survey stakes (just). At feed size the four stakes are small slivers, and the big dark ribbons dominate the lit area and read as a river map.",
    "silhouette_and_scale": "The four stakes do not read as one silhouette. The only object a reader can measure the stakes against is the asphalt seams, which are faint. The 12 by 9 m rectangle has no visible reference such as a kerb, a painted bay line or a lamp pole.",
    "rendered_not_placed": "Stakes have a lit left face, a pale cut top and a contact blob, so they are modelled. The ground reads as brown dirt or concrete slabs, not worn asphalt. Speckle is the only texture and the seam lines are faint. No screen, halftone or hatch is visible. No print look."
  },
  "verdict": "revise",
  "must_fix": [
    {
      "what": "The dominant long shadows are not cast by the stakes. They are wide meandering ribbons with branching forks that read as rivers or roots, and they are the loudest dark shapes on the lit asphalt. This fails the 'each stake casts a long shadow' item and misleads the reader about what the picture shows.",
      "where": "Full size x 400 to 1600, y 1380 to 1900. Strongest at x 1000 to 1350, y 1500 to 1900, and the long ribbon crossing the string at x 1100 to 1600, y 1700.",
      "fix": "Remove whatever off-frame caster produces these ribbons (any scatter, branch or oak occluder in the stage config). Then give each stake a thin straight cast, roughly 5 to 8 stake-heights long, raked right and away along the key azimuth (-55 deg, elevation 8). That makes four parallel long thin shadows that cross the string and the pad. If a visible caster is wanted, put a lamp pole or a hard edge in frame and make the shadows straight."
    },
    {
      "what": "The subject is too small and sits in the bottom 27 percent. A navy dead zone fills the frame between the dek and the pad. The frame fails the BOLD test: one subject filling a third to two thirds of the frame, in a pool of light with true blacks and one bright edge.",
      "where": "Dead zone: y ~830 to 1330, full width (about a quarter of the frame, a flat navy gradient). Subject confined to y 1340 to 1880.",
      "fix": "Lower the camera to eye ~1.2 m and bring it in to ~9 to 10 m off the pad, so the rectangle's far edge sits at y ~1050 to 1100 and the near stake runs off to y ~1900. Stakes then stand ~250 to 300px tall at full size, and the pad fills the lower 45 to 50 percent. Raise the horizon with it so the navy band shrinks. Brighten the pool's centre so there is one hot lit edge, and let it fall off to true black at the frame edges. Keep the sky dark."
    },
    {
      "what": "The string is a 2px hairline and the pink flags are thin. At 432px the enclosed rectangle is barely there, and the far stake's flag (x 900, y 1350) all but disappears.",
      "where": "String: the full quad, e.g. 85,1540 to 672,1745 to 1510,1500 to 900,1405. Far flag: 900-915, 1345-1385.",
      "fix": "Thicken the string to ~4 to 5px at full size (about 2px at 432px) and give it a faint cast line on the asphalt. Make the flags ~2x wider and lengthen the far one. Pink flagging against dark asphalt is the only saturated colour in the frame while the dossier says accent none. Keep it small, but desaturate it slightly toward a survey-tape salmon so it reads as flagging and not as the deck's urgency red."
    },
    {
      "what": "The ground does not read as worn asphalt. It reads as brown dirt or poured concrete slabs, with a brownish mid-tone, faint seams and a flat dull pool. The planned 'lit asphalt texture' is missing.",
      "where": "Full lit area, x 0 to 1600, y 1400 to 1900.",
      "fix": "Switch the ground to the asphalt material: darker (L* ~12 to 18 outside the pool), cooler grey-black with a visible aggregate sheen near the lamp's specular, plus 2 or 3 sharp crack lines and one painted line or oil stain inside the rectangle for scale. Keep the sodium tint to the pool only."
    },
    {
      "what": "The footer's website URL is crossed by a shadow ribbon, and the claim ids sit over the shadow field. Legible, but a cast edge touches letterforms.",
      "where": "texasaidocket.com, x 1080 to 1480, y 1840 to 1870. A ribbon passes under 'do' near x ~1250.",
      "fix": "Falls away once the ribbon shadows are removed. Otherwise darken a footer-height gradient over y 1820 to 2000 so type sits on true black."
    }
  ],
  "frame_causes": [
    {"cause": "b", "problem": "The largest object, the stakes and string, is under-built. The stakes are about 100 to 200px tall on a 2000px frame, the string is a hairline, and the flags are slivers. The subject reads as a few sticks in the dark and carries no material weight at 432px.", "fix": "Bring the camera in and lower it so the stakes are ~250 to 300px tall, thicken the string to ~4 to 5px, and enlarge the flags."},
    {"cause": "c", "problem": "Dead region. About a quarter of the frame (y 830 to 1330, full width) is a flat navy gradient carrying nothing, between the dek and the pad.", "fix": "Raise the pad's far edge to y ~1050 and shrink the sky band. Let the lit pool's falloff, asphalt texture and a visible far edge fill the zone with something."},
    {"cause": "d", "problem": "Render artifact. The long branching ribbon shadows have no visible caster and read as a river or root network. The stakes' own shadows are only contact blobs.", "fix": "Delete the stray occluder or scatter casting those ribbons, and cast straight thin shadows from each stake along the key azimuth."}
  ],
  "plan_check": "The checklist is weak and would let this frame pass mostly as it stands. 'Nothing stands beyond the pad but the dark' and 'no aircraft, tower or pod' would pass on a near-empty frame. No item sets a minimum size for the stakes at 432px or for the area the pad fills. No item says what the shadows must look like. The plan's own 'risk' line says the stakes should be 'close, lit and casting, and the rectangle large', and the frame is not that. Add: stakes at least 120px tall at 432px, the pad filling at least 40 percent of the frame height, and shadows that are straight and parallel.",
  "would_improve": [
    "Put a distant sodium lamp glow or a faint line of I-35 lights at the horizon to give the 'proposed hub beside the interstate' a place, without drawing a strip centre. The brief says no strip centre was drawn, but one lamp on the horizon would give the frame a second depth cue.",
    "Footer lists c9 c10 c11, but c11 (the city may regulate hub location so they are not next to homes) is not used in the dek. Either cite only c9 and c10 or add the c11 content. It is not a numeral or fact error.",
    "Hook 'Next, the hub comes before the rule' is an editorial inference from c10 ('helping the City develop regulations'). It is defensible, but the 'Next,' lead-in reads awkwardly after the Rowlett contrast. Consider 'The Round Rock hub comes before the rule'."
  ],
  "paths": [
    "/home/user/TexasAIDocket/out/2026-10-26/render/slide-09.png",
    "/home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-09-thumb.png",
    "/home/user/TexasAIDocket/out/2026-10-26/storyboard.md"
  ]
}