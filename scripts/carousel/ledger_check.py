#!/usr/bin/env python3
"""ledger_check.py — the variety ledgers are DERIVED, so they are re-derived and compared.

WHY THIS EXISTS. 2026-08-26, and it is the third time.

The 2026-08-25 run recut its headline count from eight to seven when a director proved the
Texas Water Development Board's action was a petition denial rather than a restriction. Every
reader-facing surface was regenerated. The DURABLE MEMORY was not, and two scorers found it:

    ledger/carousel/topics.json   "the eight Texas governmental bodies that restricted a data
                                  center", "Two of the eight say ... on the other four the
                                  record says nothing" — against a run that computed 7, 5, 2, 0
    ledger/carousel/captions.json critic_note "widens to the eight"

The same round found all three caption exclusion lists disagreeing with the entries in the file
that holds them, wrong in BOTH directions:

    opening_moves_recent  held 'the quiet decision', in no entry; dropped 'the object', 2026-08-16
    structures_recent     held 'zoom out', in no entry;            dropped 'question and answer'
    closing_moves_recent  held a move last used 2026-08-19, outside a window of three

That is not cosmetic. Those three lists are what the caption room is handed BEFORE it writes, and
the room was told that 'the quiet decision', 'zoom out' and 'ask the one question the decision
leaves open' were off the table. It wrote all three anyway and coined freehand names for them,
which cleared the lists because a list can only exclude a name it shares. So the corruption did
not merely fail to prevent a repeat. It manufactured three new move names that are on none of
CAPTION_CRAFT.md's menus, which is how the next run's list gets corrupt too.

WHAT IT CHECKS

1. Every entry's `opening_move`, `structure` and `closing_move` is a name CAPTION_CRAFT.md
   actually carries. Freehand names are the mechanism, so they are the thing to refuse.
2. The three `*_recent` lists equal what the entries derive, at the window lengths the doctrine
   states. Derived data that is also stored is data that will disagree with itself.
3. Every spelled-out count in the newest topics entry's `topic` and `angle` prose is a value the
   run actually computed. Prose beside a number is where the recut goes stale.
4. No ledger carries two entries for one date. A writer that appends produces a duplicate the
   moment it re-runs, and `recent` windows then read the stale one last.
5. No entry USES a move its own exclusion window covered. Checks 1 and 2 proved the lists were
   well formed and derived correctly, and nothing asked the one question those lists exist for.
   See THE EXCLUSIONS WERE DERIVED AND NEVER ENFORCED, below.
6. No entry FILES ITS DECK MEDIAN UNDER A NAME NOTHING READS. See `misfiled_median`, and the
   2026-09-14 entry, which measured its deck at L* 6.0, wrote it as `deck_median`, and was
   reported by this file as an entry that "predates the measurement".

It reads the DOCTRINE for the menus AND for the windows rather than keeping its own copy, because
a gate with its own copy of a list is the defect it is here to catch.
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIGHT_L = 60.0      # deck median L* at or above which a deck reads light
LIGHT_CAP = 1       # brand.yaml: at most once per eight runs

# NAMED WAIVERS OF THE LIGHT DECK CAP, one date each, with who decided and why.
#
# This is not a raised cap and it is not an exemption window. The count above is still measured
# off the shipped render, still compared against brand.yaml's one per eight, and still PRINTED
# every run whether or not a waiver applies. A date here changes one thing, which is whether
# that measured fact stops the build.
#
# WHY THE MECHANISM EXISTS AT ALL. The cap guards visual variety across the feed, which is a
# brand judgment rather than an accuracy one, and the owner owns brand judgments. The
# alternative shapes were both worse. Raising `LIGHT_CAP` would silently permit every future
# second light deck. Editing `artwork.json` to hide the measurement would corrupt the durable
# memory the cap is counted from, which is the one thing an append only ledger refuses.
#
# A WAIVER IS SELF LIMITING and that is the point. It names a single date, so it expires on its
# own the moment that deck rolls out of the eight run window, and it can never make the next
# light deck legal. Nothing is added here without the owner saying so on the record, and the
# reason string is what a later session reads instead of guessing.
LIGHT_CAP_WAIVED = {
    "2026-09-03": (
        "Owner's instruction on 2026-09-03, given after being shown that carousel no. 14 was "
        "that day's deck, carried zero hard fails from all three judges at the five round cap, "
        "and scored 6.762 against the 6.562 that carousel no. 13 shipped at the day before. The "
        "other light deck in the window, 2026-08-26, was second oldest in it and rolls out after "
        "one more run, so the deck tripped the cap by one position. The variety debt is recorded "
        "in the run record and the next deck is required dark"
    ),
}

# THE MEASUREMENT FILED UNDER A NAME NOTHING READS (2026-09-15).
#
# `check_register` counts the light deck cap off `value.deck_median_L`, deliberately, because that
# figure is measured off the shipped render rather than asserted by the run about itself. An entry
# without it is treated as one that PREDATES the measurement and is noted rather than counted, and
# that carve-out is correct for the six August entries it was written for.
#
# On 2026-09-14 the run measured its deck at L* 6.0 and wrote it as `deck_median`. The entry
# therefore has a measurement and this file reported it as "1 older entr(y/ies) predate the
# measurement", about the second most recent run in the ledger. The count silently dropped a
# measured deck, and the report told itself a false story about why.
#
# THE FIX IS NOT A LIST OF ACCEPTED SPELLINGS. That is a hole with a list attached to it: the
# moment `deck_median` is honoured, the next run invents `deckMedianLstar` and the count sleeps
# again, and nothing reports the omission. GATE_LESSONS 39 and 47 are both about exactly this.
# What is checked instead is STRUCTURAL. A key whose name reduces to the same shape as the one
# the code reads, carrying a number, is a MISFILING, and a misfiling is a different event from an
# entry that predates the measurement. The two stop sharing a report line.
#
# THE VALUE IS NEVER ADOPTED. This gate does not guess that `deck_median` means `deck_median_L`
# and fold it into the cap. Guessing is the widening it is refusing. It says the name is wrong and
# leaves the count honest about what it could read.
CANON_MEDIAN = "deck_median_L"
#
# BINDS FORWARD, like EXCLUSIONS_BIND_AFTER below and for the same reason. `artwork.json` is the
# daily lane's durable memory and the 2026-09-14 entry is published, so the finding on it is a
# NOTE that names it correctly rather than a failure nobody in this lane can clear. Every entry
# dated after this is judged, and the note disappears on its own once that date rolls out of the
# eight run window.
MEDIAN_KEY_BINDS_AFTER = "2026-09-15"

DOCTRINE = "knowledge/carousel/CAPTION_CRAFT.md"

# The counts the topic prose is ABOUT. A number word in that prose has to be one of these, not
# merely some figure the run computed: `brazoria_applications` is 4, and without this scoping
# "on the other four the record says nothing either way" would pass while being false.
COUNTING_FIGURES = ("restricted_count", "declined_count", "total_count", "stated_nonbinding",
                    "stated_binding", "force_unstated", "distinct_shapes", "late_cluster",
                    "acting_bodies", "repeat_bodies", "busiest_body_count",
                    "busiest_body_binding", "busiest_month_count")
WORDS = "zero one two three four five six seven eight nine ten eleven twelve".split()


def section(text: str, name: str) -> str:
    m = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1) if m else ""


def menus(text: str) -> dict[str, set[str]]:
    """Opening moves, structures and closing moves, read off the doctrine's own markdown."""
    opens = {m.group(1).strip().lower()
             for m in re.finditer(r"^\|\s*\*\*(.+?)\*\*\s*\|", section(text, "Opening moves"),
                                  re.M)}
    structs = {m.group(1).strip().lower()
               for m in re.finditer(r"^-\s*\*\*(.+?)\.\*\*", section(text, "Structures"), re.M)}
    closes = {m.group(1).strip().rstrip(".").lower()
              for m in re.finditer(r"^-\s+(.+)$", section(text, "Closing moves"), re.M)}
    return {"opening_move": opens, "structure": structs, "closing_move": closes}


