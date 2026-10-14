#!/usr/bin/env python3
"""pages_guards_wait_test.py -- the Pages guard proof waits for a pending result and never for a failed one.

THE DEFECT. pages.yml verify refused immediately when the exact main commit's aggregate `guards` check had
no conclusion yet. The scheduled backstop fires every two hours and full guards take most of an hour,
so it regularly met the current main commit mid run, failed, and left a red `verify` check on a healthy
commit. A red check on that commit is what the shipment contract refuses, and this repo's Actions token can't
rerun it. On 2026-10-14 that blocked the accepted shipment of the October 11th edition until a rerun.

WHAT THESE TESTS RUN. The ACTUAL step text parsed out of .github/workflows/pages.yml, under bash with a fake `gh`
and `git` on PATH, so the workflow and the test can't drift. Nothing here re-types the shell.

  pending -> success      waits, then proceeds. Covers queued, in progress and no check registered yet.
  real failure            a finished guard that did not succeed refuses on the FIRST read, with no sleeping.
  timeout                 a guard that never finishes refuses after the bound, and polls a bounded number of times.
  transient API error     reads as not yet, never as success.
  exact SHA               the query names the commit `git rev-parse HEAD` returned.
  stale dispatch          the unchanged target step still exits green without deploying when main has moved.
  deploy pin              the deploy job still packages the verified SHA.
  mutations               an unbounded loop, a loop that waits on a failure, and the old immediate refusal are
                          each caught by a test that would have passed them.
Run: python3 scripts/shared/pages_guards_wait_test.py
"""
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
PAGES = REPO / ".github" / "workflows" / "pages.yml"
SHA = "0123456789abcdef0123456789abcdef01234567"
WAIT_STEP = "Full guards passed for this exact main commit"
TARGET_STEP = "Select the guarded main commit"


def pages_doc():
    return yaml.safe_load(PAGES.read_text(encoding="utf-8"))


def step(doc, name):
    for item in doc["jobs"]["verify"]["steps"]:
        if item.get("name") == name:
            return item
    raise AssertionError("pages.yml has no step named " + name)


class Harness:
    """Runs one step's shell text with fake gh and git and reports what it did."""

    def __init__(self, script_text, env_extra=None):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.calls = self.root / "gh_calls.log"
        self.queue = self.root / "responses.json"
        self.script = self.root / "step.sh"
        self.script.write_text(script_text)
        self.output = self.root / "github_output"
        self.output.write_text("")
        self.env_extra = env_extra or {}

    def close(self):
        self.tmp.cleanup()

    def install(self, responses, head=SHA):
        """responses is a list of gh behaviours consumed in order, the last one repeating:
        a (status, conclusion) pair, None for a missing check, ("error", stderr_text) for a failing call,
        or ("raw", text) for a successful call that prints something else."""
        self.queue.write_text(json.dumps(responses))
        gh = self.bin / "gh"
        gh.write_text(f"""#!/usr/bin/env python3
import json, sys
log = open({str(self.calls)!r}, "a"); log.write(" ".join(sys.argv[1:]) + "\\n"); log.close()
queue = json.load(open({str(self.queue)!r}))
index = len(open({str(self.calls)!r}).read().splitlines()) - 1
item = queue[min(index, len(queue) - 1)]
if item == "error":
    item = ["error", "gh: HTTP 502 Bad Gateway"]
if item is None:
    print("\\t")
elif item[0] == "error":
    sys.stderr.write(item[1] + "\\n"); sys.exit(1)
elif item[0] == "raw":
    print(item[1])
else:
    print(item[0] + "\\t" + item[1])
""")
        git = self.bin / "git"
        git.write_text(f"#!/bin/sh\nif [ \"$1\" = rev-parse ]; then echo {head}; fi\n")
        for f in (gh, git):
            f.chmod(f.stat().st_mode | stat.S_IEXEC)

    def run(self, wait="2", poll="0.1", **env):
        full = {**os.environ, "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
                "GITHUB_REPOSITORY": "owner/repo", "GITHUB_OUTPUT": str(self.output),
                "GUARDS_WAIT_SECONDS": wait, "GUARDS_POLL_SECONDS": poll, **self.env_extra, **env}
        done = subprocess.run(["bash", "-e", str(self.script)], capture_output=True, text=True, env=full, timeout=60)
        return done, len(self.calls.read_text().splitlines()) if self.calls.exists() else 0


