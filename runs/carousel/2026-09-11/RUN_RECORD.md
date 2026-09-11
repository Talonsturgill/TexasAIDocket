# Run record — 2026-09-11

## THE RUN DID NOT MERGE, AND THE RECORD IS NOT LIVE

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

`browser-layout` is also red and is **not this PR's**. `tests/video_fit.mjs` throws
`AbortError: The play() request was interrupted by a new load request`. The full `responsive.mjs`
suite passes locally against this exact `docs/` tree, `main` is green on it, and this diff touches
no video file and no test. Not re-run, because `gates` blocks the merge regardless.

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

## THE DECK, AND WHY IT DID NOT SHIP

**Four of nine frames were built.** The run reached the ladder's rung (d) rather than push a deck
that had not been through pixel review or the panel of three. **A half reviewed deck breaches the
scoring floor and the merge policy, and a partial deck is worse than no deck.**

What is finished and committed under `runs/carousel/2026-09-11/`, so the next run resumes rather
than re-plans:

- **`claims.json`, 24 verified claims and 6 rejected**, past `claims_check`, with three full
  source snapshots in `sources/` swept for six subject terms and zero provision findings.
- **`storyboard.md`**, the three-lens synthesis and nine dossiers, past `dossier_check`.
- **`compute.py` and `computed.json`**, every count derived from the fetched bytes.
- **`palette_measured.json`**, seven tokens at **zero collisions**.
- **`caption.txt`**, past its critic and past `caption_check`.
- **Frames 1 to 4**, rendering clean with no page errors.

**The fact checker broke three things in the showrunner's own brief and all three were wrong.**
The subsections are under `(d)`, not `(c)`. The attachment heads itself *Text of Proposed New* and
is not adopted text. September 4th is a date line the item prints, not a vote this record
witnessed. The record and every frame were corrected before anything was drawn.

**The palette is the run's sharpest measured finding.** The winning director's seven tokens were
estimated by hand and **four of them collided**, at dE 4.94, 7.02, 5.12 and 7.96 against a
calibrated tenth percentile of 9.55, with its two lightest sitting 6.24 from each other. The
materials did not change. Where they sit did, after a sweep of the sRGB cube under a chroma cap
found where a real room material still has room.

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
