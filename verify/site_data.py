#!/usr/bin/env python3
"""Build site/data.js: the numbers behind the landing page's leaderboard and charts. Standard library only.

    python3 verify/site_data.py > site/data.js

Like BOARD.md, everything here is computed from files in this repository: the queues, the accepted records,
answer/results.json, the ledger index and MAINTAINERS. Nothing is an agent's own account of its work, and the page
shows nothing that this file does not carry.

Optional keys this script passes through when a unit or a result has them, so other work can add them without a
change here:
- a queue unit's "field" (otherwise the field is worked out from the unit, see unit_field)
- a result's or a unit's "frontier" (true marks it as potentially frontier-expanding) and "field"
- answer/open-problems.json, if it exists: a list of {"field", "title", ...} shown per field
"""
import datetime
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U  # noqa: E402

FIELDS = ("Mathematics", "Physics", "Computer science and AI", "Biology", "Medicine", "Other fields")


def field_of(label):
    """Fold the ledger's free-text field labels into six buckets, by how the label starts."""
    s = (label or "").strip().lower()
    for prefix, name in (("math", "Mathematics"), ("combinator", "Mathematics"), ("number theory", "Mathematics"),
                         ("physic", "Physics"), ("computer", "Computer science and AI"),
                         ("ai", "Computer science and AI"), ("biolog", "Biology"), ("medic", "Medicine")):
        if s.startswith(prefix):
            return name
    return "Other fields"


def ledger_rows():
    path = os.path.join(U.ROOT, "ledger", "INDEX.md")
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            m = re.match(r"^\| (UQ-(\d{4})(\d{2})(\d{2})-\d+) \| (\w+) \| (.*?) \| (.*) \|\s*$", line)
            if m:
                rows.append({"id": m.group(1), "date": "-".join(m.group(2, 3, 4)), "status": m.group(5),
                             "field": field_of(m.group(6))})
    return rows


def unit_field(u, ledger_field):
    if u.get("field"):
        return field_of(u["field"]) if field_of(u["field"]) != "Other fields" else u["field"]
    inp = u.get("inputs", {})
    if inp.get("ledger_entry") in ledger_field:
        return ledger_field[inp["ledger_entry"]]
    if u["type"] in ("answer-reproduce", "answer-piece") or u["id"].startswith("V-LR-"):
        return "Mathematics"      # every founding answer unit is a van der Waerden-type computation
    if u["type"] == "ask-generate":
        return "Any field"
    return field_of(inp["area"]) if inp.get("area") else "Other fields"


def results(units):
    """The claims on the board, with outside progress as numbers (the same rules as board.py's answers())."""
    path = os.path.join(U.ROOT, "answer", "results.json")
    out = []
    for r in (json.load(open(path)) if os.path.exists(path) else []):
        row = {"claim": r["claim"], "inside": r.get("inside", ""), "frontier": bool(r.get("frontier")),
               "field": r.get("field", "Mathematics"), "have": 0, "want": 0, "refuted": False, "kind": "none"}
        if r.get("unit") and r["unit"] in units:
            recs = U.subs(r["unit"]).values()
            row.update(kind="reproductions", unit=r["unit"], want=units[r["unit"]].get("replicas", 1),
                       have=sum(1 for x in recs if x.get("result") == "Confirms"),
                       refuted=any(x.get("result") == "Refutes" for x in recs))
        elif r.get("piece_family"):
            pieces = []
            for k in sorted(units):
                if k.startswith(r["piece_family"]):
                    recs = list(U.subs(k).values())
                    none = sum(1 for x in recs if x.get("result") == "None")
                    pieces.append({"id": k, "records": min(none, units[k].get("replicas", 1)),
                                   "want": units[k].get("replicas", 1),
                                   "found": any(x.get("result") == "Found" for x in recs)})
            row.update(kind="pieces", family=r["piece_family"], pieces=pieces, want=len(pieces),
                       have=sum(1 for p in pieces if p["records"] >= p["want"]),
                       refuted=any(p["found"] for p in pieces))
        row["inside_confirmed"] = row["inside"].lower().startswith("confirmed")
        out.append(row)
    return out


def main():
    units = U.load_all()
    led = ledger_rows()
    ledger_field = {r["id"]: r["field"] for r in led}
    maint_path = os.path.join(U.ROOT, "MAINTAINERS")
    maintainers = [x.strip() for x in open(maint_path) if x.strip() and not x.startswith("#")] \
        if os.path.exists(maint_path) else []

    people, days, by_type, open_by_field = {}, {}, {}, {}
    total_records = 0
    for uid, u in units.items():
        t = by_type.setdefault(u["type"], {"type": u["type"], "area": U.area(uid), "units": 0, "done": 0})
        t["units"] += 1
        fin = U.done(u)
        t["done"] += fin
        if not fin and not u.get("maintainers_only"):
            f = unit_field(u, ledger_field)
            o = open_by_field.setdefault(f, {"field": f, "ask": 0, "answer": 0, "frontier": 0})
            o[U.area(uid)] += 1
            o["frontier"] += bool(u.get("frontier"))
        for h, rec in U.subs(uid).items():
            total_records += 1
            p = people.setdefault(h, {"handle": h, "records": 0, "conclusive": 0, "ask": 0, "answer": 0,
                                      "units": 0, "last": "", "maintainer": h in maintainers})
            p["records"] += 1
            p["conclusive"] += U.conclusive(rec)
            p[U.area(uid)] += 1
            p["units"] += 1
            day = str(rec.get("finished", ""))[:10]
            if re.match(r"^\d{4}-\d{2}-\d{2}$", day):
                p["last"] = max(p["last"], day)
                days[day] = days.get(day, 0) + 1
    board = sorted(people.values(), key=lambda p: (-p["conclusive"], -p["records"], p["handle"].lower()))

    by_field = {f: {"field": f, "Validated": 0, "Provisional": 0, "Rejected": 0, "other": 0} for f in FIELDS}
    timeline = {}
    totals = {"tried": len(led), "Validated": 0, "Provisional": 0, "Rejected": 0}
    for r in led:
        key = r["status"] if r["status"] in ("Validated", "Provisional", "Rejected") else "other"
        by_field[r["field"]][key] += 1
        if key != "other":
            totals[key] += 1
        d = timeline.setdefault(r["date"], {"date": r["date"], "tried": 0, "surviving": 0})
        d["tried"] += 1
        d["surviving"] += key in ("Validated", "Provisional")

    problems_path = os.path.join(U.ROOT, "answer", "open-problems.json")
    data = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "units": {"total": len(units), "done": sum(t["done"] for t in by_type.values()),
                  "by_type": sorted(by_type.values(), key=lambda t: (t["area"], t["type"]))},
        "records": {"total": total_records, "by_day": [{"date": d, "n": n} for d, n in sorted(days.items())]},
        "contributors": board,
        "results": results(units),
        "open_by_field": sorted(open_by_field.values(), key=lambda o: (-(o["ask"] + o["answer"]), o["field"])),
        "ledger": {"totals": totals, "by_field": [by_field[f] for f in FIELDS if sum(
            v for k, v in by_field[f].items() if k != "field")], "by_day": [timeline[d] for d in sorted(timeline)]},
        "open_problems": json.load(open(problems_path)) if os.path.exists(problems_path) else [],
    }
    print("// Generated by verify/site_data.py from the records in this repository. Do not edit by hand.")
    print("window.SWARM_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";")


if __name__ == "__main__":
    main()
