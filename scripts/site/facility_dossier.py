#!/usr/bin/env python3
"""facility_dossier.py — what is actually known about one certified data center.

WHY THIS EXISTS

The Comptroller's registry gives every facility five fields. A reader who wants to know what a
building actually is, how big, whose, drawing what, cooled how, gets nothing from those five. The
dossier is the researched answer, one facility at a time, and it is the part of this site that
cannot be assembled by anyone who has not done the work.

THE RULE THAT MAKES IT PUBLISHABLE

`CLAUDE.md` says no numeral is ever typed by a person or produced by a language model. A
researched figure looks like exactly the thing that law forbids, so the shape here matters.

    A NUMBER IS A FIELD, NEVER A SENTENCE. Every figure lives in `facts[]` as a real value with
    a unit and a source id. `render()` formats it and `authorised()` authorises it THROUGH THE
    SAME CALL, so a displayed figure and an authorised figure cannot disagree.

    PROSE CARRIES NO NUMERALS AT ALL. `summary`, `notes[].text` and `gaps[]` are checked for
    digits and the gate fails on any. A note says Google backstops the lease obligations. The
    amount is a fact field beside it. This is what stops a model from writing a number into a
    sentence where nothing downstream would check it.

WHAT ELSE THE GATE ASSERTS

  Every fact names a source id that exists. Every source carries a url, a publisher and a
  retrieved date. Every dossier name matches a facility in the registry exactly, because a
  dossier attached to a facility that does not exist is worse than no dossier. Slugs are unique
  and url safe. `gaps[]` is non empty, because a facility with nothing unknown has not been
  researched, it has been guessed at.

SOURCE RUNGS. `knowledge/shared/DATACENTER_REGISTRY.md` ranks sources one to seven, filings at
the top and aggregators at the bottom. The rung rides on every source so the page can show a
reader whether a figure came from an SEC exhibit or from a directory site.

    facility_dossier.py              # check the ledger against the registry
    facility_dossier.py --self-test  # hermetic
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledger" / "facilities" / "dossiers.json"
REGISTRY = ROOT / "ledger" / "gridwatch" / "datacenters.json"
DIGIT = re.compile(r"\d")
SLUG_OK = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PROSE_FIELDS = ("summary",)

# A NAME THE STATE SPELLS, DECLARED FACT BY FACT.
#
# The registry names an owner "Galaxy Helios I" and a facility "Riot Corsicana Data Center I".
# That trailing roman numeral is a first person pronoun to `house_style_check`, which was right
# on the letter and wrong on the page: renaming either to satisfy a lint would publish a name no
# filing uses, and on the Helios row the letter is the whole point, because a second Helios
# certification spells the same occupant with a digit.
#
# So a fact DECLARES `proper_name` and `panel()` marks that exact string in the markup, which is
# the mechanism the house checker already uses for a page title. It is bounded here rather than
# there, because this is the module that owns the data: a declared name must be TEXT, never a
# computed value, and it must be NAME SHAPED. A text fact is allowed to be a sentence, and
# several are, so without that bound the flag would be a way to lift a whole sentence out of the
# house rules.
NAME_MAX_WORDS = 8
NAME_BANNED = ":;"

# A text fact may transcribe a street number, a project code or a date. It may not carry a
# measurement, count, duration, order or proportion. These patterns stay structural. They look
# for a quantity word beside the noun it measures and leave identifiers alone when the same word
# is part of a company, phase, model, legal code or calendar phrase.
CARDINAL = (r"zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
            r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|"
            r"thirty|forty|fifty|sixty|seventy|eighty|ninety|"
            r"single|both|pair|dozens?")
MULTIPLICITY = rf"(?:{CARDINAL}|several|multiple|hundreds?)"
COUNT_NOUN = (r"years?|months?|roles?|renewals?|options?|reactors?|entities|tenants?|"
              r"utility\s+feeds?|feeds?|"
              r"siblings?|filings?|sites?|stories|story|warehouses?|offices?|data\s+halls?|"
              r"data\s+centers?|servers?|workers?|jobs?|units?|buildings?|facilities?")
QUANTITY_TEXT = re.compile(r"""
    \b(?:
        \d(?:[\d,]*\d)?(?:\.\d+)?\s*(?:million\s+)?
        (?:MW|GW|MVA|kV|gpm|kWh|acres?|sq\s*ft|square\s+feet|miles?|feet|foot|
           gallons?(?:\s+per\s+day)?|years?|months?|workers?|jobs?|buildings?|
           units?|facilities?|roles?|options?|reactors?|entities|tenants?|utility\s+feeds?|
           percent|exahashes?\s+per\s+second)
      | (?:MULTIPLICITY)(?:\s+of)?[ -]+(?:\w+[ -]+){0,3}(?:COUNT_NOUN)
      | no[ -]+(?:\w+[ -]+){0,3}(?:COUNT_NOUN)
      | (?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+
        (?:\w+[ -]+){0,2}(?:buildings?|facilities?)
      | (?:majority|minority)
      | (?:half|(?:a|one|three)\s+quarters?)
      | near\s+zero\s+(?:water|power|energy|use|utilization|consumption)
      | no\s+(?:daily\s+)?(?:makeup\s+process\s+water|cooling\s+water(?:\s+use)?|
           independent\s+onsite\s+power\s+generation)
    )\b
""".replace("MULTIPLICITY", MULTIPLICITY).replace("COUNT_NOUN", COUNT_NOUN),
    re.IGNORECASE | re.VERBOSE)


def quantity_in_text(text: str):
    """Return the first unstructured quantity match after narrow identifier exemptions."""
    cleaned = re.sub(r"\bsingle purpose entit(?:y|ies)\b", "", str(text), flags=re.IGNORECASE)
    cleaned = re.sub(
        r"\b(?:first|second)\s+half\s+of\s+(?:the\s+year|(?:19|20)\d{2})\b",
        "",
        cleaned,
        flags=re.IGNORECASE,
    )
    return QUANTITY_TEXT.search(cleaned)


# ---------------------------------------------------------------- formatting
def commas(n) -> str:
    return f"{int(round(n)):,}"


def money(v) -> str:
    """A dollar figure at the scale a reader reads it. The rounding rule is stated, not chosen
    per figure, because rounding is a computation and not a stylistic decision."""
    v = float(v)
    if v >= 1_000_000_000:
        s = f"{v / 1_000_000_000:.1f}".rstrip("0").rstrip(".")
        return f"${s} billion"
    if v >= 1_000_000:
        s = f"{v / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"${s} million"
    return f"${commas(v)}"


def plain(v) -> str:
    """A number that is not money. Integers keep no decimal point, so 1.2 stays 1.2 and 168
    does not become 168.0."""
    v = float(v)
    return commas(v) if v == int(v) else f"{v:g}"


def scaled(v) -> str:
    """A large whole quantity in the words a reader can scan.

    This is deliberately narrower than ``money``. Gallon ranges in public filings are often
    stated in whole millions, while smaller daily flows need their exact thousands separator.
    The formatter makes that decision from the value rather than from prose in the ledger.
    """
    v = float(v)
    if abs(v) >= 1_000_000 and v % 1_000_000 == 0:
        return f"{plain(v / 1_000_000)} million"
    return plain(v)


def counted(v, singular: str, plural: str | None = None, *, attributive=False) -> str:
    """A count with grammar derived from the value.

    ``attributive`` keeps the singular noun in phrases such as ``2 story data center``. The
    number remains a field and the surrounding description remains ordinary text.
    """
    plural = plural or singular + "s"
    word = singular if attributive or float(v) == 1 else plural
    return f"{plain(v)} {word}"


def ordered(v, noun: str) -> str:
    n = int(v)
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix} {noun}"


# Every formatter accepts the attributive flag even when the unit cannot use it. One call shape
# keeps scalar facts, ranges, alternatives and composite counts on the same rendering path.
UNITS = {
    "MW": lambda v, attributive=False: f"{plain(v)} MW",
    "GW": lambda v, attributive=False: f"{plain(v)} GW",
    "MVA": lambda v, attributive=False: f"{plain(v)} MVA",
    "kV": lambda v, attributive=False: f"{plain(v)} kV",
    "acres": lambda v, attributive=False: counted(v, "acre"),
    "miles": lambda v, attributive=False: counted(v, "mile"),
    "feet": lambda v, attributive=False: counted(v, "foot", "feet"),
    "sqft": lambda v, attributive=False: f"{plain(v)} sq ft",
    "usd": lambda v, attributive=False: money(v),
    "percent": lambda v, attributive=False: f"{plain(v)} percent",
    "jobs": lambda v, attributive=False: counted(v, "job"),
    "workers": lambda v, attributive=False: counted(v, "worker"),
    "buildings": lambda v, attributive=False: counted(v, "building", attributive=attributive),
    "warehouses": lambda v, attributive=False: counted(v, "warehouse"),
    "offices": lambda v, attributive=False: counted(v, "office"),
    "stories": lambda v, attributive=False: counted(v, "story", "stories",
                                                       attributive=attributive),
    "data_halls": lambda v, attributive=False: counted(v, "data hall"),
    "units": lambda v, attributive=False: counted(v, "unit"),
    "facilities": lambda v, attributive=False: counted(v, "facility", "facilities"),
    "roles": lambda v, attributive=False: counted(v, "role"),
    "options": lambda v, attributive=False: counted(v, "option"),
    "reactors": lambda v, attributive=False: counted(v, "reactor"),
    "entities": lambda v, attributive=False: counted(v, "entity", "entities"),
    "tenants": lambda v, attributive=False: counted(v, "tenant", attributive=attributive),
    "utility_feeds": lambda v, attributive=False: counted(v, "utility feed"),
    "building_order": lambda v, attributive=False: ordered(v, "building"),
    "facility_order": lambda v, attributive=False: ordered(v, "facility"),
    "years": lambda v, attributive=False: counted(v, "year"),
    "months": lambda v, attributive=False: counted(v, "month"),
    "gallons": lambda v, attributive=False: f"{scaled(v)} gallons",
    "gallons_per_day": lambda v, attributive=False: f"{scaled(v)} gallons per day",
    "gpm": lambda v, attributive=False: f"{plain(v)} gallons per minute",
    "exahashes_per_second": lambda v, attributive=False: (
        f"{plain(v)} exahashes per second"),
    "usd_per_kwh": lambda v, attributive=False: f"${plain(v)} per kWh",
}

QUALIFIERS = {"about": "about", "less_than": "less than"}
DATE_INTROS = {"for", "in"}
SEASONS = {"spring", "summer", "fall", "winter"}


def numeric_shape(fact: dict) -> str:
    """Name the one structured quantity shape a fact carries, or return an empty string."""
    shapes = []
    if "value" in fact:
        shapes.append("value")
    if "minimum" in fact or "maximum" in fact:
        shapes.append("range")
    if "alternatives" in fact:
        shapes.append("alternatives")
    if "quantities" in fact:
        shapes.append("quantities")
    return shapes[0] if len(shapes) == 1 else ("mixed" if shapes else "")


def one_quantity(value, unit: str, *, attributive=False) -> str:
    fn = UNITS.get(unit)
    if fn is None:
        raise KeyError(f"no formatter for unit {unit!r}")
    return fn(value, attributive)


def date_context(value: dict) -> str:
    """A month or season with its year, kept as data rather than a sentence fragment."""
    year = int(value["year"])
    if value.get("month") is not None:
        return f"{MONTHS[int(value['month']) - 1]} {year}"
    return f"{value['season']} {year}"


def show(fact: dict) -> str:
    """The one place a fact becomes a string. `authorised()` calls this too, which is the whole
    reason a displayed figure and an authorised figure can never drift apart."""
    shape = numeric_shape(fact)
    if not shape:
        return str(fact.get("text", ""))
    if shape == "mixed":
        raise ValueError("a fact carries more than one numeric shape")

    unit = fact.get("unit")
    if shape == "value":
        core = one_quantity(fact["value"], unit, attributive=bool(fact.get("attributive")))
    elif shape == "range":
        # Repeating MW is useful in a list of alternatives. A range reads more cleanly with
        # the shared unit once, and this wave uses ranges only for gallons.
        if unit == "gallons":
            core = f"{scaled(fact['minimum'])} to {scaled(fact['maximum'])} gallons"
        else:
            core = (f"{one_quantity(fact['minimum'], unit)} to "
                    f"{one_quantity(fact['maximum'], unit)}")
    elif shape == "alternatives":
        shown = [one_quantity(v, unit) for v in fact["alternatives"]]
        core = shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + ", or " + shown[-1]
    else:
        shown = [one_quantity(q["value"], q["unit"],
                              attributive=bool(q.get("attributive")))
                 for q in fact["quantities"]]
        core = shown[0] if len(shown) == 1 else ", ".join(shown[:-1]) + " and " + shown[-1]

    qualifier = QUALIFIERS.get(fact.get("qualifier"), "")
    bits = [str(fact.get("prefix") or "").strip(), qualifier, core,
            str(fact.get("suffix") or "").strip()]
    out = " ".join(x for x in bits if x)
    if fact.get("date"):
        out += f" {fact.get('date_intro', 'in')} {date_context(fact['date'])}"
    return out


REGISTRY_PUBLISHER = "Texas Comptroller of Public Accounts"
REGISTRY_ROLE_LABELS = {
    "Owner of record",
    "Occupant of record",
    "Operator of record",
    "Additional owner of record",
    "Additional occupant of record",
    "Additional operator of record",
}


def fact_stamp(fact: dict, sources: dict[str, dict]) -> tuple[str, str]:
    """Return the label and date that the reader should see beside a fact.

    Registry parties are the parties on the latest reading. The effective date belongs to the
    certification and cannot date those parties because the Comptroller edits rows in place.
    Older dossiers stored the certification date in ``as_of`` on role facts. The renderer uses
    the source reading date for that narrow class so it cannot turn a current row into history.
    """
    source = sources.get(fact.get("source")) or {}
    if (fact.get("label") in REGISTRY_ROLE_LABELS
            and source.get("publisher") == REGISTRY_PUBLISHER
            and source.get("retrieved")):
        return "registry read", str(source["retrieved"])
    if fact.get("as_of"):
        return "as of", str(fact["as_of"])
    return "", ""


# ---------------------------------------------------------------- loading
def load(path: pathlib.Path = LEDGER) -> dict:
    if not path.exists():
        return {"_spec": 1, "dossiers": []}
    return json.loads(path.read_text(encoding="utf-8"))


def registry_names(path: pathlib.Path = REGISTRY) -> set[str]:
    if not path.exists():
        return set()
    d = json.loads(path.read_text(encoding="utf-8"))
    return {f["name"] for f in d.get("facilities") or []}


def by_name(doc: dict) -> dict[str, dict]:
    return {d["name"]: d for d in doc.get("dossiers") or []}


# ---------------------------------------------------------------- the gate
def name_problems(fct: dict) -> list[str]:
    """What disqualifies a fact from declaring its value a proper name.

    The flag buys one thing, an exemption from the sentence rules, so it has to be impossible to
    point at a sentence. A name is text, it is short, it does not end a thought and it carries no
    clause punctuation."""
    if numeric_shape(fct):
        return ["declares proper_name on a computed value, where the formatter owns the string"]
    text = str(fct.get("text", "")).strip()
    out = []
    if not text:
        out.append("declares proper_name with no text")
        return out
    if text.endswith((".", "?", "!")):
        out.append("declares proper_name on a sentence, which ends in terminal punctuation")
    if any(c in text for c in NAME_BANNED):
        out.append("declares proper_name on text carrying clause punctuation")
    if len(text.split()) > NAME_MAX_WORDS:
        out.append(f"declares proper_name on {len(text.split())} words, "
                   f"and a name runs to {NAME_MAX_WORDS}")
    return out


def is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def quantity_problems(fct: dict) -> list[str]:
    """Validate one fact's quantity shape without confusing identifiers for measurements."""
    out = []
    shape = numeric_shape(fct)
    label = fct.get("label")

    if not shape:
        text = str(fct.get("text") or "")
        if text and quantity_in_text(text):
            out.append(f"fact {label!r} carries a quantity in text, which must be structured")
        return out
    if shape == "mixed":
        return [f"fact {label!r} carries more than one numeric shape"]
    if fct.get("text"):
        out.append(f"fact {label!r} mixes text with a structured quantity")

    unit = fct.get("unit")
    if shape in {"value", "range", "alternatives"} and unit not in UNITS:
        out.append(f"fact {label!r} has unknown unit {unit!r}")

    if shape == "value" and not is_number(fct.get("value")):
        out.append(f"fact {label!r} has a non numeric value")
    elif (shape == "value" and unit in {"building_order", "facility_order"}
          and (float(fct["value"]) < 1 or not float(fct["value"]).is_integer())):
        out.append(f"fact {label!r} has an order that is not a positive whole number")
    elif shape == "range":
        lo, hi = fct.get("minimum"), fct.get("maximum")
        if not is_number(lo) or not is_number(hi):
            out.append(f"fact {label!r} has a non numeric range bound")
        elif lo > hi:
            out.append(f"fact {label!r} has a range whose minimum exceeds its maximum")
    elif shape == "alternatives":
        values = fct.get("alternatives")
        if not isinstance(values, list) or len(values) < 2 or not all(is_number(v) for v in values):
            out.append(f"fact {label!r} needs at least two numeric alternatives")
    elif shape == "quantities":
        quantities = fct.get("quantities")
        if not isinstance(quantities, list) or len(quantities) < 2:
            out.append(f"fact {label!r} needs at least two component quantities")
        else:
            for i, quantity in enumerate(quantities):
                if not isinstance(quantity, dict) or not is_number(quantity.get("value")):
                    out.append(f"fact {label!r} component {i} has a non numeric value")
                elif quantity.get("unit") not in UNITS:
                    out.append(f"fact {label!r} component {i} has unknown unit "
                               f"{quantity.get('unit')!r}")
                if quantity.get("attributive") not in (None, True, False):
                    out.append(f"fact {label!r} component {i} has a non boolean attributive flag")

    if fct.get("qualifier") not in (None, *QUALIFIERS):
        out.append(f"fact {label!r} has unknown qualifier {fct.get('qualifier')!r}")
    if fct.get("attributive") not in (None, True, False):
        out.append(f"fact {label!r} has a non boolean attributive flag")
    for field in ("prefix", "suffix"):
        if fct.get(field) is not None and not isinstance(fct[field], str):
            out.append(f"fact {label!r} has a non text {field}")
        elif fct.get(field) and quantity_in_text(fct[field]):
            out.append(f"fact {label!r} carries another quantity in its {field}")

    date = fct.get("date")
    if date is not None:
        if not isinstance(date, dict) or not isinstance(date.get("year"), int):
            out.append(f"fact {label!r} has a date without a numeric year")
        else:
            month, season = date.get("month"), date.get("season")
            if (month is None) == (season is None):
                out.append(f"fact {label!r} date needs exactly one month or season")
            elif month is not None and (not isinstance(month, int) or not 1 <= month <= 12):
                out.append(f"fact {label!r} has an invalid date month")
            elif season is not None and season not in SEASONS:
                out.append(f"fact {label!r} has an invalid date season")
        if fct.get("date_intro") not in DATE_INTROS:
            out.append(f"fact {label!r} date needs a supported introduction")
    elif fct.get("date_intro") is not None:
        out.append(f"fact {label!r} has a date introduction without a date")

    return out


def problems(doc: dict, names: set[str]) -> list[str]:
    out: list[str] = []
    seen_slugs: dict[str, str] = {}

    for d in doc.get("dossiers") or []:
        name = d.get("name", "(unnamed)")
        where = f"dossier {name!r}"

        if names and name not in names:
            out.append(f"{where} names a facility that is not in the registry")

        slug = d.get("slug", "")
        if not SLUG_OK.match(slug):
            out.append(f"{where} has slug {slug!r}, which is not url safe")
        elif slug in seen_slugs and seen_slugs[slug] != name:
            out.append(f"{where} reuses the slug of {seen_slugs[slug]!r}")
        else:
            seen_slugs[slug] = name

        ids = {s.get("id") for s in d.get("sources") or []}
        if not ids:
            out.append(f"{where} carries no sources")
        for s in d.get("sources") or []:
            for field in ("url", "title", "publisher", "retrieved"):
                if not s.get(field):
                    out.append(f"{where} source {s.get('id')!r} is missing {field}")
            if not isinstance(s.get("rung"), int):
                out.append(f"{where} source {s.get('id')!r} has no source rung")

        if not d.get("facts"):
            out.append(f"{where} carries no facts")
        for fct in d.get("facts") or []:
            if fct.get("source") not in ids:
                out.append(f"{where} fact {fct.get('label')!r} cites unknown source "
                           f"{fct.get('source')!r}")
            out.extend(f"{where} {why}" for why in quantity_problems(fct))
            if not numeric_shape(fct) and not fct.get("text"):
                out.append(f"{where} fact {fct.get('label')!r} has neither a value nor text")
            if fct.get("proper_name"):
                out.extend(f"{where} fact {fct.get('label')!r} {why}"
                           for why in name_problems(fct))

        # THE LAW. A digit in a sentence is a number a model typed, and nothing downstream
        # would catch it. Numbers live in facts, where the formatter owns them.
        for field in PROSE_FIELDS:
            if DIGIT.search(str(d.get(field) or "")):
                out.append(f"{where} has a numeral in its {field}, which must be a fact instead")
        for i, note in enumerate(d.get("notes") or []):
            if note.get("as_of") and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(note["as_of"])):
                out.append(f"{where} note {i} has an as_of that is not an ISO date")
            if DIGIT.search(str(note.get("text") or "")):
                out.append(f"{where} note {i} has a numeral in prose, which must be a fact instead")
            for sid in note.get("sources") or []:
                if sid not in ids:
                    out.append(f"{where} note {i} cites unknown source {sid!r}")
        for i, gap in enumerate(d.get("gaps") or []):
            if DIGIT.search(str(gap)):
                out.append(f"{where} gap {i} has a numeral in prose")

        if not d.get("gaps"):
            out.append(f"{where} names no gaps, and a facility with nothing unknown about it "
                       f"has been guessed at rather than researched")

    return out


