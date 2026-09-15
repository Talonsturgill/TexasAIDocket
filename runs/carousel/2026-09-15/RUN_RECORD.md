# Run record — 2026-09-15 — carousel no. 25

## The record

**Worklist.** The selector named 8 items due, on the 2 day leash, out of 135 held at wake.
Nothing was deferred and nothing was rotten. `reverify.py --apply` fetched 12 urls behind 40
claims, 2 answered 304 and 10 sent a body, none failed to answer. Seven items came back
unchanged and were stamped. All seven deterministic movement lines were re-worded by hand and
`reverify.py --check-notes` passed on 781 checked notes, so no figure was added to any of them.

**One thing moved.** `tx-2026-0109`, Senate Economic Development, claim `c7`. The quote marking
the September 3rd hearing canceled is no longer on
`capitol.texas.gov/Committees/MeetingsUpcoming.aspx?Chamber=S`, because that listing carries only
what is still ahead and September 3rd has passed. The record's own history had noted the row
dropping off on September 9th and the claim had not been moved with it. The claim now cites the
committee's own meetings page,
`capitol.texas.gov/Committees/MeetingsByCmte.aspx?Leg=89&Chamber=S&CmteCode=C525`, which still
carries `September 3, 2026 9:00 AM (Canceled/see notice)`. The September 22nd public hearing in
E1.016 was re-confirmed on both listings.

**Admitted, 3.** The ledger went from 135 items to 138 and from 742 claims to 762.

- `tx-2026-0159` — ERCOT's Large Load risk list, put to its own board on September 14th and 15th.
  Statewide, on ERCOT. Primary, the board presentation and the PGRR144 rules page. **This run's
  deck is built on it.**
- `tx-2026-0160` — the Houston academic physician practice moving from two ambient AI pilots to
  one system. Harris County. Primary corporate, the medical school's own account.
- `tx-2026-0161` — UT Arlington's federally funded tutor that withholds the answer, now being
  tested on Fort Worth police de-escalation training. Tarrant County. Primary, the university's
  own release.

**Held, and why.** Carrollton's September 15th consent item leasing 82 Flock cameras is
primary-sourced on Legistar and was read this run, and it is held because the agenda itself
carries no AI language and the vote had not happened when it was read. El Paso ISD's AI
governance framework item, also set for tonight, is held because its agenda PDF was not fetched
and read this run. Hays County's Axon contract is held because the only sources found are
journalism and two of them disagree about the vote date. Samsung's Taylor plant starting AI5
prototype wafers is held on journalism alone. Project Watershed 250 is held because the
Governor's own release never uses the words artificial intelligence and only the vendors' do.

**The backlog was 0 at wake and is 0 after admission.** Both ratchets stayed closed. Every item
admitted this run names its counties or is statewide on the source's own terms.

**`/sources/` share.** 660 of 762 claims rest on a primary document, across 233 documents from
105 publishers. The three items admitted today are primary on every claim, so the share did not
fall.

## Discoverability signoff

- **One decision's card, opened as an image.** `og/tx-2026-0149.png`. The headline wraps after
  "foundation", "A&M" and "station", all places a reader would break it, and the truncation ends
  on the whole word "digital" followed by an ellipsis rather than on a stump. The star plate and
  the wrap look right. LOOKED AT, clean.
- **`/questions/`.** Twelve question shapes, 135 answered on most and 04 on the open comment
  window. These read as questions somebody would type. "Where a comment window is open" answering
  04 against 135 elsewhere is the shape working rather than failing, because it is a claim about
  today. LOOKED AT, clean.
- **The `Open right now` section of `llms.txt`.** 11 entries. Every comment window with a close
  date on or after today is listed and nothing closed is. Project 59550 closing September 17th is
  there, which is the one Phase 3 re-verified this morning. **One finding, and it is a design
  question rather than a fault.** `tx-2026-0075`, Pflugerville's November 3rd charter election,
  has a future dated way in and is NOT listed, because `feeds.py` filters the section to the
  `open_comment` and `open_meeting` rooms and that item's room is `ballot`. `tx-2026-0048`, also
  a November 3rd election, IS listed because its room was recorded as `open_meeting`. Two
  elections on the same day, one published as a live door and one not, on how the room was
  recorded rather than on what a reader can do. Written up for the upgrade lane, not touched
  here.
- **`/sources/`.** The share is at the top and is read above. Top publisher is
  `interchange.puc.texas.gov` at 99 claims across 20 documents and 8 entries, which is the PUCT's
  own filing system and is exactly what a record like this should lean on hardest. Second is
  `api.nsf.gov` at 54 claims, third `webapi.legistar.com` at 37 with 29 of them primary. Nobody
  in the top three is a publisher who would be wrong to find there. Quoted material still carries
  its punctuation and numeral exemption and no house sentence is hiding inside it. LOOKED AT,
  clean.
- **`/topic/`.** 8 beats. The per-beat card counts are 30, 6, 16, 15, 15, 25, 17 and 11, which sum
  to 135 and match the front page's own `135 Decisions tracked`, and each matches the ledger's own
  count for that beat. Two beat pages were opened and counted item by item, research and science
  at 25 and health and education at 16, and both match their cards. The `still open to comment`
  figures read 3 on defense and federal and 1 on power and the grid. LOOKED AT, clean.
- **`/place/`.** 64 of 254 counties named, across 28 statistical areas. Re-checked after
  admission for the places this run landed something in. LOOKED AT, clean.

## Instruments

Both page checks exit 0 and the water page self-test exits 0. No instrument has stopped and no
page is reading wrong, so nothing in `scripts/site/gridwatch_page.py` or
`scripts/site/waterwatch_page.py` was touched.

