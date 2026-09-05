# Run record, 2026-09-05

Branch `claude/daily-2026-09-05`. One routine, two deliverables, the record first.

## Phase 0, wake

`guards_local.py --fast --only Ownership` exit 0, so `core.hooksPath` is wired to `.githooks`
and the gate that used to skip when it was not now passes on having been asked. Git identity set
to the owner's in the fresh clone, per CLAUDE.md. `docket_build --validate` and
`ownership_check --self-test` both exit 0 on the clean checkout, so nothing shipped past a gate
yesterday. `bootstrap.sh` exit 0. No `prompts/NEXT_RUN.md`, so no story was queued.

**Off the table today**, read before anything was chosen. All fifteen entries in
`ledger/carousel/topics.json` fall inside the thirty day window, so every shipped deck's topic is
excluded. Opening moves from the last six runs are off the caption menu, being the two things,
the object twice, the before and after, the plain question and the place. Structures from the
last three are off, being pivot, question and answer, and two columns.

## Phase 1, craft refresh

One rotating focus, chosen against where the last several panels actually lost craft marks
rather than against the story, since the story was not yet picked. **Legibility at feed scale and
the single dominant focal.** The finding worth handing the directors room is that attention
studies of dispersed compositions measure roughly half the central concentration of ones with a
single dominant focal, and that formal guidance for visualisation thumbnails is thin enough that
the honest move is to test at 432px rather than to trust a rule. That is the same instruction the
technique library already gives under TYPE AND CAROUSEL MECHANICS, so this run treats it as
confirmation rather than as news, and the operative sentence for the dossiers is that a frame
declares ONE focal and it is an area.

Yesterday's focus was absence and reference frames. Not repeated, deliberately, and the reason is
in Phase 8.

## Phase 2, the worklist

`docket_staleness --today 2026-09-05` exit 0. **95 of 105 items due, nothing rotten, nothing
deferred, and no `--budget` passed.** The leash is two days for every item whatever its status,
so the worklist is however long that is, and today it was 95.

## Phase 3, re-verify

`reverify.py --today 2026-09-05 --apply` exit 1, which is the code that means the report lists
what needs a person. 173 urls behind 494 claims, 23 answered 304, 147 sent a body, 3 did not
answer. **65 items stamped by the script as checked and unchanged.**

**The 65 deterministic notes were re-worded, which is the part of this phase a machine should not
keep.** The script wrote eight distinct sentences across 65 items, one of them 41 times. Each is
now the item's own sentence about its own decision. `reverify.py --check-notes` exit 0 over 323
checked notes, so no figure was introduced by hand. `docket_build --validate` caught one British
spelling in a note I wrote and it is fixed, which is the gate working on the run rather than on
the previous run.

**The 31 the diff handed back were worked one source at a time**, and most were not sources that
moved. They were sources this checker structurally cannot read. San Angelo and Killeen serve
PDFs, Legistar and the PUCT Interchange serve pages the plain fetcher cannot match, and several
newspapers refuse a bare client. Re-fetched with a browser user agent and a PDF reader, they
confirm. The Federal Register answered 500 twice and confirmed on the third attempt with backoff.

**Two real movements, and one of them was the record telling a reader something untrue.**

`tx-2026-0096` carried status `open` and room `open_meeting` and a title promising the committee
"sits again on September 2nd". Both sittings on the data center cooling water charge have been
held, and the Legislature's upcoming meetings listing no longer carries either, which is what a
past hearing looks like on that page. Status moves to `pending`, the room to `contact_only`, and
the title and summary stop advertising a door that has shut. This is exactly the failure the two
day leash exists to catch, and it is the reason a `decided` item gets the same leash as an open
one.

The two Oncor 765 kV dockets have each taken further filings, so the newest filing-count claim on
each is refreshed against today's index.

**Named as unconfirmed rather than dropped or asserted.** `seguingazette.com` and
`newschannel10.com` now serve a wrapper rather than the article, so the sheriff's words on
`tx-2026-0036` and the commissioners' words on `tx-2026-0046` could not be confirmed this run and
the items say so. Taylor's notice address still answers 404, which is what `tx-2026-0027` already
claims, so that item is confirmed by the absence rather than damaged by it.

