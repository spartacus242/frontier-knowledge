// Count 3-ranks of quadratic fields via binary cubic forms (Delone-Faddeev / Hasse):
// for a fundamental discriminant D != -3,-4, the number of GL2(Z)-classes of IRREDUCIBLE
// binary cubic forms of discriminant D equals (3^r - 1)/2, r = 3-rank of Cl(Q(sqrt D)).
// Classes are enumerated by reduction theory written from scratch:
//  D>0: Hessian H=(P,Q,R) positive definite, reduced 0<=Q<=P<=R (GL2), a>=1.
//  D<0: f = a (x - w y)(x^2 + s x y + t y^2); real quadratic factor reduced 0<=s<=1<=t, a>=1
//       <=> (1) bc>=ad, (2) (a-b)^2 + c(a-b) + ad >= 0, (3) d^2-a^2 >= bd-ac.
//  On a boundary the form is counted iff it is the lexicographic maximum among all
//  +-f o g (g in GL2 with entries in {-1,0,1}) that lie in the closed domain with a'>=1.
// Reducible forms with a>=1 can only occur for non-fundamental D (argued in report); counts for
// non-fundamental D are garbage and never read.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef long long ll;
typedef long double ld;

static int MODE; // 0 = dump (uint16 arrays indexed by |D|), 1 = segment positive (A), 2 = mirror high (3|n), 3 = mirror low (3 !| n)
static uint16_t *dumpc; static ll dumpN;
static uint8_t *ARR; static ll SEG0, SEG1; // d range [SEG0,SEG1)
static ll nhit = 0;

static inline void nib_inc(ll d) {
  if (d < SEG0 || d >= SEG1) return;
  ll k = (d - SEG0) >> 2; int sl = (int)((d - SEG0) & 3); // SEG0 multiple of 4
  if (sl == 1) ARR[k] = (ARR[k] & 0xF0) | ((ARR[k] + 1) & 0x0F);
  else if (sl == 0) ARR[k] += 0x10;
}
static inline void hit(ll n) { // n = |D|
  nhit++;
  switch (MODE) {
  case 0: if (n <= dumpN) dumpc[n]++; break;
  case 1: nib_inc(n); break;
  case 2: if (n % 3 == 0 && n % 9 != 0) nib_inc(n / 3); break;
  case 3: if (n % 3 != 0) nib_inc(3 * n); break;
  }
}
static ll fdiv(ll a, ll b) { ll q = a / b; if ((a % b != 0) && ((a < 0) != (b < 0))) q--; return q; }
static ll cdiv(ll a, ll b) { return -fdiv(-a, b); }

static void transform(ll a, ll b, ll c, ll d, int al, int be, int ga, int de, ll *o) {
  o[0] = a*al*al*al + b*al*al*ga + c*al*ga*ga + d*ga*ga*ga;
  o[1] = 3*a*al*al*be + b*(al*al*de + 2*al*be*ga) + c*(ga*ga*be + 2*al*ga*de) + 3*d*ga*ga*de;
  o[2] = 3*a*al*be*be + b*(be*be*ga + 2*al*be*de) + c*(al*de*de + 2*be*ga*de) + 3*d*ga*de*de;
  o[3] = a*be*be*be + b*be*be*de + c*be*de*de + d*de*de*de;
}
static int lexgt(const ll *x, const ll *y) { for (int i = 0; i < 4; i++) { if (x[i] != y[i]) return x[i] > y[i]; } return 0; }
static int in_pos(const ll *f) { // closed domain D>0, a>=1
  ll a=f[0],b=f[1],c=f[2],d=f[3]; if (a < 1) return 0;
  ll P=b*b-3*a*c, Q=b*c-9*a*d, R=c*c-3*b*d; return 0<=Q && Q<=P && P<=R;
}
static int in_neg(const ll *f) {
  ll a=f[0],b=f[1],c=f[2],d=f[3]; if (a < 1) return 0;
  return b*c >= a*d && (a-b)*(a-b) + c*(a-b) + a*d >= 0 && d*d - a*a >= b*d - a*c;
}
static int canon(ll a, ll b, ll c, ll d, int neg) {
  ll f[4] = {a,b,c,d}, g[4];
  for (int al=-1; al<=1; al++) for (int be=-1; be<=1; be++) for (int ga=-1; ga<=1; ga++) for (int de=-1; de<=1; de++) {
    int det = al*de - be*ga; if (det != 1 && det != -1) continue;
    transform(a,b,c,d,al,be,ga,de,g);
    for (int sg = 0; sg < 2; sg++) {
      if (sg) for (int i=0;i<4;i++) g[i] = -g[i];
      if ((neg ? in_neg(g) : in_pos(g)) && lexgt(g, f)) return 0;
    }
  }
  return 1;
}

