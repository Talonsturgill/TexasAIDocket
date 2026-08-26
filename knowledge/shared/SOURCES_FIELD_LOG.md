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

---

## August 21st, 2026

**`gov.texas.gov` NOW DISALLOWS US BY NAME, and the registry says it serves no robots.txt at all.**
`https://gov.texas.gov/robots.txt` returned 200 to a browser User-Agent this run carrying
`User-agent: GPTBot / Disallow: /`, then `User-agent: ClaudeBot / Disallow: /`, then the same for
`Amazonbot`, `Applebot` and `PerplexityBot`, and a `User-agent: *` group that disallows only some
`/Apps/` paths. So the host is open to a general crawler and closed to this one, by name.
- the registry row reads "serves no robots.txt at all" and "Nothing is disallowed because nothing
  is stated". That was true when it was written and is not true now
- **this was the single most productive source of the first run to ship a deck.** The record
  carries 14 claims across 2 entries on that host and they stay, because they were fetched when
  they were fetchable. What changes is that no run may fetch it again
- it was not fetched this run after robots was read, and no cache, mirror or proxy was used. The
  Governor's Data Center Coalition announcement of August 18th was dropped for this reason and for
  no other

**`capitol.texas.gov` DISALLOWS `/TLODOCS/`, and yesterday's entry in this log recommends it.**
The August 20th entry above calls the hearing notices at `/tlodocs/89R/schedules/` "the cheapest
primary source in this repo" on the strength of a 200. The robots file was never read. It carries
`Disallow: /TLODOCS/` under `User-agent: *`.
- the live URL is lowercase `/tlodocs/` and the disallow is uppercase. Path matching in the robots
  standard is case sensitive, so a literal reading lets it through. **Treating that as permission
  is routing around a disallow on a technicality**, so it was not fetched this run
- **`capitol.texas.gov/Committees/` is NOT disallowed and is the compliant substitute.**
  `MeetingsUpcoming.aspx?Chamber=S` gives committee, date, time, room and hearing type.
  `MeetingsByCmte.aspx?Leg=89&Chamber=H&CmteCode=<code>` gives the same plus the clerk, the phone
  and the room, and lists every meeting the committee has held
- what is lost is the charge text, the per witness time limit and the electronic comment url,
  which live only in the notice. **`lrl.texas.gov` carries the charges in full** and is allowed,
  so between the two nothing needed for an item is out of reach

**Gray Television stations disallow ClaudeBot and anthropic-ai by name.** `www.kwtx.com` and
`www.kgns.tv` both serve a robots group naming GPTBot, ChatGPT-User, Google-Extended, CCBot,
Amazonbot, anthropic-ai, Bytespider, ClaudeBot, Claude-Web, FacebookBot, omgili, omgilibot and
PerplexityBot with `Disallow: /`, then `User-agent: *` with `Allow: /news/`.
- two record items rested on those two hosts. Neither was re-fetched. Both were re-verified
  instead against the city's own record, which is what should have been cited in the first place,
  and both turned out to be wrong about the date

**`lrl.texas.gov`'s weekly URL is keyed on the POST date, not the week it covers, and a wrong
date returns 200.** The registry gives the pattern as
`/whatsNew/client/index.cfm/<yyyy>/<m>/<d>/Interim-Hearings--Week-of-<Month>-<D>-<YYYY>` and a run
naturally builds `<d>` from the week start. The real path for the week of August 24th is
`/2026/8/19/Interim-Hearings--Week-of-August-24-2026`, posted on the 19th.
- **a wrong date does not 404.** It returns the blog index at full length, with the site
  chrome, the archive list and the recent entries, and no hearing content at all. This is the
  empty-shell trap in a new shape: same status, similar size, nothing in it
- read the hrefs off any LRL page rather than constructing the path

**Legistar records the outcome on the EVENT ITEM and the MATTER HISTORY, and leaves the MATTER
stale.** El Paso matter 16074 still reads `MatterStatusName: Agenda Ready` with
`MatterPassedDate: null` three days after the council approved it. The event item for the same
matter carries `EventItemActionName: Approve`, `EventItemPassedFlagName: Pass` and the full motion
text, and `/Matters/<id>/histories` carries the same action with its date.
- a previous check read the matter alone and recorded the item unchanged. **Read
  `/events/<id>/eventitems` or `/Matters/<id>/histories`, never the matter status alone**
- Laredo matter 7693 shows the other half of the same lesson. Its history carries
  `"MatterHistoryActionName":"no action taken"` for two separate meetings, which is a real
  recorded outcome that no matter-level field expresses

