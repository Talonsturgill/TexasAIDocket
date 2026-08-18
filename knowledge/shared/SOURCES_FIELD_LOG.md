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
