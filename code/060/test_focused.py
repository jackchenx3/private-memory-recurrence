"""Constructed correctness fixtures only; no production seed draws or previews."""
import unittest,copy,ast,math,time
from common import *
from model import Evaluator,Policy,step,stage,substitute,race_select_real
from accepted_stage057 import stage as accepted_stage
from accepted_survival_model import race_select,to_uniform
from analysis import *
from seed_design import roster,verify_roster
from raw_audit import audit_record,canon
from audit_independent import recompute
from accepted_inputs055 import extend_targets
from prepare_design import source_check
CALLS=dict(constructed_paths=0,trajectory_calls=0,isolated_query_calls=0)

def fixture():
 pop=[(i*12345,2,i,(i*76543,39,i)) for i in range(32)];d=dict(labels=list(range(32)),local=[[1<<((i+g)%32) for i in range(32)] for g in range(40)],scout=[[((i+1)*1234567+g)%2**32 for i in range(32)] for g in range(40)],ties=[[(i+1)/129 for i in range(128)] for _ in range(40)])
 targets=[0,0x01234567]*20;fresh=[[(i*54321+g+1)%2**32 for i in range(32)] for g in range(40)];ks=[(i+1)*2**44 for i in range(128)];survival=[dict(k=ks,u=[to_uniform(k) for k in ks]) for _ in range(40)];noise=dict(initial=[(i+.5)/32 for i in range(32)],updates=[[((i+g)%16+.5)/16 for i in range(128)] for g in range(40)])
 return pop,d,targets,fresh,survival,noise
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.pop,cls.d,cls.targets,cls.fresh,cls.survival,cls.noise=fixture();cls.initial=substitute(cls.pop,'F',0);cls.zero=dict(initial=[.5]*32,updates=[[.5]*128 for _ in range(40)]);cls.records={}
  for name,interface,noise in [('EXACT','EXACT',cls.noise),('ZERO_ERROR','NOISY',cls.zero),('NOISY','NOISY',cls.noise)]:
   cls.records[name]=stage(cls.targets,cls.d,cls.initial,cls.fresh,cls.survival,noise,interface,0xfedcba98);CALLS['constructed_paths']+=1;CALLS['trajectory_calls']+=5152
  cls.accepted=accepted_stage(cls.targets,cls.d,cls.initial,0,[[0]*32 for _ in range(40)]+cls.fresh,cls.survival,40,0xfedcba98);CALLS['constructed_paths']+=1;CALLS['trajectory_calls']+=5152
 def test_zero_error_full_correspondence(self):
  old=self.accepted
  for name in ('EXACT','ZERO_ERROR'):
   rec=self.records[name];self.assertEqual(rec['populations'],old['populations']);self.assertEqual(rec['true_losses'],old['raw_losses']);self.assertEqual(rec['true_accuracies'],old['raw_accuracies']);self.assertEqual(rec['frequencies'],old['frequencies'])
   for s,o in zip(rec['steps'],old['steps']):
    for k in ('selected_indices','selected_records','candidates','race_keys','current_descendant_counts','type_frequency_terms'):self.assertEqual(s[k],o[k])
    donors=copy.deepcopy(o['donor_choices'])
    for donor in donors:donor['observed_scores']=donor.pop('raw_mismatches')
    self.assertEqual(s['donor_choices'],donors)
    for k in ('B','L','S','W'):self.assertEqual(s[k+'_true'],o[k+'_raw'])
 def test_real_race_integer_and_fractional(self):
  scores=[i%34 for i in range(128)];ss=self.survival[0];ties=self.d['ties'][0]
  self.assertEqual(race_select_real(scores,ties,ss['k'],ss['u']),race_select(scores,ties,ss['k'],ss['u']))
  frac=[-1+(i%34)+.125 if i%34<33 else 32.875 for i in range(128)];ids,keys=race_select_real(frac,ties,ss['k'],ss['u']);self.assertEqual(ids,sorted(range(128),key=lambda j:(-math.log(ss['u'][j])*2.**frac[j],ties[j],j))[:32])
 def test_unclipped_query_duplicates_and_indexing(self):
  noise=copy.deepcopy(self.zero);noise['initial'][:3]=[0,.99,.25];ev=Evaluator('NOISY',noise);ev.target=0
  self.assertEqual(ev.score((0,2,0,(0,0,0)),0),-1);self.assertGreater(ev.score((2**32-1,2,1,(0,0,1)),1),32);self.assertEqual(ev.score((0,2,2,(0,0,2)),2),-.5);CALLS['isolated_query_calls']+=3
  self.assertEqual([q['query_ordinal'] for q in ev.records],[0,1,2]);self.assertNotEqual(ev.records[0]['observed_score'],ev.records[2]['observed_score']);self.assertEqual(ev.calls,3)
  for rec in self.records.values():
   q=rec['initial_queries']+[q for s in rec['steps'] for q in s['query_records']];self.assertEqual([x['query_ordinal'] for x in q],list(range(5152)));self.assertEqual(len(q),rec['query_counts']['total'])
 def test_no_clean_donor_or_survival_leak(self):
  pop=[(0,1 if i==0 else 2,i,(1,39,i)) for i in range(32)];noise=copy.deepcopy(self.zero);noise['updates'][0][0]=.99;noise['updates'][0][32]=0
  outcomes=[]
  class AlteredDiagnostics(Evaluator):
   def score(self,p,i):
    returned=super().score(p,i);self.records[-1]['true_loss']=32-self.records[-1]['true_loss'];return returned
  for cls in (Evaluator,AlteredDiagnostics):
   ev=cls('NOISY',noise);ev.target=0
   for i,p in enumerate(pop):ev.score(p,i)
   ev.begin();engine=Policy(0,pop,[[0]*32 for _ in range(80)]);engine.completed=40;s=step(engine,ev,[0]*32,[0]*32,self.d['ties'][0],self.survival[0]);CALLS['isolated_query_calls']+=ev.calls;outcomes.append(s)
  a,b=outcomes;self.assertEqual(a['donor_choices'][0]['winner_index'],32);self.assertEqual(a['candidate_true_losses'][0],0);self.assertEqual(a['candidate_true_losses'][32],1)
  self.assertEqual(a['selected_indices'],b['selected_indices']);self.assertEqual(a['selected_records'],b['selected_records']);self.assertNotEqual(a['candidate_true_losses'],b['candidate_true_losses']);self.assertEqual(a['candidate_observed_scores'],[q['observed_score'] for q in a['query_records']]);self.assertNotIn('raw_mismatches',a['donor_choices'][0])
 def test_initial_observations_not_used_later(self):
  noise=copy.deepcopy(self.noise);noise['initial']=[0]*32;rec=stage(self.targets,self.d,self.initial,self.fresh,self.survival,noise,'NOISY',0xfedcba98);CALLS['constructed_paths']+=1;CALLS['trajectory_calls']+=5152
  self.assertNotEqual(rec['initial_observed_scores'],self.records['NOISY']['initial_observed_scores']);self.assertEqual(rec['steps'],self.records['NOISY']['steps']);self.assertEqual(rec['populations'],self.records['NOISY']['populations'])
 def test_source_policy_cache_and_absolute_index(self):
  self.assertEqual(source_check()['selected'],192);self.assertEqual(verify_references(),12)
  q=substitute(self.pop,'F',3)
  for i,(a,b) in enumerate(zip(self.pop,q)):self.assertEqual((a[0],a[2],a[3]),(b[0],b[2],b[3]));self.assertEqual(b[1],1 if i==3 else 2)
  for g,s in enumerate(self.records['NOISY']['steps']):
   self.assertEqual(s['fresh_probe_masks'],self.fresh[g])
   for j,p in enumerate(s['candidates'][32:]):self.assertEqual(p[3],(self.records['NOISY']['populations'][g][j%32][0],40+g,j%32))
 def test_independent_raw_audit_and_declines(self):
  for name,rec in self.records.items():
   answer=audit_record(rec,self.targets,self.d,self.initial,self.fresh,self.survival,self.zero if name=='ZERO_ERROR' else self.noise,0xfedcba98);self.assertEqual(answer['queries'],5152)
   self.assertLess(len(json.dumps(dict(record=rec),separators=(',',':')).encode()),4*1024*1024)
   self.assertTrue(any(rec['true_losses'][g+1]>rec['true_losses'][g] for g in range(40)))
  corrupt=copy.deepcopy(self.records['NOISY']);corrupt['steps'][0]['query_records'][0]['observed_score']+=.1
  with self.assertRaises(AssertionError):audit_record(corrupt,self.targets,self.d,self.initial,self.fresh,self.survival,self.noise,0xfedcba98)
 def test_seed_count_pairing_targets_and_budget(self):
  self.assertTrue(verify_roster(roster(),read('PRIOR_SEED_INVENTORY.json')['integers']));self.assertEqual(len(roster()),1393)
  h=[1,2]*20;innov=list(range(100,140));bits=[1,0]*20;self.assertEqual(extend_targets(h,innov,bits,'ZERO'),innov);self.assertEqual(extend_targets(h,innov,bits,'HALF')[:4],[1,101,1,103])
  cfg=read('config.json');self.assertEqual(192*2*2*3,cfg['new_paths']);self.assertEqual(2304*5152,cfg['new_objective_calls']);self.assertEqual(192*5152,cfg['new_noise_uniforms']);self.assertEqual(cfg['candidate_queries'],2304*40*128)
  for n in ('model.py','transfer.py'):self.assertNotIn('random.',(P/n).read_text())
 def test_sign_scale_and_units(self):
  for ci,want in [([-.1,-.01],'supports_negative'),([.01,.1],'contradicts_negative'),([0,.1],'unresolved'),([-.1,0],'unresolved')]:self.assertEqual(decisions(ci)['direction'],want)
  self.assertEqual(decisions([-.02,.02])['minus_one_descendant'],'above');self.assertEqual(decisions([-.02,.02])['plus_one_descendant'],'below');self.assertEqual(decisions([-DELTA,DELTA])['minus_one_descendant'],'overlaps');self.assertEqual(positive_scale([0,DELTA]),'overlaps_plus_one_descendant');self.assertEqual(positive_scale([0,.01]),'below_plus_one_descendant');self.assertEqual(positive_scale([.04,.1]),'above_plus_one_descendant');self.assertEqual(32*DELTA,1);self.assertEqual(1024*(1/1024),1)
 def test_independent81_estimates(self):
  panel={};paired={};idx=[[(i*i+i*(j%5)+j)%24 for i in range(24)] for j in range(2000)]
  for b in range(24):
   for r in range(8):
    cells={}
    for ci,cell in enumerate(CELLS):
     paths={}
     for cfg in CONFIGS:
      factor=1 if cfg=='STAY' else 2+int(cfg[-1]);scale=(ci+1)**2*(b+1)*(r+1)/1000000
      s=dict(accuracy=[.5+factor*scale*t for t in range(41)],founder={str(i):[1/32+factor*scale*t*(i+1) for t in range(41)] for i in (0,1)})
      paths[cfg]=s;panel[b,r,cell,cfg]=s
     cells[cell]=base(paths)
    paired[b,r]=combine(cells)
  got=recompute(panel,idx);self.assertEqual(len(got),81);self.assertEqual(set(got),set(KEYS));self.assertEqual(set(KEYS),set(read('METRIC_CATALOG.json')['keys']))
  for k in KEYS:
   mean,ci=interval([sum(paired[b,r][k] for r in range(8))/8 for b in range(24)],idx);self.assertAlmostEqual(mean,got[k]['mean'],places=13)
   for a,z in zip(ci,got[k]['ci95']):self.assertAlmostEqual(a,z,places=13)
  for v in paired.values():self.assertAlmostEqual(v[PRIMARY],v['NOISY_Q_HALF_MINUS_ZERO|EFFECT|D40']-v['EXACT_Q_HALF_MINUS_ZERO|EFFECT|D40'])
 def test_python36_syntax(self):
  for f in P.glob('*.py'):ast.parse(f.read_text(),filename=f.name,feature_version=(3,6))
if __name__=='__main__':
 start=time.time();result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));save('TEST_STATUS.json',dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_seconds=time.time()-start,fixture_accounting=CALLS,scientific_paths=0,production_seed_draws=0));raise SystemExit(0 if result.wasSuccessful() else 1)
