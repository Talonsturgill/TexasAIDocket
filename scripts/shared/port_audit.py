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
  6 ASSETS     every asset the site references is an asset the site ships, AND every typeface
               it names is a typeface something defines
  7 REFS       every repo path a knowledge doc, prompt or config cites actually exists
  8 AGENTS     every agent and skill a prompt names exists on disk
  9 PARITY     Texas config carries every key its Alaska counterpart did

Three doors, one failure. WIRING catches a script that landed and was never connected. ASSETS
and REFS were added after the same failure arrived through the other two: the three brand
typefaces sat committed and unserved while every reader got Georgia, and a design doctrine was
cited by four files and had never been written. Neither threw, because a font stack falls back
silently and a citation is prose.

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

# Texas config -> the Alaska config it must stay at key parity with. Divergences are declared in
# config/parity_map.yaml, never by deleting a row from here.
REFERENCE_CONFIGS = {
    "config/brand.yaml": "/home/user/alaskaaicarousels/config/brand.yaml",
}

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
    # The application-layer research, and the routine that acts on it. Both name the sibling
    # because the correction they carry only makes sense against it: this product's beats were
    # six-of-eight policy until somebody counted the sibling's and found power and compute was
    # ONE of six there. Strip the comparison and what is left is a beat list with no argument
    # behind it, which is a list the next context reorders on a whim.
    "knowledge/shared/APPLICATIONS.md",
    "prompts/daily_routine.md",
    # The site design study. It is a device-by-device comparison against the sibling product's
    # published site, written because the owner judged the Texas one a downgrade and the answer
    # had to be specific rather than a feeling. Naming what each device was copied FROM, and
    # which four were deliberately not taken, is the entire content of the file. Same exemption
    # and same reason as the two instrument design records above.
    "knowledge/shared/SIBLING_SITE_STUDY.md",
    # The parity map is a divergence record. Naming what each key diverged FROM is the entire
    # content of the file, so it belongs with the manifest rather than with Texas source.
    "config/parity_map.yaml",
    # The mailbox. CLAUDE.md requires the address as a module constant here rather than the
    # account-relative "me", which the Gmail connector rejects outright, and the domain
    # happens to be the shared one. Listed by exact path so the exemption covers the constant
    # and nothing else: any OTHER file naming that domain is still a residue failure, which is
    # what keeps the address in the two places it belongs.
    "scripts/carousel/gmail_draft.py",
}

# Scripts that are legitimately entry points nobody imports: run by hand, or by a human
# following a runbook. Anything not here must be reachable, or it is dead weight.
STANDALONE_ALLOW = {
    "scripts/shared/gen_port_manifest.py",
    "scripts/shared/port_audit.py",
    "scripts/shared/ownership_check.py",
}

# Documents that describe intent rather than execute it. A script named only in one of these
# is planned, not wired, and the wiring check must not accept a plan as proof of a connection.
PLAN_DOCS = {".claude/WORKLOG.md", "README.md", "CLAUDE.md", "PORT_MANIFEST.tsv"}

# Paths a knowledge document names in the FUTURE tense. A doctrine that says "planned for Wave
# 7" is making a commitment, not a citation, and failing the build over one would push the next
# writer to stop writing plans down, which is worse than the dangling path.
#
# Each entry carries where it was promised and what has to happen. The refs check prints any
# entry whose file now exists, so this stays a parking space rather than a graveyard.
REFS_PLANNED = {
    "assets/lexicon/tx_pronunciation.json":
        "TEXAS_PRONUNCIATION.md, Wave 7. Belongs to TexasAIDispatch, which owns the video "
        "engine and its VO preflight, so it will never exist at this path in this repo.",
    "ledger/deployments.json":
        "The docket schema is decision-centric and a company deployment is not a decision. "
        "The provisional resolution is a second ledger that a docket item can reference. "
        "Not built, and not needed until the record carries one.",
}