# --------------------------------------------- THE EXCLUSIONS WERE DERIVED AND NEVER ENFORCED
#
# 2026-09-03. Check 2 above proves the three `*_recent` lists agree with the entries they derive
# from. Nothing ever asked the question those lists exist to answer: did a shipped entry USE a
# move its own list said was off the table. Replayed against the ledger as it stands, EIGHT
# entries did, past a gate that was green on every one of them.
#
#   2026-08-30  opening_move 'the object'   one run after 2026-08-29 shipped 'the object'
#   2026-08-30  structure    'Zoom out'     one run after 2026-08-29 shipped 'Zoom out'
#   2026-08-26 through 2026-09-02, six entries, all closing on 'ask the one question the
#              decision leaves open', which CAPTION_CRAFT.md forbids two runs running
#
# THE CLOSING STREAK HAD A SECOND CAUSE AND IT WAS NOT DRIFT. `config/brand.yaml` fixes the
# closing FORM to a question, four of the doctrine's five closes are declarative, and the ending
# rule was wired on 2026-08-25, which is the first day of the streak. A gate forced it. That half
# is fixed in CAPTION_CRAFT.md, which now separates the substance from the form and states which
# substance the form costs. This half is the rotation, and it is enforced here.
#
# THE WINDOWS ARE READ OFF THE DOCTRINE and never typed in this file, for exactly the reason the
# menus are. A gate holding its own copy of a rule stated somewhere else is the defect this file
# was written to catch, and it would be a poor place to introduce a fresh one.
WINDOW_RX = re.compile(r"the last\s+(?:(\w+)\s+)?runs?['\N{RIGHT SINGLE QUOTATION MARK}]", re.I)
FIELD_SECTION = {"opening_move": "Opening moves",
                 "structure": "Structures",
                 "closing_move": "Closing moves"}

# IT BINDS FROM THE DAY IT SHIPPED AND NOT BEFORE, and the reason is not politeness to old work.
# `captions.json` is append only and belongs to the `daily` lane, so a violation already written
# into it can never be cleared by anybody. A gate that is permanently red with no action that
# clears it is a gate somebody eventually switches off, and it takes the real findings with it.
# The eight entries above are RE-DERIVED and PRINTED as a note instead, so the history is
# evidence rather than silence. Same call and the same reasoning as `shipped_check`'s
# CONSTRUCTION_SINCE and as the light deck cap two functions down.
#
# This run's own caption was written and gated before this check existed, so its entry is the
# last one outside the window. Every entry after it is judged.
EXCLUSIONS_BIND_AFTER = "2026-09-03"


DERIVED_KEYS = ("opening_moves_recent", "structures_recent", "closing_moves_recent")


def derived_lists(entries: list[dict], wins: dict[str, int]) -> dict[str, list[str]]:
    """The three exclusion lists, from the entries and the doctrine's own windows.

    ONE DEFINITION, USED BY BOTH DIRECTIONS. Check 2 compares the stored lists against this and
    `--derive` writes this, so the thing that judges the ledger and the thing that produces it
    cannot be two derivations that happen to agree.
    """
    newest = entries[-1]["date"]
    prior = [e for e in entries if e["date"] < newest]
    return {"opening_moves_recent": [e["opening_move"] for e in prior[-wins["opening_move"]:]],
            "structures_recent":    [e["structure"]    for e in prior[-wins["structure"]:]],
            "closing_moves_recent": [e["closing_move"] for e in prior[-wins["closing_move"]:]]}


def derive_text(cap_text: str, doctrine: str) -> str:
    """captions.json with the three derived lists rewritten, in the file's own formatting.

    THE DEFECT THIS EXISTS FOR (2026-09-17, and it is the fourth run in a row)

    The three lists drifted again. `ledger_check` caught it, as it has every time since
    2026-08-26, and the run then recomputed them BY HAND from the entries. That hand step is the
    drift: the ledger's own `_derived_note` points at `out/<date>/update_ledgers.py`, a scratch
    file each run writes fresh and which dies with the container, so every run re-derives a
    derivation and one of them is eventually wrong. A gate that reports the same drift four runs
    running is reporting a defect in the machine rather than in those runs.

    So the derivation the gate already performs to JUDGE the file is the one that WRITES it.

    THE FORMATTING IS ASSERTED, NOT ASSUMED. The file is `json.dumps(indent=1)` plus a trailing
    newline today, and the self-test proves that deriving a file that is already correct returns
    it byte for byte. A rewriter that reflows a 40 kB append-only-in-spirit ledger would bury one
    real change in a thousand cosmetic ones.

    IT WRITES THE THREE KEYS AND NOTHING ELSE. Every other finding this gate has is left standing
    and still fails, because a repair tool that can clear a check it was not written for is the
    move CLAUDE.md forbids in as many words.
    """
    cap = json.loads(cap_text)
    entries = cap.get("entries") or []
    if not entries:
        return cap_text
    want = derived_lists(entries, windows(doctrine))
    for key in DERIVED_KEYS:
        cap[key] = want[key]
    return json.dumps(cap, indent=1, ensure_ascii=False) + "\n"


