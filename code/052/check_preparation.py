"""Validate saved preparation/transfer boundary without evaluating an objective."""
import pathlib,json,gzip,collections
P=pathlib.Path(__file__).resolve().parent

def readlines(f):
 with gzip.open(P/f,'rt') as src:
  for line in src:yield json.loads(line)
def main():
 ts=json.loads((P/'PREPARATION_TARGETS.json').read_text())['blocks'];res=iter(readlines('RESIDENT_STATES.jsonl.gz'));streams=iter(readlines('streams.jsonl.gz'));count=0;checks=0;descriptive=[]
 for b in range(24):
  pairs=ts[b]['targets'][:2];assert ts[b]['targets']==pairs*20
  for r,raw in enumerate(readlines('preparation/block%02d.jsonl.gz'%b)):
   rr=next(res);stream=next(streams);rec=raw['record'];assert (raw['block'],raw['replicate'])==(b,r)==(rr['block'],rr['replicate'])==(stream['block'],stream['replicate']);assert len(rec['populations'])==41;assert all(q[0]==0 for q in rec['populations'][0]);assert sum(q[1] for q in rec['populations'][0])==1;assert rr['genotypes']==[q[0] for q in rec['populations'][-1]] and rr['preparation_first_pair']==pairs;assert rec['query_counts']['total']==5152
   for j,st in enumerate(rec['steps']):
    before=rec['populations'][j];assert rec['ground_truth'][j]['target']==pairs[j%2];assert st['candidate_raw_mismatches']==st['candidate_penalized_mismatches'];assert st['evaluator_calls']==128;assert st['selected_indices']==sorted(range(128),key=lambda i:(st['candidate_penalized_mismatches'][i],st['ties'][i],i))[:32];assert all(not x for x in st['probe_access']);assert [q[0] for q in st['candidates'][32:64]]==[q[0] for q in before];assert st['S_raw']==st['S_pen']>=0;checks+=1
   descriptive.append(dict(block=b,replicate=r,initial_raw_accuracy=rec['raw_accuracies'][0],mean_raw_accuracy=sum(rec['raw_accuracies'][1:])/40,terminal_raw_accuracy=rec['raw_accuracies'][-1],preparation_carrier_final=rec['frequencies'][-1],distinct_endpoint_genotypes=len(set(rr['genotypes'])),pair_equal=pairs[0]==pairs[1],boundary_change=pairs[0]!=pairs[1]));count+=1
  assert r==7
 assert count==192 and checks==7680 and next(res,None) is None and next(streams,None) is None
 # All6912transfer starts are extracted from the corresponding prepared population.
 states={(q['block'],q['replicate']):q for q in readlines('RESIDENT_STATES.jsonl.gz')};labels={(q['block'],q['replicate']):q['draws']['labels'] for q in readlines('streams.jsonl.gz')};n=0
 for b in range(24):
  for row in readlines('raw/block%02d.jsonl.gz'%b):
   k=b,row['replicate'];rr=states[k];pop=row['record']['populations'][0];p0,p1=labels[k][:2];cfg=row['configuration'];assign={'MIX0':{p0:1,p1:2},'MIX1':{p1:1,p0:2},'H0':{p0:1},'H1':{p1:1},'F0':{p0:2},'F1':{p1:2}}[cfg];expected=[[x,assign.get(i,0),i,[x,0,i] if i in assign else None] for i,x in enumerate(rr['genotypes'])];assert pop==expected;assert [q['target'] for q in row['record']['ground_truth'][:2]]==rr['preparation_first_pair'];n+=1
 assert n==6912
 ex=json.loads((P/'INPUT_FREEZE.json').read_text());pr=json.loads((P/'PREPARATION_STARTED.json').read_text());fr=json.loads((P/'RESIDENT_FREEZE.json').read_text());tr=json.loads((P/'TRANSFER_STARTED.json').read_text());assert ex['freeze_unix']<pr['start_unix']<fr['freeze_unix']<tr['start']
 (P/'PREPARATION_DESCRIPTIVE.json').write_text(json.dumps(descriptive,indent=2)+'\n');(P/'PREPARATION_CHECK.json').write_text(json.dumps(dict(status='PASS',preparation_paths=count,preparation_steps=checks,transfer_resets=n,all_endpoints_retained=True,staged_freeze_order_verified=True,extra_objective_calls=0),indent=2)+'\n')
if __name__=='__main__':main()
