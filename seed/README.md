# Docket seed — candidates, not the record

`docket_seed.json` holds candidate work. **`ledger/docket.json` is the published record.** The
ingest command writes here by default and refuses the live ledger as an output:

```
python3 scripts/site/docket_ingest.py --batch out/research/*.json --today <today>
python3 scripts/site/docket_build.py --promote seed/docket_seed.json --today <today>
```

**The second command is the admission AND the write.** It reads the published ledger, ignores
historical seed rows whose ids are already published, gates every seed-only candidate, appends
only the new rows that clear the bar, then validates the entire combined record. Only after all
of that passes does it replace `ledger/docket.json` atomically. It never writes this seed.

There is no manual append and promotion has no `--out` mode. `--ledger <path>` exists so a test
or maintainer can exercise the same merge against an explicit record; omitting it uses the live
ledger. A published id is immutable here even when its historical seed copy differs. Rerunning
the command with nothing new is byte-identical, and any refused validation leaves both files
byte-identical.

Read the `HELD` rows. Every admitted row has already been written by the time the command returns:
every gate passes, confidence is high, and at least one claim cites a primary source rather than
journalism. The record is append-only in substance and an existing item is never replaced by a
seed copy.

**A held item is not lost.** It stays here with its reason, and a later run that finds the
primary source promotes it without anyone intervening. Nothing here waits on a person, which is
why the reasons are written for a machine to re-test rather than for someone to adjudicate.

## What is in it now

This is working state, so its counts are read from the JSON rather than copied into this file. The
same check also separates historical candidate copies from ids that exist only in the seed:

```bash
python3 - <<'PY'
import json
seed = json.load(open("seed/docket_seed.json"))
published = {item["id"] for item in json.load(open("ledger/docket.json"))["items"]}
seed_ids = {item["id"] for item in seed}
print(f"{len(seed)} rows, {sum(len(item['claims']) for item in seed)} claims")
print(f"{len(seed_ids & published)} already published, {len(seed_ids - published)} seed only")
PY
```

Rows whose ids already exist in the published ledger are historical candidate copies. Promotion
recognizes and preserves them here while always keeping the published version. Seed-only ids
remain candidates.

Every claim carries a **verbatim quote** and a URL that was actually fetched, because the
compute-not-generate law means no number may be stated in a model's own words. Low-confidence and
journalism-only items remain held until their own `notes_for_editor` gaps are resolved. Item 0023
names private individuals as defendants and remains held until the complaints are read. The
contested SB 6 4CP deadline in item 0005 must not be published; its correction is recorded in
`knowledge/shared/TEXAS_GOVERNMENT.md`.

## Two findings worth keeping whatever happens to the rest

**Item 0008.** Three separate acts of the 89th Legislature each added a **Subchapter S** to
Government Code Chapter 2054, and two number their sections identically. **Section 2054.702 exists
twice with entirely different commands.** The codifier flagged the conflict rather than resolving
it, so which text governs a state agency's AI duties is unsettled on the face of the statute. Found
by reading the code, and apparently reported nowhere.

**Item 0009.** **The AI regulatory sandbox for public entities is Government Code 2054.706, added
by SB 1964, effective September 1st, 2025 — four months before TRAIGA.** It is widely attributed to
TRAIGA and that attribution is wrong. (TRAIGA has its own separate sandbox for private-sector
participants at B&C Chapter 553. Two sandboxes, and conflating them is an error.)

## Provenance note

The build was mid-flight when three robots.txt exclusions were discovered. `gov.texas.gov` and
`capitol.texas.gov/BillLookup/` had already been fetched. **Fetching stopped immediately and every
claim citing either host was removed.** SB 6 was re-sourced entirely to the enacted text at
`tcss.legis.texas.gov`, which is the better primary source anyway.
