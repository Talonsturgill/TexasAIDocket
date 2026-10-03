#!/usr/bin/env python3
"""week_digest.py — what the judges kept saying this week, counted, for the weekly machine pass.

WHY THIS EXISTS (owner, 2026-10-02)

The weekly machine pass is meant to fix "the things that really need to be fixed based on the
recurring themes that it saw during the week ... based on actual output". A pass that reads only
the queue fixes what the runs remembered to write down. A pass that reads one run fixes that
run. This reads the week's own artifacts, every shipped run in the window, and puts three things
in front of the upgrade engineer:

  THE SCORES     each run's weighted score, rounds and per-criterion medians, the week's mean per
                 criterion and how often each was the lowest. Computed here, never typed.
  THE THEMES     every recurring defect the judges named, counted by how many RUNS and how many
                 ROUNDS named it. A theme named in every round of a run is one the run's repairs
                 could not reach, which is the machine's to fix and not the deck's. The theme
                 names come from ILLUSTRATION_SYSTEM.md "What still fails" and the judges' own
                 words. The counting is a word match and says so: it finds the candidates and
                 the engineer reads the evidence before believing a count.
  THE EVIDENCE   the judges' ranked artwork defects from the first and last round, every hard
                 fail, each judge's last one sentence fix, and the queue, verbatim, with dates.

    week_digest.py --date 2026-10-09 [--days 7] [--out out/2026-10-09/week_digest.md]
    week_digest.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import statistics
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"
QUEUE = REPO_ROOT / "knowledge" / "carousel" / "MACHINE_QUEUE.md"
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Each theme is a defect the judges have named in more than one deck, in the words they used.
THEMES = [
    ("hero too small to own the frame",
     r"under a tenth|too small|(hero|vial|subject)\b[^.]{0,60}\b(small|tenth|percent of the frame|"
     r"does ?n[o']t own|does not own)"),
    ("largest object unmodelled (slab, bare wall, clean clay)",
     r"featureless|\bslab\b|bare wall|dead wall|smooth plane|clean clay|maquette|untextured"),
    ("primitive or low-poly model where a kit model belongs",
     r"primitive|low.?poly|capsule|extruded box|game (?:level|engine|asset)|mannequin|faceless|"
     r"\b(?:toy|tiny|small|cream|plain|box)[- ]?(?:like )?(?:cream )?blocks?\b|\bblocky\b|box towers?"),
    ("no contact, dirt or grime where things meet the ground",
     r"no contact|without contact|\bfloat(?:s|ing)?\b|no dirt|no grime|hovers?"),
    ("horizon band or seam",
     r"horizon (?:band|strip)|(?:band|strip|line)\b[^.]{0,40}\bhorizon|reads as (?:sea|water)|"
     r"(?:sky|ground|haze|horizon|plain)\b[^.]{0,40}\bseam\b|\bseam\b[^.]{0,40}\b(?:sky|ground|haze|horizon|plain)"),
    ("object in a void, no sky, camera at the ground",
     r"\bvoid\b|no sky|top.?down|looks? (?:straight )?down"),
    ("dead or empty region",
     r"dead (?:zone|region|lower|third|space|area)|empty (?:lower|ground|third|wall)|eventless|dead ground"),
    ("repeated composition or shot",
     r"repeat(?:ed|s)? (?:composition|framing|shot|camera)|same (?:shot|composition|camera|framing)"),
    ("value strobe or undeclared tonal cut",
     r"strob|value (?:cut|jump)|hard (?:value |tonal )?cuts?\b|undeclared cut",
     # a judge naming the deck's DECLARED cut is describing the plan working, not a defect
     r"^(?!.*(?:undeclared|(?:only|, ) ?one declared|not declared|no declared)).*(?:\bdeclared\b|storyboard)"),
    ("render artifact (banding, aliasing, facets, stripes)",
     r"banding|moir|artifact|aliasing|jagg|faceted|posteri"),
    ("flat 2D overlay on a rendered frame (bars, plates, stickers)",
     r"ui bars?|flat (?:2d|bars?|ui)|(?:type|text|dek|headline) on (?:a|an|the) (?:opaque )?plate|"
     r"opaque plate|sticker|scatter.?card"),
    ("grass or scatter (one tuft, black, sprite)",
     r"\btufts?\b|grass|stubble"),
    ("sky colour (mauve, magenta, smog)",
     r"mauve|magenta|purple|\bsmog\b|pink sky"),
    ("type sitting on or fighting the art",
     r"\bdek\b[^.]{0,40}\b(?:sits|edge|over|on)|type (?:on|over|fights)|legib|contrast"),
]
THEME_RX = [(t[0], re.compile(t[1], re.I)) for t in THEMES]
THEME_EXCLUDE = {t[0]: re.compile(t[2], re.I | re.S) for t in THEMES if len(t) > 2}

# A NAMED DEFECT IS NOT A NEGATED ONE (weekly pass 2026-10-03). The first digest matched the
# whole card at once, so a judge's "the value holds with no strobe" counted as a strobe, "nothing
# floats in a void" counted as a void, and a deck's declared value cut counted as an undeclared
# one. Value strobe ranked second of thirteen at five runs, and read sentence by sentence the
# judges named it on two. So a theme now counts a SENTENCE, and a match with a negator in the
# four words before it does not count. The theme's own words may carry a negator ("no contact"),
# which is why the window is the words BEFORE the match and never the match itself.
NEGATOR = re.compile(r"\b(?:no|not|nothing|never|without|none|neither|nor)\b|n't\b", re.I)
SENTENCE = re.compile(r"(?<=[.;!?])\s+")


def theme_named(name: str, rx: re.Pattern, text: str) -> bool:
    """True when some sentence of `text` names the theme without negating it."""
    ex = THEME_EXCLUDE.get(name)
    for sent in SENTENCE.split(text):
        if ex and ex.search(sent):
            continue
        for m in rx.finditer(sent):
            before = sent[:m.start()].split()[-4:]
            if not NEGATOR.search(" ".join(before)):
                return True
    return False


def _num(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def run_dirs(root: Path, date: str, days: int) -> list[Path]:
    end = dt.date.fromisoformat(date)
    start = end - dt.timedelta(days=days - 1)
    out = []
    for p in sorted(root.glob("*")):
        if p.is_dir() and DATE_RE.fullmatch(p.name) and start <= dt.date.fromisoformat(p.name) <= end:
            out.append(p)
    return out


def cards(run: Path) -> list[dict]:
    """Every judge card in the run's score history, with its round and lens, oldest first."""
    found = []
    for f in sorted((run / "scores").rglob("*.json")) if (run / "scores").exists() else []:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            continue
        if not isinstance(d, dict) or not isinstance(d.get("criteria"), list):
            continue                                   # combined panel files carry a dict
        rel = str(f.relative_to(run / "scores"))
        m = re.search(r"(?:^|/)r(\d+)/", rel) or re.search(r"round(\d+)", rel)
        rnd = int(m.group(1)) if m else (d.get("round") if _num(d.get("round")) else 0)
        lens = d.get("lens") or next((x for x in ("craft", "integrity", "reader") if x in f.name), "?")
        found.append({"round": int(rnd), "lens": str(lens), "card": d, "file": rel})
    return sorted(found, key=lambda c: (c["round"], c["lens"]))


