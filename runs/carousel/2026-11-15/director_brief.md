# Directors room brief, carousel no. 78, November 15th, 2026 (BESPOKE run, LOOK V2)

## The story (docket item tx-2026-0248, statewide, health-and-education)
Texas 2036, a nonprofit policy group, published on November 10th, 2026 a preview of its report "In Ctrl of AI in Schools".
It reports a fall 2025 survey of Texas school and district leaders: 86% reported teachers using AI, 61% reported student use.
Only 29% reported a district policy governing student AI use, and 20% a policy for teachers and staff. By the group's own
analysis 42 states have issued some form of statewide AI guidance for schools, and Texas is not among them. Its four
priorities: statewide guidance, safety standards for tools before they reach classrooms, teacher training, and age
appropriate AI literacy for students. It is a recommendation. No state agency or district has acted on it.
The verified claims are in out/2026-11-15/claims.json. Every fact on a slide carries a claim id from that file.

Texan check: the story names no Texas place (statewide). The score has to be carried on the art and on the closing frame.
The record also holds related school items (Houston ISD AI board policy tx-2026-0053, Richardson ISD's legislative ask for
classroom AI guidance tx-2026-0177, machine scoring of STAAR tx-2026-0194, Alpha School pilots tx-2026-0200). Use them only
as context if the claims file carries them.

## This is a BESPOKE run. Read knowledge/carousel/BESPOKE.md first, then CLAUDE.md LOOK V2.
Pitch the deck's VISUAL ARGUMENT, its TONE (one of wonder, explainer, win, watch, people; recent decks were all staged dark
before today, so any tone is open; at most two `watch` in seven) and NINE BEATS: for each frame, what it must make a reader
FEEL and KNOW, the figure it carries, and a suggested world/camera/medium that differs from both neighbours. Do NOT pitch an
archetype layout list, rects or depth blocks: each frame's artist composes its own picture and type. The deck shares a spine
only (tone, palette, grade, type faces, counter, site line, the accent's ONE meaning).

## The kit that fits (ARSENAL.md, THE KIT): student_desk, student_desk_rows, classroom_window, school, school_bus, laptop,
person, desk, document_stack, monitor, capitol, public_seating, hearing_dais, podium. A model the kit has is never rebuilt.
Two render routes: TXT spatial scenes (txthree.js) and TXBENCH material reliefs (txbench.js). At least six of nine frames
physical. Text stays DOM. No print screen, ever.

## What the judges charged the last three decks (so do not do it again)
- a flat face-on square with a typed label, no subject or light (Nov 14 frame 2)
- a brushed metal plate filled with type, sockets reading as a UI (Nov 14 frame 9)
- a top-down orthographic tray that reads as a chart (Nov 14 frame 6); four packs dead on at one depth read as a bar chart (Nov 13 frame 4)
- a mannequin at a flat table in an empty bay (Nov 13 frame 8); capsule people
- an orthographic grille on a mid tone field (Nov 13 frame 5); flat mid grey slab with a stair stepped cast (Nov 12 frame 5)
The last fourteen decks put the headline top left at y 150 with the art under it on every frame. Every one of them was a
dark staged scene of kit objects. Today is the first LOOK V2 bespoke deck: lit colour, no black field, no black type band.

## Numbers
No numeral is produced by a model. Every count the art draws comes from figures.json (computed by compute.py from claim
quotes). A survey figure is what the leaders REPORTED to the survey Texas 2036 cites, never a measured share of classrooms.
If a frame draws 100 of something to show 86, say in the dek that it is drawn to illustrate, one per leader in a hundred.

## House rules for every word you write
No em or en dashes, no colons or semicolons in copy, no first person, "can't" never "cannot", no sentence opening with And or
But, straight quotes, dates "November 10th". Banned words: gap, gaps, matters, pattern, patterns. Say the specific thing.

## Craft refresh notes for the directors
- Unit charts invite but simplify; each unit must be one honestly stated thing (storytellingwithdata, unit charts).
- Cloth or paper on MeshPhysicalMaterial: small sheen (0.5 to 1.0), sheenRoughness 0.3 to 0.8, never a near white sheen color under a warm key (three.js cloth material notes).

## The rule that still travels (rotation), adapted for a bespoke run
The rotation rule changed on 2026-09-16 and BESPOKE (2026-11-14) supersedes it on this run: each frame owns its world, light,
camera and type position. The nine read as one post by the SPINE and the story's order. At least two continuity devices must
be doing real work (a recurring motif that evolves, a figure carried across frames, the accent's one meaning).
