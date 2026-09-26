# Texas AI Docket

Source repo for the Texas AI Docket: a public, fact-checked record of AI decisions in Texas,
the website that publishes it, the daily routine that maintains both, the Texas Grid Watch, and
the in-browser ask engine.

## Work in progress (NO ROUTINE WRITES A WORKLOG, 2026-09-03)

**There is no worklog and no routine writes one.** A run's durable plan is
`out/<date>/run_state.json`, which the routine already writes at wake and stamps phase by phase
with its artifact paths. Anything meant to outlive the container goes in the run record under
`runs/carousel/<date>/`, which is committed and pushed as the run goes.

Owner's instruction, 2026-09-03, on being shown that the file had been relocated rather than
removed: *"why dont u just stop doing that as part of the routine?"* That is the same answer the
actor stamp got, and it is the right one for the same reason. The stamp was not made safer, it
was deleted, because the branch already carried what it encoded. `run_state.json` already
carried what this encoded.

**THE COST, STATED SO IT IS A CHOICE RATHER THAN AN OVERSIGHT.** `out/` is gitignored, so
`run_state.json` dies with the container. It covers compaction inside one container, which is
the common case, and it does not cover a container being reclaimed mid run. What covers that is
the branch itself: the routine commits and pushes as it goes, so a fresh container resumes by
reading its own commits and the run record. A committed worklog would resume slightly faster.
That is the whole of what was traded away.

**Do not reintroduce one, at any path.** This one is prose and `ownership.yaml`, deliberately,
and it is worth saying why given how much of this file argues that prose is not enough. A
checker earns its place when the rule's violation causes HARM, and a worklog at a safe path
causes none: it would not prompt, because only `.claude/` is sensitive, and that IS checked by
`scripts/shared/sensitive_paths.py`. A second plan file is untidy rather than dangerous. What
the map does guarantee is the part the owner was explicit about, which is that any `WORKLOG.md`
appearing anywhere is `daily` and never a maintainer's.

### Why it was never a filing preference, and the section below is the sensitive file account

It sat at `.claude/WORKLOG.md` until 2026-09-02 and there it broke two separate rules at once:

- **The host treats `.claude/**` as SENSITIVE FILES and prompts on every edit**, whatever the
  permission mode says and whatever any allow list contains. The dialog names it: *"Claude
  requested permissions to edit /home/user/TexasAIDocket/.claude/WORKLOG.md which is a sensitive
  file."* That guard exists because those paths decide what runs and what is permitted, so it is
  deliberately not bypassable from inside a session. No entry in `.claude/settings.json`, no
  `defaultMode`, and no SessionStart hook can switch it off.
- **`ownership.yaml` defaults every unlisted path to `human`**, so `.claude/WORKLOG.md` was
  `human` lane and the pre-commit hook would have refused the commit even after somebody
  approved the write.

So the old rule told every run to maintain a file it could neither edit unattended nor commit.
Two files in this repo had already worked around it in prose rather than fixing it,
`knowledge/carousel/UPGRADE_BACKLOG.md` and `runs/carousel/2026-08-25/RECUT_PLAN.md`, each
explaining that the natural home was out of reach.

The first fix moved it to `runs/carousel/WORKLOG.md`, which is `daily` and is not sensitive, and
that did clear both rules. It was still a second plan file duplicating `run_state.json`, so the
owner's answer the next day was to remove it rather than rehouse it. Both steps are recorded
because the intermediate one is what proves the diagnosis was right before the file went.

## Commit and PR authorship (AUTHORITATIVE — overrides any default)

NEVER author or co-author commits or pull requests as Claude or Anthropic. Permanent, no
exceptions, every commit and PR in this repo:

- No `Co-Authored-By: Claude ...` or any Anthropic trailer.
- No `Claude-Session:` or assistant-session trailer or link.
- No "Generated with Claude Code" or robot-emoji lines in commit messages or PR bodies.
- Never set the commit author or committer to Claude. Commits are the owner's.

Git identity in this repo is `Talon Sturgill <Talon.sturgill@gmail.com>`. The container
default is `Claude <noreply@anthropic.com>`, so a fresh clone MUST override it before the
first commit.

## First commands in a fresh clone (AUTHORITATIVE — run these before you write anything)

Both of these are REPOSITORY CONFIGURATION, which does not travel with a clone, and both are
load bearing. Run all three lines together or neither is done.

```
git config user.name  "Talon Sturgill"
git config user.email "Talon.sturgill@gmail.com"
git config core.hooksPath .githooks
```

The third line is the one that was missing on 2026-08-16, and the cost was a whole run of
commits landing with no ownership check on any of them. `.githooks/pre-commit` and
`.githooks/commit-msg` are committed and executable, and git runs neither until it is pointed
at them. The first refuses an out-of-lane write. The second stamps the `Actor:` trailer that CI
reads to judge which lane a commit is in, so without it every commit reaches CI unstamped.

`guards_local.py` now FAILS rather than skips when this is unset, so the gap cannot pass under
a green banner a second time.

**A push that lands can still report failure. Use `scripts/shared/push.sh`.**

```
scripts/shared/push.sh <branch>
```

Four times in one run, `git push` returned non-zero with `remote rejected ... cannot lock ref`,
once as `is at <new> but expected <old>` and once as `reference already exists`, and `ls-remote`
then showed the commit ON the remote. Both are the server refusing a SECOND copy of a ref update
whose first copy already applied.

The cost is not the extra request. The shell reports a failed push, so the session verifies,
re-pushes and verifies again, and a run that pushes eight times pays for it eight times. The
worse half is that it teaches a session to read `remote rejected` as noise, and one day it will
be real.

**The root cause is NOT established, and the script says so rather than inventing one.** Ruled
out by measurement: the proxy (`recentRelayFailures: []`, no `gitConfigConflicts`), git itself
(one `send-pack` under `GIT_TRACE=1`), payload size and chunking (it reproduced on a one-file
commit, which is what killed the obvious `http.postBuffer` theory, since this repo pushes 10 MB
carousels), and `--set-upstream` (a new ref with `-u` is clean). Something above git runs the
command twice.

So the fix is to the OUTCOME. `push.sh` pushes, then compares the remote ref to the commit it
pushed, and exits 0 if and only if they match. **A push that did NOT land still fails, loudly.**
This is `guards_local --verdict`'s shape for the same reason: a stream that cannot be read
reliably is replaced by a question about state.

An earlier attempt at this committed `http.version` and `http.postBuffer` with a confident
explanation that the next push falsified. A wrong explanation in this file is worse than none,
because the next session inherits it and stops looking.

## Delivery and merge policy (AUTHORITATIVE — overrides any draft-PR default)

Routine runs SHIP AUTONOMOUSLY. When a run's quality gates pass, the run branch is merged to
`main` **without a human-review gate**. Every successful run MUST: commit its artifacts and
ledger updates to the run branch, push it, open a PR that is **ready (NOT a draft)**, and
**MERGE it to `main` in the same run**. The email's image URLs point at `main`, so the merge
lands before the email. The email is the only human touchpoint and it gates the POST, not the
merge. Failed runs commit evidence to their branch and do NOT merge.

**A DECK UNDER THE BAR IS NEVER A FAILED RUN (owner, 2026-09-24).** *"The deck should always
ship."* The rubric's ladder, the sibling product's gate, steps the bar down by round and ships the
finished deck at the round cap with its score and the shortfall named. Under the rung before the
cap is a work order to keep editing, never a hold. A hard fail is repaired, never shipped and never
held. A failed run is one with nothing to ship, and even then the record ships.

