# Where deep questions come from

Research note of 2026-11-23, requested by the maintainer: "I think a lot of the big questions spawned from patterns being recognized and then asking if it applies to other areas or forcing the pattern to continue to it's natural conclusion. What are some general processes that lead to other deep questions to be asked? Can we incorporate those into our instructions for asking the questions?"

This note is the reasoning. The instructions it produced are the "Where candidates come from" section of LEDGER.md, carried verbatim by runner v20.

## Short answer

The maintainer's two processes are real and well documented, and they are two of about ten. The common thread across the history, the philosophy and the cognitive science is that a deep question is almost never invented from nothing. It is **derived**: someone takes one specific thing that is already known and applies one of a small number of moves to it. The moves can be written down as steps, which is what makes them usable as instructions.

The second finding matters as much for this project. Studies of how working scientists choose problems, and of how language models generate research ideas, agree on the failure mode: left alone, both drift to safe, similar, incremental questions. Structure is what counters that, so the new instructions require every draft to show its derivation and require the fifteen drafts to be spread across fourteen different moves.

## The processes

Each entry gives the move, a historical case, the source for the idea, and where it landed in LEDGER.md.

**1. Pattern transfer: does it apply elsewhere?** (the maintainer's first.) The best account of why this works is Mary Hesse's. When a known system is used as a model for an unknown one, the properties fall into three groups: those known to match (positive analogy), those known not to (negative), and those nobody has checked (neutral). The neutral group is where the questions are. Dedre Gentner's structure-mapping work adds the rule that productive analogies carry over relations between things, not surface likeness. Kevin Dunbar's observational studies of molecular biology labs found analogy in constant use, with distant analogies rarer than near ones. Cases: André Weil's 1940 "Rosetta stone" between number fields, function fields and Riemann surfaces, which the Langlands programme still works from; Schrödinger's *What Is Life?* asking a physicist's question about heredity; Hopfield carrying spin-glass physics to memory. In LEDGER.md: **cross-field transplant**, rewritten as a mapping exercise whose question must come from the never-checked list.

**2. Pushing a pattern to its natural conclusion.** (the maintainer's second.) Dirac kept the negative-energy solutions of his equation instead of discarding them and predicted antimatter. Einstein at sixteen asked what a light wave would look like to someone moving alongside it. Chandrasekhar followed the white-dwarf mass-radius relation until it gave zero radius, which is the first sign of gravitational collapse. Pólya describes the general move as generalisation and specialisation to extreme cases; Lenat's AM program (1976) mechanised it, with rules of the kind "examine extreme cases" and "consider the inverse", and rediscovered primes and Goldbach's conjecture from set theory. AM is also a warning: critics showed its output was over-interpreted, and Lenat conceded part of the point. In LEDGER.md: **pattern continuation**, new.

**3. Anomalies.** Kuhn's account of scientific change runs through anomalies: results normal science cannot absorb. Peirce gave the logical form of the step from anomaly to question: "The surprising fact, C, is observed; but if A were true, C would be a matter of course." Dunbar found that over half the findings in the labs he observed were unexpected, and that what distinguished productive labs was attending to them instead of explaining them away. In LEDGER.md: **anomaly mining**, now with Peirce's sentence as its step.

**4. Unexplained coincidences.** Two things agree and nobody knows why. Inertial and gravitational mass were known to be equal for two centuries before Einstein asked whether the equality was a law, which gave general relativity. McKay noticed 196884 = 196883 + 1 across two unrelated parts of mathematics, which became monstrous moonshine. Dicke's "why is the universe so nearly flat?" led to inflation. In LEDGER.md: folded into **unification and coincidence**.

**5. Empty cells and conspicuous absences.** Mendeleev laid out a classification and asked about the gaps. Zwicky made a general method of it (morphological analysis: list the independent properties, enumerate every combination, look at the unoccupied ones). The physicist's version is Gell-Mann's "everything not forbidden is compulsory": if theory permits something and it is not seen, the absence needs explaining. Monopoles, proton decay and Fermi's "where is everybody?" are all questions of this form. In LEDGER.md: **empty cell**, new.

**6. Symmetry and its breaking.** Noether's theorem ties each continuous symmetry to a conservation law, and David Gross's review argues symmetry became the organising principle of twentieth-century physics. Asymmetries generate questions just as well: why life uses one molecular handedness, why there is more matter than antimatter. P. W. Anderson's "More Is Different" makes broken symmetry the source of new behaviour at each scale. The mathematician's relatives are the converse, the dual and the inverse problem (Kac: "Can one hear the shape of a drum?"). In LEDGER.md: **symmetry and its breaking**, new.

**7. Collisions between accepted theories.** Many of the deepest questions came from applying two trusted results in a place where both should hold and finding they disagree: Maxwell and Newton on moving bodies (special relativity), thermodynamics and electromagnetism on black-body radiation (the quantum), general relativity and quantum theory at a horizon (Hawking radiation and the information problem). Popper's line that science starts from problems, and Lakatos's *Proofs and Refutations*, where counterexamples force better questions, are the philosophical versions. In LEDGER.md: **theory collision**, new.

**8. Dropping an assumption.** Non-Euclidean geometry came from removing one postulate; special relativity from removing absolute simultaneity. Pólya's "drop a condition, does the conclusion survive?" is the working form. In LEDGER.md: **presupposition inversion** and **textbook inversion**, the first now with explicit steps.

**9. Limits.** Carnot asked what bounds any heat engine, Shannon what bounds any channel, Turing what no machine can compute. In LEDGER.md: **limits**, already added by PR #2, now with steps.

**10. Unconnected literatures.** Don Swanson showed in 1986 that one literature tied fish oil to blood viscosity and another tied blood viscosity to Raynaud's syndrome, that the two never cited each other, and that the question "does fish oil help Raynaud's?" had therefore never been asked. It was later tested and supported. This is the most mechanical of the processes and the closest to what this ledger does. In LEDGER.md: **unlinked literatures**, new.

**11. Asking the other kind of question.** Tinbergen's four questions (mechanism, development, function, evolutionary history) and Mayr's proximate/ultimate split show that a well-studied phenomenon can have one kind of question answered exhaustively and another never posed. In LEDGER.md: **silence mapping**, now with the list of question kinds.

**12. New instruments** and **capability inversion** are unchanged from before.

## What the evidence says about doing this well

- **Anchor in the conventional, add one unusual step.** Uzzi and colleagues, on 17.9 million papers, found the highest-impact work is "primarily grounded in exceptionally conventional combinations of prior work" with an atypical combination inserted; such papers were twice as likely to be highly cited. This is why the instructions demand an established seed and exactly one move.
- **Distance pays, and is avoided.** Shi and Evans found that "unexpected combinations of contents and contexts" predict outsized impact, most often when scientists from one field address a distant one. Foster, Rzhetsky and Evans found that in biomedical chemistry repeat statements outnumbered new ones six to one (85.8% to 14.2%): risky strategies were "more likely to be ignored but also more likely to achieve high impact", and the extra reward did not cover the extra risk for a career. A ledger has no career, so it can take the risk scientists rationally decline. This is why transplants are told to prefer distant source fields.
- **Models drift to sameness.** Si, Yang and Hashimoto found LLM research ideas were judged more novel than expert ideas but weaker on feasibility, and named "lack of diversity in generation" as an open problem. This is why the spread rule exists and why no two drafts may share a seed.
- **Problem finding is a separate skill from problem solving.** Einstein and Infeld: the formulation of a problem is often more essential than its solution. Getzels and Csikszentmihalyi's long-term study of artists found time spent finding the problem predicted later success better than skill at executing. This is why seeds are collected before any question is written.

## What changed in the instructions

1. "Where candidates come from" goes from nine one-line labels to fourteen methods with steps, plus six rules that apply to all of them (seeds first, one move per draft, deepen once, record the derivation, spread, distrust the first question that comes to mind).
2. Every draft now carries a derivation line (seed, move, why the question follows), which the ranker sees and the batch report keeps. It makes the method auditable: a batch can be checked afterwards for which moves produce survivors.
3. The runner (v20) embeds the section verbatim in the drafting prompt and `check-runner-sync.py` verifies it, the same way the Ambition section is handled.

No gate, score, threshold or status changed.

## Limits of this note

- It is untested. No batch has run under these instructions; the jobs are paused. The honest test is whether drafts produced this way score higher with the ranker and survive Gate 2 more often than the last batches did, and the derivation line makes that measurable by method.
- The historical cases are retrospective and selected for success. Nobody records the times a pattern was pushed to its conclusion and gave nonsense. The methods raise the odds of a deep question; they do not certify one, which is what the gates are for.
- Fourteen methods across fifteen drafts is a judgement call to force variety. If some methods prove barren in some areas (symmetry in medicine, say), the rule should relax to "at least ten of fourteen".

## Sources

Opened and checked this session (bibliographic details and the quoted findings):

- Uzzi, Mukherjee, Stringer, Jones (2013). Atypical combinations and scientific impact. *Science* 342:468-472. Read via the Kellogg research summary page, not the journal.
- Shi, Evans (2023). Surprising combinations of research contents and contexts are related to impact and emerge with scientific outsiders from distant disciplines. *Nature Communications* 14:1641. doi:10.1038/s41467-023-36741-4.
- Foster, Rzhetsky, Evans (2015). Tradition and innovation in scientists' research strategies. *American Sociological Review* 80(5):875-908. Read as arXiv:1302.6906; the journal reference is from memory.
- Si, Yang, Hashimoto (2024). Can LLMs generate novel research ideas? A large-scale human study with 100+ NLP researchers. arXiv:2409.04109.
- Swanson (1986). Undiscovered public knowledge. *Library Quarterly* 56(2):103-118. doi:10.1086/601720. And: Fish oil, Raynaud's syndrome, and undiscovered public knowledge. *Perspectives in Biology and Medicine* 30(1):7-18. Citations confirmed via Wikipedia's Swanson page; the papers themselves were not opened.
- Lenat, Brown (1984). Why AM and EURISKO appear to work. *Artificial Intelligence* 23(3):269-294; and the critique, Ritchie, Hanna (1984). AM: a case study in AI methodology. *Artificial Intelligence* 23(3):249-268. Confirmed via Wikipedia's Automated Mathematician page, which does not list AM's individual heuristics; the two rule examples above are from memory of Lenat's thesis.
- Hesse's positive, negative and neutral analogy, as reported in Haig (2013), Analogical modeling: a strategy for developing theories in psychology. *Frontiers in Psychology* 4:348. Hesse's book was not opened.

Cited from memory, standard references, not opened this session. Treat page numbers and exact wording as unverified:

- Hesse (1966). *Models and Analogies in Science*. Gentner (1983). Structure-mapping: a theoretical framework for analogy. *Cognitive Science* 7:155-170.
- Dunbar (1995). How scientists really reason: scientific reasoning in real-world laboratories, in Sternberg and Davidson (eds), *The Nature of Insight*. The "over half unexpected" figure is from Dunbar's later summaries and was not re-checked; one attempt to open a Dunbar chapter failed.
- Kuhn (1962). *The Structure of Scientific Revolutions*. Popper (1963). *Conjectures and Refutations*. Lakatos (1976). *Proofs and Refutations*. Peirce, *Collected Papers* 5.189.
- Pólya (1945). *How to Solve It*; (1954). *Mathematics and Plausible Reasoning*.
- Zwicky (1969). *Discovery, Invention, Research through the Morphological Approach*.
- Gross (1996). The role of symmetry in fundamental physics. *PNAS* 93:14256-14259. Anderson (1972). More is different. *Science* 177:393-396. Kac (1966). Can one hear the shape of a drum? *American Mathematical Monthly* 73:1-23.
- Tinbergen (1963). On aims and methods of ethology. *Zeitschrift für Tierpsychologie* 20:410-433. Mayr (1961). Cause and effect in biology. *Science* 134:1501-1506.
- Einstein, Infeld (1938). *The Evolution of Physics*. Getzels, Csikszentmihalyi (1976). *The Creative Vision*.
- The historical cases (Dirac, Chandrasekhar, Mendeleev, Weil, McKay, Dicke, Schrödinger, Hopfield, Gell-Mann, Fermi) are textbook history told from memory.