def windows(text: str) -> dict[str, int]:
    """How many runs each move is off the menu for, READ OFF THE DOCTRINE.

    "The last six runs' opening moves are off the menu" is six. "The last run's closing substance
    is off the menu" is one, which is what CAPTION_CRAFT.md means by never the same phrasing two
    runs running.

    A section that no longer says raises rather than defaulting. A window this gate guessed would
    be a second source of truth for a rule that lives in the doctrine, and a check that quietly
    falls back to a number of its own is the shape that ships a green report over an unenforced
    rule.
    """
    out: dict[str, int] = {}
    for field, name in FIELD_SECTION.items():
        m = WINDOW_RX.search(section(text, name))
        if not m:
            raise ValueError(
                f"{DOCTRINE}'s '{name}' section no longer states how many runs a move is off the "
                f"menu for, so this gate cannot enforce it. Restore the sentence rather than "
                f"letting the window be guessed here")
        word = (m.group(1) or "one").lower()
        if word not in WORDS:
            raise ValueError(
                f"{DOCTRINE}'s '{name}' section says the last {word!r} runs and that is not a "
                f"number this gate can read. Write it as a word, the way the other sections do")
        out[field] = WORDS.index(word)
    return out


def canon(value: str, names: set[str]) -> str:
    """A stored move, resolved to the doctrine's own name for it.

    THE COMPARISON CANNOT BE STRING EQUALITY. `on_menu` deliberately accepts the head of a menu
    sentence, so one run may store 'stop on the strongest fact' and the next 'stop on the
    strongest fact, with no wrap-up at all' and mean the identical move. Comparing the raw strings
    would let an exclusion be cleared by lengthening a prefix, which is the 2026-08-25 freehand
    name defect wearing a different hat. Anything that resolves to no single menu entry is
    returned normalised and is caught by the menu check instead.
    """
    v = norm(value)
    if v in names:
        return v
    hits = [n for n in names if len(v) >= 12 and n.startswith(v)]
    return hits[0] if len(hits) == 1 else v


def exclusion_violations(entries: list[dict], menu: dict[str, set[str]],
                         win: dict[str, int]) -> list[tuple[str, str, str, str]]:
    """Every entry that used a move its own window covered, oldest first.

    Each is (date, field, the move as stored, the date it was last used).
    """
    out = []
    for i, e in enumerate(entries):
        for field, names in menu.items():
            here = canon(e.get(field, ""), names)
            if not here:
                continue
            for prev in reversed(entries[max(0, i - win[field]):i]):
                if canon(prev.get(field, ""), names) == here:
                    out.append((e["date"], field, str(e.get(field)), prev["date"]))
                    break
    return out


def norm(s: str) -> str:
    return (s or "").strip().rstrip(".").lower()


def on_menu(value: str, names: set[str]) -> bool:
    """Exact, or an unambiguous prefix of one menu entry.

    The closing moves are SENTENCES ("Stop on the strongest fact, with no wrap-up at all. This is
    often the best one."), and a ledger sensibly stores the head of one. A prefix of twelve or
    more characters that matches exactly one menu entry is that entry. Anything shorter, or
    matching two, is a freehand name and is refused: 'the procedural fact nobody expects' is a
    prefix of nothing.
    """
    if value in names:
        return True
    if len(value) < 12:
        return False
    return len([n for n in names if n.startswith(value)]) == 1


# `one` is a pronoun far more often than it is a count. "any one of them", "every one of the
# seven" and "the one that binds" are all English rather than arithmetic, and a gate that reads
# them as counts fires on correct prose, which is a gate somebody switches off.
PRONOUN_ONE = re.compile(r"\b(any|each|every|no|some|this|that|the|which|than|only)\s+one\b", re.I)


def check_captions(cap: dict, menu: dict[str, set[str]], doctrine: str) -> list[str]:
    problems: list[str] = []
    entries = sorted(cap.get("entries", []), key=lambda e: e["date"])
    seen: dict[str, int] = {}
    for e in entries:
        seen[e["date"]] = seen.get(e["date"], 0) + 1
    for d, n in seen.items():
        if n > 1:
            problems.append(f"captions.json carries {n} entries dated {d}. A ledger writer that "
                            f"appends duplicates the moment it re-runs, and the recent windows "
                            f"then read the stale one last")
    for e in entries:
        for field, names in menu.items():
            v = norm(e.get(field))
            if not v:
                problems.append(f"captions.json {e['date']} has no {field}")
            elif not on_menu(v, names):
                problems.append(
                    f"captions.json {e['date']} {field} {e[field]!r} is on no {DOCTRINE} menu. A "
                    f"freehand name cannot be excluded by a list of real ones, which is how three "
                    f"excluded moves shipped on 2026-08-25")
    if not entries:
        return problems
    newest = entries[-1]["date"]
    prior = [e for e in entries if e["date"] < newest]
    # EVERY WINDOW COMES FROM THE DOCTRINE, and until 2026-09-03 exactly one of the three did not.
    # This block read six, three and three off its own line while `windows()` read six, three and
    # ONE out of CAPTION_CRAFT.md, so the stored `closing_moves_recent` was checked three deep
    # against a rule that is one deep. The doctrine says the room is handed "the closing substance
    # from the last one", the gate demanded three, and the ledger duly carried three.
    #
    # A review bot on PR 252 found it by reading the two files side by side, which is the only way
    # it was ever findable: both halves passed, because the number the gate enforced and the number
    # the gate derived were never compared to each other. That is the defect shape CLAUDE.md names
    # three separate times, a rule stated in one place and a surface keeping its own copy, and the
    # cure is the same every time. There is now one source and this block asks it.
    try:
        wins = windows(doctrine)
    except ValueError as exc:
        problems.append(f"ledger_check cannot read an exclusion window. {exc}")
        return problems
    want = derived_lists(entries, wins)
    for key, expect in want.items():
        got = cap.get(key)
        if got != expect:
            extra = [x for x in (got or []) if x not in expect]
            missing = [x for x in expect if x not in (got or [])]
            problems.append(
                f"captions.json {key} disagrees with its own entries. It holds {got!r} and the "
                f"entries derive {expect!r}"
                + (f". {extra!r} appears in no entry" if extra else "")
                + (f". {missing!r} is in an entry and is not listed" if missing else ""))

    # ---- 5. THE EXCLUSIONS, ENFORCED RATHER THAN MERELY DERIVED. See the block above.
    # It reads the SAME `wins` the derived lists were built from, rather than asking again. Two
    # reads of one file cannot disagree today, and the point of the block above is that the
    # derivation and the enforcement are one number rather than two that happen to match.
    win = wins
    hits = exclusion_violations(entries, menu, win)
    old = [h for h in hits if h[0] <= EXCLUSIONS_BIND_AFTER]
    if old:
        print(f"  note  {len(old)} entr(y/ies) used a move their own exclusion window covered, "
              f"before this check existed on {EXCLUSIONS_BIND_AFTER}. captions.json is append "
              f"only and is the daily lane's, so these can't be cleared and are not failed. "
              f"They are the reason this check exists: "
              + "; ".join(f"{d} {f} {v!r}, last used {p}" for d, f, v, p in old))
    for date, field, value, prev in hits:
        if date > EXCLUSIONS_BIND_AFTER:
            problems.append(
                f"captions.json {date} {field} {value!r} was used {prev}, inside the window "
                f"{DOCTRINE} puts it off the menu for ({win[field]} run(s)). That list is handed "
                f"to the caption room BEFORE it writes. Spend a different one rather than "
                f"relabelling this one, which is how three freehand names reached this ledger on "
                f"2026-08-25")
    return problems


