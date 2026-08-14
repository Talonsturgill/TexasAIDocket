#!/usr/bin/env python3
"""site_build.py — the published site, generated from the ledgers.

THE READER THIS IS BUILT FOR

Someone busy and sceptical, often on a phone, sometimes sitting in a county commissioners
meeting. They have one question the rest of the internet does not answer for them:

    Is anything being decided near me, and can I still say something about it?

So the site answers that first, above everything else, computed fresh on every build. Everything
after it exists to make the answer checkable.

THREE RULES THIS FILE OBEYS

  1 docs/ IS A PURE FUNCTION OF THE LEDGERS. Nothing here reads the previous build, and no page
    is ever hand-edited. `site_fresh_check.py` proves it by rebuilding into a temp directory and
    requiring byte equality. That is what makes it structurally impossible for a bad run to
    corrupt the live site: the worst case is a stale build, never a broken one.
  2 EVERY NUMERAL IS COMPUTED. Counts come from `len()`, days come from date arithmetic. No
    figure is typed here, and `docket_build`'s gates already refused any that were typed into
    the record.
  3 NOTHING IS CLAIMED THAT THE RECORD DOES NOT HOLD. Where the record is thin the page says so
    and publishes the size of the gap. An empty docket draws an empty map.

    site_build.py --out docs
    site_build.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as _dt
import html
import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ask_answers                                                # noqa: E402
import docket_build as dk                                          # noqa: E402
import fonts_build                                                 # noqa: E402
import gridwatch_page                                              # noqa: E402
import frontchip                                                   # noqa: E402
import sky                                                         # noqa: E402
import texas_map                                                   # noqa: E402
import waterwatch_page                                             # noqa: E402
import grain                                                       # noqa: E402
import mark                                                        # noqa: E402
import numeral_lint                                                # noqa: E402
import theme                                                       # noqa: E402

LEDGER = REPO_ROOT / "ledger" / "docket.json"

SITE_NAME = "Texas AI Docket"
# One key drives every absolute URL, so moving to a custom domain is a one line change.
SITE_URL = "https://talonsturgill.github.io/TexasAIDocket"

# THE MARK IS COMPUTED FROM THE STATUTE. It used to be a star path typed into this file, whose
# points were not equidistant from its center and whose inner vertices were not on a common
# circle, sitting in a block that was very nearly square when the flag's blue stripe is twice as
# tall as it is wide. Every one of those is a small wrongness, and small wrongnesses in a mark are
# what amateur means: nobody can name the fault and everybody can see it. See scripts/site/mark.py,
# which derives all of it from Government Code sec. 3100.001.
def star(cls: str = "star") -> str:
    return mark.star_svg(cls)


HOIST = mark.flag_svg()

# THE TOP BAR CARRIES PLACES A READER GOES, and `Data` is not one of them. It is where a
# machine goes, and putting it in the masthead cost a slot in the row that has to survive a
# phone, while the readers it was aimed at were never going to look there.
# `Docket` rather than `The record`, because it is the word the thing is called. The URL stays
# `record/`, since a published address is a promise to anything already linking it and a label
# is not.
#
# `Ask` is gone from the bar because the box is on the front page now. A search field a reader
# has to navigate to is a search field a reader does not use.
NAV = [("", "Home"), ("record/", "Docket"), ("articles/", "Articles"),
       ("videos/", "Videos"), ("grid/", "Grid"),
       ("water/", "Water"), ("services/", "Services"), ("about/", "About")]

# The footer's way out. Wider than the masthead nav, because the bottom of a page is where
# somebody who did not find what they came for goes looking, and the machine-readable surfaces
# belong there rather than in the top bar.
#
# THE FOOTER SAID "DATA" TWICE. It listed the `/data/` page and then listed `docket.json` as
# "Open data" beside it, which is the same idea under two names one word apart. Worse, all
# three raw links it carried are the exact three the `/data/` page exists to list, with the
# context that page adds and the footer cannot. So the page is the entry and the raw links
# come out. One name, one route, and the shortest footer this site has had.
# The scan is the free front door under the services ladder, so it belongs in the way out
# rather than in the top bar. Eight items is already a full masthead and a ninth would
# cost the seven that were there first.
FOOTNAV = NAV[1:] + [("scan/", "Scan"), ("data/", "Data")]

# WHERE THIS WAS MADE. Austin sits on the Balcones Escarpment, the fault line where the Hill
# Country drops to the coastal plain, which runs straight through the city.
#
# THE COORDINATE USED TO BE TYPED, and the comment that sat here granted it an exemption in
# prose: the only numbers on the site not derived from the record, a fact about a place rather
# than a measurement. That is a rationalisation rather than a rule, and the footer printed it
# four words from the line "Every numeral computed from data". Worse, the typed pair named a
# different point from anything this repository holds. It is read from the gazetteer's
# area weighted centroid for Travis County now, so the sentence and the data cannot drift.
MADE_AT_LEDE = "Built on the Balcones Escarpment"

# The one script the shell carries, and the three things it does. All three are progressive:
# with script off the page keeps its atmosphere, its content and its layout, and loses only the
# arrival animations and the glass on the bar.
SHELL_JS = """<script>
document.documentElement.classList.add('js');
addEventListener('scroll',function(){
  document.querySelector('.masthead').classList.toggle('scrolled',scrollY>8);
},{passive:true});
if('IntersectionObserver' in window){
  var els=document.querySelectorAll('[data-reveal]');
  var io=new IntersectionObserver(function(es){
    es.forEach(function(en){ if(en.isIntersecting){ en.target.classList.add('in');
      io.unobserve(en.target); } });
  },{rootMargin:'0px 0px -8% 0px'});
  els.forEach(function(el){ el.classList.add('pending'); io.observe(el); });
  // Last resort. If the callback never runs, every section is shown anyway rather than left
  // present and invisible.
  setTimeout(function(){ els.forEach(function(el){ el.classList.add('in'); }); },2500);
}
// THE MAP UNDER A THUMB.
// On a laptop the map answers "what is this county" with a hover title. A phone has no hover,
// so the only way to ask was to commit to a county and load its page, come back, and commit to
// the next one. That is not looking around, it is a survey taken one page load at a time.
// Dragging a thumb across the state now names each county and says what it holds, and lifting
// the thumb without moving still opens the county, so the link is not taken away.
(function(){
  var read=document.getElementById('mapread'), map=document.querySelector('svg.txmap');
  if(!read||!map||!('ontouchstart' in window)) return;
  var moved=false, sx=0, sy=0, last=null;
  function at(t){
    var el=document.elementFromPoint(t.clientX,t.clientY);
    return el&&el.closest?el.closest('path.c'):null;
  }
  function show(p){
    if(p===last) return;
    if(last) last.classList.remove('under');
    last=p;
    if(!p){ read.textContent=''; return; }
    p.classList.add('under');
    var n=p.getAttribute('data-n');
    read.textContent=p.getAttribute('data-county')+' County. '+
      (n? n+(n==='1'?' decision':' decisions')+' on the record. Lift to open.'
        : 'Nothing on the record yet.');
  }
  map.addEventListener('touchstart',function(e){
    var t=e.touches[0]; moved=false; sx=t.clientX; sy=t.clientY; show(at(t));
  },{passive:true});
  map.addEventListener('touchmove',function(e){
    var t=e.touches[0];
    if(Math.abs(t.clientX-sx)>6||Math.abs(t.clientY-sy)>6) moved=true;
    if(moved){ show(at(t)); e.preventDefault(); }
    // NOT PASSIVE, because a drag across the map has to stop the page scrolling under it. The
    // guard is the 6 pixel threshold: until the thumb has actually moved, the browser keeps
    // its scroll, so a reader who starts a page scroll on top of the map still scrolls.
  },{passive:false});
  map.addEventListener('touchend',function(e){
    if(!moved) return;               // a tap: leave the link alone, it is the whole point
    // A DRAG IS NOT A CLICK. Without this the county under the lifted thumb navigates, so
    // looking around the map would keep throwing the reader onto a county page.
    var kill=function(ev){ ev.preventDefault(); ev.stopPropagation(); };
    map.addEventListener('click',kill,{capture:true,once:true});
    setTimeout(function(){ map.removeEventListener('click',kill,{capture:true}); },400);
    setTimeout(function(){ show(null); },2600);
  });
})();
</script>"""


def e(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def short_date(iso: str) -> str:
    """"AUG 19", for a deadline set at display size. The long form stays in the prose."""
    d = _dt.date.fromisoformat(iso)
    return f"{d:%b} {d.day}".upper()


def ordinal(d: _dt.date) -> str:
    """House style: month first, with the ordinal. August 11th, never 11 August."""
    n = d.day
    suf = "th" if 11 <= n <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{d:%B} {n}{suf}"


def rel(depth: int) -> str:
    return "../" * depth


# --------------------------------------------------------------------------- shell
def page(*, title: str, desc: str, body: str, depth: int, active: str,
         today: str, canonical: str, extra_ld: list | None = None,
         home_page: bool = False) -> str:
    p = rel(depth)
    # `""` USED TO MEAN TWO THINGS AND ONE OF THEM WAS A LIE. It is Home's own href, and it
    # was also what a page with no nav entry passed to mean "none of these". So every item
    # page and every topic page shipped `aria-current="page"` on Home, telling a screen
    # reader it was on the front page while it read an item. Nothing looked wrong, because
    # the underline it draws is small and Home is where a reader's eye is not.
    #
    # `None` is the "none of these" sentinel now, and it is checked before the comparison
    # rather than falling out of it. Item and topic pages mark THE RECORD instead, which
    # is true of both and more useful than marking nothing.
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{p}{h}"{cur if active is not None and h == active else ""}>'
                  f'{e(t)}</a>' for h, t in NAV)

    footnav = "".join(f'<li><a href="{p}{h}">{e(t)}</a></li>' for h, t in FOOTNAV)
    # The colophon is assembled from parts rather than written as a sentence, so the separator
    # is a style decision in one place and the build date can never drift from `today`.
    colophon = "".join(f"<span>{e(s)}</span>" for s in (
        MADE_AT_LEDE,
        f"Revised {ordinal(_dt.date.fromisoformat(today))}, {today[:4]}",
        _made_at(),
        "Every numeral computed from data",
    ))

    ld = [{
        "@context": "https://schema.org", "@type": "WebSite",
        "name": SITE_NAME, "url": SITE_URL,
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
    }] + (extra_ld or [])

    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/{canonical}">
<link rel="stylesheet" href="{p}site.css">
<link rel="preload" href="{p}fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="alternate" type="application/atom+xml" title="{e(SITE_NAME)}" href="{p}atom.xml">
<script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
</head>
<body{' class="home"' if home_page else ''}>
<a class="skip" href="#main">Skip to the record</a>
{sky.sky_markup()}
<header class="masthead">
  <div class="wrap">
    <a class="wordmark" href="{p or './'}">{HOIST}<span>{e(SITE_NAME)}</span></a>
    <nav class="main" aria-label="Sections">{nav}</nav>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site">
  <div class="wrap block">
    {star("colophon")}
    <div>
      <ul class="footnav" data-prose="data">{footnav}</ul>
      <p class="colophon-line" data-prose="data">{colophon}</p>
    </div>
  </div>
</footer>
{SHELL_JS}
</body>
</html>
"""


# --------------------------------------------------------------------------- pieces
def clock(item: dict, today: str) -> str:
    """The question the site exists to answer, for one item."""
    state = dk.window_state(item, today)
    pa = item.get("public_access") or {}
    if state != "open":
        return ""
    days = (_dt.date.fromisoformat(pa["closes"]) - _dt.date.fromisoformat(today)).days
    soon = " soon" if days <= 7 else ""
    unit = "day" if days == 1 else "days"
    when = ordinal(_dt.date.fromisoformat(pa["closes"]))
    # THE NUMBER IS ALREADY THE BIGGEST THING IN THE BOX, so the label does not repeat it. It read
    # "19" and then "19 DAYS LEFT TO COMMENT", which wasted the line, wrapped the column onto four
    # rows and made a screen reader say the figure twice. Dropping the digit fixes all three at
    # once: the DOM order puts the number immediately before the unit, so it is still announced as
    # "19 days left to comment", once.
    left = "closes today" if days == 0 else f"{unit} left to comment"
    return (f'<div class="clock{soon}"><span class="days">{days}</span>'
            f'<span class="lab">{e(left)}</span>'
            f'<span class="lab">Closes {e(when)}</span></div>')


