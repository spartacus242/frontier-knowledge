# Famous-questions backtest: results

## Re-run after the three rule fixes (2026-11-24)

**9 of 10 admitted, all nine at Tier: Moonshot. The bar was at least 6 admitted and at least 4 Moonshot, so the backtest now clears it on both counts.** The first run, described in full below, scored 4 of 10.

The maintainer approved the three proposed rule changes and the earlier dates on 2026-11-24. They are in LEDGER.md (Ambition requirement rule 5 dormant questions, rule 6 printed leg, new rule 7 re-development) and in runner `unasked-ledger-batch-sequential-v21.js`. Five questions were then run again, one per run, under those rules. The four admissions of the first run (M1, P2, B1, D2) and the C2 rejection were not re-run and stand as they were. The re-run records are in the folders named `<key>-rerun`; the first-run folders are untouched.

| Key | Question, as-of date | First run | Re-run | Tier | What changed the outcome |
|---|---|---|---|---|---|
| P1 | Graphene, **1998** (was 2004) | Rejected, asked | Provisional | Moonshot | The earlier date. No opened pre-1998 source measures a detached single layer. Weak: well-posedness 1/3, two contested presuppositions, and close printed neighbours on each half (Boehm et al. 1962; Gonzalez, Guinea and Vozmediano 1993). |
| B2 | Reprogramming to pluripotency, **2001** (was 2006) | Rejected, asked | Provisional (entry 12R) | Moonshot | The earlier date and rule 7. The headline was graded new; the first operational test was rejected at Gate 4 (attack 1) and marked for re-development; the second test survived two adversaries. |
| M2 | Monster group and modular functions, 1978 | Rejected, test | Provisional | Moonshot | Not rule 7. This time the developer wrote a stronger operational test and three adversaries left nothing Unresolved. Capped by a contested presupposition (the group's existence was conditional) and well-posedness 2/3. |
| D1 | Bacterial cause of gastritis and ulcer, 1983 | Rejected, asked | **Under-asked** | Moonshot | Rule 5, dormant route: a paper's subject in 1915-1916, and no adversary opened a 1958-1982 study designed to answer it. The dormancy showing is Partial: Palmer 1954, a possible printed negative, was opened by nobody. |
| C1 | Zero-knowledge proofs, 1983 | Rejected, disguise | Provisional | Moonshot | Rule 6 printed leg. All three adversaries reported their attack 2 against Yao 1982 as their own inference, which now counts as Partial. Capped by well-posedness 2/3. |

### How much weight the new score can bear

- **Three of the five gains are not independent evidence.** M2, D1 and C1 are the cases the fixes were written around. Passing them shows the fixes do what they were meant to do; it does not show the rules generalise. The two that are closer to a fair test are P1 and B2, where only the date changed, and both passed.
- **M2 passed for a different reason than the fix.** Rule 7 did not fire. A different developer draft produced a different test, which is run-to-run variation. The first-run rejection and this admission are one draw each.
- **Hindsight is visible in the developed tests.** The re-developed B2 test names a twelve-gene candidate list that includes Oct4, Sox2 and c-Myc, and the M2 test is close to the conjecture as later stated. An agent that knows the ending writes a better-aimed test than a 1978 or 2001 scientist could. The headline grades are less exposed to this than the operational tests.
- **P1 is the thinnest admission** (well-posedness 1/3, attack 5 Unresolved from two adversaries).
- **Rule 7 needed one repair during the run.** B2 was rejected at the third-adversary rejudge, after the re-development phase had already passed, so the mark was not acted on. The phase now runs last (commit 1de6d94e) and the B2 run was resumed from its saved results, so its first eight agents are the originals.
- **Still nothing Validated.** The Validated rule was made reachable in a separate change on the same day and was not in force for these runs.
- **Under-asked fired once in ten** (D1), having fired zero times in the first run.
- A usage limit stopped the D1 run after its Gate 0-3 record; it was resumed from that record about four hours later.

Final table across all ten: M1, M2, P1, P2, C1, B1, B2, D2 Provisional; D1 Under-asked; C2 Rejected (asked, Ambition 2).

---

## First run (2026-11-23 to 2026-11-24, runner v20)

Run 2026-11-23 to 2026-11-24 under the merged rules (LEDGER.md with the Ambition requirement and generation methods, runner `unasked-ledger-batch-sequential-v20.js`), one question per run, per `ledger/backtest/README.md`. Each question's entry, Gate 0-3 record and adversary logs are in the folder named for its key. Nothing here was appended to the ledger, the index, the rotation or the routed-problems file; the routing rows the judges drafted stay inside the BT entries.

## Result

**4 of 10 admitted, all four at Tier: Moonshot. The suggested bar was at least 6 admitted and at least 4 Moonshot, so the backtest misses the bar on admissions and meets it on tier.**

Every admission is Provisional. None reached Validated, and the Under-asked status was not awarded once.

| Key | Question, as-of date | Ranker / final Ambition | Status | Tier | Gate and ground |
|---|---|---|---|---|---|
| M1 | Zeta zeros and random-matrix statistics, 1972 | 3 / 3 | Provisional | Moonshot | Nothing Unresolved from three adversaries. Capped by well-posedness 2/3 and by unopened pre-1972 sources. |
| M2 | Monster group and modular functions, 1978 | 3 / 2 | Rejected | Standard | Gate 4, attack 1. The headline was graded new (nearest prior: Ogg 1975, on the group's order only). The operational test the developer wrote was trivially satisfiable; both adversaries built a module sequence meeting it. |
| P1 | Graphene, 2004 | 3 / 3 | Rejected | Standard | Gate 2, headline asked and open: isolating single sheets was a stated experimental aim (Lu et al. 1999; Shioyama 2001) and the carrier physics was printed theory. |
| P2 | Negative refractive index and sub-diffraction focusing, 2000 | 3 / 3 | Provisional | Moonshot | Nothing Unresolved from three adversaries. Veselago 1968 read in full: no sample and no diffraction-limit content. Capped by well-posedness 2/3. |
| C1 | Zero-knowledge proofs, 1983 | 3 / 3 | Rejected | Standard | Gate 4, attack 2 under rule 6: read as Yao 1982's non-disclosure question moved onto a one-sided predicate, with the record's transfer argument failing. One of two adversaries; the other returned Provisional. |
| C2 | Neural scaling laws, 2017 | 2 / 2 | Rejected | Standard | Gate 4, attack 2: headline asked (Amari and Murata 1993; Williams et al. 2015; Cohn and Tesauro 1990). One of three adversaries; two graded it Partial. |
| B1 | CRISPR repeats as defence, 2005 | 3 / 3 | Provisional | Moonshot | Novelty High on both layers. Capped by one Unresolved attack 5, contested presuppositions, and Mojica et al. 2000 unread by every reader. |
| B2 | Reprogramming to pluripotency, 2006 | 3 / 3 | Rejected | Standard | Gate 4, attack 2, both adversaries: the goal and the multi-factor route were in Yamanaka's own patent application (EP 1 403 366 A1, published 2004) and a funded programme's reports. |
| D1 | Bacterial cause of gastritis and ulcer, 1983 | 3 / 3 | Rejected | Standard | Gate 2, headline asked and open: Rosenow 1913 (full text), Celler and Thalhimer 1916 and Steer and Colin-Jones 1975 (abstracts). Not treated as Under-asked because it had been a paper's stated subject. |
| D2 | Checkpoint blockade against tumours, 1996 | 3 / 3 | Provisional | Moonshot | Nothing fatal from three adversaries. Capped by a contested presupposition (whether CTLA-4 inhibits) and an Unverified headline layer: the body of a 1995 review by the same lab could not be read. |

## Reading the six rejections

**Three look fair, and two of those are a flaw in how I chose the as-of dates.**

- **B2 and P1.** I set the date just before the famous paper. By then the question was already the stated aim of the people who went on to answer it. The right test date for a question is before it was first posed, not before it was first answered. These two runs show the pipeline correctly detecting an asked question; they say little about ambition.
- **C2.** The power-law form had been derived and partly measured decades earlier. The kill is from one adversary of three and the judge recorded it as partly procedural, so it is the least secure of the three.

**Three look like artefacts of the rules, and each points at a specific gap.**

- **M2: a new headline was lost because its operational test was badly written.** The pipeline has no way to keep a headline whose novelty stands while sending its test back for one more attempt. Gate 1 allows one reformulation, but only before the adversaries run.
- **D1: "asked, tried, and abandoned for decades" has no home.** Rule 5 excludes anything that was ever a paper's stated aim, so a question attacked in 1913 and effectively dropped is treated the same as one under active study. This is the case the Under-asked status was meant to catch, and the rule as written cannot.
- **C1: a rule 6 kill that rests on the adversaries' own inference.** The judge's entry says the kill "rests on something nobody has printed": a one-step specialisation of a theorem announced without proof. LEDGER.md already says a kill whose load-bearing leg is the adversary's own reasoning is Partial at best; under rule 6 the burden sits on the record, and the judge let that outweigh it.

Counting only the seven questions that were not already someone's stated programme at the as-of date, four were admitted and three were lost to the gaps above.

## What the run showed besides the count

- **The ambition ranker is not a rubber stamp.** It scored C2 a 2 with a stated reason, and an adversary's attack 6 lowered M2 from 3 to 2.
- **The contested-presupposition rule did its job.** B1 and D2 both carry contested premises and were capped at Provisional instead of rejected. Under the old attack 4 wording both were candidates for rejection.
- **Nothing reached Validated.** Every survivor was capped by well-posedness 2/3 or by a pre-as-of source no reader could open. This is the same unreachable-Validated problem already open from 2026-10-18.
- **Old print is hard to read from here.** Several grades rest on abstracts of pre-1980 papers, and the judges said so. Both the admissions and the "asked" kills are softer than they would be for modern questions.

## Proposed rule changes (applied 2026-11-24; see the re-run section above)

1. **Re-development.** When Gate 4 kills on attack 1 or on well-posedness, and the headline's novelty grade was not impeached, send the headline back to the developer once for a new operational test before rejecting.
2. **Dormant questions.** Extend Under-asked to a question that was once attacked and then left alone: no study designed to answer it in a stated window (say 25 years) before the search date, shown by the same follow-up search.
3. **Rule 6 kills need a printed leg.** A disguise kill whose transfer step is the adversary's own inference is Partial, in line with the existing standard for adversary reasoning.
4. **Re-run B2 and P1 with earlier dates** (for example 2003 and 1998), to test them as un-asked questions.

## Limits

- **Hindsight.** Every agent knew how each story ended, and each logged where that was hardest to set aside. Ambition scores are an upper bound.
- **One run per question.** Verdicts on this ledger have moved under re-verification before; three of the six rejections rest on a single adversary or a single unread source.
- **No comparison arm.** This measures the current rules only.
- **Post-as-of sources.** Agents logged the later sources they met as excluded in each record and adversary log; I did not independently audit those lists.
- **A container restart interrupted C1** after its Gate 0-3 record was written. The run was resumed from the saved results, so the record is the original and the adversaries and judge ran once.
