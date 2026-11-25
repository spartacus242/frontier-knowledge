import math, sys
sys.argv=['x','/tmp/work/pk/table.csv']
import fit_test as F
def chi2_cdf(x,k):
    # regularized lower gamma P(k/2, x/2) via series
    a=k/2; z=x/2; s=1/a; t=s
    for n in range(1,500):
        t*=z/(a+n); s+=t
    return s*math.exp(-z+a*math.log(z)-math.lgamma(a))
res,_=F.run('/tmp/work/pk/table.csv')
for rr,(p,se,c,chi2,dof) in res.items():
    t=0.29765117 if rr is None else 3.0**-(rr+1)
    s=math.sqrt(chi2/dof)
    print(rr, 'P(chi2<=obs)=%.4f'%chi2_cdf(chi2,dof), 'z=%.2f'%((p-t)/se), 'z(rescaled SE)=%.2f'%((p-t)/(se*s)))
for xmin in (10**5, 10**7, 10**8):
    res,_=F.run('/tmp/work/pk/table.csv',Xmin=xmin)
    print('Xmin',xmin, {('all' if k is None else k):(round(v[0],6),round(v[1],6),round(v[3],1),v[4], round((v[0]-(0.29765117 if k is None else 3.0**-(k+1)))/v[1],2)) for k,v in res.items()})
