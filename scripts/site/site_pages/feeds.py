"""Machine-readable feeds, question hubs, and source page renderers."""
from __future__ import annotations

from site_context import (
    LICENCE, REPO_ROOT, SCHEMA_CTX, SITE_NAME, SITE_URL, _dt, _host_slug,
    _made_at_numerals, _place_facts, dk, e, frontchip, json, load_runs,
    next_door, numeral_lint, ordinal, page, room_label, schema, topic_label,
    video_count,
)
from site_pages.docket import _item_metros

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
        # THE METRO LINE IS IN THE HTML, SO IT IS HERE. The twin is the record as a machine
        # reads it, and a twin that carries a narrower answer than the page is a second
        # vocabulary for the same question, which is the drift `places.py` exists to stop.
        #
        # A SUB LIST RATHER THAN A COMMA JOIN, because every OMB area name ENDS in ", TX".
        # Joined with commas, seven areas read as fourteen fields and nothing downstream
        # can split them back. County names carry no comma, which is why `Where` above can.
        *(["- Statistical areas:"] + [f"  - {m}" for m in _item_metros(it)]
          if _item_metros(it) else []),
        f'- Status: {it["status"]}',
        f'- Public access: {room_label(pa.get("room", ""))}',
    ]
    if pa.get("closes"):
        lines.append(f'- Comment closes: {pa["closes"]}')
    if pa.get("url"):
        lines.append(f'- Take part: {pa["url"]}')
    lines += ["", f'- Last checked: {it["last_verified"]}', "", "## Dates", ""]
    for k in sorted(it.get("key_dates", []), key=lambda d: d["date"]):
        lines.append(f'- {k["date"]} · {k["kind"].replace("_", " ")}'
                     + (f': {k["note"]}' if k.get("note") else ""))
    # THE MOVEMENT LOG BELONGS IN THE TWIN TOO. The twin is the record as a machine reads it,
    # and the one thing a machine reader most often gets wrong about a decision is whether it
    # is still live. A dated line saying somebody looked on the 18th and nothing had changed
    # answers that better than the status word does, and leaving it out of the twin would build
    # the same gap one layer down that this whole section exists to close.
    movement = sorted((x for x in (it.get("history") or []) if isinstance(x, dict)),
                      key=lambda d: str(d.get("date", "")))
    if movement:
        lines += ["", "## How this decision moved", "",
                  "One dated line per check, oldest first. A line that says nothing changed "
                  "means somebody looked and it had not.", ""]
        for h in movement:
            lines.append(f'- {h["date"]} · {h.get("note") or ""}')
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


def _first_sentence(text: str, cap: int = 220) -> str:
    """A description that ends where a sentence ends, never mid word.

    THE BUG THIS FIXES was `summary[:110]`, a hard character cut that shipped
    "...amend its certificate of convenience and necessity to build the Dinosau" into the file
    a model reads to learn what this site holds. Fifty eight entries, every one truncated, many
    of them mid word. A machine reading that learns the record is unreliable, which is the exact
    opposite of the thing being advertised.
    """
    text = " ".join((text or "").split())
    if len(text) <= cap:
        return text
    cut = text[:cap]
    stop = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "))
    if stop > cap * 0.5:
        return cut[:stop + 1]
    return cut[:cut.rfind(" ")].rstrip(",;") + "..."


def not_found_page(today: str, items: list) -> str:
    """The page a reader gets for a path that is not here.

    GitHub Pages serves `docs/404.html` for any unknown path. Without one, a mistyped decision
    id lands on the host's default page: no navigation, no way to search, and nothing saying
    the site is ours. The most common way to arrive here is a stale link to a decision, so the
    one useful thing to offer is the record itself and the box that answers questions about it.

    NOT IN THE SITEMAP and it carries no canonical, because it is not a destination. It is also
    the one page whose own URL is unknown at build time, which is why `canonical` points at the
    record rather than at itself.
    """
    body = f"""
<article>
<h1>That page is not here</h1>
<div class="prose">
  <p>The link may be old, or the address may have a typo in it. Nothing has been removed from
  this record, so a decision that was here is still here under its own address.</p>
  <p>The record carries <span class="num">{len(items)}</span> tracked decisions and every one
  of them is listed in one place.</p>
</div>
<p class="ctarow"><a class="cta solid" href="record/">Open the record</a>
<a class="cta ghost" href="./">Front page</a></p>
</article>
"""
    return page(title=f"Not found · {SITE_NAME}", depth=0, active=None,
                desc="That page is not here. The record and every tracked decision in it are "
                     "one link away.",
                body=body, today=today, canonical="record/")


def _cite_titles(text: str, titles: set) -> str:
    """Wrap every verbatim source title in `<cite>`, which is what it is.

    Marks quoted material as quoted so the numeral and style lints skip it, the same mechanism
    `house_style_check` has always used. Longest first, so a title containing another is not
    left in fragments. The text is ALREADY ESCAPED when this runs, so the titles are escaped to
    match before comparison.
    """
    for t in sorted(titles, key=len, reverse=True):
        text = text.replace(e(t), f"<cite>{e(t)}</cite>")
    return text


def _quoted_numerals(items: list) -> set:
    """Numerals that live inside a source's own title or url, for the two pages that print them.

    A docket number in "PUCT Interchange, Filings for 58000" is an IDENTIFIER inside QUOTED
    MATERIAL. It is not a measurement, it was not computed, and it is not ours to change: a
    document's title is the document's own words, which is the same reason `house_style_check`
    never lints a quotation.

    PASSED PER PAGE, NEVER ADDED TO THE SITE-WIDE SET. `_authorised_numerals` carries a warning
    earned twice over, that both times this gate was silently disabled the cause was an
    allowlist that grew wider than the page it guarded. Only the questions and sources pages
    print source titles, so only they get this.
    """
    out = set()
    for it in items:
        for c in it.get("claims") or []:
            for field in (c.get("source_title"), c.get("source_url")):
                if field:
                    out |= set(numeral_lint.NUMERAL.findall(field))
    return out


