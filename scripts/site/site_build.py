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
import calendar
import datetime as _dt
import functools
import hashlib
import html
import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ask_answers                                                # noqa: E402
import ask_corpus                                                 # noqa: E402
import ask_written                                                # noqa: E402
import docket_build as dk                                          # noqa: E402
import favicon                                                     # noqa: E402
import fonts_build                                                 # noqa: E402
import indexnow                                                    # noqa: E402
import lastmod                                                     # noqa: E402
import og                                                          # noqa: E402
import schema                                                      # noqa: E402
import gridwatch_page                                              # noqa: E402
import frontchip                                                   # noqa: E402
import sky                                                         # noqa: E402
import texas_map                                                   # noqa: E402
import waterwatch_page                                             # noqa: E402
import watch_page as watch_stage                                  # noqa: E402
import grain                                                       # noqa: E402
import mark                                                        # noqa: E402
import csp                                                        # noqa: E402
import numeral_lint                                                # noqa: E402
import docket_calendar as dcal                                     # noqa: E402
import theme                                                       # noqa: E402
import facility_dossier
import entities
import registry_changes
import registry_graph
import tdlr_projects

LEDGER = REPO_ROOT / "ledger" / "docket.json"

SITE_NAME = "Texas AI Docket"
# One key drives every absolute URL, so moving to a custom domain is a one line change.
# It was one, on 2026-08-15, from https://talonsturgill.github.io/TexasAIDocket. The move cost
# nothing beyond this line and the CNAME derived from it, because every link on every page is
# document relative: 77 of them and not one root relative, so dropping a path segment off the
# front of the site moved no href at all. Only the absolute URLs built from here had to change,
# which is the canonical tag, og:url, the sitemap, the feeds and the structured data.
SITE_URL = "https://texasaidocket.com"

# --------------------------------------------------------- proving the site is ours
#
# A SEARCH ENGINE WILL NOT SHOW A SITE IT HAS NEVER BEEN TOLD ABOUT. This record shipped with
# a valid sitemap, a permissive robots.txt and structured data on every page, and did not
# appear in Google at all, because none of that is a submission. Discovery is by link, the
# domain was days old, and nothing on the indexed web pointed at it. The sitemap was never
# handed to anyone.
#
# Verification is what opens that door. It is also the only way to see what the crawler
# actually thinks: which pages are indexed, which were refused and why, and what the record
# is already being found for.
#
# DNS IS THE BETTER METHOD AND NEEDS NEITHER OF THESE. A TXT record on the domain verifies
# every subdomain and both protocols at once and cannot be lost in a rebuild. These two exist
# for the case where editing DNS is not convenient, so the token is a one line change here
# rather than a hunt through a generated page. Empty means the tag is not emitted at all,
# because an empty verification tag is worse than none: it looks done.
GOOGLE_SITE_VERIFICATION = ""     # the content= value from Search Console's HTML tag method
BING_SITE_VERIFICATION = ""       # the content= value from Bing Webmaster Tools
# THE LICENCE, AS ONE STRING. Named here because it is printed in three places and its
# version number is a numeral, so the string and the authorisation that lets it through
# the numeral gate have to come from the same constant. Written out at each call site
# they can disagree, and the failure looks like a build error rather than a typo.
LICENCE = "CC BY 4.0"

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
# BEATS AND PLACES SIT IN THE FOOTER, not the masthead. Eight items is already a full top bar
# on a phone and these are the two ways INTO the record rather than two more sections beside
# it, so the way out at the bottom of the page is where somebody who did not find what they
# came for actually looks. It also means no hub is itself an orphan, which is the fault they
# were built to fix.
# SOURCES JOINS THEM, and the masthead is still eight. The archive became a family of 51
# publisher pages on 2026-08-18 and had no link from any page on the site, which made the whole
# family reachable only from the sitemap and from `llms.txt`. It is the same kind of thing as
# Beats and Places, a way INTO the record rather than a section beside it, and the argument
# above for keeping those out of the top bar applies to this one word for word. A link in the
# footer is a link on all 221 pages, which is what the family needed and all it needed.
# `questions/` was built as one of these generated views and left out of this list, so it shipped
# with nothing on the site linking to it. It was in the sitemap and reachable by URL, which is
# exactly enough to look fine and to be unread. `link_check.py` is what found it.
FOOTNAV = NAV[1:] + [("topic/", "Beats"), ("place/", "Places"), ("sources/", "Sources"),
                     ("questions/", "Questions"), ("scan/", "Scan"), ("data/", "Data")]

# WHERE THIS RECORD IS, ELSEWHERE ON THE WEB.
#
# Two jobs from one list, and the second is the one that is easy to forget. The visible job is
# the icon row at the bottom of every page. The invisible one is `sameAs` on the Organization
# node, which is how a search engine and an answer engine learn that this site, that LinkedIn
# page and that Facebook page are ONE entity rather than three unrelated things with similar
# names. Without it the record's authority is split across three strangers.
#
# So the list is the single source and `SAME_AS` is derived from it. Adding a profile in one
# place makes it appear in the footer and in the structured data at once, and there is no way
# to add one to the row and forget the claim.
#
# THE URLS ARE CANONICAL PAGE URLS, NOT SHARE LINKS. The Facebook profile arrived as
# facebook.com/share/1EgcaoaUmG/, which works for a person clicking it and is the wrong thing
# to put in `sameAs`: a share token identifies a share, it can be rotated, and it resolves
# through a login wall. Facebook's own redirect from that token names the page, and the page is
# what goes here.
#
# The glyphs are each brand's own mark on a 24 by 24 grid, drawn as a path rather than fetched,
# because an icon font or a CDN sprite is a third party request on every page of a site that
# makes none.
SOCIALS = [
    ("LinkedIn", "https://www.linkedin.com/company/texasaidocket/",
     "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 "
     "1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 "
     "3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 "
     "0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 "
     "2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 "
     ".774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 "
     "22.271V1.729C24 .774 23.2 0 22.225 0z"),
    ("Facebook", "https://www.facebook.com/Texasaidocket",
     "M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 "
     "11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 "
     "2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 "
     "3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"),
    ("Instagram", "https://www.instagram.com/texasaidocket",
     "M12 0C8.74 0 8.333.015 7.053.072 5.775.132 4.905.333 4.14.63c-.789.306-1.459.717-2.126 "
     "1.384S.935 3.35.63 4.14C.333 4.905.131 5.775.072 7.053.012 8.333 0 8.74 0 12s.015 3.667"
     ".072 4.947c.06 1.277.261 2.148.558 2.913.306.788.717 1.459 1.384 2.126.667.666 1.336 "
     "1.079 2.126 1.384.766.296 1.636.499 2.913.558C8.333 23.988 8.74 24 12 24s3.667-.015 "
     "4.947-.072c1.277-.06 2.148-.262 2.913-.558.788-.306 1.459-.718 2.126-1.384.666-.667 "
     "1.079-1.335 1.384-2.126.296-.765.499-1.636.558-2.913.06-1.28.072-1.687.072-4.947s-.015"
     "-3.667-.072-4.947c-.06-1.277-.262-2.149-.558-2.913-.306-.789-.718-1.459-1.384-2.126C21"
     ".319 1.347 20.651.935 19.86.63c-.765-.297-1.636-.499-2.913-.558C15.667.012 15.26 0 12 "
     "0zm0 2.16c3.203 0 3.585.016 4.85.071 1.17.055 1.805.249 2.227.415.562.217.96.477 1.382"
     ".896.419.42.679.819.896 1.381.164.422.36 1.057.413 2.227.057 1.266.07 1.646.07 4.85s"
     "-.015 3.585-.074 4.85c-.061 1.17-.256 1.805-.421 2.227-.224.562-.479.96-.899 1.382-.419"
     ".419-.824.679-1.38.896-.42.164-1.065.36-2.235.413-1.274.057-1.649.07-4.859.07-3.211 "
     "0-3.586-.015-4.859-.074-1.171-.061-1.816-.256-2.236-.421-.569-.224-.96-.479-1.379-.899"
     "-.421-.419-.69-.824-.9-1.38-.165-.42-.359-1.065-.42-2.235-.045-1.26-.061-1.649-.061"
     "-4.844 0-3.196.016-3.586.061-4.861.061-1.17.255-1.814.42-2.234.21-.57.479-.96.9-1.381"
     ".419-.419.81-.689 1.379-.898.42-.166 1.051-.361 2.221-.421 1.275-.045 1.65-.06 4.859"
     "-.06l.045.03zm0 3.678c-3.405 0-6.162 2.76-6.162 6.162 0 3.405 2.76 6.162 6.162 6.162 "
     "3.405 0 6.162-2.76 6.162-6.162 0-3.405-2.76-6.162-6.162-6.162zM12 16c-2.21 0-4-1.79-4-4"
     "s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4zm7.846-10.405c0 .795-.646 1.44-1.44 1.44-.795 0-1.44"
     "-.646-1.44-1.44 0-.794.646-1.439 1.44-1.439.793-.001 1.44.645 1.44 1.439z"),
    ("YouTube", "https://www.youtube.com/@TexasAIDocket",
     "M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 "
     "0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 "
     "0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 "
     "2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 "
     "3.568z"),
    # X, AT THE ADDRESS THE PROFILE ACTUALLY LIVES AT. twitter.com/TexasAIDocket still resolves,
    # by a redirect the company runs and could stop running, and `sameAs` is a claim that should
    # survive that. The mark is the current one for the same reason: a bird would be a drawing of
    # a company that no longer exists next to a link to one that does.
    ("X", "https://x.com/TexasAIDocket",
     "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 "
     "1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z"),
    # ARRIVED AS A SHARE LINK TOO, tiktok.com/@texas.ai.docket?_r=1&_t=ZT-994j3vYObvh. The
    # query is a share session, not the profile, and it is the same mistake the Facebook URL
    # above was corrected for: it identifies who passed the link on rather than whose page it
    # is, and `sameAs` is a claim about the page.
    ("TikTok", "https://www.tiktok.com/@texas.ai.docket",
     "M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 "
     "4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 "
     "8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03"
     "-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 "
     "3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 "
     "1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 "
     "2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"),
]
SAME_AS = [url for _name, url, _path in SOCIALS]

# THE CONTACT CONTROL IS NOT A PROFILE, AND IS DELIBERATELY NOT IN `SOCIALS`.
#
# It sits in the same row and wears the same 44px target, so it belongs with them visually.
# It does NOT belong in `sameAs`, which is a claim that a given URL is this organisation
# somewhere else on the web. A page on this site is not somewhere else, and putting it there
# would be a false statement in the structured data to save one list.
#
# THE HREF IS A REAL DESTINATION, not a dead anchor waiting for script. Without JavaScript the
# link goes to the form on the services page, which reaches the same mailbox by the same route.
# With script it opens the dialog instead. A control that does nothing without JavaScript is a
# promise a reader tests once.
CONTACT = ("Send a message", "services/#start",
           "M1.5 5.25A2.25 2.25 0 0 1 3.75 3h16.5a2.25 2.25 0 0 1 2.25 2.25v.38l-10.5 "
           "6.3-10.5-6.3v-.38Zm0 2.87V18.75A2.25 2.25 0 0 0 3.75 21h16.5a2.25 2.25 0 0 0 "
           "2.25-2.25V8.12l-9.92 5.95a1.5 1.5 0 0 1-1.66 0L1.5 8.12Z")


