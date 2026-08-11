# Docket seed — candidates, not the record

`docket_seed.json` holds candidate items. **`ledger/docket.json` is the published record.** An
item moves from here to there only by passing every gate in `scripts/site/docket_build.py`:

```
python3 scripts/site/docket_build.py --promote seed/docket_seed.json --out ledger/docket.json
```

**Promotion is automatic and the gates are the reviewer.** The admission bar is deliberately
stricter than the gates alone: every gate passes, confidence is high, and at least one claim
cites a primary source rather than journalism.

**A held item is not lost.** It stays here with its reason, and a later run that finds the
primary source promotes it without anyone intervening. Nothing here waits on a person, which is
why the reasons are written for a machine to re-test rather than for someone to adjudicate.

Of the first 27 candidates, **13 were admitted.** The rest were held on confidence bands, a
missing close date on an open comment window, or geography that named no place.

## What is in it

27 items, 94 claims. **77 claims cite a primary official source, 17 cite journalism.** Confidence:
**15 high, 5 medium, 7 low.**

| | |
|---|---|
| Topics | power-and-the-grid 8, state-policy 8, data-centers 6, defense-and-federal 3, research-and-science 1, surveillance-and-policing 1 |
| Status | open 10, pending 8, decided 6, unknown 3 |
| Public access | contact_only 11, open_comment 8, open_meeting 7, closed 1 |

Every claim carries a **verbatim quote** and a URL that was actually fetched, because the
compute-not-generate law means no number may be stated in a model's own words.

**Still-actionable comment windows at build time:** PUCT 58482 (September 4th), an NRC docket
(August 31st), BLS ATUS and DOE (September 8th).

## Before any of this ships

1. **Items 0018 through 0022 and 0027 rest on headlines alone.** Re-source or drop.
2. **Item 0023 names private individuals as defendants.** **Hold until the complaints are read.**
3. The seven low-confidence items each say what is missing in `notes_for_editor`. Read those first.
4. **Do not publish SB 6's December 31st, 2026 4CP deadline.** It is contested and is flagged
   inside item 0005. See the correction block in `knowledge/shared/TEXAS_GOVERNMENT.md`.

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
