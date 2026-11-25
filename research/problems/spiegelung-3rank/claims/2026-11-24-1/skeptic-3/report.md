# Independent review of claim packet 2026-11-24-1 (Dutarte / Scholz 3-rank law)

I wrote all code from scratch in /tmp/work/sp3. I used only /tmp/work/pk and this directory, and no claimant code. Everything ran on one core, with peak memory around 1.1 GB.

## Verdict: REJECT

Everything reproduces exactly. The claim does not pass the HONEST question cleanly, and novelty cannot be fully confirmed.

## 1. REPRODUCED? Yes: all 61 rows match exactly, and so do the test and the constants.

### Method
I counted GL2(Z)-classes of binary cubic forms (Delone-Faddeev correspondence). For a fundamental discriminant D, the number of cubic fields of discriminant D is (3^rk3 - 1)/2.

- **D > 0:** Forms are reduced by the Hessian (P,Q,R) = (b^2-3ac, bc-9ad, c^2-3bd), with 0 <= Q <= P <= R and a >= 1. Boundary ties go to the lexicographically largest image under Stab(H).
  - Loop bounds come from 4P^3 - 27Da^2 = G(1,0)^2 and from P <= sqrt(D). The coefficient b is a root of P b^2 - 3aQ b + 9a^2R - P^2 = 0.
- **D < 0:** Forms are reduced by the complex root tau: 0 <= ad-bc <= (a+b)^2+ac and d^2-a^2+ac-bd >= 0, with a >= 1.
  - I derived these from the symmetric functions of the roots.
  - An irreducible form is never on the boundary. The reducible ring's representative has a = 0, so it is never counted.
- **Mirror:** -3d if 3 does not divide d, otherwise -d/3. Negative discriminants are counted in segments up to 3X.
- **Built-in checks, applied to every fundamental d:**
  - every count is of the form (3^r-1)/2;
  - Scholz's theorem holds: r'-r in {0,1}.

  The run aborts on any violation. None occurred, to 10^9 or to 10^10.

### Validation
- **Identities** (check_identities.py): Hessian equivariance, the syzygy, 3aR-bQ+cP = 0 and 4PR-Q^2 = 3D hold on 2000 random forms.
- **Reduction conditions:** the integer tau-conditions agree with numerical roots on 13,979 random forms. The 13 apparent mismatches are exact boundary cases.
- **Loop bounds against brute force** (`cubicrank brute`): the loop counts match a brute-force box search D by D, for |D| < 3000 and for |D| < 20000.
- **Comparison with class groups computed directly** (classgroup.py): I used Gauss composition, with cycles of reduced indefinite forms for real fields (narrow and wide class groups have the same 3-rank).
  - r and r' agree for all 9,118 fundamental d <= 30000.
  - They also agree for all 611 fundamental d in [10^6, 10^6+2000).
  - That is 0 mismatches.
- **Known first occurrences:** my code finds 32009 as the first real 3-rank 2 and 39345017 as the first real 3-rank 3. It also finds d = 1482568, whose mirror -4447704 has 3-rank 3. All three match the literature.

### Result
- **To 10^9:** mytable.csv equals table.csv in all 61 rows (X = 10^3 ... 10^9) and all 8 columns. There are no differing rows.
- **Extended to 10^10** (mytable10.csv): 3,039,635,379 discriminants, of which 897,388,600 have r' = r+1. Both match the numbers disclosed in (c) exactly.
- **Timings:** 225 CPU-seconds to 10^9; 4,633 CPU-seconds to 10^10; a few minutes for the Python validation.

