import subprocess,sys
sys.path.insert(0,'/tmp/work/sr1')
from check import admissible
o=[int(l.split()[1]) for l in open('oeis/b304884_as_fetched.txt')]
claim={}
for line in open('/tmp/work/pk3/terms.csv').read().strip().split('\n')[1:]:
    n,a,w=line.split(','); claim[int(n)]=int(a)
bad=0; tot=0; mono=0
for n in range(3,101):
    L=open(f'res/{n}.txt').read().split('\n')
    h=L[0].split(); a=int(h[1][2:]); tot+=float(h[3][4:])
    w=list(map(int,L[0].split('witness:')[1].split()))
    assert len(w)==a and admissible(w,n),n
    f=list(map(int,L[1].split()[1:])); assert f[-1]==a and len(f)==n
    ref=o[n-1] if n<=79 else claim[n]
    if a!=ref: bad+=1; print('MISMATCH',n,a,ref)
print('n=3..79 vs OEIS and 80..100 vs claim: mismatches =',bad,' total rd CPU sec = %.0f'%tot)
print('mine 80..100:',[int(open(f'res/{n}.txt').read().split()[1][2:]) for n in range(80,101)])
# second checker dfs.c on n=3..58: exists(a) and not exists(a+1)
b2=0
for n in range(3,59):
    a=o[n-1]
    r1=subprocess.run(['./dfs',str(n),str(a)],capture_output=True,text=True).stdout
    r2=subprocess.run(['./dfs',str(n),str(a+1)],capture_output=True,text=True).stdout
    if not r1.startswith('EXISTS') or not r2.startswith('NONE'): b2+=1; print('dfs mismatch',n)
    else: assert admissible(list(map(int,r1.split()[1:])),n)
print('dfs.c cross-check n=3..58 mismatches =',b2)
