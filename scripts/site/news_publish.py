#!/usr/bin/env python3
"""Publish validated headline metadata on its own branch, without a site rebuild."""
from __future__ import annotations
import base64
import json
import subprocess
import sys
import time
import news_headlines as news

REPOSITORY = 'Talonsturgill/TexasAIDocket'
BRANCH = 'news-data'


def api(method: str, path: str, data=None):
    args = ['gh', 'api', '--method', method, f'repos/{REPOSITORY}/{path}']
    if data is not None:
        args += ['--input', '-']
    result = subprocess.run(args, input=json.dumps(data) if data is not None else None,
                            text=True, capture_output=True)
    if result.returncode:
        if method == 'GET' and '(HTTP 404)' in result.stderr:
            return None
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout) if result.stdout.strip() else {}


def restore() -> None:
    data = api('GET', f'contents/ledger/news/latest.json?ref={BRANCH}')
    if data is None:
        print('news data: first publication will use the committed seed')
        return
    previous = json.loads(base64.b64decode(data['content']))
    # Rules and schema can change between runs. Preserve the observation clock, but derive
    # selection and expiry again; an old score or publisher label must not block collection.
    snapshot = news.snapshot({'articles': []}, news.instant(previous['checked_at']),
                             news.observation_history(previous))
    snapshot['feeds'] = previous.get('feeds', [])
    news.validate(snapshot)
    news.STATE.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n')
    print('news data: restored observation history')


def publish() -> str:
    snapshot = news.load()
    problems = news.health_problems(snapshot, news.dt.datetime.now(news.UTC))
    if problems:
        raise ValueError('; '.join(problems))
    content = json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n'
    blob = api('POST', 'git/blobs', {'content': content, 'encoding': 'utf-8'})['sha']
    # This tree deliberately has one public data file. Source, workflows and Pages never move.
    tree = api('POST', 'git/trees', {'tree': [
        {'path': 'ledger/news/latest.json', 'mode': '100644', 'type': 'blob', 'sha': blob}]})['sha']
    for attempt in range(3):
        ref = api('GET', f'git/ref/heads/{BRANCH}')
        parents = [ref['object']['sha']] if ref else []
        if ref:
            old = api('GET', f'contents/ledger/news/latest.json?ref={parents[0]}')
            previous = json.loads(base64.b64decode(old['content']))
            if news.instant(previous['checked_at']) >= news.instant(snapshot['checked_at']):
                print('news data: an equal or newer refresh is already published')
                return parents[0]
        commit = api('POST', 'git/commits', {
            'message': 'news: refresh public headline metadata\n\nActor: news',
            'tree': tree, 'parents': parents})['sha']
        try:
            if ref:
                api('PATCH', f'git/refs/heads/{BRANCH}', {'sha': commit, 'force': False})
            else:
                api('POST', 'git/refs', {'ref': f'refs/heads/{BRANCH}', 'sha': commit})
            print('news data: published ' + commit)
            return commit
        except RuntimeError:
            if attempt == 2:
                raise
            time.sleep(2)
    raise RuntimeError('news publication exhausted its retries')


def self_test() -> int:
    import copy
    import tempfile
    from pathlib import Path
    from unittest.mock import patch
    now = news.dt.datetime.now(news.UTC).replace(microsecond=0)
    row = {'title': 'Texas AI researchers open a new laboratory',
           'url': 'https://dallasinnovates.com/test/', 'first_seen_at': news.stamp(now)}
    snapshot = news.snapshot({'articles': []}, now, {'articles': [row]})
    snapshot['feeds'] = [{'status': 'ok'}]
    old_schema = copy.deepcopy(snapshot)
    old_schema['_spec'] = 1
    old_schema['selected']['publisher'] = 'Former publisher name'
    old_schema['selected']['score'] = -1
    old_schema['expires_at'] = None
    old_schema['articles'] += [None, {'title': 'Broken observation without a source'},
                              {**row, 'url': 'https://evil.example/story'},
                              {**row, 'first_seen_at': 'invalid'}]
    restored_data = {'content': base64.b64encode(json.dumps(old_schema).encode()).decode()}
    with tempfile.TemporaryDirectory() as directory:
        with patch.object(news, 'STATE', Path(directory) / 'latest.json'), \
                patch(__name__ + '.api', return_value=restored_data):
            restore()
            restored = news.load()
            assert restored['selected'] == snapshot['selected']
            assert restored['checked_at'] == snapshot['checked_at']
            assert restored['articles'] == snapshot['articles']
    calls = []
    def fake(method, path, data=None):
        calls.append((method, path, data))
        if method == 'GET': return None
        return {'sha': 'test-sha'}
    with patch.object(news, 'load', return_value=snapshot), patch(__name__ + '.api', side_effect=fake):
        assert publish() == 'test-sha'
    assert calls[-1] == ('POST', 'git/refs', {'ref': 'refs/heads/news-data', 'sha': 'test-sha'})
    assert next(c[2] for c in calls if c[1] == 'git/trees')['tree'][0]['path'] == 'ledger/news/latest.json'
    assert not any('heads/main' in c[1] or (c[2] or {}).get('force') for c in calls)
    calls.clear()
    def existing(method, path, data=None):
        calls.append((method, path, data))
        if path.startswith('git/ref/'): return {'object': {'sha': 'old'}}
        if path.startswith('contents/'):
            return {'content': base64.b64encode(json.dumps(snapshot).encode()).decode()}
        return {'sha': 'test-sha'}
    with patch.object(news, 'load', return_value=snapshot), patch(__name__ + '.api', side_effect=existing):
        assert publish() == 'old'
    assert not any(c[0] == 'PATCH' or c[1] == 'git/commits' for c in calls)
    calls.clear()
    older = {**snapshot, 'checked_at': news.stamp(now - news.dt.timedelta(hours=6))}
    def update(method, path, data=None):
        if path.startswith('contents/'):
            return {'content': base64.b64encode(json.dumps(older).encode()).decode()}
        return existing(method, path, data)
    with patch.object(news, 'load', return_value=snapshot), patch(__name__ + '.api', side_effect=update):
        assert publish() == 'test-sha'
    assert calls[-1] == ('PATCH', 'git/refs/heads/news-data', {'sha': 'test-sha', 'force': False})
    assert next(c[2] for c in calls if c[1] == 'git/commits')['parents'] == ['old']
    print('news publish: observation migration, isolated data branch and no older overwrite passed')
    return 0


if __name__ == '__main__':
    try:
        if sys.argv[1:] == ['--restore']: restore()
        elif sys.argv[1:] == ['--publish']: publish()
        elif sys.argv[1:] == ['--self-test']: sys.exit(self_test())
        else: raise ValueError('use --restore, --publish or --self-test')
    except (OSError, ValueError, KeyError, RuntimeError) as error:
        print('news publish: ' + str(error), file=sys.stderr)
        sys.exit(1)
