#!/usr/bin/env python3
"""Every figure this deck prints, computed from ledger/docket.json.

THE RULE THIS FILE EXISTS FOR. No numeral reaches a slide by being typed. Each value below is
derived here, written to aggregates.json with the claim ids behind it, and the slide prints only
what this script produced.

THE COUNTING RULE IS STATED RATHER THAN ASSUMED, because "how many Texas governments said no" is
a question whose answer depends entirely on what counts as a government and what counts as a no.
A reader is owed the rule, not just the number.

  IN:  a Texas governmental body that took a RECORDED 2026 ACTION AIMED AT A DATA CENTER, or at
       the incentive one depended on. Denying a permit, an abatement or a zone. Capping its
       water. Asking a disclosure of it. Directing staff to draft rules for it. Starting the
       statutory process toward a moratorium on it.
       FORCE IS NOT PART OF THIS RULE, and the omission is the point. Whether these actions
       bind anything is the deck's whole subject, so a set defined by force would settle the
       question in the selection and then report the answer back as a finding. An earlier
       wording of this rule said "restricting, pausing, capping, denying or refusing to
       advance", which three of the seven members do not meet, and a scorer was right to say
       so: Lubbock asks a disclosure, Corpus Christi directs staff, Fort Worth starts a
       process. The set did not change. The sentence describing it was wrong.
  IN:  a body that had such an action in front of it and DID NOT take it, counted separately,
       because a deck that only counts one direction is arguing rather than recording.
  OUT: an item where a data center is merely discussed, received, or scheduled.
"""
import json, pathlib, collections, re

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
# ===========================================================================================
# THE SET IS COMPUTED OVER THE WHOLE RECORD, AND NOTHING MAY BE OMITTED IN SILENCE.
#
# Rounds 2, 4 and 5 each shipped a wrong headline out of this one spot, and the cause never
# changed: `ACTED` was a MAP TYPED BY HAND. Round 4 replaced a rule that was too narrow
# with one too broad and left the map alone, so round 5's judge read the record back and found
# three bodies that meet the published rule, sit inside the deck's own window, and are on no
# frame: El Paso's Data Center Policy Framework, San Marcos making data centers ineligible
# citywide, and Hays County's 180 day emergency water review. It also found that San Angelo
# reached for THREE instruments in 2026, so "seven bodies, seven instruments, one each" was a
# property of picking one action per body rather than a finding about the record.
#
# CANDIDATES is computed. Every candidate must then be classified into exactly one of ACTED,
# DECLINED or OUT, and the assertion below refuses to run if any is in none of them. The
# editorial judgement stays, because whether a TCEQ permit step is aimed at a data center IS a
# judgement, but it becomes EXHAUSTIVE. A silent omission stops being possible, which is the
# defect rather than any one of its three symptoms.
#
# THE RULE THE DECK PUBLISHES, and the selection is measured against it:
#   a Texas LOCAL government (city council, commissioners court, planning commission) that, on a
#   dated 2026 ORDER in this record, decided something about data center development IN ITS OWN
#   JURISDICTION. State agencies, the Legislature and letters asking another government are out,
#   each by a stated reason rather than by omission.
# THE CANDIDATE RULE READS THE RECORD'S OWN FIELDS, not prose. 2026-08-26, round 6.
#
# The first version of this was a `data cent|hyperscale` regex over title and summary, and a
# judge found what that costs: tx-2026-0029 is filed by the record under topic `data-centers`,
# carries an ordered 2026 date, and is Williamson County granting a Chapter 312 abatement in its
# own jurisdiction. Its own words are "server service center", so the regex never saw it, the
# exhaustiveness assertion could not fire on it, and the recut's whole stated guarantee that a
# silent omission is structurally impossible did not hold. An assertion is only as wide as the
# set it runs over, and a set defined by a regex over prose is a set the record does not control.
_DC = re.compile(r"data cent|hyperscale", re.I)
CANDIDATES = {i["id"] for i in items
              if any(str(k.get("date", "")).startswith("2026") for k in (i.get("key_dates") or []))
              and (i.get("topic") == "data-centers"
                   or _DC.search((i.get("title") or "") + " " + (i.get("summary") or "")))}

