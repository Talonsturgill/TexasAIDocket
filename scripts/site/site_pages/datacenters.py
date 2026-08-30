"""Data-center registry, company, facility, and construction renderers."""
from __future__ import annotations

from site_context import (
    SITE_NAME, beyond_panel, e, entities, facility_dossier, page, re,
    registry_changes, registry_graph, tdlr_projects,
)

def _facility_desc(summary: str, limit: int = 180) -> str:
    """A meta description, cut at a sentence and never mid word.

    `summary[:180]` sliced the word "in" down to "i", and a bare "i" is a first person pronoun
    to the house style checker, which was right to flag it. A truncation that can invent a word
    is a truncation that can invent a claim.
    """
    s = " ".join(str(summary).split())
    if len(s) <= limit:
        return s
    cut = s[:limit]
    for stop in (". ", "? ", "! "):
        if stop in cut:
            return cut[:cut.rindex(stop) + 1].strip()
    return cut[:cut.rindex(" ")].strip() if " " in cut else cut


def facility_filings(reg: dict, projects: dict) -> dict:
    """Every certified facility's OWN construction filings, keyed by facility name.

    Computed once for the whole build rather than per page, because the join needs to know how
    many facilities each party names before it can tell a single purpose entity from a parent
    company, and that is a question about the whole registry.

    A NAME IS THE PAGE AND A ROW IS NOT. Four names in the certified list carry two rows each,
    because a campus can be certified twice, and both rows render to one slug and one dossier.
    Keyed by row, the second row would silently overwrite the first and a page would show one
    certification's parties as if they were all of them. Worse, the parent company test counts
    how many FACILITIES a party names, so a facility certified three times would make its own
    single purpose entity look like a company that names three projects and the join would
    refuse the very row it exists to serve. The rows are unioned by name before either question
    is asked, so a certification count can never be read as a facility count.
    """
    dc = [r for r in (projects.get("projects") or [])
          if tdlr_projects.brand(r) and tdlr_projects.is_datacenter(r)]
    by_party: dict[str, list] = {}
    for r in dc:
        by_party.setdefault(entities.normalise(r.get("owner", "")), []).append(r)
    parties: dict[str, set] = {}
    for f in reg.get("facilities") or []:
        parties.setdefault(f["name"], set()).update(
            entities.normalise(x) for k in ("owners", "occupants", "operators")
            for x in (f.get(k) or []))
    specific = tdlr_projects.joinable(list(parties.values()))
    out = {}
    for name, ps in parties.items():
        m = tdlr_projects.filings_for(ps, specific, by_party)
        if m:
            out[name] = m
    return out


# WHAT A GAP CLAIMS IS A CLAIM ABOUT THE WORLD, and no gate here could check one.
#
# Nine dossiers shipped a gap reading "The street address is not public". The address was
# public. It sits in the construction filing this same build reads, in a field the parser
# already keeps, on the row the join already attaches to that facility. The dossier gate
# checks that gaps EXIST and carry no digits. It has no way to know whether one is TRUE, and a
# false gap is worse than no gap because it tells a reader to stop looking for something that
# is right there.
#
# So this checks the one class that is mechanically checkable. A gap saying a field is not
# public, where this build is holding that field, is a contradiction the build can find.
NOT_PUBLIC = re.compile(r"\b(?:not public|no address|not stated|not in the record|"
                        r"is not in the certification)\b", re.I)
GAP_FIELDS = (("address", re.compile(r"\b(?:street\s+)?address\b", re.I)),
              ("county", re.compile(r"\bcounty\b", re.I)))


def contradicted_gaps(dossiers: list, filings: dict) -> list[str]:
    """Gaps that say a field is not public while the filings this build read carry it."""
    out = []
    for d in dossiers:
        got = filings.get(d["name"]) or []
        if not got:
            continue
        # WHAT THE PAGE ITSELF SUPPLIES IS NOT A HOLE. A gap that says the CERTIFICATION has no
        # address, on a page that then prints the address out of the construction filing, is
        # provenance rather than a hole, and reads that way. The fault is a gap that sends a
        # reader away from something no other line on the page gives them.
        supplied = " ".join(str(f.get("text") or "") + " " + str(f.get("label") or "")
                            for f in d.get("facts") or []).lower()
        for gap in d.get("gaps") or []:
            if not NOT_PUBLIC.search(gap):
                continue
            for field, pat in GAP_FIELDS:
                if not pat.search(gap):
                    continue
                have = next((r[field] for r in got if r.get(field)), None)
                if have and str(have).lower() not in supplied:
                    out.append(f"{d['name']}: gap says {gap!r}, and its construction filing "
                               f"carries {field} {have!r}, which no fact on this page supplies")
    return out


