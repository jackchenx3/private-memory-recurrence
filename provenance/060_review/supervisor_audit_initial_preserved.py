"""Supervisor reconstruction from saved data only; no imports from producer code."""
import gzip,json,math,hashlib,collections
from pathlib import Path
from datetime import datetime,timezone
P=Path('PRIVATE_WORKSPACE/you-are-responsible-for-implementing-the/outputs/measurement_error_v1')
OUT=Path('PRIVATE_WORKSPACE/review-the-scientific-conclusions-in-mnt/outputs/coordination/reviews/ORG-OBSERVATION-060-AUDIT.json')
def read(n):return json.loads((P/n).read_text())
def rows(n):
 with gzip.open(P/n,'rt') as f:
  for line in f:yield json.loads(line)
def keyed(n):return {(x['block'],x['replicate']):x for x in rows(n)}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def close(a,b):assert math.isclose(a,b,rel_tol=0,abs_tol=2e-14),(a,b)
def percentile(a,p):
 a=sorted(a);v=(len(a)-1)*p;i=int(v);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(v-i)
assert read('LIVE_RESULT.json')['status']=='COMPLETE'
cells=['EXACT_Q_ZERO','EXACT_Q_HALF','NOISY_Q_ZERO','NOISY_Q_HALF']
coefs={cells[0]:[1,0,0,0],cells[1]:[0,1,0,0],cells[2]:[0,0,1,0],cells[3]:[0,0,0,1],'EXACT_Q_HALF_MINUS_ZERO':[-1,1,0,0],'NOISY_Q_HALF_MINUS_ZERO':[0,0,-1,1],'NOISY_MINUS_EXACT_AT_Q_ZERO':[-1,0,1,0],'NOISY_MINUS_EXACT_AT_Q_HALF':[0,-1,0,1],'NOISE_BY_RECURRENCE':[1,-1,-1,1]}
series={(q['block'],q['replicate'],q['cell'],q['configuration']):q for q in rows('TIME_SERIES.jsonl.gz')};assert len(series)==2304
metrics={}
for b in range(24):
 for r in range(8):
  base={}
  for c in cells:
   a=series[b,r,c,'SWITCH0']['series'];d=series[b,r,c,'SWITCH1']['series'];s=series[b,r,c,'STAY']['series'];v={}
   for m in ['D40','U','U40']:
    if m=='D40':x=(a['founder']['0'][-1]+d['founder']['1'][-1])/2-1/32;y=(s['founder']['0'][-1]+s['founder']['1'][-1])/2-1/32;prefix=''
    elif m=='U':x=(sum(a['accuracy'][1:])/40+sum(d['accuracy'][1:])/40)/2;y=sum(s['accuracy'][1:])/40;prefix='_POP'
    else:x=(a['accuracy'][-1]+d['accuracy'][-1])/2;y=s['accuracy'][-1];prefix='_POP'
    for name,z in [('SWITCH',x),('STAY',y),('EFFECT',x-y)]:v[name+prefix+'|'+m]=z
   base[c]=v
  metrics[b,r]={g+'|'+k:sum(cf[j]*base[c][k] for j,c in enumerate(cells)) for g,cf in coefs.items() for k in base[cells[0]]}
assert len(metrics)==192 and all(len(x)==81 for x in metrics.values())
for q in rows('PAIRED_METRICS.jsonl.gz'):
 v=metrics[q['block'],q['replicate']];assert set(v)==set(q['values'])
 for k in v:close(v[k],q['values'][k])
bootstrap=read('BOOTSTRAP_INDICES.json');assert len(bootstrap)==2000 and all(len(row)==24 and all(0<=i<24 for i in row) for row in bootstrap)
est=read('ESTIMATES.json');assert len(est)==81 and set(est)==set(metrics[0,0]);checked={};maxerr=0
for k in est:
 blocks=[sum(metrics[b,r][k] for r in range(8))/8 for b in range(24)];samples=[sum(blocks[i] for i in row)/24 for row in bootstrap];mean=sum(blocks)/24;ci=[percentile(samples,.025),percentile(samples,.975)];checked[k]={'mean':mean,'ci95':ci}
 for a,z in zip([mean]+ci,[est[k]['mean']]+est[k]['ci95']):close(a,z);maxerr=max(maxerr,abs(a-z))
# Authenticate all reused states; no new outcome-dependent selection.
original=list(rows('../cross_environment_replication_v1/RESIDENT_STATES.jsonl.gz'))
sel=read('SELECTED_STATES.json');assert len(sel)==192
states={}
for q in sel:
 s=q['source_state'];assert s==original[q['source_row_index']];assert s['geometry']=='HALF' and s['background']=='F';states[s['block'],s['replicate']]=s
assert set(states)=={(b,r) for b in range(24) for r in range(8)}
streams=keyed('streams.jsonl.gz');fresh=keyed('fresh_probe_masks.jsonl.gz');noise=keyed('noise_streams.jsonl.gz');survival=keyed('survival_streams.jsonl.gz');targets=read('TARGET_TABLE.json');td=read('TARGET_LAW_DRAWS.json')
for b in range(24):
 for law in ['ZERO','HALF']:
  ts=list(states[b,0]['last_two_preparation_targets'])
  for z,copy in zip(td[b]['innovations'],td[b]['copy_bits']):ts.append(ts[-2] if law=='HALF' and copy else z)
  assert targets[law][b]['targets']==ts[2:]
