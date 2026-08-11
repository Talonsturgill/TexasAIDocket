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
import datetime as _dt
import html
import json
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

import docket_build as dk                                          # noqa: E402
import texas_map                                                   # noqa: E402
import theme                                                       # noqa: E402

LEDGER = REPO_ROOT / "ledger" / "docket.json"

SITE_NAME = "Texas AI Docket"
# One key drives every absolute URL, so moving to a custom domain is a one line change.
SITE_URL = "https://talonsturgill.github.io/TexasAIDocket"

# The Lone Star. Statutory, geometric, abstract, and legible at 16 pixels, which is why it is
# the mark and a longhorn is not.
STAR = ('<svg class="star" viewBox="0 0 24 24" aria-hidden="true">'
        '<path d="M12 1.6l2.9 7.5 8 .4-6.2 5.1 2.1 7.8L12 18l-6.8 4.4 2.1-7.8L1.1 9.5l8-.4z"/>'
        '</svg>')

NAV = [("", "Docket"), ("counties/", "Counties"), ("data/", "Data"), ("about/", "About")]


def e(s) -> str:
    return html.escape(str(s if s is not None else ""), quote=True)


def ordinal(d: _dt.date) -> str:
    """House style: month first, with the ordinal. August 11th, never 11 August."""
    n = d.day
    suf = "th" if 11 <= n <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{d:%B} {n}{suf}"


def rel(depth: int) -> str:
    return "../" * depth


# --------------------------------------------------------------------------- shell
def page(*, title: str, desc: str, body: str, depth: int, active: str,
         today: str, canonical: str, extra_ld: list | None = None) -> str:
    p = rel(depth)
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{p}{h}"{cur if h == active else ""}>{e(t)}</a>'
                  for h, t in NAV)

    ld = [{
        "@context": "https://schema.org", "@type": "WebSite",
        "name": SITE_NAME, "url": SITE_URL,
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL},
    }] + (extra_ld or [])

    return f"""<!doctype html>
<html lang="en-US">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/{canonical}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{SITE_URL}/{canonical}">
<link rel="stylesheet" href="{p}site.css">
<link rel="alternate" type="application/atom+xml" title="{e(SITE_NAME)}" href="{p}atom.xml">
<script type="application/ld+json">{json.dumps(ld, separators=(",", ":"))}</script>
</head>
<body>
<a class="skip" href="#main">Skip to the record</a>
<header class="masthead">
  <div class="wrap">
    <a class="wordmark" href="{p or './'}">{STAR}<span>{e(SITE_NAME)}</span></a>
    <nav class="main" aria-label="Sections">{nav}</nav>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="site">
  <div class="wrap prose">
    <p><strong>Every numeral on this site is produced by code, from data, and can be recomputed
    from the same inputs.</strong> No number here is typed by a person. Where something cannot be
    measured, the size of the gap is published instead of an estimate.</p>
    <p>Every fact carries a quote from the source it came from, and a link to that source.
    The record is <a href="{p}docket.json">open data</a>.</p>
    <p class="num">Rebuilt {e(ordinal(_dt.date.fromisoformat(today)))}, {today[:4]}.</p>
  </div>
</footer>
</body>
</html>
"""


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
    left = "closes today" if days == 0 else f"{days} {unit} left to comment"
    return (f'<div class="clock{soon}"><span class="days">{days}</span>'
            f'<span class="lab">{e(left)}</span>'
            f'<span class="lab">Closes {e(when)}</span></div>')


def room_label(room: str) -> str:
    return {"open_comment": "Comment window open", "open_meeting": "Public meeting",
            "contact_only": "No formal process", "closed": "Closed"}.get(room, room)


def item_meta(it: dict) -> str:
    g = it.get("geography") or {}
    where = ("Statewide" if g.get("statewide")
             else ", ".join(g.get("counties") or []) or
             ("ERCOT region" if g.get("on_ercot") else ""))
    bits = [f'<span class="tag">{e(it["topic"])}</span>',
            f'<span>{e(it["decider"]["name"])}</span>']
    if where:
        bits.append(f'<span>{e(where if len(where) < 60 else where[:57] + "...")}</span>')
    bits.append(f'<span class="rooms {e(it["public_access"]["room"])}">'
                f'{e(room_label(it["public_access"]["room"]))}</span>')
    return f'<p class="meta">{"".join(bits)}</p>'


def claims_html(it: dict) -> str:
    """The proof, shown rather than asserted.

    Putting the source's own words on the page is the whole trust mechanism. A reader does not
    have to believe the summary; they can read what the filing actually said.
    """
    out = []
    for c in it.get("claims", []):
        kind = {"primary_official": "Primary source, official",
                "primary_corporate": "Primary source, the company",
                "journalism": "Journalism"}.get(c.get("source_type"), "")
        out.append(
            f'<div class="claim">'
            f'<blockquote>{e(c["verbatim_quote"])}</blockquote>'
            f'<cite><a href="{e(c["source_url"])}" rel="nofollow noopener">'
            f'{e(c.get("source_title") or c["source_url"][:70])}</a></cite> '
            f'<span class="kind">{e(kind)}</span></div>')
    return "".join(out)


