#!/usr/bin/env python3
"""Shared rendering primitives and build state for the site page families.

Page-family modules import this module instead of importing the orchestrator. BuildContext owns
all writes and page-scoped gates, so extracting a renderer cannot widen numeral authorization or
skip revision and CSP bookkeeping.
"""
from __future__ import annotations

from dataclasses import dataclass, field
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
import ask_pack                                                    # noqa: E402
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
import beyond_panel                                                # noqa: E402
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
# DATA CENTERS SITS SECOND, immediately right of the docket, because it is the thing most
# readers arrive for and the docket is the thing that gives it authority. About folded into
# Services on the owner's call the same day, which is what keeps this at eight: a ninth tab
# wraps the masthead to two rows and `responsive` measures that.
NAV = [("", "Home"), ("record/", "Docket"), ("datacenters/", "Data centers"),
       ("articles/", "Articles"), ("videos/", "Videos"), ("grid/", "Grid"),
       ("water/", "Water"), ("services/", "Services")]

# The footer's way out. Wider than the masthead nav, because the bottom of a page is where
# somebody who did not find what they came for goes looking, and the machine-readable surfaces
# belong there rather than in the top bar.
#
# THE DATA ENTRY IS GONE, and the record is no longer published as a file. The docket is the
# expensive thing this project makes, and handing it over as one parseable download was giving
# away the whole of it to anyone who wanted to reproduce the site. The record is still read on
# `/record/`, item by item, which is where a reader was always going to read it.
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
                     ("questions/", "Questions"), ("scan/", "Scan")]

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

# The shared contact dialog and the services family post through the same opaque mailbox alias.
FORM_ACTION = "https://formsubmit.co/228f72bce4f9b0e50b49d8d501374771"


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

