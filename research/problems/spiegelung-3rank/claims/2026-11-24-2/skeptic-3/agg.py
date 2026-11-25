import sys, glob, math
# sum segment files, cumulative, compare with table.csv
files = sys.argv[2:]
tot = [[0]*12 for _ in range(76)]
for fn in files:
    for l in open(fn):
        if l.startswith('#'):
            p = l.split();
            if p[5] != '0' or p[7] != '0': print("WARN", fn, l.strip())
            continue
        p = list(map(int, l.split())); i = p[0]
        for j in range(12): tot[i][j] += p[1+j]
cum = []; run = [0]*12
for i in range(76):
    run = [run[j] + tot[i][j] for j in range(12)]; cum.append(run[:])
tab = [l.strip().split(',') for l in open(sys.argv[1])][1:]
for i, row in enumerate(tab):
    X = int(row[0]); claim = list(map(int, row[1:]))
    mine = cum[i][:8]
    extra = cum[i][8:]
    st = "MATCH" if mine == claim and sum(extra) == 0 else "DIFF"
    print(X, st, "" if st == "MATCH" else (mine, extra, claim))
