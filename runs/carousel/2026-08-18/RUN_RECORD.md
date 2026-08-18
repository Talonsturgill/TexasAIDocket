# Run record — 2026-08-18 — Carousel No. 2

## Outcome: full run, both deliverables, after a mid-run pause

The run began degraded and finished whole. All six research scouts died within seconds of launch
on a **weekly account usage limit** that reset at 5pm UTC. Per the failure protocol a usage limit
is a pause rather than a failure, and per the degradation ladder the record is what a dying run
saves. So the record was re-verified by hand through direct fetches while the limit held, committed
and pushed on its own. When the limit lifted the scouts were re-run and the deck was built on top
of the already-safe record.

That ordering is the useful thing to record. The record shipped at rung (d) and the deck was added
afterwards, so at no point was a re-verified public fact waiting on a deck that might not arrive.

## The record

### Re-verified (Phase 3) — all six on the worklist, all checked and unchanged

Selector at `--budget 6`. Every item re-verified against a primary source fetched this run.
Nothing had moved, so `last_verified` advanced to 2026-08-18 and no history note was written, per
the rule that a note is added only when something changed.

| item | source fetched | finding |
|---|---|---|
| tx-2026-0034 | El Paso Legistar webapi, Matter 16074 | Unchanged. Status "Agenda Ready", agenda date August 18th, `MatterPassedDate` null. The vote was today and had not happened at fetch time, so it stays `pending` |
| tx-2026-0053 | Houston ISD Legistar webapi, Event 1304 | Unchanged. Policy CQD(LOCAL) sits on the August 13th agenda with no recorded action and no passed flag. Stays `pending`. **This item became the deck's anchor** |
| tx-2026-0064 | TCEQ NAPD PDF, permit 182126 | Unchanged. Crusoe Technologies LLC, permits 182126, PSDTX1688 and GHGPSDTX263. Comment window is 30 days from newspaper publication. Stays `open` |
| tx-2026-0027 | City of Taylor newsflash 2066 | Unchanged. The Compal amended abatement notice still posts. Stays `pending` |
| tx-2026-0032 | KWTX, Texas Scorecard | Unchanged. A discovery lead surfaced on a Killeen council agenda item, queued below. Stays `open` |
| tx-2026-0037 | GovTech, KGNS | Unchanged. Stays `open` |

Nothing rotten at wake. The three over-limit items (0032, 0037, 0064) were cleared first.

### Deferred, admitted, backlog

Eight items fell past `--budget 6`: tx-2026-0063, 0068, 0073, 0024, 0072, 0003, 0062, 0057. The
deferred list has now been non-empty two runs running, so **the next run should raise `--budget`
to 8 rather than let the tail rot.**

