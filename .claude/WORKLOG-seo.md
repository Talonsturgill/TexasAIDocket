# WORKLOG — AI SEO and the structured data spine

Started 2026-08-15. Owner asked for the sibling product's approach to AI SEO and to indexing data for models,
so the record wins the search battle, is highly discoverable to answer engines, and holds the
first page for Texas and AI queries. Called a massive task needing real effort and no
shortcuts. Follow-ups: "also like Data indexing", and "make our ai seo and all that stuff 10x
better", so the scope is every wave below rather than the first one.

Delete this file when the wrap tasks are all DONE.

---

## The finding that sets the scope

**Wave 3 is marked DONE in the task list and its structured data is a stub.** Every one of the
148 pages ships the same two boilerplate blocks and nothing else. This is not a small gap. It
is the single largest discoverability deficit the site has, and it is invisible from the page,
which is why it survived a wave being marked complete.

Measured 2026-08-15, both sites' built `docs/`.

| surface | sibling | here | note |
|---|---|---|---|
| distinct JSON-LD `@type` | **20** | **5** | and 3 of ours are one page's Dataset block |
| `FAQPage` | 21 | **0** | the single biggest AI answer surface |
| `Question` / `Answer` pairs | 208 / 208 | **0** | what feeds People Also Ask and AI Overviews |
| `NewsArticle` | 122 | **0** | |
| `BreadcrumbList` / `ListItem` | 69 / 196 | **0** | site hierarchy, shown in results |
| `Report` | 20 | **0** | the per-decision record with its citations |
| `GovernmentOrganization` | 22 | **0** | every decider is one and none is declared |
| `Dataset` | 44 | 3 | Google Dataset Search reads exactly this |
| og/twitter tags | 11 | **4** | **no `og:image` at all** |
| `llms-full.txt` | 350,825 B | **missing** | the whole corpus in one fetch |
| RSS `feed.xml` | present | **missing** | we ship Atom and JSON Feed only |
| `404.html` | present | **missing** | |
| IndexNow key + pusher | present | **missing** | |
| `/questions/` hub | present | **missing** | long-tail query surface |
| `/sources/` hub | present | **missing** | |
| sitemap URLs | 71 | **148** | ours is bigger, and it is the one thing that is |

**We are not behind on content. We are behind on machine-readable structure.** 58 items to the
sibling's 20, 148 pages to its 108, and a place taxonomy it does not have at all.

## Why this is winnable rather than aspirational

The Texas ledger is RICHER than the sibling's and every field a `Report` and an `FAQPage`
need is already in it, computed and fact-checked:

```
id  title  summary  topic  status  last_verified
decider      {name, type}                     -> GovernmentOrganization
geography    {statewide, counties[], metro, on_ercot}  -> Place, spatialCoverage
key_dates    [{date, kind, note}]             -> temporalCoverage, datePublished, event Q&A
public_access{room, how}                      -> the "can I comment" answer
claims       [{id, text, verbatim_quote, source_url, source_title, source_type, fetched}]
                                              -> citation[], and the proof behind every answer
```

234 claims across 58 items, each carrying a verbatim quote and a fetched source. The sibling
generates ten Q&A pairs per decision off a thinner record. **Nothing here needs new data. It
needs the data emitted.**

## The rule that governs every answer generated

An FAQ answer is PUBLISHED COPY. Every house rule applies to it: no first person, no colons
or semicolons, ordinal dates, the comma rules, and above all **every numeral computed, never
written.**

**The hole this opens, and it is a real one.** `house_style_check` strips `<script>` before
linting, deliberately, because the ask page ships its whole engine inline and a JS identifier
`i` was being read as a first-person pronoun. `numeral_lint` reads rendered copy. **So JSON-LD
is published prose that NO gate currently reads.** Emitting hundreds of generated sentences
into that blind spot would be the largest unlinted surface on the site.

So this work does not get to add the schema without also extending the lint to it. That is
task S2 and it is not optional, and it belongs in GATE_LESSONS when it lands.

