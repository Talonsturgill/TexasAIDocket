# WORKLOG — the record becomes a calendar

Opened 2026-08-20 on the owner's call: the record page lists the items open for
comment first, which is right, "but then after that, the fact that it just goes
into a big list of everything else, it's just not very digestible or readable".
Wanted: "a calendar view... the months laid out where everything is, the details
of everything, and they're able to click into specific things". Told to go slow
and make it robust.

**Read this first.** Resume from the task table at the bottom.

## What the data actually is, measured before designing

    64 items, 122 dated events, 9 kinds of date
    ordered 41 | hearing 26 | filed 19 | effective 14 | comment_closes 6
    statutory_deadline 6 | comment_opens 5 | signed 4 | decided 1

    range      2021-06-08 -> 2027-02-18   (68 months)
    statuses   decided 38 | pending 15 | open 11

    density is LUMPY and this is the whole design problem:
      2026-08  28 items      <- more than a third of the record, in one month
      2026-07  13
      2026-06  12
      most other months 1 to 5
      2026-10, 2026-12, 2027-01 and all of 2022 to 2024 are EMPTY

## The design, and why it is not a wall of day grids

**AN ITEM IS NOT A DATE.** Half the items carry two or more key_dates and one
carries five. So the calendar plots EVENTS, 122 of them, and an event links to
the item it belongs to. An item with a hearing in June and an order in August
appears in both months, which is true and is the thing a flat list hides.

**TWO LEVELS, because one does not fit the data.** A 7 column day grid is right
for August, which has 28 items to spread over 31 days, and is 90 percent
whitespace for a month holding two. Sixty eight of those stacked is not a page.

  1. A YEAR RAIL, revised while building C: years as ROWS, twelve month cells
     each, which is the classic year at a glance. A flat run of 68 chips was the
     first idea and it is worse: it hides that the gap is three whole years.
     Seven rows shows the record's real span in the height of a paragraph.
  2. A MONTH PANEL. The selected month as a real calendar, one cell per day,
     events sitting on their day, each a link into the item.

**Opens on the current month**, which is where a reader's question lives, and
which happens to be the dense one.

**The complete list is kept, folded.** The record has to stay wholly browsable;
what it stops being is the first thing you meet. `<details class="fold">` is
already the pattern on this page for the county tables, it needs no script, and
it is open to a keyboard and a screen reader by default.

## The rules this has to hold, none of which are optional

- **Numerals are computed, never typed.** Every count here comes from the
  ledger; `numeral_lint` fails the build otherwise.
- **The CSP hashes inline scripts.** Anything added runs through `csp.apply`,
  and `csp_runtime.mjs` will ask a browser what it refuses.
- **Contrast is gated** on every run of text against its composited ground.
- **Responsive at 12 widths, nothing overflows sideways.** A 7 column grid of
  text on a 390px phone does not work, so the month panel is a day grid on wide
  and a day-ordered list on narrow. That is a real fork, not a media query on
  font size.
- **House voice**: no em dash, no emoji, straight quotes, "can't" not "cannot",
  dates as "August 10th" with the month first.
- **docs/ is generated.** Never hand edited.

## Tasks

| # | task | state |
| --- | --- | --- |
| A | Measure the data, read the current page, decide the shape | DONE |
| B | This worklog | DONE |
| C | `docket_calendar.py`: bucket events by month and day, pure, self-tested | DONE, 26 checks |
| D | The year rail, server rendered, counts computed | TODO |
| E | The month panel: day grid wide, day-ordered list narrow | TODO |
| F | Selection: no-JS default, then progressive enhancement | TODO |
| G | Wire into `docket_index`, fold the full list | TODO |
| H | Styles in theme.py, contrast-safe both registers | TODO |
| I | `tests/docket_calendar.mjs`: a browser suite for read-time behaviour | TODO |
| J | Full nine-suite sweep, all named, plus site fresh | TODO |

## Wrap

W1. Delete this file when every task is DONE.

## Decided while building, worth keeping

**Only the months that HOLD something get a panel.** 18 of the 68 do. Rendering
all 68 would put roughly 2,400 empty day cells into a page that already runs
333KB, to say nothing. The rail still shows all 68, because the rail is where
the gaps are the point.

**No script is required to read it.** Every panel is in the page and visible;
the script's whole job is to show one at a time and wire the rail. With
JavaScript off the reader gets the record grouped by month, which is already
better than the flat list this replaces. Nothing is behind a click that is not
also in the document.

**One markup, two readings.** The day grid and the phone list are the same
cells: `grid-template-columns:repeat(7,1fr)` wide, `display:block` narrow with
the empty days hidden. A 7 column grid of text at 390px does not work, and a
second markup for phones is a second thing to keep true.