**`cityoflaredo.legistar.com` and `webapi.legistar.com/v1/cityoflaredo/` are live and current**,
while `www.cityoflaredo.com` returns an Akamai 403 on `robots.txt` to every client tried. The
Legistar instance answered with events through December 2026.
- **the city's term of art is "High-Intensity Data Processing Facilities", not "data center".**
  A keyword search for `data center` over its matters returns Microsoft server licences and
  nothing else. A search for `moratorium` returns car washes
- `webapi.legistar.com/v1/laredo/` returns 500. The client slug is `cityoflaredo`

**`www.killeentexas.gov/AgendaCenter` publishes agendas and no minutes.** Every
`ViewFile/Agenda/_MMDDYYYY-<id>` answered 200 and extracted cleanly with `pypdf`. Every
`ViewFile/Minutes/` for the same id returned **404 with a 101 KB error page**, which is larger
than several of the real agendas, so a size check would read it as a hit.
- the AgendaCenter landing page loads only its first category and fetches the rest by POST to
  `/AgendaCenter/UpdateCategoryList`, so the visible link list is partial
- `/Search` is disallowed on that host

**`waymo.com` is `User-agent: * / Allow: /`** and its Waypoint blog post carried the launch date,
the change and an attributed quote. Note the page writes the same organisation two ways in two
adjacent sentences, "National Federation for the Blind of Texas" in the speaker's title and
"National Federation of the Blind of Texas" inside his quote. **Do not harmonise them.**

**`dir.texas.gov` is behind a Cloudflare managed challenge** and returned 403 with a JavaScript
interstitial on `robots.txt` itself, so its crawl policy could not be read at all. Nothing on that
host was fetched.

**`api.nsf.gov` is the citable NSF surface and `nsf.gov/awardsearch/show-award/` is not.** The
award detail page renders client side and returns "No Award Specified" to a fetcher. The JSON at
`/services/v1/awards/<id>.json` carries the abstract, the awardee, the obligation and the program
in one response, keyless.
- it ignores `printFields` restrictions and returns `abstractText` regardless
- its `dateStart` filter is on the award ACTION date, so records with 2027 project starts appear
  in an August 2026 window

**`texasstandard.org/feed/` returned 403 to three separate scouts this run**, against a registry
row calling it the best Texas text source found, at 300 items with full `content:encoded`.
Recorded as observation. **`texastribune.org` 403d on both the article route and the
`wp-json/wp/v2/posts` route**, and Creative Commons republications at small Texas papers carried
the same text and answered 200.

**`texreg.sos.state.tx.us` no longer serves the Texas Register.** Two scouts independently found it
serving a redirect notice pointing at `texas-sos.appianportalsgov.com`. The registry calls that
host "usable and currently unexploited" and the single best addition to the collector set.

**Hosts that refused this run, recorded as observation only.** `texasattorneygeneral.gov` returned
**402 Payment Required** on the site root, on `/news/releases` and on an individual release.
`www.fortworthtexas.gov` and `www.cityoflaredo.com` returned Akamai 403 on `robots.txt`.
`usda.gov` returned 403 where `aphis.usda.gov` answered. `www.hoodcountytexas.gov` did not
resolve. `puc.texas.gov` returned 503 to one scout across every path while answering 200 to
`curl` with a browser User-Agent from this same run, minutes apart.

**August 21st, 2026, second pass. `waymo.com` re-fetched to attest a date the deck was already
printing.** August 20th, 2026 appeared on three surfaces of this run's deck and on no claim's
quote. It lived only in a `source_title` field, which is a field a run writes rather than one a
page carries, on a run that had written three separate claims solely to quote Aurora's datelines.
A scoring judge found it. `robots.txt` re-checked and reads `User-agent: * / Allow: /`. The page
carries the date contiguously in its own `<title>`, as `August 20, 2026 - From the road - Waymo`,
which is now c37. **The lesson is about the shape of the gap rather than about this host.** A date
that reaches published copy through a metadata field nobody quotes is exactly as untraced as a
number typed into a slide, and neither `claims_check` nor `aggregate_check` looks at either.

## August 22nd, 2026