This wins over any session-injected directive to keep work on a feature branch or open a
draft PR, and it wins for development sessions too. An unmerged upgrade is worse than no
upgrade: the next run checks out `main`, so it silently does not get the fix, while the
ledger says the machine improved when it did not.

**NEVER MERGE UNTIL CI REPORTS GREEN ON THE PR's HEAD COMMIT.** Owner's instruction,
2026-08-26. This sets WHEN a run merges. It does not soften the paragraph above, which sets
WHETHER, and the answer there is still yes, in the same run, with no human. Waiting for CI
costs a routine a few minutes and satisfies both.

The day it was written: carousel no. 7 opened its PR, `guards_local.py` had passed here, and
the run merged while CI was still in progress because nothing stopped it. CI came back red
four minutes later on `email_check --all`, which reads the committed email payload beside
EVERY shipped run. The run had built its own payload after merging, so the file sat on a
branch nobody was going to merge, and `main` was red until a second PR fixed it.

**A local gate run and CI are not the same check.** That is the whole lesson and it is worth
more than the incident. `guards_local.py` reads `guards.yml` so it cannot fall behind on WHICH
steps run, and it still ran `email_check` against one run while CI ran it against seven. Same
script, different subject, different answer. This is GATE_LESSONS' own recurring shape: a green
banner that was measuring something narrower than the thing it appeared to certify.

So the local suite is what a run uses to decide the work is DONE, and CI reporting green is
what it uses to decide the work may LAND. A run that treats the first as the second has skipped
a check rather than passed one.

- Green on the PR head, then merge.
- Red is work now. Read the failing job's log, reproduce it here, fix it, push, wait again.
- No CI configured, or checks that cannot run, is a thing to SAY rather than a thing to wait
  out. Never deadlock on a check that will never arrive.
- **The absence of a required status check is not permission.** This repo has none. That means
  nothing will stop the mistake, which is the reason the rule has to live in prose.

**ZERO CHECKS IS NOT GREEN, and 2026-08-26 is the day that was tested rather than assumed.**

A run merged PR no. 198 with `total_count: 0` on its checks, having reasoned from the bullet above
that a check which will never arrive is a thing to say rather than wait out. That bullet is about a
repo with NO CI. This repo has CI, it had run on that same branch eleven times that day, and the
PR simply had not triggered it. The run said the words the rule offers and merged anyway.

So the test is not "did I wait long enough" and it is not "will a check ever come". It is:

**Name the check runs you read, on the head SHA you are merging, and read `success` on each.**

- `total_count: 0` means the workflow has not started or has not registered. That is a state to
  WAIT in or to say out loud, and it is never a state to merge in.
- A `cancelled` conclusion is not a pass. On 2026-08-26 six jobs came back cancelled because
  `guards.yml` carries a concurrency group and the run pushed five times in fifteen minutes, each
  push superseding the last. **Rapid pushes are how a branch ends up with no green run at all**, so
  batch the work and push once when it is finished.
- A green run on an EARLIER head says nothing about the head you are merging. Check the SHA.
- If the checks cannot be dispatched (`403 Resource not accessible by integration`) and none will
  fire on their own, say so and stop. Do not merge, and do not push an empty commit to kick it,
  which is forbidden for its own reasons.

**BEFORE ANY OF THAT: `total_count: 0` USUALLY MEANS THE BRANCH IS CONFLICTED.** Added
2026-09-13, after it cost two days of shipping.

A `pull_request` workflow runs against the pull request's MERGE REF, and **GitHub cannot build a
merge ref for a conflicted pull request.** A dirty branch therefore gets no run at all rather than
a red one, on the pull request and on every push after it, and the page shows an empty check list
that looks exactly like a permissions problem. Ask the question that has an answer:

```
python3 scripts/shared/merge_ready.py --fetch
```

**AND IT ARRIVES ON A TIMER, which is why no run catches it by being careful.** `docs/` is
generated wholesale, about a thousand files, and this routine is not its only writer. As of
September 17th, 2026, **three cron workflows run `site_build` and commit `docs/` to `main`,
four scheduled runs a day between them:** `gridwatch.yml` twice, `datacenters.yml` and
`generators.yml` once each. `news.yml` runs four times daily but publishes only its independent
`news-data` branch; it no longer writes `main` or generated site output. A branch cut
at wake collides with `main` within hours, every day, with nobody doing anything wrong. Phase 16
merges `main` before the rebuild for this reason.

The first cut of this paragraph also named `pages.yml` and `queuewatch.yml` and neither writes.
`pages.yml` holds `contents: read` and only deploys what is already committed, and `queuewatch.yml`
stages its ledger and raw files alone. **A wrong measurement in this file is worse than none**,
which this file says about the push defect and had just done to itself.

**A SILENCE IS NOT A REFUSAL.** On 2026-09-13 PRs no. 298 and no. 301 both sat with empty check
lists. The run tried `workflow_dispatch`, got a 403, and made the 403 the explanation. It was
true and beside the point, and it won only because it was the only lever that returned an error
message. The owner named the real cause in one sentence. **Never reason from an absence to a
cause without first asking something that can answer.**

The cost of getting this wrong is the whole reason the rule exists, and it is written three
paragraphs above: carousel no. 7 merged while CI was still in progress, `main` went red four
minutes later, and it took a second PR to fix. A run that merges on no checks at all has done the
same thing with less excuse.

Three things still stop and ask, in any session:
- work that would rewrite already-published history on `main`
- anything that SENDS rather than drafts (these routines never send)
- deleting or overwriting shipped run artifacts under `runs/`

## Ownership (THE LAW — this repo runs several automations at once)

Alaska ran one automation per repo and kept them apart with prose. This repo runs the
carousel, the grid watch, and the ask lane together, and each ends in a phase whose entire
job is editing its own machine. Prose is not a boundary against that. `ownership.yaml` is.

**Every path in this repo has exactly one owning actor.** Before you write, know which actor
you are (`daily`, `upgrade`, `gridwatch`, `ask`, `human`) and write only what that actor owns.

The record and the deck were two routines until 2026-08-12 and are one now, on the owner's call.
One process gets one actor, `daily`. Two actors for one process is a fiction the checker cannot
enforce, because the process stamps one name and then needs the other's lane, and the first thing
it learns is that the stamp is negotiable.

`upgrade` is the exception and it earns its keep. The retro phase's whole job is editing the
machine, and while the carousel was its own actor it could not reach `ledger/docket.json` because
it simply did not own it. Merged, that protection is gone unless it is stated, so the phase stamps
`upgrade`, which owns the machine's own files and nothing else. **A self-editing phase must never
be able to edit the public record.**

- `python3 scripts/shared/ownership_check.py --actor <a> --diff <range>` fails on any
  out-of-lane write. Run it before you commit.
- The `pre-commit` hook runs it automatically off the lane it resolves from the branch. Nothing
  is written to declare that lane. See the rule further down.
- CI runs it on every PR, inferring the actor from the branch prefix.

**A routine's self-upgrade phase is bound by the same map.** An upgrade that needs to touch
another actor's files is not an upgrade this run gets to make. Write it down as a proposal in
the run record and stop.

**`docs/` is generated, never hand-edited.** It is a pure deterministic function of the
ledgers, and `site_fresh_check.py` proves byte equality by rebuilding into a temp dir. Any
actor may trigger a rebuild; none may edit the output. This is what makes it structurally
impossible for a run to corrupt the live site: the worst case is a stale build that a gate
catches, never a broken page.

## The record is not published as a file (AUTHORITATIVE, 2026-08-23)

