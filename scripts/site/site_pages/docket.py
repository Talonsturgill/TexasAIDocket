"""Docket, topic, item, and place page renderers."""
from __future__ import annotations

from site_context import (
    LICENCE, SCHEMA_CTX, SITE_NAME, SITE_URL, _dt, _place_facts, _place_slug,
    all_places, calendar, claims_html, clock, dcal, dk, e, item_meta,
    numeral_lint, ordinal, page, rel, schema, short_date, texas_map, topic_label,
)
from site_pages.watch import ask_box, county_links

def docket_index(items: list, today: str) -> tuple:
    """The record, twice: by when you can act, and by when it happens.

    Returns (html, the numerals it prints). The calendar computes counts, day numbers and years
    that no other page authorises, and a set built where the figures are computed is the only
    arrangement in which the shown number and the allowed number cannot disagree.
    """
    def key(it):
        st = dk.window_state(it, today)
        if st == "open":
            return (0, (_dt.date.fromisoformat(it["public_access"]["closes"])
                        - _dt.date.fromisoformat(today)).days)
        return ({"open_meeting": 1, "contact_only": 2, "closed": 3}
                .get(it["public_access"]["room"], 2), 0)

    rows = "".join(
        f'<li>{clock(it, today)}<h3><a href="../item/{e(it["id"])}/">{e(it["title"])}</a></h3>'
        f'{item_meta(it, today)}</li>'
        for it in sorted(items, key=key))

    a = numeral_lint.Authorised()
    n_open = sum(1 for i in items if dk.window_state(i, today) == "open")
    tx = _place_facts()
    proj = dk.project(items, today)
    n_state = sum(1 for i in items if (i.get("geography") or {}).get("statewide"))
    by = {}
    for it in items:
        for c in (it.get("geography") or {}).get("counties") or []:
            by.setdefault(c, []).append(it)
    lit = set(by)
    crows = "".join(
        f'<tr><td><a href="../place/county-{_place_slug(c)}/">{e(c)} County</a></td>'
        f'<td class="n num">{len(v)}</td>'
        # SEPARATED BY A MIDDOT, NOT A COMMA, because one of the labels contains a comma.
        # These were raw slugs, which read like a database, and `topic_label` is the one place
        # a slug becomes English. `land-water-and-permitting` becomes "Land, water and
        # permitting", correctly, and a comma-joined list of it beside another topic reads as
        # four things. The separator has to be something no label can contain.
        f'<td>{" · ".join(e(topic_label(t)) for t in dict.fromkeys(i["topic"] for i in v))}</td>'
        f'</tr>'
        for c, v in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])))
    mrows = "".join(
        f'<tr><td><a href="../place/{e(mid)}/">{e(m["name"])}</a></td>'
        f'<td class="n num">{len(m["items"])}</td>'
        f'<td class="n num">{len(m["touched_counties"])}</td>'
        f'<td>{e(m["area_type"])}</td></tr>'
        for mid, m in sorted(proj["by_metro"].items(),
                             key=lambda kv: (-len(kv[1]["items"]), kv[0])))
    topics = topic_chips(items, depth=1)

    body = f"""
<h1>The record</h1>
<div class="prose">
  <p><span class="num">{n_open}</span> of
  <span class="num">{len(items)}</span> are open to comment now.</p>
</div>
{topics}

<!-- THE SAME ASK BOX AS THE FRONT PAGE, above the map because a reader who arrives on the
     record wanting an answer should not have to go back to the home page to find the field.
     base="../" so the answer's citation links resolve from one level deep; every other
     endpoint it uses is absolute. -->
{ask_box(items, today, base="../")}

<!-- THE MAP LIVES ON THE RECORD NOW, because geography is a property of the record rather
     than a subject of its own. It had a tab, and a tab is a promise that a reader wants to
     browse Texas by county, which is not what anybody arrives wanting. Clicking a lit county
     still opens what that county holds. -->
{texas_map.render(lit=lit, links=county_links(items, today, 1),
                  counts=proj["by_county"])}
<p class="mapread" id="mapread" role="status" aria-live="polite" data-prose="data"></p>
  <button type="button" class="mapreset" id="mapreset" hidden>Show all of Texas</button>
<p class="meta" data-prose="data">Click a lit county to see what it holds.
  <span class="num">{len(lit)}</span> of <span class="num">{tx["counties"]}</span> counties
  are named, and <span class="num">{n_state}</span> decisions apply statewide.</p>

<!-- FOLDED, NOT DELETED. The two tables are the complete geographic answer and they are also
     forty rows, which is most of a screen a reader did not ask for. `details` costs nothing,
     needs no script, and is open to a keyboard and a screen reader by default. -->
<details class="fold">
  <summary>Every county and area, listed</summary>
  <table class="tally"><thead><tr><th>County</th><th class="n">Items</th>
    <th>Topics</th></tr></thead><tbody>{crows}</tbody></table>
  <h3>By metropolitan area</h3>
  <table class="tally"><thead><tr><th>Area</th><th class="n">Items</th>
    <th class="n">Counties</th><th>Kind</th></tr></thead><tbody>{mrows}</tbody></table>
</details>

{docket_calendar_section(items, today, 1, a, rows)}

"""
    return page(title=f"The record · {SITE_NAME}", depth=1, active="record/",
                extra_css="record.css",
                desc="Every AI decision on the Texas record, ordered by how soon you can act.",
                body=body, today=today, canonical="record/",
                # The page that IS the dataset carries its node, which is where a crawler
                # following `isPartOf` from any decision expects to arrive.
                extra_ld=[{"@context": "https://schema.org",
                           **schema.dataset_node(SCHEMA_CTX, items, today)},
                          schema.collection_node(
                              SCHEMA_CTX, name="The record", path="record/",
                              description="Every tracked decision about artificial "
                                          "intelligence in Texas.", count=len(items)),
                          schema.breadcrumbs(SCHEMA_CTX,
                                             [(SITE_NAME, ""), ("The record", "record/")])]), a.set


