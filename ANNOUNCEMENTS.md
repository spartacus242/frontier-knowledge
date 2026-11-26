# How results are announced

This project does not announce that a problem is solved until people outside it have accepted the result. Until
then it publishes the claim, the witness, the code, every record for and against, and where the claim stands on
the ladder below. Being open about status is not an announcement; it is what lets a stranger check the work.

The reasons are in the public record. Several AI-assisted "solutions" of open problems announced in 2025 and 2026
were correct mathematics that had been in the literature for decades, and "open" on a problem list often means
only that its keeper has not seen the paper. Results announced by post or press release before review have cost
their authors, in mathematics and in physics, more trust than the results earned.

## The ladder

Every claim in `answer/results.json` sits on exactly one rung. The rung fixes the words the project uses about it.
A claim moves up only on a record in this repository, and it can move down.

| Rung | What it takes | What the project says |
|---|---|---|
| 0. Lead | A claim with a witness or a program, not yet through the skeptic gate | "Lead, not confirmed" |
| 1. Confirmed inside the project | 3 of 3 fresh-context skeptics, each with an independent program or proof check | "Confirmed inside the project" |
| 2. Reproduced outside | The required outside reproductions are accepted on the board, from people who did not produce the claim, and the literature check is finished, including every source that was hard to reach | "Independently reproduced, awaiting expert review" |
| 3. Reviewed by experts | The people who posed the problem, a named specialist, or a curated database's editors have accepted it in writing | "Reviewed by ...", naming them only with their agreement |
| 4. Accepted | Published after peer review, or a formal proof checked by a proof assistant and read by a specialist | "Solved" or "corrected", with the citation |

- **Refutation beats everything.** One sound outside record that refutes a claim marks it withdrawn the same day.
  Withdrawn claims stay on the tracker with the reason.
- **Correct is not the same as new.** Until the posers or a curated record confirm that a result is new, the
  wording is "we have not found this published", never "first".
- **A database with its own editors is a review, not an announcement.** New terms may be submitted to OEIS from
  rung 1; the editors' approval moves the claim to rung 3.

Rungs 0 to 2 are computed from the records by `verify/site_data.py`. Rungs 3 and 4 are set by a maintainer, by
pull request, with the reviewer or the citation written into `answer/results.json`.

## Importance

Each claim also carries one of four labels, set by a maintainer:

1. **Well-known problem**: settles or bounds a problem in `problems/open.json`.
2. **Open in the literature**: answers something a published source explicitly left open.
3. **Correction**: shows a published value is wrong.
4. **Extension**: adds data beyond a published record.

The tracker sorts by rung first and importance second, so an important claim that nobody has checked never sits
at the top.

## Who is contacted, and in what order

1. The people who posed the problem, or the authors of the value being changed: privately, at rung 2.
2. One or two specialists on that exact problem, if the posers do not answer.
3. The curated record for that kind of result, where one exists (for example OEIS for integer sequences).
4. A preprint server, at rung 3, with the use of AI described and a human author responsible for every line.
5. A journal.

Learned societies are not contacted. They publish journals and run meetings; they do not rule on claims sent by
email. Outside contact is made by a maintainer in person. No automated job or agent in this project emails anyone,
and contributors are asked not to write to researchers in the project's name.

## Credit

Everyone whose accepted record bears on a claim is credited on that claim, from the first record and at every
rung. Credit comes from the records in this repository and from nothing else, so nobody has to ask for it and
nobody can award it to themselves.

- **What earns credit.** Asking the question, researching prior work, challenging it, checking the literature,
  attempting an answer, searching a piece of a split computation, reproducing a result, and refuting one. A
  refutation earns the same standing as a confirmation, and an honest "could not finish" is credited as
  inconclusive.
- **Where it shows.** On the results tracker, under each claim, by GitHub handle with what each person did.
  `python3 verify/site_data.py --credits` prints the same list as one sentence per claim.
- **When a result is announced.** Every note to a problem's posers, database entry, preprint and site
  announcement about a claim carries that sentence, so everyone with a record on it is named. Entries are listed
  by role and number of records, never by seniority.
- **Your name instead of your handle.** Credit is by handle unless you add a line for yourself to
  `CONTRIBUTORS.json` (`"your-handle": "Name as it should appear"`) by pull request from that account. You can
  remove it the same way. A handle is never matched to a real name by anyone else.
- **Credit is not authorship.** A paper's authors are the people who take responsibility for all of it. Anyone
  whose record supplied an idea, a proof step or a search the result rests on is offered authorship and must
  agree in writing before being listed; everyone else with a record is named in the acknowledgements. AI tools
  are described in the methods and are not authors.
- **Credit stays.** If a claim is withdrawn, the people who checked it remain listed, and the person who refuted
  it is listed first.

## What is never announced before outside review

- "Solved", "proved" or "breakthrough" for a well-known named problem.
- "First", "new" or "previously unknown".
- Anything in medicine or biology that a reader could act on.
- Any press, social media post or newsletter about a result that has no preprint or database entry a reader can check.
- A result resting on one program or one model family.
- A proof that no person and no proof assistant has checked.
- An expert's name as reviewer or supporter without their written agreement.
- A claim of priority over work someone described in private.

## If you think a claim here is wrong or already known

Open an issue with the reference or the counterexample. A pointer to earlier work is as welcome as a
reproduction, and it is recorded on the tracker the same day.
