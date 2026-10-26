Both slides: REVISE. Coordinates are design space (1080x1350). The renders were read at 1600x2000 display, so multiply those by 0.675. I read all 12 native tiles. The airframe body straddles the r2/r3 seam at y 900, so I judged it from the full-size frame plus both tiles' edges. No value_register line was supplied. L* statements are by eye, not measured.

```json
[
{
 "slide": "slide-05",
 "transcription": "WHAT THE COMPANY SAYS | 05 / 09 | Zipline says the aircraft decides | The company says each aircraft reserves its own route before launch, avoids other aircraft with an onboard system and responds to problems on its own. Every claim here is Zipline's. The aircraft and tower are drawn to illustrate. | ROUTE RESERVED BEFORE LAUNCH | ONBOARD DETECT AND AVOID | PARACHUTE | c18 c19 c20 c23 | texasaidocket.com",
 "illegible": ["Nothing unreadable. At the thumb, 'c20 c23' (design 209-317, 1252) is struck through by the tower's left vertical member. 'DETECT AND AVOID' (design 200-493, 1166) sits on the tower lattice and is legible but cluttered."],
 "checklist": [
  {"item": "the airframe, wing and rotors are visible docked on the cradle and the airframe spans at least 45 percent of the frame width", "pass": false, "note": "Width passes: the wing runs from about x 120 to the right edge, over 85 percent. Rotors are visible. 'Docked' fails. The tower arm (design 400-650, 800-870) runs behind the wing, and the port lift-rotor pod and boom (design 273-317, 871-945) sit inside the tower lattice. The aircraft reads as skewered on the tower, not seated in a cradle. No contact or cast shadow joins airframe and cradle."},
  {"item": "three leaders each land on the thing they name within 24 px", "pass": false, "note": "ROUTE RESERVED BEFORE LAUNCH ends at design (631,823), on the first dash of the corridor beside the V tail. That lands. ONBOARD DETECT AND AVOID ends at (503,985), on a dark ball under the nose. It lands on a part that reads as a sensor turret. The company gives no location for the system, so the render asserts a position. PARACHUTE ends at (543,884), a dot on the upper wing root. No hatch is visible anywhere on the dorsal spine, so it does not land on the thing it names. The PARACHUTE leader also cuts diagonally across the whole fuselage underside and the orange slab."},
  {"item": "the route corridor is visible rising from the cradle into the sky", "pass": true, "note": "Visible and legible at 432 px. Chunky white-blue dashes near the tail thin to a dotted hairline leaving the top right at design (1080,553). It starts at the V tail (design 601,819), not at the cradle. The hairline portion is about 2 px, close to the moire threshold."},
  {"item": "the cradle ring carries the dusk gold accent", "pass": false, "note": "There is no ring. A flat salmon slab (design 442-756, 928-1006) sits under the belly with no shading, bevel, rim or contact shadow. It looks placed, not lit, and it is not attached to the tower arm. The accent is also large (about 314x78 design px) where the dossier says small. A second warm orange ball beacon sits on the tower top (design 286,793), so the accent is not unique."},
  {"item": "no leader crosses the hook or the dek", "pass": true, "note": "All leaders stay below y 700."},
  {"item": "the frame's median L* at 432px is 22 or lower", "pass": true, "note": "Dark navy field, by eye well under 22. Not measured: no value_register line was supplied."}
 ],
 "verdict": "revise",
 "must_fix": [
  {"what": "PARACHUTE leader lands on nothing. No dorsal hatch is modelled, and the leader crosses the airframe and gold slab.", "where": "dot at design (543,884). Leader runs from (688,1139) up through the fuselage underside.", "fix": "Model a visible dorsal hatch on the spine behind the wing root: a raised panel about 0.3 m long with a seam line, lighter than the skin. Move the leader dot onto its centre. Move the PARACHUTE label above the aircraft, to roughly design (680-860, 745), so the leader drops straight onto the hatch without crossing the body or the slab."},
  {"what": "The aircraft is not docked. The tower arm and left rotor pod interpenetrate, and the aircraft is not seated in the cradle.", "where": "design (273-317, 871-945) rotor pod inside the lattice. Arm at (400-650, 800-870). Slab at (442-756, 928-1006).", "fix": "Shift the aircraft right by about 0.8 m, or the tower left. The port boom must clear the column. Seat the belly on a modelled cradle rail with a visible contact line and a soft shadow on the arm. The cradle must be a ring or rail around the aircraft, not a slab under it."},
  {"what": "The accent slab is a flat unlit polygon, not a ring.", "where": "design (442-756, 928-1006)", "fix": "Replace it with a torus or rounded-rect rim in #E0956A, about 0.12 m thick. Give it a lit left edge, a dark underside and a contact shadow on the arm. Cut its width to under 200 design px. Drop the orange beacon ball at (286,793) or recolour it a neutral warm white."},
  {"what": "Footer ids and the DETECT AND AVOID label sit on the tower struts. The strut crosses the 'c' of c20.", "where": "'c18 c19 c20 c23' at design (83-320, 1252). Label at (83-493, 1166). Tower left column at x 199-375.", "fix": "Move the footer ids to the right of the tower, starting at x 380, or left-align the label and ids over an x 83-190 span with a shorter label. Alternatively move the tower to x 560 and reflow the aircraft. No label or footer glyph may touch a truss member."},
  {"what": "The sensor leader asserts a location the company never gives (c18).", "where": "dot at design (503,985), chin ball under the nose", "fix": "Land this leader on a whole thing, the forward fuselage centreline at about (480,930), as the dossier risk says. If a sensor window is kept, it must be a visible lighter glazed panel in the nose."}
 ],
 "frame_causes": [
  {"cause": "b", "problem": "The largest object is unfinished. The slab is flat. The rotors are hairline black needles, for example design (770-952, 820-840) and (165-408, 867), with no blade thickness. The fuselage is a clean grey lathe with none of the planned 'panel tooth and grime aft'. The V tail is flat plates, and the aircraft and tower interpenetrate.", "fix": "Give the rotor blades real chord (about 6 px at design scale) with a lit edge, add aft grime and panel breaks to the fuselage, and separate the tower from the boom as above."},
  {"cause": "c", "problem": "The lower right is dead. There is no ground, no pool and no cast, only flat navy (design 540-1080, 1161-1350) holding a label and the URL. The planned lower third (cradle edge, cast shadow, dark land in haze) is absent. Only faint grass tufts and the column run out of frame.", "fix": "Add the stage ground pool under the tower: a lit cradle edge, a cast shadow of the aircraft on the arm and column, and haze in the dark land. Put the PARACHUTE label higher so the lower right is not an empty field."},
  {"cause": "d", "problem": "The grass tufts at design (40-1050, 1110-1350) are flat unlit 2D sprites, clip-art against the navy. A dotted star band crosses the dek's last line, 'to illustrate.', at design (0-905, 540-610), and reads as a stray dotted line at 432 px. The thin black needles are artifacts.", "fix": "Remove the star band, or confine stars above y 380. Replace the sprite grass with lit, shadowed tufts or delete it."}
 ],
 "would_improve": [
  "Showstopper test: the frame is dark and the subject is large, lit from the left, with a bright wing edge, true-black rotors and a dark field. It fails as 'an object in a void'. The sky is a flat navy gradient with no horizon, no staged ground and no pool. It would read at 432 px as 'a drone hung on a pylon' and not 'an aircraft docked at a hub'. The light does not agree with the deck's lastLight key: there is no warm seam, and the tower is lit purple-grey while the airframe is beige-grey.",
  "The dek and the orphaned last line 'to illustrate.' would hold better with balanced wrapping or a non-breaking 'drawn to illustrate'. Slide 6 has the same orphan.",
  "Acceptance weakness: nothing on this list requires contact, a cast shadow or a visible hatch. A flat vector aircraft over a tower, with a salmon rectangle and three arrows, would pass nearly every item. 'Docked' is untestable as written. The dossier's own risk line (leaders on whole things) contradicts the composition line (nose sensor window, dorsal hatch). Add 'the aircraft's belly touches the cradle with a visible contact shadow' and 'the parachute hatch is a visible panel'.",
  "Copy: no colons, semicolons, dashes, banned words or numerals beyond the counter. All leaders and the dek trace to c18, c19, c20 and c23."
 ]
},
{
 "slide": "slide-06",
 "transcription": "THE OPERATIONS CENTER | 06 / 09 | People watch from somewhere else | Zipline says trained staff monitor its flights from a remote operations center. The room is drawn to illustrate. | c24 | texasaidocket.com",
 "illegible": ["Nothing unreadable. At the thumb, 'texasaidocket.com' (design 727-1000, 1252) is legible but sits on streaked desk grain and touches the lower edge of the monitor base."],
 "checklist": [
  {"item": "the near desk's monitors are visible with lit screens and the screens together span at least 40 percent of the frame width", "pass": true, "note": "Two near monitors plus three far screens span about 75 percent of the width. The screens are very dark navy with only thin glowing route lines, so 'lit' is marginal."},
  {"item": "a route line is visible on at least one screen with no legible text", "pass": true, "note": "Dashed cyan-white route with an orange origin dot on every screen. Hairline crossing lines read as airspace. No text."},
  {"item": "an operator sits at the next desk with their back to the camera and the face is not visible", "pass": true, "note": "The back is turned and the face is in profile, with only the ear and jaw visible. The dossier's risk is realised, though. The whole figure is in frame, not 'a shoulder and an arm'. The pale sculpted hair reads as a clay mannequin helmet, and the hands are blobby."},
  {"item": "the back wall stays darker than the screens", "pass": false, "note": "The right and back wall is black. The left wall panel (design 0-307, 0-610, brown, hard vertical corner at x 307) reads lighter than the screen glass at 432 px. The screens are not the brightest area. The operator's hair and the desk hotspot out-shine them."},
  {"item": "the frame's median L* at 432px is 22 or lower", "pass": true, "note": "Very dark by eye. Not measured: no value_register line was supplied."}
 ],
 "verdict": "revise",
 "must_fix": [
  {"what": "The operator's hair is the brightest object on the left and the plastic-doll look is the frame's weakest read. It competes with the dek, only about 40 px below the dek's last line.", "where": "head and hair at design (70-180, 515-640). Dek last line baseline at about (83-260, 487).", "fix": "Cut the hair and skin albedo to about 45 percent. Replace the helmet hair with a darker cropped cap with strand breaks. Remove the key that lights the head from the left front. Let only the screens light him, as a cool rim on the near cheek and shoulder. Move the figure down about 30 px, or crop him at the shoulder as the dossier planned."},
  {"what": "The screens are not credibly the room's one source. The screen glass is near black and spills little light. The brightest areas are a cool-white desk hotspot at bottom right and the warm head, both unmotivated.", "where": "hotspot at design (600-1000, 1280-1350). Screen fields at (540-1080, 730-1190).", "fix": "Raise screen emissive and add a screen-coloured area light spill (cool, about 3x current) onto the desk and keyboard, with a falloff toward the camera. Delete the front-left fill that lights the head and the bottom-right cone. Lift the screen field about 3 L* so the glass is the lightest large area."},
  {"what": "The footer URL sits on streaked desk grain, touching the monitor base's lower edge.", "where": "design (727-1000, 1252); base lower edge at about y 1248", "fix": "Move the monitor stand left by about 60 px and darken the desk plane under the footer (lower roughness streak contrast by about 60 percent). Or add a 12 percent black darkening gradient to the bottom 140 px. The URL must have under 3 L* variation behind it."},
  {"what": "The left wall panel is a flat brown plane with a hard vertical corner running through the hook's 'p' and 'l' and lighter than the screens.", "where": "design (0-307, 0-610); corner at x 307, behind 'People'", "fix": "Drop the wall albedo to near black, matching the right wall, or push the corner left of the type margin (x under 83). The left wall should not exceed the screens' value."}
 ],
 "frame_causes": [
  {"cause": "b", "problem": "The operator is a clay mannequin. The hair is a pale sculpted cap and the hands are blobby (design 170-290, 620-700). The chair back and torso merge into one dark mass, and the legs and a warm floor patch (design 45-165, 740-770) float beside the chair.", "fix": "Retexture the person as above and reduce the figure to the head and shoulders cropped by the frame. Remove the orange floor patch or tie it to a visible source."},
  {"cause": "d", "problem": "The desk veneer reads as bright, thin wavy filaments running in long streaks, like smeared line noise, not walnut. The streaks are brightest in the lower right pool (design 500-1080, 1000-1350).", "fix": "Lower the grain's specular strength and widen the grain scale about 2x. Keep the veneer as a broad low-contrast grain, so the lit pool reads as a surface and not as hatch lines."}
 ],
 "would_improve": [
  "Showstopper test: a dark interior and one subject (desk and monitors) fill about half the frame, with true blacks. It reads at 432 px as 'a control-room operator at a desk' in one word. It passes that test on subject and scale. It fails on light logic (hair and hotspot over screens) and on a credible, finished person.",
  "Hook and dek sit on a dark field with good contrast. The upper right (design 300-1080, 0-700) is deliberate dark space, acceptable for this interior. The planned lower-third keyboard edge is barely visible, and the keyboard needs a lit edge.",
  "Acceptance weakness: no item says the screens must be the source, or bounds the operator's figure or brightness. A bright mannequin lit from the front passes every item. Add 'the brightest large area is a screen' and 'no surface other than a screen exceeds the screens in value'.",
  "Copy: matches c24. No colons, semicolons, dashes or banned words, and no numerals beyond the counter."
 ]
}
]
```

Files reviewed (absolute paths):
- /home/user/TexasAIDocket/out/2026-10-26/render/slide-05.png
- /home/user/TexasAIDocket/out/2026-10-26/render/slide-06.png
- /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-05-thumb.png
- /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-06-thumb.png
- /home/user/TexasAIDocket/out/2026-10-26/render/crops/slide-05-r1c1.png through slide-05-r3c2.png
- /home/user/TexasAIDocket/out/2026-10-26/render/crops/slide-06-r1c1.png through slide-06-r3c2.png
- /home/user/TexasAIDocket/out/2026-10-26/storyboard.md
- /home/user/TexasAIDocket/out/2026-10-26/copy.json
- /home/user/TexasAIDocket/out/2026-10-26/claims.json