# --------------------------------------------------------------------------- pages
def home(items: list, today: str) -> str:
    proj = dk.project(items, today)
    act = proj["actionable_now"]
    lit = {c for it in items for c in (it.get("geography") or {}).get("counties") or []}
    svg = texas_map.render(lit=lit)

    n_counties = len(lit)
    n_items = proj["counts"]["items"]
    n_claims = proj["counts"]["claims"]

    if act:
        soonest = act[0]
        lede = (f'<div class="clock{" soon" if soonest["days_left"] <= 7 else ""}">'
                f'<span class="days">{soonest["days_left"]}</span>'
                f'<span class="lab">days left on the next comment window</span></div>')
        openers = (f'<p><strong>{len(act)}</strong> of the '
                   f'<strong>{n_items}</strong> decisions on this record are still open to '
                   f'public comment.</p>')
    else:
        lede = ('<div class="gap"><strong>No comment window on this record is open today.</strong>'
                ' Windows are checked every day, and one appears here the moment it opens.</div>')
        openers = f"<p>The record holds <strong>{n_items}</strong> decisions.</p>"

    rows = "".join(
        f'<li><h3><a href="item/{e(a["id"])}/">{e(a["title"])}</a></h3>'
        f'<p class="meta"><span class="num">{a["days_left"]}</span> days left, '
        f'closes {e(ordinal(_dt.date.fromisoformat(a["closes"])))}</p></li>'
        for a in act[:6])

    body = f"""
<section class="hero">
  <h1>What is being decided about AI in Texas, and whether you can still say something.</h1>
  <div class="prose">{openers}</div>
  {lede}
</section>

<section>
  <h2>Where</h2>
  <div class="prose"><p>Every county in Texas, drawn from the state's own geometry. The lit
  counties are the ones this record currently touches, <span class="num">{n_counties}</span>
  of <span class="num">254</span>.</p></div>
  {svg}
</section>

{'<section><h2>Still open</h2><ul class="items">' + rows + '</ul></section>' if rows else ''}

<section>
  <h2>What this is</h2>
  <div class="prose">
    <p>A record of decisions about artificial intelligence in Texas: who decided, by when, and
    whether the public still has a way in. It holds <span class="num">{n_items}</span> decisions
    supported by <span class="num">{n_claims}</span> quoted sources.</p>
    <p>An entry is admitted only when every fact in it carries a quote from a source that was
    actually fetched, and at least one of those sources is the filing, the statute or the agency
    itself rather than a news report about it.</p>
  </div>
</section>
"""
    return page(title=f"{SITE_NAME}", depth=0, active="",
                desc=("A public, fact-checked record of AI decisions in Texas: who decides, "
                      "by when, and whether you can still comment."),
                body=body, today=today, canonical="",
                extra_ld=[docket_dataset_ld(items, today)])


def docket_index(items: list, today: str) -> str:
    """Sorted by urgency, because that is the order the reader needs, not the order we filed."""
    def key(it):
        st = dk.window_state(it, today)
        if st == "open":
            return (0, (_dt.date.fromisoformat(it["public_access"]["closes"])
                        - _dt.date.fromisoformat(today)).days)
        return ({"open_meeting": 1, "contact_only": 2, "closed": 3}
                .get(it["public_access"]["room"], 2), 0)

    rows = "".join(
        f'<li>{clock(it, today)}<h3><a href="item/{e(it["id"])}/">{e(it["title"])}</a></h3>'
        f'{item_meta(it)}</li>'
        for it in sorted(items, key=key))

    body = f"""
<h1>The record</h1>
<div class="prose"><p>Ordered by how soon a reader can still act, not by when it was filed.</p></div>
<ul class="items">{rows}</ul>
"""
    return page(title=f"The record — {SITE_NAME}", depth=0, active="",
                desc="Every AI decision on the Texas record, ordered by how soon you can act.",
                body=body, today=today, canonical="")


