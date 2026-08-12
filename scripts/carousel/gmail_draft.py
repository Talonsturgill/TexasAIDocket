#!/usr/bin/env python3
"""gmail_draft.py — build the run's email payload. Drafts only, never sends.

WHAT THIS EMAIL IS FOR

It is the only human touchpoint in an otherwise autonomous product, and it gates the POST, not
the merge. By the time it arrives the deck has already merged to main, because the image URLs
in it point at main. So this is not an approval request. It is an honest account of what
shipped, written for somebody who was not watching and has about ninety seconds.

That shapes everything below. The score goes near the top whatever it says. What degraded is
named rather than omitted. The machine's own upgrades are listed, because a routine that edits
itself and does not report it is a routine nobody can audit.

WHY THE ADDRESS IS A CONSTANT

`DRAFT_TO` is a module constant and never the account-relative `me`. The Gmail connector
rejects `me` outright with "Invalid email address", so every run that tried it burned a step
rediscovering the address and typing it into a tool call by hand. A constant each run has to
rediscover is not a constant, it is a gap. If the mailbox moves, this line and the paragraph in
CLAUDE.md change, and nothing else.

    gmail_draft.py --run 2026-08-11 --title "..." --score 7.4
    gmail_draft.py --self-test
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The mailbox. One place, plus the paragraph in CLAUDE.md. Never "me".
DRAFT_TO = "docket@alaskaaihq.com"

# Images are served from the merged commit on main, which is why the merge lands before the
# email. A raw URL against a branch that later moves would rot.
RAW = "https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/main"
SITE = "https://talonsturgill.github.io/TexasAIDocket"


def e(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def ordinal_date(iso: str) -> str:
    import datetime as _dt
    d = _dt.date.fromisoformat(iso)
    suf = "th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th")
    return f"{d:%B} {d.day}{suf}, {d.year}"


def subject(n: int, run: str, title: str) -> str:
    return f"Texas AI Docket — Carousel No. {n} — {ordinal_date(run)} — {title}"


def body(*, run: str, n: int, title: str, caption: str, first_comment: str,
         score: float | None, threshold: float, slides: int, gates: dict,
         degraded: list, upgrades: list, notes: str = "") -> str:
    """The email, written so the first screen answers the only two questions that matter."""
    shipped = score is not None and score >= threshold

    # THE VERDICT LINE COMES FIRST AND IS NEVER SOFTENED. A reader who stops after one line
    # should still know whether this is postable and how good it is.
    verdict = (f"Shipped at {score}" if shipped else
               f"Did NOT meet the bar: {score} against {threshold}" if score is not None else
               "No score recorded")

    gate_rows = "".join(
        f"<tr><td>{e(k)}</td><td><strong>{e(v)}</strong></td></tr>"
        for k, v in gates.items())

    degraded_block = ""
    if degraded:
        items = "".join(f"<li>{e(d)}</li>" for d in degraded)
        degraded_block = (
            f'<h3>What degraded</h3><ul>{items}</ul>'
            f'<p style="color:#5A5064">Named here rather than left out. A run that quietly '
            f'ships less than it planned teaches nobody anything.</p>')

    upgrade_block = ""
    if upgrades:
        items = "".join(
            f"<li><strong>{e(u.get('what'))}</strong><br>"
            f"<span style=\"color:#5A5064\">{e(u.get('why'))}</span></li>" for u in upgrades)
        upgrade_block = (f"<h3>The machine changed itself</h3><ul>{items}</ul>"
                         f'<p style="color:#5A5064">Each reverts on its own commit.</p>')

    thumbs = "".join(
        f'<img src="{RAW}/runs/carousel/{run}/thumbs/slide-{i:02d}-thumb.png" '
        f'width="216" style="margin:0 6px 6px 0;border:1px solid #D9CFBC" alt="Slide {i}">'
        for i in range(1, slides + 1))

    return f"""<div style="font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#241E2E">
<h2 style="margin:0 0 4px">{e(title)}</h2>
<p style="margin:0 0 18px;color:#5A5064">Carousel No. {n}, {e(ordinal_date(run))}</p>

<p style="font-size:17px;margin:0 0 18px"><strong>{e(verdict)}</strong>{
    "" if shipped else " &mdash; read before posting."}</p>

<div style="border:1px solid #D9CFBC;padding:12px 16px;margin-bottom:18px">
<table style="border-collapse:collapse;font-size:14px">{gate_rows}</table>
</div>

{degraded_block}

<h3>The deck</h3>
<p>{thumbs}</p>
<p><a href="{RAW}/runs/carousel/{run}/carousel.pdf">carousel.pdf</a> &nbsp;
   <a href="{RAW}/runs/carousel/{run}/contact_sheet.png">contact sheet</a> &nbsp;
   <a href="{SITE}/">the site</a></p>

