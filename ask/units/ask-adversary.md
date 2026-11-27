# ask-adversary: Gate 4, try to kill it

**Input:** the research record named in `inputs.research_unit` (or the ledger entry in `inputs.ledger_entry`, read
only the fields the unit names). **Replicas:** 2, from two different contributors, ideally on different model families.
**Independence:** not the generator or the researcher. **Cost:** 8 to 15 searches, an hour of agent time; about
155,000 tokens on the one model measured so far (`python3 verify/costs.py` has the current figure).

Your only job is to kill the candidate. Follow `LEDGER.md` Gate 4: restate the question in your own words first, run
the depth check on your restatement, then run all eight attacks.

```json
"restatement": "...",
"depth": {"completion": "The answer would be a fact about ...", "survives_deletion": true, "result": "Pass"},
"disguise_queries": [{"query": "in a vocabulary the research record did not use", "returned": "..."}],
"attacks": {
  "triviality": {"status": "Resolved | Partial | Unresolved | Unverified", "argument": "...",
                 "evidence": [{"citation": {...}, "quote": "the line you rely on", "locus": "section, page or table"}],
                 "own_reasoning": false},
  "disguise": {...}, "combinatorial_novelty": {...}, "presupposition_failure": {...}, "vagueness": {...},
  "significance_inflation": {...}, "reason_for_silence": {...}, "dissolution": {...}
},
"recommended": "Rejected | Provisional | Validated-eligible"
```
Unresolved means you ran the attack and the candidate's best answer was weak. Unverified means the check did not run;
it never kills. An Unresolved attack needs a source you opened and quoted, or `own_reasoning: true` stating that the
step is your own argument. Unresolved on triviality, disguise or presupposition_failure means `Rejected`.

The research record's `solving_method` is a recommendation and is not under attack: it is never a ground for a kill.
If the method it names would not bear on the question, say so in one line in the `significance_inflation` argument.
