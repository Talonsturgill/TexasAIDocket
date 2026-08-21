#!/usr/bin/env python3
"""scanner_sync_check.py — the published scan page and the scanner repo agree on the contract.

WHY THIS EXISTS

The scan form exists twice. This repo builds `docs/scan/index.html` from `scan_page()` in
`site_build.py`; the scanner repo keeps `web/scan.html`. Neither reads the other, and they are
SUPPOSED to look different, because this one is wrapped in the site shell with cards and a nav.
What they are not allowed to disagree about is the contract between them.

THE DEFECT IT EXISTS FOR, which had already happened twice:

  The scanner turned the captcha ON with a written rationale about abuse discipline, its repo law
  said so, and the published page stayed at `_captcha=false`. The fix landed in a file nothing
  serves. A reader met the old form, and the only defense left standing was a honeypot that a bot
  posting only the named fields never touches.

  Before that, the scanner's copy still read "Give us your website. We read what is public" after
  the published page had been rewritten out of the first person.

Both are the same shape: **a change to the scanner's copy does not reach a reader.** Only a
change here does. So the scanner's copy is vendored under `vendor/scanner/` and this compares
the two.

WHAT IT CHECKS, AND AGAINST WHAT

  from vendor/scanner/scan.html  (THE CONTRACT, never served, pinned by sha256)
    FIELDS    the form field names, compared exactly. Phase 0 of the scan routine parses these
              out of the forwarded mail, so a rename here means a request arrives without the key
              the routine reads, and nothing throws.
    HIDDEN    the values of `_subject` and `_captcha`. `_subject` is how two forms sharing one
              mailbox are told apart. `_captcha` is half the abuse defense.
    PROMISES  compared as COMMITMENTS rather than as prose. The text is normalised and each
              promise is looked for as a phrase, so either side may reword and neither may drop
              one. "No list." and "no list," are the same promise.

  It also verifies the vendored file against the sha256 in its own README, which closes the
  obvious cheat: editing the vendored copy to make the check pass, instead of fixing the page.

WHAT IT CANNOT SEE. It cannot tell you the pin is current. Nothing here reaches the scanner repo,
so if that repo's form moves and nobody re-vendors, this compares against a contract one revision
stale and reports clean. That is a deliberate trade, written up in the vendored README: a gate
that fetched upstream at build time would be green or red depending on another repo at that
moment, which is worse for a build gate than a stale pin a human moves on purpose.

  scanner_sync_check.py
  scanner_sync_check.py --self-test

Exit 0 clean, 1 a disagreement, 2 could not run.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
VENDORED = REPO / "vendor" / "scanner" / "scan.html"
VENDOR_README = REPO / "vendor" / "scanner" / "README.md"
PUBLISHED = REPO / "docs" / "scan" / "index.html"

# The promises, as commitments. Each is a phrase that must survive normalisation on BOTH sides.
# Kept short on purpose: the longer the phrase, the more it polices wording rather than meaning,
# and the two pages are allowed to read differently.
PROMISES = [
    ("one report goes to one address", "one report to one address"),
    ("there is no list", "no list"),
    ("there is no follow up sequence", "no follow up sequence"),
    ("there is no second email", "no second email"),
    ("every line traces to the requester's own pages", "traces to a page on your"),
]

# The hidden fields whose VALUE is part of the contract rather than presentation.
CONTRACT_VALUES = ("_subject", "_captcha")

FIELD_RE = re.compile(r"<(?:input|textarea)\b[^>]*\bname=\"([^\"]+)\"[^>]*>", re.I)
VALUE_RE = re.compile(r"<input\b[^>]*\bname=\"{name}\"[^>]*\bvalue=\"([^\"]*)\"", re.I)
TAGS_RE = re.compile(r"<(script|style)\b.*?</\1>|<!--.*?-->|<[^>]+>", re.S | re.I)


# THE SCAN FORM, NOT THE WHOLE DOCUMENT.
#
# This read every field on the page, which was right for exactly as long as the scan form was
# the only form on it. The footer's contact dialog put a second one on every page of the site,
# and the check went red saying the published page posts a `_template` the scanner has no
# contract for. It does not: a different form does, in the footer, and the scanner has no
# business knowing about it.
#
# The quieter half is the one worth naming. `hidden_value` takes the FIRST match in document
# order, so `_captcha` was being read off whichever form came first in the file. The scan form
# happens to sit above the footer, so it was still reading the right one, by luck rather than
# by rule, and any future reordering would have had the scan page's captcha checked against a
# dialog's.
#
# BOTH SIDES ARE SCOPED THE SAME WAY, by the class the vendored contract itself uses. If that
# class is ever renamed this RAISES rather than falling back to the document, because a scoping
# that silently stops scoping is worse than none: it goes green while checking the wrong thing.
FORM_CLASS = "leadform"
FORM_RE = re.compile(r"<form\b[^>]*\bclass=\"[^\"]*\bleadform\b[^\"]*\"[^>]*>(.*?)</form>",
                     re.S | re.I)


class NoScanForm(Exception):
    """The document holds no form marked as the scan form."""


def scan_form(html: str, where: str) -> str:
    """The scan form's own markup, from a document that may hold several forms."""
    m = FORM_RE.search(html)
    if not m:
        raise NoScanForm(
            f"{where} holds no <form> with class {FORM_CLASS!r}, so there is nothing to read the "
            f"contract off. Either the scan form was renamed, in which case rename it here too, "
            f"or the page stopped carrying it, which is a bigger problem than this check.")
    return m.group(1)


