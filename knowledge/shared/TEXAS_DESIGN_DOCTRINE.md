# Texas design doctrine

The visual standard for everything this project publishes: the website, the carousel, and the
video. Read it before drawing anything.

Four files pointed here before it existed. `config/brand.yaml` cited it twice for the palette
rules, `knowledge/shared/README.md` listed it in the index, and
`.claude/agents/carousel-treatment-director.md` tells a director to read it before pitching. A
doctrine that is referenced and absent is worse than one that was never promised, because every
reader of those files believes the argument was had. It is had here.

---

## 1. The one question this doctrine answers

**Would a Texan believe a Texan made this?**

Not "does it have Texas colours on it". The failure mode is a generic dark theme with tokens
named after Texas things, which is what this site was before this document. Renaming `#8C5A3C`
to `rust` does not make it Texan. It makes the config a mood board.

The test is material and structural: does the palette come from stone and ground that exist,
does the geometry come from a device the state actually uses, and would the result look wrong
if you moved it to another state? If it would work equally well for Oklahoma, it is not done.

---

## 2. The four registers to draw on

These are the authentic ones. Everything visual in this project comes from one of them.

### The Capitol
Faced in **sunset red granite** quarried at Granite Mountain in Burnet County. It is the most
public, most specific and least sentimental red the state owns, and unlike the flag red it
carries no urgency and can be used freely. The rotunda floor carries the seals of the six
sovereigns as a **geometric inlay**, which is the licence for terrazzo-like division of a field.

### Big Bend at dusk
The dark register. A deep violet-navy that is a real light at a real hour, in `#141020` to
`#252041`, warming into ember and gold at the horizon. It is not "dark mode". It is a place.

### Caliche
The pale calcium-carbonate hardpan that a ranch road is cut down into. Warm, dusty, pinkish
buff. **The same stone is the type at night and the ground in daylight**, which is why light
mode here is not a lightened dark mode and not a generic cream.

### Working documents
Two traditions, both Texan, both about instruments rather than decoration:

- **Mid-century oil charts.** Two-colour printing, heavy rules top and bottom of a table with
  hairlines between, flat fields, tabular figures. The weight of a rule tells you where a table
  starts and stops without drawing a box around it.
- **Survey and engineering drawing.** A neatline. A graticule. A scale bar. A title block in
  the corner saying what the sheet is and when it was last revised. This is the register the
  whole site is in, because the site is a record and a record is a document.

And one discipline rather than a look:

- **Marfa.** The empty field is the composition. Space is the most Texan thing on the page and
  the cheapest to get right. When in doubt, take something out and add air.

---

## 3. The traps

Avoid, permanently, without needing to relitigate:

| Trap | Why |
|---|---|
| Longhorns, cowhide, rope borders, lassos, boots, spurs, wagon wheels, cactus | Costume. It is what an outsider draws. `theme.py --self-test` fails the build on these words. |
| Wood type and saloon lettering | A different century and mostly a different state's mythology. |
| The Six Flags motif | One of the six is the Confederate flag. Not a debate worth inviting onto a record page. |
| A distressed or weathered texture | Says "vintage", says nothing about Texas. |
| Burnt orange as a brand colour | It belongs to one university and instantly reads as that. |
| Any hue that means "bad" | A severity ramp is a verdict. See section 6. |

---

## 4. The mark

**A single solid five-pointed star, set in a blue hoist block.**

The Lone Star flag is a blue hoist band carrying a white star, then white over red. The wordmark
is that construction and nothing else. It is the one Texas device that is simultaneously
**statutory, geometric, abstract and legible at 16 pixels**, which is why it is the mark and a
longhorn is not.

The star appears exactly twice on a page, and the restraint is the point:

1. **The masthead**, in the hoist block, at text scale.
2. **The footer title block**, large and quiet, as a colophon.

It is never a bullet, never a divider, never a background watermark, and never rotated.

Flag colours are **Pantone 193 and Pantone 281 by statute**. The hex values in `brand.yaml` are
a labelled derivation, not the law, and the site says so.

---

## 5. Colour is computed, not chosen

The compute-not-generate law in `CLAUDE.md` governs published numerals. **A contrast ratio is a
numeral and a palette is data, so the same law applies here.** This is not an analogy, it is the
same rule.

- Every foreground and background pairing the site renders is measured against WCAG 2.1 and
  gated in `theme.py --self-test`. A pairing below threshold is a build failure.
- Where a token can't meet its target as authored, the value is **derived**: the colour is
  walked toward white or black in 8-bit steps until it clears the ratio, in code, at build time.
- A colour used in more than one place is derived against **every** ground it lands on. Solving
  against the page alone is how a value passes its own test and fails where a reader meets it.

**The case that forced this.** Texas red on Big Bend night measures **2.94 to 1**, which fails
even the 3 to 1 floor for large text. The element wearing it was the countdown telling a reader
how many days remained to file a comment. The single most consequential number on the site was
the least legible thing on it, and it had passed review because it looked fine to someone who
already knew what it said.

The derived urgent red is `#D7677E` on the dark register and stays the authored `#BF0A30` on
paper, where it already clears. It is still recognisably the same red, which is why the fix is a
derivation rather than a substitution: the reservation on that colour means nothing if the
colour changes identity.

`theme.py --contrast` prints the whole table. Run it before arguing about a colour.

### The palette, as it actually ships

