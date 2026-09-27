# Run record, September 27th, 2026

## The record, first

- **Worklist.** `docket_staleness.py` named 45 items due on the two day leash, none rotten. `reverify.py --apply` stamped 14 of them from the diff alone (9 sources answered 304, 74 sent a body, 7 did not answer). The other 31 were read by hand, one primary source each, through `fetch_doc.py` and the crawl boundary, and 30 of those were stamped with a dated line. Every stamped item's movement line was re-worded (`reverify.py --check-notes` exit 0).
- **Held back, not stamped.** tx-2026-0088, Brazos County's own page, answers 403 to every client and is a measured boundary with 4 days left on its measurement. Its journalism source still reads the same, which is not the county's own word, so the item keeps its old stamp.
- **One source moved address.** tx-2026-0180, Leander's Flock notice, rotated off the front of the city's news page. The same notice reads unchanged at its own address, `/m/newsflash/Home/Detail/1347`, and both claims now cite it.
- **Read through WebFetch.** tx-2026-0120, the DHS Progreso account, answers 403 to the project fetcher and 200 to WebFetch, as the field log records. The three sentences checked came back exact.
- **Admitted.** tx-2026-0189, the Justice Department's proposed final judgment against Pinnacle Property Management Services, the Frisco apartment manager that licensed RealPage's AI Revenue Management, with the Tunney Act comment window open. tx-2026-0190, College Station City Council's 4 to 2 vote on September 24th to keep its Flock cameras, on the city's own account of the meeting. Both through `seed/docket_seed.json` and `--promote`, both on primary sources.
- **Held.** Nothing new was held.
- **A close date that is computed, and said so.** The notice for 0189 asks for comment within 60 days of September 18th and prints no closing date. The Competitive Impact Statement runs the window from the later of that date or a newspaper summary, and no newspaper date is printed. The record's close, November 17th, is the notice's own sixty days computed in code, and `notes_for_editor` says so.
- **A contradiction inside one source.** The proposed judgment's own definition places Pinnacle's headquarters in Dallas. The amended complaint and the Competitive Impact Statement say Frisco. The record follows the complaint and the statement and never attributes Frisco to the judgment.
- **Discovery.** The PUCT calendar feed carried nothing new and AI relevant (58555 is an ancillary services cost study). The Federal Register API surfaced the RealPage notice. Six scouts ran. The leads not admitted, with the reason, are in `out/research/`: El Paso Electric's McCloud proposal for decision (the PUCT document was not read), Waymo's San Antonio restart and Austin freeways (journalism only), MD Anderson's CIPHER model (a research result, a strong clinic candidate for a later run), the UT Dallas student and the AI agent under test (primary university release, not pursued for time), Wiwynn's Socorro rack plant.
- **The record's `reverify.py` writes the ledger at indent 2 and the canonical file is indent 1**, so its `--apply` rewrites every line of the 23,600 line file. This run wrote the ledger back at indent 1. A one-line fix in `reverify.py` for a maintainer or the upgrade lane.

## Instrument check

Every page check exited 0: `gridwatch_pagecheck`, `waterwatch_pagecheck`, `waterwatch_page --self-test`, the scratch build, `media_check`, `og`, `favicon`, `truetype`, `indexnow` self-tests and `seo_check`. `schema_check` exited 1 on the committed `docs/` only, because tx-2026-0180's page there still cites the old Leander listing url. The Phase 16 rebuild carries the new url.

## Discoverability signoff

- **Card.** `og/tx-2026-0189.png` opened as an image. The headline wraps at word boundaries over four lines and ends on "Frisco apartment..." with a whole word before the ellipsis.
- **/questions/.** Read as a reader. The questions are the record's own fixed set (what each decision is, who decides, how the public can take part, where a window is open). "05 answered" on open comment windows matches the hub's own count and is what a reader would ask.
- **llms.txt Open right now.** tx-2026-0189 is listed. tx-2026-0186 still closes October 11th and is listed. No window listed there closed today.
- **/sources/.** 848 of 952 claims rest on a primary document, across 277 documents from 125 publishers. Both admissions today rest wholly on primary documents. The top publisher is `interchange.puc.texas.gov`, 109 claims from 23 documents, which is a primary source.
- **/topic/.** The defense and federal card reads 8 decisions and 5 still open to comment. Its page lists 8 decisions.
- **/place/.** Brazos County, where 0190 landed, reads 10 on the hub and its page lists 10 decisions.

## Gate status

<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 64 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 6 warn(s) |
| aggregates     | PASS   | 8 declaration(s), 10 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 6.46 MB, vector |
| score          | STALE  | score.json predates the newest render, so it describes a deck that no longer exists. Re-run it |
| labels         | ABSENT | label_report.json not written yet. Run scripts/carousel/label_guard.py <run-dir> |
| quantifiers    | ABSENT | quantifier_report.json not written yet. Run scripts/carousel/quantifier_check.py <run-dir> |
| verbatim       | ABSENT | verbatim_report.json not written yet. Run scripts/carousel/verbatim_check.py --date <date> |
| dossiers       | PASS   | 30,716 chars planned |
| caption        | PASS   | 143 words |
| craft floor    | PASS   | 9 frame(s), median 839, floor 151 |
| plan vs render | WARN   | 9 of 38 acceptance item(s) checkable |
| texan          | PASS   | places Austin, Dallas, Fort Worth, Houston, Irving, Plano, Round Rock, San Antonio / body yes / deadline yes / next step yes |
| absences       | WARN   | 0 of 4 scoped to a named document, 4 unscoped |
| numerals       | FAIL   | 28 numeral(s) over 9 frame(s), 4 the cited claims do not reach: s5 prints '13' in "13 Austin- Round Rock" and NO claim in this run carries that figure in  |
| completion     | FAIL   | THE DECK DID NOT SHIP, so this run is not done |
<!-- gate-status:end -->
