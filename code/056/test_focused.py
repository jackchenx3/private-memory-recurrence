"""Focused deterministic fixtures only: no population propagation, scoring, seeds or RNG."""
import unittest,ast,tempfile
from unittest.mock import patch
from common import *
from analysis import *
from model import rebase,substitute,step
from accepted_inputs055 import extend_targets
from accepted_transfer_model import step as accepted_step
from hpc_control import normalize,parse_accounting
from validate_analyze import interval,quantile
class Focused(unittest.TestCase):
 def test_operators_and_inputs(self):
  self.assertIs(step,accepted_step);self.assertEqual(verify_references(),53)
 def test_exact_diagonal_targets(self):
  table=read('TARGET_TABLE.json')
  for p in LAWS:
   diagonal=read('source055_'+p+'_TARGETS.json')['blocks']
   for b in range(24):self.assertEqual(table['P_'+p+'_Q_'+p][b]['targets'],diagonal[b]['targets'])
 def test_history_boundary_recursion(self):
  h=list(range(40));z=list(range(100,140));c=[1]*40;self.assertEqual(extend_targets(h,z,c,'HALF'),[38,39]*20);self.assertEqual(extend_targets(h,z,c,'ZERO'),z)
  c[0]=0;self.assertEqual(extend_targets(h,z,c,'HALF'),[100,39]*20)
 def test_no_splicing(self):
  ts=read('TARGET_TABLE.json');d=read('source055_TARGET_LAW_DRAWS.json')['blocks']
  for p in LAWS:
   hs=read('source055_reused052_'+p+'_TARGETS.json')['blocks']
   for q in LAWS:
    for b in range(24):self.assertEqual(ts['P_'+p+'_Q_'+q][b]['targets'],extend_targets(hs[b]['targets'],d[b]['innovations'],d[b]['copy_bits'],q))
 def test_states_labels_caches(self):
  ss=states();ds=keyed('streams.jsonl.gz');self.assertEqual(len(ss),768)
  for (b,r,p,bg),q in ss.items():
   pop,prov=rebase(q['population']);self.assertEqual(json.loads(json.dumps(pop)),q['rebased_population']);self.assertEqual(prov,q['founder_rebase_map']);labs=ds[b,r]['draws']['labels'];self.assertEqual(sorted(labs),list(range(32)))
   for slot in (None,labs[0],labs[1]):
    out=substitute(pop,bg,slot)
    for i,(before,after) in enumerate(zip(pop,out)):
     self.assertEqual(before[0],after[0]);self.assertEqual(before[2:],after[2:]);self.assertEqual(after[1],3-before[1] if i==slot else before[1])
 def test_pairing_and_reciprocal(self):
  rows={}
  for i,cfg in enumerate(CONFIGS):rows[cfg]=dict(founders={'p0':{'D40':i/32},'p1':{'D40':-i/32}},raw={'U':i/10,'U40':i/20})
  paired=base_estimands(rows);a,b=orientation(rows,0),orientation(rows,1)
  for k in ENDPOINTS:self.assertAlmostEqual(paired[k],(a[k]+b[k])/2,places=14)
  self.assertEqual(paired['F_BG_SWITCH|D40'],-1/64)
 def test_factorial_catalog(self):
  cells={g:{k:i for k in ENDPOINTS} for i,g in enumerate(CELLS)};v=combine(cells);self.assertEqual(len(v),162);self.assertEqual(v[PRIMARY],1);self.assertEqual(v['INTERACTION|F_BG_EFFECT|D40'],0);self.assertEqual(STRUCTURAL_ZEROS,())
 def test_budget(self):
  c=read('config.json');self.assertEqual(2*2*3*24*8,c['new_paths']);self.assertEqual(c['new_paths']*5152,11870208);self.assertEqual(c['new_random_draws'],0);self.assertEqual(c['new_preparations'],0);self.assertEqual(c['new_seeds'],0)
 def test_bootstrap_units_and_negative(self):
  idx=read('source055_BOOTSTRAP_INDICES.json');self.assertEqual(len(idx),2000);self.assertTrue(all(len(x)==24 and all(type(i)==int and 0<=i<24 for i in x) for x in idx));self.assertEqual(interval([-1]*24,idx),(-1,[-1,-1]));self.assertEqual(quantile([0,10],.25),2.5)
 def test_slurm_unknown_and_steps(self):
  self.assertEqual(normalize('new_state'),'UNKNOWN');self.assertEqual(normalize('COMPLETED','1:0'),'FAILED');self.assertEqual(normalize('COMPLETED','0:0'),'COMPLETE');self.assertIsNone(parse_accounting('12.batch|COMPLETED|0:0|3|1|4G|short|00:15:00','12'));self.assertEqual(parse_accounting('12|RUNNING|0:0|3|1|4G|short|00:15:00','12')['status'],'RUNNING')
 def test_uncertain_submission_never_retried(self):
  import hpc_control
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'submission_attempt.json').write_text('{}')
   with patch.object(hpc_control,'P',root),patch.object(hpc_control,'verify_manifest'),patch.object(hpc_control.subprocess,'run') as run:
    with self.assertRaises(AssertionError):hpc_control.submit()
    run.assert_not_called()
 def test_existing_submission_is_reused(self):
  import hpc_control
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'submission.json').write_text('{}')
   with patch.object(hpc_control,'P',root),patch.object(hpc_control,'read',return_value={'job_id':'123'}),patch.object(hpc_control,'verify_manifest'),patch.object(hpc_control.subprocess,'run') as run:
    self.assertEqual(hpc_control.submit()['job_id'],'123');run.assert_not_called()
 def test_static_no_new_random_calls(self):
  for n in ('prepare_inputs.py','transfer.py','validate_analyze.py'):
   tree=ast.parse((P/n).read_text());self.assertFalse(any(isinstance(x,ast.Attribute) and x.attr in ('Random','random','randrange','getrandbits','shuffle') for x in ast.walk(tree)))
if __name__=='__main__':unittest.main(verbosity=2)
