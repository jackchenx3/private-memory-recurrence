import unittest,os,pathlib,json,collections,hashlib
from model import initial,sequence,Evaluator,step,Policy,to_uniform,race_select
import accepted_model as old
from analysis import MODES,LAWS,STARTS,MET,derive,structural
from signatures import prefix,first
from make_inputs import verify_inherited,seed,roster,draws
from io_utils import save,sha
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  assert os.environ.get('SLURM_JOB_ID');cls.calls=cls.sequences=cls.single_steps=0;cls.survival=[dict(k=[(j+1)*123456789 for j in range(128)],u=[to_uniform((j+1)*123456789) for j in range(128)]) for _ in range(40)];cls.fresh=[[i*5 for i in range(32)]]*40;cls.labels=list(range(7,32))+list(range(7));cls.draws=dict(labels=cls.labels,local=[[1<<i for i in range(32)]]*40,scout=[[0 if i%2 else 0xffffffff for i in range(32)]]*40,ties=[[j/128 for j in range(128)]]*40)
 @classmethod
 def tearDownClass(cls):save('FIXTURE_WORK.json',dict(objective_calls=cls.calls,completed_toy_sequences=cls.sequences,completed_toy_single_steps=cls.single_steps,scientific_paths=0,random_draws=0))
 def seq(self,t,m):
  r=sequence(t,self.draws,m,self.fresh,[i*17 for i in range(32)],self.survival);Tests.calls+=5152;Tests.sequences+=1;return r
 def once(self,pop,mode,target,fresh=False,ties=None,survival=None,scout=None):
  e=Policy(mode,pop,self.fresh) if fresh else old.Policy(mode,pop);ev=Evaluator();ev.target=target;ev.begin();s=step(e,ev,[0]*32,scout or [0]*32,ties or [j/128 for j in range(128)],survival or self.survival[0]);Tests.calls+=ev.calls;Tests.single_steps+=1;return s
 def test_uniform_endpoints(self):
  self.assertGreater(to_uniform(0),0);self.assertLess(to_uniform(2**52-1),1)
  for k in (-1,2**52):
   with self.assertRaises(AssertionError):to_uniform(k)
 def test_selector_order_distinct_equal_weights(self):
  ks=[(j+1)*12345 for j in range(128)];us=list(map(to_uniform,ks));selected,keys=race_select([3]*128,[0]*128,ks,us);self.assertEqual(selected,list(range(127,95,-1)));self.assertEqual(len(set(selected)),32)
  selected,_=race_select([3]*128,[0]*128,[5]*128,[to_uniform(5)]*128);self.assertEqual(selected,list(range(32)))
 def test_lower_score_can_lose(self):
  ks=[0]+[2**52-1]*127;scores=[0]+[32]*127;selected,keys=race_select(scores,[0]*128,ks,list(map(to_uniform,ks)));self.assertNotIn(0,selected);self.assertEqual(selected,list(range(1,33)));self.assertGreater(keys[0],keys[1])
 def test_common_shift_and_cost_keys(self):
  ks=self.survival[0]['k'];us=self.survival[0]['u'];scores=[j%30 for j in range(128)];ties=[0]*128;a,k=race_select(scores,ties,ks,us);b,k2=race_select([s+3 for s in scores],ties,ks,us);self.assertEqual(a,b);self.assertEqual(k2,[v*8 for v in k]);scores[7]+=1;_,kc=race_select(scores,ties,ks,us);self.assertEqual(kc[7],2*k[7]);self.assertEqual(kc[:7],k[:7]);self.assertEqual(kc[8:],k[8:])
 def test_seed_and_draw_order(self):
  self.assertEqual(seed(3,2),int(hashlib.sha256(b'ORG-SURVIVAL-050-r1|survival|3|2').hexdigest()[:16],16));rs=roster();self.assertEqual(len(rs),192);self.assertEqual(len({q['seed'] for q in rs}),192)
  class Fake:
   def __init__(self):self.calls=[]
   def getrandbits(self,b):self.calls.append(b);return len(self.calls)-1
  f=Fake();v=draws(f);self.assertEqual(f.calls,[52]*5120);self.assertEqual([k for row in v for k in row['k']],list(range(5120)));self.assertEqual(v[-1]['u'][-1],to_uniform(5119))
 def test_all_modes_two_update_prefix(self):
  for mode in MODES:
   full=self.seq([3,7]*20,mode)
   for g in ('ZERO','HALF'):
    t=[3,7]+(list(range(38)) if g=='ZERO' else [9,5]*19);new=self.seq(t,mode);self.assertEqual(prefix(new),prefix(full))
    for j,s in enumerate(new['steps']):
     self.assertEqual(s['frequency_term'],new['frequencies'][j+1]-new['frequencies'][j]);self.assertEqual(s['S_pen'],s['S_raw']+int(mode.endswith('C1'))*(s['f_before']-s['f_after'])/32)
     for suffix,ls in [('raw',new['raw_losses']),('pen',new['penalized_losses'])]:self.assertEqual(ls[j+1]-ls[j],s['W_'+suffix]-s['S_'+suffix])
 def test_active_sham_first(self):
  for cost in (0,1):self.assertEqual(first(self.seq([3,7]*20,'ACTIVE_C'+str(cost))),first(self.seq([3,7]*20,'SHAM_C'+str(cost))))
 def test_founder_cache_and_recipient_inheritance(self):
  xs=[i*17 for i in range(32)];pop=initial('ACTIVE_C0',self.labels,xs);self.assertEqual(pop[7],(xs[7],1,7,(xs[7],0,7)));self.assertEqual([q[2] for q in pop],list(range(32)));pop[7]=(3,1,7,(9,2,5));s=self.once(pop,'ACTIVE_C0',15)
  for j,q in enumerate(s['candidates']):
   self.assertEqual(q[1:3],pop[j%32][1:3]);self.assertEqual(q[3],pop[j][3] if j<32 else ((pop[j%32][0],0,j%32) if pop[j%32][1] else None))
 def test_duplicates_and_donor_ties(self):
  pop=initial('SHAM_C0',self.labels,[0]*32);s=self.once(pop,'SHAM_C0',15);self.assertEqual(s['evaluator_calls'],128);self.assertEqual([q['candidate_index'] for q in s['query_records']],list(range(128)));self.assertTrue(all(q[0]==0 for q in s['candidates']))
  for i,d in enumerate(s['donor_choices']):self.assertEqual(d['winner_index'],min((i,i+32,i+64),key=lambda j:(s['candidate_raw_mismatches'][j],s['ties'][j],j)))
 def test_negative_selection_and_pen_accuracy_valid(self):
  ks=[0]*128
  for j in range(64,96):ks[j]=2**52-1
  survival=dict(k=ks,u=list(map(to_uniform,ks)));pop=initial('SHAM_C0',self.labels,[0]*32);s=self.once(pop,'SHAM_C0',0,survival=survival,scout=[0xffffffff]*32);self.assertEqual(s['selected_indices'],list(range(64,96)));self.assertEqual(s['S_raw'],-1);self.assertEqual(s['S_pen'],-1);self.assertEqual(s['L_raw']-s['B_raw'],-s['S_raw'])
  s=self.once([(0xffffffff,1,i,(0xffffffff,0,i)) for i in range(32)],'SHAM_C1',0);self.assertLess(1-s['L_pen'],0)
 def test_grid_2808_228(self):
  v={a+'|'+g+'|'+p+'|'+m:0. for a in STARTS for g in LAWS for p in MODES for m in MET};derive(v);self.assertEqual(len(v),2808);keys={k for k in v if structural(k)};self.assertEqual(len(keys),228);self.assertEqual(sum(k.startswith('BEST32|') for k in v),1248)
  self.assertFalse(structural('RACE32_MINUS_BEST32|HALF|ACTIVE_C0-NOVEL_C0|U1'));self.assertTrue(structural('RACE32_MINUS_BEST32|HALF|ACTIVE_C0-SHAM_C0|U1'))
 def test_primary_separate_from_incremental_and_spread(self):
  from assess_primary import assess
  ks=['RACE32|HALF|ACTIVE_C0-NOVEL_C0|D40','RACE32|HALF_MINUS_ZERO|ACTIVE_C0-NOVEL_C0|D40','RACE32|HALF|ACTIVE_C0|D40','RACE32|HALF|ACTIVE_C0-SHAM_C0|D40','RACE32_MINUS_BEST32|HALF|ACTIVE_C0-NOVEL_C0|D40'];v={k:dict(zero_classification='unresolved') for k in ks};v[ks[0]]['zero_classification']='positive';q=assess(v);self.assertTrue(q['expectation_supported']);self.assertFalse(q['incremental_attribution_supported']);self.assertFalse(q['retrieval_attributed_mean_increase']);v[ks[2]]['zero_classification']='positive';self.assertFalse(assess(v)['retrieval_attributed_mean_increase']);v[ks[3]]['zero_classification']='positive';self.assertTrue(assess(v)['retrieval_attributed_mean_increase'])
 def test_immutable_sources(self):
  verify_inherited();self.assertFalse(pathlib.Path('INPUT_FREEZE.json').exists())
  for line in pathlib.Path('SOURCE_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);self.assertEqual(sha(n),h)
 def test_monitor_propagation(self):
  import runner
  g=runner.Guard()
  def fail(_):raise RuntimeError('fixture failure')
  runner.monitor(g,fail)
  with self.assertRaises(RuntimeError):g.check()
  pathlib.Path('MONITOR_FAILURE.json').unlink()
if __name__=='__main__':unittest.main(verbosity=2)
