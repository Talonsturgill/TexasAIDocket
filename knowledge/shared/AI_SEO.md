# Being found, by people and by machines

The doctrine behind this record's discoverability. Read it before changing anything under
`scripts/site/schema.py`, `robots.txt`, `llms.txt`, the feeds, or the head of a page.

The one sentence: **a record whose whole argument is that it is checkable should be the easiest
record on the internet for a machine to check.** Everything below follows from that, and
nothing below is a trick to rank. A trick that works is still a claim we cannot stand behind.

---

## 1. The two audiences want different things and both get the truth

A search crawler wants structure it can index. An answer engine wants the cleanest available
statement of what a page asserts, so it can quote it without guessing. Neither wants prose
written at it.

The split that matters in practice:

| audience | what it reads | what it is worth |
|---|---|---|
| search crawler | `Dataset`, `BreadcrumbList`, sitemap, feeds, headings | rich results, dataset entries, hierarchy in the result |
| answer engine | JSON-LD `FAQPage`, `llms.txt`, the Markdown twins, clean prose | being quoted correctly rather than paraphrased wrongly |

**Write once, emit for both.** Every question and answer this site publishes is computed from
the same ledger fields the page renders. Nothing is authored twice, so the two can never
disagree, which is the failure mode a hand-maintained FAQ always reaches.

## 2. Structured data is published copy

This is the rule the rest of this file exists to protect.

`house_style_check` strips `<script>` before it lints a page, correctly, because the ask page
ships its whole engine inline and a JavaScript `i` was being read as a first person pronoun.
JSON-LD lives in a `<script>`. So when the schema spine began emitting 633 generated sentences,
those became the largest surface of published prose on the site that **no gate read**.

`schema_check.py` reads them. Every house rule applies inside JSON-LD exactly as it applies in
a paragraph: no first person, no em or en dash, no semicolon, never "cannot", ordinal dates,
and **every numeral traced to a value in the record**.

If you add a new node type that carries prose, add it to `prose_of()` in the same commit. A
type whose text nothing lints is the hole reopening.

## 3. Every answer is computed, never written

The compute-not-generate law owns structured data the same way it owns the front page.

- The question set is a **fixed list of shapes**. Each answer is assembled from named ledger
  fields and from arithmetic done in Python.
- No model writes an answer. A model writing an answer is writing a claim, and a claim in this
  project carries a claim-id and a fetched source.
- The allow-list of numerals a sentence may state is **derived from the ledger, not from the
  generator**. Deriving it from the code that writes the sentence would be circular and would
  prove nothing. This is the same discipline the ask lane reached independently: a machine may
  state a number only if that number was in what it was given.

**A question the record cannot answer is dropped, never answered vaguely.** "No information is
available" would otherwise become the most repeated sentence on the site, and it helps nobody.

## 4. The type is a claim

Marking a page `NewsArticle` to catch a rich result is a lie told to a machine, which is the
same as telling it to a reader. These pages are a **record**. `Report` plus `Dataset` is what a
tracked decision is, so that is what it wears.

The same honesty runs the other way. `FAQPage` is emitted here **with its eyes open**: Google
cut FAQ rich results back to well-known government and health sites in 2023 and this site is
not one, so nothing about it should ever be justified by a rich result it will not get. It is
emitted because answer engines read it as the cleanest statement of what a page asserts. If
that stops being true, the block comes out rather than getting re-justified.

## 5. The graph has to join up

Repeating a publisher object on 148 pages states one fact 148 times and builds no graph. One
node, one stable `@id`, referenced everywhere:

```
/#org                  the publisher, referenced by every Report and the Dataset
/#website              the site
/record/#dataset       the record, which every Report says it isPartOf
/item/<id>/#report     one per decision
/item/<id>/#faq        its questions
```

`schema_check.py` fails on a reference to an `@id` nothing defines. A dangling edge is a graph
that looks joined up and is not, and it is invisible without a checker.

## 6. What a quotation is, and why it is never linted

Every claim carries the source's own words. Rewriting them to fit house style would falsify
them, which is far worse than an inconsistent dash.

**A document's TITLE is the document's own words by the same argument.** The Federal Register
really did publish "Proposed Information Collection; ATUS Artificial Intelligence (AI)
Questions". The Southwest Power Pool really is joined to the Association of Electric Companies
of Texas by an em dash in the title of the thing that was fetched. Neither is ours to tidy.

So source titles are stripped before the punctuation rules run, and the exemption is **derived
from the record**: a span is exempt only if it appears verbatim as a `source_title` on a claim.
That is what stops the exemption being a hole a hand-written sentence can hide in.

## 7. Never trade honesty for reach

The rules that do not bend, whatever it would buy:

- No page exists only to rank. `/questions/` and `/topics/` are generated **views over the
  record**, and a view with nothing behind it is a doorway page, which is both spam and a lie.
- No keyword written for a crawler rather than a reader.
- No claim in structured data that is absent from the page. A citation a machine repeats is
  believed more readily than a sentence a person reads, so a false one costs more.
- No number anywhere that a person or a model typed.
- Never take a path a publisher's `robots.txt` disallows.

## 8. What is measured, and against what

Recorded 2026-08-15 so a later session can tell movement from noise.

| surface | before | after S1 |
|---|---|---|
| distinct JSON-LD `@type` | 5 | 16 |
| `Question` / `Answer` pairs | 0 | 633 / 633 |
| `Report` | 0 | 58 |
| `FAQPage` | 0 | 58 |
| `BreadcrumbList` | 0 | 58 |
| `GovernmentOrganization` | 0 | 53 |
| `AdministrativeArea`, one per county named | 0 | 68 |
| citations as `CreativeWork` | 0 | 105 |
| dangling `@id` references | n/a | 0 |

The sibling ships 208 question and answer pairs off 20 decisions. This ships 633 off 58, from a
ledger that carries a verbatim quote and a fetched source behind every fact.

## 9. The order to add things in, if this is ever rebuilt

1. Structured data and the lint that reads it. Everything else is smaller than this.
2. The corpus surfaces: `llms.txt` with real sections, `llms-full.txt`, the feeds, `404.html`.
3. Social cards, so a shared link is not a bare string.
4. The answer hubs, which is where long-tail questions land.
5. Submission, which only matters once the four above are true.

Submitting a thin site faster does not make it a better site. It makes it findable sooner, and
that is the wrong end to start from.
