#!/usr/bin/env python3
"""claims_check.py — the contract between the fact-checker and everything downstream.

WHY THIS EXISTS, BEFORE IT HAS EVER BEEN NEEDED

The fact-checker is an AGENT. It is given a schema in `.claude/agents/carousel-fact-checker.md`
and asked to return JSON, and nothing about that arrangement guarantees it returns the same shape
twice. In the sibling product it drifted, and the drift is worth reading in full because it is
the argument for this file:

  - the container was named `claims`, `verified_claims`, `docket_claims`, and twice the story's
    own codename
  - the same field appeared as `claim`, `text` and `statement`
  - the source appeared as `source_url`, `url` and `evidence_url`
  - one run nested the url, the outlet and the date inside an `evidence` object
  - four runs recorded no per-slide copy at all

None of it was visible, because nothing downstream read the file closely enough to complain. The
site published anyway and **the verification record rendered empty on 14 of 18 decks.** The whole
promise of this project is that every fact traces to a fetched source, and for fourteen decks the
page that demonstrates it was blank.

Texas has shipped zero decks, which is exactly when to install this. A gate written after the
drift is archaeology. A gate written before it is a contract.

WHAT IT IS STRICT ABOUT, AND WHAT IT LEAVES ALONE

Strict about the handful of fields the public site depends on, quiet about everything else. The
fact-checker should stay free to record MORE than the minimum, because the extra is often what a
later run needs. It is not free to record less, or to rename what it records.

THE SPEC THE AGENT READS IS PART OF THIS GATE (2026-08-18)

Texas's second deck rediscovered the drift in one run: the fact-checker returned `source_url`
for `url`, `journalism` for `secondary_reported`, `dropped` for `rejected`, and no `retrieved`
at all, and the showrunner repaired the file by hand across four rejections. The gate was right
every time. **The agent was guessing, because the only schema it had was a worked example with
`"url": "the page you fetched"` in it, and the source taxonomy was written as prose advice in a
different section of the file with none of its four values spelled out.**

So this file now owns the spec as well as the check. `--template` prints a valid skeleton
BUILT FROM THE CONSTANTS BELOW, and `--self-test` runs `check()` over the JSON example in
`.claude/agents/carousel-fact-checker.md` and asserts that spec names every required field and
every source type. A schema written twice is wrong in both places eventually; this is what makes
the second copy fail loudly instead.

    claims_check.py --date 2026-08-12
    claims_check.py --file out/2026-08-12/claims.json
    claims_check.py --template
    claims_check.py --self-test

Exit 0 clean, 1 on a hard failure, 2 if the file cannot be read at all.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# THE CONTAINER. One name, and the alternatives are named here so the error can say "you called
# it verified_claims and it is called claims" rather than "missing key".
CONTAINER = "claims"
CONTAINER_ALIASES = ("verified_claims", "docket_claims", "facts", "findings", "verified")

# THE FIELDS THE SITE ACTUALLY READS. Each maps to the aliases seen in the wild, so a rename is
# reported as a rename. `text` is what the record states, `quote` is the verbatim string that
# proves it, and those two are not interchangeable: the whole gate rests on them being separate.
REQUIRED = {
    "id": ("claim_id", "cid", "ref"),
    "text": ("claim", "statement", "assertion"),
    "quote": ("verbatim", "verbatim_quote", "excerpt", "snippet"),
    "url": ("source_url", "evidence_url", "link", "source"),
    "source_type": ("type", "kind", "source_kind"),
    "retrieved": ("retrieved_at", "fetched", "date", "accessed"),
}

# The source taxonomy. A press release is evidence of a press release, and the agent is told so;
# this is where that distinction stops being advice and becomes a schema.
SOURCE_TYPES = {
    "primary_official",     # a filing, a statute, an agency page, a docket entry
    "primary_corporate",    # the company's own announcement. A claim, not a decision.
    "secondary_reported",   # a news report about one of the above
    "data",                 # a dataset or an API response
}

# ---------------------------------------------- ONE VOCABULARY, STATED TWICE (2026-09-03)
#
# `scripts/site/docket_build.py` carries its OWN `SOURCE_TYPES` and it is not this one.
#
#     deck                record              measured 2026-09-03
#     primary_official    primary_official    284 deck claims, 463 record claims
#     primary_corporate   primary_corporate    48 deck claims,   6 record claims
#     secondary_reported  journalism           71 deck claims,  80 record claims
#     data                absent                5 deck claims,   0 record claims
#
# The same news report needs two different words depending on which gate is reading, so every
# claim that moves from a deck into the record is renamed by hand. It has cost two runs already.
# On 2026-08-18 the fact-checker returned `journalism` and this gate refused it, which is one of
# the four renames in this file's own header. On 2026-09-03 three TOP500 claims went in as `data`
# and had to be rewritten `primary_official` before the record would take them.
#
# WHICH SET IS RIGHT IS NOT THIS FILE'S DECISION. `scripts/site/**` belongs to another lane, so an
# upgrade may READ it and may not change it, and reconciling a shared vocabulary from one side
# only would produce a THIRD statement of the same thing. That is the repo's oldest recurring
# shape and half a fix of it is worse than none.
#
# What this file can do is stop the divergence growing quietly and unaided. The record's set is
# IMPORTED rather than copied, every word here that the record does not hold has to be DECLARED
# below with what somebody renames it to, and an undeclared one fails the gate. This is the shape
# `config/parity_map.yaml` uses for the same problem: a divergence is data with a reason attached,
# never a silence.
#
# AND THE DECLARATION EXPIRES ON ITS OWN. If the record's vocabulary later takes one of these
# words, the divergence is over, the entry is reported as stale, and this table cannot become a
# permanent excuse for two files disagreeing. That is also the day somebody makes the two sided
# fix, and it is what tells them the other half is here.
RECORD_ONLY = {
    "secondary_reported": "renamed `journalism` at admission. Two words, one meaning, and neither "
                          "file owns the other's",
    "data": "the record has no word for a dataset at all. The 2026-09-03 run wrote "
            "`primary_official` for a TOP500 ranking table and that choice is not settled",
}


def record_source_types() -> set[str]:
    """`docket_build.SOURCE_TYPES`, imported. Never a copy kept here.

    A copy is the defect this block is about. A missing module RAISES rather than returning an
    empty set, because a divergence check that quietly passes when it cannot see the other side
    reports clean on exactly the day it is needed.
    """
    import importlib
    site = REPO_ROOT / "scripts" / "site"
    if str(site) not in sys.path:
        sys.path.insert(0, str(site))
    return set(importlib.import_module("docket_build").SOURCE_TYPES)


def vocabulary_problems(record: set[str] | None = None) -> list[str]:
    """Every undeclared divergence between this taxonomy and the record's, both directions."""
    record = record_source_types() if record is None else record
    out: list[str] = []
    for word in sorted(SOURCE_TYPES - record):
        if word not in RECORD_ONLY:
            out.append(
                f"source_type {word!r} is in this gate's taxonomy and not in "
                f"docket_build.SOURCE_TYPES ({sorted(record)}), and RECORD_ONLY does not declare "
                f"it. A claim carrying it cannot enter ledger/docket.json without somebody "
                f"renaming it by hand. Declare it with what it is renamed to, or use a word the "
                f"record already holds")
    for word in sorted(RECORD_ONLY):
        if word not in SOURCE_TYPES:
            out.append(f"RECORD_ONLY declares {word!r} and this gate's taxonomy no longer carries "
                       f"it. Delete the declaration")
        elif word in record:
            out.append(
                f"RECORD_ONLY declares {word!r} as a divergence and docket_build.SOURCE_TYPES now "
                f"holds it, so there is no divergence left. Delete the entry. This is the half of "
                f"the two sided fix that lives in this file")
    return out