# --------------------------------------------------------------------------- the calendar
# THE SCRIPT IS KEPT OUT OF THE f-STRING, same reason _SCAN_JS is: every brace below would
# have to be doubled to survive one, and a doubled brace is a typo waiting to happen.
#
# WHAT IT DOES AND WHAT IT IS NOT NEEDED FOR. Every month panel is in the document and visible
# without it, so a reader with no JavaScript gets the record grouped by month, which is already
# better than the flat list this replaces. The rail entries are real anchors and jump to their
# month. All this adds is showing one month at a time, which is a convenience and not the
# content.
_CAL_JS = """
  <script>
  (function () {
    var cal = document.getElementById('cal');
    if (!cal) return;
    var panels = [].slice.call(cal.querySelectorAll('.calmonth'));
    if (!panels.length) return;
    var order = panels.map(function (p) { return p.getAttribute('data-month'); });
    var home = cal.getAttribute('data-open');

    // The class is added by script, so the one-at-a-time CSS only ever applies where the
    // script that drives it is running. Without this the no-script reader gets one month and
    // no way to reach the others.
    cal.classList.add('js');

    // TWO MONTHS AT ONCE, because a month is not the horizon anybody plans against. Standing
    // in the last week of August, a single-month view has already run out, and the comment
    // window that closes on the 4th of September is off the end of the page. Sixty days is
    // the owner's number and it is the right one.
    //
    // The pair is the month you are on and whatever the record holds NEXT, which is not
    // always the next month on the wall. A month with nothing in it has no panel at all, and
    // drawing an empty grid to keep the sequence tidy would spend half the view saying
    // nothing. Both months name themselves in full, so there is nothing to misread.
    function show(key, focus) {
      var i = order.indexOf(key);
      if (i < 0) return false;
      panels.forEach(function (p, n) {
        var slot = n === i ? 'now' : (n === i + 1 ? 'next' : '');
        p.hidden = !slot;
        if (slot) p.setAttribute('data-slot', slot);
        else p.removeAttribute('data-slot');
      });
      // THE TWO VIEWS AGREE ABOUT WHERE YOU ARE. Reading June and then switching to the year
      // should land on June's year, not on wherever the rail was left.
      showYear(key.slice(0, 4));
      if (focus) {
        var h = cal.querySelector('.calmonth[data-slot="now"] .calmh');
        if (h) {
          // FOCUS WITHOUT THE JUMP, THEN SCROLL DELIBERATELY. Moving focus to the new heading
          // is what tells a screen reader the view changed, and a bare focus() also scrolls,
          // by whatever distance the browser decides. Measured, that was the difference
          // between a 37ms switch and a 269ms one: not work, just a long smooth scroll to a
          // month the reader could already see. `nearest` moves only if it has to.
          h.setAttribute('tabindex', '-1');
          h.focus({ preventScroll: true });
          h.scrollIntoView({ block: 'nearest' });
        }
      }
      return true;
    }

    // ONE YEAR AT A TIME. Six years of twelve small calendars is 72 grids in a column, which
    // is a scroll rather than a view; the owner asked for one year with a way to reach the
    // others and that is the whole of it.
    //
    // NO NUMERAL IS INVENTED HERE. The year and its count are lifted out of the year block's
    // own markup, which the build wrote out of the ledger and the numeral gate has already
    // passed. Script moves published numbers around; it never authors one.
    var yblocks = [].slice.call(cal.querySelectorAll('.calyr'));
    var yorder = yblocks.map(function (s) { return s.getAttribute('data-year'); });
    var yprev = document.getElementById('calyprev');
    var ynext = document.getElementById('calynext');
    var ylabel = document.getElementById('calyeart');
    var ycount = document.getElementById('calyearn');

    function showYear(y) {
      var i = yorder.indexOf(String(y));
      if (i < 0) return false;
      yblocks.forEach(function (s, n) { s.hidden = n !== i; });
      ylabel.setAttribute('datetime', yorder[i]);
      ylabel.textContent = yorder[i];
      var n = yblocks[i].querySelector('.calyn .num');
      ycount.textContent = n ? n.textContent.trim() : '';
      yprev.disabled = i <= 0;
      ynext.disabled = i >= yorder.length - 1;
      return true;
    }
    function stepYear(by) {
      var i = yorder.indexOf(ylabel.textContent) + by;
      if (i < 0 || i >= yorder.length) return;
      showYear(yorder[i]);
    }
    yprev.addEventListener('click', function () { stepYear(-1); });
    ynext.addEventListener('click', function () { stepYear(1); });

    // A LINK SHARED INTO THE MONTH STILL LANDS THERE. Somebody who was handed
    // /record/#cal-2026-06 gets June, not August, and the back button keeps working.
    function fromHash() {
      var m = (location.hash || '').match(/^#cal-(\d{4}-\d{2})$/);
      return m ? m[1] : null;
    }
    window.addEventListener('hashchange', function () {
      var k = fromHash(); if (k) show(k, true);
    });
    // THE STEPPER. Months with nothing in them have no panel, so stepping walks the months
    // that exist rather than the calendar's, and it stops at the ends instead of wrapping.
    // Wrapping off the end lands a reader years away with no way back using the button they
    // just pressed. It moves ONE month, not two: the pair is a window sliding over the
    // record, not a book being turned two leaves at a time.
    var prev = document.getElementById('calprev');
    var next = document.getElementById('calnext');
    var now = document.getElementById('calnow');

    function at() {
      var shown = cal.querySelector('.calmonth[data-slot="now"]');
      return shown ? order.indexOf(shown.getAttribute('data-month')) : order.indexOf(home);
    }
    function step(by) {
      var i = at() + by;
      if (i < 0 || i >= order.length) return;
      show(order[i], true);
      history.replaceState(null, '', '#cal-' + order[i]);
      edges();
    }
    function edges() {
      var i = at();
      prev.disabled = i <= 0;
      next.disabled = i >= order.length - 1;
      now.disabled = order[i] === home;
    }
    prev.addEventListener('click', function () { step(-1); });
    next.addEventListener('click', function () { step(1); });
    now.addEventListener('click', function () {
      show(home, true); history.replaceState(null, '', '#cal-' + home); edges();
    });

    // ONLY WHAT CAN STILL BE ACTED ON. Most of a record is history by definition, and a
    // reader who came to find out whether they can still say something should not have to
    // read the history to find out. The hiding is CSS, so nothing is removed from the
    // document and turning it back off costs no work.
    var acts = document.getElementById('calacts');
    acts.addEventListener('change', function () {
      cal.classList.toggle('acts', acts.checked);
    });

    // THREE VIEWS. Month is the default and is what a wall calendar is; year is twelve of
    // them at a glance; list is the record in one column by urgency. Different readers want
    // different things, which is the whole reason a view switcher exists.
    var views = { month: 'calvm', year: 'calvy', list: 'calvl' };
    var page = document.querySelector('.calpage');

    function view(which) {
      cal.setAttribute('data-view', which);
      Object.keys(views).forEach(function (k) {
        document.getElementById(views[k]).setAttribute('aria-pressed',
          k === which ? 'true' : 'false');
      });
      // PAGING BELONGS TO THE MONTH. Leaving prev and next sitting there in a view they cannot
      // move is the same broken promise as a button that does nothing.
      if (page) page.hidden = which !== 'month';
    }
    Object.keys(views).forEach(function (k) {
      document.getElementById(views[k]).addEventListener('click', function () { view(k); });
    });

    // PICKING A MONTH OUT OF THE YEAR MEANS "SHOW ME THAT MONTH", so it hands the reader to
    // the month view rather than leaving them on the grid they just used.
    [].slice.call(cal.querySelectorAll('a.mini.has')).forEach(function (a) {
      a.addEventListener('click', function (ev) {
        if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.altKey || ev.button) return;
        ev.preventDefault();
        view('month');
        if (show(a.getAttribute('data-month'), true)) {
          history.replaceState(null, '', a.getAttribute('href'));
        }
        edges();
      });
    });

    view('month');
    show(fromHash() || home, false);
    edges();
  })();
  </script>
"""


