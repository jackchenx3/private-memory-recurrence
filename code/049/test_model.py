import unittest,os,pathlib,json,collections,hashlib
from model import initial,sequence,Evaluator,step,Policy
import accepted_model as old
from analysis import MODES,LAWS,MET,derive,structural
from signatures import prefix,first
from make_inputs import verify_inherited,seed,roster,draws,build_targets
from io_utils import save,sha
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  assert os.environ.get('SLURM_JOB_ID');cls.calls=cls.sequences=cls.single_steps=0;cls.fresh=[[i*5 for i in range(32)]]*40;cls.labels=list(range(7,32))+list(range(7));cls.draws=dict(labels=cls.labels,local=[[1<<i for i in range(32)]]*40,scout=[[0 if i%2 else 0xffffffff for i in range(32)]]*40,ties=[[j/128 for j in range(128)]]*40)
 @classmethod
 def tearDownClass(cls):save('FIXTURE_WORK.json',dict(objective_calls=cls.calls,completed_toy_sequences=cls.sequences,completed_toy_single_steps=cls.single_steps,scientific_paths=0,random_draws=0))
 def seq(self,t,m):
  r=sequence(t,self.draws,m,self.fresh,[i*17 for i in range(32)]);Tests.calls+=5152;Tests.sequences+=1;return r
 def once(self,pop,mode,target,fresh=False,ties=None):
  e=Policy(mode,pop,self.fresh) if fresh else old.Policy(mode,pop);ev=Evaluator();ev.target=target;ev.begin();s=step(e,ev,[0]*32,[0]*32,ties or [j/128 for j in range(128)]);Tests.calls+=ev.calls;Tests.single_steps+=1;return s
 def test_own_parity_after_refresh(self):
  q=build_targets([1,2],[3,4]+[99]*36,[0,0]+[1]*36,'HALF');self.assertEqual(q[:8],[1,2,3,4,3,4,3,4]);self.assertEqual(q[2:],[3,4]*19)
 def test_q_endpoints(self):
  pair=[3,7];zs=list(range(38));self.assertEqual(build_targets(pair,zs,[0]*38,'HALF'),build_targets(pair,zs,[1]*38,'ZERO'));self.assertEqual(build_targets(pair,zs,[1]*38,'HALF'),build_targets(pair,zs,[0]*38,'FULL'));self.assertEqual(build_targets(pair,zs,[0]*38,'FULL'),pair*20)
 def test_equal_refresh_is_retained(self):
  zs=[3,7]*19
  for g in LAWS:self.assertEqual(build_targets([3,7],zs,[0]*38,g),[3,7]*20)
  self.assertEqual(build_targets([9,9],[9]*38,[0]*38,'ZERO'),[9]*40)
 def test_seed_and_draw_order(self):
  self.assertEqual(seed('copy',3),int(hashlib.sha256(b'ORG-INTERMIT-049-r1|copy|3').hexdigest()[:16],16));rs=roster();self.assertEqual(len(rs),48);self.assertEqual(len({q['seed'] for q in rs}),48)
  class Fake:
   def __init__(self):self.calls=[]
   def getrandbits(self,b):self.calls.append(b);return (len(self.calls)-1)%(2**b)
  for bits in (1,32):
   f=Fake();v=draws(f,bits);self.assertEqual(f.calls,[bits]*38);self.assertEqual(v,[i%(2**bits) for i in range(38)])
 def test_policy_has_no_law_or_copy_inputs(self):
  import inspect,ast
  self.assertEqual(list(inspect.signature(sequence).parameters),['targets','draws','mode','fresh','genotypes']);self.assertEqual(list(inspect.signature(Policy).parameters),['mode','pop','fresh']);self.assertEqual(list(inspect.signature(old.Policy).parameters),['mode','pop'])
  for name in ('model.py','accepted_model.py','accepted_fresh_model.py'):
   tree=ast.parse(pathlib.Path(name).read_text());self.assertFalse(any(isinstance(n,ast.Name) and n.id in ('law','copy_bits') for n in ast.walk(tree)))
 def test_all_modes_two_update_prefix(self):
  for mode in MODES:
   full=self.seq([3,7]*20,mode)
   for g in ('ZERO','HALF'):
    t=build_targets([3,7],list(range(38)),[i%2 for i in range(38)],g);new=self.seq(t,mode);self.assertEqual(prefix(new),prefix(full))
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
 def test_negative_raw_and_pen_valid(self):
  pop=[(0,1,i,(0,0,i)) if i<16 else (1,0,i,None) for i in range(32)];s=self.once(pop,'SHAM_C1',0,ties=[1 if j%32<16 else 0 for j in range(128)]);self.assertLess(s['S_raw'],0);self.assertGreaterEqual(s['S_pen'],0)
  s=self.once([(0xffffffff,1,i,(0xffffffff,0,i)) for i in range(32)],'SHAM_C1',0);self.assertLess(1-s['L_pen'],0)
 def test_grid_1248_96(self):
  v={'RESIDENT40|'+g+'|'+p+'|'+m:0. for g in LAWS for p in MODES for m in MET};derive(v);self.assertEqual(len(v),1248);keys={k for k in v if structural(k)};self.assertEqual(len(keys),96);self.assertEqual(sum('|FULL|' in k for k in v),312);expected=set()
  for g in LAWS:
   for a,b in [('ACTIVE','NOVEL'),('ACTIVE','SHAM'),('NOVEL','SHAM')]:
    for c in (0,1):
     for m in (('U0','F0','U1','F1') if (a,b)==('ACTIVE','SHAM') else ('U0','F0')):expected.add('RESIDENT40|'+g+'|'+a+'_C'+str(c)+'-'+b+'_C'+str(c)+'|'+m)
  for g in ('HALF_MINUS_ZERO','FULL_MINUS_HALF','FULL_MINUS_ZERO'):
   for b in ('NOVEL','SHAM'):
    for c in (0,1):
     for m in ('U0','U1','F0','F1'):expected.add('RESIDENT40|'+g+'|ACTIVE_C'+str(c)+'-'+b+'_C'+str(c)+'|'+m)
  self.assertEqual(keys,expected)
 def test_primary_separate_from_incremental_and_spread(self):
  from assess_primary import assess
  ks=['RESIDENT40|HALF|ACTIVE_C0-NOVEL_C0|D40','RESIDENT40|HALF_MINUS_ZERO|ACTIVE_C0-NOVEL_C0|D40','RESIDENT40|HALF|ACTIVE_C0|D40','RESIDENT40|HALF|ACTIVE_C0-SHAM_C0|D40'];v={k:dict(zero_classification='unresolved') for k in ks};v[ks[0]]['zero_classification']='positive';q=assess(v);self.assertTrue(q['expectation_supported']);self.assertFalse(q['incremental_attribution_supported']);self.assertFalse(q['retrieval_attributed_mean_increase']);v[ks[2]]['zero_classification']='positive';self.assertFalse(assess(v)['retrieval_attributed_mean_increase']);v[ks[3]]['zero_classification']='positive';self.assertTrue(assess(v)['retrieval_attributed_mean_increase'])
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