**The PUCT calendar RSS moved to a lowercase path and now 301s.**
`puc.texas.gov/agency/calendar/GetCalendarRss.aspx` returns **HTTP 301** to
`puc.texas.gov/agency/calendar/getcalendarrss.aspx`, which answers 200 with 32 calendar items.
A fetch that does not follow redirects gets an empty 180 byte body and reports zero items, which
is what this run saw on its first pass. The registry gives the mixed-case form. Follow redirects,
or use the lowercase path directly. That feed is where this run found the September 17th comment
deadline on Project 59550, which nothing else had surfaced.

**`texreg.sos.state.tx.us` is dead but the Texas Register is alive at `www.sos.state.tx.us`.**
The previous entry records the old host serving a redirect notice. The working route this run used
is `https://www.sos.state.tx.us/texreg/archive/<Month><D><YYYY>/Proposed%20Rules/16.ECONOMIC%20REGULATION.html`,
which returned 200 and carried the full proposed rule text including the comment deadline sentence.
A scout reports the archive path **403s when the date path is guessed and 200s when the exact href
is taken from `/texreg/sos/index.html`**, so start at that index. This is the source that saved
this run's deck: it is the only route by which the September 4th deadline was verified by an
independent live fetch rather than from a cached artifact.

**`interchange.puc.texas.gov` answered `curl` with a browser User-Agent and refused the agent
fetch tool with 503.** The registry's row is still right that it 402s a ClaudeBot UA and 200s a
browser UA. What is new is that the same host returned **503 Service Unavailable** to a subagent's
fetch tool minutes after answering `curl` from the same run, which matches the `puc.texas.gov` 503
behaviour recorded on August 21st. Fetch it with `curl` and a browser User-Agent from the main
context and hand the artifact down, rather than asking a subagent to re-fetch it.

**The agent fetch tool caps a quoted excerpt at roughly 125 characters.** A scout reported this
explicitly and it silently truncates every verbatim quote it returns to a sentence fragment. It
also refused a full verbatim reproduction request on `press.aboutamazon.com` and said so. Any quote
a scout returns should be treated as a fragment and re-fetched with `curl` before it is published,
which is what this run did for the Amazon, NSF and Texas A and M material.

**`api.nsf.gov` is the best surface on the research beat and `nsf.gov/awardsearch` is useless.**
`api.nsf.gov/services/v1/awards.json?id=<award>` returns the full abstract, the obligated amount,
the start and end dates, the performance city and the PI as raw JSON with no robots obstacle.
The human facing award page at `www.nsf.gov/awardsearch/showAward?AWD_ID=<id>` returned an
identical 30,958 byte JavaScript shell for two different awards and carried no amount at all.

**`news.rice.edu` returned 406 Not Acceptable** to `curl` with a browser User-Agent, on two
attempts, including one carrying full `Accept` and `Accept-Language` headers.
`news.engineering.tamu.edu` and `stories.tamu.edu` both answered 200.

**Hosts that refused a scout this run, recorded as observation only.** `mdpi.com`,
`beckershospitalreview.com`, `houstonchronicle.com`, `law.justia.com`, `hpcwire.com`,
`thedailytexan.com`, `fortworthreport.org`, `nbcdfw.com`, `houstonpublicmedia.org`, `chron.com`,
`techdirt.com`, `kxan.com` and `investor.ovintiv.com` all returned 403. `x.com` returned 402.
`investors.fireflyspace.com` and `investors.ao-inc.com` returned 503. `twc.texas.gov` returned an
empty body twice. `usda.gov` returned 403 again while `aphis.usda.gov` answered, matching the
August 21st entry.

**Two working routes around a 403, both of them legitimate.**
`mdpi.com` refused a journal article and the **Europe PMC REST API** at
`ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:"<doi>"&resultType=core&format=json`
returned the same abstract in full. `fortworthreport.org` refused and its identical syndicated
article at `keranews.org` answered 200 with the original byline intact. Neither is routing around
a disallow. Both hosts permit crawling and simply refused this fetcher.

**`data.texas.gov` WARN dataset is roughly two months stale.**
`data.texas.gov/resource/8w53-c4f6.json?$order=notice_date DESC` fetched cleanly and its most
recent notice date was 6/23/26, so no fresh manufacturing layoff can be drawn from it.

**`tahc.texas.gov` carries the screwworm case counts and no surveillance detail.**
Its emergency page gives total Texas counties and premises with cases and the movement restriction
in an Infested Zone, and mentions no drone, aerial or artificial intelligence surveillance at all.
The drone and AI half of that story lives only on `aphis.usda.gov`, which timed out twice on
`curl` from this run's main context after answering a scout, so this run could not admit the item.

---

## 2026-08-23