**96 of 105 items carry today's stamp and a dated movement line.** `--validate` reports all items
verified within two days.

## The backlog

Three entries at wake and three at close, all of them the ERCOT-region items exempt by name.
`tx-2026-0001`, `tx-2026-0002` and `tx-2026-0007`. **Not cleared, and the reason is a judgement
rather than a shortfall.** Each is a commission proceeding about the ERCOT region. ERCOT is not
Texas, since El Paso and part of the east are outside it, so `statewide: true` would publish a
claim about scope that no source makes, and naming two hundred counties is not what the field is
for. The backlog held steady, which the routine accepts. It did not grow.

## Phase 7, the instruments

`gridwatch_pagecheck` exit 0, `waterwatch_pagecheck` exit 0, `waterwatch_page --self-test` exit 0.
Both instruments read as current and holding their promises. Nothing to fix and nothing stopped.

**The scanner ceiling was NOT checked and this is the one thing in this phase a person should
see.** The Supabase connector is installed and connected at the org level and is
`enabledInChat: false` for this session, so its tools are not loaded and the query cannot be run.
That is not a failed query, it is an unrun one. Per Phase 7 this never blocks the run, and per the
same phase a ceiling nobody is notified about is one you learn about from the people who gave up.
**A maintainer enabling the Supabase connector for this session's environment is what fixes it.**

## Phase 4 and 5, discovery and admission

Polled, in order. PUCT calendar RSS, which named three project numbers with dates and is the
reason this run found that Project 58482's comment deadline fell yesterday and that Project 58555
is an ERCOT ancillary services study rather than an AI matter. PUCT Interchange by control number
with a browser user agent. Texas Register. Federal Register with a comment-date filter, 18 open
windows, all national rather than Texan. CourtListener v4 across the Texas federal districts and
CA5, 8 results, mostly patent suits.

Six scouts, four of them on application beats as the doctrine requires, and all six returned.

**Three items admitted and the ledger closed at 108.** It reached 110 for a few minutes and came
back down, which is not a typo and is explained in the next section.

## THE BEAT THIS RUN WANTED, TOOK, AND GAVE BACK

This is the run's largest finding and it is a contradiction between two authoritative files
rather than a defect in either.

**What was found.** `docket_build.TOPICS` carries eight beats and every one of them is about what
is being DECIDED about AI. `knowledge/shared/APPLICATIONS.md` exists to correct exactly that and
says to put the application layer first. The vocabulary that decides what the record may admit
never carried the correction, so the record has been silently refusing the thing its own doctrine
says matters most.

That is not an inference. Two candidates were sitting in `seed/docket_seed.json` naming it as the
reason they could not be filed, a driverless service opening to the public in Houston and a plant
assembling AI servers in the same county.

**CORRECTED, and the correction is the point.** This section first claimed both candidates had
already been written against the slug `ai-in-the-field` AND the decider type `company` by earlier
runs. A review bot checked the parent revision and that is only half true. Both were written against
`company`. Only the Waymo candidate was written against `ai-in-the-field`, and the Apple one was
filed under `state-policy` until THIS run changed it. So the earlier diagnosis covers the decider
type for both and the beat for one, and presenting this run's own edit as prior evidence was an
overstatement about the strength of the case.

**The second half of the gap had already cost the published record.** `DECIDER_TYPES` had no word
for a company acting alone, so items were filed under the nearest wrong one. `tx-2026-0101`
carried Houston Methodist, a private hospital system, as a `special-district`, which is a unit of
Texas local government. A closed vocabulary with no word for a thing does not stop the thing being
admitted. It makes the record say something false about it instead.

**What was done and then undone.** Both values were added, `site_build.py --self-test` passed with
the blurb check green on both sides of the two file beat change, `--validate` passed, and both
held items promoted cleanly under the new beat. Then `schema_contract.py` asked for its record to
be updated, and `ownership.yaml` refused `config/schema_contract.json` to `daily` on a stated
ground this run agrees with, being that a contract the process changing the data can also rewrite
is not a contract.

