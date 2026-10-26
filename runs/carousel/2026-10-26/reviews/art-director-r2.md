{
  "decision": "revise",
  "inputs": {
    "slides/slide-01.html": "d549d868d2e0872c00fe4c3f9e7706be7886c65415d88b57507c59aa79001c59",
    "render/slide-01.png": "a58cc51b7107a9bfdc6d5d31de3f28a56acd98141fe07f6133c487c67791f6f5",
    "assets/js/deck/2026-10-26-tether.js": "95951eb7cde825a17599e30c30c1dd24fca21ef919ef15a2077626b41388781b",
    "assets/js/noise.js": "ae48620fda646edad7262f62e8c7b394d971103327e75d405a113bd4ef4ebeaa",
    "assets/js/three.module.min.js": "08fd7545d13d2c7fb65ab691530a802dafefd638596501854f267d0fb13c39e7",
    "assets/js/txcolor.js": "0da3f0e2bc0fc005bd501806550590ad711be135d5c371012fee6af0048fb01c",
    "assets/js/txdeck.js": "8cc8c4aecdb329a0e2c31530fe94ed42b5691c638160f318d72f2ca69e4d8380",
    "assets/js/txkit.js": "f1d05898dd31b3cea5a127fd114e438f6b55ac0c962241a5c79eedcf7866cd64",
    "assets/js/txlayout.js": "a31072fd1ed965a34ad16d80007633a1055fe92897c1c8f6c870a1c33348d04e",
    "assets/js/txpost.js": "e46fc8aa813b870b7eaba8b152079b8b902081718369e612eac7fdd22cd816f0",
    "assets/js/txthree.js": "731e164ca252500792cc508af0c16c0c06d4c7261e4a89064de2367bf875aac0",
    "assets/js/txtype.js": "b1dfe1eb2e283498b839301766453c3693add52601bb99db0f36412f3f4bc3de",
    "slides/slide-04.html": "692000b73c0aed634de9ea3fd5c4b0a553548974508d562a50000e4434f3ce2a",
    "render/slide-04.png": "1f1647bfff9cfd1b234de23fd559d6781e8ade4d201d4f33294543e6ec03efcd",
    "slides/slide-09.html": "f6e46532be2427bc8a503960228bea28606c44cce44dc7f0d21be17c81a4adea",
    "render/slide-09.png": "1794cfb33f26806ca2ae0164ca60af4b1f3f11ac1e398f35fdd99555d5bd569b"
  },
  "frames": [
    {
      "slide": 1,
      "role": "cover",
      "subject": "a pale fixed-wing delivery aircraft with faired booms, lathe nacelles, a V tail and glowing nav lights, a banded pod on a short tether below it, high over a glowing street-lamp grid at night",
      "visual_consequence": "With the headline covered, the frame reads as a delivery aircraft already carrying a parcel at height over a town. The lamp strings follow a street grid that converges to the horizon. The red port light and the white strobe glow, so the aircraft reads as flying at night.",
      "weakness": "The new pod band is a regression. It is now a flat, completely unshaded salmon rectangle covering about a third of the pod's height. On the lit side the shell runs from a hot highlight to dark, while the band holds one flat value across the whole curve. Its side edges are straight verticals that stand slightly proud of the pod's rounded silhouette (r3c1 at x 925, y 320 to 495, and r3c2 at x 0 to 123, y 320 to 495). It reads as a 2D sticker pasted over a lit object, not paint on a turned shell, and at feed size it is the brightest flat block in the art. The fin passes in front of the band with a square notch cut into it (r3c2 at x 97 to 125, y 425 to 575). The rest is now finished. The lamps are soft glows with hot cores, the pylons are airfoil fairings and the nav lights bloom. The pusher keeps only a faint residual arc below the tail (r2c2 at x 170 to 430, y 800 to 900), which is acceptable.",
      "repair": "Return the band to the lit physical material, a narrower inset lathe ring with the same shading as the shell. Pick its albedo so the key-lit side measures #E0956A, so the hex holds where the light falls instead of through an unlit material.",
      "encoding_reads": true,
      "dominant_subject_finished": false,
      "feed_legible": true,
      "inputs": {
        "slides/slide-01.html": "d549d868d2e0872c00fe4c3f9e7706be7886c65415d88b57507c59aa79001c59",
        "render/slide-01.png": "a58cc51b7107a9bfdc6d5d31de3f28a56acd98141fe07f6133c487c67791f6f5",
        "assets/js/deck/2026-10-26-tether.js": "95951eb7cde825a17599e30c30c1dd24fca21ef919ef15a2077626b41388781b",
        "assets/js/noise.js": "ae48620fda646edad7262f62e8c7b394d971103327e75d405a113bd4ef4ebeaa",
        "assets/js/three.module.min.js": "08fd7545d13d2c7fb65ab691530a802dafefd638596501854f267d0fb13c39e7",
        "assets/js/txcolor.js": "0da3f0e2bc0fc005bd501806550590ad711be135d5c371012fee6af0048fb01c",
        "assets/js/txdeck.js": "8cc8c4aecdb329a0e2c31530fe94ed42b5691c638160f318d72f2ca69e4d8380",
        "assets/js/txkit.js": "f1d05898dd31b3cea5a127fd114e438f6b55ac0c962241a5c79eedcf7866cd64",
        "assets/js/txlayout.js": "a31072fd1ed965a34ad16d80007633a1055fe92897c1c8f6c870a1c33348d04e",
        "assets/js/txpost.js": "e46fc8aa813b870b7eaba8b152079b8b902081718369e612eac7fdd22cd816f0",
        "assets/js/txthree.js": "731e164ca252500792cc508af0c16c0c06d4c7261e4a89064de2367bf875aac0",
        "assets/js/txtype.js": "b1dfe1eb2e283498b839301766453c3693add52601bb99db0f36412f3f4bc3de"
      }
    },
    {
      "slide": 4,
      "role": "evidence",
      "subject": "a ring laid on the ground around a lit hub, with a lit radius to its near arc, enclosing a town of glowing street-lamp grids crossed by an Interstate 35 lamp line, seen obliquely from 1,200 m at night",
      "visual_consequence": "With the headline and labels covered, the frame reads as one reach from a single point that takes in a whole gridded town. Lamps are dense inside the near arc and the land outside goes dark. The ring now holds a visible line at the far arc, so at feed size it reads as one closed measured circle, with the street blocks as its ruler.",
      "weakness": "The ring and town are finished, and the far arc now holds about 12 px at native size (r2c1, r2c2 at y 715 to 760). Two smaller defects remain at native size. Many glow sprites leave small dark grey square halos that notch the lit street lines where their quads overlap (r3c2 at x 110, y 222; x 540, y 330; x 630, y 495; and along the streets in r3c1), an alpha-blending artifact. The lens-shaped dark patch inside the ring behind and right of the hub is still there (r2c2 at x 380 to 1080, y 760 to 820). Neither changes the reading at 432 px.",
      "repair": "Render the lamp sprites additive with depthWrite off, so their quads stop leaving dark squares on the streets.",
      "encoding_reads": true,
      "dominant_subject_finished": true,
      "feed_legible": true,
      "inputs": {
        "assets/js/deck/2026-10-26-tether.js": "95951eb7cde825a17599e30c30c1dd24fca21ef919ef15a2077626b41388781b",
        "assets/js/noise.js": "ae48620fda646edad7262f62e8c7b394d971103327e75d405a113bd4ef4ebeaa",
        "assets/js/three.module.min.js": "08fd7545d13d2c7fb65ab691530a802dafefd638596501854f267d0fb13c39e7",
        "assets/js/txcolor.js": "0da3f0e2bc0fc005bd501806550590ad711be135d5c371012fee6af0048fb01c",
        "assets/js/txdeck.js": "8cc8c4aecdb329a0e2c31530fe94ed42b5691c638160f318d72f2ca69e4d8380",
        "assets/js/txkit.js": "f1d05898dd31b3cea5a127fd114e438f6b55ac0c962241a5c79eedcf7866cd64",
        "assets/js/txlayout.js": "a31072fd1ed965a34ad16d80007633a1055fe92897c1c8f6c870a1c33348d04e",
        "assets/js/txpost.js": "e46fc8aa813b870b7eaba8b152079b8b902081718369e612eac7fdd22cd816f0",
        "assets/js/txthree.js": "731e164ca252500792cc508af0c16c0c06d4c7261e4a89064de2367bf875aac0",
        "assets/js/txtype.js": "b1dfe1eb2e283498b839301766453c3693add52601bb99db0f36412f3f4bc3de",
        "slides/slide-04.html": "692000b73c0aed634de9ea3fd5c4b0a553548974508d562a50000e4434f3ce2a",
        "render/slide-04.png": "1f1647bfff9cfd1b234de23fd559d6781e8ade4d201d4f33294543e6ec03efcd"
      }
    },
    {
      "slide": 9,
      "role": "close",
      "subject": "four pine survey stakes with pink flagging and a sagging string line closing an empty rectangle on asphalt in one warm pool, under an empty night sky",
      "visual_consequence": "With the headline covered, the four stakes and the closed cord still read as a site laid out and not built, with nothing in the sky above it. The new crack network now competes with that reading.",
      "weakness": "The new crack sealant is a regression in material and scale. The strokes are smooth meandering bands 25 to 40 px wide at native size, of even width, branching and rejoining across the whole pad (r3c2 at x 200 to 700, y 270 to 900; r3c1 at x 400 to 1080, y 80 to 400). On a 12 by 9 m pad at this camera, that makes them about 20 to 30 cm wide. They read as tree roots or a river map, not as tar-sealed cracks, and at feed size they are the strongest marks on the ground, pulling the eye off the stakes. They are flat albedo with no tar sheen or relief, and one runs alongside the near stake's long cast so that the shadow is hard to separate (r3c1 at x 580 to 860, y 700 to 780). The cut patches read correctly as darker rectangles (r3c1 at x 0 to 720, y 230 to 500). The oil stains do not register. The empty middle quarter is deliberate and recorded in the dossier, and it reads as the empty sky.",
      "repair": "Redraw the crack sealant at true scale. Use a few sparse, angular, mostly straight hairlines about 8 to 10 px wide at native size, following the patch edges and transverse to the lot. Give them a slight tar gloss in roughness rather than heavy black albedo.",
      "encoding_reads": true,
      "dominant_subject_finished": false,
      "feed_legible": true,
      "inputs": {
        "assets/js/deck/2026-10-26-tether.js": "95951eb7cde825a17599e30c30c1dd24fca21ef919ef15a2077626b41388781b",
        "assets/js/noise.js": "ae48620fda646edad7262f62e8c7b394d971103327e75d405a113bd4ef4ebeaa",
        "assets/js/three.module.min.js": "08fd7545d13d2c7fb65ab691530a802dafefd638596501854f267d0fb13c39e7",
        "assets/js/txcolor.js": "0da3f0e2bc0fc005bd501806550590ad711be135d5c371012fee6af0048fb01c",
        "assets/js/txdeck.js": "8cc8c4aecdb329a0e2c31530fe94ed42b5691c638160f318d72f2ca69e4d8380",
        "assets/js/txkit.js": "f1d05898dd31b3cea5a127fd114e438f6b55ac0c962241a5c79eedcf7866cd64",
        "assets/js/txlayout.js": "a31072fd1ed965a34ad16d80007633a1055fe92897c1c8f6c870a1c33348d04e",
        "assets/js/txpost.js": "e46fc8aa813b870b7eaba8b152079b8b902081718369e612eac7fdd22cd816f0",
        "assets/js/txthree.js": "731e164ca252500792cc508af0c16c0c06d4c7261e4a89064de2367bf875aac0",
        "assets/js/txtype.js": "b1dfe1eb2e283498b839301766453c3693add52601bb99db0f36412f3f4bc3de",
        "slides/slide-09.html": "f6e46532be2427bc8a503960228bea28606c44cce44dc7f0d21be17c81a4adea",
        "render/slide-09.png": "1794cfb33f26806ca2ae0164ca60af4b1f3f11ac1e398f35fdd99555d5bd569b"
      }
    }
  ]
}