# vendor/scanner

One file vendored from `Talonsturgill/TexasAIScanner`. It is **never edited here and never
served.** It exists so `scripts/site/scanner_sync_check.py` has something local to check the
published page against.

## Why a vendored copy at all

The scan form exists twice. This repo builds `docs/scan/index.html` from `scan_page()` in
`scripts/site/site_build.py`, and the scanner repo keeps `web/scan.html`. Neither reads the
other. They are two hand-maintained sides of one flow and they are SUPPOSED to look different,
because this one is wrapped in the site shell and carries the cards and the nav.

**What they are not allowed to disagree about is the contract between them.** CI cannot reach
across repos, so the contract has to be a committed artifact here or it is not checkable at all.

They had already drifted twice before this existed, in both directions:

- The scanner's copy still read "Give us your website. We read what is public" after the
  published page had been rewritten out of the first person.
- The scanner turned the captcha ON with a written rationale about abuse discipline, and the
  published page stayed at `false` for a day, because the fix landed in a file nothing serves.

The second one is the shape that matters. **A change to the scanner's copy does not reach a
reader.** Only a change here does.

## scan.html, the contract and not a design

**This file is not a specification and must never be copied over the live page.** It is the
scanner repo's own form, and what the check reads out of it is narrow:

| what | why it must match |
| --- | --- |
| the form FIELD NAMES | Phase 0 of the scan routine parses these out of the forwarded mail. Rename one here and a request arrives without the key the routine reads, silently |
| the hidden field VALUES (`_subject`, `_captcha`) | `_subject` is how the two forms are told apart in one mailbox. `_captcha` is half the abuse defense |
| the PROMISES | one report, one address, no list, no follow-up sequence, no second email, a person reads it, every line traces to the requester's own pages |

The promises are compared as COMMITMENTS, not as prose. The text is normalised and each promise
is looked for as a phrase, so either side may reword and neither may drop one. That is the whole
point: "One report to one address. No list." and "One report to one address, no list," are the
same promise and the check has no opinion about which reads better.

## The pin

| field | value |
| --- | --- |
| repo | `Talonsturgill/TexasAIScanner` |
| path | `web/scan.html` |
| last changed at | `af5d8973c6ad71b918ee40c030fa8ea7e6a15f87` (branch `main`) |
| sha256 | `111c89a3d67a4dbf4188f1b3b384282234bacc0b6270f90220b88f9c2a752ba3` |
| bytes | `8453` |

The commit is the one that last CHANGED the file, not whatever `main` happens to be at, so
re-vendoring says a file moved only when it did.

`scanner_sync_check.py` verifies this sha256 against the file beside it. That closes the obvious
cheat: editing the vendored copy to make the check pass instead of fixing the page fails, because
the pin above no longer matches.

## What this cannot see, stated plainly

**It cannot tell you the pin is current.** Nothing here reaches the scanner repo, so if that
repo's `web/scan.html` moves and nobody re-vendors, this check keeps comparing the published
page against a contract that is one revision stale and reports clean. Re-vendoring is a
deliberate maintainer step: copy the file, update the three pin rows above, commit.

That limit is worth writing down rather than designing around. A check that quietly fetched the
upstream file at build time would be green or red depending on somebody else's repo at that
moment, which is a worse property for a build gate than a stale pin a human moves on purpose.