def _median_shape(key: str) -> str:
    """A key name reduced to what it MEASURES, with the unit suffix taken off.

    Lowercase alphanumerics, then one trailing luminance suffix. `deck_median_L`,
    `deck_median`, `deck_median_lstar` and `deckMedianL` all reduce to `deckmedian`, so they are
    four spellings of one field. `planned_deck_median` reduces to `planneddeckmedian` and
    `per_slide_median_L` to `perslidemedian`, which are different quantities and stay different.
    """
    k = re.sub(r"[^a-z0-9]+", "", key.lower())
    for suffix in ("lstar", "l"):
        if k.endswith(suffix) and len(k) > len(suffix):
            return k[: -len(suffix)]
    return k


def misfiled_median(entry: dict) -> list[tuple[str, float]]:
    """Numbers in this entry that measure the deck median under a name nothing reads.

    Empty when the entry carries `deck_median_L`, because then the count works whatever else is
    beside it, and empty when the entry carries no deck median at all, because that entry
    genuinely predates the measurement.
    """
    v = entry.get("value")
    if not isinstance(v, dict) or isinstance(v.get(CANON_MEDIAN), (int, float)):
        return []
    want = _median_shape(CANON_MEDIAN)
    return [(k, v[k]) for k in sorted(v)
            if k != CANON_MEDIAN
            and isinstance(v[k], (int, float)) and not isinstance(v[k], bool)
            and _median_shape(k) == want]


def check_register(art: dict) -> list[str]:
    """THE LIGHT DECK CAP, COUNTED RATHER THAN ASSERTED.

    `config/brand.yaml` reads: "Big Bend at dusk is the default. A light deck is allowed as a
    deliberate high-variance move, at most once per eight runs, and the ledger enforces the
    count." The ledger did not. Every `light_decks_used` value in `artwork.json` reads the
    literal 1 while meaning light FRAMES inside a deck, which is a different quantity from the
    one brand.yaml says is being counted, so the field looked like enforcement and enforced
    nothing.

    Measured off the shipped PNGs on 2026-08-26: 08-18 at deck median L* 82.7, 08-20 at 85.5 and
    08-26 at 86.7, three light decks inside an eight run window against a cap of one. Two of
    those three had already shipped before anyone counted.

    This is GATE_LESSONS' own recurring shape, a rule stated in config with a ledger field that
    appears to enforce it and nothing in between checking they measure the same thing, and it is
    why the count comes from `value.deck_median_L`, which is measured off the render, rather than
    from any field a run writes about itself.
    """
    problems: list[str] = []
    entries = sorted(art.get("entries", []), key=lambda e: e.get("date", ""))
    window = entries[-8:]
    light = [e for e in window
             if isinstance(e.get("value"), dict)
             and isinstance(e["value"].get("deck_median_L"), (int, float))
             and e["value"]["deck_median_L"] >= LIGHT_L]
    unmeasured = [e["date"] for e in window
                  if not (isinstance(e.get("value"), dict)
                          and isinstance(e["value"].get("deck_median_L"), (int, float)))]
    # A MISFILING IS NOT AN ENTRY THAT PREDATES THE MEASUREMENT, and until 2026-09-15 they shared
    # this report line. 2026-09-14 measured its deck and filed it as `deck_median`, so the count
    # dropped it and the note called the second newest run in the ledger older than the check.
    misfiled = [(e["date"], misfiled_median(e)) for e in window if misfiled_median(e)]
    predates = [d for d in unmeasured if d not in {m[0] for m in misfiled}]
    # THE MEASUREMENT IS NEW, SO THE CAP BINDS FROM WHERE IT EXISTS. Backfilling a measured
    # field into already published entries would be editing the durable memory to suit a check
    # written after them, which is the one thing an append only ledger is for refusing. The
    # entries without it are NOTED and not failed, and the note disappears on its own as eight
    # measured runs accumulate. What is never softened is the count itself, below.
    if predates:
        print(f"  note  the light deck cap is counted over the {len(window) - len(unmeasured)} "
              f"entr(y/ies) carrying a measured deck_median_L. {len(predates)} older "
              f"entr(y/ies) predate the measurement and are not counted: "
              f"{', '.join(predates)}")
    for date, keys in misfiled:
        named = ", ".join(f"{k}={v}" for k, v in keys)
        msg = (f"artwork.json {date} measured a deck median and filed it as {named}. The light "
               f"deck cap is counted off value.{CANON_MEDIAN} and reads nothing else, so this "
               f"entry is dropped from the count while looking measured. Write the key "
               f"{CANON_MEDIAN}. This gate will not accept a second spelling, because a list of "
               f"accepted names is how the count goes quiet on the third one")
        if date > MEDIAN_KEY_BINDS_AFTER:
            problems.append(msg)
        else:
            print(f"  note  {msg}. Not failed: this entry predates the check and artwork.json is "
                  f"the daily lane's durable memory, so nothing in this lane can clear it. It "
                  f"rolls out of the eight run window on its own")
    if len(light) > LIGHT_CAP:
        named = ', '.join(e['date'] + ' at L* ' + str(e['value']['deck_median_L'])
                          for e in light)
        waived = [e for e in light if e["date"] in LIGHT_CAP_WAIVED]
        over = len(light) - len(waived)
        if over <= LIGHT_CAP:
            # THE COUNT IS NOT SOFTENED. It is still measured off the render, still over the cap,
            # and still printed here every run. What a waiver changes is only whether that fact
            # BLOCKS, and only for a date somebody named on the record.
            for e in waived:
                print(f"  note  the light deck cap is OVER at {len(light)} in {len(window)} "
                      f"({named}) and does not fail, because {e['date']} carries a named "
                      f"waiver. {LIGHT_CAP_WAIVED[e['date']]}")
        else:
            problems.append(
                f"artwork.json: {len(light)} light deck(s) in the last {len(window)} runs "
                f"({named}) "
                f"against brand.yaml's cap of {LIGHT_CAP} per eight. Measured off the render, not "
                f"asserted by the run")
    return problems


