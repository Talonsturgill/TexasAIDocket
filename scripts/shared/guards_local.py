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

DO NOT READ THIS RUNNER'S LOG TO LEARN WHETHER IT PASSED. Ask `--verdict`. See below.

WHAT IT CANNOT SEE. Whether `guards.yml` checks the right things. It is a runner, not a gate.
It also cannot reproduce the runner image: a step needing a browser or a network fetch behaves
here the way this machine behaves, not the way GitHub's does.

    guards_local.py                  every step, in workflow order
    guards_local.py --fast           skip the node suites (they dominate the wall clock)
    guards_local.py --only house     only steps whose name or command matches
    guards_local.py --list           print the steps and run nothing
    guards_local.py --strict         a skipped step is a failure
    guards_local.py --verdict        did the last full run pass, on THIS tree? fail-closed
    guards_local.py --self-test

Exit 0 all green, 1 something failed, 2 the runner could not run.

THE VERDICT FILE, and the run that paid for it (GATE_LESSONS 69, August 27th 2026)
----------------------------------------------------------------------------------
A run piped this script to a file, read the file, saw a wall of `ok` with no `FAIL`, and
recorded a pass. It had read line 84 of an eventual 269. The first `FAIL` was at line 100 and
ten of 120 steps failed. Two CI jobs then went red on a branch the run believed was clean.

**Nothing in the log could have prevented that, and reading it more carefully would not have
helped.** At line 84 the output of a run that will fail at step 100 is byte for byte identical
to the output of a run that will pass. The signal is not in the content. It is in whether the
writer has stopped writing, and a reader looking at content cannot see that.

So the verdict stopped living in the log. `--verdict` reads `out/gates/verdict.json`, which:

  - is DELETED at startup, so while a run is in flight there is no verdict to find and the
    reader fails closed rather than reporting the last run's answer,
  - is written ONCE, at the end, by an atomic rename, so it never exists half-written,
  - records the tree it judged (`HEAD` plus a digest of the working tree), so a verdict earned
    on another branch or before an edit is refused rather than reused,
  - records the invocation, so a `--fast` or `--only` run can never answer for a full one.

The reader exits 0 only when a complete, current, full-coverage, all-passed verdict is there.
Every other state, including every state a half-finished run can be in, exits non-zero and says
which one. A log is advice to a person. This is the answer to a machine.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

try:
    import yaml