## Scope, in waves. Each ends green on guards_local and is merged.

| # | wave | what lands |
|---|---|---|
| S1 | the schema spine | `scripts/site/schema.py`: Organization with a stable `@id`, `Report` per item with citation[] / spatialCoverage / temporalCoverage / mentions, `FAQPage` per item, `BreadcrumbList` on every page, `Dataset` + `DataDownload` on the data surfaces, `CollectionPage` on hubs |
| S2 | the lint that makes S1 safe | `schema_check.py`: every block parses, every claim in an answer traces to the record, no numeral that is not computed, no house-rule violation. Extends the numeral and style lints INTO JSON-LD |
| S3 | social cards | `og.py`: generated cards, no Pillow, same law as `favicon.py`. `og:image` with width/height/alt, `og:site_name`, `og:locale`, `twitter:card` |
| S4 | the corpus surfaces | `llms-full.txt`, RSS `feed.xml`, `404.html`, and `llms.txt` rebuilt with real sections and UNTRUNCATED descriptions (it currently cuts mid-word: "transmissio", "Dinosau") |
| S5 | answer hubs | `/questions/` and `/sources/` as generated views over the record, not doorway pages |
| S6 | submission | IndexNow key + pusher + workflow wiring |
| S7 | doctrine | `knowledge/shared/AI_SEO.md` so a later run keeps it, plus the GATE_LESSONS entry from S2 |

## Decisions taken, with the reason

**Q&A pairs are COMPUTED FROM THE RECORD, never written by a model.** Same law as every
numeral. The question set is a fixed list of shapes and each answer is assembled from named
fields. A model writing an answer would be writing a claim, and a claim needs a claim-id.

**No `NewsArticle` on item pages.** The sibling ships 122 because its item pages are articles.
Ours are a RECORD, and `Report` plus `Dataset` is the honest type for a tracked decision. A
decision page is not a news story and marking it as one to catch a rich result would be the
kind of small lie this project does not tell.

**`@id` anchors, so the graph joins up.** One Organization node at `/#org`, one Dataset node at
`/record/#dataset`, and every Report `isPartOf` that dataset with `author` and `publisher` as
`@id` references. Repeating the Organization object 151 times is what we do now and it builds
no graph at all.

## Gotchas paid for already

**A second session works this repo concurrently.** It landed the ask lane mid-flight today and
forced a conflict on #55. Merge main before starting each wave and expect `site_build.py` and
`docs/` to be contested.

**`docs/` is generated and byte-checked.** Every wave rebuilds and `site_fresh_check` must stay
green, so schema output has to be deterministic: sorted keys, stable ordering, no set iteration
order leaking into JSON.

**Run `guards_local.py`, not the self-tests.** That distinction cost a red build today and is
the reason the runner exists.

## Tasks

| # | task | status |
|---|---|---|
| S1 | `scripts/site/schema.py` + wire into `page()` | DONE. 5 types to 16, 633 Q&A pairs, 58 Reports, 0 dangling @ids |
| S2 | `schema_check.py`, numeral and style lints extended into JSON-LD | DONE. Proved red on the real artifact with 5 planted faults |
| S3 | `og.py` social cards | DONE, including per-decision cards. `truetype.py` reads glyph outlines out of the committed OFL fonts, so the headline is on the card with no dependency |
| S4 | llms-full.txt, feed.xml, 404.html, llms.txt rebuild | DONE. llms.txt 17k to 38k with real sections, truncation fixed |
| S5 | `/questions/` and `/sources/` | DONE. 633 answers on one hub, 95 documents from 49 publishers |
| S6 | IndexNow | DONE. Key file written by the build, fails soft, submits nothing from CI yet |
| S7 | `knowledge/shared/AI_SEO.md` + GATE_LESSONS entry | DONE |

### Wrap

| # | task | status |
|---|---|---|
| W1 | per-decision og cards carrying the headline | DONE |
| W2 | GATE_LESSONS entry for the unlinted JSON-LD surface | DONE, entry 33 |
| W3 | delete this file | TODO |
