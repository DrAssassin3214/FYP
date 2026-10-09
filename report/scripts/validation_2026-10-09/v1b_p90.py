import json, math, sys, numpy as np
from pathlib import Path
REPO=Path('/home/claude/drassassin3214/fyp'); sys.path.insert(0,str(REPO))
case=json.load(open(REPO/'examples/example_analysis_case.json',encoding='utf-8-sig'))
T0=16; DL=20
def rl_for(ids):
    rl={r['id']:dict(p=r['p']['value'],a=r['delay']['a'],m=r['delay']['m'],b=r['delay']['b']) for r in case['risks']}
    extra=[]
    for mid in ids:
        m=[x for x in case['mitigations'] if x['id']==mid][0]; t=m['risk_id']
        if m.get('p_after'): rl[t]['p']=m['p_after']['value']
        if m.get('delay_after'): d=m['delay_after']; rl[t].update(a=d['a'],m=d['m'],b=d['b'])
        for s in m.get('secondary_risks') or []: extra.append(dict(p=s['p']['value'],a=s['delay']['a'],m=s['delay']['m'],b=s['delay']['b']))
    return list(rl.values())+extra
def mc(ids, N, seed, chunk=2_000_000):
    rng=np.random.default_rng(seed); rl=rl_for(ids)
    allT=[]
    for _ in range(N//chunk):
        D=np.zeros(chunk)
        for r in rl:
            occ=rng.random(chunk)<r['p']
            s=r['b']-r['a']; al=1+4*(r['m']-r['a'])/s; be=1+4*(r['b']-r['m'])/s
            D+=np.where(occ, r['a']+s*rng.beta(al,be,chunk), 0.0)
        allT.append(T0+D)
    T=np.concatenate(allT); return T
out={}
for name,ids in [('ACCEPT',()),('O-M-BUF+M-QC',('M-BUF','M-QC')),('O-M-BUF+M-COV',('M-BUF','M-COV'))]:
    T=mc(ids,20_000_000,424242)
    q=float(np.quantile(T,0.9)); n=len(T)
    # SE of the quantile via order-statistic CI
    s=np.sort(T); half=1.96*math.sqrt(n*0.09); lo=s[int(n*0.9-half)]; hi=s[int(n*0.9+half)]
    out[name]=dict(P90=q,ci=(float(lo),float(hi)),pexc=float((T>DL).mean()),mean=float(T.mean()-T0))
    print(name,out[name])
json.dump(out,open(Path(sys.argv[1])/'v1b_p90.json','w'))