def docket_calendar_section(items: list, today: str, depth: int, a, rows: str) -> str:
    """The record laid out by WHEN, which is the half a list sorted by urgency cannot show.

    An item with a hearing in June and an order in August belongs in both months. A flat list
    can only put it under one, so the second date is invisible, and it is often the one a
    reader is looking for.

    `rows` is the record as list items, already sorted by urgency by the caller. The LIST
    view is that same markup: one view of three rather than a separate fold below, because a
    reader choosing "list" has chosen it and should not then have to open a disclosure.

    `a` is the page's `Authorised` set. Every figure here is added to it as it is computed,
    which is what makes the numeral law a mechanism rather than a promise.
    """
    cal = dcal.summarise(items, today)
    keys, months, cur = cal["month_keys"], cal["by_month"], cal["current"]
    if not keys:
        return ""

    a.add(cal["n_events"], cal["n_live"], len(items))
    # Every day of the month a grid can print, and every year the rail can show.
    a.add(*range(1, 32))
    # ONLY THE YEARS THAT HOLD SOMETHING. This drew every year from the first event to the
    # last, so three entirely empty rows sat in the middle saying nothing at length. The
    # argument for keeping them was that a gap is information, and it is, but three identical
    # rows of greyed months is a worse way to say "nothing happened" than not drawing them:
    # the years are labelled, so a reader sees 2021 followed by 2025 and the gap is plain.
    years = sorted({int(k[:4]) for k in keys if months.get(k)})
    a.add(*years)
    for k in keys:
        a.add(len(months.get(k, [])))

    # ------------------------------------------------------ the year, as twelve calendars
    # THREE VIEWS, because different readers want different things and the owner asked for the
    # choice. The MONTH is the default and the one a wall calendar is: one month, paged. The
    # YEAR is twelve small calendars, which is the same object at a different scale and reads
    # the shape of the record at a glance. The LIST is the record in one column, by urgency,
    # for somebody who wants to scan rather than to browse.
    #
    # Only the years that hold anything are drawn. Three empty rows saying nothing at length
    # was the first version and the owner was right that it was stupid to include.
    yblocks = []
    year_live = {}
    for y in years:
        minis = []
        for m in range(1, 13):
            k = f"{y:04d}-{m:02d}"
            n = len(months.get(k, []))
            days = dcal.by_day(months.get(k, []))
            cells = []
            for week in dcal.weeks(k):
                for d in week:
                    if d is None:
                        cells.append('<i class="mo"></i>')
                        continue
                    iso = d.isoformat()
                    mine = days.get(iso) or []
                    cls = ""
                    if mine:
                        cls = " mh act" if any(x["actionable"] for x in mine) else " mh"
                    if iso == today:
                        cls += " mt"
                    cells.append(f'<i class="{cls.strip() or "md"}">{d.day}</i>')
            head = "".join(f"<i>{w}</i>" for w in ("S", "M", "T", "W", "T", "F", "S"))
            inner = (f'<b class="minm"><time datetime="{k}">{e(dcal.month_short(k))}</time></b>'
                     f'<span class="minc num">{n}</span>'
                     f'<span class="minh">{head}</span>'
                     f'<span class="ming">{"".join(cells)}</span>')
            act_n = sum(1 for ev in months.get(k, []) if ev["actionable"])
            if n:
                minis.append(f'<li><a class="mini has{" hasact" if act_n else ""}" '
                             f'href="#cal-{k}" data-month="{k}" '
                             f'aria-label="{e(dcal.month_label(k))}, {n} dated">{inner}</a></li>')
            else:
                minis.append(f'<li><span class="mini none">{inner}</span></li>')
        live = sum(len(months.get(f"{y:04d}-{m:02d}", [])) for m in range(1, 13))
        year_live[y] = live
        a.add(live, y)
        yblocks.append(
            f'<section class="calyr" data-year="{y}" aria-label="{y}">'
            f'<h3 class="calyh"><time datetime="{y}"><span class="num">{y}</span></time>'
            f'<span class="calyn"><span class="num">{live}</span> dated</span></h3>'
            f'<ol class="minis">{"".join(minis)}</ol></section>')

    # ------------------------------------------------------------------ the panels
    panels = []
    for k in keys:
        evs = months.get(k)
        if not evs:
            continue                      # 50 empty grids would say nothing, at length
        days = dcal.by_day(evs)
        cells = []
        for week in dcal.weeks(k):
            for d in week:
                if d is None:
                    cells.append('<li class="calday out" aria-hidden="true"></li>')
                    continue
                iso = d.isoformat()
                mine = days.get(iso) or []
                klass = " today" if iso == today else ""
                if not mine:
                    cells.append(
                        f'<li class="calday{klass}"><b class="caldn num">{d.day}</b></li>')
                    continue
                if any(ev["actionable"] for ev in mine):
                    klass += " hasact"
                evl = "".join(
                    f'<li><a class="calev{" act" if ev["actionable"] else ""}" '
                    f'href="{rel(depth)}item/{e(ev["item_id"])}/">'
                    f'<span class="cke">{e(dcal.kind_label(ev["kind"]))}</span>'
                    f'<span class="ckt">{e(ev["title"])}</span></a></li>'
                    for ev in mine)
                cells.append(
                    f'<li class="calday full{klass}"><b class="caldn num">{d.day}</b>'
                    f'<time class="caldd" datetime="{iso}">{e(ordinal(d))}</time>'
                    f'<ul class="calevs">{evl}</ul></li>')
        n = len(evs)
        act = sum(1 for ev in evs if ev["actionable"])
        a.add(n, act)
        # "1 dated" is not a sentence. The count decides the noun, computed rather than typed.
        word = "date" if n == 1 else "dates"
        acts = (f' <span class="calact"><span class="num">{act}</span> you can still act on</span>'
                if act else "")
        panels.append(
            f'<section class="calmonth" id="cal-{k}" data-month="{k}" data-act="{act}" '
            f'aria-label="{e(dcal.month_label(k))}">'
            f'<h3 class="calmh"><time datetime="{k}">'
            f'<span class="calmnum num">{k[5:7]}</span>'
            f'<span class="calmname">{e(calendar.month_name[int(k[5:7])])}</span>'
            f'<span class="calmyear num">{k[:4]}</span></time></h3>'
            f'<p class="calmsum" data-prose="data"><span class="num">{n}</span> {word}{acts}</p>'
            f'<ol class="calhead" aria-hidden="true">'
            + "".join(f"<li>{d}</li>" for d in ("Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"))
            + f'</ol><ol class="caldays">{"".join(cells)}</ol></section>')

    # The bar opens on the landing month's year and says what that year holds. It reads the
    # count the year block was drawn with rather than summing it again, so the two cannot
    # disagree: a second copy of an arithmetic is how a heading and the thing it heads drift.
    yhead = year_live[int(cur[:4])]

    # "1 older than that ARE in the list" is not a sentence. The count picks the verb, computed
    # rather than typed, the same way the month panel's own noun is.
    older = (f' <span class="num">{cal["older"]}</span> older than that '
             f'{"is" if cal["older"] == 1 else "are"} in the list.'
             if cal["older"] else "")
    a.add(cal["older"])
    dropped = (f'<p class="meta"><span class="num">{cal["dropped"]}</span> dated entries could '
               f'not be read and are not shown.</p>' if cal["dropped"] else "")
    a.add(cal["dropped"])

    return f"""
<section class="cal" id="cal" data-open="{cur}">
  <h2>When it happens</h2>
  <p class="sub"><span class="num">{cal["n_events"]}</span> dated moments across
  <span class="num">{cal["n_live"]}</span> months.{older}</p>
  <!-- DATA, NOT PROSE, and marked as such the way the county tally already is. The rail is a
       row of month labels and counts, so with the tags stripped it reads as "May  10" and the
       house style checker calls that a badly written date. It is not a sentence; it is a
       chart's axis. `data-prose="data"` is the mechanism this project already has for that,
       and it narrows the prose rules rather than switching a checker off. -->
  <!-- EVERY CONTROL IS HIDDEN UNTIL THE SCRIPT CLAIMS IT. A button that does nothing is worse
       than no button: it is a promise a reader tests once and then distrusts the page for.
       Without script every month is already on the page and the rail entries are real anchors,
       so nothing here is the only route to anything.

       THE MONTH IS THE DEFAULT VIEW and the year is the other one. A reader arriving at a
       record wants what is happening, not a chart of the last six years, and the year rail is
       for finding your way rather than for reading. -->
  <!-- LAID OUT THE WAY NOTION LAYS OUT A DATABASE, because the owner asked me to look at it
       and it is right: the VIEW SWITCHER is tabs at the top left, next to the thing being
       viewed, and the controls that act on the current view sit at the top right. I had it
       mirrored, with the paging on the left and the view choice in a pill on the right, which
       reads as two unrelated widgets rather than one toolbar.

       The tabs are underlined text rather than a segmented pill, which is also what this
       site's own masthead nav already does for the page you are on. One idiom, twice. -->
  <div class="caltoolbar">
    <div class="caltabs" role="group" aria-label="How to see the record">
      <button type="button" id="calvm" class="caltab" aria-pressed="true">Month</button>
      <button type="button" id="calvy" class="caltab" aria-pressed="false">Year</button>
      <button type="button" id="calvl" class="caltab" aria-pressed="false">List</button>
    </div>
    <div class="calctl">
      <!-- THE READER'S OWN WORDS, declared as such. Published copy carries no I, we or our,
           because the record speaks rather than its author; a control the reader operates is
           the one place a first person is right. -->
      <label class="calswitch" data-voice="reader">
        <input type="checkbox" id="calacts">
        <span class="calswtrack" aria-hidden="true"><span class="calswknob"></span></span>
        <span class="calswlabel">Only what I can still act on</span>
      </label>
      <span class="calpage">
        <button type="button" id="calprev" class="calarrow" aria-label="The month before">
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 4 7 12l8 8"/></svg>
        </button>
        <button type="button" id="calnext" class="calarrow" aria-label="The month after">
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 4l8 8-8 8"/></svg>
        </button>
        <button type="button" id="calnow" class="calpill">Today</button>
      </span>
    </div>
  </div>
  <!-- ONE YEAR, AND A WAY TO THE OTHERS. The bar is the year view's own heading once script is
       running, which is why each year block's heading goes away under `.cal.js`: saying 2026
       twice, once in the bar and once four pixels below it, is what a page looks like when
       nobody read it back. Without script the bar is hidden and every year keeps its own
       heading, so the same document reads correctly either way.

       The year and the count in it are LIFTED from the year block the build wrote, never
       composed here. A numeral typed into a template is a numeral nothing can keep true. -->
  <div class="calrail" data-prose="data">
    <div class="calyearbar">
      <button type="button" id="calyprev" class="calarrow" aria-label="The year before">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M15 4 7 12l8 8"/></svg>
      </button>
      <b class="calyearnow" aria-live="polite">
        <time class="calyeart num" id="calyeart" datetime="{cur[:4]}">{cur[:4]}</time>
        <span class="calyearn"><span class="num" id="calyearn">{yhead}</span> dated</span>
      </b>
      <button type="button" id="calynext" class="calarrow" aria-label="The year after">
        <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M9 4l8 8-8 8"/></svg>
      </button>
    </div>
    {"".join(yblocks)}
  </div>
  <div class="calpanels" data-prose="data">{"".join(panels)}</div>
  <ul class="callist items" data-prose="data">{rows}</ul>
  {dropped}
</section>
{_CAL_JS}"""




