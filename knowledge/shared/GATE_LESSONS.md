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

## 10. A mode nothing ever opens is a mode nothing ever checks

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

## 11. A deploy that depends on who pushed

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

## 12. A gate that compares two renders must freeze the motion

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

## 13. A rule can be repealed and still read perfectly

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

## 14. A self-test is not wiring

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

## 15. Your container is not the environment being checked

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

## 16. Fixtures written by the author of the detector agree with it

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

## 17. A gate is only as strong as its narrowest scope

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

## 18. Deleting authorised strings by substring dissolves every figure

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

## 19. A reference is a dependency even when it is not a link

Item `tx-2026-0006` tells a reader "See item tx-2026-0010 for that page's statutory basis", and
there is no `tx-2026-0010`. Fact checking culled it and the pointer survived. Three checks nearly
caught it and could not: the link checker reads `href` attributes and this is prose, the claims
gate checks that claims have sources and this is not a claim, and the numeral gate's own
self-test **used that same id** as its example of a legitimate cross-reference exemption.

**What to check.** A checker that knows the id space, over every prose field. Prose that names
another record is asserting that record exists.

**And note the second half.** A test fixture demonstrating an exemption taught the suite that the
broken id was fine. See entry 15: fixtures written beside a detector agree with it.

## 20. A true count of the wrong set reads exactly like a true count

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

## 21. One value meaning two things

`page(active="")` marked the current nav entry. `""` is also Home's own href. So every item page
and every topic page shipped `aria-current="page"` on Home, telling a screen reader it was on the
front page while it read an item. Every page looked right, because the marker is a small
underline and Home is where a reader's eye is not.

**What to check.** A sentinel that collides with a real value is not a sentinel. Use `None`, and
test the sentinel before the comparison rather than letting it fall out of one.

## 22. A workflow's implicit default is a repo setting, and a setting is not a rule

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

## 23. A CSS rule can be correct, matched, and dead, and it reads as fixed

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

## 24. A test that encodes the workaround defends the bug

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

## 25. A clipped numeral is not a layout bug

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

## 26. A token pairing is not the colour a reader receives

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

## 27. A gate that mis-parses its own input invents failures, and they are convincing

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

## 28. Three small paddings are one big hole

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

## 29. A pass by half a unit is a coin flip, and the runner calls it

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

## 30. A gate that passes by collision is not passing

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

## 31. Reader copy is every field a page renders, not the two the gate was told about

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

## 32. Nine green suites and nobody had looked at the page

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

## 33. Running every self-test is not running the gates

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

## 34. A gate's own exemption is where the next unread surface grows

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

## 37. A law with no mechanism, reported as a skip

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

## 38. Two enforcers disagreeing about what a lane is scoped to

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

## 39. An allowlist of names is a gate that sleeps

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

## 40. A number can be right while the sentence around it is wrong

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

## 41. A fact the code branches on, carried only in prose

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

## 42. A test that lands inside the window the product suppresses

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

## 43. Every gate green, and the page was broken

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


## 44. A field's name is not a claim about today

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

## 45. Generated, validated, and shown to nobody

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

## 46. A self-test proved the gate could go red, on a sentence nobody writes

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

## 47. The exemption an allowlist would have been, and the pass that was luck

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

## 48. The build read git, so the build was not a function of its inputs

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

## 49. The gate enforced ten rules and could observe four

A content security policy was added to every page, hashing each inline script so an injected one
has a hash nobody authorised and does not run. The policy names ten directives. The checker
written beside it reads `<script src>`, `<img src>`, `<iframe src>` and `<form action>`, which
are resource ATTRIBUTES, and that is four.

`connect-src` is not among them, because a fetch target does not live in an attribute the way an
image does. It lives in a `data-endpoint` attribute and in a JavaScript string literal. So the
ask box's Worker origin was never added to the allowlist, the browser refused every submitted
question in production, and the checker reported the page clean because it had never looked at
the place the answer was.

**The part worth sitting with is how it was confirmed.** The change was verified by fetching ten
deployed pages from the live site and auditing each one. All ten passed. The site was broken at
the time, in a way those exact ten pages demonstrated, and the audit could not see it because
the audit and the defect had the same author and therefore the same blind spot. Fetching the
real site felt like the strong form of checking and was not, because the only thing being asked
was a question that had already been answered wrong.

**A gate you wrote is not evidence that the thing you wrote works.** It is evidence about the
part you thought of. Where those two are the same set, the gate reports on itself.

**What to check instead. Ask the enforcer, not a model of it.** A browser dispatches
`securitypolicyviolation` every time it refuses something, against the whole policy, including
the directives no parser here knows to look for. `tests/csp_runtime.mjs` loads each page in
Chromium and records those events. Replayed against the shipped fault it names both halves of
it, the refused inline scripts and the endpoint the policy omits, and it passes the eight other
sampled pages, so it is not failing indiscriminately.

**And when a gate approximates a spec, count the spec.** Ten directives, four observable, and
nothing anywhere said so. A checker covering four tenths of what it appears to cover is more
dangerous than no checker at all, because the missing six produce confidence rather than doubt.
State the coverage where the checker is defined, so the next person reads a boundary instead of
inferring a guarantee.

