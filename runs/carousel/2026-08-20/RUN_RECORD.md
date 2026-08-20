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
