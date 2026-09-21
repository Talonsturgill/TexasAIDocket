"""Authored web editions beside, never inside, the immutable shipped carousel.

Every shipped date requires ledger/articles/<date>.json. Facts carry the shipped
claim ids, links resolve through those claims, and numeric tokens read the source text.
"""
from __future__ import annotations

import calendar
import datetime as dt
import html
import json
import re
from decimal import Decimal
from urllib.parse import urlsplit

from site_context import (
    REPO_ROOT, SCHEMA_CTX, SITE_NAME, SITE_URL, article_media, ordinal, page, schema,
)


CSS = """
.article-edition { padding-top:clamp(1rem,3vw,2.5rem); }
.edition-opening { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,.8fr);
  gap:clamp(2rem,5vw,5rem); align-items:center; padding-bottom:clamp(2.5rem,5vw,4rem);
  border-bottom:1px solid var(--rule-strong); }
.edition-kicker { margin:0 0 1.4rem; font:500 .76rem/1.5 var(--mono);
  letter-spacing:.1em; text-transform:uppercase; color:var(--accent); }
.edition-kicker a { color:inherit; text-decoration:none; }
.edition-header h1 { font:600 clamp(2.8rem,5.5vw,4.8rem)/1.04 var(--display);
  letter-spacing:-.045em; max-width:12ch; margin:0 0 1.5rem; text-wrap:balance; }
.edition-header h1.edition-title-long { max-width:19ch;
  font-size:clamp(2.15rem,4.2vw,3.65rem); line-height:1.1; letter-spacing:-.035em; }
.edition-dek { font:400 clamp(1.08rem,1.7vw,1.25rem)/1.65 var(--body);
  color:var(--ink); max-width:37ch; margin:0 0 1.75rem; }
.edition-byline { display:flex; flex-wrap:wrap; gap:.35rem 1.3rem; margin:0;
  font-size:.82rem; color:var(--ink-mute); }
.edition-byline a { color:var(--ink); text-decoration:none; }
.edition-read { display:inline-flex; align-items:center; gap:.65rem; min-height:44px;
  margin-top:1.5rem; font:500 .8rem/1.4 var(--mono); text-decoration:none;
  color:var(--accent); }
.edition-read span { font-size:1.25rem; }
.edition-gallery { min-width:0; margin:0; }
.edition-track { display:flex; overflow-x:auto; scroll-snap-type:x mandatory;
  overscroll-behavior-x:contain; scrollbar-width:thin; scrollbar-color:var(--rule-strong) transparent;
  border:1px solid var(--rule-strong); border-radius:4px; background:var(--panel); }
.edition-slide { flex:0 0 100%; min-width:0; scroll-snap-align:start; margin:0; }
.edition-slide img { display:block; width:100%; height:auto; aspect-ratio:4/5; }
.edition-gallery-caption { display:flex; align-items:center; justify-content:space-between;
  flex-wrap:wrap; gap:.25rem .75rem; padding-top:.65rem; }
.edition-gallery-label { font:400 .7rem/1.5 var(--mono); text-transform:uppercase;
  letter-spacing:.07em; color:var(--ink-mute); }
.edition-controls { display:flex; align-items:center; gap:.3rem; }
.edition-controls[hidden],.edition-controls [hidden] { display:none; }
.edition-controls button { appearance:none; border:1px solid var(--rule-strong);
  border-radius:3px; background:transparent; color:var(--ink); cursor:pointer;
  min-width:44px; min-height:44px; padding:.35rem; font:500 .85rem/1 var(--mono); }
.edition-controls button:disabled { opacity:.4; cursor:default; }
.edition-controls button:hover:not(:disabled) { background:var(--surface); border-color:var(--accent); }
.edition-controls .edition-view { padding:.35rem .6rem; margin-left:.35rem;
  border-color:transparent; font-size:.72rem; }
.edition-count { min-width:3.5rem; text-align:center; font:400 .72rem/1.4 var(--mono);
  color:var(--ink-mute); }
.edition-track:focus-visible,.article-edition button:focus-visible,
.article-edition a:focus-visible,.article-edition summary:focus-visible {
  outline:2px solid var(--accent); outline-offset:4px; }
.edition-gallery.is-all .edition-track { display:grid; gap:.65rem; grid-template-columns:1fr 1fr;
  overflow:visible; border:0; background:transparent; }
.edition-gallery.is-all .edition-slide { border:1px solid var(--rule-strong); }
.edition-reading { max-width:43rem; margin:0 auto; }
.edition-story { padding-top:clamp(2rem,4vw,3.5rem); scroll-margin-top:7rem; }
.edition-story p { font:400 1.1rem/1.85 var(--body); margin:0 0 1.25rem;
  color:var(--ink); overflow-wrap:break-word; }
.edition-story .edition-lead { font-size:1.22rem; line-height:1.75; color:var(--ink-bright); }
.edition-story h2 { font:600 clamp(1.4rem,2.5vw,1.75rem)/1.3 var(--display);
  letter-spacing:-.02em; margin:2.8rem 0 1.1rem; text-wrap:balance; }
.edition-story a,.edition-records a,.edition-sources a { text-decoration-thickness:1px;
  text-underline-offset:.2em; }
.edition-records { margin:2.75rem 0; padding:1.5rem 0; border-block:1px solid var(--rule-strong); }
.edition-records h2,.edition-sources h2 { font:500 .75rem/1.5 var(--mono);
  letter-spacing:.08em; text-transform:uppercase; margin:0 0 .8rem; color:var(--ink-mute); }
.edition-records ul { padding:0; margin:0; list-style:none; }
.edition-records li { margin:.6rem 0; font-size:.95rem; }
.edition-sources { padding-bottom:2rem; }
.edition-source-list { list-style:none; padding:0; margin:0 0 1.5rem; }
.edition-source-list li { padding:.85rem 0; border-bottom:1px solid var(--rule); }
.edition-source-list a { font-size:.93rem; color:var(--ink); }
.edition-source-list cite { font-style:normal; }
.edition-source-meta { display:block; font:400 .69rem/1.65 var(--mono);
  color:var(--ink-mute); margin-top:.2rem; overflow-wrap:anywhere; }
.edition-verified { border-block:1px solid var(--rule-strong); }
.edition-verified summary { cursor:pointer; padding:1rem 0; font:500 .82rem/1.5 var(--mono);
  color:var(--ink); }
.edition-verified summary span { color:var(--ink-mute); font-weight:400; }
.edition-verified .claims { padding-left:1.3rem; margin:1rem 0; }
.edition-verified .claims > li { padding:.7rem 0 1.2rem .4rem; border-bottom:1px solid var(--rule); }
.edition-verified .claims p { font-size:.95rem; line-height:1.7; margin:.3rem 0; }
.edition-verified blockquote { margin:.65rem 0; padding-left:1rem;
  border-left:2px solid var(--rule-strong); font-size:.85rem; line-height:1.7; color:var(--ink-mute); }
.edition-verified .claims .meta { font-size:.72rem; }
.edition-verified cite { font-style:normal; }
.edition-end { display:flex; justify-content:space-between; flex-wrap:wrap; gap:.75rem;
  padding:1.5rem 0 .5rem; font-size:.8rem; color:var(--ink-mute); }
@media (max-width:54rem) {
  .edition-opening { grid-template-columns:1fr; gap:2rem; }
  .edition-header h1 { max-width:17ch; font-size:clamp(2.65rem,8vw,4.5rem); }
  .edition-dek { max-width:45ch; }
  .edition-gallery { width:100%; max-width:32rem; margin-inline:auto; }
  .edition-read { margin-top:.8rem; }
}
@media (max-width:30rem) {
  .edition-kicker { margin-bottom:1rem; }
  .edition-header h1 { margin-bottom:1rem; }
  .edition-dek { font-size:1.05rem; margin-bottom:1.25rem; }
  .edition-gallery-label { font-size:.62rem; letter-spacing:.02em; }
  .edition-controls { gap:.1rem; }
  .edition-controls .edition-view { padding-inline:.25rem; margin-left:0; }
  .edition-count { min-width:2.7rem; }
  .edition-story p { font-size:1.02rem; line-height:1.8; }
  .edition-story .edition-lead { font-size:1.12rem; }
  .edition-gallery.is-all .edition-track { grid-template-columns:1fr; }
}
"""

