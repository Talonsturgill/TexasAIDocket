#!/usr/bin/env python3
"""dependency_shape.py — prove every install uses the committed dependency locks.

Python requirements are exact pins, and installs use ``--no-deps`` so a missing transitive
package fails instead of being selected from the registry. Node installs use ``npm ci`` against
the committed package lock, and ``npx --no-install`` prevents an absent command from being
downloaded behind the lock's back.

    dependency_shape.py --self-test
    dependency_shape.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

try:
    import yaml
except ImportError:                                                   # pragma: no cover
    print("dependency_shape: PyYAML missing (install requirements.txt)", file=sys.stderr)
    sys.exit(2)


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS = (
    "requirements.txt",
    "requirements-ci.txt",
    "requirements-tools.txt",
    "requirements-carousel.txt",
)
REQUIRED_INCLUDES = {
    "requirements-ci.txt": "requirements.txt",
    "requirements-tools.txt": "requirements-ci.txt",
    "requirements-carousel.txt": "requirements-ci.txt",
}
PIN = re.compile(r"^([A-Za-z0-9_.-]+(?:\[[A-Za-z0-9_,.-]+\])?)==([^\s;]+)$")
SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def requirement_problems(root: Path) -> list[str]:
    out: list[str] = []
    versions: dict[str, tuple[str, str]] = {}
    includes: dict[str, set[str]] = {}

    for relative in REQUIREMENTS:
        path = root / relative
        includes[relative] = set()
        if not path.exists():
            out.append(f"{relative} is missing")
            continue
        for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith(("-r ", "--requirement ")):
                target_name = line.split(maxsplit=1)[1]
                target = (path.parent / target_name).resolve()
                try:
                    target_relative = target.relative_to(root.resolve()).as_posix()
                except ValueError:
                    out.append(f"{relative}:{line_number} includes a file outside the repo")
                    continue
                includes[relative].add(target_relative)
                if not target.exists():
                    out.append(f"{relative}:{line_number} includes missing {target_relative}")
                continue
            match = PIN.fullmatch(line)
            if not match:
                out.append(f"{relative}:{line_number} is not an exact == pin: {line!r}")
                continue
            package = match.group(1).lower().replace("_", "-")
            version = match.group(2)
            previous = versions.get(package)
            if previous and previous[0] != version:
                out.append(
                    f"{package} is pinned to both {previous[0]} in {previous[1]} and "
                    f"{version} in {relative}"
                )
            versions[package] = (version, relative)

    for manifest, required in REQUIRED_INCLUDES.items():
        if required not in includes.get(manifest, set()):
            out.append(f"{manifest} must include {required}")
    return out


def node_problems(root: Path) -> list[str]:
    out: list[str] = []
    package_path = root / "package.json"
    lock_path = root / "package-lock.json"
    node_version_path = root / ".node-version"
    if not package_path.exists():
        return ["package.json is missing"]
    if not lock_path.exists():
        return ["package-lock.json is missing"]
    if not node_version_path.exists():
        out.append(".node-version is missing")
    elif not SEMVER.fullmatch(node_version_path.read_text(encoding="utf-8").strip()):
        out.append(".node-version must contain one exact semantic version")

    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return out + [f"Node manifest does not parse: {exc}"]

    declared: dict[str, str] = {}
    for group in ("dependencies", "devDependencies"):
        values = package.get(group) or {}
        if not isinstance(values, dict):
            out.append(f"package.json {group} must be an object")
            continue
        declared.update(values)
        for name, version in values.items():
            if not isinstance(version, str) or not SEMVER.fullmatch(version):
                out.append(f"package.json {group}.{name} is not an exact version: {version!r}")

    packages = lock.get("packages") or {}
    if lock.get("lockfileVersion") != 3:
        out.append("package-lock.json must use lockfileVersion 3")
    if not isinstance(packages, dict) or "" not in packages:
        return out + ["package-lock.json has no root package entry"]

    lock_root = packages[""]
    locked_declared: dict[str, str] = {}
    for group in ("dependencies", "devDependencies"):
        locked_declared.update(lock_root.get(group) or {})
    if locked_declared != declared:
        out.append("package-lock.json root dependencies do not match package.json")

    for name, version in declared.items():
        entry = packages.get(f"node_modules/{name}") or {}
        if entry.get("version") != version:
            out.append(f"package-lock.json does not lock {name} to {version}")

    for location, entry in packages.items():
        if not location:
            continue
        version = entry.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            out.append(f"package-lock.json {location} has no exact version")
        if not entry.get("resolved") or not entry.get("integrity"):
            out.append(f"package-lock.json {location} has no resolved artifact and integrity")
    return out


def workflow_problems(root: Path) -> list[str]:
    out: list[str] = []
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.exists():
        return [".github/workflows is missing"]

    for path in sorted(workflow_dir.glob("*.yml")):
        try:
            document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except (yaml.YAMLError, OSError) as exc:
            out.append(f"{path.name} does not parse: {exc}")
            continue
        for job_name, job in (document.get("jobs") or {}).items():
            steps = job.get("steps") or []
            for step in steps:
                run = step.get("run")
                if not isinstance(run, str):
                    continue
                commands = [line.strip() for line in run.splitlines()
                            if line.strip() and not line.strip().startswith("#")]
                for command in commands:
                    if re.search(r"\bpip(?:3)?\s+install\b", command):
                        if not re.search(r"\bpython\s+-m\s+pip\s+install\b", command):
                            out.append(f"{path.name}/{job_name} does not bind pip to Python")
                        if "--no-deps" not in command or "--requirement" not in command:
                            out.append(f"{path.name}/{job_name} lets pip resolve outside a lock")
                        if not any(name in command for name in
                                   ("requirements.txt", "requirements-ci.txt")):
                            out.append(f"{path.name}/{job_name} installs an unknown requirement set")
                    if re.search(r"\bnpm\s+install\b", command):
                        out.append(f"{path.name}/{job_name} uses npm install instead of npm ci")
                    if command.startswith("npx ") and "--no-install" not in command:
                        out.append(f"{path.name}/{job_name} lets npx download outside the lock")

                if "playwright install" not in run:
                    continue
                if "npm ci --ignore-scripts --no-audit --no-fund" not in run:
                    out.append(f"{path.name}/{job_name} does not install Node from the lock")
                if "npx --no-install playwright install" not in run:
                    out.append(f"{path.name}/{job_name} can fetch Playwright outside the lock")
                setup_node = [candidate for candidate in steps
                              if str(candidate.get("uses", "")).startswith("actions/setup-node@")]
                if not setup_node:
                    out.append(f"{path.name}/{job_name} does not pin the Node runtime")
                else:
                    setup = setup_node[0].get("with") or {}
                    if setup.get("node-version-file") != ".node-version":
                        out.append(f"{path.name}/{job_name} does not read .node-version")
                    if setup.get("cache") != "npm":
                        out.append(f"{path.name}/{job_name} does not cache npm by package lock")
                cache_keys = [str((candidate.get("with") or {}).get("key", ""))
                              for candidate in steps
                              if str(candidate.get("uses", "")).startswith("actions/cache@")]
                if not any("hashFiles('package-lock.json')" in key for key in cache_keys):
                    out.append(f"{path.name}/{job_name} browser cache ignores package-lock.json")
    return out


def bootstrap_problems(root: Path) -> list[str]:
    path = root / ".claude" / "skills" / "carousel-engine" / "bootstrap.sh"
    if not path.exists():
        return ["carousel bootstrap is missing"]
    text = path.read_text(encoding="utf-8")
    out: list[str] = []
    if "pip install" not in text or "--no-deps" not in text:
        out.append("carousel bootstrap lets pip resolve outside the lock")
    if "requirements-carousel.txt" not in text:
        out.append("carousel bootstrap does not install requirements-carousel.txt")
    return out


def problems(root: Path = REPO_ROOT) -> list[str]:
    return (requirement_problems(root) + node_problems(root)
            + workflow_problems(root) + bootstrap_problems(root))


def write_fixture(root: Path) -> None:
    (root / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (root / ".claude" / "skills" / "carousel-engine").mkdir(
        parents=True, exist_ok=True)
    (root / "requirements.txt").write_text("PyYAML==6.0.3\n", encoding="utf-8")
    (root / "requirements-ci.txt").write_text(
        "-r requirements.txt\nPillow==12.3.0\n", encoding="utf-8")
    (root / "requirements-tools.txt").write_text(
        "-r requirements-ci.txt\nfonttools==4.63.0\n", encoding="utf-8")
    (root / "requirements-carousel.txt").write_text(
        "-r requirements-ci.txt\nplaywright==1.56.0\n", encoding="utf-8")
    (root / ".node-version").write_text("24.18.0\n", encoding="utf-8")
    (root / "package.json").write_text(json.dumps({
        "private": True, "devDependencies": {"playwright": "1.56.1"}
    }), encoding="utf-8")
    (root / "package-lock.json").write_text(json.dumps({
        "lockfileVersion": 3,
        "packages": {
            "": {"devDependencies": {"playwright": "1.56.1"}},
            "node_modules/playwright": {
                "version": "1.56.1", "resolved": "https://example.test/playwright.tgz",
                "integrity": "sha512-test",
            },
        },
    }), encoding="utf-8")
    (root / ".claude" / "skills" / "carousel-engine" / "bootstrap.sh").write_text(
        "python3 -m pip install --no-deps --requirement requirements-carousel.txt\n",
        encoding="utf-8")
    (root / ".github" / "workflows" / "guards.yml").write_text("""
