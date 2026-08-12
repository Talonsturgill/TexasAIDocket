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

---

## Two process faults, which caused more lost time than any bug above

**Reading the last line of a report.** `house_style_check` prints an advice footer on failure and a
single clean line on success, so `tail -1` looks reassuring either way. A gate was red locally and
got pushed anyway. **Check exit codes, never last lines.**

**Reading a rendering artefact as a bug.** A screenshot taken during a smooth scroll captures
sticky elements at a stale offset, and a `fullPage` capture does not scroll, so intersection
revealed sections photograph as a blank middle no reader ever sees. Both were investigated as
layout bugs before being recognised. Scroll with `behavior:'instant'` and settle before capturing.

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
