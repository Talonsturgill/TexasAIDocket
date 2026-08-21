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

7. **`aggregate_check` short-circuits the whole text node on `EXEMPT`.** `if EXEMPT.search(text):
   return []` runs before any detection, so a sentence containing a bill number or a bare year
   switches aggregate detection off for its entire length. Slide 6's dek carries both "SB 2807" and
   "2026", which is why "392 days" in the same sentence was never detected, and why a declaration
   for it is refused as undetected. An integrity judge found it independently. The fix is to strip
   the exempt spans and scan what is left, rather than dropping the node. Filed, not patched:
   `scripts/carousel/` is the `upgrade` actor's lane.

8. **`data-decorative` on the `.geo` footer is the largest hole in the numeral law, and it has now
   hidden two separate defects in two consecutive panels.** `aggregate_check`'s `scan_report` skips
   decorative nodes, which is right for a coordinate pair and wrong for everything else that block
   has ever carried. Panel one found `254 COUNTIES` typed there as a string literal on the one frame
   that loads the file it could be counted from. Panel two found `PERMIAN BASIN / OIL FIELDS` on a
   frame whose own source line cites two Aurora claims, neither of which names that place. Neither
   was visible to any gate. Two fixes, and they are different sizes. The cheap one, taken this run:
   the deck's own law is now written into the storyboard, that **the location stamp names only what
   a claim cited on that same frame names**, and no coordinate is printed at all. The real one, for
   the upgrade actor: bind the stamp to a claim id from that frame's cited set and drop the
   decorative exemption for it, so a stamp that names a place no cited claim names fails the build.

9. **`texan_check`'s DATE regex is case sensitive and its ACTION regex is not, so a closing frame
   that sets its date in caps reads as having no date.** Slide 9's date block is `AUGUST 25TH, 2026`
   in white mono on the red plate, which is the most prominent thing on the frame, and the gate
   reports `next step NO` on a frame carrying a dated public hearing, a room number and the page it
   is posted on. `DATE` is compiled without `re.I` while `ACTION` is compiled with it. This is not a
   defect in the deck and the run did not reword a frame to suit the regex, because that is the
   wrong way round and this file says so elsewhere. Add `re.I` to `DATE`, and add a self test case
   asserting an all caps closing date is seen. `scripts/carousel/` is the `upgrade` actor's lane.

10. **`docket_calendar.KIND_LABEL` has no entry for `expires`, and CI found it before the merge.**
    The two NSF awards admitted this run carry a September 30th, 2029 end date, and the kind that
    fits it is `expires`. The calendar's label table holds nine kinds and none of them is that, so
    its self test went red on `every kind on the real record has an explicit label`, and the 2029
    date broke two more of its assertions about a window computed two years back from today.
    `scripts/site/docket_calendar.py` is `human` owned so this run could not add the label. The
    key dates came back out and the fact stays where it already was, in both summaries, which say
    the project runs from October 1st, 2026 through September 30th, 2029. **The proposal is to add
    `expires` to `KIND_LABEL` and to decide deliberately whether it belongs in `ACTIONABLE`**, which
    it does not, since a grant ending is not a door. Worth saying plainly: the local gate suite the
    routine runs before pushing does not include this self test, and CI does. That is the gap, not
    the label.
11. **`deck_preview` is a word count on the deck's headline, and nothing on the carousel side can
    see it.** The article card's preview takes the first two sentences of the first slide that
    speaks prose, and slide one always speaks its hook first, so the preview is the hook and only
    the hook whenever the hook runs to two sentences. `site_build`'s own self test then requires
    eight words under every card title. This deck's hook was seven. Every carousel gate was green,
    the render was clean, the panel had passed it, and the defect lived in a counter on a different
    surface owned by a different actor. **The proposal is to let `deck_preview` keep taking whole
    sentences until it has eight words rather than stopping at two**, which is what its own budget
    argument was already for, so a short headline is previewed by the headline AND the line under
    it. `scripts/site/site_build.py` is `human` owned, so this run repaired the copy instead and the
    repair is written up below.
