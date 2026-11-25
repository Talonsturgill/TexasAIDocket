#!/usr/bin/env python3
"""fig_inject.py — each slide carries the computed figures IT reads, and nothing else.

    python3 scripts/carousel/fig_inject.py --run out/2026-10-24            write
    python3 scripts/carousel/fig_inject.py --run out/2026-10-24 --check    exit 1 if any slide is stale
    python3 scripts/carousel/fig_inject.py --self-test

WHY THIS EXISTS (queue `make-slides-rewrites-every-frame`, weekly pass 2026-10-23).

Nos. 57 and 58 both read their numbers in frame code from `figures.json`, through one line per slide,
`<script>window.FIG = {...};</script>`, which is right: figure_bearing.py wants the value in the
drawing and the numeral law wants no typed figure. Each run wrote that line with its own improvised
script, and both wrote the WHOLE of figures.json into EVERY slide. So adding one figure for one
frame changed all nine slides' bytes, and the bytes are what the machine binds a review to:
`panel_ready` refuses a frame edited after its render, and `art_preflight` binds the three-frame art
review to each source's hash. No. 58 added a figure twice and twice threw away a bound art review
and re-rendered every frame (queue, 2026-10-23). No. 45 paid the same cost from a generator that
rewrote every slide on each run (queue, 2026-10-07). The defect is not the FIG line, it is a writer
whose output for slide 3 depends on what slide 7 needs.

WHAT IT DOES. For each `slides/slide-NN.html` it reads the names the slide's own code uses
(`FIG.name` or `FIG["name"]`), and writes a FIG line carrying exactly those figures, in
figures.json's order, with the value from each entry's `value`. A file is written only when its
bytes change, so a figure added for frame 7 touches frame 7 and no other. A slide that uses FIG
dynamically (`FIG[k]`, `Object.keys(FIG)`) can't be read statically and gets every figure, and the
tool says which slide that was. A name the slide reads that figures.json lacks is an error, never
an `undefined` drawn as nothing.

WHAT IT DOES NOT DO. It computes nothing and rounds nothing: the values are figures.json's, which
compute.py owns. `--check` is a tool a run calls before rendering, not a CI gate, and it is wired to
nothing in guards.yml; a check wired to nothing is the GATE_LESSONS shape, so this file claims no
more than that.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

LINE = re.compile(r"<script>\s*window\.FIG\s*=\s*.*?;?\s*</script>", re.S)
DOT = re.compile(r"(?<![\w$.])(?:window\.)?FIG\.([A-Za-z_$][\w$]*)")
KEY = re.compile(r"(?<![\w$.])(?:window\.)?FIG\[\s*(['\"])([^'\"]+)\1\s*\]")
# any other use of the bare object: FIG[k], Object.keys(FIG), f(FIG), const F = FIG
DYNAMIC = re.compile(r"(?<![\w$.])(?:window\.)?FIG(?!\s*\.[A-Za-z_$]|\s*\[\s*['\"]|[\w$])")


def figures(run: Path) -> dict:
    """figures.json as {name: value}, in file order. An entry is {"value": v, ...} or a bare value."""
    doc = json.loads((run / "figures.json").read_text(encoding="utf-8"))
    out = {}
    for name, entry in doc.items():
        if name.startswith("_"):
            continue
        out[name] = entry["value"] if isinstance(entry, dict) and "value" in entry else entry
    return out


def line_for(sub: dict) -> str:
    return "<script>window.FIG = " + json.dumps(sub) + ";</script>"


def blank_strings(code: str) -> tuple[str, list[bool]]:
    """(code with every string literal's TEXT blanked to spaces, a mask of which offsets were inside
    one). Quotes stay, offsets stay, and a template literal's `${...}` stays code.

    WHY (weekly machine pass 2026-11-24, queue `fig-inject-reads-string-literals-as-dynamic`,
    nos. 80 and 86). A message is not a read. No. 80's guards threw 'FIG says ' and
    'window.FIG is not the brief', and the DYNAMIC match took the bare FIG inside each string as a
    dynamic use, so eight slides were handed every figure and called stale at ship."""
    out, mask = list(code), [False] * len(code)
    i, n = 0, len(code)
    while i < n:
        c = code[i]
        if c in "'\"":
            j = i + 1
            while j < n and code[j] != c and code[j] != "\n":
                j += 2 if code[j] == "\\" else 1
            for k in range(i + 1, min(j, n)):
                out[k], mask[k] = " ", True
            i = j + 1
        elif c == "`":
            j, depth = i + 1, 0
            while j < n:
                if depth == 0 and code[j] == "`":
                    break
                if depth == 0 and code.startswith("${", j):
                    depth, j = 1, j + 2
                    continue
                if depth:
                    depth += {"{": 1, "}": -1}.get(code[j], 0)
                    j += 1
                    continue
                if code[j] == "\\":
                    out[j], mask[j] = " ", True
                    j += 1
                if j < n:
                    out[j], mask[j] = (" " if code[j] != "\n" else "\n"), True
                j += 1
            i = j + 1
        else:
            i += 1
    return "".join(out), mask


def plan(html: str, figs: dict, legacy_strings: bool = False) -> tuple[str, list[str], bool]:
    """(the slide's new text, problems, dynamic). The FIG line itself is not read for names.
    `legacy_strings` reads string literals as code, the way every deck through 2026-11-24 was
    written; shipped_check uses it only to tell an archived deck from a stale one."""
    # comments are not code: a note saying "the FIG line" must not read as a dynamic use
    code = re.sub(r"<!--.*?-->|/\*.*?\*/|(?:^|(?<=\s))//[^\n]*", "", LINE.sub("", html), flags=re.S)
    # and strings are not code either: a FIG named inside a message is never a read. FIG['name'] keeps
    # its key, because the KEY match runs on the real text wherever the FIG itself is outside a string.
    # Only inside <script> bodies: an apostrophe in a headline ("can't") is not a quote.
    bare, inside = code, [False] * len(code)
    for m in ([] if legacy_strings else re.finditer(r"(<script\b[^>]*>)(.*?)(</script>)", code, flags=re.S | re.I)):
        b, k = blank_strings(m.group(2))
        s = m.start(2)
        bare = bare[:s] + b + bare[s + len(b):]
        inside[s:s + len(k)] = k
    names = ({m.group(1) for m in DOT.finditer(bare)}
             | {m.group(2) for m in KEY.finditer(code) if not inside[m.start()]})
    dynamic = bool(DYNAMIC.search(bare))
    problems = [f"reads FIG.{n}, which figures.json does not carry" for n in sorted(names - set(figs))]
    if not names and not dynamic and not LINE.search(html):
        return html, problems, dynamic                       # no FIG at all: nothing to write
    sub = dict(figs) if dynamic else {k: v for k, v in figs.items() if k in names}
    new = line_for(sub)
    if LINE.search(html):
        text = LINE.sub(lambda _m: new, html, count=1)
    else:
        i = html.find('<script type="module">')
        if i < 0:
            problems.append("reads FIG but has no FIG line and no module script to put one before")
            return html, problems, dynamic
        text = html[:i] + new + "\n" + html[i:]
    return text, problems, dynamic


def run_dir(run: Path, write: bool, legacy_strings: bool = False) -> tuple[list[str], list[str], list[str]]:
    """(written or stale slide names, problems, notes)."""
    figs = figures(run)
    changed, problems, notes, written = [], [], [], []
    for p in sorted((run / "slides").glob("slide-*.html")):
        html = p.read_text(encoding="utf-8")
        text, probs, dynamic = plan(html, figs, legacy_strings)
        problems += [f"{p.name}: {x}" for x in probs]
        if dynamic:
            notes.append(f"{p.name}: uses FIG dynamically, so it carries every figure")
        if text != html:
            changed.append(p.name)
            if write and not probs:
                p.write_text(text, encoding="utf-8")
                written.append(p.name)
    return (written if write else changed), problems, notes


def self_test() -> int:
    fails = []

    def ok(label, cond, detail=""):
        print(("  ok    " if cond else "  FAIL  ") + label + ("" if cond else f"  {detail}"))
        if not cond:
            fails.append(label)

    def slide(code):
        return ('<!doctype html><html><body><script src="x.js"></script>\n'
                '<script>window.FIG = {};</script>\n<script type="module">\n' + code + "\n</script></body></html>\n")

    def legacy(run):
        # THE DEFECT, as nos. 57 and 58 wrote it: the whole of figures.json into every slide.
        line = line_for(figures(run))
        for p in sorted((run / "slides").glob("slide-*.html")):
            s = p.read_text()
            s2 = LINE.sub(lambda _m: line, s)
            if s2 != s:
                p.write_text(s2)

    with tempfile.TemporaryDirectory() as td:
        run = Path(td)
        (run / "slides").mkdir()
        (run / "figures.json").write_text(json.dumps(
            {"_note": "x", "visits": {"value": 17, "from": ["c19"]}, "months": {"value": 12}}))
        (run / "slides/slide-01.html").write_text(slide("const n = FIG.visits; draw(n);"))
        (run / "slides/slide-02.html").write_text(slide("const m = FIG['months']; draw(m);"))
        changed, probs, _ = run_dir(run, True)
        s1 = (run / "slides/slide-01.html").read_text()
        ok("each slide carries only what it reads", '"visits": 17' in s1 and "months" not in s1, s1)
        ok("a bracketed name is read too", '"months": 12' in (run / "slides/slide-02.html").read_text())
        again, _, _ = run_dir(run, True)
        ok("a second write changes nothing", again == [], str(again))

        # THE REPLAY. A figure added for slide 2 alone must leave slide 1's bytes alone.
        before = {p.name: p.read_bytes() for p in (run / "slides").glob("*.html")}
        doc = json.loads((run / "figures.json").read_text())
        doc["hours"] = {"value": 6}
        (run / "figures.json").write_text(json.dumps(doc))
        (run / "slides/slide-02.html").write_text(
            (run / "slides/slide-02.html").read_text().replace("draw(m);", "draw(m, FIG.hours);"))
        before["slide-02.html"] = (run / "slides/slide-02.html").read_bytes()
        changed, _, _ = run_dir(run, True)
        ok("adding a figure for slide 2 rewrites slide 2 only", changed == ["slide-02.html"], str(changed))
        ok("slide 1's bytes are untouched", (run / "slides/slide-01.html").read_bytes() == before["slide-01.html"])
        # and the old writer, run on the same state, would have changed slide 1: the test sees the defect
        legacy(run)
        ok("the whole-dict writer the runs used goes red on the same replay",
           (run / "slides/slide-01.html").read_bytes() != before["slide-01.html"])
        run_dir(run, True)
        ok("and this tool puts slide 1 back exactly", (run / "slides/slide-01.html").read_bytes() == before["slide-01.html"])

        # --check: a value changed in figures.json and not in the slide is stale
        doc["visits"]["value"] = 18
        (run / "figures.json").write_text(json.dumps(doc))
        stale, _, _ = run_dir(run, False)
        ok("a stale value is reported by --check", stale == ["slide-01.html"], str(stale))
        ok("--check writes nothing", '"visits": 17' in (run / "slides/slide-01.html").read_text())

        # a name figures.json lacks is an error and the slide is not written
        (run / "slides/slide-03.html").write_text(slide("draw(FIG.vistis);"))
        _, probs, _ = run_dir(run, True)
        ok("a name figures.json lacks fails", any("FIG.vistis" in p for p in probs), str(probs))
        ok("and that slide is left as it was", "window.FIG = {};" in (run / "slides/slide-03.html").read_text())
        (run / "slides/slide-03.html").unlink()

        # dynamic use can't be read statically, so it gets everything and says so
        (run / "slides/slide-04.html").write_text(slide("Object.keys(FIG).forEach(draw);"))
        _, probs, notes = run_dir(run, True)
        s4 = (run / "slides/slide-04.html").read_text()
        ok("a dynamic reader carries every figure", all(k in s4 for k in ("visits", "months", "hours")), s4)
        ok("and is named", any("slide-04" in n for n in notes), str(notes))
        # THE REPLAY of nos. 80 and 86 (weekly machine pass 2026-11-24): a guard whose MESSAGE
        # names FIG is not a dynamic read, so the slide carries what it reads by name and no more.
        (run / "slides/slide-06.html").write_text(slide(
            "if (FIG.visits == null) throw new Error('FIG says nothing; window.FIG is not the brief');\n"
            "const t = `${FIG.months} months, FIG as words`; draw(t, \"can't FIG\");"))
        _, _, notes = run_dir(run, True)
        s6 = (run / "slides/slide-06.html").read_text()
        ok("a throw message naming FIG is not a dynamic use",
           not any("slide-06" in n for n in notes), str(notes))
        ok("...so the slide carries only the names it reads, a template's ${FIG.x} among them",
           '"visits": 18' in s6 and '"months": 12' in s6 and "hours" not in s6, s6)
        # and the strip is what does the work: without it the same slide is called dynamic
        ok("the unstripped match the runs met goes red on the same text",
           bool(DYNAMIC.search(re.sub(r"<!--.*?-->|/\*.*?\*/", "", LINE.sub("", s6), flags=re.S))))
        # a bracketed key is a string and is still read; a real dynamic use beside a string still is one
        (run / "slides/slide-07.html").write_text(slide("draw(FIG['hours'], 'a note'); const all = Object.keys(FIG);"))
        _, _, notes = run_dir(run, True)
        ok("FIG['name'] is still read and Object.keys(FIG) beside a string is still dynamic",
           any("slide-07" in n for n in notes), str(notes))
        # an apostrophe in the page's own prose is not a quote that hides a read
        (run / "slides/slide-08.html").write_text(
            "<!doctype html><html><body><h1>It's dry</h1>\n<script>window.FIG = {};</script>\n"
            "<script type=\"module\">draw(FIG.hours);</script></body></html>\n")
        run_dir(run, True)
        ok("prose apostrophes outside a script do not swallow a read",
           '"hours": 6' in (run / "slides/slide-08.html").read_text())
        for k in ("06", "07", "08"):
            (run / f"slides/slide-{k}.html").unlink()

        # a slide with no FIG at all is never touched
        plain = '<!doctype html><html><body><script type="module">draw(3);</script></body></html>\n'
        (run / "slides/slide-05.html").write_text(plain)
        run_dir(run, True)
        ok("a slide without FIG is left alone", (run / "slides/slide-05.html").read_text() == plain)

    print(f"fig_inject self-test: {'PASS' if not fails else 'FAIL'} ({len(fails)} failed)")
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="the run directory holding figures.json and slides/")
    ap.add_argument("--check", action="store_true", help="report stale slides, write nothing")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if not a.run:
        ap.error("--run is required")
    run = Path(a.run)
    changed, problems, notes = run_dir(run, not a.check)
    for n in notes:
        print("note:", n)
    for p in problems:
        print("FAIL:", p)
    if a.check:
        for c in changed:
            print("STALE:", c, "carries a FIG line that is not what it reads from figures.json")
        print(f"fig_inject --check: {'ok' if not changed and not problems else 'stale'}, "
              f"{len(changed)} stale slide(s)")
        return 1 if changed or problems else 0
    print(f"fig_inject: {len(changed)} slide(s) written"
          + (f", {len(problems)} problem(s), nothing written for those slides" if problems else ""))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
