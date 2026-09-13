# Repair round 2, held until the three scorers report

The flow critic returned while the panel was still reading the same renders. Changing a frame
under a judge produces a report about a deck that no longer exists, so these are written down and
applied in ONE round once all three score cards are in, together with whatever the panel finds.

## MEASURED AND CONFIRMED BEFORE THE ROUND

**Frame 7's hand has been on the FLOOR the whole time, and that is why the turn's accent marks
nothing.** `S.sprite` stands a sprite ON THE GROUND PLANE at its depth, and the hand's parts were
declared from y 0.00. Solved against the frame's own camera (horizon 690, f 900, eye 1.48):

    the sheet, Y 0.74 at Z 2.86 to 2.36   y 923 to 972, x 439 to 641
    the hand as built, Y 0.00 to 0.09     y 1186 to 1219      250 px BELOW the sheet
    the hand at the desk top, Y 0.74      y  922 to  954      on it

That blob at the bottom of the frame the pixel critic could not name and read as "a boot or a
small animal" is the hand. Two critics found the same defect from two directions and neither could
see the cause, because a sprite standing on the floor is a correct call to a correct function.

**THE FIX IS TO DECLARE THE HAND'S PARTS AT DESK HEIGHT**, y 0.74 to 0.83, not to move the sheet.

## THE REST OF THE ROUND

- **Frame 7.** Delete the unnamed shapes in the lower half once the hand is off the floor, and
  give the desk a visible top plane and near edge. The archetype stays OBJECT_AND_CAPTION rather
  than becoming CLOSE_CROP, because CLOSE_CROP is already spent on frame 4 and the rotation rule
  allows no archetype twice; the flow critic's suggestion costs frame 4 its page.
- **Frame 9.** The hot mix carries no surface at all. Removing the nine transverse bands fixed the
  railroad read and left the road as page colour over a third of the frame. Put aggregate on it,
  not bands. Check the mono foot against the near centre-line dash.
- **Frame 4.** One small tilted hatched rectangle floats in the section band left of the trough,
  unlabelled, the only diagonal hatch on a stipple frame. Find it and delete it.
- **Frame 1.** The clipboard reads as a dark plate beside the hand rather than held in it.
- **Frames 4 and 5 are interchangeable**, which is the deck's one soft joint. Recorded for the
  next run rather than fixed here: making one answer a question the other raised is a planning
  change, not a repair, and the round rule says a round spent on a plan is a round the plan should
  have spent on itself.

## WHAT THE FLOW CRITIC CORRECTED IN THE BRIEF

The brief said frame 6 measures 29. `measurements.json` says 14.9. The per-frame MEDIAN is not
this deck's value rhythm at all, because on any inked frame in this register the median is the
page colour and seven frames sit pinned at 6.1. The rhythm is in p95 and in coverage, and the
critic judged it there. That correction belongs in the artwork ledger's value block.

## THE PANEL'S FIRST TWO CARDS, and what they converge on

    reader  6.70   no hard fails   ship false
    craft   6.77   no hard fails   ship false     threshold 6.8

Three readers, the flow critic included, independently named THE SAME DEFECT as the deck's
worst: frame 7's granite is not under a hand. The cause is measured above. That alone is worth
more than the rest of this list, because it is the frame the whole structure is staked on.

What the two cards converge on beyond it:

- **FIVE FRAMES HAVE NO REAL LIGHT.** p95 is 59.7 on frame 3, 51.4 on 4, 55.9 on 5, 43.0 on 7
  and 60.9 on 9, while the hook ink prints at L* 86. On those five the brightest object on the
  page is the TYPE. Frame 4's own dossier calls its lit lip at #EFEFEF the craft point of the
  frame and the frame's ceiling is 51.4, so the lip never printed.
- **THE FOLD NEVER MOVES.** Seven of nine frames open kicker, two line serif hook, dek, all on
  flat page, with the art starting between y 480 and y 600. The layouts rotate BELOW the fold and
  the fold itself is the one skeleton the illustration system was written to kill.
- **A READER TAKES AWAY THAT HAND RATING IS ALREADY REPLACED.** Frame 1's past tense plus the
  caption's "now reads that damage at pixel level" lands there, and nothing on any frame carries
  c1's own "in its second phase, closer to statewide deployment" or the not_established line that
  no district has adopted it on a live inventory run. The deck knows the fact that governs its
  reader's takeaway and prints it nowhere. This is the single most valuable finding in either card.
- **THE FIRST COMMENT CALLS THE JOURNAL PAPERS THE OFFICIAL RECORDS.** `sources_block.py` writes
  "three first party accounts and two official records", and the official records here are the
  agency dashboard and the commission calendar. Upgrade lane.
- Frame 2's kicker sits on the desk's line screen, twice flagged by machine_qa.
- Frame 6 sets the four words with near zero word space and line one's cast lands on line two.
- Frame 9's road carries no surface at all and the mono foot crosses a near centre-line dash.

## WHAT A JUDGE FOUND THAT DID NOT SURVIVE CHECKING

**The reader judge said the first comment "inverts what a reader means by official", calling the
two journal papers the official records and the agency pages the first party accounts.** Checked
against `claims.json`, the classification is the other way round and it is correct:

    primary_corporate   news.txst.edu, www.ebi.ac.uk, api.crossref.org      the subject wrote it
    primary_official    www.txdot.gov, www.fhwa.dot.gov                     the agency's own record

So "three first party accounts and two official records" names the university release and the two
papers as first party, which is what they are, and the TxDOT and FHWA pages as official records,
which is what they are. `sources_block.py`'s own docstring records that this sentence has said its
exact opposite twice before, and the fix each time was to make the noun mean the document's SUBJECT
WROTE IT rather than the filer's legal form. The judge read the counts onto the wrong classes.

Nothing was changed. Recorded because an agent's finding is not a fact, and the one that survives
checking and the one that does not have to be told apart every time.

**What the same finding DID turn up.** The Europe PMC line was titled "Funding statement, Detection
of Flexible Pavement Surface Cracks...", because c14's `source_title` named the SECTION its quote
comes from. Four claims come off that url and three are from the body. The title is the paper now
and the section is in c14's note, which is where it belonged.
