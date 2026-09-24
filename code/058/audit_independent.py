"""Independent saved-score/operator reconstruction and 114-estimate arithmetic."""
import math,collections
from common import *
from raw_audit import audit_record,canon
from seed_design import verify_roster
from generators import build_targets
from accepted_inputs055 import extend_targets

def percentile(xs,p):
 a=p*(len(xs)-1);i=int(a);return (1-(a-i))*xs[i]+(a-i)*xs[min(i+1,len(xs)-1)]
def coefficients():
 cells=('HAM|Q_ZERO','HAM|Q_HALF','TRAP4|Q_ZERO','TRAP4|Q_HALF')
 cs={cells[i]:tuple(int(i==j) for j in range(4)) for i in range(4)}
 cs.update({'HAM|Q_HALF_MINUS_ZERO':(-1,1,0,0),'TRAP4|Q_HALF_MINUS_ZERO':(0,0,-1,1),'TRAP4_MINUS_HAM|Q_HALF_MINUS_ZERO':(1,-1,-1,1)})
 return cells,cs

def arithmetic():
 cells,coefs=coefficients();panel={}
 for row in rows(P/'TIME_SERIES.jsonl.gz'):
  coord=row['block'],row['replicate'],row['cell'];assert coord not in panel
  v={}
  for key,x in row['values'].items():
   assert len(x)==41
   if key.endswith('_POP'):v[key+'|U']=sum(x[1:])/40.;v[key+'|U40']=x[40]
   else:v[key+'|D40']=x[40]-x[0]
  assert len(v)==18;panel[coord]=v
 assert len(panel)==768
 weights=[collections.Counter(row) for row in read('BOOTSTRAP_INDICES.json')];est=read('ESTIMATES.json');worst=0.;n=0;verified=set()
 for group,c in coefs.items():
  for metric in panel[0,0,cells[0]]:
   if group.startswith('TRAP4_MINUS_HAM') and not metric.endswith('|D40'):continue
   bs=[sum(sum(c[j]*panel[b,r,cells[j]][metric] for j in range(4)) for r in range(8))/8 for b in range(24)]
   mean=sum(bs)/24.;draws=sorted(sum(bs[b]*count for b,count in w.items())/24 for w in weights);ci=[percentile(draws,p) for p in (.025,.975)];key=group+'|'+metric;q=est[key]
   err=max([abs(mean-q['mean'])]+[abs(x-y) for x,y in zip(ci,q['ci95'])]);assert err<=2e-13,(key,err);worst=max(worst,err);n+=1;verified.add(key)
 assert n==114 and verified==set(est)
 primary=est['TRAP4|Q_HALF_MINUS_ZERO|F_BG_EFFECT|D40'];lo,hi=primary['ci95'];a=read('ASSESSMENT.json')['decisions']
 assert a['direction']==('supports_positive' if lo>0 else 'contradicts_positive' if hi<0 else 'unresolved')
 assert a['benchmark']==('supports_exceeding_one_expected_descendant' if lo>1/32 else 'does_not_support_at_least_one_expected_descendant' if hi<1/32 else 'unresolved')
 return dict(checked_mean_interval_pairs=n,maximum_absolute_discrepancy=worst,tolerance=2e-13,arithmetic='Saved time series; explicit four-cell coefficients; bootstrap multiplicity weights; independent linear percentiles')

def uniform(genotypes,bg):
 return [(x,1 if bg=='H' else 2,i,(x,0,i)) for i,x in enumerate(genotypes)]
