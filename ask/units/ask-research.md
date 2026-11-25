# ask-research: Gates 0 to 3 on one candidate

**Input:** `inputs.candidate`. **Replicas:** 1. **Independence:** not the contributor who generated it.
**Cost:** 8 to 20 web searches and an hour or two of agent time.

Follow `LEDGER.md` Gates 0, 1, 2 and 3 exactly. `gate0.canonical` must be the candidate's question unchanged; the one
permitted reformulation goes in `gate1.reformulation`.

```json
"gate0": {"canonical": "...", "presuppositions": ["..."],
          "depth": {"object_test": "The answer would be a fact about ...", "deletion_test": "...", "result": "Pass"}},
"gate1": {"what_counts_as_an_answer": "the evidence, experiment, proof or argument that would settle it",
          "reformulation": "optional, the one permitted", "presupposition_status": "established or flagged, each"},
"gate2": {"queries": [{"query": "...", "returned": "one line on what came back"}],
          "nearest_priors": [{"citation": {"id": "doi:10....", "first_author": "Surname", "year": 2019, "title": "..."},
                              "unit_of_analysis": "...", "endpoint": "...", "comparator": "...", "estimand": "...",
                              "difference": "precisely how the candidate differs"}],
          "novelty": "High | Medium | Low | Unverified"},
"gate3": {"consequence": "...", "audience": "...", "fecundity": "...", "anchoring": "..."},
"recommended": "Proceed | Reject",
"reject_gate": "only if Reject: which gate and why"
```
If the candidate carries `bears_on` links to open problems (`inputs.candidate.bears_on`), judge each one and put the
links you stand behind in the record's own top-level `bears_on`, in the same form, correcting the relation where it
is overstated. Drop a link you cannot defend; add one the proposer missed. Only the links in your record travel on
to the answer unit and the board ([problems/README.md](../../problems/README.md)).

At least 8 distinct queries, one of them the obvious title a paper on this would carry. Exactly the three nearest
priors, each with its four-part comparison. Every prior you cite opens a source-check unit for someone else, so cite
what you actually opened.