def check_topics(top: dict, figures: dict | None) -> list[str]:
    problems: list[str] = []
    entries = sorted(top.get("entries", []), key=lambda e: e["date"])
    seen: dict[str, int] = {}
    for e in entries:
        seen[e["date"]] = seen.get(e["date"], 0) + 1
    for d, n in seen.items():
        if n > 1:
            problems.append(f"topics.json carries {n} entries dated {d}")
    if not entries or figures is None:
        return problems
    ok = {figures[k]["value"] for k in COUNTING_FIGURES if k in figures}
    allowed = {WORDS[v] for v in ok if 0 <= v < len(WORDS)}
    newest = entries[-1]
    for field in ("topic", "angle"):
        prose = newest.get(field) or ""
        masked = PRONOUN_ONE.sub(lambda m: m.group(0)[:-3] + "___", prose)
        for m in re.finditer(r"\b(" + "|".join(WORDS) + r")\b", masked, re.I):
            w = m.group(1).lower()
            if w not in allowed:
                problems.append(
                    f"topics.json {newest['date']} {field} says {w!r} and the run computed "
                    f"{sorted(ok)} for the counts that prose is about. A recut regenerates the "
                    f"deck and leaves the durable memory narrating the old number")
    return problems


def run(cap: dict, top: dict, figures: dict | None, doctrine: str,
        art: dict | None = None) -> list[str]:
    out = check_captions(cap, menus(doctrine), doctrine) + check_topics(top, figures)
    if art is None:
        f = REPO_ROOT / "ledger" / "carousel" / "artwork.json"
        art = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    return out + check_register(art)