def _run_numerals(r: dict) -> set:
    """Every numeral one shipped deck is entitled to print, and where each one comes from.

    Two origins and no third. A figure was QUOTED from a source, so it is in a claim's verbatim
    quote or in the title of the document that quote came from. Or it was COMPUTED by the run,
    in which case it is in that run's `computed.json`, which is the file its own `compute.py`
    wrote and which the run's gates checked the slides against.

    A numeral the deck printed from neither is exactly what this gate exists to refuse, and it
    stays refused: nothing here authorises a figure by it having appeared on a slide.
    """
    out = set()
    for c in r.get("claims") or []:
        for field in (c.get("quote"), c.get("text"), c.get("source_title"), c.get("url")):
            if field:
                out |= set(numeral_lint.NUMERAL.findall(str(field)))

    computed = REPO_ROOT / "runs" / "carousel" / r["date"] / "computed.json"
    try:
        blob = json.loads(computed.read_text("utf-8"))
    except Exception:                                                # noqa: BLE001
        blob = None

    def walk(node):
        if isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)
        elif isinstance(node, (int, float)) and not isinstance(node, bool):
            out.add(str(node))
            out.add(f"{node:,}")
        elif isinstance(node, str):
            out.update(numeral_lint.NUMERAL.findall(node))

    walk(blob)
    return out


def question_groups(items: list, today: str) -> dict:
    """Every computed question and answer, grouped by the KIND of question it is.

    One place builds this, and both the hub and the twelve kind pages read it, so a question
    can't appear on one and not the other.
    """
    groups = {}
    for it in sorted(items, key=lambda i: i["title"]):
        for q, a in schema.qa_pairs(SCHEMA_CTX, it, today):
            groups.setdefault(schema.shape_of(q, it["title"]), []).append((it, q, a))
    return groups


def questions_check(groups: dict) -> None:
    """The frames and `schema.QUESTION_KINDS` agree, in both directions, on every build.

    A frame with no entry would silently drop its questions off the site entirely, because the
    hub only walks the map. An entry no frame produces would render an empty page that looks
    perfectly healthy. The second is the one that rots quietly, so both are a hard fail.
    """
    mapped = {shape for shape, _s, _h, _b in schema.QUESTION_KINDS}
    built = set(groups)
    if built - mapped:
        raise SystemExit("questions: qa_pairs produces a shape with no page: "
                         + ", ".join(sorted(built - mapped)))
    if mapped - built:
        raise SystemExit("questions: QUESTION_KINDS carries a shape nothing produces: "
                         + ", ".join(sorted(mapped - built)))


def _qa_rows(rows: list, titles: dict, depth: int) -> str:
    up = "../" * depth

    def one(it, q, a):
        # A LIST ANSWER IS MARKED AS DATA, and only once it has proved it is one. The check is
        # in `schema.list_answer_ok`, which reads the item's own county list, so an answer that
        # started carrying prose would fail the build rather than quietly inherit the exemption.
        listy = (schema.shape_of(q, it["title"]) in schema.LIST_ANSWER_SHAPES
                 and schema.list_answer_ok(it, a))
        if schema.shape_of(q, it["title"]) in schema.LIST_ANSWER_SHAPES and not listy:
            raise SystemExit(f'questions: {it["id"]} claims a list answer that is not one: {a}')
        mark = ' data-prose="data"' if listy else ""
        return (f'<details><summary>{e(q)}</summary><div class="prose">'
                f'<p{mark}>{_cite_titles(e(a), titles)}</p>'
                f'<p><a class="go" href="{up}item/{it["id"]}/">Open the decision</a>.</p>'
                f'</div></details>')

    return "".join(one(it, q, a) for it, q, a in rows)


def questions_hub(items: list, today: str) -> tuple:
    """The twelve kinds of question this record answers, each linking to its own page.

    WHY A HUB AND NOT A DOORWAY. The difference is whether anything is behind it. Every kind
    listed here has a page of real answers, and every answer is the same computed pair the item
    page emits as structured data, from `schema.qa_pairs`, so the page and the JSON-LD cannot
    drift and neither can be written independently of the ledger.

    WHY IT SPLIT. This was one page carrying all 633 pairs, 290 KB of HTML and 633 `<details>`
    elements, and it was the heaviest thing on the site by a factor of six. That is a slow page
    on a phone over cellular for no reason, and it is one title, one description and one
    canonical URL trying to be about twelve different questions at once. Split, each kind gets
    a page whose title is what it is about, which is both lighter to load and a far more
    targetable unit for the search that lands on it.

    ONE KIND PER PAGE rather than one decision per page, because a reader arrives with a KIND of
    question. Fifty eight blocks of ten questions is a database dump.
    """
    groups = question_groups(items, today)
    questions_check(groups)
    total = sum(len(v) for v in groups.values())
    figures = {str(total), str(len(schema.QUESTION_KINDS))}
    figures |= {str(len(v)) for v in groups.values()}

    cards = "".join(
        f'<li data-prose="data"><a class="dcard open" href="{slug}/">'
        f'<span class="big">{len(groups[shape]):02d}</span>'
        f'<span class="left">answered</span>'
        f'<h3>{e(head)}</h3><span class="note">{e(blurb)}</span></a></li>'
        for shape, slug, head, blurb in schema.QUESTION_KINDS if groups.get(shape))

    body = f"""
<article>
<h1>Questions this record answers</h1>
<div class="prose">
  <p>Every answer is assembled from the record itself, from the same fields the decision page
  prints. Nothing here is written separately, so an answer can't drift from the entry it
  describes.</p>
  <p>An answer the record can't support is not shown at all.</p>
</div>
<ul class="deck">{cards}</ul>
</article>
"""
    return figures, page(title=f"Questions · {SITE_NAME}", depth=1, active="record/",
                desc="Every question this record can answer about AI decisions in Texas, "
                     "answered from the record itself.",
                body=body, today=today, canonical="questions/",
                extra_ld=[schema.collection_node(
                              SCHEMA_CTX, name="Questions", path="questions/",
                              description="Questions answered from the tracked record.",
                              count=total),
                          schema.breadcrumbs(SCHEMA_CTX,
                                             [(SITE_NAME, ""), ("Questions", "questions/")])])


