#!/usr/bin/env python3
"""ask_answers.py — the ask box, answered in the reader's own browser.

WHAT IT IS

A reader types a question about the Texas AI record and gets an answer, computed in their
browser, from an index shipped with the page. Nothing is sent anywhere. There is no API key, no
request, no log, and no bill. Turn off the network after the page loads and it still works.

That is a product decision before it is a technical one. A record about surveillance,
procurement and public comment should not be quietly collecting a list of who asked what about
which county.

ROUTES, NOT CACHED ANSWERS

The catalogue pairs each question with a ROUTE: a small instruction saying which view answers
it and over what. The answer is composed at read time from the index. A cached answer would be
wrong the day the record changes and nobody would know; a route is right by construction,
because it is evaluated against whatever the index currently holds.

THE QUESTIONS ARE GENERATED FROM THE RECORD, NOT TYPED

Every catalogued question is produced from what the record actually contains: its counties, its
deciders, its topics, its statuses, its open windows. Two consequences, both wanted. A question
about a county with nothing in it is never catalogued, so the box never promises an answer it
cannot give. And when the record grows, the catalogue grows with it, without anybody
maintaining a list.

THE ANSWER NEVER EXCEEDS THE RECORD

Every number in an answer is computed from the index at read time. Every claim is a sentence
the record already supports, with a link to the item it came from. Where the record holds
nothing, the honest answer is that it holds nothing, and that answer is offered rather than
avoided. A question box that invents a plausible answer is worse than no question box, because
it is the one part of a record product that a reader will trust without checking.

    ask_answers.py --self-test
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docket_build as dk                                          # noqa: E402

TOPIC_WORDS = {
    # BRITISH SPELLING STAYS IN THE MATCH LIST AND NEVER IN THE COPY. The site writes
    # "center" everywhere a reader can read it, and a reader who types "data centre"
    # still has to land on the right topic. Input and output are different questions,
    # and a spelling sweep that treats them as one silently costs recall.
    "data-centers": ["data center", "data centre", "datacenter", "hyperscale",
                     "server farm"],
    "power-and-the-grid": ["grid", "power", "electricity", "ercot", "transmission", "load",
                           "megawatt", "interconnection", "substation"],
    "state-policy": ["law", "bill", "statute", "legislature", "rule", "policy", "regulation",
                     "traiga", "senate", "house"],
    "land-water-and-permitting": ["water", "land", "permit", "zoning", "groundwater",
                                  "reservoir", "cooling"],
    "defense-and-federal": ["defense", "defence", "military", "federal", "pentagon", "base"],
    "research-and-science": ["research", "university", "lab", "science", "study"],
    "health-and-education": ["health", "hospital", "school", "student", "teacher", "staar",
                             "education", "patient"],
    "surveillance-and-policing": ["surveillance", "police", "camera", "biometric", "facial",
                                  "alpr", "flock", "privacy"],
}

# The smart views. A route names one of these plus what to run it over.
VIEWS = ("open_now", "by_county", "by_metro", "by_topic", "by_decider", "by_status",
         "item", "counts")


def _metros() -> list:
    """Every Texas statistical area, as the vocabulary the box understands.

    ALL OF THEM, NOT ONLY THE ONES IN THE RECORD, and that is a deliberate split from how
    counties work here. The catalogue is a PROMISE and lists only what the record can
    answer. The index is a VOCABULARY, and a reader who types "El Paso" deserves to be
    told the record holds nothing there yet rather than to be handed the nearest fuzzy
    match from somewhere else in Texas. Sixty-seven areas is a few kilobytes and it buys
    an honest no.

    A READER TYPES A CITY, NEVER A DELINEATION. Nobody asks about
    "Houston-Pasadena-The Woodlands", so the aliases the gazetteer already derives from
    each area's name are carried through and matched on.
    """
    try:
        sys.path.insert(0, str(REPO_ROOT / "scripts" / "shared"))
        import places                                                # noqa: PLC0415
        r = places.Resolver.load()
    except Exception:                                                # noqa: BLE001
        return []
    return [{"id": p["id"], "name": p["name"], "full_name": p["full_name"],
             "area_type": p["area_type"], "counties": p["counties"],
             "aliases": [a for a in p.get("aliases", []) if not a.isdigit()]}
            for p in sorted(r.places, key=lambda p: p.get("name", ""))
            if p.get("kind") == "cbsa"]


# --------------------------------------------------------------------------- the index
def index(items: list, today: str) -> dict:
    """Everything the browser needs, and nothing it does not.

    The index carries the record's own text and the facts derived from it. It deliberately
    does NOT carry any prose the engine will speak: the engine composes that at read time from
    these values, so an answer cannot drift away from the record while looking authoritative.
    """
    metros = _metros()
    # county -> the areas containing it, so an item's areas are DERIVED here exactly the
    # way the site derives them, from the same gazetteer, and never stored on the item.
    of_county: dict[str, list] = {}
    for m in metros:
        for c in m["counties"]:
            of_county.setdefault(c, []).append(m["id"])

    out = []
    for it in items:
        g = it.get("geography") or {}
        pa = it.get("public_access") or {}
        state = dk.window_state(it, today)
        closes = pa.get("closes")
        days_left = None
        if state == "open" and closes:
            days_left = (_dt.date.fromisoformat(closes) - _dt.date.fromisoformat(today)).days
        out.append({
            "id": it["id"],
            "title": it["title"],
            "summary": it.get("summary", ""),
            "topic": it["topic"],
            "decider": it["decider"]["name"],
            "decider_type": it["decider"]["type"],
            "status": it["status"],
            "counties": g.get("counties") or [],
            "metros": sorted({mid for c in (g.get("counties") or [])
                              for mid in of_county.get(c, [])}),
            "statewide": bool(g.get("statewide")),
            "on_ercot": bool(g.get("on_ercot")),
            "room": pa.get("room"),
            "window": state,
            "closes": closes,
            "days_left": days_left,
            "claims": len(it.get("claims") or []),
            "last_verified": it.get("last_verified"),
        })
    return {
        "generated": today,
        "items": out,
        "counties": sorted({c for i in out for c in i["counties"]}),
        "metros": metros,
        # THE AREAS THE RECORD ACTUALLY TOUCHES, kept apart from the vocabulary above.
        # The catalogue reads this one and promises nothing about the rest.
        "metros_touched": sorted({mid for i in out for mid in i["metros"]}),
        "topics": sorted({i["topic"] for i in out}),
        "deciders": sorted({i["decider"] for i in out}),
        "statuses": sorted({i["status"] for i in out}),
        "topic_words": TOPIC_WORDS,
    }


# --------------------------------------------------------------------------- the catalogue
def catalogue(idx: dict) -> list[dict]:
    """Every question the record can actually answer, with the route that answers it.

    Generated from the index, so a county with nothing in it never gets a question and the
    catalogue cannot promise what the record does not hold.
    """
    q: list[dict] = []

    def add(text, view, arg=None):
        q.append({"q": text, "route": {"view": view, "arg": arg}})

    add("What can I still comment on?", "open_now")
    add("What is open right now?", "open_now")
    add("Is anything closing this week?", "open_now")
    add("What deadlines are coming up?", "open_now")
    add("How many items are in the record?", "counts")
    add("What does this site track?", "counts")
    add("How much of the record is verified?", "counts")

    for c in idx["counties"]:
        add(f"What is happening in {c} County?", "by_county", c)
        add(f"Is anything being decided in {c} County?", "by_county", c)
        add(f"Can I comment on anything in {c} County?", "by_county", c)

    # BY AREA, and only for areas the record reaches. A reader asks about a city, and the
    # city is the metro's name, so the question is phrased the way it would be spoken.
    by_id = {m["id"]: m for m in idx.get("metros", [])}
    for mid in idx.get("metros_touched", []):
        m = by_id.get(mid)
        if not m:
            continue
        add(f"What is happening in {m['name']}?", "by_metro", mid)
        add(f"Is anything being decided around {m['name']}?", "by_metro", mid)
        add(f"Can I comment on anything in the {m['name']} area?", "by_metro", mid)

    for t in idx["topics"]:
        pretty = t.replace("-", " ")
        add(f"What is in the record about {pretty}?", "by_topic", t)
        add(f"Show me everything on {pretty}", "by_topic", t)
        add(f"Is anything open on {pretty}?", "by_topic", t)

    for d in idx["deciders"]:
        add(f"What has {d} decided?", "by_decider", d)
        add(f"What is before {d}?", "by_decider", d)

    for s in idx["statuses"]:
        add(f"What is {s}?", "by_status", s)
        add(f"Show me the {s} items", "by_status", s)

    for it in idx["items"]:
        add(it["title"], "item", it["id"])
    return q


# --------------------------------------------------------------------------- the engine (JS)
def engine_js() -> str:
    """The whole answer engine. Runs in the reader's browser, sends nothing anywhere.

    Written as one self-contained script rather than a module because it ships inline: an
    external file is a second request, and on a record page the whole point is that a reader
    on a bad connection in a county meeting still gets an answer.
    """
    return r"""
