// 3-rank of class group (narrow for real) of quadratic fields via reduced forms, own implementation.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef long long ll;
static unsigned *spf; static ll NSPF;
static ll isqrt_(ll n){ ll r=(ll)sqrtl((long double)n); while(r*r>n)r--; while((r+1)*(r+1)<=n)r++; return r;}
static ll fdiv(ll a, ll b){ ll q=a/b; if((a%b!=0)&&((a<0)!=(b<0)))q--; return q;}
static ll egcd(ll a, ll b, ll*x, ll*y){ // returns g>=0, a x + b y = g
  ll x0=1,y0=0,x1=0,y1=1;
  while(b){ ll q=a/b; ll t=a-q*b;a=b;b=t; t=x0-q*x1;x0=x1;x1=t; t=y0-q*y1;y0=y1;y1=t;}
  if(a<0){a=-a;x0=-x0;y0=-y0;} *x=x0;*y=y0; return a;}
typedef struct{ll a,b,c;} F;
static ll D, SD; // SD=isqrt(|D|) for D>0
// Cohen Alg 5.4.7 composition, a>0
static F compose(F f1, F f2){
  if(f1.a>f2.a){F t=f1;f1=f2;f2=t;}
  ll s=(f1.b+f2.b)/2, n=f2.b-s, y1,x2,y2,d,d1,u,v;
  if(f2.a%f1.a==0){y1=0;d=f1.a;} else { d=egcd(f2.a,f1.a,&u,&v); y1=u; }
  if(s%d==0){y2=-1;x2=0;d1=d;} else { d1=egcd(s,d,&u,&v); x2=u; y2=-v; }
  ll v1=f1.a/d1, v2=f2.a/d1;
  ll r=((y1*y2%v1)*(n%v1) - x2*(f2.c%v1))%v1; r%=v1; if(r<0)r+=v1;
  F g; g.b=f2.b+2*v2*r; g.a=v1*v2; g.c=(f2.c*d1 + r*(f2.b+v2*r))/v1;
  // normalise to b in range & recompute c from disc
  return g;
}
static F red_neg(F f){
  for(;;){
    if(!(-f.a<f.b && f.b<=f.a)){ ll q=fdiv(f.a-f.b,2*f.a); f.b+=2*q*f.a; f.c=(f.b*f.b-D)/(4*f.a);}
    if(f.a>f.c){ ll t=f.a; f.a=f.c; f.c=t; f.b=-f.b; continue; }
    if(f.a==f.c && f.b<0) f.b=-f.b;
    return f; }
}
static int isred_pos(F f){ ll a=f.a<0?-f.a:f.a; return f.b>0 && f.b<=SD && f.b+2*a>SD && 2*a<=f.b+SD; }
static F rho(F f){ // Cohen rho for indefinite forms
  ll ac=f.c<0?-f.c:f.c, b;
  if(ac<=SD){ // largest b' = -b mod 2ac with b'<=SD
    ll m=2*ac; ll t=(-f.b)%m; if(t<0)t+=m; // t in [0,m)
    // want b' = SD - ((SD - t) mod m)
    ll k=(SD-t)%m; if(k<0)k+=m; b=SD-k;
  } else { ll m=2*ac; ll t=(-f.b)%m; if(t<0)t+=m; // want in (-ac,ac]
    b=t; if(b>ac)b-=m; }
  F g; g.a=f.c; g.b=b; g.c=(b*b-D)/(4*f.c); return g;
}
static F red_pos(F f){ int guard=0; while(!isred_pos(f)){ f=rho(f); if(++guard>100000){fprintf(stderr,"redloop D=%lld\n",D);exit(1);} } return f; }

