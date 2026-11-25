/* Memory-compact variant of cubic.c for X up to 10^10 (same enumeration, see cubic.c for the method).
   Counts are kept in 4 bits per candidate discriminant (only residues 1, 5, 9, 13, 8, 12 mod 16 can be fundamental);
   a count that passes 15 spills into a small overflow list. The reflection statistics of stats.c are computed in-process
   and printed (same CSV format), instead of writing the count files.
   Usage: cubicx X > table.csv */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <omp.h>
typedef long long ll;
static ll X, XN;                 /* XN = 3X */
static uint8_t *pos, *neg;       /* nibble arrays */
static uint64_t *nsq;            /* bit (n >> 1) set: odd n is NOT squarefree, n in [0, 3X] */
static ll ovf[1 << 16]; static int novf;   /* signed discriminants of hits beyond 15 */
static double SL = 1.0;
static inline int sqf(ll n) { if ((n & 3) == 0) return 0; if (!(n & 1)) n >>= 1; n >>= 1; return !((nsq[n >> 6] >> (n & 63)) & 1); }
static const int SLOT[16] = {-1, 0, -1, -1, -1, 1, -1, -1, 2, 3, -1, -1, 4, 5, -1, -1};
static inline ll key(ll D) { ll m = D < 0 ? -D : D; int r = (int)(((D % 16) + 16) % 16); return (m >> 4) * 6 + SLOT[r]; }
static inline int getn(uint8_t *arr, ll k) { return (arr[k >> 1] >> ((k & 1) * 4)) & 15; }
static inline int fund(ll D) {   /* is D a fundamental discriminant (D != 1)? */
    ll m = D < 0 ? -D : D;
    if (D == 1 || D == 0) return 0;
    int r = (int)(((D % 16) + 16) % 16);
    if ((r & 3) == 1) return sqf(m);
    if ((r & 3) == 0) { int q = (int)((((D / 4) % 4) + 4) % 4); return (q == 2 || q == 3) && sqf(m / 4); }
    return 0;
}
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
static inline void hit(uint8_t *arr, ll D) {
    ll k = key(D); uint8_t *p = &arr[k >> 1]; int sh = (int)(k & 1) * 4;
    uint8_t old = __atomic_load_n(p, __ATOMIC_RELAXED);
    for (;;) {
        if (((old >> sh) & 15) == 15) {
            #pragma omp critical
            { if (novf < (1 << 16)) ovf[novf++] = D; }
            return;
        }
        if (__atomic_compare_exchange_n(p, &old, (uint8_t)(old + (1 << sh)), 1, __ATOMIC_RELAXED, __ATOMIC_RELAXED)) return;
    }
}
static int count(ll D) { int v = getn(D < 0 ? neg : pos, key(D)); if (v == 15) for (int i = 0; i < novf; i++) if (ovf[i] == D) v++; return v; }
static int rk(int v) { return v == 0 ? 0 : v == 1 ? 1 : v == 4 ? 2 : v == 13 ? 3 : v == 40 ? 4 : -1; }
static inline ll disc4(ll a, ll b, ll c, ll d) {
    return b * b * c * c - 4 * a * c * c * c - 4 * b * b * b * d - 27 * a * a * d * d + 18 * a * b * c * d;
}
static inline ll fdiv(ll x, ll y) { ll q = x / y; if ((x % y != 0) && ((x < 0) != (y < 0))) q--; return q; }   /* floor */
static inline ll cdiv(ll x, ll y) { return -fdiv(-x, y); }
int main(int argc, char **argv) {
    X = atoll(argv[1]); XN = 3 * X; if (argc > 2) SL = atof(argv[2]);
    pos = calloc((X / 16 + 1) * 3 + 8, 1); neg = calloc((XN / 16 + 1) * 3 + 8, 1); nsq = calloc(XN / 128 + 2, 8);
    if (!pos || !neg || !nsq) { fprintf(stderr, "alloc\n"); return 1; }
    for (ll p = 3; p * p <= XN; p += 2) { int isp = 1; for (ll q = 3; q * q <= p; q += 2) if (p % q == 0) { isp = 0; break; }
        if (isp) for (ll m = p * p; m <= XN; m += 2 * p * p) nsq[(m >> 1) >> 6] |= 1ULL << ((m >> 1) & 63); }
    double sX = sqrt((double)X), t0 = omp_get_wtime();
    /* ---------- positive discriminants: Hessian-reduced forms ----------
       H = (P, Q, R), P = b^2 - 3ac, Q = bc - 9ad, R = c^2 - 3bd, 3 disc = 4PR - Q^2. Reduced: |Q| <= P <= R with
       a > 0, b >= 0, d < 0 if b = 0; Q = 0 => d < 0; P = Q => b < |3a - b|; P = R => a <= |d|, and b < |c| if |d| = a.
       Then P <= sqrt(disc), so (b^2 - sqrt X)/(3a) <= c < b^2/(3a), and |bc - 9ad| <= P bounds d. */
    ll amax = (ll)(SL * (2.0 * pow((double)X, 0.25) / (3 * sqrt(3.0))) + 1);
    ll npos = 0;
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:npos)
    for (ll a = 1; a <= amax; a++) {
        double t = sX - 27.0 * a * a / 4; if (t < 0) t = 0;
        ll bmax = (ll)(SL * (1.5 * a + sqrt(t)) + 2);
        for (ll b = 0; b <= bmax; b++) {
            ll clo = cdiv(b * b - (ll)(SL * SL * sX + 2), 3 * a), chi = fdiv(b * b - 1, 3 * a);
            for (ll c = clo; c <= chi; c++) {
                ll P = b * b - 3 * a * c; if (P <= 0) continue;
                ll dlo = cdiv(b * c - P, 9 * a), dhi = fdiv(b * c + P, 9 * a);
                for (ll d = dlo; d <= dhi; d++) {
                    ll Q = b * c - 9 * a * d, R = c * c - 3 * b * d;
                    ll aQ = Q < 0 ? -Q : Q;
                    if (aQ > P || P > R) continue;
                    if (b == 0 && d >= 0) continue;
                    if (Q == 0 && d >= 0) continue;
                    if (P == Q && !(b < llabs(3 * a - b))) continue;
                    if (P == R) { ll ad = llabs(d); if (a > ad) continue; if (ad == a && !(b < llabs(c))) continue; }
                    ll D = disc4(a, b, c, d);
                    if (D <= 0 || D > X) continue;
                    if (!fund(D)) continue;
                    if (!irreducible(a, b, c, d)) continue;
                    hit(pos, D); npos++;
                }
            }
        }
    }
    fprintf(stderr, "positive done: %lld fields, %.0f s\n", npos, omp_get_wtime() - t0);
    /* ---------- negative discriminants: Mathews-reduced forms (Belabas, Section 4) ----------
       Reduced: d^2 - a^2 > bd - ac,  -(a-b)^2 - ac < ad - bc < (a+b)^2 + ac,  a > 0, b >= 0, d > 0 if b = 0.
       Bounds for -Y <= disc < 0 (Y = 3X): a <= (16Y/27)^(1/4); b <= 3a/2 + (sqrt(Y/3) - 3a^2/4)^(1/2);
       1 - b <= c <= (Y/4a)^(1/3) + (b^2/3a if a >= 2b/3, else b - 3a/4); the middle condition bounds d. */
    double Y = (double)XN; ll nneg = 0;
    ll amaxn = (ll)(SL * pow(16 * Y / 27, 0.25) + 1);
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:nneg)
    for (ll a = 1; a <= amaxn; a++) {
        double t = sqrt(Y / 3) - 0.75 * a * a; if (t < 0) t = 0;
        ll bmax = (ll)(SL * (1.5 * a + sqrt(t)) + 2);
        for (ll b = 0; b <= bmax; b++) {
            double cu = cbrt(Y / (4.0 * a)) + ((3 * a >= 2 * b) ? (double)b * b / (3.0 * a) : b - 0.75 * a);
            ll clo = (ll)(-(SL * (b + 1)) - 1), chi = (ll)(SL * cu + 2);
            for (ll c = clo; c <= chi; c++) {
                /* -(a-b)^2 - ac + bc < a d < (a+b)^2 + ac + bc */
                ll L = -(a - b) * (a - b) - a * c + b * c, U = (a + b) * (a + b) + a * c + b * c;
                ll dlo = fdiv(L, a) + 1, dhi = cdiv(U, a) - 1;
                for (ll d = dlo; d <= dhi; d++) {
                    if (!(d * d - a * a > b * d - a * c)) continue;
                    if (b == 0 && d <= 0) continue;
                    ll D = disc4(a, b, c, d);
                    if (D >= 0 || D < -XN) continue;
                    if (!fund(D)) continue;
                    if (!irreducible(a, b, c, d)) continue;
                    hit(neg, D); nneg++;
                }
            }
        }
    }
    fprintf(stderr, "negative done: %lld fields, %.0f s\n", nneg, omp_get_wtime() - t0);
    ll n[2][5][2] = {{{0}}}, viol = 0, bad = 0, hn[6] = {0}; int k = 0;
    for (ll D = 3; D <= XN; D++) if (fund(-D)) { int r = rk(count(-D)); if (r < 0) { bad++; if (bad < 20) fprintf(stderr, "BAD count %d at D=-%lld\n", count(-D), D); } else hn[r]++; }
    printf("X,cls,n00,n01,n10,n11,n20,n21,n30,n31,n40,n41\n");
    double next = pow(10, 3.0);
    for (ll d = 2; d <= X; d++) {
        if (fund(d)) {
            int cls = d % 3 == 0, r = rk(count(d)), r2 = rk(count(cls ? -d / 3 : -3 * d)), e = r2 - r;
            if (r < 0) { bad++; if (bad < 20) fprintf(stderr, "BAD count %d at D=%lld\n", count(d), d); }
            if (r < 0 || r2 < 0 || e < 0 || e > 1) { viol++; if (viol < 20) fprintf(stderr, "VIOLATION d=%lld\n", d); }
            else n[cls][r][e]++;
        }
        if (d >= (ll)(next + 0.5) || d == X) {
            for (int c = 0; c < 2; c++) { printf("%lld,%d", d, c); for (int r = 0; r < 5; r++) printf(",%lld,%lld", n[c][r][0], n[c][r][1]); printf("\n"); }
            k++; next = pow(10, 3.0 + k / 10.0); if (d == X) break;
        }
    }
    fprintf(stderr, "bad counts: %lld  Scholz violations: %lld  overflow hits: %d\n", bad, viol, novf);
    fprintf(stderr, "imaginary rank histogram to 3X:"); for (int r = 0; r < 5; r++) fprintf(stderr, " %lld", hn[r]); fprintf(stderr, "\n");
    return 0;
}