ID_RE = re.compile(r"^c\d+$")
# A claim id has to be stable and referenceable, because slides and captions cite it.

MIN_QUOTE_WORDS = 4
# Below this a "quote" is a fragment that cannot be searched for in the source, which makes it
# unverifiable by the next person, which is the same as not having one.

MIN_QUOTE_CHARS = 28
# The word count is the right test for PROSE and the wrong one for a structured span. Half this
# project's primary sources are JSON APIs, where the verbatim string that proves a fact is a
# field pair like `"EventDate":"2026-06-16T00:00:00"` -- one whitespace token, 33 characters,
# and about as findable as a string gets. On 2026-08-25 this rule refused two such quotes on a
# claims file whose every claim had been re-fetched at 200 that morning, and would have refused
# them every run after. The test is DISCRIMINATING POWER, and a span has it by words or by
# length. "no action taken" is 3 words and 15 characters and still fails, which is correct:
# that phrase appears twice in its own response and everywhere else in Legistar.


AGENT_SPEC = REPO_ROOT / ".claude" / "agents" / "carousel-fact-checker.md"

# The value --template fills source_type with. Named rather than taken as sorted(SOURCE_TYPES)[0],
# which quietly became "data" and would have taught every run that a filing is a dataset. The
# self-test asserts it is still a member of the taxonomy.
TEMPLATE_SOURCE_TYPE = "primary_official"


def template() -> dict:
    """A valid claims file, BUILT FROM THE CONSTANTS ABOVE rather than typed beside them.

    Printed by --template and asserted clean by --self-test, so the skeleton the run copies
    can never fall behind the schema the run is checked against. Every value here is a real
    one: an agent that fills in a placeholder still produces a file this gate accepts.
    """
    return {
        CONTAINER: [{
            "id": "c1",
            "text": "what the record will state, in the record's own words",
            "quote": "the verbatim string you found in the fetched page",
            "url": "https://interchange.puc.texas.gov/Documents/58482",
            "source_type": TEMPLATE_SOURCE_TYPE,
            "retrieved": _dt.date.today().isoformat(),
            "confidence": "high",
        }],
        "rejected": [{"finding": "what the scout said", "reason": "why it failed, specifically"}],
    }


