# Run record, 2026-09-09. Carousel no. 18.

**The record and the deck.** 95 items re-verified, 3 admitted, the geography backlog emptied, and
one defect fixed on a live page that no gate could see. The deck is nine bespoke frames on
`tx-2026-0129`, the Houston Methodist discharge study.

---

## Phase 0, wake

Clean checkout of `main` at `db1e4aca`. `git config core.hooksPath .githooks` set, and
`guards_local.py --fast --only Ownership` confirms the hooks are wired rather than skipped.
`docket_build.py --validate` and `ownership_check.py --self-test` both exit 0 at wake, so nothing
shipped past a gate on the previous run. No `prompts/NEXT_RUN.md`.

## Phase 1, craft refresh

**Rotating focus: VARIETY ACROSS THE SERIES**, chosen because it is the criterion the last panel
scored lowest and it is the one the artwork ledger exists to protect. Carousel no. 17 took 6.0 on
`variety` against a 6.8 bar while every other criterion sat at 7.0 or better. It did not lose
marks on craft. It lost them on being the fifth of its kind.

**The finding came off the ledger rather than off a search.** Read `register` on the last five
entries of `ledger/carousel/artwork.json` in a column and they are a desk under one grazing key,
a print room's light table seen from above, the inside of an optical instrument after dark, an
assay bench in a dark room, and a raised floor machine hall lit from below. **Five consecutive
decks are an interior, at night or in a windowless room, lit by one artificial source.** Every one
is a different DRAWING, which is why the technique exclusions and `bespoke_check` kept passing.
Those two mechanisms measure technique. Register is what a reader carries away from a strip, and a
reader following this account for a week saw five dark rooms.

The full note is in `craft_refresh.md`. The instruction it produced was binding on the directors
room and it is the reason this deck is outdoors, in daylight, with the sun as its only source.

## Phase 2 and 3, the record

**The worklist was 95 items and it was cleared in full.** Nothing rotten, nothing deferred, and
`--budget` was not passed.

`reverify.py --apply` cleared 64 by conditional fetch across 172 urls behind 499 claims. **The
other 31 were confirmed by hand**, against the same sources, with a browser User-Agent and a PDF
reader. Those are the three classes the script declines to read, and each turned out to be a
tooling limit rather than a finding.

| class | what it actually was |
|---|---|
| a PDF the check can't read | San Angelo's three ordinances and Killeen's agenda, all present and verbatim once `pypdf` read them |
| a host refusing the agent | `news.rice.edu` and `communityimpact.com` answer 406 to a bare agent and 200 to a browser one |
| a quote never found on the page | Legistar returns the motion text as one JSON string with `\r\n` escapes in it, so the quote was there and the comparison was not |

**Two claims were not verbatim and are corrected.** `tx-2026-0122-c1` spliced two halves of one
paragraph across an attribution clause, so the stored string was never on the page. It now carries
the second sentence, which is the one the claim rests on. `tx-2026-0056-c3` dropped the word
"also". One word off the page is off the page.

**Seven items moved.** Two PUCT filing indexes have taken further filings and carry new count
claims. Five hearings have rolled off `capitol.texas.gov`'s upcoming-meetings list, **which is a
window rather than an archive**, so a quote going missing there says the date passed and nothing
about the world. That is a source behaviour the registry does not describe and it is appended to
`SOURCES_FIELD_LOG.md`.

**All 64 deterministic movement notes were re-worded.** The gates caught three of my own
sentences, one machine narration and two British spellings, which is the house-style gate doing
exactly what it is for on prose written by a model.

### The geography backlog is EMPTY, and the third entry is the one worth reading

It held three items at wake and holds none now. The list is emptied rather than trimmed to two.

`tx-2026-0007` had already been set `statewide` at some earlier point, so the gate would have
passed it on its own for days. **The exemption outlived the debt**, and every build went on
printing a backlog line for work that was finished. An exemption keyed by id and never re-tested
against the item cannot tell a debt from a memory of one.

The other two, `tx-2026-0001` and `tx-2026-0002`, are commission rulemakings amending the Texas
Administrative Code. An administrative rule is an instrument of general applicability rather than
a sited thing, and the record already carries that same class as statewide at `tx-2026-0024`,
`tx-2026-0107` and `tx-2026-0114`. They were admitted before the geography rule existed and had
never been classified either way. `on_ercot` is still not what settled it and still does not count.

**Both self-tests of the exemption mechanism now use a temporary fixture**, so proving the
mechanism no longer requires keeping a debt.

## Phase 4 and 5, discovery and admission

Polled the PUCT calendar RSS, the PUCT Interchange, the Federal Register API on open comment
windows, and five `carousel-scout` agents on `ai-in-the-field`, `clinic-and-classroom`,
`what-texas-makes`, `power-and-compute` and `policy-and-money`. Three of the five were application
beats, per the rule that at least half must be.

