# Sources field log — what a run actually saw

Append-only. A run adds to the bottom and never edits a line above it.

## Why this file exists rather than a run writing the registry

`SOURCES_REGISTRY.md` says which hosts are off limits. That list is the project's crawl boundary,
and **an unattended run that could edit its own boundary does not have one.** A run that hit a
disallow could delete the disallow and the fetch would then be compliant with a file it had just
rewritten. So the registry is `human` owned and stays that way.

The daily routine's Phase 17 also says, correctly, that a source which behaved differently than
the registry describes is knowledge the next run needs. Until 2026-08-16 those two rules
contradicted each other. The routine told a run to update the registry, the map refused the write,
and the run's four findings were saved only because it wrote them out longhand in its run record
and a maintainer pasted them across by hand. **A finding that survives only because somebody
remembered to copy it is a finding the machine loses.**

This file is the seam. A run appends what it observed and can never remove anything. A maintainer
reads the log, decides what is durable, and folds it up into the registry. Observation is separate
from law, and only the maintainer moves something from one to the other.

## What belongs here

- A host the registry does not list at all, with its robots position and the User-Agent that worked.
- A host that behaved differently than the registry says, in either direction.
- A robots.txt re-check, including one that came back exactly as recorded. A confirmation is worth
  writing down, because the registry's own standing rule is that robots policy is a snapshot rather
  than a law of nature.
- A tool-level failure that could be mistaken for a policy change. A 402 or a 403 is not a robots
  decision, and writing a host off on one is how a working source gets lost.

## What does NOT belong here

A disallow you would like to be different. That is not a field observation and there is nothing a
maintainer can do with it. **Never route around a disallow and never argue with one here.**

## Format

One block per finding, newest at the bottom.

```
### YYYY-MM-DD — host
- robots: what the file says, or that there is none
- fetch: what actually came back, and to which User-Agent
- so: the one line the next run needs
```

---

### 2026-08-16 — gov.texas.gov
- robots: serves no robots.txt at all
- fetch: 200 to a browser User-Agent, on both `/news/post/<slug>` and `/uploads/files/press/*.pdf`
- so: the most productive source of this run and absent from the registry. The directive letters
  under `/uploads/files/press/` carry the actual text, where the post carries a summary

### 2026-08-16 — lrl.texas.gov
- robots: content signals, no path disallow
- fetch: 200
- so: the Legislative Reference Library's weekly interim hearings post is the cheapest route to a
  dated public microphone, which is what the record promises a reader

### 2026-08-16 — courtlistener.com
- robots: registry says this host explicitly allows `claudebot`, and the policy has not changed
- fetch: CloudFront 403 to a ClaudeBot User-Agent, on `robots.txt` itself
- so: an edge failure, not a policy change. Do not write the host off on one 403

### 2026-08-16 — texreg.sos.state.tx.us
- robots: as recorded. Disallows FacebookExternalHit, bingbot, GPTBot, ChatGPT-User, OAI-SearchBot,
  Googlebot and AhrefsBot, with no `*` group
- fetch: not exercised this run
- so: confirmed rather than assumed, which is the point of re-checking per host

<!-- A run appends below this line. Never edit above it. -->

## 2026-08-18, the daily run

**`puc.texas.gov/agency/calendar/GetCalendarRss.aspx` returned HTTP 402.**
- registry says: `[V]`, keyless RSS with project numbers and hearing rooms, and it is named the
  highest value poll in the discovery phase
- fetch: 402 to the scout's client this run, so the calendar was not read at all
- note: 402 is the same status `interchange.puc.texas.gov` gives a bot User-Agent, and the fix
  there is a browser User-Agent. Worth testing whether the same fix applies to the calendar host
  before anybody concludes the feed is gone

**`interchange.puc.texas.gov` document fetch returned HTTP 503, twice.**
- registry says: `[V]` to a browser User-Agent, no robots.txt
- fetch: `Documents/55999_84_1445376.PDF` 503'd on two attempts, so the primary filing behind the
  ERCOT large-load verification numbers could not be read and those figures stayed on journalism
- so: a 503 is the host being unwell rather than a policy change. Not a blocked-list candidate

**`texasattorneygeneral.gov` returned HTTP 402 on two attempts.**
- registry says: no feed, and the host is otherwise undescribed
- fetch: 402, page never opened