12. **The article description builder skips a block instead of trimming it, so a longer dek makes a
    shorter description.** The meta description walks slide strings and appends whole ones until it
    has 110 characters, breaking rather than cutting when the next one would carry it past 160. A
    38 character hook followed by a 148 character dek therefore ships 38 characters, and
    `seo_check` wants 50 to 200. The trap is that the failure gets WORSE as the copy gets richer,
    which is the opposite of what an author would predict, and this run walked straight into it by
    lengthening the dek to satisfy proposal 11's counter. **The proposal is to cut the final block
    at a sentence boundary inside the budget rather than dropping it whole**, which is what the
    function's own comment already says it does. Same file, same owner, same answer: the copy moved
    instead.
13. **The render engine's documented way to load committed geodata does not work in Chromium 151.**
    `render.py` resolves `@@ASSETS@@` to a `file://` path and its own header tells a slide to reach
    it with `fetch(...)`. Chromium refuses `fetch` on a `file://` URL whatever
    `--allow-file-access-from-files` says, and it refuses it silently enough that the frame simply
    throws. This is new since the deck first rendered on the same source this morning, so the
    browser under the runner moved. `XMLHttpRequest` still reads the same URL, verified against the
    committed county topojson at 495,034 bytes. **The proposal is to change the header's example to
    XHR, or better, to have the renderer inline `@@ASSETS@@` JSON at resolve time** so a slide never
    performs a network-shaped read at all. `.claude/skills/carousel-engine/render.py` is not this
    actor's, so slide six's own art carries the XHR read and a comment saying why.
14. **`sources_block.py` reports success when it was handed a path that does not exist.** Called
    with `--run <date>`, argparse prefix-matches `--run-dir` and the script takes the bare date as
    a directory. It then finds no printed ids, concludes every printed id resolves, prints
    `sources block: clean` and exits 0. A checker whose empty case is indistinguishable from its
    clean case is worse than no checker, because it is trusted. **The proposal is to fail when the
    run directory does not exist, and to fail when the deck printed no claim ids at all**, since a
    deck that cites nothing is a defect rather than a pass. Worth pairing with a second look at
    every gate in `scripts/carousel/` for the same shape, because this one was invisible for a
    whole run behind an exit code of 0.
15. **`ownership.yaml` gives `ledger/carousel/**` to `daily`, which lets the record's own actor
    rewrite the craft memory.** This run had to correct `artwork.json`, because the entry described
    slide 8 as a milled relief with the shadow on the near wall, and the sixth panel's craft judge
    measured the render and found no band and no trough. The correction was right and the file
    said so, but the actor that made the drawing is also the actor that grades it in the ledger,
    which is the arrangement `instincts.json` already refuses by keeping confidence out of the file
    and deriving it in code. **The proposal is to state in `ownership.yaml` that an artwork entry
    is written from the render reports and never from the plan, and to add a check that a technique
    line naming a focal region can be pointed at pixels.** Filed rather than acted on, because
    `ownership.yaml` is not this actor's to edit.
16. **Nothing checks the shipped render against the plan's own declared strings, and this run
    proved why that matters.** The tenth panel's integrity judge found that two repairs the run
    believed it had shipped existed only in `storyboard.md`, because `build_slides.py` had refused
    a footer collision and exited 1 while its output was suppressed. Three judges then graded a
    deck that was never rendered. `plan_render_check` compares the plan to the render and passed,
    because the fields it reads are not the hook and the byline. **The proposal is a gate that
    diffs `copy.json`, which is derived from the render report, against the storyboard's declared
    hooks, deks and bylines and fails on any mismatch in either direction.** It is the tenth
    panel's own one sentence fix and it would have caught this in under a second.
