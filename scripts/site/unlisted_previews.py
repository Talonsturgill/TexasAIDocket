#!/usr/bin/env python3
"""Deterministic, no-discovery publication of self-contained concept previews.

These are synthetic business discussion artifacts, separate from the civic record. Each source
is an explicitly approved HTML payload with an unguessable filename. It has no directory index,
no public listing and no sitemap entry. This is link-only discovery, not access control.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import csp

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "unlisted-previews"
NAME = re.compile(r"^[a-f0-9]{48}\.html$")
DESTINATION = "p"


def validate(name: str, text: str) -> None:
    if not NAME.fullmatch(name):
        raise ValueError("preview filename must carry a 192-bit random-path token")
    robots = re.search(r'<meta name="robots" content="([^"]+)">', text)
    if not robots or not {"noindex", "nofollow", "noarchive"}.issubset(
            {p.strip().lower() for p in robots.group(1).split(",")}):
        raise ValueError("preview must declare noindex, nofollow and noarchive")
    if '<meta name="referrer" content="no-referrer">' not in text:
        raise ValueError("preview must suppress outgoing referrers")
    if "SYNTHETIC DEMONSTRATION" not in text or "INDEPENDENT CONCEPT" not in text:
        raise ValueError("preview must preserve its synthetic and independent attribution")
    if re.search(r"OWNER REVIEW|uncontacted.prospect|sender.readiness|\$0 SERVICES|/Users/|/tmp/", text, re.I):
        raise ValueError("preview contains internal-only context")
    if "data:application/pdf;base64,JVBER" not in text:
        raise ValueError("preview must include its client-safe downloadable PDF")
    if "'unsafe-inline'" in text or "connect-src 'none'" not in text:
        raise ValueError("preview must hash inline blocks and forbid network connections")
    findings = csp.audit(text, "https://texasaidocket.com")
    if findings:
        raise ValueError("preview content policy failed " + "; ".join(findings))


def payloads(source: Path = SOURCE) -> list[tuple[str, str]]:
    if not source.exists():
        return []
    rows = []
    for file in sorted(source.iterdir()):
        if not file.is_file() or file.suffix != ".html":
            raise ValueError("unlisted preview inputs must be HTML payloads only")
        text = file.read_text(encoding="utf-8")
        validate(file.name, text)
        rows.append((f"{DESTINATION}/{file.name}", text))
    return rows


def write(out: Path, source: Path = SOURCE) -> list[str]:
    """Generate only the approved payloads, leaving unrelated existing output untouched."""
    written = []
    for rel, text in payloads(source):
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8")
        written.append(rel)
    return written


def audit_discovery(out: Path, source: Path = SOURCE) -> dict:
    targets = [rel for rel, _ in payloads(source)]
    names = [Path(rel).stem.encode() for rel in targets]
    leaks = []
    checked = 0
    for file in out.rglob("*"):
        if not file.is_file() or file.relative_to(out).as_posix() in targets:
            continue
        checked += 1
        data = file.read_bytes()
        if any(name in data for name in names):
            leaks.append(file.relative_to(out).as_posix())
    if leaks:
        raise ValueError("unlisted preview referenced outside itself " + ", ".join(leaks))
    for rel in targets:
        if not (out / rel).is_file():
            raise ValueError("approved unlisted preview was not generated")
        validate(Path(rel).name, (out / rel).read_text(encoding="utf-8"))
    return {"previews": len(targets), "other_public_files_checked": checked, "discovery_leaks": []}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=ROOT / "docs")
    ap.add_argument("--audit", action="store_true")
    args = ap.parse_args()
    if args.audit:
        print(audit_discovery(args.out))
    else:
        print(f"generated {len(write(args.out))} unlisted preview(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