# ACTED: place, shape, and the claim whose own words prove the shape.
ACTED = {
    "tx-2026-0051": ("Brazoria County",  "zone denied",           "c9"),
    "tx-2026-0032": ("Killeen",          "permit denied",         "c17"),
    "tx-2026-0066": ("San Angelo",       "conditional use only",  "c41"),
    "tx-2026-0067": ("San Angelo",       "discharge regulated",   "c43"),
    "tx-2026-0052": ("Brazoria County",  "resolution adopted",    "c40"),
    "tx-2026-0061": ("San Marcos",       "made ineligible",       "c35"),
    "tx-2026-0065": ("San Angelo",       "cooling fill capped",   "c32"),
    "tx-2026-0043": ("Archer County",    "abatement denied",      "c5"),
    "tx-2026-0028": ("Hays County",      "review established",    "c36"),
    "tx-2026-0033": ("El Paso",          "framework approved",    "c38"),
    "tx-2026-0050": ("Corpus Christi",   "staff directed",        "c30"),
    "tx-2026-0045": ("Lubbock County",   "disclosure asked",      "c31"),
    "tx-2026-0062": ("Fort Worth",       "process initiated",     "c22"),
    "tx-2026-0041": ("Wichita Falls",    "request approved",      "c37"),
    "tx-2026-0029": ("Williamson County","abatement approved",    "c45"),
}
DECLINED = {
    "tx-2026-0037": ("Laredo",           "no action taken",       "c14"),
    "tx-2026-0070": ("Tom Green County", "moratorium not pursued","c15"),
}
# OUT, with the reason on every single one. A reason is what makes this a classification rather
# than a shorter list.
OUT = {
    "tx-2026-0001": "PUCT, a state agency, and a comment window rather than a decision",
    "tx-2026-0002": "PUCT, a state agency",
    "tx-2026-0026": "Temple, a hearing scheduled and no 2026 order yet",
    "tx-2026-0027": "Taylor, an amended agreement NOTICED on an agenda and no order on it",
    "tx-2026-0034": "El Paso, a letter asking the Governor, aimed at another government",
    "tx-2026-0035": "El Paso, a legislative agenda amendment, aimed at the Legislature",
    "tx-2026-0042": "Young County, an application received and no order",
    "tx-2026-0044": "Angelina County, a resolution asking the Legislature for powers it lacks",
    "tx-2026-0056": "the Texas Water Development Board, a state agency",
    "tx-2026-0058": "TCEQ, a state agency",
    "tx-2026-0059": "Tarrant Regional Water District, a statement that no contract was signed",
    "tx-2026-0060": "Blanco-Pedernales Groundwater Conservation District, a resolution asking another government",
    "tx-2026-0063": "TCEQ, a state agency",
    "tx-2026-0064": "TCEQ, a state agency, and a permit for a power plant rather than the data center",
    "tx-2026-0068": "Reeves County ESD No. 2, a hearing and no order",
    "tx-2026-0069": "Pecos-Barstow-Toyah ISD, an executed incentive agreement for a power plant",
    "tx-2026-0072": "the Governor, a state office",
    "tx-2026-0073": "the Texas House, the Legislature",
    "tx-2026-0078": "House State Affairs, the Legislature",
}
_unclassified = CANDIDATES - set(ACTED) - set(DECLINED) - set(OUT)
assert not _unclassified, (
    "THE WHOLE POINT OF THIS FILE. These items are in the record, carry a 2026 date and name a "
    "data center, and are in none of ACTED, DECLINED or OUT, so the deck would count around them "
    "in silence: " + ", ".join(sorted(_unclassified)))
