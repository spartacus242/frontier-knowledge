# Claim packet 2026-11-24-2

## Problem
For a positive fundamental discriminant d let r(d) be the 3-rank of the class group of Q(sqrt d) and r'(d) the 3-rank of
the class group of its mirror field Q(sqrt(-3d)) (whose discriminant is -3d if 3 does not divide d and -d/3 if it does).
Scholz's reflection theorem gives r'(d) - r(d) in {0, 1}. Dutarte's conjecture (1984; Conjecture 1.1 and equations (2),
(5), (11) of Fouvry and Klueners, "On the Spiegelungssatz for the 4-rank", Algebra & Number Theory 4 (2010) 493-508) says
that over all positive fundamental discriminants, P(r' = r + 1 | r) = 3^-(r+1), and (with Cohen-Lenstra) that the overall
proportion with r' = r + 1 is 0.29765117.... Fouvry and Klueners print no data.

## History the reviewer should know
An earlier packet today claimed that an extrapolation p(x) = p_inf + c x^(-1/6) with free p_inf agreed with the conjecture
at 10^9. It failed review (1 of 3): the verdict depended on the exponent, and the same test failed for r = 1 at 10^10.
That claim is withdrawn. All data up to 10^10 had therefore been seen before the present test was designed, and the
two-term model below was chosen after looking at them. Only the range (10^10, 10^10.5] is out of sample.

## Frozen definition of "solved" for this question (fixed, and committed to version control, before any discriminant
## above 10^10 was counted)
Question: does the conjectured limit, with two correction terms fitted below 10^10, predict the new range
(10^10, 10^10.5]? Solved means all of:
(a) the exact table n(r, e; X) = number of positive fundamental discriminants d <= X with r(d) = r and r'(d) - r(d) = e,
    at the checkpoints X = round(10^(k/10)), k = 30..105, so X_max = 31,622,776,602 and no further; every pair satisfies
    Scholz's theorem;
(b) the prediction test, for each of four series (proportion with e = 1 over all d; among d with r = 0; r = 1; r = 2):
    bins = the d between consecutive checkpoints; x = geometric midpoint of the bin's two checkpoints.
    Model M2: p(x) = p_conj + c1 x^(-1/6) + c2 x^(-1/3), with p_conj FIXED at the conjectured limit (0.29765117...,
    1/3, 1/9, 1/27); c1, c2 fitted by weighted least squares on the 40 bins in (10^6, 10^10], weights 1/variance with
    variance pt(1 - pt)/n, pt = (s + 1/2)/(n + 1) (s successes of n in the bin). Prediction for the 5 new bins in
    (10^10, 10^10.5]. Statistic T = r^T (V + J S J^T)^-1 r, with r = observed minus predicted proportions of the new
    bins, V = diagonal of q(1 - q)/n at the predicted q, S = the covariance matrix of (c1, c2) from the fit (inverse of
    the weighted normal matrix), J = the 5 x 2 matrix of x^(-1/6), x^(-1/3) at the new bins. Under the model T is
    chi-square with 5 degrees of freedom. HELD if its p-value is > 0.01, FAILED otherwise; reported as it falls.
    Comparator: M1, the same with c2 = 0.
    Sensitivity, fixed in advance: the same T with every variance halved (reviewers of the earlier packet found the
    binomial errors about sqrt 2 too large); and the interval of shifts delta such that M2 with p_conj + delta in place
    of p_conj (c1, c2 refitted) is still HELD;
(c) no table or test of this law to a comparable range is already published.
"HELD" is a statement about conjecture and model jointly on this range, not a confirmation of the conjecture.

## The claim
(a) `table.csv` next to this packet is exact (76 rows, columns n{r}{e}; no d <= X_max has r = 4). At X_max there are
    9,612,171,555 positive fundamental discriminants, 2,841,877,607 of them with r' = r + 1:
      r = 0: 8,131,719,069 of which 2,685,854,176 have e = 1
      r = 1: 1,462,412,648 of which   155,479,714
      r = 2:    18,026,121 of which       543,632
      r = 3:        13,717 of which            85
    No pair violates Scholz's theorem.
(b) The prediction test gives
      series     M2: c1, c2            T      p       verdict   variances halved    M1: T, p, verdict
      aggregate  -0.09239, -0.04566    1.47   0.917   HELD      2.93, 0.710 HELD    1.56, 0.906 HELD
      r = 0      -0.14055, -0.06314    3.33   0.650   HELD      6.65, 0.248 HELD    2.34, 0.800 HELD
      r = 1      -0.21952, -0.27555    4.25   0.514   HELD      8.51, 0.130 HELD    28.78, 0.0000 FAILED
      r = 2      -0.31199, -0.54254   10.81   0.055   HELD      21.63, 0.0006 FAILED  12.17, 0.033 HELD
    Shift intervals for which M2 is still HELD: aggregate [-0.00028, +0.00022]; r = 0 [-0.00035, +0.00019];
    r = 1 [-0.00027, +0.00055]; r = 2 [-0.00103, +0.00130].
(c) What is claimed: by the rule fixed in advance, M2 with the conjectured limits HELD for all four series on the unseen
    range, and the one-term model M1 FAILED for r = 1. What is NOT claimed: that the conjecture is confirmed; that M2 is
    the true shape of the approach to the limit; or that the r = 2 result is robust (it fails when the variances are
    halved, mostly through one bin).
(d) No table or test of this law to a comparable range has been published.

## Artifact
`table.csv`. Nothing else.

## Compute note
The full table took us about 2.5 CPU-hours by our method; methods differ in cost by orders of magnitude. A reviewer
should rebuild as much of the table as the time allows by a method of their own, and must state exactly which rows were
rebuilt. The test in (b) needs only the table.
