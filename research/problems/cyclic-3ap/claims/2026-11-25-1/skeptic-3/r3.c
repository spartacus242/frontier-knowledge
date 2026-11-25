/* r3(L): largest 3AP-free subset of {0..L-1} (integers). Own computation, incremental:
   r3(L) in {r3(L-1), r3(L-1)+1}; test existence of size r3(L-1)+1 containing 0 and L-1,
   choosing elements in decreasing order from L-1 with bound cnt + r3(p+1). */
#include <stdio.h>
#include <string.h>
typedef unsigned __int128 u128;
static int r3[128]; static int L, K; static long long nodes;
static int el[64];
static int dfs(int d, int p, u128 forb){ /* elements chosen: el[0..d-1], last p; next must be <p */
  if(d==K) return 1;
  for(int q=p-1;q>=0;q--){
    if(d + r3[q+1] < K) return 0;           /* remaining in [0,q] */
    if((forb>>q)&1) continue;
    if(d==K-1 && q!=0) { /* last must be 0 */ continue; }
    nodes++;
    u128 f=forb;
    for(int i=0;i<d;i++){ int x=el[i]; int z=2*q-x; if(z>=0) f|=(u128)1<<z; /* x>q, z<q */
      if(((x+q)&1)==0) f|=(u128)1<<((x+q)/2); }
    el[d]=q; if(dfs(d+1,q,f)) return 1;
  }
  return 0;
}
int main(){ r3[0]=0; r3[1]=1; r3[2]=2;
  for(L=3;L<=101;L++){ K=r3[L-1]+1; el[0]=L-1; nodes=0;
    r3[L]= dfs(1,L-1,0)? K : K-1; printf("%d %d\n",L,r3[L]); fflush(stdout);}
}