**One trap in the obvious repair.** Deriving the allowlist from what the pages reference would
close this and hollow the policy out, because an injected `fetch` would then allowlist itself at
build time and the gate would go green on a compromised page. The shape that works is the one
`numeral_lint` already uses here. Keep a DECLARED list, OBSERVE what the pages actually target,
and fail on a mismatch in either direction, an undeclared target and a declared origin nothing
uses.

**Generalises to.** Any checker that approximates an enforcer it does not run. A policy parser
against a browser, a linter against a compiler, a schema validator against the consumer, a
permissions model against the API that actually decides. The question is not "does my checker
pass" but "does my checker run the thing that says no".

## 50. A security fix moved one line, and the pre-push runner went red on every clean checkout

`guards_local.py` runs what CI runs, here, before pushing. It reads `guards.yml` rather than
keeping its own step list, and it skips the steps that need a CI context, recognised by a
`${{ }}` expression in the step's `run:` block.

On 2026-08-19 the Ownership step's branch name moved out of `run:` and into `env:`, because
`github.head_ref` on a fork pull request is whatever a stranger typed and interpolating it into
a shell is a command injection. That fix was correct and it is still there.

Its side effect was that the step no longer carried a `${{ }}` anywhere the runner looked. The
step stopped being classified CI-only, ran locally with `BRANCH_NAME` unset, and
`guards_local.py` exited 1 on a clean checkout of `main` from that push onward. The daily
routine's Phase 0 sends a run to fix a gate that is red at wake before anything else, and it
found one it did not own, on the first morning after.

**Nothing edited the broken file.** Its own suite stayed green, because every case in it wrote
the expression into `run:`, which is the half that still worked. This is the same shape as
entries 13 and 30 and the `craft_floor` bands bug, and it now has enough instances to name:
**a CONSUMER reading one of the several places a PRODUCER may write.** The producer here is the
GitHub Actions step schema, which offers two routes for a context expression. The consumer knew
one. Nobody changed the contract; somebody used the other half of it.

**What to check instead.** A checker that classifies a thing must assert its classification
against the REAL artifact, not only against a fixture it wrote. The new case does both. It
replays the `env:` shape synthetically, and then it goes and finds the actual Ownership step in
`guards.yml` and asserts THAT step lands on the skip side. The synthetic half proves the logic
can tell them apart. Only the second half would have gone red on 2026-08-19, and it is one line.

**And the cost of the failure mode is worse than it looks.** A gate that is red when the product
is broken is doing its job. A pre-push runner that is red on a clean checkout teaches whoever
runs it that its red means nothing, and the next real failure is read the same way. A tool
nobody believes has negative value, not zero.

**Generalises to.** Any dispatcher, router or classifier keyed on where a value is written
rather than on what it is. Environment versus argument, header versus query string, attribute
versus child element, annotation versus config file. Ask what the producer is ALLOWED to do,
not what it happened to do the day the consumer was written.

---

## 51. The ownership guard did not run at all inside a git worktree, and nothing said so

**2026-08-20.** `.githooks/pre-commit` is the ownership guard. It is what stops one of this
repo's several unattended automations writing into another's lane, and CLAUDE.md's own first
commands section calls it load bearing by name, because the cost of it not running was already
paid once: a whole run of commits landing with no ownership check on any of them.

It ran. It just could not find the stamp, and it is written to treat a missing stamp as a
maintainer session that owns everything.

```
[ -f "$root/.git/ACTOR" ] && actor="$(tr -d '[:space:]' < "$root/.git/ACTOR")"
```

In a plain clone `$root/.git` is a directory and that path is the stamp. In a linked **worktree**
`$root/.git` is a FILE holding a gitdir pointer, so `$root/.git/ACTOR` is a path underneath a
file, `[ -f ]` is false, `actor` stays `human`, and the guard cheerfully approves a write to any
path in the repo. `commit-msg` reads the stamp the same way and exits 0 before writing anything,
so those commits also reached CI with no `Actor:` trailer.

**Both halves of the check were switched off by the same line, in the environment a session is
most likely to be isolated in.** An agent given a worktree for isolation had less enforcement than
one working in the main tree, which is exactly backwards.

**Nothing was red.** `ownership_check.py --self-test` passes, because the checker is fine. The
hook is not covered by anything: it is shell, it is invoked by git, and its failure mode is to
exit 0. `guards_local.py` runs the CI suite and CI reads the trailer, so an unstamped commit falls
back to the branch's actor, which for a maintainer branch is "owns everything" and looks correct.

**What to check instead.** For any guard whose failure mode is "does nothing", the test is not
"does it pass on a clean tree". It is **make it go red on purpose in the environment you actually
work in**. That is one command: stamp a routine actor, stage a write outside that lane, and watch
the commit be refused. Two minutes, in the worktree, and it would have caught this the first day
anybody used one.

