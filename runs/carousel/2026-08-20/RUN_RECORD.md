# Run record, August 20th, 2026

Routine: `prompts/daily_routine.md`. Actor `daily`, with one `human` lane detour at wake and
one `upgrade` stamp at Phase 17. Branch `claude/daily-2026-08-20`.

---

## A gate was red at wake, and this run did not own the fix

`python3 scripts/shared/guards_local.py --fast --only Ownership` exited 1 on a clean checkout
of `main`, before this run had written anything.

The cause was not in this run's lane and not in anybody's recent work. On August 19th the
Ownership step in `guards.yml` moved its branch name out of `run:` and into `env:`, closing a
command injection on fork pull requests. That fix was correct and it stands. `guards_local.py`
recognises a CI only step by a `${{ }}` expression in the step's `run:` block, and after that
move there was no expression anywhere it looked. The step stopped being classified CI only, ran
locally with `BRANCH_NAME` unset, and the runner exited 1 on every clean checkout from that push
onward. Nothing edited the broken file. Its own suite stayed green, because every case in it put
the expression in `run:`, which is the half that still worked.

The ownership map put `scripts/shared/guards_local.py` in the `human` lane, so Phase 0's
instruction to fix a red gate before anything else pointed at a file this run could not write.
**On the owner's explicit call during the run, the file moved to the `upgrade` lane and the fix
was made.** It went on a maintainer branch, which is the escape hatch the map already provides,
and merged as PR #122 with CI green.

`upgrade` and not `daily` is the deliberate part. It is not a gate, it is the thing that runs the
gates, and it reads `guards.yml` rather than keeping its own step list, so it cannot be loosened
to make a run pass. Loosening it only stops steps running, which shows up as a smaller step count
in its own summary. Every other file under `scripts/shared/**` is unchanged and maintainer owned.

`GATE_LESSONS` 38 carries the shape, which now has enough instances to name. **A consumer reading
one of the several places a producer may write.** Same family as entries 13 and 30 and the
`craft_floor` bands bug.

After the merge, `guards_local.py --fast` on this branch: 73 passed, 11 skipped, exit 0.

---

## Discoverability signoff

Six surfaces, each opened and looked at, on the build from this run's ledger.

- **One decision's card, opened as an image.** `docs/og/tx-2026-0077.png`, the newest item.
  LOOKED AT. It renders, wraps on four lines and truncates as `hearing on how...`. The cut lands
  on a whole word and the word is a function word, which is the weakest place to stop. The
  wrapper cuts on width and the title is long, so the cure is a shorter title rather than a
  change to the card. That is the record's to give and it is noted below.
- **`/questions/`, read as a reader.** LOOKED AT. Two findings. The card for `Where a comment
  window is open` prints `06`, zero padded to two digits, on the one question with a single digit
  answer. Every other card is naturally two digits so nothing exposed it before. It reads as a
  typo on the most actionable question the site asks. Second, the twelve entries are noun phrase
  labels rather than questions, on a page headed `Questions this record answers`. Both live in
  `scripts/site/site_build.py`, which this actor does not own. Proposals, below.
- **The `Open right now` section of `llms.txt`.** LOOKED AT. Twelve entries. Cross checked against
  the windows re-verified in Phase 3 and they agree. It is also what caught the duplicate this run
  admitted, because League City appeared in it twice under two ids.
- **`/sources/`, the record's own report card.** LOOKED AT. The share reads 209 of 281 claims
  resting on a primary document, across 109 documents from 55 publishers. Every claim this run
  added cites a primary document, so the share did not fall. The top publisher is
  `interchange.puc.texas.gov`, the commission's own filing system, which is a primary source and
  is what the record should lean on hardest. Its document list reads as documents.
- **`/topic/`, one card against its own page.** LOOKED AT. Surveillance and policing, the beat this
  run landed in, is on the hub. The per beat figures sum to the front page counter.
- **`/place/`, for the place this run landed something in.** LOOKED AT. Galveston County is on the
  hub with a count of 2, which matches the two entries behind it.

---

## Phase 7 instruments