def room_label(room: str) -> str:
    """The badge a reader sees, which has to be true of every item wearing it.

    `contact_only` READ "NO FORMAL PROCESS" AND THAT WAS FLATLY WRONG ON SOME OF THEM. TCEQ's
    preliminary decision on the Crusoe plant at Abilene carried the badge while its own summary
    said written comments are due within thirty days of newspaper publication, and its How to
    take part section told a reader how to file one. The page contradicted itself in two inches
    of screen.
    The cause is upstream and is correct: a comment window with no close date cannot be
    `open_comment`, because the schema refuses a window a reader cannot date, so the batch
    demotes it. What was wrong is that the demotion target then ASSERTED something the record
    does not know. "No formal process" is a claim about the world. What this room actually
    means is narrower and always true: there is a named decider and a way to reach them, and no
    dated window this record can stand behind.
    """
    return {"open_comment": "Comment window open", "open_meeting": "Public meeting",
            "contact_only": "Write to the decider", "closed": "Closed",
            "comment_closed": "Comment window closed"}.get(room, room)


def effective_room(it: dict, today: str) -> str:
    """The room a reader is standing in TODAY, not the kind of room the ledger recorded.

    THE BADGE HAS TO DO THE ARITHMETIC THE CLOCK ALREADY DOES. `window_state` says exactly this in
    its docstring, that the ledger stores what kind of access exists and when it ends and that
    whether it is open right now is computed fresh every build, and the badge was the one place
    that ignored it. It rendered the stored `open_comment` as a green "comment window open" on an
    item whose deadline had passed the day before and whose own headline said the deadline had
    been reached. The clock on the same page knew, because the clock asks.

    That is worse than an inconsistency. Green on this site is a promise that a door is open to a
    reader right now, and the whole record is worth nothing if it points somebody at a window that
    shut yesterday.
    """
    room = (it.get("public_access") or {}).get("room", "")
    if room == "open_comment" and dk.window_state(it, today) == "closed":
        return "comment_closed"
    return room


def item_meta(it: dict, today: str) -> str:
    g = it.get("geography") or {}
    where = ("Statewide" if g.get("statewide")
             else ", ".join(g.get("counties") or []) or
             ("ERCOT region" if g.get("on_ercot") else ""))
    # THE SAME LABEL THE FILTER ROW USES. A card that says DEFENSE-AND-FEDERAL beside a chip
    # that says "Defense and federal" is one taxonomy printed two ways, and a reader has to work
    # out that they are the same thing. The slug stays the identifier in the URL and the ledger.
    bits = [f'<span class="tag">{e(topic_label(it["topic"]))}</span>',
            f'<span>{e(it["decider"]["name"])}</span>']
    if where:
        bits.append(f'<span>{e(where if len(where) < 60 else where[:57] + "...")}</span>')
    room = effective_room(it, today)
    bits.append(f'<span class="rooms {e(room)}">{e(room_label(room))}</span>')
    # Chips, not sentences. The comma between two of Oncor's 22 counties is a delimiter, and
    # this row repeats once per card, so leaving it in a comma-density measurement would fail
    # a page for the crime of listing counties. See house_style_check.DATA_REGION.
    return f'<p class="meta" data-prose="data">{"".join(bits)}</p>'


def claims_html(it: dict) -> str:
    """The proof, shown rather than asserted.

    Putting the source's own words on the page is the whole trust mechanism. A reader does not
    have to believe the summary; they can read what the filing actually said.
    """
    out = []
    for c in it.get("claims", []):
        kind = {"primary_official": "Primary source, official",
                "primary_corporate": "Primary source, the company",
                "journalism": "Journalism"}.get(c.get("source_type"), "")
        out.append(
            f'<div class="claim">'
            f'<blockquote>{e(c["verbatim_quote"])}</blockquote>'
            f'<cite><a href="{e(c["source_url"])}" rel="nofollow noopener">'
            f'{e(c.get("source_title") or c["source_url"][:70])}</a></cite> '
            f'<span class="kind" data-prose="data">{e(kind)}</span></div>')
    return "".join(out)


# --------------------------------------------------------------------- published work
# Raw media is served from the repository rather than copied into `docs/`. A carousel run
# ships six 1080x1350 images and the site would double the repository every day if the build
# copied them. They are already committed on `main` and already public.
RAW = f"https://raw.githubusercontent.com/Talonsturgill/TexasAIDocket/main"


def load_runs() -> list:
    """Every carousel this project has shipped, newest first.

    READ FROM THE ARTIFACTS, NOT FROM A LIST SOMEBODY MAINTAINS. A run is shipped when
    `runs/carousel/<date>/` exists with copy in it, so the feed cannot claim an article that
    was never published and cannot miss one that was. A directory that does not parse is
    skipped rather than guessed at, because a half-written run is a run that did not ship.
    """
    out = []
    base = REPO_ROOT / "runs" / "carousel"
    if not base.is_dir():
        return out
    for d in sorted((x for x in base.iterdir() if x.is_dir()), key=lambda x: x.name,
                    reverse=True):
        try:
            copy = json.loads((d / "copy.json").read_text("utf-8"))
        except Exception:                                            # noqa: BLE001
            continue
        slides = sorted(d.glob("slide-*.webp")) or sorted(d.glob("slide-*.png"))
        if not slides:
            continue
        title = (copy.get("document_title") or copy.get("title") or d.name)
        hook = (copy.get("hook") or copy.get("subtitle") or "")
        out.append({"date": d.name, "title": str(title), "hook": str(hook),
                    "slides": len(slides), "cover": slides[0].name})
    return out


def video_feed() -> dict:
    """The Dispatch feed, or an empty one.

    `docs/videos/videos.json` is written by the publish step in `TexasAIDispatch` and by
    nothing here. It legitimately does not exist until the first video ships, so an absent
    feed is zero videos and never an error. Counted at every build, which means the number
    is right as of the last rebuild and the front page re-reads it live for the rest.
    """
    try:
        d = json.loads((REPO_ROOT / "docs" / "videos" / "videos.json").read_text("utf-8"))
        return d if isinstance(d, dict) else {"videos": d}
    except Exception:                                                # noqa: BLE001
        return {}


def video_count() -> int:
    return len([v for v in (video_feed().get("videos") or []) if v])


# --------------------------------------------------------------------------- pages
def telemetry(today: str) -> str:
    """One live, computed, dated line about the physical world, for the top of the front page.

    THIS USED TO REPORT THE GRID AND THAT WAS THE MISTAKE. It read "Peak drew 75.5% of
    committed capacity", which was measured, dated, correctly rounded and almost nobody's
    idea of a reason to keep reading. It asks the reader to already know what committed
    capacity is before the sentence can mean anything, and the opening line of a front page
    is the worst place in the product to require homework.

    The sibling opens with how much daylight its state capital has today and how fast it is
    losing it, and that one detail is most of why its front page reads as alive rather than
    published. What makes it work is not that it is about energy. It is that the reader
    already feels it, it moves every morning, and it accumulates in one direction so you can
    tell where you are in the season from it.

    Texas has no daylight story, so this is the heat. The hundred degree day is the unit
    Texas already keeps score in, and the count runs all summer as a shared grievance. From
    November the same clock counts freezing nights, which is the other extreme Texas counts
    and the reason it argues about its grid at all.

    The arithmetic and the rotation live in `frontchip`, with their self-tests. This function
    is markup and nothing else.

    IT IS NOT A LINK, and that is deliberate rather than an omission. It was one, pointing at
    the grid page, back when it reported the grid. A reader who clicks a line about the heat
    lands on a page that says nothing about the heat, and an unpaid promise costs more than
    the click was worth. The sibling's daily chip is a plain div for the same reason. The
    record behind it is published as open data and listed on the data page, which is where
    somebody who wants the numbers goes.

    Returns "" when the record holds nothing or has gone stale, because a front page that
    invents a number to fill a slot is the exact failure this project exists to not have.
    """
    r = frontchip.reading(_dt.date.fromisoformat(today))
    if not r:
        return ""
    place, middle, tail = frontchip.phrasing(r)
    middle = middle.format(through=ordinal(r["through"]))
    return (f'<div class="tele">{e(place)}'
            f'<span>{e(middle)}</span><span>{e(tail)}</span></div>')


def videos_page(today: str) -> str:
    """The Dispatch feed, rendered in the reader's browser from the feed file.

    GENERATED, NOT A HAND-BUILT PASSTHROUGH, and that is a deliberate departure from how the
    sibling product does it. A standalone page carries its own copy of the masthead, and this
    site's masthead changed twice in one afternoon. A hand-maintained nav does not go wrong
    loudly, it goes wrong by still pointing at a tab that no longer exists, on the one page
    nobody regenerates. So the shell is generated like every other page and only the DATA is
    external.

    THE FEED IS FETCHED RATHER THAN BAKED for the same reason the front page fetches it:
    `docs/videos/videos.json` is written by `TexasAIDispatch` on its own schedule, and a
    build cannot know what shipped after it ran.

    WORKS WITH NO FEED AT ALL. Before the first video the file does not exist, the fetch
    fails, and the page says so in a sentence. It never renders a heading over an empty grid.
    """
    body = """
<h1>Videos</h1>
<div class="prose">
  <p>One short film a day about artificial intelligence in Texas. Narrated, sourced, and
  built by the same machine that keeps the docket.</p>
</div>
<div id="vidgrid" class="deckgrid"></div>
<p id="vidnone" class="gap">No video has shipped yet. The first one appears here the day it
does.</p>
<script>
(function(){
  var grid=document.getElementById('vidgrid'), none=document.getElementById('vidnone');
  if(!window.fetch)return;
  var esc=function(t){return String(t==null?'':t).replace(/[&<>"]/g,function(m){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m];});};
  fetch('videos.json').then(function(r){
    if(!r.ok)throw 0; return r.json();
  }).then(function(m){
    var base=m.media_base||'';
    var vs=(m.videos||[]).filter(function(v){return v&&v.video});
    if(!vs.length)return;
    var abs=function(u){return /^https?:\/\//.test(u)?u:base+u};
    grid.innerHTML=vs.map(function(v){
      var when=v.date||'';
      try{when=new Date(v.date+'T12:00:00').toLocaleDateString('en-US',
        {month:'long',day:'numeric',year:'numeric'})}catch(e){}
      /* preload none and poster only. A grid of autoplaying files is a data bill for a
         reader who came to look at one of them. */
      return '<figure class="vcard"><video controls playsinline preload="none" poster="'+
        esc(abs(v.poster||''))+'" src="'+esc(abs(v.video_mobile||v.video))+
        '" aria-label="'+esc(v.title||'Texas AI video')+'"></video>'+
        '<figcaption><span class="meta" data-prose="data"><span class="tag">'+esc(when)+
        '</span></span><h3>'+esc(v.title||'')+'</h3><p>'+esc(v.caption||'')+
        '</p></figcaption></figure>';
    }).join('');
    none.hidden=true;
  }).catch(function(){});
})();
</script>
"""
    return page(title=f"Videos · {SITE_NAME}", depth=1, active="videos/",
                desc="Every video Texas AI Docket has published. One short film a day on "
                     "artificial intelligence in Texas.",
                body=body, today=today, canonical="videos/")


def articles_page(runs: list, today: str) -> str:
    """Every carousel this project has shipped, newest first.

    HONEST WHEN EMPTY. Before the first run there is nothing here, and this says so in one
    sentence rather than rendering an empty grid under a confident heading. The same
    sentence is what a reader sees if every run fails for a week, which is the point: the
    page reports the state of the work rather than a state somebody hoped for.
    """
    cards = "".join(f"""<a class="deck" href="{e(r["date"])}/">
  <img src="{RAW}/runs/carousel/{e(r["date"])}/{e(r["cover"])}" width="1080" height="1350"
       loading="lazy" alt="Cover slide, {e(r["title"])}">
  <span class="meta" data-prose="data"><span class="tag">{e(ordinal(
    _dt.date.fromisoformat(r["date"])))}</span><span>{r["slides"]} slides</span></span>
  <h3>{e(r["title"])}</h3></a>""" for r in runs)

    body = f"""
<h1>Articles</h1>
<div class="prose">
  <p>One verified Texas and AI story at a time, drawn as a carousel. Newest first.</p>
</div>
{f'<div class="deckgrid">{cards}</div>' if runs else
 '<p class="gap">No article has shipped yet. The first one appears here the day it does.</p>'}
"""
    return page(title=f"Articles · {SITE_NAME}", depth=1, active="articles/",
                desc="Every article Texas AI Docket has published. One verified Texas and AI "
                     "story at a time.",
                body=body, today=today, canonical="articles/")