**Generalises to.** Every path a script builds by string-joining onto `.git`, and more broadly
every guard that resolves its own configuration by convention instead of by asking the tool.
`git rev-parse --git-dir` answers correctly in a clone, a worktree, a submodule and a bare repo
with a work tree attached. The convention answers correctly in one of the four.

The wider shape is entries 13, 30, 37 and 38 again, in its quietest form yet: **a checker that
CANNOT go red prints the same clean line as a checker that went green on a clean product.** The
run has no way to tell those two apart from the output, so it must occasionally force the red.

---

## 52. Every film on the site was refused, and it read as a video that would not autoplay

**2026-08-20.** The owner said the videos were not autoplaying. They were not playing at all, and
they never had. The browser says so in one line:

```
Refused to load media from 'https://raw.githubusercontent.com/.../dispatch-720.mp4' because it
violates the following Content Security Policy directive: "default-src 'self'". Note that
'media-src' was not explicitly set, so 'default-src' is used as a fallback.
```

`csp.py` writes `script-src`, `style-src`, `img-src`, `font-src`, `connect-src`, `frame-src` and
`form-action`. It never wrote `media-src`, so media fell back to `default-src 'self'` and the
films, which are served from `raw.githubusercontent.com`, were refused.

**The POSTER loaded.** It is an `<img>`, `img-src` names that host for the article pages' shipped
slides, and the same host was refused for the `<video>` one attribute away. So the page showed a
still, a play button and a spinner that never resolved. **The symptom was indistinguishable from
an autoplay policy**, which is the most common reason a video does not start on its own, so the
report that reached this repo was about autoplay and the cause was a directive nobody had written.

**Why the gate could not see it, which is the part worth keeping.** `csp.audit` reads HTML
attributes: `<script src>`, `<img src>`, `<iframe src>`, `<form action>`. Neither video surface
writes an address into markup. The feed builds `<video data-src=...>` and attaches the real `src`
in JavaScript, and the home page reads `media_base` out of `docs/videos/videos.json` and assigns
`el.src`. **The URL appears in no page's markup anywhere on the site.** A regex over the built
HTML finds nothing on a site whose every film is blocked.

This is entry 30's shape and it is written into `csp.py` already, about `connect-src`: "Every
pattern above reads an HTML attribute, and a fetch target is not an attribute." The file diagnosed
its own blind spot, fixed it for one directive, and left the same hole open for the next one.

**What to check instead.** Audit against the SOURCE OF TRUTH, not against the rendered markup.
`media_targets` reads `media_base` out of `videos.json` and `unaudited_media` checks that origin
against the policy the build just wrote. That matters twice over here, because `videos.json` is
owned by `TexasAIDispatch` and is the one file it writes into this repo: the origin can change
without a byte of this repo changing, and a policy audited only against this repo's own markup
would go green straight through that too.

The self-test replays both halves, and the fix was verified by forcing the red, by setting
`MEDIA_HOSTS = ()` and confirming the gate fails on the real shipped manifest.

**Generalises to.** Every CSP directive whose resource is addressed at runtime rather than in
markup, which is most of them on any page with JavaScript: `media-src`, `connect-src`,
`worker-src`, `img-src` for a lazy-loaded gallery. And more widely, any allowlist audited against
a RENDERING instead of against the data the rendering is generated from.

**One more thing this cost.** A resource type was widened for one element and not for its sibling,
on the same host, in the same feature. When adding a host to any allowlist, ask which OTHER
directive the same feature needs, because the feature is what has the requirement and the
directive is only how it is spelled.

## 53. Two instruments could stop and the whole board would stay green

**Date.** 2026-08-21. **Found by.** Asking what happens when a gate FIRES, having just finished
checking that every gate was wired.

Both instrument page checks reported one code for every finding they could make. Exit 2, "wants
attention". The reasoning was written at the top of both files and it is good reasoning: a check
that can abort the run it rides along with is a check somebody eventually removes for costing a
day's carousel over a stale chart. So `guards.yml` turned exit 2 into a `::warning::` and passed.

**A `::warning::` does not fail a job and does not fail a build.** Nothing about a green check
run distinguishes one from a clean pass unless somebody opens the log.

Now put that beside the collector's own workflow, which is also correct on its own terms. The
water collection step is `continue-on-error: true`, because TWDB being down must never cost an
ERCOT day, and a failure there prints `::warning::the reservoir reading did not land`.

**So a dead water collector produced a warning from the cron and a warning from the page check,
and both jobs went green.** The record could stop growing entirely and the only evidence would be
a page quietly showing an older number every day, on a site with nobody in it. This repo's own
documentation calls a missed day the one irreversible failure it has.

**The shape of the mistake.** Two severities sharing one exit code. "The page reads wrong" and
"the instrument has stopped" are not the same event, and the argument for never failing a build
is an argument about the first one that had been silently extended over the second. Everything in
the design was right except that it could not tell them apart.

**What to check instead.** Give the second severity its own code and fail on it. Exit 2 stays
advisory and CI still turns it into a warning. Exit 3 means an instrument has stopped and CI
fails, which matters because `guards.yml` runs on every push to `main` and the collector pushes
straight to `main` twice a day. The alarm now rides the same path as the reading.

