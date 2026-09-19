# Homepage Trending headline

The compact homepage strip links to an attributed publisher headline and its original feed date.
Headlines rotate in six-hour editions. No model calls, article scraping or rewritten titles are used.

## Sources and relevance

The feeds in `config/news_sources.json` include Texas newsrooms, independent technology reporting,
research and first-party AI announcements. SiliconANGLE, AI News, GeekWire, TechSpot and
ScienceDaily supplement Dallas Innovates, The Texas Tribune, Data Center Dynamics, MIT News,
OpenAI, NVIDIA and Google. The production collector makes no GDELT request.

Every feed is checked against its host's robots policy. Requests have a response-size limit,
a timeout and bounded parallelism. Each source gets one attempt in a run. ETag and Last-Modified
validators reduce repeat transfers. A failed source carries a persisted retry time into the next
successful snapshot. HTTP 429 respects Retry-After rather than immediately trying again.
Other publishers keep the collection running. Only headline metadata is retained.

A candidate must state AI relevance or Texas technology relevance in its headline. Publisher
identity and feed membership never establish relevance. Stocks, sports and promotional headlines
are excluded. The same relevance and source checks cover browser seed, cache and live responses,
including all queued future headlines. MIT's unrelated reading-program story is a regression case.

Texas AI ranks first, followed by global AI and Texas technology. Independent reporting precedes
company announcements within a category. Independent coverage and source age rank the remaining
choices. Sister outlets and identical wire headlines cannot inflate coverage. This is a coverage
proxy, not audience analytics or a claim to measure the entire internet.

## Six-hour editions

The edition boundaries match the collector schedule, at 01:23, 07:23, 13:23 and 19:23 UTC.
Each successful collection prepares the current edition and up to three reserve editions.
The current published edition stays stable on retries. The next edition uses a different story,
not another outlet's version of the same story. Previously displayed topics are avoided for
72 hours when another qualifying story is available. A quiet-day fallback chooses the least
recently shown eligible topic and still refuses consecutive repeats.

Every queued story must be under 72 hours old at its scheduled start. The browser advances the
queue at the edition boundary, on reload and when returning to the tab. This works even if
GitHub starts a scheduled collection late or a feed request fails. The browser checks for a
new published queue on load and every 15 minutes while visible. Collection timestamps never
replace the original story date or make an old article appear new.

An exhausted queue retains a dated last-good headline labelled Recent. Nothing invents news
when sources fail. A snapshot without a distinct next edition or two independent working feeds
fails the publishing health check and does not replace the last published snapshot.

## Publication and verification

`.github/workflows/news.yml` collects every six hours. It restores the published observation,
rotation and source-backoff history, then validates and publishes only
`news-data/ledger/news/latest.json`. Ordinary refreshes do not change main or trigger Pages.
Non-forced updates and timestamp checks prevent an older run from overwriting a newer one.

Generated HTML embeds a seed queue for first paint. Browser local storage retains the last
valid queue. Publisher attribution, dates, HTTPS links, relevance, queue bounds and ordering
are checked before display. The homepage CSP permits only the exact public data path.

Each production run checks the public snapshot and opens the actual homepage at desktop and
phone widths. It verifies the current edition, then advances that browser's clock with feed
requests blocked to prove the next edition changes the headline. Local tests also cover
restarts, unchanged feeds, duplicate stories, exhausted queues, 304, 429 and malicious reserves.

- `python3 scripts/site/news_headlines.py --self-test`, `--check`, `--health`
- `python3 scripts/site/news_publish.py --self-test`
- `python3 scripts/site/news_publish.py --restore` and `--publish`
- `python3 scripts/site/news_headlines.py --collect` and `--live-check`
- `node tests/news_headline.mjs` and `node tests/news_live.mjs`