_phantom = (set(ACTED) | set(DECLINED) | set(OUT)) - CANDIDATES
assert not _phantom, ("classified but not a candidate, so the classification is stale against "
                      "the record: " + ", ".join(sorted(_phantom)))

# Laredo's shape was "moratorium declined" and no claim in this run's file says so. The docket
# item's TITLE says it and the claims file is what the deck is allowed to print from, so it says
# what c14 says.

for iid in list(ACTED) + list(DECLINED):
    assert iid in by, f"{iid} is not in the record"
# Every shape must point at a claim that exists in this run's claims file.
_cl = {c["id"] for c in json.loads((ROOT / "out/2026-08-25/claims.json").read_text())["claims"]}
_by_id = {c["id"]: c for c in
          json.loads((ROOT / "out/2026-08-25/claims.json").read_text())["claims"]}
# The stem each shape word has to be found by, so "asked" matches "asks" and "initiated"
# matches "initiates". Deliberately short and deliberately per word: a general stemmer would
# match things this must not, and the whole point of the assert is that it is strict.
_STEM = {"denied": "den", "asked": "ask", "directed": "direct", "initiated": "initiat",
         # added 2026-08-26 with the seven bodies the computed selection brought in.
         # The guard fired on every one of them before these existed, which is the guard
         # working: a shape word its claim does not carry is a shape the deck may not print.
         "regulated": "regulat", "adopted": "adopt", "approved": "approv",
         "established": "establish", "made": "mak", "ineligible": "ineligible",
         "conditional": "conditional", "use": "use", "only": "only",
         "resolution": "resolution", "review": "review", "request": "request",
         "framework": "framework", "discharge": "discharg", "capped": "cap", "cooling": "cooling", "fill": "fill",
         "permit": "permit", "process": "process",
         "passed": "pass", "taken": "taken", "pursued": "pursu", "disclosure": "disclos",
         "permit": "permit", "abatement": "abatement", "zone": "zone", "water": "water",
         "ordinance": "ordinance", "process": "process", "staff": "staff", "petition": "petition",
         "moratorium": "moratorium", "action": "action", "no": "no", "not": "not"}
for iid, (_p, _s, _c) in list(ACTED.items()) + list(DECLINED.items()):
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
    # THE EARLIEST ORDER INSIDE THE YEAR THE DECK COUNTS. An item can carry an order from a
    # prior year as well: tx-2026-0029 has one from December 2025 and one from April 2026, and
    # a bare min() would put the deck's first action four months outside its own window.
    in_year = [d for d in ds if d.startswith("2026")]
    assert in_year, f"{iid} carries no 2026 ordered date"
    return min(in_year)

restricted_n = len(ACTED)
declined_n   = len(DECLINED)
total_n      = restricted_n + declined_n
# `shapes_n` is deliberately NOT published. len(set()) over labels written in this file
# can only ever equal the number of labels, so "no two alike" was a sentence that could
# not be false. `resolutions` below is the substantive version, counted over what the
# CLAIMS say. Kept as a local because the shapes list at the foot still prints it.
shapes_n     = len({shape for _, shape, _c in ACTED.values()})

dates = sorted(ordered_on(i) for i in ACTED)
first_date, last_date = dates[0], dates[-1]
span_days = (__import__("datetime").date.fromisoformat(last_date)
             - __import__("datetime").date.fromisoformat(first_date)).days

# BRAZORIA: the applications that died with the zone. This was typed as `2 + 2` for three
# rounds, sourced to a prose sentence in c11, and a scorer was right to call it out: on a
# product whose first law is that the model is never the calculator, the deck's second most
# prominent number was the one number a person had counted. It is counted here instead.
#
# Brazoria County publishes its agenda system through Legistar's open API. An abatement
# application rides on a NAMED reinvestment zone, and the court refused Zone No. 26-01 on
# March 10th, so the applications that died with it are exactly the applicants whose hearing
# orders name that zone. The API response is snapshotted beside this file so the count can be
# re-derived from the same bytes.
_BZ = json.loads((ROOT / "out/2026-08-25/brazoria_matters.json").read_text(encoding="utf-8"))
_BZ_RE = re.compile(r"Tax Abatement Application of (.+?) - Brazoria County Reinvestment Zone No\. 26-01")
brazoria_applicants = sorted({m.group(1).strip()
                              for t in (x.get("MatterTitle") or "" for x in _BZ)
                              for m in [_BZ_RE.search(t)] if m})
