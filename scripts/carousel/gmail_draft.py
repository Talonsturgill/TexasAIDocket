#!/usr/bin/env python3
"""gmail_draft.py — build the run's email payload. Drafts only, never sends.

WHAT THIS EMAIL IS FOR

It is the only human touchpoint in an otherwise autonomous product, and it gates the POST, not
the merge. When a run SHIPS, the deck has already merged by the time this arrives and the image
URLs point at main. When a run HOLDS it has not merged, `--ref` carries the run branch, and the
email says so in two places rather than linking a reader to eight 404s. Either way this is not an
approval request. It is an honest account of what happened, written for somebody who was not
watching and has about ninety seconds.

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
import pathlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The mailbox. One place, plus the paragraph in CLAUDE.md. Never "me".
DRAFT_TO = "docket@alaskaaihq.com"

# Images are served from the merged commit on main when a run ships, which is why the merge lands
# before the email.
RAW_BASE = "https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket"
DEFAULT_REF = "main"

# WHICH COMMIT THE IMAGES COME FROM, 2026-08-19.
#
# This was the literal string "main", which is right for the case the file was written for: a run
# that passes its gates merges before the email goes out, so main has the artifacts. A run that
# HOLDS does not merge, and the same email then linked eight thumbnails, a PDF and a contact sheet
# to paths that do not exist on main. Every image a broken box, in the one message a reader gets,
# which is the exact failure `require` was written to prevent one line further down.
#
# The ref is now a parameter. A held run passes its run branch and the email says so.
_REF = DEFAULT_REF


def set_ref(ref: str) -> None:
    global _REF
    _REF = ref or DEFAULT_REF


def raw() -> str:
    return f"{RAW_BASE}/{_REF}"


SITE = "https://talonsturgill.github.io/TexasAIDocket"


def e(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def run_dir(run: str) -> Path:
    return REPO_ROOT / "runs" / "carousel" / run


class MissingAsset(Exception):
    """A file this email would link to is not in the run directory."""


def require(run: str, name: str) -> str:
    """The URL for one shipped artifact, and it has to be on disk before it goes in the mail.

    A DEAD LINK IN THIS EMAIL IS WORSE THAN A MISSING SECTION, because the reader cannot tell a
    404 from a run that produced nothing, and this email is the only thing they see. The sibling
    routine already learned this and wrote it down as "the routine forbids putting an unverified
    link in a draft". The same rule belongs here, enforced rather than remembered.
    """
    if not (run_dir(run) / name).exists():
        raise MissingAsset(f"{run}/{name} is not in the run directory, so the email would "
                           f"link to a 404")
    return f"{raw()}/runs/carousel/{run}/{name}"


# The formats a thumbnail has actually shipped in. `.png` on 2026-08-16 and `.webp` on
# 2026-08-18, which is the whole reason this is a list and not a constant. See `thumbs`.
THUMB_EXTS = (".png", ".webp", ".jpg", ".jpeg")


def thumbs(run: str, slides: int | None = None) -> list:
    """One URL per rendered slide, discovered from the run directory rather than assumed.

    THIS WAS HARDCODED TO `.png` AND THE 2026-08-18 RUN SHIPPED `.webp`. Every image in that
    email would have been a broken box, and nothing would have said so: the builder does not
    fetch, the connector does not fetch, and the reader finds out. The extension is not a fact
    about the email, it is a fact about what the render step happened to write that day, so it
    is read from disk.

    THE COUNT IS MEASURED, NOT DECLARED. If a caller says nine slides and eight thumbs exist,
    that is a broken email either way, and the honest failure is here rather than in the
    reader's inbox. `--slides` is checked against what is on disk and disagreeing is an error.
    """
    d = run_dir(run) / "thumbs"
    found = sorted(p for p in d.glob("slide-*-thumb.*") if p.suffix.lower() in THUMB_EXTS)
    if not found:
        raise MissingAsset(f"{run}/thumbs holds no slide thumbnail in any of {THUMB_EXTS}")
    if slides is not None and len(found) != slides:
        raise MissingAsset(f"{run}: {slides} slide(s) declared and {len(found)} thumbnail(s) "
                           f"on disk. The email would show a different deck from the one that "
                           f"shipped")
    return [f"{raw()}/runs/carousel/{run}/thumbs/{p.name}" for p in found]


def ordinal_date(iso: str) -> str:
    import datetime as _dt
    d = _dt.date.fromisoformat(iso)
    suf = "th" if 11 <= d.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d.day % 10, "th")
    return f"{d:%B} {d.day}{suf}, {d.year}"


def subject(n: int, run: str, title: str) -> str:
    # Commas, not em dashes. The house rule in CLAUDE.md is "no em dashes or en dashes anywhere"
    # and it does not carve out the subject line. This template had shipped three of them in the
    # one string the owner sees first, on every email the project has ever built.
    return f"Texas AI Docket, Carousel No. {n}, {ordinal_date(run)}, {title}"


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
        # BOTH SHAPES. This took a list of strings and every caller has passed a list of
        # {what, why} objects, the same shape the upgrades block below already renders properly.
        # The result was Python dict reprs, quotes escaped to &#x27; and all, printed into the one
        # section of the email whose whole job is explaining what went wrong.
        def _one(d):
            if isinstance(d, dict):
                what, why = d.get("what"), d.get("why")
                return (f"<li><strong>{e(what)}</strong>"
                        + (f"<br><span style=\"color:#5A5064\">{e(why)}</span>" if why else "")
                        + "</li>")
            return f"<li>{e(d)}</li>"
        items = "".join(_one(d) for d in degraded)
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

    urls = thumbs(run, slides)
    thumb_html = "".join(
        f'<img src="{u}" width="216" style="margin:0 6px 6px 0;border:1px solid #D9CFBC" '
        f'alt="Slide {i}">' for i, u in enumerate(urls, 1))
    pdf, sheet = require(run, "carousel.pdf"), require(run, "contact_sheet.png")

    return f"""<div style="font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;color:#241E2E">