So the topic addition was reverted, the contract file was restored, and the two items were removed
from the ledger before anything was committed. **`DECIDER_TYPES` is not tracked by the schema
contract, so that half is wholly inside this lane and it stayed**, along with the `tx-2026-0101`
correction it makes possible.

**Why the items were not simply filed under an existing beat.** Because that is the same fault
this run just corrected. Filing a robotaxi launch under state policy or a server plant under
research would make the record say something false in order to avoid saying nothing, and the
Houston Methodist entry is what that looks like a month later. Both are held on their own claims,
both were re-verified against their sources today, and the held reason is now one file rather
than two.

**The proposal, for a maintainer.** Add `ai-in-the-field` to `docket_build.TOPICS`, the matching
line to `TOPIC_BLURBS` in `scripts/site/site_pages/docket.py`, and the value to
`config/schema_contract.json`. Adding a value to a vocabulary is additive and does not bump
`SPEC_VERSION`, by the contract note in `docket_build.py` itself. The blurb this run wrote and
reverted, offered as a starting point rather than as the answer, was "AI already at work on Texas
ground. Oilfields and farms, freight lanes and plant floors, and who is doing the job differently
now."

**The contradiction worth naming, because a later run will meet it too.** Phase 5 of
`prompts/daily_routine.md` tells a run what to do when it admits a beat the record has never
carried, and describes it as a two file change. It is a three file change, and the third file is
`human`. Either the routine's instruction or the map needs to move, and neither is this lane's to
move.

## What was admitted

Three items, each on its institution's own announcement, each fetched this run, each naming its
county and citing a primary source.

- A Texas A&M materials screening tool the college states is free and openly available.
- Four UT Austin fusion seed grants whose release states the limits of the machine learning
  method alongside its promise, which is a rarer thing for a university to publish than the
  promise alone.
- An Energy Department award to a Houston led team using AI to search for new magnet materials
  while balancing supply constraints. **This bullet read "magnets that avoid imported rare earths"
  and so did the item's own title and summary in `ledger/docket.json`, and NOT ONE of that item's
  four evidence quotes says it.** A scorer found the reading on slide 6's dek at round 1, in the
  two carousel ledgers at round 2, and here at round 3, one surface further out each time. This is
  where it originated and this is where it is fixed.

The gate held all three at first and was right every time. One on a key date kind outside the
vocabulary, one on a British spelling, one on a comma rate of 4.52 against the 3.97 ceiling, and
two on a stamp with no movement line beside it. Each was fixed rather than argued with.

## Discoverability signoff

Six surfaces, opened rather than inferred, on the 2026-09-05 temp build of 667 pages and 108 items.

- **One decision's card, opened as an image.** `og/tx-2026-0124.png`, the run's newest item.
  Opened as a PNG. The headline breaks after "Energy Department", after "research arm funds a"
  and after "Houston led team", which are all places a reader would break it, and the fourth
  line ends on the whole word "design" before the ellipsis rather than on a stump. The wrapper
  cuts on width and this title is longer than the card holds, so the ellipsis is doing its job.
  No defect.
- **`/questions/`, read as a reader.** Opened and read. Eight shapes, and they are questions a
  person would type. What each decision is, who decides, how the public can take part, where a
  comment window is open, where in Texas it applies, what has been decided, what happens next,
  when each one started. The counts differ by shape rather than all reading 108, which is the
  honest behaviour. No shape has stopped making sense against this run's new items.
  **CORRECTED after a review bot read it against the ledger.** This bullet first paired the counts
  with the wrong shapes, saying who decides answered 101 of 108. Every one of the 108 items carries
  a decider name, so who decides answers 108. The 101 is the take part shape, which is every item
  whose room is not an open comment window, and the 7 is the comment shape, which is exactly the
  seven open windows. Counted off the ledger rather than off the page this time.