# Paths a routine WRITES AND REMOVES. Absent between runs is their normal state, so unlike a
# planned path there is nothing to nag about when one appears. Kept separate from REFS_PLANNED
# precisely so the "now built, prune it" note never fires on a file whose whole life is
# transient, which would train a reader to ignore the note.
REFS_RUNTIME = {
    "prompts/NEXT_RUN.md":
        "A story queued by the previous run for the next one. The routine reads it 'if it "
        "exists' and archives it into the run directory at ship time, so it is present only "
        "between a queueing run and the run that consumes it.",
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

    # THE MANIFEST WAS LYING, AND IT IS THE ONE FILE THAT MUST NOT. Its whole job is answering
    # "is the port done", and status was hand-maintained, so 31 rows sat at TODO with their target
    # already on disk, including all ten carousel agents. Coverage read 10 percent when the real
    # figure was higher, and because coverage only NOTES it never failed. A tracking system that
    # drifts from the tree is worse than no tracking system: it is a confident wrong answer, and
    # the whole reason this file exists is that the last attempt at this port moved files across
    # and never wired them.
    #
    # So status is now CHECKED against the tree rather than trusted. A row claiming work is
    # outstanding while the file exists is a bookkeeping fault and fails. `--reconcile` writes the
    # truth back, so fixing it is one command rather than an afternoon of hand edits.
    stale = [x for x in rows
             if x["status"] == "TODO" and x["target_path"]
             and (root / x["target_path"]).exists()]
    for x in stale[:10]:
        r.fail(f"marked TODO but already on disk: {x['source_path']} -> {x['target_path']}")
    if len(stale) > 10:
        r.fail(f"...and {len(stale) - 10} more. Run: port_audit.py --reconcile")

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
    # scripts/ AND the skill engines. A skill is exactly the shape of thing this check exists
    # to catch: a few thousand lines that arrive as a directory, are never imported by anything,
    # and go stale without a single error. Nothing else in the repo would notice.
    roots = [root / "scripts", root / ".claude" / "skills"]
    scripts = sorted(p.relative_to(root).as_posix()
                     for d in roots if d.exists() for p in d.rglob("*.py"))
    if not scripts:
        r.skip("no scripts yet")
        return r

    # Only things that can INVOKE count as evidence: prompts, workflows, shell, other code.
    # Data files are excluded on purpose. A generated artifact that stamps its own producer
    # ("generated_by: scripts/shared/places.py") would otherwise vouch for that script forever,
    # which is the same self-referential hole as a file naming itself.
    CALLER_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".sh", ".js", ".mjs", ".ts", ".txt"}
    haystack: list[tuple[str, str]] = []
    for rel, path in walk_text_files(root):
        if path.suffix not in CALLER_SUFFIXES:
            continue
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
            if holder in PLAN_DOCS:
                continue    # being named in a plan is not being wired into the machine; that
                            # confusion is exactly the failure this check exists to catch
            if invokes(text, name) or re.search(rf"\bimport\s+{re.escape(stem)}\b", text) \
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


def invokes(text: str, name: str) -> bool:
    """Does this file actually PUT THE SCRIPT TO WORK, or does it only prove the script runs?

    A `--self-test` line is not wiring. It says the script's own tests pass, which is a fact
    about the script and says nothing about anything calling it in anger. Every gate in this
    repo is listed in `guards.yml` as a self-test, so counting that as a reference made the
    orphan check structurally unable to fail for the entire class of file it matters most for.

    That was not theoretical. Merging the two routine prompts into one on 2026-08-12 meant
    writing a fresh prompt and deleting both old ones, which is precisely when a gate gets
    dropped by hand. Every one of them would have kept passing this check while being invoked
    by nothing, and "we moved it and never wired it" is the single failure this whole audit
    exists to catch.

    Verified by deleting the dedupe gate's invocation from the routine: green before this
    change, red after.
    """
    for line in text.splitlines():
        if name not in line:
            continue
        if "--self-test" in line:
            continue                    # proves the script works, not that anything calls it
        return True
    return False


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
def check_archive(root: Path) -> Result:
    """Nothing the ownership map calls append-only may be gitignored.

    THIS EXISTS BECAUSE IT ALREADY HAPPENED. `ledger/gridwatch/raw/` is the raw response
    archive: the collector snapshots it BEFORE parsing, because neither ERCOT nor TWDB keeps
    an archive and those bytes are the only way back if a parse turns out to have been wrong.
    It was gitignored, so the cron wrote it into a container that gets reclaimed, and every
    day's archive was being lost silently while ownership.yaml governed it as append-only and
    the collector's comments explained why keeping it forever was the entire point.

    Nothing threw. Nothing would ever have thrown. Three parts of the repo disagreed about
    whether a file mattered, and the one that won was a line in .gitignore written weeks
    earlier under a different assumption.

    The general form: a path an actor OWNS and may never rewrite is a path this project has
    decided is durable. Durable and ignored is a contradiction, and it is the kind that only
    shows up when somebody goes looking.
    """
    r = Result("archive")
    import subprocess
    try:
        import yaml
        rules = yaml.safe_load((root / "ownership.yaml").read_text(encoding="utf-8"))["rules"]
    except Exception as exc:                                       # noqa: BLE001
        r.skip(f"no ownership map to read ({type(exc).__name__})")
        return r

    durable = [rule["path"] for rule in rules if rule.get("append_only")]
    if not durable:
        r.skip("no append-only paths declared")
        return r

    ignored = []
    for pattern in durable:
        probe = pattern.replace("**", "x").replace("*", "x")
        try:
            out = subprocess.run(["git", "check-ignore", "-q", probe], cwd=root,
                                 capture_output=True)
        except OSError:
            r.skip("git unavailable")
            return r
        if out.returncode == 0:
            ignored.append(pattern)

    for i in ignored:
        r.fail(f"{i} is append-only in ownership.yaml but gitignored: it is being written "
               f"and thrown away")
    if not ignored:
        r.note(f"all {len(durable)} append-only path(s) are committed")
    return r


