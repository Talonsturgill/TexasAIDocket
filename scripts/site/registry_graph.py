"""registry_graph.py — the registry as a network, laid out deterministically.

WHY A NETWORK AND NOT A CHART

The job of this data is IDENTITY AND RELATIONSHIP, not magnitude. Forty companies appear on more
than one facility and forty four pairs of them share at least one. Which companies cluster, and
around what, is the question, and no bar chart answers it.

WHY THE LAYOUT IS COMPUTED HERE AND NOT IN THE BROWSER

`site_fresh_check` proves `docs/` is a pure function of the ledgers by rebuilding and comparing
byte for byte. A layout seeded with a random number would produce a different page every build
and take that proof away. So the positions are relaxed here with a FIXED start, FIXED constants
and a FIXED iteration count, and the same registry always draws the same picture.

The browser then animates FROM those positions. Motion is a read time behaviour and never
touches the bytes on disk, so the page stays deterministic and still moves under a cursor.

WHAT IT LOOKS LIKE, AND THE DOCTRINE THAT DECIDES

`TEXAS_DESIGN_DOCTRINE` section 9 is explicit that the design never dramatises, and that a
sceptical reader trusts an instrument before an argument. So this is drawn as a SURVEY of the
graph rather than a glowing brain:

    ONE HUE. Node area carries reach and edge width carries shared facilities. There is no
    categorical palette here to get wrong, and no status colour is borrowed for decoration.
    A single accent marks the neighborhood under the cursor and nothing else.

    A NEATLINE, like the county map. The field is bounded and the drawing sits inside it.

    THE LIST BELOW IS THE TABLE VIEW. Every node is a row down the page with its counts, so
    nothing here is reachable only by pointing at a picture.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import defaultdict
from itertools import combinations

W, H = 1000.0, 620.0          # the field, in user units. The svg scales to its container.
PAD = 26.0
ITERS = 260                   # fixed. more is not better once it settles, and it must be fixed.
MIN_R, MAX_R = 4.0, 19.0
# The clear space every dot keeps. It is what turns a cluster from a ball into a web: relaxed
# space is scaled to fit the field, so two nodes comfortably apart in the sim can end up
# touching, and an edge shorter than the two dots it joins is an edge nobody can see.
GAP = 17.0


def graph(entities: list[dict], min_reach: int = 2) -> dict:
    """Nodes are companies. An edge is a facility two of them both appear on.

    A line is evidence, not decoration. Retain the exact certified facility rows that created
    each relationship so the interface can answer why two companies are connected.
    """
    nodes = [e for e in entities if e["reach"] >= min_reach]
    by_fac = defaultdict(set)
    for e in nodes:
        for f in e["facilities"]:
            by_fac[f].add(e["key"])
    shared: dict[tuple[str, str], list[str]] = defaultdict(list)
    for facility, ks in by_fac.items():
        for a, b in combinations(sorted(ks), 2):
            shared[(a, b)].append(facility)
    return {
        "nodes": [{"key": n["key"], "name": n["name"], "slug": n["slug"],
                   "reach": n["reach"],
                   "roles": {r: len(v) for r, v in sorted(n["roles"].items())}}
                  for n in sorted(nodes, key=lambda x: (-x["reach"], x["name"].lower()))],
        "edges": [{"a": a, "b": b, "w": len(facilities),
                   "facilities": sorted(facilities)}
                  for (a, b), facilities in
                  sorted(shared.items(), key=lambda kv: (-len(kv[1]), kv[0]))],
    }


def _relax(nodes, edges, idx):
    """Force relaxation with no wall and no randomness, and the three forces that need to be
    there. It is unbounded on purpose: a layout that clamps to the frame while it settles does
    not settle, it stacks against the edge, and the first version of this put thirty five of
    forty nodes on the boundary and drew a rectangle of dots. The drawing is FITTED to the
    frame afterwards instead, by a uniform scale, which cannot distort what the forces found."""
    n = len(nodes)
    cx, cy = W / 2.0, H / 2.0
    # A deterministic start on a golden angle spiral, ordered by reach. Every quantity here
    # comes out of the data or out of this file, so two builds begin identically.
    pos = []
    for i in range(n):
        a = i * 2.39996322972865332
        r = 30.0 + 26.0 * math.sqrt(i + 1)
        pos.append([cx + r * math.cos(a), cy + r * math.sin(a)])

    k = math.sqrt((W - 2 * PAD) * (H - 2 * PAD) / n) * 0.72
    cut = k * 4.2                    # beyond this, two nodes are not each other's problem
    temp = k * 0.9

    for it in range(ITERS):
        # A cooling curve rather than a straight line, so the shape is found early and the
        # last third is settling rather than reshuffling.
        t = temp * (1.0 - it / ITERS) ** 1.6
        disp = [[0.0, 0.0] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx = pos[i][0] - pos[j][0]
                dy = pos[i][1] - pos[j][1]
                d2 = dx * dx + dy * dy
                if d2 < 1e-6:
                    dx, dy, d2 = 0.01 * (i + 1), 0.01 * (j + 1), 1e-4
                d = math.sqrt(d2)
                if d > cut:
                    continue
                f = (k * k) / d
                ux, uy = dx / d, dy / d
                disp[i][0] += ux * f; disp[i][1] += uy * f
                disp[j][0] -= ux * f; disp[j][1] -= uy * f
        for ed in edges:
            i, j = idx[ed["a"]], idx[ed["b"]]
            dx = pos[i][0] - pos[j][0]
            dy = pos[i][1] - pos[j][1]
            d = math.sqrt(dx * dx + dy * dy) or 1e-4
            # A heavier link pulls harder, so companies sharing a campus sit together.
            f = (d * d) / k * (1.0 + math.log(1.0 + ed["w"]) * 0.55)
            ux, uy = dx / d, dy / d
            disp[i][0] -= ux * f; disp[i][1] -= uy * f
            disp[j][0] += ux * f; disp[j][1] += uy * f
        # GRAVITY, the force whose absence broke the first version. Repulsion is the only thing
        # acting on a component nothing links to, so without a pull toward the middle every
        # island accelerates away until a clamp catches it at the wall.
        #
        # It pulls HARDER VERTICALLY, in the SQUARE of the field's ratio. Relaxation with equal
        # gravity settles into a round drawing, and a round drawing fitted into a landscape
        # field is bound by its height and leaves a third of the width empty. Stretching the
        # gravity instead of stretching the result keeps the fit uniform, so the shape the
        # forces found is the shape on the page. The square rather than the ratio itself,
        # because at the plain ratio the drawing still came out little more than half the width
        # of the box it was fitted into.
        #
        # DERIVED AND NOT TUNED, deliberately. Relaxation is chaotic: this constant moved from
        # 2.6 to 2.601 in a trial and the drawing's width moved by thirty units, because two
        # clusters swapped which one sat above the other. Every layout of a given registry is
        # identical, which is all `site_fresh_check` needs, but a constant hand fitted to a
        # local best would sit on a cliff and the picture would reshuffle the day a facility is
        # added. A ratio that comes out of the field's own shape does not have that problem.
        gx = 0.075
        gy = gx * (W / H) ** 2
        for i in range(n):
            disp[i][0] += (cx - pos[i][0]) * gx
            disp[i][1] += (cy - pos[i][1]) * gy
        for i in range(n):
            dx, dy = disp[i]
            d = math.sqrt(dx * dx + dy * dy) or 1e-9
            step = min(d, t)
            pos[i][0] += dx / d * step
            pos[i][1] += dy / d * step
    return pos


def _fit(pos, rads, box):
    """Scale and centre a relaxed drawing into a box, uniformly. Uniform is the whole point:
    the forces found a shape and a non uniform fit would be a different shape."""
    x0, y0, x1, y1 = box
    lo_x = min(p[0] for p in pos); hi_x = max(p[0] for p in pos)
    lo_y = min(p[1] for p in pos); hi_y = max(p[1] for p in pos)
    w = max(hi_x - lo_x, 1e-6); h = max(hi_y - lo_y, 1e-6)
    r = max(rads) if rads else 0.0
    s = min((x1 - x0 - 2 * r) / w, (y1 - y0 - 2 * r) / h)
    mx = (x0 + x1) / 2.0 - (lo_x + hi_x) / 2.0 * s
    my = (y0 + y1) / 2.0 - (lo_y + hi_y) / 2.0 * s
    return [[p[0] * s + mx, p[1] * s + my] for p in pos]


def _uncrowd(pos, rads, rounds=90):
    """Push apart anything overlapping, in FINAL coordinates. The fit is a scale, so two nodes
    that were comfortably apart in relaxed space can touch after it, and a dot hidden under a
    bigger dot is a company a reader cannot point at."""
    n = len(pos)
    for _ in range(rounds):
        moved = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                dx = pos[j][0] - pos[i][0]
                dy = pos[j][1] - pos[i][1]
                d = math.sqrt(dx * dx + dy * dy)
                want = rads[i] + rads[j] + GAP
                if d >= want:
                    continue
                if d < 1e-6:
                    dx, dy, d = 1.0, 0.35, 1.0616
                push = (want - d) / 2.0
                ux, uy = dx / d, dy / d
                pos[i][0] -= ux * push; pos[i][1] -= uy * push
                pos[j][0] += ux * push; pos[j][1] += uy * push
                moved += push
        if moved < 0.05:
            break
    for i in range(n):
        pos[i][0] = min(W - PAD - rads[i], max(PAD + rads[i], pos[i][0]))
        pos[i][1] = min(H - PAD - rads[i], max(PAD + rads[i], pos[i][1]))
    return pos


def layout(g: dict) -> dict:
    """The field: a linked core, relaxed and fitted, inside a halo of what links to nothing.

    THE HALO IS INFORMATION, NOT DECORATION. A company on several facilities that shares none
    of them with another company is a real and different thing from one sitting in a cluster,
    and mixing the two into one cloud hides it. Nine of the forty are in that position. They
    ride an ellipse just inside the neatline, ordered by reach, so the reading is immediate:
    everything on the ring stands alone.
    """
    nodes, edges = g["nodes"], g["edges"]
    n = len(nodes)
    if not n:
        return g
    idx = {x["key"]: i for i, x in enumerate(nodes)}

    hi = max(x["reach"] for x in nodes)
    lo = min(x["reach"] for x in nodes)
    for node in nodes:
        # Area carries reach, so the radius is a square root. A radius carrying it directly
        # would overstate the biggest company by the square of its lead.
        t = 0.0 if hi == lo else (node["reach"] - lo) / (hi - lo)
        node["r"] = round(MIN_R + (MAX_R - MIN_R) * math.sqrt(t), 2)

    linked = {e["a"] for e in edges} | {e["b"] for e in edges}
    core = [x for x in nodes if x["key"] in linked]
    loose = [x for x in nodes if x["key"] not in linked]

    place: dict[str, list] = {}
    if core:
        ci = {x["key"]: i for i, x in enumerate(core)}
        cp = _relax(core, edges, ci)
        rads = [x["r"] for x in core]
        # The core takes the middle of the field. The inset leaves the ring its lane, and
        # collapses to the whole field when there is no ring to leave it for.
        inset = 0.74 if loose else 0.98
        bx = (W / 2.0) * (1.0 - inset) + PAD * inset
        by = (H / 2.0) * (1.0 - inset) + PAD * inset
        cp = _uncrowd(_fit(cp, rads, (bx, by, W - bx, H - by)), rads)
        for i, x in enumerate(core):
            place[x["key"]] = cp[i]

    if loose:
        rx = W / 2.0 - PAD - MAX_R
        ry = H / 2.0 - PAD - MAX_R
        for i, x in enumerate(loose):
            # Ordered around the ring, and drawn a little inboard the busier it is, so the ring
            # carries reach radially as well as in the size of the dot.
            a = (i / len(loose)) * math.tau - math.pi / 2.0
            t = 0.0 if hi == lo else (x["reach"] - lo) / (hi - lo)
            pull = 1.0 - 0.085 * t
            place[x["key"]] = [W / 2.0 + rx * pull * math.cos(a),
                               H / 2.0 + ry * pull * math.sin(a)]

    for node in nodes:
        x, y = place[node["key"]]
        node["x"] = round(min(W - PAD, max(PAD, x)), 2)
        node["y"] = round(min(H - PAD, max(PAD, y)), 2)
    return g


def build(entities: list[dict]) -> dict:
    return layout(graph(entities))


def payload(g: dict, base: str = "", facility_links: dict[str, str] | None = None) -> str:
    """What the browser needs to animate and explain the relationship field."""
    facility_links = facility_links or {}
    return json.dumps({
        "w": W, "h": H,
        "nodes": [{"k": n["key"], "n": n["name"], "s": n["slug"], "x": n["x"], "y": n["y"],
                   "r": n["r"], "c": n["reach"], "o": n["roles"],
                   "u": f"{base}{n['slug']}/"} for n in g["nodes"]],
        "edges": [{"a": e["a"], "b": e["b"], "w": e["w"],
                   "f": [{"n": name, "u": facility_links.get(name, "")}
                         for name in e["facilities"]]}
                  for e in g["edges"]],
    }, separators=(",", ":"), sort_keys=True)


# ---------------------------------------------------------------- rendering
def e(t) -> str:
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


# THE NAMES THAT STAND WITHOUT BEING ASKED FOR. Forty labels at once is a wall of type, and
# none at all is a picture a reader has to interrogate before it says anything.
#
# The first version put every standing label at the same offset to the right of its dot, which
# is fine until two busy companies sit near each other, and four of them did: "Lancium LLC" ran
# straight through "Oracle America Cloud Services LLC" on the shipped page. So a label is placed
# rather than offset. Each candidate side is tried in turn and the first one that clears every
# label already placed, every dot, and the edge of the field wins. A name with nowhere to go
# keeps its hover label and gives up its standing one, because a legible eight is worth more
# than an unreadable twelve.
LABELS = 12
LFS = 13.0                 # the label's font size, matched to `.glabel` in the stylesheet
LADV = 0.6                 # a monospaced advance, in ems. The face is JetBrains Mono.
LSIDES = (("start", 1, 4), ("end", -1, 4), ("start", 1, -13), ("end", -1, -13),
          ("start", 1, 20), ("end", -1, 20))


def _boxes_hit(a, b) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])


def standing(g: dict) -> dict:
    """Which nodes wear their name with no pointer on them, and exactly where."""
    ranked = sorted(g["nodes"], key=lambda n: (-n["reach"], n["name"].lower()))[:LABELS]
    taken = [(n["x"] - n["r"] - 2, n["y"] - n["r"] - 2, n["x"] + n["r"] + 2, n["y"] + n["r"] + 2)
             for n in g["nodes"]]
    out = {}
    for n in ranked:
        w = len(n["name"]) * LFS * LADV
        for anchor, side, dy in LSIDES:
            off = (n["r"] + 7.0) * side
            x0 = n["x"] + off - (w if side < 0 else 0.0)
            box = (x0 - 2, n["y"] + dy - LFS, x0 + w + 2, n["y"] + dy + 4)
            if box[0] < 2 or box[2] > W - 2 or box[1] < 2 or box[3] > H - 2:
                continue
            if any(_boxes_hit(box, t) for t in taken):
                continue
            taken.append(box)
            out[n["key"]] = (round(off, 2), dy, anchor)
            break
    return out


def svg(g: dict, base: str = "") -> str:
    """`base` is what a node's slug hangs off. The field draws links to company pages, and it
    used to be drawn only on the company index, where a bare `slug/` resolves. Moved to the
    data centers tab on 2026-08-22 the same bare href resolved under THAT directory and every
    node pointed at a page that does not exist. Forty one broken links, and the page itself
    looked perfectly well until one was clicked."""
    """The field, drawn server side so it exists with no script at all.

    Every coordinate here is computed by `layout`. `numeral_lint` strips svg geometry for
    exactly this reason: these are not figures a reader reads, they are the drawing itself.

    THE GLOW IS A FILTER, NOT A SECOND SET OF ELEMENTS. A blurred copy of the filaments under
    the crisp ones would double what the animation loop has to move on every frame. One
    `feMerge` does it in the compositor instead, and the interactive layer stays forty links.
    """
    if not g["nodes"]:
        return ""
    at = {n["key"]: n for n in g["nodes"]}
    hi = max(x["w"] for x in g["edges"]) if g["edges"] else 1

    grid = "".join(
        f'<line class="ggrid" x1="{x}" y1="0" x2="{x}" y2="{H}"/>'
        for x in range(50, int(W), 50)) + "".join(
        f'<line class="ggrid" x1="0" y1="{y}" x2="{W}" y2="{y}"/>'
        for y in range(50, int(H), 50))

    edges = ""
    edge_hits = ""
    for i, x in enumerate(g["edges"]):
        x1, y1 = at[x["a"]]["x"], at[x["a"]]["y"]
        x2, y2 = at[x["b"]]["x"], at[x["b"]]["y"]
        edges += (
            f'<line class="gedge" data-i="{i}" data-a="{e(x["a"])}" '
            f'data-b="{e(x["b"])}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'style="--w:{round(0.6 + 2.3 * (x["w"] / hi), 3)};'
            f'--o:{round(0.3 + 0.55 * (x["w"] / hi), 3)}" aria-hidden="true"/>')
        noun = "facility record" if x["w"] == 1 else "facility records"
        edge_hits += (
            f'<line class="gedgehit" data-i="{i}" x1="{x1}" y1="{y1}" '
            f'x2="{x2}" y2="{y2}" tabindex="0" role="button" '
            f'aria-label="{e(at[x["a"]]["name"])} and {e(at[x["b"]]["name"])} '
            f'share {x["w"]} certified {noun}"/>')

    stand = standing(g)

    nodes = ""
    for n in g["nodes"]:
        roles = " ".join(f'{k} {v}' for k, v in n["roles"].items())
        put = stand.get(n["key"])
        lx, ly, anchor = put or (round(n["r"] + 7, 2), 4, "start")
        hit_r = max(16, n["r"] + 9)
        nodes += (
            f'<a class="gnode{" gnamed" if put else ""}" data-k="{e(n["key"])}" '
            f'href="{e(base)}{e(n["slug"])}/" transform="translate({n["x"]},{n["y"]})" '
            f'aria-label="{e(n["name"])}, on {n["reach"]} facilities">'
            f'<circle class="ghalo" r="{round(n["r"] * 2.15, 2)}"/>'
            f'<circle class="gring" r="{round(n["r"] + 3.2, 2)}"/>'
            f'<circle class="gdot" r="{n["r"]}"/>'
            f'<circle class="ghit" r="{hit_r}" data-base-r="{hit_r}"/>'
            f'<text class="glabel" x="{lx}" y="{ly}" text-anchor="{anchor}">'
            f'{e(n["name"])}</text>'
            f'<title>{e(n["name"])}. {e(roles)}.</title></a>')

    # The cursor light. It starts off the field, so the drawing on disk is the drawing with no
    # pointer in it, and the script moves the gradient rather than adding anything.
    defs = (
        '<defs>'
        '<filter id="gglow" x="-35%" y="-35%" width="170%" height="170%">'
        '<feGaussianBlur stdDeviation="3.4" result="b"/>'
        '<feMerge><feMergeNode in="b"/><feMergeNode in="b"/>'
        '<feMergeNode in="SourceGraphic"/></feMerge></filter>'
        '<radialGradient id="gcursor" gradientUnits="userSpaceOnUse" '
        f'cx="{int(W / 2)}" cy="-{int(H)}" r="290">'
        '<stop offset="0" class="gcs0"/><stop offset="0.55" class="gcs1"/>'
        '<stop offset="1" class="gcs2"/></radialGradient>'
        '<radialGradient id="gvig" gradientUnits="objectBoundingBox" cx="0.5" cy="0.42" r="0.78">'
        '<stop offset="0.55" class="gvs0"/><stop offset="1" class="gvs1"/>'
        '</radialGradient>'
        '</defs>')

    return (
        f'<svg class="gsvg" viewBox="0 0 {int(W)} {int(H)}" role="img" '
        f'aria-labelledby="gttl" preserveAspectRatio="xMidYMid meet">'
        f'<title id="gttl">Every company on more than one certified Texas data center, '
        f'linked where they share one.</title>'
        f'{defs}'
        f'<g class="ggrids" aria-hidden="true">{grid}</g>'
        f'<rect class="gcursorlight" x="0" y="0" width="{int(W)}" height="{int(H)}" '
        f'fill="url(#gcursor)" aria-hidden="true"/>'
        f'<rect class="gvignette" x="0" y="0" width="{int(W)}" height="{int(H)}" '
        f'fill="url(#gvig)" aria-hidden="true"/>'
        f'<rect class="gneat" x="1" y="1" width="{int(W) - 2}" height="{int(H) - 2}"/>'
        f'<g class="gedges" filter="url(#gglow)">{edges}</g>'
        f'<g class="gedgehits">{edge_hits}</g>'
        f'<g class="gnodes">{nodes}</g></svg>')


SCRIPT = """
(function () {
  var root = document.getElementById('gfield');
  if (!root) return;
  var svg = root.querySelector('.gsvg');
  var data = document.getElementById('gdata');
  if (!svg || !data) return;
  var G;
  try { G = JSON.parse(data.textContent); } catch (err) { return; }

  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)');
  var nodes = [].slice.call(svg.querySelectorAll('.gnode'));
  var edges = [].slice.call(svg.querySelectorAll('.gedge'));
  var edgeHits = [].slice.call(svg.querySelectorAll('.gedgehit'));
  var lamp = svg.querySelector('#gcursor');
  var sheet = svg.querySelector('.ggrids');
  var controls = document.getElementById('gcontrols');
  var search = document.getElementById('gsearch');
  var role = document.getElementById('grole');
  var reset = document.getElementById('greset');
  var readName = document.getElementById('grname');
  var readMeta = document.getElementById('grmeta');
  var readRoles = document.getElementById('grroles');
  var readConnections = document.getElementById('grconnections');
  var readLink = document.getElementById('grlink');
  if (!readName || !readMeta || !readRoles || !readConnections || !readLink) return;
  var home = {
    name: readName.textContent, meta: readMeta.textContent,
    roles: readRoles.innerHTML, connections: readConnections.innerHTML,
    href: readLink.getAttribute('href'), link: readLink.textContent
  };
  var byKey = {};
  var edgeByKey = {};
  G.nodes.forEach(function (n) { byKey[n.k] = n; });

  // Every node remembers where the BUILD put it and springs back to it. The drawing on disk
  // stays the resting state, so motion never becomes the source of truth.
  var P = G.nodes.map(function (n, i) {
    var hit = nodes[i] && nodes[i].querySelector('.ghit');
    return { k: n.k, hx: n.x, hy: n.y, x: n.x, y: n.y, vx: 0, vy: 0, r: n.r,
      hr: hit ? Number(hit.getAttribute('data-base-r')) : 16 };
  });
  var pi = {};
  P.forEach(function (p, i) { pi[p.k] = i; });
  var links = G.edges.map(function (l) { return { a: pi[l.a], b: pi[l.b], w: l.w }; });

  var neigh = {};
  G.edges.forEach(function (l) {
    (neigh[l.a] = neigh[l.a] || {})[l.b] = 1;
    (neigh[l.b] = neigh[l.b] || {})[l.a] = 1;
  });

  G.edges.forEach(function (edge, i) {
    (edgeByKey[edge.a] = edgeByKey[edge.a] || []).push({ edge: edge, index: i });
    (edgeByKey[edge.b] = edgeByKey[edge.b] || []).push({ edge: edge, index: i });
  });

  function clear(el) { while (el.firstChild) el.removeChild(el.firstChild); }
  function make(tag, className, value) {
    var el = document.createElement(tag);
    if (className) el.className = className;
    if (value !== undefined) el.textContent = value;
    return el;
  }
  function noun(value, one, many) { return value === 1 ? one : many; }
  function facilityList(facilities, limit) {
    var list = make('ul', 'grfacilities');
    facilities.slice(0, limit || facilities.length).forEach(function (facility) {
      var row = make('li');
      var label = facility.u ? make('a', '', facility.n) : make('span', '', facility.n);
      if (facility.u) label.setAttribute('href', facility.u);
      row.appendChild(label); list.appendChild(row);
    });
    if (facilities.length > (limit || facilities.length)) {
      list.appendChild(make('li', 'grmore', facilities.length - limit + ' more ' +
        noun(facilities.length - limit, 'record', 'records')));
    }
    return list;
  }

  var mx = -1e5, my = -1e5, near = false, held = null, hot = null, press = null;
  var hotEdge = null;
  var suppressMiddleAux = false;
  var raf = 0, calm = 0;
  // The visible point stays on the data scale. Its transparent control does not. A phone needs
  // a forty four CSS pixel target even though the viewBox compresses one thousand units into a
  // few hundred screen pixels. Recompute only the transparent radius when the drawing resizes.
  var MIN_TARGET_PX = 44;
  function sizeTargets() {
    var matrix = svg.getScreenCTM();
    if (!matrix) return;
    var scale = Math.hypot(matrix.a, matrix.b);
    if (!scale) return;
    for (var i = 0; i < nodes.length; i++) {
      var hit = nodes[i].querySelector('.ghit');
      if (!hit) continue;
      var base = Number(hit.getAttribute('data-base-r')) || 16;
      var radius = Math.max(base, MIN_TARGET_PX / (2 * scale));
      hit.setAttribute('r', radius.toFixed(2));
      P[i].hr = radius;
    }
  }
  sizeTargets();
  if (window.ResizeObserver) new ResizeObserver(sizeTargets).observe(svg);
  else window.addEventListener('resize', sizeTargets);

  // Letting a point roam twenty six units meant it could leave the entire target a reader had
  // just aimed at. Twelve keeps the field alive while the original position remains inside it.
  var MAX_DRIFT = 12;

  function toField(ev) {
    // The SVG preserves its aspect ratio and can letterbox inside its CSS box. Scaling against
    // the box width and height treats that empty inset as drawing space and chooses the wrong
    // point where targets overlap. The browser's own screen matrix is the field it painted.
    var matrix = svg.getScreenCTM();
    if (!matrix) return [-1e5, -1e5];
    var point = svg.createSVGPoint();
    point.x = ev.clientX; point.y = ev.clientY;
    var field = point.matrixTransform(matrix.inverse());
    return [field.x, field.y];
  }

  function step() {
    raf = 0;
    var moved = 0;
    for (var i = 0; i < P.length; i++) {
      var p = P[i];
      // A point under a pointer or keyboard focus is an interface control first and a particle
      // second. Hold it still until the reader leaves it. The rest of the field can keep moving.
      if (held === i || hot === i) { p.vx = p.vy = 0; continue; }
      // Spring home.
      p.vx += (p.hx - p.x) * 0.012;
      p.vy += (p.hy - p.y) * 0.012;
      // The cursor pushes a local well. Falls off fast so the whole field does not heave.
      //
      // AND IT LETS GO AT THE CENTRE. Every point here is a link to a company, and the first
      // version pushed hardest exactly where the pointer was, so the node a reader was reaching
      // for stepped aside as they arrived and neither the hover nor the click ever landed. The
      // push ramps back to nothing inside the hit radius, so the field parts around the pointer
      // and the node under it stays where it is.
      if (near) {
        var dx = p.x - mx, dy = p.y - my;
        var d2 = dx * dx + dy * dy;
        if (d2 < 42000 && d2 > 0.01) {
          var d = Math.sqrt(d2);
          var f = (1 - d / 205) * 3.4;
          if (d < 42) f *= d / 42;
          p.vx += (dx / d) * f;
          p.vy += (dy / d) * f;
        }
      }
      p.vx *= 0.86; p.vy *= 0.86;
      p.x += p.vx; p.y += p.vy;
      // Motion shows that the network is connected, but a point may never wander so far from
      // its surveyed position that the reader loses the control they were approaching.
      var ox = p.x - p.hx, oy = p.y - p.hy;
      var od = Math.sqrt(ox * ox + oy * oy);
      if (od > MAX_DRIFT) {
        p.x = p.hx + ox / od * MAX_DRIFT;
        p.y = p.hy + oy / od * MAX_DRIFT;
        p.vx *= 0.35; p.vy *= 0.35;
      }
      moved += Math.abs(p.vx) + Math.abs(p.vy);
    }
    // A dragged node drags its links, which is the whole point of a web.
    if (held !== null) {
      for (var L = 0; L < links.length; L++) {
        var l = links[L];
        var o = l.a === held ? P[l.b] : (l.b === held ? P[l.a] : null);
        if (!o) continue;
        var h = P[held];
        o.vx += (h.x - o.x) * 0.006;
        o.vy += (h.y - o.y) * 0.006;
      }
      moved += 1;
    }
    paint();
    if (moved > 0.35) raf = requestAnimationFrame(step);
    else { calm = 1; paint(); }
  }

  function paint() {
    for (var i = 0; i < nodes.length; i++) {
      var p = P[i];
      nodes[i].setAttribute('transform', 'translate(' + p.x.toFixed(2) + ',' + p.y.toFixed(2) + ')');
    }
    for (var j = 0; j < edges.length; j++) {
      var l = links[j], a = P[l.a], b = P[l.b];
      edges[j].setAttribute('x1', a.x.toFixed(2)); edges[j].setAttribute('y1', a.y.toFixed(2));
      edges[j].setAttribute('x2', b.x.toFixed(2)); edges[j].setAttribute('y2', b.y.toFixed(2));
      if (edgeHits[j]) {
        edgeHits[j].setAttribute('x1', a.x.toFixed(2)); edgeHits[j].setAttribute('y1', a.y.toFixed(2));
        edgeHits[j].setAttribute('x2', b.x.toFixed(2)); edgeHits[j].setAttribute('y2', b.y.toFixed(2));
      }
    }
  }

  function kick() { calm = 0; if (!raf) raf = requestAnimationFrame(step); }

  function lightUp(key) {
    root.classList.toggle('lit', !!key);
    var near1 = key ? (neigh[key] || {}) : {};
    nodes.forEach(function (el) {
      var k = el.getAttribute('data-k');
      el.classList.toggle('focus', !!key && k === key);
      el.classList.toggle('on', !!key && (k === key || !!near1[k]));
      el.classList.toggle('off', !!key && k !== key && !near1[k]);
    });
    edges.forEach(function (el) {
      var on = !!key && (el.getAttribute('data-a') === key || el.getAttribute('data-b') === key);
      el.classList.toggle('on', on);
      el.classList.toggle('off', !!key && !on);
    });
  }

  function lightEdge(index) {
    var edge = G.edges[index];
    if (!edge) return;
    root.classList.add('lit');
    nodes.forEach(function (el) {
      var key = el.getAttribute('data-k');
      var on = key === edge.a || key === edge.b;
      el.classList.toggle('focus', on);
      el.classList.toggle('on', on);
      el.classList.toggle('off', !on);
    });
    edges.forEach(function (el, i) {
      el.classList.toggle('on', i === index);
      el.classList.toggle('off', i !== index);
    });
  }

  function renderRoles(node) {
    clear(readRoles);
    var labels = { owner: 'Owner', occupant: 'Occupant', operator: 'Operator' };
    ['owner', 'occupant', 'operator'].forEach(function (key) {
      if (!node.o || !node.o[key]) return;
      var chip = make('span', 'grrole');
      chip.appendChild(make('b', '', String(node.o[key])));
      chip.appendChild(document.createTextNode(labels[key]));
      readRoles.appendChild(chip);
    });
  }

  function renderNodeConnections(key) {
    clear(readConnections);
    var rows = (edgeByKey[key] || []).slice().sort(function (a, b) {
      return b.edge.w - a.edge.w;
    });
    readConnections.appendChild(make('p', 'grsection', rows.length ?
      'Why this company has lines' : 'No shared row with another repeat company'));
    if (!rows.length) {
      readConnections.appendChild(make('p', 'grquiet',
        'It repeats across the registry but never beside another company that also repeats.'));
      return;
    }
    rows.slice(0, 4).forEach(function (row) {
      var edge = row.edge;
      var other = byKey[edge.a === key ? edge.b : edge.a];
      var card = make('article', 'grconnection');
      var link = make('a', 'grcompany', other.n);
      link.setAttribute('href', other.u);
      card.appendChild(link);
      card.appendChild(make('span', 'grcount', edge.w + ' shared ' +
        noun(edge.w, 'facility record', 'facility records')));
      card.appendChild(facilityList(edge.f, 2));
      var inspect = make('button', 'grinspect', 'Inspect line');
      inspect.setAttribute('type', 'button'); inspect.setAttribute('data-edge', String(row.index));
      card.appendChild(inspect); readConnections.appendChild(card);
    });
  }

  function readOut(key, href) {
    if (!key || !byKey[key]) {
      readName.textContent = home.name;
      readMeta.textContent = home.meta;
      readRoles.innerHTML = home.roles;
      readConnections.innerHTML = home.connections;
      readLink.setAttribute('href', home.href);
      readLink.textContent = home.link;
      readLink.hidden = false;
      return;
    }
    var n = byKey[key];
    readName.textContent = n.n;
    readMeta.textContent = n.c + ' certified ' + noun(n.c, 'facility', 'facilities');
    renderRoles(n);
    renderNodeConnections(key);
    readLink.setAttribute('href', n.u || href);
    readLink.textContent = 'Open company profile';
    readLink.hidden = false;
  }

  function showEdge(index) {
    var edge = G.edges[index];
    if (!edge) return;
    var a = byKey[edge.a], b = byKey[edge.b];
    lightEdge(index);
    readName.textContent = a.n + ' and ' + b.n;
    readMeta.textContent = edge.w + ' shared certified ' +
      noun(edge.w, 'facility record', 'facility records');
    clear(readRoles); clear(readConnections);
    readConnections.appendChild(make('p', 'grsection', 'The records behind this line'));
    readConnections.appendChild(facilityList(edge.f));
    var first = edge.f.filter(function (facility) { return facility.u; })[0];
    if (first) {
      readLink.setAttribute('href', first.u);
      readLink.textContent = 'Open the first shared facility';
      readLink.hidden = false;
    } else readLink.hidden = true;
  }

  // Catch the approach, not only the final pixel. A mouse reaches a moving point through the
  // field around it, so the point settles as soon as the pointer enters that approach radius.
  // The visible dot and its 32 unit hit circle remain the actual link.
  function pointAt(x, y) {
    var found = null, best = Infinity;
    for (var i = 0; i < P.length; i++) {
      var dx = P[i].x - x, dy = P[i].y - y, d2 = dx * dx + dy * dy;
      if (d2 <= P[i].hr * P[i].hr && d2 <= best) { best = d2; found = i; }
    }
    return found;
  }

  function holdPoint(i) {
    if (i === null || i === undefined || !P[i]) return;
    hot = i; P[i].vx = P[i].vy = 0;
    var el = nodes[i], k = el.getAttribute('data-k');
    lightUp(k); readOut(k, el.getAttribute('href'));
  }

  function releasePoint(i) {
    // Enlarged controls can overlap. Leaving one while the pointer remains inside another must
    // transfer the readout instead of clearing it and waiting for an enter event that already
    // happened underneath the first control.
    if (near) {
      var next = pointAt(mx, my);
      if (next !== null) {
        if (next !== hot) holdPoint(next);
        return;
      }
    }
    if (hotEdge !== null) return;
    if (i !== null && i !== undefined && hot !== i) return;
    hot = null; lightUp(null); readOut(null, ''); kick();
  }

  if (!(still && still.matches)) {
    svg.addEventListener('pointermove', function (ev) {
      var f = toField(ev); mx = f[0]; my = f[1]; near = true;
      if (held === null) {
        var next = pointAt(mx, my);
        if (next !== hot) {
          if (next === null) releasePoint(hot);
          else holdPoint(next);
        }
      }
      // The light goes where the pointer is. Moving a gradient beats adding an element: the
      // paint is one attribute pair per frame and nothing enters the interactive layer.
      if (lamp) { lamp.setAttribute('cx', mx.toFixed(1)); lamp.setAttribute('cy', my.toFixed(1)); }
      if (sheet) {
        sheet.setAttribute('transform', 'translate(' + ((G.w / 2 - mx) * 0.018).toFixed(2) +
          ',' + ((G.h / 2 - my) * 0.018).toFixed(2) + ')');
      }
      root.classList.add('near');
      if (held !== null) { P[held].x = mx; P[held].y = my; P[held].vx = P[held].vy = 0; }
      kick();
    });
    svg.addEventListener('pointerleave', function () {
      near = false; held = null; hot = null; hotEdge = null; root.classList.remove('near');
      if (sheet) sheet.removeAttribute('transform');
      lightUp(null); readOut(null, '');
      kick();
    });
    svg.addEventListener('pointerdown', function (ev) {
      var button = ev.button === undefined ? 0 : ev.button;
      if (button !== 0 && button !== 1) return;
      var f = toField(ev); mx = f[0]; my = f[1]; near = true;
      // SVG paint order decides which overlapping anchor receives the event. The drawing's own
      // nearest point rule decides what the reader selected, so readout, drag and navigation all
      // start from this one result instead of from the incidental element under the pointer.
      var i = pointAt(mx, my);
      if (i === null) return;
      ev.preventDefault();
      if (button === 1) suppressMiddleAux = true;
      held = i; press = { i: i, x: ev.clientX, y: ev.clientY, id: ev.pointerId,
                          button: button };
      holdPoint(i); root.classList.add('dragging');
      try { svg.setPointerCapture(ev.pointerId); } catch (e2) {}
    });
    svg.addEventListener('pointerup', function (ev) {
      if (!press) return;
      var f = toField(ev); mx = f[0]; my = f[1];
      var moved = Math.abs(ev.clientX - press.x) + Math.abs(ev.clientY - press.y);
      var chosen = pointAt(mx, my);
      var pointerId = press.id, button = press.button;
      held = null; press = null; root.classList.remove('dragging');
      try { svg.releasePointerCapture(pointerId); } catch (e2) {}
      if (chosen !== null) holdPoint(chosen);
      if (moved <= 6 && chosen !== null) {
        ev.preventDefault();
        var href = nodes[chosen].getAttribute('href');
        var activation = new CustomEvent('companyactivate', {
          bubbles: true, cancelable: true, detail: { key: P[chosen].k, href: href }
        });
        if (root.dispatchEvent(activation)) {
          // Pointer capture means the resolved company can differ from the painted anchor that
          // first received the press. Preserve browser modifier intent using that resolved href.
          // A features string containing only noopener keeps Ctrl or Meta in tab territory. The
          // popup hint gives Shift the separate-window style readers expect from a native link.
          if (button === 1) {
            window.open(href, '_blank', 'noopener');
            window.focus();
          }
          else if (ev.ctrlKey || ev.metaKey) window.open(href, '_blank', 'noopener');
          else if (ev.shiftKey) window.open(href, '_blank', 'noopener,popup=yes');
          else window.location.assign(href);
        }
      }
      kick();
    });
    svg.addEventListener('pointercancel', function (ev) {
      held = null; press = null; suppressMiddleAux = false; root.classList.remove('dragging');
      try { svg.releasePointerCapture(ev.pointerId); } catch (e2) {}
      kick();
    });
  }

  // Keyboard focus keeps using the real anchors. Pointer selection belongs to the field level
  // resolver above because transparent targets can overlap.
  nodes.forEach(function (el) {
    var k = el.getAttribute('data-k');
    var i = pi[k];
    el.addEventListener('focus', function () { holdPoint(i); });
    el.addEventListener('blur', function () { releasePoint(i); });
  });

  // A filament is a compact evidence control. It never navigates by itself: hover, focus and
  // click all disclose the exact registry rows in the stable lens beside the field.
  edgeHits.forEach(function (el) {
    var index = Number(el.getAttribute('data-i'));
    el.addEventListener('pointerenter', function () {
      hotEdge = index; hot = null; showEdge(index);
    });
    el.addEventListener('pointerleave', function () {
      hotEdge = null;
      if (document.activeElement !== el) { lightUp(null); readOut(null, ''); }
    });
    el.addEventListener('focus', function () { hotEdge = index; showEdge(index); });
    el.addEventListener('blur', function () {
      hotEdge = null; lightUp(null); readOut(null, '');
    });
    el.addEventListener('keydown', function (ev) {
      if (ev.key === 'Enter' || ev.key === ' ') { ev.preventDefault(); showEdge(index); }
    });
    el.addEventListener('click', function () { showEdge(index); });
  });

  readConnections.addEventListener('click', function (ev) {
    var button = ev.target.closest ? ev.target.closest('.grinspect') : null;
    if (button) showEdge(Number(button.getAttribute('data-edge')));
  });

  function findMatch() {
    if (!search) return null;
    var query = search.value.trim().toLowerCase();
    if (!query) return null;
    return G.nodes.find(function (node) { return node.n.toLowerCase().indexOf(query) === 0; }) ||
      G.nodes.find(function (node) { return node.n.toLowerCase().indexOf(query) !== -1; });
  }
  if (search) {
    search.addEventListener('input', function () {
      var match = findMatch();
      if (match) { lightUp(match.k); readOut(match.k, match.u); }
      else { lightUp(null); readOut(null, ''); }
    });
    search.addEventListener('keydown', function (ev) {
      var match = findMatch();
      if (ev.key === 'Enter' && match) { ev.preventDefault(); window.location.assign(match.u); }
      if (ev.key === 'Escape') { search.value = ''; lightUp(null); readOut(null, ''); }
    });
  }

  function emphasizeRole() {
    var chosen = role ? role.value : '';
    nodes.forEach(function (el) {
      var node = byKey[el.getAttribute('data-k')];
      el.classList.toggle('filtered', !!chosen && !(node.o || {})[chosen]);
    });
    edges.forEach(function (el, i) {
      var edge = G.edges[i];
      var hidden = !!chosen && (!(byKey[edge.a].o || {})[chosen] ||
        !(byKey[edge.b].o || {})[chosen]);
      el.classList.toggle('filtered', hidden);
      if (edgeHits[i]) edgeHits[i].classList.toggle('filtered', hidden);
    });
    lightUp(null); readOut(null, '');
  }
  if (role) role.addEventListener('change', emphasizeRole);
  if (reset) reset.addEventListener('click', function () {
    if (search) search.value = '';
    if (role) role.value = '';
    emphasizeRole();
    if (search) search.focus();
  });

  // Pointer navigation is resolved above. A keyboard-generated anchor click has detail zero and
  // keeps the native link behavior, including the destination when scripts are unavailable.
  svg.addEventListener('click', function (ev) {
    if (ev.detail > 0) ev.preventDefault();
  }, true);
  svg.addEventListener('auxclick', function (ev) {
    if (ev.button === 1 && suppressMiddleAux) {
      ev.preventDefault(); suppressMiddleAux = false;
    }
  }, true);

  if (controls) controls.hidden = false;
  root.classList.add('live');
})();
"""


def problems(g: dict) -> list[str]:
    out = []
    for n in g["nodes"]:
        if not (PAD - 0.5 <= n["x"] <= W - PAD + 0.5 and PAD - 0.5 <= n["y"] <= H - PAD + 0.5):
            out.append(f"node {n['name']!r} was laid out beyond the neatline")
    keys = {n["key"] for n in g["nodes"]}
    for e in g["edges"]:
        if e["a"] not in keys or e["b"] not in keys:
            out.append(f"edge {e['a']}-{e['b']} names a node that is not drawn")
    return out


def self_test() -> int:
    checks = []

    def ok(name, cond, extra=""):
        checks.append(bool(cond))
        print(f"  {'ok  ' if cond else 'FAIL'}  {name}{'' if cond else '  ' + str(extra)}")

    def ent(key, reach, facs):
        return {"key": key, "name": key.title(), "slug": key, "reach": reach,
                "roles": {"owner": facs}, "facilities": facs}

    es = [ent("a", 3, ["f1", "f2", "f3"]), ent("b", 2, ["f1", "f2"]),
          ent("c", 2, ["f3", "f4"]), ent("d", 1, ["f9"])]
    g = graph(es)
    ok("a company on one facility is not a node", [n["key"] for n in g["nodes"]] == ["a", "b", "c"],
       [n["key"] for n in g["nodes"]])
    ok("an edge exists where two companies share a facility",
       {(e["a"], e["b"]) for e in g["edges"]} == {("a", "b"), ("a", "c")},
       g["edges"])
    ok("...weighted by how many they share",
       [e["w"] for e in g["edges"] if e["a"] == "a" and e["b"] == "b"] == [2], g["edges"])
    ok("...and the exact rows behind the line are retained",
       [e["facilities"] for e in g["edges"] if e["a"] == "a" and e["b"] == "b"]
       == [["f1", "f2"]], g["edges"])

    # THE PROPERTY THE WHOLE BUILD DEPENDS ON.
    one, two = build([dict(x) for x in es]), build([dict(x) for x in es])
    ok("two layouts of the same registry are identical", payload(one) == payload(two))
    ok("...and the positions are real numbers inside the field", not problems(one), problems(one))

    ok("area carries reach, so the radius is its square root",
       one["nodes"][0]["r"] > one["nodes"][1]["r"], [n["r"] for n in one["nodes"]])
    wired = json.loads(payload(one, "../company/", {"f1": "../facility/f1/"}))
    ok("the browser payload carries company and source-row routes",
       wired["nodes"][0]["u"].startswith("../company/")
       and any(f == {"n": "f1", "u": "../facility/f1/"}
               for edge in wired["edges"] for f in edge["f"]), wired)
    drawing = svg(one, "../company/")
    ok("the server drawing keeps company links and inspectable edge targets",
       'href="../company/a/"' in drawing and 'class="gedgehit"' in drawing, drawing[:500])

    big = build([ent(f"n{i}", 2 + (i % 5), [f"s{i}", f"s{(i+1) % 30}"]) for i in range(30)])
    ok("a larger graph still lands inside the neatline", not problems(big), problems(big)[:2])
    ok("...with every node placed", all("x" in n for n in big["nodes"]))

    ok("an empty registry does not crash", build([])["nodes"] == [])

    bad = {"nodes": [{"key": "a", "name": "A", "x": -50, "y": 5, "r": 4, "reach": 2}], "edges": []}
    ok("a node outside the field is reported", problems(bad))
    ok("an edge to a node that is not drawn is reported",
       problems({"nodes": [], "edges": [{"a": "x", "b": "y", "w": 1}]}))

    ok("field activation preserves tab modifiers with noopener",
       "ev.ctrlKey || ev.metaKey" in SCRIPT and
       "window.open(href, '_blank', 'noopener')" in SCRIPT)
    ok("field activation preserves a Shift window with noopener",
       "ev.shiftKey" in SCRIPT and
       "window.open(href, '_blank', 'noopener,popup=yes')" in SCRIPT)
    ok("middle click uses the field resolver and a noopener tab",
       "button !== 0 && button !== 1" in SCRIPT and
       "button === 1" in SCRIPT and "suppressMiddleAux" in SCRIPT and
       "window.open(href, '_blank', 'noopener')" in SCRIPT)

    passed = sum(checks)
    print(f"\nregistry_graph self-test: {passed}/{len(checks)} passed")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import entities as E
    g = build(E.load()["entities"])
    bad = problems(g)
    if bad:
        print(f"registry_graph: {len(bad)} problem(s)")
        for b in bad:
            print(f"  {b}")
        sys.exit(1)
    print(f"registry_graph: {len(g['nodes'])} nodes, {len(g['edges'])} edges, "
          f"payload {len(payload(g)):,} bytes")
    sys.exit(0)
