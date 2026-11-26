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
- a result's "importance" (1 well-known problem, 2 open in the literature, 3 correction of a published value,
  4 extension of a published record), and the ladder keys rung() reads: "literature_checked", "reviewed",
  "accepted", "withdrawn", "novelty_confirmed"
- a result's "also_units" (unit ids whose records also earn credit on the claim), and CONTRIBUTORS.json at the
  repository root (display names contributors chose for themselves). `--credits` prints the credit sentence per claim
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
    names = display_names()
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
        row.update(rung=rung(r, row), importance=r.get("importance") if r.get("importance") in (1, 2, 3, 4) else 4,
                   novelty_confirmed=bool(r.get("novelty_confirmed")),
                   note=str(r.get("accepted") or r.get("reviewed") or r.get("withdrawn") or ""))
        row["credits"] = credits(r, units, names)
        out.append(row)
    return out


ROLE = {"answer-reproduce": "tried a reproduction", "answer-piece": "searched a piece",
        "answer-attempt": "attempted an answer", "answer-impact": "assessed the impact",
        "ask-generate": "asked the question", "ask-research": "researched prior work",
        "ask-adversary": "challenged it", "ask-judge": "judged it", "ask-verify": "checked the literature"}


def credits(r, units, names):
    """Who has an accepted record on a claim's units, and for what (ANNOUNCEMENTS.md, "Credit"). The units are the
    claim's "unit", every unit of its "piece_family", and any listed under "also_units" (for example a literature
    check several claims depend on). One entry per GitHub handle, with a count per role; an inconclusive record is
    credited too, as on the leaderboard. A handle's display name comes from CONTRIBUTORS.json, if they added one."""
    ids = [k for k in units if k == r.get("unit") or k in (r.get("also_units") or [])
           or (r.get("piece_family") and k.startswith(r["piece_family"]))]
    people = {}
    for uid in sorted(ids):
        for h, rec in U.subs(uid).items():
            role = ROLE.get(units[uid]["type"], "contributed a record")
            if units[uid]["type"] == "answer-reproduce" and rec.get("result") in ("Confirms", "Refutes"):
                role = "reproduced it" if rec["result"] == "Confirms" else "refuted it"
            if not U.conclusive(rec):
                role += " (inconclusive)"
            p = people.setdefault(h, {"handle": h, "name": names.get(h, ""), "roles": {}, "conclusive": 0})
            p["roles"][role] = p["roles"].get(role, 0) + 1
            p["conclusive"] += U.conclusive(rec)
    out = sorted(people.values(), key=lambda p: (-p["conclusive"], -sum(p["roles"].values()), p["handle"].lower()))
    for p in out:
        p["roles"] = [{"role": k, "n": n} for k, n in sorted(p["roles"].items(), key=lambda kv: (-kv[1], kv[0]))]
    return out


def display_names():
    """CONTRIBUTORS.json at the repository root: {"github-handle": "Name as it should appear"}. Optional; a
    contributor adds their own line by pull request. Without one, credit is by handle."""
    path = os.path.join(U.ROOT, "CONTRIBUTORS.json")
    if not os.path.exists(path):
        return {}
    return {str(k): " ".join(str(v).split())[:80] for k, v in json.load(open(path)).items() if isinstance(v, str)}


def credit_line(row):
    """One sentence naming everyone with a record on a claim, for an announcement or an acknowledgement."""
    if not row["credits"]:
        return "No contributor record yet."
    parts = []
    for p in row["credits"]:
        who = (p["name"] + " (@" + p["handle"] + ")") if p["name"] else "@" + p["handle"]
        parts.append(who + ": " + ", ".join(x["role"] + (" x" + str(x["n"]) if x["n"] > 1 else "") for x in p["roles"]))
    return "; ".join(parts) + "."


RUNGS = ("Lead, not confirmed", "Confirmed inside the project", "Reproduced outside",
         "Reviewed by experts", "Accepted")


def rung(r, row):
    """Where a claim stands on the verification ladder (ANNOUNCEMENTS.md): 0 lead, 1 confirmed inside the project,
    2 reproduced outside, 3 reviewed by experts, 4 accepted; -1 withdrawn. Rungs 0 to 2 are computed from the
    records. Rungs 3 and 4 need a maintainer to write who reviewed it ("reviewed") or where it was published
    ("accepted") into answer/results.json, and rung 2 also needs "literature_checked": true. A refuting outside
    record, or a "withdrawn" reason, overrides everything."""
    if row["refuted"] or r.get("withdrawn"):
        return -1
    if r.get("accepted"):
        return 4
    if r.get("reviewed"):
        return 3
    inside = row["inside"].lower().startswith("confirmed")
    outside = row["want"] > 0 and row["have"] >= row["want"]
    if outside and r.get("literature_checked") and (inside or row["kind"] == "pieces"):
        return 2
    return 1 if inside else 0


def tracker(rows):
    """The counter: one number per rung, never a single 'solved' total."""
    counts = [sum(1 for x in rows if x["rung"] == k) for k in range(5)]
    return {"rungs": [{"rung": k, "name": RUNGS[k], "n": counts[k]} for k in range(5)],
            "withdrawn": sum(1 for x in rows if x["rung"] < 0), "total": len(rows)}


def main():
    units = U.load_all()
    if "--credits" in sys.argv:      # the credit sentence per claim, for announcements and acknowledgements
        for row in results(units):
            print(row["claim"].split(". ")[0] + "\n  " + credit_line(row) + "\n")
        return
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
    res = results(units)
    data = {
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "units": {"total": len(units), "done": sum(t["done"] for t in by_type.values()),
                  "by_type": sorted(by_type.values(), key=lambda t: (t["area"], t["type"]))},
        "records": {"total": total_records, "by_day": [{"date": d, "n": n} for d, n in sorted(days.items())]},
        "contributors": board,
        "results": res,
        "tracker": tracker(res),
        "open_by_field": sorted(open_by_field.values(), key=lambda o: (-(o["ask"] + o["answer"]), o["field"])),
        "ledger": {"totals": totals, "by_field": [by_field[f] for f in FIELDS if sum(
            v for k, v in by_field[f].items() if k != "field")], "by_day": [timeline[d] for d in sorted(timeline)]},
        "open_problems": json.load(open(problems_path)) if os.path.exists(problems_path) else [],
    }
    print("// Generated by verify/site_data.py from the records in this repository. Do not edit by hand.")
    print("window.SWARM_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";")


if __name__ == "__main__":
    main()