def spec_problems(md: str) -> list[str]:
    """Does the agent's own spec state the schema this file enforces?

    GATE_LESSONS 19 and 12: a rule written in one place and enforced in another is a rule that
    reads perfectly while meaning nothing. The 2026-08-18 drift cost four rejections because
    the spec's example was placeholder prose and the source taxonomy appeared nowhere in it.
    """
    problems: list[str] = []
    m = re.search(r"```json\s*\n(.*?)```", md, re.S)
    if not m:
        problems.append("the spec has no ```json example for the agent to copy")
    else:
        try:
            problems += [f"the spec's own example fails this gate: {p}"
                         for p in check(json.loads(m.group(1)))]
        except json.JSONDecodeError as exc:
            problems.append(f"the spec's example is not valid JSON: {exc}")
    for f in sorted(REQUIRED):
        if not re.search(r"`%s`" % re.escape(f), md):
            problems.append(f"the spec never names the required field {f!r} in backticks")
    for st in sorted(SOURCE_TYPES):
        if st not in md:
            problems.append(f"the spec never names the source type {st!r}, so the agent guesses")
    if CONTAINER not in md or "rejected" not in md:
        problems.append("the spec does not name both top level keys, "
                        f"{CONTAINER!r} and 'rejected'")
    return problems


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# =========================================================================================
# THE PROVISION SWEEP. Did this run read the whole of a document it fetched?
#
# THE DEFECT, 2026-09-08, carousel no. 18. The deck argued that City Code Chapter 2-19 WEIGHED
# artificial intelligence as one of ten privacy assessment factors in April, and that an August
# resolution turned that into a bar. Section 2-19-9 of the same ordinance, six pages past the
# section the argument stood on, reads "The following surveillance technologies or data uses are
# not permitted ... (B) artificial intelligence or machine learning tools, except as consistent
# with City policy". April had already said no. **The run had fetched the whole fourteen page
# ordinance, cited six other sections of it, and never opened that one.** The thesis was false
# and the spine had to be rebuilt in the middle of scoring.
#
# A second one the same run, on the same shape: the council's Actions Taken By Council page was
# linked from an agenda the run had fetched on its first pass, and the run's `rejected` list said
# "the agenda page publishes no vote for the item", which was true of the page's prose and skipped
# the link sitting on it.
#
# Both were found by a scoring judge. No gate here had anything to say, because every gate in this
# pipeline asks whether what the deck PRINTS traces back to a source. Not one asks the other
# direction: whether what a SOURCE says reached the deck. `claims_check` is where that belongs,
# because it runs at Phase 6, before a frame exists, which is the last moment the answer is cheap.
#
# THE RULE, IN THE JUDGE'S OWN WORDS. "Before a deck asserts a contrast between two instruments,
# sweep the full snapshot of both for the subject noun and either claim or explicitly reject every
# place it appears."
#
# WHAT IS DERIVED AND WHAT IS TYPED, because a gate with a typed list of nouns would be a gate
# that goes quiet on tomorrow's story. Nothing here is typed but the stopwords.
#
#   SUBJECT TERM   a maximal run of two or more content words in the run's own `story` sentence
#                  that also appears in at least one claim's `text`. Maximal runs need no window
#                  length and no frequency floor, so there is no number to tune and none to creep.
#                  On 2026-09-08 that yields exactly `artificial intelligence` and `city manager`,
#                  which are the deck's two subjects, and drops `austin ordered security
#                  equipment` and `same resolution forbade`, which no claim states in those words.
#   PROVISION      the span from one section heading to the next. A document with no section
#                  headings is one provision, which makes this gate SILENT on an unsectioned
#                  source, and that boundary is stated here rather than left to be inferred.
#   READ           a provision holding any claim's verbatim quote, or whose section id is written
#                  down anywhere in the claims file. The second half is the "explicitly reject"
#                  arm: a run that looked and chose not to carry it names the section in
#                  `rejected` or in `notes` and the sweep goes quiet on it.
#
# WARN, NEVER FAIL, for the reason `absence_check` and `noun_trace` give and it is the same
# reason. Deciding that a provision did not matter is an editorial judgement, and a gate that
# hard-fails a correct decision is a gate somebody switches off. What this does is put the list in
# front of the run while a rebuild still costs nothing.
# =========================================================================================

# The section heading forms this project's instruments actually use. `§ 2-19-9` is the city code
# extraction; `SECTION 4.` and `ARTICLE 1.` are the shapes a resolution and an order carry. Each
# has to start a line or follow sentence-ending space, so a cross reference inside a sentence does
# not open a provision.
SECTION_HEAD = re.compile(
    r"(?:^|(?<=[\n\r]))\s*(?:§\s*|(?:SECTION|ARTICLE|PART)\s+)([0-9]+[0-9A-Za-z.\-]*)",
    re.M)

# Words that carry no subject on their own. A subject term is a run BETWEEN these.
STOPWORDS = frozenset("""
a an and are as at be been by for from had has have in into is it its of on or that the their
there this to was were which with within without upon any all not no nor but so if then than
each other over under between about after before during per via such these those they them
""".split())