def art_text(card: dict) -> str:
    """The words a card spends on the art: its art criteria, its defects, its weakest frames, its fix."""
    parts = []
    for c in card.get("criteria") or []:
        if isinstance(c, dict) and c.get("name") in ("artwork_craft", "deck_coherence"):
            parts.append(str(c.get("why") or c.get("notes") or ""))
    for k in ("artwork_defects",):
        v = card.get(k)
        parts.extend(str(x) for x in v) if isinstance(v, list) else None
    for w in card.get("artwork_weakest_frames") or []:
        if isinstance(w, dict):
            parts.append(f"{w.get('problem', '')} {w.get('fix', '')}")
    parts.append(str(card.get("one_sentence_fix") or ""))
    return " ".join(p for p in parts if p)


def digest(root: Path, date: str, days: int, queue_text: str) -> tuple[str, dict]:
    runs = run_dirs(root, date, days)
    rows, crit_vals, lowest, theme_hits = [], {}, {}, {t[0]: {} for t in THEMES}
    hard, fixes, defects = [], [], []
    for run in runs:
        try:
            s = json.loads((run / "score.json").read_text(encoding="utf-8"))
        except (ValueError, OSError):
            s = {}
        crit = {k: v.get("score") for k, v in (s.get("criteria") or {}).items()
                if isinstance(v, dict) and _num(v.get("score"))}
        for k, v in crit.items():
            crit_vals.setdefault(k, []).append(float(v))
        if crit:
            lo = min(crit.values())
            for k, v in crit.items():
                if v == lo:
                    lowest[k] = lowest.get(k, 0) + 1
        rows.append((run.name, s.get("weighted_score"), s.get("rounds"), crit))
        cs = cards(run)
        for c in cs:
            text = art_text(c["card"])
            for name, rx in THEME_RX:
                if theme_named(name, rx, text):
                    theme_hits[name].setdefault(run.name, set()).add(c["round"])
            for hf in c["card"].get("hard_fails") or []:
                hard.append(f"{run.name} r{c['round']} {c['lens']}: {str(hf)[:300]}")
        if cs:
            last = max(c["round"] for c in cs)
            for c in cs:
                if c["round"] == last and c["card"].get("one_sentence_fix"):
                    fixes.append(f"{run.name} r{last} {c['lens']}: {str(c['card']['one_sentence_fix'])[:400]}")
            craft = [c for c in cs if c["lens"] == "craft" and c["card"].get("artwork_defects")]
            if craft:
                for c in (craft[0], craft[-1]) if len(craft) > 1 else (craft[0],):
                    defects.append((run.name, c["round"], [str(x)[:300] for x in c["card"]["artwork_defects"]]))

    n = len(runs)
    L = [f"# The week's machine digest, {n} shipped run(s) to {date}", ""]
    L += ["Computed by `scripts/carousel/week_digest.py` from the shipped artifacts under "
          "`runs/carousel/`. Every number here is counted, never typed.", ""]
    L += ["## The scores", "", "| run | weighted | rounds | lowest criterion |", "|---|---|---|---|"]
    for name, w, r, crit in rows:
        lo = min(crit.values()) if crit else None
        low = ", ".join(sorted(k for k, v in crit.items() if v == lo)) if crit else "no criteria"
        L.append(f"| {name} | {w} | {r} | {low} ({lo}) |")
    L += ["", "| criterion | week mean | lowest on (runs) |", "|---|---|---|"]
    for k in sorted(crit_vals, key=lambda k: statistics.mean(crit_vals[k])):
        L.append(f"| {k} | {round(statistics.mean(crit_vals[k]), 2)} | {lowest.get(k, 0)} |")
    ranked = sorted(((name, hits) for name, hits in theme_hits.items() if hits),
                    key=lambda t: (-len(t[1]), -sum(len(r) for r in t[1].values()), t[0]))
    L += ["", "## The recurring themes, by how many runs named them", "",
          "A word match over the judges' art criteria, ranked defects, weakest frames and fixes. "
          "It finds candidates. Read the evidence below before believing a count.", "",
          "| theme | runs (of %d) | rounds named | runs and rounds |" % n, "|---|---|---|---|"]
    for name, hits in ranked:
        detail = "; ".join(f"{d} r{','.join(str(x) for x in sorted(rs))}" for d, rs in sorted(hits.items()))
        L.append(f"| {name} | {len(hits)} | {sum(len(r) for r in hits.values())} | {detail} |")
    if not ranked:
        L.append("| none matched | 0 | 0 | |")
    L += ["", "## The judges' ranked artwork defects, first and last round", ""]
    for name, rnd, ds in defects:
        L.append(f"**{name}, round {rnd}**")
        L += [f"- {d}" for d in ds]
        L.append("")
    L += ["## Hard fails, every round", ""] + ([f"- {h}" for h in hard] or ["- none"])
    L += ["", "## Each judge's last one sentence fix", ""] + ([f"- {f}" for f in fixes] or ["- none"])
    open_q = [ln for ln in queue_text.splitlines() if ln.startswith("- [ ] ")]
    L += ["", "## The queue, open items", ""] + (open_q or ["- none"])
    L.append("")
    data = {"runs": n, "themes": [{"theme": t, "runs": len(h), "rounds": sum(len(r) for r in h.values())}
                                  for t, h in ranked],
            "criteria_mean": {k: round(statistics.mean(v), 2) for k, v in crit_vals.items()}}
    return "\n".join(L), data


