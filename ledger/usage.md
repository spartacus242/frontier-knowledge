# Token use and the weekly budget

Since 2026-11-27 the scheduled ledger runs stop at a weekly token cap. The rule is in `LEDGER.md` (Parameters: WEEKLY TOKEN CAP, RUN ESTIMATE, CADENCE). This file is the account, and `ledger/tools/next-run.py` keeps it.

## How the account works

- The balance starts at 0.
- The first wake of each budget week adds the cap to the balance, up to a ceiling of two caps. A budget week starts on the wake day (Thursday), so a wake that comes a day late still counts for its own week. A second wake in the same week adds nothing.
- A run starts only when the balance after the wake is at least RUN ESTIMATE. Otherwise the wake is logged as WAIT and no batch starts.
- When a run ends, the tokens it used are subtracted, run and checking together. A run that used more than the balance leaves a debt, and the next wakes pay it down before another run starts.
- A run that has started is finished, not cut short.
- A wake that says RUN opens a run. Until that run has its own row below, the tool logs no further wake and prints HOLD, and no batch starts. So the tokens of a run that died are counted before another begins.

**What is counted.** The token figure the harness reports for each agent when it finishes, summed over every agent the run spawns and every agent its checking spawns. The run session's own turns are not in that count, because the harness does not report them to the session. So the true cost of a run is somewhat higher than its row says, and the cap should be read with that in mind.

## The log

Do not edit this table by hand. `python3 -I ledger/tools/next-run.py wake <YYYY-MM-DD>` adds a wake row and `python3 -I ledger/tools/next-run.py run <batch> <run tokens> <checking tokens>` adds a run row. The tool checks every "Balance after" cell against its own replay of the rows above it and stops if one differs. It also reads the Note cell of each wake row (RUN or WAIT), so that cell is part of the account. A run is logged once, under its batch name.

| Date (UTC) | Event | Tokens | Balance after | Note |
|---|---|---|---|---|

## Before the cap

For comparison only; these two are not rows of the account. Both ran under the fifteen-draft, five-candidate shape with full checking of every entry.

| Batch (UTC) | Run | Checking | Total |
|---|---|---|---|
| 2026-11-26 00:35 (open turn, committed) | about 7.5 million | about 12.4 million | about 19.9 million |
| 2026-11-26 12:35 (mathematics, paused unfinished on 2026-11-27) | about 7.3 million | about 12.1 million when paused | about 19.4 million |

Measured medians from the second of them, which the RUN ESTIMATE in `LEDGER.md` is built from: one headline draft about 110 thousand tokens, the ranker about 144 thousand, one developer about 130 thousand, one Gate 0 to 3 researcher about 220 thousand, one adversary about 155 thousand, one judge about 205 thousand, one source re-read about 90 thousand, one proof check about 120 thousand.
