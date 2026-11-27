#!/usr/bin/env python3
"""Build site/questions-data.js: every open question on the site's "Open questions" page. Standard library only.

    python3 verify/questions_data.py > site/questions-data.js

One row per QUESTION, never one row per unit. The units that work on a question (ninety pieces of one search, the
rounds of one "ask toward it" unit, two adversaries on one candidate) are folded under it as counts, so a search
split into ninety pieces is one row. Four kinds of question, each read from the file that owns it:

  landmark    well-known open problems                     problems/open.json
  literature  posed in print and still open                ledger/routed-open-problems.md
  new         candidate questions that have survived so far  ledger/INDEX.md (Provisional and Validated rows)
  check       a claimed result waiting for outside checks  answer/results.json and its units

plus one row for the standing unit that asks for new questions in the five fields. A problem's row also carries its
"Latest info" items from problems/news.json (see problems/README.md).

"target" is what the page's per-question agent prompt passes to `python3 verify/swarm.py next --unit <target>`:
a unit id, or the shared start of a family of ids. It is set only when it selects units of that question and no
others, and only while one of them is unfinished.
"""
import datetime
import importlib.util
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import problems as P  # noqa: E402
import site_data as S  # noqa: E402
import units as U  # noqa: E402

TYPE_WORK = {
    "ask-generate": ("propose smaller questions toward it", "agent time and web search, about an hour"),
    "ask-research": ("search the literature for it", "agent time and web search, about an hour"),
    "ask-adversary": ("attack the question", "agent time and web search, about an hour"),
    "ask-verify": ("open and check a source", "web search, or a person with the source"),
    "ask-judge": ("judge the record", "agent time"),
    "answer-attempt": ("attempt an answer", "agent time, open-ended: set a budget"),
    "answer-reproduce": ("reproduce the result independently", "CPU only"),
    "answer-piece": ("run one piece of the search", "CPU only, about an hour a piece"),
    "answer-impact": ("check a claimed link to a larger problem", "agent time and web search"),
}
TIER = {"A": "Has a part computable from public sources", "B": "Crisp, but needs data or tools that are hard to get",
        "C": "Needs laboratory work or restricted data"}


def first_sentence(text, limit=190):
    """A row's headline: the first sentence, or a cut at a word boundary."""
    text = " ".join(text.split())
    m = re.match(r"^(.{40,%d}?[?])(?:\s|$)" % limit, text)
    if m:
        return m.group(1)
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",;:([") + " …"


def source_url(sid):
    for prefix, base in (("url:", ""), ("arxiv:", "https://arxiv.org/abs/"), ("doi:", "https://doi.org/")):
        if sid.startswith(prefix):
            return base + sid[len(prefix):]
    return ""


def ledger_questions():
    """Full canonical question per ledger id, when the ledger itself is checked out; the index's cut text otherwise."""
    out = {}
    idx = os.path.join(U.ROOT, "ledger", "INDEX.md")
    if os.path.exists(idx):
        for line in open(idx, encoding="utf-8"):
            m = re.match(r"^\| (UQ-\d{8}-\d+) \| (\w+) \| (.*?) \| (.*) \|\s*$", line)
            if m:
                out[m.group(1)] = {"status": m.group(2), "domain": m.group(3).strip(),
                                   "short": m.group(4).replace("\\|", "|").strip(), "full": ""}
    src = os.path.join(U.ROOT, "ledger", "unasked-ledger.md")
    tool = os.path.join(U.ROOT, "ledger", "tools", "make-index.py")
    if os.path.exists(src) and os.path.exists(tool):
        spec = importlib.util.spec_from_file_location("make_index", tool)
        mi = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mi)
        text = open(src, encoding="utf-8").read()
        for eid, body in re.findall(r"^ID:\s*(UQ-\S+)\n(.*?)(?=\n---\n|\Z)", text, re.S | re.M):
            if eid in out:
                q = mi.field(body, "Question (canonical)")
                q = re.sub(r"^\[[^\]]*\]\s*", "", q)
                q = re.sub(r"^\((?:V\d|R\d|Gate)[^)]*\)\s*", "", q)
                out[eid]["full"] = q
                out[eid]["headline"] = mi.field(body, "Question (headline)")
    return out


def work(us):
    """Fold a question's units into counts per kind of work, and say what is still open."""
    by = {}
    for u in us:
        w = by.setdefault(u["type"], {"type": u["type"], "what": TYPE_WORK.get(u["type"], (u["type"], ""))[0],
                                      "needs": TYPE_WORK.get(u["type"], ("", ""))[1], "units": 0, "done": 0})
        w["units"] += 1
        w["done"] += U.done(u)
        cost = u.get("inputs", {}).get("expected_cost")
        if cost and u["type"] != "answer-piece":
            w["needs"] = "CPU only: " + cost
    return sorted(by.values(), key=lambda w: U.DEFAULT_PRIORITY.get(w["type"], 500))