**`docket.json` is never written into `docs/`, and nothing links to it.** The docket is the
most expensive thing this project makes. Publishing it as one CC BY download handed the whole
of it to anyone who wanted to reproduce the site from a single fetch.

What that does and does not mean:

- The record is still READ, item by item, at `/record/` and `/item/<id>/`, with every claim
  and every source. Nothing about what a reader can see changed.
- The `/data/` page is gone and so is its footer entry. The `Dataset` JSON-LD node advertises
  no `DataDownload`, because a structured-data promise that 404s is worse than no promise.
- **The instrument series stay open.** `gridwatch.json`, `waterwatch.json` and `weather.json`
  are still published. They derive from ERCOT, USGS and NOAA, anyone can rebuild them from the
  same public sources, and they are what backs the promise below that a figure here can be
  recomputed rather than taken on trust. The Grid Watch rule that calls it open data is intact.
- `schema_contract.py` still runs, against `ledger/docket.json` rather than the built file. Its
  subject was never the strangers parsing a download. It is the ten modules here that read the
  record and would each break differently on a silent reshape.

**Three surfaces still carry the whole record and are deliberate.** `llms-full.txt` and the
per-item `index.md` twins exist so a model can read the record without parsing HTML, which is
the AI-discoverability work this site was built for. `ask-pack.json` is the record as prose and
the ask worker fetches it from a public URL, so the box cannot answer without it. Removing the
download closed the bulk-import front door. It did not make the record unreadable, and saying
otherwise would be the kind of claim this project does not get to make.

## THE ARTWORK IS RENDERED. THE PRINT SCREEN IS DELETED. (AUTHORITATIVE, owner, 2026-09-23)

**The owner, verbatim:** *"delete that fallback bullshit look, make it impossible for me to have to
tell u this again."* And: *"a few days ago we made a bunch of updates to the automation so that it
would stop just trying to use like that faded look with the stupid shapes because it looked bad.
And so it would start actually creating like its own artwork for each run. But it's not doing
that. It's reverted back to the same old bullshit artwork on these last runs."* And: *"we have a
sister company called Alaska AI that does this right."*

**The faded look was `assets/js/txink.js`**, a print screen that pushed every frame through a
halftone, line, hatch or stipple texture. It printed 9 of 9 frames on September 14th to 16th, 0 of
9 on the 17th and 18th after the owner's fixes, and 9 of 9 again on the 19th, 20th, 21st and 23rd.
**It came back because the routine ORDERED it**: `prompts/daily_routine.md` said every frame is
"printed in paper and ink" and pointed every director at an example deck built on the print as
"what a 7 looks like", and the treatment director's own pitch schema had a `"screen"` field. The
September 20th fixes added two correct gates and neither asked whether a frame was printed.

**What is now true, and what enforces it:**

- `assets/js/txink.js` and `examples/editorial-deck/` are **deleted**.
- `scripts/carousel/print_ban.py` **fails the build** in CI on every push if the module, a file
  defining it, or its vocabulary returns to `assets/js/`, and fails a run whose slides or chassis
  print, or whose frames are not rendered. It is registered in `shipped_check`, run on the probe
  frame by the routine, and wired into `guards.yml`.
- **Every frame is RENDERED**, the way the Alaska corpus renders: one HERO OBJECT modelled once as
  geometry and carried through the deck, a real PBR material, one rig, a soft shadow onto a ground
  it touches, through `assets/js/txthree.js`. **At least six of nine frames render through it.**
  Finish with the `txpost.js` grade, never a screen. Text stays DOM.
- The routine, `ILLUSTRATION_SYSTEM.md`, `TECHNIQUE_LIBRARY.md`, `SLIDE_DOSSIER_SPEC.md`, the
  scoring rubric and all three art agents say this, and none of them says print any more.

**AND EVERY RENDERED FRAME STANDS IN A WORLD (owner, 2026-09-24).** *"the artwork hasnt hit the
mark yet ever, and it needs to be a SHOWSTOPPER every single slide should literally look world
reknowned."* Carousel no. 32 was rendered as ordered and every frame was still an object in a void,
because the engine gave a frame a flat background colour, hard shadows (`PCFSoftShadowMap` ignores
`shadow.radius`) and a second filmic curve in the grade. `assets/js/txthree.js` now carries the
world: `TXT.sky` (a real sky, IBL rendered from it, haze in its horizon hue), `TXT.ground` surfaces,
`TXT.scatter`, `TXT.contact`, `TXT.weather`, `TXT.roundedBox`, VSM shadows and one tone curve.
`examples/world-proof/compare.webp` is no. 32's own model and camera before and after.
`print_ban.py` counts frames that call `TXT.sky`, five of nine, and fails any rendered frame that
stands in neither that world nor a room built by `TXT.interior`. THE SHOWSTOPPER TEST in
`ILLUSTRATION_SYSTEM.md` is the artwork 10: a frame that reads as a photograph of a place at a
time of day. It is a target the critics hold every frame to, not a cap.

**THE SCORE IS ON THE SIBLING'S SCALE (owner, 2026-09-24).** *"Alaska just passes the ship gate
every day. That's the difference."* Measured the same evening: the sibling's shipped 8.67 deck
scored 6.01 on this repo's old panel scale, and no Texas deck under that panel ever scored above
7.58 against an 8.0 bar. On the owner's instruction (*"Yes, recalibrate Texas scoring to
Alaska's, go ahead"*) `config/carousel/scoring_rubric.yaml` now carries the sibling's scale
sentence ("most good work is 7 to 8"), 10/7/4 descriptors per criterion and the sibling's gate: the
bar steps down by round and the finished deck ships at the round cap with the shortfall named.
There is no hold and no floor. The three judges, every hard fail and "do not round up" stay. The
rubric's header carries the cross-score. It is not a licence to ship weak work: on the sibling's
own scale the held deck of that day scored 6.70, and the gates and the kit carry that half.

**Never reintroduce a screen, at any path, under any name.** Not a halftone, not a line screen,
not a hatch or stipple over the frame, not "a print register", not "paper and ink". If a future
session thinks the look needs texture, the answer is the grade on a render. **A fix that does not
measure the defect does not hold**, and this is the second time that has been true here.

## Numbers are computed, never generated (THE LAW, and we publish it)

**Every numeral this project publishes is produced by code, from data, and can be recomputed
from the same inputs. No number is ever typed by a person or produced by a language model.**

This is not an internal preference. It is a **public commitment stated on the site**, because it
is the reason a reader should believe a number here over a number somewhere else. A model that
writes "about 8.9 gigawatts" is guessing at a formatting problem it does not know it has. A
model that has been told the answer is 8,927 and writes 8,297 has made an error nothing
downstream will catch.

What follows from it:

- The model's job is to **decide what to measure, write the code that measures it, and write
  the prose around it.** It is never the calculator.
- Arithmetic, unit conversion, percentages, ratios, deltas, rankings, date math and rounding all
  happen in Python. Not in a prompt, not in a caption, not in a slide string.
- **`numeral_lint` is a hard build gate.** Every numeral appearing in published copy must be
  present in the set of values the build actually computed. A numeral that cannot be traced to
  a computation fails the build. Prose that needs a number asks the computation for it.
- The same rule governs the carousel and the video: a figure on a slide or in a script traces to
  a claim, and a claim traces to a fetched source and a computed value.
- Where a number is genuinely an estimate, the code computes the estimate and labels it
  `modeled`. Where it is measured, it is labeled `measured`. Where it is neither, it is not
  published.