def socials(depth: int = 0) -> str:
    """The icon row: one link per profile, then the way to send a message.

    `aria-label` NAMES THE DESTINATION, because the link's only visible content is a drawing.
    Without it a screen reader announces "link" and nothing else, which is the whole row gone.
    The mark itself is `aria-hidden`, so the name is announced once rather than twice.

    `rel="noopener"` on every profile. Those open in a new tab, and a new tab opened from a
    link gets a handle back to this page unless that is refused. The contact control opens
    nothing and stays in this tab, so it carries neither.
    """
    name, href, path = CONTACT
    icon = ('<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'<path d="{path}"/></svg>')
    return "".join(
        f'<li><a href="{url}" target="_blank" rel="noopener"'
        f' aria-label="{e(SITE_NAME)} on {e(sname)}">'
        f'<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
        f'<path d="{spath}"/></svg></a></li>'
        for sname, url, spath in SOCIALS) + (
        f'<li><a href="{rel(depth)}{href}" id="contactopen"'
        f' aria-label="{e(name)} to {e(SITE_NAME)}">{icon}</a></li>')

def contact_dialog() -> str:
    """A message to this desk, without the address being on the page.

    THE READER NEVER SEES WHERE IT GOES, and that is the point rather than a side effect. The
    action is FormSubmit's opaque alias for the mailbox, the same one the services form and the
    search feedback already post to, so the raw address appears nowhere in the served bytes and
    a scraper reading this page finds a hash. It also means no backend: there is no server to
    keep running and no secret to rotate.

    IT WEARS `askfb`, WHICH IS THE FEEDBACK DIALOG'S OWN DRESS. Not a shortcut. It is the same
    object at a different door, a small form in a dialog posting to the same endpoint, and
    giving it a second set of classes would be a second set of rules to keep in step with the
    first. The stylesheet has 513 bytes of gzip left inside the initial congestion window, so a
    duplicate would also have cost the whole site a second round trip to first paint.

    A NATIVE <dialog>. It gets focus trapping, escape to close, an inert background and the
    browser's top layer for free, and each of those is otherwise a few hundred lines of the
    kind of code that is wrong on one phone and nobody's phone is the one it was tested on.
    """
    return (
        '<dialog class="askfb" id="contactbox" aria-labelledby="contacth">\n'
        f'  <form id="contactform" method="POST" action="{FORM_ACTION}">\n'
        '    <h2 id="contacth">Send a message</h2>\n'
        '    <p class="askfbnote">It reaches the desk that publishes this record. An address '
        'below is only needed if a reply is wanted, and it is used for that and nothing '
        'else.</p>\n'
        '    <label class="askfbl" for="contactmsg">Your message</label>\n'
        '    <textarea id="contactmsg" name="message" rows="5" required></textarea>\n'
        '    <label class="askfbl" for="contactmail">Email, only if a reply is wanted</label>\n'
        '    <input id="contactmail" name="email" type="email" autocomplete="email" '
        'inputmode="email" spellcheck="false" placeholder="Optional">\n'
        '    <input type="hidden" name="_subject" value="Texas AI Docket, a message from '
        'the site">\n'
        '    <input type="hidden" name="_captcha" value="false">\n'
        '    <input type="hidden" name="_template" value="table">\n'
        # THE HONEYPOT THE OTHER TWO FORMS ALREADY CARRY. A bot fills every field it finds;
        # a reader cannot see this one, so anything in it came from something that is not one.
        '    <input type="text" name="_honey" style="display:none" tabindex="-1" '
        'autocomplete="off">\n'
        '    <p class="askfbmsg" id="contactstatus" role="status" aria-live="polite"></p>\n'
        '    <div class="askfbrow">\n'
        '      <button type="submit" class="askfbsend" id="contactsend">Send</button>\n'
        '      <button type="button" class="asklink" id="contactclose">Close</button>\n'
        '    </div>\n'
        '  </form>\n'
        '</dialog>')


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
  var read=document.getElementById('mapread'), map=document.querySelector('svg.txmap'),
      rb=document.getElementById('mapreset');
  if(!read||!map||!('ontouchstart' in window)) return;
  var moved=false, sx=0, sy=0, last=null, clearAt=0;
  // PINCH TO ZOOM, TWO FINGERS TO MOVE.
  // Even with the readout naming what is under the thumb, a county in the Panhandle is a few
  // millimetres of glass and the thumb covers all of it. So the map moves like a map.
  //
  // ONE FINGER STAYS THE PICKER and two fingers do the navigating, which is the opposite of a
  // slippy map and is right here: this drawing is a chooser, not a place to wander. One finger
  // already reads out and opens a county, and taking that away to pan would trade the working
  // interaction for a familiar one.
  //
  // THE VIEWBOX MOVES, not a transform on a group. Strokes here are `vector-effect:
  // non-scaling-stroke`, so a viewBox change keeps every hairline at its drawn weight instead
  // of fattening the borders as you zoom, and `elementFromPoint` keeps working because it asks
  // in screen coordinates either way.
  var VB={x:0,y:0,w:0,h:0}, HOME=null, MAXZ=8;
  (function(){
    var v=(map.getAttribute('viewBox')||'').split(/[ ,]+/).map(Number);
    if(v.length===4&&v.every(function(n){return !isNaN(n);})){
      HOME={x:v[0],y:v[1],w:v[2],h:v[3]}; VB={x:v[0],y:v[1],w:v[2],h:v[3]};
    }
  })();
  function apply(){
    if(!HOME) return;
    // CLAMPED SO THE MAP CANNOT BE LOST. Zooming out past the full extent and panning the
    // state off the glass are both ways to end up looking at nothing with no way back that a
    // reader would guess.
    VB.w=Math.min(HOME.w,Math.max(HOME.w/MAXZ,VB.w));
    VB.h=VB.w*(HOME.h/HOME.w);
    VB.x=Math.min(HOME.x+HOME.w-VB.w,Math.max(HOME.x,VB.x));
    VB.y=Math.min(HOME.y+HOME.h-VB.h,Math.max(HOME.y,VB.y));
    map.setAttribute('viewBox',VB.x+' '+VB.y+' '+VB.w+' '+VB.h);
    // The button is resolved once at the top with the readout, because this runs on every
    // touchmove of a pinch, roughly sixty times a second on the device with the least headroom.
    if(rb) rb.hidden=!(VB.w<HOME.w-0.5);
  }
  function reset(){ if(HOME){ VB={x:HOME.x,y:HOME.y,w:HOME.w,h:HOME.h}; apply(); } }
  if(rb) rb.addEventListener('click',function(){ reset(); show(null); });
  function span(e){
    var a=e.touches[0], b=e.touches[1];
    return Math.hypot(a.clientX-b.clientX,a.clientY-b.clientY);
  }
  function mid(e){
    var a=e.touches[0], b=e.touches[1];
    return {x:(a.clientX+b.clientX)/2,y:(a.clientY+b.clientY)/2};
  }
  var pinch=null;
  map.addEventListener('touchstart',function(e){
    if(e.touches.length===2&&HOME){
      show(null);
      pinch={d:span(e),m:mid(e),vb:{x:VB.x,y:VB.y,w:VB.w,h:VB.h},box:map.getBoundingClientRect()};
    }
  },{passive:true});
  map.addEventListener('touchmove',function(e){
    if(e.touches.length!==2||!pinch) return;
    e.preventDefault();                       // or the browser zooms the whole page instead
    var d=span(e), m=mid(e), box=pinch.box;
    var k=Math.max(0.05,d/Math.max(1,pinch.d));
    var w=pinch.vb.w/k;
    w=Math.min(HOME.w,Math.max(HOME.w/MAXZ,w));
    var h=w*(HOME.h/HOME.w);
    // ZOOM ABOUT THE FINGERS, not the centre of the drawing. Anchoring at the midpoint is what
    // makes a pinch feel like it is holding the paper rather than driving a slider.
    var fx=(pinch.m.x-box.left)/box.width, fy=(pinch.m.y-box.top)/box.height;
    VB.x=pinch.vb.x+fx*pinch.vb.w-fx*w-(m.x-pinch.m.x)/box.width*w;
    VB.y=pinch.vb.y+fy*pinch.vb.h-fy*h-(m.y-pinch.m.y)/box.height*h;
    VB.w=w; VB.h=h;
    apply();
  },{passive:false});
  map.addEventListener('touchend',function(e){
    if(e.touches.length<2) pinch=null;
  },{passive:true});
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
    if(e.touches.length>1) return;   // two fingers are a gesture, never a pick
    clearTimeout(clearAt);           // a new touch outlives the last one's timer
    var t=e.touches[0]; moved=false; sx=t.clientX; sy=t.clientY; show(at(t));
  },{passive:true});
  map.addEventListener('touchmove',function(e){
    if(e.touches.length>1||pinch) return;
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
    // HELD AND CANCELLED, because it used to be armed on every release and never cleared.
    // Drag, lift, drag again, then hold still on a county to read it, and the FIRST timer
    // fired at 2.6s and blanked the readout under a stationary thumb.
    clearTimeout(clearAt); clearAt=setTimeout(function(){ show(null); },2600);
  });
})();
// SEND A MESSAGE WITHOUT LEARNING WHERE IT GOES.
// The address is nowhere in this page and is not needed here: the form posts to FormSubmit's
// opaque alias for the mailbox and that service forwards it. What the reader gets is a box to
// type in; what a scraper gets is a hash.
//
// THE LINK UNDER THIS IS REAL. Without script the icon goes to the form on the services page,
// which reaches the same mailbox by the same route, so nothing here is the only way through.
// With script the navigation is refused and the dialog opens over the page instead.
(function(){
  var open=document.getElementById('contactopen'), box=document.getElementById('contactbox');
  if(!open||!box) return;
  var form=document.getElementById('contactform'), note=document.getElementById('contactstatus'),
      send=document.getElementById('contactsend'), shut=document.getElementById('contactclose');
  function close(){ if(typeof box.close==='function') box.close(); else box.removeAttribute('open'); }
  open.addEventListener('click',function(ev){
    // A MODIFIED CLICK IS A REQUEST FOR THE OTHER THING. Command, control, shift or a middle
    // button means open it in a tab, and taking that away is taking away a browser.
    if(ev.metaKey||ev.ctrlKey||ev.shiftKey||ev.altKey||ev.button) return;
    ev.preventDefault();
    note.textContent=''; send.disabled=false;
    if(typeof box.showModal==='function') box.showModal(); else box.setAttribute('open','');
    var t=document.getElementById('contactmsg'); if(t) t.focus();
  });
  shut.addEventListener('click',close);
  form.addEventListener('submit',function(ev){
    ev.preventDefault();
    send.disabled=true; note.textContent='Sending';
    // THE AJAX ADDRESS IS DERIVED FROM THE ONE IN THE MARKUP rather than written a second
    // time. The form carries the plain endpoint because that is what the policy's form-action
    // is checked against, and a second copy of an endpoint is one of them going stale.
    fetch(form.action.replace('formsubmit.co/','formsubmit.co/ajax/'),{
      method:'POST',
      headers:{'content-type':'application/json','accept':'application/json'},
      body:JSON.stringify(Object.fromEntries(new FormData(form).entries()))
    }).then(function(r){
      if(!r.ok) throw new Error('bad status');
      note.textContent='Thank you. That reached the desk.';
      form.reset();
      setTimeout(close,1600);
    }).catch(function(){
      // WHAT WAS TYPED STAYS IN THE BOX. Losing somebody's message and telling them it failed
      // is two bad things where one would do.
      note.textContent='That did not send. Nothing was lost, so try again or use the form on '
        + 'the services page.';
      send.disabled=false;
    });
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
def _body_class(home_page: bool, extra: str) -> str:
    """The body's classes, from a bool that predates the string and a string that supersedes it.

    `home_page` shipped first and marks exactly one page. The watch stage needs a second, so the
    bool is folded in here rather than left as a parallel mechanism, which is how a page ends up
    able to be both and neither.
    """
    names = (["home"] if home_page else []) + ([extra] if extra else [])
    return f' class="{" ".join(names)}"' if names else ""


def _verification() -> str:
    """The ownership tags, and nothing when there is nothing to say."""
    out = ""
    if GOOGLE_SITE_VERIFICATION:
        out += f'\n<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">'
    if BING_SITE_VERIFICATION:
        out += f'\n<meta name="msvalidate.01" content="{BING_SITE_VERIFICATION}">'
    return out

@functools.lru_cache(maxsize=1)
def _extra_sheet(name: str, p: str) -> str:
    """A second sheet, for a page whose component the other pages do not have.

    Versioned on its own CONTENT for the same reason site.css is: markup and stylesheet are
    cached independently, so for the length of one cache window a reader can hold new markup
    and the previous sheet, and what they see is the page rendered as bare bones.
    """
    if not name:
        return ""
    return f'\n<link rel="stylesheet" href="{p}{name}?v={_sheet_version(name)}">'


@functools.lru_cache(maxsize=4)
def _sheet_version(name: str) -> str:
    body = {"record.css": theme.record_css, "facility.css": theme.facility_css}[name]()
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:10]


def _css_version() -> str:
    """A content hash on the stylesheet URL, because shipping is not the same as being seen.

    The sheet is served from a fixed name with `cache-control: max-age=600`, and so is the HTML
    that links it, INDEPENDENTLY. So for ten minutes after any deploy a visitor can hold one and
    fetch the other, and the page they get is new markup wearing the previous stylesheet. That
    is not hypothetical: the owner watched the scanner section render as a bare ordered list on
    a page whose own bytes were correct, and whose stylesheet, fetched at that same moment,
    already held every rule the section needed.

    HASHING THE CONTENT AND NOT THE BUILD TIME. A timestamp would bust the cache on every run,
    including the daily ones that change nothing here, and hand every returning reader a fresh
    download for nothing. This changes only when the CSS does.

    theme.css() is deterministic, which its own self-test asserts by building twice and
    comparing bytes, so this is stable within a build and identical across identical builds.
    """
    return hashlib.sha256(theme.css().encode("utf-8")).hexdigest()[:10]


def _canonical(path: str) -> str:
    """The canonical is a path RELATIVE to the site, because `page()` prefixes the site itself.

    Five call sites passed an absolute URL and every one of them shipped
    `https://texasaidocket.com/https://texasaidocket.com/...` as its canonical and its og:url, on
    every facility page and every company page. Nothing looked, because a canonical is markup
    rather than copy and no gate here read markup for a doubled host.

    So it is refused at the point of use. A path that already carries a scheme is a bug in the
    caller and the build stops rather than publishing it.
    """
    if "://" in path:
        raise ValueError(
            f"canonical {path!r} is absolute. page() prefixes SITE_URL, so pass a relative path")
    return path.lstrip("/")


def page(*, title: str, desc: str, body: str, depth: int, active: str,
         today: str, canonical: str, extra_ld: list | None = None,
         home_page: bool = False, body_class: str = "", og_image: str = "og.png",
         og_alt: str | None = None, revised: bool = True,
         og_type: str = "website", extra_css: str = "") -> str:
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
    #
    # IT CARRIED "EVERY NUMERAL COMPUTED FROM DATA" AND NO LONGER DOES. The promise is real and
    # it is the reason to believe a figure here, which is exactly why a four word slogan under
    # every page was the wrong place for it. Stated that way it is an assertion a reader has no
    # way to check, repeated 167 times.
    #
    # It is not lost. `/data/` makes the same commitment where it can also say how it is kept,
    # naming the build gate that fails on a figure tracing to nothing, which is the half that
    # makes it worth reading. A claim with its mechanism on one page beats a claim without one
    # on every page.
    colophon = "".join(f"<span>{e(s)}</span>" for s in (
        MADE_AT_LEDE,
        # THE PAGE'S OWN DATE, NOT THE BUILD'S. This printed the build date under every page
        # on the site, so `/about/` told a reader it was revised this morning when its last
        # real edit was days earlier. A reader cannot check that, which is what made it the
        # wrong thing to print. `lastmod.py` works out when each page's published bytes last
        # moved and substitutes it here at the end of the build, and the same date goes into
        # the sitemap, so the two surfaces cannot disagree.
        *([lastmod.TOKEN] if revised else []),
        _made_at(),
    ))

    # ONE ORGANIZATION NODE, REFERENCED BY `@id` EVERYWHERE ELSE. This used to repeat the whole
    # publisher object on all 148 pages, which states the same fact 148 times and builds no
    # graph: nothing could tell that the publisher of a decision page and the publisher of the
    # dataset were the same body. With a stable `@id` they are one node that every other node
    # points at, which is what makes the record traversable rather than merely present.
    ld = [{
        "@context": "https://schema.org", "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "name": SITE_NAME, "url": SITE_URL, "inLanguage": "en-US",
        "publisher": {"@id": f"{SITE_URL}/#org"},
    }, {"@context": "https://schema.org", **schema.org_node(SCHEMA_CTX)}] + (extra_ld or [])

    # THE POLICY IS COMPUTED FROM THE FINISHED PAGE, which is why this is a variable and not a
    # return. `csp.apply` hashes every inline block in the exact bytes that ship, so the thing
    # hashed and the thing served cannot be different strings. See scripts/site/csp.py.
    _doc = f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/{_canonical(canonical)}">{_verification()}
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="{og_type}">
<meta property="og:url" content="{SITE_URL}/{_canonical(canonical)}">
{og.head_html(p, SITE_URL, SITE_NAME, title, desc, og_image, og_alt)}
{favicon.head_html(p)}
<link rel="stylesheet" href="{p}site.css?v={_css_version()}">{_extra_sheet(extra_css, p)}
<link rel="preload" href="{p}fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="alternate" type="application/atom+xml" title="{e(SITE_NAME)}" href="{p}atom.xml">
<script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
</head>
<body{_body_class(home_page, body_class)}>
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
      <ul class="socials" data-prose="data">{socials(depth)}</ul>
      <p class="colophon-line" data-prose="data">{colophon}</p>
    </div>
  </div>
  {contact_dialog()}
</footer>
{SHELL_JS}
</body>
</html>
"""
    return csp.apply(_doc)


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


# The date kinds that are a door a MEMBER OF THE PUBLIC can walk through. `statutory_deadline`
# is a clock on an agency and `effective` is when a rule starts biting, and neither is somewhere
# a Texan turns up and speaks. `comment_opens` is a start, not an end.
DOOR_KINDS = frozenset({"hearing", "comment_closes"})


def next_door(it: dict, today: str) -> str | None:
    """The next date a member of the public can still act on, or None.

    THE SAME LESSON AS `effective_room`, one page further out. `llms.txt` built its "Open right
    now" list from `public_access.room` alone, under a heading reading "Decisions a member of the
    public still has a dated way into". Room is what KIND of access the ledger recorded, never
    whether it is open, so every decided vote held in an open meeting stayed on that list
    forever. On 2026-08-16 that was 28 of 47 entries: Archer County's unanimous denial, Brazoria
    County's 5 to 0 denial, San Angelo's adopted ordinances. A reader following any of them finds
    a finished vote.

    DATED, NOT STATUS. The obvious fix was to drop `decided` and `withdrawn` items, and it is
    the wrong one, because it deletes the case the heading most wants. League City's council has
    DECIDED, and what it decided was to order a special election on November 3rd, which is
    exactly a dated way in. The promise in the heading is a date in the future, so that is what
    gets computed. A finished vote has no future door whatever its status says, and a future
    election has one whatever its status says.
    """
    try:
        t = _dt.date.fromisoformat(today)
    except (ValueError, TypeError):
        return None

    dates = []
    closes = (it.get("public_access") or {}).get("closes")
    if closes:
        dates.append(str(closes))
    for kd in it.get("key_dates") or []:
        if kd.get("kind") not in DOOR_KINDS or not kd.get("date"):
            continue
        # A CANCELED SITTING IS NOT A DOOR. TCEQ called off two hearings in August 2026 and the
        # record kept the original dates with the cancellation in the note, which is correct
        # history and would have published both as live doors.
        #
        # THIS READS A FIELD, NOT THE PROSE. The first version of this matched the word in the
        # note with a regex, which worked and was the wrong shape: a text match against a
        # sentence a person writes is the generated-not-computed failure this project refuses
        # everywhere else, and it would go quiet the day somebody wrote "called off" instead.
        # `gate_schema` now fails any date whose note says canceled while the flag does not, so
        # the sentence cannot drift away from the field it is describing.
        if kd.get("canceled"):
            continue
        dates.append(str(kd["date"]))

    future = []
    for d in dates:
        try:
            if _dt.date.fromisoformat(d) >= t:
                future.append(d)
        except ValueError:
            continue
    return min(future) if future else None


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
    from urllib.parse import urlparse
    out = []
    for c in it.get("claims", []):
        kind = {"primary_official": "Primary source, official",
                "primary_corporate": "Primary source, the company",
                "journalism": "Journalism"}.get(c.get("source_type"), "")
        # THE PUBLISHER, AS A DOOR RATHER THAN A LABEL. The citation goes out to the document,
        # which is right and is where a reader checking one fact wants to land. A reader
        # weighing the record wants the other question, which is what else this publisher is
        # carrying here and how much rests on it, and until the archive had a page per
        # publisher there was nowhere to send them.
        host = urlparse(c.get("source_url") or "").netloc.removeprefix("www.")
        # THE SEPARATOR IS LOAD BEARING. Set straight after the kind, "PRIMARY SOURCE, OFFICIAL
        # INTERCHANGE.PUC.TEXAS.GOV" reads as one label with the host swallowed into it. The
        # middot is what the rest of the site uses to divide two facts on one line.
        via = (f' · <a class="via" href="../../sources/{e(_host_slug(host))}/">{e(host)}</a>'
               if host else "")
        out.append(
            f'<div class="claim">'
            f'<blockquote>{e(c["verbatim_quote"])}</blockquote>'
            f'<cite><a href="{e(c["source_url"])}" rel="nofollow noopener">'
            f'{e(c.get("source_title") or c["source_url"][:70])}</a></cite> '
            f'<span class="kind" data-prose="data">{e(kind)}{via}</span></div>')
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
        # THE MANIFEST SAYS HOW MANY SLIDES THERE ARE. A GLOB SAYS HOW MANY IMAGES SURVIVED.
        #
        # This counted `slide-*.webp` and then the article page generated URLs by INDEX from
        # that count, which is only correct while the surviving files happen to be a contiguous
        # 1..N. On 2026-08-16 they were not. `ship_images` refused two slides for encoding under
        # its 40 dB quality floor, so the run shipped eight slides with six webp among them, and
        # the count came back 6. The page then emitted slide-01 through slide-06, of which 03
        # and 06 did not exist and rendered as broken images, and slides 07 and 08 were never
        # emitted at all. The homepage said "6 slides" for an eight slide deck.
        #
        # So the count comes from the manifest, which is what the deck actually is, and each
        # slide resolves to a file that is checked to exist. A missing one is reported rather
        # than silently skipped, because a hole here is a broken image on the live site.
        planned = copy.get("slides")
        n = len(planned) if isinstance(planned, (list, dict)) else 0
        files, missing = [], []
        for i in range(1, n + 1):
            # webp is the shipping format and png is what survives when webp could not meet the
            # quality floor. Either is a real slide; neither existing is a defect.
            for ext in ("webp", "png"):
                p = d / f"slide-{i:02d}.{ext}"
                if p.exists():
                    files.append(p.name)
                    break
            else:
                missing.append(f"slide-{i:02d}")
        if missing:
            print(f"  MISSING IMAGE: run {d.name} plans {n} slide(s) and "
                  f"{', '.join(missing)} has no webp and no png. The article page would "
                  f"publish a broken image.", file=sys.stderr)
        if not files:
            continue
        title = (copy.get("document_title") or copy.get("title") or d.name)

        # THE DECK'S OWN WORDS, SO THE PAGE IS READABLE AND INDEXABLE WITHOUT THE IMAGES.
        #
        # An article page that is eight pictures and a title publishes nothing a search engine,
        # a screen reader or a reader with images off can use. Everything the slides say is
        # already in `copy.json`, because that manifest is what `copy_sync_check` proves the
        # render against, so the text is right here and was simply never written into the page.
        #
        # PROSE ONLY. A slide's labels ("10,000 FT A SIDE") are furniture and read as noise in
        # running text, so the same shape test the copy gate uses picks sentences out of them.
        prose = []
        for key in sorted(normalise_slide_keys(planned), key=lambda k: k[0]):
            said = [_CLAIM_STAMP.sub(" ", " ".join(s.split())).strip()
                    for s in _slide_strings(key[1]) if _reads_as_prose(s)]
            # A QUOTATION IS MARKED AS ONE. A slide that prints a source's own words keeps them,
            # so they arrive here still wearing their quotation marks, and rendering them as
            # this project's prose would put somebody else's sentence under this project's
            # house rules. `house_style_check` exempts `blockquote` for exactly that reason and
            # says so in its own docstring: house style governs our prose and stops at the
            # quotation mark.
            said = [{"quote": s.startswith('"'), "text": s} for s in said if s]
            if said:
                prose.append(said)

        claims = []
        try:
            cj = json.loads((d / "claims.json").read_text("utf-8"))
            claims = [c for c in (cj.get("claims") or []) if isinstance(c, dict)]
        except Exception:                                            # noqa: BLE001
            pass

        # THE TEASE. One sentence, the deck's own, so a card says what the article is about
        # rather than only what it is called. A title is a name and a name is not a summary.
        #
        # It comes from the FIRST prose the deck speaks, which is slide one's line under the
        # hook, and it stops at the first full stop. Never a quotation, because a source's own
        # words under this project's house rules is the exact thing `house_style_check` exempts
        # `blockquote` to avoid. Derived here so the card and the article page cannot disagree.
        tease = ""
        for block in prose:
            said = next((x for x in block if not x["quote"] and x["text"]), None)
            if said:
                first = said["text"].split(". ")[0].strip().rstrip(".")
                if 12 <= len(first) <= 120:
                    tease = first + "."
                break

        out.append({"date": d.name, "title": str(title), "tease": tease,
                    "hook": str(copy.get("hook") or copy.get("subtitle") or ""),
                    "story": str(copy.get("story") or ""),
                    "slides": len(files), "files": files, "missing": missing,
                    "prose": prose, "claims": claims,
                    "cover": files[0]})
    return out


def normalise_slide_keys(planned) -> list:
    """(order, slide) pairs, from either shape a run writes."""
    if isinstance(planned, dict):
        out = []
        for k, v in planned.items():
            m = re.search(r"(\d+)", str(k))
            out.append((int(m.group(1)) if m else 0, v))
        return out
    if isinstance(planned, list):
        return list(enumerate(planned, start=1))
    return []


# Machinery, never reader copy. Kept in step with copy_sync_check's list by intent: this one
# only has to avoid printing citations and drawing instructions as prose.
_SLIDE_META = frozenset({"claims", "claim_id", "claim_ids", "cid", "n", "slide", "index", "id",
                         "technique", "file", "path", "art", "palette", "notes", "todo"})


def _slide_strings(node) -> list:
    out = []
    if isinstance(node, str):
        if node.strip():
            out.append(node)
    elif isinstance(node, list):
        for x in node:
            out.extend(_slide_strings(x))
    elif isinstance(node, dict):
        for k, v in node.items():
            if k not in _SLIDE_META:
                out.extend(_slide_strings(v))
    return out


# The provenance stamp the design prints beside a sourced figure. It belongs on the slide and
# reads as debris in running text, and the claim it names is published in full further down the
# page with its source attached.
_CLAIM_STAMP = re.compile(
    r"\bCLAIMS?\s+[A-Za-z0-9_.-]+\s*\.?(\s*(QUOTED\s+VERBATIM|COMPUTED|MEASURED|MODELED)\s*\.?)?",
    re.IGNORECASE)


def _reads_as_prose(text: str) -> bool:
    """Whether a slide string belongs in the story, as opposed to on the slide.

    TWO TESTS, AND THE CASE ONE IS DOING THE REAL WORK. A first pass used length and terminal
    punctuation alone, which is enough to sort a label from a sentence but not enough to sort a
    TAG from one: "SITE PLAN NOT PUBLIC." is four words ending in a full stop. The design
    doctrine sets tags, kickers and labels in capitals and writes body prose in sentence case,
    so the case is the signal, and it is the design's own signal rather than one invented here.
    """
    t = _CLAIM_STAMP.sub(" ", " ".join(str(text).split())).strip()
    if not t:
        return False
    letters = [ch for ch in t if ch.isalpha()]
    if letters and all(ch.isupper() for ch in letters):
        return False
    if len(t) >= 60:
        return True
    return len(t.split()) >= 4 and t.rstrip().endswith((".", "?", "!"))


def js_feed_date() -> str:
    """The house date, in JavaScript, for the two surfaces that render the feed client side.

    ONE COPY, BECAUSE THERE WERE TWO AND ONE OF THEM WAS WRONG. The front page and the videos
    page both take a `date` out of `videos.json` and both have to print it in the house form,
    which is the ordinal, month first. `toLocaleDateString` has no ordinal, so each page wrote
    its own line, and the front page's said "August 18, 2026" for as long as the feed existed.

    Nothing caught it, and this is worth naming because it is the third instance of the shape.
    `house_style_check` reads rendered pages, this text is assembled in the reader's browser
    from a file the build does not own, and a rule enforced on the served HTML cannot see a
    string that does not exist until somebody loads the page. The cure is not a cleverer gate.
    It is one function, so there is only one place for the rule to be.

    Returns an expression-free block defining `fmtFeedDate`.
    """
    return """
  /* The house form is the ordinal, month first. toLocaleDateString has no ordinal, so the
     suffix is derived from the number rather than looked up in a table. */
  var ordDay=function(n){var t=n%100;
    if(t>=11&&t<=13)return n+'th';
    return n+({1:'st',2:'nd',3:'rd'}[n%10]||'th');};
  var fmtFeedDate=function(d){try{
    var dt=new Date(d+'T12:00:00');
    return dt.toLocaleDateString('en-US',{month:'long'})+' '+ordDay(dt.getDate())+', '+
      dt.getFullYear();
  }catch(err){return d}};
"""


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
    """The Dispatch feed as a full-bleed vertical feed, one film per screen.

    GENERATED, AND STILL GENERATED NOW THAT IT HAS ITS OWN SHELL. The page used to be a grid
    inside the site's standard `page()` chrome, on the reasoning that a standalone page carries
    a hand-maintained copy of the masthead and this site's masthead changed twice in one
    afternoon. That reasoning was right about the failure and wrong about the cause. The danger
    is a nav somebody TYPES, not a nav that lives outside `page()`. So this document is built
    here, from `NAV` and `SITE_NAME` and the same palette every other page reads, and a section
    added to the site appears in this top bar without anyone touching this function.

    WHY IT IS NOT A GRID ANY MORE. A grid of posters asks a reader to choose before they have
    seen anything, and what they choose from is a still frame of a 2.5D film whose whole
    argument is that it moves. The sibling product's feed is one film per screen, muted, already
    rolling, and a thumb-flick away from the next one, which is the form every reader already
    knows. The measured difference is not subtle: a poster grid is a page you look at and a feed
    is a thing you stay in.

    THE FEED IS FETCHED RATHER THAN BAKED, unchanged and for the same reason as before:
    `docs/videos/videos.json` is written by `TexasAIDispatch` on its own schedule, and a build
    cannot know what shipped after it ran.

    WORKS WITH NO FEED AT ALL. Before the first video the file does not exist, the fetch fails,
    and the page says so in a sentence. It never renders a feed over nothing.

    Four things in the script below are load bearing and each is there for a failure the
    sibling shipped first, so none of them is decoration:

    - **Every feed value is HTML escaped before it reaches `innerHTML`.** A title carrying
      markup would otherwise run as script on this origin.
    - **The preload window is bounded.** Only the current card and its neighbour buffer, the
      two beyond them hold metadata, and everything else is DETACHED outright. Without it a
      reader who flicks through thirty entries leaves thirty live video elements behind and a
      phone gives up.
    - **The download resolves the URL before it checks the scheme.** Checking first rejects a
      relative `media_base` and leaves a dead button.
    - **The scrub sets `touch-action:none` on the grab area and the fill, not only on the
      track.** `touch-action` is not inherited, so setting it in one place lets the browser
      decide mid drag that the gesture was a scroll and take the feed out from under the thumb.

    And one that is this site's own: `prefers-reduced-motion` is honoured. Nothing autoplays for
    a reader who asked for that, the poster stays up, and the play glyph is the invitation. The
    sibling has no such branch, which for a page that is nothing but moving pictures is the one
    accessibility gap worth closing before copying anything else.
    """
    c = theme.palette()["dark"]
    flag = theme.tokens()["colour"]
    # The feed's palette IS the site's palette. Named locally only so the CSS below reads as
    # a feed rather than as a lookup, and sourced from `theme` so a token change reaches here.
    #
    # THE FLAG TOKENS ARE HERE BECAUSE THE MARK CAME OUT BLACK. `mark.flag_svg()` paints
    # nothing itself. Every one of its shapes carries a class and the fills live in
    # `site.css`, which this page does not load, so the first build of it put a black
    # rectangle in the masthead where the Lone Star goes. A standalone page pays for its
    # independence exactly here, and the way to pay it is to read the same tokens rather than
    # to type three hexes that will be right until brand.yaml moves.
    tokens = (
        f"--night:{c['bg']};--deep:{c['surface']};--panel:{c['raised']};--line:{c['rule']};"
        f"--snow:{c['ink-bright']};--body:{c['ink']};--mute:{c['ink-mute']};"
        f"--accent:{c['accent']};--deepaccent:{c['accent-deep']};--good:{c['sig-open']};"
        f"--flag-red:{flag['flag_red']};--flag-blue:{flag['flag_blue']};"
        f"--star:{flag['flag_white']};"
    )

    # THE TOP BAR IS THE SITE'S NAV, GENERATED. `hidesm` is applied by RULE rather than by
    # name, so a section added to `NAV` needs no edit here and cannot silently crowd a phone.
    #
    # The rule is the way out and where you are, and nothing else, because a phone has room for
    # two. Keeping the first four instead put eight items and a wordmark on a 390 px bar and
    # ran the last one off the right edge, which is the shape a hand-maintained nav goes wrong
    # in and the reason this one is generated at all.
    links = []
    for h, t in NAV:
        here = h == "videos/"
        cls = "on" if here else ("" if h == "" else "hidesm")
        a = f' class="{cls}"' if cls else ""
        links.append(f'<a href="../{h}"{a}>{e(t.upper())}</a>')
    nav = "".join(links)

    desc = ("One short film a day on artificial intelligence in Texas. Narrated, sourced, and "
            "built by the same machine that keeps the docket.")

    # THE MEDIA HOST, READ OUT OF THE FEED RATHER THAN TYPED. The films are served from
    # wherever `videos.json` says, which is a field `TexasAIDispatch` owns and this build only
    # reads. A preconnect saves the reader the TLS handshake on the first film, and getting it
    # from the feed means the hint can never point somewhere the media is not. No feed yet, or
    # a relative `media_base`, and there is simply no hint, which is correct rather than a
    # fallback: a preconnect to a host nothing is fetched from is a wasted connection.
    preconnect = ""
    host = str(video_feed().get("media_base") or "")
    m = re.match(r"(https://[^/]+)", host)
    if m:
        preconnect = f'<link rel="preconnect" href="{e(m.group(1))}" crossorigin>\n'

    css = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:var(--night);color:var(--body);
font-family:var(--body-face);overscroll-behavior-y:contain}
:focus-visible{outline:2px solid var(--accent);outline-offset:3px;border-radius:3px}
a{color:inherit}

/* ---------- top bar, an overlay so the film keeps the whole screen ---------- */
.topbar{position:fixed;top:0;left:0;right:0;z-index:40;display:flex;align-items:center;
justify-content:space-between;gap:12px;padding:calc(10px + env(safe-area-inset-top)) 16px 10px;
background:linear-gradient(180deg,rgba(8,6,15,.9),rgba(8,6,15,.55) 70%,transparent);
pointer-events:none}
.topbar>*{pointer-events:auto}
.wordmark{display:flex;align-items:center;gap:9px;text-decoration:none;white-space:nowrap;
font-family:var(--mono-face);font-size:12.5px;letter-spacing:.14em;color:var(--snow)}
@media(max-width:520px){.wordmark{font-size:11px;letter-spacing:.1em}}
/* The mark carries classes and no fills of its own, because on every other page the fills
   come from site.css. This page does not load site.css, so it paints them here from the same
   tokens. Without this the Lone Star renders as a black rectangle. */
.wordmark svg{height:17px;width:auto;display:block;flex:none}
.m-blue{fill:var(--flag-blue)}
.m-white{fill:var(--star)}
.m-red{fill:var(--flag-red)}
.m-star{fill:var(--star)}
.f-lit{fill:#FFFFFF;opacity:.55}
.f-shade{fill:var(--flag-blue);opacity:.14}
.navlinks{display:flex;gap:14px;font-family:var(--mono-face);font-size:10.5px;letter-spacing:.12em}
.navlinks a{text-decoration:none;color:var(--mute);padding:6px 2px}
.navlinks a:hover{color:var(--snow)}
.navlinks a.on{color:var(--accent)}
@media(max-width:760px){.navlinks a.hidesm{display:none}}

/* ---------- the feed ---------- */
.feed{height:100dvh;overflow-y:scroll;scroll-snap-type:y mandatory;scrollbar-width:none}
.feed::-webkit-scrollbar{display:none}
.card{position:relative;height:100dvh;scroll-snap-align:start;scroll-snap-stop:always;
display:flex;align-items:center;justify-content:center;background:var(--night)}
/* the 9:16 stage. Full bleed on a phone, a centred column on a wide screen, because a
   letterboxed vertical film on a desktop is worse than an honest column. */
.stage{position:relative;height:100%;aspect-ratio:9/16;max-width:100vw;background:#000;
overflow:hidden}
@media(min-width:700px){.stage{height:min(94dvh,1000px);border-radius:14px;
border:1px solid var(--line);box-shadow:0 30px 80px rgba(0,0,0,.6)}}
.stage video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;background:#000}
.stage .poster{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;
transition:opacity .35s}
.stage.playing .poster{opacity:0;pointer-events:none}

/* tap layer */
.tap{position:absolute;inset:0;border:0;background:transparent;cursor:pointer}
.pauseglyph{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%) scale(.8);
width:82px;height:82px;border-radius:50%;background:rgba(8,6,15,.55);border:1px solid var(--line);
display:flex;align-items:center;justify-content:center;opacity:0;
transition:opacity .2s,transform .2s;pointer-events:none}
.card.paused .pauseglyph{opacity:1;transform:translate(-50%,-50%) scale(1)}
.pauseglyph svg{width:33px;height:33px;fill:var(--snow);margin-left:5px}

/* the words over the picture */
.meta{position:absolute;left:0;right:64px;bottom:0;
padding:18px 16px calc(20px + env(safe-area-inset-bottom));
background:linear-gradient(0deg,rgba(8,6,15,.88),rgba(8,6,15,.45) 60%,transparent);
pointer-events:none}
.meta>*{pointer-events:auto}
.kicker{font-family:var(--mono-face);font-size:10px;letter-spacing:.16em;color:var(--accent);
text-transform:uppercase;margin-bottom:6px;display:flex;flex-wrap:wrap;gap:5px 9px}
.kicker .where{color:var(--mute)}
.title{font-family:var(--display-face);font-weight:600;font-size:clamp(19px,4.6vw,25px);
line-height:1.15;color:var(--snow);margin-bottom:7px;text-wrap:balance}
.cap{font-size:13.5px;line-height:1.5;color:var(--body);max-width:52ch;cursor:pointer;
display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.cap.open{-webkit-line-clamp:unset}

/* the right rail */
.rail{position:absolute;right:8px;bottom:calc(86px + env(safe-area-inset-bottom));z-index:5;
display:flex;flex-direction:column;gap:15px;align-items:center}
.rbtn{width:45px;height:45px;border-radius:50%;border:1px solid var(--line);cursor:pointer;
background:rgba(25,21,48,.72);display:flex;align-items:center;justify-content:center;
transition:transform .12s,border-color .12s;backdrop-filter:blur(6px)}
.rbtn:hover{transform:scale(1.08);border-color:var(--accent)}
.rbtn svg{width:21px;height:21px;fill:none;stroke:var(--snow);stroke-width:1.8;
stroke-linecap:round;stroke-linejoin:round}
.rbtn.toast svg{stroke:var(--good)}
.rbtn.busy{opacity:.45}

/* The progress hairline is scaleX only and never touches layout. Paused it becomes a real
   scrubber: the track thickens, a knob appears, and a thumb-sized grab area opens along the
   bottom. That area exists ONLY while the scrubber is up, since a permanent 44px strip would
   swallow every bottom-edge tap meant for play and pause. */
.prog{position:absolute;left:0;right:0;bottom:0;height:3px;background:rgba(237,230,214,.14);
z-index:6;touch-action:none;transition:height .16s,background-color .16s}
.prog i{display:block;height:100%;width:100%;
background:linear-gradient(90deg,var(--deepaccent),var(--accent));
transform:scaleX(0);transform-origin:0 50%;will-change:transform;touch-action:none}
.prog::before{content:"";position:absolute;left:0;right:0;bottom:0;height:0;touch-action:none}
.card.paused .prog::before,.card.scrubbing .prog::before{height:44px}
.card.paused .prog,.card.scrubbing .prog{height:6px;background:rgba(237,230,214,.26)}
.knob{position:absolute;top:50%;left:0;width:15px;height:15px;margin:-7.5px 0 0 -7.5px;
border-radius:50%;background:var(--accent);box-shadow:0 0 0 5px rgba(224,149,106,.22);
opacity:0;pointer-events:none;transition:opacity .16s}
.card.paused .knob,.card.scrubbing .knob{opacity:1}

/* double tap to skip, flashed on the side that was tapped */
.skip{position:absolute;top:50%;transform:translateY(-50%);width:34%;z-index:5;
pointer-events:none;display:flex;flex-direction:column;align-items:center;gap:5px;opacity:0;
transition:opacity .3s;font-family:var(--mono-face);font-size:11px;letter-spacing:.1em;
color:var(--snow)}
.skip.back{left:0}
.skip.fwd{right:0}
.skip.on{opacity:1;transition:opacity .06s}
.skip svg{width:31px;height:31px;fill:var(--snow)}

/* buffering */
.spin{position:absolute;top:50%;left:50%;width:34px;height:34px;margin:-17px 0 0 -17px;z-index:4;
border-radius:50%;border:3px solid rgba(237,230,214,.18);border-top-color:var(--accent);
opacity:0;transition:opacity .25s .2s;pointer-events:none;animation:vspin .8s linear infinite}
.card.buffering .spin{opacity:1}
@keyframes vspin{to{transform:rotate(360deg)}}

/* the sound invitation, up only while the feed is muted */
.unmute{position:fixed;z-index:45;left:50%;transform:translateX(-50%);
top:calc(58px + env(safe-area-inset-top));display:none;align-items:center;gap:8px;
background:rgba(25,21,48,.85);border:1px solid var(--accent);color:var(--snow);cursor:pointer;
font-family:var(--mono-face);font-size:11px;letter-spacing:.1em;padding:9px 16px;
border-radius:99px;backdrop-filter:blur(6px)}
body.feedready.muted .unmute{display:flex}
.unmute svg{width:15px;height:15px;fill:var(--accent)}

/* a mouse has no thumb, so a wide screen gets buttons */
.stepper{position:fixed;right:22px;top:50%;transform:translateY(-50%);z-index:40;
display:none;flex-direction:column;gap:10px}
@media(min-width:900px){body.feedready .stepper{display:flex}}
.stepper button{width:43px;height:43px;border-radius:50%;border:1px solid var(--line);
background:rgba(25,21,48,.72);color:var(--snow);font-size:16px;cursor:pointer}
.stepper button:hover{border-color:var(--accent);color:var(--accent)}

.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.notice{height:100dvh;display:flex;align-items:center;justify-content:center;text-align:center;
padding:0 24px;font-family:var(--mono-face);font-size:12px;letter-spacing:.14em;
line-height:2;color:var(--mute)}
noscript div{padding:40vh 22px 0;text-align:center;font-family:var(--mono-face);
font-size:12px;line-height:2;color:var(--mute)}

/* A reader who asked for less motion gets a still frame and a button, never an autoplay.
   CSS cannot reach media playback, so this only styles the state the script puts the page in. */
@media(prefers-reduced-motion:reduce){
  .stage .poster{transition:none}
  .pauseglyph{transition:none}
  .spin{animation:none}
}
"""

    script = r"""
(async function(){
  var feed = document.getElementById('feed');
  var notice = document.getElementById('notice');
  var calm = window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;

  var manifest;
  try{ manifest = await (await fetch('videos.json')).json(); }
  catch(err){ notice.textContent = 'THE FEED DID NOT LOAD. TRY A REFRESH.'; return; }

  var base = manifest.media_base || '';
  var vids = (manifest.videos || []).filter(function(v){ return v && v.video; });
  if(!vids.length){ notice.textContent = 'NO FILM HAS SHIPPED YET. THE FIRST ONE APPEARS HERE THE DAY IT DOES.'; return; }

  var abs = function(u){ return /^https?:\/\//.test(u) ? u : base + u; };
  /* Every value below is written into innerHTML, so it is escaped first. A title or a caption
     carrying markup would otherwise run as script on this origin. */
  var esc = function(s){ return String(s == null ? '' : s).replace(/[&<>"']/g, function(ch){
    return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]; }); };

""" + js_feed_date() + r"""  /* A deep link needs a stable handle. The publish step writes `id`; an entry from before it
     did gets one derived from its own date and title, which is stable for that entry. */
  var idOf = function(v, i){
    if(v.id) return String(v.id);
    var slug = String(v.title || '').toLowerCase().replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '').slice(0, 60);
    return (v.date || ('v' + i)) + (slug ? '-' + slug : '');
  };

  /* Source selection. A phone on a frontage road gets the 720p rendition and the jpeg thumb
     when the feed carries them; a wide screen on a healthy connection gets the master. An
     entry published before the renditions existed carries neither, so both fall back. */
  var conn = navigator.connection || {};
  var slowNet = !!(conn.saveData || /2g$/.test(conn.effectiveType || ''));
  var wantFull = window.innerWidth >= 900 && !slowNet;
  var srcOf = function(v){ return (!wantFull && v.video_mobile) ? abs(v.video_mobile) : abs(v.video); };
  var posterOf = function(v){
    var p = (!wantFull && v.poster_thumb) ? v.poster_thumb : v.poster;
    return p ? abs(p) : '';
  };

  var frag = document.createDocumentFragment();
  vids.forEach(function(v, i){
    var card = document.createElement('section');
    card.className = 'card' + (calm ? ' paused' : '');
    card.id = idOf(v, i);
    card.dataset.idx = i;
    var psrc = posterOf(v);
    var where = v.county ? '<span class="where">' + esc(v.county) + ' County</span>' : '';
    card.innerHTML =
      '<div class="stage">' +
        '<video playsinline loop muted preload="none" ' +
          (psrc ? 'poster="' + esc(psrc) + '" ' : '') +
          'data-src="' + esc(srcOf(v)) + '" aria-label="' + esc(v.title || 'Texas AI Dispatch') + '"></video>' +
        (psrc ? '<img class="poster" src="' + esc(psrc) + '" alt="" loading="lazy">' : '') +
        '<button class="tap" type="button" aria-label="Play or pause"></button>' +
        '<div class="pauseglyph" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M8 5v14l11-7z"/></svg></div>' +
        '<div class="spin" aria-hidden="true"></div>' +
        '<div class="meta">' +
          '<div class="kicker"><span>Texas AI Dispatch</span><span>' + esc(fmtFeedDate(v.date)) + '</span>' + where + '</div>' +
          '<h2 class="title">' + esc(v.title || '') + '</h2>' +
          (v.caption ? '<p class="cap" title="Tap to expand">' + esc(v.caption) + '</p>' : '') +
        '</div>' +
        '<div class="rail">' +
          '<button class="rbtn mutebtn" type="button" aria-label="Toggle sound">' +
            '<svg viewBox="0 0 24 24"><path class="spk" d="M4 9.5v5h3.5L12 18.5v-13L7.5 9.5H4z"/>' +
            '<path class="wave" d="M15.5 9a4.2 4.2 0 0 1 0 6M18 6.8a7.6 7.6 0 0 1 0 10.4"/></svg>' +
          '</button>' +
          '<button class="rbtn sharebtn" type="button" aria-label="Share this film">' +
            '<svg viewBox="0 0 24 24"><path d="M12 15V4m0 0L8 8m4-4 4 4M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5"/></svg>' +
          '</button>' +
          '<button class="rbtn dlbtn" type="button" aria-label="Download this film">' +
            '<svg viewBox="0 0 24 24"><path d="M12 4v11m0 0-4-4m4 4 4-4M5 14v5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-5"/></svg>' +
          '</button>' +
        '</div>' +
        '<div class="skip back" aria-hidden="true">' +
          '<svg viewBox="0 0 24 24"><path d="M11 6v12L2 12l9-6Zm11 0v12l-9-6 9-6Z"/></svg><span>10s</span></div>' +
        '<div class="skip fwd" aria-hidden="true">' +
          '<svg viewBox="0 0 24 24"><path d="M13 6v12l9-6-9-6ZM2 6v12l9-6L2 6Z"/></svg><span>10s</span></div>' +
        '<div class="prog" aria-hidden="true"><i></i><b class="knob"></b></div>' +
      '</div>';
    var vd = card.querySelector('video');
    vd.addEventListener('waiting', function(){ card.classList.add('buffering'); });
    vd.addEventListener('playing', function(){ card.classList.remove('buffering'); });
    vd.addEventListener('canplay', function(){ card.classList.remove('buffering'); });
    frag.appendChild(card);
  });
  notice.remove();
  feed.appendChild(frag);
  /* THE CONTROLS ARE GATED ON A FEED THAT LOADED. The sound pill and the desktop stepper are
     in the markup so they need no layout shift to appear, and their listeners are attached at
     the bottom of this function. Between those two facts is a window where a failed fetch
     leaves a reader looking at a button that does nothing, which is worse than no button. */
  document.body.classList.add('feedready');

  var cards = Array.prototype.slice.call(feed.querySelectorAll('.card'));
  var soundOn = false;
  var current = null;
  var videoOf = function(c){ return c.querySelector('video'); };

  /* A BOUNDED PRELOAD WINDOW. The current card and the next buffer in full, the previous and
     the one after next hold metadata, and every other card is DETACHED outright, src removed
     and reloaded empty. Without this a reader who flicks through a month of films leaves a
     month of live video elements behind and a phone gives up. */
  function attach(vd, pl){
    vd.preload = pl;
    if(!vd.getAttribute('src')) vd.src = vd.dataset.src;
  }
  function detach(c){
    var vd = videoOf(c);
    if(vd && vd.getAttribute('src')){
      if(!vd.paused) vd.pause();
      vd.removeAttribute('src');
      vd.load();
      c.querySelector('.stage').classList.remove('playing');
      c.classList.remove('buffering');
    }
  }
  function applyWindow(i){
    cards.forEach(function(c, j){
      var d = j - i;
      if(d === 0 || d === 1) attach(videoOf(c), 'auto');
      else if(d === -1 || d === 2) attach(videoOf(c), 'metadata');
      else detach(c);
    });
  }

  function play(c){
    var vd = videoOf(c);
    attach(vd, 'auto');
    vd.muted = !soundOn;
    vd.play().then(function(){
      c.querySelector('.stage').classList.add('playing');
      c.classList.remove('paused');
    }).catch(function(err){
      /* A real refusal, which on a phone in low power mode is the common one, has to leave the
         play glyph up so the poster is not a dead end. An AbortError from a fast flick is noise. */
      if(err && err.name === 'NotAllowedError') c.classList.add('paused');
    });
  }
  function pause(c){ var vd = videoOf(c); if(vd && !vd.paused) vd.pause(); }

  /* The incoming card starts as it crosses 40 percent mid flick, so it is already rolling when
     the snap settles, and it is committed as current at 60 percent. */
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      var c = en.target;
      if(en.intersectionRatio >= 0.6){
        if(current && current !== c) pause(current);
        current = c;
        applyWindow(+c.dataset.idx);
        if(!calm) play(c);
        bindProgress(c);
        history.replaceState(null, '', '#' + c.id);
      }else if(en.intersectionRatio >= 0.4){
        if(c !== current && !calm) play(c);
      }else{
        if(c !== current) pause(c);
      }
    });
  }, {root: feed, threshold: [0, .4, .6]});

  var SKIP = 10;
  function paint(c, f){
    var bar = c.querySelector('.prog i'), kn = c.querySelector('.knob');
    if(bar) bar.style.transform = 'scaleX(' + f + ')';
    if(kn) kn.style.left = (f * 100) + '%';
  }
  function flashSkip(c, dir){
    var el = c.querySelector(dir > 0 ? '.skip.fwd' : '.skip.back');
    if(!el) return;
    el.classList.add('on');
    clearTimeout(el._t);
    el._t = setTimeout(function(){ el.classList.remove('on'); }, 420);
  }
  function nudge(c, secs){
    var vd = videoOf(c);
    if(!vd || !isFinite(vd.duration) || !vd.duration) return;
    vd.currentTime = Math.max(0, Math.min(vd.duration, vd.currentTime + secs));
    paint(c, vd.currentTime / vd.duration);
    flashSkip(c, secs);
  }

  var tapT = 0, tapCard = null, tapWasPlaying = false;
  feed.addEventListener('click', function(ev){
    var tap = ev.target.closest('.tap');
    if(tap){
      var c = tap.closest('.card'), vd = videoOf(c);
      var r = tap.getBoundingClientRect();
      var rel = (ev.clientX - r.left) / r.width;
      var zone = rel < .35 ? -1 : (rel > .65 ? 1 : 0);
      var now = Date.now();
      /* A second tap on the same side inside 320ms UNDOES the play or pause the first one did,
         then seeks. Undoing is what keeps a single tap instant. Waiting 320ms to disambiguate
         would make every pause feel late, which is a worse trade than a brief flicker. */
      if(zone && tapCard === c && now - tapT < 320){
        if(tapWasPlaying){ play(c); } else { vd.pause(); c.classList.add('paused'); }
        nudge(c, zone * SKIP);
        tapT = 0; tapCard = null;
        return;
      }
      tapT = now; tapCard = c; tapWasPlaying = !vd.paused;
      if(vd.paused){ play(c); } else { vd.pause(); c.classList.add('paused'); }
      return;
    }
    var cap = ev.target.closest('.cap');
    if(cap){ cap.classList.toggle('open'); return; }
    var mb = ev.target.closest('.mutebtn');
    if(mb){ setSound(!soundOn); return; }
    var sb = ev.target.closest('.sharebtn');
    if(sb){
      var sc = sb.closest('.card');
      var url = location.origin + location.pathname + '#' + sc.id;
      var title = sc.querySelector('.title').textContent;
      if(navigator.share){
        navigator.share({title: title + ' - Texas AI Docket', url}).catch(function(){});
      }else if(navigator.clipboard){
        navigator.clipboard.writeText(url).then(function(){
          sb.classList.add('toast');
          setTimeout(function(){ sb.classList.remove('toast'); }, 1200);
        }).catch(function(){});
      }
      return;
    }
    var db = ev.target.closest('.dlbtn');
    if(db){
      var dc = db.closest('.card'), dv = videoOf(dc);
      var raw = dv && dv.dataset.src;
      if(!raw || db.classList.contains('busy')) return;
      /* Resolve against the document FIRST, then check the scheme. A bare scheme test rejects a
         relative media_base outright and leaves a dead button. Resolving handles both forms and
         still keeps javascript: and data: out of an href. */
      var src;
      try{ src = new URL(raw, location.href); }catch(err){ return; }
      if(src.protocol !== 'http:' && src.protocol !== 'https:') return;
      src = src.href;
      var name = (String(dc.id || '').replace(/[^a-z0-9_-]/gi, '') || 'texas-ai-dispatch') + '.mp4';
      var save = function(href){
        var a = document.createElement('a');
        a.href = href; a.download = name; a.rel = 'noopener';
        document.body.appendChild(a); a.click(); a.remove();
      };
      /* Blob first, because the download attribute is IGNORED cross origin and a plain link to
         the media host would navigate to the mp4 instead of saving it. The fetch fails only
         when CORS is absent, and then the plain link is still better than a dead button. */
      db.classList.add('busy');
      fetch(src).then(function(r){ return r.ok ? r.blob() : Promise.reject(0); }).then(function(b){
        var u = URL.createObjectURL(b);
        save(u);
        setTimeout(function(){ URL.revokeObjectURL(u); }, 60000);
        db.classList.remove('busy');
        db.classList.add('toast');
        setTimeout(function(){ db.classList.remove('toast'); }, 1400);
      }).catch(function(){ db.classList.remove('busy'); save(src); });
    }
  });

  /* SCRUB. The drag is tracked by pointer id rather than re-derived from the event target on
     every move, because deriving it ends the drag the instant the finger wanders off the strip,
     which on a phone is most of the way through a normal thumb roll. Moves are listened for on
     window for the same reason. Once the finger is down the bar owns the gesture until it lifts. */
  var drag = null, pendingF = -1, seekRaf = 0;
  function fracAt(c, clientX){
    var r = c.querySelector('.prog').getBoundingClientRect();
    return Math.min(1, Math.max(0, (clientX - r.left) / r.width));
  }
  function durOf(c){
    var vd = videoOf(c);
    return (vd && isFinite(vd.duration) && vd.duration) ? vd : null;
  }
  /* Painting is one transform and costs nothing, so it runs on every move and the bar tracks the
     thumb exactly. Assigning currentTime kicks a decoder seek and pointermove fires far faster
     than a phone can serve those, so the seek is coalesced to one a frame. */
  function commitSeek(){
    seekRaf = 0;
    if(!drag || pendingF < 0) return;
    var vd = durOf(drag.card);
    if(vd) vd.currentTime = pendingF * vd.duration;
  }
  function scrub(c, clientX){
    var f = fracAt(c, clientX);
    paint(c, f);
    pendingF = f;
    if(!seekRaf) seekRaf = requestAnimationFrame(commitSeek);
  }
  feed.addEventListener('pointerdown', function(ev){
    var pr = ev.target.closest('.prog');
    if(!pr || drag) return;
    var c = pr.closest('.card');
    drag = {card: c, id: ev.pointerId, bar: pr};
    c.classList.add('scrubbing');
    try{ pr.setPointerCapture(ev.pointerId); }catch(err){}
    scrub(c, ev.clientX);
    ev.preventDefault();
  });
  window.addEventListener('pointermove', function(ev){
    if(!drag || ev.pointerId !== drag.id) return;
    scrub(drag.card, ev.clientX);
    ev.preventDefault();
  }, {passive: false});
  function endScrub(ev){
    if(!drag || ev.pointerId !== drag.id) return;
    var c = drag.card;
    /* Land exactly where the finger left off. The last move may have been coalesced away by the
       frame budget, so the release seeks outright. */
    var vd = durOf(c), f = fracAt(c, ev.clientX);
    if(vd) vd.currentTime = f * vd.duration;
    paint(c, f);
    c.classList.remove('scrubbing');
    try{ drag.bar.releasePointerCapture(drag.id); }catch(err){}
    if(seekRaf){ cancelAnimationFrame(seekRaf); seekRaf = 0; }
    drag = null; pendingF = -1;
  }
  window.addEventListener('pointerup', endScrub);
  window.addEventListener('pointercancel', endScrub);

  function setSound(on){
    soundOn = on;
    document.body.classList.toggle('muted', !on);
    cards.forEach(function(c){ var vd = videoOf(c); if(vd) vd.muted = !on; });
    document.querySelectorAll('.mutebtn .wave').forEach(function(w){ w.style.opacity = on ? 1 : .25; });
    if(on && current && !calm){ var vd = videoOf(current); if(vd.paused) play(current); }
  }
  document.getElementById('unmute').addEventListener('click', function(){ setSound(true); });
  setSound(false);

  /* The hairline is driven by requestVideoFrameCallback on the active film, which is one paint
     aligned update a presented frame and suspends itself while paused. timeupdate is the
     fallback. scaleX never causes layout. */
  var hasRVFC = 'requestVideoFrameCallback' in HTMLVideoElement.prototype;
  var progVd = null, progBar = null, progKnob = null, progId = 0;
  function progTick(){
    if(progVd && progVd.duration){
      var f = progVd.currentTime / progVd.duration;
      progBar.style.transform = 'scaleX(' + f + ')';
      if(progKnob) progKnob.style.left = (f * 100) + '%';
    }
  }
  function progLoop(){
    progTick();
    progId = progVd.requestVideoFrameCallback(progLoop);
  }
  function bindProgress(c){
    var vd = videoOf(c);
    if(vd === progVd) return;
    if(progVd){
      if(hasRVFC && progId) progVd.cancelVideoFrameCallback(progId);
      if(!hasRVFC) progVd.removeEventListener('timeupdate', progTick);
      if(progBar) progBar.style.transform = 'scaleX(0)';
    }
    progVd = vd;
    progBar = c.querySelector('.prog i');
    progKnob = c.querySelector('.knob');
    if(hasRVFC){ progId = vd.requestVideoFrameCallback(progLoop); }
    else{ vd.addEventListener('timeupdate', progTick); }
  }

  function step(dir){
    var i = current ? +current.dataset.idx : 0;
    var t = cards[Math.min(cards.length - 1, Math.max(0, i + dir))];
    if(t) t.scrollIntoView({behavior: calm ? 'auto' : 'smooth'});
  }
  document.getElementById('prev').addEventListener('click', function(){ step(-1); });
  document.getElementById('next').addEventListener('click', function(){ step(1); });
  window.addEventListener('keydown', function(ev){
    if(ev.key === 'ArrowDown' || ev.key === 'PageDown'){ ev.preventDefault(); step(1); }
    if(ev.key === 'ArrowUp' || ev.key === 'PageUp'){ ev.preventDefault(); step(-1); }
    if(ev.key === ' '){
      ev.preventDefault();
      if(current){
        var vd = videoOf(current);
        if(vd.paused){ play(current); } else { vd.pause(); current.classList.add('paused'); }
      }
    }
    /* The keyboard equivalent of the double tap, which is also how seeking reaches anyone who
       cannot use a pointer at all. */
    if(ev.key === 'ArrowRight'){ ev.preventDefault(); if(current) nudge(current, SKIP); }
    if(ev.key === 'ArrowLeft'){ ev.preventDefault(); if(current) nudge(current, -SKIP); }
    if(ev.key.toLowerCase() === 'm'){ setSound(!soundOn); }
  });

  /* Jump before observing, so the observer's first pass attaches the linked card's window
     rather than card zero's. */
  if(location.hash){
    var t = document.getElementById(location.hash.slice(1));
    if(t) t.scrollIntoView();
  }
  cards.forEach(function(c){ io.observe(c); });
})();
"""

    ld = [{
        "@context": "https://schema.org", "@type": "CollectionPage",
        "@id": f"{SITE_URL}/videos/#page",
        "name": f"Videos · {SITE_NAME}", "url": f"{SITE_URL}/videos/",
        "description": desc, "inLanguage": "en-US",
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "publisher": {"@id": f"{SITE_URL}/#org"},
    }]

    # ITS OWN SHELL MEANS ITS OWN POLICY. This page does not go through `page()`, so the
    # CSP that every other page inherits there has to be applied here too. It carries the
    # feed loader inline, which is exactly the kind of script the policy exists to pin.
    _doc = f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Videos · {e(SITE_NAME)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/videos/">
<meta property="og:title" content="Videos · {e(SITE_NAME)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/videos/">
{og.head_html("../", SITE_URL, SITE_NAME, f"Videos · {SITE_NAME}", desc, "og.png", None)}
{favicon.head_html("../")}
{preconnect}<link rel="preload" href="videos.json" as="fetch" crossorigin>
<link rel="preload" href="../fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="../fonts/jetbrainsmono.woff2" as="font" type="font/woff2" crossorigin>
<script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
<style>
@font-face{{font-family:Fraunces;src:url(../fonts/fraunces.woff2) format("woff2");
font-weight:100 900;font-display:swap}}
@font-face{{font-family:Manrope;src:url(../fonts/manrope.woff2) format("woff2");
font-weight:200 800;font-display:swap}}
@font-face{{font-family:JBMono;src:url(../fonts/jetbrainsmono.woff2) format("woff2");
font-weight:400 600;font-display:swap}}
:root{{{tokens}
--display-face:Fraunces,Georgia,"Times New Roman",serif;
--body-face:Manrope,system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
--mono-face:JBMono,ui-monospace,SFMono-Regular,Menlo,monospace}}
{css}</style>
</head>
<body>

<nav class="topbar" aria-label="Sections">
  <a class="wordmark" href="../">{HOIST}<span>{e(SITE_NAME.upper())}</span></a>
  <div class="navlinks">{nav}</div>
</nav>

<button class="unmute" id="unmute" type="button">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3a4.5 4.5 0 0 0-2.5-4v8a4.5 4.5 0 0 0 2.5-4z"/></svg>
  TAP FOR SOUND
</button>

<div class="stepper" aria-hidden="true">
  <button id="prev" title="Previous film, or the up arrow">&#9650;</button>
  <button id="next" title="Next film, or the down arrow">&#9660;</button>
</div>

<h1 class="sr">Videos</h1>
<main class="feed" id="feed" tabindex="0" aria-label="Video feed">
  <div class="notice" id="notice">LOADING THE FEED</div>
</main>

<noscript><div>The feed needs JavaScript. Every film is also linked from
<a href="../">the front page</a>.</div></noscript>

<script>{script}</script>
</body>
</html>
"""
    return csp.apply(_doc)



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
  <h3>{e(r["title"])}</h3>
  {f'<p class="tease">{e(deck_preview(r))}</p>' if deck_preview(r) else ""}</a>""" for r in runs)

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


def article_page(r: dict, today: str, items: list) -> str:
    """One shipped carousel, as TEXT first and pictures second.

    THIS PAGE USED TO BE EIGHT IMAGES AND A TITLE. Everything the deck said was locked inside
    PNGs, so the page published nothing a search engine could index, nothing a screen reader
    could read, and nothing a reader with images off could see. The words were never missing:
    `copy.json` is the manifest `copy_sync_check` proves the render against, and `claims.json`
    holds every source those words rest on. They were simply never written into the page.

    The shape follows the sibling product's archive, which solved this first. The deck, then the
    story in the deck's own words, then every claim with the source it was checked against, then
    the beats. A reader who never loads an image still gets the whole thing.
    """
    d = _dt.date.fromisoformat(r["date"])
    # BY FILENAME, NEVER BY INDEX. See `load_runs`: generating `slide-{i:02d}.webp` from a count
    # published two broken images and dropped two slides entirely the first time the surviving
    # files were not a contiguous run.
    slides = "".join(
        f'<img src="{RAW}/runs/carousel/{e(r["date"])}/{e(name)}" width="1080"'
        f' height="1350" loading="lazy" alt="Slide {i} of {r["slides"]}">'
        for i, name in enumerate(r["files"], start=1))

    def say(block):
        return "".join(
            f"<blockquote>{e(s['text'])}</blockquote>" if s["quote"]
            else f"<p>{e(s['text'])}</p>" for s in block)

    story = "".join(say(b) for b in r.get("prose") or [])
    if not story:
        story = f'<p>{e(r["hook"] or r["title"])}</p>'

    # EVERY CLAIM, WITH WHAT IT WAS CHECKED AGAINST. The site's promise is that a fact traces to
    # a source a reader can open, and this is the page where the deck's facts live, so this is
    # where that promise has to be redeemable.
    def claim_row(i, c):
        kind = ("PRIMARY" if str(c.get("source_type", "")).startswith("primary") else "REPORT")
        url, title = str(c.get("url") or ""), str(c.get("source_title") or "")
        shown = e(title or url)
        cite = (f'<cite><a href="{e(url)}" rel="nofollow noopener">{shown}</a></cite>'
                if url else f"<cite>{shown}</cite>")
        quote = str(c.get("quote") or "").strip()
        block = f"<blockquote>{e(quote)}</blockquote>" if quote else ""
        checked = ""
        try:
            if c.get("retrieved"):
                checked = f' · checked {e(ordinal(_dt.date.fromisoformat(str(c["retrieved"]))))}'
        except ValueError:
            checked = ""
        return (f'<li><p>{e(str(c.get("text") or ""))}</p>{block}'
                f'<p class="meta" data-prose="data"><span class="tag">{kind}</span> {cite}'
                f'{checked}</p></li>')

    claims = r.get("claims") or []
    claims_html = ""
    if claims:
        rows = "".join(claim_row(i, c) for i, c in enumerate(claims, start=1))
        claims_html = f"""
<h2>What was verified</h2>
<p class="meta" data-prose="data"><span class="num">{len(claims)}</span> claims, each re-fetched
  from its source before this deck shipped.</p>
<ol class="claims">{rows}</ol>"""

    beats, entry = "", ""
    for it in items:
        if it.get("id") == r.get("story"):
            beats = (f'<h2>Beats</h2><p class="meta" data-prose="data">'
                     f'<span class="tag">{e(it.get("topic", ""))}</span></p>')
            entry = (f'<p class="meta" data-prose="data">The record entry for this decision is '
                     f'<a href="../../item/{e(it["id"])}/">{e(it["title"])}</a>.</p>')
            break

    body = f"""
<article>
<h1>{e(r["title"])}</h1>
<p class="meta" data-prose="data"><span class="tag">Published {e(ordinal(d))}</span>
  <span>{r["slides"]} slides</span></p>

<h2>The deck</h2>
<div class="slides">{slides}</div>

<h2>The story</h2>
<div class="prose">{story}{entry}</div>
{claims_html}
{beats}
<p class="meta" data-prose="data"><a href="../">Every article</a></p>
</article>
"""
    flat = [s["text"] for b in (r.get("prose") or []) for s in b if not s["quote"]]
    # THE FIRST SENTENCE IS NOT A DESCRIPTION. This took `flat[0]` and stopped, so an article
    # opening "August 7th came and went." shipped a twenty-five character description, which
    # is what a search result then had to sell itself with. Sentences are added until there is
    # enough to read, and the cut lands on a sentence boundary rather than mid-word.
    desc = ""
    for sentence in (flat or [r["title"]]):
        nxt = (desc + " " + " ".join(sentence.split())).strip()
        if desc and len(nxt) > 160:
            break
        desc = nxt
        if len(desc) >= 110:
            break
    desc = desc[:180]

    # THE ARTICLE SAYS WHAT IT IS. These three pages are the only reporting on the site and
    # they were the only pages with no schema of their own, no article date, and the generic
    # site card on every share. They are also the pages most likely to answer a topical
    # question, which is exactly the case where a crawler needs to be told what it is holding.
    art_url = f'{SITE_URL}/articles/{r["date"]}/'
    story_item = next((i for i in items if i.get("id") == r.get("story")), None)
    item_url = f'{SITE_URL}/item/{story_item["id"]}/' if story_item else None
    card = f'og/article-{r["date"]}.png'
    extra_ld = [
        schema.article_node(SCHEMA_CTX, r, desc, f"{SITE_URL}/{card}", item_url),
        schema.breadcrumbs(SCHEMA_CTX, [("Texas AI Docket", ""), ("Articles", "articles/"),
                                        (r["title"], f'articles/{r["date"]}/')]),
    ]
    return page(title=f'{r["title"]} · {SITE_NAME}', depth=2, active="articles/",
                desc=desc, body=body, today=today, extra_ld=extra_ld,
                og_image=card, og_alt=r["title"], og_type="article",
                canonical=f'articles/{r["date"]}/')


def deck_preview(r: dict, sentences: int = 2, budget: int = 210) -> str:
    """The deck's own opening lines, for a card that would otherwise carry a title and a gap.

    WHAT WAS THERE AND WHY IT WENT BLANK. The card printed `copy.json`'s top level `hook`, which
    does not exist, so it rendered an empty paragraph. The repair pointed it at the title of the
    DECISION the deck is about, which is real prose and correctly gated, and which is empty on
    any run whose `story` is empty. Two of the three shipped runs carry no story, so the front
    page and the articles index both ended up showing a headline, two buttons and nothing in
    between. A card that says only what it is called is not a preview.

    THE DECK'S OWN WORDS ARE THE PREVIEW, and they are safe to publish here for the same reason
    the article page publishes them. Every figure in them traces to that run's claims, and
    `_run_numerals` hands exactly those to whichever page renders them. The `tease` field is one
    sentence, which is what made the articles index thin in the first place, so this reads the
    opening slide instead and takes whole sentences up to a budget.

    QUOTED BLOCKS ARE SKIPPED. A quotation needs its attribution beside it to be honest, a card
    has no room for one, and house style exempts quoted material from rules this text is being
    shown under. The first slide with prose of its own supplies the preview, so a deck that
    opens on a quote is previewed by the words around it rather than by somebody else's.
    """
    picked: list[str] = []
    for slide in (r.get("prose") or []):
        for block in slide or []:
            if (block or {}).get("quote"):
                continue
            text = " ".join(str((block or {}).get("text") or "").split())
            if text:
                picked.append(text)
        if picked:
            break
    joined = " ".join(picked)
    if not joined:
        return " ".join(str(r.get("tease") or "").split())

    out, used = [], 0
    for part in re.split(r"(?<=[.!?])\s+", joined):
        if not part:
            continue
        # WHOLE SENTENCES ONLY. A preview cut mid clause reads as a fault rather than as a
        # taste, and the budget is a ceiling on what gets in rather than a place to chop.
        if out and used + len(part) > budget:
            break
        out.append(part)
        used += len(part) + 1
        if len(out) >= sentences:
            break
    return " ".join(out)


def latest_article(runs: list, items: list) -> str:
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

    # WHAT THE CARD SAYS BESIDE THE COVER, and why it is not the deck's own words.
    #
    # This printed `copy.json`'s top level `hook`, which does not exist: hooks are per slide, so
    # the card carried a title and an empty paragraph. A reader saw "Terafab, Grimes County" and
    # nothing else, which says where but not what.
    #
    # The text comes from the DECISION the deck is about, not from the deck. `copy.json` names
    # its story, that item is already on this site, and its summary is already through the
    # numeral gate, the narration gate and the house style gate. Lifting a slide's prose here
    # instead would put figures on the front page that this build never computed, which is the
    # one thing the compute-not-generate law does not bend on.
    # THE ITEM'S TITLE, NOT THE FIRST SENTENCE OF ITS SUMMARY, and the reason is dates.
    #
    # These summaries open by dating the announcement, so the card read "August 16th" in its
    # own tag and then "Governor Greg Abbott announced on August 6th, 2026" in the paragraph
    # underneath. Two bare dates a line apart, meaning different things, with nothing saying
    # which was which. A reader cannot tell whether the story is ten days old or the page is.
    #
    # The item title says what happened without dating it, so the only date on the card is the
    # one in the tag, and the tag now says what that date IS.
    # The decision's title reads well and is empty on any run with no `story`, which is most of
    # them, so it is the SECOND choice now rather than the only one. See `deck_preview`.
    blurb = deck_preview(r)
    if not blurb:
        for it in items:
            if it.get("id") == r.get("story"):
                blurb = " ".join(str(it.get("title") or "").split())
                break

    story_link = (f'<a href="item/{e(r["story"])}/">the decision it is about</a>'
                  if r.get("story") else "")

    return f"""
<section data-reveal>
  <h2 data-voice="house">Our latest article</h2>
  <div class="latest">
    <a class="cover" href="articles/{e(r["date"])}/"><img
      src="{RAW}/runs/carousel/{e(r["date"])}/{e(r["cover"])}"
      width="1080" height="1350" loading="lazy"
      alt="Cover slide, {e(r["title"])}"></a>
    <div>
      <p class="meta" data-prose="data"><span class="tag">Published {e(ordinal(
        _dt.date.fromisoformat(r["date"])))}</span>
        <span>{r["slides"]} slides</span></p>
      <h3>{e(r["title"])}</h3>
      <p>{e(blurb)}</p>
      <div class="ctarow">
        <a class="cta ghost" href="articles/{e(r["date"])}/">Read it</a>
        {story_link and f'<a class="cta ghost" href="item/{e(r["story"])}/">The record entry</a>'}
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
  <h2 data-voice="house">Our latest video</h2>
  <div class="latest">
    <!-- CONTROLS, ALWAYS. A roughly 60 second film looping forever beside the copy with no
         pause, stop or hide is a WCAG 2.2.2 failure, and `prefers-reduced-motion` cannot
         reach media playback from CSS. The reader gets a control and the script below asks
         before it starts anything. -->
    <div class="vidwrap"><video id="hv" muted playsinline loop controls preload="none"
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
  if(!sec||!window.fetch)return;""" + js_feed_date() + """
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
    /* The thumb and the rendition when the publish step made them, the masters when it did
       not. This block is one frame and one film beside a paragraph, so it never needs the
       845 KB poster or the 3.5 Mbit master, and an entry from before the renditions existed
       still works. */
    var p=v.poster_thumb||v.poster;
    if(p)el.poster=abs(p);
    el.dataset.src=abs(v.video_mobile||v.video);
    document.getElementById('hvtitle').textContent=v.title||'';
    document.getElementById('hvcap').textContent=v.caption||'';
    document.getElementById('hvdate').textContent=fmtFeedDate(v.date);
    sec.hidden=false;
    var io=new IntersectionObserver(function(es){es.forEach(function(en){
      if(!en.isIntersecting)return;
      // AUTOPLAY ONLY IF NOBODY ASKED FOR LESS MOTION. The source still loads either way, so
      // pressing play is instant. Reduced motion is a request about movement, and a looping
      // film is the largest piece of movement on the page.
      if(!el.src){
        el.src=el.dataset.src;
        var calm=window.matchMedia&&window.matchMedia('(prefers-reduced-motion:reduce)').matches;
        if(!calm){var q=el.play();if(q&&q.catch)q.catch(function(){});}
      }
      io.disconnect();})},{rootMargin:'200px'});
    io.observe(sec);
  }).catch(function(){});
})();
</script>"""


def scan_teaser() -> str:
    """The Bottleneck Scanner's homepage front door.

    THE SIBLING PUTS THIS SECOND, directly under the hero. Here it is LAST, on the owner's call,
    and the placement is the argument. That site leads with a free tool. This one leads with a
    record, and a record that opens by selling something is a record that has told you what it
    is for. Somebody who has read down the whole page is also somebody who might want the scan.

    IT WEARS THE ASK BOX'S SHELL. This shipped as a `.leadform`, which is the stacked grid the
    contact and services pages use: a square cornered field at 34rem with a square button under
    it, in a full width section, a few screens below a full width rounded composer. Two form
    shapes on one page and neither explains the other.

    So the shell is now `.composer`, the same class the ask box wears, and the difference is the
    control: an arrow where the placeholder already said what the box does, a word where it has
    to name its own action. Shared as a class and not copied, because a shape written out twice
    is a shape that is wrong in both places at once.

    NO JS AND NO CAPTCHA HERE. The single field GETs to the scan page, which prefills it and runs
    the real flow behind its own captcha. A second Turnstile widget on the homepage would load a
    third party script on every visit to a page nobody came here to submit a form on.

    NO DIGITS, deliberately, same as the scan page. `numeral_lint` refuses a numeral the build
    did not compute, and "about twenty minutes" is a claim nobody measured.

    THE QUESTION IS THE READER'S, SO IT IS IN THEIR VOICE. The heading used to be "Would AI
    actually help your business", which is the record asking a prospect a question, and it read
    like a lead capture because that is the grammar of one. The question people actually have is
    first person, and `data-voice="reader"` is the existing, deliberate exemption for exactly
    that: the same mechanism the ask box's starter questions use. It does NOT license the record
    to speak as "we" anywhere else in this section, and it does not here.

    THE CREW IS NAMED BECAUSE IT IS REAL. Four agents run in the scanner repo and each has one
    job: `footprint-analyst`, `industry-scout`, `feasibility-mapper`, `scan-critic`. Describing
    what they each do is both the most futuristic thing this section can say and the most
    checkable, which is the only kind of impressive this site is allowed to be. The wording of
    each line is taken from that agent's own description, so it stays true by construction and a
    reader who later reads the report recognises the machinery.

    NOT COUNTED, deliberately. "Four agents" would be a figure about our own system that goes
    stale the day a fifth is added, and the page states no figures at all for the same reason
    the scan page does not: every number this section wants is a promise, not a measurement.
    """
    return """
<section data-reveal id="scan">
  <h2 class="scanq" data-voice="reader"><span>Would AI actually do anything for my business?</span></h2>
  <p class="scanlede">Drop your url in and an agent team goes to work on it.</p>
  <form class="composer scanform" action="scan/" method="get">
    <label class="vh" for="scan-url">Your website</label>
    <input type="text" name="url" id="scan-url" required placeholder="yourbusiness.com"
      autocomplete="url" inputmode="url">
    <button class="cta solid" type="submit">Run it</button>
  </form>
  <p class="chainlab">The agents on your run</p>
  <ol class="chain">
    <li><b>Footprint</b><span>your pages, cited</span></li>
    <li><b>Industry</b><span>what others already tried</span></li>
    <li><b>Feasibility</b><span>the lowest honest rung</span></li>
    <li><b>Critic</b><span>defaults to rejecting it</span></li>
  </ol>
  <p class="scanfoot">Free. One report. Every line links to the page it came from.</p>
</section>
"""


def home(items: list, today: str) -> str:
    proj = dk.project(items, today)
    act = proj["actionable_now"]
    lit = {c for it in items for c in (it.get("geography") or {}).get("counties") or []}
    svg = texas_map.render(lit=lit, links=county_links(items, today, 0),
                           counts=proj["by_county"])

    n_counties = len(lit)
    n_items = proj["counts"]["items"]
    n_claims = proj["counts"]["claims"]
    # The front page's index of the beats. Its figures are authorised by the same call that
    # renders them, which is why it hands back both.
    covers_html = covers_section(items, today)[1]
    runs = load_runs()
    n_videos = video_count()

    # WHAT STANDS IN FOR THE DEADLINE CARDS WHEN THERE ARE NONE.
    #
    # This was a pair. A clock widget for when something is open, and this line for when
    # nothing is, and the clock could never render: the cards below are built from the same
    # `act` list, so they are there whenever it is non-empty, and the template reaches for
    # this only when they are not. It was a second copy of `clock()` that had drifted, missing
    # both the singular and the closes-today wording, so it was also one day from reading "1
    # days left" if anything had ever shown it. One list, one branch, no ghost widget.
    lede = ('<div class="gap"><strong>No comment window on this record is open today.</strong>'
            ' Windows are checked every day, and one appears here the moment it opens.</div>')

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
        # A `<time>`, NOT A SPAN. The tile reads "SEP 8" at display size, which is a date
        # abbreviated the way a calendar abbreviates one and not the way this project writes a
        # date in a sentence. Carrying the ISO value in the element that shows it is what makes
        # that legitimate rather than an exception: the machine-readable date is right there,
        # the house style checker verifies the visible text renders it, and a search engine or
        # a screen reader gets the unambiguous value instead of three shouted letters.
        f'<time class="big" datetime="{e(a["closes"])}">{e(short_date(a["closes"]))}</time>'
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
    #
    # SOURCES CITED SITS BESIDE DECISIONS TRACKED, and the row takes five rather than four.
    # It used to be sixth of six behind a cap of four, which meant the figure never once
    # rendered. That was survivable while the sentence under "What this is" carried it, and
    # that section came off on 2026-08-21 as something a returning reader no longer needs.
    # Taking the section without moving the number would have quietly deleted the only count
    # on this page that says the record is SOURCED rather than merely long, which is the whole
    # claim the project rests on. The two belong next to each other because one qualifies the
    # other: sixty four decisions is a size, and sixty four decisions behind two hundred and
    # eighty three quoted sources is an argument.
    candidates = [
        (len(runs), "Articles written", False, ""),
        (n_videos, "Videos published", False, ' id="vidstat"'),
        (n_items, "Decisions tracked", False, ""),
        (n_claims, "Sources cited", False, ""),
        (len(act), "Doors open to you", True, ""),
        (n_counties, "Counties named", False, ""),
    ]
    stats = "".join(
        f'<div class="stat"{attrs}><span class="n{" hot" if hot else ""}">{v:02d}</span>'
        f'<span class="l">{e(label)}</span></div>'
        for v, label, hot, attrs in [c for c in candidates if c[0]][:5])

    body = f"""
<section class="hero rise">
  {telemetry(today)}
  <h1>AI is coming <em>South</em>.</h1>
  <p class="herolede">Every AI decision in Texas and the source behind it.</p>
  <div class="ctarow">
    <a class="cta solid" href="record/">The docket</a>
    <a class="cta ghost" href="grid/">The grid</a>
  </div>
  <div class="statrow">{stats}</div>
</section>

{ask_box(items, today)}

<section data-reveal>
  <h2>Where</h2>
  <div class="prose"><p>The lit counties are the ones this record currently touches,
  <span class="num">{n_counties}</span> of
  <span class="num">{_place_facts()["counties"]}</span>.</p></div>
  {svg}
  <p class="mapread" id="mapread" role="status" aria-live="polite" data-prose="data"></p>
  <button type="button" class="mapreset" id="mapreset" hidden>Show all of Texas</button>
</section>

{'<section data-reveal><h2>Closing next</h2><ul class="deck">' + rows + '</ul>'
   '<p class="meta" data-prose="data"><a href="record/">See all ' + str(n_items) + ' decisions</a></p>'
   '</section>' if rows else
   '<section data-reveal>' + lede + '<p class="meta" data-prose="data"><a href="record/">See all '
   + str(n_items) + ' decisions</a></p></section>'}


{covers_html}

{latest_article(runs, items)}

{latest_video()}

{scan_teaser()}
"""
    # THE TITLE TAG IS THE HIGHEST WEIGHTED THING ON THE PAGE and this spent it on the brand
    # alone. The brand stays first, so the query "Texas AI Docket" still matches exactly, and
    # the half that was empty now says what the site is for every query that is not the name.
    # Same words as the hero lede, deliberately: a title that promises one thing and a page
    # that opens on another is the mismatch a reader bounces off.
    return page(title=f"{SITE_NAME} · Every AI decision in Texas and the source behind it",
                depth=0, active="", home_page=True,
                desc=("A fact-checked record of AI decisions in Texas. Who decided, by when, "
                      "and whether you can still comment."),
                body=body, today=today, canonical="",
                # THE DATASET NODE THE WHOLE RECORD HANGS OFF. Every one of the 58 Reports says
                # it `isPartOf` this `@id`, so the node has to exist somewhere or all 58
                # references dangle. It is emitted here AND on `/record/`, which is legal and
                # is not duplication in the sense that matters: both come from one function, so
                # the two can never disagree. The homepage is where a data consumer lands.
                # NO BREADCRUMB HERE. The front page is the root of the trail, so a trail on it
                # would be a list of one, which says nothing and is the kind of markup added
                # for the sake of having markup.
                extra_ld=[{"@context": "https://schema.org",
                           **schema.dataset_node(SCHEMA_CTX, items, today)}])


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


# WHAT schema.py NEEDS FROM HERE, assembled once. It is built at this point in the file rather
# than at the top because it closes over the three label functions above, and it passes them
# rather than letting that module reimplement them: each label is a house rule with a written
# reason, and a second copy is how a URL and a heading drift apart.
SCHEMA_CTX = schema.Ctx(site_url=SITE_URL, site_name=SITE_NAME, topic_label=topic_label,
                        room_label=room_label, ordinal=ordinal, same_as=SAME_AS)


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
        # What the map's count is a count OF on this page. Without it the accessible title
        # announces a statewide figure that this page's own prose contradicts two lines above.
        map_scope = f"the items on this {place['name']} page"
    else:
        tx = _place_facts()
        scope = (f'<p class="gap">This county is in no federal statistical area, which is '
                 f'true of <span class="num">{tx["outside_any_metro"]}</span> of the '
                 f'state\'s <span class="num">{tx["counties"]}</span>. It gets its own page '
                 f'for that reason.</p>')
        head = f"{e(place['name'])} County"
        sub = "Outside every metropolitan and micropolitan area"
        map_scope = f"the items on this {place['name']} County page"

    body = f"""
<h1>{head}</h1>
<div class="prose">
  <p>{sub}. <span class="num">{len(mine)}</span>
  {"item" if len(mine) == 1 else "items"} in the record.</p>
  {scope}
</div>
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
                body=body, today=today, canonical="grid/", extra_css="facility.css",
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


def ask_box(items: list, today: str, base: str = "") -> str:
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
  <div id="ask" class="askbox lean" data-base="{e(base)}"
       data-endpoint="{e(ask_written.ENDPOINT)}"
       data-sitekey="{e(ask_written.TURNSTILE_SITEKEY)}">
    <!-- THE THREAD IS ABOVE THE FIELD. A conversation reads upward, and answers below the
         composer push the field down the page as the exchange grows, so the one control a
         reader wants is the one that keeps moving away from them.
         aria-live polite because sentences arrive one at a time after the press, and a reader
         on a screen reader would otherwise be told nothing was happening at all. -->
    <button type="button" class="askclose" id="askclose" aria-label="Close the search">
      <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true" focusable="false"><path d="M18 6L6 18M6 6l12 12"/></svg>
    </button>
    <div class="askthread" id="askthread" hidden aria-live="polite" aria-atomic="false"></div>
    <form class="composer" role="search">
      <label class="vh" for="askq">Ask the record a question</label>
      <input id="askq" type="search" autocomplete="off"
             placeholder="Ask about any AI decision in Texas">
      <button type="submit"><span class="vh">Ask</span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M12 19V5M5 12l7-7 7 7"/></svg></button>
    </form>
    {ask_written.note_html()}
    <div class="chips" data-voice="reader">{chips}</div>
    <!-- Turnstile renders here, and only after the field is focused. A reader who never asks
         anything never fetches Cloudflare's script, which is what keeps the note above
         literally true rather than nearly true. -->
    <div id="askts"></div>
  </div>
  {ask_written.dialog_html(FORM_ACTION.replace("formsubmit.co/", "formsubmit.co/ajax/"))}
</section>

<script>window.__ASK_INDEX__={json.dumps(idx, separators=(",", ":"))};
window.__ASK_CATALOGUE__={json.dumps(cat, separators=(",", ":"))};</script>
<script>{ask_answers.engine_js()}</script>
<script>{ask_written.client_js()}</script>
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

# The same calendar the sibling product books into, because it is the same person on the other
# end of it. It lives on the services page and nowhere else: a booking link under the ask box
# is an offer made to somebody who came to read a record, at the moment they are reading it.
BOOKING_URL = "https://calendly.com/talon-sturgill-ixzj/new-meeting"

# THE SCAN FORM HAS A SECOND PATH AS OF 2026-08-15. With JavaScript it posts to the gatekeeper,
# which verifies the captcha, enforces the daily and per-IP caps, FIRES THE SCAN ROUTINE
# immediately, and hands back the token that opens the watch page. Without JavaScript, or if
# that request never reaches the network, the plain FormSubmit POST above still happens and the
# maintainer still gets the email. The old path is the fallback rather than the ex-path, because
# a migration that can take the form down is a migration that will.
#
# THE GATEKEEPER MOVED ON 2026-08-20, from a Supabase Edge Function to a Cloudflare Worker, on
# the owner's call that Supabase was a flaky second vendor. Same host as the ask box's worker,
# which is the same account that already serves this domain and its Turnstile. The scanner repo
# holds its source at `workers/scan/` and the reasoning in its CLAUDE.md.
#
# The SITE key is public and is meant to ship in the page. Its matching SECRET is a Worker
# secret and appears nowhere in this repo.
# IMPORTED for the same reason ask_written imports its own: the policy in csp.py has to
# allowlist this host, and an allowlist that keeps a second copy of an address is a list
# that goes stale the first time the address moves.
SCAN_WORKER = csp.SCAN_ORIGIN
SCAN_ENDPOINT = f"{SCAN_WORKER}/request"
TURNSTILE_SITE_KEY = "0x4AAAAAAEQ2csplf8Pifi79"

# Kept OUT of the page f-string on purpose: every brace in this script would have to be doubled
# to survive one, and a doubled brace is a typo waiting to happen in the one file that decides
# whether a request reaches anybody.
_SCAN_JS = """
  <script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
  <script>
  (function () {
    var form = document.querySelector('#start form.leadform');
    if (!form) return;
    var endpoint = '__ENDPOINT__';
    // The homepage teaser hands the url over as ?url=. Prefill rather than making
    // somebody type it a second time, and never overwrite what they typed here.
    var q = new URLSearchParams(location.search).get('url');
    if (q) { var pre = form.querySelector('[name=website]'); if (pre && !pre.value) pre.value = q; }

    var status = form.querySelector('.scan-status');
    var button = form.querySelector('button[type=submit]');
    var val = function (n) { var e = form.querySelector('[name=' + n + ']'); return e ? e.value.trim() : ''; };
    var say = function (m) { status.textContent = m; status.hidden = false; };

    form.addEventListener('submit', function (ev) {
      // The honeypot. A bot fills it; a person never sees it. Say nothing useful.
      if (val('_honey')) { ev.preventDefault(); say('Thanks, we have got it.'); return; }

      ev.preventDefault();
      button.disabled = true;
      say('Sending.');

      fetch(endpoint, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          url: val('website'),
          notify_email: val('email'),
          booking_url: val('booking_url'),
          jobs: val('jobs_url'),
          note: val('message'),
          turnstile_token: (window.turnstile && window.turnstile.getResponse()) || ''
        })
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (b) {
          return { ok: r.ok, status: r.status, body: b };
        });
      }).then(function (res) {
        if (res.ok) {
          // THE TOKEN IS THE PAYOFF. The homepage says an agent team goes to work on your url
          // and that you can watch them; this is the moment that becomes true, so the requester
          // is taken to the page that watches rather than told to go away and wait. A cached
          // scan lands on the same page and finds it already finished, which is the honest
          // thing to show: somebody asked about this business recently and here is what came
          // back. The link is relative, and this form is served at /scan/.
          if (res.body && res.body.token) {
            // THE WATCH PAGE SHOWS WHOSE SCAN IT IS, and this is where it learns that. The
            // token is the only thing in the link, deliberately, so the subject travels in
            // sessionStorage instead: same origin, never in the address bar, never in a
            // referrer, gone when the tab closes. A shared link therefore carries no business
            // name, which is the property the token was chosen for in the first place, and the
            // watch page simply says less when it opens without one.
            try { sessionStorage.setItem('wsubject', val('website') || ''); } catch (e) {}
            location.href = 'watch/?t=' + encodeURIComponent(res.body.token);
            return;
          }
          // A 200 with no token should not happen. If it does, say the true thing rather than
          // sending somebody to a page with nothing to watch.
          form.innerHTML = '<p class="scan-status">Got it. The report goes to the address you ' +
            'gave, once a person has read it.</p>';
          return;
        }
        // A REFUSAL IS A DECISION AND IS NOT RETRIED. Falling through to the email path on a
        // 429 would post around the daily cap, which is the one thing standing between a
        // public form and a bill. Same for a 403 from the captcha and a 400 for a bad url:
        // the gatekeeper answered, and its answer is the point.
        //
        // BUT A GATEKEEPER THAT IS NOT THERE HAS NOT DECIDED ANYTHING. A 404 is what an
        // undeployed Worker's own hostname returns, and a 5xx is one that is broken or
        // unconfigured. Both used to land here and be shown to the requester as a refusal,
        // which loses the request: the fetch did not throw, so the email path below never ran.
        // That made the day between shipping this page and deploying the Worker a day with a
        // dead form and no queue behind it. Absence is an accident, so it takes the same path
        // an accident takes.
        if (res.status === 404 || res.status >= 500) { form.submit(); return; }
        button.disabled = false;
        if (window.turnstile) window.turnstile.reset();
        say(res.body.error || 'That did not go through. Try again in a moment.');
      }).catch(function () {
        // A NETWORK FAILURE IS AN ACCIDENT, so the request is not lost: submit the form the old
        // way and let the maintainer's mailbox be the queue.
        form.submit();
      });
    });
  })();
  </script>