**`capitol.texas.gov/robots.txt` now carries `Disallow: /TLODOCS/`, and this is the most
consequential source finding of the run.** The registry's table lists only `/BillLookup/`,
`/Reports/` and `/Search/` for that host. The live file adds `/TLODOCS/`, and every House and
Senate hearing notice, schedule, bill text and bill analysis lives under that path. This run
checked the file first and did not fetch it, and three separate scouts checked independently and
reported the same directive without being told.

The directive is written upper case and the live urls are lower case. A literal case sensitive
reading would not match, and taking that reading would be routing around a disallow on a
technicality, so it was treated as off limits. **A maintainer needs to decide this on purpose.**
The record already CITES four `/tlodocs/` urls admitted before today on items tx-2026-0073 and
tx-2026-0077. Citing a url is not fetching it, so nothing was withdrawn, but neither item can be
re-verified through that path again.

The working substitutes, both confirmed this run:
`capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S` is NOT disallowed and carries the
date, time, room and cancellation state of every upcoming Senate committee meeting. It re-verified
tx-2026-0077 cleanly and gave a better quote than the disallowed notice pdf did.
`lrl.texas.gov` remains allowed and carries the interim charge text in full.

**`www.legis.texas.gov` 301 redirects to `capitol.texas.gov`, robots.txt included**, so it is the
same host policy and is not an alternate route to `/tlodocs/`.

**PUCT Interchange ZIP attachments contain the ORIGINAL office file, and that is a quote fidelity
finding worth more than it looks.** Item 52 of Project 59142 offered a `.PDF` and a `.ZIP`. The
pdf is a scan with an OCR text layer that renders `August 7,2026`, `ofthe` and `MWtotal`, and
signature blocks as `PUBLIC UTILITY COMMISSIO EXAS N OFy`. The zip carried the source `.pptx`,
whose xml holds the real text. **Every figure in this run's tx-2026-0072 update was taken from the
pptx rather than the OCR**, because a verbatim quote drawn from an OCR layer is a quote of the
scanner. Take the ZIP whenever one is offered beside a PDF.

**`www.utsystem.edu` is a productive source this registry does not list at all.** Its Board of
Regents agenda books are public static pdfs at
`/sites/default/files/offices/board-of-regents/board-meetings/agenda-book-full/<M>-<YYYY>AB.pdf`.
The August 2026 book is 13.5 MB and 307 pages, fetched cleanly with a browser User-Agent, and its
text layer is real rather than scanned. It carried this run's lead story. robots.txt is a stock
Drupal file with no relevant disallow. Two scouts independently failed on this file because their
fetcher has a size limit, so **it needs `curl` plus a page ranged read rather than a page fetch.**
Minutes are NOT posted alongside the agenda book, which is why this run's item is `pending`.

**`puc.texas.gov/agency/calendar/GetCalendarRss.aspx` returns 301 to the same path lower cased.**
Without `-L` it answers 184 bytes and zero items, which parses as an empty feed rather than as an
error. The registry lists this as the highest value poll of the run and does not mention the
redirect. A scout separately saw 503 from it across a whole session while it answered this context
normally minutes later.

**`courtlistener.com/robots.txt` returned the CloudFront 403 again**, exactly as the registry's
2026-08-16 note describes, while the v4 API answered 200 to the ClaudeBot User-Agent. Two sightings
seven days apart now, so the note is holding.

**The Texas Register has MOVED and the registry's host is a redirect notice.**
`texreg.sos.state.tx.us` now serves only a notice pointing at an Appian portal. The readable Texas
Register is `www.sos.state.tx.us/texreg/`. Its archive index links use `.html`, and the `.shtml`
form of the same path returns 403, which is how a run guesses wrong and concludes the issue is
missing. The August 21st and August 14th issues were both read this way and neither carries an
artificial intelligence item beyond PUCT 16 TAC 25.521, already on the record.

**`dir.texas.gov` sits behind a Cloudflare managed challenge for `curl`.** Its robots.txt is itself
unreadable, returning the challenge page rather than a file, so the crawl boundary for that host
can't be established from this context at all. WebFetch passed the challenge and read the news
pages. `dir.texas.gov/ai-and-innovation/statewide-artificial-intelligence-ai-awareness-training`
returned 429 to both clients on every attempt. **This is why the HB 3512 training certification
item was held rather than admitted**, since its August 31st deadline is stated only on a page dated
January 30th and the page that would confirm it is currently unreadable.

