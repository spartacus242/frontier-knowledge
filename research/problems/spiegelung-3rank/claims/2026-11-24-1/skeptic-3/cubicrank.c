/*
 * Independent computation of n(r,e;X) for positive fundamental discriminants d
 * via GL2(Z)-classes of binary cubic forms (Delone-Faddeev / Davenport-Heilbronn):
 * for a fundamental discriminant D, the number of cubic fields of discriminant D
 * is (3^rk3(Cl(Q(sqrt D))) - 1)/2.
 *
 * D>0: reduction by the Hessian H=(P,Q,R) = (b^2-3ac, bc-9ad, c^2-3bd), domain
 *      0<=Q<=P<=R, a>=1, ties on the boundary broken by taking the lexicographically
 *      largest image under Stab_GL2(H).
 * D<0: reduction by the complex root tau: 0<=Re tau<=1/2, |tau|>=1, a>=1, i.e.
 *      0 <= ad-bc <= (a+b)^2+ac  and  d^2-a^2+ac-bd >= 0.
 *
 * usage: cubicrank MODE ...
 *   cubicrank table Xmax segL outdir      -> segment files outdir/seg_<lo>.txt (resumable)
 *   cubicrank ranks lo hi                  -> prints "d r r'" for fundamental d in [lo,hi)
 *   cubicrank brute Y B                    -> compare loop enumeration vs box brute force
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include <time.h>

typedef long long ll;
typedef __int128 i128;

static ll isqrt_ll(ll n){ if(n<0) return -1; ll r=(ll)sqrtl((long double)n); while(r*r>n) r--; while((r+1)*(r+1)<=n) r++; return r; }
static ll fdiv(ll a, ll b){ ll q=a/b; if((a%b!=0)&&((a<0)!=(b<0))) q--; return q; }
static ll cdiv(ll a, ll b){ return -fdiv(-a,b); }

/* integer d with q(d)=A d^2 + B d + C <= 0, A>0. returns 0 if empty, else [*lo,*hi] */
static int qint(ll A, ll B, ll C, ll *lo, ll *hi){
    i128 disc=(i128)B*B-(i128)4*A*C;
    if(disc<0) return 0;
    long double s=sqrtl((long double)disc);
    long double r1=(-(long double)B - s)/(2.0L*A), r2=(-(long double)B + s)/(2.0L*A);
    ll l=(ll)floorl(r1), h=(ll)ceill(r2);
    #define QV(x) ((i128)A*(x)*(x)+(i128)B*(x)+(i128)C)
    /* adjust exactly: l = smallest with q<=0, h = largest */
    while(QV(l)<=0) l--; l++;
    while(l<=h && QV(l)>0) l++;
    while(QV(h)<=0) h++; h--;
    while(h>=l && QV(h)>0) h--;
    #undef QV
    if(l>h) return 0;
    *lo=l; *hi=h; return 1;
}

static int stabmats[100][4]; static int nstab=0;
static void init_mats(void){
    for(int p=-1;p<=1;p++)for(int q=-1;q<=1;q++)for(int r=-1;r<=1;r++)for(int s=-1;s<=1;s++){
        int det=p*s-q*r; if(det==1||det==-1){ stabmats[nstab][0]=p;stabmats[nstab][1]=q;stabmats[nstab][2]=r;stabmats[nstab][3]=s;nstab++; }
    }
}
/* is f lexicographically maximal among its images under Stab_GL2(H)? */
static int canonical_pos(ll a, ll b, ll c, ll d, ll P, ll Q, ll R){
    for(int i=0;i<nstab;i++){
        ll al=stabmats[i][0], be=stabmats[i][1], ga=stabmats[i][2], de=stabmats[i][3];
        ll det=al*de-be*ga;
        ll P2=P*al*al+Q*al*be+R*be*be, Q2=2*P*al*ga+Q*(al*de+be*ga)+2*R*be*de, R2=P*ga*ga+Q*ga*de+R*de*de;
        if(P2!=P||Q2!=Q||R2!=R) continue;
        /* f(al x+ga y, be x+de y) */
        ll X[2]={al,ga}, Y[2]={be,de};
        ll out[4]={0,0,0,0};
        ll co[4]={a,b,c,d};
        for(int t=0;t<4;t++){
            /* term X^(3-t) Y^t */
            ll poly[4]={1,0,0,0}; int deg=0;
            for(int k=0;k<3;k++){
                ll *L = (k<3-t)?X:Y; ll np[4]={0,0,0,0};
                for(int u=0;u<=deg;u++){ np[u]+=poly[u]*L[0]; np[u+1]+=poly[u]*L[1]; }
                deg++; memcpy(poly,np,sizeof np);
            }
            for(int u=0;u<4;u++) out[u]+=co[t]*poly[u];
        }
        for(int u=0;u<4;u++) out[u]*=det;
        ll f0[4]={a,b,c,d};
        for(int u=0;u<4;u++){ if(out[u]>f0[u]) return 0; if(out[u]<f0[u]) break; }
    }
    return 1;
}

