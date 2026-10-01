"""A bounded public-source index. No model, upload, backend or regulatory decision.

The selected source locations live in a separate reviewed fixture. All visible figures are
derived from that fixture. Browser review state is ephemeral and never means compliance.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "ledger/demos/msgp_document_index.json"
CSS = Path(__file__).with_suffix(".css")
JS = Path(__file__).with_suffix(".js")


def load() -> dict:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    validate(data)
    return data


def validate(data: dict) -> None:
    for key in ("source_url", "status_url"):
        url = urlparse(data[key])
        if url.scheme != "https" or url.hostname != "www.tceq.texas.gov":
            raise ValueError("Document demo sources must be official HTTPS TCEQ links")
    for key in ("effective", "verified"):
        dt.date.fromisoformat(data[key])
    seen = set()
    for row in data["entries"]:
        if not re.fullmatch(r"[a-z]+(?:-[a-z]+)*", row["id"]) or row["id"] in seen:
            raise ValueError("Document demo IDs must be unique and safe")
        seen.add(row["id"])
        if not re.fullmatch(r"III\.[ADE]\.\d+", row["section"]):
            raise ValueError("Document demo section is invalid")
        if not row["pages"] or row["pages"] != sorted(set(row["pages"])):
            raise ValueError("Document demo page ranges must be ordered")
        if any(type(p) is not int or not 1 <= p <= data["pdf_pages"] for p in row["pages"]):
            raise ValueError("Document demo page is outside the source PDF")
        for key in ("title", "source_heading", "summary", "question", "category"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError("Document demo copy is missing")
    if not seen:
        raise ValueError("Document demo needs source entries")


def authorised(data: dict) -> set:
    """Source identifiers, dates, page locations and index size are data-derived."""
    values = set(re.findall(r"\d+", json.dumps(data, ensure_ascii=False)))
    values.update(str(n) for n in range(len(data["entries"]) + 1))
    # Ordinal date formatting does not retain an ISO date's leading zero.
    for key in ("effective", "verified"):
        day = dt.date.fromisoformat(data[key])
        values.update((str(day.year), str(day.month), str(day.day)))
    return values


def render(today: str) -> tuple[str, set]:
    from site_context import e, ordinal, page, SITE_NAME
    data = load()
    rows = []
    for row in data["entries"]:
        rid = row["id"]
        pages = " to ".join(str(p) for p in row["pages"])
        search = " ".join([row["title"], row["section"], row["source_heading"],
                           row["category"], row["summary"], *row["keywords"]])
        rows.append(f'''<article class="di-entry" data-entry="{e(rid)}"
            data-category="{e(row['category'])}" data-search="{e(search)}">
          <div class="di-entry-top"><span class="di-section" data-prose="data">{e(row['section'])}</span>
            <span class="di-status" data-status-label>Needs review</span></div>
          <h3>{e(row['title'])}</h3>
          <p>{e(row['summary'])}</p>
          <div class="di-source"><span class="di-source-label">Source passage</span>
            <a href="{e(data['source_url'])}#page={row['pages'][0]}" target="_blank" rel="noopener"
              data-source-link data-prose="data">{e(row['source_heading'])}<span>Page {pages} <span aria-hidden="true">PDF</span>
              <span class="vh">opens PDF in a new tab</span></span></a></div>
          <details><summary>What a reviewer still needs to decide</summary><p>{e(row['question'])}</p></details>
          <div class="di-review" data-enhanced hidden><label for="review-{e(rid)}">Your review of this passage</label>
            <select id="review-{e(rid)}" data-review>
              <option value="needs-review">Needs review</option>
              <option value="question">Question for reviewer</option>
              <option value="reviewed">Reviewed in this session</option>
            </select></div>
        </article>''')
    options = "".join(f'<option value="{e(cat)}">{e(cat)}</option>'
                      for cat in dict.fromkeys(r["category"] for r in data["entries"]))
    effective = ordinal(dt.date.fromisoformat(data["effective"]))
    verified = ordinal(dt.date.fromisoformat(data["verified"]))
    version = hashlib.sha256(JS.read_bytes()).hexdigest()[:10]
    body = f'''
<section class="hero rise di-hero">
  <p class="di-eyebrow">Field Study / Working example</p>
  <h1>Find the source.<br><em>Keep the judgement.</em></h1>
  <p class="herolede">A document workflow you can inspect. Find a passage, open the source
    and leave the decision with a named reviewer.</p>
  <div class="ctarow"><a class="cta solid" href="#index">Try the index</a>
    <a class="cta ghost" href="../#field-study">See the paid pilot</a></div>
</section>
<section class="di-workspace" id="index" aria-labelledby="index-title">
  <div class="di-workspace-head"><div><p class="di-eyebrow">Public-source document index</p>
    <h2 id="index-title">From the permit to the passage</h2></div>
    <p class="di-local">Curated sample · Runs in this page</p></div>
  <div class="di-provenance" data-prose="data">
    <div><span class="di-source-label">Source document</span><strong>{e(data['source_title'])}</strong>
      <span>{e(data['permit'])} · Effective {e(effective)}</span></div>
    <div class="di-measure"><strong>{data['pdf_pages']}</strong><span>source pages</span></div>
    <div class="di-measure"><strong>{len(data['entries'])}</strong><span>selected passages</span></div>
    <a href="{e(data['status_url'])}" target="_blank" rel="noopener">Check the current permit
      <span class="vh">opens TCEQ in a new tab</span></a>
  </div>
  <p class="di-boundary">This example locates selected passages. It is not a complete permit
    summary and does not determine site requirements or compliance. No facility records are included.</p>
  <div class="di-controls" data-enhanced hidden>
    <div class="di-search"><label for="di-query">Find a topic or section</label>
      <input id="di-query" type="search" placeholder="Try retention, SWP3 or calibration"
        autocomplete="off" spellcheck="false" data-voice="off" aria-describedby="di-search-help"></div>
    <div><label for="di-category">Topic</label><select id="di-category"><option value="">All topics</option>{options}</select></div>
    <div><label for="di-status">Review state</label><select id="di-status">
      <option value="">All passages</option><option value="needs-review">Needs review</option>
      <option value="question">Question for reviewer</option><option value="reviewed">Reviewed in this session</option>
    </select></div>
    <p id="di-search-help">Search matches words in this small curated index. It does not search the full PDF or generate answers.</p>
    <div class="di-suggestions" aria-label="Example searches"><span>Try</span>
      <button type="button" data-example="correspondence">Supporting records</button>
      <button type="button" data-example="retention">Retention</button>
      <button type="button" data-example="revision">Plan revisions</button>
      <button type="button" data-example="calibration">Calibration</button>
      <button type="button" id="di-clear">Clear filters</button></div>
  </div>
  <noscript><p>The full sample index and source links work without JavaScript. Enable JavaScript for filtering and session review controls.</p></noscript>
  <div class="di-progress" data-enhanced hidden><p id="di-count" role="status" aria-live="polite" aria-atomic="true"></p>
    <p id="di-review-count"></p><button type="button" id="di-reset">Reset review</button></div>
  <p id="di-empty" class="di-empty" hidden>Not found in this sample index. That does not mean a record or requirement is absent.
    Clear the filters or <a href="{e(data['source_url'])}" target="_blank" rel="noopener">read the full permit</a>.</p>
  <div class="di-results">{''.join(rows)}</div>
  <p class="di-session-note">Search and review choices stay in this page. Reloading resets them. No upload or account is needed.
    A review label records your interaction with the example. It is not a regulatory finding.</p>
  <p class="di-verified" data-prose="data">Source locations checked {e(verified)}. Open the official source to confirm its current wording.
    PDF page links depend on your viewer. Printed page numbers are provided beside each passage.</p>
</section>
<section class="di-next">
  <div><p class="di-eyebrow">A useful next step</p><h2>Try the same discipline<br>on your own workflow.</h2>
    <p>The paid Field Study starts with an approved document packet, a defined task and a named reviewer.
    Success is tested against your team's real questions and baseline time.</p></div>
  <a class="cta solid" href="../#start">Discuss one workflow</a>
</section>
<script src="../../document-demo.js?v={version}" defer></script>
'''
    return page(title=f"Document workflow demo · {SITE_NAME}",
                desc="Try a source-linked document index with selected TCEQ permit passages. "
                     "Search topics, open the official source and try a human review queue.",
                body=body, depth=2, active="services/", today=today,
                canonical="services/document-demo/", extra_css="document-demo.css"), authorised(data)
