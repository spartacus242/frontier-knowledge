// Independent recomputation: 3-ranks of quadratic fields via counting cubic fields
// (Davenport-Heilbronn/Delone-Faddeev + Hasse: #cubic fields of fundamental disc D = (3^r-1)/2).
// Enumerates binary cubic forms with (weakly) reduced covariant, canonicalises by explicit orbit closure.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
typedef long long ll;
static ll X1;            // bound on positive fundamental d
static uint8_t *CR,*C1,*C2; // real counts idx(d); imag n=3m idx(m); imag 3∤n idx(n), n<=X1/3
static inline ll fdiv(ll a, ll b){ ll q=a/b; if((a%b!=0)&&((a<0)!=(b<0))) q--; return q; }
static inline ll cdiv(ll a, ll b){ ll q=a/b; if((a%b!=0)&&((a<0)==(b<0))) q++; return q; }
static inline ll IDX(ll n){ return ((n>>2)<<1) + (n&1); }
static inline void inc(uint8_t *p){ if(*p<255) (*p)++; }

static int hasroot_mod(ll a,ll b,ll c,ll d,int p){
  int A=((a%p)+p)%p,B=((b%p)+p)%p,C=((c%p)+p)%p,Dd=((d%p)+p)%p;
  if(A==0) return 1; // root at infinity (x=1,y=0)
  for(int t=0;t<p;t++){ if((((A*t+B)%p*t+C)%p*t+Dd)%p==0) return 1; }
  return 0;
}
static inline __int128 evalF(ll a,ll b,ll c,ll d,ll x,ll y){
  return (__int128)a*x*x*x+(__int128)b*x*x*y+(__int128)c*x*y*y+(__int128)d*y*y*y;
}
static int irreducible(ll a,ll b,ll c,ll d){
  if(a==0||d==0) return 0;
  static const int ps[]={2,3,5,7,11,13};
  for(int i=0;i<6;i++) if(!hasroot_mod(a,b,c,d,ps[i])) return 1;
  // exact rational root test: root x/y, y|a, y>0, x|d
  ll aa=llabs(a), dd=llabs(d);
  for(ll y=1;y<=aa;y++){ if(aa%y) continue;
    for(ll x=1;x<=dd;x++){ if(dd%x) continue;
      if(evalF(a,b,c,d,x,y)==0||evalF(a,b,c,d,-x,y)==0) return 0; } }
  return 1;
}
typedef struct{ll a,b,c,d;} F;
static inline F norm(F f){ if(f.a<0){f.a=-f.a;f.b=-f.b;f.c=-f.c;f.d=-f.d;} return f; }
static int weakR(F f){ // real: Hessian |Q|<=P<=R
  ll P=f.b*f.b-3*f.a*f.c, Q=f.b*f.c-9*f.a*f.d, R=f.c*f.c-3*f.b*f.d;
  return llabs(Q)<=P && P<=R;
}
static int weakC(F f){ // complex, a>0
  ll a=f.a,b=f.b,c=f.c,d=f.d;
  if(a<=0) return 0;
  if(d*d-b*d+a*c-a*a<0) return 0;
  ll m=a*d-b*c;
  return m>=-(a-b)*(a-b)-a*c && m<=(a+b)*(a+b)+a*c;
}
static int cmpF(F x,F y){ if(x.a!=y.a)return x.a<y.a?-1:1; if(x.b!=y.b)return x.b<y.b?-1:1; if(x.c!=y.c)return x.c<y.c?-1:1; if(x.d!=y.d)return x.d<y.d?-1:1; return 0;}
static ll maxorb=0;
// is f the lex-max of the set of weakly reduced forms equivalent to it (mod sign)?
static int is_canon(F f,int real){
  F q[64]; int n=1,h=0; q[0]=f;
  while(h<n){ F g=q[h++]; F t[4];
    t[0]=(F){g.a,3*g.a+g.b,3*g.a+2*g.b+g.c,g.a+g.b+g.c+g.d};
    t[1]=(F){g.a,g.b-3*g.a,3*g.a-2*g.b+g.c,-g.a+g.b-g.c+g.d};
    t[2]=(F){g.d,g.c,g.b,g.a};
    t[3]=(F){g.a,-g.b,g.c,-g.d};
    for(int i=0;i<4;i++){ F u=norm(t[i]); if(u.a==0) continue;
      if(!(real?weakR(u):weakC(u))) continue;
      int seen=0; for(int j=0;j<n;j++) if(cmpF(q[j],u)==0){seen=1;break;}
      if(!seen){ if(n>=64){fprintf(stderr,"orbit overflow\n");exit(1);} q[n++]=u; } } }
  if(n>maxorb) maxorb=n;
  for(int j=0;j<n;j++) if(cmpF(q[j],f)>0) return 0;
  return 1;
}
static ll nreal=0,ncplx=0;
static void do_real(ll X){
  double sX=sqrt((double)X); ll isX=(ll)sX; while(isX*isX>X)isX--; while((isX+1)*(isX+1)<=X)isX++;
  ll amax=(ll)(2.0/(3.0*sqrt(3.0))*sqrt(sX))+1;
  for(ll a=1;a<=amax;a++){
    double t=sX-6.75*a*a; if(t<0)t=0; ll bmax=(ll)(1.5*a+sqrt(t))+2;
    for(ll b=0;b<=bmax;b++){
      ll clo=cdiv(b*b-isX,3*a), chi=fdiv(b*b-1,3*a);
      for(ll c=clo;c<=chi;c++){
        ll P=b*b-3*a*c; ll lo=cdiv(b*c-P,9*a), hi=fdiv(b*c+P,9*a);
        ll XP=X/P;
        if(b>0){ ll h2=fdiv(c*c-P,3*b), l2=cdiv(c*c-XP,3*b); if(h2<hi)hi=h2; if(l2>lo)lo=l2; }
        else { if(c*c<P||c*c>XP) continue; }
        for(ll d=lo;d<=hi;d++){
          ll Q=b*c-9*a*d, R=c*c-3*b*d;
          if(llabs(Q)>P||P>R) continue;
          ll D3=4*P*R-Q*Q; if(D3<=0||D3>3*X) continue; ll D=D3/3;
          if((D&3)>1) continue;
          if(llabs(Q)==P||P==R||Q==0){ if(!is_canon((F){a,b,c,d},1)) continue; }
          else if(!(b>0||d>0)) continue;
          if(!irreducible(a,b,c,d)) continue;
          nreal++; inc(&CR[IDX(D)]);
        } } } }
}
static void do_cplx(ll X){ // |D|<=X
  ll amax=(ll)pow(16.0*X/27.0,0.25)+1;
  for(ll a=1;a<=amax;a++){
    double t=sqrt(X/3.0)-0.75*a*a; if(t<0)t=0; ll bmax=(ll)(1.5*a+sqrt(t))+2;
    for(ll b=0;b<=bmax;b++){
      ll clo=cdiv(-(a*a+b*b),a), chi=(ll)((double)b*b/(3.0*a)+cbrt((double)X/(4.0*a)))+1;
      for(ll c=clo;c<=chi;c++){
        ll lo=cdiv(b*c-(a-b)*(a-b)-a*c,a), hi=fdiv(b*c+(a+b)*(a+b)+a*c,a);
        ll P=b*b-3*a*c; double M=27.0*a*a*(double)X+4.0*(double)P*P*P; if(M<0) continue;
        double sM=sqrt(M); ll g0=2*b*b*b-9*a*b*c; double den=27.0*a*a;
        ll l2=(ll)floor((-sM-g0)/den)-1, h2=(ll)ceil((sM-g0)/den)+1;
        if(l2>lo)lo=l2; if(h2<hi)hi=h2;
        for(ll d=lo;d<=hi;d++){
          ll e1=d*d-b*d+a*c-a*a; if(e1<0) continue;
          ll D=b*b*c*c-4*a*c*c*c-4*b*b*b*d-27*a*a*d*d+18*a*b*c*d;
          if(D>=0||-D>X) continue; ll n=-D;
          if((n&3)==1||(n&3)==2) continue;
          uint8_t *p;
          if(n%3==0){ ll m=n/3; if(m>X1||m%3==0) continue; p=&C1[IDX(m)]; }
          else { if(3*n>X1) continue; p=&C2[IDX(n)]; }
          ll m2=a*d-b*c;
          if(e1==0||m2==-(a-b)*(a-b)-a*c||m2==(a+b)*(a+b)+a*c){ if(!is_canon((F){a,b,c,d},0)) continue; }
          else if(!(b>0||d>0)) continue;
          if(!irreducible(a,b,c,d)) continue;
          ncplx++; inc(p);
        } } } }
}
static int rk(int c){ switch(c){case 0:return 0;case 1:return 1;case 4:return 2;case 13:return 3;case 40:return 4;case 121:return 5;} return -1; }
int main(int argc,char**argv){
  X1=atoll(argv[1]); const char*dump=argc>2?argv[2]:NULL;
  CR=calloc(X1/2+8,1); C1=calloc(X1/2+8,1); C2=calloc(X1/6+8,1);
  if(!CR||!C1||!C2){fprintf(stderr,"alloc\n");return 1;}
  do_real(X1); fprintf(stderr,"real forms counted %lld\n",nreal);
  do_cplx(3*X1); fprintf(stderr,"complex forms counted %lld maxorbit %lld\n",ncplx,maxorb);
  // squarefree bitmap for 1..X1
  uint8_t *sqb=malloc(X1/8+2); memset(sqb,0xff,X1/8+2);
  for(ll p=2;p*p<=X1;p++){ ll p2=p*p; if(p>2&&!(sqb[p>>3]>>(p&7)&1)) continue; for(ll m=p2;m<=X1;m+=p2) sqb[m>>3]&=~(1<<(m&7)); }
  #define SQF(m) ((sqb[(m)>>3]>>((m)&7))&1)
  ll n[4][2]; memset(n,0,sizeof n); ll bad=0,highr=0; int k=30; ll cp=llround(pow(10.0,k/10.0));
  FILE*df=dump?fopen(dump,"w"):NULL;
  printf("X,n00,n01,n10,n11,n20,n21,n30,n31\n");
  for(ll d=2;d<=X1;d++){
      while(d>cp){ printf("%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld\n",cp,n[0][0],n[0][1],n[1][0],n[1][1],n[2][0],n[2][1],n[3][0],n[3][1]); k++; cp=llround(pow(10.0,k/10.0)); }
      int fund=0;
      if((d&3)==1) fund=SQF(d);
      else if((d&3)==0){ ll m=d>>2; if((m&3)==2||(m&3)==3) fund=SQF(m); }
      if(!fund) continue;
      int r=rk(CR[IDX(d)]); ll mm=(d%3==0)?d/3:d; int rp=rk((d%3==0)?C2[IDX(mm)]:C1[IDX(mm)]);
      if(r<0||rp<0||rp-r<0||rp-r>1){ bad++; if(bad<20) fprintf(stderr,"ANOMALY d=%lld cR=%d cI=%d\n",d,CR[IDX(d)],(d%3==0)?C2[IDX(mm)]:C1[IDX(mm)]); continue; }
      if(r>3){highr++; continue;}
      n[r][rp-r]++;
      if(df) fprintf(df,"%lld %d %d\n",d,r,rp);
  }
  while(cp<=X1){ printf("%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld,%lld\n",cp,n[0][0],n[0][1],n[1][0],n[1][1],n[2][0],n[2][1],n[3][0],n[3][1]); k++; cp=llround(pow(10.0,k/10.0)); }
  fprintf(stderr,"anomalies %lld, r>3: %lld\n",bad,highr);
  return 0;
}
