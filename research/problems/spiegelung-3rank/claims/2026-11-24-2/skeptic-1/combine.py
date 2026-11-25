import csv,glob,re,sys
rows=[list(map(int,r)) for r in list(csv.reader(open('/tmp/work/pk2/table.csv')))[1:]]
W=1600000000
segs={}
for i in range(20):
    try: t=open('seg_%d.out'%i).read()
    except FileNotFoundError: break
    if 'DONE' not in t: break
    segs[i]=t
n=len(segs); cover=min(n*W-1, 31622776602)
acc=[0]*10; bins=[[0]*10 for _ in rows]; bad=viol=nf=0; big=[]
for i in range(n):
    for l in segs[i].splitlines():
        p=l.split()
        if p[0]=='BIN':
            k=int(p[1]); assert int(p[2])==rows[k][0]
            bins[k]=[a+b for a,b in zip(bins[k],map(int,p[3:]))]
        elif p[0]=='STAT': nf+=int(p[6]); bad+=int(p[8]); viol+=int(p[10])
        elif p[0]=='BIG': big.append(tuple(map(int,p[1:])))
        elif p[0] in('BAD','VIOL','BADN'): print(l)
ok=0; diff=0; out=[]
for k,row in enumerate(rows):
    acc=[a+b for a,b in zip(acc,bins[k])]
    if row[0]>cover: break
    out.append([row[0]]+acc[:8])
    if acc[:8]==row[1:] and acc[8]==0 and acc[9]==0: ok+=1
    else: diff+=1; print('DIFF',row,acc)
print('segments',n,'covered d <=',cover,'rows matched',ok,'rows differing',diff,'last matched X',out[-1][0] if out else None)
print('fundamental discriminants seen',nf,'bad',bad,'Scholz violations',viol,'r>=3 or rprime>=4 entries',len(big))
print('first BIG',sorted(big)[:5]); print('r=3,e=1:',len([b for b in big if b[1]==3 and b[2]==4]),'rprime=4 total',len([b for b in big if b[2]==4]))
with open('mytable.csv','w') as f:
    f.write('X,n00,n01,n10,n11,n20,n21,n30,n31\n')
    for r in out: f.write(','.join(map(str,r))+'\n')
if out: print('last row',out[-1], 'total',sum(out[-1][1:]),'e=1',out[-1][2]+out[-1][4]+out[-1][6]+out[-1][8])
