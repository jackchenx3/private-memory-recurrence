"""Saved-output accounting only; no objective evaluation or random draws."""
import pathlib,json,gzip,collections,csv,math,struct
from analysis import *
from lineages import extract
P=pathlib.Path(__file__).resolve().parent

def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def sign(x):return 'positive' if x>0 else 'negative' if x<0 else 'zero'
def ulp(a,b):return abs(struct.unpack('>Q',struct.pack('>d',a))[0]-struct.unpack('>Q',struct.pack('>d',b))[0])
def bound(bs):return dict(event_blocks=len(bs),block_event_indicators=[int(b in bs) for b in range(24)],independent_units=24,continuations_per_block=8,zero_event_bound_applicable=len(bs)==0,upper95=1-.05**(1/24.) if not bs else None,unit='probability a fresh eight-continuation block has any endpoint-surviving path',assumption='24 independent identically designed blocks',not_per_lineage_probability=True,not_mean_frequency_interval=True)
def main():
 rows=collections.defaultdict(dict);traj=collections.defaultdict(lambda:{k:[0.]*41 for k in ('H','F','R','RARE','raw_accuracy','penalized_accuracy')});events=collections.defaultdict(collections.Counter);joint=collections.defaultdict(collections.Counter);bs=collections.defaultdict(set);diagnostics=collections.defaultdict(collections.Counter);ops=collections.defaultdict(collections.Counter);account=collections.defaultdict(collections.Counter);n=0;declines=0;maxerr=0;clocks=diffclocks=maxulp=0
 with (P/'CONFIGURATION_METRICS.jsonl').open('w') as mout,(P/'TYPE_EVENTS.jsonl').open('w') as eout,(P/'STATE_DECLINES.jsonl').open('w') as dout,(P/'JOINT_ENDPOINTS.jsonl').open('w') as jout:
  for block in range(24):
   with gzip.open(P/('raw/block%02d.jsonl.gz'%block),'rt') as src:
    for line in src:
     row=json.loads(line);rec=row['record'];g,c,cfg,rep=row['geometry'],row['cost'],row['configuration'],row['replicate'];cost=int(c[-1]);gp=g+'|'+c+'|'+cfg;ident=dict(block=block,replicate=rep,law=g,cost=c,configuration=cfg);freq,util=extract(rec,row['rare_founder_id'],cfg);assert freq==row['role_frequencies'];pf=rec['frequencies'];rows[block,rep][g,c,cfg]=util;n+=1;pen=rec['penalized_accuracies'];mout.write(json.dumps(dict(ident,utilities=util,penalized_accuracy=dict(initial=pen[0],mean=sum(pen[1:])/40,terminal=pen[-1])))+'\n')
     for k,data in dict(freq,raw_accuracy=rec['raw_accuracies'],penalized_accuracy=pen).items():
      for j,x in enumerate(data):traj[gp][k][j]+=x/192
     roles=('H','F','RARE')
     for role in roles:
      fs=freq[role];ep='extinct' if fs[-1]==0 else 'fixed' if fs[-1]==1 else 'polymorphic';times={name:next((i for i,x in enumerate(fs) if x==v),None) for name,v in [('extinction',0),('fixation',1)]};rk=gp+'|'+role;bs[rk];e=events[rk];e['endpoint_'+ep]+=1;e['endpoint_survives']+=int(fs[-1]>0);e['endpoint_above_initial']+=int(fs[-1]>fs[0]);
      for name,t in times.items():e[name+'_observed' if t is not None else name+'_missing']+=1
      if fs[-1]>0:bs[rk].add(block)
      eout.write(json.dumps(dict(ident,role=role,endpoint=ep,initial_fraction=fs[0],endpoint_fraction=fs[-1],maximum_count=int(32*max(fs)),first_maximum_update=fs.index(max(fs)),**times))+'\n')
     h,f=freq['H'][-1],freq['F'][-1];category='both_present' if h and f else 'H_only' if h else 'F_only';assert h+f==1;joint[gp][category]+=1;major='F' if cfg.startswith('LOW') else 'H';majorid=2 if major=='F' else 1;founders=sorted(set(q[2] for q in rec['populations'][-1] if q[1]==majorid));majorfixed=freq[major][-1]==1;joint[gp]['majority_policy_fixed_multiple_founders']+=int(majorfixed and len(founders)>1);joint[gp]['majority_policy_fixed_single_founder']+=int(majorfixed and len(founders)==1);joint[gp]['rare_founder_fixed']+=int(freq['RARE'][-1]==1)
     jout.write(json.dumps(dict(ident,category=category,majority_policy=major,majority_founders=founders,majority_policy_fixed=majorfixed,rare_founder_id=row['rare_founder_id']))+'\n')
     for j,st in enumerate(rec['steps'],1):
      assert st['evaluator_calls']==128 and sum(st['current_descendant_counts'])==32;before=rec['populations'][j-1];after=rec['populations'][j];assert all(sum(pf[k][i] for k in ('H','F','R'))==1 for i in (j-1,j));car0=pf['H'][j-1]+pf['F'][j-1];car1=pf['H'][j]+pf['F'][j];assert car0==car1==1;assert st['S_pen']==st['S_raw']+cost*(car0-car1)/32
      mapping={int(k):v for k,v in row['logical_roles'].items()}
      for role in ('H','F','R'):
       term=sum((d-1)*(int(mapping[q[1]]==role)-pf[role][j-1]) for d,q in zip(st['current_descendant_counts'],before))/32.;assert term==pf[role][j]-pf[role][j-1];assert pf[role][j-1]!=0 or pf[role][j]==0
      for role,fid in [('RARE',row['rare_founder_id'])]:
       term=sum((d-1)*(int(q[2]==fid)-freq[role][j-1]) for d,q in zip(st['current_descendant_counts'],before))/32.;assert term==freq[role][j]-freq[role][j-1];assert freq[role][j-1]!=0 or freq[role][j]==0
      assert st['persistent_cache_count']==32*car1
      for i,q in enumerate(st['candidates']):assert q[1:3]==before[i%32][1:3];assert q[3]==(before[i][3] if i<32 else ([before[i%32][0],j-1,i%32] if before[i%32][1] else None));assert st['candidate_penalized_mismatches'][i]==st['candidate_raw_mismatches'][i]+cost*int(q[1]!=0)
      if cfg in NEW:
       assert st['h_retrieval_use']==[q[1]==1 for q in before] and st['f_fresh_use']==[q[1]==2 for q in before]
      keys=[-math.log(u)*float(1<<s) for u,s in zip(st['survival_uniforms'],st['candidate_penalized_mismatches'])];saved=st['race_keys'];assert len(keys)==len(saved)==128 and all(x>0 and math.isfinite(x) for x in keys+saved);ds=[ulp(x,y) for x,y in zip(keys,saved)];assert max(ds)<=2;clocks+=128;diffclocks+=sum(x>0 for x in ds);maxulp=max(maxulp,max(ds));assert st['selected_indices']==sorted(range(128),key=lambda i:(saved[i],st['ties'][i],i))[:32]==sorted(range(128),key=lambda i:(keys[i],st['ties'][i],i))[:32]
      assert all(0<u<1 and u==(k+1)/(2**52+1) for k,u in zip(st['survival_integers'],st['survival_uniforms']))
      for d in st['donor_choices']:assert d['winner_index']==min(d['candidate_indices'],key=lambda i:(st['candidate_raw_mismatches'][i],st['ties'][i],i))
      for q in st['sources']:ops[gp]['proposed_'+q['family']]+=1
      for q in st['selected_sources']:ops[gp]['selected_'+q['family']]+=1
      for key in ('S_raw','S_pen','W_raw','W_pen'):diagnostics[gp][key+'_'+sign(st[key])]+=1
      for key in ('B_raw','W_raw','S_raw','L_raw','B_pen','W_pen','S_pen','L_pen'):account[gp][key]+=st[key]/7680
      diagnostics[gp]['negative_penalized_accuracy']+=int(pen[j]<0);bad=[]
      for suffix,loss in [('raw',rec['raw_losses']),('pen',rec['penalized_losses'])]:
       assert loss[j]-loss[j-1]==st['W_'+suffix]-st['S_'+suffix]
       if loss[j]>loss[j-1]:bad.append(suffix);diagnostics[gp][suffix+'_selected_state_declines']+=1
      if bad or st['S_raw']<0 or st['S_pen']<0:dout.write(json.dumps(dict(ident,update=j,declining_losses=bad,S_raw=st['S_raw'],S_pen=st['S_pen'],W_raw=st['W_raw'],W_pen=st['W_pen']))+'\n');declines+=1
     for suffix,loss in [('raw',rec['raw_losses']),('pen',rec['penalized_losses'])]:
      assert loss[0]+sum(st['W_'+suffix]-st['S_'+suffix] for st in rec['steps'])==loss[-1];err=abs(loss[0]+sum((40-i)*(st['W_'+suffix]-st['S_'+suffix])/40 for i,st in enumerate(rec['steps']))-sum(loss[1:])/40);maxerr=max(maxerr,err);assert err<2e-15
 assert n==2304 and len(rows)==192 and len(events)==36 and len(joint)==12
 save('TRAJECTORY_MEANS.json',traj);save('TYPE_EVENT_COUNTS.json',events);save('JOINT_ENDPOINT_COUNTS.json',joint);save('SELECTION_DIAGNOSTICS.json',diagnostics);save('OBSERVED_ACCOUNTING.json',account);save('OPERATION_COUNTS.json',ops);bounds={k:bound(b) for k,b in bs.items()};save('ROLE_BLOCK_EVENTS.json',bounds)
 save('FATE_GROUP_CHECK.json',dict(status='PASS',rare_founder_groups=12,policy_groups=24,resident_fate_groups=0,joint_groups=12))
 counts=collections.defaultdict(collections.Counter);negative=disagree=0;orient_counts=collections.defaultdict(collections.Counter)
 with (P/'PAIRED_METRICS.jsonl').open('w') as pout,(P/'ORIENTATION_METRICS.jsonl').open('w') as oout,(P/'NEGATIVE_RECORDS.jsonl').open('w') as nout,(P/'ENDPOINT_DISAGREEMENTS.jsonl').open('w') as eout:
  for (b,r),data in rows.items():
   v={};orows={}
   for g in LAWS:
    for c in COSTS:
     q={cfg:data[g,c,cfg] for cfg in CONFIGS};v.update({g+'|'+c+'|'+k:x for k,x in paired(q).items()})
     for ori in (0,1):
      ov=orientation(q,ori);orows[g,c,ori]=ov;oout.write(json.dumps(dict(block=b,replicate=r,law=g,cost=c,focal_position='p'+str(ori),paired_configurations=['LOW'+str(ori),'HIGH'+str(ori)],values=ov))+'\n')
      for k,x in ov.items():orient_counts[g+'|'+c+'|p'+str(ori)+'|'+k][sign(x)]+=1
   for g,h in LPAIRS:
    for c in COSTS:
     for ori in (0,1):
      ov={s+'|'+m:orows[g,c,ori][s+'|'+m]-orows[h,c,ori][s+'|'+m] for s in CROSS for m in FREQ};oout.write(json.dumps(dict(block=b,replicate=r,law=g+'_MINUS_'+h,cost=c,orientation=ori,values=ov))+'\n')
      for k,x in ov.items():orient_counts[g+'_MINUS_'+h+'|'+c+'|p'+str(ori)+'|'+k][sign(x)]+=1
   derive(v)
   for g in LAWS:
    for c in COSTS:
     for key in orows[g,c,0]:assert abs((orows[g,c,0][key]+orows[g,c,1][key])/2-v[g+'|'+c+'|'+key])<2e-15
   pout.write(json.dumps(dict(block=b,replicate=r,values=v))+'\n')
   for k,x in v.items():
    counts[k][sign(x)]+=1;g,c,s,m=k.split('|');ends='F40' if m in FREQ and m!='D40' else 'U40' if m in RAW and m!='MLOSS' else None
    if x<0:nout.write(json.dumps(dict(block=b,replicate=r,key=k,value=x,interpretation='negative signed value; MLOSS not a generic benefit sign'))+'\n');negative+=1
    if ends and sign(x)!=sign(v[g+'|'+c+'|'+s+'|'+ends]):eout.write(json.dumps(dict(block=b,replicate=r,key=k,value=x,endpoint=ends,endpoint_value=v[g+'|'+c+'|'+s+'|'+ends]))+'\n');disagree+=1
 blocksigns=collections.defaultdict(collections.Counter)
 for line in (P/'BLOCK_SUMMARIES.jsonl').read_text().splitlines():
  for k,x in json.loads(line)['values'].items():blocksigns[k][sign(x)]+=1
 assert len(counts)==len(blocksigns)==429;save('INDIVIDUAL_SIGNS.json',counts);save('BLOCK_SIGNS.json',blocksigns);save('ORIENTATION_SIGNS.json',orient_counts)
 v=json.loads((P/'summary.json').read_text())['values'];cross={}
 for k,q in v.items():
  g,c,s,m=k.split('|')
  if m not in ('F','U'):continue
  ms=['FE'+str(i) if m=='F' else 'E'+str(i) for i in range(1,9)];ys=[v[g+'|'+c+'|'+s+'|'+mm]['mean'] for mm in ms];ref=v[g+'|'+c+'|'+s+'|F0']['mean'] if m=='F' else 0.;nz=[(i+1,sign(y-ref)) for i,y in enumerate(ys) if y!=ref];cs=[dict(left_window=i,right_window=j,from_sign=a,to_sign=b) for (i,a),(j,b) in zip(nz,nz[1:]) if a!=b];cross[k]=dict(window_means=ys,reference=ref,observed_crossings=cs,no_observed_crossing=not cs,exact_reference_windows=[i+1 for i,y in enumerate(ys) if y==ref])
 assert len(cross)==33;save('WINDOW_CROSSINGS.json',cross)
 with (P/'COMPLETE_OUTCOMES.csv').open('w') as out:
  w=csv.writer(out);w.writerow(['key','mean','ci_low','ci_high','classification','path_positive','path_negative','path_zero','block_positive','block_negative','block_zero'])
  for k,q in sorted(v.items()):w.writerow([k,q['mean']]+q['ci95']+[q['zero_classification']]+[counts[k][s] for s in ('positive','negative','zero')]+[blocksigns[k][s] for s in ('positive','negative','zero')])
 assert clocks==11796480;save('PORTABLE_CLOCK_CHECK.json',dict(status='PASS',saved_clock_checks=clocks,non_bitwise_identical=diffclocks,maximum_ulp_difference=maxulp,tolerance_ulp=2,all_saved_and_recomputed_survivor_orders_exactly_equal=True,extra_objective_calls=0));save('POSTPROCESS_CHECKS.json',dict(status='PASS',new_paths=2304,old_paths=0,records=429,negative_records=negative,endpoint_disagreements=disagree,decline_records=declines,max_weighted_telescoping_residual=maxerr,extra_objective_calls=0));print(json.loads((P/'POSTPROCESS_CHECKS.json').read_text()))
if __name__=='__main__':main()