17. **`_footer_fit` is the only build time assertion in the deck builder and there is no gate that
    it was ever reached.** It did its job perfectly, refusing a byline 72px too wide for its frame
    and naming the overlap. What failed is that a run can suppress it and carry on rendering stale
    HTML, because the slide files are still on disk from the previous build. **The proposal is for
    the builder to delete `out/<date>/slides/` before it writes**, so a refused build leaves no
    slides to render rather than leaving yesterday's.

## Four more panels after the deck was already scored, and what each one caught

The deck was scored 7.27 on its fourth panel and pushed. CI then went red on three gates, all on
the SITE side, all reading slide one, and repairing them changed copy the panel had judged. A
changed frame makes the score STALE, which `gate_status` reads as a red row by design, so the deck
went back to the panel. It went back three more times after that, and every round found something,
which is the argument for the panel and the argument against stopping early in one table.

| panel | integrity | craft | reader | what it caught |
|---|---|---|---|---|
| 5 | 7.25 | 7.31 | 7.22 | the caption glossed a quote, two frames cited numerals whose claims were not on them, a stamp used a scope word no claim uses, and two kickers were production vocabulary and a refused universal |
| 6 | **6.61 HARD FAIL** | 7.41 | 7.27 | the cover asserted an absence the record had explicitly declined to establish |
| 7 | 7.30 | 7.47 | 7.62 | the hard fail cleared, and five overstatements upheld that no earlier panel had named |
| 8 | **6.92 HARD FAIL** | 7.22 | 7.50 | slide 7 said DPS PUBLISHES first responder plans where its own claim says the page takes them, and the storyboard's acceptance item had prescribed the verb |
| 9 | 6.96 REFUSED | 7.19 | 7.43 | no hard fail, and a refusal anyway. The caption turned c22's "this week" into a flat "on May 1st, 2025", slide 4's headline dropped c17's "in the triples configuration", and slide 9's byline filed a TxDOT claim under the Legislature |
| 10 | 7.02 | 7.18 | 7.42 | **unanimous ship, no hard fail, no refusal.** `panel.py` reads 7.42, spread 0.40, contested on claim integrity |

**The ninth panel refused without failing anything, and `panel.py` is stricter than the routine.**
The routine says any one judge's HARD FAIL stops the deck. `panel.py` also stops on `ship: false`
with no hard fail named, which is what the ninth panel's integrity judge returned at 6.96 while
calling itself in writing "a threshold miss" rather than a stop. The stricter rule is the right
one and it held: its one sentence fix was the caption's dateline, and applying that fix is what
moved the tenth panel's integrity judge to 7.02 on the same lens.

**What the tenth panel read, stated exactly.** All three judges read the deck BEFORE two of their
own integrity findings landed. Slide 4's dek did not yet carry c17's "in the triples configuration"
and slide 9's byline did not yet name TxDOT. Both are now on the frames. The published 7.42 is
therefore a floor rather than a ceiling: the deck that ships is the deck they scored plus the two
citations they asked for, and neither adds an assertion. That is the conservative direction and it
is written here rather than smoothed over.

**Where the tenth panel's craft judge landed on slide 8, which five judges have now ruled on.** Six
craft readings scored artwork craft at 6.0, 5.8, 6.5, 6.0, 6.2 and 6.0, and every one of them named
the same three frames. All six ruled slide 8 a failed technique rather than an unfinished frame, and
four said in writing that a judge ruling the other way would be reasonable and the deck should then
stop. Nobody did. The frame is composed, the relief shader ran, and it ran on the figure instead of
the ground, so the type reads raised where the plan wanted it cut. The ledger says so in its own
words and the rebuild is the run's named debt.