def rebase_reference(pop):return [(x,k,i,cache) for i,(x,k,fid,cache) in enumerate(pop)]
def raw_block():
 roots={(q['block'],q['replicate'],q['objective']):q for q in rows(P/'INITIAL_STATES.jsonl.gz')};res=states();assert len(roots)==384 and len(res)==768
 ds={s:keyed(s+'streams.jsonl.gz') for s in ('initial_','policy_','')};fresh={s:keyed(s+'fresh_probe_masks.jsonl.gz') for s in ('policy_','')};surv={s:keyed(s+'survival_streams.jsonl.gz') for s in ('policy_','')};initial=read('INITIAL_TARGETS.json')['blocks'];policy=read('POLICY_TARGETS.json')['HALF'];table=read('TARGET_TABLE.json');counts=collections.Counter()
 for folder in ('initial','policy','raw'):
  for row in rows(P/(folder+'/block00.jsonl.gz')):
   b,r,o=row['block'],row['replicate'],row['objective'];assert b==0;rec=row['record'];assert rec['objective']==o;kw={};bg=row.get('background')
   if folder=='initial':
    d=ds['initial_'][b,r]['draws'];marked=d['labels'][0];pop=[(0,int(i==marked),i,(0,0,i) if i==marked else None) for i in range(32)];targets=initial[b]['targets'];assert [x[0] for x in rec['populations'][-1]]==roots[b,r,o]['genotypes']
   elif folder=='policy':
    d=ds['policy_'][b,r]['draws'];pop=uniform(roots[b,r,o]['genotypes'],bg);targets=policy[b]['targets'];kw=dict(fresh=fresh['policy_'][b,r]['fresh'],survival=surv['policy_'][b,r]['survival']);assert rec['populations'][-1]==res[b,r,o,bg]['population']
   else:
    d=ds[''][b,r]['draws'];state=res[b,r,o,bg];pop=rebase_reference(state['population']);cfg=row['configuration'];slot=None if cfg.endswith('STAY') else d['labels'][int(cfg[-1])]
    pop=[(x,3-k if i==slot else k,fid,cache) for i,(x,k,fid,cache) in enumerate(pop)];targets=table['Q_'+row['future']][b]['targets'];kw=dict(fresh=fresh['policy_'][b,r]['fresh']+fresh[''][b,r]['fresh'],survival=surv[''][b,r]['survival'],absolute_start=40)
    assert rec['boundary_previous_target']==state['last_preparation_target'] and rec['boundary_current_target']==targets[0] and rec['boundary_actual_change']==(targets[0]!=state['last_preparation_target'])
    assert row['founder_ids']==d['labels'][:2] and row['rare_founder_id']==slot and row['preparation_founder_map']==state['founder_rebase_map']
   counts.update(audit_record(rec,d,targets,pop,**kw));counts[folder+'_paths']+=1
 assert counts['initial_paths']==16 and counts['policy_paths']==32 and counts['raw_paths']==192 and counts['paths']==240 and counts['scores']==1236480
 for (b,r,o,bg),state in res.items():
  assert canon(rebase_reference(state['population']))==canon(state['rebased_population'])
  mapping=[dict(current_slot=i,preparation_founder=x[2],genotype=x[0],policy=x[1],cache=x[3]) for i,x in enumerate(state['population'])]
  assert mapping==state['founder_rebase_map'] and state['last_two_preparation_targets']==policy[b]['targets'][-2:]
 return dict(counts)

def inputs():
 verify_manifest('SOURCE_SHA256SUMS');verify_roster(read('SEEDS.json'),read('PRIOR_SEED_INVENTORY.json')['integers']);check_stage('INPUT');check_stage('INITIAL');check_stage('RESIDENT')
 assert read('DESIGN_FREEZE.json')['freeze_unix']<read('INPUT_FREEZE.json')['freeze_unix']<read('INITIAL_STARTED.json')['start']<read('INITIAL_FREEZE.json')['freeze_unix']<read('POLICY_STARTED.json')['start']<read('RESIDENT_FREEZE.json')['freeze_unix']<read('TRANSFER_STARTED.json')['start_unix']
 hs=read('POLICY_TARGETS.json');pd=read('POLICY_TARGET_DRAWS.json')['blocks'];cd=read('CONTINUATION_TARGET_DRAWS.json')['blocks'];table=read('TARGET_TABLE.json');it=read('INITIAL_TARGETS.json')['blocks'];assert set(hs)=={'HALF'} and set(table)=={'Q_ZERO','Q_HALF'}
 for b in range(24):
  assert it[b]['targets']==pd[b]['first_pair']*20
  history=build_targets(pd[b]['first_pair'],pd[b]['innovations'],pd[b]['copy_bits'],'HALF');assert history==hs['HALF'][b]['targets']
  for q in ('ZERO','HALF'):
   row=table['Q_'+q][b];assert row['targets']==extend_targets(history,cd[b]['innovations'],cd[b]['copy_bits'],q);assert row['preparation_terminal_targets']==history[-2:]
 assert read('INITIAL_BUDGET.json')['paths']==384 and read('POLICY_BUDGET.json')['paths']==768 and read('BUDGET.json')['new_paths']==4608
 assert read('INITIAL_BUDGET.json')['total_objective_calls']+read('POLICY_BUDGET.json')['total_objective_calls']+read('BUDGET.json')['transfer_objective_calls']==29675520
 return dict(total_paths=5760,total_objective_calls=29675520,paired_inputs_exclude_objective=True,stage_freezes_in_order=True)

def preparation_declines():
 n=0
 with (P/'PREPARATION_DECLINES.jsonl').open('w') as out:
  for stage in ('initial','policy'):
   for b in range(24):
    for row in rows(P/(stage+'/block%02d.jsonl.gz'%b)):
     rec=row['record']
     for g,s in enumerate(rec['steps']):
      decline=rec['raw_losses'][g+1]>rec['raw_losses'][g]
      if decline or s['S_raw']<0:
       out.write(json.dumps(dict(stage=stage,block=b,replicate=row['replicate'],objective=row['objective'],background=row.get('background'),update=g+1,selected_state_declined=decline,S_raw=s['S_raw'],W_raw=s['W_raw']))+'\n');n+=1
 return n

def main():
 a=inputs();b=raw_block();c=arithmetic();d=preparation_declines()
 save('INDEPENDENT_AUDIT.json',dict(status='PASS',inputs=a,raw_block=0,raw_checks=b,statistics=c,preparation_declines=d,new_scientific_paths=0,new_scientific_objective_calls=0,recorded_score_reconstructions=b['scores'],new_random_draws=0))
 print(json.dumps(c))
if __name__=='__main__':main()
