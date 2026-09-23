from fractions import Fraction as F
from pathlib import Path
import datetime,json,math
O=Path(__file__).resolve().parent
checks=0
# These are exact component inequalities, not sampling or population propagation.
for M in range(1,25):
 grids=[[F(k+1,M+1) for k in range(M)], [F(k,M) for k in range(M)], [F(k+1,M) for k in range(M)], [F(2*k+1,2*M) for k in range(M)]]
 for q in grids:
  assert all(F(k,M)<=x<=F(k+1,M) for k,x in enumerate(q));checks+=1
  thresholds=set([F(0),F(1)]+q+[F(k,3*M) for k in range(3*M+1)])
  for power in range(1,9):
   # Integral of |v**power - q(v)**power|, split exactly at each cell representative.
   value=F(0)
   for k,x in enumerate(q):
    lo,hi=F(k,M),F(k+1,M);fx=x**power
    left=fx*(x-lo)-(x**(power+1)-lo**(power+1))/F(power+1)
    right=(hi**(power+1)-x**(power+1))/F(power+1)-fx*(hi-x)
    assert left>=0 and right>=0;value+=left+right
    thresholds.add(fx)
   assert value<=F(1,M);checks+=1
  for t in thresholds:
   # Either tie priority gives a threshold cut within one cell width of t.
   strict_cut=F(sum(x<=t for x in q),M)
   weak_cut=F(sum(x<t for x in q),M)
   assert abs(strict_cut-t)<=F(1,M) and abs(weak_cut-t)<=F(1,M);checks+=1
M=2**52;n=128;T=40;pairs=n*(n-1)//2
step=F(2*pairs,M);path=T*step
assert pairs==8128 and step==F(16256,2**52) and path==F(650240,2**52);checks+=3
# Earlier tie counterexample magnitude is compatible with the present error floor.
assert F(1,M)<=2*step;checks+=1
out=dict(status='PASS',completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),exact_component_checks=checks,cell_counts_tested=list(range(1,25)),cell_rules=['k+1 over M+1','left endpoint','right endpoint','midpoint'],monotone_powers_checked=list(range(1,9)),clock_count=n,updates=T,grid_denominator=M,per_update_order_mismatch_bound_exact=str(step),per_update_order_mismatch_bound=float(step),trajectory_TV_bound_exact=str(path),trajectory_TV_bound=float(path),two_endpoint_bridge_floor=float(2*path),scientific_paths_run=0,objective_calls=0,random_values_generated=0,machine_logarithm_accuracy_certified=False,scope='Exact checks of the two inequalities used in the written proof; finite checks do not replace its general monotonicity argument.')
(O/'CHECKS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