def questions_kind_page(items: list, today: str, kind: tuple) -> tuple:
    """One kind of question, asked of every decision on the record that can answer it."""
    shape, slug, head, blurb = kind
    groups = question_groups(items, today)
    rows = groups.get(shape) or []
    titles = schema.source_titles(items)
    figures = {str(len(rows))}

    others = "".join(
        f'<a href="../{s}/">{e(h)}</a>'
        for sh, s, h, _b in schema.QUESTION_KINDS if sh != shape and groups.get(sh))

    body = f"""
<article>
<h1>{e(head)}</h1>
<div class="prose">
  <p>{e(blurb)} Answered here for {len(rows)} of the decisions on the record, from the same
  fields the decision page prints.</p>
</div>
<div class="qa">{_qa_rows(rows, titles, 2)}</div>
<nav class="chips" aria-label="Other kinds of question">{others}</nav>
</article>
"""
    return figures, page(title=f"{head} · {SITE_NAME}", depth=2, active="record/",
                desc=f"{blurb} Answered from the Texas AI Docket for {len(rows)} decisions.",
                body=body, today=today, canonical=f"questions/{slug}/",
                extra_ld=[schema.collection_node(
                              SCHEMA_CTX, name=head, path=f"questions/{slug}/",
                              description=blurb, count=len(rows)),
                          schema.breadcrumbs(SCHEMA_CTX,
                                             [(SITE_NAME, ""), ("Questions", "questions/"),
                                              (head, f"questions/{slug}/")])])


def _src_stat(claims: int, primary: int, docs: int, entries: int) -> str:
    """The four figures a publisher carries, as one line, built once for both surfaces.

    EACH PAIR IS ITS OWN UNBREAKABLE SPAN. Written as a flat run of numbers and words the line
    wrapped between a figure and the word it belongs to, and "7" ended a line with "ENTRIES"
    starting the next one. A reader then has to pair them by meaning, which is the one job a
    stat line exists to do for them. Nowrap inside a pair and a wide gap between pairs is the
    whole rule, and it only works while both come from here rather than from two call sites.
    """
    def pair(n, one, many):
        return (f'<span class="st"><span class="num">{n}</span>'
                f'{one if n == 1 else many}</span>')
    return (pair(claims, "claim", "claims") + pair(primary, "primary", "primary")
            + pair(docs, "document", "documents") + pair(entries, "entry", "entries"))


def source_pages(items: list, today: str) -> list:
    """One page per publisher, which is the form this archive has to take to be found.

    WHY NOT ONE LONG PAGE, which is what it was.
    A search engine indexes a URL. Forty publishers on one URL is one thing to rank, competing
    with itself for every query, and a reader arriving from a search for one of them lands at
    the top of a list of the other thirty nine. The archive already held everything a page
    about a publisher needs, which is what it has been cited for, how much of the record rests
    on it, and which decisions those are. It was just not addressable.

    WHAT MAKES THIS NOT A DOORWAY PAGE, and the distinction is the whole reason it is allowed.
    A doorway page is one that exists for a crawler and carries nothing for a reader. Every
    sentence and every figure here is computed from the ledger, each page carries the actual
    documents and the actual entries that rest on them, and a reader who followed a citation
    back to a publisher gets exactly what they came for. The pages are also the missing half
    of the item page's evidence block, which lists a source and until now was a dead end.

    THE LINK GOES BOTH WAYS, which is the part a sitemap cannot do for you. The hub ranks and
    links down, each publisher page links back to every entry that cites it, and every entry's
    evidence block links out to the publisher. A crawler that finds any one of the three finds
    the other two.
    """
    from urllib.parse import urlparse
    hosts = {}
    for it in items:
        for c in it.get("claims") or []:
            u = c.get("source_url")
            if not u:
                continue
            h = urlparse(u).netloc.removeprefix("www.")
            d = hosts.setdefault(h, {}).setdefault(
                u, {"title": c.get("source_title") or u, "type": c.get("source_type"),
                    "items": {}, "claims": 0})
            d["items"][it["id"]] = it["title"]
            d["claims"] += 1

    out = []
    for h in sorted(hosts):
        docs = hosts[h]
        n_claims = sum(d["claims"] for d in docs.values())
        n_primary = sum(1 for d in docs.values()
                        if str(d.get("type") or "").startswith("primary"))
        ent = {i: t for d in docs.values() for i, t in d["items"].items()}
        stat = _src_stat(n_claims, n_primary, len(docs), len(ent))
        rows = "".join(
            f'<li><a href="{e(u)}" rel="nofollow noopener"><cite>{e(d["title"])}</cite></a> '
            # THE VERB AGREES WITH THE COUNT, which is the fault `schema.py` caught as "One
            # source back it" and pinned with a self-test over every answer it can produce.
            # Pluralising the noun and leaving the verb alone reads correctly on the many and
            # wrong on the one, and most documents here carry several claims, so the broken
            # form only surfaces on the handful that carry exactly one.
            f'<span class="meta">{e((d["type"] or "").replace("_", " "))}, '
            f'<span class="num">{d["claims"]}</span> '
            f'{"claim rests" if d["claims"] == 1 else "claims rest"} on it</span></li>'
            for u, d in sorted(docs.items(), key=lambda kv: (-kv[1]["claims"], kv[1]["title"])))
        ents = "".join(
            f'<li><a href="../../item/{e(i)}/">{e(t)}</a></li>'
            for i, t in sorted(ent.items(), key=lambda kv: kv[1]))
        slug = _host_slug(h)
        body = f"""
<h1>{e(h)}</h1>
<div class="prose">
  <p>What the Texas AI Docket has checked against documents published at {e(h)}, and which
  decisions rest on them. Every quote in the record is the source's own words, fetched rather
  than remembered.</p>
</div>
<p class="srcstat" data-prose="data">{stat}</p>
<h2>The documents</h2>
<ul class="sources" data-prose="data">{rows}</ul>
<h2>The decisions that rest on them</h2>
<ul class="plainlist" data-prose="data">{ents}</ul>
<p class="meta" data-prose="data"><a href="../">Every source</a> ·
<a href="../../record/">All decisions</a></p>
"""
        # THE ENTRY TITLES THIS PAGE LISTS, on the record layer's own judgement about what in a
        # title is an identifier rather than a figure. "Ordinance 20260423-029" is the ordinance's
        # name and the item page already prints it on that basis, so the page that links to the
        # item inherits the same authority rather than re-deciding it here.
        figures = ({str(n_claims), str(n_primary), str(len(docs)), str(len(ent))}
                   | {str(d["claims"]) for d in docs.values()})
        for _t in ent.values():
            figures |= _identifier_numerals(str(_t))
        out.append((slug, figures, page(
            title=f"{h} · Sources · {SITE_NAME}", depth=2, active="record/",
            desc=f"The {len(docs)} document(s) from {h} that the Texas AI Docket has checked a "
                 f"claim against, and the {len(ent)} decision(s) that rest on them.",
            body=body, today=today, canonical=f"sources/{slug}/",
            extra_ld=[
                schema.collection_node(
                    SCHEMA_CTX, name=h, path=f"sources/{slug}/",
                    description=f"Documents published at {h} that the Texas AI Docket has "
                                f"checked a claim against.",
                    count=len(docs),
                    elements=[(t, f"item/{i}/") for i, t in
                              sorted(ent.items(), key=lambda kv: kv[1])]),
                schema.breadcrumbs(SCHEMA_CTX, [(SITE_NAME, ""), ("Sources", "sources/"),
                                                (h, f"sources/{slug}/")]),
            ])))
    return out


