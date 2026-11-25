// Second, deliberately different checker (no Russian-doll table, no precomputed pair table):
// decides whether an admissible set of size k exists in Z_n. WLOG 0 in S (translation).
// Elements added in increasing order; "forbidden" array maintained by counters; bound = remaining free count.
// usage: dfs n k   -> prints EXISTS + set, or NONE
#include <stdio.h>
#include <stdlib.h>
static int n,k,S[128],forb[128];unsigned long long nodes;
static void mark(int v,int cnt,int d){ // elements w that would form an AP with v and some S[i], or v alone
  if(n%2==0) forb[(v+n/2)%n]+=d;
  for(int i=0;i<cnt;i++){int s=S[i];
    forb[((2*v-s)%n+n)%n]+=d; forb[((2*s-v)%n+n)%n]+=d;
    for(int w=0;w<n;w++) if((2*w)%n==(s+v)%n) forb[w]+=d;
  }
}
static int rec(int cnt,int next){
  nodes++;
  if(cnt==k) return 1;
  int fr=0; for(int w=next;w<n;w++) if(!forb[w]) fr++;
  for(int v=next;v<n;v++){
    if(forb[v]) continue;
    if(cnt+fr<k) return 0;
    fr--;
    mark(v,cnt,1); S[cnt]=v;
    if(rec(cnt+1,v+1)) return 1;
    mark(v,cnt,-1);
  }
  return 0;
}
int main(int c,char**a){n=atoi(a[1]);k=atoi(a[2]);
  S[0]=0; mark(0,0,1);
  if(rec(1,1)){printf("EXISTS");for(int i=0;i<k;i++)printf(" %d",S[i]);printf("\n");}
  else printf("NONE\n");
  return 0;}