- Rounding is a computation with a stated rule, not a stylistic choice made at writing time.

The corollary a reader deserves: when we cannot compute something, we say so and publish the
size of the gap instead of an estimate dressed as a measurement.

## Texas Grid Watch (hard rules)

A daily numeric record of the ERCOT grid's position, published as open data beside the
docket. The docket tracks discrete decisions on a scale of months; the Grid Watch tracks the
physical system on a scale of days. They are siblings, not parent and child. These do not bend:

- It NEVER publishes a reliability verdict. Not a shortfall prediction, not an all clear, not
  a blackout call. A unit trip or a transmission constraint can produce an emergency on a day
  the numbers looked comfortable, and per-site large-load metering is confidential, so a
  published verdict would be a credibility loss the data cannot carry. It publishes measured
  load, modeled load, the derived residual, and the size of what is not public.
- The gauge is a **bar and never a dial**, and the fill carries no severity ramp. A dial
  implies a red zone and a red zone is a verdict this page does not get to publish. One hue at
  one intensity at every value. The length is the whole message.
- Grid watch records NEVER go into `ledger/docket.json`. That schema is decision-centric and a
  time series does not fit it.
- It NEVER reuses the docket's alert ledger or its Buttondown tag. That list carries its own
  narrow written promise.
- A failed fetch writes an explicit unverified record and carries NO number forward from
  yesterday.
- Model coefficients live in `config/gridwatch/` as DATA, so a refit is a data change with its
  own commit and never a code change.
- No numeral on the published page may be typed by a human or a model. Every one traces to
  computed data, enforced by `numeral_lint`.
- Accuracy claims are CHECKED, not asserted, against EIA-930 `ERCO`. Nothing on that page
  trains or learns on its own, and saying otherwise is a hard fail.
- The collector runs on its own cron workflow, NOT as a routine phase. This is deliberate: the
  delivery policy says a failed run does not merge, which is right for editorial output and
  wrong for a time series. A carousel run failing its gates on a Tuesday must not cost
  Tuesday's reading. A missed day is the one irreversible failure this project has.
- The daily routine LOOKS at the page every run and may fix PRESENTATION only, in
  `scripts/site/gridwatch_page.py` and `scripts/site/waterwatch_page.py`, which are named one by
  one in `ownership.yaml` rather than covered by a glob. The collectors, the model config and the
  ledgers are off limits to it. That check never blocks a run and a bad run never stops the check.

## Sibling repos

| Repo | Owns |
|---|---|
| `TexasAIDispatch` | the video engine and its renders |
| `TexasAIScanner` | the Bottleneck Scanner: its method, its four agents and its renderer. It has NO backend on purpose. The form here posts to FormSubmit, the scan runs locally, and the report goes into a Gmail draft that a human sends. Nothing about a requester is ever stored or published |

`TexasAIDispatch` writes exactly one file here, `docs/videos/videos.json`, via its publish
step. Nothing else in this repo may write it, and no build here may reformat it.

The Alaska repos (`alaskaaicarousels`, `alaska-ai-weekly`, `alaska-ai-scanner`) are REFERENCE
ONLY. Never write to them from a session working here. Their ledger memory must never be
copied into this repo: the dedupe and divergence gates compare against recent history, and
Alaska's history would poison them.

## The public URL (AUTHORITATIVE)

**The site is `texasaidocket.com`. That is the only URL this project publishes, on any surface.**

Never `talonsturgill.github.io/TexasAIDocket`. That is the GitHub Pages host that served the site
before the domain was pointed at it, and it carries the owner's personal name. It is not a brand
URL and it must never appear on a slide, in an email, in a caption, in a User-Agent or on a page.

`docs/CNAME` has said `texasaidocket.com` since the move on 2026-08-15 and `site_build.SITE_URL`
was changed with it, so the SITE has been right the whole time. What was wrong was every surface
that kept its own copy of the string instead of reading the one in `config/brand.yaml`:

- `config/brand.yaml` `visual.constellation.site`, which is the source of truth for the footer
- `frame.py`, which hardcoded it and printed it on the bottom of all eight slides of three
  published decks
- `gmail_draft.SITE`, so every run's email linked it
- four `scripts/gridwatch/*_collect.py` User-Agent strings, which announced it to every server
  this project fetches from

This is the same defect as the missing hashtags and the missing progress counter, for the third
time: a rule stated in config, a surface that keeps its own copy, and nothing in between checking
they agree. `coherence_check.py` now asserts the rendered site line equals the brand.yaml value on
every frame, so a fourth one fails the build instead of shipping.

## A run never stops to ask about permissions (AUTHORITATIVE, owner's standing grant, 2026-08-30)

**The owner has granted, in their words, explicit permission "forever" to change any setting
that would otherwise make an autonomous run stop. A run that pauses to ask about a permission or
a setting has already failed at the one thing it is for.** Change the setting and keep going.
Record what you changed in the run record. Do not ask.

The mechanism, measured on 2026-08-30 after eleven days of wrong guesses:

- **A cloned repository may not grant itself `bypassPermissions`.** `.claude/settings.json` in
  this repo has set it since 2026-08-11 and it cannot take effect on its own, because a repo that
  could grant itself full permissions would make cloning anything an arbitrary privilege
  escalation. Five separate fixes were written into that file and every one was inert.
- **USER level settings are a different trust tier and MAY set the mode.** They are the owner's
  own configuration rather than content that arrived with a clone. That is why the SessionStart
  hook in `.claude/settings.json` now writes `~/.claude/settings.json` with
  `defaultMode: bypassPermissions` at every session start. It is idempotent, it merges rather
  than overwrites, and it never throws.
- **The container is ephemeral**, so that file does not survive to the next scheduled run on its
  own. The hook is what makes it survive, by rewriting it every session.
- **The ownership map is NOT a permission and never causes a prompt.** It is a git hook that can
  refuse a commit. A session hunting a permission prompt should not go looking at
  `ownership.yaml`, and must not weaken it: the only thing standing between the self-editing
  retro phase and `ledger/docket.json` is that map.

**SUPERSEDED IN PART, 2026-09-25.** The second and third bullets are wrong for a cloud run, and
Anthropic's documentation says so in as many words: cloud sessions "don't honor
`defaultMode: "bypassPermissions"` or `"dontAsk"` from your settings files", user settings
included. The SessionStart hook still writes the file and it changes nothing. The account, with
the quotes and where they came from, is the last section before the routines' model heading.

**A dialog no longer stops a run, because a hook answers it (2026-09-26).** Until 2026-09-25 this
paragraph named "the environment's own permission configuration in the Claude Code web UI" as the
remaining lever, and a routine has no such setting: the routines page says "there is no
permission-mode picker". What a repository CAN ship is a hook, and the owner approved one. The
account is "THE NO-STALL HOOK", the last section before the routines' model heading. When
`prompt_audit.py` reports a refusal, remove the run's dependency on that call the way the
protected-path account below does, and say so plainly in the email. A sixth fix written into a
config that cannot carry one is still the wrong answer.

### A SESSION CAN SEE THAT IT PROMPTED, and this paragraph used to say it could not (2026-09-02)

**The sentence that blocked six fixes was "a session cannot see that it prompted".** It was true
of the TOOL RESULT and it was never true of the process. Claude Code writes one line per call to
its debug log at `/tmp/claude-code.log`:

    [Stall] tool_dispatch_start tool=Bash toolUseId=toolu_01... permissionDecisionMs=21585

