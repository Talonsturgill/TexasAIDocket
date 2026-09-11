# Run record — 2026-09-11

## THE RUN MERGED, AND THE WALL IT STOPPED AT IS GONE

**`ask_pack --self-test` goes red on this branch and the wall is real.** The core pack measures
**421,427 characters against a ceiling of 420,000**. Measured on both sides of the diff:

| record | items | core pack | verdict |
|---|---|---|---|
| `origin/main` | 123 | 410,847 | passes, 9,153 to spare |
| this branch | 127 | **421,427** | fails by 1,427 |

Four admissions cost 10,580 characters, about **2,645 an admission**, so `main` was **three
admissions** from this wall and this run made four. Nothing warned, because the pack has no
headroom probe of the kind `index_headroom` gives the index.

**This run did not fix it and the reason is the file's own line 26**, of both ceilings: *"Raising
either ceiling is never a fix for a red build."* The other routes are worse. Dropping a true
admission would corrupt the record to satisfy a cache ceiling. Rolling a family up does not
reach, because the register is 23,783 and the reservoirs 29,892 of 421,427, so roughly **364,000
of the pack is the decisions themselves** and rolling those up is the break-glass path ceasing to
be the record.

**It is the defect the file already wrote down**, on the other ceiling, in the comment under the
assertion: two runs in September held over 644 characters of the record's ordinary growth, and
the owner's resolution was to raise `MAX_INDEX_CHARS` against a measured bill. `MAX_CHARS` guards
the `ASK_RETRIEVAL=off` break-glass that nobody pays for on an ordinary question, so its cost is
not the index's cost. **That is the owner's call, and `scripts/site/ask_pack.py` is not this
lane's file.**

**ONE ACTION CLEARS IT.** Decide whether `MAX_CHARS` moves, or whether the pack gets rungs the
way the index has.

`browser-layout` is also red, and **this run called it wrong once before getting it right.**

The first reading was "a `play()` race, not this PR's, and the suite passes locally". It failed a
SECOND time on the next head with a different symptom, which is what made the real mechanism
visible. **One case fails, the last and widest**, 1920 by 1080: the poster reports real dimensions
and fits, and the VIDEO reports no width or height at all with its crops serialising as `null`,
which is `Math.max(0, NaN)`. `videoWidth` was zero at measure time.

**It is the fixture rather than the product, and `tests/video_fit.mjs` documents this exact failure
in its own comments**: Chromium on Linux reclaiming the one-frame local canvas during the final
wide-screen case. The 100 ms repaint timer added to stop it is not enough on the runner. The
remaining gap is a race between two round trips, because `waitForFunction` and `measure()` are
separate `page.evaluate` calls and the stream can die between them. The fix is to make the
measurement itself the thing that waits.

**Not pushed.** That file is `human` lane, and while the branch may stamp `human` for a defect it
is blocked by, fixing it buys nothing today because `ask_pack` blocks the merge regardless. The
stronger reason is that this run had already been wrong about this test once, and pushing an
unattended edit to somebody else's test on the strength of a second diagnosis is the
overconfidence this repo's history warns about.

**Why it is red here and green on `main` is a HYPOTHESIS and is recorded as one.**
`docs/videos/index.html` is byte-identical to main in this diff and the test routes every request
to local fixtures, so the subject is independent of the changes. What did change is that the
branch grows the site from 700 pages to 705, and the suites running before `videoFit` in the same
browser take measurably longer, the nav suite alone going from about 37 to about 49 seconds. A
longer-lived browser process makes the late fixture likelier to be reclaimed. That is plausible
and unproven, and a wrong explanation in a run record is worse than none.

---

## THE ASK PACK CEILING, AND THE ONE COMMIT THIS RUN STAMPED `human`

**`MAX_CHARS` was not raised.** The core pack got the rungs `index_fit` has had since
2026-09-09, and `scripts/site/ask_pack.py` is `human` lane, so the commit carries
`Actor: human` on the `branch_also_allows` grant. `ownership.yaml` asks a run that uses it to say
so here, so this is that.

**Why a run took it.** The owner directed the fix twice, and the map's own note says the grant
exists because a hardcoded refusal is one no map edit can answer with nobody watching. The run was
blocked on a file it does not own, which is exactly the case the grant is written for.

