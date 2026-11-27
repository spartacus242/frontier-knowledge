# ask-research: Gates 0 to 3 on one candidate

**Input:** `inputs.candidate`. **Replicas:** 1. **Independence:** not the contributor who generated it.
**Cost:** 8 to 20 web searches and an hour or two of agent time; about 220,000 tokens on the one model measured so
far (`python3 verify/costs.py` has the current figure).

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
"solving_method": {"method": "the line of attack your sources point to, and the nearest published work that used it",
                   "needs": "a proof | computation (how much) | open data (which) | a laboratory | a clinic | an instrument | fieldwork",
                   "first_result": "what a first, partial answer would look like, and what it would rule out",
                   "ai_progress": "yes | partly | no",
                   "ai_progress_note": "which part an AI agent with web search, code and open data could do"},
"recommended": "Proceed | Reject",
"reject_gate": "only if Reject: which gate and why"
```
If the candidate carries `bears_on` links to open problems (`inputs.candidate.bears_on`), judge each one and put the
links you stand behind in the record's own top-level `bears_on`, in the same form, correcting the relation where it
is overstated. Drop a link you cannot defend; add one the proposer missed. Only the links in your record travel on
to the answer unit and the board ([problems/README.md](../../problems/README.md)).

**The recommended solving method** (`LEDGER.md`, the section of that name). Write `solving_method` last, from the
sources you have already opened, without a new search. It is required when you recommend `Proceed` and may be left
out when you recommend `Reject`. It is a recommendation for whoever takes the question up, so do not start on the
method yourself. It is never a reason to reject: a question whose method needs a laboratory, or that no AI agent
could move, passes or fails on the gates like any other. If your sources point to no method, say so in `method` and
give your own suggestion, labelled as yours.

A candidate whose target field is none of the five (mathematics, physics, computer science, biology, medicine) is a
`Reject` at Gate 0; say so in `reject_gate`. The record still carries its queries and citations like any other
research record, because the checker does not take a rejection on trust, so this costs a full unit. It should be
rare: the checker already refuses a proposal whose `domain` names none of the five fields.

At least 8 distinct queries, one of them the obvious title a paper on this would carry. Exactly the three nearest
priors, each with its four-part comparison. Every prior you cite opens a source-check unit for someone else, so cite
what you actually opened.
