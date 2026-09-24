"""Focused deterministic checks; production seeds are never drawn here."""
import unittest,itertools,copy,hashlib,json,collections,ast,time
from common import *
from objectives import loss,Evaluator,TRAP,SCHEMA
from raw_audit import reference_loss,audit_record,canon
from analysis import *
from seed_design import roster,verify_roster
from model import stage,all_policy,rebase,substitute
from preparation_model import sequence
from accepted_inputs055 import extend_targets
from accepted_model import Policy as InitialPolicy,step as initial_step
from accepted_transfer_model import Policy as TransferPolicy,step as transfer_step
from audit_independent import coefficients
CALLS=collections.Counter()
class Tests(unittest.TestCase):
 def test_full_translated_truth_table(self):
  counts=collections.Counter()
  for t in range(16):
   for x in range(16):
    got=loss(x,t,'TRAP4');u=4-bin(x^t).count('1');self.assertEqual(got,TRAP[u]);self.assertEqual(got,reference_loss(x,t,'TRAP4'))
    if t==0:counts[got]+=1
  self.assertEqual(dict(counts),{0:1,4:4,3:6,2:4,1:1});self.assertEqual(sum(k*v for k,v in counts.items())/16,43/16)
 def test_range_optima_nonadditivity(self):
  self.assertEqual(loss(0,0,'TRAP4'),0);self.assertEqual(loss(0x11111111,0,'TRAP4'),32)
  corners=[]
  for bits in itertools.product((0,15),repeat=8):
   x=sum(v<<(4*j) for j,v in enumerate(bits));y=loss(x,0,'TRAP4');corners.append(y)
   for i in range(32):self.assertGreater(loss(x^(1<<i),0,'TRAP4'),y)
  self.assertEqual(len(corners),256);self.assertEqual(corners.count(0),1)
  self.assertEqual(loss(3,0,'TRAP4')-loss(1,0,'TRAP4')-loss(2,0,'TRAP4')+loss(0,0,'TRAP4'),-5)
  # Every noncorner block has an improving neighbor; zeros require every block matched.
  for x in range(1,15):self.assertTrue(any(loss(x^(1<<i),0,'TRAP4')<loss(x,0,'TRAP4') for i in range(4)))
 def test_saved_ham_compatibility(self):
  for fixture in read('ACCEPTED_HAM_FIXTURES.json'):
   self.assertEqual(sha(P.parent/fixture['source']),fixture['source_sha256'])
   before=[canon(x) for x in fixture['before']];ev=Evaluator('HAM');ev.target=fixture['target']
   self.assertEqual([ev.score(q,i) for i,q in enumerate(before)],[q['raw_mismatch'] for q in fixture['initial_queries']]);ev.begin();s=fixture['step'];d=fixture['draws'];start=fixture['absolute_start']
   if fixture['stage']=='initial':
    engine=InitialPolicy('SHAM_C0',before);got=initial_step(engine,ev,d['local'],d['scout'],d['ties'])
   else:
    fresh=[[0]*32 for _ in range(start)]+[s['fresh_probe_masks']];engine=TransferPolicy(0,before,fresh);engine.completed=start
    got=transfer_step(engine,ev,d['local'],d['scout'],d['ties'],dict(k=s['survival_integers'],u=s['survival_uniforms']))
   got['W_raw']=got['B_raw']-sum(q['raw_mismatch'] for q in fixture['initial_queries'])/1024.;got['W_pen']=got['W_raw']
   for q in got['query_records']:self.assertEqual(q.pop('objective'),'HAM')
   self.assertEqual(canon_json(got),s);CALLS['accepted_fixture_calls']+=ev.calls
 def test_all_three_stage_propagation(self):
  d=dict(labels=list(range(32)),local=[[1<<((i+g)%32) for i in range(32)] for g in range(40)],scout=[[((i+1)*1234567+g)%2**32 for i in range(32)] for g in range(40)],ties=[[(i+1)/129 for i in range(128)] for _ in range(40)])
  ts=[0x11111111,0xfedcba98]*20;fresh=[[(i*76543+g)%2**32 for i in range(32)] for g in range(80)];ks=[(i+1)*2**44 for i in range(128)];ss=[dict(k=ks,u=[(k+1)/(2**52+1) for k in ks]) for _ in range(40)]
  allrecords={}
  for obj in ('HAM','TRAP4'):
   first=sequence(ts,d,'SHAM_C0',objective=obj);first=canon_json(first);pop=first['populations'][0];audit_record(first,d,ts,pop)
   prep0=all_policy([x[0] for x in first['populations'][-1]],'F');second=canon_json(stage(ts,d,prep0,0,fresh,ss,objective=obj));audit_record(second,d,ts,prep0,fresh,ss)
   rebased,mapping=rebase(second['populations'][-1]);transfer0=substitute(rebased,'F',d['labels'][0]);third=canon_json(stage(ts,d,transfer0,0,fresh,ss,40,ts[-1],objective=obj));audit_record(third,d,ts,transfer0,fresh,ss,40)
   for rec in (first,second,third):
    self.assertEqual(rec['objective'],obj);self.assertEqual(rec['query_counts']['total'],5152);self.assertLess(len(json.dumps(dict(record=rec,block=0,replicate=0,objective=obj),separators=(',',':')).encode()),2**21)
   CALLS['constructed_fixture_paths']+=3;CALLS['constructed_fixture_calls']+=3*5152;allrecords[obj]=first
  self.assertNotEqual(allrecords['HAM']['initial_raw_mismatches'],allrecords['TRAP4']['initial_raw_mismatches'])
 def test_donor_prefers_different_objective(self):
  # Against zero, parent15 is trap-local optimum but Hamming prefers scout7.
  pop=[(15,2,i,(15,0,i)) for i in range(32)];p=TransferPolicy(0,pop,[[0]*32]);ties=[j/128 for j in range(128)];pool=pop+p.probes()+p.scouts([8]*32)
  wins={}
  for o in ('HAM','TRAP4'):
   _,donors=p.children(pool,[loss(x[0],0,o) for x in pool],ties,[0]*32);wins[o]=donors[0]['winner_index']
  self.assertEqual(wins,{'HAM':64,'TRAP4':0})
 def test_cache_founder_substitution(self):
  original=all_policy(list(range(32)),'H');original=[(x,k,31-i,(x^1,39,i)) for i,(x,k,f,c) in enumerate(original)]
  rebased,m=rebase(original);sw=substitute(rebased,'H',3)
  for i,(a,b) in enumerate(zip(rebased,sw)):
   self.assertEqual((a[0],a[2],a[3]),(b[0],b[2],b[3]));self.assertEqual(b[1],2 if i==3 else 1);self.assertEqual(m[i]['preparation_founder'],31-i)
 def test_seeds_and_coupling(self):
  rs=roster();self.assertTrue(verify_roster(rs,read('PRIOR_SEED_INVENTORY.json')['integers']));self.assertEqual(len(rs),3193)
  self.assertTrue(all(q['namespace'].startswith('ORG-LANDSCAPE-058-r1|') and 'HAM' not in q['namespace'] and 'TRAP' not in q['namespace'] for q in rs))
  # Input-generation and stage loops consume indexed tapes, never random draws.
  for n in ('prepare_initial.py','prepare_policy.py','transfer.py','model.py','preparation_model.py'):
   s=(P/n).read_text();self.assertNotIn('random.',s)
  self.assertIn("for objective in ('HAM','TRAP4')",(P/'prepare_initial.py').read_text());self.assertIn("for objective in ('HAM','TRAP4')",(P/'prepare_policy.py').read_text())
 def test_boundary_and_counts(self):
  h=[1,2]*20;innov=list(range(100,140));bits=[1,0]*20
  z=extend_targets(h,innov,bits,'ZERO');half=extend_targets(h,innov,bits,'HALF')
  self.assertEqual(z,innov);self.assertEqual(half[0],h[-2]);self.assertEqual(half[1],innov[1]);self.assertEqual(half[2],half[0])
  c=read('config.json');self.assertEqual(384+768+4608,c['total_paths']);self.assertEqual(c['total_paths']*5152,29675520);self.assertEqual(c['total_paths']*5120,c['new_candidate_calls']);self.assertEqual(c['total_paths']*32,c['new_initial_calls'])
 def test_paired_catalog_arithmetic(self):
  cells,cs=coefficients();inputrows={cell:{k:(i+1)**2*(j+1)/1024 for j,k in enumerate(ENDPOINTS)} for i,cell in enumerate(cells)};got=combine(inputrows)
  self.assertEqual(len(got),114);self.assertEqual(set(got),set(KEYS));self.assertEqual(set(read('METRIC_CATALOG.json')['keys']),set(KEYS))
  for g,c in cs.items():
   for k in ENDPOINTS:
    if g.startswith('TRAP4_MINUS_HAM') and not k.endswith('|D40'):continue
    self.assertAlmostEqual(got[g+'|'+k],sum(c[i]*inputrows[cell][k] for i,cell in enumerate(cells)))
 def test_decisions(self):
  for ci,want in [([.01,.02],'supports_positive'),([-.1,-.01],'contradicts_positive'),([-.01,.01],'unresolved'),([0,.1],'unresolved')]:self.assertEqual(decisions(ci)['direction'],want)
  for ci,want in [([.04,.05],'supports_exceeding_one_expected_descendant'),([-.1,.02],'does_not_support_at_least_one_expected_descendant'),([.02,.04],'unresolved'),([DELTA,.1],'unresolved')]:self.assertEqual(decisions(ci)['benchmark'],want)
 def test_full_independent_statistical_recomputation(self):
  import tempfile,gzip
  from unittest.mock import patch
  import audit_independent as audit
  from validate_analyze import interval
  panel=[];paired={};indices=[[(i*i+i*(j%5)+j)%24 for i in range(24)] for j in range(2000)]
  for b in range(24):
   for r in range(8):
    cells={}
    for ci,cell in enumerate(CELLS):
     series={};endpoints={}
     for bg in ('F','H'):
      for kind,factor in (('SWITCH',2),('STAY',1),('EFFECT',1)):
       for suffix in ('','_POP'):
        name=bg+'_BG_'+kind+suffix;start=0 if kind=='EFFECT' else .5 if suffix else 1/32
        slope=(1 if bg=='F' else -1)*factor*(ci+1)*(b+1)*(r+1)/100000
        xs=[start+slope*t/40 for t in range(41)];series[name]=xs
        if suffix:endpoints[name+'|U']=sum(xs[1:])/40;endpoints[name+'|U40']=xs[-1]
        else:endpoints[name+'|D40']=xs[-1]-xs[0]
     panel.append(dict(block=b,replicate=r,cell=cell,values=series));cells[cell]=endpoints
    paired[b,r]=combine(cells)
  estimates={}
  for k in KEYS:
   xs=[sum(paired[b,r][k] for r in range(8))/8 for b in range(24)];mean,ci=interval(xs,indices);estimates[k]=dict(mean=mean,ci95=ci)
  with tempfile.TemporaryDirectory() as temp:
   root=pathlib.Path(temp)
   with gzip.open(root/'TIME_SERIES.jsonl.gz','wt') as f:
    for row in panel:f.write(json.dumps(row)+'\n')
   data={'BOOTSTRAP_INDICES.json':indices,'ESTIMATES.json':estimates,'ASSESSMENT.json':dict(decisions=decisions(estimates[PRIMARY]['ci95']))}
   # Explicit test-only filesystem injection; no accepted model/operator is patched.
   with patch.object(audit,'P',root),patch.object(audit,'read',side_effect=data.__getitem__):answer=audit.arithmetic()
  self.assertEqual(answer['checked_mean_interval_pairs'],114)
  self.assertLessEqual(answer['maximum_absolute_discrepancy'],2e-13)
 def test_audit_rejects_corrupt_scores(self):
  f=read('ACCEPTED_HAM_FIXTURES.json')[0];s=copy.deepcopy(f['step']);pop=f['before'];target=f['target']
  queries=copy.deepcopy(f['initial_queries'])
  for q in queries+s['query_records']:q['objective']='HAM'
  rec=dict(objective='HAM',steps=[s],populations=[pop,s['selected_records']],initial_queries=queries,initial_raw_mismatches=[q['raw_mismatch'] for q in queries],ground_truth=[dict(target=target,actual_change=False)],raw_losses=[s['B_raw'],s['L_raw']],penalized_losses=[s['B_pen'],s['L_pen']],raw_accuracies=[1-s['B_raw'],1-s['L_raw']],penalized_accuracies=[1-s['B_pen'],1-s['L_pen']],query_counts=dict(total=160))
  d={k:[v] for k,v in f['draws'].items()}
  self.assertEqual(audit_record(rec,d,[target],pop,expected_updates=1)['scores'],160)
  rec['steps'][0]['query_records'][33]['raw_mismatch']+=1
  with self.assertRaises(AssertionError):audit_record(rec,d,[target],pop,expected_updates=1)
 def test_operators_and_python36_syntax(self):
  self.assertEqual(verify_references(),12)
  for p in P.glob('*.py'):ast.parse(p.read_text(),filename=p.name,feature_version=(3,6))
  self.assertEqual(read('contract.json')['resources'],dict(cpus=1,memory_GiB=4,minutes=30))
def canon_json(x):return json.loads(json.dumps(x))
if __name__=='__main__':
 start=time.time();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Tests);result=unittest.TextTestRunner(verbosity=2).run(suite)
 save('TEST_STATUS.json',dict(status='PASS' if result.wasSuccessful() else 'FAIL',tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),elapsed_seconds=time.time()-start,fixture_accounting=dict(CALLS),new_production_draws=0,new_scientific_paths=0,objective_checks=dict(translated_block_states=256,strict_corner_neighbor_checks=8192),production_seeds_consumed=False))
 raise SystemExit(0 if result.wasSuccessful() else 1)
