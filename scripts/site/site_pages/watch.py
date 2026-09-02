"""Search, watch, water, grid, scan, and services page renderers."""
from __future__ import annotations

from site_context import (
    FORM_ACTION, SCHEMA_CTX, SITE_NAME, SITE_URL, _place_slug, all_places, ask_answers,
    ask_pack, ask_written, csp, dk, e, gridwatch_page, json, page, rel,
    schema, watch_stage, waterwatch_page,
)

def county_links(items: list, today: str, depth: int) -> dict:
    """county name -> href for its page, at the depth the map is being drawn from."""
    up = rel(depth)
    return {c: f"{up}place/county-{_place_slug(c)}/"
            for it in items for c in (it.get("geography") or {}).get("counties") or []}


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
    That line went the same way twice more. It explained which half of the box sends and which
    does not, which is a sentence about plumbing sitting where somebody is deciding what to
    ask. What is left is the thing a reader can act on, that the answers come from a model
    still being worked on and here is how to say when one is wrong.

    The index and the catalogue still ship inline, so the box answers with no request. That is
    still true and it is no longer advertised.
    """
    idx = ask_answers.index(items, today)
    cat = ask_answers.catalogue(idx)
    # HOW A CITATION TO SOMETHING THAT IS NOT A DECISION RENDERS.
    #
    # The written lane can now cite a data center, a county's construction or a reservoir, and
    # the page turned every citation into a link under the decision's own title at
    # /item/<id>/. For the other three families that produced the literal slug as link text,
    # pointing at a page that does not exist.
    #
    # WHICH COUNTIES HAVE A PAGE COMES FROM THE FUNCTION THAT MAKES THEM, not from counting
    # what is on disk. Listing docs/place/ gave a different answer depending on whether the
    # build was writing into docs/, which it wipes first, or into a temp directory, which
    # leaves the committed site standing. Same commit, two different sites, and site_fresh
    # _check went red on main.
    # THE DECISIONS ARE IN THIS MAP NOW AND THEIR TITLES ARE NOT. They were left out entirely,
    # because their titles already ship in the index above at 106 characters each and sending
    # them twice would put 20,000 bytes on every page. Their LABELS are 13 to 30 characters and
    # cannot be derived from anything already on the page, so the label and the link ship and
    # the title is dropped, which the renderer reads back out of the index as it always did.
    cites = {}
    for _k, _v in ask_pack.cite_map(
            today, places={pl["id"] for pl in all_places(items, today)}).items():
        cites[_k] = _v[:2] if _k.startswith("tx-") else _v
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
    <!-- A PHONE NEEDS AN ANCHOR WHEN THE REST OF THE SITE STEPS ASIDE. Hidden from assistive
         technology because the field already carries the useful label and repeating it would
         announce furniture rather than help. -->
    <div class="askmobilehead" aria-hidden="true">
      <span>Texas AI Docket</span><strong>Ask the record</strong>
    </div>
    <div class="askthread" id="askthread" hidden aria-live="polite" aria-atomic="false"></div>
    <form class="composer" role="search">
      <label class="vh" for="askq">Ask the record a question</label>
      <input id="askq" type="search" autocomplete="off"
             placeholder="{e(ask_written.COPY['placeholder'])}">
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
window.__ASK_CATALOGUE__={json.dumps(cat, separators=(",", ":"))};
window.__ASK_CITES__={json.dumps(cites, separators=(",", ":"))};
window.__ASK_SOURCE__={json.dumps(ask_pack.SOURCE, separators=(",", ":"))};</script>
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

    THE ABOUT PAGE FOLDED IN HERE on 2026-08-22, on the owner's call, so the masthead could
    carry a data centers tab without reaching nine. Three sections arrived and the page grew by
    two, because the desk's two jobs and the proof of them are one argument rather than two,
    and the verification rules read better as a paragraph inside it than as a heading of their
    own. What a reader can hold this desk to kept its own section, because it is the part of
    this page that no competitor can copy without meaning it.
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
  <h2>One desk, two jobs</h2>
  <p class="sub">AI is arriving in Texas the way oil and rail once did. As land. As load. As
  water rights. As filings nobody reads until the concrete is poured.</p>
  <p>The docket tracks those decisions one at a time with the source attached. Every fact
  carries a claim id and traces to a fetched document. Every numeral is produced by code, and
  a build gate fails on any figure that traces to no computation. Where something is not
  public the gap is published instead of an estimate.</p>
  <p>The same desk runs a working AI studio. Agentic systems and digital employees. Paperwork
  engines and assistants trained on a company's own files. Writing the beat every morning is
  exactly why the studio knows what actually pays.</p>
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
  <h2>What you can hold this desk to</h2>
  <div class="holds">
    <div class="hold"><h3>Your outcome outranks the invoice</h3>
      <p>This desk recommends what it would do with its own money. Sometimes that is a smaller
      build. Sometimes it is no.</p></div>
    <div class="hold"><h3>Plain talk both directions</h3>
      <p>Bad news arrives early and plain. No soft version. Same expected back. A problem said
      early is still small.</p></div>
    <div class="hold"><h3>The build gets guarded even from the brief</h3>
      <p>Most AI projects die of enthusiasm. When the exciting ask and the right build
      disagree, you hear it. That judgement is what you pay for.</p></div>
    <div class="hold"><h3>Nobody chases this desk</h3>
      <p>A reply lands inside one business day.</p></div>
  </div>
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
    """The stable entity page for the publication and the method behind it.

    This route existed before the studio and publication story folded into Services. Search
    engines kept the old address in their results, where it became a branded dead end. The
    route returns as a focused description of the record and stays out of the crowded top bar.
    It is linked from every footer, which makes it both a reader route and a site-wide entity
    signal without undoing the measured phone navigation.
    """
    body = """
