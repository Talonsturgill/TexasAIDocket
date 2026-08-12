# Design doctrine — the visual standard

The rules that decide whether a frame is finished. They are not style preferences; each names a
specific way a slide dies, and most are checkable.

## Value structure, which is where slides usually die

**Every frame needs a real light and a real dark.** The commonest failure in generated art is a
single value group: everything sitting in one mid band, nothing anchoring the eye, the whole
frame reading as fog. It looks deliberate. It is not.

The check is simple and worth running on every render: can you name the lightest thing in the
frame and the darkest thing, and are they doing different jobs?

**A ridge has two edges.** A form drawn as one stroke is a line. The same form drawn as a lit
edge with a shadow immediately under it becomes something with a light side and a dark side.
This is the cheapest way to turn a drawing into a thing, and it costs one extra stroke.

**Weight must vary.** A constant line width reads as a drawn line at any density. Variance in
line weight is what the eye reads as texture, and the near field must carry visibly heavier
marks than the far field or there is no depth to read.

**Crests catch light.** A few dozen small specular points at the top of the value range do more
for material than hundreds more contour lines.

## Composition

**The frame has three horizontal bands and all three must work.** A slide with everything in
the top third and a blank bottom is not minimal, it is unfinished, and the QA harness measures
it. The fix is to move the mass or run the annotation down, never to enlarge the quiet zone.

**A contact shadow needs a lit ground to subtract from.** A shadow cast onto a surface that is
already near-black is a one or two L* change and reads as nothing. The fix is never a stronger
shadow; it is to light the ground first, then cast into it.

**Type over art needs a declared defence**: an opaque knockout plate, a scrim, or a halo. A
halo works because it is the opposite value. A plate works because it removes the art entirely,
and a plate at 93 percent opacity is not a plate.

**A leader must land on the thing it points at.** Author it as a polyline terminating on the
target's own coordinates, never as a fixed offset from the annotation. A leader stopping in
void looks exactly like a leader reaching something small, which is why the slide has to
declare where the target is.

## The Texas register

**The palette comes from the story's own ground.** A Permian story is caliche, rust and flare
orange. A Piney Woods story is loblolly green and iron-red clay. A Gulf story is haze and
galvanised steel. A Panhandle story is winter wheat, grain elevator concrete and a sky that
takes up four fifths of the frame.

Reaching for one palette across every region is the clearest possible tell that an outsider
drew it, and Texas is nine landscapes a Texan can tell apart instantly.

**Registers worth drawing on**, all authentic and none kitsch:

- **Capitol granite.** The sunset-red granite and the rotunda's star inlay. Institutional Texas
  as it actually looks, which is heavier and stranger than the postcard.
- **Marfa's discipline of the empty field.** Restraint as a positive choice. The single most
  under-used move available here.
- **Mid-century Texas oil graphics.** Two-colour, confident, industrial. Wordmarks and
  cross-sections from an era that took engineering drawing seriously.
- **Mission-control telemetry.** Houston's own visual language: monospace figures, plotted
  traces, the aesthetic of a number that matters.
- **The engineering drawing itself.** Section, elevation, callout, scale bar. A record product
  earns this register honestly.

**Never**: wood type, rope borders, cowhide, lasso frames, longhorn silhouettes as decoration,
or the Six Flags motif, one of which is the Confederate flag.

**The Lone Star is the mark.** Statutory, geometric, abstract, legible at 16 pixels. It is the
one Texas symbol that carries no kitsch, which is why it is the mark and a longhorn is not.

## Colour discipline

The tokens are in `config/brand.yaml`. Two rules about them:

**Texas red is reserved for genuine urgency** and nothing else. On the site that means a
closing comment window. Reserving one colour is what makes it mean anything when it appears,
and `theme.py` fails the build if it spreads.

**No severity ramp on a measurement.** A bar showing a value is one hue at one intensity at
every value. A colour that changes with the number is a verdict, and this product does not
publish verdicts about things it measures.

## The standard

A frame is finished when it could not be swapped into a different story. If it could, it is
decoration, and decoration is the thing this product is supposed to be an alternative to.