SCRIPT = """
(() => {
  const gallery = document.querySelector('.edition-gallery');
  if (!gallery) return;
  const track = gallery.querySelector('.edition-track');
  const slides = Array.from(track.children);
  const controls = gallery.querySelector('.edition-controls');
  const previous = gallery.querySelector('[data-previous]');
  const next = gallery.querySelector('[data-next]');
  const counter = gallery.querySelector('.edition-count');
  const view = gallery.querySelector('[data-view]');
  let current = 0, all = false, frame;
  const motion = () => matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth';
  const update = () => {
    if (all) return;
    current = Math.max(0, Math.min(slides.length - 1, Math.round(track.scrollLeft / track.clientWidth)));
    counter.textContent = `${current + 1} of ${slides.length}`;
    previous.disabled = current === 0;
    next.disabled = current === slides.length - 1;
  };
  const go = (index, behavior = motion()) => {
    current = Math.max(0, Math.min(slides.length - 1, index));
    track.scrollTo({left: current * track.clientWidth, behavior});
  };
  previous.addEventListener('click', () => go(current - 1));
  next.addEventListener('click', () => go(current + 1));
  track.addEventListener('scroll', () => {
    cancelAnimationFrame(frame);
    frame = requestAnimationFrame(update);
  }, {passive:true});
  track.addEventListener('keydown', event => {
    if (all || event.target !== track) return;
    const positions = {ArrowLeft:current - 1, ArrowRight:current + 1, Home:0, End:slides.length - 1};
    if (!(event.key in positions)) return;
    event.preventDefault();
    go(positions[event.key]);
  });
  view.addEventListener('click', () => {
    all = !all;
    gallery.classList.toggle('is-all', all);
    view.setAttribute('aria-pressed', String(all));
    view.textContent = all ? 'One at a time' : 'View all';
    for (const element of [previous, next, counter]) element.hidden = all;
    if (!all) go(current, 'instant');
  });
  new ResizeObserver(() => { if (!all) go(current, 'instant'); }).observe(track);
  controls.hidden = false;
  update();
  document.querySelector('[data-correction]').addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey || event.button) return;
    const contact = document.getElementById('contactopen');
    if (!contact) return;
    event.preventDefault();
    contact.click();
    const message = document.getElementById('contactmsg');
    if (message && !message.value) {
      message.value = 'Correction for ' + document.querySelector('link[rel="canonical"]').href + '\\n\\n';
      message.setSelectionRange(message.value.length, message.value.length);
    }
  });
})();
"""