- **The `Open right now` section of `llms.txt`.** Ten entries, cross checked against what
  Phase 3 moved. tx-2026-0096 is correctly ABSENT, which is the check that matters today. Its
  hearings were held on September 1st and 2nd and this run moved its room from open_meeting to
  contact_only, so a window that shut is no longer advertised as a way in. tx-2026-0109 is
  correctly PRESENT with its September 22nd reset. The build ran after the record moved.
  One correction to my own reading, recorded because the wrong version nearly went in this
  file. A first extraction of this section came back empty and read as a defect. The range
  expression terminated on the heading it started from. The section was populated the whole
  time.
- **`/sources/`, the record's own report card.** The share at the top reads 490 of 568 claims
  resting on a primary document, across 195 documents from 86 publishers. The top publisher is
  `interchange.puc.texas.gov` at 87 claims, which is the commission's own filing index and is a
  primary source, so the heaviest thing this record leans on is a document rather than a report
  about one. Second is `api.nsf.gov`, also primary. Nothing on the top of that list would
  embarrass the promise.
- **`/topic/`, counting one card against its own page.** The hub prints 8 beats. Data centers
  27, defense and federal 2, health and education 10, land water and permitting 14, power and
  the grid 11, research and science 19, state policy 16, health and education 10, surveillance and
  policing 9.
  Those eight sum to 108 and the front page counter row prints 108 decisions tracked, so the
  beats and the counter agree.
  The figure that could have disagreed is the one about TODAY rather than about the record, and
  it does not. Four beats each print "1 still open to comment", which sums to 4. The front page
  prints "04 Doors open to you". The ledger itself holds exactly four items whose room is
  `open_comment` with a close date on or after today, being tx-2026-0016, tx-2026-0075,
  tx-2026-0107 and tx-2026-0118. Three published surfaces and the record agree.
- **`/place/`, for the places this run landed items in.** All three are on the hub with counts.
  Harris County 9, Brazos County 5, Travis County 15. This run admitted one item into each of
  the three, so the hub was rebuilt after the record moved.

## Phase 8 and 9, selection and the directors room

`tx-2026-0124`. ARPA-E funded a University of Houston led coalition, GAMBIT, to use AI to design
permanent magnets that surpass the properties of neodymium iron boron while weighing supply
constraints. Rice chooses which
candidate materials get made and tested. `dedupe_check` found nothing close.

**Four consecutive run records asked for a deck whose spine is a thing somebody did**, and deck 15's
`angle_note` said so in as many words. This one is a grant that was awarded, a coalition that was
named and a job one of its members has. Seven of nine frames are things that happened.

Three treatment directors ran on the supply chain, the object and the search. The deck takes its
cover and its attribution law from the first, its close from the second and its organising law from
the third. What each contributed and what was rejected from each is recorded at the head of
`storyboard.md` rather than repeated here.

## Phase 10, the caption room

Two directors, on the correction with a Ladder and the number that is wrong with a Ledger. **The
critic refused both**, and its two disqualifying findings were real.

- Candidate A wrote that Rice's Geoffroy Hautier *puts magnets in* air conditioning systems and
  electronic devices. c15 is Hautier SAYING magnets are everywhere. He is a computational materials
  scientist and he does not install them. The critic named it the fourth run of that defect class.
- Candidate A also completed c10's truncated quote. c10 carries confidence `medium` because only the
  leading portion was confirmed identically across two fetches, and slide 3's acceptance item ends
  the dek exactly where the confirmed text ends. The caption would have supplied the words two
  fetches could not.
- Candidate B closed on a question and then kept writing, so its body's last character was a full
  stop. `brand.yaml` sets `linkedin_post.ends_with: engagement_question` and `caption_check` hard
  fails on it. The ledger records the identical failure on 2026-08-30.
- Candidate B carried **`#HarrisCounty`**, and no claim in the file carries Harris County. It appears
  only in the storyboard's art direction register, which is a palette source and not a claim. The
  deck names no Texas place anywhere and `locator_trace` finds zero locators. A hashtag is a
  published string like any other.