counts=collections.Counter();rawkeys=set();declines=0
for path in rows('raw/block00.jsonl.gz'):
 b,r=path['block'],path['replicate'];assert b==0
 c,cfg=path['cell'],path['configuration'];key=(b,r,c,cfg);assert key not in rawkeys;rawkeys.add(key)
 d=streams[b,r]['draws'];labels=d['labels'];assert path['founder_ids']==labels[:2];source=states[b,r];slot=None if cfg=='STAY' else labels[int(cfg[-1])];assert path['slot']==slot
 before=[[p[0],1 if i==slot else 2,p[2],p[3]] for i,p in enumerate(source['rebased_population'])]
 rec=path['record'];assert rec['populations'][0]==before and len(rec['populations'])==41
 tt=targets[path['law']][b]['targets'];assert rec['boundary_previous_target']==source['last_preparation_target'];assert rec['boundary_current_target']==tt[0]
 nn=noise[b,r]['noise'];eta=1 if path['interface']=='NOISY' else 0;initial=[]
 for j,q in enumerate(rec['initial_queries']):
  h=bin(before[j][0]^tt[0]).count('1');u=nn['initial'][j];assert q==dict(query_ordinal=j,candidate_index=j,genotype=before[j][0],true_loss=h,noise_uniform=u,error=eta*(2*u-1),observed_score=h+eta*(2*u-1));initial.append(h);counts['queries']+=1
 assert rec['initial_true_losses']==initial;loss=[sum(initial)/1024]
 for g,step in enumerate(rec['steps']):
  assert before==rec['populations'][g];t=tt[g];ties=d['ties'][g];masks=fresh[b,r]['fresh'][g]
  def child(p,x,i):return [x,p[1],p[2],[p[0],40+g,i]]
  pool=list(before)+[child(p,p[3][0] if p[1]==1 else p[0]^masks[i],i) for i,p in enumerate(before)]+[child(p,p[0]^d['scout'][g][i],i) for i,p in enumerate(before)]
  obs=[]
  for j,q in enumerate(pool):obs.append(bin(q[0]^t).count('1')+eta*(2*nn['updates'][g][j]-1))
  for i,p in enumerate(before):
   inds=[i,32+i,64+i];win=min(inds,key=lambda j:(obs[j],ties[j],j));donor=step['donor_choices'][i];assert donor['winner_index']==win and donor['candidate_indices']==inds and donor['observed_scores']==[obs[j] for j in inds];assert 'raw_mismatches' not in donor
   pool.append(child(p,pool[win][0]^d['local'][g][i],i));counts['donor_choices']+=1
  assert step['candidates']==pool;truth=[];obs=[]
  for j,p in enumerate(pool):
   h=bin(p[0]^t).count('1');u=nn['updates'][g][j];error=eta*(2*u-1);returned=h+error;q=step['query_records'][j]
   assert q==dict(query_ordinal=32+g*128+j,candidate_index=j,genotype=p[0],true_loss=h,noise_uniform=u,error=error,observed_score=returned)
   truth.append(h);obs.append(returned);counts['queries']+=1
  assert truth==step['candidate_true_losses'] and obs==step['candidate_observed_scores'] and ties==step['ties'];ss=survival[b,r]['survival'][g];us=[(k+1)/(2**52+1) for k in ss['k']];assert us==ss['u']==step['survival_uniforms'] and ss['k']==step['survival_integers']
  keys=[-math.log(u)*(2.0**v) for u,v in zip(us,obs)];assert keys==step['race_keys'];chosen=sorted(range(128),key=lambda j:(keys[j],ties[j],j))[:32];assert chosen==step['selected_indices'];after=[pool[j] for j in chosen];assert after==step['selected_records']==rec['populations'][g+1]
  B=sum(truth[:32])/1024;L=sum(truth[j] for j in chosen)/1024
  assert step['B_true']==B and step['L_true']==L and step['S_true']==B-L and step['W_true']==B-loss[-1]
  counts['race_candidates']+=128;counts['updates']+=1;declines+=int(L>loss[-1] or L>B);loss.append(L);before=after
 assert loss==rec['true_losses'];assert [1-x for x in loss]==rec['true_accuracies'];ts=series[key]['series'];assert ts['accuracy']==rec['true_accuracies']
 for i,fid in enumerate(labels[:2]):assert ts['founder'][str(i)]==[sum(p[2]==fid for p in pop)/32 for pop in rec['populations']]
 for name,pol in [('H',1),('F',2),('R',0)]:assert ts['expression'][name]==[sum(p[1]==pol for p in pop)/32 for pop in rec['populations']]
 counts['paths']+=1
assert len(rawkeys)==counts['paths']==96 and counts['queries']==494592 and counts['updates']==3840
result={'task_id':'ORG-OBSERVATION-060','status':'PASS','checked_at_utc':datetime.now(timezone.utc).isoformat(),'producer_imports':False,'scientific_trajectories_rerun':0,'estimates_recomputed':81,'paired_metric_records':192*81,'maximum_estimate_discrepancy':maxerr,'raw_block':0,'counts':dict(counts),'retained_declines_in_audited_block':declines,'primary':checked['NOISE_BY_RECURRENCE|EFFECT|D40'],'recurrence':{a:checked[a+'_Q_HALF_MINUS_ZERO|EFFECT|D40'] for a in ['EXACT','NOISY']},'script_sha256':sha(Path(__file__)),'source_manifest_sha256':sha(P/'SOURCE_SHA256SUMS'),'result_manifest_sha256':sha(P/'RESULT_SHA256SUMS'),'files_bound':{n:sha(P/n) for n in ['ESTIMATES.json','TIME_SERIES.jsonl.gz','PAIRED_METRICS.jsonl.gz','BOOTSTRAP_INDICES.json','raw/block00.jsonl.gz']}}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