def facility_page(d: dict, today: str, filings: list | None = None) -> str:
    """One certified data center, and everything the research could source about it."""
    name = d["name"]
    body = (
        f'<article class="prose facilitypage" data-proper-name="{e(name)}">'
        f'<p class="crumb"><a href="../../datacenters/">Texas data centers</a> '
        f'<span aria-hidden="true">/</span> Every registered facility.</p>'
        f'<header class="entityhero facilityhero">'
        f'<span class="entityeyebrow">Certified facility dossier</span>'
        f'<h1><cite>{e(name)}</cite></h1>'
        f'</header>'
        f'{facility_dossier.panel(d, heading=2)}'
        f'{tdlr_projects.facility_panel(filings or [], e)}'
        f'<p class="dfoot">The registry entry for this facility comes from the Texas '
        f'Comptroller\'s certified list of data centers holding a sales tax exemption. '
        f'Owner, occupant and operator are roles in that filing rather than descriptions '
        f'of who runs the building.</p>'
        f'</article>')
    return page(
        title=f"{name} · {SITE_NAME}",
        desc=_facility_desc(d.get("summary") or ""),
        body=body, depth=2, active=None, today=today,
        canonical=f"facility/{d['slug']}/",
        revised=False, extra_css="facility.css")



def company_page(item: dict, data: dict, dossiers: dict, is_group: bool, today: str) -> str:
    """One company, and every certified facility the state puts it on."""
    name = item["name"]
    kind = ("Curated parent group" if is_group else
            "Registry entity shown in the state's own spelling")
    body = (
        f'<article class="prose companypage" data-proper-name="{e(name)}">'
        f'<p class="crumb"><a href="../../datacenters/">Texas data centers</a> '
        f'<span aria-hidden="true">/</span> <a href="../">Who is behind the registry</a>.</p>'
        f'<header class="entityhero companyhero">'
        f'<span class="entityeyebrow">{e(kind)}</span>'
        f'<h1><cite>{e(name)}</cite></h1>'
        f'</header>'
        f'{entities.panel(item, data, dossiers, is_group=is_group)}'
        f'<p class="dfoot">Owner, occupant and operator are roles in a sales tax exemption '
        f'filing rather than descriptions of who runs a building. Counts here are computed from '
        f"the Comptroller's certified list and nothing else.</p>"
        f'</article>')
    return page(
        title=f"{name} · {SITE_NAME}",
        desc=_facility_desc(f"Every Texas data center the certified registry puts "
                            f"{name} on, by role."),
        body=body, depth=2, active=None, today=today,
        canonical=f"company/{item['slug']}/",
        revised=False, extra_css="facility.css")



