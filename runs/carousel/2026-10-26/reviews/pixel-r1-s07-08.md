REVIEW, carousel no. 61, run 2026-10-26, slides 07 and 08. I read both full renders, both 432px thumbs, all 12 native crops (r1c1 to r3c2 per slide), the storyboard dossiers, copy.json and claims.json. Both slides get verdict REVISE. I had no shell, so I could not run value_register.py and I have no measured median L*. The L* items below are judged by eye. Coordinates are in the 1600x2000 display frame (design x 1.48), unless marked as a crop.

=== SLIDE 07 ===
```json
{
 "slide": "slide-07",
 "transcription": "ROWLETT, MAY 20TH, 2025 | 07 / 09 | Rowlett wrote the rule first, DroneXL reports | Rowlett's minutes record a 6 to 0 vote adding drone hubs and kiosks to its zoning code on May 20th, 2025. Zipline was the applicant. In the minutes a member says the hub's special use permit \"is the control.\" The chamber is drawn to illustrate. | c43 c46 c47 c48 c51 c54 | texasaidocket.com",
 "illegible": [],
 "lit_tally_count": "SIX. Display frame: (285,1095), (683,1075), (945,1065), (1140,1050), (1285,1040), (1400,1040). Thumb: six dots at x about 75, 183, 255, 308, 347, 377. Caveat: two faint unlit gooseneck stems show behind the chair backs at about (868,1112) and (1040,1110) (crop r2c2 at (90,600) and (340,600)). A reader may count eight microphones.",
 "checklist": [
  {"item": "dais runs full frame width in perspective, front at least 60 px tall at 432px", "pass": true, "note": "Runs from the left edge to the right edge. Front is about 150 px tall at the thumb."},
  {"item": "exactly six microphone tallies are lit", "pass": true, "note": "Six lit. The two ghost stems above put the 'six microphones' plan at risk."},
  {"item": "sheet of minutes visible on lectern desk in foreground", "pass": true, "note": "Present, bottom centre, cut by the bottom edge. It is flat: ruled bars, no paper thickness."},
  {"item": "back wall stays in shadow, never lit face on", "pass": true, "note": "Dark. The wall and ceiling planes meet in an odd diagonal at (0,100) to (990,470) and a vertical corner at x=990."},
  {"item": "no person, flag text or legible nameplate in frame", "pass": true, "note": "The nameplates are blank wooden wedges. The plan called them brass."},
  {"item": "frame median L* at 432px is 22 or lower", "pass": true, "note": "Judged by eye only. The top 45 percent is near black and the walnut mass sits at mid-low L*. No value_register line was available."}
 ],
 "verdict": "revise",
 "must_fix": [
  {"what": "The dais floats in a void. There is no floor and no contact. The bench's lower edge runs as a hard diagonal against flat black from (240,1900) to (1600,1350).", "where": "(240-1600, 1350-1900)", "fix": "Add a dark floor plane under the dais inside TXT.interior. Add a 30 px soft contact and ambient-occlusion band along the bench base with a kick-plate shadow. Let the lectern lamp spill fall off across the floor so the right-hand black triangle (880-1600,1400-1720) gets a value step."},
  {"what": "The tally glows are flat tan disc sprites with a visible circular edge, not lit tallies. They are about 110 px wide in the crop and desaturated. On mics 3 to 6 the disc floats off the mic head.", "where": "six discs at (285,1095), (683,1075), (945,1065), (1140,1050), (1285,1040), (1400,1040)", "fix": "Replace the discs with a small emissive LED on each mic collar (#FFE6B8, bright core). Add a gaussian bloom of about 40 px with no hard rim, centred on the LED. Make the tallies the lightest thing in the frame after the paper."},
  {"what": "The dais front is lit almost evenly and is the frame's big warm mid-tone mass (about 45 percent of the area). It has no pool, no falloff and no true dark. The key reads as fill, not as the declared west window plus lamps. That is the grey-middle look the owner rejected.", "where": "dais front (0-1600, 1300-1900)", "fix": "Move the key to rake from the left through the window. Add falloff so the panels darken about 40 percent toward the bottom and the right. Keep the highlight on the bench top and the mic zone. Let the tallies and paper be the only bright marks."},
  {"what": "The wood grain is an over-scaled procedural pattern of wavy light filaments, high contrast, at the same scale on the end cap and the panels. At 100 percent it reads as a line texture, not as walnut. The stiles and rails are crude strips.", "where": "dais panels (250-1500, 1330-1850) and the lectern top", "fix": "Cut grain contrast by about 50 percent. Halve the wave amplitude and scale the grain about 2x finer. Orient it along the board. Bevel the stile edges."},
  {"what": "The footer url's first glyph 't' sits on the paper's right edge, over a smudgy dark text-shadow blotch. The same smudge stains the wood to the right of the url. The c54 chip ends about 10 design px from the paper's shadow.", "where": "url (1080-1105, 1840-1875) and the smudge (1100-1480, 1840-1880), c54 near (660,1855)", "fix": "Move the minutes sheet about 80 display px left, or narrow it, so its right edge is at x 1030 or less. Delete the per-glyph dark shadow and use a bottom gradient wash that only darkens, over the last 140 design px."},
  {"what": "The lectern microphone's black windscreen ball sits on the dais top edge. At the thumb it reads as a black lollipop in front of the tallies. Its stem disappears behind the lectern desk and is not attached.", "where": "ball (1115-1185, 1190-1255), stem (1105, 1255-1720)", "fix": "Lower and shorten the lectern gooseneck so its head sits below the dais lip. Seat its base on the lectern desk edge. Rim the head with the key so it reads as a mic."}
 ],
 "frame_causes": [
  {"cause": "b", "problem": "The largest object (the dais) is unfinished. It has crude stile and rail moulding, procedural grain, slab chair backs with a purple rail strip, and flat-black chair blocks at (100,1200) and (590,1160). It has no floor contact. The bottom-left corner object at (0-80,1850-2000) is an unreadable clipped block.", "fix": "Finish the dais with a floor, kick plate and contact. Give the chairs a leather material with a lit edge. Remove or light the clipped object at the bottom left."},
  {"cause": "c", "problem": "The lower-right region is a flat black triangle with no floor, about 720x320 px.", "fix": "Add a floor with lamp falloff there, or crop the camera so the dais fills it."},
  {"cause": "d", "problem": "The halo sprites have visible disc edges, and the dark text-shadow smudge sits on the paper and wood at the footer.", "fix": "Use bloom with a gaussian falloff, and a bottom gradient in place of the glyph shadow."}
 ],
 "primary_image_law": {
  "world": "A dark TXT.interior chamber with the walnut dais under lamps. The staged world is the declared one.",
  "light_agreement": "Partial. The tallies and a gold spill on the bench top agree with a warm low key. The dais front is lit flat and contradicts the 'dark around one source' register.",
  "showstopper": "Mid. The frame is dark and the subject is large, about 55 percent. It has no true pool, no contact and no dirt, and the dais sits in a void. At 432px I read it in one word as a council bench or dais with lit mics. That passes the subject test.",
  "rendered_vs_placed": "Mostly rendered, with a material and a soft spill. The paper and the halos read as placed. There is no halftone or hatch."
 },
 "would_improve": [
  "Both layers of the plan are weak. The acceptance list would pass on a dark frame holding a brown box, six dots and a white rectangle. Add a testable item such as 'the tallies are the brightest non-paper pixels and the dais front falls off at least 3 L* steps left to right'.",
  "The headline claims Rowlett wrote the rule 'first'. The attribution to DroneXL is in the headline, and c43 is medium confidence. Keep it that way.",
  "The apostrophes in 'Rowlett's' and 'hub's' look curly in the crop at (165-440,750-790). copy.json holds straight ones, and the house rule is straight quotes only. The double quotes are straight. Verify the glyph.",
  "Remove the extra unlit mic stems, or show a seventh and eighth seat deliberately.",
  "Match the plan's 'brass' nameplates, or drop the word."
 ]
}
```

