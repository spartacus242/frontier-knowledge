#!/usr/bin/env python3
"""End-to-end self-test of the checker and the queue engine, on a throwaway copy of the repo. No network, no GitHub.

    python3 verify/selftest.py

Also walks one link to an open problem from question to frontier flag. Walks one candidate through generate -> research -> two adversaries -> three source checks -> judge, and one answer
piece and one reproduction, asserting that each independence and format rule accepts or refuses as it should.
"""
import json, os, sys, shutil, subprocess, tempfile
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = os.path.join(tempfile.mkdtemp(), "repo")
shutil.copytree(SRC, R, ignore=shutil.ignore_patterns(".git", "submissions", "research", "ledger", "docs"))
with open(os.path.join(R, "MAINTAINERS"), "w") as f:
    f.write("selftest-maintainer\n")
FAILS = []
def ar(uid): return "answer" if uid.startswith("A-") else "ask"
def sha(uid): return json.load(open(f"{R}/{ar(uid)}/queue/{uid}.json"))["statement_sha256"]
def put(uid, h, rec, expect="ACCEPTED"):
    base={"unit":uid,"handle":h,"statement_sha256":sha(uid),"model":"test-model","agent":"test-agent","fresh_context":True,"tokens":180000,"tokens_basis":"counted"}
    base.update(rec); os.makedirs(f"{R}/{ar(uid)}/submissions/{uid}",exist_ok=True)
    p=f"{R}/{ar(uid)}/submissions/{uid}/{h}.json"; json.dump(base,open(p,"w"))
    r=subprocess.run([sys.executable,"-I",f"{R}/verify/check.py",p],capture_output=True,text=True)
    got = r.stdout.split()[0]
    print(f"{'ok  ' if got == expect else 'FAIL'} {uid} by {h}: {got} (expected {expect})")
    if got != expect: FAILS.append((uid, h, r.stdout)); print(r.stdout)
    if r.returncode: os.remove(p)
def adv(): print("  advance opened:", " ".join(subprocess.run([sys.executable,"-I",f"{R}/verify/units.py","advance"],capture_output=True,text=True).stdout.split()) or "nothing")
L="x"*40
depth={"object_test":"The answer would be a fact about integers and their colourings","deletion_test":"Still true if every paper vanished, yes indeed.","result":"Pass"}
cands=[{"question":f"Candidate question number {k} about something mathematical and deep?","alternatives":["a","b"],"domain":"Mathematics","motivation":L,"presuppositions":["p"],"depth":depth} for k in range(1,6)]
put("Q-GEN-1","alice",{"candidates":cands[:4]},"REJECTED")   # should reject: 4 candidates
put("Q-GEN-1","alice",{"candidates":cands,"model":"<model id you ran>"},"REJECTED")   # the template's placeholder is not a model
put("Q-GEN-1","alice",{"candidates":cands,"model":"unknown"},"REJECTED")
# --- tokens: every record states what the unit used; 0 only for a unit a person did without a model ---
put("Q-GEN-1","alice",{"candidates":cands,"tokens":"<total tokens this unit used>"},"REJECTED")   # the template's placeholder
put("Q-GEN-1","alice",{"candidates":cands,"tokens":0},"REJECTED")
put("Q-GEN-1","alice",{"candidates":cands,"tokens_basis":"guess"},"REJECTED")
put("Q-GEN-1","alice",{"candidates":cands,"tokens":10**9+1},"REJECTED")                              # more than one unit can state
put("Q-GEN-1","alice",{"candidates":cands,"tokens":10**400},"REJECTED")
# --- five fields: a candidate's domain must start with one of them ---
put("Q-GEN-1","alice",{"candidates":cands[:4]+[dict(cands[4],domain="Economics - auction theory")]},"REJECTED")
put("Q-GEN-1","alice",{"candidates":cands[:4]+[dict(cands[4],domain="Computer science - learning theory")],"tokens":0,"model":"human"}); os.remove(f"{R}/ask/submissions/Q-GEN-1/alice.json")
put("Q-GEN-1","alice",{"candidates":cands}); adv()
# --- open problems: a link must name a real problem, and a unit about a problem needs a link to it ---
link=lambda pid:[{"problem":pid,"relation":"would bound","how":"An answer would bound the density at which the problem's statement can first fail."}]
tc=[dict(c,bears_on=link("OP-MATH-ERDOS-AP")) for c in cands]
put("Q-GEN-MATH-ERDOS-AP-1","alice",{"candidates":cands},"REJECTED")                                  # no link to the problem
put("Q-GEN-MATH-ERDOS-AP-1","alice",{"candidates":[dict(c,bears_on=link("OP-NOT-A-PROBLEM")) for c in cands]},"REJECTED")
put("Q-GEN-MATH-ERDOS-AP-1","alice",{"candidates":tc}); adv()
ok=os.path.exists(f"{R}/ask/queue/Q-GEN-MATH-ERDOS-AP-2.json") and os.path.exists(f"{R}/ask/queue/Q-RES-MATH-ERDOS-AP-1-5.json")
print("ok   a round toward an open problem opened its research units and the next round" if ok else "FAIL targeted round")
if not ok: FAILS.append(("targeted","",""))
cite=lambda i:{"id":"arxiv:0706.4420","first_author":"Brown","year":2007,"title":"Bounds on van der Waerden numbers and some related functions"}
res={"gate0":{"canonical":cands[0]["question"],"presuppositions":["p"],"depth":depth},
 "gate1":{"what_counts_as_an_answer":L},
 "gate2":{"queries":[{"query":f"query number {i}","returned":"nothing relevant here"} for i in range(8)],
   "nearest_priors":[{"citation":cite(i),"unit_of_analysis":"sets","endpoint":"size","comparator":"none","estimand":"est","difference":"differs because"} for i in range(3)],"novelty":"Medium"},
 "gate3":{k:L for k in ["consequence","audience","fecundity","anchoring"]},"recommended":"Proceed"}
