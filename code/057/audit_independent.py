"""Independent arithmetic from saved time series and prospectively selected raw block0."""
import math,struct,collections
from common import *
from model import all_policy,rebase
from preparation_model import initial as initial052
from seed_design import verify_roster
from generators import build_targets
from accepted_inputs055 import extend_targets

def bits(a,b):return abs(struct.unpack('>Q',struct.pack('>d',a))[0]-struct.unpack('>Q',struct.pack('>d',b))[0])
def percentile(sorted_values,p):
 x=p*(len(sorted_values)-1);lo=math.floor(x);hi=math.ceil(x);w=x-lo;return (1-w)*sorted_values[lo]+w*sorted_values[hi]
def arithmetic():
 cells=('P_ZERO_Q_ZERO','P_ZERO_Q_HALF','P_HALF_Q_ZERO','P_HALF_Q_HALF')
 coeffs={cells[i]:tuple(int(i==j) for j in range(4)) for i in range(4)}
 coeffs.update(Q_HALF_MINUS_ZERO_AT_P_ZERO=(-1,1,0,0),Q_HALF_MINUS_ZERO_AT_P_HALF=(0,0,-1,1),P_HALF_MINUS_ZERO_AT_Q_ZERO=(-1,0,1,0),P_HALF_MINUS_ZERO_AT_Q_HALF=(0,-1,0,1),INTERACTION=(1,-1,-1,1))
 panel={}
 for row in rows(P/'TIME_SERIES.jsonl.gz'):
  coord=row['block'],row['replicate'],row['cell'];assert coord not in panel
  v={}
  for key,x in row['values'].items():
   assert len(x)==41
   if key.endswith('_POP'):v[key+'|U']=sum(x[1:])/40.;v[key+'|U40']=x[40]
   else:v[key+'|D40']=x[40]-x[0]
  assert len(v)==18;panel[coord]=v
 assert len(panel)==768
 idx=read('BOOTSTRAP_INDICES.json');weights=[collections.Counter(row) for row in idx];est=read('ESTIMATES.json');worst=0.;near=[];n=0
 for group,coefs in coeffs.items():
  for metric in panel[0,0,cells[0]]:
   blockvalues=[sum(sum(coefs[j]*panel[b,r,cells[j]][metric] for j in range(4)) for r in range(8))/8 for b in range(24)]
   mean=sum(blockvalues)/24;draws=sorted(sum(blockvalues[b]*count for b,count in w.items())/24 for w in weights);ci=[percentile(draws,p) for p in (.025,.975)];q=est[group+'|'+metric]
   err=max(abs(mean-q['mean']),*(abs(x-y) for x,y in zip(ci,q['ci95'])));assert err<=2e-13,(group,metric,err);worst=max(worst,err);n+=1
   if min(abs(x) for x in ci)<2e-13:near.append(group+'|'+metric)
   else:assert q['classification']==('positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'unresolved')
 assert n==162
 return dict(checked_mean_interval_pairs=n,maximum_absolute_discrepancy=worst,tolerance=2e-13,arithmetic='Time-series-derived endpoints, explicit factorial coefficients, bootstrap multiplicity weights, weighted linear percentiles',near_zero_classification_boundaries=near)

def audit_record(rec,targets,d,kind,fresh=None,survival=None):
 assert rec['query_counts']['total']==5152 and len(rec['populations'])==41 and rec['raw_losses']==rec['penalized_losses'];clocks=0
 for t,s in enumerate(rec['steps']):
  before,after=rec['populations'][t:t+2];pool=s['candidates'];assert len(pool)==128 and s['evaluator_calls']==128;assert rec['ground_truth'][t]['target']==targets[t]
  assert s['ties']==d['ties'][t] and s['candidate_raw_mismatches']==s['candidate_penalized_mismatches'];assert pool[:32]==before
  for j,c in enumerate(pool):
   k=j%32;assert c[1:3]==before[k][1:3];assert c[3]==(before[j][3] if j<32 else ([before[k][0],t,k] if before[k][1] else None));assert s['query_records'][j]==dict(candidate_index=j,genotype=c[0],raw_mismatch=s['candidate_raw_mismatches'][j])
   if 32<=j<64:assert c[0]==(before[k][0] if kind=='initial' else before[k][3][0] if before[k][1]==1 else before[k][0]^fresh[t][k])
   if 64<=j<96:assert c[0]==before[k][0]^d['scout'][t][k]
  for k,donor in enumerate(s['donor_choices']):
   win=min(donor['candidate_indices'],key=lambda j:(s['candidate_raw_mismatches'][j],s['ties'][j],j));assert win==donor['winner_index'];assert pool[96+k][0]==pool[win][0]^d['local'][t][k]
  if kind=='initial':sel=sorted(range(128),key=lambda j:(s['candidate_raw_mismatches'][j],s['ties'][j],j))[:32]
  else:
   assert s['fresh_probe_masks']==fresh[t] and s['survival_integers']==survival[t]['k'] and s['survival_uniforms']==survival[t]['u'];keys=[-math.log(u)*float(1<<score) for u,score in zip(s['survival_uniforms'],s['candidate_raw_mismatches'])];assert max(bits(x,y) for x,y in zip(keys,s['race_keys']))<=2;sel=sorted(range(128),key=lambda j:(keys[j],s['ties'][j],j))[:32];clocks+=128
  assert sel==s['selected_indices'];assert after==s['selected_records']==[pool[j] for j in sel]
  assert rec['raw_losses'][t+1]==s['L_raw'] and rec['raw_losses'][t+1]-rec['raw_losses'][t]==s['W_raw']-s['S_raw']
 return clocks

def preparations():
 roots=keyed('INITIAL_STATES.jsonl.gz');res=states();assert len(roots)==192 and len(res)==768
 ds=keyed('initial_streams.jsonl.gz');it=read('INITIAL_TARGETS.json')['blocks'];n=0
 for q in rows(P/'initial/block00.jsonl.gz'):
  b,r=q['block'],q['replicate'];rec=q['record'];assert b==0;assert rec['populations'][0]==json.loads(json.dumps(initial052('SHAM_C0',ds[b,r]['draws']['labels'])));assert all(x[0]==0 for x in rec['populations'][0]);assert [x[0] for x in rec['populations'][-1]]==roots[b,r]['genotypes'];audit_record(rec,it[b]['targets'],ds[b,r]['draws'],'initial');n+=1
 assert n==8
 pd=keyed('policy_streams.jsonl.gz');pf=keyed('policy_fresh_probe_masks.jsonl.gz');ps=keyed('policy_survival_streams.jsonl.gz');targets=read('POLICY_TARGETS.json');m=clocks=0
 for q in rows(P/'policy/block00.jsonl.gz'):
  b,r,p,bg=q['block'],q['replicate'],q['geometry'],q['background'];rec=q['record'];assert b==0;assert rec['populations'][0]==json.loads(json.dumps(all_policy(roots[b,r]['genotypes'],bg)));state=res[b,r,p,bg];assert rec['populations'][-1]==state['population'];pop,mapping=rebase(state['population']);assert json.loads(json.dumps(pop))==state['rebased_population'] and mapping==state['founder_rebase_map'];clocks+=audit_record(rec,targets[p][b]['targets'],pd[b,r]['draws'],'policy',pf[b,r]['fresh'],ps[b,r]['survival']);m+=1
 assert m==32
 # All-state provenance and coverage checks do not rerun any trajectory.
 for (b,r,p,bg),q in res.items():
  pop,mapping=rebase(q['population']);assert json.loads(json.dumps(pop))==q['rebased_population'] and mapping==q['founder_rebase_map'];assert q['last_two_preparation_targets']==targets[p][b]['targets'][-2:]
 return dict(initial_paths_raw_audited=n,policy_paths_raw_audited=m,policy_clock_checks=clocks,all_initial_states=192,all_policy_states=768,unfiltered=True)

def input_checks():
 verify_roster(read('SEEDS.json'),read('PRIOR_SEED_INVENTORY.json')['integers']);check_stage('INPUT');check_stage('INITIAL');check_stage('RESIDENT')
 assert read('INPUT_FREEZE.json')['freeze_unix']<read('INITIAL_STARTED.json')['start']<read('INITIAL_FREEZE.json')['freeze_unix']<read('POLICY_STARTED.json')['start']<read('RESIDENT_FREEZE.json')['freeze_unix']<read('TRANSFER_STARTED.json')['start_unix']
 histories=read('POLICY_TARGETS.json');pd=read('POLICY_TARGET_DRAWS.json')['blocks'];cd=read('CONTINUATION_TARGET_DRAWS.json')['blocks'];table=read('TARGET_TABLE.json');initial=read('INITIAL_TARGETS.json')['blocks']
 for b in range(24):
  assert initial[b]['targets']==pd[b]['first_pair']*20
  for p in ('ZERO','HALF'):
   h=build_targets(pd[b]['first_pair'],pd[b]['innovations'],pd[b]['copy_bits'],p);assert h==histories[p][b]['targets']
   for q in ('ZERO','HALF'):assert extend_targets(h,cd[b]['innovations'],cd[b]['copy_bits'],q)==table['P_'+p+'_Q_'+q][b]['targets']
 assert read('INITIAL_BUDGET.json')['total_objective_calls']+read('POLICY_BUDGET.json')['total_objective_calls']+read('BUDGET.json')['transfer_objective_calls']==28686336
 return dict(seed_records=3193,all_stages_frozen_in_order=True,all_target_recursions_verified=True,total_scientific_paths=5568,total_objective_calls=28686336)

def main():
 a=input_checks();b=preparations();c=arithmetic();save('INDEPENDENT_AUDIT.json',dict(status='PASS',prospective_raw_audit_block=0,inputs=a,preparations=b,statistics=c,new_objective_calls=0,new_paths=0,new_random_draws=0));print(json.dumps(c))
if __name__=='__main__':main()