def article_page(r: dict, today: str) -> str:
    """One shipped carousel, every slide, and the caption that went out with it."""
    d = _dt.date.fromisoformat(r["date"])
    slides = "".join(
        f'<img src="{RAW}/runs/carousel/{e(r["date"])}/slide-{i:02d}.webp" width="1080"'
        f' height="1350" loading="lazy" alt="Slide {i} of {r["slides"]}">'
        for i in range(1, r["slides"] + 1))
    body = f"""
<article>
<h1>{e(r["title"])}</h1>
<p class="meta" data-prose="data"><span class="tag">{e(ordinal(d))}</span>
  <span>{r["slides"]} slides</span></p>
<div class="prose"><p>{e(r["hook"])}</p></div>
<div class="slides">{slides}</div>
<p class="meta" data-prose="data"><a href="../">Every article</a></p>
</article>
"""
    return page(title=f'{r["title"]} · {SITE_NAME}', depth=2, active="articles/",
                desc=(r["hook"] or r["title"])[:180], body=body, today=today,
                canonical=f'articles/{r["date"]}/')


def latest_article(runs: list) -> str:
    """The newest carousel, baked at build time.

    BAKED RATHER THAN FETCHED, unlike the video below it, and the difference is where the
    data lives. The runs are in this repository, so the build already knows them and a
    reader with script off still sees the article. The video feed is written by another
    repository on its own schedule, so the build's answer goes stale between rebuilds and
    has to be re-read in the page.

    Renders nothing at all when nothing has shipped. A section that explains its own
    emptiness is worse than a section that is not there.
    """
    if not runs:
        return ""
    r = runs[0]
    return f"""
<section data-reveal>
  <h2>The latest article</h2>
  <p class="sub">One verified Texas and AI story, drawn as a swipeable carousel.</p>
  <div class="latest">
    <a class="cover" href="articles/{e(r["date"])}/"><img
      src="{RAW}/runs/carousel/{e(r["date"])}/{e(r["cover"])}"
      width="1080" height="1350" loading="lazy"
      alt="Cover slide, {e(r["title"])}"></a>
    <div>
      <p class="meta" data-prose="data"><span class="tag">{e(ordinal(
        _dt.date.fromisoformat(r["date"])))}</span>
        <span>{r["slides"]} slides</span></p>
      <h3>{e(r["title"])}</h3>
      <p>{e(r["hook"])}</p>
      <div class="ctarow">
        <a class="cta ghost" href="articles/{e(r["date"])}/">Read it</a>
        <a class="cta ghost" href="articles/">Every article</a>
      </div>
    </div>
  </div>
</section>"""


def latest_video() -> str:
    """The newest Dispatch, filled in by the page from the feed it fetches.

    THE SKELETON IS BAKED AND THE CONTENT IS NOT, because `docs/videos/videos.json` belongs
    to `TexasAIDispatch` and is appended to on a schedule this build knows nothing about. A
    video that ships an hour after a rebuild would sit invisible until the next one, which
    for a daily feed is most of its life.

    HIDDEN UNTIL IT HAS SOMETHING. The section starts `hidden` and is only revealed once a
    video is actually in the feed, so a reader never meets a heading over an empty frame,
    and the page is correct on the day the feed does not exist yet.

    The file only loads when the section scrolls into view. A muted autoplaying video at the
    top of a page costs a reader on a county road their data before they have chosen to
    watch anything.
    """
    return """
<section id="homevid" data-reveal hidden>
  <h2>The latest video</h2>
  <p class="sub">The newest from the daily feed.</p>
  <div class="latest">
    <div class="vidwrap"><video id="hv" muted playsinline loop preload="none"
      aria-label="The latest Texas AI video"></video></div>
    <div>
      <p class="meta" data-prose="data"><span class="tag" id="hvdate"></span></p>
      <h3 id="hvtitle"></h3>
      <p id="hvcap"></p>
      <div class="ctarow"><a class="cta ghost" href="videos/">Every video</a></div>
    </div>
  </div>
</section>
<script>
(function(){
  var sec=document.getElementById('homevid');
  if(!sec||!window.fetch)return;
  fetch('videos/videos.json').then(function(r){return r.json()}).then(function(m){
    var base=m.media_base||'';
    var vs=(m.videos||[]).filter(function(v){return v&&v.video});
    /* The counter re-reads the same fetch, so a video that landed after the last rebuild
       is counted the moment anybody loads the page. */
    var st=document.getElementById('vidstat');
    if(st&&vs.length){var n=vs.length;
      st.querySelector('.n').textContent=(n<10?'0':'')+n;}
    if(!vs.length)return;
    var v=vs[0], abs=function(u){return /^https?:\/\//.test(u)?u:base+u};
    var el=document.getElementById('hv');
    if(v.poster)el.poster=abs(v.poster);
    el.dataset.src=abs(v.video_mobile||v.video);
    document.getElementById('hvtitle').textContent=v.title||'';
    document.getElementById('hvcap').textContent=v.caption||'';
    var d=document.getElementById('hvdate');
    try{d.textContent=new Date(v.date+'T12:00:00').toLocaleDateString('en-US',
      {month:'long',day:'numeric',year:'numeric'})}catch(e){d.textContent=v.date||''}
    sec.hidden=false;
    var io=new IntersectionObserver(function(es){es.forEach(function(en){
      if(!en.isIntersecting)return;
      if(!el.src){el.src=el.dataset.src;var q=el.play();if(q&&q.catch)q.catch(function(){});}
      io.disconnect();})},{rootMargin:'200px'});
    io.observe(sec);
  }).catch(function(){});
})();
</script>"""


def home(items: list, today: str) -> str:
    proj = dk.project(items, today)
    act = proj["actionable_now"]
    lit = {c for it in items for c in (it.get("geography") or {}).get("counties") or []}
    svg = texas_map.render(lit=lit, links=county_links(items, today, 0),
                           counts=proj["by_county"])

    n_counties = len(lit)
    n_items = proj["counts"]["items"]
    n_claims = proj["counts"]["claims"]
    runs = load_runs()
    n_videos = video_count()

    if act:
        soonest = act[0]
        lede = (f'<div class="clock{" soon" if soonest["days_left"] <= 7 else ""}">'
                f'<span class="days">{soonest["days_left"]}</span>'
                f'<span class="lab">days left on the next comment window</span></div>')
        openers = (f'<p><strong>{len(act)}</strong> of the '
                   f'<strong>{n_items}</strong> decisions on this record are still open to '
                   f'public comment.</p>')
    else:
        lede = ('<div class="gap"><strong>No comment window on this record is open today.</strong>'
                ' Windows are checked every day, and one appears here the moment it opens.</div>')
        openers = f"<p>The record holds <strong>{n_items}</strong> decisions.</p>"

    # THE DEADLINE CARDS. A date at display size, a status word that is also a colour, and a
    # live count of what is left. Somebody should be able to find what is open to them without
    # reading a sentence.
    #
    # MARKED AS DATA, and that is a measurement fix rather than a formality. A card is a badge, a
    # date, a count and a docket title, none of which is running prose, and a docket title reads
    # "PUCT Project 58482, proposed new rule on Large Load Demand Management Service, open for
    # comment", where both commas are structural. Three of those on the front page were being read
    # as sentences by the comma density rule, which is exactly what `data-prose="data"` exists to
    # stop. It narrows the density scope only, never the construction rules, so an em dash or a
    # bare date inside a card is still a violation.
    rows = "".join(
        f'<li data-prose="data">'
        f'<a class="dcard{" open" if a["days_left"] > 7 else ""}" href="item/{e(a["id"])}/">'
        f'<span class="badge {"open" if a["days_left"] > 7 else "soon"}">'
        f'{"Open to you" if a["days_left"] > 7 else "Closing soon"}</span>'
        f'<span class="big">{e(short_date(a["closes"]))}</span>'
        f'<span class="left">{a["days_left"]} '
        f'{"day" if a["days_left"] == 1 else "days"} left</span>'
        f'<h3>{e(a["title"])}</h3>'
        f'<span class="note">Public comment closes</span></a></li>'
        for a in act[:3])

    # THE STAT ROW COUNTS WHAT THIS PROJECT HAS PUBLISHED, plus the one number a reader can
    # act on. It used to count quoted sources and counties touched, which are facts about the
    # record's internals rather than about the work: a reader has no use for 55 quotes and no
    # way to want a 56th. Articles and videos are the things that exist because this ran, and
    # the open doors are the reason to come back. All four are computed at build.
    #
    # `id="vidstat"` is read again at runtime. The video feed is appended to by another
    # repository on its own schedule, so a video that lands after today's build leaves this
    # number one behind until the next one. The front page re-reads the same feed it already
    # fetches for the latest-video block, so the figure is right whenever the page is loaded,
    # and the built number stays as the answer with script off.
    # A COUNTER THAT READS ZERO IS AN EMPTY SHELF, NOT A FACT WORTH THE FRONT PAGE.
    #
    # This row printed "00 ARTICLES WRITTEN" and "00 VIDEOS PUBLISHED" beside "58 DECISIONS
    # TRACKED", so half of it advertised nothing at all on a page whose whole argument is that
    # the record is substantial. Zero padded, "00" also reads as a broken widget rather than a
    # count. Nothing is hidden by leaving it out: both sections are in the navigation and a
    # reader who wants them can go and find them empty, honestly.
    #
    # So the row is a PRIORITY LIST and takes the first four that have something in them. The
    # published work leads once it exists, because a daily product proving it ships daily is
    # the strongest thing this row can say, and it comes back on its own the day the first
    # article lands rather than needing anybody to remember this rule.
    candidates = [
        (len(runs), "Articles written", False, ""),
        (n_videos, "Videos published", False, ' id="vidstat"'),
        (n_items, "Decisions tracked", False, ""),
        (len(act), "Doors open to you", True, ""),
        (n_counties, "Counties named", False, ""),
        (n_claims, "Sources cited", False, ""),
    ]
    stats = "".join(
        f'<div class="stat"{attrs}><span class="n{" hot" if hot else ""}">{v:02d}</span>'
        f'<span class="l">{e(label)}</span></div>'
        for v, label, hot, attrs in [c for c in candidates if c[0]][:4])

    body = f"""
<section class="hero rise">
  {telemetry(today)}
  <h1>AI is coming <em>South</em>.</h1>
  <p class="herolede">Every AI decision in Texas and the source behind it. Green means a door is
  open to you.</p>
  <div class="ctarow">
    <a class="cta solid" href="record/">The docket</a>
    <a class="cta ghost" href="grid/">The grid</a>
  </div>
  <div class="statrow">{stats}</div>
</section>

{ask_box(items, today)}

{latest_article(runs)}

{latest_video()}

<section data-reveal>
  <h2>Where</h2>
  <div class="prose"><p>Every county in Texas, drawn from the state's own geometry. The lit
  counties are the ones this record currently touches, <span class="num">{n_counties}</span>
  of <span class="num">{_place_facts()["counties"]}</span>.</p></div>
  {svg}
  <p class="mapread" id="mapread" role="status" aria-live="polite" data-prose="data"></p>
</section>

{'<section data-reveal><h2>Closing next</h2><ul class="deck">' + rows + '</ul>'
   '<p class="meta" data-prose="data"><a href="record/">See all ' + str(n_items) + ' decisions</a></p>'
   '</section>' if rows else
   '<section data-reveal>' + lede + '<p class="meta" data-prose="data"><a href="record/">See all '
   + str(n_items) + ' decisions</a></p></section>'}

<section data-reveal>
  <h2>What this is</h2>
  <div class="prose">
    <p>A record of decisions about artificial intelligence in Texas. Who decided. By when. Whether
    the public still has a way in. It holds <span class="num">{n_items}</span> decisions
    supported by <span class="num">{n_claims}</span> quoted sources.</p>
    <p>An entry is admitted only when every fact in it carries a quote from a source that was
    actually fetched. At least one of those sources has to be the filing, the statute or the
    agency itself rather than a news report about it.</p>
  </div>
</section>
"""
    return page(title=f"{SITE_NAME}", depth=0, active="", home_page=True,
                desc=("A fact-checked record of AI decisions in Texas. Who decided, by when, "
                      "and whether you can still comment."),
                body=body, today=today, canonical="",
                extra_ld=[docket_dataset_ld(items, today)])


def docket_index(items: list, today: str) -> str:
    """Sorted by urgency, because that is the order the reader needs, not the order we filed."""
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
        f'<td>{", ".join(e(t) for t in dict.fromkeys(i["topic"] for i in v))}</td></tr>'
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
  <p>Every decision on the record, <strong>ordered by how soon a reader can still act</strong>,
  not by when it was filed. <span class="num">{n_open}</span> of
  <span class="num">{len(items)}</span> are open to comment now.</p>
</div>
{topics}

