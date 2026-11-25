# Re-implementation of the prediction test (b) from its description only.
import csv, math, sys
def pconj_total(N=60):
    eta_inf=1.0
    for j in range(1,200): eta_inf*=1-3.0**-j
    tot=0; s=0; eta=[1.0]
    for r in range(1,N+2): eta.append(eta[-1]*(1-3.0**-r))
    probs=[]
    for r in range(N):
        a=eta_inf*3.0**(-r*(r+1))/(eta[r]*eta[r+1])   # Cohen-Lenstra, real quadratic, P(rk3=r)
        probs.append(a); tot+=a; s+=a*3.0**-(r+1)
    return s,tot,probs
def solve(A,b):
    n=len(A); M=[row[:]+[bb] for row,bb in zip(A,b)]
    for i in range(n):
        p=max(range(i,n),key=lambda k:abs(M[k][i])); M[i],M[p]=M[p],M[i]
        for k in range(n):
            if k!=i:
                f=M[k][i]/M[i][i]
                for j in range(i,n+1): M[k][j]-=f*M[i][j]
    return [M[i][n]/M[i][i] for i in range(n)]
def chi2sf5(x):
    return math.erfc(math.sqrt(x/2))+math.sqrt(2*x/math.pi)*math.exp(-x/2)*(1+x/3)
def load(fn):
    rows=list(csv.reader(open(fn)))[1:]
    return [list(map(int,r)) for r in rows]
def series(rows,which):
    out=[]
    for i in range(1,len(rows)):
        a,b=rows[i-1],rows[i]
        d=[y-x for x,y in zip(a[1:],b[1:])]
        if which=='agg': s=d[1]+d[3]+d[5]+d[7]; n=sum(d)
        else: r=which; s=d[2*r+1]; n=d[2*r]+d[2*r+1]
        out.append((a[0],b[0],math.sqrt(a[0]*b[0]),s,n))
    return out
def test(bins,p0,terms=2,varscale=1.0):
    fit=[b for b in bins if b[0]>=10**6 and b[1]<=10**10]
    new=[b for b in bins if b[0]>=10**10]
    assert len(fit)==40 and len(new)==5,(len(fit),len(new))
    basis=lambda x:[x**(-1/6),x**(-1/3)][:terms]
    N=[[0.0]*terms for _ in range(terms)]; rhs=[0.0]*terms
    for lo,hi,x,s,n in fit:
        pt=(s+0.5)/(n+1); var=varscale*pt*(1-pt)/n; w=1/var; f=basis(x); y=s/n-p0
        for i in range(terms):
            rhs[i]+=w*f[i]*y
            for j in range(terms): N[i][j]+=w*f[i]*f[j]
    c=solve(N,rhs)
    S=[solve(N,[1.0 if i==j else 0.0 for i in range(terms)]) for j in range(terms)]  # inverse (symmetric)
    res=[];J=[];V=[]
    for lo,hi,x,s,n in new:
        f=basis(x); q=p0+sum(ci*fi for ci,fi in zip(c,f)); res.append(s/n-q); J.append(f); V.append(varscale*q*(1-q)/n)
    C=[[ (V[i] if i==j else 0.0)+sum(J[i][a]*S[a][b]*J[j][b] for a in range(terms) for b in range(terms)) for j in range(5)] for i in range(5)]
    z=solve(C,res); T=sum(a*b for a,b in zip(res,z))
    # chi2 of the fit itself (for information)
    chi=0
    for lo,hi,x,s,n in fit:
        pt=(s+0.5)/(n+1); var=varscale*pt*(1-pt)/n; f=basis(x); chi+=(s/n-p0-sum(ci*fi for ci,fi in zip(c,f)))**2/var
    return c,T,chi2sf5(T),chi,res,V
def shift_interval(bins,p0):
    held=lambda d: test(bins,p0+d)[2]>0.01
    def edge(sign):
        lo=0.0; hi=sign*1e-5
        if not held(0.0): return float('nan')
        while held(hi): hi*=2
        for _ in range(60):
            m=(lo+hi)/2
            if held(m): lo=m
            else: hi=m
        return lo
    return edge(-1),edge(+1)
if __name__=="__main__":
    fn=sys.argv[1] if len(sys.argv)>1 else '/tmp/work/pk2/table.csv'
    rows=load(fn)
    pa,tot,probs=pconj_total()
    print("p_conj aggregate = %.10f (sum of CL probs %.12f); CL P(r)=%s"%(pa,tot,["%.6g"%p for p in probs[:5]]))
    for name,which,p0 in [('aggregate','agg',pa),('r=0',0,1/3),('r=1',1,1/9),('r=2',2,1/27)]:
        b=series(rows,which)
        c,T,p,chi,res,V=test(b,p0)
        c_h,T_h,p_h,_,_,_=test(b,p0,varscale=0.5)
        c1,T1,p1,chi1,_,_=test(b,p0,terms=1)
        lo,hi=shift_interval(b,p0)
        print("%-9s M2 c1=%.5f c2=%.5f T=%.2f p=%.3f %s | halved T=%.2f p=%.4f %s | M1 c1=%.5f T=%.2f p=%.4f %s | shift [%.5f, %+.5f] | fit chi2(38 dof) M2=%.1f M1(39)=%.1f"%(
          name,c[0],c[1],T,p,'HELD' if p>0.01 else 'FAILED',T_h,p_h,'HELD' if p_h>0.01 else 'FAILED',c1[0],T1,p1,'HELD' if p1>0.01 else 'FAILED',lo,hi,chi,chi1))
        print("          new-bin residuals/sigma_binom:",["%.2f"%(r/math.sqrt(v)) for r,v in zip(res,V)])
