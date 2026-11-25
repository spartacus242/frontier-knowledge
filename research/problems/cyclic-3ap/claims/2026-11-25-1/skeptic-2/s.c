#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u;
int n,T; u FULL; int S[64]; long long nodes; int found;
static inline int pc(u x){return __builtin_popcountll((unsigned long long)x)+__builtin_popcountll((unsigned long long)(x>>64));}
static inline u bit(int i){return ((u)1)<<i;}
static inline int ctz(u x){unsigned long long l=(unsigned long long)x; if(l) return __builtin_ctzll(l); return 64+__builtin_ctzll((unsigned long long)(x>>64));}
u lowmask(int m){ /* bits 0..m */ if(m<0) return 0; if(m>=n-1) return FULL; return (bit(m+1))-1;}
int inv2; 
void rec(int k,u allowed,int last,int G){
  nodes++;
  if(k==T){found=1;return;}
  int need=T-k;
  allowed&=lowmask(n-G);
  allowed&=~(bit(last+1)-1);
  if(pc(allowed)<need) return;
  u a=allowed;
  while(a){
    int e=ctz(a); a&=a-1;
    if(pc(a)+1<need) return;
    int g=G; if(e-last>g)g=e-last;
    if(e>n-g) break;
    u na=allowed&~(bit(e+1)-1);
    S[k]=e;
    if(n%2==0) na&=~bit((e+n/2)%n);
    for(int i=0;i<=k;i++){
      int s=S[i];
      int x=((2*s-e)%n+n)%n; na&=~bit(x);
      x=((2*e-s)%n+n)%n; na&=~bit(x);
      if(n%2){ x=((s+e)%n)*((n+1)/2)%n; na&=~bit(x);}
      else if(((s+e)&1)==0){ x=((s+e)/2)%n; na&=~bit(x); na&=~bit((x+n/2)%n);}
    }
    rec(k+1,na,e,g);
    if(found)return;
  }
}
int main(int c,char**v){
  n=atoi(v[1]);T=atoi(v[2]);
  FULL=(n>=128)?~(u)0:(bit(n)-1);
  S[0]=0; u al=FULL&~bit(0); if(n%2==0) al&=~bit(n/2);
  /* element 0: also 2*0-... self-pairs handled; */
  found=0;nodes=0;
  rec(1,al,0,0);
  if(found){printf("%d %d FOUND:",n,T);for(int i=0;i<T;i++)printf(" %d",S[i]);printf("\n");}
  else printf("%d %d NONE nodes=%lld\n",n,T,nodes);
}
