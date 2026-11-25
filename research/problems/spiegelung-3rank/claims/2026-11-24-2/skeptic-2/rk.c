// From-scratch 3-rank computation. Real: narrow class group via reduced indefinite forms+rho cycles.
// Imag: reduced definite forms. 3-rank = log3 #{classes with f^3=1}.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef long long ll;
static ll fdiv(ll x,ll y){ ll q=x/y; if((x%y!=0)&&((x<0)!=(y<0)))q--; return q;}
static ll md(ll a, ll m){ ll r=a%m; if(r<0)r+=m; return r;}
static ll egcd(ll a, ll b, ll *x, ll *y){ ll x0=1,y0=0,x1=0,y1=1;
  while(b){ ll q=a/b,t=a-q*b; a=b;b=t; t=x0-q*x1;x0=x1;x1=t; t=y0-q*y1;y0=y1;y1=t;}
  *x=x0;*y=y0;return a;}
typedef struct {ll a,b,c;} F;
static F comp(F f,F g){
  if(f.a>g.a){F t=f;f=g;g=t;}
  ll s=(f.b+g.b)/2, n=g.b-s, y1,y2,x2,u,v,d,d1;
  if(g.a%f.a==0){y1=0;d=f.a;} else {d=egcd(g.a,f.a,&u,&v); y1=u;}
  if(s%d==0){y2=-1;x2=0;d1=d;} else {ll as=s<0?-s:s; d1=egcd(as,d,&u,&v); if(s<0)u=-u; x2=u;y2=-v;}
  ll v1=f.a/d1,v2=g.a/d1;
  __int128 rr=(__int128)y1*y2*n-(__int128)g.c*x2; ll r=(ll)(rr%v1); if(r<0)r+=v1;
  F h; h.b=g.b+2*v2*r; h.a=v1*v2;
  __int128 num=(__int128)g.c*d1+(__int128)r*(g.b+(__int128)v2*r);
  h.c=(ll)(num/v1); return h;}
// ---- imaginary ----
static F redim(F f, ll D){
  for(;;){
    ll k=fdiv(f.a-f.b,2*f.a); ll nb=f.b+2*f.a*k; f.b=nb; f.c=(nb*nb-D)/(4*f.a);
    if(f.a>f.c){ ll t=f.a;f.a=f.c;f.c=t;f.b=-f.b; continue;}
    if(f.a==f.c&&f.b<0) f.b=-f.b;
    return f;}}
static int rank3_imag(ll D){ // D<0
  ll A=(ll)sqrt((double)(-D)/3.0)+2; int cnt=0; ll par=md(D,2);
  for(ll a=1;a<=A;a++){ for(ll b=-a+1;b<=a;b++){
    if(md(b,2)!=par) continue;
    ll t=b*b-D; if(t%(4*a)) continue; ll c=t/(4*a);
    if(c<a) continue; if(a==c&&b<0) continue; if(a==c&&0) continue;
    if(a>c) continue;
    F f={a,b,c}; F g=redim(comp(f,f),D); g=redim(comp(g,f),D);
    if(g.a==1) cnt++;
  }}
  int r=0; while(cnt>1){ if(cnt%3){return -1;} cnt/=3; r++;} return r;}
// ---- real ----
static ll S; static ll DD;
static int isred(ll a,ll b){ ll m=a<0?-a:a; if(b<=0||b>S) return 0;
  if((2*m+b)*(2*m+b)<=DD) return 0; ll t=2*m-b; if(t<0) return 1; return t*t<DD; }
static F rho(F f){ ll c=f.c, m=c<0?-c:c; ll nb;
  if(m<=S) nb=S-md(S+f.b,2*m); else nb=m-md(m+f.b,2*m);
  F g; g.a=c; g.b=nb; g.c=(nb*nb-DD)/(4*c); return g;}
