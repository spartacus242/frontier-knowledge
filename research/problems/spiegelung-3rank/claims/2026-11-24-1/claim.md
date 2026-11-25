# Claim packet 2026-11-24-1

## Problem
For a positive fundamental discriminant d let r(d) be the 3-rank of the class group of Q(sqrt d) and r'(d) the 3-rank of
the class group of its mirror field Q(sqrt(-3d)) (whose discriminant is -3d if 3 does not divide d and -d/3 if it does).
Scholz's reflection theorem gives r'(d) - r(d) in {0, 1}. Dutarte's conjecture (1984; Conjecture 1.1 and equations (2),
(5), (11) of Fouvry and Klueners, "On the Spiegelungssatz for the 4-rank", Algebra & Number Theory 4 (2010) 493-508) says
that over all positive fundamental discriminants, P(r' = r + 1 | r) = 3^-(r+1), and (with Cohen-Lenstra) that the overall
proportion with r' = r + 1 is 0.29765117.... Fouvry and Klueners write that the conjecture "has been tested on a computer"
by Dutarte, and that in their own experiments "the constants are close, but not too close"; they print no data.

## Frozen definition of "solved" (fixed before the computation)
The numerical question is solved when:
1. there is an exact table of n(r, e; X) = the number of positive fundamental discriminants d <= X with r(d) = r and
   r'(d) - r(d) = e, for X up to X_max >= 10^9;
2. this pre-set test is applied to it: split (10^6, X_max] into the bins between consecutive checkpoints
   X = round(10^(k/10)); in each bin take the proportion with e = 1 (over all d, and among d with r = 0, 1, 2) with its
   binomial variance (variance evaluated at (s + 1/2)/(n + 1) so that an empty bin has finite weight); fit
   p(x) = p_inf + c x^(-1/6) by weighted least squares at the bins' geometric midpoints. For each of the four quantities:
   CONSISTENT if the conjectured limit lies within 3 standard errors of the fitted p_inf; INCONSISTENT otherwise; VOID if
   the fit's chi-square exceeds 2 per degree of freedom;
3. no table or test of comparable range is already published.
This is a numerical test of a conjecture, not a proof of it.

## The claim
(a) The file `table.csv` next to this packet is exact: for each checkpoint X = round(10^(k/10)), k = 30..90 (so X from
    10^3 to 10^9), it lists n(r, e; X) as columns n{r}{e}. In particular at X = 10^9 there are 303,963,559 positive
    fundamental discriminants, of which 89,388,474 have r' = r + 1, and
      r = 0: 258,536,250 of which 84,775,065 have e = 1
      r = 1:  44,945,361 of which  4,601,647
      r = 2:     481,756 of which     11,762
      r = 3:         192 of which          0
(b) The pre-set test gives: aggregate p_inf = 0.297772 +- 0.000139 (conjecture 0.29765117); r = 0: 0.333524 +- 0.000155
    (1/3); r = 1: 0.111633 +- 0.000240 (1/9); r = 2: 0.036982 +- 0.001111 (1/27); chi-square 13.1, 15.2, 14.1, 15.2 on 28
    degrees of freedom. All four: CONSISTENT. The raw proportions at 10^9 (0.294076, 0.327904, 0.102383, 0.024415) are
    well below the conjectured limits, and the x^(-1/6) term accounts for the gap.
(c) Disclosure, not part of what is claimed as verified: our own extension of the table to X_max = 10^10 (3,039,635,379
    discriminants, 897,388,600 with r' = r + 1; rows not included here) gives under the same test aggregate 0.297699 +-
    0.000042, r = 0: 0.333398 +- 0.000047, r = 2: 0.037656 +- 0.000351 (all CONSISTENT) but r = 1: 0.111415 +- 0.000073,
    which is 4.2 standard errors above 1/9, i.e. INCONSISTENT WITH THIS MODEL by the pre-set rule. So the claim is limited
    to: at X_max = 10^9 the pre-set test finds all four CONSISTENT; it is NOT claimed that the one-term model survives to
    10^10, nor that the conjecture is confirmed.
(d) No table or test of this law to a comparable range has been published.

## Artifact
`table.csv` (61 rows). Nothing else.

## Compute note
We do not expect a reviewer to recompute every row. Recompute as many rows as you can by a method of your own (rows up to
10^6 or 10^7 are cheap by several methods; the full table took us a few CPU-minutes by our method, and other methods
can be far slower), state exactly which rows you reproduced, and re-run the test in (b) on the table yourself.
