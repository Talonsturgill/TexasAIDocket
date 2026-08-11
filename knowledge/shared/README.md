# knowledge/shared — the long-term context every automation reads

This directory is the project's memory. Research done once lands here and is read on every run
thereafter, so the machine gets smarter over time instead of rediscovering the same facts and
making the same mistakes.

**The rule: research is not finished until it is written down here.** A finding that lives only
in a session transcript is a finding the next run does not have. Every research pass produces or
updates a document in this directory, and every routine prompt reads the documents relevant to
its phase before it starts work.

## What each document is for

| Document | What it holds | Read by |
|---|---|---|
| `GRID_WATCH_DESIGN.md` | The ERCOT instrument: the headline metric, what it refuses to say, the caveat block, tested endpoints, the competitive read | grid watch collector, carousel research phase |
| `OIL_WATCH_DESIGN.md` | The oil instrument: why it is weekly, the SPR headline, the two computable Texas numbers, the Baker Hughes licensing exposure, the refusal list | oil collector, carousel research phase |
| `TEXAS_ENERGY_POLITICS.md` | The live fights, the positions, who decides, and the dated decisions ahead | carousel + video research, docket phase |
| `TEXAS_POLITICS.md` | Officeholders, terms, factions, documented positions, how a decision actually gets made, who to call | docket phase, fact-checking |
| `TEXAS_POWER_FAMILIES.md` | Oil and ranch dynasties, political money, land ownership, handled to a documented-only standard | fact-checking, framing |
| `TEXAS_HISTORY.md` | The honest history, including where the popular version diverges from the record, plus a calendar of dates | carousel + video framing, artwork |
| `TEXAS_VERNACULAR.md` | Drawable regional specifics, the grin list, what locals find wrong, cultural sensitivity | video art direction, carousel artwork |
| `TEXAS_ATTITUDES.md` | How Texans think and why, by region and community; what resonates and what reads as outsider | voice, framing, caption writing |
| `TEXAS_CITIES.md` | Per-metro profiles, utility structure, government form, local outlets | metro scoping, docket, source lists |
| `TEXAS_AI_LANDSCAPE.md` | Companies building, applications actually deployed, urban and rural, research institutions | carousel + video story selection |
| `TEXAS_TELEMETRY.md` | The live numbers that matter to Texans, tested sources, seasonal rotation | site hero, grid watch |
| `TEXAS_DESIGN_DOCTRINE.md` | Colors, type, geometry, the authentic registers and the kitsch traps | site build, carousel art, video art |

## Standards these documents are held to

1. **Sourced.** Every factual claim carries a URL or is marked as unverified. A document that
   cannot tell a reader where a fact came from is not doing its job.
2. **Verification-marked.** Use `[V]` for corroborated, `[1S]` for single-source, `[?]` for
   unconfirmed, `[CONFLICT]` where sources disagree. **A conflict is reported, not resolved by
   picking one.**
3. **Dated.** Research decays. Every document says when it was compiled, and any figure carries
   its own as-of date.
4. **Reasons preserved.** A rule stripped of its reason is a rule the next context talks itself
   out of. When a document says never do something, it says why, with the evidence.
5. **Absence is a finding.** "Nobody publishes this" and "the state does not collect this" are
   among the most valuable things these documents record, because they are where the product's
   value comes from.
6. **They obey the house rules too.** No em dashes, no emojis, month-first ordinal dates,
   straight quotes. These are read by the same machines that write published copy.

## For a routine reading this

Read the documents your phase names before you begin, not while you work. They exist to change
what you decide, and a document read after the decision is a document that changed nothing.