<!-- THE MAP LIVES ON THE RECORD NOW, because geography is a property of the record rather
     than a subject of its own. It had a tab, and a tab is a promise that a reader wants to
     browse Texas by county, which is not what anybody arrives wanting. Clicking a lit county
     still opens what that county holds. -->
{texas_map.render(lit=lit, links=county_links(items, today, 1),
                  counts=proj["by_county"])}
<p class="mapread" id="mapread" role="status" aria-live="polite" data-prose="data"></p>
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

<ul class="items" data-prose="data">{rows}</ul>
"""
    return page(title=f"The record · {SITE_NAME}", depth=1, active="record/",
                desc="Every AI decision on the Texas record, ordered by how soon you can act.",
                body=body, today=today, canonical="record/")


def topic_label(topic: str) -> str:
    """The reader-facing name of a topic, derived from its slug and never typed twice.

    A slug is a filing convention. `DEFENSE-AND-FEDERAL` shouted in monospace is what a
    database looks like, not what a record reads like, and it was the label on the record
    page's filter row for as long as that row existed. The slug stays the identifier
    everywhere it is one, in the URL, the ledger and the ask engine's vocabulary, and this
    is the only place it becomes English.

    THE COMMA IS A RULE, NOT AN EXCEPTION FOR ONE SLUG. `land-water-and-permitting` is a list
    of three and reads wrong without it. `power-and-the-grid` is a list of two and reads wrong
    with it. What separates them is how many items sit before the "and", so that is what is
    counted: two or more means a serial list, and a serial list takes a comma between every
    item but the last pair. A hand-written label for the one awkward slug would be the same
    string typed in two places, which is how a URL and a heading drift apart.
    """
    words = topic.split("-")
    if "and" in words:
        i = words.index("and")
        head, tail = words[:i], words[i + 1:]
        if len(head) >= 2:
            phrase = ", ".join(head) + " and " + " ".join(tail)
            return phrase[0].upper() + phrase[1:]
    return topic.replace("-", " ").capitalize()


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
<p class="meta" data-prose="data"><a href="../../record/">All decisions</a></p>
"""
    return page(title=f"{topic_label(topic)} · {SITE_NAME}", depth=2, active="record/",
                desc=f"Texas AI decisions filed under {topic.replace('-', ' ')}.",
                body=body, today=today, canonical=f"topic/{topic}/")


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


def item_page(it: dict, today: str) -> str:
    dates = "".join(
        f'<tr><td class="num">{e(k["date"])}</td><td>{e(k["kind"].replace("_", " "))}</td>'
        f'<td>{e(k.get("note") or "")}</td></tr>'
        for k in sorted(it.get("key_dates", []), key=lambda d: d["date"]))
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

{'<section><h2>Dates</h2><table><thead><tr><th>Date</th><th>What</th><th>Note</th></tr></thead><tbody>' + dates + '</tbody></table></section>' if dates else ''}

<section>
  <h2>The evidence</h2>
  <div class="prose"><p>Every fact above rests on one of these. The words are the source's own.</p></div>
  {claims_html(it)}
</section>

<p class="meta" data-prose="data"><span class="num">Last checked {e(it["last_verified"])}</span></p>
</article>
"""
    return page(title=f'{it["title"]} · {SITE_NAME}', depth=2, active="record/",
                desc=it["summary"][:180], body=body, today=today,
                canonical=f'item/{it["id"]}/')


def _place_slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _place_facts() -> dict:
    """The two figures the place pages state about Texas itself, COMPUTED.

    The first draft of this page typed "121 of 254" into prose, which is exactly the
    thing `CLAUDE.md` forbids and exactly the thing nobody caught, because the numeral
    gate had never been run over a docket page. Both come out of the gazetteer now, so
    a redelineation changes the sentence rather than dating it.
    """
    doc = json.loads((REPO_ROOT / "assets" / "geo" / "tx-places.json").read_text("utf-8"))
    counties = [p for p in doc["places"] if p.get("kind") == "county"]
    return {
        "counties": len(counties),
        "in_a_metro": sum(1 for c in counties if c.get("metro")),
        "outside_any_metro": sum(1 for c in counties if not c.get("metro")),
    }


def _made_at() -> str:
    """The footer coordinate, read from the gazetteer rather than typed.

    ROUNDING IS A COMPUTATION WITH A STATED RULE, per `CLAUDE.md`, so the rule is here:
    degrees are truncated and the remaining fraction is rounded to the nearest whole
    minute. Seconds are dropped because a centroid is not accurate to a second and
    printing one would claim a precision the source does not carry.
    """
    doc = json.loads((REPO_ROOT / "assets" / "geo" / "tx-places.json").read_text("utf-8"))
    tr = next(p for p in doc["places"] if p.get("id") == "county-travis")

    def dm(v: float, pos: str, neg: str) -> tuple:
        d, m = int(abs(v)), round((abs(v) - int(abs(v))) * 60)
        if m == 60:                                    # 30.9999 must read 31°0', not 30°60'
            d, m = d + 1, 0
        return d, m, (pos if v >= 0 else neg)

    lat, lon = dm(tr["lat"], "N", "S"), dm(tr["lon"], "E", "W")
    return f"{lat[0]}°{lat[1]}'{lat[2]} {lon[0]}°{lon[1]}'{lon[2]}"


def _made_at_numerals() -> tuple:
    """The four figures `_made_at` prints, for the authorised set. Same call, same values."""
    return tuple(re.findall(r"\d+", _made_at()))


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
    else:
        tx = _place_facts()
        scope = (f'<p class="gap">This county is in no federal statistical area, which is '
                 f'true of <span class="num">{tx["outside_any_metro"]}</span> of the '
                 f'state\'s <span class="num">{tx["counties"]}</span>. It gets its own page '
                 f'for that reason.</p>')
        head = f"{e(place['name'])} County"
        sub = "Outside every metropolitan and micropolitan area"

    body = f"""
<h1>{head}</h1>
<div class="prose">
  <p>{sub}. <span class="num">{len(mine)}</span>
  {"item" if len(mine) == 1 else "items"} in the record.</p>
  {scope}
</div>
{texas_map.render(lit=lit, inset=True)}
<table><thead><tr><th>Item</th><th>Topic</th><th>Status</th></tr></thead>
<tbody>{rows}</tbody></table>
<p class="prose"><a href="../../record/">The whole record</a></p>
"""
    return page(title=f"{head} · {SITE_NAME}", depth=2, active="record/",
                desc=f"What the record of Texas AI decisions says about {head}.",
                body=body, today=today, canonical=f"place/{place['id']}/")


def all_places(items: list, today: str) -> list:
    """Every place that gets a page: the metros, then the counties in none of them."""
    proj = dk.project(items, today)
    out = []
    for mid, m in proj["by_metro"].items():
        out.append({**m, "kind": "metro"})
    by_county = {}
    for it in items:
        for c in (it.get("geography") or {}).get("counties") or []:
            by_county.setdefault(c, []).append(it["id"])
    # EVERY TOUCHED COUNTY, not only the ones in no metro. The map is the way into this now
    # and a reader clicking Taylor wants Taylor, not the Abilene area that contains it. A
    # county page that only existed for the unmetroed half would leave two thirds of the lit
    # counties on the map pointing at nothing.
    for c in sorted(by_county):
        out.append({"id": f"county-{_place_slug(c)}", "kind": "county", "name": c,
                    "full_name": f"{c} County", "counties": [c],
                    "touched_counties": [c], "items": by_county.get(c, [])})
    return out


def county_links(items: list, today: str, depth: int) -> dict:
    """county name -> href for its page, at the depth the map is being drawn from."""
    up = rel(depth)
    return {c: f"{up}place/county-{_place_slug(c)}/"
            for it in items for c in (it.get("geography") or {}).get("counties") or []}


def data_page(items: list, today: str) -> str:
    proj = dk.project(items, today)
    rows = "".join(f'<tr><td>{e(k)}</td><td class="n num">{v}</td></tr>'
                   for k, v in proj["counts"]["by_topic"].items())
    body = f"""
<h1>The data</h1>
<div class="prose">
  <p>Four files, each the one this site was built from, so anything published here can be
  recomputed rather than taken on trust.</p>
  <ul class="filelist" data-prose="data">
    <li><a href="../docket.json">docket.json</a> every decision in the record</li>
    <li><a href="../gridwatch.json">gridwatch.json</a> one settled ERCOT day per record, hourly</li>
    <li><a href="../waterwatch.json">waterwatch.json</a> reservoir storage, per reservoir per day</li>
    <li><a href="../weather.json">weather.json</a> observed daily weather, with its normals</li>
  </ul>
</div>
<table><thead><tr><th>Topic</th><th class="n">Items</th></tr></thead><tbody>{rows}</tbody></table>
<div class="prose">
  <h2>How a fact gets in</h2>
  <p>An entry is admitted when every gate passes. The shape is valid and every claim carries a
  verbatim quote and a URL that was fetched. No numeral appears in the prose that is not either
  quoted from a source or computed from the record itself. At least one source is primary.</p>
  <p>Entries that fail stay out until they pass. Nothing is published on the strength of a
  headline alone.</p>
</div>
"""
    return page(title=f"The data · {SITE_NAME}", depth=1, active="data/",
                desc="The Texas AI Docket as open data, and the gates every entry passes.",
                body=body, today=today, canonical="data/")


def grid_page(today: str) -> str:
    """The Texas Grid Watch. A sibling of the docket, not a child of it.

    The docket tracks discrete decisions on a scale of months. This tracks the physical system
    on a scale of days. They share a masthead and nothing else: grid readings never enter
    docket.json, because that schema is decision centric and a time series does not fit it.

    THE NUMERAL GATE RUNS HERE, AT BUILD TIME, and raises rather than warns. Every figure in
    this page's copy must trace to something gridwatch_page computed from the record. A page
    that fails is not published, which is the only version of that promise worth making.
    """
    recs = gridwatch_page.load()
    body = gridwatch_page.body(recs, today)
    stray = gridwatch_page.lint(body, gridwatch_page.figures(recs))
    if stray:
        raise SystemExit(
            "site_build: the grid watch page carries numerals that trace to no computation: "
            + ", ".join(stray[:12]))
    return page(title=f"Texas Grid Watch · {SITE_NAME}", depth=1, active="grid/",
                desc="A daily numeric record of how the ERCOT grid is absorbing large "
                     "constant load. Measured, computed, never estimated.",
                body=body, today=today, canonical="grid/",
                extra_ld=[{
                    "@context": "https://schema.org", "@type": "Dataset",
                    "name": "Texas Grid Watch",
                    "description": "Daily settled ERCOT demand: measured hourly load, ERCOT's "
                                   "day ahead forecast, committed capacity, and generation by "
                                   "fuel. One record per day, append only.",
                    "url": f"{SITE_URL}/grid/",
                    "license": "https://creativecommons.org/licenses/by/4.0/",
                    "creator": {"@type": "Organization", "name": SITE_NAME},
                    "distribution": [{"@type": "DataDownload",
                                      "encodingFormat": "application/json",
                                      "contentUrl": f"{SITE_URL}/gridwatch.json"}],
                    "isAccessibleForFree": True,
                    "temporalCoverage": (f'{recs[0]["date"]}/{recs[-1]["date"]}'
                                         if recs else today),
                }])


def ask_box(items: list, today: str) -> str:
    """The ask box, on the front page, with the essay taken off it.

    IT USED TO BE ITS OWN PAGE BEHIND ITS OWN NAV TAB, under a heading, a lede, and four
    paragraphs explaining what a search field is. A reader who has to navigate to a search
    field in order to use it mostly does not, and the copy around it was written for
    somebody deciding whether to trust the box rather than for somebody with a question.

    So the field is the first thing under the hero and the words are gone, except one line.
    That line stays because "nothing is sent anywhere" is the one thing about this box a
    reader cannot see by looking at it, and it is the whole reason it works on a phone with
    no signal in a county meeting room.

    The index and the catalogue still ship inline, so the box answers with no request.
    """
    idx = ask_answers.index(items, today)
    cat = ask_answers.catalogue(idx)
    starters = [c["q"] for c in cat if c["route"]["view"] in ("open_now", "counts")][:1] + \
               [c["q"] for c in cat if c["route"]["view"] == "by_metro"][:1] + \
               [c["q"] for c in cat if c["route"]["view"] == "by_topic"][:1]
    chips = "".join(f'<button type="button" data-ask="{e(q)}">{e(q)}</button>'
                    for q in starters)
    return f"""
