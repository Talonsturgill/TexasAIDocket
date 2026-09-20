#!/usr/bin/env python3
"""Rotating, attributed AI headlines, selected without a language model.

Publisher feeds provide titles and source dates. We rank recent coverage from named newsrooms,
group sister outlets, and retain the publisher's headline verbatim. Only headline metadata and bounded feed excerpts are retained; article pages are never fetched. See knowledge/shared/NEWS_CHIP.md.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import email.utils
import xml.etree.ElementTree as ET
import datetime as dt
import hashlib
import html
import json
import math
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import news_feeds
from html.parser import HTMLParser
from pathlib import Path
from csp import NEWS_FEED_URL

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / 'ledger/news/latest.json'
CONFIG = json.loads((ROOT / 'config/news_sources.json').read_text())
SOURCES = CONFIG['sources']
RSS_FEEDS = tuple(CONFIG['feeds'])
UTC = dt.timezone.utc
MAX_AGE = dt.timedelta(days=7)
TRENDING_AGE = dt.timedelta(hours=72)
MAX_CHECK_AGE = dt.timedelta(hours=18)
FIRST_PARTY_GROUPS = frozenset(CONFIG.get('first_party_groups', []))
EDITION_LENGTH = dt.timedelta(hours=6)
STORIES_PER_EDITION = 10
# Matches the existing 01:23, 07:23, 13:23, 19:23 UTC collection schedule.
EDITION_ANCHOR = dt.datetime(1970, 1, 1, 1, 23, tzinfo=UTC)
UA = 'TexasAIDocket/1.0 (+https://texasaidocket.com)'
TEXAS = re.compile(r'\b(?:texas|texans|dallas|houston|fort worth|san antonio|el paso|'
                   r'round rock|abilene|amarillo|lubbock|corpus christi|dfw|txdot|ercot|'
                   r'ut austin|ut dallas|ut arlington|texas a&m|unt|'
                   r'southern methodist university)\b', re.I)
AUSTIN = re.compile(r'^(?:Austin[’\x27]s|Austin[- ]based|Austin (?:AI|tech|startup|data|city|council|robot|software|chip))\b', re.I)
# Initialisms are unambiguous in this Dallas newsroom's local reporting, but not worldwide.
DALLAS_INSTITUTIONS = re.compile(r'\b(?:SMU|UTD|UTA)\b')
TECH = re.compile(r'\b(?:AI|artificial intelligence|machine learning|data[- ]cent[er]+s?|'
                  r'tech(?:nology|nologies)?|semiconductors?|microchips?|robot\w*|'
                  r'autonomous|self[- ]driving|cyber\w*|software|quantum|computing|'
                  r'chatbots?|air[- ]tax(?:i|is)|air taxis|evtol|broadband)\b', re.I)
AI = re.compile(r'\b(?:AI|artificial intelligence|machine learning|neural networks?|'
                r'LLMs?|large language models?|OpenAI|ChatGPT|GPT[- ]?\d|'
                r'Anthropic|DeepSeek|Claude Code|generative|deep learning|inference|MLPerf)\b', re.I)
JUNK = re.compile(r'\b(?:stock|shares|price target|earnings|buy rating|sponsored|press release|'
                  r'scholarship|obituary|football|basketball|baseball|betting|webinar|'
                  r'register now|join theCUBE|\w+ vs\.? \w+)\b', re.I)
STOP = set('a an and are as at be by for from has in into is it of on or over s that the their '
           'this to with texas texans dallas houston austin fort worth san antonio new'.split())


def stamp(value: dt.datetime) -> str:
    return value.astimezone(UTC).isoformat(timespec='seconds').replace('+00:00', 'Z')


def instant(value: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.tzinfo is None:
        raise ValueError('timestamp must include its timezone')
    return parsed.astimezone(UTC)


def source(url: str) -> tuple[str, str] | None:
    """Only named public newsrooms; a suffix must begin at a DNS label boundary."""
    try:
        p = urllib.parse.urlsplit(url)
        if p.scheme not in ('http', 'https') or p.username or p.password or p.port not in (None, 80, 443):
            return None
        if any(ord(c) < 33 for c in url) or '\\' in url:
            return None
        host = p.hostname or ''
        for domain, info in SOURCES.items():
            if host == domain or host.endswith('.' + domain):
                return tuple(info)
    except ValueError:
        pass
    return None


def canonical(url: str) -> str:
    p = urllib.parse.urlsplit(url)
    query = urllib.parse.urlencode([(k, v) for k, v in urllib.parse.parse_qsl(p.query)
                                   if not k.lower().startswith(('utm_', 'fbclid', 'gclid'))])
    return urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, query, ''))


def tokens(title: str) -> set[str]:
    text = title.lower()
    for pattern, replacement in [(r'air[- ]tax(?:is|ies|i)\b|air taxis', 'airtaxi'),
                                  (r'artificial intelligence', 'ai'),
                                  (r'data[- ]cent(?:er|re)s?', 'datacenter'),
                                  (r'\b(?:testing|tests)\b', 'test')]:
        text = re.sub(pattern, replacement, text)
    return {t.rstrip('s') if len(t) > 4 else t for t in re.findall(r'[a-z0-9]+', text)
            if t not in STOP and len(t) > 1}


def related(a: dict, b: dict) -> bool:
    left, right = tokens(a['title']), tokens(b['title'])
    common = left & right
    return len(common) >= 3 and len(common) / math.sqrt(len(left) * len(right)) >= .45


def topics(article: dict) -> tuple[bool, bool]:
    title = article['title']
    newsroom = source(article['url'])
    text = title + ' ' + article.get('summary', '')
    texas = bool(TEXAS.search(text) or AUSTIN.search(title) or
                 (newsroom and newsroom[1] == 'dallasinnovates' and DALLAS_INSTITUTIONS.search(title)))
    # Feed names and publisher identity establish provenance, never subject relevance.
    ai = bool(AI.search(text))
    return texas, ai


def eligible(article: dict, now: dt.datetime) -> bool:
    try:
        title = article['title']
        if not isinstance(title, str) or not 20 <= len(title) <= 220 or len(title.split()) > 32:
            return False
        newsroom = source(article['url'])
        summary = article.get('summary', '')
        if not isinstance(summary, str) or len(summary) > 1000 or '<' in summary or '>' in summary:
            return False
        texas, ai = topics(article)
        if (not newsroom or not article['url'].startswith('https://') or not (texas and (ai or TECH.search(title))) or JUNK.search(title)):
            return False
        age = now - instant(article['first_seen_at'])
        if not dt.timedelta(0) <= age < MAX_AGE:
            return False
        # A newly indexed archive article is not new coverage. Reject old dates when the
        # publisher exposes one in the URL. A discovery observation is not a publication date.
        date = re.search(r'/(20\d{2})/(\d{2})/(\d{2})/', article['url'])
        if date:
            day = dt.date(*(int(n) for n in date.groups()))
            if not dt.timedelta(0) <= now.date() - day <= MAX_AGE:
                return False
        return True
    except (KeyError, TypeError, ValueError, OverflowError):
        return False


def rank(articles: list[dict], now: dt.datetime) -> list[dict]:
    unique = {}
    for article in articles:
        if eligible(article, now):
            url = canonical(article['url'])
            # Earliest observation wins even when a feed repeats or re-indexes a URL.
            if url not in unique or article['first_seen_at'] < unique[url]['first_seen_at']:
                unique[url] = {**article, 'url': url}
    rows = list(unique.values())
    scored = []
    for article in rows:
        matches = [a for a in rows if a is article or related(article, a)]
        groups = {source(a['url'])[1] for a in matches}
        # Identical wire copy carried by many groups is still one piece of reporting.
        distinct = {tuple(sorted(tokens(a['title']))) for a in matches}
        coverage = min(len(groups), len(distinct))
        age = (now - instant(article['first_seen_at'])).total_seconds() / 3600
        score = round((1 + math.log2(coverage)) * 2 ** (-age / 24), 6)
        texas, ai = topics(article)
        priority = (0 if ai else 1) + (3 if age >= 72 else 0)
        scored.append({**article, 'publisher': source(article['url'])[0],
                       'coverage': coverage, 'score': score, 'priority': priority})
    return sorted(scored, key=lambda a: (a['priority'], source(a['url'])[1] in FIRST_PARTY_GROUPS,
                                         -a['score'], a['first_seen_at'], a['url']))


def edition_start(now: dt.datetime) -> dt.datetime:
    return EDITION_ANCHOR + ((now - EDITION_ANCHOR) // EDITION_LENGTH) * EDITION_LENGTH


def edition_story(data: dict, now: dt.datetime) -> dict | None:
    started = [entry for entry in data.get('editions', []) if instant(entry['starts_at']) <= now]
    return started[-1]['selected'] if started else data.get('selected')


def rotation(articles: list[dict], now: dt.datetime, previous: dict) -> dict:
    """Reconsider the best reusable Texas stories each slot; vary leads within that pool."""
    start = edition_start(now)
    history = []
    for entry in previous.get('history', [])[-32:]:
        try:
            if (isinstance(entry.get('title'), str) and source(entry['url']) and
                    now - MAX_AGE <= instant(entry['shown_at']) <= now):
                history.append({key: entry[key] for key in ('url', 'title', 'shown_at')})
        except (KeyError, TypeError, ValueError):
            continue
    old_editions = []
    for entry in previous.get('editions', [])[:4]:
        try:
            if not eligible(entry['selected'], now):
                continue
            instant(entry['starts_at'])
            old_editions.append(entry)
            if instant(entry['starts_at']) <= now:
                history.append({'url': entry['selected']['url'], 'title': entry['selected']['title'],
                                'shown_at': entry['starts_at']})
        except (KeyError, TypeError, ValueError):
            continue
    if not old_editions and not history and previous.get('selected') and previous.get('checked_at'):
        history.append({'url': previous['selected']['url'], 'title': previous['selected']['title'],
                        'shown_at': previous['checked_at']})
    history = sorted({(entry['shown_at'], entry['url']): entry for entry in history}.values(),
                     key=lambda entry: (entry['shown_at'], entry['url']))[-32:]
    editions, used = [], list(history)
    for offset in range(4):
        begins = start + offset * EDITION_LENGTH
        at = max(now, begins)
        # Quality and source age choose membership, never how many times a story ran.
        # The same strong reporting can fill every edition without exhausting the pool.
        pool = []
        for row in rank(articles, at):
            if not any(row['url'] == old['url'] or related(row, old) for old in pool):
                pool.append(row)
            if len(pool) == STORIES_PER_EDITION:
                break
        if not pool:
            break
        old = next((entry for entry in old_editions if entry['starts_at'] == stamp(begins)), None)
        # Retain a queued lead only while it still earns a place in the best current pool.
        chosen = next((row for row in pool if old and row['url'] == old['selected']['url']), None) if offset == 0 else None
        if chosen is None:
            # Repeats are welcome. Least-recently led wins only WITHIN the best pool.
            # Two stories alternate every six hours and can lead again after twelve.
            def last_shown(row):
                return max((entry['shown_at'] for entry in used
                            if row['url'] == entry['url'] or related(row, entry)), default='')
            chosen = min(pool, key=last_shown)
        previous_pool = old.get('stories', []) if old else []
        if (offset == 0 and previous.get('checked_at') and
                edition_start(instant(previous['checked_at'])) == start and
                {row['url'] for row in previous_pool} == {row['url'] for row in pool}):
            # Identical input on a retry keeps the links in the same order.
            by_url = {row['url']: row for row in pool}
            pool = [by_url[row['url']] for row in previous_pool]
        pool = [chosen] + [row for row in pool if row['url'] != chosen['url']]
        editions.append({'starts_at': stamp(begins), 'selected': chosen, 'stories': pool})
        used.append({'url': chosen['url'], 'title': chosen['title'], 'shown_at': stamp(begins)})
    return {'rotation_version': 1, 'carousel_version': 1, 'editions': editions, 'history': history}


def snapshot(payload: dict, now: dt.datetime, previous: dict | None = None, *, rotate=False) -> dict:
    now = instant(stamp(now))
    if not isinstance(payload, dict) or not isinstance(payload.get('articles'), list):
        raise ValueError('news source did not return an article list')
    known = {a['url']: a['first_seen_at'] for a in (previous or {}).get('articles', [])}
    rows = []
    for raw in payload['articles']:
        try:
            if not isinstance(raw, dict) or not isinstance(raw.get('url'), str) or not isinstance(raw.get('title'), str):
                continue
            url = canonical(raw['url'])
            seen = dt.datetime.strptime(raw['seendate'], '%Y%m%dT%H%M%SZ').replace(tzinfo=UTC)
            row = {'title': html.unescape(' '.join(raw['title'].split())), 'url': url,
                   'first_seen_at': min(known.get(url, stamp(seen)), stamp(seen))}
            if isinstance(raw.get('summary'), str):
                row['summary'] = raw['summary']
            if raw.get('feed') in RSS_FEEDS:
                row['feed'] = raw['feed']
            if raw.get('language') == 'English' and eligible(row, now):
                rows.append(row)
        except (KeyError, TypeError, ValueError):
            continue
    # Retain observations for a week to keep a repeated URL from resetting its own clock.
    for old in (previous or {}).get('articles', []):
        if eligible(old, now):
            rows.append(old)
    unique = {}
    for article in rows:
        current = unique.setdefault(article['url'], dict(article))
        current['first_seen_at'] = min(current['first_seen_at'], article['first_seen_at'])
    rows = sorted(unique.values(), key=lambda a: a['url'])
    ranked = rank(rows, now)
    selected = ranked[0] if ranked else None
    result = {'_spec': 2, 'checked_at': stamp(now), 'provider': 'Publisher RSS and Atom',
            'response_sha256': hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
            'articles': rows, 'selected': selected,
            'expires_at': stamp(instant(selected['first_seen_at']) + MAX_AGE) if selected else None}
    if rotate:
        result.update(rotation(rows, now, previous or {}))
        result['selected'] = result['editions'][0]['selected'] if result['editions'] else None
        result['expires_at'] = stamp(instant(result['selected']['first_seen_at']) + MAX_AGE) if result['selected'] else None
    return result


def observation_history(data: dict) -> dict:
    """Import source observations without trusting an older schema's derived ranking."""
    if not isinstance(data, dict) or not isinstance(data.get('articles'), list):
        raise ValueError('news history must contain an article list')
    rows = []
    for raw in data['articles']:
        try:
            if not isinstance(raw, dict) or not isinstance(raw.get('title'), str):
                continue
            url = canonical(raw['url'])
            if not url.startswith('https://') or not source(url) or not 20 <= len(raw['title']) <= 220:
                continue
            row = {'title': raw['title'], 'url': url,
                   'first_seen_at': stamp(instant(raw['first_seen_at']))}
            if isinstance(raw.get('summary'), str):
                row['summary'] = raw['summary']
            if raw.get('feed') in RSS_FEEDS:
                row['feed'] = raw['feed']
            rows.append(row)
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    history = {'articles': rows}
    for key in ('checked_at', 'selected', 'rotation_version', 'carousel_version', 'editions', 'history', 'feed_state'):
        if key in data:
            history[key] = data[key]
    return history


