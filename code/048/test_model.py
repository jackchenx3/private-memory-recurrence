import unittest,os,pathlib,json,itertools,math,collections
import accepted_model as old
import accepted_resident_model as resident
from model import initial,sequence,Policy,Evaluator,step,radius_probe
from analysis import MODES,NEW,STARTS,LAWS,MET,derive,structural
from signatures import first
from make_inputs import verify_inherited,seed,roster,permutations
from io_utils import save,sha
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  assert os.environ.get('SLURM_JOB_ID');cls.calls=cls.sequences=cls.single_steps=0;cls.perms=[[list(range(i,32))+list(range(i)) for i in range(32)] for g in range(40)];cls.labels=list(range(7,32))+list(range(7));cls.draws=dict(labels=cls.labels,local=[[1<<i for i in range(32)]]*40,scout=[[0 if i%2 else 0xffffffff for i in range(32)]]*40,ties=[[j/128 for j in range(128)]]*40)
 @classmethod
 def tearDownClass(cls):save('FIXTURE_WORK.json',dict(objective_calls=cls.calls,completed_toy_sequences=cls.sequences,completed_toy_single_steps=cls.single_steps,scientific_paths=0,random_draws=0))
 def once(self,pop,mode,target,original=False,ties=None):
  e=old.Policy(mode,pop) if original else Policy(mode,pop,self.perms);ev=Evaluator();ev.target=target;ev.begin();s=(old.step if original else step)(e,ev,[0]*32,[0]*32,ties or [j/128 for j in range(128)]);Tests.calls+=ev.calls;Tests.single_steps+=1;return s
 def test_radius_extremes_intermediate_nonzero(self):
  x=0xabcdef12;perm=list(reversed(range(32)))
  for c,d in [(x,0),(x^0xffffffff,32),(x^0x15,3)]:
   q=radius_probe((x,1,7,(c,2,3)),perm);self.assertEqual(q['distance'],d);self.assertEqual(q['mask'],sum(1<<i for i in perm[:d]));self.assertEqual(bin(x^q['expressed_genotype']).count('1'),d);self.assertTrue(q['use'])
  for p in [(x,1,7,None),(x,0,7,(0,0,0))]:
   q=radius_probe(p,perm);self.assertFalse(q['use']);self.assertEqual(q['mask'],0)
  with self.assertRaises(AssertionError):radius_probe((x,1,7,(0,0,0)),[0]*32)
 def test_uniform_prefix_counting(self):
  for n in range(1,7):
   for d in range(n+1):
    counts=collections.Counter(tuple(sorted(p[:d])) for p in itertools.permutations(range(n)));self.assertEqual(len(counts),math.factorial(n)//math.factorial(d)//math.factorial(n-d));self.assertEqual(set(counts.values()),{math.factorial(d)*math.factorial(n-d)})
 def test_cache_and_recipient_inheritance(self):
  pop=initial('RADIUS_C0',self.labels,[i*3 for i in range(32)]);pop[7]=(3,1,7,(9,2,5));engine=Policy('RADIUS_C0',pop,self.perms);engine.completed=6;q=engine.probes()[7];self.assertEqual(q[1:],(1,7,(3,6,7)));self.assertEqual(engine.pop[7],pop[7]);s=self.once(pop,'RADIUS_C0',15)
  for j,q in enumerate(s['candidates']):
   self.assertEqual(q[1:3],pop[j%32][1:3]);self.assertEqual(q[3],pop[j][3] if j<32 else ((pop[j%32][0],0,j%32) if pop[j%32][1] else None))
 def test_duplicate_charge_and_donor_rules(self):
  pop=initial('RADIUS_C0',self.labels,[0]*32);s=self.once(pop,'RADIUS_C0',15);self.assertEqual(s['evaluator_calls'],128);self.assertEqual(len(s['query_records']),128);self.assertEqual([q['candidate_index'] for q in s['query_records']],list(range(128)));self.assertTrue(all(q[0]==0 for q in s['candidates']))
  for i,d in enumerate(s['donor_choices']):self.assertEqual(d['winner_index'],min((i,i+32,i+64),key=lambda j:(s['candidate_raw_mismatches'][j],s['ties'][j],j)))
 def test_founder_reset_nonzero_cache(self):
  xs=[i*17 for i in range(32)]
  for i in range(32):
   labels=list(range(i,32))+list(range(i));pop=initial('RADIUS_C1',labels,xs);self.assertEqual([q[0] for q in pop],xs);self.assertEqual([q[2] for q in pop],list(range(32)));self.assertEqual(pop[i],(xs[i],1,i,(xs[i],0,i)));self.assertEqual(sum(q[1] for q in pop),1)
 def test_all_noncarrier_same_state(self):
  pop=[(i*9,0,i,None) for i in range(32)];s=self.once(pop,'RADIUS_C1',15);t=self.once(pop,'ACTIVE_C1',15,original=True);s.pop('radius_probe');self.assertEqual(s,t)
 def test_first_update_and_full_accounting(self):
  for cost in (0,1):
   rec=sequence([3,7]*20,self.draws,'RADIUS_C'+str(cost),self.perms,[i*17 for i in range(32)]);Tests.calls+=5152;Tests.sequences+=1
   for mode in ('ACTIVE','SHAM'):
    ref=resident.sequence([3,7]*20,self.draws,mode+'_C'+str(cost),[[0]*32]*40,[i*17 for i in range(32)]);Tests.calls+=5152;Tests.sequences+=1;self.assertEqual(first(rec),first(ref))
   for j,s in enumerate(rec['steps']):
    self.assertEqual(s['frequency_term'],rec['frequencies'][j+1]-rec['frequencies'][j]);self.assertEqual(s['S_pen'],s['S_raw']+cost*(s['f_before']-s['f_after'])/32)
    for suffix,ls in [('raw',rec['raw_losses']),('pen',rec['penalized_losses'])]:self.assertEqual(ls[j+1]-ls[j],s['W_'+suffix]-s['S_'+suffix])
 def test_negative_valid(self):
  pop=[(0,1,i,(0,0,i)) if i<16 else (1,0,i,None) for i in range(32)];s=self.once(pop,'RADIUS_C1',0,ties=[1 if j%32<16 else 0 for j in range(128)]);self.assertLess(s['S_raw'],0);self.assertGreaterEqual(s['S_pen'],0)
  s=self.once([(0xffffffff,1,i,(0xffffffff,0,i)) for i in range(32)],'RADIUS_C1',0);self.assertLess(1-s['L_pen'],0)
 def test_seed_and_shuffle_order(self):
  import hashlib
  self.assertEqual(seed(3,7),int(hashlib.sha256(b'ORG-DIRECTION-048-r1|probe_direction|3|7').hexdigest()[:16],16));rs=roster();self.assertEqual(len(rs),192);self.assertEqual(len({q['seed'] for q in rs}),192)
  class Fake:
   def __init__(self):self.n=0
   def shuffle(self,a):assert a==list(range(32));k=self.n%32;a[:]=a[k:]+a[:k];self.n+=1
  f=Fake();q=permutations(f);self.assertEqual(f.n,1280)
  for g in range(40):
   for i in range(32):self.assertEqual(q[g][i],list(range(i,32))+list(range(i)))
 def test_grid_exact(self):
  v={a+'|'+g+'|'+p+'|'+m:0. for a in STARTS for g in LAWS for p in MODES for m in MET};derive(v);self.assertEqual(len(v),1664);keys={k for k in v if structural(k)};self.assertEqual(len(keys),112)
  expected=set()
  for a in STARTS:
   for g in LAWS:
    for aa,bb in [('ACTIVE','RADIUS'),('RADIUS','NOVEL'),('RADIUS','SHAM')]:
     for c in (0,1):
      for m in (('U0','F0') if bb=='NOVEL' else ('U0','F0','U1','F1')):expected.add(a+'|'+g+'|'+aa+'_C'+str(c)+'-'+bb+'_C'+str(c)+'|'+m)
  for a,g in [(a,'RECUR_MINUS_IID') for a in STARTS]+[('RESIDENT40_MINUS_NAIVE',g) for g in LAWS]:
   for c in (0,1):
    for m in ('U0','U1','F0','F1'):expected.add(a+'|'+g+'|ACTIVE_C'+str(c)+'-RADIUS_C'+str(c)+'|'+m)
  self.assertEqual(keys,expected)
 def test_fixed_pool_counterexample(self):
  from fractions import Fraction
  pools=([0,0,1,1,0,0,0,1],[0,0,1,2,0,0,0,1]);means=[]
  for pool in pools:means.append(sum((Fraction(sum(sorted(bin(x^t).count('1') for x in pool)[:2]),2) for t in range(4)),Fraction())/4)
  self.assertEqual(means,[Fraction(1,2),Fraction(3,8)])
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