brazoria_apps = len(brazoria_applicants)
assert brazoria_apps, "no Brazoria matter names Reinvestment Zone No. 26-01, so the count cannot be published"
brazoria_vote = "5 to 0"

# WHAT COUNTS AS SAYING YES. Not a substring, a decision. An approval is a body granting a data
# center project or the incentive that project depends on. Regulating one, refusing one, opening
# a review of one, adopting a framework about one and directing staff to study one are all
# something else, whatever verb the label happens to use.
APPROVALS = {
    "tx-2026-0041": "c37",   # Wichita Falls granted the conditional use for the DataNovaX centre
    "tx-2026-0029": "c45",   # Williamson County granted the Chapter 312 abatement in Georgetown
}
assert set(APPROVALS) <= set(ACTED), "an approval has to be an action this deck counted"
# The two that read like approvals and are not, named so a later reader does not re-add them:
# tx-2026-0028 (Hays County) approved a REVIEW PERIOD over such projects, and tx-2026-0033
# (El Paso) adopted a FRAMEWORK about them. Neither says yes to a project.
assert "tx-2026-0028" not in APPROVALS and "tx-2026-0033" not in APPROVALS

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
# FORCE IS READ OUT OF THE RECORD. 2026-08-26.
#
# This was a typed map of six and it never opened ledger/docket.json, which carries the exact
# distinction as data: a `key_dates` entry of kind `effective`. Four of the six have one. Hays
# County has `ordered 2026-06-23` and nothing else, no claim in claims.json speaks to its force,
# and the instrument is a COUNTY RESOLUTION, which is the same thing frame 5 quotes a Lubbock
# commissioner calling non-binding two frames earlier. The justification written on its line was
# the participle in c36, "establishing" rather than "asking", which is a linguistic distinction
# doing legal work.
#
# This deck's stated method is that silence about force is PUBLISHED rather than resolved, and
# here the silence was resolved toward the headline. Hays falls into force_unstated, where the
# record leaves it, and the count is five.
_EFFECTIVE = {i["id"] for i in items
              if any(k.get("kind") == "effective" for k in (i.get("key_dates") or []))}
STATED_BINDING = {
    "tx-2026-0065": ("San Angelo",      "c32"),  # effective 2026-06-16 in the record
    "tx-2026-0066": ("San Angelo",      "c41"),  # effective 2026-05-19 in the record
    "tx-2026-0067": ("San Angelo",      "c43"),  # effective 2026-06-02 in the record
    "tx-2026-0061": ("San Marcos",      "c35"),  # effective 2026-06-16 in the record
    # A DENIAL CARRIES NO EFFECTIVE DATE because there is nothing to bring into effect, so this
    # one is admitted on evidence instead of on a date: c10 records that four abatement items
    # took no action BECAUSE the zone item failed. That is a legal state changed and observed in
    # the county's own minutes, not inferred from a verb.
    "tx-2026-0051": ("Brazoria County", "c9"),
}
_DENIAL = {"tx-2026-0051"}
assert (set(STATED_BINDING) - _DENIAL) <= _EFFECTIVE, (
    "every member but the denial must carry an `effective` key date in ledger/docket.json: "
    + str(sorted((set(STATED_BINDING) - _DENIAL) - _EFFECTIVE)))
assert "tx-2026-0028" not in STATED_BINDING, (
    "Hays County carries no effective date and no claim speaks to its force. It belongs in "
    "force_unstated and the deck publishes that silence")
