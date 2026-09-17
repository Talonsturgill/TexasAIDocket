# Discoverability signoff

## Discoverability signoff

- **One decision's card, opened as an image.** Opened `docs/og/tx-2026-0162.png` for the run's
  newest item, the Memorial Hermann entry. The card renders, the flag panel and the star are
  intact, and the headline wraps after "send" and after "an" where a reader would break it. It
  ends "AI drafted..." because the title runs past what the card holds, so the reader gets the
  subject and not the object. The cut lands on a word boundary rather than mid word, which is
  what the wrapper promises, and the title is the thing that is long rather than the card being
  wrong.
- **`/questions/`, read as a reader.** Opened the hub. Twelve shapes, each answered off the
  record, and the counts read 141 where every item can answer and 137 for how the public can
  take part, which is the four items whose room the record does not carry. The new entries are
  `contact_only` and answered under every shape. The questions are phrased as labels ("Who
  decides", "What happens next") rather than as sentences a Texan would type, which is worth a
  maintainer's eye and is not a defect this run created.
- **The `Open right now` section of `llms.txt`.** Ten entries. Cross-read against Phase 3: the
  offer cap review, tx-2026-0107, closes today, September 17th, 2026, and it is still listed,
  which is right on the day itself. Tomorrow's build is where it should come off. The calendar
  feed entry tx-2026-0024 is listed on its open meetings rather than on a comment date. No
  window that has already closed is on the list.
- **`/sources/`, the record's own report card.** The share at the top reads 700 of 784 claims
  resting on a primary document, across 243 documents from 108 publishers. This run added 22
  claims, 19 of them primary, so the share moved up rather than down. The top publisher is
  `interchange.puc.texas.gov`, 99 claims behind 20 documents, and its documents are filings,
  which is what the top of that list should be. One correction was made while reading it. The
  University of Texas at Austin's own account of its own award had been filed `journalism` on
  admission and is now `primary_official`, matching the record's own precedent for a state
  university speaking about its own work. The quoted material exemption is still confined to
  quotes.
- **`/topic/`, counting one card against its own page.** The hub card for health and education
  reads 19 decisions and the beat page lists 19. The eight beats sum to 141, which equals the
  front page counter. The beat's `still open to comment` figure is absent for this beat and
  present for defence and federal at 3 and power and the grid at 1, and the front row prints 04
  doors open, which is the same set counted the same way.
- **`/place/`, for the places this run landed something in.** Harris County reads 14 on the hub
  and lists 14, carrying the Memorial Hermann entry. Denton County reads 3 and lists 3, carrying
  the North Texas gift. Travis County lists 21 and carries the robotics centre award. The
  Houston metro page headlines 22 items and lists 22, names Galveston, Harris, Brazoria,
  Montgomery and Waller as the counties the record has reached, and still names Austin,
  Chambers, Fort Bend, Liberty and San Jacinto as the ones it has not.

## The pages, looked at rather than checked

- **The water map's pins against the day's reservoir count.** The readout prints 119 reservoirs
  and the map carries 119 hit targets. No lake is drawn short. The page is stamped September
  16th, 2026, which is the collector's last run rather than a stopped instrument, and both page
  checks exit 0.
- **A place page for a metro where the record just landed something.** Read above. The count
  matches and the untouched counties are still named.
- **The `backlog:` lines the build prints.** The build printed none. Neither ratchet grew.

## The scanner's daily ceiling

**NOT CHECKED, and the reason is a missing connector rather than a quiet day.** No Supabase tool
is exposed to this session, so the `scanner.scans` count against `daily_cap` could not be asked.
That is the third outcome the routine names, so it is recorded here and the run carried on.