def sources_page(items: list, today: str) -> str:
    """Every document a claim in this record was checked against, grouped by who published it.

    THE PAGE THAT MAKES THE WHOLE ARGUMENT CHECKABLE. This record's claim is that every fact
    traces to a fetched source. Until this page existed a reader had to open 58 decisions to
    see the shape of that, and a machine had no single place to learn what this record rests on.

    GROUPED BY HOST, because "who says so" is the question a reader is actually asking, and a
    flat list of 95 urls answers it worse than a list of the bodies behind them.
    """
    from urllib.parse import urlparse
    hosts = {}
    for it in items:
        for c in it.get("claims") or []:
            u = c.get("source_url")
            if not u:
                continue
            h = urlparse(u).netloc.removeprefix("www.")
            hosts.setdefault(h, {}).setdefault(u, {"title": c.get("source_title") or u,
                                                   "type": c.get("source_type"), "items": set(),
                                                   "claims": 0})
            hosts[h][u]["items"].add(it["id"])
            # CLAIMS, NOT DOCUMENTS, is the weight that matters. Two entries can cite one filing
            # once each and a third can rest four separate facts on it, and only the claim count
            # tells those apart. It is how much of the record would fall over if the document
            # turned out to be wrong.
            hosts[h][u]["claims"] += 1

    def primary(d) -> bool:
        return str(d.get("type") or "").startswith("primary")

    # WHAT EACH PUBLISHER CARRIES, computed once and used for both the sort and the line the
    # reader sees, so the ranking and the figures explaining it can never disagree.
    tally = {h: {"docs": len(v),
                 "primary": sum(1 for d in v.values() if primary(d)),
                 "claims": sum(d["claims"] for d in v.values()),
                 "items": len({i for d in v.values() for i in d["items"]})}
             for h, v in hosts.items()}

    blocks = []
    # SORTED BY HOW MUCH OF THE RECORD RESTS ON THEM, not alphabetically. An alphabetical
    # archive ranks nothing, so a reader who wants to know who this record leans on has to read
    # all of it and keep a tally in their head. The page already had the counts to answer that
    # on the first screen and was sorting by the one field that carries no information. Ties
    # break on the host name, so the order is stable and the build stays deterministic.
    # THE HUB RANKS AND STOPS THERE. It used to print every document under every publisher,
    # which was the only sensible shape while this was one page. It stopped being sensible the
    # moment each publisher got its own, because then the hub and the fifty one pages carried
    # the same lists word for word, and a hub that duplicates the page it links to competes
    # with it for the query they both answer. So the hub does the one thing only it can do,
    # which is rank, and the documents live on the page that is about them.
    for h in sorted(hosts, key=lambda k: (-tally[k]["claims"], -tally[k]["docs"], k)):
        st = tally[h]
        stat = _src_stat(st["claims"], st["primary"], st["docs"], st["items"])
        blocks.append(
            f'<li><h2><a href="{e(_host_slug(h))}/">{e(h)}</a></h2>'
            f'<p class="srcstat" data-prose="data">{stat}</p></li>')

    n_docs = sum(len(v) for v in hosts.values())
    n_claims = sum(t["claims"] for t in tally.values())
    n_primary = sum(d["claims"] for v in hosts.values() for d in v.values() if primary(d))

    # THE NUMBER THAT TESTS THE PROMISE RATHER THAN DESCRIBING THE PILE.
    #
    # This page used to open with documents and publishers, which are facts about the archive's
    # SIZE. The claim the whole record makes is about its QUALITY, that a fact here rests on the
    # filing or the statute rather than on a report about one, and the share of claims sourced
    # to a primary document is the only figure that puts a number on it. Publishing it is worth
    # more than the count, in both directions: a share this project is not proud of is a share
    # its readers are entitled to see, and one it is proud of is worth more than saying so.
    body = f"""
<article>
<h1>Every source this record rests on</h1>
<div class="prose">
  <p>Each entry in the record carries a verbatim quote from a document that was fetched. At
  least one of those documents has to be the filing, the statute or the agency itself rather
  than a report about it. This is all of them, heaviest first.</p>
  <p><span class="num">{n_primary}</span> of <span class="num">{n_claims}</span> claims rest on
  a primary document, across <span class="num">{n_docs}</span> documents from
  <span class="num">{len(hosts)}</span> publishers.</p>
</div>
<ol class="srclist">{"".join(blocks)}</ol>
</article>
"""
    # THE FIGURES THIS PAGE COMPUTED, handed back with it. Authorising them at the call site by
    # guessing what the page prints is how an allowlist drifts from its page; returning them
    # from the computation that produced them is the only version that cannot.
    figures = {str(n_docs), str(len(hosts)), str(n_claims), str(n_primary)}
    figures |= {str(len(v)) for v in hosts.values()}
    figures |= {str(len(d["items"])) for v in hosts.values() for d in v.values()}
    figures |= {str(n) for t in tally.values() for n in t.values()}
    return figures, page(title=f"Sources · {SITE_NAME}", depth=1, active="record/",
                desc="Every document a claim in the Texas AI Docket was checked against, "
                     "grouped by publisher.",
                body=body, today=today, canonical="sources/",
                # THE HUB'S LIST NAMES ITS MEMBERS. A collection node carrying a count and no
                # elements tells a crawler how big the family is and nothing about where it
                # lives, which is the defect this file already fixed once for the beats. The
                # publishers go in ranked, so the node agrees with the page above it.
                extra_ld=[schema.collection_node(
                              SCHEMA_CTX, name="Sources", path="sources/",
                              description="Every document a claim was checked against, "
                                          "grouped by publisher and ranked by how much of the "
                                          "record rests on each one.",
                              count=len(hosts),
                              elements=[(h, f"sources/{_host_slug(h)}/") for h in
                                        sorted(hosts, key=lambda k: (-tally[k]["claims"],
                                                                     -tally[k]["docs"], k))]),
                          schema.breadcrumbs(SCHEMA_CTX,
                                             [(SITE_NAME, ""), ("Sources", "sources/")])])


