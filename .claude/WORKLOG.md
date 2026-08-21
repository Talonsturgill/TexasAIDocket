# WORKLOG — the registry becomes a dossier

Opened 2026-08-21 on the owner's call. The grid page lists 151 certified data centers with five
fields each. Wanted: click a facility, get "every single piece of information that exists about
that data center", researched one by one. Explicitly NOT a blanket pass: "this is really gonna be
where we earn our keep as a data company". Ten or so per session, bespoke each time.

**Read this first.** Resume from the task table at the bottom. Read
`knowledge/shared/DATACENTER_REGISTRY.md` before researching anything.

## What the data is, measured before designing

    151 facilities, 5 fields each: name, effective, owners, occupants, operators
    owners present on 147 of 151, the other three fields on all 151
    85 of 151 name a major operator (Amazon, Google, Oracle, Anthropic, Lambda, Riot, Cipher...)

The registry is a TAX record from the Comptroller, under Tax Code 151.359 and 151.3595. Owner,
occupant and operator are statutory roles in an exemption filing, not job descriptions. The whole
doctrine is in `knowledge/shared/DATACENTER_REGISTRY.md` and it is not optional reading.

## Three findings from batch 1 that a blanket pass would never have produced

- **Anthropic, PBC is the certified occupant of TWO facilities**, Fluidstack Abernathy
  (owner FS AB LLC) and Cipher Barber Lake (operator Fluidstack USA II INC.).
- **LBB01 is named for Lubbock and owned by ALIGNED DATA CENTERS (ABERNATHY) PROPCO, LLC.** So
  Abernathy holds two unrelated data centers, an Aligned building with Lambda as occupant and the
  Fluidstack building with Anthropic as occupant. Nothing in the registry says they are different
  and nothing says they are the same.
- **TeraWulf's July 2026 release contradicts the state record**, placing the Anthropic lease at a
  different campus and describing Abernathy as sold to Fluidstack. Both are true about different
  things. The dossier carries both and adjudicates neither.

## The design

**A DOSSIER IS DATA, NOT PROSE.** This is what makes it legal to publish under the
compute-not-generate law. Every number lives in a `facts[]` entry as a real value with a unit and
a source id, and the page renders it through the same formatting call that authorises it for
`numeral_lint`. Prose lives in `notes[]` and **may not contain a numeral at all**, which the gate
enforces. A note says Google backstops the lease obligations. The 1.4 billion is a fact field.

**Every fact carries a source id** resolving to a `sources[]` entry with url, publisher, retrieved
date and kind. No source, no publish. Same rule the docket already runs on.

**Gaps are published.** `gaps[]` names what is not public for this facility. A dossier with four
facts and six gaps is honest and useful. One with four facts and silence is neither.

**A page AND a modal, not a modal alone.** The owner asked for a popup and a popup is right for
reading in place. But a modal is invisible to search, and 151 indexable pages each about a named
Texas data center is the single largest discoverability asset this project could hold. So each
facility gets a real page at `/facility/<slug>/` in the sitemap and `llms.txt`, and the registry
row opens the same content in a dialog with a link through. Progressive enhancement, same as the
calendar: with script off the row is a plain link to the page.

## The rules this has to hold

- Numerals computed, never typed. `numeral_lint` is a hard build gate.
- Every fact traces to a fetched source, with the retrieved date.
- `docs/` is generated. `site_fresh_check` proves byte equality.
- The dossier ledger is owned by `human` in `ownership.yaml`. **No routine may rewrite researched
  facts**, and the daily run must not be able to touch this file.
- Registry strings are published faithfully, data-entry noise included.
- House voice: no em dash, no colon or semicolon in published copy, straight quotes, "can't",
  dates as "August 21st".
- CSP hashes inline scripts, so the dialog script goes through `csp.apply`.
- Responsive, contrast gated, nothing overflows sideways.

## Tasks

| # | task | state |
| --- | --- | --- |
| A | Measure the registry, find its source, read the collector | DONE |
| B | `knowledge/shared/DATACENTER_REGISTRY.md`, the program's real semantics | DONE |
| C | This worklog | DONE |
| D | Research batch 1, ten marquee AI facilities | DONE, 10 of 10, 77 sourced facts |
| E | Dossier schema + `ledger/facilities/dossiers.json` | DONE |
| F | `facility_dossier.py` gate, 24 self-tests | DONE |
| G | Per-facility page at `/facility/<slug>/`, in the sitemap | DONE |
| H | The dialog on the registry row, progressive enhancement | DONE |
| I | `tests/facility_dossier.mjs`, 17 checks | DONE |
| J | Full sweep, `guards_local.py`, ship | IN PROGRESS |

## Wrap

W1. Delete this file when every task is DONE and all 151 have dossiers, or when the owner calls
    the project finished. Batches after the first resume at task D with a new ten.

## Batch 1, the ten

Fluidstack Abernathy (Anthropic) · Cipher Barber Lake (Anthropic) · Lancium Abilene Clean Campus II
(Oracle, Stargate) · LBB01 (Lambda, Aligned) · Meitner (Google) · Stingray (Amazon, Cipher) ·
Cipher Black Pearl (Amazon) · Riot Rockdale 1 · Riot Corsicana I · ECX AUS31-36 (EdgeConnex)

Chosen by signal rather than alphabetically. These are the rows a reader actually clicks, and they
are the ones with enough public record to prove the format works before it meets a small colo site
with almost nothing findable.

## Batch 2 starts here

The next ten. Pick by signal again rather than alphabetically, and read
`knowledge/shared/DATACENTER_REGISTRY.md` first, particularly the re-certification section,
which was the best finding of batch 1 and was not in the plan.

Candidates, all named in the registry with a major occupant and none researched yet:
Flamingo, Pecos Ranch, Bexar 1, Spectrum, Gulf Horizon and C1 Bosque I and II (all Amazon or
Google), DFW-04 (Lambda), TX11-12 (Oracle), Riot Rockdale 2 and Corsicana 02, and
Cedarvale/Pyote, which holds a re-certification showing Ionic Digital handing off to Nscale and
so is worth doing early while that pattern is fresh.

ECX AUS31-36 shipped deliberately thin and is the standing example of an honest sparse dossier.
It is also the first candidate for a second pass if better sourcing turns up.
