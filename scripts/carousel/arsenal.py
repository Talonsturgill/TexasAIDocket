#!/usr/bin/env python3
"""arsenal.py — writes knowledge/carousel/ARSENAL.md, the inventory of everything a run has.

WHY THIS EXISTS (2026-09-24)

The owner's words: the master prompt "needs to be a little bit more robust so that it knows like
all the tools and things that it actually has at its disposal." A run met its tools phase by phase,
scattered over eighteen hundred lines of `prompts/daily_routine.md`, and improvised whatever it did
not know existed. Carousel after carousel modelled a capsule person and a box house from primitives
against a deadline, while a render engine with a sky, a ground, contact shadows and weathering sat
one import away, and a kit of true-scale Texas models was being written beside it.

A hand-written inventory would be the defect this repo keeps meeting, a rule stated in one place
and a surface keeping its own copy with nothing checking they agree (GATE_LESSONS' oldest shape).
So nothing in ARSENAL.md is typed. Every row is READ from the thing it describes:

  the engine     every `TXT.<name> = function` in assets/js/txthree.js, its doc comment and
                 signature, plus the world presets, rigs, materials, surfaces and scatter kinds
  the kit        assets/js/txkit.js's helpers and every model registered by `K.define` (or a local
                 wrapper around it) in assets/js/kit/*.js, with size, options and note
  the libraries  each assets/js/*.js header sentence, its global and its public API, the layout
                 table, the 2.5D object catalogue, the geodata and the fonts
  the tools      scripts/carousel, scripts/shared and the engine skill, with docstring line, CLI
                 flags and how each is wired (CI, gate table, shipped registry, routine phases),
                 plus every record and site tool the routine names
  the people     .claude/agents and .claude/skills frontmatter
  the doctrine   knowledge/carousel and knowledge/shared first heading and first sentence
  the examples   examples/*/, and the connectors and services the routine text names

Re-running it picks up whatever landed since: a new kit model, a new gate, a new world preset.

    arsenal.py              write knowledge/carousel/ARSENAL.md
    arsenal.py --check      exit 1 if the committed file differs from a fresh build
    arsenal.py --stdout     print the build instead of writing it
    arsenal.py --self-test  prove the parsers on fixtures and that --check catches drift

Exit 0 clean, 1 drift (or a self-test assertion failed), 2 the builder could not run.
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_REL = "knowledge/carousel/ARSENAL.md"

# ------------------------------------------------------------------------------ text hygiene

_EMOJI = re.compile("[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F900-\U0001F9FF️]")


def clean(s: str) -> str:
    """One line, table safe, house clean: no em or en dash, no emoji, no pipe."""
    s = re.sub(r"(\d)\s*[\u2013\u2014]\s*(\d)", r"\1 to \2", s)
    s = re.sub(r"\s*[\u2013\u2014]+\s*", ", ", s)
    s = _EMOJI.sub("", s)
    s = s.replace("‘", "'").replace("’", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"\s+", " ", s).strip()
    # port_audit's residue rule keeps the upstream product's name out of this repo outside a few
    # lineage records. Some sources quoted here are those records, so the inventory says "sibling"
    s = re.sub(r"\bAlaska(?:'s)?\b", lambda m: "the sibling's" if m.group(0).endswith("'s") else "the sibling", s)
    s = re.sub(r"\bthe the sibling", "the sibling", s)
    return s.replace("|", "\\|")


def first_sentence(text: str, limit: int = 200) -> str:
    """The first sentence of a prose block, clipped at a word boundary."""
    t = re.sub(r"\s+", " ", text or "").strip()
    t = t.replace("**", "")
    m = re.search(r"(.+?[.!?])(?=\s+[A-Z`(\"'*]|\s*$)", t)
    s = m.group(1) if m else t
    if len(s) > limit:
        s = s[:limit].rsplit(" ", 1)[0].rstrip(",;:") + " ..."
    return clean(s)


def strip_name_prefix(s: str) -> str:
    """'txdeck.js \u2014 the deck chassis' -> 'the deck chassis'."""
    return re.sub(r"^\s*[\w./-]+\.(?:js|py|sh|md)\s*(?:[\u2013\u2014]+|-{1,2}|:|,|\.(?=\s))\s*", "", s)


# ------------------------------------------------------------------------------ JS scanning

def skip_string(src: str, i: int) -> int:
    """Index just past the string literal opening at src[i]."""
    q = src[i]
    i += 1
    while i < len(src):
        c = src[i]
        if c == "\\":
            i += 2
            continue
        if c == q:
            return i + 1
        if q == "`" and c == "$" and src.startswith("${", i):
            i = match_close(src, i + 1) + 1
            continue
        i += 1
    return i


def match_close(src: str, i: int) -> int:
    """Index of the bracket closing the one at src[i], skipping strings and comments."""
    pairs = {"{": "}", "[": "]", "(": ")"}
    stack = [pairs[src[i]]]
    i += 1
    while i < len(src) and stack:
        c = src[i]
        if c in "'\"`":
            i = skip_string(src, i)
            continue
        if src.startswith("//", i):
            j = src.find("\n", i)
            i = len(src) if j < 0 else j
            continue
        if src.startswith("/*", i):
            j = src.find("*/", i + 2)
            i = len(src) if j < 0 else j + 2
            continue
        if c in pairs:
            stack.append(pairs[c])
        elif stack and c == stack[-1]:
            stack.pop()
            if not stack:
                return i
        i += 1
    return len(src) - 1


def top_level_entries(obj: str) -> list[tuple[str, str, str]]:
    """(key, value source, trailing comment on the key's line) for an object literal body.

    `obj` is the text between the braces. Handles `key: value`, `'key': value`, shorthand
    methods `key(a, b) { ... }` and trailing `// comment` after the opening of a value.
    """
    out = []
    i, n = 0, len(obj)
    while i < n:
        m = re.compile(r"\s*(?://[^\n]*(?:\n|$)\s*|/\*[\s\S]*?\*/\s*)*").match(obj, i)
        i = m.end()
        if i >= n:
            break
        km = re.compile(r"""(?:(['"])([\w$-]+)\1|([A-Za-z_$][\w$]*))\s*(:|\()""").match(obj, i)
        sh = re.compile(r"([A-Za-z_$][\w$]*)\s*(?:,|$)").match(obj, i)
        if not km and sh:            # shorthand `{ people, homes }`
            out.append((sh.group(1), sh.group(1), ""))
            i = sh.end()
            continue
        if not km:
            # a spread or something unparseable: skip to the next top-level comma
            j = i
            while j < n and obj[j] != ",":
                j = match_close(obj, j) + 1 if obj[j] in "{[(" else (
                    skip_string(obj, j) if obj[j] in "'\"`" else j + 1)
            i = j + 1
            continue
        key = km.group(2) or km.group(3)
        j = km.end()
        if km.group(4) == "(":
            j = match_close(obj, j - 1) + 1
        start = j
        while j < n and obj[j] != ",":
            c = obj[j]
            if c in "{[(":
                j = match_close(obj, j) + 1
            elif c in "'\"`":
                j = skip_string(obj, j)
            elif obj.startswith("//", j):
                k = obj.find("\n", j)
                j = n if k < 0 else k
            elif obj.startswith("/*", j):
                k = obj.find("*/", j + 2)
                j = n if k < 0 else k + 2
            else:
                j += 1
        value = obj[start:j].strip()
        line_end = obj.find("\n", km.start())
        line = obj[km.start():line_end if line_end >= 0 else n]
        cm = re.search(r"//\s*(.*)$", line)
        # a `//` inside a string (a URL) is not a comment, so only a quote-free prefix counts
        comment = cm.group(1).strip() if cm and not re.search(r"['\"`]", line[:cm.start()]) else ""
        out.append((key, value, comment))
        i = j + 1
    return out


def object_after(src: str, pattern: str) -> str | None:
    """Body of the object literal opening right after `pattern` (a regex ending before '{')."""
    m = re.search(pattern + r"\s*\{", src)
    if not m:
        return None
    o = m.end() - 1
    return src[o + 1:match_close(src, o)]


def js_string_value(v: str) -> str:
    """Decode a JS string literal, or string concatenation of literals, into text."""
    parts = re.findall(r"""'((?:\\.|[^'\\])*)'|"((?:\\.|[^"\\])*)"|`((?:\\.|[^`\\])*)`""", v)
    if not parts:
        return v.strip()
    return "".join(a or b or c for a, b, c in parts).replace("\\'", "'").replace('\\"', '"')


def comment_above(lines: list[str], idx: int) -> str:
    """The comment block ending on the line directly above lines[idx], banners removed."""
    got: list[str] = []
    j = idx - 1
    if j >= 0 and lines[j].rstrip().endswith("*/"):
        block = []
        while j >= 0:
            block.insert(0, lines[j])
            if "/*" in lines[j]:
                break
            j -= 1
        text = "\n".join(block)
        text = re.sub(r"/\*+|\*+/", " ", text)
        text = re.sub(r"^\s*\*\s?", "", text, flags=re.M)
        got.append(text)
    else:
        while j >= 0 and lines[j].strip().startswith("//"):
            got.insert(0, lines[j].strip()[2:])
            j -= 1
    text = "\n".join(got)
    banner = re.search(r"-{3,}\s*([^\n]*?)\s*-{3,}", text)
    text = re.sub(r"-{3,}[^\n]*?-{3,}|={3,}", " ", text).strip()   # section banners
    # A banner alone directly above a definition is that definition's one line of doc.
    return text or (banner.group(1).strip() if banner else "")


# ------------------------------------------------------------------------------ the engine

def block_comments(src: str) -> list[tuple[int, str, str]]:
    """(offset, banner title, body) for every /* */ comment, the body de-starred."""
    out = []
    for m in re.finditer(r"/\*([\s\S]*?)\*/", src):
        raw = m.group(1)
        title = ""
        bm = re.match(r"\s*-{2,}\s*(.*?)\s*-{3,}", raw)
        if bm:
            title = bm.group(1).strip()
            raw = raw[bm.end():]
        body = re.sub(r"^\s*\*\s?", "", raw, flags=re.M).strip()
        out.append((m.start(), title, body))
    return out


def engine_doc(name: str, adjacent: str, comments, offset: int) -> str:
    """The doc for TXT.<name>, in order of trust.

    1. The comment directly above the definition, when it carries the signature.
    2. Any block comment that OPENS with `TXT.<name>(`, the engine's own convention for a doc
       that sits above a private helper rather than the public function (ground, scatter).
    3. The adjacent comment, whatever it says.
    4. The nearest preceding section banner named for the function ("contact shadow: ...").
    """
    if re.search(r"TXT\." + name + r"\(", adjacent):
        return adjacent
    for _, _, body in comments:
        if body.startswith(f"TXT.{name}("):
            return body
    if adjacent:
        return adjacent
    best = ""
    for off, title, body in comments:
        if off > offset:
            break
        word = re.sub(r"[^a-z]", "", (title.split() or [""])[0].lower())
        if title and word == name.lower():
            best = body or title
    return best


def parse_engine(src: str) -> dict:
    lines = src.split("\n")
    comments = block_comments(src)
    starts = [0]
    for line in lines:
        starts.append(starts[-1] + len(line) + 1)
    fns: dict[str, dict] = {}
    rx = re.compile(r"^\s*TXT\.(\w+)\s*=\s*(async\s+)?function\s*\(([^)]*)\)")
    for idx, line in enumerate(lines):
        m = rx.match(line)
        if not m:
            continue
        name, params = m.group(1), re.sub(r"\s+", " ", m.group(3).strip())
        doc = engine_doc(name, comment_above(lines, idx), comments, starts[idx])
        sig = f"TXT.{name}({params})"
        sm = re.search(r"TXT\." + name + r"\(", doc)
        if sm:
            close = match_close(doc, sm.end() - 1)
            sig = re.sub(r"\s+", " ", doc[sm.start():close + 1])
            doc = (doc[:sm.start()] + doc[close + 1:]).strip()
            doc = re.sub(r"^\s*(?:[\u2013\u2014]+|-{1,2}|:)\s*", "", doc)
        entry = {"name": name, "sig": clean(sig), "async": bool(m.group(2)),
                 "doc": first_sentence(doc, 220) if doc else "", "line": idx + 1}
        if name in fns:
            entry["redefined"] = True
            if not entry["doc"]:
                entry["doc"] = fns[name]["doc"]
        fns[name] = entry

    def keys(pattern: str) -> list[tuple[str, str, str]]:
        body = object_after(src, pattern)
        return top_level_entries(body) if body is not None else []

    worlds = [(k, clean(c)) for k, _, c in keys(r"TXT\.worlds\s*=")]
    rigs = [(k, clean(c)) for k, _, c in keys(r"TXT\.rigs\s*=")]
    mats = []
    for k, v, _ in keys(r"TXT\.mat\s*="):
        pm = re.match(r"\(([^)]*)\)\s*=>", v) or re.match(r"function\s*\(([^)]*)\)", v)
        mats.append((k, f"TXT.mat.{k}({pm.group(1).strip() if pm else ''})"))
    surfaces = [k for k, _, _ in keys(r"(?:const|let|var)\s+SURFACES\s*=")]
    scatter = []
    sm = re.search(r"TXT\.scatter\s*=\s*function\s*\([^)]*\)\s*\{", src)
    if sm:
        body = src[sm.end():match_close(src, sm.end() - 1)]
        kinds = set(re.findall(r"kind\s*===?\s*['\"](\w+)['\"]", body))
        for _, _, cbody in comments:
            if cbody.startswith("TXT.scatter("):
                km = re.search(r"kind\s*:\s*((?:'\w+'\s*\|?\s*)+)", cbody)
                if km:
                    kinds.update(re.findall(r"'(\w+)'", km.group(1)))
        scatter = sorted(kinds)
    # THE ENGINE'S OWN RECIPE, quoted rather than retyped: the indented code under the comment
    # line that opens "USAGE, the whole stage".
    recipe: list[str] = []
    for i, line in enumerate(lines):
        if re.match(r"\s*\*\s*USAGE, the whole stage", line):
            for nxt in lines[i + 1:]:
                if not re.match(r"\s*\*(\s|$)", nxt) or re.match(r"\s*\*\s*$", nxt) and recipe:
                    break
                body = re.sub(r"^\s*\*\s?", "", nxt)
                if body.strip():
                    recipe.append(body.rstrip())
            break
    if recipe:
        pad = min(len(r) - len(r.lstrip()) for r in recipe)
        recipe = [clean_code(r[pad:]) for r in recipe]
    return {"functions": sorted(fns.values(), key=lambda e: e["name"].lower()),
            "worlds": worlds, "rigs": rigs, "mats": mats, "surfaces": surfaces,
            "scatter": scatter, "recipe": recipe}


def clean_code(s: str) -> str:
    """A code line keeps its spacing, loses only what the house forbids."""
    s = re.sub(r"\s*[\u2013\u2014]+\s*", ", ", s)
    return _EMOJI.sub("", s)


# ------------------------------------------------------------------------------ the kit

def parse_size(v: str) -> str:
    nums = re.findall(r"-?\d+(?:\.\d+)?", v)
    return " x ".join(nums) if nums and v.strip().startswith("[") else clean(v)


def parse_kit_family(src: str) -> tuple[list[dict], int]:
    """Every model a family file registers, and the count of definitions it could not read."""
    definers = {"K.define"}
    for m in re.finditer(r"function\s+(\w+)\s*\(\s*(\w+)\s*,\s*\w+\s*\)\s*\{", src):
        body = src[m.end():match_close(src, m.end() - 1)]
        if re.search(r"K\.define\(\s*" + re.escape(m.group(2)) + r"\b", body):
            definers.add(m.group(1))
    for m in re.finditer(r"(?:const|let|var)\s+(\w+)\s*=\s*\(\s*(\w+)\s*,\s*\w+\s*\)\s*=>", src):
        tail = src[m.end():m.end() + 400]
        if re.search(r"K\.define\(\s*" + re.escape(m.group(2)) + r"\b", tail):
            definers.add(m.group(1))
    alt = "|".join(re.escape(d) for d in sorted(definers))
    call = re.compile(r"(?<![\w.$])(?<!function )(" + alt + r")\(\s*(['\"])([\w-]+)\2\s*,\s*\{")
    models = []
    for m in call.finditer(src):
        o = m.end() - 1
        spec = top_level_entries(src[o + 1:match_close(src, o)])
        d = {k: v for k, v, _ in spec}
        opts = d.get("options", "")
        if opts.startswith("{"):
            okeys = [k for k, _, _ in top_level_entries(opts[1:-1])]
            okeys = [k for k in okeys if k != "seed"]
            options = ", ".join(okeys)
        else:
            options = clean(opts) if opts else ""
        models.append({
            "name": m.group(3),
            "size": parse_size(d.get("size", "")) if "size" in d else "?",
            "options": options,
            "note": first_sentence(js_string_value(d["note"]), 260) if "note" in d else "",
            "family": js_string_value(d["family"]) if "family" in d else "",
        })
    literal = len(call.findall(src))
    all_calls = len(re.findall(r"(?<![\w.$])K\.define\(", src))
    wrapper_bodies = sum(1 for w in definers - {"K.define"}
                         for _ in re.finditer(r"function\s+" + re.escape(w) + r"\s*\(", src))
    wrapper_bodies += sum(1 for w in definers - {"K.define"}
                          for _ in re.finditer(r"(?:const|let|var)\s+" + re.escape(w) + r"\s*=", src))
    literal_direct = len(re.findall(r"(?<![\w.$])K\.define\(\s*['\"]", src))
    dynamic = max(0, all_calls - literal_direct - wrapper_bodies)
    del literal
    return models, dynamic


def kit_helpers(src: str, fam_srcs: dict) -> list[dict]:
    """Every public K.* helper a chassis can call.

    Three shapes, because a helper table missing one of them tells a chassis the primitive does
    not exist and it reimplements it: `K.x = function (...)` in txkit.js, the members of an
    object namespace such as `K.finish = { name: (args) => ... }`, and helpers a family module
    installs (`K.loft = K.loft || loft;` in people.js), signed from that module's own function.
    """
    lines = src.split("\n")
    helpers = []
    for idx, line in enumerate(lines):
        m = re.match(r"^\s*K\.(\w+)\s*=\s*function\s*\(([^)]*)\)", line)
        if m:
            doc = comment_above(lines, idx)
            helpers.append({"sig": clean(f"K.{m.group(1)}({m.group(2).strip()})"),
                            "doc": first_sentence(doc, 160) if doc else ""})
    for ns in re.finditer(r"^\s*K\.(\w+)\s*=\s*\{", src, re.M):
        body = object_after(src[ns.start():], r"K\.%s\s*=" % ns.group(1))
        for name, val, _ in top_level_entries(body or ""):
            am = re.match(r"\s*\(([^)]*)\)\s*=>", val)
            if am:
                helpers.append({"sig": clean(f"K.{ns.group(1)}.{name}({am.group(1).strip()})"),
                                "doc": f"a named finish in the K.{ns.group(1)} namespace"})
    for fam, fsrc in fam_srcs.items():
        flines = fsrc.split("\n")
        for m in re.finditer(r"^\s*K\.(\w+)\s*=\s*K\.\1\s*\|\|\s*(\w+)\s*;", fsrc, re.M):
            fn = re.search(r"^\s*function\s+%s\s*\(([^)]*)\)" % m.group(2), fsrc, re.M)
            args = fn.group(1).strip() if fn else ""
            doc = ""
            if fn:
                doc = comment_above(flines, fsrc[:fn.start()].count("\n") + (1 if fsrc[fn.start()] == "\n" else 0))
            helpers.append({"sig": clean(f"K.{m.group(1)}({args})"),
                            "doc": clean(f"installed by kit/{fam}.js" + (". " + first_sentence(doc, 140) if doc else ""))})
    return helpers


def parse_kit(root: Path) -> dict:
    kit_js = root / "assets/js/txkit.js"
    if not kit_js.exists():
        return {"helpers": [], "families": [], "header": ""}
    src = kit_js.read_text(encoding="utf-8")
    header = ""
    hm = re.match(r"\s*/\*(.*?)\*/", src, re.S)
    if hm:
        header = first_sentence(strip_name_prefix(re.sub(r"^\s*\*\s?", "", hm.group(1), flags=re.M)))
    fam_srcs = {p.stem: p.read_text(encoding="utf-8", errors="replace")
                for p in sorted((root / "assets/js/kit").glob("*.js"))}
    helpers = kit_helpers(src, fam_srcs)
    order = []
    fam = object_after(src, r"const\s+FAMILIES\s*=")
    if fam is not None:
        order = [k for k, _, _ in top_level_entries(fam)]
    files = {p.stem: p for p in sorted((root / "assets/js/kit").glob("*.js"))}
    names = order + sorted(k for k in files if k not in order)
    families = []
    for name in names:
        p = files.get(name)
        if not p:
            families.append({"family": name, "file": None, "summary": "", "models": [],
                             "dynamic": 0})
            continue
        fsrc = p.read_text(encoding="utf-8", errors="replace")
        summary = ""
        fm = re.match(r"\s*/\*(.*?)\*/", fsrc, re.S)
        if fm:
            text = strip_name_prefix(re.sub(r"^\s*\*\s?", "", fm.group(1), flags=re.M))
            # the boilerplate pointer back to txkit.js is not a summary, the paragraph after it is
            text = re.sub(r"^\s*,?\s*see assets/js/txkit\.js for the conventions\.\s*", "", text,
                          flags=re.I)
            summary = first_sentence(text, 200)
        models, dynamic = parse_kit_family(fsrc)
        families.append({"family": name, "file": p.relative_to(root).as_posix(),
                         "summary": summary, "models": sorted(models, key=lambda m: m["name"]),
                         "dynamic": dynamic, "imported": name in order})
    return {"helpers": helpers, "families": families, "header": header}


# ------------------------------------------------------------------------------ libraries

VENDORED = {"d3.v7.min.js", "three.module.min.js", "topojson-client.min.js", "zdog.min.js"}
COVERED = {"txthree.js", "txkit.js"}


def js_header(src: str) -> str:
    m = re.match(r"\s*/\*!?(.*?)\*/", src, re.S)
    if m:
        body = re.sub(r"^\s*\*\s?", "", m.group(1), flags=re.M).strip()
        body = re.sub(r"^@license\s*", "", body)
        return first_sentence(strip_name_prefix(body), 200)
    m = re.match(r"\s*//\s*(.*)", src)
    return clean(m.group(1)) if m else ""


def library_api(src: str) -> tuple[str, list[str]]:
    """The global a library exposes and the names on it."""
    shared = re.search(r"(?:var|const|let)\s+(\w+)\s*=\s*global\.(\w+)\s*\|\|", src)
    g = re.search(r"\bglobal\.(\w+)\s*=\s*(\w+|\{)", src)
    if shared:                      # `var TX = global.TX || (global.TX = {})`, a shared namespace
        name, var = shared.group(2), shared.group(1)
    elif g:
        name, var = g.group(1), g.group(2)
    else:
        return "", []
    api: set[str] = set()
    if var == "{":
        body = src[g.end():match_close(src, g.end() - 1)]
        api.update(k for k, _, _ in top_level_entries(body))
    else:
        api.update(re.findall(r"(?<![\w.$])" + re.escape(var) + r"\.([A-Za-z]\w*)\s*=(?!=)", src))
        body = object_after(src, r"(?:var|const|let)\s+" + re.escape(var) + r"\s*=")
        if body is not None:
            api.update(k for k, _, _ in top_level_entries(body))
    return name, sorted((a for a in api if not a.startswith("_")), key=str.lower)


def parse_libraries(root: Path) -> list[dict]:
    out = []
    for p in sorted((root / "assets/js").glob("*.js")):
        if p.name in COVERED:
            continue
        src = p.read_text(encoding="utf-8", errors="replace")
        head = js_header(src)
        if p.name in VENDORED:
            out.append({"file": p.name, "global": "", "api": [], "summary": head,
                        "vendored": True})
            continue
        gname, api = library_api(src)
        out.append({"file": p.name, "global": gname, "api": api, "summary": head,
                    "vendored": False})
    return out


def parse_layout(root: Path) -> dict:
    p = root / "assets/js/txlayout.js"
    if not p.exists():
        return {}
    src = p.read_text(encoding="utf-8")
    got = {}
    for key in ("ARCHETYPES", "DEVICES", "ROTATION"):
        m = re.search(r"var\s+" + key + r"\s*=\s*(\[[^\n]*?\]|\{[^\n]*?\});", src)
        if m:
            try:
                got[key] = json.loads(m.group(1))
            except ValueError:
                got[key] = clean(m.group(1))
    return got


def parse_objects(root: Path) -> list[tuple[str, str]]:
    p = root / "assets/js/txobjects.js"
    if not p.exists():
        return []
    src = p.read_text(encoding="utf-8")
    out = []
    for m in re.finditer(r"^\s*R\.(\w+)\s*=\s*\{\s*size:\s*(\[[^\]]*\])", src, re.M):
        out.append((m.group(1), parse_size(m.group(2))))
    return sorted(out)


def parse_geo(root: Path) -> list[tuple[str, str]]:
    out = []
    for p in sorted((root / "assets/geo").glob("*")):
        if not p.is_file():
            continue
        kb = max(1, round(p.stat().st_size / 1024))
        desc = ""
        if p.suffix == ".json":
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
                if isinstance(d, dict) and d.get("type") == "Topology":
                    objs = d.get("objects", {})
                    desc = "TopoJSON, objects " + ", ".join(
                        f"{k} ({len(v.get('geometries', []))})" for k, v in sorted(objs.items()))
                elif isinstance(d, dict) and d.get("type") == "FeatureCollection":
                    desc = f"GeoJSON, {len(d.get('features', []))} features"
                elif isinstance(d, dict):
                    ks = sorted(d.keys())
                    desc = "keys " + ", ".join(ks[:8]) + (" ..." if len(ks) > 8 else "")
                elif isinstance(d, list):
                    desc = f"list of {len(d)}"
            except ValueError:
                desc = "unparseable JSON"
        out.append((p.name, f"{kb:,} KB, {desc}" if desc else f"{kb:,} KB"))
    return out


def parse_fonts(root: Path) -> tuple[list[str], list[str]]:
    d = root / "assets/fonts"
    files = sorted(p.name for p in d.glob("*") if p.is_file() and p.suffix in (".ttf", ".otf", ".woff2", ".woff"))
    fams: set[str] = set()
    css = d / "fonts.css"
    if css.exists():
        fams.update(re.findall(r"font-family:\s*['\"]?([^;'\"]+)['\"]?\s*;", css.read_text(encoding="utf-8")))
    return files, sorted(fams)


# ------------------------------------------------------------------------------ tools

def py_doc_line(src: str) -> str:
    try:
        doc = ast.get_docstring(ast.parse(src)) or ""
    except SyntaxError:
        m = re.search(r'"""(.*?)"""', src, re.S)
        doc = m.group(1) if m else ""
    line = doc.strip().split("\n\n")[0] if doc else ""
    return first_sentence(strip_name_prefix(line), 200)


def sh_doc_line(src: str) -> str:
    for line in src.split("\n")[1:12]:
        if line.startswith("#") and line.strip("# ").strip():
            return first_sentence(strip_name_prefix(line.lstrip("# ")), 200)
    return ""


def cli_flags(src: str) -> list[str]:
    """Flags from the CODE, never from a string that merely looks like code.

    Read through the AST, so a fixture inside a self-test (this file carries one) is not
    mistaken for the tool's own interface. `add_argument("--a", "-b")` gives the long form,
    a positional gives `<name>`, and `"--x" in sys.argv` counts as a flag too.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    flags: list[str] = []

    def add(f: str) -> None:
        if f not in flags:
            flags.append(f)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "add_argument":
            names = [a.value for a in node.args
                     if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if not names:
                continue
            longs = [n for n in names if n.startswith("--")]
            add(longs[0] if longs else (names[0] if names[0].startswith("-") else f"<{names[0]}>"))
        elif isinstance(node, ast.Compare) and isinstance(node.left, ast.Constant) \
                and isinstance(node.left.value, str) and node.left.value.startswith("--") \
                and "argv" in ast.dump(node):
            add(node.left.value)
    return flags


_STOP = {"the", "what", "how", "a", "this", "and", "in", "is", "it", "of", "run", "ends",
         "turn"}


def routine_sections(text: str) -> list[tuple[int, str]]:
    """(line number, short label) for every `## ` heading of the routine."""
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        m = re.match(r"^##\s+PHASE\s+([\w.]+)", line)
        if m:
            out.append((i, m.group(1)))
            continue
        m = re.match(r"^##\s+(.+)", line)
        if m:
            words = [w for w in re.sub(r"[^A-Za-z ]", "", m.group(1).split(",")[0].split("(")[0])
                     .lower().split() if w not in _STOP]
            out.append((i, words[0] if words else "top"))
    return out


def section_of(sections: list[tuple[int, str]], line: int) -> str:
    label = "top"
    for start, lab in sections:
        if start <= line:
            label = lab
        else:
            break
    return label


def phases_naming(routine: str, sections, needle: str) -> list[str]:
    got: list[str] = []
    stem = needle.rsplit(".", 1)[0]
    # `scripts/carousel/x.py`, `x.py`, or the bare name in backticks (`layout_check --require`)
    # A bare one-word name (`sky`, `og`) is ordinary vocabulary, so it counts only with a flag.
    bare = r"|`" + re.escape(stem) + (r"[` ]" if "_" in stem else r" --")
    rx = re.compile(r"(?<![\w])" + re.escape(needle) + r"(?![\w])" + bare)
    for i, line in enumerate(routine.split("\n"), 1):
        if rx.search(line):
            lab = section_of(sections, i)
            if lab not in got:
                got.append(lab)
    return got


def ci_wiring(guards: str, rel: str) -> str:
    lines = [l for l in guards.split("\n") if rel in l]
    if not lines:
        return ""
    if any("--self-test" not in l for l in lines):
        return "run"
    return "self-test"


def mentions(src: str, stem: str) -> bool:
    return bool(re.search(r"\b" + re.escape(stem) + r"\.py\b|import\s+" + re.escape(stem)
                          + r"\b|['\"]" + re.escape(stem) + r"['\"]", src))


def parse_tools(root: Path, dirs: list[str], routine: str, guards: str,
                gate_status: str, shipped: str, only_named: bool = False) -> list[dict]:
    sections = routine_sections(routine)
    out = []
    for d in dirs:
        for p in sorted((root / d).glob("*")):
            if p.suffix not in (".py", ".sh") or p.name.startswith("_"):
                continue
            rel = p.relative_to(root).as_posix()
            src = p.read_text(encoding="utf-8", errors="replace")
            phases = phases_naming(routine, sections, p.name)
            if only_named and not phases:
                continue
            doc = py_doc_line(src) if p.suffix == ".py" else sh_doc_line(src)
            flags = cli_flags(src) if p.suffix == ".py" else []
            wired = []
            ci = ci_wiring(guards, rel)
            if ci:
                wired.append("CI" if ci == "run" else "CI self-test")
            if p.stem != "gate_status" and mentions(gate_status, p.stem):
                wired.append("gate table")
            if p.stem != "shipped_check" and mentions(shipped, p.stem):
                wired.append("shipped")
            out.append({"path": rel, "doc": doc, "flags": flags, "wired": wired,
                        "phases": phases})
    return out


# ------------------------------------------------------------------------------ people, doctrine

def frontmatter(text: str) -> dict:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).split("\n"):
        km = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if km:
            out[km.group(1)] = km.group(2).strip().strip("'\"")
    return out


def parse_agents(root: Path) -> list[dict]:
    out = []
    for p in sorted((root / ".claude/agents").glob("*.md")):
        fm = frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        out.append({"name": fm.get("name", p.stem), "tools": clean(fm.get("tools", "inherits")),
                    "model": clean(fm.get("model", "")),
                    "desc": first_sentence(fm.get("description", ""), 260)})
    return out


def parse_skills(root: Path) -> list[dict]:
    out = []
    for p in sorted((root / ".claude/skills").glob("*/SKILL.md")):
        fm = frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        out.append({"name": fm.get("name", p.parent.name),
                    "path": p.relative_to(root).as_posix(),
                    "desc": first_sentence(fm.get("description", ""), 260)})
    return out


def md_head(text: str) -> tuple[str, str]:
    heading, para, started = "", [], False
    in_fence = False
    for line in text.split("\n"):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not heading and line.startswith("#"):
            heading = line.lstrip("#").strip()
            continue
        if line.strip().startswith(("#", "|", "<!--", "---", ">")) and not started:
            continue
        if line.strip():
            started = True
            para.append(line.strip())
        elif started:
            break
    text = " ".join(para)
    first = first_sentence(text, 220)
    if len(first) < 48:             # "Compiled 2026-08-11." says when, not what
        rest = re.sub(r"\s+", " ", text.replace("**", "")).strip()[len(first.replace("\\|", "|")):]
        more = first_sentence(rest, 200) if rest.strip() else ""
        first = (first + " " + more).strip()
    return clean(heading), first


def parse_knowledge(root: Path) -> list[dict]:
    out = []
    for d in ("knowledge/carousel", "knowledge/shared"):
        for p in sorted((root / d).glob("*.md")):
            rel = p.relative_to(root).as_posix()
            if rel == OUT_REL:
                continue
            h, s = md_head(p.read_text(encoding="utf-8", errors="replace"))
            out.append({"path": rel, "heading": h, "first": s})
    return out


def parse_examples(root: Path) -> list[dict]:
    out = []
    for d in sorted(p for p in (root / "examples").glob("*") if p.is_dir()):
        summary = ""
        readme = d / "README.md"
        build = d / "build.py"
        board = d / "storyboard.md"
        if readme.exists():
            h, s = md_head(readme.read_text(encoding="utf-8", errors="replace"))
            summary = h + (". " + s if s else "")
        elif build.exists():
            summary = py_doc_line(build.read_text(encoding="utf-8", errors="replace"))
        elif board.exists():
            summary = md_head(board.read_text(encoding="utf-8", errors="replace"))[0]
        media = sorted(p.name for p in d.glob("*") if p.suffix in (".webp", ".jpg", ".png"))
        parts = [p.name for p in sorted(d.glob("*")) if p.name in ("build.py", "storyboard.md",
                                                                   "figures.json", "slides")]
        out.append({"path": d.relative_to(root).as_posix() + "/", "summary": clean(summary),
                    "media": media, "parts": parts})
    return out


def parse_decks(root: Path) -> list[str]:
    return sorted(p.name for p in (root / "assets/js/deck").glob("*.js"))


# The services a routine session reaches outside this checkout. Each row is listed only when the
# routine text actually names it, and carries the sections that do, so a service the routine
# stops using drops out of the inventory on the next build.
SERVICES = [
    ("Subagents (Task/Agent tool)", r"\bSpawn\b|\bspawn\b", "the fixed fan-out in NON-NEGOTIABLES 11; agents are leaf workers"),
    ("WebSearch", r"\bWebSearch\b|\bsearches\b", "scouts and the craft refresh"),
    ("WebFetch / HTTP fetch", r"\bWebFetch\b|(?<![-\w])fetch(?:es|ed)?\b(?! origin)", "primary sources; robots.txt re-checked per host"),
    ("Gmail connector", r"\bGmail\b|create_draft|get_draft", "create_draft with htmlBody, then get_draft; DRAFT ONLY"),
    ("Supabase connector", r"\bSupabase\b", "the scanner's daily ceiling query, read only"),
    ("GitHub (git, PR, checks)", r"pull request|check runs|workflow_dispatch|\bgit fetch\b", "push via scripts/shared/push.sh, PR ready, merge on green head SHA"),
    ("Headless browser (render.py)", r"render\.py", "Chromium via the carousel-engine skill"),
    ("Node", r"\bnode\b", "TXLAYOUT.check before dossiers; the article edition suite"),
]


def parse_services(routine: str) -> list[dict]:
    sections = routine_sections(routine)
    out = []
    lines = routine.split("\n")
    for name, pattern, use in SERVICES:
        rx = re.compile(pattern)
        where: list[str] = []
        for i, line in enumerate(lines, 1):
            if rx.search(line):
                lab = section_of(sections, i)
                if lab not in where:
                    where.append(lab)
        if where:
            out.append({"name": name, "where": where, "use": use})
    return out


# ------------------------------------------------------------------------------ the page

def table(head: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return out


def code(s: str) -> str:
    return f"`{s}`" if s else ""


def build(root: Path = REPO_ROOT) -> str:
    def read(rel: str) -> str:
        p = root / rel
        return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

    routine = read("prompts/daily_routine.md")
    guards = read(".github/workflows/guards.yml")
    gate_status = read("scripts/carousel/gate_status.py")
    shipped = read("scripts/carousel/shipped_check.py")

    engine = parse_engine(read("assets/js/txthree.js"))
    kit = parse_kit(root)
    libs = parse_libraries(root)
    layout = parse_layout(root)
    objects = parse_objects(root)
    geo = parse_geo(root) if (root / "assets/geo").exists() else []
    fonts, families = parse_fonts(root) if (root / "assets/fonts").exists() else ([], [])
    tools = parse_tools(root, ["scripts/carousel", "scripts/shared", ".claude/skills/carousel-engine"],
                        routine, guards, gate_status, shipped)
    other_tools = parse_tools(root, ["scripts/site", "scripts/gridwatch"], routine, guards,
                              gate_status, shipped, only_named=True)
    agents = parse_agents(root)
    skills = parse_skills(root)
    knowledge = parse_knowledge(root)
    examples = parse_examples(root)
    decks = parse_decks(root) if (root / "assets/js/deck").exists() else []
    services = parse_services(routine)

    n_models = sum(len(f["models"]) for f in kit["families"])
    L: list[str] = []
    L += [
        "# ARSENAL, everything a run has",
        "",
        "<!-- GENERATED by scripts/carousel/arsenal.py from the sources it lists. Do not hand-edit.",
        "     Re-run `python3 scripts/carousel/arsenal.py`; `--check` proves this file is current. -->",
        "",
        "**Generated, never hand-edited.** Every row below is read from the file it describes, so it "
        "is as current as the last build. `python3 scripts/carousel/arsenal.py --check` exits non-zero "
        "when it is not.",
        "",
        "**Open this page first when a deck is planned.** The order of reach, before anything is "
        "modelled or written:",
        "",
        "1. **A kit model** (THE KIT below). A model the kit has is never rebuilt from primitives.",
        "2. **An engine call** (THE ENGINE). The sky, the ground, the contact shadow, the weathering, "
        "the room and the scatter are the engine's, never a deck's.",
        "3. **A library** (THE LIBRARIES) for type, layout, colour, cartography and the grade.",
        "4. **Only then new geometry**, built the kit's way (`K.define` conventions, metres, +z front) "
        "so it can be lifted into the kit, and proposed in `knowledge/carousel/UPGRADE_BACKLOG.md`.",
        "",
        "| section | count |",
        "|---|---|",
        f"| engine calls (`TXT.*`) | {len(engine['functions'])} |",
        f"| world presets | {len(engine['worlds'])} |",
        f"| kit models | {n_models} in {len(kit['families'])} families |",
        f"| asset libraries | {len(libs)} |",
        f"| carousel and shared tools | {len(tools)} |",
        f"| record and site tools the routine names | {len(other_tools)} |",
        f"| agents | {len(agents)} |",
        f"| knowledge files | {len(knowledge)} |",
        f"| examples | {len(examples)} |",
        "",
    ]

    # ---- by phase: the same wiring, read the other way round
    order = [lab for _, lab in routine_sections(routine)]
    by: dict[str, list[str]] = {}
    for t in tools + other_tools:
        for ph in t["phases"]:
            by.setdefault(ph, []).append(t["path"].rsplit("/", 1)[-1])
    if by:
        L += ["## BY PHASE, the tools the routine names in each section", ""]
        L += table(["section", "tools"],
                   [[lab, ", ".join(code(n) for n in sorted(by[lab]))]
                    for lab in dict.fromkeys(order) if lab in by]) + [""]

    # ---- the engine
    L += ["## THE ENGINE, `assets/js/txthree.js`", "",
          "`import { init } from '@@ASSETS@@/js/txthree.js'; const TXT = init(THREE);` "
          "Every call below is on `TXT`.", ""]
    rows = []
    for f in engine["functions"]:
        note = f["doc"] + (" (defined twice, the later one wins)" if f.get("redefined") else "")
        rows.append([code(("await " if f["async"] else "") + f["sig"]), note])
    if engine.get("recipe"):
        L += ["**The whole stage, in the engine's own words** (quoted from its header):", "",
              "```js"] + engine["recipe"] + ["```", ""]
    L += table(["call", "what it does (its own doc comment)"], rows) + [""]
    if engine["worlds"]:
        L += ["**World presets** (`TXT.worlds`, declared once as the chassis `sky`):", ""]
        L += table(["world", "the light it is"], [[code(k), c] for k, c in engine["worlds"]]) + [""]
    if engine["surfaces"]:
        L += ["**Ground surfaces** (`TXT.ground(R, { surface })`): "
              + ", ".join(code(s) for s in engine["surfaces"]) + ".", ""]
    if engine["scatter"]:
        L += ["**Scatter kinds** (`TXT.scatter(R, { kind })`): "
              + ", ".join(code(s) for s in engine["scatter"]) + ".", ""]
    if engine["mats"]:
        L += ["**Materials** (`TXT.mat`): " + ", ".join(code(s) for _, s in engine["mats"]) + ".", ""]
    if engine["rigs"]:
        L += ["**Legacy rigs** (`TXT.rigs`, a deck uses `TXT.deckRig`): "
              + "; ".join(f"{code(k)} {c}".strip() for k, c in engine["rigs"]) + ".", ""]

    # ---- the kit
    L += ["## THE KIT, `assets/js/txkit.js` and `assets/js/kit/*.js`", ""]
    if kit["header"]:
        L += [kit["header"], ""]
    L += ["`import { initKit } from '@@ASSETS@@/js/txkit.js'; const K = initKit(THREE, TXT);` then "
          "`const m = K.make('name', { seed, ...options }); TXT.add(R, m); TXT.contact(R, m);`. "
          "Metres, y up, origin at the footprint centre on the ground, front faces +z. The size "
          "column is an ENVELOPE sampled over sixteen seeds by `examples/kit/sizes.py`, not a bound "
          "on every seed: to place a built model exactly, read its own `m.userData.size`, which "
          "`K.make` measures on every call. Proof pages: "
          "`python3 examples/kit/build.py --family <family> --out out/kit/<family>/slides`.", ""]
    if kit["helpers"]:
        L += ["**Builder helpers**, for new geometry made the kit's way:", ""]
        L += table(["helper", "note"], [[code(h["sig"]), h["doc"]] for h in kit["helpers"]]) + [""]
    for fam in kit["families"]:
        L += [f"### {fam['family']} ({len(fam['models'])})", ""]
        if not fam["file"]:
            L += ["Imported by `txkit.js` and has no file yet.", ""]
            continue
        line = code(fam["file"])
        if fam["summary"]:
            line += ", " + fam["summary"]
        if not fam.get("imported", True):
            line += " **Not imported by txkit.js, so K.make can't reach it.**"
        L += [line, ""]
        if fam["dynamic"]:
            L += [f"{fam['dynamic']} definition(s) here use a computed name and are not listed. "
                  "Run `K.list()` in a page for the whole set.", ""]
        if fam["models"]:
            L += table(["model", "size w x h x d (m)", "options", "note"],
                       [[code(m["name"]), m["size"], m["options"], m["note"]] for m in fam["models"]])
            L += [""]
        else:
            L += ["No models registered yet.", ""]

    # ---- libraries
    L += ["## THE LIBRARIES, `assets/js/*.js`", "",
          "Classic scripts expose a global. The engine and the kit are ES modules and are above.", ""]
    rows = []
    for lib in libs:
        api = ", ".join(lib["api"][:28]) + (f" (+{len(lib['api']) - 28})" if len(lib["api"]) > 28 else "")
        rows.append([code(lib["file"]), code(lib["global"]) if lib["global"] else ("vendored" if lib["vendored"] else ""),
                     lib["summary"], api])
    L += table(["file", "global", "what it is", "API"], rows) + [""]
    if layout:
        L += ["**Layouts** (`TXLAYOUT`, checked in Node before any dossier):", ""]
        if "ARCHETYPES" in layout:
            L += ["- archetypes: " + ", ".join(code(a) for a in layout["ARCHETYPES"])]
        if "DEVICES" in layout:
            L += ["- continuity devices: " + ", ".join(code(a) for a in layout["DEVICES"])]
        if "ROTATION" in layout and isinstance(layout["ROTATION"], dict):
            L += ["- rotation rule: " + ", ".join(f"{k} {v}" for k, v in layout["ROTATION"].items())]
        L += [""]
    if objects:
        L += ["**The 2.5D object catalogue** (`TXOBJ.sprite(name)` on the `TXSCENE` bench, canvas "
              "only, for the rare frame that is not rendered; a rendered frame takes the kit): "
              + ", ".join(f"{code(n)} {s}" for n, s in objects) + ".", ""]
    if decks:
        L += ["**Earlier deck chassis** (`assets/js/deck/`, read how a `TXDECK.declare` is written, "
              "never copy a world): " + ", ".join(code(d) for d in decks) + ".", ""]
    if geo:
        L += ["**Geodata** (`assets/geo/`):", ""]
        L += table(["file", "contents"], [[code(n), d] for n, d in geo]) + [""]
    if fonts:
        L += ["**Fonts** (`assets/fonts/`, served by `fonts.css`): families "
              + ", ".join(families) + ". Files " + ", ".join(fonts) + ".", ""]

    # ---- tools
    L += ["## THE TOOLS AND GATES", "",
          "Run every gate by EXIT CODE, never by reading the last line. **Wired** says what runs it "
          "without a session remembering to: `CI` is a real invocation in `guards.yml`, `CI "
          "self-test` only its self-test there, `gate table` a row or import in `gate_status.py`, "
          "`shipped` the published-run registry in `shipped_check.py`. **Phases** are the routine "
          "sections that name it.", ""]

    def tool_rows(ts):
        return [[code(t["path"]), t["doc"], " ".join(t["flags"]), ", ".join(t["wired"]),
                 ", ".join(t["phases"])] for t in ts]
    L += table(["tool", "what it is", "flags", "wired", "phases"], tool_rows(tools)) + [""]
    if other_tools:
        L += ["**Record, site and instrument tools the routine names:**", ""]
        L += table(["tool", "what it is", "flags", "wired", "phases"], tool_rows(other_tools)) + [""]

    # ---- agents and skills
    L += ["## THE AGENTS AND SKILLS, `.claude/` (read only to a run)", ""]
    L += table(["agent", "tools", "what it does"],
               [[code(a["name"]), a["tools"] + (f", model {a['model']}" if a["model"] else ""),
                 a["desc"]] for a in agents]) + [""]
    if skills:
        L += table(["skill", "file", "what it does"],
                   [[code(s["name"]), code(s["path"]), s["desc"]] for s in skills]) + [""]

    # ---- services
    if services:
        L += ["## THE SERVICES THE ROUTINE NAMES", ""]
        L += table(["service", "how the routine uses it", "sections"],
                   [[s["name"], s["use"], ", ".join(s["where"])] for s in services]) + [""]

    # ---- knowledge
    L += ["## THE DOCTRINE, `knowledge/`", ""]
    L += table(["file", "heading", "first sentence"],
               [[code(k["path"]), k["heading"], k["first"]] for k in knowledge]) + [""]

    # ---- examples
    L += ["## THE EXAMPLES, `examples/`", "",
          "Measurements and plumbing, never a subject or a palette to copy.", ""]
    L += table(["example", "what it is", "open"],
               [[code(e["path"]), e["summary"], ", ".join(e["media"][:6] + e["parts"])] for e in examples])
    L += [""]
    text = "\n".join(L).rstrip() + "\n"
    return text


# ------------------------------------------------------------------------------ check, self-test

def check(root: Path = REPO_ROOT) -> int:
    target = root / OUT_REL
    fresh = build(root)
    if not target.exists():
        print(f"arsenal --check: FAIL, {OUT_REL} does not exist. Run scripts/carousel/arsenal.py")
        return 1
    have = target.read_text(encoding="utf-8")
    if have == fresh:
        print(f"arsenal --check: ok, {OUT_REL} is current")
        return 0
    a, b = have.split("\n"), fresh.split("\n")
    n = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    print(f"arsenal --check: FAIL, {OUT_REL} is stale from line {n + 1}.")
    print(f"  committed: {a[n][:160] if n < len(a) else '<end of file>'}")
    print(f"  fresh:     {b[n][:160] if n < len(b) else '<end of file>'}")
    print("  Re-run `python3 scripts/carousel/arsenal.py` and commit the result. Never hand-edit it.")
    return 1


FIX_TXTHREE = """export function init(THREE) {
  const TXT = {};
  /* ---- probe ---------------------------------------------------------- */
  // Tells whether WebGL works. Probes a throwaway canvas.
  TXT.webglOK = function () { return true; };

  /* TXT.fog(R, { near, far }) \u2014 thick morning fog in the horizon's hue. Call once. */
  TXT.fog = function (R, o) { o = o || {}; };
  TXT.snapshot = async function (R, o) { };
  TXT.worlds = {
    dawn: {     // the first light, cold and long
      az: 90 },
    dusk: { az: 270 },
  };
  const SURFACES = {
    mud: { base: 1 },
    sand: { base: 2, note: "a, b" },
  };
  TXT.scatter = function (R, o) {
    if (kind === 'reeds') {} else if (kind === 'rocks') {}
  };
  return TXT;
}
"""

FIX_KIT = """/* txkit.js \u2014 THE KIT: fixture models. */
import * as farm from './kit/farm.js';
const FAMILIES = { farm };
export function initKit(THREE, TXT) {
  const K = {};
  // Registers a model.
  K.define = function (name, spec) {};
  K.box = function (w, h, d, mat) {};
}
"""

FIX_FAMILY = """/* kit/farm.js \u2014 the farm, for the self-test. More words here. */
export function install(K, THREE, TXT) {
  function def(name, spec) {
    K.define(name, Object.assign({}, spec, { make(o, r) { return spec.make(o, r); } }));
  }
  K.define('silo', {
    size: [4, 12.5, 4],
    options: { seed: 1, cap: "'dome'|'cone'", rust: 0.2 },
    note: 'A grain silo with a {braced} note, and a comma. Second sentence.',
    make(o, r) { return { a: [1, 2, { b: 3 }] }; },
  });
  def("tractor", { size: [5, 3, 2.4], options: {}, note: "Red.", make(o) { return 1; } });
  for (const n of ['x', 'y']) K.define(n, { size: [1, 1, 1], make() {} });
}
"""

FIX_TOOL = '''#!/usr/bin/env python3
"""fake_gate.py \u2014 a fixture gate that checks nothing at all. It has a second sentence."""
import argparse
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("run_dir")
    ap.add_argument("--self-test", action="store_true")
'''


def self_test() -> int:
    checks: list[tuple[str, bool, object]] = []

    def ok(name: str, cond: bool, got: object = "") -> None:
        checks.append((name, bool(cond), got))

    eng = parse_engine(FIX_TXTHREE)
    names = [f["name"] for f in eng["functions"]]
    ok("engine: every TXT.<name> = function is found, async included",
       names == ["fog", "scatter", "snapshot", "webglOK"], names)
    fog = next(f for f in eng["functions"] if f["name"] == "fog")
    ok("engine: the signature is taken from the doc comment when it gives one",
       fog["sig"] == "TXT.fog(R, { near, far })", fog["sig"])
    ok("engine: the doc sentence loses the signature and its dash, and keeps no em dash",
       fog["doc"].startswith("thick morning fog") and "\u2014" not in fog["doc"], fog["doc"])
    probe = next(f for f in eng["functions"] if f["name"] == "webglOK")
    ok("engine: a // comment is read and the dashed banner above it is not",
       probe["doc"] == "Tells whether WebGL works." and "---" not in probe["doc"], probe["doc"])
    ok("engine: world presets and their trailing comments",
       eng["worlds"] == [("dawn", "the first light, cold and long"), ("dusk", "")], eng["worlds"])
    ok("engine: surfaces survive a comma inside a string value",
       eng["surfaces"] == ["mud", "sand"], eng["surfaces"])
    ok("engine: scatter kinds", eng["scatter"] == ["reeds", "rocks"], eng["scatter"])

    models, dynamic = parse_kit_family(FIX_FAMILY)
    by = {m["name"]: m for m in models}
    ok("kit: K.define and a local wrapper around it are both read",
       sorted(by) == ["silo", "tractor"], sorted(by))
    silo = by.get("silo", {})
    ok("kit: size", silo.get("size") == "4 x 12.5 x 4", silo.get("size"))
    ok("kit: option keys, seed dropped as universal", silo.get("options") == "cap, rust",
       silo.get("options"))
    ok("kit: the note's first sentence, braces inside the string do not break the parse",
       silo.get("note") == "A grain silo with a {braced} note, and a comma.", silo.get("note"))
    ok("kit: a computed-name definition is counted rather than silently missed", dynamic == 1,
       dynamic)

    hs = [h["sig"] for h in kit_helpers(
        "  K.box = function (w, h, d) {\n  };\n  K.finish = {\n    galvanized: () => 1,\n    steelPaint: (c) => 2,\n  };\n",
        {"people": "  /* tube through sections */\n  function loft(ctrl, o) {\n  }\n  K.loft = K.loft || loft;\n"})]
    ok("kit helpers: direct, namespace members and family-installed are all listed",
       hs == ["K.box(w, h, d)", "K.finish.galvanized()", "K.finish.steelPaint(c)", "K.loft(ctrl, o)"], hs)

    tool_flags = cli_flags(FIX_TOOL)
    ok("tools: argparse flags, the long form preferred, positionals shown in brackets",
       tool_flags == ["--date", "--verbose", "<run_dir>", "--self-test"], tool_flags)
    ok("tools: docstring first sentence without the file name prefix",
       py_doc_line(FIX_TOOL) == "a fixture gate that checks nothing at all.", py_doc_line(FIX_TOOL))

    ok("hygiene: dashes become words or commas, emoji dropped, pipes escaped",
       clean("a \u2014 b 3\u20134 x|y \U0001F600") == "a, b 3 to 4 x\\|y", clean("a \u2014 b 3\u20134 x|y \U0001F600"))

    # THE WHOLE BUILDER ON A FAKE TREE, AND --check GOING RED ON DRIFT. Scratch stays in the
    # working tree (CLAUDE.md, "Scratch never leaves the working tree").
    scratch = REPO_ROOT / "out" / "arsenal"
    scratch.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=scratch) as td:
        root = Path(td)
        (root / "assets/js/kit").mkdir(parents=True)
        (root / "assets/js/txthree.js").write_text(FIX_TXTHREE)
        (root / "assets/js/txkit.js").write_text(FIX_KIT)
        (root / "assets/js/kit/farm.js").write_text(FIX_FAMILY)
        (root / "assets/js/txfoo.js").write_text(
            "/* txfoo.js \u2014 a fixture library. */\n(function (global) {\n  var F = { a: 1, "
            "draw(x) { return x; } };\n  F.paint = function () {};\n  global.TXFOO = F;\n})(this);\n")
        (root / "scripts/carousel").mkdir(parents=True)
        (root / "scripts/carousel/fake_gate.py").write_text(FIX_TOOL)
        (root / "prompts").mkdir()
        (root / "prompts/daily_routine.md").write_text(
            "# R\n\n## PHASE 11 \u2014 ART\n\nRun `fake_gate.py`. Spawn nothing. Then WebSearch.\n")
        (root / ".github/workflows").mkdir(parents=True)
        (root / ".github/workflows/guards.yml").write_text(
            "run: python3 scripts/carousel/fake_gate.py --self-test\n")
        (root / "knowledge/carousel").mkdir(parents=True)
        (root / "knowledge/carousel/DOC.md").write_text("# The doc\n\nIt says one thing. Then more.\n")

        text = build(root)
        ok("build: the kit model reaches the page", "`silo` | 4 x 12.5 x 4" in text)
        ok("build: the engine call reaches the page", "`TXT.fog(R, { near, far })`" in text)
        ok("build: a library's global and API reach the page",
           "`TXFOO`" in text and "draw, paint" in text)
        ok("build: a tool's wiring reads a self-test line as self-test, never as a run",
           "CI self-test" in text and "| 11 |" in text)
        ok("build: the routine's services are read from its text",
           "WebSearch" in text and "Subagents" in text)
        ok("build: the doctrine row, a too-short first sentence carries its next one",
           "| The doc | It says one thing. Then more. |" in text)
        ok("build: the by-phase index names the tool under its phase",
           "| 11 | `fake_gate.py` |" in text)
        ok("build: no em or en dash and no emoji anywhere in the page",
           not re.search("[\u2013\u2014]", text) and not _EMOJI.search(text))
        ok("build: deterministic, two builds are byte identical", text == build(root))

        (root / OUT_REL).write_text(text)
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            clean_rc = check(root)
            (root / "assets/js/kit/farm.js").write_text(
                FIX_FAMILY.replace("K.define('silo'", "K.define('barn', { size: [9, 7, 12], "
                                   "make() {} });\n  K.define('silo'"))
            drift_rc = check(root)
            (root / OUT_REL).unlink()
            absent_rc = check(root)
        ok("--check: exit 0 on a current file", clean_rc == 0, clean_rc)
        ok("--check: exit 1 when a new kit model lands and the page was not rebuilt",
           drift_rc == 1, drift_rc)
        ok("--check: exit 1 when the page does not exist", absent_rc == 1, absent_rc)

    bad = [c for c in checks if not c[1]]
    for name, passed, got in checks:
        print(f"  {'ok  ' if passed else 'FAIL'} {name}" + ("" if passed else f"  (got {got!r})"))
    print(f"arsenal --self-test: {len(checks) - len(bad)}/{len(checks)} passed")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true", help="exit 1 if the committed file is stale")
    ap.add_argument("--stdout", action="store_true", help="print the build, write nothing")
    ap.add_argument("--self-test", action="store_true", help="prove the parsers and the drift check")
    a = ap.parse_args()
    try:
        if a.self_test:
            return self_test()
        if a.check:
            return check()
        text = build()
        if a.stdout:
            sys.stdout.write(text)
            return 0
        (REPO_ROOT / OUT_REL).write_text(text, encoding="utf-8")
        print(f"arsenal: wrote {OUT_REL}, {text.count(chr(10))} lines")
        return 0
    except Exception as e:  # the builder could not run: say so, never report clean
        print(f"arsenal: could not build ({type(e).__name__}: {e})", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