# The gate's own tokeniser, imported rather than copied. A second copy of this pattern is a
# second thing to keep in step, and the whole failure mode here is two versions of one rule.
try:
    from numeral_lint import NUMERAL as _NUMERAL
except Exception:  # pragma: no cover - only when run outside the site package
    _NUMERAL = re.compile(r"\d(?:[\d,]*\d)?(?:\.\d+)?")


def authorised(doc: dict) -> set[str]:
    """Every numeral string a dossier page may show, produced by the same call that shows it.

    THE DATES GO THROUGH `ordinal()`, NOT THE RAW ISO. The first version of this authorised
    `2024-11-19` while the page printed `November 19th, 2024`, so the build reported three
    real violations on a correct page. A display path and an authorisation path that are not
    the same call WILL drift, which is the exact thing this module's docstring warns about,
    and it drifted here first.

    TEXT FACTS HAVE THEIR NUMERALS AUTHORISED, and the reason is narrow enough to state. A
    text fact is a TRANSCRIBED IDENTIFIER from a cited source: a street address, a postcode,
    a lease year, a facility name the state assigned. None of them is a quantity and none is
    arithmetic. Every actual QUANTITY is forced into a value field by `problems()`, where the
    formatter owns it, and prose is forbidden a digit at all. So this authorises the class of
    numeral a model cannot use to smuggle a computed figure past the gate.
    """
    out: set[str] = set()

    def tokens(text: str) -> set[str]:
        return set(_NUMERAL.findall(str(text)))

    for d in doc.get("dossiers") or []:
        sources = {s.get("id"): s for s in d.get("sources") or []}
        out |= tokens(d.get("name", ""))
        for fct in d.get("facts") or []:
            if numeric_shape(fct):
                out.add(show(fct))
            else:
                out |= tokens(fct.get("text", ""))
            _, stamp = fact_stamp(fct, sources)
            if stamp:
                out.add(ordinal(stamp))
        for note in d.get("notes") or []:
            if note.get("as_of"):
                out.add(ordinal(note["as_of"]))
        for s in d.get("sources") or []:
            if s.get("retrieved"):
                out.add(ordinal(s["retrieved"]))
            # A SOURCE TITLE IS THE MOST VERBATIM STRING ON THE PAGE. One of these documents is
            # actually called "Crusoe's 998,000 Square Foot Data Center" and another "to 1.2
            # Gigawatts". Altering either to satisfy a lint would misquote a citation, which is
            # a worse fault than the one the lint is guarding against. Same narrow class as the
            # transcribed identifiers above: quoted, sourced, and never arithmetic.
            out |= tokens(s.get("title", ""))
            out |= tokens(s.get("publisher", ""))
    return out


