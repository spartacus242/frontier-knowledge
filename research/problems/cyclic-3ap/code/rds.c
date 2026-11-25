/* Largest subset S of Z_n with no x, y, z in S, not all equal, x + z = 2y (mod n)  (OEIS A304884 for n >= 3).
   For even n this also forbids x and x + n/2 together (x, x + n/2, x is a progression with d = n/2).
   Russian-doll search: g[p] = largest such subset of {p, ..., n-1}; g[p] is g[p+1] or g[p+1] + 1, decided by a depth-first
   search for a set of size g[p+1] + 1 that contains p, pruned with count + g[v] for the next candidate v.
   Usage: rds n [DISTINCT]   prints n, a(n), a witness, node count. DISTINCT=1: only progressions with three distinct
   elements count (OEIS A341584). */
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define B(i) ((u128)1 << (i))
static int n, g[130], target, sol[130], best[130], cs[130], DIST;
static u128 T[128][128], anti[128];
static long long nodes;
static int rec(int cnt, int from, u128 forb) {      /* extend cs[0..cnt-1] with elements >= from */
    nodes++;
    if (cnt == target) { for (int i = 0; i < cnt; i++) sol[i] = cs[i]; return 1; }
    for (int v = from; v < n; v++) {
        if (cnt + g[v] < target) return 0;
        if (forb >> v & 1) continue;
        u128 f = forb | anti[v];
        for (int i = 0; i < cnt; i++) f |= T[cs[i]][v];
        cs[cnt] = v;
        if (rec(cnt + 1, v + 1, f)) return 1;
    }
    return 0;
}
int main(int argc, char **argv) {
    n = atoi(argv[1]); DIST = argc > 2 ? atoi(argv[2]) : 0;
    if (n < 1 || n > 127) return 2;
    for (int a = 0; a < n; a++) {
        if (!DIST && n % 2 == 0 && n > 2) anti[a] = B((a + n / 2) % n);
        for (int b = 0; b < n; b++) if (a != b) {
            u128 m = 0;
            for (int c = 0; c < n; c++) if (c != a && c != b)
                if ((a + b) % n == (2 * c) % n || (a + c) % n == (2 * b) % n || (b + c) % n == (2 * a) % n) m |= B(c);
            T[a][b] = m;
        }
    }
    g[n] = 0; int nb = 0;
    for (int p = n - 1; p >= 0; p--) {
        target = g[p + 1] + 1; cs[0] = p;
        if (rec(1, p + 1, anti[p])) { g[p] = target; nb = target; for (int i = 0; i < nb; i++) best[i] = sol[i]; }
        else g[p] = g[p + 1];
    }
    printf("%d %d :", n, g[0]); for (int i = 0; i < nb; i++) printf(" %d", best[i]); printf(" : nodes %lld\n", nodes);
    return 0;
}