// positive discriminants D in [Lo,Hi]
static void enum_pos(ll Lo, ll Hi) {
  if (Lo < 1) Lo = 1; if (Hi < Lo) return;
  ld sH = sqrtl((ld)Hi);
  ll Pmax = (ll)floorl(sH) + 1;
  ll amax = (ll)floorl(sqrtl(4*sH/27)) + 1;
  for (ll a = 1; a <= amax; a++) {
    ll Pmin = (ll)floorl(cbrtl(27.0L*a*a*(ld)Lo/4)) - 1; if (Pmin < 1) Pmin = 1;
    if (Pmin > Pmax) continue;
    ll bmax = (ll)ceill(1.5L*a + 2*sqrtl(3.0L)*sqrtl((ld)Pmax)) + 2;
    for (ll b = -bmax; b <= bmax; b++) {
      ll clo = cdiv(b*b - Pmax, 3*a), chi = fdiv(b*b - Pmin, 3*a);
      ll cc = (b > 0 ? b : 0) - 3*a; if (chi > cc) chi = cc;
      for (ll c = clo; c <= chi; c++) {
        ll P = b*b - 3*a*c; if (P < 1) continue;
        ll dlo = cdiv(b*c - P, 9*a), dhi = fdiv(b*c, 9*a);
        ll Rlo = cdiv(3*Lo, 4*P); if (Rlo < P) Rlo = P;
        ll Rhi = fdiv(3*Hi + P*P, 4*P);
        if (Rhi < Rlo) continue;
        if (b > 0) { ll l = cdiv(c*c - Rhi, 3*b), h = fdiv(c*c - Rlo, 3*b); if (l > dlo) dlo = l; if (h < dhi) dhi = h; }
        else if (b < 0) { ll B = 3*b; ll l = cdiv(c*c - Rlo, B), h = fdiv(c*c - Rhi, B); if (l > dlo) dlo = l; if (h < dhi) dhi = h; }
        else { if (c*c < Rlo || c*c > Rhi) continue; }
        for (ll d = dlo; d <= dhi; d++) {
          ll Q = b*c - 9*a*d, R = c*c - 3*b*d;
          if (Q < 0 || Q > P || R < P) continue;
          ll T = 4*P*R - Q*Q; ll D = T / 3;
          if (D < Lo || D > Hi) continue;
          if ((Q == 0 || Q == P || P == R) && !canon(a,b,c,d,0)) continue;
          hit(D);
        }
      }
    }
  }
}

