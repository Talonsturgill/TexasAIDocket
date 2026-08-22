#!/usr/bin/env python3
"""ask_written.py — the client for the lane that leaves the page.

TWO LANES IN ONE FIELD, AND A READER HAS TO FEEL THE DIFFERENCE BEFORE THEY PRESS.

  TYPING is answered by scripts/site/ask_answers.py, in the browser, from an index that ships
  inside the page. It is instant, free, works on a phone with no signal in a county meeting
  room, and sends nothing anywhere. It is most of what the box does.

  PRESSING ENTER sends the question to a worker, which puts the whole published record in one
  prompt and streams back only the sentences that passed a check against that record. It costs
  money every time.

Those are different enough that hiding the difference would be a small dishonesty on a product
whose whole argument is that the small ones matter. The note above the field says which is
which, in a reader's own terms, BEFORE the press rather than after.

WHY THIS IS NOT IN ask_answers.py. That module's self-test asserts it phones nobody, and that
assertion is worth more than the convenience of one file. Keeping the lane that does phone
somebody in a different module means the free lane's promise stays mechanically checkable.

WHY THE THREAD SITS ABOVE THE FIELD. A conversation reads upward. Answers below the composer
push the field down the page as the exchange grows, so the one control a reader wants is the
one that keeps moving away from them.
"""

import argparse
import re
import sys

# The worker. Its own subdomain rather than a path on this site, because it is a different
# thing with a different deploy and a different failure mode, and pretending otherwise would
# make an outage here look like an outage there.
# IMPORTED, not typed. The policy has to allowlist whatever this is, and when the two were
# separate strings the policy shipped without this one and every submitted question was
# refused by the browser. csp.py owns it now, so they cannot disagree.
from csp import ASK_ORIGIN as ENDPOINT

# Public by design. It identifies the widget to Cloudflare and is meant to be read by anyone
# who views source. The SECRET half lives in the worker and appears nowhere in this repository.
TURNSTILE_SITEKEY = "0x4AAAAAAEQ2csplf8Pifi79"

# FEEDBACK GOES TO EMAIL WITH NO BACKEND. formsubmit.co takes a POST and forwards it, so this
# needs no server, no secret and nothing to keep running. The ACTION IS PASSED IN from
# site_build, which already owns that endpoint for the services form. Two constants holding
# one URL is one of them going stale.
#
# The ajax variant returns JSON rather than redirecting, which keeps a reader on the page.
FEEDBACK_SUBJECT = "Texas AI Docket, feedback on the search"


# EVERY SENTENCE A READER CAN SEE, IN ONE PLACE.
#
# Not a style preference. This copy ships inside a JavaScript string, where the house style
# gates that read built pages cannot reach it, and where a colon in a comment two lines above
# is indistinguishable from a colon in a sentence somebody reads. Collected here, the copy is
# reviewable at a glance and checkable exactly, and self_test runs the house rules over this
# block rather than over the source around it.
COPY = {
    "placeholder":  "Ask about any AI decision in Texas",
    "followup":     "Ask a follow-up",
    "stage_human":  "Passing the human check",
    "stage_read":   "Reading the record",
    # WHAT THIS SAYS AND WHY IT NO LONGER BLAMES THE RECORD.
    #
    # It read "The record does not answer that." and the PAGE prints it, not the model. It
    # fires when a stream ended with nothing rendered, which happens when the reply came back
    # empty, or every sentence was withheld, or the connection ended early. None of those are
    # facts about the record, and a reader told the record does not answer something concludes
    # the docket lacks it. It was seen on a question the record answers completely.
    #
    # This box refuses a great deal in order to be trustworthy. Saying "no" on the record's
    # behalf when the truth is "nothing we produced survived" is the one refusal it has not
    # earned.
    "no_answer":    "Nothing came back for that one. Asking again usually works, and typing "
                    "searches the whole record instantly either way.",
    "failed":       "That did not get through. Try again in a moment.",
    "capped":       "That is this month's last written answer. Typing still searches the "
                    "whole record instantly and for nothing, which is most of what this box does.",
    "provenance":   "Written from the published record. Every figure checked against it.",
    # Said when the ceiling cut a stream that had already begun. It names the limit rather
    # than blaming the network, because the limit is ours and a narrower question is the
    # thing a reader can actually do about it.
    "cut_time":     "The rest was cut at eight seconds. A narrower question gets a whole "
                    "answer inside it.",
    "too_slow":     "That one did not come back inside eight seconds. Typing a narrower "
                    "question searches the whole record instantly and for nothing.",
    # Said under an answer the page produced itself, which is most of them. It is not the
    # same claim as the written lane's: nothing was written, the record was read.
    # The refusal wears the same provenance line an answer does. A separate one announced that
    # a different machine had handled it, which is true and is not the reader's problem.
    "checked":      "Checked against the published record.",
    "off_record":   "That is not something this record covers. It holds Texas decisions about "
                    "artificial intelligence, who made them and whether a comment window is "
                    "still open.",
    "again":        "Start over",
    "send":         "Ask",
    "accept":       "Use the suggested question",
    "feedback":     "Send feedback",
    "too_long":     "That answer ran longer than the space for it, so the last part is not "
                    "shown. A narrower question gets the whole of it.",
    "fb_sending":   "Sending",
    "fb_thanks":    "Thanks. That goes straight to a person.",
    "fb_failed":    "That did not send. Try the book a call link instead.",
    "cut_some":     "The rest was withheld because ",
    "cut_none":     "None of that answer is shown, because ",
    # One per reason the worker can send. A reason with no words here falls through to the
    # last line, which is true and tells a reader nothing about what actually happened.
    "why_numeral":  "it stated a figure the record does not carry",
    "why_citation": "it named a decision that is not on the record",
    "why_voice":    "it slipped into the first person, which this record never writes in",
    "why_verdict":  "it made a call on whether the grid holds, which this record never makes",
    "why_other":    "it could not be checked against the record",
}


def note_html() -> str:
    """The line under the field.

    IT SAID MORE AND CARRIED LESS, twice. First it was two sentences explaining which half of
    the box sends and which does not, above a control most people press without reading
    anything. Then it was one clause doing the same job in fewer words, which was still a
    sentence about plumbing sitting where a reader is deciding what to ask.

    Owner's call both times. What is left is the thing a reader can act on: the answers come
    from a model that is still being worked on, and here is how to say when one is wrong.
    """
    return (
        '<p class="asknote">Model in training. '
        '<button type="button" class="asklink" id="askfbopen">Send feedback</button></p>'
    )