class WaitStep(unittest.TestCase):
    def harness(self, text=None):
        h = Harness(text if text is not None else step(pages_doc(), WAIT_STEP)["run"])
        self.addCleanup(h.close)
        return h

    def test_pending_then_success_waits_and_proceeds(self):
        for label, sequence in (("in progress", [("in_progress", ""), ("in_progress", ""), ("completed", "success")]),
                                ("queued", [("queued", ""), ("completed", "success")]),
                                ("not registered yet", [None, None, ("completed", "success")])):
            h = self.harness(); h.install(sequence)
            done, calls = h.run()
            self.assertEqual(done.returncode, 0, (label, done.stdout, done.stderr))
            self.assertEqual(calls, len(sequence), label)
            self.assertIn("waiting", done.stdout)

    def test_success_on_the_first_read_does_not_wait(self):
        h = self.harness(); h.install([("completed", "success")])
        done, calls = h.run(poll="30")
        self.assertEqual((done.returncode, calls), (0, 1))

    def test_a_real_failure_refuses_at_once_without_waiting(self):
        for conclusion in ("failure", "cancelled", "timed_out", "action_required", "skipped", "neutral", "stale"):
            h = self.harness(); h.install([("completed", conclusion)])
            done, calls = h.run(wait="60", poll="30")      # a wait here would blow the 60 second test timeout
            self.assertEqual(done.returncode, 1, conclusion)
            self.assertEqual(calls, 1, conclusion)
            self.assertIn("refusing to deploy", done.stdout)
            self.assertIn(conclusion, done.stdout)

    def test_a_guard_that_fails_while_we_wait_refuses_on_that_read(self):
        h = self.harness(); h.install([("in_progress", ""), ("completed", "failure"), ("completed", "success")])
        done, calls = h.run()
        self.assertEqual((done.returncode, calls), (1, 2))

    def test_a_guard_that_never_finishes_refuses_after_the_bound(self):
        h = self.harness(); h.install([("in_progress", "")])
        done, calls = h.run(wait="1", poll="0.2")
        self.assertEqual(done.returncode, 1)
        self.assertIn("did not finish within 1 seconds", done.stdout)
        self.assertIn("refusing to deploy", done.stdout)
        self.assertGreaterEqual(calls, 2)
        self.assertLessEqual(calls, 8)               # bounded, not an open ended poll

    def test_a_missing_check_that_never_appears_also_times_out(self):
        h = self.harness(); h.install([None])
        done, calls = h.run(wait="1", poll="0.2")
        self.assertEqual(done.returncode, 1)
        self.assertIn("last status none", done.stdout)

    def test_a_server_error_or_lost_connection_is_retried_then_proceeds(self):
        for label, failure in (("502", ["error", "gh: HTTP 502 Bad Gateway"]),
                               ("503", ["error", "gh: HTTP 503 Service Unavailable"]),
                               ("504", ["error", "gh: HTTP 504 Gateway Timeout"]),
                               ("500", ["error", "gh: HTTP 500 Internal Server Error"]),
                               ("connection reset", ["error", "Get https://api.github.com/x: read tcp: connection reset by peer"]),
                               ("no such host", ["error", "dial tcp: lookup api.github.com: no such host"])):
            h = self.harness(); h.install([failure, failure, ("completed", "success")])
            done, calls = h.run()
            self.assertEqual((done.returncode, calls), (0, 3), (label, done.stdout, done.stderr))
            self.assertIn("transient GitHub API error", done.stdout)

    def test_a_client_error_is_never_read_as_pending_and_refuses_at_once(self):
        for code, text in (("403", "gh: Resource not accessible by integration (HTTP 403)"),
                           ("401", "gh: Bad credentials (HTTP 401)"),
                           ("404", "gh: Not Found (HTTP 404)"),
                           ("422", "gh: Validation Failed (HTTP 422)"),
                           ("429", "gh: HTTP 429 rate limit exceeded")):
            h = self.harness(); h.install([["error", text], ("completed", "success")])
            done, calls = h.run(wait="60", poll="30")      # waiting here would blow the 60 second test timeout
            self.assertEqual(done.returncode, 1, code)
            self.assertEqual(calls, 1, code)
            self.assertIn("could not read the guards result", done.stdout)
            self.assertIn(code, done.stdout)
            self.assertIn("refusing to deploy", done.stdout)

    def test_an_unrecognized_error_refuses_at_once(self):
        for text in ("gh: something nobody planned for", "jq: error: syntax error", "failed to parse response"):
            h = self.harness(); h.install([["error", text], ("completed", "success")])
            done, calls = h.run(wait="60", poll="30")
            self.assertEqual((done.returncode, calls), (1, 1), text)
            self.assertIn("could not read the guards result", done.stdout)

    def test_a_server_error_that_never_clears_refuses_after_a_few_tries(self):
        h = self.harness(); h.install([["error", "gh: HTTP 503 Service Unavailable"]])
        done, calls = h.run(wait="60", poll="0.1", GUARDS_API_RETRIES="4")
        self.assertEqual(done.returncode, 1)
        self.assertEqual(calls, 4)                           # bounded by the retry count, not by the wait
        self.assertIn("could not read the guards result after 4 consecutive transient API errors", done.stdout)

    def test_transient_errors_only_count_in_a_row(self):
        # Alternating errors and pending reads never reach the cap, and the guard still has to finish.
        err = ["error", "gh: HTTP 502 Bad Gateway"]
        h = self.harness(); h.install([err, ("in_progress", ""), err, ("in_progress", ""), err, ("completed", "success")])
        done, calls = h.run(wait="30", poll="0.05", GUARDS_API_RETRIES="2")
        self.assertEqual((done.returncode, calls), (0, 6), done.stdout)

    def test_an_invalid_response_is_not_pending(self):
        for raw in ("garbage", "mystery\tnone", "completed_maybe\t", "\u0000"):
            h = self.harness(); h.install([("raw", raw), ("completed", "success")])
            done, calls = h.run(wait="60", poll="30")
            self.assertEqual((done.returncode, calls), (1, 1), repr(raw))
            self.assertIn("could not read the guards result", done.stdout)

    def test_the_query_names_the_exact_checked_commit(self):
        h = self.harness(); h.install([("completed", "success")], head="f" * 40)
        h.run()
        query = h.calls.read_text()
        self.assertIn("commits/" + "f" * 40 + "/check-runs", query)
        self.assertIn("check_name=guards", query)
        self.assertIn("filter=latest", query)
        self.assertNotIn(SHA, query)

    def test_the_wait_is_declared_bounded_in_the_workflow(self):
        env = step(pages_doc(), WAIT_STEP)["env"]
        self.assertTrue(0 < int(env["GUARDS_WAIT_SECONDS"]) <= 7200)
        self.assertGreaterEqual(float(env["GUARDS_POLL_SECONDS"]), 1)
        self.assertTrue(1 <= int(env["GUARDS_API_RETRIES"]) <= 10)
        timeout = pages_doc()["jobs"]["verify"].get("timeout-minutes")
        self.assertIsNotNone(timeout)
        self.assertGreater(timeout * 60, int(env["GUARDS_WAIT_SECONDS"]))

    def test_mutations_are_caught(self):
        real = step(pages_doc(), WAIT_STEP)["run"]
        # 1 The old behaviour: refuse on any non success, so a pending guard is a red check again.
        old = ('SHA=$(git rev-parse HEAD)\n'
               'conclusion=$(gh api "repos/${GITHUB_REPOSITORY}/commits/${SHA}/check-runs?check_name=guards&filter=latest&per_page=1" '
               "--jq '.check_runs[0].conclusion // \"\"')\n"
               'if [ "$conclusion" != "success" ]; then echo "::error::refusing to deploy"; exit 1; fi\n')
        h = self.harness(old); h.install([("in_progress", ""), ("completed", "success")])
        self.assertEqual(h.run()[0].returncode, 1)           # the real step passes this same scenario
        h = self.harness(); h.install([("in_progress", ""), ("completed", "success")])
        self.assertEqual(h.run()[0].returncode, 0)
        # 1b The first cut collapsed every API error into pending. A 403 would then wait out the whole bound.
        collapsed = real.replace('exit 1\n              fi\n            fi\n            status=', 'exit 1\n              fi\n            fi\n            status=')
        old_read = ('SHA=$(git rev-parse HEAD)\nstarted=$SECONDS\nwhile true; do\n'
                    '  row=$(gh api "repos/${GITHUB_REPOSITORY}/commits/${SHA}/check-runs?check_name=guards&filter=latest&per_page=1" '
                    "--jq '[(.check_runs[0].status // \"\"), (.check_runs[0].conclusion // \"\")] | @tsv' 2>/dev/null) || row=\"\"\n"
                    '  status=$(printf \'%s\' "$row" | cut -f1); conclusion=$(printf \'%s\' "$row" | cut -f2)\n'
                    '  if [ -n "$conclusion" ] && [ "$conclusion" != "success" ]; then echo "::error::guards finished ${conclusion}; refusing to deploy"; exit 1; fi\n'
                    '  [ "$conclusion" = "success" ] && break\n'
                    '  if [ $((SECONDS - started)) -ge "${GUARDS_WAIT_SECONDS}" ]; then echo "did not finish; refusing to deploy"; exit 1; fi\n'
                    '  sleep "${GUARDS_POLL_SECONDS}"\ndone\n')
        h = self.harness(old_read); h.install([["error", "gh: HTTP 403 forbidden"]])
        done, calls = h.run(wait="1", poll="0.2")
        self.assertGreater(calls, 1)                          # the collapsed loop kept polling a 403
        h = self.harness(); h.install([["error", "gh: HTTP 403 forbidden"]])
        done, calls = h.run(wait="1", poll="0.2")
        self.assertEqual((done.returncode, calls), (1, 1))     # the real step refuses on the first read
        # 2 An unbounded loop would hang on a guard that never finishes.
        unbounded = re.sub(r'if \[ \$\(\(SECONDS - started\)\) -ge "\$\{GUARDS_WAIT_SECONDS\}" \]; then.*?\n\s*fi\n', '', real, flags=re.S)
        self.assertNotEqual(unbounded, real)
        h = self.harness(unbounded); h.install([("in_progress", "")])
        with self.assertRaises(subprocess.TimeoutExpired):
            subprocess.run(["bash", "-e", str(h.script)], capture_output=True, text=True, timeout=3,
                           env={**os.environ, "PATH": str(h.bin) + os.pathsep + os.environ["PATH"],
                                "GITHUB_REPOSITORY": "o/r", "GUARDS_WAIT_SECONDS": "1", "GUARDS_POLL_SECONDS": "0.2"})
        # 3 A loop that waits on a finished failure would sit out the whole bound before refusing.
        patient = real.replace('if [ -n "$conclusion" ] && [ "$conclusion" != "success" ]; then', 'if false; then')
        self.assertNotEqual(patient, real)
        h = self.harness(patient); h.install([("completed", "failure")])
        done, calls = h.run(wait="1", poll="0.2")
        self.assertGreater(calls, 1)                          # the real step refuses on the first read, see above


