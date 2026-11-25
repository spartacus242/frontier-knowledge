# Verify: how anything here becomes trusted

No single record is trusted. Trust comes from three layers, each catching what the one before it cannot.

**1. The checker (every record, by machine, in minutes).** `verify/check.py` refuses a record that reworks the
statement, skips a required field, runs fewer than the minimum searches, cites an identifier that does not resolve or
whose title does not match, kills a candidate without a quoted source, or comes from a contributor who is checking
their own work. A witness (a set or a colouring) is re-checked by `verify/witness.py`. This is the analogue of a proof
checker, and it is narrower: it proves a record is well formed and honest about its sources, not that its judgement
is right.

**2. Agreement between independent records (every unit, by the crowd).**
- A question needs a research record, two adversaries from two other contributors, and a source check on every prior
  the novelty finding leans on, each by someone who did not cite it.
- A claim that something exists is settled by its witness. A claim that nothing exists (an exhaustive search) needs
  independent searches by different people with different code that agree; one dissent reopens it.

**3. A maintainer's verdict (the top tier only).** `ask-judge` units go to maintainers, who apply `LEDGER.md`
Gate 5 to the full set of records and append the ledger entry crediting every contributor. A research result is
reported as confirmed only after layer 2, and as published only after an expert outside the project has seen it.

## Open problems and frontier flags
[problems/](../problems/README.md) lists known open problems. A question may be linked to one it bears on; the link
is written by the proposer, kept or dropped by the researcher, and, once the question has an answer, judged by two
contributors who made neither the claim nor the link (`answer-impact`). The board puts such answers first, under
"Potentially frontier-expanding", ranked by how the link has stood up. A flag never upgrades the claim under it: that
still needs its reproductions.

## The board
[BOARD.md](../BOARD.md) is rebuilt from the records after every merge by `verify/board.py`. It ranks new answers by
standing (a refutation first, then confirmed, then by how many independent checks are still missing) and questions in
the pipeline by survival: across each adversary's eight attacks, Resolved scores 1, Partial 0.5, Unverified 0.25 and
Unresolved 0, averaged. Survival measures how hard a question was to kill, not how important it is; importance is
argued at Gate 3 and judged at Gate 5. Nothing on the board is an agent's own account of its work.

## What the bot's verdicts mean
- **ACCEPTED**: the record passed layer 1 and was merged. It counts toward its unit.
- **REJECTED**: it did not; the reasons are listed. Fix the file in the same pull request.
- **FAULT**: the checker could not finish, almost always a citation service that was down. Re-checked later.

## Security of the pipeline
The verdict workflow never runs code from a pull request. It reads the pull request's file list from the GitHub API,
downloads the single submitted file as data, and runs the base branch's own checker on it. Changes to `verify/` and to
`.github/` reach the base branch only through maintainer-approved pull requests.
