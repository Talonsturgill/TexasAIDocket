#!/usr/bin/env python3
"""One attributed Texas tech headline, selected without a language model.

GDELT provides discovery metadata, not readership counts or a verified publication date.
We rank recent coverage from named newsrooms, group sister outlets, and retain the publisher's
headline verbatim. Only headline metadata is retained; article pages are never fetched. See knowledge/shared/NEWS_CHIP.md.
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
GLOBAL_GROUPS = frozenset(CONFIG.get('global_groups', []))
QUERY = ('(Texas OR Dallas OR Austin OR Houston OR "San Antonio" OR "Fort Worth") '
         '("artificial intelligence" OR AI OR "data center" OR technology OR semiconductor '
         'OR robotics) sourcelang:english')
FEED = 'https://api.gdeltproject.org/api/v2/doc/doc?' + urllib.parse.urlencode({
    'query': QUERY, 'mode': 'artlist', 'format': 'json', 'maxrecords': 250,
    'timespan': '24h', 'sort': 'HybridRel'})
UA = 'TexasAIDocket/1.0 (+https://texasaidocket.com)'
TEXAS = re.compile(r'\b(?:texas|texans|dallas|houston|fort worth|san antonio|el paso|'
                   r'round rock|abilene|amarillo|lubbock|corpus christi|dfw|txdot|'
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
                r'generative|deep learning|inference|MLPerf)\b', re.I)
JUNK = re.compile(r'\b(?:stock|shares|price target|earnings|buy rating|sponsored|press release|'
                  r'scholarship|obituary|football|basketball|baseball|betting|\w+ vs\.? \w+)\b', re.I)
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
    texas = bool(TEXAS.search(title) or AUSTIN.search(title) or
                 (newsroom and newsroom[1] == 'dallasinnovates' and DALLAS_INSTITUTIONS.search(title)))
    # Feed names and publisher identity establish provenance, never subject relevance.
    ai = bool(AI.search(title))
    return texas, ai


def eligible(article: dict, now: dt.datetime) -> bool:
    try:
        title = article['title']
        if not isinstance(title, str) or not 20 <= len(title) <= 220 or len(title.split()) > 32:
            return False
        newsroom = source(article['url'])
        texas, ai = topics(article)
        if (not newsroom or not article['url'].startswith('https://') or not ((ai and newsroom[1] in GLOBAL_GROUPS) or
                                  (texas and TECH.search(title))) or JUNK.search(title)):
            return False
        age = now - instant(article['first_seen_at'])
        if not dt.timedelta(0) <= age < MAX_AGE:
            return False
        # A newly indexed archive article is not new coverage. Reject old dates when the
        # publisher exposes one in the URL. GDELT's seendate is never labelled "published".
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
        priority = (0 if texas and ai else 1 if ai else 2) + (3 if age >= 72 else 0)
        scored.append({**article, 'publisher': source(article['url'])[0],
                       'coverage': coverage, 'score': score, 'priority': priority})
    return sorted(scored, key=lambda a: (a['priority'], -a['score'], a['first_seen_at'], a['url']))


def snapshot(payload: dict, now: dt.datetime, previous: dict | None = None) -> dict:
    now = instant(stamp(now))
    if not isinstance(payload, dict) or not isinstance(payload.get('articles'), list):
        raise ValueError('GDELT did not return an article list')
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
    return {'_spec': 2, 'checked_at': stamp(now), 'provider': 'GDELT and publisher RSS',
            'feed_url': FEED, 'response_sha256': hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
            'articles': rows, 'selected': selected,
            'expires_at': stamp(instant(selected['first_seen_at']) + MAX_AGE) if selected else None}


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
            if raw.get('feed') in RSS_FEEDS:
                row['feed'] = raw['feed']
            rows.append(row)
        except (KeyError, TypeError, ValueError, AttributeError):
            continue
    return {'articles': rows}


def validate(data: dict) -> None:
    if data.get('_spec') != 2 or data.get('provider') != 'GDELT and publisher RSS':
        raise ValueError('unknown news snapshot')
    now = instant(data['checked_at'])
    ranked = rank(data['articles'], now)
    selected = ranked[0] if ranked else None
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
    return {key: data.get(key) for key in ('_spec', 'checked_at', 'selected', 'expires_at')}


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
        date = f'{observed:%B} {day}{suffix}, {observed.year}'
    url = selected['url'] if selected else '/articles/'
    first_seen = selected['first_seen_at'] if selected else ''
    description = ('Headlines ranked by coverage and freshness, with Texas AI first. '
                   'The date is the publisher feed date or first observation. Opens the source in a new tab.')
    relevance = {name: pattern.pattern for name, pattern in
                 [('texas', TEXAS), ('austin', AUSTIN), ('local', DALLAS_INSTITUTIONS),
                  ('tech', TECH), ('ai', AI), ('junk', JUNK)]}
    relevance['global_groups'] = sorted(GLOBAL_GROUPS)
    return (f'<a class="tele news-chip" data-news-status="{status}" '
            f'data-news-feed="{NEWS_FEED_URL}" '
            f'data-news-sources="{e(json.dumps(SOURCES), quote=True)}" '
            f'data-news-relevance="{e(json.dumps(relevance), quote=True)}" '
            f'data-news-initial="{e(json.dumps(public_snapshot(data)), quote=True)}" '
            f'data-checked-at="{e(data.get("checked_at", ""), quote=True)}" '
            f'data-first-seen-at="{e(first_seen)}" data-expires-at="{e(data.get("expires_at") or "")}" '
            f'href="{e(url, quote=True)}" target="_blank" rel="noopener noreferrer" '
            f'title="{description}"><span class="news-meta"><span class="news-label">{label}</span>'
            f'<cite class="news-source">{e(publisher)}</cite>'
            f'<time class="news-date" datetime="{e(first_seen)}">{date}</time></span>'
            f'<cite class="news-title">{e(title)}</cite>'
            '<svg class="news-arrow" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" '
            'fill="none" stroke="currentColor" stroke-width="1.6"><path d="M7 17 17 7M7 7h10v10"/></svg>'
            '</a><script>' + (ROOT / 'scripts/site/news_runtime.js').read_text() + '</script>')


def fetch(url: str) -> bytes:
    """One modest feed request with bounded retries. Never follow a cross-host redirect."""
    class SameHost(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if urllib.parse.urlsplit(newurl).hostname != urllib.parse.urlsplit(url).hostname:
                raise ValueError('unexpected feed redirect')
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    opener = urllib.request.build_opener(SameHost())
    for attempt in range(2):
        try:
            with opener.open(urllib.request.Request(url, headers={'User-Agent': UA, 'Cache-Control': 'no-cache'}), timeout=15) as response:
                body = response.read(2_000_001)
                if len(body) > 2_000_000:
                    raise ValueError('feed exceeded response limit')
                return body
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 1:
                raise
        except (TimeoutError, urllib.error.URLError):
            if attempt == 1:
                raise
        time.sleep(2 * (attempt + 1))
    raise RuntimeError('feed unavailable')


def checked_fetch(url: str) -> bytes:
    """Read the host's policy before reading its feed; never route around a disallow."""
    parts = urllib.parse.urlsplit(url)
    robots_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, '/robots.txt', '', ''))
    try:
        robots = fetch(robots_url).decode()
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        robots = ''
    policy = urllib.robotparser.RobotFileParser()
    policy.parse(robots.splitlines())
    if robots and not all(policy.can_fetch(agent, url) for agent in (UA, 'GPTBot', 'ClaudeBot')):
        raise ValueError('feed disallowed by source robots policy')
    if parts.hostname == 'api.gdeltproject.org':
        time.sleep(6)  # GDELT asks for at least five seconds between requests.
    return fetch(url)


