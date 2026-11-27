#!/usr/bin/env python3
"""Check that the batch runner carries LEDGER.md's rule sections verbatim.

    python3 -I ledger/tools/check-runner-sync.py

LEDGER.md is the rule; the runner is what actually runs. A change made in one and
not mirrored in the other has never taken effect, so this compares them:
  - the Ambition requirement section must equal the runner's AMBITION constant
    byte for byte (one constant, interpolated into every prompt that needs it);
  - the "Where candidates come from" section must equal the runner's GENERATION
    constant byte for byte, and SOURCE_METHODS must list its methods in order;
  - the Depth requirement section, as the runner embeds it on one line, must
    appear unchanged in the generator, researcher and adversary prompts;
  - the run size in Parameters (BATCH SIZE: how many headline drafts, how many
    developed) must equal the runner's RUN_DRAFTS and RUN_DEVELOPED;
  - the entry schema's "Recommended solving method" label must be in the runner
    as LEDGER.md spells it, so the entries the runner writes carry the field.
Exits non-zero on any mismatch.
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
ledger = open(os.path.join(REPO, "LEDGER.md"), encoding="utf-8").read()
runners = sorted(glob.glob(os.path.join(HERE, "unasked-ledger-batch-sequential-v*.js")),
                 key=lambda p: int(re.search(r"-v(\d+)\.js$", p).group(1)))
runner_path = runners[-1]
runner = open(runner_path, encoding="utf-8").read()
ok = True

def section(name):
    m = re.search(rf"^## {re.escape(name)}\n.*?(?=^## )", ledger, re.S | re.M)
    if not m:
        sys.exit(f"LEDGER.md has no '## {name}' section")
    return m.group(0).rstrip("\n")

amb = section("Ambition requirement")
m = re.search(r"^const AMBITION = (\".*\")$", runner, re.M)
if not m:
    print("FAIL: runner has no AMBITION constant"); ok = False
elif json.loads(m.group(1)) != amb:
    print("FAIL: runner AMBITION constant differs from LEDGER.md's Ambition requirement"); ok = False
else:
    print(f"ok: AMBITION constant matches LEDGER.md ({len(amb)} chars); used in {runner.count('${AMBITION}')} prompts")

gen = section("Where candidates come from (when asked to generate)")
m = re.search(r"^const GENERATION = (\".*\")$", runner, re.M)
if not m:
    print("FAIL: runner has no GENERATION constant"); ok = False
elif json.loads(m.group(1)) != gen:
    print("FAIL: runner GENERATION constant differs from LEDGER.md's 'Where candidates come from'"); ok = False
else:
    print(f"ok: GENERATION constant matches LEDGER.md ({len(gen)} chars); used in {runner.count('${GENERATION}')} prompts")
methods = [x.lower() for x in re.findall(r"^- \*\*([^.(*]+?)(?: \([^)]*\))?\.\*\*", gen, re.M)]
m = re.search(r"^const SOURCE_METHODS = '(.*)'$", runner, re.M)
listed = m.group(1).split(", ") if m else []
if methods != listed:
    print(f"FAIL: SOURCE_METHODS ({len(listed)}) does not list LEDGER.md's methods ({len(methods)}) in order"); ok = False
else:
    print(f"ok: SOURCE_METHODS lists all {len(methods)} methods")

depth = section("Depth requirement")
body = depth.split("\n", 1)[1].strip("\n")
# The runner embeds the section on one line: paragraphs joined by " || ", line breaks as spaces,
# and apostrophes and backticks escaped for the JS template literal.
want = body.replace("\n\n", " || ").replace("\n", " ")
start, end = "the maintainer, 2026-10-28, in project chat: delve", "which stay excluded under (b)."
copies, i = [], 0
while (i := runner.find(start, i)) >= 0:
    j = runner.find(end, i) + len(end)
    copies.append(runner[i:j].replace("\\'", "'").replace("\\`", "`"))
    i = j
good = sum(c == want for c in copies)
if len(copies) == 3 and good == 3:
    print("ok: Depth requirement embedded verbatim in all 3 prompts")
else:
    print(f"FAIL: {good} of {len(copies)} embedded Depth copies match LEDGER.md (expected 3 of 3)"); ok = False

size = re.search(r"\*\*BATCH SIZE\*\*[^\n]*?: (\d+) developed candidates, chosen by the ranker from (\d+) headline drafts", ledger)
drafts = re.search(r"^const RUN_DRAFTS = (\d+)$", runner, re.M)
developed = re.search(r"^const RUN_DEVELOPED = (\d+)$", runner, re.M)
if not size:
    print("FAIL: LEDGER.md's BATCH SIZE does not read 'N developed candidates, chosen by the ranker from M headline drafts'"); ok = False
elif not drafts or not developed:
    print("FAIL: runner has no RUN_DRAFTS or RUN_DEVELOPED constant"); ok = False
elif (size.group(2), size.group(1)) != (drafts.group(1), developed.group(1)):
    print(f"FAIL: LEDGER.md says {size.group(2)} drafts and {size.group(1)} developed; the runner says {drafts.group(1)} and {developed.group(1)}"); ok = False
else:
    print(f"ok: run size matches LEDGER.md ({drafts.group(1)} headline drafts, {developed.group(1)} developed)")

label = re.search(r"^(Recommended solving method \([^)]*\):)", ledger, re.M)
if not label:
    print("FAIL: LEDGER.md's entry schema has no 'Recommended solving method (...):' line"); ok = False
elif label.group(1) not in runner:
    print(f"FAIL: the runner does not carry the schema label '{label.group(1)}'"); ok = False
else:
    print(f"ok: the runner carries the schema label '{label.group(1)}' ({runner.count(label.group(1))} prompts)")

print(f"runner checked: {os.path.relpath(runner_path, REPO)}")
sys.exit(0 if ok else 1)