def topic_chips(items: list, depth: int, current: str = "") -> str:
    """The record's filter row: one pill per topic, carrying its share of the record.

    THE COUNT IS THE HIERARCHY. Five identical boxes say every topic is the same size, and
    on this record they are not: one beat can hold half the decisions while another holds
    one. A reader deciding where to look is asking exactly that question, so the row answers
    it before they click. Every count here is `len()` of a filtered list, which is what the
    compute-not-generate law requires of a published numeral.
    """
    by: dict = {}
    for it in items:
        by.setdefault(it["topic"], []).append(it)
    up = "../" * depth
    out = []
    for t in sorted(by):
        # `aria-current` and not a class, because the state is "this is the page you are on"
        # and that is a thing assistive technology already knows how to say.
        here = ' aria-current="page"' if t == current else ""
        out.append(
            f'<a class="topicchip" href="{up}topic/{e(t)}/"{here}>'
            f'<span class="tc-name">{e(topic_label(t))}</span>'
            f'<span class="tc-n num">{len(by[t])}</span></a>')
    return ('<nav class="topicrow" data-prose="data" aria-label="Filter the record by topic">'
            + "".join(out) + "</nav>")


def topic_page(topic: str, items: list, today: str) -> str:
    mine = [i for i in items if i["topic"] == topic]
    rows = "".join(
        f'<li>{clock(it, today)}<h3><a href="../../item/{e(it["id"])}/">{e(it["title"])}</a></h3>'
        f'{item_meta(it, today)}</li>' for it in mine)
    body = f"""
<h1>{e(topic_label(topic))}</h1>
<div class="prose"><p><span class="num">{len(mine)}</span> of
<span class="num">{len(items)}</span> decisions on the record.</p></div>
{topic_chips(items, depth=2, current=topic)}
<ul class="items" data-prose="data">{rows}</ul>
<p class="meta" data-prose="data"><a href="../../record/">All decisions</a> ·
<a href="../">All beats</a></p>
"""
    return page(
        title=f"{topic_label(topic)} · {SITE_NAME}", depth=2, active="record/",
        # THE DESCRIPTION SAYS WHAT THE BEAT IS, not what the URL is. It read "Texas AI
        # decisions filed under data centers", which is the slug with spaces in it and tells a
        # reader in a result list nothing they did not already know from the title. The blurb
        # is the line written to describe this beat, so it is the line that belongs here.
        desc=f"{topic_blurb(topic)} Tracked on the Texas AI Docket.",
        body=body, today=today, canonical=f"topic/{topic}/",
        extra_ld=[
            schema.collection_node(
                SCHEMA_CTX, name=topic_label(topic), path=f"topic/{topic}/",
                description=topic_blurb(topic), count=len(mine),
                elements=[(i["title"], f'item/{i["id"]}/') for i in mine]),
            schema.breadcrumbs(SCHEMA_CTX, [(SITE_NAME, ""), ("The beats", "topic/"),
                                            (topic_label(topic), f"topic/{topic}/")]),
        ])


# ---------------------------------------------------------------- the beats, and their hub