def _registry_field(data: dict, base: str = "") -> str:
    """The network, drawn from the same resolution the lists are built from.

    `base` prefixes every node's href. The field lives on the data centers tab and the pages
    it links to live under `/company/`, so it is `../company/` there and empty on the company
    index itself, where a bare slug already resolves.
    """
    g = registry_graph.build(data["entities"])
    if not g["nodes"]:
        return ""
    n0 = entities.n0
    at = {node["key"]: node for node in g["nodes"]}
    dossiers = facility_dossier.by_name(facility_dossier.load())
    facility_links = {
        name: f'../facility/{dossier["slug"]}/'
        for name, dossier in dossiers.items()
    }

    def facility_ref(name: str) -> str:
        href = facility_links.get(name)
        return (f'<a href="{e(href)}"><cite>{e(name)}</cite></a>' if href
                else f'<cite>{e(name)}</cite>')

    strongest = ""
    for index, edge in enumerate(g["edges"][:2]):
        a, b = at[edge["a"]], at[edge["b"]]
        noun = "facility record" if edge["w"] == 1 else "facility records"
        examples = "".join(f'<li>{facility_ref(name)}</li>'
                           for name in edge["facilities"][:2])
        strongest += (
            f'<article class="grconnection">'
            f'<p class="grpair"><a href="{e(base)}{e(a["slug"])}/">{e(a["name"])}</a>'
            f'<span aria-hidden="true">+</span>'
            f'<a href="{e(base)}{e(b["slug"])}/">{e(b["name"])}</a></p>'
            f'<span class="grcount"><strong class="num">{n0(edge["w"])}</strong> shared '
            f'{noun}</span><ul class="grfacilities">{examples}</ul>'
            f'<button class="grinspect" type="button" data-edge="{index}">Inspect line</button>'
            f'</article>')

    return (
        f'<section class="gwrap" id="registry-field" aria-labelledby="registry-field-title">'
        f'<header class="ghead">'
        f'<span class="sectioneyebrow">Registry relationship field</span>'
        f'<h2 id="registry-field-title">Follow the same names across Texas</h2>'
        f'<p>Every point is a company on more than one certified facility. Every line is a '
        f'facility record where two of those companies meet.</p>'
        f'</header>'
        f'<div class="gcontrols" id="gcontrols" hidden>'
        f'<label for="gsearch"><span>Find a company</span>'
        f'<input id="gsearch" type="search" autocomplete="off" '
        f'placeholder="Company name"></label>'
        f'<label for="grole"><span>Emphasize a role</span>'
        f'<select id="grole"><option value="">Every role</option>'
        f'<option value="owner">Owner</option><option value="occupant">Occupant</option>'
        f'<option value="operator">Operator</option></select></label>'
        f'<button id="greset" type="button">Reset field</button>'
        f'</div>'
        f'<div class="gworkspace">'
        f'<div class="gfield" id="gfield">{registry_graph.svg(g, base)}</div>'
        f'<aside class="glens" aria-live="polite">'
        f'<span class="grk">Relationship readout</span>'
        f'<h3 id="grname">The strongest shared rows</h3>'
        f'<p id="grmeta">Choose a company or a line to see what the state record connects.</p>'
        f'<div class="grroles" id="grroles" data-prose="data">'
        f'<span class="grrole"><b>Point</b>company</span>'
        f'<span class="grrole"><b>Line</b>shared row</span>'
        f'<span class="grrole"><b>Orbit</b>no shared row</span></div>'
        f'<div class="grconnections" id="grconnections">'
        f'<p class="grsection">Largest connections in the registry</p>{strongest}</div>'
        f'<a class="grlink" id="grlink" href="{e(base)}">Browse every company</a>'
        f'</aside></div>'
        f'<p class="gkey" data-prose="data">'
        f'<span><b>Point size</b> certified facilities</span>'
        f'<span><b>Line</b> same certified row</span>'
        f'<span><b>Line weight</b> shared rows</span>'
        f'<span><b>Outer orbit</b> repeat company with no shared row</span></p>'
        f'<p class="ghint">Select a company to open its profile. Point at a line to reveal '
        f'the facility records behind it.</p>'
        f'<script type="application/json" id="gdata">'
        f'{registry_graph.payload(g, base, facility_links)}</script>'
        f'<script>{registry_graph.SCRIPT}</script>'
        f'</section>')


