<!-- gate-status:begin -->
| gate | status | detail |
|---|---|---|
| claims         | PASS   | 41 verified claim(s) |
| render         | PASS   | 9 slide(s) |
| qa             | WARN   | 0 fail(s), 14 warn(s) |
| aggregates     | PASS   | 8 declaration(s), 14 numeric phrase(s) in the render, all re-derived |
| assembly       | PASS   | 9 slide(s), 21.62 MB, vector |
| score          | FAIL   | 6.582, below threshold |
| labels         | PASS   | 0 claim id(s) checked, every label beside one traces to the shape its claim proves |
| quantifiers    | PASS   | 99 published string(s) read from one list, every universal names its set |
| dossiers       | PASS   | 31,638 chars planned |
| caption        | PASS   | 134 words |
| craft floor    | PASS   | 9 frame(s), median 335, floor 60 |
| plan vs render | WARN   | 18 of 51 acceptance item(s) checkable |
| texan          | PASS   | places El Paso / body yes / deadline yes / next step yes |
| absences       | PASS   | 4 of 4 scoped to a named document |
| numerals       | PASS   | 27 numeral(s) over 9 frame(s), every one reachable |
| completion     | FAIL   | THE DECK DID NOT SHIP, so this run is not done |
<!-- gate-status:end -->

## PROPOSALS FOR A MAINTAINER, because they are outside this run's lane

`ownership_check` refused both of these to actor `daily` and it was right to. They are recorded
here rather than made, which is what `CLAUDE.md` says to do with an edit another actor owns.

### 1. `scripts/site/site_pages/editorial.py` — an address is not this project's prose

`house_style_check` reports one first person hit and one over-long sentence on
`articles/2026-08-30/index.html`, and both are the same string:

    LISTED ON THE STATE MOTOR VEHICLES DEPARTMENT'S OWN PAGE txdmv.gov/about-us/MVCPA · c40

The checker reads the `about-us` segment of that path as the first person plural, and then runs
the line into the two paragraphs beside it, because a slide's set lines carry no terminal
punctuation and the sentence splitter has nothing to stop on. Three short labels are reported as
one 36 word sentence. Nobody here wrote that address, and the deck prints the path deliberately:
a scoring judge asked for it, because `txdmv.gov` alone is a department rather than a page.

The fix is in `say()` in `article_page`, and it is two lines:

- wrap an address in `<cite>`, which is what `_stripped` already removes through `QUOTED`.
- end a transcript line on a full stop where it does not already end on one.

**Two instruments were tried first and both are wrong in a way worth recording, because both
read as handled.** `data-prose="data"` exempts ONLY the comma density rule, in `our_sentences`;
every other rule reads the page through `our_prose`, which never consults it. And `<code>` is not
what the checker's `CODE` pattern means: that pattern is `script` and `style`, the two elements
whose CONTENT would otherwise be linted as prose. A mark that looks like an exemption and is not
one is worse than no mark.

### 2. `config/schema_contract.json` — the shape grew

`schema_contract` reports `claims[].retrieved_at` as a new field and asks for `--update`. The map
puts that file with `human` for a stated reason: a routine adds ITEMS and never FIELDS, and the
shape is a public contract published under CC BY, so a person decides whether the change breaks
anybody. This run did not add the field and does not get to record it.

### What that costs this run

`house_style_check` and `schema_contract` are two of Phase 16's verification gates and both stay
red. Every other gate on that list is green: `docket_build --validate`, `site_fresh_check`,
`schema_check`, `port_audit`, `media_check`, `seo_check`, and `ownership_check --actor daily`.
The two red ones are red because the fix belongs to somebody else, which is the map working
rather than the run failing.
