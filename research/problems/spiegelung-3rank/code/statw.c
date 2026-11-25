/* Reflection statistics from the window files of cubicw.c (same CSV as cubicx.c).
   Usage: statw X W dir > table.csv     windows (iW, (i+1)W], files dir/p_<i>.bin (positive, up to X) and dir/n_<i>.bin
   (negative, up to 3X). Every stored count must be 0, 1, 4, 13 or 40 (= (3^r - 1)/2); every pair must satisfy Scholz. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
typedef long long ll;
static ll X, W; static const char *dir;
static uint8_t *win[2][4096]; static ll *ov[2]; static int nov[2];
static const int SLOT[16] = {-1, 0, -1, -1, -1, 1, -1, -1, 2, 3, -1, -1, 4, 5, -1, -1};
static int cmp(const void *a, const void *b) { ll x = *(ll *)a, y = *(ll *)b; return x < y ? -1 : x > y; }
static void load(int s, int i) {
    char nm[700]; snprintf(nm, sizeof nm, "%s/%c_%d.bin", dir, s ? 'n' : 'p', i);
    int fd = open(nm, O_RDONLY); if (fd < 0) { fprintf(stderr, "missing %s\n", nm); exit(1); }
    struct stat st; fstat(fd, &st); win[s][i] = mmap(0, st.st_size, PROT_READ, MAP_SHARED, fd, 0);
    if (win[s][i] == MAP_FAILED) { perror("mmap"); exit(1); }
    strcat(nm, ".ovf"); FILE *f = fopen(nm, "r"); ll D; if (!f) { fprintf(stderr, "missing %s\n", nm); exit(1); }
    while (fscanf(f, "%lld", &D) == 1) { ov[s] = realloc(ov[s], (nov[s] + 1) * sizeof(ll)); ov[s][nov[s]++] = D; } fclose(f);
}
static int count(ll D) {
    ll m = D < 0 ? -D : D; int s = D < 0, i = (int)((m - 1) / W), r = (int)(((D % 16) + 16) % 16);
    ll k = ((m >> 4) - ((i * W) >> 4)) * 6 + SLOT[r];
    int v = (win[s][i][k >> 1] >> ((k & 1) * 4)) & 15;
    if (v == 15) { ll *p = bsearch(&D, ov[s], nov[s], sizeof(ll), cmp); if (p) { while (p > ov[s] && p[-1] == D) p--; while (p < ov[s] + nov[s] && *p == D) { v++; p++; } } }
    return v;
}
static int rk(int v) { return v == 0 ? 0 : v == 1 ? 1 : v == 4 ? 2 : v == 13 ? 3 : v == 40 ? 4 : -1; }
#define CH (1LL << 28)
static uint64_t osq[CH / 64 + 1]; static ll cbase = -1; static int *primes, npr;
static int oddsqfree(ll n) {          /* no odd prime square divides n (n <= 3X) */
    ll base = n / CH * CH;
    if (base != cbase) { cbase = base; memset(osq, 0, sizeof osq);
        for (int j = 0; j < npr; j++) { ll pp = (ll)primes[j] * primes[j]; if (pp > base + CH) break;
            for (ll m = (base + pp - 1) / pp * pp; m < base + CH; m += pp) osq[(m - base) >> 6] |= 1ULL << ((m - base) & 63); } }
    return !((osq[(n - base) >> 6] >> ((n - base) & 63)) & 1);
}
static int fund(ll D) {
    ll m = D < 0 ? -D : D; int r = (int)(((D % 16) + 16) % 16);
    if (D == 1) return 0;
    if ((r & 3) == 1) ; else if ((r & 3) == 0) { int q = (int)((((D / 4) % 4) + 4) % 4); if (!(q == 2 || q == 3)) return 0; } else return 0;
    return oddsqfree(m);
}
int main(int argc, char **argv) {
    X = atoll(argv[1]); W = atoll(argv[2]); dir = argv[3];
    ll lim = (ll)sqrt(3.0 * X) + 2; char *comp = calloc(lim + 1, 1); primes = malloc(sizeof(int) * (lim / 2 + 10));
    for (ll p = 3; p <= lim; p += 2) if (!comp[p]) { primes[npr++] = (int)p; for (ll q = p * p; q <= lim; q += 2 * p) comp[q] = 1; }
    for (int i = 0; i * W < X; i++) load(0, i);
    for (int i = 0; i * W < 3 * X; i++) load(1, i);
    for (int s = 0; s < 2; s++) qsort(ov[s], nov[s], sizeof(ll), cmp);
    ll bad = 0, viol = 0, hn[6] = {0}, n[2][5][2] = {{{0}}}; int k = 0;
    for (ll D = 3; D <= 3 * X; D++) if (fund(-D)) { int r = rk(count(-D)); if (r < 0) { bad++; if (bad < 20) fprintf(stderr, "BAD count %d at D=-%lld\n", count(-D), D); } else hn[r]++; }
    printf("X,cls,n00,n01,n10,n11,n20,n21,n30,n31,n40,n41\n");
    double next = 1000;
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
    fprintf(stderr, "bad counts: %lld  Scholz violations: %lld  overflow hits: %d\n", bad, viol, nov[0] + nov[1]);
    fprintf(stderr, "imaginary rank histogram to 3X:"); for (int r = 0; r < 5; r++) fprintf(stderr, " %lld", hn[r]); fprintf(stderr, "\n");
    return 0;
}
