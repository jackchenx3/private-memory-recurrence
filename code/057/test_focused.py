"""No scientific scoring, stochastic draws, or propagation in these fixtures."""
import unittest,ast,tempfile,collections
from unittest.mock import patch
from common import *
from seed_design import *
from analysis import *
from model import rebase,substitute,all_policy,step
from accepted_transfer_model import step as accepted_step
from accepted_inputs055 import extend_targets
from generators import build_targets,local_masks,scouts,ties,labels,bootstrap
from preparation_model import initial as initial052
from hpc_control import normalize,parse_accounting
from validate_analyze import interval,quantile
class FakeRNG:
 def __init__(self):self.calls=collections.Counter()
 def randrange(self,n):self.calls['randrange'+str(n)]+=1;return n-1
 def getrandbits(self,n):self.calls['getrandbits'+str(n)]+=1;return 0
 def random(self):self.calls['random']+=1;return .5
 def shuffle(self,x):self.calls['shuffle']+=1;x.reverse()
class Focused(unittest.TestCase):
 def test_operator_identity(self):self.assertIs(step,accepted_step);self.assertEqual(verify_references(),16)
 def test_seed_roster_inventory(self):self.assertTrue(verify_roster(read('SEED_ROSTER.json'),read('PRIOR_SEED_INVENTORY.json')['integers']))
 def test_seed_stage_separation(self):
  rs=roster();sets=[{q['seed'] for q in rs if q['family'].startswith(s+'_')} for s in ('initial','policy','continuation')]
  self.assertEqual([len(x) for x in sets],[768,1200,1200]);self.assertTrue(all(not sets[i]&sets[j] for i in range(3) for j in range(i)))
 def test_exact_generator_shapes_and_draw_counts(self):
  r=FakeRNG();self.assertEqual(len(local_masks(r)),40);self.assertEqual(r.calls['randrange32'],40*32*32);self.assertEqual(len(scouts(r)),40);self.assertEqual(r.calls['getrandbits32'],1280);self.assertEqual(len(ties(r)[0]),128);self.assertEqual(r.calls['random'],5120);self.assertEqual(labels(r),list(reversed(range(32))));self.assertEqual(len(bootstrap(r)),2000);self.assertEqual(r.calls['randrange24'],48000)
 def test_target_recursion_boundary(self):
  h=build_targets([4,8],list(range(100,138)),[1]*38,'HALF');self.assertEqual(h,[4,8]*20);z=list(range(200,240));self.assertEqual(extend_targets(h,z,[1]*40,'HALF'),[4,8]*20);self.assertEqual(extend_targets(h,z,[0]*40,'HALF'),z);self.assertEqual(extend_targets(h,z,[1]*40,'ZERO'),z)
 def test_initial052_distribution(self):
  p=initial052('SHAM_C0',list(range(32)));self.assertTrue(all(q[0]==0 for q in p));self.assertEqual([q[2] for q in p],list(range(32)));self.assertEqual(sum(q[1] for q in p),1)
 def test_all_policy_and_exact_cache_rebase(self):
  for bg in ('F','H'):
   old=all_policy(list(range(32)),bg);old=[(x,k,7,(x^3,17,31-i)) for i,(x,k,f,c) in enumerate(old)];p,m=rebase(old);self.assertEqual([q[3] for q in old],[q[3] for q in p]);self.assertTrue(all(x['preparation_founder']==7 for x in m))
   for slot in (None,2,11):
    new=substitute(p,bg,slot)
    for i,(a,b) in enumerate(zip(p,new)):self.assertEqual(a[0],b[0]);self.assertEqual(a[2:],b[2:]);self.assertEqual(b[1],3-a[1] if i==slot else a[1])
 def test_pairing(self):
  rr={cfg:dict(founders={'p0':{'D40':i/32},'p1':{'D40':-i/32}},raw={'U':i/10,'U40':i/20}) for i,cfg in enumerate(CONFIGS)};v=base_estimands(rr);a,b=orientation(rr,0),orientation(rr,1)
  for k in ENDPOINTS:self.assertAlmostEqual(v[k],(a[k]+b[k])/2,places=14)
 def test_catalog_and_factorial(self):
  d={g:{k:i for k in ENDPOINTS} for i,g in enumerate(CELLS)};v=combine(d);self.assertEqual(len(v),162);self.assertEqual(v[PRIMARY],1);self.assertEqual(v['INTERACTION|F_BG_EFFECT|D40'],0);self.assertEqual(STRUCTURAL_ZEROS,())
 def test_block_bootstrap_and_negative(self):
  idx=[list(range(24))]*2000;self.assertEqual(interval([-1]*24,idx),(-1,[-1,-1]));self.assertEqual(quantile([0,10],.25),2.5)
 def test_counts_and_unfiltered_design(self):
  self.assertEqual(24*8,192);self.assertEqual(192*2*2,768);self.assertEqual(768*2*3,4608);self.assertEqual((192+768+4608)*5152,28686336);self.assertEqual(4608*5152,23740416)
  code=(P/'transfer.py').read_text();self.assertIn("[('ZERO','ZERO'),('ZERO','HALF'),('HALF','ZERO'),('HALF','HALF')]",code);self.assertIn('assert n==4608 and len(used)==768',code)
 def test_stage_pairing_sources(self):
  for n in ('prepare_policy.py','transfer.py'):
   tree=ast.parse((P/n).read_text());self.assertFalse(any(isinstance(x,ast.Attribute) and x.attr in ('Random','getrandbits','randrange','shuffle','random') for x in ast.walk(tree)))
  s=(P/'make_inputs.py').read_text();self.assertIn("for stage in ('initial','policy','continuation')",s);self.assertIn("stem='' if stage=='continuation' else stage+'_'",s)
 def test_scheduler_unknown_and_step_filter(self):
  self.assertEqual(normalize('UNKNOWN'),'UNKNOWN');self.assertEqual(normalize('COMPLETED','1:0'),'FAILED');self.assertIsNone(parse_accounting('12.batch|COMPLETED|0:0|3|1|4G|short|00:30:00','12'))
 def test_uncertain_submission_not_retried(self):
  import hpc_control
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'submission_attempt.json').write_text('{}')
   with patch.object(hpc_control,'P',root),patch.object(hpc_control,'verify_manifest'),patch.object(hpc_control.subprocess,'run') as run:
    with self.assertRaises(AssertionError):hpc_control.submit()
    run.assert_not_called()
 def test_runner_freeze_order_and_audit_scope(self):
  t=(P/'runner.py').read_text();self.assertLess(t.index("'make_inputs.py'"),t.index("'prepare_initial.py'"));self.assertLess(t.index("'prepare_initial.py'"),t.index("'prepare_policy.py'"));self.assertLess(t.index("'prepare_policy.py'"),t.index("'transfer.py'"));self.assertIn("if b==0:validate",(P/'validate_analyze.py').read_text());self.assertIn("stage('audit_independent.py'",t)
if __name__=='__main__':unittest.main(verbosity=2)
