"""Real local-Git CAS tests only. No GitHub access and no provider writes."""
import concurrent.futures
import copy
import json
from pathlib import Path
import subprocess
import tempfile
import threading
import unittest
from unittest.mock import patch
import upload_post_state as state

REPO = 'Talonsturgill/TexasAIDispatch'


def identity(index=0):
    return {'repository': REPO, 'edition_id': '2026-11-10', 'user': 'default',
            'platform': 'facebook', 'placement': 'story', 'segment_index': index}


def git(path, *args, data=None):
    return subprocess.run(['git', '-C', str(path), *args], input=data,
                          capture_output=True, check=True).stdout.decode().strip()


class LocalState(state.GitState):
    def _verify_remote(self):
        # Test-only local bare remotes; production validator is tested separately.
        pass


class StateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.remote = root / 'remote.git'; self.remote.mkdir()
        git(self.remote, 'init', '--bare', '--quiet')
        self.work = root / 'first'; self.work.mkdir()
        git(self.work, 'init', '--quiet')
        git(self.work, 'remote', 'add', 'origin', str(self.remote))
        self.second = root / 'second'; self.second.mkdir()
        git(self.second, 'init', '--quiet')
        git(self.second, 'remote', 'add', 'origin', str(self.remote))
        self.a = LocalState(self.work, REPO)
        self.b = LocalState(self.second, REPO)

    def test_readiness_creates_only_empty_state_and_is_idempotent(self):
        self.assertTrue(self.a.initialize()['ready'])
        first = git(self.remote, 'rev-parse', state.REF)
        self.b.initialize()
        self.assertEqual(first, git(self.remote, 'rev-parse', state.REF))
        self.assertEqual(git(self.remote, 'ls-tree', '--name-only', state.REF), state.FILE)
        self.assertEqual(self.b.records(), [])
        self.assertEqual(git(self.remote, 'for-each-ref', '--format=%(refname)'), state.REF)

    def test_claim_survives_scratch_loss_and_no_takeover(self):
        claim = self.a.claim(identity(), 'a' * 64)
        self.assertEqual(self.b.lookup(identity()), claim)
        self.assertEqual(claim['state'], 'UNKNOWN')
        with self.assertRaises(state.StateBlocked): self.b.claim(identity(), 'b' * 64)
        self.assertEqual(self.b.records('2026-11-10'), [claim])
        self.assertEqual(self.b.records('other'), [])

    def test_receipt_is_durable_idempotent_and_preserves_other_destinations(self):
        first = self.a.claim(identity(), 'a' * 64)
        second = self.b.claim(identity(1), 'b' * 64)
        receipt = {'state': 'ACCEPTED', 'request_id': 'r1', 'http_status': 200,
                   'post_url': 'https://facebook.com/story.php?story_fbid=123&id=456'}
        saved = self.a.save_result(first, receipt)
        head = git(self.remote, 'rev-parse', state.REF)
        self.assertEqual(self.b.save_result(first, receipt), saved)
        self.assertEqual(git(self.remote, 'rev-parse', state.REF), head)
        self.assertEqual(self.b.lookup(identity(1)), second)
        self.assertEqual(self.b.lookup(identity())['result']['request_id'], 'r1')

    def test_conflicting_result_or_owner_never_overwrites(self):
        claim = self.a.claim(identity(), 'a' * 64)
        wrong = {**claim, 'owner': 'b' * 32}
        with self.assertRaises(state.StateBlocked): self.b.save_result(wrong, {'state': 'UNKNOWN'})
        self.a.save_result(claim, {'state': 'ACCEPTED', 'request_id': 'r1'})
        with self.assertRaises(state.StateBlocked): self.b.save_result(claim, {'state': 'ACCEPTED', 'request_id': 'r2'})

    def test_push_response_lost_never_returns_claim(self):
        original = self.a._append
        def lost(parent, value):
            original(parent, value)
            raise state.StateBlocked('simulated lost push reply')
        with patch.object(self.a, '_append', side_effect=lost):
            with self.assertRaises(state.StateBlocked): self.a.claim(identity(), 'a' * 64)
        self.assertEqual(self.b.lookup(identity())['state'], 'UNKNOWN')
        with self.assertRaises(state.StateBlocked): self.b.claim(identity(), 'a' * 64)

    def test_receipt_push_response_lost_reconciles_without_rewriting(self):
        claim = self.a.claim(identity(), 'a' * 64)
        original = self.a._append
        calls = []
        def lost(parent, value):
            calls.append(1)
            original(parent, value)
            raise state.StateBlocked('simulated lost push reply')
        with patch.object(self.a, '_append', side_effect=lost):
            result = self.a.save_result(claim, {'state': 'ACCEPTED', 'request_id': 'r1'})
        self.assertEqual(len(calls), 1)
        self.assertEqual(result['result']['request_id'], 'r1')

    def race(self, same, initialized):
        if initialized: self.a.initialize()
        barrier = threading.Barrier(2)
        for store in (self.a, self.b):
            original = store._append
            def sync(parent, value, original=original):
                barrier.wait(timeout=10)
                return original(parent, value)
            store._append = sync
        def run(store, ident):
            try: return store.claim(ident, 'a' * 64)
            except state.StateBlocked: return None
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            futures = [pool.submit(run, self.a, identity()), pool.submit(run, self.b, identity(0 if same else 1))]
            results = [f.result() for f in futures]
        self.assertEqual(sum(r is not None for r in results), 1)
        self.assertEqual(len(self.a.records()), 1)
        return results

    def test_same_delivery_initial_creation_race(self): self.race(True, False)
    def test_different_delivery_initial_creation_race(self): self.race(False, False)
    def test_existing_branch_cas_race(self): self.race(True, True)

    def test_different_destination_contention_can_be_resumed_if_absent(self):
        results = self.race(False, True)
        absent = identity(0 if results[0] is None else 1)
        new = LocalState(self.work, REPO)
        new.claim(absent, 'b' * 64)
        self.assertEqual(len(new.records()), 2)

    def test_receipt_cas_retries_merge_other_destination(self):
        claim = self.a.claim(identity(), 'a' * 64)
        original = self.a._append
        calls = []
        def contend(parent, value):
            if not calls:
                calls.append(1)
                self.b.claim(identity(1), 'b' * 64)
            return original(parent, value)
        with patch.object(self.a, '_append', side_effect=contend):
            self.a.save_result(claim, {'state': 'ACCEPTED', 'request_id': 'r1'})
        self.assertEqual(len(self.a.records()), 2)

    def test_denied_receipt_push_is_not_retried(self):
        claim = self.a.claim(identity(), 'a' * 64)
        calls = []
        def denied(parent, value):
            calls.append(1)
            raise state.StateBlocked('simulated hook or permission denial')
        with patch.object(self.a, '_append', side_effect=denied):
            with self.assertRaises(state.StateBlocked):
                self.a.save_result(claim, {'state': 'ACCEPTED', 'request_id': 'r1'})
        self.assertEqual(len(calls), 1)
        self.assertNotIn('result', self.b.lookup(identity()))

    def test_conflict_without_remote_advance_is_not_retried(self):
        claim = self.a.claim(identity(), 'a' * 64)
        calls = []
        def conflict(parent, value):
            calls.append(1)
            raise state.StateConflict('simulated conflict without observed advance')
        with patch.object(self.a, '_append', side_effect=conflict):
            with self.assertRaises(state.StateBlocked):
                self.a.save_result(claim, {'state': 'ACCEPTED', 'request_id': 'r1'})
        self.assertEqual(len(calls), 1)

    def test_state_push_explicitly_disables_follow_tags(self):
        original = self.a._git
        pushes = []
        def record(*args, **kwargs):
            if args[0] == 'push': pushes.append(args)
            return original(*args, **kwargs)
        with patch.object(self.a, '_git', side_effect=record):
            self.a.claim(identity(), 'a' * 64)
        self.assertEqual(len(pushes), 1)
        self.assertIn('--no-follow-tags', pushes[0])
        self.assertIn('--porcelain', pushes[0])
        self.assertFalse(any(arg.startswith('--force') for arg in pushes[0]))

    def test_invalid_state_schema_is_not_replaced(self):
        self.a.initialize()
        head, value = self.a._snapshot()
        value['schema'] = 'other'
        # Deliberately inject invalid upstream metadata with raw Git, not module API.
        blob = git(self.work, 'hash-object', '-w', '--stdin', data=json.dumps(value).encode())
        tree = git(self.work, 'mktree', data=f'100644 blob {blob}\tstate.json\n'.encode())
        commit = self.a._git('commit-tree', tree, '-p', head, '-m', 'invalid test').stdout.decode().strip()
        self.a._git('push', '--quiet', 'origin', commit + ':' + state.REF)
        with self.assertRaises(state.StateBlocked): self.b.claim(identity(), 'a' * 64)
        self.assertEqual(git(self.remote, 'rev-parse', state.REF), commit)

    def test_no_main_index_or_checkout_changes(self):
        before = git(self.work, 'symbolic-ref', 'HEAD')
        (self.work / 'unrelated.txt').write_text('untouched')
        self.a.claim(identity(), 'a' * 64)
        self.assertEqual(git(self.work, 'symbolic-ref', 'HEAD'), before)
        self.assertEqual((self.work / 'unrelated.txt').read_text(), 'untouched')
        self.assertEqual(git(self.work, 'ls-files'), '')
        self.assertFalse((self.work / '.git' / 'FETCH_HEAD').exists())
        self.assertEqual(git(self.work, 'for-each-ref', '--format=%(refname)', 'refs/upload-post-read'), '')

    def test_remote_validator_accepts_only_exact_github_origins(self):
        for url in ['https://github.com/' + REPO, 'https://github.com/' + REPO + '.git', 'git@github.com:' + REPO + '.git']:
            self.assertTrue(state.valid_remote(url, REPO))
        for url in ['https://evil.example/' + REPO, 'https://github.com.evil.example/' + REPO,
                    'https://github.com/other/repo', 'https://token@github.com/' + REPO,
                    'https://github.com/' + REPO + '?token=secret', str(self.remote),
                    'ext::evil ' + REPO, 'https://github.com:443/' + REPO]:
            self.assertFalse(state.valid_remote(url, REPO))
        with self.assertRaises(state.StateBlocked): state.GitState(self.work, REPO)

    def test_github_case_variant_is_same_exact_repository(self):
        lower_url = 'https://github.com/' + REPO.lower()
        self.assertTrue(state.valid_remote(lower_url, REPO))
        self.assertTrue(state.valid_remote('https://github.com/' + REPO.upper() + '.git', REPO))
        self.assertFalse(state.valid_remote(lower_url + '-other', REPO))
        self.assertFalse(state.valid_remote(lower_url + '/extra', REPO))
        self.assertFalse(state.valid_remote('https://token@github.com/' + REPO.lower(), REPO))
        git(self.work, 'remote', 'set-url', 'origin', lower_url)
        actual = state.GitState(self.work, REPO)
        self.assertEqual(actual.repository, REPO)

    def test_pushurl_and_multiple_origin_urls_are_blocked(self):
        git(self.work, 'remote', 'set-url', 'origin', 'https://github.com/' + REPO)
        git(self.work, 'config', 'remote.origin.pushurl', 'https://github.com/' + REPO)
        with self.assertRaises(state.StateBlocked): state.GitState(self.work, REPO)
        git(self.work, 'config', '--unset-all', 'remote.origin.pushurl')
        git(self.work, 'config', '--add', 'remote.origin.url', 'https://github.com/' + REPO)
        with self.assertRaises(state.StateBlocked): state.GitState(self.work, REPO)

    def test_identity_and_receipt_secrets_rejected(self):
        bad = identity(); bad['repository'] = 'Talonsturgill/alaska-ai-weekly'
        with self.assertRaises(state.StateBlocked): self.a.claim(bad, 'a' * 64)
        for edition in ('private user note', 'person@example.com', '2026-11-10/path'):
            bad = identity(); bad['edition_id'] = edition
            with self.assertRaises(state.StateBlocked): self.a.claim(bad, 'a' * 64)
        for receipt in [{'state': 'ACCEPTED', 'access_token': 'secret'},
                        {'state': 'ACCEPTED', 'request_id': 'person@example.com'},
                        {'state': 'ACCEPTED', 'request_id': 'ghp_' + 'a' * 30},
                        {'state': 'ACCEPTED', 'response': {'request_id': 'r1'}},
                        {'state': 'ACCEPTED', 'post_url': 'https://facebook.com/p?access_token=secret'},
                        {'state': 'ACCEPTED', 'post_url': 'https://storage.example/p'}]:
            with self.assertRaises(state.StateBlocked): state.validate_result(receipt)


if __name__ == '__main__': unittest.main()
