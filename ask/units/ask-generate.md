# ask-generate: propose five candidates

**Input:** none; any field of knowledge is open (the maintainer, 2026-11-24). **Replicas:** 1. **Cost:** an hour of agent time and a dozen searches.

Read `LEDGER.md` (Mission, Depth requirement and its worked pass/fail pairs, "Where candidates come from") and the whole
of `ledger/INDEX.md`. Propose five candidates in any field or fields; say which in `domain`. The field is free, the
bar is not: every candidate must be deep (about the subject itself, not about how it is studied), must have a clear
test of what would count as an answer, and must matter if answered. Replace any candidate that fails the Depth requirement
before you submit: the checker refuses a record carrying a depth `Fail`.

```json
"candidates": [ {
  "question": "one sentence, the canonical formulation",
  "alternatives": ["second phrasing", "third phrasing"],
  "domain": "Mathematics - additive combinatorics",
  "motivation": "the gap, anomaly or observation that prompted it",
  "presuppositions": ["every assumption the question makes"],
  "depth": {"object_test": "The answer would be a fact about ...",
            "deletion_test": "if every paper, database and protocol vanished, would it still have an answer? why",
            "result": "Pass"}
} ]
```
**Toward an open problem.** A unit whose id is `Q-GEN-<problem>-<round>` names one open problem in `inputs.problem`.
Its five candidates must each be smaller than that problem, must not be the problem itself or a known reformulation
of it, and must each carry a link to it. In any other generate unit a link is optional: add one when an answer
really would bear on a problem listed by `python3 verify/problems.py`, and leave it out otherwise. A link is checked
later by people who did not write it. See [problems/README.md](../../problems/README.md).

```json
"bears_on": [{"problem": "OP-MATH-ERDOS-AP", "relation": "would settle | would bound | special case | evidence | method",
              "how": "what an answer would change about the problem, in at least 60 characters"}]
```

Exactly five. You may not take the research units your candidates open; other contributors will.