// negative discriminants, |D| in [Lo,Hi]; need3: 1 -> only 3 | D (d stepped by 3)
static void enum_neg(ll Lo, ll Hi, int need3) {
  if (Lo < 1) Lo = 1; if (Hi < Lo) return;
  ll amax = (ll)floorl(powl(16.0L*Hi/27, 0.25L)) + 1;
  ld W4 = powl((ld)Hi/3, 0.25L);
  for (ll a = 1; a <= amax; a++) {
    ld Tmax = 0.25L + cbrtl((ld)Hi/(4.0L*a*a*a*a));
    ll blo = (ll)floorl(-W4) - 1, bhi = (ll)ceill(1.5L*a + W4) + 1;
    for (ll b = blo; b <= bhi; b++) {
      ld be = (ld)b / a;
      ld mn = be - 1 < 0 ? be - 1 : 0;
      ld mx = (be >= 0 && be <= 2) ? be*be/4 : (be < 0 ? 0 : be - 1);
      ll clo = (ll)floorl(a*(1 + mn)) - 1, chi = (ll)ceill(a*(Tmax + mx)) + 1;
      int bm3 = (int)(((b % 3) + 3) % 3);
      for (ll c = clo; c <= chi; c++) {
        ll dlo = cdiv(-(a-b)*(a-b) - c*(a-b), a), dhi = fdiv(b*c, a);
        if (dlo > dhi) continue;
        ld A2 = 27.0L*a*a, B = 18.0L*a*b*c - 4.0L*b*b*b, C = (ld)b*b*c*c - 4.0L*a*c*c*c;
        ld disc1 = B*B + 4*A2*(C + Hi);
        if (disc1 < 0) continue;
        ld s1 = sqrtl(disc1);
        ll r1 = (ll)floorl((B - s1)/(2*A2)) - 1, r2 = (ll)ceill((B + s1)/(2*A2)) + 1;
        if (r1 > dlo) dlo = r1; if (r2 < dhi) dhi = r2;
        if (dlo > dhi) continue;
        // excluded open region where |D| < Lo i.e. D(d) > -Lo
        ll e1 = dhi + 1, e2 = dhi; // exclude [e1,e2] (safe inner)
        ld disc2 = B*B + 4*A2*(C + Lo);
        if (disc2 > 0) { ld s2 = sqrtl(disc2); e1 = (ll)ceill((B - s2)/(2*A2)) + 1; e2 = (ll)floorl((B + s2)/(2*A2)) - 1; }
        ll step = 1, start = dlo;
        if (need3) {
          ll cm = ((c % 3) + 3) % 3, am = ((a % 3) + 3) % 3;
          if (bm3 == 0) { if ((am * cm) % 3 != 0) continue; }
          else {
            ll t = (bm3*bm3*cm*cm - am*cm*cm*cm) % 3; t = (t + 3) % 3; // b^2c^2 - a c^3
            ll dm = (bm3 * t) % 3; // d = b*(...) mod 3
            ll s0 = ((dlo % 3) + 3) % 3; start = dlo + ((dm - s0 + 3) % 3); step = 3;
          }
        }
        for (ll d = start; d <= dhi; d += step) {
          if (d >= e1 && d <= e2) { if (step == 1) { d = e2; continue; } else { d += ((e2 - d) / 3) * 3; continue; } }
          ll D = b*b*c*c - 4*a*c*c*c - 4*b*b*b*d - 27*a*a*d*d + 18*a*b*c*d;
          if (D > -Lo || D < -Hi) continue;
          ll t3 = d*d - a*a - b*d + a*c; if (t3 < 0) continue;
          ll t1 = b*c - a*d, t2 = (a-b)*(a-b) + c*(a-b) + a*d;
          if ((t1 == 0 || t2 == 0 || t3 == 0) && !canon(a,b,c,d,1)) continue;
          hit(-D);
        }
      }
    }
  }
}

static int rank_of(int v) { switch (v) { case 0: return 0; case 1: return 1; case 4: return 2; case 13: return 3; case 8: return 4; case 9: return 5; } return -1; }

