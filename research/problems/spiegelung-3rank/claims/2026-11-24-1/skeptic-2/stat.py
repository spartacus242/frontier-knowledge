import csv,math,sys
rows=list(csv.reader(open(sys.argv[1] if len(sys.argv)>1 else '/tmp/work/pk/table.csv')))[1:]
T={int(r[0]):list(map(int,r[1:])) for r in rows}
Xmax=int(sys.argv[2]) if len(sys.argv)>2 else 10**9
ks=[k for k in range(30,91) if round(10**(k/10))<=Xmax and round(10**(k/10)) in T]
cp=[round(10**(k/10)) for k in ks]
def get(x): return T[x]
def quant(v,q):
    if q=='all': n=sum(v); s=v[1]+v[3]+v[5]+v[7]
    else:
        r=int(q); n=v[2*r]+v[2*r+1]; s=v[2*r+1]
    return n,s
def solve(A,b):
    n=len(A); M=[row[:]+[b[i]] for i,row in enumerate(A)]
    for i in range(n):
        p=max(range(i,n),key=lambda r:abs(M[r][i])); M[i],M[p]=M[p],M[i]
        for r in range(n):
            if r!=i:
                f=M[r][i]/M[i][i]; M[r]=[x-f*y for x,y in zip(M[r],M[i])]
    return [M[i][n]/M[i][i] for i in range(n)]
for q,lim in [('all',0.29765117),('0',1/3),('1',1/9),('2',1/27)]:
    xs=[];ps=[];ws=[]
    for i in range(len(cp)-1):
        if cp[i]< 10**6: continue
        a,b=get(cp[i]),get(cp[i+1])
        n1,s1=quant(a,q); n2,s2=quant(b,q); n=n2-n1; s=s2-s1
        p=s/n if n else 0.0
        var=((s+.5)/(n+1))*(1-(s+.5)/(n+1))/n if n else None
        if n==0: var=0.25  # empty bin finite weight (n->1 effective)
        xs.append(math.sqrt(cp[i]*cp[i+1])); ps.append(p); ws.append(1/var)
    # WLS p = a + c x^(-1/6)
    u=[x**(-1/6) for x in xs]
    S=sum(ws);Su=sum(w*t for w,t in zip(ws,u));Suu=sum(w*t*t for w,t in zip(ws,u))
    Sp=sum(w*p for w,p in zip(ws,ps));Sup=sum(w*t*p for w,t,p in zip(ws,u,ps))
    det=S*Suu-Su*Su
    a=(Suu*Sp-Su*Sup)/det; c=(S*Sup-Su*Sp)/det
    se=math.sqrt(Suu/det)
    chi=sum(w*(p-a-c*t)**2 for w,p,t in zip(ws,ps,u)); dof=len(xs)-2
    print(q,'bins',len(xs),'p_inf=%.6f se=%.6f c=%.4f chi2=%.1f dof=%d lim=%.6f z=%.2f'%(a,se,c,chi,dof,lim,(a-lim)/se),'VOID' if chi>2*dof else ('CONSISTENT' if abs(a-lim)<=3*se else 'INCONSISTENT'))
