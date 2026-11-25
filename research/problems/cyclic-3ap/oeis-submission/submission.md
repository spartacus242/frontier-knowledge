# OEIS A304884: proposed edit (terms a(80) to a(100))

Everything needed for the edit is in this folder. OEIS edits are made by a logged-in contributor under their own real
name, so this has to be entered from the maintainer's own OEIS account; nothing here has been sent to OEIS.

## Steps
1. Log in at https://oeis.org (register first if needed; new accounts are approved by hand, which can take a day or two).
2. Open https://oeis.org/A304884 and click "edit".
3. LINKS section: replace the b-file. Upload `b304884.txt` from this folder with the line
   `<your name>, <a href="/A304884/b304884.txt">Table of n, a(n) for n = 1..100</a> (terms 1..79 from Giovanni Resta)`
4. LINKS section, optional: upload `a304884_sets.txt` with the line
   `<your name>, <a href="/A304884/a304884.txt">Sets of size a(n) for n = 80..100</a>`
5. EXTENSIONS section, add: `a(80)-a(100) from <your name>, Nov 25 2026` (use the date of submission; if the editors
   prefer the terms only in the b-file, drop this line and keep the DATA section as it is).
6. COMMENTS section, optional, add:
   `a(n) is the function alpha(n, 3) of Halbeisen and Halbeisen. For n = 81..84, 86..90, 92, 94 and 98 the 16 nonnegative integers below 41 whose ternary expansion has only digits 0 and 1 form a set of maximum size. - <your name>, Nov 25 2026`
7. In the edit summary / pink box, say how the terms were obtained, for example:
   `a(80)-a(100) found by exhaustive computer search (branch and bound using the affine symmetries x -> u*x + t of Z_n), cross-checked by a second independent search and by three further independently written programs; all programs reproduce a(3)-a(79). Computed with AI assistance (Claude); code at <repository link if public>.`
8. Submit ("These changes are ready for review"). An editor reviews it; answer any question in the pink discussion box.

## Things to know before submitting
- Say plainly that the work was AI-assisted. OEIS editors scrutinise such submissions; check the current contributor
  guidance on the OEIS wiki before submitting. The values themselves are exact and reproducible.
- The repository is private, so an editor cannot see the code through a link. Either leave the link out or paste a
  program into the PROG section (`code/sym.c` is the short, fast one).
- Novelty rests on "nothing found": OEIS full-text search and Google Scholar could not be reached from the research
  environment. Searching OEIS for the new terms as a subsequence before submitting takes a minute and closes that gap.
- The entry's a(2) = 2 does not follow from its own definition (which gives 1). Not part of this edit; an editor may
  raise it.

## The new terms
a(80..100) = 15, 16, 16, 16, 16, 17, 16, 16, 16, 16, 16, 17, 16, 17, 16, 17, 17, 17, 16, 17, 17
