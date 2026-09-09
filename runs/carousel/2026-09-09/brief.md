# The story, 2026-09-09. Carousel no. 18.

**Docket item tx-2026-0129**, admitted to the record today.

A quality improvement study published in JAMA Network Open on September 3rd, 2026 compared two
ways of answering one question at Houston Methodist Hospital. When will this patient go home?

One answer came from a commercial AI tool wired into the hospital's electronic health record.
The other came from the hospital's own case managers, working normally. Both were compared
against the date the patient actually left, at three points in the stay. Admission, forty eight
hours before discharge, and twenty four hours before discharge.

At admission the two were close on error, and the case managers were already hitting the exact
date more often. By the last day the case managers had pulled away hard.

**The authors are the ones who put the knife in their own result**, and that is the reason this
is worth a deck. They write that the case managers' estimates were part of usual care and
visible to the care teams, so they may be partly self fulfilling, while the AI's estimates sat
in the record without being switched on automatically. The humans were being read; the machine
was not. They also write that the strong correlation at admission should not be read as evidence
the tool captured what clinicians know across the stay.

## The verified claims

Every string on every frame comes from `out/2026-09-09/claims.json`. Read it. The ones that
carry the story:

- **c2** the last-day comparison, within one day
- **c4** the admission comparison, and READ ITS NOTE. In every pair the FIRST figure is the case
  managers and the second is the AI. A frame that reverses them reverses the story.
- **c3** mean absolute error at both later points, with the confidence intervals
- **c5** what produced the AI dates, and the only description the paper gives of the tool
- **c6** the study's own statement of what it found, and when the answer is used
- **c7** the warning against reading the admission result as understanding
- **c8** THE COUNTER-IMAGE. The limitation the authors raise against themselves
- **c9** what they say has to happen before anyone concludes the tool is worth running
- **c10** the encounter counts, medium confidence, no arithmetic across them
- **c11** no baseline patient demographics at all
- **c12** the SQUIRE reporting guideline
- **c14** the publication date

Nothing about a vendor. The paper never names one and the fact-checker REFUSED to certify that
absence, because a negative needs a document. What is certified is c5, which is the only
description the paper gives. Say what c5 says. Do not say no vendor is named.

## What the gates already know about this story

`texan_check` at selection: **places Harris County and Houston, names no deciding body, and has
NO NEXT STEP.** A story with no next step is capped by that gate. The closing frame has to carry
one and it is the cheapest frame in the deck to get right. The study names its own next step at
c9, which is a prospective outcome based evaluation, and the study itself is open access and a
reader can go and read it.

`dedupe_check`: nothing close in seventeen entries over the thirty day window. `health-and-education`
is two of the last seventeen decks.

## THE VARIETY INSTRUCTION, and it is not a suggestion

Carousel no. 17 scored **6.0 on variety** against a 6.8 bar while every other criterion sat at
7.0 or better. It did not lose marks on craft. It lost them on being the fifth of its kind.
Read the `register` field on the last five entries of `ledger/carousel/artwork.json` in a column:
a desk under one grazing key, a light table seen from above, the inside of an optical instrument
after dark, an assay bench in a dark room, a machine hall lit from below. **Five consecutive
decks are an interior, at night or in a windowless room, lit by one artificial source.** Every
one was a different drawing, which is why the technique exclusions kept passing. Register is what
a reader carries away from a strip, and a reader following this account for a week saw five dark
rooms.

So:

1. **TODAY'S REGISTER IS OUTDOORS, IN DAYLIGHT, WITH THE SUN AS THE SOURCE.** Not a room, not a
   ward, not a bench, not a bay. A place in Texas a person could stand in, at an hour the light
   is doing something. The subject is a hospital and the frame that carries it is still outdoors.
   This is not as much of a stretch as it sounds. The whole story is about the day somebody goes
   home, and that day happens outside.
2. **The palette comes off the ground, not off the hardware.** Four of the last five drew their
   palettes from manufactured surfaces. Name a Harris County soil, a Gulf coastal prairie
   vegetation community, a Houston sky, a bayou, the coastal plain. Name the source in the
   dossier.
3. **The value arc inverts the other way.** Those five were dark decks with a light turn. A light
   deck with one dark turn is a different memory.

Technique exclusions from the last six decks are in `out/2026-09-09/tmp/tech_exclusions.txt`.
Read it. Nothing on it may be reached for again.

## Craft memory the machine has earned

- Make every count on a frame name the set it counted, and make that set one the deck read.
- After answering a composition gate, re-read the frame for what the new furniture now asserts.
- Write every acceptance item so that rendering NOTHING fails it, not just so that rendering too
  much fails it.
- Any position or length a reader could measure goes through a computation, not just the ones
  that carry a printed number.
- A declared focal is an AREA carrying one extreme of the frame's value range. Never a line.
