# Numerical/exact sanity checks of the algebraic facts used by cubicrank.c
import random, cmath, itertools
import numpy as np

def disc(a,b,c,d): return b*b*c*c-4*a*c**3-4*b**3*d-27*a*a*d*d+18*a*b*c*d
def hess(a,b,c,d): return (b*b-3*a*c, b*c-9*a*d, c*c-3*b*d)
def act(f,g):
    # twisted action f^g(x,y) = det(g)^{-1} f(al x + ga y, be x + de y), g=[[al,be],[ga,de]]
    a,b,c,d=f; (al,be),(ga,de)=g
    det=al*de-be*ga
    # expand f(al x+ga y, be x+de y) as cubic in x,y
    # use polynomial multiplication on coefficient lists in powers x^3..y^3
    def lin(p,q): return [p,q]  # p x + q y
    def mul(u,v):
        r=[0]*(len(u)+len(v)-1)
        for i,x in enumerate(u):
            for j,y in enumerate(v): r[i+j]+=x*y
        return r
    X=lin(al,ga); Y=lin(be,de)
    terms=[mul(mul(X,X),X), mul(mul(X,X),Y), mul(mul(X,Y),Y), mul(mul(Y,Y),Y)]
    out=[0,0,0,0]
    for coef,t in zip((a,b,c,d),terms):
        for i in range(4): out[i]+=coef*t[i]
    return tuple(o*det for o in out)  # det^{-1}=det for det=+-1
def qact(H,g):
    P,Q,R=H; (al,be),(ga,de)=g
    # H(al x+ga y, be x+de y)
    return (P*al*al+Q*al*be+R*be*be, 2*P*al*ga+Q*(al*de+be*ga)+2*R*be*de, P*ga*ga+Q*ga*de+R*de*de)

random.seed(1)
mats=[((p,q),(r,s)) for p,q,r,s in itertools.product(range(-3,4),repeat=4) if abs(p*s-q*r)==1]
bad=0
for _ in range(2000):
    f=tuple(random.randint(-20,20) for _ in range(4))
    g=random.choice(mats)
    if hess(*act(f,g))!=qact(hess(*f),g): bad+=1
    if disc(*act(f,g))!=disc(*f): bad+=1
    # syzygy at (1,0): 4P^3 = G0^2 + 27 D a^2 with G0^2 = 9a^2Q^2-4P(9a^2R-P^2)
    a,b,c,d=f; P,Q,R=hess(*f); D=disc(*f)
    if 4*P**3 - 27*D*a*a != 9*a*a*Q*Q-4*P*(9*a*a*R-P*P): bad+=1
    if 3*a*R-b*Q+c*P!=0: bad+=1
    if 4*P*R-Q*Q!=3*D: bad+=1
print("identity failures:",bad)

# tau conditions for D<0
bad=0;n=0
for _ in range(20000):
    a=random.randint(1,30); b,c,d=(random.randint(-60,60) for _ in range(3))
    D=disc(a,b,c,d)
    if D>=0: continue
    r=np.roots([a,b,c,d])
    tau=[z for z in r if z.imag>1e-9]
    if len(tau)!=1: continue
    t=tau[0]; n+=1
    c1=(a*d-b*c>0)==(t.real>0)
    c2=(a*d-b*c<(a+b)**2+a*c)==(t.real<0.5)
    c3=(d*d-a*a+a*c-b*d>0)==(abs(t)>1)
    c4=(a*d-b*c>-(a-b)**2-a*c)==(t.real>-0.5)
    if not(c1 and c2 and c3 and c4): bad+=1
print("tau-condition mismatches:",bad,"of",n)
