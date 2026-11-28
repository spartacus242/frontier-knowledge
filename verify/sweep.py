#!/usr/bin/env python3
"""Judge every open submission that has no verdict yet. Run by .github/workflows/sweep.yml every 15 minutes.

Why: verdict.yml runs one check at a time in the concurrency group "verdict", and GitHub keeps only ONE pending run
per group. In a burst of submissions every earlier pending run is cancelled, and those pull requests would sit
without a verdict until their author pushed again. The sweep runs in the same group (so it never races a verdict
run on replica counts) and catches them up.

For each open pull request into the default branch that touches a submissions folder, it reads the verdict markers
that verify/ci_verdict.py leaves in its comments (only the bot's count), and judges the current head commit when
  - it has no verdict at all, or
  - its verdict is FAULT, at least RETRY_AFTER old, and has been tried fewer than MAX_TRIES times
    (a repeated FAULT edits the same comment, so a citation service that stays down does not flood the thread).
Like verdict.yml it executes NO code from the pull request: it reuses ci_verdict.judge, which reads the one file as data.
At most MAX_CHECKS judgments per run, oldest pull request first; the rest wait for the next run.
Env: GH_TOKEN, GH_REPO.
"""
import datetime as dt
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ci_verdict as V  # noqa: E402

MAX_CHECKS = 8
MAX_TRIES = 3
RETRY_AFTER = dt.timedelta(minutes=30)


def touches_submissions(files):
    return any(f["filename"].startswith(V.SUBMISSIONS) or (f.get("previous_filename") or "").startswith(V.SUBMISSIONS)
               for f in files)


def due(prior, now):
    """Whether a head commit with this latest verdict marker (or None) should be judged now, and why."""
    if prior is None:
        return True, "no verdict"
    if prior["result"] != "FAULT":
        return False, prior["result"]
    if prior["tries"] >= MAX_TRIES:
        return False, f"FAULT after {prior['tries']} tries; left for a maintainer or the next push"
    if now - prior["at"] < RETRY_AFTER:
        return False, "FAULT, retried later"
    return True, f"FAULT retry {prior['tries'] + 1}"


def main():
    repo = os.environ["GH_REPO"]
    default = V.gh("api", f"repos/{repo}", "--jq", ".default_branch").strip()
    prs = sorted(V.api_list(f"repos/{repo}/pulls?state=open&per_page=100"), key=lambda p: p["number"])
    now = dt.datetime.now(dt.timezone.utc)
    judged, merged = 0, 0
    for p in prs:
        n, sha = p["number"], p["head"]["sha"]
        head_repo = (p["head"].get("repo") or {}).get("full_name")
        if p["base"]["ref"] != default or not head_repo:
            continue
        files = V.api_list(f"repos/{repo}/pulls/{n}/files?per_page=100")
        if not touches_submissions(files):
            continue
        prior = V.latest_verdict(V.pr_comments(repo, n), sha)
        go, why = due(prior, now)
        if not go:
            print(f"#{n} {sha[:12]}: skip ({why})")
            continue
        if judged >= MAX_CHECKS:
            print(f"#{n} {sha[:12]}: waiting for the next sweep (limit of {MAX_CHECKS} per run)")
            continue
        judged += 1
        try:
            verdict = V.judge(repo, n, sha, head_repo, p["user"]["login"], files=files,
                              fault=prior if prior and prior["result"] == "FAULT" else None)
        except (SystemExit, Exception) as e:      # one bad pull request must not stop the sweep
            print(f"#{n} {sha[:12]}: error, left for the next sweep: {e}")
            continue
        merged += verdict == "ACCEPTED"
        print(f"#{n} {sha[:12]}: {why} -> {verdict}")
    print(f"sweep: judged {judged}, merged {merged}")
    if merged:   # a GITHUB_TOKEN merge triggers no push workflow, so start advance.yml as verdict.yml does
        subprocess.run(["gh", "workflow", "run", "advance.yml"], check=False)


if __name__ == "__main__":
    main()