def dialog_html(action: str) -> str:
    """The feedback form, as a real dialog element.

    A NATIVE <dialog> RATHER THAN A DIV. It gets focus trapping, escape to close, an inert
    background and the browser's top layer for free, and every one of those is otherwise a
    few hundred lines of the kind of code that is wrong on one phone and nobody's phone is
    the one it was tested on.

    WHAT IT SENDS IS ON SCREEN BEFORE IT SENDS. The last exchange is the single most useful
    thing a reader can attach to "that answer was wrong", and attaching it quietly would be
    collecting somebody's conversation without saying so. It is shown, it is a checkbox, and
    the row does not appear at all until there is an exchange to attach.

    NO BACKEND. formsubmit.co takes the POST and forwards it as mail, so there is no server
    to keep running, no secret to rotate and nothing to go stale.
    """
    return (
        '<dialog class="askfb" id="askfb" aria-labelledby="askfbh">\n'
        f'  <form id="askfbform" method="POST" action="{action}">\n'
        '    <h2 id="askfbh">Model in training</h2>\n'
        '    <p class="askfbnote">The search writes from the published record and is checked '
        'against it line by line. If an answer missed something or read oddly, that is worth '
        'knowing.</p>\n'
        '    <label class="askfbl" for="askfbtext">What happened</label>\n'
        '    <textarea id="askfbtext" name="feedback" rows="4" required\n'
        '              placeholder="The answer missed a filing, or read oddly, or stopped '
        'short"></textarea>\n'
        '    <label class="askfbl" for="askfbmail">Email, only if a reply is wanted</label>\n'
        '    <input id="askfbmail" name="email" type="email" autocomplete="email" '
        'placeholder="Optional">\n'
        '    <label class="askfbcheck" id="askfbattachrow" hidden>\n'
        '      <input type="checkbox" id="askfbattach" checked>\n'
        '      <span>Attach the last question and answer</span>\n'
        '    </label>\n'
        '    <pre class="askfbctx" id="askfbctxview" hidden></pre>\n'
        f'    <input type="hidden" name="_subject" value="{FEEDBACK_SUBJECT}">\n'
        '    <input type="hidden" name="_captcha" value="false">\n'
        '    <input type="hidden" name="_template" value="table">\n'
        '    <input type="hidden" name="exchange" id="askfbctx">\n'
        '    <p class="askfbmsg" id="askfbmsg" role="status" aria-live="polite"></p>\n'
        '    <div class="askfbrow">\n'
        '      <button type="submit" class="askfbsend" id="askfbsend">Send</button>\n'
        '      <button type="button" class="asklink" id="askfbclose">Close</button>\n'
        '    </div>\n'
        '  </form>\n'
        '</dialog>'
    )


def client_js() -> str:
    """The client, with every reader-facing sentence substituted in from COPY.

    The JS holds %%key%% markers rather than the sentences themselves, so there is exactly one
    place to read, review or change what a person is shown. A marker with no entry raises here
    rather than shipping "%%chip%%" onto the front page as a button label.
    """
    js = _CLIENT
    for key in sorted(set(re.findall(r"%%([a-z_]+)%%", js)), key=len, reverse=True):
        if key not in COPY:
            raise KeyError(f"client_js references %%{key}%% with no entry in COPY")
        js = js.replace(f"%%{key}%%", COPY[key].replace('"', '\\"'))
    return js


