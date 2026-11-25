# Claim packet 2026-11-25-1

## Problem
For n >= 3 let a(n) be the size of the largest subset S of the cyclic group Z_n that contains no nontrivial 3-term
arithmetic progression: no x, y, z in S, not all equal, with x + z = 2y (mod n). Equivalently no x, x+d, x+2d all in S
with d != 0 (mod n); the three elements need not be distinct, so for even n a set may not contain both x and x + n/2.
This is OEIS A304884 (for n >= 3) and the function alpha(n, 3) of Halbeisen and Halbeisen, "Avoiding arithmetic
progressions in cyclic groups", Elem. Math. 60 (2005) 114-123, who write "we do not require all elements of the sequence
to be different".

Published values known to us: Halbeisen and Halbeisen give n = 9..12, 17..20, 24, 25, 27 (table), 5, 7, 35, 36 (text).
OEIS A304884 lists a(1)..a(79) (a(51)..a(79) from Giovanni Resta, 2018-05-22; b-file n = 1..79; page read 2026-11-25),
ending ..., a(75..79) = 14, 14, 14, 14, 15. Different functions, not claimed here: OEIS A341584 (progressions must have
three distinct elements; listed to n = 80) and A003002 (subsets of the integer interval [1, n]).

## Frozen definition of "solved" (written before any term beyond 79 was computed)
This run's target: exact values a(80), ..., a(90) at least (a contiguous block; more is welcome, fewer is a sub-result),
each with a witness set of that size and an exhaustive proof that no admissible set one larger exists, obtained by two
programs of ours that share no search code and agree and that both reproduce the published a(3)..a(79); and the terms
not already published.

## The claim
(a) a(80), ..., a(100) = 15, 16, 16, 16, 16, 17, 16, 16, 16, 16, 16, 17, 16, 17, 16, 17, 17, 17, 16, 17, 17.
(b) `terms.csv` next to this packet gives for each n a witness set of size a(n) (lower bound).
(c) For each n in 80..100 no admissible set of size a(n) + 1 exists (upper bound): established by exhaustive computer
    search with two independently written programs, which agree on every n in 80..100 and on the published terms.
(d) These 21 terms are not already published: the OEIS entry and its b-file stop at n = 79, and we found no other table
    of this function beyond n = 79.
Not claimed: values beyond n = 100 (we have single-program values up to 112, not cross-checked and not part of this
claim).

## Artifact
`terms.csv`. Nothing else.

## Compute note
The upper bounds are the expensive part. Over all 21 terms, one of our programs needed about 1.5 CPU-minutes and the other
about 3 CPU-hours; the cost grows by roughly 1.3 per step in n and odd n are harder than even n. A reviewer who cannot
finish every n should say exactly which were finished.