jobs:
  collect:
    steps:
      - run: python -m pip install --no-deps --requirement requirements.txt
  browser:
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version-file: .node-version
          cache: npm
      - uses: actions/cache@v4
        with:
          key: pw-${{ hashFiles('package-lock.json') }}
      - run: |
          npm ci --ignore-scripts --no-audit --no-fund
          npx --no-install playwright install chromium
""", encoding="utf-8")


def self_test() -> int:
    failures = 0

    def check(label: str, condition: bool, extra: str = "") -> None:
        nonlocal failures
        print(f"  {'ok  ' if condition else 'FAIL'}  {label}"
              f"{'' if condition else '  ' + extra}")
        if not condition:
            failures += 1

    with tempfile.TemporaryDirectory(prefix="dependency-shape-") as temp:
        root = Path(temp)
        write_fixture(root)
        check("a fully locked fixture passes", not problems(root), "; ".join(problems(root)))

        (root / "requirements.txt").write_text("PyYAML>=6\n", encoding="utf-8")
        found = problems(root)
        check("a floating Python version is CAUGHT",
              any("not an exact == pin" in item for item in found), str(found))
        write_fixture(root)

        package = json.loads((root / "package.json").read_text(encoding="utf-8"))
        package["devDependencies"]["playwright"] = "^1.56.1"
        (root / "package.json").write_text(json.dumps(package), encoding="utf-8")
        found = problems(root)
        check("a ranged Node version is caught",
              any("not an exact version" in item for item in found), str(found))
        write_fixture(root)

        lock = json.loads((root / "package-lock.json").read_text(encoding="utf-8"))
        lock["packages"]["node_modules/playwright"]["version"] = "1.57.0"
        (root / "package-lock.json").write_text(json.dumps(lock), encoding="utf-8")
        found = problems(root)
        check("package and lock drift is caught",
              any("does not lock playwright" in item for item in found), str(found))
        write_fixture(root)

        workflow = root / ".github" / "workflows" / "guards.yml"
        workflow.write_text(workflow.read_text(encoding="utf-8").replace(
            "npm ci --ignore-scripts --no-audit --no-fund", "npm install playwright"),
            encoding="utf-8")
        found = problems(root)
        check("npm install outside the lock is caught",
              any("npm install instead of npm ci" in item for item in found), str(found))
        write_fixture(root)

        workflow.write_text(workflow.read_text(encoding="utf-8").replace(
            "npx --no-install", "npx"), encoding="utf-8")
        found = problems(root)
        check("npx registry fallback is caught",
              any("npx download outside the lock" in item for item in found), str(found))

    live = problems(REPO_ROOT)
    check("the committed dependency shape is locked", not live, "; ".join(live))
    if failures:
        print(f"\ndependency_shape self-test: {failures} FAILED")
        return 1
    print("\ndependency_shape self-test: all passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    found = problems(REPO_ROOT)
    if found:
        print("dependency lock shape:", file=sys.stderr)
        for problem in found:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print("dependency shape ok: Python, Node, workflows, and bootstrap are locked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
