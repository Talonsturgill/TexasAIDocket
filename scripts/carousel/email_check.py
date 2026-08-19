#!/usr/bin/env python3
"""email_check.py — the run's email is the payload the builder produced, and it is postable.

THE DEFECT THIS EXISTS FOR, in the owner's words: "look at the email you sent me on run #2, and
then look at the email I sent me on run #1. run #2 was like WAY off idk wtf u were thinking as
far as the Gmail payload."

Run #1 called `gmail_draft.py` and mailed what it produced: an HTML page with the score, the
gate table, the nine thumbnails, the PDF, the post copy and the first comment. Run #2 did not
call it at all. It hand-wrote a long plaintext essay about how the run had gone, with **no post
copy, no first comment, no PDF link and no images**, and closed by telling the reader which two
files to go and open in the repository.

That is the whole failure and it is worth naming precisely, because it does not look like one
from the inside. The prose was accurate. Every fact in it was true. It was still the wrong
artifact, because **this email is the only human touchpoint and it gates the POST**. An email
that cannot be posted from has not done the one job it has, however well written it is.

WHY A HAND-WRITTEN EMAIL COULD HAPPEN AT ALL, which is the real hole. `gmail_draft.py` existed,
worked, and was connected to nothing. No gate read its output, no artifact recorded that it had
run, and its payload defaulted into gitignored `out/`, so a run that skipped it left no trace
and a run that used it left no evidence either. A builder nothing checks is a suggestion.

WHAT THIS CHECKS, and every item is a thing that has actually gone wrong:

  1. The payload exists in the run directory. If it is missing, the email was hand-written or
     was never built, and there is nothing to audit.
  2. It is HTML. Run #2's was plaintext, which is what an essay looks like.
  3. It carries `caption.txt` VERBATIM. This is the post. Its absence is the defect above.
  4. It carries `first_comment.txt` VERBATIM. This is the evidence the post rests on.
  5. It links the PDF and one thumbnail per rendered slide, and every one of those files is on
     disk. `gmail_draft` hardcoded `.png` while the 2026-08-18 render wrote `.webp`, so every
     image in that email would have been a broken box.
  6. The caption's hashtag block survived into the email. Run #1 mailed three tags, run #2 mailed
     none, and both passed every gate, because `brand.yaml` set a count that nothing enforced.
     `caption_check.py` owns the count and the placement; this owns the trip into the payload.
  7. It names the score, whatever the score is.
  8. It says nothing was sent, because that promise is in CLAUDE.md and the email is where a
     reader would look for it.

WHY VERBATIM AND NOT "CONTAINS SOMETHING LIKE". A summary of the post copy is the same failure
one size down. The reader has to be able to select the block and paste it, so the block has to
be the file, character for character, HTML-escaped and no more.

    email_check.py --run 2026-08-18
    email_check.py --all
    email_check.py --self-test
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNS = REPO_ROOT / "runs" / "carousel"

PAYLOAD = "gmail_payload.json"
THUMB_EXTS = (".png", ".webp", ".jpg", ".jpeg")

# The same shape `caption_check.HASHTAG` matches. Repeated rather than imported because this file
# reads shipped artifacts and must keep working on a run whose caption predates that gate.
HASHTAG = re.compile(r"#[A-Za-z][A-Za-z0-9]*")

# RUNS THAT SHIPPED BEFORE THE TAG RULE WAS ENFORCED, EXEMPT BY NAME.
#
# `--all` reads every shipped run, so a new rule applied to history turns CI red over a post that
# went out weeks ago. There are two ways out and only one of them is honest. Editing
# `runs/carousel/2026-08-18/caption.txt` to add the tags it never had would make this green by
# rewriting what was published, which CLAUDE.md puts on the short list of things that stop and
# ask, and it would leave the record saying that run did something it did not do.
#
# So the run is named here instead. The rule starts on 2026-08-19 and history keeps what actually
# happened. NOTHING IS EVER ADDED TO THIS SET. A second entry would mean a run shipped tagless
# after the gate existed, and the fix for that is the caption, never this line. The exemption is
# printed rather than applied silently, because an exemption nobody sees is a rule nobody has.
TAGS_EXEMPT = {"2026-08-18"}


def _hashtags(text: str) -> list:
    """The tag block in a caption, with url fragments excluded the way the caption gate does."""
    return HASHTAG.findall(re.sub(r"https?://\S+", " ", text))


def check_run(d: Path) -> list:
    """Every way this run's email fails to be a postable email. Empty means clean."""
    bad = []
    run = d.name
    pf = d / PAYLOAD

    if not pf.exists():
        return [f"{run}: no {PAYLOAD}. The email was hand-written or never built. "
                f"Run scripts/carousel/gmail_draft.py --run {run} and draft from its output"]
    try:
        p = json.loads(pf.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{run}: {PAYLOAD} is not JSON ({exc})"]

    body = str(p.get("body", ""))
    if not p.get("isHtml"):
        bad.append(f"{run}: the payload is not marked HTML. Run 2's email was a plaintext "
                   f"essay and that is what this flag distinguishes")
    if not str(p.get("to", "")).strip() or "@" not in str(p.get("to", "")):
        bad.append(f"{run}: no recipient address on the payload")
    if str(p.get("to")) == "me":
        bad.append(f"{run}: the recipient is 'me', which the Gmail connector rejects outright")
    if not str(p.get("subject", "")).strip():
        bad.append(f"{run}: no subject")

    # ---- the post itself, verbatim ------------------------------------------------------
    for name, what in ((("caption.txt"), "post copy"), ("first_comment.txt", "first comment")):
        f = d / name
        if not f.exists():
            bad.append(f"{run}: {name} is missing, so the run has no {what} to mail")
            continue
        text = f.read_text(encoding="utf-8").strip()
        if not text:
            bad.append(f"{run}: {name} is empty")
        elif html.escape(text, quote=True) not in body:
            bad.append(f"{run}: the email does not carry {name} verbatim. This is the "
                       f"defect the whole check exists for. A reader has to be able to select "
                       f"the {what} and paste it, so it has to be the file character for "
                       f"character")

    # ---- the tag block actually reached the draft ----------------------------------------
    #
    # The verbatim check above already implies this, and it is asserted separately anyway,
    # because the owner reads the EMAIL rather than `caption.txt` and this is the surface the
    # defect was reported on. Run No. 1 mailed "#GrimesCounty #ERCOT #Terafab" and run No. 2
    # mailed a post with no tags at all, past a green suite. `caption_check` is what enforces the
    # count and the placement; this only proves the block survived the trip into the payload, so
    # a future builder that strips or escapes it away fails here rather than in somebody's feed.
    cap = d / "caption.txt"
    if cap.exists():
        tags = _hashtags(cap.read_text(encoding="utf-8"))
        if not tags and run in TAGS_EXEMPT:
            print(f"  note  {run}: shipped before the tag rule and is exempt by name. "
                  f"History keeps what was published", file=sys.stderr)
        elif not tags:
            bad.append(f"{run}: caption.txt carries no hashtags. The post takes the count set in "
                       f"config/brand.yaml, and scripts/carousel/caption_check.py is the gate "
                       f"that enforces it. This run's post would publish with no tag block")
        for t in tags:
            if t not in body and html.escape(t, quote=True) not in body:
                bad.append(f"{run}: the hashtag {t} is in caption.txt but not in the email. The "
                           f"tag block has to survive into the draft, because the draft is what "
                           f"gets posted")

    # ---- every link resolves to a file that shipped -------------------------------------
    pdf = d / "carousel.pdf"
    if not pdf.exists():
        bad.append(f"{run}: carousel.pdf is missing, so there is nothing to upload")
    elif "carousel.pdf" not in body:
        bad.append(f"{run}: the email does not link the PDF, which is the thing being posted")

    thumbs = sorted(x for x in (d / "thumbs").glob("slide-*-thumb.*")
                    if x.suffix.lower() in THUMB_EXTS)
    if not thumbs:
        bad.append(f"{run}: no slide thumbnails on disk")
    for t in thumbs:
        if t.name not in body:
            bad.append(f"{run}: {t.name} shipped but is not in the email. A thumbnail named "
                       f"with the wrong extension is a broken image and nothing here fetches "
                       f"a URL to find out")

    # ---- the verdict, and the promise ---------------------------------------------------
    score = (json.loads((d / "score.json").read_text(encoding="utf-8"))
             if (d / "score.json").exists() else {})
    # THE SCORER'S OWN FIELD NAME, whatever it is called. `weighted_score` is what this repo's
    # rubric writes and the first draft of this check looked for `total`, so it read no score
    # on every real run and silently skipped the one assertion about the verdict. A check that
    # cannot find the number it checks reports clean, which is the failure this file is about.
    total = next((score[k] for k in
                  ("weighted_score", "weighted_total", "total", "score") if k in score), None)
    if total is not None and str(total) not in body:
        bad.append(f"{run}: the email does not state the score ({total}). The verdict goes "
                   f"near the top whatever it says")
    if "Nothing was sent" not in body:
        bad.append(f"{run}: the email does not say that nothing was sent, which is the "
                   f"promise CLAUDE.md makes on this routine's behalf")
    return bad


def shipped_runs() -> list:
    """Run directories that produced a deck. A run with no caption never had an email to send."""
    if not RUNS.is_dir():
        return []
    return sorted(d for d in RUNS.iterdir() if d.is_dir() and (d / "caption.txt").exists())


def self_test() -> int:
    """Prove it bites, on each of the four failures that have actually happened."""
    import tempfile
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import gmail_draft                                              # noqa: E402
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    def build(tmp, *, payload=True, is_html=True, with_caption=True, with_thumb=True,
              caption_tags=True, tags_in_body=True):
        d = Path(tmp) / "2026-01-01"
        (d / "thumbs").mkdir(parents=True)
        cap = "The post copy.\n\n#Texas #ERCOT #Grid" if caption_tags else "The post copy."
        (d / "caption.txt").write_text(cap, encoding="utf-8")
        (d / "first_comment.txt").write_text("Sources.", encoding="utf-8")
        (d / "carousel.pdf").write_bytes(b"%PDF")
        (d / "thumbs" / "slide-01-thumb.webp").write_bytes(b"x")
        body = ("<div>carousel.pdf slide-01-thumb.webp "
                + ((cap + " ") if with_caption else "")
                + "Sources. Nothing was sent.</div>")
        if not tags_in_body:
            for _t in ("#Texas", "#ERCOT", "#Grid"):
                body = body.replace(_t, "")
        if not with_thumb:
            body = body.replace("slide-01-thumb.webp ", "")
        if payload:
            # THE ADDRESS COMES FROM `gmail_draft.DRAFT_TO`, never typed again here. CLAUDE.md
            # says the mailbox lives in exactly two places so a repoint is one edit, and a
            # fixture that hardcodes it is a third. `port_audit`'s residue rule caught this
            # copy, which is the rule doing precisely its job.
            (d / PAYLOAD).write_text(json.dumps(
                {"to": gmail_draft.DRAFT_TO, "subject": "s", "body": body,
                 "isHtml": is_html}), encoding="utf-8")
        return d

    with tempfile.TemporaryDirectory() as t:
        ok("a well formed payload passes", not check_run(build(t)))
    with tempfile.TemporaryDirectory() as t:
        bad = check_run(build(t, payload=False))
        ok("a hand-written email is caught, because it leaves no payload",
           any("no gmail_payload.json" in b for b in bad), str(bad))
    with tempfile.TemporaryDirectory() as t:
        bad = check_run(build(t, is_html=False))
        ok("a plaintext essay is caught", any("not marked HTML" in b for b in bad), str(bad))
    with tempfile.TemporaryDirectory() as t:
        bad = check_run(build(t, with_caption=False))
        ok("an email with no post copy is caught",
           any("caption.txt verbatim" in b for b in bad), str(bad))
    # THE TAG BLOCK. Run No. 2 mailed a post with none and every gate was green.
    with tempfile.TemporaryDirectory() as t:
        bad = check_run(build(t, caption_tags=False))
        ok("a caption with no hashtags is caught",
           any("no hashtags" in b for b in bad), str(bad))
    # THE EXEMPTION IS NARROW AND CANNOT GROW INTO A LOOPHOLE. A dated run that predates the rule
    # is excused; every other tagless run still fails, which is the property that matters.
    ok("the exemption names exactly the one run that predates the rule",
       TAGS_EXEMPT == {"2026-08-18"}, str(TAGS_EXEMPT))
    ok("...and a tagless run outside it still fails",
       "2026-01-01" not in TAGS_EXEMPT)
    with tempfile.TemporaryDirectory() as t:
        bad = check_run(build(t, tags_in_body=False))
        ok("a tag block that did not survive into the email is caught",
           any("not in the email" in b for b in bad), str(bad))

    with tempfile.TemporaryDirectory() as t:
        bad = check_run(build(t, with_thumb=False))
        ok("a thumbnail the email misses is caught",
           any("shipped but is not in the email" in b for b in bad), str(bad))

    if failures:
        print(f"\nemail_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nemail_check self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", help="one run date, e.g. 2026-08-18")
    ap.add_argument("--all", action="store_true", help="every run that shipped a deck")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()

    if a.self_test:
        return self_test()

    targets = [RUNS / a.run] if a.run else shipped_runs()
    if not targets:
        print("email_check: no shipped run to check")
        return 0

    bad = []
    for d in targets:
        if not d.is_dir():
            print(f"email_check: {d} is not a run directory", file=sys.stderr)
            return 1
        bad += check_run(d)

    for line in bad:
        print(f"  {line}")
    if bad:
        print(f"\nemail_check: {len(bad)} problem(s) across {len(targets)} run(s). The email "
              f"is the only human touchpoint and it gates the post, so an email a reader "
              f"cannot post from has not done its job.", file=sys.stderr)
        return 1
    print(f"email_check: {len(targets)} run(s), every email built by the builder and postable "
          f"from the mail alone")
    return 0


if __name__ == "__main__":
    sys.exit(main())
