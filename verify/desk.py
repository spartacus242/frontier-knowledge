#!/usr/bin/env python3
"""The desk: hands out units under leases, using GitHub issues as the shared state. Runs in GitHub Actions only.

Every unit in ask/queue/ or answer/queue/ has one issue titled "[<unit id>] <title>". The issue body ends in a state block that only this
program writes:  <!-- desk {"holders": {"handle": "lease-until ISO time"}} -->
Labels: unit, type:<type>, and exactly one of open / held / done.

    python3 verify/desk.py sync                         create missing issues; set labels from the queues and submissions
    python3 verify/desk.py command <issue> <handle> <comment text>    handle /claim, /beat, /release <reason>
    python3 verify/desk.py expire                       drop leases that were not renewed

Needs the gh CLI with GH_TOKEN and GH_REPO set. Leases: 45 minutes, renewed by /beat, at most 6 hours in all.
One handle holds one unit at a time.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import units as U  # noqa: E402

LEASE = dt.timedelta(minutes=45)
MAX_LEASE = dt.timedelta(hours=6)
STATE_RE = re.compile(r"<!-- desk (\{.*?\}) -->", re.S)
RELEASE_REASONS = {"too_hard", "missing_source", "statement_seems_wrong", "out_of_time", "out_of_budget", "other"}


def gh(*args, input=None):
    r = subprocess.run(["gh", *args], capture_output=True, text=True, input=input)
    if r.returncode:
        raise SystemExit(f"gh {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def now():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0)


def iso(t):
    return t.isoformat().replace("+00:00", "Z")


def parse(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def issues():
    out = json.loads(gh("issue", "list", "--label", "unit", "--state", "all", "--limit", "5000",
                        "--json", "number,title,body,labels,state"))
    by_unit = {}
    for i in out:
        m = re.match(r"^\[([^\]]+)\]", i["title"])
        if m:
            by_unit[m.group(1)] = i
    return by_unit


def state_of(issue):
    m = STATE_RE.search(issue.get("body") or "")
    return json.loads(m.group(1)) if m else {"holders": {}}


def body_for(u, st):
    lines = [f"**{u['type']}** · replicas wanted: {u.get('replicas', 1)} · priority {U.priority(u)} (lower is first)", "", "### Statement (frozen)", "",
             u["statement"], "", f"statement_sha256: `{u['statement_sha256']}`", "",
             f"Unit file: `{U.area(u['id'])}/queue/{u['id']}.json`. How to do this unit: `{U.area(u['id'])}/units/{u['type']}.md`.", "",
             "To take it, comment `/claim`. Renew with `/beat` at least every 30 minutes. If you stop, comment "
             "`/release <reason>`, where reason is one of " + ", ".join(sorted(RELEASE_REASONS)) +
             ". An honest release is useful work: say why.", ""]
    if st["holders"]:
        lines.append("Held by: " + ", ".join(f"@{h} (lease to {t})" for h, t in sorted(st["holders"].items())))
        lines.append("")
    lines.append(f"<!-- desk {json.dumps(st, sort_keys=True)} -->")
    return "\n".join(lines)


def label_for(u, st):
    n = U.filled(u["id"])
    want = u.get("replicas", 1)
    if U.done(u):
        return "done"
    return "held" if n + len(st["holders"]) >= want else "open"


def apply(u, issue, st):
    lab = label_for(u, st)
    body = body_for(u, st)
    if issue is None:
        gh("issue", "create", "--title", f"[{u['id']}] {u['title']}", "--body", body,
           "--label", f"unit,area:{U.area(u['id'])},type:{u['type']},{lab}" + (",maintainers-only" if u.get("maintainers_only") else ""))
        time.sleep(2)  # stay under GitHub's limit on how fast issues may be created
        return
    old = {l["name"] for l in issue["labels"]}
    args = []
    title = f"[{u['id']}] {u['title']}"
    if issue["title"] != title:
        args += ["--title", title]
    if (issue.get("body") or "").strip() != body.strip():
        args += ["--body", body]
    for l in {"open", "held", "done"} - {lab}:
        if l in old:
            args += ["--remove-label", l]
    if lab not in old:
        args += ["--add-label", lab]
    if args:  # touch an issue only when something changed: a sync over a hundred unchanged units makes no calls
        gh("issue", "edit", str(issue["number"]), *args)
    if lab == "done" and issue["state"] == "OPEN":
        gh("issue", "close", str(issue["number"]), "--reason", "completed")


def ensure_labels(units):
    for name in {"unit", "open", "held", "done", "maintainers-only", "area:ask", "area:answer"} | {f"type:{u['type']}" for u in units.values()}:
        gh("label", "create", name, "--force")


def sync():
    units = U.load_all()
    ensure_labels(units)
    iss = issues()
    for uid, u in units.items():
        st = state_of(iss[uid]) if uid in iss else {"holders": {}}
        st["holders"] = {h: t for h, t in st["holders"].items() if h not in U.subs(uid)}
        apply(u, iss.get(uid), st)


def say(number, text):
    gh("issue", "comment", str(number), "--body", text)


def command(number, handle, text):
    iss = issues()
    found = [(uid, i) for uid, i in iss.items() if i["number"] == int(number)]
    if not found:
        return
    uid, issue = found[0]
    units = U.load_all()
    u = units.get(uid)
    if u is None:
        return
    st = state_of(issue)
    words = text.strip().split()
    if not words or not words[0].startswith("/"):
        return
    cmd = words[0]
    t = now()
    if cmd == "/claim":
        if u.get("maintainers_only") and handle not in maintainers():
            return say(number, f"@{handle} this unit is for maintainers only.")
        held = [k for k, i in iss.items() if k != uid and handle in state_of(i)["holders"]]
        if held:
            return say(number, f"@{handle} you already hold {held[0]}. One unit at a time: submit or `/release` it first.")
        if handle in U.subs(uid):
            return say(number, f"@{handle} you already submitted this unit.")
        for dep in u.get("distinct_from_units", []):
            if handle in U.subs(dep):
                return say(number, f"@{handle} this unit checks {dep}, which you submitted. Take a different one.")
        if label_for(u, st) != "open" and handle not in st["holders"]:
            return say(number, f"@{handle} this unit is fully held or done. `python3 verify/swarm.py next` finds another.")
        st["holders"][handle] = iso(t + LEASE)
        st.setdefault("started", {})[handle] = iso(t)
        apply(u, issue, st)
        say(number, f"@{handle} lease granted to {iso(t + LEASE)}. Renew with `/beat` every 30 minutes.")
    elif cmd == "/beat":
        if handle not in st["holders"]:
            return say(number, f"@{handle} you do not hold this unit; `/claim` it first.")
        start = parse(st.get("started", {}).get(handle, iso(t)))
        until = min(t + LEASE, start + MAX_LEASE)
        st["holders"][handle] = iso(until)
        apply(u, issue, st)
    elif cmd == "/release":
        reason = words[1] if len(words) > 1 else "other"
        if reason not in RELEASE_REASONS:
            reason = "other"
        st["holders"].pop(handle, None)
        st.get("started", {}).pop(handle, None)
        st.setdefault("releases", []).append({"handle": handle, "reason": reason, "at": iso(t),
                                              "note": " ".join(words[2:])[:300]})
        apply(u, issue, st)
        say(number, f"Released by @{handle}: {reason}. Thank you; this is recorded for the next person.")


def expire():
    units = U.load_all()
    t = now()
    for uid, issue in issues().items():
        st = state_of(issue)
        live = {h: v for h, v in st["holders"].items() if parse(v) > t}
        if live != st["holders"] and uid in units:
            st["holders"] = live
            apply(units[uid], issue, st)


def maintainers():
    path = os.path.join(U.ROOT, "MAINTAINERS")
    return {l.strip().lstrip("@") for l in open(path) if l.strip() and not l.startswith("#")} if os.path.exists(path) else set()


if __name__ == "__main__":
    c = sys.argv[1] if len(sys.argv) > 1 else ""
    if c == "sync":
        sync()
    elif c == "command" and len(sys.argv) >= 5:
        command(sys.argv[2], sys.argv[3], " ".join(sys.argv[4:]))
    elif c == "expire":
        expire()
    else:
        sys.exit(__doc__)
