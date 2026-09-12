# The homepage news headline

The homepage's former weather chip is one link to a publisher's Texas tech or AI story.
The weather instruments and their collection remain separate.

## Selection, without a model

`scripts/site/news_headlines.py` reads the free, keyless GDELT DOC API. It requests English
coverage from the preceding day with Texas place names and technology terms. It also reads the public Dallas Innovates RSS feed, keeping a local source available during
a GDELT outage. Only headline, link and publication timestamp are extracted from RSS. It does
not fetch article pages, Google News, or model APIs.

The returned headline must itself name Texas, a specific Texas city or institution, and a
technology subject. An Austin possessive or a headline beginning with a clear Austin location phrase is also
accepted; a bare Austin person name is not.
Sports, stock commentary, scholarships and promotional text are excluded. Only newsrooms in
`config/news_sources.json` may appear. The configuration groups sister outlets together.

Similar headlines need three shared content words and token cosine similarity of at least 0.45.
Each candidate's coverage is the smaller of its matching ownership groups and distinct normalized
headlines. Identical wire copies count once. The score is `(1 + log2(coverage)) * 2^(-age_hours/24)`.
The highest score wins, with stable timestamp and URL tie breaks. This is a bounded **coverage
proxy**, not measured reader traffic, a comprehensive census, or a promise of an objective
statewide number one. Broad keyword filters can miss stories; the allowlist can be expanded.

GDELT's `seendate` is an indexing time, not a verified publication time. We never label it as
publication. RSS uses the publisher's own timestamp as its freshness anchor. An old dated
article URL is rejected. A URL's first observation is retained for a
week, so a repeated result cannot keep refreshing its own expiry. The linked publisher owns the
headline; the site quotes it unchanged in a `cite`, with visible publisher attribution. Discovery
is credited to The GDELT Project and publisher RSS in the link's description and the committed snapshot.

## Freshness and failure

Every selected story expires 36 hours after its first observation. The renderer omits expired
records on later builds, and a small browser timer hides a stale chip even if a deployment stalls.
A successful empty feed retires the story once no eligible previous observation remains. A failed feed emits a workflow warning; the other feed and still-fresh previous observations
remain eligible. If both feeds fail, the last snapshot stays intact and the collector fails
visibly, retrying on the next scheduled run. A missing headline leaves the hero clean. It never substitutes a weather statistic,
invents a story, or calls yesterday's timestamp a new publication date.

Requests have bounded response size, timeouts, retries, and a robots check on the API host.
The source response is represented by its hash and normalized eligible metadata in
`ledger/news/latest.json`. Selection and expiry are recomputed by `--check`. Builds use this
committed snapshot without network or wall-clock reads, keeping site reproduction deterministic.

## Scheduling and release

`.github/workflows/news.yml` runs at 01:23, 07:23, 13:23 and 19:23 UTC daily, and has a manual
GitHub Actions dispatch. No AI routine or API key is involved. The `news` actor can change only
its snapshot and regenerate `docs/`. Source configuration, scripts and workflow permissions
remain outside its lane.

The workflow fetches once, rebuilds on the latest main, checks the house style and ownership,
and pushes one commit. A concurrent main update causes a fresh rebuild, not a generated-file
rebase. It then dispatches the existing full guards; Pages publishes only an exactly guarded
main SHA. If a feed fails, review the failed `Texas tech headline` run and rerun that workflow.

## Verification

- `python3 scripts/site/news_headlines.py --self-test`
- `python3 scripts/site/news_headlines.py --collect` (network; updates snapshot)
- `python3 scripts/site/news_headlines.py --check` (offline; recomputes selection)
- `python3 scripts/site/site_build.py --out docs --today YYYY-MM-DD`
- `node tests/news_headline.mjs` (desktop, phone, source link, cached expiry)

Both Python checks are wired into full guards. Feed documentation:
https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