**The water map's pins against the day's reservoir count.** The readout prints `Reservoirs 119`
and `ledger/gridwatch/water.jsonl` holds 119 reservoirs for September 14th, with Addicks and
Barker excluded for having no conservation pool and Elephant Butte excluded as out of state. The
map svg carries 122 tank circles, and 119 of them carry a decile class while the other three are
the key, the dots group and the legend. The drawing is not one lake short. COUNTED.

**The scanner's daily ceiling was NOT checked.** No Supabase connector is available in this
session, so the query could not be run at all. That is the third outcome this phase names and it
never blocks a run, but it means nobody looked at the scan cap or the 24 hour failure count
today.

## Sources, as they actually behaved

- **`puc.texas.gov/agency/calendar/GetCalendarRss.aspx` answers a 302 to its own lowercase path.**
  A fetch that does not follow redirects gets 184 bytes of `Object Moved` and parses as zero
  items, which looks exactly like an empty calendar. Following the redirect returns 37 items.
  Appended to the field log.
- **`capitol.texas.gov/Committees/MeetingsByCmte.aspx`** answers 200 under a browser User-Agent,
  sits under no disallowed path in the live robots.txt, and carries a committee's PAST meetings
  including cancellations, which the upcoming listing does not. It is the durable home for a
  claim about a meeting that has happened. Appended to the field log.
- **`www.ercot.com`** behaved as the registry describes. The board materials and the market rules
  pages answered 200 under a descriptive User-Agent.

## The deck, and the two decisions a judge should not have to reconstruct

### The value arc was REWRITTEN, not redrawn, and here is the measurement that decided it

`panel_ready` held the deck at a deck median L* of 16.9 against a planned 40, a miss of 23.1
where one Munsell value step is 10. The routine allows either answer and asks which was taken.
**This run rewrote the arc.** The reason is a property of the press rather than of the drawing.

On a dark ground `TXINK` lays LIGHT ink where the source is light, so a screened frame's median
is bounded by how much ink its screen can physically put down. Measured by printing a white
field through each of this deck's own screen configurations and reading the press back:

| screen | mean of a white field | that frame's ceiling |
|---|---|---|
| stipple, cell 5, 6 dots per cell | 63 of 255 | L* 27 |
| hatch, cell 6 to 8 | 108 of 255 | L* 45 |
| halftone, cell 6 | 206 of 255 | L* 83 |

Frame 3 is a stipple frame and the plan asked it for a median of 40, which is 13 above the
highest value that screen can reach with every pixel of the frame painted white. That is not a
deck that was drawn too dark. It is a plan that asked for a value the chosen screen cannot
print, and no gate in this repo asks that question at planning time.

The nine planned medians now read 9, 90, 9, 16, 88, 17, 60, 93, 10, re-derived from the press.
The paper frames are unaffected because their sheet is painted AFTER the press, unscreened.

**What this does not excuse**, stated because the same measurement would otherwise be an alibi
for any dark frame: a frame that came out dark because nothing was drawn in it. Frame 3 was one,
and it was rebuilt rather than re-planned. See below.

### Frame 3 was rebuilt, and the type's own scrim is what was eating it

The frame's whole content is a figure against a wall, and its dossier asks for a wall at least
six times the figure's height. It was measuring 329 px of visible wall against a 77 px figure,
because the hall stood 560 px tall with 231 px of it buried under the solid scrim the hook and
the dek sit on. A reader was shown a band at the horizon with two figures, a fence, bollards,
posts and tyre tracks in front of it, and at 432 px it read as noise.

Four changes, in the order they were made and each measured after:

- **The horizon went from 700 to 1042**, so the wall owns the middle band the dossier gave it
  and the apron owns the bottom third rather than 48% of the frame. Three numbers fix
  everything else and each is forced: the scrim ends at 430 because the dek does, the apron
  keeps 130 px because the pickup and the fence stand on it, and the figure must measure 55 to
  80 px, which fixes the depth at 26 m.
- **The wall is drawn from metres rather than taken from the catalogue.** `TXOBJ.data_center`
  puts its doors 8 m and 14 m from the ends of a 130 m hall and its roof plant 4.2 m over the
  parapet. Thirty three metres of hall fit in this frame, so either door brings an END of the
  building on screen and the record gives no capacity for any facility. The roof plant at that
  height lands in the scrim and comes off the press as cropped boxes under the dek.
- **The sky is painted after the press**, unscreened, which is the device frames 2, 5, 7 and 8
  already use for their sheet. A dawn painted at #D7AE79 into the screened plate printed at the
  same value as the ground beside it, for the reason in the table above.
- **The pad is graded caliche with stone on it.** A stipple over one value is still one value:
  the screen lays dots and a flat fill under it leaves every near-ground cell holding one tone
  plus a few dark specks, which `frame_balance` reads as a dead lower zone however many objects
  are standing on it. The bottom band went from 0.237 to 0.607 of the frame's own craft density,
  and the band ratio from 0.54 to 1.06, by adding tone under the dots rather than more objects.

The dossier was corrected with it. Its technique line named the catalogue, its palette named a
transformer yard that is not in the frame, and its acceptance list asked for every shadow to run
to frame LEFT when the deck's one declared light, azimuth -68 at elevation 6, throws every shadow
in every world frame to frame RIGHT and toward the camera.

### One strikethrough, fixed by moving the type rather than by covering the rule

Frame 2's `50 METRES` label had the hall's own bay divider running down through its glyph band at
x 130.7. A knockout plate does not answer that and the gate says why in its own docstring: paint
order is not consulted, because a dark hairline across a word reads as a strikethrough whichever
was rasterised last. The scale bar moved out of the elevation and into the sheet's clear upper
left quadrant, which is where a survey sheet puts it and where the only thing it can cross is air.
