#!/usr/bin/env python3
"""The registry of open problems the swarm works toward. Standard library only.

    python3 verify/problems.py          list every problem id, field and title

Two sources, one registry:
- problems/open.json            well-known open problems, added by maintainers. Ids look like OP-MATH-RH.
- ledger/routed-open-problems.md  questions the ledger found posed in print and still open. They are read from that
                                  file, never copied; a row's id is OP- followed by its ledger id, e.g. OP-UQ-20261015-02.

A question, a unit or an answer points at a problem with a LINK: {"problem": id, "relation": one of RELATIONS,
"how": one or two sentences}. Links and what is done with them: problems/README.md.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Strongest first. The board ranks flags in this order.
RELATIONS = ["would settle", "would bound", "special case", "evidence", "method", "direct attempt"]


def load(root=ROOT):
    out = {}
    path = os.path.join(root, "problems", "open.json")
    parents = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        parents = d.get("routed_parents", {})
        for p in d["problems"]:
            out[p["id"]] = dict(p, scale="landmark")
    fields = {}
    idx = os.path.join(root, "ledger", "INDEX.md")
    if os.path.exists(idx):
        for line in open(idx, encoding="utf-8"):
            m = re.match(r"^\| (UQ-\d{8}-\d+) \| \w+ \| (.*?) \|", line)
            if m:
                fields[m.group(1)] = m.group(2)
    routed = os.path.join(root, "ledger", "routed-open-problems.md")
    if os.path.exists(routed):
        for line in open(routed, encoding="utf-8"):
            if not re.match(r"^\| 20\d\d-\d\d-\d\d \| UQ-", line):
                continue
            c = [x.strip() for x in line.strip().strip("|").split(" | ")]
            if len(c) != 6:
                continue
            pid = "OP-" + c[1]
            out[pid] = {"id": pid, "field": fields.get(c[1], ""), "title": c[2][:90], "statement": c[2],
                        "source": c[3], "tier": c[4], "picked": c[5], "added": c[0], "status": "open",
                        "scale": "routed", "parents": parents.get(pid, [])}
    return out


def check_links(links, errs, where, root=ROOT, must_include=None):
    """Validate a list of links. Returns the problem ids named."""
    if not isinstance(links, list):
        errs.append(f"{where}: must be a list of links, each with problem, relation and how")
        return []
    known = load(root)
    seen = []
    for i, l in enumerate(links):
        w = f"{where}[{i}]"
        if not isinstance(l, dict):
            errs.append(w + ": must be an object")
            continue
        if l.get("problem") not in known:
            errs.append(f"{w}.problem: {l.get('problem')!r} is not a problem id (run python3 verify/problems.py)")
        elif l["problem"] in seen:
            errs.append(f"{w}.problem: {l['problem']} is linked twice")
        seen.append(l.get("problem"))
        if l.get("relation") not in RELATIONS[:-1]:
            errs.append(f"{w}.relation: must be one of {RELATIONS[:-1]}")
        if not isinstance(l.get("how"), str) or len(l["how"].strip()) < 60:
            errs.append(f"{w}.how: say in at least 60 characters how an answer would bear on the problem")
    if must_include and must_include not in seen:
        errs.append(f"{where}: this unit is about {must_include}, so a link to it is required")
    return seen


# How far a reported claim or result has been checked. A news item must carry exactly one of these, so the page
# never has to find its own words for a claim's standing.
NEWS_STATUS = ["Claim, not checked", "Claim, machine-checked, not refereed", "Claim, under expert review",
               "Published result, peer reviewed", "Accepted by the field", "Withdrawn or refuted", "Progress report"]


def load_news(root=ROOT, known=None):
    """problems/news.json as {problem id: [items, newest first]}, plus the date of the last check. Raises ValueError on
    an item that breaks a rule in problems/README.md, 'Latest info', so a bad item stops the build instead of reaching
    the page."""
    path = os.path.join(root, "problems", "news.json")
    if not os.path.exists(path):
        return {}, ""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    known = load(root) if known is None else known
    day = re.compile(r"^20\d\d-\d\d-\d\d$")
    out = {}
    for pid, items in d.get("news", {}).items():
        if pid not in known:
            raise ValueError(f"news.json: {pid} is not a problem id")
        for i, it in enumerate(items):
            w = f"news.json {pid}[{i}]"
            if it.get("status") not in NEWS_STATUS:
                raise ValueError(f"{w}: status must be one of {NEWS_STATUS}")
            for k in ("date", "checked"):
                if not day.match(str(it.get(k, ""))):
                    raise ValueError(f"{w}: {k} must be a date, YYYY-MM-DD")
            if len(str(it.get("headline", "")).strip()) < 10 or len(str(it.get("summary", "")).strip()) < 80:
                raise ValueError(f"{w}: needs a headline and a summary of at least 80 characters")
            src = it.get("sources") or []
            if not src or any(not str(s.get("url", "")).startswith("https://") or not s.get("publisher") or not s.get("title")
                              for s in src):
                raise ValueError(f"{w}: needs at least one source with publisher, title and an https url")
            if it["status"] != "Accepted by the field" and re.search(r"\b(?:is|was|has been|now) (?:solved|proved|proven|settled)\b",
                                                                      it["headline"] + " " + it["summary"], re.I):
                raise ValueError(f"{w}: says the problem is solved or proved, but its status is {it['status']!r}")
        out[pid] = sorted(items, key=lambda it: it["date"], reverse=True)
    return out, str(d.get("checked", ""))


if __name__ == "__main__":
    for p in load().values():
        print(f"{p['id']:22} {p['scale']:9} {p['field'][:28]:28} {p['title']}")