int main(int argc, char **argv) {
  if (argc >= 3 && !strcmp(argv[1], "dump")) {
    // print counts for all |D| <= N: "D cnt" for D>0 and D<0
    dumpN = atoll(argv[2]); MODE = 0;
    dumpc = calloc(dumpN + 1, 2); enum_pos(1, dumpN);
    for (ll n = 1; n <= dumpN; n++) if (dumpc[n]) printf("%lld %d\n", n, dumpc[n]);
    memset(dumpc, 0, 2*(dumpN+1)); enum_neg(1, dumpN, 0);
    for (ll n = 1; n <= dumpN; n++) if (dumpc[n]) printf("%lld %d\n", -n, dumpc[n]);
    return 0;
  }
  if (argc >= 5 && !strcmp(argv[1], "seg")) {
    // seg d0 d1 outfile : d in [d0,d1), d0 % 4 == 0
    SEG0 = atoll(argv[2]); SEG1 = atoll(argv[3]);
    ll L = SEG1 - SEG0; ll nb = (L >> 2) + 1;
    ARR = malloc(nb); uint8_t *MIR = malloc(nb);
    // checkpoints
    ll cp[76]; for (int k = 30; k <= 105; k++) cp[k-30] = llround(pow(10.0, k/10.0));
    static ll cnt[76][6][2]; memset(cnt, 0, sizeof cnt); ll bad = 0, badpair = 0;
    memset(ARR, 0, nb); MODE = 1; nhit = 0; enum_pos(SEG0, SEG1 - 1);
    fprintf(stderr, "pos hits %lld\n", nhit);
    uint8_t *A = ARR; ARR = MIR; memset(ARR, 0, nb); MODE = 2; nhit = 0;
    enum_neg(3*SEG0, 3*(SEG1-1), 1);
    fprintf(stderr, "neg-high hits %lld\n", nhit);
    MODE = 3; nhit = 0; enum_neg(cdiv(SEG0, 3), fdiv(SEG1 - 1, 3), 0);
    fprintf(stderr, "neg-low hits %lld\n", nhit);
    // join with squarefree sieve in blocks
    const ll BL = 1 << 22; uint8_t *sq = malloc(BL);
    ll pmax = (ll)sqrt((double)SEG1) + 2; char *isc = calloc(pmax + 1, 1);
    for (ll i = 2; i * i <= pmax; i++) if (!isc[i]) for (ll j = i*i; j <= pmax; j += i) isc[j] = 1;
    int bin = 0;
    for (ll B0 = SEG0; B0 < SEG1; B0 += BL) {
      ll B1 = B0 + BL; if (B1 > SEG1) B1 = SEG1;
      memset(sq, 0, BL);
      for (ll p = 3; p <= pmax; p += 2) if (!isc[p]) { ll p2 = p*p; if (p2 >= B1) break; ll s = ((B0 + p2 - 1) / p2) * p2; for (ll m = s; m < B1; m += p2) sq[m - B0] = 1; }
      for (ll d = B0; d < B1; d++) {
        if (d < 5) continue;
        int m16 = (int)(d & 15);
        if (!((d & 3) == 1 || m16 == 8 || m16 == 12)) continue;
        if (sq[d - B0]) continue;
        ll k = (d - SEG0) >> 2; int sl = (int)((d - SEG0) & 3);
        int ca = sl == 1 ? (A[k] & 15) : (A[k] >> 4), cm = sl == 1 ? (MIR[k] & 15) : (MIR[k] >> 4);
        int r = rank_of(ca), rp = rank_of(cm);
        if (d == 12) rp = 0; // mirror Q(sqrt -1): special (D=-4 has extra automorphisms); h=1
        if (r < 0 || rp < 0) { bad++; if (bad < 20) fprintf(stderr, "BAD d=%lld ca=%d cm=%d\n", d, ca, cm); continue; }
        int e = rp - r; if (e < 0 || e > 1) { badpair++; if (badpair < 20) fprintf(stderr, "SCHOLZ FAIL d=%lld r=%d r'=%d\n", d, r, rp); continue; }
        while (bin < 76 && d > cp[bin]) bin++;
        if (bin >= 76) continue;
        cnt[bin][r][e]++;
      }
    }
    FILE *fo = fopen(argv[4], "w");
    fprintf(fo, "# seg %lld %lld bad %lld badpair %lld\n", SEG0, SEG1, bad, badpair);
    for (int i = 0; i < 76; i++) { fprintf(fo, "%d", i); for (int r = 0; r < 6; r++) for (int e = 0; e < 2; e++) fprintf(fo, " %lld", cnt[i][r][e]); fprintf(fo, "\n"); }
    fclose(fo);
    return 0;
  }
  fprintf(stderr, "usage\n"); return 1;
}