# WHY A BLURB IS DATA RATHER THAN A SENTENCE INSIDE A TEMPLATE.
#
# Two surfaces publish it, the hub at /topic/ and the front page's covers grid, and a line
# written into either template is the same sentence typed twice, which is how a heading and a
# description drift apart. It sits beside `topic_label` because both turn a filing slug into
# something a reader was meant to read, and both are the only place that happens.
#
# THESE ARE THE ONE PLACE THIS SITE DESCRIBES A BEAT RATHER THAN COUNTING IT. A hub whose
# cards carry a name and a number is a directory listing, and a directory listing is thin to a
# reader deciding where to look and thin to a crawler deciding whether the page is about
# anything. The blurb is what makes /topic/ a page about Texas AI decisions instead of a page
# about eight links.
TOPIC_BLURBS = {
    "data-centers":
        "Where the buildings go and who signs off on them. Zoning votes. Tax abatements. "
        "Moratoriums county by county.",
    "power-and-the-grid":
        "The load these projects add and the rules written around it. Interconnection. "
        "Curtailment. Who pays for the wires.",
    "state-policy":
        "Bills and agency rules that set what AI may do in Texas. Statewide directives and "
        "who answers for them.",
    "land-water-and-permitting":
        "The acreage and the water a project needs before anything is built. Groundwater "
        "districts. Plats. The permits that gate them.",
    "defense-and-federal":
        "Federal agencies and installations making AI decisions on Texas ground. Base "
        "contracts and national programs sited here.",
    "research-and-science":
        "University labs and state research money. The institutions building these systems "
        "rather than buying them.",
    "health-and-education":
        "AI reaching patients and students. What hospital systems and school districts allow "
        "in clinical and classroom use.",
    "surveillance-and-policing":
        "Cameras and plate readers in the hands of Texas agencies. The predictive tools "
        "beside them and the oversight attached to each.",
    "ai-in-the-field":
        "AI already at work on Texas ground. Oilfields and farms, freight lanes and plant "
        "floors, and who is doing the job differently now.",
}


def topic_blurb(topic: str) -> str:
    """One line on what a beat covers, shared by the hub and the front page.

    IT FAILS THE BUILD RATHER THAN FALLING BACK TO EMPTY. A missing blurb rendered as an
    empty string publishes a card with a heading and nothing under it, which reads as a beat
    nobody has filed against yet rather than as a build fault, and it would ship. Admitting a
    new topic to the ledger is therefore deliberately a two file change.
    """
    try:
        return TOPIC_BLURBS[topic]
    except KeyError:
        raise SystemExit(
            f"site_build: topic {topic!r} has no blurb. Every beat the ledger admits needs one "
            f"line in TOPIC_BLURBS saying what it covers, because /topic/ and the front page "
            f"both publish it and neither has anywhere else to get it.")


def _open_now(subset: list, today: str) -> int:
    """How many of these decisions a Texan can still comment on TODAY. Computed, never typed.

    IT ASKS `window_state` RATHER THAN READING THE ROOM, and the first draft of this did read
    the room, which was wrong in a way that would have shipped a false claim on the two most
    visible pages on the site.

    `public_access.room` records what KIND of access a decision has, not whether that access is
    still available. Counting `open_meeting` as open put "18 still open to the public" on the
    data centers card while one of those meetings had closed five days earlier. The room is a
    fact about the decision. Whether the door is open is arithmetic against today, which is
    exactly what `window_state` exists to do and what the item pages already trust.

    THERE IS ONE DEFINITION OF OPEN ON THIS SITE and this is not allowed to be a second one. A
    broader count would read better and would mean something no other page means, which is how
    two surfaces start disagreeing about the same record.
    """
    return sum(1 for i in subset if dk.window_state(i, today) == "open")


def topics_index(items: list, today: str) -> tuple:
    """The hub for /topic/. Returns (numerals it prints, html).

    WHY THIS PAGE HAD TO EXIST. Eight topic pages shipped with no index above them and
    nothing on the site linking to one, so the only routes in were the chip row on a page a
    reader had already found and the sitemap. A page family reachable only sideways is
    crawled slowly and understood as a set of strangers rather than as a structure, and it
    gets worse every time the record grows, which is the direction this record only goes.

    IT RETURNS ITS OWN NUMERALS, the pattern the questions and sources pages already use, so
    the figures it prints and the figures it is authorised to print come out of the same
    call and cannot drift.
    """
    by: dict = {}
    for it in items:
        by.setdefault(it["topic"], []).append(it)

    a = numeral_lint.Authorised()
    a.add(len(items), len(by))

    cards = []
    for t in sorted(by):
        mine = by[t]
        openn = _open_now(mine, today)
        a.add(len(mine), openn)
        # THE OPEN COUNT IS PRINTED ONLY WHEN THERE IS ONE. "0 still open" is a true sentence
        # that reads as a dead beat, and most beats are closed most of the time because that
        # is what a record of decided things looks like.
        still = (f'<span class="cv-open">{openn} still open to comment</span>'
                 if openn else "")
        cards.append(
            f'<li class="cv-card"><a href="{e(t)}/"><h2>{e(topic_label(t))}</h2></a>'
            f'<p class="cv-blurb">{e(topic_blurb(t))}</p>'
            f'<p class="cv-foot" data-prose="data">'
            f'<span class="num">{len(mine)}</span> '
            f'{"decision" if len(mine) == 1 else "decisions"}{still}</p></li>')

    body = f"""
<h1>The beats</h1>
<div class="prose"><p>Every decision on this record is filed under one of these
<span class="num">{len(by)}</span> beats. Each keeps its own page whether or not it moved this
week. Each names the decisions on it and who decided them. Each says whether a Texan still has
a way in.</p>
</div>
<ul class="covers">{"".join(cards)}</ul>
<p class="meta" data-prose="data"><a href="../record/">All
<span class="num">{len(items)}</span> decisions</a> ·
<a href="../place/">Browse by place</a></p>
"""
    html = page(
        title=f"The beats · {SITE_NAME}", depth=1, active="record/",
        desc=("The beats the Texas AI Docket tracks, from data centers and the ERCOT grid to "
              "land, water and permitting. Every AI decision in Texas, filed and sourced."),
        body=body, today=today, canonical="topic/",
        extra_ld=[
            schema.collection_node(
                SCHEMA_CTX, name="The beats", path="topic/",
                description="Every beat the Texas AI Docket files decisions under.",
                count=len(by),
                elements=[(topic_label(t), f"topic/{t}/") for t in sorted(by)]),
            schema.breadcrumbs(SCHEMA_CTX, [(SITE_NAME, ""), ("The record", "record/"),
                                            ("The beats", "topic/")]),
        ])
    return a.set, html


def covers_section(items: list, today: str) -> tuple:
    """The front page's index of the record. Returns (numerals it prints, html).

    DENSER THAN THE CARD WALL IT IS MODELLED ON, and carrying more. The reference version of
    this pattern is a column of full width cards of name, count and blurb, which spends most of
    a screen on eight facts. This is one row per beat in a grid that runs two and three wide,
    and each row carries the name, the count, the blurb and whether anything on that beat is
    still open, which is one more fact per beat in roughly a third of the height.

    THE BLURB IS THE SAME STRING THE HUB PUBLISHES, by construction. Two surfaces describing
    the same eight beats in two sets of words is how a site starts contradicting itself.

    It is a SECOND route to the same pages rather than a decoration. The beats were reachable
    from the chip row on the record page and from nowhere else a reader lands first, and the
    front page is where nearly everybody lands first.
    """
    by: dict = {}
    for it in items:
        by.setdefault(it["topic"], []).append(it)

    a = numeral_lint.Authorised()
    a.add(len(items), len(by))

    cards = []
    for t in sorted(by, key=lambda k: (-len(by[k]), k)):
        mine = by[t]
        openn = _open_now(mine, today)
        a.add(len(mine), openn)
        still = (f'<span class="cv-open">{openn} open to comment</span>' if openn else "")
        cards.append(
            f'<li class="cv-card"><a href="topic/{e(t)}/"><h3>{e(topic_label(t))}</h3></a>'
            f'<p class="cv-blurb">{e(topic_blurb(t))}</p>'
            f'<p class="cv-foot" data-prose="data"><span class="num">{len(mine)}</span> '
            f'{"decision" if len(mine) == 1 else "decisions"}{still}</p></li>')

    html = f"""<section data-reveal>
  <h2><a href="topic/">What this record covers</a></h2>
  <div class="prose"><p>Every decision is filed under one of
  <span class="num">{len(by)}</span> beats. Each keeps its own page whether or not it moved
  this week.</p></div>
  <ul class="covers front">{"".join(cards)}</ul>
  <p class="meta" data-prose="data"><a href="topic/">All beats</a> ·
  <a href="place/">Browse by place</a> ·
  <a href="record/">All <span class="num">{len(items)}</span> decisions</a></p>
</section>"""
    return a.set, html