**The pack gets two rungs where the index gets three**, and the reason is a contract rather than
taste. The worker cuts this field into one block per decision and asserts there are exactly as
many blocks as decisions, which `workers/ask/test.js` runs from the other side. **A pack that
drops a body breaks a worker deployed by hand, by pasting, while this file rebuilds itself every
day.** So every decision keeps a block and the rung reduces what is INSIDE one. All 168 of the
worker's assertions pass against the new pack.

Today the pack measures 419,129 characters with one body reduced, and there is room for 1,090 more
decisions. **The ceiling can still go red**, and the self-test proves it on the case no rung can
give up: a record whose windows are all open reduces nothing and overflows at 1,851,922.

---

## A REVIEW BOT FOUND A FABRICATION THIS RUN HAD ALREADY COMMITTED

**Six findings arrived on the pull request after the first push. Every one was checked against
the source and five were real.** The first is the serious one and it is the kind of defect this
whole project exists to prevent.

**`compute.py` invented a hole in the standards.** Its heading pattern was
`\((\d+)\)\s+([A-Z][A-Za-z ,\-&]{8,120}?)\.\s*The student`, and the character class has no
colon in it. The document prints **`(6) Budgeting: Spending and Planning.`**, so that heading
never matched, chapter six never entered `knowledge_numbers`, and `knowledge_missing` came back
as `[6]`.

**Slide 2's entire centrepiece was that gap.** Its hook read *"Nine numbered chapters. There is
no sixth."* and it cut a void clean through a wall to draw it. **The standard skips no chapter.
There are ten.** The frame is rebuilt rather than relabelled, and it now draws ten filled cells
with the three that carry the machine as the only ones the light reaches.

**The public record never carried it.** `tx-2026-0142` says "three separate chapters", which is
true, and publishes no chapter count. The falsehood was confined to the deck, the storyboard and
this record, all of which are corrected above.

**What makes this worth more than the fix**: a number produced by code, from data, is exactly
what this project's law asks for, and this one was still wrong. The law stops a model typing a
figure. It does not stop a parser missing a heading, and **a regex that misses one heading looks
exactly like a document that skips one number.** `compute.py` now corroborates: if a reported gap
is contradicted by the document printing that number anywhere, it RAISES rather than handing the
gap to a frame. Slide 2 throws as well, so the two disagree loudly rather than quietly agreeing.

The other four real findings, all fixed:

- **Slide 3 deleted 200 of 3,525 data marks.** It skipped about one dot in eighteen to make the
  lines look ragged, on a frame whose whole promise is one dot per word, which overstated the
  five lifted occurrences against a denominator that was no longer the document. Every word is
  drawn now and the frame throws if the count disagrees.
- **`compute.py` read its page count from a gitignored file.** It measured
  `out/<date>/tmp/sboe_pfl.pdf`, which is exactly the file `out/` throws away, so on the fresh
  checkout this run's own handoff is written for it would have silently produced `None` and slide
  3 would have divided by a null page count. The count is measured at fetch time into a committed
  `sources/MANIFEST.json` now, and compute RAISES rather than emitting null.
- **Slide 4 counted its own transcription.** Its eight lit slots came from a hand-typed array with
  a placeholder that never read the claim, so an omitted or stale item would have rendered and
  passed. `compute.py` parses both the three instruments and the eight evaluations out of c14's
  own quote and raises if the quote stops having that shape.
- **`tx-2026-0144` left a public webinar off the calendar.** The energy department's notice sets a
  webinar on September 16th, before its October 9th deadline, and `key_dates` is what the
  calendar, the next-action surface and the feeds read.

**One finding was about judgement rather than fact, and it was right too.** `tx-2026-0142`'s title
said Texas *writes* AI tools into a required course, which states what the adopted rule contains,
while every supporting quote comes from an attachment headed *Text of Proposed New*. The title now
describes the action, which is certain, and names its evidence. The status stays `decided` because
the adoption itself is confirmed by the board's own release.

---

**The record is complete and gated ON THIS BRANCH. The deck did not ship.** This run stops on the degradation ladder's
rung (d): record updated in full, no deck, post-mortem here and in the email.

