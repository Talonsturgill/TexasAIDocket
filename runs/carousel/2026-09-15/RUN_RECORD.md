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