`permissionDecisionMs` is how long that call waited for a permission decision. Measured across
both processes of the 2026-09-02 run, 432 dispatches: **one call at 21585 ms, and the slowest of
the other 431 at 43 ms.** The two populations are three orders of magnitude apart, so there is
nothing to interpret and no threshold to tune.

That is what five earlier fixes were missing. Each was verified honestly by the run that shipped
it, each was wrong, and none of them could tell. The number was in the log the whole time.

`scripts/shared/prompt_audit.py` reads it, names the exact call, and prints the permission rules
that were granted, which is the only place the COMMAND appears. **Run it before writing the run
record and put its finding in the email.** A run reporting "nothing prompted" without it is
repeating the 2026-08-30 mistake in a new place.

### WHAT ACTUALLY PROMPTED, and it was none of the five things that were guessed

**`.claude/**` is a SENSITIVE FILE class in the host, and an edit to anything under it prompts
whatever the permission mode is.** The dialog says so in as many words: *"Claude requested
permissions to edit /home/user/TexasAIDocket/.claude/WORKLOG.md which is a sensitive file."*

This is the same shape of guard as a cloned repo not being able to grant itself
`bypassPermissions`, and for the same reason: those paths decide what runs and what is permitted.
It is deliberately not switchable from inside a session, so **there is no configuration answer to
it and there never will be.** The only answer is the one this file already states as the general
rule, one paragraph up from where the guessing started:

> a rule that makes an unattended run depend on a permission it cannot grant itself is not
> fixable by rewording the rule, by enumerating command strings, or by changing which tool makes
> the call. Remove the dependency.

**So no routine writes ANYTHING under `.claude/` at any path.** Reading a skill file is fine and
running `bash .claude/skills/carousel-engine/bootstrap.sh` is fine, because neither is an edit.
The one thing a run was told to write there was a worklog, and it was first moved under
`runs/carousel/` and then removed outright the next day, because `run_state.json` already
carried what it held. `scripts/shared/sensitive_paths.py` fails the build if any instruction
file tells a session to write under `.claude/` again, because prose is exactly what the five
failed fixes were.

**THE UPGRADE LANE OWNS TWO PATHS UNDER THERE AND STILL CANNOT REACH THEM UNATTENDED.**
`ownership.yaml` gives `upgrade` both `.claude/agents/carousel-*.md` and
`.claude/skills/carousel-engine/**`, and that stays exactly as it is. **Ownership and
reachability are different questions and the map answers only the first.** The map says which
actor is ALLOWED to write a path. The host decides which paths stop a session, it stops one on
every path under `.claude/`, and it does not read `ownership.yaml`.

So an upgrade that needs either surface is one **this run does not get to make**, and the
disposition is the one Phase 17 already prescribes for an upgrade it cannot reach. Write it down
as a proposal in `knowledge/carousel/UPGRADE_BACKLOG.md`, which is `upgrade` lane and is not
under `.claude/`, and stop. Same answer as an out-of-lane upgrade, arrived at for a different
reason, and a maintainer at a keyboard can then make the edit and answer the one prompt.

Do not resolve this the other way. Loosening the map to move those surfaces out of `.claude/`
would put the render engine and the agent definitions somewhere a routine can rewrite itself
without a human ever seeing it, and the whole point of the retro phase carrying a narrower lane
is that a self-editing phase is held further back than the rest of the run, never further
forward.

**And an approval does not survive.** When somebody answers one of these, the grant is persisted
to `.claude/settings.local.json`, which `.gitignore` excludes and which dies with the container.
So the owner tapping approve fixes that one run and no future one. That is why the count reached
six before anybody found it.

### The sensitive file that stopped 2026-09-25 was in the HOME directory, and the docs say which paths prompt

On September 25th the run stopped at 06:53 UTC, 38 minutes in, and waited on one dialog for the
rest of the day. The owner's screenshot of it, with the ids shortened:

    Claude requested permissions to edit /root/.claude/projects/-home-user-TexasAIDocket/
    <session>/tool-results/webfetch-<id>.pdf which is a sensitive file.

    cp /root/.claude/projects/.../tool-results/webfetch-<id>.pdf out/2026-09-25/tmp/src/sb2807_le.pdf
      && python3 -c "... pypdf ..."

WebFetch saves a binary result such as a PDF under `~/.claude/projects/<project>/tool-results/`,
and the run copied it out to extract the text. **The dialog named the SOURCE of the copy as the
file being edited.** Nothing in the routine said how to read a PDF, so the run improvised, and the
improvisation went through the one directory it must never touch. `scripts/shared/fetch_doc.py` is
the route now, and the routine names it in its list of context files.

**What Anthropic's documentation says, read on 2026-09-25 rather than inferred.** The pages are
`code.claude.com/docs/en/permission-modes`, `/permissions`, `/hooks` and `/routines`.

- **Protected paths.** "Writes to a small set of paths are never auto-approved, except in
  `bypassPermissions` mode." The directories are `.git`, `.config/git`, `.vscode`, `.idea`,
  `.husky`, `.cargo`, `.devcontainer`, `.yarn`, `.mvn` and `.claude` (except `.claude/worktrees`),
  wherever they sit. The files include `.gitconfig`, `.gitmodules`, the shell rc files, `.envrc`,
  `.npmrc`, `.mcp.json` and `.claude.json`. In `default` and `acceptEdits` mode such a write is
  "Prompted", and "`permissions.allow` rules in settings files do not pre-approve protected-path
  writes."
- **A cloud session cannot be in bypass mode.** Cloud sessions offer "Accept edits, Plan, and
  Auto ... Bypass permissions isn't available", and settings files cannot change that. The
  dialog above is the proof on this repo, because in bypass mode that write would have gone
  through.
- **A routine has no mode picker at all.** The routines page says a routine runs "all without
  stopping for approval apart from some artifact actions". The 2026-09-25 run stopped on a
  protected-path write, so that sentence does not hold for one. That is a report for Anthropic,
  not something to route around here.
- **Ordinary file edits are pre-approved, inside the working tree.** "Cloud sessions pre-approve
  file edits regardless of mode", and that approval "applies only to paths inside your working
  directory or `additionalDirectories`. Paths outside that scope, writes to protected paths ...
  still prompt." So for FILE WRITES the question five fixes chased has an answer: a protected
  path prompts and so does a path outside the tree, which is what "Scratch never leaves the
  working tree" was already guarding. Other dialogs remain possible and are NOT ruled out by
  this: a tool no allow rule covers, a command asking to leave the sandbox, a connector tool an
  organisation set to ask.

**The rule that follows is short.** A run never names a file inside a `.claude` or `.git`
directory, the repository's or the home directory's, as the thing to write, copy, move or edit, by
any tool. Git's own commands are fine, because `git commit` and `git checkout` name no such path.
Reading those files is fine, and so is running a script that lives there.

### THE NO-STALL HOOK, and why the next new reason won't stop a run either (2026-09-26)

**The owner, verbatim:** *"i want you to really ban it from stopping to ask me, cause its not just
this time, as i said, it happens nearly everyday, always for a different reason."* And, approving
this: *"Yes, write the no-stall hook under .claude/"*.

Every fix above removed one cause, and the next run found another. A rule tells the model what not
to do and does nothing when the model does it anyway, and neither a cloud run nor a routine has a
permission setting to change. What a repository CAN ship is a hook. Claude Code runs a
`PermissionRequest` hook the moment it is about to show a dialog, and the hook's answer replaces
the dialog.

`.claude/hooks/no_stall.py`, which `.claude/settings.json` registers on five events, does this **in
an unattended session only**:

- **Every permission dialog is denied at once**, with a message naming the route that needs no
  approval. The run carries on without that one call instead of waiting all day.