**Which findings are halting is a judgement, and it is the part to get right.** A gap in the
series and a day already recorded unverified are PERMANENT, because neither ERCOT nor TWDB keeps
an archive to backfill from. Failing on those would make the build red forever with no action
that could clear it, which is entry 38's lesson from the other direction: a permanently red gate
is a gate somebody turns off, and it takes the real findings with it. Halting is reserved for
what a fix can clear.

**Two defects fell out of writing the self-test, and both were older than the split.**

*The staleness rule was measuring the wrong thing.* It compared today against the newest record
of ANY kind. Both pages publish only VERIFIED days, on purpose: an unverified record is the
collector saying it fetched and could not trust what came back. So the rule was asking whether
the collector was RUNNING and calling that the instrument working. A collector that runs every
day and writes unverified every day passed it forever while the page froze on the last day that
verified. That is the exact failure `queue_findings` had been written for one series over, three
weeks earlier, and neither daily series was checking it. **A rule written for one series is worth
reading against its siblings the same day.**

*The water page's staleness check was passing by collision.* It asked whether the newest reading's
date appeared anywhere in the file, and the head carries a `temporalCoverage` ending on exactly
that date, computed by the builder from the same ledger. The check was answering a question about
its own input rather than about the page, and it would agree with itself forever. The grid check
had already learned this with the registry roster's effective dates and written it down. **Same
defect, one file over, and the write-up did not travel.**

**Generalises to.** Any check whose findings vary in kind but share an exit code, and any advisory
channel that two independent systems both report into. Ask what the board looks like on the worst
day the checks can describe. If that day is green, the severity is missing rather than the check.

**And the enforcement is not prose.** `guards_shape.py` now EXTRACTS the shell out of each page
check step, substitutes a stub for the checker that exits with a chosen code, runs it under
`bash -e`, and asserts what the step does. Grepping that block for `exit 3` would be a gate on
spelling. The question is what the step DOES when the checker says 3, so the step is asked.

## 54. The law was written the same evening the rule was broken, in the file that breaks it

**Date.** 2026-08-21. **Found by.** Reading `prompts/daily_routine.md` for something else.

On 2026-08-20 the owner was interrupted twice by a sandboxed command trying to write outside the
working tree. The session went looking at the permission mode first, because that is where the
word permission is, and the answer was somewhere else entirely: the Bash sandbox and the
permission mode are two different mechanisms, and a sandboxed write outside the tree stops and
ASKS, which is a prompt no permission mode answers and no unattended run has anybody to answer.

The law went into `CLAUDE.md` that evening. Every temporary file goes in `out/<run>/tmp/`. Never
`/tmp`, never a system scratchpad. It is a good rule and the write-up is thorough.

**Two lines of the routine went on saying `--out /tmp/site` anyway.** Phase 2 and Phase 7, both
executed by the unattended run every morning, both writing exactly where the law says never.

**The shape of the mistake.** A rule stated in one file and broken in another, with nothing in
between checking they agree. That is the third time this repo has found the same shape written
down: the missing hashtags, the missing progress counter, and the site URL that lived in five
places at once. `coherence_check.py` exists because of the third one. This is the fourth.

**What to check instead.** Read the rule out of the prose it governs. `routine_claims.py` now
scans the routine's fenced shell blocks and refuses any command that writes to `/tmp`,
`/var/tmp`, `/var/folders` or `~/.cache`. It runs in `guards.yml` already, so the rule went from
being remembered to being enforced without adding a step.

**The case that decides whether it is a rule or a substring search.** `out/<date>/tmp/site` is
the correct answer and it contains the letters of the thing being forbidden. The pattern is
anchored at the start of a path, and the self-test asserts that the FIX is not flagged as the
defect. It also asserts that prose explaining the rule is not read as an instruction, because a
gate that makes its own reasoning unwritable loses the reasoning at the first rewrite.

**Generalises to.** Every law in `CLAUDE.md` that governs a file which is not `CLAUDE.md`. Ask,
on the day the rule is written, what would catch the file that breaks it, and write that instead
of a second paragraph.

---

## 55. Three checks passed on work that never happened, because a click cost more than its timeout

The record calendar's browser suite failed about one run in four. It failed in CI on
`walking all the way back lands on the first month`, reporting `2025-04`, and then passed
four times running, which is the signature that gets a suite labelled flaky and then ignored.

**The cause is not in the calendar.** The page is correct. Every page on this site carries
infinite decorative animations, one of which shimmers a full width blurred layer that cannot be
composited, so a headless renderer with no GPU repaints and re-blurs it every frame. Playwright's
actionability loop is measured in frames. Measured on `docs/record/`, one `page.click` costs
**426 to 875ms** with motion on and **49 to 215ms** under `reducedMotion: "reduce"`. Every walk
loop in the suite gave a click `{ timeout: 400 }` and then swallowed the failure with
`.catch(() => {})`.

So the loops were dropping steps and asserting wherever they had run out of iterations.

