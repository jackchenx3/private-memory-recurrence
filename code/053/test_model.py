import unittest,os,pathlib,json
import model as m
import accepted_survival_model as old
from analysis import *
from lineages import prefix
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
 def test_grid_1716_90(self):
  v={g+'|'+c+'|'+s+'|'+m:0. for g in LAWS for c in COSTS for ss,ms in ((FBASE,FREQ),(RABS,RAW)) for s in ss for m in ms};self.assertEqual(len(v),546);derive(v);self.assertEqual(len(v),1716);self.assertEqual(sum(structural(k) for k in v),90);self.assertFalse(structural('HALF|C0|R_H|F1'))
 def test_orientation_pairing_and_interaction(self):
  rows={c:dict(raw={m:float(i) for m in RAW},founders={r:{m:float(i+j) for m in FREQ} for j,r in enumerate(('p0','p1'))},frequency={r:{m:float(i+(r=='H')) for m in FREQ} for r in ('H','F','R')}) for i,c in enumerate(CONFIGS)}
  # Actual mixed founder identities must agree with the H/F policy mapping.
  for cfg,i in [('MIX0',0),('MIX1',1)]:
   rows[cfg]['frequency']['H']=rows[cfg]['founders']['p'+str(i)];rows[cfg]['frequency']['F']=rows[cfg]['founders']['p'+str(1-i)]
  out=paired(rows);self.assertEqual(out['HH_AVG|F40'],.5);self.assertEqual(out['FF_AVG|F40'],1.5);v={g+'|'+c+'|'+k:x for g in LAWS for c in COSTS for k,x in out.items()};derive(v)
  for m in FREQ:
   a,b=orientation(rows,0),orientation(rows,1)
   for key in ('R_H','R_F','COMP_H','COMP_F','INTERACTION','MIX_RANK'):self.assertAlmostEqual((a[key+'|'+m]+b[key+'|'+m])/2,v['HALF|C0|'+key+'|'+m])
   q=lambda k:v['HALF|C0|'+k+'|'+m];self.assertAlmostEqual(q('INTERACTION'),(q('HH_CARR')+q('FF_CARR'))/2-q('HF_CARR'))
 def test_primary_companion_separate(self):
  from assess_primary import assess
  v={k:dict(zero_classification='unresolved') for k in ['HALF|C0|R_H|D40','HALF|C0|R_F|D40','HALF|C0|INTERACTION|D40']};v['HALF|C0|R_H|D40']['zero_classification']='positive';self.assertTrue(assess(v)['primary_supported']);self.assertFalse(assess(v)['common_competitor_pattern_supported']);v['HALF|C0|R_F|D40']['zero_classification']='positive';self.assertTrue(assess(v)['common_competitor_pattern_supported'])
 def test_homotypic_founder_initialization(self):
  for cfg,k in [('HH',1),('FF',2)]:
   pop=m.initial(cfg,self.labels,self.xs);self.assertEqual([q[0] for q in pop],self.xs);self.assertEqual([q[2] for q in pop],list(range(32)));self.assertEqual(sum(q[1]!=0 for q in pop),2)
   for i,q in enumerate(pop):self.assertEqual(q[1],k if i in self.labels[:2] else 0);self.assertEqual(q[3],(q[0],0,i) if i in self.labels[:2] else None)
 def test_founder_tracking_and_absence(self):
  from lineages import extract
  for cfg in NEW:
   rec=self.seq(cfg,1);fs,u=extract(rec,self.labels)
   for i in range(41):self.assertEqual(fs['p0'][i]+fs['p1'][i],fs['CARR'][i]);self.assertEqual(fs['CARR'][i]+fs['R'][i],1)
   self.assertEqual(fs['p0'][0],1/32);self.assertEqual(fs['CARR'][0],1/16)
   for j,st in enumerate(rec['steps']):
    before=rec['populations'][j]
    for i,q in enumerate(st['candidates']):self.assertEqual(q[2],before[i%32][2])
    for k,fid in zip(('p0','p1'),self.labels[:2]):self.assertEqual(fs[k][j+1]-fs[k][j],sum((n-1)*(int(q[2]==fid)-fs[k][j]) for n,q in zip(st['current_descendant_counts'],before))/32);self.assertTrue(fs[k][j]!=0 or fs[k][j+1]==0)
 def test_unchanged_mixed_reduction(self):
  import accepted_transfer_model as ref
  for cfg in ('MIX0','MIX1'):
   a=self.seq(cfg,1);b=ref.sequence([3,7]*20,self.draws,cfg,1,self.fresh,self.xs,self.survival);Tests.calls+=5152;Tests.sequences+=1;self.assertEqual(a,b)
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
 def test_time_series_identities(self):
  from lineages import time_series
  rows={cfg:dict(founders={'p0':[a]*41,'p1':[b]*41},accuracy=[q]*41) for cfg,a,b,q in [('HH',.125,.25,.75),('FF',.0625,.125,.5),('MIX0',.25,.0625,.625),('MIX1',.125,.375,.875)]};ts=time_series(rows);self.assertEqual(len(ts),19);self.assertEqual(ts['HH_POP'],[.75]*41);self.assertEqual(ts['HF_POP'],[.75]*41)
  for i in range(41):self.assertEqual(ts['INTERACTION'][i],ts['R_H'][i]-ts['R_F'][i]);self.assertEqual(ts['INTERACTION'][i],(ts['HH_CARR'][i]+ts['FF_CARR'][i])/2-ts['HF_CARR'][i])
if __name__=='__main__':unittest.main(verbosity=2)