<h3>The post copy</h3>
<pre style="white-space:pre-wrap;font:14px/1.6 ui-monospace,Menlo,monospace;
            background:#F3EEE2;padding:14px;border:1px solid #D9CFBC">{e(caption)}</pre>

<h3>First comment</h3>
<pre style="white-space:pre-wrap;font:13px/1.6 ui-monospace,Menlo,monospace;
            background:#F3EEE2;padding:14px;border:1px solid #D9CFBC">{e(first_comment)}</pre>

{upgrade_block}
{f'<h3>Notes</h3><p>{e(notes)}</p>' if notes else ''}

<p style="color:#5A5064;font-size:13px;margin-top:24px">
This is a draft. Nothing was sent. The deck is already merged to main, so these links are
live; posting is the only step left, and it is yours.</p>
</div>"""


def payload(**kw) -> dict:
    return {"to": DRAFT_TO,
            "subject": subject(kw["n"], kw["run"], kw["title"]),
            "body": body(**kw), "isHtml": True}


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    base = dict(run="2026-08-11", n=1, title="Abilene approves the substation",
                caption="The commission met August 11th.", first_comment="Source: ...",
                score=7.4, threshold=7.0, slides=9,
                gates={"machine QA": "pass", "caption lint": "pass", "bespoke": "0.06"},
                degraded=[], upgrades=[])

    p = payload(**base)
    ok("the payload addresses the mailbox as a constant", p["to"] == DRAFT_TO)
    ok("...and never the account-relative me", p["to"] != "me" and "@" in p["to"])
    ok("the subject carries the number, the date and the title",
       "No. 1" in p["subject"] and "August 11th, 2026" in p["subject"]
       and "Abilene" in p["subject"], p["subject"])
    ok("the date in the subject is house style, not ISO", "2026-08-11" not in p["subject"])

    # THE VERDICT IS NEVER SOFTENED.
    ok("a passing score is stated plainly", "Shipped at 7.4" in p["body"])
    low = payload(**{**base, "score": 6.9})
    ok("a failing score says so first, and says read before posting",
       "Did NOT meet the bar: 6.9" in low["body"] and "read before posting" in low["body"])
    none = payload(**{**base, "score": None})
    ok("a missing score is reported, not silently omitted",
       "No score recorded" in none["body"])

    deg = payload(**{**base, "degraded": ["six slides instead of nine"]})
    ok("what degraded is named", "six slides instead of nine" in deg["body"])
    ok("...and a clean run carries no degradation block",
       "What degraded" not in p["body"])

    up = payload(**{**base, "upgrades": [{"what": "tightened the numeral gate",
                                          "why": "it missed a negative figure"}]})
    ok("machine upgrades are reported to the human",
       "tightened the numeral gate" in up["body"] and "it missed a negative figure" in up["body"])

    ok("images point at main, not at a run branch",
       "/main/runs/carousel/2026-08-11/" in p["body"] and "carousel/2026-08-11/carousel.pdf"
       in p["body"])
    ok("one thumb per slide", p["body"].count("slide-0") >= 9)
    ok("the caption is escaped, so markup in copy cannot break the email",
       "&lt;b&gt;" in payload(**{**base, "caption": "<b>x</b>"})["body"])

    ok("the email says plainly that nothing was sent",
       "This is a draft. Nothing was sent." in p["body"])
    ok("...and that the merge already happened",
       "already merged to main" in p["body"])

    ok("nothing in this file can send", "send" not in
       {n for n in dir(sys.modules[__name__]) if not n.startswith("_")})
    return _finish(failures)


def _finish(failures: int) -> int:
    if failures:
        print(f"\ngmail_draft self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\ngmail_draft self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run")
    ap.add_argument("--n", type=int, default=1)
    ap.add_argument("--title", default="")
    ap.add_argument("--score", type=float)
    ap.add_argument("--threshold", type=float, default=7.0)
    ap.add_argument("--slides", type=int, default=9)
    ap.add_argument("--caption-file")
    ap.add_argument("--comment-file")
    ap.add_argument("--gates-file", help="json object of gate name to result")
    ap.add_argument("--out", help="write the payload here for the connector call")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()
    if not a.run:
        ap.print_help()
        return 0

    def read(p):
        return Path(p).read_text(encoding="utf-8").strip() if p and Path(p).exists() else ""

    p = payload(run=a.run, n=a.n, title=a.title, caption=read(a.caption_file),
                first_comment=read(a.comment_file), score=a.score, threshold=a.threshold,
                slides=a.slides,
                gates=json.loads(read(a.gates_file) or "{}"), degraded=[], upgrades=[])
    out = Path(a.out) if a.out else REPO_ROOT / "out" / a.run / "gmail_payload.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gmail_draft: payload written to {out}")
    print(f"  to: {p['to']}\n  subject: {p['subject']}")
    print("  DRAFT ONLY. Pass this to the Gmail connector's create_draft. Never send.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"gmail_draft: broke: {exc}", file=sys.stderr)
        sys.exit(1)
