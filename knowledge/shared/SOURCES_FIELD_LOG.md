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
