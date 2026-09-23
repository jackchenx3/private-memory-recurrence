import unittest,os,pathlib,json
import accepted_transfer_model as m
import model as w
import accepted_survival_model as old
from analysis import *
from lineages import extract,time_series
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
 def staged(self,pop,absolute=0,cost=0,targets=None):
  rec=w.stage(targets or [3,7]*20,self.draws,pop,cost,self.fresh+self.fresh,self.survival,absolute,7 if absolute else None);Tests.calls+=5152;Tests.sequences+=1;return rec
 def test_allcarrier_initialization_and_operators(self):
  self.assertIs(w.step,m.step);self.assertIs(w.Policy,m.Policy)
  for bg,k in [('H',1),('F',2)]:
   pop=w.all_policy(self.xs,bg);self.assertEqual([q[0] for q in pop],self.xs)
   for i,q in enumerate(pop):self.assertEqual(q,(self.xs[i],k,i,(self.xs[i],0,i)))
 def test_substitution_cache_and_reverse_provenance(self):
  original=[(i,2,5 if i<16 else 9,(i^3,37,i%4)) for i in range(32)];base,mapping=w.rebase(original);self.assertEqual([q[2] for q in base],list(range(32)))
  for i,(q,r) in enumerate(zip(original,base)):self.assertEqual(q[:2],r[:2]);self.assertEqual(q[3],r[3]);self.assertEqual(mapping[i]['preparation_founder'],q[2]);self.assertEqual(mapping[i]['cache'],q[3])
  switch=w.substitute(base,'F',7)
  for i,(q,r) in enumerate(zip(base,switch)):self.assertEqual(q[0],r[0]);self.assertEqual(q[2:],r[2:]);self.assertEqual(r[1],1 if i==7 else 2)
  self.assertEqual(w.substitute(base,'F'),base)
 def test_founder_extraction_stay_and_minority(self):
  for bg in ('F','H'):
   pop=w.all_policy(self.xs,bg)
   for cfg,i in [(bg+'_STAY',None),(bg+'_SWITCH0',0),(bg+'_SWITCH1',1)]:
    r=self.staged(w.substitute(pop,bg,None if i is None else self.labels[i]),40);fs,u=extract(r,self.labels,cfg);self.assertEqual(fs['p0'][0],1/32);self.assertEqual(fs['p1'][0],1/32)
    if i is None:self.assertEqual(fs[bg],[1]*41)
    else:self.assertEqual(fs['RARE'],fs['H' if bg=='F' else 'F'])
    for xs in fs.values():
     for x,y in zip(xs,xs[1:]):self.assertTrue(x!=0 or y==0)
 def test_absolute_time_and_separate_fresh_index(self):
  pop=w.all_policy(self.xs,'F');ev=m.Evaluator();ev.target=3;ev.begin();fresh=[[1]*32 for _ in range(40)]+[[2]*32 for _ in range(40)];eng=m.Policy(0,pop,fresh);eng.completed=40;st=w.step(eng,ev,[0]*32,[0]*32,[j/128 for j in range(128)],self.survival[0]);Tests.calls+=128;Tests.single_steps+=1
  self.assertEqual(st['fresh_probe_masks'],[2]*32)
  for j in range(32):self.assertEqual(st['candidates'][32+j][0],pop[j][0]^2)
  for j in range(32,128):self.assertEqual(st['candidates'][j][3],(pop[j%32][0],40,j%32))
  self.assertEqual(eng.completed,41)
 def test_uninterrupted80_equals_split40_40(self):
  first=[3,7]*20;second=[11,13]*20;pop=w.all_policy(self.xs,'F');fresh=self.fresh+[[9*i for i in range(32)] for _ in range(40)];d1=self.draws;d2=dict(self.draws,local=[[1<<(31-i) for i in range(32)]]*40);a=w.stage(first,d1,pop,0,fresh,self.survival);b=w.stage(second,d2,a['populations'][-1],0,fresh,self.survival,40,first[-1]);Tests.calls+=10304;Tests.sequences+=2
  ev=m.Evaluator();ev.target=first[0];eng=m.Policy(0,pop,fresh)
  for i,q in enumerate(pop):ev.score(q,i)
  snaps=[pop];ss=[]
  for j,target in enumerate(first+second):
   ev.target=target;ev.begin();d=d1 if j<40 else d2;localj=j%40;st=w.step(eng,ev,d['local'][localj],d['scout'][localj],d['ties'][localj],self.survival[localj]);ss.append(st);snaps.append(eng.pop)
  Tests.calls+=ev.calls;Tests.single_steps+=80;self.assertEqual(ev.calls,10272);self.assertEqual(snaps,a['populations']+b['populations'][1:])
  for x,y in zip(ss,a['steps']+b['steps']):
   for k in x:self.assertEqual(x[k],y[k])
  self.assertEqual(b['boundary_previous_target'],7);self.assertEqual(b['boundary_current_target'],11);self.assertTrue(b['boundary_actual_change']);self.assertFalse(b['ground_truth'][0]['actual_change']);self.assertEqual(b['ground_truth'][0]['absolute_update'],40);self.assertEqual(b['steps'][0]['W_raw'],0)
 def test_target_boundary_lag_two(self):
  from make_inputs import extend_targets
  history=list(range(40));innov=list(range(100,140));copy=[1,1,0,1]+[0]*36
  full=extend_targets(history,innov,copy,'FULL');half=extend_targets(history,innov,copy,'HALF');zero=extend_targets(history,innov,copy,'ZERO');self.assertEqual(full,[38,39]*20);self.assertEqual(half[:4],[38,39,102,39]);self.assertEqual(zero,innov)
 def test_common_cost_stage_invariance(self):
  pop=w.substitute(w.all_policy(self.xs,'H'),'H',7);a=self.staged(pop,40,0);b=self.staged(pop,40,1)
  for k in ('populations','raw_losses','frequencies','utilities','ground_truth'):self.assertEqual(a[k],b[k])
  for x,y in zip(a['steps'],b['steps']):self.assertEqual(x['selected_indices'],y['selected_indices']);self.assertEqual(x['candidates'],y['candidates']);self.assertEqual(y['race_keys'],[2*z for z in x['race_keys']])
 def test_grid624_24_and_references(self):
  v={g+'|C0|'+s+'|'+m:0. for g in LAWS for ss,ms in ((FBASE,FREQ),(RABS,RAW)) for s in ss for m in ms};self.assertEqual(len(v),312)
  for g in LAWS:
   for s in FBASE:v[g+'|C0|'+s+'|F0']=1/32
  derive(v);self.assertEqual(len(v),624);self.assertEqual(sum(structural(k) for k in v),24);self.assertFalse(structural('HALF_MINUS_ZERO|C0|F_BG_EFFECT|F1'));self.assertEqual(set(v),set(json.loads(pathlib.Path('DESIGN_GRID.json').read_text())['keys']))
 def test_position_average_and_single_stay_path(self):
  rows={cfg:dict(founders={r:{m:(i+j)/16. for m in FREQ} for j,r in enumerate(('p0','p1'))},raw={m:i/8. for m in RAW}) for i,cfg in enumerate(CONFIGS)};out=paired(rows);v={g+'|C0|'+k:x for g in LAWS for k,x in out.items()};derive(v)
  for k in orientation(rows,0):self.assertEqual((orientation(rows,0)[k]+orientation(rows,1)[k])/2,v['HALF|C0|'+k])
  self.assertEqual(out['F_BG_STAY|F40'],1/32);self.assertEqual(out['F_BG_STAY_POP|U40'],0)
 def test_seed_namespace_unique_and_prechecked(self):
  from make_inputs import roster,check_roster
  rs=roster();self.assertEqual(len(rs),1200);self.assertEqual(rs,json.loads(pathlib.Path('SEED_ROSTER.json').read_text()));check_roster(rs,json.loads(pathlib.Path('PRIOR_SEED_INVENTORY.json').read_text())['integers'])
 def test_fixed_criteria_separate(self):
  from assess_primary import assess
  keys=['HALF|C0|F_BG_EFFECT|D40','HALF|C0|H_BG_EFFECT|D40','HALF|C0|F_BG_SWITCH|D40','HALF|C0|H_BG_SWITCH|D40','HALF_MINUS_ZERO|C0|F_BG_EFFECT|D40'];v={k:dict(zero_classification='unresolved') for k in keys};v[keys[0]]['zero_classification']='positive';v[keys[1]]['zero_classification']='negative';q=assess(v);self.assertTrue(q['resident_background_policy_advantage_supported']);self.assertFalse(q['absolute_H_introduction_supported']);self.assertFalse(q['regime_comparison_supported'])
if __name__=='__main__':unittest.main(verbosity=2)
