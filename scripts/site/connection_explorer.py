"""A touch-first, source-linked network built from individual certification rows.

The overview reuses the publication's deterministic layout. The focused view gives
each name its own generous control. It pages neighbors explicitly instead of hiding
companies behind overlapping labels or suggesting that a partial view is the whole
network. No third-party runtime or account is required by a reader.
"""
from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from itertools import combinations

import entities
import facility_dossier
import registry_graph
from flourish_registry import record_id

PAGE_SIZE = 4
ARROW = ('<svg class="cearrow" viewBox="0 0 16 16" aria-hidden="true">'
         '<path d="M3 13L13 3M4 3h9v9" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>')


def build(data: dict, dossiers: dict | None = None) -> dict:
    nodes = [{"key": item["key"], "name": item["name"], "slug": item["slug"],
              "reach": item["reach"], "roles": {r: len(v) for r, v in item["roles"].items()}}
             for item in data["entities"] if item["reach"] >= entities.MIN_REACH]
    keys = {node["key"] for node in nodes}
    if dossiers is None:
        dossiers = facility_dossier.by_name(facility_dossier.load())
    by_pair = defaultdict(list)
    # Facility names can recur in different certifications with different parties.
    # Only the SAME row creates a connection. The record ID also opens that exact
    # certification in the explorer below, rather than a similarly named record.
    for row in sorted(data["facilities"], key=lambda r: (r["name"].casefold(), r["effective"])):
        members = {entities.normalise(raw) for role in entities.ROLES for raw in row.get(role, [])}
        dossier = dossiers.get(row["name"])
        record = {"id": record_id(row), "n": row["name"],
                  "d": entities.ordinal_date(row["effective"]),
                  "u": f"../facility/{dossier['slug']}/" if dossier else ""}
        for pair in combinations(sorted(members & keys), 2):
            by_pair[pair].append(record)
    edges = [{"a": a, "b": b, "w": len({r["n"] for r in rows}), "f": rows}
             for (a, b), rows in by_pair.items()]
    edges.sort(key=lambda edge: (-edge["w"], edge["a"], edge["b"]))
    graph = registry_graph.layout({"nodes": nodes, "edges": edges})
    for node in nodes:
        node["u"] = f"../company/{node['slug']}/"
        node["short"] = re.sub(r"[,\s]+(?:LLC|L\.L\.C\.|Inc\.?|Corporation|LTD|L\.P\.)$",
                               "", node["name"], flags=re.I).strip()
    default = next((n for n in nodes if n["key"] == entities.normalise("Lancium Abilene LLC")),
                   nodes[0] if nodes else None)
    graph["initial"] = default["key"] if default else ""
    graph["page_size"] = PAGE_SIZE
    return graph


def authorised(data: dict) -> set[str]:
    graph = build(data)
    return {entities.n0(value) for value in
            [len(graph["nodes"]), len(graph["edges"]), PAGE_SIZE]
            + [node["reach"] for node in graph["nodes"]]
            + [edge["w"] for edge in graph["edges"]]
            + [sum(node["key"] in (e["a"], e["b"]) for e in graph["edges"])
               for node in graph["nodes"]]}