**Three newsrooms 403'd a fetch this run:** `houstonpublicmedia.org` (two articles),
`khou.com`, `fortworthreport.org`, and `fortworthtexas.gov` (the city's own data center page).
- consequence worth recording: the Houston ISD start date, the AI platform branding and the
  assessment threshold all rested on the 403'd Houston Public Media articles, so they were held
  out of the claims rather than carried on a page nobody opened
- the standing rule on this page applies. A tool-level 403 is not a property of the source, and
  none of these belong on a blocked list without a retest from a second client

**`abc13.com` answered 200 and truncated its quotes to about 125 characters.**
- so: usable as a lead, useless as a verbatim source. An empty shell fails loudly, a truncated
  one does not, and a quote cut at 125 characters would have shipped as a real quote

**A dating trap worth naming.** A search for Texas Attorney General AI enforcement surfaces the
investigation of Meta AI Studio and Character.AI heavily, and it is dated **August 18th, 2025**,
not 2026. The source URLs carry `/2025/08/18/`. An anniversary reads as news to a search ranker,
and the year is the only thing that distinguishes them.

## 2026-08-18, second pass, the re-verification that cleared the new two day leash

**`puc.texas.gov/agency/calendar/GetCalendarRss.aspx` answered 200 to curl with a browser
User-Agent**, the same host and path that returned 402 to the scout's client earlier the same
day. 12,722 bytes of real RSS, 31 open meetings from August 14th, 2026 to July 29th, 2027.
- so: the 402 recorded earlier today belonged to the fetching client, not to the host. This is
  the registry's own standing rule reproducing itself, that a tool-level failure is not a
  property of the source, and it is now the second time this project has nearly written off a
  working feed on one client's status code
- the compliant move is unchanged. `puc.texas.gov/robots.txt` is `User-agent: * Allow: /`

**`tcss.legis.texas.gov` serves NO robots.txt**, 404 with a zero byte body, and answers a
browser User-Agent with full statute text. BC.552 28,877 bytes, UT.39 635,739, GV.2054 480,543.
- this is where Texas statute text is actually fetchable. `statutes.capitol.texas.gov` is a
  JavaScript application that serves its own HTML shell for `/robots.txt`, so it is not a
  useful fetch target and `tcss.legis.texas.gov` is

**`interchange.puc.texas.gov` answered 200 to a browser User-Agent**, 1,398,029 bytes for
docket 59315. It had 503'd twice earlier today.
- so: the earlier 503 was the host being unwell for a moment, not a policy change, and the
  browser UA rule in the registry still holds

**A QUOTE FIDELITY TRAP, and it is in the statute text itself.** Texas statute pages write a
bill citation with a space before the closing parenthesis, `(H.B. 149 )` and `(S.B. 1964 )`.
A stored quote that tidied that to `(H.B. 149)` no longer matches the source. One item here
had the tidied form and one had the faithful one, which is how it was noticed at all.

**AN RSS DESCRIPTION IS DOUBLE ESCAPED.** The PUCT calendar feed carries markup inside its
`<description>`, escaped, so a verifier that strips tags BEFORE unescaping sees
`&lt;strong&gt;` as visible text and a correct quote reads as missing. Unescape first, then
strip. This produced one false negative in today's check and would produce one every run.

---

## 2026-08-19, the daily run

**THE STANDING RULE FIRED FOR A THIRD TIME, AND THIS RUN NEARLY FILED FOUR ITEMS ON IT.**
`interchange.puc.texas.gov` and `puc.texas.gov/agency/calendar/GetCalendarRss.aspx` both returned
**HTTP 503 to every WebFetch attempt** across this whole run, and to the scout's attempts before
that. Four items were written up as unconfirmed on the strength of it.

Retested with `curl` and a browser User-Agent, per this file's own entry from 2026-08-16:

| url | WebFetch | curl, browser UA |
|---|---|---|
| `puc.texas.gov/agency/calendar/GetCalendarRss.aspx` | 503 | **200, 12,722 bytes, 32 items** |
| `interchange.puc.texas.gov` control 58000 | 503 | **200, 60,737 bytes, 67 filings** |
| `interchange.puc.texas.gov` control 58482 | 503 | **200, 37,109 bytes, 34 filings** |
| `interchange.puc.texas.gov` control 59315 | 503 | **200, 1,398,029 bytes, 2,000 filings** |

- the calendar needs `-L`. It 301s from `GetCalendarRss.aspx` to the lowercased path, and a client
  that does not follow the redirect sees 180 bytes and concludes nothing is there
- so: three different status codes have now been recorded against these hosts by three different
  clients on three different days, 402, 503 and 200, and the host was serving on all three. **The
  status code a fetch returns is a fact about the fetcher.** Retest before writing anything down
- what it was worth: four items moved from unconfirmed to verified, and Project 58482 turned out to
  have taken a comment on August 18th that would otherwise have gone unrecorded

**`www.federalregister.gov` HTML now 302s to `unblock.federalregister.gov`** for document pages,
which is a bot wall rather than a redirect worth following.
- the API is unaffected. `federalregister.gov/api/v1/documents.json` answers fully, takes
  `conditions[term]`, `conditions[comment_date][gte]` and a `fields[]` list, and returns
  `comments_close_on` directly
- so: **query the API and never the document page.** Two items were verified this way after the
  HTML route failed

**`tcss.legis.texas.gov/resources/GV/htm/GV.2054.htm` is served in full but arrives truncated.**
A fetch of Chapter 2054 stops at Section 2054.0702, which is short of all three Subchapter S
enactments, so the AI provisions this record rests on sit past the cut.
- a run re-verifying `tx-2026-0008` or `tx-2026-0025` from that URL will appear to find that
  Subchapter S does not exist. It does. The file is roughly 480 KB and the retrieval is the limit
- do not conclude from a truncated fetch that a provision was repealed

**`webapi.legistar.com` is the route into any Legistar city, and the HTML calendar is not.**
Legistar HTML calendars publish meeting dates and no item text, so nine items were left partly
unconfirmed before this was tried. The Web API serves the item text as JSON.
- `webapi.legistar.com/v1/<tenant>/matters?$filter=MatterIntroDate+gt+datetime'YYYY-MM-DD'&$orderby=MatterIntroDate+desc&$top=40`
- confirmed tenants: `leaguecity`, `brazoriacountytx`, `elpasotexas`, `denton-tx`, `cityofdallas`.
  A scout recorded HTTP 500 for every Fort Worth tenant name tried
- **`MatterStatusName` AND `MatterPassedDate` ARE NOT EVIDENCE.** Both El Paso items read
  "Agenda Ready" with a null passed date, which is the exact shape that flagged the Houston ISD
  board policy last run. `/v1/<tenant>/Matters/<id>/Histories` carries the actual motion, the
  second, the action date and a `PassedFlag`. Both El Paso items show `PassedFlag` 1. **This run
  came close to writing down two correct items as overstated on the strength of a workflow field**

**Hosts that refused this run**, each retried at least twice and none routed around.

- `www.usda.gov` 403 on every path including the August 11th press release. `aphis.usda.gov` served
  normally, so the screwworm material is reachable and the department's own releases are not
- `hhs.texas.gov` and `pfd.hhs.texas.gov` 403 including on `robots.txt`. This blocks the Rural
  Health Transformation Program and its Lone Star Advanced AI and Telehealth initiative, which is a
  statewide state-run AI procurement and the largest unworked lead this run produced
- `texasattorneygeneral.gov` 402 on the press release index
- `www.fortworthtexas.gov` 403 on `/` and on `/robots.txt`, so the host's own policy could not be
  read. `apps.fortworthtexas.gov` and `fortworth.granicus.com` both 404. No Fort Worth primary
  document was reachable by any route tried, which left a real August 11th council action on
  journalism alone
- `hpcwire.com`, `texasmonthly.com`, `beckershospitalreview.com`, `fortworthreport.org`,
  `houstonpublicmedia.org` all 403
- `assets-ir.tesla.com` 403 and `digitalassets.tesla.com` 404
- `www.brazoscountytx.gov` timed out at 60 seconds twice

**A PDF is read as a document or it is not read.** The Governor's directive letter answered 200 at
153 KB and the fetch tool's text extractor refused it. Read as a binary it yielded both a text
layer and rendered pages, which is the only reason this run can be exact about the 474 figure.
- and the figure is worth the trouble. **The signed letter says "approximately 474 gigawatts". The
  press release from the same office on the same day says "approximately over 474 gigawatts".**
  The letter is the primary document and its wording is the one to publish
- the same letter writes **PUC** throughout where the press release writes **PUCT**, and its
  information bullets end with a semicolon and the word "and" where the release drops them. A quote
  carries whichever form its own source uses

**A FETCH SUMMARY IS NOT A QUOTE, AND THIS BIT TWICE.** A scout recorded that two passes over one
`nsf.gov` page returned two different sentences attributed to the same speaker, meaning the
retrieval paraphrased on at least one pass. It excluded every quote from that page rather than
publish one.
- the fact checker hit the same thing on `ercot.com`, where a first pass returned a summary and a
  second pass with an explicit transcription instruction returned the body verbatim
- so: **a quote is verified by a fetch that was asked to transcribe, not by one that was asked what
  a page says.** Ask twice and compare when a numeral or a quote is going to be published

---

## August 20th, 2026

**`puc.texas.gov` 402s a default agent, and the registry only said that about the Interchange.**
`GetCalendarRss.aspx` returned 402 to the fetch tool and 200 to a browser User-Agent. The registry
carries the 402 finding for `interchange.puc.texas.gov` and not for the main `puc.texas.gov` host.
Both behave the same way.
- **the RSS url also 301s**, from `GetCalendarRss.aspx` to the lowercase `getcalendarrss.aspx`. A
  fetch that does not follow redirects gets 180 bytes and no feed. Follow it.

**THE CALENDAR FEED NEVER NAMES A DOCKET, FOR ANY ENTRY, AND THIS COST A WRONG PUBLIC FACT.** The
`<description>` of a PUCT calendar entry carries the room and whether it is public. That is all it
has ever carried. A previous run read the absence of a docket number from the August 21st entry as
the docket having come off the agenda and published that, when the docket was item 3 on the agenda
the entry links.
- **the agenda is one click away and is where the matters live.** Each `AppointmentDetail.aspx`
  page carries an `[Agenda]` link to a PDF at `ftp.puc.texas.gov/public/puct-info/agency/om/`,
  named `MMDDYYFinal.pdf`. It lists every docket and project number, who is presenting, which items
  are taken up without discussion and which will not be taken up at all
- that PDF answered 200 to a browser User-Agent and extracted cleanly with `pypdf`

**The Interchange filing index reports the true count and renders only the first page of rows.**
Docket 59315 reports 5793 filings and the web view returned 2000 rows across three pages. A count
taken from the rows understates the docket by a factor. **Quote the index line, never count the
table.** A previous run published 2,000 as though it were the filing count.

**`capitol.texas.gov` hearing notices are the cheapest primary source in this repo.** Both the HTML
form at `/tlodocs/89R/schedules/html/<code>.htm` and the PDF at `/tlodocs/89R/schedules/pdf/<code>.PDF`
answered 200 to a browser User-Agent. They carry the committee, the chair, the room, the time,
every interim charge in full, whether testimony is invited only or public, the per witness time
limit and the electronic comment url. A whole item can be built from one of them.

**`lagovistatexas.gov` is the dot gov, and `lagovistatexas.org` does not resolve.** Its CivicPlus
AgendaCenter served 2023 agendas only and its search returned nothing for a term that is in the
news, so **no 2026 minutes or agendas appear to be published there**. A council vote covered by
four outlets could not be sourced to the city that took it.

**`leaguecitytx.gov` publishes ballot language on its news page, verbatim.**
`/m/newsflash/Home/Detail/<id>` answered 200 to a browser User-Agent and carried the full
proposition text. **It spells nonbinding as one word where every outlet covering it wrote
non-binding.** That is the reason to fetch the city rather than the coverage.

**`legistar1.granicus.com` attachment PDFs are primary and extract cleanly.** A city's charter
review commission report, filed with the ordinance, carried the full proposed charter text.

**Hosts that refused this run, recorded as observation only.** `usda.gov` returned 403 on three
attempts to a scout. `fortworthreport.org`, `texastribune.org`, `kxan.com` and `newsradioklbj.com`
returned 403 to a default agent. `globenewswire.com` and `investors.kodiak.ai` returned 503.
`tacc.utexas.edu` returned 403, and that one is **a disallow rather than a failure**, recorded in
the registry, and was not routed around.