TOKEN = re.compile(r"\{\{((?:checked|date|money|number):c\d+(?::\d+)?)\}\}")
LINK = re.compile(r"\[([^\]]+)\]\((c\d+)\)")
MONTHS = {name.lower(): index for index, name in enumerate(calendar.month_name) if name}
DATE = re.compile(r"\b(" + "|".join(MONTHS) + r")\s+(\d{1,2})(?:st|nd|rd|th)?,?\s+(\d{4})\b", re.I)


def _url(claim: dict) -> str:
    url = str(claim.get("url") or "")
    if urlsplit(url).scheme not in {"http", "https"} or not urlsplit(url).netloc:
        raise ValueError("An article claim needs an HTTP source URL")
    return url


def _expand(text: str, claims: dict) -> str:
    def token(match):
        key = match.group(1)
        kind, claim_id, *position = key.split(":")
        claim = claims[claim_id]
        if kind == "number":
            # Read a figure from the source quote, never from authored prose.
            figures = re.findall(r"(?<![\w])\d[\d,]*(?:\.\d+)?%?", claim["quote"])
            index = int(position[0]) if position else 0
            if index >= len(figures):
                raise ValueError(f"No quoted number {index} in {claim_id}")
            return figures[index]
        if position:
            raise ValueError("Only number tokens take an index")
        if kind == "checked":
            date = dt.date.fromisoformat(claim["retrieved"])
            return f"{ordinal(date)}, {date.year}"
        if kind == "date":
            found = DATE.search(claim["text"]) or DATE.search(claim.get("quote", ""))
            if not found:
                raise ValueError(f"No source date in {claim_id}")
            month, day, year = found.groups()
            date = dt.date(int(year), MONTHS[month.lower()], int(day))
            return f"{ordinal(date)}, {date.year}"
        found = re.search(r"\$([\d,]+(?:\.\d+)?)", claim["quote"])
        if not found:
            raise ValueError(f"No quoted amount in {claim_id}")
        raw = found.group(1)
        value = Decimal(raw.replace(",", ""))
        # THE SOURCE'S OWN PRECISION, READ OFF THE SOURCE. This was always `,.2f`, so a contract
        # the briefing states as $2,556,000 published as $2,556,000.00, and those cents were the
        # renderer's invention rather than the record's. numeral_lint caught it: the computed set
        # holds 2556000 and the page printed a figure the build never computed.
        #
        # The first fix was "drop the cents when the amount is whole" and it was wrong in the
        # other direction. 2026-09-18 quotes $19,200.00, whose cents ARE stated, and dropping
        # them invented a different precision and broke a page that had been passing. So the rule
        # is neither always two places nor never: it is however many places the quote itself
        # carries. A figure this project prints matches the document it came from.
        places = len(raw.partition(".")[2])
        return f"${value:,.{places}f}"
    expanded = TOKEN.sub(token, text)
    if "{{" in expanded or "}}" in expanded:
        raise ValueError("Unresolved article token")
    return expanded