def companies_index(data: dict, today: str) -> str:
    """The registry read down its columns instead of across its rows."""
    ents, groups = entities.published(data)
    split = entities.split_by_punctuation(data["entities"])
    n0 = entities.n0

    def row(x, is_group):
        roles = " ".join(f'<span class="crolechip">{k} {n0(len(v))}</span>'
                         for k, v in sorted(x["roles"].items()))
        return (f'<li><a href="{x["slug"]}/"><cite>{e(x["name"])}</cite></a> '
                f'<strong class="num">{n0(x["reach"])}</strong> {roles}</li>')

    body = (
        f'<article class="prose companyindex">'
        f'<p class="crumb"><a href="../datacenters/">Texas data centers</a> '
        f'<span aria-hidden="true">/</span> Who is behind the registry.</p>'
        f'<h1>Who is behind the registry</h1>'
        f'<p>The certified list names <strong class="num">{n0(len(data["facilities"]))}</strong> '
        f'facilities and reads as that many unrelated buildings. It is not. '
        f'<strong class="num">{n0(sum(1 for x in data["entities"] if x["reach"] > 1))}</strong> '
        f'companies appear on more than one, and the largest relationships in Texas are only '
        f'visible reading down a column.</p>'
        # THE FIELD MOVED AND DID NOT COPY. It leads the data centers tab now, which is the
        # page a reader arrives at. Drawing it twice ships the same forty node simulation and
        # its script on two pages, and gives a reader no way to know which one is the real one.
        f'<p class="qnote"><a href="../datacenters/">The registry drawn as a field</a> leads '
        f'the data centers page, where every point is a company on more than one facility.</p>'
        + f'<h2>Filed under more than one spelling</h2>'
        f'<p>Punctuation and capitalisation alone split '
        f'<strong class="num">{n0(len(split))}</strong> companies into separate rows. Counting '
        f'the strings rather than the companies reports the largest occupant in the state as two '
        f'smaller ones.</p>'
        f'<ul class="csplit" data-prose="data">'
        + "".join(f'<li><strong class="num">{n0(x["reach"])}</strong> '
                  + " ".join(f"<cite>{e(v)}</cite>" for v in x["variants"]) + "</li>"
                  for x in split)
        + f'</ul>'
        f'<h2>Companies, as the state spells them</h2>'
        f'<p class="qnote">Resolved mechanically. Case, punctuation and the corporate suffix are '
        f'ignored. Nothing else is.</p>'
        f'<ul class="clist" data-prose="data">' + "".join(row(x, False) for x in ents) + "</ul>"
        f'<h2>Grouped by parent</h2>'
        f'<p class="qnote">A judgment rather than a rule. Each grouping states its reason on '
        f"its own page. Where the two layers disagree the mechanical one above is the "
        f"defensible number.</p>"
        f'<ul class="clist" data-prose="data">' + "".join(row(x, True) for x in groups) + "</ul>"
        f'</article>')
    return page(
        title=f"Who is behind the registry · {SITE_NAME}",
        desc="Every company the Texas data center registry names, resolved across the spellings "
             "the state filed them under, with every facility and role.",
        body=body, depth=1, active=None, today=today,
        canonical="company/", revised=False, extra_css="facility.css")


def _record_ontology() -> str:
    """The reader model behind the registry, shown before the full roster.

    The registry page used the words owner, occupant and operator everywhere while explaining
    their difference only after several screens. This makes the record's atomic row and the
    research layered onto it visible as one system before the reader starts filtering names.
    """
    return (
        '<section class="dcontology" id="record-model" aria-labelledby="record-model-title">'
        '<header class="ontohead">'
        '<span class="sectioneyebrow">How the record works</span>'
        '<h2 id="record-model-title">One certification. Three legal roles.</h2>'
        '<p>The state publishes one row for a tax exemption. The row names a facility and three '
        'parties. Research adds evidence without turning a filing role into a claim about '
        'corporate control or daily operations.</p>'
        '</header>'
        '<div class="ontoflow">'
        '<article class="ontocore">'
        '<span class="ontok">Certified facility</span>'
        '<h3>The row Texas publishes</h3>'
        '<p>A facility name and effective date anchor every relationship in the field.</p>'
        '</article>'
        '<div class="ontoroles">'
        '<article><span class="ontomark">O</span><div><h3>Owner</h3>'
        '<p>The entity named in the owner column.</p></div></article>'
        '<article><span class="ontomark">U</span><div><h3>Occupant</h3>'
        '<p>The entity named in the occupant column.</p></div></article>'
        '<article><span class="ontomark">R</span><div><h3>Operator</h3>'
        '<p>The entity named in the operator column.</p></div></article>'
        '</div></div>'
        '<div class="ontolayers" data-prose="data">'
        '<article><span>Research layer</span><strong>Sourced fact</strong>'
        '<small>A claim tied to a source and a reading date</small></article>'
        '<article><span>Research layer</span><strong>Open gap</strong>'
        '<small>A question the public record still can\'t answer</small></article>'
        '<article><span>Second register</span><strong>Construction filing</strong>'
        '<small>Address, cost, size and schedule when the entity match is specific</small></article>'
        '</div>'
        '</section>')



