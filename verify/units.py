#!/usr/bin/env python3
"""Queue engine. Standard library only.

    python3 verify/units.py seed       write the starting units into ask/queue/ and answer/queue/ (run once, by a maintainer)
    python3 verify/units.py seed-problems   open the units for problems/open.json and ledger/routed-open-problems.md
                                       that have none yet; safe to run again (advance runs it every time)
    python3 verify/units.py advance    open the next units that finished units unlock; prints the new ids
    python3 verify/units.py status     counts per type and state, as Markdown (part of BOARD.md)

A unit is a file <area>/queue/<id>.json, where area is ask or answer. Its "statement" is frozen: every submission carries its sha256, so nobody
works a reworded version. A unit is done when it has "replicas" accepted submissions in <area>/submissions/<id>/,
each from a different handle.

The Ask loop (questions), following LEDGER.md:
    Q-GEN-n          five candidates, from the five fields            -> Q-RES-n-1 .. Q-RES-n-5, and Q-GEN-(n+1)
    Q-RES-n-k        Gates 0-3 on one candidate                       -> Q-ADV-n-k (2 replicas), Q-VER-n-k-1..3
    Q-ADV-n-k        Gate 4, a fresh-context adversary
    Q-VER-n-k-p      open one cited prior and check what the record says it says
    Q-JDG-n-k        Gate 5, the verdict; maintainers only           (opens once ADV and every VER are done)
                     a Validated or Provisional verdict             -> A-ATT-n-k, an attempt at answering it
The Answer loop: answer-attempt, answer-reproduce and answer-piece units. Attempts open automatically for surviving
questions, ranked by verdict and by how many adversary attacks they withstood; the rest are seeded by maintainers.
Open problems (problems/, verify/problems.py):
    Q-GEN-<PROBLEM>-r  five smaller un-asked questions that bear on one well-known open problem; then as Q-GEN-n
    A-OPEN-<UQ id>     a direct attempt at a routed open problem that has a computable part
    A-IMP-<unit>       two people who did not make the claim say whether an answer advances the problem it is linked to
Every unit has a priority (lower = first); contributors are handed the highest-priority open unit.
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import problems as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AREAS = ("ask", "answer")


def area(unit_id):
    """Which of the two work areas a unit lives in: answer/ for A-..., ask/ for everything else."""
    return "answer" if unit_id.startswith("A-") else "ask"


def queue_path(unit_id):
    return os.path.join(ROOT, area(unit_id), "queue", unit_id + ".json")


def subs_dir(unit_id):
    return os.path.join(ROOT, area(unit_id), "submissions", unit_id)


# the maintainer, 2026-11-27: asking is limited to five fields (LEDGER.md, Parameters, DOMAIN SCOPE). From 2026-11-24 until
# then it was open to any field. The depth check applies in every one, and answering effort goes first to what ranks
# highest. There is no rotation of areas here: a round may draw on any of the five, and every unit carries a priority.
GEN_FIELDS = "mathematics, physics, computer science, biology or medicine"
GEN_TITLE = "Ask: five un-asked questions, in " + GEN_FIELDS
GEN_STATEMENT = ("Propose five candidate un-asked questions in " + GEN_FIELDS + ", each passing the Depth "
                 "requirement of LEDGER.md (deep, with a clear test of what would count as an answer, and important "
                 "if answered), none a duplicate of ledger/INDEX.md.")
# Lower number = do it first. Ask units: finish questions that are closest to a verdict before starting new ones.
DEFAULT_PRIORITY = {"ask-judge": 5, "ask-verify": 10, "ask-adversary": 20, "ask-research": 30, "ask-generate": 40,
                    "answer-reproduce": 50, "answer-piece": 60, "answer-attempt": 200, "answer-impact": 8}
LINK_BOOST = 20   # an answer-attempt on a question the researcher linked to an open problem moves up by this much
OPEN_PRIORITY = 300   # direct attempts at routed open problems come after the questions that survived the Ask area
SCORE = {"Resolved": 1.0, "Partial": 0.5, "Unverified": 0.25, "Unresolved": 0.0}


def priority(u):
    return u.get("priority", DEFAULT_PRIORITY.get(u["type"], 500))


def survival(adversary_records):
    """Share of adversary attacks a question withstood, 0..100, or None if no adversary has reported."""
    s = [SCORE.get(a.get("status"), 0) for r in adversary_records for a in r.get("attacks", {}).values()]
    return round(100 * sum(s) / len(s)) if s else None


def load_all():
    units = {}
    for a in AREAS:
        q = os.path.join(ROOT, a, "queue")
        for n in sorted(os.listdir(q)) if os.path.isdir(q) else []:
            if n.endswith(".json"):
                with open(os.path.join(q, n)) as f:
                    u = json.load(f)
                units[u["id"]] = u
    return units


def subs(unit_id):
    d = subs_dir(unit_id)
    out = {}
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            if n.endswith(".json"):
                with open(os.path.join(d, n)) as f:
                    out[n[:-5]] = json.load(f)
    return out


def conclusive(rec):
    """A record that could not reach a conclusion is kept and credited, but does not fill one of the unit's slots."""
    return rec.get("result") != "Unfinished" and rec.get("finding") != "Unreachable" \
        and rec.get("label") != "NO PROGRESS"


