#!/usr/bin/env python3
"""gen_port_manifest.py — enumerate every file in the Alaska machines and route it.

WHY THIS EXISTS
The last attempt at this port moved files across and forgot to wire them up. Prose checklists
do not catch that, because a checklist is written by the same context that then loses it. So
the port plan is generated MECHANICALLY from the source repos, one row per real file, and the
audit that reads it fails on any row still unresolved.

The important property is that a file we have not thought about yet routes to UNROUTED, which
port_audit.py treats as a failure. Forgetting is loud instead of silent.

    gen_port_manifest.py --out PORT_MANIFEST.tsv
    gen_port_manifest.py --out PORT_MANIFEST.tsv --refresh   # keep status of existing rows

COLUMNS
    source_repo  source_path  bytes  lines  ak_hits  disposition  target_path  status  reason

DISPOSITIONS
    PORT_VERBATIM   copy across, no Alaska content to change
    PORT_RETHEMED   port the structure, rewrite the Texas-specific content
    REBUILD         Texas needs this concept but the file is written fresh
    DROP            deliberately not ported; a reason is REQUIRED
    UNROUTED        nobody has decided yet. port_audit fails on this.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

SOURCES = {
    "alaskaaicarousels": Path("/home/user/alaskaaicarousels"),
    "alaska-ai-weekly": Path("/home/user/alaska-ai-weekly"),
    "alaska-ai-scanner": Path("/workspace/alaska-ai-scanner"),
}

# Alaska-ness detector. Counting these is how a file's disposition gets proposed: a script
# with zero hits is almost always pure machinery that ports untouched, and one with hundreds
# is a rewrite wearing a familiar filename.
AK_TERMS = re.compile(
    r"alaska|alaskan|anchorage|fairbanks|juneau|cook\s*inlet|railbelt|kenai|cingsa|enstar|"
    r"chugach|gvea|iditarod|permafrost|aurora|polaris|denali|nenana|utqiagvik|sitka|bethel|"
    r"kodiak|ancsa|tundra|glacier|salmon|moose|caribou|beluga|ptarmigan|forget.me.not|"
    r"north\s*slope|arctic|\bak\b|akleg|aidea|\brca\b|taps|borough",
    re.IGNORECASE,
)

# Paths never worth a row. Build debris, third-party trees, and the shipped-artifact
# archives, which are Alaska's published history and can only be its own.
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".remotion", ".venv-voice", "out",
    "runs", "archive", "docs/awesomeproposal",
}
SKIP_SUFFIXES = {".pyc", ".pyo", ".webp", ".mp4", ".wav", ".woff2", ".DS_Store"}
SKIP_NAMES = {".gitkeep", ".DS_Store"}

# Explicit routing. This table IS the port plan; everything not named here lands UNROUTED and
# fails the audit, which is the point.
ROUTES: list[tuple[str, str, str, str, str]] = [
    # (repo, path-regex, disposition, target-template, reason)

    # ---- carousels: generated output and Alaska's own memory ----
    ("alaskaaicarousels", r"^docs/", "DROP", "", "generated site output; Texas regenerates from its own ledgers"),
    ("alaskaaicarousels", r"^ledger/", "REBUILD", "ledger/", "Alaska's memory would poison Texas dedupe and divergence gates"),
    ("alaskaaicarousels", r"^assets/geo/", "REBUILD", "assets/geo/", "Alaska geodata; Texas needs its own counties, zones and gazetteer"),
    ("alaskaaicarousels", r"^assets/fonts/", "PORT_VERBATIM", "assets/fonts/", ""),
    ("alaskaaicarousels", r"^assets/js/akgeo\.js$", "PORT_RETHEMED", "assets/js/txgeo.js", "encodes the Alaska conic fit; Texas needs its own projection recipe"),
    ("alaskaaicarousels", r"^assets/js/", "PORT_VERBATIM", "assets/js/", ""),
    ("alaskaaicarousels", r"^examples/", "REBUILD", "examples/", "engine-proof decks are written fresh against Texas art"),
    ("alaskaaicarousels", r"^research/broadband/", "DROP", "", "Alaska USAC data; a Texas analogue is a later project, not this port"),
    ("alaskaaicarousels", r"^vendor/scanner/", "REBUILD", "vendor/scanner/", "vendored contract regenerates from TexasAIScanner"),
    ("alaskaaicarousels", r"^supabase/", "PORT_RETHEMED", "supabase/", ""),
    ("alaskaaicarousels", r"^workers/ask/", "PORT_RETHEMED", "workers/ask/", ""),
    ("alaskaaicarousels", r"^tests/", "PORT_RETHEMED", "tests/", ""),
    ("alaskaaicarousels", r"^knowledge/FIELD_NOTES\.md$", "REBUILD", "knowledge/carousel/FIELD_NOTES.md", "living run-retro log; Texas starts empty"),
    ("alaskaaicarousels", r"^knowledge/", "PORT_RETHEMED", "knowledge/carousel/", ""),
    ("alaskaaicarousels", r"^config/gaswatch", "REBUILD", "config/gridwatch/", "Cook Inlet gas model has no Texas analogue; ERCOT publishes its own forecast"),
    ("alaskaaicarousels", r"^config/", "PORT_RETHEMED", "config/", ""),
    ("alaskaaicarousels", r"^prompts/routine_instructions\.md$", "PORT_RETHEMED", "prompts/daily_routine.md", ""),
    ("alaskaaicarousels", r"^prompts/ROUTINE_PROMPT\.txt$", "PORT_RETHEMED", "prompts/CAROUSEL_TRIGGER.txt", ""),
    ("alaskaaicarousels", r"^prompts/ASK_ROUTINE\.md$", "PORT_RETHEMED", "prompts/ask_routine.md", ""),
    ("alaskaaicarousels", r"^\.claude/agents/", "PORT_RETHEMED", ".claude/agents/carousel-", "namespaced: both Alaska repos ship a scorer and a flow-critic"),
    ("alaskaaicarousels", r"^\.claude/skills/carousel-engine/", "PORT_RETHEMED", ".claude/skills/carousel-engine/", ""),
    ("alaskaaicarousels", r"^\.github/workflows/gaswatch", "REBUILD", ".github/workflows/", "becomes the grid watch workflow"),
    ("alaskaaicarousels", r"^\.github/workflows/", "PORT_RETHEMED", ".github/workflows/", ""),
    ("alaskaaicarousels", r"^(README|CLAUDE)\.md$", "REBUILD", "", "written fresh for the Texas repo topology"),
    ("alaskaaicarousels", r"^(LICENSE|\.gitignore)$", "PORT_VERBATIM", "", ""),

    # ---- carousels scripts, namespaced by owning actor ----
    ("alaskaaicarousels", r"^scripts/gaswatch_", "REBUILD", "scripts/gridwatch/", "ERCOT, not Cook Inlet: different sources, different physics"),
    ("alaskaaicarousels", r"^scripts/(site_build|site_fresh_check|feeds_build|docket_build|docket_dates_check|docket_staleness|docket_alerts|ask_answers|ask_corpus|indexnow|read_stats|fetch_map_layers|scanner_sync_check)\.py$",
     "PORT_RETHEMED", "scripts/site/", ""),
    ("alaskaaicarousels", r"^scripts/(caption_check|gate_status|aggregate_check|bespoke_check|copy_sync_check|dossier_check|claims_check|dedupe_check|parsers_check|trend_check|craft_corpus|gmail_draft|ship_images|shrink_pdfs|prune_runs)\.py$",
     "PORT_RETHEMED", "scripts/carousel/", ""),
    ("alaskaaicarousels", r"^scripts/style_lint\.py$", "PORT_RETHEMED", "scripts/shared/", ""),

    # ---- weekly: the video machine, which lands in TexasAIDispatch ----
    ("alaska-ai-weekly", r"^\.claude/skills/alaska-dispatch/", "DROP", "", "retired engine, explicitly, at dispatch_routine.md:530"),
    ("alaska-ai-weekly", r"^\.claude/skills/alaska-ai-brief/", "PORT_RETHEMED", "TexasAIDispatch:.claude/skills/texas-brief/", ""),
    ("alaska-ai-weekly", r"^\.claude/skills/deep-research-ak/", "REBUILD", "TexasAIDispatch:.claude/skills/deep-research-tx/", "100 percent Alaska search vocabulary"),
    ("alaska-ai-weekly", r"^prompts/dispatch_routine\.md$", "PORT_RETHEMED", "TexasAIDispatch:prompts/dispatch_routine.md", ""),
    ("alaska-ai-weekly", r"^prompts/routine_instructions\.md$", "DROP", "", "stale legacy prompt for the retired 3D engine, not the Facebook routine"),
    ("alaska-ai-weekly", r"^docs/ROUTINE_SPEC\.md$", "DROP", "", "superseded generation of the master prompt; history only"),
    ("alaska-ai-weekly", r"^docs/craft/DIMENSIONAL_CRAFT\.md$", "DROP", "", "doctrine for the retired raymarcher"),
    ("alaska-ai-weekly", r"^docs/craft/(ALASKA_NOSTALGIA|ANCHORAGE_LANDMARKS)\.md$", "REBUILD", "TexasAIDispatch:knowledge/video/", "the two files that are purely local flavor; Texas writes its own"),
    ("alaska-ai-weekly", r"^docs/craft/research/", "PORT_VERBATIM", "TexasAIDispatch:knowledge/video/research/", "raw craft dossiers, state-agnostic"),
    ("alaska-ai-weekly", r"^docs/craft/", "PORT_RETHEMED", "TexasAIDispatch:knowledge/video/", ""),
    ("alaska-ai-weekly", r"^docs/RUN_UPGRADES\.md$", "REBUILD", "TexasAIDispatch:docs/RUN_UPGRADES.md", "Alaska's run history; Texas starts empty"),
    ("alaska-ai-weekly", r"^docs/", "PORT_RETHEMED", "TexasAIDispatch:knowledge/video/", ""),
    ("alaska-ai-weekly", r"^video-engine/src/lib/(biomes|fauna|vehicles|underice|firecraft)\.tsx$",
     "REBUILD", "TexasAIDispatch:video-engine/src/lib/", "the Alaska-coded art; Texas needs its own species, land and machines"),
    ("alaska-ai-weekly", r"^video-engine/src/lib/(Character|kit|materials)\.tsx$",
     "PORT_RETHEMED", "TexasAIDispatch:video-engine/src/lib/", "engine is sound; the outfit, silhouette and substance tables are Alaska"),
    ("alaska-ai-weekly", r"^video-engine/src/lib/", "PORT_VERBATIM", "TexasAIDispatch:video-engine/src/lib/", ""),
    ("alaska-ai-weekly", r"^video-engine/src/(Ep\d+|Episode|Nenana3D|Standoff|IGSHook|UnderIceLook)\.tsx$",
     "DROP", "", "per-story compositions; every Dispatch is a new film, never a re-skin"),
    ("alaska-ai-weekly", r"^video-engine/src/\w*Showcase\w*\.tsx$", "REBUILD", "TexasAIDispatch:video-engine/src/", "look-dev sheets get rebuilt against Texas assets"),
    ("alaska-ai-weekly", r"^video-engine/src/", "PORT_RETHEMED", "TexasAIDispatch:video-engine/src/", ""),
    ("alaska-ai-weekly", r"^video-engine/", "PORT_VERBATIM", "TexasAIDispatch:video-engine/", ""),
    ("alaska-ai-weekly", r"^config/(state|eval_ledger|owner_release)\.\w+$", "REBUILD", "TexasAIDispatch:config/", "Alaska's ledger memory; starting non-empty breaks the divergence gates"),
    ("alaska-ai-weekly", r"^config/", "PORT_RETHEMED", "TexasAIDispatch:config/", ""),
    ("alaska-ai-weekly", r"^assets/sfx/", "PORT_VERBATIM", "TexasAIDispatch:assets/sfx/", "original synthesis and CC0, fully state-agnostic"),
    ("alaska-ai-weekly", r"^assets/voice/", "REBUILD", "TexasAIDispatch:assets/voice/", "Texas gets its own narrator persona"),
    ("alaska-ai-weekly", r"^examples/", "REBUILD", "TexasAIDispatch:examples/", ""),
    ("alaska-ai-weekly", r"^\.claude/agents/", "PORT_RETHEMED", "TexasAIDispatch:.claude/agents/", ""),
    ("alaska-ai-weekly", r"^\.claude/settings", "REBUILD", "TexasAIDispatch:.claude/", ""),
    ("alaska-ai-weekly", r"^\.githooks/", "PORT_VERBATIM", "TexasAIDispatch:.githooks/", "the auto-push guardrail earns its place in every repo"),
    ("alaska-ai-weekly", r"^scripts/", "PORT_RETHEMED", "TexasAIDispatch:scripts/", ""),
    ("alaska-ai-weekly", r"^(README|CLAUDE)\.md$", "REBUILD", "TexasAIDispatch:", ""),
    ("alaska-ai-weekly", r"^(requirements\.txt|\.gitignore|\.mcp\.json)$", "PORT_VERBATIM", "TexasAIDispatch:", ""),

    # ---- scanner, which lands in TexasAIScanner ----
    ("alaska-ai-scanner", r"^web/", "PORT_RETHEMED", "TexasAIScanner:web/", ""),
    # The Deno function layer these targeted was replaced by a Cloudflare Worker on
    # 2026-08-20, so an Alaska edge function ports INTO workers/scan/ rather than beside
    # it. The rule moved with the destination; the five TODO rows it had already routed
    # were repointed in the same commit rather than left describing a directory that no
    # longer exists.
    ("alaska-ai-scanner", r"^supabase/", "PORT_RETHEMED", "TexasAIScanner:workers/scan/",
     "the Deno function layer it targeted was replaced by a Cloudflare Worker on "
     "2026-08-20, so this ports into workers/scan/ rather than beside it"),
    ("alaska-ai-scanner", r"^db/", "PORT_RETHEMED", "TexasAIScanner:db/", ""),
    ("alaska-ai-scanner", r"^prompts/", "PORT_RETHEMED", "TexasAIScanner:prompts/", ""),
    ("alaska-ai-scanner", r"^knowledge/", "PORT_RETHEMED", "TexasAIScanner:knowledge/", ""),
    ("alaska-ai-scanner", r"^scripts/", "PORT_RETHEMED", "TexasAIScanner:scripts/", ""),
    ("alaska-ai-scanner", r"^config/", "PORT_RETHEMED", "TexasAIScanner:config/", ""),
    ("alaska-ai-scanner", r"^\.claude/agents/", "PORT_RETHEMED", "TexasAIScanner:.claude/agents/", ""),
    ("alaska-ai-scanner", r"^docs/", "PORT_RETHEMED", "TexasAIScanner:docs/", ""),
    ("alaska-ai-scanner", r"^samples/", "REBUILD", "TexasAIScanner:samples/", ""),
    ("alaska-ai-scanner", r"^(README|CLAUDE)\.md$", "REBUILD", "TexasAIScanner:", ""),
    ("alaska-ai-scanner", r"^\.gitignore$", "PORT_VERBATIM", "TexasAIScanner:", ""),
]

COMPILED = [(repo, re.compile(rx), disp, target, reason) for repo, rx, disp, target, reason in ROUTES]
HEADER = ["source_repo", "source_path", "bytes", "lines", "ak_hits",
          "disposition", "target_path", "status", "reason"]


def should_skip(rel: Path) -> bool:
    parts = rel.parts
    for i in range(len(parts)):
        if parts[i] in SKIP_DIRS:
            return True
        if "/".join(parts[: i + 1]) in SKIP_DIRS:
            return True
    return rel.suffix in SKIP_SUFFIXES or rel.name in SKIP_NAMES


def measure(path: Path) -> tuple[int, int, int]:
    size = path.stat().st_size
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except (UnicodeDecodeError, OSError):
        return size, 0, 0                       # binary: no lines, no terms
    return size, text.count("\n") + (0 if text.endswith("\n") or not text else 1), \
        len(AK_TERMS.findall(text))


def route(repo: str, rel: str) -> tuple[str, str, str]:
    """Map one source file to its Texas home.

    A target ending in '/', ':' or '-' is a PREFIX and takes the part of the source path the
    rule did not consume, so `supabase/functions/track/index.ts` keeps its shape instead of
    collapsing onto every other `index.ts`. An empty target means the same path in the target
    repo. Anything else is a literal rename.
    """
    for r, rx, disp, target, reason in COMPILED:
        if r != repo:
            continue
        m = rx.search(rel)
        if not m:
            continue
        # What the rule did not match is the structure worth preserving. A rule that matched
        # the whole path leaves nothing, so fall back to the filename.
        remainder = rel[m.end():] if m.start() == 0 else ""
        tail = remainder or Path(rel).name
        if disp == "DROP":
            tgt = ""
        elif target.endswith(("/", ":", "-")):
            tgt = target + tail
        elif target:
            tgt = target
        else:
            tgt = rel
        return disp, tgt, reason
    return "UNROUTED", "", ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(REPO_ROOT / "PORT_MANIFEST.tsv"))
    ap.add_argument("--refresh", action="store_true",
                    help="preserve the status column of rows that already exist")
    args = ap.parse_args()

    out = Path(args.out)
    prior: dict[tuple[str, str], tuple[str, str]] = {}
    if args.refresh and out.exists():
        with out.open(newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh, delimiter="\t"):
                prior[(row["source_repo"], row["source_path"])] = (
                    row.get("status", "TODO"), row.get("reason", ""))

    rows, missing = [], []
    for repo, root in SOURCES.items():
        if not root.exists():
            missing.append(f"{repo} ({root})")
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(root)
            if should_skip(rel):
                continue
            rel_s = rel.as_posix()
            size, lines, hits = measure(path)
            disp, target, reason = route(repo, rel_s)
            status, kept_reason = prior.get((repo, rel_s), ("TODO", ""))
            if disp == "DROP" and status == "TODO":
                status = "DROPPED"
            rows.append([repo, rel_s, size, lines, hits, disp, target, status,
                         kept_reason or reason])

    if missing:
        print(f"gen_port_manifest: source repo(s) not on disk: {', '.join(missing)}",
              file=sys.stderr)

    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, delimiter="\t", lineterminator="\n")
        w.writerow(HEADER)
        w.writerows(rows)

    tally: dict[str, int] = {}
    for r in rows:
        tally[r[5]] = tally.get(r[5], 0) + 1
    print(f"gen_port_manifest: {len(rows)} rows -> {out}")
    for disp in sorted(tally, key=lambda d: -tally[d]):
        print(f"  {disp:<14} {tally[disp]}")
    if tally.get("UNROUTED"):
        print(f"\n  {tally['UNROUTED']} file(s) UNROUTED. port_audit fails until each one is "
              f"either routed in ROUTES or explicitly dropped with a reason.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
