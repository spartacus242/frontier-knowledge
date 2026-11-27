#!/usr/bin/env python3
"""The submission checker. Standard library only. The same program runs on your machine and in CI.

    python3 verify/check.py <area>/submissions/<unit>/<handle>.json            offline checks
    python3 verify/check.py <area>/submissions/<unit>/<handle>.json --online   also resolve every DOI and arXiv id

Prints one verdict line, ACCEPTED, REJECTED or FAULT, followed by the reasons.
FAULT means the checker could not finish (a citation service was unreachable); it is not your fault and is re-run later.
Exit code: 0 ACCEPTED, 1 REJECTED, 2 FAULT.

A check here is necessary, not sufficient. ACCEPTED means the record is well formed, honest about its sources and
independent of the records it must be independent of. Whether the question is new, or the claim is true, is decided
by agreement between independent records and, at the top tier, by a maintainer. See verify/README.md.
<area> is ask or answer: units whose id starts with A- live in answer/, all others in ask/.
"""
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import problems as P  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_BYTES = 512 * 1024
HANDLE_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
UNIT_RE = re.compile(r"^[A-Z]+-[A-Za-z0-9-]+$")
ATTACKS = ["triviality", "disguise", "combinatorial_novelty", "presupposition_failure",
           "vagueness", "significance_inflation", "reason_for_silence", "dissolution"]
ATTACK_STATUS = {"Resolved", "Partial", "Unresolved", "Unverified"}
NOVELTY = {"High", "Medium", "Low", "Unverified"}
PLACEHOLDERS = {"unknown", "n/a", "none", "tbd", "todo", "model", "agent", "model id", "model id you ran",
                "agent and version", "...", "xxx"}
CITE_PREFIXES = ("doi:", "arxiv:", "isbn:", "url:")


class Fault(Exception):
    pass


def statement_sha256(unit):
    return hashlib.sha256(unit["statement"].encode("utf-8")).hexdigest()


def area(unit_id):
    return "answer" if unit_id.startswith("A-") else "ask"


