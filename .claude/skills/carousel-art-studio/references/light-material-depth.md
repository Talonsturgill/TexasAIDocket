# Light, material and depth

## Light is part of the claim

Write the light plot before shading:

```text
Key: source, direction, size, color, story-world reason
Fill: source, ratio to key, what must remain readable
Practical/emissive: physical source and narrative job
Ground: value and material under the subject
Contact: where weight is proven
Atmosphere: what catches light and why it exists
```

One strong key with controlled fill usually reads better than many undirected lights. A rim
light is meaningful when it separates a subject from the environment or belongs to a real
source; otherwise it becomes a “cinematic” sticker.

## Value pass

Before color, identify:

- darkest anchor;
- lightest event;
- subject value group;
- type reserve;
- separation between adjacent planes.

The lightest and darkest regions need different jobs. Check the thumbnail in grayscale. If
subject and ground merge, color will not rescue them after platform compression.

## Material sentence

Do not say “make it tactile.” Define each important surface:

```text
Material:
Base value/hue:
Roughness / gloss:
Edge behavior:
Microstructure and scale:
Thickness / translucency:
Wear or manufacture:
What distinguishes it from the adjacent surface:
```

Material comes from response, not texture pasted on top. Metal needs coherent highlights and
edge behavior; paper needs fiber scale, thickness and soft grazing light; stone needs mass,
fracture and broad value variation; glass needs reflection/refraction logic and something to
reveal by transmitting.

## The depth stack

Build in this order:

1. camera and silhouette;
2. occlusion and overlap;
3. lit ground and contact shadow;
4. key-to-fill ratio;
5. local material response;
6. aerial perspective or depth fog;
7. optical finish.

Contact shadow on a black ground is invisible. Light the ground first, then subtract the
shadow. A floating hero object should float because the claim wants suspension, not because a
contact solution was skipped.

## Browser-native benches

- `txthree.js`: PBR, ACES, soft shadows, procedural environment, lighting rigs and hero-object
  helpers. Use for one consequential dimensional shot, not every slide.
- `txsdf.js`: ray-marched continuous forms, unions/cuts and impossible sections.
- `txrelief.js`: fast relit heightfields and 2.5D form.
- SVG diffuse/specular lighting plus turbulence/displacement: useful for paper, relief and
  surface detail that must remain browser-native.
- `txpost.js`: final grade, bloom, grain, sharpen and dither after structure is resolved.

Use the lightest bench that produces the shot. Complexity hidden behind a flat camera has no
value.

## Finish restraint

Bloom belongs to luminous energy, not every bright edge. Grain binds layers at final size;
visible repeating grain is texture wallpaper. Chromatic aberration and glow are not proof of
depth. Finish should make the materials feel photographed through one optical system, not make
the frame announce software.