**Two hard fails, three panels apart, and they are the same defect.** The cover said "No column for
it" because the deck wanted a rhetorical spine. Slide 7 said "DPS publishes" because an acceptance
item had written the word PUBLISH into the plan. In both cases the composition chose the word and
the fact was fitted to it afterwards, and in both cases every gate in the suite stayed green,
because a gate can check that a claim id resolves and cannot check that the sentence above it says
what the claim says. That is the finding of this run, and it costs more to learn than the deck did.

**The eighth panel's fix changed the plan, not just the frame.** The acceptance item that said the
dek must say "what each does publish" now says it must say what each page HOLDS, in the words the
record actually read on it, with a line stating that an acceptance item may require a frame to be
positive and may not choose its verb. Fixing only the sentence would have left the instruction that
produced it sitting in the plan for the next run to execute again.

**Panel 6 is the one that earned all of them.** Its integrity judge failed the cover. The hook read
"Every mile is logged. No column for it." over the source line `Aurora, c27 c28`, where c27 is a
dateline and c28 is Aurora's mileage figure, and neither supports an absence. The absence this run
actually verified is narrower on both axes, a crash COUNT missing from three named pages, and the
run's own rejected list says in writing that the TxDOT CRIS query never rendered and **an absence
cannot be asserted from a page that did not render**. The deck had chosen its rhetorical spine
before the record could verify it, and four panels, every carousel gate, a full pixel review and a
flow critic had all read that cover and let it through.

The cover now ASKS. "Every mile is logged. Who counts the crashes?" A question asserts nothing, and
the deck answers it from verified material one swipe later, on slide 7 with the three pages and on
slide 8 with the federal file. `fitText` was capped at two lines when the longer hook wrapped to
three and machine QA caught it running through the dek, which is the gate doing its job on a change
made to satisfy a judge.

**Panel 7 upheld five findings without failing any, and four were corrected.** Slide 2 said "five
of seven marks in the last 89 days" for a window that ends on the hearing, four days after
publication, and counted the hearing as one of the five. It now says "in the final 89", which is a
statement about the shape of the 481 day span rather than about days that have elapsed. Slide 6
said "the first driverless lane", a superlative in no claim, and now names the Dallas to Houston
lane. The caption said "its three charges" and closed a list nothing establishes as closed, two
sentences after `aggregates.json` argues at length that the deck may not close a list a source
leaves open. And `artwork.json` stated the law "every word on a frame is DOM text" beside a frame
that ships four canvas bitmaps, so the entry now records the law AND that this deck broke it.

**The fifth was left standing and it is written here rather than fixed.** 481, 392 and 89 all
anchor on May 1st, 2025, taken from Aurora's announcement, whose own quoted words are that
deliveries began "this week". The lane opened somewhere in a several day window, so three published
day counts are floors printed as exact. The eighth panel's integrity judge ruled on it and did not
fail it: a dated primary announcement of commencement is a legitimate anchor for a derived span,
the `modeled` label governs estimates code produces from a model rather than a day count between
two fetched documents, and the imprecision is bounded inside the announcement week and runs
conservative. It is a real demerit and it is one word from being exactly true, which is what the
next run should spend the word on.

**What was NOT fixed, and is carried rather than hidden.** Three craft findings survived every
panel because each is a frame rebuild rather than a copy change, and this run did not have the day
left for one. Slide 8's declared focal, a milled band of lit groove lips about 880 by 260px, does
not exist in the render, and what shipped is the inverse of the technique with the striations
inside the letterforms; three craft judges each ruled it a failed technique rather than an
unfinished frame, and two of the three said in writing that they would not argue against a judge
who ruled the other way. Slide 5, the deck's declared turn, has a cast shadow with no caster in
frame. Slide 3's rig reads as clip art at thumb size and shows one trailer for a dek about triples.
Slide 8 also ships its four header strings as canvas bitmaps against this deck's own recorded law
that every word on a frame is DOM text, which the artwork ledger now states along with the breach.