def llms_txt(items: list, today: str) -> str:
    """The map of this site for a machine, in the community `llms.txt` shape.

    PUBLISHED AS CHEAP HYGIENE, and nothing on this site claims it does more. No major AI
    crawler documents that it reads `/llms.txt`. Google, Anthropic and Perplexity all name
    robots.txt as the control surface and none mention it. It is a community proposal, not a
    standard. Publishing costs one generated file from a build that already holds the index in
    memory. Claiming it works would be exactly the unverifiable assertion this project refuses.

    WHAT CHANGED, and why it was worth changing. The first version was one flat list of every
    item with each description cut at 110 characters, mid word. A flat list is not a map: it
    tells a reader what exists and nothing about what matters, and a truncated description is
    worse than none because it looks like the whole answer.

    THE ORDER IS THE ARGUMENT. What a person can still act on comes first, because a comment
    window that closes on Friday is the most perishable thing this record holds. Then the
    standing surfaces, then the whole record, then the data.
    """
    def line(i):
        return (f'- [{i["title"]}]({SITE_URL}/item/{i["id"]}/): '
                f'{_first_sentence(i["summary"])}')

    # The heading below promises a DATED way in, so the filter computes one. Room alone is the
    # kind of access the ledger recorded and says nothing about whether it is still open. See
    # `next_door` for the 28 finished votes this used to publish as live doors.
    open_now = [i for i in items
                if (i.get("public_access") or {}).get("room") in ("open_comment", "open_meeting")
                and next_door(i, today)]
    by_topic = {}
    for i in items:
        by_topic.setdefault(i["topic"], []).append(i)

    parts = [
        f"# {SITE_NAME}", "",
        "> A public, fact-checked record of decisions about artificial intelligence in Texas. "
        "Every entry carries verbatim quotes from the sources it rests on, and at least one "
        "primary source. Every numeral is computed from data, never written by a person.", "",
        "This record may be read, indexed, cited and quoted. Attribution to the "
        f"{SITE_NAME} with a link to the page is requested. No crawler is blocked. Every "
        "decision also exists as Markdown at the same path plus index.md, and the whole "
        "record is one fetch at /llms-full.txt.", "",
        "## Start here", "",
        f"- [The record, every tracked decision]({SITE_URL}/record/)",
        f"- [Questions answered from the record]({SITE_URL}/questions/)",
        f"- [Every source a claim was checked against]({SITE_URL}/sources/)",
        f"- [Texas Grid Watch, the daily ERCOT record]({SITE_URL}/grid/)",
        f"- [Texas Water Watch]({SITE_URL}/water/)",
    ]

    # THE TWELVE QUESTION PAGES, NAMED. This file exists so a model can find the answer without
    # crawling, and one link to a hub is a link to twelve more links. Naming them here is the
    # difference between "questions are answered somewhere on this site" and "the page that
    # says who decides is at this URL". Generated from the same map the pages are, so a kind
    # can't be listed here and missing there.
    parts += ["## Questions, by what is being asked", "",
              "Each page answers one kind of question about every decision on the record.", ""]
    parts += [f"- [{head}]({SITE_URL}/questions/{slug}/): {blurb}"
              for _shape, slug, head, blurb in schema.QUESTION_KINDS]
    parts += [""]

    # THE PUBLISHERS, NAMED, for the same reason the question pages are. A model asked "what
    # does the Texas AI Docket rest on" can answer it from this file without crawling 51 pages,
    # and a model checking whether a specific agency's filings are tracked here gets a URL
    # rather than a hub. Ranked by how much of the record rests on each, so the order carries
    # the same information the page does.
    from urllib.parse import urlparse as _up
    _weight = {}
    for _it in items:
        for _c in _it.get("claims") or []:
            _h = _up(_c.get("source_url") or "").netloc.removeprefix("www.")
            if _h:
                _weight[_h] = _weight.get(_h, 0) + 1
    if _weight:
        parts += ["## What the record rests on, by publisher", "",
                  "Every document a claim here was checked against, grouped by who published "
                  "it. Heaviest first.", ""]
        parts += [f"- [{h}]({SITE_URL}/sources/{_host_slug(h)}/)"
                  for h in sorted(_weight, key=lambda k: (-_weight[k], k))]
        parts += [""]

    if open_now:
        parts += ["## Open right now", "",
                  "Decisions a member of the public still has a dated way into.", ""]
        parts += [line(i) for i in sorted(open_now, key=lambda x: x["title"])]
        parts += [""]

    parts += ["## The whole record, by beat", ""]
    for topic in sorted(by_topic):
        parts += [f"### {topic_label(topic)}", ""]
        parts += [line(i) for i in sorted(by_topic[topic], key=lambda x: x["title"])]
        parts += [""]

    parts += [
        "## Feeds", "",
        f"- [RSS]({SITE_URL}/feed.xml)",
        f"- [Atom]({SITE_URL}/atom.xml)",
        f"- [JSON Feed]({SITE_URL}/feed.json)", "",
        "## Data", "",
        f"- [Every decision as Markdown, one fetch]({SITE_URL}/llms-full.txt)",
        f"- [Grid Watch as JSON]({SITE_URL}/gridwatch.json)",
        f"- [Water Watch as JSON]({SITE_URL}/waterwatch.json)", "",
    ]
    return "\n".join(parts)


