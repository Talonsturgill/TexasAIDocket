# Homepage Trending headline

The compact homepage bar links to a real publisher headline and shows its source and date.
No model calls, keys, article scraping, ticker or rewritten headlines are involved.

## Selection

`scripts/site/news_headlines.py` reads GDELT discovery metadata and seven publisher RSS feeds:
Dallas Innovates, The Texas Tribune, Data Center Dynamics, MIT News, OpenAI, NVIDIA and Google's
AI feed. Each feed is read only after its host's robots policy permits access. Requests have
bounded sizes, retries and timeouts and run in parallel; one slow provider cannot hold up all
other feeds. Only headline metadata is retained.

Texas AI stories rank first, followed by broader AI coverage and then Texas technology news.
Global coverage is limited to the four explicitly configured groups. The three dedicated AI
feeds can establish subject relevance even when the headline omits the letters AI. The general
NVIDIA feed still requires an AI term, so gaming headlines do not qualify. Regional feed
boilerplate never establishes Texas relevance. Stocks, sports and promotional headlines are
excluded. Publisher attribution and source links come from the allowlist in
`config/news_sources.json`.

Within each category, independent coverage and age determine rank. Sister publishers and
identical wire headlines cannot inflate coverage. This is a coverage proxy, not audience
analytics or a claim to measure the entire internet. A headline under 72 hours old outranks
older coverage. Up to seven days of observations provide a dated last-good fallback. Repeated
URLs retain their earliest source date or observation; successful fetches never make old
articles new again.

## Publication independent of the website

`.github/workflows/news.yml` runs every six hours (`23 1,7,13,19 * * *` UTC). It restores the
previous observations, collects, validates, and publishes **only** `news-data/ledger/news/latest.json` using
`scripts/site/news_publish.py`. Non-forced updates and a timestamp check prevent older refreshes
from overwriting newer ones. This data branch contains no site code or workflows. The collector
never changes `main` or generated `docs/`, and does not dispatch full-site guards or Pages.

The homepage reads that exact public JSON file from GitHub's raw host. Its CSP permits this
specific path only on the homepage. The browser validates the payload version, timestamps,
publisher identity, title and HTTPS link before using textContent to update the existing bar.
It fetches at page load, every 15 minutes while visible, and when a reader returns to the tab or
comes online. The request sends no credentials or referrer.

The generated homepage still embeds a deterministic seed from `ledger/news/latest.json` for
first paint and offline use. Builds never make network calls. A browser also retains the last
successful feed in local storage. Network errors, bad data, an empty response or a stale CDN
response cannot erase a more recent valid headline. Older retained stories use “Recent”
with their original date. After seven days, the last-resort link leads to the site's
AI reporting; it does not pretend an old article is trending.

## Monitoring and verification

A fresh candidate and at least one working feed are required before publishing. Total feed
failure preserves the last snapshot and fails the job. The job verifies the public feed's
refresh timestamp and the deployed homepage integration, then opens the **actual live page**
in Playwright at desktop and phone widths. It succeeds only when that refresh is visible with
its source, date and link. Website deployment failures no longer block news-data publication.

- `python3 scripts/site/news_headlines.py --self-test`, `--check`, `--health`
- `python3 scripts/site/news_publish.py --self-test`
- `python3 scripts/site/news_publish.py --restore` (GitHub read)
- `python3 scripts/site/news_headlines.py --collect` (source reads, local snapshot write)
- `python3 scripts/site/news_publish.py --publish` (validated data branch write)
- `python3 scripts/site/news_headlines.py --live-check` (public feed and integration)
- `node tests/news_headline.mjs` (offline fixtures under production CSP, responsive layout,
  fresh data replacing stale/empty HTML, failed requests, reload cache, aging and invalid data)
- `node tests/news_live.mjs` (production browser check; optional `NEWS_CHECKED_AT` minimum)

The failure repaired here on September 17 had two causes: the browser deleted headlines after
36 hours, and an unrelated Water Watch test blocked the full-site release the news job depended
on. Neither extending an expiry alone nor adding another empty-state message solves that.
