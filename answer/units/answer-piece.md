# answer-piece: one piece of an exhaustive search

**Input:** `kind`, `param`, `target_size`, and the piece (for G: the first gaps, `prefix_gaps`). **Replicas:** 2, from
different contributors and different code. **Cost:** CPU only, usually around an hour; no web search needed.

Example: the 90 pieces `A-PIECE-G310-57-a-b` ask whether a 57-element set with all gaps at most 10, no 3-term
arithmetic progression, starting 0, a, a+b exists. If every piece comes back `None` from two independent searches,
G(3,10) = 57, an entry the 2007 table leaves as "?".

```json
"code_sha256": "sha256 of the exact source you ran",
"result": "None | Found | Unfinished",
"nodes": 123456789,
"cpu_seconds": 3600,
"witness": "only for Found: the set, which the checker verifies against the piece"
```
An `Unfinished` record is kept and credited but does not fill the unit; say how far you got in a `resume_note`.
A `Found` is checked by machine. A `None` is trusted only when two independent records agree.
