/* cyc n K : decide whether some subset of Z_n of size K has no nontrivial 3AP
   (x+z=2y mod n, x,y,z in S not all equal). Exhaustive DFS.
   Normalisation (translation): 0 in S, elements s0=0<s1<..<s_{K-1}, and the wrap gap n-s_{K-1}
   is >= every other gap (rotate so that the largest gap ends at 0).
   Pruning: forbidden bitmask; popcount of allowed slots; arc bound |S cap arc of length L| <= r3(L)
   (an integer 3AP inside an arc is a 3AP mod n). r3 table read from r3_mine.txt (own computation).
   Output: FOUND <set>  or  NONE, plus node count. */
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
static int n,K,half,r3[200]; static long long nodes;
static int el[64];
static inline int pc(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
static inline u128 bit(int i){return (u128)1<<i;}
static u128 rangemask(int lo,int hi){ /* bits lo..hi inclusive */
  if(hi<lo) return 0; u128 m = (hi>=127)? ~(u128)0 : ((bit(hi+1))-1); return m & ~((bit(lo))-1); }
static int dfs(int d,int p,int G,u128 forb){
  if(d==K) return 1;
  int r=K-d; int E=n-G;
  /* arc bounds */
  if(r > r3[E-p]) return 0;
  for(int j=0;j<d;j++) if((d-j)+r > r3[E-el[j]+1]) return 0;
  u128 avail = ~forb & rangemask(p+1,E);
  if(pc(avail) < r) return 0;
  int qmax = (n+p)/2; if(qmax>E) qmax=E;
  for(int q=p+1;q<=qmax;q++){
    if(!((avail>>q)&1)) continue;
    int G2 = q-p>G? q-p:G;
    if(q > n-G2) continue;
    nodes++;
    u128 f=forb;
    for(int i=0;i<d;i++){ int x=el[i];
      f|=bit((2*q-x)%n); f|=bit(((2*x-q)%n+n)%n);
      int s=x+q;
      if(n&1){ f|=bit((s&1)? (s+n)/2 : s/2); }
      else if(!(s&1)){ f|=bit(s/2); f|=bit((s/2+half)%n); }
    }
    if(!(n&1)) f|=bit((q+half)%n);
    el[d]=q;
    if(dfs(d+1,q,G2,f)) return 1;
  }
  return 0;
}
int main(int argc,char**argv){
  n=atoi(argv[1]); K=atoi(argv[2]); half=n/2;
  FILE*fp=fopen("/tmp/work/sr3/r3_mine.txt","r"); int a,b; for(int i=0;i<200;i++) r3[i]=1000;
  r3[0]=0;r3[1]=1;r3[2]=2; int last=2; while(fscanf(fp,"%d %d",&a,&b)==2){ r3[a]=b; last=a;} fclose(fp);
  for(int i=last+1;i<200;i++) r3[i]=r3[i-1]+1; /* safe: r3(L)<=r3(L-1)+1 */
  if(n>127){fprintf(stderr,"n too big\n");return 1;}
  el[0]=0; u128 f0 = (n&1)?0:bit(half);
  int res = (K<=1)? 1 : dfs(1,0,0,f0);
  if(res){ printf("FOUND n=%d K=%d :",n,K); for(int i=0;i<K;i++) printf(" %d",el[i]); }
  else printf("NONE n=%d K=%d",n,K);
  printf(" nodes=%lld\n",nodes); return 0;
}