def rss_articles(body: bytes) -> list[dict]:
    rows = []
    root = ET.fromstring(body)
    if root.tag != 'rss' or root.find('channel') is None:
        raise ValueError('publisher did not return an RSS feed')
    for item in root.findall('./channel/item'):
        try:
            published = email.utils.parsedate_to_datetime(item.findtext('pubDate'))
            if published.tzinfo is None:
                raise ValueError('RSS publication time has no timezone')
            published = published.astimezone(UTC)
            rows.append({'title': item.findtext('title'), 'url': item.findtext('link'),
                         'language': 'English', 'seendate': published.strftime('%Y%m%dT%H%M%SZ')})
        except (TypeError, ValueError, AttributeError):
            continue
    return rows


def collect() -> int:
    # Explicit bounds record which day of coverage this observation requested.
    end = dt.datetime.now(UTC).replace(microsecond=0)
    query = dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(FEED).query))
    query.pop('timespan')
    query.update(startdatetime=(end-dt.timedelta(days=1)).strftime('%Y%m%d%H%M%S'),
                 enddatetime=end.strftime('%Y%m%d%H%M%S'))
    feed_url = 'https://api.gdeltproject.org/api/v2/doc/doc?' + urllib.parse.urlencode(query)
    def read_feed(url):
        try:
            body = checked_fetch(url)
            if url in RSS_FEEDS:
                rows = rss_articles(body)
                rows = [{**row, 'feed': url} for row in rows]
            else:
                payload = json.loads(body)
                if not isinstance(payload, dict) or not isinstance(payload.get('articles'), list):
                    raise ValueError('GDELT did not return an article list')
                rows = payload['articles']
            return rows, {'url': url, 'status': 'ok', 'items': len(rows),
                          'sha256': hashlib.sha256(body).hexdigest()}
        except (OSError, ValueError, ET.ParseError) as error:
            print(f'::warning::news feed unavailable: {urllib.parse.urlsplit(url).hostname}: {error}',
                  file=sys.stderr)
            return [], {'url': url, 'status': 'unavailable'}
    combined, feeds = [], []
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for rows, feed in pool.map(read_feed, (feed_url, *RSS_FEEDS)):
            combined.extend(rows)
            feeds.append(feed)
    if not any(feed['status'] == 'ok' for feed in feeds):
        raise OSError('all news feeds failed; previous snapshot preserved')
    # The old schema is accepted only as observation history during this migration. Every
    # candidate is filtered and ranked again; an old selected headline is never trusted.
    previous = observation_history(json.loads(STATE.read_text())) if STATE.exists() else {}
    result = snapshot({'articles': combined}, dt.datetime.now(UTC), previous)
    result['feed_url'] = feed_url
    result['feeds'] = feeds
    validate(result)
    STATE.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    temp.replace(STATE)
    print(json.dumps({'eligible': len(rank(result['articles'], instant(result['checked_at']))),
                      'selected': result['selected'], 'expires_at': result['expires_at']}, ensure_ascii=False))
    return 0