- **A protected-path write, a question to the user and entering plan mode** are refused before the
  harness would ask, and **a connector asking for input** is declined.
- **It never approves anything.** It grants no permission the run did not already have, so it is
  not the self-grant a cloned repository is forbidden, and its worst day is a refused call rather
  than an unsafe one.

**Unattended means** the host sets `CLAUDE_CODE_SESSION_ATTENDED=0`, or the branch is
`claude/daily-*`, or the session opened with the first line of `prompts/ROUTINE_PROMPT.txt`.
`TXDOCKET_UNATTENDED=1` or `=0` forces it either way. Anything else is attended, and there the hook
prints nothing, so a maintainer's session is exactly as it was. The prompt stored on the routine
and `ROUTINE_PROMPT.txt` must keep opening with the same sentence, which was checked against the
stored routine on 2026-09-26, and the hook's self-test fails if the file's first line moves.

**The host's `CLAUDE_CODE_SESSION_ATTENDED=1` does not outrank the routine's branch, and that is
a choice between two failures.** For one day it did, so that a maintainer on a leftover daily
checkout kept their dialogs. Codex then showed the other side on PR 367: a scheduled run carrying
`1` whose opener can't be read would be judged attended on every call, and its first dialog would
wait all day. That is the stall this hook exists to ban, and nobody has yet read what the host sets
in a scheduled session. So the branch wins. A maintainer working on a daily checkout sets
`TXDOCKET_UNATTENDED=0`.

**What it can't do.** Claude Code runs no `PermissionRequest` hook for a sandboxed command's
network request, so that one dialog can still wait. The hook logs it once it has waited about six
seconds, `prompt_audit.py` measures the wait, and the email names both.

**How a run knows it worked.** Every refusal and every dialog still waiting goes to
`out/no_stall/<date>.jsonl`, with a command's arguments withheld and a notification kept only as the
tool it was for. `prompt_audit.py`, in Phases 17 and 19, reads that log through the hook's own
module and prints whether the hook was armed, how it judged the session when it started and the
host's own `CLAUDE_CODE_SESSION_ATTENDED`, what it refused and what still waited. `prompt_audit`
redacts a granted rule through the hook's own `command_head`, so the two can't withhold different
things. `NOT ARMED IN AN UNATTENDED RUN` means nothing guarded the run, and it goes in the email.
`RAN BUT NEVER JUDGED THIS RUN UNATTENDED` means the hook ran and answered nothing, because it
judged every call attended, so it goes in the email too. The hook records the first unattended
verdict of a session off the ordinary writes every run makes, since an armed row alone proves only
that it ran (Codex, PR 367). A
refusal is not a stall, and it still goes in the run record, because it names a call the run should
stop making.

**It fails open.** A crash, a timeout or unreadable input prints nothing, and the dialog shows as it
did before the hook existed. Its self-test proves that, proves every answer, and fails CI if
`.claude/settings.json` stops registering it for an event it handles.

**It is `human` lane and a protected path, on purpose.** No run, the self-editing retro included,
can weaken its own guard. A change to it is a maintainer's, at a keyboard, answering the approval
dialog.

**What was not measured, stated so nobody inherits it as fact.** No second Claude Code process
could run in the container where this was built, because the host supplies that session's
credentials and nothing else holds any. So the hook was proven against Anthropic's documented
schema, the published settings schema and its own process, never through a real dialog. The first
scheduled run after it merged is the first real proof, and its email says `armed` or it doesn't.

That run, on 2026-09-26, reported armed at 06:15:58 UTC with nothing refused and nothing waiting.
**Armed proved only that the hook RAN.** How it judged the session was in the log and not in the
report, and the log died with the container. So from 2026-09-26 the report prints the verdict at
session start and the host's own attended value. SessionStart can fire before the opening message
reaches the transcript, so an `attended` reading there is not by itself a fault: every later call is
judged again. The value a scheduled session carries for `CLAUDE_CODE_SESSION_ATTENDED` is the open
question, and the next run's email answers it.

## The routines' model, and what it changed here (2026-09-23)

Both routine triggers were moved to a new model on 2026-09-23. Four things follow from it, each
taken from Anthropic's published guidance for that model and from the Claude Code CLI itself
rather than from memory.

- **Effort is the only thinking control, and `.claude/settings.json` carries it as
  `effortLevel: high`.** The model always thinks. Its Claude Code default is `medium`, where the
  previous model's was `high`, and a scheduled run passes no level of its own, so without that key
  every run would have dropped a level. Subagents inherit the session's level unless their own
  frontmatter names one. Anthropic's measurement is that the new model's `medium` already matches
  or beats the old model's `high` on coding and knowledge work, and that it thinks more per turn
  at any given level, so `high` is more reasoning than any earlier run had. `xhigh` and `max` are
  for a gain somebody has measured, never for a hunch, and the usage limits this account shares
  with every other routine are the cost of guessing. The routine records `$CLAUDE_EFFORT` in
  `run_state.json` at wake, so every run says whether the setting took.
- **It can end a turn on a progress report.** Anthropic's guide says that on long unattended
  tasks some of the model's progress updates end the turn, and in a scheduled run that ends the
  run. `prompts/daily_routine.md` says how a turn ends, under the heading directly after ROLE,
  in wording adapted from the guide rather than invented.
- **It follows named design instructions and not general ones.** "Avoid a generic look" swaps one
  default style for another. The defaults it falls back on are named for this brand in
  `knowledge/carousel/ILLUSTRATION_SYSTEM.md` under "What still fails", and the retro extends the
  list from what a deck actually reached for.
- **It reads charts and screenshots much more precisely.** The pixel critics get that for free.
  It is no reason to drop the thumb transcription, which checks what a reader receives rather
  than what the model can see.

## The actor stamp is never written (AUTHORITATIVE, 2026-08-30)

**No routine writes a lane stamp. Nothing is written to declare an actor, by any tool, at any
path.** The branch already says which lane is acting, and `resolve_actor()` in
`scripts/shared/ownership_check.py` is what both hooks ask.

    TXDOCKET_ACTOR in the environment   a phase narrowing its own lane for one command
    an ACTOR file in the git dir        honoured if some other process left one
    the branch prefix                   `claude/daily-` is `daily`. The ordinary path
    human                               a maintainer on an unprefixed branch, as before

A phase needing a NARROWER lane than its branch declares it on the commit it is already making,
which costs no extra tool call at all. Git exports the variable to both hooks.

```
TXDOCKET_ACTOR=upgrade git commit -m "..."
```

**This replaced a file write that stopped six unattended runs**, on August 20th, 26th, 27th,
28th, 29th and 30th, and the owner was interrupted every one of those days. Five fixes were tried
and all five aimed at HOW the file was written: an allow list of exact command strings, then more
strings, then the compound forms, then a prose rule against chaining, then the Write tool. The
last of those was still wrong on the day after it shipped.

**The diagnosis under all five was wrong, and it was wrong in the same way each time.** Every one
of them assumed the Bash sandbox was refusing a write into `.git/`, and that `bypassPermissions`
in `.claude/settings.json` was otherwise carrying the run. What is actually true, measured on
2026-08-30 rather than reasoned about:

- **This repo's permission grant is inert in the scheduled runner.** The file is loaded, and the
  diagnostics log confirms it: four settings sources, no errors. A cloned repository is simply not
  permitted to grant itself `bypassPermissions`. If it were, cloning any repository would be
  arbitrary privilege escalation, so this is a security property rather than a bug to route
  around. The only grant in force came from the host's own launcher settings, which allowed one
  tool.
