# Skeptic review of claim packet 2026-11-24-1 (Scholz reflection / Dutarte's law for 3-ranks)

Verdict: SIGN-OFF (with caveats recorded in section 3). All code here was written from scratch in this directory;
only /tmp/work/pk/claim.md and table.csv were read.

## 1. REPRODUCED? Yes

### (i) Table rows
**All 61 rows of table.csv (X = 10^3 ... 10^9, k = 30..90) were recomputed and match exactly, every column.**
(`diff table.csv out1e9.csv` is empty.) No row differs.

Method A (`cub.c`, all 61 rows). Count cubic fields: for a fundamental discriminant D the number of cubic fields of
discriminant D is (3^r - 1)/2 (Hasse), and cubic rings correspond to GL2(Z)-classes of integral binary cubic forms
(Delone-Faddeev); a ring of fundamental discriminant is maximal, so it is enough to count irreducible classes.
I enumerate forms whose quadratic covariant is weakly reduced (Hessian |Q|<=P<=R for D>0; the Mathews covariant,
with inequalities I re-derived from the real root, for D<0), with loop bounds I derived, and select one form per class
by explicitly closing each boundary form's orbit under the edge identifications and keeping the lexicographic maximum
(no reliance on remembered boundary conventions). Irreducibility is tested exactly (roots mod 2..13, then rational
root test). Real forms to 10^9, complex forms to 3*10^9. Built-in checks, all passed with zero anomalies over all
303,963,559 discriminants: every per-discriminant count lies in {0,1,4,13,40,121} (i.e. is of the form (3^r-1)/2),
and r' - r is in {0,1} for every d (Scholz's theorem). Timing: 9 min 26 s, one core, 1.3 GB.

Method B (`qf.c`, rows up to X = 10^6, k = 30..60, an unrelated method). Direct class groups by binary quadratic
forms: for each fundamental d <= 10^6 and its mirror, count classes g with g^3 = 1 (definite forms for the mirror;
cycles of reduced indefinite forms, narrow class group, for d). Validated on known values: h(-23)=3, h(-47)=5,
h(-71)=7, h(-163)=1, h(-3299)=27 with 3-rank 2, -3896 and -4027 rank 2, -3321607 rank 3, 229 and 257 h=3,
32009 rank 2 (smallest real), narrow h(12)=2, h(60)=4, h(136)=4, h(145)=4, h(328)=4.
Result: the (r, r') pair agrees with method A **for every one of the 303,957 fundamental d <= 10^6** (file compare of
`qf_out.txt` and `dump1e6.txt`), and the totals equal the table row for 10^6 (182209, 83674, 34782, 3131, 161).
Timing: 4 min 55 s.

Headline figures at 10^9 confirmed: 303,963,559 discriminants; 89,388,474 with r'=r+1; r=0: 258,536,250 / 84,775,065;
r=1: 44,945,361 / 4,601,647; r=2: 481,756 / 11,762; r=3: 192 / 0.

### (ii) The statistical test of (b) (`fit.py`, output in `fit_out.txt`)
30 bins between checkpoints k=60..90, binomial variance at (s+1/2)/(n+1), WLS fit of p_inf + c x^(-1/6) at geometric
midpoints, 28 d.o.f.

| quantity | my p_inf +- se | claimed | conjecture | z | my chi2 | claimed chi2 | verdict |
|---|---|---|---|---|---|---|---|
| aggregate | 0.297772 +- 0.000139 | 0.297772 +- 0.000139 | 0.29765117 | +0.87 | 13.1 | 13.1 | CONSISTENT |
| r=0 | 0.333524 +- 0.000155 | 0.333524 +- 0.000155 | 1/3 | +1.23 | 15.2 | 15.2 | CONSISTENT |
| r=1 | 0.111633 +- 0.000240 | 0.111633 +- 0.000240 | 1/9 | +2.18 | 14.1 | 14.1 | CONSISTENT |
| r=2 | 0.036982 +- 0.001111 | 0.036982 +- 0.001111 | 1/27 | -0.05 | 15.2 | 15.2 | CONSISTENT |

Raw proportions at 10^9: 0.294076, 0.327904, 0.102383, 0.024415 - as claimed. Claim (b) reproduces to every digit.

