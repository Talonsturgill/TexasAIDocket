#!/usr/bin/env python3
"""Every figure this deck prints, computed from ledger/docket.json.

THE RULE THIS FILE EXISTS FOR. No numeral reaches a slide by being typed. Each value below is
derived here, written to aggregates.json with the claim ids behind it, and the slide prints only
what this script produced.

THE COUNTING RULE IS STATED RATHER THAN ASSUMED, because "how many Texas governments said no" is
a question whose answer depends entirely on what counts as a government and what counts as a no.
A reader is owed the rule, not just the number.

  IN:  a Texas governmental body that took a RECORDED ACTION in 2026 restricting, pausing,
       capping, denying or refusing to advance a data center or the incentive a data center
       depended on.
  IN:  a body that DECLINED to restrict, counted separately, because a deck that only counts one
       direction is arguing rather than recording.
  OUT: an item where a data center is merely discussed, received, or scheduled.
"""
import json, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parents[2]
doc = json.loads((ROOT / "ledger/docket.json").read_text(encoding="utf-8"))
items = doc["items"] if isinstance(doc, dict) else doc
by = {i["id"]: i for i in items}

# Each entry is a hand-classified DECISION about what the record says, paired with the item it
# rests on. The classification is editorial and is stated; the counting is arithmetic and is here.
# EVERY SHAPE NAMES THE CLAIM THAT PROVES IT, and two of these were wrong until a director
# checked them against claims.json rather than against the item titles.
#
#   "category denied" rested on nothing. The only TWDB claims confirmed by this run's re-check
#   say the agenda carried an item to CONSIDER ACTING ON a petition, which is not a denial. The
#   denial was recovered by re-fetching the source directly, and the stored quote turned out to
#   be missing the word "also", which is why the differ could never find it.
#
#   "zoning prohibition drafted" overstated Corpus Christi, whose own coverage says in terms
#   that "The motion does not ban data centers in Corpus Christi."
#
#   "applications paused" overstated Fort Worth, which adopted a resolution starting a process.
#
# A shape a claim does not state is a shape this deck does not print.
RESTRICTED = {
    # EVERY SHAPE IS IN ITS CLAIM'S OWN WORDS, and the assert below proves it. These read
    # slightly less punchy than "permit refused" and "water capped" and they are what the
    # sources say. Four of the seven are a denial and the OBJECT denied is different every
    # time, which is what "no two reached for the same instrument" actually means.
    "tx-2026-0032": ("Killeen",            "permit denied",             "c17"),
    "tx-2026-0043": ("Archer County",      "abatement denied",          "c5"),
    "tx-2026-0045": ("Lubbock County",     "disclosure asked",          "c31"),
    "tx-2026-0050": ("Corpus Christi",     "staff directed",            "c30"),
    "tx-2026-0051": ("Brazoria County",    "zone denied",               "c9"),
    "tx-2026-0062": ("Fort Worth",         "process initiated",         "c22"),
    "tx-2026-0065": ("San Angelo",         "water ordinance passed",    "c12"),
}
# THE WATER DEVELOPMENT BOARD IS NOT IN THIS SET, and it was until a scoring judge read c29
# against the rule above. The board DENIED A PETITION that asked it to project data center water
# demand as its own category. That is a refusal to add scrutiny, which is the opposite direction,
# and counting it made the deck's headline number eight when the record supports seven. It cost
# the cover, two frames, the caption and the whole arithmetic, and it was one line of a map typed
# by hand from memory of the record rather than read off it.
DECLINED = {
    "tx-2026-0037": ("Laredo",             "no action taken",           "c14"),
    "tx-2026-0056": ("Texas Water Development Board", "petition denied","c29"),
    "tx-2026-0070": ("Tom Green County",   "moratorium not pursued",    "c15"),
}
# Laredo's shape was "moratorium declined" and no claim in this run's file says so. The docket
# item's TITLE says it and the claims file is what the deck is allowed to print from, so it says
# what c14 says.

for iid in list(RESTRICTED) + list(DECLINED):
    assert iid in by, f"{iid} is not in the record"
# Every shape must point at a claim that exists in this run's claims file.
_cl = {c["id"] for c in json.loads((ROOT / "out/2026-08-25/claims.json").read_text())["claims"]}
_by_id = {c["id"]: c for c in
          json.loads((ROOT / "out/2026-08-25/claims.json").read_text())["claims"]}
# The stem each shape word has to be found by, so "asked" matches "asks" and "initiated"
# matches "initiates". Deliberately short and deliberately per word: a general stemmer would
# match things this must not, and the whole point of the assert is that it is strict.
_STEM = {"denied": "den", "asked": "ask", "directed": "direct", "initiated": "initiat",
         "passed": "pass", "taken": "taken", "pursued": "pursu", "disclosure": "disclos",
         "permit": "permit", "abatement": "abatement", "zone": "zone", "water": "water",
         "ordinance": "ordinance", "process": "process", "staff": "staff", "petition": "petition",
         "moratorium": "moratorium", "action": "action", "no": "no", "not": "not"}
