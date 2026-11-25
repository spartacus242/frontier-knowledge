import csv
a=[int(x) for x in open('oeis.txt').read().split(',')]
exp=[15,16,16,16,16,17,16,16,16,16,16,17,16,17,16,17,17,17,16,17,17]
rows=list(csv.reader(open('/tmp/work/pk3/terms.csv')))[1:]
for r in rows:
    n=int(r[0]);k=int(r[1]);S=list(map(int,r[2].split()))
    ok=len(S)==k==exp[n-80] and len(set(S))==k and all(0<=x<n for x in S)
    Ss=set(S)
    for x in S:
        for z in S:
            if (x+z)%n==0 or True:
                for y in S:
                    if (x+z-2*y)%n==0 and not(x==y==z): ok=False
    print(n,k,ok)