def filled(unit_id):
    return sum(1 for r in subs(unit_id).values() if conclusive(r))


def done(u):
    if filled(u["id"]) >= u.get("replicas", 1):
        return True
    # A source two different people could not open is treated as unreachable, so the question is not stuck on it;
    # the judge then lists it among the sources not read and applies LEDGER.md Gate 5, 'What "the complete search
    # record" means': it holds the entry at Provisional only if it is a must-read source or nobody argued it.
    return u["type"] == "ask-verify" and sum(1 for r in subs(u["id"]).values() if r.get("finding") == "Unreachable") >= 2


def links(u):
    """The open problems a unit bears on: its own links, or the problem it attacks directly."""
    if u.get("bears_on"):
        return u["bears_on"]
    if u["type"] == "answer-attempt" and u.get("inputs", {}).get("problem"):
        return [{"problem": u["inputs"]["problem"], "relation": "direct attempt", "how": "This unit attacks the problem itself."}]
    return []


def positive(u):
    """Has this answer unit produced something that could move a linked problem? (A claim, not yet a result.)"""
    recs = list(subs(u["id"]).values())
    if u["type"] == "answer-attempt":
        return any(r.get("label") in ("PARTIAL", "PROMISING") for r in recs)
    if u["type"] == "answer-reproduce":
        return done(u) and not any(r.get("result") == "Refutes" for r in recs)
    return False