def _block(block: dict, claims: dict, *, css: str = "") -> str:
    refs = block["claims"]
    if not refs or any(ref not in claims for ref in refs):
        raise ValueError("Every article paragraph must name existing claim ids")
    text = _expand(block["text"], claims)
    for match in TOKEN.finditer(block["text"]):
        if ":" in match.group(1) and match.group(1).split(":")[1] not in refs:
            raise ValueError("An article token must name one of the paragraph's claims")
    rendered, start = [], 0
    for match in LINK.finditer(text):
        label, ref = match.groups()
        if ref not in refs:
            raise ValueError("An article link must name one of the paragraph's claims")
        rendered.extend([html.escape(text[start:match.start()]),
                         f'<a href="{html.escape(_url(claims[ref]), quote=True)}" '
                         f'data-claim="{ref}" rel="noopener">{html.escape(label)}</a>'])
        start = match.end()
    rendered.append(html.escape(text[start:]))
    attr = f' class="{css}"' if css else ""
    return f'<p{attr} data-claims="{html.escape(" ".join(refs), quote=True)}">{"".join(rendered)}</p>'


def load_edition(run: dict) -> dict:
    if "edition" in run:  # Explicit fixture injection; production loads the committed input.
        return run["edition"]
    path = REPO_ROOT / "ledger" / "articles" / f'{run["date"]}.json'
    if not path.is_file():
        raise ValueError(f"Missing authored article {path.relative_to(REPO_ROOT)}")
    return json.loads(path.read_text("utf-8"))


def validate(run: dict, edition: dict) -> None:
    if edition.get("_spec", {}).get("version") != 1:
        raise ValueError("An article needs its versioned _spec envelope")
    claims = {claim["id"]: claim for claim in run["claims"]}
    if not claims or len(claims) != len(run["claims"]):
        raise ValueError("An article needs a nonempty, unique claim record")
    for claim in claims.values():
        _url(claim)
        dt.date.fromisoformat(claim["retrieved"])
    if not isinstance(edition.get("section"), str) or not edition["section"].strip():
        raise ValueError("An article needs a section")
    if not edition.get("introduction") or not edition.get("sections"):
        raise ValueError("An article needs a lead and narrative sections")
    blocks = [edition["dek"], *edition["introduction"]]
    for section in edition["sections"]:
        if not section.get("heading", "").strip() or not section.get("paragraphs"):
            raise ValueError("Article sections need headings and paragraphs")
        blocks.extend(section["paragraphs"])
    for block in blocks:
        if not block.get("text", "").strip():
            raise ValueError("Empty article paragraph")
        if re.search(r"first comment|link in bio|swipe (?:left|right|to)|sources below", block["text"], re.I):
            raise ValueError("Social-only directions don't belong in a web article")
        _block(block, claims)
    dek = LINK.sub(r"\1", _expand(edition["dek"]["text"], claims))
    if not 50 <= len(html.escape(dek, quote=True)) <= 200:
        raise ValueError("The article dek must fit the search description, 50 to 200 HTML characters")


