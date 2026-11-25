import csv,collections
rows=list(csv.DictReader(open('table.csv')))
data=sorted(tuple(map(int,l.split())) for l in open('all.txt'))
import bisect
ds=[d[0] for d in data]
ok=bad=0
for r in rows:
    X=int(r['X'])
    if X>10**6: break
    n=collections.Counter()
    for d,a,b in data[:bisect.bisect_right(ds,X)]: n[(a,b-a)]+=1
    exp={k:int(v) for k,v in r.items() if k!='X'}
    got={f'n{a}{e}':v for (a,e),v in n.items()}
    if all(exp[k]==got.get(k,0) for k in exp): ok+=1
    else: bad+=1; print('DIFF',X)
print(ok,bad)
