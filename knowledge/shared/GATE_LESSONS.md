# How this machine has lied to itself

The living record of faults that shipped with every gate green. Read this before adding a gate,
before trusting one, and before concluding that a green suite means a correct product.

Nothing here is hypothetical. Every entry happened, and every entry has a gate now that was
replayed against the original defect and watched go red. A gate that has never been seen to fail
is a decoration, and the entries below are the argument for why.

The pattern across all of them is one sentence. **A checker sees what it reads, and the product is
what a reader receives.** Every fault below lived in the gap between those two things.

---

## 1. A composite is not its parts

The page rendered mauve while all 62 contrast pairings passed. Warm veils screening over a violet
ground at 9 percent lightness is mauve, and contrast does not care about hue: mauve at the right
luminance passes perfectly.

**What to check instead.** Sample the rendered pixel. `tests/page_ground.mjs` renders the page and
reads the ground where no content sits.

**Generalises to.** Any property that emerges from layering. Blend modes, opacity stacks, a filter
over a gradient. If the value a reader receives is computed by the compositor, only the compositor
can be asked.

## 2. A container's edge is not its content's edge

Every warm layer in the sky was anchored to the bottom of a fixed-height box with
`overflow:hidden`, so each reached full strength exactly where it was cut. The seam measured
`rgb(58,40,37)` above and `rgb(8,6,15)` below, a 106 step drop across one pixel, right across
the page.

**The fix is structural, not per-layer.** A fade on each layer holds until somebody adds a layer.
A mask on the container cannot be defeated. And the first repair moved the layers up out of the
fade, which relocated the edge rather than removing it: **peaks go above the fade, geometry goes
through it.**

## 3. Which token reached the element is not which token is correct

The front page says green means a door is open to you. The room badges and the countdowns were
painted in `accent`, the link colour, so the site contradicted its own instruction on 14 of 27
pages. Every token held its authored value. The defect was in the cascade.

**What to check instead.** Ask the browser for the computed colour of the element making the
promise, and compare it to the token the promise is about.

## 4. A signal colour equal to another role is not a signal

`signal_soon` was documented as the accent "doing double duty". That comment was the tell. The one
badge meaning "closes this week" was byte-identical to every link on the page.

**What to check.** When a palette reserves a colour, assert nothing else already holds it. A
reservation with a duplicate is not a reservation.

## 5. Specificity beats a media query

The mark was turned on by `.home .sky .lonestar` and turned off on phones by `.sky .lonestar`, one
class less specific, so it never came off. A media query is not a trump card.

**Write an override at the specificity of the rule it overrides.**

## 6. Styling by document shape breaks when the shape changes

The clearance under the sticky bar was `main > h1:first-child`. Item pages wrap their title in an
`<article>`, so it matched the pages somebody had opened and missed all 13 they had not.

**Put the rule on the container, and sweep every page rather than the three you were looking at.**
The all-pages sweep in `page_ground.mjs` found a phone clipping bug on its first run.

## 7. Furniture tokens on content

The county mesh used `rule`, the hairline divider, at 1.39 to 1, under a caption promising "every
county in Texas". A divider at that ratio is correct, because a divider is decoration and WCAG
1.4.11 asks nothing of decoration. The figure of a section is not a divider.

**Keep the threshold. Use stroke weight for quiet.** The temptation is to dim the colour, which
puts the geometry back under the floor.

## 8. The head is published copy

`house_style_check` scoped to `<main>`, so nothing had ever read the page metadata. The title
separator was an em dash on 26 of 27 pages. That string is the browser tab, every search result
and every shared link unfurl, and **more people read it than read the page.**

## 9. A branch that has not rendered has not been checked

These pages are written to be true at one record and to say more as the series grows, which is the
right design. It means whole paragraphs exist only at two records, or at fourteen. The water page's
comparison paragraph rendered for the first time the day a second reading landed, carrying a colon
and pushing the page over its comma ceiling, and it reached the deploy gate because nothing had
ever read it. The self-test fixtures already built that shape; the assertions on it only asked
structural questions.

**Lint every shape the fixtures build, as copy.** Applying this immediately found a semicolon in
the grid watch trend block, which needs 14 settled days to render and was a fortnight from a
reader.

**Generalises to.** Any output whose form depends on data volume, recency or completeness. An empty
state, a single-item state, a paginated state, a "no data yet" state. Each is prose somebody
eventually reads.

## 9a. A mode nothing ever opens is a mode nothing ever checks

The same fault as 9, in a wider form, and it cost the same bug twice.

Every check in `page_ground.mjs` opened the page with `colorScheme: 'dark'`. Every screenshot taken
during review forced it too. So the light register was never once looked at by anything, by a gate
or by a person. The owner opened the live site on a light machine and asked why the background was
pink.

It was. The dusk atmosphere rendered over cream paper with `mix-blend-mode: multiply`, and multiply
takes the darker of the two, so the only thing a red veil can do to cream paper is stain it.
Measured at `#F0E4D7`, twelve points of red over green, spread across a soft field the width of the
page. Small numbers, and a large soft field of warm-shifted cream reads as a colour regardless.

**Two lessons, and the second is the one that generalises.**

The design lesson: a night sky does not become a daylight version of itself by being turned down.
The atmosphere is a night sky or it is nothing. On paper the honest version of paper is paper.

The gate lesson: **enumerate the modes and check every one.** Colour scheme, viewport, reduced
motion, print, script disabled, locale. Each is a complete second rendering of the product. A suite
that only opens one of them is measuring a preference, not a page.

**What to check instead.** Where two modes are meant to agree, render both and **compare them**
rather than holding each to an absolute threshold. Two attempts at a warmth ceiling here failed on
the accent in the headline and then on the Lone Star's halo, both warm because they are supposed to
be. There is no number that separates "warm on purpose" from "stained". There is a very simple
check that a reader on a light machine gets the same page.

## 10. A deploy that depends on who pushed

`pages.yml` fired on `push` and nothing else. **A push made with `GITHUB_TOKEN` does not start a
workflow** — deliberate, to stop a workflow triggering itself forever. So the deploy ran for a
merge made with a user token and silently did not for a merge made by a bot.

A merged pull request left the live site on the previous build with every gate green and nothing
reporting a failure, because nothing had failed. **No run had started.**

This is the worst shape a fault can take here. The record said the change shipped, the ledger said
the machine improved, and the page a reader loads was old. There is no human at the keyboard.

**Any pipeline step that must happen needs a trigger that does not depend on the actor.** A
schedule is the only one that qualifies, which is why there is a two hourly backstop. Deploying an
unchanged site is a no-op; a missed deploy is permanent without one.

**Also.** Under `workflow_run` the default ref is the *triggering* run's SHA, so for a collector
that pushes, an unpinned checkout publishes the state that existed just before the thing being
published. Pin the ref.

---

## 11. A gate that compares two renders must freeze the motion

Once the sky was sped up to be visible, the check comparing a light-machine render against a dark
one started failing in CI at **"off by 8"** while passing five times out of five locally. The two
browser contexts load independently, so by the time each was photographed the clouds were at
different points in the drift, and a slower runner widens the gap. The gate was measuring
animation phase.

**A gate that depends on runner speed teaches people to press re-run**, which is worse than no
gate, because it also teaches them to ignore the real failure when it arrives.

**What to check instead.** Decide what the comparison is actually about. This one is about the
REGISTER, and motion is not part of that question, so both sides are frozen with
`animation: none !important` before the pixels are read. The separation is stark once you look:
a genuine register split measures 237, the phase flake measured 8.

**And where motion IS part of the question, sample it deterministically.** The ground-brightness
ceiling has to hold while a lit cloud drifts over a gutter, so it is checked at five fixed offsets
rewound with `animationDelay`, keeping the least favourable frame. One screenshot answers that by
luck. Five fixed ones answer it, and the message names the second it happened.