def self_test() -> int:
    fails = 0

    def ok(label, cond, extra=""):
        nonlocal fails
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            fails += 1

    doc = (REPO_ROOT / DOCTRINE).read_text(encoding="utf-8")
    M = menus(doc)
    ok("the doctrine's ten opening moves are read off the doctrine", len(M["opening_move"]) == 10,
       str(sorted(M["opening_move"])))
    ok("...its eight structures too", len(M["structure"]) == 8, str(sorted(M["structure"])))
    ok("...and its five closing moves", len(M["closing_move"]) == 5, str(sorted(M["closing_move"])))

    base = {"entries": [
        {"date": "2026-08-20", "opening_move": "the plain question", "structure": "question and answer",
         "closing_move": "name what happens next and when"},
        {"date": "2026-08-21", "opening_move": "the before and after", "structure": "clock",
         "closing_move": "point at the record, plainly, without a call to action"},
        {"date": "2026-08-22", "opening_move": "the deadline", "structure": "zoom in",
         "closing_move": "name what is still not public, and how big that is"},
        {"date": "2026-08-25", "opening_move": "the quiet decision", "structure": "zoom out",
         "closing_move": "ask the one question the decision leaves open"}]}
    good = dict(base,
                opening_moves_recent=["the plain question", "the before and after", "the deadline"],
                structures_recent=["question and answer", "clock", "zoom in"],
                # ONE DEEP, because that is what the doctrine's Closing moves section says and
                # this fixture used to carry three. It passed against a gate that also typed
                # three, which is the whole of the 2026-09-03 finding: a fixture and the code it
                # exercises can agree with each other and both disagree with the rule.
                closing_moves_recent=["name what is still not public, and how big that is"])
    ok("a ledger whose lists match its entries passes", not check_captions(good, M, doc),
       str(check_captions(good, M, doc)))
    deep = dict(good, closing_moves_recent=[
        "point at the record, plainly, without a call to action",
        "name what is still not public, and how big that is"])
    ok("a closing list deeper than the doctrine's own window FAILS",
       any("closing_moves_recent" in x for x in check_captions(deep, M, doc)),
       str(check_captions(deep, M, doc)))

    # THE 2026-08-25 DEFECT, both directions.
    bad = json.loads(json.dumps(good))
    bad["structures_recent"] = ["zoom out", "zoom in", "clock"]
    p = check_captions(bad, M, doc)
    ok("a list holding a move that is in no entry FAILS", any("structures_recent" in x for x in p))
    ok("...and the report names the move that appears in no entry",
       any("zoom out" in x and "no entry" in x for x in p), str(p))
    ok("...and names the one that is in an entry and unlisted",
       any("question and answer" in x for x in p), str(p))

    # ---- --derive, ADDED 2026-09-17 BECAUSE THE SAME DRIFT HAD BEEN REPORTED FOUR RUNS RUNNING.
    # Every assertion here is on `bad`, which is the 2026-08-25 corruption, so the repair is
    # replayed against the defect it exists for rather than against a fixture written beside it.
    fmt = lambda o: json.dumps(o, indent=1, ensure_ascii=False) + "\n"      # noqa: E731
    _cap = REPO_ROOT / "ledger" / "carousel" / "captions.json"
    _raw = _cap.read_text(encoding="utf-8") if _cap.exists() else None
    ok("the ledger this file writes is still json.dumps(indent=1) plus a newline",
       _raw is not None and fmt(json.loads(_raw)) == _raw,
       "the real captions.json no longer round-trips, so --derive would reflow the whole file")
    derived = json.loads(derive_text(fmt(bad), doc))
    ok("--derive rewrites the corrupt structures list to what the entries derive",
       derived["structures_recent"] == good["structures_recent"], derived["structures_recent"])
    ok("...and the derived file then PASSES the check that was red on it",
       not check_captions(derived, M, doc), str(check_captions(derived, M, doc)))
    ok("...and it is a no-op, byte for byte, on a ledger that is already right",
       derive_text(fmt(good), doc) == fmt(good))
    ok("...and it touched nothing outside the three derived keys",
       {k: v for k, v in derived.items() if k not in DERIVED_KEYS}
       == {k: v for k, v in bad.items() if k not in DERIVED_KEYS})
    # A REPAIR TOOL THAT CAN CLEAR A CHECK IT WAS NOT WRITTEN FOR IS THE MOVE THAT IS FORBIDDEN.
    cannot = json.loads(json.dumps(good))
    cannot["entries"][-1]["structure"] = "a shape nobody put on a menu"
    still = json.loads(derive_text(fmt(cannot), doc))
    ok("--derive does NOT clear a freehand move name, which is a different finding",
       any("on no" in x for x in check_captions(still, M, doc)),
       str(check_captions(still, M, doc)))

    free = json.loads(json.dumps(good))
    free["entries"][-1]["opening_move"] = "the procedural fact nobody expects"
    p = check_captions(free, M, doc)
    ok("a freehand move name that is on no menu FAILS",
       any("on no" in x and "procedural fact" in x for x in p), str(p))

    dup = json.loads(json.dumps(good))
    dup["entries"].append(json.loads(json.dumps(dup["entries"][-1])))
    ok("two entries for one date FAIL",
       any("2 entries dated" in x for x in check_captions(dup, M, doc)))

    # ---- 5. THE EXCLUSIONS, ENFORCED (2026-09-03) --------------------------------------
    # Eight shipped entries used a move their own window covered and this gate was green on
    # every one. These cases are the proof it goes red now.
    W = windows(doc)
    ok("the windows are read off the doctrine rather than typed here",
       W == {"opening_move": 6, "structure": 3, "closing_move": 1}, str(W))
    stripped = doc.replace("**The last run's closing substance is off the menu.**", "Rotate.")
    try:
        windows(stripped)
        ok("a doctrine that stops stating a window RAISES rather than guessing one", False)
    except ValueError as exc:
        ok("a doctrine that stops stating a window RAISES rather than guessing one",
           "Closing moves" in str(exc), str(exc))

    def ledger(rows):
        """A well-formed captions.json from (date, opening, structure, closing) rows.

        Its windows come from `W`, which came from the doctrine. Typed here they would be a third
        copy of the number, and a fixture holding the wrong one makes a correct gate look broken,
        which is exactly how these two cases read the moment the gate was fixed.
        """
        es = [{"date": d, "opening_move": o, "structure": s, "closing_move": c}
              for d, o, s, c in rows]
        prior = es[:-1]
        return {"entries": es,
                "opening_moves_recent": [e["opening_move"] for e in prior[-W["opening_move"]:]],
                "structures_recent": [e["structure"] for e in prior[-W["structure"]:]],
                "closing_moves_recent": [e["closing_move"] for e in prior[-W["closing_move"]:]]}

    OPEN, STRUCT = "the deadline", "ladder"
    CLOSE_A = "ask the one question the decision leaves open"
    CLOSE_B = "name what happens next and when"
    rotates = ledger([("2026-09-10", "the object", "pivot", CLOSE_A),
                      ("2026-09-11", OPEN, STRUCT, CLOSE_B)])
    ok("a ledger that rotates every field passes",
       not check_captions(rotates, M, doc), str(check_captions(rotates, M, doc)))

    # THE 2026-08-30 DEFECT, replayed on dates this check governs.
    repeat_open = ledger([("2026-09-10", "the object", "pivot", CLOSE_A),
                          ("2026-09-11", "the object", STRUCT, CLOSE_B)])
    p = check_captions(repeat_open, M, doc)
    ok("an opening move repeated inside its six run window FAILS",
       any("opening_move" in x and "2026-09-11" in x for x in p), str(p))
    ok("...and the report names the run it was last used on",
       any("last used 2026-09-10" in x or "used 2026-09-10" in x for x in p), str(p))
    repeat_struct = ledger([("2026-09-10", "the object", "Zoom out", CLOSE_A),
                            ("2026-09-11", OPEN, "zoom out", CLOSE_B)])
    ok("a structure repeated inside its three run window FAILS, whatever its case",
       any("structure" in x and "2026-09-11" in x
           for x in check_captions(repeat_struct, M, doc)),
       str(check_captions(repeat_struct, M, doc)))

    # THE CLOSING STREAK, which ran seven captions long because a gate forced the FORM.
    repeat_close = ledger([("2026-09-10", "the object", "pivot", CLOSE_A),
                           ("2026-09-11", OPEN, STRUCT, CLOSE_A)])
    ok("a closing move repeated the very next run FAILS",
       any("closing_move" in x and "2026-09-11" in x
           for x in check_captions(repeat_close, M, doc)),
       str(check_captions(repeat_close, M, doc)))
    two_back = ledger([("2026-09-09", "the object", "pivot", CLOSE_A),
                       ("2026-09-10", "the who", "ledger", CLOSE_B),
                       ("2026-09-11", OPEN, STRUCT, CLOSE_A)])
    ok("...while the same close two runs back is inside the doctrine's window and passes",
       not check_captions(two_back, M, doc), str(check_captions(two_back, M, doc)))

    # AN EXCLUSION MUST NOT BE CLEARABLE BY LENGTHENING A PREFIX. `on_menu` accepts the head of
    # a menu sentence, so two spellings of one move must still collide.
    prefix = ledger([("2026-09-10", "the object", "pivot", "stop on the strongest fact"),
                     ("2026-09-11", OPEN, STRUCT,
                      "stop on the strongest fact, with no wrap-up at all")])
    ok("...and a longer prefix of the same close does NOT clear the exclusion",
       any("closing_move" in x and "2026-09-11" in x for x in check_captions(prefix, M, doc)),
       str(check_captions(prefix, M, doc)))

    # THE BINDING DATE, both directions. The identical repeat before it is noted, never failed,
    # because captions.json is append only and belongs to another lane.
    before = ledger([("2026-08-29", "the object", "pivot", CLOSE_A),
                     ("2026-08-30", "the object", "pivot", CLOSE_A)])
    ok("the same repeat BEFORE the binding date is not failed",
       not check_captions(before, M, doc), str(check_captions(before, M, doc)))

    # THE REAL ARTIFACT, which is the half a fixture cannot supply. A gate proved only against
    # cases its own author wrote agrees with its author. This asserts the rule finds the eight
    # violations actually sitting in the shipped ledger.
    real = REPO_ROOT / "ledger" / "carousel" / "captions.json"
    if real.exists():
        got = exclusion_violations(
            sorted(json.loads(real.read_text(encoding="utf-8"))["entries"],
                   key=lambda e: e["date"]), M, W)
        ok("the shipped ledger's own eight violations are all found",
           len(got) >= 8 and ("2026-08-30", "opening_move") in {(d, f) for d, f, _, _ in got}
           and ("2026-08-30", "structure") in {(d, f) for d, f, _, _ in got}
           and len([1 for _, f, _, _ in got if f == "closing_move"]) >= 6,
           str([(d, f) for d, f, _, _ in got]))

    # TOPICS. The eight that stayed after the run recut to seven.
    figs = {"restricted_count": {"value": 7}, "declined_count": {"value": 3},
            "total_count": {"value": 10}, "stated_nonbinding": {"value": 5},
            "stated_binding": {"value": 2}, "force_unstated": {"value": 0},
            "distinct_shapes": {"value": 7}, "late_cluster": {"value": 3},
            "brazoria_applications": {"value": 4}}
    t_ok = {"entries": [{"date": "2026-08-25",
                         "topic": "the seven Texas governmental bodies that acted on a data center",
                         "angle": "Five of the seven stop nothing and two changed a legal state"}]}
    ok("topic prose whose counts the run computed passes", not check_topics(t_ok, figs),
       str(check_topics(t_ok, figs)))
    t_bad = {"entries": [{"date": "2026-08-25",
                          "topic": "the eight Texas governmental bodies that restricted a data center",
                          "angle": "Two of the eight say they stop nothing and on the other four "
                                   "the record says nothing either way"}]}
    p = check_topics(t_bad, figs)
    ok("the stale 'eight' FAILS", any("'eight'" in x for x in p), str(p))
    ok("...and so does 'four', which IS a computed figure but not one of these counts",
       any("'four'" in x for x in p), str(p))
    ok("...reported on both the topic and the angle",
       any("topic says" in x for x in p) and any("angle says" in x for x in p), str(p))

    ok("a closing move stored as the head of the doctrine's sentence is accepted",
       on_menu("stop on the strongest fact", M["closing_move"]))
    ok("...while a freehand name that prefixes nothing is not",
       not on_menu("the procedural fact nobody expects", M["opening_move"]))
    ok("...and a prefix too short to be unambiguous is not",
       not on_menu("stop on", M["closing_move"]))
    t_pron = {"entries": [{"date": "2026-08-25",
                           "topic": "taken as a pattern rather than as any one of them",
                           "angle": "the record speaks to force on every one of the seven"}]}
    ok("'any one' and 'every one' are read as English, not as a count",
       not check_topics(t_pron, figs), str(check_topics(t_pron, figs)))
    t_count = {"entries": [{"date": "2026-08-25", "topic": "x",
                            "angle": "nine of the seven changed a legal state"}]}
    ok("...while a bare count that the run did not compute still FAILS",
       any("'nine'" in x for x in check_topics(t_count, figs)))

    # THE LIGHT DECK CAP, AND THE WAIVER THAT MUST NOT DISABLE IT. A named waiver stops one
    # measured date from blocking. It may never stop the count, and it may never make the NEXT
    # light deck legal, which is the failure mode a raised cap would have had.
    def _art(*pairs):
        return {"entries": [{"date": d, "value": {"deck_median_L": L}} for d, L in pairs]}

    dark = [(f"2026-07-{n:02d}", 20.0) for n in range(1, 7)]
    ok("one light deck in eight is inside the cap",
       not check_register(_art(*dark, ("2026-08-26", 86.7), ("2026-09-03", 20.0))))
    ok("two light decks in eight FAIL when neither is waived",
       any("light deck(s)" in x for x in
           check_register(_art(*dark, ("2026-08-26", 86.7), ("2026-08-27", 73.1)))))
    ok("...and do NOT fail when one of them carries a named waiver",
       not check_register(_art(*dark, ("2026-08-26", 86.7), ("2026-09-03", 73.1))))
    ok("...while a THIRD light deck fails even with the waiver in place",
       any("light deck(s)" in x for x in
           check_register(_art(*dark[:-1], ("2026-08-20", 85.5),
                               ("2026-08-26", 86.7), ("2026-09-03", 73.1)))))
    ok("the waiver is one date and never a window",
       all(isinstance(k, str) and len(k) == 10 for k in LIGHT_CAP_WAIVED)
       and all(v.strip() for v in LIGHT_CAP_WAIVED.values()))

    # ---------------------------------------------- THE MISFILED DECK MEDIAN, 2026-09-15
    #
    # REPLAYED AGAINST THE SHIPPED LEDGER, not only against a fixture. GATE_LESSONS 50: the
    # synthetic half proves the logic can tell the shapes apart, and only a check against the
    # real artifact would have gone red on the day this happened. The 2026-09-14 entry is that
    # artifact and it is committed, so the assertion is one line and it cannot rot.
    real = json.loads((REPO_ROOT / "ledger" / "carousel" / "artwork.json").read_text("utf-8"))
    hit = [(e["date"], misfiled_median(e)) for e in real.get("entries", []) if misfiled_median(e)]
    ok("the real 2026-09-14 entry is seen as a MISFILING, not as one that predates the check",
       [d for d, _ in hit] == ["2026-09-14"], str(hit))
    ok("...and the key it names is the one the run actually wrote",
       bool(hit) and hit[0][1] == [("deck_median", 6.0)], str(hit))
    ok("...and the shipped ledger still passes, because the date is inside the bind window",
       not [x for x in check_register(real) if "filed it as" in x], str(check_register(real)))

    # THE SHAPES THAT MUST NOT BE CONFUSED FOR EACH OTHER.
    ok("an entry carrying deck_median_L is not a misfiling",
       misfiled_median({"date": "d", "value": {"deck_median_L": 13.7, "deck_median": 13.7}}) == [])
    ok("an entry carrying no deck median at all genuinely predates the measurement",
       misfiled_median({"date": "d", "value": {"palette": "bond"}}) == [])
    ok("planned_deck_median is a different quantity and is never read as the measurement",
       misfiled_median({"date": "d", "value": {"planned_deck_median": 30}}) == [])
    ok("per_slide_median_L is a different quantity too",
       misfiled_median({"date": "d", "value": {"per_slide_median_L": [6.1, 86.1]}}) == [])
    ok("a prose note beside the figure is not a figure",
       misfiled_median({"date": "d", "value": {"deck_median_note": "20.4 sits between"}}) == [])
    # NOT A LIST OF SPELLINGS. Three names nobody has written yet all reduce to the same shape.
    for invented in ("deck_median", "deck_median_lstar", "deckMedianL", "deck-median-L"):
        ok(f"a run inventing {invented!r} is caught without that name being listed anywhere",
           misfiled_median({"date": "d", "value": {invented: 86.7}}) == [(invented, 86.7)])
    # Three of those four names have never been written by any run, and none of them is listed
    # anywhere in the rule: `_median_shape` derives the match from CANON_MEDIAN itself. That is
    # the difference between this and an allowlist, and it is why a fourth spelling invented
    # tomorrow is caught rather than skipped.
    ok("the rule is derived from the canonical key and holds no spellings of its own",
       _median_shape(CANON_MEDIAN) == "deckmedian"
       and _median_shape("planned_deck_median") != "deckmedian")

    # IT BINDS FORWARD AND IT DOES BIND. A misfiling dated after the bind date is a hard fail.
    after = {"entries": [{"date": d, "value": {"deck_median_L": L}} for d, L in dark]
             + [{"date": "2026-09-20", "value": {"deck_median": 86.7}}]}
    ok("a misfiling dated after the bind date FAILS",
       any("filed it as" in x for x in check_register(after)), str(check_register(after)))
    ok("...and the failure names the key the run must write instead",
       any(CANON_MEDIAN in x and "deck_median=86.7" in x for x in check_register(after)))
    # AND THE VALUE IS NOT ADOPTED. 86.7 is a light deck. The gate says the name is wrong; it does
    # not guess that the misfiled number is the measurement and count it, because guessing is the
    # widening this whole check refuses.
    ok("the misfiled value is NOT folded into the light deck count",
       not any("light deck(s)" in x for x in check_register(after)), str(check_register(after)))
    # The note and the failure must not share a line, which is the defect itself one level up.
    before = {"entries": [{"date": d, "value": {"deck_median_L": L}} for d, L in dark]
              + [{"date": "2026-09-01", "value": {"deck_median": 6.0}}]}
    ok("a misfiling dated before the bind date does not fail",
       not any("filed it as" in x for x in check_register(before)))
    ok("...and it is no longer counted among the entries that predate the measurement",
       misfiled_median(before["entries"][-1]) != [])

    print("\nledger_check self-test: " + ("all passed" if not fails else f"{fails} FAILED"))
    return 1 if fails else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--date", help="run date, to read out/<date>/figures.json")
    ap.add_argument("--ledger-dir", default="ledger/carousel")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--derive", action="store_true",
                    help="rewrite captions.json's three derived exclusion lists from its own "
                         "entries, then check. Writes nothing else and clears no other finding")
    a = ap.parse_args()
    if a.self_test:
        return self_test()

    d = REPO_ROOT / a.ledger_dir
    cp, tp = d / "captions.json", d / "topics.json"
    for p in (cp, tp):
        if not p.exists():
            print(f"ledger_check: {p} does not exist", file=sys.stderr)
            return 2
    if a.derive:
        before = cp.read_text(encoding="utf-8")
        after = derive_text(before, (REPO_ROOT / DOCTRINE).read_text(encoding="utf-8"))
        if after == before:
            print(f"ledger_check --derive: {cp.name}'s three exclusion lists already agree with "
                  f"its entries. Nothing was written")
        else:
            cp.write_text(after, encoding="utf-8")
            old, new = json.loads(before), json.loads(after)
            for k in DERIVED_KEYS:
                if old.get(k) != new.get(k):
                    print(f"ledger_check --derive: {k} was {old.get(k)!r} and the entries derive "
                          f"{new.get(k)!r}")
    figures = None
    if a.date:
        fp = REPO_ROOT / "out" / a.date / "figures.json"
        if not fp.exists():
            fp = REPO_ROOT / "runs/carousel" / a.date / "figures.json"
        if not fp.exists():
            print(f"ledger_check: --date {a.date} was given and no figures.json was found for it. "
                  f"The topic prose check needs the run's computed counts", file=sys.stderr)
            return 2
        figures = json.loads(fp.read_text(encoding="utf-8"))

    problems = run(json.loads(cp.read_text(encoding="utf-8")),
                   json.loads(tp.read_text(encoding="utf-8")),
                   figures, (REPO_ROOT / DOCTRINE).read_text(encoding="utf-8"))
    if problems:
        print(f"ledger_check: {len(problems)} problem(s)\n", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        print("\n  These lists and this prose are DERIVED. Recompose them from the entries and "
              "from figures.json rather than editing them beside it.\n"
              "  The three exclusion lists have one committed derivation and it is this file's:\n"
              "      python3 scripts/carousel/ledger_check.py --derive\n"
              "  Writing a fresh derivation into out/<date>/ instead is what has put those three "
              "lists\n  one entry behind on four runs running.", file=sys.stderr)
        return 1
    print("ledger_check: the variety ledgers agree with their own entries and with the run's "
          "computed counts")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                                       # noqa: BLE001
        print(f"ledger_check: broke: {exc}", file=sys.stderr)
        sys.exit(2)