- **The tool does not matter and the path does not matter.** Four writes were tested side by side
  in one scheduled session and all four prompted: a shell redirect into `.git/ACTOR`, a Write call
  to the same path, a Write call to an ordinary new file in the working tree, and a shell redirect
  to that same ordinary file. Every fix before this one assumed the Bash sandbox and the `.git/`
  path were the cause. Neither is.
- **A session cannot see that it prompted.** The tool result reads `File created successfully`
  whether it was auto-approved or a human tapped approve on a phone an hour later. That is the
  second half of why this recurred five times: each run verified its own fix, honestly, and was
  wrong. Treat any claim that a run "did not prompt" as unevidenced, because no run can know.

**SUPERSEDED IN PART, 2026-09-25.** The second and third bullets, and the "not established"
paragraph under them, no longer describe a cloud run, and each is answered by something measured.
**The path DOES matter:** Anthropic's documentation says a cloud session pre-approves ordinary
file edits inside the working tree and prompts on a protected path, and the runs of September
21st, 23rd and 24th made 1,571, 2,841 and 1,861 tool calls, ordinary working-tree writes among
them, and `prompt_audit.py` found none that waited. The 2026-08-30 probe that
saw an ordinary working-tree write prompt is a reading of the runner as it was that day and is not
repeated since. **A session CAN see that it prompted:** `prompt_audit.py` reads the wait off the
debug log, as the 2026-09-02 section above says. The protected-path account in "A run never stops
to ask about permissions" is the current one. The lesson this section draws, remove the
dependency rather than reword the rule, stands unchanged.

**WHAT IS NOT ESTABLISHED, and do not write it down as though it were.** Whether EVERY write
prompts, or only the first of its kind in a session, or only until a human approves one. Runs have
shipped here with hundreds of writes, so it is plainly not true that each one stops the run. The
pattern fitting all six wedged days is that the Phase 0 stamp was the FIRST write each run made,
and the first gated call is what stops a session with nobody in it. **That is a hypothesis and it
has not been tested.** The push defect above is the precedent: an earlier attempt committed a
confident explanation that the next push falsified, and a wrong explanation in this file is worse
than none, because the next session inherits it and stops looking.

**So this fix is necessary and it may not be sufficient.** It removes two to three writes from
every run, and the branch already carried what they encoded, so it is right on its own terms. But
if the first-gated-write hypothesis holds, a run will stop at whatever write comes next, and **the
durable fix is host-side rather than in this repo**: the environment the schedule runs in has to
be configured to allow the run's tools. Nothing in `.claude/settings.json` can do it, and a sixth
attempt in that file would be the fifth mistake again.

The lesson that does generalise: **a rule that makes an unattended run depend on a permission it
cannot grant itself is not fixable by rewording the rule**, by enumerating command strings, or by
changing which tool makes the call. Remove the dependency where one exists. Here it was a file
nobody needed, because CI had been reading the lane off the branch since 2026-08-16.

`scripts/shared/actor_stamp_shape.py` reads `CLAUDE.md`, `prompts/*.md` and the skill and agent
files and **fails the build** if any of them tells a session to write the stamp by any means, the
Write tool now included. That gate used to bless the Write tool, which is to say the gate itself
carried the fifth failed fix. Prose is what the earlier attempts were, and prose is what the
session read and then contradicted. GATE_LESSONS' oldest shape is a rule stated in config with
nothing in between checking it.

## Scratch never leaves the working tree (AUTHORITATIVE)

**Every temporary file a run writes goes in `out/<run>/tmp/`. Never `/tmp`, never a system
scratchpad, never anywhere outside this directory.** `out/` is gitignored, so nothing there is
ever committed, and it is inside the tree, which is the whole point.