def _norm(s: str) -> str:
    """Case folded, punctuation to single spaces. The ordinance's text layer breaks words across
    a page footer, so whitespace is collapsed rather than preserved."""
    s = (s or "").replace("’", "'").replace("‘", "'")
    return re.sub(r"[^a-z0-9']+", " ", s.lower()).strip()


def subject_terms(doc: dict) -> list[str]:
    """The deck's own subject nouns, taken from its story and confirmed against its claims."""
    story, cur, runs = doc.get("story") or "", [], []
    for w in _norm(story).split():
        if w in STOPWORDS or len(w) < 2:
            if len(cur) > 1:
                runs.append(" ".join(cur))
            cur = []
        else:
            cur.append(w)
    if len(cur) > 1:
        runs.append(" ".join(cur))
    claims = doc.get(CONTAINER) if isinstance(doc.get(CONTAINER), list) else []
    texts = [_norm(c.get("text", "")) for c in claims if isinstance(c, dict)]
    out, seen = [], set()
    for r in runs:
        if r not in seen and any(r in t for t in texts):
            seen.add(r)
            out.append(r)
    return out


def provisions(raw: str) -> list[tuple[str, str]]:
    """(label, normalised text) per section heading. One entry for an unsectioned document."""
    marks = [(m.start(), m.group(1)) for m in SECTION_HEAD.finditer(raw)]
    if not marks:
        return [("(the whole document)", _norm(raw))]
    out = []
    if marks[0][0] > 0:
        out.append(("(before the first section)", _norm(raw[:marks[0][0]])))
    for i, (pos, label) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(raw)
        out.append((label, _norm(raw[pos:end])))
    return out


def unread_provisions(doc: dict, snapshots: dict[str, str]) -> list[str]:
    """One finding per subject term per document, naming the provisions nothing reached."""
    terms = subject_terms(doc)
    if not terms:
        return []
    claims = doc.get(CONTAINER) if isinstance(doc.get(CONTAINER), list) else []
    quotes = [q for q in (_norm(c.get("quote", "")) for c in claims if isinstance(c, dict)) if q]
    # Everything the run WROTE DOWN, so a section named in `rejected` or in `notes` counts as
    # disposed of. `json.dumps` rather than a field walk, because the disposition can be written
    # into a finding, a reason, a note or a claim's own text and all four are the run saying it
    # looked.
    written = _norm(json.dumps(doc.get("rejected") or []) + " " + json.dumps(doc.get("notes") or [])
                    + " " + " ".join(str(c.get("text", "")) for c in claims if isinstance(c, dict)))
    findings = []
    for name in sorted(snapshots):
        provs = provisions(snapshots[name])
        if len(provs) < 2:
            continue                       # unsectioned. The boundary is stated in the block above
        for term in terms:
            unread = []
            for label, text in provs:
                if term not in text:
                    continue
                if any(q and q in text for q in quotes):
                    continue
                if _norm(label) and _norm(label) in written:
                    continue
                unread.append(label)
            if unread:
                findings.append(
                    f"{name} names {term!r} in {len(unread)} provision(s) no claim quotes and "
                    f"nothing in this file disposes of: {', '.join(unread[:8])}"
                    f"{' ...' if len(unread) > 8 else ''}. Read each one and either claim it or "
                    f"write why it was not carried into `rejected`. On 2026-09-08 the one that "
                    f"was skipped this way, 2-19-9, refuted the deck's whole thesis")
    return findings


