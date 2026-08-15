#!/usr/bin/env python3
"""guards_local.py — run what CI runs, here, before pushing.

WHY THIS EXISTS

A homepage section shipped with "Scan my business" in it. `house_style_check` refuses first
person in published copy, CI ran it against the built site, and it went red on the first push.

Locally it had been "verified" by running every `--self-test` under `scripts/`, and every one
of them passed. They were the wrong half. **A self-test proves the checker can go red. Only the
checker proves the product is clean**, which is GATE_LESSONS' oldest entry, arrived at again by
the same route, because knowing it and having a way to act on it are different things.

The reason the wrong half got run is worth stating plainly: `guards.yml` is more than forty
steps and nothing could run them. So "run the gates" meant remembering forty commands, and what
a person remembers under time pressure is the shape of the list, not the list.

IT READS THE WORKFLOW. It does not keep its own copy of the step list. A runner with a
hand-maintained list is a second source of truth that goes stale, and a stale runner is worse
than none: it reports green over a step CI added last week. Add a step to `guards.yml` and it
runs here the same day, with no edit to this file.

WHAT IT REFUSES TO DO QUIETLY

  PARSE NOTHING. If the workflow yields zero steps, that is an error and not a clean run. The
  shape of a workflow file is not this project's to control.

  SKIP SILENTLY. Steps carrying a `${{ }}` expression need a CI context that does not exist on
  a laptop. They are reported by name as SKIPPED and counted in the summary, so the count a
  person reads is never mistaken for full coverage. `--strict` makes any skip an exit 1.

  READ THE LAST LINE. Every step is judged by EXIT CODE. This repo has shipped a red gate under
  `tail -1` before, because a report that prints advice on failure and one clean line on success
  looks reassuring either way.

WHAT IT CANNOT SEE. Whether `guards.yml` checks the right things. It is a runner, not a gate.
It also cannot reproduce the runner image: a step needing a browser or a network fetch behaves
here the way this machine behaves, not the way GitHub's does.

    guards_local.py                  every step, in workflow order
    guards_local.py --fast           skip the node suites (they dominate the wall clock)
    guards_local.py --only house     only steps whose name or command matches
    guards_local.py --list           print the steps and run nothing
    guards_local.py --strict         a skipped step is a failure
    guards_local.py --self-test

Exit 0 all green, 1 something failed, 2 the runner could not run.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:                                                       # pragma: no cover
    print("guards_local: PyYAML missing (pip install pyyaml)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "guards.yml"

# A GitHub Actions context expression. A step carrying one cannot run verbatim off a runner,
# because the values come from the event payload.
CI_EXPR = re.compile(r"\$\{\{")

# Steps that stand up the runner rather than check the product. Running `actions/checkout`
# locally is meaningless, and a `uses:` step has no shell command at all, so those never appear.
# These are `run:` steps that install things this machine already has.
SETUP_MARKERS = ("pip install", "npm install", "playwright install", "apt-get")

# The node suites under `tests/`. Most drive a real browser, which is why they dominate the
# wall clock and are worth being able to defer while iterating on copy. They are matched as one
# family rather than named individually, because a list of which suite needs a browser would be
# a second source of truth about the tests, and it would be wrong the first time one changed.
NODE_SUITE_MARKERS = ("node tests/",)


class Step:
    def __init__(self, name: str, run: str):
        self.name = name
        self.run = run

    @property
    def needs_ci(self) -> bool:
        return bool(CI_EXPR.search(self.run))

    @property
    def is_setup(self) -> bool:
        return all(
            any(m in line for m in SETUP_MARKERS)
            for line in self._commands()
        ) and bool(self._commands())

    @property
    def is_node_suite(self) -> bool:
        return any(m in self.run for m in NODE_SUITE_MARKERS)

    def _commands(self) -> list[str]:
        """The non-comment, non-blank lines. Used only for classification, never for running:
        the step is executed as one script so its `||`, heredocs and multi-line pipes survive."""
        out = []
        for line in self.run.splitlines():
            s = line.strip()
            if s and not s.startswith("#"):
                out.append(s)
        return out


def steps(workflow: Path = WORKFLOW) -> list[Step]:
    """Every `run:` step in the workflow, in file order, across all jobs."""
    doc = yaml.safe_load(workflow.read_text(encoding="utf-8"))
    found: list[Step] = []
    for job_name, job in (doc.get("jobs") or {}).items():
        for i, step in enumerate(job.get("steps") or []):
            run = step.get("run")
            if not run:
                continue                       # a `uses:` step: nothing to run here
            found.append(Step(step.get("name") or f"{job_name} step {i + 1}", run))
    return found


def ci_note(step: Step) -> str:
    """Why a CI-only step did not run, and what covers it here instead.

    A skip that says only "cannot run" reads as a hole. Some of these are already covered by
    another mechanism, and a person deciding whether it is safe to push deserves to know which.
    Anything not named here gets the honest default, which IS a hole.
    """
    base = "needs a CI context (a ${{ }} expression), so it can only run on a runner"
    if "ownership_check.py" in step.run:
        # CHECKED, not asserted. "The hook covers it" is only true in a checkout where the hook
        # is actually installed, and a fresh clone does not have one until somebody sets
        # core.hooksPath. Saying it anyway would be a comforting sentence with nothing under it.
        if hook_installed():
            return (base + ". Covered here by the pre-commit hook, which runs the same check "
                    "off .git/ACTOR on every commit")
        return (base + ". NOT covered here either: core.hooksPath does not point at an existing "
                "pre-commit hook in this checkout, so the ownership law has no local mechanism. "
                "Run `git config core.hooksPath .githooks`")
    return base


def hook_installed() -> bool:
    """Whether this checkout really has a pre-commit hook git would run."""
    try:
        out = subprocess.run(["git", "config", "core.hooksPath"], cwd=REPO_ROOT,
                             capture_output=True, text=True)
        path = out.stdout.strip()
    except OSError:
        return False
    root = (REPO_ROOT / path) if path else (REPO_ROOT / ".git" / "hooks")
    hook = root / "pre-commit"
    return hook.exists() and hook.stat().st_mode & 0o111 != 0


def run_step(step: Step) -> tuple[int, str, float]:
    """Execute one step exactly as the workflow shell would, and judge it by exit code."""
    t0 = time.monotonic()
    proc = subprocess.run(["bash", "-e", "-c", step.run], cwd=REPO_ROOT,
                          capture_output=True, text=True)
    return proc.returncode, (proc.stdout + proc.stderr), time.monotonic() - t0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fast", action="store_true", help="skip the node/browser suites")
    ap.add_argument("--only", metavar="TEXT", help="only steps whose name or command matches")
    ap.add_argument("--list", action="store_true", help="print the steps and run nothing")
    ap.add_argument("--strict", action="store_true", help="a skipped step is a failure")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    if not WORKFLOW.exists():
        print(f"guards_local: no workflow at {WORKFLOW}", file=sys.stderr)
        return 2
    try:
        all_steps = steps()
    except (yaml.YAMLError, OSError) as exc:
        print(f"guards_local: cannot read the workflow: {exc}", file=sys.stderr)
        return 2

    # PARSED NOTHING IS AN ERROR. Reporting a clean run over an empty list is the exact
    # failure this file exists to stop, one level up.
    if not all_steps:
        print(f"guards_local: parsed ZERO steps out of {WORKFLOW.name}. Either it has none, "
              f"or this runner is looking for a shape it no longer uses. Both mean a green "
              f"line below would be a lie.", file=sys.stderr)
        return 2

    if args.list:
        for s in all_steps:
            tag = ("setup" if s.is_setup else "ci-only" if s.needs_ci
                   else "node" if s.is_node_suite else "check")
            print(f"  {tag:8}  {s.name}")
        print(f"\n{len(all_steps)} step(s) in {WORKFLOW.name}")
        return 0

    failed: list[tuple[Step, str]] = []
    skipped: list[tuple[Step, str]] = []
    ran = 0

    for s in all_steps:
        if args.only and args.only.lower() not in (s.name + s.run).lower():
            continue
        if s.is_setup:
            skipped.append((s, "sets up the runner, not a check"))
            continue
        if s.needs_ci:
            skipped.append((s, ci_note(s)))
            continue
        if args.fast and s.is_node_suite:
            skipped.append((s, "node suite, deferred by --fast"))
            continue

        rc, out, secs = run_step(s)
        ran += 1
        if rc == 0:
            print(f"  ok   {secs:6.1f}s  {s.name}")
        else:
            print(f"  FAIL {secs:6.1f}s  {s.name}  (exit {rc})")
            failed.append((s, out))

    print()
    for s, out in failed:
        print(f"--- {s.name} " + "-" * max(0, 60 - len(s.name)))
        print("\n".join(out.strip().splitlines()[-25:]))
        print()

    # SKIPS ARE NAMED, never folded into a total. A person reading "41 passed" has to be able
    # to see that four of them never ran.
    if skipped:
        print(f"{len(skipped)} step(s) did NOT run here:")
        for s, why in skipped:
            print(f"  -  {s.name}: {why}")
        print()

    if failed:
        print(f"guards_local: {len(failed)} of {ran} step(s) FAILED", file=sys.stderr)
        return 1
    if args.strict and skipped:
        print(f"guards_local: {ran} passed, but --strict and {len(skipped)} skipped",
              file=sys.stderr)
        return 1
    print(f"guards_local: {ran} step(s) passed"
          + (f", {len(skipped)} skipped" if skipped else "")
          + ". CI runs the skipped ones.")
    return 0


# ---------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    import tempfile

    def parse(text: str) -> list[Step]:
        with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as fh:
            fh.write(text)
        try:
            return steps(Path(fh.name))
        finally:
            Path(fh.name).unlink()

    got = parse("""
