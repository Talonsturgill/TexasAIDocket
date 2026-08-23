#!/usr/bin/env python3
"""schema_contract.py — the record shape cannot change without saying so.

WHY THIS EXISTS

`ledger/docket.json` is the record every other module here reads. Ten of them parse it: the
site build, the docket build, the calendar, the map, the staleness gate and the four ask
builders among them. A field quietly renamed or retyped in the ledger breaks all of them, and
it breaks them at different depths and at different times.

**A version nothing is obliged to move is not a weak promise, it is a false one.** A reader of
the shape who pins to `version: 1` and meets a silently reshaped file is worse off than one who
knew there was no guarantee, because the number talked them out of checking.

So this computes the shape the ledger actually carries and compares it against a committed
contract, and it fails when the shape moved in a way that breaks a parser and the version did
not rise to say so.

IT CHECKED THE PUBLISHED FILE UNTIL 2026-08-23. `docs/docket.json` was the whole record as one
CC BY download, and this contract existed for the strangers parsing it. That file is no longer
published, on the owner's call: the docket is the most expensive thing this project makes and
one parseable fetch handed over all of it. The contract survives the download because its real
subject was never the strangers. It was the ten modules here that would break in ten different
ways, and they still read the same file.

THE RULE, WHICH LIVES WITH THE CONSTANT IT GOVERNS in `docket_build.SPEC_VERSION`:

  BREAKING, the version must rise
    a required field removed, or no longer required
    any field's type changed
    a value removed from a published vocabulary

  NOT BREAKING, the version stays
    a new field added anywhere
    a value ADDED to a vocabulary. A consumer switching on what it knows still works and
    simply meets a value it does not. Bumping for every new beat makes the number rise often
    enough that nobody reads it, which costs more than it buys. (Owner's call, 2026-08-20.)

WHERE "REQUIRED" COMES FROM, and this is the part that is easy to get circular. Not from what
today's items happen to contain: a genuinely optional field that every current item carries
would look required, and the day one item omits it the gate would cry about a break that never
happened. It comes from `docket_build.REQUIRED_FIELDS`, which is the same tuple the validator
enforces, so the contract describes the PROMISE rather than the sample.

THE CONTRACT FILE IS OWNED BY `human`, deliberately. A routine adds items, never fields, so
this will not block a run. When the shape really does change it is a change to a public
contract, and a person deciding whether it breaks anybody is exactly the friction that should
be there.

    schema_contract.py                 # check the ledger against config/schema_contract.json
    schema_contract.py --update        # rewrite the contract from the current record
    schema_contract.py --self-test
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docket_build as dk                                            # noqa: E402

CONTRACT = REPO_ROOT / "config" / "schema_contract.json"
# The record itself, which is what the shape is a contract over. This read the BUILT file until
# the record stopped being published as one, and reading the ledger is what it should always
# have done: a contract over the source cannot be dodged by a build that never ran.
LEDGER_PATH = REPO_ROOT / "ledger" / "docket.json"
DOCS = REPO_ROOT / "docs"

# The published vocabularies, by the name they are checked under. Removing a value from any of
# these breaks a consumer that has a branch per value.
VOCABULARIES = {
    "topic": lambda: sorted(dk.TOPICS),
    "status": lambda: sorted(dk.STATUSES),
    "public_access.room": lambda: sorted(dk.ROOMS),
}


def kind(v) -> str:
    """The type a consumer's parser sees. `null` is its own thing, since a field that is
    sometimes null is not the same promise as one that never is."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "bool"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, list):
        return "array"
    return "object"


def shape_of(items: list) -> dict:
    """Field path -> the sorted set of types seen at it, one level into nested objects.

    ONE LEVEL AND NOT ARBITRARY DEPTH. `claims` and `key_dates` are arrays of objects whose
    own fields matter, so those are walked. Going deeper would make the contract a transcript
    of the data rather than a description of its shape.
    """
    seen: dict[str, set] = {}

    def note(path, value):
        seen.setdefault(path, set()).add(kind(value))

    for it in items:
        for k, v in it.items():
            note(k, v)
            if isinstance(v, dict):
                for k2, v2 in v.items():
                    note(f"{k}.{k2}", v2)
            elif isinstance(v, list) and v and isinstance(v[0], dict):
                for row in v:
                    for k2, v2 in row.items():
                        note(f"{k}[].{k2}", v2)
    return {k: sorted(v) for k, v in sorted(seen.items())}


def contract_now() -> dict:
    """The contract the record currently carries."""
    published = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    return {
        "version": published["_spec"]["version"],
        "required": list(dk.REQUIRED_FIELDS),
        "fields": shape_of(published["items"]),
        "vocabularies": {name: fn() for name, fn in VOCABULARIES.items()},
    }


