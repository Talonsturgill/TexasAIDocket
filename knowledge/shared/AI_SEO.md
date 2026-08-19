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

**Amended 2026-08-19, and the amendment is the point.** The ban was written for the record and
then applied to the whole site, so `/articles/<date>/` was refused the one type that is true of
it. Those pages are the carousel's written companion. They have a headline, a body of prose, a
publisher and a date they were published, which is what `NewsArticle` describes. Refusing it
there was not honesty, it was a rule reaching past what it was written to protect, and the cost
was that the three pages most likely to be quoted told a crawler the least about themselves.

The carve-out in `schema_check.article_type_ok` is narrow on purpose and both halves matter. One
type rather than three, because the ban's real job is to stop a decision being dressed as
journalism, and `Article` on an item page would do that just as well. And the node must carry
`datePublished`, so the exemption cannot be taken by an article-shaped node that is not dated,
which is the shape a mistake would have. **An exemption is a promise about the content of a
region, never about the path**, and one that nothing tests is a hole with a comment over it, so
the self-test asserts it in both directions.

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

---

## 10. The part that was actually wrong, and it was none of the above

On 2026-08-19 the site did not appear in Google for its own name. Every check in the repository
was green and none of them was wrong. They were pointed at the wrong thing.

**A search engine will not show a site it has never been told about.** There was no Search
Console property, no verification of any kind, and the sitemap had never been handed to anyone.
Discovery is by link: a crawler reaches a new site by following one from a page it already
knows, and nothing on the indexed web pointed at the domain, which was four days old. A new
domain with no inbound links and no submission sits weeks before a first index. With the
sitemap submitted it is days.

So the order in section 9 is right and the last line of it was the one that had not been done.
**Being excellent at the first four is not a substitute for the fifth.** A perfect site nobody
has been told about is a perfect site nobody reads.

### What only a person can do, written down so a run stops trying

A routine cannot create a Search Console property, cannot prove ownership of a domain, and
cannot earn a link from somebody else's site. Those three are the owner's, permanently. What the
machine can do is make sure that the moment they happen there is nothing left to fix, and that
is what `seo_check.py` gates.

### Three defects the green suite was hiding

**`lastmod` said today, on every url, every day.** Google's stated position is that a `lastmod`
it finds unreliable is one it stops reading, so the single field that says "this page is worth
fetching again" was being spent on 222 pages that were not. The fix is `lastmod.py`, and the
source of truth is the history of the generated bytes themselves, because `docs/` is committed
and git already holds exactly the record of when a page changed. No new state to keep and
nothing to drift.

The prerequisite is worth remembering because it is not obvious and it makes the naive fix do
nothing. The page footer **printed the date into the page**, so every page differed from its
committed self every morning and every date came back as today no matter how it was derived. A
page carrying its own date cannot be compared against itself without normalising the date out
of both sides first. The same computation now feeds the footer, so the two surfaces cannot
disagree.

**The articles carried no article markup.** No schema, no date, `og:type` of website, and the
generic site card on every share, so a link to a piece of writing looked like a link to the
front page. They are the only reporting on the site and were the pages telling a crawler the
least about themselves.

**One shipped a 25-character description**, because the builder took the first sentence and
stopped. That description is what a search result has to sell itself with.

### The pattern, since this is the fourth time

A rule stated in one place, a surface that never checks it, and nothing in between. It has now
been the site URL, the hashtags, the progress counter, and this. The cure is the same every
time and it is not more prose: a gate that reads the built artifact and can be proved to go red
against the real defect. `seo_check.py` is that gate, and it was planted against the live build
to prove it was connected before it was believed.

---

## 11. The submission runbook

Owner decision 2026-08-19: verification is by **DNS TXT**, not by meta tag. It verifies the
whole domain including every subdomain and both protocols, and it cannot be dropped by a build.
`GOOGLE_SITE_VERIFICATION` and `BING_SITE_VERIFICATION` in `site_build.py` stay empty and exist
only as a fallback. `seo_check` reports an absent tag as a note and never as a failure, because
an empty token is a legitimate finished state under this decision.

**Google Search Console.** Add a **Domain** property for `texasaidocket.com`, take the TXT
record it offers, add it at the registrar, verify. Then submit `sitemap.xml` under Sitemaps, and
use URL Inspection plus Request Indexing on the front page and `/record/`. Requests are capped
around ten a day, so spend them on hubs rather than on item pages, which are reached from the
hubs anyway.

**Bing Webmaster Tools.** Import the Google property rather than verifying again. IndexNow
already submits to Bing on every deploy, so this is for the reporting rather than for the
crawling.

**The first IndexNow sweep is a one-off.** `pages.yml` runs `indexnow.py --since <today>`, which
is right for a daily deploy and submits nothing that has not changed. Running it with no
`--since` submits the whole sitemap, which is what a site nobody has ever been told about needs
once.

### Discovery, which is the half no submission fixes

A crawler reaches a new site by following a link. These are the ones this project controls, and
each was empty on 2026-08-19:

- the **repository homepage field**, which is a link from github.com and is one click in repo
  settings. Not settable from a routine, no API tool here reaches it.
- the **README**, fixed the same day. The repo is public and github.com is crawled constantly.
- the **LinkedIn and Facebook profiles**, whose website field is the most direct link a brand
  owns. They are already in `sameAs` on every page, so the machine readable half of the loop
  was done and the human half was not.

`sameAs` pointing out at a profile that does not point back is half a loop. Both directions are
what tells an engine the profile and the site are one entity.