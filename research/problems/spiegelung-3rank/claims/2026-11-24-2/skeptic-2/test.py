import numpy as np, csv, math
rows=list(csv.DictReader(open('table.csv')))
X=[int(r['X']) for r in rows]
def g(r,k): return np.array([int(x[k]) for x in rows],dtype=float)
def sf5(t): # chi2 sf, 5 dof: Q(5/2,t/2), via erfc closed form
    x=t/2
    return math.erfc(math.sqrt(x))+2*math.sqrt(x/math.pi)*math.exp(-x)*(1+2*x/3)
series={'aggregate':(None,0.29765117),'r0':(0,1/3),'r1':(1,1/9),'r2':(2,1/27)}
def bins(sr):
    r=series[sr][0]
    if r is None:
        s=sum(g(0,f'n{q}1') for q in range(4)); n=s+sum(g(0,f'n{q}0') for q in range(4))
    else: s=g(0,f'n{r}1'); n=s+g(0,f'n{r}0')
    ds=np.diff(s); dn=np.diff(n); xm=np.sqrt(np.array(X[:-1],float)*np.array(X[1:],float))
    return ds,dn,xm
def fit(ds,dn,xm,p,idx,cols,half=1.0):
    pt=(ds+.5)/(dn+1); var=pt*(1-pt)/dn*half
    A=np.stack([xm**(-1/6),xm**(-1/3)][:cols],1)
    y=ds/dn-p
    W=1/var[idx]; N=A[idx].T@(A[idx]*W[:,None]); c=np.linalg.solve(N,A[idx].T@(W*y[idx]))
    return c,np.linalg.inv(N),A
def test(sr,delta=0,cols=2,half=1.0):
    ds,dn,xm=bins(sr); p=series[sr][1]+delta
    idx=np.where((xm>1e6)&(xm<1e10))[0]; new=np.where(xm>1e10)[0]
    c,S,A=fit(ds,dn,xm,p,idx,cols,half)
    q=p+A[new]@c; res=ds[new]/dn[new]-q; V=np.diag(q*(1-q)/dn[new]*half); J=A[new]
    T=res@np.linalg.inv(V+J@S@J.T@np.eye(5) if False else V+J@S@J.T)@res
    return c,T,sf5(T),len(idx),len(new)
for sr in series:
    c,T,p,ni,nn=test(sr); c1,T1,p1,_,_=test(sr,cols=1); ch,Th,ph,_,_=test(sr,half=0.5)
    ok=lambda d:test(sr,delta=d)[2]>0.01
    ds=np.linspace(-0.004,0.004,8001); good=[d for d in ds if ok(d)]
    print(sr,ni,nn,'c',c.round(5),'T %.2f p %.3f'%(T,p),'half T %.2f p %.4f'%(Th,ph),'M1 T %.2f p %.4f'%(T1,p1),'shift',(round(min(good),5),round(max(good),5)) if good else None)
