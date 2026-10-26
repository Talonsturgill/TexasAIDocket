ROUND 2 RECHECK, carousel no. 61, slides 07 and 08. I read both full renders, both 432px thumbs, slide 07 crops r2c1, r2c2, r3c1 and r3c2, slide 08 crops r2c1, r2c2, r3c1 and r3c2, copy.json and the craft block in brief_all.txt. I did not re-read the storyboard or claims.json, so the checklist items below are the round 1 versions. I had no shell, so I have no value_register line and the L* items are judged by eye. Coordinates are in the 1600x2000 display frame unless marked.

Both slides stay REVISE.

=== SLIDE 07 ===
```json
{
 "slide": "slide-07",
 "transcription": "ROWLETT, MAY 20TH, 2025 | 07 / 09 | Rowlett wrote the rule first, DroneXL reports | Rowlett's minutes record a 6 to 0 vote adding drone hubs and kiosks to its zoning code on May 20th, 2025. Zipline was the applicant. In the minutes a member says the hub's special use permit \"is the control.\" The chamber is drawn to illustrate. | c43 c46 c47 c48 c51 c54 | texasaidocket.com",
 "illegible": [],
 "lit_tally_count": "SIX. Display frame: mic 1 (270,1060), faint; mic 2 (680,1040); mic 3 (945,1025); mic 4 (1135,1000); mic 5 (1285,985); mic 6 (1400,990). Thumb: glows at x about 75 (barely), 183, 255, 308, 347, 377. The halos are smaller and dimmer than round 1. Two unlit gooseneck stems still show behind the chair backs at about (873,1110) and (1058,1100) (crop r2c2 at (100,550) and (350,570)). They are very faint and invisible at the thumb, so a reader counts six.",
 "checklist": [
  {"item": "dais runs full frame width in perspective, front at least 60 px tall at 432px", "pass": true, "note": "Unchanged. About 150 px tall at the thumb."},
  {"item": "exactly six microphone tallies are lit", "pass": true, "note": "Six lit. Mic 1's glow is the weakest and is nearly lost at the thumb. Two ghost stems are still present at full size."},
  {"item": "sheet of minutes visible on lectern desk in foreground", "pass": true, "note": "Present at bottom left, cut by the bottom edge. It is flat ruled bars with no paper thickness. Its right edge is now at x about 565, so the url no longer touches it."},
  {"item": "back wall stays in shadow, never lit face on", "pass": true, "note": "Dark. The odd diagonal wall and ceiling join at (0,60) to (990,470) remains."},
  {"item": "no person, flag text or legible nameplate in frame", "pass": true, "note": "The nameplates are blank wedges and read as wood, not brass."},
  {"item": "frame median L* at 432px is 22 or lower", "pass": true, "note": "Judged by eye only. The upper 45 percent is near black. The walnut dais is a large mid-low mass, about 40 percent of the frame."}
 ],
 "round1_must_fix_status": [
  {"item": "1. Dais floats in a void, no floor or contact", "status": "NOT RESOLVED", "note": "Crop r3c2 still shows the bench base as a hard diagonal against flat black. The right-hand triangle (880-1600,1350-1900) is still empty black with only faint floor cracks. There is no kick plate shadow or contact band."},
  {"item": "2. Tally glows are flat discs", "status": "PARTIAL", "note": "They are smaller and dimmer, and the 'big tan plates' read is gone. In crop r2c2 mics 2 to 6 still show a circular rim edge on the halo, and the LED heads are tiny. They read as small lit mics at the thumb, which is acceptable."},
  {"item": "3. Dais front lit flat, grey-middle mass", "status": "NOT RESOLVED", "note": "The panels are still evenly lit across 0 to 1500, with no falloff to the right or bottom and no true dark inside the mass. The downlights are dimmer, but the bench top spill at (400-900,1160-1190) is the only pool."},
  {"item": "4. Over-scaled wavy grain", "status": "NOT RESOLVED", "note": "Crop r3c1 shows the same high-contrast light filaments at the same scale on the panels and the lectern top. It reads as a line texture, not walnut. The stiles are still plain strips."},
  {"item": "5. Footer collides with paper and smudge", "status": "PARTIAL", "note": "The url is clear of paper and sits on clean black, so that half is fixed. The c43 to c54 chips now sit ON the paper's lower left, over its text bars, with a dark per-glyph shadow blotch (crop r3c1 at (150-920,650-760)). The blotch smears the paper and the wood to the right of c54. Light chips over the paper's ruled lines read as a smudge, and c43 and c46 lose their edge against the white paper."},
  {"item": "6. Lectern microphone ball", "status": "RESOLVED", "note": "The black windscreen ball is gone. The lectern desk is bare apart from the sheet."}
 ],
 "verdict": "revise",
 "must_fix": [
  {"what": "The dais has no floor and no contact. Its base is a hard diagonal against flat black, and the lower right is a dead black triangle.", "where": "(240-1600, 1350-1900)", "fix": "Add a dark floor plane inside TXT.interior under the dais. Add a 30 px soft contact and ambient-occlusion band along the bench base and a kick-plate shadow. Let the lectern-side lamp spill fall across the floor so the right-hand triangle takes a value step."},
  {"what": "The dais front is one evenly lit warm mass with no falloff. The grain is over-scaled, high contrast and the same on every board.", "where": "dais panels (0-1500, 1300-1850), lectern top (0-940, 1670-2000)", "fix": "Rake the key from the left so the panels fall about 40 percent toward the bottom and right. Cut grain contrast about 50 percent and scale the grain about 2x finer along each board. Keep the bright marks to the bench top, the six tallies and the paper."},
  {"what": "The claim chips c43 to c54 sit over the paper's text bars and over a dark per-glyph text-shadow smudge that stains the paper and the wood. c43 and c46 lose their edge against the white sheet.", "where": "chips (120-665, 1835-1875), smudge (100-920, 1800-1880)", "fix": "Move the sheet up about 150 display px, or shorten it, so its bottom edge sits above y 1780 and the chips sit on bare wood. Remove the per-glyph dark shadow and use a bottom gradient wash that only darkens, over the last 140 design px."},
  {"what": "The tally halos still show a circular rim. Mic 1's glow is nearly invisible at the thumb.", "where": "halos at (270,1060), (680,1040), (945,1025), (1135,1000), (1285,985), (1400,990)", "fix": "Replace the sprite with a gaussian bloom with no hard edge, with a small emissive core on the collar. Raise mic 1's tally to match mic 2 so the thumb shows six equal dots."}
 ],
 "frame_causes": [
  {"cause": "b", "problem": "The largest object, the dais, is still unfinished. It has crude stile and rail strips, procedural grain with no scale change, no floor contact, and flat black chair slabs at (100,1200) and (590,1160).", "fix": "Add floor, kick plate and contact. Fine the grain and bevel the stile edges."},
  {"cause": "c", "problem": "The lower-right region (880-1600, 1350-1900) is flat black with no floor information, about 720x500 px.", "fix": "Add a floor with lamp falloff there."},
  {"cause": "d", "problem": "The halo sprites have visible rims, and the dark text-shadow smudge sits on the paper and wood behind the chips at (100-920,1800-1880).", "fix": "Use a gaussian bloom and a bottom gradient in place of the glyph shadow."}
 ],
 "primary_image_law": {
  "world": "A dark TXT.interior chamber with the walnut dais under lamps. The staged world is the declared one.",
  "light_agreement": "Partial. The tallies and a warm bench-top spill agree with a low key. The dais front is lit flat, which contradicts 'dark around one source'.",
  "showstopper": "Mid. The camera lift gives a clearer dais read, and at 432px it reads in one word as a council bench with lit mics. It still has no pool, no contact and no dirt, and it sits in a void.",
  "rendered_vs_placed": "Mostly rendered. The paper and the halos still read as placed. No halftone or hatch is present."
 },
 "would_improve": [
  "The acceptance list would still pass on a dark frame holding a brown box, six dots and a white rectangle. Add a testable item such as 'the dais front falls off at least 3 L* steps from left to right and a floor contact band is present'.",
  "Remove the two ghost stems, or show a seventh and eighth seat on purpose.",
  "The apostrophes in Rowlett's and hub's render curly at the thumb and at 100 percent, though copy.json holds straight ones. The house rule is straight quotes. Check whether the font's straight apostrophe glyph is drawn curly, or whether a typographic replacement runs in the renderer.",
  "The brief calls the nameplates brass and they read as plain wood wedges. Match the plan or drop the word."
 ]
}
```

