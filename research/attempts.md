# Attempts log

Append-only. One entry per daily session (see PROMPT.md, END OF DAY).

## 2026-10-14 (first session, started on request; ran into 2026-10-15 UTC)
- **Problem:** improve published lower bounds for the off-diagonal van der Waerden numbers w(2;3,t), t = 31..39
  (Ahmed-Kullmann-Snevily, arXiv:1102.5433 Table 2). Tier A.
- **Frozen definition of solved:** for some t in 31..39, an explicit 2-colouring of [1..n] with n > B_t (B_t = 930, 1006, 1063,
  1143, 1204, 1257, 1338, 1378, 1418) whose colour 0 has no 3-AP and colour 1 has no t-AP.
- **Approaches (verdicts):**
  1. Plain probSAT, no symmetry: weak (t=20 stalls below 370).
  2. Palindromic probSAT: finds the extremal w(2;3,20) > 388 in ~2 min; cb=5 much better than 2.3.
  3. Incremental palindromic climbing (insert middle bit): works but slows sharply near the palindromic maximum.
  4. Cyclic Z_p colourings constant on multiplicative cosets + CaDiCaL: ruled out, high confidence (t=5 cyclic max p=7 vs 21 linear).
  5. PAWS-style clause weighting: no better than probSAT at the frontier; dropped.
  6. Palindromic climbing with skipping (non-monotone n): t=38 to 1274, t=39 to 1322 palindromic; too slow at n ~ 1300.
  7. LNS SAT repair of near-misses: every neighbourhood up to ~60% of variables UNSAT; ruled out as implemented, moderate confidence.
  8. Palindromic seed + non-palindromic extension: the winner. Reproduced the conjectured exact w(2;3,24) > 592 in seconds from a
     564 palindromic seed. Reached t=31: 893, t=33: 1039, t=35: 1154. All short of the records.
- **Label:** NO PROGRESS. No skeptic gate run (no claim).
- **Code/data:** `research/problems/vdw-w23t-lower-bounds/` (`code/ls.c`, `code/climb*.py`, `code/verify.py`, `best/`, `notes.md`).
- **Tomorrow:** if continuing, spend the whole session on t=33 (24 short): many palindromic seeds past 1000, faster bitset
  solver, interior-insertion and backtracking extensions. Otherwise pick a different problem.