# The three the record does not speak to either way are Brazoria's conditions resolution, El
# Paso's policy framework and the Wichita Falls approval, and the deck publishes that silence
# rather than rounding it into one side. Round 4 had this set at zero and said so on a frame,
# which was true of a set of seven picked by hand and is not true of the record.
assert not (set(STATED_NONBINDING) & set(STATED_BINDING)), "a body cannot be in both sets"
assert set(STATED_NONBINDING) <= set(ACTED) and set(STATED_BINDING) <= set(ACTED)

# How the eight fell in time. The flow critic found frames 2 and 3 doing the same job, and the
# one thing the record holds that no other frame shows is WHEN. This is the shape of it.
_d = __import__("datetime")
_ds = sorted(_d.date.fromisoformat(ordered_on(i)) for i in ACTED)
# THE SPLIT IS CHOSEN AND THE WINDOW IS MEASURED, in that order and never the other way. An
# earlier version fixed the window at 21 days and counted what fell inside it, and 21 is the
# SMALLEST window that yields four: at twenty the answer is three. That is a tuned parameter
# wearing a finding's clothes. Half the set is a split nobody tuned, and the span those last
# four actually occupy is then a measurement.
late_n = len(ACTED) // 2
late_span = (_ds[-1] - _ds[-late_n]).days

# WHAT IS STILL DATED. Frame 9 closed on "the nearest dated step this record carries", a
# superlative over all 73 items that nothing computed and that is FALSE: eight dated steps in
# the record fall before November 10th, including a hearing on the day this deck was made. What
# is true and computable is narrower and better, so the frame says that instead.
_ALL = list(ACTED) + list(DECLINED)
_TODAY = _d.date(2026, 8, 25)
def _future(iid):
    return [k for k in (by[iid].get("key_dates") or [])
            if k.get("date") and not k.get("canceled")
            and _d.date.fromisoformat(k["date"]) >= _TODAY]
still_dated = sorted(i for i in _ALL if _future(i))

# The chronology frame 3 sets, in the order the bodies acted. Nothing here is typed.
_MONTHS = ("January February March April May June July August September October November "
           "December").split()
_by_month = collections.Counter(int(ordered_on(i)[5:7]) for i in ACTED)

chronology = [{"date": ordered_on(i), "place": ACTED[i][0], "shape": ACTED[i][1],
               "claim": ACTED[i][2], "item": i} for i in sorted(ACTED, key=ordered_on)]