def description(run: dict) -> str:
    edition = load_edition(run)
    claims = {claim["id"]: claim for claim in run["claims"]}
    return LINK.sub(r"\1", _expand(edition["dek"]["text"], claims))


def _sources(run: dict, edition: dict) -> tuple[str, str]:
    blocks = [edition["dek"], *edition["introduction"],
              *(block for section in edition["sections"] for block in section["paragraphs"])]
    cited = {ref for block in blocks for ref in block["claims"]}
    cited_urls = {_url(claim) for claim in run["claims"] if claim["id"] in cited}
    sources = {}
    for claim in run["claims"]:
        url = _url(claim)
        if url not in sources:
            sources[url] = {
                "title": claim.get("document") or claim.get("source_title") or claim.get("source_publisher") or urlsplit(url).hostname,
                # The archived first-party category includes universities, not only companies.
                "kind": {"primary_corporate": "First-party account", "secondary_reported": "Reported account",
                         "data": "Source data"}.get(claim.get("source_type"), "Primary source"),
            }
    rows = []
    for url, source in sources.items():
        if url not in cited_urls:
            continue
        rows.append(f'<li><cite><a href="{html.escape(url, quote=True)}" rel="noopener">'
                    f'{html.escape(source["title"])}</a></cite><span class="edition-source-meta">'
                    f'{html.escape(source["kind"])} · {html.escape(urlsplit(url).hostname)}</span></li>')
    verified = []
    for claim in run["claims"]:
        url = _url(claim)
        date = dt.date.fromisoformat(claim["retrieved"])
        # Preserve the exact quote after HTML decoding without raw trailing whitespace in
        # generated source. Do not strip or rewrite the historical evidence itself.
        quoted = html.escape(claim.get("quote") or "").replace("\r", "&#13;").replace("\n", "&#10;")
        quote = f'<blockquote>{quoted}</blockquote>' if quoted else ""
        verified.append(f'<li id="claim-{html.escape(claim["id"], quote=True)}">'
                        f'<p>{html.escape(claim["text"])}</p>{quote}'
                        f'<p class="meta" data-prose="data"><cite><a href="{html.escape(url, quote=True)}" '
                        f'rel="noopener">{html.escape(sources[url]["title"])}</a></cite>'
                        f' · Checked {ordinal(date)}, {date.year}</p></li>')
    return "".join(rows), "".join(verified)


