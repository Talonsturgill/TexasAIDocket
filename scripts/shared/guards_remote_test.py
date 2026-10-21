"""Offline transport tests around an actual completed full-runner fixture verdict."""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import guards_remote as remote


class RemoteVerdictTest(unittest.TestCase):
    def setUp(self):
        scratch = Path(remote.__file__).resolve().parents[2] / 'out/guards-remote-tests/tmp'
        scratch.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / 'candidate'
        self.repo.mkdir()
        self.artifact = Path(self.tmp.name) / 'actual-fixture-output'
        self.artifact.mkdir()
        def git(*args):
            return subprocess.check_output(['git', *args], cwd=self.repo, text=True).strip()
        self.git = git
        git('init', '-q'); git('config', 'user.name', 'Talon Sturgill')
        git('config', 'user.email', 'Talon.sturgill@gmail.com')
        git('remote', 'add', 'origin', 'https://github.com/' + remote.REPOSITORY + '.git')
        (self.repo / 'scripts/shared').mkdir(parents=True)
        shutil.copy2(Path(remote.__file__).with_name('guards_local.py'), self.repo / 'scripts/shared')
        (self.repo / '.github/workflows').mkdir(parents=True)
        (self.repo / '.github/workflows/guards.yml').write_text(
            "jobs:\n  fixture:\n    steps:\n      - name: real fixture command\n"
            "        run: python3 -c 'print(123)'\n")
        (self.repo / remote.WORKFLOW_PATH).write_text('fixture approved executor bytes\n')
        (self.repo / '.gitignore').write_text('out/\n')
        (self.repo / '.githooks').mkdir()
        for name in ('pre-commit', 'commit-msg'):
            hook = self.repo / '.githooks' / name
            hook.write_text('#!/bin/sh\nexit 0\n'); hook.chmod(0o755)
        git('config', 'core.hooksPath', '.githooks')
        git('add', '.'); git('commit', '-qm', 'Offline original-runner fixture')
        self.sha = git('rev-parse', 'HEAD')
        git('update-ref', 'refs/remotes/origin/main', self.sha)
        subprocess.run([sys.executable, 'scripts/shared/guards_local.py'], cwd=self.repo,
                       capture_output=True, check=True)
        subprocess.run([sys.executable, 'scripts/shared/guards_local.py', '--verdict'],
                       cwd=self.repo, capture_output=True, check=True)
        shutil.copy2(self.repo / 'out/gates/verdict.json', self.artifact)
        (self.artifact / 'full-run.log').write_text('Offline fixture process actually completed.\n')
        (self.artifact / 'full-verdict.txt').write_text('Offline fixture reader actually exited zero.\n')
        self.run = {'id': 123, 'run_attempt': 1, 'status': 'completed', 'conclusion': 'success',
                    'display_title': 'Full local verdict for ' + self.sha,
                    'head_sha': self.sha, 'html_url': 'https://github.com/offline-fixture/run/123'}
        self.receipt = {'schema': 'docket_full_local_execution/1', 'candidate_sha': self.sha,
                        'checkout_sha': self.sha, 'workflow_sha': self.sha,
                        'workflow_ref': remote.REPOSITORY + '/' + remote.WORKFLOW_PATH + '@refs/heads/main',
                        'run_id': '123', 'run_attempt': '1', 'suite_exit': 0, 'verdict_exit': 0}
        self.save_artifact()
        (self.repo / 'out/gates/verdict.json').unlink()
        self.rows = [self.run]
        self.dispatches = 0
        original = remote.command
        def command(args, cwd):
            if args[:3] == ['gh', 'workflow', 'run']:
                self.dispatches += 1
                return ''
            if args[:3] == ['gh', 'run', 'download']:
                target = Path(args[args.index('--dir') + 1])
                for path in self.artifact.iterdir(): shutil.copy2(path, target)
                return ''
            return original(args, cwd)
        def api(path, repo):
            if path.startswith('actions/workflows/'):
                return {'workflow_runs': copy.deepcopy(self.rows)}
            if path.startswith('contents/'):
                return {'sha': self.git('rev-parse', 'origin/main:' + remote.WORKFLOW_PATH)}
            raise AssertionError(path)
        self.addCleanup(patch.stopall)
        patch.object(remote, 'command', side_effect=command).start()
        patch.object(remote, 'api', side_effect=api).start()

    def save_artifact(self):
        self.receipt['files'] = {name: {'bytes': len((self.artifact / name).read_bytes()),
            'sha256': hashlib.sha256((self.artifact / name).read_bytes()).hexdigest()}
            for name in remote.FILES}
        (self.artifact / 'execution.json').write_text(json.dumps(self.receipt))

    def test_completed_execution_imports_unchanged_bytes_and_original_reader_accepts(self):
        code, result = remote.ensure(self.repo)
        self.assertEqual(code, 0)
        self.assertEqual(result['execution_host'], 'GitHub Actions')
        self.assertEqual((self.artifact / 'verdict.json').read_bytes(),
                         (self.repo / 'out/gates/verdict.json').read_bytes())
        self.assertEqual(self.dispatches, 0)

    def test_active_execution_is_reused_without_a_duplicate_or_passing_verdict(self):
        self.rows[0]['status'] = 'in_progress'; self.rows[0]['conclusion'] = None
        code, result = remote.ensure(self.repo)
        self.assertEqual((code, result['run_id']), (3, '123'))
        self.assertEqual(self.dispatches, 0)
        self.assertFalse((self.repo / 'out/gates/verdict.json').exists())

    def test_repeated_start_preserves_one_dispatch_intent(self):
        self.rows = []
        self.assertEqual(remote.ensure(self.repo)[0], 3)
        self.assertEqual(remote.ensure(self.repo)[0], 3)
        self.assertEqual(self.dispatches, 1)

    def test_failed_run_requires_its_exact_retained_identity_before_retry(self):
        self.rows[0]['conclusion'] = 'failure'
        with self.assertRaises(ValueError): remote.ensure(self.repo)
        with self.assertRaises(ValueError): remote.ensure(self.repo, 'unrelated')
        self.assertEqual(remote.ensure(self.repo, '123')[0], 3)
        self.assertEqual(remote.ensure(self.repo, '123')[0], 3)
        self.assertEqual(self.dispatches, 1)

    def test_dirty_candidate_is_refused_before_remote_work(self):
        (self.repo / 'uncommitted.txt').write_text('different input')
        with self.assertRaises(ValueError): remote.ensure(self.repo)
        self.assertEqual(self.dispatches, 0)

    def test_wrong_workflow_revision_is_refused_without_import(self):
        with patch.object(remote, 'api', side_effect=lambda path, repo:
                {'workflow_runs': self.rows} if path.startswith('actions/') else {'sha': '0' * 40}):
            with self.assertRaises(ValueError): remote.ensure(self.repo)
        self.assertFalse((self.repo / 'out/gates/verdict.json').exists())

    def test_wrong_identity_or_failed_exit_never_imports(self):
        for key, value in (('candidate_sha', '0' * 40), ('checkout_sha', '0' * 40),
                           ('workflow_sha', '0' * 40), ('run_id', '999'), ('run_attempt', '2'),
                           ('workflow_ref', 'another repository'), ('suite_exit', 1), ('verdict_exit', 2)):
            original = self.receipt[key]; self.receipt[key] = value; self.save_artifact()
            with self.subTest(key=key), self.assertRaises(ValueError): remote.ensure(self.repo)
            self.assertFalse((self.repo / 'out/gates/verdict.json').exists())
            self.receipt[key] = original

    def test_changed_bytes_are_refused(self):
        (self.artifact / 'full-run.log').write_text('tampered after its recorded execution')
        with self.assertRaises(ValueError): remote.ensure(self.repo)

    def test_fast_or_different_candidate_verdict_cannot_be_promoted(self):
        path = self.artifact / 'verdict.json'
        original = json.loads(path.read_text())
        for mutation in ('fast', 'head'):
            verdict = copy.deepcopy(original)
            if mutation == 'fast': verdict['invocation']['fast'] = True
            else: verdict['state']['head'] = '0' * 40
            path.write_text(json.dumps(verdict)); self.save_artifact()
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): remote.ensure(self.repo)
        self.assertFalse((self.repo / 'out/gates/verdict.json').exists())

    def test_original_reader_still_refuses_a_stale_tree_even_with_matching_hashes(self):
        path = self.artifact / 'verdict.json'
        verdict = json.loads(path.read_text())
        verdict['state']['tree'] = 'wrongtree'
        verdict['state_at_start'] = copy.deepcopy(verdict['state'])
        path.write_text(json.dumps(verdict)); self.save_artifact()
        with self.assertRaisesRegex(ValueError, 'original local verdict reader refused'):
            remote.ensure(self.repo)

    def test_prior_original_verdict_is_preserved_byte_for_byte(self):
        previous = self.repo / 'out/gates/verdict.json'
        prior = b'previous failed or incomplete execution bytes\n'
        previous.write_bytes(prior)
        self.assertEqual(remote.ensure(self.repo)[0], 0)
        archived = list((self.repo / 'out/gates/remote-executions' / self.sha).glob('prior-verdict-*'))
        self.assertEqual(len(archived), 1)
        self.assertEqual(archived[0].read_bytes(), prior)


if __name__ == '__main__':
    unittest.main()
