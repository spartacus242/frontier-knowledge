// Independent direct check: 3-rank of class groups of quadratic fields via binary quadratic forms.
// Counts classes g with g^3 = 1 (=3^r). Imaginary: reduced definite forms. Real: cycles of reduced indefinite forms (narrow class group).
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
typedef long long ll; typedef __int128 LL;
typedef struct{ll a,b,c;} Q;
static ll fdiv(ll a,ll b){ll q=a/b; if((a%b!=0)&&((a<0)!=(b<0)))q--; return q;}
static ll isqrt(ll n){ll r=(ll)sqrt((double)n); while(r*r>n)r--; while((r+1)*(r+1)<=n)r++; return r;}
static ll xg(ll a,ll b,ll*u,ll*v){ if(b==0){*u=(a<0)?-1:1;*v=0;return llabs(a);} ll u1,v1; ll g=xg(b,a%b,&u1,&v1); *u=v1; *v=u1-(a/b)*v1; return g; }
static Q red_def(Q f,ll D){ // positive definite reduction, D<0
  for(;;){ ll a=f.a,b=f.b;
    if(b>a||b<=-a){ ll k=fdiv(b+a,2*a); b-=2*k*a; if(b<=-a) b+=2*a; f.b=b; f.c=(ll)(((LL)b*b-D)/(4*a)); }
    if(f.a>f.c){ ll t=f.a; f.a=f.c; f.c=t; f.b=-f.b; continue; }
    if(f.a==f.c&&f.b<0) f.b=-f.b;
    return f; } }
static int isred_ind(Q f,ll s){ ll aa=2*llabs(f.a); return f.b>0&&f.b<=s&&aa>s-f.b&&aa<=s+f.b; } // s=floor(sqrt D), D nonsquare
static Q rho(Q f,ll D,ll s){ // (a,b,c)->(c,b',a')
  ll c=f.c, ac=llabs(c); ll b;
  // b' = -b mod 2|c|, in (s-2|c|, s] if |c|<=s else in (-|c|,|c|]
  ll m=((-f.b)%(2*ac)+2*ac)%(2*ac);
  if(ac<=s){ b=m+2*ac*fdiv(s-m,2*ac); } else { b=m; if(b>ac) b-=2*ac; }
  Q g={c,b,(ll)(((LL)b*b-D)/(4*c))}; return g; }
static Q red_ind(Q f,ll D,ll s){ int it=0; while(!isred_ind(f,s)){ f=rho(f,D,s); if(++it>100000){fprintf(stderr,"red fail\n");exit(1);} } return f; }
static Q comp(Q f,Q g,ll D){
  ll s=(f.b+g.b)/2,u,v,w,t1,t2; ll g1=xg(f.a,g.a,&u,&v); ll gg=xg(g1,s,&t1,&t2); u*=t1; v*=t1; w=t2; // u f.a+v g.a+w s=gg
  LL A=(LL)(f.a/gg)*(g.a/gg);
  LL num=(LL)u*f.a*g.b+(LL)v*g.a*f.b+(LL)w*(((LL)f.b*g.b+D)/2);
  if(num%gg!=0){fprintf(stderr,"comp div\n");exit(1);}
  LL B=num/gg; LL m=2*A; B%=m; if(B<0)B+=m;
  LL C4=B*B-D; if(C4%(4*A)!=0){fprintf(stderr,"comp C\n");exit(1);}
  Q r={(ll)A,(ll)B,(ll)(C4/(4*A))}; return r; }
static ll gcd3(ll a,ll b,ll c){ll u,v; return xg(xg(a,b,&u,&v),c,&u,&v);}
// returns 3^r (number of classes with cube = identity); *h = class number (narrow for D>0)
static ll tors3(ll D,ll*h){
  ll cnt=0; *h=0;
  if(D<0){ ll n=-D; Q id={1,D&1,(ll)(((D&1)-D)/4)};
    for(ll b=n&1; 3*b*b<=n; b+=2){ ll ac=(b*b+n)/4; for(ll a=(b>1?b:1); a*a<=ac; a++){ if(ac%a) continue; ll c=ac/a; if(gcd3(a,b,c)!=1) continue;
        for(int sgn=0;sgn<2;sgn++){ if(sgn&&(b==0||a==b||a==c)) continue; Q f={a,sgn?-b:b,c}; (*h)++;
          Q f3=red_def(comp(red_def(comp(f,f,D),D),f,D),D); if(f3.a==id.a&&f3.b==id.b&&f3.c==id.c) cnt++; } } }
    return cnt; }
  ll s=isqrt(D);
  // principal cycle
  static Q pc[200000]; int np=0; Q p0={1,(D&1),0}; p0.c=(ll)(((LL)p0.b*p0.b-D)/4); p0=red_ind(p0,D,s); Q f=p0;
  do{ pc[np++]=f; f=rho(f,D,s);}while(!(f.a==p0.a&&f.b==p0.b));
  // enumerate all reduced forms, group into cycles
  static Q all[2000000]; static char used[2000000]; int na=0;
  for(ll b=(D&1)?1:2;b<=s;b+=2){ ll ac=(D-b*b)/4; // a*c=-ac
    for(ll a=1;a*a<=ac;a++){ if(ac%a) continue; ll c0=ac/a; ll cand[2]={a,c0}; int nc=(a==c0)?1:2;
      for(int i=0;i<nc;i++) for(int sg=-1;sg<=1;sg+=2){ Q q={sg*cand[i],b,-sg*(ac/cand[i])}; if(!isred_ind(q,s)) continue; if(gcd3(q.a,q.b,q.c)!=1) continue; used[na]=0; all[na++]=q; } } }
  for(int i=0;i<na;i++){ if(used[i]) continue; (*h)++; Q q=all[i]; Q g=q;
    do{ for(int j=i;j<na;j++) if(all[j].a==g.a&&all[j].b==g.b&&all[j].c==g.c){used[j]=1;break;} g=rho(g,D,s);}while(!(g.a==q.a&&g.b==q.b&&g.c==q.c));
    Q f3=red_ind(comp(red_ind(comp(q,q,D),D,s),q,D),D,s); for(int j=0;j<np;j++) if(pc[j].a==f3.a&&pc[j].b==f3.b&&pc[j].c==f3.c){cnt++;break;} }
  return cnt; }
static int fund(ll d){ ll m=d; if((d&3)==0){ m=d/4; if((m&3)!=2&&(m&3)!=3) return 0; } else if((d&3)!=1) return 0; if(m<2&&d<2) return 0; for(ll p=2;p*p<=m;p++) if(m%(p*p)==0) return 0; return 1; }
static int l3(ll t){ int r=0; while(t>1){ if(t%3){fprintf(stderr,"not 3-power %lld\n",t);exit(1);} t/=3; r++; } return r; }
int main(int argc,char**argv){
  if(argc>2){ ll D=atoll(argv[2]),h; ll t=tors3(D,&h); printf("D=%lld h=%lld tors3=%lld\n",D,h,t); return 0; }
  ll X=atoll(argv[1]);
  for(ll d=5;d<=X;d++){ if(!fund(d)) continue; ll h1,h2; int r=l3(tors3(d,&h1)); ll m=(d%3==0)?-(d/3):-3*d; int rp=l3(tors3(m,&h2)); printf("%lld %d %d\n",d,r,rp); }
  return 0; }