## 12. A rule can be repealed and still read perfectly

`ownership.yaml` is matched .gitignore style, last match wins. `scripts/site/**` was written near
the top as `owner: human`, with the note **"the gates. A routine that can edit the gate that judges
it has no gate."** Further down, in a different section, the same pattern was written again with
`rebuild_by: [carousel, gridwatch]`.

The second one won. For as long as it stood, the carousel could edit `site_build.py`,
`house_style_check.py` and `docket_build.py`: **every gate that judges it.** The file said the
opposite, in the plainest language anyone could write, and the sentence was worth nothing.

This is worse than a rule that is wrong, because a rule that is wrong can be read and disagreed
with. **A repealed rule still reads correctly.** Anyone auditing the file finds the strict sentence,
believes it, and stops looking. The `rebuild_by` in the winning rule even carried a note claiming it
meant "allowed to RUN it and commit the output", which the code does not implement and could not:
running a script needs no permission at all.

**What to check instead.** Ask each rule whether it still answers for its own namesake path. Build
the canonical path the rule exists to match, run it back through the resolver, and fail if a
different rule claims it. `ownership_check.py --self-test` does this against the shipped map on
every run, and **it found a second dead rule the moment it was switched on** — `scripts/site/ask_*.py`,
which a reordering had just buried under a broader rule. Two dead rules in a 190-line file that
had been read carefully several times.

**Generalises to.** Every last-match-wins or first-match-wins configuration: `.gitignore`, CSS
cascades, firewall tables, route tables, `CODEOWNERS`, redirect maps. In all of them a later broad
entry silently repeals an earlier specific one, and none of them warn. **If order decides meaning,
something has to test that each entry still means what it says.**

**Also worth naming.** The defect was found while merging two routines into one, because the merge
forced a re-read of who owns what. Consolidation is when this class of fault surfaces, so a merge
is the moment to check the boundary rather than assume it survived.

## 13. A self-test is not wiring

Found ten minutes after 12, during the same merge, and it is the same disease wearing different
clothes.

`port_audit`'s orphan check answers "is this script wired into the machine?" and the whole port
manifest exists because the last attempt at this **moved files over and never wired them up**. It
counted a script as wired if any workflow, prompt or script named it.

Every gate in this repo is named in `guards.yml` as `<gate>.py --self-test`. So every gate
satisfied the check permanently, no matter what. **For the entire class of file the check matters
most for, it could not fail.**

The cost was about to be real. Merging two routine prompts into one meant writing a fresh prompt
and deleting both old ones, which is exactly the operation that drops a gate by hand. Any gate left
out of the new prompt would have gone on passing, while being invoked by nothing, on the one
question this audit exists to answer.

**What to check instead.** Ask what the evidence actually proves. A self-test line proves the
script's own tests pass. That is a fact about the script and says nothing about anything calling it
in anger. The fix is one filter: a mention on a `--self-test` line is not a reference. Verified by
deleting the dedupe gate's invocation from the routine, green before, red after.

**The trap in the fix.** The obvious over-correction is "a gate must appear in a routine prompt".
That breaks the cron-driven collectors, which appear in no prompt by design and must not be dragged
into one. A real invocation in a workflow is still wiring. There is a self-test case for that too,
because the repair for one fault is a good place to introduce the next.

**Generalises to.** Any check whose evidence is "X is mentioned somewhere". Coverage that counts a
file as tested because a test file imports it. A dependency audit that counts a package as used
because a lockfile lists it. A dead-code sweep that counts a function as live because a test calls
it. **When the evidence and the question are one inference apart, the check answers the easier
question and reports it as the harder one.**

## 14. Your container is not the environment being checked

`ship_images` passed its self-test fifteen times locally and failed on the first push with
`Pillow and numpy are required`. The development container had them. The CI runner installed
`pyyaml` and nothing else.

The failure is trivial. **The tempting fix is the trap.** The obvious move is to make the self-test
skip when the library is absent, so the suite goes green everywhere. That would have produced a
green CI run in which the gate never executed, forever, and nobody would have looked again. A
skipped test and a passing test are the same colour.

**Install the dependency. Never skip the check.** The entire reason to run these in CI is that the
machine they run on is not the machine they were written on.

**What to check instead.** The audit is one line and worth running whenever a gate gains an
import: list every script CI invokes, list its non-stdlib imports, compare to the install step.
Note the trap inside the trap, which cost a second pass here: an anchored `^import` grep finds
nothing, because the import that matters is indented inside the `try` block that produces the
friendly error message.

**Generalises to.** Fonts, locales, timezones, a headless browser, a git identity, an environment
variable with a default in your shell profile. Every one of them is something the developer's
machine supplies silently and a fresh runner does not.

## 15. Fixtures written by the author of the detector agree with it

The end-to-end proof ran the whole chain on a real render for the first time. **Every gate's
self-tests were green before it started.** It found five defects in under an hour, and not one was
exotic.

- `aggregate_check` matched `\d{1,4}` and so read `2,600 streamlines` as **600**. It named a
  number the slide does not contain. **A gate that misreports a figure is worse than one that
  misses it**, because the run then hunts for something that was never there.
- The same gate flagged the slide counter, `slide one of four`, on every slide. Nine findings a
  deck, forever, none real. A gate that cries wolf nine times teaches the run to scroll past the
  tenth.
- It also refused a count computed the way the law requires. `254 counties` is `len()` of the
  committed topojson, not a tally of 254 claims, and the declaration format could only express
  the claim route. **It would have taught the first real run that the honest route fails and the
  shortcut passes.**
- `gate_status` marked `claims.json` STALE for predating the render. Claims are written in Phase
  6 and the art is built in Phase 11, so that is true of every run that has ever gone right. Three
  rows would have been red forever, and **a row that is always red is ignored exactly as fast as
  one that is always green.**
- The same gate read `aggregates.json`, an INPUT the run authors, as though it were a report. So
  it printed a stale row saying "re-run it" that re-running could not clear, because a check does
  not rewrite its own input. **Inputs precede the render. Reports describe it**, and a status row
  belongs to a report.

The pattern is one sentence. **A fixture written by the same hand as the detector agrees with the
detector.** Every one of these needed a real artifact from a real render to surface, and a real
artifact is the only thing that carries the shapes nobody thought to write down: a thousands
separator, a slide counter, a file that legitimately precedes the thing it is being compared to.

**What to check instead.** Run the whole chain on real output before believing the suite. The
proof is not a formality at the end of the work, it is the first honest measurement of it, and it
is cheap: one render and one pass through every gate.

---

## 16. A gate is only as strong as its narrowest scope

`numeral_lint` checks a page's numerals against the set of values the build computed. The first
wiring merged the grid watch's and water watch's authorised sets into one set shared by all 48
pages. Those two pages authorise an hourly load series and a full fuel mix, several hundred
figures spanning every magnitude a page might print, so almost any three to five digit number
was authorised somewhere on the site. A figure typed into a docket page passed because an
unrelated megawatt reading happened to match it.

**What to check.** Widening an allowlist to make a gate green is the same move as switching the
gate off, and it does not look like it. When a gate is scoped per page, plant a value that is
legitimately authorised on a DIFFERENT page and require a red build. `site_build --self-test`
does exactly that, with a real grid watch figure.

## 17. Deleting authorised strings by substring dissolves every figure

Same gate, second and worse cause. The scanner removed each authorised string from the text and
reported whatever digits survived. Any real page authorises all ten single digits within a few
counts and dates, so `8,927` was deleted one character at a time by four authorisations that had
nothing to do with it. Nothing survived, so nothing was ever reported. **Every numeral on the
site had been dissolving from the inside for two waves, and the module's own docstring claimed
it was "strong on the figures that matter, which are the multi digit and decimal ones".**