### (iii) Constants
Fouvry-Klueners (ANT 4 (2010), msp.org PDF opened): Conjecture 1.1 / eq. (2),(5) give 3^-(r+1) for positive D;
eq. (11) gives 0.29765117...; the sentences "It has been tested on a computer by Dutarte [1984, 4.2]" and "We ran
similar experiments and the constants are close, but not too close" are there, with no data. I recomputed the constant
from the Cohen-Lenstra real-quadratic 3-rank law, sum_r 3^-(r+1) * 3^(-r(r+1)) eta_inf/(eta_r eta_(r+1)) =
0.297651172917. Matches. (Side note: Dutarte's own section 4.2, as far as the extracted text shows, tested only "one
third of fundamental units are 3-primary" on two samples of 1000 discriminants.)

### Not reproduced
The 10^10 figures in disclosure (c): rows are not in the packet and recomputing them was outside my memory/time budget.
I confirmed only that the number of positive fundamental discriminants <= 10^10 is 3,039,635,379 (`fcount.c`, 32 s).
The count 897,388,600 and the four 10^10 fits are unverified. They are not part of what is claimed as verified.

## 2. NOVEL? Yes, as far as I could search
I found no published table or numerical test of this law at anything like this range. Closest prior work:
- Belabas, "On quadratic fields with large 3-rank" (Math. Comp. 2004): states Dutarte's conjecture and checks one
  consequence on 1618 real fields of 3-rank 4 (6 mirrors of rank 5 against 6.7 predicted). A point check, not a table.
- Belabas, "On the mean 3-rank of quadratic fields" (1999) and "Variations sur un theme de Davenport et Heilbronn"
  (2003): state the conjecture and prove an h3-weighted equidistribution of the Scholz defect; no numerical tables;
  cubic field counts to 10^11 are counts of fields only.
- Fouvry-Klueners 2010 and the 2009 Oberwolfach abstract: no data.
- Dutarte 1984: 2 x 1000 random discriminants, a different statistic.
- OEIS A250236 (d with both 3-class groups of type (3), 40 terms to 2993): not a count table.
- arXiv 2512.20023, 1605.04371, 2301.00791, 0912.1427, Wikipedia "Reflection theorem": nothing on this.

Queries run (WebSearch):
1. Dutarte conjecture Scholz reflection 3-rank real quadratic field mirror field probability numerical data table
2. Fouvry Klueners "On the Spiegelungssatz for the 4-rank" Dutarte 0.29765
3. Dutarte "Compatibilite avec le Spiegelungssatz de probabilites conjecturales sur le 3-rang du groupe des classes"
4. Scholz reflection principle statistics 3-rank quadratic fields computation discriminants up to 10^9 "Spiegelungssatz" Cohen-Lenstra numerical evidence
5. mathoverflow Scholz reflection theorem distribution 3-rank Q(sqrt d) Q(sqrt(-3d)) proportion equal ranks heuristics data
6. math.stackexchange Scholz reflection 3-rank real quadratic mirror imaginary quadratic how often ranks differ probability 1/3
7. OEIS fundamental discriminants 3-rank class group real quadratic field Scholz mirror field sequence
8. "Dutarte" conjecture 3-rank "Spiegelungssatz" OR "reflection" numerical verification cubic fields tabulation Belabas Cohen "escalatory" "non-escalatory" proportion
9. Gras Scholz reflection 3-rank quadratic fields "Dutarte" densities numerical PARI statistics "3-primary" fundamental unit proportion
10. arXiv "Scholz" "reflection" 3-torsion class groups quadratic fields joint distribution "Q(\sqrt{-3d})" Cohen-Lenstra moments Bhargava Varma OR Klagsbrun OR "Lemke Oliver" secondary term
11. papers citing Fouvry Klueners "Spiegelungssatz for the 4-rank" 3-rank Dutarte conjecture computations "Scholz defect" statistics (extended mode)
12. "Dutarte" "3-rank" OR "3-rang" quadratic "mirror" OR "miroir" OR "reflection" conjecture tested computed "10^9" OR "10^8" OR "10^10" OR "10^11" discriminants table
13. site:mathoverflow.net Scholz reflection 3-rank quadratic field statistics "Dutarte" OR "how often" OR "density" equality
14. site:math.stackexchange.com Scholz reflection theorem 3-rank Q(sqrt(-3d)) class group density
15. site:oeis.org Scholz 3-rank real quadratic imaginary "-3d" OR "mirror" OR "reflection" discriminants class group
Pages opened: msp.org FK paper; arXiv 2512.20023, 1605.04371, 2301.00791, 0912.1427 (abstracts); Belabas mean3-99.pdf,
r3.pdf, stnp.pdf; Dutarte (pmb.centre-mersenne.org PDF); Oberwolfach Report 33/2009; Leiden thesis page; Wikipedia
"Reflection theorem"; OEIS A250236.

Could not open / limits: Google Scholar (robots-disallowed), so there is no true forward-citation list for
Fouvry-Klueners or Dutarte - query 11 is only a substitute. The site-restricted MathOverflow/MSE/OEIS queries returned
no on-site hits about this law (they fell back to general results). The Dalla Torre thesis (Leiden 2019) full text
and the bodies of the arXiv papers were not read beyond abstracts; PDFs were read through a summarising fetcher, so a
table buried in one could be missed. Unpublished data (the Fouvry-Klueners experiments, LMFDB-derived counts) may
exist. Novelty is therefore "nothing found", not "proved absent".

## 3. HONEST? Yes, with caveats that must travel with the claim
The frozen definition is met as written and was not narrowed: exact table to X_max = 10^9 (item 1), the pre-set test
applied with pre-set exponent, bins and thresholds (item 2), no comparable publication found (item 3). The claim says
explicitly that it is a numerical test, not a confirmation, and (c) volunteers a result that goes against it. That is
honest handling. The points below limit how much (b) can carry:

1. **Choice of X_max.** The definition allows any X_max >= 10^9. The claimant holds a 10^10 table on which the same
   pre-set rule returns INCONSISTENT for r = 1 (4.2 se), and reports the headline at 10^9, the smallest permitted value.
   This is disclosed plainly, so the reader is not misled, but "All four: CONSISTENT" should never be quoted without
   (c). On the claimant's best data the pre-set verdict for r = 1 is INCONSISTENT with the one-term model.
2. **The verdict hinges on the exponent, and the data cannot check the exponent.** Re-running the same test with other
   exponents (`fit_out.txt`): at -0.16, r=1 is z=+3.9 (INCONSISTENT); at -0.18 all four pass; at -1/5 the aggregate,
   r=0 and r=1 are 5 to 7 se below the conjecture; at -1/8 they are 8 to 13 se above. Chi-square stays between 13 and
   29 on 28 d.o.f. for every exponent from -0.08 to -0.28, so the VOID rule never fires. The test therefore examines
   the joint hypothesis "Dutarte + exactly one x^(-1/6) term"; the quoted standard errors carry no model uncertainty.
   The sentence "the x^(-1/6) term accounts for the gap" is true only in that sense.
3. **Chi-squares are low** (13.1 to 15.2 on 28 d.o.f.; a chi-square of 13.1 or less has probability under 1%). The
   binomial variances look too large for these counts, which makes the 3-se band generous. Scaling the errors by
   sqrt(chi2/dof) moves r=1 at 10^9 from 2.18 to about 3.1 se. So r=1 is already marginal at 10^9, in line with (c).
4. Trend: the r=1 excess grows as the range extends (z = +0.85, +1.37, +2.18 for X_max = 10^8, 10^8.5, 10^9), again in
   line with the 10^10 failure. Start-of-range choices (10^4 to 10^8) do not change any verdict.
5. The 10^10 rows are withheld, so (c) is unverifiable; it is correctly labelled as not part of the verified claim.

None of these contradicts a statement the claim actually makes. The claim as limited in (c) - exact table to 10^9,
pre-set test returns four CONSISTENT at 10^9, not claimed beyond - stands.

## Files
cub.c (method A), out1e6.csv / out1e7.csv / out1e8.csv / out1e9.csv, log1e8.txt, log1e9.txt, dump1e6.txt;
qf.c (method B), qf_out.txt; fit.py, fit_out.txt; fcount.c; verdict.txt.

## Timings (one core)
cub 10^6: 0.2 s; 10^7: 2.2 s; 10^9: 9 min 26 s (an earlier 10^8 run with a slow fundamental-discriminant test took
2 min 19 s and also matched). qf to 3*10^5: 31 s; to 10^6: 4 min 55 s. fcount 10^10: 32 s. No background process left.
