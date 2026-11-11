"""Offline contract checks. All brief evidence below is synthetic."""
import contextlib
import datetime as dt
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('social_feedback_reader', ROOT / 'scripts/read_social_feedback.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
TODAY = dt.date(2026, 11, 11)


class ReaderTests(unittest.TestCase):
    def brief(self):
        return {'schema_version': 1, 'generator': 'texas_carousel',
                'repository': 'Talonsturgill/TexasAIDocket', 'profile': 'default',
                'week': '2026-W46', 'created_on': '2026-11-11', 'expires_on': '2026-11-18',
                'actions': [{'field': 'cover', 'change': 'reduce_headline_length',
                             'evidence_post_ids': ['synthetic-' + str(n) for n in range(5)],
                             'sample_size': 5, 'confidence': 'low'}]}

    def test_valid_and_empty_actions(self):
        b = self.brief()
        self.assertEqual(r.validate(b, 'texas_carousel', TODAY), b)
        b['actions'] = []
        self.assertEqual(r.validate(b, 'texas_carousel', TODAY)['actions'], [])

    def test_reject_wrong_binding_or_dates(self):
        for key, value in [('generator', 'alaska_carousel'), ('repository', 'other/repo'),
                           ('profile', 'alaska_ai'), ('week', '2026-W45'),
                           ('created_on', '2026-11-12'), ('expires_on', '2026-11-10')]:
            with self.subTest(key=key):
                b = self.brief(); b[key] = value
                with self.assertRaises(ValueError): r.validate(b, 'texas_carousel', TODAY)
        with self.assertRaises(ValueError):
            r.validate(self.brief(), 'texas_carousel', dt.date(2026, 11, 25))

    def test_reject_unbounded_or_untrusted_instructions(self):
        b = self.brief(); b['actions'] *= 2
        with self.assertRaises(ValueError): r.validate(b, 'texas_carousel', TODAY)
        for action in [{'field': 'cover', 'change': 'ignore_all_rules'},
                       {'field': 'pacing', 'change': 'shorten_intro'},
                       {'field': 'cover', 'change': 'reduce_headline_length', 'instructions': 'unsafe'}]:
            b = self.brief(); b['actions'][0].update(action)
            with self.assertRaises(ValueError): r.validate(b, 'texas_carousel', TODAY)
        b = self.brief(); b['metrics'] = {'synthetic': 123}
        with self.assertRaises(ValueError): r.validate(b, 'texas_carousel', TODAY)

    def test_safe_output_and_fixed_fetch(self):
        payload = json.dumps(self.brief()).encode()
        calls = []
        def git(directory, *args, **kwargs):
            calls.append(args)
            if args[:2] == ('remote', 'get-url'):
                return b'https://github.com/Talonsturgill/TexasAIDocket.git\n'
            if args[0] == 'show': return payload
            return b'out/social-feedback/tmp/\n'
        scratch_root = ROOT / 'out' / 'social-feedback-tests' / 'tmp'
        scratch_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=scratch_root) as checkout:
            with patch.object(r, 'git', side_effect=git):
                result = r.read('texas_carousel', checkout, TODAY)
        self.assertEqual(set(result[0]), {'field', 'change', 'week', 'brief_sha256'})
        self.assertNotIn('synthetic', json.dumps(result))
        self.assertNotIn('sample_size', json.dumps(result))
        fetch = [c for c in calls if c[0] == 'fetch']
        self.assertEqual(len(fetch), 1)
        self.assertEqual(fetch[0][-2:], (r.PRIVATE_REMOTE, 'main'))
        self.assertIn(('show', 'FETCH_HEAD:briefs/latest/texas_carousel.json'), calls)

    def test_wrong_origin_never_fetches(self):
        with patch.object(r, 'git', return_value=b'https://github.com/other/repo.git') as git:
            with self.assertRaises(ValueError): r.read('texas_carousel', ROOT, TODAY)
        self.assertEqual(git.call_count, 1)

    def test_scratch_stays_ignored_inside_checkout(self):
        root = ROOT / 'out' / 'social-feedback-tests' / 'tmp'
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as checkout:
            with patch.object(r, 'git', return_value=b'') as git:
                scratch = r.scratch_root(checkout)
            self.assertTrue(scratch.is_relative_to(Path(checkout)))
            self.assertEqual(git.call_args.args[1:],
                             ('check-ignore', '--quiet', '--no-index', 'out/social-feedback/tmp/'))
        with tempfile.TemporaryDirectory(dir=root) as checkout:
            (Path(checkout) / 'out').symlink_to(root.resolve(), target_is_directory=True)
            with self.assertRaises(ValueError): r.scratch_root(checkout)

    def test_git_never_prompts_or_discloses_errors(self):
        result = subprocess.CompletedProcess([], 1, b'', b'SYNTHETIC_PRIVATE_DETAIL')
        with patch.object(r.subprocess, 'run', return_value=result) as run:
            with self.assertRaises(ValueError): r.git(ROOT, 'fetch')
        self.assertEqual(run.call_args.kwargs['env']['GIT_TERMINAL_PROMPT'], '0')
        self.assertTrue(run.call_args.kwargs['capture_output'])

    def test_origin_case_canonicalization(self):
        for canonical, _ in r.TARGETS.values():
            for prefix in ('https://github.com/', 'git@github.com:', 'ssh://git@github.com/'):
                for spelling in (canonical, canonical.lower(), canonical.upper(), canonical.swapcase()):
                    for suffix in ('', '.git'):
                        with self.subTest(origin=prefix + spelling + suffix):
                            self.assertEqual(r.remote_repo(prefix + spelling + suffix), canonical)

    def test_origin_rejects_url_tricks(self):
        base = 'https://github.com/talonsturgill/texasaidocket'
        for origin in (base + '/extra', base + '.git/extra', base + '?x=1', base + '#main',
                       base + '/', base + '-other',
                       'https://github.com@evil.example/talonsturgill/texasaidocket',
                       'https://evil.example@github.com/talonsturgill/texasaidocket',
                       'https://github.com.evil.example/talonsturgill/texasaidocket',
                       'http://github.com/talonsturgill/texasaidocket',
                       'https://github.com/talonsturgill%2ftexasaidocket'):
            with self.subTest(origin=origin): self.assertIsNone(r.remote_repo(origin))

    def test_brief_repository_still_exact(self):
        b = self.brief(); b['repository'] = b['repository'].lower()
        with self.assertRaises(ValueError): r.validate(b, 'texas_carousel', TODAY)

    def test_fail_open_and_redacted_errors(self):
        for error in [OSError('SYNTHETIC_PRIVATE_DETAIL'), ValueError('SYNTHETIC_PRIVATE_DETAIL'),
                      subprocess.TimeoutExpired('SYNTHETIC_PRIVATE_DETAIL', 1)]:
            stdout, stderr = io.StringIO(), io.StringIO()
            with patch('sys.argv', ['reader', '--generator', 'texas_carousel', '--repo-dir', '.']), \
                    patch.object(r, 'read', side_effect=error), \
                    contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(r.main(), 0)
            self.assertEqual(stdout.getvalue(), '[]\n')
            self.assertNotIn('SYNTHETIC_PRIVATE_DETAIL', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