def render(data: dict) -> str:
    graph = build(data)
    if not graph["nodes"]:
        return ""
    esc, n0 = html.escape, entities.n0
    at = {node["key"]: node for node in graph["nodes"]}
    initial = at[graph["initial"]]
    seeds = []
    for name in ("Lancium Abilene LLC", "Google LLC", "Riot Platforms Inc", "Microsoft Corporation"):
        node = at.get(entities.normalise(name))
        if node:
            seeds.append(f'<button type="button" class="ceseed" data-key="{esc(node["key"], quote=True)}"'
                         f' aria-pressed="{"true" if node == initial else "false"}">'
                         f'<cite>{esc(node["short"])}</cite></button>')
    fallback = "".join(f'<li><a href="{esc(node["u"], quote=True)}"><cite>{esc(node["name"])}</cite></a>'
                       f'<span>{n0(node["reach"])} facility names</span></li>' for node in graph["nodes"])
    payload = json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return (
        '<section class="ce" id="registry-field" aria-labelledby="registry-field-title">'
        '<header class="cehead"><span class="sectioneyebrow">The company network</span>'
        '<h2 id="registry-field-title">Follow the names<br>behind the buildout.</h2>'
        '<p>See where companies meet in the state filings. Follow a connection all the way '
        'to the record that puts them together.</p></header>'
        '<div class="ceinteractive" hidden>'
        '<div class="cetools"><div class="cesearch"><label for="gsearch">Find a company</label>'
        '<input id="gsearch" type="search" placeholder="Search the network" autocomplete="off" '
        'aria-controls="ceresults" aria-expanded="false">'
        '<div class="ceresults" id="ceresults" hidden></div></div>'
        '<button class="cemode" id="cemode" type="button" aria-pressed="false">Whole network '
        + ARROW + '</button></div>'
        '<div class="ceseeds" aria-label="Companies to start with">' + "".join(seeds) + '</div>'
        '<div class="ceworkspace"><div class="cecanvas">'
        '<header class="cecanvashead"><div><span class="sectioneyebrow" id="ceviewlabel">Company in focus</span>'
        f'<h3 id="cename"><cite>{esc(initial["name"])}</cite></h3></div>'
        f'<a id="ceprofile" href="{esc(initial["u"], quote=True)}">Company profile '
        + ARROW + '</a></header>'
        '<div class="ceplot" id="ceplot" role="group" aria-label="Company connections">'
        '<svg class="celines" id="celines" viewBox="0 0 400 400" preserveAspectRatio="none" aria-hidden="true"></svg>'
        '<div id="cenodes"></div></div>'
        '<div class="ceplotfoot"><p id="cescope" aria-live="polite"></p>'
        '<div class="cepaging" id="cepaging" hidden>'
        '<button id="ceprev" type="button" aria-label="Previous connections">←</button>'
        '<button id="cenext" type="button" aria-label="Next connections">→</button></div></div>'
        '<p class="cegesture" id="cegesture">Tap a company to read its shared records.</p></div>'
        '<aside class="ceinspector" aria-label="Connection evidence">'
        '<span class="sectioneyebrow">Behind the connection</span>'
        '<div id="cereadout" aria-live="polite"></div></aside></div>'
        '<dialog class="cesheet" id="cesheet" aria-labelledby="cesheettitle">'
        '<header><h3 id="cesheettitle">Connection evidence</h3>'
        '<button id="cesheetclose" type="button" aria-label="Close connection">×</button></header>'
        '<div class="ceinspector cesheetbody"></div></dialog>'
        '<div class="celegend"><p><span class="cekeydot" aria-hidden="true"></span>'
        'Larger points appear at more facilities</p><p><span class="cekeyline" aria-hidden="true"></span>'
        'Heavier lines share more facility names</p></div></div>'
        '<details class="cemethod"><summary>Read the network</summary>'
        f'<p data-prose="data">{n0(len(graph["nodes"]))} companies. {n0(len(graph["edges"]))} connections. '
        'A company enters this view when it is named at more than one facility. A line requires '
        'both companies on the same certification row. Point area and line weight follow distinct '
        'facility names. Separate certifications remain separate records.</p>'
        '<p>Names are matched across case, punctuation and corporate suffixes. A connection '
        'does not establish corporate control. Positions show relationships, not geography.</p>'
        '<p><a href="https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php" '
        'target="_blank" rel="noopener">Read the state registry ' + ARROW + '</a></p></details>'
        '<div class="cefallback"><p>Follow a company to every certified facility that names it.</p>'
        f'<ul data-prose="data">{fallback}</ul></div>'
        f'<script type="application/json" id="cedata">{payload}</script>'
        f'<style>{STYLE}</style><script>{SCRIPT}</script></section>')


