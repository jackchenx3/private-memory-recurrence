import unittest,os,pathlib,json,ast
import accepted_model as old
from model import initial,sequence,Policy,Evaluator,step
from analysis import MODES,NEW
from signatures import prefix,first,numeric
from analysis import derive,structural,MET
from make_inputs import verify_inherited,seed,masks
from io_utils import save,sha
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  assert os.environ.get('SLURM_JOB_ID');cls.calls=cls.sequences=cls.single_steps=0;cls.fresh=[[0,3,0xffffffff]+[1<<i for i in range(3,32)]]*40;cls.labels=list(range(7,32))+list(range(7));cls.draws=dict(labels=cls.labels,local=[[1<<(i%32) for i in range(32)]]*40,scout=[[0 if i%2 else 0xffffffff for i in range(32)]]*40,ties=[[j/128 for j in range(128)]]*40)
 @classmethod
 def tearDownClass(cls):save('FIXTURE_WORK.json',dict(objective_calls=cls.calls,completed_toy_sequences=cls.sequences,completed_toy_single_steps=cls.single_steps,scientific_paths=0,random_draws=0))
 def seq(self,targets,mode):
  rec=sequence(targets,self.draws,mode,self.fresh);Tests.calls+=rec['query_counts']['total'];Tests.sequences+=1;return rec
 def once(self,pop,mode,target,local=None,scout=None,ties=None,original=False,fresh=None):
  e=old.Policy(mode,pop) if original else Policy(mode,pop,fresh or self.fresh);ev=Evaluator();ev.target=target;ev.begin();s=(old.step if original else step)(e,ev,local or [0]*32,scout or [0]*32,ties or [j/128 for j in range(128)]);Tests.calls+=ev.calls;Tests.single_steps+=1;return s
 def test_initial_nontrivial_nested_slot(self):
  for mode in ('ACTIVE_C0','ACTIVE_C1','SHAM_C0','SHAM_C1'):
   pop=initial(mode,self.labels);half=old.initial(mode,self.labels);self.assertEqual(sum(p[1] for p in pop),1);self.assertEqual(pop[7],(0,1,7,(0,0,7)));self.assertEqual(half[7],pop[7]);self.assertEqual(sum(p[1] for p in half),16);self.assertTrue(all(p[0]==0 and p[2]==i for i,p in enumerate(pop)));self.assertTrue(all(pop[i][3] is None for i in range(32) if i!=7))
 def test_private_cache_and_recipient_inheritance(self):
  pop=initial('ACTIVE_C0',self.labels);pop[7]=(3,1,7,(9,2,5))
  for mask in (0,3,10,15,0xffffffff):
   fresh=[[mask]*32]*40;e=Policy('NOVEL_C0',pop,fresh);e.completed=6;self.assertEqual(e.probes()[7],(3^mask,1,7,(3,6,7)));self.assertEqual(e.pop[7],pop[7])
  s=self.once(pop,'NOVEL_C0',15,fresh=[[10]*32]*40,scout=[10]*32)
  self.assertEqual(s['candidates'][39][0],9);self.assertEqual(s['candidates'][71][0],9);self.assertFalse(any(s['probe_access']))
  for j in range(128):
   self.assertEqual(s['candidates'][j][1:3],pop[j%32][1:3])
   if j<32:self.assertEqual(s['candidates'][j],pop[j])
   else:self.assertEqual(s['candidates'][j][3],(pop[j%32][0],0,j%32) if pop[j%32][1] else None)
 def test_queries_zero_multiple_flips_and_donor_coordinates(self):
  pop=initial('ACTIVE_C0',self.labels);local=[0,3,0xffffffff]+[1<<i for i in range(3,32)];s=self.once(pop,'NOVEL_C0',15,local=local,scout=[0xffffffff]*32);self.assertEqual(s['evaluator_calls'],128);self.assertEqual([q['candidate_index'] for q in s['query_records']],list(range(128)))
  for i,d in enumerate(s['donor_choices']):
   win=min([i,32+i,64+i],key=lambda j:(s['candidate_raw_mismatches'][j],s['ties'][j],j));self.assertEqual(d['winner_index'],win);self.assertEqual(s['candidates'][96+i][0],s['candidates'][win][0]^local[i])
 def test_full_prefixes_and_fields(self):
  for cost in (0,1):
   iid=self.seq([3,7]+[15]*38,'NOVEL_C'+str(cost));rec=self.seq([3,7]*20,'NOVEL_C'+str(cost));self.assertEqual(prefix(iid),prefix(rec))
   for r in (iid,rec):
    self.assertEqual(r['query_counts']['total'],5152)
    for j,s in enumerate(r['steps']):
     self.assertEqual(s['frequency_term'],r['frequencies'][j+1]-r['frequencies'][j]);self.assertEqual(s['S_pen'],s['S_raw']+cost*(s['f_before']-s['f_after'])/32)
     for k,field in (('raw','raw_losses'),('pen','penalized_losses')):self.assertEqual(r[field][j+1]-r[field][j],s['W_'+k]-s['S_'+k])
 def test_absorption_all_noncarrier_operator(self):
  pop=[(0,0,i,None) for i in range(32)];s=self.once(pop,'NOVEL_C1',15,scout=[1]*32);t=self.once(pop,'ACTIVE_C1',15,scout=[1]*32,original=True);self.assertEqual(s['f_after'],0);self.assertTrue(all(p[1]==0 and p[3] is None for p in s['selected_records']));s.pop('fresh_probe_use');s.pop('fresh_probe_masks');self.assertEqual(s,t)
 def test_negative_raw_and_penalized_valid(self):
  pop=[(0,1,i,(0,0,i)) if i<16 else (1,0,i,None) for i in range(32)];s=self.once(pop,'SHAM_C1',0,original=True,ties=[1 if j%32<16 else 0 for j in range(128)]);self.assertLess(s['S_raw'],0);self.assertGreaterEqual(s['S_pen'],0)
  pop=[(0xffffffff,1,i,(0xffffffff,0,i)) for i in range(32)];s=self.once(pop,'NOVEL_C1',0,fresh=[[0]*32]*40);self.assertLess(1-s['L_pen'],0);self.assertEqual(s['f_after'],1)
 def test_xor_bijection_and_seed_draw_order(self):
  for bits in range(1,6):
   for x in range(2**bits):self.assertEqual(sorted(x^u for u in range(2**bits)),list(range(2**bits)))
  import hashlib
  self.assertEqual(seed(3,7),int(hashlib.sha256(b'ORG-NOVELTY-045-r1|fresh_probe|3|7').hexdigest()[:16],16))
  class Fake:
   def __init__(self):self.n=0
   def getrandbits(self,k):assert k==32;self.n+=1;return self.n-1
  f=Fake();v=masks(f);self.assertEqual(v,[[g*32+i for i in range(32)] for g in range(40)]);self.assertEqual(f.n,1280)
 def test_grid_780_52_exact_keys(self):
  v={'RARE|'+g+'|'+p+'|'+m:0. for g in ('IID','RECUR') for p in MODES for m in MET};derive(v);keys={k for k in v if structural(k)};self.assertEqual(len(v),780);self.assertEqual(len(keys),52);self.assertEqual(keys,set(json.loads(pathlib.Path('DESIGN_CHECK.json').read_text())['structural_zero_keys']));self.assertFalse(structural('RARE|RECUR|ACTIVE_C0-NOVEL_C0|F1'))
 def test_inherited_and_source_immutability(self):
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