One rewrite shipped. It keeps B's opening move, its structure and its first two sentences, ends on
the question, drops the slide count, and replaces "Both pages agree on the rest", which the claims
file contradicts, with the second divergence the record actually carries: Rice prints the ARPA-E
program as Magnetic Acceleration Generating and ARPA-E's own archive runs on to New Innovations and
Tactical Outcomes.

## Phase 11 and 12, the art and the taste gate

Five pixel critics over nine frames, then a verification pass over the five most changed and a flow
critic on the sequence. The findings that changed the product:

- **Slide 8 was a slope chart built out of props.** $2.9 million sat high, $2.88 million sat low, and
  one continuous brass wire ran between them. Every acceptance item on that dossier passed while the
  frame drew the comparison five structural laws forbid, because the list checked size, fill,
  lighting, type and the absence of a drawn bar, and never checked POSITION. The repair is a content
  swap, so the higher tag now carries the smaller figure and the composition is untouched. A new
  acceptance item names it.
- **Slide 2 printed five product names beside one claim id.** CONDENSER FAN MOTOR, BLOWER MOTOR, HARD
  DRIVE, EARBUD DRIVER, HAPTIC. c15 says magnets run "from air conditioning systems to all our
  electronic devices" and names nothing more granular, so those were five facts the record does not
  carry. `label_guard` refused them and was right. The frame now labels the quote's own two ends.
- **Slide 5's hook asserted a majority the source does not state.** "Most of it becomes magnets"
  against c17's "the estimated leading global use was magnets", which is a plurality. Worse, the only
  antecedent for "it" was the US import table above it, and c17 says the leading DOMESTIC end use was
  catalysts. The closing line of the frame contradicted the frame's own quote. No numeral is involved,
  so `numeral_lint` could never have seen it.
- **Slide 6's cut was lit on the wrong side.** The key is upper left and the cream wall was on the
  upper left, which is how a RAISED face lights. GAMBIT read as an emboss on the one frame whose whole
  subject is a name, inverting structural law 2. A sign flip.
- **Slide 3 stopped at a horizontal rule under a 250px fade**, which is the visual grammar of a video
  player's caption bar. A reader at 432px received "this is where the text goes" rather than "the
  record stops here". The boundary is now a hard arc.
- **Three palette tokens were passing `plan_render_check` off DEAD CONSTS.** Slides 7 and 8 declared
  `plate_ni`, `sinter` and `copper` at the top of their scripts and never drew them. The gate reads the
  frame's source, so the plan's colour test was green on code nothing executed. That is the
  2026-08-19 slide 5 defect wearing the gate's own clothes. The consts are gone.

## THE VALUE ARC, AND THIS RUN DID BOTH THINGS THE GATE OFFERS

`panel_ready` refuses a deck more than one Munsell step from its own arc. The first build measured
**6.2, 6.2, 8.4, 7.1, 75.9, 28.1, 4.4, 8.2, 3.1, a deck median of 7.1 against a plan of 33.**

The frames were redrawn first, in two passes. The ambient floor on six frames went from 6 to 8 up to
25 to 52, the lamp reach on the close widened by half, and the deck came up to **15.7, 15.3, 8.3,
16.4, 76.3, 28.0, 11.5, 18.7, 25.9, a median of 16.4.**

Then the arc was rewritten, and not because 33 was hard. A median of 34 means half the pixels of a
frame sit at mid grey, which is not a room with one inspection lamp in it. The first nine numbers
were written before a pixel existed and they describe a different room. What the measurement caught,
and what the redraw fixed, is that an ambient floor of 6 to 8 is not a dark room either, it is a
vacuum, and the bench away from the lamp carried no modelled tone at all.

**The part that mattered was the SHAPE and it is now right.** The close was the DARKEST frame in the
deck at 3.1 and it is now 25.9, the third brightest and a real climb out of frame 8. A frame whose
whole subject is that nothing is there yet has to be a bench a reader can SEE is empty.