_CLIENT = r"""
(function () {
  "use strict";
  var box = document.getElementById("ask");
  if (!box) return;
  var EP = box.getAttribute("data-endpoint") || "";
  if (!EP) return;                       /* no endpoint, no written lane, no broken button */
  var SITEKEY = box.getAttribute("data-sitekey") || "";
  var BASE = box.getAttribute("data-base") || "";

  var form   = box.querySelector("form");
  var input  = box.querySelector("input");
  var send   = box.querySelector('button[type="submit"]');
  var thread = document.getElementById("askthread");
  if (!form || !input || !send || !thread) return;

  var busy = false;
  /* THE CEILING'S TIMER LIVES HERE AND NOT IN THE HANDLER, so every path that ends an answer
     can cancel it. It used to be declared inside the send handler, where `finish` could reach
     it and `finishLocal` could not, and `finishLocal` is what the instant refusal calls.
     So a refused question left a live eight second timer behind. It was harmless on its own,
     because the callback checks `busy` and a finished exchange is not busy. It was not
     harmless when a reader asked something else within those eight seconds: the OLD timer
     fired into the NEW answer, found `busy` true because the new question was running, and
     stamped "the rest was cut at eight seconds" onto a reply that had not been cut at all.
     Which is exactly what a reader who pushes back does. They ask, get refused, and type
     "u sure?" straight away. */
  var ceiling = null;
  /* The suggested follow-up, waiting in the placeholder. Held here rather than read back off
     the placeholder, because the placeholder is display and this is data. */
  var pending = null;

  function acceptPending() {
    if (!pending) return false;
    input.value = pending;
    pending = null;
    input.placeholder = "%%followup%%";
    send.setAttribute("aria-label", "%%send%%");
    input.focus();
    try { input.setSelectionRange(input.value.length, input.value.length); } catch (e) {}
    return true;
  }

  function dropPending() {
    if (!pending) return;
    pending = null;
    input.placeholder = "%%followup%%";
    send.setAttribute("aria-label", "%%send%%");
  }
  /* The conversation, held in the page only. Nothing is stored anywhere, it goes when the tab
     does, and it is what makes "when does that close" mean something on its own. The worker
     keeps no session either: the thread travels with each question. */
  var turns = [];

  /* ---- the human check ---------------------------------------------------
     ARMED ON FOCUS, AND THIS HAS BEEN BOTH WAYS. The history is the point.
     It was on focus once and was reverted, correctly at the time: the note under the field
     then said typing sends nothing anywhere, arming on focus fetched Cloudflare's script the
     moment a caret landed in the field, and tests/ask_engine.mjs caught the contradiction.
     THAT SENTENCE LEFT THE NOTE IN #59 and is not coming back. The note reads "Model in
     training" and claims nothing about typing, so the revert was buying a promise that had
     stopped being made while still paying 1 to 3 seconds for it on the first question of every
     session. Owner's call on 2026-08-20 to arm on focus.
     WHAT STILL HOLDS IS THE PART THAT WAS NEVER ABOUT COPY. The challenge host is named in
     ask_engine.mjs, it is armed once per session rather than per keystroke, and any other host
     appearing on this page still fails that suite. A request per keystroke would spend a cap
     counted in calls a month inside an afternoon, and an unannounced host would carry what a
     reader is typing to somebody nobody chose. Neither of those was ever a sentence under a
     field. */
  var tsId = null, tsToken = "";
  function armTurnstile() {
    if (box.dataset.ts || !SITEKEY) return;
    box.dataset.ts = "1";
    window.askTurnstileReady = function () {
      try {
        tsId = turnstile.render(document.getElementById("askts"), {
          sitekey: SITEKEY,
          theme: "dark",
          size: "flexible",
          /* Invisible unless a person is genuinely needed, and on automatic execution, so a
             token is being earned while the reader is still typing rather than after. */
          appearance: "interaction-only",
          callback: function (t) { tsToken = t || ""; },
          "error-callback": function () { tsToken = ""; },
          "expired-callback": function () { tsToken = ""; }
        });
      } catch (e) { tsId = null; }
    };
    var s = document.createElement("script");
    s.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?onload=askTurnstileReady";
    s.async = true; s.defer = true;
    document.head.appendChild(s);
  }

  /* A token is SINGLE USE. Spending it and resetting the widget makes the next one ready while
     the reader reads the answer they just got. Without the reset the first question worked and
     every one after it was refused with "finish the human check first", which is a confusing
     thing to tell somebody who did nothing wrong. */
  function spendToken() {
    tsToken = "";
    if (SITEKEY && window.turnstile && tsId !== null) {
      try { turnstile.reset(tsId); } catch (e) {}
    }
  }
  /* A WAIT NOBODY WOULD NOTICE IS NOT WORTH ANNOUNCING.
     This said "Passing the human check" the instant it began waiting, before the first poll a
     tenth of a second later. So a token that arrived almost at once still flashed the message,
     and an owner watching an eval reported seeing it briefly on every single question after
     the re-arm had already been moved earlier to make the wait short.
     Both changes were needed and they fix different things. Moving the re-arm made the wait
     short. This stops a short wait from being narrated. A quarter second of silence costs a
     reader nothing and a message that appears and vanishes costs them the sense that something
     went wrong.
     The grace is cancelled the moment the token lands, so on a slow connection, where this
     line is the honest explanation for why nothing is happening yet, it still appears. */
  var STAGE_GRACE_MS = 250;

  function waitForToken(stage) {
    if (!SITEKEY) return Promise.resolve("");
    if (tsToken) return Promise.resolve(tsToken);
    var announce = setTimeout(function () { stage("%%stage_human%%"); }, STAGE_GRACE_MS);
    /* Keep waiting rather than giving up if the script is slow: a bad connection is not a
       failed check, and this box exists for people on bad connections. */
    return new Promise(function (resolve) {
      var n = 0;
      var t = setInterval(function () {
        if (tsToken) { clearTimeout(announce); clearInterval(t); resolve(tsToken); return; }
        if (++n > 150) { clearTimeout(announce); clearInterval(t); resolve(""); }
      }, 100);
    });
  }

  /* ---- rendering --------------------------------------------------------- */
  var CITE = /\[\[([a-z0-9-]+)\]\]/g;

  /* A citation becomes a link to the decision it names, UNDER ITS OWN TITLE.
     It used to render the bare id, so an otherwise human paragraph broke off mid sentence into
     "tx-2026-0001", which is a database key wearing a link. The page already ships every title
     in the index the free engine reads, so the name costs one lookup and no bytes.
     The id is kept as the fallback and as the link's title attribute, because a reader who
     wants the key should still be able to find it. The worker has already refused any citation
     that is not on the record, so every id reaching here resolves. */
  var TITLES = {};
  (function () {
    var idx = window.__ASK_INDEX__;
    if (!idx || !idx.items) return;
    for (var i = 0; i < idx.items.length; i++) TITLES[idx.items[i].id] = idx.items[i].title;
  })();

  /* THE RECORD IS FOUR FAMILIES NOW AND ONLY ONE OF THEM LIVES AT /item/.
     The written lane can cite a data center, a county's construction total or a reservoir, and
     this used to render every citation as the decision's title at BASE + "item/" + id. For the
     other three that put the raw slug on the page, "facility-nexus-data-centers", linking to a
     page that does not exist.
     The map is built where the names are, in ask_pack, and shipped for the three families the
     index above does not already carry. Anything missing from it is a decision, which is why
     the fallback is the old behaviour rather than an error. */
  var CITES = window.__ASK_CITES__ || {};
  /* [what the link says, where it goes, what it is]. The first is a LABEL and not a title:
     "Docket 59315" where the record gives an identifier, "the water record" where it does
     not. ask_pack.cite_label holds why. The third is the full title, kept for the tooltip, so
     a reader who wants the whole name still has it without it landing in the sentence. */
  function citeLabel(id) { return (CITES[id] && CITES[id][0]) || TITLES[id] || ""; }
  function citeTitle(id) { return (CITES[id] && CITES[id][2]) || TITLES[id] || ""; }
  function citeHref(id) {
    return BASE + ((CITES[id] && CITES[id][1]) || ("item/" + id + "/"));
  }

  /* THE LABEL IS ALREADY THE RIGHT LENGTH, so nothing is cut here any more.
     This function used to trim the title to fit a sentence, and the cap was wrong in both
     directions: 44 characters made nearly every citation a fragment ending in an ellipsis, and
     170 made it repeat the sentence it followed. A title that IS a sentence cannot be inlined
     after a paraphrase of itself at any length, which is why the choice moved upstream to
     ask_pack.cite_label and this reads what that decided. The longest label the record
     produces is 30 characters. The guard stays because a builder is not a promise. */
  function handle(id) {
    var t = citeLabel(id);
    if (!t) return id;
    if (t.length <= 40) return t;
    var cut = t.slice(0, 36), sp = cut.lastIndexOf(" ");
    return (sp > 20 ? cut.slice(0, sp) : cut) + "...";
  }

  function renderCites(target, text) {
    var at = 0, m;
    CITE.lastIndex = 0;
    while ((m = CITE.exec(text)) !== null) {
      if (m.index > at) {
        target.appendChild(document.createTextNode(text.slice(at, m.index)));
      }
      var a = document.createElement("a");
      a.className = "cite";
      a.href = citeHref(m[1]);
      a.textContent = handle(m[1]);
      a.title = citeTitle(m[1]) || m[1];
      target.appendChild(a);
      at = m.index + m[0].length;
    }
    if (at < text.length) target.appendChild(document.createTextNode(text.slice(at)));
  }

  /* WHY AN ANSWER STOPPED, IN WORDS. The worker names the check that failed. Saying "something
     went wrong" instead would be worse than the stop, because a reader can't tell a refused
     claim from a broken box, and on a record product they should never have to guess. */
  function whyCut(reason) {
    return ({
      numeral:  "%%why_numeral%%",
      citation: "%%why_citation%%",
      voice:    "%%why_voice%%",
      verdict:  "%%why_verdict%%"
    })[reason] || "%%why_other%%";
  }

  /* THE CLOSING OFFER, AS ONE PRESS. Every answer ends by offering the obvious next question.
     Until now a reader had to retype that offer as their own, which is the one bit of work the
     box plainly knew how to do for them.
     It FILLS THE FIELD AND STOPS. Sending is the metered half, the note above the field says
     so, and a chip that sent by itself would spend on a mis-tap and make that note false.
     Only the shapes the prompt actually produces are rewritten. A trailing question that is
     not an offer gets no chip, because a button that guesses is worse than no button. */
  function followUp(sentence) {
    var s = String(sentence || "").trim(), m;
    if (s.length < 8 || s.length > 220 || s.charAt(s.length - 1) !== "?") return null;
    if ((m = s.match(/^(?:do you\s+)?want me to\s+(.+)\?$/i))) return "Yes, " + m[1] + ".";
    if ((m = s.match(/^(?:do you\s+)?want\s+(.+)\?$/i)))       return "Show me " + m[1] + ".";
    if ((m = s.match(/^(?:would you like|shall i|should i)\s+(?:me\s+)?(?:to\s+)?(.+)\?$/i))) {
      return "Yes, " + m[1] + ".";
    }
    return null;
  }

  function clearTrailing() {
    ["askfrom", "asknext"].forEach(function (c) {
      var el = thread.querySelector("." + c);
      if (el) el.remove();
    });
  }

  function reset() {
    turns = [];
    pending = null;
    thread.textContent = "";
    thread.hidden = true;
    box.classList.remove("answering");
    input.value = "";
    input.placeholder = "%%placeholder%%";
    input.focus();
    /* Give the engine back its live list for whatever is in the field now. */
    input.dispatchEvent(new Event("input", { bubbles: true }));
  }

  /* ---- keeping the field where the thumb already is ----------------------- */
  /* GAP is the breathing room under the composer. Plus the phone's own home indicator strip,
     which is real estate the browser will happily let a control sit under. */
  var GAP = 20;

  /* A reader who scrolls up to re-read is DRIVING, and a chat that drags them back to the
     bottom mid-sentence is the single most irritating thing this pattern does. Following is
     given up the moment the newest line is well clear of the composer, and taken back the
     moment they return to it. */
  var following = true;

  function bottomGapNow() {
    var last = thread.lastElementChild;
    if (!last) return 0;
    return form.getBoundingClientRect().top - last.getBoundingClientRect().bottom;
  }

  addEventListener("scroll", function () {
    if (parking) return;
    /* Anything under a screenful means they are still reading the live end of it. */
    following = bottomGapNow() < innerHeight * 0.6;
  }, { passive: true });

  var parking = 0;
  // Where the last park asked the page to be. Null when nothing is pending, so a genuine
  // scroll before the first answer is never mistaken for ours.
  function park() {
    if (!following) return;
    var calm = matchMedia && matchMedia("(prefers-reduced-motion:reduce)").matches;
    var r = form.getBoundingClientRect();
    var safe = 0;
    try {
      safe = parseFloat(getComputedStyle(document.documentElement)
        .getPropertyValue("--safe-bottom")) || 0;
    } catch (e) { safe = 0; }
    /* Where the composer's bottom edge should sit: one gap above the bottom of the glass. */
    var delta = r.bottom - (innerHeight - GAP - safe);
    if (Math.abs(delta) < 2) return;
    parking++;
    /* "auto" MEANS "USE THE STYLESHEET", NOT "JUMP", and this sheet sets
       `scroll-behavior: smooth` on `html`. So the reduced motion branch was asking for
       exactly the animation it exists to avoid. "instant" is the value that overrides it. */
    scrollBy({ top: delta, behavior: calm ? "instant" : "smooth" });
    /* The flag is dropped a beat later so the smooth scroll's own events are not read as the
       reader taking over, which would switch following off on the very first press. */
setTimeout(function () { parking = Math.max(0, parking - 1); }, calm ? 0 : 420);
  }

  /* ---- asking ------------------------------------------------------------ */
  /* The close-out for an answer that never left the page. The streamed lane has its own,
     which also handles provenance, the cut reasons and the follow-up offer. This one exists
     because an instant answer has none of those and should not pretend to: it is the record
     read directly, so it says so and stops. */
  var localExchange = "";

  function finishLocal(note) {
    var foot = document.createElement("p");
    foot.className = "askfrom";
    var prov = document.createElement("span");
    prov.textContent = note;
    foot.appendChild(prov);
    var again = document.createElement("button");
    again.type = "button";
    again.className = "askagain";
    again.textContent = "%%again%%";
    again.addEventListener("click", reset);
    foot.appendChild(again);
    /* FEEDBACK BELONGS UNDER AN INSTANT ANSWER TOO, and leaving it out was the first version's
       mistake. The written lane offers it because the moment somebody has just watched an
       answer be wrong is the moment they can say so usefully. An answer read straight from
       the record can be wrong in exactly the same way, by matching the wrong item, and it now
       arrives for most questions, so omitting it here would have quietly removed feedback from
       the majority of answers this box gives. */
    var say = document.createElement("button");
    say.type = "button";
    say.className = "askagain";
    say.textContent = "%%feedback%%";
    say.addEventListener("click", function () {
      var open = document.getElementById("askfbopen");
      if (open) open.click();
    });
    foot.appendChild(say);
    thread.appendChild(foot);
    // `:last-of-type` MATCHES THE LAST DIV, NOT THE LAST OF THE CLASS. Both of these are
    // divs among many divs, so the selector picked whatever div happened to be last and the
    // attachment came out as "Q. " with nothing after it.
    var qs = thread.querySelectorAll(".askturn"), as = thread.querySelectorAll(".askreply");
    var q = qs[qs.length - 1], a = as[as.length - 1];
    localExchange = "Q. " + (q ? q.textContent : "") + "\n\nA. " + (a ? a.textContent : "");
    /* AN INSTANT ANSWER GOES INTO THE THREAD, and leaving it out is what made "u sure?" get
       the same canned sentence twice. The classifier only lets a follow-up through once this
       box has ANSWERED something, and a refusal recorded nothing, so the next question was
       judged as a first question and refused again. The box had spoken and its own transcript
       did not know it.
       IT IS SAFE TO SEND BACK for the reason the rule was written. Only guard approved text
       may re-enter, and this text is the page's own copy or the engine's own render of the
       record. No model wrote it, so there is nothing here a checker refused. And a reader
       pushing back needs the model to see what it is being challenged on. */
    if (a && a.textContent.trim()) {
      turns.push({ role: "assistant", content: a.textContent.trim() });
    } else {
      turns.pop();
    }
    // An instant answer is an answer. It ends the exchange, so it stops the clock.
    clearTimeout(ceiling);
    ceiling = null;
    busy = false;
    send.disabled = false;
    send.removeAttribute("aria-busy");
    input.value = "";
    park();
  }

  function ask(question) {
    if (busy) return;
    busy = true;
    send.disabled = true;
    send.setAttribute("aria-busy", "true");
    box.classList.add("answering");
    /* A new question is always a return to the live end, whatever they were reading before. */
    following = true;
    thread.hidden = false;
    clearTrailing();

    turns.push({ role: "user", content: question });

    /* The question is read back. In a one-shot box that was duplication, because it sat in the
       field an inch below. In a thread it is the only record of what was asked three answers
       ago, and the field has been cleared for the next one. */
    var asked = document.createElement("div");
    asked.className = "askturn";
    asked.textContent = question;
    thread.appendChild(asked);

    var body = document.createElement("div");
    body.className = "askreply";
    // APPENDED BEFORE THE CLASSIFIER RUNS, not after the stream starts. The instant and refuse
    // lanes return early, and the original append sat past that return, so both rendered into
    // an element that was never in the document. The thread showed a question, a provenance
    // line and nothing between them.
    thread.appendChild(body);

    /* ---- the classifier decides whether this costs anything at all ------------
       THE CHEAPEST ANSWER IS THE ONE THAT NEVER LEAVES THE PAGE, and the engine in
       ask_answers.py already knew which questions those were. It scores against a catalogue
       and refuses below a floor, so it can say "I have this" or "I do not", and that judgement
       was being thrown away at the press while every question went to a model taking seconds.
       Asked here, before the request is built. A lookup is answered from the page in no time
       and for nothing. An off-record question is refused without calling anybody. Only a
       question that genuinely needs prose reaches the worker, which is what makes an eight
       second ceiling a promise rather than a hope: most questions never start the clock. */
    /* ---- THE EIGHT SECOND CEILING -------------------------------------------
       Owner's brief: "an eight second execution ceiling, so it's fast when users are asking
       it questions".
       IT CUTS, IT DOES NOT DISCARD. Aborting at the ceiling and showing nothing would trade a
       slow answer for no answer, which is not what a ceiling is for. What arrived stays on
       screen, the stream is stopped, and the reader is told the rest was cut for time and
       offered the thing that actually helps, which is a narrower question.
       WHY EIGHT IS ACHIEVABLE AT ALL. Most questions never start this clock, because the
       classifier answers them from the page. The ceiling only has to hold for questions that
       genuinely need a model, and the token is already in hand by the time one is pressed.
       THE CLOCK STARTS AT THE PRESS AND IS RESTARTED WHEN THE REQUEST GOES OUT, and the second
       half of that was missing. The line above says the token is already in hand by the time a
       question is pressed. That is true of every question except the FIRST one of a session,
       where Turnstile arms on focus and is still solving, and solving takes one to three
       seconds. So the first question of every session spent part of its eight on a human check
       and then got cut.
       IT LOOKED WORSE THAN A CUT. When the ceiling fires during the token wait, `stopStream`
       is still null, because no fetch has started for it to stop. So the reader was shown "it
       did not come back in eight seconds", and then the answer arrived a moment later and
       overwrote the message. An owner watching an eval saw exactly that and called it odd.
       The promise is unchanged and it is about the ANSWER. A human check is not the answerer
       being slow, it is a challenge the reader cannot skip, and it says so on screen while it
       runs. Restarting the clock at the fetch is what makes eight seconds mean the thing it
       claims to mean. */
    var CEILING_MS = 8000;
    var overran = false;
    /* WHICH ENDING GOT HERE FIRST, tracked explicitly rather than inferred from whether the
       body happens to have text in it. Two different endings both wrote "if nothing started
       and the body is empty", which is a read of the DOM standing in for a fact about control
       flow, and when an owner reported seeing one message replaced by the other there was no
       way to tell from the page which path had run. A flag says so. */
    var ended = "";
    function ceilingFired() {
      if (!busy) return;
      overran = true;
      if (stopStream) { try { stopStream(); } catch (e) {} }
      dropStage();
      if (ended) return;
      ended = "ceiling";
      if (!started && !body.textContent) body.textContent = "%%too_slow%%";
      else {
        var cut = document.createElement("p");
        cut.className = "askstop";
        cut.textContent = "%%cut_time%%";
        body.appendChild(cut);
      }
      finish();
    }
    /* ARMED AT THE PRESS AS WELL AS AT THE FETCH, so a question that never reaches the network
       at all still ends rather than hanging. startClock replaces this one the moment the
       request actually goes out. */
    clearTimeout(ceiling);
    ceiling = setTimeout(ceilingFired, CEILING_MS);

    localExchange = "";
    /* THE THREAD'S DEPTH GOES WITH THE QUESTION. A follow-up carries no record vocabulary by
       its nature, so judged alone it looks exactly like somebody asking for a recipe.
       COUNTED IN ANSWERS GIVEN, NOT TURNS TAKEN. `turns` already holds this question by the
       time we get here, so its length is 1 on a first ask and `depth > 0` switched the refusal
       off for everybody. tests/ask_engine.mjs caught it. An assistant turn is the unambiguous
       thing being asked about: has this box already answered something in this thread. Nothing
       else makes a bare "why" a follow-up rather than a fresh question about nothing. */
    var answered = 0;
    for (var ti = 0; ti < turns.length; ti++) {
      if (turns[ti].role === "assistant") answered++;
    }
    var verdict = window.__askClassify
      ? window.__askClassify(question, answered)
      : { bucket: "written" };

    /* THERE IS NO LOCAL ANSWER LANE ANY MORE, and removing it is the point.
       A block here used to render a headline and a list of item links for anything the
       catalogue matched, which was most questions. It was fast and it was not an answer, and
       the owner's verdict was plain: "people are typing in a question cause they want an
       answer that is the agent or looks like its from an agent, it cant be anything less".
       So the only thing that ends here is a question this record has no business answering,
       and it ends as a SENTENCE in the same bubble with the same footer, because a refusal
       that looks like a different kind of object reads as the machine giving up. */
    if (verdict.bucket === "refuse") {
      var no = document.createElement("p");
      no.textContent = "%%off_record%%";
      body.appendChild(no);
      finishLocal("%%checked%%");
      return;
    }


    input.value = "";
    pending = null;
    input.placeholder = "%%followup%%";
    send.setAttribute("aria-label", "%%send%%");

    /* THE FIELD STAYS DOWN AND THE TALK GROWS ABOVE IT, which is how every chat a reader has
       ever used behaves and is the one thing this box got wrong.
       It used to scroll the QUESTION to just under the masthead. On a page where the box sits
       partway down, with an empty thread, that put the composer near the TOP of the screen on
       the first press, so asking a question threw the page somewhere else and moved the one
       control the reader was using.
       Parking the composer near the bottom instead needs no sticky, no fixed element and no
       nested scroller, so it behaves the same on a phone, a tablet and a desktop and it can
       never float over another section. */
    park();

    /* The first press is the intent that arms the human check. Everything before it, focus
       and typing included, leaves the page alone. */
    armTurnstile();

    var stageEl = null, started = false, para = null, said = [];
    var stopStream = null;

    /* THE STAGE LINE MAY NOT DESTROY AN ANSWER, AND IT COULD.
       Creating the element cleared the whole body first, which is safe only while the body is
       empty. It is not empty once a sentence has rendered, and `dropStage` sets stageEl back
       to null the moment one does, so ANY later call recreated the element and wiped the
       answer off the screen. An owner saw exactly that: the answer appeared and vanished.
       The 250ms grace timer added a late caller, which is how a message meant to be quieter
       ended up deleting the thing a reader was reading. The timer is not the fault. A function
       that empties the body as a side effect of adding one line is.
       It clears only what it is entitled to clear, which is nothing once the answer has begun,
       and it refuses to speak at all after that: a stage line under a finished sentence is
       noise even when it is harmless. */
    function stage(text) {
      /* NOTHING MAY WRITE TO THE BODY ONCE AN ENDING HAS WRITTEN TO IT, and this guard was
         half built. It already refused to speak over an answer in progress, which was the fix
         for an owner watching a sentence appear and vanish. It did not refuse to speak over an
         ENDING, and an ending is the case where the body holds one short line and nothing else.
         So: the eight second ceiling fires, writes "that one did not come back", and calls
         dropStage, which sets stageEl to null. A chunk already in flight then reaches this
         function, which sees no answer started and no sentences said, decides it is allowed to
         speak, finds no stage element, and clears the body to make one. The ceiling's message
         is gone. The next dropStage removes the stage line too and the reader is looking at
         nothing at all. Reported as "the eight seconds didn't return anything, then went
         blank".
         stopStream is called before this, and it cannot help: a chunk already dispatched still
         arrives. The ending is the fact to guard on rather than the stream. */
      if (started || said.length || ended) return;
      if (!stageEl) {
        body.textContent = "";
        stageEl = document.createElement("div");
        stageEl.className = "askstage";
        body.appendChild(stageEl);
      }
      stageEl.textContent = text;
      park();
    }
    function dropStage() {
      if (stageEl) { stageEl.remove(); stageEl = null; }
    }
    function sentence(t) {
      said.push(t);
      dropStage();
      if (!started) { started = true; para = document.createElement("p"); body.appendChild(para); }
      var span = document.createElement("span");
      span.className = "askseg";
      renderCites(span, (para.childNodes.length ? " " : "") + t);
      para.appendChild(span);
      park();
    }

    function finish() {
      /* CALLED ONCE, WHATEVER GETS HERE FIRST. The stream finishing and the ceiling firing are
         a race by design, and both end the answer. Without the guard a stream that lands just
         after the cut appends a second footer, pushes a second assistant turn into `turns` and
         re-enables a control that is already enabled. */
      if (!busy) return;
      clearTimeout(ceiling);
      ceiling = null;

      /* What it SAID goes back into the thread, not what it tried to say. A sentence the
         reader never saw must not be one the model can build on either, or a refused claim
         re-enters through the back door on the next question. */
      if (said.length) turns.push({ role: "assistant", content: said.join(" ") });
      else turns.pop();

      busy = false;
      send.disabled = false;
      send.removeAttribute("aria-busy");

      clearTrailing();

      /* THE OFFER GOES INTO THE FIELD, NOT INTO A BUTTON.
         It was a chip under the answer, which worked and was one more thing to look at. A
         reader who has just read an answer is already looking at the field they will type the
         next one into, so the suggestion belongs there, lightly, the way an editor suggests a
         completion. The send control accepts it and a second press sends it, which is the same
         two presses the chip needed and one fewer place to look. */
      pending = said.length ? followUp(said[said.length - 1]) : null;
      if (pending) {
        input.placeholder = pending;
        send.setAttribute("aria-label", "%%accept%%");
      }

      var foot = document.createElement("div");
      foot.className = "askfrom";
      if (started) {
        var prov = document.createElement("span");
        prov.textContent = "%%provenance%%";
        foot.appendChild(prov);
      }
      var again = document.createElement("button");
      again.type = "button";
      again.className = "askagain";
      again.textContent = "%%again%%";
      again.addEventListener("click", reset);
      foot.appendChild(again);

      /* FEEDBACK BELONGS HERE TOO, and this was a real hole. Answering hides the note under
         the field, note and starters and live list together, so the one moment a reader has
         just watched the model be wrong was the one moment they had no way to say so. It sits
         beside Start over, which is where somebody who has finished reading already is. */
      var say = document.createElement("button");
      say.type = "button";
      say.className = "askagain";
      say.textContent = "%%feedback%%";
      say.addEventListener("click", function () {
        var open = document.getElementById("askfbopen");
        if (open) open.click();
      });
      foot.appendChild(say);
      thread.appendChild(foot);

      /* ONE LAST PARK, because this footer is the tallest thing appended after the sentences
         stop. Without it the provenance line, Start over and the feedback control push the
         composer off the bottom of the glass at the exact moment the reader looks down to type
         the next question, which is the fault this whole change exists to remove. */
      park();
    }

    function handle(ev) {
      if (ev.stage) { stage(ev.stage); return; }
      if (ev.sentence) { sentence(ev.sentence); return; }
      if (ev.withheld) {
        dropStage();
        var stop = document.createElement("div");
        stop.className = "askstop";
        var why = whyCut(ev.withheld);
        /* Different copy when NOTHING survived, because then there is no "rest". Saying the
           rest was withheld when the whole answer was reads as a bug, and it was one. */
        stop.textContent = (started ? "%%cut_some%%" : "%%cut_none%%") + why + ".";
        body.appendChild(stop);
        return;
      }
      if (ev.long) {
        /* The model ran out of room. The half sentence it was in the middle of is dropped by
           the worker rather than shipped, because "under the Paperw" reaching a reader is
           worse than saying the answer was too long, and a reader cannot tell a truncation
           from the record simply stopping there. */
        dropStage();
        var cut = document.createElement("div");
        cut.className = "askstop";
        cut.textContent = "%%too_long%%";
        body.appendChild(cut);
        return;
      }
      if (ev.capped) {
        dropStage();
        if (!started) {
          body.textContent = "%%capped%%";
        }
        return;
      }
      if (ev.error) {
        dropStage();
        if (!started) body.textContent = ev.error;
      }
    }

    function post(tok) {
      return fetch(EP + "/answer", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ messages: turns, turnstile_token: tok || null })
      });
    }

    /* THE CLOCK RESTARTS HERE, once the challenge is done and the question is actually on its
       way. Everything before this point is the human check, which the reader can see happening
       and which is not the answerer taking too long. */
    function startClock() {
      clearTimeout(ceiling);
      ceiling = setTimeout(ceilingFired, CEILING_MS);
    }

    waitForToken(stage).then(function (tok) {
      stage("%%stage_read%%");
      startClock();
      var sent = post(tok);
      /* THE NEXT CHALLENGE IS EARNED NOW, NOT AFTER THE ANSWER.
         A Turnstile token is single use, so every question needs a fresh one, and solving takes
         one to three seconds. This used to re-arm in `finish`, once the answer was already on
         screen. An owner running ten questions in a row saw "Passing the human check" in front
         of nearly every one of them, because a reader moving question to question arrives
         before the new token does.
         The token is spent the moment it is handed to the worker, so the challenge can start
         again immediately and solve WHILE the answer streams and while the reader reads it.
         The first question of a session still waits, because nothing has been earned yet, and
         that one is honest. */
      spendToken();
      return sent;
    }).then(function (r) {
      /* A 403 here is a token that was spent, expired or never arrived, and it is not the
         reader's doing. Showing them "finish the human check first" next to a widget that is
         deliberately invisible is a dead end nobody can act on, which is exactly what an eval
         found. Ask for a fresh one and go again, once. */
      if (r.status !== 403) return r;
      stage("%%stage_human%%");
      spendToken();
      clearTimeout(ceiling);
      return waitForToken(stage).then(function (fresh) {
        startClock();
        return fresh ? post(fresh) : r;
      });
    }).then(function (r) {
      if (!r.body || !r.body.getReader) {
        /* No streaming in this browser. Read it whole and play it out, so the behaviour a
           reader sees is the same one. */
        return r.text().then(function (t) {
          t.split("\n").forEach(function (l) {
            if (l.trim()) { try { handle(JSON.parse(l)); } catch (e) {} }
          });
        });
      }
      var reader = r.body.getReader(), dec = new TextDecoder(), buf = "";
      // Handed to the ceiling so it can stop the stream rather than let it go on writing into
      // a thread that has already been closed off and footed.
      stopStream = function () { try { reader.cancel(); } catch (e) {} };
      return (function pump() {
        if (overran) return;
        return reader.read().then(function (res) {
          if (overran || res.done) {
            if (buf.trim()) { try { handle(JSON.parse(buf)); } catch (e) {} }
            return;
          }
          buf += dec.decode(res.value, { stream: true });
          var lines = buf.split("\n");
          buf = lines.pop();
          for (var i = 0; i < lines.length; i++) {
            if (!lines[i].trim()) continue;
            try { handle(JSON.parse(lines[i])); } catch (e) {}
          }
          return pump();
        });
      })();
    }).then(function () {
      dropStage();
      if (!ended) {
        ended = "stream";
        if (!started && !body.textContent) body.textContent = "%%no_answer%%";
      }
      finish();
    }).catch(function () {
      dropStage();
      if (!ended) {
        ended = "failed";
        if (!started) body.textContent = "%%failed%%";
      }
      finish();
    });
  }

  /* ---- feedback ----------------------------------------------------------
     A model that is still being worked on needs a way to hear that it was wrong, and the
     reader who just watched it be wrong is the only person who can say so. This is that,
     and it is the shortest path that reaches a person: a form that posts to a forwarding
     service and no backend anywhere. */
  var fb = document.getElementById("askfb");
  var fbOpen = document.getElementById("askfbopen");
  if (fb && fbOpen) {
    var fbForm  = document.getElementById("askfbform");
    var fbMsg   = document.getElementById("askfbmsg");
    var fbCtx   = document.getElementById("askfbctx");
    var fbView  = document.getElementById("askfbctxview");
    var fbRow   = document.getElementById("askfbattachrow");
    var fbCheck = document.getElementById("askfbattach");
    var fbSend  = document.getElementById("askfbsend");

    /* The last exchange, as text, or nothing. Read from `turns` rather than scraped off the
       page, so what gets attached is exactly what was said and not what the DOM happens to
       hold after a Start over. */
    /* AN INSTANT ANSWER IS AN EXCHANGE TOO, and it is not in `turns`.
       `turns` is the MODEL's conversation and only guard-approved sentences go into it, which
       is a rule worth keeping: a page-generated answer pushed in there would come back as
       context the model treats as its own prior words. So an answer read from the record is
       remembered separately, purely so feedback about it can carry it.
       Without this, feedback on the majority of answers this box now gives would arrive with
       nothing attached, which is the half of a bug report that makes it actionable. */
    function lastExchange() {
      if (localExchange) return localExchange;
      for (var i = turns.length - 1; i > 0; i--) {
        if (turns[i].role === "assistant") {
          return "Q. " + turns[i - 1].content + "\n\nA. " + turns[i].content;
        }
      }
      return "";
    }

    fbOpen.addEventListener("click", function () {
      var ex = lastExchange();
      /* No exchange, no offer to attach one. An unticked checkbox next to an empty box is a
         question a reader has to work out the answer to. */
      fbRow.hidden = !ex;
      fbView.hidden = !ex;
      fbView.textContent = ex;
      if (fbCheck) fbCheck.checked = !!ex;
      fbMsg.textContent = "";
      fbSend.disabled = false;
      if (typeof fb.showModal === "function") fb.showModal();
      else fb.setAttribute("open", "");
      var t = document.getElementById("askfbtext");
      if (t) t.focus();
    });

    document.getElementById("askfbclose").addEventListener("click", function () {
      if (typeof fb.close === "function") fb.close(); else fb.removeAttribute("open");
    });
    if (fbCheck) {
      fbCheck.addEventListener("change", function () { fbView.hidden = !fbCheck.checked; });
    }

    fbForm.addEventListener("submit", function (e) {
      e.preventDefault();
      /* Attached only if the box is ticked, and the field is cleared otherwise rather than
         left holding a value from a previous open. */
      fbCtx.value = (fbCheck && fbCheck.checked) ? lastExchange() : "";
      fbSend.disabled = true;
      fbMsg.textContent = "%%fb_sending%%";
      fetch(fbForm.action, {
        method: "POST",
        headers: { "content-type": "application/json", "accept": "application/json" },
        body: JSON.stringify(Object.fromEntries(new FormData(fbForm).entries()))
      }).then(function (r) {
        if (!r.ok) throw new Error("bad status");
        fbMsg.textContent = "%%fb_thanks%%";
        fbForm.reset();
        fbView.hidden = true;
        setTimeout(function () {
          if (typeof fb.close === "function") fb.close(); else fb.removeAttribute("open");
        }, 1600);
      }).catch(function () {
        /* Say where it stands and give the second route, rather than losing what somebody
           took the trouble to write. */
        fbMsg.textContent = "%%fb_failed%%";
        fbSend.disabled = false;
      });
    });
  }

  /* Writing your own question puts the suggestion away. A placeholder that lingers under
     text somebody is typing is just noise behind their sentence. */
  /* FOCUS ARMS THE CHECK, AND THE POINT IS WHERE THE WAITING HAPPENS.
     Armed by the press before this, on the reasoning that focus is not intent to ask. That
     cost 1 to 3 seconds on the FIRST question of every session and nothing on any after it,
     because spending a token resets the widget and the next is earned while the reader types.
     The first question, the one that forms the impression, was the only one paying.
     Managed mode solves in the background with no interaction, so on focus it solves DURING
     typing, which is the slowest thing in the sequence, and the press has nothing left to wait
     for. Somebody who pastes and submits inside a second still polls, exactly as before.
     Never slower. Owner's call, 2026-08-20, made knowing it had been tried and reverted. */
  input.addEventListener("focus", armTurnstile, { once: true });

  /* ---- THE BOX TAKES THE SCREEN ON A PHONE ---------------------------------
     Owner: "when a user clicks onto the search bar, we really want everything else on the
     screen to just disappear", and after a press on a phone, "there's so much stuff on screen,
     your eyes don't even go to the right spot".
     A CLASS ON `body`, NOT A NEW ELEMENT. Everything that is not the box is taken out of the
     flow by the stylesheet at phone widths, so there is nothing to build, nothing to keep in
     sync with the page it covers, and on a laptop the rule simply does not apply.
     THE SCROLL POSITION IS REMEMBERED AND PUT BACK. Hiding the page collapses it, so the
     browser forgets where the reader was and dumps them at the top when it returns, which
     feels like having lost their place because they have. */
  /* CAPTURED BEFORE THE BROWSER MOVES THEM, which is why this is not simply read at focus.
     A browser scrolls a focused input into view itself, and it does that BEFORE the focus
     handler runs, so reading the offset there records where the browser had just put them and
     not where they were reading. Measured: a reader at 600 was recorded at 74 and handed back
     to 74, which is the bug this was meant to prevent wearing a fix's clothes.
     `pointerdown` fires before focus and before that scroll. The scroll listener is the
     fallback for a reader who arrives by keyboard, where nothing has moved yet anyway. */
  var wasAt = 0, lastY = 0;
  addEventListener("scroll", function () {
    if (!document.body.classList.contains("asking")) lastY = window.pageYOffset;
  }, { passive: true });
  input.addEventListener("pointerdown", function () { wasAt = window.pageYOffset; });
  /* A STARTER IS A QUESTION, so pressing one has to take the screen exactly as tapping the
     field does. It did not, because immersion hung off focus and a button press never focuses
     the input. The owner pressed "What can I still comment on?" on a phone and got the answer
     rendered inline with the hero, the footer and every other section still there, with the
     box grown to 917px inside a 780px screen and scrolled off the top. Captured on the
     starter's own pointerdown, before anything moves. */
  box.querySelectorAll(".chips [data-ask]").forEach(function (btn) {
    btn.addEventListener("pointerdown", function () { wasAt = window.pageYOffset; });
  });
  /* THE SAME BREAKPOINT THE STYLESHEET USES, asked of the browser rather than guessed. Setting
     the class at every width was harmless while the rules were scoped, and it left one real
     trap: a reader focused on a laptop and then narrowing the window, or turning a tablet, would
     be thrown into a full screen mode they never asked for. */
  var PHONE = window.matchMedia ? window.matchMedia("(max-width:37.5rem)") : null;
  function immerse() {
    if (PHONE && !PHONE.matches) return;
    if (document.body.classList.contains("asking")) return;
    // A pointerdown a moment ago is the truest reading. Otherwise the last settled scroll,
    // and only then the current offset, which by now may already have been moved.
    if (!wasAt) wasAt = lastY || window.pageYOffset;
    document.body.classList.add("asking");
  }
  function surface() {
    if (!document.body.classList.contains("asking")) return;
    document.body.classList.remove("asking");
    var target = wasAt;
    wasAt = 0;
    /* RESTORED AFTER THE PAGE HAS ITS HEIGHT BACK. Removing the class un-hides the hero, the
       nav and every section, and until that layout has happened the document is barely taller
       than the viewport, so a scroll to 600 is clamped to whatever fits and the reader lands
       near the top anyway. Measured: it came back at 74 instead of 600. Two frames is one to
       apply the style and one to lay it out. */
    /* IT VERIFIES ITSELF RATHER THAN FIRING ONCE AND HOPING. One frame put the reader at 74
       instead of 600 and two frames at 169, because the page regains its height in stages as
       sections, fonts and images lay back out, and a scroll past the current bottom is clamped
       silently. So it asks for the position again on each of the next few frames and stops as
       soon as it sticks. Bounded, so a page that genuinely cannot reach that offset any more,
       which is a real case if the thread is long, settles at the nearest it can. */
    /* IT VERIFIES ITSELF, AND IT WAITS IN TIME RATHER THAN IN FRAMES. The page regains its
       height in stages as sections, fonts and images lay back out, and a scroll past the
       current bottom is clamped silently, so a single call landed the reader at 74 instead of
       600 and two frames at 169. Eight frames was not enough either once a thread had been
       added, which is about 130ms against a page that takes longer than that to come back.
       Bounded at half a second, after which the nearest reachable offset is the honest answer:
       a long thread really can make the old position unreachable. */
    var until = 500, step = 40, waited = 0;
    (function restore() {
      window.scrollTo({ top: target, behavior: "instant" });
      if (Math.abs(window.pageYOffset - target) > 2 && waited < until) {
        waited += step;
        setTimeout(restore, step);
      }
    })();
  }
  input.addEventListener("focus", immerse);
  var closer = document.getElementById("askclose");
  if (closer) closer.addEventListener("click", function () { surface(); input.blur(); });
  /* ESCAPE LEAVES, which is what a keyboard reader reaches for, and it must not also clear the
     field: a search input treats Escape as clear on its own, so the default is stopped. */
  input.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && document.body.classList.contains("asking")) {
      e.preventDefault();
      surface();
      input.blur();
    }
  });
  /* Start over hands the screen back as well, since the reader has said they are finished. */
  box.addEventListener("click", function (e) {
    if (e.target && e.target.classList && e.target.classList.contains("askagain") &&
        e.target.textContent === "%%again%%") surface();
  });

  input.addEventListener("input", function () { if (input.value) dropPending(); });

  /* Tab and the right arrow accept it, which is the convention everywhere else a field
     suggests a completion, and both only fire when the field is empty so neither steals a
     keystroke from somebody writing. */
  input.addEventListener("keydown", function (e) {
    if (input.value || !pending) return;
    if (e.key === "Tab" || e.key === "ArrowRight") {
      e.preventDefault();
      acceptPending();
    }
  });

  /* SUBMIT IS THE WRITTEN LANE NOW. It used to re-run the engine, which is what typing already
     does, so pressing enter did nothing a reader could see. */
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    /* An empty field with a suggestion waiting means the arrow accepts rather than sends. The
       reader sees the words land in their own field and presses again to ask, so nothing is
       ever sent that they have not seen in full. */
    if (!input.value.trim() && acceptPending()) return;
    var q = input.value.trim();
    if (!q) return;
    /* IMMERSION FOLLOWS ASKING, NOT FOCUSING, and that distinction is the bug the owner hit.
       It hung off the field's focus event, and a starter chip is a button that never focuses
       the field, so pressing "What can I still comment on?" on a phone answered INLINE with
       the hero, the footer and every section still on screen, and the box grew to 917px
       inside a 780px viewport and scrolled off the top.
       Here it covers every way a question can be asked: a starter, the arrow, and Enter. */
    immerse();
    ask(q);
  });
})();
"""