put("Q-RES-1-1","bob",res,"REJECTED")      # reject: a record that recommends Proceed needs the recommended solving method
method={"method":"Extend the density-increment argument of the nearest prior to the two-colour case.","needs":"a proof; a small computer search for the base cases","first_result":"A bound for the first open case, which would rule out the linear conjecture.","ai_progress":"partly","ai_progress_note":"the base-case search"}
put("Q-RES-1-1","bob",dict(res,solving_method=dict(method,ai_progress="maybe")),"REJECTED")
put("Q-RES-1-1","bob",dict(res,solving_method=dict(method,ai_progress=["yes"])),"REJECTED")          # refused, and the checker does not crash on it
put("Q-RES-1-1","bob",dict(res,solving_method=dict(method,needs="")),"REJECTED")
method=dict(method,needs="a proof")                                                                  # the guide's own shortest example is enough
put("Q-RES-1-1","bob",dict(res,recommended="Reject",reject_gate="Gate 2: asked before"),"ACCEPTED"); os.remove(f"{R}/ask/submissions/Q-RES-1-1/bob.json")   # a Reject needs no method
res=dict(res,solving_method=method)
put("Q-RES-1-1","alice",res,"REJECTED")    # reject: alice made the generate unit
put("Q-RES-1-1","bob",dict(res,bears_on=link("OP-MATH-ERDOS-AP"))); adv()
atk={n:{"status":"Partial","argument":L} for n in ["triviality","disguise","combinatorial_novelty","presupposition_failure","vagueness","significance_inflation","reason_for_silence","dissolution"]}
a={"restatement":L,"depth":{"completion":"The answer would be a fact about integers","survives_deletion":True,"result":"Pass"},
 "disguise_queries":[{"query":f"disguise query {i}","returned":"x"} for i in range(8)],"attacks":atk,"recommended":"Provisional"}
