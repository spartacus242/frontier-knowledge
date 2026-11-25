import subprocess,sys,os,csv
rows=list(csv.reader(open('/tmp/work/pk/table.csv')))[1:]
X=[int(r[0]) for r in rows]
maxX=int(sys.argv[1])
out='mine.csv'
done={}
if os.path.exists(out):
    for l in open(out):
        p=l.split(','); done[int(p[0])]=p
cum=[0]*8; prev=0
for i,x in enumerate(X):
    if x>maxX: break
    if x in done:
        v=list(map(int,done[x][1:])); cum=v; prev=x; continue
    # chunk interval into pieces of <=1e6 for resumability not needed here
    o=subprocess.run(['./rank3',str(prev),str(x)],capture_output=True,text=True).stdout.split('\n')
    assert 'viol 0' in o,o
    cum=list(cum)
    for l in o[:8]:
        r,a,b=map(int,l.split()); cum[2*r if False else 0]+=0
    # cum layout n00 n01 n10 n11 n20 n21 n30 n31
    cum=cum[:8]
    for l in o[:4]:
        r,a,b=map(int,l.split()); cum[2*r]+=a; cum[2*r+1]+=b
    assert all(int(l.split()[1])+int(l.split()[2])==0 for l in o[4:8])
    with open(out,'a') as f: f.write(','.join(map(str,[x]+cum))+'\n')
    ok = list(map(int,rows[i][1:]))==cum
    print(x,'MATCH' if ok else 'DIFF',cum,rows[i][1:],flush=True)
    prev=x