def self_test() -> int:
    ok = [True]

    def check(label, cond, detail=""):
        print(f"  {'PASS' if cond else 'FAIL'}  {label}{'  ' + detail if detail else ''}")
        if not cond:
            ok[0] = False

    js = client_js()
    note = note_html()

    print("the line under the field")
    # The long version explained which half of the box sends and which does not, and was not
    # read. What survives is the one fact a reader cannot discover by using the box: that
    # pressing sends. Losing that clause would leave a page that quietly calls a model.
    check("it says the model is still being worked on", "Model in training" in note)
    check("feedback is offered", 'id="askfbopen"' in note and "Send feedback" in note)
    # It is one short sentence and a control. Anything longer went unread twice.
    check("and it stays short", len(re.sub(r"<[^>]+>", "", note)) < 40, note)

    print("the feedback form")
    d = dialog_html("https://example.test/ajax/abc")
    check("it is a real dialog element", d.startswith("<dialog"))
    check("it posts to the action it was handed", "https://example.test/ajax/abc" in d)
    check("and labels itself so two products stay sortable", FEEDBACK_SUBJECT in d)
    check("the note field is required", 'name="feedback"' in d and "required" in d)
    check("email is optional", 'name="email"' in d and "Optional" in d)
    # Attaching somebody's conversation without showing it would be collecting it quietly.
    check("what gets attached is shown before it is sent",
          'id="askfbctxview"' in d and 'id="askfbattach"' in d)
    check("and attaching is a choice", 'type="checkbox"' in d)
    check("the attach row is hidden until there is something to attach",
          'id="askfbattachrow" hidden' in d)
    check("no endpoint is hardcoded here", "formsubmit" not in dialog_html("X"))
    js = client_js()
    check("nothing is attached when the box is unticked",
          'fbCheck.checked) ? lastExchange() : ""' in js)
    check("the exchange is read from the thread, not scraped off the page",
          "for (var i = turns.length - 1" in js)

    print("the house rules, over the copy a reader actually sees")
    # Read from COPY and the note, never from the source around them. A colon in a comment two
    # lines above a sentence is not a colon in the sentence, and an earlier version of this
    # check could not tell the two apart, so it failed on "use strict".
    prose = " ".join(list(COPY.values()) + [re.sub(r"<[^>]+>", "", note)])
    for mark, name in ((":", "colon"), (";", "semicolon"), ("\u2014", "em dash"),
                       ("\u2013", "en dash"), ("\u2019", "curly apostrophe")):
        check(f"no {name} in reader copy", mark not in prose,
              repr(prose[max(0, prose.find(mark) - 45):prose.find(mark) + 25])
              if mark in prose else "")
    check("never cannot", "cannot" not in prose.lower())
    check("no sentence opens with And or But",
          not any(re.match(r"^(And|But)\b", v) for v in COPY.values()))
    check("no first person in anything a reader is shown",
          not re.search(r"\b(?:I|we|our|us|my)\b", prose, re.I),
          repr(re.search(r".{0,40}\b(?:I|we|our|us|my)\b.{0,25}", prose, re.I).group(0))
          if re.search(r"\b(?:I|we|our|us|my)\b", prose, re.I) else "")

    print("every marker in the client resolves")
    # A marker with no entry would ship "%%chip%%" onto the front page as a button label.
    js_markers = set(re.findall(r"%%([a-z_]+)%%", _CLIENT))
    check("no marker is unresolved", not (js_markers - set(COPY)),
          str(sorted(js_markers - set(COPY))))
    check("and no copy entry is dead", not (set(COPY) - js_markers - {"placeholder"}),
          str(sorted(set(COPY) - js_markers - {"placeholder"})))

    print("the lanes stay separate")
    check("the client does nothing without an endpoint", 'if (!EP) return;' in js)
    # The promise above the field is only true if NOTHING goes out before the press. Focus is
    # not intent to ask, and tests/ask_engine.mjs asserts exactly this from the outside.
    check("turnstile is armed by focus", 'addEventListener("focus", armTurnstile' in js)
    check("...and it is armed once, not on every focus",
          '"focus", armTurnstile, { once: true }' in js)
    check("only guard approved text goes back to the model",
          'turns.push({ role: "assistant", content: said.join(" ") })' in js)

    print("the guard's reasons are all spoken for")
    # Every reason the worker can send needs words here. A reason with no copy falls through to
    # "could not be checked", which is true but tells a reader nothing.
    for reason in ("numeral", "citation", "voice", "verdict"):
        check(f"{reason} has a sentence", f"{reason}:" in js)

    print("the suggested follow-up waits in the field and never sends itself")
    check("it lands in the placeholder, lightly", 'input.placeholder = pending;' in js)
    check("accepting puts it in the field", "input.value = pending;" in js)
    # The whole point of two presses. Sending is the metered half, so a suggestion that sent
    # itself would spend on a mis-tap and on words the reader never saw in full.
    check("accepting returns before anything is sent",
          "if (!input.value.trim() && acceptPending()) return;" in js)
    check("tab and the right arrow take it too",
          'e.key === "Tab" || e.key === "ArrowRight"' in js)
    check("and neither steals a keystroke from somebody typing",
          "if (input.value || !pending) return;" in js)
    check("writing your own question puts it away", "if (input.value) dropPending();" in js)
    check("the send control says what it will do",
          '"%%accept%%"' in _CLIENT and '"%%send%%"' in _CLIENT)

    print()
    print("ask_written self-test clean" if ok[0] else "ask_written self-test FAILED")
    return 0 if ok[0] else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    print(f"ask_written: {len(client_js())} chars of client, endpoint {ENDPOINT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