### The test in (b), re-implemented in fit_test.py
I used 30 bins, var = p^(1-p^)/n with p^ = (s+1/2)/(n+1), a weighted least-squares fit of p_inf + c x^(-1/6) at the geometric midpoints, and unscaled standard errors from (A'WA)^-1.

| quantity | my p_inf +- SE | claimed | my chi2/28 | claimed | verdict |
|---|---|---|---|---|---|
| all | 0.297772 +- 0.000139 | same | 13.10 | 13.1 | CONSISTENT z=+0.87 |
| r=0 | 0.333524 +- 0.000155 | same | 15.19 | 15.2 | CONSISTENT z=+1.23 |
| r=1 | 0.111633 +- 0.000240 | same | 14.05 | 14.1 | CONSISTENT z=+2.18 |
| r=2 | 0.036982 +- 0.001111 | same | 15.22 | 15.2 | CONSISTENT z=-0.05 |

On my own 10^10 table (38 dof):

| quantity | p_inf +- SE | verdict |
|---|---|---|
| all | 0.297699 +- 0.000042 | CONSISTENT |
| r=0 | 0.333398 +- 0.000047 | CONSISTENT |
| r=1 | 0.111415 +- 0.000073 | INCONSISTENT, z=+4.18 |
| r=2 | 0.037656 +- 0.000351 | CONSISTENT |

These match the numbers in (c) exactly.

### The constants
- **Fouvry-Klueners 2010** (msp.org): Conjecture 1.1 and equations (2), (5) and (11) give 3^-(r+1) and 0.29765117. The quote about Dutarte and "close, but not too close" is accurate.
- **Belabas** (mean3-99, Conjecture 3.2; r3.pdf, Conjecture 4.3) states the same law as P(defect 0 | r) = 3^-(r+1).
- **My own check:** the sum over r of Cohen-Lenstra P_real(r) times 3^-(r+1) is 0.297651172917, which confirms the constant.

## 2. NOVEL? Probably, but I could not confirm it.

I found no published table or numerical test of the joint (r, r') law at a comparable range.

- **FK 2010:** no data printed.
- **Dutarte 1984** (Publ. Math. Besancon, opened): his only test is a small statistical test of whether fundamental units are 3-primary. There are no 3-rank tables.
- **Belabas, mean-3-rank paper:** cubic-field counts to 10^11, but no data on this law.
- **Belabas, large 3-rank paper (2004):** a single remark that 6 of 1,618 real 3-rank-4 fields have mirror rank 5, against Dutarte's prediction of about 6.7.
- **Belabas, thesis:** the opened portion has no such table.
- **Malle 2010, Jacobson-Scheidler (function fields), Dalla Torre (thesis), Hough, arXiv 2512.20023, arXiv 2301.00791:** none has data on this law.
- **OEIS A250236:** a list of discriminants, not statistics.
- **Wikipedia "Reflection theorem":** nothing relevant.
- **Works citing FK 2010** (OpenAlex, 6 listed) and Lee 2002 (5): all are about 4-ranks or unrelated topics.

**Queries:**
1. Dutarte conjecture Scholz reflection 3-rank r' = r+1 probability 3^-(r+1) numerical
2. Fouvry Klüners "On the Spiegelungssatz for the 4-rank" Algebra Number Theory 2010
3. 0.29765117 Scholz reflection
4. Belabas 3-rank real quadratic field imaginary mirror field statistics Scholz reflection theorem cubic fields table
5. "Dutarte" "Spiegelungssatz" OR "reflection" 3-rank quadratic heuristic Cohen-Lenstra
6. mathoverflow Scholz reflection theorem 3-rank equal or differ by one proportion of real quadratic fields
7. Yoonjin Lee "Cohen-Lenstra heuristics and the Spiegelungssatz" number fields numerical data
8. "Scholz defect" OR "reflection defect" 3-rank numerical tables discriminants 10^9 OR 10^10 OR 10^11
9. arxiv joint distribution 3-rank class group Q(sqrt d) Q(sqrt -3d) computation Cohen-Lenstra verification
10. Dutarte 1984 Publications Mathématiques de Besançon 3-rang corps quadratiques réflexion Scholz
11. OEIS 3-rank class group real quadratic field mirror field Q(sqrt(-3d))
12. math.stackexchange Scholz reflection theorem 3-rank Q(sqrt d) Q(sqrt -3d) how often
13. "A Constructive Approach to Spiegelung Relations between 3-Ranks of Absolute Ideal Class Groups"
14. Daniel C. Mayer statistics 3-class groups real quadratic fields discriminant 10^7 mirror imaginary Scholz type table
15. Cohen-Lenstra heuristics Wikipedia 3-rank real quadratic fields numerical evidence (site en.wikipedia.org)
16. "Spiegelungssatz" 3-rank numerical experiment proportion "r+1" real quadratic discriminants up to arXiv 2024 2025 2026 (extended mode)
17. OpenAlex: search "Spiegelungssatz for the 4-rank"; cites:W2122438061 (FK 2010); cites:W2058452165 (Lee 2002)
18. Site-restricted searches on mathoverflow.net, math.stackexchange.com and oeis.org: the proxy rejected them (HTTP 400)

**Could not open:**
- Google Scholar (robots).
- MathOverflow and Math StackExchange (site blocked).
- OEIS search (robots).
- The Wikipedia Cohen-Lenstra page (not found).
- Semantic Scholar and OpenAlex through curl (proxy 403). OpenAlex worked through WebFetch.
- The Mayer 2000 Springer chapter, and paywalled full texts.

**How this bears on novelty:** I have no citation list for Dutarte 1984, and the Q&A sites went unchecked. Belabas's tables to 10^11 contain this data implicitly, and FK say they ran experiments. A comparable unpublished or obscure computation is plausible, so (d) is not a clear yes.

## 3. HONEST? Not a clear yes.

The numbers are correct. My concerns are about framing and weight.

**1. The stopping point.**
- The frozen definition allows any X_max >= 10^9. The claimant had the exact table to 10^10, where the same pre-set test gives r=1 INCONSISTENT (z=4.18). I reproduced this.
- Presenting the passing X_max = 10^9 as the result picks a stopping point after the outcome was seen. Only the disclosure in (c) keeps it from being hidden.
- (c) is candid and accurate. But labelling it "not part of what is claimed" moves a failing result out of the claim; it does not mean the claim survives it.

**2. The test is weaker than it looks.**
- The chi-squares are far too small for 28 dof: P(chi2 <= observed) is 0.008, 0.024, 0.013 and 0.024 for the four quantities. The 10^10 fits show the same, with 15-24 on 38 dof.
- So the binomial standard errors are about sqrt(2) too large.
- With rescaled standard errors, r=1 at 10^9 already gives z = 3.07, which would be INCONSISTENT.
- The VOID rule only catches chi2 that is too large, not too small.

**3. The model is unstable.**
- The fitted p_inf for r=1 falls as the start of the fit window rises: 0.11166 from 10^5, 0.11163 from 10^6, 0.11155 from 10^7, 0.11143 from 10^8, then 0.111415 from 10^6 to 10^10.
- Each fit extrapolates over a gap of 25-50 standard errors.
- So "the x^(-1/6) term accounts for the gap" overstates what the data show.

**4. What was actually shown.** The data neither confirm nor refute the conjecture. The one-term model is already inadequate for r=1 by 10^10.

## Files (all in /tmp/work/sp3)
- cubicrank.c and cubicrank10.c
- check_identities.py, classgroup.py, aggregate.py, fit_test.py, extra_stats.py
- mytable.csv and mytable10.csv
- cg_*/cf_* validation outputs
- t9/ and t10/ (segment files and logs)
- verdict.txt
