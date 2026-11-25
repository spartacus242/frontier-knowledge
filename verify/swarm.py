#!/usr/bin/env python3
"""Contributor helper. Standard library plus the gh CLI, signed in as you.

    python3 verify/swarm.py next [--area ask|answer] [--type <unit type>]   show the highest-priority open unit you may take
    python3 verify/swarm.py next --unit <id or start of id>   the same, limited to one question's units (the Open
                                                          questions page gives the value for each question)
    python3 verify/swarm.py claim <issue>                 take it (posts /claim; the desk answers on the issue)
    python3 verify/swarm.py beat <issue>                  renew your lease (every 30 minutes)
    python3 verify/swarm.py release <issue> <reason> [note]
    python3 verify/swarm.py template <unit id>            write a skeleton record for that unit
    python3 verify/swarm.py submit <unit id>              check, branch, commit, push and open the PR

Set UPSTREAM if you work against a different upstream than the default below.
"""
import hashlib
import json
import os
import subprocess
import sys

UPSTREAM = os.environ.get("UPSTREAM", "spartacus242/frontier-knowledge")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PRIORITY = {"ask-judge": 5, "ask-verify": 10, "ask-adversary": 20, "ask-research": 30, "ask-generate": 40,
                    "answer-reproduce": 50, "answer-piece": 60, "answer-attempt": 200, "answer-impact": 8}  # same table as verify/units.py


def gh(*args):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stderr.strip())
    return r.stdout


def git(*args):
    subprocess.run(["git", *args], check=True, cwd=ROOT)


def me():
    return gh("api", "user", "--jq", ".login").strip()


def area(uid):
    return "answer" if uid.startswith("A-") else "ask"


def unit(uid):
    with open(os.path.join(ROOT, area(uid), "queue", uid + ".json")) as f:
        return json.load(f)


def next_unit(kind=None, want_area=None, want_unit=None):
    handle = me()
    out = json.loads(gh("issue", "list", "--repo", UPSTREAM, "--label", "open", "--state", "open", "--limit", "500",
                        "--json", "number,title,labels"))
    # Highest-ranked work first: each unit's priority (lower is first), then the oldest issue.
    def key(i):
        try:
            u = unit(i["title"][1:i["title"].index("]")])
            return (u.get("priority", DEFAULT_PRIORITY.get(u["type"], 500)), i["number"])
        except (FileNotFoundError, ValueError):
            return (10 ** 6, i["number"])
    out.sort(key=key)
    for i in out:
        labels = {l["name"] for l in i["labels"]}
        if "maintainers-only" in labels or (kind and f"type:{kind}" not in labels) \
                or (want_area and f"area:{want_area}" not in labels):
            continue
        uid = i["title"][1:i["title"].index("]")]
        if want_unit and not uid.startswith(want_unit):
            continue                  # --unit: one unit by its id, or one question's family of units by their shared start
        try:
            u = unit(uid)
        except FileNotFoundError:
            print(f"(skipping {uid}: not in your clone yet; sync your fork and pull)")
            continue
        subs_dir = lambda d: os.path.join(ROOT, area(d), "submissions", d, handle + ".json")
        if any(os.path.exists(subs_dir(d)) for d in u.get("distinct_from_units", []) + [uid]):
            continue
        print(json.dumps({"issue": i["number"], "unit": u}, indent=2, ensure_ascii=False))
        return
    if want_unit:
        print(f"No open unit matching {want_unit} for you right now: it may be claimed, finished, or one you may not "
              "take. Tell your owner; do not take a different unit unless they say so.")
        return
    print("No open unit for you right now. Wait a few minutes and ask again.")


def template(uid):
    u = unit(uid)
    rec = {"unit": uid, "handle": me(),
           "statement_sha256": hashlib.sha256(u["statement"].encode("utf-8")).hexdigest(),
           "model": "<model id you ran>", "agent": "<agent and version>", "fresh_context": True,
           "started": "<ISO time>", "finished": "<ISO time>"}
    path = os.path.join(ROOT, area(uid), "submissions", uid, rec["handle"] + ".json")
    if os.path.exists(path):
        sys.exit(f"{path} already exists; not overwriting it.")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(rec, f, indent=2)
        f.write("\n")
    print(f"Wrote {os.path.relpath(path, ROOT)}. Add the fields {area(uid)}/units/{u['type']}.md lists for this unit type.")


def submit(uid):
    handle = me()
    path = f"{area(uid)}/submissions/{uid}/{handle}.json"
    r = subprocess.run([sys.executable, "-I", "verify/check.py", path, "--online"], cwd=ROOT)
    if r.returncode == 1:
        sys.exit("The checker rejected the record. Fix it and run submit again.")
    branch = uid
    git("checkout", "-b", branch)
    git("add", path)
    git("commit", "-m", uid)
    git("push", "-u", "origin", branch)
    gh("pr", "create", "--repo", UPSTREAM, "--head", f"{handle}:{branch}", "--title", uid, "--body",
       f"Submission for {uid}. Only the file is read.")
    print("Submitted. The bot comments ACCEPTED, REJECTED or FAULT on the pull request within minutes.")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "next":
        opts = dict(zip(a[1::2], a[2::2]))
        next_unit(opts.get("--type"), opts.get("--area"), opts.get("--unit"))
    elif a[0] in ("claim", "beat") and len(a) == 2:
        gh("issue", "comment", a[1], "--repo", UPSTREAM, "--body", "/" + a[0])
        print("Posted. The desk answers on the issue.")
    elif a[0] == "release" and len(a) >= 3:
        gh("issue", "comment", a[1], "--repo", UPSTREAM, "--body", " ".join(["/release"] + a[2:]))
    elif a[0] == "template" and len(a) == 2:
        template(a[1])
    elif a[0] == "submit" and len(a) == 2:
        submit(a[1])
    else:
        sys.exit(__doc__)