def check_links(root: Path) -> Result:
    r = Result("links")
    docs = root / "docs"
    if not docs.exists():
        r.skip("site not built yet")
        return r
    href = re.compile(r'(?:href|src)="([^"#?]+)"')
    # Script blocks are stripped first. A URL assembled at runtime, like the ask engine's
    # "../item/" + id + "/", is not a static href: reading it as one reports a broken link to
    # a path that never existed as a string. What those links point at is checked as DATA in
    # site_build's own tests, which verify every id the engine can route to has a page.
    script = re.compile(r"<script\b.*?</script>", re.DOTALL | re.IGNORECASE)
    broken, checked = [], 0
    for page in docs.rglob("*.html"):
        text = script.sub(" ", page.read_text(encoding="utf-8", errors="ignore"))
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


def check_assets(root: Path) -> Result:
    """Every asset the built site REFERENCES is an asset the built site SHIPS.

    The wiring gate above answers "is this script reachable". Nothing answered the same question
    about an asset, and that is where the failure actually landed: `config/brand.yaml` named
    three typefaces, `theme.py` wrote them into every font stack, `assets/fonts/` held all three
    on disk, and no rule served any of them. Every reader got Georgia and system-ui. The config
    and the page disagreed for the whole life of the site, and nothing threw, because a font
    stack that names a family no rule defines renders perfectly well in the fallback.

    So: a stylesheet's `url(...)`, a document's `<link href>` and every `@font-face` source have
    to resolve inside `docs/`. `check_links` reads markup only, which is why a font referenced
    from inside the CSS was invisible to it.
    """
    r = Result("assets")
    docs = root / "docs"
    if not docs.exists():
        r.skip("site not built yet")
        return r

    url_in_css = re.compile(r"url\(\s*[\"']?([^\"')]+)[\"']?\s*\)")
    missing, checked = [], 0
    # ONE pass per stylesheet. Both halves read the identical text, so walking twice bought two
    # file reads and the chance of the two loops drifting onto different file sets.
    for sheet in docs.rglob("*.css"):
        text = sheet.read_text(encoding="utf-8", errors="ignore")

        for target in url_in_css.findall(text):
            if target.startswith(("http://", "https://", "data:", "//")):
                continue
            checked += 1
            dest = (docs if target.startswith("/") else sheet.parent) / target.lstrip("/")
            if not dest.exists():
                missing.append(f"{sheet.relative_to(root)} -> {target}")

        # THE OTHER HALF, and the half that actually bit. An asset can exist and still not be
        # WORN: a served font nothing declares is as useless as a declared font nothing serves.
        # Every family named as the first choice in a font stack must have a rule defining it.
        declared = set(re.findall(r'@font-face\{[^}]*font-family:"([^"]+)"', text))
        for stack in re.findall(r"--(?:display|body|mono):\"([^\"]+)\"", text):
            checked += 1
            if stack not in declared:
                missing.append(f"{sheet.relative_to(root)}: font stack leads with "
                               f"'{stack}' but no @font-face defines it, so every reader "
                               f"silently gets the fallback")

    for m in missing[:12]:
        r.fail(f"unwired asset: {m}")
    if len(missing) > 12:
        r.fail(f"...and {len(missing) - 12} more")
    if not missing:
        r.note(f"{checked} asset reference(s) resolve and every named face is defined")
    return r