# The one script the shell carries, and the four things it does. All four are progressive:
# with script off the page keeps its atmosphere, its content and its layout, and loses only the
# arrival animations and the glass on the bar.
SHELL_JS = """<script>
document.documentElement.classList.add('js');
addEventListener('scroll',function(){
  document.querySelector('.masthead').classList.toggle('scrolled',scrollY>8);
},{passive:true});
// A CLIPPED LABEL IS USUALLY THE PHONE NAV'S SCROLL CUE, but an edge can land exactly in the
// gap between two labels. In that narrow band the remaining sections are reachable and still
// look absent. The cue follows actual scroll state, so it never points past the final section
// and never appears merely because the small-screen layout rule is active.
(function(){
  var nav=document.querySelector('nav.main'), cue=document.querySelector('.navcue');
  if(!nav||!cue) return;
  function edge(){
    cue.hidden=!(nav.scrollLeft+nav.clientWidth<nav.scrollWidth-1);
  }
  cue.addEventListener('click',function(){
    nav.scrollBy({left:nav.clientWidth,
      behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});
  });
  nav.addEventListener('scroll',edge,{passive:true});
  addEventListener('resize',edge,{passive:true});
  edge();
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(edge);
})();
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
    body = {"home.css": theme.home_css, "record.css": theme.record_css,
            "facility.css": theme.facility_css}[name]()
    return hashlib.sha256(body.encode("utf-8")).hexdigest()[:10]


@functools.lru_cache(maxsize=1)
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

    A full build calls page once for every page. The hash is shared by all of them, so computing
    the same generated stylesheet again on every call only repeats YAML parsing and colour work.
    Keep the result for this process, which is the lifetime of a normal build and its inputs.
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
    # It is not lost. `/record/` carries the same commitment where it can also say how it is
    # kept, naming the build gate that fails on a figure tracing to nothing, which is the half
    # that makes it worth reading. A claim with its mechanism on one page beats a claim without
    # one on every page. It lived on `/data/` until that page came down with the download.
    colophon = "".join(f"<span>{e(s)}</span>" for s in (
        MADE_AT_LEDE,
        # THE PAGE'S OWN DATE, NOT THE BUILD'S. This printed the build date under every page
        # on the site, so the about page told a reader it was revised this morning when its last
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
    <button class="navcue" type="button" aria-label="More sections" hidden></button>
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
        # THE CLAIMS COME FIRST NOW, because the prose loop below needs them to tell a
        # quotation from this project's own sentence. See `_is_quotation`.
        claims = []
        try:
            cj = json.loads((d / "claims.json").read_text("utf-8"))
            claims = [c for c in (cj.get("claims") or []) if isinstance(c, dict)]
        except Exception:                                            # noqa: BLE001
            pass

        prose = []
        for key in sorted(normalise_slide_keys(planned), key=lambda k: k[0]):
            said = [_CLAIM_STAMP.sub(" ", " ".join(s.split())).strip()
                    for s in _slide_strings(key[1]) if _reads_as_prose(s)]
            said = [{"quote": _is_quotation(s, claims), "text": s} for s in said if s]
            if said:
                prose.append(said)

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


def _is_quotation(said: str, claims: list) -> bool:
    """Is this slide string a SOURCE'S OWN WORDS, checked against the run's own claims file.

    THIS USED TO BE `said.startswith('"')`, AND THE PUNCTUATION MARK WAS THE WHOLE TEST.

    House style governs this project's prose and stops at the quotation mark, which is why the
    article page sets a quotation in `<blockquote>` and why `house_style_check` exempts that
    element. Both halves of that are right. What was wrong was HOW a quotation got recognised:
    a deck whose design attributes a quote with a plate and an attribution line rather than with
    quotation marks handed the article page a verbatim sentence wearing no mark, and the page
    published the Public Utility Commission's own sentence as a paragraph this project wrote.

    On 2026-08-28 that put three violations on the board at once, in copy nobody here composed:
    a bare "September 17" against the ordinal rule, a 32 word sentence and a 39 word sentence
    against the backstop. The gate was correct every time and the sentences were unfixable,
    because rewriting them would have been falsifying a quotation.

    **The three it caught were the tip.** Every verbatim dek in that deck arrived unmarked. The
    others passed only because they happened to be short and carried no bare date, so the same
    defect was shipping in silence on the frames that did not trip a rule. Rebuilding the site
    with this fix changes four already-published article pages, 2026-08-20, 08-22, 08-25 and
    08-26, which is the measure of how long it had been live.

    So the test is no longer a mark on the string. `claims.json` holds the quote each fact was
    checked against, the deck may print a source's words only from there, and a string that
    appears inside a claim's quote IS that source's words no matter how the frame dressed it.
    Derived from the fetched source rather than declared by whoever typed the slide, which is
    the same standard every number on this site is held to. A leading quotation mark still
    counts, because a deck that does mark its quotes is not made a liar by this, and a short
    string is excluded so a label is never mistaken for a quotation.
    """
    if said.startswith('"'):
        return True
    body = said.strip().rstrip(".").casefold()
    if len(body) < 24:                    # too short to identify anything. a label, not a quote.
        return False
    return any(body in " ".join(str(c.get("quote") or "").split()).casefold()
               for c in claims)


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
    series behind it is published as open data at `weather.json`, which is where somebody who
    wants the numbers goes.

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



def all_places(items: list, today: str) -> list:
    """Every place that gets a page: touched metros, then every touched county."""
    proj = dk.project(items, today)
    out = []
    for mid, m in proj["by_metro"].items():
        out.append({**m, "kind": "metro"})

    # A COUNTY PAGE MUST KEEP ITS GAZETTEER ASSIGNMENT. The page list used to rebuild each
    # county from only its docket ids, discarding the `metro` field in tx-places.json. The
    # renderer therefore had no way to distinguish Travis County, which is in the Austin
    # metropolitan area, from Loving County, which genuinely is outside every CBSA. Forty of
    # the fifty-nine published county pages consequently stated the opposite of the same
    # gazetteer this build had read. Carry the resolved CBSA record with the page instead of
    # making the renderer derive or remember a second geography.
    gazetteer = json.loads(
        (REPO_ROOT / "assets" / "geo" / "tx-places.json").read_text("utf-8"))
    counties = {p["name"]: p for p in gazetteer["places"]
                if p.get("kind") == "county"}
    metros = {p["code"]: p for p in gazetteer["places"]
              if p.get("kind") == "cbsa"}
    by_county = {}
    for it in items:
        for c in (it.get("geography") or {}).get("counties") or []:
            by_county.setdefault(c, []).append(it["id"])
    # EVERY TOUCHED COUNTY, not only the ones in no metro. The map is the way into this now
    # and a reader clicking Taylor wants Taylor, not the Abilene area that contains it. A
    # county page that only existed for the unmetroed half would leave two thirds of the lit
    # counties on the map pointing at nothing.
    for c in sorted(by_county):
        county = counties[c]       # docket_build already refuses an unresolved county
        membership = county.get("metro")
        metro = metros[membership["cbsa"]] if membership else None
        out.append({"id": f"county-{_place_slug(c)}", "kind": "county", "name": c,
                    "full_name": f"{c} County", "counties": [c],
                    "touched_counties": [c], "items": by_county.get(c, []),
                    "metro": metro})
    return out



def _host_slug(host: str) -> str:
    """A publisher's own page path, derived from its host and from nothing else.

    NOT A TITLE SLUG. A source title is the document's words and changes when the publisher
    retitles a page, and a URL that moves loses whatever rank it had. The host is the one part
    of a citation that is stable for as long as the publisher exists, so it is what the address
    is built from. `interchange.puc.texas.gov` becomes `interchange-puc-texas-gov`, which is
    ugly and permanent, and permanent is the half that matters for an address.
    """
    return re.sub(r"[^a-z0-9]+", "-", host.lower()).strip("-")



# Files this build must preserve rather than produce. Externally owned, listed rather than
# pattern-matched so adding one is a deliberate act with a name attached.
CARRY_THROUGH = (Path("videos") / "videos.json",)



@dataclass
class BuildContext:
    """Mutable state shared by the single orchestrator and every page family.

    Renderers return bytes or text; this context is the only path that writes them. Keeping the
    numeral allowlist and revision inventory here makes those release gates independent of which
    module owns a page renderer.
    """

    out: Path
    today: str
    items: list
    runs: list
    authorised: set
    by_item: dict[str, set]
    written: list[str] = field(default_factory=list)
    unauthorised: list[str] = field(default_factory=list)
    broken: list[str] = field(default_factory=list)
    connect_seen: set[str] = field(default_factory=set)
    pages: dict[str, tuple[str, set]] = field(default_factory=dict)

    def write(self, path: str, text: str, extra: set | None = None) -> None:
        """Write one output and apply the page-scoped numeral gate."""
        target = self.out / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        self.written.append(path)
        if path.endswith(".html"):
            allowed = extra or set()
            self.pages[path] = (text, allowed)
            stray = numeral_lint.scan(text, self.authorised | allowed)
            if stray:
                self.unauthorised.append(f"{path}: {', '.join(stray[:8])}")

    def listed(self, subset: list) -> set:
        """Return the numeral union for exactly the listed docket items."""
        return (set().union(*(self.by_item[item["id"]] for item in subset))
                if subset else set())


__all__ = [name for name in globals() if not name.startswith("__")]