def _item_metros(it: dict) -> list:
    """The statistical areas an item's counties fall in, derived and never typed."""
    r = dk._resolver()
    if not r:
        return []
    out = {}
    for c in (it.get("geography") or {}).get("counties") or []:
        m = r.metro_of(c)
        if m:
            out[m["id"]] = m["full_name"]
    return [out[k] for k in sorted(out, key=lambda k: out[k])]


def item_where(it: dict) -> str:
    """The item's places, linked, so the record reads in both directions.

    THE PLACE PAGES LINKED TO ITEMS AND NOTHING LINKED BACK. A reader on the Abilene
    transmission item could not reach the Abilene page, could not see what else touches
    Shackelford, and had no way to discover that per place views exist at all. A one way
    link is half a cross reference and it is the half nobody notices is missing, because
    every page it points at looks correctly connected from where it sits.

    METROS AND LOOSE COUNTIES ARE BOTH NAMED, in that order, for the reason `M3` found:
    thirteen of this record's twenty-two counties are in no statistical area, including
    Shackelford, which is where the data center is. A metro-only line would read as
    complete while dropping the part of Texas the story is actually about.
    """
    g = it.get("geography") or {}
    counties = g.get("counties") or []
    if g.get("statewide"):
        return ('<p>Statewide. This decision applies across Texas rather than to a '
                'named county.</p>')
    if not counties:
        return ('<p class="gap">No county is named for this item yet. It appears on no '
                'place page and lights nothing on the map.</p>')

    r = dk._resolver()
    metros, loose = {}, []
    for c in counties:
        m = r.metro_of(c) if r else None
        if m:
            metros.setdefault(m["id"], m["name"])
        else:
            loose.append(c)

    def links(pairs):
        return ", ".join(f'<a href="../../place/{e(i)}/">{e(n)}</a>' for i, n in pairs)

    parts = [f'<p><span class="num">{len(counties)}</span> '
             f'{"county" if len(counties) == 1 else "counties"}.']
    if metros:
        parts.append(f' In {links(sorted(metros.items(), key=lambda kv: kv[1]))}.')
    if loose:
        parts.append(
            f' {"Also in" if metros else "In"} '
            f'{links((f"county-{_place_slug(c)}", c) for c in sorted(loose))}, which '
            f'{"is" if len(loose) == 1 else "are"} in no metropolitan or micropolitan area.')
    parts.append('</p>')
    return "".join(parts)


def item_timeline(it: dict, today: str) -> str:
    """The decision's dates as a strip, with today standing in its own place in the order.

    THIS REPLACED THE DATES TABLE RATHER THAN JOINING IT. Two renderings of one field is two
    things to keep in step, and the table's own failure was that it answered "what are the
    dates" while a reader arrives asking "has this happened yet". A table cannot answer the
    second question, because the answer is not in the data, it is in where the data sits
    relative to now. Putting today in the sequence is the whole idea. Everything above the
    marker has happened and everything below it has not, and no sentence has to say so.

    THE NEXT DATE IS THE ONE A READER CAME FOR, so it is named and counted. The count is
    computed here and authorised where the page's numerals are assembled, per the law that no
    published numeral is ever typed.

    `data-prose="data"` on the list, for the reason the deadline cards carry it. A date chip
    and a five word label are not running prose, and measuring comma density over a strip of
    them says nothing about whether the page breathes. It narrows DENSITY only. The
    construction rules still apply to every word in here, which is why the dates go in `<time>`
    elements that render their own value rather than as bare abbreviations.
    """
    ks = sorted((k for k in (it.get("key_dates") or []) if k.get("date")),
                key=lambda d: d["date"])
    if not ks:
        return ""
    t = _dt.date.fromisoformat(today)
    nxt = next((k for k in ks if _dt.date.fromisoformat(k["date"]) > t), None)

    rows, marked = [], False
    for k in ks:
        d = _dt.date.fromisoformat(k["date"])
        if d > t and not marked:
            rows.append('<li class="now"><span class="dot"></span>'
                        '<span class="lbl">Today</span></li>')
            marked = True
        when = ""
        if nxt is not None and k is nxt:
            out = (d - t).days
            when = f'<span class="out">{out} day{"" if out == 1 else "s"} out</span>'
        note = k.get("note") or ""
        note_html = f"<p>{e(note)}</p>" if note else ""
        rows.append(
            f'<li class="{"ahead" if d > t else "past"}"><span class="dot"></span>'
            f'<time datetime="{e(k["date"])}">{e(short_date(k["date"]))}</time>'
            f'<span class="lbl">{e(k["kind"].replace("_", " "))}</span>'
            f'{note_html}{when}</li>')
    if not marked:
        rows.append('<li class="now"><span class="dot"></span>'
                    '<span class="lbl">Today</span></li>')
    return ('<section><h2>Timeline</h2><ol class="tl" data-prose="data">'
            + "".join(rows) + "</ol></section>")