STYLE = """
.ce { scroll-margin-top:6rem; margin:clamp(2.5rem,6vw,5rem) 0; --ce-line:color-mix(in srgb,var(--accent) 42%,transparent); }
.ce cite { font-style:normal; }
.cearrow { width:.9em; height:.9em; display:inline-block; flex-shrink:0; vertical-align:middle; }
.cehead { margin-bottom:1.5rem; max-width:49rem; }
.cehead h2 { font-size:clamp(2.3rem,5vw,4.9rem); letter-spacing:-.045em; line-height:1.02;
  margin:.55rem 0 1rem; font-weight:650; }
.cehead p { margin:0; color:var(--caliche); max-width:38rem; line-height:1.65; }
.ce [hidden] { display:none!important; }
.cetools { display:flex; align-items:end; gap:1rem; }
.cesearch { position:relative; flex:1; min-width:0; }
.cesearch label { display:block; font:var(--s-2) var(--mono); color:var(--dust); margin-bottom:.45rem; }
.cesearch input { box-sizing:border-box; width:100%; min-width:0; min-height:3rem; border-radius:.3rem;
  border:1px solid var(--rule-strong); padding:.7rem 3rem .7rem .85rem; color:var(--limestone);
  background:var(--panel); font:1rem var(--body); }
.ce button { font-family:var(--body); cursor:pointer; }
.cemode { display:flex; align-items:center; justify-content:space-between; gap:1rem; min-height:3rem;
  padding:.6rem 1rem; border:1px solid var(--rule-strong); border-radius:.3rem;
  background:transparent; color:var(--limestone); font-size:.93rem; }
.cemode span { color:var(--accent); }
.ceseeds { display:flex; gap:.5rem; flex-wrap:wrap; padding:.85rem 0 1.2rem; }
.ceseed { border:1px solid var(--rule); border-radius:2rem; padding:.55rem .9rem;
  min-height:2.75rem; background:transparent; color:var(--caliche); font-size:.85rem; }
.ceseed[aria-pressed=true] { background:var(--accent); color:var(--night); border-color:var(--accent); }
.ceresults { position:absolute; inset:calc(100% + .3rem) 0 auto; z-index:5; max-height:20rem;
  overflow:auto; background:var(--panel); border:1px solid var(--rule-strong); border-radius:.4rem;
  box-shadow:0 12px 30px color-mix(in srgb,var(--night) 85%,transparent); }
.ceresults button { display:flex; width:100%; text-align:left; justify-content:space-between;
  gap:1rem; border:0; border-bottom:1px solid var(--rule); padding:.85rem; min-height:3rem;
  background:transparent; color:var(--limestone); line-height:1.45; }
.ceresults button:hover, .ceresults button:focus { background:var(--raised); }
.ceresults small { color:var(--dust); white-space:nowrap; }
.ceresults p { padding:1rem; margin:0; color:var(--dust); }
.ceworkspace { display:grid; grid-template-columns:minmax(0,1.5fr) minmax(18rem,1fr);
  border:1px solid var(--rule-strong); border-radius:.6rem; overflow:hidden; }
.cecanvas { scroll-margin-top:6rem; min-width:0; background:var(--night); }
.cecanvashead { display:flex; justify-content:space-between; align-items:start; gap:1rem;
  padding:1.3rem 1.4rem 0; min-height:6.5rem; }
.cecanvashead h3 { margin:.45rem 0 0; font-size:clamp(1.15rem,2vw,1.6rem); line-height:1.25; }
.cecanvashead > a { flex-shrink:0; font-size:.78rem; line-height:1.4; color:var(--accent);
  min-height:2.75rem; display:flex; gap:.35rem; align-items:center; text-underline-offset:.25em; }
.ceplot { position:relative; margin:.2rem 0 0; isolation:isolate;
  background-image:radial-gradient(circle,color-mix(in srgb,var(--caliche) 10%,transparent) .7px,transparent .9px);
  background-size:24px 24px; }
.ceplot::before { content:""; position:absolute; width:58%; aspect-ratio:1; border-radius:50%;
  border:1px solid var(--rule); left:50%; top:50%; transform:translate(-50%,-50%); z-index:-1; }
.celines { width:100%; height:100%; position:absolute; inset:0; overflow:visible; }
.celines path { fill:none; stroke:var(--ce-line); vector-effect:non-scaling-stroke;
  transition:stroke .2s,opacity .2s; }
.celines path.picked { stroke:var(--accent); }
.celines path.secondary { stroke:var(--caliche); opacity:.2; }
.cenode { position:absolute; transform:translateX(-50%); width:43%; max-width:12rem;
  min-height:3rem; padding:.25rem; background:transparent; border:0; border-radius:.4rem;
  color:var(--limestone); display:flex; flex-direction:column; align-items:center; gap:.45rem;
  z-index:1; -webkit-tap-highlight-color:transparent; }
.cenode:focus-visible { outline:2px solid var(--accent); outline-offset:3px; }
.cedot { display:grid; place-items:center; width:var(--diameter); height:var(--diameter);
  flex-shrink:0; background:var(--night); border:1.5px solid var(--accent); border-radius:50%;
  transition:background .2s,box-shadow .2s; }
.cenode:hover .cedot, .cenode[aria-pressed=true] .cedot { background:var(--accent);
  box-shadow:0 0 0 6px color-mix(in srgb,var(--accent) 12%,transparent); }
.cenodelabel { display:block; font-size:.8rem; line-height:1.35; max-width:100%;
  background:var(--night); padding:.1rem .25rem; overflow-wrap:anywhere; }
.cenode small { display:block; color:var(--dust); font: .67rem var(--mono); }
.cenode.center { width:38%; pointer-events:none; }
.cenode.center .cedot { background:var(--accent); color:var(--night); font:600 1.1rem var(--mono);
  box-shadow:0 0 0 7px color-mix(in srgb,var(--accent) 10%,transparent),0 0 0 18px color-mix(in srgb,var(--accent) 4%,transparent); }
.cenode.center .cenodelabel { font-weight:600; }
.ceplot:not(.overview) #cenodes { display:grid; grid-template-columns:repeat(2,minmax(0,1fr));
  grid-template-rows:auto auto auto; align-content:space-between; justify-items:center;
  min-height:420px; gap:1.3rem 1rem; padding:1.2rem .75rem; }
.ceplot:not(.overview) .cenode { position:relative; top:auto!important; left:auto!important;
  transform:none; width:100%; max-width:12rem; align-self:start; }
.ceplot:not(.overview) .cenode.center { grid-row:2; grid-column:1 / -1; width:38%; }
.ceplot:not(.overview) .cenode:nth-child(2) { grid-row:1; grid-column:1; }
.ceplot:not(.overview) .cenode:nth-child(3) { grid-row:1; grid-column:2; }
.ceplot:not(.overview) .cenode:nth-child(4) { grid-row:3; grid-column:1; }
.ceplot:not(.overview) .cenode:nth-child(5) { grid-row:3; grid-column:2; }
.ceplot.overview { height:430px; }
.ceplot.overview::before { display:none; }
.ceplot.overview .cenode { width:28px; height:28px; min-height:28px; padding:0; }
.ceplot.overview .cenodelabel { position:absolute; bottom:calc(100% + .4rem); width:max-content;
  max-width:11rem; padding:.45rem .6rem; border:1px solid var(--rule-strong); border-radius:.3rem;
  opacity:0; pointer-events:none; }
.ceplot.overview .cenode.hovered, .ceplot.overview .cenode:focus-visible { z-index:3; }
.ceplot.overview .cenode.hovered .cenodelabel, .ceplot.overview .cenode:focus-visible .cenodelabel { opacity:1; }
.ceplot.overview .cedot { background:var(--accent); opacity:.85; }
.ceplotfoot { display:flex; align-items:center; justify-content:space-between; gap:.5rem;
  min-height:3rem; padding:.4rem 1.3rem 0; }
.ceplotfoot p { margin:0; font:.74rem var(--mono); color:var(--caliche); line-height:1.5; }
.cepaging { display:flex; gap:.4rem; }
.cepaging button { min-width:2.75rem; min-height:2.75rem; border:1px solid var(--rule-strong);
  color:var(--limestone); background:var(--panel); border-radius:.3rem; font-size:1.2rem; }
.cepaging button:disabled { opacity:.3; cursor:default; }
.cegesture { margin:.5rem 1.3rem 1.2rem!important; font-size:.76rem; color:var(--dust); }
.ceinspector { padding:1.5rem; background:var(--panel); border-left:1px solid var(--rule-strong); min-width:0; }
.cesheet { position:fixed; inset:auto 0 0; margin:0 auto; width:100%; max-width:34rem;
  max-height:85dvh; padding:0; border:1px solid var(--rule-strong); border-radius:1rem 1rem 0 0;
  background:var(--panel); color:var(--limestone); overscroll-behavior:contain; }
.cesheet::backdrop { background:color-mix(in srgb,var(--night) 75%,transparent); backdrop-filter:blur(3px); }
.cesheet > header { position:sticky; top:0; z-index:1; display:flex; align-items:center;
  justify-content:space-between; gap:1rem; padding:.65rem 1.2rem; background:var(--panel);
  border-bottom:1px solid var(--rule-strong); }
.cesheet > header h3 { margin:0; font:500 .78rem var(--mono); color:var(--dust); }
.cesheet > header button { min-width:2.75rem; min-height:2.75rem; color:var(--limestone);
  border:1px solid var(--rule-strong); border-radius:50%; background:transparent; font-size:1.5rem; }
.cesheet .cesheetbody { border:0; padding-top:.6rem; }
.ceinspector h4 { font-size:clamp(1.25rem,2vw,1.65rem); line-height:1.25; margin:.65rem 0 1rem; }
.cereadpair { display:block; font-size:.8rem; color:var(--dust); margin-bottom:.5rem; }
.ceinspector p { font-size:.88rem; color:var(--caliche); line-height:1.6; }
.ceinspector .cebig { font:500 clamp(2.8rem,5vw,4.5rem) var(--body); letter-spacing:-.05em;
  color:var(--accent); line-height:1; display:block; }
.cemetric { margin:0 0 1.1rem!important; }
.cemetric span + span { display:block; margin-top:.4rem; color:var(--dust); font:.73rem var(--mono); }
.cefollow { display:block; width:100%; text-align:left; border:1px solid var(--rule-strong);
  border-radius:.3rem; color:var(--limestone); background:transparent; padding:.8rem .9rem;
  min-height:3rem; font-size:.86rem; line-height:1.45; margin:1rem 0; }
.cefollow span { color:var(--accent); }
.cerecords { margin:1.1rem 0 0; padding:0; list-style:none; }
.cerecords li { border-top:1px solid var(--rule); padding:.8rem 0; }
.cerecords cite { font-size:.88rem; line-height:1.4; display:block; }
.cerecords small { display:block; color:var(--dust); font:.68rem var(--mono); margin:.4rem 0; }
.cerecords button, .cerecords a { display:inline-flex; align-items:center; min-height:2.75rem;
  padding:.4rem 0; margin-right:1rem; font-size:.76rem; line-height:1.3; color:var(--accent);
  border:0; background:transparent; text-decoration:underline; text-underline-offset:.25em; }
.cerecordmore { margin-top:.75rem; color:var(--caliche); font-size:.82rem; }
.cerecordmore summary { min-height:2.75rem; cursor:pointer; padding:.5rem 0; }
.celegend { display:flex; flex-wrap:wrap; gap:.3rem 1.5rem; padding:.8rem 0; }
.celegend p { display:flex; align-items:center; gap:.5rem; margin:0; font:.7rem var(--mono); color:var(--dust); }
.cekeydot { width:.6rem; height:.6rem; border:1px solid var(--accent); border-radius:50%; }
.cekeyline { width:1.1rem; border-top:2px solid var(--accent); }
.cemethod { color:var(--dust); font-size:.85rem; }
.cemethod summary { min-height:2.75rem; cursor:pointer; padding:.6rem 0; }
.cemethod p { max-width:50rem; line-height:1.65; }
.cefallback ul { list-style:none; padding:0; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:.8rem; }
.cefallback li { border-bottom:1px solid var(--rule); padding:.75rem 0; }
.cefallback span { display:block; color:var(--dust); font-size:.85rem; }
@media(max-width:55rem) {
  .ceworkspace { grid-template-columns:1fr; }
  .cecanvashead { padding:1.1rem 1rem 0; min-height:6rem; }
  .cecanvashead > a { max-width:5rem; }
  .ceinspector { border-left:0; border-top:1px solid var(--rule-strong); padding:1.2rem; }
  .ceplot:not(.overview) #cenodes { min-height:390px; }
  .ceplot.overview { height:390px; }
  .ceplotfoot { padding:.4rem 1rem 0; }
  .cegesture { margin:.5rem 1rem 1rem!important; }
  .cenodelabel { font-size:.76rem; }
  .ceinspector .cebig { font-size:3rem; }
  .ceinspector h4 { font-size:1.4rem; }
}
@media(max-width:30rem) {
  .cetools { gap:.6rem; align-items:stretch; flex-direction:column; }
  .cemode { min-height:2.75rem; }
  .ceseeds { gap:.4rem; }
  .ceseed { padding:.5rem .75rem; font-size:.78rem; }
  .ceplot:not(.overview) #cenodes { gap:1.1rem .5rem; }
  .cenode.center { width:35%; }
  .cenode small { font-size:.61rem; }
  .cecanvashead .sectioneyebrow { font-size:.65rem; }
  .cecanvashead h3 { font-size:1.12rem; }
  .celegend { flex-direction:column; gap:.6rem; }
  .cefallback ul { grid-template-columns:1fr; }
}
@media(prefers-reduced-motion:reduce) { .ce *, .ce *::before { transition:none!important; animation:none!important; } }
"""


