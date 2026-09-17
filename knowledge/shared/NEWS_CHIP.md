# The homepage news headline

The homepage's former weather chip is one link to a publisher's Texas tech or AI story,
or a visible availability message when no current story qualifies.
The weather instruments and their collection remain separate.

## Selection, without a model

`scripts/site/news_headlines.py` reads the free, keyless GDELT DOC API. It requests English
coverage from the preceding day with Texas place names and technology terms. It also reads the
public RSS feeds from Dallas Innovates, The Texas Tribune and Data Center Dynamics, configured
in `config/news_sources.json`. These independently published feeds continue during a GDELT
outage. Only headline, link and publication timestamp are extracted from RSS. It does
not fetch article pages, Google News, or model APIs.

The returned headline must itself name Texas, a specific Texas city or institution, and a
technology subject. An Austin possessive or a headline beginning with a clear Austin location phrase is also
accepted; a bare Austin person name is not.
SMU, UTD and UTA also identify Texas institutions in Dallas Innovates headlines. Those
initialisms do not establish Texas relevance in other outlets. Feed descriptions are not used
to establish location because regional publishers can append local boilerplate to national stories.
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

Every selected story expires 36 hours after its first observation. The renderer replaces expired
records with a visible availability message on later builds. A small browser timer retires the
stale link and shows that same message even if a deployment stalls, preserving its occupied height.
A successful empty feed retires the story once no eligible previous observation remains. A failed
feed emits a workflow warning; other feeds and still-fresh previous observations remain eligible.
If all feeds fail, the last snapshot stays intact and the collector fails visibly, retrying on the
next scheduled run. An empty bar says "Fresh headlines are temporarily unavailable." It never
invents a story or calls yesterday's timestamp a new publication date.

Requests have bounded response size, timeouts, retries, and a robots check on each feed host.
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
main SHA. The news job then checks feed health and waits up to 40 minutes for that refresh (or a
newer one) to appear on the public homepage. Dispatching guards alone is not success. No current
headline, fewer than two available feeds, or a collection timestamp over 18 hours old fails the
health check. An empty snapshot can still publish the honest availability message.

The existing six-hour `livecheck` workflow also verifies a current attributed publisher link,
unexpired headline and recent refresh timestamp on the public homepage. A stalled deployment or
silent empty result therefore fails monitoring. Review the failed run's feed warnings or
publication error before rerunning `Texas tech headline`.

## Verification

- `python3 scripts/site/news_headlines.py --self-test`
- `python3 scripts/site/news_headlines.py --collect` (network; updates snapshot)
- `python3 scripts/site/news_headlines.py --check` (offline; recomputes selection)
- `python3 scripts/site/news_headlines.py --health` (current snapshot and multiple feeds)
- `python3 scripts/site/news_headlines.py --live-check` (public homepage and freshness)
- `python3 scripts/site/site_build.py --out docs --today YYYY-MM-DD`
- `node tests/news_headline.mjs` (desktop, phone, source link, empty state and cached expiry)

Both Python checks are wired into full guards. Feed documentation:
https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
