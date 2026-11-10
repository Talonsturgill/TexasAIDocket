#!/usr/bin/env python3
"""release_shape.py — prove every deployment reaches Pages through full guards.

The release chain has two kinds of main writer. A user-token push starts guards.yml through its
push trigger. A collector push uses GITHUB_TOKEN, which deliberately does not start another
workflow, so each collector dispatches guards.yml explicitly after its push succeeds.

The success-only release job downstream of the aggregate `guards` check dispatches Pages with its
exact SHA. Pages never listens directly to a push or collector. It exits cleanly if main has moved,
and otherwise checks that the exact SHA it is about to publish has a successful check named
`guards`. The deploy job checks out that verified SHA rather than a branch name. The scheduled
backstop uses the same proof, so it can recover a missed deploy without becoming a validation
bypass.

This checker refuses any break in that chain and self-tests the ways it can fail.
"""
from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:                                                  # pragma: no cover
    print("release_shape: PyYAML missing (install requirements.txt)", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"
PAGES = WORKFLOWS / "pages.yml"
GUARDS = WORKFLOWS / "guards.yml"
PUSH = re.compile(r"\bgit\s+push\b")
GUARDED_PUSH = "git push origin HEAD:main"
DISPATCH = "gh workflow run guards.yml --ref main"
PAGES_DISPATCH = ('gh workflow run pages.yml --repo "${GITHUB_REPOSITORY}" --ref main '
                  '--field guarded_sha="${GITHUB_SHA}"')


def triggers(doc: dict) -> dict:
    """PyYAML 1.1 reads an unquoted `on` as True, so accept both spellings."""
    return doc.get("on") or doc.get(True) or {}


def run_steps(doc: dict) -> list[tuple[str, str]]:
    return [(name, step.get("run") or "")
            for job in (doc.get("jobs") or {}).values()
            for step in (job.get("steps") or [])
            for name in [step.get("name") or "(unnamed)"]
            if isinstance(step.get("run"), str)]


def pages_problems(doc: dict) -> list[str]:
    out: list[str] = []
    on = triggers(doc)

    if "push" in on:
        out.append("pages still has a push trigger, so deployment can race the full guard suite")
    if "workflow_run" in on:
        out.append("pages still uses workflow_run, which is suppressed after token-dispatched guards")
    if "workflow_dispatch" not in on:
        out.append("pages has no explicit dispatch trigger for the post-guard release job")
    dispatch = on.get("workflow_dispatch") or {}
    if not isinstance(dispatch, dict) or "guarded_sha" not in (dispatch.get("inputs") or {}):
        out.append("pages dispatch does not accept the exact guarded SHA")
    if "schedule" not in on:
        out.append("pages has no scheduled recovery path for a missed deployment")

    permissions = doc.get("permissions") or {}
    if permissions.get("checks") != "read":
        out.append("pages cannot read the guard check attached to the main commit")

    jobs = doc.get("jobs") or {}
    verify = jobs.get("verify") or {}

    checkout_main = any(step.get("uses", "").startswith("actions/checkout@")
                        and (step.get("with") or {}).get("ref") == "main"
                        for step in (verify.get("steps") or []))
    if not checkout_main:
        out.append("pages verify does not check out main by name")

    outputs = verify.get("outputs") or {}
    if outputs.get("deploy") != "${{ steps.target.outputs.deploy }}":
        out.append("pages verify does not expose the stale-dispatch decision to deploy")
    if outputs.get("sha") != "${{ steps.target.outputs.sha }}":
        out.append("pages verify does not expose the exact checked SHA to deploy")

    shell = "\n".join(run for _name, run in run_steps({"jobs": {"verify": verify}}))
    for required, problem in (
        ("git rev-parse HEAD", "pages does not identify the exact commit it checked out"),
        ("GUARDED_SHA", "pages does not compare a release dispatch with current main"),
        ("deploy=false", "pages cannot skip a stale release dispatch cleanly"),
        ("deploy=true", "pages cannot authorize a matching or recovery dispatch"),
        ("sha=${SHA}", "pages does not record the exact checked SHA for deploy"),
        ("commits/${SHA}/check-runs", "pages does not query checks for that exact commit"),
        ("check_name=guards", "pages does not require the aggregate guard check by name"),
        ('[ "$conclusion" != "success" ]', "pages does not reject a non-success guard result"),
        ("GUARDS_WAIT_SECONDS", "pages can wait on a pending guard result without a bound"),
        ("GUARDS_POLL_SECONDS", "pages polls a pending guard result without a stated interval"),
        ("did not finish within", "pages does not refuse a guard result that never arrives"),
        ("could not read the guards result", "pages does not fail closed on a GitHub API error or invalid response"),
        ("GUARDS_API_RETRIES", "pages retries a GitHub API error without a stated limit"),
    ):
        if required not in shell:
            out.append(problem)

    # The wait must be a stated, bounded number, and the job must outlast it.
    wait_steps = [step for step in (verify.get("steps") or [])
                  if "check_name=guards" in str(step.get("run") or "")]
    for step in wait_steps:
        env = step.get("env") or {}
        try:
            bound = int(str(env.get("GUARDS_WAIT_SECONDS")))
            poll = float(str(env.get("GUARDS_POLL_SECONDS")))
        except ValueError:
            out.append("pages does not state its guard wait and poll interval as numbers")
            continue
        if not 0 < bound <= 7200:
            out.append("pages guard wait is not a bounded number of seconds up to two hours")
        if poll < 1:
            out.append("pages polls the guard result more than once a second")
        limit = verify.get("timeout-minutes")
        if not isinstance(limit, int) or limit * 60 <= bound:
            out.append("the pages verify job can be cut off before its guard wait ends")

    deploy = jobs.get("deploy") or {}
    needs = deploy.get("needs") or []
    if isinstance(needs, str):
        needs = [needs]
    if "verify" not in needs:
        out.append("the deploy job does not wait on release verification")
    if "needs.verify.outputs.deploy == 'true'" not in str(deploy.get("if") or ""):
        out.append("the deploy job does not skip a stale guarded SHA")
    pinned_checkout = any(step.get("uses", "").startswith("actions/checkout@")
                          and (step.get("with") or {}).get("ref") ==
                          "${{ needs.verify.outputs.sha }}"
                          for step in (deploy.get("steps") or []))
    if not pinned_checkout:
        out.append("the deploy job does not package the exact SHA the verify job checked")
    # A pinned checkout is not an upload, and a successful API request is not proof
    # that readers receive these bytes. Check the real steps, not mentions in comments.
    steps = deploy.get("steps") or []
    uploads = [(i, step) for i, step in enumerate(steps)
               if step.get("uses", "").startswith("actions/upload-pages-artifact@")]
    releases = [(i, step) for i, step in enumerate(steps)
                if step.get("uses", "").startswith("actions/deploy-pages@")]
    if len(uploads) != 1 or (uploads[0][1].get("with") or {}).get("path") != "docs":
        out.append("Pages must upload exactly one artifact from docs")
    if deploy.get("continue-on-error", False) is not False:
        out.append("Pages deployment job must fail closed")
    if len(releases) != 1:
        out.append("Pages must use exactly one deployment, not retries that restart syncing")

    preflight = "python3 scripts/site/pages_release_check.py --site docs"
    archive = preflight + ' --archive "$RUNNER_TEMP/artifact.tar"'
    live = preflight + " --url https://texasaidocket.com --wait-seconds 300"

    def required_step(command: str) -> list[int]:
        # Require a standalone command, not an echo, comment, self-test, or || true.
        return [i for i, step in enumerate(steps)
                if str(step.get("run") or "").strip() == command]

    before, after = required_step(preflight), required_step(live)
    packaged = required_step(archive)
    if len(before) != 1:
        out.append("Pages lacks its standalone artifact preflight invocation")
    if len(after) != 1:
        out.append("Pages lacks its standalone live byte proof invocation")
    if len(packaged) != 1:
        out.append("Pages lacks its standalone uploaded archive proof invocation")
    required = uploads + releases + [(i, steps[i]) for i in before + packaged + after]
    for _i, step in required:
        if step.get("continue-on-error", False) is not False:
            out.append("Pages upload, deployment and release proofs must fail closed")
        if step.get("if") not in (None, "success()", "${{ success() }}"):
            out.append("Pages upload, deployment and release proofs must not be skipped or run after failure")
        if step.get("working-directory") not in (None, "."):
            out.append("Pages release proofs must run from the repository root")
    if (deploy.get("defaults") or {}).get("run", {}).get("working-directory") not in (None, "."):
        out.append("Pages release proofs must run from the repository root")
    if len(uploads) == len(releases) == len(before) == len(packaged) == len(after) == 1:
        if not before[0] < uploads[0][0] < packaged[0] < releases[0][0] < after[0]:
            out.append("Pages must preflight, upload, check the archive, deploy, then prove the live bytes in that order")
    if len(releases) == 1:
        release = releases[0][1]
        if release.get("uses") != "actions/deploy-pages@v4":
            out.append("Pages must use the reviewed deploy-pages@v4 action")
        if len(uploads) == 1:
            uploaded_name = (uploads[0][1].get("with") or {}).get("name", "github-pages")
            deployed_name = (release.get("with") or {}).get("artifact_name", "github-pages")
            if uploaded_name != deployed_name:
                out.append("Pages must deploy the same artifact name that was uploaded")
        if release.get("id") != "deployment":
            out.append("the single Pages deployment must expose its deployment output")
        try:
            timeout = int(str((release.get("with") or {}).get("timeout")))
        except ValueError:
            timeout = 0
        if not 1800000 <= timeout <= 3600000:
            out.append("Pages deployment timeout must be bounded between 30 and 60 minutes")
        budget = deploy.get("timeout-minutes")
        # Five minutes for live propagation plus five for checkout, preflight and upload.
        if not isinstance(budget, int) or isinstance(budget, bool) or not timeout / 60000 + 10 <= budget <= 90:
            out.append("Pages job budget must cover deployment plus ten minutes, bounded at 90 minutes")
        step_budget = release.get("timeout-minutes")
        if step_budget is not None and (not isinstance(step_budget, int) or step_budget * 60000 <= timeout):
            out.append("Pages deployment step budget can cut off its polling timeout")
    return out


def guards_problems(doc: dict) -> list[str]:
    out: list[str] = []
    if doc.get("name") != "guards":
        out.append("guards.yml changed the aggregate check name Pages proves before release")
    on = triggers(doc)
    if "workflow_dispatch" not in on:
        out.append("guards.yml has no workflow_dispatch trigger for GITHUB_TOKEN writers")
    push = on.get("push") or {}
    if "main" not in (push.get("branches") or []):
        out.append("guards.yml does not run when a user-token push moves main")

    jobs = doc.get("jobs") or {}
    release = jobs.get("release") or {}
    if not release:
        out.append("guards.yml has no success-only release job to dispatch Pages")
        return out

    needs = release.get("needs") or []
    if isinstance(needs, str):
        needs = [needs]
    if "guards" not in needs:
        out.append("the release job can dispatch Pages before the aggregate guards check passes")

    condition = str(release.get("if") or "")
    if "github.ref == 'refs/heads/main'" not in condition:
        out.append("the release job is not restricted to main")

    permissions = release.get("permissions") or {}
    if permissions.get("actions") != "write":
        out.append("the release job cannot dispatch Pages because actions: write is missing")

    dispatch_steps = [step for step in (release.get("steps") or [])
                      if PAGES_DISPATCH in str(step.get("run") or "")]
    if not dispatch_steps:
        out.append("the release job does not dispatch Pages after full guards")
    elif not any((step.get("env") or {}).get("GH_TOKEN") == "${{ github.token }}"
                 for step in dispatch_steps):
        out.append("the Pages dispatch has no GH_TOKEN and cannot authenticate")
    return out


def writer_problems(name: str, doc: dict) -> list[str]:
    out: list[str] = []
    if (doc.get("permissions") or {}).get("actions") != "write":
        out.append(f"{name} cannot dispatch guards because actions: write is missing")

    found_push = False
    guarded_push = False
    for job_name, job in (doc.get("jobs") or {}).items():
        runs = [step.get("run") or "" for step in (job.get("steps") or [])
                if isinstance(step.get("run"), str)]
        push_at = [i for i, run in enumerate(runs) if PUSH.search(run)]
        if not push_at:
            continue
        found_push = True
        guarded_at = [i for i, run in enumerate(runs) if GUARDED_PUSH in run]
        if not guarded_at:
            out.append(f"{name}/{job_name} writes git history without the guarded HEAD:main push")
            continue
        guarded_push = True
        dispatch_at = [i for i, run in enumerate(runs) if DISPATCH in run]
        if not dispatch_at:
            out.append(f"{name}/{job_name} can move main without dispatching full guards")
        elif not any(i > max(guarded_at) for i in dispatch_at):
            out.append(f"{name}/{job_name} does not dispatch guards after its main push")

    if not found_push:
        out.append(f"{name} was classified as a writer but contains no git push")
    elif not guarded_push:
        out.append(f"{name} writes git history but does not use the guarded HEAD:main push")
    return out


def all_problems(pages: dict, guards: dict, writers: dict[str, dict]) -> list[str]:
    out = pages_problems(pages)
    out.extend(guards_problems(guards))
    if not writers:
        out.append("no workflow that writes git history was found; writer discovery is broken")
    for name, doc in sorted(writers.items()):
        out.extend(writer_problems(name, doc))
    return out


def self_test() -> int:
    failures = 0

    def check(label: str, condition: bool, extra: str = "") -> None:
        nonlocal failures
        print(f"  {'ok  ' if condition else 'FAIL'}  {label}"
              f"{'' if condition else '  ' + extra}")
        failures += int(not condition)

    GOOD_WAIT = ("SHA=$(git rev-parse HEAD)\n"
                 "gh api repos/x/commits/${SHA}/check-runs?check_name=guards\n"
                 'if [ -n "$conclusion" ] && [ "$conclusion" != "success" ]; then exit 1; fi\n'
                 'echo "did not finish within ${GUARDS_WAIT_SECONDS}"; sleep "${GUARDS_POLL_SECONDS}"\n'
                 'echo "could not read the guards result ${GUARDS_API_RETRIES}"')
    good_pages = {
        "on": {"workflow_dispatch": {"inputs": {"guarded_sha": {"required": False}}},
               "schedule": [{"cron": "0 */2 * * *"}]},
        "permissions": {"checks": "read"},
        "jobs": {
            "verify": {
                "timeout-minutes": 100,
                "outputs": {"deploy": "${{ steps.target.outputs.deploy }}",
                            "sha": "${{ steps.target.outputs.sha }}"},
                "steps": [
                    {"uses": "actions/checkout@v4", "with": {"ref": "main"}},
                    {"id": "target", "run": "SHA=$(git rev-parse HEAD)\n"
                            "echo sha=${SHA}\n"
                            "if [ -n \"$GUARDED_SHA\" ] && [ \"$GUARDED_SHA\" != \"$SHA\" ]; then\n"
                            "  echo deploy=false\n"
                            "fi\n"
                            "echo deploy=true"},
                    {"env": {"GUARDS_WAIT_SECONDS": "4500", "GUARDS_POLL_SECONDS": "60", "GUARDS_API_RETRIES": "4"},
                     "run": GOOD_WAIT}]},
            "deploy": {"needs": "verify", "timeout-minutes": 40,
                       "if": "needs.verify.outputs.deploy == 'true'",
                       "steps": [{"uses": "actions/checkout@v4",
                                  "with": {"ref": "${{ needs.verify.outputs.sha }}"}},
                                 {"run": "python3 scripts/site/pages_release_check.py --site docs"},
                                 {"uses": "actions/upload-pages-artifact@v3", "with": {"path": "docs"}},
                                 {"run": 'python3 scripts/site/pages_release_check.py --site docs --archive "$RUNNER_TEMP/artifact.tar"'},
                                 {"uses": "actions/deploy-pages@v4", "id": "deployment",
                                  "with": {"timeout": 1800000}},
                                 {"run": "python3 scripts/site/pages_release_check.py --site docs"
                                         " --url https://texasaidocket.com --wait-seconds 300"}]}}}
    good_writer = {
        "permissions": {"actions": "write"},
        "jobs": {"write": {"steps": [
            {"name": "push", "run": GUARDED_PUSH},
            {"name": "guard", "run": DISPATCH}]}}}
    good_release = {
        "needs": "guards",
        "if": "github.ref == 'refs/heads/main'",
        "permissions": {"actions": "write"},
        "steps": [{"name": "release", "env": {"GH_TOKEN": "${{ github.token }}"},
                   "run": PAGES_DISPATCH}]}
    good_guards = {
        "name": "guards",
        "on": {"push": {"branches": ["main"]}, "workflow_dispatch": {}},
        "jobs": {"guards": {"steps": [{"run": "echo green"}]},
                 "release": good_release}}

    check("a complete release chain reports nothing",
          not all_problems(good_pages, good_guards, {"writer.yml": good_writer}),
          str(all_problems(good_pages, good_guards, {"writer.yml": good_writer})))

    raced = {**good_pages, "on": {**good_pages["on"], "push": {"branches": ["main"]}}}
    check("a direct Pages push trigger is caught",
          any("race" in p for p in pages_problems(raced)), str(pages_problems(raced)))

    chained = {**good_pages, "on": {**good_pages["on"], "workflow_run": {
        "workflows": ["guards"], "types": ["completed"], "branches": ["main"]}}}
    check("a token-suppressed workflow_run handoff is caught",
          any("suppressed" in p for p in pages_problems(chained)),
          str(pages_problems(chained)))

    wrong_check = {**good_pages, "jobs": {**good_pages["jobs"], "verify": {
        **good_pages["jobs"]["verify"],
        "steps": [{"uses": "actions/checkout@v4", "with": {"ref": "main"}},
                  {"run": "git rev-parse HEAD"}]}}}
    check("a deployment with no exact-SHA guard query is caught",
          any("exact commit" in p or "aggregate guard" in p for p in
              pages_problems(wrong_check)), str(pages_problems(wrong_check)))

    def with_wait_step(**changes):
        verify = dict(good_pages["jobs"]["verify"])
        steps = [dict(s) for s in verify["steps"]]
        steps[2] = {**steps[2], **changes.get("step", {})}
        if "run" in changes:
            steps[2]["run"] = changes["run"]
        verify["steps"] = steps
        verify.update(changes.get("verify", {}))
        return {**good_pages, "jobs": {**good_pages["jobs"], "verify": verify}}

    check("a guard wait with no bound is caught",
          any("without a bound" in p for p in pages_problems(
              with_wait_step(run=GOOD_WAIT.replace("GUARDS_WAIT_SECONDS", "OTHER")))),
          str(pages_problems(with_wait_step(run=GOOD_WAIT.replace("GUARDS_WAIT_SECONDS", "OTHER")))))
    check("a guard wait with no timeout refusal is caught",
          any("never arrives" in p for p in pages_problems(
              with_wait_step(run=GOOD_WAIT.replace("did not finish within", "x")))))
    check("an enormous guard wait is caught",
          any("bounded number" in p for p in pages_problems(
              with_wait_step(step={"env": {"GUARDS_WAIT_SECONDS": "99999", "GUARDS_POLL_SECONDS": "60", "GUARDS_API_RETRIES": "4"}}))))
    check("an API error that is not failed closed is caught",
          any("fail closed on a GitHub API error" in p for p in pages_problems(
              with_wait_step(run=GOOD_WAIT.replace("could not read the guards result", "x")))))
    check("an unbounded API retry is caught",
          any("without a stated limit" in p for p in pages_problems(
              with_wait_step(run=GOOD_WAIT.replace("GUARDS_API_RETRIES", "OTHER")))))
    check("a busy poll is caught",
          any("more than once a second" in p for p in pages_problems(
              with_wait_step(step={"env": {"GUARDS_WAIT_SECONDS": "4500", "GUARDS_POLL_SECONDS": "0.1", "GUARDS_API_RETRIES": "4"}}))))
    check("a verify job that can be cut off before the wait ends is caught",
          any("cut off" in p for p in pages_problems(with_wait_step(verify={"timeout-minutes": 10}))))
    check("a missing verify timeout is caught",
          any("cut off" in p for p in pages_problems(with_wait_step(verify={"timeout-minutes": None}))))

    no_stale_skip = {**good_pages, "jobs": {**good_pages["jobs"], "verify": {
        **good_pages["jobs"]["verify"],
        "steps": [{"uses": "actions/checkout@v4", "with": {"ref": "main"}},
                  {"run": "SHA=$(git rev-parse HEAD)\n"
                          "gh api repos/x/commits/${SHA}/check-runs?check_name=guards\n"
                          'if [ "$conclusion" != "success" ]; then exit 1; fi'}]}}}
    check("a release that turns a stale dispatch red is caught",
          any("stale release" in p or "compare a release" in p for p in
              pages_problems(no_stale_skip)), str(pages_problems(no_stale_skip)))

    moving_deploy = {**good_pages, "jobs": {**good_pages["jobs"], "deploy": {
        **good_pages["jobs"]["deploy"],
        "steps": [{"uses": "actions/checkout@v4", "with": {"ref": "main"}}]}}}
    check("a deploy that re-reads a moving main branch is caught",
          any("exact SHA" in p for p in pages_problems(moving_deploy)),
          str(pages_problems(moving_deploy)))

    def broken_deploy(label, mutate, expected):
        doc = copy.deepcopy(good_pages)
        mutate(doc["jobs"]["deploy"])
        problems = pages_problems(doc)
        check(label, any(expected in p for p in problems), str(problems))

    broken_deploy("a soft-failing deployment job is caught",
                  lambda d: d.update({"continue-on-error": True}), "job must fail closed")
    broken_deploy("a mismatched artifact name is caught",
                  lambda d: d["steps"][2]["with"].update(name="other-site"), "same artifact name")
    broken_deploy("a wrong upload directory is caught",
                  lambda d: d["steps"][2]["with"].update(path="missing-directory"), "from docs")
    broken_deploy("removing every upload and deployment is caught",
                  lambda d: d.update(steps=d["steps"][:2]), "exactly one deployment")
    broken_deploy("a deployment retry that restarts syncing is caught",
                  lambda d: d["steps"].append(copy.deepcopy(d["steps"][4])), "exactly one deployment")
    for index in (1, 2, 3, 4, 5):
        broken_deploy(f"release step {index} cannot hide failure",
                      lambda d, i=index: d["steps"][i].update({"continue-on-error": True}), "fail closed")
        broken_deploy(f"release step {index} cannot be conditionally skipped",
                      lambda d, i=index: d["steps"][i].update({"if": "false"}), "must not be skipped")
    for value in (None, 600000, 3600001, "invalid"):
        broken_deploy(f"invalid deployment timeout {value!r} is caught",
                      lambda d, v=value: d["steps"][4]["with"].update(timeout=v), "bounded between")
    for value in (None, 30, 39, 1000):
        broken_deploy(f"insufficient or unbounded job budget {value!r} is caught",
                      lambda d, v=value: d.update({"timeout-minutes": v}), "job budget")
    broken_deploy("a premature step timeout is caught",
                  lambda d: d["steps"][4].update({"timeout-minutes": 10}), "step budget")
    broken_deploy("live proof before deployment is caught",
                  lambda d: d["steps"].insert(4, d["steps"].pop(5)), "in that order")
    broken_deploy("preflight after upload is caught",
                  lambda d: d["steps"].insert(2, d["steps"].pop(1)), "in that order")
    for prefix, suffix in (("# ", ""), ("echo ", ""), ("", " --self-test"), ("", " || true")):
        broken_deploy(f"a preflight mention {prefix!r}/{suffix!r} is not execution",
                      lambda d, p=prefix, s=suffix: d["steps"][1].update(
                          run=p + d["steps"][1]["run"] + s), "artifact preflight")
    broken_deploy("live proof against a different site is caught",
                  lambda d: d["steps"][5].update(run=d["steps"][5]["run"].replace(
                      "https://texasaidocket.com", "https://example.com")), "live byte proof")
    broken_deploy("a changed working directory is caught",
                  lambda d: d.update(defaults={"run": {"working-directory": "elsewhere"}}), "repository root")

    broken_deploy("missing uploaded archive validation is caught",
                  lambda d: d["steps"].pop(3), "uploaded archive proof")
    broken_deploy("archive validation before upload is caught",
                  lambda d: d["steps"].insert(2, d["steps"].pop(3)), "in that order")
    broken_deploy("archive validation of a different file is caught",
                  lambda d: d["steps"][3].update(run=d["steps"][3]["run"].replace(
                      "artifact.tar", "other.tar")), "uploaded archive proof")

    no_permission = {**good_writer, "permissions": {}}
    check("a writer unable to dispatch guards is caught",
          any("actions: write" in p for p in writer_problems("writer", no_permission)),
          str(writer_problems("writer", no_permission)))

    no_dispatch = {**good_guards, "on": {"push": {"branches": ["main"]}}}
    check("removing the guard dispatch trigger is caught",
          any("workflow_dispatch" in p for p in guards_problems(no_dispatch)),
          str(guards_problems(no_dispatch)))

    no_release_permission = {**good_guards, "jobs": {**good_guards["jobs"],
        "release": {**good_release, "permissions": {}}}}
    check("a release job unable to dispatch Pages is caught",
          any("actions: write" in p for p in guards_problems(no_release_permission)),
          str(guards_problems(no_release_permission)))

    bypass = {**good_guards, "jobs": {**good_guards["jobs"],
        "release": {**good_release, "needs": "gates"}}}
    check("a release job bypassing aggregate guards is caught",
          any("before the aggregate" in p for p in guards_problems(bypass)),
          str(guards_problems(bypass)))

    no_pages_dispatch = {**good_guards, "jobs": {**good_guards["jobs"],
        "release": {**good_release, "steps": [{"run": "echo done"}]}}}
    check("removing the post-guard Pages dispatch is caught",
          any("does not dispatch Pages" in p for p in guards_problems(no_pages_dispatch)),
          str(guards_problems(no_pages_dispatch)))

    no_repo_context = {**good_guards, "jobs": {**good_guards["jobs"],
        "release": {**good_release, "steps": [{
            "env": {"GH_TOKEN": "${{ github.token }}"},
            "run": "gh workflow run pages.yml --ref main"}]}}}
    check("a Pages dispatch without repository context is caught",
          any("does not dispatch Pages" in p for p in guards_problems(no_repo_context)),
          str(guards_problems(no_repo_context)))

    backwards = {**good_writer, "jobs": {"write": {"steps": [
        {"name": "guard", "run": DISPATCH},
        {"name": "push", "run": GUARDED_PUSH}]}}}
    check("dispatching before the push is caught",
          any("after" in p for p in writer_problems("writer", backwards)),
          str(writer_problems("writer", backwards)))

    if failures:
        print(f"\nrelease shape self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nrelease shape self-test: all passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    pages = yaml.safe_load(PAGES.read_text(encoding="utf-8"))
    guards = yaml.safe_load(GUARDS.read_text(encoding="utf-8"))
    writers: dict[str, dict] = {}
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if PUSH.search(text):
            writers[path.name] = yaml.safe_load(text)

    problems = all_problems(pages, guards, writers)
    if problems:
        print("release shape: BROKEN", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"release shape: OK — Pages is dispatched after guards; "
          f"{len(writers)} main writers reach it")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                          # noqa: BLE001
        print(f"release_shape: broke: {exc}", file=sys.stderr)
        sys.exit(2)
