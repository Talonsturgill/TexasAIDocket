#!/usr/bin/env python3
"""Prepare the sourced registry for Flourish without a second entity-resolution rule.

The Points and Links sheets use the same company identities as the site. A connection
requires both companies on the SAME certification row. Re-certifications remain separate
in the evidence while the network's weight counts distinct facility names, like the
company pages. The export never uploads or publishes anything.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import pathlib
from collections import defaultdict
from itertools import combinations

import entities

ROOT = pathlib.Path(__file__).resolve().parents[2]
POINT_FIELDS = ("id", "company", "facilities", "owners", "occupants", "operators",
                "connections", "profile", "details", "source", "read")
LINK_FIELDS = ("source", "target", "shared_facilities", "certifications", "details")


def canonical(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def record_id(row: dict) -> str:
    return hashlib.sha256(canonical(row).encode()).hexdigest()[:16]


def build(registry: dict, dossiers: dict, site_url: str) -> dict:
    rows = registry.get("facilities") or []
    resolved = entities.resolve(rows)
    repeated = {entity["key"]: entity for entity in resolved if entity["reach"] > 1}
    source = registry.get("source", "")
    read = registry.get("read", "")
    dossier_at = {item["name"]: item for item in dossiers.get("dossiers", [])}
    entity_at = {entity["key"]: entity for entity in resolved}
    evidence = []
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    by_company: dict[str, list[dict]] = defaultdict(list)

    for row in sorted(rows, key=lambda item: (item["name"].casefold(), item["effective"], canonical(item))):
        members = set()
        roles = {}
        for role in entities.ROLES:
            parties = []
            for raw in row.get(role) or []:
                key = entities.normalise(raw)
                if not key or key not in entity_at:
                    continue
                members.add(key)
                entity = entity_at[key]
                parties.append({"name": raw, "key": key,
                                "href": f"{site_url}/company/{entity['slug']}/"
                                if entity["reach"] >= entities.MIN_REACH else ""})
            roles[role[:-1]] = parties
        dossier = dossier_at.get(row["name"])
        record = {"id": record_id(row), "name": row["name"],
                  "effective": row["effective"], "roles": roles,
                  "href": f"{site_url}/facility/{dossier['slug']}/" if dossier else "",
                  "source": source}
        evidence.append(record)
        for key in members:
            by_company[key].append(record)
        for pair in combinations(sorted(members & repeated.keys()), 2):
            by_pair[pair].append(record)

    def refs(records: list[dict]) -> str:
        names = {}
        for record in records:
            names[record["name"]] = record["href"]
        out = []
        for name, href in sorted(names.items(), key=lambda item: item[0].casefold()):
            label = html.escape(name)
            if href:
                label = f'<a href="{html.escape(href, quote=True)}" target="_blank" rel="noopener">{label}</a>'
            out.append(f"<li>{label}</li>")
        return "<ul>" + "".join(out) + "</ul>"

    links = []
    neighbours: dict[str, set[str]] = defaultdict(set)
    for (a, b), records in by_pair.items():
        neighbours[a].add(b)
        neighbours[b].add(a)
        # Flourish uses the point ID as its visible label. Keep the resolved filed
        # spelling here, not the lower-case normalization key used for matching.
        links.append({"source": repeated[a]["name"], "target": repeated[b]["name"],
                      "shared_facilities": len({record["name"] for record in records}),
                      "certifications": len(records), "details": refs(records)})
    links.sort(key=lambda link: (-link["shared_facilities"], link["source"], link["target"]))
    points = []
    for key, entity in repeated.items():
        points.append({"id": entity["name"], "company": entity["name"], "facilities": entity["reach"],
                       "owners": len(entity["roles"].get("owner", [])),
                       "occupants": len(entity["roles"].get("occupant", [])),
                       "operators": len(entity["roles"].get("operator", [])),
                       "connections": len(neighbours[key]),
                       "profile": f"{site_url}/company/{entity['slug']}/",
                       "details": refs(by_company[key]), "source": source, "read": read})
    content = {"points": points, "links": links, "records": evidence}
    return {"schema": 1, "registry_read": read, "source": source,
            "content_sha256": hashlib.sha256(canonical(content).encode()).hexdigest(),
            "counts": {"certifications": len(rows),
                       "facility_names": len({row["name"] for row in rows}),
                       "companies": len(resolved), "repeat_companies": len(points),
                       "connections": len(links)},
            "definitions": {
                "point": "A resolved company named at more than one facility.",
                "point_size": "Distinct facility names naming this company in any filed role.",
                "link": "Companies named together on the same certification row.",
                "link_weight": "Distinct facility names shared by the two companies.",
                "roles": "Roles in the state filing. These do not establish corporate control.",
                "effective": "Certification effective date. This is not an opening date."},
            **content}


def as_csv(items: list[dict], fields: tuple[str, ...]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(items)
    return output.getvalue()


def export(destination: pathlib.Path) -> dict:
    # Use the site's canonical URL instead of maintaining a second brand constant.
    from site_context import SITE_URL

    registry = json.loads((ROOT / "ledger/gridwatch/datacenters.json").read_text())
    dossiers = json.loads((ROOT / "ledger/facilities/dossiers.json").read_text())
    result = build(registry, dossiers, SITE_URL)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "network.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    (destination / "points.csv").write_text(as_csv(result["points"], POINT_FIELDS))
    (destination / "links.csv").write_text(as_csv(result["links"], LINK_FIELDS))
    return result


def self_test() -> int:
    def row(name, date, owner, occupant):
        return {"name": name, "effective": date, "owners": owner,
                "occupants": occupant, "operators": []}

    rows = [row("Shared <site>", "2025-01-01", ["A, LLC"], ["B Inc."]),
            row("A second", "2025-02-01", ["A LLC"], []),
            row("B second", "2025-03-01", [], ["B, Inc."]),
            row("Shared <site>", "2026-01-01", ["A LLC"], ["B Inc."]),
            row("Same name", "2025-01-01", ["A LLC"], []),
            row("Same name", "2026-01-01", ["C LLC"], []),
            row("C second", "2026-02-01", ["C LLC"], [])]
    registry = {"read": "2026-09-13", "source": "https://example.com/registry", "facilities": rows}
    result = build(registry, {"dossiers": []}, "https://example.com")
    checks = {
        "spelling variants resolve together": len(result["points"]) == 3,
        "a shared name across different rows invents no edge": len(result["links"]) == 1,
        "re-certification preserves evidence without doubling facility weight":
            result["links"][0]["shared_facilities"] == 1 and result["links"][0]["certifications"] == 2,
        "source names are escaped in popup HTML":
            "&lt;site&gt;" in result["links"][0]["details"] and "<site>" not in result["links"][0]["details"],
        "every certification survives": len(result["records"]) == len(rows),
        "record ids are unique across re-certifications":
            len({record["id"] for record in result["records"]}) == len(rows),
        "every link joins displayed company identities":
            all(link[end] in {point["id"] for point in result["points"]}
                for link in result["links"] for end in ("source", "target")),
        "identical inputs produce identical exports":
            canonical(result) == canonical(build(registry, {"dossiers": []}, "https://example.com")),
        "CSV round trip retains punctuation and HTML":
            list(csv.DictReader(io.StringIO(as_csv(result["points"], POINT_FIELDS))))[0]["company"] == result["points"][0]["company"],
    }
    for label, passed in checks.items():
        print(f"{'ok' if passed else 'FAIL'}  {label}")
    return 0 if all(checks.values()) else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    if args.out is None:
        parser.error("--out is required when exporting")
    result = export(args.out)
    print(json.dumps({"output": str(args.out.resolve()), "read": result["registry_read"],
                      "counts": result["counts"], "sha256": result["content_sha256"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
