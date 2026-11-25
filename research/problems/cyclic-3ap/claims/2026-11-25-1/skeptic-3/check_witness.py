# Independent brute-force check of each witness in terms.csv:
# S subset of Z_n, size a(n), no x,y,z in S not all equal with x+z = 2y mod n.
import csv, sys
rows = list(csv.reader(open('/tmp/work/pk3/terms.csv')))[1:]
ok = True
for r in rows:
    n, a = int(r[0]), int(r[1]); S = [int(t) for t in r[2].split()]
    assert len(set(S)) == len(S) == a, (n, 'size/dupe')
    assert all(0 <= s < n for s in S), (n, 'range')
    Ss = set(S); bad = None
    for x in S:
        for y in S:
            z = (2*y - x) % n
            if z in Ss and not (x == y == z):
                bad = (x, y, z); break
        if bad: break
    print(n, a, 'OK' if not bad else f'BAD {bad}'); ok &= not bad
print('ALL OK' if ok else 'FAILURE')
