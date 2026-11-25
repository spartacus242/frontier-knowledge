# Skeptic review of claim packet 2026-11-24-2 (Dutarte / Scholz 3-rank table and prediction test)

Verdict: **REJECT** (reproduction: clear yes; honesty: yes, with reservations; novelty as worded: not a clear yes).
All code here was written from scratch in this directory; I read only `claim.md`, `table.csv` and the brief.

## 1. REPRODUCED? — yes, completely

### (i) The table: all 76 rows rebuilt, 76 match, 0 differ (my `mytable.csv` is byte-identical to `table.csv`)

Method (`cub.c`, my own derivation, not Belabas's published reduction conditions):
* For a fundamental discriminant D the number of GL2(Z)-classes of integral binary cubic forms of discriminant D
  is 1 + (3^r3(D) - 1)/2 (one reducible class Z + O_K, plus one class per cubic field; every cubic ring of
  fundamental discriminant is maximal). So the class count must be one of 1, 2, 5, 14, 41 and gives r3 directly.
* r(d): count classes of forms with disc = d > 0, reduced through the Hessian (P,Q,R), 0 <= Q <= P <= R.
* r'(d): count classes of forms with disc = -3d (3 does not divide d) or -d/3 (3 | d), reduced by putting the
  complex root of the form in the GL2(Z) fundamental domain (-1 <= u <= 0, v >= 1 for the factor x^2+uxy+vy^2).
* Forms on the boundary of the reduction domain are settled by explicitly generating the orbit under the
  stabiliser and keeping the lexicographic maximum, so each class is counted exactly once (reducible ones included).
* 20 segments of width 1.6e9 in d, one byte per discriminant, squarefree sieve, then the join. Resumable (`runall.sh`).

Result over all 9,612,171,555 positive fundamental d <= 31,622,776,602:
* every single d had a class count in {1,2,5,14} (real side) and {1,2,5,14,41} (mirror side): 0 anomalies;
* 0 violations of Scholz's theorem (r' - r in {0,1} for every d);
* final row 5445864893, 2685854176, 1306932934, 155479714, 17482489, 543632, 13632, 85 = the claimed
  r=0: 8,131,719,069 / 2,685,854,176; r=1: 1,462,412,648 / 155,479,714; r=2: 18,026,121 / 543,632; r=3: 13,717 / 85;
  total 9,612,171,555 with 2,841,877,607 having e = 1; no d with r = 4 (the 85 d with r' = 4 all have r = 3).
* All rows k = 30..105 match, including the five rows above 10^10 on which the claim rests.

Independent validation of my method (so the agreement is not two copies of one mistake):
* `clgp.py` (pure Python, no cubic forms at all): 3-ranks from class groups of binary quadratic forms
  (Gauss composition; imaginary: reduced forms; real: cycles of reduced indefinite forms, narrow class group).
  Run for every fundamental d <= 251,189 and its mirror: its 25 checkpoint rows (X = 1000 .. 251189) equal the
  table; 0 Scholz violations. Also h(-23)=3, h(-47)=5, h(-163)=1, h+(12)=2, h(-3299)=27 with 3-rank 2,
  d=32009 has r=2 (known smallest), d=229 smallest with r=1.
* OEIS A250236 (d with both 3-class groups of order exactly 3): 40 terms up to 3000, first 229, last 2993 — my
  class-group code gives exactly 40, 229, ..., 2993.
* Smallest real d with r = 3 from my cubic-form run is 39,345,017 (the known Llorente-Quer value); class-group
  code confirms (r,r') = (3,3) for 39345017, 44806173, 61310597.
* The structural check above (9.6e9 counts all of the form 1+(3^r-1)/2, Scholz never violated) would be broken
  by essentially any error in the reduction theory or the loop bounds.

### (ii) The prediction test (`predtest.py`, re-implemented from the description), run on table.csv

| series | my c1, c2 | my T, p | claimed | halved var (mine) | M1 (mine) | shift interval (mine) | claimed |
|---|---|---|---|---|---|---|---|
| aggregate | -0.09239, -0.04566 | 1.47, 0.917 HELD | 1.47, 0.917 | 2.93, 0.710 HELD | 1.56, 0.906 HELD | [-0.000289, +0.000224] | [-0.00028, +0.00022] |
| r = 0 | -0.14055, -0.06314 | 3.33, 0.650 HELD | 3.33, 0.650 | 6.65, 0.248 HELD | 2.34, 0.800 HELD | [-0.000357, +0.000195] | [-0.00035, +0.00019] |
| r = 1 | -0.21952, -0.27555 | 4.25, 0.513 HELD | 4.25, 0.514 | 8.51, 0.130 HELD | 28.78, 0.0000 FAILED | [-0.000278, +0.000552] | [-0.00027, +0.00055] |
| r = 2 | -0.31199, -0.54254 | 10.81, 0.055 HELD | 10.81, 0.055 | 21.63, 0.0006 FAILED | 12.17, 0.033 HELD | [-0.001034, +0.001300] | [-0.00103, +0.00130] |

Everything agrees; the shift intervals agree after truncation toward zero (one 0.001 difference in a p-value is rounding).
Same numbers from my rebuilt table (identical file).

### (iii) Constants
* Fouvry-Klueners, ANT 4 (2010) 493-508: Conjecture 1.1 / eq. (2) is exactly the 3^-(r+1) law over positive
  fundamental D with Q(sqrt(-3D)); eq. (5) the conditional-probability form; eq. (11) gives 0.29765117....
  (Read through a text extraction of the msp.org PDF.) Dutarte's own report (Besancon 1983-84) has the same
  conditional law (his eq. (3)).
* Recomputed: sum_r 3^-(r+1) * eta_inf(3) 3^-r(r+1) / (eta_r(3) eta_(r+1)(3)) = 0.2976511729. Matches.

## 2. NOVEL? — not a clear yes as worded

What I found:
* **Belabas, "On quadratic fields with large 3-rank", Math. Comp. 73 (2004) 2061-2074, sections 4.2.3 and 5.2.**
  States Dutarte's conjecture (Conj. 4.3), finds all 1618 real quadratic fields with r3 = 4 in 0 < d <= 1.6e13,
  computes the 3-ranks of all their mirrors and compares with the law: "According to Dutarte's heuristic, roughly
  1618/3^5 = 6.7 of them should have a complex mirror of 3-rank equal to 5. In fact there are exactly 6."
  This is a published numerical test of this law (its r = 4 case) to a range 500 times beyond 3.16e10. It has no
  counts for r <= 3 and its sample is 1618, so it does not duplicate the table, but the unqualified sentence
  "No table or test of this law to a comparable range has been published" is contradicted by it. The packet does not cite it.
* Fouvry-Klueners themselves, next to eq. (11): "It has been tested on a computer by Dutarte [1984, 4.2]. We ran
  similar experiments and the constants are close, but not too close." No data or range printed. The packet's
  "Fouvry and Klueners print no data" is true but leaves this out.
* Dutarte 1984, section 4.2: chi-square test that 1/3 of fundamental units are 3-primary, two random samples of
  1000 discriminants (range lost in extraction). Small.
* Kraft-Washington, "Heuristics for class numbers and lambda invariants", Math. Comp. 76 (2007) 1005-1023: predicts
  the 3-parts of Cl(Q(sqrt(-d))) and Cl(Q(sqrt(3d))) from Cohen-Lenstra + Scholz and "tests computationally".
  **I could not open the full text** (AMS PDF and ResearchGate refused), so I do not know its range; related work
  (Ellenberg-Jain-Venkatesh) uses about 10^6 fields, so I expect it to be far below 10^10, but this is unverified.
* Breuer-Punch, "Quadratic units and cubic fields", arXiv 2507.06579: computation to 10^11 with 1/3 - c d^(-1/6)
  fits, but for units modulo 2 (conductor-2 ring class groups), an analogue, not this law.
* No table of n(r,e;X) found anywhere: Belabas 1997/1999/2004 (cubic field counts to 1e11, mean 3-rank), Malle
  2008/2010 (quadratic extensions of Q(sqrt(-3)), different family), Sawin-Wood 2023, Ellenberg's 2026 survey,
  Y. Lee 2002, Dalla Torre's thesis (abstract only), OEIS A250235-A250242 (d <= 3000 or so), Wikipedia
  "Reflection theorem" (no statistics), MathOverflow / Math.SE (nothing found).

Could not open: Kraft-Washington 2007 full text; Dalla Torre thesis chapters; algebra.at/mirror.htm (D. C. Mayer);
Exp. Math. doi 10.1080/10586458.2026.2633713 (not identified); Google Scholar (robots); Y. Lee 2002 full text;
arXiv author listing for Klueners (rate limit). Citation lists of Fouvry-Klueners 2010 and Dutarte 1984 were
searched only through general web search. Each of these could hide a further test; none is likely to hold a
table to 3e10, but with Belabas 2004 already on record the novelty statement needs rewording regardless.

Queries (web search unless noted):
1. Dutarte conjecture Scholz reflection 3-rank real quadratic field mirror imaginary probability numerical table
2. Fouvry Klueners "On the Spiegelungssatz for the 4-rank" Dutarte conjecture 3-rank 3^{-(r+1)}
3. Dutarte 1984 "Compatibilite avec le Spiegelungssatz de probabilites conjecturales sur le p-rang du groupe des classes"
4. numerical test 3-rank real quadratic field versus Q(sqrt(-3d)) Scholz "r+1" proportion fundamental discriminants computation up to 10^9 OR 10^10 OR 10^11
5. Belabas "3-rank" quadratic fields computation cubic fields discriminant 10^11 table Cohen-Lenstra secondary term numerical
6. "Spiegelungssatz" Cohen-Lenstra heuristics 3-rank numerical evidence "Dutarte" escalatory non-escalatory Scholz statistics
7. mathoverflow Scholz reflection theorem 3-rank real quadratic imaginary quadratic how often r' = r+1 heuristics data
8. math.stackexchange Scholz reflection principle 3-rank Q(sqrt(d)) Q(sqrt(-3d)) probability equal ranks statistics
9. OEIS real quadratic fields 3-rank class group mirror field Q(sqrt(-3d)) Scholz sequence discriminants
10. Dalla Torre "The unit residue group" thesis Leiden Scholz theorem 3-ranks statistics fundamental unit cube modulo 3 density numerical
11. citing "On the Spiegelungssatz for the 4-rank" Fouvry Klueners 3-rank Dutarte conjecture numerical verification computation
12. "Dutarte" conjecture 3-rank "Q(\sqrt{-3D})" OR "-3D" Cohen-Lenstra reflection joint distribution proven OR numerical 2020..2026 arXiv
13. Malle "Cohen-Lenstra heuristic and roots of unity" OR "On the distribution of class groups of number fields" data Q(sqrt(-3)) 3-part quadratic fields discriminant range Scholz
14. "3-primary" fundamental unit real quadratic field density one third numerical "Scholz" "escalatory" count discriminants table
15. Belabas "On quadratic fields with large 3-rank" Mathematics of Computation 2004 Dutarte heuristic mirror 1618 real fields 3-rank 4
16. tabulation class groups real quadratic fields AND imaginary mirror "Scholz" verification 3-rank "10^{11}" Jacobson Williams te Riele Mosunov statistics reflection
17. Cohen-Lenstra real quadratic 3-rank conditional on mirror imaginary field numerical experiment "x^{-1/6}" secondary term Roberts Taniguchi-Thorne Bhargava-Shankar-Tsimerman 3-torsion count data
18. Yoonjin Lee "Cohen-Lenstra heuristics and the Spiegelungssatz: number fields" numerical data real quadratic 3-rank mirror table discriminant bound
19. scholar "Dutarte" "Spiegelungssatz" cited by 3-rank quadratic fields numerical "table" r3(-3d) = r3(d)+1 frequency computed discriminants
20. Kraft Washington "Heuristics for class numbers and lambda invariants" Scholz 3-rank Q(sqrt(-d)) Q(sqrt(3d)) numerical data range discriminants pdf (and three variants of it)
21. arXiv 2024 OR 2025 OR 2026 numerical "Scholz" reflection "3-rank" real quadratic "mirror" distribution "cubic fields" count discriminant "10^{10}" OR "10^{11}" Cohen-Lenstra test Dutarte
22. Daniel C. Mayer "Connections between Cubic and Dual Quadratic Fields" mirror algebra.at Scholz 3-class rank statistics counts discriminants
23. Experimental Mathematics 2026 10.1080/10586458.2026.2633713
Pages read (via fetch): msp.org ANT 2010 4-5 p01 (Fouvry-Klueners); pmb.centre-mersenne.org pmb.a-40 (Dutarte);
Belabas r3.pdf, mean3-99.pdf, mathcomp97.pdf; arXiv 2507.06579, 2512.20023, 2301.00791, 0912.1427, 2606.06024,
2506.13749, 2208.06862, 2207.06287; ejv.pdf (Ellenberg-Jain-Venkatesh); OEIS A250236; Wikipedia Reflection theorem;
AMS abstract page of Kraft-Washington; Ewha page for Y. Lee 2002; Byeon's Q(sqrt D), Q(sqrt tD) paper; Leiden thesis record.

## 3. HONEST? — yes as worded, with reservations a reader should carry

* History is handled openly: the earlier failed packet, the fact that all data below 10^10 had been seen and that
  M2 was chosen after seeing them, and that only (10^10, 10^10.5] is out of sample are all stated. The goal was
  narrowed from "agrees with the conjecture" to "the fixed limit plus two fitted terms predicts half a decade";
  the packet says so and says HELD is a joint statement about model and conjecture.
* The claim as worded is a claim about a table (exact, confirmed) and the outcome of a stated rule (confirmed).
  It explicitly disclaims confirmation of the conjecture, the shape M2, and the robustness of r = 2.
* Reservations:
  1. The decision rule uses binomial variances the authors already knew to be about twice too large. The fit
     confirms it: chi-square of the M2 fit on 38 degrees of freedom is 15.0, 20.4, 22.2, 19.0 (ratio 0.39-0.58).
     With variances rescaled by those ratios (or simply halved) r = 2 FAILS (T = 21.6, p = 0.0006), and I find
     no shift delta at all for which r = 2 would be HELD under halved variances (min T = 21.5), so that failure
     is one bin / the model, not the limit. "HELD for all four series" is therefore true only under the
     inflated-variance rule; the packet does disclose this, but the headline rests on it.
  2. The test is an extrapolation over half a decade after a four-decade fit (x^(-1/6) moves from 0.0215 to
     0.0178); p-values near 0.9 mostly reflect the inflated variances. Its real content is the shift intervals:
     limits differing from the conjectured ones by more than about 3e-4 (aggregate, r = 0), 3-5e-4 (r = 1),
     1e-3 (r = 2; about 3 percent of 1/27) would have been rejected; with halved variances roughly
     [-2.0e-4, +1.4e-4], [-2.5e-4, +0.9e-4], [-1.1e-4, +3.9e-4], and nothing for r = 2.
  3. The literature paragraph is thinner than it should be (see 2): it is the novelty sentence, not the
     numerical claims, that overreaches.

## Timings (one core)
* Table rebuild: 20 segments, 1701 s wall in total (about 76-92 s per segment), about 1.9 GB RAM.
* Class-group validation in Python to d <= 251,189: about 12 min. Prediction test: under 1 s (shift scans a few seconds).

## Files
`cub.c`, `runall.sh`, `seg_0.out` .. `seg_19.out`, `combine.py`, `mytable.csv`, `clgp.py`, `clgp_251189.out`,
`clgp_31623_v2.out`, `predtest.py`, `run.log`, `verdict.txt`.

Note on the validator: `clgp_251189.out` was produced before I tightened one normalisation step in the reduction of
indefinite forms (needed only for d around 4e7, where an internal assertion stopped the run; it never fired below
251,189). The corrected version reproduces the same rows up to 31,623 (`clgp_31623_v2.out`).
No background process of mine is left running.