def load_unit(root, unit_id):
    path = os.path.join(root, area(unit_id), "queue", unit_id + ".json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def submitters(root, unit_id):
    d = os.path.join(root, area(unit_id), "submissions", unit_id)
    if not os.path.isdir(d):
        return set()
    return {n[:-5] for n in os.listdir(d) if n.endswith(".json")}


def maintainers(root):
    path = os.path.join(root, "MAINTAINERS")
    if not os.path.exists(path):
        return set()
    return {l.strip().lstrip("@") for l in open(path) if l.strip() and not l.startswith("#")}


# ---------- small field helpers ----------

def need_str(rec, key, errs, min_len=1, where=""):
    v = rec.get(key)
    if not isinstance(v, str) or len(v.strip()) < min_len:
        errs.append(f"{where}{key}: a text of at least {min_len} characters is required")
        return ""
    return v


def need_list(rec, key, errs, min_n=1, where=""):
    v = rec.get(key)
    if not isinstance(v, list) or len(v) < min_n:
        errs.append(f"{where}{key}: a list of at least {min_n} items is required")
        return []
    return v


def need_enum(rec, key, allowed, errs, where=""):
    v = rec.get(key)
    if v not in allowed:
        errs.append(f"{where}{key}: must be one of {sorted(allowed)}")
    return v


def check_citation(c, errs, where):
    if not isinstance(c, dict):
        errs.append(f"{where}: a citation must be an object with id, first_author, year, title")
        return
    cid = c.get("id", "")
    if not isinstance(cid, str) or not cid.startswith(CITE_PREFIXES):
        errs.append(f"{where}.id: must start with one of {CITE_PREFIXES} (a bare PMCID or a guess is not an id)")
    for k in ("first_author", "title"):
        if not isinstance(c.get(k), str) or not c.get(k).strip():
            errs.append(f"{where}.{k}: required")
    if not isinstance(c.get("year"), int):
        errs.append(f"{where}.year: an integer year is required")


def collect_citations(obj, out):
    if isinstance(obj, dict):
        if "id" in obj and "title" in obj and isinstance(obj.get("id"), str) and obj["id"].startswith(CITE_PREFIXES):
            out.append(obj)
        for v in obj.values():
            collect_citations(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_citations(v, out)


def check_depth(d, errs, where="depth"):
    if not isinstance(d, dict):
        errs.append(f"{where}: an object with object_test and deletion_test is required")
        return None
    obj = need_str(d, "object_test", errs, 20, where + ".")
    if obj and not obj.strip().lower().startswith("the answer would be a fact about"):
        errs.append(f'{where}.object_test: must complete the sentence "The answer would be a fact about ___"')
    need_str(d, "deletion_test", errs, 20, where + ".")
    return need_enum(d, "result", {"Pass", "Fail"}, errs, where + ".")


# ---------- per-type checks ----------

def t_ask_generate(rec, unit, errs, root):
    cands = need_list(rec, "candidates", errs, 5)
    if len(cands) != 5:
        errs.append("candidates: exactly 5 are required")
    for i, c in enumerate(cands):
        w = f"candidates[{i}]."
        if not isinstance(c, dict):
            errs.append(w + " must be an object")
            continue
        need_str(c, "question", errs, 30, w)
        alts = need_list(c, "alternatives", errs, 2, w)
        need_str(c, "domain", errs, 3, w)
        need_str(c, "motivation", errs, 30, w)
        need_list(c, "presuppositions", errs, 1, w)
        if check_depth(c.get("depth"), errs, w + "depth") == "Fail":
            errs.append(w + "depth: a candidate that fails the depth gate must be replaced, not submitted")
        if alts and len(alts) < 2:
            errs.append(w + "alternatives: two phrasings are required")
        target = unit.get("inputs", {}).get("problem")
        if target or "bears_on" in c:
            P.check_links(c.get("bears_on", []), errs, w + "bears_on", root, must_include=target)


def t_ask_research(rec, unit, errs, root):
    g0 = rec.get("gate0") or {}
    need_str(g0, "canonical", errs, 30, "gate0.")
    if g0.get("canonical") and g0["canonical"].strip() != unit["inputs"]["candidate"]["question"].strip():
        errs.append("gate0.canonical: must be the unit's candidate question, unchanged (reformulate at Gate 1, not here)")
    need_list(g0, "presuppositions", errs, 1, "gate0.")
    depth = check_depth(g0.get("depth"), errs, "gate0.depth")
    g1 = rec.get("gate1") or {}
    need_str(g1, "what_counts_as_an_answer", errs, 40, "gate1.")
    g2 = rec.get("gate2") or {}
    qs = need_list(g2, "queries", errs, 8, "gate2.")
    seen = set()
    for i, q in enumerate(qs):
        if not isinstance(q, dict):
            errs.append(f"gate2.queries[{i}]: must be an object with query and returned")
            continue
        need_str(q, "query", errs, 3, f"gate2.queries[{i}].")
        need_str(q, "returned", errs, 10, f"gate2.queries[{i}].")
        seen.add(" ".join(str(q.get("query", "")).lower().split()))
    if len(seen) < 8:
        errs.append(f"gate2.queries: at least 8 DISTINCT queries are required, found {len(seen)}")
    priors = need_list(g2, "nearest_priors", errs, 3, "gate2.")
    for i, p in enumerate(priors):
        w = f"gate2.nearest_priors[{i}]"
        if not isinstance(p, dict):
            errs.append(w + ": must be an object")
            continue
        check_citation(p.get("citation"), errs, w + ".citation")
        for k in ("unit_of_analysis", "endpoint", "comparator", "estimand", "difference"):
            need_str(p, k, errs, 3, w + ".")
    need_enum(g2, "novelty", NOVELTY, errs, "gate2.")
    g3 = rec.get("gate3") or {}
    for k in ("consequence", "audience", "fecundity", "anchoring"):
        need_str(g3, k, errs, 30, "gate3.")
    if "bears_on" in rec:
        P.check_links(rec["bears_on"], errs, "bears_on", root)
    rec_v = need_enum(rec, "recommended", {"Proceed", "Reject"}, errs)
    if depth == "Fail" and rec_v == "Proceed":
        errs.append("recommended: a depth Fail cannot proceed")


def t_ask_adversary(rec, unit, errs, root):
    need_str(rec, "restatement", errs, 30)
    d = rec.get("depth") or {}
    comp = need_str(d, "completion", errs, 20, "depth.")
    if comp and not comp.lower().startswith("the answer would be a fact about"):
        errs.append('depth.completion: must complete "The answer would be a fact about ___"')
    if not isinstance(d.get("survives_deletion"), bool):
        errs.append("depth.survives_deletion: true or false is required")
    need_enum(d, "result", {"Pass", "Fail"}, errs, "depth.")
    dq = need_list(rec, "disguise_queries", errs, 8)
    if len({" ".join(str(q.get("query", "")).lower().split()) for q in dq if isinstance(q, dict)}) < 8:
        errs.append("disguise_queries: at least 8 distinct queries, in vocabularies the research record did not use")
    atk = rec.get("attacks")
    if not isinstance(atk, dict) or set(atk) != set(ATTACKS):
        errs.append(f"attacks: an object with exactly these keys is required: {ATTACKS}")
        atk = {}
    for name, a in atk.items():
        w = f"attacks.{name}."
        if not isinstance(a, dict):
            errs.append(w[:-1] + ": must be an object")
            continue
        st = need_enum(a, "status", ATTACK_STATUS, errs, w)
        need_str(a, "argument", errs, 30, w)
        ev = a.get("evidence", [])
        if st == "Unresolved":
            sourced = [e for e in ev if isinstance(e, dict) and e.get("quote") and e.get("citation")]
            if not sourced and not a.get("own_reasoning"):
                errs.append(w + "evidence: an Unresolved attack needs a source you opened, with a quoted line, "
                                "or own_reasoning: true saying the step is your own argument (LEDGER.md: a kill "
                                "that cannot be sourced is Partial at best)")
        for j, e in enumerate(ev):
            if isinstance(e, dict) and "citation" in e:
                check_citation(e["citation"], errs, f"{w}evidence[{j}].citation")
    v = need_enum(rec, "recommended", {"Rejected", "Provisional", "Validated-eligible"}, errs)
    fatal = [n for n in ("triviality", "disguise", "presupposition_failure")
             if isinstance(atk.get(n), dict) and atk[n].get("status") == "Unresolved"]
    if fatal and v != "Rejected":
        errs.append(f"recommended: Unresolved on {fatal} means Rejected (LEDGER.md Gate 4)")
    if d.get("result") == "Fail" and v != "Rejected":
        errs.append("recommended: a depth Fail means Rejected at Gate 0")


def t_ask_verify(rec, unit, errs, root):
    if not isinstance(rec.get("opened"), bool):
        errs.append("opened: true or false is required")
    f = need_enum(rec, "finding", {"Supports", "Partly", "Contradicts", "Unreachable"}, errs)
    if rec.get("opened"):
        need_str(rec, "access_route", errs, 5)
        need_str(rec, "quote", errs, 20)
        need_str(rec, "locus", errs, 2)
    elif f != "Unreachable":
        errs.append("finding: a source you did not open can only be Unreachable")
    need_str(rec, "note", errs, 20)


def check_witness(kind, param, text, errs, min_len=None, prefix_gaps=None):
    sys.path.insert(0, os.path.join(ROOT, "verify"))
    import witness
    ok, info = witness.check(kind, param, text)
    if not ok:
        errs.append(f"witness: {info}")
        return
    if min_len is not None and info < min_len:
        errs.append(f"witness: has {info} elements, {min_len} required")
    if prefix_gaps:
        xs = sorted(int(t) for t in text.split())
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        if gaps[:len(prefix_gaps)] != prefix_gaps:
            errs.append(f"witness: does not start with this piece's gaps {prefix_gaps}")


def t_answer_reproduce(rec, unit, errs, root):
    need_str(rec, "method", errs, 60)
    if rec.get("independent") is not True:
        errs.append("independent: must be true; reproduce with a program you wrote or chose, not the claim's own code")
    need_str(rec, "code_sha256", errs, 64)
    r = need_enum(rec, "result", {"Confirms", "Refutes", "Unfinished"}, errs)
    if not isinstance(rec.get("cpu_hours"), (int, float)):
        errs.append("cpu_hours: a number is required")
    if r == "Refutes":
        inp = unit["inputs"]
        if not rec.get("witness"):
            errs.append("witness: a refutation of a 'no such object' claim must include the object")
        else:
            check_witness(inp["kind"], inp["param"], rec["witness"], errs, min_len=inp["target_size"])
    if r == "Unfinished":
        need_str(rec, "resume_note", errs, 20)


def t_answer_piece(rec, unit, errs, root):
    need_str(rec, "code_sha256", errs, 64)
    r = need_enum(rec, "result", {"None", "Found", "Unfinished"}, errs)
    if not isinstance(rec.get("nodes"), int):
        errs.append("nodes: the integer count of search nodes visited is required")
    if not isinstance(rec.get("cpu_seconds"), (int, float)):
        errs.append("cpu_seconds: a number is required")
    inp = unit["inputs"]
    if r == "Found":
        check_witness(inp["kind"], inp["param"], rec.get("witness", ""), errs,
                      min_len=inp["target_size"], prefix_gaps=inp["piece"].get("prefix_gaps"))


def t_answer_attempt(rec, unit, errs, root):
    need_enum(rec, "label", {"NO PROGRESS", "PARTIAL", "PROMISING"}, errs)
    need_str(rec, "summary", errs, 60)
    need_str(rec, "claim", errs, 4)
    w = rec.get("witness")
    if w:
        inp = unit["inputs"]
        if "kind" in inp:
            check_witness(inp["kind"], inp["param"], w, errs)


def t_answer_impact(rec, unit, errs, root):
    want = [l["problem"] for l in unit["inputs"]["links"]]
    a = need_list(rec, "assessments", errs, len(want))
    got = []
    for i, x in enumerate(a):
        w = f"assessments[{i}]."
        if not isinstance(x, dict):
            errs.append(w[:-1] + ": must be an object")
            continue
        got.append(x.get("problem"))
        need_enum(x, "verdict", {"Advances", "Bears on it, no advance", "No bearing"}, errs, w)
        need_str(x, "reason", errs, 80, w)
    if sorted(map(str, got)) != sorted(want):
        errs.append(f"assessments: exactly one for each linked problem is required: {want}")
    if rec.get("read_the_answer_records") is not True or rec.get("opened_the_problem_source") is not True:
        errs.append("read_the_answer_records and opened_the_problem_source: both must be true; if you could not open "
                    "the problem's source, release the unit")


def t_ask_judge(rec, unit, errs, root):
    if rec.get("handle") not in maintainers(root):
        errs.append("handle: judge units are taken by maintainers only (see MAINTAINERS)")
    need_enum(rec, "status", {"Validated", "Provisional", "Rejected"}, errs)
    need_str(rec, "reason", errs, 40)
    need_str(rec, "strongest_remaining_objection", errs, 20)


TYPES = {
    "ask-generate": t_ask_generate, "ask-research": t_ask_research, "ask-adversary": t_ask_adversary,
    "ask-verify": t_ask_verify, "ask-judge": t_ask_judge,
    "answer-attempt": t_answer_attempt, "answer-reproduce": t_answer_reproduce, "answer-piece": t_answer_piece,
    "answer-impact": t_answer_impact,
}


# ---------- online citation check ----------

def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "unasked-questions-checker/1"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise Fault(f"{url}: HTTP {e.code}")
    except Exception as e:  # network trouble is a FAULT, not your fault
        raise Fault(f"{url}: {e}")


def _words(s):
    return {w for w in re.findall(r"[a-z0-9]+", s.lower()) if len(w) > 2}


def _same_title(a, b):
    A, B = _words(a), _words(b)
    return bool(A and B) and len(A & B) / len(A | B) >= 0.6


def resolve(c, errs):
    cid = c["id"]
    if cid.startswith("doi:"):
        doi = cid[4:]
        body = _get("https://api.crossref.org/works/" + urllib.parse.quote(doi))
        if body is None:
            body = _get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi))
            if body is None:
                errs.append(f"citation {cid}: this DOI does not resolve in Crossref or OpenAlex")
                return
            m = json.loads(body)
            title = m.get("title") or ""
            auths = [a["author"]["display_name"] for a in m.get("authorships", [])]
        else:
            m = json.loads(body)["message"]
            title = (m.get("title") or [""])[0]
            auths = [a.get("family", "") for a in m.get("author", [])]
        if not _same_title(title, c["title"]):
            errs.append(f'citation {cid}: the record says "{c["title"]}" but the DOI is "{title}"')
        if auths and not any(c["first_author"].lower() in a.lower() or a.lower() in c["first_author"].lower()
                             for a in auths[:1]):
            errs.append(f"citation {cid}: first author is {auths[0]}, the record says {c['first_author']}")
    elif cid.startswith("arxiv:"):
        body = _get("https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(cid[6:]))
        titles = re.findall(r"<entry>.*?<title>(.*?)</title>", body or "", re.S)
        if not titles:
            errs.append(f"citation {cid}: no such arXiv id")
        elif not _same_title(" ".join(titles[0].split()), c["title"]):
            errs.append(f'citation {cid}: the record says "{c["title"]}" but arXiv has "{" ".join(titles[0].split())}"')


# ---------- main ----------

def check_file(path, root=ROOT, online=False):
    errs = []
    rel = os.path.relpath(os.path.abspath(path), root).replace(os.sep, "/")
    m = re.match(r"^(ask|answer)/submissions/([^/]+)/([^/]+)\.json$", rel)
    if not m or m.group(1) != area(m.group(2)):
        return "REJECTED", ["path: a submission is exactly one file at <area>/submissions/<unit>/<handle>.json, "
                            "in answer/ for A-... units and in ask/ for all others"]
    _, unit_id, handle = m.groups()
    if not UNIT_RE.match(unit_id) or not HANDLE_RE.match(handle):
        return "REJECTED", ["path: unit id or handle has characters that are not allowed"]
    if os.path.getsize(path) > MAX_BYTES:
        return "REJECTED", [f"size: a record is at most {MAX_BYTES} bytes"]
    try:
        rec = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        return "REJECTED", [f"json: {e}"]
    if not isinstance(rec, dict):
        return "REJECTED", ["json: the record must be an object"]
    unit = load_unit(root, unit_id)
    if unit is None:
        return "REJECTED", [f"unit: there is no {area(unit_id)}/queue/{unit_id}.json"]
    if rec.get("unit") != unit_id:
        errs.append("unit: must equal the unit id in the path")
    if rec.get("handle") != handle:
        errs.append("handle: must equal your GitHub handle, which is the file name")
    if rec.get("statement_sha256") != statement_sha256(unit):
        errs.append("statement_sha256: does not match the unit's statement; you must work the statement exactly as posted")
    for k, what in (("model", "the model id you ran, e.g. claude-opus-5-5 or gpt-5.1; for a unit a person did "
                                  "without a model, write human"),
                    ("agent", "the agent or tool you ran it in, with its version")):
        v = need_str(rec, k, errs, 3)
        if v and (re.search(r"[<>]", v) or v.strip().lower() in PLACEHOLDERS):
            errs.append(f"{k}: replace the template's placeholder with {what}")
    if rec.get("fresh_context") is not True:
        errs.append("fresh_context: must be true; start the unit in a new session that has not seen other records "
                    "for this question except those the unit lists as inputs")
    # independence
    others = 0
    for h in submitters(root, unit_id) - {handle}:
        try:
            with open(os.path.join(root, area(unit_id), "submissions", unit_id, h + ".json")) as f:
                o = json.load(f)
        except Exception:
            o = {}
        others += (o.get("result") != "Unfinished" and o.get("finding") != "Unreachable"
                   and o.get("label") != "NO PROGRESS")
    if others >= unit.get("replicas", 1):
        errs.append(f"unit: already has the {unit.get('replicas', 1)} conclusive records it wants")
    for dep in unit.get("distinct_from_units", []):
        if handle in submitters(root, dep):
            errs.append(f"independence: you submitted {dep}, which this unit checks, so another contributor must take it")
    if handle in unit.get("distinct_from_handles", []):
        errs.append("independence: this unit checks your own work, so another contributor must take it")
    fn = TYPES.get(unit["type"])
    if fn is None:
        return "REJECTED", [f"unit: unknown type {unit['type']}"]
    fn(rec, unit, errs, root)
    cites = []
    collect_citations(rec, cites)
    for i, c in enumerate(cites):
        check_citation(c, errs, f"citation[{i}]")
    if online and not errs:
        try:
            for c in cites:
                resolve(c, errs)
        except Fault as f:
            return "FAULT", [str(f)]
    return ("REJECTED", errs) if errs else ("ACCEPTED", [])


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    online = "--online" in argv
    files = [a for a in argv if not a.startswith("--")]
    worst = 0
    for f in files:
        verdict, reasons = check_file(f, online=online)
        print(f"{verdict} {f}")
        for r in reasons:
            print("  - " + r)
        worst = max(worst, {"ACCEPTED": 0, "REJECTED": 1, "FAULT": 2}[verdict])
    sys.exit(worst)


if __name__ == "__main__":
    main(sys.argv[1:])
