/* Second, independently written decision program for A304884 (shares no search code or bound with rds.c / rds2.c).
   Usage: sym n k   decides whether Z_n has a k-subset S with no x, y, z in S, not all equal, x + z = 2y (mod n).
   Symmetry: affine maps x -> u x + t (u a unit) preserve admissibility and gcd(x - y, n). Let d_1 < d_2 < ... be the
   proper divisors of n and g the first one that occurs as gcd(a - b, n) for a pair of S; an affine map sends that pair to
   (0, g). So it suffices to search, for each g, sets containing 0 and g in which no difference has a gcd earlier in the
   list. (k >= 2 assumed.) Search: elements in increasing order, include/skip, pruned only by counting the elements still
   allowed, plus a packing bound: disjoint progressions among the allowed elements each lose one. */
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define B(i) ((u128)1 << (i))
static int n, k, cs[130];
static u128 T[128][128], pairbad[128], G[128];
static long long nodes;
static int gcd(int a, int b) { while (b) { int t = a % b; a = b; b = t; } return a; }
static inline int pc(u128 x) { return __builtin_popcountll((unsigned long long)x) + __builtin_popcountll((unsigned long long)(x >> 64)); }
static int pack(u128 al) {           /* greedy number of disjoint 3-APs x, x+d, x+2d (as integers) inside al, small d first */
    int c = 0;
    for (int d = 1; d <= 3; d++) { u128 m = al & (al >> d) & (al >> (2 * d));
        while (m) { int x = (unsigned long long)m ? __builtin_ctzll((unsigned long long)m) : 64 + __builtin_ctzll((unsigned long long)(m >> 64));
            u128 t = B(x) | B(x + d) | B(x + 2 * d); if ((al & t) == t) { al &= ~t; c++; } m &= ~B(x); } }
    return c;
}
static int rec(int cnt, int from, u128 forb) {
    nodes++;
    if (cnt == k) return 1;
    u128 al = ~forb & ~(B(from) - 1) & (B(n) - 1);
    int av = pc(al);
    if (cnt + av < k) return 0;
    if (cnt + av - pack(al) < k) return 0;
    for (int v = from; v < n; v++) {
        if (forb >> v & 1) continue;
        if (cnt + av < k) return 0;
        u128 f = forb | pairbad[v] | G[v];
        for (int i = 0; i < cnt; i++) f |= T[cs[i]][v];
        cs[cnt] = v;
        if (rec(cnt + 1, v + 1, f)) return 1;
        av--;
    }
    return 0;
}
int main(int argc, char **argv) {
    n = atoi(argv[1]); k = atoi(argv[2]); if (n < 3 || n > 127 || k < 2) return 2;
    for (int a = 0; a < n; a++) for (int b = 0; b < n; b++) if (a != b) {
        if ((2 * a) % n == (2 * b) % n) pairbad[a] |= B(b);              /* a, b, a is a progression */
        for (int c = 0; c < n; c++) if (c != a && c != b) {
            int s1 = (a + b - 2 * c) % n, s2 = (a + c - 2 * b) % n, s3 = (b + c - 2 * a) % n;
            if (s1 == 0 || s2 == 0 || s3 == 0) T[a][b] |= B(c);
        }
    }
    u128 earlier = 0;    /* bit d set: divisor d is earlier in the list */
    int found = 0;
    for (int g = 1; g < n && !found; g++) if (n % g == 0) {
        for (int v = 0; v < n; v++) { G[v] = 0; for (int w = 0; w < n; w++) if (w != v && (earlier >> gcd((w - v + n) % n, n) & 1)) G[v] |= B(w); }
        if (!(pairbad[0] >> g & 1) && !(G[0] >> g & 1)) {
            cs[0] = 0; cs[1] = g;
            u128 f = B(0) | B(g) | pairbad[0] | pairbad[g] | G[0] | G[g] | T[0][g];
            /* elements below g other than 0 are still candidates: search all of 1..n-1 */
            if (rec(2, 1, f)) found = 1;
        }
        earlier |= B(g);
    }
    printf("sym n=%d k=%d %s nodes=%lld", n, k, found ? "FOUND" : "NONE", nodes);
    if (found) { printf(" :"); for (int i = 0; i < k; i++) printf(" %d", cs[i]); }
    printf("\n");
    return 0;
}
