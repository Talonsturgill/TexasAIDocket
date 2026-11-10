#!/usr/bin/env python3
"""Check the files Pages receives and the bytes readers receive after deployment.

Freshness proves the builder agrees with docs, not that the upload contains docs or
that Pages published it. Keep those proofs separate and fail closed on each.
"""
from __future__ import annotations
import argparse
import hashlib
import io
from pathlib import Path, PurePosixPath
import tarfile
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
LIMIT = 1_000_000_000  # Pages' published-site limit, with a conservative decimal GB.


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def inventory(site: Path) -> dict[str, str]:
    files = {}
    size = 0
    for path in sorted(site.rglob('*')):
        if path.is_symlink():
            raise ValueError(f'Pages input contains a symbolic link: {path}')
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f'Pages input contains a special file: {path}')
        name = path.relative_to(site).as_posix()
        if any(part in ('.git', '.github') for part in path.relative_to(site).parts):
            raise ValueError(f'Pages upload excludes repository metadata path: {name}')
        data = path.read_bytes()
        size += len(data)
        files[name] = digest(data)
    if 'index.html' not in files:
        raise ValueError('Pages input has no root index.html')
    if size >= LIMIT:
        raise ValueError(f'Pages input exceeds published-site limit: {size} bytes')
    if len({n.casefold() for n in files}) != len(files):
        raise ValueError('Pages input has case-colliding paths')
    return files


def check_archive(archive: Path, expected: dict[str, str]) -> None:
    actual = {}
    with tarfile.open(archive) as tar:
        for member in tar:
            path = PurePosixPath(member.name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError(f'Unsafe archive path: {member.name}')
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError(f'Pages archive contains a link or special entry: {member.name}')
            name = path.as_posix()
            if name in actual:
                raise ValueError(f'Duplicate archive file: {name}')
            if name not in expected or member.size >= LIMIT:
                raise ValueError(f'Unexpected archive file: {name}')
            actual[name] = digest(tar.extractfile(member).read())
    if actual != expected:
        bad = sorted(n for n in actual.keys() | expected.keys() if actual.get(n) != expected.get(n))
        raise ValueError(f'Pages archive differs from verified site: {bad[:10]}')


def probes(site: Path) -> list[str]:
    paths = ['index.html', 'articles/index.html', 'feed.json', 'sitemap.xml']
    # The latest five web editions are precisely the publication surface at issue.
    paths += [p.relative_to(site).as_posix() for p in
              sorted((site / 'articles').glob('*/index.html'), reverse=True)[:5]]
    return paths


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={
        'User-Agent': 'TexasAIDocket-release-check/1.0', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read()


def check_live(site: Path, url: str, wait_seconds: int, fetcher=fetch,
               clock=time.monotonic, sleep=time.sleep) -> None:
    expected = {p: digest((site / p).read_bytes()) for p in probes(site)}
    pending = dict(expected)
    deadline = clock() + wait_seconds
    while pending:
        failures = {}
        for path, sha in list(pending.items()):
            route = path[:-10] if path.endswith('index.html') else path
            # A content-derived query avoids accepting a cached previous release.
            target = f'{url.rstrip("/")}/{route}?release={sha[:20]}'
            try:
                if digest(fetcher(target)) == sha:
                    del pending[path]
                else:
                    failures[path] = 'served bytes differ from verified commit'
            except (OSError, urllib.error.URLError) as exc:
                failures[path] = str(exc)
        if not pending:
            print(f'Live release verified: {len(expected)} pages/feeds match the checked-out commit')
            return
        if clock() >= deadline:
            raise ValueError(f'Live release not verified: {failures}')
        print(f'Waiting for Pages propagation: {failures}', flush=True)
        sleep(min(15, max(0, deadline - clock())))


def self_test() -> None:
    scratch = ROOT / 'out' / 'pages-release-tests' / 'tmp'
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as tmp:
        root = Path(tmp)
        site = root / 'docs'
        for name in ['index.html', 'articles/index.html', 'feed.json', 'sitemap.xml',
                     'articles/2026-11-10/index.html']:
            p = site / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(name)
        expected = inventory(site)
        archive = root / 'artifact.tar'
        with tarfile.open(archive, 'w') as tar:
            tar.add(site, arcname='.')
        check_archive(archive, expected)
        def refuses(call):
            try:
                call()
            except ValueError:
                return
            raise AssertionError('bad input was accepted')
        (site / 'index.html').write_text('changed')
        refuses(lambda: check_archive(archive, inventory(site)))
        (site / 'index.html').write_text('index.html')
        for kind in ['missing', 'extra', 'duplicate', 'link', 'parent']:
            with tarfile.open(archive, 'w') as tar:
                for n in expected:
                    if kind == 'missing' and n == 'index.html':
                        continue
                    tar.add(site / n, arcname=n)
                if kind in ['extra', 'duplicate', 'parent']:
                    name = {'extra': 'bad', 'duplicate': 'index.html', 'parent': '../bad'}[kind]
                    info = tarfile.TarInfo(name); info.size = 1
                    tar.addfile(info, io.BytesIO(b'x'))
                if kind == 'link':
                    info = tarfile.TarInfo('link'); info.type = tarfile.SYMTYPE
                    info.linkname = 'index.html'; tar.addfile(info)
            refuses(lambda: check_archive(archive, expected))
        refuses(lambda: check_live(site, 'https://example.test', 0, fetcher=lambda _: b'stale'))
        def current(url):
            name = url.split('https://example.test/')[1].split('?')[0]
            return (site / (name + 'index.html' if not name or name.endswith('/') else name)).read_bytes()
        check_live(site, 'https://example.test', 0, fetcher=current)
        def missing(_):
            raise urllib.error.URLError('missing')
        refuses(lambda: check_live(site, 'https://example.test', 0, fetcher=missing))
        (site / 'hidden').symlink_to(site / 'index.html')
        refuses(lambda: inventory(site))
    print('pages_release_check self-test passed')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', type=Path, default=ROOT / 'docs')
    parser.add_argument('--archive', type=Path)
    parser.add_argument('--url')
    parser.add_argument('--wait-seconds', type=int, default=0)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            return 0
        expected = inventory(args.site)
        print(f'Pages input verified: {len(expected)} files')
        if args.archive:
            check_archive(args.archive, expected)
            print('Pages archive exactly matches the verified site')
        if args.url:
            if not 0 <= args.wait_seconds <= 600:
                raise ValueError('Live check wait must be between 0 and 600 seconds')
            check_live(args.site, args.url, args.wait_seconds)
    except (ValueError, OSError, tarfile.TarError) as exc:
        print(f'ERROR: {exc}')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