<section class="asksection" data-reveal>
  <div id="ask" class="askbox lean" data-base="">
    <form role="search">
      <label class="vh" for="askq">Ask the record a question</label>
      <input id="askq" type="search" autocomplete="off"
             placeholder="Ask about any AI decision in Texas">
      <button type="submit"><span class="vh">Ask</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 19V5M5 12l7-7 7 7"/></svg></button>
    </form>
    <div class="chips" data-voice="reader">{chips}</div>
    <div class="answer" hidden></div>
  </div>
</section>

<script>window.__ASK_INDEX__={json.dumps(idx, separators=(",", ":"))};
window.__ASK_CATALOGUE__={json.dumps(cat, separators=(",", ":"))};</script>
<script>{ask_answers.engine_js()}</script>
"""


def water_page(today: str) -> str:
    """The Texas Water Watch. The grid watch's sibling, and the other half of the account.

    Same numeral gate, same refusal to publish a verdict, same build time raise. A data center
    draws on electricity and on water, and a site that tracked only the first would be telling
    half of the story it claims to keep.
    """
    recs = waterwatch_page.load()
    body = waterwatch_page.body(recs, today)
    stray = waterwatch_page.lint(body, waterwatch_page.figures(recs))
    if stray:
        raise SystemExit(
            "site_build: the water watch page carries numerals that trace to no computation: "
            + ", ".join(stray[:12]))
    return page(title=f"Texas Water Watch · {SITE_NAME}", depth=1, active="water/",
                desc="Water held in Texas reservoirs, by metro, measured daily. The Permian "
                     "metros nearest the new load hold the least.",
                body=body, today=today, canonical="water/",
                extra_ld=[{
                    "@context": "https://schema.org", "@type": "Dataset",
                    "name": "Texas Water Watch",
                    "description": "Daily conservation storage for every monitored Texas "
                                   "reservoir, rolled up statewide and by metro. Out of state "
                                   "reservoirs and flood control dams are excluded and the "
                                   "exclusions are recorded.",
                    "url": f"{SITE_URL}/water/",
                    "license": "https://creativecommons.org/licenses/by/4.0/",
                    "creator": {"@type": "Organization", "name": SITE_NAME},
                    "distribution": [{"@type": "DataDownload",
                                      "encodingFormat": "application/json",
                                      "contentUrl": f"{SITE_URL}/waterwatch.json"}],
                    "isAccessibleForFree": True,
                    "temporalCoverage": (f'{recs[0]["date"]}/{recs[-1]["date"]}'
                                         if recs else today),
                }])


# The contact form posts to FormSubmit, because a Pages site has no backend. The action is
# FormSubmit's opaque alias for the docket mailbox named in CLAUDE.md, which keeps the raw
# address out of the page source. It is the SAME alias the sibling product uses, because it
# is the same mailbox and it is already activated. `_subject` tells the two apart in the
# inbox. The domain is deliberately not spelled here: the residue check reads this file.
FORM_ACTION = "https://formsubmit.co/228f72bce4f9b0e50b49d8d501374771"


def scan_page(today: str) -> str:
    """The Bottleneck Scanner, the free front door under the paid ladder.

    THE PAGE IS THE CONTRACT. Every promise in this copy is something the scanner routine in
    the sibling repo actually holds: one report, to one address, no list, no second message,
    nothing published. If this copy and that routine ever disagree, this is what the requester
    agreed to and the routine is what is wrong.

    NO DIGITS IN THIS COPY, deliberately. `numeral_lint` refuses a numeral the build did not
    compute, and every number this page wants to say is a promise rather than a measurement.
    So the promises are written in words and the page states no figures at all.

    SECOND PERSON THROUGHOUT, per the house rule. A page about somebody else's operation that
    keeps saying "we" is talking about itself.
    """
    body = f"""
<section class="hero" data-reveal>
  <h1>See where AI would actually help you</h1>
  <p class="sub">Give us a website. What comes back is an honest map of where AI would carry
  real load in that operation, where ordinary software does the same job cheaper and safer,
  and where it has no business at all.</p>
</section>

<section data-reveal>
  <h2>What comes back</h2>
  <div class="cards">
    <div class="card"><h3>Sourced to your own pages</h3><p>Every line traces to a page on your
    site, linked so you can check it. Nothing is inferred from another business and nothing is
    invented. If the public site is too thin to say something true, the report says that
    instead.</p></div>
    <div class="card"><h3>The honest no, included</h3><p>Most operations have a pocket where a
    scale already counts it, or a person clears it in a couple of minutes. Those get marked as
    leave-it-alone, and they are the reason the rest of the report is worth reading.</p></div>
    <div class="card"><h3>What your industry already published</h3><p>What operators in the same
    line of work have published about trying the same thing, and where it got rolled back.
    Their results, cited and linked, never dressed up as a forecast about you.</p></div>
  </div>
</section>

<section id="start" data-reveal>
  <h2>Ask for one</h2>
  <p class="sub">One report, to one address. No list, no follow-up sequence, no second email.</p>
  <form class="leadform" action="{FORM_ACTION}" method="POST">
    <input type="hidden" name="_subject" value="Texas AI Docket, bottleneck scan request">
    <input type="hidden" name="_captcha" value="false">
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
    <label class="vh" for="sc-site">Your website</label>
    <input id="sc-site" name="website" type="text" inputmode="url" required
      placeholder="Your website">
    <label class="vh" for="sc-mail">Where the report should go</label>
    <input id="sc-mail" name="email" type="email" required
      placeholder="Where the report should go">
    <label class="vh" for="sc-book">Booking page, optional</label>
    <input id="sc-book" name="booking_url" type="text" inputmode="url"
      placeholder="Booking or scheduling page, optional">
    <label class="vh" for="sc-jobs">Careers page, optional</label>
    <input id="sc-jobs" name="jobs_url" type="text" inputmode="url"
      placeholder="Careers page, optional">
    <label class="vh" for="sc-note">Anything worth knowing</label>
    <textarea id="sc-note" name="message" rows="3"
      placeholder="Anything worth knowing, optional"></textarea>
    <button class="cta solid" type="submit">Send it</button>
  </form>
  <p class="fine">A person reads every report before it goes out, so this takes a day or two
  rather than seconds. Your report is not published anywhere and is not shown to anyone else.
  It reads what is public, so it can't see a billing system or a call volume, and it says so
  where that matters. If it turns out to be worth going further, the
  <a href="../services/">Field Study</a> is what goes deeper.</p>
</section>
"""
    return page(title=f"Bottleneck scan · {SITE_NAME}", depth=1, active="",
                desc="An honest read of where AI would help a Texas business, where ordinary "
                     "software is cheaper, and what the industry has already published.",
                body=body, today=today, canonical="scan/")


def services_page(items: list, today: str) -> str:
    """The commercial wing, argued from the record rather than from adjectives.

    THE DOCKET IS THE PORTFOLIO. Every consulting page in this category says the same three
    things about rigour and none of them can be checked. This one points at a working system
    the reader is already looking at, and the counts are computed from the live record at
    build time, so the page can't claim more than the machine does.

    WRITTEN IN THE SECOND PERSON, which the house rule forces and the copy is better for. "No
    first person in published copy" rules out the whole vocabulary this page would otherwise
    reach for, and what is left is the reader and what they get, which is what a services page
    should have been about anyway.

    SHORT ON PURPOSE. The version this replaced was a table of docket statistics with no offer
    on it, and the version before that explained the philosophy at length. A page that has to
    be read twice to find the price is not a page anybody buys from.
    """
    proj = dk.project(items, today)
    c = proj["counts"]
    n_topics = len(c["by_topic"])
    stats = "".join(
        f'<div class="stat"><span class="n{" hot" if hot else ""}">{n}</span>'
        f'<span class="l">{e(label)}</span></div>'
        for n, label, hot in (
            (c["items"], "Decisions tracked", False),
            (c["claims"], "Sources quoted", False),
            (c["counties_touched"], "Counties covered", False),
            (n_topics, "Beats watched daily", True),
        ))

    caps = "".join(
        f'<div class="cap"><span class="k">{k}</span><h3>{h}</h3><p>{t}</p></div>'
        for k, h, t in (
            ("Answer", "Voice and chat that never sleeps",
             "Every call picked up. Every job booked. 2am in February and through the "
             "August rush."),
            ("Retrieve", "Assistants that know your files",
             "Twenty years of contracts and permits. Answers with the source attached."),
            ("Automate", "Workflows that run themselves",
             "Invoicing and scheduling. Data entry and reporting. The busywork moves itself."),
            ("Draft", "The paperwork engine",
             "Proposals and bids drafted in hours. Permits and filings too. Texas runs on "
             "paperwork."),
            ("Employ", "Digital employees",
             "The hire you couldn't make. A named agent with a real job description. On shift "
             "around the clock."),
            ("Connect", "The whole back office",
             "Connected agents running your operation together. Wired into the tools you "
             "already pay for."),
        ))

    offers = "".join(
        f'<div class="offer{" lead" if lead else ""}">'
        f'<span class="tag">{e(when)}</span>'
        f'<h3>{h}</h3><p>{t}</p>'
        f'<p class="terms">{terms}</p></div>'
        for h, when, t, terms, lead in (
            ("The Field Study", "1 to 2 weeks",
             "Your operation studied from the inside and your competitors from the outside. "
             "Then a ranked map of where AI actually pays for you. Most firms sell a slide "
             "deck here. You get a working prototype of the best bet.",
             "That answer comes back even if AI doesn't pay in your business yet.", True),
            ("The Build", "Live inside a month, typically",
             "Whatever the Field Study surfaces, or what you already know you want. Shipped "
             "to production behind real quality gates. Improved on a schedule after that.",
             "Every build ends with something you own.", False),
            ("The Partnership", "Ongoing",
             "An embedded engineer and standing AI leadership. Built for owners who want to "
             "win the AI front of their industry without becoming engineers.",
             "On the hook for the outcome, not the deliverable.", False),
        ))

    body = f"""
<section class="hero rise">
  <h1>Texas is where it gets <em>built</em>.</h1>
  <p class="herolede">The data centers. The load. The water. It is all landing here first.
  The businesses that move first will own the decade.</p>
  <div class="ctarow">
    <a class="cta solid" href="#start">Start here</a>
    <a class="cta ghost" href="#ways">See the three ways in</a>
  </div>
</section>

<section data-reveal>
  <h2>The proof is the site you are on</h2>
  <p class="sub">Every figure below is counted from the live record at the moment this page was
  built. It moves when the work does.</p>
  <div class="statrow">{stats}</div>
</section>

<section data-reveal>
  <h2>What gets built</h2>
  <p class="sub">If the work happens on a screen it can probably be built. Bring a specific ask
  or let the Field Study find the highest payers.</p>
  <div class="capgrid">{caps}</div>
</section>

<section id="ways" data-reveal>
  <h2>Three ways in</h2>
  <p class="sub">Every engagement ends with something you own. Scope and price are set on a
  call against your numbers.</p>
  <div class="offers">{offers}</div>
</section>

<section data-reveal>
  <h2>The shop runs on what it sells</h2>
  <p class="sub">You are not the test case.</p>
  <div class="capgrid">
    <div class="cap"><span class="k">In public</span><h3>This site ships itself</h3>
      <p>The record, the deck and the video all ship from an autonomous studio. You are
      reading the proof of work.</p></div>
    <div class="cap"><span class="k">In production</span><h3>Systems running now</h3>
      <p>Content engines and event pipelines. Multi-agent systems too. All of it behind
      quality gates and approval steps.</p></div>
    <div class="cap"><span class="k">Self improving</span><h3>The machine upgrades itself</h3>
      <p>After every run the studio studies what hurt and ships fixes to its own machinery.
      What you own gets the same habit.</p></div>
  </div>
</section>

<section id="start" data-reveal>
  <h2>Start here</h2>
  <p class="sub">Say what the work is. A reply comes inside one business day.</p>
  <p class="sub">Not ready for that yet, and want to see the thinking first. The
  <a href="../scan/">bottleneck scan</a> is free, and it reads your own site and says
  where AI would and would not help.</p>
  <form class="leadform" action="{FORM_ACTION}" method="POST">
    <input type="hidden" name="_subject" value="Texas AI Docket, services enquiry">
    <input type="hidden" name="_captcha" value="false">
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
    <label class="vh" for="lf-name">Your name</label>
    <input id="lf-name" name="name" type="text" placeholder="Your name" required>
    <label class="vh" for="lf-co">Company</label>
    <input id="lf-co" name="company" type="text" placeholder="Company">
    <label class="vh" for="lf-mail">Email</label>
    <input id="lf-mail" name="email" type="email" placeholder="Email" required>
    <label class="vh" for="lf-msg">What is the work</label>
    <textarea id="lf-msg" name="message" rows="4" required
      placeholder="What is the work and what would a win look like"></textarea>
    <button class="cta solid" type="submit">Send it</button>
  </form>
