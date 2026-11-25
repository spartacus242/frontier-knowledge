#!/usr/bin/env python3
"""Run by .github/workflows/verdict.yml on every pull request that touches a submissions folder. Executes NO code from the pull request.

It reads the PR's file list from the API, requires exactly one added file at <area>/submissions/<unit>/<PR author>.json,
downloads that file's bytes as data, places them in this (base) checkout, and runs the base branch's own checker.
Then it comments ACCEPTED / REJECTED / FAULT and merges an ACCEPTED record.
Env: GH_TOKEN, GH_REPO, PR, HEAD_SHA, HEAD_REPO, AUTHOR.
"""
import base64
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FOOT = "\n\n<sub>Checked by verify/check.py on the base branch. Only the file is read.</sub>"


def gh(*args, check=True):
    r = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and r.returncode:
        raise SystemExit(f"gh {' '.join(args[:3])}: {r.stderr.strip()}")
    return r.stdout


def comment(pr, text):
    gh("pr", "comment", pr, "--body", text + FOOT)


def main():
    repo, pr, sha = os.environ["GH_REPO"], os.environ["PR"], os.environ["HEAD_SHA"]
    head_repo, author = os.environ["HEAD_REPO"], os.environ["AUTHOR"]
    files = json.loads(gh("api", f"repos/{repo}/pulls/{pr}/files", "--paginate"))
    if len(files) != 1 or files[0]["status"] != "added":
        return comment(pr, "**REJECTED**\n\n- A submission is one pull request adding exactly one new file. "
                           f"This one changes {len(files)} file(s).")
    path = files[0]["filename"]
    m = re.match(r"^(?:ask|answer)/submissions/([A-Z]+-[A-Za-z0-9-]+)/([A-Za-z0-9-]+)\.json$", path)
    if not m:
        return comment(pr, f"**REJECTED**\n\n- `{path}` is not at <area>/submissions/<unit>/<your handle>.json")
    if m.group(2).lower() != author.lower():
        return comment(pr, f"**REJECTED**\n\n- The file is named for `{m.group(2)}` but the pull request is from "
                           f"`{author}`. Submit under your own handle.")
    blob = json.loads(gh("api", f"repos/{head_repo}/contents/{path}?ref={sha}"))
    data = base64.b64decode(blob["content"])
    dest = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "wb") as f:
        f.write(data)
    r = subprocess.run([sys.executable, "-I", os.path.join(ROOT, "verify", "check.py"), dest, "--online"],
                       capture_output=True, text=True, cwd=ROOT)
    report = r.stdout.strip().splitlines()
    verdict = {0: "ACCEPTED", 1: "REJECTED", 2: "FAULT"}.get(r.returncode, "FAULT")
    reasons = "\n".join(report[1:]) or "- all checks passed"
    if verdict == "ACCEPTED":
        comment(pr, f"**ACCEPTED**\n\n{reasons}\n\nMerging. Your record now counts toward `{m.group(1)}`.")
        gh("pr", "merge", pr, "--squash", "--match-head-commit", sha)
    elif verdict == "REJECTED":
        comment(pr, f"**REJECTED**\n\n{reasons}\n\nPush a fixed file to this same pull request, or `/release` "
                    "the unit with a reason.")
    else:
        comment(pr, f"**FAULT** (our side, not yours; it is re-checked on the next push or by a maintainer)\n\n{reasons}")


if __name__ == "__main__":
    main()
