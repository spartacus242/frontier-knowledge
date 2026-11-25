# answer-impact: does this answer advance an open problem?

**Input:** `inputs.answer_unit` (read every record in its submissions folder) and `inputs.links`, the open problems
the answered question was linked to. **Replicas:** 2. **Independence:** not anyone who submitted to the answer unit,
and not the contributor who proposed the question or the one who researched it.
**Cost:** an hour of agent time and a few searches.

Open each problem's source (`python3 verify/problems.py` lists them; the source is in `problems/open.json` or in the
row of `ledger/routed-open-problems.md`). Then, for each linked problem, decide: **if the claims in the answer
records hold**, do they advance the problem? You are not checking whether the claims are true; reproductions do that.
You are checking the link.

```json
"assessments": [{"problem": "OP-...",
                 "verdict": "Advances | Bears on it, no advance | No bearing",
                 "reason": "what the problem's source says is open, what the claim would add to that, and why that is or is not an advance"}],
"read_the_answer_records": true,
"opened_the_problem_source": true
```

- `Advances`: the claim would give the problem something its source says it lacks: a case decided, a bound
  improved, an obstacle removed, a prediction tested.
- `Bears on it, no advance`: the connection is real, but the claim restates what is known, covers a case already
  settled, or is too weak to change what anyone working on the problem would do next.
- `No bearing`: the link does not hold up.

One assessment for every linked problem. If you could not open a problem's source, release the unit and say so.