def validate(data: dict) -> None:
    if data.get('_spec') != 2 or data.get('provider') not in ('GDELT and publisher RSS', 'Publisher RSS and Atom'):
        raise ValueError('unknown news snapshot')
    now = instant(data['checked_at'])
    if data.get('carousel_version') not in (None, 1) or (data.get('carousel_version') == 1 and data.get('rotation_version') != 1):
        raise ValueError('unknown carousel snapshot')
    ranked = rank(data['articles'], now)
    selected = ranked[0] if ranked else None
    if data.get('rotation_version') == 1:
        editions = data.get('editions')
        if not isinstance(editions, list) or len(editions) > 4:
            raise ValueError('invalid rotation queue')
        for offset, entry in enumerate(editions):
            begins = edition_start(now) + offset * EDITION_LENGTH
            at = max(now, begins)
            story = entry['selected']
            if (entry['starts_at'] != stamp(begins) or story not in rank(data['articles'], at) or
                    at - instant(story['first_seen_at']) >= MAX_AGE):
                raise ValueError('rotation contains an invalid or stale headline')
            if data.get('carousel_version') == 1:
                pool = entry.get('stories')
                if not isinstance(pool, list) or not 1 <= len(pool) <= STORIES_PER_EDITION or pool[0] != story:
                    raise ValueError('invalid edition story pool')
                if offset and len(pool) > 1 and (story['url'] == editions[offset - 1]['selected']['url'] or
                        related(story, editions[offset - 1]['selected'])):
                    raise ValueError('consecutive leads repeat despite available alternatives')
                ranked_at = rank(data['articles'], at)
                for index, candidate in enumerate(pool):
                    if candidate not in ranked_at or at - instant(candidate['first_seen_at']) >= MAX_AGE:
                        raise ValueError('carousel contains an invalid or stale headline')
                    if any(candidate['url'] == old['url'] or related(candidate, old) for old in pool[:index]):
                        raise ValueError('carousel repeats a headline or story')
        selected = editions[0]['selected'] if editions else None
    if selected != data['selected']:
        raise ValueError('selected story disagrees with the recorded candidates and ranking')
    expected = stamp(instant(selected['first_seen_at']) + MAX_AGE) if selected else None
    if data['expires_at'] != expected:
        raise ValueError('headline expiry disagrees with its first observation')