**What to check instead.** Tokenise first, then ask of each whole token whether the build
computed THAT number. A multi token phrase like "4pm to 5pm" is still consumed whole, and a
phrase is defined as an authorised string carrying a character a numeral token cannot contain,
which is what stops it splitting a figure it merely overlaps.

**Generalises to.** Any checker that works by removing what is allowed and reporting the
remainder. Subtraction over a shared alphabet is not filtering.

## 18. A reference is a dependency even when it is not a link

Item `tx-2026-0006` tells a reader "See item tx-2026-0010 for that page's statutory basis", and
there is no `tx-2026-0010`. Fact checking culled it and the pointer survived. Three checks nearly
caught it and could not: the link checker reads `href` attributes and this is prose, the claims
gate checks that claims have sources and this is not a claim, and the numeral gate's own
self-test **used that same id** as its example of a legitimate cross-reference exemption.

**What to check.** A checker that knows the id space, over every prose field. Prose that names
another record is asserting that record exists.

**And note the second half.** A test fixture demonstrating an exemption taught the suite that the
broken id was fine. See entry 15: fixtures written beside a detector agree with it.

## 19. A true count of the wrong set reads exactly like a true count

The ask engine answered "El Paso" with "9 items in the El Paso area", one line above a note
saying nothing had been found in either of El Paso's counties. All nine were statewide. Every
number in that sentence was correct, so no count assertion could see it, and a reader in El Paso
would have read it as local coverage.

The same shape hit the water page independently: "20 of the 67 statistical areas", where 67 is
the CBSA count and the 20 included two metropolitan divisions, which are not CBSAs and are both
inside one. Dallas and Fort Worth were counted twice and their shared area zero times. Both
numerals were computed from data and `numeral_lint` passed them.

**What to check.** Recompute the set the headline claims to describe, from the same data, and
compare. `tests/ask_engine.mjs` does it for all 87 place questions. For a ratio, assert the
partition closes: `lined + unlined == areas` is what would have caught the water page.

**The general rule, and it bounds every gate in this repo.** A gate that checks whether a figure
was COMPUTED cannot check whether it was the RIGHT figure. The compute-not-generate law protects
against a number nobody derived. It does not protect against a number derived from the wrong
population, and only reading the sentence catches that.

## 20. One value meaning two things

`page(active="")` marked the current nav entry. `""` is also Home's own href. So every item page
and every topic page shipped `aria-current="page"` on Home, telling a screen reader it was on the
front page while it read an item. Every page looked right, because the marker is a small
underline and Home is where a reader's eye is not.

**What to check.** A sentinel that collides with a real value is not a sentinel. Use `None`, and
test the sentinel before the comparison rather than letting it fall out of one.

## 21. A workflow's implicit default is a repo setting, and a setting is not a rule

`gridwatch.yml` ran `actions/checkout@v4` with no `ref`, which takes the repository's default
branch, and every push in the same job targeted `main`. Those were the same branch only because
nobody had changed the setting, and this repository's default is a feature branch.

**What that bought while it "worked".** The job checked out the feature branch, committed the
reading on top of it, and rebased onto `origin/main`. While main was an ancestor the rebase was a
no-op and the push fast-forwarded, so every run was green **while a data collection cron pushed
unreviewed feature work to trunk once a day.** Nothing in the repo grants it that. The
`ownership_check` step immediately above it passed, because it checks the FILES a job wrote, not
the COMMITS a job pushes.

**What it cost when it broke.** A squash merge left trunk and the feature branch holding
identical content through different history. The rebase replayed the branch over its own squashed
self, conflicted in two files, and both of that day's runs died with the reading in the workspace.
ERCOT keeps no archive, so that day is gone.

**What to check.** Any step that names a branch must name it everywhere, including the checkout.
An implicit ref in a job with an explicit push target is a mismatch waiting for a setting to
change. And **`pages.yml` in this same repo already pinned `ref: main`, with a comment explaining
why** — the fix existed twenty lines away in a sibling file and had not been carried across. When
a workflow learns something about refs, grep the other workflows the same day.

**The second half, which is its own lesson.** A push retry loop must not push after a failed
rebase. This one aborted the rebase and pushed anyway, so one conflict burned all five attempts
printing the same rejection five times and buried the actual cause under the noise. The loop now
also refuses to push when it is more than one commit ahead of trunk, which is the check that would
have caught the whole thing on day one.

## 22. A CSS rule can be correct, matched, and dead, and it reads as fixed

The front page chip wrapped onto a third line on a phone, carrying one word. The fix was to give
up a little letter-spacing below 30rem, and it was written into the `max-width:30rem` block that
already existed for hiding the star.

**It changed nothing.** The measured height was 78px before and 78px after. The selector was
right, the media query matched, the property was valid, and the value was sensible.

A media query carries **no specificity of its own**. That block sits above the `.tele` rule in the
sheet, so `.tele{letter-spacing:.13em}` and `.tele{letter-spacing:.095em}` were two rules of equal
specificity and the later one won. Moving the same three lines below the base rule fixed it.

**What to check.** An override written into a media query is only an override if it comes AFTER
the rule it overrides in source order. Grouping narrow-screen rules into one tidy block near the
top of a stylesheet is exactly how this happens, because the tidiness is what puts them before
the declarations they mean to beat.

**And the broader one, which is the reason this is in this file.** The measurement is what caught
it. The rule was reviewed twice and read correctly both times, because it *was* correct. Nothing
short of measuring the rendered box could tell the difference between this and a working fix.
Every CSS change that claims a measurable effect gets measured after, in a browser, on the built
page. Reading the diff is not verification of a stylesheet.

## 23. A test that encodes the workaround defends the bug

The Lone Star was `display:none` below 30rem, because its glow landed in the wrapped
navigation. Two tests then asserted that arrangement. `page_ground.mjs` required the mark to be
absent on a phone, in a check named "and not on a phone". `responsive.mjs` permitted hiding it
wherever a collision existed, so a stylesheet hiding it on every phone was green by
construction.

**The owner found it by looking at the site.** Both suites were passing, and one of them was
written specifically to check that mark.

**What to check.** When a fix is "hide it", the test that follows must assert the OUTCOME the
reader wants, not the mechanism chosen. "The mark is visible and touches nothing" is a
requirement. "The mark is hidden where it would touch something" is a restatement of the
workaround, and it will hold just as happily when the workaround has eaten the whole feature.

The sweep that found the truth also found a band nobody had looked at: from 488 to 592px the
mark sat directly on the "Services" and "About" links, at widths where it was never hidden and
never tested.

## 24. A clipped numeral is not a layout bug

The load chart's axis type steps up to 27 user units on a phone so it survives being scaled
down. The left gutter that type is drawn into was 52 units and fixed in Python, while the type
size is a CSS breakpoint, so neither could see the other. Six characters at 27 units is about
97, and it did not fit.

**It did not render as a cut. It rendered as "500", where the record says 2,500.** The part
that fell off the left edge was "2,". The residual axis was wrong, by a factor of five, on
every phone, under a `numeral_lint` that had authorised the correct value and a legibility test
that had measured the correct font size.

**What to check.** `numeral_lint` proves a published figure traces to a computation. It reads
the DOM, so it cannot see that the glyphs were painted outside the canvas. Any figure drawn
into a fixed coordinate space needs its rendered box measured against that space, and
`responsive.mjs` now does exactly that at fifteen widths. Legible and present are two
questions, and the suite was only asking one.

The generalisation is worth keeping: **whenever a value's geometry lives in one language and
its type size lives in another, something has to measure the pair.** Every clipped label here
came from that split.

## Two process faults, which caused more lost time than any bug above

**Reading the last line of a report.** `house_style_check` prints an advice footer on failure and a
single clean line on success, so `tail -1` looks reassuring either way. A gate was red locally and
got pushed anyway. **Check exit codes, never last lines.**