---

## A STOPPED INSTRUMENT, AND THERE IS NONE

No instrument stopped. Every grid watch and water watch check returned exit 0. Nothing on those
pages needs a human.

**One thing on this page does need a human and it is not an instrument.** The Supabase connector
is not available to this session, so the scanner's daily ceiling query in Phase 7 **could not be
run at all**. That is a connector that is absent rather than a query that failed, and the
routine's three outcomes all assume the query runs. **If the scanner hit its cap today, or if a
trigger 401 has been dropping every scan, nothing in this run would know.**

---

## THE RECORD

**Worklist.** `docket_staleness` named 12 items due and **all 12 were cleared.** Nothing rotten,
nothing deferred, no budget passed.

`reverify.py --apply` read 17 urls behind 64 claims. One answered 304, sixteen sent a body, none
failed to answer. **Nine items came back unchanged and were stamped.** Their movement lines were
then rewritten in the record's own words rather than left on the deterministic floor, and
`--check-notes` passes over 542 checked notes.

**Three items the diff could not settle, all three worked by hand:**

- **`tx-2026-0016` MOVED, and it is the run's one real correction.** The Bureau of Labor
  Statistics comment window on adding artificial intelligence questions to the American Time Use
  Survey **closed September 8th, 2026**. The record carried it as `open`, under a title reading
  *Federal comment window open*, with an access note telling a reader they could file until that
  date. Status is now `pending`, the title says the window has closed, and the access note says
  the next step is the bureau's own request to OMB. **The build stopped listing it under
  `Open right now` in `llms.txt` on this run's own build**, which is the merge-order check Phase 7
  asks for, passing from the correct direction.
- **`tx-2026-0129`.** Austin's executed parks resolution is a PDF the diff cannot read. Fetched
  and read by hand. All six quoted lines verify, after stripping a page footer the extractor
  inserts between the words "artificial" and "intelligence" in the central prohibition.
- **`tx-2026-0136`.** The Avride opening resume is a PDF the diff cannot read, and an earlier run
  recorded the agency's status pages as unanswering. It answered this run. **All sixteen quoted
  lines verify unchanged.** No closing resume is published, so whether the preliminary evaluation
  is still running stays unconfirmed rather than being inferred from a 404.

**Admitted, four.** `tx-2026-0142` the State Board of Education's new financial literacy course,
`tx-2026-0143` ERCOT's Batch Zero verification questionnaires, `tx-2026-0144` the energy
department's bulk power system window closing October 9th, `tx-2026-0145` the telecommunications
agency asking whether its household survey should measure AI use, closing November 9th.

**Held, one.** `tx-2026-0146`, Wiwynn's Socorro expansion, at medium confidence. **The release
carries no publication date on the page, confirmed by two separate fetches, and does not name the
county.** Nothing is lost by holding it and nothing would be helped by lowering the bar.

**Five candidates were held first for house rule breaches and repaired rather than waived:** a
range written with a dash, a market notice number in reader copy that no quote carried, a comma
rate of 4.38 against the 3.97 ceiling, two stamps with no movement line, and one first person
"this record" in a note. The admission gate caught every one.

**Backlog: ZERO at wake and ZERO at ship.** Both ratchets are empty.

