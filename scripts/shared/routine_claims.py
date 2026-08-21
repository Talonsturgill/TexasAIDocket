#!/usr/bin/env python3
"""routine_claims.py — the routine's claims about published copy, checked against the copy.

THE FAILURE THIS EXISTS FOR, which nearly happened on 2026-08-20.

`prompts/daily_routine.md` is what the unattended run reads every morning to know what to do,
and part of it DESCRIBES what the published pages say. On that day the owner had the water page
drop its coverage and exclusion notes, and the routine went on saying the page promised them.

Nothing was factually wrong in either file. The page was as the owner wanted it and the
routine's sentence had been true the day before. But the routine may edit `waterwatch_page.py`
for presentation, so the next run would have read its own instructions, found the page missing
copy those instructions said it carried, and PUT IT BACK. Every gate would have passed while it
did, because restored copy is true, computed, and in house style. The only evidence would have
been a deleted section reappearing on the site.

THAT IS A DIFFERENT KIND OF WRONG FROM THE ONES THIS REPO ALREADY CATCHES. A stale numeral is
wrong about a fact and `numeral_lint` sees it. A stale instruction is wrong about an INTENTION,
and nothing type-checks a paragraph. Delete a function something calls and Python throws; delete
a sentence a paragraph describes and the paragraph just sits there being confidently out of date.

WHAT THIS CHECKS, AND WHAT IT DELIBERATELY DOES NOT

It cannot read prose and work out what the routine meant. What it can do is hold the routine to
any claim it makes EXPLICITLY, so a claim worth relying on is a claim worth marking:

    <!-- onpage  water/ "storage over capacity" -->
    <!-- offpage water/ "San Antonio has no line" -->

`onpage` says the published page carries that string. `offpage` says it must not, which is the
half that catches this defect head on: copy removed on purpose stays removed, and a run that
restores it turns the suite red instead of quietly winning.

THE SCOPE IS HONEST RATHER THAN COMPLETE. A marker covers one string on one page. Prose around
it can still drift, and no gate here can stop that. What it removes is the case where a claim
was worth writing down and nothing was holding it to the page.

THE SECOND RULE, AND IT NEEDS NO MARKER. Every command the routine tells a run to execute must
keep its scratch inside the working tree.

That is a house law with a cost attached and the cost has already been paid. The Bash sandbox
and the permission mode are two different mechanisms: a sandboxed command that writes outside
the tree cannot complete, and the tool then stops and asks to re-run it unsandboxed, which is a
prompt no permission mode answers and no unattended run has anybody to answer. On 2026-08-20 the
owner was interrupted twice by exactly that, and this file's own first paragraph is about a near
miss on the same day.

The law was written down that evening. Two lines of this routine went on saying `--out /tmp/site`
anyway, because writing a rule in `CLAUDE.md` does nothing to the file that breaks it. So the
rule is read out of the prose it governs. `out/<date>/tmp/` takes anything `/tmp` would.

    routine_claims.py --self-test
    routine_claims.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PROMPTS = REPO_ROOT / "prompts"
DOCS = REPO_ROOT / "docs"

# `onpage` or `offpage`, a site path, then the exact string in double quotes. The string is
# taken verbatim and never normalised, because a claim about published copy that only matches
# after tidying is not a claim about published copy.
MARKER = re.compile(
    r"<!--\s*(?P<kind>onpage|offpage)\s+(?P<path>\S+)\s+\"(?P<text>[^\"]+)\"\s*-->")


def claims(root: Path = PROMPTS) -> list[dict]:
    """Every marked claim in every prompt, with the file and line that made it."""
    out = []
    for md in sorted(root.glob("*.md")):
        for n, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            for m in MARKER.finditer(line):
                out.append({"file": md.name, "line": n, "kind": m.group("kind"),
                            "path": m.group("path"), "text": m.group("text")})
    return out


def page_text(site_path: str, docs: Path = DOCS) -> str | None:
    """The built page a claim points at, or None when it is not there to check."""
    p = docs / site_path.lstrip("/")
    if p.is_dir() or site_path.endswith("/"):
        p = docs / site_path.strip("/") / "index.html"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8")


# Fenced shell blocks, which is where a routine's executable instructions live. Prose may name
# a system path while explaining why not to use one, and a rule that could not tell those apart
# would make the explanation unwritable.
FENCE = re.compile(r"^```(?:bash|sh|shell)\n(.*?)^```", re.MULTILINE | re.DOTALL)

# The scratch roots outside the working tree. `out/` is gitignored and inside it, which is the
# whole point: nothing there is ever committed and nothing there trips the sandbox.
# ANCHORED AT THE START OF A PATH, not merely at a slash. `out/<date>/tmp/site` is the correct
# answer to this rule and it contains the letters of the thing the rule forbids, so a pattern
# that matched a bare `/tmp` anywhere would flag the fix as the defect.
OUTSIDE = re.compile(
    r"""(?:^|[\s=:'"(])(/tmp|/var/tmp|/var/folders|~/\.cache)(?=[/\s"']|$)""")


def scratch_problems(root: Path = PROMPTS) -> list[str]:
    """Commands the routine tells a run to execute that write outside the working tree."""
    out = []
    for md in sorted(root.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        for fence in FENCE.finditer(text):
            base = text[:fence.start(1)].count("\n") + 1
            for i, line in enumerate(fence.group(1).splitlines()):
                if line.lstrip().startswith("#"):
                    continue
                hit = OUTSIDE.search(line)
                if hit:
                    out.append(f"{md.name}:{base + i} tells a run to write to "
                               f"{hit.group(1)}, which is outside the working tree. A "
                               f"sandboxed write there stops and asks, and an unattended run "
                               f"has nobody to answer. Use out/<date>/tmp/")
    return out


def problems(found: list[dict], docs: Path = DOCS) -> list[str]:
    """Every claim the published pages do not bear out."""
    out = []
    for c in found:
        html = page_text(c["path"], docs)
        if html is None:
            out.append(f'{c["file"]}:{c["line"]} points at {c["path"]}, which is not a built '
                       f"page; the claim cannot be checked and reads as though it were")
            continue
        present = c["text"] in html
        if c["kind"] == "onpage" and not present:
            out.append(f'{c["file"]}:{c["line"]} says {c["path"]} carries "{c["text"]}" and it '
                       f"does not; either the page changed or the instruction went stale, and "
                       f"a run reading it may put the copy back")
        if c["kind"] == "offpage" and present:
            out.append(f'{c["file"]}:{c["line"]} says {c["path"]} must not carry "{c["text"]}" '
                       f"and it does; copy removed on purpose has come back")
    return out


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    import tempfile                                                  # noqa: PLC0415
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        (root / "prompts").mkdir()
        (root / "docs" / "water").mkdir(parents=True)
        (root / "docs" / "water" / "index.html").write_text(
            "<html><main><p>storage over capacity</p></main></html>", encoding="utf-8")

        def write(body):
            (root / "prompts" / "r.md").write_text(body, encoding="utf-8")
            return claims(root / "prompts")

        c = write('<!-- onpage water/ "storage over capacity" -->')
        check("a marker is parsed off a prompt", len(c) == 1 and c[0]["kind"] == "onpage", str(c))
        check("a claim the page bears out reports nothing",
              problems(c, root / "docs") == [], str(problems(c, root / "docs")))

        # THE DEFECT, REPLAYED. The instruction describes copy the page no longer has.
        c = write('<!-- onpage water/ "a metro with no line is a gap" -->')
        p = problems(c, root / "docs")
        check("an instruction describing copy the page LOST is CAUGHT",
              any("went stale" in x for x in p), str(p))

        # THE OTHER HALF. Copy deleted on purpose, put back by a run.
        c = write('<!-- offpage water/ "storage over capacity" -->')
        p = problems(c, root / "docs")
        check("copy removed on purpose coming BACK is CAUGHT",
              any("come back" in x for x in p), str(p))

        c = write('<!-- offpage water/ "San Antonio has no line" -->')
        check("...and stays quiet while it is still gone",
              problems(c, root / "docs") == [], str(problems(c, root / "docs")))

        c = write('<!-- onpage nowhere/ "anything" -->')
        p = problems(c, root / "docs")
        check("a claim pointing at no built page is CAUGHT rather than skipped",
              any("not a built page" in x for x in p), str(p))

        check("prose with no marker makes no claim",
              write("The water page promises several things in ordinary prose.") == [])

        # ---------------------------------------------------------- THE SCRATCH RULE
        def fence(body):
            (root / "prompts" / "r.md").write_text(body, encoding="utf-8")
            return scratch_problems(root / "prompts")

        sp = fence("Build it.\n\n```bash\npython3 build.py --out /tmp/site\n```\n")
        check("a command writing to /tmp is CAUGHT",
              any("outside the working tree" in x for x in sp), str(sp))
        check("...and it is pointed at the line that does it",
              any(":4 " in x for x in sp), str(sp))

        # THE FIX IS NOT THE DEFECT. `out/<date>/tmp/site` is the correct answer and it carries
        # the letters of what the rule forbids, so this is the case that decides whether the
        # rule is a rule or a substring search.
        check("the correct scratch path is NOT flagged",
              fence("```bash\npython3 build.py --out out/<date>/tmp/site\n```\n") == [],
              str(fence("```bash\npython3 build.py --out out/<date>/tmp/site\n```\n")))

        # PROSE MAY NAME THE THING IT FORBIDS. A rule that could not tell an instruction from
        # an explanation would make its own reasoning unwritable, and the reasoning is the part
        # that survives a rewrite.
        check("prose explaining the rule is not an instruction",
              fence("Never write to /tmp. Use out/<date>/tmp/ instead.\n") == [])
        check("...and neither is a commented out line inside a fence",
              fence("```bash\n# do not do this: build.py --out /tmp/x\ntrue\n```\n") == [])

        for bad in ("/var/tmp/x", "/var/folders/z/q", "~/.cache/site"):
            sp = fence("```bash\npython3 build.py --out %s\n```\n" % bad)
            check(f"{bad} is caught too, since the law is about the tree and not the word tmp",
                  sp != [], str(sp))

        # AND THE COMMITTED ROUTINE, which is the only reason the six above matter. Two lines of
        # it said `--out /tmp/site` for the whole day after the law was written.
        check("the committed prompts keep their scratch inside the tree",
              not scratch_problems(), "; ".join(scratch_problems()))

    # AND THE COMMITTED PROMPTS, which is the only reason the rest of this matters.
    live = claims()
    check("the prompts carry at least one marked claim", bool(live), f"{len(live)} found")
    check("every marked claim holds against the published site", not problems(live),
          "; ".join(problems(live)[:3]))

    if failures:
        print(f"\nroutine_claims self-test: {failures} FAILED")
        return 1
    print("\nroutine_claims self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    found = claims()
    bad = problems(found) + scratch_problems()
    if bad:
        print("the routine is out of step with what it governs:", file=sys.stderr)
        for b in bad:
            print(f"  - {b}", file=sys.stderr)
        return 1
    on = sum(1 for c in found if c["kind"] == "onpage")
    print(f"routine claims ok: {on} on-page and {len(found) - on} off-page claim(s) hold, "
          f"and every command it gives keeps its scratch inside the tree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