def llms_full_txt(items: list, today: str) -> str:
    """Every decision as Markdown in one fetch.

    THE HIGHEST VALUE FILE ON THIS SITE FOR A MACHINE READER, and it costs one concatenation of
    twins the build already writes. A model answering a question about Texas and AI can hold the
    entire record in one request rather than crawling 58 pages and parsing HTML out of each.

    Built from `item_markdown` rather than from a second rendering, so the one fetch and the 58
    fetches can never disagree. A separate renderer here would be a second vocabulary for the
    same record, which is the drift this project keeps having to design against.
    """
    head = [
        f"# {SITE_NAME}", "",
        "The whole record as plain Markdown, one decision after another, in the order they "
        "are filed. Every fact carries a quote from a source that was fetched, and at least "
        "one of those sources is the filing, the statute or the agency itself.", "",
        f"Licence CC BY 4.0. Built {ordinal(_dt.date.fromisoformat(today))}, {today[:4]}. "
        f"The canonical page for any decision below is {SITE_URL}/item/<id>/.", "",
        "---", "",
    ]
    body = []
    for it in sorted(items, key=lambda i: i["id"]):
        body += [item_markdown(it, today).rstrip(), "", "---", ""]
    return "\n".join(head + body)


def feed_xml(items: list, today: str) -> str:
    """RSS 2.0, beside the Atom and JSON feeds.

    Three feed formats is not indulgence. Atom is the better specification, JSON Feed is the
    easiest to consume, and RSS is the one every reader, aggregator and newsroom tool actually
    supports. Shipping the two better ones and not the common one is a purity that costs
    readers.
    """
    def rfc822(d: str) -> str:
        return _dt.date.fromisoformat(d).strftime("%a, %d %b %Y 00:00:00 +0000")

    latest = max((i["last_verified"] for i in items), default=today)
    rows = "".join(
        f"<item><title>{e(i['title'])}</title>"
        f"<link>{SITE_URL}/item/{i['id']}/</link>"
        f"<guid isPermaLink=\"true\">{SITE_URL}/item/{i['id']}/</guid>"
        f"<pubDate>{rfc822(i['last_verified'])}</pubDate>"
        f"<description>{e(i['summary'])}</description></item>"
        for i in sorted(items, key=lambda x: x["last_verified"], reverse=True))
    return ('<?xml version="1.0" encoding="utf-8"?>'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f"<title>{e(SITE_NAME)}</title><link>{SITE_URL}/</link>"
            f'<atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>'
            "<description>A public, fact-checked record of decisions about artificial "
            "intelligence in Texas.</description><language>en-US</language>"
            f"<lastBuildDate>{rfc822(latest)}</lastBuildDate>"
            f"{rows}</channel></rss>")


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
def _identifier_numerals(text: str) -> set:
    """Numerals inside the spans the RECORD layer has already vetted as identifiers.

    NOT A SECOND OPINION. `docket_build.gate_numerals` is the authority on whether a
    numeral in the record is a figure or an identifier, and it decides by stripping six
    named spans before it looks. A statute section, a bill citation, a bare year, an item
    id, a hearing room and an ordinal date are identifiers there. Re-deciding that here
    would put two rules in the repository that answer the same question, which is how "the
    Austin metro" came to mean two things on two pages, so this inherits the judgement by
    running the record layer's own regexes.

    What is deliberately NOT inherited is the figure itself. A quantity in reader copy
    still has to trace to a computation or a quote.
    """
    out = set()
    # `dk.LOCATORS` is the rest of an address, added when the record grew a beat whose whole
    # subject is where to go and who to call. Spread from the record layer's own tuple rather
    # than listed again here, so a locator this project recognises is a locator on every
    # surface and there is still exactly one place that decides.
    for rx in (dk.ITEM_ID, dk.DATE_ORDINAL, dk.CITATION, dk.PLACE_NUMBER,
               *dk.LOCATORS, dk.DOTTED_SECTION, dk.YEAR):
        for m in rx.finditer(text):
            for n in dk.NUMERAL.findall(m.group(0)):
                out.add(n)
                out.add(n.replace(",", "").rstrip("%"))
    return out


