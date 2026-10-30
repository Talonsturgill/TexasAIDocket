"""Every figure the October 30th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}


def grab(cid, pattern, group=1):
    m = re.search(pattern, claims[cid]["quote"])
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    return int(m.group(group).replace(",", ""))


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}
F = lambda k, v, src, basis: figures.__setitem__(k, {"value": v, "from": src, "basis": basis})

chat = grab("c1", r"in the amount of \$([\d,]+)")
F("chatgpt_usd", chat, ["c1"], "ChatGPT Enterprise from Carahsoft, dollars, per the agenda item")
darwin = grab("c2", r"in the amount of \$([\d,]+)")
F("darwin_usd", darwin, ["c2"], "the Darwin AI governance platform from Carahsoft, dollars, per the agenda item")
ms = grab("c3", r"in the amount of \$([\d,]+)")
F("microsoft_usd", ms, ["c3"], "Microsoft Enterprise from SHI Government Solutions, dollars, per the agenda item")
reserve = grab("c4", r"an additional \$([\d,]+)")
F("reserve_usd", reserve, ["c4"], "the amount held for approved growth, dollars, per the agenda item")
ceiling = grab("c4", r"not-to-exceed amount of \$([\d,]+)")
F("ceiling_usd", ceiling, ["c4"], "the not to exceed total, dollars, per the agenda item")
if chat + darwin + ms + reserve != ceiling:
    raise SystemExit("the four lines no longer sum to the ceiling")
pop = int(claims["c15"]["quote"].split(",")[-1])
F("population_2024", pop, ["c15"], "the Census Bureau's 2024 population estimate for the city of Plano")

# THE TURN, computed. Rounding rules are stated in each basis.
F("darwin_cents_per_chat_dollar", round(100 * darwin / chat), ["c1", "c2"],
  "computed: Darwin AI's dollars over ChatGPT Enterprise's dollars, in whole cents per dollar")
F("darwin_pct_of_ceiling", round(100 * darwin / ceiling), ["c2", "c4"], "computed: Darwin AI's share of the ceiling, whole percent")
F("chatgpt_pct_of_ceiling", round(100 * chat / ceiling), ["c1", "c4"], "computed: ChatGPT Enterprise's share of the ceiling, whole percent")
F("microsoft_pct_of_ceiling", round(100 * ms / ceiling), ["c3", "c4"], "computed: Microsoft's share of the ceiling, whole percent")
F("reserve_pct_of_ceiling", round(100 * reserve / ceiling), ["c4"], "computed: the reserve's share of the ceiling, whole percent")
F("chat_plus_darwin_usd", chat + darwin, ["c1", "c2"], "computed: ChatGPT Enterprise plus Darwin AI, dollars")
F("chat_minus_darwin_usd", chat - darwin, ["c1", "c2"], "computed: how many dollars more the chatbot line is than the governance line")
F("ceiling_cents_per_resident", round(100 * ceiling / pop), ["c4", "c15"], "computed: the ceiling over the 2024 population estimate, whole cents")
F("darwin_cents_per_resident", round(100 * darwin / pop), ["c2", "c15"], "computed: Darwin AI's dollars over the 2024 population estimate, whole cents")
F("chatgpt_cents_per_resident", round(100 * chat / pop), ["c1", "c15"], "computed: ChatGPT Enterprise's dollars over the 2024 population estimate, whole cents")
F("ceiling_usd_per_resident", round(ceiling / pop, 2), ["c4", "c15"], "computed: the ceiling over the 2024 population estimate, dollars to two decimals")
F("lines_on_item", 4, ["c1", "c2", "c3", "c4"], "counted: the four money lines the agenda item names")

# THE DRAWING UNIT. One slotted weight stands for UNIT dollars, the greatest common divisor of the four lines, which is
# the Microsoft line itself (c3). Every count the deck draws is a line over this unit, so every weight is a whole one.
from math import gcd
UNIT = gcd(gcd(chat, darwin), gcd(ms, reserve))
if UNIT != ms:
    raise SystemExit("the drawing unit is no longer the Microsoft line")
F("unit_usd", UNIT, ["c1", "c2", "c3", "c4"], "computed: the greatest common divisor of the four lines, dollars per drawn weight, equal to the Microsoft line")
F("chatgpt_units", chat // UNIT, ["c1", "c3"], "computed: ChatGPT Enterprise in weights of unit_usd")
F("darwin_units", darwin // UNIT, ["c2", "c3"], "computed: Darwin AI in weights of unit_usd")
F("microsoft_units", ms // UNIT, ["c3"], "computed: Microsoft in weights of unit_usd")
F("reserve_units", reserve // UNIT, ["c3", "c4"], "computed: the reserve in weights of unit_usd")
F("ceiling_units", ceiling // UNIT, ["c3", "c4"], "computed: the ceiling in weights of unit_usd")
F("chat_minus_darwin_units", (chat - darwin) // UNIT, ["c1", "c2", "c3"], "computed: the chatbot line less the watcher line, in weights")
if (chat - darwin) != reserve:
    raise SystemExit("the difference no longer equals the reserve")

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
print(json.dumps({k: v["value"] for k, v in figures.items() if k != "_note"}, indent=1))
