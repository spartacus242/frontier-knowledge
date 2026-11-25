# Contributing

`verify/check.py` enforces everything marked **(checked)**. A pull request that breaks one is refused automatically.

## A submission
- One pull request adds exactly one new file, `<area>/submissions/<unit>/<your GitHub handle>.json` (area is `ask` or `answer`), and changes nothing
  else. **(checked)**
- The file is named for the pull request's author. You cannot submit for someone else. **(checked)**
- The record works the unit's statement exactly as posted, proven by its sha256. **(checked)**
- The record has every field its unit guide in `ask/units/` or `answer/units/` lists. **(checked)**
- At most 512 KB. **(checked)**

## Independence
- You may not take a unit that checks a record you submitted. **(checked)**
- A unit wants a set number of records from different handles; a full unit refuses more. **(checked)**
- Start each unit in a fresh session that has seen only the unit's inputs, and say so with `fresh_context: true`.
  This one is on your honour; it is the reason the system works.
- One person, one handle. Sock-puppet handles used to satisfy independence get every record they touched removed.

## Sources
- Every citation has an exact identifier (`doi:`, `arxiv:`, `isbn:` or `url:`), first author, year and title. DOIs
  and arXiv ids are resolved and their titles compared. **(checked)**
- Never guess an identifier or a quote. A source you could not open is reported as unopened, and that is fine.
- A kill needs a source you opened and quoted, or an explicit `own_reasoning: true`. **(checked)**

## Content
- Questions in biology and medicine are about mechanisms. Nothing that makes a pathogen, toxin or weapon easier to
  produce or use; maintainers remove such candidates and the records attached to them.
- No issues or pull requests other than records for units you hold. Discussion goes in Discussions.

## Changing the rules
`LEDGER.md`, `PROMPT.md`, the unit guides, the queues and `verify/` change only through pull requests approved by a maintainer listed in
`MAINTAINERS`. A rule change says why, in the file itself, as `LEDGER.md` already does.

## Conduct and security
How people are expected to treat each other is in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). To report a security
problem privately, see [SECURITY.md](SECURITY.md).
