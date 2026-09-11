# Handoff — carousel no. 21, planned and half built

**THIS WAS WRITTEN TO `prompts/NEXT_RUN.md` FIRST AND THE OWNERSHIP MAP REFUSED IT.** That path
is `human` lane. The daily routine's own Phase 0 says to read a story "queued by the previous
run" from it, and `ownership.yaml` does not let a run write it. The branch may stamp `human`
through `branch_also_allows`, and that grant is for a defect this run caused or is blocked by,
which queuing a story is not. So the handoff lives here instead, in the run record, which is
`daily` lane and is where a proposal belongs. **The contradiction is logged as an upgrade
proposal in `RUN_RECORD.md`.**

**The 2026-09-11 run shipped the record in full and did NOT ship a deck.** It stopped on the
degradation ladder's rung (d) with the deck planned, claimed, computed, captioned and four frames
built. Everything below is committed under `runs/carousel/2026-09-11/`. **Do not re-plan it. Pick
it up.**

## The story

`tx-2026-0142`. The Texas State Board of Education took new 19 TAC Section 113.26, Applied
Personal Financial Literacy (One-Half Credit), to second reading and final adoption on an item
dated September 4th, 2026. The text that item publishes as its one attachment carries a machine in
three separate chapters of a money class, and the board's own news release about the meeting names
no technology at all.

- `(d)(3)(C)` USE IT. "research career pathways using labor-market data, online resources, and artificial intelligence tools"
- `(d)(4)(C)` EXPLAIN IT. "explain how consumerism and marketing strategies, including social media influencers, algorithm-driven recommendations, financial technology platforms, and traditional advertising, influence spending behavior and financial decision-making"
- `(d)(7)(J)` APPRAISE IT. "appraise responsible use of financial technology through automated investment platforms, including robot-advisors and micro-investing apps, by analyzing fee structures, investment strategies, algorithmic limitations, and suitability for different investor profiles"

**It is not an elective.** The item's statutory authority section says the statute "requires the
State Board of Education (SBOE) to establish curriculum and graduation requirements" and names
"the curriculum requirement for a one-half credit in personal financial literacy".

## What is already done and must not be redone

| artifact | where | state |
|---|---|---|
| claims, 24 verified, 6 rejected | `runs/carousel/2026-09-11/claims.json` | `claims_check` clean, provision sweep over 3 snapshots, 0 findings |
| source snapshots | `runs/carousel/2026-09-11/sources/` | the served bytes of all three documents |
| storyboard and nine dossiers | `runs/carousel/2026-09-11/storyboard.md` | `dossier_check` clean |
| compute.py and computed.json | `runs/carousel/2026-09-11/` | every count derived from the snapshots, no numeral typed |
| palette, measured | `runs/carousel/2026-09-11/palette_measured.json` | 7 tokens, ZERO collisions against a calibrated p10 of 9.55 |
| caption and its critic verdict | `runs/carousel/2026-09-11/caption-UNSHIPPED.txt` | `caption_check` clean, 140 words, 1.43 commas per 100 |
| frames 1 to 4 | `runs/carousel/2026-09-11/slides/` | render clean, no page errors |
| tooling | `inject_computed.py`, `build_copy.py`, `measure_palette.py` | reusable, each tested |

## What is left

Frames 5 to 9 per the storyboard's dossiers, then the ordinary tail: pixel review, flow critic,
`aggregate_check`, assembly, `panel_ready`, the panel of three, ship images, ledgers.

**The measured frame medians so far are 28.4, 65.4, 42.7 and 73.1 against planned 38, 62, 44 and
56.** Frames 2 and 4 are running light because the mint CMU wall is inherently L\* 83 and the
overhead falloff was not doing enough work. **The deck median must come in under 60** or
`ledger_check` fails: the light cap is already over at 2 in 8 and survives only on the named
2026-09-03 waiver.

## Two defects in the frames as handed over

- **Frame 4's far wall is still too bright** and the three declared planes separate less than the
  dossier's 9 L\* step promises. Measure before the panel sees it.
- **Frame 3's desk leg and tablet edge read as a red bar on a stick.** It holds the bottom third
  and it is not yet a desk.

## The topic is NOT spent

`ledger/carousel/topics.json` carries no entry for it, because no deck shipped. The thirty day
dedupe window is clean for this story.


## Why the caption and the source block carry an UNSHIPPED suffix

`email_check.shipped_runs()` treats **any** run directory holding a `caption.txt` as a run that
produced a deck, and then requires a `gmail_payload.json`, a linked PDF and slide thumbnails
beside it. `gmail_draft.py` cannot build a payload without thumbnails, so a run that writes a
gated caption and ships no deck would fail `email_check --all` in CI on every future run, not just
its own.

**The honest reading is that an unshipped caption is not a shipped caption**, so the files are
named for what they are. Rename them back when the deck ships.
