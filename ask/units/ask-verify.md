# ask-verify: open one source and check it

**Input:** `inputs.citation` and `inputs.claim_in_record`. **Replicas:** usually 1; library units 2.
**Independence:** not the contributor whose record cited it. **Cost:** minutes to an hour. This is the unit that most
needs people: a source behind a paywall or on a library shelf is one an AI agent cannot open.

```json
"opened": true,
"access_route": "where you read it: publisher page, arXiv html, library copy, ...",
"locus": "page, section, table or figure",
"quote": "the exact line that settles it",
"finding": "Supports | Partly | Contradicts | Unreachable",
"note": "what the record said, and what the source actually says"
```
A source you could not open is `opened: false`, `finding: Unreachable`, and that is a useful record too. It is kept
and credited but does not fill the unit: the unit stays open for someone who can reach the source, and closes as
unreachable only when two different contributors have failed. An unopened source does not end the matter for the
question: under `LEDGER.md` Gate 5 ('What "the complete search record" means') the judge may still validate an entry
that names the source and argues, from a page that was fetched, why it cannot change the novelty grade. So if you
could reach an abstract, a table of contents or a review, quote what it shows in `note`; that is what the argument
will rest on. Two kinds of source must be read and cannot be argued: the nearest prior, and a source whose stated
subject is both the question's object and its phenomenon.