=== SLIDE 08 ===
```json
{
 "slide": "slide-08",
 "transcription": "UNDER THE FLIGHT PATH | 08 / 09 | The neighbor gets an email address | Round Rock directs operational feedback to Zipline at community@zipline.com and safety concerns to the FAA. Citing Community Impact, DroneXL reports a limit of about 5 pounds per order, lowered on a tether. The pod and yard are drawn to illustrate. | c6 c13 c14 c38 | texasaidocket.com",
 "illegible": [],
 "glyph_check": "The thumb reads '5 pounds' and '08 / 09' correctly. No 3/5 confusion. The dek text matches claim c38.",
 "checklist": [
  {"item": "pod and gold band visible with tether rising out of right edge", "pass": true, "note": "The pod is at (1240-1365,1035-1235). The tether runs to the top-right edge. The band is a flat rectangle."},
  {"item": "pod stands at least 40 px tall at 432px", "pass": true, "note": "About 54 px."},
  {"item": "resident visible at fence, turned away, at least 50 px tall at 432px", "pass": true, "note": "About 96 px tall, back to camera, hand at cap."},
  {"item": "lawn under the pod is lit and the person casts a contact shadow", "pass": false, "note": "The lawn is near black with sparse straw tufts and no pool under the pod. The figure's feet show no contact shadow on the ground. Only a hard black silhouette falls on the fence."},
  {"item": "tether does not cross hook or dek", "pass": true, "note": "The tether stays right of x=1300 at the dek lines."},
  {"item": "frame median L* at 432px is 24 or lower", "pass": true, "note": "Judged by eye only. Most of the frame is near black. No value_register line was available."}
 ],
 "verdict": "revise",
 "must_fix": [
  {"what": "The lawn is a black void with floating tufts, and the pod has no pool of light on it. The dossier's own focal ('the lit pod and its pool on the lawn') is missing. The fence base meets black with no contact.", "where": "(0-1600, 1600-2000)", "fix": "Add a warm spot under the pod, radius about 3 m. Put a worn straw lawn texture under it with visible ground. Ground the fence base with a 20 px contact darkening. Place the tufts on the lit ground only. Thin the tufts that sit behind the footer."},
  {"what": "The shadows are hard-edged pure black. The pod's shadow is a detached black capsule on the fence, offset about 100 px below the pod. At the thumb it reads as a hole in the fence. The figure's shadow is also hard black.", "where": "pod shadow (1195-1290, 1250-1380), figure shadow (440-545, 1340-1620)", "fix": "Use PCSS penumbra for the sun shadows. Tint the shadow to about L* 8-12 instead of #000. Raise the light, or lower the pod, so the shadow ties visibly to the pod. Add a real contact where the figure's feet meet the ground."},
  {"what": "The pod is unfinished. The gold band is a flat unshaded rectangle wider than the capsule. It overhangs the silhouette and is not wrapped on the curve. The white two-prong decal on it is flat. The capsule is clean, with no grime, a weak rim and no specular.", "where": "pod (1238-1366, 1035-1235), band (1238-1366, 1090-1162), decal (1245-1272, 1135-1200)", "fix": "Wrap the band on the pod's cylinder at radius 1.01x with the same roughness. Give it a lit left edge and shading, and keep #E0956A. Model the tab with thickness or delete it. Add scuffs near the tether eye and a key rim on the left."},
  {"what": "The subject is too small. The pod is about 8 percent of the frame width and the resident about 7 percent. The biggest thing in the frame is a flat, evenly lit fence band. That is not 'one subject filling a third of the frame'.", "where": "whole frame", "fix": "Dolly from about 12 m to about 5-6 m and set the fov to about 38. The pod and resident then fill about 25-30 percent of the frame height. Light the fence in a falloff pool, not edge to edge."},
  {"what": "The resident's model is weak. The jeans texture is blurred against the crisp fence. The raised arm is a stiff slab in a red-brown that does not match the neck skin. The head is tiny.", "where": "(375-545, 1285-1640)", "fix": "Raise the figure's texture resolution and match the arm skin to the neck. Bend the raised arm at the elbow. Scale the head up about 10 percent."},
  {"what": "Straw tufts cross the footer glyphs, and low-contrast gold blades pass behind the 'texasaidocket.com' letters. The oak foliage highlights sit behind the left dek lines.", "where": "footer (1080-1480, 1830-1890), dek left (0-500, 150-1100)", "fix": "Clear the tufts in the footer band of 60 design px. Darken the oak crown behind the dek by 30 percent, or lower it out of the text block."}
 ],
 "frame_causes": [
  {"cause": "b", "problem": "The largest object is unfinished. The pod has a flat band and decal and no wear. The resident reads as a mannequin with a blurred jeans texture.", "fix": "Wrap the band as a lit cylinder segment. Add wear. Raise the figure's texture resolution."},
  {"cause": "c", "problem": "The bottom 20 percent is a black lawn with no ground information.", "fix": "Add the pod's warm lawn pool and a visible ground texture."},
  {"cause": "d", "problem": "The pod's detached hard black shadow capsule reads as a hole in the fence. The jeans texture is blurred.", "fix": "Use a soft, tinted PCSS shadow tied to the pod, and a sharper figure texture."}
 ],
 "primary_image_law": {
  "world": "A night yard on the staged dark sky, with a cedar fence, an oak and one subject area. The sky is a deliberate near-black navy.",
  "light_agreement": "Partial. The fence and figure are raked from the camera's left, as the deck's key says. The pod's rim and the missing lawn pool do not carry the same light. The tree-shadow blotches on the fence top at left are consistent.",
  "showstopper": "Mid-low. The frame is dark, with true blacks and a lit fence, but the subject is small and the ground is dead. At 432px I read it as a person shading their eyes at a fence while a pale capsule hangs on a line. That works as a narrative. The planned brick house wall and the pod's pool are missing.",
  "rendered_vs_placed": "Rendered, with materials (cedar boards and cloth). The grass tufts read as scattered cutout sprites, and the band as a placed decal. No screen texture."
 },
 "would_improve": [
  "The footer chip 'c6' cites a claim the dek never states. The dossier listed c13, c14 and c38 only. Remove c6 from the chips, or add its sentence.",
  "The accent band renders salmon-orange. Tune it toward dusk gold #E0956A with shading.",
  "The oak crown and brick wall in the plan are barely present. Either show them lit by the key or drop them from the plan."
 ]
}
```

Copy checks on both slides. There are no colons, semicolons, dashes or emojis. "can't" is not at issue, since neither dek uses it. None of the words gap, matters or pattern appear. Every numeral traces to a claim: 6 to 0 and May 20th, 2025 to c47 and c46, and about 5 pounds to c38. Slide 07's headline attributes c43 (medium confidence) to DroneXL.

Files read: /home/user/TexasAIDocket/out/2026-10-26/render/slide-07.png, /home/user/TexasAIDocket/out/2026-10-26/render/slide-08.png, /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-07-thumb.png, /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-08-thumb.png, the 12 crops under /home/user/TexasAIDocket/out/2026-10-26/render/crops/, /home/user/TexasAIDocket/out/2026-10-26/storyboard.md, /home/user/TexasAIDocket/out/2026-10-26/copy.json and /home/user/TexasAIDocket/out/2026-10-26/claims.json.