**Reading a rendering artefact as a bug.** A screenshot taken during a smooth scroll captures
sticky elements at a stale offset, and a `fullPage` capture does not scroll, so intersection
revealed sections photograph as a blank middle no reader ever sees. Both were investigated as
layout bugs before being recognised. Scroll with `behavior:'instant'` and settle before capturing.

## 25. A token pairing is not the colour a reader receives

`scripts/site/theme.py` measures contrast, and it measures TOKEN against TOKEN. That is exactly
right for `--ink` on the page ground and blind to anything a rule composites out of two tokens.

The topic chip a reader is standing on is `--on-accent` on `--accent-deep`. That pairing is in
the list, it measures 4.52, it passes. The count numeral beside it sat in a well of
`color-mix(in srgb,#000 24%,transparent)` laid over the same ember, and **no token names that
colour, so no pairing existed for it.** It shipped at 2.92 with the suite green.

The mechanical mistake is worth naming because it will recur. Every other chip on that row is
light ink on a dark ground, where mixing black into a well RAISES contrast. That one is dark ink
on a light ground, where the identical declaration LOWERS it. One rule, two grounds, opposite
outcomes, and nothing in a stylesheet can tell you which you have.

**What to check.** `tests/text_contrast.mjs` walks the built pages and, for every run of visible
text, composites the whole ancestor background stack down to the page ground the way a browser
does, then measures the glyph colour against THAT. 2,729 runs across 56 pages. It declines text
over an image or gradient ground, because there is no single ground to measure, and it PRINTS the
count it declined on success as well as on failure, so a run that covered almost nothing cannot
read as a run that found nothing.

## 26. A gate that mis-parses its own input invents failures, and they are convincing

The first draft of that contrast gate scraped four numbers out of a computed colour with
`/[\d.]+/g`. Correct for `rgb(180, 102, 79)`. Silently wrong for `color(srgb 1 1 1 / 0.34)`,
which is what Chrome returns for anything built with `color-mix()`: those channels run 0 to 1,
not 0 to 255, so a 34 percent white well parsed as `rgb(1,1,1)` and the gate reported a
perfectly legible numeral at 2.42.

**It reported the fix as worse than the bug**, 2.42 against 2.92, which is the most persuasive
shape a false failure can take: it looks like evidence you made things worse, and the obvious
next move is to revert a correct change. The tell was that the arithmetic did not reconcile.
34 percent white over that ember is about 7.5 to near-black ink, and no amount of squinting at
the stylesheet gets to 2.42.

Note what saved it, because it is cheap and it is not automatic: the original 2.92 reading was
right ONLY by coincidence. `color(srgb 0 0 0 / 0.24)` parses identically in both scales, because
zero is zero. The parser was already broken when it caught the real bug.

**What to check.** Do not parse a browser's output with a regular expression when the browser
will hand you the answer. That gate now paints one pixel and reads it back, which is correct in
any colour syntax Chrome accepts including ones that do not exist yet. And prove a new gate
against the defect it was written for: revert the fix, watch it go red at the expected number,
restore. Ours prints 2.92, which is the figure hand arithmetic gives.

## 27. Three small paddings are one big hole

A phone screenshot from the owner: the whole first screen of the about page was a wordmark, a
navigation, and a field of stars, with the headline pushed off the bottom. Nothing in it looked
broken enough to point at.

Four measured things were adding up, and each was defensible alone. The nav wrapped, because
eight labels need 327 pixels of text and the seven gaps add 123 more; that cost 34 pixels of
masthead and left ABOUT alone on a second row, which does not read as navigation, it reads as a
rendering fault. `main` spent `6vh`. The hero spent `9vh` on top of its own 26 of margin. On a
915 pixel phone that is 164 pixels of nothing under a 97 pixel masthead.

**`vh` is a proportion of the window, which is the right instinct on a laptop and the wrong one
on a phone**, where the window is tall, narrow, and already carrying a masthead a desktop hides.
Every one of those rules was written and reviewed on a wide screen where it looks like air.

**What to check.** No gate here measures how much of the first screen is empty, and the reason
is that a threshold for that would be taste with a number bolted on. What is asserted instead is
the thing that has a right answer: `responsive.mjs` now checks that the nav is ONE row at every
width AND that the last link can be scrolled into view, together. Either alone is passable by a
fault, since a row that never wraps is trivially achieved by clipping four sections away.

## 28. A pass by half a unit is a coin flip, and the runner calls it

`responsive.mjs` asserts that no chart label falls outside the drawing. It passed locally and
failed in CI **on the same commit and the same bytes**: `320px cut -2,500`.

Neither machine was wrong. The chart's left gutter was a constant of 108, correct when it was
measured, and the residual strip's ceiling moves with the data. The day it reached 2,500 the
negative label became six characters wanting 100.4 units of the 100 the gutter leaves. Under
half a unit, decided by which fonts a machine happens to have installed. **The runner's fonts
are what a reader with a web font still loading is looking at**, so the red result was the
honest one and the green one was luck.

Two things were wrong and only one of them was the number.

**The gutter was typed, against labels that change daily.** It is computed now, from every
string that actually gets drawn into it, which meant factoring the residual ceiling out so the
gutter and the strip cannot disagree about how wide `-2,500` is. The advance-width estimate
went from 0.62 to 0.66 for the same reason: 0.62 is about right for the face this site serves
and is not a BOUND, and a layout bound has to hold for the fallback too.

**The assertion had no margin.** "Not outside the box" is satisfied at 0.1 units of clearance,
and 0.1 units is not a passing layout, it is an unresolved one. Labels now have to clear the
drawing by 2 units. That change alone found a second thing: the `GW` caption was anchored flush
at x=0, one antialiasing pixel from being clipped on any machine.

**The general rule.** When a check is a geometric inequality, assert a margin, not the
inequality. A tolerance of zero turns every rounding difference between two machines into a
flapping test, and flapping tests get their failures explained away.

## 29. A gate that passes by collision is not passing

The water watch page printed four percentages that its own module did not authorise. It passed
anyway, for months, because `_authorised_numerals` unions the whole record's counts and 42, 71,
76 and 93 all happened to equal some unrelated docket figure.

Growing the record from 13 items to 58 changed those counts. The coincidence lapsed and four
phantom numerals appeared on a page nobody had touched, which is how it was finally seen.

Underneath was a second fault, and it is the sharper one. Phrase removal in `numeral_lint` was a
plain `str.replace`. The set carried a bare `"0%"` from an unrelated computation, the page
printed `"Amarillo 42.0%"`, and the replace took the `0%` out of the MIDDLE of the percentage
and left `42.` behind. **The scanner then reported a stray 42 on a figure that was correct.**
The file's own comment claimed longest-first ordering prevented exactly this, and it only does
when a longer authorised phrase covers the same span.

**What to check.** Removal is anchored now: a phrase may not begin inside a number and may not
end immediately before more digits. And the general rule, which `_watch_numerals` already
records one level up: **a gate is only as strong as its narrowest scope, and a union is not a
scope.** If a page passes because some other page computed the same integer, nothing has been
checked.

## 30. Reader copy is every field a page renders, not the two the gate was told about

`docket_build`'s copy gates read `title`, `summary` and `public_access.how`. The site renders
more than that: a claim's own `text`, and the `note` on every key date. Neither was ever checked
at the record layer, so vote counts written `7-0`, a bare `May 20` and an agenda code reading as
the first person all passed the record's gates and were caught later by
`house_style_check.py`, which reads the built page instead.

That is the right backstop and the wrong place to find out. The record layer knows which item is
wrong and can say so; the page layer knows a file under `docs/` is wrong and has to be traced
back. The gap also means the RECORD can hold copy the SITE will reject, which is a build that
fails on a ledger nobody edited.

