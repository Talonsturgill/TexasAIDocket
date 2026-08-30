#!/usr/bin/env python3
"""entities.py — who is behind the registry, resolved and counted.

WHY THIS EXISTS

The Comptroller's list is 151 rows and reads as 151 unrelated buildings. It is not. Forty one
companies appear on more than one of them, and the largest relationships in Texas are only
visible by reading DOWN a column rather than across a row. Oracle is the occupant of record at
more data centers than anyone, and nothing on a facility page could ever tell you that.

THE COMMA PROBLEM, WHICH IS THE WHOLE REASON THIS IS A MODULE AND NOT A GROUP BY

    Oracle America Cloud Services LLC     15 facilities
    Oracle America Cloud Services, LLC    10 facilities

That is one company, filed two ways, and a naive count reports the largest occupant in the state
as two mid sized ones. Sixteen companies are split like this. Google appears three ways, Whinstone
three ways, Amazon Data Services two.

TWO LAYERS, AND THE LINE BETWEEN THEM IS THE POINT

  1. RESOLUTION IS MECHANICAL. Case, punctuation and the corporate suffix are removed, and two
     strings that come out identical are one entity. There is no judgment in this and nothing to
     argue with. `Oracle America Cloud Services LLC` and `Oracle America Cloud Services, LLC`
     resolve together. `Oracle America Cloud Services` and `Oracle America, Inc.` do NOT, because
     they are different legal entities and collapsing them would destroy the distinction the
     filing was making.

  2. PARENT GROUPING IS CURATED, and lives in `config/entity_groups.json` as data owned by a
     human. Saying that Oracle America Cloud Services and Oracle America are both Oracle is a
     judgment. It is a correct one, and it is still a judgment, so it is written down where it can
     be read and disagreed with rather than buried in a regex.

The page shows both numbers and says which is which. A reader who trusts only the mechanical
layer gets a defensible figure; a reader who wants the corporate picture gets that too.

THE DISPLAY NAME IS THE STATE'S OWN. Where variants disagree the most frequent spelling wins,
ties broken by the longest, so this publishes a string the Comptroller actually used rather than
one this project tidied up.

    entities.py                # summarise the graph
    entities.py --self-test    # hermetic
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "ledger" / "gridwatch" / "datacenters.json"
GROUPS = ROOT / "config" / "entity_groups.json"
ROLES = ("owners", "occupants", "operators")
MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")

try:
    from numeral_lint import NUMERAL as _NUMERAL
except Exception:  # pragma: no cover
    _NUMERAL = re.compile(r"\d(?:[\d,]*\d)?(?:\.\d+)?")

# The corporate suffixes a filing clerk may or may not type. Removed for MATCHING only; the
# published name keeps whatever the state wrote.
SUFFIX = re.compile(
    r"\b(llc|l\s?l\s?c|inc|incorporated|ltd|limited|lp|l\s?p|corporation|corp|"
    r"company|co|holdings|us|usa)\b")


def normalise(name: str) -> str:
    """The mechanical rule. Case, punctuation and corporate suffix only."""
    s = str(name).lower().strip()
    s = re.sub(r"[.,'\"]", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = SUFFIX.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def slug(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    return re.sub(r"-{2,}", "-", s) or "entity"


def load_groups(path: pathlib.Path = GROUPS) -> dict:
    if not path.exists():
        return {"_spec": 1, "groups": []}
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(facilities: list[dict]) -> list[dict]:
    """Every entity in the registry, with the facilities and roles it holds.

    Sorted by reach then name, so the order is a property of the data rather than of the dict.
    """
    seen: dict[str, dict] = {}
    for f in facilities:
        for role in ROLES:
            for raw in f.get(role) or []:
                raw = str(raw).strip()
                if not raw:
                    continue
                key = normalise(raw)
                if not key:
                    continue
                e = seen.setdefault(key, {
                    "key": key, "variants": Counter(),
                    "roles": {r[:-1]: set() for r in ROLES}})
                e["variants"][raw] += 1
                e["roles"][role[:-1]].add(f["name"])

    out = []
    for e in seen.values():
        # The state's own dominant spelling: most used, ties to the longest.
        display = sorted(e["variants"].items(), key=lambda kv: (-kv[1], -len(kv[0])))[0][0]
        facs = set().union(*e["roles"].values())
        out.append({
            "key": e["key"],
            "name": display,
            "slug": slug(display),
            "variants": sorted(e["variants"]),
            "roles": {r: sorted(v) for r, v in e["roles"].items() if v},
            "facilities": sorted(facs),
            "reach": len(facs),
        })
    return sorted(out, key=lambda e: (-e["reach"], e["name"].lower()))


def grouped(entities: list[dict], groups: dict) -> list[dict]:
    """The curated parent layer. Every member is named explicitly in config, never inferred."""
    by_key = {e["key"]: e for e in entities}
    out = []
    for g in groups.get("groups") or []:
        members = [by_key[normalise(m)] for m in g.get("members", []) if normalise(m) in by_key]
        if not members:
            continue
        facs = set()
        roles = defaultdict(set)
        for m in members:
            facs |= set(m["facilities"])
            for r, v in m["roles"].items():
                roles[r] |= set(v)
        out.append({
            "name": g["name"], "slug": slug(g["name"]), "note": g.get("note", ""),
            "members": [m["name"] for m in members],
            "roles": {r: sorted(v) for r, v in roles.items()},
            "facilities": sorted(facs), "reach": len(facs),
        })
    return sorted(out, key=lambda g: (-g["reach"], g["name"].lower()))


def split_by_punctuation(entities: list[dict]) -> list[dict]:
    """Entities the state filed under more than one spelling. The finding this module exists for."""
    return [e for e in entities if len(e["variants"]) > 1]


def load() -> dict:
    if not REGISTRY.exists():
        return {"entities": [], "groups": [], "facilities": []}
    facs = json.loads(REGISTRY.read_text(encoding="utf-8")).get("facilities") or []
    ents = resolve(facs)
    return {"entities": ents, "groups": grouped(ents, load_groups()), "facilities": facs}


def problems(data: dict) -> list[str]:
    out = []
    seen = {}
    for e in data["entities"]:
        if e["slug"] in seen and seen[e["slug"]] != e["key"]:
            out.append(f"entity slug {e['slug']!r} is claimed by two different entities")
        seen[e["slug"]] = e["key"]
        if not e["facilities"]:
            out.append(f"entity {e['name']!r} resolved to no facility")
    gs = {}
    for g in data["groups"]:
        if g["slug"] in gs:
            out.append(f"group slug {g['slug']!r} is used twice")
        gs[g["slug"]] = True
        if not g.get("note"):
            out.append(f"group {g['name']!r} states no reason for grouping its members")
    # A group slug that collides with an entity slug would make two different pages fight for
    # one url, and the loser would be whichever the build wrote second.
    for g in data["groups"]:
        if g["slug"] in seen:
            out.append(f"group {g['name']!r} takes the slug of entity {g['slug']!r}")
    return out


# ---------------------------------------------------------------- rendering
MIN_REACH = 2   # A company on one facility says nothing its facility page does not already say.


def e(t) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def n0(v) -> str:
    return f"{int(v):,}"


def ordinal_date(iso: str) -> str:
    """The house date for a registry effective date."""
    y, m, d = (int(x) for x in str(iso).split("-"))
    suffix = "th" if 11 <= d <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(d % 10, "th")
    return f"{MONTHS[m - 1]} {d}{suffix}, {y}"


def published(data: dict) -> tuple[list, list]:
    """Who gets a page. Entities on more than one facility, and every curated group.

    A single facility entity is left off deliberately. Its page would repeat the facility page
    and add a thin url to the sitemap, which is the opposite of what more pages are for.
    """
    ents = [x for x in data["entities"] if x["reach"] >= MIN_REACH]
    return ents, list(data["groups"])


def _facility_list(names, dossiers, facilities) -> str:
    out = []
    for n in sorted(names):
        d = dossiers.get(n)
        eff = (facilities.get(n) or {}).get("effective", "")
        label = (f'<a href="../../facility/{e(d["slug"])}/"><cite>{e(n)}</cite></a>'
                 if d else f"<cite>{e(n)}</cite>")
        when = f' <time datetime="{e(eff)}" class="cwhen">{e(eff)}</time>' if eff else ""
        out.append(f"<li>{label}{when}</li>")
    return "".join(out)


def relationships(item: dict, data: dict, *, is_group: bool = False) -> list[dict]:
    """Other repeat entities that share at least one certified facility with ``item``.

    This is the prose answer to what a line on the registry field means. Parent groups are not
    nodes in that field and therefore do not acquire relationships from their members here.
    """
    if is_group:
        return []
    target = set(item.get("facilities") or [])
    out = []
    for other in data.get("entities") or []:
        if other.get("key") == item.get("key") or other.get("reach", 0) < MIN_REACH:
            continue
        shared = sorted(target & set(other.get("facilities") or []))
        if shared:
            out.append({"name": other["name"], "slug": other["slug"], "shared": shared})
    return sorted(out, key=lambda row: (-len(row["shared"]), row["name"].lower()))


def panel(item: dict, data: dict, dossiers: dict, *, is_group: bool) -> str:
    """One company, each facility once, and the certified rows behind its graph lines."""
    facilities = {f["name"]: f for f in data["facilities"]}

    by_facility: dict[str, list[str]] = defaultdict(list)
    for role in ("owner", "occupant", "operator"):
        for name in item["roles"].get(role) or []:
            by_facility[name].append(role)

    def facility_link(name: str) -> str:
        dossier = dossiers.get(name)
        return (f'<a href="../../facility/{e(dossier["slug"])}/"><cite>{e(name)}</cite></a>'
                if dossier else f'<cite>{e(name)}</cite>')

    facility_rows = []
    order = sorted(by_facility, key=lambda name: (
        (facilities.get(name) or {}).get("effective", ""), name.lower()), reverse=True)
    for name in order:
        effective = (facilities.get(name) or {}).get("effective", "")
        when = (f'<time datetime="{e(effective)}" class="cwhen">'
                f'{e(ordinal_date(effective))}</time>' if effective else "")
        role_chips = "".join(
            f'<span class="cfacrole">{e(role.title())}</span>'
            for role in ("owner", "occupant", "operator") if role in by_facility[name])
        facility_rows.append(
            f'<li class="cfac"><div class="cfacmain">{facility_link(name)}{when}</div>'
            f'<div class="cfacroles">{role_chips}</div></li>')

    stat_rows = [("Certified facilities", item["reach"])] + [
        (f'{role.title()} of record', len(item["roles"].get(role) or []))
        for role in ("owner", "occupant", "operator")]
    stats = "".join(
        f'<span class="cstat"><strong class="num">{n0(value)}</strong>'
        f'<small>{e(label)}</small></span>' for label, value in stat_rows)

    if is_group:
        head = (f'<div class="cidentity"><p class="csum">A curated grouping of '
                f'<strong class="num">{n0(len(item["members"]))}</strong> entities that file '
                f'separately in the registry. {e(item["note"])}</p>'
                f'<details class="fold"><summary>Entities in this parent grouping</summary>'
                f'<ul class="cvars" data-prose="data">'
                + "".join(f"<li><cite>{e(m)}</cite></li>" for m in sorted(item["members"]))
                + "</ul></details></div>")
    else:
        v = item["variants"]
        head = ""
        if len(v) > 1:
            head = (f'<div class="cidentity"><p class="csum">The state filed this company under '
                    f'<strong class="num">{n0(len(v))}</strong> different spellings. They differ '
                    f'only by punctuation or capitalisation, so they are counted as one here.</p>'
                    f'<details class="fold"><summary>State spelling variants</summary>'
                    f'<ul class="cvars" data-prose="data">'
                    + "".join(f"<li><cite>{e(x)}</cite></li>" for x in v)
                    + "</ul></details></div>")

    relation_rows = []
    for relation in relationships(item, data, is_group=is_group):
        shared = "".join(
            f'<li>{facility_link(name)}</li>' for name in relation["shared"][:3])
        more = len(relation["shared"]) - min(3, len(relation["shared"]))
        if more:
            shared += f'<li class="crelmore">{n0(more)} more</li>'
        noun = "facility record" if len(relation["shared"]) == 1 else "facility records"
        relation_rows.append(
            f'<article class="crelation"><h3><a href="../{e(relation["slug"])}/">'
            f'<cite>{e(relation["name"])}</cite></a></h3>'
            f'<p><strong class="num">{n0(len(relation["shared"]))}</strong> shared {noun}.</p>'
            f'<ul data-prose="data">{shared}</ul></article>')

    relations = ""
    if not is_group:
        relations = (
            f'<section class="crelations"><h2>Why this company has lines</h2>'
            f'<p>A line on the relationship field means two repeat companies appear on the '
            f'same certified facility row. It is a registry relationship. It is not a claim '
            f'about ownership between the companies.</p>'
            + (f'<div class="crelationgrid">{"".join(relation_rows)}</div>' if relation_rows
               else '<p class="cempty">This company repeats across the registry without '
                    'sharing a row with another company that also repeats.</p>')
            + '</section>')

    return (f'<div class="company"><div class="cstats" data-prose="data">{stats}</div>{head}'
            f'<section class="cportfolio"><h2>Every certified facility</h2>'
            f'<p>Each facility appears once. The badges show every role this company holds on '
            f'that row.</p><ul class="cfacs" data-prose="data">'
            f'{"".join(facility_rows)}</ul></section>{relations}</div>')


def authorised(data: dict) -> set:
    """Every numeral a company page may show, from the same calls that render them."""
    out = set()
    ents, groups = published(data)
    for item in ents + groups:
        out.add(n0(item["reach"]))
        for role in ("owner", "occupant", "operator"):
            out.add(n0(len(item["roles"].get(role) or [])))
        if "members" in item:
            out.add(n0(len(item["members"])))
        if "variants" in item:
            out.add(n0(len(item["variants"])))
        for relation in relationships(item, data, is_group="members" in item):
            shared = len(relation["shared"])
            out.add(n0(shared))
            if shared > 3:
                out.add(n0(shared - 3))
    for f in data["facilities"]:
        if f.get("effective"):
            out.add(str(f["effective"]))
            out.add(ordinal_date(f["effective"]))
    for v in (len(ents), len(groups), len(data["entities"]), len(data["facilities"]),
              len(split_by_punctuation(data["entities"])),
              sum(1 for x in data["entities"] if x["reach"] > 1)):
        out.add(n0(v))

    # A COMPANY NAME IS THE STATE'S STRING, and some carry digits. `1102 McKinzie LLC` is a
    # street number somebody filed as a company name. Same narrow class as the facility names
    # in facility_dossier.authorised: transcribed identifiers, never arithmetic, and every
    # computed figure on the page is authorised above by the call that renders it.
    for item in ents + groups:
        out |= set(_NUMERAL.findall(item["name"]))
        for v in item.get("variants", []):
            out |= set(_NUMERAL.findall(v))
        for m in item.get("members", []):
            out |= set(_NUMERAL.findall(m))
        for names in item["roles"].values():
            for n in names:
                out |= set(_NUMERAL.findall(n))
    return out


def self_test() -> int:
    checks = []

    def ok(name, cond, extra=""):
        checks.append(bool(cond))
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}{'' if cond else '  ' + str(extra)}")

    # THE DEFECT THIS EXISTS FOR.
    ok("a comma alone does not make two companies",
       normalise("Oracle America Cloud Services LLC") == normalise("Oracle America Cloud Services, LLC"))
    ok("nor does case", normalise("GOOGLE LLC") == normalise("Google, LLC"))
    ok("nor does a stray period",
       normalise("Coreweave Compute Acquisition Co. II. LLC")
       == normalise("Coreweave Compute Acquisition Co. II, LLC"))
    ok("nor does a comma inside the name", normalise("Whinstone, US, Inc.") == normalise("Whinstone US Inc."))

    # AND THE LINE IT MUST NOT CROSS.
    ok("different legal entities of one parent stay apart",
       normalise("Oracle America Cloud Services, LLC") != normalise("Oracle America, Inc."))
    ok("...and so do sibling subsidiaries",
       normalise("Riot Platforms, Inc.") != normalise("Riot Data Centers, LLC"))
    ok("...and two unrelated companies never merge",
       normalise("Lancium Abilene, LLC") != normalise("Lancium, LLC"))

    facs = [
        {"name": "A", "owners": ["Oracle America Cloud Services LLC"], "occupants": [], "operators": []},
        {"name": "B", "owners": ["Oracle America Cloud Services, LLC"], "occupants": [], "operators": []},
        {"name": "C", "owners": [], "occupants": ["Google, LLC"], "operators": ["GOOGLE LLC"]},
    ]
    ents = resolve(facs)
    oracle = [e for e in ents if "oracle" in e["key"]][0]
    ok("one entity across two spellings", oracle["reach"] == 2, oracle["reach"])
    ok("...and both spellings are kept", len(oracle["variants"]) == 2, oracle["variants"])
    google = [e for e in ents if "google" in e["key"]][0]
    ok("one facility counted once across two roles", google["reach"] == 1, google["reach"])
    ok("...while both roles are recorded", set(google["roles"]) == {"occupant", "operator"},
       sorted(google["roles"]))

    # The display name is the state's, not ours.
    many = resolve([{"name": str(i), "owners": ["Design, LLC"], "occupants": [], "operators": []}
                    for i in range(3)]
                   + [{"name": "z", "owners": ["Design LLC"], "occupants": [], "operators": []}])
    ok("the most used spelling is the one published", many[0]["name"] == "Design, LLC", many[0]["name"])

    # The C fixture spells Google two ways across its two roles, so a single spelling case
    # needs its own fixture. Getting this wrong the first time is what the check is for.
    one = resolve([{"name": "s", "owners": ["Solo LLC"], "occupants": ["Solo LLC"],
                    "operators": []}])
    ok("an entity spelled one way is not reported as split",
       split_by_punctuation(one) == [], [e["variants"] for e in one])
    ok("every entity spelled more than one way is reported",
       len(split_by_punctuation(ents)) == 2, [e["variants"] for e in split_by_punctuation(ents)])

    # The gate.
    bad = {"entities": [{"key": "a", "name": "A", "slug": "x", "variants": ["A"], "roles": {},
                         "facilities": []}], "groups": []}
    ok("an entity resolving to no facility fails", problems(bad))
    dupe = {"entities": [{"key": "a", "name": "A", "slug": "x", "variants": [], "roles": {},
                          "facilities": ["f"]}],
            "groups": [{"name": "G", "slug": "x", "note": "n", "members": [], "roles": {},
                        "facilities": ["f"], "reach": 1}]}
    ok("a group taking an entity's url fails", problems(dupe))
    nonote = {"entities": [], "groups": [{"name": "G", "slug": "g", "note": "", "members": [],
                                          "roles": {}, "facilities": [], "reach": 0}]}
    ok("a group with no stated reason fails", problems(nonote))

    passed = sum(checks)
    print(f"\nentities self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    data = load()
    bad = problems(data)
    if bad:
        print(f"entities: {len(bad)} problem(s)")
        for b in bad:
            print(f"  {b}")
        return 1
    ents, groups = data["entities"], data["groups"]
    split = split_by_punctuation(ents)
    print(f"entities: {len(ents)} resolved from the registry, "
          f"{sum(1 for e in ents if e['reach'] > 1)} on more than one facility")
    print(f"          {len(split)} filed under more than one spelling")
    print(f"          {len(groups)} curated parent group(s)")
    for e in ents[:8]:
        r = " ".join(f"{k}:{len(v)}" for k, v in sorted(e["roles"].items()))
        print(f"   {e['reach']:>3}  {e['name'][:46]:<46} {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