| check | exit | note |
|---|---|---|
| `gridwatch_pagecheck.py` | 0 | current, and holding its promises |
| `waterwatch_pagecheck.py` | 2 | one finding, and it is a FALSE POSITIVE. See below |
| `waterwatch_page.py --self-test` | 0 | |
| `media_check.py` | 0 | |
| `schema_check.py` | 0 | |
| `og.py --self-test` | 0 | |
| `favicon.py --self-test` | 0 | |
| `truetype.py --self-test` | 0 | |
| `indexnow.py --self-test` | 0 | |
| `seo_check.py` | 0 | |

**The water page advisory is a false positive and worth writing down carefully.** It reported
`supply verdict language on a page that promises never to publish one: safe`. There is no supply
verdict on that page. The checker matched the substring `safe` inside `'unsafe-inline'`, in the
Content Security Policy meta tag added by the recent CSP work. It reads the whole document rather
than the reader visible prose, so a security header it has never heard of tripped a rule about
editorial language.

It is advisory and never blocks, which is why this is a note and not an incident. It is also the
second time in two days that a change in one place has made a checker somewhere else report on
something that is not there. `scripts/gridwatch/` belongs to cron and is off limits to this run,
so this is a proposal.

---

## Proposals, for a maintainer session

1. **`waterwatch_pagecheck.py` should read reader prose, not the whole document.** Strip `<head>`,
   `<script>`, `<style>` and meta content before matching the verdict vocabulary, and match on
   word boundaries rather than substrings. Either change alone would have prevented today's false
   positive. A self test case that feeds it a CSP header containing `unsafe-inline` and asserts no
   finding would keep it prevented.
2. **`/questions/` prints `06`.** The count is zero padded to two digits, which is invisible until
   a count is a single digit. It is on the card for the open comment windows, which is the most
   actionable question the site answers.
3. **`/questions/` entries are labels, not questions.** `What each decision is` and `Who decides`
   are the shapes the answers are computed from. As reader copy on a page headed
   `Questions this record answers` they read as a table of contents.
4. **The record has no gate against admitting a decision it already carries.** This run admitted
   League City's November 3rd ballot as a new item when it was already on the record as
   `tx-2026-0048`, from a stronger source. `docket_ingest` and `--promote` check schema, house
   style, geography, numerals and staleness, and neither asks whether the decision is already in
   the record under another id. It was caught by reading `llms.txt` during the signoff, which is
   luck rather than a mechanism. A candidate sharing a decider, a key date and a subject with a
   published item should be held for a human sentence rather than admitted.
5. **The four rooms have no `ballot`, and `DATE_KINDS` has no `election`.** Two items admitted this
   run go to voters on November 3rd. Both are filed as `open_comment` closing on election day,
   which is true about when a Texan can still act and imprecise about how. The schema is in
   `docket_build.py`.
6. **A long item title truncates on a function word in its social card.** See the signoff above.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 16 verified claim(s) |
| render         | PASS   | 7 slide(s) |
| qa             | WARN   | 0 fail(s), 2 warn(s) |
| aggregates     | PASS   | 3 declared and re-derived |
| assembly       | PASS   | 7 slide(s), 2.72 MB, vector |
| score          | ABSENT | score.json not written yet |
| dossiers       | PASS   | 34,896 chars planned |
| caption        | PASS   | 136 words |
| craft floor    | WARN   | 7 frame(s), median 1033, floor 186, 2 quiet |
| plan vs render | WARN   | 6 of 44 acceptance item(s) checkable |
| texan          | WARN   | places NONE / body yes / deadline yes / next step yes |
| absences       | WARN   | 1 of 5 scoped to a named document, 4 unscoped |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->


---

## The record

**Worklist cleared in full.** Five items due, five re-verified against a primary source, every one
carrying a dated line whether or not it moved. `docket_staleness` reports 0 due after the pass.
Nothing rotten. The backlog held at its three by-name exemptions and did not grow.

**A wrong public fact was corrected.** The record said the utility commission's August 21st open
meeting no longer named Docket 59315, Oncor's 765 kV Dinosaur Switch to Longshore Switch
application. The agenda published for that meeting names it as item 3, marked for discussion and
possible action, and names a second Oncor 765 kV application as item 2.