**Deck median 16.4 against priors of 27.7, 22.2, 15.6, 21.2, 20.4, 22.5 and one breach at 73.1.**
Second darkest this project has shipped and it sits beside the 15.6, so it does not fill a band the
ledger has never seen, which is what the first plan claimed for 33. Said plainly rather than left in
the ledger to read as a variety win it is not.

**Two things the lift cost, both repaired.** The bench's raking grain runs horizontally, which is
what makes it read as rake, and at the amplitude the lift needed it drew rules straight through the
closing line and the coalition list on frame 9. The engine called it a strikethrough and it was one.
It is answered with a local knockout under the closing line, not by flattening the grain, because
flat wood does not rake. Four footers went marginal on contrast against benches that had come up
under them and were brightened.

## What the gates said, by exit code

Machine QA **0 fails** on all nine frames, four warns. `panel_ready` **0**. Green on
`plan_render_check`, `verbatim_check`, `copy_sync_check`, `dossier_check`, `absence_check`,
`craft_floor`, `coherence_check`, `texan_check`, `noun_trace`, `locator_trace`,
`construction_check`, `aggregate_check`, `quantifier_check`, `numeral_trace`, `label_guard`,
`bespoke_check`, `caption_check`, `sources_block --check`, `ship_images` (40.2 to 46.1 dB against a
40.0 floor).

**`texan_check` reports places NONE, body yes, deadline NO, next step NO**, and the last two are the
record's own state rather than a gap this deck could close. No claim carries a comment window, a
hearing or any dated door, so the deck spends no reserved red and carries no date anywhere. The body
was missing and is not any more: slide 4's dek now names the Department of Energy's Advanced Research
Projects Agency-Energy in full, where it read "the federal target" and a reader could finish the deck
without learning who funded it.

**The places answer was a gate limitation and Phase 17 fixed it.** `assets/geo/tx-places.json`
carries 254 counties, 67 CBSAs, 13 CSAs, 2 divisions and NO CITIES. `places_named` matched a city by
bare name at length over four, so the city of Houston was unmatchable and the only Houston in the
file is Houston COUNTY in East Texas. A Houston story reported places NONE. The gate now reads
principal cities out of each statistical area's delineated name, and across sixteen decks with a
`copy.json` it had been reporting no place on SIX that name Austin, Dallas, Fort Worth or Houston in
plain prose. **This deck now reports `places Houston`.** The deck was SCORED at places NONE, which
is the profile the judges graded, and it is recorded both ways rather than quietly upgraded.

## Phase 15, the panel, and it took three rounds

`panel_ready` exited 0 before a single scorer was spawned, which is the rule and is why the
judges spent themselves on craft and on claims rather than on plates over sentences.

| round | integrity | craft | reader | median | verdict |
|---|---|---|---|---|---|
| 1 | 6.694 | 7.10 | 6.14 | 6.67 | HOLD, 1 hard fail |
| 2 | 6.41 | 6.942 | 7.364 | 6.988 | HOLD, 1 hard fail |

**ROUND 1'S HARD FAIL WAS REAL AND IT WAS CHEMISTRY.** Slide 6's dek printed that the project's
name states the search space and it is not rare earths, under a claim rail reading c4 c7 c8. No
claim says it. Worse, the deck's own slide 3 refutes it: boride and carbide are ANION classes,
rare earth is a CATION class, and Nd2Fe14B, which frame 3 prints in lilac at the top of the
frame, is a rare earth boride. The project's name excludes nothing at all. The frame now reads
"The name states a chemistry and not a supply chain."

**ROUND 2'S HARD FAIL WAS THE SAME SENTENCE, IN THE RECORD RATHER THAN ON THE DECK**, and it is
the more useful of the two findings. The repair had landed on the frame and on the storyboard's
story line and nowhere else. `ledger/carousel/topics.json` still described the run's topic by it,
`ledger/carousel/artwork.json` still carried it as structural law 1, `claims.json`'s own `story`
field said "cut reliance on imported rare earths", and two of the storyboard's palette rationales
still justified the colour scheme by it. This ledger's own deck 9 entry states the cost in one
line, and it came true one run after it was written: **a ledger field is memory, so a refuted
reading left in it becomes the next run's premise.**

