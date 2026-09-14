"""A real certification, with navigable filed parties, in place of the abstract role diagram."""
from __future__ import annotations

import html
import json
from numeral_lint import NUMERAL

import entities
import facility_dossier
from flourish_registry import record_id
from connection_explorer import ARROW


def authorised(data: dict) -> set[str]:
    """Filed identifiers and effective dates shown by the certification picker."""
    values = []
    for row in data["facilities"]:
        values.extend([row["name"], entities.ordinal_date(row["effective"])])
        for role in entities.ROLES:
            values.extend(row.get(role) or [])
    return {number for value in values for number in NUMERAL.findall(value)}


def render(data: dict) -> str:
    rows = sorted(data["facilities"], key=lambda row: (row["name"].casefold(), row["effective"]))
    if not rows:
        return ""
    by_key = {entity["key"]: entity for entity in data["entities"]}
    dossiers = facility_dossier.by_name(facility_dossier.load())
    records = []
    for row in rows:
        roles = {}
        for role in entities.ROLES:
            parties = []
            for name in row.get(role) or []:
                entity = by_key.get(entities.normalise(name))
                if entity:
                    parties.append({"n": name, "u": f"../company/{entity['slug']}/"
                                    if entity["reach"] >= entities.MIN_REACH else ""})
            roles[role[:-1]] = parties
        dossier = dossiers.get(row["name"])
        records.append({"id": record_id(row), "n": row["name"],
                        "d": entities.ordinal_date(row["effective"]), "r": roles,
                        "u": f"../facility/{dossier['slug']}/" if dossier else ""})
    selected = next((record for record in records
                     if record["n"] == "Lancium Abilene Clean Campus II"), records[0])
    esc = html.escape

    def role_html(role, parties):
        links = "".join(
            f'<li><a href="{esc(party["u"], quote=True)}"><cite>{esc(party["n"])}</cite>'
            f'{ARROW}</a></li>' if party["u"] else
            f'<li><span class="fxparty"><cite>{esc(party["n"])}</cite></span></li>'
            for party in parties)
        return (f'<section class="fxrole"><h4>{role.title()}</h4><ul data-prose="data">{links}</ul>'
                + ('' if parties else '<p>No party is listed.</p>') + '</section>')

    options = "".join(f'<option value="{record["id"]}" data-proper-name="{esc(record["n"], quote=True)}"'
                      + (' selected' if record["id"] == selected["id"] else '')
                      + f'>{esc(record["n"])} · {esc(record["d"])}</option>' for record in records)
    roles = "".join(role_html(role, selected["r"][role]) for role in ("owner", "occupant", "operator"))
    payload = json.dumps(records, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return (
        '<section class="fx" id="record-model" aria-labelledby="record-model-title">'
        '<a class="fxback" id="fxback" href="#registry-field" hidden>Back to the network</a>'
        '<header class="fxhead"><span class="sectioneyebrow">Inside the record</span>'
        '<h2 id="record-model-title">One place. The names behind it.</h2>'
        '<p>Choose a certification. Follow a company to the other facilities that name it.</p></header>'
        '<div class="fxpicker" hidden><label for="fxselect">Choose a certification</label>'
        f'<select id="fxselect">{options}</select></div>'
        '<div class="fxsheet" aria-live="polite" aria-atomic="false">'
        '<div class="fxfacility"><span class="sectioneyebrow">Certified facility</span>'
        f'<h3 id="fxname" tabindex="-1" data-prose="data"><cite>{esc(selected["n"])}</cite></h3>'
        f'<p id="fxdate" data-prose="data">Took effect {esc(selected["d"])}</p></div>'
        f'<div class="fxroles" id="fxroles">{roles}</div>'
        '<div class="fxactions">'
        f'<a id="fxdossier" href="{esc(selected["u"], quote=True)}"'
        + ('' if selected["u"] else ' hidden') + f'>Open the facility dossier {ARROW}</a>'
        '<a href="https://comptroller.texas.gov/taxes/data-centers/data-center-lists.php" '
        f'target="_blank" rel="noopener">Read the state registry {ARROW}</a>'
        '</div></div>'
        '<details class="fxmeaning"><summary>What the filed roles mean</summary>'
        '<p>Owner, occupant and operator are the columns in the state filing. The same company '
        'can fill several roles. A filed role alone does not establish corporate control or '
        'daily operations.</p><p>The date is when the certification took effect. It is not '
        'an opening date. Separate certifications for the same facility remain separate choices.</p>'
        '</details>'
        f'<script type="application/json" id="fxdata">{payload}</script>'
        f'<style>{STYLE}</style><script>{SCRIPT}</script></section>')


STYLE = """
.fx { scroll-margin-top:6rem; margin-top:clamp(2.5rem,6vw,5rem); }
.fxback { display:inline-flex; min-height:2.75rem; align-items:center; color:var(--accent); margin-bottom:.75rem; }
.fxback[hidden] { display:none; }
.fxhead { max-width:47rem; margin-bottom:1.4rem; }
.fxhead h2 { margin:.4rem 0 .7rem; font-size:clamp(2rem,4.5vw,4rem); line-height:1.04; }
.fxhead p { color:var(--caliche); margin:0; max-width:40rem; }
.fxpicker { display:grid; gap:.4rem; margin-bottom:1rem; }
.fxpicker[hidden] { display:none; }
.fxpicker label { font-family:var(--mono); font-size:var(--s-2); color:var(--dust); }
.fxpicker select { width:100%; min-width:0; min-height:3rem; padding:.65rem .75rem;
  font:inherit; font-size:1rem; color:var(--limestone); background:var(--panel);
  border:1px solid var(--rule-strong); border-radius:.3rem; }
.fxsheet { border:1px solid var(--rule); border-radius:.6rem; overflow:hidden;
  background:var(--panel); }
.fxfacility { position:relative; padding:1.5rem; border-bottom:1px solid var(--rule); }
.fxfacility::before { content:""; position:absolute; inset:0 auto 0 0; width:3px; background:var(--accent); }
.fxfacility h3 { margin:.5rem 0; font-size:clamp(1.45rem,2.5vw,2.2rem); line-height:1.15; }
.fxfacility cite, .fxrole cite { font-style:normal; }
.fxfacility p { margin:0; color:var(--dust); font:var(--s-2) var(--mono); line-height:1.5; }
.fxroles { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); }
.fxrole { padding:1.25rem; min-width:0; }
.fxrole + .fxrole { border-left:1px solid var(--rule); }
.fxrole h4 { margin:0 0 .65rem; font:var(--s-2) var(--mono); color:var(--dust);
  text-transform:uppercase; letter-spacing:.12em; }
.fxrole ul { list-style:none; padding:0; margin:0; }
.fxrole li + li { margin-top:.5rem; }
.fxrole a, .fxparty { display:flex; align-items:center; justify-content:space-between; gap:.75rem;
  min-height:2.8rem; color:var(--limestone); line-height:1.45; text-decoration:underline;
  text-decoration-color:var(--rule); text-underline-offset:.25em; overflow-wrap:anywhere; }
.fxrole a span { color:var(--accent); flex-shrink:0; }
.fxrole a:hover { text-decoration-color:var(--accent); }
.fxparty { text-decoration:none; }
.fxrole p { margin:0; color:var(--dust); }
.fxactions { display:flex; flex-wrap:wrap; gap:.4rem 1.5rem; padding:1rem 1.25rem;
  border-top:1px solid var(--rule); }
.fxactions a { display:inline-flex; align-items:center; gap:.6rem; min-height:2.8rem;
  color:var(--accent); text-underline-offset:.25em; }
.fxactions a[hidden] { display:none; }
.fxmeaning { margin-top:1rem; color:var(--dust); }
.fxmeaning summary { width:fit-content; min-height:2.8rem; cursor:pointer; padding:.55rem 0; }
.fxmeaning p { max-width:49rem; line-height:1.6; }
@media(max-width:40rem) {
  .fxfacility { padding:1.15rem; }
  .fxroles { grid-template-columns:1fr; }
  .fxrole { display:grid; grid-template-columns:5.8rem minmax(0,1fr); gap:.5rem;
    align-items:start; padding:.65rem 1.15rem; }
  .fxrole h4 { margin:.8rem 0 0; font-size:.7rem; }
  .fxrole + .fxrole { border-left:0; border-top:1px solid var(--rule); }
  .fxrole a, .fxparty { font-size:.94rem; }
  .fxactions { padding:.7rem 1.15rem; }
  .fxactions a { font-size:.9rem; }
}
"""


SCRIPT = r"""
(function () {
  'use strict';
  var root = document.getElementById('record-model');
  var input = document.getElementById('fxselect');
  var source = document.getElementById('fxdata');
  if (!root || !input || !source) return;
  var svgNS = root.querySelector('svg').namespaceURI;
  var records;
  try { records = JSON.parse(source.textContent); } catch (_) { return; }
  var byId = {};
  records.forEach(function (record) { byId[record.id] = record; });
  function select(id) {
    var record = byId[id];
    if (!record) return;
    input.value = id;
    document.getElementById('fxname').textContent = record.n;
    document.getElementById('fxdate').textContent = 'Took effect ' + record.d;
    var roles = document.getElementById('fxroles');
    roles.replaceChildren();
    ['owner', 'occupant', 'operator'].forEach(function (role) {
      var section = document.createElement('section'); section.className = 'fxrole';
      var heading = document.createElement('h4');
      heading.textContent = role.charAt(0).toUpperCase() + role.slice(1);
      section.appendChild(heading);
      var list = document.createElement('ul');
      (record.r[role] || []).forEach(function (party) {
        var item = document.createElement('li'), link = document.createElement(party.u ? 'a' : 'span');
        if (party.u) link.href = party.u; else link.className = 'fxparty';
        var name = document.createElement('cite'); name.textContent = party.n;
        var arrow = document.createElementNS(svgNS,'svg');
        arrow.setAttribute('viewBox','0 0 16 16'); arrow.setAttribute('class','cearrow');
        arrow.setAttribute('aria-hidden', 'true');
        var path = document.createElementNS(svgNS,'path');
        path.setAttribute('d','M3 13L13 3M4 3h9v9'); path.setAttribute('fill','none');
        path.setAttribute('stroke','currentColor'); path.setAttribute('stroke-width','1.5');
        arrow.appendChild(path);
        link.appendChild(name); if (party.u) link.appendChild(arrow);
        item.appendChild(link); list.appendChild(item);
      });
      section.appendChild(list);
      if (!(record.r[role] || []).length) {
        var gap = document.createElement('p'); gap.textContent = 'No party is listed.'; section.appendChild(gap);
      }
      roles.appendChild(section);
    });
    var dossier = document.getElementById('fxdossier');
    dossier.hidden = !record.u;
    if (record.u) dossier.setAttribute('href', record.u); else dossier.removeAttribute('href');
  }
  input.addEventListener('change', function () { select(input.value); });
  // Back navigation can restore a native select after the document's initial render.
  // Read that restored value on the next frame so the filed details match the picker.
  window.addEventListener('pageshow', function () {
    window.requestAnimationFrame(function () { select(input.value); });
  });
  document.addEventListener('certification-select', function (event) {
    var id = event.detail && event.detail.id;
    if (!byId[id]) return;
    select(id);
    document.getElementById('fxback').hidden = false;
    root.scrollIntoView({block:'start', behavior:'auto'});
    document.getElementById('fxname').focus({preventScroll:true});
  });
  root.querySelector('.fxpicker').hidden = false;
}());
"""
