#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
typedef long long ll;
// count squarefree n<=N in residue classes mod 4 via segmented sieve
int main(int argc,char**argv){ ll N=atoll(argv[1]); ll SEG=1<<24; char*s=malloc(SEG); ll c[4]={0,0,0,0}; ll cq[4]={0,0,0,0}; ll N4=N/4;
  for(ll lo=1;lo<=N;lo+=SEG){ ll hi=lo+SEG-1; if(hi>N)hi=N; memset(s,1,hi-lo+1);
    for(ll p=2;p*p<=hi;p++){ ll p2=p*p; ll m=((lo+p2-1)/p2)*p2; for(;m<=hi;m+=p2) s[m-lo]=0; }
    for(ll n=lo;n<=hi;n++) if(s[n-lo]){ c[n&3]++; if(n<=N4) cq[n&3]++; } }
  printf("N=%lld fundamental discriminants in (1,N]: %lld\n",N,(c[1]-1)+cq[2]+cq[3]); return 0; }