put("Q-ADV-1-1","bob",a,"REJECTED")  # reject: bob did research
a2=json.loads(json.dumps(a)); a2["attacks"]["disguise"]["status"]="Unresolved"
put("Q-ADV-1-1","carol",a2,"REJECTED")  # reject: unsourced unresolved + must be Rejected
put("Q-ADV-1-1","carol",a); put("Q-ADV-1-1","dave",a); put("Q-ADV-1-1","erin",a,"REJECTED")  # erin: full
v={"opened":True,"access_route":"arxiv.org/abs","quote":"G(3,9) printed as 48 in Table 1","locus":"Table 1","finding":"Supports","note":"checked the table directly"}
for p in (1,2,3): put(f"Q-VER-1-1-{p}","carol",v)
adv()
put("Q-JDG-1-1","carol",{"status":"Provisional","reason":L,"strongest_remaining_objection":L},"REJECTED")
put("Q-JDG-1-1","selftest-maintainer",{"status":"Provisional","reason":L,"strongest_remaining_objection":L})
adv()   # a Provisional verdict must open an answer-attempt unit, ranked by survival
att = json.load(open(f"{R}/answer/queue/A-ATT-1-1.json")) if os.path.exists(f"{R}/answer/queue/A-ATT-1-1.json") else {}
gen2 = json.load(open(f"{R}/ask/queue/Q-GEN-2.json"))
ok = att.get("priority") == 230 and att.get("bears_on") and gen2["inputs"]["area"] == "mathematics, physics, computer science, biology or medicine" \
    and "any field" not in gen2["statement"] + gen2["title"] and att.get("inputs", {}).get("recommended_method", {}).get("ai_progress") == "partly"
print("ok   surviving question opened A-ATT-1-1 at priority 230 (250 less 20 for its link to an open problem) carrying the recommended method; next round is in the five fields" if ok else f"FAIL attempt unit {att.get('priority')}")
if not ok: FAILS.append(("A-ATT", "", str(att)))
put("A-ATT-1-1","erin",{"label":"NO PROGRESS","summary":"x"*60,"claim":"none"}); adv()
if os.path.exists(f"{R}/answer/queue/A-IMP-ATT-1-1.json"): FAILS.append(("impact","","opened on NO PROGRESS")); print("FAIL impact unit opened on NO PROGRESS")
put("A-ATT-1-1","frank",{"label":"PARTIAL","summary":"x"*60,"claim":"a bound for the first case"}); adv()
imp=lambda v:{"assessments":[{"problem":"OP-MATH-ERDOS-AP","verdict":v,"reason":"y"*80}],"read_the_answer_records":True,"opened_the_problem_source":True}
put("A-IMP-ATT-1-1","frank",imp("Advances"),"REJECTED")   # frank made the claim
put("A-IMP-ATT-1-1","bob",imp("Advances"),"REJECTED")     # bob kept the link at the research step
put("A-IMP-ATT-1-1","alice",imp("Advances"),"REJECTED")   # alice proposed the question
put("A-IMP-ATT-1-1","gina",{"assessments":[]},"REJECTED")
put("A-IMP-ATT-1-1","gina",imp("Advances")); put("A-IMP-ATT-1-1","hal",imp("Advances"))
w=open(f"{R}/answer/witness/G_s10_56elements.txt").read()
put("A-PIECE-G310-57-5-1","alice",{"code_sha256":"0"*64,"result":"Found","witness":w,"nodes":5,"cpu_seconds":1},"REJECTED")  # reject: 56 < 57
put("A-PIECE-G310-57-5-1","alice",{"code_sha256":"0"*64,"result":"None","nodes":5,"cpu_seconds":1})
put("A-REP-G39-49","alice",{"method":"x"*60,"independent":True,"code_sha256":"0"*64,"result":"Confirms","cpu_hours":1.2})

