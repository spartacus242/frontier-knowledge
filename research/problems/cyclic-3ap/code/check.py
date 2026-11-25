"""check.py n e1 e2 ... : verifies that the set is admissible in Z_n (no x, y, z in S, not all equal, x + z = 2y mod n)."""
import sys
n = int(sys.argv[1]); S = sorted(set(int(x) % n for x in sys.argv[2:]))
assert len(S) == len(sys.argv) - 2, "repeated element"
bad = [(x, y, z) for x in S for y in S for z in S if not (x == y == z) and (x + z - 2 * y) % n == 0]
print(n, len(S), "OK" if not bad else f"BAD {bad[0]}")