class StaleDispatchAndPin(unittest.TestCase):
    def test_a_stale_dispatch_still_exits_green_without_deploying(self):
        h = Harness(step(pages_doc(), TARGET_STEP)["run"])
        self.addCleanup(h.close); h.install([("completed", "success")])
        done, _ = h.run(GUARDED_SHA="a" * 40)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("deploy=false", h.output.read_text())
        self.assertIn("main advanced", done.stdout)

    def test_a_matching_or_recovery_dispatch_authorizes_the_deploy(self):
        for guarded in (SHA, ""):
            h = Harness(step(pages_doc(), TARGET_STEP)["run"])
            self.addCleanup(h.close); h.install([("completed", "success")])
            done, _ = h.run(GUARDED_SHA=guarded)
            self.assertEqual(done.returncode, 0)
            text = h.output.read_text()
            self.assertIn("deploy=true", text)
            self.assertIn("sha=" + SHA, text)

    def test_the_deploy_job_still_packages_the_verified_sha(self):
        doc = pages_doc()
        deploy = doc["jobs"]["deploy"]
        self.assertIn("verify", [deploy["needs"]] if isinstance(deploy["needs"], str) else deploy["needs"])
        self.assertIn("needs.verify.outputs.deploy == 'true'", deploy["if"])
        refs = [s.get("with", {}).get("ref") for s in deploy["steps"] if str(s.get("uses", "")).startswith("actions/checkout@")]
        self.assertEqual(refs, ["${{ needs.verify.outputs.sha }}"])
        self.assertEqual(doc["jobs"]["verify"]["outputs"]["sha"], "${{ steps.target.outputs.sha }}")

    def test_the_later_gates_are_still_required_before_a_deploy(self):
        names = [s.get("name") for s in pages_doc()["jobs"]["verify"]["steps"]]
        for required in ("The record passes its own gates", "The copy about to be published keeps the house rules",
                         "The published site is exactly what the ledgers produce"):
            self.assertIn(required, names)
        order = [names.index(n) for n in (WAIT_STEP, "The record passes its own gates",
                                          "The published site is exactly what the ledgers produce")]
        self.assertEqual(order, sorted(order))


if __name__ == "__main__":
    unittest.main(verbosity=2)
