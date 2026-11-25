# answer-reproduce: independently re-check a claimed result

**Input:** a claim stated as "there is no object of size `target_size`", with `kind` (G, M or W) and `param`, and the
known witness one size smaller in `answer/witness/`. **Replicas:** 2 or 3, from different contributors.
**Cost:** stated in `inputs.expected_cost`.

Write or choose your own program. Do not run the claim's original code: the point is a second, independent search.
Check the known witness with `python3 verify/witness.py <kind> <param> answer/witness/<file>` first.

```json
"method": "what your search does, how it splits the work and how it uses symmetry",
"independent": true,
"code_url": "optional link to your code",
"code_sha256": "sha256 of the exact source you ran",
"result": "Confirms | Refutes | Unfinished",
"cpu_hours": 3.2,
"witness": "only for Refutes: the object, which the checker verifies",
"resume_note": "only for Unfinished: how far you got, so the next person can continue"
```
An `Unfinished` record is kept and credited but does not count as a reproduction.

Make your run resumable, writing each part's result to disk as it finishes; earlier skeptic gates in this project
were lost to machine restarts, not to errors.