def check(doc: dict) -> list[str]:
    """Every problem, phrased so somebody can fix it without opening this file."""
    problems: list[str] = []

    if not isinstance(doc, dict):
        return ["the file is not a JSON object"]

    if CONTAINER not in doc:
        found = [k for k in CONTAINER_ALIASES if k in doc]
        if found:
            problems.append(
                f"the claim list is called {found[0]!r} and it must be called {CONTAINER!r}. "
                f"Everything downstream reads {CONTAINER!r}, so a rename here publishes an empty "
                f"verification record rather than failing")
        else:
            problems.append(f"no {CONTAINER!r} key. Keys present: {sorted(doc)[:8]}")
        return problems

    claims = doc[CONTAINER]
    if not isinstance(claims, list):
        return [f"{CONTAINER!r} is {type(claims).__name__}, and it must be a list"]

    # An empty claims file is legitimate but it is never silent: an empty run is one of the three
    # declared causes and has to be a decision rather than an accident.
    if not claims:
        problems.append("the claim list is empty. That is a legitimate outcome and it is never "
                        "an accident: say so explicitly in the run record")

    seen_ids: set[str] = set()
    for i, c in enumerate(claims):
        where = f"claim {i}"
        if not isinstance(c, dict):
            problems.append(f"{where} is {type(c).__name__}, not an object")
            continue
        cid = c.get("id")
        if isinstance(cid, str):
            where = f"claim {cid}"

        for field, aliases in REQUIRED.items():
            if field in c and str(c[field]).strip():
                continue
            wrong = [a for a in aliases if a in c]
            if wrong:
                problems.append(f"{where}: field is called {wrong[0]!r} and must be {field!r}")
            else:
                problems.append(f"{where}: no {field!r}")

        if isinstance(cid, str) and cid:
            if not ID_RE.match(cid):
                problems.append(f"{where}: id must look like c1, c2. Slides cite it")
            if cid in seen_ids:
                problems.append(f"{where}: duplicate id. A citation would be ambiguous")
            seen_ids.add(cid)

        st = c.get("source_type")
        if st and st not in SOURCE_TYPES:
            problems.append(f"{where}: source_type {st!r} is not one of {sorted(SOURCE_TYPES)}")

        q = c.get("quote")
        if (isinstance(q, str) and q.strip()
                and len(q.split()) < MIN_QUOTE_WORDS and len(q.strip()) < MIN_QUOTE_CHARS):
            problems.append(
                f"{where}: the quote is {len(q.split())} words and {len(q.strip())} characters. "
                f"Under {MIN_QUOTE_WORDS} words it needs {MIN_QUOTE_CHARS} characters to be "
                f"searched for in the source, which is the same as not having one")

        # THE ONE THAT MATTERS MOST. `text` is what the record will state and `quote` is the
        # string that proves it. If they are identical the fact-checker has copied the source
        # into the claim rather than verifying a statement against it, and the distinction the
        # whole gate rests on has quietly collapsed.
        t = c.get("text")
        if isinstance(t, str) and isinstance(q, str) and t.strip() and t.strip() == q.strip():
            problems.append(f"{where}: text and quote are identical. One states what the record "
                            f"claims, the other proves it. Identical means nothing was verified")

        u = c.get("url")
        if isinstance(u, str) and u.strip() and not u.startswith(("http://", "https://")):
            problems.append(f"{where}: url {u[:40]!r} is not a fetchable address")

        r = c.get("retrieved")
        if isinstance(r, str) and r.strip():
            try:
                _dt.date.fromisoformat(r.strip())
            except ValueError:
                problems.append(f"{where}: retrieved {r!r} is not an ISO date")

    # REJECTIONS ARE PART OF THE RECORD. The agent is told that rejecting is the job, so a run
    # that rejected nothing is either a suspiciously clean day or an agent that stopped checking.
    # Reported, never failed: a genuinely clean day exists.
    rej = doc.get("rejected")
    if rej is None:
        problems.append("no 'rejected' key. Rejecting is the job, and the reasons are how a "
                        "reader tells an unreachable page from a wrong claim")
    elif isinstance(rej, list):
        for i, r in enumerate(rej):
            if isinstance(r, dict) and not str(r.get("reason", "")).strip():
                problems.append(f"rejection {i}: no reason. 'Could not verify' is not a reason")

    return problems