def _item_numerals(it: dict, today: str) -> set:
    """One item's own figures, for the pages that render THAT item and no others.

    PER ITEM, because the record's set is the union of thirteen items and unioning it
    site wide is the mistake `_watch_numerals` documents, one order of magnitude down. A
    Federal Register document number quoted by one item is not a licence to print that
    number on another item's page.

    A CLAIM'S SOURCE TITLE IS THE SOURCE'S WORDS. "PUCT Interchange, Filings for 58000,
    item 64, party ERCOT" is a citation rendered verbatim, in the same class as the
    verbatim quote beside it, and neither is this page choosing a number. The claim's own
    `text` is NOT included, because that sentence is written rather than fetched and its
    figures belong in a quote.
    """
    a = numeral_lint.Authorised()
    a.add(it["id"], *str(it["id"]).split("-"))
    for field in ("title", "summary"):
        a.add(*_identifier_numerals(str(it.get(field, ""))))
    a.add(*_identifier_numerals(str((it.get("public_access") or {}).get("how", ""))))

    for c in (it.get("claims") or []):
        for field in ("verbatim_quote", "source_title"):
            for n in dk.NUMERAL.findall(str(c.get(field, ""))):
                a.add(n, n.replace(",", "").rstrip("%"))
        a.add(*_identifier_numerals(str(c.get("text", ""))))
    for kd in (it.get("key_dates") or []):
        a.add(kd.get("date"), *str(kd.get("date", "")).split("-"))
        a.add(*_identifier_numerals(str(kd.get("what", "")) + " " + str(kd.get("note", ""))))
        # A NAME WITH A NUMBER IN IT, on the record layer's judgement rather than this one's.
        # "NewsChannel 6" is a broadcaster and `dk._name_numerals` decides that by asking
        # whether the item's own evidence carries the name, which is the same inheritance this
        # function already makes for statutes and dates. Stated here because without it the
        # page passed by luck: a single digit is almost always in the site-wide set from some
        # unrelated computation, so the gate was waving the name through for the wrong reason
        # and would have failed the day the number was less common.
        a.add(*dk._name_numerals(it, str(kd.get("note", ""))))

    # THE COUNT ON THE TIMELINE'S NEXT STATION, computed here by the same subtraction the
    # strip does and authorised because of it rather than in spite of it. This is the shape the
    # law asks for. The page does not get to print a figure and have the gate wave it through
    # for being small, so the figure is derived twice from the same two dates and the second
    # derivation is what lets it through.
    ks = sorted(k["date"] for k in (it.get("key_dates") or []) if k.get("date"))
    t = _dt.date.fromisoformat(today)
    nxt = next((k for k in ks if _dt.date.fromisoformat(k) > t), None)
    if nxt:
        a.add((_dt.date.fromisoformat(nxt) - t).days)

    # THE MOVEMENT LOG, and this is a carve-out rather than an oversight. `docket_build`'s
    # numeral gate excludes history notes for a structural reason, and the site layer has to
    # make the same exclusion or the record passes and the page it produces fails. A movement
    # line's whole job is to say what the record USED TO HOLD, "the filing index moved from
    # 5782 to 5790". The old figure is by definition in no current claim quote, because the
    # claim was updated to the new one. Holding the log to the numeral set would make the one
    # sentence a movement log exists to write unwriteable, and would push a run toward "the
    # index moved" with no figures at all, which is worse copy and a weaker record. The old
    # value's provenance is `ledger/docket.json`'s own git history, which is a stronger trace
    # than a quote because it carries the run that observed the change.
    #
    # PER ITEM, like everything else in this function. An old figure from one decision's log
    # is not a licence to print that figure on another decision's page, so the carve-out is
    # exactly as wide as the page that renders the line and no wider.
    for h in (it.get("history") or []):
        if not isinstance(h, dict):
            continue
        for n in dk.NUMERAL.findall(str(h.get("note", "")) + " " + str(h.get("date", ""))):
            a.add(n, n.replace(",", "").rstrip("%"))
        a.add(*str(h.get("date", "")).split("-"))

    # THE LICENCE VERSION, WHICH IS A NAME AND NOT A MEASUREMENT. "CC BY 4.0" names a document,
    # the same way "H.B. 149" and "Chapter 552" do, and the record layer already treats those as
    # identifiers rather than figures. Taken from `LICENCE` rather than written here, so a page
    # that starts printing a different licence fails this gate instead of quietly passing it.
    a.add(*dk.NUMERAL.findall(LICENCE))

    # THE CONTROL NUMBER A READER NEEDS IN ORDER TO ACT. `public_access.how` says which
    # docket to file under, and that number is the single most consequential string on the
    # page. It is an identifier taken from the filing system, and it is authorised only
    # where a claim's source metadata carries the same digits, so a number typed into that
    # sentence and matching nothing in the evidence still fails.
    return a.set


