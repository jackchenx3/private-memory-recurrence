"""Check prospective algebra on two-state fixtures, never read study061outcomes."""
from fractions import Fraction as F
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
mu=F(1,16);beta=1-2*mu;scale=beta/(2*mu)
PZ=[[F(3,4),F(1,4)],[F(1,2),F(1,2)]]
PH=[[F(1,2),F(1,2)],[F(1,4),F(3,4)]]
h=[F(0),F(1)];trueZ=[F(2,3),F(1,3)];trueH=[F(1,3),F(2,3)]
dot=lambda a,b:sum((x*y for x,y in zip(a,b)),F(0))
mv=lambda p:[dot(row,h) for row in p]
dZ=[(x-mu)/beta-y for x,y in zip(mv(PZ),h)];dH=[(x-mu)/beta-y for x,y in zip(mv(PH),h)]
span=lambda a:max(a)-min(a)
f=[scale*(a-b) for a,b in zip(dH,dZ)];g=[scale*(a+b)/2 for a,b in zip(dH,dZ)]
def quantities(z,hp):
 sz=dot(z,dZ);sh=dot(hp,dH);direct=dot([(a+b)/2 for a,b in zip(z,hp)],f);occ=dot([a-b for a,b in zip(hp,z)],g)
 return [sz,sh,sh-sz,direct,occ,direct+occ]
true=quantities(trueZ,trueH);checks=0;nonzero_corrections=0
for dz in [F(-1,100),F(0),F(1,100)]:
 for dh in [F(-1,100),F(0),F(1,100)]:
  z=[trueZ[0]+dz,trueZ[1]-dz];hp=[trueH[0]+dh,trueH[1]-dh];q=quantities(z,hp);ez,eh=abs(dz),abs(dh)
  radii=[ez*span(dZ),eh*span(dH),ez*span(dZ)+eh*span(dH),(ez+eh)*span(f)/2,(ez+eh)*span(g),scale*(ez*span(dZ)+eh*span(dH))]
  for val,exact,radius in zip(q,true,radii):assert val-radius<=exact<=val+radius;checks+=1
  assert q[5]==scale*q[2];checks+=1
  rz=dot(z,[a-b for a,b in zip(mv(PZ),h)]);rh=dot(hp,[a-b for a,b in zip(mv(PH),h)])
  correction=(rh-rz)/(2*mu)
  assert q[5]-(dot(hp,h)-dot(z,h))==correction;checks+=1
  nonzero_corrections+=int(correction!=0)
assert scale==7 and nonzero_corrections>0
result=dict(status='PASS',fixture='Two explicit two-state rational kernels; analytic stationary weights and nine fixed perturbed-weight pairs',exact_checks=checks,nonzero_residual_corrections=nonzero_corrections,study061_files_read=0,production_transition_rows=0,stationary_solves=0,new_component_outcomes_seen=False)
(R/'outputs/coordination/tasks/ORG-STATIONARY-FLOW-062-PROSPECTIVE_CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