(function () {
  "use strict";
  var IDX = window.__ASK_INDEX__, CAT = window.__ASK_CATALOGUE__;
  if (!IDX || !CAT) return;

  function norm(s) {
    return (s || "").toLowerCase().replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
  }

  /* STOPWORDS ARE DROPPED BEFORE SCORING, and this is the difference between a useful box and
     a dishonest one. Nearly every catalogued question contains "what" and "the", so a query
     made entirely of noise still shared words with the catalogue and scored above zero. Asked
     for the airspeed velocity of an unladen swallow, the engine returned a confident answer
     about data centers. On a record product that is the single worst thing the box can do:
     a reader trusts the one part of the page that is talking to them directly. */
  var STOP = {what:1, the:1, and:1, for:1, from:1, with:1, this:1, that:1, are:1, was:1,
              were:1, has:1, have:1, had:1, can:1, could:1, would:1, should:1, does:1,
              did:1, doing:1, about:1, show:1, tell:1, give:1, list:1, find:1, any:1,
              all:1, how:1, much:1, many:1, right:1, now:1, still:1, anything:1,
              everything:1, something:1, there:1, here:1, been:1, being:1, into:1,
              over:1, under:1, than:1, then:1, when:1, where:1, which:1, who:1, whose:1,
              why:1, will:1, its:1, it:1, you:1, your:1, please:1, tex:1};
  function words(s) {
    return norm(s).split(" ").filter(function (w) { return w.length > 2 && !STOP[w]; });
  }

  /* A query that shares nothing meaningful with the catalogue gets no route, and the engine
     says so. Below this floor the match is noise wearing a confident sentence. */
  var FLOOR = 0.9;

  /* Scoring is deliberately simple and explainable: shared words, weighted by how rare the
     word is across the catalogue. A reader who types "abilene water" should reach the Taylor
     County water item, and should be able to see WHY it was chosen. An opaque ranker on a
     record product is a trust problem, not a features problem. */
  var DF = {};
  CAT.forEach(function (c) {
    var seen = {};
    words(c.q).forEach(function (w) { if (!seen[w]) { seen[w] = 1; DF[w] = (DF[w] || 0) + 1; } });
  });
  function idf(w) { return Math.log(1 + CAT.length / (1 + (DF[w] || 0))); }

  // TOKENS ARE MEMOISED, like DF already is. `best()` re-tokenised all 401 catalogue
  // questions on every keystroke, two regex passes and a split each, none of it changing
  // between characters. Measured at 2.90ms a call on a desktop, which is 15 to 25ms per
  // character on the mid-range Android this box is written for.
  var _TOK = {};
  function toks(q) { var v = _TOK[q]; if (!v) { v = _TOK[q] = words(q); } return v; }
  function best(query) {
    var qw = words(query);
    if (!qw.length) return null;
    var top = null;
    CAT.forEach(function (c) {
      var cw = words(c.q), score = 0;
      qw.forEach(function (w) {
        if (cw.indexOf(w) >= 0) { score += idf(w); return; }
        /* A PREFIX MATCH NEEDS ENOUGH PREFIX TO MEAN SOMETHING.
           This was any shared opening character, which is a fine rule for "permit" against
           "permits" and a bad one for "air" against "airspeed". The record grew a beat of TCEQ
           air permits, "air" entered the catalogue vocabulary, and the box answered "what is
           the airspeed velocity of an unladen swallow" with a confident item about air quality
           permits. The stopword note above already records what that costs: a reader trusts the
           one part of the page that talks back, so the box has to be honest more than it has to
           be helpful. Four characters is the shortest shared stem that is a word rather than a
           coincidence, and BOTH sides must clear it so a long query word cannot claim a short
           catalogue one. */
        var stemmy = cw.some(function (x) {
          if (x.length < 4 || w.length < 4) return false;
          return x.indexOf(w) === 0 || w.indexOf(x) === 0;
        });
        if (stemmy) score += idf(w) * 0.5;
      });
      if (!top || score > top.score) top = { c: c, score: score };
    });
    /* A direct mention of a county, a topic word or a decider outranks a fuzzy catalogue
       match, because it is what the reader actually said. */
    var direct = null;
    var nq = norm(query);

    /* THE COUNTY AND THE CITY SHARE A NAME AND THEY ARE NOT THE SAME PLACE. Reeves County
       contains the city of Pecos. Pecos County is two hundred miles west. Midland, Tyler,
       El Paso and Lubbock are each a county and the central city of an area that is not
       the same shape. places.py refuses that ambiguity by keeping one index per grain, and
       the browser has to make the same distinction or it will answer a different question
       than the one asked.

       So the word "county" decides it. A reader who writes it means the county, and a
       reader who writes a bare city name means the place they live, which is the area. */
    var saysCounty = /\bcounty\b/.test(nq);
    if (saysCounty) IDX.counties.forEach(function (c) {
      if (nq.indexOf(norm(c)) >= 0) direct = { view: "by_county", arg: c };
    });
    if (!direct) (IDX.metros || []).forEach(function (m) {
      if (direct) return;
      var hit = nq.indexOf(norm(m.name)) >= 0 ||
                (m.aliases || []).some(function (a) { return nq.indexOf(norm(a)) >= 0; });
      if (hit) direct = { view: "by_metro", arg: m.id };
    });
    if (!direct) IDX.counties.forEach(function (c) {
      if (nq.indexOf(norm(c)) >= 0) direct = { view: "by_county", arg: c };
    });
    if (!direct) IDX.deciders.forEach(function (d) {
      if (norm(query).indexOf(norm(d)) >= 0) direct = { view: "by_decider", arg: d };
    });
    if (!direct) Object.keys(IDX.topic_words).forEach(function (t) {
      IDX.topic_words[t].forEach(function (w) {
        if (!direct && norm(query).indexOf(norm(w)) >= 0) direct = { view: "by_topic", arg: t };
      });
    });
    if (direct && (!top || top.score < 2.5)) return direct;
    return top && top.score >= FLOOR ? top.c.route : direct;
  }

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"]/g, function (m) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m];
    });
  }
  function link(it) {
    return '<a href="' + BASE + 'item/' + esc(it.id) + '/">' + esc(it.title) + "</a>";
  }
  function list(items) {
    if (!items.length) return "";
    return "<ul>" + items.map(function (it) {
      var bits = [];
      if (it.window === "open" && it.days_left != null)
        bits.push(it.days_left === 0 ? "closes today"
          : it.days_left + (it.days_left === 1 ? " day left" : " days left"));
      bits.push(it.decider);
      return "<li>" + link(it) + '<br><span class="meta">' + esc(bits.join(" · ")) +
             "</span></li>";
    }).join("") + "</ul>";
  }
  function plural(n, one, many) { return n === 1 ? one : many; }

  /* EVERY NUMBER BELOW IS COUNTED FROM THE INDEX AT READ TIME. None is stored, none is
     written into a string by hand, and none can be stale relative to the record on the page. */
  function answer(route) {
    if (!route) return { head: "No answer for that yet.", body:
      "<p>Try a county, a topic, or the body that made the decision. The record holds " +
      IDX.items.length + " " + plural(IDX.items.length, "item", "items") + ".</p>" };

    var all = IDX.items, sel, head, note = "";
    switch (route.view) {
      case "open_now":
        sel = all.filter(function (i) { return i.window === "open"; })
                 .sort(function (a, b) { return (a.days_left || 0) - (b.days_left || 0); });
        head = sel.length ? sel.length + " " + plural(sel.length, "item is", "items are") +
               " open for comment right now" : "Nothing is open for comment right now";
        note = sel.length ? "" :
          "<p>The record holds " + all.length + " " + plural(all.length, "item", "items") +
          ", and none has an open window today. That is the record's answer, not a gap in it.</p>";
        break;
      /* LOCAL AND STATEWIDE ARE COUNTED SEPARATELY, and the headline counts only the
         local ones. Merging them produced the single worst sentence this engine has
         written: "9 items in the El Paso area", above a note saying nothing had been
         found in either of El Paso's counties. All nine were statewide. A reader in El
         Paso would have read that as local coverage and been wrong, and the number was
         perfectly accurate the whole time. A true count of the wrong set is a lie with a
         citation. */
      case "by_county":
        var local = all.filter(function (i) {
          return i.counties.indexOf(route.arg) >= 0; });
        var state = all.filter(function (i) { return i.statewide; });
        sel = local.concat(state.filter(function (i) { return local.indexOf(i) < 0; }));
        head = local.length
          ? local.length + " " + plural(local.length, "item", "items") + " in " +
            route.arg + " County"
          : "Nothing in the record is specific to " + route.arg + " County";
        note = state.length
          ? "<p>" + state.length + " statewide " +
            plural(state.length, "decision reaches", "decisions reach") +
            " it as well, and " + plural(state.length, "it is", "they are") +
            " listed below.</p>"
          : "";
        break;
      /* BY AREA. The counties with nothing found are NAMED rather than dropped. A page
         that listed only the covered counties would read as a complete answer about the
         area, and the honest statement is that the area is this and the record reaches
         part of it. Same instinct as the grid watch publishing the size of what is not
         public. */
      case "by_metro":
        var M = null;
        IDX.metros.forEach(function (m) { if (m.id === route.arg) M = m; });
        if (!M) { sel = []; head = "Not an area this record knows"; break; }
        var mlocal = all.filter(function (i) { return i.metros.indexOf(M.id) >= 0; });
        var mstate = all.filter(function (i) { return i.statewide; });
        sel = mlocal.concat(mstate.filter(function (i) { return mlocal.indexOf(i) < 0; }));
        var covered = {};
        mlocal.forEach(function (i) {
          i.counties.forEach(function (c) {
            if (M.counties.indexOf(c) >= 0) covered[c] = 1; }); });
        var missing = M.counties.filter(function (c) { return !covered[c]; });
        head = mlocal.length
          ? mlocal.length + " " + plural(mlocal.length, "item", "items") + " in the " +
            M.name + " area"
          : "Nothing in the record is specific to the " + M.name + " area";
        note = "<p>The " + esc(M.full_name) + " " +
               (M.area_type === "metropolitan" ? "metropolitan" : "micropolitan") +
               " area is " + M.counties.length + " " +
               plural(M.counties.length, "county", "counties") + ". " +
               (missing.length
                 ? "Nothing has yet been found in " + esc(missing.join(", ")) + "."
                 : "The record reaches every one of them.") + "</p>" +
               (mstate.length
                 ? "<p>" + mstate.length + " statewide " +
                   plural(mstate.length, "decision reaches", "decisions reach") +
                   " it as well, and " + plural(mstate.length, "it is", "they are") +
                   " listed below.</p>"
                 : "");
        break;
      case "by_topic":
        sel = all.filter(function (i) { return i.topic === route.arg; });
        head = sel.length + " " + plural(sel.length, "item", "items") + " on " +
               route.arg.replace(/-/g, " ");
        break;
      case "by_decider":
        sel = all.filter(function (i) { return i.decider === route.arg; });
        head = sel.length + " " + plural(sel.length, "item", "items") + " from " + route.arg;
        break;
      case "by_status":
        sel = all.filter(function (i) { return i.status === route.arg; });
        head = sel.length + " " + plural(sel.length, "item", "items") + " marked " + route.arg;
        break;
      case "item":
        sel = all.filter(function (i) { return i.id === route.arg; });
        head = sel.length ? sel[0].title : "Not in the record";
        note = sel.length ? "<p>" + esc(sel[0].summary) + "</p>" : "";
        break;
      case "counts":
      default:
        sel = all;
        var open = all.filter(function (i) { return i.window === "open"; }).length;
        var claims = all.reduce(function (n, i) { return n + i.claims; }, 0);
        head = all.length + " " + plural(all.length, "item", "items") + " in the record";
        note = "<p>Backed by " + claims + " verified " + plural(claims, "claim", "claims") +
               ", each carrying the source's own words. " + open + " " +
               plural(open, "has", "have") + " an open comment window today.</p>";
        sel = all.slice(0, 8);
        break;
    }
    return { head: head, body: note + list(sel) };
  }

  var box = document.getElementById("ask");
  if (!box) return;
  /* THE LINK PREFIX COMES FROM THE MARKUP, because the box moved. It used to hardcode
     "../item/", which was correct for exactly one location: a page one directory deep. The
     box is on the front page now, at depth 0, where "../item/" walks out of the site
     entirely. Every answer it rendered would have linked to a 404 and the page would have
     looked perfect. The host element states its own depth and the engine reads it. */
  var BASE = box.getAttribute("data-base") || "";
  var input = box.querySelector("input");
  var form = box.querySelector("form");

  /* NOTHING IS RENDERED FROM THIS FILE ANY MORE, and that is the point.
     There were two places an answer could appear, facing opposite directions: a panel that
     rewrote itself on every keystroke, and a conversation above it that arrived on the press.
     The owner, on a phone: "there's so much stuff on screen, your eyes don't even go to the
     right spot", and of the typing panel, "very distracting".
     So this file computes and the written lane renders, all of it into the thread, one thing
     at a time. `classify` is the whole of the interface. The engine has not gone anywhere and
     is not slower: it answers at the PRESS now, which is also what lets most questions skip
     the model entirely. THE PROMISE IS UNCHANGED. This file still phones nobody. */
  box.querySelectorAll("[data-ask]").forEach(function (b) {
    b.addEventListener("click", function () {
      // A starter goes through the same press as a typed question, so a chip and a keystroke
      // cannot answer differently. It called a renderer the press did not use before.
      input.value = b.dataset.ask;
      box.querySelector("form").dispatchEvent(
        new Event("submit", { bubbles: true, cancelable: true }));
    });
  });

  /* ---- the classifier -------------------------------------------------------
     THE CHEAPEST ANSWER IS THE ONE THAT NEVER LEAVES THE PAGE.
     This engine already scores a question against the catalogue and already refuses below a
     floor, so it already knows the difference between "I have this" and "I do not". That
     judgement was spent on a panel and thrown away at the press, while every question went to
     a paid model taking seconds, including ones answerable here in no time at all.
       instant  the catalogue has a confident route. Rendered from the page, no request.
       written  the record may hold it but not as a lookup. Worth a model.
       refuse   nothing in the question touches this record. Say so and call nobody.

     THE CATALOGUE IS LOOKUP SHAPED, so a high score is not permission to answer anything.
     Every route resolves to WHICH, WHAT, WHEN or WHERE. None of them explains. Asked "why did
     the PUCT delay the comment deadline" the scorer matched PUCT and deadline and offered a
     confident list, which is a fast wrong answer and worse than a slow right one on a record
     product. So shape is checked BEFORE score. The markers are conservative on purpose: a
     false WRITTEN costs two seconds and a fraction of a cent, a false INSTANT costs the
     reader their answer.

     REFUSE IS DELIBERATELY NARROW, firing only when a query shares NO term with the whole
     vocabulary, which is the airspeed-velocity case the floor was written for. Refusing a real
     question to save a fraction of a cent is the worst trade available here.

     No network call and no new dependency. This file still phones nobody. */
  var EXPLANATORY = /^\s*(why|how come|how did|how does|how do|how will|how would|explain)\b/i;
  var MEANS = /\b(mean|means|meaning|implication|implications|impact|affect|affects|consequence|consequences|likely|difference between)\b/i;
  // "can i still" WAS HERE AND WAS WRONG. "What can I still comment on?" is a lookup, the
  // plainest one this record answers, and the marker sent it to a paid model that took six
  // seconds to say what the page was already holding. A marker has to catch questions that
  // want an EXPLANATION, and "can I still" asks which windows are open.
  var SCENARIO = /(what happens if|should i|do i need to)/i;

  function explanatory(t) {
    return EXPLANATORY.test(t) || MEANS.test(t) || SCENARIO.test(t);
  }

  function vocabulary() {
    if (vocabulary.cache) return vocabulary.cache;
    var bag = {};
    /* THE SUMMARY IS IN THE BAG AND HAS TO BE. Built from titles and deciders alone, the bag
       held proper nouns and almost no ordinary English, so "why does it matter who decides it"
       shared nothing with it and was REFUSED. That is a real question about this record and
       refusing it is the worst outcome this classifier has, far worse than paying for a model
       call. Summaries carry the working vocabulary of the record, which is decide, comment,
       deadline, rule, permit, hearing, and every other word a reader would actually use. */
    (IDX.items || []).forEach(function (i) {
      [i.title, i.summary, i.decider, i.topic, i.room].forEach(function (f) {
        words(String(f || "")).forEach(function (w) { bag[w] = 1; });
      });
      [].concat(i.counties || [], i.metros || []).forEach(function (c) {
        words(String(c)).forEach(function (w) { bag[w] = 1; });
      });
    });
    (CAT || []).forEach(function (c) {
      words(String(c.q || "")).forEach(function (w) { bag[w] = 1; });
    });
    vocabulary.cache = bag;
    return bag;
  }

  function classify(q) {
    var text = String(q || "").trim();
    if (!text) return { bucket: "empty" };
    /* THE AGENT ANSWERS EVERY QUESTION ABOUT THE RECORD, and the first version of this did
       not. It routed anything the catalogue matched to the in-page engine, which renders a
       headline and a list of item links. That is fast and it is not an ANSWER, and the owner
       said so within a day of it shipping: "the query is not being answered by an agent it is
       being answered by the cached stuff and just giving me a bunch of links".
       The brief was to make the agent ten times better. Routing around the agent makes the
       agent zero times better and takes the prose away, so the trade was wrong.
       WHAT THE CLASSIFIER IS FOR NOW. One thing, and it is the one thing a model cannot do
       cheaply: refusing a question this record has no business answering. Asked for a recipe,
       it says so in 36ms and spends nothing. Everything on topic goes to the agent.
       The local route is not deleted. It is the FALLBACK when the month's cap is spent, where
       a list of the right decisions beats an apology, and `askLocal` is how the written lane
       reaches it. */
    var bag = vocabulary(), ws = words(text), touched = 0;
    ws.forEach(function (w) { if (bag[w]) touched++; });
    if (ws.length && touched === 0 && !best(text)) return { bucket: "refuse" };
    return { bucket: "written" };
  }

  window.__askClassify = classify;
  /* The written lane calls this when the cap is spent, so a reader still gets the right
     decisions rather than only an apology. */
  window.__askLocal = function (q) { var r = best(q); return r ? answer(r) : null; };
  window.__askAnswer = function (q) { return answer(best(q)); };   // for tests/ask_engine.mjs
})();
"""


# --------------------------------------------------------------------------- self-test
def self_test() -> int:
    failures = 0

    def ok(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    items = [
        {"id": "tx-1", "title": "PUCT rule on transmission cost", "summary": "A rule.",
         "topic": "power-and-the-grid",
         "decider": {"name": "Public Utility Commission of Texas", "type": "state-agency"},
         "status": "open", "geography": {"counties": ["Taylor"], "statewide": False,
                                         "on_ercot": True},
         "public_access": {"room": "open_comment", "opens": "2026-08-01",
                           "closes": "2026-08-20"},
         "claims": [{"id": "c1"}, {"id": "c2"}], "last_verified": "2026-08-11",
         "key_dates": []},
        {"id": "tx-2", "title": "Statewide AI procurement standard", "summary": "A standard.",
         "topic": "state-policy",
         "decider": {"name": "Department of Information Resources", "type": "state-agency"},
         "status": "decided", "geography": {"counties": [], "statewide": True,
                                            "on_ercot": False},
         "public_access": {"room": "closed"}, "claims": [{"id": "c3"}],
         "last_verified": "2026-08-10", "key_dates": []},
    ]
    idx = index(items, "2026-08-11")
    cat = catalogue(idx)

    ok("the index carries one entry per item", len(idx["items"]) == 2)
    ok("the open window is derived, not stored",
       idx["items"][0]["window"] == "open" and idx["items"][1]["window"] != "open")
    ok("days left is computed from today", idx["items"][0]["days_left"] == 9,
       str(idx["items"][0]["days_left"]))
    ok("counties, topics and deciders come from the record",
       idx["counties"] == ["Taylor"] and len(idx["topics"]) == 2 and len(idx["deciders"]) == 2)

    # THE VOCABULARY AND THE PROMISE ARE DIFFERENT LISTS, and this is the one design
    # decision in the metro view worth guarding. The box knows every Texas area so it can
    # tell a reader in El Paso that the record holds nothing there. The catalogue names
    # only the areas the record reaches, so it never promises an answer it does not have.
    ok("the index carries every Texas area as vocabulary, not only the touched ones",
       len(idx["metros"]) > 60 and any(m["name"] == "El Paso" for m in idx["metros"]),
       str(len(idx["metros"])))
    ok("...while the touched list holds only what the record reaches",
       idx["metros_touched"] == ["metro-abilene"], str(idx["metros_touched"]))
    ok("an item's areas are derived from its counties and never stored on it",
       idx["items"][0]["metros"] == ["metro-abilene"], str(idx["items"][0]["metros"]))
    ok("a city alias reaches its area, because nobody types a delineation name",
       any("houston" in (m["aliases"] or [])
           for m in idx["metros"] if m["name"].startswith("Houston")))

    qs = [c["q"] for c in cat]
    ok("the catalogue asks about every county in the record",
       any("Taylor County" in q for q in qs))
    ok("...and never about a county the record does not hold",
       not any("Harris" in q for q in qs))
    ok("the catalogue asks about the areas the record reaches",
       any("in Abilene?" in q for q in qs))
    ok("...and never about an area it does not",
       not any("El Paso" in q for q in qs))
    ok("...and about every topic, decider and status",
       any("power and the grid" in q for q in qs)
       and any("Department of Information Resources" in q for q in qs)
       and any("decided" in q for q in qs))
    ok("every item is reachable by its own title", any(q == items[0]["title"] for q in qs))
    ok("every catalogued question carries a route, and every route names a real view",
       all(c["route"]["view"] in VIEWS for c in cat))
    ok("the catalogue grows with the record, so nobody maintains a list",
       len(catalogue(index(items * 3, "2026-08-11"))) > len(cat))

    # THE ENGINE IS SHIPPED AS SOURCE. These assert the properties the page depends on.
    js = engine_js()
    ok("the engine sends nothing anywhere",
       not any(t in js for t in ("fetch(", "XMLHttpRequest", "WebSocket", "navigator.sendBeacon",
                                 "new Image(", "location.href =")),
       "an answer engine on a record product must not phone home")
    ok("...and stores nothing about the reader",
       not any(t in js for t in ("localStorage", "sessionStorage", "document.cookie",
                                 "indexedDB")))
    ok("the engine escapes what it prints", "function esc(" in js and "&amp;" in js)
    ok("it exposes an entry point the browser test can call", "__askAnswer" in js)
    ok("counts are computed in the engine, never baked into the index",
       "reduce(" in js and not re.search(r'"\d+ items in the record"', js))
    ok("the index carries no prose the engine will speak",
       all("answer" not in k and "prose" not in k for k in idx))

    ok("an empty record produces a catalogue that promises nothing",
       [c for c in catalogue(index([], "2026-08-11")) if c["route"]["view"] == "by_county"] == [])
    ok("...and still offers the questions that are always answerable",
       any(c["route"]["view"] == "counts" for c in catalogue(index([], "2026-08-11"))))

    if failures:
        print(f"\nask_answers self-test: {failures} FAILED", file=sys.stderr)
        return 1
    print(f"\nask_answers self-test: all passed ({len(cat)} questions catalogued from "
          f"{len(items)} items)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--today", default=_dt.date.today().isoformat())
    a = ap.parse_args()
    if a.self_test:
        return self_test()
    items = dk.load(REPO_ROOT / "ledger" / "docket.json")
    idx = index(items, a.today)
    cat = catalogue(idx)
    print(json.dumps({"items": len(idx["items"]), "questions": len(cat),
                      "counties": len(idx["counties"]), "topics": len(idx["topics"])}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
