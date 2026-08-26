# Round 5 recut — the plan, written before the code

`.claude/WORKLOG.md` is the `human` lane, so this lives in the run record, which is `daily`.

## Why

Round 5's integrity judge returned 6.02 with two hard fails and is right on both.

1. **The headline count is not a count.** `RESTRICTED` and `DECLINED` in `compute.py` are maps
   TYPED BY HAND. The record holds 34 items whose title or summary names data centers and that
   carry a 2026 date, and at least three of them meet the rule the deck publishes, sit inside
   the deck's own window, and are on no frame: `tx-2026-0033` El Paso (Data Center Policy
   Framework, Special Permit for hyperscale, local incentives eliminated), `tx-2026-0061` San
   Marcos (voted 4 to 3 to make data centers ineligible citywide), `tx-2026-0028` Hays County
   (180 day emergency water review).
2. **"Seven bodies, seven instruments. One each." is false.** San Angelo reached for three in
   2026: zoning as conditional use only on May 19th, sewer discharge rules on June 2nd, the
   water cap on June 16th. The distinctness the cover claims is a property of picking one
   action per body, not a finding about the record.

Round 4 replaced a rule that was too narrow with one too broad and left the hand map alone, so
the sentence describing the set is still wrong, now in the other direction. Three rounds, three
wrong headlines, one cause.

## The fix, which is the judge's own one sentence fix

**The set becomes a SELECTION COMPUTED OVER EVERY ITEM IN `ledger/docket.json`, and the code
refuses to run if any candidate is unclassified.** The editorial judgement stays, because
whether a TCEQ permit step is aimed at a data center is a judgement, but it becomes EXHAUSTIVE:
every candidate is classified IN with a shape or OUT with a stated reason, and an assertion
fails the build on any candidate that is neither. A silent omission stops being possible, which
is the actual defect.

## The scope the rule states

A **Texas LOCAL government** (city council, commissioners court, planning commission) that, on a
dated 2026 ORDER in this record, decided something about data center development **in its own
jurisdiction**. State agencies, the Legislature and letters asking another government are OUT,
each by a stated reason rather than by omission.

## What that changes, and it is a better deck

The deck stops claiming seven bodies each reaching once. It says what the record says: a Texas
local government took a data center up sixteen times in 2026, fourteen of those were actions,
**San Angelo went back three times**, Brazoria twice, and one of the fourteen was an approval.
The thesis is unchanged and better supported. The shape of the instrument still decides whether
anything stops.

## Waves

| # | wave | state |
|---|---|---|
| A | `select.py`, exhaustive selection + unclassified assertion | DOING |
| B | Claims for every newly included body, live fetch, verbatim | TODO |
| C | Recut frames 1, 2, 3, 5, 6, 8 content. The art survives | TODO |
| D | Re-render, every gate green by exit code, re-measure | TODO |
| E | Panel round 6 | TODO |
| F | Ship, or fail honestly and say so in the email | TODO |

## Craft findings from round 5, all verified real, all in wave C

- **Frame 2's declared central device did not render.** Its dossier's technique is one hard
  diagonal occlusion shadow whose job is "what stops seven stacked lines reading as a table",
  with "the later rows crossed". What draws is a soft patch in the sheet's upper RIGHT over the
  greeked column only, crossing not one instrument name. My own round 3 fix caused it: routing
  the edge past the right corner to stop it banding across the headline removed its purpose.
- **Frame 6's cork is still flat at 432px.** The 2px speckle is right at 2160 and gone at feed
  scale, which is where round 4's complaint was. Needs low frequency mottle that survives the
  downscale, not the blocky mosaic that failed before.
- **Frame 8's dossier still says "the deck's quietest ... between its two loudest."** Claimed
  repaired, never touched. Measured 55.6 against neighbours 52.4 and 48.8.
- **`RUN_RECORD` line 80 still prints the falloff as 12.2 L\*** and a median of 54.7, against
  `measurements.json` 16.5 and 52.4. Its gate table says 31 claims and 14 aggregates against 34
  and 17.
- **`artwork.json` commits one quantity twice**: `camera` names five frames, `avoid_next` says
  four, in the entry whose own note explains that everything in it is composed from one source.
- **`aggregates.json`'s "Four applications" still says `value_from: c11` and "NOT counted"**,
  now the opposite of what `compute.py` does. Both integrity and reader named it.
- **Frame 6 closes the quote at "per square foot"**, dropping "of Gross Building Area", so the
  cap ships with no denominator.
- **Frame 3's art denies its own dek.** "The last three came inside 21 days of each other" over
  seven evenly spaced rows, so a 48 day gap reads identically to a 1 day gap.