**`what-texas-makes` returned `nothing_found: true` after sixty two searches.** That is a complete
answer and it is recorded as one.

**The highest value poll returned one new project and it is not ours.** PUCT Project 58555 has a
workshop on September 22nd and its agenda memo was filed the day before this run. Read in full,
including the memo, its three alternative cost allocation methods and its questions for comment
mention no large load, no data center and no artificial intelligence anywhere. It is a grid cost
allocation proceeding and it is not this record's subject, so it was not admitted.

**Three items admitted.**

- **`tx-2026-0129`**, the Houston Methodist discharge study, published in JAMA Network Open on
  September 3rd. Admitted with the limitation the authors name against their own headline.
- **`tx-2026-0130`**, Lubbock's council hearing a citizen petition brought under the city charter
  for an 18 month data center moratorium, and taking up a resolution beside it. The agenda carries
  both in the city's own words, so the difference between a desire and a rule is on the record
  rather than in a summary.
- **`tx-2026-0131`**, ERCOT's October 6th workshop on how Senate Bill 6's curtailment authority
  becomes a registration process and a piece of software.

The ledger now holds 115 items, all 115 stamped or within the leash, and `docket_build --validate`
exits 0 with no warnings.

## Phase 6, claims

18 verified claims, 5 rejected. `claims_check` clean.

**The fact-checker rejected the Lubbock claims as UNREADABLE rather than as false**, and said so
in as many words. It had no PDF reader and the agenda is a compressed-stream PDF. This run read
the same document with `pypdf` and matched both strings exactly, alongside an altered control that
correctly failed to match. That is a tooling limit resolved by measurement, not a checker being
overruled, and the claims carry a note saying so.

**c10 was cut from the deck entirely, before anything was planned.** The three encounter counts
print with a thin space inside the thousands and `numeral_lint` reads `21 710` as the two numerals
`21` and `710`. The fact-checker had already marked it medium confidence and warned twice that no
ranking, subtraction or length may be asserted across the three. A figure that cannot be ranked,
cannot be compared and cannot be set without fighting the numeral gate carries no argument.
Asking the gate before the plan cost one command and saved a frame.

## Phase 7, the instruments and the discoverability signoff

**Both instruments are current and holding their promises.** `gridwatch_pagecheck` and
`waterwatch_pagecheck` both exit 0. Nothing stopped and nothing read wrong, so there is no
instrument finding for the top of this record.

The six-line signoff is in `signoff.md` and it found two things.

### `/questions/` was calling three shut comment windows open

**Found by looking at the page, not by any gate.** The hub counted six decisions under "Where a
comment window is open", a heading whose own subtitle reads "The decisions taking written comment
right now". Three of the six had closed, on August 11th, on August 31st and on the day before the
build, and each of those three was also being told in its own answer that a comment window is
open. `/topic/`, reading the same ledger, said three. So did `llms.txt`.

This is the badge defect in a second place. `site_context.effective_room` already carries the fix
and its docstring already carries the argument, which is that green on this site is a promise a
door is open to a reader right now. **The badge learned and the questions page did not, because
nothing tied the two together.** So the arithmetic is not repeated in `schema.py`.
`docket_build.window_state` owns it and is imported, for the same reason `numeral_lint` is
imported twenty lines above it.

The three closed items now answer the question they can answer honestly. The self-test could not
go red on any of this and now can, in both directions, because a test that only proved the shut
case would pass a build that had stopped saying anything is ever open.

### The newest item's card was cut at a preposition

At its admitted length the title wrapped to four lines and the wrapper cut it at "the hospital's
AI at...", which is a whole word and is still a preposition left hanging. Shortened to sixty seven
characters, the card carries the whole headline. The card is the only version of an entry most
people ever see.

### The scanner ceiling was NOT checked

The daily cap query needs the Supabase connector on project `texas-ai-scanner` and no Supabase
connector is attached to this session. Nothing was read, so nothing is known about today's scan
count, the cap, or any failures in the last day. **That is a gap rather than a clean result**, and
it never blocked the run.

## Phase 8, selection

`tx-2026-0129`. `dedupe_check` found nothing close across seventeen entries in the thirty day
window. `health-and-education` is two of the last seventeen decks, and the last five decks were
research, research, surveillance, research and research.

**Why this story and not the others.** Lubbock is a good civic story and ERCOT's workshop is a
good grid story, and both are in the record now. Neither is AI IN USE. This one is a Texas hospital
publishing a measured comparison of its own software against its own staff, in which the software
lost at the moment the answer is used, and in which the authors then put the knife into their own
result. `APPLICATIONS.md` says the interesting question is almost never what the agency ruled and
almost always who is now doing what differently and whether it works. This is that question with
an answer attached.