def run(path: Path) -> int:
    try:
        doc = load(path)
    except FileNotFoundError:
        print(f"claims_check: no file at {path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"claims_check: {path} is not valid JSON: {exc}", file=sys.stderr)
        return 2

    problems = check(doc)
    n = len(doc.get(CONTAINER) or []) if isinstance(doc.get(CONTAINER), list) else 0
    if problems:
        print(f"claims_check: {len(problems)} problem(s) in {path}\n")
        for p in problems:
            print(f"  - {p}")
        print("\n  The deck is built from this file only. Fix it before Phase 6.")
        print("  `claims_check.py --template` prints a valid skeleton to work from.")
        return 1
    print(f"claims: clean ({n} verified claim(s), {len(doc.get('rejected') or [])} rejected)")
    # ONE VOCABULARY, STATED TWICE. Named at claims time rather than discovered at admission,
    # where it has already cost two runs a repair pass. See RECORD_ONLY above.
    counts: dict[str, int] = {}
    for c in (doc.get(CONTAINER) or []) if isinstance(doc.get(CONTAINER), list) else []:
        t = c.get("source_type")
        if t in RECORD_ONLY:
            counts[t] = counts.get(t, 0) + 1
    if counts:
        print("claims_check: this file uses source_type words ledger/docket.json does not hold, "
              "so anything admitted to the record is renamed by hand")
        for t in sorted(counts):
            print(f"  note  {counts[t]} claim(s) carry {t!r}, {RECORD_ONLY[t]}")

    # THE PROVISION SWEEP. Advisory, and it prints what it swept on the clean path as well as on
    # the dirty one, because a sweep that found no snapshots and a sweep that found nothing wrong
    # must not print the same line. GATE_LESSONS 26.
    snaps = read_snapshots(path.parent / "sources")
    terms = subject_terms(doc)
    if not snaps:
        print("claims_check: no sources/ beside this file, so no provision sweep was run")
    else:
        findings = unread_provisions(doc, snaps)
        for f in findings:
            print(f"  warn  {f}", file=sys.stderr)
        print(f"claims_check: swept {len(snaps)} snapshot(s) for "
              f"{len(terms)} subject term(s) {terms}, {len(findings)} provision finding(s)")
    return 0


# Text a sweep can read. A snapshot this project stores as JSON is a dataset rather than an
# instrument with provisions in it, and reading it as prose would report its keys as sections.
SNAPSHOT_SUFFIXES = (".txt", ".md", ".html", ".htm")


def read_snapshots(sources: Path) -> dict[str, str]:
    if not sources.is_dir():
        return {}
    out = {}
    for p in sorted(sources.iterdir()):
        if p.is_file() and p.suffix.lower() in SNAPSHOT_SUFFIXES:
            try:
                out[p.name] = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
    return out


def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    good = {
        "claims": [{
            "id": "c1",
            "text": "The commission set a comment deadline of September 4th, 2026.",
            "quote": "Comments are due no later than September 4, 2026",
            "url": "https://interchange.puc.texas.gov/Documents/58482",
            "source_type": "primary_official",
            "retrieved": "2026-08-12",
            "confidence": "high",
        }],
        "rejected": [{"finding": "a 500 MW figure", "reason": "the filing says 380 MW"}],
    }
    ok("a well formed claims file passes", not check(good), str(check(good))[:110])

    # EVERY DRIFT THE SIBLING ACTUALLY SUFFERED, replayed. This is the list from eighteen runs,
    # and each one shipped silently at the time.
    import copy as _copy                                             # noqa: PLC0415
    for name, mutate in [
        ("the container renamed to verified_claims",
         lambda d: {"verified_claims": d["claims"], "rejected": d["rejected"]}),
        ("the container renamed to a codename",
         lambda d: {"stargate_claims": d["claims"], "rejected": d["rejected"]}),
        ("text renamed to claim",
         lambda d: _swap(d, "text", "claim")),
        ("text renamed to statement",
         lambda d: _swap(d, "text", "statement")),
        ("url renamed to source_url",
         lambda d: _swap(d, "url", "source_url")),
        ("url renamed to evidence_url",
         lambda d: _swap(d, "url", "evidence_url")),
        ("the source nested inside an evidence object",
         lambda d: _nest(d)),
        ("the quote missing entirely",
         lambda d: _drop(d, "quote")),
        ("the retrieved date missing",
         lambda d: _drop(d, "retrieved")),
    ]:
        broken = mutate(_copy.deepcopy(good))
        ok(f"caught: {name}", bool(check(broken)))

    # The narrower faults, which are about quality rather than shape.
    bad_id = _copy.deepcopy(good); bad_id["claims"][0]["id"] = "claim-one"
    ok("caught: an id a slide cannot cite", bool(check(bad_id)))
    dup = _copy.deepcopy(good); dup["claims"].append(dict(dup["claims"][0]))
    ok("caught: two claims sharing an id", any("duplicate" in p for p in check(dup)))
    short = _copy.deepcopy(good); short["claims"][0]["quote"] = "due soon"
    ok("caught: a quote too short to find in the source", bool(check(short)))
    same = _copy.deepcopy(good); same["claims"][0]["quote"] = same["claims"][0]["text"]
    ok("caught: text and quote identical, so nothing was verified",
       any("identical" in p for p in check(same)))
    badtype = _copy.deepcopy(good); badtype["claims"][0]["source_type"] = "press_release"
    ok("caught: a source type outside the taxonomy", bool(check(badtype)))
    badurl = _copy.deepcopy(good); badurl["claims"][0]["url"] = "interchange.puc.texas.gov"
    ok("caught: a url nobody can fetch", bool(check(badurl)))
    baddate = _copy.deepcopy(good); baddate["claims"][0]["retrieved"] = "August 12th"
    ok("caught: a retrieved date that is not ISO", bool(check(baddate)))
    norej = _copy.deepcopy(good); del norej["rejected"]
    ok("caught: no rejection record at all", bool(check(norej)))
    blankrej = _copy.deepcopy(good); blankrej["rejected"] = [{"finding": "x", "reason": " "}]
    ok("caught: a rejection with no reason", bool(check(blankrej)))
    # THE QUOTE LENGTH RULE, BOTH DIRECTIONS (2026-08-25). A JSON field pair is one whitespace
    # token and is the most findable string a primary API source has. A three word phrase is not.
    shortq = _copy.deepcopy(good)
    shortq["claims"][0]["quote"] = "no action taken"
    ok("caught: a three word prose fragment is still not a quote",
       any("characters" in x for x in check(shortq)), str(check(shortq))[:140])
    jsonq = _copy.deepcopy(good)
    jsonq["claims"][0]["quote"] = '"MatterHistoryActionName":"no action taken"'
    ok("...but a 42 character field pair is one, whitespace notwithstanding",
       not any("characters" in x for x in check(jsonq)), str(check(jsonq))[:140])
    edgeq = _copy.deepcopy(good)
    edgeq["claims"][0]["quote"] = "x" * (MIN_QUOTE_CHARS - 1)
    ok("...and the character floor is a floor, not a suggestion",
       any("characters" in x for x in check(edgeq)))

    ok("an empty claim list is reported, not passed silently",
       bool(check({"claims": [], "rejected": []})))
    ok("a file that is not an object fails rather than throwing", bool(check(["c1"])))

    # THE SPEC IS PART OF THE GATE (2026-08-18). Four rejections in one run, all of them the
    # agent guessing at a field name the spec did not state. A spec that has drifted from the
    # checker is not a documentation problem, it is the checker's input being wrong.
    ok("the template this file prints passes this file's own check",
       not check(template()), str(check(template()))[:120])
    ok("...and its source_type is really in the taxonomy",
       TEMPLATE_SOURCE_TYPE in SOURCE_TYPES, TEMPLATE_SOURCE_TYPE)

    # THE 2026-08-18 SHAPE, replayed exactly as the fact-checker returned it that day: four
    # renames in one file, each of which the gate caught and the showrunner repaired by hand.
    tx = {"claims": [{"id": "c1", "text": good["claims"][0]["text"],
                      "quote": good["claims"][0]["quote"],
                      "source_url": good["claims"][0]["url"],
                      "source_type": "journalism", "confidence": "high"}],
          "dropped": [{"finding": "a 500 MW figure", "reason": "the filing says 380 MW"}]}
    p = check(tx)
    ok("caught: 2026-08-18's source_url", any("source_url" in x for x in p), str(p))
    ok("caught: 2026-08-18's missing retrieved", any("'retrieved'" in x for x in p), str(p))
    ok("caught: 2026-08-18's journalism source type", any("journalism" in x for x in p), str(p))
    ok("caught: 2026-08-18's dropped instead of rejected",
       any("rejected" in x for x in p), str(p))
    if not AGENT_SPEC.exists():
        ok(f"the fact-checker spec exists at {AGENT_SPEC.relative_to(REPO_ROOT)}", False,
           "the agent has no schema at all")
    else:
        md = AGENT_SPEC.read_text(encoding="utf-8")
        sp = spec_problems(md)
        ok("the fact-checker's own spec states the schema this gate enforces",
           not sp, "; ".join(sp)[:300])
        # and the spec check itself has to be able to go red
        ok("...and that check can fail: a spec missing the taxonomy is CAUGHT",
           bool(spec_problems(md.replace("secondary_reported", "journalism"))))
        ok("...and a spec whose example fails the gate is CAUGHT",
           bool(spec_problems(md.replace('"url":', '"source_url":'))))

    # ---- ONE VOCABULARY, STATED TWICE (2026-09-03) ----------------------------------------
    # The record's set is read from `docket_build`, which is another lane's file, so this is a
    # real second artifact rather than a fixture written beside the detector.
    rec = record_source_types()
    ok("the record's source taxonomy is imported from docket_build, never copied here",
       "journalism" in rec and rec != SOURCE_TYPES, str(sorted(rec)))
    ok("...and every divergence between the two is declared today",
       not vocabulary_problems(rec), "; ".join(vocabulary_problems(rec))[:300])
    ok("...with the two words this run measured named in the declaration",
       set(RECORD_ONLY) == SOURCE_TYPES - rec, str(sorted(set(RECORD_ONLY))))

    # BOTH DIRECTIONS, FORCED RED. A declaration table nobody can make fail is a table that
    # becomes a rubber stamp, which is the one way this fix could be worse than the defect.
    _saved_types, _saved_only = set(SOURCE_TYPES), dict(RECORD_ONLY)
    try:
        SOURCE_TYPES.add("dataset_api")
        p = vocabulary_problems(rec)
        ok("a NEW deck word the record does not hold and nobody declared FAILS",
           any("dataset_api" in x and "RECORD_ONLY does not declare" in x for x in p), str(p))
        SOURCE_TYPES.discard("dataset_api")
        # The day somebody makes the two sided fix in the daily lane, this half must not be
        # left behind saying the vocabularies still disagree.
        p = vocabulary_problems(rec | {"data"})
        ok("...and a declaration the record has since ADOPTED is reported as stale",
           any("'data'" in x and "no divergence left" in x for x in p), str(p))
        RECORD_ONLY["retired_word"] = "no longer in the taxonomy"
        p = vocabulary_problems(rec)
        ok("...and a declaration for a word this taxonomy dropped is reported as stale",
           any("retired_word" in x and "Delete the declaration" in x for x in p), str(p))
    finally:
        SOURCE_TYPES.clear()
        SOURCE_TYPES.update(_saved_types)
        RECORD_ONLY.clear()
        RECORD_ONLY.update(_saved_only)
    ok("...and the fixtures put the module constants back exactly as they were",
       SOURCE_TYPES == _saved_types and RECORD_ONLY == _saved_only)

    # ---- THE PROVISION SWEEP, replayed against the run it exists for --------------------
    # SYNTHETIC HALF. What a subject term is and what it is not.
    _doc = {"story": "Austin ordered security equipment for its parks and forbade its city "
                     "manager from considering any camera that depends upon artificial "
                     "intelligence.",
            CONTAINER: [{"text": "The clause binds the city manager.", "quote": "x"},
                        {"text": "It names artificial intelligence.", "quote": "y"}]}
    ok("the subject terms are the story's content runs the claims confirm",
       subject_terms(_doc) == ["city manager", "artificial intelligence"], str(subject_terms(_doc)))
    ok("...and a story phrase no claim states is not a subject term",
       "security equipment" not in " | ".join(subject_terms(_doc)), str(subject_terms(_doc)))
    ok("...and a story with no claims behind it yields no terms",
       subject_terms({"story": _doc["story"], CONTAINER: []}) == [])

    _sec = provisions("preamble text\n§ 2-19-3 COUNCIL APPROVAL.\nbody one\n"
                      "§ 2-19-9 PROHIBITED.\nartificial intelligence tools\n")
    ok("a document splits at its section headings",
       [lab for lab, _ in _sec] == ["(before the first section)", "2-19-3", "2-19-9"], str(_sec))
    ok("...and an unsectioned document is ONE provision, which is where this gate is silent",
       len(provisions("a page of prose with no headings at all")) == 1)
    ok("...and a section id cited inside a sentence opens no provision",
       len(provisions("as required by § 2-19-3 the manager shall act")) == 1,
       str(provisions("as required by § 2-19-3 the manager shall act")))

    # REAL ARTIFACT HALF. The ordinance this run fetched, the claims file as it ships, and the
    # same file with 2-19-9 taken back out of it. GATE_LESSONS 16: a fixture written by the
    # author of the detector agrees with the detector, and only a real snapshot carries the
    # shapes nobody thought to write down.
    _run = REPO_ROOT / "runs" / "carousel" / "2026-09-08"
    ok("the 2026-09-08 snapshots this replay needs are committed",
       (_run / "sources" / "ordinance.txt").exists() and (_run / "claims.json").exists())
    if (_run / "sources" / "ordinance.txt").exists():
        _snaps = read_snapshots(_run / "sources")
        _ship = json.loads((_run / "claims.json").read_text(encoding="utf-8"))
        _found = unread_provisions(_ship, _snaps)
        ok("the SHIPPED claims file leaves no provision naming its subject noun unread",
           not any("artificial intelligence" in f for f in _found), str(_found))

        # Take 2-19-9 back out, exactly as the run had it before a judge found the section.
        _target = dict(provisions(_snaps["ordinance.txt"]))["2-19-9"]
        _before = json.loads(json.dumps(_ship))
        _before[CONTAINER] = [c for c in _before[CONTAINER]
                              if not (_norm(c.get("quote", "")) and
                                      _norm(c.get("quote", "")) in _target)
                              and "2-19-9" not in str(c.get("text", ""))]
        _before["rejected"] = [r for r in (_before.get("rejected") or [])
                               if "2-19-9" not in json.dumps(r)]
        _before["notes"] = [n for n in (_before.get("notes") or []) if "2-19-9" not in str(n)]
        _back = unread_provisions(_before, _snaps)
        ok("...and with 2-19-9 removed the sweep NAMES it against the deck's subject noun",
           any("artificial intelligence" in f and "2-19-9" in f for f in _back), str(_back))
        ok("...and the removal actually changed the file, so the red is not an empty result",
           len(_before[CONTAINER]) < len(_ship[CONTAINER]),
           f"{len(_before[CONTAINER])} vs {len(_ship[CONTAINER])}")

        # THE DISPOSAL ARM. Writing the section into `rejected` is what quiets it, and that is
        # the "explicitly reject" half of the judge's rule rather than a way to switch it off.
        _dispose = json.loads(json.dumps(_before))
        _dispose["rejected"] = list(_dispose["rejected"]) + [
            {"finding": "Section 2-19-9 of the ordinance",
             "reason": "read in full and not carried, because the deck argues from 2-19-3"}]
        ok("...and naming that section in `rejected` quiets it",
           not any("artificial intelligence" in f and "2-19-9" in f
                   for f in unread_provisions(_dispose, _snaps)),
           str(unread_provisions(_dispose, _snaps)))

        # CALIBRATION, recorded as a number so a later change that makes this noisy shows up as
        # a number rather than as a feeling. absence_check does the same thing for the same
        # reason.
        ok("the shipped deck raises at most two provision findings",
           len(_found) <= 2, f"{len(_found)}: {_found}")

    ok("a JSON dataset beside the prose snapshots is not swept as an instrument",
       ".json" not in SNAPSHOT_SUFFIXES)

    if failures:
        print(f"\nclaims_check self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nclaims_check self-test: all passed ({len(REQUIRED)} required fields, "
          f"every sibling drift replayed, and the agent spec checked against them)")
    return 0


def _swap(d: dict, old: str, new: str) -> dict:
    for c in d["claims"]:
        c[new] = c.pop(old)
    return d


def _drop(d: dict, field: str) -> dict:
    for c in d["claims"]:
        c.pop(field, None)
    return d


def _nest(d: dict) -> dict:
    for c in d["claims"]:
        c["evidence"] = {"url": c.pop("url"), "outlet": "PUCT", "date": c.get("retrieved")}
    return d


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="check out/<date>/claims.json")
    ap.add_argument("--file", help="check this file")
    ap.add_argument("--out", default=str(REPO_ROOT / "out"),
                    help="run scratch root, so every gate takes the same flags")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--template", action="store_true",
                    help="print a valid claims.json skeleton built from this file's schema")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    if a.template:
        print(json.dumps(template(), indent=2))
        return 0
    if a.file:
        return run(Path(a.file))
    if a.date:
        return run(Path(a.out) / a.date / "claims.json")
    ap.error("give --date, --file or --self-test")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                        # noqa: BLE001
        print(f"claims_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
