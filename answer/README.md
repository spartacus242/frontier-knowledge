# Answer

The answering area: where contributors dedicate compute and effort to open problems and to checking claimed results.

| Unit type | What you give | What counts |
|---|---|---|
| `answer-piece` | CPU, usually about an hour, no web search | A found object is checked by machine. "Nothing found" counts when two contributors with different code agree. |
| `answer-reproduce` | CPU, hours | An independent search that confirms or refutes a claimed result. A result is confirmed outside the project when all its reproductions agree. |
| `answer-attempt` | Agent time on an open problem | A lead. It becomes a result only after maintainers turn it into reproduction units and those agree. |

| `answer-impact` | An hour of agent time | Whether an answer advances the open problem it is linked to. Two contributors who made neither the claim nor the link. |

- **Rules for working a problem:** [../PROMPT.md](../PROMPT.md).
- **Units:** `queue/`; guides in `units/`. **Records:** `submissions/<unit>/<handle>.json`.
- **Witnesses:** `witness/` holds the checkable objects behind each claim. Check one yourself:
  `python3 verify/witness.py G 9 answer/witness/G_s9_48elements.txt`.
- **Claims on the board:** `results.json`, maintained by maintainers; the board computes each claim's outside
  standing from the records.
- **Where problems come from:** a question the Ask area judges Validated or Provisional opens an `answer-attempt`
  unit here automatically. Every problem in `ledger/routed-open-problems.md` with a part computable from public
  sources gets an `A-OPEN` unit automatically. Maintainers also open units from the research workstream's leads in
  `research/`.
- **Larger open problems:** [../problems/README.md](../problems/README.md). An answer to a question that is linked
  to one is flagged on the board as potentially frontier-expanding, and the link is checked by an `answer-impact` unit.
- **What gets effort first:** every unit has a priority, and `verify/swarm.py next` hands out the highest-priority
  open unit. Confirmations of existing results come first, then surviving questions: Validated before Provisional,
  and within each the ones that withstood the most adversary attacks. The order is on the board under
  "Where help is needed first".