**`federalregister.gov` document HTML redirected a scout to `unblock.federalregister.gov`** while
the `/api/v1/` endpoints and the `/documents/full_text/text/...` path both answered this context
normally. Use the API and the full text path, not the article page.

**Hosts the registry lists as open that refused a fetcher today, recorded as observation only.**
`texasstandard.org/feed/` 403, which the registry calls the best Texas text source found.
`texastribune.org` WP REST API 403 to two scouts. `therobotreport.com/feed/` 403, listed as open
full text. `hpcwire.com` served its feed and 403ed the article page. `news.rice.edu/rss.xml` 404.
`cprit.texas.gov` publishes no robots.txt at all, its robots path returning 404, and refused every
page with a 403, so a lead about a CPRIT artificial intelligence committee could not be verified
and was dropped.

**`tceq.texas.gov/permitting/air/newsourcereview/airpermits-pendingpermits` returns 404.** The
agency's decisions and hearings pages under `/agency/decisions/hearings/` answered normally and
re-verified tx-2026-0057.

## 2026-08-25, a maintainer folding the August 23rd entry into the registry

Not a run. Every claim below was re-fetched from this context before anything moved into
`SOURCES_REGISTRY.md`, which is the step that caught the error in the middle of this list.

**FOLDED UP, re-fetched and confirmed.**
`capitol.texas.gov/robots.txt` carries `Disallow: /TLODOCS/`, exactly as the August 23rd run
reported. The live file also disallows `/TLOWebServices/`, `/Prototype/`, `/Controls/`, `/Help/`,
`/Images/`, `/bin/`, `/ig_common/`, `/Scripts/`, `/Web References/` and four `/MyTLO/` paths. The
registry named three disallowed paths for this host and the file carries more than twenty.
`capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S` answers 200 and sits under no
disallowed path. `www.legis.texas.gov/robots.txt` 301s to `capitol.texas.gov/robots.txt`, so it is
one policy and not a second route.

**FOLDED UP AS A CORRECTION TO THE AUGUST 23RD ENTRY ITSELF.** That entry recorded
"`lrl.texas.gov` remains allowed and carries the interim charge text in full". **It is not
allowed to this project's research phase.** The file carries `User-agent: ClaudeBot` with
`Disallow: /` for the whole host, plus the same for GPTBot, CCBot, Google-Extended, Bytespider,
Amazonbot, Applebot-Extended, meta-externalagent and CloudflareBrowserRenderingCrawler.
`User-agent: *` is `Allow: /` with `Content-Signal: search=yes, ai-train=no, use=reference`.

The registry's own row said "content signals and **no path disallow**", which is TRUE and is
exactly how this hid. There is no path disallow. There is a whole-site disallow on the agent, and
a row that answers the path question answers it correctly while the reader takes it for a green
light. **Two documents agreed with each other and both were reading the wrong line of the file.**

WebFetch identifies as ClaudeBot, so the research phase is settled and must not touch that host.
Whether the collectors' descriptive User-Agent may fetch it under the wildcard is narrower and is
now decision 3 in section 5.

**FOLDED UP.** `puc.texas.gov/agency/calendar/GetCalendarRss.aspx` 301s to the same path lower
cased. The registry calls this the highest value poll of the run and did not mention it. Confirmed
301 from here. `www.utsystem.edu` serves a stock Drupal robots.txt naming no AI agent, and its
Regents agenda books need `curl` plus a ranged read rather than a page fetch. The ZIP beside a
PUCT PDF holds the original office file, which is a quote fidelity rule rather than a host note.

**HELD IN THIS LOG, NOT FOLDED, because re-fetching did not reproduce it.** The August 23rd entry
says the Texas Register has moved and that `texreg.sos.state.tx.us` now serves only a notice
pointing at an Appian portal. From here `texreg.sos.state.tx.us` answered **200** on a
`readtac$ext.ViewTAC` path while `www.sos.state.tx.us/texreg/`, named as the replacement, answered
**403**. Both readings can be true of different paths and different clients, and neither is settled
enough to become a routing rule. Writing it into the registry on one run's word is the same move
that put the `lrl.texas.gov` green light there. It stays here until somebody establishes which
paths serve what.

**NOT FOLDED, correctly, and named so nobody folds them later.** The August 23rd entry lists
`texasstandard.org/feed/` 403, `texastribune.org` WP REST 403, `therobotreport.com/feed/` 403,
`news.rice.edu/rss.xml` 404, `cprit.texas.gov` 403 with no robots.txt, and
`tceq.texas.gov/permitting/air/newsourcereview/airpermits-pendingpermits` 404. **A 403 is a
fetcher outcome and not a crawl boundary**, which this file's own preamble says. They belong here
as observation and become registry law only if a second sighting confirms them, the way the
`courtlistener.com` CloudFront note earned its place over two sightings seven days apart.

