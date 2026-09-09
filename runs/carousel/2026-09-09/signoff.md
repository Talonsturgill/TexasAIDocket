## Discoverability signoff

Six surfaces, opened rather than inferred, one line each. The build under all of these is
`out/2026-09-09/tmp/site`, rebuilt after every fix below.

- **One decision's card, opened as an image.** `og/tx-2026-0137.png`, the run's newest item.
  **LOOKED AT, AND IT CHANGED THE RECORD.** At its admitted length the title wrapped to four
  lines and the wrapper cut it at "the hospital's AI at...", which is a whole word and is still
  a preposition left hanging in the air. The title was rewritten to sixty seven characters and
  the card now carries the whole headline with nothing dropped. The card is the only version of
  an entry most people ever see.
- **`/questions/`, read as a reader.** **LOOKED AT, AND IT WAS WRONG.** The hub counted six
  decisions under "Where a comment window is open", a heading whose own subtitle says "The
  decisions taking written comment right now". Three of the six had closed, on August 11th, on
  August 31st and on the day before the build, and each of those three was also being told in
  its own answer that a comment window is open. `/topic/`, reading the same ledger, said three.
  Fixed at the source in `scripts/site/schema.py`, which now asks `docket_build.window_state`
  rather than reading the stored room, and the three closed items answer honestly instead of
  being dropped. The hub now says three. The self-test could not go red on this and now can, in
  both directions.
- **The `Open right now` section of `llms.txt`.** Ten entries, cross checked against the six
  items the ledger holds in an `open_comment` room and against the windows Phase 3 re-verified.
  Every listed item still has a dated way in, today's ERCOT admission included, and none of the
  three windows that closed appears anywhere on it. That is what established the defect above
  was in the questions page rather than in the record.
- **`/sources/`, the record's own report card.** The share at the top reads 544 of 626 claims
  resting on a primary document, across 207 documents from 94 publishers. Today's three
  admissions all cite a primary document and the share did not fall. The top publisher is
  `interchange.puc.texas.gov`, the commission's own filing system, which is the right thing to
  be leaning on hardest, and its document list reads as filings rather than as coverage of
  filings. The punctuation and numeral exemption is still confined to quoted material and is
  not covering any of this project's own sentences.
- **`/topic/`, counting one card against its own page.** Health and education carries eleven
  decisions on its card, which is the beat this run landed in, and the beat page lists eleven.
  The eight cards sum to 115, which is the count the front page's own counter prints. The three
  "still open to comment" figures on the cards sum to three, which is the number the ledger
  computes and is what caught the questions page.
- **`/place/`, for the places this run landed something in.** Harris County is on the hub at
  ten items and its page lists ten, the Houston Methodist entry among them. Lubbock County is
  on the hub at two and its page lists two. The Lubbock area page names the counties nothing has
  been found in yet, which is Cochran, Crosby, Garza, Hockley and Lynn.

**The pages themselves.**

- **The water map's pins against the day's reservoir count.** The readout says 119 reservoirs
  and the map draws 119, plus three more in the legend that shows what a fill level looks like.
  Nothing is one lake short.
- **A place page for a metro where the record just landed something.** Covered above. The counts
  in the headlines match the items listed under them and the untouched counties are still named.
- **The `backlog:` lines the build prints.** There are none. The list held three entries at wake
  and holds none now.

**Both instruments are current and holding their promises.** `gridwatch_pagecheck` and
`waterwatch_pagecheck` both exit 0. Nothing stopped and nothing read wrong, so there is no
finding for the top of this record.

**The scanner ceiling was NOT checked, and that is a gap rather than a clean result.** The daily
cap query needs the Supabase connector on project `texas-ai-scanner` and no Supabase connector is
attached to this session. Nothing was read, so nothing is known about today's scan count, the cap
or any failures in the last day. This never blocks a run and it did not block this one.