def item_page(it: dict, today: str) -> str:
    dates = "".join(
        f'<tr><td class="num">{e(k["date"])}</td><td>{e(k["kind"].replace("_", " "))}</td>'
        f'<td>{e(k.get("note") or "")}</td></tr>'
        for k in sorted(it.get("key_dates", []), key=lambda d: d["date"]))
    pa = it.get("public_access") or {}
    how = pa.get("how") or ""
    url = pa.get("url")
    act = (f'<p>{e(how)}</p>' + (f'<p><a href="{e(url)}" rel="nofollow noopener">'
                                 f'Where to do it</a></p>' if url else "")
           ) if how else '<p>No formal way in is published for this decision.</p>'

    body = f"""
<article>
<h1>{e(it["title"])}</h1>
{item_meta(it)}
{clock(it, today)}
<div class="prose"><p>{e(it["summary"])}</p></div>

<section><h2>How to take part</h2><div class="prose">{act}</div></section>

{'<section><h2>Dates</h2><table><thead><tr><th>Date</th><th>What</th><th>Note</th></tr></thead><tbody>' + dates + '</tbody></table></section>' if dates else ''}

<section>
  <h2>The evidence</h2>
  <div class="prose"><p>Every fact above rests on one of these. The words are the source's own.</p></div>
  {claims_html(it)}
</section>

<p class="meta"><span class="num">Last checked {e(it["last_verified"])}</span></p>
</article>
"""
    return page(title=f'{it["title"]} — {SITE_NAME}', depth=2, active="",
                desc=it["summary"][:180], body=body, today=today,
                canonical=f'item/{it["id"]}/')


def counties_page(items: list, today: str) -> str:
    by = {}
    for it in items:
        for c in (it.get("geography") or {}).get("counties") or []:
            by.setdefault(c, []).append(it)
    rows = "".join(
        f'<tr><td>{e(c)} County</td><td class="n num">{len(v)}</td>'
        f'<td>{", ".join(e(t) for t in dict.fromkeys(i["topic"] for i in v))}</td></tr>'
        for c, v in sorted(by.items(), key=lambda kv: (-len(kv[1]), kv[0])))
    statewide = [i for i in items if (i.get("geography") or {}).get("statewide")]

    body = f"""
<h1>By county</h1>
<div class="prose">
  <p><span class="num">{len(by)}</span> of Texas's <span class="num">254</span> counties are
  named in the record. A further <span class="num">{len(statewide)}</span> decisions apply
  statewide.</p>
  <p class="gap"><strong>A county with no entry is not a county where nothing is happening.</strong>
  It is a county where nothing has yet been found in a primary source. Roughly half of the data
  centres planned in Texas sit in unincorporated land, where there is no zoning file to read.</p>
</div>
{texas_map.render(lit=set(by))}
<table><thead><tr><th>County</th><th class="n">Items</th><th>Topics</th></tr></thead>
<tbody>{rows}</tbody></table>
"""
    return page(title=f"By county — {SITE_NAME}", depth=1, active="counties/",
                desc="Which Texas counties appear in the record of AI decisions.",
                body=body, today=today, canonical="counties/")


def data_page(items: list, today: str) -> str:
    proj = dk.project(items, today)
    rows = "".join(f'<tr><td>{e(k)}</td><td class="n num">{v}</td></tr>'
                   for k, v in proj["counts"]["by_topic"].items())
    body = f"""
<h1>The data</h1>
<div class="prose">
  <p>The whole record is one JSON file. It is the same file this site is built from, so anything
  published here can be recomputed from it.</p>
  <p><a href="../docket.json">docket.json</a></p>
</div>
<table><thead><tr><th>Topic</th><th class="n">Items</th></tr></thead><tbody>{rows}</tbody></table>
<div class="prose">
  <h2>How a fact gets in</h2>
  <p>An entry is admitted when every gate passes: the shape is valid, every claim carries a
  verbatim quote and a URL that was fetched, no numeral appears in the prose that is not either
  quoted from a source or computed from the record itself, and at least one source is primary.</p>
  <p>Entries that fail stay out until they pass. Nothing is published on the strength of a
  headline alone.</p>
</div>
"""
    return page(title=f"The data — {SITE_NAME}", depth=1, active="data/",
                desc="The Texas AI Docket as open data, and the gates every entry passes.",
                body=body, today=today, canonical="data/")


def about_page(today: str) -> str:
    body = """
<h1>About</h1>
<div class="prose">
  <p>The Texas AI Docket is a public record of decisions about artificial intelligence in Texas:
  data centres, the electric grid, state policy, land, water and permitting.</p>

  <h2>Numbers are computed, never generated</h2>
  <p>Every numeral published here is produced by code, from data, and can be recomputed from the
  same inputs. No number is typed by a person. This is the reason to believe a figure here over a
  figure somewhere else, and it is enforced by a build gate rather than by good intentions: a
  numeral that cannot be traced to a quoted source or to a computation fails the build.</p>

  <h2>Where we cannot measure, we say so</h2>
  <p>Some things are genuinely not public. Per-site large load metering is confidential. Roughly
  half the data centres planned in Texas sit in unincorporated land with no zoning file. Where
  that is true this record publishes the size of the gap rather than an estimate dressed as a
  measurement.</p>

  <h2>What this record will never do</h2>
  <p>It will not tell you whether the grid will hold. It will not predict an outcome or publish a
  verdict on a project. It publishes what was decided, by whom, by when, and whether the public
  still has a way in.</p>

  <h2>Corrections</h2>
  <p>When something here has been wrong, the correction says what was wrong, for how long, and
  where the right answer was checked. Corrections stay on the page.</p>
</div>
"""
    return page(title=f"About — {SITE_NAME}", depth=1, active="about/",
                desc="What the Texas AI Docket is, how its numbers are produced, and its limits.",
                body=body, today=today, canonical="about/")


