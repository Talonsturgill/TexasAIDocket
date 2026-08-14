# Caption craft — the variety engine for post copy

The caption is the only part of the deck a reader meets before deciding whether to look at the
deck. It is also the most repeatable thing this machine produces, and that is the danger. A
machine will find an opening that scores well and use it every day until the account reads like a
form letter with the nouns swapped.

`config/brand.yaml` holds the voice and the house rules, and `scripts/carousel/caption_check.py`
enforces the mechanics. **This file is about the shape of the thing**, and about the one rule the
mechanics cannot check.

---

## The anti-template law

**Every caption is conceived fresh for its own story.** Not filled in.

The test is simple and it is applied by the caption critic, whose default is dissatisfaction: if
you can swap yesterday's nouns into today's caption and it still reads correctly, it was a
template, and it fails. Two captions may share a structure. **They may not share a sentence
skeleton.**

This cannot be checked mechanically, which is exactly why it is written down first. A linter can
count commas. Only a reader can tell that the machine has stopped thinking.

---

## Opening moves

The caption room is handed an assignment and the ledger's exclusions. **The last six runs' opening
moves are off the menu**, recorded in `ledger/carousel/captions.json` under
`opening_moves_recent`.

Aim at four to seven words for the first line, per the brevity principle in `brand.yaml`. Intrigue
beats completeness. The sentence underneath is where the completeness goes.

| move | what it does | example shape |
|---|---|---|
| **the number that is wrong** | opens on a figure the reader will misjudge, then corrects it | "Eight gigawatts asked. Four are drawing." |
| **the deadline** | opens on a date that is about to pass, because a closing comment window is the one thing a reader can still act on | "Comments close September 4th." |
| **the place** | opens on a specific Texas place, so the story lands somewhere before it means anything | "Hood County has a new neighbour." |
| **the plain question** | one question a Texan would actually ask, answered in the body | "Who pays for the line?" |
| **the quiet decision** | opens on the fact that something was decided while nobody watched | "The rule changed in March." |
| **the two things** | sets two facts beside each other and lets the gap do the work | "Approved, 8.9 gigawatts. Drawing, 4.0." |
| **the object** | opens on a physical thing, not a policy, because a transformer is easier to see than a docket | "A substation yard outside Abilene." |
| **the correction** | opens by naming a thing everybody believes that is not so | "Data centers do not mostly drink water." |
| **the who** | opens on the body that decided, named plainly, since most readers cannot name the PUCT | "Three commissioners decided this." |
| **the before and after** | states the old state of the world in one clause, the new one in the next | "Anyone could file. Now it costs." |

**These are ten doors into a room, not ten templates.** The move names where the caption starts.
It does not supply the sentence.

---

## Structures

The last three runs' structures are off the menu.

- **Ladder.** Fact, consequence, consequence, stop. Each sentence stands on the one before it.
- **Pivot.** Half the caption sets up the reading everybody has, then one sentence turns it.
- **Zoom in.** State to region to county to a single site. Ends somewhere a person could stand.
- **Zoom out.** One site, then what it is an instance of.
- **Clock.** Ordered by date. Works when the story is a sequence of decisions and nothing else.
- **Ledger.** What is known, then what is not known, then the size of the gap. The honest shape,
  and the one to reach for when the record is thin.
- **Question and answer.** One question, answered, then the part of it that is still open.
- **Two columns.** What was asked for beside what happened. The gap is the story.

---

## Closing moves

Rotate. Never the same phrasing two runs running.

The close is where a caption most wants to become furniture, because the writer has said the
interesting part and wants to get out. **Resist the urge to summarise.** The reader just read it.

- Name what happens next and when.
- Name what is still not public, and how big that is.
- Point at the record, plainly, without a call to action.
- Ask the one question the decision leaves open.
- Stop on the strongest fact, with no wrap-up at all. This is often the best one.

---

## Banned furniture

Mechanically enforced where possible, judged where not. These are the phrases that make copy
sound like every other account.

Openers that promise and deliver nothing: "In a move that", "It is worth noting", "Let us be
clear", "Make no mistake", "Here is the thing", "The bottom line", "At the end of the day",
"Simply put", "Needless to say".

Engagement bait: "Thoughts?", "What do you think?", "Drop a comment", "Agree or disagree",
"Share if you", "Follow for more", "Read that again", any hashtag, any emoji.

Hype: "game changer", "revolutionary", "unprecedented" unless it is literally true and sourced,
"massive", "explosive", "staggering", "shocking", "the future of".

Consultant filler: "leverage", "unlock", "empower", "at scale", "double down", "circle back",
"deep dive", "learnings", "in today's landscape".

Hedges fenced off by a pair of commas. This is a construction rule, not a word list, and it is in
`brand.yaml` because it applies everywhere. Write two sentences.

---

## Voice, which does not move

Texas first. **We want Texans and AI to win**, and that is not a slogan, it is the lens: a story
about a data center is a story about the county it sits in and the grid it draws from.

Analytical, not boosterish, and not doom. A press release is not a fact. Neither is a lawsuit.

No first person, ever. The record does not have a personality and should not grow one.

No numeral is ever typed. Every figure traces to a claim id or to a computation, per the law in
`CLAUDE.md`.

Plain nouns for civic bodies, because most readers cannot name them. **A county judge is an
executive, not a judge.** The Railroad Commission regulates no railroads.
`knowledge/shared/TEXAS_LANGUAGE.md` is the list, and getting one of these wrong in public is the
fastest way to be read as an outsider writing about Texas.

---

## The comma ceiling is deliberately not set

The site's running prose is held to 3.97 commas per 100 words, ten percent below its own measured
4.41.

**Captions have no ceiling yet, and borrowing the site's would be exactly the typed-in number the
compute-not-generate law forbids.** No caption has shipped, so there is nothing to measure. The
ceiling is computed from this product's first twenty shipped captions, at ten percent below their
measured mean, once, with the date recorded.

The unblock condition is in `config/parity_map.yaml`. `caption_check.py` measures the rate every
run and reports it without failing, so the corpus builds while the gate waits.

Ten percent below a corpus that a comma rule has already cut is a ratchet that reaches zero in
three rounds. **It is a one time move off an unconstrained corpus, and the file must say so.**

---

## The ledger contract

Every shipped caption records, in `ledger/carousel/captions.json`:

```
{
  "date": "2026-08-12",
  "opening_move": "the deadline",
  "structure": "ladder",
  "closing_move": "name what is still not public",
  "first_line": "the actual first line, verbatim",
  "words": 143,
  "commas_per_100w": 3.1
}
```

The caption room is handed the exclusions before it writes: opening moves from the last six runs,
structures from the last three. `first_line` is stored verbatim on purpose, because the critic's
real job is catching the skeleton that survives a change of nouns, and it can only do that with
the actual lines in front of it.

`words` and `commas_per_100w` are the corpus the ceiling will be computed from. **They are
measured by the script, never typed into the ledger by hand.**