# ---------------------------------------------------------------- rendering
# What a source rung MEANS to a reader, from knowledge/shared/DATACENTER_REGISTRY.md. A figure
# from an SEC exhibit and a figure from a directory site are not the same kind of fact, and a
# page that shows them identically is quietly lying about how much it knows.
RUNGS = {1: "filing", 2: "company", 3: "local government", 4: "permit",
         5: "grid operator", 6: "trade press", 7: "directory"}
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


def e(t) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def ordinal(iso: str) -> str:
    """August 21st, 2026. The house form, month first, ordinal day."""
    y, m, d = (int(x) for x in str(iso).split("-"))
    suf = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return f"{MONTHS[m - 1]} {d}{suf}, {y}"


def panel(d: dict, *, heading: int = 3) -> str:
    """The dossier body. The PAGE and the DIALOG render this same call, so the two can never
    drift into showing a reader different things about one facility."""
    h = f"h{heading}"
    src_n = {s["id"]: i + 1 for i, s in enumerate(d.get("sources") or [])}
    sources_by_id = {s.get("id"): s for s in d.get("sources") or []}

    def cite(sid):
        n = src_n.get(sid)
        return (f'<sup class="dcite">[<a href="#dsrc-{e(d["slug"])}-{n}">{n}</a>]</sup>'
                if n else "")

    rows = []
    for f in d.get("facts") or []:
        stamp_label, stamp_date = fact_stamp(f, sources_by_id)
        when = (f'<span class="dwhen">{e(stamp_label)} {e(ordinal(stamp_date))}</span>'
                if stamp_date else "")
        # The declaration travels with the value, so the exemption is visible in the markup at
        # the point of use rather than asserted somewhere a reader of the page would not find it.
        mark = f' data-proper-name="{e(show(f))}"' if f.get("proper_name") else ""
        rows.append(f'<div class="drow"><dt>{e(f.get("label", ""))}</dt>'
                    f'<dd><span class="dval"{mark}>{e(show(f))}</span>{cite(f.get("source"))}'
                    f'{when}</dd></div>')

    notes = "".join(
        f'<li>{e(n.get("text", ""))}'
        + "".join(cite(x) for x in (n.get("sources") or []))
        + (f'<span class="dwhen">{e(ordinal(n["as_of"]))}</span>' if n.get("as_of") else "")
        + "</li>"
        for n in d.get("notes") or [])

    def stop(t: str) -> str:
        t = str(t).strip()
        return t if t.endswith((".", "?", "!")) else t + "."

    gaps = "".join(f"<li>{e(stop(g))}</li>" for g in d.get("gaps") or [])

    sources = "".join(
        f'<li id="dsrc-{e(d["slug"])}-{i + 1}">'
        f'<a href="{e(s["url"])}" rel="nofollow noopener">'
        f'<cite>{e(s["title"])}</cite></a>. '
        f'<span class="dpub"><cite>{e(s["publisher"])}</cite></span>. '
        f'<span class="drung">{e(RUNGS.get(s.get("rung"), "other"))}</span>. '
        f'<span class="dwhen">Read {e(ordinal(s["retrieved"]))}.</span></li>'
        for i, s in enumerate(d.get("sources") or []))

    return (
        f'<div class="dossier">'
        f'<p class="dsum">{e(d.get("summary", ""))}</p>'
        f'<{h}>What is known</{h}><dl class="dfacts">{"".join(rows)}</dl>'
        + (f'<{h}>Worth knowing</{h}><ul class="dnotes">{notes}</ul>' if notes else "")
        + (f'<{h}>What is not public</{h}><ul class="dgaps">{gaps}</ul>' if gaps else "")
        + f'<{h}>Sources</{h}><ol class="dsources">{sources}</ol>'
        f'</div>')