def item_page(it: dict, today: str) -> str:
    timeline = item_timeline(it, today)
    # HOW THIS DECISION MOVED. One dated line per check, oldest first, including the checks
    # where nothing moved. Added 2026-08-18 on the owner's call: the field already existed, the
    # routine only wrote to it on a change, and NOTHING RENDERED IT, so 57 of 61 items showed a
    # reader a wall of quotes and a single date. A record that is watched should look watched.
    moved = "".join(
        f'<li><span class="num">{e(h["date"])}</span><p>{e(h.get("note") or "")}</p></li>'
        for h in sorted((x for x in (it.get("history") or []) if isinstance(x, dict)),
                        key=lambda d: str(d.get("date", ""))))
    # ASSEMBLED HERE RATHER THAN INLINE, so an item with no log emits nothing at all. Written
    # inline the conditional left two blank lines behind on the 57 pages that have no history
    # yet, which is a byte change on 57 files for a section none of them carry. The site's
    # freshness check compares bytes, so noise like that turns a real diff into a haystack.
    moved_block = (
        '<section><h2>How this decision moved</h2><div class="prose"><p>One dated line per '
        'check, oldest first. A line that says nothing changed means somebody looked and it '
        f'had not.</p></div><ol class="moved">{moved}</ol></section>\n\n') if moved else ""

    # THE QUESTIONS, WHICH THIS SITE HAS BEEN ANSWERING FOR MACHINES ONLY.
    #
    # `schema.qa_pairs` has produced up to twelve answered questions per item for as long as it
    # has existed, every one assembled from named fields and arithmetic, and the item page has
    # shipped them in an invisible FAQPage node. A crawler could read them. The person the page
    # is for could not. That is the same defect as the movement log one section down, found the
    # same afternoon, and the fix is the same shape: render what is already produced.
    #
    # THE SAME CALL, not a second copy. The visible block and the structured data come out of
    # one function, so they can never answer one question two ways.
    #
    # THE SUBJECT IS DROPPED HERE AND ONLY HERE. Every frame reads "<title>. Who decides it?",
    # because those questions travel alone into a search result where nothing has named the
    # subject. On this page the h1 has just named it, so printing the headline twelve more times
    # would be noise. `shape_of` is what removes it, and it lives beside the frames for that
    # reason rather than being reversed out with a string replace here.
    # AND THE QUESTION IS THE CROSS LINK. The first draft put the hub's heading under each
    # question as a mono kicker, which is what the reference page does. Read back, every one of
    # them was the question again in capitals: "Who decides it?" over WHO DECIDES. The kicker
    # only carries information on a page where the question still names its subject, and this
    # page has just dropped that. So the question itself becomes the door to the same question
    # asked of the whole record, which is the cross link that section wanted and one line of
    # furniture less rather than one more.
    qa = schema.qa_pairs(SCHEMA_CTX, it, today)
    qa_slugs = {shape: slug for shape, slug, _head, _b in schema.QUESTION_KINDS}
    qa_rows = []
    for q, a in qa:
        shape = schema.shape_of(q, it["title"])
        # `data-prose="data"` on the one shape whose commas are delimiters, by the rule
        # `LIST_ANSWER_SHAPES` already states and `list_answer_ok` already proves. A county list
        # is not a writer leaning on commas and there is no way to split it into sentences.
        data = ' data-prose="data"' if shape in schema.LIST_ANSWER_SHAPES else ""
        slug = qa_slugs.get(shape)
        head = (f'<a href="../../questions/{e(slug)}/">{e(shape)}?</a>' if slug
                else f"{e(shape)}?")
        qa_rows.append(f'<div class="qa"><h3>{head}</h3><p{data}>{e(a)}</p></div>')
    qa_block = ('<section><h2>Questions about this decision</h2><div class="prose"><p>Answered '
                'from the record itself. Every answer is assembled from stored fields, so an '
                f'answer the record has no basis for is left out rather than guessed.</p></div>'
                f'{"".join(qa_rows)}</section>\n\n') if qa_rows else ""

    # CITE THIS, because a public record that is hard to cite gets paraphrased instead, and a
    # paraphrase is where the number goes wrong. One line a reader can copy whole, carrying the
    # publisher, the entry, the two dates that bound what is being cited, the canonical URL, the
    # licence and the item id that pulls the same entry out of the JSON.
    #
    # BOTH DATES OR NEITHER. "Last verified" alone invites a reader to date the decision to the
    # day somebody looked at it, and "tracked since" alone hides how stale the citation may be.
    # The pair is the honest interval and it is the thing a citation is actually asserting.
    #
    # `data-prose="data"` for the density measurement only. A citation is a row of fields with
    # separators, not a sentence that breathes, and the house cure for a comma is to split the
    # sentence at it, which would turn one copyable line into six.
    seen = sorted([k["date"] for k in (it.get("key_dates") or []) if k.get("date")]
                  + [h["date"] for h in (it.get("history") or [])
                     if isinstance(h, dict) and h.get("date")])
    since = (f'Tracked since {ordinal(_dt.date.fromisoformat(seen[0]))}, {seen[0][:4]}. '
             if seen else "")
    cite = (
        f'<section><h2>Cite this</h2><div class="prose"><p class="cite" data-prose="data">'
        f'{e(SITE_NAME)}, {e(it["title"])}. {since}'
        f'Last verified {e(ordinal(_dt.date.fromisoformat(it["last_verified"])))}, '
        f'{e(it["last_verified"][:4])}. '
        f'<a href="{SITE_URL}/item/{e(it["id"])}/">{SITE_URL}/item/{e(it["id"])}/</a>. '
        f'Reuse permitted under {LICENCE} with attribution. The same entry is in the docket '
        f'JSON as item {e(it["id"])}.</p></div></section>')

    # THE BEAT, AS A LINK RATHER THAN A CHIP. The topic hub has always existed and the item page
    # has always printed the topic as dead text, so the one page that proves a decision belongs
    # to a beat was the one page that would not take a reader to the rest of that beat.
    beat = (f'<section><h2>Beat</h2><div class="prose"><p>Filed under '
            f'<a href="../../topic/{e(it["topic"])}/">{e(topic_label(it["topic"]))}</a>, '
            f'with every other decision on that beat.</p></div></section>')

    pa = it.get("public_access") or {}
    how = pa.get("how") or ""
    url = pa.get("url")
    # `go` marks a STANDALONE action link, as opposed to a link inside a sentence. WCAG 2.5.8
    # exempts the inline case and this is not it, so the class is what lets the stylesheet give
    # it a target a thumb can hit without inline-blocking every link in the prose.
    act = (f'<p>{e(how)}</p>' + (f'<p><a class="go" href="{e(url)}" rel="nofollow noopener">'
                                 f'Where to do it</a></p>' if url else "")
           ) if how else '<p>No formal way in is published for this decision.</p>'

    body = f"""
<article>
<h1>{e(it["title"])}</h1>
{item_meta(it, today)}
{clock(it, today)}
<div class="prose"><p>{e(it["summary"])}</p></div>

<section><h2>How to take part</h2><div class="prose">{act}</div></section>

<section><h2>Where</h2><div class="prose" data-prose="data">{item_where(it)}</div></section>

{timeline}

{moved_block}<section>
  <h2>The evidence</h2>
  <div class="prose"><p>Every fact above rests on one of these. The words are the source's own.</p></div>
  {claims_html(it)}
</section>

{qa_block}{cite}

{beat}

<p class="meta" data-prose="data"><span class="num">Last checked {e(it["last_verified"])}</span></p>
</article>
"""
    return page(title=f'{it["title"]} · {SITE_NAME}', depth=2, active="record/",
                desc=it["summary"][:180], body=body, today=today,
                canonical=f'item/{it["id"]}/',
                # ITS OWN CARD, carrying its own headline. A shared decision link now shows
                # what the decision is rather than the site's generic mark.
                og_image=f'og/{it["id"]}.png',
                og_alt=f'{it["title"]}. A card from the Texas AI Docket.',
                # THE RECORD, SAID IN MACHINE READABLE FORM. A Report carrying this item's
                # citations, the questions a reader arrives with answered from its own fields,
                # and the trail back up. Every one computed in schema.py, none written.
                extra_ld=schema.item_nodes(SCHEMA_CTX, it, today))