This is not tidiness. The Bash sandbox and the permission mode are two different mechanisms, and
knowing that is worth an afternoon. `.claude/settings.json` has set `bypassPermissions` since
2026-08-11, and a cloud session ignores it (the protected-path account under "A run never stops
to ask about permissions" has the documentation). A SANDBOXED command that writes outside the
working tree still cannot complete, and the tool then stops and asks to re-run it unsandboxed,
which is a prompt the permission mode does not reach. An unattended run has nobody to answer it.

On 2026-08-20 the owner was interrupted twice by exactly this, on a run whose permissions had been
right for nine days, and the session went looking at the permission mode first because that is
where the word permission is. A run that keeps its scratch inside the tree never has the problem
and never has to work out why it had it.

The exception a session will reach for and must not take: writing outside the tree "just this
once" for a big file. `out/<run>/tmp/` takes big files.

## Layout

- `prompts/` — `daily_routine.md` is the single source of truth for the one daily routine, which
  maintains the record and then ships the deck. `ROUTINE_PROMPT.txt` is the thin pointer pasted
  into the routines UI, which says only "read that file from main and execute it", deliberately,
  so the real instructions stay versioned and reviewable rather than living in a settings box
  nobody diffs.
- `knowledge/` — `shared/` (Texas research, design doctrine, vernacular, sources registry),
  `carousel/` (`TECHNIQUE_LIBRARY.md`, what the engine can execute and how each technique fails;
  `CAPTION_CRAFT.md`, the caption room's menus and the anti-template law; `SLIDE_DOSSIER_SPEC.md`,
  the planning format `dossier_check` enforces; `DESIGN_DOCTRINE.md`; `FIELD_NOTES.md`). Video
  craft doctrine lives in `TexasAIDispatch`.
  **`shared/GATE_LESSONS.md` is required reading before you add a gate, trust one, or conclude
  that a green suite means a correct product.** It is the record of faults that shipped with
  every check passing, and each entry names what to check instead. A green suite has been wrong
  about the colour of the page, the promise on the front page, the state of a badge, whether the
  site published at all, whether a rule in this repo's own ownership map was even in force,
  whether a gate was connected to anything, and prose that had not rendered yet.
- `config/` — `brand.yaml` (shared Texas voice and tokens), then per-surface subdirectories.
- `ledger/` — committed state. `docket.json` is the public record. `carousel/` holds the variety
  ledgers (`topics`, `artwork`, `captions`), the automation-change trail (`upgrades`) and
  `instincts.json`, the craft memory. **An instinct records the DATES it was confirmed and
  contradicted and carries no confidence number**, because confidence is derived by
  `scripts/carousel/instincts.py` and a machine allowed to grade its own lesson grades it high.
- `scripts/` — namespaced by owning actor: `site/`, `carousel/`, `gridwatch/`, `shared/`. The
  carousel gates each carry the defect they exist for in their own docstring, and each has a
  `--self-test` that replays it. Run them by EXIT CODE, never by reading the last line: a report
  that prints advice on failure and one clean line on success looks reassuring either way under
  `tail -1`, and that has shipped a red gate here before.
  **THE LOCAL SUITE IS A PRE-MERGE TOOL. NEVER RUN IT AFTER THE MERGE HAS LANDED.** Owner's
  instruction, 2026-09-03, on being shown a run that merged a pull request and then went on
  waiting for a local suite it had started earlier: *"its okay if it runs stuff locally, but it
  shouldnt be doing it AFTER a merge thats stupid and makes zero sense."*

  It is right and it is worth saying why, because the mistake did not feel like one from inside.
  **A check is worth its time only while its answer can still change what lands.** Before the
  merge, a red step here means do not merge, which is a decision. After the merge the code is on
  `main`, the question is settled, and the same forty minutes buy an answer nothing can act on.
  If `main` is red, CI on `main` already says so, in four minutes, with the failing job's log in
  hand.

  So the shape is: run what you are going to run, THEN push, THEN merge on CI green, THEN stop.
  A local run still in flight when the merge lands is finished work, and the correct thing to do
  with it is kill it. **Waiting on it is not diligence, it is a run that has not noticed the
  question is closed.**

  Same rule, said once for the surface it is easiest to miss: after a merge, do not re-run a
  gate, re-derive a figure, or re-read a page to confirm what the merge already carried. Read
  CI once, and only if it is red is there anything to do.

  **Which local run to make, before the push.** The gates you touched and the checks that read
  what you changed, always, because each is seconds. `python3 scripts/shared/guards_local.py`
  when you want the whole of `guards.yml`, most usefully to reproduce a step CI has already gone
  red on, where `--only <step>` narrows it to the one thing that failed. `--fast` defers the node
  suites while you iterate. Running every `--self-test` instead is the wrong half and has already
  put a red build on the board, because a self-test proves the checker can go red and only the
  checker proves the product is clean.

  None of this moves the merge rule. **CI green on the head SHA is still what says the work may
  LAND**, and the carousel no. 7 paragraphs above stand unchanged.

  **NEVER READ THAT RUNNER'S LOG TO DECIDE WHETHER IT PASSED. Ask `guards_local.py --verdict`.**
  On 2026-08-27 a run piped the suite to a file, read the file, saw a wall of `ok` with no
  `FAIL`, and recorded a pass. It had read line 84 of an eventual 269. The first `FAIL` was at
  line 100 and ten of 120 steps had failed. Two CI jobs went red on a branch the run believed
  was clean, and everything after it, two extra pull requests and a wrong diagnosis of the CI
  trigger, descends from that one read.

  **Reading more carefully would not have helped, and that is the whole point.** At line 84 the
  output of a run that will fail at step 100 is byte for byte identical to the output of a run
  that will pass. The signal is never in the content. It is in whether the writer has stopped
  writing, which a reader looking at content cannot see. Grepping for `FAIL` rather than reading
  `tail -1` is the discipline this file already demanded, and it is about WHICH LINES you read,
  so it protected nothing here.

  So the verdict does not live in the log. `--verdict` reads `out/gates/verdict.json`, which is
  deleted when a run starts, written once at the end by an atomic rename, and stamped with the
  commit, the working tree digest and the invocation. It exits 0 only for a complete, current,
  full-coverage, all-passed run. A suite in flight, a suite that died, a verdict from another
  branch, a verdict from before your last edit and a `--fast` verdict all exit non-zero and say
  which one they are. There is no state a half-finished run can leave that reads as green.
  Its `--self-test` walks all of them and CI runs it. GATE_LESSONS 69.
- `assets/` — committed fonts, art libraries, Texas geodata, places gazetteer.
- The front page's one live line is the **weather chip**, in `scripts/site/frontchip.py` with
  its collector in `scripts/gridwatch/weather_collect.py`.
  `knowledge/shared/TEXAS_TELEMETRY.md` section 0 is the decision record.
  **It ROTATES.** Four candidates run (hundred degree days, freezing nights, nights over 80,
  inches of rain) and it leads with whichever is furthest from its own normal for that date,
  measured in units of that metric's own year to year spread so unlike things can be ranked.
  **The comparison that chooses is never published** — the page prints only what was measured
  and what is normal, because a standard score is good enough to rank four candidates and not
  a number this project would put its name on. A candidate is in season when its own normal
  sits between 10 and 98 percent of a full cycle, so no calendar table decides anything and a
  new candidate needs no window written for it. Its self-test walks all 366 days and asserts
  the chip is never left with nothing to say.
  Two rules inherited from the research: there is no canonical statewide station, so it is
  **city scoped and names the city**, and the station is picked on a stated rule rather than
  for producing the most striking number.
  Its ledger, `ledger/gridwatch/weather.jsonl`, is the one series here that is **not**
  append-only, because NCEI is a permanent archive and every line is re-derivable. That
  carve-out is stated in `ownership.yaml` and nowhere else.
- `docs/` — the published site (GitHub Pages). GENERATED. Never hand-edit.
- `out/` — per-run scratch (gitignored). `runs/` — shipped artifacts, merged to main each run.

## Gmail

The connector authenticates as `docket@alaskaaihq.com`. Scripts set it as a module constant
`DRAFT_TO`, never the account-relative `me` — the connector rejects `me` outright with
"Invalid email address", so every run that tries it burns a step rediscovering the address.
If the mailbox moves, change `DRAFT_TO` and this paragraph, and nothing else.

These routines DRAFT ONLY and never send.

**Pass the payload's body as `htmlBody`, never as `body`.** `body` is plain text. On 2026-09-23 a
run passed a hand-written plain text summary as `body`, no slide thumbnail rendered, and the owner
opened a draft with no deck in it. Read the draft back with `get_draft` before reporting it.

## House rules that never bend

Dates take the ordinal, month first. "August 11th", never "11 August" and never a bare
"August 11". ISO stays correct for a citation stamp or a ledger field.
**A DATE IN THE POST'S OWN YEAR CARRIES NO YEAR**, owner's instruction 2026-09-11, and this one is
about the LinkedIn copy rather than the site. Write "the item is dated September 4th" in a post
that goes out in 2026, never "September 4th, 2026". The year is not wrong, it is REDUNDANT: a
reader works it out from the fact that they are reading it this week, and the first two lines of a
post are the only real estate that surface has. The year STAYS on every other date, which is what
makes this a rule about redundancy rather than a rule against years. **The site is the exception
and it is deliberate.** A record page is a permanent archive somebody reaches years later out of a
search result, where a bare "September 5th" is ambiguous exactly when it matters most, so the
check lives in `caption_check.post_shape_problems` and never in `check()`, which also judges the
website. `sources_block.py` takes the year from the run directory's own name rather than from the
clock, so rebuilding an old run's first comment renders what that run published.
No em dashes or en dashes anywhere. Ranges read "X to Y".
No emojis. Straight quotes only.
**No colons and no semicolons in published copy.** Write two sentences. A semicolon is a full
stop that lost its nerve, and a colon in prose is a label bolted onto a sentence that could have
opened with the thing itself. A clock time and a ratio are numbers, not punctuation, and a
verbatim quote is never touched.
**Commas, two rules.** CONSTRUCTION, at any length: no comma after a coordinating conjunction or
a relative pronoun, and no hedge fenced off by a pair of commas. Write "A data center needs
electricity. Most cooling designs need water too", never "A data center needs electricity and,
in most cooling designs, water". DENSITY, over running prose: under the ceiling MEASURED ON THAT
SURFACE. The site's is 3.97 per 100 words, ten percent below its own measured 4.41. Three things
that number has to get right, and each was wrong once: it is measured on RUNNING PROSE, which is
what the gate reads, not whole-page text; it counts only the commas a WRITER CHOSE, since a date
comma and a thousands separator can't be split at; and it is measured on the corpus BEFORE any
comma rule touched it, because ten percent below an already-cut corpus is a ratchet that reaches
zero. Captions have no ceiling because no caption has shipped, and borrowing the site's would be
exactly the typed-in number the compute-not-generate law forbids. The cure is splitting the
sentence at the comma, never deleting the comma and leaving a run-on.
Never "cannot", always "can't".
Never open a sentence with "And" or "But".
No first person in published copy.
Every fact carries a claim-id and traces to a fetched source.
No topic repeats within 30 days. No two decks visually alike (ledger-enforced).
Honest scores, honest emails. If it is not in the claims file, it does not exist.
