#!/usr/bin/env python3
"""Run by .github/workflows/verdict.yml on every pull request that touches a submissions folder. Executes NO code from the pull request.

It reads the PR's file list from the API, requires exactly one added file at <area>/submissions/<unit>/<PR author>.json,
downloads that file's bytes as data, places them in this (base) checkout, and runs the base branch's own checker.
Then it comments ACCEPTED / REJECTED / FAULT and merges an ACCEPTED record.
Env: GH_TOKEN, GH_REPO, PR, HEAD_SHA, HEAD_REPO, AUTHOR.

Every verdict comment ends in a hidden marker naming the head commit it judged:
    <!-- verdict {"sha": "<head sha>", "result": "ACCEPTED|REJECTED|FAULT", "tries": n} -->
so a commit that already has an ACCEPTED or REJECTED verdict is never judged twice, and verify/sweep.py can find the
submissions that were never judged (GitHub cancels queued verdict runs in a burst; see verify/README.md).
"""
import base64
import datetime as dt
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOOT = "\n\n<sub>Checked by verify/check.py on the base branch. Only the file is read.</sub>"
BOT = "github-actions[bot]"          # the GITHUB_TOKEN's account; only its markers count
MARK_RE = re.compile(r"<!-- verdict (\{[^<>]*\}) -->")
SUBMISSIONS = ("ask/submissions/", "answer/submissions/")


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"gh {' '.join(args[:3])}: {r.stderr.strip()}")
    return r.stdout


def items(text):
    """Flatten `gh api --paginate` output, which prints one JSON array per page back to back."""
    out, dec, i, text = [], json.JSONDecoder(), 0, text.strip()
    while i < len(text):
        val, i = dec.raw_decode(text, i)
        out.extend(val if isinstance(val, list) else [val])
        while i < len(text) and text[i].isspace():
            i += 1
    return out


def api_list(path):
    return items(gh("api", path, "--paginate"))


def merge(pr, sha):
    return subprocess.run(["gh", "pr", "merge", str(pr), "--squash", "--match-head-commit", sha],
                          capture_output=True, text=True)


def parse_time(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def latest_verdict(comments, sha):
    """The newest bot verdict marker for this head commit, as a dict with id, result, tries and at, or None."""
    found = None
    for c in comments:
        if (c.get("user") or {}).get("login") != BOT:
            continue
        for m in MARK_RE.finditer(c.get("body") or ""):
            try:
                info = json.loads(m.group(1))
            except ValueError:
                continue
            if info.get("sha") == sha and info.get("result") in ("ACCEPTED", "REJECTED", "FAULT"):
                found = {"id": c["id"], "result": info["result"], "tries": int(info.get("tries", 1)),
                         "at": parse_time(c.get("updated_at") or c["created_at"])}
    return found


def pr_comments(repo, pr):
    return api_list(f"repos/{repo}/issues/{pr}/comments?per_page=100")


def judge(repo, pr, sha, head_repo, author, files=None, fault=None):
    """Check one submission at one head commit, comment, and merge if ACCEPTED. Returns the verdict.

    fault: the earlier FAULT marker for this same commit, if this is a retry. A repeated FAULT then edits that
    comment (counting the try) instead of adding another one.
    """
    def say(result, text, tries=1):
        mark = json.dumps({"sha": sha, "result": result, "tries": tries})
        body = f"{text}{FOOT}\n<!-- verdict {mark} -->"
        if result == "FAULT" and fault:
            gh("api", "-X", "PATCH", f"repos/{repo}/issues/comments/{fault['id']}", "-f", f"body={body}")
        else:
            gh("pr", "comment", str(pr), "--body", body)
        return result

    if files is None:
        files = api_list(f"repos/{repo}/pulls/{pr}/files?per_page=100")
    if len(files) != 1 or files[0]["status"] != "added":
        return say("REJECTED", "**REJECTED**\n\n- A submission is one pull request adding exactly one new file. "
                               f"This one changes {len(files)} file(s).")
    path = files[0]["filename"]
    m = re.match(r"^(?:ask|answer)/submissions/([A-Z]+-[A-Za-z0-9-]+)/([A-Za-z0-9-]+)\.json$", path)
    if not m:
        return say("REJECTED", f"**REJECTED**\n\n- `{path}` is not at <area>/submissions/<unit>/<your handle>.json")
    if m.group(2).lower() != author.lower():
        return say("REJECTED", f"**REJECTED**\n\n- The file is named for `{m.group(2)}` but the pull request is from "
                               f"`{author}`. Submit under your own handle.")
    blob = json.loads(gh("api", f"repos/{head_repo}/contents/{path}?ref={sha}"))
    data = base64.b64decode(blob["content"])
    dest = os.path.join(ROOT, path)
    # The sweep judges several pull requests in one checkout, so the file must not outlive its own check
    # (check.py counts the records it finds in the unit's folder). Put back whatever was there before.
    before = open(dest, "rb").read() if os.path.exists(dest) else None
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    merged = False
    try:
        r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "verify", "check.py"), dest, "--online"],
                           capture_output=True, text=True, cwd=ROOT)
        report = r.stdout.strip().splitlines()
        verdict = {0: "ACCEPTED", 1: "REJECTED", 2: "FAULT"}.get(r.returncode, "FAULT")
        reasons = "\n".join(report[1:]) or "- all checks passed"
        if verdict == "ACCEPTED":
            m2 = merge(pr, sha)
            if m2.returncode == 0:
                merged = True   # the base now holds this exact file, so later checks in this run must see it
                return say("ACCEPTED", f"**ACCEPTED**\n\n{reasons}\n\nMerged. Your record now counts toward "
                                       f"`{m.group(1)}`.")
            verdict, reasons = "FAULT", f"- the record passed, but merging failed: {m2.stderr.strip()[:300]}"
        if verdict == "REJECTED":
            return say("REJECTED", f"**REJECTED**\n\n{reasons}\n\nPush a fixed file to this same pull request, or "
                                   "`/release` the unit with a reason.")
        tries = fault["tries"] + 1 if fault else 1
        return say("FAULT", f"**FAULT** (our side, not yours; it is re-checked automatically, try {tries}, and again "
                            f"on your next push)\n\n{reasons}", tries)
    finally:
        if not merged:
            if before is None:
                os.remove(dest)
            else:
                with open(dest, "wb") as f:
                    f.write(before)


def main():
    repo, pr, sha = os.environ["GH_REPO"], os.environ["PR"], os.environ["HEAD_SHA"]
    head_repo, author = os.environ["HEAD_REPO"], os.environ["AUTHOR"]
    prior = latest_verdict(pr_comments(repo, pr), sha)
    if prior and prior["result"] != "FAULT":
        print(f"#{pr} already has a {prior['result']} verdict for {sha[:12]}; nothing to do")
        return
    print(f"#{pr}: {judge(repo, pr, sha, head_repo, author, fault=prior)}")


if __name__ == "__main__":
    main()