Every one of those surfaces is rewritten and each carries a note saying what it read before and
why that was wrong. The old wording survives only inside those notes, as a quotation of the
error, which is the point of them.

**What the judges also moved, round over round.** The cover's five percentages came off, because
slide 5 is the declared turn and it was restating figures a reader had already met four slides
earlier. Slide 5's hook rendered c17's "was" as "is" directly beneath the verbatim quote carrying
the tense. Slide 3's stop bar, added to answer a truncated quote, read as a dash to two judges and
came off, and the acceptance item that demanded it was rewritten rather than left to contradict
the frame. Slide 9's dust free patch and the lamp pool were the same region, which four judges
across two rounds read as light rather than as absence, so the lamp's core moved into the near
corner and the patch now sits on its flank.

**What was NOT taken at round 3, and why.** Slide 2's bore carries no value break where the
magnet's top face meets the bore wall. Slide 6's engraved field is a cross hatch mesh in bands
rather than tool paths. Slide 7 is the thinnest frame in the deck. Slide 8's single continuous
wire still joins two figures the deck says may not be compared. Each of those is a RE-PLAN and not
a repair, and this project's own record says twice that a later round's hard fails were
manufactured by an earlier round's repairs. They are the next deck's work and they are written
into `avoid_next`.


## Phase 17, the retro and the upgrade lane

**Three gates shipped, each carrying the defect it exists for, each with a self test that replays
that defect and goes red without the fix, and each replayed across the seventeen shipped decks
under `runs/carousel/` so it does not fire on correct work.**

- **`texan_check` reads principal cities out of the statistical area names.** See above. Six decks
  in sixteen were reporting no place while naming a Texas city in plain prose.
- **`label_guard` masks the wordmark from `config/brand.yaml` as a PHRASE.** Its `FURNITURE` set's
  own comment claimed it held the deck's own furniture and it held none, so a colophon that puts
  the mark in the same element as a claim id had TEXAS, AI and DOCKET read as three unsupported
  labels. A phrase and never words, so a lone `AI` beside a claim is still checked. 2026-08-30 goes
  from 35 findings to 32 and every other deck is unchanged.
- **`aggregate_check` stops reading a count of one as a tally.** "Which one does ARPA-E publish?"
  was reported as a computed count of the word "does", and this run reworded a caption around it.
  Over every published surface of seventeen decks the shape fires ten times with a numeral of one
  and NONE of the ten is an aggregate. A scale word after the numeral keeps the count, so "one
  hundred filings" stays declarable.

**`quantifier_check`'s mechanical extraction was NOT built and the measurement is why.** The last
run filed it for this phase. The current pattern raises 18 findings across 16 decks and the widened
word set raises 240, about fifteen a deck. The defect is real, and this run's own "No material named
yet." and "Three years is the only schedule in the record" are both outside the pattern, and the
naive fix is a row that is always red.

### THE INCIDENT, AND IT IS THE MOST USEFUL THING PHASE 17 PRODUCED

**The upgrade lane ran `git checkout -- ledger/docket.json`, which is the daily lane's file, and
destroyed the record correction the daily lane was making at that moment.** It read an equal
insertion and deletion count, 12,727 each, as a stray whitespace reformat. **Equal counts are also
what a same length string edit produces.** `site_fresh_check` went red one step later because
`docs/` held the new wording and the ledger held the old, the tree was made consistent by rebuilding
`docs/` from the reverted ledger, and commit `6bd8f89c` therefore says it struck a reading that
`ledger/docket.json` still carried. It was recovered from the built page and re-applied.

Two things follow and both are written into the backlog.

1. **The two writers of `ledger/docket.json` disagree about its indent.** `reverify.py` writes two
   spaces and `docket_build.py --promote` writes one, so the file reformats itself depending on
   which touched it last, and that is what made a same length string edit indistinguishable from
   noise at a glance.
2. **Two lanes running at once share one working tree.** The ownership map is a commit time guard
   and it says nothing about a checkout. Nothing stopped this and nothing would have.
