"""Bounded publisher-feed reads with conditional requests and persistent backoff.

Only titles, links, source dates and bounded feed excerpts survive parsing. Article bodies are never fetched.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import hashlib
import html
import re
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
import xml.etree.ElementTree as ET

UTC = dt.timezone.utc
UA = 'TexasAIDocket/1.0 (+https://texasaidocket.com)'
LIMIT = 2_000_000


def stamp(value):
    return value.astimezone(UTC).isoformat(timespec='seconds').replace('+00:00', 'Z')


def instant(value):
    result = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('source date has no timezone')
    return result.astimezone(UTC)


def request(url, headers=None):
    class SameHost(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, hdrs, newurl):
            if urllib.parse.urlsplit(newurl).hostname != urllib.parse.urlsplit(url).hostname:
                raise ValueError('unexpected feed redirect')
            return super().redirect_request(req, fp, code, msg, hdrs, newurl)
    opener = urllib.request.build_opener(SameHost())
    with opener.open(urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})}), timeout=15) as response:
        body = response.read(LIMIT + 1)
        if len(body) > LIMIT:
            raise ValueError('feed exceeded response limit')
        return body, dict(response.headers.items())


def allowed(url):
    parts = urllib.parse.urlsplit(url)
    robots_url = urllib.parse.urlunsplit((parts.scheme, parts.netloc, '/robots.txt', '', ''))
    try:
        body, _ = request(robots_url)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        return
    policy = urllib.robotparser.RobotFileParser()
    policy.parse(body.decode().splitlines())
    if not all(policy.can_fetch(agent, url) for agent in (UA, 'GPTBot', 'ClaudeBot')):
        raise ValueError('feed disallowed by source robots policy')


def summary_text(value):
    """Keep a bounded feed excerpt, excluding publisher-wide location boilerplate."""
    value = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', value or '', flags=re.I | re.S)
    value = html.unescape(re.sub(r'<[^>]*>', ' ', value))
    value = ' '.join(value.split())
    value = re.sub(r"^Dallas Innovates, Every Day: Here's what's new \+ next in North Texas\.\s*", '', value)
    value = re.split(r'\s+The post .+ appeared first on ', value, maxsplit=1)[0]
    return value[:1000]


def articles(body):
    root = ET.fromstring(body)
    atom = '{http://www.w3.org/2005/Atom}'
    if root.tag == 'rss' and root.find('channel') is not None:
        items, kind = root.findall('./channel/item'), 'rss'
    elif root.tag == atom + 'feed':
        items, kind = root.findall(atom + 'entry'), 'atom'
    else:
        raise ValueError('publisher did not return RSS or Atom')
    rows = []
    for item in items:
        try:
            if kind == 'rss':
                title, url = item.findtext('title'), item.findtext('link')
                summary = summary_text(item.findtext('description'))
                published = email.utils.parsedate_to_datetime(item.findtext('pubDate'))
            else:
                title = item.findtext(atom + 'title')
                summary = summary_text(item.findtext(atom + 'summary'))
                links = [link for link in item.findall(atom + 'link') if link.get('rel', 'alternate') == 'alternate']
                url = links[0].get('href') if links else None
                published = instant(item.findtext(atom + 'published') or item.findtext(atom + 'updated'))
            if not title or not url or published.tzinfo is None:
                continue
            rows.append({'title': title, 'url': url, 'language': 'English',
                         'seendate': published.astimezone(UTC).strftime('%Y%m%dT%H%M%SZ'),
                         **({'summary': summary} if summary else {})})
        except (TypeError, ValueError, AttributeError, OverflowError):
            continue
    return rows


def read(url, previous, now):
    """A source gets one attempt per run. A 429 never triggers an immediate retry."""
    previous = previous if isinstance(previous, dict) else {}
    state = {key: previous[key] for key in ('etag', 'last_modified', 'retry_at', 'failures', 'ok_at', 'sha256', 'parser_version') if key in previous}
    report = {'url': url, 'status': 'unavailable'}
    try:
        if state.get('retry_at') and now < instant(state['retry_at']):
            return [], {**report, 'status': 'backoff', 'retry_at': state['retry_at']}, state
        allowed(url)
        headers = {}
        if state.get('etag') and state.get('parser_version') == 2:
            headers['If-None-Match'] = state['etag']
        if state.get('last_modified') and state.get('parser_version') == 2:
            headers['If-Modified-Since'] = state['last_modified']
        try:
            body, response_headers = request(url, headers)
        except urllib.error.HTTPError as error:
            if error.code != 304 or not state.get('ok_at'):
                raise
            state.update(ok_at=stamp(now), failures=0)
            state.pop('retry_at', None)
            return [], {**report, 'status': 'not_modified'}, state
        rows = articles(body)
        response_headers = {key.lower(): value for key, value in response_headers.items()}
        state = {'ok_at': stamp(now), 'failures': 0, 'parser_version': 2, 'sha256': hashlib.sha256(body).hexdigest()}
        for header, key in [('etag', 'etag'), ('last-modified', 'last_modified')]:
            if response_headers.get(header):
                state[key] = response_headers[header][:512]
        return [{**row, 'feed': url} for row in rows], {**report, 'status': 'ok', 'items': len(rows), 'sha256': state['sha256']}, state
    except (OSError, ValueError, ET.ParseError) as error:
        failures = min(int(state.get('failures', 0)) + 1, 8)
        retry = now + dt.timedelta(hours=min(24, 6 * 2 ** (failures - 1)))
        if isinstance(error, urllib.error.HTTPError):
            report['http_status'] = error.code
            value = error.headers.get('Retry-After') if error.headers else None
            if value:
                try:
                    requested = (now + dt.timedelta(seconds=max(0, int(value)))) if value.isdigit() else email.utils.parsedate_to_datetime(value)
                    retry = max(retry, requested.astimezone(UTC))
                except (TypeError, ValueError, OverflowError):
                    pass
        state.update(failures=failures, retry_at=stamp(retry))
        return [], {**report, 'retry_at': state['retry_at'], 'reason': str(error)[:160]}, state