def render(run: dict, today: str, items: list, edition: dict | None = None) -> str:
    if edition is None:
        edition = load_edition(run)
    validate(run, edition)
    claims = {claim["id"]: claim for claim in run["claims"]}
    by_id = {item["id"]: item for item in items}
    related = []
    for record in edition["related"]:
        if record["id"] not in by_id:
            raise ValueError(f'Unknown related Docket record {record["id"]}')
        related.append(f'<li><a href="../../item/{html.escape(record["id"], quote=True)}/">'
                       f'{html.escape(record["label"])}</a></li>')
    paragraphs = "".join(_block(block, claims, css="edition-lead" if index == 0 else "")
                         for index, block in enumerate(edition["introduction"]))
    for section in edition["sections"]:
        paragraphs += f'<h2>{html.escape(section["heading"])}</h2>'
        paragraphs += "".join(_block(block, claims) for block in section["paragraphs"])
    source_rows, verified_rows = _sources(run, edition)
    slides = []
    for index, filename in enumerate(run["files"]):
        prose = run.get("prose") or []
        text = " ".join(s["text"] for s in prose[index]) if index < len(prose) else run["title"]
        attrs = article_media.image_attrs(run, filename, 2)
        # Eager cover loading needs an explicit rendered width, not lazy-image sizes=auto.
        attrs = re.sub(r'sizes="[^"]*"', 'sizes="(max-width: 540px) calc(100vw - 48px), (max-width: 864px) 512px, 460px"', attrs)
        loading = 'loading="eager" fetchpriority="high"' if index == 0 else 'loading="lazy"'
        slides.append(f'<figure class="edition-slide" role="group" aria-label="Slide {index + 1} of {len(run["files"])}">'
                      f'<img {attrs} {loading} alt="{html.escape(text, quote=True)}"></figure>')
    date = dt.date.fromisoformat(run["date"])
    published = f"{ordinal(date)}, {date.year}"
    related_html = (f'<aside class="edition-records" aria-labelledby="edition-records-title">'
                    f'<h2 id="edition-records-title">Follow the record</h2>'
                    f'<ul data-prose="data">{"".join(related)}</ul></aside>') if related else ""
    body = f"""
<style>{CSS}</style>
<article class="article-edition" aria-labelledby="edition-title">
  <div class="edition-opening">
    <header class="edition-header">
      <p class="edition-kicker"><a href="../">Articles</a> · {html.escape(edition['section'])}</p>
      <h1 id="edition-title"{(' class="edition-title-long"' if len(run['title']) > 48 else '')}>{html.escape(run['title'])}</h1>
      {_block(edition['dek'], claims, css='edition-dek')}
      <p class="edition-byline" data-prose="data"><span>By <a href="../../about/">{SITE_NAME}</a></span>
        <time datetime="{run['date']}">{published}</time></p>
      <a class="edition-read" href="#story">Read the story <span aria-hidden="true">↓</span></a>
    </header>
    <figure class="edition-gallery" aria-label="Visual edition">
      <div class="edition-track" id="visual-edition" tabindex="0" role="region" aria-roledescription="carousel" aria-label="Visual edition slides">{''.join(slides)}</div>
      <figcaption class="edition-gallery-caption">
        <span class="edition-gallery-label">The visual edition</span>
        <div class="edition-controls" hidden>
          <button type="button" data-previous aria-label="Previous slide" aria-controls="visual-edition">←</button>
          <span class="edition-count" aria-live="polite" aria-atomic="true" data-prose="data">1 of {len(slides)}</span>
          <button type="button" data-next aria-label="Next slide" aria-controls="visual-edition">→</button>
          <button type="button" class="edition-view" data-view aria-pressed="false" aria-controls="visual-edition">View all</button>
        </div>
      </figcaption>
    </figure>
  </div>
  <div class="edition-reading">
    <div class="edition-story prose" id="story" tabindex="-1">{paragraphs}</div>
    {related_html}
    <section class="edition-sources" aria-labelledby="edition-sources-title">
      <h2 id="edition-sources-title">Sources for this story</h2>
      <ul class="edition-source-list" data-prose="data">{source_rows}</ul>
      <details class="edition-verified">
        <summary>Claim-by-claim verification <span data-prose="data">· {len(run['claims'])} claims</span></summary>
        <ol class="claims">{verified_rows}</ol>
      </details>
      <div class="edition-end"><a href="../">Every article</a>
        <a href="../../services/#start" data-correction>Suggest a correction</a></div>
    </section>
  </div>
</article>
<script>{SCRIPT}</script>
"""
    card = f'og/article-{run["date"]}.png'
    desc = LINK.sub(r"\1", _expand(edition["dek"]["text"], claims))
    article = schema.article_node(SCHEMA_CTX, run, desc, f"{SITE_URL}/{card}", None)
    article["articleSection"] = edition["section"]
    article["keywords"] = ["Texas", edition["section"], "artificial intelligence"]
    article["citation"] = list(dict.fromkeys(_url(claim) for claim in run["claims"]))
    article["about"] = [{"@id": f'{SITE_URL}/item/{record["id"]}/#report'} for record in edition["related"]]
    return page(title=f'{run["title"]} · {SITE_NAME}', desc=desc, body=body, depth=2,
                active="articles/", today=today, canonical=f'articles/{run["date"]}/',
                og_image=card, og_alt=run["title"], og_type="article",
                extra_ld=[article, schema.breadcrumbs(SCHEMA_CTX, [
                    (SITE_NAME, ""), ("Articles", "articles/"),
                    (run["title"], f'articles/{run["date"]}/')])])
