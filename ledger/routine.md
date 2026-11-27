# The scheduled routine: intended settings

The routine "Un-Asked Questions Ledger" is stored by the scheduler, outside this repository, and only the ledger thread can change it. This file records what its settings are meant to be under the weekly token cap (`LEDGER.md`, Parameters: WEEKLY TOKEN CAP, RUN ESTIMATE, CADENCE), so that the change can be read and agreed before it is made.

**Status on 2026-11-27: not applied.** the maintainer paused the routine that day. It still holds the six-hourly cron line and the old prompt, and it stays paused and unchanged until he says to turn it back on. When he does, the name, the cron line and the prompt below are set together, and this paragraph is updated with the date.

| Setting | Now (paused) | Intended |
|---|---|---|
| Name | Un-Asked Questions Ledger (every 6 hours) | Un-Asked Questions Ledger (weekly, under the token cap) |
| Cron (UTC) | `33 */6 * * *` | `33 12 * * 4`, which is Thursday 12:33 |
| Enabled | no | yes, when the maintainer says |

The mathematics batch that was paused unfinished on 2026-11-27 (2026-11-26-1235) is not part of this. It was started before the cap, it has no row in `ledger/usage.md`, and the routine does not resume it. It waits for the maintainer.

## Intended prompt

```
Un-Asked Questions Ledger, weekly wake (Thursday 12:33 UTC, under the weekly token cap the maintainer set on 2026-11-27). Treat this as a fresh run: do not rely on memory of earlier runs in this conversation; the repo is the source of truth.

1. In spartacus242/frontier-knowledge, run: git fetch origin main && git checkout main && git pull origin main.
2. Before anything else, run: python3 -I ledger/tools/next-run.py wake <today's UTC date as YYYY-MM-DD>. If it added a row to ledger/usage.md, commit that row and push it. Then do what it printed:
   - WAIT: reply in this thread with the balance in one sentence and stop. Start no batch and spawn no agent.
   - HOLD: an earlier run was started and never logged, and no row was added. Follow LEDGER.md, END OF RUN step 1, for that run, and reply with what you did. Start a batch at this wake only if a second `wake` then prints RUN.
   - RUN: go on to step 3 with the area and the four drafting methods it printed.
3. Read LEDGER.md at the repo root in full. It is your complete instructions; follow it exactly: the DOMAIN SCOPE, the area and methods from step 2, the duplicate check against ledger/INDEX.md (no duplicates of earlier entries), the documented search minimum, strict fresh-context adversaries for Gate 4, "Checking in proportion" and no checking beyond it, and END OF RUN, including `next-run.py run` with the tokens used. Continue ledger IDs from the highest already used today. Name the batch file by UTC date and start time. Do not edit anything under research/. Do not resume the batch 2026-11-26-1235, which waits for the maintainer.
4. Commit everything under ledger/ and push to main (pull and rebase first, since the research run pushes to the same branch; retry on network errors with backoff). Never rewrite history.
5. Reply in this thread with a short summary: counts by status, each Validated, Provisional or Under-asked question in one line, the rejection rate, anything routed to research, anything owed, the tokens the run and its checking used, and the balance left. Link the batch file on GitHub.
```

## What changes from the prompt in force until 2026-11-27

- The wake comes once a week, not every six hours, and the first thing it does is ask the token account whether a run fits. Most of the old prompt's cost was that every wake started a batch.
- A wake that does not start a batch says so in one sentence and spawns nothing.
- The old line "if a previous batch is still in progress in this session, finish and push it first" is replaced by HOLD: the token account refuses a new wake while a run it started has no row, which holds for a run in any session.
- The summary now carries the tokens used and the balance left.
