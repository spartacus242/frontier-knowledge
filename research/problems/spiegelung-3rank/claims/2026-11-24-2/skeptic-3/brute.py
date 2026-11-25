# Independent check: 3-rank of class groups of quadratic fields by binary quadratic forms
# (narrow class group for D>0; 3-part of narrow = 3-part of wide). Written from scratch.
import sys, math

def xgcd(a, b):
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a - q * b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0

def compose(f1, f2, D):
    # Dirichlet composition via united forms (Cohen Alg 5.4.7 style)
    a1, b1, c1 = f1; a2, b2, c2 = f2
    if abs(a1) > abs(a2):
        a1, b1, c1, a2, b2, c2 = a2, b2, c2, a1, b1, c1
    s = (b1 + b2) // 2; n = b2 - s
    if a2 % a1 == 0:
        y1 = 0; d = a1
    else:
        d, u, v = xgcd(a2, a1); y1 = u
    if s % d == 0:
        y2 = -1; x2 = 0; d1 = d
    else:
        d1, u, v = xgcd(s, d); x2 = u; y2 = -v
    v1 = a1 // d1; v2 = a2 // d1
    r = (y1 * y2 * n - x2 * c2) % v1
    b3 = b2 + 2 * v2 * r; a3 = v1 * v2
    c3 = (b3 * b3 - D) // (4 * a3)
    assert b3 * b3 - 4 * a3 * c3 == D
    return (a3, b3, c3)

def red_def(f):
    a, b, c = f
    while True:
        if not (-a < b <= a):
            k = (a - b) // (2 * a)
            b, c = b + 2 * a * k, c + k * b + a * k * k
        if a > c:
            a, b, c = c, -b, a
            continue
        if a == c and b < 0:
            b = -b
        return (a, b, c)

def classes_imag(D):
    # reduced forms |b|<=a<=c, b>=0 if |b|==a or a==c
    res = []
    a = 1
    while 3 * a * a <= -D:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a): continue
            c = (b * b - D) // (4 * a)
            if c < a: continue
            if b < 0 and (a == c): continue
            if math.gcd(math.gcd(a, abs(b)), c) != 1: continue
            res.append((a, b, c))
        a += 1
    return res

def rank3_imag(D):
    cl = classes_imag(D)
    cnt = 0
    for f in cl:
        g = red_def(compose(compose(f, f, D), f, D))
        if g[0] == 1: cnt += 1
    r = round(math.log(cnt, 3)); assert 3 ** r == cnt
    return r

def isqrt(n): return math.isqrt(n)

def rho(f, D):
    a, b, c = f
    sD = math.sqrt(D)
    # new form (c, b', a') with b' = -b mod 2c chosen in standard range
    cc = abs(c)
    if cc > sD:
        r = (-b) % (2 * cc)
        if r > cc: r -= 2 * cc
    else:
        # sqrt(D) - 2|c| < r < sqrt(D)
        r = (-b) % (2 * cc)
        sq = isqrt(D)
        # largest r congruent to -b mod 2cc with r < sqrt(D) (D non-square)
        while r + 2 * cc <= sq: r += 2 * cc
        while r > sq: r -= 2 * cc
    a2 = c; b2 = r; c2 = (b2 * b2 - D) // (4 * a2)
    return (a2, b2, c2)

def is_red_indef(f, D):
    a, b, c = f
    sD = math.sqrt(D)
    return 0 < b < sD and abs(sD - 2 * abs(a)) < b

def reduce_indef(f, D):
    for _ in range(10000):
        if is_red_indef(f, D): return f
        f = rho(f, D)
    raise Exception("no reduce")

def rank3_real(D):
    sq = isqrt(D)
    red = []
    for b in range(1, sq + 1):
        if (b * b - D) % 4: continue
        if b * b >= D: break
        m = (D - b * b) // 4  # -ac
        for a in range(1, int(math.sqrt(D)) + 2):
            if m % a: continue
            for sa in (a, -a):
                c = -(D - b * b) // (4 * sa)
                f = (sa, b, c)
                if not is_red_indef(f, D): continue
                if math.gcd(math.gcd(a, b), abs(c)) != 1: continue
                red.append(f)
    cyc = {}
    nc = 0
    for f in red:
        if f in cyc: continue
        g = f
        while g not in cyc:
            cyc[g] = nc
            g = rho(g, D)
            assert is_red_indef(g, D)
        nc += 1
    # principal cycle
    b0 = sq if (sq - D) % 2 == 0 else sq - 1
    if b0 * b0 == D: b0 -= 2
    prin = cyc[reduce_indef((1, b0, (b0 * b0 - D) // 4), D)]
    reps = {}
    for f, i in cyc.items():
        reps.setdefault(i, f)
    cnt = 0
    for i, f in reps.items():
        g = reduce_indef(compose(compose(f, f, D), f, D), D)
        if cyc[g] == prin: cnt += 1
    r = round(math.log(cnt, 3)); assert 3 ** r == cnt, (D, cnt)
    return r, nc

def fundamental(D):
    if D % 4 == 1 or (D % 4 == 3 and D < 0 and False): pass
    m = D
    if D % 4 == 1 % 4 and D % 4 != 0:
        core = D
    elif D % 4 == 0:
        core = D // 4
        if core % 4 not in (2, 3): return False
    else:
        return False
    core = abs(core)
    p = 2 if D % 4 == 0 else 3
    for p in range(2, isqrt(core) + 1):
        if core % (p * p) == 0: return False
    return D not in (0, 1)

if __name__ == "__main__":
    N = int(sys.argv[1])
    for D in range(-N, N + 1):
        if D in (0, 1) or not fundamental(D): continue
        if D < 0:
            print(D, rank3_imag(D))
        else:
            print(D, rank3_real(D)[0])
