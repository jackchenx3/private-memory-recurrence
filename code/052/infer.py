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
 assert len(values)==1482 and sum(structural(k) for k in values)==84
 save('summary.json',dict(primary='HALF|C0|MIX_H_MINUS_F|D40',values=values,interval_scope='All intervals including primary approximate pointwise;24blocks x8 paired continuations; orientations not independent replicates',numpy_version=np.__version__,python=sys.version));save('INFERENCE_CHECK.json',dict(status='PASS',records=1482,structural_zero_records=84,new_objective_calls=0,quantile_method='linear'))
 print(values['HALF|C0|MIX_H_MINUS_F|D40'])
if __name__=='__main__':main()