static inline ll discf(ll a, ll b, ll c, ll d){ return b*b*c*c-4*a*c*c*c-4*b*b*b*d-27*a*a*d*d+18*a*b*c*d; }

/* count D>0 forms with Xlo<=D<Xhi into cnt[D-Xlo] */
static ll enum_pos(ll Xlo, ll Xhi, unsigned char *cnt){
    ll nforms=0; ll Xm=Xhi-1;
    ll Pmax=isqrt_ll(Xm);
    ll Amax=(ll)floor(sqrt(sqrt(16.0*(double)Xm/729.0)))+1;
    ll sP=(ll)ceil(sqrt((double)Pmax))+1;
    for(ll a=1;a<=Amax;a++){
        /* 4P^3 >= 27 D a^2 >= 27 Xlo a^2 */
        ll Pmin=(ll)floor(cbrt(27.0*(double)Xlo*a*a/4.0))-2; if(Pmin<1) Pmin=1;
        while(Pmin>1 && 4*(i128)(Pmin-1)*(Pmin-1)*(Pmin-1) >= (i128)27*Xlo*a*a) Pmin--;
        while(4*(i128)Pmin*Pmin*Pmin < (i128)27*Xlo*a*a) Pmin++;
        if(Pmin>Pmax) continue;
        if(27*(i128)a*a > 4*(i128)Pmax*Pmax*Pmax) continue; /* need 27 a^2 D <= 4P^3, D>=1 */
        ll bmin=-sP, bmax=(3*a)/2+sP+1;
        for(ll b=bmin;b<=bmax;b++){
            ll clo=cdiv(b*b-Pmax,3*a), chi=fdiv(b*b-Pmin,3*a);
            for(ll c=clo;c<=chi;c++){
                ll P=b*b-3*a*c; if(P<Pmin||P>Pmax) continue;
                /* 0<=Q<=P: bc-P <= 9ad <= bc */
                ll dlo=cdiv(b*c-P,9*a), dhi=fdiv(b*c,9*a);
                /* R>=P: c^2-3bd>=P */
                if(b>0){ ll t=fdiv(c*c-P,3*b); if(t<dhi) dhi=t; }
                else if(b<0){ ll t=cdiv(c*c-P,3*b); if(t>dlo) dlo=t; }
                else { if(c*c<P) continue; }
                if(dlo>dhi) continue;
                /* D(d) = -27a^2 d^2 + (18abc-4b^3) d + (b^2c^2-4ac^3) >= Xlo */
                ll A=27*a*a, B=-(18*a*b*c-4*b*b*b), C0=-(b*b*c*c-4*a*c*c*c);
                ll l1,h1,l2,h2;
                if(!qint(A,B,C0+Xlo,&l1,&h1)) continue;
                int has2=qint(A,B,C0+Xhi,&l2,&h2); /* D>=Xhi : exclude */
                if(l1<dlo) l1=dlo; if(h1>dhi) h1=dhi;
                for(ll d=l1; d<=h1; d++){
                    if(has2 && d>=l2 && d<=h2){ d=h2; continue; }
                    ll Q=b*c-9*a*d, R=c*c-3*b*d;
                    ll D=(4*P*R-Q*Q)/3;
                    if(D<Xlo||D>=Xhi) { fprintf(stderr,"pos range bug\n"); exit(2); }
                    if(Q==0||Q==P||P==R){ if(!canonical_pos(a,b,c,d,P,Q,R)) continue; }
                    cnt[D-Xlo]++; nforms++;
                }
            }
        }
    }
    return nforms;
}

