"""Deterministic constructed fixtures only; never draws production seed tapes."""
import unittest,copy,ast,itertools,time
from common import *
from model import stage,substitute,revert_to_H
from analysis import *
from seed_design import roster,verify_roster
from raw_audit import audit_record,canon
from audit_independent import recompute
from accepted_inputs055 import extend_targets
from prepare_design import source_check
CALLS=dict(constructed_paths=0,constructed_trajectory_calls=0)

def fixture():
 pop=[(i*12345,1,i,(i*76543,39,i)) for i in range(32)]
 draws=dict(labels=list(range(32)),local=[[1<<((i+g)%32) for i in range(32)] for g in range(40)],scout=[[((i+1)*1234567+g)%2**32 for i in range(32)] for g in range(40)],ties=[[(i+1)/129 for i in range(128)] for _ in range(40)])
 targets=[0,0x01234567]*20;fresh=[[(i*54321+g+1)%2**32 for i in range(32)] for g in range(40)]
 ks=[2**52-1]*32+[0]*96;survival=[dict(k=ks,u=[(k+1)/(2**52+1) for k in ks]) for _ in range(40)]
 return pop,draws,targets,fresh,survival
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pop,cls.draws,cls.targets,cls.fresh,cls.survival=fixture();cls.records={}
  for cfg in CONFIGS:
   arm='STAY' if cfg=='STAY' else cfg[:-1];slot=None if cfg=='STAY' else int(cfg[-1]);initial=substitute(cls.pop,slot)
   cls.records[cfg]=stage(cls.targets,cls.draws,initial,cls.fresh,cls.survival,arm,0xfedcba98);CALLS['constructed_paths']+=1;CALLS['constructed_trajectory_calls']+=5152
 def test_reversion_only_labels_and_noop(self):
  p=substitute(self.pop,3);q=revert_to_H(p)
  self.assertEqual(q,self.pop);self.assertEqual(revert_to_H(self.pop),self.pop);self.assertEqual(p[3][1],2)
  for a,b in zip(p,q):self.assertEqual((a[0],a[2],a[3]),(b[0],b[2],b[3]));self.assertIs(a[3],b[3])
 def test_first_update_identity_boundary(self):
  for i in (0,1):
   p,c=self.records['PULSE'+str(i)],self.records['CONT'+str(i)]
   self.assertEqual(p['initial_queries'],c['initial_queries']);self.assertEqual(p['populations'][0],c['populations'][0]);self.assertEqual(p['steps'][0],c['steps'][0])
   self.assertEqual(len(p['reversion_events']),1);event=p['reversion_events'][0];self.assertEqual((event['after_update'],event['before_update'],event['absolute_completed']),(1,2,41))
   self.assertEqual(event['pre_reversion_population'],p['steps'][0]['selected_records']);self.assertEqual(event['post_reversion_population'],p['populations'][1]);self.assertEqual(event['post_reversion_population'],p['steps'][1]['candidates'][:32])
   for g,pop in enumerate(p['populations'][1:]):self.assertTrue(all(x[1]==1 for x in pop));self.assertEqual(p['steps'][g]['fresh_probe_masks'],self.fresh[g])
   self.assertEqual(c['reversion_events'],[])
 def test_founders_are_not_expression(self):
  p=self.records['PULSE0'];f=lineage_series(p,[0,1])['0'];self.assertGreater(f[1],0);self.assertEqual(p['expression_selected']['F'][1],f[1]);self.assertEqual(p['expression_carried']['F'][1],0);self.assertGreater(f[40],0)
  self.assertEqual(p['intervention_frequency_terms'][0]['F'],-f[1]);self.assertEqual(p['expression_carried']['F'][2:],[0]*39)
  for g in range(40):
   for k in ('H','F','R'):self.assertEqual(p['expression_carried'][k][g+1]-p['expression_carried'][k][g],p['steps'][g]['type_frequency_terms'][k]+p['intervention_frequency_terms'][g][k])
 def test_recorded_score_and_transition_audit(self):
  for cfg,rec in self.records.items():
   initial=substitute(self.pop,None if cfg=='STAY' else int(cfg[-1]));answer=audit_record(rec,self.targets,self.draws,initial,self.fresh,self.survival,0xfedcba98)
   self.assertEqual(answer,dict(paths=1,recorded_scores=5152,race_keys=5120,updates=40));self.assertLess(len(json.dumps(dict(record=rec),separators=(',',':')).encode()),2**21)
 def test_audit_rejects_wrong_reversion(self):
  rec=copy.deepcopy(self.records['PULSE0']);rec['populations'][1][0]=(rec['populations'][1][0][0]^1,)+rec['populations'][1][0][1:]
  with self.assertRaises(AssertionError):audit_record(rec,self.targets,self.draws,substitute(self.pop,0),self.fresh,self.survival,0xfedcba98)
 def test_metric_windows_and_units(self):
  a=[i/40 for i in range(41)];f=[1/32]*41;v=endpoints(a,f)
  self.assertEqual(v['U1'],1/40);self.assertEqual(v['U_LATE'],sum(a[2:])/39);self.assertEqual(v['U_ALL'],sum(a[1:])/40);self.assertEqual(v['U40'],1);self.assertEqual(v['D1'],0);self.assertEqual(v['D40'],0)
  self.assertEqual(DELTA*1024,1);self.assertEqual(DELTA*100,.09765625);self.assertEqual(32*(1/32),1)
 def test_all36_and_structural_identities(self):
  ps={k:dict(accuracy=rec['raw_accuracies'],founder=lineage_series(rec,[0,1])) for k,rec in self.records.items()};out=summarize(ps);self.assertEqual(len(out),36)
  for k in STRUCTURAL_ZEROS:self.assertEqual(out[k],0)
  self.assertEqual(out['STAY|U40'],ps['STAY']['accuracy'][-1]);self.assertEqual(set(out),set(read('METRIC_CATALOG.json')['keys']))
 def test_independent_36_estimates(self):
  # Algebraic synthetic time series, not simulated outcomes or production RNG.
  panel={};paired={};idx=[[(i*i+i*(j%5)+j)%24 for i in range(24)] for j in range(2000)]
  for b in range(24):
   for r in range(8):
    ps={}
    for cfg in CONFIGS:
     effect=0 if cfg=='STAY' else 1 if cfg.startswith('PULSE') else 2;placement=0 if cfg=='STAY' else int(cfg[-1]);scale=(b+1)*(r+1)/100000
     a=[.5]+[.5+scale*((1 if t==1 and effect else effect)*(t+placement)) for t in range(1,41)]
     fs={str(i):[1/32]+[1/32+scale*((1 if t==1 and effect else effect)*(t+i)) for t in range(1,41)] for i in (0,1)}
     s=dict(accuracy=a,founder=fs);ps[cfg]=s;panel[b,r,cfg]=s
    paired[b,r]=summarize(ps)
  got=recompute(panel,idx)
  for k in KEYS:
   bs=[sum(paired[b,r][k] for r in range(8))/8 for b in range(24)];mean,ci=interval(bs,idx);self.assertAlmostEqual(mean,got[k]['mean'],places=13)
   for a,z in zip(ci,got[k]['ci95']):self.assertAlmostEqual(a,z,places=13)
 def test_sign_benchmark_and_ties(self):
  for ci,want in [([.0001,.0002],'supports_positive'),([-.002,-.001],'contradicts_positive'),([0,.001],'unresolved'),([0,0],'unresolved')]:self.assertEqual(decisions(ci)['direction'],want)
  for ci,want in [([.002,.003],'above_one_matching_bit'),([0,.0005],'below_one_matching_bit'),([DELTA,.002],'overlaps_one_matching_bit'),([0,DELTA],'overlaps_one_matching_bit')]:self.assertEqual(decisions(ci)['benchmark'],want)
 def test_seed_roster_and_indexed_coupling(self):
  self.assertTrue(verify_roster(roster(),read('PRIOR_SEED_INVENTORY.json')['integers']));self.assertEqual(len(roster()),1201)
  self.assertTrue(all('PULSE' not in q['family'] and 'CONT' not in q['family'] for q in roster()))
  for name in ('model.py','transfer.py'):self.assertNotIn('random.',(P/name).read_text())
  for g,s in enumerate(self.records['PULSE0']['steps']):self.assertEqual(s['survival_integers'],self.survival[g]['k']);self.assertEqual(s['ties'],self.draws['ties'][g])
 def test_target_boundary_and_counts(self):
  h=[1,2]*20;innov=list(range(100,140));bits=[1,0]*20;t=extend_targets(h,innov,bits,'HALF');self.assertEqual(t[:4],[1,101,1,103])
  cfg=read('config.json');self.assertEqual(cfg['new_paths'],24*8*5);self.assertEqual(960*5152,cfg['new_objective_calls']);self.assertEqual(cfg['post_pulse_updates'],39)
  self.assertEqual(cfg['resources'],dict(cpus=1,memory_GiB=4,minutes=15,partition='norm'))
 def test_source_authentication_and_preserved_operators(self):
  self.assertEqual(source_check()['selected'],192);self.assertEqual(verify_references(),11)
 def test_python36_syntax(self):
  for f in P.glob('*.py'):ast.parse(f.read_text(),filename=f.name,feature_version=(3,6))
if __name__=='__main__':
 start=time.time();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests))
 save('TEST_STATUS.json',dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_seconds=time.time()-start,fixture_accounting=CALLS,scientific_paths=0,production_seed_draws=0))
 raise SystemExit(0 if result.wasSuccessful() else 1)
