/* Reflection statistics from the count files written by cubic.c (run in the directory holding pos.bin and neg.bin).
   Usage: stats X > table.csv
   For every positive fundamental discriminant d <= X: r = 3-rank of Q(sqrt d), r' = 3-rank of the mirror field Q(sqrt(-3d)),
   whose discriminant is -3d if 3 does not divide d and -d/3 if it does. Scholz: r' - r is 0 or 1 (any other value is
   reported as a violation). Output: one line per checkpoint X' (10 per decade) and class of d
   (cls 0: 3 does not divide d; 1: 3 | d), cumulative counts n[r][e], e = r' - r. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
typedef long long ll;
static uint64_t *nsq; static ll XN;
static inline int sqf(ll n) { return !((nsq[n >> 6] >> (n & 63)) & 1); }
static inline int fund(ll D) { if (D <= 1) return 0; if ((D & 3) == 1) return sqf(D); if ((D & 3) == 0) { int q = (D / 4) & 3; return (q == 2 || q == 3) && sqf(D / 4); } return 0; }
static int rk(int v) { return v == 0 ? 0 : v == 1 ? 1 : v == 4 ? 2 : v == 13 ? 3 : v == 40 ? 4 : -1; }
int main(int argc, char **argv) {
    ll X = atoll(argv[1]); XN = X;
    uint8_t *pos = malloc(X + 1), *neg = malloc(3 * X + 1); nsq = calloc(X / 64 + 2, 8);
    FILE *f = fopen("pos.bin", "rb"); if (!f || fread(pos, 1, X + 1, f) != (size_t)(X + 1)) return 1; fclose(f);
    f = fopen("neg.bin", "rb"); if (!f || fread(neg, 1, 3 * X + 1, f) != (size_t)(3 * X + 1)) return 1; fclose(f);
    for (ll p = 2; p * p <= X; p++) { int isp = 1; for (ll q = 2; q * q <= p; q++) if (p % q == 0) { isp = 0; break; }
        if (isp) for (ll m = p * p; m <= X; m += p * p) nsq[m >> 6] |= 1ULL << (m & 63); }
    ll n[2][5][2] = {{{0}}}, viol = 0; int k = 0;
    printf("X,cls,n00,n01,n10,n11,n20,n21,n30,n31,n40,n41\n");
    double next = pow(10, 3.0);
    for (ll d = 2; d <= X; d++) {
        if (fund(d)) {
            int cls = d % 3 == 0, r = rk(pos[d]), r2 = rk(neg[cls ? d / 3 : 3 * d]), e = r2 - r;
            if (r < 0 || r2 < 0 || e < 0 || e > 1) { viol++; if (viol < 20) fprintf(stderr, "VIOLATION d=%lld counts %d %d\n", d, pos[d], neg[cls ? d / 3 : 3 * d]); }
            else n[cls][r][e]++;
        }
        if (d >= (ll)(next + 0.5) || d == X) {
            for (int c = 0; c < 2; c++) { printf("%lld,%d", d, c); for (int r = 0; r < 5; r++) printf(",%lld,%lld", n[c][r][0], n[c][r][1]); printf("\n"); }
            k++; next = pow(10, 3.0 + k / 10.0); if (d == X) break;
        }
    }
    fprintf(stderr, "violations: %lld\n", viol);
    return 0;
}