The reading was wrong because the calendar feed's description field never carries a docket number
for any entry, so its absence there says nothing about what will be taken up. That is now written
into the item's editor note, into the feed item's own access note and into the field log.

**Four items admitted, three published.** tx-2026-0075 Pflugerville's November election on charter
amendments including a section on the city's use of artificial intelligence, tx-2026-0076 PUCT
Docket 59029, Oncor's second 765 kV application across ten west Texas counties, and tx-2026-0077
Senate Transportation's August 25th hearing on driverless vehicle deployment under SB 2807.

**The fourth was withdrawn before it published, and that is the run's own defect.** tx-2026-0074
was admitted as League City's November ballot when the record already carried that decision as
tx-2026-0048, from the city's Legistar record, with the ordinance number and the motion that
passed it. It was caught by reading `llms.txt` during the discoverability signoff, where League
City appeared twice under two ids. That is luck rather than a mechanism, and the proposal is
above.

## The deck

Story `tx-2026-0048`. League City put its police license plate reader cameras on the November 3rd
ballot and the first clause of the ballot question tells the voter the result is a nonbinding
statement of voter preference.

**Two rounds of a three judge panel.** Round one: craft 7.23 ship, reader 6.82 stop, integrity 6.81
stop. Four hard fails across two judges, and the routine's rule is that any one judge's hard fail
stops the deck whatever the median says.

**What the panel caught that every machine gate had passed.**

- **An unsourced fact on a published frame.** Slide 4 read "Galveston County is crushed oyster
  shell. Pflugerville sits on the Blackland Prairie, the state soil." It carried two claim ids and
  neither claim mentions soil. Nothing fetched this run supports it, and the integrity judge noted
  Galveston County's mapped soils are coastal clays, so it was probably also wrong. It came from
  the storyboard's own palette rationale, grafted from a losing treatment, and nothing between the
  palette and the frame asked whether a colour's justification had become a claim. The frame now
  states the county sets, which the record does hold, and a structural law was added: the palette
  is craft and never evidence.
- **The record of what the deck says had stopped describing the deck.** `copy.json` was
  hand-written, slides were re-rendered after it during repair, and two strings reached slide 9
  having passed through no gate. `copy.json` is now DERIVED from `render/render_report.json` and
  declares `derived_from`, so the drift is impossible rather than merely checked for.
- **A frame all three judges wanted gone.** The old slide 6 read as a bar chart, which was its own
  dossier's named risk, and it argued slide 5's point a second time in a weaker drawing. It was
  cut and the deck renumbered to eight.
- **Three smaller integrity repairs.** Slide 5 said the ordinance "passed" where its quote records
  a motion made and seconded. The closing frame implied the camera question is on the August 25th
  agenda, which nothing establishes. c16's own note said the address and date were asserted on no
  slide while the closing frame set both at 38px.

**Two defects the showrunner introduced and the machine caught.**

- **A fabricated numeral in a director brief.** One lens brief said the two cities are eleven miles
  apart. They are two metros apart, the figure is in no claim, and a treatment director refused to
  build on it. No distance appears anywhere in the deck, and slide 4 draws the dimension and labels
  the gap "not measured" rather than dropping it.
- **A wrong computed count in the largest type on a frame.** Slide 2's hook read "Read the first
  six words." The clause is seven words. `aggregate_check` refused the undeclared count, the count
  was then computed in code from claim c1's own quote, and both frames were corrected.

## Craft findings for the next run

**Contrast was computed before any code and it changed a frame.** The winning treatment planned
Section 2.03's body in the dropout green on the ballot stock. That measures 1.48 to 1. It is now a
printed shape and never type on paper. The reserved red measures 5.12 on stock and 2.89 on the
soil, which is why the close can carry it and no other frame could.

**`plan_render_check` went from 0 of 46 checkable acceptance items on the last deck to 8 of 58
here, and the declared-colour half of it caught three plan-versus-render disagreements** before any
judge saw them, including two frames whose plans named a mark colour the frames could not legibly
draw.

