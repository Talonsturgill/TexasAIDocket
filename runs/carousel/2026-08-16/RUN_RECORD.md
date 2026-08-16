# Run record, August 16th, 2026

Carousel No. 1. The first deck this repo has shipped, so every carousel ledger was empty at
wake and nothing was excluded.

## The record

Selector run at `--budget 6`. The first worklist cleared, and because the deferred list held
seven items on a 58 item record, the budget was raised in a second pass rather than letting
the tail age. Twelve items were re-verified in all.

| item | what happened |
|---|---|
| tx-2026-0001 | CHANGED. The filing index moved from 66 to 67 with a late comment from Antora Energy. The proposal for publication also creates a NEW Section 25.252, which the summary did not carry. Both fixed |
| tx-2026-0024 | CHANGED. The August 21st open meeting no longer names Docket 59315 and no longer sits in Commissioners Hearing Room 7-100. It now gives an off site address. A meeting on August 20th has been added |
| tx-2026-0042 | Quote fidelity. The stored quote spliced two sentences across a `," he said. "` that the source carries. Replaced with the contiguous string |
| tx-2026-0055 | Quote fidelity. The stored quote capitalised an initial word and converted the source's double quotes to single. Replaced |
| tx-2026-0008, 0025, 0026 | Checked and unchanged. Statute text and the Temple agenda both still carry every quote |
| tx-2026-0002, 0015, 0016, 0034, 0058 | Checked and unchanged. Every open comment window still open on the date the record publishes |

Nothing was rotten. `docket_staleness` exited 0 both times.

### The backlog

Four entries at wake, three at ship.

- **CLEARED** `tx-2026-0006 points at tx-2026-0010, which is not in the record`. The reader copy
  now states the statutory basis itself rather than pointing at an item fact checking had culled.
  Business and Commerce Code Sec. 552.102 requires the Attorney General to run an online
  complaint mechanism, and that sentence is now in the item with its own claim and quote.
- **NOT CLEARED** the three `no county and not statewide` entries, all ERCOT rulemaking dockets.
  Their own sources name no county, and the ERCOT region is not the state, so both available
  answers would be a guess about scope. Left as they are rather than published wrong.

### Admitted

| item | source | why it cleared the bar |
|---|---|---|
| tx-2026-0071 | Governor's release, August 6th | Primary. Names Grimes County. Every numeral quoted |
| tx-2026-0072 | Governor's directive letter, August 3rd | Primary. Statewide. Points at the utility commission's August 20th open meeting as the dated way in |
| tx-2026-0073 | Legislative Reference Library hearings listing | Primary. Two dated hearings, August 19th and August 20th |

Nothing was held this run.

## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0070.png`, the newest item.
  Opened. The headline wraps at word boundaries across four lines and truncates on a whole
  token, "Precinct 4", rather than mid-word. Legible. The lower two fifths of the card carry
  nothing, which is a composition observation and not a fault. `og.py` is maintainer owned, so
  it is a proposal below and not an edit.
- **`/questions/`, read as a reader.** Twelve question pages, each answering one kind of
  question about every entry. Counts read 58 answered for what each decision is, 54 for how
  the public can take part, and 04 for where a comment window is open. Those are questions a
  Texan would type. No shape has broken on a room or a status the record has not carried before.
- **The `Open right now` section of `llms.txt`.** Cross checked against the windows re-verified
  in Phase 3. No window closed today, and none that closed is still listed. The merge order is
  right. A defect in the section's SCOPE is recorded as a proposal below.
- **A source title in `/sources/`.** Checked five titles carrying punctuation the house bans in
  its own prose. All five are genuine source titles, including
  `Cancellation of Notice & Comment Hearing: Vantage Data Centers TX11, LLC, O4791 | TCEQ`.
  The quoted-material exemption is doing its job and is not hiding one of our own sentences.

## Instrument once over

Every check run by exit code, all 0.

| check | exit |
|---|---|
| `gridwatch_pagecheck.py` | 0, page current and holding its promises |
| `waterwatch_page.py --self-test` | 0 |
| `schema_check.py` | 0, 534 nodes across 163 pages |
| `og.py --self-test` | 0 |
| `favicon.py --self-test` | 0 |
| `truetype.py --self-test` | 0 |
| `indexnow.py --self-test` | 0 |

**The water page's coverage sentence.** Read. It still says the state's water data tags
reservoirs to 19 of the 67 statistical areas and that San Antonio-New Braunfels is not one of
them, and it still calls that a gap rather than an answer. The source has not started tagging
San Antonio, so the paragraph is still true and still needed.

**A place page for a metro.** Killeen-Temple, where Bell County carries this run's re-verified
Temple item. The headline count and the items agree, and the untouched counties are still named
by name, "Nothing has yet been found in Coryell, Lampasas."

**The `backlog:` lines.** Four at wake, three at ship. Shrunk, not grown.

**The scanner's daily ceiling.** NOT CHECKED. No Supabase connector is available to this
session, so the `scanner.scans` query could not be run at all. This is the "the query itself
fails" outcome and it does not block the run. It is worth saying plainly that a ceiling nobody
is notified about went unchecked today.

## Proposals, out of this actor's lane

Each of these is in `scripts/site/`, which `ownership.yaml` gives to `human`. The daily routine
may fix presentation only in `gridwatch_page.py` and `waterwatch_page.py`, so these are written
down and stopped.