<article>
<section class="hero rise">
  <h1>Texas AI Docket</h1>
  <p class="herolede">A public, fact-checked record of artificial intelligence decisions
  across Texas and the source behind each one.</p>
  <div class="ctarow">
    <a class="cta solid" href="../record/">Read the docket</a>
    <a class="cta ghost" href="../sources/">Open the sources</a>
  </div>
</section>

<section data-reveal>
  <h2>What belongs here</h2>
  <div class="prose">
    <p>Texas AI Docket follows the decisions that shape how artificial intelligence reaches
    the state. Agency rules and local votes belong. Court filings and public contracts belong.
    Data centers belong too. Electric load and water belong when a public document connects
    them to the record.</p>
    <p>The point is not to predict what might happen. It is to show what was filed and decided.
    It also shows what is open for public action and makes the evidence easy to inspect.</p>
  </div>
</section>

<section data-reveal>
  <h2>How the record earns trust</h2>
  <div class="prose">
    <p>Every entry carries the words of a source that was fetched and checked. At least one
    source has to be primary. Dates and counts come from the record rather than from promotional
    copy. Deadlines do too. When a fact is not public the page names the gap instead of filling
    it with an estimate.</p>
    <p>The docket is rebuilt from its ledgers and tested before publication. That keeps the
    article and source trail tied to the same evidence. The machine-readable version stays tied
    to it too.</p>
  </div>
</section>

<section data-reveal>
  <h2>Where to begin</h2>
  <ul class="plainlist">
    <li><a href="../record/">The docket</a> shows every tracked decision and whether a public
    door is still open.</li>
    <li><a href="../articles/">Articles</a> turn one verified Texas and AI story into a visual
    report.</li>
    <li><a href="../datacenters/">Data centers</a> follows the buildout. <a href="../grid/">The
    grid</a> and <a href="../water/">water</a> show the physical systems behind it.</li>
    <li><a href="../sources/">Sources</a> shows the documents the record rests on, grouped by
    publisher.</li>
  </ul>
</section>
</article>
"""
    return page(
        title=f"About {SITE_NAME}", depth=1, active=None,
        desc="How Texas AI Docket tracks artificial intelligence decisions across Texas and "
             "ties every entry to evidence a reader can inspect.",
        body=body, today=today, canonical="about/", revised=False,
        extra_ld=[schema.breadcrumbs(SCHEMA_CTX, [(SITE_NAME, ""),
                                                   ("About", "about/")])])



__all__ = ['county_links', 'grid_page', 'ask_box', 'water_page', 'BOOKING_URL', 'SCAN_WORKER', 'SCAN_ENDPOINT', 'TURNSTILE_SITE_KEY', '_SCAN_JS', 'field', 'scan_page', 'SCAN_RESULT_URL', 'watch_page', 'services_page', 'about_page']
