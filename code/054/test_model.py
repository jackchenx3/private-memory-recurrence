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
 def test_negative_selection_and_pen_accuracy(self):
  ks=[0]*128
  for j in range(64,96):ks[j]=2**52-1
  s=self.once(m.initial('MIX0',self.labels,[0]*32),target=0,scout=[0xffffffff]*32,survival=dict(k=ks,u=list(map(m.to_uniform,ks))));self.assertEqual(s['S_pen'],-1);self.assertEqual(s['S_raw'],-1);self.assertEqual(s['L_pen']-s['B_pen'],-s['S_pen'])
  s=self.once([(0xffffffff,2,i,(0xffffffff,0,i)) for i in range(32)],1,target=0,fresh=[[0]*32 for _ in range(40)]);self.assertLess(1-s['L_pen'],0)
 def test_same_policy_label_exchange_only(self):
  pop=m.initial('MIX0',self.labels,self.xs);swapped=[(x,3-k if k else 0,f,c) for x,k,f,c in pop];a=self.once(pop,1,strategies={0:'R',1:'F',2:'F'});b=self.once(swapped,1,strategies={0:'R',1:'F',2:'F'});self.assertEqual(a['race_keys'],b['race_keys']);self.assertEqual(a['selected_indices'],b['selected_indices']);self.assertEqual(a['type_frequencies_after']['H'],b['type_frequencies_after']['F'])
 def test_common_two_update_prefix(self):
  for cfg in NEW:
   for cost in (0,):
    full=self.seq(cfg,cost)
    for ts in ([3,7]+list(range(38)),[3,7]+[9,5]*19):self.assertEqual(prefix(full),prefix(self.seq(cfg,cost,ts)))
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
 def test_allcarrier_initialization(self):
  for cfg in CONFIGS:
   pop=m.initial(cfg,self.labels,self.xs);self.assertEqual([q[0] for q in pop],self.xs);self.assertEqual([q[2] for q in pop],list(range(32)));rareid=self.labels[int(cfg[-1])];rare=1 if cfg.startswith('LOW') else 2
   for i,q in enumerate(pop):self.assertEqual(q[1],rare if i==rareid else 3-rare);self.assertEqual(q[3],(q[0],0,i))
   f=m.frequencies(pop);self.assertEqual(f['R'],0);self.assertEqual(f['H'],1/32 if rare==1 else 31/32)
 def test_rare_founder_complements_absence(self):
  from lineages import extract
  for cfg in CONFIGS:
   rec=self.seq(cfg);fs,u=extract(rec,self.labels[int(cfg[-1])],cfg);self.assertEqual(fs['RARE'][0],1/32)
   for i in range(41):self.assertEqual(fs['H'][i]+fs['F'][i],1);self.assertEqual(fs['R'][i],0)
   for j,st in enumerate(rec['steps']):
    before=rec['populations'][j]
    for i,q in enumerate(st['candidates']):self.assertEqual(q[1:3],before[i%32][1:3])
    for r,k in [('H',1),('F',2)]:self.assertEqual(fs[r][j+1]-fs[r][j],sum((d-1)*(int(q[1]==k)-fs[r][j]) for d,q in zip(st['current_descendant_counts'],before))/32);self.assertTrue(fs[r][j]!=0 or fs[r][j+1]==0)
  for k in (1,2):
   st=self.once([(i,k,i,(i,0,i)) for i in range(32)]);self.assertEqual(set(q[1] for q in st['selected_records']),{k})
 def test_uniform_cost_shift_structural_invariance(self):
  for cfg in CONFIGS:
   a=self.seq(cfg,0);b=self.seq(cfg,1)
   for key in ('populations','raw_losses','raw_accuracies','frequencies','ground_truth','utilities','query_counts','initial_queries','initial_raw_mismatches'):self.assertEqual(a[key],b[key])
   for x,y in zip(a['penalized_losses'],b['penalized_losses']):self.assertEqual(y,x+1/32)
   for x,y in zip(a['steps'],b['steps']):
    for key in ('candidates','selected_indices','selected_records','sources','selected_sources','donor_choices','query_records','current_descendant_counts','S_raw','S_pen','W_raw','W_pen'):self.assertEqual(x[key],y[key])
    self.assertEqual(y['race_keys'],[2*z for z in x['race_keys']]);self.assertEqual(y['candidate_penalized_mismatches'],[z+1 for z in x['candidate_penalized_mismatches']]);self.assertEqual(x['S_pen'],x['S_raw'])
 def test_unchanged_old_initialization(self):
  import accepted_transfer_model as ref
  for cfg in ('HH','FF','MIX0','MIX1','H0','H1','F0','F1'):self.assertEqual(m.initial(cfg,self.labels,self.xs),ref.initial(cfg,self.labels,self.xs))
 def test_grid_429_21_and_nonzero_initial_contrast(self):
  v={g+'|C0|'+s+'|'+m:0. for g in LAWS for ss,ms in ((FBASE,FREQ),(RABS,RAW)) for s in ss for m in ms};self.assertEqual(len(v),234)
  for g in LAWS:
   for pre,f in [('LOW',1/32),('HIGH',31/32)]:v[g+'|C0|'+pre+'_H|F0']=f;v[g+'|C0|'+pre+'_F|F0']=1-f
  derive(v);self.assertEqual(len(v),429);self.assertEqual(sum(structural(k) for k in v),21)
  for g in LAWS:self.assertEqual(v[g+'|C0|LOW_MINUS_HIGH_H|F0'],-30/32);self.assertFalse(structural(g+'|C0|LOW_MINUS_HIGH_H|F0'))
 def test_position_average_and_endpoint_estimands(self):
  rows={cfg:dict(frequency={r:{m:(i+j)/16. for m in FREQ} for j,r in enumerate(('H','F','R'))},raw={m:i/8. for m in RAW}) for i,cfg in enumerate(CONFIGS)};q=paired(rows);v={g+'|C0|'+k:x for g in LAWS for k,x in q.items()};derive(v)
  for k in orientation(rows,0):self.assertEqual((orientation(rows,0)[k]+orientation(rows,1)[k])/2,v['HALF|C0|'+k])
  from accepted_model import metrics
  low=metrics([.5]*41,[1/32]+[.5]*40);high=metrics([.5]*41,[31/32]+[.75]*40);self.assertEqual(low['F40']-high['F40'],-.25);self.assertEqual(low['D40']-high['D40'],.6875)
 def test_independent_fixed_criteria(self):
  from assess_primary import assess
  keys=['HALF|C0|LOW_H|D40','HALF|C0|HIGH_F|D40','HALF_MINUS_ZERO|C0|LOW_H|D40','HALF|C0|LOW_MINUS_HIGH_H|D40'];v={k:dict(zero_classification='unresolved') for k in keys};v[keys[0]]['zero_classification']='positive';self.assertTrue(assess(v)['primary_supported']);self.assertFalse(assess(v)['two_boundary_H_advantage_supported']);v[keys[1]]['zero_classification']='negative';self.assertTrue(assess(v)['two_boundary_H_advantage_supported']);self.assertFalse(assess(v)['incremental_recurrence_supported'])
 def test_time_series_complement_and_reference(self):
  from lineages import time_series
  rows={cfg:dict(frequency={'H':[a]*41,'F':[1-a]*41},accuracy=[.75]*41) for cfg,a in [('LOW0',1/32),('LOW1',1/32),('HIGH0',31/32),('HIGH1',31/32)]};ts=time_series(rows);self.assertEqual(len(ts),8);self.assertEqual(ts['LOW_MINUS_HIGH_H'],[-30/32]*41);self.assertEqual(ts['LOW_MINUS_HIGH_POP'],[0]*41)
if __name__=='__main__':unittest.main(verbosity=2)
