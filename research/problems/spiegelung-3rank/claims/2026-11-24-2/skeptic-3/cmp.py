import sys
br = {}
for l in open(sys.argv[1]):
    D, r = map(int, l.split()); br[D] = r
cu = {}
for l in open(sys.argv[2]):
    D, c = map(int, l.split()); cu[D] = c
inv = {0:0, 1:1, 4:2, 13:3, 40:4}
bad = 0
for D, r in br.items():
    c = cu.get(D, 0)
    if inv.get(c) != r:
        bad += 1
        if bad < 15: print("MISMATCH", D, "brute r", r, "cubic count", c)
print("checked", len(br), "mismatches", bad)