**The part worth keeping is what the swallow did to the OTHER checks.** The end of range
assertion at least failed. Three more passed:

- the backward walk timed out on **15 of 22** iterations while `#calprev` was still enabled
- `the third rapid tap` delivered **0 of 5** taps, and both of its assertions passed on a
  calendar nobody had touched
- eight filter flips were swallowed, and the assertion was true of a filter nobody toggled

A swallowed interaction does not make a check fail. It makes the check TRUE, about an initial
state, forever. That is worse than the flake, because the flake at least announced itself.

The forward walk had a fourth version of it in a different disguise. It compared
`seen.filter((v, i) => v !== seen[i - 1])`, dropping consecutive repeats, and a dropped click
produces exactly a consecutive repeat. The filter deleted the evidence of the fault it would
otherwise have caught.

**What to check instead.**

- **Never swallow an interaction.** `.catch(() => {})` on a click is a lie told to the assertion
  that follows it. If a click can fail without the test failing, the test is not about the click.
- **Assert on the STATE CHANGE, not on the call returning.** `walk()` clicks and then waits for
  the shown month to differ from the one it recorded, and stops on the control's own `disabled`
  state rather than on an iteration count. A cap is a runaway guard, and reaching it is a failure.
- **Count what the handlers actually received.** The rapid tap now fires its clicks in the page
  and asserts the listeners saw five. The filter flips are counted the same way. A test that
  cannot say how many events it delivered cannot say what it proved.
- **Never normalise away a duplicate you have not explained.** A repeat is either the behaviour or
  the bug, and a filter that removes it decides which without looking.

**A concurrency trap in the same block.** Five `page.click` calls in a `Promise.all` share one
mouse and interleave, so a mousedown on prev with a mouseup on next fires the click on the pair's
common ancestor and neither button hears it. That delivered two to five taps per run, with nothing
rejected. Firing them synchronously in the page is both deterministic and a harsher race than a
thumb can make, because the handlers run back to back with no frame between them.

**And `goto` to a url that differs only in its fragment is a SAME DOCUMENT navigation.** Nothing
reloads, `hashchange` fires, and the startup path that parses the hash never runs. The block
headed "A DEEP LINK NEEDS A FRESH DOCUMENT" had been testing the listener and reporting it as the
cold parse. A visit counter in the query makes each load a real load.

**Turning motion off is right, and it leaves a hole that has to be named.** `reducedMotion` is
what a CI runner should emulate, the site honours it in its own stylesheet, and nothing the suite
asserts is about motion. Except one thing. `html` carries `scroll-behavior:smooth`, which reduced
motion turns to `auto`, so the deep link check is the ONE assertion whose subject is where the
viewport ends up, and it is the one the setting changes. Arriving at `#cal-2026-06`, the panel
sits at 1517, 1517, 1164 and 0 at 0ms, 200ms, 500ms and 1000ms under default motion, and at 0 on
the first frame under `reduce`. The page is right either way. So that assertion is asked a second
time in the mode the suite no longer covers, waiting for the scroll to STOP MOVING rather than
sleeping a guessed interval, which would be the same guess that flaked to begin with.

**Generalises to.** Every browser suite in this repo, and to any timeout written as a constant
next to an interaction. A per action timeout is a claim about how long the product takes, made by
somebody who was not measuring. If a suite needs one, measure the action first and then say in
the comment what it measured, or the number is a guess that will come back as a one in four
failure on a machine nobody was thinking about.

**Result.** Two minutes fifty seven with two failures, to thirty five seconds clean, eight
consecutive green runs, and the checks now fail when the interaction does not land.

## 56. A marker check is only as good as the marker, and a wrong marker reads as a broken deploy

Three times in one session, a check grepped for an identifier that was never in the product, and
the zero it got back was read as the feature being missing.

The live site had just taken the ask box work. The verification grepped the served page for
`caltoday`, `calstep` and `actonly`, got three zeros, and reported that the calendar's today
marker, its phone stepper and its act filter had not shipped. All three had shipped. They are
called `calnow`, `calprev` with `calnext`, and `calswitch`. The names were invented by the person
writing the check, from what the features do, and never once compared against the code that emits
them.

The same shape twice more the same week, and one of them shipped. A phone layout check asserted
that `.sitefoot` was hidden. The footer is `footer.site`. The selector matched nothing, so the
assertion was true on a page with the footer standing wide open, which is exactly the bug a reader
then reported. And a live bug check looked for a starter chip at `#ask .askstarters button`. The
chips are `button[data-ask]`, so the check failed on a working product and cost a round of
diagnosis pointed at the wrong thing.

**Why it survives review.** A zero is not evidence of absence, it is evidence that the query found
nothing, and those two are the same character on the screen. Every other assertion in a suite gets
its truth from the product. A string match gets its truth from a string the author typed, and
nothing in a green run distinguishes a marker that matched from a marker that could never match.

