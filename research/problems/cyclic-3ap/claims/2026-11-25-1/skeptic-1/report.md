# Skeptic review of claim packet 2026-11-25-1 (A304884, n = 80..100)

Verdict: SIGN-OFF (see verdict.txt). All work below is my own code in this directory; I read only claim.md and terms.csv.

## 1. REPRODUCED? Yes, for every n in 80..100.

(i) Witnesses. `check.py` tests each terms.csv row straight from the definition (all triples x,y,z in S, not all equal,
x+z = 2y mod n; size and distinctness checked). All 21 witnesses are admissible and have the stated size.

(ii) Upper bounds. `rd.c` is an exhaustive "Russian doll" branch-and-bound: f(m) = largest admissible subset of the
window {0..m-1} of Z_n (progressions taken mod n), computed for m = 1..n; f(m) = f(m-1)+1 iff a set containing m-1 of
that size exists; elements are chosen in decreasing order and a branch is cut only when count + f(j+1) or
count + (number of still-allowed candidates) is below the target. Both cuts are valid bounds, so f(n) = a(n) exactly,
i.e. each run proves both existence of size a(n) and non-existence of size a(n)+1. No symmetry reduction is used.
The search FINISHED for every n = 3..100 (one result file per n in res/). Results for n = 80..100:
15 16 16 16 16 17 16 16 16 16 16 17 16 17 16 17 17 17 16 17 17 -- identical to claim (a) in all 21 places.
So for all n in 80..100 I independently confirm: no admissible set of size a(n)+1 exists.

Validation of my program: rd.c reproduces all of OEIS a(3)..a(79) (b-file fetched by me, saved in
oeis/b304884_as_fetched.txt), value and impossibility of one more, 0 mismatches. A second, structurally different
program (`dfs.c`: 0 in S WLOG, increasing order, counter-based forbidden array, popcount bound only) confirms
"size a(n) exists, size a(n)+1 does not" for n = 3..58 against OEIS; plain Python subset enumeration (`check.py`)
confirms a(3)..a(24). Every witness that rd.c itself produced was re-verified by the Python definition check.
Caveat: for n = 80..100 the upper bound rests on my one program rd.c (plus agreement with the claimant's value).

Timings (one core): rd.c total 1568 CPU-s for n = 3..100; n=80: 4 s, 85: 10 s, 90: 26 s, 95: 108 s, 97: 185 s,
98: 151 s, 99: 457 s (hardest, 2.2e10 nodes), 100: 141 s. dfs.c cross-check n=3..58: ~11 s. Wall time ~25 min.

(iii) Definition. OEIS A304884: "Size of the largest subset of the cyclic group of order n which does not contain a
nontrivial 3-term arithmetic progression"; comment "Arithmetic progressions are trivial if they are of the form
x,x,x". Halbeisen & Halbeisen (EMS PDF read): progression a, a+d, ..., 1 <= d < n, "we do not require all elements of
the sequence to be different". Packet definition matches both. Confirmed numerically: the strict definition gives
a(6)=2, a(36)=8 as in OEIS/paper (the distinct-element variant A341584 gives 4 at n=6). The paper's values (n=9..12,
17..20, 24, 25, 27, 35, 36, also 3, 5, 6, 7) agree with OEIS and my program. Notes: OEIS a(2)=2 does not satisfy the
strict definition, the packet correctly restricts to n >= 3; the packet's list of the paper's text values omits n=3
and 6 (immaterial). For odd n A341584 = A304884; A341584 (data and b-file) stops at n=80, so nothing odd beyond 79.

## 2. NOVEL? Yes as far as I could search: no published value of this function beyond n = 79 found.

