#!/usr/bin/env python3
"""One attributed Texas tech headline, selected without a language model.

GDELT provides discovery metadata, not readership counts or a verified publication date.
We rank recent coverage from named newsrooms, group sister outlets, and retain the publisher's
headline verbatim. No article bodies are fetched. See knowledge/shared/NEWS_CHIP.md.
"""
from __future__ import annotations

import argparse
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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE = ROOT / 'ledger/news/latest.json'
SOURCES = json.loads((ROOT / 'config/news_sources.json').read_text())['sources']
UTC = dt.timezone.utc
MAX_AGE = dt.timedelta(hours=36)
QUERY = ('(Texas OR Dallas OR Austin OR Houston OR "San Antonio" OR "Fort Worth") '
         '("artificial intelligence" OR AI OR "data center" OR technology OR semiconductor '
         'OR robotics) sourcelang:english')
FEED = 'https://api.gdeltproject.org/api/v2/doc/doc?' + urllib.parse.urlencode({
    'query': QUERY, 'mode': 'artlist', 'format': 'json', 'maxrecords': 250,
    'timespan': '24h', 'sort': 'HybridRel'})
RSS = 'https://dallasinnovates.com/feed/'
UA = 'TexasAIDocket/1.0 (+https://texasaidocket.com)'
TEXAS = re.compile(r'\b(?:texas|texans|dallas|houston|fort worth|san antonio|el paso|'
                   r'round rock|abilene|amarillo|lubbock|corpus christi|dfw|txdot|'
                   r'ut austin|texas a&m|unt)\b', re.I)
AUSTIN = re.compile(r'^(?:Austin[’\x27]s|Austin[- ]based|Austin (?:AI|tech|startup|data|city|council|robot|software|chip))\b', re.I)
TECH = re.compile(r'\b(?:AI|artificial intelligence|machine learning|data[- ]cent[er]+s?|'
                  r'tech(?:nology|nologies)?|semiconductors?|microchips?|robot\w*|'
                  r'autonomous|self[- ]driving|cyber\w*|software|quantum|computing|'
                  r'chatbots?|air[- ]tax(?:i|is)|air taxis|evtol|broadband)\b', re.I)
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


def eligible(article: dict, now: dt.datetime) -> bool:
    try:
        title = article['title']
        if not isinstance(title, str) or not 20 <= len(title) <= 220 or len(title.split()) > 32:
            return False
        if (not source(article['url']) or not (TEXAS.search(title) or AUSTIN.search(title))
                or not TECH.search(title) or JUNK.search(title)):
            return False
        age = now - instant(article['first_seen_at'])
        if not dt.timedelta(0) <= age < MAX_AGE:
            return False
        # A newly indexed archive article is not new coverage. Reject old dates when the
        # publisher exposes one in the URL. GDELT's seendate is never labelled "published".
        date = re.search(r'/(20\d{2})/(\d{2})/(\d{2})/', article['url'])
        if date:
            day = dt.date(*(int(n) for n in date.groups()))
            if not dt.timedelta(0) <= now.date() - day <= dt.timedelta(days=2):
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
        scored.append({**article, 'publisher': source(article['url'])[0],
                       'coverage': coverage, 'score': score})
    return sorted(scored, key=lambda a: (-a['score'], a['first_seen_at'], a['url']))


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
            if raw.get('language') == 'English' and eligible(row, now):
                rows.append(row)
        except (KeyError, TypeError, ValueError):
            continue
    # Retain observations for a week to keep a repeated URL from resetting its own clock.
    for old in (previous or {}).get('articles', []):
        if dt.timedelta(0) <= now - instant(old['first_seen_at']) < dt.timedelta(days=7):
            rows.append(old)
    unique = {a['url']: a for a in rows}
    rows = sorted(unique.values(), key=lambda a: a['url'])
    ranked = rank(rows, now)
    selected = ranked[0] if ranked else None
    return {'schema_version': 1, 'checked_at': stamp(now), 'provider': 'GDELT and publisher RSS',
            'feed_url': FEED, 'response_sha256': hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest(),
            'articles': rows, 'selected': selected,
            'expires_at': stamp(instant(selected['first_seen_at']) + MAX_AGE) if selected else None}


def validate(data: dict) -> None:
    if data.get('schema_version') != 1 or data.get('provider') != 'GDELT and publisher RSS':
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


def markup(today: str, data: dict | None = None) -> str:
    data = load() if data is None else data
    selected = data.get('selected')
    build_start = dt.datetime.combine(dt.date.fromisoformat(today), dt.time(), UTC)
    if not selected or build_start >= instant(data['expires_at']):
        return ''
    e = html.escape
    title = ('Selected from recent Texas tech and AI coverage, ranked by coverage and freshness. '
             'Discovery by The GDELT Project and publisher RSS. The source headline opens in a new tab.')
    return (f'<a class="tele news-chip" href="{e(selected["url"], quote=True)}" '
            f'target="_blank" rel="noopener noreferrer" data-expires-at="{e(data["expires_at"])}" '
            f'title="{title}"><span class="news-meta"><span class="news-label">Top story</span>'
            f'<cite class="news-source">{e(selected["publisher"])}</cite></span>'
            f'<cite class="news-title">{e(selected["title"])}</cite>'
            '<svg class="news-arrow" aria-hidden="true" viewBox="0 0 24 24" width="18" height="18" '
            'fill="none" stroke="currentColor" stroke-width="1.6"><path d="M7 17 17 7M7 7h10v10"/></svg>'
            '</a><script>' + EXPIRY_JS + '</script>')