## Two more proposals, from the deck side

7. **`plan_render_check` hand-parses the storyboard's YAML instead of loading it.** An acceptance
   item written the way `SLIDE_DOSSIER_SPEC.md` asks, quoting the exact string, needs YAML escaping
   for its quotes, and the escape survives into the needle as a literal backslash. The item can then
   never match a render. Six of this deck's nine items failed that way on the first pass and the
   fix was to requote them, which works and hides the defect from the next run. The gate rewards
   exactly the habit the spec mandates and cannot pass it. It lives in the `upgrade` lane.

8. **The engine's thumbnails are re-rendered rather than downscaled from the shipped PNGs.** Round
   one's reader judge found a broken frame sitting behind a clean thumbnail and could not tell which
   was the product. A thumbnail that is a separate generation of the deck cannot be evidence about
   the deck. Downscale the render.

9. **`SKILL.md` documents `fetch()` for the committed geodata and this Chromium refuses it**, with
   `URL scheme "file" is not supported`, which `--allow-file-access-from-files` does not reach. The
   slide rendered in 407ms with an empty canvas. `render.py` caught it as an error rather than
   shipping a blank frame, which is the gate working. `XMLHttpRequest` still honours the flag and is
   what slide 4 uses. The skill's example should change.

## A process fault this run committed twice

**The artifacts were changed while the panel was reading them.** Round one's reader judge reported
a broken frame behind a clean thumbnail and a `copy.json` describing a different deck. Both were
true when it looked, and both were mid-repair states rather than the product. It was right to stop
the deck and its root-cause reading was correct, but two of its four findings were about a moving
target.

Then this run did it again, reassembling during round two.

**The fix is not a gate, it is an order of operations.** Freeze `out/<date>/` before the panel is
spawned and do not touch it until every judge has returned. A judge reading a directory that is
being written is not a second reading of the deck, it is a race. This is recorded as an instinct.

## The variety ledger repeated a fault its own predecessor documents

Round three's reader judge found the 2026-08-20 artwork entry written against the eight slide plan
rather than against the renders. It recorded `slides: 8`, a technique that never shipped (the three
county polygons), the red on a slide number that does not exist, an eight move camera line, and a
`bespoke_closest_pair` naming a file that was deleted. The county frame that was actually cut was
recorded as shipped.

**The 2026-08-19 entry documents this exact fault at length, in its own `renumbered_after_the_cut`
field, and states the reason it matters.** A technique recorded there that never shipped blocks
tomorrow from a drawing nobody made, and leaves the drawing that ran unrecorded. The very next run
reproduced it.

Twice is a pattern and the cause is the same both times. **The entry is written from the plan while
the deck is still moving.** The fix is the same one this run applied to `copy.json` after the second
panel: write it from `render/render_report.json` after the last render, never from the dossier. The
entry has been rewritten from the renders and the proposal is below.

## Panel round four, and the finding all three judges reached alone

Round four returned no hard fail from any judge. The reader scored 7.05 and shipped, craft 7.27 and
shipped, integrity 6.72 and did not, on the number rather than on a condition. Three judges reading
the deck separately arrived at the same sentence.

**Seven slides about a referendum and the election date was on none of them.** The reader put it
hardest. A reader who never opens the caption is told at 96px that a November vote is nonbinding and
is never told when it is, which makes the product complicit in the thing it is reporting. November
3rd, 2026 is quoted verbatim in c2 for League City and in c12 for Pflugerville, so putting it on a
frame completes a claim the deck already leans on rather than adding one. It is on frames 3, 4 and 7
now, in ink, and it takes no red on any of them, per the structural law that until today governed
frames which did not exist. That is the shape of the fault. **A law written for a frame is not a law
about the deck**, and this one read as satisfied for six frames because the thing it governed was
never drawn.

**Slide 4's dek was a weld.** It read "Ordinance No. 2026-27, moved and seconded on first and final
reading, August 11th, 2026." c16's quote gives the ordinance number and the reading. c2's quote
gives the date. Nothing this run fetched puts that number on that date, and c13's editor note shows
the run knew how to record an unquoted API field and did not do it here. Two true halves welded into
an assertion no source makes is harder to catch than a fabrication, because every part of it traces.
The dek is now the election date, which both bound claims quote, and it answers its own hook for the
first time.

