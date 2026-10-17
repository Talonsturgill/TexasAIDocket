# Run record, October 17th, 2026

Carousel no. 53, MD Anderson's SPACER, an AI model that reads gene activity mapped across intact
tumor tissue to infer why T cells gather in some regions and avoid others, and whose leading finding
is that mucin may form a physical barrier keeping T cells away. Docket item tx-2026-0217, admitted
this run. The first deck under `prompts/carousel_studio.md`, and the first whose every frame is a
material relief through `txbench.js` rather than a staged spatial scene.

Effort at wake: `high`, as the repo's settings carry it.

## The record, first

- **Worklist.** `docket_staleness.py` named 29 items due, none rotten. 24 sit behind a measured crawl
  boundary (re-measured October 15th, five days left on that measurement) and are named UNREACHABLE
  by the selector, not counted as rot.
- **Re-verify** (commit 08c21a2e). `reverify.py --apply` stamped three items whose every claim came
  back unchanged (tx-2026-0118, tx-2026-0182, tx-2026-0212), and their tool-written notes were
  re-worded. Six more were checked by hand against the sources that answered and stamped with their
  own movement lines: tx-2026-0062 (Community Impact), tx-2026-0078 and tx-2026-0079 (the House
  committee meeting archives), tx-2026-0126 (the Senate committee meeting archive), tx-2026-0138
  (Texas Public Radio) and tx-2026-0179 (the city's own finance committee briefing and FOX 4). Each
  names what stays unconfirmed. `reverify.py --check-notes` exits 0.
- **Unreachable this run, and not stamped.** 403 from wilcotx.gov, keranews.org, brazoscountytx.gov,
  dhs.gov, brownsvilletx.gov, mylubbock.us, hayscountytx.gov, leandertx.gov and globenewswire.com,
  and 24 urls the crawl boundary refused before any request.
- **Admitted.** tx-2026-0217 (commit 79ed5e6f), MD Anderson's October 13th release, eleven claims,
  all primary, Harris County.
- **Discover.** Six scouts ran (ai-in-the-field, clinic-and-classroom, research-and-machines,
  what-texas-makes, power-and-compute, community-signal). The Federal Register API returned no open
  Texas AI comment window beyond the CFTC compute derivatives request the record already carries
  (tx-2026-0118, closing October 20th). Leads held for a later run, each needing its primary
  document: Plano's city council approval of a citywide AI initiative (October 12th, news reports
  only), the PUC's suit against the Attorney General's open records rulings on its data center
  survey (Texas Tribune, October 6th), USDA's AI-assisted screwworm drone flights over Texas (KRGV,
  October 12th), Fermi America's AMD credit support agreement at Project Matador in Carson County
  (company release, October 13th), Mesquite and La Joya ISDs' AI drafting of special education
  plans (trade press, October 13th) and UT Health San Antonio's dementia model fairness study
  (October 12th release).
- **Backlog.** The temp-dir build printed no `backlog:` lines, so the list held at zero.

## Instruments

Phase 7 ran every page check and every discoverability self-test, and all exited 0. The scanner's
daily ceiling was not read: this run holds no Cloudflare D1 access and no reading of the live
Worker's `DAILY_CAP`, so both values are unknown rather than healthy.

## Craft refresh

Not run as searches. The scouts spent the session's whole web search budget before Phase 1's
queries ran, so the refresh was the studio material instead: `examples/studio-proof/`, the
`txbench.js` source and `examples/art-direction-proof/`.

## Why this story and not the others

SPACER is AI in use at the bench rather than a decision about AI, it has a primary source on the
institution's own site and a peer reviewed abstract behind it, it is in Houston, and it carries a
physical claim, a sugar coat that may wall T cells off, that a material relief can draw directly.
`dedupe_check.py --item tx-2026-0217` exited 0 and the item clears the thirty day rule against all
26 decks in the window. Its host, mdanderson.org, is new to the window's instruments. Its beat,
research-and-science, carried 2 of the 26.

Refused, and why. Kodiak and Charger's Dallas to Laredo lane is tx-2026-0209 already and shares a
company and a city with no. 41 inside the window. Tesla's Cybercab count in Austin rests on a Tesla
post relayed by a fan site, the day after no. 52's robotaxi deck. The USDA screwworm drones rest on
one TV station's account. Fermi's AMD agreement is a company release on a site the record already
carries three items about. The UT System's Abridge agreement is tx-2026-0210. TEA's rescoring
requests are no. 38's subject.

`texan_check` at selection read places Houston, no public body, no deadline and no next step. A
research result has no comment window, so the deck carries its score on the art and on a close that
says plainly what the finding is not yet.

## The directors room

Three treatment directors pitched THE MEASURED EVIDENCE FIELD (one slide world under a darkfield key
at seven scales), ADDRESSES AND A WALL (the release's own postal comparison, a copper route stopping
at a mucin rampart) and WHAT A TEXAN HOLDS (a glass slide the size of a finger, down to the wall and
back up to the bench). The synthesis kept the first's spine and world, the second's wall and funders
and the third's 2 by 2 and its honest close, and refused the postal route (SPACER infers signals and
tracks no cell's route, so a drawn route overclaims), every txthree frame and every new kit model (a
microscope, a quarter, a gloved hand). `storyboard.md` carries the reasons. The deck is all nine
frames as material reliefs through `txbench.js`, the first under the studio route.

## The audition, and what it cost

The art director reviewed the cover, frame 7 (the wall, the hardest) and the close three times.

- **First reading, revise.** The coat and the wall split into two flat tones with a ragged
  boundary and speckled highlights, the wall cast nothing on the tumor, and the close was flat
  rectangles: a matte card for glass, a grey slab of stage, a beige disc for the light.
- **Second reading, revise.** The cover passed. Frame 7 carried screen aligned stripes and no
  crest highlight, and frame 9's light still read as a ceramic plate. The one repair rule applied,
  so the representation changed. Test renders with the cast off and then the specular off proved
  the stripes were geometry: the wall's centre line and the nest's outline wobbled on a three octave
  noise whose upper octaves changed their slope every 60 to 120 px. Both now follow smooth sums of
  sines. The close became darkfield: the aperture stays black, and light shows only as a thin ring
  at its rim and a lit rim on the section's outline.
- **Third reading, accept**, with polish items for the pixel pass: vary the coat's width, put a
  tighter highlight on the wall's crest, shade the engraved funder lines as cavities.

The relief engine has no transparency, no second specular lobe and no emissive term, and the
close's light from below is a screened stroke laid over the render after `TXBENCH.relief`. Queued.
