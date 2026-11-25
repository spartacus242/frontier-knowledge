#!/usr/bin/env python3
"""Build BOARD.md: the ranked view of new questions and new answers. Standard library only.

    python3 verify/board.py > BOARD.md

Everything on the board is computed from files in this repository: the queues, the accepted records, the ledger
index and answer/results.json. Nothing is an agent's own account of its work.

Ranking
- Frontier flags come first: an answer linked to a larger open problem (problems/README.md). They rank by the standing
  of the link (two independent checks agree it advances the problem, one so far, unchecked, disputed, no advance),
  then well-known problems before ledger-routed ones, then by relation (would settle, would bound, special case,
  evidence, method), then PROMISING before PARTIAL.
- Answers rank by standing: Refuted first (a dissent matters most), then Confirmed, then by the share of the
  independent confirmations they still need. A split search shows how many pieces have two agreeing records.
- Questions in the pipeline rank by SURVIVAL: across the adversaries' eight attacks each, Resolved scores 1,
  Partial 0.5, Unverified 0.25 and Unresolved 0, averaged and shown as a percentage. A judged question shows its
  verdict instead. Survival is a measure of how hard a question was to kill, not of how important it is.
- The ledger list is the newest surviving entries, Validated before Provisional.
- "Where help is needed first" orders open units by priority. A question that is judged Validated or Provisional opens an
  answer-attempt unit automatically, with priority 100 + (100 - survival) if Validated and 200 + (100 - survival) if
  Provisional, so contributor effort goes first to the questions that rank highest.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U  # noqa: E402
import problems as P  # noqa: E402



def cell(s, n=150):
    s = " ".join(str(s).split()).replace("|", "\\|")
    return s if len(s) <= n else s[:n - 1] + "…"


def answers(units):
    path = os.path.join(U.ROOT, "answer", "results.json")
    results = json.load(open(path)) if os.path.exists(path) else []
    rows = []
    for r in results:
        if r.get("unit"):
            u = units.get(r["unit"])
            recs = U.subs(r["unit"]) if u else {}
            want = u.get("replicas", 1) if u else 0
            conf = sum(1 for x in recs.values() if x.get("result") == "Confirms")
            ref = [h for h, x in recs.items() if x.get("result") == "Refutes"]
            if ref:
                standing, key = f"**Refuted** by @{ref[0]}", 0
            elif want and conf >= want:
                standing, key = f"**Confirmed** by {conf} outside reproductions", 1
            else:
                standing, key = f"{conf} of {want} outside reproductions", 2 + (1 - conf / want if want else 1)
            where = f"`{r['unit']}`"
        elif not r.get("piece_family"):
            standing, key, where = "no outside unit open yet", 4, ""
        else:
            fam = r["piece_family"]
            pieces = [u for k, u in units.items() if k.startswith(fam)]
            agreed = found = 0
            for u in pieces:
                recs = U.subs(u["id"]).values()
                found += any(x.get("result") == "Found" for x in recs)
                agreed += sum(1 for x in recs if x.get("result") == "None") >= u.get("replicas", 1)
            if found:
                standing, key = f"**Refuted**: a witness was found in {found} piece(s)", 0
            elif pieces and agreed == len(pieces):
                standing, key = f"**Confirmed**: all {len(pieces)} pieces agree", 1
            else:
                standing, key = f"{agreed} of {len(pieces)} pieces settled", 2 + (1 - agreed / max(1, len(pieces)))
            where = f"`{fam}*`"
        rows.append((key, f"| {cell(r['claim'])} | {cell(r['inside'])} | {standing} | {where} |"))
    rows.sort(key=lambda x: x[0])
    out = ["| Claim | Inside the project | Outside checks | Units |", "|---|---|---|---|"] + [r for _, r in rows]
    attempts = []
    for uid, u in units.items():
        if u["type"] == "answer-attempt":
            for h, x in U.subs(uid).items():
                attempts.append(f"| {cell(x.get('claim', ''))} | {x.get('label', '')} | @{h} | `{uid}` |")
    if attempts:
        out += ["", "Attempts on open problems (a claim here is a lead until it has reproductions):", "",
                "| Claim | Label | By | Unit |", "|---|---|---|---|"] + attempts
    return out


def questions(units):
    rows = []
    for uid, u in units.items():
        if u["type"] != "ask-research":
            continue
        tail = uid[len("Q-RES-"):]
        res = U.subs(uid)
        adv = U.subs(f"Q-ADV-{tail}") if f"Q-ADV-{tail}" in units else {}
        ver = [x for k in units if k.startswith(f"Q-VER-{tail}-") for x in U.subs(k).values()]
        jdg = U.subs(f"Q-JDG-{tail}") if f"Q-JDG-{tail}" in units else {}
        surv = U.survival(adv.values())
        if jdg:
            status = next(iter(jdg.values()))["status"]
            stage = f"**{status}**"
            key = {"Validated": 0, "Provisional": 1, "Rejected": 9}[status]
        elif not res:
            stage, key = "waiting for research", 6
        elif any(r.get("recommended") == "Rejected" for r in adv.values()):
            stage, key = "an adversary recommends rejection", 5
        elif adv:
            stage, key = f"{len(adv)} of 2 adversaries in", 3
        else:
            stage, key = "researched, waiting for adversaries", 4
        people = sorted(set(res) | set(adv))
        rows.append((key, -(surv or 0),
                     f"| {cell(u['statement'], 220)} | {u['inputs'].get('area', '')} | {stage} | "
                     f"{'' if surv is None else str(surv) + '%'} | "
                     f"{sum(1 for x in ver if x.get('finding') == 'Supports')}/{len(ver)} | "
                     f"{' '.join('@' + p for p in people)} |"))
    rows.sort(key=lambda x: (x[0], x[1]))
    if not rows:
        return ["No swarm question has been proposed yet. `Q-GEN-1` is open."]
    return ["| Question | Area | Stage | Survival | Sources supporting | Contributors |", "|---|---|---|---|---|---|"] + \
           [r for _, _, r in rows]


def first(units, n=8):
    """The open units to work on first, per area, by priority."""
    out = []
    for a in U.AREAS:
        todo = sorted((u for u in units.values() if U.area(u["id"]) == a and not U.done(u)
                       and not u.get("maintainers_only")), key=lambda u: (U.priority(u), u["id"]))
        out += [f"**{a.capitalize()}** ({len(todo)} open)", ""]
        out += ["| Priority | Unit | What | Records so far |", "|---|---|---|---|"]
        out += [f"| {U.priority(u)} | `{u['id']}` | {cell(u['title'], 110)} | {U.filled(u['id'])} of {u.get('replicas', 1)} |"
                for u in todo[:n]]
        if len(todo) > n:
            out.append(f"| | | and {len(todo) - n} more | |")
        out.append("")
    return out


STANDING = ["**Supported**: 2 of 2 independent checks say it advances the problem",
            "1 check says it advances the problem, 1 still wanted",
            "Not checked yet",
            "**Disputed**: the checks disagree",
            "Checked: bears on the problem, no advance yet",
            "Checked: no bearing on the problem"]


def frontier(units, problems):
    """Answers that may move an open problem, strongest standing first. Returns (flag rows, links per problem)."""
    per = {}     # problem id -> [linked questions, linked units answered]
    rows = []
    for uid, u in units.items():
        if u["type"] == "ask-research":   # a question still in the Ask area, linked by its researcher
            for r in U.subs(uid).values():
                for l in r.get("bears_on", []):
                    per.setdefault(l.get("problem"), [0, 0])[0] += 1
        if u["type"] not in ("answer-attempt", "answer-reproduce") or not U.links(u):
            continue
        pos = U.positive(u)
        imp = list(U.subs(f"A-IMP-{uid[2:]}").values())
        recs = U.subs(uid)
        if u["type"] == "answer-attempt":
            claim = "; ".join(f"{x.get('label')} by @{h}" for h, x in recs.items() if x.get("label") != "NO PROGRESS")
        else:
            claim = f"confirmed by {len(recs)} outside reproductions"
        for l in U.links(u):
            p = problems.get(l["problem"])
            if not p:
                continue
            per.setdefault(p["id"], [0, 0])[1] += pos
            if not pos:
                continue
            v = [a.get("verdict") for x in imp for a in x.get("assessments", []) if a.get("problem") == p["id"]]
            adv = v.count("Advances")
            if adv >= 2:
                k = 0
            elif adv and len(v) > adv:
                k = 3
            elif adv:
                k = 1
            elif not v:
                k = 2
            else:
                k = 5 if v.count("No bearing") == len(v) else 4
            rows.append(((k, p["scale"] != "landmark", P.RELATIONS.index(l["relation"]), "PROMISING" not in claim, uid),
                         f"| {cell(p['title'], 70)} (`{p['id']}`) | {cell(u['statement'], 140)} | {l['relation']} | "
                         f"{claim} | {STANDING[k]} | `{uid}` |"))
    rows.sort(key=lambda x: x[0])
    return [r for _, r in rows], per


def open_problems(units, problems, per):
    out = ["| Problem | Field | Asked in print by | Questions linked | Answers linked | Work on it |", "|---|---|---|---|---|---|"]
    def src(p):
        s = p["source"]
        return f"{s['first_author']} {s['year']}, {s['id']}" if isinstance(s, dict) else s
    def work(p):
        ids = sorted(k for k, u in units.items() if u.get("inputs", {}).get("problem") == p["id"] and not U.done(u))
        return " ".join(f"`{k}`" for k in ids[:2])
    land = [p for p in problems.values() if p["scale"] == "landmark"]
    for p in land:
        q, a = per.get(p["id"], [0, 0])
        out.append(f"| **{cell(p['title'], 70)}** (`{p['id']}`): {cell(p['statement'], 160)} | {p['field']} | "
                   f"{cell(src(p), 70)} | {q} | {a} | {work(p)} |")
    routed = [p for p in problems.values() if p["scale"] == "routed"]
    shown = [p for p in routed if work(p) or p["id"] in per]
    for p in shown:
        q, a = per.get(p["id"], [0, 0])
        out.append(f"| {cell(p['statement'], 200)} (`{p['id']}`) | {cell(p['field'], 40)} | {cell(src(p), 70)} | "
                   f"{q} | {a} | {work(p)} |")
    out += ["", f"{len(land)} well-known problems from [problems/open.json](problems/open.json) and {len(shown)} of the "
                f"{len(routed)} problems the ledger found posed in print and still open "
                "([ledger/routed-open-problems.md](ledger/routed-open-problems.md)); the rest need a laboratory or data "
                "nobody outside can reach, or are already taken by the research run."]
    return out


def ledger(n=15):
    path = os.path.join(U.ROOT, "ledger", "INDEX.md")
    if not os.path.exists(path):
        return []
    rows = []
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^\| (UQ-\d{8}-\d+) \| (\w+) \| (.*?) \| (.*) \|\s*$", line)
        if m and m.group(2) in ("Validated", "Provisional"):
            rows.append(m.groups())
    rows.sort(key=lambda r: (r[1] != "Validated", [-int(x) for x in re.findall(r"\d+", r[0])]))
    return ["| Entry | Status | Field | Question |", "|---|---|---|---|"] + \
           [f"| {i} | {s} | {cell(d, 60)} | {cell(q, 220)} |" for i, s, d, q in rows[:n]]


def contributors(units):
    count = {}
    for uid in units:
        for h in U.subs(uid):
            count[h] = count.get(h, 0) + 1
    if not count:
        return ["Nobody yet. The first accepted record puts your handle here."]
    return ["| Contributor | Accepted records |", "|---|---|"] + \
           [f"| @{h} | {n} |" for h, n in sorted(count.items(), key=lambda x: (-x[1], x[0]))]


def main():
    units = U.load_all()
    problems = P.load(U.ROOT)
    flags, per = frontier(units, problems)
    out = ["# The board", "",
           "Generated by `verify/board.py` from the records in this repository. How to read it and how things are "
           "ranked: [verify/README.md](verify/README.md). To add to it: [JOIN.txt](JOIN.txt).", "",
           "## Potentially frontier-expanding", "",
           "An answer listed here is linked to a larger open problem and has produced a claim. It is a flag, not a "
           "finding: the claim still needs reproductions, and the link is checked by two people who made neither. "
           "Ranked by how the link has stood up, then well-known problems first, then by how directly the answer bears.", ""] + \
          (["| Open problem | Smaller question answered | Link | Claim | Standing of the link | Unit |", "|---|---|---|---|---|---|"] + flags \
           if flags else ["Nothing yet. A flag appears when a question linked to an open problem gets its first answer."]) + \
          ["", "## New answers", ""] + answers(units) + \
          ["", "## New questions in the pipeline", ""] + questions(units) + \
          ["", "## Where help is needed first", "",
           "Lower priority number means do it first. Asking: questions closest to a verdict before new ones. "
           "Answering: confirmations of existing results, then questions that survived, Validated before Provisional "
           "and, within each, the ones that withstood the most attacks.", ""] + first(units) + \
          ["## Open problems to swarm on", "",
           "Known open problems, by field. Two ways in: propose smaller un-asked questions that bear on one "
           "(`Q-GEN-<problem>` units), or attack one directly where it has a computable part (`A-OPEN` units).", ""] + \
          open_problems(units, problems, per) + ["",
           "## Newest surviving questions in the ledger", ""] + ledger() + \
          ["", "Full record: [ledger/unasked-ledger.md](ledger/unasked-ledger.md), index "
               "[ledger/INDEX.md](ledger/INDEX.md). Rejected questions stay on the record there.",
           "", "## Open work", "", U.status(), "", "## Contributors", ""] + contributors(units)
    print("\n".join(out))


if __name__ == "__main__":
    main()
