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
ENDPOINT = "https://texas-ask.talon-sturgill.workers.dev"

# Public by design. It identifies the widget to Cloudflare and is meant to be read by anyone
# who views source. The SECRET half lives in the worker and appears nowhere in this repository.
TURNSTILE_SITEKEY = "0x4AAAAAAEQ2csplf8Pifi79"


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
    "no_answer":    "The record does not answer that.",
    "failed":       "That did not get through. Try again in a moment.",
    "capped":       "That is this month's last written answer. Typing still searches the "
                    "whole record instantly and for nothing, which is most of what this box does.",
    "provenance":   "Written from the published record. Every figure checked against it.",
    "again":        "Start over",
    "chip":         "Yes, show me",
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
    """The honest half of the offer, above the control it describes.

    Both sentences are load bearing and neither may be softened without changing what the code
    does. Typing really does send nothing. Pressing really does send the question.
    """
    return (
        '<p class="asknote">Typing searches the record here in your browser and '
        '<b>sends nothing anywhere</b>. Press enter and the question goes to a model that '
        'writes an answer from that same record, checked line by line against it.</p>'
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
  /* The conversation, held in the page only. Nothing is stored anywhere, it goes when the tab
     does, and it is what makes "when does that close" mean something on its own. The worker
     keeps no session either: the thread travels with each question. */
  var turns = [];

  /* ---- the human check ---------------------------------------------------
     ARMED ON THE FIRST SUBMIT, AND NOT BEFORE.
     This was on focus, which was faster and was wrong. The note above the field says typing
     sends nothing anywhere, and arming on focus fetched Cloudflare's script the moment a
     caret landed in the field, so a request left the page during what that note calls typing.
     tests/ask_engine.mjs caught it, because that suite asserts no request leaves the page
     after ANY interaction, and it was right to.
     The cost is about a second on the first question while the widget loads and solves. That
     is bounded, it happens once, and the stage line says what the wait is for. A promise that
     is literally true is worth more than a second. */
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
  function waitForToken(stage) {
    if (!SITEKEY) return Promise.resolve("");
    if (tsToken) return Promise.resolve(tsToken);
    stage("%%stage_human%%");
    /* Keep waiting rather than giving up if the script is slow: a bad connection is not a
       failed check, and this box exists for people on bad connections. */
    return new Promise(function (resolve) {
      var n = 0;
      var t = setInterval(function () {
        if (tsToken) { clearInterval(t); resolve(tsToken); return; }
        if (++n > 150) { clearInterval(t); resolve(""); }
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

  /* A LINK INSIDE A SENTENCE HAS TO BE A HANDLE, NOT A HEADLINE. Titles on this record are
     descriptive sentences, 106 characters on average, and dropping one whole into a paragraph
     buried the paragraph: four lines of gold link around six words of prose.
     The first clause is the handle where there is one, which is why "PUCT Project 58000,
     rulemaking to update ERCOT transmission cost recovery, comment deadline reached" reads as
     "PUCT Project 58000". Most titles here carry no comma at all, so anything still long is cut
     at a word boundary. The full title rides along as the link's tooltip and the whole thing is
     one click away, so nothing is lost by not shouting it. */
  function handle(id) {
    var t = TITLES[id];
    if (!t) return id;
    var first = t.split(",")[0];
    if (first.length <= 44) return first;
    var cut = first.slice(0, 40);
    var sp = cut.lastIndexOf(" ");
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
      a.href = BASE + "item/" + m[1] + "/";
      a.textContent = handle(m[1]);
      a.title = TITLES[m[1]] || m[1];
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
    thread.textContent = "";
    thread.hidden = true;
    box.classList.remove("answering");
    input.value = "";
    input.placeholder = "%%placeholder%%";
    input.focus();
    /* Give the engine back its live list for whatever is in the field now. */
    input.dispatchEvent(new Event("input", { bubbles: true }));
  }

  /* ---- asking ------------------------------------------------------------ */
  function ask(question) {
    if (busy) return;
    busy = true;
    send.disabled = true;
    send.setAttribute("aria-busy", "true");
    box.classList.add("answering");
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
    thread.appendChild(body);

    input.value = "";
    input.placeholder = "%%followup%%";

    /* The question goes to the top and the answer arrives under it, the way a conversation
       moves. Not scrollIntoView: the masthead is sticky, so start-of-element lands under it.
       Its height is measured rather than guessed, because a guess is wrong on one phone. */
    var nav = document.querySelector(".masthead, nav.main");
    window.scrollTo({
      behavior: "smooth",
      top: asked.getBoundingClientRect().top + window.pageYOffset -
           ((nav ? nav.getBoundingClientRect().height : 0) + 16)
    });

    /* The first press is the intent that arms the human check. Everything before it, focus
       and typing included, leaves the page alone. */
    armTurnstile();

    var stageEl = null, started = false, para = null, said = [];

    function stage(text) {
      if (!stageEl) {
        body.textContent = "";
        stageEl = document.createElement("div");
        stageEl.className = "askstage";
        body.appendChild(stageEl);
      }
      stageEl.textContent = text;
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
    }

    function finish() {
      /* What it SAID goes back into the thread, not what it tried to say. A sentence the
         reader never saw must not be one the model can build on either, or a refused claim
         re-enters through the back door on the next question. */
      if (said.length) turns.push({ role: "assistant", content: said.join(" ") });
      else turns.pop();

      busy = false;
      send.disabled = false;
      send.removeAttribute("aria-busy");
      spendToken();

      clearTrailing();

      var next = said.length ? followUp(said[said.length - 1]) : null;
      if (next) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "asknext";
        chip.textContent = "%%chip%%";
        chip.addEventListener("click", function () {
          input.value = next;
          input.focus();
          try { input.setSelectionRange(next.length, next.length); } catch (e) {}
          chip.remove();
        });
        thread.appendChild(chip);
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
      thread.appendChild(foot);
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

    waitForToken(stage).then(function (tok) {
      stage("%%stage_read%%");
      return fetch(EP + "/answer", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ messages: turns, turnstile_token: tok || null })
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
      return (function pump() {
        return reader.read().then(function (res) {
          if (res.done) {
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
      if (!started && !body.textContent) body.textContent = "%%no_answer%%";
      finish();
    }).catch(function () {
      dropStage();
      if (!started) body.textContent = "%%failed%%";
      finish();
    });
  }

  /* SUBMIT IS THE WRITTEN LANE NOW. It used to re-run the engine, which is what typing already
     does, so pressing enter did nothing a reader could see. */
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = input.value.trim();
    if (!q) return;
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

    print("the honest half of the offer")
    check("the note says typing sends nothing", "sends nothing anywhere" in note)
    check("and that pressing enter does send", "goes to a model" in note)
    # Both halves have to be there. A note carrying only the reassuring half is worse than no
    # note, because it reads as a promise about the whole box.
    check("neither half stands alone",
          "sends nothing" in note and "Press enter" in note)

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
    check("turnstile is armed by the press, not by focus or load",
          "armTurnstile();" in js and 'addEventListener("focus", armTurnstile' not in js)
    check("only guard approved text goes back to the model",
          'turns.push({ role: "assistant", content: said.join(" ") })' in js)

    print("the guard's reasons are all spoken for")
    # Every reason the worker can send needs words here. A reason with no copy falls through to
    # "could not be checked", which is true but tells a reader nothing.
    for reason in ("numeral", "citation", "voice", "verdict"):
        check(f"{reason} has a sentence", f"{reason}:" in js)

    print("the follow-up chip fills, and never sends")
    check("it sets the field", "input.value = next;" in js)
    check("and there is no submit in its handler",
          "chip.addEventListener" in js and "ask(next)" not in js)

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