""".replace("__ENDPOINT__", SCAN_ENDPOINT)


def field(fid: str, label: str, control: str, optional: bool = False,
          hint: str = "") -> str:
    """One form field, with a REAL label that stays on screen.

    WHAT THIS REPLACED, AND WHY IT WAS THE WHOLE PROBLEM. Every field on both forms carried a
    visually hidden label and repeated its text as a `placeholder`. That is the oldest tell in
    web form design and it is broken three ways besides. The name of the field disappears the
    moment somebody types, so a reader checking their own answer has nothing to check it
    against. A placeholder renders at a contrast no rule here would allow in body copy. Browser
    autofill paints over it, so the one moment a field is most likely to be wrong is the moment
    it is least likely to be labelled.

    The label is a mono uppercase kicker, which is the vocabulary this site already speaks in
    its footer, its colophon and its section cards. A form stops looking like a control panel
    bolted onto an editorial page and starts looking like part of one.
    """
    opt = ' <span class="opt">optional</span>' if optional else ""
    tip = f'<span class="hint">{e(hint)}</span>' if hint else ""
    return (f'<div class="field"><label for="{fid}">{e(label)}{opt}</label>'
            f'{control}{tip}</div>')


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
    # SAME FIELD SYSTEM AS THE SERVICES FORM, because they are the same component and were
    # drifting apart as two copies of one idea. Both carried placeholder-as-label; both now
    # carry a real one.
    site_f = field("sc-site", "Your website",
                   '<input id="sc-site" name="website" type="text" inputmode="url" required '
                   'autocomplete="url" spellcheck="false">')
    rmail_f = field("sc-mail", "Where the report should go",
                    '<input id="sc-mail" name="email" type="email" required '
                    'autocomplete="email" inputmode="email" spellcheck="false">')
    book_f = field("sc-book", "Booking page",
                   '<input id="sc-book" name="booking_url" type="text" inputmode="url" '
                   'spellcheck="false">', optional=True)
    jobs_f = field("sc-jobs", "Careers page",
                   '<input id="sc-jobs" name="jobs_url" type="text" inputmode="url" '
                   'spellcheck="false">', optional=True)
    note_f = field("sc-note", "Anything worth knowing",
                   '<textarea id="sc-note" name="message" rows="3"></textarea>', optional=True)

    body = f"""
