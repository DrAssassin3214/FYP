import json, sys, copy, re
from pathlib import Path
REPO=Path('/home/claude/drassassin3214/fyp'); sys.path.insert(0,str(REPO))
from app import service, analysis
ex=json.loads(json.dumps(service.example_analysis_case()))
# n sweep
bad=[]
for n in list(range(1,16))+[20,50,100]:
    c=copy.deepcopy(ex); c['simulation']['n']=n
    try: analysis.run_analysis(c)
    except service.CaseError: pass
    except Exception as e: bad.append((n,type(e).__name__))
print('n values that crash run_analysis:', bad)
# lambda
for lam in (0,-1,1e-300):
    c=copy.deepcopy(ex); c['risks'][0]['delay']['lam']=lam
    try: analysis.run_analysis(c|{'simulation':{'n':300}}); print('lam',lam,'-> accepted')
    except service.CaseError as e: print('lam',lam,'-> CaseError:',e.problems[0][:90])
    except Exception as e: print('lam',lam,'-> UNHANDLED',type(e).__name__,e)
# explanation text vs numbers
r=analysis.run_analysis(ex)
print('--- explanation keys:', list(r['explanation'].keys()) if isinstance(r['explanation'],dict) else type(r['explanation']))
exp=r['explanation']
txt=json.dumps(exp) if not isinstance(exp,str) else exp
print(txt[:1500])
s=r['summary']; print('--- numbers: expected_delay %.3f P90 %.2f p_exceed %.3f E[cost] %.0f'%(s['expected_delay'],s['percentiles']['P90'],s['p_exceed_deadline'],r['cost']['expected_cost']))
md=r['report_markdown']; print('--- analysis.md length',len(md)); 
for pat in [r'P90[^\n]{0,80}', r'Expected total delay[^\n]{0,80}|expected delay[^\n]{0,80}', r'deadline[^\n]{0,100}']:
    m=re.findall(pat,md,flags=re.I)[:3]; print(pat[:20],'->',m)
