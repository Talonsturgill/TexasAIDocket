# Run record, October 1st, 2026

Effort at wake: `high` (as the repo's settings carry it). The no-stall hook logged `armed` at
SessionStart with `CLAUDE_CODE_SESSION_ATTENDED=0`.

## Craft refresh

Focus: the most repeated named defect of the last three decks, kit people that read as
mannequins, and the roadside world a plate reader deck would stand in.
- Flock's own spec sheet in a village board packet gives the hero at true scale: a 12 ft DOT
  breakaway aluminum pole of 2.875 in OD in black, dual solar panels 21.25 by 28 in on the pole
  top, and a camera body 8.75 by 5 by 2.875 in on band clamps.
  https://www.longgroveil.gov/sites/default/files/fileattachments/village_board/meeting/packets/7817/05b_flock_camera_specifications.pdf
- Screen space contact shadows are what ground a thin object where it meets a surface. A pole is
  the case a shadow map misses, so `TXT.contact` under the pole base is not optional.
  https://threepipe.org/plugin/SSContactShadowsPlugin.html
- Mannequin read: the literature on low poly figures says the read comes from form and material,
  a matte uniform skin and a missing silhouette break (hair, collar, a held object). Keep people
  small, at distance, in silhouette against the sky, never as the subject.
  https://superhivemarket.com/products/base-mesh-pack---normal-humanoid-mannequins
- Nothing found on instanced counts in editorial 3D that this engine does not already do.
  https://lab.imedd.org/en/?p=20466

## Discoverability signoff

- **Card.** `docs/og/tx-2026-0146.png` (the run's newest item, Wiwynn's El Paso County plant), opened
  as an image. Four lines, broken at "Wiwynn / say", "expand / the", "County / plant", ending
  "builds..." on a whole word. Reads cleanly.
- **`/questions/`.** Seven question pages, each answered across 157 to 167 entries: what has been
  decided, what happens next, when each started, what kind, what sources, ERCOT or not, last
  checked. Questions a reader would type. No new room or status today to stretch a shape.
- **`llms.txt`, Open right now.** Ten entries with dated ways in. The October 11th Zipline window,
  the October 9th energy department window and League City's November 3rd election are all still
  open and all listed. Nothing that closed today is listed.
- **`/sources/`.** 903 of 1018 claims rest on a primary document, across 297 documents from 130
  publishers. Today's admission (Wiwynn) rests on two company releases, which are primary for what
  the companies say. The top publisher is interchange.puc.texas.gov, 141 claims, filings that read
  as filings.
- **`/topic/`.** Data centers, the beat today's admission joined, prints 32 on the card and lists 32
  decisions on its page.
- **`/place/`.** El Paso County, where today's admission sits, prints 9 items and lists 9.

## Instruments

`gridwatch_pagecheck` and `waterwatch_pagecheck` exit 0, and every discoverability check and
self-test exits 0 (`media_check`, `schema_check`, `og`, `favicon`, `truetype`, `indexnow`,
`seo_check`). The build printed no `backlog:` lines.

**Scanner ceiling.** Not checked. This run has no Cloudflare D1 access and no Worker settings
access, so `today`, `failed_24h` and the live `DAILY_CAP` are all unknown. Nothing is reported
healthy from a repository default.