**Nothing was admitted.** Three genuinely new decisions surfaced (Fort Worth's first moratorium
vote, Denton's hearing-date vote, a five-member Dallas council memo) and all three rest on
journalism alone, because `fortworthtexas.gov` 403'd and the PUCT calendar RSS 402'd. Under the
admission bar they are **held in the seed with that reason**, which is the designed outcome and
costs nothing.

Backlog held steady at 3, the grandfathered ERCOT statewide dockets. Not grown.

## Phase 7 — instrument and discoverability

Grid and water instruments untouched. Both page checks, the water self-test, `media_check`,
`schema_check`, `og`, `favicon`, `truetype` and `indexnow` all pass by exit code.

**Scanner daily-cap check: NOT RUN.** The Supabase connector for `texas-ai-scanner` was not
available in this environment. Recorded rather than skipped silently.

### Discoverability signoff

- **One decision's card.** `docs/og/tx-2026-0073.png` opened as an image. Wraps at word boundaries
  across four lines, ends in an intentional ellipsis on a long title. No mid-word stump. Fine.
- **`llms.txt` Open right now.** Lists tx-2026-0034, tx-2026-0015, tx-2026-0016 and tx-2026-0072.
  Consistent with the re-verified windows, and no closed window is listed, so the merge order is
  right. Fine.
- **`/sources/`.** Titles render as host names, the quoted-material exemption doing its job and not
  hiding one of our own sentences. Fine.
- **`/questions/`.** NOT LOOKED AT in depth. Recorded honestly rather than signed off as fine.

## The deck

**Story:** Houston ISD's Future 2 model, an AI-era school whose afternoon experiences are
screen-free, against a board AI policy that shows no recorded action. Anchored to `tx-2026-0053`,
re-verified this run. Dedupe gate clean against the one prior deck.

### THE MOST IMPORTANT THING THAT HAPPENED THIS RUN

**The fact-checker killed the story's premise, and it was right to.** The deck was briefed as "two
neighbouring districts went opposite directions on AI in children's hands". The Katy ISD half of
that does not exist. The primary post carries no grade restriction, no prohibition, and no mention
of Gemini or Copilot, and the AI Framework document itself was unreachable through eleven paths.
Nine claims were rejected in all, including:

- an August 10th start date and an "Alpha School TimeBack" vendor name, both tracing only to
  `houstonpublicmedia.org`, which returns 403 site-wide
- an assessment threshold of "above 60 percent" that is **contradicted** by the source, which
  states 93% attendance and the 40th percentile
- "AI literacy in the afternoon", also contradicted, because the district states the afternoon is
  screen-free

The surviving story is better than the briefed one. An AI-era school that takes the screens away
after lunch is a stronger and truer frame than a manufactured conflict between two districts.

### One number this deck deliberately refused

A treatment proposed publishing the instructional day as 510 minutes, the named blocks as 500 of
them, and the difference of 10 as time the schedule does not describe. The arithmetic runs.
**It is not published anywhere.** c4 says the curriculum separates the day into three parts and c3
says the first four hours follow the standard curriculum, and no source states those are disjoint.
Summing them may double count, which makes the residual an artefact of an unstated assumption
rather than a fact about the day. That is the exact shape of the sibling's wrong FIVE. The refusal
is recorded in `compute.py` and in `aggregates.json` rather than in a comment nobody reads.

### What the reviewers caught, and it was a lot

The caption critic rejected **both** candidates. Candidate A's hook, "Future 2 afternoons are
screen-free", committed the deck's single largest over-read in the one sentence that travels alone,
because the record says afternoon *experiences*. It also flagged "three blocks carry the rest" as
implied arithmetic. One rewrite was spent against its brief.

Three pixel critics returned nine FAILs between them. The ones that mattered:

- **Slide 5 read as a Gantt chart.** Three offset tiles under a captioned span rule assert start
  times, while the caption directly beneath says the record never states which block falls when.
  The art contradicted the copy on the same frame. The stagger had not neutralised position, it had
  fabricated it. The span rule was deleted and the tiles now sit rotated and overlapping as loose
  objects. **All five of that slide's acceptance items passed while it was broken**, which is the
  clearest example this product has yet produced of a checklist that cannot catch its own failure.
- **Slide 9 printed the word "passed"**, breaching its own first acceptance item, and a dashed
  leader ran from the no-action node into that empty field, which is a causal drawing and reads as
  an accusation. Both are gone. The leader had been added to answer the dead-lower-zone gate, so one
  gate's fix created a worse editorial problem than the one it solved.
- **Slide 7 printed "MAP"**, a product name, one line above the word "platform", on the frame whose
  entire claim is that no product is named.
- **Slide 8 struck a line through "Academy"**, because a fixed-width plaque wrapped a long school
  name outside its own face. A reader does not see illegible type there, they see a school name
  crossed out on a slide about which schools were added.
- **Slide 2 marked a filled dot inside Harris County** for a claim that carries no coordinates.
- **Slide 4's legend wrapped** so that "it optional" landed under the FILLED swatch, inverting the
  deck's own evidence grammar at feed size.

Two dead-lower-zone failures were also caught and repaired with real furniture rather than with a
larger quiet zone.

### Craft notes worth keeping

- The register is a deliberate inversion of the August 16th deck: daylight throughout with exactly
  one dark frame, against that deck's dark register with one paper inversion. Palette source is a
  post-war Houston ISD elementary building on the Gulf Coast prairie of Harris County.
- The reserved red is **unspent**. No comment window in this story closes in a period a reader can
  act on, and painting a pending policy red would dramatise a hole.
- Two structural laws held all deck: no circles anywhere except one path node, argued for by name;
  and a filled form means the source states it while an outlined form means the source calls it
  optional or does not describe it.

## Sources that behaved differently from the registry

Appended to `knowledge/shared/SOURCES_FIELD_LOG.md` in the same commit range. The PUCT calendar RSS
402'd, `interchange.puc.texas.gov` 503'd twice, `texasattorneygeneral.gov` 402'd, and four newsrooms
plus a city's own page 403'd. `abc13.com` answered 200 and truncated its quotes to about 125
characters, which is worse than a refusal because it fails silently.

**A dating trap worth naming:** a search for Texas AG AI enforcement surfaces the Meta and
Character.AI investigation heavily, and it is dated **August 18th, 2025**, not 2026. A scout caught
it. An anniversary reads as news to a search ranker and the year is the only thing separating them.

## Proposals, which this actor may not implement

- **The fact-checker agent has no write tool.** It returned a complete claims file as text and the
  showrunner had to transcribe it, which is a transcription risk on the single most important file
  in the run. Its tool grant should include Write.
- **`claims_check` rejected the fact-checker's output on four separate field names** (`source_url`
  vs `url`, a missing `retrieved`, `journalism` vs `secondary_reported`, `dropped` vs `rejected`).
  The agent's own prompt should carry the exact schema the gate enforces, or the gate's expected
  shape should be published where the agent reads it.
- **`aggregate_check` has no route for a numeral that is quoted from a single claim.** Its `count`
  rule requires one claim id per unit counted, so a figure the source itself writes has to be
  declared through `computed_by`. That works and is honest, but the field name says the opposite of
  what happened.

## What the next run should pick up

- **Raise `--budget` to 8.** The deferred list has been non-empty two runs running.
- The El Paso vote (tx-2026-0034) resolved today. Re-verify the outcome.
- Killeen council took up the data center subject as a future agenda item. Find the primary agenda
  record and decide whether it advances tx-2026-0032 or is a new item.
- Three held DFW items need a primary source before admission: Fort Worth, Denton, Dallas.
- The scanner daily-cap query, which needs the Supabase connector.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 18 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | PASS   | 9 slide(s), zero fails, zero warns |
| aggregates     | PASS   | 7 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 8.76 MB, vector |
| score          | PASS   | None |
| dossiers       | PASS   | 29,823 chars planned |
| caption        | PASS   | 178 words |
<!-- gate-status:end -->
