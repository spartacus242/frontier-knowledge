# Skeptic 3 (Opus), claim 2026-11-24-2: REJECT

(The reviewer could not write this file itself; this is its final report as handed back, condensed by the claimant without
changing any finding. Its own `verdict.txt`, code and `compare_full.txt` are beside this file.)

## 1. Reproduced? Yes
- Table: all 76 rows rebuilt with own code (`cub.c`), X = 1000 to 31,622,776,602; every column matches. No d <= X_max has
  r >= 4; zero Scholz violations; totals of claim (a) match. A separate small run rebuilt every row to 10^7 first.
- Method: counts GL2(Z)-classes of irreducible binary cubic forms of fundamental discriminant D, which number
  (3^r - 1)/2. D > 0: positive definite Hessian, reduced domain 0 <= Q <= P <= R, a >= 1. D < 0: reduction of the real
  quadratic factor, as three integer conditions bc >= ad, (a-b)^2 + c(a-b) + ad >= 0, d^2 - a^2 >= bd - ac. Boundary cases
  by lexicographic maximum among images under small GL2 matrices. 8 segments, about 30 CPU-minutes on one core, 2.1 GB.
- Independent validation: `brute.py` computes 3-ranks from class groups of binary quadratic forms; agrees with the cubic
  counts for all 182,369 fundamental D with |D| <= 300,000 (except the expected special cases -3 and -4).
- Prediction test re-implemented (`test.py`): aggregate c = -0.09239, -0.04566, T 1.4669, p 0.9169; r=0 -0.14055,
  -0.06314, T 3.3267, p 0.6498; r=1 -0.21952, -0.27555, T 4.2537, p 0.5135, M1 T 28.78 FAILED; r=2 -0.31199, -0.54254,
  T 10.8129, p 0.0552, halved variances T 21.63 FAILED. Shift intervals [-0.000289, +0.000224], [-0.000357, +0.000195],
  [-0.000278, +0.000552], [-0.001034, +0.001300] (the packet's endpoints are these truncated toward zero). r=2
  standardized residuals in the new bins: 0.15, -2.94, -0.77, 1.34, 0.23.
- Constants: Cohen-Lenstra sum 0.297651172917; Fouvry-Klueners Conj. 1.1, (2), (5), (11) as quoted; Belabas (Compositio
  1999, Conj. 3.2; Math. Comp. 2004, section 4.2.3) state the same law.

## 2. Novel? Not a clear yes
19 queries (Fouvry-Klueners/Dutarte; arXiv numerical Scholz reflection data; papers citing Fouvry-Klueners; "Heuristics for
class numbers and lambda invariants" (Kraft-Washington, Math. Comp. 2007); MathOverflow, Math StackExchange and OEIS
searches; Belabas's cubic field tables; Jacobson real quadratic class groups; "Scholz defect"; site-restricted searches).
Key finding: Belabas, "On quadratic fields with large 3-rank", Math. Comp. 73 (2004), section 5.2, computed the mirror
3-ranks of all 1618 real fields with 3-rank 4 up to about 1.6e13 and compared with Dutarte's prediction (1618/35, about
6.7 rank-5 mirrors; found 6). That is a published numerical test of this law (the r = 4 slice) far beyond 10^10.5, and
the packet does not cite it. Belabas 1997 (all cubic fields to 10^11) implicitly determines the table but prints no
joint table. Kraft-Washington test joint 3-part heuristics for Q(sqrt(-d)) and Q(sqrt(3d)); only the abstract was
readable, range unknown. Could not open: Google Scholar cited-by lists, Kraft-Washington full text, Dalla Torre's thesis
chapters. Conclusion: a full joint table to 10^10.5 with a four-series prediction test appears unpublished, but claim (d)
and frozen condition (c) as worded are contradicted by Belabas 2004.

## 3. Honest? Mostly yes, with caveats
Positive: history disclosed candidly; (c) does not claim confirmation; r = 2 fragility flagged; numbers accurate; nothing
narrowed. Caveats: the pre-registration cannot be verified from the packet (no commit hash or timestamp); the test is weak
(a two-parameter correction fitted on the adjacent 40 bins and chosen after the one-term model failed extrapolates half a
decade almost regardless of the limit; the shift intervals show how little HELD pins down; the M1 failure for r = 1 shows
power against a rigid model, not support for the limit); "HELD for all four" depends on the variance model; the novelty
clause overreaches.