def datacenters_page(today: str) -> str:
    """Every certified data center in Texas, led by the network they form.

    THE FIELD LEADS BECAUSE IT IS THE ARGUMENT. The registry reads as a hundred and fifty one
    unrelated buildings and it is nothing of the kind. Drawing the companies that appear on
    more than one of them, before a word of prose, says in one look what the lists below take
    a page to say. It was buried under an intro paragraph on the companies index, which is a
    page most readers never reached.

    Everything here is computed. The counts come from the resolution the lists are built from,
    the money from the construction filings, and `w()` authorises each through the same call
    that renders it.
    """
    data = entities.load()
    n0 = entities.n0
    pj = tdlr_projects.load()
    dc = [r for r in (pj.get("projects") or [])
          if tdlr_projects.brand(r) and tdlr_projects.is_datacenter(r)]
    t = tdlr_projects.totals(dc)
    camps = tdlr_projects.campuses(dc)
    multi = sum(1 for x in data["entities"] if x["reach"] > 1)
    doss = facility_dossier.load().get("dossiers") or []
    # BOTH BEYOND PANELS READ THE SAME FILE, so it is loaded once. Generation moved here from
    # the grid page on the owner's call: what is being BUILT FOR these buildings is a data
    # center fact, and the grid tab is for what the system is doing rather than for who is
    # arriving on it.
    _beyond = beyond_panel.load()

    def bn(v):
        return f"${v / 1_000_000_000:.2f} billion" if v >= 1_000_000_000 else f"${n0(v)}"

    # THE HEADLINE FIGURES, four of them, each a different register saying a different thing.
    tiles = "".join(
        f'<div class="dctile"><span class="dcn num">{v}</span>'
        f'<span class="dck">{k}</span></div>'
        for k, v in (("Certified facilities", n0(len(data["facilities"]))),
                     ("Companies on more than one", n0(multi)),
                     ("Filed to build", bn(t["cost"])),
                     ("Researched in detail", n0(len(doss)))))

    crow = "".join(
        f'<div class="cbrow"><span class="cbd">{e(c["project"])}</span>'
        f'<span class="cbm"><strong class="num">{e(bn(c["cost"]))}</strong></span>'
        f'<span class="cbs">' + (f'<strong class="num">{n0(c["sqft"])}</strong> sq ft'
                                 if c["sqft"] else "") + f'</span>'
        f'<span class="cbf">{n0(c["buildings"])} '
        f'{"building" if c["buildings"] == 1 else "buildings"}</span>'
        f'<span class="cbc">{e(", ".join(c["counties"]))}</span></div>'
        for c in camps[:8])

    body = (
        f'<section class="dchero">'
        f'<div class="dchero-copy">'
        f'<span class="sectioneyebrow">Texas infrastructure atlas</span>'
        f'<h1>Texas data centers</h1>'
        f'<p class="dclede">A tax list became an infrastructure map. Follow the companies '
        f'across certified sites. Open the evidence behind each one.</p>'
        f'<nav class="dcjump" aria-label="Data center page">'
        f'<a href="#registry-field">Explore relationships</a>'
        f'<a href="#registry-roster">Find a facility</a>'
        f'</nav></div>'
        f'<div class="dctiles" data-prose="data">{tiles}</div>'
        f'</section>'
        + _registry_field(data, "../company/")
        + _record_ontology()
        + f'<div class="prose dcpage">'
        + beyond_panel.registry(_beyond, today)
        + beyond_panel.generation(_beyond, today)
        + f'</div>'
        + f'<article class="prose dcpage">'
        f'<h2>Campuses, as the builder filed them</h2>'
        f'<p>Several filings under one project name are the developer\'s own grouping. '
        f'Buildings scoped as data centers are counted apart from the offices and yards filed '
        f'beside them.</p>'
        f'<div class="cbtable cbcamp" data-prose="data">{crow}</div>'
        f'<p class="qnote"><a href="../construction/">The whole construction register</a>, by '
        f'year, by county and by company. It states the rule that decides what counts.</p>'
        f'<h2>Where to go from here</h2>'
        f'<ul class="dcways">'
        f'<li><a href="../company/">Who is behind the registry</a>. Every company the state '
        f'names, resolved across the spellings it filed them under.</li>'
        f'<li><a href="../construction/">What Texas filed to build</a>. The second register, '
        f'priced and dated, and where the two meet.</li>'
        f'<li><a href="../registry-changes/">What the registry changed</a>. Every row the '
        f'state added, dropped or edited, with the before and the after.</li>'
        f'<li><a href="../grid/">The Grid Watch</a>. What the system these buildings draw on '
        f'is doing, measured daily.</li>'
        f'</ul>'
        f'</article>')
    return page(
        title=f"Texas data centers · {SITE_NAME}",
        desc="Every data center Texas has certified, the companies behind them, and what was "
             "filed to build them. Counted from the state's own registers.",
        body=body, depth=1, active="datacenters/", today=today,
        canonical="datacenters/", revised=False, extra_css="facility.css")