**The closing frame said by layout what its sentences refused to say.** c16's note is explicit that
the record does NOT establish the license plate reader question is on the August 25th agenda, and
the copy stayed inside that fence. The composition did not. A bare OPEN MEETING in the reserved red,
under an eyebrow reading "where it gets decided", sends a reader to a meeting this record has not
seen the agenda for. **No gate can see a verdict delivered by composition**, and no gate saw this
one. The label is now the record's own wording, next regular meeting, and both dates stand on the
frame with the red spent on one of them.

## Three ledgers were carrying the plan rather than the run

The 08-19 entry documents this fault. The 08-20 entry was rewritten from the renders after round
three found it again. Round four found it a third time, in three more places, and one of them was
inside the very entry that had just been repaired.

- **`artwork.json`'s `structural_laws` was a copy of the plan.** Its second law said the two grounds
  never mix, and three shipped frames put stock value on the dark ground: the charter's lit course
  on 3, the ballot card on 4, the bounded figure on 5. The renders had already contradicted the law
  when the entry claiming to be written from them recorded it as held. The law is amended, in the
  storyboard and in the ledger, and says what the deck does: a frame's GROUND is stock or it is
  houston_black and never both, and lit paper is not a ground.
- **`topics.json` listed three counties** for a deck that cut its only cartographic frame precisely
  because no claim names a county, and says so in its own storyboard. Left there, the dedupe gate
  would compare future runs against entities this record never established.
- **`captions.json`'s `structures_recent`** read ledger, pivot, question and answer, when the last
  three shipped structures were ledger, two columns, question and answer. One hand edit dropped a
  structure that IS off the table and held one that is not, so the exclusion list handed to the next
  caption room was wrong in both directions. All three lists are now recomputed from `entries`.

## The line break that hid the largest numeral in the deck

Every hook in this deck is set with a manual `<br>`. In `textContent`, which is what `copy.json` and
every gate read, a `<br>` with no space before it closes the two words up. Slide 2's largest line
reached `aggregate_check` all run as "Read the firstseven words." and the gate saw no aggregate on
that frame. The single most important computed numeral in the deck, the one whose first render said
six and had to be corrected to seven, was invisible to the gate that exists to catch exactly that.

Every `<br>` in the deck now carries a space before it. The space renders as nothing, because a
trailing space before a forced break is collapsed, and it makes the string in the record equal the
string on the frame. `aggregate_check` now reports four computed figures where it reported three.

**This is the fifth entry in a row with the same shape.** A rule stated in one place, a surface
keeping its own copy, and nothing in between checking they agree. Here the two copies were the frame
and its own `textContent`, which is as close as two copies can possibly be.

## The permission interruption, and where it can and cannot be fixed

The owner interrupted twice in this run because an unattended routine stopped to ask. The committed
`.claude/settings.json` already sets `defaultMode: bypassPermissions` and has since 2026-08-11, and
its own comment explains why: a prompt in an unattended container has nobody to answer it, so the
run does not fail, it wedges until the container is reclaimed.

What was still asking is not the permission mode. It is the Bash SANDBOX, which asks to be escaped
when a command writes outside the working tree, and this run wrote its scratch scripts to a system
temp directory. Every scratch file now goes in `out/<date>/tmp/`, which is gitignored and inside the
tree, so no escape is needed and nothing has to be approved.

`.claude/settings.local.json` is not the fix. It is gitignored, so it dies with the container and
the next run starts without it. That was already true of the copy this run wrote at wake.

**The one file that could hold a permanent fix is the one file this repo's law says an automation
may not edit.** `ownership.yaml` puts `.claude/settings.json` under the constitution, alongside
`CLAUDE.md` and `prompts/daily_routine.md`, with the note that no automation edits its own
permissions because that is the rule which makes every other rule hold. That is not a mistake in the
map the way `guards_local.py` was. It is the map working. So the sandbox change above is made, and
anything further is written down as a proposal rather than taken.
