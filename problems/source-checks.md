# Source checks for `open.json`

The fourteen problems in [open.json](open.json) were first written with their citations from memory. This file
records the check of each citation against the web, done on 2026-11-25. "Matches" means the identifier was found
attached to a work with the stated title; it does not mean the full text was read.

| Problem | Cited as | Check | Result |
|---|---|---|---|
| `OP-MATH-RH` | url: claymath.org/millennium/riemann-hypothesis/ | Page fetched | Loads, headed "Riemann Hypothesis". The page tags the problem "Active" and speaks of "a proof that it is true" as something not yet had; it does not use the word "unsolved". |
| `OP-MATH-COLLATZ` | arxiv:2111.02635, Lagarias, "The 3x+1 Problem: An Overview" | Search for the identifier | Matches. The text is a chapter from a 2010 book, posted to arXiv in 2021, so 2021 is the posting year. |
| `OP-MATH-ERDOS-AP` | arxiv:2007.03528, Bloom (with Sisask), "Breaking the logarithmic barrier in Roth's theorem on arithmetic progressions" | Search for the identifier | Matches. |
| `OP-PHYS-YM` | url: claymath.org/millennium/yang-mills-the-maths-gap/ | Page fetched | Loads, headed "Yang-Mills & the Mass Gap", tagged "Unsolved": "no proof of this property is known". The odd spelling in the address is Clay's own. |
| `OP-PHYS-DM` | doi:10.1103/RevModPhys.90.045002, Bertone (with Hooper), "History of dark matter" | Search for the identifier | Matches (Rev. Mod. Phys. 90, 045002, 2018). |
| `OP-PHYS-HTSC` | doi:10.1038/nature14165, Keimer et al., "From quantum matter to high-temperature superconductivity in copper oxides" | Search for the identifier | Matches (Nature 518, 2015). |
| `OP-CS-PNP` | url: claymath.org/millennium/p-vs-np/ | Page fetched | Loads, headed "P vs NP", tagged "Unsolved". |
| `OP-CS-OMEGA` | arxiv:2010.05846, Alman (with Vassilevska Williams), "A Refined Laser Method and Faster Matrix Multiplication" | Search for the identifier | Matches. |
| `OP-CS-GI` | arxiv:1512.03547, Babai, "Graph Isomorphism in Quasipolynomial Time" | Search for the identifier | Matches. |
| `OP-BIO-ORIGIN`, `OP-BIO-REGEN`, `OP-BIO-DIVERSITY`, `OP-MED-HIV-VACCINE` | doi:10.1126/science.309.5731.75, Kennedy (with Norman), "What Don't We Know?" | Search; the DOI page could not be fetched | **Partly checked.** The article exists as cited (Science 309, page 75, 1 July 2005, the 125th-anniversary issue), but neither the article nor its list of questions was opened, so the wording of the four questions is unchecked against it. The DOI string itself was not seen to resolve, because the publisher's page refused the fetch. The checker resolves it when a record first cites it. |
| `OP-MED-PETO` | doi:10.1016/j.tree.2011.01.002, Caulin (with Maley), "Peto's Paradox: evolution's prescription for cancer prevention" | Search for the identifier | Matches (Trends Ecol. Evol. 26(4), 175-182, 2011). |

## What was not checked

- Whether each source, read in full, states the problem in the words used in `open.json`. The statements are short
  standard formulations; anyone who finds one that misstates its problem should correct it by pull request.
- Whether any of these problems has been settled since its source was written. None was reported settled in the
  searches above.

One nuance worth knowing: four of the fourteen rest on a single magazine feature (Science, 2005) rather than on a
research paper that poses the problem. A better primary source for each would be an improvement.
