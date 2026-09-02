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
    ):
        if required not in shell:
            out.append(problem)

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

    good_pages = {
        "on": {"workflow_dispatch": {"inputs": {"guarded_sha": {"required": False}}},
               "schedule": [{"cron": "0 */2 * * *"}]},
        "permissions": {"checks": "read"},
        "jobs": {
            "verify": {
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
                    {"run": "SHA=$(git rev-parse HEAD)\n"
                            "gh api repos/x/commits/${SHA}/check-runs?check_name=guards\n"
                            'if [ "$conclusion" != "success" ]; then exit 1; fi'}]},
            "deploy": {"needs": "verify",
                       "if": "needs.verify.outputs.deploy == 'true'",
                       "steps": [{"uses": "actions/checkout@v4",
                                  "with": {"ref": "${{ needs.verify.outputs.sha }}"}},
                                 {"run": "true"}]}}}
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