# The build handles missing data; this handles a cached page surviving a missed cron or deploy.
# No network request, model call, tracking, ticker or carousel in the reader's browser.
EXPIRY_JS = """(function(){
  var chip=document.querySelector('.news-chip');
  if(!chip)return;
  var expires=Date.parse(chip.dataset.expiresAt);
  function retire(){if(!Number.isFinite(expires)||Date.now()>=expires)chip.hidden=true;}
  retire();
  if(expires>Date.now())setTimeout(retire,Math.min(expires-Date.now()+100,2147483647));
  document.addEventListener('visibilitychange',retire);
})();"""


def fetch(url: str) -> bytes:
    """One modest feed request with bounded retries. Never follow a cross-host redirect."""
    class SameHost(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            if urllib.parse.urlsplit(newurl).hostname != urllib.parse.urlsplit(url).hostname:
                raise ValueError('unexpected feed redirect')
            return super().redirect_request(req, fp, code, msg, headers, newurl)
    opener = urllib.request.build_opener(SameHost())
    for attempt in range(3):
        try:
            with opener.open(urllib.request.Request(url, headers={'User-Agent': UA, 'Cache-Control': 'no-cache'}), timeout=50) as response:
                body = response.read(2_000_001)
                if len(body) > 2_000_000:
                    raise ValueError('feed exceeded response limit')
                return body
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (TimeoutError, urllib.error.URLError):
            if attempt == 2:
                raise
        time.sleep(10 * (attempt + 1))
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
            published = email.utils.parsedate_to_datetime(item.findtext('pubDate')).astimezone(UTC)
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
    combined, feeds = [], []
    for url in (feed_url, RSS):
        try:
            body = checked_fetch(url)
            if url == RSS:
                rows = rss_articles(body)
            else:
                payload = json.loads(body)
                if not isinstance(payload, dict) or not isinstance(payload.get('articles'), list):
                    raise ValueError('GDELT did not return an article list')
                rows = payload['articles']
            combined.extend(rows)
            feeds.append({'url': url, 'status': 'ok', 'items': len(rows),
                          'sha256': hashlib.sha256(body).hexdigest()})
        except (OSError, ValueError, ET.ParseError) as error:
            feeds.append({'url': url, 'status': 'unavailable'})
            print(f'::warning::news feed unavailable: {urllib.parse.urlsplit(url).hostname}: {error}',
                  file=sys.stderr)
    if not any(feed['status'] == 'ok' for feed in feeds):
        raise OSError('all news feeds failed; previous snapshot preserved')
    result = snapshot({'articles': combined}, dt.datetime.now(UTC), load())
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
            self.assertFalse(eligible(row(hours=36), now))
            self.assertFalse(eligible(row(hours=-1), now))
            self.assertFalse(eligible(row(path='2020/09/11/archive'), now))
            self.assertEqual(rank([], now), [])
        def test_coverage_and_syndication(self):
            a = row()
            b = row('Texas launches Project Nexus electric air taxi pilot tests', 'cbs4local.com')
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
            p['articles'][0]['seendate'] = '20260912T200000Z'
            later = snapshot(p, now+dt.timedelta(days=1), s)
            self.assertEqual(later['expires_at'], s['expires_at'])
            p['articles'][0]['seendate'] = '20260913T200000Z'
            self.assertIsNone(snapshot(p, now+dt.timedelta(days=2), later)['selected'])
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
            with self.assertRaises(ValueError): rss_articles(b'<html>unavailable</html>')
            self.assertEqual(articles[0]['seendate'], '20260911T180000Z')
            self.assertIsNotNone(snapshot({'articles': articles}, now)['selected'])

        def test_markup(self):
            r = row('Texas AI lab announces <script> & "new" tools')
            s = snapshot({'articles': []}, now, {'articles':[r]})
            out = markup('2026-09-11', s)
            self.assertIn('&lt;script&gt; &amp; &quot;new&quot;', out)
            self.assertIn('<cite class="news-title">', out)
            self.assertIn('rel="noopener noreferrer"', out)
            self.assertEqual(markup('2026-09-15', s), '')
            self.assertEqual(markup('2026-09-11', {}), '')
    return 0 if unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(Cases)).wasSuccessful() else 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--collect', action='store_true')
    action.add_argument('--check', action='store_true')
    action.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    try:
        if args.self_test:
            sys.exit(self_test())
        if args.collect:
            sys.exit(collect())
        validate(load())
        print('news_headlines: recorded selection and expiry verified')
    except (ValueError, KeyError, OSError) as error:
        print(f'news_headlines: {error}', file=sys.stderr)
        sys.exit(1)
