## Discoverability signoff

- **One decision's card, opened as an image.** `docs/og/tx-2026-0141.png`, the newest item at the
  time of the check. The headline wraps across four lines and ends on a whole word with an
  ellipsis, `UT San Antonio / builds a solar / powered flood sensor / that runs its model...`. The
  one break a reader would not choose is `solar / powered`, which splits a compound adjective. The
  wrapper cuts on width and this title has no long proper noun in it, so the card is doing what it
  should. Not a defect, recorded because it is the break that will look worst on the next long
  title.
- **`/questions/`, read as a reader.** Twelve questions on the hub, and they read as questions a
  Texan would type. `Where a comment window is open`, `Which are on the ERCOT grid` and `When each
  one was last checked` are the three that earn the page. Nothing on it went odd on this run's new
  rooms, and the one new `closed` room admitted today (tx-2026-0142) did not produce a shape that
  stops making sense.
- **The `Open right now` section of `llms.txt`.** Ten items listed. **tx-2026-0016 is NOT among
  them**, which is the check this bullet exists for. Its window closed September 8th, this run
  moved the record before the build, and the built corpus therefore stopped advertising a door
  that had shut. Cross-checked against the record's own future-dated closes and the two agree.
- **`/sources/`, the record's own report card.** The share at the top reads **600 of 682 claims
  rest on a primary document, across 217 documents from 99 publishers**, read on the build made
  before this run's four admissions. Every claim this run admitted is `primary_official` except
  the held Wiwynn item, so the share moves up rather than down. The top publisher is
  `interchange.puc.texas.gov` at 97 claims over 20 documents, which is the right host to be
  leaning on hardest for a record about Texas utility decisions and reads as documents rather
  than as reports about them. The quoted-material exemption is still confined to quotes. No page
  in the family was edited.
- **`/topic/`, counting one card against its own page.** Eight beats. `surveillance-and-policing`
  prints 10 on its card and its page lists 10 items. The per-beat figures sum to 123 against the
  hub's own `All 123 decisions` and the front page's `123 Decisions tracked`, all on the
  pre-admission build. The `still open to comment` figure is 3, one each on
  `defense-and-federal`, `power-and-the-grid` and `surveillance-and-policing`, and the record
  holds exactly three `open_comment` rooms whose close date is today or later. **`research-and-science`
  no longer carries one**, which is the same ATUS closure showing through a second surface.
- **`/place/`, for a place the record recently landed something in.** Bexar County is on the hub
  at 4, and the record holds 4 items naming Bexar. The hub and the ledger agree.

## Instrument once over

Every check by exit code, none of them blocking:

| check | exit |
|---|---|
| `gridwatch_pagecheck` | 0 |
| `waterwatch_pagecheck` | 0 |
| `waterwatch_page --self-test` | 0 |
| `media_check` | 0 |
| `schema_check` | 1, then 0 after the repair below |
| `og --self-test` | 0 |
| `favicon --self-test` | 0 |
| `truetype --self-test` | 0 |
| `indexnow --self-test` | 0 |
| `seo_check` | 0 |

**No instrument has stopped.** No exit 3 anywhere, so nothing here needs a human.

`schema_check` went red on this run's own edit rather than on a collector. Moving tx-2026-0016's
abstract claim to the Federal Register API left the item's access url cited by no claim, and the
gate reads every url a page cites and asserts it is in one. The claim was pointed back at the
notice itself and the gate came back clean at 2,372 nodes across 701 pages with every reference
resolved.

**The water map's pins against the day's reservoir count.** The readout prints `Reservoirs 119`
and the map SVG carries 119 `<title>` elements, 119 elements classed `res` and 119 distinct
reservoir titles. **The drawing is not one lake short.** Nothing was restored to that page and
the four removed blocks stay removed.

**The front page counter row.** Five of six candidates printed, and `Sources cited` is one of
them at 682. That is the figure this routine is told to protect, and it is rendering.

## The scanner's daily ceiling — NOT CHECKED

**No Supabase connector is available to this session.** The tool list carries the GitHub and Gmail
servers and nothing else, so the `scanner.scans` query in Phase 7 could not be run at all. This is
not a query that failed, it is a connector that is absent, and the routine's three outcomes all
assume the query runs. Recorded as NOT LOOKED AT rather than as fine: if the scanner hit its daily
cap today, or if a `trigger 401` has been dropping every scan, nothing in this run would know.