SCRIPT = r"""
(function () {
  'use strict';
  var root = document.getElementById('registry-field'), raw = document.getElementById('cedata');
  if (!root || !raw) return;
  var data;
  try { data = JSON.parse(raw.textContent); } catch (_) { return; }
  if (!data.nodes.length) return;
  var at = {}, selected = data.initial, offset = 0, overview = false, picked = null;
  data.nodes.forEach(function (n) { at[n.key] = n; });
  var plot = document.getElementById('ceplot'), nodes = document.getElementById('cenodes');
  var lines = document.getElementById('celines'), readout = document.getElementById('cereadout');
  var input = document.getElementById('gsearch'), results = document.getElementById('ceresults');
  var sheet = document.getElementById('cesheet'), inspector = root.querySelector('.ceworkspace .ceinspector');
  var phone = window.matchMedia('(max-width:55rem)');
  var previousOverflow = '';
  function restoreReadout() {
    if (readout.parentElement === inspector) return;
    inspector.appendChild(readout); inspector.style.minHeight = '';
    document.documentElement.style.overflow = previousOverflow;
  }
  function closeSheet() {
    if (!sheet.open) return;
    sheet.close();
    // Restore layout before a follow or certification action calculates its scroll target.
    // The native close event is queued, which is too late when the evidence has expanded.
    restoreReadout();
  }
  sheet.addEventListener('close', restoreReadout);
  document.getElementById('cesheetclose').addEventListener('click', closeSheet);
  sheet.addEventListener('click', function (event) { if (event.target === sheet) closeSheet(); });
  phone.addEventListener('change', function () { if (!phone.matches) closeSheet(); });
  function openSheet() {
    if (!phone.matches || !sheet.showModal) return;
    inspector.style.minHeight = inspector.getBoundingClientRect().height + 'px';
    sheet.querySelector('.cesheetbody').appendChild(readout);
    previousOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    sheet.showModal();
    document.getElementById('cesheetclose').focus({preventScroll:true});
  }
  var maxReach = Math.max.apply(null, data.nodes.map(function (n) { return n.reach; }));
  function drawLines() {
    var box = plot.getBoundingClientRect(), positions = {};
    if (!box.width || !box.height) return;
    nodes.querySelectorAll('.cenode').forEach(function (node) {
      var dot = node.querySelector('.cedot').getBoundingClientRect();
      positions[node.dataset.key] = [(dot.left + dot.width / 2 - box.left) / box.width * 400,
        (dot.top + dot.height / 2 - box.top) / box.height * 400];
    });
    lines.replaceChildren();
    data.edges.forEach(function (edge) {
      var a = positions[edge.a], b = positions[edge.b];
      if (!a || !b) return;
      var line = document.createElementNS(lines.namespaceURI,'path');
      line.setAttribute('d', 'M' + a[0] + ',' + a[1] + ' L' + b[0] + ',' + b[1]);
      line.setAttribute('stroke-width', String(.8 + Math.sqrt(edge.w) * .55));
      if (edge === picked && !overview) line.classList.add('picked');
      if (!overview && edge.a !== selected && edge.b !== selected) line.classList.add('secondary');
      lines.appendChild(line);
    });
  }
  function el(tag, cls, text) {
    var item = document.createElement(tag); if (cls) item.className = cls;
    if (text !== undefined) item.textContent = text; return item;
  }
  function adjacent(key) { return data.edges.filter(function (e) { return e.a === key || e.b === key; }); }
  function other(edge) { return at[edge.a === selected ? edge.b : edge.a]; }
  function link(text, href) {
    var a = el('a', '', text.replace('↗', '').trim() + ' '); a.setAttribute('href', href);
    var svg = document.createElementNS(lines.namespaceURI,'svg');
    svg.setAttribute('viewBox','0 0 16 16'); svg.setAttribute('class','cearrow'); svg.setAttribute('aria-hidden','true');
    var path = document.createElementNS(lines.namespaceURI,'path');
    path.setAttribute('d','M3 13L13 3M4 3h9v9'); path.setAttribute('fill','none');
    path.setAttribute('stroke','currentColor'); path.setAttribute('stroke-width','1.5');
    svg.appendChild(path); a.appendChild(svg); return a;
  }
  function evidence(edge) {
    picked = edge;
    readout.replaceChildren();
    var company = at[selected], next = edge && other(edge), heading = el('h4');
    heading.appendChild(el('span', 'cereadpair', company.name));
    heading.appendChild(el('cite', '', next ? next.name : 'Where this company appears'));
    readout.appendChild(heading);
    var metric = el('p', 'cemetric');
    metric.appendChild(el('strong', 'cebig', String(edge ? edge.w : company.reach)));
    metric.appendChild(el('span', '', edge ? (edge.w === 1 ? 'shared facility name' : 'shared facility names') : 'distinct facility names'));
    readout.appendChild(metric);
    if (!edge) {
      readout.appendChild(el('p', '', 'No certification row connects this company to another repeat company. Its full profile lists every facility and filed role.'));
      readout.appendChild(link('Open the company profile ↗', company.u));
      return;
    }
    readout.appendChild(el('p', '', 'The same certification names both companies. Open a record to see their filed roles.'));
    var follow = el('button', 'cefollow'); follow.type = 'button';
    follow.appendChild(el('span', '', 'Follow this company → '));
    follow.appendChild(el('cite', '', next.name));
    follow.addEventListener('click', function () { closeSheet(); focus(next.key, true); }); readout.appendChild(follow);
    function rows(items) {
      var list = el('ul', 'cerecords');
      items.forEach(function (record) {
        var row = el('li'); row.appendChild(el('cite', '', record.n));
        row.appendChild(el('small', '', 'Took effect ' + record.d));
        var inspect = el('button', '', 'Read filed roles'); inspect.type = 'button';
        inspect.dataset.record = record.id;
        inspect.addEventListener('click', function () {
          closeSheet();
          root.dispatchEvent(new CustomEvent('certification-select', {bubbles:true, detail:{id:record.id}}));
        }); row.appendChild(inspect);
        if (record.u) row.appendChild(link('Facility dossier ↗', record.u));
        list.appendChild(row);
      });
      return list;
    }
    readout.appendChild(rows(edge.f.slice(0, 2)));
    if (edge.f.length > 2) {
      var more = el('details', 'cerecordmore');
      more.appendChild(el('summary', '', 'Show all ' + edge.f.length + ' certifications'));
      more.appendChild(rows(edge.f.slice(2))); readout.appendChild(more);
    }
  }
  function draw() {
    var related = adjacent(selected), shown = related.slice(offset, offset + data.page_size);
    plot.classList.toggle('overview', overview);
    nodes.replaceChildren(); lines.replaceChildren();
    var positions = {}, visible = overview ? data.nodes : [at[selected]].concat(shown.map(other));
    visible.forEach(function (n, i) {
      positions[n.key] = overview ? [n.x / 1000 * 360 + 20, n.y / 620 * 350 + 25] :
        (i === 0 ? [200,185] : [[92,55],[308,55],[92,300],[308,300]][i-1]);
    });
    // HTML buttons keep full names in the accessibility tree and do not rely on
    // SVG hit-testing. Diagram coordinates and names are the same on every input.
    visible.forEach(function (n) {
      var center = !overview && n.key === selected;
      var button = el(center ? 'div' : 'button', 'cenode' + (center ? ' center' : ''));
      if (!center) button.type = 'button';
      button.dataset.key = n.key;
      var pos = positions[n.key]; button.style.left = pos[0] / 4 + '%';
      var diameter = overview ? 8 + 22 * Math.sqrt(n.reach / maxReach) : 24 + 27 * Math.sqrt(n.reach / maxReach);
      button.style.setProperty('--diameter', diameter + 'px');
      button.style.top = 'calc(' + pos[1] / 4 + '% - ' + (overview ? 0 : diameter / 2 + 4) + 'px)';
      if (overview) button.style.transform = 'translate(-50%,-50%)';
      var dot = el('span', 'cedot', center ? String(n.reach) : ''); dot.setAttribute('aria-hidden','true');
      button.appendChild(dot); button.appendChild(el('cite','cenodelabel',center ? 'In focus' : n.short));
      if (center) button.setAttribute('aria-label', n.name + ', ' + n.reach + ' facility names');
      if (!overview) button.appendChild(el('small','',center ? 'facility names' : n.reach + ' facility names'));
      if (!center) {
        var edge = shown.find(function (e) { return e.a === n.key || e.b === n.key; });
        button.setAttribute('aria-label', overview ? 'Explore ' + n.name : 'Read connection to ' + n.name);
        if (!overview) button.setAttribute('aria-pressed', String(edge === picked));
        button.addEventListener('click', function () {
          if (overview) focus(n.key, true);
          else {
            evidence(edge);
            // Keep the pressed button in place and focused while the evidence changes.
            nodes.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed',String(b === button)); });
            drawLines();
            openSheet();
          }
        });
      }
      nodes.appendChild(button);
    });
    drawLines();
    document.getElementById('cename').textContent = overview ? 'Every repeat company' : at[selected].name;
    document.getElementById('ceviewlabel').textContent = overview ? 'The full network' : 'Company in focus';
    var profile = document.getElementById('ceprofile');
    profile.setAttribute('href', overview ? '../company/' : at[selected].u);
    profile.firstChild.textContent = overview ? 'All company profiles ' : 'Company profile ';
    document.getElementById('cescope').textContent = overview ? data.nodes.length + ' companies · ' + data.edges.length + ' connections' :
      (related.length ? 'Showing ' + shown.length + ' of ' + related.length + ' connections' : 'No shared row with another repeat company');
    document.getElementById('cepaging').hidden = overview || related.length <= data.page_size;
    document.getElementById('ceprev').disabled = offset === 0;
    document.getElementById('cenext').disabled = offset + data.page_size >= related.length;
    document.getElementById('cegesture').textContent = overview ? 'Choose a point to bring its connections into focus. Search also reaches every company.' : 'Tap a company to read its shared records.';
    var mode = document.getElementById('cemode'); mode.setAttribute('aria-pressed', String(overview));
    mode.firstChild.textContent = overview ? 'Return to company ' : 'Whole network ';
    root.querySelectorAll('.ceseed').forEach(function (b) { b.setAttribute('aria-pressed',String(!overview && b.dataset.key === selected)); });
  }
  function closeSearch() { results.hidden = true; input.setAttribute('aria-expanded','false'); }
  function nearestPoint(event) {
    var best = null, distance = Infinity;
    nodes.querySelectorAll('button').forEach(function (button) {
      var dot = button.querySelector('.cedot').getBoundingClientRect();
      var d = Math.hypot(event.clientX - dot.left - dot.width / 2, event.clientY - dot.top - dot.height / 2);
      if (d <= Math.max(14, dot.width / 2 + 3) && d < distance) { best = button; distance = d; }
    });
    return best;
  }
  // The overview can be dense. Use the same nearest visible point for hover and
  // pointer activation, regardless of which overlapping HTML target is on top.
  // Keyboard activation keeps the explicitly focused button's own identity.
  plot.addEventListener('pointermove', function (event) {
    if (!overview || event.pointerType === 'touch') return;
    var nearest = nearestPoint(event);
    nodes.querySelectorAll('button').forEach(function (button) { button.classList.toggle('hovered',button === nearest); });
  });
  plot.addEventListener('pointerleave', function () {
    nodes.querySelectorAll('.hovered').forEach(function (button) { button.classList.remove('hovered'); });
  });
  plot.addEventListener('click', function (event) {
    if (!overview || event.detail === 0) return;
    event.preventDefault(); event.stopPropagation();
    var nearest = nearestPoint(event);
    if (nearest) focus(nearest.dataset.key, true);
  }, true);
  function focus(key, restoreFocus) {
    if (!at[key]) return;
    selected = key; offset = 0; overview = false;
    closeSearch(); input.value = '';
    evidence(adjacent(selected)[0] || null); draw();
    if (restoreFocus) {
      document.getElementById('ceprofile').focus({preventScroll:true});
      root.querySelector('.cecanvas').scrollIntoView({block:'start',behavior:'auto'});
    }
  }
  function search() {
    var q = input.value.trim().toLocaleLowerCase(); results.replaceChildren();
    if (!q) { closeSearch(); return; }
    var found = data.nodes.filter(function (n) { return n.name.toLocaleLowerCase().includes(q); });
    results.hidden = false; input.setAttribute('aria-expanded','true');
    if (!found.length) results.appendChild(el('p','','No company in this network matches. Try the full facility registry below.'));
    found.forEach(function (n) {
      var button = el('button'); button.type = 'button'; button.dataset.key = n.key;
      button.appendChild(el('cite','',n.name)); button.appendChild(el('small','',n.reach + ' facilities'));
      button.addEventListener('click',function () { focus(n.key, true); }); results.appendChild(button);
    });
  }
  input.addEventListener('input',search);
  input.addEventListener('keydown',function (event) {
    var first = results.querySelector('button');
    if (event.key === 'Escape') closeSearch();
    if (event.key === 'ArrowDown' && first) { event.preventDefault(); first.focus(); }
    if (event.key === 'Enter' && first) { event.preventDefault(); focus(first.dataset.key, true); }
  });
  root.addEventListener('keydown',function (event) {
    if (event.key === 'Escape' && !results.hidden) { closeSearch(); input.focus(); }
  });
  document.addEventListener('click',function (event) { if (!event.target.closest('.cesearch')) closeSearch(); });
  root.querySelectorAll('.ceseed').forEach(function (b) { b.addEventListener('click',function () { focus(b.dataset.key,false); }); });
  document.getElementById('cemode').addEventListener('click',function () { overview = !overview; draw(); });
  function turn(delta) {
    offset = Math.max(0, offset + delta * data.page_size);
    evidence(adjacent(selected)[offset] || null); draw();
  }
  document.getElementById('ceprev').addEventListener('click',function () { turn(-1); });
  document.getElementById('cenext').addEventListener('click',function () { turn(1); });
  root.querySelector('.ceinteractive').hidden = false;
  evidence(adjacent(selected)[0] || null); draw();
  if (window.ResizeObserver) new ResizeObserver(drawLines).observe(plot);
  root.querySelector('.cefallback').hidden = true;
}());
"""


