# Field notes — lessons that cost something to learn

The living record of what has actually gone wrong here, and what the fix turned out to be. It
grows by one entry when a run learns something, and it never grows by speculation.

**A lesson with no evidence behind it is a preference.** Every entry names what happened, how it
was found, and what changed. Entries that cannot do that do not belong.

**This file starts nearly empty on purpose.** The sibling product's field notes run to three
thousand lines of hard-won knowledge about a different state, its sources, its audience and its
own past runs. Copying that here would import a history this product has not lived and cannot
verify, and the dedupe and divergence gates would then be reasoning against somebody else's
past. What ports is the machinery and the craft. What does not port is the memory.

---

## 2026-08-12 — A generator function multiplied by a number is NaN, and NaN draws nothing

**Found:** building the engine-proof deck. Slide three rendered as an empty frame. The render
report said zero errors and zero warnings.

**Cause:** `TX.rng(seed)` RETURNS a seeded generator function. The slide called `TX.rng()` bare
and multiplied the result by a number, which yields `NaN`. Every coordinate was `NaN`. Canvas
drawing calls with `NaN` coordinates do nothing at all and throw nothing at all.

**Why nothing caught it:** the renderer only reports what the page reports. A blank canvas is a
successful render.

**Fix:** the near-uniform canvas gate in `qa.py` is what catches this class, and it is now
written into `SKILL.md` in the largest letters the file has. Never ship a slide whose canvas
gate you have not read.

**The general lesson:** the dangerous bugs in a render pipeline are the ones that produce a
valid image. Look for gates that check for the ABSENCE of work, not just the correctness of it.

## 2026-08-12 — Fixing the art broke the type, and only the worst-point check saw it

**Found:** machine QA, immediately after strengthening the title card's dusk atmosphere.

**Cause:** the accent line of the headline and the atmosphere behind it were drawn from the same
ember family, and the strengthened band moved under the type. Contrast fell to 1.8:1 at the
worst point while the box mean still read 5.6.

**Why the mean would have passed it:** a mean over a graded ground is close to meaningless. The
eye goes straight to the worst point.

**Fix:** separate figure and ground in SPACE first (move the band above the type), then in
value. A reserve is the tool for the second part. Changing the accent to a lighter tint of the
same family was the smaller half of the fix.

## 2026-08-12 — A gate that answers a legibility failure can create a composition one

**Found:** machine QA, one round after the fix above.

**Cause:** a full-width opaque caption plate solved "art crossing glyphs" and created a dead
lower third, which the composition gate then failed.

**Fix:** narrow the plate so the art runs past its edge to the frame bottom. The gate's own
advice was right: move the mass, do not enlarge the quiet.

**The general lesson:** gates interact. A fix that satisfies one by making the frame emptier is
usually trading one failure for another.

## 2026-08-12 — The house-rule lint found four violations in copy written the same day

**Found:** running `house_style_check.py` against the built site for the first time.

**Cause:** two "cannot", a "we", and an "ours", in prose written hours after the rules were
restated. Every one of them read perfectly well.

**The general lesson:** the rules that need a lint are exactly the ones that are invisible in
the sentence that breaks them. If a rule is obvious when violated, a human catches it. If it is
not, only a machine will.

**Corollary, learned in the same hour:** a lint run against real data finds bugs in the lint.
This one suggested writing "July 31th", and read "Commissioners Hearing Room 7-100" as a numeric
range. Neither shows up against test strings somebody wrote to pass.

## 2026-08-12 — The display face turned a 3 into a 5 at feed size

**Found:** by looking at the contact sheet of the engine-proof deck. Slide 4's headline reads
**"Software 5D, no GPU"** on the contact sheet and at the 432px thumb. At full 2160x2700 it is
plainly 3D.

**Cause:** Fraunces' 3 has a flat top rather than a round upper bowl. At display weight and
feed size that flat top plus the closed lower bowl reads as a 5. Nothing was clipped, nothing
was low contrast, and every machine check passed. `render_report.json` even transcribed the
string correctly, because the DOM says 3D. **The defect exists only in the glyph a reader
receives.**

**The general lesson, which is the one this repo keeps relearning:** a checker sees what it
reads and a reader sees what was drawn. Machine QA reads the text node. Only an eye on the
thumbnail catches a glyph that renders as a different character.

**What to do about it.** This is a pixel-critic finding, not an engine bug, and the critic is
already told to read the 432px thumb and to transcribe every visible word. Transcribing from
the THUMB rather than from the full size is what would surface it, since transcribing the
full-size image gives the right answer and hides the problem.

**Where it bites hardest.** Any numeral in the display face at feed size, which is most of what
a slide is for. `3` and `5` are the pair to watch. A figure that a reader misreads is worse
than one they cannot read at all, because a blur invites a second look and a wrong glyph does
not.