def _home_numerals(items: list, today: str) -> set:
    """What the front page computes at render time, authorised by the same calls.

    The strip and the counter both format at the moment they draw, and neither form is
    what `_authorised_numerals` holds. The share is a ratio the record does not carry, and
    the open-doors counter is zero padded for the display, so `3` was authorised and `03`
    was what shipped.
    """
    a = numeral_lint.Authorised()
    # THE CHIP AND ITS DATE ARE ONE STATEMENT AND ONE CALL AUTHORISES BOTH. The date comes
    # from the weather ledger rather than from this build's `today`, and for as long as the
    # two matched nothing objected. The day a collector recovered a reading the site had not
    # been rebuilt for, the strip carried a day number no computation on this page had
    # produced. `frontchip.figures` returns exactly the numerals the chip prints, its own
    # self-test proves that set is neither short nor long, and the day is one of them.
    chip = frontchip.reading(_dt.date.fromisoformat(today))
    if chip:
        a.add(*frontchip.figures(chip))
    a.add(f"{len(dk.project(items, today)['actionable_now']):02d}")
    # THE PUBLISHED-WORK COUNTS, zero padded the way the row prints them. `02d` of zero is
    # "00", which is not "0", and the row prints three of them.
    a.add(f"{len(load_runs()):02d}", f"{video_count():02d}", len(load_runs()), video_count())
    return a.set


def _authorised_numerals(items: list, today: str) -> set:
    """Every numeral this build is entitled to print, assembled from what it computed.

    ASSEMBLED, NOT DECLARED. A hand-written allowlist drifts away from the pages the
    moment either changes, and the drift is invisible because both halves still look
    reasonable. So this walks the same projection the pages render from, plus the record
    itself, and a page may print exactly what the build worked out.

    Dates, years and statute citations are identifiers rather than measurements and are
    already stripped by `docket_build`'s numeral rules at the record layer. Here they are
    authorised explicitly, because a page prints them as text and the scanner cannot tell
    a section number from a quantity by looking at it.
    """
    proj = dk.project(items, today)
    a = numeral_lint.Authorised()
    tx = _place_facts()
    a.add(*tx.values())
    a.add(*_made_at_numerals())            # the colophon coordinate, on every page

    c = proj["counts"]
    a.add(c["items"], c["claims"], c["counties_touched"], c["metros_touched"],
          c["counties_touched_outside_any_metro"])
    a.add(*c["by_topic"].values(), *c["by_status"].values(), *c["by_room"].values())
    a.add(*proj["by_county"].values(), *proj["unmetroed_counties"].values())
    for m in proj["by_metro"].values():
        a.add(len(m["items"]), len(m["counties"]), len(m["touched_counties"]),
              len([x for x in m["counties"] if x not in m["touched_counties"]]), m["code"])
    for act in proj["actionable_now"]:
        a.add(act["days_left"], act["closes"], *str(act["closes"]).split("-"))

    for it in items:
        a.add(it["id"], len(it.get("claims") or []), len(it.get("key_dates") or []),
              len((it.get("geography") or {}).get("counties") or []))
        for src in (it.get("claims") or []):
            for m in dk.NUMERAL.findall(str(src.get("verbatim_quote", ""))):
                a.add(m, m.replace(",", "").rstrip("%"))
        for kd in (it.get("key_dates") or []):
            a.add(kd.get("date"), *str(kd.get("date", "")).split("-"))
        for field in ("title", "summary"):
            for m in dk.CITATION.findall(str(it.get(field, ""))):
                a.add(m)
    a.add(today, *today.split("-"), _dt.date.fromisoformat(today).day)

    # THE RENDERED FORM, not just the ISO one. `short_date` prints "SEP 8" for
    # 2026-09-08, and "8" is not "08", so authorising the ISO parts alone left every
    # single-digit deadline looking like a typed figure. Authorise what a reader sees.
    for it in items:
        for d in [(it.get("public_access") or {}).get("closes")] + \
                 [k.get("date") for k in (it.get("key_dates") or [])]:
            try:
                dd = _dt.date.fromisoformat(str(d))
            except (TypeError, ValueError):
                continue
            a.add(dd.day, f"{dd.day:02d}", dd.year, ordinal(dd).split()[-1].rstrip("stndrh"))

    # Statewide items are counted on several pages, and the count is a computation.
    a.add(sum(1 for i in items if (i.get("geography") or {}).get("statewide")))

    return a.set


def _watch_numerals(mod) -> set:
    """One watch page's own authorised set, kept SEPARATE from the record's.

    THE FIRST VERSION MERGED THESE INTO THE SITE-WIDE SET AND THAT MADE THE GATE
    VACUOUS. The grid watch authorises an hourly series and a full fuel mix, which is
    several hundred figures spanning every magnitude a page might print. Union them with
    everything else and almost any three to five digit number is authorised somewhere on
    the site, so a numeral typed into a docket page passes because an unrelated megawatt
    reading happens to match it.

    It was caught the only way it could be: by planting `8,927` into a sentence after the
    gate went green and watching the build sail through. **A gate is only as strong as
    its narrowest scope**, and the narrow scope here is the page, not the site.

    THE SECOND VERSION OF THIS FUNCTION FED THE WRONG SHAPE AND HID IT. It walked
    `mod.load()` and passed each raw reading to `mod.authorised()`, which wants the
    derived FRAME that `mod.figures()` builds. Every call raised `KeyError` on the first
    field, a bare `except Exception: pass` swallowed it, and the function returned an
    almost empty set that read as "this page authorises very little" rather than as
    "this never ran". Both watch pages then failed the site gate on their own correctly
    computed figures.

    So it goes through `figures()`, the same call the page renders from, and a failure is
    RAISED rather than absorbed. A watch page whose figures cannot be built is a broken
    page, and the build is the right place to find that out.
    """
    a = numeral_lint.Authorised()
    records = mod.load()
    if not records:
        return a.set
    a.add(*mod.authorised(mod.figures(records)))
    return a.set



__all__ = ['item_markdown', 'atom', 'feed_json', '_first_sentence', 'not_found_page', '_cite_titles', '_quoted_numerals', '_run_numerals', 'question_groups', 'questions_check', '_qa_rows', 'questions_hub', 'questions_kind_page', '_src_stat', 'source_pages', 'sources_page', 'llms_txt', 'llms_full_txt', 'feed_xml', 'docket_dataset_ld', '_identifier_numerals', '_item_numerals', '_home_numerals', '_authorised_numerals', '_watch_numerals']

