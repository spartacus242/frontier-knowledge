# Work units

Every unit is a file in `ask/queue/` or `answer/queue/` (units whose id starts with `A-` are answer units). Its `statement` is frozen and its `inputs` are everything you are allowed to read
about it besides the open literature. Every record carries these common fields:

| Field | Meaning |
|---|---|
| `unit`, `handle` | the unit id and your GitHub handle; must match the path `<area>/submissions/<unit>/<handle>.json` |
| `statement_sha256` | sha256 of the unit's statement, so nobody works a reworded version (`swarm.py template` fills it) |
| `model`, `agent` | the model id and agent you ran, e.g. `claude-opus-5-5` and `claude-code 3.x`. Required on every record; the checker refuses a placeholder. Write `human` as the model for a unit a person did without one. It is your own report and is not verified. The board shows it beside each record. |
| `fresh_context` | `true`: you began in a new session that had seen no other records for this question beyond the unit's inputs |
| `started`, `finished` | ISO times |

Type guides, asking: [ask-generate](../ask/units/ask-generate.md) · [ask-research](../ask/units/ask-research.md) ·
[ask-adversary](../ask/units/ask-adversary.md) · [ask-verify](../ask/units/ask-verify.md) ·
[ask-judge](../ask/units/ask-judge.md). Answering: [answer-reproduce](../answer/units/answer-reproduce.md) ·
[answer-piece](../answer/units/answer-piece.md) · [answer-attempt](../answer/units/answer-attempt.md) ·
[answer-impact](../answer/units/answer-impact.md).

The gates themselves are defined in `LEDGER.md`. These guides say what each unit must hand back; `LEDGER.md` says how
to do it well. Where they disagree, `LEDGER.md` wins and the guide is a bug.

## How units unlock each other

```
Q-GEN-n  ──►  Q-RES-n-1..5  ──►  Q-ADV-n-k (2 adversaries, different people)  ──┐
   │                         └─►  Q-VER-n-k-1..3 (one per nearest prior)  ────────┴─►  Q-JDG-n-k (maintainer)
   └─► Q-GEN-(n+1), the next round, in any field              a Validated or Provisional verdict ─► A-ATT-n-k (answer/)
```

Open problems ([problems/README.md](../problems/README.md)) add three kinds of unit:

```
Q-GEN-<problem>-r   five smaller questions toward one well-known open problem  ──► the same chain as Q-GEN-n, and round r+1
A-OPEN-<ledger id>  a direct attempt at a routed open problem with a computable part
A-IMP-<unit>        opens when a linked answer unit gets its first claim: does the claim advance the problem? (2 people)
```

Other answer units are opened by maintainers from the research workstream's leads.
