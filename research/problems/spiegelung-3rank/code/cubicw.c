/* Windowed variant of cubicx.c: counts cubic fields whose discriminant D has sign SIGN and lo < |D| <= hi, so that
   large ranges are done in resumable pieces of bounded memory (same enumeration and reduction as cubic.c).
   For fixed (a, b, c) the discriminant is a concave quadratic in d, so the d-range is cut to the (at most two) intervals
   where it lands in the window; the exact window test is still applied to every form.
   Usage: cubicw SIGN(+1|-1) lo hi out.bin      (lo a multiple of 16)
   out.bin: 4-bit counts, 6 slots per 16 integers (residues 1, 5, 9, 13, 8, 12 of the signed D mod 16), slot index
   ((|D| >> 4) - (lo >> 4)) * 6 + slot; counts beyond 15 are listed as text in out.bin.ovf. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <omp.h>
typedef long long ll;
static ll LO, HI; static int SG;
static uint8_t *arr; static uint64_t *osq;   /* osq bit n - LO: an odd prime square divides n */
static ll ovf[1 << 20]; static int novf;
static const int SLOT[16] = {-1, 0, -1, -1, -1, 1, -1, -1, 2, 3, -1, -1, 4, 5, -1, -1};
static inline int fund(ll D) {
    ll m = D < 0 ? -D : D; int r = (int)(((D % 16) + 16) % 16);
    if ((r & 3) == 1) ; else if ((r & 3) == 0) { int q = (int)((((D / 4) % 4) + 4) % 4); if (!(q == 2 || q == 3)) return 0; } else return 0;
    ll i = m - LO; return !((osq[i >> 6] >> (i & 63)) & 1);
}
static inline ll key(ll D) { ll m = D < 0 ? -D : D; int r = (int)(((D % 16) + 16) % 16); return ((m >> 4) - (LO >> 4)) * 6 + SLOT[r]; }
/* does a t^3 + b t^2 + c t + d (projectively) have a root mod l? */
static inline int root_mod(ll a, ll b, ll c, ll d, int l) {
    int A = (int)(((a % l) + l) % l), B = (int)(((b % l) + l) % l), C = (int)(((c % l) + l) % l), D = (int)(((d % l) + l) % l);
    if (A == 0) return 1;                       /* root at infinity (x, y) = (1, 0) */
    for (int t = 0; t < l; t++) if ((((A * t + B) % l * t + C) % l * t + D) % l == 0) return 1;
    return 0;
}
static int irreducible(ll a, ll b, ll c, ll d) {
    static const int pr[] = {2, 3, 5, 7, 11, 13, 17, 19, 23};
    for (int i = 0; i < 9; i++) if (!root_mod(a, b, c, d, pr[i])) return 1;
    /* exact: a rational root p/q (lowest terms) has q | a. For each q | a search p with F(p, q) = 0 near the real roots. */
    if (d == 0) return 0;
    long double A = a, B = b, C = c, Dd = d;
    /* real roots by scanning for sign changes of the cubic between its critical points */
    long double roots[3]; int nr = 0;
    long double disc = B * B - 3 * A * C, lo = -1e7L, hi = 1e7L, pts[4]; int np = 0;
    pts[np++] = lo;
    if (disc > 0) { long double s = sqrtl(disc); pts[np++] = (-B - s) / (3 * A); pts[np++] = (-B + s) / (3 * A); }
    pts[np++] = hi;
    for (int i = 0; i + 1 < np; i++) {
        long double u = pts[i], v = pts[i + 1];
        long double fu = ((A * u + B) * u + C) * u + Dd, fv = ((A * v + B) * v + C) * v + Dd;
        if (fu == 0) { roots[nr++] = u; continue; }
        if ((fu < 0) == (fv < 0) && fv != 0) continue;
        for (int it = 0; it < 200; it++) {
            long double m = (u + v) / 2, fm = ((A * m + B) * m + C) * m + Dd;
            if ((fm < 0) == (fu < 0)) { u = m; fu = fm; } else v = m;
        }
        roots[nr++] = (u + v) / 2;
    }
    for (ll q = 1; q <= a; q++) if (a % q == 0)
        for (int i = 0; i < nr; i++) {
            ll p0 = (ll)llroundl(roots[i] * q);
            for (ll p = p0 - 1; p <= p0 + 1; p++) {
                __int128 v = (__int128)a * p * p * p + (__int128)b * p * p * q + (__int128)c * p * q * q + (__int128)d * q * q * q;
                if (v == 0) return 0;
            }
        }
    return 1;
}
static inline void hit(ll D) {
    ll k = key(D); uint8_t *p = &arr[k >> 1]; int sh = (int)(k & 1) * 4;
    uint8_t old = __atomic_load_n(p, __ATOMIC_RELAXED);
    for (;;) {
        if (((old >> sh) & 15) == 15) {
            #pragma omp critical
            { if (novf < (1 << 20)) ovf[novf++] = D; else { fprintf(stderr, "overflow list full\n"); exit(3); } }
            return;
        }
        if (__atomic_compare_exchange_n(p, &old, (uint8_t)(old + (1 << sh)), 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) return;
    }
}
static inline ll disc4(ll a, ll b, ll c, ll d) {
    return b * b * c * c - 4 * a * c * c * c - 4 * b * b * b * d - 27 * a * a * d * d + 18 * a * b * c * d;
}
static inline ll fdiv(ll x, ll y) { ll q = x / y; if ((x % y != 0) && ((x < 0) != (y < 0))) q--; return q; }
static inline ll cdiv(ll x, ll y) { return -fdiv(-x, y); }
/* d-intervals (within [dlo, dhi]) where L1 <= disc <= L2; returns the number of intervals (0..2), padded by 2. */
static inline int dwin(ll a, ll b, ll c, ll dlo, ll dhi, ll L1, ll L2, ll *s, ll *e) {
    long double A2 = -27.0L * a * a, B1 = 18.0L * a * b * c - 4.0L * b * b * b, C0 = (long double)b * b * c * c - 4.0L * a * c * c * c;
    long double q1 = B1 * B1 - 4 * A2 * (C0 - L1);            /* disc >= L1 between the roots */
    if (q1 < 0) { if (q1 < -1e-3L * (B1 * B1 + 1)) return 0; q1 = 0; }
    long double s1 = sqrtl(q1), u1 = (-B1 + s1) / (2 * A2), v1 = (-B1 - s1) / (2 * A2);   /* u1 <= v1 since A2 < 0 */
    ll x = (ll)floorl(u1) - 2, y = (ll)ceill(v1) + 2; if (x < dlo) x = dlo; if (y > dhi) y = dhi;
    if (x > y) return 0;
    long double q2 = B1 * B1 - 4 * A2 * (C0 - L2);            /* disc > L2 strictly inside (u2, v2) */
    if (q2 <= 0) { s[0] = x; e[0] = y; return 1; }
    long double s2 = sqrtl(q2), u2 = (-B1 + s2) / (2 * A2), v2 = (-B1 - s2) / (2 * A2);
    ll m1 = (ll)ceill(u2) + 2, m2 = (ll)floorl(v2) - 2;      /* keep [x, m1] and [m2, y] */
    if (m1 >= m2 - 1) { s[0] = x; e[0] = y; return 1; }
    int n = 0;
    if (x <= m1) { s[n] = x; e[n] = m1 < y ? m1 : y; n++; }
    if (m2 <= y) { s[n] = m2 > x ? m2 : x; e[n] = y; n++; }
    return n;
}
int main(int argc, char **argv) {
    SG = atoi(argv[1]); LO = atoll(argv[2]); HI = atoll(argv[3]);
    if (LO % 16 || HI <= LO) return 2;
    ll nb = ((HI - LO) / 16 + 2) * 3;
    arr = calloc(nb, 1); osq = calloc((HI - LO) / 64 + 2, 8);
    if (!arr || !osq) { fprintf(stderr, "alloc\n"); return 1; }
    double t0 = omp_get_wtime();
    { ll lim = (ll)sqrt((double)HI) + 2; char *comp = calloc(lim + 1, 1);
      for (ll p = 3; p <= lim; p += 2) if (!comp[p]) { for (ll q = p * p; q <= lim; q += 2 * p) comp[q] = 1; }
      #pragma omp parallel for schedule(dynamic, 64)
      for (ll p = 3; p <= lim; p += 2) if (!comp[p]) { ll pp = p * p; for (ll m = ((LO / pp) + 1) * pp; m <= HI; m += pp) { ll i = m - LO; __atomic_fetch_or(&osq[i >> 6], 1ULL << (i & 63), __ATOMIC_RELAXED); } }
      free(comp); }
    ll nf = 0;
    if (SG > 0) {
        double X = (double)HI, sX = sqrt(X);
        ll amax = (ll)(2.0 * pow(X, 0.25) / (3 * sqrt(3.0)) + 1);
        #pragma omp parallel for schedule(dynamic, 1) reduction(+:nf)
        for (ll a = 1; a <= amax; a++) {
            double t = sX - 27.0 * a * a / 4; if (t < 0) t = 0;
            ll bmax = (ll)(1.5 * a + sqrt(t) + 2);
            for (ll b = 0; b <= bmax; b++) {
                ll clo = cdiv(b * b - (ll)(sX + 2), 3 * a), chi = fdiv(b * b - 1, 3 * a);
                for (ll c = clo; c <= chi; c++) {
                    ll P = b * b - 3 * a * c; if (P <= 0) continue;
                    ll dlo = cdiv(b * c - P, 9 * a), dhi = fdiv(b * c + P, 9 * a), s[2], e[2];
                    int ni = dwin(a, b, c, dlo, dhi, LO + 1, HI, s, e);
                    for (int w = 0; w < ni; w++) for (ll d = s[w]; d <= e[w]; d++) {
                        ll D = disc4(a, b, c, d);
                        if (D <= LO || D > HI) continue;
                        ll Q = b * c - 9 * a * d, R = c * c - 3 * b * d;
                        ll aQ = Q < 0 ? -Q : Q;
                        if (aQ > P || P > R) continue;
                        if (b == 0 && d >= 0) continue;
                        if (Q == 0 && d >= 0) continue;
                        if (P == Q && !(b < llabs(3 * a - b))) continue;
                        if (P == R) { ll ad = llabs(d); if (a > ad) continue; if (ad == a && !(b < llabs(c))) continue; }
                        if (!fund(D)) continue;
                        if (!irreducible(a, b, c, d)) continue;
                        hit(D); nf++;
                    }
                }
            }
        }
    } else {
        double Y = (double)HI;
        ll amaxn = (ll)(pow(16 * Y / 27, 0.25) + 1);
        #pragma omp parallel for schedule(dynamic, 1) reduction(+:nf)
        for (ll a = 1; a <= amaxn; a++) {
            double t = sqrt(Y / 3) - 0.75 * a * a; if (t < 0) t = 0;
            ll bmax = (ll)(1.5 * a + sqrt(t) + 2);
            for (ll b = 0; b <= bmax; b++) {
                double cu = cbrt(Y / (4.0 * a)) + ((3 * a >= 2 * b) ? (double)b * b / (3.0 * a) : b - 0.75 * a);
                ll clo = (ll)(-(b + 1) - 1), chi = (ll)(cu + 2);
                for (ll c = clo; c <= chi; c++) {
                    ll L = -(a - b) * (a - b) - a * c + b * c, U = (a + b) * (a + b) + a * c + b * c;
                    ll dlo = fdiv(L, a) + 1, dhi = cdiv(U, a) - 1, s[2], e[2];
                    if (dlo > dhi) continue;
                    int ni = dwin(a, b, c, dlo, dhi, -HI, -LO - 1, s, e);
                    for (int w = 0; w < ni; w++) for (ll d = s[w]; d <= e[w]; d++) {
                        ll D = disc4(a, b, c, d);
                        if (D >= -LO || D < -HI) continue;
                        if (!(d * d - a * a > b * d - a * c)) continue;
                        if (b == 0 && d <= 0) continue;
                        if (!fund(D)) continue;
                        if (!irreducible(a, b, c, d)) continue;
                        hit(D); nf++;
                    }
                }
            }
        }
    }
    char nm[600]; snprintf(nm, sizeof nm, "%s.tmp", argv[4]);
    FILE *f = fopen(nm, "wb"); if (!f || fwrite(arr, 1, nb, f) != (size_t)nb || fclose(f)) { fprintf(stderr, "write\n"); return 1; }
    char no[600]; snprintf(no, sizeof no, "%s.ovf", argv[4]); f = fopen(no, "w"); for (int i = 0; i < novf; i++) fprintf(f, "%lld\n", ovf[i]); fclose(f);
    rename(nm, argv[4]);
    printf("window %+d (%lld, %lld]: %lld fields, %d overflow hits, %.0f s\n", SG, LO, HI, nf, novf, omp_get_wtime() - t0);
    return 0;
}
