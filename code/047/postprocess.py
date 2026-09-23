"""Local stored-output accounting only. No new objective evaluation or dynamics."""
import pathlib,json,gzip,collections,csv
from analysis import derive,RAW,FREQ
P=pathlib.Path(__file__).resolve().parent

def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def sign(x):return 'positive' if x>0 else 'negative' if x<0 else 'zero'
def arms(v,a,g,pol,ms):
 abundances=('RESIDENT40','NAIVE') if a=='RESIDENT40_MINUS_NAIVE' else (a,);regs=('RECUR','IID') if g=='RECUR_MINUS_IID' else (g,);ps=pol.split('-');return {ab+'|'+r+'|'+p:{m:v[ab+'|'+r+'|'+p+'|'+m] for m in ms} for ab in abundances for r in regs for p in ps}
def main():
 groups=collections.defaultdict(dict);trajectories=collections.defaultdict(lambda:{k:[0.]*41 for k in ('raw_accuracy','penalized_accuracy','frequency')});ops=collections.defaultdict(collections.Counter);donors=collections.defaultdict(collections.Counter);diagnostics=collections.defaultdict(collections.Counter);account=collections.defaultdict(lambda:collections.Counter());events=collections.defaultdict(collections.Counter);n=0;declines=0;maxerr=0.;surviving_blocks=collections.defaultdict(set);event_paths=collections.defaultdict(list);fresh_counts=collections.defaultdict(lambda:[collections.Counter() for _ in range(40)])
 with (P/'STATE_DECLINES.jsonl').open('w') as dout,(P/'TYPE_EVENTS.jsonl').open('w') as eout,(P/'SEQUENCE_UTILITIES.jsonl').open('w') as uout:
  for b in range(24):
   with gzip.open(P/('raw/block%02d.jsonl.gz'%b),'rt') as src:
    for line in src:
     row=json.loads(line);r=row['record'];g,pol,rep=row['geometry'],row['policy'],row['replicate'];a=row['abundance'];gp=a+'|'+g+'|'+pol;ident=dict(block=b,replicate=rep,abundance=a,geometry=g,policy=pol);n+=1;v=r['utilities'];groups[b,rep].update({gp+'|'+m:x for m,x in v.items()});uout.write(json.dumps(dict(ident,utilities=v))+'\n');f=r['frequencies']
     for key,data in [('raw_accuracy',r['raw_accuracies']),('penalized_accuracy',r['penalized_accuracies']),('frequency',f)]:
      for j,x in enumerate(data):trajectories[gp][key][j]+=x/192
     event={name:next((j for j,x in enumerate(f) if x==value),None) for name,value in [('extinction',0),('fixation',1)]};endpoint='extinct' if f[-1]==0 else 'fixed' if f[-1]==1 else 'polymorphic';extra=dict(endpoint=endpoint,endpoint_survives=f[-1]>0,endpoint_above_initial=f[-1]>f[0],maximum_carrier_count=int(32*max(f)),first_maximum_update=f.index(max(f)),initial_fraction=f[0],endpoint_fraction=f[-1]);eout.write(json.dumps(dict(ident,**dict(event,**extra)))+'\n');events[gp]['endpoint_'+endpoint]+=1;events[gp]['endpoint_survives']+=int(f[-1]>0);events[gp]['endpoint_above_initial']+=int(f[-1]>f[0]);event_paths[gp].append(dict(ident,**dict(event,**extra)))
     if a in ('RESIDENT40','NAIVE'):
      surviving_blocks[gp]
      if f[-1]>0:surviving_blocks[gp].add(b)
     for name,t in event.items():events[gp][name+'_observed' if t is not None else name+'_missing']+=1
     for j,s in enumerate(r['steps'],1):
      assert sum(s['current_descendant_counts'])==32 and s['frequency_term']==f[j]-f[j-1];assert s['persistent_cache_count']==32*f[j];assert all(s['candidates'][i][1:3]==r['populations'][j-1][i%32][1:3] for i in range(128));assert s['S_pen']>=0;cost=int(pol.endswith('C1'));assert s['S_pen']==s['S_raw']+cost*(f[j-1]-f[j])/32
      if f[j-1] in (0,1):assert f[j]==f[j-1]
      if pol.startswith('NOVEL'):
       q=fresh_counts[gp][j-1];q['states']+=1;q['recipient_slots']+=32;q['carrier_fresh_probe_uses']+=int(32*f[j-1]);q['noncarrier_parent_probe_uses']+=int(32*(1-f[j-1]));q['extinct_states']+=int(f[j-1]==0);q['fixed_states']+=int(f[j-1]==1);q['polymorphic_states']+=int(0<f[j-1]<1);assert s['fresh_probe_use']==[bool(p[1]) for p in r['populations'][j-1]];assert not any(s['probe_access'])
      for x in s['sources']:ops[gp]['proposed_'+x['family']]+=1
      for x in s['selected_sources']:ops[gp]['selected_'+x['family']]+=1
      for d in s['donor_choices']:donors[gp][d['winner_family']]+=1
      for key in ('B_raw','W_raw','S_raw','L_raw','B_pen','W_pen','S_pen','L_pen','persistent_cache_count'):account[gp][key]+=s[key]/7680
      for key in ('S_raw','S_pen','W_raw','W_pen'):diagnostics[gp][key+'_'+sign(s[key])]+=1
      if r['penalized_accuracies'][j]<0:diagnostics[gp]['negative_penalized_accuracy']+=1
      bad=[]
      for suffix,ls in [('raw',r['raw_losses']),('pen',r['penalized_losses'])]:
       assert ls[j]-ls[j-1]==s['W_'+suffix]-s['S_'+suffix]
       if ls[j]>ls[j-1]:bad.append(suffix);diagnostics[gp][suffix+'_selected_state_declines']+=1
      if bad or s['S_raw']<0:dout.write(json.dumps(dict(ident,update=j,declining_losses=bad,S_raw=s['S_raw'],S_pen=s['S_pen'],W_raw=s['W_raw'],W_pen=s['W_pen'],f_before=f[j-1],f_after=f[j],raw_loss=r['raw_losses'][j],penalized_loss=r['penalized_losses'][j]))+'\n');declines+=1
     for suffix,ls in [('raw',r['raw_losses']),('pen',r['penalized_losses'])]:
      assert ls[0]+sum(s['W_'+suffix]-s['S_'+suffix] for s in r['steps'])==ls[-1];err=abs(ls[0]+sum((40-i)*(s['W_'+suffix]-s['S_'+suffix])/40 for i,s in enumerate(r['steps']))-sum(ls[1:])/40);maxerr=max(maxerr,err);assert err<2e-15
 assert n==4608 and len(groups)==192
 counts=collections.defaultdict(collections.Counter);negative=disagreements=0
 with (P/'NEGATIVE_RECORDS.jsonl').open('w') as neg,(P/'ENDPOINT_DISAGREEMENTS.jsonl').open('w') as diff:
  for (b,rep),v in groups.items():
   derive(v)
   for k,x in v.items():
    counts[k][sign(x)]+=1;a,g,p,m=k.split('|')
    if x<0:neg.write(json.dumps(dict(block=b,replicate=rep,key=k,value=x,units='raw mismatch' if m=='MLOSS' else 'carrier frequency/change' if m in FREQ else 'raw accuracy',arms=arms(v,a,g,p,[m]),interpretation='negative sign; no generic favorability assigned'))+'\n');negative+=1
    endpoint='U40' if m in ('U0','U1','U') or m.startswith('E') else 'F40' if m in ('F0','F1','F') or m.startswith('FE') else None
    if endpoint and sign(x)!=sign(v[a+'|'+g+'|'+p+'|'+endpoint]):diff.write(json.dumps(dict(block=b,replicate=rep,key=k,value=x,endpoint=endpoint,endpoint_value=v[a+'|'+g+'|'+p+'|'+endpoint],arms=arms(v,a,g,p,[m,endpoint])))+'\n');disagreements+=1
 blocks=collections.defaultdict(collections.Counter)
 for line in (P/'BLOCK_SUMMARIES.jsonl').read_text().splitlines():
  for k,x in json.loads(line)['values'].items():blocks[k][sign(x)]+=1
 assert len(counts)==len(blocks)==1716
 save('INDIVIDUAL_SIGNS.json',counts);save('BLOCK_SIGNS.json',blocks);save('TRAJECTORY_MEANS.json',trajectories);save('OPERATION_COUNTS.json',ops);save('DONOR_COUNTS.json',donors);save('SELECTION_DIAGNOSTICS.json',diagnostics);save('OBSERVED_ACCOUNTING.json',account);save('TYPE_EVENT_COUNTS.json',events)
 values=json.loads((P/'summary.json').read_text())['values'];crossings={}
 for k,q in values.items():
  a,g,p,m=k.split('|')
  if m not in ('U','F'):continue
  prefix0='E' if m=='U' else 'FE';ys=[values[a+'|'+g+'|'+p+'|'+prefix0+str(i)]['mean'] for i in range(1,9)];ref=0 if m=='U' else values[a+'|'+g+'|'+p+'|F0']['mean'];zs=[x-ref for x in ys];nz=[(i+1,sign(x)) for i,x in enumerate(zs) if x!=0];cross=[dict(left_window=a,right_window=b,from_sign=sa,to_sign=sb) for (a,sa),(b,sb) in zip(nz,nz[1:]) if sa!=sb];crossings[k]=dict(window_means=ys,reference=ref,reference_meaning='zero accuracy/contrast' if m=='U' else 'initial frequency or initial frequency contrast; descriptive subtraction only',observed_crossings=cross,no_observed_crossing=not cross,exact_reference_windows=[i+1 for i,x in enumerate(zs) if x==0])
 save('WINDOW_CROSSINGS.json',crossings);save('FRESH_PROBE_COUNTS.json',dict(per_update=fresh_counts,per_group={g:dict(sum(rows,collections.Counter())) for g,rows in fresh_counts.items()},denominators='Each NOVEL group192paths x40updates x32slots; all extinct/fixed states retained. Carrier slots use frozen masks including zero/duplicate masks; noncarrier slots use current genotype.'))
 bounds={g:dict(event_blocks=len(bs),block_event_indicators=[int(b in bs) for b in range(24)],independent_units=24,continuations_per_block=8,zero_event_bound_applicable=len(bs)==0,upper95=1-.05**(1/24.) if not bs else None,unit='probability a fresh eight-continuation block has any endpoint-surviving path',assumption='24 independent identically designed blocks',not_per_lineage_probability=True,not_mean_frequency_interval=True) for g,bs in surviving_blocks.items()};assert len(bounds)==24;save('RARE_BLOCK_EVENTS.json',bounds);save('ALL_PATH_EVENT_SUMMARIES.json',event_paths)
 ratios={g:dict(ratio=q['mean']/values[g[:-3]+'F0']['mean'],ci95=[x/values[g[:-3]+'F0']['mean'] for x in q['ci95']],same_evidence=True) for g,q in values.items() if g.endswith('|F40') and g.split('|')[0] in ('NAIVE','RESIDENT40') and g.split('|')[1] in ('IID','RECUR') and '-' not in g.split('|')[2]};assert len(ratios)==24;save('ENDPOINT_INITIAL_RATIOS.json',ratios)
 with (P/'COMPLETE_OUTCOMES.csv').open('w') as out:
  w=csv.writer(out);w.writerow(['key','mean','ci_low','ci_high','classification','interpretation','individual_positive','individual_negative','individual_zero','block_positive','block_negative','block_zero'])
  for k,q in sorted(values.items()):w.writerow([k,q['mean']]+q['ci95']+[q['zero_classification'],q['interpretation']]+[counts[k][s] for s in ('positive','negative','zero')]+[blocks[k][s] for s in ('positive','negative','zero')])
 save('POSTPROCESS_CHECKS.json',dict(status='PASS',new_paths=4608,old_paths=0,records=1716,negative_records=negative,endpoint_disagreements=disagreements,decline_records=declines,max_weighted_telescoping_residual=maxerr,extra_objective_calls=0));print(json.dumps(json.loads((P/'POSTPROCESS_CHECKS.json').read_text())))
if __name__=='__main__':main()
