# ask-generate: propose five candidates

**Input:** none. **Fields:** mathematics, physics, computer science, biology or medicine (the maintainer, 2026-11-27; any field
was open from 2026-11-24 until then). **Replicas:** 1. **Cost:** an hour of agent time and a dozen searches. In tokens,
about 550,000 going by the founding pipeline's figure of about 110,000 per candidate; a whole unit has not been
measured yet (`python3 verify/costs.py` has the current figure).

Read `LEDGER.md` (Mission, Depth requirement and its worked pass/fail pairs, "Where candidates come from") and the whole
of `ledger/INDEX.md`. Propose five candidates, each in one of the five fields. `domain` starts with the field's name,
then the subfield, and the checker refuses any other start; a question about AI goes under Computer science. The
method may come from anywhere. What must be one of the five is the target field: the one whose literature decides
whether the question is new and whose community would act on the answer. Every candidate must be deep (about the
subject itself, not about how it is studied), must have a clear test of what would count as an answer, and must
matter if answered. Replace any candidate that fails the Depth requirement before you submit: the checker refuses a
record carrying a depth `Fail`.

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