**What to check.** When a gate names the fields it reads, that list is a claim about what the
page renders, and it goes stale the moment a template starts rendering one more field. Diff the
two: every string a builder interpolates into a page is reader copy, whoever wrote it.

## 31. Nine green suites and nobody had looked at the page

Every gate in this repository passed. `house_style_check` clean across 147 pages,
`site_fresh_check` byte identical, `text_contrast` over 7,713 runs of text, `responsive`,
`page_ground`, `ask_engine`, `numeral_lint`, the docket's eight. Then the owner asked for a
LOOK at the pages, and one pass of screenshots found three faults in ten minutes.

**The atmosphere was painting on top of the record.** `.sky` is a positioned element at
z-index 0 and `main` is a static one, and a positioned box paints after every non-positioned
block in the same stacking context. So the weather layer had been over the copy the whole time,
and `pointer-events:none` hid it from everything that hit tests. The tumbleweed made it visible
by rolling across the front page's own statistics, the record's map and the grid chart's
residual strip, in the accent colour, on top.

**A badge contradicted its own page.** TCEQ's preliminary decision on the Crusoe plant wore
"NO FORMAL PROCESS" two inches above a summary saying comments are due within thirty days and a
section headed "How to take part". The upstream demotion was correct, since a window with no
close date cannot be `open_comment`. The label it demoted to made a claim about the world that
the record had never checked.

**The front page advertised nothing.** Two of four counters read "00", zero padded, on a page
arguing the record is substantial.

Not one of these is a thing a checker can see. `page_ground` samples points where content is
NOT. `text_contrast` composites background COLOURS and cannot see a drawing laid over a
numeral. `numeral_lint` proved "00" traced to a computation, which it did. `house_style_check`
read the badge as three well-formed words. Every gate answered its own question correctly.

**And when the fix is a layout choice, measure the options rather than argue them.** The
water watch's metro table was four columns in 380 pixels, and the bar cell was taking 131
of them from a `width:40%` and a 6rem floor while the metro name got 100 and wrapped to two
lines with the federal delineation wrapping to two more. Four candidates were rendered and
measured: dropping the bar column was the shortest table by a little and was the WRONG
answer, because the caption tells a reader the length carries the comparison and a width
where the bar is absent makes the caption lie. Narrowing it kept every column and every
figure, gave the name 176 pixels instead of 100, and took the worst row from 118 to 75.

**What to check.** A gate answers the question it was given. It cannot notice that the page is
self-contradictory, that a decoration is on top of the data, or that a true number is the wrong
thing to lead with. **Look at the rendered pages after any change you did not visually
confirm**, at the widths a reader uses, and treat a green suite as evidence that the things you
thought to ask about are fine rather than that the product is.

## 32. Running every self-test is not running the gates

The homepage grew a scanner section whose button read "Scan my business". `house_style_check`
refuses first person in published copy, it ran against the built site in CI, and it went red on
the first push.

Locally the change had been "verified" by running every `--self-test` under `scripts/`, and all
of them passed. They were the wrong half. **A self-test proves the checker can go red. Only the
checker proves the product is clean.** That distinction is the oldest lesson in this file and it
was still arrived at again by the same route, which is the part worth recording: knowing a
principle and having a way to act on it are different things.

The reason the wrong half got run is mechanical rather than careless. `guards.yml` is fifty
steps. Nothing could run them, so "run the gates before pushing" meant remembering fifty
commands, and what anybody remembers under time pressure is the shape of a list rather than the
list. The self-tests are the memorable shape: one flag, uniform across every script, greppable.
The gates are the part that varies.

The defect itself came from the sibling repo, cleanly. That site's button says SCAN MY BUSINESS
and its checker does not read first person, so the copy arrived intact and correct by its own
rules and wrong by ours. **A rule the source repo does not enforce is a rule its copy will not
carry.** Anything ported is only as clean as the strictest gate on the receiving side, which is
an argument for running the receiving side's gates on the day the port lands rather than the day
after.

**What to check instead.** `scripts/shared/guards_local.py` runs the workflow's steps here, by
exit code, in one command. It reads `guards.yml` rather than keeping its own list, because a
runner with a hand-maintained list is a second source of truth that reports green over the step
CI added last week. It refuses to report a clean run over zero parsed steps, and it names every
step it skipped instead of folding them into a total.

**Generalises to.** Any ritual that stands in for a check. If the honest version is long and the
convenient version is short, the convenient one is what gets run, and no amount of writing the
rule down changes that. Make the honest version one command.

---

## 33. A gate's own exemption is where the next unread surface grows

`house_style_check` strips `<script>` before it lints, and the reason is good and is written
down: the ask page ships its whole engine inline, and a JavaScript identifier `i` was being read
as a first person pronoun. `numeral_lint` strips the same block for the same reason, after a
build failed all 48 pages on the `8` in `scrollY>8`.

Both exemptions were correct. Neither was wrong on the day it was added.

Then the structured data spine began emitting 633 generated question and answer pairs into
`<script type="application/ld+json">`, and the site acquired **its largest single surface of
published prose that no gate read.** Those sentences are quoted by answer engines and read back
to people. They are exactly as public as the page body and were exactly as checked as a comment.

Nothing went red. The exemption did precisely what it was written to do.

**What to check instead.** When you add an exemption, write down what it is exempting and what
would make that wrong later. An exemption is a promise about the CONTENT of a region, not about
the region itself: "script tags hold code" was true, and the moment a script tag held prose the
promise expired silently. `schema_check.py` now reads inside the block the other two skip.

**Two smaller faults from the same build, both worth their own line.**

There were TWO numeral tokenisers. `numeral_lint` had already met the bug where a token that may
contain a comma but need not END on a digit swallows the sentence's punctuation, had documented
it, and had fixed it. The new module wrote its own regex and met the identical bug, so "Room
170, Austin" came back as the token "170," and a correctly rendered address looked like an
invented figure. The lesson is not that the regex was wrong. **It is that there was a second
regex at all**, in a repo whose stated rule is that a thing written twice is wrong in both
places at once.

And the first version of the numeral check compared generated sentences against the PAGE'S
RENDERED TEXT. The page prints a date as `2021-06-08` and the sentence prints it as "June 8th",
so every correctly computed day number was reported as unauthorised. A gate that reports a
correct product as a violation is how a gate gets switched off, and the fix was to check against
the LEDGER, which is the input both of them derive from.

**Generalises to.** Any rule of the form "region X is not copy". It is a claim about what
somebody puts in X, and nobody tells the linter when that changes.

---

---

## The rule for setting a threshold

Two thresholds here were set by measuring our own corpus, and only one of them was safe.

The comma ceiling is 3.97, ten percent below the site's own measured 4.41. That works **only**
because it is written down as a one time move off an unconstrained corpus. Re-deriving it from a
corpus it has already tightened is a ratchet with no floor, and three rounds arrive at zero.

So the sentence-length backstop is **not** measured from us. It is 30 words, the point plain
language guidance puts a reader at having to re-read. An external threshold cannot creep, because
it was never derived from us.

**Prefer an external standard. If you must measure your own corpus, say in the file that it is a
one time move and record the date.** And keep the target separate from the backstop: the target is
taste and belongs in `config/brand.yaml` where a writer reads it; the backstop is an edge and
belongs in the linter.

## 35. A checker that cannot see the form the product actually ships

The month abbreviation rule in `caption_check` matched `Aug 31` and not `AUG 31`. Its own
self test proved it fired, on `"Filed Aug 11."`, and stayed green for as long as it existed.

`short_date()` returns `f"{d:%b} {d.day}".upper()`. Uppercase is the only form this site has
ever rendered an abbreviated month in. So the rule could see every case that was not on the
site and could not see the one case that was, and the self test agreed with it, because the
self test was written from the rule rather than from the page.

May was the only month it ever caught, through a different rule that happened to match a
three letter month spelled in full. That is what made the gap visible at all, and it was
luck.