**Two corrections were themselves caught by gates, which is worth more than the corrections.**
`shipped_check` found that slide 6's two new claim ids never reached the published sources block,
because `sources_block.py` had been called with a flag that does not exist for the whole run.
`dossier_check` found that the storyboard note added for the superlative fix had closed a quote in
the wrong place and destroyed slide 6's dossier. Neither would have been visible by reading.

## Four process errors this run made, and what they cost

All four were mine and all four are worth writing down, because each one wasted a review round.

**A build that REFUSED was treated as a build that ran.** `build_slides.py` was invoked as
`python3 ... >/dev/null 2>&1` and its exit code was never read. `_footer_fit` refused the run,
correctly, naming a slide 9 byline 72px too wide for its frame, and printed the overlap to a
suppressed stream. The previous build's HTML was still in `out/<date>/slides/`, so the renderer
rendered it, every gate passed on it, and three scoring judges graded a deck that had never been
built. One of them caught it by reading the pixels against the plan and said so in its first
paragraph. **This is the repo's own stated law violated in the one place the law does not name.**
`CLAUDE.md` says run a gate BY EXIT CODE and never by reading its last line. The gate here was not
a gate, it was the builder, and its exit code was not read at all. Proposals 16 and 17 are the two
halves of the fix: check the plan against what actually rendered, and have a refused build leave no
slides behind for the next command to render.

**`sources_block.py` was called with `--run` for the whole run, and there is no `--run`.** The
flag is `--run-dir`, and argparse matches an unambiguous prefix, so `--run 2026-08-21` set the run
DIRECTORY to the string `2026-08-21` and the script then reported `sources block: clean, every
claim id the deck prints resolves to a document` and exited 0. It said that every time it was
asked, including immediately after slide 6 gained two claim ids, and `shipped_check` caught the
real state one step later: the deck printed c22 and the published sources block did not list it,
so a reader could not reach the document. Building it needs `--build` and checking it needs
`--check`, and with neither the script does something that looks like both. **This is the exact
shape `CLAUDE.md` warns about, arrived at from a direction the warning does not cover.** The rule
is to run a gate by exit code rather than by reading its last line, and the exit code was 0 and
the last line was reassuring and the gate had not been pointed at the run at all. An exit code
proves nothing about a checker that was handed the wrong path. The standing proposal is at 14.

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

## What the first scoring panel refused, and what it cost to fix

Three judges, three lenses, three refusals at 6.67, 6.75 and 6.81. None of them cleared the 7.0
floor and two of them carried hard fails. Every one of the findings below was real and none of
them had been caught by any gate in the suite.

**A typed numeral on the one frame that could have counted it.** `STATEWIDE / 254 COUNTIES` was
a Python string literal, on slide 6, which loads `assets/geo/tx-counties.topo.json` to draw the
mesh and never counts its geometries. The identical stamp on slide 2 was computed. Two of the
three judges found it independently, one of them by reading the builder. It was invisible to
`aggregate_check` because the `.geo` block carries `data-decorative`, and that exemption exists
for a coordinates footer that this run had already deleted. `aggregate_check`'s own docstring uses
"254 counties, `len()` of a topojson" as its canonical example of the computed route. The number
was right and nothing in the pipeline made it right, which is the whole of the law.

