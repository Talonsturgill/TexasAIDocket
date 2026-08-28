# Proposals from the 2026-08-28 run

Each is out of the `daily` lane and is written down rather than made.

## 1. The caption ledger's exclusion lists are wrong in both directions, and a judge used them

`ledger/carousel/captions.json` stores `opening_moves_recent` and `structures_recent` as hand-kept
arrays. Computed from `entries`, the last six opening moves are `the plain question, the before and
after, the deadline, the quiet decision, the number that is wrong, the who`. The STORED array reads
`the two things, the plain question, the before and after, the deadline, the quiet decision, the
number that is wrong`. It carries a move that is seven runs back and omits yesterday's. The same is
true of the structures. The ledger's own `recent_lists_note` predicted this on 2026-08-20 and asked
for `caption_check.py` to DERIVE the lists from entries. It has not been done.

This run paid for it. The caption room was handed the computed lists and the critic judged against
the stored ones, so the two halves of one phase were working from different exclusion sets. The
critic's rejection was still right on other grounds, which is luck rather than a defence.

**The change.** Derive both lists in `scripts/carousel/caption_check.py` from `entries` and delete
the stored arrays, or make the gate fail when the stored arrays disagree with what entries compute.

## 2. `label_guard` fails closed on decks that print no act labels

It looks for an `ACTED` shape map in `compute.py`, a construction one earlier deck used to print a
place, an act and a claim id together. This deck prints source attributions instead, so the gate
reports "found no shape map in compute.py, so it is reading the wrong file" and exits 1. A gate that
refuses a deck for not using one particular construction is answering a question it was not given.
It is not in `guards.yml` and `shipped_check` is clean, so nothing broke, and a red exit code that
nobody can act on is how a run learns to stop reading exit codes.

**The change.** Report NOT APPLICABLE when the deck prints no labelled acts, and keep failing when a
map exists and a frame's label disagrees with it.

## 3. `docket_build.backlog` prints an exemption that no longer describes anything

`GEOGRAPHY_BACKLOG` is a dict of three item ids and every build prints one line per id
unconditionally. `tx-2026-0007` already carries `statewide: true`, so its line is false about the
current record, and no amount of work on the record can ever clear it because the printer never
looks at the item. A ratchet that cannot move is a decoration, which is the exact shape
`GATE_LESSONS.md` keeps recording.

**The change.** Print a backlog line only when the item still has the gap the exemption names, and
say out loud when an exemption has gone stale so it can be deleted.

## 4. `brand.yaml`'s `ends_with: engagement_question` collapses five closing moves into one

`CAPTION_CRAFT.md` offers five closes and tells the room to rotate them. `caption_check` enforces
`linkedin_post.ends_with: engagement_question`, so every caption must end on a question mark. Four
of the last four shipped captions therefore close by asking the question the decision leaves open,
because that is the only one of the five moves that is natively a question. The doctrine and the
config are pulling against each other and the config wins every time.

**The change.** Either drop `ends_with`, or rewrite the four other closes in CAPTION_CRAFT so each
has an interrogative form, and have the ledger record which was used.

## 5. The scout agents cannot write the file the routine tells them to write

`carousel-scout` is defined with `WebSearch`, `WebFetch` and `Read`. `prompts/daily_routine.md`
Phase 2 has them write `out/research/scout-<beat>.json`. All six scouts reported the same failure
unprompted and returned their findings in their replies instead, so nothing was lost. A step that
can never succeed is a step that silently does nothing.

**The change.** Either give the scout a write tool, or drop the instruction and have the showrunner
persist the replies.

## 6. `plan_render_check`'s palette regex cannot express this project's own token names