Adding `re.IGNORECASE` immediately turned up three real violations on the front page.

**What to check instead.** When you write a rule against a rendered form, get the form from
the renderer, not from your idea of it. Grep for the function that produces it and read what
it returns. A self test written from the rule tests the rule against itself; a self test
written from a real rendered string tests it against the product.

**The second half of this one is worth as much as the first.** The three violations it found
were on a calendar tile that reads "SEP 8" at display size, and the honest answer was neither
to widen the exemption nor to spell "September 8th" across a 2.5rem tile.

The tile became a `time` element carrying its own `datetime` attribute, and the checker
verifies that the visible text is a rendering of that attribute before letting it past the
date rules. The exemption is earned per element, by proof, and an element that fails to earn
it is reported AND left in the prose stream, so wrapping a sentence in `time` gets it linted
twice rather than not at all.

Note which direction the derivation runs. The permitted renderings are computed in the
CHECKER from the ISO value. Importing them from the builder would produce a checker that
agrees with the generator about a wrong answer, which is the same fault as an allow list
built from the output instead of the input.

**Generalises to.** Every "this region is data, not prose" argument. The way to settle it is
not a marker asserting the region is exempt. It is a machine readable value in the element
itself that the checker can hold the visible text against.

## 36. A test that cannot tell a working implementation from a broken one

`map_gestures.mjs` has said in its header since the day it was written that zoom anchors on
the fingers rather than the centre of the drawing. Fourteen assertions, none of them that one.

The reason is worth more than the omission. Every pinch in the file was performed at the
centre of the viewport, and **an anchored zoom and a centre anchored zoom produce the same
viewBox when the fingers are at the centre.** The two implementations are indistinguishable
under the only input the test supplied. Deleting the anchoring maths from the page would not
have turned it red.

Underneath that, every pinch used a hardcoded `(195, 400)` on a viewport where the drawing
starts at y=502. The gestures were being performed above the map. The handler ran anyway,
because the events were dispatched straight at the element, so the whole file was passing on
input no finger could produce.

`text_contrast.mjs` had the same shape at a different scale. It swept 151 pages in one 1100px
desktop context, where a `max-width` query cannot fire and the map's touch built controls do
not exist. The site's two newest controls, over a live map, had never been measured by the
gate whose entire promise is that every word on the site is legible.

**What to check instead.** For any assertion, ask what the broken implementation would
produce and whether your input distinguishes it. If a centred pinch, a desktop viewport or a
default value makes two different behaviours agree, the test is measuring the agreement.

The fix is to state the discrimination in the test itself. The anchoring assertion now
computes what a centre anchored zoom WOULD have left under the finger and fails if the
observed answer is not several times closer to the anchored one, so a pinch too near the
centre to be a test reports itself as such instead of passing.

**And a coverage rule that came out of the same pass.** When a suite runs in more than one
context, assert the count PER CONTEXT. A phone pass that silently built nothing lands as a
healthy total, because the desktop pass alone clears any threshold written against the sum.

## 19. A law with no mechanism, reported as a skip

`ownership.yaml` is the boundary between several unattended automations sharing one git
history, and `.githooks/pre-commit` is what enforces it locally. On 2026-08-16 the whole of a
run's work went in with **no ownership check on any commit**, because `core.hooksPath` was
unset in that checkout and `.git/hooks/pre-commit` did not exist. The hook file was committed,
executable and unreferenced. Git runs a hook it has been pointed at, and repository config does
not travel with a clone.

The stamping ritual ran the entire time. Phase 0 wrote `.git/ACTOR`, every phase that changed
lane rewrote it, and the run record described a hook enforcing something. The stamp was going
into a file nothing read.

**`guards_local.py` was the only thing that noticed, and it reported the gap as a SKIPPED
step**, then printed `51 step(s) passed` and exited 0. This repo's own instructions say to run
gates by exit code rather than by reading the last line. A run that obeyed them learned nothing.

**What to check instead.** A skip and an unavailable check are not the same event and must not
share a report line. A skip is what a check looks like when it is not needed. A check that
CANNOT RUN is the opposite, and belongs in the failure list with a non-zero exit. Ask of any
skip: does this mean "covered elsewhere" or does it mean "not covered at all"? Only the first
is a skip.

**And the second-order lesson, which is why this is entry 19 and not a footnote.** Entry 12 in
this file is a rule that was repealed and still read perfectly. This is the same fault one level
down: not a rule that was overridden, but a rule with nothing implementing it. Both were found
by a person reading rather than by anything red. When a check exists to enforce a written rule,
something has to assert THE CHECK IS CONNECTED, and that assertion has to be able to fail.

## 20. Two enforcers disagreeing about what a lane is scoped to

The pre-commit hook checked the staged change against `.git/ACTOR`, so it scoped a lane to a
COMMIT. CI pinned one actor from the branch prefix and checked the whole branch diff, so it
scoped a lane to a BRANCH. Both were correct implementations of a sentence nobody had made
precise, and each was green on inputs the other refused.

That was not academic. The daily routine's own Phase 17 instructs the run to stamp `upgrade` and
commit, on the only branch Phase 16 gives it. **Obeying the routine exactly produced a branch CI
was built to reject**, and the first run to ship a deck spent its ship phase discovering that and
moving two commits onto a separate pull request.

**What to check instead.** Where two mechanisms enforce one rule, write down which unit the rule
is scoped to and make both read the same signal. Here the stamp is copied into the commit as an
`Actor:` trailer by `.githooks/commit-msg`, so one stamp drives the hook and the runner.

**The trap inside the fix.** Trusting a per-commit declaration means a commit can name its own
lane, and the lanes are what carry the protection: `upgrade` owns the machine and not the record,
so a false `upgrade` stamp buys nothing. `human` is the exception, because it owns every path, so
a routine that could stamp `human` would switch the whole map off from inside a commit message.
`actors_allowed_on_branch` drops `human` in code rather than trusting the map to be written
carefully, and the self-test puts `human` in the test map on purpose to prove the drop happens.

## 21. An allowlist of names is a gate that sleeps

`copy_sync_check` decided what to check by matching KEY NAMES against a list: kicker, headline,
subhead, body and eleven more. Slides here are bespoke and the copywriter names keys to suit the
slide. The 2026-08-16 deck used `hook`, `hook2`, `tag`, `tag2`, `dek`, `bodies`, `how`, `rows`,
`attribution`, `site`, `source2` and `when1`. **Twelve of its nineteen key names were invisible
to the gate**, including every key carrying body prose. It reported clean having examined 35
strings and none of the deck's sentences.

That is how a slide sentence citing "SB 6" with nothing behind it reached the published record
with every gate green. The run found the missing REVERSE direction and proposed adding it, which
was right and would not have been enough: a reverse check over the same allowlist would have
missed the same twelve keys.

**What to check instead.** When a gate selects what to examine, the default must be EXAMINE, with
named exemptions. An allowlist fails silent, because a name nobody thought of is a thing nobody
checks and nothing reports the omission. A denylist fails loud, because the failure mode is a
gate complaining about something harmless, which somebody then fixes.

Ask of any selector: if tomorrow's artifact invents a name, does this gate check it or skip it?

**The related note on carve-outs.** The reverse direction was left out originally on the
argument that it would flag every axis label and that a gate crying wolf is worse than no gate.
The premise was true and the conclusion was wrong. The answer to a noisy check is carve-outs
narrow enough to state, not the absence of the check. Here the carve-outs are the design's own
`decorative` flag, named standing furniture, and a prose-shape test. And a provenance stamp is
STRIPPED from a node rather than exempting the node, because exempting anything containing a
stamp would blind the gate to whatever sits beside it.

## 22. A number can be right while the sentence around it is wrong