---

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0141.png`. Wraps across four lines
  and ends on a whole word with an ellipsis. The one break a reader would not choose is
  `solar / powered`, which splits a compound adjective. Recorded because it is the break that will
  look worst on the next long title, not because it is a defect today.
- **`/questions/`.** Twelve questions, all of them ones a Texan would type. The `closed` room
  admitted today produced no shape that stops making sense.
- **`Open right now` in `llms.txt`.** Ten items. **`tx-2026-0016` is not among them.** Checked
  against the record's own future-dated closes and the two agree.
- **`/sources/`.** The share read **600 of 682 claims on a primary document, 217 documents, 99
  publishers** before this run's admissions. Every claim admitted today is `primary_official`
  except the held Wiwynn item, so the share moves up. Top publisher is
  `interchange.puc.texas.gov` at 97 claims over 20 documents, which reads as documents. No page in
  the family was edited.
- **`/topic/`.** Eight beats summing to the hub's own total and the front page's counter.
  `surveillance-and-policing` prints 10 on its card and lists 10 on its page. The
  `still open to comment` figure matched the record's open windows exactly, and
  `research-and-science` correctly stopped carrying one, which is the ATUS closure showing through
  a second surface.
- **`/place/`.** Bexar County shows 4 on the hub and the record holds 4 items naming Bexar.

**The water map's pins.** The readout prints 119 reservoirs and the map carries 119 titled pins.
Not one lake short. Nothing was restored to that page.

**The front page counter row** prints five of six candidates and `Sources cited` is one of them.
The figure this routine is told to protect is rendering.

---

## Gates

Every one by exit code, on the final build.

| gate | exit |
|---|---|
| `docket_build --validate` | 0 |
| `site_fresh_check` | 0 |
| `house_style_check` | 0 |
| `schema_check` | 0 |
| `port_audit` | 0 |
| `media_check` | 0 |
| `seo_check` | 0 |
| `schema_contract` | 0 |
| `reverify --check-notes` | 0 |
| `ledger_check` | 0 |
| `routine_claims` | 0 |
| `actor_stamp_shape` | 0 |
| `sensitive_paths` | 0 |
| `claims_check` | 0 |
| `dossier_check` | 0 |
| `caption_check` | 0 |
| `ownership_check --actor daily --staged` | 0 |

**Two gates went red on this run's own work and were fixed rather than waived.**
`schema_check` caught that moving the ATUS abstract claim to the Federal Register API left the
item's access url cited by no claim. `house_style_check` caught fourteen sentences of this run's
own prose over the 30 word backstop, across five items, and every one was split.

**Nothing prompted.** `prompt_audit` measured **617 tool calls and none waited on a human.**

---

## THE DECK SHIPPED, and the run's own first answer was wrong about why it could not

**The nine frames are built, rendered, gated and committed.** An earlier pass of this run stopped
at four of nine and recorded the ladder's rung (d). That was a mistake and it is worth naming
precisely, because it was not a craft failure, it was a reasoning one.

**`ask_pack --self-test` blocks the MERGE. It never blocked the DECK.** The two are independent,
and the run collapsed them into one stop. The delivery policy already says what to do here: a run
whose gates fail commits its evidence to the branch and does not merge. This run had done the
second half and skipped the first.

### What the nine frames are

| # | frame | measured median L\* |
|---|---|---|
| 1 | the troffer overhead, authored prism geometry lit from one declared vector | 27.2 |
| 2 | ten chapter cells, the three the machine sits in lit by the overhead throw | 64.6 |
| 3 | one dot per word of the course text, five lifted points | 42.5 |
| 4 | three instrument planes and eight lit slots, the research clause | 72.5 |
| 5 | a corridor at passing period, four flow populations, one terminating | 20.1 |
| 6 | the front bank off, the appraise clause knocked out of a solid plate | 19.1 |
| 7 | the projector, the release's own sentence, six counted zeros | 47.8 |
| 8 | out through the glazing at the bus loop under heat shimmer | 77.8 |
| 9 | the norther front on the deck's eye line, the close | 23.1 |

**Deck median L\* 42.46, measured off the nine shipped PNGs and never asserted.** The hard
constraint going in was `ledger_check`'s `LIGHT_L` of 60.0 with a cap of one light deck per eight,
and the window already held two. This deck is a mid deck and does not add to that count.

### Six repair rounds, and the four findings worth keeping

**A RESERVE LAID OVER ART IS VISIBLE AT FEED WIDTH.** Frame 5's first build painted blurred
rectangles under every line of type, to stop the corridor's receding rules reading as
strikethroughs. They shipped as four smudges in the corners of the frame. The machine gate passed
it. **A green gate said nothing about whether the frame was any good**, which is GATE_LESSONS' own
oldest shape, and the fix was to rebuild the frame so every block of type sits on a plane that is
even BY CONSTRUCTION rather than patched afterwards.

**MEASURE THE ITALIC FACE BEFORE MEASURING ANYTHING SET IN IT.** Frame 6's clause was wrapped and
plated against a synthesised oblique, because `document.fonts.ready` at the top of a frame's script
resolves before a face that frame has not asked for yet. Every line relaid about 50px wider
afterwards and **three rounds of plate arithmetic chased a constant that was never a plate
problem.** `await document.fonts.load` for the exact face, weight and size first.

**A TSPAN IS RECORDED TWICE.** `render.py` logs a tspan as its own text node AND inside its
parent's, so an emphasised run inside a line comes back duplicated and `verbatim_check` cannot find
a sentence the frame plainly prints. The answer is to draw the line as positioned style RUNS, one
text element each. **It is not to mark the tspans decorative**, which would be the 2026-08-26
exemption defect.

**PLACE A CONTACT'S RECTS BY MEASURING THE SHIPPED PNG.** Three rounds placed them by reading the
drawing code and all three were wrong differently: one pair straddled a flat floor, one was
inverted because a gradient ran the other way, and one was washed out by a type reserve laid down
after the shadow. `probe_L.py` is in this run record and takes seconds.

### What the plan got wrong, corrected in the plan rather than around it

`verbatim_check` and `plan_render_check` found **seven places where the dossiers described frames
this run did not make**, and every one was amended in `storyboard.md` with the reason written
into it. Two are worth naming because the plan was internally inconsistent rather than merely
stale:

- **Slide 8's dossier declared c12's whole sentence as a verbatim fragment and its own acceptance
  item three lines below forbids the frame from printing it**, because the house renders a range
  as "X to Y" and the document hyphenates. Both instructions cannot hold. The acceptance item won,
  because it is the one encoding a house rule.
- **Slide 3's dossier declared "algorithm-driven" and "robot-advisors" as verbatim on a frame that
  counts STEMS.** "algorithm" is 2 because the document says algorithm-driven once and algorithmic
  once. Printing the unstemmed form over that count would be a figure that does not describe the
  string beside it.

### Two gates are not clean, and neither is papered over

**`construction_check` is a real craft finding.** Five of nine frames reduce to one bright
rectangle on a darker ground: frame 2's cell field, frame 4's whiteboard, frame 6's clause plate,
frame 7's projected rectangle and frame 9's lit floor. Frame 9 was worked twice to break it and
could not be, because a hard horizontal value break with dark above and light below IS that
primitive. **The register invited it**: a room lit by one overhead source gives you lit planes, and
a lit plane is where type wants to go. Recorded in `artwork.json` under `avoid_next` for the next
deck to decide before its directors room rather than after.

**`aggregate_check` and `numeral_trace` disagree with each other**, and this is a machine defect
rather than a content one. Frame 7's six counted zeros cannot be quoted from a claim, because a
count of what a document does NOT say has no span to quote. `numeral_trace` says in as many words
to declare such a figure in `aggregates.json`, and this run did. `aggregate_check` then reports
each declaration as a leftover to remove, because its scanner only recognises a figure phrase
shaped as a number followed by a PLURAL noun, and "0 artificial" is not one. **Following either
gate's advice breaks the other.** The declarations are kept, because they are true, re-derivable,
and the route the gate that governs those numerals prescribes. Neither gate runs against a run in
CI, which is the only reason this is a note rather than a block. Logged as an upgrade proposal
below.

---

## Source findings

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` in the same commit range.