/* count D<0 forms with Ylo<=|D|<Yhi into cnt[|D|-Ylo] */
static ll enum_neg(ll Ylo, ll Yhi, unsigned char *cnt){
    ll nforms=0; ll Ym=Yhi-1;
    ll Amax=(ll)floor(sqrt(sqrt(16.0*(double)Ym/27.0)))+1;
    for(ll a=1;a<=Amax;a++){
        double aT=sqrt(sqrt((double)Ym/3.0));            /* a*T */
        double pmax=0.25+cbrt((double)Ym/(4.0*a*a*a*a));
        ll bmin=(ll)floor(-aT-1.5*a)-1, bmax=(ll)ceil(aT)+1;
        for(ll b=bmin;b<=bmax;b++){
            ll clo=(-b<0?-b:0)-1;
            ll chi=(ll)ceil(a*pmax)+(-b>0?-b:0)+1;
            for(ll c=clo;c<=chi;c++){
                ll w=(a+b)*(a+b)+a*c; if(w<0) continue;
                ll dlo=cdiv(b*c,a), dhi=fdiv(b*c+w,a);
                if(dlo>dhi) continue;
                ll A=27*a*a, B=-(18*a*b*c-4*b*b*b), C0=-(b*b*c*c-4*a*c*c*c);
                ll l1,h1,l2,h2;
                /* D >= -Ym  <=> -D - Ym <= 0 : A d^2 + B d + C0 - Ym <= 0 */
                if(!qint(A,B,C0-Ym,&l1,&h1)) continue;
                /* exclude |D| < Ylo i.e. D >= -(Ylo-1) */
                int has2 = (Ylo>=1) ? qint(A,B,C0-(Ylo-1),&l2,&h2) : 0;
                if(l1<dlo) l1=dlo; if(h1>dhi) h1=dhi;
                for(ll d=l1; d<=h1; d++){
                    if(has2 && d>=l2 && d<=h2){ d=h2; continue; }
                    if(d*d-a*a+a*c-b*d<0) continue;
                    ll D=discf(a,b,c,d);
                    if(D>=0){ continue; }
                    ll aD=-D;
                    if(aD<Ylo||aD>=Yhi){ fprintf(stderr,"neg range bug %lld\n",D); exit(2); }
                    cnt[aD-Ylo]++; nforms++;
                }
            }
        }
    }
    return nforms;
}

static int rank_of(int n){
    switch(n){case 0:return 0;case 1:return 1;case 4:return 2;case 13:return 3;case 40:return 4;case 121:return 5;}
    return -1;
}

/* odd-squarefree sieve on [lo,hi): sf[i]=1 if no odd p^2 divides lo+i */
static unsigned char *small_primes_sieve(ll lim, ll **pr, ll *np){
    unsigned char *s=calloc(lim+1,1); ll *p=malloc(sizeof(ll)*(lim+1)); ll n=0;
    for(ll i=2;i<=lim;i++){ if(!s[i]){ p[n++]=i; for(ll j=i*i;j<=lim;j+=i) s[j]=1; } }
    free(s); *pr=p; *np=n; return NULL;
}
static void sieve_oddsf(ll lo, ll hi, unsigned char *sf){
    memset(sf,1,hi-lo);
    ll lim=isqrt_ll(hi)+1; ll *pr; ll np; small_primes_sieve(lim,&pr,&np);
    for(ll i=1;i<np;i++){ ll p=pr[i], q=p*p; if(q>=hi) break; ll s=((lo+q-1)/q)*q; for(ll x=s;x<hi;x+=q) sf[x-lo]=0; }
    free(pr);
}
static inline int is_fund_pos(ll d, unsigned char sfo){
    if(d<=1) return 0; if(!sfo) return 0;
    ll m16=d%16; if(d%4==1) return 1; if(m16==8||m16==12) return 1; return 0;
}

/* compute r(d), r'(d) for fundamental d in [lo,hi). callback via arrays */
typedef struct { ll lo,hi; unsigned char *pos,*neg1,*neg2,*sf; ll l3; } Seg;
static void compute_seg(Seg *S){
    ll lo=S->lo, hi=S->hi, L=hi-lo;
    S->pos=calloc(L,1); S->neg1=calloc(3*L,1);
    S->l3=lo/3; ll h3=(hi-1)/3+1; S->neg2=calloc(h3-S->l3+1,1);
    S->sf=malloc(L);
    enum_pos(lo,hi,S->pos);
    enum_neg(3*lo,3*hi,S->neg1);
    enum_neg(S->l3,h3,S->neg2);
    sieve_oddsf(lo,hi,S->sf);
}
static int get_ranks(Seg *S, ll d, int *r, int *rp){
    if(!is_fund_pos(d,S->sf[d-S->lo])) return 0;
    int n=S->pos[d-S->lo];
    int np = (d%3) ? S->neg1[3*d-3*S->lo] : S->neg2[d/3-S->l3];
    *r=rank_of(n); *rp=rank_of(np);
    if(d==12){ *rp=0; }  /* mirror Q(i): disc -4, h=1 (special point tau=i) */
    if(*r<0||*rp<0){ fprintf(stderr,"BAD count d=%lld n=%d n'=%d\n",d,n,np); exit(3); }
    if(!(*rp==*r || *rp==*r+1)){ fprintf(stderr,"SCHOLZ VIOLATION d=%lld r=%d r'=%d\n",d,*r,*rp); exit(4); }
    return 1;
}
static void free_seg(Seg *S){ free(S->pos);free(S->neg1);free(S->neg2);free(S->sf); }

