# Largest 3-AP-free subsets of cyclic groups (OEIS A304884): run of 2026-11-25 08:53 UTC

## Why tractable now
A304884(n) is the size of the largest subset of the cyclic group Z_n with no nontrivial 3-term arithmetic progression
(x, x+d, x+2d with d != 0 mod n; for even n this includes x, x + n/2, x). The OEIS entry lists a(1)..a(79); a(51)..a(79)
were added by Giovanni Resta on 2018-05-22 and the b-file stops at 79 (page read 2026-11-25). The values are small (15 at
n = 79), so each new term is a finite exhaustive search of a kind this project has already built (branch and bound with
bitmask propagation), a reviewer can rebuild single terms in CPU-minutes to CPU-hours with any method (integer
programming, SAT, clique search), and the lower bound for each term is a witness set anyone can check by hand. A
Russian-doll search written this morning reproduces a(1)..a(60), a(70) and a(79) and needs 134 s at n = 79, growing by
about 1.35 per step, so the low 80s are immediately in reach and the 90s need better pruning or symmetry.

## Standard definition of "solved", frozen before any term beyond 79 was computed
The problem "extend A304884" has no finish line; this run's target is fixed as follows. Definition used: S subset of
Z_n is admissible when there are no x, y, z in S, not all equal, with x + z = 2y (mod n). (This matches the OEIS data
for every n >= 3; the entry's a(2) = 2 does not follow from its own wording, which gives 1, and is not our concern.)
SOLVED for this run means all of:
(a) exact values a(80), a(81), ..., a(90), a contiguous block of eleven new terms (more is welcome, fewer is a
    sub-result), each with a witness set of that size;
(b) for each, an exhaustive proof that no admissible set one larger exists, by two programs of ours that share no search
    code and agree, both of which also reproduce the published a(3)..a(79);
(c) the terms are not already published (OEIS A304884 and its b-file, Halbeisen and Halbeisen 2005, and a literature
    search for tables of r_3(Z_n)).
A value supported by only one program, or a lower bound alone, is a sub-result and is labelled as such.

## Work and results
1. Russian-doll search (`code/rds.c`): g[p] = best subset of {p..n-1}, depth-first with count + g[v] pruning. Reproduces
   a(1)..a(60), a(70), a(79); 134 s at n = 79, factor about 1.35 per step. Correct but slow.
2. Same with a split-point bound (`code/rds2.c`): for every q, (allowed elements in [from, q)) + g[q] must reach the
   target. 3 times faster (44 s at 79). Used as the cross-check: a(80)..a(100), 1.46e11 nodes, about 3 CPU-hours.
3. Symmetry-reduced decision program (`code/sym.c`, no shared search code): affine maps x -> ux + t preserve the problem
   and gcd(x - y, n), so a set can be assumed to contain 0 and g for the first divisor g occurring as a gcd of a
   difference, with earlier gcds forbidden; bounds are a count of allowed elements and a greedy packing of disjoint
   progressions. Reproduces all 77 published terms a(3)..a(79) (value and impossibility of one more) in 5 s, and gives
   a(80)..a(100) in 96 s. Symmetry is worth three to four orders of magnitude here.
4. Variant check: `rds n 1` (three distinct elements required) reproduces OEIS A341584 for n = 3..56, so the progression
   tables are right in both conventions.
5. Literature: Halbeisen and Halbeisen 2005 define the same function (repeats allowed) and give values only up to
   n = 36; OEIS stops at 79. Csajbok and Nagy (arXiv 2401.06283) use the distinct-element convention and study minimum
   complete sets, a different question.
6. Beyond the claim: `sym` alone gives a(101)..a(112) = 17, 17, 18, 17, 18, 17, 18, 18, 18, 19, 20, 18 (single program,
   not cross-checked, NOT claimed).

Values: a(80..100) = 15, 16, 16, 16, 16, 17, 16, 16, 16, 16, 16, 17, 16, 17, 16, 17, 17, 17, 16, 17, 17. Both programs
agree on all 21; every witness passes `code/check.py`. Observation: for n = 81..84, 86..90, 92, 94, 98 the 16-element
set of integers below 41 with ternary digits 0 and 1 only is optimal.

## Skeptic gate, claim 2026-11-25-1: 3 of 3 SIGN-OFF
- Skeptic 1 (default model): own Russian-doll program without symmetry, all n = 3..100, 1568 CPU-s; second own checker to
  n = 58. Novelty: nothing found; OEIS search and Google Scholar blocked.
- Skeptic 2 (Sonnet): own exhaustive C search, all 21 terms in about 2 minutes, n = 3..79 matched first.
- Skeptic 3 (Opus): own search with a largest-gap normalisation and interval bounds from its own r_3 table, all 21 terms
  (343 s), re-run without the gap assumption (4223 s). Notes the packet's list of Halbeisen values omits n = 3 and 6,
  and that Math StackExchange question 4012158 (linked from A341584) could not be opened; for odd n A341584 equals
  this function, and its OEIS data stop at 80.
Remaining caveat, stated by all three: novelty is "nothing found" with OEIS full-text search and Google Scholar
unreachable.
