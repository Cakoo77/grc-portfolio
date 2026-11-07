#!/usr/bin/env python3
"""Validate the Orvanta master data: unique IDs, resolvable references, headcount, fleet totals."""
import json
import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "00-company-profile" / "data" / "orvanta_master.json"
EXPECTED_HEADCOUNT = 120


def main() -> int:
    m = json.loads(DATA.read_text(encoding="utf-8"))
    errors = []

    id_sets = {}
    for key in ("roles", "processes", "systems", "data_classes", "vendors", "data_flows", "regulations", "observations"):
        ids = [x["id"] for x in m[key]]
        if len(ids) != len(set(ids)):
            errors.append(f"Duplicate IDs in {key}")
        id_sets[key] = set(ids)

    roles, systems, data_classes = id_sets["roles"], id_sets["systems"], id_sets["data_classes"]
    for r in m["roles"]:
        if r["reports_to"] and r["reports_to"] not in roles:
            errors.append(f"{r['id']}: unknown manager {r['reports_to']}")
    for d in m["departments"]:
        if d["lead"] not in roles:
            errors.append(f"Department {d['name']}: unknown lead {d['lead']}")
    for p in m["processes"]:
        if p["owner"] not in roles:
            errors.append(f"{p['id']}: unknown owner {p['owner']}")
        errors += [f"{p['id']}: unknown system {s}" for s in p["systems"] if s not in systems]
    for s in m["systems"]:
        if s["owner"] not in roles:
            errors.append(f"{s['id']}: unknown owner {s['owner']}")
        errors += [f"{s['id']}: unknown data class {c}" for c in s["data"] if c not in data_classes]
    for key in ("regulations", "observations"):
        for x in m[key]:
            if x["owner"] not in roles:
                errors.append(f"{x['id']}: unknown owner {x['owner']}")
    for f in m["data_flows"]:
        for ref in re.findall(r"SYS-\d+", f["from"] + f["to"]):
            if ref not in systems:
                errors.append(f"{f['id']}: unknown system {ref}")
    for x in m["maturity"]:
        for ref in re.findall(r"OBS-\d+", x["basis"]):
            if ref not in id_sets["observations"]:
                errors.append(f"Maturity {x['domain']}: unknown {ref}")
        if not 0 <= x["score"] <= 5:
            errors.append(f"Maturity {x['domain']}: score out of range")

    headcount = sum(d["vilnius"] + d["baku"] + d["remote"] for d in m["departments"])
    if headcount != EXPECTED_HEADCOUNT:
        errors.append(f"Headcount {headcount}, expected {EXPECTED_HEADCOUNT}")
    if len(m["vendors"]) != 20:
        errors.append(f"Vendors {len(m['vendors'])}, expected 20")

    print(f"roles={len(roles)} processes={len(id_sets['processes'])} systems={len(systems)} "
          f"vendors={len(id_sets['vendors'])} flows={len(id_sets['data_flows'])} "
          f"regs={len(id_sets['regulations'])} obs={len(id_sets['observations'])} headcount={headcount}")
    if errors:
        print("\n".join("ERROR: " + e for e in errors))
        return 1
    print("Master data OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