<section class="hero" data-reveal>
  <h1>See where AI would actually help you</h1>
</section>

<section data-reveal>
  <h2>What comes back</h2>
  <div class="cards">
    <div class="card"><h3>Sourced to your own pages</h3><p>Every line traces to a page on your
    site. Each one is linked so you can check it. Nothing is inferred from another business and
    nothing is invented. A site too thin to support a true finding gets told exactly that.</p></div>
    <div class="card"><h3>The honest no</h3><p>Most operations have a pocket where a scale
    already counts it. Others have one a person clears in a couple of minutes. Those get marked
    leave-it-alone. They are the reason the rest of the report is worth reading.</p></div>
    <div class="card"><h3>What your industry already published</h3><p>What operators in the same
    line of work have published about trying the same thing. Also where it got rolled back. Their
    results are cited and linked. None of it is dressed up as a forecast about you.</p></div>
  </div>
</section>

<section id="start" data-reveal>
  <h2>Ask for one</h2>
  <p class="sub">One report to one address. No list. No follow-up sequence. No second email.</p>
  <form class="leadform" action="{FORM_ACTION}" method="POST">
    <input type="hidden" name="_subject" value="Texas AI Docket, bottleneck scan request">
    <!-- THE CAPTCHA IS ON HERE AND OFF ON THE SERVICES FORM, deliberately. Do not harmonise
         them. The scanner repo's CLAUDE.md names two abuse defenses and only two, the honeypot
         and FormSubmit's own handling, and the honeypot is the weaker half by a wide margin
         because a bot posting only the named fields never touches it. Off, that left roughly
         one defense standing.

         The two forms differ because what sits behind them differs. A services enquiry costs a
         maintainer the seconds it takes to read. A scan request is an item in a queue that
         costs money and runs research when it is picked up, which is what the scanner's COST
         AND ABUSE DISCIPLINE section is about. The extra click is the cheapest thing in the
         whole path.

         scanner_sync_check.py compares this value against the scanner's own copy. -->
    <input type="hidden" name="_captcha" value="true">
    <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
    {site_f}
    {rmail_f}
    <div class="row2">
      {book_f}
      {jobs_f}
    </div>
    {note_f}
    <div class="cf-turnstile" data-sitekey="{TURNSTILE_SITE_KEY}" data-theme="auto"></div>
    <button class="cta solid" type="submit">Send it</button>
    <p class="scan-status" role="status" aria-live="polite" hidden></p>
  </form>
{_SCAN_JS}
</section>
"""
    return page(title=f"Bottleneck scan · {SITE_NAME}", depth=1, active="",
                desc="An honest read of where AI would help a Texas business. Where ordinary "
                     "software is cheaper. What the industry has already published.",
                body=body, today=today, canonical="scan/")



# The read-only route on the same worker. The token is the credential and the browser never
# holds anything else.
SCAN_RESULT_URL = f"{SCAN_WORKER}/result"


def watch_page(today: str) -> str:
    """Watching your own scan run, which is the one page here that DOES phone somewhere.

    THE STAGE LIVES IN `scripts/site/watch_page.py`, and it is the only page on this site whose
    register is different. The reasoning, the promises it still keeps, and its own self-test are
    all in that module's docstring. Owner's call, 2026-08-20, after watching a run and finding
    the honest version of it genuinely dull to sit through.

    `body_html` takes the result endpoint rather than reading it, so the page and the policy in
    `csp.py` cannot end up pointing at two different workers.
    """
    return page(title=f"Your scan · {SITE_NAME}", depth=2, active="",
                desc="Watch a bottleneck scan run, by the token in your link.",
                body=watch_stage.body_html(SCAN_RESULT_URL), today=today,
                canonical="scan/watch/", body_class="stage")

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

    # THE FOUR FIELDS, BUILT BEFORE THE TEMPLATE so the label text sits in one readable place
    # rather than spread through markup. `autocomplete` is on every one of them, which is the
    # difference between a form a phone fills in one tap and a form a phone fights.
    name_f = field("lf-name", "Your name",
                   '<input id="lf-name" name="name" type="text" required '
                   'autocomplete="name" autocapitalize="words">')
    co_f = field("lf-co", "Company",
                 '<input id="lf-co" name="company" type="text" '
                 'autocomplete="organization">', optional=True)
    mail_f = field("lf-mail", "Email",
                   '<input id="lf-mail" name="email" type="email" required '
                   'autocomplete="email" inputmode="email" spellcheck="false">')
    msg_f = field("lf-msg", "What is the work",
                  '<textarea id="lf-msg" name="message" rows="5" required></textarea>',
                  hint="Say what a win would look like.")

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

<section id="start" data-reveal>
  <div class="startgrid">
    <div class="startsay">
      <h2>Start here</h2>
      <p class="sub">Say what the work is. A reply comes inside one business day.</p>
      <ul class="altways">
        <li><span class="k">Not ready</span>
          <a href="../scan/">Run the bottleneck scan</a>
          <p>Free. It reads your own site and says where AI would and would not help.</p></li>
        <li><span class="k">Rather talk</span>
          <a href="{BOOKING_URL}" target="_blank" rel="noopener">Book a call</a>
          <p>Skip the back and forth.</p></li>
      </ul>
    </div>
    <form class="leadform" action="{FORM_ACTION}" method="POST">
      <input type="hidden" name="_subject" value="Texas AI Docket, services enquiry">
      <input type="hidden" name="_captcha" value="false">
      <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off">
      <div class="row2">
        {name_f}
        {co_f}
      </div>
      {mail_f}
      {msg_f}
      <button class="cta solid" type="submit">Send it</button>
    </form>
  </div>
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
  decisions one at a time with the source attached.</p>
  <p>The same desk runs a working AI studio. Agentic systems and digital employees.
  Paperwork engines and assistants trained on a company's own files. That work lives on the
  <a href="../services/">services page</a>. Writing the beat every morning is exactly why the
  studio knows what actually pays.</p>

  <h2>How the work gets verified</h2>
  <p>Every fact carries a claim id and traces to a fetched document. At least one source on
  every item is the filing or the statute or the agency itself. An item that can't be
  re-verified says so on <a href="../record/">its own page</a>.</p>
  <p>Every numeral is produced by code. A build gate fails on any figure that traces to no
  computation. Where something is not public the gap is published instead of an estimate.</p>

  <h2>What you can hold this desk to</h2>
  <p><strong>Your outcome outranks the invoice.</strong> This desk recommends what it would
  do with its own money. Sometimes that is a smaller build. Sometimes it is no.</p>
  <p><strong>Plain talk both directions.</strong> Bad news arrives early and plain. No soft
  version. Same expected back. A problem said early is still small.</p>
  <p><strong>The build gets guarded even from the brief.</strong> Most AI projects die of
  enthusiasm. When the exciting ask and the right build disagree, you hear it. That judgement
  is what you pay for.</p>
  <p><strong>Nobody chases this desk.</strong> A reply lands inside one business day.</p>

  <h2>Where to find it</h2>
  <p>The record, the <a href="../articles/">articles</a> and the
  <a href="../videos/">videos</a> live here. For the studio, start at
  <a href="../services/">services</a>.</p>
</div>
"""
    return page(title=f"About · {SITE_NAME}", depth=1, active="about/", revised=False,
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
    # THE MOVEMENT LOG BELONGS IN THE TWIN TOO. The twin is the record as a machine reads it,
    # and the one thing a machine reader most often gets wrong about a decision is whether it
    # is still live. A dated line saying somebody looked on the 18th and nothing had changed
    # answers that better than the status word does, and leaving it out of the twin would build
    # the same gap one layer down that this whole section exists to close.
    movement = sorted((x for x in (it.get("history") or []) if isinstance(x, dict)),
                      key=lambda d: str(d.get("date", "")))
    if movement:
        lines += ["", "## How this decision moved", "",
                  "One dated line per check, oldest first. A line that says nothing changed "
                  "means somebody looked and it had not.", ""]
        for h in movement:
            lines.append(f'- {h["date"]} · {h.get("note") or ""}')
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


def _first_sentence(text: str, cap: int = 220) -> str:
    """A description that ends where a sentence ends, never mid word.

    THE BUG THIS FIXES was `summary[:110]`, a hard character cut that shipped
    "...amend its certificate of convenience and necessity to build the Dinosau" into the file
    a model reads to learn what this site holds. Fifty eight entries, every one truncated, many
    of them mid word. A machine reading that learns the record is unreliable, which is the exact
    opposite of the thing being advertised.
    """
    text = " ".join((text or "").split())
    if len(text) <= cap:
        return text
    cut = text[:cap]
    stop = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    if stop > cap * 0.5:
        return cut[:stop + 1]
    return cut[:cut.rfind(" ")].rstrip(",;") + "..."


def not_found_page(today: str, items: list) -> str:
    """The page a reader gets for a path that is not here.

    GitHub Pages serves `docs/404.html` for any unknown path. Without one, a mistyped decision
    id lands on the host's default page: no navigation, no way to search, and nothing saying
    the site is ours. The most common way to arrive here is a stale link to a decision, so the
    one useful thing to offer is the record itself and the box that answers questions about it.

    NOT IN THE SITEMAP and it carries no canonical, because it is not a destination. It is also
    the one page whose own URL is unknown at build time, which is why `canonical` points at the
    record rather than at itself.
    """
    body = f"""
<article>
<h1>That page is not here</h1>
<div class="prose">
  <p>The link may be old, or the address may have a typo in it. Nothing has been removed from
  this record, so a decision that was here is still here under its own address.</p>
  <p>The record carries <span class="num">{len(items)}</span> tracked decisions and every one
  of them is listed in one place.</p>
</div>
<p class="ctarow"><a class="cta solid" href="record/">Open the record</a>
<a class="cta ghost" href="./">Front page</a></p>
</article>
"""
    return page(title=f"Not found · {SITE_NAME}", depth=0, active=None,
                desc="That page is not here. The record and every tracked decision in it are "
                     "one link away.",
                body=body, today=today, canonical="record/")


def _cite_titles(text: str, titles: set) -> str:
    """Wrap every verbatim source title in `<cite>`, which is what it is.

    Marks quoted material as quoted so the numeral and style lints skip it, the same mechanism
    `house_style_check` has always used. Longest first, so a title containing another is not
    left in fragments. The text is ALREADY ESCAPED when this runs, so the titles are escaped to
    match before comparison.
    """
    for t in sorted(titles, key=len, reverse=True):
        text = text.replace(e(t), f"<cite>{e(t)}</cite>")
    return text


def _quoted_numerals(items: list) -> set:
    """Numerals that live inside a source's own title or url, for the two pages that print them.

    A docket number in "PUCT Interchange, Filings for 58000" is an IDENTIFIER inside QUOTED
    MATERIAL. It is not a measurement, it was not computed, and it is not ours to change: a
    document's title is the document's own words, which is the same reason `house_style_check`
    never lints a quotation.

    PASSED PER PAGE, NEVER ADDED TO THE SITE-WIDE SET. `_authorised_numerals` carries a warning
    earned twice over, that both times this gate was silently disabled the cause was an
    allowlist that grew wider than the page it guarded. Only the questions and sources pages
    print source titles, so only they get this.
    """
    out = set()
    for it in items:
        for c in it.get("claims") or []:
            for field in (c.get("source_title"), c.get("source_url")):
                if field:
                    out |= set(numeral_lint.NUMERAL.findall(field))
    return out


def _run_numerals(r: dict) -> set:
    """Every numeral one shipped deck is entitled to print, and where each one comes from.

    Two origins and no third. A figure was QUOTED from a source, so it is in a claim's verbatim
    quote or in the title of the document that quote came from. Or it was COMPUTED by the run,
    in which case it is in that run's `computed.json`, which is the file its own `compute.py`
    wrote and which the run's gates checked the slides against.

    A numeral the deck printed from neither is exactly what this gate exists to refuse, and it
    stays refused: nothing here authorises a figure by it having appeared on a slide.
    """
    out = set()
    for c in r.get("claims") or []:
        for field in (c.get("quote"), c.get("text"), c.get("source_title"), c.get("url")):
            if field:
                out |= set(numeral_lint.NUMERAL.findall(str(field)))

    computed = REPO_ROOT / "runs" / "carousel" / r["date"] / "computed.json"
    try:
        blob = json.loads(computed.read_text("utf-8"))
    except Exception:                                                # noqa: BLE001
        blob = None

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            out.add(str(node))
            out.add(f"{node:,}")
        elif isinstance(node, str):
            out.update(numeral_lint.NUMERAL.findall(node))

    walk(blob)
    return out


def question_groups(items: list, today: str) -> dict:
    """Every computed question and answer, grouped by the KIND of question it is.

    One place builds this, and both the hub and the twelve kind pages read it, so a question
    can't appear on one and not the other.
    """
    groups = {}
    for it in sorted(items, key=lambda i: i["title"]):
        for q, a in schema.qa_pairs(SCHEMA_CTX, it, today):
            groups.setdefault(schema.shape_of(q, it["title"]), []).append((it, q, a))
    return groups


def questions_check(groups: dict) -> None:
    """The frames and `schema.QUESTION_KINDS` agree, in both directions, on every build.

    A frame with no entry would silently drop its questions off the site entirely, because the
    hub only walks the map. An entry no frame produces would render an empty page that looks
    perfectly healthy. The second is the one that rots quietly, so both are a hard fail.
    """
    mapped = {shape for shape, _s, _h, _b in schema.QUESTION_KINDS}
    built = set(groups)
    if built - mapped:
        raise SystemExit("questions: qa_pairs produces a shape with no page: "
                         + ", ".join(sorted(built - mapped)))
    if mapped - built:
        raise SystemExit("questions: QUESTION_KINDS carries a shape nothing produces: "
                         + ", ".join(sorted(mapped - built)))


def _qa_rows(rows: list, titles: dict, depth: int) -> str:
    up = "../" * depth

    def one(it, q, a):
        # A LIST ANSWER IS MARKED AS DATA, and only once it has proved it is one. The check is
        # in `schema.list_answer_ok`, which reads the item's own county list, so an answer that
        # started carrying prose would fail the build rather than quietly inherit the exemption.
        listy = (schema.shape_of(q, it["title"]) in schema.LIST_ANSWER_SHAPES
                 and schema.list_answer_ok(it, a))
        if schema.shape_of(q, it["title"]) in schema.LIST_ANSWER_SHAPES and not listy:
            raise SystemExit(f'questions: {it["id"]} claims a list answer that is not one: {a}')
        mark = ' data-prose="data"' if listy else ""
        return (f'<details><summary>{e(q)}</summary><div class="prose">'
                f'<p{mark}>{_cite_titles(e(a), titles)}</p>'
                f'<p><a class="go" href="{up}item/{it["id"]}/">Open the decision</a>.</p>'
                f'</div></details>')

    return "".join(one(it, q, a) for it, q, a in rows)


def questions_hub(items: list, today: str) -> tuple:
    """The twelve kinds of question this record answers, each linking to its own page.

    WHY A HUB AND NOT A DOORWAY. The difference is whether anything is behind it. Every kind
    listed here has a page of real answers, and every answer is the same computed pair the item
    page emits as structured data, from `schema.qa_pairs`, so the page and the JSON-LD cannot
    drift and neither can be written independently of the ledger.

    WHY IT SPLIT. This was one page carrying all 633 pairs, 290 KB of HTML and 633 `<details>`
    elements, and it was the heaviest thing on the site by a factor of six. That is a slow page
    on a phone over cellular for no reason, and it is one title, one description and one
    canonical URL trying to be about twelve different questions at once. Split, each kind gets
    a page whose title is what it is about, which is both lighter to load and a far more
    targetable unit for the search that lands on it.

    ONE KIND PER PAGE rather than one decision per page, because a reader arrives with a KIND of
    question. Fifty eight blocks of ten questions is a database dump.
    """
    groups = question_groups(items, today)
    questions_check(groups)
    total = sum(len(v) for v in groups.values())
    figures = {str(total), str(len(schema.QUESTION_KINDS))}
    figures |= {str(len(v)) for v in groups.values()}

    cards = "".join(
        f'<li data-prose="data"><a class="dcard open" href="{slug}/">'
        f'<span class="big">{len(groups[shape]):02d}</span>'
        f'<span class="left">answered</span>'
        f'<h3>{e(head)}</h3><span class="note">{e(blurb)}</span></a></li>'
        for shape, slug, head, blurb in schema.QUESTION_KINDS if groups.get(shape))

    body = f"""
<article>
<h1>Questions this record answers</h1>
<div class="prose">
  <p>Every answer is assembled from the record itself, from the same fields the decision page
  prints. Nothing here is written separately, so an answer can't drift from the entry it
  describes.</p>
  <p>An answer the record can't support is not shown at all.</p>
</div>
<ul class="deck">{cards}</ul>
</article>
"""
    return figures, page(title=f"Questions · {SITE_NAME}", depth=1, active="record/",
                desc="Every question this record can answer about AI decisions in Texas, "
                     "answered from the record itself.",
                body=body, today=today, canonical="questions/",
                extra_ld=[schema.collection_node(
                              SCHEMA_CTX, name="Questions", path="questions/",
                              description="Questions answered from the tracked record.",
                              count=total),
                          schema.breadcrumbs(SCHEMA_CTX,
                                             [(SITE_NAME, ""), ("Questions", "questions/")])])


def questions_kind_page(items: list, today: str, kind: tuple) -> tuple:
    """One kind of question, asked of every decision on the record that can answer it."""
    shape, slug, head, blurb = kind
    groups = question_groups(items, today)
    rows = groups.get(shape) or []
    titles = schema.source_titles(items)
    figures = {str(len(rows))}

    others = "".join(
        f'<a href="../{s}/">{e(h)}</a>'
        for sh, s, h, _b in schema.QUESTION_KINDS if sh != shape and groups.get(sh))

    body = f"""
<article>
<h1>{e(head)}</h1>
<div class="prose">
  <p>{e(blurb)} Answered here for {len(rows)} of the decisions on the record, from the same
  fields the decision page prints.</p>
</div>
<div class="qa">{_qa_rows(rows, titles, 2)}</div>
<nav class="chips" aria-label="Other kinds of question">{others}</nav>
</article>
"""
    return figures, page(title=f"{head} · {SITE_NAME}", depth=2, active="record/",
                desc=f"{blurb} Answered from the Texas AI Docket for {len(rows)} decisions.",
                body=body, today=today, canonical=f"questions/{slug}/",
                extra_ld=[schema.collection_node(
                              SCHEMA_CTX, name=head, path=f"questions/{slug}/",
                              description=blurb, count=len(rows)),
                          schema.breadcrumbs(SCHEMA_CTX,
                                             [(SITE_NAME, ""), ("Questions", "questions/"),
                                              (head, f"questions/{slug}/")])])


def _src_stat(claims: int, primary: int, docs: int, entries: int) -> str:
    """The four figures a publisher carries, as one line, built once for both surfaces.

    EACH PAIR IS ITS OWN UNBREAKABLE SPAN. Written as a flat run of numbers and words the line
    wrapped between a figure and the word it belongs to, and "7" ended a line with "ENTRIES"
    starting the next one. A reader then has to pair them by meaning, which is the one job a
    stat line exists to do for them. Nowrap inside a pair and a wide gap between pairs is the
    whole rule, and it only works while both come from here rather than from two call sites.
    """
    def pair(n, one, many):
        return (f'<span class="st"><span class="num">{n}</span>'
                f'{one if n == 1 else many}</span>')
    return (pair(claims, "claim", "claims") + pair(primary, "primary", "primary")
            + pair(docs, "document", "documents") + pair(entries, "entry", "entries"))


def _host_slug(host: str) -> str:
    """A publisher's own page path, derived from its host and from nothing else.

    NOT A TITLE SLUG. A source title is the document's words and changes when the publisher
    retitles a page, and a URL that moves loses whatever rank it had. The host is the one part
    of a citation that is stable for as long as the publisher exists, so it is what the address
    is built from. `interchange.puc.texas.gov` becomes `interchange-puc-texas-gov`, which is
    ugly and permanent, and permanent is the half that matters for an address.
    """
    return re.sub(r"[^a-z0-9]+", "-", host.lower()).strip("-")


def source_pages(items: list, today: str) -> list:
    """One page per publisher, which is the form this archive has to take to be found.

    WHY NOT ONE LONG PAGE, which is what it was.
    A search engine indexes a URL. Forty publishers on one URL is one thing to rank, competing
    with itself for every query, and a reader arriving from a search for one of them lands at
    the top of a list of the other thirty nine. The archive already held everything a page
    about a publisher needs, which is what it has been cited for, how much of the record rests
    on it, and which decisions those are. It was just not addressable.

    WHAT MAKES THIS NOT A DOORWAY PAGE, and the distinction is the whole reason it is allowed.
    A doorway page is one that exists for a crawler and carries nothing for a reader. Every
    sentence and every figure here is computed from the ledger, each page carries the actual
    documents and the actual entries that rest on them, and a reader who followed a citation
    back to a publisher gets exactly what they came for. The pages are also the missing half
    of the item page's evidence block, which lists a source and until now was a dead end.

    THE LINK GOES BOTH WAYS, which is the part a sitemap cannot do for you. The hub ranks and
    links down, each publisher page links back to every entry that cites it, and every entry's
    evidence block links out to the publisher. A crawler that finds any one of the three finds
    the other two.
    """
    from urllib.parse import urlparse
    hosts = {}
    for it in items:
        for c in it.get("claims") or []:
            u = c.get("source_url")
            if not u:
                continue
            h = urlparse(u).netloc.removeprefix("www.")
            d = hosts.setdefault(h, {}).setdefault(
                u, {"title": c.get("source_title") or u, "type": c.get("source_type"),
                    "items": {}, "claims": 0})
            d["items"][it["id"]] = it["title"]
            d["claims"] += 1

    out = []
    for h in sorted(hosts):
        docs = hosts[h]
        n_claims = sum(d["claims"] for d in docs.values())
        n_primary = sum(1 for d in docs.values()
                        if str(d.get("type") or "").startswith("primary"))
        ent = {i: t for d in docs.values() for i, t in d["items"].items()}
        stat = _src_stat(n_claims, n_primary, len(docs), len(ent))
        rows = "".join(
            f'<li><a href="{e(u)}" rel="nofollow noopener"><cite>{e(d["title"])}</cite></a> '
            # THE VERB AGREES WITH THE COUNT, which is the fault `schema.py` caught as "One
            # source back it" and pinned with a self-test over every answer it can produce.
            # Pluralising the noun and leaving the verb alone reads correctly on the many and
            # wrong on the one, and most documents here carry several claims, so the broken
            # form only surfaces on the handful that carry exactly one.
            f'<span class="meta">{e((d["type"] or "").replace("_", " "))}, '
            f'<span class="num">{d["claims"]}</span> '
            f'{"claim rests" if d["claims"] == 1 else "claims rest"} on it</span></li>'
            for u, d in sorted(docs.items(), key=lambda kv: (-kv[1]["claims"], kv[1]["title"])))
        ents = "".join(
            f'<li><a href="../../item/{e(i)}/">{e(t)}</a></li>'
            for i, t in sorted(ent.items(), key=lambda kv: kv[1]))
        slug = _host_slug(h)
        body = f"""
<h1>{e(h)}</h1>
<div class="prose">
  <p>What the Texas AI Docket has checked against documents published at {e(h)}, and which
  decisions rest on them. Every quote in the record is the source's own words, fetched rather
  than remembered.</p>
</div>
<p class="srcstat" data-prose="data">{stat}</p>
<h2>The documents</h2>
<ul class="sources" data-prose="data">{rows}</ul>
<h2>The decisions that rest on them</h2>
<ul class="plainlist" data-prose="data">{ents}</ul>
<p class="meta" data-prose="data"><a href="../">Every source</a> ·
<a href="../../record/">All decisions</a></p>
"""
        # THE ENTRY TITLES THIS PAGE LISTS, on the record layer's own judgement about what in a
        # title is an identifier rather than a figure. "Ordinance 20260423-029" is the ordinance's
        # name and the item page already prints it on that basis, so the page that links to the
        # item inherits the same authority rather than re-deciding it here.
        figures = ({str(n_claims), str(n_primary), str(len(docs)), str(len(ent))}
                   | {str(d["claims"]) for d in docs.values()})
        for _t in ent.values():
            figures |= _identifier_numerals(str(_t))
        out.append((slug, figures, page(
            title=f"{h} · Sources · {SITE_NAME}", depth=2, active="record/",
            desc=f"The {len(docs)} document(s) from {h} that the Texas AI Docket has checked a "
                 f"claim against, and the {len(ent)} decision(s) that rest on them.",
            body=body, today=today, canonical=f"sources/{slug}/",
            extra_ld=[
                schema.collection_node(
                    SCHEMA_CTX, name=h, path=f"sources/{slug}/",
                    description=f"Documents published at {h} that the Texas AI Docket has "
                                f"checked a claim against.",
                    count=len(docs),
                    elements=[(t, f"item/{i}/") for i, t in
                              sorted(ent.items(), key=lambda kv: kv[1])]),
                schema.breadcrumbs(SCHEMA_CTX, [(SITE_NAME, ""), ("Sources", "sources/"),
                                                (h, f"sources/{slug}/")]),
            ])))
    return out


def sources_page(items: list, today: str) -> str:
    """Every document a claim in this record was checked against, grouped by who published it.

    THE PAGE THAT MAKES THE WHOLE ARGUMENT CHECKABLE. This record's claim is that every fact
    traces to a fetched source. Until this page existed a reader had to open 58 decisions to
    see the shape of that, and a machine had no single place to learn what this record rests on.

    GROUPED BY HOST, because "who says so" is the question a reader is actually asking, and a
    flat list of 95 urls answers it worse than a list of the bodies behind them.
    """
    from urllib.parse import urlparse
    hosts = {}
    for it in items:
        for c in it.get("claims") or []:
            u = c.get("source_url")
            if not u:
                continue
            h = urlparse(u).netloc.removeprefix("www.")
            hosts.setdefault(h, {}).setdefault(u, {"title": c.get("source_title") or u,
                                                   "type": c.get("source_type"), "items": set(),
                                                   "claims": 0})
            hosts[h][u]["items"].add(it["id"])
            # CLAIMS, NOT DOCUMENTS, is the weight that matters. Two entries can cite one filing
            # once each and a third can rest four separate facts on it, and only the claim count
            # tells those apart. It is how much of the record would fall over if the document
            # turned out to be wrong.
            hosts[h][u]["claims"] += 1

    def primary(d) -> bool:
        return str(d.get("type") or "").startswith("primary")

    # WHAT EACH PUBLISHER CARRIES, computed once and used for both the sort and the line the
    # reader sees, so the ranking and the figures explaining it can never disagree.
    tally = {h: {"docs": len(v),
                 "primary": sum(1 for d in v.values() if primary(d)),
                 "claims": sum(d["claims"] for d in v.values()),
                 "items": len({i for d in v.values() for i in d["items"]})}
             for h, v in hosts.items()}

    blocks = []
    # SORTED BY HOW MUCH OF THE RECORD RESTS ON THEM, not alphabetically. An alphabetical
    # archive ranks nothing, so a reader who wants to know who this record leans on has to read
    # all of it and keep a tally in their head. The page already had the counts to answer that
    # on the first screen and was sorting by the one field that carries no information. Ties
    # break on the host name, so the order is stable and the build stays deterministic.
    # THE HUB RANKS AND STOPS THERE. It used to print every document under every publisher,
    # which was the only sensible shape while this was one page. It stopped being sensible the
    # moment each publisher got its own, because then the hub and the fifty one pages carried
    # the same lists word for word, and a hub that duplicates the page it links to competes
    # with it for the query they both answer. So the hub does the one thing only it can do,
    # which is rank, and the documents live on the page that is about them.
    for h in sorted(hosts, key=lambda k: (-tally[k]["claims"], -tally[k]["docs"], k)):
        st = tally[h]
        stat = _src_stat(st["claims"], st["primary"], st["docs"], st["items"])
        blocks.append(
            f'<li><h2><a href="{e(_host_slug(h))}/">{e(h)}</a></h2>'
            f'<p class="srcstat" data-prose="data">{stat}</p></li>')

    n_docs = sum(len(v) for v in hosts.values())
    n_claims = sum(t["claims"] for t in tally.values())
    n_primary = sum(d["claims"] for v in hosts.values() for d in v.values() if primary(d))

    # THE NUMBER THAT TESTS THE PROMISE RATHER THAN DESCRIBING THE PILE.
    #
    # This page used to open with documents and publishers, which are facts about the archive's
    # SIZE. The claim the whole record makes is about its QUALITY, that a fact here rests on the
    # filing or the statute rather than on a report about one, and the share of claims sourced
    # to a primary document is the only figure that puts a number on it. Publishing it is worth
    # more than the count, in both directions: a share this project is not proud of is a share
    # its readers are entitled to see, and one it is proud of is worth more than saying so.
    body = f"""
<article>
<h1>Every source this record rests on</h1>
<div class="prose">
  <p>Each entry in the record carries a verbatim quote from a document that was fetched. At
  least one of those documents has to be the filing, the statute or the agency itself rather
  than a report about it. This is all of them, heaviest first.</p>
  <p><span class="num">{n_primary}</span> of <span class="num">{n_claims}</span> claims rest on
  a primary document, across <span class="num">{n_docs}</span> documents from
  <span class="num">{len(hosts)}</span> publishers.</p>
</div>
<ol class="srclist">{"".join(blocks)}</ol>
</article>
"""
    # THE FIGURES THIS PAGE COMPUTED, handed back with it. Authorising them at the call site by
    # guessing what the page prints is how an allowlist drifts from its page; returning them
    # from the computation that produced them is the only version that cannot.
    figures = {str(n_docs), str(len(hosts)), str(n_claims), str(n_primary)}
    figures |= {str(len(v)) for v in hosts.values()}
    figures |= {str(len(d["items"])) for v in hosts.values() for d in v.values()}
    figures |= {str(n) for t in tally.values() for n in t.values()}
    return figures, page(title=f"Sources · {SITE_NAME}", depth=1, active="record/",
                desc="Every document a claim in the Texas AI Docket was checked against, "
                     "grouped by publisher.",
                body=body, today=today, canonical="sources/",
                # THE HUB'S LIST NAMES ITS MEMBERS. A collection node carrying a count and no
                # elements tells a crawler how big the family is and nothing about where it
                # lives, which is the defect this file already fixed once for the beats. The
                # publishers go in ranked, so the node agrees with the page above it.
                extra_ld=[schema.collection_node(
                              SCHEMA_CTX, name="Sources", path="sources/",
                              description="Every document a claim was checked against, "
                                          "grouped by publisher and ranked by how much of the "
                                          "record rests on each one.",
                              count=len(hosts),
                              elements=[(h, f"sources/{_host_slug(h)}/") for h in
                                        sorted(hosts, key=lambda k: (-tally[k]["claims"],
                                                                     -tally[k]["docs"], k))]),
                          schema.breadcrumbs(SCHEMA_CTX,
                                             [(SITE_NAME, ""), ("Sources", "sources/")])])


def llms_txt(items: list, today: str) -> str:
    """The map of this site for a machine, in the community `llms.txt` shape.

    PUBLISHED AS CHEAP HYGIENE, and nothing on this site claims it does more. No major AI
    crawler documents that it reads `/llms.txt`. Google, Anthropic and Perplexity all name
    robots.txt as the control surface and none mention it. It is a community proposal, not a
    standard. Publishing costs one generated file from a build that already holds the index in
    memory. Claiming it works would be exactly the unverifiable assertion this project refuses.

    WHAT CHANGED, and why it was worth changing. The first version was one flat list of every
    item with each description cut at 110 characters, mid word. A flat list is not a map: it
    tells a reader what exists and nothing about what matters, and a truncated description is
    worse than none because it looks like the whole answer.

    THE ORDER IS THE ARGUMENT. What a person can still act on comes first, because a comment
    window that closes on Friday is the most perishable thing this record holds. Then the
    standing surfaces, then the whole record, then the data.
    """
    def line(i):
        return (f'- [{i["title"]}]({SITE_URL}/item/{i["id"]}/): '
                f'{_first_sentence(i["summary"])}')

    # The heading below promises a DATED way in, so the filter computes one. Room alone is the
    # kind of access the ledger recorded and says nothing about whether it is still open. See
    # `next_door` for the 28 finished votes this used to publish as live doors.
    open_now = [i for i in items
                if (i.get("public_access") or {}).get("room") in ("open_comment", "open_meeting")
                and next_door(i, today)]
    by_topic = {}
    for i in items:
        by_topic.setdefault(i["topic"], []).append(i)

    parts = [
        f"# {SITE_NAME}", "",
        "> A public, fact-checked record of decisions about artificial intelligence in Texas. "
        "Every entry carries verbatim quotes from the sources it rests on, and at least one "
        "primary source. Every numeral is computed from data, never written by a person.", "",
        "This record may be read, indexed, cited and quoted. Attribution to the "
        f"{SITE_NAME} with a link to the page is requested. No crawler is blocked. Every "
        "decision also exists as Markdown at the same path plus index.md, and the whole "
        "record is one fetch at /llms-full.txt.", "",
        "## Start here", "",
        f"- [The record, every tracked decision]({SITE_URL}/record/)",
        f"- [Questions answered from the record]({SITE_URL}/questions/)",
        f"- [Every source a claim was checked against]({SITE_URL}/sources/)",
        f"- [The data, its schema and its licence]({SITE_URL}/data/)",
        f"- [Texas Grid Watch, the daily ERCOT record]({SITE_URL}/grid/)",
        f"- [Texas Water Watch]({SITE_URL}/water/)",
        f"- [About this record]({SITE_URL}/about/)", "",
    ]

    # THE TWELVE QUESTION PAGES, NAMED. This file exists so a model can find the answer without
    # crawling, and one link to a hub is a link to twelve more links. Naming them here is the
    # difference between "questions are answered somewhere on this site" and "the page that
    # says who decides is at this URL". Generated from the same map the pages are, so a kind
    # can't be listed here and missing there.
    parts += ["## Questions, by what is being asked", "",
              "Each page answers one kind of question about every decision on the record.", ""]
    parts += [f"- [{head}]({SITE_URL}/questions/{slug}/): {blurb}"
              for _shape, slug, head, blurb in schema.QUESTION_KINDS]
    parts += [""]

    # THE PUBLISHERS, NAMED, for the same reason the question pages are. A model asked "what
    # does the Texas AI Docket rest on" can answer it from this file without crawling 51 pages,
    # and a model checking whether a specific agency's filings are tracked here gets a URL
    # rather than a hub. Ranked by how much of the record rests on each, so the order carries
    # the same information the page does.
    from urllib.parse import urlparse as _up
    _weight = {}
    for _it in items:
        for _c in _it.get("claims") or []:
            _h = _up(_c.get("source_url") or "").netloc.removeprefix("www.")
            if _h:
                _weight[_h] = _weight.get(_h, 0) + 1
    if _weight:
        parts += ["## What the record rests on, by publisher", "",
                  "Every document a claim here was checked against, grouped by who published "
                  "it. Heaviest first.", ""]
        parts += [f"- [{h}]({SITE_URL}/sources/{_host_slug(h)}/)"
                  for h in sorted(_weight, key=lambda k: (-_weight[k], k))]
        parts += [""]

    if open_now:
        parts += ["## Open right now", "",
                  "Decisions a member of the public still has a dated way into.", ""]
        parts += [line(i) for i in sorted(open_now, key=lambda x: x["title"])]
        parts += [""]

    parts += ["## The whole record, by beat", ""]
    for topic in sorted(by_topic):
        parts += [f"### {topic_label(topic)}", ""]
        parts += [line(i) for i in sorted(by_topic[topic], key=lambda x: x["title"])]
        parts += [""]

    parts += [
        "## Feeds", "",
        f"- [RSS]({SITE_URL}/feed.xml)",
        f"- [Atom]({SITE_URL}/atom.xml)",
        f"- [JSON Feed]({SITE_URL}/feed.json)", "",
        "## Data", "",
        f"- [The whole record as JSON]({SITE_URL}/docket.json), CC BY 4.0",
        f"- [Every decision as Markdown, one fetch]({SITE_URL}/llms-full.txt)",
        f"- [Grid Watch as JSON]({SITE_URL}/gridwatch.json)",
        f"- [Water Watch as JSON]({SITE_URL}/waterwatch.json)", "",
    ]
    return "\n".join(parts)


def llms_full_txt(items: list, today: str) -> str:
    """Every decision as Markdown in one fetch.

    THE HIGHEST VALUE FILE ON THIS SITE FOR A MACHINE READER, and it costs one concatenation of
    twins the build already writes. A model answering a question about Texas and AI can hold the
    entire record in one request rather than crawling 58 pages and parsing HTML out of each.

    Built from `item_markdown` rather than from a second rendering, so the one fetch and the 58
    fetches can never disagree. A separate renderer here would be a second vocabulary for the
    same record, which is the drift this project keeps having to design against.
    """
    head = [
        f"# {SITE_NAME}", "",
        "The whole record as plain Markdown, one decision after another, in the order they "
        "are filed. Every fact carries a quote from a source that was fetched, and at least "
        "one of those sources is the filing, the statute or the agency itself.", "",
        f"Licence CC BY 4.0. Built {ordinal(_dt.date.fromisoformat(today))}, {today[:4]}. "
        f"The canonical page for any decision below is {SITE_URL}/item/<id>/.", "",
        "---", "",
    ]
    body = []
    for it in sorted(items, key=lambda i: i["id"]):
        body += [item_markdown(it, today).rstrip(), "", "---", ""]
    return "\n".join(head + body)


def feed_xml(items: list, today: str) -> str:
    """RSS 2.0, beside the Atom and JSON feeds.

    Three feed formats is not indulgence. Atom is the better specification, JSON Feed is the
    easiest to consume, and RSS is the one every reader, aggregator and newsroom tool actually
    supports. Shipping the two better ones and not the common one is a purity that costs
    readers.
    """
    def rfc822(d: str) -> str:
        return _dt.date.fromisoformat(d).strftime("%a, %d %b %Y 00:00:00 +0000")

    latest = max((i["last_verified"] for i in items), default=today)
    rows = "".join(
        f"<item><title>{e(i['title'])}</title>"
        f"<link>{SITE_URL}/item/{i['id']}/</link>"
        f"<guid isPermaLink=\"true\">{SITE_URL}/item/{i['id']}/</guid>"
        f"<pubDate>{rfc822(i['last_verified'])}</pubDate>"
        f"<description>{e(i['summary'])}</description></item>"
        for i in sorted(items, key=lambda x: x["last_verified"], reverse=True))
    return ('<?xml version="1.0" encoding="utf-8"?>'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f"<title>{e(SITE_NAME)}</title><link>{SITE_URL}/</link>"
            f'<atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>'
            "<description>A public, fact-checked record of decisions about artificial "
            "intelligence in Texas.</description><language>en-US</language>"
            f"<lastBuildDate>{rfc822(latest)}</lastBuildDate>"
            f"{rows}</channel></rss>")


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


def _item_numerals(it: dict, today: str) -> set:
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
        # A NAME WITH A NUMBER IN IT, on the record layer's judgement rather than this one's.
        # "NewsChannel 6" is a broadcaster and `dk._name_numerals` decides that by asking
        # whether the item's own evidence carries the name, which is the same inheritance this
        # function already makes for statutes and dates. Stated here because without it the
        # page passed by luck: a single digit is almost always in the site-wide set from some
        # unrelated computation, so the gate was waving the name through for the wrong reason
        # and would have failed the day the number was less common.
        a.add(*dk._name_numerals(it, str(kd.get("note", ""))))

    # THE COUNT ON THE TIMELINE'S NEXT STATION, computed here by the same subtraction the
    # strip does and authorised because of it rather than in spite of it. This is the shape the
    # law asks for. The page does not get to print a figure and have the gate wave it through
    # for being small, so the figure is derived twice from the same two dates and the second
    # derivation is what lets it through.
    ks = sorted(k["date"] for k in (it.get("key_dates") or []) if k.get("date"))
    t = _dt.date.fromisoformat(today)
    nxt = next((k for k in ks if _dt.date.fromisoformat(k) > t), None)
    if nxt:
        a.add((_dt.date.fromisoformat(nxt) - t).days)

    # THE MOVEMENT LOG, and this is a carve-out rather than an oversight. `docket_build`'s
    # numeral gate excludes history notes for a structural reason, and the site layer has to
    # make the same exclusion or the record passes and the page it produces fails. A movement
    # line's whole job is to say what the record USED TO HOLD, "the filing index moved from
    # 5782 to 5790". The old figure is by definition in no current claim quote, because the
    # claim was updated to the new one. Holding the log to the numeral set would make the one
    # sentence a movement log exists to write unwriteable, and would push a run toward "the
    # index moved" with no figures at all, which is worse copy and a weaker record. The old
    # value's provenance is `ledger/docket.json`'s own git history, which is a stronger trace
    # than a quote because it carries the run that observed the change.
    #
    # PER ITEM, like everything else in this function. An old figure from one decision's log
    # is not a licence to print that figure on another decision's page, so the carve-out is
    # exactly as wide as the page that renders the line and no wider.
    for h in (it.get("history") or []):
        if not isinstance(h, dict):
            continue
        for n in dk.NUMERAL.findall(str(h.get("note", "")) + " " + str(h.get("date", ""))):
            a.add(n, n.replace(",", "").rstrip("%"))
        a.add(*str(h.get("date", "")).split("-"))

    # THE LICENCE VERSION, WHICH IS A NAME AND NOT A MEASUREMENT. "CC BY 4.0" names a document,
    # the same way "H.B. 149" and "Chapter 552" do, and the record layer already treats those as
    # identifiers rather than figures. Taken from `LICENCE` rather than written here, so a page
    # that starts printing a different licence fails this gate instead of quietly passing it.
    a.add(*dk.NUMERAL.findall(LICENCE))

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


# Files this build must preserve rather than produce. Externally owned, listed rather than
# pattern-matched so adding one is a deliberate act with a name attached.
CARRY_THROUGH = (Path("videos") / "videos.json",)




def _facility_desc(summary: str, limit: int = 180) -> str:
    """A meta description, cut at a sentence and never mid word.

    `summary[:180]` sliced the word "in" down to "i", and a bare "i" is a first person pronoun
    to the house style checker, which was right to flag it. A truncation that can invent a word
    is a truncation that can invent a claim.
    """
    s = " ".join(str(summary).split())
    if len(s) <= limit:
        return s
    cut = s[:limit]
    for stop in (". ", "? ", "! "):
        if stop in cut:
            return cut[:cut.rindex(stop) + 1].strip()
    return cut[:cut.rindex(" ")].strip() if " " in cut else cut


def facility_page(d: dict, today: str) -> str:
    """One certified data center, and everything the research could source about it."""
    name = d["name"]
    body = (
        f'<article class="prose facilitypage" data-proper-name="{e(name)}">'
        f'<p class="crumb"><a href="../../grid/">The Grid Watch</a> '
        f'<span aria-hidden="true">/</span> Every registered facility.</p>'
        f'<h1><cite>{e(name)}</cite></h1>'
        f'{facility_dossier.panel(d, heading=2)}'
        f'<p class="dfoot">The registry entry for this facility comes from the Texas '
        f'Comptroller\'s certified list of data centers holding a sales tax exemption. '
        f'Owner, occupant and operator are roles in that filing rather than descriptions '
        f'of who runs the building.</p>'
        f'</article>')
    return page(
        title=f"{name} · {SITE_NAME}",
        desc=_facility_desc(d.get("summary") or ""),
        body=body, depth=2, active=None, today=today,
        canonical=f"facility/{d['slug']}/",
        revised=False, extra_css="facility.css")



def company_page(item: dict, data: dict, dossiers: dict, is_group: bool, today: str) -> str:
    """One company, and every certified facility the state puts it on."""
    name = item["name"]
    kind = "group of entities" if is_group else "entity as the state files it"
    body = (
        f'<article class="prose companypage" data-proper-name="{e(name)}">'
        f'<p class="crumb"><a href="../../grid/">The Grid Watch</a> '
        f'<span aria-hidden="true">/</span> <a href="../">Who is behind the registry</a>.</p>'
        f'<h1><cite>{e(name)}</cite></h1>'
        f'<p class="ckind">Shown as a {kind}.</p>'
        f'{entities.panel(item, data, dossiers, is_group=is_group)}'
        f'<p class="dfoot">Owner, occupant and operator are roles in a sales tax exemption '
        f'filing rather than descriptions of who runs a building. Counts here are computed from '
        f"the Comptroller's certified list and nothing else.</p>"
        f'</article>')
    return page(
        title=f"{name} · {SITE_NAME}",
        desc=_facility_desc(f"Every Texas data center the certified registry puts "
                            f"{name} on, by role."),
        body=body, depth=2, active=None, today=today,
        canonical=f"company/{item['slug']}/",
        revised=False, extra_css="facility.css")



def _registry_field(data: dict) -> str:
    """The network, drawn from the same resolution the lists below are built from."""
    g = registry_graph.build(data["entities"])
    if not g["nodes"]:
        return ""
    n0 = entities.n0
    return (
        f'<div class="gwrap">'
        f'<div class="gfield" id="gfield">{registry_graph.svg(g)}</div>'
        # A LEGEND, not running prose. Four labelled chips with no full stop between them read as
        # one thirty word sentence to the length backstop, which is the measurement narrowing this
        # marker exists for. The construction rules still read every word of it.
        f'<p class="gkey" data-prose="data">'
        f'<span>Each point is a company on more than one facility.</span>'
        f'<span><b>Size</b> how many it appears on</span>'
        f'<span><b>Line</b> a facility two of them share</span>'
        f'<span><b>Thickness</b> how many they share</span></p>'
        # "Hover" is a verb a phone cannot perform, and this line is read on a phone.
        f'<p class="ghint">A pointer lights a company\'s neighborhood and can drag it across the '
        f'field. Every point is a link to that company, and the same information is listed '
        f'below.</p>'
        f'<script type="application/json" id="gdata">{registry_graph.payload(g)}</script>'
        f'<script>{registry_graph.SCRIPT}</script>'
        f'</div>')


def companies_index(data: dict, today: str) -> str:
    """The registry read down its columns instead of across its rows."""
    ents, groups = entities.published(data)
    split = entities.split_by_punctuation(data["entities"])
    n0 = entities.n0

    def row(x, is_group):
        roles = " ".join(f'<span class="crolechip">{k} {n0(len(v))}</span>'
                         for k, v in sorted(x["roles"].items()))
        return (f'<li><a href="{x["slug"]}/"><cite>{e(x["name"])}</cite></a> '
                f'<strong class="num">{n0(x["reach"])}</strong> {roles}</li>')

    body = (
        f'<article class="prose companyindex">'
        f'<p class="crumb"><a href="../grid/">The Grid Watch</a> '
        f'<span aria-hidden="true">/</span> Who is behind the registry.</p>'
        f'<h1>Who is behind the registry</h1>'
        f'<p>The certified list names <strong class="num">{n0(len(data["facilities"]))}</strong> '
        f'facilities and reads as that many unrelated buildings. It is not. '
        f'<strong class="num">{n0(sum(1 for x in data["entities"] if x["reach"] > 1))}</strong> '
        f'companies appear on more than one, and the largest relationships in Texas are only '
        f'visible reading down a column.</p>'
        + _registry_field(data)
        + f'<h2>Filed under more than one spelling</h2>'
        f'<p>Punctuation and capitalisation alone split '
        f'<strong class="num">{n0(len(split))}</strong> companies into separate rows. Counting '
        f'the strings rather than the companies reports the largest occupant in the state as two '
        f'smaller ones.</p>'
        f'<ul class="csplit" data-prose="data">'
        + "".join(f'<li><strong class="num">{n0(x["reach"])}</strong> '
                  + " ".join(f"<cite>{e(v)}</cite>" for v in x["variants"]) + "</li>"
                  for x in split)
        + f'</ul>'
        f'<h2>Companies, as the state spells them</h2>'
        f'<p class="qnote">Resolved mechanically. Case, punctuation and the corporate suffix are '
        f'ignored. Nothing else is.</p>'
        f'<ul class="clist" data-prose="data">' + "".join(row(x, False) for x in ents) + "</ul>"
        f'<h2>Grouped by parent</h2>'
        f'<p class="qnote">A judgment rather than a rule. Each grouping states its reason on '
        f"its own page. Where the two layers disagree the mechanical one above is the "
        f"defensible number.</p>"
        f'<ul class="clist" data-prose="data">' + "".join(row(x, True) for x in groups) + "</ul>"
        f'</article>')
    return page(
        title=f"Who is behind the registry · {SITE_NAME}",
        desc="Every company the Texas data center registry names, resolved across the spellings "
             "the state filed them under, with every facility and role.",
        body=body, depth=1, active=None, today=today,
        canonical="company/", revised=False, extra_css="facility.css")



def construction_page(data: dict, reg: dict, today: str) -> str:
    """What the OTHER state register says, and where the two disagree.

    Every figure on this page comes out of `tdlr_projects`, which computes it from the filings.
    Nothing here is typed, and nothing here asserts that a filing and a certification are the
    same building, because the state never published that join.
    """
    n0 = entities.n0
    recs = data.get("projects") or []
    sa = tdlr_projects.scoped(recs, ("Bexar", "Medina"))
    t = tdlr_projects.totals(sa)
    groups = tdlr_projects.by_designation(sa)
    conflicts = tdlr_projects.county_conflicts(recs)

    def money(v):
        return f"${v / 1_000_000_000:.2f} billion" if v >= 1_000_000_000 else f"${n0(v)}"

    def row(g):
        sq = f'<strong class="num">{n0(g["sqft"])}</strong> sq ft' if g["sqft"] else ""
        nf = n0(g["filings"])
        fil = f'{nf} filing' + ("" if g["filings"] == 1 else "s")
        if len(g["buildings"]) > 1:
            fil += f', {n0(len(g["buildings"]))} buildings'
        return (f'<div class="cbrow"><span class="cbd">{e(g["designation"])}</span>'
                f'<span class="cbm"><strong class="num">{e(money(g["cost"]))}</strong></span>'
                f'<span class="cbs">{sq}</span>'
                f'<span class="cbf">{fil}</span>'
                f'<span class="cbc">{e(", ".join(g["counties"]))}</span></div>')

    rows = "".join(row(g) for g in groups)

    # The two registers, side by side, with no claim that a row and a filing are one building.
    certified = sorted({f["name"] for f in reg.get("facilities") or []
                        if any("Microsoft" in x for x in (f.get("occupants") or []))
                        and "SAT" in f["name"].upper()})
    named = tdlr_projects.covered(sa)

    conf = ""
    for c in conflicts:
        lines = "".join(
            f'<li><cite>{e(f["project"])}</cite> gives <cite>{e(f["county"])}</cite> '
            f'at <cite>{e(f["address"])}</cite></li>' for f in c["filings"])
        conf += (f'<h3>One postcode, two counties</h3>'
                 f'<p>Postcode <strong class="num">{e(c["postcode"])}</strong> carries filings '
                 f'naming {e(" and ".join(c["counties"]))}. This page reports the disagreement '
                 f'rather than choosing a side.</p>'
                 f'<ul class="rcl" data-prose="data">{lines}</ul>')

    body = (
        f'<article class="prose construction">'
        f'<p class="crumb"><a href="../grid/">The Grid Watch</a> '
        f'<span aria-hidden="true">/</span> The construction register.</p>'
        f'<h1>What the builders told a different agency</h1>'
        f'<p>The Comptroller certifies who holds a tax exemption on a data center. It records no '
        f'address, no size and no cost. A second state register does. Every large commercial '
        f'project is registered with the Department of Licensing and Regulation. That filing '
        f'carries a street address, a county, a square footage, an estimated cost and a '
        f'schedule.</p>'
        f'<p>Reading both is how the shape of a buildout becomes visible. This page holds '
        f'Microsoft in the San Antonio area. That is where the two registers diverge most.</p>'
        f'<p class="qnote" data-prose="data">'
        f'<strong class="num">{n0(t["filings"])}</strong> filings, '
        f'<strong class="num">{n0(t["new_build"])}</strong> of them new construction, '
        f'<strong class="num">{e(money(t["cost"]))}</strong> estimated, '
        f'<strong class="num">{n0(t["sqft"])}</strong> sq ft across '
        f'<strong class="num">{n0(t["sqft_known"])}</strong> of them, first started '
        f'<time datetime="{e(t["first"])}">{e(facility_dossier.ordinal(t["first"]))}</time>.</p>'
        f'<h2>By designation, as filed</h2>'
        f'<p>A designation filed twice is one row here and two filings. A cost counted once per '
        f'filing would report a building twice. A filing naming a range of buildings keeps its '
        f'single cost for the same reason.</p>'
        f'<div class="cbtable" data-prose="data">{rows}</div>'
        f'<h2>What each register names</h2>'
        f'<p>Neither list is wrong. They record different acts, and only one of them is about '
        f'buildings.</p>'
        f'<div class="ctwo" data-prose="data">'
        f'<div><h3>Certified for the exemption</h3><ul class="rcl">'
        + "".join(f"<li><cite>{e(x)}</cite></li>" for x in certified) + '</ul></div>'
        f'<div><h3>Named in a construction filing</h3><ul class="rcl">'
        + "".join(f"<li><cite>{e(x)}</cite></li>" for x in named) + '</ul></div>'
        f'</div>'
        + conf +
        f'<p class="qnote">This page names no person. A filing carries the contact who submitted '
        f'it and the specialist who inspects it. The parser drops both before anything reaches a '
        f'file here.</p>'
        f'</article>')
    return page(
        title=f"The construction register \u00b7 {SITE_NAME}",
        desc="Texas registers every large commercial construction project with a second agency. "
             "What Microsoft filed in the San Antonio area, beside what it certified.",
        body=body, depth=1, active=None, today=today,
        canonical="construction/", revised=False, extra_css="facility.css")


def registry_changes_page(data: dict, today: str) -> str:
    """What the state has quietly changed since anyone started looking."""
    n0 = entities.n0
    hist = list(reversed(data["history"]))
    blocks = []
    for h in hist:
        parts = []
        if h["added"]:
            parts.append(f'<h3>Added <strong class="num">{n0(len(h["added"]))}</strong></h3>'
                         f'<ul class="rcl" data-prose="data">'
                         + "".join(f"<li><cite>{e(x)}</cite></li>" for x in h["added"]) + "</ul>")
        if h["removed"]:
            parts.append(f'<h3>Removed <strong class="num">{n0(len(h["removed"]))}</strong></h3>'
                         f'<ul class="rcl" data-prose="data">'
                         + "".join(f"<li><cite>{e(x)}</cite></li>" for x in h["removed"]) + "</ul>")
        if h["substantive"]:
            rows = ""
            for c in h["substantive"]:
                moved = "".join(
                    f'<div class="rcf"><span class="rcfl">{e(f["label"])}</span>'
                    f'<span class="rcwas"><span class="rcw">was</span>'
                    f'<cite>{e(f["was"]) or "not stated"}</cite></span>'
                    f'<span class="rcnow"><span class="rcw">now</span>'
                    f'<cite>{e(f["now"]) or "not stated"}</cite></span>'
                    f'</div>'
                    for f in registry_changes.fields(c))
                rows += f'<li><cite>{e(c["name"])}</cite>{moved}</li>'
            parts.append(f'<h3>Rewritten in place '
                         f'<strong class="num">{n0(len(h["substantive"]))}</strong></h3>'
                         f'<ul class="rcl" data-prose="data">{rows}</ul>')
        if not parts:
            parts.append('<p class="qnote">Nothing moved.</p>')
        blocks.append(f'<section class="rcday"><h2>'
                      f'<time datetime="{e(h["to"])}">{e(h["to"])}</time></h2>'
                      + "".join(parts) + "</section>")

    body = (
        f'<article class="prose regchanges">'
        f'<p class="crumb"><a href="../grid/">The Grid Watch</a> '
        f'<span aria-hidden="true">/</span> What the registry changed.</p>'
        f'<h1>What the registry changed</h1>'
        f'<p>The certified list is not append only. Rows are added, and existing rows are '
        f'rewritten while keeping their original effective date. A row therefore names who holds '
        f'an exemption now. It does not name who held it when the exemption was granted.</p>'
        f'<p>This page compares every reading the collector has kept. It ignores a date that was '
        f'only reformatted, because burying an owner swap under punctuation noise is how a watch '
        f'stops being read.</p>'
        f'<p class="qnote">The record begins with the first reading on '
        f'<time datetime="{e(data["first"] or "")}">{e(data["first"] or "")}</time> and covers '
        f'<strong class="num">{n0(data["readings"])}</strong> readings. Nothing before that can '
        f'be reported, and the list was not necessarily stable before anyone was looking.</p>'
        + "".join(blocks) + "</article>")
    return page(
        title=f"What the registry changed · {SITE_NAME}",
        desc="The Texas certified data center list is edited in place. Every change between "
             "readings, with the rows that were rewritten.",
        body=body, depth=1, active=None, today=today,
        canonical="registry-changes/", revised=False, extra_css="facility.css")


def build(out: Path, today: str) -> dict:
    items = dk.load(LEDGER)
    runs = load_runs()
    # blocking_only: a stale record still rebuilds, loudly. See NON_BLOCKING_FOR_BUILD in
    # docket_build. Refusing to rebuild because the input is old leaves the reader with an
    # even older page, which is the wrong party paying for the run's debt.
    bad, results = dk.run_gates(items, today, blocking_only=True)
    stale = [r for r in results if r.name in dk.NON_BLOCKING_FOR_BUILD and r.status == "FAIL"]
    if bad:
        dk.report(results)
        raise SystemExit("site_build: the record does not pass its own gates; refusing to build")
    if stale:
        dk.report(results)
        print("site_build: BUILDING ANYWAY, but the record is stale and `--validate` will fail. "
              "Re-verify the items named above. This is a debt, not a pass.")

    # THE ONE FILE THIS BUILD DOES NOT OWN AND MUST NOT DESTROY.
    #
    # `ownership.yaml` says of `docs/videos/videos.json`: "No build in this repo may write,
    # reformat, or delete it, and site_build copies it through verbatim." It did not copy it
    # through. The wipe below removes everything not in this build's manifest, and the feed is
    # written by the publish step in `TexasAIDispatch` rather than produced here, so an in-place
    # rebuild deleted the sibling repo's only artifact in this repo.
    #
    # Worse, and this is why it went unnoticed: `video_feed()` reads the file from the repo root,
    # so after the wipe a rebuild counted ZERO videos and wrote an index that disagreed with the
    # feed still sitting in git. `site_fresh_check` cannot see any of it, because it builds into
    # a temp directory where the deletion never touches the real file.
    #
    # Found on 2026-08-19, when the first Dispatch feed entry was published and CI went red on a
    # single stat tile. Carried through here, byte for byte, exactly as the ownership note says.
    carried: dict[Path, bytes] = {}
    for rel in CARRY_THROUGH:
        src = out / rel
        if src.is_file():
            carried[rel] = src.read_bytes()

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for rel, blob in carried.items():
        dest = out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(blob)

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
    by_item = {it["id"]: _item_numerals(it, today) for it in items}
    unauthorised: list[str] = []
    broken: list[str] = []
    connect_seen: set[str] = set()          # content security policy findings, per page
    pages: dict[str, tuple[str, set]] = {}

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
            # Held so the revision-date pass below can substitute the real date in and
            # re-check the page it actually ships. The token carries no numeral, so linting
            # here and again after substitution is the same check over strictly more text.
            pages[path] = (text, extra or set())
            stray = numeral_lint.scan(text, authorised | (extra or set()))
            if stray:
                unauthorised.append(f"{path}: {', '.join(stray[:8])}")

    def listed(subset: list) -> set:
        """The union over exactly the items a listing page renders."""
        return set().union(*(by_item[i["id"]] for i in subset)) if subset else set()

    w("site.css", theme.css())
    # SERVED TO THE ONE PAGE THAT HAS A CALENDAR. See theme.record_css for why it is not in
    # the sheet every other page waits on.
    w("record.css", theme.record_css())
    w("facility.css", theme.facility_css())

    # THE CUSTOM DOMAIN, told to GitHub Pages. Derived from SITE_URL rather than typed, so the
    # domain the pages claim as canonical and the domain Pages actually serves cannot disagree.
    #
    # It has to be IN THE ARTIFACT, not only in the repository's Pages settings. This site
    # deploys through Actions, and an Actions deploy publishes exactly what the artifact
    # contains: a custom domain set in settings but missing from the upload gets dropped on the
    # next deploy, and the site silently reverts to the github.io hostname.
    (out / "CNAME").write_text(SITE_URL.split("//", 1)[1].rstrip("/") + "\n", encoding="utf-8")
    written.append("CNAME")

    # THE FILM GRAIN, as its own asset. It used to be a 12 KB base64 data URI inside site.css,
    # which is close to incompressible and sat in the middle of a render blocking download, so a
    # decorative texture was delaying first paint on every page. Written from the generator rather
    # than copied, because it is computed from three named constants and is byte-deterministic.
    (out / theme.GRAIN_FILE).write_bytes(grain.png())
    written.append(theme.GRAIN_FILE)

    # THE TAB ICON. Every page declares it, and `favicon.ico` also sits at the site root for the
    # request a browser makes on its own before it has parsed any markup. Generated from the same
    # statute as the wordmark rather than committed as a binary, for grain.py's reason: an icon
    # that can go missing without throwing puts the generic globe back on a green build.
    # THE SOCIAL CARD. Absolute url in the tags, so a scraper resolving against its own base
    # cannot miss it, which is the most common way a card silently fails.
    # THE INDEXNOW OWNERSHIP FILE. Served at the site root, containing the key and nothing
    # else. Without it every submission fails verification, so it is written by the build
    # rather than committed by hand and hoped for.
    w(indexnow.KEY_FILE, indexnow.key_file_contents())

    for name, blob in og.files(items, runs).items():
        # The per-decision cards live in their own directory, which has to exist first. The
        # site card sits at the root beside the favicon.
        (out / name).parent.mkdir(parents=True, exist_ok=True)
        (out / name).write_bytes(blob)
        written.append(name)

    for name, blob in favicon.files().items():
        (out / name).write_bytes(blob)
        written.append(name)

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

    w("index.html", home(items, today),
      _home_numerals(items, today) | listed(items) | covers_section(items, today)[0]
      | (_run_numerals(runs[0]) if runs else set()))
    # THE VERSION THE LEDGER ALREADY CARRIES, PUBLISHED RATHER THAN DISCARDED.
    #
    # This rebuilt `_spec` from scratch with only the build date, so `version` and `gates`
    # existed in `ledger/docket.json` and reached no reader. The file is open data under
    # CC BY, so the one thing a consumer needs, which is whether their parser still works,
    # was the one thing the publish step dropped. Same shape as the site URL, the hashtags
    # and the progress counter: a value stated in one place and a surface keeping its own
    # copy of it. `dk.SPEC_VERSION` carries the rule that governs when it moves.
    w("docket.json", json.dumps(
        {"_spec": {"version": dk.SPEC_VERSION, "generated": today,
                   "license": schema.LICENSE,
                   "rule": "version rises only when a parser would break. A new field or a "
                           "new topic never moves it."},
         "items": items}, indent=2, ensure_ascii=False) + "\n")
    for it in items:
        w(f'item/{it["id"]}/index.html', item_page(it, today), by_item[it["id"]])
        # The Markdown twin. A crawler that fetches this gets the record without parsing HTML,
        # and a model quoting from it is far less likely to mangle a figure.
        w(f'item/{it["id"]}/index.md', item_markdown(it, today))
    w("atom.xml", atom(items, today))
    w("feed.json", feed_json(items, today))
    # THE TWO HUBS. Views over the record, never doorway pages: every sentence on them is
    # computed from the ledger, and the questions page shares `schema.qa_pairs` with the
    # structured data so the page and the JSON-LD cannot say different things.
    _quoted = _quoted_numerals(items)
    _allnums = (set().union(*(schema.authorised_numerals(i, today) for i in items))
                if items else set())
    _qfig, _qhtml = questions_hub(items, today)
    w("questions/index.html", _qhtml, extra=_allnums | _quoted | _qfig)
    # ONE PAGE PER KIND OF QUESTION. The hub above walks the same map, and `questions_check`
    # fails the build if the map and the frames disagree either way, so a kind cannot be
    # answered on the site without being linked from the hub or listed without existing.
    for _kind in schema.QUESTION_KINDS:
        _kfig, _khtml = questions_kind_page(items, today, _kind)
        w(f"questions/{_kind[1]}/index.html", _khtml, extra=_allnums | _quoted | _kfig)
    _sfig, _shtml = sources_page(items, today)
    w("sources/index.html", _shtml, extra=_quoted | _sfig)
    # ONE PAGE PER PUBLISHER, written straight after the hub that ranks them, so the family
    # reads as a family here the way the beats and the question kinds do. Each one lands in
    # the sitemap by being an index.html, which is the rule the loop at the end of this build
    # already applies to every other page.
    for _sslug, _ssfig, _sshtml in source_pages(items, today):
        w(f"sources/{_sslug}/index.html", _sshtml, extra=_quoted | _ssfig)
    w("llms.txt", llms_txt(items, today))
    # THE WHOLE RECORD IN ONE FETCH, built from the same twins the item pages ship so the one
    # fetch and the 58 fetches can never disagree.
    w("llms-full.txt", llms_full_txt(items, today))
    # RSS beside Atom and JSON Feed. Atom is the better spec and RSS is the one every reader
    # actually supports, so shipping only the better one is a purity that costs readers.
    w("feed.xml", feed_xml(items, today))
    # A 404 THAT IS A WAY BACK IN, not a dead end. GitHub Pages serves docs/404.html for any
    # unknown path, and without one a mistyped decision id lands a reader on the host's default
    # page with no navigation, no search and no sign the site is even ours.
    w("404.html", not_found_page(today, items))
    # THE RECORD AUTHORISES ITS OWN ARITHMETIC. `listed` covers the figures the items carry;
    # the calendar's counts, day numbers and years are computed on the page and come back with
    # it, so the two sets are unioned rather than one silently standing in for the other.
    _rec_html, _rec_figs = docket_index(items, today)
    w("record/index.html", _rec_html, listed(items) | _rec_figs)
    # THE HUB, THEN THE BEATS. Written above the loop so the family reads as a family, and
    # so a reader or a crawler arriving at /topic/ finds a page rather than a 404.
    _tfig, _thtml = topics_index(items, today)
    w("topic/index.html", _thtml, extra=_tfig)
    for t in sorted({i["topic"] for i in items}):
        w(f"topic/{t}/index.html", topic_page(t, items, today),
          listed([i for i in items if i["topic"] == t]))

    # A PAGE PER RESEARCHED FACILITY. The registry names 151 data centers and gives five
    # fields each. These are the ones somebody actually researched, and each gets a real url
    # so a reader who searches the facility by name can land on it. The dialog on the grid
    # page renders the SAME `panel` call, so the two surfaces cannot drift.
    _doss = facility_dossier.load()
    for _d in _doss.get("dossiers") or []:
        w(f"facility/{_d['slug']}/index.html", facility_page(_d, today),
          facility_dossier.authorised({"dossiers": [_d]}))

    # WHO IS BEHIND THE REGISTRY. The same 151 rows read down their columns. Every count on
    # these pages is computed from the certified list, and the resolution that makes the counts
    # correct is in entities.py with the comma problem it exists for.
    _ent = entities.load()
    _dmap = {x["name"]: x for x in (_doss.get("dossiers") or [])}
    _enums = entities.authorised(_ent)
    w("company/index.html", companies_index(_ent, today), _enums)

    # WHAT THE STATE QUIETLY CHANGED. A pure function of the raw snapshots the collector keeps.
    _rc = registry_changes.load()
    if _rc["readings"] >= 2:
        _rcnums = {entities.n0(_rc["readings"])}
        for _h in _rc["history"]:
            _rcnums |= {entities.n0(len(_h[k])) for k in ("added", "removed", "substantive")}
            _rcnums |= {_h["from"], _h["to"]}
        for _f in _ent["facilities"]:
            if _f.get("effective"):
                _rcnums.add(str(_f["effective"]))
        w("registry-changes/index.html", registry_changes_page(_rc, today), _rcnums)
    # THE SECOND STATE REGISTER. Every numeral on it is computed by tdlr_projects from the
    # filings, so the authorised set is built the same way rather than listed by hand.
    _tp = tdlr_projects.load()
    if _tp.get("projects"):
        _sa = tdlr_projects.scoped(_tp["projects"], ("Bexar", "Medina"))
        _tt = tdlr_projects.totals(_sa)
        _tnums = {entities.n0(_tt[k]) for k in ("filings", "new_build", "sqft", "sqft_known")}
        _tnums |= {f"${_tt['cost'] / 1_000_000_000:.2f} billion",
                   facility_dossier.ordinal(_tt["first"]), _tt["first"]}
        for _g in tdlr_projects.by_designation(_sa):
            _tnums |= {entities.n0(_g["filings"]), entities.n0(_g["sqft"]),
                       entities.n0(len(_g["buildings"])), _g["designation"]}
            _tnums.add(f"${_g['cost'] / 1_000_000_000:.2f} billion" if _g["cost"] >= 1_000_000_000
                       else f"${entities.n0(_g['cost'])}")
        for _c in tdlr_projects.county_conflicts(_tp["projects"]):
            _tnums.add(_c["postcode"])
        _tnums |= set(tdlr_projects.covered(_sa))
        for _f in _ent["facilities"]:
            _tnums.add(_f["name"])
        w("construction/index.html", construction_page(_tp, _ent, today), _tnums)

    _elist, _glist = entities.published(_ent)
    for _x in _elist:
        w(f"company/{_x['slug']}/index.html",
          company_page(_x, _ent, _dmap, False, today), _enums)
    for _g in _glist:
        w(f"company/{_g['slug']}/index.html",
          company_page(_g, _ent, _dmap, True, today), _enums)
    # THE INDEX SHOWS EVERY RUN, so its authorised set is the union of every run's own
    # figures and not a byte wider. `_run_numerals` derives each from that run's claims and
    # its `computed.json`, never from what a slide happened to print, so this stays the
    # non-circular allowlist the per-article pages already use.
    w("articles/index.html", articles_page(runs, today),
      extra=set().union(*(_run_numerals(r) for r in runs)) if runs else set())
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
        # THE DECK'S OWN NUMERALS, AUTHORISED WHERE THEY WERE COMPUTED AND QUOTED.
        #
        # This page now publishes the deck's prose and every claim behind it, so it carries
        # figures this site build did not compute. That is exactly the case the law already
        # covers at the docket layer: a numeral reaches published copy either by being computed
        # from data or by being QUOTED FROM A SOURCE. Both sets come from the run's own
        # artifacts, so nothing here is authorised by being typed.
        #
        # PER PAGE, NEVER SITE-WIDE, for the reason `_authorised_numerals` records twice over:
        # both times this gate was silently disabled, the cause was an allowlist that grew
        # wider than the page it guarded. Only this article page gets this article's figures.
        w(f'articles/{r["date"]}/index.html', article_page(r, today, items),
          extra=_run_numerals(r))
    # PER PLACE. The index, then a page for every metro the record touches and every
    # touched county that is in no metro. Nothing falls between the two.
    #
    # THIS COMMENT PROMISED AN INDEX FOR MONTHS AND THERE WAS NONE. It is written now, and it
    # is written first, because 73 pages reachable only sideways from whichever item names
    # them is the largest family on this site being crawled as strangers.
    _plfig, _plhtml = places_index(items, today)
    w("place/index.html", _plhtml, extra=_plfig)
    for pl in all_places(items, today):
        w(f'place/{pl["id"]}/index.html', place_page(pl, items, today),
          listed([i for i in items if i["id"] in set(pl["items"])]))
    w("grid/index.html", grid_page(today), _watch_numerals(gridwatch_page))
    # The grid watch as open data, in the same shape the page was built from. A reader who
    # doubts a figure here can recompute it without refetching anything from ERCOT.
    w("gridwatch.json", json.dumps(
        {"_spec": {"version": dk.SPEC_VERSION, "generated": today,
                   "note": "One settled ERCOT day per record. Hourly series included so every "
                           "published figure is recomputable. Unverified days carry no "
                           "numbers rather than yesterday's."},
         "readings": gridwatch_page.load()}, indent=2, ensure_ascii=False) + "\n")
    # The catalogue size is the one figure this page states, and it is the length of the
    # list the page is shipping. It passed the gate before the metro questions existed
    # only because the count was 121 and the state has 121 counties in no metro, which is
    # the coincidence `numeral_lint`'s docstring admits it cannot see through.

    w("scan/index.html", scan_page(today))
    w("scan/watch/index.html", watch_page(today))
    w("services/index.html", services_page(items, today))
    w("water/index.html", water_page(today), _watch_numerals(waterwatch_page))
    w("waterwatch.json", json.dumps(
        {"_spec": {"version": dk.SPEC_VERSION, "generated": today,
                   "note": "One day per record, per reservoir, so every roll up is "
                           "recomputable. Out of state reservoirs and flood control dams with "
                           "no conservation pool are excluded, and both exclusions are named "
                           "in each record."},
         "readings": waterwatch_page.load()}, indent=2, ensure_ascii=False) + "\n")

    # THE ANSWERING RECORD, published as two files beside the site.
    #
    # ask-pack.json is the whole record as prose, which is what the written answer lane puts in
    # front of the model. ask-corpus.json is the answer key the worker marks the reply against,
    # and its numeral allow-list is READ OFF THE PACK rather than off the ledger, so the promise
    # is exact: the model may state a number only if that number was in what it was shown.
    #
    # IT RUNS HERE, AFTER THE FEEDS, AND READS THEM OUT OF THIS BUILD'S OWN OUTPUT. Reading
    # them from the repository's docs/ instead made the pack depend on whatever the LAST build
    # left on disk, so a rebuild into a temp directory picked up stale instrument readings and
    # produced a different pack. site_fresh_check caught exactly that, which is what it is for.
    # A build has to be a pure function of the ledgers or the freshness promise is hollow.
    #
    # Published rather than bundled into the worker because both change daily with the record
    # and the worker does not. A worker carrying its own copy would answer from yesterday's
    # docket the morning after a run, and nothing would say so.
    corpus, pack = ask_corpus.write(out / "ask-corpus.json", out / "ask-pack.json",
                                    today, docs_dir=out)
    written.extend(["ask-corpus.json", "ask-pack.json"])
    # The heat clock as open data, on the same terms as the other two series. It has no page
    # of its own, because it is one line at the top of the front page rather than a subject,
    # so the data page is where a reader finds it.
    w("weather.json", json.dumps(
        {"_spec": {"version": dk.SPEC_VERSION, "generated": today,
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

    # EVERY PAGE'S OWN REVISION DATE, computed once and spent twice.
    #
    # This stamped `today` on all 222 urls, which told Google the whole site changed this
    # morning every morning. Google's position on a `lastmod` it finds unreliable is to stop
    # reading it, so the one field that says "this page is worth fetching again" was being
    # spent on 222 pages that were not worth fetching again. The colophon printed the same
    # untruth in words under every page.
    #
    # `lastmod.py` derives the date from the only record that actually holds it, which is the
    # history of the generated bytes themselves. The substitution happens here, after every
    # page exists, because a page cannot be compared against its committed self while it is
    # still being written.
    revised = lastmod.dates_for(pages, items=items, runs=runs)
    for path, (text, extra) in pages.items():
        iso = revised.get(path)
        stamped = lastmod.apply(text, iso, ordinal)
        own = set()
        if iso:
            d = _dt.date.fromisoformat(iso)
            # The date is a ledger field, so its numerals are authorised. Per page rather than
            # site wide, because a page is entitled to its own date and not another's.
            own = {str(d.day), f"{d.day:02d}", str(d.year), iso, *iso.split("-")}
        stray = numeral_lint.scan(stamped, authorised | extra | own)
        if stray:
            unauthorised.append(f"{path}: {', '.join(stray[:8])}")
        # THE POLICY IS CHECKED HERE, AGAINST `stamped`, and the position is the point. The
        # policy was computed inside `page()` and `lastmod.apply` has rewritten the document
        # since, so auditing any earlier string would check bytes nobody serves. If that
        # substitution ever reaches inside a script or a style block, the hash it invalidates
        # is caught on this line rather than by a reader whose page quietly stopped working.
        if path.endswith(".html"):
            broken.extend(f"{path}: {v}" for v in csp.audit(stamped, SITE_URL))
            connect_seen |= csp.connect_targets(stamped)
        (out / path).write_text(stamped, encoding="utf-8")

    # A url with no honest date carries no `lastmod`. The element is optional and an absent one
    # reads as "no claim", which is true, where a wrong one costs the whole field its
    # credibility across every url on the site.
    urls = [u for u in written if u.endswith("index.html")]
    locs = "".join(
        f"<url><loc>{SITE_URL}/{u[:-10]}</loc>"
        + (f"<lastmod>{revised[u]}</lastmod>" if u in revised else "")
        + "</url>"
        for u in urls)
    w("sitemap.xml",
      f'<?xml version="1.0" encoding="UTF-8"?>'
      f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{locs}</urlset>')

    # AND THE OTHER DIRECTION, which needs every page and so cannot live in a per-page audit.
    # A declared origin nothing targets widens the policy for free. The entry for the scan
    # intake outlived the intake by a day and no gate said so, because an over-wide policy
    # refuses nothing and therefore reports nothing.
    broken.extend(csp.unused_connect(connect_seen))
    # THE FILMS' OWN ORIGIN, checked against the policy this build just wrote. Neither video
    # surface writes the address into markup, so `csp.audit`'s attribute patterns see nothing on
    # a site whose every film is being refused. The manifest is where the origin actually lives,
    # and TexasAIDispatch can change it without a byte of this repo changing.
    broken.extend(csp.unaudited_media(video_feed(), SITE_URL))

    # THE GATE FIRES HERE, after every page is written, so the report names all of them
    # rather than the first. A build that would publish a typed numeral does not publish.
    # A CSP FAILURE IS SILENT AND TOTAL, so it stops the build the same way a typed numeral does.
    # A policy that misses one inline script does not warn anybody: the browser refuses that
    # script, the page half works, and every other gate here stays green.
    if broken:
        for line in broken:
            print(f"  csp: {line}", file=sys.stderr)
        raise SystemExit(
            f"site_build: {len(broken)} content security policy finding(s). A page loads or "
            f"posts to an origin its own policy refuses, carries an inline block nobody "
            f"hashed, or the policy declares an origin no page targets. The allowlist is "
            f"scripts/site/csp.py and it is checked BOTH WAYS: add the origin there if a page "
            f"should be reaching it, remove it if nothing does, and otherwise the page should "
            f"not be reaching it.")

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

    # THE TOPIC VOCABULARY LIVES IN TWO FILES AND THEY HAVE TO AGREE.
    #
    # `docket_build.TOPICS` decides what the record may admit. `TOPIC_BLURBS` decides what
    # /topic/ and the front page can say about it. Adding a beat to the first and not the second
    # is a build that dies at Phase 16 with the deck already made, which is the most expensive
    # minute of the run to discover it in. Adding it to the second only is a blurb nothing
    # renders, which nobody notices at all.
    #
    # So it is checked HERE, where it costs a second and CI runs it on the pull request that
    # adds the beat. The error names the missing side, because the whole point is that whoever
    # trips it should not have to read this file to know what to do.
    missing = sorted(dk.TOPICS - set(TOPIC_BLURBS))
    check(f"every admitted beat has a blurb (missing {missing or 'none'})", not missing,
          "add one line per slug to TOPIC_BLURBS in scripts/site/site_build.py")
    orphan = sorted(set(TOPIC_BLURBS) - dk.TOPICS)
    check(f"...and no blurb describes a beat the record cannot admit ({orphan or 'none'})",
          not orphan, "remove it, or add the slug to TOPICS in scripts/site/docket_build.py")
    # A BLURB THAT SAYS NOTHING PASSES THE CHECK ABOVE AND FAILS THE READER. It is published as
    # the page's meta description, which is the sentence a search result shows.
    thin = sorted(t for t, b in TOPIC_BLURBS.items() if len(b.split()) < 8)
    check(f"...and every blurb is a sentence rather than a placeholder ({thin or 'none'})",
          not thin, "a meta description under eight words tells a search result nothing")

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
        # THE SENTENCE THIS USED TO CHECK IS GONE, on the owner's call that every word has to
        # earn its space. It read "Green means a door is open to you", and the check asserted the
        # page taught the signal. The counted, hot-marked figure above is what carries the answer
        # now, and a check with no subject left is worse than no check at all.
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
              "## The whole record, by beat" in (Path(td) / "a" / "llms.txt").read_text(encoding="utf-8"))

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

        # A CARD THAT SAYS ONLY WHAT IT IS CALLED IS NOT A PREVIEW, and this has now gone
        # blank twice for two different reasons, which is what makes it worth a check rather
        # than a careful edit. First the card printed `copy.json`'s top level `hook`, a field
        # that does not exist, so the paragraph rendered empty. The repair pointed it at the
        # title of the DECISION the deck is about, which is real prose and correctly gated and
        # is empty on any run carrying no `story`. Two of the three shipped runs carry none, so
        # the front page and the articles index both went back to a headline, two buttons and a
        # gap in between.
        #
        # Neither failure could redden anything. An empty paragraph is valid HTML, the numeral
        # gate has no numeral to trace, and house style has no words to judge, so every gate on
        # this site agreed the page was fine while the page said nothing. That is the shape
        # GATE_LESSONS keeps recording: the checks all observed the copy and not the ABSENCE of
        # it. So this counts the cards and reads what is under each title, on the BUILT page.
        arts = (Path(td) / "a" / "articles" / "index.html").read_text(encoding="utf-8")
        cards = re.findall(r"<h3>(.*?)</h3>\s*(?:<p class=\"tease\">(.*?)</p>)?", arts, re.S)
        bare = [" ".join(re.sub(r"<[^>]+>", "", t).split()) for t, tease in cards
                if len(re.sub(r"<[^>]+>", "", tease or "").split()) < 8]
        check(f"every article card carries a preview and not just a title ({len(cards)} card(s))",
              cards and not bare, f"thin: {bare[:3]}; widen deck_preview's sentence budget")
        # The same card on the front page, which is where a reader meets it first and where the
        # blank one was found. It is built by a different function off the same helper, so one
        # of the two staying right proves nothing about the other.
        home_card = idx[idx.find("Our latest article"):]
        home_card = home_card[:home_card.find("</section>")]
        blurbs = [" ".join(re.sub(r"<[^>]+>", "", m).split())
                  for m in re.findall(r"<p[^>]*>(.*?)</p>", home_card, re.S)]
        check("...and so does the one on the front page",
              any(len(b.split()) >= 8 for b in blurbs), f"got: {blurbs}")

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
            """Plant a figure in a page builder's html, whatever shape it hands back.

            `docket_index` returns (html, the numerals it computed) so the calendar's counts
            can be authorised where they are computed. A helper that assumed a bare string
            broke this gate the moment that changed, which would have been a self-test failing
            for a reason that has nothing to do with the law it guards.
            """
            def go(*a, **k):
                out = fn(*a, **k)
                if isinstance(out, tuple):
                    html, *rest = out
                    return (html.replace(find, find + ins, 1), *rest)
                return out.replace(find, find + ins, 1)
            return go

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

    # ---------------------------------------------------------------- next_door
    # WHAT COUNTS AS A DOOR A READER CAN STILL WALK THROUGH. `llms.txt` published 28 finished
    # votes of 47 entries under a heading promising a dated way in, because it filtered on the
    # KIND of access recorded rather than on whether the door is open.
    def door(**over):
        it = {"public_access": {"room": "open_meeting", "closes": None},
              "key_dates": [{"date": "2026-09-04", "kind": "hearing", "note": ""}],
              "status": "pending"}
        it.update(over)
        return it

    check("a future hearing is a door", next_door(door(), "2026-08-16") == "2026-09-04")
    check("a past hearing is not",
          next_door(door(key_dates=[{"date": "2026-07-01", "kind": "hearing"}]),
                    "2026-08-16") is None)
    check("the door is today's, when it is today",
          next_door(door(key_dates=[{"date": "2026-08-16", "kind": "hearing"}]),
                    "2026-08-16") == "2026-08-16")
    check("the NEAREST future door is the one reported",
          next_door(door(key_dates=[{"date": "2026-11-03", "kind": "hearing"},
                                    {"date": "2026-09-04", "kind": "hearing"}]),
                    "2026-08-16") == "2026-09-04")

    # A DECIDED ITEM WITH A FUTURE DOOR KEEPS IT, which is why this is not a status filter.
    # League City has decided, and what it decided was to order a November 3rd election.
    check("a decided item with a future door still has one",
          next_door(door(status="decided"), "2026-08-16") == "2026-09-04")

    # A clock on an agency is not a room a Texan can stand in.
    check("a statutory deadline is not a public door",
          next_door(door(key_dates=[{"date": "2026-09-04", "kind": "statutory_deadline"}]),
                    "2026-08-16") is None)
    check("...nor is the date a rule takes effect",
          next_door(door(key_dates=[{"date": "2027-02-16", "kind": "effective"}]),
                    "2026-08-16") is None)

    # A CANCELED SITTING IS NOT A DOOR, AND IT IS A FIELD RATHER THAN A SENTENCE. This read the
    # note with a regex first, which worked and would have gone quiet the day somebody wrote
    # "called off". gate_schema keeps the note from disagreeing with the flag.
    check("a canceled hearing is not a door",
          next_door(door(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                     "canceled": True, "note": "since canceled"}]),
                    "2026-08-16") is None)
    check("...and the prose alone no longer decides it",
          next_door(door(key_dates=[{"date": "2026-09-04", "kind": "hearing",
                                     "note": "since canceled"}]),
                    "2026-08-16") == "2026-09-04",
          "the flag is the truth; gate_schema is what refuses this item at build time")

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