`numeral_lint` is a hard build gate and it enforces something precise: every numeral in published
copy traces to a value the build actually computed. It is structurally unable to see whether the
words around the numeral describe what was computed. Two defects shipped in that blind spot on
one page each.

The map's accessible title read "N of 254 counties carry an item" on every page, where the lit
set is whatever the caller passed. On the Killeen-Temple page that is the counties of that
metro's items, so the map announced **"1 of 254 counties carry an item"** to a screen reader, a
statewide claim contradicted by the page's own prose two lines above.

`llms.txt` built its "Open right now" list from `public_access.room` alone, under a heading
reading "Decisions a member of the public still has a dated way into". Room records what KIND of
access exists, never whether it is open. **28 of 47 entries were finished votes.**

Both numbers were correctly computed and correctly rendered. Neither sentence was true.

**What to check instead.** For every published figure, ask what noun phrase the reader will
attach to it and whether the code guarantees that phrase. A count needs its scope named in the
same sentence, and a list under a promise needs the promise computed rather than approximated by
a nearby field.

**And prefer the derivation the heading promises, not the one that is easy.** The obvious fix
for `llms.txt` was to drop `decided` items. That is a proxy, and it deletes the case the heading
most wants: League City has decided, and what it decided was to order a special election on
November 3rd, which is precisely a dated way in. Computing a FUTURE DOOR keeps it and drops the
finished votes, because a finished vote has no future door whatever its status says.

## 23. A fact the code branches on, carried only in prose

`llms.txt` decides whether a dated hearing is still a door a reader can walk through. TCEQ
called off two August 2026 hearings and the record kept the original dates with the
cancellation written into the `note`, which is correct history: the sitting was scheduled and
then was not.

The first fix read that note with a regex. It worked, it was pinned by a self-test, and it was
the wrong shape. **The site was branching on a sentence a person writes.** It would have gone
quiet the day somebody wrote "called off", or "postponed indefinitely", or moved the word into
the summary instead, and nothing would have reported the change: the page would simply have
started publishing a canceled hearing as a live door again.

This is the compute-not-generate law at the level of a boolean rather than a numeral. The law
says no published NUMBER is ever typed by a person. The same argument covers any fact the build
makes a decision on, because a decision derived from prose is a decision derived from whatever
phrasing happened to be used that day.

**What to check instead.** For every branch in a builder, ask where the fact it tests lives. If
the answer is a free-text field, the fact needs a field of its own, and the free text needs a
gate keeping it honest against that field.

Both halves matter and the second is the part that is easy to skip. `key_dates[].canceled` is
the truth now, and `gate_schema` fails any date whose note calls itself canceled while the flag
does not. Without that gate the field would silently drift out of date the first time somebody
wrote the note and forgot the flag, and a field nobody maintains is worse than the prose it
replaced, because the code trusts it more.

The asymmetry is deliberate. A note saying canceled REQUIRES the flag. A canceled date requires
no note at all. The gate exists to stop the prose contradicting the data, not to make writers
describe every field twice.

## 24. A test that lands inside the window the product suppresses

`responsive.mjs` asserts three things about the map on a phone, and says in its own comment that
any two without the third is a defect: the readout fills under a dragging thumb, releasing the
drag does NOT navigate, and a plain tap still opens the county.

The third assertion failed in CI on a build whose `docs/index.html` was byte identical to the
one that had passed fifteen minutes earlier. Locally it navigated on **one run in three**.

The cause was not geometry and not timing noise. A drag's `touchend` arms a capture-phase click
killer and removes it after **400ms**, which is precisely what makes assertion two true. The test
waited **350ms** and then tapped. It was tapping inside the window the product deliberately
suppresses clicks in, so it could only pass by accident: the killer is `once:true`, so it
survived unless the drag's own `touchend` had already produced a click that consumed it. Whether
that happened was the coin toss.

**The gate was not measuring what it claimed.** It said "a plain tap" and performed a tap that no
reader performs, 350ms after lifting from a drag, in the one window where the product's answer is
supposed to be "no".

**What to check instead.** When a product deliberately suppresses, debounces or delays a
behaviour, any test of the behaviour has to state where its input sits relative to that window.
Read the constant, do not guess a wait. A test whose input falls inside a suppression window is
testing the suppression, whatever its label says.

**And the fix has a direction.** The wait went to 700ms because the killer lives 400ms. If this
assertion starts failing again, raising the number is NOT the fix, because that would mean the
killer is outliving its own window, which is a defect in the map rather than in the clock in the
test. The comment says so at the call site, since the next person to meet a red test at 3am will
reach for the number first.

**The near miss worth recording.** This surfaced on a pull request that changed one JSON file and
could not have caused it. The tempting reading was "unrelated, therefore flaky, therefore re-run",
and a re-run would have been green about a third of the time. A latent coin toss in a gate is
indistinguishable from an intermittent product fault until somebody reproduces it, and the only
honest way to tell them apart is to reproduce it.

## 25. Every gate green, and the page was broken

The owner opened the site and said two slides had not rendered. They had not. The article page
carried two broken images, silently published six slides of an eight slide deck, and told the
front page it was a six slide deck. The whole suite was green.

Each link in the chain behaved correctly on its own.

1. `ship_images` encoded eight slides and refused two for coming in under its 40 dB quality
   floor, the stipple paper register at 39.0 and the hachured soil section at 40.0. That was the
   right call, correctly measured. It printed PROBLEM and exited 1.
2. **The run read the message and shipped anyway.** Exit 1 was treated as a note.
3. `site_build` counted `slide-*.webp`, got six, and generated image URLs BY INDEX from that
   count. So it emitted 01 through 06, of which 03 and 06 did not exist, and never emitted 07 or
   08 at all.
4. Nothing in the suite opened a built page and asked whether what it points at is there.

**The count came from one place and the URLs from another, and nothing checked they agreed.** A
count of surviving files is only a valid source of indices while the survivors happen to be a
contiguous 1..N, which is an assumption nobody wrote down and the first irregular deck broke.

**What to check instead.** Derive a collection's length and its members from the SAME source. The
manifest says what the deck is; a glob says what survived. Where the two can differ, the
difference is the finding, and it should be reported rather than resolved by picking whichever
number is smaller.

**And check the product, not the intent.** `site_fresh_check` proved `docs/` was byte-identical
to what the builders produce, which was true and useless: the builders and the comparison agreed
about publishing a broken image. `media_check.py` now opens every built page and resolves every
asset it references, including the ones served from this project's own repository, and it fails
if an article page is pictures and a title with no words under them. Replayed against the run as
it shipped, it names both broken slides.

**The half of this that is not about code.** The gate that failed hardest was the one that
noticed. `ship_images` said, in plain words and in its exit code, that two slides were not fit to
ship, and the run went past it. No amount of new checking helps if a red gate is read as advice,
so the routine now says at that step that its exit code is a stop.

The rule underneath: **a defect the owner finds by looking at the site is a defect the automation
was supposed to find first.** Publishing is not the last step. Opening what you published is.


## 26. A field's name is not a claim about today

The hub cards for the beats and the front page's index of them were built to carry one fact past
the count, whether a Texan can still act on anything on that beat. The first cut read
`public_access.room` and counted `open_comment` and `open_meeting` together, which put **"18
still open to the public"** on the data centers card while one of those meetings had closed five
days before the build.

Every gate passed. `house_style_check` read the sentence and found nothing wrong with its
grammar, its commas or its voice. `numeral_lint` traced the 18 to a computation, because 18
genuinely was the length of a filtered list. `schema_check` validated the node the number sat
beside. `site_fresh_check` proved the page was exactly what the builder produces. The build was
byte reproducible, house style clean, fully sourced and wrong.

`room` records what KIND of access a decision has. It does not record whether that access is
still available, and nothing in its name says so. The arithmetic against today is a separate
question that this repository had already answered once, in `window_state`, which the item pages
already trusted and which the front page's own counter was already printing.

