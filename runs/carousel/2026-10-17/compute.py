"""Every figure the October 17th deck states or draws, extracted from a claim quote or computed here.

No figure in the deck is typed. Each value below is parsed out of the verified quote it cites in
claims.json, and figures.json is written from this file alone.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
claims = {c["id"]: c for c in json.loads((HERE / "claims.json").read_text())["claims"]}
WORDS = {"four": 4}


def quote(cid):
    return claims[cid]["quote"]


def grab(cid, pattern, group=1):
    m = re.search(pattern, quote(cid))
    if not m:
        raise SystemExit(f"{cid}: pattern {pattern!r} not in its quote")
    return m.group(group)


figures = {"_note": "Every value is extracted from a claim quote by compute.py, or computed here from values that were."}

datasets = int(grab("c4", r"across (\d+) datasets"))
low = WORDS[grab("c4", r"was (\w+)- to \d+-times")]
high = int(grab("c4", r"to (\d+)-times more effective"))
assert datasets == int(grab("c20", r"Applied to (\d+) SRT datasets")), "release and abstract disagree on datasets"
pub_day = int(grab("c17", r"Published: (\d+) October 2026"))
pub_year = int(grab("c17", r"October (\d{4})"))

figures["datasets"] = {"value": datasets, "from": ["c4"], "basis": "datasets SPACER was applied across, the release's count, the abstract's too (c20)"}
figures["benchmark_low"] = {"value": low, "from": ["c4"], "basis": "the low end of the benchmark range, four times more effective, the release's word parsed to a number"}
figures["benchmark_high"] = {"value": high, "from": ["c4"], "basis": "the high end of the benchmark range, 21 times more effective"}
figures["published_day"] = {"value": pub_day, "from": ["c17"], "basis": "day of October the journal published the article"}
figures["published_year"] = {"value": pub_year, "from": ["c17"], "basis": "year the journal published the article"}

types = re.search(r"Across several (.+?) datasets", quote("c8")).group(1)
cancer_types = [t.strip() for t in re.split(r" and |, ", types.replace(" cancer", "")) if t.strip()]
uses = re.search(r"including (.+?)\.$", quote("c9")).group(1)
named_uses = [u.strip() for u in re.split(r", and |, | and ", uses) if u.strip()]
funded = re.search(r"funded in part by (.+?)\.$", quote("c12")).group(1)
funders = [f.strip() for f in re.split(r", and |, ", funded) if f.strip()]
figures["cancer_types_mucin"] = {"value": len(cancer_types), "from": ["c8"], "basis": "cancer types the mucin association names: " + ", ".join(cancer_types)}
figures["named_uses"] = {"value": len(named_uses), "from": ["c9"], "basis": "settings beyond cancer the release names as possible uses: " + ", ".join(named_uses)}
figures["funders"] = {"value": len(funders), "from": ["c12"], "basis": "funders the release names: " + "; ".join(funders)}

(HERE / "figures.json").write_text(json.dumps(figures, indent=1) + "\n")
for k, v in figures.items():
    if k != "_note":
        print(f"{k:16} {v['value']}")