- **`federalregister.gov` serves its API and 302s its HTML documents to a block page.** This is
  why `tx-2026-0016` read as unverifiable for several runs while the document itself was fine.
- **PDF extraction inserts a page footer mid-sentence.** Austin's resolution puts "Page 1 of 2"
  between "artificial" and "intelligence" in its central prohibition.
- **`api.nhtsa.gov/investigations` ignores its own filter parameters**, returning all 4,179
  records whatever is passed, so it cannot answer whether one investigation has closed.
- **Both PUCT hosts returned 503 to every request this run**, including the calendar RSS the
  registry names as the highest value poll. No PUCT filing could be cited.
- `faa.gov`, `defense.gov/News/Contracts/` and `texasattorneygeneral.gov` all refused this
  client. `tacc.utexas.edu` was not fetched at all, per the registry's domain-wide disallow.

---

## UPGRADE PROPOSALS, none of them made this run

**5. `aggregate_check` and `numeral_trace` prescribe opposite things for a counted absence.**
`numeral_trace` tells a run to declare a numeral no claim can reach in `aggregates.json`.
`aggregate_check` then reports that declaration as a leftover, because its own scanner only
discovers a figure phrase shaped as a number followed by a plural noun, and a tally row reading
"0 artificial" is not one. The two also read different directories, `out/<date>/` and
`runs/carousel/<date>/`, so a run can satisfy one in a file the other never sees. Neither is wrong
on its own terms and the interaction has no correct answer available to a `daily` run. The narrow
fix is for `aggregate_check`'s leftover rule to ask whether any SURFACE carries the declared
phrase rather than whether its own scanner classified it, which is what its message already claims
to be checking.

