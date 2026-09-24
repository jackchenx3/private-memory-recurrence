"""One deterministic validation of new records; reuse authenticated diagonals without rerunning."""
import math,struct,collections,gzip,csv,time
from common import *
from analysis import *
from model import rebase,substitute
from lineages import extract,time_series

def sign(x):return 'positive' if x>0 else 'negative' if x<0 else 'zero'
def ulp(a,b):return abs(struct.unpack('>Q',struct.pack('>d',a))[0]-struct.unpack('>Q',struct.pack('>d',b))[0])
def quantile(xs,p):
 ys=sorted(xs);x=(len(ys)-1)*p;i=int(x);return ys[i]+(ys[min(i+1,len(ys)-1)]-ys[i])*(x-i)
def interval(xs,indices):
 mean=sum(xs)/24.;rep=[sum(xs[i] for i in row)/24. for row in indices];return mean,[quantile(rep,.025),quantile(rep,.975)]

def validate(row,st,streams,fresh,surv,table,counters):
 b,r,p,q,cfg,bg=row['block'],row['replicate'],row['preparation'],row['future'],row['configuration'],row['background'];rec=row['record'];source=st[b,r,p,bg];lab=streams[b,r]['draws']['labels'];tt=table['P_'+p+'_Q_'+q][b];pop,prov=rebase(source['population']);slot=None if cfg.endswith('STAY') else lab[int(cfg[-1])]
 assert row['founder_ids']==lab[:2] and row['rare_founder_id']==slot and row['preparation_founder_map']==prov==source['founder_rebase_map']
 assert json.loads(json.dumps(substitute(pop,bg,slot)))==rec['populations'][0]
 assert rec['absolute_start']==40 and rec['boundary_previous_target']==source['last_preparation_target']==tt['boundary_previous_target'] and rec['boundary_current_target']==tt['targets'][0] and rec['boundary_actual_change']==tt['boundary_actual_change']
 assert rec['query_counts']==dict(initial=32,candidates=5120,total=5152,extra_diagnostic_loss_calls=0)
 assert rec['raw_losses']==rec['penalized_losses'] and rec['raw_accuracies']==[1-x for x in rec['raw_losses']]
 assert rec['raw_losses'][0]==sum(rec['initial_raw_mismatches'])/1024
 assert [x['genotype'] for x in rec['initial_queries']]==[x[0] for x in rec['populations'][0]]
 d=streams[b,r]['draws'];fs=rec['frequencies']
 for i,step in enumerate(rec['steps']):
  before,after=rec['populations'][i:i+2];truth=rec['ground_truth'][i];assert truth==dict(target=tt['targets'][i],actual_change=i>0 and tt['targets'][i]!=tt['targets'][i-1],absolute_update=40+i)
  assert step['evaluator_calls']==128 and len(step['candidates'])==128 and sum(step['current_descendant_counts'])==32
  assert after==step['selected_records']==[step['candidates'][j] for j in step['selected_indices']]
  assert step['ties']==d['ties'][i] and step['fresh_probe_masks']==fresh[b,r]['fresh'][i]
  assert step['survival_integers']==surv[b,r]['survival'][i]['k'] and step['survival_uniforms']==surv[b,r]['survival'][i]['u']
  assert step['h_retrieval_use']==[x[1]==1 for x in before] and step['f_fresh_use']==[x[1]==2 for x in before]
  assert step['candidate_raw_mismatches']==step['candidate_penalized_mismatches'] and step['persistent_cache_count']==32
  for j,c in enumerate(step['candidates']):
   parent=j%32;assert c[1:3]==before[parent][1:3] and c[3]==(before[j][3] if j<32 else [before[parent][0],40+i,parent])
   assert step['query_records'][j]==dict(candidate_index=j,genotype=c[0],raw_mismatch=step['candidate_raw_mismatches'][j])
   if j<32:assert c==before[j]
   elif j<64:assert c[0]==(before[parent][3][0] if before[parent][1]==1 else before[parent][0]^fresh[b,r]['fresh'][i][parent])
   elif j<96:assert c[0]==before[parent][0]^d['scout'][i][parent]
  for parent,donor in enumerate(step['donor_choices']):
   win=min(donor['candidate_indices'],key=lambda j:(step['candidate_raw_mismatches'][j],step['ties'][j],j));assert donor['winner_index']==win
   assert step['candidates'][96+parent][0]==step['candidates'][win][0]^d['local'][i][parent]
  keys=[-math.log(u)*float(1<<s) for u,s in zip(step['survival_uniforms'],step['candidate_raw_mismatches'])];ds=[ulp(a,b) for a,b in zip(keys,step['race_keys'])];assert max(ds)<=2
  assert step['selected_indices']==sorted(range(128),key=lambda j:(keys[j],step['ties'][j],j))[:32]==sorted(range(128),key=lambda j:(step['race_keys'][j],step['ties'][j],j))[:32]
  counters['clock_checks']+=128;counters['nonexact_clocks']+=sum(x>0 for x in ds);counters['max_ulp']=max(counters['max_ulp'],max(ds))
  assert step['L_raw']==rec['raw_losses'][i+1] and step['S_raw']==step['S_pen'] and rec['raw_losses'][i+1]-rec['raw_losses'][i]==step['W_raw']-step['S_raw']
  for role,k in [('H',1),('F',2)]:
   assert fs[role][i+1]==sum(x[1]==k for x in after)/32
   delta=sum((n-1)*(int(x[1]==k)-fs[role][i]) for n,x in zip(step['current_descendant_counts'],before))/32;assert delta==fs[role][i+1]-fs[role][i]
 return True