**What to check instead.** Ask whether a published claim is a fact about the RECORD or a fact
about TODAY. A count of rows in a ledger is the first. Anything carrying "still", "open",
"current", "now" or "remaining" is the second, and it has to be computed against a date. No lint
can catch this, because both are the same integer to a scanner. The check is a reader asking what
the sentence promises.

**And it is why a second definition is worse than a missing one.** The broader count read better
and would have been defensible in isolation. What made it a defect is that this site already had
one definition of open, so shipping a second meant two surfaces disagreeing about the same
record on any day the two happened to diverge. The per topic figures now sum to exactly the
number the front page prints, and that agreement is checkable by hand in one line.

**Generalises to.** Any enum that describes a kind of thing being read as a statement about that
thing's current state. A status, a room, a category, a type. If the answer depends on the date,
the field alone can't give it.

---

## 27. Generated, validated, and shown to nobody

Three fields on the same page, found on one afternoon in August 2026, each written by something
and read by nothing a person could see.

`history` had existed on every item since the record did. The routine wrote to it only when
something changed, so every "checked and unchanged" observation was discarded at the instant it
was made, and no builder rendered the field at all. **57 of 61 items carried no movement log**,
and the four that did showed a reader nothing.

`schema.qa_pairs` produced up to twelve answered questions per item, every one assembled from
named fields and arithmetic, every one governed by its own self-tests for punctuation, voice and
subject-verb agreement. All of it shipped inside a `FAQPage` JSON-LD node. **A crawler could read
those answers. The person the page was built for could not.**

`key_dates[].note` rendered in the Dates table where a reader read it, and sat outside every copy
gate on both layers, because the gates were written against a list of fields somebody maintained
by hand and nobody had asked whether this one was on it.

Every gate was green throughout. There is no gate for this, and that is the point: a build gate
answers "is what we published correct", and none of the three was incorrect. Two of them were not
published at all, and the third was published outside the gates' field list.

**What to check instead.** For each field the record carries, ask three separate questions and
expect three separate answers. **Who writes it. What validates it. Where a reader sees it.** A
field with a gap in any column is not a feature yet. The `history` field had a writer and nothing
else, `qa_pairs` had a writer and a validator and no reader, and `key_dates[].note` had a writer
and a reader and no validator. Three different gaps, one shape.

**Generalises to.** Any field added in a hurry to carry state, then never wired to a surface. The
tell is that grepping the field name finds the write and a comment, and nothing else. That grep
takes ten seconds and is worth running over the schema once a quarter.

---

## 28. A self-test proved the gate could go red, on a sentence nobody writes

`gate_narration` refuses machine narration in reader copy. Its self-tests were real, it had been
watched going red, and one of its branches read `(?:could|couldn't|can't) be verified`.

The sentence a person actually writes is "**the date could not be verified**".

The negation sits between the modal and the verb, so the branch missed it. The neighbouring
`not verified` alternative missed it too, because the string is "not BE verified". The gate whose
entire subject is that phrase was blind to its most natural form, and had been for as long as it
had existed.

It was found by widening the gate to a new field and then deliberately trying to make the new
coverage fail. Three test phrasings were tried. Two went red, and the third passed when it
plainly should not have, which is the only reason anybody looked at the pattern.

**What to check instead.** "Every gate can go red" is necessary and it is not sufficient. A gate
that goes red on the phrasing its author had in mind proves the wiring works, not that the rule
is covered. When a gate targets a PHRASE rather than a structure, write out three or four ways a
person would really say it, including the negated form, and check that each one fails. Negation,
contraction and passive voice are where a phrase pattern leaks, in that order.

**Generalises to.** Any check built on a list of literal phrases rather than on a structural
property. Banned-word lists, narration detectors, hedge detectors, tone checks. The structural
gates in this repo do not have this failure mode, because a semicolon is a semicolon.

---

## 29. The exemption an allowlist would have been, and the pass that was luck

A key date note on `tx-2026-0041` reads "Date NewsChannel 6 reported the Planning and Zoning
Commission approval". The `6` is half a broadcaster's name. It is not a measurement, it traces to
no computation, and it never will, so the numeral gate could not read those notes at all and they
stayed outside it while every other field moved inside.

**The obvious fix is a list of station names, and a list is a hole with a list attached to it.**
The moment "Channel 12" goes on it, "Channel 12" is authorised on every page of this site forever,
whether or not any source ever mentioned it, and the gate has quietly stopped being about
evidence.

**What was done instead.** The candidate span is found structurally, a capitalised run followed by
a number, and then it has to MATCH A NAME THE ITEM'S OWN EVIDENCE ALREADY CARRIES: a source URL's
host, a source title, the deciding body, the item's title. `NewsChannel 6` is authorised on that
item because that item cites `newschannel6now.com`, whose host squashes to `newschannel6nowcom`
and carries `newschannel6`. `NewsChannel 9` is authorised nowhere, because nothing in the record
is called that. The exemption is **earned per item**, which is the same shape as
`schema.list_answer_ok`, where the comma exemption is checked against the counties the record
actually holds rather than granted to a region of the page.

**And then the second half, which is the part worth remembering.** With the record layer fixed,
the site layer's build passed. It had been passing all along. Not because the site layer had
solved this, but because `6` is a single digit and a single digit is nearly always in the
site-wide authorised set already, put there by some unrelated computation on some unrelated page.

**The gate was returning the right answer for a reason that had nothing to do with the question.**
It would have gone red the first day a broadcaster's number was less common, on a change that had
nothing to do with broadcasters. Both layers now derive the same answer from the same function.

**What to check instead.** When a gate passes on the case you were worried about, find out WHY it
passed before you move on. A pass is evidence about the gate only if you know which rule produced
it. This one was reached by asking the authorised set directly, item by item, instead of reading
the build's exit code, which is the same instruction as "run a gate by exit code, never by reading
the last line", one level in.

**Generalises to.** Any allowlist shared across a whole site where the values are small integers,
short strings, or common tokens. The wider the set, the more often it is right by coincidence, and
coincidence does not survive a refactor.

---

## 30. The build read git, so the build was not a function of its inputs

`docs/` gained a per page revision date, and the first version derived it from the history of
the generated bytes. The reasoning looked airtight: `docs/` is committed, so git already holds
an exact record of when each page changed, and using it adds no new state and has nothing to
drift. It passed 78 of 78 local steps.

CI failed on the next push, on `site_fresh_check`, with 218 pages CHANGED.

**Neither build was corrupt.** Both were correct given what they could see. The laptop had the
full history and a branch tip at HEAD. The runner had a synthetic merge commit at HEAD, the one
`actions/checkout` builds for a pull request and which exists in no branch, so the same ledgers
produced different bytes.

**The rule this is a case of.** `site_fresh_check` proves `docs/` is a pure deterministic
function of the ledgers, and that proof is what makes it structurally impossible for a run to
corrupt the live site: the worst case is a stale build a gate catches. Anything the build reads
that is not a ledger is an input to that function. Git history is such an input, and it varies
by clone depth, by checkout ref, by whether the runner fetched tags, and by nothing anybody
writes down.

**What was done instead.** Every date is now a field the record already holds. An item page
takes its own `last_verified`, an article takes the date it shipped, a hub takes the newest
verification in the record. Where no ledger field answers, the page publishes no date at all
rather than an invented one.

**How it is proved now, and this is the part worth copying.** A `--depth 1` clone is built into
a temp dir and diffed against `docs/` byte for byte. One commit of history, identical output.
That test would have failed against the git-based version in seconds, and no amount of reading
the code would have suggested writing it, because the defect is invisible in a repository that
has all its history.

**Generalises to.** Any build step reading the clock, the environment, the filesystem outside
the repository, the network, or git itself. The question is not "is this value correct" but
"would a different machine compute the same one".
