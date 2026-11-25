#!/usr/bin/env python3
"""Check a witness for one of the Ramsey-table problems. Standard library only.

    python3 tools/witness.py G <s> <file>   integers, every gap <= s, no 3-term AP   -> shows G(3,s) > len
    python3 tools/witness.py M <s> <file>   one integer per block [i*s, i*s+s-1]     -> shows M(3,s) > len
    python3 tools/witness.py W <r> <file>   string of colours 1..r                     -> shows w*(3;r) > len

A W witness fails if some x, x+d, x+2d have colours c1, c2, c3 with c1 + c3 == 2*c2
(all equal, or themselves evenly spaced). Prints OK <n> or FAIL <reason>; exit code 0 only for OK.
"""
import sys


def ints(text):
    return [int(t) for t in text.split()]


def no_3ap(xs):
    s = set(xs)
    xs = sorted(s)
    for i, a in enumerate(xs):
        for b in xs[i + 1:]:
            if 2 * b - a in s:
                return (a, b, 2 * b - a)
    return None


def check(kind, param, text):
    if kind == "G":
        xs = ints(text)
        if len(set(xs)) != len(xs):
            return False, "repeated element"
        xs.sort()
        gaps = [b - a for a, b in zip(xs, xs[1:])]
        if any(g > param for g in gaps):
            return False, f"gap larger than {param}"
        bad = no_3ap(xs)
        return (False, f"3-AP {bad}") if bad else (True, len(xs))
    if kind == "M":
        xs = ints(text)
        for i, x in enumerate(xs):
            if not i * param <= x <= i * param + param - 1:
                return False, f"element {x} outside block {i}"
        bad = no_3ap(xs)
        return (False, f"3-AP {bad}") if bad else (True, len(xs))
    if kind == "W":
        cs = [int(ch) for ch in text.strip() if not ch.isspace()]
        n = len(cs)
        if any(not 1 <= c <= param for c in cs):
            return False, f"colour outside 1..{param}"
        for x in range(n):
            for d in range(1, (n - 1 - x) // 2 + 1):
                if cs[x] + cs[x + 2 * d] == 2 * cs[x + d]:
                    return False, f"bad triple at positions {x + 1},{x + d + 1},{x + 2 * d + 1}"
        return True, n
    return False, f"unknown kind {kind}"


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    ok, info = check(sys.argv[1], int(sys.argv[2]), open(sys.argv[3]).read())
    print(f"OK {info}" if ok else f"FAIL {info}")
    sys.exit(0 if ok else 1)