<h2 style="margin:0 0 4px">{e(title)}</h2>
<p style="margin:0 0 18px;color:#5A5064">Carousel No. {n}, {e(ordinal_date(run))}</p>

<p style="font-size:17px;margin:0 0 18px"><strong>{e(verdict)}</strong>{
    "" if shipped else ". Read before posting."}</p>
{"" if _REF == DEFAULT_REF else
 f'<p style="border-left:3px solid #B98D46;padding-left:12px;color:#5A5064">'
 f'This run did not merge, so the images below come from the run branch '
 f'<code>{e(_REF)}</code> rather than from main. They stop resolving if that branch is '
 f'deleted.</p>'}

<div style="border:1px solid #D9CFBC;padding:12px 16px;margin-bottom:18px">
<table style="border-collapse:collapse;font-size:14px">{gate_rows}</table>
</div>

{degraded_block}

<h3>Post this</h3>
<p style="margin:0 0 10px">Upload the PDF to LinkedIn as a <strong>document</strong>, title it
<strong>{e(title)}</strong>, paste the post copy under it, then paste the first comment within
a minute of posting.</p>
<p><a href="{pdf}">carousel.pdf</a> &nbsp; <a href="{sheet}">contact sheet</a> &nbsp;
   <a href="{SITE}/">the site</a></p>
<p>{thumb_html}</p>

<h3>1. The post copy</h3>
<pre style="white-space:pre-wrap;font:14px/1.6 ui-monospace,Menlo,monospace;
            background:#F3EEE2;padding:14px;border:1px solid #D9CFBC">{e(caption)}</pre>

<h3>2. The first comment</h3>
<pre style="white-space:pre-wrap;font:13px/1.6 ui-monospace,Menlo,monospace;
            background:#F3EEE2;padding:14px;border:1px solid #D9CFBC">{e(first_comment)}</pre>

{upgrade_block}
{f'<h3>Notes</h3><p>{e(notes)}</p>' if notes else ''}

