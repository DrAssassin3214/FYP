import json, math, sys, numpy as np
from pathlib import Path
REPO=Path('/home/claude/drassassin3214/fyp'); sys.path.insert(0,str(REPO))
from app.engine.simulation import quantile_ci, simulate, summarise
from app import analysis
from app.engine.models import Activity
# (1) quantile_ci on iid exponential data: true P90 = -ln(0.1)
rng=np.random.default_rng(11); true=-math.log(0.1)
for n in (1000,10000,50000):
    cov=0; T=3000
    for _ in range(T):
        x=np.sort(rng.exponential(size=n)); lo,hi=quantile_ci(x,0.9); cov+=(lo<=true<=hi)
    print(f'iid exponential n={n}: coverage {cov/T:.3f} (+/-{math.sqrt(.95*.05/T):.3f})')
# (2) engine, ACCEPT, n=10k, 600 seeds, truth = 20M-draw reference
ref=json.load(open(Path(sys.argv[1])/'v1b_p90.json'))['ACCEPT']['P90']
case=json.load(open(REPO/'examples/example_analysis_case.json',encoding='utf-8-sig'))
pa=analysis.parse_analysis(case); act=Activity('A','A',pa['planned'],deadline_days=pa['deadline'])
cov=0; T=600
for s in range(20000,20000+T):
    r=simulate(act,pa['risks'],10_000,s); x=np.sort(r.duration); lo,hi=quantile_ci(x,0.9); cov+=(lo<=ref<=hi)
print(f'engine ACCEPT n=10k, {T} seeds: coverage {cov/T:.3f} (+/-{math.sqrt(.95*.05/T):.3f})')