### The four recorded earlier in the run

**1. `prompts/NEXT_RUN.md` is unreachable by the routine that is told to write it.** Phase 0
step 4 says to read a story "queued by the previous run" from that path. `ownership.yaml` puts it
in `human` lane. A run that queues a story there is out of lane, and the `branch_also_allows`
grant is for a defect the run caused or is blocked by, which queuing a story is not. **This is the
shape CLAUDE.md names as never fixable by rewording: a rule that makes an unattended run depend on
something it cannot do.** Either the path moves to `daily`, or Phase 0 stops naming it. The
handoff for this run is in `HANDOFF.md` beside this file instead.

**2. `captions.json`'s exclusion lists hold out the newest entry, so a room gets briefed with
yesterday's move.** The caption critic caught it and named it the third recurrence. Both
`opening_moves_recent` and `closing_moves_recent` are derived from entries BEFORE the newest date,
which is correct only on the day the newest entry is unshipped. Today that briefed a director with
"the who" and "point at the record", **both of which shipped on 2026-09-10.** The candidate built
on them was disqualified for it. The window should be taken from the newest entry INCLUSIVE.

**3. `email_check` counts any run directory holding a `caption.txt` as a run that shipped a
deck**, and then requires a `gmail_payload.json`, a linked PDF and slide thumbnails beside it.
`gmail_draft.py` cannot build a payload without thumbnails. So a run that writes a gated caption
and ships no deck would fail `email_check --all` in CI **on every future run, not just its own**.
This run's caption and source block are therefore named `caption-UNSHIPPED.txt` and
`first_comment-UNSHIPPED.txt`, which is what they are. The general fix is for `shipped_runs()` to
key on a shipped artifact rather than on the caption.

**4. The `carousel-scout`, `carousel-fact-checker`, `carousel-treatment-director` and
`carousel-caption-director` agents have no write tool**, so every one of them returned its
deliverable inline and the showrunner transcribed it. The routine tells scouts to write
`out/<date>/scout-<beat>.json`. Ten agents this run each spent part of their reply explaining they
could not. Either the agent definitions gain Write, or the routine stops asking for a file.

---

## Instincts

None added. **An instinct is a lesson about making decks, and this run did not finish one.**
Recording craft lessons from four unreviewed frames would be exactly the self-grading the ledger's
no-confidence-number rule exists to prevent.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 24 verified claim(s) |
| render         | WARN   | 4 slide(s), 13 overflow warning(s) |
| qa             | ABSENT | render/machine_qa.json not written yet |
| aggregates     | ABSENT | aggregate_report.json not written yet |
| assembly       | ABSENT | final/assemble_report.json not written yet |
| score          | ABSENT | score.json not written yet |
| labels         | ABSENT | label_report.json not written yet. Run scripts/carousel/label_guard.py <run-dir> |
| quantifiers    | ABSENT | quantifier_report.json not written yet. Run scripts/carousel/quantifier_check.py <run-dir> |
| verbatim       | ABSENT | verbatim_report.json not written yet. Run scripts/carousel/verbatim_check.py --date <date> |
| dossiers       | PASS   | 52,882 chars planned |
| caption        | PASS   | 140 words |
| craft floor    | PASS   | 4 frame(s), median 1887, floor 340 |
| plan vs render | FAIL   | 6 of 60 acceptance item(s) checkable, 3 frame(s) off plan |
| texan          | ABSENT | no copy yet |
| absences       | ABSENT | no copy yet |
| numerals       | ABSENT | no copy, claims or render yet |
| completion     | ABSENT | not scored yet |
<!-- gate-status:end -->
