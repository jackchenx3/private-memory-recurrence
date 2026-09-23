"""Frozen local post-allocation NumPy analysis of saved records; no simulation."""
import json,pathlib,sys
import numpy as np
from analysis import derive,structural,direction
P=pathlib.Path(__file__).resolve().parent

def main():
 blocks=json.loads((P/'BASE_BLOCKS.json').read_text());idx=np.asarray(json.loads((P/'BOOTSTRAP_INDICES.json').read_text()),dtype=int);assert idx.shape==(2000,24);cols={}
 with (P/'BLOCK_SUMMARIES.jsonl').open('w') as out:
  for r in blocks:
   derive(r['values']);out.write(json.dumps(r,separators=(',',':'))+'\n')
   for k,x in r['values'].items():cols.setdefault(k,[]).append(x)
 values={}
 for k,x in cols.items():
  a=np.asarray(x);assert a.shape==(24,);boot=a[idx].mean(axis=1);ci=np.quantile(boot,[.025,.975],method='linear').tolist();cl,meaning=direction(k,ci)
  if structural(k):assert np.all(a==0)
  elif np.all(a==0):cl,meaning='observed_exact_zero','sampled equality; not a design guarantee'
  values[k]=dict(mean=float(a.mean()),ci95=ci,zero_classification=cl,interpretation=meaning)
 assert len(values)==780 and sum(structural(k) for k in values)==52
 (P/'summary.json').write_text(json.dumps(dict(primary='RARE|RECUR_MINUS_IID|ACTIVE_C0-NOVEL_C0|D40',values=values,interval_scope='Independent046cohort;2304newpaths985newseeds;new2000wholeblockbootstrap;all intervals including primary approximate pointwise;no pooling',numpy_version=np.__version__,python=sys.version),indent=2)+'\n')
 (P/'INFERENCE_CHECK.json').write_text(json.dumps(dict(status='PASS',records=780,structural_zero_records=52,numpy_version=np.__version__,quantile_method='linear',analysis_location='local postallocation; stored outputs only',new_dynamics=0),indent=2)+'\n')
 print(values['RARE|RECUR_MINUS_IID|ACTIVE_C0-NOVEL_C0|D40'])
if __name__=='__main__':main()