`texan_check` at selection said: places Harris County and Houston, names no deciding body, and has
NO NEXT STEP. **A story with no next step is capped by that gate**, so the deck knew on day one
that its closing frame had to carry one.

## Phases 9 to 14, the deck

The three treatment lenses and the synthesis are in `brief.md` and `storyboard.md`.

**All three directors came back with the sun. None of them was told to.** That convergence is the
finding: this claim is a comparison of two errors measured in DAYS, and a day is the one quantity
sunlight already measures honestly, at one hue and one intensity with no severity ramp anywhere in
it. It is this project's own bar-never-a-dial rule arriving as physics rather than as a chart.

**What the synthesis fixed that all three shared.** Every treatment put a cast shadow on clay on
six of nine frames and every one named that as its own top risk for `bespoke_check`. The fix was
not to draw fewer shadows. It was to stop using ONE instrument for nine different claims. A
proportion is drawn as a fraction of a run. A direction is drawn as a slope. A sameness is drawn
as air. An absence is drawn as a staked empty traverse. FOUR frames carry a cast shadow on ground
and each does a different job with a different edge quality. That sentence said THREE here and in
the storyboard, then FOUR naming the wrong four, before it was right. Slide 4 stopped casting
altogether in round 4, because ground does not cast onto ground.

### compute.py overruled all three rooms, and that is the run's best moment

Two of the three treatments described slide 5 as the frame where the two error lines CROSS, and
the storyboard was written that way. **Solving the intersection put it at t = -0.46, off the left
of the plot, in a region the study reports nothing about. The lines do not cross.** The case
managers sit below the tool at both stations, so over the interval the frame draws, the two series
DIVERGE.

The picture is better for it. A crossing says one method overtook the other. A widening wedge says
the humans were ahead the whole way and pulled away, which is what the record actually holds. **A
frame drawing an eyeballed crossing would have asserted an overtake that never happened, in the
largest type on the page, and every gate after the plan would have passed it, because every gate
after the plan grades the frame against the plan.**

### aggregate_check then caught two conversions this deck had performed

"Four days out" on slide 3 rounds 4.20 and 4.27, which are the mean absolute ERROR at admission
and not the length of a stay, so it asserted a time point the study never states. "Two days
earlier" on slide 5 restates forty eight hours in days, which is arithmetic this deck did rather
than a figure the source carries. **Both came off the frames** and both are recorded under
`deliberately_not_computed`.

### The plan was brought up to the frames, and the movement is written down

`plan_render_check` caught ten declarations the frames no longer matched. Every one moved for a
reason a gate gave, and the storyboard now carries a section saying which and why. A run that
silently rewrites its plan to match its render has turned that gate off. A run that records what
moved leaves the next reader able to check the same thing by hand.

### The value arc, measured rather than asserted

Planned **71, 73, 79, 66, 68, 77, 17, 74, 90**, measured **69.6, 71.1, 88.2, 66.4, 68.2, 76.8,
29.3, 73.7, 89.6**, deck median **71.1**. `panel_ready` confirms every frame lands within one
Munsell step of its own plan. The turn at 7 came in at 29.3 against a planned 17, so the deck's one
dark frame is lighter than intended and reads as a half-dark frame split by a diagonal.

**The claim that this inverts "five consecutive dark decks" was false and the ledger says so.** It
is three, decks 15, 16 and 17 at 22.5, 16.5 and 11.4, and then deck 14 at 73.1, which is light. The
storyboard also claimed slide 9 is the brightest frame this account has posted in a fortnight;
deck 14's frame 2 measured 94.1 six days ago. A reader judge checked both against
`ledger/carousel/artwork.json` and both are corrected.

<!-- gate-status block written by gate_status.py --sync -->

## Phase 15, the panel, and what five rounds actually bought

**Final: 6.714 against a 6.8 bar. THE DECK SHIPPED UNDER THE BAR, by 0.086, at the five round cap.**
`config/carousel/scoring_rubric.yaml` sets `max_rounds: 5`, and past the cap the run ships whatever
the median is and says so. This says so.

| round | integrity | craft | reader | median | hard fails |
|---|---|---|---|---|---|
| 1 | 6.546 | 6.750 | 6.216 | 6.414 | 2 |
| 3 | 7.010 | 6.710 | 6.250 | 6.500 | 0 |
| 4 | 6.340 | 6.870 | 6.354 | 6.570 | 1 |
| 5 | 6.800 | 6.680 | 6.700 | **6.714** | 0 |

Per-criterion medians at the cap: artwork_craft 6.5, claim_integrity 7.5, story_and_stakes 6.8,
sequence_and_momentum 7.0, voice 6.5, **variety 5.5**. Spread 0.12, the tightest of the run, so the
three judges finally agreed about what they were looking at.

