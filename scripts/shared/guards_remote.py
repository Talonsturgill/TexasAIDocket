"""Run the complete local guard runner on its finite, durable GitHub executor.

Exit 3 means the same remote execution is pending. It is never a passing verdict.
Only the original runner's byte-identical atomic verdict can be imported, and the
original local --verdict reader must accept it on this unchanged clean candidate.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

REPOSITORY = 'Talonsturgill/TexasAIDocket'
WORKFLOW = 'full-local-verdict.yml'
WORKFLOW_PATH = '.github/workflows/' + WORKFLOW
FILES = ('verdict.json', 'full-run.log', 'full-verdict.txt')


def command(args, cwd):
    return subprocess.check_output(args, cwd=cwd, text=True, timeout=60).strip()


def api(path, repo):
    return json.loads(command(['gh', 'api', 'repos/' + REPOSITORY + '/' + path], repo))


def write_json(path, value):
    temporary = path.with_suffix('.partial')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)


def clean_candidate(repo):
    remote = command(['git', 'remote', 'get-url', 'origin'], repo).removesuffix('.git')
    if remote not in ('https://github.com/' + REPOSITORY, 'git@github.com:' + REPOSITORY):
        raise ValueError('the full verdict belongs to the selected Docket repository')
    candidate = command(['git', 'rev-parse', 'HEAD'], repo)
    if not re.fullmatch('[0-9a-f]{40}', candidate):
        raise ValueError('a committed candidate is required')
    if command(['git', 'status', '--porcelain', '--untracked-files=all'], repo):
        raise ValueError('preserve the candidate; commit or resolve its actual dirty files first')
    return candidate


@contextmanager
def locked(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a+b') as stream:
        if os.name == 'nt':
            import msvcrt
            if not path.stat().st_size:
                stream.write(b'0'); stream.flush()
            stream.seek(0)
            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == 'nt':
                stream.seek(0)
                msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(stream, fcntl.LOCK_UN)


def verify_artifact(directory, candidate, run):
    receipt_path = directory / 'execution.json'
    if (receipt_path.is_symlink() or not receipt_path.is_file()
            or receipt_path.stat().st_size > 1024 * 1024):
        raise ValueError('the actual regular execution receipt is required')
    receipt = json.loads(receipt_path.read_text())
    expected_ref = REPOSITORY + '/' + WORKFLOW_PATH + '@refs/heads/main'
    expected = {'schema': 'docket_full_local_execution/1', 'candidate_sha': candidate,
                'checkout_sha': candidate, 'workflow_sha': run['head_sha'],
                'workflow_ref': expected_ref, 'run_id': str(run['id']),
                'run_attempt': str(run['run_attempt']), 'suite_exit': 0, 'verdict_exit': 0}
    if any(receipt.get(key) != value for key, value in expected.items()):
        raise ValueError('remote execution identity or actual full-run/verdict exit does not match')
    if set(receipt.get('files', {})) != set(FILES):
        raise ValueError('the complete original execution artifacts are required')
    for name in FILES:
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 64 * 1024 * 1024:
            raise ValueError('unexpected remote artifact: ' + name)
        data = path.read_bytes()
        if receipt['files'][name] != {'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data)}:
            raise ValueError('remote artifact bytes differ: ' + name)
    verdict = json.loads((directory / 'verdict.json').read_text())
    invocation = verdict.get('invocation') or {}
    if (verdict.get('state', {}).get('head') != candidate
            or verdict.get('state_at_start') != verdict.get('state')
            or invocation.get('fast') is not False or invocation.get('only') is not None
            or verdict.get('exit') != 0):
        raise ValueError('only a completed full verdict on this unchanged candidate can be imported')
    return receipt


def ensure(repo, retry_run=None):
    repo = repo.resolve()
    candidate = clean_candidate(repo)
    root = repo / 'out/gates/remote-executions' / candidate
    if any(path.is_symlink() for path in (root, *root.parents) if path != repo and repo in path.parents):
        raise ValueError('remote execution evidence must stay in the real owned candidate')
    root.mkdir(parents=True, exist_ok=True)
    with locked(root / 'execution.lock'):
        # Only a merged, fetched main definition can supply the remote executor.
        approved_blob = command(['git', 'rev-parse', 'origin/main:' + WORKFLOW_PATH], repo)
        response = api('actions/workflows/' + WORKFLOW + '/runs?event=workflow_dispatch&per_page=100', repo)
        rows = [r for r in response['workflow_runs']
                if r.get('display_title') == 'Full local verdict for ' + candidate]
        active = [r for r in rows if r['status'] != 'completed']
        selected = active[-1] if active else next((r for r in rows if r['conclusion'] == 'success'), None)
        if selected is None and rows and retry_run != str(rows[0]['id']):
            raise ValueError('retain failed remote run ' + str(rows[0]['id'])
                             + '; repair its actual cause before --retry-run with that exact identity')
        if selected is None:
            intent = root / 'dispatch-intents.json'
            history = json.loads(intent.read_text()) if intent.exists() else []
            key = {'workflow_blob': approved_blob, 'retry_run': retry_run}
            if history and all(history[-1].get(k) == v for k, v in key.items()):
                return 3, {'status': 'pending', 'candidate_sha': candidate,
                           'reason': 'the retained dispatch is awaiting its actual GitHub run identity'}
            history.append({**key, 'requested_at': datetime.now(timezone.utc).isoformat()})
            write_json(intent, history)
            command(['gh', 'workflow', 'run', WORKFLOW, '--repo', REPOSITORY,
                     '--ref', 'main', '-f', 'candidate_sha=' + candidate], repo)
            return 3, {'status': 'pending', 'candidate_sha': candidate,
                       'reason': 'one full-runner execution dispatched; reuse it on subsequent checks'}
        run_id = str(selected['id'])
        if selected['status'] != 'completed':
            return 3, {'status': 'pending', 'candidate_sha': candidate,
                       'run_id': run_id, 'url': selected['html_url']}
        actual_blob = api('contents/' + WORKFLOW_PATH + '?ref=' + selected['head_sha'], repo)['sha']
        if actual_blob != approved_blob:
            raise ValueError('the execution used another workflow definition; preserve it without importing')
        destination = root / run_id
        if destination.is_symlink():
            raise ValueError('the retained execution directory must be real')
        if not destination.exists():
            with tempfile.TemporaryDirectory(prefix='download-', dir=root) as temporary:
                command(['gh', 'run', 'download', run_id, '--repo', REPOSITORY,
                         '--name', 'full-local-' + candidate, '--dir', temporary], repo)
                verify_artifact(Path(temporary), candidate, selected)
                os.replace(temporary, destination)
        verify_artifact(destination, candidate, selected)
        if clean_candidate(repo) != candidate:
            raise ValueError('the candidate changed while its evidence was retrieved')
        target = repo / 'out/gates/verdict.json'
        data = (destination / 'verdict.json').read_bytes()
        if target.exists() and target.read_bytes() != data:
            prior = root / ('prior-verdict-' + hashlib.sha256(target.read_bytes()).hexdigest() + '.json')
            if not prior.exists():
                shutil.copy2(target, prior)
        temporary = target.with_suffix('.remote.partial')
        temporary.write_bytes(data)
        os.replace(temporary, target)
        # Never author or translate a passing verdict. Ask the unchanged original reader.
        readback = subprocess.run([sys.executable, str(repo / 'scripts/shared/guards_local.py'), '--verdict'],
                                  cwd=repo, capture_output=True, text=True, timeout=60)
        (destination / 'local-readback.txt').write_text(readback.stdout + readback.stderr)
        if readback.returncode:
            raise ValueError('the original local verdict reader refused the imported evidence: '
                             + (readback.stdout + readback.stderr)[-3000:])
        return 0, {'status': 'complete', 'candidate_sha': candidate, 'run_id': run_id,
                   'url': selected['html_url'], 'execution_host': 'GitHub Actions',
                   'evidence': str(destination), 'local_verdict_exit': readback.returncode}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path.cwd())
    parser.add_argument('--retry-run', help='exact retained failed run, only after its cause is repaired')
    args = parser.parse_args()
    try:
        code, result = ensure(args.repo, args.retry_run)
    except (ValueError, KeyError, OSError, subprocess.SubprocessError) as exc:
        print(json.dumps({'status': 'incomplete', 'error': str(exc)}))
        return 1
    print(json.dumps(result))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
