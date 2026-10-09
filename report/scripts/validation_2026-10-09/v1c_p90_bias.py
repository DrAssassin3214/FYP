import json, math, sys, numpy as np
from pathlib import Path
REPO=Path('/home/claude/drassassin3214/fyp'); sys.path.insert(0,str(REPO))
from app import analysis
from app.engine.decision import apply_mitigations
from app.engine.simulation import simulate, summarise
from app.engine.models import Activity
case=json.load(open(REPO/'examples/example_analysis_case.json',encoding='utf-8-sig'))
pa=analysis.parse_analysis(case); risks=pa['risks']; mm={m.mitigation_id:m for m in pa['mitigations']}
act=Activity('A','A',pa['planned'],deadline_days=pa['deadline'])
ref=json.load(open(Path(sys.argv[1])/'v1b_p90.json'))
N=50_000; SEEDS=range(5000,5100)
res={}
for name,ids in [('ACCEPT',()),('O-M-BUF+M-QC',('M-BUF','M-QC')),('O-M-BUF+M-COV',('M-BUF','M-COV'))]:
    resid=apply_mitigations(risks,[mm[i] for i in ids])
    p90=[];cover=0
    for s in SEEDS:
        r=simulate(act,resid,N,s); sm=summarise(r,deadline_days=20)
        p90.append(sm['percentiles']['P90']); lo,hi=sm['percentile_ci95']['P90']; cover+=(lo<=ref[name]['P90']<=hi)
    p90=np.array(p90); se=p90.std(ddof=1)/math.sqrt(len(p90))
    res[name]=dict(mean_P90=float(p90.mean()),ref=ref[name]['P90'],diff=float(p90.mean()-ref[name]['P90']),se_mean=float(se),
                   z=float((p90.mean()-ref[name]['P90'])/math.hypot(se,(ref[name]['ci'][1]-ref[name]['ci'][0])/3.92)),sd_single=float(p90.std(ddof=1)),coverage=cover/len(SEEDS))
    print(name,res[name])
json.dump(res,open(Path(sys.argv[1])/'v1c_p90_bias.json','w'))