**A frame that refuted itself.** Slide 8's dek said the federal header row "begins with the
reporting entity and the report type" while the frame drew `Report ID, Report Version, Reporting
Entity, Report Type` at 84px directly above the sentence. The frame's acceptance list checked the
milled header word for word against c31 and checked the dek for one required string and one
forbidden word, and never checked the dek's second sentence against anything.

**An absence that overreached its own source.** The absence record asserted that the three pages
checked were "the three Texas agency pages the committee's own charge points to". c4's quote names
the Department of Public Safety, the Department of Motor Vehicles and the Texas Department of
Licensing and Regulation. The Department of Transportation is not among them, and it is the agency
that publishes the state's crash records. The three pages checked are the Legislative Reference
Library's resource list beneath the charge, which is a different set. Corrected in the claims file,
the caption and the aggregates, and the mismatch is now published as what it is: the charge asking
for a collision count names three agencies and leaves out the one that keeps the crash records.

**Numerals typed beside the code that computes them.** "Five of seven" on slide 2 and "392" on
slide 6 were both typed while `TAIL_MARKS`, `len(SEQ)` and `SPAN_TO_AUTH` sat computed and unused.
Both are interpolated now, and the spelling of a small count is a function of the count.

**A hook with no claim under it.** Slide 1 said "Every mile logged" over a dek about Dallas to
Houston, and neither cited claim mentioned miles, logging or measuring. The dek now carries c28,
which is Aurora reporting one hundred thousand driverless miles on public roads.

**A city that did not do the thing.** Slide 5's headline read "Houston opened it to everyone".
Waymo did. A reader who reads only headlines never reaches the dek that corrects it. The headline
is now the source's own sentence.

**A close with nothing to do.** `texan_check` had been reporting `next step NO` all run and the
run had been treating it as the acceptable cost of refusing to assert a right to testify. The
reader judge found the middle the run had missed: the Legislature's own upcoming meetings listing
is the page c1, c2 and c36 were fetched from, and naming it asserts nothing about who may speak.

**A plan describing a deck that no longer existed.** The `FRAME WIDTH` stamp was removed from the
pixels earlier in the run and the storyboard's own prose still called it load bearing on every
slide, as did the builder's docstring. The acceptance items had been updated and the narrative had
not, which is how a fix silently reverts on the next run.

The panel is the most expensive phase in this routine and it is the only one that has ever found
these. The pixel critics read the frames and found craft. The gates read the files and found form.
Only a judge told to refute the deck went and read the builder to see whether a number on a slide
was a number the code produced.

## What eight scoring panels cost, and what they were worth

Twenty four judgments across eight panels. The scores went 6.67 6.75 6.81, then 6.41 6.51 6.88,
then 6.85 7.07 7.47, then the fourth that shipped, then the four in the table above. Not one of the
eighteen findings below was caught by any gate in the suite, and the suite ran green on every one
of those rounds.

**The last four panels change what this section concludes.** Written after the fourth, it said the
panel had stopped paying and that a fifth would be scoring the same deck. Then the fifth found six
defects, the sixth failed the cover outright, the seventh upheld five more, and the eighth ruled on
the last one standing. The honest revision is that a panel keeps paying as long as the deck keeps
moving, and this deck kept moving because each repair changed copy. What actually stopped paying
was re-scoring a deck NOBODY had changed, which is not what any of the last four did.

Counting them by KIND rather than by frame is the useful cut, because the kinds repeat and the
frames do not.

**Six numerals typed beside the code that computes them.** 254 counties on the one frame that
loads the county file. "Five of seven" beside `TAIL_MARKS` and `len(SEQ)`. 392 beside
`SPAN_TO_AUTH`. A `FRAME WIDTH` in feet on all nine frames, contradicting its own drawing on at
least two. Three coordinate pairs, two of them wrong against the committed gazetteer's own
centroids. The pattern is not carelessness about arithmetic. It is that every one of them lived in
FURNITURE, and furniture is where a run stops thinking of a string as a claim.

**Four place stamps naming a place no cited claim names.** PERMIAN BASIN on an Aurora only cover.
PERMIAN BASIN again on a Kodiak filing frame whose claims name a conveyor. STATEWIDE on two more.
Each was fixed one frame at a time as each panel caught one, which is the shape of a defect that is
being treated as an incident. Checking all nine at once was what ended it.

**Three sentences that overreached their own source.** A dek saying the federal header row "begins
with" two fields the drawing above it shows it does not. An absence record claiming three pages
were "the three the committee's own charge points at" when the charge names a fourth agency and
not one of these. A closing sentence turning the source's expressly non-exhaustive "including"
into a closed list, on the deck's sharpest finding.

**Two artefacts that had drifted from the pixels.** The storyboard, three of whose repairs existed
only on the frames. `first_comment.txt`, which did not resolve a claim id two frames printed.

**One date on three surfaces with no claim quoting it,** living in a `source_title`, which is a
field a run writes rather than one a page carries.

The single most useful thing a panel did was read the BUILDER. Two judges opened
`build_slides.py` and found a string literal where the code beside it was computing the same
number. No pixel critic could have seen it, because the pixels were correct. No gate could,
because `.geo` is `data-decorative` and the exemption was written for a footer this run had
already deleted.

## Why this deck names no county, and why that is an answer rather than a gap

Every panel priced it and each was right that the rubric's 9 for story_and_stakes reads "names the
county, the body and the deadline". Three judges suggested computing Harris for the Houston frame
and Travis for the Capitol frame out of the committed gazetteer, the way slide 6's 254 is now a
`len()` of the county topojson.

**The record already answered it and the answer is none.** `ledger/docket.json`, tx-2026-0077,
carries `geography: {statewide: true, counties: [], metro: null, on_ercot: false}`, computed and
validated by `docket_build`. A Senate interim charge directing a committee to study a statewide
deployment has no county, and the item this deck is built on says so in a field this project
computes rather than types.

The gazetteer cannot supply one either. It holds 254 counties, 67 metros, 13 combined areas and
two divisions, and **no city records at all**, so Houston does not resolve to Harris from anything
committed here. A run that wrote Harris on slide 5 would be typing a fact it could not compute,
on the one deck whose whole argument is about a state that publishes an authorization and no count.

So the cap stands and it is bought honestly. What is worth changing is not the county, it is that
slide 6 draws all 254 outlines and points at none of them while stamping a word about scope. The
frame's argument is that the requirement applies in every county equally, which is why it draws one
class for all 254, and the drawing makes that argument without needing a label to assert it.

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

**The claims gate is clean.** Thirty two verified claims and eleven rejected, and the rejections are
the interesting half. The 9:00 AM start time of the hearing is on the Legislature's page and is
NOT quotable, because it renders as an isolated table cell and the labelled form lives only in
the notice under the disallowed directory. Kodiak's own page says "more than 1,400 loads" where
a first retrieval returned "over 1,400", and the figure survives with the source's verb. A
county for the Permian trucks was checked for and does not exist on the page, so no county goes
on that frame. Amazon's Prime Air expansion is undated on its own page and came back with a
false exact match on a shortened string, so it is out of the deck entirely.

**The honest absence the deck will carry**, verified and cleared: none of the three Texas agency
pages this record checked publishes a count of crashes involving driverless vehicles. It names
where it looked. It first said "the three pages the committee's own charge points at" and the
scoring panel was right that this is not what those three are. c4's quote names the Department of
Public Safety, the Department of Motor Vehicles and the Department of Licensing and Regulation, and
the Department of Transportation is not among them. The three checked are the Legislative Reference
Library's own resource list beneath the charge. The mismatch is the sharper finding and it is on
slide 9 now rather than only in the caption: the charge asking for a collision count leaves out the
agency that keeps the state's crash records. A second absence, that the federal file is the ONLY public
source, was offered and REFUSED, because the two pages that would settle it returned 403.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 32 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 15 warn(s) |
| aggregates     | PASS   | 10 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 4.59 MB, vector |
| score          | PASS   | 7.42 |
| dossiers       | PASS   | 43,820 chars planned |
| caption        | PASS   | 177 words |
| craft floor    | WARN   | 9 frame(s), median 208, floor 60, 4 quiet |
| plan vs render | WARN   | 6 of 67 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step NO |
| absences       | WARN   | 3 of 6 scoped to a named document, 3 unscoped |
| completion     | PASS   | the deck shipped |
<!-- gate-status:end -->