def main():
 assert not (P/'VALIDATION_CHECK.json').exists(),'Validation already completed; use recorded outputs'
 verify_manifest('SCIENCE_SHA256SUMS');verify_manifest('SOURCE_SHA256SUMS');verify_references();start=time.time()
 st=states();streams=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');surv=keyed('survival_streams.jsonl.gz');table=read('TARGET_TABLE.json');counters=collections.Counter();data=collections.defaultdict(dict);events=collections.defaultdict(collections.Counter);joints=collections.defaultdict(collections.Counter);timeline={};nnew=nold=0
 with (P/'PATH_METRICS.jsonl').open('w') as metricsout,(P/'FATES.jsonl').open('w') as fateout,(P/'DECLINES.jsonl').open('w') as declineout,gzip.open(P/'TIME_SERIES.jsonl.gz','wt') as tsout:
  for b in range(24):
   blockrows=collections.defaultdict(dict);tls=collections.defaultdict(dict)
   for kind,filename in [('new',P/('raw/block%02d.jsonl.gz'%b)),('reused',SOURCE/('raw/block%02d.jsonl.gz'%b))]:
    for original in rows(filename):
     row=original
     if kind=='reused':
      if row['geometry'] not in LAWS:continue
      row=dict(row,preparation=row['geometry'],future=row['geometry']);nold+=1
     else:validate(row,st,streams,fresh,surv,table,counters);nnew+=1
     r,p,q,cfg,bg=row['replicate'],row['preparation'],row['future'],row['configuration'],row['background'];cell='P_'+p+'_Q_'+q;ident=dict(block=b,replicate=r,cell=cell,configuration=cfg,source=kind);rec=row['record'];freq,u=extract(rec,row['founder_ids'],cfg);assert freq==row['role_frequencies'];assert cfg not in blockrows[r,cell];blockrows[r,cell][cfg]=u;tls[r,cell][cfg]=dict(frequency=freq,accuracy=rec['raw_accuracies']);metricsout.write(json.dumps(dict(ident,values=u))+'\n')
     for role in (('H','F','RARE') if 'SWITCH' in cfg else ('p0','p1')):
      fs=freq[role];ep='extinct' if fs[-1]==0 else 'fixed' if fs[-1]==1 else 'polymorphic';key=cell+'|'+cfg+'|'+role;events[key][ep]+=1;events[key]['above_initial']+=int(fs[-1]>fs[0]);events[key]['below_initial']+=int(fs[-1]<fs[0]);times={name:next((i for i,x in enumerate(fs) if x==v),None) for name,v in [('first_extinction',0),('first_fixation',1)]};fateout.write(json.dumps(dict(ident,role=role,endpoint=ep,initial=fs[0],terminal=fs[-1],**times))+'\n')
     key=cell+'|'+cfg
     if 'SWITCH' in cfg:
      h,f=freq['H'][-1],freq['F'][-1];joints[key]['both_policies' if h and f else 'H_only' if h else 'F_only']+=1;majorfixed=freq[bg][-1]==1;nf=len(set(x[2] for x in rec['populations'][-1]));joints[key]['majority_fixed_multiple_founders']+=int(majorfixed and nf>1);joints[key]['majority_fixed_one_founder']+=int(majorfixed and nf==1)
     else:
      a,z=freq['p0'][-1],freq['p1'][-1];joints[key]['both_founders' if a and z else 'p0_only' if a else 'p1_only' if z else 'neither']+=1
     for i,step in enumerate(rec['steps']):
      declined=rec['raw_losses'][i+1]>rec['raw_losses'][i];negative=step['S_raw']<0
      if declined or negative:declineout.write(json.dumps(dict(ident,update=i+1,selected_state_declined=declined,S_raw=step['S_raw'],W_raw=step['W_raw']))+'\n');counters['decline_or_negative_selection_records']+=1
   assert len(blockrows)==32
   for (r,cell),cfgs in blockrows.items():
    assert set(cfgs)==set(CONFIGS);data[b,r][cell]=base_estimands(cfgs);timeline[b,r,cell]=time_series(tls[r,cell]);tsout.write(json.dumps(dict(block=b,replicate=r,cell=cell,values=timeline[b,r,cell]))+'\n')
    for i in (0,1):data[b,r].setdefault('orientation'+str(i),{})[cell]=orientation(cfgs,i)
 assert nnew==nold==2304 and len(data)==192 and counters['clock_checks']==11796480
 blockcols=collections.defaultdict(lambda:collections.defaultdict(list));signs=collections.defaultdict(collections.Counter);osigns=collections.defaultdict(collections.Counter);neg=disagreements=0
 with (P/'PAIRED_METRICS.jsonl').open('w') as out,(P/'ORIENTATION_METRICS.jsonl').open('w') as oo,(P/'NEGATIVE_OUTCOMES.jsonl').open('w') as no,(P/'TRANSMISSION_ACCURACY_DISAGREEMENTS.jsonl').open('w') as do:
  for (b,r),cells in sorted(data.items()):
   vs=combine({k:cells[k] for k in CELLS});out.write(json.dumps(dict(block=b,replicate=r,values=vs))+'\n')
   ovs=[combine(cells['orientation'+str(i)]) for i in (0,1)]
   for i,ov in enumerate(ovs):
    oo.write(json.dumps(dict(block=b,replicate=r,placement=i,values=ov))+'\n')
    for k,x in ov.items():osigns[str(i)+'|'+k][sign(x)]+=1
   for k,x in vs.items():
    assert abs(x-(ovs[0][k]+ovs[1][k])/2)<2e-15;blockcols[b][k].append(x);signs[k][sign(x)]+=1
    if x<0:no.write(json.dumps(dict(block=b,replicate=r,key=k,value=x))+'\n');neg+=1
   for g in GROUPS:
    for bg in ('F','H'):
     f=vs[g+'|'+bg+'_BG_EFFECT|D40']
     for m in ('U','U40'):
      a=vs[g+'|'+bg+'_BG_EFFECT_POP|'+m]
      if sign(f)!=sign(a):do.write(json.dumps(dict(block=b,replicate=r,group=g,background=bg,population_metric=m,founder_effect=f,population_effect=a))+'\n');disagreements+=1
  blocks=[]
  for b,cols in sorted(blockcols.items()):
   assert len(cols)==162 and all(len(v)==8 for v in cols.values());blocks.append(dict(block=b,values={k:sum(v)/8 for k,v in cols.items()}))
 save('BLOCK_SUMMARIES.json',blocks);idx=read('source055_BOOTSTRAP_INDICES.json');assert len(idx)==2000 and all(len(x)==24 and all(type(i)==int and 0<=i<24 for i in x) for x in idx)
 estimates={}
 for k in read('METRIC_CATALOG.json')['keys']:
  xs=[b['values'][k] for b in blocks];mean,ci=interval(xs,idx);cl='positive' if ci[0]>0 else 'negative' if ci[1]<0 else 'observed_exact_zero' if all(x==0 for x in xs) else 'unresolved';estimates[k]=dict(mean=mean,ci95=ci,classification=cl,mean_percentage_points=mean*100,ci95_percentage_points=[x*100 for x in ci],expected_terminal_descendant_difference=mean*32 if k.endswith('|D40') else None,paired_signs=signs[k],block_signs=dict(collections.Counter(sign(x) for x in xs)))
 save('ESTIMATES.json',estimates);save('ORIENTATION_SIGNS.json',osigns);save('FATE_COUNTS.json',events);save('JOINT_ENDPOINT_COUNTS.json',joints)
 with (P/'ESTIMATES.csv').open('w') as f:
  w=csv.writer(f);w.writerow(['key','mean','ci_low','ci_high','mean_pp','low_pp','high_pp','classification','mean_descendant_difference'])
  for k,q in estimates.items():w.writerow([k,q['mean']]+q['ci95']+[q['mean_percentage_points']]+q['ci95_percentage_points']+[q['classification'],q['expected_terminal_descendant_difference']])
 save('ASSESSMENT.json',dict(primary=PRIMARY,estimate=estimates[PRIMARY],prediction='positive',supported=estimates[PRIMARY]['classification']=='positive',contradicted=estimates[PRIMARY]['classification']=='negative',interval_scope='approximate pointwise',interaction_direction_not_predicted=True,exploratory_selected_after055=True,independent_replication=False))
 save('VALIDATION_CHECK.json',dict(status='PASS',new_paths=nnew,reused_paths=nold,source_prepared_states=768,new_objective_calls=0,new_draws=0,intervals=162,structural_zeros=0,negative_paired_records=neg,transmission_accuracy_disagreements=disagreements,checks=counters,clock_tolerance_ulp=2,survivor_indices_and_order_exact=True,elapsed_seconds=time.time()-start))
 print(json.dumps(read('ASSESSMENT.json')))
if __name__=='__main__':main()