Opened and read: OEIS A304884 page and /internal (79 terms, %E "a(51)-a(79) from Giovanni Resta, May 22 2018", last
edit #13 Jul 05 2018, only crossref A003002); b304884.txt (ends "79 15"); A341584 /internal and b341584.txt (end at
n=80, distinct-element variant); Halbeisen-Halbeisen PDF at ems.press (largest k=3 value n=36); arXiv 2606.30186 and
2401.06283 (Csajbok-Nagy: MINIMUM complete 3-AP-free sets, distinct-element definition, tables m<=80, no maxima);
arXiv 1903.08266 and 2009.11897 (Z_m^n, only tiny m for n=1); 2501.01634 and 2606.04016 (integer interval [1,N]);
2401.12802 (asymptotic Z_m^n); Wikipedia "Salem-Spencer set" and "Cap set" (no cyclic-group values, no mention of
A304884 or Halbeisen).

Queries (WebSearch):
1. A304884 largest subset of cyclic group of order n no nontrivial 3-term arithmetic progression
2. Halbeisen "Avoiding arithmetic progressions in cyclic groups" cited by exact values Z_n 3-term progression free maximum size table
3. "r_3(Z_n)" OR "r_3(\mathbb{Z}_n)" exact values computation largest 3-AP-free subset cyclic group Z_n n up to 100
4. mathoverflow OR math.stackexchange largest subset of Z/nZ without three-term arithmetic progression exact values small n table
5. "3-term arithmetic progression" cyclic group Z_n maximum size exact values computed "n <= 100" OR "up to 100" Salem-Spencer modular
6. Halbeisen Halbeisen 2005 "arithmetic progressions in cyclic groups" alpha(n,3) extended computation new values
7. "A304884"
8. site:mathoverflow.net largest subset cyclic group Z_N no three-term arithmetic progression exact values small N computed
9. site:math.stackexchange.com largest subset Z_n no 3-term arithmetic progression modulo n sequence values regular n-gon no isosceles triangle
10. maximum number of vertices of regular n-gon no three forming isosceles triangle exact values n up to 100 computed
11. arXiv "progression-free" subsets "Z_N" OR "Z/NZ" exact maximum small N SAT solver OR "integer programming" OR "exhaustive search" table 3-term cyclic "N = 97" OR "N=97" OR "N = 100"
12. "A341584" OR "does not contain a 3-term arithmetic progression modulo n" stackexchange "A question about this sequence"
13. "cyclic group" "no three-term arithmetic progression" OR "3-AP-free" maximum size "Z_81" OR "Z_{81}" OR "Z_85" OR "Z_{97}" OR "Z_{100}" exact
14. "Halbeisen" "Avoiding arithmetic progressions in cyclic groups" cited in arXiv references progression-free cyclic

Could NOT open: direct curl to oeis.org (proxy 403; pages obtained through the fetch tool instead, which summarises,
so the b-file was transcribed by that tool - it matches the /internal %S,%T,%U data line); OEIS full-text/sequence
search (robots-disallowed), so I could not search OEIS for the new terms as a subsequence or enumerate all related
sequences; Google Scholar (robots-disallowed) and Semantic Scholar API (error), so I have no "cited by" list for
Halbeisen-Halbeisen and relied on web-search hits; MathOverflow / Math.SE were searched only via general web search
(no site-internal search), and the MSE thread linked from A341584 was not opened. Bearing: novelty is "nothing found
after a reasonable search", not a proof of absence; an unindexed table (thesis, personal page, unsubmitted OEIS draft)
cannot be excluded. The packet's own wording ("we found no other table") is equally modest.

## 3. HONEST? Yes.

The frozen target was a(80)..a(90) at least, each with a witness and an exhaustive upper bound, from two independent
programs agreeing with each other and with a(3)..a(79). The claim delivers a contiguous block 80..100 under the same
(strict, OEIS/Halbeisen) definition; nothing was narrowed or weakened, and values 101..112 are explicitly excluded.
I cannot audit the claimant's two programs (not in the packet), but their output is right on all 21 terms and their
description of cost (odd n harder, ~1.3x per step) matches what I saw. The claim does not say more than was computed.

## Files
rd.c (main exhaustive search), dfs.c (second checker), check.py (witness check + brute force), final.py (comparison),
runall.sh, res/N.txt (one per n = 3..100: value, nodes, seconds, witness, f(1..n)), oeis/b304884_as_fetched.txt.
No background process left running.