def self_test() -> int:
    """A matching facility name on two different filings cannot invent a line."""
    def row(name, date, owners, occupants):
        return {"name": name, "effective": date, "owners": owners,
                "occupants": occupants, "operators": []}
    rows = [row("Shared campus", "2025-01-01", ["A LLC"], ["B Inc"]),
            row("Shared campus", "2026-01-01", ["A, LLC"], ["B Inc."]),
            row("Different A", "2025-01-01", ["A LLC"], []),
            row("Different B", "2025-01-01", [], ["B Inc"]),
            row("Reused name", "2025-01-01", ["A LLC"], []),
            row("Reused name", "2026-01-01", ["C LLC"], []),
            row("Different C", "2026-01-01", ["C LLC"], [])]
    data = {"facilities": rows, "entities": entities.resolve(rows)}
    graph = build(data, {})
    checks = {
        "only a shared certification creates a line": len(graph["edges"]) == 1,
        "recertification retains both dates without doubling the facility weight":
            graph["edges"][0]["w"] == 1 and len(graph["edges"][0]["f"]) == 2,
        "separate certifications have separate evidence destinations":
            len({r["id"] for r in graph["edges"][0]["f"]}) == 2,
        "a company with no shared row remains in the network": len(graph["nodes"]) == 3,
        "rebuilding the same data gives the same network": graph == build(data, {}),
        "an empty registry renders no invented company":
            build({"facilities": [], "entities": []}, {})["initial"] == "",
    }
    for name, passed in checks.items():
        print(f"{'ok' if passed else 'FAIL'}  {name}")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    import sys
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    result = build(entities.load())
    print(json.dumps({"companies": len(result["nodes"]), "connections": len(result["edges"])}))