<p style="color:#5A5064;font-size:13px;margin-top:24px">
This is a draft. Nothing was sent. {
    "The deck is already merged to main, so these links are live. Posting is the only step left, "
    "and it is yours." if _REF == DEFAULT_REF else
    "The deck did NOT merge, so nothing here is on main and there is nothing to post. The links "
    "resolve against the run branch for as long as it exists."}</p>
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

    # A REAL SHIPPED RUN, deliberately. The old fixture used a run name that has never existed,
    # so every assertion below was made against a deck on no disk anywhere, and the one defect
    # that reached a reader, a thumbnail extension that did not match what the render step
    # wrote, was exactly the kind a fixture cannot see. Pointing the happy path at real
    # artifacts means this test fails the day the run directory's shape changes again.
    REAL = "2026-08-18"
    base = dict(run=REAL, n=1, title="Abilene approves the substation",
                caption="The commission met August 11th.", first_comment="Source: ...",
                score=7.4, threshold=7.0, slides=None,
                gates={"machine QA": "pass", "caption lint": "pass", "bespoke": "0.06"},
                degraded=[], upgrades=[])

    p = payload(**base)
    ok("the payload addresses the mailbox as a constant", p["to"] == DRAFT_TO)
    ok("...and never the account-relative me", p["to"] != "me" and "@" in p["to"])
    ok("the subject carries the number, the date and the title",
       "No. 1" in p["subject"] and ordinal_date(REAL) in p["subject"]
       and "Abilene" in p["subject"], p["subject"])
    ok("the subject carries no em dash and no en dash, which the house rule bans anywhere",
       "\u2014" not in p["subject"] and "\u2013" not in p["subject"], p["subject"])
    ok("...and neither does the body, in any of its encodings",
       not any(m in p["body"] for m in ("\u2014", "\u2013", "&mdash;", "&ndash;", "&#8212;")),
       [m for m in ("\u2014", "\u2013", "&mdash;", "&ndash;", "&#8212;") if m in p["body"]])
    ok("the date in the subject is house style, not ISO", "2026-08-11" not in p["subject"])

    # THE VERDICT IS NEVER SOFTENED.
    ok("a passing score is stated plainly", "Shipped at 7.4" in p["body"])
    low = payload(**{**base, "score": 6.9})
    ok("a failing score says so first, and says read before posting",
       "Did NOT meet the bar: 6.9" in low["body"] and "Read before posting" in low["body"])
    # A HELD RUN'S IMAGES ARE NOT ON MAIN, because a held run does not merge. This shipped
    # pointing at main regardless, so every image in the email would have been a broken box.
    try:
        set_ref("claude/daily-2026-08-19")
        held = payload(**{**base, "score": 6.8})
        ok("a held run's images point at the ref it was given, not at main",
           "/claude/daily-2026-08-19/runs/" in held["body"]
           and "/main/runs/" not in held["body"])
        ok("...and the email says so rather than leaving the reader to find out",
           "did not merge" in held["body"] and "claude/daily-2026-08-19" in held["body"])
    finally:
        set_ref(DEFAULT_REF)
    back = payload(**base)
    ok("...and the default is still main", "/main/runs/" in back["body"])

    none = payload(**{**base, "score": None})
    ok("a missing score is reported, not silently omitted",
       "No score recorded" in none["body"])

    deg = payload(**{**base, "degraded": ["six slides instead of nine"]})
    ok("what degraded is named", "six slides instead of nine" in deg["body"])
    ok("...and a clean run carries no degradation block",
       "What degraded" not in p["body"])

    # A DICT REPR IN THE EMAIL. Every caller passes {what, why} and this rendered str(dict).
    obj = payload(**{**base, "degraded": [{"what": "the deck holds", "why": "it scored 6.8"}]})
    ok("a degraded entry given as an object renders as prose, not as a python repr",
       "the deck holds" in obj["body"] and "it scored 6.8" in obj["body"]
       and "&#x27;what&#x27;" not in obj["body"] and "{'what'" not in obj["body"])
    ok("...and a plain string still renders",
       "just a string" in payload(**{**base, "degraded": ["just a string"]})["body"])
    up = payload(**{**base, "upgrades": [{"what": "tightened the numeral gate",
                                          "why": "it missed a negative figure"}]})
    ok("machine upgrades are reported to the human",
       "tightened the numeral gate" in up["body"] and "it missed a negative figure" in up["body"])

    ok("images point at main, not at a run branch",
       f"/main/runs/carousel/{REAL}/" in p["body"]
       and f"carousel/{REAL}/carousel.pdf" in p["body"])

    # THE DEFECT THAT WOULD HAVE REACHED A READER. The thumbnail extension was hardcoded to
    # `.png` while the 2026-08-18 render wrote `.webp`, so every image in that email would have
    # been a broken box and nothing in the pipeline fetches a URL to find out.
    on_disk = sorted(x.name for x in (run_dir(REAL) / "thumbs").glob("slide-*-thumb.*"))
    ok(f"every thumbnail on disk is in the email ({len(on_disk)} of them)",
       all(n in p["body"] for n in on_disk), str(on_disk[:2]))
    ok("...and the extension comes from disk rather than from this file",
       all(f'thumb{pathlib.Path(n).suffix}"' in p["body"] for n in on_disk[:1]))

    # A LINK THIS EMAIL CANNOT VERIFY IS NOT SENT. Both failure modes, by exception.
    try:
        payload(**{**base, "run": "1999-01-01"})
        ok("a run with no artifacts refuses to build an email", False, "it built one")
    except MissingAsset:
        ok("a run with no artifacts refuses to build an email", True)
    try:
        payload(**{**base, "slides": 999})
        ok("...and a declared slide count that disagrees with disk is an error", False)
    except MissingAsset:
        ok("...and a declared slide count that disagrees with disk is an error", True)

    # THE PAYLOAD IS A SHIPPED ARTIFACT. It defaulted under gitignored `out/`, so no run has
    # ever committed the email it produced and no gate could read one.
    ok("the payload's home is the run directory, not scratch",
       "runs" in str(run_dir(REAL)) and "out" not in run_dir(REAL).parts)

    # THE POST IS ACTIONABLE FROM THE EMAIL ALONE. This is the whole complaint that opened
    # this file's second draft: an email that describes the run and does not carry the post is
    # a status report, and the reader still has to go and find the repository.
    ok("the email carries the post copy verbatim",
       e(base["caption"]) in p["body"])
    ok("...and the first comment verbatim", e(base["first_comment"]) in p["body"])
    ok("...and says what to do with them", "as a <strong>document</strong>" in p["body"]
       and "first comment within" in p["body"].replace("\n", " "))
    ok("the caption is escaped, so markup in copy cannot break the email",
       "&lt;b&gt;" in payload(**{**base, "caption": "<b>x</b>"})["body"])

    ok("the email says plainly that nothing was sent",
       "This is a draft. Nothing was sent." in p["body"])
    ok("...and that the merge already happened",
       "already merged to main" in p["body"])
    # A HELD RUN MUST NOT CLAIM THE MERGE. The footer said the deck was on main whatever the score.
    try:
        set_ref("some/run-branch")
        held = payload(**{**base, "score": 6.8})
        ok("a held run's footer does not claim a merge that did not happen",
           "already merged to main" not in held["body"]
           and "did NOT merge" in held["body"])
    finally:
        set_ref(DEFAULT_REF)

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
    # NO DEFAULT. Nine was the default and nine is the usual deck, so a run that shipped eight
    # would have been emailed as nine with one dead image. Left unset the count is measured
    # from the thumbnails on disk, which is the only number that describes what actually
    # rendered. Pass it only to ASSERT a count, and a disagreement is then an error.
    ap.add_argument("--slides", type=int, default=None)
    ap.add_argument("--ref", default=DEFAULT_REF,
                    help="the git ref the image URLs point at. A run that HOLDS "
                         "does not merge, so it passes its run branch here or the "
                         "email links eight broken images on main")
    ap.add_argument("--caption-file")
    ap.add_argument("--comment-file")
    ap.add_argument("--gates-file", help="json object of gate name to result")
    ap.add_argument("--degraded-file", help="json array of what this run did not do in full")
    ap.add_argument("--upgrades-file", help="json array of {what, why} the machine changed")
    ap.add_argument("--notes-file", help="the account of the day: verified, admitted, held")
    ap.add_argument("--out", help="write the payload here for the connector call")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    set_ref(a.ref)

    if a.self_test:
        return self_test()
    if not a.run:
        ap.print_help()
        return 0

    def read(p):
        return Path(p).read_text(encoding="utf-8").strip() if p and Path(p).exists() else ""

    # THE CAPTION AND THE FIRST COMMENT DEFAULT TO THE RUN'S OWN FILES. Every run writes them
    # to the same two names, so making the caller pass paths was one more thing to get wrong on
    # the way to the one email a human reads.
    cap = a.caption_file or run_dir(a.run) / "caption.txt"
    com = a.comment_file or run_dir(a.run) / "first_comment.txt"
    caption, first_comment = read(cap), read(com)
    if not caption:
        print(f"gmail_draft: {cap} is empty or missing. An email with no post copy is the "
              f"defect this builder exists to prevent", file=sys.stderr)
        return 1
    if not first_comment:
        print(f"gmail_draft: {com} is empty or missing. The source block is the half of the "
              f"post that carries the evidence", file=sys.stderr)
        return 1

    p = payload(run=a.run, n=a.n, title=a.title, caption=caption,
                first_comment=first_comment, score=a.score, threshold=a.threshold,
                slides=a.slides,
                gates=json.loads(read(a.gates_file) or "{}"),
                degraded=json.loads(read(a.degraded_file) or "[]"),
                upgrades=json.loads(read(a.upgrades_file) or "[]"),
                notes=read(a.notes_file))
    # THE PAYLOAD IS A SHIPPED ARTIFACT, NOT SCRATCH. It used to default under `out/`, which is
    # gitignored, so no run has ever committed the email it sent and there was nothing for a
    # gate to check. `email_check.py` reads this file, and it can only do that if the file is
    # in the run directory beside the deck it describes.
    out = Path(a.out) if a.out else run_dir(a.run) / "gmail_payload.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(p, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"gmail_draft: payload written to {out}")
    print(f"  to: {p['to']}\n  subject: {p['subject']}")
    print(f"  {len(thumbs(a.run, a.slides))} slide thumbnail(s), every linked file verified "
          f"present")
    print("  DRAFT ONLY. Pass this file to the Gmail connector's create_draft. Never send.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"gmail_draft: broke: {exc}", file=sys.stderr)
        sys.exit(1)
