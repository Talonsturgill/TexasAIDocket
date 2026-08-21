# Run record, August 21st, 2026

## The finding that needs a human first

**Thirty nine of the fifty eight county pages tell a reader the county is outside every
metropolitan area, and all thirty nine are inside one.**

`site_build` prints two sentences directly under the `<h1>` on every `/place/county-*/` page:

    Outside every metropolitan and micropolitan area. N items in the record.
    This county is in no federal statistical area, which is true of 121 of the state's 254.
    It gets its own page for that reason.

It prints them unconditionally. Harris County is the principal county of
Houston-Pasadena-The Woodlands and its page says it belongs to no area. So do Bexar, Travis,
Bell, El Paso, Cameron, Ector and thirty two more. The metro page one link away names those
counties in its own list, so the site contradicts itself across a single click.

The `121 of 254` figure is computed and correct. What is wrong is that the sentence is printed
for every county rather than only for a county `places.metro_of` puts in no area, which is the
test the page's own second sentence describes.

Nine gates ran green over this build, including `schema_check` linting 1,694 generated
sentences and `seo_check` across 241 pages. None of them asks whether a computed sentence is
TRUE of the page it is on, which is the whole of `GATE_LESSONS.md`.

**This run may not fix it.** `scripts/site/site_build.py` is `human` owned in `ownership.yaml`,
and the daily routine's only carve out under `scripts/site/` is the grid watch and water watch
page builders, named one by one. Proposal below.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0082.png`, the run's newest
  item, opened and read. The headline wraps after "Epic", after "into" and after "and", all
  places a reader would break it, and it ends on the whole word "advanced" followed by an
  ellipsis rather than on a stump. The apostrophe in "Microsoft's" renders straight. Clean.
- **`/questions/`, read as a reader.** Twelve shapes, all of them questions somebody would
  type. Counts read 69, 69, 64, 05, 67, 69, 68, 68, 69, 69, 69, 69 against 69 items, and each
  gap is explained by the record rather than by the shape breaking. "How the public can take
  part" is 64 because five items are in a closed room. "Where in Texas each one applies" is 67
  because two items still carry no place, and it was 66 before this run set tx-2026-0007 to
  statewide. No new room or status this run made a shape stop making sense.
- **The `Open right now` section of `llms.txt`.** Nine entries, cross checked against every
  window Phase 3 re-verified. tx-2026-0077 is listed with its August 25th door, the three
  dockets on today's PUCT open meeting are listed, and tx-2026-0034 correctly dropped off
  because its August 18th meeting has happened and the run moved it to a closed room. No
  closed window is still advertised as live.
- **`/sources/`, the record's own report card.** The share reads **242 of 314 claims rest on a
  primary document, across 124 documents from 58 publishers**. It went UP this run. Every one
  of the 31 claims added today is primary, 13 in re-verification and 18 in admission, so the
  share moved from 211 of 283 to 242 of 314. The top publisher is `webapi.legistar.com` at 29
  claims across 10 entries, and its page reads as documents: city and county event items,
  matter records and action histories, which is the clerk's own record rather than a report
  about it. Nobody would object to it sitting first. The quoted material exemption is still
  scoped to quotes and is not hiding any of our own sentences.
- **`/topic/`, counting one card against its own page.** The research and science card says 5
  decisions and the beat page lists exactly 5, including both NSF awards admitted today. The
  eight per beat figures sum to 69, which is what the front page counter prints. The
  `still open to comment` figure is 4 across the beats while `/questions/` counts 5 items in an
  `open_comment` room, and that difference is correct rather than a defect: tx-2026-0001's
  window closed on August 11th, so it is a room the record recorded and not a door open today.
  That is `GATE_LESSONS.md` entry 44 being honoured rather than repeated.
- **`/place/`, for the places this run landed something in.** Waller, Travis and Galveston are
  all on the hub with counts of 1, 4 and 2, and each county page lists exactly that many items.
  The Houston-Pasadena-The Woodlands metro page carries 9 items, names the five counties in the
  record (Galveston, Harris, Brazoria, Montgomery, Waller) and names the five it has found
  nothing in (Austin, Chambers, Fort Bend, Liberty, San Jacinto), so an untouched county is
  still named. Both items admitted into that metro today appear on it. **The county pages
  themselves carry the defect at the top of this record.**

## The instruments

Every check exit 0. No 2 and no 3, so nothing is reading wrong and nothing has stopped.

    gridwatch_pagecheck        0    current, and holding its promises
    waterwatch_pagecheck       0    current, and holding its promises
    waterwatch_page --self-test 0
    media_check                0    every reference in docs resolves
    schema_check               0    1,013 nodes across 242 pages
    og --self-test             0
    favicon --self-test        0
    truetype --self-test       0
    indexnow --self-test       0
    seo_check                  0    clean across 241 pages

**The water map draws 119 circles and the day's record holds 119 reservoirs.** Counted from the
rendered markup against `reservoir_count` in `waterwatch.json`. The drawing is not one lake
short. None of the four removed blocks has come back.

**The front page counter row prints five of six candidates and `Sources cited` is one of them,
at 314.** The weather chip rotated to nights over 80, leads with Dallas Fort Worth, and prints
the measured value and the normal without publishing the comparison that chose it.

**The scanner's daily ceiling could not be read.** There is no Supabase connector in this
environment, so `scanner.scans` and `scanner.config` were not queried and the day's scan count,
the cap and any failures are unknown. Per the routine this never blocks a run, and it is
recorded rather than skipped. A requester who hit the cap today would not have been noticed.

## The record

**Worklist: 16 due, 16 re-verified, nothing deferred, nothing rotten.** The staleness gate now
reports zero due. Two items were wrong and both were wrong in the same way, which is the
finding underneath the numbers.

**tx-2026-0034, El Paso.** The council approved and adopted the letter to the Governor on
August 18th as agenda item 34, on a motion by one member and a second by another, and the
record had it as pending. Legistar leaves `MatterStatusName` at `Agenda Ready` and
`MatterPassedDate` at null after a vote, and records the outcome on the event item and in the
matter's action history instead. The previous check read the matter alone and recorded the item
unchanged, correctly reporting what it read.

**tx-2026-0037, Laredo.** Dated to August 5th, which is the day the reporting published, not
the day the council met. The meeting was July 27th. The city's own record files the direction
to write rules as a council item on high intensity data processing facilities, records
`no action taken` on it at the June 15th and July 27th meetings, and put it back on the
August 3rd agenda where it again records no action. Both sources the item rested on were
journalism, and one of them is on a host that now disallows this project by name.

**tx-2026-0032, Killeen.** The hearing date was a reported approximation carrying its own
caveat. It is now confirmed from the commission's own agenda: April 27th, 2026, public hearing
PH-1, Case Z26-07, a conditional use permit on land zoned University District at 6509 South
Fort Hood Street, applied for by Belton Engineering, Inc. on behalf of 4 Lazy J Properties, LLC.
No Killeen agenda posted through August 27th carries the case, so the council decision the
commission's vote feeds into has not been scheduled.

**tx-2026-0007** is a Texas statute binding a statewide agency, so it is now stored statewide,
which is how every other statute in this record is stored. That is one of the three geography
backlog entries answered in the data.

**Admitted, five, each on a primary document fetched this run.** House State Affairs on
August 19th on data centers and on the 765 kV lines, both charges in full. House Public Health
on August 20th on artificial intelligence use in health care. NSF to Prairie View A and M on
August 11th and to UT Austin on August 13th. UTMB moving Epic into Azure on August 13th.

**Held, one, and the reason is the record's own vocabulary rather than the sourcing.** Waymo
opened its Houston driverless service to anyone with the app on August 20th. The company's own
post carries every claim verbatim. See the proposals.

**Backlog: three at wake, three at ship.** It did not grow. One of the three is fixed in the
data and still prints, for the reason in the proposals.

## Proposals, all outside this run's lane

1. **Fix the county page metro sentence.** `scripts/site/site_build.py`, `human` owned. Print
   "Outside every metropolitan and micropolitan area" only when `places.metro_of(county)`
   returns nothing, and otherwise name the area the county is in and link it. Thirty nine of
   fifty eight pages are wrong today. Add the case to the builder's self test so it can go red:
   assert that a Harris County page does not contain that sentence and that a Loving County
   page does.
2. **The backlog roster is a static list, so a cleared entry never leaves it.**
   `docket_build.backlog()` prints every id in `GEOGRAPHY_BACKLOG` whether or not the item
   still needs the exemption. tx-2026-0007 was given a real statewide scope this run and still
   prints as outstanding. A ratchet that cannot shrink is a list, not a ratchet. Report an
   entry only while `_geography_problems` would still fire on it without it.
3. **The record has no beat for AI in the field and no decider type for a company.**
   `docket_build.TOPICS` carries eight beats and six are policy or infrastructure, which is
   exactly the drift `knowledge/shared/APPLICATIONS.md` was written to correct.
   `docket_build.DECIDER_TYPES` carries nine types and every one is a unit of government.
   Between them the record can hold a decision ABOUT a deployment and not a decision BY the
   deployer, on a site whose editorial doctrine says the default story is somebody using a
   tool. The Waymo item is held on both counts and is sitting in the seed ready to promote.
   This is a three file change: `TOPICS`, `DECIDER_TYPES` and `site_build.TOPIC_BLURBS`, and
   `site_build` refuses to build if the blurb is missing, which is the right behaviour.
4. **`gov.texas.gov` needs a registry row saying it is off limits.** It now serves
   `User-agent: ClaudeBot / Disallow: /`. The registry row says it serves no robots.txt at all.
   `knowledge/shared/SOURCES_REGISTRY.md` is `human` owned. Field log entry is filed.
5. **`capitol.texas.gov/TLODOCS/` needs the same, and yesterday's field log recommends it.**
   The August 20th entry calls those hearing notices the cheapest primary source in the repo on
   the strength of a 200, and the robots file disallows the directory. The live path is
   lowercase and the disallow is uppercase, and the owner should decide on purpose whether that
   is permission. This run treated it as a disallow. `/Committees/` is not disallowed and
   covers everything except the charge text, which `lrl.texas.gov` carries in full.

6. **`aggregate_check.to_int` cannot parse a thousands separator, so no quoted figure at or
   above 1,000 can ever be declared through `quoted_from`.** `NUM` matches `1,400` correctly.
   `to_int` then does `t.isdigit()`, which is False for a string carrying a comma, and returns
   `None`. The token list collapses to empty and the gate reports "the quoted string carries no
   numeral at all" about a string whose numeral is right there. Slide 4's 1,400 hit it this run.
   The fix is one line, `t.replace(",", "")` before the `isdigit` test, plus a self test case
   asserting a quoted 1,400 re-derives. `scripts/carousel/` is the `upgrade` actor's lane and
   CLAUDE.md says the routine does not edit the engine it is currently running, so this is filed
   rather than patched. The figure was declared through `computed_by` instead, which is honest
   here because the frame's 1,400 is a drawn count the builder asserts at build time, and the
   declaration says so and names c17 as the floor. It would not have been honest for a figure
   that was only ever quoted, and the next one will be.

## Two process errors this run made, and what they cost

Both were mine and both are worth writing down, because each one wasted a full review round.

**The pixel critics were spawned before the storyboard was reconciled.** Slides 1, 2, 4, 5, 7
and 9 had been rebuilt during the render loop and the dossiers still described the drawings that
were planned rather than the ones that shipped. Two critics correctly reported "I am grading a
render against an acceptance list written for a different drawing" and spent findings on the
mismatch. Reconcile the plan to the frame FIRST, then review. A stale dossier does not just
waste a review, it makes `dossier_check` green against nothing.

**The thumbs were not regenerated after the last render.** `assemble.py` was run, then four
slides were re-rendered, and the critics read thumbs that predated the fixes. Two of them caught
it, one of them by comparing landmarks across six points to prove it was one file and not a
pipeline failure, and both correctly said no perceptual item on those frames could be judged
until it was fixed. Every string check in the suite reads the DOM and the DOM was right, so
nothing else could have seen it. **Re-run `assemble.py` after every render, without exception**,
and the standing proposal is a gate that asserts each thumb is not older than its own render, by
exit code, so a re-render without a re-thumb fails the build instead of shipping the previous
frame to the feed.

## The deck

### Selection, and why this story and not the others

**The story: driverless vehicles are already ordinary work in Texas, and on August 25th the
Senate Committee on Transportation meets to study their deployment under SB 2807 and to
quantify the impact on traffic related collisions.**

The record holds the decision. tx-2026-0077 was admitted yesterday and re-verified this run
against the Legislature's own upcoming meetings listing, which is a compliant path on a host
whose hearing notice directory is not. So this is a deck about a decision the docket carries,
which is the Phase 8 bar.

**Why this one.** Six candidates came back strong enough to build on. The Governor's Data
Center Coalition announcement is downstream of a deck that shipped two days ago and rests on a
host this project may no longer fetch. The House State Affairs hearing on data centers and 765
kV is the biggest story of the week by turnout and it is the fourth data center or grid deck in
six days, which is the drift `APPLICATIONS.md` exists to correct. Fort Worth's moratorium and
the Westlake restraining order are both real and both rest on journalism this run could not get
behind, because `fortworthtexas.gov` answers an edge 403 and a state district court order is not
in any keyless database. The NSF awards are good record material and thin deck material,
because a grant that starts in October 2026 has nothing a reader can see yet.

This one wins on four counts a rubric actually measures. It is **AI in use** rather than a
filing about AI, which is the beat balance the doctrine asks for and which four consecutive
decks have missed. It has a **dated door four days out** that a Texan can walk through, which
is the closing frame `texan_check` says a placeless story has to carry. Its **ordering is the
argument**, so the deck has a spine rather than a list. And it carries a **genuine counter
image from the primary source itself**, in a blind rider's welcome for the same empty seat the
deck opens on, so the deck can't be read as one sided.

**Dedupe: nothing close.** Four entries in the thirty day window and the tool found no overlap
on entities or keywords. Read rather than trusted: the four shipped decks are a semiconductor
fab in Grimes County, a Houston ISD school model, the Governor's data center audit, and a
League City surveillance ballot. None of them is a vehicle, a road or a transportation
committee.

**`texan_check` at selection: places Harris County and Travis County, body yes, deadline yes,
next step yes.** Run on the candidate before a word was drawn. The first pass named no place,
which is the warning the tool exists to give, and the fix was to anchor the deck in the two
counties the story actually happens in rather than to carry it on art alone.

**The claims gate is clean.** Thirty verified claims and ten rejected, and the rejections are
the interesting half. The 9:00 AM start time of the hearing is on the Legislature's page and is
NOT quotable, because it renders as an isolated table cell and the labelled form lives only in
the notice under the disallowed directory. Kodiak's own page says "more than 1,400 loads" where
a first retrieval returned "over 1,400", and the figure survives with the source's verb. A
county for the Permian trucks was checked for and does not exist on the page, so no county goes
on that frame. Amazon's Prime Air expansion is undated on its own page and came back with a
false exact match on a shortened string, so it is out of the deck entirely.

**The honest absence the deck will carry**, verified and cleared: none of the three Texas agency
pages the committee's own charge points at publishes a count of crashes involving driverless
vehicles. It names where it looked. A second absence, that the federal file is the ONLY public
source, was offered and REFUSED, because the two pages that would settle it returned 403.