on: [push]
jobs:
  guards:
    steps:
      - uses: actions/checkout@v4
      - name: A real check
        run: python3 scripts/x.py --self-test
      - name: A multi line one
        run: |
          # a comment
          python3 scripts/y.py
""")
    ok("a `uses:` step contributes nothing to run", len(got) == 2, str([s.name for s in got]))
    ok("a step keeps its name", got[0].name == "A real check")
    ok("a block step keeps its whole script", "scripts/y.py" in got[1].run)
    ok("a comment is not mistaken for a command", got[1]._commands() == ["python3 scripts/y.py"])

    ci = parse("""
jobs:
  g:
    steps:
      - name: Ownership
        run: |
          BRANCH="${{ github.head_ref }}"
          python3 scripts/shared/ownership_check.py --branch "$BRANCH"
""")
    ok("a step carrying a CI expression is recognised", ci[0].needs_ci)
    ok("...and a plain one is not", not got[0].needs_ci)

    setup = parse("""
jobs:
  g:
    steps:
      - name: Deps
        run: |
          pip install pyyaml
      - name: Browser suite
        run: |
          npm install --no-save --silent playwright
          SITE=docs node tests/responsive.mjs
""")
    ok("a pure install step is classified as setup", setup[0].is_setup)
    ok("a step that installs AND checks is NOT setup", not setup[1].is_setup,
       "it would be skipped and its check would silently never run")
    ok("...and it is recognised as a node suite", setup[1].is_node_suite)

    # THE RUNNER CAN GO RED, on exit code and not on output. Both halves matter: this repo has
    # shipped a red gate read by its last printed line.
    rc, out, _ = run_step(Step("red", "python3 -c \"print('all clean'); raise SystemExit(1)\""))
    ok("a step that prints success and exits 1 is a FAILURE", rc == 1)
    ok("...and its output is captured for the report", "all clean" in out)
    rc, _, _ = run_step(Step("green", "python3 -c \"raise SystemExit(0)\""))
    ok("a step that exits 0 passes", rc == 0)
    rc, _, _ = run_step(Step("half", "false\npython3 -c 'pass'"))
    ok("an early failure inside a block fails the step", rc != 0,
       "bash -e is what stops line one's failure being hidden by line two's success")

    # THE SKIP NOTES. A skip that overstates its coverage is worse than a bare one, because it
    # is the sentence somebody reads instead of running the check.
    own = Step("Ownership check", 'BRANCH="${{ github.head_ref }}"\n'
                                  'python3 scripts/shared/ownership_check.py --branch "$BRANCH"')
    note = ci_note(own)
    ok("the ownership skip names what covers it locally",
       ("pre-commit hook" in note) == hook_installed(),
       "it claims the hook covers this while no hook is installed" if not hook_installed()
       else "the hook is installed and the note does not say so")
    ok("...and a step with no local cover gets the plain reason",
       "pre-commit" not in ci_note(Step("x", 'run: "${{ github.sha }}"')))
    ok("this checkout really does have the hook the note claims", hook_installed(),
       "core.hooksPath does not resolve to an executable pre-commit here")

    ok("the real workflow parses to something", len(steps()) > 10, str(len(steps())))
    ok("...and the house style CHECK is one of the steps found, not just its self-test",
       any("house_style_check.py" in s.run and "--self-test" not in s.run for s in steps()),
       "the step that caught the defect this file exists for is missing from the run list")

    print("\nguards_local self-test: " + ("all passed" if not failures else f"{failures} FAILED"))
    return 0 if not failures else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nguards_local: interrupted", file=sys.stderr)
        sys.exit(2)
    except Exception as exc:                                              # noqa: BLE001
        print(f"guards_local: broke: {exc}", file=sys.stderr)
        sys.exit(2)