def check_refs(root: Path) -> Result:
    """Every repo path named in prose is a repo path that exists.

    `knowledge/shared/TEXAS_DESIGN_DOCTRINE.md` was cited by four files and did not exist. The
    brand config pointed at it twice for the palette rules, the knowledge index listed it, and
    an agent definition told a director to read it before pitching a deck. Nothing threw,
    because a citation is prose: every reader of those files believed the argument had been had
    somewhere, and the agent that was told to read it simply read nothing.

    This is the same failure the wiring gate catches for scripts and the assets gate catches for
    fonts, arriving through the third door. A path written down is a promise, so it is checked.
    """
    r = Result("refs")
    # Only the directories this repo owns, and only real file extensions. Broad path-shaped
    # matching would read a URL fragment or an example in a fenced block as a claim.
    ref = re.compile(r"\b((?:knowledge|prompts|config|ledger|assets|scripts|tests|\.claude)"
                     r"/[A-Za-z0-9_./-]+\.(?:md|ya?ml|json|py|mjs|txt|tsv|sh))\b")
    # PLAN_DOCS describe intent rather than execute it, so a path in one of them is a proposal.
    # The wiring gate already draws this line for scripts, and it is the same line here.
    scan = [p for d in ("knowledge", "prompts", "config", ".claude")
            for p in (root / d).rglob("*") if p.is_file()
            and p.suffix in (".md", ".yaml", ".yml")
            and p.relative_to(root).as_posix() not in PLAN_DOCS]

    missing: dict = {}
    checked = 0
    for src in scan:
        if not src.exists():
            continue
        for target in set(ref.findall(src.read_text(encoding="utf-8", errors="ignore"))):
            # A glob or a placeholder is a description of a family of files, not a citation.
            if (any(ch in target for ch in "*<>{}")
                    or target in REFS_PLANNED or target in REFS_RUNTIME):
                continue
            checked += 1
            if not (root / target).exists():
                missing.setdefault(target, []).append(str(src.relative_to(root)))

    for target, sources in sorted(missing.items())[:12]:
        r.fail(f"{target} is cited by {', '.join(sorted(sources)[:3])} and does not exist")
    if len(missing) > 12:
        r.fail(f"...and {len(missing) - 12} more dangling references")

    # A LOUD PARKING SPACE, NOT A QUIET GRAVE, the same discipline the parity map's deferrals
    # get. A planned path that now exists is an allowlist entry doing nothing, and an allowlist
    # nobody prunes is how an exemption outlives its reason.
    landed = [p for p in REFS_PLANNED if (root / p).exists()]
    for p in landed:
        r.note(f"PLANNED and now built, drop it from REFS_PLANNED: {p}")
    if not missing:
        r.note(f"{checked} cited path(s) all exist, {len(REFS_PLANNED)} planned and "
               f"{len(REFS_RUNTIME)} written at run time")
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
    # HOW A PROMPT ACTUALLY NAMES AN AGENT. The first version of this required the literal
    # word "agent" directly after the name, and matched 1 of the 10 references in the carousel
    # routine: real prompts write "Spawn up to 6 `carousel-scout` agents" and "Spawn 1
    # `carousel-fact-checker` over everything the scouts returned". A gate that sees one
    # reference in ten would pass a prompt naming an agent that does not exist, which is the
    # entire thing it was built to catch.
    #
    # So: inside any sentence that spawns or launches something, every backticked hyphenated
    # identifier is an agent reference. The hyphen requirement keeps file paths and flags out,
    # and the sentence scope keeps unrelated backticks out.
    spawn_line = re.compile(r"[^.\n]*\b(?:spawn|launch)\w*\b[^.\n]*", re.IGNORECASE)
    backticked = re.compile(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`")
    # THE HYPHEN IS REQUIRED, and it is what keeps this from reading English as a name.
    # Agents in this repo are named <lane>-<role>, so "carousel-scout" is a reference and the
    # "more" in "never spawn more agents" is not. Without it that negative sentence, which
    # exists in every routine prompt precisely to forbid extra fan-out, reported a missing
    # agent called "more".
    bare = re.compile(r"(?:spawn|launch)\w*\s+(?:a\s+|an\s+|the\s+)?"
                      r"`?([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`?\s+agent", re.IGNORECASE)
    named: set[str] = set()
    for prompt in prompts.rglob("*.md"):
        text = prompt.read_text(encoding="utf-8", errors="ignore")
        for sentence in spawn_line.findall(text):
            named |= {m.lower() for m in backticked.findall(sentence)}
        named |= {m.lower() for m in bare.findall(text)}
    missing = sorted(named - available)
    for m in missing:
        r.fail(f"prompt names agent '{m}' but .claude/agents/{m}.md does not exist")
    if not named:
        r.skip("no agents referenced by prompts yet")
    elif not missing:
        r.note(f"{len(named)} agent reference(s) all resolve")
    return r


# --------------------------------------------------------------------------- 7 parity
def _yaml_keys(node, prefix: str = "") -> set:
    out = set()
    if isinstance(node, dict):
        for k, v in node.items():
            out.add(f"{prefix}{k}")
            out |= _yaml_keys(v, f"{prefix}{k}.")
    return out


def check_parity(root: Path, refs: dict | None = None) -> Result:
    """Texas config must carry every KEY its Alaska counterpart had. Values differ, shape does
    not. This is what catches a half-ported config that looks finished.

    Divergence is allowed, but only in writing. config/parity_map.yaml records each missing key
    as renamed, dropped or deferred, and this check holds each disposition to its own standard:

      renamed  -> the Texas key it names MUST exist, so a rename can never stand in for a key
                  nobody actually wrote. That loophole would recreate the exact failure the
                  parity gate exists to catch.
      dropped  -> a non-empty reason is required.
      deferred -> a reason AND a blocked_on are required, and every deferral is PRINTED on every
                  run. A parking space nobody sees is a grave.

    A map entry for a key that is present is STALE and fails. Stale exemptions are how a strict
    gate rots into a decorative one: the key comes back, nobody removes the waiver, and the next
    time it goes missing the waiver silently covers it.
    """
    r = Result("parity")
    try:
        import yaml
    except ImportError:
        r.skip("PyYAML unavailable")
        return r

    # Injectable so the self-test can point the gate at a throwaway reference. Without that the
    # only way to exercise parity is against the real Alaska checkout, which is not present on
    # CI and would make this the one gate that never proves it can go red.
    pairs = [(root / rel, Path(ref)) for rel, ref in (refs or REFERENCE_CONFIGS).items()]

    map_path = root / "config" / "parity_map.yaml"
    pmap = {}
    if map_path.exists():
        try:
            pmap = yaml.safe_load(map_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            r.fail(f"config/parity_map.yaml does not parse: {e}")
            return r

    checked, deferrals = 0, []
    for texas, alaska in pairs:
        if not texas.exists():
            continue
        if not alaska.exists():
            r.skip(f"reference {alaska} not on disk")
            continue
        checked += 1
        rel = str(texas.relative_to(root))
        entry = pmap.get(rel, {}) or {}
        renamed = entry.get("renamed", {}) or {}
        dropped = entry.get("dropped", {}) or {}
        deferred = entry.get("deferred", {}) or {}

        tex_keys = _yaml_keys(yaml.safe_load(texas.read_text(encoding="utf-8")))
        missing = _yaml_keys(yaml.safe_load(alaska.read_text(encoding="utf-8"))) - tex_keys

        unexplained = []
        for k in sorted(missing):
            if k in renamed:
                target = renamed[k]
                if target not in tex_keys:
                    r.fail(f"{rel}: '{k}' is mapped to '{target}', which does not exist")
            elif k in dropped:
                if not str((dropped[k] or {}).get("reason", "")).strip():
                    r.fail(f"{rel}: '{k}' is dropped with no reason")
            elif k in deferred:
                d = deferred[k] or {}
                if not str(d.get("reason", "")).strip():
                    r.fail(f"{rel}: '{k}' is deferred with no reason")
                if not str(d.get("blocked_on", "")).strip():
                    r.fail(f"{rel}: '{k}' is deferred with no blocked_on")
                # The full argument lives in the map. The gate line only has to name the key
                # and what unblocks it, or the deferral list becomes the thing nobody reads.
                on = " ".join(str(d.get("blocked_on", "?")).split())
                if len(on) > 58:
                    on = on[:57].rsplit(" ", 1)[0] + "..."
                deferrals.append(f"{k} (blocked on {on})")
            else:
                unexplained.append(k)

        for k in unexplained[:15]:
            r.fail(f"{rel} is missing key '{k}' and config/parity_map.yaml does not explain it")
        if len(unexplained) > 15:
            r.fail(f"...and {len(unexplained) - 15} more unexplained missing keys")

        for group in ("renamed", "dropped", "deferred"):
            for k in sorted((entry.get(group, {}) or {})):
                if k not in missing:
                    r.fail(f"{rel}: parity_map lists '{k}' as {group}, but it is present. "
                           f"Stale exemption, remove it.")

    if checked == 0:
        r.skip("no config to compare yet")
    elif r.status == "PASS":
        r.note(f"{checked} config file(s) at parity, divergences explained")
    for d in sorted(set(deferrals)):
        r.note(f"DEFERRED: {d}")
    return r


CHECKS = {
    "coverage": check_coverage, "residue": check_residue, "wiring": check_wiring,
    "schema": check_schema, "archive": check_archive, "links": check_links,
    "assets": check_assets, "refs": check_refs,
    "agents": check_agents, "parity": check_parity,
}


# --------------------------------------------------------------------------- self-test
def _fail_result() -> "Result":
    r = Result("x")
    r.fail("status was rewritten by a deletion")
    return r


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

        # A SELF-TEST IS NOT WIRING, and this is the case that mattered most. Every gate in
        # this repo is listed in guards.yml as `<gate>.py --self-test`, so while that counted
        # as a reference the orphan check could not fail for a gate no matter what. It would
        # have watched a routine rewrite drop a gate entirely and reported all clear.
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "guards.yml").write_text(
            "      - run: python3 scripts/a.py --self-test\n", encoding="utf-8")
        (root / "prompts" / "r.md").write_text("nothing calls it now\n", encoding="utf-8")
        expect("wiring REFUSES a script whose only mention is a CI self-test",
               check_wiring(root), "FAIL")
        (root / "prompts" / "r.md").write_text(
            "then run scripts/a.py --date <date>\n", encoding="utf-8")
        expect("wiring passes once something actually invokes it", check_wiring(root), "PASS")
        # A real invocation in the WORKFLOW is still wiring. Cron-driven collectors live there
        # and appear in no prompt at all, so this must not become "prompts only".
        (root / "prompts" / "r.md").write_text("nothing calls it now\n", encoding="utf-8")
        (root / ".github" / "workflows" / "guards.yml").write_text(
            "      - run: python3 scripts/a.py --self-test\n"
            "      - run: python3 scripts/a.py --collect\n", encoding="utf-8")
        expect("wiring accepts a real invocation in a workflow", check_wiring(root), "PASS")
        import shutil as _shutil
        _shutil.rmtree(root / ".github")
        (root / "prompts" / "r.md").write_text("then run scripts/a.py\n", encoding="utf-8")

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

        # agents: a named-but-absent agent must be caught. Names are <lane>-<role> here, and
        # the hyphen is what stops the detector reading ordinary English as a name.
        (root / "prompts" / "r.md").write_text(
            "run scripts/a.py then spawn the carousel-scout agent\n", encoding="utf-8")
        expect("agents catches a missing agent file", check_agents(root), "FAIL")
        (root / ".claude" / "agents" / "carousel-scout.md").write_text("x", encoding="utf-8")
        expect("agents passes when the file exists", check_agents(root), "PASS")

        # THE FALSE POSITIVE THAT PROVED THE HYPHEN IS LOAD BEARING. Every routine prompt
        # carries a sentence forbidding extra fan-out, and without the hyphen rule the
        # detector read "never spawn more agents" as a reference to an agent called "more".
        (root / "prompts" / "r.md").write_text(
            "spawn the carousel-scout agent. There is no phase where spawning more agents "
            "is the answer.\n", encoding="utf-8")
        expect("agents does not read plain English as an agent name",
               check_agents(root), "PASS")

        # The phrasing real prompts use, which the first version of this detector missed:
        # a count between the verb and the name, and no literal "agent" after it.
        (root / "prompts" / "r.md").write_text(
            "Spawn up to 6 `carousel-scout` agents, one per beat.\n"
            "Spawn 1 `carousel-scorer` over the finished package.\n", encoding="utf-8")
        expect("agents sees a counted, backticked reference with no trailing noun",
               check_agents(root), "FAIL")   # carousel-scorer.md does not exist in the fixture

        # links: a dangling href must be caught
        docs = root / "docs"
        docs.mkdir()
        (docs / "index.html").write_text('<a href="nope/">x</a>', encoding="utf-8")
        # archive: a durable path that is gitignored is being written and thrown away
        import subprocess as _sp
        _sp.run(["git", "init", "-q"], cwd=root, capture_output=True)
        (root / "ownership.yaml").write_text(
            "rules:\n  - path: 'ledger/keep/**'\n    owner: x\n    append_only: true\n",
            encoding="utf-8")
        (root / ".gitignore").write_text("ledger/keep/\n", encoding="utf-8")
        expect("archive catches a durable path that is gitignored", check_archive(root), "FAIL")
        (root / ".gitignore").write_text("out/\n", encoding="utf-8")
        expect("archive passes when the durable path is committed", check_archive(root), "PASS")

        expect("links catches a dangling href", check_links(root), "FAIL")
        (docs / "nope").mkdir()
        (docs / "nope" / "index.html").write_text("ok", encoding="utf-8")
        expect("links passes when the target exists", check_links(root), "PASS")

        # ASSETS. Both halves of the real failure, reintroduced. A font referenced from inside
        # the CSS is invisible to the link checker, and a font stack naming a family nothing
        # defines renders perfectly well in the fallback, so neither goes red on its own.
        css = docs / "site.css"
        css.write_text('@font-face{font-family:"Manrope";src:url("fonts/manrope.woff2")}'
                       ':root{--body:"Manrope",system-ui}', encoding="utf-8")
        expect("assets catches a font that is referenced but not served",
               check_assets(root), "FAIL")
        (docs / "fonts").mkdir()
        (docs / "fonts" / "manrope.woff2").write_bytes(b"stub")
        expect("assets passes once the file is actually there", check_assets(root), "PASS")
        css.write_text('@font-face{font-family:"Manrope";src:url("fonts/manrope.woff2")}'
                       ':root{--body:"Manrope",system-ui;--display:"Fraunces",Georgia}',
                       encoding="utf-8")
        expect("assets catches a face that is named but never defined",
               check_assets(root), "FAIL")

        # REFS. A cited path that does not exist. This is how a doctrine file can be pointed
        # at by four places and never written: prose does not throw.
        (root / "knowledge").mkdir(parents=True, exist_ok=True)
        (root / "knowledge" / "INDEX.md").write_text(
            "See knowledge/shared/TEXAS_DESIGN_DOCTRINE.md before drawing.\n", encoding="utf-8")
        expect("refs catches a cited file that does not exist", check_refs(root), "FAIL")
        (root / "knowledge" / "shared").mkdir(parents=True, exist_ok=True)
        (root / "knowledge" / "shared" / "TEXAS_DESIGN_DOCTRINE.md").write_text(
            "the doctrine\n", encoding="utf-8")
        expect("refs passes once it is written", check_refs(root), "PASS")
        (root / "knowledge" / "INDEX.md").write_text(
            "Decks live at knowledge/carousel/*.md\n", encoding="utf-8")
        expect("refs does not read a glob as a citation", check_refs(root), "PASS")

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

        # STATUS DRIFT. The manifest is the answer to "is the port done", and its status column
        # was kept by hand, so 31 rows sat at TODO with the file already on disk, all ten
        # carousel agents among them. Coverage read 10 percent against a real 17 and never
        # failed, because it only noted. A tracking system that drifts from the tree is a
        # confident wrong answer, which is worse than no answer.
        (root / "ledger" / "ported.json").write_text("{}", encoding="utf-8")
        man.write_text(head + "\n" + "\t".join(
            ["r", "p", "1", "1", "0", "PORT_VERBATIM", "ledger/ported.json", "TODO", ""])
            + "\n", encoding="utf-8")
        expect("coverage catches a row marked TODO whose target exists",
               check_coverage(root), "FAIL")
        assert reconcile(root) == 0
        expect("...and reconcile writes the truth back", check_coverage(root), "PASS")
        # Only in the safe direction: a missing file must NOT quietly un-do a DONE row, because
        # that would let a deletion rewrite the plan.
        (root / "ledger" / "ported.json").unlink()
        assert reconcile(root) == 0
        rows_after = read_manifest(root / "PORT_MANIFEST.tsv")
        expect("...and a deletion does not rewrite the plan",
               Result("x") if rows_after[0]["status"] == "DONE" else _fail_result(), "PASS")

        # parity: every disposition in the map has to be held to its own standard, and an
        # undeclared missing key has to fail. Run against a throwaway reference config.
        cfg = root / "config"
        cfg.mkdir()
        ref = root / "_ref.yaml"
        ref.write_text("a:\n  keep: 1\n  gone: 2\n", encoding="utf-8")
        refs = {"config/brand.yaml": str(ref)}
        tex, pmap = cfg / "brand.yaml", cfg / "parity_map.yaml"

        tex.write_text("a:\n  keep: 1\n  gone: 2\n", encoding="utf-8")
        expect("parity passes an exact key match", check_parity(root, refs), "PASS")

        tex.write_text("a:\n  keep: 1\n", encoding="utf-8")
        expect("parity catches an undeclared missing key", check_parity(root, refs), "FAIL")

        pmap.write_text(
            'config/brand.yaml:\n  renamed:\n    a.gone: a.nowhere\n', encoding="utf-8")
        expect("parity catches a rename to a key that does not exist",
               check_parity(root, refs), "FAIL")

        tex.write_text("a:\n  keep: 1\n  renamed_to: 2\n", encoding="utf-8")
        pmap.write_text(
            'config/brand.yaml:\n  renamed:\n    a.gone: a.renamed_to\n', encoding="utf-8")
        expect("parity passes a rename whose target exists", check_parity(root, refs), "PASS")

        pmap.write_text(
            'config/brand.yaml:\n  dropped:\n    a.gone:\n      reason: ""\n', encoding="utf-8")
        expect("parity catches a drop with an empty reason", check_parity(root, refs), "FAIL")

        pmap.write_text(
            'config/brand.yaml:\n  dropped:\n    a.gone:\n      reason: "not a Texas concept"\n',
            encoding="utf-8")
        expect("parity passes a reasoned drop", check_parity(root, refs), "PASS")

        pmap.write_text('config/brand.yaml:\n  deferred:\n    a.gone:\n'
                        '      reason: "must be measured first"\n', encoding="utf-8")
        expect("parity catches a deferral with no blocked_on", check_parity(root, refs), "FAIL")

        pmap.write_text('config/brand.yaml:\n  deferred:\n    a.gone:\n'
                        '      reason: "must be measured first"\n'
                        '      blocked_on: "Wave 6"\n', encoding="utf-8")
        expect("parity passes a fully argued deferral", check_parity(root, refs), "PASS")

        tex.write_text("a:\n  keep: 1\n  gone: 2\n  renamed_to: 3\n", encoding="utf-8")
        expect("parity catches a stale exemption for a key that came back",
               check_parity(root, refs), "FAIL")

    if failures:
        print(f"\nport_audit self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nport_audit self-test: all passed (every gate can go red)")
    return 0



def reconcile(root: Path) -> int:
    """Write the manifest's status column back from what is actually on disk.

    ONLY IN THE SAFE DIRECTION. TODO becomes DONE where the target exists, and nothing else moves.
    Flipping DONE back to TODO because a file is missing would let a deletion quietly rewrite the
    plan, and the plan is the thing that remembers what was supposed to happen.
    """
    import csv                                                      # noqa: PLC0415
    mpath = root / "PORT_MANIFEST.tsv"
    rows = read_manifest(mpath)
    if not rows:
        print("port audit: no manifest to reconcile", file=sys.stderr)
        return 2
    fields = list(rows[0].keys())
    changed = 0
    for x in rows:
        if x["status"] == "TODO" and x["target_path"] and (root / x["target_path"]).exists():
            x["status"] = "DONE"
            changed += 1
    if changed:
        with mpath.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields, delimiter="\t", lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    print(f"port audit: reconciled {changed} row(s) from the tree")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(REPO_ROOT))
    ap.add_argument("--only", nargs="*", choices=sorted(CHECKS), help="run only these checks")
    ap.add_argument("--summary", action="store_true", help="coverage progress only")
    ap.add_argument("--reconcile", action="store_true",
                    help="write status back from the tree: TODO becomes DONE where the target "
                         "exists. The manifest is bookkeeping, and bookkeeping that has to be "
                         "kept by hand is bookkeeping that drifts.")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    root = Path(args.root)

    if args.reconcile:
        return reconcile(root)
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
