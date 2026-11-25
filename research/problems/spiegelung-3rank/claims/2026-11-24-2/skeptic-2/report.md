# Skeptic review, packet 2026-11-24-2

## 1. REPRODUCED?
(i) Own C code (rk.c): 3-rank of the narrow class group of Q(sqrt d) via reduced indefinite forms, rho-cycles and composition (3^r = number of cycles whose cube is principal); mirror field by reduced definite forms. Counts d > 1 fundamental. Validation: Scholz's inequality 0 <= r'-r <= 1 held for all ~6e5 discriminants computed (no violations, no non-power-of-3 counts). Cost is ~X^2, so 10^6 took ~10 min on one core; 10^7 would need ~17 h.
Rows rebuilt: all 31 rows X = 1000 ... 1,000,000 (k = 30..60) match table.csv exactly, every column. No row differed. Rows k = 61..105 (X from 1.26e6 to 3.16e10), including ALL rows above 10^10 on which the claim rests, were NOT rebuilt. 31 of 76 rows = 41%, 0 of 5 out-of-sample bins' rows.
(ii) Prediction test re-implemented from the description (test.py, numpy; chi2 sf for 5 dof in closed form). Results (40 fit bins, 5 new bins):
 aggregate c=(-0.09239,-0.04566) T=1.47 p=0.917; halved 2.93/0.710; M1 1.56/0.906; shift [-0.00029,+0.00022]
 r=0 c=(-0.14055,-0.06314) T=3.33 p=0.650; halved 6.65/0.248; M1 2.34/0.800; shift [-0.00036,+0.00019]
 r=1 c=(-0.21952,-0.27555) T=4.25 p=0.513; halved 8.51/0.130; M1 28.78/0.0000; shift [-0.00028,+0.00055]
 r=2 c=(-0.31199,-0.54254) T=10.81 p=0.055; halved 21.63/0.0006; M1 12.17/0.0325; shift [-0.00103,+0.00130]
All agree with the claim (shift endpoints differ by <=1e-5, my grid step is 1e-6; claim lists -0.00028 and -0.00035 where I get -0.00029 and -0.00036; immaterial). This only shows that the packet's arithmetic on its own table is right; it says nothing about whether the table is right above 10^6.
(iii) Constants: Fouvry-Klueners (msp.org/ant/2010/4-5/ant-v4-n5-p01-p.pdf) state Conjecture 1.1 as ratio -> 3^-(r+1), formula (11) gives 0.29765117..., matching the packet. NOTE: they say it is supported by Dutarte's computer tests (their sec. 4.2) and by their own similar experiments, "close, but not too close", attributing the gap to a second-order term. So the claim "Fouvry and Klueners print no data" is literally defensible but omits that they report experiments with a slowly converging gap, and that the 1/6-power correction is not theirs.

## 2. NOVEL?
Queries (WebSearch): 
1 "Dutarte conjecture 3-rank class group Q(sqrt d) Q(sqrt -3d) Spiegelungssatz numerical data"
2 "Belabas counting cubic fields 3-rank quadratic fields tables discriminant 10^10 reflection theorem Scholz"
3 "Fouvry Klueners On the Spiegelungssatz for the 4-rank Dutarte conjecture 0.29765 numerical"
4 "arXiv 3-rank class groups real imaginary quadratic fields Scholz reflection distribution computation discriminants up to 10^10 secondary term"
5 "OEIS number of real quadratic fields with 3-rank 1 discriminant up to 10^n class group 3-rank counts"
6 "mathoverflow OR math.stackexchange Scholz reflection theorem 3-rank ... proportion 3^{-(r+1)} Dutarte"
7 "Cohen-Lenstra heuristics real quadratic 3-rank statistics numerical computation 10^10 Jacobson Ramachandran Williams class group tables"
8 "Wikipedia Scholz's reflection theorem; Cohen-Lenstra heuristics; 3-rank quadratic field tables Belabas Fouvry ..."
Fetched: arXiv 2512.20023 (theory only), Belabas mean3-99.pdf (cubic field counts to 1e11; Conjecture 3.2 = Dutarte, no numerical check), FK 2010, Scheidler 3-rank-tab (function fields), Belabas r3.pdf "On quadratic fields with large 3-rank" (Math. Comp. 2004).
Findings: Belabas 2004 does test Dutarte's prediction for r=4 (real fields with r3=4 up to ~1.6e13, six of 1618 have mirror rank 5 vs ~6.7 predicted) and tabulates large-rank fields to 1e10-6.5e11. That is a published numerical test of this law, beyond 1e10, albeit for one rank and only counts, not a full proportion table. Dutarte 1984 and FK experiments are also published tests, at unknown (smaller) range; I could not open Dutarte 1984. The Leiden thesis full text (chapters) and the mean3-99 cited tables, Belabas 1997 tables, Dutarte 1984 itself, OEIS search pages (robots-disallowed), Google Scholar, MathOverflow/MSE and Wikipedia pages could not be opened directly; searches via WebSearch surfaced nothing new but that is weak evidence. Conclusion: a full exact table n(r,e;X) of all four ranks to 3.2e10 is probably new, but (d) as worded ("no table or test ... to a comparable range") is contradicted in part by Belabas 2004 and is unverified for Dutarte 1984. Not a clear yes.

## 3. HONEST?
Good: the packet states the withdrawn earlier claim, that data to 1e10 were seen, that M2 was chosen after looking, that only 5 bins are out of sample, that r=2 is fragile (fails with halved variances, M1 fails r=1), and that HELD is not confirmation. It frames the claim as about a table and a stated test.
Problems: (1) Selection: M2 has two free parameters per series fit after seeing data; the exponents -1/6, -1/3 are tuned (the earlier failure shows exponent-dependence). With 5 bins, 2 fitted parameters, a pass at p>0.01 is a very weak test: the shift intervals (+-0.0003 on 0.30) show it has power, but only conditional on the model shape; M1 failing for r=1 shows the outcome is shape dependent, which the claim concedes. 5 bins are tiny share of the data; p>0.01 threshold is permissive and set to be passable; a pass cannot "bear weight" for the conjecture. (2) Four series are correlated and the verdict "all four HELD" uses 0.01 each without multiplicity discussion; r=2 p=0.055 and halved-variance fail. (3) Halved variances are an ad hoc sensitivity (the reviewers' sqrt2 remark is unexplained; bins are exact multinomial so variance should be right) and the claim does not say which is correct. (4) Claim (c)/(d) "no comparable table or test published" overstated given Belabas 2004. (5) The packet's "Fouvry and Klueners print no data" omits their mention of experiments. (6) The compute note shifts the burden of verifying 45 of 76 rows (all rows above 1.26e6, including every out-of-sample row) to reviewers; I could only match through 1e6.

## Timings
rk 2..1e5: 6 s; 1e5+1..1e6: ~10 min (single core). test.py: seconds. No background processes remain.