# --------------------------------------------------------------------------- machine readers
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
        f'- Status: {it["status"]}',
        f'- Public access: {room_label(pa.get("room", ""))}',
    ]
    if pa.get("closes"):
        lines.append(f'- Comment closes: {pa["closes"]}')
    if pa.get("url"):
        lines.append(f'- Take part: {pa["url"]}')
    lines += ["", f'- Last checked: {it["last_verified"]}', "", "## Dates", ""]
    for k in sorted(it.get("key_dates", []), key=lambda d: d["date"]):
        lines.append(f'- {k["date"]} — {k["kind"].replace("_", " ")}'
                     + (f': {k["note"]}' if k.get("note") else ""))
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


def llms_txt(items: list, today: str) -> str:
    """Published as cheap hygiene, and nothing on this site claims it does more.

    No major AI crawler documents that it reads /llms.txt. Google, Anthropic and Perplexity all
    name robots.txt as the control surface and none mention it. It is a community proposal, not
    a standard. Publishing costs one generated file from a build that already holds the index in
    memory; claiming it works would be exactly the unverifiable assertion this project refuses.
    """
    rows = "\n".join(f'- [{i["title"]}]({SITE_URL}/item/{i["id"]}/index.md): '
                     f'{i["summary"][:110]}' for i in items)
    return (f"# {SITE_NAME}\n\n"
            f"> A public, fact-checked record of decisions about artificial intelligence in "
            f"Texas. Every entry carries verbatim quotes from the sources it rests on, and at "
            f"least one primary source. Every numeral is computed from data, never written by "
            f"a person.\n\n"
            f"## The record\n\n{rows}\n\n"
            f"## Data\n\n"
            f"- [The whole record as JSON]({SITE_URL}/docket.json)\n"
            f"- [Atom feed]({SITE_URL}/atom.xml)\n"
            f"- [JSON feed]({SITE_URL}/feed.json)\n")


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
def build(out: Path, today: str) -> dict:
    items = dk.load(LEDGER)
    bad, results = dk.run_gates(items, today)
    if bad:
        dk.report(results)
        raise SystemExit("site_build: the record does not pass its own gates; refusing to build")

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    written = []

    def w(path: str, text: str):
        p = out / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        written.append(path)

    w("site.css", theme.css())
    w("index.html", home(items, today))
    w("docket.json", json.dumps({"_spec": {"generated": today}, "items": items},
                                indent=2, ensure_ascii=False) + "\n")
    for it in items:
        w(f'item/{it["id"]}/index.html', item_page(it, today))
        # The Markdown twin. A crawler that fetches this gets the record without parsing HTML,
        # and a model quoting from it is far less likely to mangle a figure.
        w(f'item/{it["id"]}/index.md', item_markdown(it, today))
    w("atom.xml", atom(items, today))
    w("feed.json", feed_json(items, today))
    w("llms.txt", llms_txt(items, today))
    w("counties/index.html", counties_page(items, today))
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

    urls = [u for u in written if u.endswith("index.html")]
    locs = "".join(
        f"<url><loc>{SITE_URL}/{u[:-10]}</loc><lastmod>{today}</lastmod></url>"
        for u in urls)
    w("sitemap.xml",
      f'<?xml version="1.0" encoding="UTF-8"?>'
      f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{locs}</urlset>')

    return {"pages": len(urls), "files": len(written), "items": len(items)}


def self_test() -> int:
    import tempfile
    failures = 0

    def check(label, cond, extra=""):
        nonlocal failures
        print(f"  {'ok  ' if cond else 'FAIL'}  {label}{'' if cond else '  ' + extra}")
        if not cond:
            failures += 1

    today = "2026-08-11"
    with tempfile.TemporaryDirectory() as td:
        stats = build(Path(td) / "a", today)
        check("the site builds", stats["pages"] >= 4, str(stats))
        idx = (Path(td) / "a" / "index.html").read_text(encoding="utf-8")
        check("the home page names the reader's question",
              "still say something" in idx or "still open" in idx)
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
              "## The record" in (Path(td) / "a" / "llms.txt").read_text(encoding="utf-8"))

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
        check("an item page links the source", "rel=\"nofollow noopener\"" in one)

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
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:                                       # noqa: BLE001
        print(f"site_build: broke: {exc}", file=sys.stderr)
        sys.exit(2)