put("A-PIECE-G310-57-5-2","alice",{"code_sha256":"0"*64,"result":"Unfinished","nodes":5,"cpu_seconds":1})
put("A-PIECE-G310-57-5-2","bob",{"code_sha256":"0"*64,"result":"None","nodes":5,"cpu_seconds":1})
put("A-PIECE-G310-57-5-2","carol",{"code_sha256":"0"*64,"result":"None","nodes":5,"cpu_seconds":1})   # an Unfinished record does not fill a slot
put("A-PIECE-G310-57-5-2","dave",{"code_sha256":"0"*64,"result":"None","nodes":5,"cpu_seconds":1},"REJECTED")
b = subprocess.run([sys.executable, "-I", f"{R}/verify/board.py"], capture_output=True, text=True)
good = b.returncode == 0 and "Provisional" in b.stdout and "**Supported**: 2 of 2" in b.stdout
print("ok   board builds and shows the frontier flag as supported" if good else "FAIL board")
if not good: FAILS.append(("board", "", b.stderr))
# Typical cost: a median over contributors, each counted once. carol alone filed the three ask-verify records above,
# so the seed figure still stands; made-up rows then check the median, the per-model figure and the wording.
sys.path.insert(0, f"{R}/verify"); import costs as C
seed = C.typical("ask-verify", units={})
solo = C.typical("ask-verify", "TEST-model")
row = lambda h, t, m="m1", e=False: {"handle": h, "model": m, "key": m.lower(), "tokens": t, "estimated": e}
rep = {"ask-verify": [row("a", 1), row("a", 1), row("a", 1), row("b", 100_000), row("c", 120_000, "m2", True)]}
all3 = C.typical("ask-verify", "m1", _reported=rep)       # m1 has two contributors, so the figure is taken over every model
rep["ask-verify"].append(row("d", 300_000))
m1 = C.typical("ask-verify", "M1", _reported=rep)        # now three on m1: a's own median is 1, then 100,000 and 300,000
tab = [r for r in C.table({}) if r["type"] == "ask-verify"][0]
good = (seed["tokens"] == C.SEED["ask-verify"][0] and solo["tokens"] == C.SEED["ask-verify"][0] and solo["n"] == 3 and solo["handles"] == 1
        and all3["tokens"] == 100_000 and all3["handles"] == 3 and "all models" in all3["basis"] and "5 accepted records, 1 estimated" in all3["basis"]
        and m1["tokens"] == 100_000 and m1["handles"] == 3 and "on M1" in m1["basis"]
        and C.cell("x | [free](https://e)") == "x \\| \\[free\\](https://e)" and tab["basis"] == C.SEED_SOURCE
        and C.typical("ask-research")["tokens"] == C.SEED["ask-research"][0] and "## Typical cost of a unit" in b.stdout)
try: C.quote("ask_verify"); good = False
except ValueError: pass
print("ok   typical cost: one contributor's records do not move the figure; three contributors' median replaces the seed" if good else f"FAIL costs {seed} {solo} {all3} {m1}")
if not good: FAILS.append(("costs", "", str((solo, all3, m1))))
# The Open questions page: one row per question, and a row's prompt target selects that question's units only.
q = subprocess.run([sys.executable, "-I", f"{R}/verify/questions_data.py"], capture_output=True, text=True)
rows = json.loads(q.stdout.split("window.QUESTIONS_DATA = ", 1)[1].rstrip().rstrip(";"))["questions"] if q.returncode == 0 else []
uids = [n[:-5] for a in ("ask", "answer") for n in os.listdir(f"{R}/{a}/queue") if n.endswith(".json")]
hit = {u: [r["id"] for r in rows if r["target"] and u.startswith(r["target"])] for u in uids}
g310 = [r for r in rows if r["target"] == "A-PIECE-G310-57-"]
good = bool(rows) and all(len(v) <= 1 for v in hit.values()) and len(g310) == 1 and g310[0]["work"][0]["units"] == 90 \
    and len({r["id"] for r in rows}) == len(rows)
print("ok   open-questions list builds: the 90 G(3,10) pieces are one row, and no unit answers to two rows' prompts" if good else "FAIL questions list")
if not good: FAILS.append(("questions", "", q.stderr[-400:]))
# Latest info: an item that calls a problem solved before the field accepts it must stop the build.
sys.path.insert(0, f"{R}/verify"); import problems as PN
np_ = f"{R}/problems/news.json"; keep = open(np_).read() if os.path.exists(np_) else None
item = {"date": "2026-01-02", "checked": "2026-01-03", "status": "Claim, not checked", "headline": "A proof is claimed by someone",
        "summary": "x" * 90, "sources": [{"publisher": "P", "title": "T", "url": "https://example.org/a"}]}
def news_ok(**ch):
    json.dump({"news": {"OP-MATH-RH": [dict(item, **ch)]}}, open(np_, "w"))
    try: PN.load_news(R); return True
    except ValueError: return False
good = news_ok() and not news_ok(summary="The Riemann hypothesis has been proved. " + "x" * 90) and not news_ok(status="Solved") \
    and not news_ok(sources=[]) and news_ok(status="Accepted by the field", summary="The conjecture has been proved. " + "x" * 90)
if keep is None: os.remove(np_)
else: open(np_, "w").write(keep)
print("ok   latest info: a claim worded as solved, an unknown status or a missing source is refused" if good else "FAIL news rules")
if not good: FAILS.append(("news", "", ""))
print()
print("SELFTEST PASSED" if not FAILS else f"SELFTEST FAILED: {len(FAILS)} unexpected verdicts")
sys.exit(1 if FAILS else 0)
