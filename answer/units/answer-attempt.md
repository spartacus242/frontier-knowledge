# answer-attempt: work an open problem

**Input:** a question that survived the Ask area (`inputs.question_records` lists its research, adversary and verdict
records; read them first), or a problem from `ledger/routed-open-problems.md` or the research workstream.
**Replicas:** set per unit; a NO PROGRESS record is kept and credited but does not fill a slot. Follow `PROMPT.md` (the research run's instructions) for how to work it and label it.

```json
"label": "NO PROGRESS | PARTIAL | PROMISING",
"summary": "what you tried and what you found",
"claim": "the exact claim, or 'none'",
"witness": "if the claim has a checkable object",
"artifacts": ["links to code and logs"]
```
A unit whose id starts with `A-OPEN-` is a direct attempt at a problem from `ledger/routed-open-problems.md`
(`inputs.problem`); open `inputs.source_showing_it_is_open` first and confirm it is still open. If the unit carries
`bears_on`, or is an `A-OPEN` unit, a PARTIAL or PROMISING record puts it on the board under "Potentially
frontier-expanding" and opens an [answer-impact](answer-impact.md) unit for two other contributors.

A PROMISING claim is never a result on its own: a maintainer turns it into answer-reproduce units for others.
