# 3-rank reflection law for (Q(sqrt d), Q(sqrt(-3d))): numerical test (ledger row UQ-20261028-02)

## Why tractable now (2026-11-24 08:53 UTC run)
Scholz's reflection theorem: for a positive fundamental discriminant d with r = r_3(Q(sqrt d)) and mirror field
Q(sqrt(-3d)), r_3(mirror) is r or r + 1. Dutarte's heuristic (1984), restated as Fouvry-Klueners Conjecture 1.1 (ANT 4
(2010) 493-508), predicts P(r' = r + 1 | r) = 3^-(r+1) and an aggregate proportion 0.29765117...; the ledger row records
that Fouvry-Klueners call the match of their own numerics "close, but not too close" and that the law is unproved.
3-ranks need no class groups: the number of cubic fields of fundamental discriminant D is (3^r - 1)/2, and Belabas's
reduced-form enumeration lists all of them in about 10 s for |D| <= 3 * 10^8 on this machine. So both ranks for every
d <= 10^9 or more are a few minutes of compute, far past what a 1984 or 2010 table is likely to have covered. The per-G
limb of the row (dependence on the group beyond its rank) needs class group structures, i.e. PARI or similar; installing a
PARI binding was not permitted in this run's environment, so that limb is NOT attempted.

## Frozen definition of "solved" (written before any run beyond 10^8; the 10^8 table was seen first)
The aggregate limb is solved when:
1. there is an exact table of counts n(r, e; X), the number of positive fundamental d <= X with r_3(d) = r and
   r_3(mirror) - r = e, for X up to X_max >= 10^9, with every count of cubic fields per discriminant of the form
   (3^r - 1)/2 and no violation of Scholz's theorem (both are checked on every discriminant);
2. the pre-set convergence test is applied: split (10^6, X_max] into disjoint bins [10^(k/10), 10^((k+1)/10)); for each
   bin the proportion with e = 1 (aggregate, and conditional on r = 0, 1, 2) with binomial variance; weighted least squares
   fit p(x) = p_inf + c x^(-1/6) at the bins' geometric midpoints (the exponent of the known secondary term in counts of
   3-torsion, Taniguchi-Thorne / Bhargava-Shankar-Tsimerman). Verdict for each of the four quantities: CONSISTENT if the
   predicted limit (0.29765117, 1/3, 1/9, 1/27) lies within 3 standard errors of the fitted p_inf, otherwise INCONSISTENT
   WITH THIS MODEL; the fit's chi-square per degree of freedom is reported and a value above 2 voids the verdict (the
   one-term model is then inadequate and nothing is concluded);
3. the table and verdicts are not already published to a comparable range.
A table alone, or a verdict from a different model, is a sub-result. This is a numerical test, never a proof of the law.

