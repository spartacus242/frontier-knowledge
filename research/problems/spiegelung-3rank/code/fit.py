"""Pre-set convergence test (see notes.md, frozen definition). Usage: python3 fit.py table.csv [xmin=1e6] [exponent=1/6]
Bins between consecutive checkpoints above xmin; per bin the proportion with e = 1 (aggregate; conditional on r = 0, 1, 2)
with binomial variance; weighted least squares p = p_inf + c * x^(-exponent) at geometric bin midpoints."""
import csv, sys, math
rows = list(csv.DictReader(open(sys.argv[1])))
xmin = float(sys.argv[2]) if len(sys.argv) > 2 else 1e6
ex = eval(sys.argv[3]) if len(sys.argv) > 3 else 1 / 6
Xs = sorted({int(r['X']) for r in rows})
cum = {X: [sum(int(r[f'n{k}{e}']) for r in rows if int(r['X']) == X) for k in range(5) for e in range(2)] for X in Xs}
def series(sel):          # sel(counts) -> (successes, trials)
    out = []
    for a, b in zip(Xs, Xs[1:]):
        if a < xmin * 0.999: continue
        d = [y - x for x, y in zip(cum[a], cum[b])]; s, n = sel(d)
        if n > 0: out.append((math.sqrt(a * b), s, n))
    return out
def wls(pts):
    S = Sx = Sy = Sxx = Sxy = 0.0; data = []
    for x, s, n in pts:
        p = s / n; pt = (s + 0.5) / (n + 1); v = pt * (1 - pt) / n;   # variance from the add-half estimate: a bin with s = 0 must not get infinite weight
        u = x ** (-ex); w = 1 / v
        S += w; Sx += w * u; Sy += w * p; Sxx += w * u * u; Sxy += w * u * p; data.append((u, p, w))
    det = S * Sxx - Sx * Sx; pinf = (Sxx * Sy - Sx * Sxy) / det; c = (S * Sxy - Sx * Sy) / det
    se = math.sqrt(Sxx / det); chi = sum(w * (p - pinf - c * u) ** 2 for u, p, w in data)
    return pinf, se, c, chi, len(data) - 2
eta = lambda k: math.prod(1 - 3.0 ** -j for j in range(1, k + 1))
agg = eta(200) * sum(3.0 ** -((r + 1) ** 2) / (eta(r) ** 2 * (1 - 3.0 ** -(r + 1))) for r in range(40))
tests = [("aggregate", lambda d: (sum(d[1::2]), sum(d)), agg)] + \
        [(f"r={k}", (lambda k: lambda d: (d[2 * k + 1], d[2 * k] + d[2 * k + 1]))(k), 3.0 ** -(k + 1)) for k in range(3)]
X = Xs[-1]; tot = cum[X]
print(f"X_max = {X}, N = {sum(tot)}, model p_inf + c x^-{ex:.4f}, bins above {xmin:g}")
for name, sel, pred in tests:
    s, n = sel(tot); pinf, se, c, chi, dof = wls(series(sel))
    z = (pinf - pred) / se; ok = chi / dof <= 2
    verdict = "VOID (chi2/dof > 2)" if not ok else ("CONSISTENT" if abs(z) <= 3 else "INCONSISTENT WITH THIS MODEL")
    print(f"{name:9s} raw {s}/{n} = {s / n:.6f}  predicted {pred:.8f}  fit p_inf {pinf:.6f} +- {se:.6f}  c {c:+.4f}  "
          f"z {z:+.2f}  chi2/dof {chi:.1f}/{dof}  {verdict}")