=== SLIDE 08 ===
```json
{
 "slide": "slide-08",
 "transcription": "UNDER THE FLIGHT PATH | 08 / 09 | The neighbor gets an email address | Round Rock directs operational feedback to Zipline at community@zipline.com and safety concerns to the FAA. Citing Community Impact, DroneXL reports a limit of about 5 pounds per order, lowered on a tether. The pod and yard are drawn to illustrate. | c6 c13 c14 c38 | texasaidocket.com",
 "illegible": [],
 "glyph_check": "The thumb reads '5 pounds' and '08 / 09' correctly. There is no 3/5 confusion. The dek matches c38.",
 "checklist": [
  {"item": "pod and gold band visible with tether rising out of right edge", "pass": true, "note": "The pod is at (1220-1385,985-1255). The tether runs to the top-right edge. The band is a flat rectangle."},
  {"item": "pod stands at least 40 px tall at 432px", "pass": true, "note": "About 70 px."},
  {"item": "resident visible at fence, turned away, at least 50 px tall at 432px", "pass": true, "note": "About 95 px."},
  {"item": "lawn under the pod is lit and the person casts a contact shadow", "pass": false, "note": "Two failures. The lawn is still near black with sparse straw tufts and no warm pool anywhere (crop r3c1 and r3c2 show black ground). The pod is also drawn above the fence line and not over any lawn. The figure's feet have only a faint sole line and no contact shadow, and the hard black silhouette falls on the fence."},
  {"item": "tether does not cross hook or dek", "pass": true, "note": "The tether stays right of x=1300 at the dek lines."},
  {"item": "frame median L* at 432px is 24 or lower", "pass": true, "note": "Judged by eye only. Most of the frame is near black."}
 ],
 "round1_must_fix_status": [
  {"item": "1. Lawn is a black void, no pool under the pod, no fence-base contact", "status": "NOT RESOLVED", "note": "No porch flood is visible anywhere in the render. The lawn is black and the fence base meets it with only a thin darker line. The warm pool the repair describes is not in the pixels."},
  {"item": "2. Hard black shadows, detached pod capsule on the fence", "status": "PARTIAL", "note": "The detached pod capsule on the fence is gone. The figure's shadow is still a hard pure-black silhouette on the fence (440-545,1340-1620) with no penumbra, and the feet have no contact."},
  {"item": "3. Pod unfinished: flat overhanging band, flat decal, clean capsule", "status": "NOT RESOLVED", "note": "Crop r2c2 shows the band as a flat salmon rectangle wider than the capsule. It overhangs both silhouette edges and is not wrapped on the curve. The white tab is still a flat rectangle. The capsule is clean with no wear. Two stray black and white corner fragments sit at its base at about (1365,1235)."},
  {"item": "4. Subject too small", "status": "NOT RESOLVED", "note": "The pod is about 10 percent of the frame width and the resident about 10 percent. The fence is still the biggest object, an evenly lit band across the full width. A slight improvement from the closer camera, but not a third of the frame."},
  {"item": "5. Resident model weak", "status": "NOT RESOLVED", "note": "Crop r3c1 shows the same blurred jeans texture, the stiff slab arm in red-brown that doesn't match the neck, and a tiny head."},
  {"item": "6. Straw tufts and oak foliage over type", "status": "PARTIAL", "note": "The url now sits on mostly clear black, with only a blade at the far right of its band. Tufts still sit behind the chips c13 and c14 and around (0-1000,1700-2000), and blades are still rooted close to the baseline of c6 c13 c14 c38. The oak foliage at (0-330,600-1150) still sits behind the first characters of the dek lines. The dek stays legible."}
 ],
 "verdict": "revise",
 "must_fix": [
  {"what": "The warm porch pool on the lawn is not rendered. The lawn is black, the pod hangs above the fence and not over the lawn, and the dossier's focal ('the lit pod and its pool on the lawn') is missing.", "where": "(0-1600, 1700-2000) and the lawn under the pod", "fix": "Verify that the porch light is on and reaches the lawn, then raise its intensity until a pool about 3 m across is visible on the ground. Put the pod's tether line and its landing point over the lawn in front of the fence, or add a short fence-top ledge of light so the pod is tied to the yard. Put the tufts only on the lit ground."},
  {"what": "The figure's shadow is a hard pure-black silhouette on the fence, and the feet have no contact shadow.", "where": "shadow (440-545,1340-1620), feet (160-260,1740-1760)", "fix": "Use a PCSS penumbra and tint the shadow to about L* 8 to 12 instead of #000. Add a 15 px dark contact ellipse under the shoes on the ground."},
  {"what": "The pod band is a flat unshaded rectangle that overhangs the capsule. The tab is flat, the capsule is clean and there are stray corner fragments at its base.", "where": "pod (1220-1385,985-1255), band (1220-1385,1075-1140), tab (1238-1272,1165-1235), fragments (1365,1235)", "fix": "Wrap the band on the cylinder at 1.01x radius with the same roughness and a lit left edge, keeping the dusk gold #E0956A. Delete the flat tab or give it thickness, remove the stray fragments and add scuffs near the tether eye."},
  {"what": "Straw tufts still sit behind and across the chips and footer band.", "where": "footer band (0-1480, 1830-1900), chips (120-450, 1835-1875)", "fix": "Clear the tufts in a 60 design px band across the footer and keep the lawn tufts to the lit pool only."},
  {"what": "The resident is weak. The jeans texture is blurry, the arm skin does not match the neck, and the head is small.", "where": "(375-545, 1285-1640)", "fix": "Raise the figure's texture resolution, match the arm skin to the neck, bend the raised arm at the elbow and scale the head up about 10 percent."}
 ],
 "frame_causes": [
  {"cause": "b", "problem": "The largest objects are unfinished. The pod band is flat and overhangs the capsule, the tab is flat, and the resident reads as a mannequin with blurry jeans.", "fix": "Wrap the band as a lit cylinder segment, add wear, and raise the figure's texture resolution."},
  {"cause": "c", "problem": "The bottom 15 percent of the frame is black lawn with sparse tufts and no ground information, and no pool.", "fix": "Make the warm porch pool reach the ground and give it a worn lawn texture."},
  {"cause": "d", "problem": "The figure's shadow is hard black, and stray black and white fragments sit at the pod's base at about (1365,1235).", "fix": "Use a soft tinted shadow and remove the fragments."}
 ],
 "primary_image_law": {
  "world": "A night yard on the staged dark sky, with a cedar fence, a partial oak crown and a dark lawn. No house or porch light is visible.",
  "light_agreement": "Weak. The fence and figure are lit from the camera's left, but the declared warm porch flood is not in the pixels, so the pod and the lawn don't carry any matching light.",
  "showstopper": "Mid-low. The frame is dark with a lit fence, and at 432px I read it in one word as a person shading their eyes at a fence with a capsule on a line. The subject is still small and the ground is dead.",
  "rendered_vs_placed": "Rendered, with cedar boards and cloth. The grass tufts read as scattered cutouts and the band as a placed decal. No screen texture."
 },
 "would_improve": [
  "The chip c6 cites a claim the dek never states. The dossier lists c13, c14 and c38 only. Remove c6 from the chips, or add its sentence.",
  "The accent band renders salmon and not dusk gold #E0956A. Tune it with shading.",
  "The brick house wall in the plan is absent. Drop it from the plan or light it with the key so the porch flood has a source."
 ]
}
```

Files read: /home/user/TexasAIDocket/out/2026-10-26/reviews/pixel-r1-s07-08.md, /home/user/TexasAIDocket/out/2026-10-26/render/slide-07.png, /home/user/TexasAIDocket/out/2026-10-26/render/slide-08.png, /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-07-thumb.png, /home/user/TexasAIDocket/out/2026-10-26/final/thumbs/slide-08-thumb.png, the crops listed above under /home/user/TexasAIDocket/out/2026-10-26/render/crops/, /home/user/TexasAIDocket/out/2026-10-26/tmp/brief_all.txt, /home/user/TexasAIDocket/out/2026-10-26/copy.json.