except ImportError:                                                       # pragma: no cover
    print("guards_local: PyYAML missing (install requirements.txt)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "guards.yml"

# A GitHub Actions context expression. A step carrying one cannot run verbatim off a runner,
# because the values come from the event payload.
CI_EXPR = re.compile(r"\$\{\{")

# Steps that stand up the runner rather than check the product. Running `actions/checkout`
# locally is meaningless, and a `uses:` step has no shell command at all, so those never appear.
# These are `run:` steps that install things this machine already has.
SETUP_MARKERS = ("pip install", "npm install", "npm ci", "playwright install", "apt-get")

# The node suites under `tests/`. Most drive a real browser, which is why they dominate the
# wall clock and are worth being able to defer while iterating on copy. They are matched as one
# family rather than named individually, because a list of which suite needs a browser would be
# a second source of truth about the tests, and it would be wrong the first time one changed.
NODE_SUITE_MARKERS = ("node tests/",)

# WHERE THE ANSWER LIVES. Under out/, which is gitignored and inside the tree, per the scratch
# rule in CLAUDE.md. Never beside the log, so that "the log" and "the verdict" cannot be
# confused for one another by a reader in a hurry.
VERDICT = REPO_ROOT / "out" / "gates" / "verdict.json"
VERDICT_VERSION = 1


def _tree_state() -> dict:
    """What tree this verdict is about, so a stale one cannot be spent on a changed tree.

    HEAD alone is not enough and that is not hypothetical. The run this mechanism comes from
    ran the suite on one branch, switched branches, and still had the first branch's log on
    disk under a name that said nothing about either. `git status --porcelain` folded in
    catches the other half, an edit made after the suite ran, which is the more common way a
    verdict goes stale on one branch.

    A checkout with no git at all returns nulls and `--verdict` then refuses, because a
    verdict that cannot say what it judged is not a verdict.
    """
    def git(*a: str) -> str | None:
        try:
            r = subprocess.run(("git", *a), cwd=REPO_ROOT, capture_output=True,
                               text=True, timeout=30)
        except (OSError, subprocess.SubprocessError):
            return None
        return r.stdout if r.returncode == 0 else None

    head = git("rev-parse", "HEAD")
    # --porcelain rather than a diff: it names untracked files too, and a new file is exactly
    # the kind of change that turns a green suite red.
    dirty = git("status", "--porcelain")
    if head is None or dirty is None:
        return {"head": None, "tree": None}
    return {"head": head.strip(),
            "tree": hashlib.sha256(dirty.encode("utf-8")).hexdigest()[:16]}


def _clear_verdict() -> None:
    """FAIL CLOSED WHILE RUNNING. Called before the first step, so the window in which a
    reader could find a stale answer is closed before any new work begins."""
    try:
        VERDICT.unlink()
    except FileNotFoundError:
        pass
    except OSError:
        pass


def _write_verdict(payload: dict) -> None:
    """One atomic rename. The file is complete the instant it is visible, or it is absent."""
    try:
        VERDICT.parent.mkdir(parents=True, exist_ok=True)
        tmp = VERDICT.with_suffix(".json.partial")
        tmp.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
        os.replace(tmp, VERDICT)
    except OSError as exc:                                                # pragma: no cover
        print(f"guards_local: could not write the verdict ({exc}). The run's result is in the "
              f"exit code above and `--verdict` will refuse.", file=sys.stderr)


def read_verdict() -> int:
    """`--verdict`. Exit 0 only for a complete, current, full-coverage, all-passed run.

    Every branch below is a REFUSAL with a reason. There is deliberately no output that a
    caller could mistake for a pass, and no path that returns 0 on a missing or partial file.
    """
    if not VERDICT.exists():
        print("guards_local: NO VERDICT. The suite has not finished on this tree.\n"
              "  Either it never ran, or it is running right now, or it died part way.\n"
              "  This is not a pass. Run `python3 scripts/shared/guards_local.py` and wait "
              "for it to exit.", file=sys.stderr)
        return 2
    try:
        v = json.loads(VERDICT.read_text("utf-8"))
    except (OSError, ValueError) as exc:
        print(f"guards_local: the verdict is unreadable ({exc}). Refusing.", file=sys.stderr)
        return 2

    if v.get("version") != VERDICT_VERSION:
        print(f"guards_local: the verdict was written by another version of this runner "
              f"({v.get('version')!r}). Refusing. Re-run the suite.", file=sys.stderr)
        return 2

    now, was = _tree_state(), v.get("state") or {}
    if now["head"] is None:
        print("guards_local: cannot read this tree's git state, so a verdict cannot be "
              "matched to it. Refusing.", file=sys.stderr)
        return 2
    if now != was:
        what = ("a different commit" if now["head"] != was.get("head")
                else "edits made since the suite ran")
        print(f"guards_local: the verdict is STALE. It judged {what}.\n"
              f"  verdict: {was.get('head', '?')[:12]} tree {was.get('tree')}\n"
              f"  now:     {now['head'][:12]} tree {now['tree']}\n"
              f"  A suite that passed on other bytes says nothing about these. Re-run it.",
              file=sys.stderr)
        return 2

    inv = v.get("invocation") or {}
    if inv.get("fast") or inv.get("only"):
        narrow = "--fast" if inv.get("fast") else f"--only {inv['only']}"
        print(f"guards_local: the verdict covers a NARROWED run ({narrow}), so it cannot "
              f"answer for the whole suite. Re-run without it.", file=sys.stderr)
        return 2

    if v.get("exit") != 0:
        names = v.get("failed") or []
        print(f"guards_local: the last full run FAILED, {len(names)} step(s).", file=sys.stderr)
        for nm in names:
            print(f"  FAIL  {nm}", file=sys.stderr)
        return 1

    print(f"guards_local: verdict GREEN. {v.get('passed')} step(s) passed"
          + (f", {len(v.get('skipped') or [])} skipped" if v.get("skipped") else "")
          + f", on {now['head'][:12]}.")
    return 0


class Step:
    def __init__(self, name: str, run: str, env: dict | None = None):
        self.name = name
        self.run = run
        # THE STEP'S `env:` BLOCK, AND WHY THIS RUNNER HAS TO READ IT.
        #
        # A step's CI context can reach bash by two routes, and until 2026-08-20 this file knew
        # only one. `${{ }}` interpolated straight into `run:` is the route it watched for. The
        # other is `env:`, where the expression sits beside the script rather than inside it.
        #
        # On 2026-08-19 the Ownership step moved its branch name from `run:` to `env:`, because
        # a branch name is attacker controlled and interpolating one into a shell is a command
        # injection. That fix was right. Its side effect was that this runner stopped seeing any
        # `${{ }}` in the step at all, classified a CI-only step as an ordinary local check, and
        # ran it with `BRANCH_NAME` unset. It failed on every clean checkout from that day on.
        #
        # A `guards_local` that is red on a clean checkout is worse than one that is missing.
        # The whole point of it is that a person runs it before pushing and believes the answer,
        # and a check that is always red teaches them to stop reading it. Same shape as the
        # faults GATE_LESSONS collects: a CONSUMER reading only half of what the PRODUCER writes.
        self.env = env or {}

    @property
    def needs_ci(self) -> bool:
        """True if anything the step depends on comes from the event payload.

        Both routes count. The `env:` values are joined and searched with the same pattern,
        because an expression is CI-only wherever it is written.
        """
        haystack = self.run + "\n" + "\n".join(
            f"{k}={v}" for k, v in self.env.items()
        )
        return bool(CI_EXPR.search(haystack))

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
            # `env:` comes along because a CI expression can live there instead of in `run:`.
            # See Step.__init__ for the run this cost.
            env = step.get("env") or {}
            if not isinstance(env, dict):
                env = {}
            found.append(Step(step.get("name") or f"{job_name} step {i + 1}", run, env))
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
        return base + ". " + NO_LOCAL_MECHANISM
    return base


# THIS IS A FAILURE, NOT A SKIP, AND THE DIFFERENCE COST A WHOLE RUN.
#
# On 2026-08-16 `core.hooksPath` was unset in the working checkout, so `.githooks/pre-commit`
# sat committed and executable and unreferenced. Every commit that run made went in with no
# ownership check on it. This file was the ONLY thing that noticed, and it reported the gap as a
# skipped step, printed `51 step(s) passed`, and exited 0. A run reading the exit code, which
# this repo's own instructions say to do rather than reading the last line, learned nothing.
#
# A skip is what a check looks like when it is not needed. This is a check that CANNOT RUN,
# which is the opposite, and reporting the two the same way is what made a green suite mean
# "the ownership law is not in force".
NO_LOCAL_MECHANISM = (
    "NOT covered here either: core.hooksPath does not point at an executable pre-commit hook "
    "in this checkout, so the ownership law has no local mechanism at all. "
    "Run `git config core.hooksPath .githooks`")


def hook_installed() -> bool:
    """Whether this checkout really has the hooks git would run.

    Both hooks, not just one. `pre-commit` is what refuses an out-of-lane write, and
    `commit-msg` is what stamps the `Actor:` trailer CI reads to judge a commit's lane. A
    checkout with only the first enforces locally and then hands CI commits it cannot judge.
    """
    try:
        out = subprocess.run(["git", "config", "core.hooksPath"], cwd=REPO_ROOT,
                             capture_output=True, text=True)
        path = out.stdout.strip()
    except OSError:
        return False
    root = (REPO_ROOT / path) if path else (REPO_ROOT / ".git" / "hooks")
    return all((root / name).exists() and (root / name).stat().st_mode & 0o111 != 0
               for name in ("pre-commit", "commit-msg"))


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
    ap.add_argument("--verdict", action="store_true",
                    help="did the last FULL run pass on THIS tree? never reads the log")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.verdict:
        return read_verdict()

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

    # THE OLD ANSWER GOES FIRST, before a single step runs. From here until this process
    # writes a new one there is no verdict on disk, so `--verdict` refuses rather than handing
    # back the previous run's result for a tree it no longer describes.
    _clear_verdict()

    failed: list[tuple[Step, str]] = []
    skipped: list[tuple[Step, str]] = []
    ran = 0

    # ONE RUN PER DISTINCT COMMAND, because the workflow is several jobs now.
    #
    # CI splits these across parallel runners, and a runner that needs a browser has to install
    # one whether or not another runner already did. So the browser install step appears in
    # three jobs, correctly, and the pip install in three more. Locally there is one machine and
    # one checkout, and running the identical command a second time proves nothing that the
    # first run did not. It only makes the local check slower than CI, which is the direction
    # that stops people running it.
    #
    # Keyed on the COMMAND rather than the step name, since the same command under two names is
    # still one thing to run, and two different commands sharing a name would both survive.
    seen_cmds: set[str] = set()

    for s in all_steps:
        if args.only and args.only.lower() not in (s.name + s.run).lower():
            continue
        key = s.run.strip()
        if key in seen_cmds:
            continue
        seen_cmds.add(key)
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

    # EVERY EXIT FROM HERE DOWN GOES THROUGH `finish`, so there is no way to leave this
    # function having run the suite and written nothing. A path that returned a code without
    # recording it would leave the last run's verdict deleted and no new one in its place,
    # which `--verdict` reads as "did not finish". That is the safe direction, and it is still
    # worth not having: a green run that reports nothing is a green run nobody can spend.
    def finish(code: int) -> int:
        _write_verdict({
            "version": VERDICT_VERSION,
            "exit": code,
            "state": _tree_state(),
            "invocation": {"fast": bool(args.fast), "only": args.only,
                           "strict": bool(args.strict)},
            "passed": ran,
            "failed": [s.name for s, _ in failed],
            "skipped": [s.name for s, _ in skipped],
        })
        return code

    # A LAW WITH NO MECHANISM IS A FAILURE. See NO_LOCAL_MECHANISM above for the run this cost.
    unenforced = [s for s, why in skipped if NO_LOCAL_MECHANISM in why]
    if unenforced:
        print("guards_local: the ownership law has NO LOCAL MECHANISM in this checkout.",
              file=sys.stderr)
        print("  .githooks/pre-commit and .githooks/commit-msg are committed and executable, "
              "and git is\n  not pointed at them, so every commit here goes in unchecked and "
              "unstamped.\n\n      git config core.hooksPath .githooks\n", file=sys.stderr)
        print("  This is a FAILURE and not a skip. A skip is what a check looks like when it is "
              "not\n  needed. This is a check that cannot run.", file=sys.stderr)
        return finish(1)

    if failed:
        print(f"guards_local: {len(failed)} of {ran} step(s) FAILED", file=sys.stderr)
        return finish(1)
    if args.strict and skipped:
        print(f"guards_local: {ran} passed, but --strict and {len(skipped)} skipped",
              file=sys.stderr)
        return finish(1)
    print(f"guards_local: {ran} step(s) passed"
          + (f", {len(skipped)} skipped" if skipped else "")
          + ". CI runs the skipped ones.")
    return finish(0)


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

    # THE 2026-08-20 DEFECT, REPLAYED IN THE SHAPE IT ACTUALLY SHIPPED IN.
    #
    # The Ownership step's branch name moved out of `run:` and into `env:` on 2026-08-19, to
    # close a command injection. From that push until this fix, `needs_ci` searched only `run:`,
    # found no expression, ran the step locally with BRANCH_NAME unset, and guards_local exited
    # 1 on a clean checkout of main. Nothing in this file's suite could see it, because every
    # case here put the expression in `run:`.
    env_ci = parse("""
jobs:
  g:
    steps:
      - name: Ownership check
        env:
          BRANCH_NAME: ${{ github.head_ref || github.ref_name }}
        run: |
          python3 scripts/shared/ownership_check.py --branch "$BRANCH_NAME"
""")
    ok("an expression in `env:` makes the step CI-only, same as one in `run:`",
       env_ci[0].needs_ci,
       "it would run here with the variable unset and fail on a clean checkout")
    ok("...and the env block is carried onto the step rather than dropped at parse",
       "github.head_ref" in "".join(str(v) for v in env_ci[0].env.values()))
    ok("...while a step with a plain env block is still an ordinary local check",
       not parse("""
jobs:
  g:
    steps:
      - name: Plain
        env:
          SITE: docs
        run: python3 scripts/x.py --self-test
""")[0].needs_ci)

    # AND THE PRODUCT, NOT ONLY THE LOGIC. The case above proves the classifier can tell the
    # two apart. This asserts the REAL workflow's own Ownership step is on the skip side of it,
    # which is the thing that was actually broken. A checker that only tests its own synthetic
    # fixture is the wrong half, which is the lesson in this file's own docstring.
    real = [s for s in steps() if "ownership_check.py --branch" in s.run]
    ok("the real workflow still has an Ownership step to classify", len(real) == 1,
       f"found {len(real)}; if it was renamed or removed, this assertion is stale")
    ok("...and this checkout classifies it as CI-only, so it does not run here",
       all(s.needs_ci for s in real),
       "guards_local would run it with no branch and go red on a clean checkout")

    setup = parse("""
jobs:
  g:
    steps:
      - name: Deps
        run: |
          pip install pyyaml
      - name: Browser suite
        run: |
          npm ci --ignore-scripts --no-audit --no-fund
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
    ok("this checkout really does have the hooks the note claims", hook_installed(),
       "core.hooksPath does not resolve to executable pre-commit AND commit-msg hooks here")

    # THE RED CASE FOR THE FAULT THIS FILE MISSED. On 2026-08-16 the hook was not installed,
    # this file said so in a skip line, and it exited 0 under a passing banner. The assertion
    # is not "the note mentions it" but "a missing mechanism is routed to the FAILURE list",
    # because the note was already correct that day and the exit code was still green.
    ok("a missing local mechanism produces the sentinel the failure path keys on",
       NO_LOCAL_MECHANISM in ci_note(own) or hook_installed(),
       "the note no longer carries the sentinel, so the failure path is unreachable")
    ok("...and the failure path keys on that same sentinel",
       "NO_LOCAL_MECHANISM in why" in Path(__file__).read_text(encoding="utf-8"),
       "the sentinel and the check that reads it have drifted apart")

    # Simulate the 2026-08-16 checkout: hook absent, note produced, and assert the classifier
    # routes it to the failure list rather than the skip list.
    import unittest.mock as _mock
    with _mock.patch(f"{__name__}.hook_installed", return_value=False):
        absent_note = ci_note(own)
    ok("with no hook installed, the note carries the sentinel",
       NO_LOCAL_MECHANISM in absent_note, absent_note)
    ok("...and that note would be classified unenforced, not merely skipped",
       [1 for w in [absent_note] if NO_LOCAL_MECHANISM in w] == [1])
    with _mock.patch(f"{__name__}.hook_installed", return_value=True):
        present_note = ci_note(own)
    ok("...while an installed hook is NOT classified unenforced",
       NO_LOCAL_MECHANISM not in present_note, present_note)

    ok("the real workflow parses to something", len(steps()) > 10, str(len(steps())))
    ok("...and the house style CHECK is one of the steps found, not just its self-test",
       any("house_style_check.py" in s.run and "--self-test" not in s.run for s in steps()),
       "the step that caught the defect this file exists for is missing from the run list")

    # ---------------------------------------------------------- the verdict, fail-closed
    #
    # EVERY CASE BELOW IS A STATE A HALF-FINISHED RUN CAN LEAVE ON DISK, and the assertion is
    # always the same: `--verdict` does NOT say green. The August 27th run had to distinguish
    # "no FAIL yet" from "no FAIL", and could not, because both look identical in a log. These
    # prove that question is now answerable without reading one.
    #
    # The real VERDICT path is swapped for a temp file so a self-test can never eat the answer
    # a suite running in another terminal just earned.
    global VERDICT
    real_verdict = VERDICT
    with tempfile.TemporaryDirectory() as td:
        VERDICT = Path(td) / "verdict.json"
        here = _tree_state()
        green = {"version": VERDICT_VERSION, "exit": 0, "state": here,
                 "invocation": {"fast": False, "only": None, "strict": False},
                 "passed": 120, "failed": [], "skipped": []}

        def verdict_of(payload: dict | None) -> int:
            if payload is None:
                _clear_verdict()
            else:
                _write_verdict(payload)
            return read_verdict()

        ok("a verdict that was never written is not a pass", verdict_of(None) != 0)

        # THE ONE THIS EXISTS FOR. Mid-run there is no file, because the runner deletes it
        # before its first step. The reader cannot be handed a stale green, and it cannot be
        # handed a partial one either, because the write is a rename.
        _write_verdict(green)
        _clear_verdict()
        ok("a run in flight has deleted the old verdict and written no new one",
           verdict_of(None) != 0)

        ok("a complete green verdict on this exact tree passes", verdict_of(green) == 0)

        ok("a verdict recording a failure is not a pass",
           verdict_of({**green, "exit": 1, "failed": ["Site build self-test"]}) != 0)

        # STALENESS, both halves. A suite that passed on other bytes says nothing about these.
        ok("a verdict from another commit is refused",
           verdict_of({**green, "state": {"head": "0" * 40, "tree": here["tree"]}}) != 0)
        ok("a verdict from the same commit with a different working tree is refused",
           verdict_of({**green, "state": {**here, "tree": "deadbeefdeadbeef"}}) != 0)

        # NARROWING. --fast defers the node suites, which is exactly where two of this repo's
        # CI failures have lived. A fast run answering for a full one would reinstate the bug.
        ok("a --fast verdict cannot answer for the whole suite",
           verdict_of({**green, "invocation": {"fast": True, "only": None, "strict": False}}) != 0)
        ok("an --only verdict cannot answer for the whole suite",
           verdict_of({**green, "invocation":
                       {"fast": False, "only": "house", "strict": False}}) != 0)

        ok("a verdict from a future version of this runner is refused",
           verdict_of({**green, "version": VERDICT_VERSION + 1}) != 0)

        # A corrupt or truncated file is the one case where the atomic rename could in theory
        # be defeated, by something outside this script. It still must not read as green.
        VERDICT.write_text('{"version": 1, "exit": 0, "sta', encoding="utf-8")
        ok("a truncated verdict is refused rather than parsed optimistically",
           read_verdict() != 0)
    VERDICT = real_verdict

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