**The gate now.** Before a check asserts on an identifier, the identifier is proved to exist in the
source that emits it, and the check is proved to match when the feature is present. In practice
that is one grep of the builder before the grep of the output, and it is what
`scripts/shared/lesson_refs.py` does for the one class of marker this repo cites most, the
`GATE_LESSONS` entry numbers. Twelve of those numbers had been used twice, one citation already
resolved to the wrong lesson, and repairing that turned three correct citations into wrong ones
without touching a character of them.

**Generalises to.** Every assertion whose subject is named rather than found: CSS selectors, DOM
ids, grep patterns, JSON keys, environment variable names. Ask what the check does when the name
is wrong, and if the answer is "passes", the check is a decoration.

---

## 57. A measurement that includes the instrument's own work

The calendar's month switch was timed with `playwright.click`, which scrolls the target into view
before it clicks. It reported 540ms. The switch takes 37ms. The other five hundred were the test
harness moving the page so it could reach a button.

An afternoon nearly went into optimising a page that was already fast, on a number that was
measuring the tape measure.

What the bad number did point at was real, and would have been missed if the number had simply
been thrown out. `focus()` on the new month heading also scrolls, by whatever distance the browser
chooses, and that was a genuine 263ms of long smooth scroll to a month already on screen. It is
`focus({preventScroll:true})` with an explicit `scrollIntoView({block:'nearest'})` now, which
moves only when it has to.

**The gate now.** Latency is measured inside the page, from the dispatch of the event to the next
paint, never around a driver call. Measured that way the switch is 38 to 55ms median and 81 to
83ms worst on a phone at six times slower CPU.

**Generalises to.** Any timing taken from outside the thing being timed. The driver, the network
stub, the screenshot, the await that resolves on a poll interval, all of them add their own work
to the number and none of them announce it.

---

## 58. The speed fix that broke the suite, and the entry that nearly shipped praising it

The calendar suite took thirteen and a half minutes. Almost none of it was work. Playwright's
actionability check includes "enabled", so every deliberate click past the end of the month range
waited the full thirty second default before giving up. Those clicks were given
`{ timeout: 400 }`, the suite fell to thirty eight seconds, and the run log said the same checks
passed. It was written up as a win, in a worklog, in the words "13m29s to 38s, same checks".

It was not the same checks. Entry 55 above is what that 400ms actually did. A click on this site
costs 426 to 875ms with motion on, so the timeout was under the cost of the operation, and the
loops silently dropped steps and asserted wherever they had run out. Three checks then passed on
work that never happened.

**The two halves that look identical and are opposites.** A wait for something that is supposed
to NOT happen must be short, because it is paid on every run forever. A wait for something that
is supposed to succeed must be generous, because shortening it does not make the work faster, it
makes the work optional. The same diff, the same units, and the second one converts a slow suite
into a fast lie.

**What nearly shipped.** This entry was first written as "a suite slow enough to be skipped is a
suite that is not run", holding up the 400ms as the fix, on the strength of the worklog that
recorded it. Merging with `main` is the only reason it was read against entry 55 before landing.
Two entries in this file would have given opposite advice about one line of code.

**Generalises to.** Every performance win in a test suite. Ask what the suite stopped doing. If
the answer is "waiting", ask what it was waiting FOR, because a test that no longer waits for the
thing it asserts about is not faster, it is no longer a test.

**And to the worklogs themselves.** A worklog is written by the session that made the change, at
the moment it felt like a win, and it is the least adversarial account of that change that will
ever exist. Its lessons are worth rescuing before the file is deleted, and they are worth
re-reading against what has landed since. This one was four days old and already wrong.

---

## 59. CSS fails silently, and a green suite has never once looked at a colour

`stroke: var(--signal-link)` where the token is actually `--sig-link` is not an error. It is a
declaration the browser discards, and the element renders with its initial value. A stroke goes
to none. A fill goes to black. Nothing is logged, no build step complains, and the page looks
like a page somebody designed that way.

It shipped here three times. Twice quietly, as `--ink-dim` and `--ink-quiet` on the file list and
the cover cards, where the text simply inherited and nobody could tell. The third time it drew
every filament of a network diagram with no stroke at all, on a page whose entire subject is the
filaments, and the whole suite was green over it.

**Why every existing gate was blind.** `numeral_lint` reads numerals. `house_style_check` reads
prose. `site_fresh_check` proves the bytes match the ledgers, which they did: the build faithfully
reproduced the wrong token every time. Nothing in the suite read a stylesheet as a stylesheet.

**The gate.** `scripts/site/css_tokens.py`. Every `var(--x)` in the built stylesheets resolves to
a definition in the built stylesheets, in the built markup, or to its own fallback. It found all
three defects on its first run against a site that had passed everything else.

**The two things it had to get right, and the second is the harder one.** A fallback passes,
because `var(--x, #fff)` renders something the author chose either way. And a token set inline on
an element counts as defined, because the queue chart writes `style="--h:41.20%"` on each bar and
the sheet reads it back. A gate that reported that as missing would be reporting a correct
product as a violation, and that is how a gate gets switched off.