def load() -> dict:
    if not STATE.exists():
        return {}
    data = json.loads(STATE.read_text())
    validate(data)
    return data


def public_snapshot(data: dict) -> dict:
    keys = ('_spec', 'checked_at', 'selected', 'expires_at', 'rotation_version', 'carousel_version', 'editions')
    return {key: data[key] for key in keys if key in data}


def markup(today: str, data: dict | None = None) -> str:
    data = load() if data is None else data
    selected = data.get('selected')
    build_start = dt.datetime.combine(dt.date.fromisoformat(today), dt.time(), UTC)
    if selected and build_start >= instant(data['expires_at']):
        selected = None
    e = html.escape
    recent = selected and (build_start - instant(selected['first_seen_at']) >= TRENDING_AGE or
                           build_start - instant(data['checked_at']) > MAX_CHECK_AGE)
    status = ('recent' if recent else 'current') if selected else 'empty'
    label = 'Recent' if recent else 'Trending'
    title = (selected['title'] if selected else 'Explore the latest AI reporting')
    publisher = selected['publisher'] if selected else ''
    date = ''
    if selected:
        observed = instant(selected['first_seen_at'])
        day = observed.day
        suffix = 'th' if 10 <= day % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        date = f'{observed:%B} {day}{suffix}'
    url = selected['url'] if selected else '/articles/'
    first_seen = selected['first_seen_at'] if selected else ''
    description = ('Texas AI headlines rotate every five seconds and refresh every six hours. '
                   'The date is the publisher feed date or first observation. Opens the source in a new tab.')
    relevance = {name: pattern.pattern for name, pattern in
                 [('texas', TEXAS), ('austin', AUSTIN), ('local', DALLAS_INSTITUTIONS),
                  ('tech', TECH), ('ai', AI), ('junk', JUNK)]}
    return (f'<div class="tele news-chip" role="region" aria-roledescription="carousel" '
            f'aria-label="Trending headlines" data-news-status="{status}" '
            f'data-news-feed="{NEWS_FEED_URL}" '
            f'data-news-sources="{e(json.dumps(SOURCES), quote=True)}" '
            f'data-news-relevance="{e(json.dumps(relevance), quote=True)}" '
            f'data-news-initial="{e(json.dumps(public_snapshot(data)), quote=True)}" '
            f'data-checked-at="{e(data.get("checked_at", ""), quote=True)}" '
            f'data-first-seen-at="{e(first_seen)}" data-expires-at="{e(data.get("expires_at") or "")}" '
            f'title="{description}"><div class="news-header"><span class="news-label">{label}</span>'
            '<div class="news-controls" hidden>'
            '<button type="button" class="news-prev" aria-label="Previous headline" title="Previous headline">'
            '<svg aria-hidden="true" viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5">'
            '<path d="m10 3-5 5 5 5"/></svg></button>'
            '<button type="button" class="news-next" aria-label="Next headline" title="Next headline">'
            '<svg aria-hidden="true" viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.5">'
            '<path d="m6 3 5 5-5 5"/></svg></button></div></div>'
            '<div class="news-slides" aria-live="off">'
            '<div class="news-slide" role="group" aria-roledescription="slide" aria-hidden="false">'
            f'<a class="news-link" href="{e(url, quote=True)}" target="_blank" rel="noopener noreferrer">'
            f'<cite class="news-title">{e(title)}</cite><span class="news-meta">'
            f'<cite class="news-source">{e(publisher)}</cite>'
            f'<time class="news-date" datetime="{e(first_seen)}">{date}</time></span>'
            '<svg class="news-arrow" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" '
            'fill="none" stroke="currentColor" stroke-width="1.6"><path d="M7 17 17 7M7 7h10v10"/></svg>'
            '</a></div></div></div><script>' + (ROOT / 'scripts/site/news_runtime.js').read_text() + '</script>')