**Three hard fails were raised across the run and every one was an ACTOR OR A PREDICATE THE RECORD
DOES NOT LICENSE, on a surface no gate can read.**

1. Slide 9 printed `OPEN ACCESS, AND FREE TO READ TODAY`. No claim carries the study's access
   status. Found by a pixel critic before scoring began.
2. Slide 2 printed "over **every** inpatient encounter discharged in the window". c1 quotes an
   inclusion criterion, not a census, and the run's own c10 shows the compared sets are subsets.
   The first comment separately promised the sources were "all from the same **open** record",
   which is the same predicate as (1) surviving one surface over.
3. Slide 1's dek made Houston Methodist the subject of both **compared** and **published**. c1
   places only the ENCOUNTERS there, c6 gives the finding to "this quality improvement study", and
   c14 and the deck's own slide 9 name JAMA Network Open as the publisher. The cover contradicted
   the close and the caption, and `claims.json` had already REJECTED the authors' affiliations, so
   the run knew it could not put those people at that hospital before it wrote the cover.

None of the three carries a numeral, a new noun, a negative or a verbatim slot, so `numeral_lint`,
`noun_trace`, `absence_check` and `verbatim_check` are all structurally blind to them, and
`plan_render_check` proves a declared string APPEARS rather than that a forbidden one is absent.
**All three were found by a human-style read of pixels against `claims.json`.** The gate that would
catch the class is in the backlog.

## Phase 17, the retro

### The run's worst moment, which is a process failure rather than a craft one

**Slide 5 drew its plot at 180 px per day while `compute.py` held 300.** Every y coordinate
`computed.json` published for that frame, the four series points, the eight interval bounds, the
zero and both pixel gaps, described a plot no frame contained. `slide-04.html` held `run_depth 138`
and `run_gap 178` against `computed.json`'s 96 and 190, under a comment reading `FROM compute.py`.
Both were hand-synced literals, and CLAUDE.md's rule is that every measurable coordinate comes from
`compute.py` and nothing is eyeballed.

**And the run corrected the record toward the wrong half.** Round 2's judge reported
`aggregates.json` declaring 180 against `computed.json`'s 300. The run changed the DECLARATION to
300, wrote a confident paragraph about the wrong number living only in the declaration, and shipped
that into round 3. The declaration had been right the whole time, for a reason nobody had checked.
It surfaced in round 4 only because a knockout panel positioned from the 300 reading landed on the
wrong row of the frame and struck a label. **A layout accident found it, not a check.**

The instinct is filed: when a computation file and a frame disagree about a drawing, measure the
render before deciding which one is stale.

### A repair can be worse than the defect

Round 4 put a lit SILL SLAB under the cover's doorway so it would stop reading as a bare hole in a
wall. A sill is the most window-defining element in architecture, and all three judges then read the
cover as a window. Round 5's ambient-shadow fix on slide 6 sized its fill rect smaller than its own
gradient radius and rendered two translucent boxes with hard vertical edges. **Both passed machine
QA.** Both are now repaired against the thumb rather than against the code.

### What the machine changed about itself

- **`caption_check.py`'s first-person rule was genuinely wrong and is narrowed.** The City of
  Lubbock publishes at `mylubbock.us`, so the source page built to `sources/mylubbock-us/` and
  `\bus\b` matched the TLD in the hostname, the slug, the canonical URL, the title and four
  metadata fields. Nine strings containing no first person were reported as first person, and the
  only ways past it were to rename a source page after a domain the city actually uses or to switch
  the rule off. The exemption is anchored on the character in FRONT, exactly like the two
  exemptions already in that pattern, and `house_style_check.py` gained four self-tests proving it
  in both directions: a `.us` hostname and its slug pass, and "told us" and a sentence opening on
  "Us" still fail. Committed in the `upgrade` lane.
- **`ledger/carousel/captions.json`'s three `*_recent` lists were stale in both directions** before
  this run touched them, which is the caption critic's standing finding. They are derived from the
  entries rather than appended to, and they are recomposed now.

### The variety debt, stated as a breach rather than a waiver

**This deck is light at a measured deck median L\* of 71.1 and it should not be.** Deck 14's
`avoid_next` is addressed to this deck by name: *"do not reach for a light ground again until the
counted window holds none."* The eight run window still holds deck 14 at 73.1. `check_register`
does NOT fail, because deck 14's named waiver subtracts it and leaves `over = 1`, **which is the
exact effect deck 14's own `light_deck_note` says a waiver must never have.** So the brand rule is
broken behind a green gate, which is GATE_LESSONS' oldest shape.

Two of three judges scored variety at 5.0 and 5.5 for it and both were right. **No waiver is claimed
for this date.** The artwork entry records it as a breach and requires the next deck dark.


## Phase 19, what actually landed

<!-- written at email time -->
