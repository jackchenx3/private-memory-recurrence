from pathlib import Path
from fractions import Fraction
import json,math
P=Path(__file__).resolve().parent
h=lambda x,y:bin(x^y).count('1')
checks=targets=0
for n in range(1,9):
 for d in range(n+1):
  x=0;y=(1<<d)-1;rows=[(h(x,t),h(y,t)) for t in range(1<<n)];den=len(rows)
  ex=sum(Fraction(a,den) for a,b in rows);ey=sum(Fraction(b,den) for a,b in rows)
  cov=sum(Fraction(a*b,den) for a,b in rows)-ex*ey
  gain=sum(Fraction(max(a-b,0),den) for a,b in rows)
  exact=Fraction(d*math.comb(d-1,(d-1)//2),1<<d) if d else Fraction()
  assert ex==ey==Fraction(n,2) and cov==Fraction(n-2*d,4) and gain==exact
  checks+=1;targets+=den
parents=[0,0];probes_a=[1,1];probes_b=[1,2];background=[0,0,0,1];a=parents+probes_a+background;b=parents+probes_b+background
assert [h(x,y) for x,y in zip(parents,probes_a)]==[h(x,y) for x,y in zip(parents,probes_b)]==[1,1]
score=lambda pool,t:Fraction(sum(sorted(h(x,t) for x in pool)[:2]),2)
table=[dict(target=format(t,'02b'),selected_mean_A=str(score(a,t)),selected_mean_B=str(score(b,t))) for t in range(4)]
ea=sum((score(a,t) for t in range(4)),Fraction())/4;eb=sum((score(b,t) for t in range(4)),Fraction())/4
assert ea==Fraction(1,2) and eb==Fraction(3,8) and ea-eb==Fraction(1,8)
result=dict(status='PASS',covariance_and_local_gain_cases=checks,enumerated_targets=targets,pool_targets=4,pool_A=a,pool_B=b,parent_probe_distances=[1,1],selected_mean_A=str(ea),selected_mean_B=str(eb),mean_difference=str(ea-eb),table=table,random_draws=0,population_paths=0,scope='Exact finite fixed-candidate assay; no claim that these are trajectories of the research model.')
(P/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