</section>
"""
    return page(title=f"Services · {SITE_NAME}", depth=1, active="services/",
                desc="AI systems built for Texas businesses by the desk that publishes the "
                     "Texas AI Docket. Three ways in, priced on a call.",
                body=body, today=today, canonical="services/")


def about_page(today: str) -> str:
    """Who this is and what it is for, in the second person the house rule forces.

    MODELLED ON THE SIBLING PRODUCT'S SHAPE and not its voice. That page is written in the
    first person, which this one can't use, so every commitment is stated as what a client
    gets rather than as what the desk promises. It reads harder that way, which is the right
    direction for a page whose whole job is telling somebody what they can hold you to.
    """
    body = """
<section class="hero rise">
  <h1>Built for the <em>Lone Star State</em>.</h1>
  <p class="herolede">Texas AI Docket is a daily publication about artificial intelligence in
  Texas and an AI studio that builds for Texas businesses. One desk, two jobs.</p>
</section>

<div class="prose" data-reveal>
  <h2>What this is</h2>
  <p>AI is arriving in Texas the way oil and rail once did. As land. As load. As water
  rights. As filings nobody reads until the concrete is poured. The docket tracks those
  decisions one at a time with the source attached, so a Texan can see it coming.</p>
  <p>The same desk runs a working AI studio. Agentic systems and digital employees.
  Paperwork engines and assistants trained on a company's own files. That work lives on the
  <a href="../services/">services page</a>. Writing the beat every morning is exactly why the
  studio knows what actually pays.</p>

  <h2>Who runs it</h2>
  <p>Founded and run by <a href="https://www.linkedin.com/in/talonsturgill">Talon
  Sturgill</a>, also lead AI engineer for a large lab serving enterprise clients. That
  expertise gets pointed at Texas businesses who rarely get access to it.</p>

  <h2>How the work gets verified</h2>
  <p>Every fact carries a claim id and traces to a document that was actually fetched. At
  least one source on every item has to be the filing or the statute or the agency itself
  rather than a story about it. Nothing enters <a href="../record/">the record</a> without
  that. An item that can't be re-verified says so on its own page.</p>
  <p>Every numeral is produced by code from data. A build gate fails on any figure that
  can't be traced to a computation. Where something is genuinely not public, the size of the
  gap gets published instead of an estimate.</p>

  <h2>What you can hold this desk to</h2>
  <p><strong>Your outcome outranks the invoice.</strong> The recommendation is what this desk
  would do in your seat with its own money. Sometimes that is a smaller build than you asked
  about. Sometimes it is the honest no. You get the same answer either way.</p>
  <p><strong>Plain talk both directions.</strong> Bad news arrives early and in plain words.
  No soft version. No jargon fog. No risk buried in an appendix. Same expected back. A client
  who says it straight gets problems fixed while they are still small.</p>
  <p><strong>The build gets guarded even from the brief.</strong> Most AI projects die of
  enthusiasm. The wrong first system built too big on data that was not ready. Watching that
  happen across an industry every morning is how you learn where the road washes out. When the
  exciting ask and the right build disagree, you will hear about it. That judgement is most of
  what you are paying for.</p>
  <p><strong>Nobody chases this desk.</strong> A note gets a reply inside one business day and
  usually sooner. A person reads everything and the machines are on shift around the clock.</p>

  <h2>Where to find it</h2>
  <p>The record, the <a href="../articles/">articles</a> and the
  <a href="../videos/">videos</a> live here. For the studio, start at
  <a href="../services/">services</a>.</p>
