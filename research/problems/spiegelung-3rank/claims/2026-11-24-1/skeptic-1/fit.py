import csv, math, sys
from fractions import Fraction
rows=[{k:int(v) for k,v in r.items()} for r in csv.DictReader(open('/tmp/work/pk/table.csv'))]
# sanity: monotone, checkpoints
for i,r in enumerate(rows):
    assert r['X']==round(10**((30+i)/10)), r['X']
    if i: assert all(r[k]>=rows[i-1][k] for k in r)
# conjectured constant
def eta(k): 
    p=1.0
    for i in range(1,k+1): p*=1-3.0**-i
    return p
einf=eta(200)
PR=[3.0**(-r*(r+1))*einf/(eta(r)*eta(r+1)) for r in range(40)]   # Cohen-Lenstra real quadratic, P(3-rank=r)
print("sum P_real(r) =",sum(PR), "P(r=0..3)=",PR[:4])
conj=sum(PR[r]*3.0**-(r+1) for r in range(40))
print("aggregate conjectured constant = %.12f"%conj)
def wls(xs,ys,ws):
    S=sum(ws);Sx=sum(w*x for w,x in zip(ws,xs));Sy=sum(w*y for w,y in zip(ws,ys))
    Sxx=sum(w*x*x for w,x in zip(ws,xs));Sxy=sum(w*x*y for w,x,y in zip(ws,xs,ys))
    det=S*Sxx-Sx*Sx; c=(S*Sxy-Sx*Sy)/det; p=(Sxx*Sy-Sx*Sxy)/det
    chi=sum(w*(y-p-c*x)**2 for w,x,y in zip(ws,xs,ys))
    return p,math.sqrt(Sxx/det),c,math.sqrt(S/det),chi
def test(kmin=60,kmax=90,expo=-1/6,quiet=False,label=""):
    out=[]
    for name,cols,target in [("agg",[0,1,2,3],conj),("r=0",[0],1/3),("r=1",[1],1/9),("r=2",[2],1/27)]:
        xs=[];ys=[];ws=[]
        for k in range(kmin,kmax):
            lo=rows[k-30];hi=rows[k-29]
            s=sum(hi['n%d1'%r]-lo['n%d1'%r] for r in cols); n=s+sum(hi['n%d0'%r]-lo['n%d0'%r] for r in cols)
            if n==0: continue
            pt=(s+0.5)/(n+1); var=pt*(1-pt)/n
            xs.append(math.sqrt(lo['X']*hi['X'])**expo); ys.append(s/n); ws.append(1/var)
        p,se,c,sc,chi=wls(xs,ys,ws); dof=len(xs)-2
        z=(p-target)/se
        verdict="VOID" if chi>2*dof else ("CONSISTENT" if abs(z)<=3 else "INCONSISTENT")
        out.append((name,p,se,z,chi,dof,verdict))
        if not quiet: print("%s %-4s p_inf=%.6f +- %.6f  c=%.4f+-%.4f target=%.8f z=%+.2f chi2=%.1f/%d %s"%(label,name,p,se,c,sc,target,z,chi,dof,verdict))
    return out
print("== pre-set test, bins (1e6,1e9], exponent -1/6 ==")
test()
r=rows[-1]
tot=sum(v for k,v in r.items() if k!='X'); e1=sum(r['n%d1'%i] for i in range(4))
print("at 1e9: total",tot,"e=1",e1,"raw agg %.6f"%(e1/tot),[ "%.6f"%(r['n%d1'%i]/(r['n%d0'%i]+r['n%d1'%i])) for i in range(3)], [r['n%d0'%i]+r['n%d1'%i] for i in range(4)])
print("== sensitivity: exponent ==")
for e in (-1/12,-1/8,-1/6,-1/5,-1/4,-1/3,-1/2): test(expo=e,label="expo=%.3f"%e)
print("== sensitivity: start of fit range ==")
for k0 in (40,50,60,65,70,75,80): test(kmin=k0,label="kmin=%d"%k0)
print("== sensitivity: end of fit range (X_max) ==")
for k1 in (70,75,80,85,90): test(kmax=k1,label="kmax=%d"%k1)
print("== free exponent scan: chi2 and p_inf vs exponent (r=1, agg) ==")
for e100 in range(8,31,2):
    o=test(expo=-e100/100,quiet=True)
    print("expo=-%.2f"%(e100/100)," ".join("%s:p=%.5f z=%+.1f chi=%.1f"%(a,p,z,chi) for a,p,se,z,chi,dof,v in o))
