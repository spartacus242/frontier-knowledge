// Russian-doll exhaustive search for largest 3AP-free subset of Z_n (strict definition:
// no x,y,z in S, not all equal, with x+z = 2y mod n).  Written from scratch by reviewer.
// f[m] = max size of admissible subset of window {0..m-1}.  f[n] = a(n).
// usage: rd n [outfile]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
typedef unsigned __int128 u128;
static int n;
static u128 T[128][128];   // T[s][v]: elements forbidden once both s and v are in S
static u128 SELF[128];     // elements forbidden once v in S (v+n/2 for even n)
static int f[130];
static int target;
static unsigned long long nodes;
static int best[130], cur[130];
static inline int pc(u128 x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
static inline int hi(u128 x){unsigned long long h=(unsigned long long)(x>>64); if(h) return 127-__builtin_clzll(h); return 63-__builtin_clzll((unsigned long long)x);}
// cand: allowed elements, all below every chosen element. cnt chosen so far.
static int rec(u128 cand,int cnt){
  nodes++;
  if(cnt>=target){memcpy(best,cur,sizeof(int)*cnt);return 1;}
  while(cand){
    int j=hi(cand);
    if(cnt+f[j+1]<target) return 0;
    if(cnt+pc(cand)<target) return 0;
    cand&=~((u128)1<<j);
    u128 c=cand&~SELF[j];
    for(int i=0;i<cnt;i++) c&=~T[cur[i]][j];
    cur[cnt]=j;
    if(rec(c,cnt+1)) return 1;
  }
  return 0;
}
int main(int argc,char**argv){
  n=atoi(argv[1]);
  for(int s=0;s<n;s++){
    SELF[s]=0;
    for(int y=0;y<n;y++) if(y!=s && (2*y)%n==(2*s)%n) SELF[s]|=(u128)1<<y;   // s + s = 2y
    for(int v=0;v<n;v++){ if(v==s) continue;
      u128 m=0;
      for(int w=0;w<n;w++){
        // is {s,v,w} (w possibly equal to s or v excluded) containing a nontrivial AP using s,v,w ?
        if(w==s||w==v) continue;
        if((s+v)%n==(2*w)%n || (s+w)%n==(2*v)%n || (v+w)%n==(2*s)%n) m|=(u128)1<<w;
      }
      T[s][v]=m;
    }
  }
  // pairs s,v that directly conflict (2s=2v, or s+s=2v etc.) are handled by SELF.
  clock_t t0=clock();
  f[0]=0;
  int w[130],wn=0;
  for(int m=1;m<=n;m++){
    target=f[m-1]+1;
    // must contain m-1
    u128 cand=(((u128)1<<(m-1))-1)&~SELF[m-1];
    cur[0]=m-1;
    if(rec(cand,1)){f[m]=target; wn=target; memcpy(w,best,sizeof(int)*wn);} else f[m]=f[m-1];
    fprintf(stderr,"n=%d m=%d f=%d nodes=%llu t=%.1f\n",n,m,f[m],nodes,(double)(clock()-t0)/CLOCKS_PER_SEC);
  }
  FILE*o=argc>2?fopen(argv[2],"w"):stdout;
  fprintf(o,"n=%d a=%d nodes=%llu sec=%.2f witness:",n,f[n],nodes,(double)(clock()-t0)/CLOCKS_PER_SEC);
  for(int i=wn-1;i>=0;i--) fprintf(o," %d",w[i]);
  fprintf(o,"\nf:");for(int m=1;m<=n;m++)fprintf(o," %d",f[m]);fprintf(o,"\n");
  if(o!=stdout)fclose(o);
  return 0;
}