def target(us, all_units):
    """What `swarm.py next --unit` should be given so that it hands out this question's units and no others."""
    todo = [u for u in us if not U.done(u) and not u.get("maintainers_only")]
    if not todo:
        return ""
    mine = {u["id"] for u in us}
    ids = [u["id"] for u in todo]
    prefix = os.path.commonprefix(ids)
    if len(ids) > 1 and prefix and all(k in mine for k in all_units if k.startswith(prefix)):
        return prefix
    first = min(todo, key=lambda u: (U.priority(u), u["id"]))["id"]
    return first


def main():
    units = U.load_all()
    probs = P.load(U.ROOT)
    led = ledger_questions()
    res = json.load(open(os.path.join(U.ROOT, "answer", "results.json")))
    res_rows = {r["claim"]: r for r in S.results(units)}

    # ---- every unit belongs to exactly one question ----
    owner = {}
    for uid, u in units.items():
        inp = u.get("inputs", {})
        if inp.get("problem") in probs:
            owner[uid] = inp["problem"]
        elif inp.get("ledger_entry") in led:
            owner[uid] = inp["ledger_entry"]
        elif u["type"] == "ask-generate":
            owner[uid] = "ASK-ANY"
    for i, r in enumerate(res):
        for uid in units:
            if uid == r.get("unit") or (r.get("piece_family") and uid.startswith(r["piece_family"])):
                owner[uid] = "RESULT-%d" % i
    for uid in units:
        owner.setdefault(uid, uid)          # a unit nothing else claims is a question of its own
    mine = {}
    for uid, q in owner.items():
        mine.setdefault(q, []).append(units[uid])

    rows = []
    news, news_checked = P.load_news(U.ROOT, probs)     # raises on an item that breaks the rules, which stops the build

    def add(qid, kind, field, title, text, us, family="", **more):
        row = {"id": qid, "kind": kind, "field": field, "title": title, "text": text if text != title else "",
               "work": work(us), "target": target(us, units)}
        ids = {u["id"] for u in us}
        if row["target"] and family and all(k in ids for k in units if k.startswith(family)):
            row["target"] = family
        row["open"] = sum(w["units"] - w["done"] for w in row["work"])
        if news.get(qid):
            row["news"] = news[qid]
        row.update({k: v for k, v in more.items() if v})
        rows.append(row)

    for p in probs.values():
        us = mine.pop(p["id"], [])
        if p.get("status", "open") != "open":
            continue
        if p["scale"] == "landmark":
            src = p["source"]
            add(p["id"], "landmark", S.field_of(p["field"]), p["title"], p["statement"], us, note=p.get("note", ""),
                family="Q-GEN-%s-" % p["id"][3:],     # every round of its "ask toward it" unit, so the prompt outlives round 1
                source="%s (%s), %s" % (src["first_author"], src["year"], src["title"]), source_url=source_url(src["id"]))
        else:
            letter = p["tier"][:1]
            add(p["id"], "literature", S.field_of(p["field"]), first_sentence(p["statement"]), p["statement"], us,
                source=p["source"], badge=TIER.get(letter, ""), tier=p["tier"],
                note=("The founding research run has taken this one: " + p["picked"]) if p["picked"].strip("() ").lower()
                not in ("", "not picked here") else "")

    for eid, e in led.items():
        us = mine.pop(eid, [])
        if e["status"] not in ("Provisional", "Validated"):
            continue
        full = e["full"] or e["short"]
        add(eid, "new", S.field_of(e["domain"]), e.get("headline") or first_sentence(full), full, us,
            badge=e["status"], domain=e["domain"])

    for i, r in enumerate(res):
        us = mine.pop("RESULT-%d" % i, [])
        if not us:
            continue                         # a claim with no check open is on the results tracker, not here
        row = res_rows[r["claim"]]
        lead = min(us, key=lambda u: (U.priority(u), u["id"]))
        add("RESULT-%d" % i, "check", row["field"], r["claim"].split(". ")[0].rstrip("."),
            lead["statement"] if len(us) == 1 else lead["inputs"].get("whole_problem", r["claim"]), us,
            badge=S.RUNGS[row["rung"]] if row["rung"] >= 0 else "Withdrawn", note=r.get("inside", ""))

    us = mine.pop("ASK-ANY", [])
    if us:
        add("ASK-ANY", "ask", "All five fields", "Ask something nobody has asked, in one of the five fields", us[0]["statement"], us)

    ledger_field = {k: S.field_of(v["domain"]) for k, v in led.items()}
    for qid, us in mine.items():             # whatever is left: units that stand alone
        u = us[0]
        f = S.unit_field(u, ledger_field)
        add(qid, "check" if qid.startswith(("A-", "V-")) else "new", f if f in S.FIELDS else "Other fields",
            u["title"], u["statement"], us, note=u.get("inputs", {}).get("why", ""))

    data = {"generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "news_checked": news_checked, "fields": list(S.FIELDS), "questions": rows}
    print("// Generated by verify/questions_data.py from the records in this repository. Do not edit by hand.")
    print("window.QUESTIONS_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";")


if __name__ == "__main__":
    main()
