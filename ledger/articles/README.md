# Web editions

A dated JSON file here is required for every shipped carousel. The site build validates
all editions before generating output and refuses a missing or invalid story. The daily
routine writes the edition alongside its final carousel and commits both with the rebuild.
Do not edit the shipped copy, claims or artwork in `runs/carousel/` to rewrite a web story.

Write the dek and narrative from the same verified reporting brief used for the deck.
Edit the two formats separately. The article should stand on its own, with the outstanding
questions stated as of the source check. Keep social instructions in the social package.

- `_spec` carries `version: 1`, the purpose, source-preservation law and `written_by: daily`.
- `section` labels the coverage area.
- `dek`, `introduction` and each section's `paragraphs` contain `text` and `claims`.
- Every paragraph names the claim ids that support it. `[source label](c7)` links directly
  to that claim's source. An unknown or unbound claim makes the build fail.
- The dek doubles as the search description. Keep its rendered, HTML-escaped length between
  50 and 200 characters; the article gate checks this before the full build.
- `{{date:c1}}` formats the first date in a claim's text. `{{money:c8}}` formats its quoted
  dollar amount. `{{checked:c15}}` formats that specific source's retrieval date. Numeric
  copy must continue to pass the build's page-scoped numeral check. `{{number:c7}}` reads
  the first numeral in that claim's quote; `{{number:c7:1}}` reads the second. Inspect the
  quoted sequence before choosing an index. Never authorize numbers from authored copy.
- `related` names real Docket ids and concise link labels. Unknown records fail the build.

The byline is the existing organizational attribution. Publication date, artwork, source
documents and expandable verification are derived from the shipped run. Claim text and quotes
are retained in full. A site rebuild never asserts that the sources were checked again.

Write a specific lead and connected narrative, not a reformatted slide transcript. State
the important unknowns as of the original reporting date. Do not invent a person for the
byline or label a template rebuild as newly checked reporting. Related records may carry
later developments; the article remains a dated account. The compact source list covers
the narrative, while the disclosure preserves every claim from the complete visual edition.

Run `python tests/test_article_edition.py` and `python scripts/site/article_check.py`.
Rebuild with `scripts/site/site_build.py`, then run `SITE=docs node tests/article_edition.mjs`.
The browser test starts its own local server unless `BASE_URL` is supplied. Inspect the
desktop and phone screenshots it writes under `out/` as well as the automated verdict.
CI runs the article regressions through the existing site-build self-test and the archive
browser suite through `tests/csp_runtime.mjs`. No separate workflow or schedule is required.