## Status check (2026-11-24, from the papers themselves)
- Fouvry-Klueners 2010: Conjecture 1.1 / eq. (2), (5) average over ALL positive fundamental discriminants (3 | D included;
  the mirror is the field Q(sqrt(-3D)), discriminant -D/3 when 3 | D) and condition on the real field's rank; eq. (11) gives
  0.29765117... (recomputed here from the formula). They print NO numerical data ("We ran similar experiments and the
  constants are close, but not too close").
- Dutarte 1984 (Publ. Math. Besancon, Expose 4): his test is two random samples of 1000 discriminants, chi-square at 5%.
- Belabas 2004 (Math. Comp. 73): only one count against the law (6 observed, 6.7 predicted, at r = 4).
- No later table or test found. Sawin-Wood arXiv:2301.00791 sections 9, 11, 12 could not be read (fetch truncation), so
  whether their module-level conjecture already contains Dutarte's law is unresolved; that concerns the per-G limb.

## Approaches (08:53 run)
1. Routed per-G limb via class groups: needs PARI; installing a binding was not permitted. Not attempted.
2. `code/cubic.c`: 3-ranks from counts of cubic fields (reduced binary cubic forms, Belabas 1997), both signs. Checks:
   real cubic discriminants below 1000 and the first rank-2 and rank-3 fields match the literature (229, ..., 993; 32009,
   -3299, 39345017, -3321607; four imaginary rank-4 fields below 3 * 10^9); widening every loop bound by 1.6 changes
   nothing at 10^6; every count is of the form (3^r - 1)/2; Scholz's theorem holds for every pair.
3. `code/stats.c` + `code/fit.py`: checkpoint table and the pre-set test. X = 10^9: 303,963,559 pairs, 112 s
   (`table_1e9.csv`). All four quantities CONSISTENT (aggregate 0.297772 +- 0.000139; r = 0: 0.333524 +- 0.000155;
   r = 1: 0.111633 +- 0.000240; r = 2: 0.036982 +- 0.001111).
   DEVIATION FROM THE FROZEN TEXT: a bin with zero successes (r = 2, small x) has binomial variance 0 and broke the first
   fit; the variance is now evaluated at (s + 1/2)/(n + 1). Found and fixed after seeing the r = 2 output; the other three
   fits do not change at the printed precision.
4. `code/cubicx.c`, memory-compact variant (4 bits per candidate discriminant), identical tables at 10^8 and 10^9.
   X = 10^10: 3,039,635,379 pairs, 0 bad counts, 0 Scholz violations, about 20 min (`table_1e10.csv`). Pre-set test:
   aggregate 0.297699 +- 0.000042 (z +1.1), r = 0: 0.333398 +- 0.000047 (z +1.4), r = 2: 0.037656 +- 0.000351 (z +1.8),
   all CONSISTENT; **r = 1: 0.111415 +- 0.000073, z = +4.2: INCONSISTENT WITH THIS MODEL.**
5. Exploratory, post hoc (not part of the frozen test): the r = 1 excess shrinks as the fit starts later (z = +2.8 from
   10^8, +1.4 from 10^9), and a two-term model p_inf + c x^(-1/6) + e x^(-1/3) puts all four limits within 0.25 standard
   errors of the conjecture (r = 1: 0.111154 +- 0.000198). Reading: the one-term model is too crude at this precision; the
   data do not point away from Dutarte's values. This reading is a hypothesis, not a verdict.

## Skeptic gate, claim 2026-11-24-1 (table to 10^9 plus the pre-set test)

1 of 3: the claim does not count as verified. Records in `claims/2026-11-24-1/skeptic-{1,2,3}/`.

- Skeptic 1 (default model): SIGN-OFF. Own cubic-form count reproduced all 61 rows to 10^9; a second method (class groups
  from quadratic forms) agreed for every d <= 10^6; test values reproduced to every digit. Caveats: the verdict depends on
  the fixed exponent -1/6, chi-squares are low, the r = 1 excess grows with range.
- Skeptic 2 (Sonnet): REJECT. Own class-group code reproduced the 36 rows to 3.16e6 only (method too slow beyond); test
  reproduced; rejects because the CONSISTENT verdict holds only for exponents near 1/6 and novelty could not be confirmed.
- Skeptic 3 (Opus): REJECT. Own cubic-form count reproduced all 61 rows AND the 10^10 table (3,039,635,379 pairs,
  897,388,600 with r' = r + 1), test values at both ranges. Rejects on honesty: reporting 10^9 when the same test fails
  for r = 1 at 10^10 is a stopping point chosen after seeing the outcome; chi-squares of 13 to 15 on 28 dof (p about 0.01
  to 0.02) mean the binomial errors are about sqrt(2) too large, and with rescaled errors r = 1 is already at z = 3.07 at
  10^9; the fitted limit drifts as the fit window moves.

What stands after the gate:
- The exact table is solid: three independent programs agree to 10^9 (one only to 3.16e6), two agree to 10^10. No count
  outside (3^r - 1)/2 and no Scholz violation among 3.04 billion pairs.
- The statistical verdict does NOT stand. The honest result of the pre-set test is the one at the largest range: at 10^10
  the one-term x^(-1/6) model is rejected for r = 1 (z = +4.2). The data neither confirm nor refute the conjectured
  limits; they show that the approach to the limit is not a single x^(-1/6) term with these error bars.
- Novelty: no skeptic found a comparable published table; none could open Google Scholar or the Belabas 10^11 tables.

---

# Run of 2026-11-24 20:53 UTC: an out-of-sample test

## Why tractable now
The morning run left an exact table to 10^10 and a failed test design: the limit was extrapolated with one correction term
whose exponent the data could not check, and the verdict changed with the range. The reviewers' objections point at a
design that needs no extrapolation: fix a model on the data already seen, then check its PREDICTION on discriminants not
yet counted. The enumeration is fast enough to add half a decade (to 10^10.5) in about an hour on this machine, and a
reviewer can rebuild it in a few CPU-hours. The second correction term has a source in theory: the best proven error term
in the Davenport-Heilbronn count with its secondary term is O(X^(2/3 + eps)) (Bhargava, Taniguchi, Thorne, "Improved error
estimates for the Davenport-Heilbronn theorems"), i.e. relative size x^(-1/3) after the x^(-1/6) term of Roberts'
conjecture. (To be checked against the paper this run; the model below is frozen regardless.)

## Frozen definition of "solved" for this run (written before any discriminant above 10^10 is counted)
Problem: same law as the morning run (P(r' = r + 1 | r) = 3^-(r+1), aggregate 0.29765117). This run's question:
does the conjectured limit, with two correction terms fitted below 10^10, predict the new range (10^10, 10^10.5]?

Solved means all of:
(a) the exact table n(r, e; X) at the checkpoints 10^(k/10), extended to X_max = round(10^10.5) = 31,622,776,602 and no
    further this run; every cubic-field count of the form (3^r - 1)/2; no Scholz violation; rows up to 10^10 identical
    to `table_1e10.csv`;
(b) the prediction test, for each of four series (aggregate, r = 0, r = 1, r = 2): model
    M2: p(x) = p_conj + c1 x^(-1/6) + c2 x^(-1/3), p_conj FIXED at the conjectured limit, c1 and c2 fitted by weighted
    least squares (weights from the add-half binomial variance, as in `fit.py`) on the 40 bins between checkpoints in
    (10^6, 10^10], x = geometric bin midpoint. Prediction for the 5 new bins in (10^10, 10^10.5]. Statistic
    T = r^T (V + J S J^T)^-1 r with r = observed minus predicted proportions, V the diagonal binomial variances of the
    new bins (at the predicted p), S the covariance of (c1, c2), J the design rows of the new bins. Under the model T is
    chi-square with 5 degrees of freedom. HELD if the p-value is > 0.01, FAILED otherwise. Reported as it falls.
    Comparator, same procedure: M1 with c2 = 0 (the morning model with the limit fixed).
    Sensitivity, reported beside it and fixed now: the same T with all variances divided by 2 (the reviewers found the
    binomial errors about sqrt 2 too large); and the largest shift delta of p_conj for which M2 with p_conj + delta
    still gives HELD (how much the test can tell).
(c) not already published (same status check as the morning).
"HELD" is a statement about conjecture and model jointly on this range. It is not a confirmation of the conjecture and
will not be called one. A sub-result (table only, or test only) is labelled as such.

## Results of the 20:53 run
- Approach 1, windowed counter (`code/cubicw.c`, `code/runw.sh`, `code/statw.c`): cuts the innermost loop to the d-range
  whose discriminant falls in a window, so any range runs in resumable pieces of bounded memory. Identical to
  `table_1e9.csv` at 10^9; its table to 10^10.5 has the 10^10 table as an exact prefix. 16 windows, about 40 minutes on
  4 cores. `table_1e10.5.csv`, `log_1e10.5.txt`: 9,612,171,555 pairs, 2,841,877,607 with e = 1, 0 bad counts, 0 Scholz
  violations, no r = 4; imaginary rank histogram to 3 X_max: 16309497798, 11999082317, 526145650, 1788321, 370.
- Approach 2, theory for the second term: the arXiv listing of Bhargava-Taniguchi-Thorne (2107.12819) gives the error
  O(X^(2/3 + eps)) after the X^(5/6) term; paper not opened beyond the abstract. This motivates x^(-1/3) but proves
  nothing about the conditional proportions.
- Approach 3, backtest on old data (`backtest_fit1e9_predict1e10.txt`): fit to 10^9, predict (10^9, 10^10]: M2 held for
  all four; M1 borderline for r = 1 (p = 0.011). Not out of sample (all of it had been seen).
- Approach 4, the frozen out-of-sample test (`code/predict.py`, `predict_1e10.5.txt`): M2 HELD for all four series
  (p = 0.917, 0.650, 0.514, 0.055); M1 FAILED for r = 1 (T = 28.8). Shift intervals about +-3e-4 for aggregate, r = 0,
  r = 1 and +-1e-3 for r = 2.
- Approach 5, sensitivity to the variance model: with variances halved r = 2 FAILS (p = 0.0006), driven by one bin
  (standardized residual -2.9 at 1.4e10). The fit chi-squares (15 to 22 on 38 dof) again say the binomial errors are
  too large, so the calibrated reading for r = 2 is "failed".
- Approach 6, the morning's one-term free-limit fit on the longer table (`code/fit.py`): r = 1 now 6.5 se off. Dead.

## Skeptic gate, claim 2026-11-24-2: 0 of 3
- Skeptic 1 (default model): REJECT. Rebuilt all 76 rows (byte-identical), reproduced the test. Rejects on novelty as
  worded: Belabas, Math. Comp. 73 (2004), section 5.2 tests the law for r = 4 to 1.6e13 and the packet did not cite it;
  also Kraft-Washington 2007 unread. Says it would sign off if (d) were restricted and those cited.
- Skeptic 2 (Sonnet): REJECT. Rebuilt rows to 10^6 only (its method is quadratic); test reproduced; same novelty point;
  test too weak for the weight.
- Skeptic 3 (Opus): REJECT. Rebuilt all 76 rows, reproduced the test; same novelty point; pre-registration not
  verifiable from the packet; test weak.
The omission is ours: Belabas 2004 was in our own morning status check and was left out of this packet's problem
statement and of clause (c)/(d). Per RULE ZERO the result does not count and the same reviewers are not re-asked.
What stands: the exact table to 10^10.5, now rebuilt independently by three programs (two today, both whole).
