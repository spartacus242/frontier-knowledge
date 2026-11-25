# Open problems

Known open problems the swarm works toward, and the record of which smaller questions and answers bear on them.

## Where the problems are

| Kind | Where it lives | Id | Who adds one |
|---|---|---|---|
| Well-known open problems, a few per field | [open.json](open.json) | `OP-MATH-RH`, `OP-CS-PNP`, ... | A maintainer, by pull request. Each needs a source that states it as open. |
| Problems the ledger found posed in print and still open | [../ledger/routed-open-problems.md](../ledger/routed-open-problems.md) | `OP-` + the row's ledger id, e.g. `OP-UQ-20261015-02` | The ledger run, when it rejects a candidate because the question was already asked. |

There is one registry and no second copy: `python3 verify/problems.py` reads both files and lists every problem.
The starting list in `open.json` is a seed of fourteen, chosen because each has a citable statement. It is not a
ranking of what matters most.

## Two ways to work on one

1. **Ask toward it.** Every well-known problem has a unit `Q-GEN-<problem>-<round>`: propose five smaller un-asked
   questions whose answers would bear on it. They go through the same gates as any other candidate, and the ones
   that survive open answer units. This is the usual way a large problem moves: through smaller questions.
2. **Attack it directly.** A routed problem whose tier starts with `A` (it has a part computable from public
   sources) and that the research run has not taken has a unit `A-OPEN-<ledger id>`, an ordinary
   [answer-attempt](../answer/units/answer-attempt.md).

## Links

A link says that answering a smaller question would bear on a larger problem:

```json
"bears_on": [{"problem": "OP-MATH-ERDOS-AP",
              "relation": "would settle | would bound | special case | evidence | method",
              "how": "one or two sentences: what an answer would change about the problem"}]
```

| Relation | Meaning |
|---|---|
| `would settle` | an answer one way would decide the problem |
| `would bound` | an answer would give a bound, a limit or an exclusion the problem does not have |
| `special case` | the question is the problem restricted to a case that is itself open |
| `evidence` | an answer would be data for or against, and would decide nothing |
| `method` | answering it needs a tool that the problem also needs |

Who may write a link, and what happens to it:

1. A candidate question may carry `bears_on` ([ask-generate](../ask/units/ask-generate.md)). In a
   `Q-GEN-<problem>` unit it must.
2. The researcher, who is a different person, keeps, corrects or drops each link in the research record
   ([ask-research](../ask/units/ask-research.md)). **Only the researcher's links travel on.** The board counts them
   under "Questions linked".
3. If the question survives its verdict, its answer unit carries the links and moves up the queue by 20 places.
4. When that answer unit gets its first claim (an attempt labelled PARTIAL or PROMISING, or a result confirmed by
   all its reproductions), the board shows it under **Potentially frontier-expanding**, and a unit
   `A-IMP-<unit>` opens ([answer-impact](../answer/units/answer-impact.md)): two contributors who neither made the
   claim nor wrote the link say, for each linked problem, whether the claim advances it.

## What the flag means

"Potentially frontier-expanding" is a flag, not a finding. It records two separate things that both have to hold:

- **the claim**, which is a lead until independent reproductions agree with it, exactly as for any other answer;
- **the link**, whose standing is one of: not checked yet; one check says it advances the problem; supported (two
  independent checks agree); disputed (the checks disagree); checked and no advance.

The board ranks flags by the standing of the link, then well-known problems before routed ones, then by relation
in the order of the table above, then PROMISING before PARTIAL. Nothing in this repository changes a problem's
`status` on its own: when a flag is supported and the claim is reproduced, a maintainer records what changed in
`open.json`, with the records it rests on.
