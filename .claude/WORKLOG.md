# WORKLOG — run 2026-08-30

Durable plan for the daily routine, written to survive context compaction. Delete when every
wave is DONE.

## Context this run inherited

The permission defect that stopped six unattended runs was diagnosed and fixed BEFORE this
routine started, as a separate maintainer change on `tsturg/practical-franklin-5qoevl`, merged
to `main` as PR no. 237 (`cd5d10b5`). The lane is now resolved from the branch and nothing is
written to declare it. This run is the first to operate under that.

If a later context is reading this and wonders whether to write a lane stamp: no. See CLAUDE.md
under the heading saying the stamp is never written.

## Decisions already made, with the measured reason

- **The deck is NOT TeraFab.** `dedupe_check` scored 0.64 LIKELY REPEAT against carousel no. 1
  (2026-08-16), whose entities already include TeraFab AI LLC, Grimes County, Iola ISD and
  Anderson-Shiro CISD, and whose keywords already include JETI. Read in full before deciding.
  The fact-checker also rejected Grimes County as an inference the Comptroller table does not
  state, so the item has no place and could not be admitted anyway.
- **The deck is the Flock money trail.** Dedupe 0.41 against the 2026-08-20 League City deck,
  below the repeat threshold, and read in full: that deck was a nonbinding municipal BALLOT in
  one city. This is state grant money, a statewide network and a Governor's order. Different
  decider, different instrument, different scale.
- Claims live at `out/2026-08-30/claims.json`, 39 verified, 18 rejected, `claims_check` clean.
- Five scout files are in `out/research/`.

## Wave status

| wave | what | status |
|---|---|---|
| 0 | wake, branch, gates | DONE, `claude/daily-2026-08-30` off `cd5d10b5` |
| 2 | scouts (5, three on application beats) | DONE, `out/research/*.json` |
| 3 | re-verify the record, 17 due, 0 rotten | TODO |
| 4 | discover | PARTIAL, folded into the scout pass |
| 5 | admit | TODO |
| 6 | claims | DONE, 39 verified, gate clean |
| 7 | instrument once over | TODO |
| 8 | selection + dedupe | DONE, see above |
| 9 | directors room | TODO |
| 10 | copy chamber | TODO |
| 11 | art build | TODO |
| 12 | pixel review | TODO |
| 12b | the six gates | TODO |
| 13 | aggregate gate | TODO |
| 14 | assembly | TODO |
| 15 | scoring panel | TODO |
| 16 | assemble, PR | TODO |
| 17 | retro + upgrade | TODO |
| 18 | merge | TODO |
| 19 | gmail draft | TODO |

## Sources field log to append at Phase 17

- PUCT was dark all run. `interchange.puc.texas.gov` and `www.puc.texas.gov` returned HTTP 503
  to three separate clients, including the calendar RSS the registry calls the highest value
  poll of the run. Tool level, not a robots decision.
- `texreg.sos.state.tx.us` has MOVED. The Texas Register now serves from `www.sos.texas.gov/texreg/`.
- `capitol.texas.gov/TLODOCS/` is robots-disallowed for all agents, so committee hearing notices
  cannot be read. Respected, not routed around.
- The Texas Tribune WP REST API returns `content.rendered` in full and is how figures became
  quotable. Use it by slug rather than the article URL when a Tribune figure matters.
- HTTP 403 to this client: `usda.gov`, `texasattorneygeneral.gov` (402), `openai.com`,
  `cprit.texas.gov`, `www.fortworthtexas.gov`, `houstonpublicmedia.org`, `kxan.com`.
- `assets.comptroller.texas.gov` JETI PDFs exceed the fetcher's 10 MB limit.
- `search.txcourts.gov` opinion PDFs have no extractable text layer.
- `kfgo.com` injects zero-width unicode into body text, which breaks character-for-character
  quoting.