def fields(html: str) -> set[str]:
    """Every field name the SCAN FORM posts."""
    return set(FIELD_RE.findall(html))


def hidden_value(html: str, name: str) -> str | None:
    m = re.search(VALUE_RE.pattern.replace("{name}", re.escape(name)), html, re.I)
    return m.group(1) if m else None


def normalise(html: str) -> str:
    """The words a reader sees, flattened so punctuation cannot make two equal promises differ.

    Tags out, entities resolved, everything that is not a letter or a digit becomes one space.
    "One report to one address. No list." and "one report to one address, no list" both come out
    as the same run of words, which is the point: this checks the COMMITMENT, not the prose.
    """
    import html as _html
    text = _html.unescape(TAGS_RE.sub(" ", html))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def pinned_sha() -> str | None:
    """The sha256 the vendored README claims for the file beside it."""
    if not VENDOR_README.is_file():
        return None
    m = re.search(r"sha256.*?`([0-9a-f]{64})`", VENDOR_README.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def compare(contract: str, published: str) -> list[str]:
    """Everything the two documents disagree about. Empty means they hold the same contract."""
    bad: list[str] = []

    # ---- the field names, exactly. This is the machine half of the contract.
    try:
        cform, pform = scan_form(contract, "the vendored contract"), \
            scan_form(published, "the published page")
    except NoScanForm as exc:
        return [str(exc)]
    cf, pf = fields(cform), fields(pform)
    for missing in sorted(cf - pf):
        bad.append(f"the published page has no field named {missing!r}, and the scanner's form "
                   f"does. Phase 0 parses that key out of the forwarded mail, so a request would "
                   f"arrive without it and nothing would throw.")
    for extra in sorted(pf - cf):
        bad.append(f"the published page posts a field named {extra!r} that the scanner's form "
                   f"does not have, so the routine has no contract for it.")

    # ---- the hidden values that are contract rather than presentation
    for name in CONTRACT_VALUES:
        cv, pv = hidden_value(cform, name), hidden_value(pform, name)
        if cv is None and pv is None:
            continue
        if cv != pv:
            bad.append(f"{name} is {pv!r} on the published page and {cv!r} in the scanner's "
                       f"form. One of them is wrong, and the published page is the one a "
                       f"requester actually meets.")

    # ---- the promises, as commitments
    nc, np_ = normalise(contract), normalise(published)
    for label, phrase in PROMISES:
        in_c, in_p = phrase in nc, phrase in np_
        if in_c and not in_p:
            bad.append(f"the scanner's form promises that {label} and the published page does "
                       f"not. The published page is what a requester agreed to.")
        elif in_p and not in_c:
            bad.append(f"the published page promises that {label} and the scanner's form does "
                       f"not, so the routine is not on the hook for it.")
    return bad


def check(verbose: bool = True) -> list[str]:
    bad: list[str] = []
    if not VENDORED.is_file():
        return [f"{VENDORED.relative_to(REPO)} is missing, so there is no contract to check "
                f"the published page against"]
    if not PUBLISHED.is_file():
        return [f"{PUBLISHED.relative_to(REPO)} is missing. The scan page is not built, so the "
                f"front door this checks does not exist."]

    raw = VENDORED.read_bytes()
    want = pinned_sha()
    got = hashlib.sha256(raw).hexdigest()
    if want is None:
        bad.append("vendor/scanner/README.md records no sha256, so the vendored contract could "
                   "have been edited to agree with the page instead of the other way round")
    elif want != got:
        bad.append(f"the vendored contract does not match the sha256 its README pins "
                   f"({got[:12]} against {want[:12]}). Either it was hand-edited here, which it "
                   f"must never be, or it was re-vendored without updating the pin.")

    bad += compare(raw.decode("utf-8"), PUBLISHED.read_text(encoding="utf-8"))
    if verbose and not bad:
        cf = fields(scan_form(raw.decode("utf-8"), "the vendored contract"))
        print(f"scanner sync: clean. {len(cf)} field(s) and {len(PROMISES)} promise(s) agree, "
              f"vendored contract matches its pin")
    return bad


# ---------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    base = """<section><p>One report to one address. No list, no follow-up sequence, no second
    email. Every line traces to a page on your own site. A person reads every report before it
    goes out.</p>
    <form class="leadform" action="x">
    <input type="hidden" name="_subject" value="Texas AI Docket, scan">
    <input type="hidden" name="_captcha" value="true">
    <input type="text" name="_honey"><input name="website" type="text" required>
    <input name="email" type="email" required><textarea name="message"></textarea></form></section>"""

    ok("two identical documents agree", not compare(base, base), str(compare(base, base)))

    # THE PROSE IS ALLOWED TO DIFFER. This is the whole reason promises are normalised.
    reworded = base.replace("One report to one address. No list, no follow-up sequence, no second\n    email.",
                            "One report to one address; no list; no follow-up sequence; no second email!")
    ok("rewording and repunctuating a promise is NOT a disagreement",
       not compare(base, reworded), str(compare(base, reworded)))

    # THE CAPTCHA, which is the defect this file was written for.
    off = base.replace('name="_captcha" value="true"', 'name="_captcha" value="false"')
    got = compare(base, off)
    ok("the captcha differing is caught", any("_captcha" in p for p in got), str(got[:1]))
    ok("...and the message says the published page is the one a requester meets",
       any("requester actually meets" in p for p in got))

    # A FIELD RENAME, which is the silent one.
    renamed = base.replace('name="website"', 'name="site_url"')
    got = compare(base, renamed)
    ok("a renamed field is caught in both directions", len(got) >= 2, str(got))
    ok("...and the message says the routine would get a request without that key",
       any("nothing would throw" in p for p in got))

    # A DROPPED PROMISE.
    dropped = base.replace("no second\n    email. ", "")
    got = compare(base, dropped)
    ok("a promise dropped from the published page is caught",
       any("no second email" in p or "second email" in p for p in got), str(got[:1]))

    # AND A PROMISE THE PAGE MAKES THAT THE ROUTINE IS NOT ON THE HOOK FOR.
    extra = base.replace("One report", "There is no list. One report")
    thin = base.replace("No list, ", "")
    got = compare(thin, extra)
    ok("a promise on the page that the contract does not carry is caught",
       any("not on the hook" in p for p in got), str(got[:1]))

    # NORMALISATION does not swallow a real difference into a match.
    # ---- the scoping ---------------------------------------------------------
    # A SECOND FORM ON THE PAGE IS NOT THE SCAN FORM'S BUSINESS. The footer's contact dialog put
    # one on every page of the site, and unscoped this reported its `_template` as a field the
    # scanner has no contract for. It has no contract for it because it is not its form.
    footer = base + """<footer><dialog><form id="contactform" action="x">
    <input type="hidden" name="_template" value="table">
    <input type="hidden" name="_captcha" value="false">
    <textarea name="message"></textarea></form></dialog></footer>"""
    ok("another form on the page is not read as the scan form's",
       not compare(base, footer), str(compare(base, footer)))
    # And the quiet half: a hidden value must come off the scan form rather than off whichever
    # form happens to appear first in the file.
    above = """<footer><form id="contactform" action="x">
    <input type="hidden" name="_captcha" value="false"></form></footer>""" + base
    ok("...even when it sits ABOVE the scan form in the document",
       not compare(base, above), str(compare(base, above)))
    # A SCOPING THAT SILENTLY STOPS SCOPING IS WORSE THAN NONE, so a renamed class is loud.
    renamed_form = base.replace('class="leadform"', 'class="scanform"')
    problems = compare(base, renamed_form)
    ok("a renamed form class fails loudly rather than falling back to the document",
       len(problems) == 1 and "no <form> with class" in problems[0], str(problems))

    ok("normalise flattens punctuation but keeps the words",
       normalise("<p>One report, to one address!</p>") == "one report to one address")

    # THE REAL FILES. A fixture proves the checker works and says nothing about this repo.
    real = check(verbose=False)
    ok("the vendored contract and the published page agree", not real,
       "\n      " + "\n      ".join(real))
    ok("...and the vendored file matches the sha256 its README pins",
       VENDORED.is_file() and pinned_sha() == hashlib.sha256(VENDORED.read_bytes()).hexdigest())

    if failures:
        print(f"\nscanner_sync_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nscanner_sync_check self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    try:
        problems = check()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"scanner_sync_check: cannot run: {exc}", file=sys.stderr)
        return 2
    if problems:
        print(f"scanner sync: {len(problems)} disagreement(s)\n", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
