# Independent check: 3-ranks of class groups of quadratic fields by binary quadratic forms
# (Gauss composition + reduction). Imaginary: reduced forms. Real: narrow classes via cycles
# of reduced indefinite forms (3-rank of narrow = 3-rank of wide class group).
import sys, math

def xgcd(a, b):
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a - q*b
        x0, x1 = x1, x0 - q*x1
        y0, y1 = y1, y0 - q*y1
    return a, x0, y0

def compose(f, g, D):
    # Dirichlet composition (forms with a>0), returns (a3,b3,c3) unreduced
    a1, b1, c1 = f; a2, b2, c2 = g
    s = (b1 + b2)//2; n = b2 - s
    e, u, v = xgcd(a1, a2)            # u a1 + v a2 = e
    d, x, y = xgcd(e, s)              # x e + y s = d
    # d = gcd(a1,a2,s) = (x u) a1 + (x v) a2 + y s
    U, V, W = x*u, x*v, y
    a3 = a1*a2//(d*d)
    b3 = (b2 + 2*a2//d*(V*(s - b2) - W*c2)) % (2*a3)
    c3 = (b3*b3 - D)//(4*a3)
    assert b3*b3 - 4*a3*c3 == D
    return (a3, b3, c3)

def red_imag(f):
    a, b, c = f
    while True:
        if c < a or (c == a and b < 0):
            a, b, c = c, -b, a
        if -a < b <= a:
            if not (a == c and b < 0):
                return (a, b, c)
        k = (a - b)//(2*a)
        # translate b into (-a,a]
        b2 = b + 2*a*k
        if b2 <= -a: b2 += 2*a; k += 1
        if b2 > a: b2 -= 2*a; k -= 1
        c = a*k*k + b*k + c
        b = b2

def rank3_imag(D):
    # D<0 fundamental
    forms = []
    a = 1
    while 3*a*a <= -D:
        for b in range(-a+1, a+1):
            if (b*b - D) % (4*a) == 0:
                c = (b*b - D)//(4*a)
                if c < a: continue
                if c == a and b < 0: continue
                if math.gcd(math.gcd(a, b), c) != 1: continue
                forms.append((a, b, c))
        a += 1
    ident = red_imag((1, D % 2, (D % 2 - D)//4))
    cnt = 0
    for f in forms:
        f2 = red_imag(compose(f, f, D)); f3 = red_imag(compose(f2, f, D))
        if f3 == ident: cnt += 1
    r = round(math.log(cnt, 3)); assert 3**r == cnt, (D, cnt)
    return r, len(forms)

# ---- real quadratic ----
def is_reduced_real(f, D, sD):
    a, b, c = f
    # 0 < b < sqrt D, sqrt D - b < 2|a| < sqrt D + b
    return 0 < b and b*b < D and (sD - b) < 2*abs(a) < (sD + b)

def rho(f, D, sD):
    a, b, c = f
    # (a,b,c) -> (c, -b + 2c t, ...) with -b+2ct in proper range
    cc = abs(c)
    # choose b' ≡ -b mod 2c with sqrt(D)-2|c| < b' < sqrt(D) if |c|<sqrtD/... ; else -|c|<b'<=|c|
    if cc*cc*4 > D or True:
        pass
    if cc < sD:
        # b' in (sD-2|c|, sD)
        lo = sD - 2*cc
        t = math.floor((sD - (-b)) / (2*cc))
        bp = -b + 2*cc*t
        while bp >= sD: bp -= 2*cc
        while bp <= lo: bp += 2*cc
    else:
        bp = -b % (2*cc)
        if bp > cc: bp -= 2*cc
    cp = (bp*bp - D)//(4*c)
    return (c, bp, cp)

def red_real(f, D, sD):
    for _ in range(10000):
        if is_reduced_real(f, D, sD): return f
        f = rho(f, D, sD)
    raise RuntimeError("no reduce")

def rank3_real(D):
    sD = math.sqrt(D)
    # all reduced forms
    red = []
    b = 1 if D % 2 else 2
    while b*b < D:
        N = (D - b*b)//4
        for a in range(1, min(N, math.isqrt(D))+1):
            if N % a == 0:
                for sa in (a, -a):
                    c = -N//sa
                    f = (sa, b, c)
                    if is_reduced_real(f, D, sD) and math.gcd(math.gcd(a, b), abs(c)) == 1:
                        red.append(f)
        b += 2
    cyc = {}
    nc = 0
    for f in red:
        if f in cyc: continue
        g = f
        while g not in cyc:
            cyc[g] = nc
            g = red_real(rho(g, D, sD), D, sD)
        nc += 1
    ident = red_real((1, D % 2, (D % 2 - D)//4), D, sD)
    pid = cyc[ident]
    reps = {}
    for f, i in cyc.items():
        if i not in reps and f[0] > 0: reps[i] = f
    cnt = 0
    for i, f in reps.items():
        f2 = compose(f, f, D)
        f2 = red_real(f2, D, sD)
        if f2[0] < 0:
            # find positive-leading form in same cycle
            g = f2
            while g[0] < 0: g = red_real(rho(g, D, sD), D, sD)
            f2 = g
        f3 = red_real(compose(f2, f, D), D, sD)
        if cyc[f3] == pid: cnt += 1
    assert len(reps) == nc
    r = round(math.log(cnt, 3)); assert 3**r == cnt, (D, cnt, nc)
    return r, nc

def is_fund(D):
    def sqf(n):
        n = abs(n); p = 2
        while p*p <= n:
            if n % (p*p) == 0: return False
            p += 1
        return True
    if D % 4 == 1: return sqf(D) and D != 1
    if D % 4 == 0:
        m = D//4
        return m % 4 in (2, 3) and sqf(m)
    return False

if __name__ == "__main__":
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    for d in range(lo, hi):
        if not is_fund(d): continue
        Dm = -3*d if d % 3 else -d//3
        r, hp = rank3_real(d)
        rp, h = rank3_imag(Dm)
        print(d, r, rp, hp, h)