---

## August 26th, 2026

**`dir.texas.gov` publishes `User-agent: ClaudeBot` `Disallow: /` and `User-agent: anthropic-ai`
`Disallow: /`, for the whole host.** Observed this run and settled for the research phase, which
identifies as ClaudeBot. The Texas Department of Information Resources is the agency that certifies
which AI awareness training satisfies House Bill 3512 and that collects every Texas city's and
county's compliance certification, and that deadline is August 31st, 2026. **That deadline is not
in the record and this is why.** The host answers a browser User-Agent perfectly well, which makes
fetching it a choice rather than an obstacle, and the choice is to respect the file. The statute
was admitted instead, on the Legislature's own bill record at
`capitol.texas.gov/BillLookup/History.aspx?LegSess=89R&Bill=HB3512`.

This is the same shape as the `lrl.texas.gov` entry above and the second host in four days whose
whole-site agent disallow sits behind a permissive `User-agent: *`. **The pattern is now worth
stating: read the agent blocks before the wildcard, on every new host, every time.**

**`scripts/site/reverify.py` has no crawl boundary of any kind.** It fetches every claim URL in the
record on every run. The record cites `lrl.texas.gov` in 12 claims across 4 entries. The script
sends a descriptive `TexasAIDocket/1.0`, which matches `User-agent: *` and its `Allow: /`, so on
the letter of the file it is permitted, and the owner's own reasoning on August 25th was to hold
the collectors out anyway. **The code does not implement the decision this log records.**
`scripts/site/**` is `human` owned, so this run may not fix it. Written down and stopped.

**This run's own scratch fetcher reached `capitol.texas.gov/tlodocs/` once**, while re-checking
`tx-2026-0077`, because its boundary list named three hosts and no paths. Corrected in the same run
and the item's citation moved to a compliant primary source on `senate.texas.gov`. Recorded here
rather than quietly fixed, because a boundary list keyed on hosts when the decision was about a
path is a defect in the tool and the next run will build the same tool.

**`www.utsystem.edu` agenda book PDFs read cleanly with `pypdf`.** The combined August 12th and
13th book is 13,480,609 bytes across 307 pages and the per-committee extracts are small enough to
fetch whole. UT System publishes each committee's pages as a separate file, so a committee
document's boundary is the publisher's own and never a guess at page breaks. **The documents number
their own pages in a running footer** (`Facilities Planning and Construction Committee Agenda Book
- 130`), and that footer is the folio to quote. A PDF page index is not a page number, and this run
published 129 to 133 before catching it.

**`tacc.utexas.edu` answered 403 to the research phase** and `interchange.puc.texas.gov` answered
503 to one client and 200 to another within the same run. Both are fetcher outcomes and not crawl
boundaries, so they stay here as observation until a second sighting.

**`www.statesman.com` publishes a whole-host `Disallow: /` under `User-agent: ClaudeBot`.** Read
before fetching, while looking for coverage published after the August 12th UT System meeting, and
not fetched. That is the third host in four days carrying an agent block behind a permissive
`User-agent: *`, after `lrl.texas.gov` and `dir.texas.gov`, and it is the reading order stated in
the entry above earning its keep on the same day it was written.

`communityimpact.com` carries no relevant disallow and served the report that settled it, at
`communityimpact.com/austin/central-austin/development/2026/08/13/ut-system-regents-approve-first-phase-of-dell-medical-center/`.

**UT System publishes a pre-meeting agenda book and, for this meeting, no minutes.** The August
12th book is what a committee was ASKED to approve, and there is no document on `utsystem.edu`
published after the meeting that says what the board did. So the fact that the regents approved
Phase 1 is not establishable from the publisher at all this week, and the only source for it is
journalism.

**This is the source behaviour behind this run's second hard fail.** The record and four deck
surfaces said the board voted, authorized and amended, every one of them citing the agenda book,
which is a request. The bar the routine sets is primary sources over journalism, and on this fact
the primary source cannot answer the question and the journalism can. **Prefer the primary document
for what a body was asked to do and require a post-meeting source for what it did**, rather than
reading a stronger verb out of the stronger source type. `public_access.how` on `tx-2026-0095` now
states that no minutes exist.
