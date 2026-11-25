"""Out-of-sample prediction test, frozen in notes.md (run of 2026-11-24 20:53 UTC) before the new range was counted.
Usage: python3 predict.py table.csv [xfit_lo=1e6] [xfit_hi=1e10]
Fit on bins in (xfit_lo, xfit_hi]: p(x) = p_conj + c1 x^(-1/6) + c2 x^(-1/3) (M2) or c2 = 0 (M1), p_conj fixed, weighted
least squares with add-half binomial variances. Predict every bin above xfit_hi; T = r' (V + J S J')^-1 r, chi-square with
(number of new bins) degrees of freedom. HELD if p > 0.01."""
import csv, sys, math
rows = list(csv.DictReader(open(sys.argv[1])))
lo = float(sys.argv[2]) if len(sys.argv) > 2 else 1e6
hi = float(sys.argv[3]) if len(sys.argv) > 3 else 1e10
Xs = sorted({int(r['X']) for r in rows})
cum = {X: [sum(int(r[f'n{k}{e}']) for r in rows if int(r['X']) == X) for k in range(5) for e in range(2)] for X in Xs}
def bins(sel):
    fit, new = [], []
    for a, b in zip(Xs, Xs[1:]):
        if a < lo * 0.999: continue
        d = [y - x for x, y in zip(cum[a], cum[b])]; s, n = sel(d)
        if n > 0: (fit if b <= hi * 1.001 else new).append((math.sqrt(a * b), s, n))
    return fit, new
def solve(A, b):                      # Gaussian elimination with pivoting; b may be a matrix (list of rows)
    n = len(A); M = [list(A[i]) + list(b[i]) for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]; M[r] = [x - f * y for x, y in zip(M[r], M[i])]
    return [[M[i][n + j] / M[i][i] for j in range(len(b[0]))] for i in range(n)]
def chi2sf(t, k):                     # survival function, any integer k, by series/recurrence
    if t <= 0: return 1.0
    if k % 2 == 0:
        term = s = math.exp(-t / 2)
        for i in range(1, k // 2): term *= t / (2 * i); s += term
        return s
    s = math.erfc(math.sqrt(t / 2)); term = math.sqrt(2 * t / math.pi) * math.exp(-t / 2)
    for i in range(1, k, 2): s += term; term *= t / (i + 2)
    return s
def test(fit, new, pconj, nterms, vscale=1.0):
    ex = [1 / 6, 1 / 3][:nterms]
    # normal equations
    A = [[0.0] * nterms for _ in range(nterms)]; g = [[0.0] for _ in range(nterms)]
    for x, s, n in fit:
        pt = (s + 0.5) / (n + 1); w = n / (pt * (1 - pt)) / vscale; u = [x ** -e for e in ex]; y = s / n - pconj
        for i in range(nterms):
            g[i][0] += w * u[i] * y
            for j in range(nterms): A[i][j] += w * u[i] * u[j]
    I = [[float(i == j) for j in range(nterms)] for i in range(nterms)]
    S = solve(A, I); c = [sum(S[i][j] * g[j][0] for j in range(nterms)) for i in range(nterms)]
    chifit = sum((n / (((s + .5) / (n + 1)) * (1 - (s + .5) / (n + 1))) / vscale) * (s / n - pconj - sum(ci * x ** -e for ci, e in zip(c, ex))) ** 2 for x, s, n in fit)
    m = len(new); J = [[x ** -e for e in ex] for x, s, n in new]
    pred = [pconj + sum(ci * u for ci, u in zip(c, Jr)) for Jr in J]
    r = [[s / n - p] for (x, s, n), p in zip(new, pred)]
    C = [[sum(J[a][i] * S[i][j] * J[b][j] for i in range(nterms) for j in range(nterms)) + (pred[a] * (1 - pred[a]) / new[a][2] * vscale if a == b else 0.0) for b in range(m)] for a in range(m)]
    z = solve(C, r); T = sum(r[i][0] * z[i][0] for i in range(m))
    return T, chi2sf(T, m), c, chifit, len(fit) - nterms, pred
eta = lambda k: math.prod(1 - 3.0 ** -j for j in range(1, k + 1))
agg = eta(200) * sum(3.0 ** -((r + 1) ** 2) / (eta(r) ** 2 * (1 - 3.0 ** -(r + 1))) for r in range(40))
series = [("aggregate", lambda d: (sum(d[1::2]), sum(d)), agg)] + \
         [(f"r={k}", (lambda k: lambda d: (d[2 * k + 1], d[2 * k] + d[2 * k + 1]))(k), 3.0 ** -(k + 1)) for k in range(3)]
print(f"X_max = {Xs[-1]}; fit bins in ({lo:g}, {hi:g}], prediction bins above")
for name, sel, pconj in series:
    fit, new = bins(sel)
    print(f"{name}: {len(fit)} fit bins, {len(new)} new bins")
    for label, nt in (("M2", 2), ("M1", 1)):
        T, p, c, chifit, dof, pred = test(fit, new, pconj, nt)
        T2, p2, *_ = test(fit, new, pconj, nt, 0.5)
        print(f"  {label}: c = {', '.join(f'{x:+.5f}' for x in c)}; fit chi2/dof {chifit:.1f}/{dof}; T = {T:.2f}, p = {p:.4f} "
              f"{'HELD' if p > 0.01 else 'FAILED'}; with variances halved T = {T2:.2f}, p = {p2:.4f} {'HELD' if p2 > 0.01 else 'FAILED'}")
        if nt == 2:
            for (x, s, n), q in zip(new, pred): print(f"      bin at {x:.4g}: observed {s / n:.6f}, predicted {q:.6f}, binomial se {math.sqrt(q * (1 - q) / n):.6f}")
            # sensitivity: range of shifts delta of p_conj that still give HELD
            def held(dl): return test(fit, new, pconj + dl, 2)[1] > 0.01
            rng = []
            for sgn in (-1, 1):
                dl = 0.0; step = 1e-5
                while abs(dl) < 0.05 and held(dl + sgn * step): dl += sgn * step
                rng.append(dl)
            print(f"      M2 still HELD for p_conj shifted by delta in [{rng[0]:+.5f}, {rng[1]:+.5f}]" + ("" if held(0) else " (not held at delta = 0)"))
