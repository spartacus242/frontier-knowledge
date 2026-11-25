# Skeptic review, claim 2026-11-25-1 (a(80..100) of A304884)
Code: s.c (exhaustive search), val.py (validation on OEIS), wit.py (witness check), run.sh, res/<n>.txt (one result per n).

## 1. Reproduced: YES
(i) wit.py checked all 21 witnesses in terms.csv by brute force over all (x,y,z) triples incl. repeats (x+z=2y mod n, not x=y=z): all valid, sizes equal the claimed a(n).
(ii) Own program s.c: DFS over increasing elements, 0 in S (translation), largest cyclic gap placed before 0 (translation symmetry breaking, so every set is covered up to translation), 128-bit forbidden masks, counting prune. Even n: x and x+n/2 forbidden together. Validation: OEIS data (fetched via WebFetch of A304884 and its b-file, n=1..79, identical) for every n=3..79: a size-a(n) set is found AND no size a(n)+1 set exists (val.py, 0 mismatches, 7.4 s total).
Main run: for each n=80..100, search for size a(n)+1 (claimed value +1) finished with exhaustive result NONE for ALL 21 n (80..100), single core, about 2 minutes total (largest: n=99, 3.7e8 nodes; n=100 1.4e8). Together with the verified witnesses, a(80..100) = 15,16,16,16,16,17,16,16,16,16,16,17,16,17,16,17,17,17,16,17,17 as claimed. Only one program of mine (the claim's two-program agreement is not something I checked).
(iii) Definition: OEIS name/comment ("trivial progressions are x,x,x") and Halbeisen-Halbeisen (ems.press text: elements need not be distinct, non-constant progression, example n=4 {0,2} forbidden) match the packet. My program reproduces OEIS for even n, confirming the repeated-element convention.

## 2. Novel: YES as far as I could determine
Queries (WebSearch): "OEIS A304884 largest subset cyclic group no 3-term arithmetic progression a(80)"; "Avoiding arithmetic progressions in cyclic groups Halbeisen alpha(n,3) values table"; "cap sets Z_n 3-AP-free subsets cyclic group maximum size computed n up to 100 Salem-Spencer modular". WebFetch: oeis.org/A304884 (data ends a(79)=15, no terms beyond), its b-file (ends n=79), ems.press Halbeisen paper (table only n=9..27 plus a few), arxiv 2606.30186 (complete sets, not max size, no table n>=80), oeis.org/A341584 (different function, to n=80, a(80)=18).
Not opened/limits: Google Scholar, MathOverflow, Math StackExchange, Wikipedia (Salem-Spencer, cap set) were not directly opened (only appeared via search engine, no hit); no citing-paper search via Scholar; curl to oeis.org is blocked by the proxy (403). So absence is based on limited search; a late/unindexed table cannot be excluded.

## 3. Honest: YES
Claim states exactly what was computed (witnesses, upper bounds a(80..100)), target a(80..90) met and exceeded, values beyond 100 explicitly not claimed, A341584/A003002 explicitly distinguished. I could not check the claimant's statements about their two programs/CPU times.

Timings: validation 7 s; n=80..100 about 2 minutes total on one core.