def health_problems(data: dict, now: dt.datetime) -> list[str]:
    """Operational health is separate from the reproducible snapshot/schema check."""
    problems = []
    if not data.get('selected') or now - instant(data['selected']['first_seen_at']) >= TRENDING_AGE:
        problems.append('no fresh AI or Texas tech headline is available')
    if not dt.timedelta(minutes=-5) <= now - instant(data['checked_at']) <= MAX_CHECK_AGE:
        problems.append('news collection is overdue or its clock is invalid')
    if sum(feed.get('status') == 'ok' for feed in data.get('feeds', [])) < 1:
        problems.append('no news feed is available')
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
    if tag != 'a' or chip.get('data-news-feed') != NEWS_FEED_URL:
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
            feed_request = urllib.request.Request(NEWS_FEED_URL + '?refresh=' + str(int(time.time())),
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
                with patch(__name__ + '.STATE', state), patch(__name__ + '.fetch', side_effect=TimeoutError()):
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
            def read(url):
                if url not in RSS_FEEDS:
                    raise urllib.error.HTTPError(url, 429, 'Too Many Requests', {}, None)
                return body
            with tempfile.TemporaryDirectory() as directory:
                state = Path(directory) / 'latest.json'
                with patch(__name__ + '.STATE', state), patch(__name__ + '.checked_fetch', side_effect=read):
                    self.assertEqual(collect(), 0)
                    result = load()
                self.assertEqual(result['selected']['title'], 'Texas AI research laboratory opens')
                self.assertEqual(sum(f['status'] == 'ok' for f in result['feeds']), len(RSS_FEEDS))
                self.assertEqual(health_problems(result, dt.datetime.now(UTC)), [])

        def test_empty_refresh_is_not_operational_success(self):
            s = snapshot({'articles': []}, now)
            s['feeds'] = [{'status': 'ok'}, {'status': 'ok'}]
            validate(s)  # An honest empty snapshot is publishable, but needs attention.
            self.assertIn('no fresh AI or Texas tech headline is available', health_problems(s, now))
            self.assertIn('data-news-status="empty"', markup('2026-09-11', s))

        def test_operational_health(self):
            s = snapshot({'articles': []}, now, {'articles': [row()]})
            s['feeds'] = [{'status': 'ok'}, {'status': 'ok'}]
            self.assertEqual(health_problems(s, now), [])
            self.assertIn('news collection is overdue or its clock is invalid',
                          health_problems(s, now + dt.timedelta(hours=19)))
            self.assertIn('no fresh AI or Texas tech headline is available',
                          health_problems(s, now + dt.timedelta(hours=73)))
            s['feeds'][1]['status'] = 'unavailable'
            self.assertEqual(health_problems(s, now), [])
            s['feeds'][0]['status'] = 'unavailable'
            self.assertIn('no news feed is available', health_problems(s, now))

        def test_global_ai_and_quiet_days(self):
            global_ai = row('AI researchers develop a safer surgery technique', 'news.mit.edu', path='ai')
            self.assertTrue(eligible(global_ai, now))
            self.assertFalse(eligible(row('Cute critters launch on a gaming service', 'blogs.nvidia.com'), now))
            texas_ai = row('Texas researchers develop a safer AI surgery technique', 'dallasinnovates.com')
            self.assertEqual(rank([global_ai, texas_ai], now)[0]['url'], texas_ai['url'])
            self.assertEqual(rank([global_ai, row(hours=40)], now)[0]['url'], global_ai['url'])
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
            self.assertTrue(eligible({**row('New AI technique makes surgery safer and more precise', 'news.mit.edu'),
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

        def test_markup(self):
            r = row('Texas AI lab announces <script> & "new" tools')
            s = snapshot({'articles': []}, now, {'articles':[r]})
            out = markup('2026-09-11', s)
            self.assertIn('&lt;script&gt; &amp; &quot;new&quot;', out)
            self.assertIn('September 11th, 2026</time>', out)
            self.assertIn('<cite class="news-title">', out)
            self.assertIn('rel="noopener noreferrer"', out)
            self.assertIn('Recent', markup('2026-09-15', s))
            self.assertIn('data-news-status="empty"', markup('2026-09-20', s))
            self.assertIn('Explore the latest AI reporting', markup('2026-09-11', {}))
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