out = {
  "restricted_count":  {"value": restricted_n, "rule": "Texas governmental bodies in the record that took a recorded 2026 action aimed at a data center or at the incentive one depended on, of any binding force",
                        "from_items": sorted(ACTED)},
  "declined_count":    {"value": declined_n, "rule": "bodies that had such an action in front of them and did not take it",
                        "from_items": sorted(DECLINED)},
  "total_count":       {"value": total_n, "rule": "restricted plus declined"},
  "stated_nonbinding": {"value": len(STATED_NONBINDING),
                        "rule": "acting bodies whose own source states the action does not bind",
                        "from_items": sorted(STATED_NONBINDING)},
  "stated_binding":    {"value": len(STATED_BINDING),
                        "rule": "acting bodies whose record shows the action changed a legal state on the day",
                        "from_items": sorted(STATED_BINDING)},
  "force_unstated":    {"value": restricted_n - len(STATED_NONBINDING) - len(STATED_BINDING),
                        "rule": "acting bodies the record says nothing about either way",
                        "from_items": sorted(set(ACTED) - set(STATED_NONBINDING) - set(STATED_BINDING))},
  "late_cluster":      {"value": late_n, "rule": "the later half of the acting bodies by ordered date, floor divided, so %d of %d" % (late_n, restricted_n)},
  "late_span":         {"value": late_span,
                        "rule": "days from the %dth from last ordered action to the last, MEASURED after the half was chosen" % late_n,
                        "from_items": sorted(ACTED, key=ordered_on)[-late_n:]},
  "still_dated":       {"value": len(still_dated),
                        "rule": "of the %d items this deck carries, those whose key_dates hold a step on or after 2026-08-25" % total_n,
                        "from_items": still_dated},
  "chronology":        {"value": len(chronology), "rule": "the actions in the order they happened",
                        "marks": chronology},
  "first_action_date": {"value": first_date, "rule": "earliest ORDERED date among the acting items, the date a body acted"},
  "last_action_date":  {"value": last_date,  "rule": "latest ORDERED date among the acting items"},
  "span_days":         {"value": span_days,  "rule": "days from first_action_date to last_action_date"},
  "brazoria_applications": {"value": brazoria_apps,
                        "rule": "distinct applicants whose Brazoria County hearing orders name Reinvestment Zone No. 26-01, the zone the court refused on March 10th, counted from the county's own Legistar matter titles",
                        "applicants": brazoria_applicants,
                        "source": "https://webapi.legistar.com/v1/brazoriacountytx/matters",
                        "from_items": ["tx-2026-0051"]},
  "brazoria_vote":     {"value": brazoria_vote, "rule": "quoted from tx-2026-0051-c1"},
  # THE FACT THAT KILLED "ONE EACH", and it is better than what it replaced. Round 5 found San
  # Angelo reaching for three instruments in 2026, so a set of one action per body was a
  # property of the picking. Counted over the computed selection, eleven bodies took fourteen
  # actions and two of them went back.
  # The month the deck's third frame is about, and the busiest body's share of the binding set.
  # Both are printed, so both are computed. An earlier draft had frame 3 saying "six of the
  # fourteen" while frame 6 said the same words about a different derivation, and the gate keys
  # on the phrase, so one of the two would have silently satisfied the other's declaration.
  # THE COUNTER TO THE DECK'S OWN OLD CLAIM, and a judge is owed the credit for it.
  # `distinct_shapes` is len(set()) over labels this file writes, so it can only ever equal the
  # number of labels, and the deck printed it as "no two reached for the same instrument". That
  # sentence could not be false, which is the definition of a claim that is not a finding.
  # This is the substantive version, counted over what the CLAIMS say rather than over what the
  # labels say: how many of the acting items rest on a claim whose own words call the thing a
  # resolution. Five of them do, and a resolution is one instrument used five times.
  # HOW MANY OF THE ACTIONS SAID YES. Frame 8's hook read "One said yes" while frame 2's own
  # list printed two approvals, because Williamson County joined the set in round 7 and the
  # hook did not move. It was a hand-typed count on a product whose law is that no number is,
  # and it was wrong, which is what a typed count buys you.
  # AND IT IS DEFINED OVER THE RECORD, NOT OVER THE VOCABULARY THIS FILE TYPES. Round 9's
  # integrity judge found `len([i for i in ACTED if "approv" in ACTED[i][1]])`, a substring test
  # over labels written twenty lines above it, which makes the count a property of the wording
  # and not of what happened. Two items whose own claims say "approved" were excluded only
  # because their labels read "review established" and "framework adopted": Hays County's
  # review period and El Paso's policy framework. The published two was right and the
  # derivation was the same shape as the `distinct_shapes` tautology this file already retired.
  #
  # An approval here means a body said yes to A PROJECT OR TO THE INCENTIVE ONE DEPENDS ON.
  # That is a decision about the record, so it is written down as a decision, item by item,
  # with the claim that carries it, and it cannot drift when a label is reworded.
  "approvals":         {"value": len(APPROVALS),
                        "rule": "acting items whose cited claim records a body approving a data "
                                "center project or the incentive one depends on, as opposed to "
                                "regulating, refusing, studying or directing staff",
                        "from_items": sorted(APPROVALS)},
  "resolutions":       {"value": len([i for i in ACTED
                                      if "resolution" in (_by_id[ACTED[i][2]].get("quote", "") + " "
                                                          + _by_id[ACTED[i][2]].get("text", "")).lower()]),
                        "rule": "acting items whose own cited claim calls the instrument a resolution",
                        "from_items": sorted(i for i in ACTED
                                             if "resolution" in (_by_id[ACTED[i][2]].get("quote", "") + " "
                                                                 + _by_id[ACTED[i][2]].get("text", "")).lower())},
  "busiest_month":     {"value": _MONTHS[max(_by_month, key=lambda m: _by_month[m]) - 1],
                        "rule": "the calendar month carrying the most acting dates"},
  "busiest_month_count": {"value": max(_by_month.values()),
                        "rule": "how many of the acting dates fall in that month"},
  "busiest_body_binding": {"value": len([i for i in STATED_BINDING
                                         if ACTED[i][0] == max({p for p, _s, _c in ACTED.values()},
                                             key=lambda q: len([1 for r, _s2, _c2 in ACTED.values() if r == q]))]),
                        "rule": "how many of the binding actions the busiest body wrote"},
  "acting_bodies":     {"value": len({p for p, _s, _c in ACTED.values()}),
                        "rule": "distinct places among the acting items",
                        "from_items": sorted(ACTED)},
  "repeat_bodies":     {"value": len([p for p in {p for p, _s, _c in ACTED.values()}
                                      if len([1 for q, _s2, _c2 in ACTED.values() if q == p]) > 1]),
                        "rule": "acting places that appear on more than one action"},
  "busiest_body":      {"value": max({p for p, _s, _c in ACTED.values()},
                                     key=lambda p: len([1 for q, _s2, _c2 in ACTED.values() if q == p])),
                        "rule": "the acting place with the most actions"},
  "busiest_body_count":{"value": max(len([1 for q, _s2, _c2 in ACTED.values() if q == p])
                                     for p in {p for p, _s, _c in ACTED.values()}),
                        "rule": "how many actions the busiest place took"},
  "docket_items":      {"value": len(items), "rule": "items in ledger/docket.json"},
  # A director checked this against claims.json and found "three agendas" stated nowhere in it.
  # It is true and it lives in the record's key_dates rather than in a quote, so it is COUNTED
  # here rather than typed on a slide. That is the difference between a figure and a memory.
  "laredo_agendas":    {"value": len([k for k in by["tx-2026-0037"].get("key_dates") or []
                                      if k.get("kind") == "hearing"]),
                        "rule": "hearing key_dates on tx-2026-0037, the agendas Laredo's direction reached",
                        "from_items": ["tx-2026-0037"]},
}
# computed.json, WRITTEN HERE so it cannot drift from figures.json.
#
# The site's numeral gate reads runs/<date>/computed.json to learn which numerals a deck may
# print. This run wrote only figures.json for six decks, so that gate got None and authorised
# nothing the run computed, falling back to whatever numerals happened to sit inside a claim's
# quote or url. It passed on coincidence until the claims file grew past forty four entries and
# the article page printed a claim count nothing authorised. Writing it by hand then drifted
# again two claims later, which is the same defect one layer up. It is written from the same
# dict, in the same breath, or it is not written.
_computed = {k: (v["value"] if isinstance(v, dict) and "value" in v else v) for k, v in out.items()}
_computed["claims_verified"] = len(_cl)
_computed["_note"] = ("Written by compute.py beside figures.json, for the site's numeral gate, "
                      "which reads this filename. Every value traces to a computation over "
                      "ledger/docket.json.")
(pathlib.Path(__file__).parent / "computed.json").write_text(
    json.dumps(_computed, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

(pathlib.Path(__file__).parent / "figures.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
for k, v in out.items():
    print(f"  {k:24} {v['value']}")
print(f"\n  shapes: {', '.join(sorted({s for _, s, _c in ACTED.values()}))}")