1. **`llms.txt` promises something its filter does not deliver.** `site_build.py:2357` builds
   `open_now` from `public_access.room in ("open_comment", "open_meeting")` and ignores
   `status`. The heading above it reads "Decisions a member of the public still has a dated way
   into." A decided item whose room is `open_meeting` therefore appears there. Archer County's
   unanimous denial of a data center abatement is on that list, and a reader following it finds
   a finished vote. The filter wants `and status not in ("decided", "withdrawn")`, or the
   heading wants to stop promising.

2. **A metro place page states a statewide fact it does not mean.** The map caption reads
   "Texas counties in the record. 1 of 254 counties carry an item." On a metro page that count
   is scoped to that metro's items, so Killeen-Temple says 1, Austin says 3 and El Paso says 1.
   The number is right and the sentence is not. It should name the scope it is counting.

3. **A water page check has no equivalent to `gridwatch_pagecheck.py`.** It would live in
   `scripts/gridwatch/`, which this routine does not own. Recorded, per the master routine's
   own instruction.

4. **`docket_build.py --promote SEED --out ledger/docket.json` is destructive, and the master
   routine tells a run to type it.** `promote()` writes ONLY the admitted set to `--out`. Run as
   Phase 5 prints it, against a seed carrying 27 candidates and a ledger carrying 58 published
   items, it writes 6 items and silently drops 52. That was proved this run by writing the
   output to a temp file and diffing, never at the ledger. Admissions were done instead by
   gating each candidate with `--promote` and no `--out`, then appending what passed. Both the
   command in `prompts/daily_routine.md` and the guard in `promote()` are maintainer owned.
   The safe form of the command is `--promote SEED` with no `--out` at all.

## The deck

**Story.** `tx-2026-0071`, the Terafab semiconductor plant SpaceX will build in Grimes County,
admitted to the record earlier in this same run.

**Why this one and not the others.** The Abbott audit directive is the biggest policy story of the
fortnight and the docket on this site already publishes it, and `APPLICATIONS.md` is explicit that
the deck must not narrate the record back. The Atlas and Kodiak driverless sand fleet in the
Permian is the strongest pure application story the scouts found and it is not a decision the
record holds, which Phase 8 rules out. Terafab is both a decision the record now carries and the
manufacturing end of the application layer, which is the loop `APPLICATIONS.md` says nobody draws.

**The through-line.** Texas has spent two years arguing about what plugs into its grid. Three days
before this announcement the state froze the queue pending an audit. The plant is reported to be
building its own generation rather than joining it. The deck ends somewhere a reader who has
followed this story did not expect to be.

`dedupe_check` was clean at selection with zero entries in the ledger. `instincts.py --top 5`
printed nothing, so the directors room and the caption room were handed nothing, which is correct
on run one rather than a gap.

### The rooms

Three treatment directors were sent out on three lenses. Two returned before the art phase and one,
the signed-record lens, returned after the storyboard was already written. **The spine is the
showrunner's**, because neither of the first two had claim c24 and c24 is the turn. What was
grafted, and from whom, is written into `storyboard.md` at the head. The late lens still changed
the deck: its soil section replaced the planned slide 8 outright, and it is the best single image
any of the three produced.

Two caption directors wrote on different assigned moves. The critic rejected both and rewrote,
which is the outcome its own doctrine says should be the default, and its reasons were specific.
It caught an unsourced superlative in one candidate, "the biggest new load here", and date
arithmetic done in prose rather than in code in both.

### Numbers

`out/2026-08-16/compute.py` produces every figure on the deck that is not quoted, and it is shipped
beside the artifacts so anybody can re-run it. The stated floor area is a perfect square and the
script asserts that rather than assuming it, because a rounded side length in the largest type on
slide 1 would be a typed number wearing a computation's clothes.

Two figures were deliberately NOT computed. Ninety percent of 474 gigawatts is the product of two
approximations, so the queue on slide 7 is drawn as one hundred paths, one per PERCENT, and never
one per gigawatt. The floor area is never converted to acres, because a reader takes an acreage for
a site size and no acreage is published.

The Governor's letter and ERCOT's own June figures are never set on a shared scale. They are seven
weeks apart, from two bodies, and neither restates the other.

### What the fact checker rejected, and one place it was wrong

Seven rejections are recorded in `claims.json`. The load-bearing ones: the widely repeated "78
percent" is the reporter's own sentence and not a quotation from the lawyer it is attributed to,
and the water quotes belong to a Terafab representative rather than to that lawyer. A slide putting
those words in a lawyer's mouth would have been false.

**It was wrong about one thing and the raw bytes settled it.** It reported that two quotes end in a
period where the record stores a comma. The saved HTML of the release carries `Innovation Act,"`
and `Grimes County,"` with the comma inside the closing quotation mark, so the record's quotes were
already right and were left alone. An agent's confident correction is not evidence either.

## Sources registry

`SOURCES_REGISTRY.md` behaved as written with three exceptions, all recorded in the same commit
as this record.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 29 verified claim(s) |
| render         | WARN   | 9 slide(s), 1 overflow warning(s) |
| qa             | WARN   | 0 fail(s), 29 warn(s) |
| aggregates     | PASS   | 4 declared and re-derived |
| assembly       | PASS   | 9 slide(s), 4.15 MB, vector |
| score          | ABSENT | score.json not written yet |
| dossiers       | PASS   | 33,704 chars planned |
| caption        | PASS   | 138 words |
<!-- gate-status:end -->
