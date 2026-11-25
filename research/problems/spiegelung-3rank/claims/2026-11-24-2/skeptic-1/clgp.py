# Independent validation: 3-ranks of class groups of quadratic fields via binary quadratic forms (pure Python).
# Imaginary: reduced forms + Gauss composition, count classes with f^3 = 1.
# Real: cycles of reduced indefinite forms (narrow class group; same 3-rank), cube each cycle.
import sys, math
from math import gcd, isqrt
def xgcd(a,b):
    x0,x1,y0,y1=1,0,0,1
    while b: q=a//b; a,b=b,a-q*b; x0,x1=x1,x0-q*x1; y0,y1=y1,y0-q*y1
    return a,x0,y0
def compose(f,g,D):
    a1,b1,c1=f; a2,b2,c2=g
    s=(b1+b2)//2
    d1,u,v=xgcd(a1,a2)
    d,U,w=xgcd(d1,s)     # d = U*d1 + w*s = U*u*a1 + U*v*a2 + w*s
    x,y=U*u,U*v
    a3=a1*a2//(d*d)
    # B = b2 + 2*a2/d * ( y*(b1-b2)/2 ... ) standard: 
    b3=(b2+2*(a2//d)*((v*U*( (b1-b2)//2) - w*c2)))% (2*a3)
    c3=(b3*b3-D)//(4*a3)
    return (a3,b3,c3)
def red_im(f):
    a,b,c=f
    while True:
        if c<a: a,b,c=c,-b,a
        if b>a or b<=-a:
            k=(a-b)//(2*a) if True else 0
            # choose b in (-a,a]
            r=b%(2*a)
            if r>a: r-=2*a
            k=(r-b)//(2*a)
            c=c+k*b+k*k*a; b=r
            continue
        if a==c and b<0: b=-b
        if c>=a: return (a,b,c)
def rank_im(D):  # D<0 fundamental
    forms=[]
    a=1
    while 3*a*a<=-D:
        for b in range(-a+1,a+1):
            if (b*b-D)%(4*a)==0:
                c=(b*b-D)//(4*a)
                if c>=a and not (a==c and b<0) and gcd(gcd(a,abs(b)),c)==1: forms.append((a,b,c))
        a+=1
    idf=red_im((1,D%2,(D%2-D)//4))
    n=0
    for f in forms:
        f2=red_im(compose(f,f,D)); f3=red_im(compose(f2,f,D))
        assert (f3[1]**2-4*f3[0]*f3[2])==D
        if f3==idf: n+=1
    r=0
    while n>1: assert n%3==0; n//=3; r+=1
    return r,len(forms)
def rho(f,D,s):
    a,b,c=f   # indefinite reduced: 0<b<sqrt(D), sqrt(D)-b<2|a|<sqrt(D)+b
    # rho(a,b,c)=(c,b',a') with b' = -b mod 2c in (s-2|c|, s]  (s=floor sqrt D)
    ac=abs(c)
    bp=(-b)%(2*ac)
    if ac*ac>D:               # |c| > sqrt(D): normalise to -|c| < b' <= |c|
        if bp>ac: bp-=2*ac
    else:
        bp+= ((s-bp)//(2*ac))*(2*ac)
    return (c,bp,(bp*bp-D)//(4*c))
def isred(f,D,s):
    a,b,c=f
    if not (0<b<=s): return False
    aa=2*abs(a)
    # sqrt(D)-b < 2|a| < sqrt(D)+b
    return (aa+b)**2>D and aa-b<=s and (aa-b)**2<D if aa-b>=0 else (aa+b)**2>D
def red_re(f,D,s):
    n=0
    while not isred(f,D,s):
        f=rho(f,D,s); n+=1
        assert n<10000
    return f
def rank_re(D):
    s=isqrt(D)
    forms=[]
    for b in range(1,s+1):
        if (b-D)%2: continue
        m=(b*b-D)//4   # a*c = m <0
        mm=-m
        for a in range(1,isqrt(mm)+1):
            if mm%a==0:
                for A in {a,mm//a}:
                    for sg in (1,-1):
                        f=(sg*A,b,-sg*(mm//A))
                        if isred(f,D,s) and gcd(gcd(A,b),mm//A)==1: forms.append(f)
    cyc={}; ncyc=0; reps=[]
    for f in forms:
        if f in cyc: continue
        g=f
        while g not in cyc:
            cyc[g]=ncyc; g=rho(g,D,s); assert isred(g,D,s)
        reps.append(f); ncyc+=1
    idf=red_re((1,s if (s-D)%2==0 else s-1,0) if False else (1,(s if (s-D)%2==0 else s-1),(( (s if (s-D)%2==0 else s-1))**2-D)//4),D,s)
    pid=cyc[idf]
    n=0
    for f in reps:
        f2=compose(f,f,D); f3=compose(f2,f,D)
        a,b,c=f3; assert b*b-4*a*c==D
        if cyc[red_re(f3,D,s)]==pid: n+=1
    r=0
    while n>1: assert n%3==0,(D,n); n//=3; r+=1
    return r,ncyc
def fund_pos(N0,N1):
    for d in range(max(N0,2),N1+1):
        if d%4==1: m=d
        elif d%16 in (8,12): m=d//4
        else: continue
        ok=True; p=2
        while p*p<=m:
            if m%(p*p)==0: ok=False;break
            p+=1
        if ok: yield d
if __name__=="__main__":
    N0=int(sys.argv[1]); N1=int(sys.argv[2])
    cks=[int(l.split(',')[0]) for l in open('/tmp/work/pk2/table.csv').read().split()[1:]]
    cnt={}
    out=open(sys.argv[3],'w')
    ci=0; viol=0
    for d in fund_pos(N0,N1):
        while ci<len(cks) and d>cks[ci]:
            out.write("CK %d %s\n"%(cks[ci],sorted(cnt.items()))); ci+=1
        r,h=rank_re(d)
        Dm=-3*d if d%3 else -d//3
        rp,hm=rank_im(Dm)
        if rp-r not in (0,1): viol+=1
        cnt[(r,rp-r)]=cnt.get((r,rp-r),0)+1
        if d<1100: out.write("d %d h+ %d r %d  mirror %d h %d r' %d\n"%(d,h,r,Dm,hm,rp))
    while ci<len(cks) and N1>=cks[ci]:
        out.write("CK %d %s\n"%(cks[ci],sorted(cnt.items()))); ci+=1
    out.write("viol %d\n"%viol)
