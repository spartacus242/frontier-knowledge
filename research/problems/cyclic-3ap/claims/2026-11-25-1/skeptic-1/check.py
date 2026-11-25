# Independent (pure Python) checks: witness verification by brute definition; tiny-n brute force.
import sys, itertools
def admissible(S, n):
    S = set(S)
    if any(not (0 <= x < n) for x in S): return False
    for x in S:
        for y in S:
            for z in S:
                if x == y == z: continue
                if (x + z - 2*y) % n == 0: return False
    return True
def brute(n):
    # largest admissible subset by plain enumeration of k-subsets containing 0
    best = 1
    k = 2
    while True:
        found = False
        for c in itertools.combinations(range(1, n), k-1):
            if admissible((0,)+c, n): found = True; break
        if not found: return k-1
        k += 1
if __name__ == "__main__":
    ok = True
    for line in open('/tmp/work/pk3/terms.csv').read().strip().split('\n')[1:]:
        n, a, w = line.split(',')
        n = int(n); a = int(a); w = list(map(int, w.split()))
        good = len(w) == a and len(set(w)) == a and admissible(w, n)
        print(n, a, 'witness OK' if good else 'WITNESS BAD'); ok &= good
    print('ALL WITNESSES OK' if ok else 'FAIL')
    print('brute a(3..24):', [brute(n) for n in range(3, 25)])