`PALETTE_DEF = re.compile(r"`([a-z][a-z ]*?) (#[0-9A-Fa-f]{6})`")`. The name pattern allows lower
case letters and spaces and nothing else, so `sky_predawn`, `rim_light`, `caliche_cap`,
`satin_spar` and `ledge_shadow` can never match, and the declared-colour check reported "the
storyboard defines no `name #HEX` palette" all run. Every palette this project has shipped uses
underscored token names.

**The change.** Allow an underscore in the token name.

## 7. The site publishes the commission's sentences as this project's own prose

**This is the most consequential thing this run found, it is live on `texasaidocket.com` right now
on every shipped deck, and the fix is out of the `daily` lane so this run may not make it.**

`site_context.load_runs` builds each article page's prose from `copy.json` and decides whether a
sentence is a quotation with `said.startswith('"')`. A leading quotation mark is the entire test.

This deck attributes its quotes the way the design doctrine asks, with a plate colour and an
attribution line, so nine verbatim sentences from PUCT Docket 59220 arrived at the article page
wearing no mark, and the page set them as paragraphs this project wrote. `house_style_check` then
did exactly its job and reported three violations in "copy this project wrote": a bare
"September 17" against the ordinal rule and two sentences over the 30 word backstop. All three
were in the Public Utility Commission's words, and every one of them was unfixable, because
rewriting a quotation to satisfy a house rule is falsifying it.

**The three it caught were the tip.** Every verbatim dek in the deck arrived unmarked. The rest
passed only because they happened to be short and carried no bare date, so the same defect was
shipping in silence on the frames that did not trip a rule. Rebuilding the site after a trial fix
changed four already-published article pages, from 2026-08-20, 08-22, 08-25 and 08-26, which is
the proof that this has been live for as long as the article page has published prose.

**What this run did instead, and why it is not the whole fix.** The deck now prints straight
quotation marks on all nine of its verbatim strings, on eight frames. That is in lane, it satisfies
the builder's documented contract, and it is better on the slides too. It fixes this deck. It does
not fix the next one, because nothing stops a future deck attributing a quote with a plate again,
and the failure is silent unless the quotation happens to break a house rule.

**The change, for a maintainer session.** `claims.json` already holds the exact quote every fact
was checked against, and a deck may only print a source's words from there. So the article page can
DERIVE the answer instead of trusting punctuation: a slide string that appears inside a claim's
quote is that source's words, however the frame dressed them. A leading quotation mark still counts,
so a deck that does mark its quotes is not made a liar by it, and a short string is excluded so a
label is never mistaken for a quotation. That is the same standard every number on this site is
already held to, derived from the fetched source rather than declared by whoever typed the slide.

This was implemented and verified here before being reverted: with it, the 2026-08-28 article page
set nine blockquotes and ten paragraphs, `house_style_check` went clean across 415 pages, and
`site_context.py --self-test` passed. The diff is one function plus moving the `claims` load above
the `prose` loop. `scripts/site/site_context.py` is owned by `human`, and `ownership_check` refused
it, which is the map working exactly as intended.

## 8. A gate can prove a URL is correct and still not prove it is readable

Slide 9's `texasaidocket.com` was the least legible text in the deck. It is set in brown on pale
caliche in a plan view that carries no scrim, and a desiccation crack ran straight through
"docket.com". `coherence_check` passed it, correctly, because the string matches `brand.yaml` on
every frame. `copy_sync_check` passed it. Machine QA passed it. Round 3's craft judge found it by
looking.

The one URL this project publishes is named in CLAUDE.md as a thing three separate surfaces got
wrong before, and every check written since asks whether the string is RIGHT. None asks whether a
reader can read it.

**The change.** Machine QA already computes ink-to-ground separation under a text line box for its
busy-art warning. Give the site line its own floor, checked on every frame rather than warned
about, so a footer that cannot be read fails the build. This deck now measures 150 levels of
separation on slide 9 after the ground was lifted under the footer, which is a number a floor
could be set against.

## 9. The artwork ledger compares palettes for equality, and the collisions are near misses

Round 3's craft judge measured three of this deck's ten tokens against deck no. 8's, from two runs
ago: `satin_spar #F5F1E6` against `cut_face #F4F0E4`, `caliche_cap #E4DCC6` against
`limestone #E5DECC`, and `ledge_shadow #241E22` against `blackland #211E1A`. The first two are
indistinguishable by eye. `satin_spar` is this deck's declared light and its type colour, so the
most-seen colour across nine frames is deck 8's light under a new name.

Deck no. 8's own ledger entry already records the shape of this: "granite returns at the identical
hex last spent on 08-16, which a judge found and which no ledger field currently compares". That
entry describes an EXACT repeat. These three are near misses, so even the equality check that entry
asks for would not have caught them.

**The change.** Compare palettes by perceptual distance rather than by string equality, against the
last N decks in `ledger/carousel/artwork.json`, and fail or warn below a stated threshold. The
threshold is a number, so it gets computed from the distances between tokens this project has
already shipped rather than picked.

Two related findings from the same judge, recorded here rather than repaired by hand, because both
are engine work rather than one deck's work:

- **One granular crumb primitive carries the declared focal on slides 1, 3, 7 and 8**, four of
  nine. `bespoke_check` reports a median pairwise similarity of 0.2081 and a closest pair of 0.6953,
  and it passed, so its measure is not seeing this. It compares frames; the repetition is in the
  TECHNIQUE each frame reaches for.
- **Slides 1, 3 and 8 resolve to one picture at feed size**, a cold graded sky over a pale
  irregular band over a dark warm mass with plates. The camera plan declares three different
  cameras and the thumbs do not show three. Camera variety is currently asserted in the dossier and
  never measured.

## 10. A document-structure locator is a claim, and nothing checks that one traces

Round 4's integrity judge called a hard fail on slide 8 for printing
`PUCT DOCKET 59220, ORDER, ORDERING PARAGRAPH 6` when the numeral 6 appeared in no claim quote,
no `source_title`, and nowhere in `computed.json` or `aggregates.json`. The call was correct.
The deck was printing four such locators and not one of them traced: `ORDERING PARAGRAPH 6` on
slide 8, `ORDERING PARAGRAPH 1` and `CONDITION 1` on slide 3, and `FINDINGS OF FACT` on slide 5.

**All four turned out to be TRUE**, which is the interesting part. Checked against the order text
this run had already fetched: line 658 is `V. Ordering Paragraphs`, its paragraph 1 is
`The Commission approves the proposed net metering arrangement` followed by `Condition 1:`, line
750 is `6. The Commission denies all other motions`, line 317 is `III. Findings of Fact`, and c3
and c5 are findings 3 and 5 within it. So the frames were right and the claims file simply did not
carry what they were asserting. The fix here was to the DATA: every locator now sits in its
claim's `source_title`, so the string on the frame traces to a field a reader can check.

**That the locators were true is exactly why this needs a gate rather than more care.** A figure
cannot reach a frame without going through `compute.py`, which refuses anything not in a quote.
A locator reaches a frame by being typed into the slide HTML, and nothing stands between. This
one happened to be right. `numeral_lint` did not see it, because it reads published site copy
rather than slide strings. `copy_sync_check` did not see it, because the string is in `copy.json`
and in the render and that is all it asks. Four gates, one judge, and only the judge looked.

**The change.** A `locator_trace` gate over the run's slide strings: any span matching a
document-structure locator (ordering paragraph, finding of fact, conclusion of law, condition,
section, exhibit, item, followed by a number or standing as a named heading) must appear in some
claim's `source_title`, `quote` or `text`. Fail the build otherwise. That is the same shape as
`numeral_lint` and the same shape as `compute.quoted()`, applied to the one class of assertion
that currently has no route.

## 11. An assertion about arithmetic is not an assertion about a source

Round 5's reader judge asked slide 6 to show the arithmetic its own hook promises. It looked free:
260 and 265.5 were already quoted figures and they sum to the quoted 525.5 exactly. So `compute.py`
emitted `260 MW load + 265.5 MW generation`, guarded by an assertion that the components equal the
total, and the frame printed it. Every gate passed. `numeral_lint` passed, because both numerals
trace. `copy_sync_check` passed. `aggregate_check` passed. `plan_render_check` passed.

**The guard passed and the sentence was false.** The order's recital of the contention, page 7,
reads that Docket 58881 already requires the Crusoe One Load "(which is 265.5 MW)" to curtail, and
that if the Crusoe Two Load "(which is 260 MW) is also obligated to curtail, it would result in a
total curtailment of 525.5 MW". The applicants added TWO LOADS. The 265.5 in their total is the
Crusoe One Load as they characterise it, not GOODNIT1's generation. The frame said generation.

The defect is exact and it generalises. `quoted()` works because it asks a CLAIM a question: is
this string in that source's words. The sum guard asked ARITHMETIC a question, and arithmetic
answers the same way for the wrong components as for the right ones, because 260 + 265.5 = 525.5
either way. **A tautology cannot fail, so it certifies nothing.** It is a green check measuring
something narrower than the thing it appears to certify, which is GATE_LESSONS' own recurring
shape, this time built deliberately and in good faith by a run trying to be rigorous.

It is worth recording HOW it was caught, because no machine caught it. An integrity judge asked
which claim stated the decomposition, found none, and refused. That question, not the arithmetic,
is the check.

**The change.** A relationship between figures is a CLAIM and needs a claim id like any other. If
the deck states that A plus B is C, some claim's quote must say so. `compute.py` should offer no
way to publish a derived relationship without naming the claim that establishes it, in the same
shape `quoted()` already has: `related(cid, "...")` that reads the claim's own words. The
arithmetic check can stay as a second belt, but it must never be the only one, and it must never
be mistaken for provenance.

**The house law already said this and the run still got it wrong.** "Every fact carries a claim-id
and traces to a fetched source." A sum of two facts is a third fact. The lesson is that the law is
easiest to break precisely when every ingredient is already sourced, because the result feels
sourced too.
