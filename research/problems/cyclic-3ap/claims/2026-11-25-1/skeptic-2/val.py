import subprocess
a=[int(x) for x in open('oeis.txt').read().split(',')]
bad=0
for n in range(3,80):
    k=a[n-1]
    r1=subprocess.run(['./s',str(n),str(k)],capture_output=True,text=True).stdout
    r2=subprocess.run(['./s',str(n),str(k+1)],capture_output=True,text=True).stdout
    ok=('FOUND' in r1) and ('NONE' in r2)
    if not ok: bad+=1; print("MISMATCH",n,r1,r2)
print("bad",bad)