def self_test() -> int:
    bad = 0

    def ok(label, cond, extra=""):
        nonlocal bad
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        bad += 0 if cond else 1

    def card(lens, rnd, art_why, defects=(), fix="", hf=()):
        return {"lens": lens, "round": rnd, "hard_fails": list(hf), "one_sentence_fix": fix,
                "criteria": [{"name": "artwork_craft", "score": 6, "why": art_why},
                             {"name": "voice", "score": 7, "why": "plain"}],
                "artwork_defects": list(defects)}

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for name, art, w in (("2026-10-01", 6.0, 7.1), ("2026-10-02", 6.5, 7.4), ("2026-09-20", 5.0, 6.0)):
            d = root / name
            (d / "scores" / "r1").mkdir(parents=True)
            (d / "scores" / "r2").mkdir(parents=True)
            (d / "score.json").write_text(json.dumps({"weighted_score": w, "rounds": 2, "criteria": {
                "artwork_craft": {"score": art}, "voice": {"score": 7.0}}}))
            (d / "scores" / "r1" / "score-craft.json").write_text(json.dumps(
                card("craft", 1, "the hero is under a tenth of the frame", ["1. a featureless slab of coping"])))
            (d / "scores" / "r2" / "score-craft.json").write_text(json.dumps(
                card("craft", 2, "the vial is too small on 2 and 3", ["1. still a featureless slab"],
                     fix="bring the camera in", hf=["a figure with no claim"] if name == "2026-10-02" else ())))
            (d / "scores" / "r2" / "score.json").write_text(json.dumps({"criteria": {"x": {}}}))
        text, data = digest(root, "2026-10-02", 7, "## Open\n- [ ] 2026-10-01 | repeat: 1 | x\n")
        th = {t["theme"]: t for t in data["themes"]}
        ok("a run outside the window is not read", data["runs"] == 2, str(data))
        ok("the week's mean is computed per criterion", data["criteria_mean"].get("artwork_craft") == 6.25,
           str(data["criteria_mean"]))
        ok("a theme named in every round of two runs counts two runs and four rounds",
           th.get("hero too small to own the frame", {}).get("runs") == 2
           and th["hero too small to own the frame"]["rounds"] == 4, str(th))
        ok("the slab is its own theme", th.get("largest object unmodelled (slab, bare wall, clean clay)",
                                               {}).get("runs") == 2, str(th))
        ok("a theme nobody named is not listed", "sky colour (mauve, magenta, smog)" not in th)
        ok("hard fails, fixes and the queue reach the digest verbatim",
           "a figure with no claim" in text and "bring the camera in" in text and "repeat: 1" in text)
        ok("a combined panel file is not read as a judge card", "| 2026-10-01 |" in text)
        # THE NEGATION REPLAY (2026-10-03): the week of 2026-09-27 counted these as defects
        ok("a judge saying the value holds with no strobe names no strobe",
           not theme_named("value strobe or undeclared tonal cut", dict(THEME_RX)["value strobe or undeclared tonal cut"],
                           "The value holds with no strobe. Canvas means hold, so nothing strobes."))
        ok("a strobe the judge names still counts, so the theme can still go red",
           theme_named("value strobe or undeclared tonal cut", dict(THEME_RX)["value strobe or undeclared tonal cut"],
                       "The value strobes, five hard cuts, one declared."))
        ok("the deck's declared value cut is not an undeclared one",
           not theme_named("value strobe or undeclared tonal cut", dict(THEME_RX)["value strobe or undeclared tonal cut"],
                           "Frame 9's interior is the one declared value cut."))
        ok("an undeclared value cut counts",
           theme_named("value strobe or undeclared tonal cut", dict(THEME_RX)["value strobe or undeclared tonal cut"],
                       "Frame 5 an undeclared value cut mid deck."))
        ok("'nothing floats in a void' names no void",
           not theme_named("object in a void, no sky, camera at the ground",
                           dict(THEME_RX)["object in a void, no sky, camera at the ground"],
                           "This isn't a 4, since nothing floats in a void and there's no banding."))
        ok("a defect whose own words carry a negator still counts ('no contact')",
           theme_named("no contact, dirt or grime where things meet the ground",
                       dict(THEME_RX)["no contact, dirt or grime where things meet the ground"],
                       "The exterior ground has no contact and no dirt."))
        ok("the sources block is not a primitive block",
           not theme_named("primitive or low-poly model where a kit model belongs",
                           dict(THEME_RX)["primitive or low-poly model where a kit model belongs"],
                           "Regenerate the stale sources block and the text block."))
        ok("toy blocks are a primitive",
           theme_named("primitive or low-poly model where a kit model belongs",
                       dict(THEME_RX)["primitive or low-poly model where a kit model belongs"],
                       "Frame 3's field reads as shadowless toy blocks."))
        ok("a glass seam is not a horizon band",
           not theme_named("horizon band or seam", dict(THEME_RX)["horizon band or seam"],
                           "Frame 6 shows a hard vertical glass seam."))
        ok("a strip on the horizon line is a horizon band",
           theme_named("horizon band or seam", dict(THEME_RX)["horizon band or seam"],
                       "A dark floating gradient strip still sits on the horizon line."))
        e, _ = digest(root, "2026-08-01", 7, "")
        ok("an empty week says so rather than failing", "0 shipped run(s)" in e and "none matched" in e)
    live, _ = digest(RUNS, "2026-10-02", 7, "")
    ok("the live corpus digests", "## The recurring themes" in live)
    print("\nweek_digest self-test: " + ("all passed" if not bad else f"{bad} FAILED"))
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    text, data = digest(RUNS, a.date, a.days, QUEUE.read_text(encoding="utf-8") if QUEUE.exists() else "")
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(text, encoding="utf-8")
        print(f"week_digest: {data['runs']} run(s), {len(data['themes'])} theme(s), written to {a.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