**Generalises to.** Every language that ignores what it cannot parse instead of refusing it. A
mistyped CSS property. An `aria-labelledby` pointing at no id. A `<use href="#x">` with no `#x`.
An SVG `filter:url(#y)` where `y` was renamed. All of them render, none of them complain, and
none of them are wrong in a way a diff will show you.

**The same afternoon, the same file, a second one, and the first diagnosis was wrong.** A right
arrow on the same page rendered as a box with "92" beside it. That was written up here as a font
subset problem and it was not: the served mono face carries U+2192 perfectly well. The stylesheet
is BUILT FROM A PYTHON STRING, and `content:"\2192"` inside one is not a CSS escape. It is
Python's OCTAL escape, which takes `\21`, produces chr(17), and leaves `92` as text. The page
shipped a control character in its copy.

Two escape languages had a turn at one literal and nothing in between checked what came out. The
lesson that nearly shipped would have sent the next session to re-subset the fonts. Reading the
cmap of the actual served file, which took one command, is what stopped it.

**And the gate that came out of it, `tests/glyphs.mjs`, was nearly the wrong gate too.** Written
for the font question, its first version collected only characters ABOVE the ASCII range, which
is precisely the window a control character slips through. It now refuses any control character
in published copy, which needs no font at all, and checks coverage only for the faces this
project actually ships. Judging a system family would have failed the videos page for drawing a
triangle in Arial, which every reader has and a headless container does not.

**And its self check went red on CI while passing locally, which is the whole reason it has one.**
The measurement compared a character drawn in the asked-for family against the same character
drawn in a family that does not exist, on the theory that both fall back to the same face. They do
not always. A missing glyph can draw as the LAST RESORT BOX, and the box carries the asked-for
family's own metrics, so it does not match the plain fallback and the comparison reads a missing
glyph as CARRIED. Locally the runner had a CJK font and drew the control character properly, so
the flaw was invisible; the container had none and drew the box. One measurement, two
environments, opposite answers, and the reassuring one was the wrong one.

The fix is a second comparison against a codepoint no font carries, drawn in the same family, so
the family's own box is recognised as a box. **A gate whose instrument is only checked on the
machine that wrote it has been checked in the easy case.**

---

## 60. Thirty five of forty nodes were stacked against the wall and every gate said yes

The company graph's first layout was textbook Fruchterman Reingold, clamped to the field. Its
self-test passed eleven of eleven. It proved the layout was deterministic, that every node landed
inside the neatline, and that no edge named a node that was not drawn. All three were true. The
picture was a rectangle of dots around an empty middle.

Classic force layout assumes a connected graph. This one is forty nodes and forty four edges,
nine of them connected to nothing at all, so repulsion was the only force acting on a third of
the field and there was no gravity to answer it. Everything accelerated outward until the clamp
caught it, and the clamp is what made the result look deliberate: every node was inside the
frame, which is exactly what the gate asked.

**What the gate could not ask.** Whether the drawing was worth looking at. "Inside the field" and
"laid out" are not the same predicate, and only the first one is checkable.

**What found it.** Rendering the page in a browser and looking at the screenshot. Nothing else
was ever going to.

**The same session, the same page, a second one.** With the layout fixed, the cursor well pushed
hardest exactly where the pointer was, so the node a reader reached for stepped aside as they
arrived. Every point on that field is a link to a company and not one of them could be hovered or
clicked. No gate has an opinion about that either. It took driving the page with a real pointer
and asserting on the lit state afterwards, and the first two attempts to do that reported a false
negative of their own, because an `<a>` in SVG has a bounding box that includes its label and the
centre of that box is empty space.

**Generalises to.** Anything whose output is a picture or a gesture. Layout, spacing, contrast,
motion, hit targets, focus order. Write the gates for what is checkable, and then RENDER IT AND
LOOK AT IT, and DRIVE IT AND CHECK WHAT LIT UP. Those are two separate steps and neither implies
the other.

---

## 61. The build that would have deleted thirty billion dollars because its scratch was gone

`tdlr_fetch.py --build` parsed every raw filing in `out/tabs/` and wrote the result to
`ledger/facilities/projects.json`. That is correct exactly once, on the machine that did the
fetching, and wrong every time after.

`out/` is gitignored scratch. The ledger is the committed artifact. When the container was
re-provisioned mid-session the 626 raw pages were gone and the ledger was still complete, so the
next `--build` would have written the 25 pages that happened to be on disk over the top of it.
201 data center filings and $36.97 billion would have become whatever those 25 held.

**Nothing would have gone red.** The ledger would still parse. `tdlr_projects` would still pass
its gate, because every remaining record is well formed. `site_fresh_check` would prove `docs/`
matches the ledgers byte for byte, which it would, because a smaller ledger produces a smaller
site perfectly faithfully. The published page would have shown a smaller number with total
confidence.

**What caught it** was noticing that `ls out/tabs/*.html` returned 25 where it had returned 626,
before running the build rather than after.

**The fix is a merge, not a replace.** `merge()` is keyed on the project number, the newest parse
wins, and the ledger survives having no scratch beside it. Five self-tests, including that a
re-parse replaces rather than doubles and that a record with no number never enters.