static int divs[20000]; 
static int gen_divs(ll N){ // all divisors of N into divs (N<NSPF)
  int cnt=1; divs[0]=1; ll n=N;
  while(n>1){ unsigned p=spf[n]; int e=0; while(n%p==0){n/=p;e++;}
    int c0=cnt; ll pw=1; for(int i=1;i<=e;i++){pw*=p; for(int j=0;j<c0;j++) divs[cnt++]=divs[j]*pw;} }
  return cnt;
}
#define HB 18
#define HS (1<<HB)
static ll hkey[HS]; static int hval[HS]; static int hstamp[HS]; static int stampc=0;
static inline ll mk(ll a,ll b){ return (a+(1<<20))*(1<<21)+b; }
static inline unsigned hh(ll k){ return (unsigned)((k*0x9E3779B97F4A7C15ULL)>>(64-HB)); }
static void hput(ll k,int v){ unsigned h=hh(k); while(hstamp[h]==stampc && hkey[h]!=k) h=(h+1)&(HS-1); hstamp[h]=stampc;hkey[h]=k;hval[h]=v;}
static int hget(ll k){ unsigned h=hh(k); while(hstamp[h]==stampc){ if(hkey[h]==k) return hval[h]; h=(h+1)&(HS-1);} return -2; }
static F *forms; static int *cyc; static int nforms_cap=0;
static ll gcd3(ll a,ll b,ll c){ a=llabs(a);b=llabs(b);c=llabs(c); while(b){ll t=a%b;a=b;b=t;} while(c){ll t=a%c;a=c;c=t;} return a;}
// returns 3-rank r (>=0) ; also class number via *hout. mode: D<0 imag, D>0 real(narrow)
static int rank3(ll DD, ll *hout){
  D=DD; int nf=0;
  if(nforms_cap==0){ nforms_cap=1<<20; forms=malloc(sizeof(F)*nforms_cap); cyc=malloc(sizeof(int)*nforms_cap);}
  if(D<0){
    ll aD=-D; ll bmax=isqrt_(aD/3);
    for(ll b=aD&1; b<=bmax; b+=2){ ll N=(b*b+aD)/4; int nd=gen_divs(N);
      for(int i=0;i<nd;i++){ ll a=divs[i]; if(a<b) continue; ll c=N/a; if(c<a) continue;
        if(gcd3(a,b,c)!=1) continue;
        F f={a,b,c}; forms[nf++]=f;
        if(b>0 && b<a && a<c){ F g={a,-b,c}; forms[nf++]=g; } } }
    *hout=nf;
    if(nf%3) return 0;
    int cnt=0; F id={1,D&1,(((D&1)-D)/4)};
    for(int i=0;i<nf;i++){ F f=forms[i]; F g=red_neg(compose(f,f)); g=red_neg(compose(g,f)); if(g.a==1&&g.b==id.b) cnt++; }
    int r=0; ll p=1; while(p<cnt){p*=3;r++;} if(p!=cnt){fprintf(stderr,"nonpower3 D=%lld cnt=%d\n",D,cnt);exit(2);}
    // sanity: 3^r divides h
    return r;
  } else {
    SD=isqrt_(D);
    for(ll b=D&1; b<=SD; b+=2){ if(b==0) continue; ll N=(D-b*b)/4; if(N<=0) continue; int nd=gen_divs(N);
      for(int i=0;i<nd;i++){ ll a=divs[i]; if(!(2*a+b>SD && 2*a<=b+SD)) continue; // sqrtD-b<2a<sqrtD+b
        ll c=N/a; if(gcd3(a,b,c)!=1) continue;
        F f={a,b,-c}; forms[nf++]=f; F g={-a,b,c}; forms[nf++]=g; } }
    stampc++; for(int i=0;i<nf;i++) hput(mk(forms[i].a,forms[i].b),i);
    for(int i=0;i<nf;i++) cyc[i]=-1;
    int ncyc=0; static int rep[200000]; 
    for(int i=0;i<nf;i++) if(cyc[i]<0){ int j=i; int r0=-1; do{ cyc[j]=ncyc; if(forms[j].a>0&&r0<0) r0=j; F g=rho(forms[j]); int k=hget(mk(g.a,g.b)); if(k<0||forms[k].c!=g.c){fprintf(stderr,"rho not closed D=%lld\n",D);exit(3);} j=k; }while(j!=i); rep[ncyc++]=r0; }
    *hout=ncyc;
    if(ncyc%3) return 0;
    F id; id.a=1; id.b=SD-(((SD-D)&1)?1:0); id.c=(id.b*id.b-D)/4;
    int idk=hget(mk(id.a,id.b)); if(idk<0){fprintf(stderr,"no principal D=%lld\n",D);exit(4);} int idc=cyc[idk];
    int cnt=0;
    for(int t=0;t<ncyc;t++){ F f=forms[rep[t]]; F g=red_pos(compose(f,f)); if(g.a<0){ /*find pos rep not needed: rho*/ }
      // g reduced; need a>0 for compose: step via rho if a<0
      if(g.a<0) g=rho(g);
      g=compose(g,f); g=red_pos(g); int k=hget(mk(g.a,g.b)); if(k<0){fprintf(stderr,"lookup fail D=%lld\n",D);exit(5);} if(cyc[k]==idc) cnt++; }
    int r=0; ll p=1; while(p<cnt){p*=3;r++;} if(p!=cnt){fprintf(stderr,"nonpower3 real D=%lld cnt=%d\n",D,cnt);exit(2);}
    return r;
  }
}
static int isfund(ll d){ // d>0 or <0 nonzero
  ll m=d; if(m<0)m=-m;
  if((d&3)==1 || (d&3)==-3) { /* d mod 4 ==1 */ }
  ll dm=((d%4)+4)%4;
  if(dm==1){ // squarefree
    for(ll p=3;p*p<=m;p+=2) if(m%(p*p)==0) return 0; return 1; }
  if(dm==0){ ll q=d/4; ll qm=((q%4)+4)%4; if(qm!=2&&qm!=3) return 0; ll mm=q<0?-q:q; if(mm%4==0)return 0; for(ll p=3;p*p<=mm;p+=2) if(mm%(p*p)==0) return 0; return 1;}
  return 0;
}
int main(int argc,char**argv){
  if(argc<3){ // test mode: print class number & rank for given D
    return 1; }
  if(strcmp(argv[1],"D")==0){ NSPF=3000000; spf=calloc(NSPF+1,4); for(ll i=2;i<=NSPF;i++) if(!spf[i]) for(ll j=i;j<=NSPF;j+=i) if(!spf[j]) spf[j]=i;
    for(int i=2;i<argc;i++){ ll DD=atoll(argv[i]); ll h; int r=rank3(DD,&h); printf("%lld h=%lld r=%d\n",DD,h,r);} return 0; }
  ll lo=atoll(argv[1]), hi=atoll(argv[2]);
  NSPF=hi+10; if(NSPF<3000000)NSPF=3000000; spf=calloc(NSPF+1,4);
  for(ll i=2;i<=NSPF;i++) if(!spf[i]) for(ll j=i;j<=NSPF;j+=i) if(!spf[j]) spf[j]=i;
  static ll cnt[8][3]; memset(cnt,0,sizeof cnt); ll viol=0;
  for(ll d=lo+1; d<=hi; d++){
    if(d==1||!isfund(d)) continue;
    ll h; int r=rank3(d,&h);
    ll dd = (d%3==0)? -(d/3) : -3*d;
    if(!isfund(dd)){fprintf(stderr,"mirror not fund d=%lld\n",d);exit(9);}
    ll h2; int r2=rank3(dd,&h2);
    int e=r2-r; if(e<0||e>1){viol++; fprintf(stderr,"SCHOLZ VIOLATION d=%lld r=%d r'=%d\n",d,r,r2);}
    else cnt[r<7?r:7][e]++;
  }
  for(int r=0;r<8;r++) printf("%d %lld %lld\n",r,cnt[r][0],cnt[r][1]);
  printf("viol %lld\n",viol);
  return 0; }
