# Sum segment files into a cumulative table and compare with the claimant's table.csv
import sys, glob, csv
segdir = sys.argv[1]
out = sys.argv[2]
tot = None; Xs = None
for fn in sorted(glob.glob(segdir + "/seg_*.txt")):
    rows = [l.split() for l in open(fn) if not l.startswith("#")]
    vals = [[int(v) for v in r[1:]] for r in rows]
    if tot is None:
        tot = vals; Xs = [int(r[0]) for r in rows]
    else:
        tot = [[a + b for a, b in zip(u, v)] for u, v in zip(tot, vals)]
with open(out, "w") as f:
    f.write("X,n00,n01,n10,n11,n20,n21,n30,n31,n40,n41\n")
    for X, v in zip(Xs, tot):
        f.write(",".join(map(str, [X] + v)) + "\n")
claim = list(csv.reader(open("/tmp/work/pk/table.csv")))[1:]
mine = {X: v for X, v in zip(Xs, tot)}
nmatch = 0; nrows = 0; maxX = 0
for row in claim:
    X = int(row[0]); c = [int(v) for v in row[1:]]
    if X not in mine:
        print("not computed:", X); continue
    m = mine[X]
    if m[8] or m[9]: print("rank 4 present at", X, m[8:])
    nrows += 1
    if m[:8] == c:
        nmatch += 1; maxX = max(maxX, X)
    else:
        print("DIFF at X=%d claim=%s mine=%s" % (X, c, m[:8]))
print("rows compared %d, matching %d, max matching X %d" % (nrows, nmatch, maxX))
