# What the sibling site does, and what Texas took from it

A close read of the Alaska product's published site and its stylesheet, done because the owner
looked at both and said the Texas one felt web 2.0 and the Alaska one felt like a real designer
made it. That judgement was correct. This is what the difference actually was, device by device,
and what Texas built instead.

Read this before changing anything about the site's chrome. It is here so the next context
starts from the finding rather than re-deriving it.

---

## 1. The finding, in one line

**The Alaska page has weather and the Texas page had none.** Everything else on the list below is
real, and none of it matters as much as that. A flat dark rectangle reads as a default no matter
how good the typography on it is.

---

## 2. Device by device

| Device | Sibling | Texas v1 | Texas v2 |
|---|---|---|---|
| Atmosphere | Aurora: 3 drifting blurred veils, 2 skewed curtains, star field, periodic meteor | none, flat `#141020` | Big Bend at dusk: horizon glow, 2 heat-shimmer bands, 3 warm veils, 24-star field |
| Texture | Film grain, `mix-blend-mode:overlay`, opacity .55 | none | same idea, generated with no dependencies |
| Signature mark | Big Dipper and Polaris in gold, upper right | 1em star in the masthead | the Lone Star with halo and spikes, upper right |
| Display size | h1 to **92px** | h1 to **41px** | h1 to **~90px** on its own scale |
| Colour inside the headline | last word gold via `h1 em` | none | `<em>` in the accent |
| Eyebrow | live daylight pill with a shine sweep | none | live ERCOT pill with a shine sweep |
| Calls to action | one filled gold, two ghost | none | one filled, two ghost |
| Counters | 4 mono stats, one gold, zero-padded | none | 4 mono stats, one accent, zero-padded |
| Nav | sticky, glass fades in on scroll, underline wipes in from the left | solid bar, border toggles | same two devices |
| Cards | gradient panel, hover lift, status-tinted border, date at 44px, status badge | flat list rows | gradient panel, hover lift, status border, date at 40px, status badge |
| Signal colours | 4 (green, amber, blue, violet) | 1 accent plus urgent | 4, each derived per mode |
| Scroll feedback | 2px gold progress hairline, scroll-driven | none | same |
| Reveals | IO-driven, staggered hero rise | none | same, but failing visible |
| Footer | brand, 13-link row, 7 social buttons, mono colophon with coordinates | star, 2 paragraphs, 3-row table | brand, 12-link row, mono colophon with coordinates |
| Chrome scale | mono at 11 to 13px, letterspacing .09em to .24em | mono at 11px, letterspacing .04em to .06em | letterspacing raised to .13em to .17em |

---

## 3. The five that carried most of the difference

**One. Size.** The headline was less than half the size. A front page gets to be loud exactly
once, and the type scale that is right for a heading is not right for a masthead. Texas v2 gives
display type its own scale, `--d1` and `--d2`, separate from the reading scale.

**Two. Atmosphere.** See section 4.

**Three. The eyebrow that is alive.** The sibling opens with how much daylight its state capital
has left today and how fast it is losing it. It is one line, it is true, and it is different
every morning, and it does more for the feeling of a live product than any amount of layout.

**Four. Colour that means something.** Four signal colours, each carrying one state, is why a
reader can scan that docket without reading it. Texas had one accent and one urgent red, so
every row looked the same and the reader had to read.

**Five. The bottom of the page.** A record that ends in a build stamp tells a reader they have
reached the end of a document. The sibling ends in a way out and a colophon. The colophon is the
line people quote back.

---

## 4. Atmosphere, and why Texas did not copy it

The aurora is vertical, cold, northern and specific. Porting it would have been the single
loudest possible tell that this product was cloned. What ports is the LESSON: a page that
depicts a real place at a real hour reads as made.

Texas is **Big Bend at dusk**, which was already the stated base register and had never been
drawn:

- **Horizon glow.** The sun goes behind the Chisos and the bottom of the sky stays lit long
  after the top has gone. Warm, low, and the opposite end of the frame from an aurora.
- **Heat shimmer** where the sibling has curtains. Air off hot ground, banding and sliding
  sideways just above the skyline. Horizontal and warm against vertical and cold.
- **A dense star field, which is earned.** Big Bend is a certified International Dark Sky Park
  with among the least light pollution left in the lower 48. The star field is drawing a fact
  about the place, not borrowing a device.
- **The Lone Star** where the sibling puts a constellation. One star rather than a pattern,
  which is the entire point of the thing.

On paper the whole sky thins to a haze and the star field comes off. A star field on a cream
page is confetti.

---

## 5. Things the sibling does that Texas deliberately did not take

- **A meteor every seven seconds.** Charming once. On a record about public comment deadlines it
  is motion competing with a countdown, and it is the first thing that would look silly in a
  screenshot pasted into a commission filing.
- **A view-transition opt-out comment.** Already handled here by never adding one.
- **Grain via Pillow as a soft dependency.** Their own source records a build that shipped every
  page with the texture silently stripped because the box lacked Pillow. Texas writes the PNG
  from the format up with `zlib` and `struct`, so it cannot go missing and it is byte-stable,
  which the freshness gate needs.
- **`overflow-x:clip` on `body`.** Copied at first and it silently broke `position:sticky`,
  because a clipping ancestor becomes the scroll container a sticky element resolves against.
  The bar detached and rode down the page over the copy. It belongs on `html`.

---

## 6. Two mistakes worth not repeating

**Hiding content in CSS and relying on script to bring it back.** The reveal pattern is
`opacity:0` until an observer adds a class. Written the obvious way, any failure between those
two points leaves a reader looking at a blank column with the content present and invisible. In
v2 the stylesheet hides nothing on its own: the script marks each element `pending` at the
moment it observes it, so no script means no marking means no hiding, and a timeout reveals
everything anyway if the callback never runs.

**Class-name collisions when a design system grows.** `.tag` was already the topic chip. Reusing
it for the hero lede rendered the opening paragraph as a bordered mono chip, which looked
deliberate enough to survive a glance. Check the existing stylesheet before naming anything.

---

## 7. What is still not ported

Honest list, so nobody assumes these were considered and rejected.

- An email capture block above the footer. Texas has no list yet.
- Social buttons in the footer. Texas has no accounts yet, and a row of dead icons is worse
  than none.
- The timeline rail with a pulsing today tick, used on their docket item pages.
- A latest-deck and latest-video panel on the front page, which needs Wave 7 to exist first.
- Per-item door illustrations.
