import subprocess, sys, time
oe = dict(map(int,l.split()) for l in open('/tmp/work/sr3/oeis_A304884.txt'))
lo, hi = int(sys.argv[1]), int(sys.argv[2]); BIN = sys.argv[3] if len(sys.argv)>3 else '/tmp/work/sr3/cyc'
for n in range(lo, hi+1):
    t=time.time(); K=1; last=None
    while True:
        out = subprocess.run([BIN,str(n),str(K+1)],capture_output=True,text=True).stdout.strip()
        if out.startswith('FOUND'): K+=1; last=out
        else: break
    print(n, K, oe.get(n), 'MATCH' if oe.get(n)==K else 'MISMATCH', f'{time.time()-t:.2f}s', '| upper:', out, flush=True)
