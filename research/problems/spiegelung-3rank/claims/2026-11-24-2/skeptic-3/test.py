# Re-implementation of the prediction test (b) of the claim, from its written description only.
import sys, math
import numpy as np

def chi2_sf5(x):
    # survival function of chi-square with 5 dof (closed form for odd dof)
    if x <= 0: return 1.0
    return math.erfc(math.sqrt(x / 2)) + math.sqrt(2 * x / math.pi) * math.exp(-x / 2) * (1 + x / 3)

def cl_constant(N=60):
    # Cohen-Lenstra, real quadratic fields (u=1), p=3:  P(r) = 3^{-r(r+1)} eta_inf / (eta_r eta_{r+1})
    def eta(k):
        return math.prod(1 - 3.0 ** (-i) for i in range(1, k + 1))
    einf = eta(400)
    P = [3.0 ** (-r * (r + 1)) * einf / (eta(r) * eta(r + 1)) for r in range(N)]
    return sum(P), sum(P[r] * 3.0 ** (-(r + 1)) for r in range(N)), P

rows = [l.strip().split(',') for l in open(sys.argv[1] if len(sys.argv) > 1 else '/tmp/work/pk2/table.csv')][1:]
X = [int(r[0]) for r in rows]
N = np.array([[int(v) for v in r[1:]] for r in rows], dtype=float)  # cols n00 n01 n10 n11 n20 n21 n30 n31
assert len(X) == 76

def series(name):
    if name == 'agg':
        s = N[:, 1] + N[:, 3] + N[:, 5] + N[:, 7]; n = N.sum(axis=1)
    else:
        r = int(name); s = N[:, 2 * r + 1]; n = N[:, 2 * r] + N[:, 2 * r + 1]
    ds = np.diff(s); dn = np.diff(n)
    x = np.sqrt(np.array(X[:-1], float) * np.array(X[1:], float))
    lo = np.array(X[:-1], float); hi = np.array(X[1:], float)
    return ds, dn, x, lo, hi

def run(name, pconj, model=2, varfac=1.0, delta=0.0, verbose=False):
    ds, dn, x, lo, hi = series(name)
    fit = (lo >= 1e6 - 0.5) & (hi <= 1e10 + 0.5)
    new = (lo >= 1e10 - 0.5) & (hi <= 31622776602 + 0.5)
    assert fit.sum() == 40 and new.sum() == 5
    p0 = pconj + delta
    def design(xx):
        return np.column_stack([xx ** (-1 / 6), xx ** (-1 / 3)])[:, :model]
    y = ds[fit] / dn[fit]; nf = dn[fit]
    pt = (ds[fit] + 0.5) / (nf + 1)
    var = varfac * pt * (1 - pt) / nf
    w = 1 / var
    Jf = design(x[fit])
    Nmat = Jf.T @ (w[:, None] * Jf)
    c = np.linalg.solve(Nmat, Jf.T @ (w * (y - p0)))
    S = np.linalg.inv(Nmat)
    J = design(x[new])
    q = p0 + J @ c
    obs = ds[new] / dn[new]
    r = obs - q
    V = np.diag(varfac * q * (1 - q) / dn[new])
    T = float(r @ np.linalg.solve(V + J @ S @ J.T, r))
    p = chi2_sf5(T)
    if verbose:
        return c, T, p, obs, q
    return c, T, p

def shift_interval(name, pconj):
    f = lambda dl: run(name, pconj, delta=dl)[2] - 0.01
    # scan
    grid = np.linspace(-0.005, 0.005, 20001)
    ok = [f(g) > 0 for g in grid]
    idx = [i for i, v in enumerate(ok) if v]
    if not idx: return None
    i0, i1 = idx[0], idx[-1]
    assert all(ok[i0:i1 + 1]), "held set not an interval"
    def bis(a, b):  # f(a)<=0<f(b) or reverse
        fa = f(a)
        for _ in range(60):
            m = (a + b) / 2
            if (f(m) > 0) == (fa > 0): a = m
            else: b = m
        return (a + b) / 2
    return bis(grid[i0 - 1], grid[i0]), bis(grid[i1], grid[i1 + 1])

if __name__ == '__main__':
    tot, agg, P = cl_constant()
    print("Cohen-Lenstra sum P(r) =", tot, " P(r)=", [round(v, 8) for v in P[:5]])
    print("sum_r P(r) 3^-(r+1) = %.12f" % agg)
    consts = {'agg': agg, '0': 1 / 3, '1': 1 / 9, '2': 1 / 27}
    for nm in ['agg', '0', '1', '2']:
        pc = consts[nm]
        c, T, p, obs, q = run(nm, pc, verbose=True)
        _, Th, ph = run(nm, pc, varfac=0.5)
        c1, T1, p1 = run(nm, pc, model=1)
        si = shift_interval(nm, pc)
        print(f"{nm:4s} M2 c1={c[0]:.5f} c2={c[1]:.5f} T={T:.2f} p={p:.3f} {'HELD' if p > 0.01 else 'FAILED'} | half: T={Th:.2f} p={ph:.4f} {'HELD' if ph > 0.01 else 'FAILED'} | M1 c1={c1[0]:.5f} T={T1:.2f} p={p1:.4f} {'HELD' if p1 > 0.01 else 'FAILED'} | shift [{si[0]:+.5f}, {si[1]:+.5f}]")
        print("     new-bin z:", np.round((obs - q) / np.sqrt(q * (1 - q) / series(nm)[1][-5:]), 2))