def place_page(place: dict, items: list, today: str) -> str:
    """One metro or one county. The same page shape either way, because to a reader they
    are the same question asked about a different size of place."""
    ids = set(place["items"])
    mine = [i for i in items if i["id"] in ids]
    lit = set(place.get("touched_counties") or place.get("counties") or [])

    rows = "".join(
        f'<tr><td><a href="../../item/{e(i["id"])}/">{e(i["title"])}</a></td>'
        f'<td>{e(i["topic"])}</td><td>{e(i["status"])}</td></tr>' for i in mine)

    if place["kind"] == "metro":
        counties = place["counties"]
        touched = place.get("touched_counties") or []
        untouched = [c for c in counties if c not in touched]
        # THE UNTOUCHED COUNTIES ARE NAMED, not omitted. A metro page listing only the
        # counties with entries would imply the area is the sum of what we found, and the
        # honest statement is that the area is this and we have found something in some of it.
        scope = (f'<p class="gap">This area is <span class="num">{len(counties)}</span> '
                 f'{"county" if len(counties) == 1 else "counties"}. The record currently '
                 f'names {", ".join(e(c) for c in touched)}.'
                 + (f' Nothing has yet been found in {", ".join(e(c) for c in untouched)}.'
                    if untouched else '') + '</p>')
        head = f"{e(place['name'])}"
        sub = e(place["full_name"])
        # What the map's count is a count OF on this page. Without it the accessible title
        # announces a statewide figure that this page's own prose contradicts two lines above.
        map_scope = f"the items on this {place['name']} page"
    else:
        tx = _place_facts()
        head = f"{e(place['name'])} County"
        metro = place.get("metro")
        if metro:
            # THE AREA IS THE GAZETTEER'S, AND THE LINK IS PART OF THE CLAIM. County pages
            # once discarded this assignment and all took the `else` branch below, so forty
            # counties that are in a CBSA said they were outside every one. Naming and linking
            # the resolved area lets the reader inspect the larger geographic answer directly.
            sub = (f'Part of the <a href="../{e(metro["id"])}/">{e(metro["name"])}</a> '
                   f'{e(metro["area_type"])} statistical area')
            scope = ""
        else:
            sub = "Outside every metropolitan and micropolitan area"
            scope = (f'<p class="gap">This county is in no federal statistical area, which is '
                     f'true of <span class="num">{tx["outside_any_metro"]}</span> of the '
                     f'state\'s <span class="num">{tx["counties"]}</span>. It gets its own page '
                     f'for that reason.</p>')
        map_scope = f"the items on this {place['name']} County page"

    # Preserve the established indentation when a scope paragraph exists, while emitting no
    # whitespace-only line for assigned county pages whose linked area is already in `sub`.
    scope_html = f"  {scope}\n" if scope else ""
    body = f"""
<h1>{head}</h1>
<div class="prose">
  <p>{sub}. <span class="num">{len(mine)}</span>
  {"item" if len(mine) == 1 else "items"} in the record.</p>
{scope_html}</div>
{texas_map.render(lit=lit, inset=True, scope=map_scope)}
<table><thead><tr><th>Item</th><th>Topic</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="prose"><a href="../../record/">The whole record</a> ·
<a href="../">Every place</a></p>
"""
    return page(
        title=f"{head} · {SITE_NAME}", depth=2, active="record/",
        desc=f"What the record of Texas AI decisions says about {head}.",
        body=body, today=today, canonical=f"place/{place['id']}/",
        # A PLACE PAGE IS A COLLECTION AND IT SAID SO NOWHERE. These 73 pages carried the
        # boilerplate site node and nothing else, so the most locally searched question this
        # record answers, whether anything is happening in my county, was the one a crawler
        # had the least to go on. The list names the decisions rather than counting them.
        extra_ld=[
            schema.collection_node(
                SCHEMA_CTX, name=head, path=f"place/{place['id']}/",
                description=f"Texas AI decisions on the record for {head}.",
                count=len(mine),
                elements=[(i["title"], f'item/{i["id"]}/') for i in mine]),
            schema.breadcrumbs(SCHEMA_CTX, [(SITE_NAME, ""), ("By place", "place/"),
                                            (head, f"place/{place['id']}/")]),
        ])


def places_index(items: list, today: str) -> tuple:
    """The hub for /place/. Returns (numerals it prints, html).

    THE BIGGEST SURFACE ON THIS SITE HAD NO INDEX. Seventy odd place pages shipped with no
    page above them, reachable only from whichever item happened to name that county and from
    the sitemap. The build loop's own comment said "The index, then a page for every metro",
    and the index it named was never written. So a reader could not see the geography of the
    record at all, and the pages that answer the most locally searched question this record
    can answer, whether anything is happening in MY county, were the hardest ones to reach.

    METROS AND COUNTIES ARE LISTED SEPARATELY because they are different sizes of answer, and
    a single alphabetical run of both would put Bell County next to the Killeen area that
    contains it with nothing saying which is which.
    """
    places = all_places(items, today)
    metros = [pl for pl in places if pl["kind"] == "metro"]
    counties = [pl for pl in places if pl["kind"] == "county"]
    tx = _place_facts()

    a = numeral_lint.Authorised()
    a.add(len(items), len(places), len(metros), len(counties), *tx.values())

    def cell(pl: dict, label: str) -> str:
        n = len(pl["items"])
        a.add(n)
        return (f'<a class="topicchip" href="{e(pl["id"])}/">'
                f'<span class="tc-name">{e(label)}</span>'
                f'<span class="tc-n num">{n}</span></a>')

    metro_row = "".join(cell(pl, pl["name"]) for pl in
                        sorted(metros, key=lambda x: x["name"]))
    county_row = "".join(cell(pl, f'{pl["name"]} County') for pl in
                         sorted(counties, key=lambda x: x["name"]))

    body = f"""
<h1>By place</h1>
<div class="prose"><p>Texas has <span class="num">{tx["counties"]}</span> counties. This record
currently names <span class="num">{len(counties)}</span> of them across
<span class="num">{len(metros)}</span> statistical areas. Every county the record touches keeps
its own page. So does every area. A reader asking about Bell County wants Bell County rather
than the Killeen area that contains it.</p></div>

<h2>Statistical areas</h2>
<div class="prose"><p>The federal metropolitan and micropolitan areas this record touches.
Each page names the counties in the area and says plainly which of them nothing has been found
in yet.</p></div>
{'<nav class="topicrow" aria-label="Areas">' + metro_row + '</nav>' if metro_row else ''}

<h2>Counties</h2>
<div class="prose"><p>Every county with at least one decision on the record.</p></div>
{'<nav class="topicrow" aria-label="Counties">' + county_row + '</nav>' if county_row else ''}

<p class="meta" data-prose="data"><a href="../record/">All
<span class="num">{len(items)}</span> decisions</a> ·
<a href="../topic/">Browse by beat</a></p>
"""
    html = page(
        title=f"By place · {SITE_NAME}", depth=1, active="record/",
        desc=("Texas AI decisions by county and metro area. Every county this record touches "
              "keeps its own page of who decided, by when, and whether the public still has "
              "a way in."),
        body=body, today=today, canonical="place/",
        extra_ld=[
            schema.collection_node(
                SCHEMA_CTX, name="By place", path="place/",
                description="Every Texas county and statistical area this record touches.",
                count=len(places),
                elements=[(pl["name"] if pl["kind"] == "metro" else f'{pl["name"]} County',
                           f'place/{pl["id"]}/')
                          for pl in sorted(places, key=lambda x: (x["kind"], x["name"]))]),
            schema.breadcrumbs(SCHEMA_CTX, [(SITE_NAME, ""), ("The record", "record/"),
                                            ("By place", "place/")]),
        ])
    return a.set, html



__all__ = ['docket_index', '_CAL_JS', 'docket_calendar_section', 'topic_chips', 'topic_page', 'TOPIC_BLURBS', 'topic_blurb', '_open_now', 'topics_index', 'covers_section', '_item_metros', 'item_where', 'item_timeline', 'item_page', 'place_page', 'places_index']