def compare(old: dict, new: dict) -> tuple[list[str], list[str]]:
    """`(breaking, additive)`. Pure, so the self-test can drive it without a built site."""
    breaking, additive = [], []

    gone = set(old.get("required", [])) - set(new.get("required", []))
    for f in sorted(gone):
        breaking.append(f"required field '{f}' is no longer required")

    o, n = old.get("fields", {}), new.get("fields", {})
    for f in sorted(set(o) - set(n)):
        breaking.append(f"field '{f}' is no longer published")
    for f in sorted(set(n) - set(o)):
        additive.append(f"field '{f}' is new")
    for f in sorted(set(o) & set(n)):
        if o[f] != n[f]:
            # A field that GAINS a type is a break too: a consumer that always got a string
            # and now sometimes gets null has a crash waiting for it.
            breaking.append(f"field '{f}' changed type, {'/'.join(o[f])} to {'/'.join(n[f])}")

    ov, nv = old.get("vocabularies", {}), new.get("vocabularies", {})
    for name in sorted(set(ov) | set(nv)):
        was, now = set(ov.get(name, [])), set(nv.get(name, []))
        for v in sorted(was - now):
            breaking.append(f"{name} no longer allows '{v}'")
        for v in sorted(now - was):
            additive.append(f"{name} allows '{v}', which is additive and does not bump")
    return breaking, additive


def report() -> int:
    if not CONTRACT.exists():
        print(f"schema_contract: no contract at {CONTRACT}. Run --update to write the first "
              "one, and read it before you commit it.", file=sys.stderr)
        return 2
    old = json.loads(CONTRACT.read_text(encoding="utf-8"))
    new = contract_now()
    breaking, additive = compare(old, new)

    for line in additive:
        print(f"  note: {line}")
    if breaking and new["version"] <= old["version"]:
        for line in breaking:
            print(f"  BREAKING: {line}", file=sys.stderr)
        print(f"schema_contract: the record shape broke and _spec.version is still "
              f"{new['version']}. Raise docket_build.SPEC_VERSION, then --update.",
              file=sys.stderr)
        return 1
    if breaking:
        print(f"schema_contract: {len(breaking)} breaking change(s), and the version rose to "
              f"{new['version']} to say so. Run --update to record the new shape.")
        return 1
    if additive or old != new:
        print("schema_contract: the shape grew and nothing broke. Run --update to record it.")
        return 1
    print(f"schema_contract: the record shape matches the contract at version "
          f"{new['version']}, {len(new['fields'])} field(s)")
    return 0


def update() -> int:
    CONTRACT.parent.mkdir(parents=True, exist_ok=True)
    CONTRACT.write_text(json.dumps(contract_now(), indent=2) + "\n", encoding="utf-8")
    print(f"schema_contract: wrote {CONTRACT.relative_to(REPO_ROOT)}")
    return 0


def self_test() -> int:
    failures = 0

    def check(label, cond, got=""):
        nonlocal failures
        print(("  ok   " if cond else "  FAIL ") + label + ("" if cond else f"  ({got})"))
        if not cond:
            failures += 1

    base = {"version": 1, "required": ["id", "title"],
            "fields": {"id": ["string"], "title": ["string"], "note": ["string"]},
            "vocabularies": {"topic": ["grid", "water"]}}

    def variant(**kw):
        out = json.loads(json.dumps(base))
        out.update(kw)
        return out

    print("an unchanged shape is unchanged")
    b, a = compare(base, json.loads(json.dumps(base)))
    check("nothing breaking", b == [], str(b))
    check("nothing additive", a == [], str(a))

    print("\nand every breaking change is caught")
    b, _ = compare(base, variant(fields={"id": ["string"], "title": ["string"]}))
    check("a field stops being published", any("no longer published" in x for x in b), str(b))
    b, _ = compare(base, variant(required=["id"]))
    check("a required field stops being required",
          any("no longer required" in x for x in b), str(b))
    b, _ = compare(base, variant(fields={**base["fields"], "id": ["number"]}))
    check("a field changes type", any("changed type" in x for x in b), str(b))
    b, _ = compare(base, variant(fields={**base["fields"], "id": ["null", "string"]}))
    check("a field starts sometimes being null",
          any("changed type" in x for x in b), str(b))
    b, _ = compare(base, variant(vocabularies={"topic": ["grid"]}))
    check("a vocabulary loses a value", any("no longer allows" in x for x in b), str(b))

    print("\nand additive change is called additive, which is the owner's rule")
    b, a = compare(base, variant(fields={**base["fields"], "extra": ["string"]}))
    check("a new field does not break", b == [], str(b))
    check("...and is reported", any("is new" in x for x in a), str(a))
    b, a = compare(base, variant(vocabularies={"topic": ["grid", "water", "chips"]}))
    check("a new topic does not break", b == [], str(b))
    check("...and is reported", any("does not bump" in x for x in a), str(a))

    print("\nrequired comes from the validator, never from what the data happens to hold")
    check("the contract's required list is the validator's tuple",
          tuple(contract_now()["required"]) == dk.REQUIRED_FIELDS)
    check("and every required field is really published",
          all(f in contract_now()["fields"] for f in dk.REQUIRED_FIELDS),
          str([f for f in dk.REQUIRED_FIELDS if f not in contract_now()["fields"]]))

    print("\nthe real build agrees with the committed contract")
    if CONTRACT.exists():
        b, a = compare(json.loads(CONTRACT.read_text()), contract_now())
        check("no drift between them", not b and not a, str(b + a))
    else:
        check("a contract exists to compare against", False, "run --update")

    print("\nschema_contract self-test: " + ("all passed" if not failures
                                             else f"{failures} FAILED"))
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    return update() if a.update else report()


if __name__ == "__main__":
    raise SystemExit(main())