static int *lab=0,*stamp=0; static size_t cap=0; static int gen=0;
static inline size_t key(ll a,ll b){ ll m=a<0?-a:a; return ((size_t)(b*(S+2)+m))*2+(a<0);}
static int rank3_real(ll D, int *hplus){
  DD=D; S=(ll)sqrt((double)D); while(S*S>D)S--; while((S+1)*(S+1)<=D)S++;
  size_t need=(size_t)(S+2)*(S+2)*2+8; if(need>cap){cap=need; lab=realloc(lab,cap*sizeof(int)); stamp=realloc(stamp,cap*sizeof(int)); memset(stamp,0,cap*sizeof(int)); gen=0;}
  gen++;
  ll par=md(D,2); int ncyc=0; int nf=0;
  static F *reps=0; static size_t repcap=0; if(!reps){repcap=1<<20; reps=malloc(repcap*sizeof(F));}
  // enumerate
  for(ll b=1;b<=S;b++){ if(md(b,2)!=par) continue; ll m=(D-b*b)/4;
    ll lo=(S-b)/2-1; if(lo<1)lo=1; ll hi=(S+b)/2+2;
    for(ll a=lo;a<=hi;a++){ if(m%a) continue; if(!isred(a,b)) continue;
      // forms (a,b,-m/a)? a*c=(b^2-D)/4=-m so c=-m/a
      for(int sg=0;sg<2;sg++){ ll aa=sg?-a:a; size_t k=key(aa,b); stamp[k]=gen; lab[k]=-1; nf++; }
    }}
  // cycles
  ll b0=(md(S,2)==par)?S:S-1; F pr={1,b0,(b0*b0-D)/4};
  int principal=-1;
  for(ll b=1;b<=S;b++){ if(md(b,2)!=par) continue; ll m=(D-b*b)/4; ll lo=(S-b)/2-1; if(lo<1)lo=1; ll hi=(S+b)/2+2;
    for(ll a=lo;a<=hi;a++){ if(m%a) continue; if(!isred(a,b)) continue;
      for(int sg=0;sg<2;sg++){ ll aa=sg?-a:a; size_t k=key(aa,b); if(lab[k]>=0) continue;
        F f={aa,b,-(m/a)*(sg?-1:1)*(-1)}; // c: a*c=-m => c=-m/aa
        f.c=-m/aa;
        int id=ncyc++; F cur=f; int have=0; 
        for(;;){ size_t kk=key(cur.a,cur.b); if(lab[kk]>=0) break; lab[kk]=id; if(cur.a>0&&!have){ if((size_t)ncyc>repcap){} reps[id]=cur; have=1;} cur=rho(cur); }
        if(!have){ cur=rho(f); reps[id]=cur; /* a<0 start; neighbor positive */ }
        if(!have){ // find a positive member
          F x=f; for(;;){ if(x.a>0){reps[id]=x;break;} x=rho(x);} }
      }}}
  { F x=pr; size_t kk=key(x.a,x.b); if(stamp[kk]!=gen){fprintf(stderr,"principal not reduced D=%lld\n",D);exit(1);} principal=lab[kk]; }
  int t3=0;
  for(int id=0;id<ncyc;id++){ F f=reps[id];
    F g=comp(f,f), h;
    for(int pass=0;pass<2;pass++){
      if(pass==1) g=comp(h,f);
      int it=0; while(!(isred(g.a,g.b)&&g.a>0)){ g=rho(g); if(++it>100000){fprintf(stderr,"loop D=%lld\n",D);exit(1);} }
      h=g; }
    size_t kk=key(h.a,h.b); if(stamp[kk]!=gen){fprintf(stderr,"cube unreduced D=%lld\n",D);exit(1);}
    if(lab[kk]==principal) t3++; }
  *hplus=ncyc;
  int r=0; while(t3>1){ if(t3%3) return -1; t3/=3; r++; } return r; }
int main(int argc,char**argv){
  ll lo=atoll(argv[1]), hi=atoll(argv[2]);
  char *sf=calloc(hi+2,1); for(ll p=2;p*p<=hi;p++){ ll q=p*p; for(ll m=q;m<=hi;m+=q) sf[m]=1; }
  // optional mode: argv[3]=="v" print per d
  for(ll d=lo; d<=hi; d++){
    int fund=0;
    if(d%4==1) fund=!sf[d]; else if(d%4==0){ ll m=d/4; if(m%4==2||m%4==3) fund=!sf[m]; }
    if(!fund||d==1) continue;
    int hp; int r=rank3_real(d,&hp);
    ll Dm = (d%3==0)? -d/3 : -3*d;
    int rp=rank3_imag(Dm);
    printf("%lld %d %d\n",d,r,rp);
  }
  return 0;}