**Generalises to.** Any step that rebuilds a committed artifact from an ephemeral input. A cache
warm that writes through. A "regenerate the index from the files on disk". A migration that reads
a directory. Ask what the step does when its input is EMPTY, and if the answer is "writes an empty
artifact", it is a delete with extra steps.

**And to this project specifically.** `site_fresh_check` proves the site is a function of the
ledgers. It has never had anything to say about whether the ledgers are complete, and this is the
second time that gap has mattered.

## 62. A table wrapped to three lines beside an empty gutter and 110 checks said yes

The facility filings panel shipped its first build with `grid-template-columns:6.5rem 9rem 8rem
1fr 6rem`, inherited from the construction register's tables because it reuses their class. Those
tables put a county or a company name in the first column. This one puts a four digit year there.

So 6.5rem went to `2019` and the project name got what was left, which was 150px, and
`DFW III-II Building 3 Tenant Fit Out` wrapped to three lines with a hand's width of empty gutter
sitting beside it on every row.

**Nothing went red, and nothing could have.** The markup is valid. Every numeral traces to a
computation. The house style gate reads text and has no opinion about where text lands.
`site_fresh_check` proves the page is exactly what the ledgers produce, which it was. `css_tokens`
proves every `var()` resolves, and every one did. The suite has 110 checks and not one of them
knows what a column is.

**What caught it** was opening the page in a browser and looking at it, then measuring rather than
squinting: the widest string in each of the five columns is 1.75, 5.25, 6.56, 15.75 and 3.06rem,
totalling 32.4rem inside a 42.5rem row. Every one of them fit on a single line the whole time. The
space was not short. It was allocated to the column that needed none of it.

**The fix is a modifier class, not a wider table.** `.cbfile .cbrow` carries its own template,
measured from the content, with headroom for a figure an order of magnitude larger and a longer
city. The register's tables keep theirs.

**Generalises to.** Any class reused across surfaces whose content differs. A shared table, a
shared card, a shared badge. The class says the two things look alike and says nothing about
whether they hold alike, and the second surface inherits a layout tuned for the first.

**Then writing the gate for it taught the harder half.** The first cut asserted the obvious
thing, that a cell wraps only when the row has no room. It passed. Run under the other chromium
on the same machine, on the same build, it failed and named the defect. The two binaries measure
the same string about four percent apart, and the fault sat at the boundary: a hundred pixels of
text in a hundred and four pixel track. **A gate asserting a hairline fit reports which binary it
launched.** It asserts headroom now, five percent over the widest content in each column, which
is a property of the design rather than of the measuring instrument, and both browsers agree in
both directions.

Two smaller things fell out of chasing that. It measures over HTTP rather than `file://`, because
the web font resolved differently off disk and every column came out narrow. And it asserts the
font it is measuring in is the font that loaded, because a fallback mono is narrower and a gate
measuring a font nobody is served will happily pass a table that wraps for a reader.

**And the standing lesson underneath it, now three entries deep.** Number 59 was a colour, 60 was
thirty five nodes stacked on a wall, and this is a column. A gate reads the document. It has never
once seen the page. Render it, open it, and measure the thing you are about to call finished.

## 63. Three self-tests passed on a fixture the code never saw

The join in `facility_filings` was rewritten to union registry rows by name, and it came with three
self-tests built on a small fake registry and two fake filings. Two of them failed on the first
run, which is how the third was noticed, and the third is the one worth writing down.

**It asserted an EMPTY result.** A party named on three different facilities is a parent company
and joins to nothing, so the test asserted `facility_filings(...) == {}` and got `{}` and passed.

It would have passed if the function returned nothing for any reason at all. And that is exactly
what was happening: `facility_filings` drops every filing whose owner `brand()` does not recognise
before it joins anything, and the fixture owners were invented for the occasion. `ALPHA SPE LLC`
is not a tracked brand. Nothing in that fixture ever reached the code under test.

The two neighbours failed loudly because they asserted a specific non-empty answer. The one
asserting absence had nothing to distinguish "the rule worked" from "the input was thrown away
three steps earlier".

**Two things fix it, and both are cheap.**

- **Assert the fixture arrives.** One line before the others, checking the function returns the
  rows the fixture is about. It fails first and names the real problem, instead of leaving three
  confusing failures for someone to work backwards from.
- **Pair every assertion of absence with one of presence, on the same input.** The parent company
  rule is now checked as two: the same party joins fine when it names two facilities and joins to
  nothing when it names three. An empty result can no longer pass by accident, because the test
  beside it proves the pipeline was live.

**Generalises to.** Every negative test in this repo. A gate self-test that plants a defect and
asserts the checker goes red is safe, because red is specific. A test asserting nothing was
returned, nothing was written, nothing was flagged, or no error was raised is passing on a
condition that a dozen unrelated breakages also satisfy. Ask what else would make it green.

**And it is the same shape as entry 62 one level up.** That one was a gate measuring a font
nobody is served. This is a test measuring an input the code never received. In both, the check
ran, printed green, and was about something other than the product.