## 2026-10-15 (scheduled run)
- **Problem:** same as 2026-10-14, focused on w(2;3,33), then w(2;3,35).
- **Frozen definition:** unchanged: an explicit good 2-colouring of [1..n] with n > B_t (t=33: n >= 1064).
- **Approaches (verdicts):**
  1. Extension with interior inserts + trim-6 backtracking: 1039 -> 1046. Works where end-only extension had stalled.
  2. Trim-12 backtracking from 1046: reached 1064 (beats AKS 1063), then 1068 in three independent runs; stalled there.
  3. Palindromic seed climbs from 1000: 1002 / 1004 (inside AKS's published palindromic range); stopped as not needed.
  4. Skeptic gate on "w(2;3,33) > 1068": 3 fresh skeptics (default model, Sonnet, Fable) all REPRODUCED=YES, HONEST=YES/UNSURE,
     NOVEL=NO. OEIS A171081 has an Aug 21 2026 comment by Juan Lopez Marcano: a(31) >= 954, a(33) >= 1072 (w(2;3,33) > 1071),
     with certificates and a Zenodo preprint (10.5281/zenodo.21943191). Skeptic 1 verified the 1071 certificate. DOES NOT COUNT.
  5. Same pipeline at t=35: 1154 -> 1185 (record 1204, 19 short).
  6. Trim-20 from 1068 at t=33: no progress in 1 h.
- **Label:** NO PROGRESS. Skeptic verdicts: 0/3 sign-off (novelty).
- **Code/data:** `problems/vdw-w23t-lower-bounds/` (`code/climb_plain2.py` new; `best/`; `claims/2026-10-15-1/`).
- **Lesson:** the status check must open the OEIS A-number page directly (oeis.org/A171081 is fetchable by WebFetch even though
  OEIS search pages are not). The current records are t=31: >953, t=33: >1071 (Marcano 2026); others still AKS.
- **Ideas for tomorrow:** t=35 is 19 short with steady (slowing) gains; continue it from `best/t35_n1185.txt` with more runs
  and deeper trims, after first re-checking A171081 and the Zenodo record for any t=35 update. Or switch problem.

## 2026-10-16 (scheduled run)
- **Problem:** w(2;3,35) lower bound (record w > 1204, AKS arXiv:1102.5433; re-checked OEIS A171081, Zenodo 21943191,
  arXiv:2608.20824: nothing newer for t=35). Also reviewed `ledger/routed-open-problems.md`; did not pick a routed problem.
- **Frozen definition:** good 2-colouring of [1..n], n >= 1205, no 3-AP in colour 0, no 35-AP in colour 1.
- **Approaches (verdicts):**
  1. Trim-and-regrow from 1185 with trims 12/20/30: 1185 -> 1195 (only trim 20 moved).
  2. Restarts from 1195: -> 1197.
  3. Deeper trims 30-60 from 1197 for 90 min: nothing.
- **Label:** NO PROGRESS (best w(2;3,35) > 1197, 7 short). No skeptic gate (no claim).
- **Code/data:** `problems/vdw-w23t-lower-bounds/best/t35_n1197.txt`, `code/climb_plain2.py`.
- **Ideas for tomorrow:** after three days on w(2;3,t) this basin looks exhausted. Either restart t=35 from a much stronger
  palindromic seed (AKS palindromic range (1114,1155); ours was 1040) to reach a new basin, or switch problem (a routed
  ledger problem or another Tier A target).

## 2026-10-17 (scheduled run)
- **Problem:** w(2;3,38) and w(2;3,39) lower bounds (records > 1378 and > 1418, AKS arXiv:1102.5433; OEIS A171081 re-checked,
  no update for these t). Reason: AKS's step from t=37 to 38 to 39 is only +40, against +53..81 for t=31..37.
- **Frozen definition:** good 2-colouring of [1..n], no 3-AP in colour 0, no t-AP in colour 1, n >= 1379 (t=38) or n >= 1419 (t=39).
- **Approaches (verdicts):**
  1. Cross-t seed (the t=35-good 1197 colouring is t=38/39-good) and old palindromic seeds, trim-20 regrow: t=38 1374, t=39 1412 in 2 h.
  2. Deeper trims 40/60: t=38 1375; t=39 nothing.
  3. Four trims 20-60 on t=38 from 1375 for 90 min: nothing.
- **Label:** NO PROGRESS (t=38 3 short, t=39 6 short). No skeptic gate (no claim).
- **Code/data:** `problems/vdw-w23t-lower-bounds/best/t38_n1375.txt`, `best/t39_n1412.txt`.
- **Ideas for tomorrow:** four days on w(2;3,t) end the same way: the pipeline plateaus just below every known record.
  Switch problem. Candidates: a routed ledger problem with a computable part, or another Tier A target where the published
  search effort is thin (check OEIS first). If ever returning here, the missing ingredient is a fundamentally different
  search (e.g. a complete SAT solver on a structured sub-space), not more trimming.

## 2026-10-18 (scheduled run; cut off before END OF DAY, entry written 2026-10-21 from its notes)
- **Problem:** unknown "?" entries of Brown-Landman-Robertson's Table 1 for k = 3 (arXiv:0706.4420): w1(3,s) s >= 8, M(3,s)
  s >= 8, G(3,s) s >= 10. Tier A.
- **Frozen definition:** exact value of a "?" entry: witness of size v - 1 plus an UNSAT proof at v.
- **Approaches (verdicts):** SAT encodings for w1, M, G (worked); probSAT lower bounds for w1 (n = 192 at s = 7, stalls near 238
  at s = 8); upward SAT scan w1(3,8) (SAT to 237); 357 local-search attempts at 238 (all fail); cube-and-conquer at 238 (11/36
  cubes UNSAT, stopped); monolithic CaDiCaL proved 238 UNSAT, so w1(3,8) = 238, but NOT NEW (Ahmed 2009, Integers 9 A06, as
  wd(2;3,8) = 238). Recomputing the table disagreed with the printed M(3,4..6) and G(3,6).
- **Label:** NO PROGRESS (the one exact value found was already published). No skeptic gate.
- **Code/data:** `problems/vdw-related-functions/` (committed 2026-10-21 as work in progress).
- **Lesson:** search notation variants (w_d, "common difference at most d") in the status check.

## 2026-10-21

### 04:52 UTC (run fired on request)
- **Problem:** the M(3,s) and G(3,s) rows of BLR Table 1 (arXiv:0706.4420), following up the 2026-10-18 disagreement.
- **Frozen definition:** the correct exact value of at least one k = 3 M or G entry that is "?" or wrong in the table: witness of
  size v - 1 under the printed definition, exhaustive impossibility at v by an independent method, not published elsewhere.
- **Approaches (verdicts):**
  1. Re-read definitions and table from the arXiv PDF: quoted correctly; the disagreement is real.
  2. Plain C backtracking (`code/bt.c`): M = 7, 11, 19, 31, 38 (s = 2..6), G = 5, 9, 11, 17, 23, 33, 37 (s = 2..8).
  3. Search-shortcut hypothesis (`code/btv*.c`): forcing x_1 = 0 in M reproduces the printed M row exactly; forcing the first
     gap to 1 in G reproduces the printed G row exactly. Likely mechanism of the errors (inferred, moderate confidence).
  4. Forward-checking search (`code/fc.c`): third method, same values.
  5. CaDiCaL scans for M(3,7) from n = 46 and G(3,9) from n = 45: no result (died once, restarted, still running at log time).
  6. Skeptic gate on "M(3,4) = 19, M(3,5) = 31, M(3,6) = 38, G(3,6) = 23 (printed 18, 29, 37, 22)".
- **Label:** PROMISING. Skeptics: 1 SIGN-OFF, 2 (Sonnet) REJECT on novelty only (Landman-Robertson 2nd ed. not inspectable),
  3 (Fable) SIGN-OFF. All three reproduced every value. 2 of 3, does not count.
- **Code/data:** `problems/vdw-related-functions/` (`code/bt.c`, `code/fc.c`, `code/btv.c`, `code/btv2.c`, `claims/2026-10-21-1/`).
- **Ideas for next run:** the only open objection is the book. Find a readable copy or table of contents of Landman-Robertson
  2nd ed. (2014) sections on these functions; if it settles novelty, send a NEW claim packet to three NEW skeptics. Separately,
  finish M(3,7) and G(3,9) (printed 48 each; true values >= 46 and >= 45 from our witnesses) with symmetry-broken SAT or
  cube-and-conquer: an exact value there that differs from print would be a stronger result.

### 08:53 UTC (scheduled run)
- **Problem:** same as 04:52: BLR Table 1 (arXiv:0706.4420), now targeting M(3,7) and G(3,9) (printed 48 each).
- **Frozen definition:** unchanged from 04:52.
- **Approaches (verdicts):**
  1. Looked again for the Landman-Robertson book: its 1st ed. (2004) notation index does define the one-per-block function,
     so the book treats it; the text is unreadable here (Google Books robots-blocked). Novelty question still open.
  2. Shortcut-hypothesis predictions: restricted (first gap 1) G(3,8) = 37 and G(3,9) = 48, both equal to the printed values
     (SAT and exhaustive C, 2.0e10 nodes for s = 9). Strong support for the 04:52 explanation of the table's errors.
     Gives true G(3,9) >= 48 (47-element witness in `code/btv2_G9_gap1.log`).
  3. Resumable cube-and-conquer for unrestricted n = 48 (`code/cube1.py`, `code/runjobs.sh`): too slow, no cube finished in ~2 h.
  4. Forward-checking search for a restricted 47-block M(3,7) witness: not found in 15 min.
  5. Solver comparison: CaDiCaL 1.9.5 ~20% faster, Kissat slower and ignores assumptions in python-sat. Not worth switching.
  6. Min-conflicts local search for M witnesses: too weak beyond s = 5.
- **Label:** NO PROGRESS (no entry settled this run). No skeptic gate (no claim).
- **Code/data:** `problems/vdw-related-functions/code/` (`cube1.py`, `runjobs.sh`, `jobs1.txt`, `jobs2.txt`, `cubes/`, `fcf.c`,
  `lsM.c`, `bench/`, `btv2_G9_gap1.log`).
- **Ideas for next run:** M(3,7)/G(3,9) at 48 need a better method than plain cubes: e.g. G via a DFS that also uses the
  reversal symmetry and a "remaining length" bound, or an order/ladder encoding for M. The novelty blocker for the 04:52
  claim (the book) needs a human with the book; ask the maintainer. Otherwise consider a different problem.

### 20:53 UTC (scheduled run; ran into 2026-10-22 UTC through four container restarts)
- **Problem:** G(3,9) in BLR Table 1 (arXiv:0706.4420), printed 48.
- **Frozen definition:** unchanged from 04:52 (exact value of a wrong or "?" k = 3 M/G entry, witness + exhaustive
  impossibility, unpublished).
- **Approaches (verdicts):**
  1. Forward-checking search split on the first two gaps (`code/fcp.c`, `code/runfcp.sh`, 81 resumable cubes): at T = 48,
     2 cubes FOUND a 48-element gap-9 3-AP-free set (mirror images); at T = 49 all 81 NONE. About 4 CPU-h each.
  2. Independent plain backtracking without forward checking (`code/btv2.c`, `code/btp.c`, `code/bt_res/`, `code/btp_res/`):
     maximum 48 exactly, only for first gaps (8,1) and (9,8). Agrees with 1.
  3. Skeptic gate, claim 2026-10-21-2 "G(3,9) = 49": 3 of 3 SIGN-OFF.
  (Earlier SAT cube runs and local search from the 08:53 run were abandoned for this; the M(3,7) work did not continue.)
- **Label:** CONFIRMED. G(3,9) = 49, correcting the printed 48. Skeptics: SIGN-OFF (default model), SIGN-OFF (Sonnet),
  SIGN-OFF (Fable). Shared caveat: the Landman-Robertson book text could not be read.
- **Code/data:** `problems/vdw-related-functions/` (`witness/G_s9_48elements.txt`, `claims/2026-10-21-2/`, code above).
- **Ideas for next run:** M(3,7) (printed 48) with the same split forward-checking search (`code/fcpm.c` forces the first
  block offsets; validated on M(3,4)); then G(3,10), the first "?" entry. The 04:52 claim (M(3,4..6), G(3,6)) could go to a new
  gate with the journal-version finding added to its packet.

## 2026-10-22

### 08:53 UTC (scheduled run; ran until 20:35 UTC)
- **Problem:** M(3,7) in BLR Table 1 (arXiv:0706.4420), printed 48.
- **Frozen definition:** unchanged from 2026-10-21 04:52.
- **Approaches (verdicts):**
  1. Split forward-checking search on the first three block offsets (`code/fcpm.c`, `code/runfcpm.sh`, `runfcpm_rev.sh`,
     343 resumable cubes, `code/fcpm_res/`): FOUND at T = 48, 49 and 50 (witnesses in `witness/M_s7_48blocks.txt`,
     `witness/M_s7_50blocks.txt`, all re-checked by brute force); T = 51 all 343 cubes NONE (about 8 h on 4 cores).
  2. Driver bug found and fixed: a killed cube could leave a result file with no verdict. All result files re-checked.
- **Label:** PROMISING (not verified). M(3,7) >= 51 is certain from the witness (printed 48 is wrong); M(3,7) = 51 rests on one
  exhaustive program, with no independent check and no skeptic gate yet.
- **Correction to an earlier record:** the 2026-10-21 summaries said the printed M and G rows come out exactly from a
  search that fixes the first element (M) or first gap (G). That holds for M only up to s = 6: at s = 7 a 48-block choice
  with x_1 = 0 exists, so the shortcut does not explain the printed M(3,7) = 48. The G explanation still holds through s = 9.
- **Code/data:** `problems/vdw-related-functions/` (`code/fcpm.c`, `code/runfcpm*.sh`, `code/fcpm_res/`, `witness/`).
- **Ideas for next run:** an independent exhaustive check of T = 51 (a separately written search, ideally faster, e.g. using
  the reflection symmetry x -> 51*7-1-x to halve it), then a skeptic gate on "M(3,7) = 51". Budget: about 30 CPU-hours per
  independent check with the current method, so skeptics need a faster method or the result stays PROMISING.

### 20:53 UTC (scheduled run; ran into 2026-10-23 UTC)
- **Problem:** M(3,7) in BLR Table 1 (arXiv:0706.4420), printed 48: independent check of the 08:53 result M(3,7) = 51.
- **Frozen definition:** unchanged from 2026-10-21 04:52.
- **Approaches (verdicts):**
  1. `code/mb.c`, bitset search placing the last block first: correct on s = 2..5 but ~5x slower than fcpm. Dropped.
  2. `code/mrv.c`, most-constrained block first, all three AP roles forbidden via shifted bitsets: correct on s = 2..6, about
     as fast as fcpm with a left-most tie-break.
  3. Most-central tie-break: 3x fewer nodes on M(3,6). Outermost tie-break: far slower.
  4. Central-block cubes with the reflection symmetry (`code/mrvcubes.py`, `code/runmrv.sh`, `code/mrv_res/`), validated on
     s = 5, 6 both ways: **s = 7, T = 51 all 175 canonical cubes NONE, 6188 CPU-s (about 20x faster than fcpm)**; T = 50
     FOUND (witness re-checked). Two independently written programs now agree: M(3,7) = 51.
  5. Novelty: AMS post-publication page of the Landman-Robertson 2nd ed. lists no errata; book still unreadable.
  6. Skeptic gate, claim 2026-10-22-1 "M(3,7) = 51": 0 of 3. Skeptic 1 reproduced it fully with its own search but rejected
     on novelty (book and OEIS search unreachable); skeptic 2 could not finish the search; skeptic 3 finished 16 of 49 parts
     (all impossible) and rejected for incompleteness.
- **Label:** PROMISING (not verified). M(3,7) >= 51 is certain (witness); = 51 now rests on three independent exhaustive
  searches, but the gate did not sign off.
- **Code/data:** `problems/vdw-related-functions/` (`code/mrv.c`, `code/mrvcubes.py`, `code/runmrv.sh`, `code/checkM.py`,
  `code/mrv_res/`, `code/mb.c`, `code/mb_bench/`, `claims/2026-10-22-1/`).
- **Ideas for next run:** the remaining blocker for all three claims is the same: the Landman-Robertson book (ask the maintainer again
  only through the thread). A new gate for M(3,7) should tell skeptics the search takes 1-2 CPU-hours with a good branching
  order, so they budget for it (that is a compute note, not a method hint beyond what the packet already says). Otherwise move
  to G(3,10), the first "?" entry, where `mrv`-style ordering may also help.

## 2026-10-23

### 08:53 UTC (scheduled run)
- **Problem:** G(3,10), the first "?" entry of the G row in BLR Table 1 (arXiv:0706.4420). Status check: no source gives a
  value (Brown-Hare 1997, which defines G(k;r), gives only asymptotic bounds).
- **Frozen definition:** unchanged from 2026-10-21 04:52 (witness of size v - 1 plus exhaustive impossibility at v, unpublished);
  a witness alone is a sub-result.
- **Approaches (verdicts):**
  1. `code/gm.c`, middle-out search from the middle element, extending the more constrained side: correct on G(3,2..8); about
     as fast as fcp alone.
  2. Lmin span bound (`code/lmin.c` computes Lmin(1..30), matching OEIS A065825; `lmin_oeis43.txt` adds A065825's terms to 43):
     4x fewer nodes at s = 9. Kept.
  3. Reversal symmetry for odd T (`code/gmcubes.py`, `code/rungm.sh`, `code/gm_res/`): validated at s = 8; **G(3,9), T = 49:
     45/45 cubes NONE in 3387 CPU-s**, a third independent exhaustive check of G(3,9) = 49, 4x cheaper than fcp.
  4. Serial witness search for s = 10 (`code/gm10/probe.txt`): witnesses up to 54 elements (`witness/G_s10_54elements.txt`),
     so **G(3,10) >= 55**. T = 55 undecided in 600 s.
  5. T = 55 by capped cubes: 3 cubes NONE, 7 hit the 15 min cap; full decision estimated at 30-80 CPU-hours. Stopped.
  6. T = 55 witness hunt with four search orders (incl. randomised), 50 min each: nothing.
- **Label:** PROMISING (sub-result): G(3,10) >= 55, a lower bound for an entry the table leaves open; exact value not reached.
  No skeptic gate (no full claim).
- **Code/data:** `problems/vdw-related-functions/` (`code/gm.c`, `code/lmin.c`, `code/lmin_*.txt`, `code/gmcubes.py`,
  `code/rungm.sh`, `code/checkG.py`, `code/gm_res/`, `code/gm10/`, `witness/G_s10_54elements.txt`).
- **Ideas for next run:** G(3,10) needs about 10x more pruning before an exhaustive run fits in a session: e.g. a bitset
  rewrite of gm (2-3x), a gap-bounded analogue of Lmin (least span of a k-element 3-AP-free set with gaps <= 10, likely far
  above Lmin for large k, judging by the witness), or a SAT/cube hybrid on the hardest cubes. Witness side: a 55-element set
  may still exist; try local search seeded from the 54-element witness. The book remains the blocker for the earlier claims.

### 20:53 UTC (scheduled run)
- **Problem:** G(3,10) in BLR Table 1 (arXiv:0706.4420), "?" in print; lower bound 55 from the 08:53 run.
- **Frozen definition:** unchanged from 2026-10-23 08:53.
- **Approaches (verdicts):**
  1. Exact least spans of gap-bounded 3-AP-free sets, H_10(1..29) (`code/hmin.c`, validated on s = 4, 5): within ~5% of Lmin.
  2. That bound in gm.c: no speed-up (732 s vs 730 s on the same cube). Ruled out, high confidence.
  3. Hole refilling (`code/regrow.c`): 54 -> 55 -> 56 elements. **G(3,10) >= 57** (`witness/G_s10_56elements*.txt`, checked).
     Sanity: on s = 9 it finds nothing past the known maximum 48.
  4. Repeated refilling from four different starts (`code/climb.sh`): all stop at exactly 56; holes up to 45 tried on one set.
  5. Plateau moves (same-size refills): no alternative refill for any hole up to 14 elements; the sets are locally rigid.
  6. Timing sample for the T = 57 exhaustive check: one cube 734 s, two over 1500 s; tens of CPU-hours in all. Not run.
- **Label:** PROMISING (sub-result): G(3,10) >= 57, up from 55 this morning; four independent climbs stopping at 56 suggest
  G(3,10) = 57, but there is no impossibility proof. No skeptic gate (no full claim).
- **Code/data:** `problems/vdw-related-functions/` (`code/hmin.c`, `code/hmin10.out`, `code/mergeLM.py`, `code/lm_s10.txt`,
  `code/regrow.c`, `code/climb.sh`, `code/climb10*/`, `code/regrow_out/`, `witness/G_s10_5[56]elements*.txt`).
- **Ideas for next run:** the exact value needs an exhaustive "no 57-element set" check, tens of CPU-hours with gm. Options:
  run it across runs as resumable cubes (results persist in `code/gm_res/`), or find a stronger pruning idea first (a bitset
  gm for 2-3x; a SAT solver on the hardest cubes). Otherwise turn to another table entry.

## 2026-10-28

### 21:32 UTC (fired on request)
- **Problem:** first G(3,10) at T = 57 (BLR Table 1, "?"), then w*(3;5) in the same table (printed ">= 75"), a new problem.
- **Frozen definition:** G(3,10) unchanged from 2026-10-23; w*(3;5) frozen in `problems/wstar/notes.md` (a 74-colouring
  plus an exhaustive, recorded check at 75).
- **Approaches (verdicts):**
  1. Timing sample of the G(3,10), T = 57 exhaustive check with gm.c (`vdw-related-functions/code/sample57/`): 90+ CPU-hours.
     Not run. A bitset gm (`code/gmb.c`) gives the same node counts, slower. Dropped.
  2. Switched to w*(3;5). SAT encoding (`wstar/code/wstar_sat.py`) with an independent checker (`code/check_wstar.py`);
     reproduces w*(3;3) = 23 and w*(3;4) = 40.
  3. Tabu local search (`code/wls.c`): weak, best 13 conflicts at n = 74. Ruled out.
  4. Symmetric colourings: colour(i) = 6 - colour(75 - i) gives a valid 74-colouring (`runs/pal74.txt`), reproducing the printed
     bound; neither symmetric type exists for n = 75..78.
  5. Seed extension (`code/wext.py`): every central placement of the 74-colouring's middle block is UNSAT at 75 and 76.
  6. Cube split on central positions (`code/wcube.py`, validated on r = 3, 4): width 5 leaves pieces of 20+ min; width 7 has
     7687 pieces, 20 sampled all UNSAT at 60 s average, about 128 CPU-hours for the full check. Not run.
- **Label:** NO PROGRESS on either open entry: the printed w*(3;5) >= 75 is reproduced, not improved, and the evidence that it
  equals 75 is partial. No skeptic gate (no claim).
- **Code/data:** `problems/wstar/` (all), `problems/vdw-related-functions/code/sample57/`, `code/gmb.c`.
- **Ideas for next run:** the w*(3;5) = 75 proof is the cheapest exact result in reach: run `wcube.py 5 75 7 runs/c5_75w7 j 4`
  across several runs (it resumes from saved pieces; commit `runs/c5_75w7/` each time), or first cut the cost with stronger
  symmetry breaking or a dedicated solver. G(3,10) = 57 needs 90+ CPU-hours with current tools.

## 2026-10-29

### 08:53 UTC (scheduled run)
- **Problem:** w*(3;5) in BLR Table 1 (arXiv:0706.4420), printed ">= 75". Status check: no other published value found.
- **Frozen definition:** as in `problems/wstar/notes.md` (good colouring of [1, N-1] plus a recorded exhaustive check at N,
  unpublished).
- **Approaches (verdicts):**
  1. Direct DFS with forward checking (`wstar/code/wdfs.c`): validated on 9, 23, 40; 30x faster than CaDiCaL on sampled cubes.
  2. Resumable cube runs (`code/rundfs.sh`, `code/wdcubes.py`): n = 75 has good colourings (`witness/wstar_r5_n75.txt`);
     **n = 76: all 97,969 cubes NONE, 4.3 CPU-h** (`runs/d5_76w8_all.txt.gz`).
  3. SAT cross-check of 32 n = 76 cubes (10 hardest + 22 random): all UNSAT, agreeing.
  4. Plain backtracking cross-check (`code/wbt.c`): too slow on hard cubes. Dropped.
  5. Six colours by anti-symmetric SAT: good 82-colouring, so **w*(3;6) >= 83** (table "?"); 84+ timed out.
  6. Skeptic gate, claim 2026-10-29-1 "w*(3;5) = 76".
- **Correction found by the gate:** the lower bound w*(3;5) >= 76 is classical: {1,2,4,5} is a 3-AP-free colour set, so
  W(3;4) = 76 (Beeler-O'Neil 1979) gives it directly, and our 75-colouring is a recoloured 4-colouring. The printed ">= 75"
  was weaker than a known bound. Only the upper bound (no good 5-colouring of [1, 76]) is new.
- **Label:** PROMISING (not verified). Skeptics: 1 (default model) REJECT, own search stopped at about 10% of the tree,
  nothing found; 2 (Sonnet) SIGN-OFF, own exhaustive search of [1, 76] finished (8.2e10 nodes, 3.2 h) with none found;
  3 (Fable) REJECT, could not finish a search in time. 1 of 3: does not count. Novelty: no prior value found by any
  skeptic, but the Landman-Robertson book, Google Scholar, OEIS search and MathOverflow search could not be opened.
- **Code/data:** `problems/wstar/` (`code/wdfs.c`, `code/rundfs.sh`, `code/wdcubes.py`, `code/wbt.c`, `runs/d5_7*`,
  `runs/sat_check76.txt`, `runs/pal6_scan*.txt`, `witness/`, `claims/2026-10-29-1/`).
- **Ideas for next run:** a new gate on "w*(3;5) <= 76" (the packet should state the classical lower bound and give a
  realistic compute note: naive SAT and plain backtracking do not finish; a strong search takes 3-5 CPU-hours, so skeptics
  need the whole session and resumable jobs). Then w*(3;6): push the lower bound past 83 (non-symmetric search seeded
  from the 82-colouring), with the exact value likely far out of reach.
- **Process lesson:** grepping /proc/*/cmdline of bash processes for a pattern also matches the calling shell; it killed this
  run's shell once. Kill only by PID of the named binary (pgrep -x), or by a PID saved at launch.

### 20:53 UTC (scheduled run; ran into 2026-10-30 UTC through two container restarts)
- **Problem:** w*(3;5) in BLR Table 1 (arXiv:0706.4420): a fresh gate on the 08:53 result w*(3;5) = 76 (new part: <= 76).
  Status re-checked by web search: nothing newer than ">= 75".
- **Frozen definition:** unchanged from 2026-10-28 (`problems/wstar/notes.md`).
- **Approaches (verdicts):**
  1. Revised claim packet 2026-10-29-2: states the classical lower bound (W(3;4) = 76) and a realistic compute note
     (several hours, resumable, relaunch allowed).
  2. Skeptic gate with three fresh skeptics (none from 2026-10-29-1).
  3. Six colours, anti-symmetric class (`code/wdfs.c`, WDFS_ANTI=1): exhaustive within the class, none at 84, 86, 88, 90.
  4. Six colours, palindromic class (WDFS_ANTI=2): none at 83..88.
  5. Six colours, long anti-symmetric SAT at 84 (2 h): timed out; superseded by 3.
- **Label:** PROMISING (not verified). Skeptics: A (default model) SIGN-OFF, own exhaustive search complete, none found;
  B (Sonnet) REJECT, search not finished (0% proven coverage, about 8 CPU-h lost to two restarts); C (Fable) REJECT, search
  not finished (0.5% coverage by its fastest method, projected about 340 CPU-h). 1 of 3: does not count. Over both gates two
  independent complete searches (Sonnet at 08:53, default model now) agree with ours; no skeptic found a prior publication,
  none could open the Landman-Robertson book.
- **Code/data:** `problems/wstar/` (`claims/2026-10-29-2/`, `code/wdfs.c`, `runs/anti6_dfs.txt`, `runs/pal6_dfs.txt`,
  `runs/pal6_84_long.txt`).
- **Ideas for next run:** the gate keeps failing on compute, not on findings: skeptics' first methods (SAT, plain DFS) need
  tens to hundreds of CPU-hours and hourly container restarts kill long jobs. A packet may not hint at our method, so a
  future gate needs skeptics with resumable designs from the start; or leave w*(3;5) as PROMISING and move on. Six colours:
  a non-symmetric search seeded from the 82-colouring for w*(3;6) >= 84.

## 2026-10-30

### 08:53 UTC (scheduled run)
- **Problem:** M(3,8) in BLR Table 1 (arXiv:0706.4420), printed "?". Status check: no later value found by web search.
- **Frozen definition:** unchanged from 2026-10-21 04:52 (witness of T - 1 blocks plus exhaustive impossibility at T,
  unpublished); a witness alone is a sub-result.
- **Approaches (verdicts):**
  1. Plain SAT per T (`code/sat_funcs.py`): witnesses at 50, 51, 52 blocks; 53 and 56 undecided in 20 min.
  2. SAT window climbing with new blocks at the end (`code/mclimb.py`): stuck at once. Ruled out as built.
  3. `mrv` with wider bitsets (`code/mrv16.c`, validated on M(3,5), M(3,6)) as a complete cube climber
     (`code/runmrv16.sh`, `code/mclimb_mrv.sh`): witnesses at 53, 54, 55, 56 blocks.
  4. Coarse exhaustive cubes at T = 57: 1.5 h per cube without finishing. Stopped.
  5. Finer cost sample at T = 57 (5 central blocks fixed): about 1,200 CPU-hours for the full check. Out of reach.
  6. SAT extension with the witness shifted one block right and its centre fixed (`code/mext.py`): **a valid 57-block
     choice at once, so M(3,8) >= 58**; T = 58 UNSAT with 8 to 40 central blocks fixed, smaller centres undecided.
- **Label:** PROMISING (sub-result): M(3,8) >= 58 for an entry the table leaves open; exact value not reached. No skeptic
  gate (no full claim). All witnesses checked by `checkM.py`.
- **Code/data:** `problems/vdw-related-functions/` (`code/mrv16.c`, `code/runmrv16.sh`, `code/mclimb_mrv.sh`,
  `code/mclimb.py`, `code/mext.py`, `code/mext_climb.sh`, `code/m8/`, `code/mrv16_res/`, `witness/M_s8_5[2-7]blocks.txt`).
- **Ideas for next run:** M(3,8) = 58 would need an exhaustive "no 58-block choice" proof, likely thousands of CPU-hours
  with mrv; a sharper bound (e.g. an Lmin-style span bound per block, as gm uses for G) is the first thing to try. A 58-block
  witness may still exist: run mext with shifts of 2+ blocks or with the 55/56-block witnesses as seeds.

## 2026-11-24

### 08:53 UTC (scheduled run; write-up finished at the 20:53 firing)
- **Problem:** the 3-rank reflection law for quadratic fields (ledger row UQ-20261028-02, aggregate limb only). For a
  positive fundamental discriminant d with r = 3-rank of Q(sqrt d) and r' = 3-rank of its mirror field, Scholz gives
  r' - r in {0, 1}; the conjecture (Dutarte 1984; Fouvry-Klueners 2010, Conj. 1.1) is P(r' = r + 1 | r) = 3^-(r+1),
  aggregate 0.29765117. Status check: Fouvry-Klueners print no data, Dutarte tested 2 x 1000 discriminants, Belabas 2004
  one count (6 against 6.7). No later numerics found; Sawin-Wood sections 9, 11, 12 unread.
- **Frozen definition:** exact table n(r, e; X) to X_max >= 10^9, every cubic-field count of the form (3^r - 1)/2 and no
  Scholz violation, plus a pre-set test (bins between checkpoints 10^(k/10) above 10^6, weighted fit
  p = p_inf + c x^(-1/6), CONSISTENT within 3 se, VOID if chi2/dof > 2), and not already published.
- **Approaches (verdicts):**
  1. Class groups per discriminant with PARI: `pip install cypari` was denied by the session's permission rules; not
     worked around. The per-group limb of the ledger row is therefore not attempted.
  2. Count cubic fields by reduced binary cubic forms (Belabas 1997), `code/cubic.c` + `code/stats.c`: validated on known
     discriminants; 303,963,559 pairs to 10^9 in 112 s, 0 bad counts, 0 violations.
  3. Pre-set test at 10^9 (`code/fit.py`): all four limits CONSISTENT (aggregate 0.297772 +- 0.000139, r=0 0.333524 +-
     0.000155, r=1 0.111633 +- 0.000240, r=2 0.036982 +- 0.001111). Deviation disclosed: variance at (s + 1/2)/(n + 1)
     after a zero-success bin broke the r = 2 fit.
  4. Memory-compact rewrite `code/cubicx.c` to 10^10: 3,039,635,379 pairs, 897,388,600 with r' = r + 1, 0 bad, 0
     violations. Same test: aggregate, r=0, r=2 CONSISTENT; **r=1 0.111415 +- 0.000073, z = +4.2, INCONSISTENT with the
     one-term model.**
  5. Post hoc (not pre-set): the r=1 z falls to +2.8 and +1.4 when the fit starts at 10^8 and 10^9; a two-term model
     (x^-1/6 and x^-1/3) puts all four within 0.25 se. Suggestive only.
- **Label:** PROMISING (not verified). Gate on the 10^9 table and test: skeptic 1 (default model) SIGN-OFF; skeptic 2
  (Sonnet) REJECT; skeptic 3 (Opus) REJECT. 1 of 3: does not count. All three reproduced the table as far as they
  computed (two to all 61 rows, skeptic 3 also the 10^10 table) and the test values to every digit. The rejections are on
  the statistics: the verdict holds only for an exponent near 1/6, chi-squares are too low (errors about sqrt 2 too
  large; rescaled, r=1 fails already at 10^9), and reporting 10^9 when 10^10 fails is a stopping point chosen after the
  fact. Accepted: the result of record is the 10^10 one. The exact table stands; the claim "consistent with the
  conjecture" is withdrawn; nothing here refutes the conjecture either.
- **Code/data:** `problems/spiegelung-3rank/` (`notes.md`, `code/`, `table_1e9.csv`, `table_1e10.csv`,
  `claims/2026-11-24-1/` with three skeptic folders).
- **Ideas for next run:** the test design was the weak point, not the data. Either find the proven or conjectured
  secondary terms for the two 3-torsion averages (Roberts' x^(5/6) term is for the first moment; the r-conditional
  laws have no known second term) and pre-register a model from theory, or drop extrapolation and test a quantity with a
  known finite-X prediction. Per-group limb needs PARI or a hand-written class group structure routine.

### 20:53 UTC (scheduled run)
- **Problem:** same law as 08:53 (3-rank reflection, P(r' = r + 1 | r) = 3^-(r+1)); this run's question: does the
  conjectured limit with two correction terms fitted below 10^10 predict the unseen range (10^10, 10^10.5]? Status check
  repeated by web search: no new numerics found.
- **Frozen definition:** exact table to X_max = round(10^10.5) with no Scholz violation; out-of-sample prediction test
  fixed and committed (9c20436a, 0dbfa010) before counting: M2 p = p_conj + c1 x^(-1/6) + c2 x^(-1/3), p_conj fixed, fit
  on (10^6, 10^10], chi-square statistic on the 5 new bins, HELD if p > 0.01; comparator M1; sensitivity with halved
  variances and shift intervals; not already published.
- **Approaches (verdicts):**
  1. Windowed, resumable counter (`code/cubicw.c`): matches the 10^9 and 10^10 tables exactly; 9,612,171,555 pairs to
     10^10.5, 0 violations.
  2. Theory for a second term (Bhargava-Taniguchi-Thorne error X^(2/3)): motivates x^(-1/3); abstract only.
  3. Backtest (fit to 10^9, predict to 10^10): M2 held; not out of sample.
  4. Frozen test: **M2 HELD for all four series** (p = 0.917, 0.650, 0.514, 0.055); M1 FAILED for r = 1.
  5. Variance sensitivity: with halved variances r = 2 FAILS (one bin at -2.9); the calibrated reading for r = 2 is
     "failed". Shift intervals: the test pins the limits only to about +-3e-4 (r = 2: +-1e-3).
  6. Morning one-term fit on the longer table: r = 1 now 6.5 se off. Ruled out for good.
- **Label:** PROMISING (not verified). Skeptics 0 of 3: all three REJECT. Two rebuilt all 76 rows exactly with their
  own programs and all three reproduced every test figure. All three reject on novelty as worded: Belabas, Math. Comp. 73
  (2004) section 5.2 is a published test of this law (r = 4 slice, to 1.6e13) and the packet did not cite it, an omission
  of ours since the morning status check had it. Two also find the test too weak to carry weight (model chosen after
  seeing data below 10^10, 5 bins, r = 2 dependent on the variance model). One would sign off on a restricted novelty
  clause; not re-asked.
- **Code/data:** `problems/spiegelung-3rank/` (`code/cubicw.c`, `code/statw.c`, `code/runw.sh`, `code/predict.py`,
  `table_1e10.5.csv`, `predict_1e10.5.txt`, `backtest_fit1e9_predict1e10.txt`, `claims/2026-11-24-2/`).
- **Ideas for next run:** the data are no longer the issue (three independent rebuilds); the statistical framing is.
  A fresh gate would need a new packet that cites Belabas 2004, Kraft-Washington 2007 and Fouvry-Klueners' remark, claims
  only the table for r <= 3, and uses calibrated variances; that is bookkeeping, not research, so prefer a new problem
  unless someone wants the table published. Kraft-Washington 2007 should be read first: it may already contain a joint
  test. The windowed counter makes 10^11 a 4-hour job if ever needed.

## 2026-11-25

### 08:53 UTC (scheduled run)
- **Problem:** extend OEIS A304884, the size a(n) of the largest subset of the cyclic group Z_n with no nontrivial
  3-term arithmetic progression (x + z = 2y mod n, not all equal). Status check: OEIS lists a(1)..a(79) (Resta 2018,
  b-file to 79); Halbeisen and Halbeisen 2005 give values up to n = 36; no other table found.
- **Frozen definition:** exact a(80)..a(90) at least, each with a witness and an exhaustive proof of the upper bound by
  two programs sharing no search code, both reproducing a(3)..a(79); not already published.
- **Approaches (verdicts):**
  1. Russian-doll search (`code/rds.c`): correct on known terms, 134 s at n = 79, too slow alone.
  2. Split-point bound added (`code/rds2.c`): 3 times faster; a(80)..a(100) in about 3 CPU-hours.
  3. Affine-symmetry decision program with gcd case split and packing bound (`code/sym.c`): all 77 known terms in 5 s,
     a(80)..a(100) in 96 s. Agrees with 2 on all 21 terms.
  4. Distinct-element variant against A341584 (n = 3..56): 0 differences.
  5. Literature definitions compared (Halbeisen 2005 same function; Csajbok-Nagy different convention).
  6. Single-program extension a(101)..a(112): not claimed.
- **Result:** a(80..100) = 15, 16, 16, 16, 16, 17, 16, 16, 16, 16, 16, 17, 16, 17, 16, 17, 17, 17, 16, 17, 17.
- **Label:** CONFIRMED. Skeptics 3 of 3 SIGN-OFF (default model, Sonnet, Opus): each checked all 21 witnesses and proved
  all 21 upper bounds with its own exhaustive program, after matching OEIS for n = 3..79. Caveat from all three: novelty
  is "nothing found"; OEIS full-text search, Google Scholar and Math StackExchange question 4012158 were unreachable.
- **Code/data:** `problems/cyclic-3ap/` (`notes.md`, `code/`, `runs/`, `claims/2026-11-25-1/`).
- **Ideas for next run:** cross-check a(101)..a(112) with a faster second program (rds2 is too slow there; a symmetry
  program written differently would do) and widen the masks past n = 127; the same machinery extends A341584 (distinct
  elements, stops at 80) and the r = 4, 5 analogues alpha(n, r) of Halbeisen. Submitting terms to OEIS is the maintainer's call.