int main(int argc, char **argv){
    init_mats();
    if(argc<2){ fprintf(stderr,"usage\n"); return 1; }
    if(!strcmp(argv[1],"ranks")){
        Seg S; S.lo=atoll(argv[2]); S.hi=atoll(argv[3]); if(S.lo<2) S.lo=2;
        compute_seg(&S);
        for(ll d=S.lo; d<S.hi; d++){ int r,rp; if(get_ranks(&S,d,&r,&rp)) printf("%lld %d %d\n",d,r,rp); }
        free_seg(&S); return 0;
    }
    if(!strcmp(argv[1],"brute")){
        /* compare enum_pos/enum_neg on [1,Y) with brute force over box |coef|<=B */
        ll Y=atoll(argv[2]); ll B=atoll(argv[3]);
        unsigned char *p1=calloc(Y,1),*p2=calloc(Y,1),*n1=calloc(Y,1),*n2=calloc(Y,1);
        ll fp=enum_pos(1,Y,p1), fn=enum_neg(1,Y,n1);
        ll bp=0,bn=0, maxa=0;
        for(ll a=1;a<=B;a++)for(ll b=-B;b<=B;b++)for(ll c=-B;c<=B;c++)for(ll d=-B;d<=B;d++){
            ll D=discf(a,b,c,d);
            if(D>0 && D<Y){
                ll P=b*b-3*a*c,Q=b*c-9*a*d,R=c*c-3*b*d;
                if(0<=Q&&Q<=P&&P<=R){ if(Q==0||Q==P||P==R){ if(!canonical_pos(a,b,c,d,P,Q,R)) continue; } p2[D-1]++; bp++; if(llabs(b)>maxa)maxa=llabs(b); if(llabs(c)>maxa)maxa=llabs(c); if(llabs(d)>maxa)maxa=llabs(d);}
            } else if(D<0 && -D<Y){
                ll t=a*d-b*c;
                if(t>=0 && t<=(a+b)*(a+b)+a*c && d*d-a*a+a*c-b*d>=0){ n2[-D-1]++; bn++; if(llabs(b)>maxa)maxa=llabs(b); if(llabs(c)>maxa)maxa=llabs(c); if(llabs(d)>maxa)maxa=llabs(d);}
            }
        }
        ll diff=0; for(ll i=0;i<Y;i++){ if(p1[i]!=p2[i]) diff++; if(n1[i]!=n2[i]) diff++; }
        printf("loops: pos %lld neg %lld | brute: pos %lld neg %lld | maxcoef seen %lld | differing D: %lld\n",fp,fn,bp,bn,maxa,diff);
        return 0;
    }
    if(!strcmp(argv[1],"table")){
        ll Xmax=atoll(argv[2]); ll segL=atoll(argv[3]); const char *od=argv[4];
        ll X[61]; for(int k=30;k<=90;k++) X[k-30]=llround(pow(10.0,k/10.0));
        for(ll lo=0; lo<=Xmax; lo+=segL){
            ll hi=lo+segL; if(hi>Xmax+1) hi=Xmax+1;
            char fn[512]; snprintf(fn,sizeof fn,"%s/seg_%012lld.txt",od,lo);
            FILE *t=fopen(fn,"r"); if(t){ fclose(t); continue; }
            clock_t t0=clock();
            Seg S; S.lo=(lo<2?2:lo); S.hi=hi;
            compute_seg(&S);
            /* cumulative counts within segment for each checkpoint */
            ll cnt[61][5][2]; memset(cnt,0,sizeof cnt);
            ll cur[5][2]; memset(cur,0,sizeof cur);
            int k=0; while(k<61 && X[k]<S.lo) k++;
            ll curk_start=k;
            for(ll d=S.lo; d<S.hi; d++){
                int r,rp; if(get_ranks(&S,d,&r,&rp)) cur[r][rp-r]++;
                while(k<61 && X[k]==d){ memcpy(cnt[k],cur,sizeof cur); k++; }
            }
            for(;k<61;k++) memcpy(cnt[k],cur,sizeof cur);
            free_seg(&S);
            char tmp[520]; snprintf(tmp,sizeof tmp,"%s.tmp",fn);
            FILE *o=fopen(tmp,"w");
            fprintf(o,"# segment [%lld,%lld) cpu %.1f s\n",S.lo,S.hi,(double)(clock()-t0)/CLOCKS_PER_SEC);
            for(int j=0;j<61;j++){ fprintf(o,"%lld",X[j]); for(int r=0;r<5;r++)for(int e=0;e<2;e++) fprintf(o," %lld",cnt[j][r][e]); fprintf(o,"\n"); }
            fclose(o); rename(tmp,fn);
            fprintf(stderr,"done segment %lld-%lld in %.1f s\n",S.lo,S.hi,(double)(clock()-t0)/CLOCKS_PER_SEC);
            (void)curk_start;
        }
        return 0;
    }
    return 1;
}