</div>
"""
    return page(title=f"About · {SITE_NAME}", depth=1, active="about/",
                desc="Texas AI Docket is a daily publication on AI in Texas and an AI studio "
                     "building for Texas businesses.",
                body=body, today=today, canonical="about/")


def item_markdown(it: dict, today: str) -> str:
    """A clean Markdown twin of every item.

    THIS IS THE HIGHEST VALUE THING ON THE SITE FOR A MACHINE READER, and almost nobody ships
    it. A crawler that can fetch Markdown gets the record without parsing HTML, and a model
    quoting a figure out of a fenced source block is far less likely to mangle it than one
    reading it out of a rendered table. It also costs almost nothing to produce.
    """
    g = it.get("geography") or {}
    where = ("Statewide" if g.get("statewide")
             else ", ".join(g.get("counties") or [])
             or ("ERCOT region" if g.get("on_ercot") else "Texas"))
    pa = it.get("public_access") or {}
    lines = [
        f'# {it["title"]}', "",
        it["summary"], "",
        f'- Topic: {it["topic"]}',
        f'- Decided by: {it["decider"]["name"]} ({it["decider"]["type"]})',
        f'- Where: {where}',
        # THE METRO LINE IS IN THE HTML, SO IT IS HERE. The twin is the record as a machine
        # reads it, and a twin that carries a narrower answer than the page is a second
        # vocabulary for the same question, which is the drift `places.py` exists to stop.
        #
        # A SUB LIST RATHER THAN A COMMA JOIN, because every OMB area name ENDS in ", TX".
        # Joined with commas, seven areas read as fourteen fields and nothing downstream
        # can split them back. County names carry no comma, which is why `Where` above can.
        *(["- Statistical areas:"] + [f"  - {m}" for m in _item_metros(it)]
          if _item_metros(it) else []),
        f'- Status: {it["status"]}',
        f'- Public access: {room_label(pa.get("room", ""))}',
    ]
    if pa.get("closes"):
        lines.append(f'- Comment closes: {pa["closes"]}')
    if pa.get("url"):
        lines.append(f'- Take part: {pa["url"]}')
    lines += ["", f'- Last checked: {it["last_verified"]}', "", "## Dates", ""]
    for k in sorted(it.get("key_dates", []), key=lambda d: d["date"]):
        lines.append(f'- {k["date"]} · {k["kind"].replace("_", " ")}'
                     + (f': {k["note"]}' if k.get("note") else ""))
    lines += ["", "## Evidence", "",
              "Every fact above rests on one of these. The words are the source's own.", ""]
    for c in it.get("claims", []):
        lines += [f'### {c["text"]}', "",
                  "> " + c["verbatim_quote"].replace("\n", " "), "",
                  f'Source ({c.get("source_type", "")}): {c["source_url"]}', ""]
    return "\n".join(lines) + "\n"


def atom(items: list, today: str) -> str:
    def entry(it):
        url = f'{SITE_URL}/item/{it["id"]}/'
        return (f"<entry><title>{e(it['title'])}</title>"
                f'<link href="{url}"/><id>{url}</id>'
                f"<updated>{it['last_verified']}T00:00:00Z</updated>"
                f"<summary>{e(it['summary'])}</summary></entry>")
    latest = max((i["last_verified"] for i in items), default=today)
    rows = "".join(entry(i) for i in
                   sorted(items, key=lambda i: i["last_verified"], reverse=True))
    return (f'<?xml version="1.0" encoding="utf-8"?>'
            f'<feed xmlns="http://www.w3.org/2005/Atom">'
            f"<title>{e(SITE_NAME)}</title>"
            f'<link href="{SITE_URL}/"/><link rel="self" href="{SITE_URL}/atom.xml"/>'
            f"<id>{SITE_URL}/</id><updated>{latest}T00:00:00Z</updated>"
            f"{rows}</feed>")


def feed_json(items: list, today: str) -> str:
    return json.dumps({
        "version": "https://jsonfeed.org/version/1.1",
        "title": SITE_NAME, "home_page_url": f"{SITE_URL}/",
        "feed_url": f"{SITE_URL}/feed.json",
        "description": "A fact-checked record of AI decisions in Texas.",
        "items": [{
            "id": f'{SITE_URL}/item/{i["id"]}/',
            "url": f'{SITE_URL}/item/{i["id"]}/',
            "title": i["title"], "content_text": i["summary"],
            "date_modified": f'{i["last_verified"]}T00:00:00Z',
            "tags": [i["topic"]],
        } for i in sorted(items, key=lambda i: i["last_verified"], reverse=True)],
    }, indent=2, ensure_ascii=False) + "\n"


def llms_txt(items: list, today: str) -> str:
    """Published as cheap hygiene, and nothing on this site claims it does more.

    No major AI crawler documents that it reads /llms.txt. Google, Anthropic and Perplexity all
    name robots.txt as the control surface and none mention it. It is a community proposal, not
    a standard. Publishing costs one generated file from a build that already holds the index in
    memory; claiming it works would be exactly the unverifiable assertion this project refuses.
    """
    rows = "\n".join(f'- [{i["title"]}]({SITE_URL}/item/{i["id"]}/index.md): '
                     f'{i["summary"][:110]}' for i in items)
    return (f"# {SITE_NAME}\n\n"
            f"> A public, fact-checked record of decisions about artificial intelligence in "
            f"Texas. Every entry carries verbatim quotes from the sources it rests on, and at "
            f"least one primary source. Every numeral is computed from data, never written by "
            f"a person.\n\n"
            f"## The record\n\n{rows}\n\n"
            f"## Data\n\n"
            f"- [The whole record as JSON]({SITE_URL}/docket.json)\n"
            f"- [Atom feed]({SITE_URL}/atom.xml)\n"
            f"- [JSON feed]({SITE_URL}/feed.json)\n")


def docket_dataset_ld(items: list, today: str) -> dict:
    """Dataset is the one structured-data type with a documented, currently operating consumer.
    FAQPage was retired in May 2026 and SpecialAnnouncement deprecated in July 2025."""
    dates = sorted(k["date"] for it in items for k in it.get("key_dates", []))
    return {
        "@context": "https://schema.org", "@type": "Dataset",
        "name": f"{SITE_NAME}: AI decisions in Texas",
        "description": ("A fact-checked record of decisions about artificial intelligence in "
                        "Texas. Every entry carries verbatim quotes from primary sources."),
        "url": f"{SITE_URL}/", "license": "https://creativecommons.org/licenses/by/4.0/",
        "creator": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
        "spatialCoverage": {"@type": "Place", "name": "Texas, United States"},
        "temporalCoverage": f"{dates[0]}/{dates[-1]}" if dates else today,
        "dateModified": today,
        "variableMeasured": ["decision status", "key dates", "public access window",
                             "deciding body", "county"],
        "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json",
                          "contentUrl": f"{SITE_URL}/docket.json"}],
    }


# --------------------------------------------------------------------------- build
def _identifier_numerals(text: str) -> set:
    """Numerals inside the spans the RECORD layer has already vetted as identifiers.

    NOT A SECOND OPINION. `docket_build.gate_numerals` is the authority on whether a
    numeral in the record is a figure or an identifier, and it decides by stripping six
    named spans before it looks. A statute section, a bill citation, a bare year, an item
    id, a hearing room and an ordinal date are identifiers there. Re-deciding that here
    would put two rules in the repository that answer the same question, which is how "the
    Austin metro" came to mean two things on two pages, so this inherits the judgement by
    running the record layer's own regexes.

    What is deliberately NOT inherited is the figure itself. A quantity in reader copy
    still has to trace to a computation or a quote.
    """
    out = set()
    # `dk.LOCATORS` is the rest of an address, added when the record grew a beat whose whole
    # subject is where to go and who to call. Spread from the record layer's own tuple rather
    # than listed again here, so a locator this project recognises is a locator on every
    # surface and there is still exactly one place that decides.
    for rx in (dk.ITEM_ID, dk.DATE_ORDINAL, dk.CITATION, dk.PLACE_NUMBER,
               *dk.LOCATORS, dk.DOTTED_SECTION, dk.YEAR):
        for m in rx.finditer(text):
            for n in dk.NUMERAL.findall(m.group(0)):
                out.add(n)
                out.add(n.replace(",", "").rstrip("%"))
    return out


def _item_numerals(it: dict) -> set:
    """One item's own figures, for the pages that render THAT item and no others.

    PER ITEM, because the record's set is the union of thirteen items and unioning it
    site wide is the mistake `_watch_numerals` documents, one order of magnitude down. A
    Federal Register document number quoted by one item is not a licence to print that
    number on another item's page.

    A CLAIM'S SOURCE TITLE IS THE SOURCE'S WORDS. "PUCT Interchange, Filings for 58000,
    item 64, party ERCOT" is a citation rendered verbatim, in the same class as the
    verbatim quote beside it, and neither is this page choosing a number. The claim's own
    `text` is NOT included, because that sentence is written rather than fetched and its
    figures belong in a quote.
    """
    a = numeral_lint.Authorised()
    a.add(it["id"], *str(it["id"]).split("-"))
    for field in ("title", "summary"):
        a.add(*_identifier_numerals(str(it.get(field, ""))))
    a.add(*_identifier_numerals(str((it.get("public_access") or {}).get("how", ""))))

    for c in (it.get("claims") or []):
        for field in ("verbatim_quote", "source_title"):
            for n in dk.NUMERAL.findall(str(c.get(field, ""))):
                a.add(n, n.replace(",", "").rstrip("%"))
        a.add(*_identifier_numerals(str(c.get("text", ""))))
    for kd in (it.get("key_dates") or []):
        a.add(kd.get("date"), *str(kd.get("date", "")).split("-"))
        a.add(*_identifier_numerals(str(kd.get("what", "")) + " " + str(kd.get("note", ""))))

    # THE CONTROL NUMBER A READER NEEDS IN ORDER TO ACT. `public_access.how` says which
    # docket to file under, and that number is the single most consequential string on the
    # page. It is an identifier taken from the filing system, and it is authorised only
    # where a claim's source metadata carries the same digits, so a number typed into that
    # sentence and matching nothing in the evidence still fails.
    return a.set


def _home_numerals(items: list, today: str) -> set:
    """What the front page computes at render time, authorised by the same calls.

    The strip and the counter both format at the moment they draw, and neither form is
    what `_authorised_numerals` holds. The share is a ratio the record does not carry, and
    the open-doors counter is zero padded for the display, so `3` was authorised and `03`
    was what shipped.
    """
    a = numeral_lint.Authorised()
    # THE CHIP AND ITS DATE ARE ONE STATEMENT AND ONE CALL AUTHORISES BOTH. The date comes
    # from the weather ledger rather than from this build's `today`, and for as long as the
    # two matched nothing objected. The day a collector recovered a reading the site had not
    # been rebuilt for, the strip carried a day number no computation on this page had
    # produced. `frontchip.figures` returns exactly the numerals the chip prints, its own
    # self-test proves that set is neither short nor long, and the day is one of them.
    chip = frontchip.reading(_dt.date.fromisoformat(today))
    if chip:
        a.add(*frontchip.figures(chip))
    a.add(f"{len(dk.project(items, today)['actionable_now']):02d}")
    # THE PUBLISHED-WORK COUNTS, zero padded the way the row prints them. `02d` of zero is
    # "00", which is not "0", and the row prints three of them.
    a.add(f"{len(load_runs()):02d}", f"{video_count():02d}", len(load_runs()), video_count())
    return a.set


def _authorised_numerals(items: list, today: str) -> set:
    """Every numeral this build is entitled to print, assembled from what it computed.

    ASSEMBLED, NOT DECLARED. A hand-written allowlist drifts away from the pages the
    moment either changes, and the drift is invisible because both halves still look
    reasonable. So this walks the same projection the pages render from, plus the record
    itself, and a page may print exactly what the build worked out.

    Dates, years and statute citations are identifiers rather than measurements and are
    already stripped by `docket_build`'s numeral rules at the record layer. Here they are
    authorised explicitly, because a page prints them as text and the scanner cannot tell
    a section number from a quantity by looking at it.
    """
    proj = dk.project(items, today)
    a = numeral_lint.Authorised()
    tx = _place_facts()
    a.add(*tx.values())
    a.add(*_made_at_numerals())            # the colophon coordinate, on every page

    c = proj["counts"]
    a.add(c["items"], c["claims"], c["counties_touched"], c["metros_touched"],
          c["counties_touched_outside_any_metro"])
    a.add(*c["by_topic"].values(), *c["by_status"].values(), *c["by_room"].values())
    a.add(*proj["by_county"].values(), *proj["unmetroed_counties"].values())
    for m in proj["by_metro"].values():
        a.add(len(m["items"]), len(m["counties"]), len(m["touched_counties"]),
              len([x for x in m["counties"] if x not in m["touched_counties"]]), m["code"])
    for act in proj["actionable_now"]:
        a.add(act["days_left"], act["closes"], *str(act["closes"]).split("-"))

    for it in items:
        a.add(it["id"], len(it.get("claims") or []), len(it.get("key_dates") or []),
              len((it.get("geography") or {}).get("counties") or []))
        for src in (it.get("claims") or []):
            for m in dk.NUMERAL.findall(str(src.get("verbatim_quote", ""))):
                a.add(m, m.replace(",", "").rstrip("%"))
        for kd in (it.get("key_dates") or []):
            a.add(kd.get("date"), *str(kd.get("date", "")).split("-"))
        for field in ("title", "summary"):
            for m in dk.CITATION.findall(str(it.get(field, ""))):
                a.add(m)
    a.add(today, *today.split("-"), _dt.date.fromisoformat(today).day)

    # THE RENDERED FORM, not just the ISO one. `short_date` prints "SEP 8" for
    # 2026-09-08, and "8" is not "08", so authorising the ISO parts alone left every
    # single-digit deadline looking like a typed figure. Authorise what a reader sees.
    for it in items:
        for d in [(it.get("public_access") or {}).get("closes")] + \
                 [k.get("date") for k in (it.get("key_dates") or [])]:
            try:
                dd = _dt.date.fromisoformat(str(d))
            except (TypeError, ValueError):
                continue
            a.add(dd.day, f"{dd.day:02d}", dd.year, ordinal(dd).split()[-1].rstrip("stndrh"))

    # Statewide items are counted on several pages, and the count is a computation.
    a.add(sum(1 for i in items if (i.get("geography") or {}).get("statewide")))

    return a.set


def _watch_numerals(mod) -> set:
    """One watch page's own authorised set, kept SEPARATE from the record's.

    THE FIRST VERSION MERGED THESE INTO THE SITE-WIDE SET AND THAT MADE THE GATE
    VACUOUS. The grid watch authorises an hourly series and a full fuel mix, which is
    several hundred figures spanning every magnitude a page might print. Union them with
    everything else and almost any three to five digit number is authorised somewhere on
    the site, so a numeral typed into a docket page passes because an unrelated megawatt
    reading happens to match it.

    It was caught the only way it could be: by planting `8,927` into a sentence after the
    gate went green and watching the build sail through. **A gate is only as strong as
    its narrowest scope**, and the narrow scope here is the page, not the site.

    THE SECOND VERSION OF THIS FUNCTION FED THE WRONG SHAPE AND HID IT. It walked
    `mod.load()` and passed each raw reading to `mod.authorised()`, which wants the
    derived FRAME that `mod.figures()` builds. Every call raised `KeyError` on the first
    field, a bare `except Exception: pass` swallowed it, and the function returned an
    almost empty set that read as "this page authorises very little" rather than as
    "this never ran". Both watch pages then failed the site gate on their own correctly
    computed figures.

    So it goes through `figures()`, the same call the page renders from, and a failure is
    RAISED rather than absorbed. A watch page whose figures cannot be built is a broken
    page, and the build is the right place to find that out.
    """
    a = numeral_lint.Authorised()
    records = mod.load()
    if not records:
        return a.set
    a.add(*mod.authorised(mod.figures(records)))
    return a.set


def build(out: Path, today: str) -> dict:
    items = dk.load(LEDGER)
    runs = load_runs()
    bad, results = dk.run_gates(items, today)
    if bad:
        dk.report(results)
        raise SystemExit("site_build: the record does not pass its own gates; refusing to build")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    written = []
    # THE NUMERAL GATE, OVER EVERY PAGE, and it had never run over one of them.
    #
    # CLAUDE.md calls numeral_lint "a hard build gate" and says every numeral in published
    # copy must be present in the set of values the build computed. That was true of
    # exactly two pages: `gridwatch_page` and `waterwatch_page` call it on their own
    # output. `site_build` never called it at all, so the record's forty-six other pages
    # were publishing whatever their f-strings happened to contain, and the law that is
    # printed on the site as the reason to believe a number here was enforced nowhere the
    # record is actually rendered.
    #
    # It surfaced the way these always do. The first draft of the places index typed
    # "121 of 254" straight into a sentence, nothing objected, and the only reason it is
    # computed now is that writing it felt wrong. A rule you have to feel is not a rule.
    #
    # The authorised set is assembled from the projection rather than declared, so a page
    # is entitled to exactly what the build worked out and nothing else.
    authorised = _authorised_numerals(items, today)
    by_item = {it["id"]: _item_numerals(it) for it in items}
    unauthorised: list[str] = []

    def w(path: str, text: str, extra: set | None = None):
        """Write a page, and check every numeral it prints against what it may print.

        `extra` IS PER PAGE AND IS NEVER ACCUMULATED. A page gets the site-wide set plus
        whatever the items it actually renders authorise, and nothing another page earned.
        Both times this gate has been silently disabled, the cause was a set that grew
        wider than the page it was guarding.
        """
        p = out / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        written.append(path)
        if path.endswith(".html"):
            stray = numeral_lint.scan(text, authorised | (extra or set()))
            if stray:
                unauthorised.append(f"{path}: {', '.join(stray[:8])}")

    def listed(subset: list) -> set:
        """The union over exactly the items a listing page renders."""
        return set().union(*(by_item[i["id"]] for i in subset)) if subset else set()

    w("site.css", theme.css())

    # THE FILM GRAIN, as its own asset. It used to be a 12 KB base64 data URI inside site.css,
    # which is close to incompressible and sat in the middle of a render blocking download, so a
    # decorative texture was delaying first paint on every page. Written from the generator rather
    # than copied, because it is computed from three named constants and is byte-deterministic.
    (out / theme.GRAIN_FILE).write_bytes(grain.png())
    written.append(theme.GRAIN_FILE)

    # THE TYPE. Copied verbatim from the committed subsets rather than generated here: the
    # byte-equal rebuild guarantee cannot depend on a compression library's version, and a copy
    # is deterministic where a subsetting run is not. See scripts/site/fonts_build.py, which
    # exists because brand.yaml named three faces, the stylesheet wrote them into every font
    # stack, and nothing served them, so every reader got Georgia and system-ui instead.
    (out / "fonts").mkdir(parents=True, exist_ok=True)
    for face in fonts_build.manifest()["faces"]:
        shutil.copyfile(fonts_build.WEB / face["file"], out / "fonts" / face["file"])
        written.append(f'fonts/{face["file"]}')
    # The licence ships beside the fonts, because the repository is public and all three faces
    # are redistributed under the Open Font License.
    shutil.copyfile(fonts_build.WEB / "OFL.txt", out / "fonts" / "OFL.txt")
    written.append("fonts/OFL.txt")

    w("index.html", home(items, today), _home_numerals(items, today) | listed(items))
    w("docket.json", json.dumps({"_spec": {"generated": today}, "items": items},
                                indent=2, ensure_ascii=False) + "\n")
    for it in items:
        w(f'item/{it["id"]}/index.html', item_page(it, today), by_item[it["id"]])
        # The Markdown twin. A crawler that fetches this gets the record without parsing HTML,
        # and a model quoting from it is far less likely to mangle a figure.
        w(f'item/{it["id"]}/index.md', item_markdown(it, today))
    w("atom.xml", atom(items, today))
    w("feed.json", feed_json(items, today))
    w("llms.txt", llms_txt(items, today))
    w("record/index.html", docket_index(items, today), listed(items))
    for t in sorted({i["topic"] for i in items}):
        w(f"topic/{t}/index.html", topic_page(t, items, today),
          listed([i for i in items if i["topic"] == t]))
    w("articles/index.html", articles_page(runs, today))
    w("videos/index.html", videos_page(today))
    # THE FEED ITSELF IS EXTERNAL DATA and is copied through byte for byte. It is written by
    # `TexasAIDispatch` and `ownership.yaml` gives it to that actor, so no build here may
    # write it, reformat it, or invent one when it is missing.
    feed_src = REPO_ROOT / "docs" / "videos" / "videos.json"
    if feed_src.exists() and feed_src.resolve() != (out / "videos" / "videos.json").resolve():
        (out / "videos").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(feed_src, out / "videos" / "videos.json")
        written.append("videos/videos.json")
    for r in runs:
        w(f'articles/{r["date"]}/index.html', article_page(r, today))
    # PER PLACE. The index, then a page for every metro the record touches and every
    # touched county that is in no metro. Nothing falls between the two.
    for pl in all_places(items, today):
        w(f'place/{pl["id"]}/index.html', place_page(pl, items, today),
          listed([i for i in items if i["id"] in set(pl["items"])]))
    w("grid/index.html", grid_page(today), _watch_numerals(gridwatch_page))
    # The grid watch as open data, in the same shape the page was built from. A reader who
    # doubts a figure here can recompute it without refetching anything from ERCOT.
    w("gridwatch.json", json.dumps(
        {"_spec": {"generated": today,
                   "note": "One settled ERCOT day per record. Hourly series included so every "
                           "published figure is recomputable. Unverified days carry no "
                           "numbers rather than yesterday's."},
         "readings": gridwatch_page.load()}, indent=2, ensure_ascii=False) + "\n")
    # The catalogue size is the one figure this page states, and it is the length of the
    # list the page is shipping. It passed the gate before the metro questions existed
    # only because the count was 121 and the state has 121 counties in no metro, which is
    # the coincidence `numeral_lint`'s docstring admits it cannot see through.

    w("scan/index.html", scan_page(today))
    w("services/index.html", services_page(items, today))
    w("water/index.html", water_page(today), _watch_numerals(waterwatch_page))
    w("waterwatch.json", json.dumps(
        {"_spec": {"generated": today,
                   "note": "One day per record, per reservoir, so every roll up is "
                           "recomputable. Out of state reservoirs and flood control dams with "
                           "no conservation pool are excluded, and both exclusions are named "
                           "in each record."},
         "readings": waterwatch_page.load()}, indent=2, ensure_ascii=False) + "\n")
    # The heat clock as open data, on the same terms as the other two series. It has no page
    # of its own, because it is one line at the top of the front page rather than a subject,
    # so the data page is where a reader finds it.
    w("weather.json", json.dumps(
        {"_spec": {"generated": today,
                   "note": "Observed daily maximum and minimum at one anchor station, from "
                           "NCEI daily summaries. A day with no observation is absent rather "
                           "than zero. Normals are the 1991 to 2020 period computed from the "
                           "same record and shipped beside it."},
         "normals": frontchip.normals(),
         "readings": frontchip.load()}, indent=2, ensure_ascii=False) + "\n")
    w("data/index.html", data_page(items, today))
    w("about/index.html", about_page(today))

    # A permissive robots.txt is the product strategy, not a concession. For a record built to
    # be cited, blocking the crawlers that cite it would be self-defeating.
    w("robots.txt",
      "# The Texas AI Docket wants to be read, indexed, cited and learned from.\n"
      "# Content-Signal is the only machine readable way to say yes rather than no.\n"
      "Content-Signal: search=yes, ai-input=yes, ai-train=yes\n\n"
      "User-agent: *\nAllow: /\n\n"
      f"Sitemap: {SITE_URL}/sitemap.xml\n")

    urls = [u for u in written if u.endswith("index.html")]
    locs = "".join(
        f"<url><loc>{SITE_URL}/{u[:-10]}</loc><lastmod>{today}</lastmod></url>"
        for u in urls)
    w("sitemap.xml",
      f'<?xml version="1.0" encoding="UTF-8"?>'
      f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{locs}</urlset>')

    # THE GATE FIRES HERE, after every page is written, so the report names all of them
    # rather than the first. A build that would publish a typed numeral does not publish.
    if unauthorised:
        for line in unauthorised:
            print(f"  numeral: {line}", file=sys.stderr)
        raise SystemExit(
            f"site_build: {len(unauthorised)} page(s) print a numeral this build did not "
            f"compute. Every published figure traces to data, which is the reason a reader "
            f"should believe one here. Compute it, or authorise it where it is computed.")

    return {"pages": len(urls), "files": len(written), "items": len(items),
            "numerals_authorised": len(authorised)}


def self_test() -> int:
    import tempfile
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    today = "2026-08-11"
    with tempfile.TemporaryDirectory() as td:
        stats = build(Path(td) / "a", today)
        check("the site builds", stats["pages"] >= 4, str(stats))
        idx = (Path(td) / "a" / "index.html").read_text(encoding="utf-8")
        # WHAT THIS PROTECTS IS THE ANSWER, NOT ONE DRAFT'S PHRASING. It used to look for the
        # literal words "still say something", which lived in the first headline, so shortening
        # the headline failed a check about whether the page answers the reader's question. The
        # question is whether somebody can still act. The page answers it with a COUNTED number
        # of ways in, marked hot so it reads first, and with the sentence that teaches what the
        # green means. Both of those are structural and survive a rewrite. A quoted fragment of
        # a headline is a copy of the copy, and it only ever fails for the wrong reason.
        check("the home page counts the ways a reader can still act",
              'class="n hot"' in idx and "Doors open to you" in idx)
        # Matched against COLLAPSED whitespace, because the lede is a multi line f-string and
        # HTML whitespace is not semantic. Searching the raw source for a phrase that wraps finds
        # nothing and reports that the page lost the sentence it is looking at.
        flat = " ".join(idx.split())
        check("...and teaches the signal that marks them",
              "Green means a door is open to you" in flat)
        check("the map is inline, so it needs no second request", "<svg class=\"txmap\"" in idx)
        check("Dataset structured data is emitted", '"@type":"Dataset"' in idx)
        check("robots says yes rather than no",
              "ai-train=yes" in (Path(td) / "a" / "robots.txt").read_text())
        check("the advertised feed exists", (Path(td) / "a" / "atom.xml").exists())
        check("a Markdown twin exists for every item",
              len(list((Path(td) / "a" / "item").rglob("index.md"))) == stats["items"])
        md = next((Path(td) / "a" / "item").rglob("index.md")).read_text(encoding="utf-8")
        check("the Markdown twin carries the source's own words", "> " in md)
        check("llms.txt claims nothing it cannot back",
              "## The record" in (Path(td) / "a" / "llms.txt").read_text(encoding="utf-8"))

        # Rule 1: docs/ is a pure function of the ledgers.
        b = Path(td) / "b"
        build(b, today)
        diff = [p for p in (Path(td) / "a").rglob("*") if p.is_file()
                and (b / p.relative_to(Path(td) / "a")).read_bytes() != p.read_bytes()]
        check("two builds are byte identical", not diff, f"{len(diff)} differ")

        # An item page must show the source's own words, or the proof is only asserted.
        items = dk.load(LEDGER)
        one = (Path(td) / "a" / "item" / items[0]["id"] / "index.html").read_text(encoding="utf-8")
        check("an item page quotes its sources", "<blockquote>" in one)

        # THE PLACE LINKS RUN BOTH WAYS. The place pages listed their items from the
        # first build and nothing pointed back, which looks correct from either end: every
        # place page is fully connected when you are standing on it. Checked here as a
        # round trip rather than as "the item page contains the word place", because the
        # thing worth guaranteeing is that a reader can get from an item to a place page
        # and find that same item waiting there.
        located = [i for i in items
                   if ((i.get("geography") or {}).get("counties") or [])]
        round_trip = []
        for i in located:
            page_html = (Path(td) / "a" / "item" / i["id"] / "index.html").read_text("utf-8")
            for pid in set(re.findall(r'href="\.\./\.\./place/([^"/]+)/"', page_html)):
                target = Path(td) / "a" / "place" / pid / "index.html"
                if not target.exists() or f'item/{i["id"]}/' not in target.read_text("utf-8"):
                    round_trip.append(f'{i["id"]} -> {pid}')
        check("every located item links to a place page that lists it back",
              located and not round_trip, f"broken: {round_trip[:3]}")
        check("...and an item with no county says so rather than linking nowhere",
              all("appears on no place page" in
                  (Path(td) / "a" / "item" / i["id"] / "index.html").read_text("utf-8")
                  for i in items if i not in located
                  and not (i.get("geography") or {}).get("statewide")))

        # THE NUMERAL GATE, PROVEN TO FIRE, AND PROVEN TO BE NARROW.
        #
        # This gate has been green and inert twice, for two unrelated reasons, and the
        # suite reported clean through both. First its per page sets were unioned into one
        # site wide set, and the grid watch's several hundred hourly and fuel mix figures
        # authorised almost any number on any page. Then, after that was fixed, the
        # scanner still deleted authorised strings as SUBSTRINGS, so the ten single digits
        # every page authorises within a few counts and dates dissolved every multi digit
        # figure on the site one character at a time.
        #
        # Neither was found by a test. Both were found by planting a figure by hand and
        # watching the build sail through. So the plant is a test now, and it plants twice:
        # once with a number nothing computed, and once with a number that IS computed on
        # a DIFFERENT page, which is the only way to catch a set that has quietly widened.
        import contextlib as _cl, io as _io
        real_docket, real_home = docket_index, home

        def planted(fn, find, ins):
            return lambda *a, **k: fn(*a, **k).replace(find, find + ins, 1)

        for label, name, real, ins, want in (
                ("a figure nothing computed", "docket_index", real_docket,
                 "<p>Roughly 8,927 megawatts.</p>", "8,927"),
                ("a figure computed on another page", "docket_index", real_docket,
                 "<p>Energy served was 1,743,297 MWh.</p>", "1,743,297"),
                ("a figure planted on the front page", "home", real_home,
                 "<p>Some 41,203 filings.</p>", "41,203")):
            anchor = "<h1>The record</h1>" if name == "docket_index" else "</h1>"
            globals()[name] = planted(real, anchor, ins)
            err, fired = _io.StringIO(), False
            try:
                with _cl.redirect_stderr(err):
                    build(Path(td) / "planted", today)
            except SystemExit:
                fired = True
            finally:
                globals()[name] = real
            check(f"the numeral gate reddens the build on {label}", fired)
            check(f"...and names {want}, so it can be found", want in err.getvalue(),
                  err.getvalue()[:200])

        check("the gate is still green once the plants are removed",
              build(Path(td) / "clean", today)["pages"] == stats["pages"])

        # NO ORPHAN PAGE BUILDERS. docket_index() shipped once defined and never called, so
        # nothing listed the whole record and no gate noticed: an unreferenced function does
        # not throw, which is the same failure mode the port audit's wiring check exists for.
        import inspect, re as _re
        src = inspect.getsource(build)
        builders = [n for n, o in globals().items()
                    if callable(o) and (n.endswith("_page") or n in {"home", "docket_index"})]
        orphans = [n for n in builders if not _re.search(rf"\b{n}\s*\(", src)]
        check("every page builder is reached by build()", not orphans, f"orphaned: {orphans}")

        # LINK DEPTH. Moving a page one directory deeper silently breaks every relative link
        # inside it, and it renders fine, so nothing notices until a reader clicks. The port
        # audit catches it repo-wide; catching it here means a broken build never gets written.
        import re as _re2
        root = Path(td) / "a"
        broken = []
        # Script blocks are stripped first. A URL built at runtime, like the ask engine's
        # "../item/" + id + "/", is not a static href and cannot be resolved by reading it.
        # The links it produces are covered instead by the data check below, which is the
        # honest way to check them: verify every id it could use, not the string that uses it.
        script = _re2.compile(r"<script\b.*?</script>", _re2.DOTALL | _re2.IGNORECASE)
        for f in root.rglob("*.html"):
            text = script.sub(" ", f.read_text(encoding="utf-8"))
            for href in _re2.findall(r'href="([^"#?:]+)"', text):
                if href.startswith(("http", "//", "mailto")):
                    continue
                t = (f.parent / href).resolve()
                if not (t.exists() or (t / "index.html").exists()):
                    broken.append(f"{f.relative_to(root)} -> {href}")
        # THE ASK ENGINE'S LINKS, CHECKED AS DATA. Every item the index can route to must
        # have a page built for it. This is what the static scan above structurally cannot do.
        ask_idx = ask_answers.index(dk.load(LEDGER), "2026-08-11")
        missing_pages = [i["id"] for i in ask_idx["items"]
                         if not (root / "item" / i["id"] / "index.html").exists()]
        check("every item the ask engine can route to has a page",
              not missing_pages, str(missing_pages[:5]))
        ask_routes = {c["route"]["view"] for c in ask_answers.catalogue(ask_idx)}
        check("every route the catalogue emits is one the engine implements",
              ask_routes <= set(ask_answers.VIEWS), str(ask_routes - set(ask_answers.VIEWS)))

        check("every relative link resolves from its own page", not broken,
              f"{len(broken)} broken, first: {broken[:1]}")
        check("an item page links the source", "rel=\"nofollow noopener\"" in one)

    if failures:
        print(f"\nsite_build self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print("\nsite_build self-test: all passed")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=str(REPO_ROOT / "docs"))
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    stats = build(Path(a.out), a.today)
    print(f"site: {stats['pages']} pages, {stats['files']} files, {stats['items']} items")
    # THE OUTSTANDING EXEMPTIONS, ON A GREEN BUILD TOO. See `docket_build.backlog`.
    for line in dk.backlog(dk.load(LEDGER)):
        print(f"  backlog: {line}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:                                       # noqa: BLE001
        print(f"site_build: broke: {exc}", file=sys.stderr)
        sys.exit(2)