# ---------------------------------------------------------------- self test
def self_test() -> int:
    checks = []

    def check(name, ok, detail=""):
        checks.append(ok)
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}{('  ' + str(detail)) if not ok else ''}")

    good = {
        "name": "X", "slug": "x", "summary": "A plain sentence.",
        "facts": [{"label": "Load", "value": 168, "unit": "MW", "source": "s1"}],
        "notes": [{"text": "Prose with no digits.", "sources": ["s1"]}],
        "gaps": ["Cooling is not public"],
        "sources": [{"id": "s1", "url": "https://e.x", "title": "T", "publisher": "P",
                     "rung": 1, "retrieved": "2026-08-21"}],
    }
    names = {"X"}

    def one(mutate=None):
        import copy
        d = copy.deepcopy(good)
        if mutate:
            mutate(d)
        return problems({"dossiers": [d]}, names)

    check("a well formed dossier passes", one() == [], one())

    # The law, in both places a model could break it.
    check("a numeral in the summary fails",
          one(lambda d: d.update(summary="It draws 168 MW.")) != [])
    check("a numeral in a note fails",
          one(lambda d: d["notes"].__setitem__(0, {"text": "Google put up $1.4 billion.",
                                                   "sources": ["s1"]})) != [])
    check("a numeral in a gap fails", one(lambda d: d.update(gaps=["2 things unknown"])) != [])
    quantity_texts = (
        "Direct 345 kV transmission connection",
        "State Highway 211 about 800 feet south of Lambda Drive",
        "Approximately 11.6 exahashes per second",
        "Between 1 million and 2 million gallons",
        "One warehouse and one office",
        "New two story data center with site improvements",
        "Six data halls and a project substation",
        "Amazon Data Services, Inc. in all three roles",
        "Ten year triple net lease with Nscale",
        "Two five year extension options",
        "The fourth Red Oak building",
        "Four AP1000 nuclear reactors under federal application",
        "Both registry entities are IREN subsidiaries",
        "Near zero water utilization efficiency",
        "No daily makeup process water",
        "Single utility feed",
        "One prospective tenant",
        "Majority clean with a minority of onsite gas",
        "Thirty facilities are planned",
        "Several buildings share the campus",
        "Multiple data halls are planned",
        "Hundreds of facilities could be built",
        "No facilities are operating",
        "Half of the campus load is reserved",
        "A quarter of the buildings are operating",
    )
    missed = [text for text in quantity_texts
              if not quantity_problems({"label": "Test", "text": text})]
    check("quantity shaped text facts fail", not missed, missed)
    check("a street number remains an identifier",
          not quantity_problems({"label": "Address", "text": "5150 Rogers Road"}))
    check("a project code remains an identifier",
          not quantity_problems({"label": "Company", "text": "RPI AUS01-0H DC LLC"}))
    check("a month and year remain a date",
          not quantity_problems({"label": "Target", "text": "December 2028"}))
    allowed_identifiers = (
        "CyrusOne", "Cyrus One Allen", "AP1000", "LBB-01", "DFW III",
        "Phase One", "Phase Two", "Freebird Phase One", "Sweetwater One",
        "Horizons One through Four", "Tier 3", "N plus one", "Chapter 312",
        "First quarter of 2027", "Second half of the year", "Second half of 2026",
        "Triple net lease",
        "A single purpose entity", "This one", "The one", "All parties",
        "None is listed", "No final order", "No City supply", "Around the clock",
    )
    false_positives = [text for text in allowed_identifiers
                       if quantity_problems({"label": "Identifier", "text": text})]
    check("identifiers, calendar language and evidence absence stay prose",
          not false_positives, false_positives)
    check("a second quantity hidden in a prefix fails",
          bool(quantity_problems({"label": "Buildings", "value": 2, "unit": "buildings",
                                  "prefix": "and 99 buildings"})))
    check("a second quantity hidden in a suffix fails",
          bool(quantity_problems({"label": "Buildings", "value": 2, "unit": "buildings",
                                  "suffix": "plus six facilities"})))
    fragment_quantities = (
        "with thirty facilities", "across several buildings", "beside multiple data halls",
        "among hundreds of facilities", "with no facilities operating", "covering half the site",
        "and a quarter of the campus",
    )
    missed_prefixes = [text for text in fragment_quantities
                       if not quantity_problems({"label": "Buildings", "value": 2,
                                                 "unit": "buildings", "prefix": text})]
    missed_suffixes = [text for text in fragment_quantities
                       if not quantity_problems({"label": "Buildings", "value": 2,
                                                 "unit": "buildings", "suffix": text})]
    check("expanded quantity forms fail in prefixes", not missed_prefixes, missed_prefixes)
    check("expanded quantity forms fail in suffixes", not missed_suffixes, missed_suffixes)

    check("a fact citing an unknown source fails",
          one(lambda d: d["facts"][0].update(source="nope")) != [])
    check("a note citing an unknown source fails",
          one(lambda d: d["notes"][0].update(sources=["nope"])) != [])
    check("a source missing its retrieved date fails",
          one(lambda d: d["sources"][0].pop("retrieved")) != [])
    check("a source missing its rung fails", one(lambda d: d["sources"][0].pop("rung")) != [])
    check("an unknown unit fails", one(lambda d: d["facts"][0].update(unit="furlongs")) != [])
    check("a non numeric value fails", one(lambda d: d["facts"][0].update(value="lots")) != [])
    check("a dossier with no gaps fails", one(lambda d: d.update(gaps=[])) != [])
    check("a dossier with no facts fails", one(lambda d: d.update(facts=[])) != [])
    check("a slug that is not url safe fails", one(lambda d: d.update(slug="Not A Slug")) != [])
    check("a dossier for a facility not in the registry fails",
          one(lambda d: d.update(name="Ghost")) != [])
    check("two dossiers sharing a slug fails",
          len(problems({"dossiers": [good, {**good, "name": "Y"}]}, {"X", "Y"})) > 0)

    # Formatting, where a wrong rule would put a wrong number on the page.
    check("megawatts read as integers", show({"value": 168, "unit": "MW"}) == "168 MW",
          show({"value": 168, "unit": "MW"}))
    check("a fractional gigawatt keeps its decimal", show({"value": 1.2, "unit": "GW"}) == "1.2 GW",
          show({"value": 1.2, "unit": "GW"}))
    check("square feet take thousands separators",
          show({"value": 998000, "unit": "sqft"}) == "998,000 sq ft",
          show({"value": 998000, "unit": "sqft"}))
    check("billions read as billions",
          show({"value": 9_100_000_000, "unit": "usd"}) == "$9.1 billion",
          show({"value": 9_100_000_000, "unit": "usd"}))
    check("a round billion drops the decimal",
          show({"value": 3_000_000_000, "unit": "usd"}) == "$3 billion",
          show({"value": 3_000_000_000, "unit": "usd"}))
    check("millions read as millions",
          show({"value": 450_000_000, "unit": "usd"}) == "$450 million",
          show({"value": 450_000_000, "unit": "usd"}))
    check("a fractional million keeps its decimal",
          show({"value": 9_500_000, "unit": "usd"}) == "$9.5 million",
          show({"value": 9_500_000, "unit": "usd"}))
    check("a percentage keeps its decimal",
          show({"value": 50.1, "unit": "percent"}) == "50.1 percent",
          show({"value": 50.1, "unit": "percent"}))
    check("an approximate rate keeps its qualifier",
          show({"value": 11.6, "unit": "exahashes_per_second", "qualifier": "about"})
          == "about 11.6 exahashes per second")
    check("a less than daily flow keeps its bound and context",
          show({"value": 4_000, "unit": "gallons_per_day", "qualifier": "less_than",
                "suffix": "for drinking and toilets"})
          == "less than 4,000 gallons per day for drinking and toilets")
    check("a gallon range keeps both structured bounds",
          show({"minimum": 1_000_000, "maximum": 2_000_000, "unit": "gallons"})
          == "1 million to 2 million gallons")
    check("alternatives keep every structured value",
          show({"alternatives": [25, 45, 65], "unit": "MW"})
          == "25 MW, 45 MW, or 65 MW")
    check("component quantities keep their separate nouns",
          show({"quantities": [{"value": 1, "unit": "warehouses"},
                               {"value": 1, "unit": "offices"}]})
          == "1 warehouse and 1 office")
    check("an attributive count keeps its surrounding description",
          show({"value": 2, "unit": "stories", "attributive": True,
                "prefix": "New", "suffix": "data center with site improvements"})
          == "New 2 story data center with site improvements")
    check("a month target is assembled from structured date fields",
          show({"value": 150, "unit": "MVA", "date": {"year": 2028, "month": 12},
                "date_intro": "for"}) == "150 MVA for December 2028")
    check("a season target is assembled from structured date fields",
          show({"value": 2, "unit": "buildings", "suffix": "approved",
                "date": {"year": 2026, "season": "winter"}, "date_intro": "in"})
          == "2 buildings approved in winter 2026")
    check("building order is computed",
          show({"value": 4, "unit": "building_order"}) == "4th building")
    check("a fractional building order fails",
          bool(quantity_problems({"label": "Order", "value": 1.5,
                                  "unit": "building_order"})))

    # The authorisation path is the display path.
    a = authorised({"dossiers": [good]})
    check("the authorised set carries the rendered figure", "168 MW" in a, sorted(a))

    # A DECLARED PROPER NAME, and the four ways it is not one. The flag buys an exemption from
    # the house sentence rules, so every one of these has to stay shut.
    def named(**kw):
        f = {"label": "Owner of record", "text": "Galaxy Helios I",
             "source": "s1", "proper_name": True}
        f.update(kw)
        return one(lambda d: d.update(facts=[f]))

    check("a name declares cleanly", named() == [], named())
    check("a declared name that ends a sentence fails",
          named(text="The name gives away nothing about where it stands.") != [])
    check("a declared name carrying a colon fails", named(text="Owner: Galaxy") != [])
    check("a declared name carrying a semicolon fails", named(text="Galaxy; Helios") != [])
    check("a declared name longer than a name fails",
          named(text="A lease with the Texas Tech University System and its regents") != [])
    check("a declared name on a computed value fails",
          named(text=None, value=168, unit="MW") != [])
    check("the declaration reaches the markup",
          'data-proper-name="Galaxy Helios I"' in panel(
              {**good, "facts": [{"label": "Owner of record", "text": "Galaxy Helios I",
                                  "source": "s1", "proper_name": True}]}))
    check("an undeclared value carries no marker",
          "data-proper-name" not in panel(good))

    registry = {
        **good,
        "facts": [{"label": "Owner of record", "text": "Example Owner LLC",
                   "source": "s1", "as_of": "2022-02-07"}],
        "sources": [{"id": "s1", "url": "https://e.x", "title": "Data Center Lists",
                     "publisher": REGISTRY_PUBLISHER, "rung": 1,
                     "retrieved": "2026-08-27"}],
    }
    registry_html = panel(registry)
    check("a registry role carries the reading date",
          "registry read August 27th, 2026" in registry_html, registry_html)
    check("a registry role does not turn certification into party history",
          "as of February 7th, 2022" not in registry_html, registry_html)
    dated_html = panel({**good, "facts": [{"label": "Company update", "text": "Current",
                                            "source": "s1", "as_of": "2022-02-07"}]})
    check("a non registry fact keeps its own date",
          "as of February 7th, 2022" in dated_html, dated_html)

    passed = sum(checks)
    print(f"\nfacility_dossier self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    doc = load()
    n = len(doc.get("dossiers") or [])
    if not n:
        print("facility_dossier: no dossiers yet")
        return 0
    bad = problems(doc, registry_names())
    if bad:
        print(f"facility_dossier: {len(bad)} problem(s)")
        for b in bad:
            print(f"  {b}")
        return 1
    facts = sum(len(d.get("facts") or []) for d in doc["dossiers"])
    print(f"facility_dossier: {n} dossier(s), {facts} facts, every one sourced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