def construction_page(data: dict, reg: dict, today: str) -> str:
    """What Texas filed to BUILD, beside what it certified for a tax exemption.

    Every figure comes out of `tdlr_projects`, computed from the filings. Nothing is typed. The
    page states the rule that decides which filings count, because a reader who disagrees with
    the rule should be able to see it rather than infer it.
    """
    n0 = entities.n0
    recs = data.get("projects") or []
    tracked = [r for r in recs if tdlr_projects.brand(r)]
    dc = [r for r in tracked if tdlr_projects.is_datacenter(r)]
    other = [r for r in tracked if not tdlr_projects.is_datacenter(r)]
    t = tdlr_projects.totals(dc)
    ot = tdlr_projects.totals(other)
    years = tdlr_projects.by_year(dc)
    brands = tdlr_projects.by_brand(dc)
    dupes = tdlr_projects.shared_buildings(dc)
    conflicts = tdlr_projects.county_conflicts(dc)

    def bn(v):
        return f"${v / 1_000_000_000:.2f} billion" if v >= 1_000_000_000 else f"${n0(v)}"

    counties = {}
    for r in dc:
        c = r.get("county")
        if c:
            counties[c] = counties.get(c, 0) + (r.get("cost") or 0)
    top = sorted(counties.items(), key=lambda kv: -kv[1])[:12]

    crow = "".join(
        f'<div class="cbrow"><span class="cbd">{e(c)}</span>'
        f'<span class="cbm"><strong class="num">{e(bn(v))}</strong></span>'
        f'<span class="cbf">{n0(sum(1 for r in dc if r.get("county") == c))} '
        f'{"filing" if sum(1 for r in dc if r.get("county") == c) == 1 else "filings"}</span>'
        f'<span class="cbc"></span><span class="cbc"></span></div>' for c, v in top)

    brow = "".join(
        f'<div class="cbrow"><span class="cbd">{e(b["brand"])}</span>'
        f'<span class="cbm"><strong class="num">{e(bn(b["cost"]))}</strong></span>'
        f'<span class="cbs"><strong class="num">{n0(b["sqft"])}</strong> sq ft</span>'
        f'<span class="cbf">{n0(b["filings"])} '
        f'{"filing" if b["filings"] == 1 else "filings"}</span>'
        f'<span class="cbc">{n0(len(b["counties"]))} '
        f'{"county" if len(b["counties"]) == 1 else "counties"}</span></div>'
        for b in brands)

    # A CAMPUS IS THE FILER'S OWN GROUPING, and the only figure worth adding up across a
    # project name is the one for the buildings. `dc_scope` keeps the office out.
    krow = "".join(
        f'<div class="cbrow"><span class="cbd">{e(c["project"])}</span>'
        f'<span class="cbm"><strong class="num">{e(bn(c["cost"]))}</strong></span>'
        f'<span class="cbs">' + (f'<strong class="num">{n0(c["sqft"])}</strong> sq ft'
                                  if c["sqft"] else "") + f'</span>'
        f'<span class="cbf">{n0(c["buildings"])} '
        f'{"building" if c["buildings"] == 1 else "buildings"}</span>'
        f'<span class="cbc">{e(", ".join(c["counties"]))}</span></div>'
        for c in tdlr_projects.campuses(dc))

    # THE JOIN, computed by the one function the facility pages also call. It was written twice
    # for a week, and two copies of a rule about which parties are specific enough to join on is
    # how this table and a facility page come to disagree about the same building.
    joined = [(name, m, sum(x.get("cost") or 0 for x in m))
              for name, m in facility_filings(reg, data).items()]
    joined.sort(key=lambda x: -x[2])
    jrow = "".join(
        f'<div class="cbrow"><span class="cbd"><cite>{e(name)}</cite></span>'
        f'<span class="cbm"><strong class="num">{e(bn(cost))}</strong></span>'
        f'<span class="cbs"></span>'
        f'<span class="cbf">{n0(len(m))} filing{"" if len(m) == 1 else "s"}</span>'
        f'<span class="cbc">{e(m[0].get("county", ""))}</span></div>'
        for name, m, cost in joined)

    silent = tdlr_projects.andlist(tdlr_projects.NO_FILINGS)

    # THE MIRROR OF THAT. A company can build in Texas and hold no certification at all, which
    # is computed from the two records rather than asserted.
    _words = []
    for _f in reg.get("facilities") or []:
        _words.append(_f.get("name", ""))
        for _k in ("owners", "occupants", "operators"):
            _words.extend(_f.get(_k) or [])
    certified_blob = " ".join(_words).lower()
    uncertified = sorted({b["brand"] for b in brands
                          if b["brand"].lower() not in certified_blob})

    body = (
        f'<article class="prose construction">'
        f'<p class="crumb"><a href="../datacenters/">Texas data centers</a> '
        f'<span aria-hidden="true">/</span> The construction register.</p>'
        f'<h1>What Texas filed to build</h1>'
        f'<p>The Comptroller certifies who holds a tax exemption. It records no address, no '
        f'size and no cost. A second state register does. Every large commercial project is '
        f'filed with the Department of Licensing and Regulation. That filing carries a street '
        f'address, a county, a square footage, an estimated cost and a schedule.</p>'
        f'<p class="qnote" data-prose="data">'
        f'<strong class="num">{e(bn(t["cost"]))}</strong> across '
        f'<strong class="num">{n0(t["filings"])}</strong> filings, '
        f'<strong class="num">{n0(t["sqft"])}</strong> sq ft in '
        f'<strong class="num">{n0(t["sqft_known"])}</strong> of them, '
        f'<strong class="num">{n0(t["counties"])}</strong> counties, from '
        f'<time datetime="{e(t["first"])}">{e(facility_dossier.ordinal(t["first"]))}</time> to '
        f'<time datetime="{e(t["last"])}">{e(facility_dossier.ordinal(t["last"]))}</time>.</p>'

        f'<h2>Filed per year</h2>'
        f'<p>By the year a project was scheduled to start. A year with nothing filed is drawn '
        f'empty rather than left out. Drop the quiet years and a rush looks like a trend.</p>'
        f'<div class="cywrap">{tdlr_projects.columns(years, "cost")}</div>'

        f'<h2>Where the money is going</h2>'
        f'<p>Counties by capital filed. The largest is not a metro.</p>'
        f'<div class="cbtable" data-prose="data">{crow}</div>'

        f'<h2>By company</h2>'
        f'<div class="cbtable" data-prose="data">{brow}</div>'
        f'<p class="qnote">Several operators file nothing under their own name. {e(silent)}. '
        f'That is not an absence of building. It is the difference between a company that builds '
        f'and one that leases what somebody else built.</p>'

        + (f'<p class="qnote">The mirror of that also happens. '
           f'{e(tdlr_projects.andlist(uncertified))} '
           + ("files" if len(uncertified) == 1 else "file")
           + f' construction here and hold'
           + ("s" if len(uncertified) == 1 else "")
           + f' no certification at all. A reader working from the tax record alone would not '
           f'know they build in Texas.</p>' if uncertified else "") +
        f'<h2>Filed as one campus</h2>'
        f'<p>Several filings under one project name are the developer\'s own grouping rather '
        f'than one made here. Buildings scoped as data centers are counted apart from the '
        f'offices and yards filed beside them.</p>'
        f'<div class="cbtable cbcamp" data-prose="data">{krow}</div>'

        f'<h2>Where the two registers meet</h2>'
        f'<p>The state published this link on both sides. A certification names an owner and a '
        f'construction filing names the same entity. These are the certified facilities whose '
        f'own buildings can be priced.</p>'
        f'<p>The match is made only on an entity specific enough to mean one project. A parent '
        f'company named on many certifications identifies a company and not a building. Joining '
        f'on one would attach every Microsoft filing in the state to a single row.</p>'
        f'<div class="cbtable cbjoin" data-prose="data">{jrow}</div>'

        f'<h2>What counts, and what does not</h2>'
        f'<p>A filing counts when it names a data center, a colocation building, a data hall, '
        f'a substation or a critical power system. The test is what the filer wrote. Exclusions '
        f'run first. A warehouse and a data hall share the airport code naming convention. '
        f'Without that a fulfillment center lands in a figure about compute.</p>'
        f'<p class="qnote" data-prose="data">The same companies filed '
        f'<strong class="num">{e(bn(ot["cost"]))}</strong> of other work in Texas across '
        f'<strong class="num">{n0(ot["filings"])}</strong> filings. That is counted here and '
        f'added to nothing above.</p>'
        f'<p>Membership is decided on the owner each filing carries. It is never decided on the '
        f'search that found it. That endpoint matches a substring, so a query for one operator '
        f'returns a metal building supplier and a nail bar.</p>'
        f'<p class="qnote">A campus counted twice would show as two filings at one address for '
        f'one cost under two owners. There are none.</p>'
        f'<p class="qnote">This page names no person. A filing carries the contact who submitted '
        f'it and the specialist who inspects it. The parser drops both.</p>'
        f'</article>')
    return page(
        title=f"What Texas filed to build \u00b7 {SITE_NAME}",
        desc="Texas registers every large construction project with a second agency. What the "
             "data center operators filed to build, by county, by company and by year.",
        body=body, depth=1, active=None, today=today,
        canonical="construction/", revised=False, extra_css="facility.css")