| Role | Dark (Big Bend at dusk) | Light (caliche in sun) |
|---|---|---|
| page | `#141020` night | `#F6F1E4` paper |
| panel | `#1B1830` deep | `#EDE6D6` limestone |
| raised | `#252041` panel | `#E4D8C3` caliche |
| body ink | `#E4D8C3` caliche | `#1B1830` deep |
| heading | `#EDE6D6` limestone | `#141020` night |
| muted | `#C9B393` dust | `#625E64` derived |
| hairline | `#3B2A4A` line | `#CFC2A6` paper rule |
| control edge | `#756980` derived | `#837A69` derived |
| accent | `#E0956A` dusk gold | `#9A3B2A` Capitol granite |
| accent fill | `#B4664F` dusk ember | `#6F2A1E` derived |
| **urgent** | `#D7677E` derived | `#BF0A30` flag red |

A token that is defined and never used is decoration pretending to be a decision.
`brand.yaml`'s `site_palette` names which tokens the website uses, and the self-test requires
every one of them to reach the stylesheet. `rust`, `bluebonnet` and `mesquite` are real Texas
material with no job on a record page, so they are declared **deck only** and the self-test
fails if one of them leaks into the site.

Beyond the fixed tokens, **each deck draws its accents from the material world of its own story
and region.** A Permian story is caliche, rust and flare orange. A Piney Woods story is not. One
palette across all regions is the tell that an outsider drew it.

---

## 6. A bar and never a dial

The instrument pages publish measured load, modelled load, the residual, and the size of what
is not public. **They never publish a verdict.**

That constrains the drawing directly:

- The gauge is a **bar**, never a dial. A dial implies a red zone, and a red zone is a verdict.
- The fill carries **one hue at one intensity at every value**. The length is the whole message.
- The county map has no severity ramp. A county is lit or it is not.
- No colour anywhere may mean "bad".

`theme.py --self-test` refuses a `.fill.warn`, a `.bar.crit`, the word `dial` and any
`conic-gradient`. If a future edit needs one of those, it has changed what the page claims, and
the gate is where that argument has to happen.

---

## 7. Type

**Fraunces** display, **Manrope** body, **JetBrains Mono** data. Kept deliberately from the
sibling product: changing the typeface would cost the family resemblance and buy nothing.
Differentiation is by colour and geometry, not by type.

Figures are set in the mono face with **tabular numerals**, always. A number on this site is a
measurement, and tabular means a reader can compare two of them by eye without counting digits.

**The type has to actually ship.** For the whole first life of this site, `brand.yaml` named
three faces, `theme.py` wrote them into every font stack, `assets/fonts/` held all three on
disk, and nothing served them. Every reader got Georgia and system-ui. A font stack that names a
family no `@font-face` defines renders perfectly well in the fallback, so nothing threw and
nothing looked broken.

`scripts/site/fonts_build.py` subsets the three faces to 105 KB total, axes pinned to what is
actually used, and `port_audit`'s `assets` gate now fails the build if a served font is missing
**or** if a named family has no rule defining it. Both halves, because either one alone stays
silent.

All three are SIL Open Font License 1.1 and the licence ships beside them. The copyright lines
are **read out of each font's own name table**, not typed from memory.

---

## 8. The page as a sheet

The site is a document, so it is built like one.

- **Section furniture.** A hairline rule runs the full width above each section heading, with a
  short heavy tick at its left end. That is a drawing sheet's zone division, and it costs two
  declarations.
- **Tables** take the oil-chart treatment: two-pixel rules top and bottom, hairlines between.
- **The title block.** Every drawing sheet ends in one. The footer carries the sheet name, a
  link to the record, and the revision date, set in mono, beside the star at colophon scale.
- **Marfa spacing.** One band step, `clamp(3rem, 7vw, 5.5rem)`, between every section. Used
  everywhere so the rhythm is a decision rather than an accident.

### The map is a survey, not an infographic

All 254 counties, drawn from the same geodata the resolver uses, lit by the record. Plus the
furniture that makes it a survey sheet:

- A **neatline** around the field.
- A **graticule**: whole-degree ticks, each placed where its own meridian or parallel actually
  crosses the frame, found by bisection. A conic projection's meridians are not vertical, so a
  tick placed by measuring from the corner would be in the wrong place, and confidently so.
- A **scale bar** in a round number of miles, its length computed from the projection and the
  largest round step that fits the sheet. Albers is equal-area rather than equidistant, so the
  bar can't be exact everywhere; it is sampled at the reference latitude between the standard
  parallels where the error is smallest, and the projection is named in the accessible title.

The scale bar is **checked the way a reader would use it**: the self-test measures El Paso to
Jefferson off the drawing and compares against the great circle. That is the longest span the
state offers and therefore where an equal-area projection's distance error is worst. It comes
out **736 miles against a true 743, under one percent**. A decorative scale bar is worse than
none, because it invites a reader to measure with it.

---

## 9. What "Texas First" looks like on a page

The voice is not tone deaf about data centres and it is not against them. AI is transformational
technology and Texas should win with it. That position has a visual consequence:

**The design never dramatises.** No alarm colours, no urgent typography, no charts that lean.
The most persuasive thing a record can look like is a working document that has nothing to
prove, and a reader who is sceptical of both boosters and opponents will trust an instrument
before they trust an argument.

Restraint here is not neutrality. It is the argument.