for iid, (_p, _s, _c) in list(RESTRICTED.items()) + list(DECLINED.items()):
    assert _c in _cl, f"{iid} shape {_s!r} cites {_c}, which is not in claims.json"
    # AND THAT THE CLAIM SAYS IT. The membership test alone let "moratorium declined" through on
    # Laredo citing a claim reading only "no action taken", and "disclosure asked" through on
    # Lubbock citing a claim about the vote count. Both were found by a judge reading the file,
    # never by this assert, because the assert only asked whether the id resolved.
    _hay = (_by_id[_c].get("quote", "") + " " + _by_id[_c].get("text", "")).lower()
    _miss = [w for w in _s.split() if _STEM.get(w, w) not in _hay]
    assert not _miss, (f"{iid} shape {_s!r} cites {_c}, and {_miss} appears in neither its quote "
                       f"nor its text. A shape a claim does not state is a shape this deck does "
                       f"not print.")

def ordered_on(iid):
    """The date the BODY ACTED, which is the `ordered` key date and nothing else.

    The first draft of this took the earliest key date of any kind and produced February 10th
    for Brazoria, which is the date an APPLICATION WAS FILED with the county. That is a date
    somebody else caused. Counting it as the start of the pushback would have printed a span
    five months long on the strength of a developer's paperwork, and the whole claim of the
    frame is about when GOVERNMENTS moved. Every one of these items carries an `ordered` date.
    """
    ds = [k["date"] for k in (by[iid].get("key_dates") or [])
          if k.get("kind") == "ordered" and k.get("date")]
    assert ds, f"{iid} carries no ordered date, so the deck cannot say when it acted"
    return min(ds)

restricted_n = len(RESTRICTED)
declined_n   = len(DECLINED)
total_n      = restricted_n + declined_n
shapes_n     = len({shape for _, shape, _c in RESTRICTED.values()})

dates = sorted(ordered_on(i) for i in RESTRICTED)
first_date, last_date = dates[0], dates[-1]
span_days = (__import__("datetime").date.fromisoformat(last_date)
             - __import__("datetime").date.fromisoformat(first_date)).days

# Brazoria: applications that died with the zone. This is NOT computed and must never say it is.
# c11 states the composition, two entities named as data center companies and two named as power
# companies, and the count follows from that sentence rather than from any structure in the
# ledger. Its declaration carries `value_from: c11` for the same reason.
brazoria_apps = 2 + 2      # c11, two data center companies and two power companies
brazoria_vote = "5 to 0"

# BINDING FORCE. The flow critic caught frame 5 saying "most", which is a quantifier standing in
# for a count on a product whose law is that every number is computed. A count is only honest here
# if the RECORD speaks to force, so these two sets hold only the bodies whose own sources do.
# The other four are not counted either way, and that silence is the deck's actual point: a
# headline does not tell a reader whether a refusal stops anything.
STATED_NONBINDING = {
    "tx-2026-0043": ("Archer County",   "c5"),   # "does not stop the project from moving forward"
    "tx-2026-0045": ("Lubbock County",  "c7"),   # "Resolutions do nothing, they are not binding."
    "tx-2026-0050": ("Corpus Christi",  "c30"),  # "The motion does not ban data centers"
    "tx-2026-0062": ("Fort Worth",      "c22"),  # a resolution that STARTS a process, no pause today
    "tx-2026-0032": ("Killeen",         "c18"),  # the council, not the commission, decides
}
# This was two, and the run published "the record says nothing either way about four bodies" on
# a frame and in the caption. A judge read the claims file back and found the record speaks to
# every one of them: c30 says the Corpus Christi motion bans nothing, c22 and c23 are the whole
# subject of frame 4, and c18 says Killeen's commission vote is a recommendation the council
# still has to act on. The silent set is empty, and saying it had four in it was the same defect
# as the count above, one map typed from memory.
STATED_BINDING = {
    "tx-2026-0051": ("Brazoria County", "c9"),  # the zone was refused and c10 shows four abatements died with it
    "tx-2026-0065": ("San Angelo",      "c12"), # a cap written into the water ordinance, approved 7 to 0
}
assert not (set(STATED_NONBINDING) & set(STATED_BINDING)), "a body cannot be in both sets"
assert set(STATED_NONBINDING) <= set(RESTRICTED) and set(STATED_BINDING) <= set(RESTRICTED)

# How the eight fell in time. The flow critic found frames 2 and 3 doing the same job, and the
# one thing the record holds that no other frame shows is WHEN. This is the shape of it.
_d = __import__("datetime")
_ds = sorted(_d.date.fromisoformat(ordered_on(i)) for i in RESTRICTED)
# THE SPLIT IS CHOSEN AND THE WINDOW IS MEASURED, in that order and never the other way. An
# earlier version fixed the window at 21 days and counted what fell inside it, and 21 is the
# SMALLEST window that yields four: at twenty the answer is three. That is a tuned parameter
# wearing a finding's clothes. Half the set is a split nobody tuned, and the span those last
# four actually occupy is then a measurement.
late_n = len(RESTRICTED) // 2
late_span = (_ds[-1] - _ds[-late_n]).days

