# WORKLOG — the hub pages and the homepage covers section

Actor: `human` (scripts/site/** and docs/** rebuild are human-owned in ownership.yaml).

## The ask (owner, 2026-08-18)

> it looks like the Texas page did not properly index data.. look at how the Alaska page did it
> https://alaskaaihq.com/topics/ Also on the homepage they have a What Alaska AI covers section
> (there's is great, make our homepage version take up less screen space but be no less robust)
> ... I'm thinking maybe this is part of the reason that we don't even show up on Google ...
> so look into how we can 10x our signal cause this DB is gonna keep growing

## What was ALREADY true, measured on current main (246be51)

A first pass diagnosed a stale checkout that was 107 commits behind and concluded the site had
no structured data and no custom domain. **Both were wrong.** Current main already ships:

- `SITE_URL = https://texasaidocket.com` and `docs/CNAME`. The live site serves there and
  github.io redirects to it. Canonicals are correct.
- `scripts/site/schema.py` (859 lines) plus `schema_check.py`. 666 Question/Answer, 61 FAQPage,
  76 BreadcrumbList, 54 GovernmentOrganization, 69 AdministrativeArea, 61 Report,
  15 CollectionPage, 15 ItemList across the built site.
- `indexnow.py`, `og.py`, 61 Markdown alternates, `llms-full.txt`.

So the entity layer is built. Do not rebuild it. **Record this so the next context does not
re-diagnose a solved problem.**

## The REAL gap: three page families have no hub, and nothing links to one

Measured with `find docs/<f> -mindepth 2 -name index.html` against `docs/<f>/index.html`:

| family | children | hub | inbound links to children |
|---|---|---|---|
| `/place/` | **73** | **MISSING** | 311, all from item pages |
| `/topic/` | **8** | **MISSING** | 80, all from the chip row |
| `/item/` | 61 | missing, but `/record/` lists all 61 and serves the role | 972 |

`/place/` is the biggest surface on the site and has no index at all. A reader cannot see the
geography of the record, and a crawler reaches those 73 pages only sideways from item pages or
from the sitemap. Sitemap-only pages get crawled slowly and rank badly. That is the honest
mechanism behind "we did not really index the data", and it matters more as the record grows,
which is exactly the owner's point.

The homepage has no covers section at all. Its `h2`s are Model in training, The latest video,
Where, The latest article, Closing next, What this is, Would AI actually help your business.

## Waves

| # | wave | status |
|---|---|---|
| 1 | Topic labels and blurbs as data, so a hub and a homepage card share one source | DONE |
| 2 | `/topic/` hub page, CollectionPage + ItemList + breadcrumbs | DONE |
| 3 | `/place/` hub page, grouped metro and county, same schema treatment | DONE |
| 4 | Homepage covers section, denser than Alaska's, linking both hubs | DONE |
| 5 | Sitemap, nav and internal linking so no hub is itself an orphan | DONE |
| 6 | All gates green, docs/ rebuilt, byte equality proven | DONE |

## What shipped, measured

Structured data nodes across the built site, before to after:

| node | before | after |
|---|---|---|
| `ListItem` | 225 | 734 |
| `BreadcrumbList` | 76 | 159 |
| `CollectionPage` | 15 | 98 |
| `ItemList` | 15 | 98 |

81 pages that carried only the boilerplate site node now carry a `CollectionPage` naming their
own children plus a `BreadcrumbList`. `collection_node` gained an optional `elements`, so an
`ItemList` says what is in it rather than only how big it is.

## The one thing that was nearly published false

The first cut of the hub card counted `public_access.room in (open_comment, open_meeting)` and
printed "18 still open to the public" on the data centers card. `room` records what KIND of
access a decision has and NOT whether it is still available, and one of those meetings had
closed five days before the build. The count asks `dk.window_state` now, which is the one
definition of open this site already had, and the per topic figures sum to exactly the 3 the
front page's own counter prints. A second definition of open would have been the real defect
even on a day the numbers happened to agree.

## Gates that must stay green

`numeral_lint` (every published numeral computed), `house_style_check`, `schema_check`,
`site_fresh_check` (rebuild into temp dir, prove byte equality), `ownership_check --actor human`.

House rules that bite this work: no colons or semicolons in published copy, comma construction
and density rules, no first person, "can't" never "cannot", ordinal dates month first, no em or
en dashes, ranges read "X to Y".
