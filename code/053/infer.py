import pathlib,json,sys
import numpy as np
from analysis import derive,structural,direction,LAWS,COSTS,RAW,FREQ
P=pathlib.Path(__file__).resolve().parent
def save(n,v):(P/n).write_text(json.dumps(v,indent=2)+'\n')
def main():
 idx=np.asarray(json.loads((P/'BOOTSTRAP_INDICES.json').read_text()),dtype=int);assert idx.shape==(2000,24);blocks=json.loads((P/'BASE_BLOCKS.json').read_text());cols={}
 with (P/'BLOCK_SUMMARIES.jsonl').open('w') as out:
  for row in blocks:
   derive(row['values']);out.write(json.dumps(row,separators=(',',':'))+'\n')
   for k,x in row['values'].items():cols.setdefault(k,[]).append(x)
 values={}
 for k,x in cols.items():
  a=np.asarray(x);ci=np.quantile(a[idx].mean(axis=1),[.025,.975],method='linear').tolist();cl=direction(k,ci)
  if structural(k):assert np.all(a==0)
  elif np.all(a==0):cl='observed_exact_zero'
  values[k]=dict(mean=float(a.mean()),ci95=ci,zero_classification=cl)
 assert len(values)==1716 and sum(structural(k) for k in values)==90
 save('summary.json',dict(primary='HALF|C0|R_H|D40',values=values,interval_scope='All intervals including primary approximate pointwise;24blocks x8 paired continuations; orientations not independent replicates',numpy_version=np.__version__,python=sys.version));save('INFERENCE_CHECK.json',dict(status='PASS',records=1716,structural_zero_records=90,new_objective_calls=0,quantile_method='linear'))
 old=json.loads((P.parent/'independent_prepared_competition_v1/summary.json').read_text())['values'];refs={}
 for g in LAWS:
  for c in COSTS:
   for new,original,ms in [('HF_H','MIX_H',FREQ),('HF_F','MIX_F',FREQ),('MIX_RANK','MIX_H_MINUS_F',FREQ),('HF_POP','MIX_POP',RAW)]:
    for m in ms:
     nk=g+'|'+c+'|'+new+'|'+m;ok=g+'|'+c+'|'+original+'|'+m;assert values[nk]==old[ok],(nk,values[nk],old[ok]);refs[nk]=dict(source_key=ok,value=values[nk])
 assert len(refs)==312;save('REUSED_INTERVALS.json',refs);save('BASELINE_REUSE_CHECK.json',dict(status='PASS',exact_interval_records=312,stored_paths=2304,reruns=0));print(values['HALF|C0|R_H|D40'])
if __name__=='__main__':main()
