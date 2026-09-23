import unittest,os,pathlib,json
import model as m
import accepted_survival_model as old
from analysis import *
from views import prefix
from io_utils import save,sha
from make_inputs import verify_inherited
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  assert os.environ.get('SLURM_JOB_ID');cls.calls=cls.sequences=cls.single_steps=0;cls.labels=list(range(7,32))+list(range(7));cls.xs=[i*17 for i in range(32)];cls.fresh=[[5*i for i in range(32)] for _ in range(40)];cls.draws=dict(labels=cls.labels,local=[[1<<i for i in range(32)]]*40,scout=[[0 if i%2 else 0xffffffff for i in range(32)]]*40,ties=[[j/128 for j in range(128)]]*40);cls.survival=[dict(k=[(j+1)*123456789 for j in range(128)],u=[m.to_uniform((j+1)*123456789) for j in range(128)]) for _ in range(40)]
 @classmethod
 def tearDownClass(cls):save('FIXTURE_WORK.json',dict(objective_calls=cls.calls,completed_toy_sequences=cls.sequences,completed_toy_single_steps=cls.single_steps,scientific_paths=0,random_draws=0))
 def seq(self,cfg,cost=0,t=None):
  r=m.sequence(t or [3,7]*20,self.draws,cfg,cost,self.fresh,self.xs,self.survival);Tests.calls+=5152;Tests.sequences+=1;return r
 def once(self,pop,cost=0,target=15,scout=None,survival=None,strategies=None,fresh=None):
  ev=m.Evaluator();ev.target=target;ev.begin();engine=m.Policy(cost,pop,self.fresh if fresh is None else fresh,strategies);s=m.step(engine,ev,[0]*32,scout or [0]*32,[j/128 for j in range(128)],survival or self.survival[0]);Tests.calls+=128;Tests.single_steps+=1;self.assertEqual(ev.calls,128);return s
 def test_two_position_initialization(self):
  for cfg in CONFIGS:
   pop=m.initial(cfg,self.labels,self.xs);self.assertEqual([q[0] for q in pop],self.xs);self.assertEqual([q[2] for q in pop],list(range(32)))
   for i,q in enumerate(pop):self.assertEqual(q[3],(q[0],0,i) if q[1] else None)
  self.assertEqual(m.initial('MIX0',self.labels,self.xs)[7][1],1);self.assertEqual(m.initial('MIX0',self.labels,self.xs)[8][1],2);self.assertEqual(m.initial('MIX1',self.labels,self.xs)[7][1],2)
 def test_single_policy_reductions(self):
  for cost in (0,1):
   for cfg,mode,role in [('H0','ACTIVE','H'),('F0','NOVEL','F')]:
    new=self.seq(cfg,cost);ref=old.sequence([3,7]*20,self.draws,mode+'_C'+str(cost),self.fresh,self.xs,self.survival);Tests.calls+=5152;Tests.sequences+=1
    for k in ('initial_queries','initial_raw_mismatches','raw_losses','penalized_losses','raw_accuracies','penalized_accuracies','ground_truth','query_counts'):self.assertEqual(new[k],ref[k])
    self.assertEqual(new['frequencies'][role],ref['frequencies'])
    norm=lambda pop:[(q[0],int(q[1]!=0),q[2],q[3]) for q in pop]
    self.assertEqual([norm(pop) for pop in new['populations']],ref['populations'])
    for a,b in zip(new['steps'],ref['steps']):
     for k in ('candidate_raw_mismatches','candidate_penalized_mismatches','donor_choices','race_keys','selected_indices','query_records','current_descendant_counts','S_raw','S_pen','W_raw','W_pen','L_raw','L_pen'):self.assertEqual(a[k],b[k])
     self.assertEqual(norm(a['candidates']),b['candidates'])
 def test_equal_carrier_cost(self):
  pop=[(0,i%3,i,(0,0,i) if i%3 else None) for i in range(32)];s=self.once(pop,1,target=0)
  for q,h,sp in zip(s['candidates'],s['candidate_raw_mismatches'],s['candidate_penalized_mismatches']):self.assertEqual(sp-h,int(q[1]!=0))
 def test_role_probes_and_cache_writes(self):
  pop=m.initial('MIX0',self.labels,self.xs);pop[7]=(3,1,7,(9,4,6));pop[8]=(5,2,8,(17,4,6));s=self.once(pop)
  self.assertEqual(s['candidates'][39][0],9);self.assertEqual(s['candidates'][40][0],5^40);self.assertTrue(s['h_retrieval_use'][7]);self.assertTrue(s['f_fresh_use'][8]);self.assertFalse(s['h_retrieval_use'][8])
  for j,q in enumerate(s['candidates']):self.assertEqual(q[1:3],pop[j%32][1:3]);self.assertEqual(q[3],pop[j][3] if j<32 else ((pop[j%32][0],0,j%32) if pop[j%32][1] else None))
 def test_raw_donors_and_race_order(self):
  s=self.once(m.initial('MIX0',self.labels,self.xs),1)
  for i,d in enumerate(s['donor_choices']):self.assertEqual(d['winner_index'],min((i,i+32,i+64),key=lambda j:(s['candidate_raw_mismatches'][j],s['ties'][j],j)))
  self.assertEqual(s['selected_indices'],sorted(range(128),key=lambda j:(s['race_keys'][j],s['ties'][j],j))[:32]);self.assertEqual(len(set(s['selected_indices'])),32)
 def test_three_frequencies_and_absence(self):
  for cfg in ('H1','F1','MIX0'):
   r=self.seq(cfg,1)
   for j in range(41):self.assertEqual(sum(fs[j] for fs in r['frequencies'].values()),1)
   for role,fs in r['frequencies'].items():
    for j,s in enumerate(r['steps']):self.assertEqual(fs[j+1]-fs[j],s['type_frequency_terms'][role]);self.assertTrue(fs[j]!=0 or fs[j+1]==0)
   for j,s in enumerate(r['steps']):self.assertEqual(s['S_pen'],s['S_raw']+(s['f_before']-s['f_after'])/32)
  s=self.once([(0,1 if i%2 else 2,i,(0,0,i)) for i in range(32)]);self.assertEqual(s['type_frequencies_after']['R'],0)
 def test_negative_selection_and_pen_accuracy(self):
  ks=[0]*128
  for j in range(64,96):ks[j]=2**52-1
  s=self.once(m.initial('MIX0',self.labels,[0]*32),target=0,scout=[0xffffffff]*32,survival=dict(k=ks,u=list(map(m.to_uniform,ks))));self.assertEqual(s['S_pen'],-1);self.assertEqual(s['S_raw'],-1);self.assertEqual(s['L_pen']-s['B_pen'],-s['S_pen'])
  s=self.once([(0xffffffff,2,i,(0xffffffff,0,i)) for i in range(32)],1,target=0,fresh=[[0]*32 for _ in range(40)]);self.assertLess(1-s['L_pen'],0)
 def test_same_policy_label_exchange_only(self):
  pop=m.initial('MIX0',self.labels,self.xs);swapped=[(x,3-k if k else 0,f,c) for x,k,f,c in pop];a=self.once(pop,1,strategies={0:'R',1:'F',2:'F'});b=self.once(swapped,1,strategies={0:'R',1:'F',2:'F'});self.assertEqual(a['race_keys'],b['race_keys']);self.assertEqual(a['selected_indices'],b['selected_indices']);self.assertEqual(a['type_frequencies_after']['H'],b['type_frequencies_after']['F'])
 def test_common_two_update_prefix(self):
  for cfg in NEW:
   for cost in (0,1):
    full=self.seq(cfg,cost)
    for ts in ([3,7]+list(range(38)),[3,7]+[9,5]*19):self.assertEqual(prefix(full),prefix(self.seq(cfg,cost,ts)))
 def test_grid_1482_84(self):
  v={g+'|'+c+'|'+s+'|'+m:0. for g in LAWS for c in COSTS for ss,ms in ((FABS,FREQ),(RABS,RAW)) for s in ss for m in ms};self.assertEqual(len(v),624);derive(v);self.assertEqual(len(v),1482);self.assertEqual(sum(structural(k) for k in v),84);self.assertFalse(structural('HALF|C0|MIX_H_MINUS_F|F1'))
 def test_orientation_pairing(self):
  rows={c:dict(raw={m:float(i) for m in RAW},frequency={r:{m:float(i) for m in FREQ} for r in ('H','F','R')}) for i,c in enumerate(CONFIGS)};v=paired(rows);self.assertEqual(v['MIX_H|F40'],.5);self.assertEqual(v['ISO_H|F40'],2.5);self.assertEqual(v['ISO_F|F40'],4.5)
 def test_primary_not_spread_or_moderation(self):
  from assess_primary import assess
  keys=['HALF|C0|'+s+'|D40' for s in ('MIX_H_MINUS_F','MIX_H','MIX_F','MIX_MINUS_ISO_RANK')]+['HALF_MINUS_ZERO|C0|MIX_H_MINUS_F|D40'];v={k:dict(zero_classification='unresolved') for k in keys};v[keys[0]]['zero_classification']='positive';a=assess(v);self.assertTrue(a['expectation_supported']);self.assertFalse(a['historical_mean_increase']);self.assertFalse(a['incremental_recurrence_supported'])
 def test_immutable_inputs(self):
  verify_inherited();self.assertFalse(pathlib.Path('INPUT_FREEZE.json').exists())
  for line in pathlib.Path('SOURCE_SHA256SUMS').read_text().splitlines():h,n=line.split(None,1);self.assertEqual(sha(n),h)
 def test_monitor_failure_propagation(self):
  import runner
  g=runner.Guard()
  def fail(_):raise RuntimeError('fixture failure')
  runner.monitor(g,fail)
  with self.assertRaises(RuntimeError):g.check()
  pathlib.Path('MONITOR_FAILURE.json').unlink()
 def test_seed_roster_coordinates(self):
  from make_inputs import roster,check_roster
  rs=roster();self.assertEqual(len(rs),1993);self.assertEqual(rs,json.loads(pathlib.Path('SEED_ROSTER.json').read_text()));check_roster(rs,json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers'])
  from collections import Counter
  self.assertEqual(Counter(q['family'] for q in rs)['bootstrap'],1)
  for q in rs:self.assertEqual(q['seed'],int(__import__('hashlib').sha256(q['namespace'].encode()).hexdigest()[:16],16))
 def test_generators_deterministic_api_order(self):
  import generators as g
  class Fake:
   def __init__(self):self.calls=[];self.n=0
   def randrange(self,n):self.calls.append(('randrange',n));self.n+=1;return (self.n-1)%n
   def getrandbits(self,n):self.calls.append(('getrandbits',n));self.n+=1;return self.n
   def random(self):self.calls.append(('random',));self.n+=1;return self.n/100000.
   def shuffle(self,a):self.calls.append(('shuffle',tuple(a)));a.reverse()
  q=Fake();a=g.local_masks(q);self.assertEqual(a,[[1]*32 for _ in range(40)]);self.assertEqual(q.calls,[('randrange',32)]*40960)
  q=Fake();a=g.scouts(q);self.assertEqual(a[0],list(range(1,33)));self.assertEqual(a[-1][-1],1280);self.assertEqual(q.calls,[('getrandbits',32)]*1280)
  q=Fake();a=g.ties(q);self.assertEqual(a[0][0],.00001);self.assertEqual(a[-1][-1],.0512);self.assertEqual(q.calls,[('random',)]*5120)
  q=Fake();self.assertEqual(g.labels(q),list(reversed(range(32))));self.assertEqual(len(q.calls),1)
  q=Fake();self.assertEqual(g.bootstrap(q),[list(range(24)) for _ in range(2000)]);self.assertEqual(q.calls,[('randrange',24)]*48000)
 def test_target_law_same_preparation_pair(self):
  from generators import build_targets
  for pair in ([3,7],[5,5]):
   zs=list(range(38));cs=[i%2 for i in range(38)]
   for law in LAWS:
    ts=build_targets(pair,zs,cs,law);self.assertEqual(ts[:2],pair)
    for i in range(2,40):self.assertEqual(ts[i],ts[i-2] if law=='FULL' or law=='HALF' and cs[i-2] else zs[i-2])
   self.assertEqual(build_targets(pair,zs,cs,'FULL'),pair*20)
 def test_accepted_preparation_and_unfiltered_reset(self):
  import preparation_model,accepted_rare_model
  from prepare import extract
  ts=[3,7]*20;a=preparation_model.sequence(ts,self.draws,'SHAM_C0',None);b=accepted_rare_model.sequence(ts,self.draws,'SHAM_C0');Tests.calls+=10304;Tests.sequences+=2;self.assertEqual(a,b);self.assertTrue(all(q[0]==0 for q in a['populations'][0]));self.assertEqual(sum(q[1] for q in a['populations'][0]),1)
  rr=extract(a,0,0,ts[:2]);self.assertEqual(rr['genotypes'],[q[0] for q in a['populations'][-1]])
  for cfg in CONFIGS:
   pop=m.initial(cfg,list(reversed(self.labels)),rr['genotypes']);self.assertEqual([q[0] for q in pop],rr['genotypes']);self.assertEqual([q[2] for q in pop],list(range(32)))
   for i,q in enumerate(pop):self.assertEqual(q[3],(q[0],0,i) if q[1] else None)
  # An equal-target or unfavorable record is extracted identically, without a criterion.
  rr=extract(a,1,2,[5,5]);self.assertFalse(rr['boundary_change']);self.assertEqual(rr['genotypes'],[q[0] for q in a['populations'][-1]])
 def test_staged_freeze_and_accounting(self):
  from make_inputs import validate_freeze
  tmp=pathlib.Path('fixture-freeze.json');tmp.write_text(json.dumps(dict(source_manifest_sha256=sha('SOURCE_SHA256SUMS'),files={'model.py':sha('model.py')})))
  try:
   self.assertEqual(validate_freeze(str(tmp))['files']['model.py'],sha('model.py'));tmp.write_text(json.dumps(dict(source_manifest_sha256='wrong',files={})))
   with self.assertRaises(AssertionError):validate_freeze(str(tmp))
  finally:tmp.unlink()
  self.assertFalse(pathlib.Path('PREPARATION_STARTED.json').exists());self.assertFalse(pathlib.Path('RESIDENT_FREEZE.json').exists());self.assertFalse(pathlib.Path('TRANSFER_STARTED.json').exists());self.assertEqual(192*5152,989184);self.assertEqual(6912*5152,35610624);self.assertEqual((192+6912)*5152,36599808)
 def test_three_part_replication_decision(self):
  from assess_primary import assess
  keys=['HALF|C0|'+s+'|D40' for s in ('MIX_H_MINUS_F','MIX_H','MIX_F','MIX_MINUS_ISO_RANK')]+['HALF_MINUS_ZERO|C0|MIX_H_MINUS_F|D40'];v={k:dict(zero_classification='positive') for k in keys};self.assertTrue(assess(v)['full_three_part_pattern_reproduced']);v[keys[-1]]['zero_classification']='unresolved';self.assertTrue(assess(v)['expectation_supported']);self.assertFalse(assess(v)['full_three_part_pattern_reproduced'])
if __name__=='__main__':unittest.main(verbosity=2)