def write(u):
    u.setdefault("replicas", 1)
    u["statement_sha256"] = hashlib.sha256(u["statement"].encode("utf-8")).hexdigest()
    path = queue_path(u["id"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(u, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return u["id"]


# ---------- seed ----------

LEDGER_ADV = {
    "UQ-20261029-08": "For a managed-runtime program traced to exact object death times on a single declared clock (bytes "
                      "allocated), does the death hazard of a heap object depend only on its age, or do the identifiable "
                      "curvatures of the death-time (period) and allocation-epoch (cohort) axes differ from zero?",
    "UQ-20261030-04": "Within a single cell, is the number of de-novo somatic mutations carried by each individual "
                      "near-full-length mtDNA molecule distributed as the Poisson expectation computed from that same cell's "
                      "per-base de-novo mutation frequency times the called molecule length, or is it overdispersed - a "
                      "minority of molecules carrying a disproportionate share of the cell's mutations, as a replication "
                      "hierarchy among genome copies would produce?",
    "UQ-20261030-07": "Across human one-to-many transmission clusters of an acute respiratory virus, what is the donor-level "
                      "intraclass correlation of log10 transmission bottleneck size N_b - do the several recipients infected "
                      "by one donor show correlated founding-population sizes, and what fraction of between-event variance "
                      "in bottleneck width sits at the donor level?",
}


def seed():
    ids = []
    # --- Answer loop: independent reproductions of the research workstream's open leads ---
    ids.append(write({
        "id": "A-REP-M37-51", "type": "answer-reproduce", "replicas": 3, "priority": 2,
        "title": "Reproduce: M(3,7) = 51 (a 2007 table prints 48)",
        "statement": "There is no choice of one integer from each of the 51 blocks [7i, 7i+6], i = 0..50, such that no three "
                     "chosen integers form an arithmetic progression. (A valid choice from 50 blocks exists, so this "
                     "statement is equivalent to M(3,7) = 51, where Brown, Landman and Robertson, arXiv:0706.4420, Table 1, "
                     "print 48.)",
        "inputs": {"kind": "M", "param": 7, "target_size": 51,
                   "known_witness": "answer/witness/M_s7_50blocks.txt",
                   "expected_cost": "under 2 CPU-hours with a most-constrained-block-first backtracking search using the "
                                    "mirror symmetry; about 32 CPU-hours for plain backtracking"},
    }))
    ids.append(write({
        "id": "A-REP-W35-76", "type": "answer-reproduce", "replicas": 3, "priority": 3,
        "title": "Reproduce: w*(3;5) <= 76 (the 2007 table prints >= 75)",
        "statement": "Every colouring of 1..76 with 5 colours contains x, x+d, x+2d (d >= 1) whose colours c1, c2, c3 satisfy "
                     "c1 + c3 = 2*c2. (The matching lower bound w*(3;5) >= 76 is classical; only this upper bound is new.)",
        "inputs": {"kind": "W", "param": 5, "target_size": 76,
                   "known_witness": "answer/witness/wstar_r5_n75.txt",
                   "expected_cost": "about 4.3 CPU-hours with a propagating search split into about 100,000 pieces; "
                                    "make your run resumable, since a restart should cost only the pieces in flight"},
    }))
    ids.append(write({
        "id": "A-REP-G39-49", "type": "answer-reproduce", "replicas": 2, "priority": 1,
        "title": "Reproduce: G(3,9) = 49 (the 2007 table prints 48)",
        "statement": "There is no set of 49 integers whose consecutive gaps are all at most 9 and which contains no three "
                     "terms in arithmetic progression. (A 48-element set exists, so this is G(3,9) = 49; three independent "
                     "searches inside this project agree, and this unit asks for confirmation from outside it.)",
        "inputs": {"kind": "G", "param": 9, "target_size": 49,
                   "known_witness": "answer/witness/G_s9_48elements.txt",
                   "expected_cost": "about 1 CPU-hour growing the set outward from its middle; a few CPU-hours for plain "
                                    "backtracking in C"},
    }))
    # The G(3,10) proof, split so a crowd can finish it: about 90 CPU-hours in all with the project's fastest search.
    for a in range(1, 11):
        for b in range(1, 11):
            if a == b:
                continue  # {0, a, 2a} is itself an arithmetic progression
            ids.append(write({
                "id": f"A-PIECE-G310-57-{a}-{b}", "type": "answer-piece", "replicas": 2, "priority": 4,
                "title": f"G(3,10) = 57? Piece: first gaps ({a}, {b})",
                "statement": f"Decide by exhaustive search whether there is a set 0 = x1 < x2 < ... < x57 of 57 integers with "
                             f"every consecutive gap in 1..10, no three elements in arithmetic progression, x2 - x1 = {a} "
                             f"and x3 - x2 = {b}. Report None if there is none, or the set.",
                "inputs": {"kind": "G", "param": 10, "target_size": 57, "piece": {"prefix_gaps": [a, b]},
                           "whole_problem": "If all 90 pieces return None, G(3,10) = 57 (a 56-element set is known: "
                                            "answer/witness/G_s10_56elements.txt). Brown, Landman and Robertson's 2007 table "
                                            "leaves G(3,10) as '?'.",
                           "expected_cost": "about 1 CPU-hour per piece on average with a good search; pieces vary widely"},
            }))
    # --- Ask loop ---
    ids.append(write({
        "id": "V-LR-BOOK-2014", "type": "ask-verify", "replicas": 2,
        "title": "Library unit: does the 2014 Landman-Robertson book already correct the 2007 table?",
        "statement": "In B. M. Landman and A. Robertson, Ramsey Theory on the Integers, 2nd edition, American Mathematical "
                     "Society, 2014: does the book give values or bounds for G(3,s) (s = 6..10), M(3,s) (s = 4..8) or "
                     "w*(3;5), and if so, which, and do any of them differ from Table 1 of arXiv:0706.4420?",
        "inputs": {"why": "The only open objection on this project's corrections to the 2007 table is that nobody could read "
                          "this book from a machine. It needs a person with a library or the book.",
                   "claim_in_record": "The project's results G(3,9) = 49, M(3,7) = 51, M(3,4) = 19, M(3,5) = 31, "
                                      "M(3,6) = 38, G(3,6) = 23 and w*(3;5) = 76 are not already in this book."},
    }))
    ids.append(write({
        "id": "Q-GEN-1", "type": "ask-generate", "replicas": 1,
        "title": GEN_TITLE,
        "statement": GEN_STATEMENT,
        "inputs": {"area": GEN_FIELDS},
    }))
    for uq, q in LEDGER_ADV.items():
        ids.append(write({
            "id": f"Q-ADV-{uq}", "type": "ask-adversary", "replicas": 2,
            "title": f"Attack: a cross-model adversary for ledger entry {uq}",
            "statement": q,
            "inputs": {"ledger_entry": uq, "record": "ledger/unasked-ledger.md",
                       "read_only": "the entry's fields from 'Question (canonical)' through the significance argument. Do "
                                    "NOT read its earlier adversary logs or verification notes before you finish: this "
                                    "unit exists to get an attack that was not anchored on them.",
                       "why": "Provisional after three adversaries from one model family; a second family's attack is "
                              "the cheapest independent check left."},
        }))
    return ids


def gen_problem(p, r):
    return {"id": f"Q-GEN-{p['id'][3:]}-{r}", "type": "ask-generate", "replicas": 1, "priority": 45,
            "title": f"Ask toward an open problem: {p['title']}"[:110],
            "statement": f"Propose five candidate un-asked questions, each smaller than the open problem below and each "
                         f"such that its answer would bear on it. Problem {p['id']}: {p['statement']} Each candidate "
                         f"must pass the Depth requirement of LEDGER.md, must not be a duplicate of ledger/INDEX.md, "
                         f"must not be the problem itself or a known reformulation of it, and must carry a bears_on "
                         f"link to {p['id']} saying how its answer would bear on the problem.",
            "inputs": {"area": p["field"], "problem": p["id"], "problem_source": p["source"]}}


def seed_problems():
    """One 'ask toward it' unit per well-known problem; one direct attempt per routed problem with a computable part."""
    units = load_all()
    ids = []
    for p in P.load(ROOT).values():
        if p["scale"] == "landmark":
            if p.get("status") == "open" and not any(u["type"] == "ask-generate" and u["inputs"].get("problem") == p["id"]
                                                     for u in units.values()):
                ids.append(write(gen_problem(p, 1)))
        elif p["tier"].startswith("A") and not p["picked"] and f"A-OPEN-{p['id'][3:]}" not in units:
            ids.append(write({
                "id": f"A-OPEN-{p['id'][3:]}", "type": "answer-attempt", "replicas": 2, "priority": OPEN_PRIORITY,
                "title": f"Open problem: {p['title']}"[:110], "statement": p["statement"],
                "inputs": {"problem": p["id"], "source_showing_it_is_open": p["source"], "tier": p["tier"],
                           "record": "ledger/routed-open-problems.md",
                           "how": "Work it as PROMPT.md describes. Open the source first and confirm the problem is "
                                  "still open. State exactly what you established and what you did not."}}))
    return ids


# ---------- advance ----------

def advance():
    new = seed_problems()
    units = load_all()

    def add(u):
        if u["id"] not in units:
            units[u["id"]] = u
            new.append(write(u))

    for u in list(units.values()):
        if not done(u):
            continue
        s = subs(u["id"])
        if u["type"] == "ask-generate":
            n = u["id"].split("-", 2)[2]
            rec = next(iter(s.values()))
            target = u["inputs"].get("problem")
            for k, c in enumerate(rec["candidates"], 1):
                add({"id": f"Q-RES-{n}-{k}", "type": "ask-research", "replicas": 1,
                     "title": f"Research: {c['question'][:80]}",
                     "statement": c["question"], "inputs": {"candidate": c, "area": c.get("domain", "")},
                     "distinct_from_units": [u["id"]]})
            if target:   # the next round toward the same problem, while it is still listed as open
                p = P.load(ROOT).get(target)
                if p and p.get("status") == "open":
                    stem, r = n.rsplit("-", 1)
                    add(gen_problem(p, int(r) + 1))
                continue
            add({"id": f"Q-GEN-{int(n) + 1}", "type": "ask-generate", "replicas": 1,
                 "title": GEN_TITLE,
                 "statement": GEN_STATEMENT, "inputs": {"area": GEN_FIELDS}})
        elif u["type"] == "ask-research":
            tail = u["id"][len("Q-RES-"):]
            rec = next(iter(s.values()))
            chain = u.get("distinct_from_units", []) + [u["id"]]
            add({"id": f"Q-ADV-{tail}", "type": "ask-adversary", "replicas": 2,
                 "title": f"Attack: {u['statement'][:80]}", "statement": u["statement"],
                 "inputs": {"research_unit": u["id"]}, "distinct_from_units": chain})
            for p, prior in enumerate(rec["gate2"]["nearest_priors"], 1):
                c = prior["citation"]
                add({"id": f"Q-VER-{tail}-{p}", "type": "ask-verify", "replicas": 1,
                     "title": f"Verify a source: {c['title'][:80]}",
                     "statement": f"Open {c['id']} ({c['first_author']} {c['year']}, \"{c['title']}\") and check whether "
                                  f"it says what research unit {u['id']} says it says.",
                     "inputs": {"citation": c, "claim_in_record": prior.get("difference", ""),
                                "research_unit": u["id"]},
                     "distinct_from_units": [u["id"]]})
    for u in list(units.values()):
        if u["type"] == "ask-research" and done(u):
            tail = u["id"][len("Q-RES-"):]
            deps = [f"Q-ADV-{tail}"] + sorted(k for k in units if k.startswith(f"Q-VER-{tail}-"))
            if all(d in units and done(units[d]) for d in deps):
                add({"id": f"Q-JDG-{tail}", "type": "ask-judge", "replicas": 1,
                     "title": f"Judge: {u['statement'][:80]}", "statement": u["statement"],
                     "inputs": {"records": [u["id"]] + deps}, "maintainers_only": True})
    # A question that survives its verdict gets answering effort, ranked: Validated before Provisional, and within
    # each by how many adversary attacks it withstood.
    for u in list(units.values()):
        if u["type"] == "ask-judge" and done(u):
            tail = u["id"][len("Q-JDG-"):]
            verdict = next(iter(subs(u["id"]).values())).get("status")
            if verdict not in ("Validated", "Provisional"):
                continue
            surv = survival(subs(f"Q-ADV-{tail}").values()) or 0
            # Links to open problems come from the RESEARCH record: the researcher is a different person from the
            # one who proposed the question, so a link that reaches here has been stated by one and kept by another.
            res = next(iter(subs(f"Q-RES-{tail}").values()), {})
            bears = [l for l in res.get("bears_on", []) if l.get("problem") in P.load(ROOT)]
            add({"id": f"A-ATT-{tail}", "type": "answer-attempt", "replicas": 2, **({"bears_on": bears} if bears else {}),
                 "priority": (100 if verdict == "Validated" else 200) + (100 - surv) - (LINK_BOOST if bears else 0),
                 "title": f"Answer: {u['statement'][:80]}", "statement": u["statement"],
                 "inputs": {"question_records": u["inputs"]["records"] + [u["id"]], "verdict": verdict,
                            "survival_percent": surv,
                            # The researcher's recommended solving method travels with the question. It is a
                            # suggestion from someone who read the nearby literature, not an instruction.
                            **({"recommended_method": res["solving_method"]}
                               if isinstance(res.get("solving_method"), dict) else {}),
                            "how": "Work it as PROMPT.md describes. State exactly what you established and what you "
                                   "did not; a claim becomes a result only after others reproduce it. If "
                                   "recommended_method is present it is the researcher's suggestion, to take or "
                                   "leave."}})
    # An answer that could move a linked open problem is flagged on the board, and two people who did not make the
    # claim are asked whether it does.
    for u in list(units.values()):
        if u["type"] in ("answer-attempt", "answer-reproduce") and links(u) and positive(u):
            # Not the people who made the claim, and not the people who proposed or kept the link.
            linkers = [q for q in u["inputs"].get("question_records", [])[:1] if q in units]
            linkers += [g for q in linkers for g in units[q].get("distinct_from_units", [])]
            add({"id": f"A-IMP-{u['id'][2:]}", "type": "answer-impact", "replicas": 2,
                 "title": f"Does this answer advance an open problem? {u['title']}"[:110],
                 "statement": "For each open problem listed in inputs.links: if the claims recorded for unit "
                              f"{u['id']} hold, do they advance that problem? Unit statement: {u['statement']}",
                 "inputs": {"answer_unit": u["id"], "links": links(u),
                            "read": f"{area(u['id'])}/submissions/{u['id']}/ and each problem's source "
                                    "(python3 verify/problems.py lists them)"},
                 "distinct_from_units": [u["id"]] + linkers})
    return new


def status():
    units = load_all()
    rows = {}
    for u in units.values():
        r = rows.setdefault(u["type"], [0, 0, 0])
        n = filled(u["id"])
        r[0] += 1
        r[1] += n >= u.get("replicas", 1)
        r[2] += n
    out = ["| Unit type | Units | Done | Conclusive records |", "|---|---|---|---|"]
    out += [f"| {t} | {a} | {b} | {c} |" for t, (a, b, c) in sorted(rows.items())]
    return "\n".join(out)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "seed":
        print("\n".join(seed()))
    elif cmd == "seed-problems":
        print("\n".join(seed_problems()))
    elif cmd == "advance":
        print("\n".join(advance()))
    elif cmd == "status":
        print(status())
    else:
        sys.exit(__doc__)
