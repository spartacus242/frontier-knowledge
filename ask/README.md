# Ask

The asking area. A question enters the ledger only after it has survived other people's attempts to kill it.

```
Q-GEN-n  ──►  Q-RES-n-1..5  ──►  Q-ADV-n-k (2 adversaries, different people)  ──┐
 five candidates,   Gates 0-3 on    Q-VER-n-k-1..3 (one per nearest prior)  ───┴─►  Q-JDG-n-k (maintainer verdict)
 one area           one candidate
   └─► Q-GEN-(n+1), the next round                                               └─► a surviving question opens A-ATT-n-k in answer/
```

- **Toward open problems.** `Q-GEN-<problem>-<round>` units ask for smaller un-asked questions that bear on one
  known open problem; any candidate may carry a `bears_on` link to one. See
  [../problems/README.md](../problems/README.md).
- **Any field.** Since 2026-11-24 a question may come from any field of knowledge. What is not relaxed is the depth
  check, applied to every candidate at Gate 0 and again by each adversary: the question must be deep (about the
  subject itself, not about how it is studied), have a clear test of what would count as an answer, and be important
  if answered.
- **Rules:** [../LEDGER.md](../LEDGER.md). Read its Mission, Depth requirement and the gate you are running.
- **Order of work:** questions closest to a verdict come first (source checks, then adversaries, then research, then
  new candidates), so the pipeline finishes questions before it starts more.
- **Units:** `queue/` holds every open and finished ask unit; `units/` says what each type must hand back.
- **Records:** `submissions/<unit>/<handle>.json`, one per contributor per unit.
- **Where candidates come from:** `LEDGER.md` lists the generating moves ("Where candidates come from"). That section
  is where new ways of finding deep questions are added, and every `ask-generate` unit follows it.
- **The record:** judged questions are appended to [../ledger/unasked-ledger.md](../ledger/unasked-ledger.md) with
  credit to everyone who ran a gate. A question that turns out to be already asked and still open is routed to
  [../ledger/routed-open-problems.md](../ledger/routed-open-problems.md), where the Answer area picks it up.

Library units (`V-...`) live here too: a source that only a person with a library can open.
