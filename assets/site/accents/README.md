# Site finishing artwork

Two original decorative illustrations generated with the built-in image generator on September 18th, 2026. The approved transparent masters, exact generation and editing prompts, and compact web exports are retained here.

## Placement

- Home uses the limestone relief beneath the existing star in the open right margin.
- Services uses the limestone, graphite, copper and drafting-paper assembly beside its introduction.
- Home, Services and About reuse the limestone relief as a small footer signature.

Hero images appear from 68rem. The footer signature appears from 74rem and at phone widths up to 34rem. On phones it sits beside the existing star, above the links. These decorations add no text, controls, layout height or animation. CSS backgrounds keep them out of the accessibility tree and away from hit targets. Print and forced-colors modes omit them.

The landscape is an imagined regional illustration, not a photograph, mapped geography or evidence of conditions at a real place. The assembly is an abstract material study, not a product or technical diagram.

## Daily rebuilds

`scripts/site/site_build.py` copies only the two selected 960px AVIF exports into every generated site and writes `finishing.css` from `theme.finishing_css()`. The homepage includes the same rules in `home.css`. Services and About request the content-versioned `finishing.css` through the shared page shell. The shared `site.css` stays unchanged.

Every daily or collector run that calls the normal site builder therefore carries the artwork forward. A missing source export fails the build. The site determinism and freshness checks compare the generated assets along with the rest of the publication. No image generation or image conversion runs during publication.

## Files and provenance

- `masters/balcones-relief-v2.png` and `masters/studio-assembly-v2.png` are the selected transparent masters.
- `balcones-relief-v2-960.avif` and `studio-assembly-v2-960.avif` are the selected web exports. They preserve alpha transparency and were encoded with macOS sips at quality 65.
- `prompts.json` records the original generation prompts, transparency edits and export settings. No generated lettering or numerical claims appear in the artwork.