def registry_changes_page(data: dict, today: str) -> str:
    """What the state has quietly changed since anyone started looking."""
    n0 = entities.n0
    hist = list(reversed(data["history"]))
    blocks = []
    for h in hist:
        parts = []
        if h["added"]:
            parts.append(f'<h3>Added <strong class="num">{n0(len(h["added"]))}</strong></h3>'
                         f'<ul class="rcl" data-prose="data">'
                         + "".join(f"<li><cite>{e(x)}</cite></li>" for x in h["added"]) + "</ul>")
        if h["removed"]:
            parts.append(f'<h3>Removed <strong class="num">{n0(len(h["removed"]))}</strong></h3>'
                         f'<ul class="rcl" data-prose="data">'
                         + "".join(f"<li><cite>{e(x)}</cite></li>" for x in h["removed"]) + "</ul>")
        if h["substantive"]:
            rows = ""
            for c in h["substantive"]:
                moved = "".join(
                    f'<div class="rcf"><span class="rcfl">{e(f["label"])}</span>'
                    f'<span class="rcwas"><span class="rcw">was</span>'
                    f'<cite>{e(f["was"]) or "not stated"}</cite></span>'
                    f'<span class="rcnow"><span class="rcw">now</span>'
                    f'<cite>{e(f["now"]) or "not stated"}</cite></span>'
                    f'</div>'
                    for f in registry_changes.fields(c))
                rows += f'<li><cite>{e(c["name"])}</cite>{moved}</li>'
            parts.append(f'<h3>Rewritten in place '
                         f'<strong class="num">{n0(len(h["substantive"]))}</strong></h3>'
                         f'<ul class="rcl" data-prose="data">{rows}</ul>')
        if not parts:
            parts.append('<p class="qnote">Nothing moved.</p>')
        blocks.append(f'<section class="rcday"><h2>'
                      f'<time datetime="{e(h["to"])}">{e(h["to"])}</time></h2>'
                      + "".join(parts) + "</section>")

    body = (
        f'<article class="prose regchanges">'
        f'<p class="crumb"><a href="../datacenters/">Texas data centers</a> '
        f'<span aria-hidden="true">/</span> What the registry changed.</p>'
        f'<h1>What the registry changed</h1>'
        f'<p>The certified list is not append only. Rows are added, and existing rows are '
        f'rewritten while keeping their original effective date. A row therefore names who holds '
        f'an exemption now. It does not name who held it when the exemption was granted.</p>'
        f'<p>This page compares every reading the collector has kept. It ignores a date that was '
        f'only reformatted, because burying an owner swap under punctuation noise is how a watch '
        f'stops being read.</p>'
        f'<p class="qnote">The record begins with the first reading on '
        f'<time datetime="{e(data["first"] or "")}">{e(data["first"] or "")}</time> and covers '
        f'<strong class="num">{n0(data["readings"])}</strong> readings. Nothing before that can '
        f'be reported, and the list was not necessarily stable before anyone was looking.</p>'
        + "".join(blocks) + "</article>")
    return page(
        title=f"What the registry changed · {SITE_NAME}",
        desc="The Texas certified data center list is edited in place. Every change between "
             "readings, with the rows that were rewritten.",
        body=body, depth=1, active=None, today=today,
        canonical="registry-changes/", revised=False, extra_css="facility.css")



__all__ = ['_facility_desc', 'facility_filings', 'NOT_PUBLIC', 'GAP_FIELDS', 'contradicted_gaps', 'facility_page', 'company_page', '_registry_field', 'companies_index', 'datacenters_page', 'construction_page', 'registry_changes_page']