def rss_articles(body: bytes) -> list[dict]:
    return news_feeds.articles(body)


def collect() -> int:
    now = dt.datetime.now(UTC).replace(microsecond=0)
    previous = {}
    if STATE.exists():
        try:
            previous = observation_history(json.loads(STATE.read_text()))
        except (ValueError, KeyError, TypeError):
            pass
    saved = previous.get('feed_state', {})
    def read_feed(url):
        return url, news_feeds.read(url, saved.get(url, {}), now)
    combined, feeds, feed_state = [], [], {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for url, (rows, report, state) in pool.map(read_feed, RSS_FEEDS):
            combined.extend(rows)
            feeds.append(report)
            feed_state[url] = state
    if not any(feed['status'] in ('ok', 'not_modified') for feed in feeds):
        raise OSError('all news feeds failed; previous published snapshot preserved')
    result = snapshot({'articles': combined}, dt.datetime.now(UTC), previous, rotate=True)
    result['feeds'], result['feed_state'] = feeds, feed_state
    validate(result)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    temp.replace(STATE)
    print(json.dumps({'eligible': len(result['articles']), 'working_feeds': sum(
        feed['status'] in ('ok', 'not_modified') for feed in feeds),
        'editions': [{'starts_at': entry['starts_at'], 'title': entry['selected']['title'],
                      'publisher': entry['selected']['publisher']} for entry in result['editions']]}, ensure_ascii=False))
    return 0


def health_problems(data: dict, now: dt.datetime) -> list[str]:
    """Operational health is separate from the reproducible snapshot/schema check."""
    problems = []
    selected = edition_story(data, now)
    if not selected or now - instant(selected['first_seen_at']) >= MAX_AGE:
        problems.append('no eligible Texas AI or technology headline is available')
    if not dt.timedelta(minutes=-5) <= now - instant(data['checked_at']) <= MAX_CHECK_AGE:
        problems.append('news collection is overdue or its clock is invalid')
    if sum(feed.get('status') in ('ok', 'not_modified') for feed in data.get('feeds', [])) < 1:
        problems.append('no news feed is available')
    if data.get('rotation_version') == 1:
        editions = data['editions']
        if len(editions) < 2 or instant(editions[-1]['starts_at']) <= now:
            next_candidates = rank(data['articles'], edition_start(now) + EDITION_LENGTH)
            if not (selected and next_candidates and all(
                    row['url'] == selected['url'] or related(row, selected) for row in next_candidates)):
                problems.append('no eligible headline is ready for the next six-hour edition')
        groups = {source(feed['url'])[1] for feed in data.get('feeds', [])
                  if feed.get('status') in ('ok', 'not_modified') and source(feed.get('url', ''))}
        if len(groups) < 2:
            problems.append('fewer than two independent publisher feeds are available')
    return problems


class PublishedHeadline(HTMLParser):
    def __init__(self):
        super().__init__()
        self.chips = []
        self.current = None
        self.field = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'news-chip' in attrs.get('class', '').split():
            self.current = {'title': '', 'source': ''}
            self.chips.append((tag, attrs, self.current))
        if self.current is not None:
            for name in ('title', 'source'):
                if 'news-' + name in attrs.get('class', '').split():
                    self.field = (tag, name)

    def handle_data(self, data):
        if self.current is not None and self.field:
            self.current[self.field[1]] += data

    def handle_endtag(self, tag):
        if self.field and self.field[0] == tag:
            self.field = None
        if self.current is not None and tag == self.chips[-1][0]:
            self.current = None


def live_problems(body: str, now: dt.datetime, expected_check: str | None = None,
                  feed_data: dict | None = None) -> list[str]:
    """Check the shipped integration and its separately published feed. Browser QA runs too."""
    parser = PublishedHeadline()
    parser.feed(body)
    if len(parser.chips) != 1:
        return ['the published homepage does not contain exactly one news bar']
    tag, chip, text = parser.chips[0]
    if tag not in ('a', 'div') or chip.get('data-news-feed') != NEWS_FEED_URL:
        return ['the published homepage is not connected to the independent news feed']
    if not feed_data:
        return ['the public headline feed is unavailable']
    try:
        validate(feed_data)
        problems = health_problems(feed_data, now)
        if expected_check and instant(feed_data['checked_at']) < instant(expected_check):
            problems.append('the collected headline has not reached the public feed')
        return problems
    except (KeyError, TypeError, ValueError) as error:
        return ['invalid public headline feed: ' + str(error)]


def browser_feed_url(timestamp: float) -> str:
    # Match news_runtime.js exactly. A unique probe URL can bypass a stale CDN entry
    # and certify a refresh that has not yet reached an ordinary reader.
    return NEWS_FEED_URL + '?refresh=' + str(int(timestamp // 300))


def check_live(wait_seconds: int = 0, expected_check: str | None = None) -> int:
    url = 'https://' + (ROOT / 'docs/CNAME').read_text().strip() + '/'
    deadline = time.monotonic() + wait_seconds
    previous = None
    while True:
        try:
            request = urllib.request.Request(url, headers={'User-Agent': UA, 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read(4_000_001)
                if len(body) > 4_000_000:
                    raise ValueError('homepage exceeded response limit')
            feed_request = urllib.request.Request(browser_feed_url(time.time()),
                                                  headers={'User-Agent': UA, 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(feed_request, timeout=20) as response:
                feed_body = response.read(500_001)
                if len(feed_body) > 500_000:
                    raise ValueError('headline data exceeded response limit')
            problems = live_problems(body.decode('utf-8'), dt.datetime.now(UTC), expected_check,
                                     json.loads(feed_body))
        except (OSError, ValueError) as error:
            problems = [f'could not verify the published headline: {error}']
        if not problems:
            print('news live: a current attributed headline is published')
            return 0
        if problems != previous:
            print('news live: ' + '; '.join(problems), flush=True)
            previous = problems
        if time.monotonic() >= deadline:
            return 1
        time.sleep(min(20, max(0, deadline - time.monotonic())))


def self_test() -> int:
    import copy
    import unittest
    now = instant('2026-09-11T20:00:00Z')
    def row(title='Texas launches Project Nexus to test electric air taxis', host='nbcdfw.com', hours=1, path='story'):
        return {'title': title, 'url': f'https://{host}/{path}', 'first_seen_at': stamp(now-dt.timedelta(hours=hours))}
    class Cases(unittest.TestCase):
        def test_relevance_and_sources(self):
            self.assertTrue(eligible(row(), now))
            self.assertTrue(eligible(row('Austin startup opens an AI research lab'), now))
            self.assertTrue(eligible(row('SMU Gets $19.3M from DOE to Adapt Oil-and-Gas Tech for Critical Minerals Mining', 'dallasinnovates.com'), now))
            self.assertFalse(eligible(row('SMU opens an AI research laboratory', 'reuters.com'), now))
            self.assertFalse(eligible(row("Steve Austin's new AI wrestling game"), now))
            for title in ['Texas Tech wins college football game with AI prediction', 'Austin Butler talks artificial intelligence',
                          'Texas stock shares rise as AI earnings beat estimates', 'AI startup opens an office in Boston',
                          'Texas gets a new museum this weekend', 'Austin Minnesota opens a new AI lab']:
                self.assertFalse(eligible(row(title), now), title)
            for host in ['nbcdfw.com.evil.example', 'unknown.example', '127.0.0.1']:
                self.assertFalse(eligible(row(host=host), now))
            self.assertFalse(source('https://user:password@nbcdfw.com/a'))
            self.assertFalse(source('javascript:alert(1)'))
        def test_texas_scope_covers_live_failures_and_feed_context(self):
            foreign = [
                ('Bitdeer AI to lease 65MW data center in Johor, Malaysia', 'datacenterdynamics.com'),
                ('Cybersecurity researchers gain access to OpenAI’s GitHub repository using Claude', 'siliconangle.com'),
                ('For AI agents, it is the best of times, it is the worst of times', 'siliconangle.com'),
                ('AI data center builder Crusoe valued at $30.9B in $3.9B round', 'siliconangle.com'),
                ('AI researchers develop a safer surgery technique', 'news.mit.edu'),
            ]
            for title, host in foreign:
                candidate = row(title, host)
                self.assertFalse(eligible(candidate, now), title)
                repaired = snapshot({'articles': []}, now, {'articles': [candidate]}, rotate=True)
                self.assertEqual(repaired['editions'], [])
            candidate = row('CoPoint AI acquires a consulting business', 'dallasinnovates.com')
            self.assertFalse(eligible(candidate, now))
            candidate['summary'] = 'Two Dallas-based AI consulting firms combined.'
            self.assertTrue(eligible(candidate, now))
            for summary in [None, ['Texas'], '<b>Texas</b>', 'Texas ' * 300]:
                self.assertFalse(eligible({**candidate, 'summary': summary}, now))
            boilerplate = "<p>Dallas Innovates, Every Day: Here's what's new + next in North Texas.</p>"
            excerpt = news_feeds.summary_text(boilerplate + '<p>An AI company expands in Malaysia.</p>' +
                         '<p>The post Story appeared first on Dallas Innovates.</p>')
            self.assertEqual(excerpt, 'An AI company expands in Malaysia.')
            self.assertFalse(eligible({**candidate, 'summary': excerpt}, now))
            self.assertEqual(news_feeds.summary_text(boilerplate + '<p>Dallas-based AI firms combine.</p>'),
                             'Dallas-based AI firms combine.')

        def test_quiet_texas_pool_keeps_dates_and_rejects_global_padding(self):
            rows = [row('Texas AI researchers test a surgery technique', hours=80),
                    row('Dallas launches autonomous transit pilot program', hours=90, path='transit'),
                    row('AI infrastructure expands in Malaysia', 'datacenterdynamics.com', hours=1)]
            result = snapshot({'articles': []}, now, {'articles': rows}, rotate=True)
            validate(result)
            self.assertEqual(len(result['articles']), 2)
            self.assertEqual([len(e['stories']) for e in result['editions']], [2, 2, 2, 2])
            self.assertIn('Recent', markup('2026-09-11', result))
            self.assertEqual(result['selected']['first_seen_at'], rows[0]['first_seen_at'])

        def test_single_texas_story_survives_quiet_refresh(self):
            first = snapshot({'articles': []}, now, {'articles': [row()]}, rotate=True)
            later = now + EDITION_LENGTH
            second = snapshot({'articles': []}, later, first, rotate=True)
            validate(second)
            self.assertEqual(second['selected']['url'], first['selected']['url'])
            self.assertEqual(second['selected']['first_seen_at'], first['selected']['first_seen_at'])
            self.assertEqual(len(second['editions'][0]['stories']), 1)
            second['feeds'] = [{'url': RSS_FEEDS[0], 'status': 'ok'}, {'url': RSS_FEEDS[1], 'status': 'ok'}]
            self.assertEqual(health_problems(second, later), [])

        def test_freshness(self):
            self.assertTrue(eligible(row(hours=36), now))
            self.assertFalse(eligible(row(hours=168), now))
            self.assertFalse(eligible(row(hours=-1), now))
            self.assertFalse(eligible(row(path='2020/09/11/archive'), now))
            self.assertEqual(rank([], now), [])
        def test_coverage_and_syndication(self):
            a = row('Texas launches Project Nexus to test AI air taxis')
            b = row('Texas launches Project Nexus AI air taxi pilot tests', 'cbs4local.com')
            c = row('Texas AI startup opens a new robotics laboratory', 'dallasinnovates.com')
            ranked = rank([c, b, a, a], now)
            self.assertEqual(ranked[0]['coverage'], 2)
            copies = [row(host=h) for h in ['nbcdfw.com', 'cbs4local.com', 'cbsaustin.com']]
            self.assertEqual(rank(copies, now)[0]['coverage'], 1)
            self.assertEqual(rank([row(hours=30), c], now)[0]['url'], c['url'])
        def test_snapshot_and_reindex(self):
            p = {'articles': [{'title': row()['title'], 'url': row()['url'], 'language': 'English', 'seendate': '20260911T190000Z'}]}
            s = snapshot(p, now.replace(microsecond=123456))
            validate(s)
            p['articles'][0]['title'] = 'Texas expands Project Nexus to test electric air taxis'
            p['articles'][0]['seendate'] = '20260912T200000Z'
            later = snapshot(p, now+dt.timedelta(days=1), s)
            self.assertEqual(later['expires_at'], s['expires_at'])
            self.assertEqual(later['selected']['title'], p['articles'][0]['title'])
            p['articles'][0]['seendate'] = '20260913T200000Z'
            self.assertEqual(snapshot(p, now+dt.timedelta(days=2), later)['expires_at'], s['expires_at'])
            self.assertIsNone(snapshot({'articles': []}, now+dt.timedelta(days=8), later)['selected'])
            broken = copy.deepcopy(s)
            broken['selected']['title'] = 'invented'
            with self.assertRaises(ValueError): validate(broken)
            with self.assertRaises(ValueError): snapshot({}, now)
        def test_failed_fetch_preserves_snapshot(self):
            from unittest.mock import patch
            import tempfile
            with tempfile.TemporaryDirectory() as directory:
                state = Path(directory) / 'latest.json'
                state.write_text('last known snapshot')
                with patch(__name__ + '.STATE', state), patch.object(news_feeds, 'request', side_effect=TimeoutError()):
                    with self.assertRaises(OSError): collect()
                self.assertEqual(state.read_text(), 'last known snapshot')

        def test_rss(self):
            body = b'<rss><channel><item><title>UNT to launch an AI college</title><link>https://dallasinnovates.com/college/</link><pubDate>Fri, 11 Sep 2026 18:00:00 +0000</pubDate></item><item><title>Undated</title></item></channel></rss>'
            articles = rss_articles(body)
            self.assertEqual(len(articles), 1)
            self.assertEqual(rss_articles(body.replace(b' +0000', b'')), [])
            with self.assertRaises(ValueError): rss_articles(b'<html>unavailable</html>')
            self.assertEqual(articles[0]['seendate'], '20260911T180000Z')
            self.assertIsNotNone(snapshot({'articles': articles}, now)['selected'])

        def test_partial_feed_failure(self):
            from unittest.mock import patch
            import tempfile
            published = email.utils.format_datetime(dt.datetime.now(UTC) - dt.timedelta(hours=1))
            body = ('<rss><channel><item><title>Texas AI research laboratory opens</title>'
                    '<link>https://dallasinnovates.com/research/</link><pubDate>' + published +
                    '</pubDate></item></channel></rss>').encode()
            def read(url, previous, checked):
                if url == RSS_FEEDS[-1]:
                    return [], {'url': url, 'status': 'unavailable'}, {}
                return [{**a, 'feed': url} for a in rss_articles(body)], {'url': url, 'status': 'ok'}, {}
            with tempfile.TemporaryDirectory() as directory:
                state = Path(directory) / 'latest.json'
                with patch(__name__ + '.STATE', state), patch.object(news_feeds, 'read', side_effect=read):
                    self.assertEqual(collect(), 0)
                    result = load()
                self.assertEqual(result['selected']['title'], 'Texas AI research laboratory opens')
                self.assertEqual(sum(f['status'] == 'ok' for f in result['feeds']), len(RSS_FEEDS) - 1)
                self.assertEqual(health_problems(result, dt.datetime.now(UTC)), [])

        def test_empty_refresh_is_not_operational_success(self):
            s = snapshot({'articles': []}, now)
            s['feeds'] = [{'status': 'ok'}, {'status': 'ok'}]
            validate(s)  # An honest empty snapshot is publishable, but needs attention.
            self.assertIn('no eligible Texas AI or technology headline is available', health_problems(s, now))
            self.assertIn('data-news-status="empty"', markup('2026-09-11', s))

        def test_operational_health(self):
            s = snapshot({'articles': []}, now, {'articles': [row()]})
            s['feeds'] = [{'status': 'ok'}, {'status': 'ok'}]
            self.assertEqual(health_problems(s, now), [])
            self.assertIn('news collection is overdue or its clock is invalid',
                          health_problems(s, now + dt.timedelta(hours=19)))
            self.assertIn('no eligible Texas AI or technology headline is available',
                          health_problems(s, now + dt.timedelta(hours=169)))
            s['feeds'][1]['status'] = 'unavailable'
            self.assertEqual(health_problems(s, now), [])
            s['feeds'][0]['status'] = 'unavailable'
            self.assertIn('no news feed is available', health_problems(s, now))

        def test_texas_required_even_on_quiet_days(self):
            global_ai = row('AI researchers develop a safer surgery technique', 'news.mit.edu', path='ai')
            self.assertFalse(eligible(global_ai, now))
            self.assertFalse(eligible(row('Cute critters launch on a gaming service', 'blogs.nvidia.com'), now))
            texas_ai = row('Texas researchers develop a safer AI surgery technique', 'dallasinnovates.com')
            self.assertEqual(rank([global_ai, texas_ai], now)[0]['url'], texas_ai['url'])
            self.assertEqual(rank([global_ai, row(hours=40)], now)[0]['url'], row()['url'])
            dated = snapshot({'articles': []}, now, {'articles': [row(hours=100)]})
            self.assertIsNotNone(dated['selected'])
            self.assertIn('Recent', markup('2026-09-11', dated))

        def test_feed_membership_never_establishes_relevance(self):
            for title in ['A new chapter for MIT Reads',
                          'MIT spinout turns plastic waste into resilient building materials',
                          'Measure by measure, studying society accurately']:
                article = {**row(title, 'news.mit.edu'),
                           'feed': 'https://news.mit.edu/rss/topic/artificial-intelligence2'}
                self.assertFalse(eligible(article, now), title)
                # Restored observations must not resurrect the same irrelevant story.
                repaired = snapshot({'articles': []}, now, {'articles': [article]})
                self.assertEqual(repaired['articles'], [])
                self.assertIsNone(repaired['selected'])
            for host, feed in [('openai.com', 'https://openai.com/news/rss.xml'),
                               ('blog.google', 'https://blog.google/technology/ai/rss/')]:
                self.assertFalse(eligible({**row('A community reading program opens today', host), 'feed': feed}, now))
            self.assertTrue(eligible({**row('Texas AI technique makes surgery safer and more precise', 'news.mit.edu'),
                                      'feed': 'https://news.mit.edu/rss/topic/artificial-intelligence2'}, now))

        def test_live_health(self):
            s = snapshot({'articles': []}, now, {'articles': [row()]})
            s['feeds'] = [{'status': 'ok'}]
            page = markup('2026-09-11', s)
            self.assertEqual(live_problems(page, now, s['checked_at'], s), [])
            self.assertTrue(live_problems('<main>Unchanged homepage</main>', now, feed_data=s))
            self.assertTrue(live_problems(page, now, stamp(now + dt.timedelta(hours=6)), s))
            self.assertTrue(live_problems(page, now + dt.timedelta(hours=73), feed_data=s))
            self.assertTrue(live_problems(page.replace('data-news-feed', 'missing-feed'), now, feed_data=s))
            broken = copy.deepcopy(s)
            broken['selected']['url'] = 'https://evil.example/story'
            self.assertTrue(live_problems(page, now, feed_data=broken))
            self.assertTrue(live_problems(page, now))

        def test_publication_probe_uses_reader_cache_bucket(self):
            start = instant('2026-09-19T13:35:00Z').timestamp()
            expected = NEWS_FEED_URL + '?refresh=' + str(int(start / 300))
            self.assertEqual(browser_feed_url(start), expected)
            self.assertEqual(browser_feed_url(start + 299.999), expected)
            self.assertNotEqual(browser_feed_url(start + 300), expected)

        def test_markup(self):
            r = row('Texas AI lab announces <script> & "new" tools')
            s = snapshot({'articles': []}, now, {'articles':[r]})
            out = markup('2026-09-11', s)
            self.assertIn('&lt;script&gt; &amp; &quot;new&quot;', out)
            self.assertIn('September 11th</time>', out)
            self.assertIn('<cite class="news-title">', out)
            self.assertIn('rel="noopener noreferrer"', out)
            self.assertIn('Recent', markup('2026-09-15', s))
            self.assertIn('data-news-status="empty"', markup('2026-09-20', s))
            self.assertIn('Explore the latest AI reporting', markup('2026-09-11', {}))

        def test_six_hour_rotation_survives_unchanged_feeds_and_restart(self):
            titles = ['Texas deploys AI for hurricane forecasts', 'AI improves breast cancer screening accuracy',
                      'ChatGPT faces new privacy rules in schools', 'Anthropic releases smaller coding models',
                      'AI accelerators reduce electricity consumption', 'Teachers evaluate AI tutors for mathematics',
                      'AI-generated video raises election security concerns', 'New AI method deciphers ancient manuscripts']
            rows = [row('Texas ' + title, 'siliconangle.com', hours=i + 1, path=str(i)) for i, title in enumerate(titles)]
            previous = {'articles': rows, 'selected': rows[0], 'checked_at': stamp(now - EDITION_LENGTH)}
            first = snapshot({'articles': []}, now, previous, rotate=True)
            validate(first)
            self.assertEqual(len(first['editions']), 4)
            self.assertNotEqual(first['selected']['url'], rows[0]['url'])
            # A retry in this slot stays stable. A delayed next run retains the queued story
            # readers have already seen, and replenishes future slots rather than repeating it.
            same = snapshot({'articles': []}, now + dt.timedelta(minutes=15), first, rotate=True)
            self.assertEqual(first['selected']['url'], same['selected']['url'])
            next_time = instant(first['editions'][1]['starts_at']) + dt.timedelta(hours=2)
            restored = observation_history(json.loads(json.dumps(first)))
            second = snapshot({'articles': []}, next_time, restored, rotate=True)
            validate(second)
            self.assertEqual(second['selected']['url'], first['editions'][1]['selected']['url'])
            self.assertNotEqual(first['selected']['url'], second['selected']['url'])
            shown = {first['selected']['url'], second['selected']['url']}
            for _ in range(4):
                next_time += EDITION_LENGTH
                second = snapshot({'articles': []}, next_time, second, rotate=True)
                validate(second)
                self.assertNotIn(second['selected']['url'], shown)
                shown.add(second['selected']['url'])

        def test_rotation_rejects_repeats_stale_and_off_topic_reserves(self):
            rows = [row('Texas deploys AI for hurricane forecasts', 'siliconangle.com', path='weather'),
                    row('Texas AI improves breast cancer screening accuracy', 'techspot.com', path='medicine')]
            result = snapshot({'articles': []}, now, {'articles': rows}, rotate=True)
            self.assertEqual(len(result['editions']), 4)
            self.assertEqual([e['selected']['url'] for e in result['editions']],
                             [rows[0]['url'], rows[1]['url'], rows[0]['url'], rows[1]['url']])
            for field, value in [('title', 'A new chapter for MIT Reads'), ('url', 'https://evil.example/news'),
                                 ('first_seen_at', stamp(now - dt.timedelta(days=8)))]:
                broken = copy.deepcopy(result)
                broken['editions'][1]['selected'][field] = value
                with self.assertRaises(ValueError): validate(broken)
            broken = copy.deepcopy(result)
            entry = broken['editions'][1]
            repeated = next(s for s in entry['stories'] if s['url'] == broken['selected']['url'])
            entry['selected'] = repeated
            entry['stories'] = [repeated] + [s for s in entry['stories'] if s['url'] != repeated['url']]
            with self.assertRaises(ValueError): validate(broken)
            result['feeds'] = [{'url': RSS_FEEDS[0], 'status': 'ok'}, {'url': RSS_FEEDS[1], 'status': 'not_modified'}]
            self.assertEqual(health_problems(result, now), [])
            self.assertEqual(health_problems(result, now + dt.timedelta(hours=12)), [])
            self.assertTrue(health_problems(result, now + dt.timedelta(hours=19)))

        def test_ten_best_stories_repeat_without_exhausting_the_pool(self):
            # Independent subjects and an irrelevant feed item.
            titles = ['AI diagnoses pancreatic cancer in screening trials', 'ChatGPT faces new school privacy rules',
                      'Anthropic releases smaller coding models', 'Texas deploys AI for hurricane forecasts',
                      'AI accelerators reduce electricity consumption', 'Robots use AI to sort textile waste',
                      'AI video raises election security concerns', 'AI deciphers ancient manuscripts',
                      'AI forecasts volcanic eruptions from seismic signals', 'AI optimizes freight delivery routes',
                      'AI helps astronomers map distant galaxies', 'AI restores hearing through implants',
                      'AI detects deepfake telephone scams', 'AI predicts protein structures for vaccines',
                      'AI improves semiconductor lithography precision', 'AI identifies invasive forest pests',
                      'AI translates endangered Indigenous languages', 'AI detects bridge corrosion using drones',
                      'AI compresses satellite imagery for transmission', 'AI personalizes physical rehabilitation']
            rows = [row('Texas ' + title, 'siliconangle.com', hours=i / 2, path=str(i)) for i, title in enumerate(titles)]
            rows.append(row('A new chapter for MIT Reads', 'news.mit.edu'))
            first = snapshot({'articles': []}, now, {'articles': rows}, rotate=True)
            validate(first)
            pools = [entry['stories'] for entry in first['editions']]
            self.assertEqual([len(pool) for pool in pools], [10, 10, 10, 10])
            self.assertEqual(len({story['url'] for pool in pools for story in pool}), 10)
            best = {r['url'] for r in rows[:10]}
            for pool in pools:
                self.assertEqual({story['url'] for story in pool}, best)
            retry = snapshot({'articles': []}, now + dt.timedelta(minutes=5), first, rotate=True)
            self.assertEqual([s['url'] for s in pools[0]], [s['url'] for s in retry['editions'][0]['stories']])
            for mutation in ('irrelevant', 'unsafe', 'duplicate', 'stale', 'oversized', 'empty'):
                broken = copy.deepcopy(first)
                pool = broken['editions'][0]['stories']
                if mutation == 'irrelevant': pool[2]['title'] = 'A new chapter for MIT Reads'
                if mutation == 'unsafe': pool[2]['url'] = 'javascript:alert(1)'
                if mutation == 'duplicate': pool[2] = copy.deepcopy(pool[1])
                if mutation == 'stale': pool[2]['first_seen_at'] = stamp(now - dt.timedelta(days=8))
                if mutation == 'oversized': pool.append(rank(rows, now)[10])
                if mutation == 'empty': pool.clear()
                with self.assertRaises(ValueError, msg=mutation): validate(broken)
            # Recently shown strong reporting beats older unseen reporting in every slot.
            repeated = snapshot({'articles': []}, now + EDITION_LENGTH, first, rotate=True)
            self.assertEqual({story['url'] for story in repeated['editions'][0]['stories']}, best)
            # Falling out of the current ten is not a permanent exclusion. After newer
            # coverage crosses a freshness tier, still-eligible reporting can return.
            strong = row('Texas AI satellites monitor coastal erosion', hours=80, path='returning')
            prior = snapshot({'articles': []}, now, {'articles': rows[:10] + [strong]}, rotate=True)
            self.assertNotIn(strong['url'], [s['url'] for s in prior['editions'][0]['stories']])
            # Independent reporting outranks a company post within the same age tier.
            company = {**rows[0], 'url': 'https://blog.google/company-research'}
            prior = snapshot({'articles': []}, now, {'articles': [company] + rows[1:10] + [strong]}, rotate=True)
            self.assertNotIn(strong['url'], [s['url'] for s in prior['editions'][0]['stories']])
            returning = snapshot({'articles': []}, now + dt.timedelta(hours=72), prior, rotate=True)
            validate(returning)
            self.assertIn(strong['url'], [s['url'] for s in returning['editions'][0]['stories']])
            # A fresh collector run can add newly published reporting to the new edition.
            later = edition_start(now) + EDITION_LENGTH + dt.timedelta(minutes=1)
            new = {'title': 'Texas AI satellite network monitors coastal erosion',
                   'url': 'https://dallasinnovates.com/coastal-erosion', 'first_seen_at': stamp(later)}
            second = snapshot({'articles': []}, later, {**first, 'articles': first['articles'] + [new]}, rotate=True)
            validate(second)
            self.assertIn(new['url'], [s['url'] for s in second['editions'][0]['stories']])
            self.assertEqual(len(second['editions'][0]['stories']), 10)
            self.assertNotIn(rows[9]['url'], [s['url'] for s in second['editions'][0]['stories']])
            same_slot = snapshot({'articles': []}, now + dt.timedelta(minutes=5),
                                 {**first, 'articles': first['articles'] + [{**new, 'first_seen_at': stamp(now)}]}, rotate=True)
            validate(same_slot)
            self.assertIn(new['url'], [s['url'] for s in same_slot['editions'][0]['stories']])

        def test_repeated_stories_expire_without_resetting_their_dates(self):
            original = row(hours=167)
            first = snapshot({'articles': []}, now, {'articles': [original]}, rotate=True)
            validate(first)
            self.assertEqual(len(first['editions']), 1)
            expired = snapshot({'articles': []}, now + EDITION_LENGTH, first, rotate=True)
            validate(expired)
            self.assertIsNone(expired['selected'])
            self.assertEqual(expired['editions'], [])

        def test_rate_limit_is_not_retried_and_retry_after_survives_restart(self):
            from unittest.mock import patch
            url = RSS_FEEDS[0]
            error = urllib.error.HTTPError(url, 429, 'Too Many Requests', {'Retry-After': '43200'}, None)
            with patch.object(news_feeds, 'allowed'), patch.object(news_feeds, 'request', side_effect=error) as request:
                rows, report, state = news_feeds.read(url, {}, now)
                self.assertEqual(request.call_count, 1)
                self.assertEqual(rows, [])
                self.assertEqual(report['http_status'], 429)
                self.assertEqual(state['retry_at'], stamp(now + dt.timedelta(hours=12)))
            with patch.object(news_feeds, 'request') as request:
                _, report, _ = news_feeds.read(url, json.loads(json.dumps(state)), now + EDITION_LENGTH)
                self.assertEqual(report['status'], 'backoff')
                request.assert_not_called()

        def test_conditional_feed_refresh_and_atom_dates(self):
            from unittest.mock import patch
            url = RSS_FEEDS[0]
            previous = {'parser_version': 2, 'etag': '"v1"', 'last_modified': 'Fri, 11 Sep 2026 18:00:00 GMT', 'ok_at': stamp(now - EDITION_LENGTH)}
            error = urllib.error.HTTPError(url, 304, 'Not Modified', {}, None)
            with patch.object(news_feeds, 'allowed'), patch.object(news_feeds, 'request', side_effect=error) as request:
                _, report, state = news_feeds.read(url, previous, now)
                self.assertEqual(report['status'], 'not_modified')
                self.assertEqual(state['ok_at'], stamp(now))
                self.assertEqual(request.call_args.args[1]['If-None-Match'], '"v1"')
            body = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>New AI research improves surgery</title><link href="https://news.mit.edu/surgery"/><published>2026-09-11T18:00:00Z</published><updated>2026-09-12T18:00:00Z</updated></entry></feed>'
            self.assertEqual(rss_articles(body)[0]['seendate'], '20260911T180000Z')

        def test_feed_parser_upgrade_fetches_texas_context_once(self):
            from unittest.mock import patch
            url = RSS_FEEDS[0]
            old = {'etag': '"old"', 'ok_at': stamp(now - EDITION_LENGTH)}
            body = b'<rss><channel><item><title>AI firms combine their consulting teams</title><link>https://dallasinnovates.com/deal/</link><pubDate>Fri, 11 Sep 2026 18:00:00 +0000</pubDate><description>&lt;p&gt;Two Dallas-based companies combine.&lt;/p&gt;</description></item></channel></rss>'
            with patch.object(news_feeds, 'allowed'), patch.object(news_feeds, 'request', return_value=(body, {'ETag': '"new"'})) as request:
                rows, report, state = news_feeds.read(url, old, now)
                self.assertEqual(request.call_args.args[1], {})
                self.assertEqual(state['parser_version'], 2)
                self.assertEqual(state['etag'], '"new"')
                self.assertEqual(rows[0]['summary'], 'Two Dallas-based companies combine.')
                result = snapshot({'articles': rows}, now)
                self.assertIsNotNone(result['selected'])
                validate(result)

        def test_company_blog_does_not_displace_independent_reporting(self):
            company = row('Texas experts join Google AI research team', 'blog.google', hours=1)
            report = row('Texas AI researchers test safety of driverless taxis', 'siliconangle.com', hours=12)
            self.assertEqual(rank([company, report], now)[0]['url'], report['url'])
    return 0 if unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Cases)).wasSuccessful() else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--collect', action='store_true')
    action.add_argument('--check', action='store_true')
    action.add_argument('--self-test', action='store_true')
    action.add_argument('--health', action='store_true')
    action.add_argument('--live-check', action='store_true')
    parser.add_argument('--wait-seconds', type=int, default=0)
    parser.add_argument('--expected-check')
    args = parser.parse_args()
    try:
        if args.self_test:
            sys.exit(self_test())
        if args.collect:
            sys.exit(collect())
        if args.live_check:
            if not 0 <= args.wait_seconds <= 2400:
                parser.error('--wait-seconds must be between zero and 2400')
            sys.exit(check_live(args.wait_seconds, args.expected_check))
        if args.health:
            problems = health_problems(load(), dt.datetime.now(UTC))
            print('news health: ' + ('; '.join(problems) if problems else 'current headline and a working feed available'))
            sys.exit(1 if problems else 0)
        validate(load())
        print('news_headlines: recorded selection and expiry verified')
    except (ValueError, KeyError, OSError) as error:
        print(f'news_headlines: {error}', file=sys.stderr)
        sys.exit(1)