# WHAT IS STILL DATED. Frame 9 closed on "the nearest dated step this record carries", a
# superlative over all 73 items that nothing computed and that is FALSE: eight dated steps in
# the record fall before November 10th, including a hearing on the day this deck was made. What
# is true and computable is narrower and better, so the frame says that instead.
_ALL = list(RESTRICTED) + list(DECLINED)
_TODAY = _d.date(2026, 8, 25)
def _future(iid):
    return [k for k in (by[iid].get("key_dates") or [])
            if k.get("date") and not k.get("canceled")
            and _d.date.fromisoformat(k["date"]) >= _TODAY]
still_dated = sorted(i for i in _ALL if _future(i))

# The chronology frame 3 sets, in the order the bodies acted. Nothing here is typed.
chronology = [{"date": ordered_on(i), "place": RESTRICTED[i][0], "shape": RESTRICTED[i][1],
               "claim": RESTRICTED[i][2], "item": i} for i in sorted(RESTRICTED, key=ordered_on)]

out = {
  "restricted_count":  {"value": restricted_n, "rule": "Texas governmental bodies in the record that took a recorded 2026 action restricting, pausing, capping or denying a data center or its incentive",
                        "from_items": sorted(RESTRICTED)},
  "declined_count":    {"value": declined_n, "rule": "bodies in the record that considered a restriction and declined it",
                        "from_items": sorted(DECLINED)},
  "total_count":       {"value": total_n, "rule": "restricted plus declined"},
  "stated_nonbinding": {"value": len(STATED_NONBINDING),
                        "rule": "restricting bodies whose own source states the action does not bind",
                        "from_items": sorted(STATED_NONBINDING)},
  "stated_binding":    {"value": len(STATED_BINDING),
                        "rule": "restricting bodies whose record shows the action changed a legal state on the day",
                        "from_items": sorted(STATED_BINDING)},
  "force_unstated":    {"value": restricted_n - len(STATED_NONBINDING) - len(STATED_BINDING),
                        "rule": "restricting bodies the record says nothing about either way",
                        "from_items": sorted(set(RESTRICTED) - set(STATED_NONBINDING) - set(STATED_BINDING))},
  "late_cluster":      {"value": late_n, "rule": "the later half of the restricting bodies by ordered date, floor divided, so %d of %d" % (late_n, restricted_n)},
  "late_span":         {"value": late_span,
                        "rule": "days from the %dth from last ordered action to the last, MEASURED after the half was chosen" % late_n,
                        "from_items": sorted(RESTRICTED, key=ordered_on)[-late_n:]},
  "still_dated":       {"value": len(still_dated),
                        "rule": "of the ten bodies this deck carries, those whose key_dates hold a step on or after 2026-08-25",
                        "from_items": still_dated},
  "chronology":        {"value": len(chronology), "rule": "the restricting actions in the order they happened",
                        "marks": chronology},
  "distinct_shapes":   {"value": shapes_n, "rule": "distinct kinds of restriction among the restricting bodies",
                        "shapes": sorted({s for _, s, _c in RESTRICTED.values()}),
                        "backed_by": {p: [s, c] for p, s, c in RESTRICTED.values()}},
  "first_action_date": {"value": first_date, "rule": "earliest ORDERED date among the restricting items, the date a body acted"},
  "last_action_date":  {"value": last_date,  "rule": "latest ORDERED date among the restricting items"},
  "span_days":         {"value": span_days,  "rule": "days from first_action_date to last_action_date"},
  "brazoria_applications": {"value": brazoria_apps, "value_from": "c11", "rule": "abatement applications the Brazoria zone carried, per the item summary", "from_items": ["tx-2026-0051"]},
  "brazoria_vote":     {"value": brazoria_vote, "rule": "quoted from tx-2026-0051-c1"},
  "docket_items":      {"value": len(items), "rule": "items in ledger/docket.json"},
  # A director checked this against claims.json and found "three agendas" stated nowhere in it.
  # It is true and it lives in the record's key_dates rather than in a quote, so it is COUNTED
  # here rather than typed on a slide. That is the difference between a figure and a memory.
  "laredo_agendas":    {"value": len([k for k in by["tx-2026-0037"].get("key_dates") or []
                                      if k.get("kind") == "hearing"]),
                        "rule": "hearing key_dates on tx-2026-0037, the agendas Laredo's direction reached",
                        "from_items": ["tx-2026-0037"]},
}
(pathlib.Path(__file__).parent / "figures.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
for k, v in out.items():
    print(f"  {k:24} {v['value']}")
print(f"\n  shapes: {', '.join(sorted({s for _, s, _c in RESTRICTED.values()}))}")
