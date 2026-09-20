# Homepage Trending headline

The compact homepage strip links to an attributed publisher headline and its original feed date.
Up to ten distinct headlines rotate every five seconds, with a gentle fade. Six-hour editions
refresh the story pool. No model calls, article scraping or rewritten titles are used. Bounded publisher feed excerpts can establish a Texas connection omitted from a headline.

## Sources and relevance

The feeds in `config/news_sources.json` include Texas newsrooms, independent technology reporting,
research and first-party AI announcements. SiliconANGLE, AI News, GeekWire, TechSpot and
ScienceDaily supplement Dallas Innovates, The Texas Tribune, Data Center Dynamics, MIT News,
OpenAI, NVIDIA and Google. The production collector makes no GDELT request.

Every feed is checked against its host's robots policy. Requests have a response-size limit,
a timeout and bounded parallelism. Each source gets one attempt in a run. ETag and Last-Modified
validators reduce repeat transfers. A failed source carries a persisted retry time into the next
successful snapshot. HTTP 429 respects Retry-After rather than immediately trying again.
Other publishers keep the collection running. Only headline metadata and plain-text feed excerpts of at most 1000 characters are retained. Publisher boilerplate and post-attribution footers are removed before classification.

Every candidate must have both a Texas connection and AI or technology relevance. Texas
places and institutions must appear in the headline or its publisher-provided feed excerpt.
A publisher address, feed name or company reputation is not evidence of a Texas story.
Generic global AI coverage is never a fallback. Stocks, sports and promotional headlines
are excluded. The same checks cover the seed, browser cache, live responses and every queued
story. Regression cases include the Malaysia data center, generic OpenAI cybersecurity and MIT's
reading-program story. Dallas Innovates' site-wide North Texas boilerplate does not count.

Texas AI ranks before other Texas technology reporting. Reports under 72 hours rank before
older reports. Independent reporting precedes company announcements within a category.
Independent coverage and source age rank the remaining choices. Sister outlets and identical
wire headlines cannot inflate coverage. This is a coverage proxy rather than audience analytics.

## Six-hour editions

The edition boundaries match the collector schedule, at 01:23, 07:23, 13:23 and 19:23 UTC.
Each successful collection prepares up to ten stories for the current edition and each of up to
three reserve editions. The new collection can bring freshly published reporting into the current
batch. Already-open pages keep the active link stable during reading or interaction.
Membership comes from the best ten distinct eligible stories at each edition boundary, ranked by
Texas AI relevance, freshness, independent sourcing and coverage. Having appeared before never
lowers a story's rank. Strong stories can stay across editions or return after being displaced.
There is no daily quota and no requirement to find ten replacements at every refresh.

Within that pool the least recently used lead goes first. Two eligible stories alternate their
leads and can lead again after twelve hours. A single qualifying story can remain. This lead
rotation never pulls a lower-ranked story into the pool just because it has not appeared before.
Identical input on a retry keeps the current order. New reporting can displace a weaker story
immediately on collection, including during the same six-hour slot.

Every queued story must be under seven days old at its scheduled start. Reports older than
72 hours display Recent with their original date. Quiet days can use fewer than ten Texas
stories and reuse eligible Texas reports. They never import global AI stories to fill slots. The browser advances the
queue at the edition boundary, on reload and when returning to the tab. A focused or hovered
carousel waits until the reader moves away or navigates before replacing its links. This works even if
GitHub starts a scheduled collection late or a feed request fails. The browser checks for a
new published queue on load and every 15 minutes while visible. Collection timestamps never
replace the original story date or make an old article appear new. The browser removes each
story at its own seven-day deadline, including offline. One expired member never discards the
rest of a still-eligible pool.

An exhausted queue retains a dated last-good headline labelled Recent. Nothing invents news
when sources fail. A snapshot without an eligible next edition or two independent working feeds fails the
publishing health check. A quiet period with just one eligible Texas story retains that
story with its original date and pauses automatic rotation until another story qualifies.

## Five-second reading experience

The complete headline, publisher and source date fade together. Each story occupies the same
grid cell and the tallest story reserves the height. No headline is truncated. The transition
takes 700 milliseconds, included in the five-second cadence. No request is made per transition.
A faint accent moves along the upper edge when motion is enabled. Hover adds a soft warm glow.

The compact controls provide previous and next buttons. The visible date shows month and day.
The full source timestamp stays in the time element. Hover, keyboard focus and pressing a story
pause rotation while the reader interacts. Rotation resumes after they move away. Reduced-motion
preferences use manual navigation without automatic rotation or fades. Background
tabs and offscreen carousels stop their timers. Automatic changes are not live announcements.
Only the visible story is accessible to the keyboard and assistive technology.

The feed preserves the original single-story fields for older pages during rollout. Both the
collector and the browser validate every member of every new story pool. Quiet periods use fewer
stories or reuse qualified reporting rather than pad the carousel with unrelated or stale links.

## Publication and verification

`.github/workflows/news.yml` collects every six hours. It restores the published observation,
rotation and source-backoff history, then validates and publishes only
`news-data/ledger/news/latest.json`. Ordinary refreshes do not change main or trigger Pages.
Non-forced updates and timestamp checks prevent an older run from overwriting a newer one.

Generated HTML embeds a seed queue for first paint. Browser local storage retains the last
valid queue. Publisher attribution, dates, HTTPS links, relevance, queue bounds and ordering
are checked before display. The homepage CSP permits only the exact public data path.

Each production run checks the public snapshot and opens the actual homepage at desktop and
phone widths. It observes a full five-second rotation through the current story pool, including attribution and
stable height, then advances that browser's clock with feed
requests blocked to prove the next edition changes the headline. Local tests also cover
restarts, unchanged feeds, duplicate stories, exhausted queues, 304, 429 and malicious reserves.

- `python3 scripts/site/news_headlines.py --self-test`, `--check`, `--health`
- `python3 scripts/site/news_publish.py --self-test`
- `python3 scripts/site/news_publish.py --restore` and `--publish`
- `python3 scripts/site/news_headlines.py --collect` and `--live-check`
- `node tests/news_headline.mjs` and `node tests/news_live.mjs`
