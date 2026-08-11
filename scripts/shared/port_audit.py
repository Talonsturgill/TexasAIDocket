#!/usr/bin/env python3
"""port_audit.py — is the port actually done, and is what we moved actually wired up?

WHY THIS EXISTS
The previous attempt at this port failed in a specific way: files were copied across and then
never connected to anything. Nothing was obviously broken, because an unreferenced script does
not throw. It just quietly is not part of the machine, while the plan says it is.

So "done" is not a feeling here, it is these checks passing:

  1 COVERAGE   every manifest row is resolved, and every DROP states why
  2 RESIDUE    no Alaska name survives outside a short allowlist of lineage notes
  3 WIRING     every script is reachable from a workflow, a prompt, or another script
  4 SCHEMA     every ledger parses and carries the envelope the readers expect
  5 LINKS      every internal link in the built site resolves to a real file
  6 AGENTS     every agent and skill a prompt names exists on disk
  7 PARITY     Texas config carries every key its Alaska counterpart did

Checks whose subject does not exist yet report SKIP rather than failing, so this is useful
from the first wave rather than only at the end.

    port_audit.py                # run everything
    port_audit.py --summary      # just the progress table
    port_audit.py --only wiring
    port_audit.py --self-test    # prove the gate can go red

EXIT CODES
    0  clean            1  at least one check failed            2  the audit itself broke
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "PORT_MANIFEST.tsv"

# Alaska names that must not survive the port. Deliberately narrower than the detector in
# gen_port_manifest.py: this one runs against Texas source, where a false positive is noise a
# human has to triage, so ambiguous words ("arctic", "aurora") are left out and the
# unmistakable ones are kept.
RESIDUE = re.compile(
    r"\balaska\w*\b|\banchorage\b|\bfairbanks\b|\bjuneau\b|cook\s*inlet|\brailbelt\b|"
    r"\bkenai\b|\bcingsa\b|\benstar\b|\bchugach\b|\bgvea\b|\biditarod\b|\bdenali\b|"
    r"\bnenana\b|\butqiagvik\b|\bancsa\b|alaskaaihq|alaskaaicarousels|forget.me.not",
    re.IGNORECASE,
)

# Files that are ALLOWED to name Alaska, because naming it is their job: the port plan, the
# tools that read it, and the documents that record where this machine came from.
RESIDUE_ALLOW = {
    "PORT_MANIFEST.tsv",
    "scripts/shared/gen_port_manifest.py",
    "scripts/shared/port_audit.py",
    "scripts/shared/ownership_check.py",
    "ownership.yaml",
    ".claude/WORKLOG.md",
    "CLAUDE.md",
    "README.md",
    # Design records for the two numeric instruments. These name the upstream product on
    # purpose: each documents which discipline was inherited and why, and a rule stripped of
    # its reason is a rule the next context talks itself out of. Listed by exact path rather
    # than a directory glob so the exemption cannot quietly spread.
    "knowledge/shared/GRID_WATCH_DESIGN.md",
    "knowledge/shared/OIL_WATCH_DESIGN.md",
}

# Scripts that are legitimately entry points nobody imports: run by hand, or by a human
# following a runbook. Anything not here must be reachable, or it is dead weight.
STANDALONE_ALLOW = {
    "scripts/shared/gen_port_manifest.py",
    "scripts/shared/port_audit.py",
    "scripts/shared/ownership_check.py",
}

SKIP_SCAN_DIRS = {".git", "node_modules", "__pycache__", "out", "docs", "runs", "vendor"}
TEXT_SUFFIXES = {".py", ".md", ".yaml", ".yml", ".json", ".txt", ".js", ".mjs", ".ts",
                 ".tsx", ".html", ".css", ".sh", ".tsv"}


class Result:
    def __init__(self, name: str):
        self.name, self.status, self.lines = name, "PASS", []

    def fail(self, msg: str):
        self.status = "FAIL"
        self.lines.append(msg)

    def skip(self, msg: str):
        if self.status == "PASS":
            self.status = "SKIP"
            self.lines.append(msg)

    def note(self, msg: str):
        self.lines.append(msg)


def walk_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_SCAN_DIRS for part in rel.parts):
            continue
        yield rel, path


def read_manifest(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


# --------------------------------------------------------------------------- 1 coverage
def check_coverage(root: Path) -> Result:
    r = Result("coverage")
    mpath = root / "PORT_MANIFEST.tsv"
    if not mpath.exists():
        r.fail("PORT_MANIFEST.tsv missing; run gen_port_manifest.py")
        return r
    rows = read_manifest(mpath)
    if not rows:
        r.fail("manifest is empty")
        return r

    unrouted = [x for x in rows if x["disposition"] == "UNROUTED"]
    for x in unrouted[:10]:
        r.fail(f"UNROUTED: {x['source_repo']}/{x['source_path']}")
    if len(unrouted) > 10:
        r.fail(f"...and {len(unrouted) - 10} more unrouted")

    dropped_no_reason = [x for x in rows
                         if x["disposition"] == "DROP" and not x["reason"].strip()]
    for x in dropped_no_reason[:10]:
        r.fail(f"DROP without a reason: {x['source_repo']}/{x['source_path']}")

    todo = [x for x in rows if x["status"] == "TODO"]
    done = [x for x in rows if x["status"] == "DONE"]
    dropped = [x for x in rows if x["status"] == "DROPPED"]
    total_work = len(rows) - len(dropped)
    pct = (len(done) / total_work * 100) if total_work else 100.0
    r.note(f"{len(done)}/{total_work} ported ({pct:.0f}%), {len(dropped)} deliberately dropped")
    if todo:
        by_repo: dict[str, int] = {}
        for x in todo:
            by_repo[x["source_repo"]] = by_repo.get(x["source_repo"], 0) + 1
        r.skip("still to port: " + ", ".join(f"{k} {v}" for k, v in sorted(by_repo.items())))
    return r


# --------------------------------------------------------------------------- 2 residue
def check_residue(root: Path) -> Result:
    r = Result("residue")
    hits = 0
    for rel, path in walk_text_files(root):
        if rel.as_posix() in RESIDUE_ALLOW:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            m = RESIDUE.search(line)
            if m:
                hits += 1
                if hits <= 12:
                    r.fail(f"{rel}:{i}: {m.group(0)!r} in: {line.strip()[:90]}")
    if hits > 12:
        r.fail(f"...and {hits - 12} more Alaska references")
    if hits == 0:
        r.note("no Alaska names outside the allowlist")
    return r


# --------------------------------------------------------------------------- 3 wiring
def check_wiring(root: Path) -> Result:
    """The check that catches "we moved it but never hooked it up"."""
    r = Result("wiring")
    scripts = sorted(p.relative_to(root).as_posix()
                     for p in (root / "scripts").rglob("*.py")) if (root / "scripts").exists() else []
    if not scripts:
        r.skip("no scripts yet")
        return r

    # Everything that could plausibly name a script: prompts, workflows, other code, docs.
    haystack: list[tuple[str, str]] = []
    for rel, path in walk_text_files(root):
        try:
            haystack.append((rel.as_posix(), path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    for wf in (root / ".github" / "workflows").glob("*.y*ml") if (root / ".github" / "workflows").exists() else []:
        haystack.append((wf.relative_to(root).as_posix(), wf.read_text(encoding="utf-8", errors="ignore")))

    orphans = []
    for script in scripts:
        if script in STANDALONE_ALLOW:
            continue
        name = Path(script).name
        stem = Path(script).stem
        referenced = False
        for holder, text in haystack:
            if holder == script:
                continue                                  # a file naming itself proves nothing
            if name in text or re.search(rf"\bimport\s+{re.escape(stem)}\b", text) \
                    or re.search(rf"\bfrom\s+{re.escape(stem)}\s+import\b", text):
                referenced = True
                break
        if not referenced:
            orphans.append(script)

    for o in orphans:
        r.fail(f"{o} is not referenced by any workflow, prompt, or other script")
    if not orphans:
        r.note(f"all {len(scripts)} script(s) reachable")
    return r


# --------------------------------------------------------------------------- 4 schema
def check_schema(root: Path) -> Result:
    r = Result("schema")
    ledger = root / "ledger"
    if not ledger.exists():
        r.skip("no ledger yet")
        return r
    seen = 0
    for path in sorted(ledger.rglob("*.json")):
        seen += 1
        rel = path.relative_to(root).as_posix()
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            r.fail(f"{rel}: does not parse: {exc}")
            continue
        if isinstance(doc, dict) and "_spec" not in doc:
            r.fail(f"{rel}: missing the _spec envelope every ledger carries")
    for path in sorted(ledger.rglob("*.jsonl")):
        seen += 1
        rel = path.relative_to(root).as_posix()
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                r.fail(f"{rel}:{i}: bad JSONL: {exc}")
                break
    if seen == 0:
        r.skip("no ledger files yet")
    elif r.status == "PASS":
        r.note(f"{seen} ledger file(s) valid")
    return r


# --------------------------------------------------------------------------- 5 links
def check_links(root: Path) -> Result:
    r = Result("links")
    docs = root / "docs"
    if not docs.exists():
        r.skip("site not built yet")
        return r
    href = re.compile(r'(?:href|src)="([^"#?]+)"')
    broken, checked = [], 0
    for page in docs.rglob("*.html"):
        text = page.read_text(encoding="utf-8", errors="ignore")
        for target in href.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "data:", "//")):
                continue
            checked += 1
            base = docs if target.startswith("/") else page.parent
            dest = (base / target.lstrip("/")).resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                broken.append(f"{page.relative_to(root)} -> {target}")
    for b in broken[:12]:
        r.fail(f"broken link: {b}")
    if len(broken) > 12:
        r.fail(f"...and {len(broken) - 12} more broken links")
    if not broken:
        r.note(f"{checked} internal link(s) resolve")
    return r


# --------------------------------------------------------------------------- 6 agents
def check_agents(root: Path) -> Result:
    r = Result("agents")
    prompts = root / "prompts"
    agents_dir = root / ".claude" / "agents"
    if not prompts.exists():
        r.skip("no prompts yet")
        return r
    available = {p.stem for p in agents_dir.glob("*.md")} if agents_dir.exists() else set()
    # A prompt names an agent as `spawn the X agent` or backticked. Matching the phrasing the
    # routine prompts actually use rather than every capitalised word.
    pat = re.compile(r"(?:spawn|launch)\s+(?:a\s+|an\s+|the\s+)?`?([a-z][a-z0-9-]{2,})`?\s+agent",
                     re.IGNORECASE)
    named: set[str] = set()
    for prompt in prompts.rglob("*.md"):
        named |= {m.lower() for m in pat.findall(prompt.read_text(encoding="utf-8", errors="ignore"))}
    missing = sorted(named - available)
    for m in missing:
        r.fail(f"prompt names agent '{m}' but .claude/agents/{m}.md does not exist")
    if not named:
        r.skip("no agents referenced by prompts yet")
    elif not missing:
        r.note(f"{len(named)} agent reference(s) all resolve")
    return r


# --------------------------------------------------------------------------- 7 parity
def check_parity(root: Path) -> Result:
    """Texas config must carry every KEY its Alaska counterpart had. Values differ, shape
    does not. This is what catches a half-ported config that looks finished."""
    r = Result("parity")
    try:
        import yaml
    except ImportError:
        r.skip("PyYAML unavailable")
        return r
    pairs = [(root / "config" / "brand.yaml",
              Path("/home/user/alaskaaicarousels/config/brand.yaml"))]
    checked = 0
    for texas, alaska in pairs:
        if not texas.exists():
            continue
        if not alaska.exists():
            r.skip(f"reference {alaska} not on disk")
            continue
        checked += 1

        def keys(node, prefix=""):
            out = set()
            if isinstance(node, dict):
                for k, v in node.items():
                    out.add(f"{prefix}{k}")
                    out |= keys(v, f"{prefix}{k}.")
            return out

        missing = keys(yaml.safe_load(alaska.read_text(encoding="utf-8"))) - \
            keys(yaml.safe_load(texas.read_text(encoding="utf-8")))
        for k in sorted(missing)[:15]:
            r.fail(f"{texas.relative_to(root)} is missing key '{k}'")
        if len(missing) > 15:
            r.fail(f"...and {len(missing) - 15} more missing keys")
    if checked == 0:
        r.skip("no config to compare yet")
    elif r.status == "PASS":
        r.note(f"{checked} config file(s) at full key parity")
    return r


CHECKS = {
    "coverage": check_coverage, "residue": check_residue, "wiring": check_wiring,
    "schema": check_schema, "links": check_links, "agents": check_agents,
    "parity": check_parity,
}


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    """Prove each gate can go red, using a throwaway tree. A gate that cannot fail proves
    nothing about what it guards."""
    import tempfile
    failures = 0

    def expect(label: str, result: Result, want: str):
        nonlocal failures
        ok = result.status == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {label} -> {result.status}")
        if not ok:
            failures += 1
            for line in result.lines[:3]:
                print(f"        {line}", file=sys.stderr)

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "scripts" / "shared").mkdir(parents=True)
        (root / "ledger").mkdir()
        (root / "prompts").mkdir()
        (root / ".claude" / "agents").mkdir(parents=True)

        # residue: a live Alaska name must be caught
        (root / "scripts" / "a.py").write_text("# built for Anchorage\n", encoding="utf-8")
        expect("residue catches a stray Alaska name", check_residue(root), "FAIL")
        (root / "scripts" / "a.py").write_text("# built for Houston\n", encoding="utf-8")
        expect("residue passes clean Texas source", check_residue(root), "PASS")

        # wiring: an unreferenced script must be caught, and a referenced one must pass
        expect("wiring catches an orphan script", check_wiring(root), "FAIL")
        (root / "prompts" / "r.md").write_text("then run scripts/a.py\n", encoding="utf-8")
        expect("wiring passes a referenced script", check_wiring(root), "PASS")

        # schema: bad json, then a missing envelope, then valid
        (root / "ledger" / "x.json").write_text("{not json", encoding="utf-8")
        expect("schema catches unparseable json", check_schema(root), "FAIL")
        (root / "ledger" / "x.json").write_text('{"items": []}', encoding="utf-8")
        expect("schema catches a missing _spec envelope", check_schema(root), "FAIL")
        (root / "ledger" / "x.json").write_text('{"_spec": {}, "items": []}', encoding="utf-8")
        expect("schema passes a well-formed ledger", check_schema(root), "PASS")
        (root / "ledger" / "s.jsonl").write_text('{"d":1}\nnot json\n', encoding="utf-8")
        expect("schema catches bad jsonl", check_schema(root), "FAIL")
        (root / "ledger" / "s.jsonl").write_text('{"d":1}\n{"d":2}\n', encoding="utf-8")
        expect("schema passes good jsonl", check_schema(root), "PASS")

        # agents: a named-but-absent agent must be caught
        (root / "prompts" / "r.md").write_text(
            "run scripts/a.py then spawn the scout agent\n", encoding="utf-8")
        expect("agents catches a missing agent file", check_agents(root), "FAIL")
        (root / ".claude" / "agents" / "scout.md").write_text("x", encoding="utf-8")
        expect("agents passes when the file exists", check_agents(root), "PASS")

        # links: a dangling href must be caught
        docs = root / "docs"
        docs.mkdir()
        (docs / "index.html").write_text('<a href="nope/">x</a>', encoding="utf-8")
        expect("links catches a dangling href", check_links(root), "FAIL")
        (docs / "nope").mkdir()
        (docs / "nope" / "index.html").write_text("ok", encoding="utf-8")
        expect("links passes when the target exists", check_links(root), "PASS")

        # coverage: unrouted rows and reasonless drops must be caught
        man = root / "PORT_MANIFEST.tsv"
        head = "\t".join(["source_repo", "source_path", "bytes", "lines", "ak_hits",
                          "disposition", "target_path", "status", "reason"])
        man.write_text(head + "\n" + "\t".join(
            ["r", "p", "1", "1", "0", "UNROUTED", "", "TODO", ""]) + "\n", encoding="utf-8")
        expect("coverage catches an unrouted row", check_coverage(root), "FAIL")
        man.write_text(head + "\n" + "\t".join(
            ["r", "p", "1", "1", "0", "DROP", "", "DROPPED", ""]) + "\n", encoding="utf-8")
        expect("coverage catches a DROP with no reason", check_coverage(root), "FAIL")
        man.write_text(head + "\n" + "\t".join(
            ["r", "p", "1", "1", "0", "DROP", "", "DROPPED", "because"]) + "\n", encoding="utf-8")
        expect("coverage passes a justified drop", check_coverage(root), "PASS")

    if failures:
        print(f"\nport_audit self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nport_audit self-test: all passed (every gate can go red)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(REPO_ROOT))
    ap.add_argument("--only", nargs="*", choices=sorted(CHECKS), help="run only these checks")
    ap.add_argument("--summary", action="store_true", help="coverage progress only")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    root = Path(args.root)
    names = args.only or (["coverage"] if args.summary else list(CHECKS))

    print(f"port audit  {root}\n")
    worst = 0
    for name in names:
        try:
            res = CHECKS[name](root)
        except Exception as exc:                                  # noqa: BLE001
            print(f"  ERROR {name}: {exc}", file=sys.stderr)
            worst = max(worst, 2)
            continue
        mark = {"PASS": "PASS", "SKIP": "SKIP", "FAIL": "FAIL"}[res.status]
        print(f"  [{mark}] {res.name}")
        for line in res.lines:
            print(f"         {line}")
        if res.status == "FAIL":
            worst = max(worst, 1)
    print()
    if worst == 0:
        print("port audit: clean")
    elif worst == 1:
        print("port audit: FAILED", file=sys.stderr)
    return worst


if __name__ == "__main__":
    sys.exit(main())
