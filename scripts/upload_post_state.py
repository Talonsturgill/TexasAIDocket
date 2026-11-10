"""Append-only social delivery claims, independent of production and main.

A successful claim is durable UNKNOWN intent, not publication approval. No claim
expires and no existing intent is taken over. Normal fast-forward pushes provide
compare-and-swap; uncertain pushes stop publishing, while receipt-only updates
can reconcile and retry contention without repeating a provider request.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone
from urllib.parse import urlsplit, parse_qsl
from uuid import uuid4

REF = 'refs/heads/claude/social-delivery-state-v1'
FILE = 'state.json'
SCHEMA = 'upload-post-social-state/1'
REPOSITORIES = {'Talonsturgill/alaska-ai-weekly', 'Talonsturgill/alaskaaicarousels',
                'Talonsturgill/TexasAIDispatch', 'Talonsturgill/TexasAIDocket'}
IDENTITY_KEYS = {'repository', 'edition_id', 'user', 'platform', 'placement', 'segment_index'}
RESULT_KEYS = {'state', 'request_id', 'job_id', 'http_status', 'platform_post_id',
               'post_url', 'error_code', 'failure_stage'}


class StateBlocked(RuntimeError):
    """No provider write may follow this failure."""


class StateConflict(StateBlocked):
    """A confirmed normal-push compare-and-swap rejection, not a denial."""


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def key_for(identity):
    return hashlib.sha256(encoded(identity).encode()).hexdigest()


def require(condition, message):
    if not condition:
        raise StateBlocked(message)


def valid_remote(url, repository):
    """Only exact recognized repository addresses; never infer from a suffix."""
    expected = repository + '.git'
    if url.startswith('git@github.com:'):
        path = url[len('git@github.com:'):]
        return path in {repository, expected}
    parsed = urlsplit(url)
    return (parsed.scheme == 'https' and parsed.hostname == 'github.com'
            and parsed.port is None and parsed.username is None and parsed.password is None
            and not parsed.query and not parsed.fragment
            and parsed.path in {'/' + repository, '/' + expected})


def validate_result(result):
    require(isinstance(result, dict) and set(result) <= RESULT_KEYS, 'unsupported durable receipt fields')
    require(result.get('state') in {'UNKNOWN', 'ACCEPTED', 'PUBLISHED', 'FAILED', 'BLOCKED'}, 'invalid durable receipt state')
    for key, value in result.items():
        require(type(value) in {str, int}, 'durable receipt values must be strings or integers')
        require(len(str(value)) <= 2000, 'durable receipt value too long')
        text = str(value)
        require(not re.search(r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', text),
                'account email is not durable metadata')
        require(not re.search(r'(gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_\-]{20,}|AIza[A-Za-z0-9_\-]{20,}|Bearer\s+|Apikey\s+|BEGIN [A-Z ]*PRIVATE KEY)', text, re.I),
                'credential-like text is not durable metadata')
        if key == 'post_url':
            parsed = urlsplit(value)
            require(parsed.scheme == 'https' and parsed.hostname and not parsed.username
                    and not parsed.password and not parsed.fragment,
                    'durable post URL must be public HTTPS without credentials')
            hosts = {'facebook.com', 'fb.watch', 'linkedin.com', 'instagram.com', 'tiktok.com', 'youtube.com', 'youtu.be'}
            require(any(parsed.hostname == host or parsed.hostname.endswith('.' + host) for host in hosts),
                    'durable post URL must belong to an authorized social platform')
            require(not any(any(word in key.lower() for word in ('token', 'signature', 'credential', 'secret', 'password', 'apikey', 'api_key')) or key.lower() == 'sig'
                            for key, _ in parse_qsl(parsed.query)), 'credential-like URL query is not durable metadata')
    return dict(result)


class GitState:
    def __init__(self, repo_path, repository):
        require(repository in REPOSITORIES, 'repository is not an authorized daily routine')
        self.repo = Path(repo_path).resolve()
        self.repository = repository
        self._verify_remote()

    def _git(self, *args, data=None, check=True):
        author = {'GIT_AUTHOR_NAME': 'Talon Sturgill', 'GIT_AUTHOR_EMAIL': 'Talon.sturgill@gmail.com',
                  'GIT_COMMITTER_NAME': 'Talon Sturgill', 'GIT_COMMITTER_EMAIL': 'Talon.sturgill@gmail.com'}
        try:
            result = subprocess.run(['git', '-C', str(self.repo), *args], input=data,
                                    capture_output=True, timeout=90,
                                    env={**os.environ, **author}, check=False)
        except (OSError, subprocess.TimeoutExpired):
            raise StateBlocked('git state operation outcome uncertain; reconcile without publishing') from None
        if check and result.returncode:
            raise StateBlocked('git state operation failed; reconcile without publishing')
        return result

    def _verify_remote(self):
        explicit_push = self._git('config', '--get-all', 'remote.origin.pushurl', check=False)
        require(explicit_push.returncode == 1, 'explicit origin push URL is not allowed')
        fetch = self._git('remote', 'get-url', '--all', 'origin').stdout.decode().splitlines()
        push = self._git('remote', 'get-url', '--push', '--all', 'origin').stdout.decode().splitlines()
        require(len(fetch) == 1 and len(push) == 1 and fetch == push,
                'origin must have one identical fetch and push URL')
        try:
            allowed = valid_remote(fetch[0], self.repository)
        except ValueError:
            allowed = False
        require(allowed, 'origin does not match the exact authorized repository')

    def _identity(self, identity):
        require(isinstance(identity, dict) and set(identity) == IDENTITY_KEYS, 'invalid delivery identity fields')
        require(identity['repository'] == self.repository, 'delivery repository mismatch')
        require(isinstance(identity['edition_id'], str) and len(identity['edition_id']) <= 200
                and re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:-[a-z0-9]+(?:-[a-z0-9]+)*)?', identity['edition_id']),
                'invalid edition identity')
        require(identity['user'] == ('alaska_ai' if '/alaska' in self.repository else 'default'),
                'delivery profile mismatch')
        require(identity['platform'] in {'facebook', 'instagram', 'linkedin', 'tiktok', 'youtube'}, 'invalid delivery platform')
        require(identity['placement'] in {'feed', 'story'}, 'invalid delivery placement')
        require(type(identity['segment_index']) is int and identity['segment_index'] >= 0, 'invalid delivery segment')
        return dict(identity)

    def _validate(self, state):
        require(isinstance(state, dict) and set(state) == {'schema', 'repository', 'deliveries'}, 'invalid durable state fields')
        require(state['schema'] == SCHEMA and state['repository'] == self.repository, 'durable state binding mismatch')
        require(isinstance(state['deliveries'], dict), 'invalid durable delivery map')
        for key, entry in state['deliveries'].items():
            require(isinstance(entry, dict) and set(entry) in (
                {'key', 'identity', 'fingerprint', 'owner', 'started_at', 'state'},
                {'key', 'identity', 'fingerprint', 'owner', 'started_at', 'state', 'result'}), 'invalid durable claim fields')
            self._identity(entry['identity'])
            require(key == entry['key'] == key_for(entry['identity']), 'durable identity digest mismatch')
            require(re.fullmatch('[a-f0-9]{64}', entry['fingerprint']) is not None, 'invalid durable fingerprint')
            require(re.fullmatch('[a-f0-9]{32}', entry['owner']) is not None, 'invalid durable owner')
            require(entry['state'] == 'UNKNOWN', 'intent must remain UNKNOWN; outcome belongs in result')
            require(isinstance(entry['started_at'], str), 'invalid claim timestamp')
            if 'result' in entry:
                validate_result(entry['result'])
        return state

    def _snapshot(self):
        self._verify_remote()
        listing = self._git('ls-remote', '--heads', 'origin', REF).stdout.decode().strip()
        if not listing:
            return None, {'schema': SCHEMA, 'repository': self.repository, 'deliveries': {}}
        rows = listing.splitlines()
        require(len(rows) == 1, 'ambiguous social state branch')
        advertised, ref = rows[0].split('\t')
        require(ref == REF and re.fullmatch('[a-f0-9]{40,64}', advertised), 'invalid social state reference')
        private = 'refs/upload-post-read/' + uuid4().hex
        try:
            self._git('fetch', '--quiet', '--no-tags', '--no-write-fetch-head', 'origin', REF + ':' + private)
            commit = self._git('rev-parse', private + '^{commit}').stdout.decode().strip()
            tree = self._git('ls-tree', '--name-only', commit).stdout.decode().splitlines()
            require(tree == [FILE], 'social branch contains unexpected paths')
            raw = self._git('show', commit + ':' + FILE).stdout
            require(len(raw) <= 16 * 1024 * 1024, 'durable state exceeds size bound')
            try:
                state = json.loads(raw)
            except (ValueError, UnicodeDecodeError):
                raise StateBlocked('durable social state is unreadable') from None
            return commit, self._validate(state)
        finally:
            existing = self._git('rev-parse', '--verify', '--quiet', private, check=False)
            if existing.returncode == 0:
                self._git('update-ref', '-d', private, existing.stdout.decode().strip())

    def initialize(self):
        """Initialize only an empty state branch, then verify; no publication claim."""
        parent, state = self._snapshot()
        if parent is not None:
            return {'repository': self.repository, 'ref': REF, 'ready': True}
        self._append(None, state)
        parent, current = self._snapshot()
        require(parent is not None and current == state, 'empty social state verification failed')
        return {'repository': self.repository, 'ref': REF, 'ready': True}

    def records(self, edition_id=None):
        _, state = self._snapshot()
        values = state['deliveries'].values()
        return [entry for entry in values if edition_id is None or entry['identity']['edition_id'] == edition_id]

    def lookup(self, identity):
        identity = self._identity(identity)
        _, state = self._snapshot()
        return state['deliveries'].get(key_for(identity))

    def _append(self, parent, state):
        self._validate(state)
        self._verify_remote()
        blob = self._git('hash-object', '-w', '--stdin', data=(encoded(state) + '\n').encode()).stdout.decode().strip()
        tree = self._git('mktree', data=('100644 blob ' + blob + '\t' + FILE + '\n').encode()).stdout.decode().strip()
        args = ['commit-tree', tree, '-m', 'Record daily social delivery state']
        if parent:
            args += ['-p', parent]
        commit = self._git(*args).stdout.decode().strip()
        # Never force, delete, switch branches or touch the user's index/worktree.
        pushed = self._git('push', '--porcelain', '--quiet', '--no-follow-tags',
                           'origin', commit + ':' + REF, check=False)
        if pushed.returncode:
            lines = pushed.stdout.decode(errors='replace').splitlines()
            conflicts = ('[rejected] (non-fast-forward)', '[rejected] (fetch first)')
            if any(line.startswith('!\t') and line.split('\t')[1].endswith(':' + REF)
                   and line.split('\t')[-1] in conflicts for line in lines):
                raise StateConflict('social state compare-and-swap conflict')
            raise StateBlocked('social state push failed or uncertain; do not repeat the push')
        return commit

    def claim(self, identity, fingerprint):
        identity = self._identity(identity)
        require(isinstance(fingerprint, str) and re.fullmatch('[a-f0-9]{64}', fingerprint), 'invalid delivery fingerprint')
        key = key_for(identity)
        parent, state = self._snapshot()
        require(key not in state['deliveries'], 'delivery already claimed; reconciliation only')
        entry = {'key': key, 'identity': identity, 'fingerprint': fingerprint,
                 'owner': uuid4().hex, 'started_at': datetime.now(timezone.utc).isoformat(), 'state': 'UNKNOWN'}
        state['deliveries'][key] = entry
        self._append(parent, state)  # Any rejection/timeout blocks this provider write.
        require(self.lookup(identity) == entry, 'durable claim verification failed; do not publish')
        return entry

    def save_result(self, claim, compact_receipt):
        result = validate_result(compact_receipt)
        require(isinstance(claim, dict) and 'result' not in claim, 'original intent claim required')
        identity = self._identity(claim.get('identity'))
        key = key_for(identity)
        for _ in range(3):
            parent, state = self._snapshot()
            current = state['deliveries'].get(key)
            if current == {**claim, 'result': result}:
                return current
            require(current == claim, 'durable claim changed or result conflicts; do not overwrite')
            updated = {**claim, 'result': result}
            state['deliveries'][key] = updated
            try:
                self._append(parent, state)
            except StateConflict:
                # Retry only a reported CAS conflict whose remote branch actually
                # advanced. Permission, hook and transport failures are not CAS.
                advanced, latest = self._snapshot()
                found = latest['deliveries'].get(key)
                if found == updated:
                    return found
                require(found == claim and advanced is not None and advanced != parent,
                        'CAS conflict did not preserve the claimed delivery')
                require(parent is not None and self._git('merge-base', '--is-ancestor',
                        parent, advanced, check=False).returncode == 0,
                        'social state history did not advance monotonically')
                continue
            except StateBlocked:
                # A response may have been lost after the push committed. One
                # readback can prove the exact result; otherwise stop, never retry.
                found = self.lookup(identity)
                if found == updated:
                    return found
                raise StateBlocked('receipt push not confirmed; retain local result and reconcile without republishing') from None
            require(self.lookup(identity) == updated, 'durable receipt verification failed')
            return updated
        raise StateBlocked('durable receipt not confirmed; preserve local result and reconcile without republishing')
