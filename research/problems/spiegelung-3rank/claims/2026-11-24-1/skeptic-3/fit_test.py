# Re-implementation of the pre-set test of claim (b), from the packet's description.
import sys, csv, math
import numpy as np

def load(fn):
    rows = list(csv.reader(open(fn)))
    hdr = rows[0]; data = [[int(v) for v in r] for r in rows[1:]]
    return hdr, data

def run(fn, Xmin=10**6, Xmax=None, varmode="n", verbose=True):
    hdr, data = load(fn)
    idx = {h: i for i, h in enumerate(hdr)}
    data = [r for r in data if r[0] >= Xmin and (Xmax is None or r[0] <= Xmax)]
    def tot(r, rr):  # (n, s) for rank rr (None = all)
        if rr is None:
            n = sum(r[idx["n%d%d" % (q, e)]] for q in range(4) for e in (0, 1) if "n%d%d" % (q, e) in idx)
            s = sum(r[idx["n%d1" % q]] for q in range(4) if "n%d1" % q in idx)
            for q in (4,):
                if "n%d0" % q in idx: n += r[idx["n%d0" % q]] + r[idx["n%d1" % q]]; s += r[idx["n%d1" % q]]
            return n, s
        return r[idx["n%d0" % rr]] + r[idx["n%d1" % rr]], r[idx["n%d1" % rr]]
    targets = {None: None, 0: 1/3, 1: 1/9, 2: 1/27}
    # conjectured aggregate: sum_r P(r) 3^-(r+1) with Cohen-Lenstra real-quadratic 3-rank distribution
    res = {}
    for rr in (None, 0, 1, 2):
        xs, ys, ws = [], [], []
        for lo, hi in zip(data[:-1], data[1:]):
            n1, s1 = tot(lo, rr); n2, s2 = tot(hi, rr)
            n, s = n2 - n1, s2 - s1
            ph = (s + 0.5) / (n + 1)
            var = ph * (1 - ph) / (n if varmode == "n" else n + 1)
            xs.append(math.sqrt(lo[0] * hi[0])); ys.append(s / n if n else ph); ws.append(1 / var)
        x = np.array(xs); y = np.array(ys); w = np.array(ws)
        A = np.vstack([np.ones_like(x), x ** (-1 / 6)]).T
        AtW = A.T * w
        cov = np.linalg.inv(AtW @ A)
        beta = cov @ (AtW @ y)
        chi2 = float(np.sum(w * (y - A @ beta) ** 2))
        res[rr] = (beta[0], math.sqrt(cov[0, 0]), beta[1], chi2, len(x) - 2)
    return res, data[-1]

if __name__ == "__main__":
    fn = sys.argv[1]
    agg_conj = float(sys.argv[2]) if len(sys.argv) > 2 else 0.29765117
    for vm in ("n", "n+1"):
        res, last = run(fn, varmode=vm)
        print("variance denominator:", vm)
        for rr, (p, se, c, chi2, dof) in res.items():
            t = agg_conj if rr is None else 3.0 ** -(rr + 1)
            z = (p - t) / se
            verdict = "VOID" if chi2 / dof > 2 else ("CONSISTENT" if abs(z) <= 3 else "INCONSISTENT")
            print("  %-4s p_inf=%.6f +- %.6f  c=%.4f  chi2=%.2f/%d  target=%.8f  z=%+.2f  %s" %
                  ("all" if rr is None else "r=%d" % rr, p, se, c, chi2, dof, t, z, verdict))
